// Odds and ends a reader will try: Both in 3D and turning it, a c lifted off the flat plane, zooming a flat
// picture at a late step to find the bite, the one-step buttons, the reset, leaving Learn and coming back.
//@ sleep=1.2 shot=out/r26/checkb/NAME-01-3d-both-00.png
await openLearn(); await pickShape(); $('learnShapeAgain').click(); kindBar('both'); spaceBar(3); await frame();
return { ...said(), hint: $('learnHint').textContent };
//@ sleep=1.0 shot=out/r26/checkb/NAME-02-3d-both-03.png
$('learnShapeTicks').children[3].click(); await frame(); return said();
//@ sleep=0.5 shot=out/r26/checkb/NAME-03-3d-both-03.35.png
$('learnShapePos').value = 3.35; $('learnShapePos').dispatchEvent(new Event('input', { bubbles: true })); await frame(); return said();
//@ sleep=1.0 shot=out/r26/checkb/NAME-04-3d-both-08.png
$('learnShapeTicks').children[8].click(); await frame(); return said();
//@ sleep=1.0 shot=out/r26/checkb/NAME-05-3d-both-08-turned.png
// a drag in the right picture: do both turn?
const cv = $('learnShapeCanvas'), v0 = L.shape.state().view3;
ptr(cv, 'pointerdown', 650, 250);
for (let i = 1; i <= 15; i++) { ptr(cv, 'pointermove', 650 + 10 * i, 250 + 4 * i); await frame(); }
ptr(cv, 'pointerup', 800, 310); await frame();
// and a try at dragging the diamond of the left picture, as the flat page allows
const s = L.shape.state(), d = s.diamonds[0], c0 = s.c.slice(), v1 = s.view3;
ptr(cv, 'pointerdown', d[0], d[1]); for (let i = 1; i <= 6; i++) { ptr(cv, 'pointermove', d[0] + 5 * i, d[1]); await frame(); } ptr(cv, 'pointerup', d[0] + 30, d[1]);
const s2 = L.shape.state();
return { view0: v0, viewAfterDrag: v1, cBefore: c0, cAfterTryingToDragTheDiamond: s2.c, viewAfterThat: s2.view3, hint: $('learnHint').textContent };
//@ sleep=1.0 shot=out/r26/checkb/NAME-06-3d-j-c-lifted.png
// the Julia shape with c lifted off the flat plane by its z dial (set as the dial would)
$('learnShapeViewReset').click(); kindBar('j'); L.shape.set({ c: [-0.4, 0.3, 0.8] }); $('learnShapeTicks').children[5].click(); await frame();
return { ...said(), notice: $('learnShapeNotice').textContent, dials: [...document.querySelectorAll('#learnShapeDials input[type=number]')].map(i => i.value) };
//@ sleep=0.6 shot=out/r26/checkb/NAME-07-2d-m-12.3.png
// the flat Mandelbrot shape late in the play: is there anything to see at step 13?
L.shape.set({ c: [-0.4, 0.3, 0] }); kindBar('m'); spaceBar(2); await sleep(200);
$('learnShapePos').value = 12.3; $('learnShapePos').dispatchEvent(new Event('input', { bubbles: true })); await frame(); return said();
//@ sleep=0.8 shot=out/r26/checkb/NAME-08-2d-m-12.3-zoomed.png
// ten notches of the wheel over the left tip of the shape
const st = $('stage'), P = L.shape.state().panes[0], sc = 0.21 * Math.min(P.w, P.h), x = P.x + P.w / 2 + (-1.4) * sc, y = P.y + P.h / 2;
for (let i = 0; i < 10; i++) { wheel(st, x, y, -100); await frame(); }
return { view2: L.shape.state().view2.m, reset: box('learnShapeViewReset'), hint: $('learnHint').textContent };
//@ sleep=0.8 shot=out/r26/checkb/NAME-09-2d-m-13-zoomed.png
$('learnShapeTicks').children[13].click(); await frame(); return said();
//@ sleep=0.8 shot=out/r26/checkb/NAME-10-2d-m-16-zoomed.png
$('learnShapeTicks').children[16].click(); await frame(); return said();
//@ sleep=0.3
// the one-step buttons, from step 3
$('learnShapeViewReset').click(); $('learnShapeTicks').children[3].click(); await sleep(200);
const t0 = performance.now(); $('learnShapeFwd').click(); await frame();
const a = said(); let ms = 0;
for (let i = 0; i < 200; i++) { await sleep(25); if ($('learnShapePlay').textContent === 'Play') { ms = Math.round(performance.now() - t0); break; } }
const b = said(); $('learnShapeBack').click(); await sleep(150); const c = said();
return { rightAfterForward: a, forwardTookMs: ms, thenStandsAt: b.slider, afterBack: c.slider, backDisabledAt0: (() => { $('learnShapeAgain').click(); return $('learnShapeBack').disabled && $('learnShapeAgain').disabled; })() };
//@ sleep=0.5 shot=out/r26/checkb/NAME-11-after-section-reset.png
// "Reset this section" and what comes back
kindBar('both'); spaceBar(3); await sleep(600); $('learnShapeTicks').children[6].click(); await sleep(300);
const btn = [...$('learnFollow').closest('details').querySelectorAll('button')].find(b => /reset this section/i.test(b.textContent));
btn.click(); await sleep(400);
return { follow: [...document.querySelectorAll('input[name=learnFollow]')].find(r => r.checked).value, summary: $('learnFollow').closest('details').querySelector('summary').textContent, shapeBarHidden: $('learnShapeBar').hidden, state: (s => ({ kind: s.kind, space: s.space, pos: s.pos, c: s.c, on: s.on }))(L.shape.state()) };
//@ sleep=0.6 shot=out/r26/checkb/NAME-12-second-time-in.png
// in again: no playing by itself the second time
$('learnFollowShape').click(); await sleep(500);
return { ...said(), state: (s => ({ kind: s.kind, space: s.space, pos: s.pos, playing: s.playing }))(L.shape.state()) };
//@ sleep=0.8 shot=out/r26/checkb/NAME-13-back-from-julia-tab.png
// leave Learn for the lab's Julia tab and come back
kindBar('j'); $('learnShapeTicks').children[5].click(); await sleep(200);
$('mode-j').click(); await sleep(700); const away = { learnBarHidden: $('learnShapeBar').hidden || $('learnShapeBar').getBoundingClientRect().height === 0 };
$('mode-l').click(); await sleep(600);
return { away, back: said(), state: (s => ({ kind: s.kind, space: s.space, pos: s.pos, follow: s.follow }))(L.shape.state()) };
