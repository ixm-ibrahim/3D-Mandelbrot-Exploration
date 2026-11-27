// Learn, "A whole shape": every point of the big circle (in 3D the big ball) takes steps of z -> z^n + c, and a
// point that lands further than 2 from the centre is thrown out for good. Shape k is what is left after k steps.
// Holds the choice "Follow", the transport, the pictures, the dots and the words.
//   Mandelbrot shape: every point of the picture is its own c, and its dot starts on that point.
//   Julia shape:      one c for all (the diamond); every point of the picture is a place to start from.
// 66-learn-view.js hands over to this file while LEARN.follow === 'shape'; learnShape3d (68-learn-shape3d.js) draws
// the 3D picture. The 2D rule is the flat one (learnFlatRule) after the modifiers |x|, |y| and flip y, as z^n + c.
const LEARN_SHAPE_N = 16;                          // the last step the slider reaches
// one step at each speed: seconds on the move, then seconds standing still on the whole step
const LEARN_SHAPE_SECONDS = { slow: [2.2, 0.6], normal: [1.1, 0.35], fast: [0.55, 0.15] };
// Seconds a play that starts at step 0 first rests there, so that the opening sentence can be read.
const LEARN_SHAPE_OPENING = { slow: 2.4, normal: 1.5, fast: 0.9 };
// Opacities handed to the 3D picture: the shape on show, the ghost of the shape before, and the peel a step takes
// away. deep: between these two steps the near side of the body goes from glass to solid (learnShapeLevels).
const LEARN_SHAPE_GLASS = { solid: 1, ghost: 0.22, peel: 0.42, deep: [5, 11] };
// The opening 3D view: higher up than LEARN_V_VIEWS.s3, so that a shape along the flat plane is not seen edge on.
const LEARN_SHAPE_VIEW3 = { yaw: -0.62, pitch: 0.9, zoom: 1 };
// A bite thinner than this many pixels, averaged along the shape's outline, is too fine to see: the sentence says so.
const LEARN_SHAPE_THIN = 1;
// The names are true of the plain power 2 only, and are shown only then. text: the value as the dials name it.
const LEARN_SHAPE_NAMED = [
  { c: [-1, 0, 0], text: 'c at x −1, y 0', name: 'the basilica' },
  { c: [-0.1226, 0.7449, 0], text: 'c at x −0.12, y 0.74', name: 'the rabbit' },
  { c: [0, 1, 0], text: 'c at x 0, y 1', name: 'a bare twig' },
  { c: [0, 0, 0], text: 'c at x 0, y 0', name: 'a plain disc' },
];
const LEARN_SHAPE = {
  kind: 'both',                  // 'm' Mandelbrot shape | 'j' Julia shape | 'both'
  each: 'moves',                 // 'once': a step shows only what it leaves | 'moves': the moves inside it, played on dots
  dots: 'some',                  // 'few' | 'some' | 'many' | 'most': how close the dots lie (LEARN_SHAPE_SPACING)
  see: 'dots',                   // 'dots' | 'skin' | 'both': the dots, the surface, or both
  mesh: null,                    // the canvas and program the lit 3D surface is drawn with (learnShapeMeshMake)
  orbits: 'few',                 // whose whole paths are drawn: 'few' (the handful drawn larger) | 'all' | 'none'
  Lv: {},                        // Lv[kind]: what the surface "right now" keeps of that picture (learnShapeLive)
  lay: 'both',                   // how the dots of a 3D picture are laid out: 'grid' | 'sheets' | 'shells' | 'both'
  tint: 'mix',                   // what a dot's colour says about where it started: 'dir' | 'height' | 'dist' | 'mix' (how far out and how high)
  refill: true,                  // as dots are thrown out, new dots are added that start between the ones that are left (learnShapeRefill)
  D: {},                         // D[kind]: the kept dots of that picture (learnShapeDots)
  mv: { sig: null, moves: [], names: [], chips: [], keys: [] },   // the kept moves of one step (learnShapeMoves)
  endSide: false,                // at the joint of two parts: stand at the end of the part before (a play of one part stopped there)
  sig3: '', res3: null,          // what the 3D picture last drew, so that the same glass is not drawn twice (learnShapeSolid)
  c: null,                       // the Julia c, [x, y, z]; the 2D page uses x and y
  pos: 0,                        // the slider: whole steps taken, and how far through the next (3.4 = shape 3 with step 4 under way)
  playing: false, until: null, dwell: 0, last: 0, raf: 0, rest: 0,
  played: false,                 // the picture has played by itself once in this visit
  view2: null,                   // view2.m / view2.j = { x, y, zoom }: the middle of each flat picture, and how far it is zoomed in
  view3: null,                   // { yaw, pitch, zoom }, in the sense of LEARN_V_VIEWS.s3
  panes: [], side: true,         // where the pictures stand on the stage; side: next to each other (not one above the other)
  maps: {},                      // maps[kind]: the kept numbers of that flat picture
  three: null, threeTried: false, threeNote: '', note: '', warned: false,
  gone: '',                      // the pictures on show of which nothing is left at the step the slider stands on: '', 'm', 'j' or 'mj'
  thin: '',                      // thin[k] === '1': the bite of step k + 1 is too fine to see in the pictures as they stand (learnShapeDraw)
  zero: { sig: '', out: false }, // kept answer of learnShapeZeroOut
  first: { sigJ: '', whole: true },   // kept answer of learnShapeStartWhole
  above: {},                     // above[kind]: what learnShapeAbove keeps of a 3D shape seen from straight above
  place: null,                   // where One point stood when Follow went to the whole shape (learnShapeFollow)
  hot: 0, touched: 0, seen: '',
  ptr: new Map(), drag: null, pinch: null,
  el: {}, dials: null, sig: '', cols: null, cut: { sig: '', holds: false },
};
const learnShapeEase = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const learnShapeIsOn = () => LEARN.on && LEARN.follow === 'shape';
const learnShapeCalm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const learnShapeKinds = () => (LEARN_SHAPE.kind === 'both' ? ['m', 'j'] : [LEARN_SHAPE.kind]);

// The numbers
// The step at which the 2D point p is thrown out: 0 when it starts outside the big circle, maxK + 1 when it is
// still in after maxK steps. The test is x² + y² > 4: a square root can round a point just off the circle to 2.
// Whole powers 2 to 8 are multiplied out, as in learnShapeMap, so that both agree for a point on a skin.
function learnShapeOut2(p, kind, c, maxK) {
  const n = S.n, abs = S.abs, flip = S.flip, jul = kind === 'j';
  const px = +p[0], py = +p[1], cc = jul ? [+c[0] || 0, +c[1] || 0] : [px, py];
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0;
  if (!(px * px + py * py <= 4)) return 0;
  // A Mandelbrot dot's step from the centre to its own point is k = 0 and is not tested, so the Mandelbrot and the
  // Julia shape of the same step have taken the same number of steps that can throw anything out.
  let z = jul ? [px, py, 0] : [0, 0, 0];
  for (let k = jul ? 1 : 0; k <= maxK; k++) {
    const x = abs[0] ? Math.abs(z[0]) : z[0], y = (abs[1] ? Math.abs(z[1]) : z[1]) * (flip[0] ? -1 : 1);
    let w;
    if (mul === 2) w = [x * x - y * y, 2 * x * y];
    else if (mul) { let a = x, b = y; for (let m = 1; m < mul; m++) { const t = a * x - b * y; b = a * y + b * x; a = t; } w = [a, b]; }
    else w = learnFlatRule([x, y, 0], n);
    z = [w[0] + cc[0], w[1] + cc[1], 0];
    if (k && !(z[0] * z[0] + z[1] * z[1] <= 4)) return k;
  }
  return maxK + 1;
}
// The same for a block of samples: (i, j) is the point (x0 + i * dx, y0 - j * dy). The picture is drawn from this.
function learnShapeMap(kind, c, n, abs, flip, x0, y0, dx, dy, w, h, maxK, out) {
  const ax = !!abs[0], ay = !!abs[1], fy = !!flip[0], jul = kind === 'j', jx = +c[0] || 0, jy = +c[1] || 0;
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0;      // 0: the polar form
  let o = 0;
  for (let j = 0; j < h; j++) {
    const py = y0 - j * dy;
    for (let i = 0; i < w; i++, o++) {
      const px = x0 + i * dx;
      if (!(px * px + py * py <= 4)) { out[o] = 0; continue; }
      let x = 0, y = 0, cx = px, cy = py, k = 0;      // k = 0: a Mandelbrot dot's step to its own point (see learnShapeOut2)
      if (jul) { x = px; y = py; cx = jx; cy = jy; k = 1; }
      for (; k <= maxK; k++) {
        if (ax) x = Math.abs(x);
        if (ay) y = Math.abs(y);       // Math.abs, not "if below 0": a zero keeps the sign the lab's own rule gives it,
        if (fy) y = -y;                // which decides the side of the cut when the power is not a whole number
        if (mul === 2) { const t = x * x - y * y + cx; y = 2 * x * y + cy; x = t; }
        else if (mul) {
          let a = x, b = y;
          for (let m = 1; m < mul; m++) { const t = a * x - b * y; b = a * y + b * x; a = t; }
          x = a + cx; y = b + cy;
        } else {
          const r = Math.hypot(x, y);
          if (r < 1e-20 && n > 0) { x = cx; y = cy; }
          else { const R = aprPow(r, n), q = Math.atan2(y, x) * n; x = R * Math.cos(q) + cx; y = R * Math.sin(q) + cy; }
        }
        if (k && !(x * x + y * y <= 4)) break;
      }
      out[o] = k;
    }
  }
  return out;
}
// For the outlines: the lowest number within r samples of each one. Past the block's edge the edge is repeated.
function learnShapeEdge(map, w, h, r, tmp, out) {
  for (let j = 0, o = 0; j < h; j++) {
    const row = j * w;
    for (let i = 0; i < w; i++, o++) {
      let m = map[o];
      if (m) for (let q = row + Math.max(0, i - r), e = row + Math.min(w - 1, i + r); q <= e; q++) if (map[q] < m) m = map[q];
      tmp[o] = m;
    }
  }
  for (let j = 0, o = 0; j < h; j++) {
    const a = Math.max(0, j - r) * w, b = Math.min(h - 1, j + r) * w;
    for (let i = 0; i < w; i++, o++) {
      let m = tmp[o];
      if (m) for (let q = a + i; q <= b + i; q += w) if (tmp[q] < m) m = tmp[q];
      out[o] = m;
    }
  }
  return out;
}
// Points just inside the surface of the big ball, in 26 directions.
function learnShapeRim() {
  const out = [];
  for (const x of [-1, 0, 1]) for (const y of [-1, 0, 1]) for (const z of [-1, 0, 1]) { const l = Math.hypot(x, y, z); if (l) out.push([x, y, z].map(v => v / l * 2 * (1 - 1e-9))); }
  return out;
}
// Does a Julia shape begin as the whole big circle or ball? On the page it does. In space the 3D rule is asked
// about the points of learnShapeRim: each has to count as inside before the first step.
function learnShapeStartWhole() {
  if (LEARN.space !== 3) return true;
  const Sh = LEARN_SHAPE, F = Sh.first, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, Sh.c].join('|');
  if (F.sigJ === sig) return F.whole;
  F.sigJ = sig; F.whole = true;
  try { F.whole = learnShapeRim().every(p => learnShape3d.out(p, 'j', Sh.c, 0) === 1); } catch (err) { F.whole = true; }
  return F.whole;
}
// In space: does the very first step throw out every point of a Mandelbrot shape? It does when it takes the dot at 0
// further than 4 from the centre, or to no number, before c is added. learnShape3d.out has to agree.
function learnShapeZeroOut() {
  const Sh = LEARN_SHAPE, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip].join('|');
  if (Sh.zero.sig === sig) return Sh.zero.out;
  Sh.zero.sig = sig; Sh.zero.out = false;
  try {
    const q = S.param[a.id], car = CARRY[a.id] || null, z = [0, 0, 0];
    const cs = [[0, 0, 0], [1.9, 0, 0], [-1.9, 0, 0], [0, 1.9, 0], [0, -1.9, 0], [0, 0, 1.9], [0, 0, -1.9], [0.3, 0.2, 0.1], [-0.7, 0.9, -0.5], [1, -1, 1]];
    Sh.zero.out = cs.every(c => {
      const w = car ? car.pw(car.step(car.start(q), z, c, q), z, S.n) : MATH[a.id](z, S.n, q, c);
      return (!learnVFinite(w) || len(w) > 4) && learnShape3d.out(c, 'm', c, 1) === 1;
    });
  } catch (err) { Sh.zero.out = false; }
  return Sh.zero.out;
}
// Is the 3D shape, cut at z = 0, the 2D shape of the same step? learnShape3d.out is asked about a grid of points
// of the flat plane and compared with learnShapeOut2, each time the settings change.
function learnShapeCutHolds() {
  const Sh = LEARN_SHAPE, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, Sh.kind, Sh.c].join('|');
  if (Sh.cut.sig === sig) return Sh.cut.holds;
  Sh.cut.sig = sig; Sh.cut.holds = false;
  if (Sh.kind !== 'm' && Sh.c[2] !== 0) return false;
  try {
    let bad = 0, seen = 0;
    for (const kind of learnShapeKinds()) {
      for (let i = 0; i < 23; i++) for (let j = 0; j < 23; j++) {
        const p = [-2 + (i + 0.37) * 4 / 23, -2 + (j + 0.61) * 4 / 23, 0];
        if (Math.hypot(p[0], p[1]) > 2) continue;
        seen++;
        if (learnShape3d.out(p, kind, Sh.c, LEARN_SHAPE_N) !== learnShapeOut2(p, kind, Sh.c, LEARN_SHAPE_N)) bad++;
      }
    }
    Sh.cut.holds = seen > 0 && bad <= 1;      // one point within a hair of a skin may fall either way
  } catch (err) { Sh.cut.holds = false; }
  return Sh.cut.holds;
}

// What the words need of a block of numbers: left[k], how many points are still in after k steps, and thick[k],
// how thick the bite of step k + 1 is on the average along the outline of shape k: the points the step throws out,
// over the points of shape k within `band` points of its outline (edge: learnShapeEdge with that reach), times band.
function learnShapeTally(map, edge, n, N, band) {
  const hist = new Uint32Array(N + 2), rim = new Int32Array(N + 3), left = new Uint32Array(N + 2), thick = new Float64Array(N + 1);
  for (let o = 0; o < n; o++) { const m = map[o], e = edge[o]; hist[m]++; if (e < m) { rim[e]++; rim[m]--; } }
  for (let v = N, more = hist[N + 1]; v >= 0; v--) { left[v] = more; more += hist[v]; }
  for (let k = 0, r = 0; k < N; k++) { r += rim[k]; const bite = left[k] - left[k + 1]; thick[k] = bite > 0 ? (r > 0 ? bite / r * band : Infinity) : 0; }
  return { left, thick };
}
// The same for a 3D shape, asked of the 3D module's columns(): for every upright line through the big ball, the
// last step at which a point of it is still in. Worked out once for a rule, a kind and a c, and not while something
// is dragged. null while it is not known. LEARN_SHAPE_ABOVE: lines each way, and points on each.
const LEARN_SHAPE_ABOVE = 192;
function learnShapeAbove(kind, quality) {
  const Sh = LEARN_SHAPE, T = Sh.three, N = LEARN_SHAPE_N, a = ap(), now = performance.now();
  const sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, kind === 'j' ? Sh.c : ''].join('|');
  const A = Sh.above[kind] || (Sh.above[kind] = { sig: '', at: 0, done: false, data: null });
  if (A.sig !== sig) { A.sig = sig; A.at = now; A.done = false; A.data = null; }
  if (!A.done && T && !Sh.drag && !Sh.pinch && (quality === 'still' || (Sh.playing && now - A.at >= 150))) {
    A.done = true;
    try {
      const size = LEARN_SHAPE_ABOVE, n = size * size, map = T.columns(kind, Sh.c, { size, half: 2, stops: size, maxK: N });
      if (map) { A.data = learnShapeTally(map, learnShapeEdge(map, size, size, 1, new Uint8Array(n), new Uint8Array(n)), n, N, 1); A.data.unit = 4 / (size - 1); }
    } catch (err) { A.data = null; }
  }
  return A.data;
}

// Each step: Move by move
// The picture of a whole shape shows starting places. Move by move lays dots over it, one for each starting place,
// and plays step k + 1 on them in parts (ph.key). A dot keeps going from where the last step left it.
//   move    one move of the rule, from the chain learnPlan gives for the space on show
//   gone    the dots that have landed further than 2 from the centre light up and fade
// The moves of step k + 1 start from the exact place after k steps and end on the exact place after k + 1.
// One step of six parts at each speed: seconds on the parts, then seconds standing still on the whole step.
const LEARN_SHAPE_MOVE_SECONDS = { slow: [9.2, 0.8], normal: [4.6, 0.4], fast: [2.3, 0.2] };
// how far apart the dots lie, on the 2D page and in space
const LEARN_SHAPE_SPACING = { 2: { few: 0.125, some: 0.08, many: 0.05, most: 0.035 }, 3: { few: 0.25, some: 0.2, many: 0.15, most: 0.12 } };
// How strongly the picture of starting places shows behind the dots: on the 2D page, in space (the opacity of the
// glass picture's canvas), and at a whole step.
const LEARN_SHAPE_QUIET = { 2: 0.3, 3: 0.34, whole: 0.75 };
const LEARN_SHAPE_MARKED = 6;      // how many dots are drawn larger, to be followed
const learnShapeMovesOn = () => LEARN_SHAPE.each === 'moves' && learnShapeMoves().moves.length > 0;

