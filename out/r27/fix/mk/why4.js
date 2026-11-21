// Round 27, fixer: the stray stops that are left at 100 % (t = 1). For stops of pick() that stand further than 2.5 px
// from every ball the search meets and not beside a region that only the depth calls solid: the marcher of GL_TAIL
// written out on the twin's two numbers (ray step 0.8, hold 1.25 thresholds, 600 steps, the page's 16 rounds), along
// the same ray. How does that ray end, and what stands at the place where the page stopped?
const t = 1, g = 0, rounds = 16, c = [-1.25, 0.5, 0.30, [0.525, 0, 0]];
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame(); L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice();
go(); await settle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h, bound = S.view.bound;
const o300 = { t, grid: g, rounds: 300, parts: true }, oPage = { t, grid: g, rounds, parts: true };
const open = [];
for (let j = 0; j < h && open.length < 40; j += 4) for (let i = 0; i < w && open.length < 40; i += 4) {
  const p = L.pick(i + 0.5, j + 0.5); if (!p) continue;
  const sd = Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]), one = pix * sd, met = L.ballsEstimate(p[0], p[1], p[2], o300)[0] / one;
  if (!(met > 2.5)) continue;
  const rd = [(p[0] - ro[0]) / sd, (p[1] - ro[1]) / sd, (p[2] - ro[2]) / sd]; let dep = false;
  for (let k = 0; k <= 3 && !dep; k += 0.25) { const q = [p[0] + k * one * rd[0], p[1] + k * one * rd[1], p[2] + k * one * rd[2]]; if (L.ballsInside(q[0], q[1], q[2]) && !L.ballsInside(q[0], q[1], q[2], { t, grid: g, rounds: 3000 })) dep = true; }
  if (!dep) open.push({ rd, sd, met, p });
}
const march = (rd, K, STEPS, FLOOR) => {
  const bb = rd[0] * ro[0] + rd[1] * ro[1] + rd[2] * ro[2], hh = bb * bb - (ro[0] * ro[0] + ro[1] * ro[1] + ro[2] * ro[2]) + bound * bound;
  let s = Math.max(-bb - Math.sqrt(hh), 0); const sMax = -bb + Math.sqrt(hh);
  let inFloor = 0, n = 0, d = 0, e = 0;
  for (n = 1; n <= STEPS; n++) {
    e = Math.max(pix * s, 1e-7);
    const bf = L.ballsEstimate(ro[0] + rd[0] * s, ro[1] + rd[1] * s, ro[2] + rd[2] * s, oPage);
    if (bf[0] < 0) return { end: 'landed in solid (at the depth of the page)', n, s, inFloor };
    if (bf[1] < FLOOR * e) inFloor++;
    d = Math.min(bf[0], Math.max(bf[1], FLOOR * e));
    if (d < e) return { end: 'a ball the search meets within a threshold', n, s, inFloor };
    s += d * K;
    if (s > sMax) return { end: 'left the picture', n, s, inFloor };
  }
  return { end: d < 3.8 * e ? 'out of steps, counted as a hit' : 'out of steps, far', n: STEPS, s, inFloor };
};
const tally = {}, some = [];
for (const o of open) {
  const r = march(o.rd, 0.8, 600, 1.25), at = L.ballsEstimate(o.p[0], o.p[1], o.p[2], oPage), one = pix * o.sd;
  const key = r.end; tally[key] = (tally[key] || 0) + 1;
  if (some.length < 12) some.push({ ends: r.end, steps: r.n, stepsInTheHold: r.inFloor, writtenOutStopsAt: +r.s.toFixed(5), pageStopsAt: +o.sd.toFixed(5), metPx300: +o.met.toFixed(1), atThePagesStop_bestPx16: +(at[0] / one).toFixed(2), freePx16: +(at[1] / one).toFixed(2), trueSolidWithin: (() => { for (let rr = 0.25; rr <= 12; rr += 0.25) for (let k = 0; k < 60; k++) { const u = 2 * ((k * 0.61803) % 1) - 1, a = 2.39996 * k, s2 = Math.sqrt(1 - u * u); if (L.ballsInside(o.p[0] + rr * one * s2 * Math.cos(a), o.p[1] + rr * one * s2 * Math.sin(a), o.p[2] + rr * one * u, { t, grid: g, rounds: 3000 })) return rr; } return 99; })() });
}
return JSON.stringify({ openStopsLookedAt: open.length, tally, some });
