// Mandelbrot shape against Julia shape against Both, on the 2D page, with the page's own controls; then the
// diamond dragged by a scripted pointer, and the named values of c.
//@ sleep=0.5 shot=out/r26/checkb/NAME-j-00.png
await openLearn(); await pickShape(); $('learnShapeAgain').click(); await sleep(150);
kindBar('j'); await frame();
return { ...said(), hint: $('learnHint').textContent, c: L.shape.state().c };
//@ sleep=0.5 shot=out/r26/checkb/NAME-j-01.png
$('learnShapeTicks').children[1].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-j-03.png
$('learnShapeTicks').children[3].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-j-16.png
$('learnShapeTicks').children[16].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-both-00.png
$('learnShapeAgain').click(); kindBar('both'); await frame(); return { ...said(), hint: $('learnHint').textContent };
//@ sleep=0.45 shot=out/r26/checkb/NAME-both-00.5.png
L.shape.goto(0.5); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-both-01.png
$('learnShapeTicks').children[1].click(); await frame(); return said();
//@ sleep=0.45 shot=out/r26/checkb/NAME-both-02.3.png
$('learnShapePos').value = 2.3; $('learnShapePos').dispatchEvent(new Event('input', { bubbles: true })); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-both-03.png
$('learnShapeTicks').children[3].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-both-08.png
$('learnShapeTicks').children[8].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-both-16.png
$('learnShapeTicks').children[16].click(); await frame(); return said();
//@ sleep=0.05 shot=out/r26/checkb/NAME-drag-1-held.png
// drag the diamond in the LEFT picture, at step 8, from where it stands to c = -1, 0 in twenty moves, timing each frame
$('learnShapeTicks').children[8].click(); await sleep(400);
const cv = $('learnShapeCanvas'), s = L.shape.state(), d = s.diamonds[0], P = s.panes[0];
const sc = 0.21 * Math.min(P.w, P.h), to = [P.x + P.w / 2 + (-1) * sc, P.y + P.h / 2];
window.__drag = { from: d, to, c0: s.c.slice() };
const dts = []; let last = performance.now();
ptr(cv, 'pointerdown', d[0], d[1]);
for (let i = 1; i <= 20; i++) { ptr(cv, 'pointermove', d[0] + (to[0] - d[0]) * i / 20, d[1] + (to[1] - d[1]) * i / 20); await frame(); const n = performance.now(); dts.push(r1(n - last)); last = n; }
return { from: d, to, frameMs: dts, cWhileHeld: [...LAB.learn.shape.state().c], cursor: cv.style.cursor };
//@ sleep=0.5 shot=out/r26/checkb/NAME-drag-2-released.png
const cv = $('learnShapeCanvas'); ptr(cv, 'pointerup', window.__drag.to[0], window.__drag.to[1]); await frame();
return { c: L.shape.state().c, ...said() };
//@ sleep=0.05 shot=out/r26/checkb/NAME-drag-3-outside-held.png
// on to a c outside the Mandelbrot shape of step 8: c = 0.6, 0.6
const cv = $('learnShapeCanvas'), s = L.shape.state(), d = s.diamonds[0], P = s.panes[0];
const sc = 0.21 * Math.min(P.w, P.h), to = [P.x + P.w / 2 + 0.6 * sc, P.y + P.h / 2 - 0.6 * sc];
window.__drag = { to };
ptr(cv, 'pointerdown', d[0], d[1]);
for (let i = 1; i <= 20; i++) { ptr(cv, 'pointermove', d[0] + (to[0] - d[0]) * i / 20, d[1] + (to[1] - d[1]) * i / 20); await frame(); }
return { cWhileHeld: [...L.shape.state().c] };
//@ sleep=0.5 shot=out/r26/checkb/NAME-drag-4-outside-released.png
const cv = $('learnShapeCanvas'); ptr(cv, 'pointerup', window.__drag.to[0], window.__drag.to[1]); await frame();
return { c: L.shape.state().c, ...said() };
//@ sleep=0.5 shot=out/r26/checkb/NAME-drag-5-right-picture.png
// the diamond in the RIGHT picture can be taken too: drag it there to c = -0.12, 0.74
const cv = $('learnShapeCanvas'), s = L.shape.state(), d = s.diamonds[1], P = s.panes[1];
const sc = 0.21 * Math.min(P.w, P.h), to = [P.x + P.w / 2 + (-0.12) * sc, P.y + P.h / 2 - 0.74 * sc];
ptr(cv, 'pointerdown', d[0], d[1]);
for (let i = 1; i <= 20; i++) { ptr(cv, 'pointermove', d[0] + (to[0] - d[0]) * i / 20, d[1] + (to[1] - d[1]) * i / 20); await frame(); }
ptr(cv, 'pointerup', to[0], to[1]); await frame();
return { c: L.shape.state().c, ...said() };
//@ repeat=4 sleep=0.6 shot=out/r26/checkb/NAME-named-##.png
// the four named values, by their buttons, in Both at step 16
const bs = [...document.querySelectorAll('#learnShapeCs button')];
if (__I__ === 0) $('learnShapeTicks').children[16].click();
const b = bs[1 + __I__]; b.scrollIntoView({ block: 'center' }); b.click(); await frame();
return { button: b.textContent, c: L.shape.state().c, ...said(), buttons: __I__ === 0 ? bs.map(x => x.textContent) : undefined };
//@ sleep=0.4 shot=out/r26/checkb/NAME-panel-lower.png
// the lower part of the panel, as it stands with Both
$('learnShapeNotice').scrollIntoView({ block: 'end' }); await frame();
return { notice: $('learnShapeNotice').textContent, dials: [...document.querySelectorAll('#learnShapeDials .label, #learnShapeDials label')].map(e => e.textContent.trim()).filter(Boolean) };
