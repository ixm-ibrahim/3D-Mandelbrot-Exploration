// The final look: the screenshots three of the four pictures for the user are made of (a, b, d: one picture on the
// stage). Each is the stage of the real page (clip #stage), resting on a whole step chosen with the tick under the
// slider. Run at 1100x1000, where the stage is nearly square. make_strips.py puts them together.
// (strips_both.js takes the screenshots of picture c.)
//@
await openShape();
return { window: [innerWidth, innerHeight], stage: box('stage'), approach: AP().name, power: S.n };
//@ repeat=6 sleep=0.45 shot=out/r26/final/strip/a-2d-m-##.png clip=#stage
// (a) the 2D picture, Mandelbrot shape, steps 0, 1, 2, 3, 5, 16
kindBar('m'); spaceBar(2); const K = [0, 1, 2, 3, 5, 16][__I__]; tick(K); await sleep(350);
const s = L.shape.state(); return { k: K, ...page(), quality: s.quality, pane: s.panes[0] };
//@ sleep=1.2
spaceBar(3); await sleep(1200); const s = await rest(400); return { space: s.space, threeOk: s.threeOk, view: s.view3 };
//@ repeat=6 sleep=0.6 shot=out/r26/final/strip/b-3d-m-##.png clip=#stage
// (b) the 3D picture, Mandelbrot shape, the same steps, the view as it opens
const K = [0, 1, 2, 3, 5, 16][__I__]; tick(K); const s = await rest(700);
return { k: K, ...page(), quality: s.quality, asked: lv(s.three.levels), cardMs: r2(s.ms.three) };
//@ sleep=0.6
// (d) the 3D picture, Julia shape, c = -1 (the named value "the basilica", pressed in the panel)
kindBar('j'); await sleep(400);
const b = [...document.querySelectorAll('#learnShapeCs button')].find(x => /x −1, y 0/.test(x.textContent)); if (!b) fail('no button for c = -1');
b.click(); await sleep(500); scrollTo(0, 0); await sleep(200);
return { c: L.shape.state().c, button: b.textContent.trim() };
//@ repeat=4 sleep=0.6 shot=out/r26/final/strip/d-3d-j-##.png clip=#stage
const K = [0, 2, 5, 16][__I__]; tick(K); const s = await rest(700);
return { k: K, ...page(), c: s.c, quality: s.quality, asked: lv(s.three.levels), cardMs: r2(s.ms.three) };