// The places of one 2D dot: learnShapeOut2 with the places kept, the same arithmetic line for line.
// Returns { out, pts, c, carry: null }: pts[j] is where the dot is after j steps, for j = 0 .. min(out, maxK).
function learnShapeOrbit2(p, kind, c, maxK) {
  const n = S.n, abs = S.abs, flip = S.flip, jul = kind === 'j';
  const px = +p[0], py = +p[1], cc = jul ? [+c[0] || 0, +c[1] || 0, 0] : [px, py, 0];
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0, res = { out: 0, pts: [], c: cc, carry: null };
  if (!(px * px + py * py <= 4)) return res;
  let z = jul ? [px, py, 0] : [0, 0, 0];
  if (jul) res.pts.push(z);
  for (let k = jul ? 1 : 0; k <= maxK; k++) {
    const x = abs[0] ? Math.abs(z[0]) : z[0], y = (abs[1] ? Math.abs(z[1]) : z[1]) * (flip[0] ? -1 : 1);
    let w;
    if (mul === 2) w = [x * x - y * y, 2 * x * y];
    else if (mul) { let a = x, b = y; for (let m = 1; m < mul; m++) { const t = a * x - b * y; b = a * y + b * x; a = t; } w = [a, b]; }
    else w = learnFlatRule([x, y, 0], n);
    z = [w[0] + cc[0], w[1] + cc[1], 0];
    res.pts.push(z);
    if (k && !(z[0] * z[0] + z[1] * z[1] <= 4)) { res.out = k; return res; }
  }
  res.out = maxK + 1;
  return res;
}
// The moves of one step for the space on show, as learnPlan gives them. One chain serves every dot; the last move,
// the slide, is made with each dot's own c (learnShapeMoveAt). Where the orbit carries something, or the rule itself
// depends on c (an entry with usesC): learnShapeOwnMoves.
function learnShapeMoves() {
  const L = LEARN, Sh = LEARN_SHAPE, a = ap(), three = L.space === 3;
  const sig = [three ? 3 : 2, S.n, S.abs, S.flip, three ? a.id + JSON.stringify(S.param[a.id]) : ''].join('|');
  if (Sh.mv.sig === sig) return Sh.mv;
  let moves = [];
  try {
    const plan = learnPlan({ space: three ? 3 : 2, id: a.id, params: S.param[a.id], n: S.n, c: [0, 0, 0], abs: S.abs.slice(), flip: S.flip.slice() });
    if (plan && Array.isArray(plan.moves)) moves = plan.moves;
  } catch (err) { moves = []; }
  // The last move, "Add c" in One point, is named Slide here, and "Add the phase" is named "Add the turn".
  const names = moves.map(m => (m.key === 'shift' ? 'Slide' : m.name === 'Add the phase' ? 'Add the turn' : m.name || 'Move'));
  // The parts of one step: the moves, then the throwing out. car: each dot has a chain of its own.
  return (Sh.mv = { sig, moves, names, car: three && (!!CARRY[a.id] || !!a.usesC), chips: names.concat(['Thrown out']), keys: moves.map(() => 'move').concat(['gone']) });
}
// Which part of a step the fraction u (0 .. 1) of the slider stands in: its number i (the moves come first, so a
// move's number is its part's number), its key, and how far through it, t. At a joint, a play that stopped there
// stands at the end of its part (endSide).
function learnShapePart(u) {
  const Sh = LEARN_SHAPE, M = learnShapeMoves(), n = M.keys.length, x = clamp(u, 0, 1) * n;
  let i = Math.min(n - 1, Math.floor(x + 1e-9)), t = clamp(x - i, 0, 1);
  if (t < 1e-9 && i > 0 && Sh.endSide) { i -= 1; t = 1; }
  return { i, t, key: M.keys[i] };
}
// The surface as it is right now, a closed lit body: every starting place that is still in after k steps and whose
// dot is inside the big ball at this moment of step k + 1. The number at a grid point is its dot's distance from the
// centre less 2 (below 0: inside); for a point that is out, the same at the step that threw it out. The surface is
// where the number crosses 0, joined as "surface nets" are. Where dots carry something no chain of moves serves
// every dot: there a dot goes straight from where the step begins to where it ends.
function learnShapeLive(kind, k) {
  const L = LEARN, Sh = LEARN_SHAPE, three = L.space === 3, a = ap(), N = LEARN_SHAPE_N, M = learnShapeMoves(), now = performance.now();
  const base = [three ? 3 : 2, kind, S.n, S.abs, S.flip, three ? a.id + JSON.stringify(S.param[a.id]) : '', kind === 'j' ? (three ? Sh.c : Sh.c.slice(0, 2)) : ''].join('|');
  const T = Sh.Lv[kind] || (Sh.Lv[kind] = { base: null, at: -1e9, grids: {}, sets: {} });
  if (T.base !== base) { T.at = T.base === null ? -1e9 : now; T.base = base; T.grids = {}; T.sets = {}; }
  // a coarse grid while the settings change with every frame; a fine body follows as soon as they rest
  const rough = now - T.at < 150, n = three ? (rough ? 22 : k <= 1 ? 44 : 72) : (rough ? 110 : 300), key = k + '|' + n + '|' + M.sig;
  if (rough) { clearTimeout(T.timer); T.timer = setTimeout(() => { if (learnShapeIsOn()) learnShapeNow(); }, 200); }
  if (T.sets[key]) return T.sets[key];
  const nz = three ? n : 1, nn = n * n, far = 2.08, h = 2 * far / (n - 1), at = i => -far + i * h;
  const P = o => [at(o % n), at(Math.floor(o / n) % n), three ? at(Math.floor(o / nn)) : 0];
  const orb = (p, m) => (three ? learnShape3d.orbit(p, kind, Sh.c, m) : learnShapeOrbit2(p, kind, Sh.c, m));
  let G = T.grids[n];
  if (!G) { G = T.grids[n] = new Uint8Array(nn * nz); for (let o = 0; o < G.length; o++) { const p = P(o); G[o] = three ? learnShape3d.out(p, kind, Sh.c, N) : learnShapeOut2(p, kind, Sh.c, N); } }
  const idx = [];
  for (let o = 0; o < G.length; o++) if (G[o] > k) idx.push(o);
  const cnt = idx.length, m = M.moves.length, lin = !!M.car || !m, phi = new Float32Array(G.length).fill(NaN), cs = new Float32Array(3 * cnt), J = [new Float32Array(3 * cnt)];
  const next = k < N ? new Float32Array(3 * cnt) : null, cross = [];
  for (let i = 0; i < cnt; i++) {
    const o = idx[i], q = orb(P(o), Math.min(N, k + 1)), pts = q.pts, zk = pts[Math.min(k, pts.length - 1)];
    let top = 0;
    for (let j = 0; j <= k && j < pts.length; j++) top = Math.max(top, Math.hypot(pts[j][0], pts[j][1], pts[j][2]));
    phi[o] = Math.min(top - 2, -1e-6);
    J[0].set(zk, 3 * i); cs.set(q.c, 3 * i);
    if (next) next.set(pts[k + 1] || zk, 3 * i);
  }
  // cross[j]: how many dots the move j takes across the big ball (0: that move leaves the surface as it is)
  const inB = (A, i) => A[3 * i] * A[3 * i] + A[3 * i + 1] * A[3 * i + 1] + A[3 * i + 2] * A[3 * i + 2] <= 4;
  if (next && !lin) {
    const d = { c: [0, 0, 0] };
    for (let j = 0; j < m; j++) {
      const A = J[j], B = new Float32Array(3 * cnt);
      let x = 0;
      for (let i = 0; i < cnt; i++) {
        d.c[0] = cs[3 * i]; d.c[1] = cs[3 * i + 1]; d.c[2] = cs[3 * i + 2];
        const v = learnShapeMoveAt(M, null, d, j, [A[3 * i], A[3 * i + 1], A[3 * i + 2]], 1);
        B[3 * i] = v[0]; B[3 * i + 1] = v[1]; B[3 * i + 2] = v[2];
        if (inB(A, i) !== inB(B, i)) x++;
      }
      J.push(B); cross.push(x);
    }
  } else if (next) { J.push(next); let x = 0; for (let i = 0; i < cnt; i++) if (!inB(next, i)) x++; for (let j = 0; j < Math.max(1, m); j++) cross.push(x); }
  // a point that is out: how far outside its dot was when it was thrown out (worked out when a neighbour asks)
  const out = o => {
    let v = 4;
    try { const g = G[o], p = P(o); if (!g) v = Math.max(Math.hypot(p[0], p[1], p[2]) - 2, 0.05); else { const z = orb(p, g).pts[g]; if (z) v = Math.hypot(z[0], z[1], z[2]) - 2; } } catch (err) { v = 4; }
    return (phi[o] = v !== v || v > 1e6 ? 4 : Math.max(v, 1e-3));
  };
  const old = Object.keys(T.sets);
  if (old.length > 5) delete T.sets[old[0]];
  return (T.sets[key] = { n, nn, h, far, at, idx, cnt, m, lin, phi, cs, J, next: !!next, cross, out, M, F: new Float32Array(G.length) });
}
// The numbers of the surface right now, into set.F: for every point that is still in, how far its dot is from the
// centre at this moment of the step (ph: the part being played, or null at a whole step), less 2.
function learnShapeLiveField(set, ph) {
  const F = set.F, phi = set.phi, idx = set.idx, cnt = set.cnt, J = set.J, m = set.m, cs = set.cs, glide = ph ? learnShapeEase(0, 1, ph.t) : 0;
  F.set(phi);
  let j = 0, t = 0;
  if (ph && set.next) { if (ph.key === 'move') { j = ph.i; t = glide; } else { j = Math.max(0, m - 1); t = 1; } }
  if (set.lin) {
    const u = set.next ? clamp((j + t) / Math.max(1, m), 0, 1) : 0, A = J[0], B = J[1] || J[0];
    for (let i = 0; i < cnt; i++) { const o = idx[i], x = A[3 * i] + (B[3 * i] - A[3 * i]) * u, y = A[3 * i + 1] + (B[3 * i + 1] - A[3 * i + 1]) * u, z = A[3 * i + 2] + (B[3 * i + 2] - A[3 * i + 2]) * u; F[o] = Math.max(phi[o], Math.hypot(x, y, z) - 2); }
    return;
  }
  if (t >= 1 && J[j + 1]) { j += 1; t = 0; }
  const A = J[Math.min(j, J.length - 1)];
  if (t <= 0 || !set.next) { for (let i = 0; i < cnt; i++) { const o = idx[i]; F[o] = Math.max(phi[o], Math.hypot(A[3 * i], A[3 * i + 1], A[3 * i + 2]) - 2); } return; }
  const d = { c: [0, 0, 0] };
  for (let i = 0; i < cnt; i++) {
    d.c[0] = cs[3 * i]; d.c[1] = cs[3 * i + 1]; d.c[2] = cs[3 * i + 2];
    const q = learnShapeMoveAt(set.M, null, d, j, [A[3 * i], A[3 * i + 1], A[3 * i + 2]], t), o = idx[i];
    F[o] = Math.max(phi[o], Math.hypot(q[0], q[1], q[2]) - 2);
  }
}
// The body in space for the numbers in set.F: { pos, el }, the points and the triangles (three numbers each).
function learnShapeLiveMesh(set) {
  const F = set.F, idx = set.idx, cnt = set.cnt, n = set.n, nn = set.nn, at = set.at, h = set.h, st = [1, n, nn], cn = n - 1;
  const fv = o => { let v = F[o]; if (v !== v) { v = set.out(o); F[o] = v; } return v; };
  if (!set.vid) { set.vid = new Int32Array(cn * cn * cn); set.stamp = new Int32Array(cn * cn * cn); set.frame = 0; }
  const vid = set.vid, stamp = set.stamp, frame = ++set.frame, pos = [], el = [];
  const vert = (cx, cy, cz) => {      // the point of one cell: the middle of the places where the surface crosses its twelve edges
    const ci = cx + cy * cn + cz * cn * cn;
    if (stamp[ci] === frame) return vid[ci];
    const o0 = cx + cy * n + cz * nn;
    let sx = 0, sy = 0, sz = 0, c = 0;
    for (let ax = 0; ax < 3; ax++) {
      const b = (ax + 1) % 3, c2 = (ax + 2) % 3;
      for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) {
        const oa = o0 + i * st[b] + j * st[c2], fa = fv(oa), fb = fv(oa + st[ax]);
        if ((fa < 0) === (fb < 0)) continue;
        const q = [cx, cy, cz]; q[b] += i; q[c2] += j;
        const e = [at(q[0]), at(q[1]), at(q[2])]; e[ax] += h * fa / (fa - fb);
        sx += e[0]; sy += e[1]; sz += e[2]; c++;
      }
    }
    stamp[ci] = frame; vid[ci] = pos.length / 3;
    if (c) pos.push(sx / c, sy / c, sz / c); else pos.push(at(cx) + h / 2, at(cy) + h / 2, at(cz) + h / 2);
    return vid[ci];
  };
  for (let i = 0; i < cnt; i++) {
    const o = idx[i];
    if (!(F[o] < 0)) continue;
    const q = [o % n, Math.floor(o / n) % n, Math.floor(o / nn)];
    for (let ax = 0; ax < 3; ax++) for (let dir = -1; dir <= 1; dir += 2) {
      if (fv(o + dir * st[ax]) < 0) continue;      // an edge from inside to outside: the four cells round it are joined
      const b = (ax + 1) % 3, c = (ax + 2) % 3, e = q.slice();
      if (dir < 0) e[ax] -= 1;
      const cell = (db, dc) => { const w = e.slice(); w[b] += db; w[c] += dc; return vert(w[0], w[1], w[2]); };
      const A = cell(-1, -1), B = cell(0, -1), C = cell(0, 0), D = cell(-1, 0);
      if (dir > 0) el.push(A, B, C, A, C, D); else el.push(A, C, B, A, D, C);
    }
  }
  return { pos, el };
}
// A colour as three numbers (0..1) into out: the colours learnShapeDotColour gives in space, worked without text.
function learnShapeTintRgb(p, dark, tint, out) {
  const up = p[2], side = Math.hypot(p[0], p[1]);
  let hue, t;
  if (tint === 'height') { hue = 250 - 250 * clamp((up + 2) / 4, 0, 1); t = clamp(side / 2, 0, 1); }
  else if (tint === 'dist' || tint === 'mix') { hue = 290 * clamp(len(p) / 2, 0, 1); t = clamp((2 - up) / 4, 0, 1); }      // 'mix': the same hue, and the height told by a wide run from light to dark
  else { hue = (Math.atan2(p[1], p[0]) * 180 / PI + 360) % 360; t = clamp((2 - up) / 4, 0, 1); }
  const wide = tint === 'mix', l = (dark ? (wide ? 88 - 48 * t : 80 - 26 * t) : (wide ? 20 + 40 * t : 26 + 18 * t)) / 100, s = dark ? 0.88 : 0.84, b = l < 0.5 ? l * (1 + s) : l + s - l * s, a = 2 * l - b, hh = hue / 360;
  const f = x => { x = (x % 1 + 1) % 1; return x < 1 / 6 ? a + (b - a) * 6 * x : x < 0.5 ? b : x < 2 / 3 ? a + (b - a) * (2 / 3 - x) * 6 : a; };
  out[0] = f(hh + 1 / 3); out[1] = f(hh); out[2] = f(hh - 1 / 3);
}
// The lit body of every pane in the list, on the canvas of learnShapeMeshMake. Each place of the body is painted in
// the colour a dot that starts there carries, drawn towards the body colour: so a dot can be traced home by colour.
function learnShapeLiveDraw3(panes, mv) {
  const Sh = LEARN_SHAPE, G = Sh.mesh || (Sh.mesh = learnShapeMeshMake()), gl = G.gl;
  if (!gl) return;
  const cv = G.canvas, w = stage.clientWidth, h = stage.clientHeight, dpr = clamp(window.devicePixelRatio || 1, 1, 2), bw = Math.round(w * dpr), bh = Math.round(h * dpr);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; }
  cv.hidden = false;
  gl.disable(gl.SCISSOR_TEST); gl.viewport(0, 0, bw, bh); gl.clearColor(0, 0, 0, 0); gl.clearDepth(1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.disable(gl.CULL_FACE); gl.disable(gl.BLEND);
  gl.useProgram(G.prog); gl.bindVertexArray(G.vao);
  const dark = learnVDark(), brass = learnShapeCols().brass, rgb = [0, 0, 0];
  for (const P of panes) {
    const set = learnShapeLive(P.kind, Math.min(mv.k, LEARN_SHAPE_N));
    if (!set.cnt) continue;
    learnShapeLiveField(set, mv.ph);
    const mesh = learnShapeLiveMesh(set), nv = mesh.pos.length / 3;
    if (!nv || !mesh.el.length) continue;
    const pos = new Float32Array(mesh.pos), el = new Uint32Array(mesh.el), nrm = new Float32Array(3 * nv), col = new Float32Array(3 * nv);
    for (let e = 0; e < el.length; e += 3) {
      const a = 3 * el[e], b = 3 * el[e + 1], c = 3 * el[e + 2];
      const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      nrm[a] += nx; nrm[a + 1] += ny; nrm[a + 2] += nz; nrm[b] += nx; nrm[b + 1] += ny; nrm[b + 2] += nz; nrm[c] += nx; nrm[c + 1] += ny; nrm[c + 2] += nz;
    }
    for (let i = 0; i < nv; i++) { learnShapeTintRgb([pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]], dark, Sh.tint, rgb); for (let q = 0; q < 3; q++) col[3 * i + q] = 0.5 * rgb[q] + 0.5 * brass[q]; }
    gl.bindBuffer(gl.ARRAY_BUFFER, G.buf[0]); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.DYNAMIC_DRAW);
    gl.bindBuffer(gl.ARRAY_BUFFER, G.buf[1]); gl.bufferData(gl.ARRAY_BUFFER, nrm, gl.DYNAMIC_DRAW);
    gl.bindBuffer(gl.ARRAY_BUFFER, G.buf[2]); gl.bufferData(gl.ARRAY_BUFFER, col, gl.DYNAMIC_DRAW);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, G.idx); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, el, gl.DYNAMIC_DRAW);
    const pr = learnShape3d.proj(Sh.view3, [P.x, P.y, P.w, P.h]), R = pr.R, U = pr.U, D = pr.D, light = norm([0.55 * D[0] + 0.65 * U[0] - 0.5 * R[0], 0.55 * D[1] + 0.65 * U[1] - 0.5 * R[1], 0.55 * D[2] + 0.65 * U[2] - 0.5 * R[2]]);
    const vx = Math.round(P.x * dpr), vy = Math.round((h - P.y - P.h) * dpr), vw = Math.round(P.w * dpr), vh = Math.round(P.h * dpr);
    gl.viewport(vx, vy, vw, vh); gl.enable(gl.SCISSOR_TEST); gl.scissor(vx, vy, vw, vh);
    gl.uniform3fv(G.u.uR, R); gl.uniform3fv(G.u.uU, U); gl.uniform3fv(G.u.uD, D); gl.uniform3fv(G.u.uL, light);
    gl.uniform2f(G.u.uS, pr.s / (P.w / 2), pr.s / (P.h / 2));
    gl.drawElements(gl.TRIANGLES, el.length, gl.UNSIGNED_INT, 0);
  }
  gl.bindVertexArray(null);
}
// The same on the 2D page: the inside of the shape as it is right now, filled.
function learnShapeLiveFlat(g, P, to, k, ph) {
  const set = learnShapeLive(P.kind, Math.min(k, LEARN_SHAPE_N));
  if (!set.cnt) return;
  learnShapeLiveField(set, ph);
  const n = set.n, F = set.F, idx = set.idx, K = learnShapeCols().brass, r = Math.round(K[0] * 255), gr = Math.round(K[1] * 255), b = Math.round(K[2] * 255);
  if (!set.cv) { set.cv = document.createElement('canvas'); set.cv.width = set.cv.height = n; set.img = set.cv.getContext('2d').createImageData(n, n); }
  const data = set.img.data;
  data.fill(0);
  for (let i = 0; i < set.cnt; i++) {
    const o = idx[i];
    if (!(F[o] < 0)) continue;
    const q = 4 * (o % n + (n - 1 - Math.floor(o / n)) * n);
    data[q] = r; data[q + 1] = gr; data[q + 2] = b; data[q + 3] = 255;
  }
  set.cv.getContext('2d').putImageData(set.img, 0, 0);
  const a = to([-set.far - set.h / 2, set.far + set.h / 2, 0]), size = (2 * set.far + set.h) * P.s;
  g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
  g.globalAlpha = 0.92; g.drawImage(set.cv, a[0], a[1], size, size); g.globalAlpha = 1;
}
// The canvas and the program of the lit 3D surface, between the glass picture and the canvas that carries the dots.
// The flat camera of the glass picture. Both sides of the skin are lit: a move can turn a surface inside out.
function learnShapeMeshMake() {
  const Sh = LEARN_SHAPE, cv = document.createElement('canvas'), G = { canvas: cv, gl: null };
  cv.className = 'learn-shape-gl learn-shape-mesh'; cv.id = 'learnShapeMesh'; cv.setAttribute('aria-hidden', 'true');
  stage.insertBefore(cv, Sh.el.canvas);
  try {
    const gl = cv.getContext('webgl2', { alpha: true, antialias: true });
    if (!gl) return G;
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, '#version 300 es\nlayout(location=0) in vec3 aP; layout(location=1) in vec3 aN; layout(location=2) in vec3 aC;\nuniform vec3 uR, uU, uD; uniform vec2 uS; out vec3 vN, vC;\nvoid main(){ vN = aN; vC = aC; gl_Position = vec4(dot(aP, uR) * uS.x, dot(aP, uU) * uS.y, -dot(aP, uD) / 12.0, 1.0); }'));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, '#version 300 es\nprecision highp float; in vec3 vN, vC; uniform vec3 uD, uL; out vec4 o;\nvoid main(){ vec3 n = normalize(vN); if (dot(n, uD) < 0.0) n = -n; float dif = max(dot(n, uL), 0.0), rim = 1.0 - max(dot(n, uD), 0.0);\n  float sp = pow(max(dot(n, normalize(uL + uD)), 0.0), 28.0); o = vec4(vC * (0.26 + 0.74 * dif) * (1.0 - 0.35 * rim * rim) + vec3(0.22) * sp, 1.0); }'));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    G.u = {}; for (const k of ['uR', 'uU', 'uD', 'uS', 'uL']) G.u[k] = gl.getUniformLocation(prog, k);
    G.vao = gl.createVertexArray(); gl.bindVertexArray(G.vao);
    G.buf = [0, 1, 2].map(loc => { const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 3, gl.FLOAT, false, 0, 0); return b; });
    G.idx = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, G.idx);
    gl.bindVertexArray(null);
    G.gl = gl; G.prog = prog;
    cv.addEventListener('webglcontextlost', ev => { ev.preventDefault(); cv.remove(); if (Sh.mesh === G) Sh.mesh = null; });
  } catch (err) { console.warn('the lit surface could not be set up', err); G.gl = null; }
  return G;
}
// New dots as dots are thrown out: after each step dots are added until there are as many as at the start. Their
// starting places lie between the ones that are left, and each has taken every step so far. The places are tried
// in a fixed, evenly spread order (a Halton sequence), and in space lie as the layout does.
const LEARN_SHAPE_SHEETS = [1.8, 1.2, 0.6, 0, -0.6, -1.2, -1.8], LEARN_SHAPE_SHELLS = [1.98, 1.5, 1, 0.5];
const learnShapeHal = (i, b) => { let f = 1, r = 0; i += 1; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
function learnShapeCandidate(three, lay, i) {      // the i-th starting place to try, or null when it falls outside the big circle
  if (!three) { const p = [4 * learnShapeHal(i, 2) - 2, 4 * learnShapeHal(i, 3) - 2, 0]; return p[0] * p[0] + p[1] * p[1] <= 4 ? p : null; }
  if (lay === 'both') { lay = i % 2 ? 'shells' : 'sheets'; i = Math.floor(i / 2); }
  const a = learnShapeHal(i, 2), b = learnShapeHal(i, 3), c = learnShapeHal(i, 5);
  if (lay === 'shells') {      // a shell is picked as often as its share of all the shells' surface
    let u = c * LEARN_SHAPE_SHELLS.reduce((s, r) => s + r * r, 0), r = LEARN_SHAPE_SHELLS[LEARN_SHAPE_SHELLS.length - 1];
    for (const q of LEARN_SHAPE_SHELLS) { if (u < q * q) { r = q; break; } u -= q * q; }
    const zz = 1 - 2 * a, rr = Math.sqrt(Math.max(0, 1 - zz * zz));
    return [r * rr * Math.cos(2 * PI * b), r * rr * Math.sin(2 * PI * b), r * zz];
  }
  const p = [4 * a - 2, 4 * b - 2, lay === 'sheets' ? LEARN_SHAPE_SHEETS[Math.min(LEARN_SHAPE_SHEETS.length - 1, Math.floor(c * LEARN_SHAPE_SHEETS.length))] : 4 * c - 2];
  return p[0] * p[0] + p[1] * p[1] + p[2] * p[2] <= 4 ? p : null;
}
// Makes sure the dots that come in at the steps 1 .. K are there (D: the dots of one picture, learnShapeDots). A dot
// that comes in at step k has from = k: it is on show from that step on. D.enter[k]: how many came in at step k.
function learnShapeRefill(D, K) {
  if (!D || !D.fill) return;
  K = Math.min(K, LEARN_SHAPE_N);
  while (D.filled < K) {
    const k = ++D.filled;
    let on = 0, got = 0, tries = 0;
    for (const d of D.dots) if (d.out > k && !(d.from > k)) on++;
    const need = D.n0 - on, most = 25 * need + 200;
    if (!D.dead) while (got < need && tries < most) {
      if (tries === 2000 && !got) break;      // nothing in two thousand tries: next to nothing is left to start from
      const p = learnShapeCandidate(D.three, D.lay, D.seq++);
      tries++;
      if (!p) continue;
      let ok = false;
      try { ok = D.outAt(p, k) > k; } catch (err) { ok = false; }
      if (!ok) continue;
      const d = D.make(p);
      if (!d || !(d.out > k)) continue;
      d.from = k; D.dots.push(d); got++;
    }
    if (need > 0 && !got && !on) D.dead = true;      // no dot is left and none is found: the later steps are not searched
    D.enter[k] = got;
  }
}
// The starting places of the dots, as { pts, gap }: the grid of learnVGridPoints, or in space level sheets or shells
// (balls inside one another), with about as many dots as the full grid of the same choice has.
function learnShapeLayout(three, h, lay) {
  if (three && lay === 'both') {      // sheets and shells together, each with half the dots
    const A = learnShapeLayout(true, h * 1.26, 'sheets'), B = learnShapeLayout(true, h * 1.26, 'shells');
    return { pts: A.pts.concat(B.pts), gap: Math.min(A.gap, B.gap) };
  }
  if (!three || (lay !== 'sheets' && lay !== 'shells')) return { pts: learnVGridPoints(three ? 3 : 2, h), gap: h };
  const out = [];
  if (lay === 'sheets') {
    const g = 1.3 * Math.pow(h, 1.5), m = Math.ceil(2 / g) + 1;
    for (const z of LEARN_SHAPE_SHEETS) for (let j = m - 1; j >= -m; j--) for (let i = -m; i < m; i++) {
      const p = [(i + 0.5) * g, (j + 0.25) * g, z];
      if (p[0] * p[0] + p[1] * p[1] + z * z <= 4) out.push(p);
    }
    return { pts: out, gap: g };
  }
  const g = 1.67 * Math.pow(h, 1.5), ga = PI * (3 - Math.sqrt(5));
  for (const r of LEARN_SHAPE_SHELLS) {
    const M = Math.max(12, Math.round(4 * PI * r * r / (g * g)));
    for (let i = 0; i < M; i++) { const zz = 1 - (i + 0.5) * 2 / M, rr = Math.sqrt(1 - zz * zz); out.push([r * rr * Math.cos(i * ga), r * rr * Math.sin(i * ga), r * zz]); }
  }
  return { pts: out, gap: g };
}
// A dot's colour for good, from where it starts. dir: the hue says which way it lies from the centre and the shade
// how far out (in space: how high), as learnVDotColour has it. height: blue at the bottom to red at the top. dist: red
// at the centre to violet at the rim. Rounded to a few hundred colours, so that dots of one colour are drawn together.
function learnShapeDotColour(p, three, dark, tint) {
  const up = three ? p[2] : p[1], side = three ? Math.hypot(p[0], p[1]) : Math.abs(p[0]);
  let hue, t;
  if (tint === 'height') { hue = 250 - 250 * clamp((up + 2) / 4, 0, 1); t = clamp(side / 2, 0, 1); }
  else if (tint === 'dist' || tint === 'mix') { hue = 290 * clamp(len(p) / 2, 0, 1); t = clamp((2 - up) / 4, 0, 1); }      // 'mix': the same hue, and the height told by a wide run from light to dark
  else { hue = (Math.atan2(p[1], p[0]) * 180 / PI + 360) % 360; t = three ? clamp((2 - p[2]) / 4, 0, 1) : clamp(Math.hypot(p[0], p[1]) / 2, 0, 1); }
  hue = Math.round(hue / 8) * 8 % 360;
  const wide = tint === 'mix';
  return dark ? `hsl(${hue}, 88%, ${Math.round((wide ? 88 - 48 * t : 80 - 26 * t) / 3) * 3}%)` : `hsl(${hue}, 84%, ${Math.round((wide ? 20 + 40 * t : 26 + 18 * t) / 3) * 3}%)`;
}
// The dots of one picture. dot = { p, out, pts, c, carry, col, big, from }: p the starting place; out the step at
// which it is thrown out (N + 1: still in after N); pts, c, carry as learnShapeOrbit2 / learnShape3d.orbit give them;
// col its colour for good; big: one of the handful drawn larger; from: the step it is on show from (0: from the start).
function learnShapeDots(kind) {
  const L = LEARN, Sh = LEARN_SHAPE, three = L.space === 3, a = ap(), N = LEARN_SHAPE_N, dark = learnVDark();
  const sig = [three ? 3 : 2, kind, Sh.dots, three ? Sh.lay : '', Sh.tint, Sh.refill, S.n, S.abs, S.flip, three ? a.id + JSON.stringify(S.param[a.id]) : '', kind === 'j' ? (three ? Sh.c : Sh.c.slice(0, 2)) : '', dark].join('|');
  let D = Sh.D[kind];
  if (D && D.sig === sig) return D;
  const gaps = LEARN_SHAPE_SPACING[three ? 3 : 2], lay = learnShapeLayout(three, gaps[Sh.dots] || gaps.some, Sh.lay), h = lay.gap, dots = [];
  const make = p => {
    let o = null;
    try { o = three ? learnShape3d.orbit(p, kind, Sh.c, N) : learnShapeOrbit2(p, kind, Sh.c, N); } catch (err) { o = null; }
    return o && o.pts.length ? { p, out: o.out, pts: o.pts, c: o.c, carry: o.carry, col: learnShapeDotColour(p, three, dark, Sh.tint), big: false, from: 0 } : null;
  };
  for (const p of lay.pts) { const d = make(p); if (d) dots.push(d); }
  // A handful to follow with the eye, far apart from one another: two that stay to the end, and four that are
  // thrown out on the way, early ones and late ones (where there are such).
  const pick = [], all = dots.map((d, i) => i), d2 = (x, y) => (x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2 + (x[2] - y[2]) ** 2;
  const far = pool => {
    let best = -1, bd = -Infinity;
    for (const i of pool) {
      if (pick.includes(i)) continue;
      let d = pick.length ? Infinity : -Math.abs(len(dots[i].p) - 0.9);      // the first: one about half way out
      for (const j of pick) d = Math.min(d, d2(dots[i].p, dots[j].p));
      if (d > bd) { bd = d; best = i; }
    }
    if (best >= 0) pick.push(best);
    return best >= 0;
  };
  const stay = all.filter(i => dots[i].out > N), mid = all.filter(i => dots[i].out >= 2 && dots[i].out <= N).sort((x, y) => dots[x].out - dots[y].out);
  far(stay); far(stay);
  for (let q = 0; q < 4; q++) far(mid.slice(Math.floor(q * mid.length / 4), Math.floor((q + 1) * mid.length / 4)));
  for (const pool of [stay.concat(mid), all]) while (pick.length < LEARN_SHAPE_MARKED && far(pool)) { /* fill up */ }
  for (const i of pick) dots[i].big = true;
  // for learnShapeRefill: the dots at the start (n0), how far it has got (filled, seq), outAt and make for a new place
  const outAt = (p, m) => (three ? learnShape3d.out(p, kind, Sh.c, m) : learnShapeOut2(p, kind, Sh.c, m));
  return (Sh.D[kind] = { sig, three, h, dots, big: pick, chain: null, n0: dots.length, filled: 0, seq: 0, enter: [], lay: three ? Sh.lay : '', outAt, make, fill: Sh.refill });
}
// The moves of one step for one dot of an entry whose orbit carries something (an entry of CARRY in
// 10-approaches.js) or whose rule depends on c: the chain learnPlan gives for what the dot carries when the step
// begins and for its own c. With nothing carried the chain depends on c alone, and the dots of a Julia picture, which
// share one c, share one chain. A chain of another length is fitted to m parts: a dot with fewer moves waits, one
// with more makes the first in one part.
const LEARN_SHAPE_OWN = { key: '', mv: null };
function learnShapeOwnMoves(d, k, m, kind) {
  const a = ap(), key = CARRY[a.id] ? '' : [learnShapeMoves().sig, kind, d.c, m].join('|');
  if (key && LEARN_SHAPE_OWN.key === key) return LEARN_SHAPE_OWN.mv;
  const mv = learnShapeFit(d, k, m, kind);
  if (key) { LEARN_SHAPE_OWN.key = key; LEARN_SHAPE_OWN.mv = mv; }
  return mv;
}
function learnShapeFit(d, k, m, kind) {
  const a = ap();
  let mv = [];
  try { mv = learnPlan({ space: 3, id: a.id, params: S.param[a.id], n: S.n, c: d.c.slice(), abs: S.abs.slice(), flip: S.flip.slice(), carry: d.carry ? d.carry[k] : undefined, kind }).moves; } catch (err) { mv = []; }
  if (mv.length === m) return mv;
  const stay = { key: 'stay', at: v => [v[0], v[1], v[2]] };
  if (!mv.length) return new Array(m).fill(stay);
  if (mv.length < m) { const out = mv.slice(0, -1); while (out.length < m - 1) out.push(stay); out.push(mv[mv.length - 1]); return out; }
  const head = mv.slice(0, mv.length - m + 1), q = head.length;
  const first = { key: 'own', at: (v, t) => { let x = v; for (let i = 0; i < q; i++) { const u = clamp(t * q - i, 0, 1); if (u <= 0) break; x = head[i].at(x, u); } return x; } };
  return [first].concat(mv.slice(mv.length - m + 1));
}
// Where the dot d is after the fraction t of the move j, coming from v. own: its chain of learnShapeOwnMoves, or null.
function learnShapeMoveAt(M, own, d, j, v, t) {
  let p = null;
  try {
    if (own) p = own[j].at(v, t);
    else if (M.moves[j].key === 'shift') p = [v[0] + t * d.c[0], v[1] + t * d.c[1], v[2] + t * d.c[2]];      // the slide: by the dot's own c
    else p = M.moves[j].at(v, t);
  } catch (err) { p = null; }
  return p && isFinite(p[0]) && isFinite(p[1]) && isFinite(p[2]) ? p : v;
}
// Step k + 1 of one picture, for every dot that is still in after k steps. pos[i]: where the dot stands at the
// joints of the step (pos[i][0] after k steps, pos[i][j + 1] after the move j; the last is the exact place after
// k + 1 steps). moved[j]: does the move j move any dot. list, on, thrown: the dots that take the step, how many
// they are, and how many of them it throws out.
function learnShapeChain(kind, k) {
  const D = learnShapeDots(kind), M = learnShapeMoves();
  learnShapeRefill(D, k);      // the dots that have come in by this step take part in it
  if (D.chain && D.chain.k === k && D.chain.M === M) return D.chain;
  const m = M.moves.length, n = D.dots.length;
  const ch = { k, M, m, pos: new Array(n).fill(null), own: M.car ? new Array(n).fill(null) : null, list: [], on: 0, thrown: 0, moved: new Array(m).fill(false) };
  if (k < LEARN_SHAPE_N) D.dots.forEach((d, i) => {
    if (!(d.out > k) || d.from > k || !d.pts[k + 1]) return;
    ch.on++; ch.list.push(i);
    if (d.out === k + 1) ch.thrown++;
    const own = M.car ? (ch.own[i] = learnShapeOwnMoves(d, k, m, kind)) : null, v = [d.pts[k]];
    for (let j = 0; j < m; j++) v.push(learnShapeMoveAt(M, own, d, j, v[j], 1));
    v[m] = d.pts[k + 1]; ch.pos[i] = v;
    for (let j = 0; j < m; j++) if (len(sub(v[j + 1], v[j])) > 1e-9) ch.moved[j] = true;
  });
  if (D.fill) { learnShapeRefill(D, k + 1); ch.came = D.enter[k + 1] || 0; }      // how many new dots come in when this step is done
  return (D.chain = ch);
}
// Where the dot i stands in the part ph of the step the chain ch belongs to, at the eased fraction te of the part.
function learnShapeDotAt(D, ch, i, ph, te) {
  const d = D.dots[i], v = ch.pos[i];
  if (ph.key === 'move') return te >= 1 ? v[ph.i + 1] : te <= 0 ? v[ph.i] : learnShapeMoveAt(ch.M, ch.own ? ch.own[i] : null, d, ph.i, v[ph.i], te);
  return v[ch.m];
}
// The dots of one picture, drawn over it. to(v) gives [x, y, depth], the place of a point on the canvas (in space:
// learnShape3d.proj, depth growing towards the eye); s: pixels to a unit; ph: the part being played, or null at a
// whole step. A part starts and ends gently (te).
function learnShapeDotsDraw(g, P, to, s, k, ph, three) {
  const Sh = LEARN_SHAPE, C = LEARN.col, e = learnShapeEase;
  const D = learnShapeDots(P.kind), dots = D.dots;
  learnShapeRefill(D, k + 1);      // the dots that come in up to the end of this step
  const part = !!ph && k < LEARN_SHAPE_N, ch = part ? learnShapeChain(P.kind, k) : null, te = part ? e(0, 1, ph.t) : 0, m = ch ? ch.m : 0;
  const key = part ? ph.key : '', away = part || k > 0;
  const gap = D.h * s, r = three ? clamp(0.075 * gap, 1.3, 3) : clamp(0.22 * gap, 1.1, 3.4), R = Math.max(r, 1.6) * 1.55 + 1.3;
  const inPane = q => q[0] > P.x - 12 && q[0] < P.x + P.w + 12 && q[1] > P.y - 12 && q[1] < P.y + P.h + 12;
  const circle = (x, y, rad) => { g.beginPath(); g.arc(x, y, rad, 0, 2 * PI); };
  const show = [], put = (i, v, a, going) => { if (a < 0.02) return; const q = to(v); if (inPane(q)) show.push({ i, x: q[0], y: q[1], z: q[2] || 0, a, going }); };
  for (let i = 0; i < dots.length; i++) {
    const d = dots[i];
    if (!(d.out > k)) continue;                                    // thrown out before: not on show
    // a dot that comes in when this step is done fades in where it then is, while the ones thrown out fade away
    if (d.from > k) { if (d.from === k + 1 && key === 'gone' && d.out > k + 1 && d.pts[k + 1]) put(i, d.pts[k + 1], e(0.45, 1, ph.t), false); continue; }
    const going = part && d.out === k + 1, v = part ? ch.pos[i] : null;      // going: the step under way throws it out
    if (part && !v) continue;
    if (!part) put(i, d.pts[k], 1, false);
    else put(i, learnShapeDotAt(D, ch, i, ph, te), 1, going);
  }
  if (three) show.sort((a, b) => a.z - b.z);                       // the far ones first
  const lit = key === 'gone' ? e(0, 0.18, ph.t) : 0, fade = key === 'gone' ? 1 - e(0.55, 1, ph.t) : 1;
  // Faint marks at the starting places of the dots that are still in, while the dots are away from them. The marks
  // of the dots a step throws out go with them. Very many dots get no marks: the picture behind shows the places.
  const markAl = away ? (three ? 0.4 : 0.5) : 0, mr = Math.max(0.9, r * 0.42);
  if (markAl > 0.01) {
    const gone = d => part && d.out === k + 1;
    for (const pass of dots.length <= 3000 ? [false, true] : []) {
      g.beginPath();
      for (let i = 0; i < dots.length; i++) {
        const d = dots[i];
        if (!(d.out > k) || d.from > k || gone(d) !== pass) continue;
        const q = to(d.p);
        if (inPane(q)) { g.moveTo(q[0] + mr, q[1]); g.arc(q[0], q[1], mr, 0, 2 * PI); }
      }
      g.fillStyle = C.ink2; g.globalAlpha = markAl * (pass ? fade : 1); g.fill(); g.globalAlpha = 1;
    }
    for (const i of D.big) {
      const d = dots[i];
      if (!(d.out > k)) continue;
      const q = to(d.p);
      if (!inPane(q)) continue;
      circle(q[0], q[1], R + 1); g.strokeStyle = d.col; g.lineWidth = 1.5; g.globalAlpha = Math.min(1, markAl * 1.8) * (gone(d) ? fade : 1); g.stroke(); g.globalAlpha = 1;
    }
  }
  // A dot's path so far, added to the path being drawn: its places after each whole step.
  const pathOf = i => { const d = dots[i], n = Math.min(k, d.pts.length - 1); let q = to(d.pts[0]); g.moveTo(q[0], q[1]); for (let j = 1; j <= n; j++) { q = to(d.pts[j]); g.lineTo(q[0], q[1]); } };
  // Every dot's whole path (orbits 'all'): thin lines, the dots of one colour in one go. The handful get theirs below.
  if (Sh.orbits === 'all' && k + (part ? 1 : 0) > 0) {
    const by = new Map();
    for (const sh of show) { const d = dots[sh.i]; if (d.big) continue; let l = by.get(d.col); if (!l) by.set(d.col, l = []); l.push(sh); }
    g.lineWidth = 1; g.lineJoin = 'round';
    for (const [col, l] of by) {
      g.beginPath();
      for (const sh of l) { pathOf(sh.i); if (part) g.lineTo(sh.x, sh.y); }
      g.strokeStyle = col; g.globalAlpha = (three ? 0.28 : 0.4) * (key === 'gone' ? 0.5 + 0.5 * fade : 1); g.stroke();
    }
    g.globalAlpha = 1;
  }
  // the dots; the ones the step throws out light up in the warning colour, swell and fade. In space a far dot is
  // smaller and fainter than a near one. Very many dots are drawn as plain squares, which is several times faster.
  const fast = show.length > 2500, rim = !fast && r >= 1.6;
  const dotOf = (sh, big) => {
    const d = dots[sh.i], f = three ? clamp((sh.z + 2) / 4, 0, 1) : 1;
    let rad = (big ? R : r) * (three ? 0.6 + 0.8 * f : 1), al = (three ? 0.3 + 0.7 * f : 1) * sh.a, col = d.col;
    if (sh.going && key === 'gone') { if (lit > 0.3) col = C.bad; rad *= 1 + (r < 1.7 ? 0.4 : 0.7) * lit; al *= fade; }
    if (al < 0.02) return;
    g.globalAlpha = al;
    if (fast && !big) { const q = rad * 0.89; g.fillStyle = col; g.fillRect(sh.x - q, sh.y - q, 2 * q, 2 * q); return; }
    if (big) {
      circle(sh.x, sh.y, rad + 2.6); g.fillStyle = C.stage; g.fill();
      circle(sh.x, sh.y, rad + 1.5); g.strokeStyle = C.ink; g.lineWidth = 1.4; g.stroke();
    } else if (rim) { circle(sh.x, sh.y, rad + 0.9); g.fillStyle = C.stage; g.fill(); }
    circle(sh.x, sh.y, rad); g.fillStyle = col; g.fill();
  };
  for (const sh of show) if (!dots[sh.i].big) dotOf(sh, false);
  g.globalAlpha = 1;
  // The handful to follow: the whole way each has come as a line, then the dot itself, larger and ringed. The moves
  // of the step under way are drawn as the curves they are.
  const bigs = show.filter(sh => dots[sh.i].big);
  if (away && Sh.orbits !== 'none') {
    for (const sh of bigs) {
      const d = dots[sh.i], v = part ? ch.pos[sh.i] : null, own = part && ch.own ? ch.own[sh.i] : null;
      g.beginPath();
      pathOf(sh.i);
      if (part) {
        const upto = key === 'move' ? ph.i : m - 1;
        for (let j = 0; j <= upto; j++) {
          const end = key === 'move' && j === ph.i ? te : 1, n = j === upto ? 16 : 8;
          for (let a = 1; a <= n; a++) { const q = to(a === n && end === 1 ? v[j + 1] : learnShapeMoveAt(ch.M, own, d, j, v[j], end * a / n)); g.lineTo(q[0], q[1]); }
        }
      }
      g.lineJoin = g.lineCap = 'round';
      g.strokeStyle = C.stage; g.lineWidth = 4; g.globalAlpha = 0.7 * (sh.going && key === 'gone' ? fade : 1); g.stroke();
      g.strokeStyle = d.col; g.lineWidth = 1.8; g.globalAlpha = sh.going && key === 'gone' ? fade : 1; g.stroke();
    }
  }
  for (const sh of bigs) dotOf(sh, true);
  g.globalAlpha = 1;
}
// The words of one part of step k + 1: label names the part, say is the sentence.
function learnShapePartWords(k, ph) {
  const L = LEARN, Sh = LEARN_SHAPE, three = L.space === 3, ring = three ? 'ball' : 'circle', kinds = learnShapeKinds(), both = kinds.length === 2, kind = Sh.kind;
  const M = learnShapeMoves(), chs = kinds.map(kd => learnShapeChain(kd, k)), m = M.moves.length, step = `Step ${k + 1}`;
  const [First, Second] = Sh.side ? ['Left', 'Right'] : ['Upper', 'Lower'];
  const on = chs.reduce((n, c) => n + c.on, 0), thrown = chs.reduce((n, c) => n + c.thrown, 0);
  const label = ph.key === 'gone' ? 'thrown out' : M.names[ph.i];
  let say;
  if (!on) say = `${step}. No dot is left to show it: every dot has already been thrown out. Dots: Many shows more of them, and Each step: At once shows every bite.`;
  else if (ph.key === 'move') {
    const mv = M.moves[ph.i], name = M.names[ph.i], moved = chs.some(c => c.moved[ph.i]);
    // every dot of every picture that moves at all stands at the centre when this move begins
    const centre = chs.every(c => c.list.every(i => len(c.pos[i][ph.i]) < 1e-12));
    if (!moved) say = `${step}, ${name}: ` + (centre ? 'every dot is at the centre, so nothing moves.' : mv.key === 'shift' && kind === 'j' ? 'c is 0 here, so no dot moves.' : 'this move leaves every dot where it is.');
    else if (mv.key === 'shift') say = `${step}, ${name}: ` + (both ? `${First.toLowerCase()}, every dot is moved by its own c. ${Second}, every dot is moved by the diamond’s c.` : kind === 'm' ? 'every dot is moved by its own c.' : 'every dot is moved by c.');
    else say = `${step}, ${name}: ${mv.all || 'every dot makes this move by its own amount; Follow One point shows it for a single dot'}.`;
    // with the surface on show: does this move change it? It does when it takes a dot across the big ball.
    if (LEARN_SHAPE.see !== 'dots') {
      const sets = kinds.map(kd => learnShapeLive(kd, k)), known = sets.every(s => s.cross.length > ph.i);
      if (known) say += sets.some(s => s.cross[ph.i] > 0) ? ' The surface changes with it.' : ' The surface stays as it is.';
    }
  } else {
    // In space a dot outside the big ball can be drawn inside its outline, in front of the ball or behind it: the
    // sentence then says so. thin[k] other than '-': the pictures themselves show this step taking something.
    let hid = false;
    if (three && thrown) chs.forEach((c, n) => {
      const P = Sh.panes[n], D = learnShapeDots(kinds[n]);
      if (!P || hid) return;
      const pr = learnShapeProj(P), mid = pr.to([0, 0, 0]);
      hid = c.list.some(i => { if (D.dots[i].out !== k + 1) return false; const q = pr.to(c.pos[i][m]); return Math.hypot(q[0] - mid[0], q[1] - mid[1]) < 2 * pr.s; });
    });
    say = thrown ? `${step}. The dots that landed outside the big ${ring} are thrown out${both ? ', in both pictures' : ''}: ${thrown} of ${on}.` + ' The places they started from leave the shape.' + (chs.some(c => c.came > 0) ? ' New dots come in between the ones that are left.' : '') + (hid ? ' Some of them are in front of the ball or behind it.' : '')
      : `${step}. No dot landed outside the big ${ring}, so none is thrown out.` + (Sh.thin[k] === '0' || Sh.thin[k] === '1' ? ' What this step takes is finer than the gaps between the dots.' : '');
  }
  return { key: ph.key, label, say, i: ph.i, t: ph.t };
}
// What the picture of starting places shows in a part of step k + 1: the step k and the fraction u of the blend
// (learnShapeTint, learnShapeLevels), and how strongly it shows behind the dots (back).
function learnShapeBackdrop(k, ph, three) {
  const e = learnShapeEase, q = LEARN_SHAPE_QUIET[three ? 3 : 2], w = LEARN_SHAPE_QUIET.whole;
  // the picture stays behind the dots, quieter while they move, and shows the bite as they are thrown out
  if (ph.key === 'move') return { k, u: 0, back: ph.i ? q : w - (w - q) * e(0, 0.5, ph.t) };
  return ph.t >= 1 ? { k: k + 1, u: 0, back: w } : { k, u: ph.t, back: q + (w - q) * e(0, 0.3, ph.t) };
}
// The names of the parts of one step, in a row under the sentence. A click plays that part alone.
function learnShapeChips(W) {
  const Sh = LEARN_SHAPE, E = Sh.el, on = learnShapeMovesOn();
  E.parts.hidden = !on;
  if (!on) return;
  const M = learnShapeMoves(), sig = M.chips.join('|');
  if (E.parts.dataset.sig !== sig) {
    E.parts.dataset.sig = sig; E.parts.textContent = '';
    M.chips.forEach((name, i) => {
      const b = document.createElement('button');
      b.type = 'button'; b.tabIndex = -1; b.textContent = name; b.title = `Play this part of the step: ${name}`;
      b.addEventListener('click', () => learnShapePlayPart(i));
      E.parts.appendChild(b);
    });
  }
  const at = W.part ? W.part.i : -1;
  [...E.parts.children].forEach((b, i) => { b.classList.toggle('is-on', i === at); b.classList.toggle('is-past', at >= 0 && i < at); });
}
// Play one part of the step under way (at a whole step: of the step that starts there), and stop at its end.
function learnShapePlayPart(i) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N, n = learnShapeMoves().keys.length;
  if (!n || !learnShapeIsOn()) return;
  const k = Math.min(N - 1, Math.floor(Sh.pos + 1e-9)), end = i + 1 >= n ? k + 1 : k + (i + 1) / n;
  learnShapeStop();
  Sh.endSide = false;
  if (learnShapeCalm()) { Sh.pos = end; Sh.endSide = i + 1 < n; learnShapeNow(); return; }      // no motion wanted: the part's end, at once
  Sh.pos = k + i / n;
  learnShapePlay(end);
}

// The words
function learnShapeWords() {
  const L = LEARN, Sh = LEARN_SHAPE, N = LEARN_SHAPE_N, three = L.space === 3, ring = three ? 'ball' : 'circle';
  const k = Math.min(N, Math.floor(Sh.pos + 1e-9)), u = Sh.pos - k, whole = u < 1e-9, kind = Sh.kind, n = S.n;
  const [first, second] = Sh.side ? ['left', 'right'] : ['upper', 'lower'], First = Sh.side ? 'Left' : 'Upper', Second = Sh.side ? 'Right' : 'Lower';
  const start = kind === 'm' || learnShapeStartWhole();    // the Julia shape begins as the whole big circle or ball
  // Of which pictures on show nothing is left after these k steps (learnShapeDraw finds out). A flat picture is
  // asked point by point, and what it cannot show, a dust of single points, say, is not claimed to be gone.
  const goneM = k > 0 && kind !== 'j' && Sh.gone.includes('m'), goneJ = k > 0 && kind !== 'm' && Sh.gone.includes('j');
  const gone = kind === 'm' ? goneM : kind === 'j' ? goneJ : goneM && goneJ, steps = `${k} step${k === 1 ? '' : 's'}`;
  // the bite of the step under way is too fine to see in the pictures as they stand (learnShapeDraw finds out)
  const thin = k < N && Sh.thin[k] === '1';
  // calm: while the steps play from end to end the sentence stays the same, since one that changes every third of a
  // second cannot be read. With Move by move every part of a step has its own sentence, also while the steps play.
  const mvOn = learnShapeMovesOn();
  const calm = !mvOn && Sh.playing && Sh.until === null && Sh.pos > 1e-9, pics = kind === 'both' ? 's' : '';
  const mName = 'the Mandelbrot shape', jName = 'the Julia shape for the diamond’s c';
  // every sentence is short enough for three lines on a phone: about 150 letters
  let say;
  if (gone) {
    say = calm ? `Nothing is left to see: every point of the picture${pics} has been thrown out.`
      : whole ? `After ${steps} nothing is left to see: every point of the picture${pics} has been thrown out.`
        : `Step ${k + 1}: there is nothing left to take it. Every point of the picture${pics} has already been thrown out.`;
  } else if (calm) {
    // a bite has been too fine by this step and none from here on can be seen, so the sentence does not come and go
    say = k < N && Sh.thin.slice(0, k + 1).includes('1') && !Sh.thin.slice(k).includes('0') ? 'The bites are now too fine to see at this size. Zoom in.'
      : `At each step${kind === 'both' ? ', in both pictures,' : ''} every point that is still here takes one more step. The ones that land outside the big ${ring} are thrown out.`;
  } else if (whole && (goneM || goneJ)) {
    say = `After ${steps}. ${First}: ${goneM ? 'nothing is left to see' : mName}. ${Second}: ${goneJ ? 'nothing is left to see' : jName}.`;
  } else if (whole && k === 0) {
    // less: a 3D Julia shape that does not begin as the whole ball, with an approach whose dials put the picture's
    // points further out than they look (learnShapeStartWhole)
    const less = `With this approach’s dials as they stand, the points near the surface of the big ball already count as outside`;
    say = kind === 'm' ? `The big ${ring}: every point no further than 2 from the centre. Each point is tried as the number c, and its dot starts on that same point.`
      : kind === 'j' ? (start ? `The big ${ring}. Every point is a place to start from, and all of them use the same c, the diamond.`
        : `The start. ${less}, so the shape begins smaller.`)
        : start ? `Two big ${ring}s. ${First}: each point is tried as the number c, and its dot starts there. ${Second}: each point is where a dot starts, all with the diamond’s c.`
          : `The start. ${First}: each point is tried as the number c. ${Second}: the points near the ball’s surface already count as outside.`;
  } else if (whole) {
    const after = `What is left after ${steps}`;
    if (k === N) {
      // "becomes the set" is said only where it is known: a whole power of 2 or more on the page (then a point that
      // has left the big circle never comes back), and for a Julia shape a c that lies inside the big circle itself
      const ends = !three && Number.isInteger(n) && n >= 2, plain = n === 2 && !S.abs[0] && !S.abs[1] && !S.flip[0], cIn = Math.hypot(Sh.c[0], Sh.c[1]) <= 2;
      const m = 'the Mandelbrot set' + (plain ? '' : ' of this rule');
      say = `${after}.` + (!ends || (kind === 'j' && !cIn) ? ' The picture stops here. More steps could only take more away.'
        : kind === 'm' ? ` After endlessly many steps this becomes ${m}.`
          : kind === 'j' ? ' After endlessly many steps this becomes the Julia set of this c.'
            : cIn ? ` After endlessly many steps these become ${m} (${first}) and the Julia set of the diamond’s c (${second}).`
              : ` After endlessly many steps the ${first} picture becomes ${m}.`);
    } else say = kind === 'both' ? `${after}. ${First}: ${mName}. ${Second}: ${jName}.` : `${after}.`;
  } else if (thin) {
    say = `Step ${k + 1}: this bite is too fine to see at this size. Zoom in.`;
  } else {
    say = `Step ${k + 1}: ${kind === 'both' ? 'in both pictures ' : ''}every point that is still here takes one more step. The ones that land outside the big ${ring} are thrown out.`;
  }
  // Move by move: between two whole steps the words are those of the part being played, unless nothing is left
  let part = null;
  if (mvOn && !whole && k < N && !gone) { part = learnShapePartWords(k, learnShapePart(u)); say = part.say; }
  const where = whole ? `Step ${k} of ${N}: <b>${k === 0 ? 'the start' : 'what is left'}</b>` : `Step ${k + 1} of ${N}: <b>${part ? part.label : 'under way'}</b>`;
  const read = whole ? (k === 0 ? 'the start' : `after ${k} step${k === 1 ? '' : 's'}`) : part ? `step ${k + 1}: ${part.label}` : `step ${k + 1}`;
  return { say, where, read, k, u, whole, part };
}

// Where the pictures stand
function learnShapePanes(w, h) {
  const Sh = LEARN_SHAPE, kinds = learnShapeKinds();
  let rects;
  if (kinds.length === 1) rects = [[0, 0, w, h]];
  else {
    // next to each other or one above the other, whichever leaves the two circles larger
    Sh.side = Math.min(w / 2, h) >= Math.min(w, h / 2);
    const a = Math.floor((Sh.side ? w : h) / 2);
    rects = Sh.side ? [[0, 0, a, h], [a, 0, w - a, h]] : [[0, 0, w, a], [0, a, w, h - a]];
  }
  return rects.map((r, i) => {
    // at zoom 1 the big circle takes 84% of the smaller side; of two small pictures (Both on a phone) 76%, so that
    // the labels in the corners and the buttons the stage carries there stand clear of it
    const share = kinds.length === 2 && Math.min(r[2], r[3]) < 260 ? 0.19 : 0.21;
    const V = Sh.view2[kinds[i]], s = share * Math.min(r[2], r[3]) * V.zoom;
    return { kind: kinds[i], x: r[0], y: r[1], w: r[2], h: r[3], s, cx: r[0] + r[2] / 2, cy: r[1] + r[3] / 2, V, dia: null };
  });
}
const learnShapePaneAt = (x, y) => LEARN_SHAPE.panes.find(P => x >= P.x && x < P.x + P.w && y >= P.y && y < P.y + P.h) || null;
const learnShapeHold = V => { const m = 2 * (1 - 1 / V.zoom); V.x = clamp(V.x, -m, m) + 0; V.y = clamp(V.y, -m, m) + 0; };

// Drawing
function learnShapeCols() {
  const Sh = LEARN_SHAPE, C = LEARN.col;
  if (Sh.cols && Sh.cols.from === C) return Sh.cols;
  const rgb = s => { try { const v = hexRgb(s); return v.every(x => isFinite(x)) ? v : [0.5, 0.5, 0.5]; } catch (err) { return [0.5, 0.5, 0.5]; } };
  return (Sh.cols = { from: C, stage: rgb(C.stage), brass: rgb(C.brass), bad: rgb(C.bad), ink: rgb(C.ink), ink2: rgb(C.ink2) });
}
function learnShapeQuality() {
  const Sh = LEARN_SHAPE;
  return Sh.playing || Sh.drag || Sh.pinch || performance.now() - Sh.hot < 140 ? 'move' : 'still';
}
// Everything a picture depends on, as one string. A change soon after the last one means a dial or the slider is
// being dragged: the pictures stay coarse until that rests. In 3D every change counts as such: the picture is drawn
// coarse at once and fine 180 ms later, and the cost of the coarse one tells the 3D module how fine the next can be.
function learnShapeSeen() {
  const Sh = LEARN_SHAPE, a = ap(), V = Sh.view2, W = Sh.view3;
  const sig = [S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.kind, LEARN.space, V.m.x, V.m.y, V.m.zoom, V.j.x, V.j.y, V.j.zoom,
    W.yaw, W.pitch, W.zoom, LEARN.space === 3 ? Sh.pos : ''].join('|');
  if (sig === Sh.seen) return;
  const now = performance.now();
  if (LEARN.space === 3 || (Sh.seen && now - Sh.touched < 250)) Sh.hot = now;
  Sh.touched = now; Sh.seen = sig;
}
// The kept numbers of one flat picture, worked out again when they do not fit the picture asked for.
function learnShapeChart(P, quality) {
  const Sh = LEARN_SHAPE, V = P.V, N = LEARN_SHAPE_N;
  // the part of the pane the big circle covers, in whole CSS pixels
  const x0 = Math.max(P.x, Math.floor(P.cx + (-2 - V.x) * P.s)), x1 = Math.min(P.x + P.w, Math.ceil(P.cx + (2 - V.x) * P.s));
  const y0 = Math.max(P.y, Math.floor(P.cy - (2 - V.y) * P.s)), y1 = Math.min(P.y + P.h, Math.ceil(P.cy - (-2 - V.y) * P.s));
  const key = [P.kind, S.n, S.abs[0], S.abs[1], S.flip[0], P.kind === 'j' ? Sh.c[0] + ',' + Sh.c[1] : '', x0, y0, x1, y1, P.s, P.cx, P.cy, V.x, V.y].join('|');
  // samples to a CSS pixel, each way: 2 at rest; 1 while something is dragged, or 1/2 when the power needs the polar
  // form, which costs some twenty times more a sample
  const polar = !(Number.isInteger(S.n) && S.n >= 2 && S.n <= 8), want = quality === 'move' ? (polar ? 0.5 : 1) : 2;
  let M = Sh.maps[P.kind];
  if (M && M.key === key && M.dens >= want) return M;
  const dens = want, w = Math.ceil(Math.max(0, x1 - x0) * dens), h = Math.ceil(Math.max(0, y1 - y0) * dens);
  if (!M) M = Sh.maps[P.kind] = { cv: document.createElement('canvas'), n: 0 };
  Object.assign(M, { key, dens, w, h, bx: x0, by: y0, bw: w / dens, bh: h / dens });
  if (!w || !h) return M;
  if (M.n !== w * h) { M.n = w * h; M.map = new Uint8Array(M.n); M.edge = new Uint8Array(M.n); M.tmp = new Uint8Array(M.n); }
  if (M.cv.width !== w || M.cv.height !== h) { M.cv.width = w; M.cv.height = h; M.g = M.cv.getContext('2d'); M.img = M.g.createImageData(w, h); M.px = new Uint32Array(M.img.data.buffer); }
  const d = 1 / (dens * P.s);
  learnShapeMap(P.kind, Sh.c, S.n, S.abs, S.flip, V.x + (x0 + 0.5 / dens - P.cx) / P.s, V.y - (y0 + 0.5 / dens - P.cy) / P.s, d, d, w, h, N, M.map);
  const band = dens >= 2 ? 2 : 1;
  learnShapeEdge(M.map, w, h, band, M.tmp, M.edge);
  // thick is kept in pixels of the picture (see learnShapeTally)
  const tally = learnShapeTally(M.map, M.edge, M.n, N, band);
  M.left = tally.left; M.thick = tally.thick.map(t => t / dens);
  return M;
}
// One flat picture for the slider's position k + u: the numbers become colours. What is left after step k + 1 is
// the body. The points thrown out at step k + 1 (the bite) light up and fade. The outline of the shape before
// fades out, and the outline of shape k comes up where the bite was.
function learnShapeTint(M, k, u, keep) {
  // keep: when the canvas already holds the colours of this very picture they are not worked out again (Move by move)
  if (keep) { const sig = [k, u, M.key, M.dens].join('|'), of = learnShapeCols(); if (M.tint === sig && M.tintOf === of) return; M.tint = sig; M.tintOf = of; } else M.tint = '';
  const K = learnShapeCols(), e = learnShapeEase, A = 1, G = 0.85;   // how solid the body is, and the outlines at their strongest
  const pack = (c, a) => ((Math.round(clamp(a, 0, 1) * 255) << 24) | (Math.round(c[2] * 255) << 16) | (Math.round(c[1] * 255) << 8) | Math.round(c[0] * 255)) >>> 0;
  const t = e(0, 0.22, u), ba = A * (1 - e(0.45, 1, u)), bc = K.brass.map((x, i) => x + (K.bad[i] - x) * t);
  const gNew = G * e(0.5, 1, u), gOld = G * (1 - e(0, 0.6, u)), oa = gNew + ba * (1 - gNew);
  const body = pack(K.brass, A), bite = pack(bc, ba), old = pack(K.ink2, gOld);
  const rim = oa > 0 ? pack(bc.map((x, i) => (K.ink2[i] * gNew + x * ba * (1 - gNew)) / oa), oa) : 0;   // the new outline, laid over the bite
  const map = M.map, edge = M.edge, px = M.px, k1 = k + 1;
  for (let o = 0, n = M.n; o < n; o++) {
    const m = map[o];
    px[o] = m > k1 ? body : m === k1 ? (edge[o] <= k ? rim : bite) : m === k && edge[o] < k ? old : 0;
  }
  M.g.putImageData(M.img, 0, 0);
}
// The writing kit of a frame: a label with a rim in the stage colour, kept inside a box.
function learnShapeLabel(g, C, w, h) {
  return (txt, x, y, col, align, px, weight, box) => {
    const B = box || [0, 0, w, h];
    g.font = `${weight || 500} ${px}px ${C.mono}`; g.textAlign = align || 'left'; g.textBaseline = 'middle';
    const tw = g.measureText(txt).width, l = align === 'right' ? tw : align === 'center' ? tw / 2 : 0;
    x = clamp(x, B[0] + 5 + l, Math.max(B[0] + 5 + l, B[0] + B[2] - 5 - (tw - l))); y = clamp(y, B[1] + 9, Math.max(B[1] + 9, B[1] + B[3] - 9));
    g.lineWidth = 4; g.strokeStyle = C.stage; g.globalAlpha = 0.92; g.strokeText(txt, x, y); g.globalAlpha = 1; g.fillStyle = col; g.fillText(txt, x, y);
  };
}
function learnShapeDiamond(g, C, label, q, small) {
  const r = 7;
  g.beginPath(); g.moveTo(q[0], q[1] - r); g.lineTo(q[0] + r, q[1]); g.lineTo(q[0], q[1] + r); g.lineTo(q[0] - r, q[1]); g.closePath();
  g.globalAlpha = 0.9; g.fillStyle = C.stage; g.fill(); g.globalAlpha = 1; g.strokeStyle = C.ink; g.lineWidth = 2; g.setLineDash([]); g.stroke();
  label('c', q[0] + 11, q[1] + 9, C.ink, 'left', small ? 12 : 13.5, 600);
}
// One flat picture: faint axes, what is left, the big circle, a few numbers, the diamond. mv: null with At once;
// with Move by move { k, ph, back }: the step the dots are at, the part being played (null at a whole step) and how
// strongly the picture shows behind the dots; k and u are then what learnShapeBackdrop gives.
function learnShapeFlat(g, P, k, u, quality, C, label, small, mv) {
  const Sh = LEARN_SHAPE, V = P.V, X = x => P.cx + (x - V.x) * P.s, Y = y => P.cy - (y - V.y) * P.s, box = [P.x, P.y, P.w, P.h];
  const line = (x0, y0, x1, y1, col, wd, al, dash) => { g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.strokeStyle = col; g.lineWidth = wd; g.globalAlpha = al; g.setLineDash(dash || []); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; };
  g.save(); g.beginPath(); g.rect(P.x, P.y, P.w, P.h); g.clip();
  line(P.x, Y(0), P.x + P.w, Y(0), C.ink2, 1, 0.55); line(X(0), P.y, X(0), P.y + P.h, C.ink2, 1, 0.55);
  // A few numbers along the axes: a mark at each, and the figure where there is room for it. They lie under the
  // shape, like the axes. step: the finest that leaves the marks 80 pixels apart; a small picture names only 2 and −2.
  const step = [0.02, 0.05, 0.1, 0.2, 0.5, 1].find(s => s * P.s >= 80) || 1, dec = step >= 1 ? 0 : step >= 0.1 ? 1 : 2, tight = P.s < 46;
  const inX = x => x > P.x + 4 && x < P.x + P.w - 4, inY = y => y > P.y + 4 && y < P.y + P.h - 4;
  for (let i = Math.ceil(-2 / step - 1e-9); i <= Math.floor(2 / step + 1e-9); i++) {
    if (!i) continue;
    const v = i * step, far = Math.abs(Math.abs(v) - 2) < 1e-9;
    line(X(v), Y(0) - 3, X(v), Y(0) + 3, C.ink2, 1, 0.8); line(X(0) - 3, Y(v), X(0) + 3, Y(v), C.ink2, 1, 0.8);
    if (tight && !far) continue;
    // a figure follows its mark; when the axis itself is out of the picture it waits at the picture's edge
    if (inX(X(v))) label(learnVNum(v, dec), X(v) + (far ? (v > 0 ? 9 : -9) : 0), Y(0) + 12, C.ink2, far ? (v > 0 ? 'left' : 'right') : 'center', small ? 10 : 11, 500, box);
    // The figures of the upright axis stand to the right of it, clear of the upper and lower tips of the Mandelbrot
    // shape. In a small picture the 2 at the top is left out: the labels of the picture's corner stand there.
    if (tight && v > 0) continue;
    if (inY(Y(v))) label(learnVNum(v, dec), X(0) + 8, Y(v) + (far ? (v > 0 ? -9 : 9) : 0), C.ink2, 'left', small ? 10 : 11, 500, box);
  }
  const M = learnShapeChart(P, quality);
  if (M.w && M.h) {
    learnShapeTint(M, k, u, !!mv); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    if (mv) g.globalAlpha = mv.back;
    g.drawImage(M.cv, M.bx, M.by, M.bw, M.bh);
    if (mv) g.globalAlpha = 1;
  }
  // the big circle; while the dots are away from home it is drawn firmly: it is the line the throwing out is judged by
  g.beginPath(); g.arc(X(0), Y(0), 2 * P.s, 0, 2 * PI);
  if (mv && mv.ph) { g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.9; g.stroke(); g.globalAlpha = 1; }
  else { g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.globalAlpha = 0.8; g.setLineDash([4, 4]); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; }
  if (mv) {
    const to2 = v => [X(v[0]), Y(v[1]), 0];
    if (Sh.see !== 'dots') learnShapeLiveFlat(g, P, to2, mv.k, mv.ph);
    if (Sh.see !== 'skin') learnShapeDotsDraw(g, P, to2, P.s, mv.k, mv.ph, false);
  }
  P.dia = null;
  if (Sh.kind !== 'm') {
    const q = [X(Sh.c[0]), Y(Sh.c[1])];
    if (q[0] > P.x - 8 && q[0] < P.x + P.w + 8 && q[1] > P.y - 8 && q[1] < P.y + P.h + 8) { P.dia = q; learnShapeDiamond(g, C, (t, x, y, col, al, px, wt) => label(t, x, y, col, al, px, wt, box), q, small); }
  }
  g.restore();
}
// The 3D module's view, made the first time 3D is asked for. null (and a sentence in threeNote) when there is none.
function learnShapeThree() {
  const Sh = LEARN_SHAPE;
  if (Sh.three || Sh.threeTried) return Sh.three;
  Sh.threeTried = true;
  let view = null;
  try { view = learnShape3d.make(); } catch (err) { console.warn('learnShape3d.make failed', err); }
  if (!view) {
    Sh.threeNote = learnShape3d.note() || 'This device cannot draw the 3D picture. The 2D page still works.';
    return null;
  }
  view.canvas.classList.add('learn-shape-gl'); view.canvas.setAttribute('aria-hidden', 'true'); view.canvas.hidden = true;
  // When the graphics are lost the module's sentence stands in the picture's place; when they come back the page puts
  // the picture back in sight, a task later (after the module's own listener), and asks learnShapeAbove again.
  for (const ev of ['webglcontextlost', 'webglcontextrestored']) view.canvas.addEventListener(ev, () => setTimeout(() => { Sh.above = {}; learnShapeNow(); }, 0));
  stage.insertBefore(view.canvas, Sh.el.canvas);
  return (Sh.three = view);
}
// The skins of one 3D picture for the slider's position k + u. At a whole step: the shape as solid glass and the
// shape before as a ghost. In between: the skin of shape k + 1 comes up to solid glass, and the skin of shape k
// thins to a peel, takes the warning colour, then pales to a ghost while the old ghost fades out.
// solid: between the steps of LEARN_SHAPE_GLASS.deep the near side of the body goes from glass to solid. bite: how
// thick the part is that the step takes, in pixels (undefined: not known); a thin bite gets a faint peel, and none
// when too fine to see.
function learnShapeLevels(k, u, bite) {
  const G = LEARN_SHAPE_GLASS, e = learnShapeEase, grey = 0.55, out = [], deep = e(G.deep[0], G.deep[1], k + u);
  const before = k > 0;      // a ghost of the shape before
  if (u < 1e-9) { out.push({ k, alpha: G.solid, tint: 0, solid: deep }); if (before) out.push({ k: k - 1, alpha: G.ghost, tint: 0, ghost: grey, solid: 0 }); }
  else {
    const thinned = e(0, 0.18, u), pale = e(0.55, 1, u), show = bite === undefined ? 1 : e(0.5, 3, bite), peel = Math.max(G.peel * show, G.ghost);
    out.push({ k: k + 1, alpha: G.solid * e(0, 0.12, u), tint: 0, solid: deep });
    out.push({ k, alpha: G.solid + (peel - G.solid) * thinned + (G.ghost - peel) * pale, tint: show * e(0.08, 0.25, u) * (1 - pale), ghost: grey * pale, solid: deep * (1 - thinned) });
    if (before) out.push({ k: k - 1, alpha: G.ghost * (1 - e(0, 0.5, u)), tint: 0, ghost: grey, solid: 0 });
  }
  return out.filter(l => l.alpha > 0.004);
}
// Where a point of space lands in a pane of the 3D picture, as learnShape3d.proj gives it: to(v), and s, pixels to
// a unit. A flat camera, the big ball taking 80% of the smaller side at zoom 1.
function learnShapeProj(P) { return learnShape3d.proj(LEARN_SHAPE.view3, [P.x, P.y, P.w, P.h]); }
// The 3D pictures. Returns '' when they are drawn, or the sentence to show in their place. mv: as for learnShapeFlat.
function learnShapeSolid(g, panes, k, u, quality, C, label, small, above, mv) {
  const Sh = LEARN_SHAPE, T = learnShapeThree(), K = learnShapeCols();
  if (!T) return Sh.threeNote;
  // Each picture has skins of its own: the thickness of its bite comes from above[i] (learnShapeAbove).
  const lv = panes.map((P, i) => {
    const A = above ? above[i] : null, bite = A && k < LEARN_SHAPE_N ? A.thick[k] * A.unit * learnShapeProj(P).s : undefined;
    return learnShapeLevels(k, u, bite);
  });
  const V = Sh.view3, o = {
    panes: panes.map((P, i) => ({ kind: P.kind, rect: [P.x, P.y, P.w, P.h], levels: lv[i] })), c: Sh.c.slice(),
    yaw: V.yaw, pitch: V.pitch, zoom: V.zoom, quality, colours: { bg: K.stage, body: K.brass, warn: K.bad, ink: K.ink },
  };
  let res = null;
  if (T.canvas.hidden) T.canvas.hidden = false;      // the module fits its buffer to the box, so the box has to be there
  // Move by move: while only the dots move, the glass picture is the same from frame to frame. It is then not drawn
  // again (its canvas keeps it), and behind the dots it shows faintly, by the opacity of its canvas.
  const a3 = ap(), sig3 = mv ? JSON.stringify([o, a3.id, S.param[a3.id], S.n, S.abs, S.flip, T.canvas.clientWidth, T.canvas.clientHeight, window.devicePixelRatio]) : '';
  if (mv && sig3 === Sh.sig3 && Sh.res3 && Sh.res3.ok) res = Sh.res3;
  else {
    try { res = T.draw(o); } catch (err) { if (!Sh.warned) { Sh.warned = true; console.warn('learnShape3d.draw failed', err); } }   // said once, not once a frame
    Sh.sig3 = sig3; Sh.res3 = res;
  }
  // with the lit body on show the glass picture is put out of sight, or the two would show through each other
  const faint = mv && Sh.see !== 'dots' ? '0' : mv && mv.back < 0.999 ? String(Math.round(mv.back * 1000) / 1000) : '';
  if (T.canvas.style.opacity !== faint) T.canvas.style.opacity = faint;
  if (!res || !res.ok) return (res && res.note) || learnShape3d.note() || 'The 3D picture could not be drawn for these settings.';
  // Over the glass: the rim of the big ball as a dashed ring, faintly the circle in which the flat plane cuts it,
  // and the diamond c with a thin line down to the flat plane, so that its height can be read.
  const livePanes = [];      // the panes whose surface is drawn as a closed lit body
  for (const P of panes) {
    const pr = learnShapeProj(P), to = pr.to, mid = to([0, 0, 0]), box = [P.x, P.y, P.w, P.h];
    P.dia = null;
    g.save(); g.beginPath(); g.rect(P.x, P.y, P.w, P.h); g.clip();
    g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.setLineDash([4, 4]);
    g.beginPath(); g.arc(mid[0], mid[1], 2 * pr.s, 0, 2 * PI); g.globalAlpha = 0.6; g.stroke();
    g.beginPath(); for (let i = 0; i <= 72; i++) { const a = i / 72 * 2 * PI, q = to([2 * Math.cos(a), 2 * Math.sin(a), 0]); if (i) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); }
    g.lineWidth = 1; g.setLineDash([2, 4]); g.globalAlpha = 0.4; g.stroke(); g.setLineDash([]); g.globalAlpha = 1;
    // while the dots are away from home the big ball's outline is drawn firmly
    if (mv && mv.ph) { g.beginPath(); g.arc(mid[0], mid[1], 2 * pr.s, 0, 2 * PI); g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.85; g.stroke(); g.globalAlpha = 1; }
    if (mv && Sh.see !== 'dots') livePanes.push(P);
    if (mv && Sh.see !== 'skin') learnShapeDotsDraw(g, P, to, pr.s, mv.k, mv.ph, true);
    if (Sh.kind === 'm') { g.restore(); continue; }
    const q = to(Sh.c), f = to([Sh.c[0], Sh.c[1], 0]);
    // as in a flat picture: a diamond that is out of the picture is not drawn, and neither is its letter
    if (!(q[0] > P.x - 8 && q[0] < P.x + P.w + 8 && q[1] > P.y - 8 && q[1] < P.y + P.h + 8)) { g.restore(); continue; }
    if (Math.hypot(q[0] - f[0], q[1] - f[1]) > 3) {
      g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(f[0], f[1]); g.strokeStyle = C.ink; g.lineWidth = 1; g.globalAlpha = 0.7; g.setLineDash([2, 3]); g.stroke(); g.setLineDash([]);
      g.beginPath(); g.arc(f[0], f[1], 1.75, 0, 2 * PI); g.fillStyle = C.ink; g.fill(); g.globalAlpha = 1;
    }
    learnShapeDiamond(g, C, (t, x, y, col, al, px, wt) => label(t, x, y, col, al, px, wt, box), q, small);
    g.restore();
  }
  if (livePanes.length) learnShapeLiveDraw3(livePanes, mv); else if (Sh.mesh) Sh.mesh.canvas.hidden = true;
  return '';
}
// In a flat picture P.dia is where the diamond stands, and it can be taken hold of there. Over a 3D picture the
// diamond is only shown: there c is moved with its dials.
function learnShapeDraw() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, cv = E.canvas;
  if (!learnShapeIsOn() || !cv) return;
  const w = stage.clientWidth, h = stage.clientHeight;
  if (!w || !h) return;
  const t0 = performance.now(), dpr = clamp(window.devicePixelRatio || 1, 1, 3), bw = Math.round(w * dpr), bh = Math.round(h * dpr);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; }
  if (!L.col) learnVTheme();
  if (L.space === 1) { L.space = 2; L.stale = true; }
  learnShapeSeen();
  const C = L.col, g = cv.getContext('2d'), three = L.space === 3, quality = learnShapeQuality(), small = w < 480;
  const N = LEARN_SHAPE_N, k = Math.min(N, Math.floor(Sh.pos + 1e-9)), u = k >= N ? 0 : clamp(Sh.pos - k, 0, 1), panes = Sh.panes = learnShapePanes(w, h);
  const label = learnShapeLabel(g, C, w, h);
  g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h); g.lineJoin = g.lineCap = 'round';
  let note = '';
  // a flat picture's numbers do not change while the steps play, so playing alone does not make it coarse
  const flatQ = Sh.drag || Sh.pinch || t0 - Sh.hot < 140 ? 'move' : 'still';
  // asked before the picture is drawn, so that the answer does not have to wait for a fine picture as well
  const above = three && learnShapeThree() ? panes.map(P => learnShapeAbove(P.kind, quality)) : null;
  // Move by move: ph, the part of the step being played (null at a whole step); bd, what the picture of starting
  // places shows in it and how strongly; mv, what the pictures need to draw the dots.
  const mvOn = learnShapeMovesOn(), ph = mvOn && u > 1e-9 && k < N ? learnShapePart(u) : null;
  const bd = ph ? learnShapeBackdrop(k, ph, three) : { k, u, back: mvOn ? LEARN_SHAPE_QUIET.whole : 1 }, mv = mvOn ? { k, ph, back: bd.back } : null;
  if (three) note = learnShapeSolid(g, panes, bd.k, bd.u, quality, C, label, small, above, mv);
  else for (const P of panes) learnShapeFlat(g, P, bd.k, bd.u, flatQ, C, label, small, mv);
  if (Sh.three) Sh.three.canvas.hidden = !three || !!note;
  if (Sh.mesh && (!three || note)) Sh.mesh.canvas.hidden = true;
  if (note) g.clearRect(0, 0, w, h);
  let said = Sh.note !== note;
  if (said) { Sh.note = note; E.note.textContent = note; }
  E.note.hidden = !note;
  // Of which pictures is nothing left after these k steps? A flat picture is asked itself, the whole one only. In 3D:
  // a Mandelbrot shape whose every point the first step throws out (learnShapeZeroOut), or a shape that is gone seen
  // from straight above (learnShapeAbove), unless zoomed in beyond 1.5, where the picture could show finer crumbs.
  const gone = k > 0 && !note ? panes.filter((P, i) => {
    if (three) return (P.kind === 'm' && learnShapeZeroOut()) || (!!above && !!above[i] && Sh.view3.zoom <= 1.5 && above[i].left[k] === 0);
    const M = Sh.maps[P.kind];
    return !!M && !!M.left && P.V.zoom <= 1 + 1e-9 && M.left[k] === 0;
  }).map(P => P.kind).join('') : '';
  if (gone !== Sh.gone) { Sh.gone = gone; said = true; }
  // Of which steps is the bite too fine to see in the pictures as they stand? Those whose bite is thinner than
  // LEARN_SHAPE_THIN pixels in every picture that shows one at all (a step that takes nothing is not "too fine").
  let thin = '';
  if (!note) {
    const px = panes.map((P, i) => {      // thick[k] of each picture, in its own pixels
      if (!three) { const M = Sh.maps[P.kind]; return M && M.thick ? M.thick : null; }
      const A = above ? above[i] : null, s = A ? A.unit * learnShapeProj(P).s : 0;
      return A ? A.thick.map(t => t * s) : null;
    });
    // '1': too fine; '0': a bite that can be seen (or one not known); '-': the pictures show nothing being taken
    for (let j = 0; j < N; j++) {
      let some = false, all = true;
      for (const t of px) { const v = t ? t[j] : NaN; if (v > 0) { some = true; if (!(v < LEARN_SHAPE_THIN)) all = false; } else if (v !== 0) all = false; }
      thin += !all ? '0' : some ? '1' : '-';
    }
  }
  if (thin !== Sh.thin) { Sh.thin = thin; said = true; }
  // between two pictures: a hairline. In the corner of each: its name, and in the first what the slider stands on.
  if (panes.length === 2 && !note) {
    const P = panes[1];
    g.beginPath(); if (Sh.side) { g.moveTo(P.x + 0.5, 0); g.lineTo(P.x + 0.5, h); } else { g.moveTo(0, P.y + 0.5); g.lineTo(w, P.y + 0.5); }
    g.strokeStyle = C.line; g.lineWidth = 1; g.stroke();
  }
  if (!note) {
    const W = learnShapeWords(), narrow = panes[0].w < 300;
    panes.forEach((P, i) => {
      // in Both the Julia picture is named after the diamond that chooses it, where there is room
      const box = [P.x, P.y, P.w, P.h], name = (P.kind === 'm' ? 'Mandelbrot' : 'Julia') + (narrow ? '' : ' shape') + (P.kind === 'j' && panes.length === 2 && P.w >= 330 ? ' for the diamond’s c' : '');
      label(name, P.x + 10, P.y + 15, C.ink, 'left', small ? 12.5 : 14, 600, box);
      // in a part of a step the corner names the part, where there is room; only the throwing out has the warning colour
      if (i === 0) label(W.part && narrow ? `step ${W.k + 1}` : W.read, P.x + 10, P.y + (small ? 32 : 35), W.whole ? C.brass : W.part && W.part.key !== 'gone' ? C.ink : C.bad, 'left', small ? 12.5 : 14, 600, box);
      // where the corner has room for a third line: what a dot is
      if (i === 0 && mv && !small && !narrow) label('a dot keeps the colour of where it started', P.x + 10, P.y + 54, C.ink2, 'left', 12, 500, box);
    });
  }
  if (said) learnShapePaint();      // the hint and the panel say whether there is a 3D picture; the sentence, whether anything is left
  // a coarse picture is followed by a fine one as soon as things rest
  if (quality === 'move' && !Sh.playing && !Sh.drag && !Sh.pinch) {
    clearTimeout(Sh.rest);
    Sh.rest = setTimeout(() => { Sh.rest = 0; if (learnShapeIsOn()) { learnShapePaint(); learnShapeDraw(); } }, 180);
  }
}

