"""Engineer "mesh", round 9: the edit for item 1 (the colours of a cut face), applied once to src/js/46-mesh.js."""
p = 'src/js/46-mesh.js'
s = open(p, encoding='utf-8', newline='').read()
crlf = '\r\n' in s
s = s.replace('\r\n', '\n')


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:70])
    s = s.replace(a, b)


# ---- constants
rep("""const MESH_MANY_PIECES = 200;        // from this many pieces on, the solid is finer than the grid can show, and the panel says so
""", """const MESH_MANY_PIECES = 200;        // from this many pieces on, the solid is finer than the grid can show, and the panel says so
// Where a sample holds the colour of the cut face and not a colour of the surface. The sampler (RAW_CUT, RAW_ABOVE
// and RAW_IN in 30-shaders.js, which these three numbers repeat) gives that colour to every sample inside the solid
// in the slices from MESH_FACE_BELOW cells below the cut plane to MESH_FACE_ABOVE above it, and anywhere else to a
// sample whose estimate reads more than MESH_FACE_DEEP cells inside.
const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
""")

# ---- meshTrue keeps the own distances
rep("""  return { d, f };
}

// The box that holds the solid""", """  return { d, f, own: d.slice() };   // own: the distances as the solid alone gives them, before meshField applies the picture's limits
}

// The box that holds the solid""")
rep("""// The estimates of one slice as distances: { d, f }, f being what each estimate was multiplied by.""",
    """// The estimates of one slice as distances: { d, f, own }, f being what each estimate was multiplied by.""")

# ---- meshSlice
rep("""// A slice ready for marching: which samples are inside (m), how many in each row (rows), the distances (d), what
// meshTrue multiplied each estimate by (f), the colours (c).
// Samples on the outer wall of the grid are counted as outside whatever they hold, which closes the mesh where the
// solid runs into the wall.
function meshSlice(g, d, c, end, f) {
  const n = g.n, m = new Uint8Array(n * n), rows = new Int32Array(n), L = g.level;
  for (let j = 0, q = 0; j < n; j++) {
    const wall = end || j === 0 || j === n - 1;
    let count = 0;
    for (let i = 0; i < n; i++, q++) {
      if (!(d[q] <= L)) continue;
      if (wall || i === 0 || i === n - 1) d[q] = L + g.h;
      else { m[q] = 1; count++; }
    }
    rows[j] = count;
  }
  return { d, c, m, rows, f };
}""", """// A slice ready for marching: which samples are inside (m), how many in each row (rows), the distances (d), what
// meshTrue multiplied each estimate by (f), the colours (c).
// Samples on the outer wall of the grid are counted as outside whatever they hold, which closes the mesh where the
// solid runs into the wall (wall marks those samples).
// For the colours of a cut face (see meshPoint): own holds the distances before the picture's limits were applied,
// zc is the height of the slice above the cut plane (minus infinity when the solid is not cut), and face says that
// every sample inside the solid holds the colour of the cut face in this slice (see MESH_FACE_BELOW).
function meshSlice(g, d, c, end, f, own, zc) {
  const n = g.n, m = new Uint8Array(n * n), rows = new Int32Array(n), L = g.level, wall = new Uint8Array(n * n);
  for (let j = 0, q = 0; j < n; j++) {
    const edge = end || j === 0 || j === n - 1;
    let count = 0;
    for (let i = 0; i < n; i++, q++) {
      if (!(d[q] <= L)) continue;
      if (edge || i === 0 || i === n - 1) { d[q] = L + g.h; wall[q] = 1; }
      else { m[q] = 1; count++; }
    }
    rows[j] = count;
  }
  return { d, c, m, rows, f, own, zc, wall, face: zc > -MESH_FACE_BELOW * g.h && zc < MESH_FACE_ABOVE * g.h };
}
// A sample holds the colour of the cut face, not a colour of the surface: it lies inside the solid by its own
// estimate, in a slice beside the cut plane or deep inside (see MESH_FACE_BELOW).
const meshHoldsFace = (g, s, q) => { const e = s.c[4 * q + 3]; return e <= 0 && (s.face || e < -MESH_FACE_DEEP * g.h); };
// The sample a point of a cut face takes its colour from, as [the colours of its slice, its place in them]: the
// inside end of the point's grid edge if it holds the face's colour, else the outside end, else the nearest sample
// that does, within g.reach cells in the two slices (the band by which the model is fatter than the solid is as
// wide as the surface offset, and no sample in it lies inside the solid). null when there is none.
function meshFaceFrom(g, si, qi, so, qo) {
  if (meshHoldsFace(g, si, qi)) return [si.c, 4 * qi];
  if (meshHoldsFace(g, so, qo)) return [so.c, 4 * qo];
  const n = g.n, R = g.reach;
  let best = null, least = Infinity;
  for (let e = 0; e < 2; e++) {
    const sl = e ? so : si, q = e ? qo : qi, i0 = q % n, j0 = (q - i0) / n;
    for (let j = Math.max(0, j0 - R); j <= Math.min(n - 1, j0 + R); j++) {
      for (let i = Math.max(0, i0 - R); i <= Math.min(n - 1, i0 + R); i++) {
        const far = (i - i0) * (i - i0) + (j - j0) * (j - j0);
        if (far < least && meshHoldsFace(g, sl, j * n + i)) { least = far; best = [sl.c, 4 * (j * n + i)]; }
      }
    }
  }
  return best;
}""")

