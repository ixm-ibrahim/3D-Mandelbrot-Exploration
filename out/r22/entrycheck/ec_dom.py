"""Round 22, entrycheck: the two entries driven through the page's own controls (typed numbers, the c dials, extreme
ranges, reset), odd equations and start values, fly mode, the Kleinian view and back.
  python out/r22/entrycheck/ec_dom.py -> dom.log, dom/*.png
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive

H = drive.HEAD + """
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const cardText = () => ($('card') ? $('card').innerText.replace(/\\s+/g, ' ').trim() : '');
const sig = () => grid()[2];
const pick = async id => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; L.resetCam(); go(); await settle(); await sleep(300); };
"""
steps = [drive.UP]
# 1. the three dials of Pulled plane, typed
steps.append(dict(js=H + """
await pick('pulledplane');
const out = [], s0 = sig(), P = S.param.pulledplane;
type('par-pulledplane-holdNum', 0.3); await settle();
out.push('hold typed 0.3 -> ' + P.hold + '; formula says "' + ($('f-pulledplane').textContent.match(/w = \\([^)]*\\)/) || ['?'])[0] + '"; picture ' + (sig() === s0 ? 'UNCHANGED' : 'changed'));
type('par-pulledplane-easeNum', 2); await settle(); out.push('ease typed 2 -> ' + P.ease);
type('par-pulledplane-easeNum', -1); await settle(); out.push('ease typed -1 -> ' + P.ease);
type('par-pulledplane-cpullNum', 100); await settle(); out.push('cpull typed 100 (ordinary range to 64) -> ' + P.cpull);
type('par-pulledplane-holdNum', 'abc'); await settle(); out.push('hold typed abc -> ' + P.hold);
const ex = document.querySelector('#extremeHost input[type=checkbox]');
if (ex && !ex.checked) { ex.click(); await sleep(300); }
out.push('extreme ranges: ' + (ex ? ex.checked : 'no box'));
type('par-pulledplane-cpullNum', 10000); type('par-pulledplane-holdNum', 100); await settle();
out.push('extreme: cpull ' + P.cpull + ', hold ' + P.hold + ', probes ' + grid()[0] + (L.R.failed ? ' PROGRAM FAILED' : ''));
S.c = [-0.122561, 0.744862, 0]; go(); await settle(); out.push('rabbit with those: probes ' + grid()[0]);
type('par-pulledplane-holdNum', 0); type('par-pulledplane-cpullNum', 0); type('par-pulledplane-easeNum', 0); await settle();
out.push('all three at 0: ' + JSON.stringify(P) + ', probes ' + grid()[0] + (L.R.failed ? ' PROGRAM FAILED' : ''));
if (ex && ex.checked) { ex.click(); await sleep(300); }
out.push('extreme off: ' + JSON.stringify(P));
const rs = [...document.querySelectorAll('#secApproach button')].find(b => /reset this section/i.test(b.textContent));
if (rs) { rs.click(); await sleep(300); await settle(); out.push('Reset this section -> ' + JSON.stringify(P) + ', entry ' + apId() + ', eq ' + S.eq); } else out.push('no "Reset this section" button found in the Approach section');
S.c = [-1, 0, 0]; Object.assign(P, { hold: 0.05, ease: 0.7, cpull: 16 }); go(); await settle();
out.push('back at the start: picture ' + (sig() === s0 ? 'the same as at first' : 'DIFFERENT from the first'));
return out.join(' | ');
""", wait='done', timeout=600, shot='out/r22/entrycheck/dom/1-dials.png'))
# 2. the c dials, typed: the card of Pulled plane follows; what Along once does
steps.append(dict(js=H + """
const out = [];
for (const id of ['pulledplane', 'alongonce', 'turnalong']) {
  await pick(id);
  const c0 = cardText(), n0 = L.cardRun.cache.size;
  type('cyNum', 0.5); await settle(); await sleep(500);
  const c1 = cardText(), n1 = L.cardRun.cache.size;
  go(); await settle(); await sleep(500);
  const c2 = cardText();
  type('czNum', 0.25); await settle(); await sleep(500);
  const c3 = cardText(), n3 = L.cardRun.cache.size;
  go(); await settle(); await sleep(500);
  const c4 = cardText();
  out.push(id + ': c typed to ' + JSON.stringify(S.c) + '; card after c along y = 0.5 ' + (c1 === c0 ? 'unchanged' : 'changed') + (c1 === c2 ? '' : ' BUT NOT what a fresh measurement shows') + '; after c along z = 0.25 ' + (c3 === c1 ? 'unchanged' : 'changed') + (c3 === c4 ? '' : ' BUT NOT what a fresh measurement shows') + '; remembered measurements ' + n0 + ' -> ' + n1 + ' -> ' + n3 + '; slice line: ' + ((c4.match(/Slice[^.]*\\.[^.]*\\./i) || [''])[0]).slice(0, 160));
}
return out.join(' | ');
""", wait='done', timeout=600, shot='out/r22/entrycheck/dom/2-cdials.png'))
# 3. odd equations and start values
steps.append(dict(js=H + """
const out = [];
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id);
  for (const [what, f] of [
    ['(z + 1)^2 + c, Julia c = -0.5', () => { S.eq = '(z + 1)^2 + c'; S.c = [-0.5, 0, 0]; }],
    ['conj(z)^2 + c, Julia c = -0.5', () => { S.eq = 'conj(z)^2 + c'; S.c = [-0.5, 0, 0]; }],
    ['z^2 + c*z, Julia c = 0.5', () => { S.eq = 'z^2 + c*z'; S.c = [0.5, 0, 0]; }],
    ['c*z*(1 - z), Mandelbrot from 0.5', () => { S.eq = 'c*z*(1 - z)'; S.mode = 'm'; S.z0 = '0.5'; }],
    ['z^2 + c, Mandelbrot from c^2', () => { S.eq = 'z^n + c'; S.mode = 'm'; S.z0 = 'c^2'; }],
    ['z^n + c, n = 2, Mandelbrot, fly mode', () => { S.eq = 'z^n + c'; S.z0 = '0'; S.mode = 'm'; S.view.fly = true; }],
  ]) {
    try { f(); L.resetCam(); go(); await settle(); out.push(id + ' ' + what + ': ' + grid()[0] + ' probes' + (L.R.failed ? ' PROGRAM FAILED ' + L.R.failed : '')); }
    catch (e) { out.push(id + ' ' + what + ': FAILED ' + e.message); }
  }
  S.view.fly = false; S.eq = 'z^n + c'; S.z0 = '0'; S.mode = 'j'; S.c = [-1, 0, 0]; L.resetCam(); go(); await settle();
  const s0 = sig();
  $('mode-k').click(); await sleep(300); await settle();
  $('mode-j').click(); await sleep(300); await settle();
  out.push(id + ' Kleinian view and back: entry ' + apId() + ', picture ' + (sig() === s0 ? 'the same' : 'DIFFERENT'));
}
return out.join(' | ');
""", wait='done', timeout=600, shot='out/r22/entrycheck/dom/3-odd.png'))
os.makedirs(os.path.join(HERE, 'dom'), exist_ok=True)
code, text, vals = drive.shot(drive.PAGE, steps, 'dom-steps', '1400x950')
drive.write('dom.log', text + 'exit %d\n' % code)
print(text[-7000:]); print('exit', code)
sys.exit(code)
