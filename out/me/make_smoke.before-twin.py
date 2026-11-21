"""Write tools/smoke.json (the page's smoke test) from the steps below.

  python out/r4/page/make_smoke.py            -> tools/smoke.json, screenshots to out/smoke-*.png
  python out/r4/page/make_smoke.py --mine     -> out/r5/page/smoke-mine.json, screenshots to out/r5/page/smoke/

Each step throws on a wrong state, so a failure shows as "page script failed" with the reason.
Write tools/smoke.json only from a version that has passed as --mine: other people run that file too.
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MINE = '--mine' in sys.argv
SHOTS = 'out/r5/page/smoke/' if MINE else 'out/'

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
L.R.warmOn = false; L.S.q.aa = 3; L.touch();
return 'default; sections: ' + order;
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
if ($('par-mercator-planes').max !== '8') fail('the planes dial should go to 8');
for (const id of ['par-mercator-liftPlay', 'par-mercator-turnPlay', 'par-bulb-latPlay', 'par-bulb-lonPlay', 'par-classic-thetaPlay', 'par-classic-phiPlay', 'col-shiftPlay']) if (!$(id)) fail('no play button ' + id);
const foot = document.querySelector('footer.why').textContent;
for (const t of ['Inversions added together can', 'the count is a free choice', 'the solid pulses from its poles', 'Questions from testing, answered', 'What does a list entry change?', 'Do quaternions or the third map have a part in this?',
  'The version you tested had Planes at 2', 'not a published theorem', 'as the Lathe approach', 'limited to c ∈ R', 'is an open problem', 'This works in Mandelbrot, Julia and Kleinian pictures',
  'The slices were in the colouring, not in the shape', 'the Kleinian view never had it', 'the first real test of saving a file from the published page is yours', 'Preparing the formula']) if (!foot.includes(t)) fail('the closing text lacks: ' + t);
if (document.querySelector('[data-needs]') || document.querySelector('footer.why [hidden]')) fail('a closing text is still held back');
// every control the closing text names must be on the page under that very label
const names = new Set([...document.querySelectorAll('.dials label, .dials button, .dials option, .dials optgroup, .dials summary, .dials .rule .name, footer.why button')].map(e => (e.label || e.textContent).replace(/\s+/g, ' ').trim()));
const has = t => names.has(t) || [...names].some(n => n.startsWith(t + ' ') || n.startsWith(t + ','));
for (const t of ['Planes', 'Use the third map', 'In the 3D view the trap', 'Colours the surface', 'Is the solid', 'Is added to the solid', 'Trap thickness', 'Trap shape', 'Orbit steps skipped at the start',
  '2D view', 'Outline width, pixels', 'Glow beside the outline, pixels', 'Inside the set, colour by', 'Plain', 'Orbit trap', 'Where the orbit ends up', 'How deep inside', 'How quickly the orbit settles', 'Palette for the inside',
  'Colour the cut face like the inside of the 2D view', 'Glow width', 'Balanced', 'Colour by', 'Sphere shell', 'How near it came, as a glow', 'Rainbow', 'Depth of the search', 'Extreme ranges', 'Iterations', 'Ray steps, at most', 'Refining passes', 'Power n',
  'Frame it', 'As it was found', 'Found with two planes', 'Turning-out sphere', 'Save a picture', 'Start the picture', 'Size', 'Quality', 'File type', 'Save the file', 'Save a 3D model', 'Start the model', 'Show Figure 4', 'Back to one plane', 'Lathe', 'Sphere inversions', 'Colour and light', 'Kleinian group']) {
  if (!has(t)) fail('the closing text names a control that the page does not have under that label: ' + t);
  if (!foot.includes(t)) fail('the closing text no longer names: ' + t);
}
if (!$('par-mercator-note1').textContent.includes('For the look of Figure 4') || !$('par-mercator-note2').textContent.includes('whole only while c is on the x-axis')) fail('the notes under the planes dial do not point to each other');
const all = document.body.textContent;
for (const t of ['cannot be built from inversions', 'rebuilt by eye', 'the bounded piece that is left', 'sampling its derivative', 'pole phase']) if (all.includes(t)) fail('an old wording is still on the page: ' + t);
if (!document.querySelector('.lede').textContent.includes('the ordinary 2D Mandelbrot or Julia set')) fail('the lede does not say what the flat set is');
if (!!$('powStep') === !!L.APPROACHES[L.S.approach].integerOnly) fail('the power dial has a step toggle exactly when the approach takes any power');
if ($('iterStep')) fail('the iterations dial must not have a step toggle');
return document.querySelectorAll('.dial').length + ' dials, ' + document.querySelectorAll('select').length + ' selects, ' + document.querySelectorAll('.dial-reset').length + ' reset buttons; every closing text is on show and names its controls by their labels';
""", '6-page', clip=None, wait=None)

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
type('par-mercator-planesNum', '2');
if (!$('par-mercator-turn').closest('.dial').hidden) fail('the turn dial should be hidden with two planes');
type('par-mercator-planesNum', '1');
if ($('par-mercator-turn').closest('.dial').hidden) fail('the turn dial did not appear with one plane');
type('par-mercator-turnNum', '40'); type('par-mercator-liftNum', '0.3');
const p = L.S.param.mercator;
if (p.planes !== 1 || p.turn !== 40 || p.lift !== 0.3) fail('approach parameters not set: ' + JSON.stringify(p));
if (!$('f-mercator').textContent.includes('40')) fail('the formula text did not follow the turn dial');
return JSON.stringify(p);
""", '11-approach-params')

# 13 Approach reset, then a trap choice
step(r"""
document.querySelector('#approachReset .dial-reset').click();
const p = L.S.param.mercator, planes0 = L.APPROACHES.find(a => a.id === 'mercator').params.find(s => s.key === 'planes').def;
if (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');
if (p.planes !== planes0 || p.turn !== 0 || p.lift !== 0) fail('the Approach reset left ' + JSON.stringify(p));
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
const view = camNow(), planes = L.S.param.mercator.planes;
pick('juliaPreset', 'Douady rabbit');
const c = L.S.c;
if (Math.abs(c[0] + 0.122561) > 1e-9 || Math.abs(c[1] - 0.744862) > 1e-9) fail('the Julia entry did not set c: ' + c);
if (camNow() !== view) fail('a Julia entry moved the camera');
if (L.S.iter !== 17) fail('a Julia entry changed the iterations to ' + L.S.iter);
if (L.S.param.mercator.planes !== planes) fail('a Julia entry changed the planes dial');
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
return (sel.options.length - 1) + ' Julia points in a drop-down; an entry leaves camera, iterations and planes alone; Frame it moves only the camera; saving also works with storage blocked';
""", '15-julia-preset')

# "As it was found": the planes and iterations an entry records, nothing else, and only while they differ
step(r"""
if (L.APPROACHES[L.S.approach].id !== 'mercator' || L.S.param.mercator.planes !== 1 || L.S.iter !== 17) fail('unexpected state before the test: ' + [L.S.approach, L.S.param.mercator.planes, L.S.iter]);
if (!shown('juliaFound')) fail('the rabbit records 24 iterations and the page has 17: As it was found should be on show');
const view = camNow(), c = L.S.c.join();
$('juliaFound').focus(); $('juliaFound').click(); await sleep(150);
if (L.S.iter !== 24 || $('iterNum').value !== '24' || L.S.param.mercator.planes !== 1) fail('As it was found should set 24 iterations and leave one plane: ' + [L.S.iter, L.S.param.mercator.planes]);
if (camNow() !== view || L.S.c.join() !== c) fail('As it was found changed the camera or c');
if (shown('juliaFound')) fail('As it was found should go when nothing differs any more');
if (document.activeElement === document.body) fail('focus was lost when the button went');
pick('juliaPreset', 'Cracked Basilica'); await sleep(150);
if ($('juliaPreset').selectedOptions[0].parentNode.label !== 'Found with two planes') fail('Cracked Basilica is not under Found with two planes');
if (!shown('juliaFound') || !$('juliaFound').title.includes('Planes to 2')) fail('an entry found with two planes should offer As it was found while Planes is 1: ' + $('juliaFound').title);
$('juliaFound').click(); await sleep(150);
if (L.S.param.mercator.planes !== 2 || $('par-mercator-planesNum').value !== '2' || L.S.iter !== 24) fail('As it was found should set Planes to 2 and nothing else');
if (shown('juliaFound')) fail('the button should go once the planes are as recorded');
$('ap-lathe').click(); type('par-mercator-planesNum', '1'); await sleep(150);
if (shown('juliaFound')) fail('under another approach the planes do not count, so the button should stay away');
$('ap-mercator').click(); await sleep(150);
if (!shown('juliaFound')) fail('back under Sphere inversions with one plane the button should return');
$('juliaFound').click(); await sleep(150);
return 'As it was found: 24 iterations for the rabbit, Planes 2 for Cracked Basilica, camera and c untouched, hidden when nothing differs';
""", '15b-as-it-was-found')

# back to where the following steps expect the page: one plane, 17 iterations, the rabbit
step(r"""
type('par-mercator-planesNum', '1'); type('iterNum', '17'); pick('juliaPreset', 'Douady rabbit');
return 'one plane and 17 iterations again';
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
$('ap-mercator').click(); type('par-mercator-liftNum', '0.4'); $('par-mercator-liftPlay').click();
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absx').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
await sleep(200);
$('fig4Show').click(); await sleep(400);
const S = L.S, p = S.param.mercator, bad = [];
if (S.mode !== 'j' || !$('mode-j').checked) bad.push('the mode');
if (S.flat || $('flat').checked) bad.push('the 2D view');
if (S.c.join() !== '-1,0,0' || [$('cxNum').value, $('cyNum').value, $('czNum').value].join() !== '-1,0,0') bad.push('the c dials at ' + [$('cxNum').value, $('cyNum').value, $('czNum').value]);
if (L.APPROACHES[S.approach].id !== 'mercator' || !$('ap-mercator').checked) bad.push('the approach');
if (p.planes !== 2 || $('par-mercator-planesNum').value !== '2') bad.push('the planes at ' + $('par-mercator-planesNum').value);
if (p.turn !== 0 || p.lift !== 0 || $('par-mercator-liftNum').value !== '0') bad.push('turn or lift at ' + [p.turn, p.lift]);
if (!$('par-mercator-turn').closest('.dial').hidden || $('par-mercator-note2').hidden) bad.push('the planes panel (Turn should be away, the note on the earlier version on show)');
if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absx').checked || S.colour.solid !== 0) bad.push('the equation, the cut, a modifier or the trap solid');
if (chosen('juliaPreset') !== 'Basilica') bad.push('the Julia list at ' + chosen('juliaPreset'));
if ($('juliaPanel').hidden || !$('kleinPanel').hidden || $('secApproach').hidden) bad.push('the panels');
await sleep(900);
if (L.S.param.mercator.lift !== 0) bad.push('the Lift sweep, still running');
if (bad.length) fail('Show Figure 4 did not set: ' + bad.join('; '));
const r = $('stage').getBoundingClientRect();
if (r.bottom <= 0 || r.top >= innerHeight) fail('after Show Figure 4 the picture is out of view');
return 'Show Figure 4 from the Kleinian 2D view: Julia, c = (-1, 0, 0), power 2, Sphere inversions with 2 planes, turn 0, lift 0, framed';
""", '21e-figure-4')
step(r"""
const two = probes();
if (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');
const view = camNow();
$('fig4Back').click(); await sleep(300);
const p = L.S.param.mercator;
if (p.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('Back to one plane left the planes at ' + p.planes);
if ($('par-mercator-turn').closest('.dial').hidden || $('par-mercator-note1').hidden) fail('with one plane the Turn dial and the one-plane note should be on show');
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the planes');
return 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane set the planes dial to 1 and nothing else';
""", '21f-one-plane')
# ... and "Back to one plane" from the Kleinian view with another approach chosen; then the opening state again
step(r"""
type('par-mercator-planesNum', '3'); $('ap-lathe').click(); $('mode-k').click(); await sleep(150);
$('fig4Back').click(); await sleep(300);
if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');
if (L.APPROACHES[L.S.approach].id !== 'mercator' || !$('ap-mercator').checked || L.S.param.mercator.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('Back to one plane should show Sphere inversions with Planes at 1');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.param.mercator.planes !== 1 || L.S.colour.solid !== 0) fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'Back to one plane also works from the Kleinian view and another approach';
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

path = os.path.join(ROOT, 'out', 'r5', 'page', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke.json')
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(steps, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('%d steps -> %s' % (len(steps), os.path.relpath(path, ROOT)))
