// Check 1: Follow = One point is what it was. The same steps are run on the frozen page (base18a) and on the test
// page, and the pictures of the stage and of the transport are compared pixel for pixel (compare.py).
//@
$('mode-l').click(); await sleep(400);
if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on');
const s = L.state();
return { space: s.space, z: s.z, c: s.c, moves: s.moves, sentence: s.sentence, follow: L.follow };
//@ sleep=0.3 shot=out/r26/core/NAME-1-stage.png clip=#stage
//@ shot=out/r26/core/NAME-1-bar.png clip=#learnBar
//@
const s = L.goto(1, 0.5);
return { move: s.move, t: s.t, sentence: s.sentence, point: s.point };
//@ sleep=0.3 shot=out/r26/core/NAME-2-stage.png clip=#stage
//@ shot=out/r26/core/NAME-2-bar.png clip=#learnBar
//@
$('learnSpace3').click(); await sleep(300);
const s = L.goto(0, 0.6);
return { space: s.space, moves: s.moves, sentence: s.sentence, point: s.point, note: s.note };
//@ sleep=0.3 shot=out/r26/core/NAME-3-stage.png clip=#stage
//@ shot=out/r26/core/NAME-3-bar.png clip=#learnBar
//@
$('learnNext').click(); await sleep(300);
const s = L.goto(1, 0.25);
return { step: s.step, playing: s.playing, sentence: s.sentence, orbit: s.orbit };
//@ sleep=0.3 shot=out/r26/core/NAME-4-stage.png clip=#stage
//@ shot=out/r26/core/NAME-4-bar.png clip=#learnBar
//@
$('learnSpace1').click(); await sleep(300);
const s = L.goto(0, 0.5);
return { space: s.space, hidden: s.hidden, sentence: s.sentence, point: s.point };
//@ sleep=0.3 shot=out/r26/core/NAME-5-stage.png clip=#stage
//@ shot=out/r26/core/NAME-5-bar.png clip=#learnBar
//@
$('learnSpace2').click(); await sleep(300);
const s = L.set({ show: 'all', hidden: true, z: [0.5, -0.6, 0], c: [0.2, 0.4, 0] }); L.goto(0, 0.7);
const t = L.state();
return { space: t.space, show: t.show, hidden: t.hidden, sentence: t.sentence, point: t.point };
//@ sleep=0.3 shot=out/r26/core/NAME-6-stage.png clip=#stage
//@ shot=out/r26/core/NAME-6-bar.png clip=#learnBar
//@
// a wheel over the stage zooms the one-point picture, and "Reset view" comes up
$('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -400, bubbles: true, cancelable: true, clientX: 300, clientY: 400 })); await sleep(200);
const z = L.view.h2.zoom, shownReset = shown('learnViewReset');
return { zoom: z, shownReset, hint: $('learnHint').textContent };
//@ sleep=0.3 shot=out/r26/core/NAME-7-stage.png clip=#stage
//@
// the panel's own reset, then Reset everything
document.querySelector('#learnReset button').click(); await sleep(300);
const a = L.state();
$('resetAll').click(); await sleep(500);
return { afterPanelReset: { space: a.space, z0: a.z0, c: a.c, show: a.show, on: a.on, follow: L.follow }, afterResetAll: { on: L.on, isLearn: document.body.classList.contains('is-learn'), mode: S.mode } };
//@ wait=done timeout=110
return 'done';
