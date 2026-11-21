// Round 27, final, number 1: verdicts of the page against out/r25/klein/tree.py, square grid, t = 1.4.
// (a) the JavaScript twin (ballsInside) at 20000 random points of the box (-1.8..1.8, -1.3..1.3, -1.3..1.3) and at
//     20000 random points of the flat cut (z = 0), with the page's own depth (nothing passed for rounds) and 40 rounds;
// (b) the shader, read through sampleSlice from the program the picture is drawn with, at the page's own depth:
//     the flat view on a 142 x 142 grid (20164 points, the grid moved by a random offset), and in space on twenty
//     32 x 32 grids at random heights (20480 points).
// The points and the verdicts go back to Python, which asks tree.py.
if (typeof L.ballsInside !== 'function') fail('no ballsInside on the handle');
if (typeof L.sampleSlice !== 'function') fail('no sampleSlice on the handle');
let a = 0x9e3779b9 ^ 20261120;                                   // mulberry32, my own seed
const rnd = () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const out = { asOpened: null, twin: {}, shader: [] };
$('ap-balls').click(); await settle();                           // the user's way in: the row in the Approach list
out.asOpened = { mode: S.mode, group: S.k.group, bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit, flat: S.flat, status: $('status').textContent };
if (!(S.mode === 'k' && S.k.group === 1 && S.k.bt === 1.4 && S.k.bgrid === 0)) fail('the row did not give Balls on balls with its defaults: ' + JSON.stringify(out.asOpened));
const r5 = x => +x.toFixed(12);
// (a) the twin
const N = 20000, P = [];
for (let i = 0; i < N; i++) P.push([r5(-1.8 + 3.6 * rnd()), r5(-1.3 + 2.6 * rnd()), r5(-1.3 + 2.6 * rnd())]);
out.twin.pts = P;
const bits = (flat, o) => { let s = ''; for (const p of P) s += L.ballsInside(p[0], p[1], flat ? 0 : p[2], o) ? '1' : '0'; return s; };
out.twin.spaceOwnDepth = bits(false, { t: 1.4, grid: 'square' });
out.twin.flatOwnDepth = bits(true, { t: 1.4, grid: 'square' });
out.twin.space40 = bits(false, { t: 1.4, grid: 'square', rounds: 40 });
out.twin.flat40 = bits(true, { t: 1.4, grid: 'square', rounds: 40 });
// (b) the shader, as the page stands (depth S.k.bit)
S.flat = false; S.cutOn = false; go(); await settle();
const side = 3.6;
const slice = async (n, z) => {
  const cx = 0.02 * (rnd() - 0.5), cy = 0.02 * (rnd() - 0.5);
  const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, cx, cy, side, z, n); L.releaseSnapshot(snap);
  if (!arr) fail('sampleSlice gave nothing');
  let s = ''; const ds = [];
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const d = arr[4 * (j * n + i) + 3]; s += !(d > 0) ? '1' : '0'; ds.push(+d.toPrecision(6)); }
  out.shader.push({ n, z: r5(z), cx: r5(cx), cy: r5(cy), side, depth: S.k.bit, bits: s, d: ds });
};
await slice(142, 0);
for (let k = 0; k < 20; k++) { await slice(32, r5(-1.3 + 2.6 * rnd())); await sleep(5); }
return JSON.stringify(out);
