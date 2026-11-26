// Every body's own line, for the entries "Two planes, about every body's own line" and "Two planes, about the middle
// body's own line" (10-approaches.js), and at the end of the file the middle body's two pinch points from c alone,
// for the entry "Two planes, between the middle body's pinch points".
//
// A Julia set of z² + c whose c has a cycle of bodies is made of bodies that hang on one another at pinch points.
// Each body has a line of its own: through its middle, from the point where it hangs on its parent (its root) to
// the point opposite. The flat rule lays each line onto another one, and the lines of the bodies of the cycle onto
// each other in turn. The first entry folds a point about the nearest such line, as "two planes" folds it about the
// x-axis. The second folds about the line of the middle body alone, the body that holds 0: the rule lays every other
// body onto that one sooner or later, and so carries the fold to them itself.
//
// The lines are found from the flat rule alone (lnBuild):
//   1. The cycle the orbit of 0 settles on, and of its points the one in the body that holds 0 (lnCycle).
//   2. That body's root: the one point of its edge that the cycle's own number of steps brings back to itself
//      (lnRoot, by Newton's method from starts round the body).
//   3. An arm in each body of the cycle, from its root to its middle: a straight stretch, taken back through the
//      rule until it stops changing. A step back pushes every point away from the middle, so the far end is put back
//      on the middle each time: beside the middle an arm is all but straight.
//   4. The middle body's line is its arm and the arm's mirror image through 0. Every step back from a line gives the
//      lines of the two bodies that land on its body. The body that holds c is the one body the rule lays two bodies
//      onto at once, so its line is not taken back: that would lay a second line across the middle body.
// Each line is then a row of points LN_STEP apart, each with the line's direction there and the body's half-width
// (how far one can go square to the line, on the nearer side, before leaving the flat set). Both ends of a line lie
// on the body's edge, so the half-width is nothing there, and it grows no faster than the line runs. Along a long
// line it is evened out, since the fold ends where the reach does and an uneven reach leaves a ragged end.
//
// The fold (lnAbout) wants the nearest point of a line, and the shader cannot search for it. It is handed a map
// (a table's idx): for every cell of a grid over the flat plane, a point near the cell on a big body's line, on a
// middle-sized body's and on a small body's. From that point it walks along the line to the point beside it and
// drops onto the stretch between two points, so the foot moves without a jump as the point moves.
// A point is folded about a big body's line first, then a middle-sized body's, then a small one's (lnFold), so a
// point over a bud that the first fold lays beside a body is folded again about the bud's own line.
// A table's idx and dat are the textures the shader reads (lnUniforms). lnFold is the same fold in JavaScript, from
// the same two arrays.
const LN_GRID = 768, LN_HALF = 2, LN_STEP = 0.006, LN_DEPTH = 9, LN_PTS = 96, LN_NONE = 65535, LN_WIDE = 1024;
const LN_BIG = 0.12, LN_MID = 0.035;          // a line is of a big body, a middle-sized one or a small one by its widest half-width
const LN_SLACK = 0.02;                        // how much nearer than the map's point a line's nearest point can be
// A table's dat is a picture LN_WIDE wide. The points fill its upper rows (x, y, direction). The same places in its
// lower rows hold the half-width there, the numbers of the first and the last point of the point's line, and the
// gap between two points of that line.
const lnBlank = () => ({ key: '', ver: 0, on: false, count: 0, period: 0, why: '', idx: new Uint16Array(4).fill(LN_NONE), dat: new Float32Array(8 * LN_WIDE), rows: 1, g: 1 });
const LN = { all: lnBlank(), mid: lnBlank() };  // a table for each entry: every body's line, and the middle body's alone
const LN_GL = new WeakMap();                    // for each graphics context: its two textures, and the table and version they hold