// The words and marks on the page
function learnShapePanel() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, three = L.space === 3, a = ap();
  const set = (node, text) => { if (node.textContent !== text) node.textContent = text; };
  const bare = !S.abs.some(Boolean) && !S.flip.some(Boolean), plain = S.n === 2 && bare, first = Sh.side ? 'left' : 'upper', second = Sh.side ? 'right' : 'lower';
  E.cBlock.hidden = Sh.kind === 'm';
  // a named value: its name first, where the name is true (the plain power 2), and the value as the dials name it
  E.named.forEach((b, i) => { const v = LEARN_SHAPE_NAMED[i]; b.firstChild.hidden = !plain; set(b.lastChild, plain ? `(${v.text})` : v.text); });
  // what a step is, in a line
  set(E.intro, 'Take every point inside the big circle (in 3D, the big ball) and let each one take steps. A point that lands outside is thrown out. Press Play under the picture and watch what is left after each step.'
    + ` A step is the lab’s rule: ${S.n === 2 ? 'square' : 'take to the power ' + String(+(+S.n).toFixed(2)).replace('-', '−') + ' (the dial “Power n”)'}, then add c. (Follow: One point shows one step slowly.)`);
  set(E.helpJ, 'The number c is the same for all: the diamond. Each point of the picture is a place where a dot starts.');
  set(E.helpBoth, `${Sh.side ? 'Side by side' : 'One above the other'}. The diamond in the ${first} picture picks one c; the ${second} picture is the Julia shape for that c. `
    + (three ? 'Move c with its dials and watch the ' : 'Drag the diamond and watch the ') + second + ' picture.');
  E.rule.hidden = !three;
  // Sh.note: the sentence the stage shows when there is no 3D picture; learnShapeDraw paints again when it changes
  set(E.rule, !three ? '' : `In 3D the steps follow the approach chosen under Approach and equation, now “${a.name}”, with its dials and power as set there.`
    + (Sh.note ? ' ' + Sh.note : ''));
  // Both on the 2D page, a whole power of 2 or more and no modifier: once c is thrown out of the Mandelbrot shape
  // (the diamond stands outside the left shape), the Julia shape of the same step is in pieces.
  set(E.notice, three
    ? 'The ball is not bent into the shape. It is eaten away: each step removes the points that have just landed outside, and the bites get smaller and finer.'
      + (learnShapeCutHolds() ? ' Slice this 3D shape level through its middle, where the dotted ring runs, and the cut is exactly the 2D picture of the same step.'
        + (Sh.kind === 'm' ? ' (True for this approach.)' : ' (True for this approach while c’s z dial stands at 0.)') : '')
    : 'The circle is not bent into the shape. It is eaten away: each step removes the points that have just landed outside, and the bites get smaller and finer.'
      + (Sh.kind === 'both' && bare && Number.isInteger(S.n) && S.n >= 2 ? ` After a step or two, drag the diamond out of the ${first} shape and the ${second} one falls to pieces.` : ''));
  set(E.eachHelp, Sh.each === 'moves'
    ? 'Dots are laid over the picture, one for each starting place. A dot takes step after step and is never put back: each step is played part by part, the moves of the rule one after another and then the throwing out. The picture behind shows the starting places whose dots are still in.'
      + (Sh.refill ? ' As dots are thrown out, new dots are added: dots that start between the ones that are left. A new dot is not new to the game. It has taken every step so far and was only not drawn.' : '')
      + ' A dot keeps the colour of the place it started from, and a few are drawn larger, with their paths, so that you can follow them. (The last move, Slide, is the one that One point calls Add c.)'
      + (Sh.see !== 'dots' ? ' The surface is the shape as it is at this very moment: every starting place whose dot is inside the big ' + (three ? 'ball' : 'circle') + ' right now. It is drawn again all through a move, so you see which move changes it, and how. A move that only turns the dots changes nothing, because it takes no dot across the big ' + (three ? 'ball' : 'circle') + '.' : '')
    : 'Each step shows only what it leaves. Move by move shows the moves inside each step, played on dots.');
  Sh.dials.sync();
}
function learnShapePaint() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, N = LEARN_SHAPE_N;
  if (!learnShapeIsOn() || !E.bar) return;
  if (L.space === 1) { L.space = 2; L.stale = true; }
  const put = (node, text, html) => { if (node.dataset.t !== text) { node.dataset.t = text; if (html) node.innerHTML = text; else node.textContent = text; } };
  const W = learnShapeWords(), three = L.space === 3;
  put(E.where, W.where, true); put(E.say, W.say);
  // Move by move: the slider goes through the parts of a step, so the hand needs finer notches
  const fine = learnShapeMovesOn() ? '0.005' : '0.05';
  if (E.pos.step !== fine) E.pos.step = fine;
  if (Math.abs(+E.pos.value - Sh.pos) > 1e-6) E.pos.value = Sh.pos;
  E.pos.setAttribute('aria-valuetext', W.whole ? (W.k === 0 ? 'The start' : `What is left after ${W.k} of ${N} steps`)
    : W.part ? `Step ${W.k + 1} of ${N}, ${W.part.label}, ${Math.round(W.part.t * 100)} percent` : `Step ${W.k + 1} of ${N}, ${Math.round(W.u * 100)} percent`);
  learnShapeChips(W);
  // A low phone window: with the row of Each step and Dots the picture's block would be taller than the pin of
  // 85-pin.js holds (PIN_MOST of the window), and the picture would scroll away. The two choices then stand in the
  // panel only. 280: the transport with that row, the gap above it and the pin's 6 px; 236: without the row.
  { const low = PIN.can && PIN.want && PIN.small > 0 && matchMedia('(max-width: 620px)').matches
      && stage.offsetHeight + 280 > PIN.small * PIN_MOST - 2 && stage.offsetHeight + 236 <= PIN.small * PIN_MOST;
    if (E.bar.classList.contains('is-low') !== low) E.bar.classList.toggle('is-low', low); }
  // while Move by move plays, the sentence changes with every part: a reader that speaks the page is not sent each one
  { const live = Sh.playing && W.part ? 'off' : 'polite'; if (E.say.getAttribute('aria-live') !== live) E.say.setAttribute('aria-live', live); }
  for (const r of E.eachs) r.checked = r.value === Sh.each;
  for (const s of E.dotSels) { if (s.value !== Sh.dots) s.value = Sh.dots; s.disabled = Sh.each !== 'moves'; }
  for (const key of ['tint', 'lay', 'see', 'orbits']) { const s = E[key]; if (s.value !== Sh[key]) s.value = Sh[key]; s.disabled = Sh.each !== 'moves' || (key === 'lay' && L.space !== 3); }
  for (const key of ['orbits', 'see', 'lay']) { const s = E.bars[key]; if (s.value !== Sh[key]) s.value = Sh[key]; s.disabled = Sh.each !== 'moves' || (key === 'lay' && L.space !== 3); }
  E.refill.checked = Sh.refill; E.refill.disabled = Sh.each !== 'moves';
  [...E.ticks.children].forEach((b, j) => { b.classList.toggle('is-on', W.whole && j === W.k); b.classList.toggle('is-past', j <= Sh.pos + 1e-9); });
  put(E.play, Sh.playing ? 'Pause' : 'Play'); E.play.setAttribute('aria-pressed', String(Sh.playing));
  E.back.disabled = Sh.pos <= 1e-9; E.fwd.disabled = Sh.pos >= N - 1e-9; E.again.disabled = Sh.pos <= 1e-9 && !Sh.playing;
  const again = three ? 'Back to the big ball' : 'Back to the big circle';
  if (E.again.title !== again) E.again.title = again;
  for (const r of E.kinds) r.checked = r.value === Sh.kind;
  for (const r of E.spaces) r.checked = +r.value === L.space;
  for (const r of L.el.spaces) r.checked = +r.value === L.space;
  for (const r of E.follows) r.checked = r.value === L.follow;
  if (E.speed.value !== L.speed) E.speed.value = L.speed;
  const a = ap(), sig = [Sh.kind, L.space, S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.threeTried, !!Sh.three, Sh.note, Sh.side, Sh.each, Sh.see, Sh.refill].join('|');
  if (sig !== Sh.sig) { Sh.sig = sig; learnShapePanel(); }
  L.el.eqNote.hidden = S.eq === 'z^n + c';
  L.el.hint.hidden = !!Sh.note;
  // over a 3D picture a drag turns the picture, also when it starts on the diamond: there c is moved with its dials
  put(L.el.hint, three ? (Sh.kind === 'm' ? 'Drag to turn the picture. Scroll or pinch to zoom.' : 'Drag to turn, scroll or pinch to zoom. Move c with its dials.')
    : Sh.kind === 'm' ? 'Scroll or pinch to zoom in, then drag to move the picture.' : 'Drag the diamond to move c. Scroll or pinch to zoom.');
  const V = Sh.view2, D = LEARN_SHAPE_VIEW3, W3 = Sh.view3;
  E.viewReset.hidden = three ? !(W3.yaw !== D.yaw || W3.pitch !== D.pitch || Math.abs(W3.zoom - D.zoom) > 1e-6) : !learnShapeKinds().some(kd => Math.abs(V[kd].zoom - 1) > 1e-6);
  L.el.viewReset.hidden = true;
}

