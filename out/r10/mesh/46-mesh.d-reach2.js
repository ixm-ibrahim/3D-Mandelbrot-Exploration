// ---------- "Save a 3D model": the solid as a mesh of triangles, packed in a zip as STL, OBJ and PLY files.
//
// The distance estimate is read one level slice at a time (sampleSlice: alpha holds the estimate, rgb the surface
// colour). A coarse first pass finds the box that holds the solid. Each slice's estimates are then turned into
// distances with the help of the slices below and above (meshTrue), and marching cubes runs between each pair of
// neighbouring slices, so only a few slices are ever held. Each place where the surface crosses a grid edge becomes
// one point, found again through per-slice edge maps by every triangle around it, so the mesh is indexed and has
// no open edges. The job is a chain of short turns and works from its own snapshot: the page stays usable, and
// nothing done on the page afterwards changes the model.
//
// For tests: window.squaringLabMeshTest = { field: 'sphere' | 'torus' | 'gyroid' | 'pearl' | 'noise', cells? }
// puts a built-in field in place of the picture (behind the same call as sampleSlice), and the finished mesh is
// left in its .mesh.

// The marching-cubes tables. Corners and edges are numbered as in the standard tables: corners 0 to 3 go round the
// lower face of a cell and 4 to 7 sit above them; edges 0 to 3 go round the lower face, 4 to 7 round the upper one,
// 8 to 11 are the uprights. Bit c of a case number is set when corner c is inside the solid. MESH_EDGE_TABLE holds
// the edges the surface crosses in each case, MESH_TRI_TABLE the triangles as edge numbers written in hex, three
// to a triangle, turning counter-clockwise seen from outside. Where the two inside corners of a face sit on a
// diagonal, each is cut off on its own. That choice only looks at the face, so two cells that share a face agree
// and the surface has no cracks. Both tables were worked out and checked case by case (notes/r4-mesh.md).
const MESH_EDGE_TABLE = [
  0x000, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c, 0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
  0x190, 0x099, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c, 0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
  0x230, 0x339, 0x033, 0x13a, 0x636, 0x73f, 0x435, 0x53c, 0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
  0x3a0, 0x2a9, 0x1a3, 0x0aa, 0x7a6, 0x6af, 0x5a5, 0x4ac, 0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
  0x460, 0x569, 0x663, 0x76a, 0x066, 0x16f, 0x265, 0x36c, 0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
  0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0x0ff, 0x3f5, 0x2fc, 0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
  0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x055, 0x15c, 0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
  0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0x0cc, 0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
  0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc, 0x0cc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
  0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c, 0x15c, 0x055, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
  0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc, 0x2fc, 0x3f5, 0x0ff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
  0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c, 0x36c, 0x265, 0x16f, 0x066, 0x76a, 0x663, 0x569, 0x460,
  0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac, 0x4ac, 0x5a5, 0x6af, 0x7a6, 0x0aa, 0x1a3, 0x2a9, 0x3a0,
  0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c, 0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x033, 0x339, 0x230,
  0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c, 0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x099, 0x190,
  0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c, 0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x000,
];
const MESH_TRI_TABLE = [
  '', '038', '091', '139389', '1a2', '0381a2', '0929a2', '23938929a', '2b3', '0282b8', '0912b3', '1282b8189',
  '1a3ab3', '01b1ab0b8', '09a0a3ab3', '89b9ab', '487', '034374', '091487', '139374349', '1a2487', '0343741a2',
  '0929a2487', '23727a74a49a', '2b3487', '02b0b7074', '0912b3487', '1292b9b79749', '1a3ab3487', '0141a4ab7a74',
  '09a0a3ab3487', '49a4a7ab7', '459', '038459', '041451', '138184145', '1a2459', '0381a2459', '04505a0a2',
  '23a38a84a45a', '2b3459', '0282b8459', '0414512b3', '1252b5b84b45', '1a3ab3459', '01b1ab0b8459', '04345b5ab4b3',
  '45b5ab4b8', '597987', '037079759', '085875051', '135375', '1a2597987', '0370797591a2', '08287275a7a2',
  '23727a75a', '2b3597987', '0292b5b75259', '0858750512b3', '1252b5b75', '1a3ab3597987', '01b1ab0b7079759',
  '08587505a0a3ab3', '5a7ab7', '56a', '03856a', '09156a', '13938956a', '152562', '038152562', '092952562',
  '236386895856', '2b356a', '0282b856a', '0912b356a', '1282b818956a', '15616b1b3', '0150585686b8', '0939535636b3',
  '5686b8589', '48756a', '03437456a', '09148756a', '13937434956a', '152562487', '034374152562', '092952562487',
  '239374349295256', '2b348756a', '02b0b707456a', '0912b348756a', '1292b9b7974956a', '15616b1b3487',
  '01b15616b0b7074', '0939535636b3487', '49795b56b9b7', '4696a9', '0384696a9', '04146a4a1', '13a38684636a',
  '196946162', '038196946162', '042462', '236386846', '2b34696a9', '0282b84696a9', '04146a4a12b3', '1282b818414a46a',
  '19394346b4b3', '01b19694616b0b8', '04346b4b3', '4686b8', '6a9697987', '0370797696a9', '0818717616a1', '13a37636a',
  '198182872762', '037079769621619', '082872762', '236376', '2b36a9697987', '02b0b70797696a9', '0818717616a12b3',
  '1272b717a76a', '19698797616b1b3', '0196b7', '0868760636b3', '6b7', '67b', '03867b', '09167b', '13938967b',
  '1a267b', '0381a267b', '0929a267b', '23938929a67b', '263673', '028267278', '091263673', '126169679789',
  '1a3a63673', '0181a8a68678', '09a0a3a63673', '67978969a', '4868b6', '0343b4b64', '0914868b6', '1393b4b64349',
  '1a24868b6', '0343b4b641a2', '0929a24868b6', '2393b4b6434929a', '263648683', '024264', '091263648683', '126169649',
  '1a3a63648683', '0141a4a64', '09a0a3a63648683', '4969a6', '45967b', '03845967b', '04145167b', '13818414567b',
  '1a245967b', '0381a245967b', '04505a0a267b', '23a38a84a45a67b', '263673459', '028267278459', '041451263673',
  '128267278184145', '1a3a63673459', '0181a8a68678459', '04505a0a3a63673', '4585a8a68678', '5985868b6',
  '0393b9b69659', '08b0b1b61651', '13b1b6165', '1a25985868b6', '0393b9b696591a2', '0858b686505a0a2', '23a3b5b6535a',
  '263658598683', '029265259', '085836326865051', '125265', '1a3a63658598683', '0161a6069659', '0835a6', '5a6',
  '57a7ba', '03857a7ba', '09157a7ba', '13938957a7ba', '15257b5b2', '03815257b5b2', '09295257b5b2', '23938929525b57b',
  '2a7a57273', '0282a7a57278', '0912a7a57273', '1282a7a57278189', '153573', '015058578', '097957073', '579789',
  '48b4b5ba5', '0343b4ba5b54', '09148b4b5ba5', '1393b4ba5b54349', '15254b48b5b2', '0343b4b25215b54',
  '09295254b48b5b2', '23b495', '2a3a53543483', '02a0a5054', '0912a3a53543483', '1292a4a54249', '154148183', '014154',
  '093953543483', '495', '47a7ba4a9', '03847a7ba4a9', '04147a7ba4a1', '13818414a47a7ba', '1929424727b2',
  '0381929424727b2', '04707b0b2', '23438424b47b', '2a9293943473', '0282a7a94a47278', '04147a73272a4a1', '12a478',
  '193943473', '018197947178', '043473', '478', '8b9ba9', '03a3ba0a9', '08b0b1ba1', '13a3ba', '1981828b2',
  '0393b9b29219', '0828b2', '23b', '2a9293983', '0292a9', '08183a32a8a1', '12a', '193983', '019', '083', '',
];
// For each edge: the x and y offset of its lower end, whether that end lies in the upper slice, and the axis the
// edge runs along (0 x, 1 y, 2 from the lower slice to the upper).
const MESH_EDGE_AT = [[0, 0, 0, 0], [1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [1, 0, 1, 1], [0, 1, 1, 0], [0, 0, 1, 1],
  [0, 0, 0, 2], [1, 0, 0, 2], [1, 1, 0, 2], [0, 1, 0, 2]];
const MESH_PASSES = [24, 32, 48, 48, 48, 48];   // slices across the box in each pass of the search for the solid
const MESH_MAX_TRIS = 15e6;          // more than a browser page can hold with its files
const MESH_MAX_BYTES = 1.4e9;        // the same limit for the files together
const MESH_WARN_TRIS = 2e6;
const MESH_SLOPE_MIN = 0.25;         // an estimate is taken to read at most four times too short (see meshTrue)
const MESH_KEPT_SHARE = 0.8;         // below this share of the surface, the panel says how much the largest piece holds
const MESH_MANY_PIECES = 200;        // from this many pieces on, the solid is finer than the grid can show, and the panel says so
const MESH_THIN = 0.5;               // a part of a trap solid thinner than this many cells is left out of the model, whatever the picture shows (see meshCore)
const MESH_THIN_PX = 2.4;            // and so is a part thinner than this many pixels of the picture, up to one cell: the picture does not draw it
const MESH_THIN_TOL = 0.25;          // an estimate this many cells shorter than the thick parts allow is taken to come from a thin layer (see meshThin)
// Where a sample holds the colour of the cut face and not a colour of the surface. The sampler (RAW_CUT, RAW_ABOVE
// and RAW_IN in 30-shaders.js, which these three numbers repeat) gives that colour to every sample inside the solid
// in the slices from MESH_FACE_BELOW cells below the cut plane to MESH_FACE_ABOVE above it, and anywhere else to a
// sample whose estimate reads more than MESH_FACE_DEEP cells inside.
const MESH_FACE_BELOW = 1.01, MESH_FACE_ABOVE = 3.01, MESH_FACE_DEEP = 1.5;
const MESH_FACE_NEAR = 0.5;          // a point this close under the cut plane's face, in cells, is coloured as part of it
const MESH_FACE_RULE2 = true;        // the second exception of meshPoint's colours, kept as a switch so that it can be measured on and off
const MESH_NAMES = { m: 'mandelbrot', j: 'julia', k: 'kleinian' };
const MESH_WORDS = {
  sample: 'The picture could not be read just now. Wait until it has finished drawing, then start again.',
  lost: 'The graphics of this page were interrupted, so the model could not be finished. Start it again.',
  empty: 'Nothing solid was found inside the drawing radius, so there is no model to make.',
  big: 'This model would have more than 15 million triangles, which is more than a browser page can hold. Choose a lower resolution.',
  bytes: 'These files would be too large for a browser page to put together. Choose a lower resolution or fewer kinds of file.',
  cancel: 'Cancelled. Nothing was saved.',
  none: 'Saving a model is not available in this build of the page.',
  kinds: 'Choose at least one kind of file.',
  failed: 'The model could not be built. It may need more memory than the browser gives a page. Try a lower resolution.',
  prepare: 'Preparing to read this solid. The first model of each formula takes a few seconds longer. The next one starts at once.',
};

const MESH = {
  opt: { cells: 128, offset: 0.5, mm: 100, largest: true, stl: true, obj: true, ply: true },
  job: null,       // the model being built
  result: null,    // the finished zip, kept until it is discarded: { name, blob, facts, warn }
  ui: null,        // the panel's elements, once buildMeshPanel has run
  tri: null,       // the triangle table as numbers, 16 per case, -1 after the last
  crc: null,       // the CRC-32 table
  port: null, waiting: [],   // see meshYield
};

function meshBusy() { return !!MESH.job; }
const meshStop = code => Object.assign(new Error('mesh job stopped: ' + code), { mesh: code });

// Hand the thread back to the page for a moment. A message comes round sooner than a timer does, and it is not
// slowed down while the tab is in the background.
function meshYield() {
  return new Promise(done => {
    if (!MESH.port) {
      const ch = new MessageChannel();
      ch.port1.onmessage = () => { const f = MESH.waiting.shift(); if (f) f(); };
      MESH.port = ch.port2;
    }
    MESH.waiting.push(done);
    MESH.port.postMessage(0);
  });
}

// ---------- built-in fields for tests, behind the signature of sampleSlice
// sphere and torus have known volumes; gyroid is a thin wall folded many times inside a ball; pearl is zero
// inside and reads long outside, like the large pearls of the Kleinian view; noise visits every case of the tables.
function meshTestSlice(kind, cx, cy, side, z, n) {
  const out = new Float32Array(4 * n * n), h = side / n;
  for (let j = 0, o = 0; j < n; j++) {
    const y = cy - side / 2 + (j + 0.5) * h;
    for (let i = 0; i < n; i++, o += 4) {
      const x = cx - side / 2 + (i + 0.5) * h, r = Math.hypot(x, y, z);
      let d = r - 1;
      if (kind === 'torus') d = Math.hypot(Math.hypot(x, y) - 1, z) - 0.35;
      else if (kind === 'gyroid') {
        const k = 5.5, g = Math.sin(k * x) * Math.cos(k * y) + Math.sin(k * y) * Math.cos(k * z) + Math.sin(k * z) * Math.cos(k * x);
        d = Math.max(Math.abs(g) / (1.5 * k) - 0.022, r - 1.2);
      } else if (kind === 'pearl') d = Math.max(0, 1.6 * (r - 1));
      else if (kind === 'noise') {
        const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453;
        d = Math.max(0.2 * (s - Math.floor(s) - 0.5), r - 0.5);
      }
      out[o] = clamp(0.5 + 0.4 * x, 0, 1); out[o + 1] = clamp(0.5 + 0.4 * y, 0, 1); out[o + 2] = clamp(0.5 + 0.4 * z, 0, 1);
      out[o + 3] = d;
    }
  }
  return Promise.resolve(out);
}

// ---------- the field the model is made from
// The distances of one slice with the picture's own limits applied: nothing outside the drawing radius, and
// nothing above the cut when the solid is cut open.
// With T (from meshTrue) the slice's estimates have been turned into distances already, and T.d is filled in place.
// The two limits are true distances themselves, so where one of them decides, T.f goes back to 1.
function meshField(job, raw, cx, cy, side, z, n, T) {
  const d = T ? T.d : new Float32Array(n * n), h = side / n, x0 = cx - side / 2 + h / 2, y0 = cy - side / 2 + h / 2;
  const B = job.bound, zz = z * z, cut = job.cutOn ? z - job.cut : -Infinity;
  for (let j = 0, q = 0; j < n; j++) {
    const y = y0 + j * h, yz = y * y + zz;
    for (let i = 0; i < n; i++, q++) {
      const x = x0 + i * h, ball = Math.sqrt(x * x + yz) - B, lim = ball > cut ? ball : cut;
      let v = T ? d[q] : raw[4 * q + 3];
      if (v !== v) v = 1e9;            // not a number: count it as empty space
      if (lim > v) { v = lim; if (T) T.f[q] = 1; }
      d[q] = v;
    }
  }
  return d;
}
// The estimates of one slice as distances: { d, f, own }, f being what each estimate was multiplied by.
// The estimate is right about which side of the surface a sample is on, but outside the solid it reads short, by
// a factor that changes from place to place: measured on the Douady rabbit, about two right beside the surface
// and five a few cells above its flat top, hardly at all off a tip. A surface offset counted in that estimate
// moved the top of a solid four times as far as its rim. What a sample can tell by itself is how fast the estimate
// changes around it: a distance changes by one cell per cell. So each estimate outside the solid, up to a cell
// past the level, is divided by its own slope, taken from its six neighbours (lo and hi are the raw slices below
// and above, or null). Along each axis the steeper side counts: across a thin sheet or the bottom of a crevice
// the two sides cancel, while one side alone still knows. An estimate is never made shorter (a slope above one
// is a jump in the estimate, as beside the deep inside of a solid, not a distance) and never more than
// 1 / MESH_SLOPE_MIN times longer (where parts lie closer together than two cells no slope can be read).
// Samples inside the solid keep their estimate; meshPoint brings them to the scale of the outside end.
// One kind of sample outside keeps its plain estimate too: the one that sits beside a part thinner than a cell
// (a spike such as the Mandelbrot set's needle, a thin sheet). No sample lies inside such a part, so it shows as a
// pit in the estimates: lowest at this sample and rising clearly to both sides along some axis. A thin part is
// only caught at all if the sample nearest to it counts as solid, which for a spike can be 0.7 of a cell away.
// The plain estimate reads short, and that is exactly the margin that keeps thin parts in one piece.
const meshPit = (v, p, q) => p >= v && q >= v && p + q - 2 * v >= 0.5 * v;   // false when a neighbour is missing
function meshTrue(g, lo, mid, hi) {
  const n = g.n, d = new Float32Array(n * n), f = new Float32Array(n * n).fill(1), far = g.level + g.h, one = g.h, least = MESH_SLOPE_MIN * g.h, n4 = 4 * n;
  for (let j = 0, q = 0; j < n; j++) {
    for (let i = 0; i < n; i++, q++) {
      const a = 4 * q + 3, v = mid[a];
      d[q] = v;
      if (!(v > 0 && v < far)) continue;
      const x0 = i > 0 ? mid[a - 4] : NaN, x1 = i < n - 1 ? mid[a + 4] : NaN, y0 = j > 0 ? mid[a - n4] : NaN, y1 = j < n - 1 ? mid[a + n4] : NaN;
      const z0 = lo ? lo[a] : NaN, z1 = hi ? hi[a] : NaN;
      if (meshPit(v, x0, x1) || meshPit(v, y0, y1) || meshPit(v, z0, z1)) continue;
      let x = 0, y = 0, z = 0, t;
      if ((t = Math.abs(v - x0)) > x) x = t;
      if ((t = Math.abs(x1 - v)) > x) x = t;
      if ((t = Math.abs(v - y0)) > y) y = t;
      if ((t = Math.abs(y1 - v)) > y) y = t;
      if ((t = Math.abs(v - z0)) > z) z = t;
      if ((t = Math.abs(z1 - v)) > z) z = t;
      const rise = Math.sqrt(x * x + y * y + z * z);   // the change of the estimate over one cell
      if (rise >= one) continue;
      f[q] = one / (rise > least ? rise : least);
      d[q] = v * f[q];
    }
  }
  return { d, f, own: d.slice() };   // own: the distances as the solid alone gives them, before meshField applies the picture's limits
}
// ---------- a solid made by a trap: its thinnest layers are left out
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
      for (let w = R > 1 ? R - 1 : R; w <= R && u === Infinity; w++) {   // the nearer samples first: they mostly settle it
        for (let c = -w; c <= w; c++) {
          const sl = deep[at + c];
          if (!sl) continue;
          for (let b = Math.max(0, j - w), b1 = Math.min(n - 1, j + w); b <= b1; b++) {
            for (let e = Math.max(0, i - w), e1 = Math.min(n - 1, i + w), p = b * n + e; e <= e1; e++, p++) {
              if (sl[p] < 0) continue;
              const t = h * Math.sqrt(c * c + (b - j) * (b - j) + (e - i) * (e - i)) - sl[p];
              if (t < u) u = t;
            }
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

// The box that holds the solid, as [x0, x1, y0, y1, z0, z1], or null when there is nothing solid.
// Each pass samples the box found by the pass before, so the box closes in on the solid. Three passes are
// enough at an ordinary drawing radius; a very large radius takes more, until the box stops shrinking fast.
async function meshLocate(job) {
  const o = job.opt, B = job.bound, pad = 2 + Math.ceil(o.offset);
  let box = [-B, B, -B, B, -B, B];
  for (let p = 0; p < MESH_PASSES.length; p++) {
    const M = MESH_PASSES[p], side = Math.max(box[1] - box[0], box[3] - box[2]), tall = box[5] - box[4], ext = Math.max(side, tall);
    const nz = Math.max(2, Math.ceil(M * tall / ext)), hz = tall / nz;
    const n = Math.max(8, Math.ceil(2 * M * side / ext)), hx = side / n;   // samples within a slice cost little: twice as fine
    const cx = (box[0] + box[1]) / 2, cy = (box[2] + box[3]) / 2;
    // A point of the solid is at most `reach` from its nearest sample, and the estimate can read up to twice
    // too long. So every sample whose estimate is within twice the reach (plus the surface offset) marks a
    // place where the solid may be, and no part of the solid goes unmarked.
    const reach = Math.hypot(hx, hx, hz) / 2, near = 2 * reach + o.offset * ext / Math.max(8, o.cells - 2 * pad);
    let i0 = n, i1 = -1, j0 = n, j1 = -1, k0 = nz, k1 = -1;
    for (let k = 0; k < nz; k++) {
      const z = box[4] + (k + 0.5) * hz, d = meshField(job, await job.sample(cx, cy, side, z, n), cx, cy, side, z, n);
      for (let j = 0, q = 0; j < n; j++) {
        for (let i = 0; i < n; i++, q++) {
          if (!(d[q] <= near)) continue;
          if (i < i0) i0 = i; if (i > i1) i1 = i;
          if (j < j0) j0 = j; if (j > j1) j1 = j;
          if (k < k0) k0 = k; k1 = k;
        }
      }
      await job.turn('Finding the solid', 0.1 * (1 - 0.5 ** (p + (k + 1) / nz)), true);
    }
    if (i1 < 0) return null;
    const was = (box[1] - box[0]) * (box[3] - box[2]) * tall, x0 = cx - side / 2, y0 = cy - side / 2;
    box = [Math.max(box[0], x0 + i0 * hx), Math.min(box[1], x0 + (i1 + 1) * hx), Math.max(box[2], y0 + j0 * hx), Math.min(box[3], y0 + (j1 + 1) * hx),
      box[4] + k0 * hz, box[4] + (k1 + 1) * hz];
    if ((box[1] - box[0]) * (box[3] - box[2]) * (box[5] - box[4]) > (p < 2 ? 0.85 : 0.5) * was) break;   // it has stopped closing in
  }
  return box;
}

// ---------- marching cubes, one pair of slices at a time
function meshTables() {
  if (MESH.tri) return;
  MESH.tri = new Int8Array(256 * 16).fill(-1);
  MESH_TRI_TABLE.forEach((row, c) => { for (let i = 0; i < row.length; i++) MESH.tri[16 * c + i] = parseInt(row[i], 16); });
}
// A slice ready for marching: which samples are inside (m), how many in each row (rows), the distances (d), what
// meshTrue multiplied each estimate by (f), the colours (c).
// Samples on the outer wall of the grid are counted as outside whatever they hold, which closes the mesh where the
// solid runs into the wall (wall marks those samples).
// For the colours of a cut face (see meshPoint): own holds the distances before the picture's limits were applied,
// zc is the height of the slice above the cut plane (minus infinity when the solid is not cut), and face says that
// every sample inside the solid holds the colour of the cut face in this slice (see MESH_FACE_BELOW).
// drop marks the samples that meshThin put outside (null for a solid that is not made by a trap).
function meshSlice(g, d, c, end, f, own, zc, drop) {
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
  return { d, c, m, rows, f, own, zc, wall, drop: drop || null, face: zc > -MESH_FACE_BELOW * g.h && zc < MESH_FACE_ABOVE * g.h };
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
}
// The point where the surface crosses the grid edge from sample q0 of slice s0 to sample q1 of slice s1.
// (bi, bj, bk) is the grid position of the first end; the edge runs along `axis`.
function meshPoint(g, s0, s1, q0, q1, bi, bj, bk, axis) {
  if (3 * g.nv + 3 > g.pos.length) {
    const pos = new Float32Array(2 * g.pos.length), col = new Uint8Array(2 * g.col.length);
    pos.set(g.pos); col.set(g.col); g.pos = pos; g.col = col;
  }
  const L = g.level, h = g.h, d0 = s0.d[q0], d1 = s1.d[q1], in0 = d0 <= L;
  // An inside end that lies in the solid itself still holds the plain estimate, which reads short just as the
  // outside end's did. Multiplied by what the outside end was multiplied by, the two are on one scale again,
  // and the place where the estimate passes zero stays where the plain estimates put it: at offset 0 the
  // surface is not moved by any of this.
  let din = in0 ? d0 : d1;
  if (din < 0) din *= in0 ? s1.f[q1] : s0.f[q0];
  // s: share of the way from the inside end to the outside end. Close to the surface the two values are
  // distances, and the level lies between them in proportion (neither is trusted for more than one cell).
  // Where the inside end holds a plain zero nothing is known there, and the outside end alone says how far
  // the surface is. The point never sits on a sample itself, so no triangle ends up without area.
  const a = Math.min((in0 ? d1 : d0) - L, h), b = Math.min(L - din, h);
  let s = din === 0 ? 1 - a / h : b / (a + b);
  s = s > 0.02 ? (s < 0.98 ? s : 0.98) : 0.02;
  const t = in0 ? s : 1 - s, v = g.nv++, p = 3 * v;
  g.pos[p] = bi + (axis === 0 ? t : 0); g.pos[p + 1] = bj + (axis === 1 ? t : 0); g.pos[p + 2] = bk + (axis === 2 ? t : 0);
  // The colour lies between the colours of the two ends, by the point's place on the edge, like the position.
  // Both ends hold the colour of the surface nearest to them, with two exceptions.
  // 1. A point of a cut face. The model is cut open there, by the cut plane or by the wall of the grid, and the
  //    picture shows such a face in one plain colour (or painted like the inside of the 2D view), right up to its
  //    edge. So the point takes the colour of a sample that holds the face's colour (meshFaceFrom), or failing
  //    that the colour the face had at the point before. A point belongs to the cut plane's face when its edge
  //    stands upright, the outside end lies above the face, and on the way up the cut plane is reached before the
  //    solid's own surface is: where the plane's distance passes the level, the solid's own is still within it.
  //    Round the rim of the face, where the solid is thinner than a cell, the two samples cannot tell which comes
  //    first, and the point ends up a little under the face: within MESH_FACE_NEAR cells it counts as the face too.
  //    (Without this the face kept a rim of surface colours two to four cells wide.)
  // 2. An inside end that holds the cut face's colour says nothing about the surface, so there the outside end
  //    alone gives the colour.
  const si = in0 ? s0 : s1, so = in0 ? s1 : s0, ei = in0 ? q0 : q1, eo = in0 ? q1 : q0, cin = si.c, cout = so.c, qi = 4 * ei, qo = 4 * eo;
  let w = s, from = null, cut = so.wall[eo] === 1;
  if (!cut && axis === 2 && so.zc > L) {
    const reached = (L - si.zc) / (so.zc - si.zc);
    cut = si.own[ei] + reached * (so.own[eo] - si.own[ei]) <= L || L - (si.zc + s * (so.zc - si.zc)) <= MESH_FACE_NEAR * h;
  }
  if (cut) {
    from = meshFaceFrom(g, si, ei, so, eo);
    if (from) { const c = g.faceCol || (g.faceCol = [0, 0, 0]); for (let k = 0; k < 3; k++) c[k] = from[0][from[1] + k]; }
  } else if (MESH_FACE_RULE2 && meshHoldsFace(g, si, ei) && !meshHoldsFace(g, so, eo)) w = 1;
  else if (so.drop && so.drop[eo]) w = 0;   // 3. an outside end that meshThin put outside holds the colour of a layer the model leaves out
  for (let k = 0; k < 3; k++) {
    const lin = from ? from[0][from[1] + k] : cut && g.faceCol ? g.faceCol[k] : cin[qi + k] * (1 - w) + cout[qo + k] * w;
    g.col[p + k] = lin > 0 ? Math.round(255 * Math.pow(Math.min(lin, 1), 1 / 2.2)) : 0;   // files hold display values, not linear light
  }
  return v;
}
// Triangles between slice A (grid height k) and slice B above it. xA, yA, xB, yB, zE remember the point made
// on each grid edge: along x and along y within each slice, and on the uprights between the two.
function meshMarch(g, A, B, k, xA, yA, xB, yB, zE) {
  const n = g.n, tri = MESH.tri, mA = A.m, mB = B.m, ev = g.ev;
  for (let j = 0; j < n - 1; j++) {
    const inside = A.rows[j] + A.rows[j + 1] + B.rows[j] + B.rows[j + 1];
    if (inside === 0) continue;
    for (let i = 0, q = j * n; i < n - 1; i++, q++) {
      const c = mA[q] | mA[q + 1] << 1 | mA[q + n + 1] << 2 | mA[q + n] << 3 | mB[q] << 4 | mB[q + 1] << 5 | mB[q + n + 1] << 6 | mB[q + n] << 7;
      if (c === 0 || c === 255) continue;
      const bits = MESH_EDGE_TABLE[c];
      for (let e = 0; e < 12; e++) {
        if (!(bits >> e & 1)) continue;
        const at = MESH_EDGE_AT[e], axis = at[3], up = at[2], w = q + at[1] * n + at[0];
        const map = axis === 2 ? zE : axis === 0 ? (up ? xB : xA) : (up ? yB : yA);
        if (map[w] < 0) map[w] = meshPoint(g, up ? B : A, up || axis === 2 ? B : A, w, axis === 0 ? w + 1 : axis === 1 ? w + n : w, i + at[0], j + at[1], k + up, axis);
        ev[e] = map[w];
      }
      if (g.ni + 15 > g.idx.length) { const idx = new Uint32Array(2 * g.idx.length); idx.set(g.idx); g.idx = idx; }
      for (let t = 16 * c; tri[t] >= 0; t++) g.idx[g.ni++] = ev[tri[t]];
    }
  }
}
// The whole mesh: positions in grid cells (g.pos), display colours (g.col), triangles as point numbers (g.idx).
async function meshBuild(job, box) {
  const o = job.opt, N = o.cells, pad = 2 + Math.ceil(o.offset);
  const ext = [box[1] - box[0], box[3] - box[2], box[5] - box[4]], h = Math.max(...ext) / Math.max(8, N - 2 * pad);
  const cells = ext.map(e => Math.min(N, Math.ceil(e / h - 1e-9) + 2 * pad));
  const n = Math.max(cells[0], cells[1]) + 1, nz = cells[2] + 1, side = n * h;
  const cx = (box[0] + box[1]) / 2, cy = (box[2] + box[3]) / 2, z0 = (box[4] + box[5]) / 2 - cells[2] * h / 2;
  // thin: for a solid made by a trap, how far (in cells, along each axis) meshThin looks for a part thick enough to keep.
  // The samples it looks at lie up to the offset and one cell from such a part, and each of those has a sample inside
  // the part no more than one cell further on. (With one cell less, the samples just outside the model's surface
  // lost their estimate wherever the surface lay square to the grid, and the surface came out in terraces.)
  const R0 = job.trap ? Math.floor(o.offset) + 2 : 0;
  const g = { n, nz, h, level: o.offset * h, reach: Math.min(8, pad), thin: R0, thinT: MESH_THIN * h, faceCol: null, nv: 0, ni: 0, ev: new Int32Array(12),
    org: [cx - (n - 1) * h / 2, cy - (n - 1) * h / 2, z0], pos: new Float32Array(3 << 14), col: new Uint8Array(3 << 14), idx: new Uint32Array(3 << 15) };
  let xA = new Int32Array(n * n).fill(-1), yA = new Int32Array(n * n).fill(-1), xB = new Int32Array(n * n), yB = new Int32Array(n * n);
  const zE = new Int32Array(n * n), began = performance.now();
  // A slice is turned into distances once the slice above it has been read (meshTrue looks at both neighbours),
  // so the marching runs one slice behind the reading, and three raw slices are held. For a solid made by a trap
  // the reading runs g.thin slices further ahead: a slice can be thinned once the thick parts of the g.thin slices
  // above it are known, and those of a slice are known once the slice above that one has been read.
  if (R0 && job.snap) {
    // the size of a pixel of the picture where the solid is (as the picture works it out: gPix in 30-shaders.js)
    const b = job.snap.basis, st = job.snap.stage, v = job.snap.S && job.snap.S.view;
    const px = b && st && v ? 2 * v.fov * Math.hypot(b.pos[0] - cx, b.pos[1] - cy, b.pos[2] - (box[4] + box[5]) / 2) / st.ph : NaN;
    if (px > 0 && isFinite(px)) g.thinT = h * clamp(MESH_THIN_PX * px / h, MESH_THIN, 1);
  }
  const R = g.thin, look = R + 1, raw = [], deep = [];   // raw slices and what meshCore found, by slice number, let go once nothing needs them
  let A = null;
  meshTables();
  for (let k = 0; k < nz + look; k++) {
    if (k < nz) raw[k] = await job.sample(cx, cy, side, z0 + k * h, n);
    if (R && k >= 1 && k <= nz) deep[k - 1] = meshCore(g, raw[k - 2] || null, raw[k - 1], raw[k] || null);
    const at = k - look;
    if (at >= 0) {
      const z = z0 + at * h, mid = raw[at], T = meshTrue(g, raw[at - 1] || null, mid, raw[at + 1] || null);
      const drop = R ? meshThin(g, T, deep, raw, at) : null;
      const Bs = meshSlice(g, meshField(job, mid, cx, cy, side, z, n, T), mid, at === 0 || at === nz - 1, T.f, T.own, job.cutOn ? z - job.cut : -Infinity, drop);
      if (A) {
        xB.fill(-1); yB.fill(-1); zE.fill(-1);
        meshMarch(g, A, Bs, at - 1, xA, yA, xB, yB, zE);
        [xA, xB, yA, yB] = [xB, xA, yB, yA];
      }
      A = Bs;
      if (at >= 2) raw[at - 2] = null;
      if (R && at >= R) deep[at - R] = null;
      if (g.ni > 3 * MESH_MAX_TRIS) throw meshStop('big');
    }
    if (k >= nz) continue;
    job.left = (performance.now() - began) * (nz - 1 - k) / (k + 1);
    await job.turn(`Building the mesh, slice ${k + 1} of ${nz}`, 0.1 + 0.7 * (k + 1) / nz, true);
  }
  job.left = 0;
  return g;
}

// ---------- the finished mesh: loose pieces, measurements
// Count the pieces and, with `keep`, drop all but the largest. Two points belong to one piece when a triangle
// joins them (union-find over the points).
// The largest piece is the one with the most triangles among the pieces that enclose a volume. A piece whose
// volume comes out negative faces inward: it is the wall of a hollow inside another piece and no body by itself.
// (Chosen by its triangles alone, the inner wall of a hollow trap solid was kept at offset 0: a ball turned inside
// out, with a negative volume in the readme.)
// Returns { pieces, best, seen, seenTris, inward }: the number of pieces; the triangles of the largest; how many of
// the other pieces can be seen from outside, and their triangles (a piece inside the largest one cannot, and nor
// can the wall of a hollow); inward is true when no piece encloses a volume, which a closed mesh never gives.
async function meshPieces(job, g, keep) {
  const nv = g.nv, ni = g.ni, idx = g.idx, P = g.pos, par = new Int32Array(nv), count = new Int32Array(nv), vol = new Float64Array(nv), CHUNK = 3 << 16;
  for (let i = 0; i < nv; i++) par[i] = i;
  const find = v => { while (par[v] !== v) { par[v] = par[par[v]]; v = par[v]; } return v; };
  for (let t = 0; t < ni; t += 3) {
    const a = find(idx[t]), b = find(idx[t + 1]);
    if (a !== b) par[b] = a;
    const c = find(idx[t + 2]);
    if (c !== a) par[c] = a;
    if (t % CHUNK === 0) await job.turn('Looking for loose pieces', 0.8 + 0.01 * t / ni);
  }
  // triangles and six times the volume of each piece, kept at the point that stands for the piece
  const ox = g.n / 2, oy = g.n / 2, oz = g.nz / 2;
  let pieces = 0;
  for (let t = 0; t < ni; t += 3) {
    const r = find(idx[t]), a = 3 * idx[t], b = 3 * idx[t + 1], c = 3 * idx[t + 2];
    if (count[r]++ === 0) pieces++;
    const ax = P[a] - ox, ay = P[a + 1] - oy, az = P[a + 2] - oz, bx = P[b] - ox, by = P[b + 1] - oy, bz = P[b + 2] - oz, ux = P[c] - ox, uy = P[c + 1] - oy, uz = P[c + 2] - oz;
    vol[r] += ax * (by * uz - bz * uy) + ay * (bz * ux - bx * uz) + az * (bx * uy - by * ux);
    if (t % CHUNK === 0) await job.turn('Looking for loose pieces', 0.81 + 0.005 * t / ni);
  }
  let best = -1, most = -1;
  for (let v = 0; v < nv; v++) {
    if (count[v] === 0) continue;
    if (most < 0 || count[v] > count[most]) most = v;
    if (vol[v] > 0 && (best < 0 || count[v] > count[best])) best = v;
  }
  const inward = best < 0, out = { pieces, best: 0, seen: 0, seenTris: 0, inward };
  if (inward) best = most;
  out.best = count[best];
  if (pieces > 1) {
    // Which of the other pieces lie inside the largest one? One point of each (the middle of one of its triangles)
    // is asked how often a line straight up from it passes through the largest piece: an odd number means inside.
    // The triangles of a cell lie over that cell alone, so each one is tried against the points under its own cell.
    // A point over a line of the grid is not used: there the line up could run along the sides of triangles.
    const probes = new Map(), cols = new Map(), n = g.n;
    for (let t = 0; t < ni; t += 3) {
      const r = find(idx[t]);
      if (r === best || !(vol[r] > 0) || probes.has(r)) continue;
      const a = 3 * idx[t], b = 3 * idx[t + 1], c = 3 * idx[t + 2], x = (P[a] + P[b] + P[c]) / 3, y = (P[a + 1] + P[b + 1] + P[c + 1]) / 3;
      const fx = x - Math.floor(x), fy = y - Math.floor(y);
      if (fx < 1e-3 || fx > 0.999 || fy < 1e-3 || fy > 0.999) continue;
      const pr = { x, y, z: (P[a + 2] + P[b + 2] + P[c + 2]) / 3, hits: 0 }, key = Math.floor(x) + n * Math.floor(y), list = cols.get(key);
      probes.set(r, pr);
      if (list) list.push(pr); else cols.set(key, [pr]);
      if (t % CHUNK === 0) await job.turn('Looking for loose pieces', 0.815);
    }
    for (let t = 0; t < ni && cols.size; t += 3) {
      if (t % CHUNK === 0) await job.turn('Looking for loose pieces', 0.815 + 0.005 * t / ni);
      if (find(idx[t]) !== best) continue;
      const a = 3 * idx[t], b = 3 * idx[t + 1], c = 3 * idx[t + 2], x1 = P[a], y1 = P[a + 1], x2 = P[b], y2 = P[b + 1], x3 = P[c], y3 = P[c + 1];
      const list = cols.get(Math.floor((x1 + x2 + x3) / 3) + n * Math.floor((y1 + y2 + y3) / 3));
      if (!list) continue;
      const den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
      if (den === 0) continue;   // seen edge on from above
      for (const pr of list) {
        const u = ((y2 - y3) * (pr.x - x3) + (x3 - x2) * (pr.y - y3)) / den, w = ((y3 - y1) * (pr.x - x3) + (x1 - x3) * (pr.y - y3)) / den;
        if (u >= 0 && w >= 0 && u + w <= 1 && u * P[a + 2] + w * P[b + 2] + (1 - u - w) * P[c + 2] > pr.z) pr.hits++;
      }
    }
    for (let v = 0; v < nv; v++) {
      if (count[v] === 0 || v === best || !(vol[v] > 0)) continue;
      const pr = probes.get(v);
      if (pr && pr.hits % 2 === 1) continue;
      out.seen++; out.seenTris += count[v];
    }
  }
  if (!keep || pieces < 2) return out;
  // Close the gaps in the arrays. Points keep their order, so each one moves down or stays: nothing that is
  // still to be moved gets overwritten. Every point is a corner of some triangle, so its piece is known.
  const to = new Int32Array(nv), kept = new Uint32Array(3 * count[best]);
  let nn = 0, ki = 0;
  for (let v = 0; v < nv; v++) {
    to[v] = find(v) === best ? nn : -1;
    if (to[v] < 0) continue;
    for (let k = 0; k < 3; k++) { g.pos[3 * nn + k] = g.pos[3 * v + k]; g.col[3 * nn + k] = g.col[3 * v + k]; }
    nn++;
    if (v % CHUNK === 0) await job.turn('Leaving out loose pieces', 0.82 + 0.01 * v / nv);
  }
  for (let t = 0; t < ni; t += 3) {
    if (to[idx[t]] < 0) continue;
    kept[ki++] = to[idx[t]]; kept[ki++] = to[idx[t + 1]]; kept[ki++] = to[idx[t + 2]];
    if (t % CHUNK === 0) await job.turn('Leaving out loose pieces', 0.83 + 0.01 * t / ni);
  }
  g.idx = kept; g.ni = ki; g.nv = nn;
  return out;
}
// Size and placement of the saved model. The mesh is scaled so that its longest side is `mm` millimetres, set
// on z = 0 and centred on the z-axis. The result turns grid cells into millimetres: (p - o) * s.
async function meshMeasure(job, g, mm) {
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity], P = g.pos, I = g.idx, CHUNK = 3 << 17;
  for (let v = 0, p = 0; v < g.nv; v++) for (let k = 0; k < 3; k++, p++) { if (P[p] < lo[k]) lo[k] = P[p]; if (P[p] > hi[k]) hi[k] = P[p]; }
  const s = mm / Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], 1e-9), o = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]];
  let vol = 0;   // six times the volume, in cells: the sum of a . (b x c) over the triangles
  for (let t = 0; t < g.ni; t += 3) {
    const a = 3 * I[t], b = 3 * I[t + 1], c = 3 * I[t + 2];
    const ax = P[a] - o[0], ay = P[a + 1] - o[1], az = P[a + 2] - o[2], bx = P[b] - o[0], by = P[b + 1] - o[1], bz = P[b + 2] - o[2];
    const ux = P[c] - o[0], uy = P[c + 1] - o[1], uz = P[c + 2] - o[2];
    vol += ax * (by * uz - bz * uy) + ay * (bz * ux - bx * uz) + az * (bx * uy - by * ux);
    if (t % CHUNK === 0) await job.turn('Measuring the model', 0.84);
  }
  return { s, o, size: [0, 1, 2].map(k => (hi[k] - lo[k]) * s), volume: vol / 6 * s * s * s, unit: s / g.h };
}

