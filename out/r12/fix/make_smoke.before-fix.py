"""Write the page's smoke test for round 12 (every approach an entry of its own) from the steps below.

  python out/r4/page/make_smoke.py            -> tools/smoke-v12.json
  python out/r4/page/make_smoke.py --mine     -> out/r12/page/smoke-mine.json (a trial copy)
  Screenshots of both go to out/r12/page/smoke/.

Run it with:  python tools/shot.py --url dist/<page>.html --actions tools/smoke-v12.json
Each step throws on a wrong state, so a failure shows as "page script failed" with the reason.
Write tools/smoke-v12.json only from a version that has passed as --mine: other people run that file too.
This script no longer writes tools/smoke.json. That file and tools/smoke-v9.json, tools/smoke-v9m.json belong to
earlier rounds (the Planes dial under one Sphere inversions entry) and must stay as they are.

The steps work for any number of entries and groups in the Approach list: they read L.APPROACHES and
L.APPROACH_GROUPS, and name an entry only where a button or a text of the page names it.
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MINE = '--mine' in sys.argv
SHOTS = 'out/r12/page/smoke/'

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(6)).join();
// which of 49 probes spread over the picture hit the solid: '1' for a hit, '0' for none
const probes = () => { let s = ''; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) s += L.pick(w * i / 8, h * j / 8) ? '1' : '0'; return s; };
const hits = s => s.split('1').length - 1;
const apId = () => L.APPROACHES[L.S.approach].id;   // the id of the approach in use
// 15 x 11 probes: [hits, hits on the outermost row or column]. A solid that is whole in the picture has (nearly) none on the ring.
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) if (L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11)) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } return [n, ring]; };
"""

steps = []


def step(js, shot=None, clip='#stage', wait='done', timeout=240):
    a = {'js': PRE + js.strip()}
    if wait:
        a['wait'] = wait
        a['timeout'] = timeout
    if shot:
        a['shot'] = SHOTS + 'smoke-' + shot + '.png'
        if clip:
            a['clip'] = clip
    steps.append(a)


# 1 the page as it opens
step(r"""
for (const id of ['extreme', 'resetAll', 'collapseAll', 'juliaPreset', 'juliaFrame', 'kleinPreset', 'kleinFrame', 'secExport', 'exportPanel', 'secMesh', 'meshPanel', 'pow', 'iter']) if (!$(id)) fail('the page lacks #' + id);
if (!$('qBal').classList.contains('is-on') || $('qBal').getAttribute('aria-pressed') !== 'true') fail('Balanced is not marked as the quality preset in use');
if (L.S.k.iter !== 150) fail('the Kleinian depth should start at 150, it is ' + L.S.k.iter);
if (L.S.extreme) fail('extreme ranges should start off');
const order = [...document.querySelectorAll('#sections > details.sec')].map(d => d.id).join(' ');
if (!/secQuality secExport secMesh$/.test(order)) fail('the two new sections should follow Quality and speed: ' + order);
const box = $('stage').getBoundingClientRect(), btn = $('reset').getBoundingClientRect();
if (scrollY !== 0 || box.top < 0 || box.bottom > innerHeight || btn.bottom > innerHeight) fail('when the page opens the whole picture with its buttons should be on the first screen: picture ' + Math.round(box.top) + ' to ' + Math.round(box.bottom) + ' of ' + innerHeight);
L.R.warmOn = false; L.S.q.aa = 3; L.touch();
return 'default; picture at ' + Math.round(box.top) + ' to ' + Math.round(box.bottom) + ' of ' + innerHeight + '; sections: ' + order;
""", '1-default')

# 2 wheel zoom
step(r"""
const cv = $('view'), d0 = L.cam.dist;
cv.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, bubbles: true, cancelable: true, clientX: 300, clientY: 300 }));
await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
const d1 = L.cam.dist; await sleep(600); const d2 = L.cam.dist;
if (Math.abs(Math.abs(Math.log(d2 / d0)) - Math.log(1.12)) > 0.01) fail('one wheel notch should change the distance by 12%: ' + d0 + ' -> ' + d2);
if (!((d1 - d0) * (d2 - d1) > 0)) fail('the zoom jumped instead of easing: ' + [d0, d1, d2]);
L.cam.dist = d0; L.touch();
return 'wheel zoom eased ' + d0 + ' -> ' + d1.toFixed(3) + ' -> ' + d2.toFixed(3);
""")

# 3 another approach: busy label and progress bar
step(r"""
$('ap-classic').click(); L.S.n = 8; L.S.iter = 10; L.syncControls(); L.cam.target = [0, 0, 0]; L.cam.dist = 4.2; L.refresh(false);
let busy = '', bar = false;
for (let i = 0; i < 4000 && !L.idle(); i++) { await sleep(16); const b = $('busy'), d = $('drawProgress'); if (b && !b.hidden) busy = b.textContent; if (d && !d.hidden) bar = true; }
if (!busy) fail('no busy label while the new approach was being prepared');
if (!bar) fail('the progress bar never showed while drawing');
return 'classic n=8; busy label seen: ' + busy + '; progress bar seen';
""", '2-classic8')

# 4 lathe with spin 3
step(r"""
$('ap-lathe').click(); L.S.n = 2; L.S.param.lathe.spin = 3; L.syncControls(); L.refresh(false);
return JSON.stringify(L.S.param.lathe);
""", '3-lathe-spin3')

# 5 Julia
step(r"""
$('ap-mercator').click(); $('mode-j').click();
L.S.colour.mode = 2; L.S.colour.pal = 1; L.syncControls(); L.cam.pitch = 1.5; L.cam.yaw = -Math.PI / 2; L.cam.dist = 4.4; L.touch();
return 'julia, escape count, ember';
""", '4-julia')

# 6 Kleinian
step(r"""
$('mode-k').click();
return 'kleinian';
""", '5-klein')

# 7 the whole page: texts and controls
step(r"""
document.querySelectorAll('details.sec').forEach(d => { d.open = true; });
const name = document.querySelector('#rules .rule .name').textContent;
if (name !== L.APPROACHES[0].name) fail('the first approach in the list should be ' + L.APPROACHES[0].name + ', it is ' + name);
if (!L.APPROACHES.some(a => a.id === 'mercator')) fail('the Sphere inversions approach (mercator) has gone from the list');
if ($('par-fold-planes').min !== '2' || $('par-fold-planes').max !== '8') fail('the Planes dial of Sphere inversions, two planes should run from 2 to 8');
if ($('par-mercator-planes') || $('par-fold-turn')) fail('the one-plane entry should have no Planes dial, and the two-planes entry no Turn dial');
for (const id of ['par-mercator-liftPlay', 'par-mercator-turnPlay', 'par-fold-liftPlay', 'par-tilt-tiltPlay', 'par-bulb-latPlay', 'par-bulb-lonPlay', 'par-classic-thetaPlay', 'par-classic-phiPlay', 'col-shiftPlay']) if (!$(id)) fail('no play button ' + id);
const foot = document.querySelector('footer.why').textContent;
for (const t of ['Inversions added together can', 'the count is a free choice', 'the solid pulses from its poles', 'Questions from testing, answered', 'What does a list entry change?', 'Do quaternions or the third map have a part in this?',
  'The version you tested is the one the list now calls Sphere inversions, two planes', 'not a published theorem', 'in the list as Quaternion square (Lathe)', 'limited to c ∈ R',
  'kept as an entry of its own', 'Back to one plane chooses Sphere inversions, one plane, and changes nothing else', 'only under Sphere inversions, two planes',
  'Is there a quaternion rule that works everywhere in space?', 'checked against each other on 200,000 points', 'The rings break up into one body with tunnels', 'up close its skin is smooth',
  'Could the hidden rotation axis of the flat picture show the way?', 'a turn needs a plane to turn in', 'The twisted square is what makes that second turn count', 'the words on it say what it will change', 'is an open problem', 'This works in Mandelbrot and Julia pictures',
  'The slices were in the colouring, not in the shape', 'Now the colour is read from the surface itself', 'So a place keeps its colour at Ultra fast, Fast, Balanced and Fine', 'the first real test of saving a file from the published page is yours', 'Preparing the formula',
  'Every rule has a mirror twin', 'the pictures match pixel for pixel', 'None of the three is Figure 4', 'at 0 the trap shape itself is part of the solid',
  'shows the beads as separate discs', 'came out as one piece at every height that was tried', 'a tiny circle drawn on the ball is still a circle', 'like a cushion with a front and a back',
  'the jump does not show', 'it is moved just far enough']) if (!foot.includes(t)) fail('the closing text lacks: ' + t);
if (document.querySelector('[data-needs]') || document.querySelector('footer.why [hidden]')) fail('a closing text is still held back');
// every control the closing text names must be on the page under that very label
const names = new Set([...document.querySelectorAll('.dials label, .dials button, .dials option, .dials optgroup, .dials summary, .dials .rule .name, footer.why button')].map(e => (e.label || e.textContent).replace(/\s+/g, ' ').trim()));
const has = t => names.has(t) || [...names].some(n => n.startsWith(t + ' ') || n.startsWith(t + ',') || n.startsWith(t + ':'));
for (const t of ['Planes', 'Use the third map', 'In the 3D view the trap', 'Colours the surface', 'Is the solid', 'Is added to the solid', 'Trap thickness', 'Trap shape', 'Orbit steps skipped at the start',
  '2D view', 'Outline width, pixels', 'Glow beside the outline, pixels', 'Inside the set, colour by', 'Plain', 'Orbit trap', 'Where the orbit ends up', 'How deep inside', 'How quickly the orbit settles', 'Palette for the inside',
  'Colour the cut face like the inside of the 2D view', 'Glow width', 'Balanced', 'Colour by', 'Sphere shell', 'How near it came, as a glow', 'Rainbow', 'Depth of the search', 'Extreme ranges', 'Iterations', 'Ray steps, at most', 'Refining passes', 'Power n',
  'Frame it', 'As it was found', 'Found with two planes', 'Turning-out sphere', 'Save a picture', 'Start the picture', 'Size', 'Quality', 'File type', 'Save the file', 'Save a 3D model', 'Start the model', 'Show Figure 4', 'Back to one plane', 'Sphere inversions', 'Colour and light',
  'Sphere inversions, one plane', 'Sphere inversions, two planes', 'Quaternion square (Lathe)', 'Quaternion square, twisted', 'Turn', 'Lift', 'Spin multiplier (odd)', 'Tilt of the axis, degrees',
  'Show the quaternion square', 'Show the twisted quaternion square', 'Kleinian group',
  'flip z', 'Height z of the cut or slice', 'Trap radius', 'Twin of Sphere inversions', 'Twin of the Lathe', 'Twin of the Mandelbulb', 'Back to the plain rule', 'Mandelbulb', 'Orbit steps the trap reads', 'Examples', 'Surface threshold, pixels']) {
  if (!has(t)) fail('the closing text names a control that the page does not have under that label: ' + t);
  if (!foot.includes(t)) fail('the closing text no longer names: ' + t);
}
if (!$('pd-mercator').textContent.includes('Sphere inversions, two planes') || !document.querySelector('.rule[data-ap=fold]').textContent.includes('earlier version')) fail('the two Sphere inversions entries do not say how they belong together');
// the closing text names the entries kept for the record exactly when the list has some
const tried = L.APPROACHES.filter(a => a.group === 'tried'), triedTitle = ((L.APPROACH_GROUPS || []).find(g => g.id === 'tried') || {}).title;
if (!$('triedNote')) fail('the closing text has no place for the entries kept for the record');
if (!tried.length && $('triedNote').textContent) fail('the closing text names entries kept for the record, and the list has none');
if (tried.length && (!foot.includes(triedTitle) || tried.some(a => !$('triedNote').textContent.includes(a.name)))) fail('the closing text should name the heading and every entry kept for the record: ' + $('triedNote').textContent);
const all = document.body.textContent;
if (!all.includes('turns a rule into its mirror twin')) fail('the note under Modifiers does not say what flip z is for');
for (const t of ['had Planes at 2', 'Planes at 1', 'set Planes to 2', 'the Lathe approach', 'Planes 1, Turn 0', 'cannot be built from inversions', 'rebuilt by eye', 'the bounded piece that is left', 'sampling its derivative', 'pole phase', 'one smooth piece at every height', 'keeps angles true', 'wind it three times', 'hides the jump']) if (all.includes(t)) fail('an old wording is still on the page: ' + t);
if (!document.querySelector('.lede').textContent.includes('the ordinary 2D Mandelbrot or Julia set')) fail('the lede does not say what the flat set is');
// the trap solid examples: a list right under "In the 3D view the trap", nine entries under three headings
const ex = $('trapExamples');
if (!ex || ex.options.length !== 10 || [...ex.querySelectorAll('optgroup')].map(g => g.label).join() !== 'Mandelbrot,Julia,Kleinian') fail('the Examples list should hold nine trap solids under Mandelbrot, Julia and Kleinian');
if (!has('Examples') || $('exampleHost').previousElementSibling !== $('col-solid').closest('.field')) fail('the Examples list should stand right under In the 3D view the trap');
if (!!$('powStep') === !!L.APPROACHES[L.S.approach].integerOnly) fail('the power dial has a step toggle exactly when the approach takes any power');
if ($('iterStep')) fail('the iterations dial must not have a step toggle');
return document.querySelectorAll('.dial').length + ' dials, ' + document.querySelectorAll('select').length + ' selects, ' + document.querySelectorAll('.dial-reset').length + ' reset buttons; every closing text is on show and names its controls by their labels';
""", '6-page', clip=None, wait=None)