// The clock
function learnShapeNow() { if (learnShapeIsOn()) { learnShapePaint(); learnShapeDraw(); } }
function learnShapeQueue() { const Sh = LEARN_SHAPE; if (!Sh.raf && learnShapeIsOn()) Sh.raf = requestAnimationFrame(learnShapeFrame); }
function learnShapeFrame(now) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N;
  Sh.raf = 0;
  if (!learnShapeIsOn()) return;
  if (Sh.playing) {
    const TS = learnShapeMovesOn() ? LEARN_SHAPE_MOVE_SECONDS : LEARN_SHAPE_SECONDS;
    const dt = clamp(now - Sh.last, 0, 80), T = TS[LEARN.speed] || TS.normal, stop = Sh.until === null ? N : Math.min(N, Sh.until);
    // LEARN_SHAPE_MOVE_SECONDS is the time of a step of six parts: with fewer parts a step is shorter, a part as long
    const per = T[0] * (learnShapeMovesOn() ? learnShapeMoves().keys.length / 6 : 1);
    Sh.last = now;
    if (Sh.dwell > 0) Sh.dwell -= dt;
    else {
      // The next whole step: the one above the slider, and the very one it stands a hair under, since the sum of the
      // frames can end a rounding error short of a whole step and Play must not run on through it without its rest.
      const edge = Math.floor(Sh.pos) + 1;
      let pos = Sh.pos + dt / (per * 1000);
      if (pos >= edge) { pos = edge; if (edge < stop) Sh.dwell = T[1] * 1000; }
      if (pos >= stop - 1e-9) { pos = stop; Sh.playing = false; Sh.until = null; Sh.endSide = Math.abs(stop - Math.round(stop)) > 1e-9; }
      Sh.pos = pos;
    }
  }
  learnShapeNow();
  if (Sh.playing) learnShapeQueue();
}
function learnShapeStop() { const Sh = LEARN_SHAPE; Sh.playing = false; Sh.until = null; Sh.dwell = 0; }
function learnShapePlay(until) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N;
  if (!learnShapeIsOn()) return;
  if (Sh.pos >= N - 1e-9) Sh.pos = 0;                 // at the end: play again from the start
  Sh.until = until === undefined ? null : until; Sh.endSide = false;
  Sh.playing = true; Sh.dwell = Sh.until === null && Sh.pos <= 1e-9 ? (LEARN_SHAPE_OPENING[LEARN.speed] || LEARN_SHAPE_OPENING.normal) * 1000 : 0;
  Sh.last = performance.now();
  learnShapePaint(); learnShapeQueue();
}
function learnShapeGoto(pos) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N;
  learnShapeStop(); Sh.endSide = false;
  pos = clamp(+pos || 0, 0, N);
  // close to a whole step is the whole step; with Move by move only very close, or the first part of a step could
  // not be gone through by hand
  Sh.pos = Math.abs(pos - Math.round(pos)) < (learnShapeMovesOn() ? 0.004 : 0.02) ? Math.round(pos) : pos;
  learnShapeNow();
}