// ---------- the three kinds of file. Each returns its bytes as a list of pieces.
// STL, binary: an 80-byte heading, the count, then 50 bytes a triangle (its normal, three corners, two spare bytes).
async function meshStl(job, g, T, f0, f1) {
  const nt = g.ni / 3, dv = new DataView(new ArrayBuffer(84 + 50 * nt)), P = g.pos, I = g.idx, s = T.s, q = new Float64Array(9);
  const head = 'Binary STL from 3D Squaring Lab. Units: millimetres.';   // must not begin with the word solid
  for (let i = 0; i < head.length; i++) dv.setUint8(i, head.charCodeAt(i));
  dv.setUint32(80, nt, true);
  for (let t = 0, at = 84; t < nt; t++, at += 50) {
    for (let e = 0; e < 3; e++) { const p = 3 * I[3 * t + e]; for (let k = 0; k < 3; k++) q[3 * e + k] = (P[p + k] - T.o[k]) * s; }
    const ux = q[3] - q[0], uy = q[4] - q[1], uz = q[5] - q[2], vx = q[6] - q[0], vy = q[7] - q[1], vz = q[8] - q[2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, nl = Math.hypot(nx, ny, nz) || 1;
    dv.setFloat32(at, nx / nl, true); dv.setFloat32(at + 4, ny / nl, true); dv.setFloat32(at + 8, nz / nl, true);
    for (let k = 0; k < 9; k++) dv.setFloat32(at + 12 + 4 * k, q[k], true);
    if ((t & 8191) === 8191) await job.turn('Writing the STL file', f0 + (f1 - f0) * t / nt);
  }
  return [new Uint8Array(dv.buffer)];
}
// PLY, binary and little-endian: 15 bytes a point (x, y, z as floats, then red, green, blue), 13 bytes a triangle.
async function meshPly(job, g, T, f0, f1) {
  const nt = g.ni / 3, nv = g.nv, P = g.pos, I = g.idx, C = g.col, s = T.s;
  const head = new TextEncoder().encode('ply\nformat binary_little_endian 1.0\ncomment 3D Squaring Lab. Units: millimetres.\n' +
    `element vertex ${nv}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\n` +
    `element face ${nt}\nproperty list uchar int vertex_indices\nend_header\n`);
  const dv = new DataView(new ArrayBuffer(15 * nv + 13 * nt));
  for (let v = 0, at = 0; v < nv; v++, at += 15) {
    for (let k = 0; k < 3; k++) { dv.setFloat32(at + 4 * k, (P[3 * v + k] - T.o[k]) * s, true); dv.setUint8(at + 12 + k, C[3 * v + k]); }
    if ((v & 16383) === 16383) await job.turn('Writing the PLY file', f0 + (f1 - f0) * 0.5 * v / nv);
  }
  for (let t = 0, at = 15 * nv; t < nt; t++, at += 13) {
    dv.setUint8(at, 3);
    for (let e = 0; e < 3; e++) dv.setInt32(at + 1 + 4 * e, I[3 * t + e], true);
    if ((t & 16383) === 16383) await job.turn('Writing the PLY file', f0 + (f1 - f0) * (0.5 + 0.5 * t / nt));
  }
  return [head, new Uint8Array(dv.buffer)];
}
// Text written straight into bytes: a model has millions of numbers, far more than one string can hold.
function meshText() {
  let buf = new Uint8Array(1 << 21), n = 0;
  const parts = [], digits = new Uint8Array(20);
  const whole = v => { let k = 0; do { digits[k++] = 48 + v % 10; v = Math.floor(v / 10); } while (v > 0); while (k > 0) buf[n++] = digits[--k]; };
  return {
    room() { if (n > buf.length - 128) { parts.push(buf.subarray(0, n)); buf = new Uint8Array(1 << 21); n = 0; } },   // call once a line
    str(s) { for (let i = 0; i < s.length; i++) buf[n++] = s.charCodeAt(i); },
    int: whole,
    num(v, dec) {   // a number with `dec` decimals
      const p = 10 ** dec, x = Math.round(Math.abs(v) * p), w = Math.floor(x / p);
      if (v < 0 && x > 0) buf[n++] = 45;
      whole(w); buf[n++] = 46;
      for (let f = x - w * p, q = p / 10; q >= 1; q /= 10) { const dgt = Math.floor(f / q); buf[n++] = 48 + dgt; f -= dgt * q; }
    },
    done() { parts.push(buf.subarray(0, n)); return parts; },
  };
}
// OBJ, text: "v x y z r g b" for a point with its colour (0 to 1), "f a b c" for a triangle, counting from 1.
// OBJ files are read with y pointing up, so the lab's (x, y, z) is written as (x, z, -y): that way the model
// stands the same way up as the STL and PLY when a program applies its usual OBJ turn.
async function meshObj(job, g, T, f0, f1, title) {
  const nt = g.ni / 3, nv = g.nv, P = g.pos, I = g.idx, C = g.col, s = T.s, w = meshText();
  const head = new TextEncoder().encode(`# 3D Squaring Lab: ${title}\n# Units: millimetres. y points up. Each v line: x y z, then red green blue from 0 to 1.\no model\n`);
  for (let v = 0; v < nv; v++) {
    const p = 3 * v;
    w.room(); w.str('v ');
    w.num((P[p] - T.o[0]) * s, 4); w.str(' '); w.num((P[p + 2] - T.o[2]) * s, 4); w.str(' '); w.num(-(P[p + 1] - T.o[1]) * s, 4);
    for (let k = 0; k < 3; k++) { w.str(' '); w.num(C[p + k] / 255, 3); }
    w.str('\n');
    if ((v & 8191) === 8191) await job.turn('Writing the OBJ file', f0 + (f1 - f0) * 0.6 * v / nv);
  }
  for (let t = 0; t < nt; t++) {
    w.room(); w.str('f ');
    w.int(I[3 * t] + 1); w.str(' '); w.int(I[3 * t + 1] + 1); w.str(' '); w.int(I[3 * t + 2] + 1); w.str('\n');
    if ((t & 16383) === 16383) await job.turn('Writing the OBJ file', f0 + (f1 - f0) * (0.6 + 0.4 * t / nt));
  }
  return [head, ...w.done()];
}

// ---------- zip
function meshCrc(bytes, crc) {   // CRC-32 of `bytes`, carrying on from the CRC of what came before (0 at the start)
  if (!MESH.crc) {
    MESH.crc = new Uint32Array(256);
    for (let i = 0; i < 256; i++) { let c = i; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; MESH.crc[i] = c; }
  }
  const T = MESH.crc;
  let c = ~crc;
  for (let i = 0; i < bytes.length; i++) c = T[(c ^ bytes[i]) & 255] ^ (c >>> 8);
  return ~c >>> 0;
}
const meshParts = data => (Array.isArray(data) ? data : [typeof data === 'string' ? new TextEncoder().encode(data) : data]);
// entries: [{ name, parts: [Uint8Array], crc }]. Every entry is stored as it is, without compression.
function meshZipBlob(entries) {
  const now = new Date(), time = now.getHours() << 11 | now.getMinutes() << 5 | now.getSeconds() >> 1;
  const date = Math.max(0, now.getFullYear() - 1980) << 9 | (now.getMonth() + 1) << 5 | now.getDate();
  const out = [], dir = [];
  let at = 0;
  for (const e of entries) {
    const name = new TextEncoder().encode(e.name), size = e.parts.reduce((a, p) => a + p.length, 0);
    if (at + size > 0xfff00000) throw meshStop('bytes');   // the plain zip layout counts in 32 bits
    const local = new DataView(new ArrayBuffer(30)), cd = new DataView(new ArrayBuffer(46));
    // shared by both headers: version needed 2.0, names in UTF-8, method 0 (stored), time, date, CRC, the size twice
    const common = (dv, o) => {
      dv.setUint16(o, 20, true); dv.setUint16(o + 2, 0x0800, true); dv.setUint16(o + 4, 0, true); dv.setUint16(o + 6, time, true); dv.setUint16(o + 8, date, true);
      dv.setUint32(o + 10, e.crc, true); dv.setUint32(o + 14, size, true); dv.setUint32(o + 18, size, true); dv.setUint16(o + 22, name.length, true);
    };
    local.setUint32(0, 0x04034b50, true); common(local, 4);
    cd.setUint32(0, 0x02014b50, true); cd.setUint16(4, 20, true); common(cd, 6); cd.setUint32(42, at, true);
    out.push(new Uint8Array(local.buffer), name, ...e.parts);
    dir.push(new Uint8Array(cd.buffer), name);
    at += 30 + name.length + size;
  }
  const end = new DataView(new ArrayBuffer(22)), dirSize = dir.reduce((a, p) => a + p.length, 0);
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, entries.length, true); end.setUint16(10, entries.length, true);
  end.setUint32(12, dirSize, true); end.setUint32(16, at, true);
  return new Blob([...out, ...dir, new Uint8Array(end.buffer)], { type: 'application/zip' });
}
// A plain zip of files = [{ name, data }], data a Uint8Array or a string: stored entries with correct CRC-32.
function zipStore(files) {
  return meshZipBlob(files.map(f => { const parts = meshParts(f.data); return { name: f.name, parts, crc: parts.reduce((c, p) => meshCrc(p, c), 0) }; }));
}
// The same for the model's own files, which can be hundreds of megabytes: the CRC is worked out a few megabytes a turn.
async function meshZip(job, files) {
  const total = files.reduce((a, f) => a + f.size, 0);
  let seen = 0;
  for (const f of files) {
    f.crc = 0;
    for (const p of f.parts) {
      for (let o = 0; o < p.length; o += 1 << 22) {
        const piece = p.subarray(o, o + (1 << 22));
        f.crc = meshCrc(piece, f.crc); seen += piece.length;
        await job.turn('Packing the zip', 0.97 + 0.03 * seen / Math.max(1, total));
      }
    }
  }
  return meshZipBlob(files);
}

