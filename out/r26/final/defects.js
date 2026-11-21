// The final look: every defect of the list, looked for again on dist/r26-final.html with the page's own controls.
// Pictures: out/r26/final/NAME-*.png (NAME = the log's name, so dark and light keep apart).
//@ shot=out/r26/final/NAME-W1-about-0.6s-in.png
// W1: the reader's first click on "A whole shape" plays by itself. What is on the page in the first 2.6 s?
await openLearn();
window.__t0 = performance.now(); window.__seen = [];
$('learnFollowShape').click();
const t0 = window.__t0, rows = [];
let firstMove = null;
while (performance.now() - t0 < 500) { await frame(); const p = page(); if (firstMove === null && p.slider > 0) firstMove = Math.round(performance.now() - t0); rows.push([Math.round(performance.now() - t0), p.slider]); }
window.__firstMove = firstMove;
return { at500ms: page(), firstMoveWithin500ms: firstMove, framesSeen: rows.length };
//@
// W1, M10, M1, and the joiner's (a): the whole of that first play, frame by frame. Every sentence with the time it
// came and how long it stayed; how long the picture rested on every whole step; the gaps between frames.
const t0 = window.__t0, seen = [], gaps = [], rests = {};
let last = null, firstMove = window.__firstMove, prevT = performance.now(), prevPos = -1, restStart = null, restAt = null;
for (;;) {
  await frame();
  const now = performance.now(), p = page(), t = Math.round(now - t0);
  gaps.push(now - prevT); prevT = now;
  if (firstMove === null && p.slider > 0) firstMove = t;
  if (p.say !== last) { seen.push([t, r2(p.slider), p.say]); last = p.say; }
  const pos = L.shape.state().pos;
  if (Number.isInteger(pos) && pos === prevPos) { if (restStart === null) { restStart = now; restAt = pos; } }
  else if (restStart !== null) { rests[restAt] = Math.round(now - restStart); restStart = null; }
  prevPos = pos;
  if (p.play === 'Play' && pos >= 16) break;
  if (now - t0 > 70000) fail('the play did not end in 70 s');
}
const total = performance.now() - t0;
const list = seen.map((r, i) => ({ at: r[0], stays: (i + 1 < seen.length ? seen[i + 1][0] : Math.round(total)) - r[0], slider: r[1], say: r[2] }));
const g = gaps.slice().sort((a, b) => a - b);
const shortRests = Object.entries(rests).filter(([k, v]) => +k > 0 && +k < 16 && v < 250);
return { seconds: r2(total / 1000), firstMoveAtMs: firstMove, sentences: list.length, list, restsMs: rests, restsUnder250ms: shortRests,
  frames: gaps.length, gapMedian: r2(g[g.length >> 1]), gap95: r2(g[Math.floor(g.length * 0.95)]), gapMax: r2(g[g.length - 1]), gapsOver34: gaps.filter(x => x > 34).length };
