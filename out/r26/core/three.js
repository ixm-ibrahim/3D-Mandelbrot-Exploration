// The 3D calling code, against the fake (page fake) or builder "three"'s live module (page three).
//@
const s = await shapeOn({ kind: 'm', space: 3, pos: 0 });
if (!s.threeOk) fail('3D should be there on this page: ' + s.note);
return { state: brief(s), three: s.three };
//@ sleep=0.5 shot=out/r26/core/NAME-m-00.png clip=.bench-main
//@
const s = L.shape.goto(4);
return { state: brief(s), three: s.three };
//@ sleep=0.5 shot=out/r26/core/NAME-m-04.png clip=.bench-main
//@
const s = L.shape.set({ pos: 4.4 });
const lv = s.three.levels;
if (lv.length !== 3) fail('between two steps three skins are asked for: ' + JSON.stringify(lv));
return { state: brief(s), three: s.three };
//@ sleep=0.5 shot=out/r26/core/NAME-m-04.4.png clip=.bench-main
//@
const s = L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 6 });
if (s.three.panes !== 2) fail('Both should hand over two panes');
return { state: brief(s), three: s.three, panes: s.panes, diamonds: s.diamonds };
//@ sleep=0.5 shot=out/r26/core/NAME-both-06.png clip=.bench-main
//@
// a c off the flat plane: the diamond stands above its foot
const s = L.shape.set({ kind: 'j', c: [-0.3, 0.2, 0.6], pos: 3 });
return { state: brief(s), three: s.three, diamonds: s.diamonds };
//@ sleep=0.5 shot=out/r26/core/NAME-j-03.png clip=.bench-main
//@
// turning by hand: scripted pointer events on the canvas over the picture
const cv = $('learnShapeCanvas'), before = L.shape.state().view3;
ptr(cv, 'pointerdown', 300, 200);
const q = [];
for (let i = 1; i <= 6; i++) { ptr(cv, 'pointermove', 300 + 20 * i, 200 + 6 * i); await frame(); await frame(); q.push(LAB.learn.shape.state().quality); }
ptr(cv, 'pointerup', 420, 236);
await sleep(300);
const s = L.shape.state();
if (Math.abs(s.view3.yaw - before.yaw) < 0.5) fail('dragging should turn the picture: ' + JSON.stringify([before, s.view3]));
if (s.quality !== 'still') fail('at rest the picture should be the fine one');
return { before, after: s.view3, whileDragging: q, atRest: s.quality, resetShown: shown('learnShapeViewReset') };
//@ sleep=0.3 shot=out/r26/core/NAME-turned.png clip=.bench-main
//@
$('learnShapeViewReset').click(); await sleep(200);
const s = L.shape.state();
if (Math.abs(s.view3.yaw + 0.62) > 1e-9 || shown('learnShapeViewReset')) fail('Reset view should put the view back and go away');
// play from the start to step 2 and watch what is asked of the 3D picture
L.shape.goto(0); L.shape.play();
const seen = [];
for (let i = 0; i < 200 && L.shape.state().pos < 2; i++) { await sleep(40); const t = L.shape.state(); seen.push([+t.pos.toFixed(2), t.quality, t.three.levels.map(l => l.k + ':' + l.alpha.toFixed(2) + ':' + l.tint.toFixed(2)).join(' ')]); }
L.shape.pause(); await sleep(300);
const e = L.shape.state();
return { samples: seen.filter((x, i) => i % 6 === 0), atRest: e.quality, pos: e.pos, ms: e.ms };
//@
// the light theme and back: the colours handed over follow the theme
document.documentElement.setAttribute('data-theme', 'light'); await sleep(300);
const s = L.shape.set({ kind: 'both', pos: 5 });
return { state: brief(s) };
//@ sleep=0.4 shot=out/r26/core/NAME-light-both-05.png clip=.bench-main
//@
document.documentElement.removeAttribute('data-theme'); await sleep(200);
return brief(L.shape.state());