# The Approach list: a heading from APPROACH_GROUPS before the first entry of each group, nothing for a group
# without entries, every entry with its ids, and one set of radios in the order the list is shown.
step(r"""
$('mode-m').click(); await sleep(100);   // the Approach section is put away in the Kleinian view
const groups = L.APPROACH_GROUPS, A = L.APPROACHES;
if (!Array.isArray(groups) || !groups.length) fail('window.squaringLab.APPROACH_GROUPS is missing');
const known = new Set(groups.map(g => g.id));
// what the list should read, top to bottom: ['head', title] and ['entry', id]
const want = [];
for (const g of groups) { const list = A.filter(a => a.group === g.id); if (list.length) { want.push('head ' + g.title); list.forEach(a => want.push('entry ' + a.id)); } }
A.filter(a => !known.has(a.group)).forEach(a => want.push('entry ' + a.id));
const got = [...document.querySelectorAll('#rules .rule-group-head, #rules .rule')].map(e => (e.classList.contains('rule') ? 'entry ' + e.dataset.ap : 'head ' + e.textContent));
if (got.join(' | ') !== want.join(' | ')) fail('the Approach list should read ' + want.join(' | ') + ' and reads ' + got.join(' | '));
const heads = [...document.querySelectorAll('#rules .rule-group-head')];
for (const h of heads) {
  const first = h.parentNode.querySelector('.rule');
  if (!first || h.nextElementSibling !== first) fail('the heading ' + h.textContent + ' does not stand right before the first entry of its group');
  if (h.parentNode.getAttribute('aria-labelledby') !== h.id) fail('the group under ' + h.textContent + ' is not named by its heading');
  if (h.getBoundingClientRect().width <= 0) fail('the heading ' + h.textContent + ' is not on show');
}
const radios = [...document.querySelectorAll('#rules input[type=radio]')];
if (radios.length !== A.length || radios.some(r => r.name !== 'approach')) fail('every entry needs one radio of the set "approach", so that the arrow keys walk the whole list');
if (radios.map(r => r.id).join() !== want.filter(w => w.startsWith('entry ')).map(w => 'ap-' + w.slice(6)).join()) fail('the radios are not in the order the list is shown');
if (radios.filter(r => r.checked).length !== 1 || document.querySelectorAll('#rules .rule.is-on').length !== 1) fail('exactly one entry should be marked as chosen');
for (const a of A) {
  for (const id of ['ap-' + a.id, 'f-' + a.id, 'pd-' + a.id]) if (!$(id)) fail('the list lacks #' + id);
  if (+$('ap-' + a.id).value !== A.indexOf(a)) fail('the radio of ' + a.name + ' does not carry its place in the list of approaches');
  for (const s of a.params || []) if (s.key !== undefined && !$('par-' + a.id + '-' + s.key)) fail('the list lacks #par-' + a.id + '-' + s.key);
  const rule = document.querySelector('.rule[data-ap="' + a.id + '"]');
  if (rule.querySelector('.name').textContent !== a.name || !rule.querySelector('.tag').textContent.trim()) fail('the entry ' + a.id + ' does not show its name and its one-line description');
}
if (document.documentElement.scrollWidth > innerWidth + 1) fail('the page is wider than the window: ' + document.documentElement.scrollWidth + ' of ' + innerWidth);
return heads.length + ' headings (' + heads.map(h => h.textContent).join(', ') + ') over ' + A.length + ' entries: ' + got.filter(w => w.startsWith('entry ')).map(w => w.slice(6)).join(', ');
""", '6b-approach-list', clip='#secApproach', wait=None)

# Every entry draws: its Mandelbrot solid, and its Julia set for c = -1. The loop runs in the page and the step
# waits for it, so it works for any number of entries (a script that awaited it would hit the tool's time limit).
step(r"""
const E = window.smokeEntries = { done: false, error: '', rows: [] };
(async () => {
  try {
    const settle = async name => { await sleep(150); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 120000) throw new Error('the picture of ' + name + ' was not finished after 120 s'); await sleep(40); } };
    for (const mode of ['m', 'j']) {
      $('mode-' + mode).click();
      if (mode === 'j') L.applyJuliaPreset({ c: [-1, 0, 0] });
      for (const a of L.APPROACHES) {
        const what = (mode === 'm' ? 'the Mandelbrot solid of ' : 'the Julia set for c = −1 of ') + a.name;
        $('ap-' + a.id).click(); await settle(what);
        const on = [...document.querySelectorAll('#rules .rule.is-on')];
        if (apId() !== a.id || !$('ap-' + a.id).checked || on.length !== 1 || on[0].dataset.ap !== a.id) throw new Error('choosing ' + a.name + ' did not take');
        if (on[0].querySelector('.rule-body').getBoundingClientRect().height <= 0) throw new Error('the chosen entry ' + a.name + ' does not show its formula and dials');
        if (!$('f-' + a.id).textContent.trim()) throw new Error('no formula text for ' + a.name);
        const g = grid();
        E.rows.push(a.id + ' ' + mode + ' ' + g[0]);
        if (g[0] < 1) throw new Error(what + ' is empty: none of 165 probes hit');
      }
    }
  } catch (e) { E.error = e.message || String(e); }
  E.done = true;
})();
return 'drawing every entry, Mandelbrot solid and Julia set for c = −1: ' + L.APPROACHES.map(a => a.id).join(', ');
""", '6c-every-entry', wait='window.smokeEntries && window.smokeEntries.done', timeout=900)
step(r"""
const E = window.smokeEntries;
if (E.error) fail(E.error + ' (drawn before that: ' + E.rows.join(', ') + ')');
if (E.rows.length !== 2 * L.APPROACHES.length) fail('not every entry was drawn: ' + E.rows.join(', '));
$('ap-mercator').click(); $('mode-k').click();
return 'every entry drew (entry, m or j, probes hit of 165): ' + E.rows.join(', ');
""")