//@ sleep=0.4 shot=out/r26/final/NAME-2d-m-16-whole-window.png
// the end of the play (M8: the figures of the upright axis; the closing sentence)
return page();
//@ sleep=0.3 shot=out/r26/final/NAME-M1-2d-m-12.4.png clip=#stage
// M1 by hand: a late step under way. What does the sentence say, and what does the page know of the bites?
await slider(12.4); await sleep(200);
const s = L.shape.state();
return { ...page(), thin: s.thin, thickPx: s.thick };
//@ sleep=0.3 shot=out/r26/final/NAME-M1-2d-m-12.4-zoomed.png clip=#stage
// ... and zoomed in on the rim (the wheel, eight notches, over the left edge of the shape)
const st = $('stage'), b = st.getBoundingClientRect(), P = L.shape.state().panes[0];
const X = b.left + P.x + P.w / 2 - 0.21 * Math.min(P.w, P.h) * 0.75, Y = b.top + P.y + P.h / 2;
for (let i = 0; i < 8; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: X, clientY: Y, deltaY: -150, deltaMode: 0 })); await sleep(60); }
await sleep(400);
const s = L.shape.state(), out = { ...page(), zoom: r2(s.view2.m.zoom), thin: s.thin, resetShown: !$('learnShapeViewReset').hidden };
$('learnShapeViewReset').click(); await sleep(200); out.zoomAfterReset = L.shape.state().view2.m.zoom;
return out;
//@
// M10: the label of a step under way; the opening sentence's lines at this width (a short word alone on a line?)
await slider(0); await sleep(150);
const e = $('learnShapeSay'), lines = el => { const rg = document.createRange(); rg.selectNodeContents(el); const tops = {}; for (const r of rg.getClientRects()) tops[Math.round(r.top)] = Math.max(tops[Math.round(r.top)] || 0, Math.round(r.width)); return Object.values(tops); };
const out = { step0: page().say, step0Lines: lines(e) };
await slider(2.5); out.labelUnderWay = page().where; out.underWay = page().say; out.underWayLines = lines(e);
await slider(3); out.labelWhole = page().where; out.whole = page().say;
await slider(0);
return out;
//@
// W2, M3, M4, M9, M12: every word of this part, read from the page: 2D first, then 3D. And the words the round forbids.
const txt = n => (n ? n.textContent.replace(/\s+/g, ' ').trim() : null), out = {};
const panel = () => [...document.querySelectorAll('#learnPanel .learn-only-shape, #learnFollow, #learnSpace, #learnShapeBar, #learnHint')].filter(n => n.offsetParent !== null);
const grab = () => { const all = []; for (const n of panel()) { all.push(n.innerText); for (const q of n.querySelectorAll('[title],[aria-label]')) all.push(q.getAttribute('title') || '', q.getAttribute('aria-label') || ''); } all.push($('learnShapeCanvas').getAttribute('aria-label')); return all.join(' \n '); };
let pile = '';
out.summary = txt(document.querySelector('#learnPanel summary'));
out.note = txt($('learnShapeIntro'));
out.helps = [...document.querySelectorAll('.learn-kind-help p')].map(txt);
const say = async () => { const o = {}; for (const p of [0, 0.5, 1, 1.5, 3, 3.5, 16]) { await slider(p); await sleep(60); o[p] = page().say; pile += ' ' + page().say + ' ' + page().where; } return o; };
out.d2 = {};
for (const kd of ['m', 'j', 'both']) { kindBar(kd); await sleep(150); out.d2[kd] = { hint: txt($('learnHint')), notice: txt($('learnShapeNotice')), say: await say() }; pile += grab(); }
out.named = [...document.querySelectorAll('#learnShapeCs button')].map(txt);
out.cDials = [...document.querySelectorAll('#learnShapeDials label, #learnShapeDials .dial-label, #learnShapeDials .label')].map(txt).filter(Boolean).slice(0, 6);
await slider(0); spaceBar(3); await sleep(1200);
out.d3 = {};
for (const kd of ['m', 'j', 'both']) { kindBar(kd); await sleep(500); await rest(200); out.d3[kd] = { hint: txt($('learnHint')), notice: txt($('learnShapeNotice')), rule: txt($('learnShapeRule')), againTitle: $('learnShapeAgain').title, say: await say() }; pile += grab(); }
const banned = ['iterate', 'iteration', 'escape', 'bailout', 'preimage', 'level set', 'orbit', 'potential', 'membership', 'sample', 'voxel', 'shader', 'mesh', 'render'];
out.bannedFound = banned.filter(w => pile.toLowerCase().includes(w));
out.lettersRead = pile.length;
await slider(0); kindBar('m'); spaceBar(2); await sleep(300);
return out;
//@ sleep=0.4 shot=out/r26/final/NAME-M9-2d-both-05.png clip=#stage
// M9: Both in 2D at step 5, before any drag: what ties the diamond on the left to the picture on the right?
kindBar('both'); await sleep(150); tick(5); await sleep(300); return page();
//@ sleep=0.3 shot=out/r26/final/NAME-E1-2d-both-00.4.png clip=#stage
// E1: the first step held at 0.4. The 2D page first (the reference) ...
await slider(0.4); await sleep(200); return page();
//@ sleep=0.4 shot=out/r26/final/NAME-E1-3d-both-00.4.png clip=#stage
// ... then 3D, Both: is the left ball in the warning colour while the sentence says nobody lands outside?
spaceBar(3); await sleep(1000); await slider(0.4); const s = await rest();
return { ...page(), panes: s.three && s.three.paneLevels ? s.three.paneLevels.map(lv) : null, look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E1-3d-m-00.4.png clip=#stage
kindBar('m'); await sleep(400); await slider(0.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E1-3d-m-00.8.png clip=#stage
await slider(0.8); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-3d-m-01.png clip=#stage
tick(1); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-02.15.png clip=#stage
// E2: a step under way in 3D: does the warning colour mark the part that goes, with the body that stays in sight?
await slider(2.15); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-02.4.png clip=#stage
await slider(2.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-02.7.png clip=#stage
await slider(2.7); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-04.4.png clip=#stage
await slider(4.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-06.4.png clip=#stage
await slider(6.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-E2-3d-m-09.4.png clip=#stage
// (a late step: the checker saw "a small gold lump that blinks red at each step")
await slider(9.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3(), thin: s.thin, aboveThick: s.above[0] ? s.above[0].thick : null };
//@ sleep=0.4 shot=out/r26/final/NAME-M11-3d-m-00.png clip=#stage
// M11: the 3D view as it opens, steps 0, 2, 5, 8, 16
tick(0); const s = await rest(); return { ...page(), view: s.view3, look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-M11-3d-m-02.png clip=#stage
tick(2); const s = await rest(); return { ...page(), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-M11-3d-m-05.png clip=#stage
tick(5); const s = await rest(); return { ...page(), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-M11-3d-m-08.png clip=#stage
tick(8); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.4 shot=out/r26/final/NAME-M11-3d-m-16.png clip=#stage
tick(16); const s = await rest(); return { ...page(), asked: lv(s.three.levels), look: look3() };
//@ sleep=0.5 shot=out/r26/final/NAME-M11-3d-m-16-zoom3.png clip=#stage
// the same from close (the wheel, over the middle): the "pale patch with a straight edge" the fixer saw on the flat top
const st = $('stage'), b = st.getBoundingClientRect();
for (let i = 0; i < 5; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -150, deltaMode: 0 })); await sleep(150); }
const s = await rest(900); return { zoom: r2(s.view3.zoom), quality: s.quality, ms: s.ms, look: look3() };
//@ sleep=0.5 shot=out/r26/final/NAME-M1-3d-m-12.4.png
// M1 in 3D, a late step under way, at the opening view
$('learnShapeViewReset').click(); await sleep(300); await slider(12.4); const s = await rest(); return { ...page(), asked: lv(s.three.levels), thin: s.thin };
//@ sleep=0.5 shot=out/r26/final/NAME-M2-turnalong-08.png clip=#stage
// M2: the rougher approaches at step 8 and at step 16
const name = await approach('turnalong'); tick(8); const s = await rest(900); return { name, ...page(), asked: lv(s.three.levels) };
//@ sleep=0.5 shot=out/r26/final/NAME-M2-turnalong-16.png clip=#stage
tick(16); const s = await rest(900); return { ...page(), asked: lv(s.three.levels) };
//@ sleep=0.5 shot=out/r26/final/NAME-M2-fold-16.png clip=#stage
const name = await approach('fold'); tick(16); const s = await rest(900); return { name, ...page() };
//@ sleep=0.5 shot=out/r26/final/NAME-M2-lathe-16.png clip=#stage
const name = await approach('lathe'); tick(16); const s = await rest(900); return { name, ...page() };
//@ sleep=0.5 shot=out/r26/final/NAME-M2-bulb-16.png clip=#stage
const name = await approach('bulb'); tick(16); const s = await rest(900); return { name, ...page() };
//@ sleep=0.4 shot=out/r26/final/NAME-A2-quat4-w1.5-m-00.5.png
// A2: "Quaternions, 4D (slices)" with its dial w at 1.5 and at 0.3: the words of the start and of the first step
// against what the 3D rule itself does with a grid of the ball (0.125 between points)
const name = await approach('quat4'), out = { name };
const grid = (kind, c, k) => { let n = 0, left = 0; for (let i = -16; i <= 16; i++) for (let j = -16; j <= 16; j++) for (let m = -16; m <= 16; m++) { const p = [i / 8, j / 8, m / 8]; if (i * i + j * j + m * m > 256) continue; n++; if (LAB.learnShape3d.out(p, kind, kind === 'm' ? p : c, k) > k) left++; } return [left, n]; };
for (const w of [0, 0.3, 1.5]) {
  S.param.quat4.w = w; refresh(); const o = out['w=' + w] = {};
  kindBar('m'); await sleep(400);
  for (const p of [0, 0.5, 1]) { await slider(p); await rest(250); o['m ' + p] = page().say; }
  o.mLeftAfterStep1 = grid('m', null, 1);
  kindBar('j'); await sleep(400); await slider(0); const s = await rest(250); o['j 0'] = page().say; o.jInAtStart = grid('j', s.c, 0);
  kindBar('both'); await sleep(400); for (const p of [0, 0.5, 1]) { await slider(p); await rest(250); o['both ' + p] = page().say; }
}
kindBar('m'); await slider(0.5); await rest();
return out;
//@ sleep=0.4 shot=out/r26/final/NAME-A1-power1-3d-j-12.png
// A1: the ordinary Power dial at 1, Julia shape (c as it opens), 3D. Step by step: the sentence, how much of the
// picture is not stage colour, and how many points of a 0.1 grid of the ball the 3D rule still keeps.
const a = LAB.APPROACHES.find(x => x.id === 'quat4'); for (const p of a.params || []) if (p.key !== undefined) S.param.quat4[p.key] = p.def; refresh();
await approach('mercator'); kindBar('j');
const pw = $('pow'); pw.value = 1; pw.dispatchEvent(new Event('input', { bubbles: true })); pw.dispatchEvent(new Event('change', { bubbles: true })); await sleep(500);
const c = L.shape.state().c, rows = [];
const kept = k => { let left = 0; for (let i = -20; i <= 20; i++) for (let j = -20; j <= 20; j++) for (let m = -20; m <= 20; m++) { if (i * i + j * j + m * m > 400) continue; if (LAB.learnShape3d.out([i / 10, j / 10, m / 10], 'j', c, k) > k) left++; } return left; };
for (const k of [0, 4, 7, 8, 9, 12, 16]) { tick(k); await rest(); rows.push({ k, say: page().say, look: look3(), gridPointsLeft: kept(k) }); }
tick(12); await rest(); return { n: S.n, c, rows };
//@ sleep=0.4 shot=out/r26/final/NAME-A1-power1-2d-j-12.png
spaceBar(2); await sleep(400); tick(12); await sleep(250); return page();
//@ sleep=0.4 shot=out/r26/final/NAME-A1-c7-3d-j-02.png
// A1 again: c = (7, 0, 0) at the power 2, and what a play says of it
const pw = $('pow'); pw.value = 2; pw.dispatchEvent(new Event('input', { bubbles: true })); pw.dispatchEvent(new Event('change', { bubbles: true })); await sleep(200);
L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0], pos: 2 }); const s = await rest();
const out = { n: S.n, ...page(), look: look3(), c: s.c };
tick(0); await rest(200); out.step0 = page().say; tick(1); await rest(200); out.step1 = page().say; await slider(0.5); await rest(200); out.half = page().say; tick(2); await rest(200);
return out;
//@ sleep=0.4 shot=out/r26/final/NAME-A1-zoomed-2-empty-3d.png clip=#stage
// the fixer's open point: zoomed in beyond 1.5 an empty 3D picture is not called empty
const st = $('stage'), b = st.getBoundingClientRect();
for (let i = 0; i < 3; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -160, deltaMode: 0 })); await sleep(150); }
const s = await rest(600); const out = { zoom: r2(s.view3.zoom), ...page(), look: look3() };
return out;
//@ sleep=0.4 shot=out/r26/final/NAME-A5-3d-zoomed-lone-c.png clip=#stage
// A5: 3D, Julia shape, c = (-1.8, 0.9, 0) set with its dials, then the wheel until the diamond is off the stage
$('learnShapeViewReset').click(); await sleep(200);
L.shape.set({ kind: 'j', space: 3, c: [-0.4, 0.3, 0], pos: 3 });
for (const [id, v] of [['learnShape-cx', -1.8], ['learnShape-cy', 0.9]]) { const e = $(id); if (!e) fail('no dial ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); }
await sleep(400);
const before = L.shape.state().diamonds, st = $('stage'), b = st.getBoundingClientRect();
for (let i = 0; i < 6; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, clientX: b.left + b.width / 2, clientY: b.top + b.height / 2, deltaY: -200, deltaMode: 0 })); await sleep(150); }
const s = await rest(700);
return { c: s.c, zoom: r2(s.view3.zoom), diamondBefore: before, diamondNow: s.diamonds, stage: [s.panes[0].w, s.panes[0].h] };
//@ sleep=0.3 shot=out/r26/final/NAME-A5-3d-diamond-in-sight.png clip=#stage
// (and back at zoom 1 the diamond and its letter are both there)
$('learnShapeViewReset').click(); const s = await rest(500); return { zoom: s.view3.zoom, diamond: s.diamonds };
//@
// A3: the tip c = (-2, 0) of the Mandelbrot shape, out2 against mask2; and the whole square, both kinds
L.shape.set({ kind: 'm', space: 2, c: [-0.4, 0.3, 0], pos: 0 }); await sleep(250);
const out = { n: S.n, tip: { out2: L.shape.out2([-2, 0], 'm', null, 16), out2K40: L.shape.out2([-2, 0], 'm', null, 40) } };
const m16 = L.shape.mask2('m', 129, 2, 16), m40 = L.shape.mask2('m', 129, 2, 40);
out.tip.mask2 = m16[64 * 129]; out.tip.mask2K40 = m40[64 * 129];
return out;
//@
// A4: One point keeps its place across a visit to the whole shape (2D -> 3D -> 2D inside it), by the page's controls
$('learnFollowPoint').click(); await sleep(250);
$('learnNext').click(); await sleep(200); L.goto(1, 0.4); await sleep(150);
const st = () => { const s = L.state(); return { space: s.space, step: s.step, move: s.move, t: r3(s.t), z0: s.z0, c: s.c }; };
const before = st();
$('learnFollowShape').click(); await sleep(250); L.shape.pause(); spaceBar(3); await sleep(600); spaceBar(2); await sleep(300);
$('learnFollowPoint').click(); await sleep(300);
const after = st();
$('learnFollowShape').click(); await sleep(200); L.shape.pause(); $('learnFollowPoint').click(); await sleep(250); const plain = st();
$('learnFollowShape').click(); await sleep(200); L.shape.pause(); spaceBar(3); await sleep(600); $('learnFollowPoint').click(); await sleep(300); const endIn3 = st();
return { before, after, kept: JSON.stringify(before) === JSON.stringify(after), plainRoundTripKept: JSON.stringify(before) === JSON.stringify(plain), endingIn3D: endIn3 };
