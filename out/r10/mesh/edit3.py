"""Round 10, mesh: the third version of the rule that leaves the thin layers of a trap solid out (run once, from the workspace root)."""
p = 'src/js/46-mesh.js'
s = open(p, encoding='utf-8').read()
a = s.index('// ---------- a solid made by a trap: its thinnest layers are left out')
b = s.index('// The box that holds the solid, as [x0, x1, y0, y1, z0, z1]')
new = r'''// ---------- a solid made by a trap: its thinnest layers are left out
// A trap that is the solid wraps the set in layer upon layer, each thinner than the last, without end: hairs and
// sheets far thinner than a cell. The picture leaves out every layer thinner than two to three of its pixels
// (TRAP_THIN in 30-shaders.js). A volume sample is asked without a pixel size and holds them all. With a surface
// offset every sample within that distance of a hair counted as solid, so the hairs grew into fins and flakes all
// over the model, which the picture does not show.
// So the model of such a solid is built from its parts that are at least g.thinT thick (meshBuild sets it: what
// the picture still draws, between MESH_THIN cells and one cell), and the offset grows only those.
// Inside a layer of a trap and right beside it the estimate is a distance to first order. So three samples in a
// row along an axis, v in the middle between p and r, tell how thick the part is that lies at the middle one or
// between it and its lower neighbour: |p - r| - 2v. (Across a wall the estimate falls to the wall and rises again
// behind it, both at the same rate, and that rate is what one step along the axis is worth.)
// meshCore finds the samples inside thick parts: a sample inside the solid that has, along each axis, either a
// neighbour inside the solid or a part at least g.thinT thick around it. It returns for each such sample of the
// slice `mid` the radius of a ball around it that the solid reaches: its depth, or the way to the far face of a
// wall where that is known (at most g.thin cells and a half), and -1 for every other sample. lo and hi are the raw
// slices below and above, or null.
function meshCore(g, lo, mid, hi) {
  const n = g.n, n4 = 4 * n, deep = new Float32Array(n * n).fill(-1), most = (g.thin + 0.5) * g.h, thin = g.thinT;
  for (let j = 1; j < n - 1; j++) {
    for (let i = 1, q = j * n + 1; i < n - 1; i++, q++) {
      const a = 4 * q + 3, v = mid[a];
      if (!(v <= 0)) continue;
      let rad = -v, ok = true;
      for (let k = 0; k < 3 && ok; k++) {
        const p = k === 0 ? mid[a - 4] : k === 1 ? mid[a - n4] : lo ? lo[a] : Infinity, r = k === 0 ? mid[a + 4] : k === 1 ? mid[a + n4] : hi ? hi[a] : Infinity;
        if (p <= 0 || r <= 0) continue;
        const across = Math.abs(p - r) - 2 * v;
        if (!(across >= thin)) ok = false;
        else if (across + v > rad) rad = across + v;
      }
      if (ok) deep[q] = rad < most ? rad : most;
    }
  }
  return deep;
}
// Two samples outside the solid, side by side along an axis, with a thick part between them that no sample fell
// into: v is this sample, a its neighbour across the part, b the neighbour on its own far side, c the sample
// beyond a. The estimate rises away from the part on both far sides (b above v, c above a) by what one step is
// worth, and what the two estimates leave of that step is the part. (A hair leaves nothing. Beside a thick part
// with a hair in front of it the estimate does not rise on the far side of a, which lies toward the solid.)
const meshWall = (v, a, b, c, thin, h) => a > 0 && b - v > 0 && c - a > 0 && b - v < 1.25 * h && Math.min(b - v, c - a) - v - a >= thin;
// The distances of slice `at` (T, from meshTrue) with the thin layers taken out. deep holds what meshCore found,
// by slice number, for the slices from g.thin below to g.thin above; raw holds the raw slices from two below to
// two above (nothing where there is no slice).
// A sample inside a thick part tells every sample around it that the solid is no further than its distance to
// that sample less the radius meshCore gave. The least of these, u, is a distance to the thick parts alone, a
// little too long at most. An estimate that reads more than MESH_THIN_TOL cells shorter than u is the doing of a
// thin layer close by, and u takes its place; with no thick part within reach the sample is put outside. A sample
// right beside a thick wall that no sample fell into (meshWall) keeps its estimate.
// Only samples that count as solid at the level, or lie within a cell of it, are looked at: the others are not
// used for the surface. Returns the samples whose estimate was changed and that now lie outside.
function meshThin(g, T, deep, raw, at) {
  const n = g.n, n4 = 4 * n, R = g.thin, d = T.d, L = g.level, h = g.h, far = L + h, tol = MESH_THIN_TOL * h, thin = g.thinT, drop = new Uint8Array(n * n);
  const mine = deep[at], mid = raw[at], z1 = raw[at - 1], z2 = raw[at - 2], z3 = raw[at + 1], z4 = raw[at + 2];
  for (let j = 0, q = 0; j < n; j++) {
    for (let i = 0; i < n; i++, q++) {
      if (!(d[q] <= far) || mine[q] >= 0) continue;
      const a = 4 * q + 3, v = mid[a];
      if (v > 0 && thin < h) {
        const xm = i > 0 ? mid[a - 4] : NaN, xp = i < n - 1 ? mid[a + 4] : NaN, ym = j > 0 ? mid[a - n4] : NaN, yp = j < n - 1 ? mid[a + n4] : NaN;
        const zm = z1 ? z1[a] : NaN, zp = z3 ? z3[a] : NaN;
        if (meshWall(v, xm, xp, i > 1 ? mid[a - 8] : NaN, thin, h) || meshWall(v, xp, xm, i < n - 2 ? mid[a + 8] : NaN, thin, h) ||
            meshWall(v, ym, yp, j > 1 ? mid[a - 2 * n4] : NaN, thin, h) || meshWall(v, yp, ym, j < n - 2 ? mid[a + 2 * n4] : NaN, thin, h) ||
            meshWall(v, zm, zp, z2 ? z2[a] : NaN, thin, h) || meshWall(v, zp, zm, z4 ? z4[a] : NaN, thin, h)) continue;
      }
      let u = Infinity;
      for (let c = -R; c <= R; c++) {
        const sl = deep[at + c];
        if (!sl) continue;
        for (let b = Math.max(0, j - R), b1 = Math.min(n - 1, j + R); b <= b1; b++) {
          for (let e = Math.max(0, i - R), e1 = Math.min(n - 1, i + R), p = b * n + e; e <= e1; e++, p++) {
            if (sl[p] < 0) continue;
            const t = h * Math.sqrt(c * c + (b - j) * (b - j) + (e - i) * (e - i)) - sl[p];
            if (t < u) u = t;
          }
        }
      }
      if (u === Infinity) u = far;
      else if (!(d[q] < u - tol)) continue;
      d[q] = u; T.own[q] = u; T.f[q] = 1;
      if (u > L) drop[q] = 1;
    }
  }
  return drop;
}

'''
s = s[:a] + new + s[b:]