# 8 2D view
step(r"""
$('mode-m').click(); document.querySelector('#colReset .dial-reset').click(); L.S.q.aa = 2; L.syncControls();
for (const id of ['lightAz', 'qsteps', 'viewFly', 'viewBound', 'qShadow', 'qde']) if (!shown(id)) fail(id + ' should be visible in the 3D view');
$('flat').click();
if (!L.S.flat) fail('the 2D view checkbox did not set S.flat');
await sleep(300);
if ($('stage').dataset.cam !== 'flat') fail('the stage did not switch to 2D input');
if (!$('camMode').hidden) fail('the camera switch should hide in the 2D view');
for (const id of ['lightAz', 'lightEl', 'qsteps', 'qdetail', 'qstepk', 'qsmooth', 'qde', 'normals', 'qShadow', 'qAO', 'viewFly', 'viewSpeed', 'viewFov', 'viewBound']) if (shown(id)) fail(id + ' does nothing in the 2D view and should be put away there');
for (const id of ['qres', 'qaa', 'cut']) if (!shown(id)) fail(id + ' still matters in the 2D view and should stay');
L.S.cut = 0.35; L.syncControls(); L.touch(); await sleep(200);
if (!$('flatHost').textContent.includes('z = 0.35')) fail('the 2D view label does not say which slice is drawn: ' + $('flatHost').textContent);
L.S.cut = 0; L.syncControls(); L.touch();
return '2D view on, slice height ' + L.S.cut + ', picture height ' + L.S.v2.h.toFixed(2) + '; label: ' + $('flatHost').textContent.trim();
""", '7-flat')

# 9 mosaic in 3D: opens the cut at z = 0
step(r"""
$('flat').click();
if (L.S.flat) fail('2D view did not switch off');
if (!shown('lightAz') || !shown('qsteps')) fail('the 3D controls did not come back');
if (!$('m-mosaicCell').closest('.dial').hidden) fail('the cell dial should be hidden until the mosaic is on');
if (L.S.cutOn) fail('the cut should be off before the mosaic is ticked');
$('m-mosaic').click();
if (!L.S.mosaic) fail('the mosaic checkbox did not set S.mosaic');
if ($('m-mosaicCell').closest('.dial').hidden) fail('the cell dial did not appear');
if (!L.S.cutOn || L.S.cut !== 0 || !$('cutOn').checked) fail('ticking the mosaic in 3D should cut the solid open at z = 0');
return 'mosaic on, cell ' + L.S.mosaicCell + ', cut open at z = ' + L.S.cut;
""", '8-mosaic')

# 10 mosaic in 2D
step(r"""
$('flat').click();
return 'mosaic in the 2D view';
""", '9-mosaic-flat')

# 11 a negative power, typed
step(r"""
$('flat').click(); $('m-mosaic').click();
if (L.S.mosaic || L.S.flat) fail('mosaic or 2D view still on');
if (L.S.cutOn) fail('unticking the mosaic should put the cut back as it was (off)');
type('powNum', '−2');
if (L.S.n !== -2) fail('typing a negative power gave n = ' + L.S.n);
if ($('pow').min !== '-8' || $('pow').max !== '10') fail('the power slider is not -8 to 10');
return 'n = ' + L.S.n + ', formula: ' + $('f-' + L.APPROACHES[L.S.approach].id).textContent.slice(0, 60);
""", '10-negative-power')

# 12 Equation reset keeps the view; approach parameters
step(r"""
$('ap-mercator').click();
L.cam.yaw += 0.3; L.touch(); const view = camNow();
document.querySelector('#eqReset .dial-reset').click();
if (L.S.n !== 2 || L.S.iter !== 14) fail('the Equation reset did not restore n and the iterations');
if (camNow() !== view) fail('the Equation reset moved the camera');
$('ap-fold').click(); await sleep(100);
type('par-fold-planesNum', '3');
if (L.S.param.fold.planes !== 3 || !$('f-fold').textContent.includes('3 planes')) fail('the Planes dial of the two-planes entry did not set the planes, or the formula text did not follow: ' + $('f-fold').textContent);
type('par-fold-planesNum', '1');
if (L.S.param.fold.planes < 2) fail('the Planes dial should not go below 2, it is at ' + L.S.param.fold.planes);
type('par-fold-planesNum', '2');
$('ap-mercator').click(); await sleep(100);
if ($('par-mercator-turn').closest('.dial').hidden) fail('the one-plane entry should show its Turn dial');
type('par-mercator-turnNum', '40'); type('par-mercator-liftNum', '0.3');
const p = L.S.param.mercator;
if (p.turn !== 40 || p.lift !== 0.3 || p.planes !== undefined) fail('approach parameters not set: ' + JSON.stringify(p));
if (!$('f-mercator').textContent.includes('40')) fail('the formula text did not follow the turn dial');
return JSON.stringify(p);
""", '11-approach-params')

# 13 Approach reset, then a trap choice
step(r"""
document.querySelector('#approachReset .dial-reset').click();
if (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');
for (const a of L.APPROACHES) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined && L.S.param[a.id][s.key] !== s.def) fail('the Approach reset left ' + s.label + ' of ' + a.name + ' at ' + L.S.param[a.id][s.key]);
$('ap-mercator').click();
pick('col-trap', 'Cross'); pick('col-by', 'How near it came, as a glow'); pick('col-pal', 'Electric');
const c = L.S.colour;
if (c.trap !== 1 || c.by !== 4) fail('trap choice not set: ' + JSON.stringify(c));
return 'trap ' + c.trap + ', by ' + c.by + ', palette ' + c.pal;
""", '12-trap-cross')

# 14 quality presets and their mark
step(r"""
type('qstepkNum', '0.5'); type('qsmoothNum', '2');
if (document.querySelector('#secQuality .row-btns .is-on')) fail('no preset should be marked after a hand change');
$('qUltra').click();
const q = L.S.q;
if (q.de !== 0 || q.res !== 0.5 || q.aa !== 1 || q.shadow || q.ao || q.normals !== 'smooth') fail('Ultra fast did not apply: ' + JSON.stringify(q));
if (q.stepk !== 0.8 || q.smooth !== 1) fail('a preset should set every dial of the section: ' + JSON.stringify(q));
if ($('qde').selectedIndex !== 2 || $('qShadow').checked) fail('the quality controls do not show the preset');
if (!$('qUltra').classList.contains('is-on') || $('qBal').classList.contains('is-on')) fail('Ultra fast is not marked as the preset in use');
return 'ultra fast: ' + JSON.stringify(q);
""", '13-ultra-fast')

# 15 Kleinian list: an entry sets the group and nothing else; Frame it; your own values; reset
step(r"""
$('mode-k').click();
if ($('kleinPanel').hidden || !$('juliaPanel').hidden || !$('secApproach').hidden) fail('wrong panels for Kleinian mode');
L.cam.yaw += 0.4; L.cam.dist *= 0.8; L.touch(); type('kiterNum', '90');
const view = camNow();
pick('kleinPreset', '1/3 cusp');
if (Math.abs(L.S.k.mx - 0.581203) > 1e-9 || L.S.k.three !== true) fail('the Kleinian entry did not apply: ' + JSON.stringify(L.S.k));
if (camNow() !== view) fail('a Kleinian entry moved the camera');
if (L.S.k.iter !== 90) fail('a Kleinian entry changed the depth of the search to ' + L.S.k.iter);
if ($('kmxNum').value !== '0.581203') fail('the Kleinian dials do not show the entry');
if (!$('kleinNote').textContent.startsWith('Turned out')) fail('the entry note is missing');
if (chosen('kleinPreset') !== '1/3 cusp') fail('the list should show the chosen entry, it shows ' + chosen('kleinPreset'));
$('kleinFrame').click();
if (camNow() === view) fail('Frame it did not move the camera');
if (L.S.k.iter !== 90 || Math.abs(L.S.k.mx - 0.581203) > 1e-9) fail('Frame it changed more than the camera');
const framed = camNow();
type('kmxNum', '0.6');
if (chosen('kleinPreset') !== 'Your own values') fail('with a dial moved off the entry the list should read Your own values, it reads ' + chosen('kleinPreset'));
pick('kleinPreset', '0/1 cusp, one row');
if (L.S.k.three !== false || shown('kL')) fail('the L dial should be put away while the third map is off');
document.querySelector('#kleinReset .dial-reset').click();
if (camNow() !== framed) fail('the Kleinian reset moved the camera');
if (L.S.k.iter !== 150 || L.S.k.my !== 2 || !L.S.k.three || !shown('kL')) fail('the Kleinian reset left ' + JSON.stringify(L.S.k));
if (chosen('kleinPreset') !== L.KLEIN_PRESETS[0].name) fail('after the reset the list should show the first entry');
if (!$('kleinWarn').hidden) fail('an entry of the list should not show the warning about broken pictures');
type('kmyNum', '1.3'); await sleep(100);
if ($('kleinWarn').hidden) fail('walls this close together (i part 1.3) should show a warning');
document.querySelector('#kleinReset .dial-reset').click();
if (!$('kleinWarn').hidden) fail('the warning should go when the values are back on an entry');
// a turning-out sphere so large that the solid swallows the camera: a sentence says so, and goes from far enough away
L.cam.dist = 7; L.touch(); type('kinvrNum', '3'); await sleep(250);
if ($('kleinWarn').hidden || !$('kleinWarn').textContent.includes('grown past the camera')) fail('a turning-out radius of 3 fills the picture and the page should say so');
L.cam.dist = 45; L.touch(); await sleep(250);
if ($('kleinWarn').textContent.includes('grown past the camera')) fail('from far enough away the sentence about the camera should go');
// ... but this solid reaches past the Drawing radius, and from far away that is what cuts it off: a sentence of its own
if ($('kleinWarn').hidden || !$('kleinWarn').textContent.includes('reaches past the Drawing radius')) fail('a solid that reaches past the Drawing radius should say so from far away');
const bound0 = L.S.view.bound; L.S.view.bound = 40; L.syncControls(); L.touch(); await sleep(250);
if (!$('kleinWarn').hidden) fail('with the Drawing radius raised the sentence should go');
L.S.view.bound = bound0; L.syncControls(); L.touch(); await sleep(150);
type('kinvrNum', '1.5'); L.cam.dist = 7; L.touch(); await sleep(250);
if (!$('kleinWarn').hidden) fail('a radius of 1.5 is whole in the picture and should not show the sentence');
L.cam.dist = 1.2; L.touch(); await sleep(250);
if (!$('kleinWarn').hidden) fail('coming in close on a solid of ordinary size should not show the sentence about a large radius');
L.cam.dist = 7; L.touch();
document.querySelector('#kleinReset .dial-reset').click();
// every name can be read in the closed list
const ks = $('kleinPreset'), kcs = getComputedStyle(ks), kc = document.createElement('canvas').getContext('2d');
kc.font = kcs.fontWeight + ' ' + kcs.fontSize + ' ' + kcs.fontFamily;
const long = [...ks.options].filter(o => kc.measureText(o.text).width > ks.clientWidth - parseFloat(kcs.paddingLeft) - parseFloat(kcs.paddingRight) - 18).map(o => o.text);
if (long.length) fail('Kleinian names too long for the closed list: ' + long.join(' | '));
pick('kleinPreset', '1/3 cusp'); $('kleinFrame').click();
return ($('kleinPreset').options.length - 1) + ' Kleinian entries in ' + $('kleinPreset').querySelectorAll('optgroup').length + ' groups; an entry leaves camera and depth alone; Frame it moves only the camera';
""", '14-klein-preset')

