// The final look: things the first lists left open.
//@ sleep=0.4 shot=out/r26/final/NAME-1-2d-m-12.4-zoomed.png clip=#stage
// (1) M1: a late step under way, zoomed in on the left rim of the shape: is the bite there to see again?
await openShape(); await slider(12.4); await sleep(200);
const st = $('stage'), b = st.getBoundingClientRect(), P = L.shape.state().panes[0];
const X = b.left + P.x + P.w / 2 - 0.21 * Math.min(P.w, P.h) * 0.75, Y = b.top + P.y + P.h / 2;
for (let i = 0; i < 8; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: X, clientY: Y, deltaY: -150, deltaMode: 0 })); await sleep(60); }
await sleep(500);
const s = L.shape.state(); return { ...page(), zoom: r2(s.view2.m.zoom), thin: s.thin, thickPx: s.thick[0].slice(8, 16) };
//@ sleep=0.5 shot=out/r26/final/NAME-2-3d-m-12.4-zoomed.png clip=#stage
// ... and the same in 3D (the wheel over the middle, to zoom 4.5 or so)
$('learnShapeViewReset').click(); await sleep(150); spaceBar(3); await sleep(1200); await slider(12.4); await rest(300);
const st = $('stage'), b = st.getBoundingClientRect();
for (let i = 0; i < 7; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -145, deltaMode: 0 })); await sleep(150); }
const s = await rest(900); return { ...page(), zoom: r2(s.view3.zoom), asked: lv(s.three.levels), thin: s.thin, quality: s.quality, cardMs: r2(s.ms.three) };
//@ sleep=0.5 shot=out/r26/final/NAME-3-3d-m-16-from-the-side.png clip=#stage
// (2) the pale patch with a straight edge on the top of the opening approach's shape at step 16: seen from another
// side (a scripted drag), at zoom 3. Does the patch stay on the same part of the body?
$('learnShapeViewReset').click(); await sleep(200); tick(16); await rest(300);
const st = $('stage'), b = st.getBoundingClientRect(), cv = $('learnShapeCanvas');
for (let i = 0; i < 5; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -150, deltaMode: 0 })); await sleep(150); }
const ev = (type, x, y) => cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: 6, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: b.left + x, clientY: b.top + y }));
ev('pointerdown', 300, 250); for (let i = 1; i <= 10; i++) { ev('pointermove', 300 + i * 14, 250 - i * 5); await frame(); } ev('pointerup', 440, 200);
const s = await rest(900); return { view: { yaw: r2(s.view3.yaw), pitch: r2(s.view3.pitch), zoom: r2(s.view3.zoom) } };
//@ sleep=0.5 shot=out/r26/final/NAME-4-3d-m-16-level.png clip=#stage
// ... and from level with the flat plane (pitch 0.05): how thick is the body?
const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect();
const ev = (type, x, y) => cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: 6, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: b.left + x, clientY: b.top + y }));
const p0 = L.shape.state().view3.pitch, dy = Math.round((0.05 - p0) / 0.01);
ev('pointerdown', 300, 250); for (let i = 1; i <= 10; i++) { ev('pointermove', 300, 250 + dy * i / 10); await frame(); } ev('pointerup', 300, 250 + dy);
const s = await rest(900); return { view: { yaw: r2(s.view3.yaw), pitch: r2(s.view3.pitch), zoom: r2(s.view3.zoom) } };
//@ sleep=0.5 shot=out/r26/final/NAME-5-quat4-w1.5-m-00.png clip=#stage
// (3) A2 once more: "Quaternions, 4D (slices)" with w = 1.5. The Mandelbrot shape at the start: the words say "the
// big ball", is the whole ball there? And the Julia shape after 1 step, which the page calls gone.
$('learnShapeViewReset').click(); await sleep(200);
const name = await approach('quat4'); S.param.quat4.w = 1.5; refresh(); kindBar('m'); await sleep(400); tick(0); const s = await rest(400);
const T3 = LAB.learnShape3d, c = s.c; let n = 0, m0 = 0, j1 = 0, j0 = 0;
for (let i = -16; i <= 16; i++) for (let j = -16; j <= 16; j++) for (let k = -16; k <= 16; k++) { if (i * i + j * j + k * k > 256) continue; const p = [i / 8, j / 8, k / 8]; n++; if (T3.out(p, 'm', p, 0) > 0) m0++; if (T3.out(p, 'j', c, 0) > 0) j0++; if (T3.out(p, 'j', c, 1) > 1) j1++; }
return { name, w: S.param.quat4.w, ...page(), gridPointsOfTheBall: n, mandelbrotInAtStart: m0, juliaInAtStart: j0, juliaLeftAfterStep1: j1, c, look: look3() };
//@ sleep=0.5 shot=out/r26/final/NAME-6-quat4-w1.5-j-01.png clip=#stage
kindBar('j'); await sleep(400); tick(1); await rest(400); return { ...page(), look: look3() };
//@ sleep=1.2 wait=done timeout=100 shot=out/r26/final/NAME-7-lab-solid-turnalong.png clip=#stage
// (4) M2: is the rough body of "Turning plane, along" the rule's own? The lab's own solid of the same rule
// (Mandelbrot tab, as the lab draws it), to hold beside the whole shape's step 16.
const a = LAB.APPROACHES.find(x => x.id === 'quat4'); for (const p of a.params || []) if (p.key !== undefined) S.param.quat4[p.key] = p.def; refresh();
await approach('turnalong'); $('mode-m').click(); await sleep(600);
return { mode: S.mode, approach: AP().name, dim: S.dim, iter: S.iter };
//@ sleep=1.2 wait=done timeout=100 shot=out/r26/final/NAME-8-lab-solid-fold.png clip=#stage
await approach('fold'); await sleep(400); return { approach: AP().name };
//@ sleep=0.6 shot=out/r26/final/NAME-9-shape-turnalong-12.png clip=#stage
// and the whole shape of the same rule at step 12 and 16, zoomed to 2
await approach('turnalong'); $('mode-l').click(); await sleep(600);
if (L.follow !== 'shape') { $('learnFollowShape').click(); await sleep(200); L.shape.pause(); }
L.shape.set({ kind: 'm', space: 3, pos: 12 }); await sleep(600);
const st = $('stage'), b = st.getBoundingClientRect();
for (let i = 0; i < 3; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -155, deltaMode: 0 })); await sleep(150); }
const s = await rest(900); return { zoom: r2(s.view3.zoom), ...page(), cardMs: r2(s.ms.three) };
//@ sleep=0.6 shot=out/r26/final/NAME-10-shape-turnalong-16.png clip=#stage
tick(16); const s = await rest(900); return { zoom: r2(s.view3.zoom), ...page(), cardMs: r2(s.ms.three) };
//@ sleep=0.4 shot=out/r26/final/NAME-11-after-learn-panel-reset.png
// (5) the Learn panel's own reset (the button inside #learnReset), pressed from inside the whole shape: Follow goes
// back to One point, and inside the whole shape: Mandelbrot shape, 2D, step 0, c as Learn opens
$('learnShapeViewReset').click(); await sleep(150); await approach('mercator');
L.shape.set({ on: true, kind: 'both', space: 3, c: [0.3, -0.6, 0.4], pos: 7 }); await rest(300);
const btn = $('learnReset').querySelector('button'); if (!btn) fail('no reset button in the Learn panel');
const shown = btn.offsetParent !== null, label = btn.textContent.trim();
btn.click(); await sleep(700);
const s = L.shape.state();
return { button: label, buttonShownInTheWholeShape: shown, learnOn: L.on, follow: L.follow, pointChecked: $('learnFollowPoint').checked, onePointSpace: L.state().space,
  wholeShapeInside: { kind: s.kind, space: s.space, pos: s.pos, c: s.c, view3: s.view3 }, stageShows: document.body.className };
