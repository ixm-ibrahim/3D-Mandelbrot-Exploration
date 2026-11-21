// Check 4: dragging the diamond changes the Julia picture live. Scripted pointer events on the picture's canvas.
// Also the times of a redraw: while the diamond is held (coarse numbers), at rest (fine numbers), and when only
// the slider moves (the kept numbers are coloured again).
//@
const s = await shapeOn({ kind: 'j', space: 2, pos: 6, c: [-0.4, 0.3, 0] });
const cv = $('learnShapeCanvas'), g = cv.getContext('2d');
// how much of the canvas is body colour, and a fingerprint of it
window.__ink = () => { const d = g.getImageData(0, 0, cv.width, cv.height).data; let n = 0, h = 0; for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 200 && d[i] > 180 && d[i + 1] > 140 && d[i + 2] < 130) { n++; h = (h * 31 + i) >>> 0; } return n + ':' + h; };
return { diamond: s.diamonds[0], c: s.c, body: window.__ink(), hint: $('learnHint').textContent };
//@ sleep=0.3 shot=out/r26/core/drag-0-before.png clip=#stage
//@
// take hold of the diamond and carry it, a few pixels a frame, towards the place of c = -1
const cv = $('learnShapeCanvas'), s0 = L.shape.state(), d0 = s0.diamonds[0], P = s0.panes[0], sc = 0.21 * Math.min(P.w, P.h);
const goal = [P.x + P.w / 2 + (-1) * sc, P.y + P.h / 2 - 0 * sc], log = [], seen = new Set();
ptr(cv, 'pointerdown', d0[0], d0[1]);
const steps = 24;
for (let i = 1; i <= steps; i++) {
  const x = d0[0] + (goal[0] - d0[0]) * i / steps, y = d0[1] + (goal[1] - d0[1]) * i / steps;
  ptr(cv, 'pointermove', x, y);
  await frame(); await frame();
  const body = window.__ink(), st = LAB.learn.shape;   // read without state(), which would ask for the fine picture
  seen.add(body);
  const raw = { c: $('learnShape-cxNum') ? $('learnShape-cxNum').value : null };
  log.push([i, body.split(':')[0], raw.c]);
  if (i === 12) window.__mid = true;
}
// still held: what quality is on show, and what the redraw took
const held = L.shape.state();
return { movesSent: steps, differentPictures: seen.size, heldQuality: held.quality, heldMs: held.ms, cWhileHeld: held.c, log: log.filter((x, i) => i % 4 === 3) };
//@ shot=out/r26/core/drag-1-held.png clip=#stage
//@
const cv = $('learnShapeCanvas'), s0 = L.shape.state(), d = s0.diamonds[0];
ptr(cv, 'pointerup', d[0], d[1]);
await sleep(350);
const s = L.shape.state();
if (Math.abs(s.c[0] + 1) > 0.011 || Math.abs(s.c[1]) > 0.011) fail('the diamond should have arrived at c = -1: ' + s.c);
if (s.quality !== 'still' || s.ms.mapDens !== 2) fail('at rest the fine picture should be on show: ' + JSON.stringify([s.quality, s.ms]));
return { c: s.c, quality: s.quality, ms: s.ms, dials: [$('learnShape-cxNum').value, $('learnShape-cyNum').value], sentence: s.sentence };
//@ sleep=0.3 shot=out/r26/core/drag-2-released.png clip=#stage
//@
// Both: taking the diamond in the LEFT picture (the Mandelbrot shape) changes the RIGHT one (the Julia shape)
const s0 = L.shape.set({ kind: 'both', pos: 16 });
const cv = $('learnShapeCanvas'), d0 = s0.diamonds[0], P = s0.panes[0], sc = 0.21 * Math.min(P.w, P.h);
const before = window.__ink();
const goal = [P.x + P.w / 2 + (-0.1226) * sc, P.y + P.h / 2 - 0.7449 * sc], seen = new Set();
ptr(cv, 'pointerdown', d0[0], d0[1]);
for (let i = 1; i <= 16; i++) { ptr(cv, 'pointermove', d0[0] + (goal[0] - d0[0]) * i / 16, d0[1] + (goal[1] - d0[1]) * i / 16); await frame(); await frame(); seen.add(window.__ink()); }
const held = L.shape.state();
ptr(cv, 'pointerup', goal[0], goal[1]); await sleep(350);
const s = L.shape.state();
return { differentPictures: seen.size, heldMs: held.ms, c: s.c, diamonds: s.diamonds, restMs: s.ms };
//@ sleep=0.3 shot=out/r26/core/drag-3-both-rabbit.png clip=#stage
//@
// the times, each the middle one of many: (a) the slider moves (numbers kept), (b) c moves while held (coarse
// numbers), (c) c moves and rests (fine numbers). Single picture and Both; power 2, 3 and 2.5.
const mid = a => a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)], out = [], t = () => performance.now();
const cv = $('learnShapeCanvas');
for (const [name, n] of [['power 2', 2], ['power 3', 3], ['power 2.5 (polar form)', 2.5]]) {
  S.n = n; go(); await sleep(400);
  for (const kind of ['j', 'both']) {
    L.shape.set({ kind, c: [-0.4, 0.3, 0], pos: 3 }); await sleep(400); L.shape.state();
    // (a) the slider: every call draws at once
    const a = [], aFill = [];
    for (let i = 0; i < 40; i++) { const t0 = t(); L.shape.goto(3 + i * 0.07); a.push(t() - t0); aFill.push(L.shape.state().ms.frame); }
    // (b) held: pointer moves, one redraw a frame
    const s0 = L.shape.state(), d0 = s0.diamonds[s0.diamonds.length - 1], b = [], bMap = [];
    ptr(cv, 'pointerdown', d0[0], d0[1]);
    for (let i = 1; i <= 20; i++) { ptr(cv, 'pointermove', d0[0] + 3 * i, d0[1] + 2 * i); await frame(); await frame(); const st = LAB.learn.shape.state(); b.push(st.ms.frame); bMap.push(st.ms.mapLast); }
    const dens = L.shape.state().ms.mapDens, samples = L.shape.state().ms.mapSamples;
    ptr(cv, 'pointerup', d0[0] + 60, d0[1] + 40); await sleep(350);
    // (c) at rest: a new c, drawn fine at once
    const c = [], cMap = [];
    for (let i = 0; i < 9; i++) { await sleep(300); const t0 = t(); const st = L.shape.set({ c: [-0.4 + 0.03 * i, 0.3, 0] }); c.push(t() - t0); cMap.push(st.ms.mapLast); }
    const st = L.shape.state();
    out.push({ what: name + ', ' + (kind === 'j' ? 'Julia shape alone' : 'Both'), sliderRedrawMs: +mid(a).toFixed(2), sliderRedrawWorstMs: +Math.max(...a).toFixed(2),
      heldRedrawMs: +mid(b).toFixed(2), heldNumbersMs: +mid(bMap).toFixed(2), heldSamples: samples, heldSamplesToAPixel: dens,
      restRedrawMs: +mid(c).toFixed(2), restNumbersMs: +mid(cMap).toFixed(2), restSamples: st.ms.mapSamples, restSamplesToAPixel: st.ms.mapDens });
  }
}
S.n = 2; go(); await sleep(200);
const P = L.shape.state().panes;
return { stage: [$('stage').clientWidth, $('stage').clientHeight], dpr: devicePixelRatio, rows: out };
