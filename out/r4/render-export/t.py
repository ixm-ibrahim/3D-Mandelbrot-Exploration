"""Tests of the picture job and the snapshots (render-export, round 4).

  python out/r4/render-export/t.py <test> [--url dist/r4-render-export.html] [--size 1400x950] [--theme dark]

Each test is a list of steps for tools/shot.py; the steps file is written next to this script and run.
"""
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = 'out/r4/render-export/'

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const idle = async () => { while (!L.idle()) await sleep(50); };
const jobDone = async () => { while (L.exportBusy()) await sleep(50); };
// the picture on screen, as an ImageBitmap-like canvas (read from the GL canvas right after a redraw of the finished picture)
const pixelsOf = async (src, w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d', { willReadFrequently: true }); x.imageSmoothingQuality = 'high'; x.drawImage(src, 0, 0, w, h); return x.getImageData(0, 0, w, h).data; };
const diff = (a, b) => { let sum = 0, worst = 0, over = 0; for (let i = 0; i < a.length; i += 4) { const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2])); sum += d; if (d > worst) worst = d; if (d > 24) over++; } const n = a.length / 4; return { mean: +(sum / n).toFixed(3), worst, over: +(100 * over / n).toFixed(3) }; };
// The finished picture on screen. A GL canvas is emptied once it has been shown, so the copy is taken in the very
// task that draws to the screen: every draw to the default framebuffer is followed by a copy while wantGrab is set.
const liveShot = async () => {
  const cv = $('view'), glx = cv.getContext('webgl2');
  if (!glx.wrapped) {
    const draw = glx.drawArrays.bind(glx); glx.wrapped = true;
    glx.drawArrays = (...a) => { draw(...a); if (window.wantGrab && glx.getParameter(glx.FRAMEBUFFER_BINDING) === null) { const c = window.grabbed || (window.grabbed = document.createElement('canvas')); c.width = cv.width; c.height = cv.height; c.getContext('2d').drawImage(cv, 0, 0); } };
  }
  window.wantGrab = true; L.touch(); await idle(); window.wantGrab = false;
  return window.grabbed;
};
// put pictures side by side over the page, for a screenshot with the clip #cmp
const show = (...list) => {
  let box = $('cmp'); if (box) box.remove();
  box = document.createElement('div'); box.id = 'cmp'; box.style.cssText = 'position:fixed;left:0;top:0;z-index:99;display:flex;gap:4px;background:#888;padding:4px';
  const w = Math.floor((innerWidth - 8 - 4 * (list.length - 1)) / list.length);
  for (const src of list) { const sw = src.width, sh = src.height, c = document.createElement('canvas'); c.width = w; c.height = Math.round(w * sh / sw); const x = c.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(src, 0, 0, c.width, c.height); box.appendChild(c); }
  document.body.appendChild(box);
};
window.files = window.files || [];
window.squaringLabSaveHook = (name, blob) => { window.files.push({ name, blob }); };
const startJob = async (size, quality, kind, w, h) => {
  $('secExport').open = true;
  pick('exportSize', size); if (w) { type('exportWNum', String(w)); type('exportHNum', String(h)); }
  pick('exportQuality', quality); pick('exportKind', kind);
  if ($('exportDiscard').getBoundingClientRect().width > 0) $('exportDiscard').click();
  $('exportStart').click();
};
const saveJob = async () => {
  await jobDone();
  if (!($('exportSave').getBoundingClientRect().width > 0)) fail('no Save button after the job: ' + $('exportMsg').textContent);
  const n = window.files.length; $('exportSave').click(); await sleep(300);
  const f = window.files[n]; if (!f) fail('Save the file handed nothing over');
  const bm = await createImageBitmap(f.blob);
  return { f, bm };
};
"""


def step(js, shot=None, clip=None, wait=None, timeout=300, sleep=None):
    a = {'js': PRE + js.strip()}
    if wait: a['wait'] = wait; a['timeout'] = timeout
    if sleep: a['sleep'] = sleep
    if shot:
        a['shot'] = OUT + shot
        if clip: a['clip'] = clip
    return a


TESTS = {}

# ---- basic: a typed 256 x 256 PNG arrives through the hook with exactly that size; the panel in its three states
TESTS['basic'] = [
    step("L.R.warmOn = false; await idle(); $('secExport').open = true; $('secExport').scrollIntoView(); return $('exportSizeNote').textContent;", shot='panel-1-idle.png', clip='#secExport'),
    step("""