// Which part of Learn is on show
// Puts every element of both parts in or out of sight for LEARN.on and LEARN.follow. Called by learnVSetOn too.
function learnShapeSync() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, el = L.el, on = learnShapeIsOn();
  if (!E.bar) return;
  document.body.classList.toggle('is-learn-shape', on);
  if (L.on) { el.bar.hidden = on; el.canvas.hidden = on; }
  E.bar.hidden = !on; E.canvas.hidden = !on; E.viewReset.hidden = true;
  if (!on) {
    learnShapeStop();
    if (Sh.raf) { cancelAnimationFrame(Sh.raf); Sh.raf = 0; }
    clearTimeout(Sh.rest); Sh.rest = 0;
    E.note.hidden = true; el.hint.hidden = false;
    if (Sh.three) Sh.three.canvas.hidden = true;
    if (Sh.mesh) Sh.mesh.canvas.hidden = true;
    Sh.drag = null; Sh.pinch = null; Sh.ptr.clear();
  }
  for (const r of E.follows) r.checked = r.value === L.follow;
  const head = L.follow === 'shape' ? 'Learn: a whole shape, step by step' : E.summaryWas;
  if (E.summary.textContent !== head) E.summary.textContent = head;
}
// Follow = One point or A whole shape. The first switch to the whole shape in a visit plays the steps once by itself.
function learnShapeFollow(shape) {
  const L = LEARN, Sh = LEARN_SHAPE;
  shape = !!shape;
  if ((L.follow === 'shape') !== shape) {
    learnVStop(); learnShapeStop();
    // Choosing another space starts One point's step afresh, so where One point stood is kept on the way in and put
    // back on the way out, when the space is the same again and its points have not been moved.
    if (shape) Sh.place = { space: L.space, k: L.k, pos: L.pos, endSide: L.endSide, pts: JSON.stringify(L.pts[L.space]) };
    else if (Sh.place) {
      const p = Sh.place;
      if (p.space === L.space && p.pts === JSON.stringify(L.pts[L.space])) { L.k = p.k; L.pos = p.pos; L.endSide = p.endSide; }
      Sh.place = null;
    }
    L.follow = shape ? 'shape' : 'point';
    if (shape && L.space === 1) { L.space = 2; L.k = 0; L.pos = 0; L.endSide = false; }
    Sh.sig = ''; Sh.seen = '';
    learnShapeSync();
    if (L.dials) { L.dials.sync(); L.checks.sync(); }
    learnVChanged();
  }
  if (shape && L.on && !Sh.played) {
    Sh.played = true;
    if (!learnShapeCalm()) { Sh.pos = 0; learnShapePlay(); }
  }
}
// Called by learnVDefaults: this part back to how it opens. Follow = A whole shape, both shapes, step 0, c as Learn
// opens on the 2D page, the views as they open. The space, 2D, is put back by learnVDefaults.
function learnShapeDefaults() {
  const L = LEARN, Sh = LEARN_SHAPE;
  learnShapeStop();
  L.follow = 'shape';
  Sh.kind = 'both'; Sh.c = LEARN_V_START[2].c.slice(); Sh.pos = 0;
  Sh.each = 'moves'; Sh.dots = 'some'; Sh.endSide = false; Sh.D = {}; Sh.sig3 = '';
  Sh.orbits = 'few'; Sh.lay = 'both'; Sh.tint = 'mix'; Sh.refill = true; Sh.see = 'dots'; Sh.Lv = {};
  Sh.view2 = { m: { x: 0, y: 0, zoom: 1 }, j: { x: 0, y: 0, zoom: 1 } }; Sh.view3 = learnVCopy(LEARN_SHAPE_VIEW3);
  Sh.sig = ''; Sh.seen = '';
  if (Sh.el.speed) Sh.el.speed.value = 'normal';
  if (Sh.dials) Sh.dials.sync();
  learnShapeSync();
}

