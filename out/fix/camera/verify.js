// Camera checks, run in the page by tools/shot.py (see notes/camera_steps.py). Needs the test boot (out/camera/boot-test.js).
const L = window.squaringLab, S = L.S, cam = L.cam, c = document.getElementById('view');
const $ = id => document.getElementById(id);
const rect = () => c.getBoundingClientRect();
const raf = () => new Promise(r => requestAnimationFrame(r));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { for (let i = 0; i < 300 && (L.CV.goal || L.CV.raf); i++) await raf(); await raf(); await raf(); };
const wheel = (dy, o = {}, el = c) => { const r = rect(); el.dispatchEvent(new WheelEvent('wheel', Object.assign({ deltaY: dy, bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }, o))); };
const ptr = (type, x, y, o = {}, el = c) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent(type, Object.assign({ pointerId: 1, pointerType: 'mouse', isPrimary: true, buttons: type === 'pointerup' ? 0 : 1, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y }, o))); };
const key = (type, code, k, o = {}, el = c) => el.dispatchEvent(new KeyboardEvent(type, Object.assign({ code, key: k === undefined ? code : k, bubbles: true, cancelable: true }, o)));
const type = (inp, text, how = 'Enter') => { inp.focus(); inp.value = text; inp.dispatchEvent(new Event('input', { bubbles: true })); if (how === 'blur') inp.dispatchEvent(new FocusEvent('blur')); else key('keydown', how, how, {}, inp); };
const near = (a, b, tol = 1e-6) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));
const sub = (a, b) => a.map((v, i) => v - b[i]), dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0), len = a => Math.sqrt(dot(a, a));
const out = [], ok = (name, cond, info) => out.push((cond ? 'PASS ' : 'FAIL ') + name + (info === undefined ? '' : '  [' + info + ']'));
const done = () => { const f = out.filter(s => s.startsWith('FAIL')); return [f.length ? 'FAILED ' + f.length + ' of ' + out.length : 'all ' + out.length + ' pass'].concat(out); };
const whole = (r, x, y) => { const X = Math.round(r.left + x), Y = Math.round(r.top + y); return { clientX: X, clientY: Y, px: X - r.left, py: Y - r.top }; };
const hold = async (code, ms) => { key('keydown', code); await sleep(ms); key('keyup', code); await settle(); };

const note = () => { const e = $('camNote'); return e && !e.hidden ? e.textContent : ''; };
const clickReal = id => $(id).dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, detail: 1 }));

//# name=frame-negative wait=done timeout=240
Object.assign(S.q, { res: 0.6, aa: 2 }); S.mode = 'm'; S.n = 2; L.resetCam(); L.refresh(false); await settle();
const rows = [];
for (const n of [-0.5, -1, -2, -3, -8, 2, 8]) { S.n = n; L.resetCam(); rows.push([n, +cam.dist.toFixed(3), cam.target.join(','), +S.v2.h.toFixed(3)]); }
ok('n = -2 starts as far back as the negative-power preset does (6.5), plus a little air', near(rows[2][1], 6.84, 1e-9) && near(rows[2][3], 4.378, 1e-3), JSON.stringify(rows[2]));
ok('nearer to 0 the start is further back, and it stops growing below |n| = 1', rows[0][1] === rows[1][1] && rows[1][1] > rows[2][1] && rows[2][1] > rows[3][1] && rows[3][1] > rows[4][1] && rows[4][1] > 4.8, JSON.stringify(rows.map(r => r[1])));
ok('positive powers start as before', rows[5][1] === 5.2 && rows[5][2] === '-0.6,0,0' && rows[6][1] === 4.8 && rows[6][2] === '0,0,0');
S.n = -3; L.resetCam(); L.refresh(false);
return done().concat([JSON.stringify(rows)]);

//# name=shot-n-3 wait=done timeout=240 shot=out/fix/camera/a1-n-3-reset.png clip=#stage
return 'n=-3 dist ' + cam.dist;

//# name=n-2 wait=done timeout=240
S.n = -2; L.resetCam(); L.refresh(false); return 'n=-2 dist ' + cam.dist;

//# name=shot-n-2 wait=done timeout=240 shot=out/fix/camera/a2-n-2-reset.png clip=#stage
return 'shot';

//# name=n-8 wait=done timeout=240
S.n = -8; L.resetCam(); L.refresh(false); return 'n=-8 dist ' + cam.dist;

//# name=shot-n-8 wait=done timeout=240 shot=out/fix/camera/a3-n-8-reset.png clip=#stage
return 'shot';

//# name=n-1 wait=done timeout=240
S.n = -1; L.resetCam(); L.refresh(false); return 'n=-1 dist ' + cam.dist;