await startJob('Typed', 'Fine', 'PNG', 256, 256);
await sleep(30);
const busy = L.exportBusy(), text = $('exportStep').textContent;
const { f, bm } = await saveJob();
if (bm.width !== 256 || bm.height !== 256) fail('asked 256 x 256, got ' + bm.width + ' x ' + bm.height);
return { busyAtStart: busy, stepText: text, name: f.name, type: f.blob.type, bytes: f.blob.size, size: bm.width + 'x' + bm.height, msg: $('exportMsg').textContent, facts: $('exportFacts').textContent };
""", shot='panel-3-done.png', clip='#secExport'),
    step("""
$('exportDiscard').click(); await sleep(50);
await startJob('3840', 'Fine', 'JPG');
await sleep(1500);
return { step: $('exportStep').textContent, bar: $('exportBar').getAttribute('aria-valuenow') };
""", shot='panel-2-running.png', clip='#secExport'),
    step("""
$('exportCancel').click(); await jobDone(); await sleep(100);
return { msg: $('exportMsg').textContent, startShown: $('exportStart').getBoundingClientRect().width > 0, focus: document.activeElement && document.activeElement.id };
"""),
]

# ---- match: the job's picture, scaled down, against the picture on screen (same quality), 3D and 2D, and sizes
TESTS['match'] = [
    step("""
L.R.warmOn = false; L.S.q.aa = 6; L.touch(); await idle();
const cv = $('view'), W = cv.width, H = cv.height;
const out = {};
for (const [label, size, k] of [['same size', 'As on screen', 1], ['twice', 'Twice', 2]]) {
  await startJob(size, 'As on screen', 'PNG');
  const { f, bm } = await saveJob();
  if (bm.width !== W * k || bm.height !== H * k) fail(label + ': expected ' + W * k + ' x ' + H * k + ', got ' + bm.width + ' x ' + bm.height);
  // the screen's own picture: redraw it from the finished target, then read the canvas in the same task
  const live = await liveShot();
  out[label] = Object.assign({ size: bm.width + 'x' + bm.height }, diff(await pixelsOf(bm, W, H), await pixelsOf(live, W, H)));
  window['bm_' + k] = bm; $('exportDiscard').click();
}
return out;
"""),
    step("""