// ---------- the job
const meshCount = n => Math.round(n).toLocaleString('en-US');
const meshMm = v => (v >= 99.95 ? v.toFixed(0) : v.toFixed(1));
// A share of the surface, in words. It is counted in triangles, which are all about the same size.
const meshShare = f => (f < 0.01 ? 'less than 1%' : f > 0.99 ? 'more than 99%' : `about ${Math.round(100 * f)}%`);
function meshBytes(n) { return n >= 1048576 ? (n / 1048576).toFixed(n >= 10485760 ? 0 : 1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' kB'; }
function meshReadme(job, info) {
  const o = job.opt, f = info.files, line = (name, text) => '  ' + name.padEnd(info.base.length + 6) + text;
  return [
    '3D Squaring Lab: a 3D model',
    '',
    'Made from: ' + job.what + '.',
    'Made on:   ' + new Date(Date.now() - 60000 * new Date().getTimezoneOffset()).toISOString().slice(0, 16).replace('T', ' '),
    '',
    'What is in this zip',
    ...(f.stl ? [line(info.base + '.stl', 'The surface as triangles, without colours. For 3D printing and any 3D program.')] : []),
    ...(f.obj ? [line(info.base + '.obj', 'The same surface with a colour at every point.')] : []),
    ...(f.ply ? [line(info.base + '.ply', 'The same surface with colours, in a compact binary form.')] : []),
    line('readme.txt', 'This note.'),
    '',
    'The model',
    `  Size:       ${info.size.map(meshMm).join(' x ')} mm. The longest side was set to ${dialFmt(o.mm)} mm.`,
    `  Triangles:  ${meshCount(info.tris)}`,
    `  Points:     ${meshCount(info.points)}`,
    info.inward ? '  Volume:     none. The surface faces inward, like the wall of a hollow.' : `  Volume:     ${(info.volume / 1000).toPrecision(4)} cubic centimetres`,
    `  Grid:       ${o.cells} cells across. ` + (o.offset > 0 ? `The surface was moved outward by about ${dialFmt(o.offset)} ${o.offset === 1 ? 'cell' : 'cells'}, which is ${(o.offset * info.cell).toFixed(2)} mm.` : 'The surface was not moved outward.'),
    ...(job.trap ? ['              A trap makes layers without end, each thinner than the last. Layers thinner than about', '              one cell were left out, as the picture leaves out layers too thin for it to draw.'] : []),
    '  Pieces:     ' + (!o.largest ? `all ${meshCount(info.pieces)} of them.` : info.pieces < 2 ? 'one.' : info.seen
      ? `the largest only, which holds ${meshShare(info.kept)} of the surface that can be seen. ${meshCount(info.pieces - 1)} other ${info.pieces === 2 ? 'piece was' : 'pieces were'} left out.`
      : `the largest only. ${info.pieces === 2 ? 'The other piece lies' : `The ${meshCount(info.pieces - 1)} other pieces lie`} inside it, where nobody sees ${info.pieces === 2 ? 'it, and was' : 'them, and were'} left out.`),
    ...(job.cutOn ? [`  The solid is cut open at height z = ${dialFmt(job.cut)}, as in the picture.`] : []),
    info.inward ? '  The surface is closed, but it faces inward, so a program for 3D printing will not take it for a body.' : '  The surface is closed: it has no holes and no loose edges, so it can be printed.',
    `  The numbers in the files are millimetres. One unit of the lab's space is ${info.unit.toPrecision(4)} mm.`,
    '  The model stands on z = 0 and is centred on the z-axis.',
    '',
    'Blender',
    '  File > Import, then STL, Wavefront (.obj) or Stanford PLY (.ply).',
    '  Blender reads the numbers as metres, so the model arrives very large. Set Scale to 0.001 in the',
    '  import options for its real size.',
    '  To see the colours of the OBJ or PLY file, open the viewport shading options and set Color to',
    '  Attribute (Vertex in older versions). For a render, add a Color Attribute node to the material',
    '  and connect it to Base Color.',
    '',
    'Rhino',
    '  File > Import, then choose the file. The numbers are millimetres.',
    '  For the OBJ file keep "Map OBJ Y to Rhino Z" ticked. OBJ files are written with y pointing up,',
    '  and that setting stands the model upright, the same as the STL and PLY.',
    '',
    '3D printing',
    '  Open the STL file in your slicer. If thin parts come out too fragile, make the model again with a',
    '  larger surface offset.',
    '',
  ].join('\r\n');
}
// What the model was made from, in words, for the readme and the OBJ heading (one line, no line breaks): enough
// to tell two models apart and to make one again.
const MESH_TRAPS = ['a point', 'the three axis lines', 'a line along the ', 'a ray toward ', 'the three coordinate planes', 'a sphere shell', 'a ring in the xy-plane'];
function meshWhat() {
  const k = S.k, c = S.colour || {}, tidy = t => String(t).replace(/<[^>]*>/g, ''), vec = v => `(${v.map(dialFmt).join(', ')})`;
  const num = v => typeof v === 'number' && isFinite(v);
  // A trap that is the solid, or is added to it, shapes the model (the trap numbers are those of TRAP in 25-colour.js;
  // the last one, three tones, has no shape and makes no solid).
  let trap = '';
  if (c.solid > 0 && MESH_TRAPS[c.trap]) {
    let shape = MESH_TRAPS[c.trap];
    if (c.trap === 2) shape += (['x', 'y', 'z'][c.axis] || 'x') + '-axis';
    if (c.trap === 3) shape += ['+x', '-x', '+y', '-y', '+z', '-z'][c.ray] || '+x';
    const parts = [shape];
    if (c.trap !== 0 && num(c.radius)) parts.push(`radius ${dialFmt(c.radius)}`);
    if ([c.tx, c.ty, c.tz].every(num)) parts.push(`centre ${vec([c.tx, c.ty, c.tz])}`);
    if (num(c.thick)) parts.push(`thickness ${dialFmt(c.thick)}`);
    if (num(c.skip)) parts.push(`${c.skip} orbit ${c.skip === 1 ? 'step' : 'steps'} skipped`);
    trap = `. The trap ${c.solid > 1.5 ? 'is added to the solid' : 'is the solid'}: ${parts.join(', ')}`;
  }
  if (S.mode === 'k') {
    return `the Kleinian group with mu = ${vec([k.mx, k.my, k.mz])}, L = ${dialFmt(k.L)}, ${k.three ? 'with' : 'without'} the third map, ` +
      `turned out through the sphere of radius ${dialFmt(k.invR)} around ${vec([k.cx, k.cy, k.cz])}, depth of search ${k.iter}${trap}`;
  }
  const set = S.mode === 'j' ? `the Julia set of c = ${vec(S.c)}` : S.mosaic ? `the Julia mosaic of the Mandelbrot set (cells ${dialFmt(S.mosaicCell)} wide)` : 'the Mandelbrot set';
  const mods = ['|x|', '|y|', '|z|'].filter((m, i) => S.abs && S.abs[i]).concat(['flip y', 'flip z'].filter((m, i) => S.flip && S.flip[i]));
  return `${set} for ${S.eq}, approach "${tidy(ap().name)}", power ${dialFmt(S.n)}, ${S.iter} iterations${mods.length ? `, with the ${mods.length > 1 ? 'modifiers' : 'modifier'} ${mods.join(', ')}` : ''}${trap}`;
}
async function meshRun(job) {
  const o = job.opt;
  const box = await meshLocate(job);
  if (!box) throw meshStop('empty');
  const g = await meshBuild(job, box);
  if (!g.ni) throw meshStop('empty');
  const found = await meshPieces(job, g, o.largest), pieces = found.pieces;
  const nt = g.ni / 3, T = await meshMeasure(job, g, o.mm);
  // kept: the share the largest piece holds of the surface that can be seen from outside, counted in triangles.
  // Pieces inside the largest one, such as the inner layers of a hollow solid, are not counted: leaving them out
  // takes nothing from the model's looks (found.seen counts the other pieces that can be seen).
  // part: the largest piece is clearly not the whole of what the picture shows, and it alone was kept.
  const kept = found.best / (found.best + found.seenTris), part = o.largest && kept < MESH_KEPT_SHARE, inward = !(T.volume > 0);
  if (84 * 3 + nt * ((o.stl ? 50 : 0) + (o.obj ? 24 : 0) + (o.ply ? 13 : 0)) + g.nv * ((o.obj ? 48 : 0) + (o.ply ? 15 : 0)) > MESH_MAX_BYTES) throw meshStop('bytes');
  const base = `${job.kind}-${o.cells}`, files = [], kinds = ['stl', 'obj', 'ply'].filter(k => o[k]);
  for (let i = 0; i < kinds.length; i++) {
    const f0 = 0.84 + 0.13 * i / kinds.length, f1 = 0.84 + 0.13 * (i + 1) / kinds.length, kind = kinds[i];
    await job.turn(`Writing the ${kind.toUpperCase()} file`, f0);
    const parts = kind === 'stl' ? await meshStl(job, g, T, f0, f1) : kind === 'ply' ? await meshPly(job, g, T, f0, f1) : await meshObj(job, g, T, f0, f1, job.what);
    files.push({ name: `${base}.${kind}`, parts, size: parts.reduce((a, p) => a + p.length, 0) });
  }
  const info = { base, files: { stl: o.stl, obj: o.obj, ply: o.ply }, size: T.size, volume: T.volume, unit: T.unit, cell: T.s, tris: nt, points: g.nv, pieces, kept, part, seen: found.seen, inward };
  const readme = new TextEncoder().encode(meshReadme(job, info));
  const blob = await meshZip(job, [...files, { name: 'readme.txt', parts: [readme], size: readme.length }]);
  if (job.test) job.test.mesh = { pos: g.pos.subarray(0, 3 * g.nv), col: g.col.subarray(0, 3 * g.nv), idx: g.idx.subarray(0, g.ni), h: g.h, n: g.n, nz: g.nz, org: g.org, box, ...info };
  const facts = [['Triangles', meshCount(nt)], ['Points', meshCount(g.nv)], ['Size', info.size.map(meshMm).join(' × ') + ' mm'],
    ['Pieces', !o.largest ? meshCount(pieces) : pieces > 1 ? `The largest of ${meshCount(pieces)}` + (found.seen ? `, with ${meshShare(kept)} of the surface that can be seen` : pieces > 2 ? '. The others lie inside it.' : '. The other lies inside it.') : '1'],
    ...files.map(f => [f.name, meshBytes(f.size)]), ['Zip to save', meshBytes(blob.size)]];
  // What the user should know about this model before saving it: each a plain sentence, shown together.
  // A solid finer than the grid (a negative power: sheets thinner than a cell of any grid on offer) cannot be made
  // to match its picture by any setting. Measured on the power -2 picture at 128, 256 and 512 cells with offsets
  // 0.5, 1 and 1.5 (notes/r9-mesh.md): with every piece kept, 93 to 99% of the picture's outline is covered and
  // the shapes of the picture are there from 256 cells on, together with outer shells that the picture draws only
  // in part; the largest piece alone lacks 16 to 82% of the picture, more of it at every higher resolution; a
  // larger offset joins more pieces but thickens the sheets, and the outlines then agree less, not more. So the
  // warning says what does help, in the order that helps: the tick box first, more cells only after that.
  // Nothing is said about a model that follows its picture: one whose largest piece holds most of what can be seen,
  // however many pieces lie inside it (a hollow trap solid has hundreds of inner layers that nobody sees).
  const warn = [], fine = found.seen + 1 >= MESH_MANY_PIECES && kept < MESH_KEPT_SHARE, more = o.cells < 256 ? '256 or 512 cells' : o.cells < 512 ? '512 cells' : '';
  if (inward) warn.push('This surface faces inward, like the wall of a hollow, so a program for 3D printing will not take it for a body.' + (o.largest ? ' Untick "Keep only the largest piece" and start again.' : ''));
  else if (fine && part) {
    warn.push(`This solid has parts thinner than one cell of the grid. They came out as ${meshCount(pieces)} loose pieces, and only the largest was kept: ${meshShare(kept)} of the surface that can be seen. So this model does not look like the picture. To get closer, untick "Keep only the largest piece" and start again. ` +
      (more ? `With every piece kept, ${more} follow the picture more closely. With the box ticked, more cells tend to make the kept piece smaller. ` : '') + 'A larger surface offset joins more of the pieces, but it makes the thin parts thick.');
  } else if (fine && !o.largest) {
    warn.push(`This solid has parts thinner than one cell of the grid. They came out as ${meshCount(pieces)} loose pieces, so the model is rougher than the picture and can look unlike it. ` +
      (more ? `${more[0].toUpperCase() + more.slice(1)} follow the picture more closely. ` : '') + 'A larger surface offset joins more of the pieces, but it makes the thin parts thick.');
  } else if (part) warn.push(`Only the largest piece was kept: ${meshShare(kept)} of the surface that can be seen. Untick "Keep only the largest piece" and start again to get all ${meshCount(pieces)} pieces.`);
  if (nt > MESH_WARN_TRIS) warn.push(`This model has ${(nt / 1e6).toFixed(1)} million triangles. Above two million, many programs become slow. A lower resolution gives a lighter model.`);
  return { name: `squaring-lab-${base}.zip`, blob, facts, warn: warn.join(' ') };
}
async function meshStart() {
  if (MESH.job || MESH.result) return;
  const o = { ...MESH.opt }, test = window.squaringLabMeshTest || null, field = test && test.field;
  if (!o.stl && !o.obj && !o.ply) { meshSay(MESH_WORDS.kinds); return; }
  if (!field && (typeof takeSnapshot !== 'function' || typeof sampleSlice !== 'function')) { meshSay(MESH_WORDS.none); return; }
  if (test && test.cells) o.cells = test.cells;
  // What the model needs to know about the picture is read here, in the same moment as the snapshot is taken.
  const job = MESH.job = { opt: o, test, cancel: false, step: 'Starting', frac: 0, left: 0, last: performance.now(), snap: null,
    bound: S.view.bound, cutOn: S.cutOn, cut: S.cut, kind: field ? 'test-' + field : MESH_NAMES[S.mode] || 'model',
    // the solid is made by a trap, alone or together with the set (the renderer's own test: colProgramNeeds in 25-colour.js)
    trap: !field && typeof colProgramNeeds === 'function' && colProgramNeeds().solid ? 1 : 0,
    what: field ? `the built-in test field "${field}"` : meshWhat() };
  job.sample = async (cx, cy, side, z, n) => {
    const raw = await (field ? meshTestSlice(field, cx, cy, side, z, n) : sampleSlice(job.snap, cx, cy, side, z, n));
    if (job.cancel) throw meshStop('cancel');
    if (!raw) throw meshStop('sample');
    return raw;
  };
  // Called between pieces of work: notes the progress and gives the page its turn (always after a slice,
  // otherwise once the work has held the thread for a while).
  job.turn = async (step, frac, always) => {
    job.step = step; job.frac = frac;
    if (always || performance.now() - job.last > 12) { meshPaint(); await meshYield(); job.last = performance.now(); }
    if (job.cancel) throw meshStop('cancel');
  };
  // The browser can take the page's graphics away at any moment (and gives them back later). A job that was
  // reading the picture then cannot go on, and the reason is not that the picture was still being drawn.
  const canvas = document.getElementById('view'), onLost = () => { job.lost = true; };
  if (canvas && !field) canvas.addEventListener('webglcontextlost', onLost);
  meshSay(''); meshShow(true);
  try {
    if (!field) { job.snap = takeSnapshot(); await meshPrepare(job); }
    MESH.result = await meshRun(job);
    meshSay('The model is ready.');
  } catch (err) {
    let code = err && err.mesh;
    if (!field && (code === 'sample' || !code) && (job.lost || meshGraphicsLost(canvas))) code = 'lost';
    else if (!code) console.error('The 3D model could not be built: ' + (err && err.stack || err));
    meshSay(MESH_WORDS[code] || MESH_WORDS.failed);
  } finally {
    if (canvas) canvas.removeEventListener('webglcontextlost', onLost);
    if (job.snap && typeof releaseSnapshot === 'function') { try { releaseSnapshot(job.snap); } catch (err) { console.error(err); } }
    MESH.job = null;
    meshShow(true);
  }
}
// The first model of a formula waits while the browser prepares the program its samples are drawn with (the
// renderer starts that program when a model first asks for it: snapProg in 40-render.js answers 'wait' until it is
// there). That takes a few seconds, and until now the panel said "Starting. 0%." all the while. The progress line
// says in plain words what is going on, for as long as it lasts, and counts the seconds once there are two.
async function meshPrepare(job) {
  if (typeof snapProg !== 'function') return;
  const began = performance.now();
  job.plain = true;   // the line shows the step as it is, without a percentage
  try {
    while (snapProg(job.snap, true) === 'wait') {
      const s = Math.round((performance.now() - began) / 1000);
      await job.turn(MESH_WORDS.prepare + (s >= 2 ? ` ${s} seconds so far.` : ''), 0, true);
      await new Promise(done => setTimeout(done, 60));
    }
  } finally { job.plain = false; }
}
// True while the page's graphics are gone. Asked of the canvas itself, so it needs nothing from the renderer.
function meshGraphicsLost(canvas) {
  try {
    const ctx = canvas && canvas.getContext('webgl2');
    return !!ctx && ctx.isContextLost();
  } catch (err) { return false; }
}
async function meshSave() {
  const r = MESH.result;
  if (!r || r.saving) return;
  r.saving = true;
  let out = null;
  // saveFile promises not to throw; if it ever does, the button must still work for the next press
  try { out = await saveFile(r.name, r.blob); } catch (err) { console.error('Saving the model failed: ' + (err && err.stack || err)); } finally { r.saving = false; }
  if (MESH.result !== r) return;
  if (out && out.ok) meshSay(`Saved as ${r.name}. You can save it again, or discard it to make another model.`);
  else meshSay(`${out && out.message || 'The file could not be saved.'} The model is still here${out && out.again === false ? '.' : ', so you can try again.'}`);
}

// ---------- the panel
function meshSay(text) { const u = MESH.ui; if (u && u.msg.textContent !== text) u.msg.textContent = text; }
function meshPaint() {   // the progress of the running job
  const u = MESH.ui, job = MESH.job;
  if (!u || !job) return;
  const pc = Math.round(100 * clamp(job.frac, 0, 1)), s = job.left / 1000;
  u.fill.style.transform = `scaleX(${(pc / 100).toFixed(2)})`;
  u.bar.setAttribute('aria-valuenow', pc);
  const left = s < 3 ? '' : s < 90 ? ` About ${Math.round(s)} seconds left.` : ` About ${Math.round(s / 60)} minutes left.`;
  const text = job.plain ? job.step : `${job.step}. ${pc}%.${left}`;
  if (u.step.textContent !== text) u.step.textContent = text;
}
// Show the block that fits the state: the start button, the running job, or the finished model. With `move`,
// the keyboard focus follows when the button it was on has just gone.
function meshShow(move) {
  const u = MESH.ui, job = MESH.job, res = MESH.result;
  if (!u) return;
  const lost = move && [u.start, u.cancel, u.save, u.discard].includes(document.activeElement);
  u.idle.hidden = !!job || !!res; u.run.hidden = !job; u.done.hidden = !!job || !res;
  if (job) meshPaint();
  if (res && !job) {
    u.facts.textContent = '';
    res.facts.forEach(([k, v]) => { u.facts.appendChild(Object.assign(document.createElement('dt'), { textContent: k })); u.facts.appendChild(Object.assign(document.createElement('dd'), { textContent: v })); });
    u.warn.textContent = res.warn; u.warn.hidden = !res.warn;
  }
  if (lost) (job ? u.cancel : res ? u.save : u.start).focus();
}
function buildMeshPanel(host) {
  host = typeof host === 'string' ? $(host) : host;
  if (!host || MESH.ui) return;
  const O = MESH.opt, grp = { group: 'mesh' };
  const make = (parent, tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; parent.appendChild(e); return e; };
  const button = (parent, id, text, act) => { const b = make(parent, 'button', 'btn', text); b.type = 'button'; b.id = id; b.addEventListener('click', act); return b; };
  host.classList.add('mesh-panel');
  make(host, 'p', 'note', 'Turns the solid into a mesh of triangles and packs it in a zip, ready for Blender, Rhino or a 3D printer. The model is taken from the picture as it is when you press Start. What you change afterwards does not affect it.');
  addSelect(host, 'meshCells', 'Resolution, cells across the solid', [[96, '96 (quickest)'], [128, '128'], [192, '192'], [256, '256'], [384, '384'], [512, '512 (slow, large files)']],
    () => O.cells, v => { O.cells = v; }, { ...grp, def: 128, help: 'More cells show finer detail and take longer. Each doubling makes the files about four times larger.' });
  addDial(host, 'meshOffset', 'Surface offset, grid cells', 0, 2, 0.05, () => O.offset, v => { O.offset = v; },
    { ...grp, def: 0.5, xmax: 4, xhi: 8, help: 'Moves the surface outward by about this many cells, the same on every side. Thin parts get thicker, which a printer needs. At 0 the surface is where the picture has it, and parts thinner than a cell can break up.' });
  addDial(host, 'meshMm', 'Longest side, mm', 10, 300, 1, () => O.mm, v => { O.mm = v; },
    { ...grp, def: 100, lo: 1, hi: 2000, xmax: 2000, xhi: 100000, help: 'The saved model is scaled so that its longest side has this length.' });
  addCheck(host, 'meshLargest', 'Keep only the largest piece', () => O.largest, v => { O.largest = !!v; }, { ...grp, def: true, help: 'Leaves out loose pieces, which make a print fail. Untick it when the picture is made of several separate parts.' });
  const kinds = make(host, 'div', 'field mesh-kinds'), label = make(kinds, 'span', 'label', 'Files to put in the zip'), checks = make(kinds, 'div', 'checks');
  label.id = 'meshKindsLabel'; kinds.setAttribute('role', 'group'); kinds.setAttribute('aria-labelledby', label.id);
  addCheck(checks, 'meshStl', 'STL, for printing', () => O.stl, v => { O.stl = !!v; }, { ...grp, def: true });
  addCheck(checks, 'meshObj', 'OBJ, with colours', () => O.obj, v => { O.obj = !!v; }, { ...grp, def: true });
  addCheck(checks, 'meshPly', 'PLY, with colours', () => O.ply, v => { O.ply = !!v; }, { ...grp, def: true });
  const idle = make(host, 'div', 'row-btns'), run = make(host, 'div', 'mesh-run'), bar = make(run, 'div', 'mesh-bar');
  const u = MESH.ui = { idle, run, bar, fill: make(bar, 'span'), step: make(run, 'p', 'mesh-step') };
  bar.id = 'meshBar'; bar.setAttribute('role', 'progressbar'); bar.setAttribute('aria-label', 'Progress of the 3D model');
  bar.setAttribute('aria-valuemin', 0); bar.setAttribute('aria-valuemax', 100);
  u.step.id = 'meshStep';
  u.start = button(idle, 'meshStart', 'Start the model', meshStart);
  u.cancel = button(make(run, 'div', 'row-btns'), 'meshCancel', 'Cancel', () => { if (MESH.job) MESH.job.cancel = true; });
  u.done = make(host, 'div', 'mesh-done');
  u.facts = make(u.done, 'dl', 'mesh-facts'); u.facts.id = 'meshFacts';
  u.warn = make(u.done, 'p', 'note mesh-warn'); u.warn.id = 'meshWarn';
  const row = make(u.done, 'div', 'row-btns');
  u.save = button(row, 'meshSave', 'Save the file', meshSave);
  u.discard = button(row, 'meshDiscard', 'Discard', () => { MESH.result = null; meshSay(''); meshShow(true); });
  u.msg = make(host, 'p', 'note mesh-msg'); u.msg.id = 'meshMsg'; u.msg.setAttribute('role', 'status');
  addReset(host, 'mesh');
  meshShow(false);
}