# 16 Julia list: a drop-down; an entry sets c and nothing else; Frame it; saving and deleting
step(r"""
$('mode-j').click(); $('qFast').click();
const sel = $('juliaPreset');
if (sel.tagName !== 'SELECT') fail('the Julia list should be a drop-down');
const groups = [...sel.querySelectorAll('optgroup')].map(g => g.label);
if (groups.join('|') !== 'Classic sets|Found by exploring|Found with two planes') fail('unexpected groups in the Julia list: ' + groups.join('|'));
const two = [...sel.querySelectorAll('optgroup')].pop(), twoNames = [...two.children].map(o => o.text).join('|');
if (twoNames !== 'Cracked Basilica|Split conch|Flint|Plated egg|Plated ball|Cracked gourd') fail('the entries found with two planes are: ' + twoNames);
L.cam.yaw += 0.3; L.touch(); type('iterNum', '17');
const view = camNow(), approach = JSON.stringify([L.S.approach, L.S.param]);
pick('juliaPreset', 'Douady rabbit');
const c = L.S.c;
if (Math.abs(c[0] + 0.122561) > 1e-9 || Math.abs(c[1] - 0.744862) > 1e-9) fail('the Julia entry did not set c: ' + c);
if (camNow() !== view) fail('a Julia entry moved the camera');
if (L.S.iter !== 17) fail('a Julia entry changed the iterations to ' + L.S.iter);
if (JSON.stringify([L.S.approach, L.S.param]) !== approach) fail('a Julia entry changed the approach or one of its dials');
if ($('cyNum').value !== '0.744862') fail('the c dials do not show the entry');
if (chosen('juliaPreset') !== 'Douady rabbit' || !$('juliaNote').textContent.startsWith('The centre of')) fail('the list or its note does not show the entry');
$('juliaFrame').click();
if (camNow() === view) fail('Frame it did not move the camera');
if (L.S.iter !== 17 || Math.abs(L.S.c[1] - 0.744862) > 1e-9) fail('Frame it changed more than the camera');
type('cxNum', '-0.2');
if (chosen('juliaPreset') !== 'Your own values') fail('with c moved off the entry the list should read Your own values, it reads ' + chosen('juliaPreset'));
if (!$('juliaDelete').hidden) fail('the delete button should only show for a saved point');
$('juliaName').value = 'Smoke test point'; $('juliaSave').click();
let saved = L.juliaSaved();
if (!saved.length || saved[saved.length - 1].name !== 'Smoke test point') fail('Save this point did not add to the list');
if (Object.keys(saved[saved.length - 1]).some(k => k === 'cam' || k === 'planes' || k === 'iter')) fail('a saved point should hold only c and a name');
if (chosen('juliaPreset') !== 'Smoke test point' || sel.querySelector('optgroup').label !== 'Your saved points') fail('the saved point is not on top of the list and chosen');
if ($('juliaDelete').hidden) fail('no delete button for the saved point');
const n = saved.length;
$('juliaName').value = 'Smoke test point'; $('juliaSave').click();
if (L.juliaSaved().length !== n) fail('saving the same point under the same name made a second entry');
$('juliaDelete').focus(); $('juliaDelete').click();
if (L.juliaSaved().length !== n - 1) fail('Delete did not remove the saved point');
if (document.activeElement === document.body) fail('focus was lost after deleting a saved point');
Object.defineProperty(window, 'localStorage', { configurable: true, get() { throw new Error('storage is blocked'); } });
$('juliaName').value = 'No storage point'; $('juliaSave').click();
if (!L.juliaSaved().some(p => p.name === 'No storage point')) fail('saving failed when storage is blocked');
if ($('juliaSaveNote').hidden) fail('no note that the point is kept for this visit only');
if (![...sel.options].some(x => x.text === 'No storage point')) fail('the saved point is not in the list');
$('juliaDelete').click();
if (L.juliaSaved().some(p => p.name === 'No storage point')) fail('delete failed when storage is blocked');
delete window.localStorage;
pick('juliaPreset', 'Douady rabbit');
return (sel.options.length - 1) + ' Julia points in a drop-down; an entry leaves camera, iterations and the approach alone; Frame it moves only the camera; saving also works with storage blocked';
""", '15-julia-preset')

# "As it was found": the Sphere inversions entry (one plane, or two planes with their count) and the iterations
# an entry records, nothing else, and only while they differ. The words on the button say what it will do.
step(r"""
if (apId() !== 'mercator' || L.S.iter !== 17) fail('unexpected state before the test: ' + [apId(), L.S.iter]);
const f = $('juliaFound');
if (!shown('juliaFound')) fail('the rabbit records 24 iterations and the page has 17: As it was found should be on show');
if (f.textContent !== 'As it was found: 24 iterations' || !f.title.includes('Iterations to 24')) fail('the words on the button should say what it will do: ' + f.textContent + ' / ' + f.title);
const view = camNow(), c = L.S.c.join(), dials = JSON.stringify(L.S.param);
f.focus(); f.click(); await sleep(150);
if (L.S.iter !== 24 || $('iterNum').value !== '24' || apId() !== 'mercator') fail('As it was found should set 24 iterations and leave the approach: ' + [L.S.iter, apId()]);
if (camNow() !== view || L.S.c.join() !== c) fail('As it was found changed the camera or c');
if (shown('juliaFound')) fail('As it was found should go when nothing differs any more');
if (document.activeElement === document.body) fail('focus was lost when the button went');
// an entry found with two planes, while the one-plane entry is in use: the button goes to the two-planes entry
pick('juliaPreset', 'Cracked Basilica'); await sleep(150);
if ($('juliaPreset').selectedOptions[0].parentNode.label !== 'Found with two planes') fail('Cracked Basilica is not under Found with two planes');
const note = $('juliaNote').textContent;
if (!note.includes('Sphere inversions, two planes') || /set Planes|Planes to/.test(note)) fail('the note of an entry found with two planes should name the entry of the Approach list, not a dial: ' + note);
if (!shown('juliaFound') || f.textContent !== 'As it was found: two planes' || !f.title.includes('Sphere inversions, two planes')) fail('an entry found with two planes should offer the two-planes entry while the one-plane entry is in use: ' + f.textContent + ' / ' + f.title);
const c2 = L.S.c.join();
f.click(); await sleep(150);
if (apId() !== 'fold' || !$('ap-fold').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'fold') fail('As it was found should choose Sphere inversions, two planes: ' + apId());
if (L.S.param.fold.planes !== 2 || L.S.iter !== 24 || JSON.stringify(L.S.param) !== dials) fail('As it was found should leave the planes at 2 and move no other dial: ' + JSON.stringify(L.S.param));
if (camNow() !== view || L.S.c.join() !== c2 || L.S.mode !== 'j') fail('As it was found changed the camera, c or the kind of picture');
if (shown('juliaFound')) fail('the button should go once the entry is in use with the planes as recorded');
// the two-planes entry in use with another count: the button sets the count
type('par-fold-planesNum', '3'); await sleep(150);
if (!shown('juliaFound') || f.textContent !== 'As it was found: two planes' || !f.title.includes('Planes to 2')) fail('with Planes at 3 the button should offer to set them to 2: ' + f.textContent + ' / ' + f.title);
f.click(); await sleep(150);
if (L.S.param.fold.planes !== 2 || $('par-fold-planesNum').value !== '2' || apId() !== 'fold') fail('As it was found should set Planes to 2 and nothing else');
// an entry found with one plane, while the two-planes entry is in use: the button goes to the one-plane entry
pick('juliaPreset', 'Dendrite'); await sleep(150);
if (!shown('juliaFound') || f.textContent !== 'As it was found: one plane' || !f.title.includes('Sphere inversions, one plane')) fail('an entry found with one plane should offer the one-plane entry while the two-planes entry is in use: ' + f.textContent + ' / ' + f.title);
f.click(); await sleep(150);
if (apId() !== 'mercator' || !$('ap-mercator').checked || JSON.stringify(L.S.param) !== dials) fail('As it was found should choose Sphere inversions, one plane and move no dial: ' + apId());
if (shown('juliaFound')) fail('the button should go once the one-plane entry is in use');
// under any other approach the two entries do not count
$('ap-lathe').click(); pick('juliaPreset', 'Cracked Basilica'); await sleep(150);
if (shown('juliaFound')) fail('under another approach the button should stay away: ' + f.textContent);
$('ap-mercator').click(); await sleep(150);
if (!shown('juliaFound')) fail('back under Sphere inversions, one plane the button should return');
f.click(); await sleep(150);
if (apId() !== 'fold') fail('the button did not choose the two-planes entry the second time');
return 'As it was found: 24 iterations for the rabbit; Cracked Basilica goes to Sphere inversions, two planes, and sets Planes back from 3 to 2; Dendrite goes back to one plane; camera, c and the other dials untouched; hidden when nothing differs and under another approach';
""", '15b-as-it-was-found')

