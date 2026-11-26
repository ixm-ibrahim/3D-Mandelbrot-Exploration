// Every body's own line, for the entry "Two planes, about every body's own line" (10-approaches.js).
//
// A Julia set of z² + c whose c has a cycle of bodies is made of bodies that hang on one another at pinch points.
// Each body has a line of its own: through its middle, from the point where it hangs on its parent (its root) to
// the point opposite. The flat rule lays each line onto another one, and the lines of the bodies of the cycle onto
// each other in turn. The entry folds a point about the nearest such line, as "two planes" folds it about the x-axis.
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
// (how far one can go square to the line, on the nearer side, before leaving the flat set).
//
// The shader cannot search the points, so it is handed a map (lnMap): for every cell of a grid over the flat plane,
// the nearest point of a big body's line, of a middle-sized body's and of a small body's. A point high above a
// small body lies outside that body's reach and inside a bigger one's, which is why there are three.
// LN.idx holds the map (three point numbers a cell) and LN.dat the points (x, y, direction; half-width), both as
// the textures the shader reads (lnUniforms). lnFold is the same fold in JavaScript, from the same two arrays.
const LN_GRID = 768, LN_HALF = 2, LN_STEP = 0.006, LN_DEPTH = 9, LN_PTS = 96, LN_NONE = 65535, LN_WIDE = 1024;
const LN_BIG = 0.12, LN_MID = 0.035;          // a line is of a big body, a middle-sized one or a small one by its widest half-width
// LN.dat is a picture LN_WIDE wide: the points fill its upper rows (x, y, direction), their half-widths the same
// places in its lower rows.
const LN = { key: '', ver: 0, on: false, count: 0, period: 0, why: '', idx: new Uint16Array(4).fill(LN_NONE), dat: new Float32Array(8 * LN_WIDE), rows: 1, g: 1 };
const LN_GL = new WeakMap();                    // for each graphics context: its two textures and the version they hold

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
// The lines for c: a list of curves, or a word for why there are none.
function lnCurves(cx, cy) {
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
  for (let lev = 1; lev <= LN_DEPTH && front.length; lev++) {
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
// The lines for c as the two arrays the shader reads. Returns why not, or ''.
function lnBuild(cx, cy) {
  const curves = lnCurves(cx, cy);
  if (typeof curves === 'string') return curves;
  const pts = [], size = [];                    // x, y, direction x, direction y, half-width for each point; size: 0 big, 1 middle, 2 small
  for (const z of curves) {
    const l = lnLength(z), m = Math.max(4, Math.round(l / LN_STEP) + 1), s = lnResample(z, m), at = pts.length / 5;
    let widest = 0;
    for (let i = 0; i < m; i++) {
      const a = Math.max(i - 1, 0), b = Math.min(i + 1, m - 1), tx = s[2 * b] - s[2 * a], ty = s[2 * b + 1] - s[2 * a + 1], tl = Math.hypot(tx, ty) || 1;
      const x = s[2 * i], y = s[2 * i + 1], dx = tx / tl, dy = ty / tl;
      let wide = Infinity;
      for (const side of [1, -1]) {             // out along the line's square, until the flat set ends
        let far = 0.004;
        while (far < 2 && lnStill(x - side * far * dy, y + side * far * dx, cx, cy, 150)) far *= 1.6;
        let lo = far > 0.004 ? far / 1.6 : 0, hi = far;
        for (let it = 0; it < 10; it++) { const mid = 0.5 * (lo + hi); if (lnStill(x - side * mid * dy, y + side * mid * dx, cx, cy, 150)) lo = mid; else hi = mid; }
        wide = Math.min(wide, lo);
      }
      pts.push(x, y, dx, dy, wide); widest = Math.max(widest, wide);
    }
    for (let i = 0; i < m; i++) size[at + i] = widest > LN_BIG ? 0 : widest > LN_MID ? 1 : 2;
  }
  const n = pts.length / 5;
  if (!n || n >= LN_NONE) return 'no lines';
  const G = LN_GRID, rows = Math.ceil(n / LN_WIDE), idx = new Uint16Array(4 * G * G).fill(LN_NONE), dat = new Float32Array(8 * rows * LN_WIDE);
  for (let i = 0; i < n; i++) { dat.set([pts[5 * i], pts[5 * i + 1], pts[5 * i + 2], pts[5 * i + 3]], 4 * i); dat[4 * (rows * LN_WIDE + i)] = pts[5 * i + 4]; }
  for (let k = 0; k < 3; k++) {
    const seed = new Uint16Array(G * G).fill(LN_NONE);
    let any = false;
    for (let i = 0; i < n; i++) {
      if (size[i] !== k) continue;
      const gx = Math.floor((pts[5 * i] + LN_HALF) / (2 * LN_HALF) * G), gy = Math.floor((pts[5 * i + 1] + LN_HALF) / (2 * LN_HALF) * G);
      if (gx >= 0 && gy >= 0 && gx < G && gy < G) { seed[gy * G + gx] = i; any = true; }
    }
    if (!any) continue;
    const near = lnNearest(seed, G);
    for (let j = 0; j < G * G; j++) idx[4 * j + k] = near[j];
  }
  LN.idx = idx; LN.dat = dat; LN.rows = rows; LN.g = G; LN.count = curves.length; LN.period = curves.period;
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
function lnTable() {
  const plain = S.n === 2 && String(S.eq).replace(/\s+/g, '') === 'z^n+c' && !S.abs.some(Boolean) && !S.flip.some(Boolean);
  const key = S.mode !== 'j' ? 'mandelbrot' : !plain ? 'other' : S.c[0] + ',' + S.c[1];
  if (key === LN.key) return LN;
  LN.key = key; LN.ver++;
  const why = key === 'mandelbrot' || key === 'other' ? key : lnBuild(S.c[0], S.c[1]);
  LN.on = !why; LN.why = why;
  if (why) { LN.idx = new Uint16Array(4).fill(LN_NONE); LN.dat = new Float32Array(8 * LN_WIDE); LN.rows = 1; LN.g = 1; LN.count = 0; LN.period = 0; }
  return LN;
}
// What the entry says about the picture on show.
function lnSays() {
  const T = lnTable();
  return T.on ? `For this c: a cycle of ${T.period} ${T.period === 1 ? 'body' : 'bodies'}, and ${T.count} ${T.count === 1 ? 'line' : 'lines'}.` : LN_WHY[T.why];
}
const lnReach = q => clamp(q && isFinite(+q.reach) ? +q.reach : 1.6, 0.5, 4);
// The fold, in JavaScript: the shader's lnFold line for line.
function lnFold(v, q) {
  const T = lnTable();
  if (!T.on || v[2] === 0) return v;
  const G = T.g, gx = Math.floor((v[0] + LN_HALF) / (2 * LN_HALF) * G), gy = Math.floor((v[1] + LN_HALF) / (2 * LN_HALF) * G);
  if (!(gx >= 0 && gy >= 0 && gx < G && gy < G)) return v;
  const reach = lnReach(q), slack = LN_STEP + 2 * (2 * LN_HALF / G), d = T.dat;
  let best = 1, hit = false, sx = 0, sy = 0, qx = 0, qy = 0, nx = 0, ny = 0;
  for (let k = 0; k < 3; k++) {
    const i = T.idx[4 * (gy * G + gx) + k];
    if (i === LN_NONE) continue;
    const tx = d[4 * i + 2], ty = d[4 * i + 3], along = clamp((v[0] - d[4 * i]) * tx + (v[1] - d[4 * i + 1]) * ty, -slack, slack);
    const fx = d[4 * i] + along * tx, fy = d[4 * i + 1] + along * ty, ox = v[0] - fx, oy = v[1] - fy;
    const share = Math.hypot(ox, oy, v[2]) / Math.max(reach * d[4 * (T.rows * LN_WIDE + i)], 1e-9);
    if (share <= best) { best = share; hit = true; sx = fx; sy = fy; qx = ox; qy = oy; nx = -ty; ny = tx; }
  }
  if (!hit) return v;
  const dist = Math.hypot(qx, qy), ux = dist > 0 ? qx / dist : nx, uy = dist > 0 ? qy / dist : ny;
  if (q && +q.wall > 0.5) {
    if (Math.abs(v[2]) <= dist) return v;
    const side = qx * nx + qy * ny < 0 ? -1 : 1;
    return [sx + v[2] * side * ux, sy + v[2] * side * uy, side * dist];
  }
  const a = Math.atan2(Math.abs(v[2]), dist), g = 0.25 * PI - Math.abs(a - 0.25 * PI), rho = Math.hypot(dist, v[2]);
  return [sx + ux * rho * Math.cos(g), sy + uy * rho * Math.sin(g), (v[2] < 0 ? -1 : 1) * rho * Math.sin(g)];
}
// Hands the map and the points to the shader, as two textures on the units 2 and 3 (the display uses 0 and 1).
function lnUniforms(gl, loc) {
  const T = lnTable();
  let t = LN_GL.get(gl);
  gl.activeTexture(gl.TEXTURE2);
  if (!t || !gl.isTexture(t.idx)) {
    t = { idx: gl.createTexture(), dat: gl.createTexture(), ver: -1 };
    for (const tex of [t.idx, t.dat]) {
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }
    LN_GL.set(gl, t);
  }
  const fresh = t.ver !== T.ver;
  gl.bindTexture(gl.TEXTURE_2D, t.idx);
  if (fresh) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16UI, T.g, T.g, 0, gl.RGBA_INTEGER, gl.UNSIGNED_SHORT, T.idx);
  gl.activeTexture(gl.TEXTURE3); gl.bindTexture(gl.TEXTURE_2D, t.dat);
  if (fresh) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, LN_WIDE, 2 * T.rows, 0, gl.RGBA, gl.FLOAT, T.dat);
  t.ver = T.ver;
  gl.activeTexture(gl.TEXTURE0);
  gl.uniform1i(loc('uLnIdx'), 2); gl.uniform1i(loc('uLnDat'), 3);
  gl.uniform4f(loc('uLn'), T.g, T.rows, LN_STEP + 2 * (2 * LN_HALF / LN_GRID), T.on ? 1 : 0);
}