const lnStill = (x, y, cx, cy, n) => {          // does the flat orbit stay within reach for n steps
  for (let i = 0; i < n; i++) { const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t; if (x * x + y * y > 16) return false; }
  return true;
};
// The cycle the orbit of 0 settles on: its length p, its points m (m[0] in the body that holds 0), and A, half the
// second slope of p steps at m[0], whose reciprocal is about the half-width of that body. Nothing when the orbit
// leaves, or has not settled on a cycle of at most 64 points.
function lnCycle(cx, cy) {
  const N = 6000;
  let x = 0, y = 0;
  for (let i = 0; i < N; i++) { const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t; if (x * x + y * y > 16) return null; }
  const x0 = x, y0 = y;
  let p = 0;
  for (let k = 1; k <= 64 && !p; k++) { const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t; if (Math.hypot(x - x0, y - y0) < 1e-10) p = k; }
  if (!p) return null;
  for (let k = (p - (N + p) % p) % p; k > 0; k--) { const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t; }
  const m = [];
  let d1 = [1, 0], d2 = [0, 0];
  for (let k = 0; k < p; k++) {
    m.push([x, y]);
    const s = [d1[0] * d1[0] - d1[1] * d1[1], 2 * d1[0] * d1[1]];
    d2 = [2 * s[0] + 2 * (x * d2[0] - y * d2[1]), 2 * s[1] + 2 * (x * d2[1] + y * d2[0])];
    d1 = [2 * (x * d1[0] - y * d1[1]), 2 * (x * d1[1] + y * d1[0])];
    const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t;
  }
  if (Math.hypot(d1[0], d1[1]) > 0.97) return null;      // hardly pulling: the bodies are about to come apart
  return { p, m, A: [0.5 * d2[0], 0.5 * d2[1]] };
}
// The root of the body that holds 0.
function lnRoot(cx, cy, cyc) {
  const p = cyc.p, [ax, ay] = cyc.m[0], size = clamp(1 / Math.max(Math.hypot(cyc.A[0], cyc.A[1]), 1e-9), 0.01, 2), found = [];
  for (const rad of [0.5, 0.8, 1.1, 1.5, 2.2]) for (let j = 0; j < 16; j++) {
    let x = ax + rad * size * Math.cos(j * PI / 8 + rad), y = ay + rad * size * Math.sin(j * PI / 8 + rad), ok = false, dx = 1, dy = 0;
    for (let it = 0; it < 60 && !ok; it++) {
      let u = x, v = y;
      dx = 1; dy = 0;
      for (let k = 0; k < p; k++) { const e = 2 * (u * dx - v * dy); dy = 2 * (u * dy + v * dx); dx = e; const t = u * u - v * v + cx; v = 2 * u * v + cy; u = t; }
      const gx = u - x, gy = v - y, hx = dx - 1, hy = dy, h2 = hx * hx + hy * hy;
      if (!(h2 > 1e-30) || !isFinite(gx + gy)) break;
      const sx = (gx * hx + gy * hy) / h2, sy = (gy * hx - gx * hy) / h2;
      x -= sx; y -= sy;
      ok = sx * sx + sy * sy < 1e-26;
    }
    if (!ok || Math.hypot(dx, dy) <= 1.0001 || Math.hypot(x - ax, y - ay) < 1e-7) continue;      // it has to push away, and not be the middle
    if (!found.some(f => Math.hypot(f[0] - x, f[1] - y) < 1e-7)) found.push([x, y]);
  }
  // on the body's edge: the straight way from the middle to it stays in the body
  const inBody = r => {
    for (const t of [0.15, 0.3, 0.45, 0.6, 0.75, 0.9]) {
      let x = ax + t * (r[0] - ax), y = ay + t * (r[1] - ay), near = false;
      for (let it = 0; it < 400 && !near; it++) {
        for (let k = 0; k < p; k++) { const e = x * x - y * y + cx; y = 2 * x * y + cy; x = e; }
        if (!(x * x + y * y < 16)) return false;
        near = Math.hypot(x - ax, y - ay) < 1e-3 * size;
      }
      if (!near) return false;
    }
    return true;
  };
  return found.filter(inBody).sort((a, b) => Math.hypot(a[0] - ax, a[1] - ay) - Math.hypot(b[0] - ax, b[1] - ay))[0] || null;
}
// Curves are rows of points, x and y in turn.
function lnLength(z) { let s = 0; for (let i = 2; i < z.length; i += 2) s += Math.hypot(z[i] - z[i - 2], z[i + 1] - z[i - 1]); return s; }
function lnResample(z, m) {
  const n = z.length / 2, s = new Float64Array(n), out = new Float64Array(2 * m);
  for (let i = 1; i < n; i++) s[i] = s[i - 1] + Math.hypot(z[2 * i] - z[2 * i - 2], z[2 * i + 1] - z[2 * i - 1]);
  let j = 0;
  for (let i = 0; i < m; i++) {
    const t = s[n - 1] * i / (m - 1);
    while (j < n - 2 && s[j + 1] < t) j++;
    const f = s[j + 1] > s[j] ? clamp((t - s[j]) / (s[j + 1] - s[j]), 0, 1) : 0;
    out[2 * i] = z[2 * j] + f * (z[2 * j + 2] - z[2 * j]); out[2 * i + 1] = z[2 * j + 1] + f * (z[2 * j + 3] - z[2 * j + 1]);
  }
  return out;
}
// One step back along a curve, with no jump: the square root of (curve − c), its sign carried on from point to
// point. With an anchor, the whole is given the sign that puts its point number `at` nearer the anchor.
function lnBack(z, cx, cy, anchor, at) {
  const n = z.length / 2, w = new Float64Array(2 * n);
  let px = 0, py = 0;
  for (let i = 0; i < n; i++) {
    const u = z[2 * i] - cx, v = z[2 * i + 1] - cy, r = Math.hypot(u, v);
    let sx = Math.sqrt(Math.max(0.5 * (r + u), 0)), sy = Math.sqrt(Math.max(0.5 * (r - u), 0));
    if (v < 0) sy = -sy;
    if (i && (sx - px) * (sx - px) + (sy - py) * (sy - py) > (sx + px) * (sx + px) + (sy + py) * (sy + py)) { sx = -sx; sy = -sy; }
    w[2 * i] = px = sx; w[2 * i + 1] = py = sy;
  }
  if (anchor) {
    const x = w[2 * at], y = w[2 * at + 1];
    if (Math.hypot(x - anchor[0], y - anchor[1]) > Math.hypot(x + anchor[0], y + anchor[1])) for (let i = 0; i < 2 * n; i++) w[i] = -w[i];
  }
  return w;
}
function lnGap(z, q) {                           // how near a curve comes to the point q
  let best = Infinity;
  for (let i = 0; i + 3 < z.length; i += 2) {
    const ax = z[i], ay = z[i + 1], bx = z[i + 2] - ax, by = z[i + 3] - ay, l2 = bx * bx + by * by;
    const t = l2 > 0 ? clamp(((q[0] - ax) * bx + (q[1] - ay) * by) / l2, 0, 1) : 0;
    best = Math.min(best, Math.hypot(q[0] - ax - t * bx, q[1] - ay - t * by));
  }
  return best;
}
// The lines for c: a list of curves, or a word for why there are none. depth: how many steps back from the middle
// body's line (0: that line alone).
function lnCurves(cx, cy, depth) {
  const cyc = lnCycle(cx, cy);
  if (!cyc) return 'no cycle';
  const root = lnRoot(cx, cy, cyc);
  if (!root) return 'no root';
  const p = cyc.p, roots = [root];
  for (let k = 1; k < p; k++) { const [x, y] = roots[k - 1]; roots.push([x * x - y * y + cx, 2 * x * y + cy]); }
  const straight = (a, b) => { const z = new Float64Array(2 * LN_PTS); for (let i = 0; i < LN_PTS; i++) { const t = i / (LN_PTS - 1); z[2 * i] = a[0] + t * (b[0] - a[0]); z[2 * i + 1] = a[1] + t * (b[1] - a[1]); } return z; };
  let arms = cyc.m.map((mid, k) => straight(roots[k], mid));
  for (let round = 0; round < 12 * p; round++) {
    arms = arms.map((_, k) => {
      const w = lnBack(arms[(k + 1) % p], cx, cy, roots[k], 0), cut = new Float64Array(w.length - 4);
      cut.set(w.subarray(0, w.length - 6)); cut[cut.length - 2] = cyc.m[k][0]; cut[cut.length - 1] = cyc.m[k][1];
      return lnResample(cut, LN_PTS);
    });
  }
  const a0 = arms[0], first = new Float64Array(4 * LN_PTS);
  first.set(a0);
  for (let i = 0; i < LN_PTS; i++) { first[2 * LN_PTS + 2 * i] = -a0[2 * (LN_PTS - 1 - i)]; first[2 * LN_PTS + 2 * i + 1] = -a0[2 * (LN_PTS - 1 - i) + 1]; }
  const out = [first];
  let front = [{ z: first, body: 0 }];            // body: which body of the cycle the line belongs to, or -1
  for (let lev = 1; lev <= depth && front.length; lev++) {
    const next = [];
    for (const line of front) {
      if (line.body === 1 % p) continue;
      const w = lnBack(line.z, cx, cy);
      for (const sign of [1, -1]) {
        const z = sign > 0 ? w : w.map(t => -t), l = lnLength(z);
        if (l < 2 * LN_STEP) continue;
        const before = line.body < 0 ? -1 : (line.body + p - 1) % p;
        next.push({ z: lnResample(z, clamp(Math.round(l / 0.004), 8, 2 * LN_PTS)), body: before >= 0 && lnGap(z, cyc.m[before]) < Math.max(1e-4, 0.01 * l) ? before : -1 });
      }
    }
    for (const line of next) out.push(line.z);
    front = next;
  }
  out.period = p;
  return out;
}
// For every cell of the grid the number of the nearest seed, by two sweeps: down the columns, then along the rows
// with the lower edge of the parabolas (Felzenszwalb and Huttenlocher). seed: a point number for each cell, or LN_NONE.
function lnNearest(seed, G) {
  const INF = 1e20, d = new Float32Array(G * G), row = new Int32Array(G * G), out = new Uint16Array(G * G).fill(LN_NONE);
  for (let x = 0; x < G; x++) {
    let last = -1;
    for (let y = 0; y < G; y++) { if (seed[y * G + x] !== LN_NONE) last = y; row[y * G + x] = last; d[y * G + x] = last < 0 ? INF : (y - last) * (y - last); }
    last = -1;
    for (let y = G - 1; y >= 0; y--) {
      if (seed[y * G + x] !== LN_NONE) last = y;
      if (last >= 0 && (last - y) * (last - y) < d[y * G + x]) { row[y * G + x] = last; d[y * G + x] = (last - y) * (last - y); }
    }
  }
  const v = new Int32Array(G), zz = new Float64Array(G + 1);
  for (let y = 0; y < G; y++) {
    const o = y * G;
    let k = -1;
    for (let q = 0; q < G; q++) {
      if (d[o + q] >= INF) continue;
      let s = 0;
      while (k >= 0) {
        const r = v[k];
        s = ((d[o + q] + q * q) - (d[o + r] + r * r)) / (2 * q - 2 * r);
        if (s <= zz[k]) k--; else break;
      }
      k++; v[k] = q; zz[k] = k ? s : -INF; zz[k + 1] = INF;
    }
    if (k < 0) continue;
    for (let q = 0, j = 0; q < G; q++) {
      while (zz[j + 1] < q) j++;
      out[o + q] = seed[row[o + v[j]] * G + v[j]];
    }
  }
  return out;
}
// The lines for c as the two arrays the shader reads, put into the table T. Returns why not, or ''.
function lnBuild(T, cx, cy, depth) {
  const curves = lnCurves(cx, cy, depth);
  if (typeof curves === 'string') return curves;
  const pts = [], size = [];                    // for each point: x, y, direction x and y, half-width, first and last point of its line, gap; size: 0 big, 1 middle, 2 small
  for (const z of curves) {
    const l = lnLength(z), m = Math.max(4, Math.round(l / LN_STEP) + 1), s = lnResample(z, m), at = pts.length / 8, gap = l / (m - 1);
    const dir = new Float64Array(2 * m), wide = new Float64Array(m);
    for (let i = 0; i < m; i++) {
      const a = Math.max(i - 1, 0), b = Math.min(i + 1, m - 1), tx = s[2 * b] - s[2 * a], ty = s[2 * b + 1] - s[2 * a + 1], tl = Math.hypot(tx, ty) || 1;
      const x = s[2 * i], y = s[2 * i + 1], dx = dir[2 * i] = tx / tl, dy = dir[2 * i + 1] = ty / tl;
      if (!i || i === m - 1) continue;          // an end of the line: on the body's edge
      wide[i] = Infinity;
      for (const side of [1, -1]) {             // out along the line's square, until the flat set ends
        let far = 0.004;
        while (far < 2 && lnStill(x - side * far * dy, y + side * far * dx, cx, cy, 150)) far *= 1.6;
        let lo = far > 0.004 ? far / 1.6 : 0, hi = far;
        for (let it = 0; it < 10; it++) { const mid = 0.5 * (lo + hi); if (lnStill(x - side * mid * dy, y + side * mid * dx, cx, cy, 150)) lo = mid; else hi = mid; }
        wide[i] = Math.min(wide[i], lo);
      }
    }
    // no faster than the line runs: that also drops a width measured through a gap too thin to see into the next body
    for (let i = 1; i < m; i++) wide[i] = Math.min(wide[i], wide[i - 1] + gap);
    for (let i = m - 2; i >= 0; i--) wide[i] = Math.min(wide[i], wide[i + 1] + gap);
    for (let pass = Math.min(m >> 4, 8); pass > 0; pass--) {      // evened out, the ends staying where they are
      let before = wide[0];
      for (let i = 1; i < m - 1; i++) { const here = wide[i]; wide[i] = 0.25 * (before + 2 * here + wide[i + 1]); before = here; }
    }
    const widest = Math.max(...wide);
    for (let i = 0; i < m; i++) { pts.push(s[2 * i], s[2 * i + 1], dir[2 * i], dir[2 * i + 1], wide[i], at, at + m - 1, gap); size[at + i] = widest > LN_BIG ? 0 : widest > LN_MID ? 1 : 2; }
  }
  const n = pts.length / 8;
  if (!n || n >= LN_NONE) return 'no lines';
  const G = LN_GRID, rows = Math.ceil(n / LN_WIDE), idx = new Uint16Array(4 * G * G).fill(LN_NONE), dat = new Float32Array(8 * rows * LN_WIDE);
  for (let i = 0; i < n; i++) { dat.set(pts.slice(8 * i, 8 * i + 4), 4 * i); dat.set(pts.slice(8 * i + 4, 8 * i + 8), 4 * (rows * LN_WIDE + i)); }
  for (let k = 0; k < 3; k++) {
    const seed = new Uint16Array(G * G).fill(LN_NONE);
    let any = false;
    for (let i = 0; i < n; i++) {
      if (size[i] !== k) continue;
      const gx = Math.floor((pts[8 * i] + LN_HALF) / (2 * LN_HALF) * G), gy = Math.floor((pts[8 * i + 1] + LN_HALF) / (2 * LN_HALF) * G);
      if (gx >= 0 && gy >= 0 && gx < G && gy < G) { seed[gy * G + gx] = i; any = true; }
    }
    if (!any) continue;
    const near = lnNearest(seed, G);
    for (let j = 0; j < G * G; j++) idx[4 * j + k] = near[j];
  }
  T.idx = idx; T.dat = dat; T.rows = rows; T.g = G; T.count = curves.length; T.period = curves.period;
  return '';
}
// The lines the picture on show is drawn with. They belong to a Julia set of z² + c, so any other picture has none.
const LN_WHY = {
  'no cycle': 'This c has no cycle of bodies, so there are no lines: the picture is Sphere inversions, one plane.',
  'no root': 'For this c the lines could not be found: the picture is Sphere inversions, one plane.',
  'no lines': 'For this c the lines could not be found: the picture is Sphere inversions, one plane.',
  mandelbrot: 'In the Mandelbrot picture every point has its own c, so there is no one set of lines: the picture is Sphere inversions, one plane.',
  other: 'The lines are those of z² + c with nothing folded or flipped. With this equation, power or modifier the picture is Sphere inversions, one plane.',
};
// The lines and the pinch points are those of z² + c with nothing folded or flipped.
const lnPlain = () => S.n === 2 && String(S.eq).replace(/\s+/g, '') === 'z^n+c' && !S.abs.some(Boolean) && !S.flip.some(Boolean);
// mid: the table of the middle body's line alone.
function lnTable(mid) {
  const T = mid ? LN.mid : LN.all;
  const key = S.mode !== 'j' ? 'mandelbrot' : !lnPlain() ? 'other' : S.c[0] + ',' + S.c[1];
  if (key === T.key) return T;
  const ver = T.ver + 1, why = key === 'mandelbrot' || key === 'other' ? key : lnBuild(T, S.c[0], S.c[1], mid ? 0 : LN_DEPTH);
  if (why) Object.assign(T, lnBlank());
  T.key = key; T.ver = ver; T.on = !why; T.why = why;
  return T;
}
// What an entry says about the picture on show.
function lnSays(mid) {
  const T = lnTable(mid);
  if (!T.on) return LN_WHY[T.why];
  const cycle = `For this c: a cycle of ${T.period} ${T.period === 1 ? 'body' : 'bodies'}`;
  return mid ? cycle + ', folded about the line of the one that holds 0.' : cycle + `, and ${T.count} ${T.count === 1 ? 'line' : 'lines'}.`;
}
const lnReach = q => clamp(q && isFinite(+q.reach) ? +q.reach : 1.6, 0.5, 4);
// The fold about the line that holds the point number i, in JavaScript: the shader's lnAbout line for line.
// A point v within reach of the line is mirrored in the plane that stands at 45° on it.
function lnAbout(T, v, i, most, q) {
  const d = T.dat, low = 4 * T.rows * LN_WIDE;
  if (Math.hypot(v[0] - d[4 * i], v[1] - d[4 * i + 1], v[2]) > most) return v;
  const a = d[low + 4 * i + 1], b = d[low + 4 * i + 2], gap = d[low + 4 * i + 3];
  for (let k = 0; k < 2; k++) {                 // along the line to the point beside v
    const j = clamp(i + Math.floor(((v[0] - d[4 * i]) * d[4 * i + 2] + (v[1] - d[4 * i + 1]) * d[4 * i + 3]) / gap + 0.5), a, b);
    if (j === i) break;
    i = j;
  }
  const px = d[4 * i], py = d[4 * i + 1], tx = d[4 * i + 2], ty = d[4 * i + 3];
  const j = clamp(i + ((v[0] - px) * tx + (v[1] - py) * ty < 0 ? -1 : 1), a, b);
  let fx = px, fy = py, wide = d[low + 4 * i];
  if (j !== i) {                                // onto the stretch between two points
    const ex = d[4 * j] - px, ey = d[4 * j + 1] - py, t = clamp(((v[0] - px) * ex + (v[1] - py) * ey) / Math.max(ex * ex + ey * ey, 1e-12), 0, 1);
    fx = px + t * ex; fy = py + t * ey; wide += t * (d[low + 4 * j] - wide);
  }
  const ox = v[0] - fx, oy = v[1] - fy, nx = -ty, ny = tx;
  const dist = Math.hypot(ox, oy), rho = Math.hypot(dist, v[2]), share = rho / Math.max(lnReach(q) * wide, 1e-9);
  if (share >= 1) return v;
  const ux = dist > 0 ? ox / dist : nx, uy = dist > 0 ? oy / dist : ny;
  if (q && +q.wall > 0.5) {
    if (Math.abs(v[2]) <= dist) return v;
    const side = ox * nx + oy * ny < 0 ? -1 : 1;
    return [fx + v[2] * side * ux, fy + v[2] * side * uy, side * dist];
  }
  const ang = Math.atan2(Math.abs(v[2]), dist);
  if (ang <= 0.25 * PI) return v;
  const g = 0.5 * PI - ang;
  return [fx + ux * rho * Math.cos(g), fy + uy * rho * Math.cos(g), (v[2] < 0 ? -1 : 1) * rho * Math.sin(g)];
}
// The whole fold: about a big body's line, then a middle-sized body's, then a small one's. mid: about the middle
// body's line alone.
function lnFold(v, q, mid) {
  const T = lnTable(mid);
  if (!T.on || v[2] === 0) return v;
  const G = T.g, reach = lnReach(q);
  for (let k = 0; k < 3; k++) {
    const gx = Math.floor((v[0] + LN_HALF) / (2 * LN_HALF) * G), gy = Math.floor((v[1] + LN_HALF) / (2 * LN_HALF) * G);
    if (!(gx >= 0 && gy >= 0 && gx < G && gy < G)) return v;
    const i = T.idx[4 * (gy * G + gx) + k];
    if (i !== LN_NONE) v = lnAbout(T, v, i, k ? reach * (k === 1 ? LN_BIG : LN_MID) + LN_SLACK : Infinity, q);
  }
  return v;
}
// Hands the map and the points to the shader, as two textures on the units 2 and 3 (the display uses 0 and 1).
function lnUniforms(gl, loc, mid) {
  const T = lnTable(mid);
  let t = LN_GL.get(gl);
  gl.activeTexture(gl.TEXTURE2);
  if (!t || !gl.isTexture(t.idx)) {
    t = { idx: gl.createTexture(), dat: gl.createTexture(), of: null, ver: -1 };
    for (const tex of [t.idx, t.dat]) {
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }
    LN_GL.set(gl, t);
  }
  const fresh = t.of !== T || t.ver !== T.ver;
  gl.bindTexture(gl.TEXTURE_2D, t.idx);
  if (fresh) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16UI, T.g, T.g, 0, gl.RGBA_INTEGER, gl.UNSIGNED_SHORT, T.idx);
  gl.activeTexture(gl.TEXTURE3); gl.bindTexture(gl.TEXTURE_2D, t.dat);
  if (fresh) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, LN_WIDE, 2 * T.rows, 0, gl.RGBA, gl.FLOAT, T.dat);
  t.of = T; t.ver = T.ver;
  gl.activeTexture(gl.TEXTURE0);
  gl.uniform1i(loc('uLnIdx'), 2); gl.uniform1i(loc('uLnDat'), 3);
  gl.uniform4f(loc('uLn'), T.g, T.rows, 0, T.on ? 1 : 0);
}