# ---- meshPoint colour
rep("""  // The colour lies between the colours of the two ends, by the point's place on the edge, like the position.
  const cin = (in0 ? s0 : s1).c, cout = (in0 ? s1 : s0).c, qi = 4 * (in0 ? q0 : q1), qo = 4 * (in0 ? q1 : q0), w = s;
  for (let k = 0; k < 3; k++) {
    const lin = cin[qi + k] * (1 - w) + cout[qo + k] * w;
    g.col[p + k] = lin > 0 ? Math.round(255 * Math.pow(Math.min(lin, 1), 1 / 2.2)) : 0;   // files hold display values, not linear light
  }
  return v;
}""", """  // The colour lies between the colours of the two ends, by the point's place on the edge, like the position.
  // Both ends hold the colour of the surface nearest to them, with two exceptions.
  // 1. A point of a cut face. The model is cut open there, by the cut plane or by the wall of the grid, and the
  //    picture shows such a face in one plain colour (or painted like the inside of the 2D view), right up to its
  //    edge. So the point takes the colour of a sample that holds the face's colour (meshFaceFrom), or failing
  //    that the colour the face had at the point before. A point belongs to the cut plane's face when its edge
  //    stands upright, the outside end lies above the face, and on the way up the cut plane is reached before the
  //    solid's own surface is: where the plane's distance passes the level, the solid's own is still within it.
  //    (Without this the face kept a rim of surface colours two to four cells wide.)
  // 2. An inside end that holds the cut face's colour says nothing about the surface, so there the outside end
  //    alone gives the colour.
  const si = in0 ? s0 : s1, so = in0 ? s1 : s0, ei = in0 ? q0 : q1, eo = in0 ? q1 : q0, cin = si.c, cout = so.c, qi = 4 * ei, qo = 4 * eo;
  let w = s, from = null, cut = so.wall[eo] === 1;
  if (!cut && axis === 2 && so.zc > L) {
    const reached = (L - si.zc) / (so.zc - si.zc);
    cut = si.own[ei] + reached * (so.own[eo] - si.own[ei]) <= L;
  }
  if (cut) {
    from = meshFaceFrom(g, si, ei, so, eo);
    if (from) { const c = g.faceCol || (g.faceCol = [0, 0, 0]); for (let k = 0; k < 3; k++) c[k] = from[0][from[1] + k]; }
  } else if (MESH_FACE_RULE2 && meshHoldsFace(g, si, ei) && !meshHoldsFace(g, so, eo)) w = 1;
  for (let k = 0; k < 3; k++) {
    const lin = from ? from[0][from[1] + k] : cut && g.faceCol ? g.faceCol[k] : cin[qi + k] * (1 - w) + cout[qo + k] * w;
    g.col[p + k] = lin > 0 ? Math.round(255 * Math.pow(Math.min(lin, 1), 1 / 2.2)) : 0;   // files hold display values, not linear light
  }
  return v;
}""")

# ---- meshBuild: g.reach, slices carry own and zc
rep("""  const g = { n, nz, h, level: o.offset * h, nv: 0, ni: 0, ev: new Int32Array(12), org: [cx - (n - 1) * h / 2, cy - (n - 1) * h / 2, z0],""",
    """  const g = { n, nz, h, level: o.offset * h, reach: Math.min(8, pad), faceCol: null, nv: 0, ni: 0, ev: new Int32Array(12), org: [cx - (n - 1) * h / 2, cy - (n - 1) * h / 2, z0],""")
rep("""      const Bs = meshSlice(g, meshField(job, mid, cx, cy, side, z, n, T), mid, at === 0 || at === nz - 1, T.f);""",
    """      const Bs = meshSlice(g, meshField(job, mid, cx, cy, side, z, n, T), mid, at === 0 || at === nz - 1, T.f, T.own, job.cutOn ? z - job.cut : -Infinity);""")
# a switch for the experiment: rule 2 on or off (window.squaringLabMeshTest.rule2 === false turns it off)
rep("""const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
""", """const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
let MESH_FACE_RULE2 = true;
""")
open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('edited; crlf', crlf, len(s))