# back to where the following steps expect the page: one plane, 17 iterations, the rabbit
step(r"""
$('ap-mercator').click(); type('iterNum', '17'); pick('juliaPreset', 'Douady rabbit');
if (apId() !== 'mercator' || L.S.param.fold.planes !== 2) fail('could not put the page back to the one-plane entry');
return 'the one-plane entry and 17 iterations again';
""")

# 17 fly camera
step(r"""
$('camFly').click();
if (!L.S.view.fly || $('stage').dataset.cam === 'arc') await sleep(300);
if (!L.S.view.fly || $('stage').dataset.cam !== 'fly') fail('the Fly button did not switch the camera');
if (!$('viewFly').checked) fail('the View section checkbox did not follow');
const a = L.basis().pos.slice(), cv = $('view');
cv.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyW', key: 'w', bubbles: true }));
await sleep(700);
window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyW', key: 'w', bubbles: true }));
await sleep(400);
const b = L.basis().pos, moved = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
if (!(moved > 0.05)) fail('holding W did not move the fly camera: ' + moved);
return 'fly camera moved ' + moved.toFixed(3) + ' at speed ' + L.S.view.speed;
""", '16-fly')

# 18 section resets
step(r"""
const viewReset = document.querySelector('#viewReset .dial-reset');
viewReset.click();
if (L.S.view.fly || L.S.view.bound !== 8 || L.S.view.fov !== 0.32) fail('the View reset left ' + JSON.stringify(L.S.view));
await sleep(300);
if ($('stage').dataset.cam !== 'arc' || $('viewFly').checked) fail('the camera did not go back to arcball');
type('camFar', '200');
if (L.S.view.zmax !== 200) fail('typing the farthest zoom limit on the stage slider gave ' + L.S.view.zmax);
type('viewBoundNum', '500');
if (L.S.view.bound !== 500) fail('the drawing radius should reach 500, got ' + L.S.view.bound);
type('viewBoundNum', '900');
if (L.S.view.bound !== 500) fail('the drawing radius should stop at 500 while extreme ranges are off');
viewReset.click();
if (L.S.view.zmax !== 60 || L.S.view.bound !== 8) fail('the View reset left the limits at ' + JSON.stringify(L.S.view));
document.querySelector('#qReset .dial-reset').click();
const q = L.S.q;
if (q.de !== 3 || q.res !== 1 || q.aa !== 12 || !q.shadow || !q.ao || q.normals !== 'sharp' || q.steps !== 260) fail('the Quality reset left ' + JSON.stringify(q));
if ($('qde').selectedIndex !== 0 || !$('qShadow').checked) fail('the quality controls do not show the reset values');
if (!$('qBal').classList.contains('is-on')) fail('after the Quality reset Balanced should be marked');
$('juliaName').value = 'left over';
document.querySelector('#juliaReset .dial-reset').click();
if (L.S.c.join() !== '-1,0,0') fail('the Julia reset left c = ' + L.S.c);
if ($('juliaName').value !== '') fail('the Julia reset left a name in the box');
L.resetCam(); L.S.q.aa = 2; L.syncControls(); L.touch();
return document.querySelectorAll('.dial-reset').length + ' reset buttons; view (with zoom limits and drawing radius), quality and Julia resets restore their defaults';
""", '17-after-resets')

# 19 extreme ranges
step(r"""
if (typeof L.setExtreme !== 'function') return 'skipped: the dial kit of this page has no extreme ranges (setExtreme is missing)';
$('mode-m').click();
const max0 = $('iter').max, kmax0 = $('kiter').max;
$('extreme').click(); await sleep(100);
if (!L.S.extreme || !L.isExtreme()) fail('the switch did not set S.extreme');
if (!(+$('iter').max > +max0) || !(+$('kiter').max > +kmax0) || !(+$('qsteps').max > 700) || !(+$('pow').max > 10)) fail('the ranges did not widen: ' + [$('iter').max, $('kiter').max, $('qsteps').max, $('pow').max]);
const wide = [...document.querySelectorAll('.dial-wide')].filter(e => !e.hidden).length;
if (wide < 15) fail('only ' + wide + ' dials show a wider range');
type('iterNum', '2000');
if (L.S.iter !== 2000) fail('with extreme ranges on, 2000 iterations should be accepted: ' + L.S.iter);
type('iterNum', '40');
type('viewBoundNum', '900');
if (L.S.view.bound !== 900) fail('with extreme ranges on the drawing radius should reach 900');
$('extreme').click(); await sleep(100);
if (L.S.extreme) fail('the switch did not go off');
if ($('iter').max !== max0) fail('the iterations slider did not go back to its usual range');
if (L.S.view.bound !== 500 || $('viewBoundNum').value !== '500') fail('switching off should pull the drawing radius back to 500, it is ' + L.S.view.bound);
document.querySelector('#viewReset .dial-reset').click(); document.querySelector('#eqReset .dial-reset').click();
return 'extreme ranges: ' + wide + ' dials widen (iterations ' + max0 + ' -> 400 on the slider, typed to 4000); switching off pulled the drawing radius from 900 back to 500';
""", '18-extreme-off')

# 20 an approach that only takes whole powers
step(r"""
const free = L.APPROACHES.find(a => !a.integerOnly && a.id !== 'bulb');
$('ap-bulb').click();
if (L.APPROACHES.find(a => a.id === 'bulb').integerOnly) fail('the Mandelbulb should take any power');
type('powNum', '2.5');
if (L.S.n !== 2.5 || !$('powStep') || !$('powWhole').hidden) fail('a free approach should take the power 2.5 and offer the step toggle');
free.integerOnly = true;
try {
  $('ap-' + free.id).click(); await sleep(100);
  if (L.S.n !== 3) fail('switching to a whole-power approach should round 2.5 to 3, n is ' + L.S.n);
  if ($('pow').step !== '1' || $('powStep') || $('powWhole').hidden) fail('the power dial should move in whole numbers and say why');
  type('powNum', '3.4');
  if (L.S.n !== 3) fail('a typed 3.4 should become 3, n is ' + L.S.n);
  type('powNum', '-2');
  if (L.S.n !== -2) fail('whole negative powers should still be accepted');
} finally { delete free.integerOnly; }
$('ap-bulb').click(); await sleep(100);
if ($('pow').step !== '0.1' || !$('powStep') || !$('powWhole').hidden) fail('leaving the whole-power approach should give the dial its freedom back');
type('powNum', '2.5');
if (L.S.n !== 2.5) fail('after leaving, 2.5 should be accepted again');
const own = L.APPROACHES.filter(a => a.integerOnly).map(a => a.id);
return 'whole powers: tried on ' + free.id + '; approaches of this page that are whole-power by themselves: ' + (own.join(', ') || 'none');
""", '19-whole-powers')

# 21 reset everything
step(r"""
$('mode-j').click(); type('cyNum', '0.3'); $('qFine').click(); L.cam.yaw += 1; L.touch(); $('flat').click();
if (typeof L.setExtreme === 'function') { $('extreme').click(); type('iterNum', '900'); }
$('resetAll').click(); await sleep(300);
const S = L.S;
if (S.mode !== 'm' || !$('mode-m').checked || S.flat || S.extreme || S.approach !== 0) fail('Reset everything left mode, 2D view, extreme ranges or approach changed');
if (S.n !== 2 || S.iter !== 14 || S.c.join() !== '-1,0,0' || S.eq !== 'z^n + c' || S.cutOn || S.mosaic) fail('Reset everything left the equation, c, the cut or the mosaic changed');
if (S.q.aa !== 12 || !$('qBal').classList.contains('is-on')) fail('Reset everything left the quality changed');
const view = camNow(); L.resetCam();
if (camNow() !== view) fail('Reset everything left the camera at ' + view + ', the starting view is ' + camNow());
if ($('juliaPanel').hidden === false || $('mandelPanel').hidden) fail('the panels do not show Mandelbrot mode');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'reset everything: back to the opening state';
""", '20-reset-everything')

# 22 the two new panels; a 256 x 256 picture job
step(r"""
window.smokeFiles = []; window.squaringLabSaveHook = (name, blob) => { window.smokeFiles.push({ name, size: blob.size, type: blob.type }); };
if (!$('exportPanel').firstElementChild || !$('meshPanel').firstElementChild) fail('a new panel is empty');
if (typeof L.exportBusy !== 'function') return 'picture job skipped: the picture module (45-export.js) is not part of this page';
__EXPORT_START__
""", wait='!window.squaringLab.exportBusy || !window.squaringLab.exportBusy()', timeout=300)
# (tools/shot.py runs a step's js first and its wait afterwards, so the wait for the job belongs to the step that starts it)
step(r"""
if (typeof L.exportBusy !== 'function') return 'picture job skipped';
__EXPORT_SAVE__
""", wait=None)

