// The final look: a last handful of things tried on dist/r26-final.html.
//@
// (1) Before anything is touched: the whole shape has built nothing heavy (no 3D canvas of its own, its own canvas
// and transport out of sight), and with Learn on and Follow = One point it still has not.
const a = { glCanvas: !!document.querySelector('canvas.learn-shape-gl'), shapeCanvasHidden: $('learnShapeCanvas').hidden, barHidden: $('learnShapeBar').hidden, bodyClass: document.body.className };
await openLearn(); await sleep(300);
const b = { glCanvas: !!document.querySelector('canvas.learn-shape-gl'), shapeCanvasHidden: $('learnShapeCanvas').hidden, barHidden: $('learnShapeBar').hidden, onePointBarHidden: $('learnBar').hidden, bodyClass: document.body.className,
  followShown: $('learnFollow').offsetParent !== null, wholeShapePartsShown: [...document.querySelectorAll('.learn-only-shape')].filter(n => n.offsetParent !== null).length };
return { atLoad: a, learnOnePoint: b };
//@
// (2) A reader who has asked for reduced motion (matchMedia answered for them): the first switch does not play by
// itself, and the one-step button goes there at once.
const mm = window.matchMedia.bind(window);
window.matchMedia = q => (/prefers-reduced-motion/.test(q) ? { matches: true, media: q, onchange: null, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return false; } } : mm(q));
$('learnFollowShape').click(); await sleep(500);
const first = { playing: L.shape.state().playing, pos: L.shape.state().pos, play: page().play };
$('learnShapeFwd').click(); await sleep(120);
const fwd = { playing: L.shape.state().playing, pos: L.shape.state().pos };
window.matchMedia = mm;
return { firstSwitch: first, afterForwardButton: fwd };
//@
// (3) The buttons: forward plays one step and stops there; back goes back at once; Play at the end starts again
// from step 0 (with its rest on the start).
$('learnShapeAgain').click(); await sleep(150);
const t0 = performance.now(); $('learnShapeFwd').click(); await sleep(150); const mid = { playing: L.shape.state().playing, pos: r2(L.shape.state().pos), say: page().say };
while (L.shape.state().playing && performance.now() - t0 < 5000) await sleep(30);
const one = { ms: Math.round(performance.now() - t0), pos: L.shape.state().pos, say: page().say };
$('learnShapeFwd').click(); while (L.shape.state().playing) await sleep(30); const two = L.shape.state().pos;
$('learnShapeBack').click(); await sleep(120); const back = L.shape.state().pos;
tick(16); await sleep(150); $('learnShapePlay').click(); await sleep(400); const again = { playing: L.shape.state().playing, pos: L.shape.state().pos, say: page().say };
await sleep(1500); const moving = r2(L.shape.state().pos); $('learnShapePlay').click(); await sleep(100);
return { duringOneStep: mid, oneStepForward: one, twoStepsForward: two, thenBack: back, playAtTheEnd: again, posAfter1900ms: moving };
//@ sleep=0.6 shot=out/r26/final/NAME-1-busy-hands-end.png
// (4) Busy hands while it plays in 3D: shapes, spaces, approaches, speed and the slider changed quickly, twice round.
spaceBar(3); await sleep(1000); $('learnShapeAgain').click(); await sleep(100); $('learnShapePlay').click(); await sleep(1800);
const ids = ['fold', 'lathe', 'bulb', 'pulledplane', 'mercator'], log = [];
for (let r = 0; r < 2; r++) for (const id of ids) {
  await approach(id); kindBar(['j', 'both', 'm'][(r + ids.indexOf(id)) % 3]); await sleep(120);
  if (!L.shape.state().playing) $('learnShapePlay').click();
  const sp = $('learnShapeSpeed'); sp.value = ['fast', 'slow', 'normal'][ids.indexOf(id) % 3]; sp.dispatchEvent(new Event('change', { bubbles: true }));
  await sleep(250); spaceBar(2); await sleep(120); spaceBar(3); await sleep(250); await slider(3.4 + ids.indexOf(id)); await sleep(100);
  const s = L.shape.state(); log.push([id, s.kind, s.space, r2(s.pos), s.playing, s.threeOk, s.note || '-']);
}
const sp = $('learnShapeSpeed'); sp.value = 'normal'; sp.dispatchEvent(new Event('change', { bubbles: true }));
kindBar('both'); tick(6); const s = await rest(600);
return { rounds: log, end: { approach: AP().id, kind: s.kind, space: s.space, pos: s.pos, ok: s.three && s.three.ok, quality: s.quality, speedOfOnePoint: $('learnSpeed').value }, ...page() };
//@ sleep=0.6 shot=out/r26/final/NAME-2-3d-both-c-off-the-plane.png clip=#stage
// (5) Both in 3D with c lifted off the flat plane by its z dial (0.6): the diamond stands above its foot, and the
// sentence about the cut is taken back
const e = $('learnShape-cz'); if (!e) fail('no z dial for c'); const shown = e.offsetParent !== null;
e.value = 0.6; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true }));
const s = await rest(600);
const cut = $('learnShapeNotice').textContent.includes('the cut is exactly');
kindBar('m'); await sleep(400); const cutM = $('learnShapeNotice').textContent.includes('the cut is exactly'); kindBar('both'); await rest(400);
return { zDialShown: shown, c: s.c, diamonds: s.diamonds, cutSentenceShownInBoth: cut, cutSentenceShownForTheMandelbrotShape: cutM };
//@
// (6) and on the 2D page the z dial of c is put away
spaceBar(2); await sleep(300);
const e = $('learnShape-cz'), row = e.closest('.dial') || e.parentNode;
return { zDialShownIn2D: e.offsetParent !== null, c: L.shape.state().c };
