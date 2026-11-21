// The same in 3D, the reader's way: Learn, "A whole shape", Start again, the 3D switch under the picture, Play.
//@ sleep=0.4
await openLearn(); await pickShape(); await sleep(200);
$('learnShapeAgain').click(); await sleep(200);
return said();
//@ sleep=1.2 shot=out/r26/checkb/NAME-a-step0.png
window.__t3 = performance.now();
spaceBar(3);
await frame(); await frame();
return { ms: Math.round(performance.now() - window.__t3), ...said(), hint: $('learnHint') ? $('learnHint').textContent : null, again: $('learnShapeAgain').title, state: brief(L.shape.state()), approach: LAB.APPROACHES[S.approach].name };
//@
window.__t0 = performance.now();
$('learnShapePlay').click();
await frame();
return { clicked: true, ...said() };
//@ repeat=52 sleep=0.33 shot=out/r26/checkb/NAME-play-##.png
return { i: __I__, t: Math.round(performance.now() - window.__t0), ...said() };
//@ sleep=0.6 shot=out/r26/checkb/NAME-z-end.png
return { t: Math.round(performance.now() - window.__t0), ...said(), state: brief(L.shape.state()) };