// Hands on the picture
function learnShapeZoom(f, x, y) {
  const L = LEARN, Sh = LEARN_SHAPE;
  if (L.space === 3) { Sh.view3.zoom = clamp(Sh.view3.zoom * f, 0.4, 6); return; }
  const P = (x === undefined ? null : learnShapePaneAt(x, y)) || Sh.panes[0];
  if (!P) return;
  const V = P.V, z = clamp(V.zoom * f, 1, 24), X = x === undefined ? P.cx : x, Y = y === undefined ? P.cy : y;
  // the point under the pointer stays under the pointer
  const px = V.x + (X - P.cx) / P.s, py = V.y - (Y - P.cy) / P.s, s = P.s / V.zoom * z;
  V.zoom = z; V.x = px - (X - P.cx) / s; V.y = py + (Y - P.cy) / s;
  learnShapeHold(V);
}
// The wheel over the stage (handed on by the listener in 66-learn-view.js, which keeps it from the solid's camera).
function learnShapeWheel(e) {
  const r = LEARN_SHAPE.el.canvas.getBoundingClientRect();
  learnShapeZoom(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0015)), e.clientX - r.left, e.clientY - r.top);
  learnShapeNow();
}
function learnShapeBind(cv) {
  const L = LEARN, Sh = LEARN_SHAPE, at = e => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  const grab = (x, y, reach) => {                  // the diamond under the pointer, in a flat picture
    if (L.space === 3) return null;
    const P = learnShapePaneAt(x, y);
    return P && P.dia && Math.hypot(x - P.dia[0], y - P.dia[1]) <= reach ? { kind: 'c', P, dx: P.dia[0] - x, dy: P.dia[1] - y } : null;
  };
  const spread = () => { const [p, q] = [...Sh.ptr.values()]; return Math.hypot(p[0] - q[0], p[1] - q[1]); };
  const zoomOf = () => (L.space === 3 ? Sh.view3 : (Sh.pinch && Sh.pinch.P ? Sh.pinch.P.V : Sh.panes[0].V));
  cv.addEventListener('pointerdown', e => {
    if (!learnShapeIsOn() || (e.pointerType === 'mouse' && e.button !== 0)) return;
    try { cv.setPointerCapture(e.pointerId); } catch (err) { /* a pointer that is already gone cannot be captured */ }
    const [x, y] = at(e);
    Sh.ptr.set(e.pointerId, [x, y]);
    if (Sh.ptr.size === 2) { const P = learnShapePaneAt(x, y); Sh.pinch = { d: Math.max(1, spread()), P }; Sh.pinch.zoom = zoomOf().zoom; Sh.drag = null; return; }
    if (L.space === 3) Sh.drag = { kind: 'turn', x, y };
    else {
      const P = learnShapePaneAt(x, y);
      Sh.drag = grab(x, y, e.pointerType === 'mouse' ? 16 : 26) || (P && P.V.zoom > 1 + 1e-6 ? { kind: 'pan', P, x, y } : null);
    }
    if (Sh.drag) e.preventDefault();
  });
  cv.addEventListener('pointermove', e => {
    if (!learnShapeIsOn()) return;
    const [x, y] = at(e);
    if (!Sh.ptr.has(e.pointerId)) {
      const P = L.space === 3 ? null : learnShapePaneAt(x, y);
      cv.style.cursor = L.space === 3 ? '' : grab(x, y, 16) ? 'move' : P && P.V.zoom > 1 + 1e-6 ? 'grab' : 'default';
      return;
    }
    Sh.ptr.set(e.pointerId, [x, y]);
    if (Sh.pinch && Sh.ptr.size === 2) {
      const V = zoomOf(), z = Sh.pinch.zoom * spread() / Sh.pinch.d;
      if (L.space === 3) V.zoom = clamp(z, 0.4, 6); else { V.zoom = clamp(z, 1, 24); learnShapeHold(V); }
      learnShapeQueue(); return;
    }
    const d = Sh.drag;
    if (!d) return;
    if (d.kind === 'turn') {
      const V = Sh.view3;
      V.yaw -= (x - d.x) * 0.01; V.pitch = clamp(V.pitch + (y - d.y) * 0.01, -1.5, 1.5); d.x = x; d.y = y;
    } else if (d.kind === 'pan') {
      const V = d.P.V;
      V.x -= (x - d.x) / d.P.s; V.y += (y - d.y) / d.P.s; d.x = x; d.y = y; learnShapeHold(V);
    } else {
      // the diamond: c follows the pointer, in hundredths, and stays inside the picture
      const P = d.P, V = P.V, r2 = v => clamp(Math.round(v * 100) / 100, -2.4, 2.4) + 0;
      Sh.c = [r2(V.x + (x + d.dx - P.cx) / P.s), r2(V.y - (y + d.dy - P.cy) / P.s), Sh.c[2]];
    }
    learnShapeQueue();      // drawn once a frame, however fast the pointer reports
  });
  const up = e => {
    const busy = !!(Sh.drag || Sh.pinch);
    Sh.ptr.delete(e.pointerId);
    if (Sh.ptr.size < 2) Sh.pinch = null;
    if (!Sh.ptr.size) Sh.drag = null;
    if (busy && !Sh.drag && !Sh.pinch) { Sh.hot = 0; learnShapeNow(); }      // let go: the fine picture, at once
  };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('keydown', e => {
    if (!learnShapeIsOn() || e.ctrlKey || e.metaKey || e.altKey) return;
    const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
    if (e.key === '+' || e.key === '=') learnShapeZoom(1.15);
    else if (e.key === '-') learnShapeZoom(1 / 1.15);
    else if (e.key === ' ') { if (Sh.playing) learnShapeStop(); else learnShapePlay(); }
    else if (dir && L.space === 3) { const V = Sh.view3; V.yaw -= dir[0] * 0.1; V.pitch = clamp(V.pitch + dir[1] * 0.1, -1.5, 1.5); }
    else if (dir && Sh.kind !== 'm') { const st = e.shiftKey ? 0.01 : 0.05; Sh.c = [clamp(+(Sh.c[0] + dir[0] * st).toFixed(2), -2.4, 2.4), clamp(+(Sh.c[1] + dir[1] * st).toFixed(2), -2.4, 2.4), Sh.c[2]]; }
    else return;
    e.preventDefault(); learnShapeNow();
  });
}

