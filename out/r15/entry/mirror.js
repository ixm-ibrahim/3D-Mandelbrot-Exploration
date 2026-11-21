// Round 15, entry: is the rule mirror-symmetric in z? F(x, y, -z) against the mirror image of F(x, y, z), 20,000 directions, powers 2 to 5.
// Also: how far apart the direction rule sends two directions that sit on either side of the plane z = 0 (sign of z out),
// and what share of all directions land on the other side of the plane.
const M = window.squaringLab.MATH; let seed = 77;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const out = [];
for (const n of [2, 3, 4, 5]) {
  let worst = 0, sum = 0, flip = 0, N = 20000;
  for (let i = 0; i < N; i++) {
    const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * Math.PI, h = Math.sqrt(1 - z * z), v = [h * Math.cos(a), h * Math.sin(a), z];
    const f = M.sqpillow(v, n, {}), g = M.sqpillow([v[0], v[1], -v[2]], n, {});
    const d = Math.hypot(f[0] - g[0], f[1] - g[1], f[2] + g[2]);
    worst = Math.max(worst, d); sum += d;
    if (f[2] * z < 0) flip++;
  }
  out.push({ power: n, mirrorWorst: worst, mirrorMean: sum / N, shareLandingOnTheOtherSideOfThePlane: flip / N });
}
return JSON.stringify(out);