# 23 a 48-cell model job
step(r"""
if (typeof L.meshBusy !== 'function' || !$('meshStart')) return 'model job skipped: the 3D model module (46-mesh.js) is not part of this page';
// without the renderer's sampleSlice the module's own test field stands in for the picture
window.squaringLabMeshTest = typeof L.sampleSlice === 'function' ? { cells: 48 } : { cells: 48, field: 'sphere' };
$('mode-j').click(); await sleep(100);
$('meshStart').click(); await sleep(200);
return 'model job started' + (window.squaringLabMeshTest.field ? ' on the built-in test sphere (the renderer of this page cannot sample the picture)' : ' on the Julia set for c = -1');
""", wait='!window.squaringLab.meshBusy || !window.squaringLab.meshBusy()', timeout=420)
step(r"""
if (typeof L.meshBusy !== 'function' || !$('meshStart')) return 'model job skipped';
const before = window.smokeFiles.length;
if (!shown('meshSave')) fail('the model job did not end with a file to save: ' + ($('meshMsg') ? $('meshMsg').textContent : ''));
$('meshSave').click(); await sleep(500);
const f = window.smokeFiles[before];
if (!f) fail('Save the file did not hand over a file');
if (!/\.zip$/.test(f.name) || f.size < 1000) fail('the model file is not a zip of a sensible size: ' + JSON.stringify(f));
delete window.squaringLabMeshTest; $('mode-m').click();
return 'model job delivered ' + f.name + ', ' + f.size + ' bytes';
""", '21-after-jobs')

# a trap that is the solid, in the Mandelbrot picture. The probes say where the picture has something in it:
# they must hit, and not in the same places as the plain set.
step(r"""
if (L.S.mode !== 'm' || L.S.flat || L.S.colour.solid !== 0) fail('unexpected state before the trap solid test');
window.smokeProbe = { m0: probes() };
if (shown('col-thick') || shown('col-skip')) fail('the trap thickness and skip dials should wait until the trap is a solid');
pick('col-solid', 'Is the solid');
if (L.S.colour.solid !== 1 || !shown('col-thick') || !shown('col-skip')) fail('Is the solid did not set the state or show its two dials');
return 'Mandelbrot, the trap is the solid; the plain set was hit by ' + hits(window.smokeProbe.m0) + ' of 49 probes';
""", '21b-trap-solid-m')
step(r"""
const now = probes(), was = window.smokeProbe.m0;
if (hits(now) < 3) fail('with the trap as the solid the Mandelbrot picture is empty: ' + hits(now) + ' of 49 probes hit');
if (now === was) fail('with the trap as the solid the Mandelbrot picture shows the same solid as before');
pick('col-solid', 'Colours the surface'); $('mode-k').click();
return 'trap solid in the Mandelbrot picture: ' + hits(now) + ' of 49 probes hit (' + hits(was) + ' on the plain set)';
""")
step(r"""
window.smokeProbe.k0 = probes();
pick('col-solid', 'Is the solid');
if (L.S.colour.solid !== 1 || !shown('col-thick')) fail('Is the solid is not offered in the Kleinian view');
return 'Kleinian, the trap is the solid; the plain set was hit by ' + hits(window.smokeProbe.k0) + ' of 49 probes';
""", '21c-trap-solid-k')
step(r"""
const now = probes(), was = window.smokeProbe.k0;
if (hits(now) < 3) fail('with the trap as the solid the Kleinian picture is empty: ' + hits(now) + ' of 49 probes hit');
if (now === was) fail('with the trap as the solid the Kleinian picture shows the same solid as before');
// an inside colouring in the 2D view
pick('col-solid', 'Colours the surface'); $('mode-m').click(); $('flat').click(); await sleep(150);
if (!shown('col-edge') || !shown('col-edgeGlow') || !shown('col-inMode') || shown('col-solid')) fail('the 2D view should show the outline, glow and inside controls, and put the trap solid choice away');
if (shown('col-inPal')) fail('the palette for the inside should wait until the inside is coloured');
pick('col-inMode', 'How quickly the orbit settles'); await sleep(100);
if (!L.S.colour.inMode || !shown('col-inPal')) fail('the inside colouring did not switch on');
pick('col-inPal', 'Fire'); await sleep(100);
if (!(L.S.colour.inPal >= 0) || !shown('col-inRev')) fail('a palette of its own for the inside should offer its own reverse box');
return 'trap solid in the Kleinian picture: ' + hits(now) + ' of 49 probes hit (' + hits(was) + ' on the plain set); 2D view with the inside coloured by how quickly the orbit settles';
""", '21d-inside-2d')
# the picture itself: a small picture job of that 2D view, and the colours at places inside the set
step(r"""
if (shown('exportDiscard')) { $('exportDiscard').click(); await sleep(150); }   // the picture of the earlier job is still held
__EXPORT_START__
""", wait='!window.squaringLab.exportBusy || !window.squaringLab.exportBusy()', timeout=300)
step(r"""
const v = { x: L.S.v2.x, y: L.S.v2.y, h: L.S.v2.h };
__EXPORT_BLOB__
const cv = document.createElement('canvas'); cv.width = bm.width; cv.height = bm.height;
const g = cv.getContext('2d'); g.drawImage(bm, 0, 0);
const at = (x, y) => [...g.getImageData(Math.round(bm.width / 2 + (x - v.x) * bm.height / v.h), Math.round(bm.height / 2 - (y - v.y) * bm.height / v.h), 1, 1).data.slice(0, 3)];
// middles of the heart-shaped body, the round bulb, the top bulb, and places between them: all inside the set
const cols = [[0, 0], [-1, 0], [-0.1226, 0.7449], [-0.4, 0.3], [0.2, -0.3], [-0.6, 0], [-1.15, 0.1]].map(p => at(p[0], p[1]));
const far = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) > 24;
const kinds = cols.reduce((list, c) => (list.some(k => !far(k, c)) ? list : list.concat([c])), []);
if (kinds.length < 3) fail('the inside of the 2D picture is (nearly) one colour, the inside colouring does not draw: ' + JSON.stringify(cols));
$('exportDiscard').click(); $('flat').click(); document.querySelector('#colReset .dial-reset').click();
if (L.S.colour.inMode !== 0 || L.S.flat) fail('the colour reset or the 2D switch left the inside colouring on');
return 'inside colouring drawn: ' + kinds.length + ' clearly different colours at 7 places inside the set';
""")

# "Show Figure 4" from as far away as the page can be: Kleinian, 2D view, a cut, a modifier, a trap solid, a
# sweeping Lift dial. Every control must show the new state.
step(r"""
$('ap-mercator').click(); type('par-mercator-turnNum', '30');
$('ap-fold').click(); type('par-fold-planesNum', '5'); type('par-fold-liftNum', '0.4'); $('par-fold-liftPlay').click();
$('ap-classic').click(); $('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absx').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
L.S.view.zmax = 3; L.S.view.bound = 1.5; L.syncControls(); L.viewChanged();   // a far zoom limit and a drawing radius that would not let the solid fit
await sleep(200);
$('fig4Show').click(); await sleep(400);
const S = L.S, p = S.param.fold, bad = [];
if (S.mode !== 'j' || !$('mode-j').checked) bad.push('the mode');
if (S.flat || $('flat').checked) bad.push('the 2D view');
if (S.c.join() !== '-1,0,0' || [$('cxNum').value, $('cyNum').value, $('czNum').value].join() !== '-1,0,0') bad.push('the c dials at ' + [$('cxNum').value, $('cyNum').value, $('czNum').value]);
if (apId() !== 'fold' || !$('ap-fold').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'fold') bad.push('the approach, which is ' + apId() + ' and should be Sphere inversions, two planes');
if (p.planes !== 2 || $('par-fold-planesNum').value !== '2') bad.push('the planes at ' + $('par-fold-planesNum').value);
if (p.lift !== 0 || $('par-fold-liftNum').value !== '0') bad.push('the lift at ' + p.lift);
if (S.param.mercator.turn !== 30) bad.push('the Turn dial of the one-plane entry, which is not this button\'s to move');
if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absx').checked || S.colour.solid !== 0) bad.push('the equation, the cut, a modifier or the trap solid');
if (chosen('juliaPreset') !== 'Basilica') bad.push('the Julia list at ' + chosen('juliaPreset'));
if ($('juliaPanel').hidden || !$('kleinPanel').hidden || $('secApproach').hidden) bad.push('the panels');
await sleep(900);
if (L.S.param.fold.lift !== 0) bad.push('the Lift sweep, still running');
if (Math.abs(L.cam.dist - 4.8) > 0.05 || L.S.view.zmax < L.cam.dist || L.S.view.bound < 2) bad.push('the framing: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + L.S.view.zmax + ', drawing radius ' + L.S.view.bound);
if (bad.length) fail('Show Figure 4 did not set: ' + bad.join('; '));
const r = $('stage').getBoundingClientRect();
if (r.bottom <= 0 || r.top >= innerHeight) fail('after Show Figure 4 the picture is out of view');
return 'Show Figure 4 from the Kleinian 2D view with the classic Mandelbulb chosen and Planes at 5: Julia, c = (-1, 0, 0), power 2, the entry Sphere inversions, two planes with Planes 2 and Lift 0, framed';
""", '21e-figure-4')
step(r"""
const two = probes(), whole = grid();
if (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');
if (whole[1] > 4) fail('the picture of Figure 4 is not whole in the frame: ' + whole[1] + ' probes hit on the outer ring');
const view = camNow(), dials = JSON.stringify(L.S.param);
$('fig4Back').click(); await sleep(300);
if (apId() !== 'mercator' || !$('ap-mercator').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'mercator') fail('Back to one plane should choose Sphere inversions, one plane, the approach is ' + apId());
if (JSON.stringify(L.S.param) !== dials) fail('Back to one plane moved a dial: ' + JSON.stringify(L.S.param));
if ($('par-mercator-turn').closest('.dial').hidden) fail('the one-plane entry should show its Turn dial');
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the approach');
return 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane chose Sphere inversions, one plane and nothing else';
""", '21f-one-plane')
# ... and "Back to one plane" from the Kleinian view with another approach chosen; then the opening state again
step(r"""
type('par-fold-planesNum', '3'); $('ap-tilt').click(); $('mode-k').click(); await sleep(150);
$('fig4Back').click(); await sleep(300);
if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');
if (apId() !== 'mercator' || !$('ap-mercator').checked || L.S.param.fold.planes !== 3) fail('Back to one plane should show Sphere inversions, one plane and leave the Planes dial of the other entry alone');
// ... and Show Figure 4 a second time, from the Mandelbrot solid of the twisted quaternion square
$('ap-tilt').click(); $('mode-m').click(); await sleep(150);
$('fig4Show').click(); await sleep(300);
if (apId() !== 'fold' || L.S.mode !== 'j' || L.S.param.fold.planes !== 2 || L.S.c.join() !== '-1,0,0' || !$('ap-fold').checked) fail('Show Figure 4 from the twisted quaternion square did not land on Sphere inversions, two planes with Planes at 2');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.param.fold.planes !== 2 || L.S.param.mercator.turn !== 0 || L.S.colour.solid !== 0) fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'Back to one plane also works from the Kleinian view and another approach; Show Figure 4 also from the twisted quaternion square';
""")

