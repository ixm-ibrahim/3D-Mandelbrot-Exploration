// Step 1: the JavaScript twin at 20000 random points for each of nine settings (three grids; t = 1, 1.4, 2.5).
// Returns the points' seed and, for each setting, the verdicts as a string of 0 and 1, for tree.py to be compared with.
if (typeof L.ballsInside !== 'function') fail('no ballsInside on the handle');
let seed = 12345;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const N = 20000, pts = [];
for (let i = 0; i < N; i++) pts.push([-1.8 + 3.6 * rnd(), -1.3 + 2.6 * rnd(), -1.3 + 2.6 * rnd()]);
const out = { n: N, pts: pts.map(p => p.map(x => +x.toFixed(12))), cases: [] };
for (const grid of ['square', 'hex', 'line']) for (const t of [1, 1.4, 2.5]) for (const flat of [true, false]) {
  let s = '', inside = 0;
  for (const p of out.pts) { const v = L.ballsInside(p[0], p[1], flat ? 0 : p[2], { t, grid, rounds: 40 }); s += v ? '1' : '0'; if (v) inside++; }
  out.cases.push({ grid, t, flat, inside, bits: s });
}
return JSON.stringify(out);
