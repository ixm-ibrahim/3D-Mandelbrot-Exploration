// What the cures bring with them, checked on the mended page: the rest at the start of a play and where it must not
// be; the sentence of a bite too fine to see and its going when zoomed in; the plays of Both and of an empty shape;
// the 3D module's new columns() against its own out(); what a lost graphics context does to what the words know.
//@
// 1. The one-step button from step 0 does not rest first, and keeps the sentence of its step.
await openShape(); kindBar('m'); spaceBar(2); await sleep(200);
const t0 = performance.now(); $('learnShapeFwd').click(); await sleep(120);
const early = said(); let t1 = 0;
for (let i = 0; i < 100; i++) { await sleep(25); if (said().play === 'Play' && said().slider >= 1) { t1 = performance.now() - t0; break; } }
return { after120ms: early, reachedStep1AfterMs: Math.round(t1), then: said() };
//@
// 2. Play from the middle (step 3) starts at once; Play from the start rests 1.5 s (Normal) on the opening sentence.
tick(3); await sleep(100); let t0 = performance.now(); $('learnShapePlay').click(); await sleep(150); const mid = { afterMs: Math.round(performance.now() - t0), ...said() }; $('learnShapePlay').click();
$('learnShapeAgain').click(); await sleep(100); t0 = performance.now(); $('learnShapePlay').click(); let moved = 0;
for (let i = 0; i < 200; i++) { await sleep(20); if (said().slider > 0) { moved = performance.now() - t0; break; } }
$('learnShapePlay').click();
const sp = $('learnShapeSpeed'), rests = {};
for (const v of ['fast', 'slow']) { sp.value = v; sp.dispatchEvent(new Event('change', { bubbles: true })); $('learnShapeAgain').click(); await sleep(100); t0 = performance.now(); $('learnShapePlay').click(); for (let i = 0; i < 300; i++) { await sleep(20); if (said().slider > 0) { rests[v] = Math.round(performance.now() - t0); break; } } $('learnShapePlay').click(); }
sp.value = 'normal'; sp.dispatchEvent(new Event('change', { bubbles: true })); $('learnShapeAgain').click();
return { fromStep3: mid, fromTheStartFirstMoveAfterMs: Math.round(moved), atFastAndSlow: rests };
//@ sleep=0.3 shot=out/r26/fix/NAME-thin-2d-zoomed.png
// 3. A bite too fine to see, 2D: the sentence at 12.4, and after zooming in on the shape's edge (six notches).
await slider(12.4); await sleep(200); const before = { ...said(), thin: L.shape.state().thin };
for (let i = 0; i < 6; i++) { wheel($('stage'), 300, 255, -200); await sleep(100); }
await sleep(500); const s = L.shape.state();
return { before, zoomedIn: { ...said(), zoom: +s.view2.m.zoom.toFixed(2), thin: s.thin, bitePx: s.thick[0] && s.thick[0][12] } };
//@ sleep=0.3 shot=out/r26/fix/NAME-thin-3d-zoomed.png
// ... and in 3D
$('learnShapeViewReset').click(); spaceBar(3); await sleep(900); await slider(12.4); let s = await rest(); const before = { ...said(), thin: s.thin, asked: lv(s) };
for (let i = 0; i < 5; i++) { wheel($('stage'), 430, 255, -200); await sleep(120); }
s = await rest(700);
return { before, zoomedIn: { ...said(), zoom: +s.view3.zoom.toFixed(2), thin: s.thin, asked: lv(s) } };
//@
// 4. One play of Both in 2D and one of an empty Julia shape in 3D (c = 7), Fast: every sentence shown.
$('learnShapeViewReset').click(); spaceBar(2); kindBar('both'); const sp = $('learnShapeSpeed'); sp.value = 'fast'; sp.dispatchEvent(new Event('change', { bubbles: true }));
const play = async () => { $('learnShapeAgain').click(); await sleep(300); const t0 = performance.now(), seen = []; let last = null; $('learnShapePlay').click();
  for (let i = 0; i < 900; i++) { const s = said(); if (s.say !== last) { seen.push([Math.round(performance.now() - t0), +s.slider.toFixed(2), s.say]); last = s.say; } if (s.play === 'Play' && s.slider >= 16) break; await sleep(25); }
  return { seconds: +((performance.now() - t0) / 1000).toFixed(1), seen }; };