// Building it. Called once by learnInit, after the one-point part is built.
function learnShapeInit() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, el = L.el, N = LEARN_SHAPE_N;
  const make = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html) n.innerHTML = html; return n; };
  if (E.bar || !el.panel) return;
  Sh.c = LEARN_V_START[2].c.slice();
  Sh.view2 = { m: { x: 0, y: 0, zoom: 1 }, j: { x: 0, y: 0, zoom: 1 } }; Sh.view3 = learnVCopy(LEARN_SHAPE_VIEW3);

  // the stage: the canvas the flat pictures are drawn on (over a 3D picture it carries only what stands on top),
  // the sentence shown when there is no 3D picture, and the button that puts the view back
  E.canvas = make('canvas', 'learn-canvas learn-shape-canvas');
  E.canvas.id = 'learnShapeCanvas'; E.canvas.tabIndex = 0; E.canvas.hidden = true;
  E.canvas.setAttribute('role', 'img');
  E.canvas.setAttribute('aria-label', 'Picture of what is left of the big circle, or the big ball, after each step. The sentence under the picture says the same in words. With the picture in focus, plus and minus zoom, the space bar plays or pauses, and the arrow keys move c on the 2D page or turn the 3D picture.');
  E.note = make('p', 'stage-note learn-shape-note'); E.note.id = 'learnShapeNote'; E.note.setAttribute('role', 'status'); E.note.hidden = true;
  stage.insertBefore(E.canvas, el.over); stage.insertBefore(E.note, el.over);
  E.viewReset = make('button', 'btn'); E.viewReset.id = 'learnShapeViewReset'; E.viewReset.type = 'button'; E.viewReset.textContent = 'Reset view'; E.viewReset.hidden = true;
  el.over.appendChild(E.viewReset);
  E.viewReset.addEventListener('click', () => {
    if (L.space === 3) Sh.view3 = learnVCopy(LEARN_SHAPE_VIEW3); else for (const kd of learnShapeKinds()) Sh.view2[kd] = { x: 0, y: 0, zoom: 1 };
    learnShapeNow();
  });
  learnShapeBind(E.canvas);

  // the transport, directly under the stage (in the place of the one-point one)
  const seg = (name, value, text, title) => `<label class="seg"${title ? ` title="${title}"` : ''}><input type="radio" name="${name}" value="${value}"><span>${text}</span></label>`;
  E.bar = make('div', 'learn-bar learn-shape-bar',
    '<div class="learn-head"><span class="label learn-where" id="learnShapeWhere"></span>' +
    '<label class="learn-speed"><span class="label">Speed</span><select id="learnShapeSpeed"><option value="slow">Slow</option><option value="normal" selected>Normal</option><option value="fast">Fast</option></select></label></div>' +
    '<p class="learn-say" id="learnShapeSay" aria-live="polite"></p>' +
    '<div class="learn-ticks learn-shape-parts" id="learnShapeParts" role="group" aria-label="The parts of one step" hidden></div>' +
    `<div class="learn-track"><input class="learn-pos" id="learnShapePos" type="range" min="0" max="${N}" step="0.05" value="0" aria-label="Step. Drag to take the steps forwards and backwards by hand.">` +
    '<div class="learn-shape-scale"><div class="learn-shape-ticks" id="learnShapeTicks"></div></div></div>' +
    '<div class="learn-shape-row"><div class="learn-btns" role="group" aria-label="Play the steps">' +
    '<button class="btn learn-step" id="learnShapeBack" type="button" aria-label="Back one step" title="Back one step">◀</button>' +
    '<button class="btn learn-play" id="learnShapePlay" type="button" aria-pressed="false">Play</button>' +
    '<button class="btn learn-step" id="learnShapeFwd" type="button" aria-label="Forward one step" title="Forward one step">▶</button>' +
    '<button class="btn" id="learnShapeAgain" type="button" title="Back to the big circle">Start again</button></div>' +
    // the word "Shape" before the row: without it the row reads Mandelbrot | Julia | Both, and on a phone it can
    // stand right above the lab's own tabs Mandelbrot | Julia | Kleinian | Learn, which mean something else
    '<div class="learn-shape-pick"><span class="label learn-shape-cap" aria-hidden="true">Shape</span><fieldset class="learn-shape-seg" id="learnShapeKindBar"><legend class="learn-shape-legend">Which shape</legend>' +
    seg('learnShapeKindBar', 'm', 'Mandelbrot', 'Mandelbrot shape') + seg('learnShapeKindBar', 'j', 'Julia', 'Julia shape') + seg('learnShapeKindBar', 'both', 'Both') + '</fieldset>' +
    '<fieldset class="learn-shape-seg" id="learnShapeSpaceBar"><legend class="learn-shape-legend">Space</legend>' +
    seg('learnShapeSpaceBar', '2', '2D', '2D page') + seg('learnShapeSpaceBar', '3', '3D', '3D space') + '</fieldset></div>' +
    '<div class="learn-shape-pick learn-shape-how"><span class="label learn-shape-cap" aria-hidden="true">Each step</span><fieldset class="learn-shape-seg" id="learnShapeEachBar"><legend class="learn-shape-legend">Each step</legend>' +
    seg('learnShapeEachBar', 'once', 'At once', 'Each step shows only what it leaves') + seg('learnShapeEachBar', 'moves', 'Move by move', 'The moves inside each step, played on dots') + '</fieldset>' +
    '<label class="learn-shape-dots"><span class="label learn-shape-cap">Dots</span><select id="learnShapeDotsBar"><option value="few">Few</option><option value="some">Some</option><option value="many">Many</option><option value="most">Very many</option></select></label>' +
    '<label class="learn-shape-dots"><span class="label learn-shape-cap">Orbits</span><select id="learnShapeOrbitsBar"><option value="few">A few dots</option><option value="all">Every dot</option><option value="none">None</option></select></label>' +
    '<label class="learn-shape-dots"><span class="label learn-shape-cap">In 3D</span><select id="learnShapeLayBar"><option value="grid">Full grid</option><option value="sheets">Sheets</option><option value="shells">Shells</option><option value="both">Sheets and shells</option></select></label>' +
    '<label class="learn-shape-dots"><span class="label learn-shape-cap">Show</span><select id="learnShapeSeeBar"><option value="dots">Dots</option><option value="skin">Surface</option><option value="both">Both</option></select></label></div></div>');
  E.bar.id = 'learnShapeBar'; E.bar.hidden = true;
  el.bar.after(E.bar);
  for (const [key, id] of [['where', 'learnShapeWhere'], ['say', 'learnShapeSay'], ['pos', 'learnShapePos'], ['ticks', 'learnShapeTicks'], ['back', 'learnShapeBack'], ['play', 'learnShapePlay'], ['fwd', 'learnShapeFwd'], ['again', 'learnShapeAgain'], ['speed', 'learnShapeSpeed']]) E[key] = E.bar.querySelector('#' + id);
  for (let j = 0; j <= N; j++) {
    const b = make('button'); b.type = 'button'; b.tabIndex = -1; b.textContent = String(j); b.title = j ? `What is left after ${j} step${j === 1 ? '' : 's'}` : 'The start';
    b.style.left = (j / N * 100) + '%';
    b.addEventListener('click', () => learnShapeGoto(j));
    E.ticks.appendChild(b);
  }
  E.pos.addEventListener('input', () => learnShapeGoto(+E.pos.value));
  // the arrow keys on the slider go by whole steps (the slider's own step is for the hand)
  E.pos.addEventListener('keydown', e => {
    const d = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1 }[e.key];
    if (!d || e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault();
    learnShapeGoto(d > 0 ? Math.floor(Sh.pos + 1e-9) + 1 : Math.ceil(Sh.pos - 1e-9) - 1);
  });
  E.play.addEventListener('click', () => { if (Sh.playing) { learnShapeStop(); learnShapeNow(); } else learnShapePlay(); });
  E.back.addEventListener('click', () => learnShapeGoto(Math.ceil(Sh.pos - 1e-9) - 1));
  E.fwd.addEventListener('click', () => {
    const next = Math.floor(Sh.pos + 1e-9) + 1;
    if (learnShapeCalm()) learnShapeGoto(next); else learnShapePlay(next);
  });
  E.again.addEventListener('click', () => learnShapeGoto(0));
  E.speed.addEventListener('change', () => { L.speed = LEARN_SHAPE_SECONDS[E.speed.value] ? E.speed.value : 'normal'; if (el.speed) el.speed.value = L.speed; });
  E.bar.querySelector('#learnShapeSpaceBar').addEventListener('change', e => { if (e.target.name === 'learnShapeSpaceBar') L.set({ space: +e.target.value }); });

  // the panel: the choice "Follow" at its top, and the parts that belong to the whole shape
  const body = el.panel.querySelector('.sec-body'), intro = body.querySelector('p.note');
  E.summary = el.panel.querySelector('summary'); E.summaryWas = E.summary.textContent;
  const follow = make('fieldset', 'learn-follow', '<legend class="label">Follow</legend>' +
    '<label class="seg"><input type="radio" name="learnFollow" id="learnFollowPoint" value="point"><span>One point</span></label>' +
    '<label class="seg"><input type="radio" name="learnFollow" id="learnFollowShape" value="shape" checked><span>A whole shape</span></label>');
  follow.id = 'learnFollow';
  body.prepend(follow);
  E.follows = [...follow.querySelectorAll('input')];
  follow.addEventListener('change', e => { if (e.target.name === 'learnFollow') learnShapeFollow(e.target.value === 'shape'); });
  // the words of the note and of the helps are set by learnShapePanel: some of them follow the power and the space
  const note = make('p', 'note learn-only-shape');
  note.id = 'learnShapeIntro';
  intro.after(note);
  E.intro = note;
  const kind = make('div', 'sec-inner learn-only-shape', '<fieldset class="learn-kind" id="learnShapeKind"><legend class="label">Which shape</legend>' +
    seg('learnShapeKind', 'm', 'Mandelbrot shape') + seg('learnShapeKind', 'j', 'Julia shape') + seg('learnShapeKind', 'both', 'Both') + '</fieldset>' +
    '<div class="learn-kind-help"><p class="note"><b>Mandelbrot shape.</b> Each point of the picture is tried as the number c, the one that is added at every step. Its dot starts on that same point. (Starting every dot at the centre gives the same shapes one step later: that first step only carries a dot from the centre to its own point.)</p>' +
    '<p class="note"><b>Julia shape.</b> <span id="learnShapeHelpJ"></span></p>' +
    '<p class="note"><b>Both.</b> <span id="learnShapeHelpBoth"></span></p></div>');
  el.eqNote.after(kind);
  E.helpJ = kind.querySelector('#learnShapeHelpJ'); E.helpBoth = kind.querySelector('#learnShapeHelpBoth');
  // Each step and the choices for the dots: here with a line of help, and in the transport
  const each = make('div', 'sec-inner learn-only-shape', '<fieldset class="learn-follow" id="learnShapeEach"><legend class="label">Each step</legend>' +
    seg('learnShapeEach', 'once', 'At once') + seg('learnShapeEach', 'moves', 'Move by move') + '</fieldset>' +
    '<p class="note" id="learnShapeEachHelp"></p>' +
    '<div class="field"><label class="label" for="learnShapeDots">Dots</label><select id="learnShapeDots" class="learn-shape-sel"><option value="few">Few</option><option value="some">Some</option><option value="many">Many</option><option value="most">Very many</option></select></div>' +
    '<div class="field"><label class="label" for="learnShapeSee">Show</label><select id="learnShapeSee" class="learn-shape-sel"><option value="dots">The dots</option><option value="skin">The surface</option><option value="both">Both</option></select></div>' +
    '<div class="field"><label class="label" for="learnShapeOrbits">Orbits: the whole path of</label><select id="learnShapeOrbits" class="learn-shape-sel"><option value="few">A few dots, drawn larger</option><option value="all">Every dot</option><option value="none">No dot</option></select></div>' +
    '<label class="check"><input type="checkbox" id="learnShapeRefill" checked> <span>Add new dots as dots are thrown out</span></label>' +
    '<div class="field"><label class="label" for="learnShapeTint">Colour each dot by</label><select id="learnShapeTint" class="learn-shape-sel"><option value="dir">Which way from the centre it started</option><option value="height">How high it started</option><option value="dist">How far from the centre it started</option><option value="mix">How far from the centre and how high it started</option></select></div>' +
    '<div class="field"><label class="label" for="learnShapeLay">In 3D, lay the dots out as</label><select id="learnShapeLay" class="learn-shape-sel"><option value="grid">A full grid</option><option value="sheets">Level sheets, one above the other</option><option value="shells">Shells, one ball inside the other</option><option value="both">Sheets and shells together</option></select></div>');
  each.id = 'learnShapeEachBlock';
  kind.after(each);
  E.eachHelp = each.querySelector('#learnShapeEachHelp'); E.parts = E.bar.querySelector('#learnShapeParts');
  E.eachs = [...each.querySelectorAll('input[name=learnShapeEach]'), ...E.bar.querySelectorAll('input[name=learnShapeEachBar]')];
  E.dotSels = [each.querySelector('#learnShapeDots'), E.bar.querySelector('#learnShapeDotsBar')];
  const pickEach = e => { if (e.target.name === 'learnShapeEach' || e.target.name === 'learnShapeEachBar') learnShapeSet({ each: e.target.value }); };
  each.addEventListener('change', pickEach); E.bar.querySelector('#learnShapeEachBar').addEventListener('change', pickEach);
  for (const s of E.dotSels) s.addEventListener('change', () => learnShapeSet({ dots: s.value }));
  for (const key of ['tint', 'lay', 'see', 'orbits']) { const s = E[key] = each.querySelector('#learnShape' + key[0].toUpperCase() + key.slice(1)); s.addEventListener('change', () => learnShapeSet({ [key]: s.value })); }
  E.refill = each.querySelector('#learnShapeRefill');
  E.refill.addEventListener('change', () => learnShapeSet({ refill: E.refill.checked }));
  E.bars = {};
  for (const key of ['orbits', 'see', 'lay']) { const s = E.bars[key] = E.bar.querySelector('#learnShape' + key[0].toUpperCase() + key.slice(1) + 'Bar'); s.addEventListener('change', () => learnShapeSet({ [key]: s.value })); }
  const cBlock = make('div', 'sec-inner learn-only-shape', '<div id="learnShapeDials" class="sec-inner"></div><div class="learn-btncol" id="learnShapeCs">' +
    '<button class="btn" id="learnShapeJuliaC" type="button">Use the c of the Julia tab</button></div>');
  cBlock.id = 'learnShapeC';
  const spaceSet = el.panel.querySelector('#learnSpace');
  spaceSet.after(cBlock);
  E.cBlock = cBlock;
  E.rule = make('p', 'note learn-only-shape'); E.rule.id = 'learnShapeRule';
  cBlock.after(E.rule);
  E.notice = make('p', 'learn-notice learn-only-shape'); E.notice.id = 'learnShapeNotice';
  el.notice.after(E.notice);
  // what belongs to one point only is put away by the style sheet while the whole shape is on
  for (const n of [intro, el.panel.querySelector('#learnChecks'), el.hiddenNote, el.panel.querySelector('#learnDials'), el.panel.querySelector('#learnZero').parentNode,
    el.panel.querySelector('#learnMovesHead'), el.moves, el.note, el.notice]) n.classList.add('learn-only-point');
  el.panel.querySelector('#learnSpace1').closest('.seg').classList.add('learn-space-1');
  E.kinds = [...kind.querySelectorAll('input[name=learnShapeKind]'), ...E.bar.querySelectorAll('input[name=learnShapeKindBar]')];
  E.spaces = [...E.bar.querySelectorAll('input[name=learnShapeSpaceBar]')];
  const pickKind = e => { if (e.target.name === 'learnShapeKind' || e.target.name === 'learnShapeKindBar') learnShapeSet({ kind: e.target.value }); };
  kind.addEventListener('change', pickKind); E.bar.querySelector('#learnShapeKindBar').addEventListener('change', pickKind);
  // the c of the Julia shape: dials, the c of the Julia tab, and a few named values
  const store = {};
  ['x', 'y', 'z'].forEach((axis, i) => Object.defineProperty(store, 'c' + axis, { get: () => Sh.c[i], set: v => { Sh.c[i] = v; }, enumerable: true }));
  const pd = (key, label, when) => ({ type: 'dial', key, label, min: -2, max: 2, step: 0.01, lo: -8, hi: 8, when });
  Sh.dials = buildControls('learnShapeDials', [
    pd('cx', 'The point <span class="asis">c</span>, along x'), pd('cy', 'The point <span class="asis">c</span>, along y'),
    pd('cz', 'The point <span class="asis">c</span>, along z', () => L.space === 3),
  ], store, learnShapeNow, { idPrefix: 'learnShape-', group: 'learn' });
  const cs = cBlock.querySelector('#learnShapeCs');
  cBlock.querySelector('#learnShapeJuliaC').addEventListener('click', () => { learnShapeSet({ c: S.c.slice() }); learnVShowStage(); });
  E.named = LEARN_SHAPE_NAMED.map(v => {
    // "the rabbit (c at x −0.12, y 0.74)": the name, shown where it is true, and the value (learnShapePanel)
    const b = make('button', 'btn learn-shape-value', '<span class="learn-shape-name"></span><span></span>');
    b.type = 'button'; b.firstChild.textContent = v.name + ' '; b.lastChild.textContent = v.text;
    b.addEventListener('click', () => { learnShapeSet({ c: v.c.slice() }); learnVShowStage(); });
    cs.appendChild(b);
    return b;
  });
  learnShapePanel();
  learnShapeSync();
}