// the 2D view and the Kleinian view, same size as the screen
const cv = $('view'), W = cv.width, H = cv.height, out = {};
$('flat').click(); await idle();
for (const label of ['2d']) {
  await startJob('As on screen', 'As on screen', 'PNG');
  const { bm } = await saveJob();
  out[label] = diff(await pixelsOf(bm, W, H), await pixelsOf(await liveShot(), W, H)); $('exportDiscard').click();
}
$('flat').click(); $('mode-k').click(); await idle();
await startJob('As on screen', 'As on screen', 'PNG');
const { bm } = await saveJob();
out.klein = diff(await pixelsOf(bm, W, H), await pixelsOf(await liveShot(), W, H)); $('exportDiscard').click();
$('mode-m').click(); await idle();
return out;
"""),
]

# ---- twice the size against the screen: with the default colours (to look at) and with plain clay (the shape alone)
TESTS['twice'] = [
    step('''
L.R.warmOn = false; L.S.q.aa = 6; L.touch(); await idle();
const cv = $('view'), W = cv.width, H = cv.height;
await startJob('Twice', 'As on screen', 'PNG');
const { bm } = await saveJob();
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return d;
''', shot='twice-default.png', clip='#cmp'),
    step('''
const cv = $('view'), W = cv.width, H = cv.height;
L.S.colour.mode = 7; L.syncControls(); L.touch(); await idle();
await startJob('Twice', 'As on screen', 'PNG');
const { bm } = await saveJob();
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return d;
''', shot='twice-clay.png', clip='#cmp'),
]

# ---- independence: a job started before the approach, the colours, the camera and the mode change shows the ORIGINAL picture
TESTS['indep'] = [
    step('''
L.R.warmOn = false; L.S.q.aa = 6; L.touch(); await idle();
const cv = $('view'), W = cv.width, H = cv.height;
// the reference: the same job, run with the page left alone
await startJob('Twice', 'As on screen', 'PNG');
const ref = (await saveJob()).bm; $('exportDiscard').click();
const before = JSON.stringify(L.S), cam0 = JSON.stringify(L.basis());
const liveBefore = document.createElement('canvas'); liveBefore.width = W; liveBefore.height = H; liveBefore.getContext('2d').drawImage(await liveShot(), 0, 0);
// the job under test: started, then everything is changed while it runs
await startJob('Twice', 'As on screen', 'PNG');
await sleep(60);
const fracAtChange = +$('exportBar').getAttribute('aria-valuenow');
L.S.approach = (L.S.approach + 1) % L.APPROACHES.length; L.S.n = 3; L.refresh(false);
L.S.colour.mode = 2; L.S.colour.pal = 5; L.S.colour.rev = false; L.S.lightAz = 40; L.S.iter = 9; L.S.cutOn = true; L.S.cut = 0.1;
L.cam.yaw += 1.1; L.cam.pitch = 0.2; L.cam.dist *= 0.6; L.S.q.aa = 2; L.S.q.detail = 2; L.syncControls(); L.touch();
await sleep(250);
$('mode-j').click();
const busyAfterChange = L.exportBusy(), fracAfterChange = +$('exportBar').getAttribute('aria-valuenow');
// the live picture while the job is still running
const liveDuring = document.createElement('canvas'); liveDuring.width = W; liveDuring.height = H; liveDuring.getContext('2d').drawImage(await liveShot(), 0, 0);
const busyAfterLive = L.exportBusy();
const job = (await saveJob()).bm;
const liveAfter = await liveShot();
const stateKept = JSON.stringify(L.S);
const out = {
  busyAfterChange, busyAfterLive, fracAtChange, fracAfterChange,
  'job against the reference': diff(await pixelsOf(job, W, H), await pixelsOf(ref, W, H)),
  'job against the picture on screen before': diff(await pixelsOf(job, W, H), await pixelsOf(liveBefore, W, H)),
  'job against the picture on screen now (should differ)': diff(await pixelsOf(job, W, H), await pixelsOf(liveAfter, W, H)),
  'live during the job against live after it': diff(await pixelsOf(liveDuring, W, H), await pixelsOf(liveAfter, W, H)),
  liveStateChangedByUs: stateKept !== before, mode: L.S.mode, approach: L.S.approach, camMoved: JSON.stringify(L.basis()) !== cam0,
};
show(liveBefore, job, liveAfter);
return out;
''', shot='indep.png', clip='#cmp'),
]

# ---- frame gaps while a job runs: a simulated drag on Balanced, back to back without, with, without a job
GAPS = '''
const gaps = async (ms, drag) => {
  const g = []; let last = performance.now(), t0 = last;
  while (last - t0 < ms) { await new Promise(r => requestAnimationFrame(r)); const now = performance.now(); g.push(now - last); last = now; if (drag) { L.cam.yaw += 0.012; L.touch(); } }
  g.sort((a, b) => a - b);
  return { frames: g.length, mean: +(g.reduce((a, b) => a + b, 0) / g.length).toFixed(1), p95: +g[Math.floor(0.95 * g.length)].toFixed(1), worst: +g[g.length - 1].toFixed(1), over50: g.filter(x => x > 50).length };
};
const finish = async () => { const t = performance.now(); L.cam.yaw += 0.02; L.touch(); const g = gaps(1e9, false); await idle(); return Math.round(performance.now() - t); };
const timeLive = async () => { const t = performance.now(); L.cam.yaw += 0.02; L.touch(); const g = []; let last = t; while (!L.idle()) { await new Promise(r => requestAnimationFrame(r)); const now = performance.now(); g.push(now - last); last = now; } return { ms: Math.round(performance.now() - t), worstGap: +Math.max(...g).toFixed(1), over50: g.filter(x => x > 50).length }; };
'''
TESTS['gaps'] = [
    step(GAPS + '''
L.R.warmOn = false; await idle();
const out = { quality: JSON.stringify(L.S.q), timer: !!L.R.tq };
await gaps(500, true);
out['drag, no job (1)'] = await gaps(3000, true);
out['finish live, no job (1)'] = await timeLive();
await startJob('7680', 'Extra', 'PNG'); await sleep(300);
const f0 = EXPORTFRAC();
out['drag, job running'] = await gaps(3000, true);
const f1 = EXPORTFRAC();
out['finish live, job running'] = await timeLive();
const f2 = EXPORTFRAC();
out['idle, job running'] = await gaps(3000, false);
const f3 = EXPORTFRAC();
out['job progress'] = { 'during 3 s of dragging': +(f1 - f0).toFixed(4), 'while the live picture finished': +(f2 - f1).toFixed(4), 'during 3 s idle': +(f3 - f2).toFixed(4) };
out['still busy'] = L.exportBusy();
$('exportCancel').click(); await jobDone();
out['drag, no job (2)'] = await gaps(3000, true);
out['finish live, no job (2)'] = await timeLive();
return out;
'''.replace('EXPORTFRAC()', "(parseFloat(($('exportStep').textContent.match(/([0-9.]+)%/) || [0, 0])[1]) / 100)")),
]

# ---- sampleSlice: the layout the contract fixes, checked point by point on a scene with no mirror symmetry; and
# that a snapshot keeps its scene; and what a call costs
TESTS['slice'] = [
    step('''
L.R.warmOn = false; $('mode-j').click(); L.S.c = [-0.12, 0.74, 0.1]; L.syncControls(); L.refresh(false); await idle();
const snap = L.takeSnapshot(), N = 64, cx = 0.1, cy = -0.2, side = 3, z = 0.05;
const t0 = performance.now(), big = await L.sampleSlice(snap, cx, cy, side, z, N), tBig = performance.now() - t0;
if (!big || big.length !== 4 * N * N) fail('no slice');
let inside = 0, bad = 0; for (let i = 0; i < N * N; i++) { if (big[4 * i + 3] <= 0) inside++; for (let k = 0; k < 3; k++) { const v = big[4 * i + k]; if (!(v >= 0 && v <= 1.0001)) bad++; } if (!isFinite(big[4 * i + 3])) bad++; }
// single points, asked one at a time, against the grid
let worst = 0, n = 0;
for (const [i, j] of [[0, 0], [63, 0], [0, 63], [63, 63], [20, 31], [31, 20], [40, 12], [12, 40], [33, 33], [50, 45]]) {
  const x = cx - side / 2 + (i + 0.5) * side / N, y = cy - side / 2 + (j + 0.5) * side / N;
  const one = await L.sampleSlice(snap, x, y, side / N, z, 1);
  for (let k = 0; k < 4; k++) worst = Math.max(worst, Math.abs(one[k] - big[4 * (j * N + i) + k]));
  n++;
}
// mirrored in y the scene is different: the two halves of the grid must not be mirror images
let asym = 0; for (let j = 0; j < N / 2; j++) for (let i = 0; i < N; i++) asym = Math.max(asym, Math.abs(big[4 * (j * N + i) + 3] - big[4 * ((N - 1 - j) * N + i) + 3]));
// the page moves on: another mode, another camera. The snapshot must give the same numbers as before.
$('mode-k').click(); L.cam.yaw += 1; L.touch(); await sleep(100);
const again = await L.sampleSlice(snap, cx, cy, side, z, N);
let moved = 0; for (let i = 0; i < big.length; i++) moved = Math.max(moved, Math.abs(big[i] - again[i]));
await idle();
// what calls cost: many small ones, then large ones (the model job's pattern)
const t1 = performance.now(); for (let k = 0; k < 100; k++) await L.sampleSlice(snap, 0, 0, 3, -1 + k / 50, 49); const small = (performance.now() - t1) / 100;
const t2 = performance.now(); for (let k = 0; k < 20; k++) await L.sampleSlice(snap, 0, 0, 3, -1 + k / 10, 513); const large = (performance.now() - t2) / 20;
L.releaseSnapshot(snap);
const after = await L.sampleSlice(snap, cx, cy, side, z, 8);
$('mode-m').click();
return { 'points inside, of 4096': inside, 'values out of range': bad, 'largest difference, single points against the grid': worst, points: n, 'largest difference between the two halves in y (must not be 0)': +asym.toFixed(4),
  'largest change after the page moved on (must be 0)': moved, 'ms per call, N = 49': +small.toFixed(2), 'ms per call, N = 513': +large.toFixed(2), 'first call ms': +tBig.toFixed(1), 'after release': after };
'''),
]

# ---- hidden tab: with animation frames stopped and the page reporting itself hidden, a job still finishes
TESTS['hidden'] = [
    step('''
L.R.warmOn = false; await idle();
const t0 = performance.now();
await startJob('1920', 'As on screen', 'JPG'); const a = await saveJob(); const shownMs = Math.round(performance.now() - t0); $('exportDiscard').click();
// "hide" the page: no animation frames at all, and document.hidden true
const raf = window.requestAnimationFrame; window.requestAnimationFrame = () => 0;
Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' });
document.dispatchEvent(new Event('visibilitychange'));
const t1 = performance.now();
await startJob('1920', 'As on screen', 'JPG'); const b = await saveJob(); const hiddenMs = Math.round(performance.now() - t1);
delete document.hidden; delete document.visibilityState; window.requestAnimationFrame = raf; document.dispatchEvent(new Event('visibilitychange'));
const d = diff(await pixelsOf(a.bm, 960, 540), await pixelsOf(b.bm, 960, 540));
$('exportDiscard').click(); L.touch(); await idle();
return { shownMs, hiddenMs, size: b.bm.width + 'x' + b.bm.height, type: b.f.blob.type, 'hidden job against the same job shown': d };
'''),
]

# ---- what a job does, second by second
TESTS['stat'] = [
    step('''
L.R.warmOn = false; await idle();
const rows = [], R = L.R, t0 = performance.now();
await startJob('1920', 'As on screen', 'JPG');
let n0 = R.bgN, m0 = R.bgMs, h0 = R.bgHeld;
while (L.exportBusy() && performance.now() - t0 < 40000) {
  await sleep(1000);
  rows.push([Math.round(performance.now() - t0), $('exportStep').textContent.replace(/^.*pixels[.] /, ''), 'pieces ' + (R.bgN - n0), 'their ms ' + Math.round(R.bgMs - m0), 'held ' + (R.bgHeld - h0), 'live idle ' + L.renderIdle(), 'since touch ' + Math.round(performance.now() - R.lastTouch)].join(' | '));
  n0 = R.bgN; m0 = R.bgMs; h0 = R.bgHeld;
}
if (L.exportBusy()) { $('exportCancel').click(); await jobDone(); }
return rows;
'''),
]

# ---- 8K: the whole job to the end (one pass, to keep it short), and a size that is refused in plain words
TESTS['big'] = [
    step("""