//# name=shot-n-1 wait=done timeout=240 shot=out/fix/camera/a4-n-1-reset.png clip=#stage
return 'shot';

//# name=flat-n-2 wait=done timeout=240
S.n = -2; S.flat = true; L.resetCam(); L.refresh(false); return '2D n=-2 span ' + S.v2.h;

//# name=shot-2d wait=done timeout=240 shot=out/fix/camera/a5-n-2-flat.png clip=#stage
return 'shot';

//# name=bulb-n-3 wait=done timeout=240
S.flat = false; S.approach = L.APPROACHES.findIndex(a => a.id === 'bulb'); S.n = -3; L.resetCam(); L.refresh(false); return 'bulb n=-3 dist ' + cam.dist;

//# name=shot-bulb wait=done timeout=240 shot=out/fix/camera/a6-bulb-n-3-reset.png clip=#stage
return 'shot';

//# name=back wait=done timeout=240
S.approach = 0; S.n = 2; L.resetCam(); L.refresh(false); return 'back to n = 2';

//# name=limits-and-reset
S.flat = false; S.view.fly = false; S.mode = 'm'; S.n = 2; L.resetZoomLimits(); L.resetCam(); await settle();
type($('camNear'), '10'); await settle();
ok('near limit 10 pulls the camera out to 10', S.view.zmin === 10 && cam.dist === 10, cam.dist);
$('reset').click(); await settle(); await raf();
ok('Reset view holds the start distance to the near limit (code-2)', cam.dist === 10 && $('camVal').textContent === '10' && $('camThumb').style.top === '0%', cam.dist + ' ' + $('camVal').textContent + ' ' + $('camThumb').style.top);
L.resetZoomLimits(); L.resetCam(); await settle();
type($('camFar'), '4'); await settle();
$('reset').click(); await settle(); await raf();
ok('Reset view holds the start distance to a far limit of 4 (p8c-1)', cam.dist === 4 && $('camVal').textContent === '4', cam.dist);
const dBefore = cam.dist; wheel(100); await settle();
ok('scrolling out at the far limit never moves the camera in', cam.dist === dBefore, cam.dist);
ok('and a note says why nothing moved', note().startsWith('This is the farthest the zoom may go'), note());
S.mode = 'k'; L.resetCam(); ok('Kleinian start distance is held to the far limit too', cam.dist === 4, cam.dist);
L.resetCam({ eq: 'c*z*(1 - z)', target: [1, 0, 0], dist: 10 }); ok('and so is an equation preset', cam.dist === 4);
L.resetCam({ cam: { yaw: 0, pitch: 0, dist: 30 } }); ok('and a camera preset', cam.dist === 4);
S.mode = 'm'; L.resetCam();
// the View reset while the 2D view is up must also pull the 3D distance inside
S.flat = true; L.touch(); await raf(); await raf();
S.view.zmin = 20; S.view.zmax = 50; cam.dist = 30; L.resetZoomLimits(); await settle();
cam.dist = 100; L.resetZoomLimits(); await settle();
ok('limits reset in 2D: the 3D distance is held inside its own limits', cam.dist === 60, cam.dist);
S.flat = false; L.touch(); await raf(); await raf();
S.v2.h = 100; cam.dist = 0.001; L.resetZoomLimits(); await settle();
ok('limits reset in 3D: the camera eases inside and the 2D span is held', cam.dist === 0.005 && S.v2.h === 40, cam.dist + ' ' + S.v2.h);
L.resetZoomLimits(); L.resetCam(); L.touch();
return done();

//# name=fly-after-reset
S.flat = false; S.view.fly = false; S.mode = 'm'; S.n = 2; L.resetZoomLimits(); L.resetCam(); S.view.speed = 1; await settle();
cam.dist = 0.05; cam.target = [-0.75, 0.1, 0]; L.touch(); await raf();
$('camFly').click(); await raf(); await raf();
ok('entering fly close up sets a small speed', near(S.view.speed, 0.0125, 1e-12), S.view.speed);
clickReal('reset'); await raf(); await raf();
ok('Reset view while flying gives a speed that suits the start view (p7-2)', near(S.view.speed, 1.3, 1e-12) && cam.dist === 5.2 && S.view.fly === true, S.view.speed);
ok('and hands the keyboard to the picture (p7-1)', document.activeElement === c, document.activeElement && document.activeElement.id);
const p0 = L.basis().pos; await hold('KeyW', 500); const moved = len(sub(L.basis().pos, p0));
ok('W flies straight after Reset view', moved > 0.3, moved.toFixed(3));
$('zoomIn').focus(); clickReal('zoomIn'); ok('the plus button hands the keyboard over too', document.activeElement === c); await settle();
$('zoomOut').focus(); clickReal('zoomOut'); ok('and the minus button', document.activeElement === c); await settle();
$('reset').focus(); $('reset').click(); ok('pressed from the keyboard, Reset view keeps the focus', document.activeElement === $('reset'));
S.view.speed = 1; $('camArc').click(); await raf(); L.resetCam(); L.touch();
return done();