const both2 = await play();
L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0] }); await sleep(900); const empty3 = await play();
L.shape.set({ kind: 'both', space: 3, c: [-0.4, 0.3, 0] }); await sleep(900); const both3 = await play();
sp.value = 'normal'; sp.dispatchEvent(new Event('change', { bubbles: true })); L.shape.set({ kind: 'm', space: 2, pos: 0 });
return { both2, empty3, both3 };
//@
// 5. Another power: the note, the helps and "What to notice" (Both, 2D), read from the page.
setRange('pow', 3); await sleep(200); kindBar('both'); await sleep(200);
const txt = id => $(id).textContent.replace(/\s+/g, ' ').trim();
const p3 = { note: txt('learnShapeIntro'), notice: txt('learnShapeNotice'), named: [...document.querySelectorAll('#learnShapeCs button')].map(b => b.textContent) };
$('mod-absx') && 0;
setRange('pow', 2.5); await sleep(200); const p25 = { note: txt('learnShapeIntro'), notice: txt('learnShapeNotice') };
setRange('pow', 2); await sleep(200); kindBar('m');
return { power3: p3, power2_5: p25, back: txt('learnShapeIntro').slice(-90) };
//@
// 6. columns() of the 3D module against its own out(): 33 x 33 upright lines with 48 points each, both kinds, six approaches.
const T = LAB.learnShape3d.make(), rows = [];
for (const id of ['mercator', 'fold', 'lathe', 'turnalong', 'alongonce', 'pulledplane', 'quat4']) {
  await approach(id); if (id === 'quat4') { Object.assign(S.param.quat4, { w: 0.3 }); go(); }
  for (const kind of ['m', 'j']) {
    const c = [-0.4, 0.3, 0.1], size = 33, stops = 48, t0 = performance.now(), g = T.columns(kind, c, { size, half: 2, stops, maxK: 16 }), ms = performance.now() - t0;
    if (!g) { rows.push([id, kind, 'no answer']); continue; }
    let differ = 0, hair = 0, n = 0;
    for (let r = 0; r < size; r++) for (let q = 0; q < size; q++) {
      const x = q * 4 / (size - 1) - 2, y = 2 - r * 4 / (size - 1), hc = Math.sqrt(Math.max(4 - x * x - y * y, 0)); let m = 0, m2 = 0, m3 = 99;
      for (let i = 0; i < stops; i++) { const z = hc * (2 * (i + 0.5) / stops - 1); m = Math.max(m, LAB.learnShape3d.out([x, y, z], kind, c, 16));
        // (the same line asked a hair to either side: the card works in 32-bit numbers)
        const a = LAB.learnShape3d.out([x * (1 - 1e-5), y * (1 - 1e-5), z * (1 - 1e-5)], kind, c, 16), b = LAB.learnShape3d.out([x * (1 + 1e-5), y * (1 + 1e-5), z * (1 + 1e-5)], kind, c, 16); m2 = Math.max(m2, a, b); m3 = Math.min(m3, Math.max(a, b)); }
      n++; if (g[r * size + q] !== m) { differ++; if (g[r * size + q] <= m2) hair++; }
    }
    rows.push([id, kind, 'lines ' + n, 'differ ' + differ, 'of those within a hair ' + hair, Math.round(ms) + ' ms']);
  }
  if (id === 'quat4') { Object.assign(S.param.quat4, { w: 0 }); go(); }
}
T.dispose(); await approach('mercator');
return rows;
//@
// 7. How long columns() takes at the size the page uses (192 x 192 lines, 192 points each), every approach, Mandelbrot shape.
const T = LAB.learnShape3d.make(), rows = [];
for (const a of LAB.APPROACHES) { await approach(a.id); T.columns('m', [0, 0, 0], { size: 8, stops: 4, maxK: 16 }); const ts = []; for (let i = 0; i < 3; i++) { const t0 = performance.now(); T.columns('m', [0, 0, 0], { size: 192, half: 2, stops: 192, maxK: 16 }); ts.push(performance.now() - t0); } rows.push(a.id + ' ' + ts.map(t => Math.round(t)).join('/')); }
T.dispose(); await approach('mercator');
return rows;
//@
// 9. "Nothing is left to see" in 3D against the arithmetic: for nine settings, at every step, does the page say it,
// and how many points of a grid of the big ball (0.1 apart, 33,401 points, the module's out()) are still in?
// wrong: the page says nothing is left while more than three grid points are (three or fewer: points on a skin).
const cases = [['mercator', 2, 'j', [7, 0, 0]], ['mercator', 1, 'j', [-0.4, 0.3, 0]], ['mercator', -2, 'm', [0, 0, 0]], ['mercator', -2, 'j', [-0.4, 0.3, 0]], ['fold', -2, 'j', [-0.4, 0.3, 0]],
  ['lathe', 2, 'j', [2.5, 2.5, 0]], ['quat4', 2, 'j', [-0.4, 0.3, 0], { w: 1.5 }], ['alongonce', 2, 'j', [1.2, 1.2, 0.5]], ['mercator', 2, 'j', [0.6, 0.6, 0]], ['turnalong', 2, 'j', [0.9, 0.2, 0.6]]];
