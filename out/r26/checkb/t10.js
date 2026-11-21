// Evidence for the first step in 3D: the slider held at 0.4 of step 1, where the sentence says that nothing is
// thrown out. One picture, Both, and the 2D page at the same place beside it. Also what the 3D picture was asked
// to draw there (the page's own record).
//@ sleep=1.0 shot=out/r26/checkb/NAME-3d-both-00.4.png clip=#stage
await openLearn(); await pickShape(); $('learnShapeAgain').click(); kindBar('both'); spaceBar(3); await sleep(900);
$('learnShapePos').value = 0.4; $('learnShapePos').dispatchEvent(new Event('input', { bubbles: true })); await sleep(500);
return { ...said(), asked: L.shape.state().three.levels };
//@ sleep=1.0 shot=out/r26/checkb/NAME-3d-m-00.4.png clip=#stage
kindBar('m'); await sleep(500);
return { ...said(), asked: L.shape.state().three.levels };
//@ sleep=0.6 shot=out/r26/checkb/NAME-2d-both-00.4.png clip=#stage
kindBar('both'); spaceBar(2); await sleep(300);
return said();
//@ sleep=1.0 shot=out/r26/checkb/NAME-3d-m-06.4.png clip=#stage
// and a late step in 3D, dark theme: the whole body in the warning colour
kindBar('m'); spaceBar(3); await sleep(600);
$('learnShapePos').value = 6.4; $('learnShapePos').dispatchEvent(new Event('input', { bubbles: true })); await sleep(500);
return { ...said(), asked: L.shape.state().three.levels };
//@ sleep=0.6 shot=out/r26/checkb/NAME-2d-m-06.4.png clip=#stage
spaceBar(2); await sleep(300); return said();