// The middle body's two pinch points from c alone, for the entry "Two planes, between the middle body's pinch
// points". No table is built: the shader works the same numbers out for itself (its pnFind is this one step for
// step), so a Julia picture and the Mandelbrot solid, where every point is its own c, follow one formula.
//   1. Follow the orbit of 0. Each time it comes nearer to 0 than ever before, after k steps, look for a point
//      there that k steps bring back to itself (Newton's method). The first such point that pulls its
//      neighbours in is the point of the bodies' cycle in the body that holds 0, and k is the cycle's length.
//      A cycle of one point means a set of one body, which hangs on nothing and has no pinch point.
//   2. Beside that point w, k steps are w + d t + e t² to the second order. The other point this short formula
//      brings back to itself, t = (1 - d) / e, lies near the body's pinch point: Newton's method from there
//      finds the pinch point r itself, a point that pushes its neighbours away.
// The flat set looks the same from both sides of 0, so the body's second pinch point is -r, and the straight line
// between the two runs through 0.
//   3. The body's shape about that line, from the same numbers. 1 / |e| is its half-width at 0: through the glass
//      that makes k steps a plain squaring the body is a round disc, and e is that glass. At a pinch point the body
//      ends in a wedge. k steps push the neighbours of r away m times as far, and a disc's edge twice as far, so the
//      wedge opens by log2(m) of a straight angle. The half-width at a place along the line is the disc's there, or
//      the wedge's where that is less.
const PN_MAX = 12, PN_NEWTON = 6;
const pnDiv = (a, b) => { const m = Math.max(b[0] * b[0] + b[1] * b[1], 1e-30); return [(a[0] * b[0] + a[1] * b[1]) / m, (a[1] * b[0] - a[0] * b[1]) / m]; };
// k steps from the point w: where they end (u), their slope (d) and half their second slope (e)
function pnSteps(w, cx, cy, k) {
  let u = w, d = [1, 0], e = [0, 0];
  for (let j = 0; j < k; j++) {
    e = [d[0] * d[0] - d[1] * d[1] + 2 * (u[0] * e[0] - u[1] * e[1]), 2 * d[0] * d[1] + 2 * (u[0] * e[1] + u[1] * e[0])];
    d = [2 * (u[0] * d[0] - u[1] * d[1]), 2 * (u[0] * d[1] + u[1] * d[0])];
    u = [u[0] * u[0] - u[1] * u[1] + cx, 2 * u[0] * u[1] + cy];
  }
  return { u, d, e };
}
function pnNewton(w, cx, cy, k) {
  for (let s = 0; s < PN_NEWTON; s++) {
    const { u, d } = pnSteps(w, cx, cy, k), t = pnDiv([u[0] - w[0], u[1] - w[1]], [d[0] - 1, d[1]]);
    w = [w[0] - t[0], w[1] - t[1]];
  }
  return w;
}
// The cycle's length p, the pinch point r, the body's half-width at 0 and the slope of its edge at a pinch point.
// Only p when the cycle is one point. Nothing when 0 leaves or no cycle of at most PN_MAX points pulls.
function pnFind(cx, cy) {
  let z = [0, 0], best = Infinity;
  for (let k = 1; k <= PN_MAX; k++) {
    z = [z[0] * z[0] - z[1] * z[1] + cx, 2 * z[0] * z[1] + cy];
    const m = z[0] * z[0] + z[1] * z[1];
    if (!(m < 16)) return null;
    if (m >= best) continue;
    best = m;
    const w = pnNewton(z, cx, cy, k), at = pnSteps(w, cx, cy, k);
    if (!(Math.hypot(at.u[0] - w[0], at.u[1] - w[1]) < 1e-4) || !(Math.hypot(at.d[0], at.d[1]) < 1)) continue;
    if (k === 1) return { p: 1, r: null };
    const t = pnDiv([1 - at.d[0], -at.d[1]], at.e), r = pnNewton([w[0] + t[0], w[1] + t[1]], cx, cy, k), far = pnSteps(r, cx, cy, k);
    if (!(Math.hypot(far.u[0] - r[0], far.u[1] - r[1]) < 1e-4) || !(Math.hypot(far.d[0], far.d[1]) > 1) || !(Math.hypot(r[0], r[1]) > 1e-6)) return null;
    return { p: k, r, wide: 1 / Math.max(Math.hypot(at.e[0], at.e[1]), 1e-9), tip: Math.tan(0.5 * PI * clamp(Math.log2(Math.hypot(far.d[0], far.d[1])), 0.05, 0.95)) };
  }
  return null;
}
const PN = { key: '', at: null };                // the last c asked about, and its answer
// What pnFind says for the constant c, or nothing: it belongs to z² + c with nothing folded or flipped.
function pnOf(c) {
  if (!c || !lnPlain()) return null;
  const key = c[0] + ',' + c[1];
  if (key !== PN.key) { PN.key = key; PN.at = pnFind(c[0], c[1]); }
  return PN.at;
}
const pnReach = q => clamp(q && isFinite(+q.reach) ? +q.reach : 1.6, 0.5, 4);
// The fold in JavaScript, the shader's pnFold line for line: a point within reach of the line between the pinch
// points is mirrored in the plane that stands at 45° on it. c: the orbit's constant.
function pnFold(v, q, c) {
  const P = pnOf(c || (S.mode === 'j' ? S.c : null));
  if (!P || !P.r || v[2] === 0) return v;
  const L = Math.hypot(P.r[0], P.r[1]), ux = P.r[0] / L, uy = P.r[1] / L, s = v[0] * ux + v[1] * uy, t = v[1] * ux - v[0] * uy, f = Math.abs(s) / L;
  if (!(f < 1)) return v;
  const wide = Math.min(P.wide * Math.sqrt(1 - f * f), (L - Math.abs(s)) * P.tip);
  if (!(Math.hypot(t, v[2]) < pnReach(q) * wide) || Math.abs(v[2]) <= Math.abs(t)) return v;
  const side = (t < 0 ? -1 : 1) * Math.abs(v[2]);
  return [s * ux - side * uy, s * uy + side * ux, (v[2] < 0 ? -1 : 1) * Math.abs(t)];
}
// uPn: a Julia picture's pinch point (x, y), the body's half-width at 0 (nothing when there is no pinch point) and
// the slope of its edge at a pinch point. uPnEach: 1 when the shader is to work these out for each point of the
// picture, as the Mandelbrot solid needs.
function pnUniforms(gl, loc) {
  const each = S.mode !== 'j' && lnPlain(), at = each ? null : pnOf(S.mode === 'j' ? S.c : null), P = at && at.r ? at : null;
  gl.uniform4f(loc('uPn'), P ? P.r[0] : 0, P ? P.r[1] : 0, P ? P.wide : 0, P ? P.tip : 0);
  gl.uniform1f(loc('uPnEach'), each ? 1 : 0);
}
// What the entry says about the picture on show.
function pnSays() {
  if (!lnPlain()) return 'The pinch points are those of z² + c with nothing folded or flipped. With this equation, power or modifier the picture is Sphere inversions, one plane.';
  if (S.mode !== 'j') return 'In the Mandelbrot picture every point is its own c, and has pinch points of its own.';
  const P = pnOf(S.c);
  if (!P) return `This c has no cycle of at most ${PN_MAX} bodies, so nothing is folded: the picture is Sphere inversions, one plane.`;
  if (!P.r) return 'For this c the set is one body, which has no pinch points, so nothing is folded: the picture is Sphere inversions, one plane.';
  return `For this c: a cycle of ${P.p} ${P.p === 1 ? 'body' : 'bodies'}, and pinch points at (${aprNum(P.r[0])}, ${aprNum(P.r[1])}) and straight across.`;
}
