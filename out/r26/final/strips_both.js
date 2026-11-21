// The final look: the screenshots picture c for the user is made of: Both in 2D for the rabbit at steps 0, 2, 5, 16.
// Each is the stage of the real page (clip #stage) at 1400x950, where the two pictures stand side by side.
//@
await openShape();
kindBar('both'); spaceBar(2); await sleep(300);
const b = [...document.querySelectorAll('#learnShapeCs button')].find(x => /x −0\.12, y 0\.74/.test(x.textContent)); if (!b) fail('no button for the rabbit');
b.click(); await sleep(500); scrollTo(0, 0); await sleep(200);
return { window: [innerWidth, innerHeight], stage: box('stage'), c: L.shape.state().c, button: b.textContent.trim() };
//@ repeat=4 sleep=0.45 shot=out/r26/final/strip/c-2d-both-##.png clip=#stage
const K = [0, 2, 5, 16][__I__]; tick(K); await sleep(400);
const s = L.shape.state(); return { k: K, ...page(), c: s.c, quality: s.quality, panes: s.panes, diamonds: s.diamonds };
