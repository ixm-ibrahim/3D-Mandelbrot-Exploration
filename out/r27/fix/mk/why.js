// Round 27, fixer: why do rays stop nowhere at t = 1? The marcher of GL_TAIL written out in JavaScript on the twin's
// two numbers (ballsEstimate with parts), for rays that pick() says stop nowhere. Where do the steps go?
const t = 1, g = 0, rounds = 16, c = [-1.25, 0.5, 0.30, [0.525, 0, 0]];
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame(); L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice();
go(); await settle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h, bound = S.view.bound;
const ray = (px, py) => { const ux = (2 * px - w) / h * fov, uy = (2 * (h - py) - h) / h * fov;
  const rd = [0, 1, 2].map(k => b.right[k] * ux + b.up[k] * uy + b.f[k]), n = Math.hypot(rd[0], rd[1], rd[2]); return rd.map(x => x / n); };
const miss = [];
for (let j = 0; j < h && miss.length < 4000; j += 8) for (let i = 0; i < w; i += 8) if (!L.pick(i + 0.5, j + 0.5)) miss.push([i + 0.5, j + 0.5]);
const opts = { t, grid: g, rounds, parts: true };
const march = (rd, K, STEPS, FLOOR) => {
  const bb = rd[0] * ro[0] + rd[1] * ro[1] + rd[2] * ro[2], hh = bb * bb - (ro[0] * ro[0] + ro[1] * ro[1] + ro[2] * ro[2]) + bound * bound;
  let s = Math.max(-bb - Math.sqrt(hh), 0); const sMax = -bb + Math.sqrt(hh);
  let inFloor = 0, n = 0, d = 0, e = 0, lastFree = 0, lastBest = 0;
  for (n = 1; n <= STEPS; n++) {
    e = Math.max(pix * s, 1e-7);
    const bf = L.ballsEstimate(ro[0] + rd[0] * s, ro[1] + rd[1] * s, ro[2] + rd[2] * s, opts);
    lastBest = bf[0]; lastFree = bf[1];
    if (bf[0] < 0) return { end: 'inside', n, s, inFloor };
    if (bf[1] < FLOOR * e) inFloor++;
    d = Math.min(bf[0], Math.max(bf[1], FLOOR * e));
    if (d < e) return { end: 'hit', n, s, inFloor };
    s += d * K;
    if (s > sMax) return { end: 'left', n, s, inFloor };
  }
  return { end: d < 3.8 * e ? 'out of steps, near' : 'out of steps, far', n: STEPS, s, inFloor, dOverE: d / e, freeOverE: lastFree / e, bestOverE: lastBest / e };
};
const out = { rays: miss.length, cases: [] };
for (const [K, STEPS, FLOOR] of [[0.5, 300, 2], [0.8, 300, 1.25], [1, 300, 1.25], [0.8, 600, 1.25], [1, 600, 1.25], [0.5, 600, 2], [0.5, 2000, 2], [1, 2000, 1.25]]) {
  const tally = {}, fl = [], far = [];
  for (const [px, py] of miss.slice(0, 400)) {
    const r = march(ray(px, py), K, STEPS, FLOOR);
    tally[r.end] = (tally[r.end] || 0) + 1;
    fl.push(r.inFloor / r.n);
    if (r.end === 'out of steps, far') far.push([+r.s.toFixed(4), +r.dOverE.toFixed(1), +r.freeOverE.toFixed(1), +r.bestOverE.toFixed(1), r.inFloor]);
  }
  fl.sort((a, b2) => a - b2);
  out.cases.push({ K, STEPS, FLOOR, tally, shareOfStepsInFloorZoneMedian: +fl[fl.length >> 1].toFixed(2), someFar: far.slice(0, 6) });
}
return JSON.stringify(out);