//# name=wheel-on-controls
S.flat = false; S.view.fly = false; L.resetZoomLimits(); L.resetCam(); await settle();
for (const id of ['zoomIn', 'zoomOut', 'reset', 'camFar', 'camNear', 'camArc', 'camFly', 'camRail']) {
  const el = $(id), b = el.getBoundingClientRect(), d = cam.dist;
  const ev = new WheelEvent('wheel', { deltaY: 100, bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2 });
  el.dispatchEvent(ev); await settle();
  ok('wheel over #' + id + ' zooms and does not scroll the page (p4-1)', ev.defaultPrevented && near(cam.dist / d, 1.12, 1e-9), ev.defaultPrevented + ' x' + (cam.dist / d).toFixed(4));
}
const ev2 = new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true }); c.dispatchEvent(ev2); await settle();
ok('wheel over the picture still zooms', ev2.defaultPrevented);
// 2D: over the picture the spot under the pointer holds; over a control the zoom is about the middle
S.flat = true; L.resetCam(); L.touch(); await raf(); await raf(); await settle();
const r = rect(), x0 = S.v2.x, y0 = S.v2.y, bb = $('zoomIn').getBoundingClientRect();
$('zoomIn').dispatchEvent(new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true, clientX: bb.left + 5, clientY: bb.top + 5 })); await settle();
ok('2D: wheel over a button zooms about the middle', S.v2.x === x0 && S.v2.y === y0 && near(S.v2.h, 2 * 0.32 * 5.2 / 1.12, 1e-9), S.v2.h);
wheel(-100, { clientX: Math.round(r.left + 100), clientY: Math.round(r.top + 100) }); await settle();
ok('2D: wheel over the picture holds the spot under the pointer', S.v2.x < x0 && S.v2.y > y0);
S.flat = false; L.resetCam(); L.touch(); await raf(); await raf();
let d = cam.dist; $('zoomIn').click(); await settle(); const fb = cam.dist / d;
d = cam.dist; key('keydown', 'Equal', '+'); await settle(); const fk = cam.dist / d;
ok('the plus key and the plus button take the same step (p4-2)', near(fb, 0.8, 1e-9) && near(fk, 0.8, 1e-9), fb + ' ' + fk);
d = cam.dist; key('keydown', 'Minus', '-'); await settle(); $('zoomOut').click(); await settle();
ok('and so do minus and its button', near(cam.dist / d, 1 / 0.64, 1e-9));
L.resetCam(); L.touch();
return done();

//# name=typed-limits
S.flat = false; S.view.fly = false; L.resetZoomLimits(); L.resetCam(); await settle();
const nb = $('camNear'), fb = $('camFar'), flagged = el => el.getAttribute('aria-invalid') === 'true';
type(nb, '2'); ok('near 2 is taken as typed, no flag', S.view.zmin === 2 && !flagged(nb) && note() === '', note());
type(fb, '1'); ok('far 1 with near 2 is refused: old value back, box flagged, note says why (p8c-2)', S.view.zmax === 60 && fb.value === '60' && flagged(fb) && note().includes('at least twice the nearest limit, so 4 or more here'), fb.value + ' | ' + note());
await sleep(950); type(fb, '3'); ok('far 3 likewise', S.view.zmax === 60 && flagged(fb));
type(nb, '20'); ok('near 20 fits under far 60', S.view.zmin === 20 && nb.value === '20');
await settle(); const dd = cam.dist;
await sleep(950); type(nb, '500'); await settle();
ok('near 500 with far 60 is refused and the camera is not carried away', S.view.zmin === 20 && nb.value === '20' && flagged(nb) && cam.dist === dd && note().includes('at most half the farthest limit, so 30 or less here'), nb.value + ' ' + cam.dist + ' | ' + note());
await sleep(950); type(fb, '5000'); ok('a far limit beyond the hard range is held to 1000, flagged, with the range named', S.view.zmax === 1000 && flagged(fb) && note() === 'The farthest limit is kept between 0.002 and 1000.', note());
await sleep(950); type(fb, 'abc'); ok('nonsense: flagged with a note', S.view.zmax === 1000 && flagged(fb) && note() === 'A zoom limit is a number above zero.', note());
ok('the box titles state the rule', nb.title.includes('At most half the farthest') && fb.title.includes('At least twice the nearest'), nb.title + ' | ' + fb.title);
L.resetZoomLimits(); L.resetCam(); await settle();
return done();

