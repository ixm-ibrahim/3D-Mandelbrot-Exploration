// Every defect of the two checkers, shown on the page with the page's own controls where a reader has them.
// Run on the page as joined (--page r26-fix-before --log before) and on the mended page (--log after):
// the same steps, the same pictures, side by side.
//@ sleep=0.05 shot=out/r26/fix/NAME-W1-half-second-in.png
// W1: the first switch to "A whole shape" plays by itself. What stands on the page half a second after the click?
await openLearn(); window.__t0 = performance.now(); window.__rows = [];
const rows = window.__rows, note = () => rows.push([Math.round(performance.now() - window.__t0), +said().slider.toFixed(2), said().where, said().say]);
await pickShape(); note();
for (const t of [60, 250, 450]) { await sleep(Math.max(0, t - (performance.now() - window.__t0))); note(); }
return rows;
//@
// W1, M10, M1: the whole of that first play. Every change of the sentence, with the time it came and how long it stayed.
const t0 = window.__t0, seen = []; let last = null;
for (let i = 0; i < 900; i++) {
  const s = said(), t = Math.round(performance.now() - t0);
  if (s.say !== last) { seen.push([t, +s.slider.toFixed(2), s.say]); last = s.say; }
  if (s.play === 'Play' && s.slider >= 16) break;
  await sleep(40);
}
const out = seen.map((r, i) => ({ at: r[0], for: (i + 1 < seen.length ? seen[i + 1][0] : Math.round(performance.now() - t0)) - r[0], slider: r[1], say: r[2] }));
return { seconds: +((performance.now() - t0) / 1000).toFixed(1), sentences: out.length, shortest: Math.min(...out.slice(0, -1).map(o => o.for)), list: out };
//@ sleep=0.3 shot=out/r26/fix/NAME-M8-2d-m-16.png clip=#stage
// M8: the numbers 1 and -1 of the upright axis on the tips of the shape (step 16, as the play ends)
return said();
//@ sleep=0.3 shot=out/r26/fix/NAME-M1-2d-m-12.4.png
// M1: a late step under way, by hand: what is there to see, and what does the sentence say?
await slider(12.4); await sleep(200); return said();
//@ sleep=0.3 shot=out/r26/fix/NAME-M10-2d-m-00.png
// M10: the sentence of step 0 at 1400 wide (one short word alone on a second line?), and the label of a step under way
await slider(0); await sleep(150);
const e = $('learnShapeSay'), rg = document.createRange(); rg.selectNodeContents(e);
const lines = [...rg.getClientRects()].map(r => Math.round(r.width));
await slider(2.5); const where = said().where; await slider(0);
return { say: said().say, lineWidths: lines, labelOfAStepUnderWay: where };
//@
// W2, M3, M4, M9, M12: the words. Panel, helps, named values, hints, tooltips, pane names (read from the page).
const txt = id => ($(id) ? $(id).textContent.replace(/\s+/g, ' ').trim() : null);
const out = {};
out.note = txt('learnShapeIntro');
out.helps = [...document.querySelectorAll('.learn-kind-help p')].map(p => p.textContent.replace(/\s+/g, ' ').trim());
kindBar('both'); await sleep(200);
out.named = [...document.querySelectorAll('#learnShapeCs button')].map(b => b.textContent.replace(/\s+/g, ' ').trim());
out.notice2dBoth = txt('learnShapeNotice'); out.hint2dBoth = txt('learnHint');
const S2 = {}; for (const kd of ['m', 'j', 'both']) { kindBar(kd); await sleep(80); S2[kd] = {}; for (const p of [0, 0.5, 1, 3, 3.5, 16]) { await slider(p); S2[kd][p] = said().say; } }
out.sentences2d = S2; await slider(0);
kindBar('j'); spaceBar(3); await sleep(900);
out.hint3dJulia = txt('learnHint'); out.rule3d = txt('learnShapeRule'); out.notice3dJulia = txt('learnShapeNotice'); out.againTitle3d = $('learnShapeAgain').title;
kindBar('m'); await sleep(400); out.notice3dM = txt('learnShapeNotice'); out.hint3dM = txt('learnHint');
const S3 = {}; for (const kd of ['m', 'both']) { kindBar(kd); await sleep(300); S3[kd] = {}; for (const p of [0, 0.5, 1, 3, 3.5, 16]) { await slider(p); S3[kd][p] = said().say; } }
out.sentences3d = S3; await slider(0); kindBar('m'); spaceBar(2); await sleep(200);
return out;
//@ sleep=0.5 shot=out/r26/fix/NAME-M9-2d-both-05.png clip=#stage
// M9: Both, before any drag: what ties the left diamond to the right picture?
kindBar('both'); await sleep(100); tick(5); await sleep(300); return said();
//@ sleep=0.3 shot=out/r26/fix/NAME-E1-2d-both-00.4.png clip=#stage
// E1: the first step held at 0.4, on the 2D page (which is right) ...
await slider(0.4); await sleep(200); return said();
//@ sleep=0.3 shot=out/r26/fix/NAME-E1-3d-both-00.4.png clip=#stage
// ... and in 3D, Both: is the left ball in the warning colour while the sentence says nothing is thrown out?
spaceBar(3); await sleep(900); await slider(0.4); const s = await rest(); return { ...said(), asked: lv(s), panes: s.three && s.three.paneLevels ? s.three.paneLevels.map(p => p.map(l => l.k + ':a' + (+l.alpha).toFixed(2) + (l.tint ? ':t' + (+l.tint).toFixed(2) : '')).join(' ')) : null };
//@ sleep=0.3 shot=out/r26/fix/NAME-E1-3d-m-00.4.png clip=#stage
kindBar('m'); await sleep(300); await slider(0.4); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-E1-3d-m-01.png clip=#stage
// after the first step, at rest
tick(1); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-E2-3d-m-02.15.png clip=#stage
// E2: a step under way in 3D: does the warning colour show which part goes? (step 3 at 0.15, 0.4, 0.7; step 7 at 0.4)
await slider(2.15); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-E2-3d-m-02.4.png clip=#stage
await slider(2.4); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-E2-3d-m-02.7.png clip=#stage
await slider(2.7); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-E2-3d-m-06.4.png clip=#stage
await slider(6.4); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-M11-3d-m-05.png clip=#stage
// M11: the 3D view as it opens (steps 5 and 16): is the shape seen nearly edge on?
tick(5); const s = await rest(); return { ...said(), view: s.view3 };
//@ sleep=0.3 shot=out/r26/fix/NAME-M11-3d-m-16.png
tick(16); const s = await rest(); return { ...said(), view: s.view3 };
//@ sleep=0.3 shot=out/r26/fix/NAME-M1-3d-m-12.4.png
// M1 in 3D: a late step under way
await slider(12.4); const s = await rest(); return { ...said(), asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-M2-turnalong-16.png clip=#stage
// M2: step 16 of the rougher approaches
const name = await approach('turnalong'); tick(16); const s = await rest(900); return { name, ...said() };
//@ sleep=0.3 shot=out/r26/fix/NAME-M2-fold-16.png clip=#stage
const name = await approach('fold'); tick(16); const s = await rest(900); return { name, ...said() };
//@ sleep=0.3 shot=out/r26/fix/NAME-M2-lathe-16.png clip=#stage
const name = await approach('lathe'); tick(16); const s = await rest(900); return { name, ...said() };
//@ sleep=0.3 shot=out/r26/fix/NAME-M2-bulb-16.png clip=#stage
const name = await approach('bulb'); tick(16); const s = await rest(900); return { name, ...said() };
//@ sleep=0.3 shot=out/r26/fix/NAME-A2-quat4-w1.5-m-00.5.png
// A2: "Quaternions, 4D (slices)" with its dial w at 1.5: the words of the first step against what the step does
const name = await approach('quat4'); Object.assign(S.param.quat4, { w: 1.5 }); go(); kindBar('m'); await sleep(300);
const say = {}; for (const p of [0, 0.5, 1]) { await slider(p); await rest(300); say[p] = said().say; }
let n = 0, left1 = 0; for (let i = 0; i <= 20; i++) for (let j = 0; j <= 20; j++) for (let m = 0; m <= 20; m++) { const p = [-2 + i * 0.2, -2 + j * 0.2, -2 + m * 0.2]; if (Math.hypot(...p) > 2) continue; n++; if (LAB.learnShape3d.out(p, 'm', p, 1) > 1) left1++; }
await slider(0.5); const s = await rest(); return { name, w: S.param.quat4.w, say, gridPointsOfTheBall: n, leftAfterStep1: left1, asked: lv(s) };
//@ sleep=0.3 shot=out/r26/fix/NAME-A2-quat4-w1.5-j-00.png
kindBar('j'); await sleep(300); await slider(0); const s = await rest();
let n = 0, in0 = 0; for (let i = 0; i <= 20; i++) for (let j = 0; j <= 20; j++) for (let m = 0; m <= 20; m++) { const p = [-2 + i * 0.2, -2 + j * 0.2, -2 + m * 0.2]; if (Math.hypot(...p) > 2) continue; n++; if (LAB.learnShape3d.out(p, 'j', s.c, 0) > 0) in0++; }
const say0 = said().say; kindBar('both'); await sleep(300); const both = {}; for (const p of [0, 0.5, 1]) { await slider(p); await rest(300); both[p] = said().say; }
kindBar('j'); await slider(0); await rest(300);
return { say: say0, gridPointsOfTheBall: n, inShape0: in0, both };
//@ sleep=0.3 shot=out/r26/fix/NAME-A1-power1-3d-j-12.png
// A1: the Power dial at 1, Julia shape (c as it opens), 3D: nothing is left from step 9 on. What does the page say?
dialsBack('quat4'); await approach('mercator'); kindBar('j'); setRange('pow', 1); await sleep(400);
const rows = [];
for (const k of [0, 4, 8, 9, 12, 16]) { tick(k); const s = await rest(); rows.push([k, said().say, 'picture covers ' + cover()]); }
tick(12); await rest(); return { n: S.n, c: L.shape.state().c, rows };
//@ sleep=0.3 shot=out/r26/fix/NAME-A1-power1-2d-j-12.png
spaceBar(2); await sleep(300); tick(12); await sleep(200); return said();
//@ sleep=0.3 shot=out/r26/fix/NAME-A1-c7-3d-j-02.png
// A1 again: c = (7, 0, 0), from step 1
setRange('pow', 2); await sleep(100); L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0], pos: 2 }); const s = await rest(); return { ...said(), cover: cover(), c: s.c };
//@ sleep=0.3 shot=out/r26/fix/NAME-A5-3d-zoomed-lone-c.png clip=#stage
// A5: 3D, Julia shape, c = (-1.8, 0.9, 0), five notches of the wheel: the diamond is off the stage. Is its letter?
L.shape.set({ kind: 'j', space: 3, c: [-0.4, 0.3, 0], pos: 3 }); setRange('learnShape-cx', -1.8); setRange('learnShape-cy', 0.9); await sleep(300);
const a = L.shape.state(), cv = $('learnShapeCanvas');
for (let i = 0; i < 5; i++) { wheel($('stage'), 430, 255, -200); await sleep(120); }
const s = await rest(600);
return { c: s.c, zoom: +s.view3.zoom.toFixed(2), diamondBefore: a.diamonds, diamond: s.diamonds, stage: [s.panes[0].w, s.panes[0].h] };
//@
// A3: the tip c = (-2, 0) of the Mandelbrot shape: out2 against mask2
$('learnShapeViewReset').click(); L.shape.set({ kind: 'm', space: 2, c: [-0.4, 0.3, 0], pos: 0 }); await sleep(200);
const m = L.shape.mask2('m', 129, 2, 16), m40 = L.shape.mask2('m', 129, 2, 40);
let differ = 0, asked = 0; for (let r = 0; r < 129; r++) for (let q = 0; q < 129; q++) { const p = [-2 + q * 4 / 128, 2 - r * 4 / 128]; asked++; if (L.shape.out2(p, 'm', null, 16) !== m[r * 129 + q]) differ++; }
return { out2: L.shape.out2([-2, 0], 'm', null, 16), mask2: m[64 * 129], out2K40: L.shape.out2([-2, 0], 'm', null, 40), mask2K40: m40[64 * 129], pointsAsked: asked, differ };
//@
// A4: One point, 2D, Next step, the slider into the second move; A whole shape; 3D, then 2D; One point again.
$('learnFollowPoint').click(); await sleep(200);
$('learnNext').click(); await sleep(150); L.goto(1, 0.4); await sleep(100);
const st = () => { const s = L.state(); return [s.space, s.step, s.move, +s.t.toFixed(3), s.z0, s.c]; }, before = st();
$('learnFollowShape').click(); await sleep(200); L.shape.pause(); spaceBar(3); await sleep(500); spaceBar(2); await sleep(300);
$('learnFollowPoint').click(); await sleep(300);
const after = st();
// and the plain round trip, and the round trip that ends in another space
L.goto(1, 0.4); const b2 = st(); $('learnFollowShape').click(); await sleep(200); $('learnFollowPoint').click(); await sleep(200); const a2 = st();
$('learnFollowShape').click(); await sleep(200); spaceBar(3); await sleep(500); $('learnFollowPoint').click(); await sleep(300); const a3 = st();
L.set({ space: 2 }); $('learnFollowShape').click(); await sleep(200);
return { before, after, kept: JSON.stringify(before) === JSON.stringify(after), plainRoundTrip: JSON.stringify(b2) === JSON.stringify(a2), endingIn3D: a3 };