const rows = []; let wrong = 0;
for (const [id, n, kind, c, dial] of cases) {
  await approach(id); if (dial) Object.assign(S.param[id], dial); S.n = n; go(); L.shape.set({ kind, space: 3, c, pos: 0 }); await rest(500);
  const hist = new Array(18).fill(0);
  for (let i = 0; i <= 40; i++) for (let j = 0; j <= 40; j++) for (let m = 0; m <= 40; m++) { const p = [-2 + i * 0.1, -2 + j * 0.1, -2 + m * 0.1]; if (Math.hypot(...p) > 2) continue; hist[LAB.learnShape3d.out(p, kind, kind === 'm' ? p : c, 16)]++; }
  const left = k => hist.slice(k + 1).reduce((a, b) => a + b, 0), says = [], bad = [];
  for (let k = 1; k <= 16; k++) { L.shape.set({ pos: k }); const s = L.shape.state(); const claim = /nothing is left/.test(s.sentence); if (claim) says.push(k); if (claim && left(k) > 3) { bad.push(k + ' (' + left(k) + ' points)'); wrong++; } }
  const firstEmpty = [...Array(17).keys()].find(k => k > 0 && left(k) === 0);
  rows.push({ what: id + (dial ? ' ' + JSON.stringify(dial) : '') + ', power ' + n + ', ' + kind + ', c ' + c, pageSaysNothingLeftFromStep: says[0] || null, gridEmptyFromStep: firstEmpty === undefined ? null : firstEmpty, gridPointsLeftAfter1_4_8_16: [1, 4, 8, 16].map(left), wrong: bad });
  if (dial) { for (const key in dial) S.param[id][key] = 0; }
}
S.n = 2; go(); await approach('mercator'); L.shape.set({ kind: 'm', space: 2, c: [-0.4, 0.3, 0], pos: 0 });
return { wrong, rows };
//@
// 8. The graphics taken away and given back, on an empty 3D Julia shape: the sentence before, while gone, and after.
L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0], pos: 3 }); let s = await rest(900); const before = said().say;
const cv = document.querySelector('canvas.learn-shape-gl'), ext = cv.getContext('webgl2').getExtension('WEBGL_lose_context');
ext.loseContext(); await sleep(400); const gone = { say: said().say, note: $('learnShapeNote').hidden ? '' : $('learnShapeNote').textContent };
ext.restoreContext(); await sleep(900); s = await rest(600);
const after = said().say; L.shape.set({ kind: 'm', space: 2, c: [-0.4, 0.3, 0], pos: 0 });
return { before, whileGone: gone, after, aboveAfter: s.above.map(a => [a.kind, a.done, a.left && a.left.slice(0, 4).join(' ')]) };
