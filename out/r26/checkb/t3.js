// 3D, five approaches, by the page's own controls. Picture number = 10 * approach + view:
//   approach 0 mercator (Sphere inversions, one plane), 1 fold (two planes), 2 turnalong (Turning plane, along),
//            3 lathe (Quaternion square), 4 bulb (Mandelbulb)
//   view 0..4: Mandelbrot shape after 0, 2, 4, 8, 16 steps, as the view opens
//        5: after 8 steps, turned by a drag      6: the same, zoomed in by five notches of the wheel
//        7: after 16 steps, still turned and zoomed
//        8: view put back, Julia shape, c = -1 (the named button), after 4 steps     9: the same after 10 steps
//@ repeat=50 sleep=1.0 shot=out/r26/checkb/NAME-##.png clip=#stage
const AP = ['mercator', 'fold', 'turnalong', 'lathe', 'bulb'], a = Math.floor(__I__ / 10), s = __I__ % 10;
const cv = $('learnShapeCanvas'), st = $('stage'), tick = j => $('learnShapeTicks').children[j].click();
if (__I__ === 0) { await openLearn(); await pickShape(); $('learnShapeAgain').click(); spaceBar(3); await sleep(300); }
let name = LAB.APPROACHES[S.approach].name;
if (s === 0) { name = await approach(AP[a]); kindBar('m'); if (!$('learnShapeViewReset').hidden) $('learnShapeViewReset').click(); await sleep(200); }
if (s <= 4) tick([0, 2, 4, 8, 16][s]);
if (s === 5) {
  tick(8); await sleep(300);
  ptr(cv, 'pointerdown', 430, 250);
  for (let i = 1; i <= 15; i++) { ptr(cv, 'pointermove', 430 + 10 * i, 250 + 4 * i); await frame(); }
  ptr(cv, 'pointerup', 580, 310);
}
if (s === 6) { for (let i = 0; i < 5; i++) { wheel(st, 430, 255, -100); await frame(); await frame(); } }
if (s === 7) tick(16);
if (s === 8) {
  $('learnShapeViewReset').click(); kindBar('j'); await sleep(100);
  const b = [...document.querySelectorAll('#learnShapeCs button')].find(x => x.textContent.startsWith('c = −1'));
  if (!b) fail('no button for c = -1'); b.click(); tick(4);
}
if (s === 9) tick(10);
await frame();
return { i: __I__, approach: name, view: s, ...said(), rule: $('learnShapeRule').textContent.slice(0, 160), notice: s === 0 || s === 8 ? $('learnShapeNotice').textContent : undefined };