//# name=note-shot shot=out/fix/camera/b1-limit-note.png clip=#stage
S.flat = false; S.view.fly = false; L.resetZoomLimits(); L.resetCam(); L.touch(); await settle();
type($('camNear'), '2'); type($('camFar'), '1');
return [note()];

//# name=flat-reset-and-notes
S.flat = false; S.view.fly = false; S.mode = 'm'; S.n = 2; L.resetZoomLimits(); L.resetCam(); await settle();
cam.yaw = -1.72; cam.pitch = 0.87; cam.dist = 4.145; cam.target = [0.1, 0.2, 0.3]; L.touch(); await raf();
const was = JSON.stringify(cam);
S.flat = true; L.touch(); await raf(); await raf();
S.v2.x = 0.4; S.v2.y = -0.3; S.v2.h = 0.2; L.touch();
$('reset').click(); await raf(); await raf();
ok('Reset view in 2D re-centres the flat picture', S.v2.x === -0.6 && S.v2.y === 0 && near(S.v2.h, 3.328, 1e-9), JSON.stringify(S.v2));
ok('and leaves the 3D camera alone (p12-2)', JSON.stringify(cam) === was, JSON.stringify(cam));
S.v2.x = 0.4; S.v2.y = -0.3; S.v2.h = 0.2; S.flat = false; L.touch(); await raf(); await raf();
$('reset').click(); await raf();
ok('Reset view in 3D resets the camera and leaves the 2D pan and zoom alone', cam.dist === 5.2 && cam.yaw === -1 && S.v2.x === 0.4 && S.v2.h === 0.2, JSON.stringify(S.v2));
L.resetCam(); ok('resetCam() itself still puts both back', S.v2.x === -0.6 && near(S.v2.h, 3.328, 1e-9));
S.flat = true; L.touch(); await raf(); await raf();
const rail = $('camRail');
ok('2D wording says span, never height (text-18)', rail.title === 'Zoom: how tall a piece of the slice fits in the picture' && rail.getAttribute('aria-valuetext') === 'Span 3.33' && !/height/i.test($('camNear').title + $('camFar').title + rail.title), rail.getAttribute('aria-valuetext') + ' | ' + $('camNear').title + ' | ' + $('camFar').title);
for (let i = 0; i < 90; i++) wheel(-300); await settle();
ok('zooming in stops at 0.0005', S.v2.h === 0.0005, S.v2.h);
await sleep(100); wheel(-100); await settle();
ok('one more notch explains the stop (p12-4)', S.v2.h === 0.0005 && note().startsWith('This is the closest the zoom may go') && note().includes('0.0005'), note());
type($('camNear'), '0.000001');
ok('a limit under the hard range is held to 0.00001, flagged and explained', S.v2.hmin === 1e-5 && $('camNear').getAttribute('aria-invalid') === 'true' && note() === 'The closest zoom is kept between 0.00001 and 500.', note());
await sleep(950); type($('camNear'), '0.0001');
ok('a limit below the sharp range is taken, with a warning', S.v2.hmin === 1e-4 && $('camNear').getAttribute('aria-invalid') !== 'true' && note().includes('loses sharpness'), note());
L.resetZoomLimits(); await settle(); type($('camNear'), '0.0001'); wheel(-100); await settle();
ok('zooming past 0.0005 warns', S.v2.h < 0.0005 && note().includes('loses sharpness'), S.v2.h + ' ' + note());
S.flat = false; L.touch(); await raf(); await raf();
ok('the note goes when the view changes', note() === '');
L.resetZoomLimits(); L.resetCam(); L.touch();
return done();

//# name=ease-rate
S.flat = false; S.view.fly = false; L.resetZoomLimits(); L.resetCam(); L.touch(); await settle();
while (!L.idle()) await sleep(50);
const run = async (n, gap) => { L.resetCam(); await settle(); let worst = 0, last = cam.dist, t0 = performance.now(), sent = 0; const d0 = cam.dist;
  while (performance.now() - t0 < n * gap + 700) { if (sent < n && performance.now() - t0 >= sent * gap) { wheel(100); sent++; } await raf(); worst = Math.max(worst, cam.dist / last - 1); last = cam.dist; }
  return [worst, cam.dist / d0]; };
const one = await run(1, 60), five = await run(5, 60);
ok('one notch: no frame moves more than 3%', one[0] < 0.03 && near(one[1], 1.12, 1e-9), (one[0] * 100).toFixed(2) + '%');
ok('five quick notches: no frame moves more than 5% (perf-7)', five[0] < 0.05 && near(five[1], Math.pow(1.12, 5), 1e-9), (five[0] * 100).toFixed(2) + '%');
L.resetCam(); L.touch();
return done();
