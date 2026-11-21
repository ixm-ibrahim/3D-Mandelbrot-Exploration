// slice() (the picture's own program, on the graphics card) against out() (JavaScript, MATH / CARRY), point for point.
// For every point that differs: how near is a skin that explains the difference? "hair" is the smallest of the tried
// distances h at which the card's value lies between the least and the greatest value JavaScript finds at the point
// and at its 26 neighbours h away.
// window.T3_SLICE_CASES (set by the action before this file) overrides the list of cases.
const T = window.T3, L = T.L, M = T.M, V = T.view;
const SIZE = 257, HALF = 2, MAXK = 16;      // 257 points on [-2, 2]: the spacing is 1/64, exact in both arithmetics
const RABBIT = [-0.122561, 0.744862, 0];
const IDS = ['mercator', 'fold', 'lathe', 'turnalong', 'alongonce', 'pulledplane', 'bulb', 'split'];
let cases = window.T3_SLICE_CASES;
if (!cases) {
  cases = [];
  for (const id of IDS) for (const z of [0, 0.3]) {
    cases.push({ id, n: 2, kind: 'm', c: [0, 0, 0], z });
    cases.push({ id, n: 2, kind: 'j', c: [-1, 0, 0], z });
    cases.push({ id, n: 2, kind: 'j', c: RABBIT, z });
  }
  for (const id of ['mercator', 'lathe']) for (const z of [0, 0.3]) {
    cases.push({ id, n: 3, kind: 'm', c: [0, 0, 0], z });
    cases.push({ id, n: 3, kind: 'j', c: [-0.3, 0.2, 0.1], z });
  }
}
const DIRS = [];
for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) if (a || b || c) DIRS.push([a, b, c]);
const HAIRS = [1e-9, 1e-7, 1e-6, 1e-5, 3e-5, 1e-4, 1e-3, 1e-2];
const rows = [];
const n0 = L.S.n, ap0 = L.S.approach;
for (const cs of cases) {
  T.setAp(cs.id, cs.params); L.S.n = cs.n;
  if (cs.abs) L.S.abs = cs.abs; if (cs.flip) L.S.flip = cs.flip;
  const opt = { z: cs.z, half: HALF, size: SIZE, maxK: MAXK };
  const t0 = performance.now();
  const g = V.slice(cs.kind, cs.c, opt);
  const tg = performance.now() - t0;
  const row = { id: cs.id, n: cs.n, kind: cs.kind, c: cs.c.join(','), z: cs.z, points: SIZE * SIZE, differ: 0, hairs: {}, worst: null, inBall: 0, kept: 0, ms: Math.round(tg) };
  if (cs.params) row.params = JSON.stringify(cs.params);
  if (cs.abs || cs.flip) row.mods = JSON.stringify([cs.abs || 0, cs.flip || 0]);
  if (!g) { row.error = 'slice gave nothing: ' + M.note(); rows.push(row); continue; }
  const hist = new Array(MAXK + 2).fill(0);
  for (let r = 0; r < SIZE; r++) for (let x = 0; x < SIZE; x++) {
    const p = V.slicePoint(r, x, opt), js = M.out(p, cs.kind, cs.c, MAXK), gv = g[r * SIZE + x];
    hist[js]++;
    if (js > 0) row.inBall++;
    if (js === MAXK + 1) row.kept++;
    if (js === gv) continue;
    row.differ++;
    // out() only changes across a skin, and to get from one value to another every skin between them is crossed. So
    // if the card's value lies between the least and the greatest value JavaScript finds within h of the point, the
    // point is within h of the skin that explains the difference.
    let hair = 'none';
    for (const h of HAIRS) {
      let lo = js, hi = js;
      for (const d of DIRS) { const v = M.out([p[0] + h * d[0], p[1] + h * d[1], p[2] + h * d[2]], cs.kind, cs.c, MAXK); if (v < lo) lo = v; if (v > hi) hi = v; }
      if (gv >= lo && gv <= hi) { hair = String(h); break; }
    }
    row.hairs[hair] = (row.hairs[hair] || 0) + 1;
    const rank = hair === 'none' ? 1 : +hair;
    if (!row.worst || rank > row.worst.rank) row.worst = { rank, p: p.map(v => +v.toFixed(6)), js, gpu: gv, hair };
  }
  row.hist = hist.join(' ');
  rows.push(row);
  if (cs.abs) L.S.abs = [0, 0, 0]; if (cs.flip) L.S.flip = [0, 0];
  if (cs.params) { const a = L.APPROACHES[L.S.approach]; (a.params || []).filter(s => s.key !== undefined).forEach(s => { L.S.param[a.id][s.key] = s.def; }); }
}
L.S.n = n0; L.S.approach = ap0;
return rows;