# the mirror twins: each button shows the Mandelbrot solid of one approach with "flip z" ticked, from any state
TWIN_CHECK = r"""
const twinState = (btn, id) => {
  const S = L.S, bad = [];
  if (S.mode !== 'm' || !$('mode-m').checked) bad.push('the mode');
  if (S.flat || $('flat').checked) bad.push('the 2D view');
  if (L.APPROACHES[S.approach].id !== id || !$('ap-' + id).checked) bad.push('the approach');
  if (S.flip.join() !== '0,1' || !$('flipz').checked || $('flipy').checked) bad.push('flip z');
  if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
  if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absy').checked || S.colour.solid !== 0 || S.mosaic) bad.push('the equation, the cut, a modifier, the mosaic or the trap solid');
  const p = S.param.mercator;
  if (id === 'mercator' && (p.turn !== 0 || p.lift !== 0 || $('par-mercator-turnNum').value !== '0' || $('par-mercator-liftNum').value !== '0')) bad.push('the dials of Sphere inversions, one plane');
  if ($('mandelPanel').hidden || !$('juliaPanel').hidden || !$('kleinPanel').hidden) bad.push('the panels');
  if (bad.length) fail(btn + ' did not set: ' + bad.join('; '));
  const r = $('stage').getBoundingClientRect();
  if (r.bottom <= 0 || r.top >= innerHeight) fail('after ' + btn + ' the picture is out of view');
};
const twinPicture = name => { const h = hits(probes()), g = grid(); if (h < 5) fail('the picture of the twin of ' + name + ' is empty: ' + h + ' of 49 probes hit'); if (g[1] > 8) fail('the twin of ' + name + ' is not whole in the frame: ' + g[1] + ' probes hit on the outer ring'); return h; };
"""
step(TWIN_CHECK + r"""
type('par-mercator-turnNum', '25'); type('par-mercator-liftNum', '0.4');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
L.S.view.zmax = 3; L.syncControls(); L.viewChanged();   // a far zoom limit that would not let the solid fit
await sleep(200);
$('twinMerc').click(); await sleep(400);
twinState('Twin of Sphere inversions', 'mercator');
if (L.cam.dist < 5.5 || L.S.view.zmax < L.cam.dist) fail('the twin button did not stand back for the whole solid: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + L.S.view.zmax);
return 'Twin of Sphere inversions from the Kleinian 2D view: Mandelbrot, power 2, the one-plane entry with Turn 0 and Lift 0, flip z ticked';
""", '21g-twin-inversions')
step(TWIN_CHECK + r"""
const h = twinPicture('Sphere inversions');
$('m-mosaic').click(); await sleep(150);
$('twinLathe').click(); await sleep(400);
twinState('Twin of the Lathe', 'lathe');
return 'twin of Sphere inversions drawn (' + h + ' of 49 probes hit); Twin of the Lathe from the mosaic';
""", '21h-twin-lathe')
step(TWIN_CHECK + r"""
const h = twinPicture('the Lathe');
$('twinBulb').click(); await sleep(400);
twinState('Twin of the Mandelbulb', 'bulb');
return 'twin of the Lathe drawn (' + h + ' of 49 probes hit); Twin of the Mandelbulb';
""", '21i-twin-bulb')
step(TWIN_CHECK + r"""
const h = twinPicture('the Mandelbulb'), view = camNow();
$('twinOff').click(); await sleep(300);
if (L.S.flip.join() !== '0,0' || $('flipz').checked) fail('Back to the plain rule left flip z on');
if (L.S.mode !== 'm' || L.APPROACHES[L.S.approach].id !== 'bulb' || camNow() !== view) fail('Back to the plain rule changed more than flip z');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.flip.join() !== '0,0') fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'twin of the Mandelbulb drawn (' + h + ' of 49 probes hit); Back to the plain rule unticked flip z and nothing else';
""")

# The two buttons beside the quaternion answer: each shows the plain Mandelbrot solid of one entry (the quaternion
# square with Spin 1, the twisted one with its Tilt at the starting value) and frames the whole solid, from any state.
QUAT_CHECK = r"""
const quatState = (btn, id) => {
  const S = L.S, bad = [], a = L.APPROACHES.find(x => x.id === id);
  if (!a) fail('the list has no entry ' + id);
  if (S.mode !== 'm' || !$('mode-m').checked) bad.push('the mode');
  if (S.flat || $('flat').checked) bad.push('the 2D view');
  if (apId() !== id || !$('ap-' + id).checked || document.querySelector('#rules .rule.is-on').dataset.ap !== id) bad.push('the approach, which is ' + apId());
  if (S.flip.join() !== '0,0' || $('flipz').checked || $('flipy').checked) bad.push('flip y or flip z');
  if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
  if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absy').checked || S.colour.solid !== 0 || S.mosaic) bad.push('the equation, the cut, a modifier, the mosaic or the trap solid');
  for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined && (S.param[id][s.key] !== s.def || $('par-' + id + '-' + s.key + 'Num').value !== String(s.def))) bad.push('the dial ' + s.label + ', at ' + S.param[id][s.key]);
  if ($('mandelPanel').hidden || !$('juliaPanel').hidden || !$('kleinPanel').hidden) bad.push('the panels');
  if (S.view.zmax < L.cam.dist || S.view.bound < 3) bad.push('the room for the whole solid: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + S.view.zmax + ', drawing radius ' + S.view.bound);
  if (bad.length) fail(btn + ' did not set: ' + bad.join('; '));
  const r = $('stage').getBoundingClientRect();
  if (r.bottom <= 0 || r.top >= innerHeight) fail('after ' + btn + ' the picture is out of view');
};
const quatPicture = name => { const g = grid(); if (g[0] < 8) fail('the picture of ' + name + ' is (nearly) empty: ' + g[0] + ' of 165 probes hit'); if (g[1] > 4) fail(name + ' is not whole in the frame: ' + g[1] + ' probes hit on the outer ring'); return g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring'; };
"""
step(QUAT_CHECK + r"""
if (typeof L.showQuaternionSquare !== 'function' || typeof L.showTwistedSquare !== 'function') fail('window.squaringLab lacks showQuaternionSquare or showTwistedSquare');
if ($('quatShow').textContent !== 'Show the quaternion square' || $('tiltShow').textContent !== 'Show the twisted quaternion square') fail('the two buttons do not carry their names');
const answer = $('quatShow').closest('.row-btns').previousElementSibling;
let h = answer; while (h && h.tagName !== 'H3') h = h.previousElementSibling;
if (!h || h.textContent !== 'Is there a quaternion rule that works everywhere in space?' || $('tiltShow').parentNode !== $('quatShow').parentNode) fail('the two buttons should stand together beside the answer on the quaternion rule');
type('par-tilt-tiltNum', '-120'); type('par-lathe-spinNum', '3');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); $('flipz').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
L.S.view.zmax = 3; L.S.view.bound = 1.5; L.syncControls(); L.viewChanged();   // a far zoom limit and a drawing radius that would not let the solid fit
await sleep(200);
$('tiltShow').click(); await sleep(400);
quatState('Show the twisted quaternion square', 'tilt');
if (L.S.param.lathe.spin !== 3) fail('Show the twisted quaternion square moved a dial of another entry');
return 'Show the twisted quaternion square from the Kleinian 2D view with Tilt at −120: Mandelbrot, power 2, Tilt 40, no flip, room made for the solid';
""", '21k-twisted-square')
step(QUAT_CHECK + r"""
const was = quatPicture('the twisted quaternion square');
$('m-mosaic').click(); await sleep(150);
$('mode-j').click(); $('ap-bulb').click(); $('flipz').click(); await sleep(150);
$('quatShow').click(); await sleep(400);
quatState('Show the quaternion square', 'lathe');
if (L.S.param.tilt.tilt !== 40) fail('Show the quaternion square moved a dial of another entry');
return 'twisted quaternion square drawn (' + was + '); Show the quaternion square from the Julia set of the Mandelbulb with Spin at 3 and flip z ticked: Mandelbrot, power 2, Spin 1, no flip';
""", '21l-quaternion-square')
step(QUAT_CHECK + r"""
const was = quatPicture('the quaternion square');
// the same two by their names on window.squaringLab, from Figure 4
$('fig4Show').click(); await sleep(300);
L.showTwistedSquare(); await sleep(300);
quatState('showTwistedSquare()', 'tilt');
$('fig4Show').click(); await sleep(300);
L.showQuaternionSquare(); await sleep(300);
quatState('showQuaternionSquare()', 'lathe');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.param.tilt.tilt !== 40 || L.S.param.lathe.spin !== 1 || L.S.flip.join() !== '0,0') fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'quaternion square drawn (' + was + '); showTwistedSquare() and showQuaternionSquare() do the same from Figure 4';
""")