def swap(old, new_):
    global s
    assert old in s, old
    s = s.replace(old, new_)


swap("const MESH_THIN = 1;                 // a part of a trap solid thinner than this many cells is left out of the model (see meshCore)",
     "const MESH_THIN = 0.5;               // a part of a trap solid thinner than this many cells is left out of the model, whatever the picture shows (see meshCore)\n"
     "const MESH_THIN_PX = 2.4;            // and so is a part thinner than this many pixels of the picture, up to one cell: the picture does not draw it")
swap("  const R = g.thin, look = R + 1, raw = [], deep = [];",
     """  if (R0 && job.snap) {
    // the size of a pixel of the picture where the solid is (as the picture works it out: gPix in 30-shaders.js)
    const b = job.snap.basis, st = job.snap.stage, v = job.snap.S && job.snap.S.view;
    const px = b && st && v ? 2 * v.fov * Math.hypot(b.pos[0] - cx, b.pos[1] - cy, b.pos[2] - (box[4] + box[5]) / 2) / st.ph : NaN;
    if (px > 0 && isFinite(px)) g.thinT = h * clamp(MESH_THIN_PX * px / h, MESH_THIN, 1);
  }
  const R = g.thin, look = R + 1, raw = [], deep = [];""")
swap("thin: job.trap ? Math.floor(o.offset) + 1 : 0,", "thin: R0, thinT: MESH_THIN * h,")
swap("  const g = { n, nz, h, level: o.offset * h,", "  const R0 = job.trap ? Math.floor(o.offset) + 1 : 0;\n  const g = { n, nz, h, level: o.offset * h,")
swap("      const drop = R ? meshThin(g, T, deep, at) : null;", "      const drop = R ? meshThin(g, T, deep, raw, at) : null;")
swap("      if (at >= 1) raw[at - 1] = null;", "      if (at >= 2) raw[at - 2] = null;")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