L.R.warmOn = false; L.S.q.aa = 1; L.syncControls(); L.touch(); await idle();
const t0 = performance.now();
await startJob('7680', 'As on screen', 'JPG');
const { f, bm } = await saveJob();
const out = { size: bm.width + 'x' + bm.height, bytes: f.blob.size, type: f.blob.type, seconds: +((performance.now() - t0) / 1000).toFixed(1), facts: $('exportFacts').textContent, preview: $('exportPreview').width + 'x' + $('exportPreview').height };
if (bm.width !== 7680 || bm.height !== 4320) fail('not 8K: ' + out.size);
return out;
""", shot='panel-8k-done.png', clip='#secExport'),
    step("""
$('exportDiscard').click(); L.setExtreme(true); L.syncControls();
await startJob('Typed', 'As on screen', 'PNG', 16384, 16384); await sleep(200);
const out = { busy: L.exportBusy(), msg: $('exportMsg').textContent, note: $('exportSizeNote').textContent };
L.setExtreme(false); L.syncControls();
out.afterExtremeOff = [$('exportWNum').value, $('exportHNum').value];
$('resetAll').click(); await sleep(100); await idle();
return out;
"""),
]

# ---- Fine at twice the size against the screen (the default settings of the panel), to look at
TESTS['fine'] = [
    step("""
L.R.warmOn = false; await idle();
const cv = $('view'), W = cv.width, H = cv.height;
const t0 = performance.now();
await startJob('Twice', 'Fine', 'PNG');
const { bm } = await saveJob(); const secs = +((performance.now() - t0) / 1000).toFixed(1);
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return Object.assign({ seconds: secs }, d);
""", shot='fine-default.png', clip='#cmp'),
    step("""
$('cmp').remove(); $('mode-j').click(); await idle();
const cv = $('view'), W = cv.width, H = cv.height;
await startJob('Twice', 'Fine', 'PNG');
const { bm } = await saveJob();
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return d;
""", shot='fine-julia.png', clip='#cmp'),
]


def main():
    name = sys.argv[1]
    args = sys.argv[2:]
    path = os.path.join(HERE, name + '.steps.json')
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(TESTS[name], f, indent=1, ensure_ascii=False)
    url = 'dist/r4-render-export.html'
    if '--url' in args:
        i = args.index('--url'); url = args[i + 1]; del args[i:i + 2]
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', url, '--actions', path] + args, cwd=ROOT, env=env))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in TESTS:
        main()
