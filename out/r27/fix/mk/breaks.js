// Round 27, fixer: part C of verdict.js counts a point of the probe sphere as "inside a ball" when ballsInside says
// so with 60 rounds, and ballsInside (like tree.py) calls a point that is still undecided after its rounds inside.
// At t = 1 that part reports a few breaks on the fixed page. Are they balls? The same random points (same generator,
// same order of draws), and for every probe that 60 rounds call inside: the recipe again with 5000 rounds, where
// "inside" means that a wall was reached.
const S3 = Math.sqrt(3), K2 = 1.05;
const near = (g, x, y) => { if (g === 2) return [Math.round(x), 0]; if (g === 0) return [Math.round(x), Math.round(y)];
  const b0 = Math.round(y / (S3 / 2)); let best = null, bd = Infinity;
  for (let j = -1; j <= 1; j++) { const b = b0 + j, a = Math.round(x + b / 2), px = a - b / 2, py = b * S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py); if (d < bd) { bd = d; best = [px, py]; } }
  return best; };
const sure = (g, t, x, y, z, R) => { const top = 2 * t, ux = y, uy = z, uz = x - K2 / 2, d = Math.max(ux * ux + uy * uy + uz * uz, 1e-300); let mx = K2 * ux / d, my = K2 * uy / d, mz = 1 + K2 * uz / d;
  for (let i = 0; i < R; i++) { if (mz < 0 || mz > top) return [1, i]; const n = near(g, mx, my); mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / rb; mx *= s; my *= s; mz *= s; } else if (rt < 1) { const s = 1 / rt; mx *= s; my *= s; mz = top + (mz - top) * s; } else return [0, i + 1]; }
  return [2, R]; };
let seed = 2027;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
for (const grid of [0, 1, 2]) for (const t of [1, 1.4, 2.5]) for (const flat of [true, false]) { rnd(); rnd(); if (!flat) rnd(); }   // part A's draws
const dirs = [];
for (let i = 0; i < 240; i++) { const u = 2 * rnd() - 1, a = 2 * Math.PI * rnd(), s = Math.sqrt(1 - u * u); dirs.push([s * Math.cos(a), s * Math.sin(a), u]); }
const out = [];
for (const grid of [0, 1, 2]) for (const t of [1, 1.4, 2.5]) {
  const opts = { t, grid, rounds: 60 };
  const r = { grid, t, outsidePoints: 0, pointsWithAProbeThat60RoundsCallInside: 0, ofThoseProbes: { aWallIsReached: 0, outsideAfterMoreRounds: 0, stillUndecidedAfter5000: 0 }, roundsTheOutsideOnesNeeded: [] };
  for (let k = 0; k < 3000; k++) {
    const p = [-1.9 + 3.8 * rnd(), -1.4 + 2.8 * rnd(), -1.4 + 2.8 * rnd()];
    if (t !== 1) continue;
    const d = L.ballsEstimate(p[0], p[1], p[2], opts);
    if (!(d > 0)) continue;
    r.outsidePoints++;
    let any = false;
    for (const v of dirs) { const q = [p[0] + 0.999 * d * v[0], p[1] + 0.999 * d * v[1], p[2] + 0.999 * d * v[2]];
      if (!L.ballsInside(q[0], q[1], q[2], opts)) continue;
      any = true; const s = sure(grid, t, q[0], q[1], q[2], 5000);
      if (s[0] === 1) r.ofThoseProbes.aWallIsReached++; else if (s[0] === 0) { r.ofThoseProbes.outsideAfterMoreRounds++; r.roundsTheOutsideOnesNeeded.push(s[1]); } else r.ofThoseProbes.stillUndecidedAfter5000++; }
    if (any) r.pointsWithAProbeThat60RoundsCallInside++;
  }
  if (t === 1) out.push(r);
}
return JSON.stringify(out);