// A choice made with a control of this part: any of kind, each, dots, see, lay, refill, tint, orbits, c.
function learnShapeSet(o) {
  const Sh = LEARN_SHAPE;
  if (o.kind !== undefined && ['m', 'j', 'both'].includes(o.kind)) Sh.kind = o.kind;
  if (o.each !== undefined && ['once', 'moves'].includes(o.each) && o.each !== Sh.each) { Sh.each = o.each; Sh.endSide = false; Sh.sig3 = ''; }
  if (o.dots !== undefined && ['few', 'some', 'many', 'most'].includes(o.dots)) Sh.dots = o.dots;
  if (o.see !== undefined && ['dots', 'skin', 'both'].includes(o.see)) Sh.see = o.see;
  if (o.lay !== undefined && ['grid', 'sheets', 'shells', 'both'].includes(o.lay)) Sh.lay = o.lay;
  if (o.refill !== undefined) Sh.refill = !!o.refill;
  if (o.tint !== undefined && ['dir', 'height', 'dist', 'mix'].includes(o.tint)) Sh.tint = o.tint;
  if (o.orbits !== undefined && ['few', 'all', 'none'].includes(o.orbits)) Sh.orbits = o.orbits;
  if (o.c) Sh.c = [0, 1, 2].map(i => (isFinite(+o.c[i]) ? clamp(+o.c[i], -8, 8) + 0 : 0));
  if (!learnShapeIsOn()) return;
  learnShapeNow();
  // where a coarse picture waits for its fine one, the fine one is drawn at once
  if (Sh.rest || (Sh.raf && !Sh.playing)) { clearTimeout(Sh.rest); Sh.rest = 0; if (!Sh.drag) Sh.hot = 0; learnShapeNow(); }
}
