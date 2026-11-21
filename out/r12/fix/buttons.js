//pre  Fixer of round 12: the buttons and words of the page, tried from the states the checkers named.
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(150); for (let i = 0; i < 600 && !L.idle(); i++) await sleep(100); };
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const camNow = () => [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => x.toFixed(4)).join();
const apId = () => L.APPROACHES[L.S.approach].id;
const where = () => 'approach ' + apId() + ', mode ' + L.S.mode + ', power ' + L.S.n + ', c ' + L.S.c.join() + ', cam ' + camNow();
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0, far = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const p = L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); if (p) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; const q = p.pos || p.p || p; if (q && q.length === 3) far = Math.max(far, Math.hypot(...q)); } } return { hit: n, onTheOuterRing: ring, farthestPickedPoint: +far.toFixed(3) }; };
//====
// W1: Back to one plane, from a Mandelbrot picture, from Figure 4 and from the Kleinian view
const out = {};
$('ap-bulb').click(); type('powNum', '3'); await settle();
let view = camNow(), dials = JSON.stringify(L.S.param); out.fromMandelbulb_before = where(); $('fig4Back').click(); await settle();
out.fromMandelbulb_after = where(); out.fromMandelbulb_cameraKept = camNow() === view; out.fromMandelbulb_dialsKept = JSON.stringify(L.S.param) === dials;
$('fig4Show').click(); await settle(); view = camNow(); out.fromFigure4_before = where(); $('fig4Back').click(); await settle(); out.fromFigure4_after = where(); out.fromFigure4_cameraKept = camNow() === view;
$('ap-lathe').click(); $('mode-k').click(); await settle(); view = camNow(); const k = JSON.stringify(L.S.k); out.fromKleinian_before = where(); $('fig4Back').click(); await settle();
out.fromKleinian_after = where(); out.fromKleinian_cameraKept = camNow() === view; out.fromKleinian_groupKept = JSON.stringify(L.S.k) === k; out.fromKleinian_radioOnEntry = $('ap-mercator').checked;
out.sentenceOnThePage = (document.querySelector('footer.why').textContent.match(/Back to one plane chooses[^.]*\.(?: From a[^.]*\. From the Kleinian[^.]*\.)?/) || [''])[0];
return JSON.stringify(out, null, 1);
//====
// W2: the words on As it was found
const f = $('juliaFound'), out = [], say = t => out.push(t + ' -> ' + (shown('juliaFound') ? 'button "' + f.textContent + '" (title: ' + f.title + ')' : 'button not on show'));
$('resetAll').click(); await sleep(200); $('mode-j').click(); await settle();
pick('juliaPreset', 'Cracked Basilica'); await settle(); say('one plane in use, Cracked Basilica');
f.click(); await settle(); out.push('after the click: ' + where() + ', Planes ' + L.S.param.fold.planes); say('then');
type('par-fold-planesNum', '4'); await settle(); say('two planes in use with Planes at 4, Cracked Basilica');
f.click(); await settle(); out.push('after the click: ' + where() + ', Planes ' + L.S.param.fold.planes); say('then');
type('par-fold-planesNum', '5'); type('iterNum', '14'); await settle(); say('two planes in use with Planes at 5 and 14 iterations, Cracked Basilica');
pick('juliaPreset', 'Douady rabbit'); await settle(); say('two planes in use, Douady rabbit');
$('ap-mercator').click(); await settle(); say('one plane in use, Douady rabbit, iterations ' + L.S.iter);
return out.join('\n');
//====
//shot tilt90
// M1: the picture of the twisted square with the Tilt at 90, from the button's own camera
const out = {};
$('resetAll').click(); await sleep(200); $('tiltShow').click(); await settle(); out.atTilt40 = { state: where(), view: grid(), drawingRadius: L.S.view.bound };
type('par-tilt-tiltNum', '90'); await settle(); out.atTilt90 = { tilt: L.S.param.tilt.tilt, view: grid() };
return JSON.stringify(out, null, 1);
//====
//shot tilt-90
const out = {}; type('par-tilt-tiltNum', '-90'); await settle(); out.atTiltMinus90 = { tilt: L.S.param.tilt.tilt, view: grid() };
return JSON.stringify(out, null, 1);
//====
// the words of the page: every sentence the defects name, read from the live page
const all = document.querySelector('.page').textContent, out = {};
const has = t => all.includes(t);
const A = id => L.APPROACHES.find(a => a.id === id), texts = a => [a.name, a.tag, a.about || '', ...(a.params || []).map(p => (p.text || '') + ' ' + (p.label || '') + ' ' + (p.help || '') + ' ' + (p.options || []).map(o => o[1]).join(' '))].join(' ');
const every = L.APPROACHES.map(texts).join(' ') + ' ' + all;
out.old = {}; for (const t of ['has no end', 'runs off along a band', 'as with every quaternion rule', 'no plane chosen and no seam', 'sheet with no thickness', 'changes nothing else', 'Twin of the Lathe', 'the Lathe’s mirror twin', 'turned against each other', 'cube roots', 'branch points', 'usual sphere coordinate', 'one closed formula', 'keeps every angle true', 'bodies of revolution', 'body of revolution', 'Smooth step', 'Smoother step', 'sin(4', 'A minus sign gives the mirror image.', 'the same product with its second factor twisted', 'For every approach here except', 'the one approach whose z = 0 slice', 'polynomial']) out.old[t] = every.includes(t);
out.buttons = [...document.querySelectorAll('footer.why .row-btns button')].map(b => b.textContent);
out.lede = document.querySelector('.lede').textContent.split('. ').slice(-1)[0];
out.dashes = (every.match(/—/g) || []).length;
return JSON.stringify(out, null, 1);