# The trap solid examples (the list "Examples" under "In the 3D view the trap"). Each sets what it says: the kind
# of picture, the Julia point or the Kleinian starting group, the trap shape, what the trap does, thickness,
# skipped steps and radius, and a camera that shows the object whole. Nothing else. The picture must not be empty.
# The skipped steps are compared with the page's own table (L.EXAMPLES), because the three Mandelbrot values will
# change when the colour module changes what the count means (EXAMPLE_SKIP_M in src/js/75-presets.js).
EXAMPLES = [
    # name, mode, trap shape as its list reads, what the trap does, radius, c (Julia) or None
    ('Spiky coral', 'm', 'Cross', 'Is the solid', '1', None),
    ('Discs and arches', 'm', 'Planes', 'Is the solid', '1', None),
    ('Rings around the set', 'm', 'Ring', 'Is added to the solid', '1', None),
    ('Chain of bubbles', 'j', 'Sphere shell', 'Is the solid', '0.7', '-1,0,0'),
    ('Sea urchins', 'j', 'Cross', 'Is the solid', '1', '-1,0,0'),
    ('Arches and hoops', 'j', 'Planes', 'Is the solid', '1', '-0.122561,0.744862,0'),
    ('Pearls and balls', 'k', 'Sphere shell', 'Is added to the solid', '1', None),
    ('Rings in the lace', 'k', 'Ring', 'Is the solid', '1', None),
    ('Discs under the set', 'k', 'Planes', 'Is added to the solid', '1', None),
]
EX_CHECK = r"""
const exSet = (i, name, mode, trap, does, radius, c) => {
  const S = L.S, e = L.EXAMPLES[i], bad = [];
  if (!e || e.name !== name) fail('example ' + (i + 1) + ' should be ' + name);
  pick('trapExamples', name);
  if (chosen('trapExamples') !== name) bad.push('the Examples list, which reads ' + chosen('trapExamples'));
  if (S.mode !== mode || !$('mode-' + mode).checked) bad.push('the kind of picture');
  if (!chosen('col-trap').startsWith(trap)) bad.push('the trap shape, at ' + chosen('col-trap'));
  if (chosen('col-solid') !== does) bad.push('what the trap does, at ' + chosen('col-solid'));
  if ($('col-thickNum').value !== '0.05' || $('col-radiusNum').value !== radius) bad.push('thickness or radius, at ' + [$('col-thickNum').value, $('col-radiusNum').value]);
  if (S.colour.skip !== e.skip || $('col-skipNum').value !== String(e.skip)) bad.push('the skipped steps, at ' + $('col-skipNum').value);
  if (c && (S.c.join() !== c || [$('cxNum').value, $('cyNum').value, $('czNum').value].join() !== c)) bad.push('the Julia point, at ' + S.c);
  if (mode === 'k' && chosen('kleinPreset') !== L.KLEIN_PRESETS[0].name) bad.push('the Kleinian group, at ' + chosen('kleinPreset'));
  if (bad.length) fail(name + ' did not set: ' + bad.join('; '));
  // nothing else: iterations, depth of the search, approach, power, quality and the colouring are the user's
  if (S.iter !== 17 || S.k.iter !== 90 || S.approach !== 0 || S.n !== 2 || S.q.aa !== 2 || S.colour.mode !== 0 || S.colour.pal !== window.smokePal) fail(name + ' changed more than it says: ' + JSON.stringify([S.iter, S.k.iter, S.approach, S.n, S.q.aa, S.colour.mode, S.colour.pal]));
};
const exPicture = name => { const g = grid(); if (g[0] < 5) fail('the picture of ' + name + ' is empty: ' + g[0] + ' of 165 probes hit'); if (g[1] > 4) fail(name + ' is not whole in the frame: ' + g[1] + ' probes hit on the outer ring'); return name + ' drawn (' + g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring)'; };
"""
for i, (name, mode, trap, does, radius, c) in enumerate(EXAMPLES):
    call = "exSet(%d, %s, %s, %s, %s, %s, %s);" % (i, json.dumps(name), json.dumps(mode), json.dumps(trap), json.dumps(does), json.dumps(radius), json.dumps(c))
    if i == 0:
        step(EX_CHECK + r"""
if (L.S.mode !== 'm' || L.S.flat || L.S.colour.solid !== 0) fail('unexpected state before the examples');
if (chosen('trapExamples') !== 'Choose one to try' || !shown('trapExamples')) fail('before an example is chosen the list should be on show and read Choose one to try, it reads ' + chosen('trapExamples'));
L.S.iter = 17; L.S.k.iter = 90; L.S.q.aa = 2; window.smokePal = L.S.colour.pal; L.syncControls();
""" + call + "\nreturn 'example 1 chosen: " + name + "';", '21j-example-1')
    else:
        prev = EXAMPLES[i - 1][0]
        step(EX_CHECK + "const was = exPicture(%s);\n" % json.dumps(prev) + call + "\nreturn was + '; example %d chosen: %s';" % (i + 1, name),
             '21j-example-%d' % (i + 1) if i in (3, 6) else None)
step(EX_CHECK + r"""
const was = exPicture('Discs under the set'), view = camNow();
type('col-thickNum', '0.08'); await sleep(150);
if (chosen('trapExamples') !== 'Choose one to try') fail('with a dial moved off the example the list should read Choose one to try, it reads ' + chosen('trapExamples'));
if (camNow() !== view) fail('moving a trap dial moved the camera');
$('flat').click(); await sleep(150);
if (shown('trapExamples')) fail('the Examples list belongs to the 3D view and should be put away in the 2D view');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.colour.solid !== 0 || L.S.flat || chosen('trapExamples') !== 'Choose one to try') fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return was + '; the list reads Choose one to try once a dial is moved, and is put away in the 2D view';
""")

# 24 collapse all, also for the sections of the other modes
step(r"""
const secs = () => [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden);
const b = $('collapseAll'), box0 = b.getBoundingClientRect();
b.click(); await sleep(200);
if (secs().some(d => d.open)) fail('Collapse all left a section open');
if (b.textContent !== 'Expand all') fail('the button should now read Expand all, it reads ' + b.textContent);
const box1 = b.getBoundingClientRect();
if (Math.abs(box0.left - box1.left) > 0.5 || Math.abs(box0.width - box1.width) > 0.5) fail('the button moved or changed size when its label changed');
$('mode-j').click(); await sleep(100);
if (secs().some(d => d.open)) fail('after Collapse all, switching to Julia showed an open section');
$('mode-m').click(); await sleep(100);
if (getComputedStyle($('toprow')).position !== 'sticky') fail('the top row should stay in reach while the column scrolls');
return secs().length + ' sections collapsed: ' + secs().map(d => d.querySelector('summary').textContent).join(', ');
""", '22-collapsed', clip=None, wait=None)

# 25 expand all
step(r"""
const secs = () => [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden);
const b = $('collapseAll');
b.click(); await sleep(200);
if (secs().some(d => !d.open)) fail('Expand all left a section closed');
if (b.textContent !== 'Collapse all') fail('the button should read Collapse all again');
return 'expanded again';
""", '23-expanded', clip=None)

# The picture job. These pieces go by what a viewer sees (the button texts "Start the picture" and "Save the
# file", the size choice with typed width and height) and fall back to the size the panel has when they cannot
# find the typed size. EXPORT_BLOB leaves the saved picture in `bm` (an ImageBitmap) and its file in `f`.
EXPORT_START = r"""const panel = $('exportPanel'), start = [...panel.querySelectorAll('button')].find(b => /^start/i.test(b.textContent.trim()));
if (!start) fail('the picture panel has no Start button');
let sized = false;
const sel = [...panel.querySelectorAll('select')].find(s => [...s.options].some(o => /typed|own size|custom/i.test(o.text)));
if (sel) {
  const o = [...sel.options].find(x => /typed|own size|custom/i.test(x.text));
  sel.value = o.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100);
  const box = word => { const d = [...panel.querySelectorAll('.dial')].find(e => !e.hidden && e.querySelector('label') && new RegExp(word, 'i').test(e.querySelector('label').textContent)); return d && d.querySelector('input.num'); };
  const w = box('width'), h = box('height');
  if (w && h) { for (const e of [w, h]) { e.value = '256'; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); } sized = true; }
}
window.smokeSized = sized;
start.click(); await sleep(300);
return 'picture job started' + (sized ? ' at 256 x 256' : ' at the size the panel had (no typed width and height were found)');"""
EXPORT_BLOB = r"""const panel = $('exportPanel'), save = [...panel.querySelectorAll('button')].find(b => /^save/i.test(b.textContent.trim()) && b.getBoundingClientRect().width > 0);
if (!save) fail('the picture job did not end with a Save the file button');
const before = window.smokeFiles.length, hook = window.squaringLabSaveHook; let blob = null;
window.squaringLabSaveHook = (name, b) => { blob = b; hook(name, b); };
save.click(); await sleep(800);
window.squaringLabSaveHook = hook;
const f = window.smokeFiles[before];
if (!f || !blob) fail('Save the file did not hand over a picture');
const bm = await createImageBitmap(blob);
if (window.smokeSized && (bm.width !== 256 || bm.height !== 256)) fail('asked for 256 x 256, got ' + bm.width + ' x ' + bm.height);"""
EXPORT_SAVE = EXPORT_BLOB + r"""
return 'picture job delivered ' + f.name + ', ' + bm.width + ' x ' + bm.height + ', ' + f.size + ' bytes';"""
for a in steps:
    a['js'] = a['js'].replace('__EXPORT_START__', EXPORT_START).replace('__EXPORT_SAVE__', EXPORT_SAVE).replace('__EXPORT_BLOB__', EXPORT_BLOB)

path = os.path.join(ROOT, 'out', 'r12', 'page', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke-v12.json')
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(steps, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('%d steps -> %s' % (len(steps), os.path.relpath(path, ROOT)))
