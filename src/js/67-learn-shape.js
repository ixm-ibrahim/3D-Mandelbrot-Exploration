// ---------- Learn, "A whole shape" (round 26): the steps taken by a whole shape, not by one point.
// The game: take every point of the big circle (all points no further than 2 from the centre; in 3D the big ball)
// and let each one take steps of z -> z^n + c. A point that lands outside is thrown out, for good. "Shape k" is
// what is left after k steps: shape 0 is the big circle, and each shape lies inside the one before.
//   Mandelbrot shape: every point of the picture is a c of its own, and its dot starts at 0.
//   Julia shape:      one c for everybody (the diamond); every point of the picture is a place to start from.
// This file owns the choice "Follow" in the Learn panel, the transport under the stage, the layout of one or two
// pictures, the 2D pictures (Canvas 2D), everything drawn over the pictures, the words, and the test handle
// LEARN.shape. The 3D picture is drawn by learnShape3d (68-learn-shape3d.js) through make() and draw(o); without
// that file the 2D pictures work fully and 3D shows a plain note. 66-learn-view.js hands over to this file while
// LEARN.follow === 'shape': learnVPaint -> learnShapePaint, learnVDraw -> learnShapeDraw, the wheel ->
// learnShapeWheel, and learnVSetOn, learnVDefaults and learnInit call learnShapeSync, learnShapeDefaults and
// learnShapeInit. With Follow = One point nothing here draws or listens.
// (Round 29.) "Each step: Move by move" lays dots over the pictures and plays the moves inside each step on them;
// "At once" is the behaviour described here, unchanged. See the part "Each step: Move by move" below.
//
// The 2D picture. For every sample of a pane the step at which that point is thrown out is worked out once and
// kept (learnShapeMap: 0 = it starts outside the big circle, N + 1 = it is still in after N steps), together with
// the lowest such number close by (learnShapeEdge, for the outlines). A frame is then one pass that turns the kept
// numbers into colours for the slider's position, so the slider and Play cost a few milliseconds whatever the
// rule. Only a new c, power, modifier, zoom or size works the numbers out again: one sample to a CSS pixel each way
// while something is being dragged, two once it rests (the picture is then scaled down, which smooths its edge).
// The rule is the flat one: the complex power of x + iy, by plain multiplication for the whole powers 2 to 8 and in
// polar form otherwise (exactly learnFlatRule), with the modifiers |x|, |y| and flip y applied first, and the plain
// equation z^n + c from the start value 0 whatever the equation field says.
const LEARN_SHAPE_N = 16;                          // the last step the slider reaches
// one step at each speed: seconds on the move, then seconds standing still on the whole step
const LEARN_SHAPE_SECONDS = { slow: [2.2, 0.6], normal: [1.1, 0.35], fast: [0.55, 0.15] };
// A play that starts at step 0 first stands still on it for this long, so that the opening sentence can be read
// (before, the first play of a visit left it on the page for a twentieth of a second).
const LEARN_SHAPE_OPENING = { slow: 2.4, normal: 1.5, fast: 0.9 };
// The opacities handed to the 3D picture: the skin of the shape on show, the ghost of the shape before, and the
// skin of the part a step is taking away while it shows in the warning colour (thin glass, so that the body that
// stays is seen inside it; at full strength it hid that body and the whole picture turned red at every step).
// deep: between these two steps the near side of the body goes from glass to solid (see learnShapeLevels).
const LEARN_SHAPE_GLASS = { solid: 1, ghost: 0.22, peel: 0.42, deep: [5, 11] };
// How the 3D picture opens: looked at from higher up than the one-point picture of space (LEARN_V_VIEWS.s3, pitch
// 0.4), from where a shape that lies along the flat plane was seen nearly edge on.
const LEARN_SHAPE_VIEW3 = { yaw: -0.62, pitch: 0.9, zoom: 1 };
// A bite thinner than this many pixels of the picture, on the average along the shape's outline, cannot be seen to
// go: the sentence then says so, and that zooming in shows it again. (At 1400 x 950 the Mandelbrot shape's bites
// measure 1.25, 0.91 and 0.60 pixels at steps 8, 9 and 10, and step 9 is where the eye stops seeing them go.)
const LEARN_SHAPE_THIN = 1;
// The names are true of the plain power 2 only, and are shown only then. The value is written the way the dials
// name it (along x, along y).
const LEARN_SHAPE_NAMED = [
  { c: [-1, 0, 0], text: 'c at x −1, y 0', name: 'the basilica' },
  { c: [-0.1226, 0.7449, 0], text: 'c at x −0.12, y 0.74', name: 'the rabbit' },
  { c: [0, 1, 0], text: 'c at x 0, y 1', name: 'a bare twig' },
  { c: [0, 0, 0], text: 'c at x 0, y 0', name: 'a plain disc' },
];
const LEARN_SHAPE_MISSING = 'The 3D picture is missing from this copy of the page.';
const LEARN_SHAPE = {
  kind: 'm',                     // 'm' Mandelbrot shape | 'j' Julia shape | 'both'
  each: 'moves',                 // (round 29) 'once': a step shows only what it leaves | 'moves': the moves inside it, played on dots
  dots: 'some',                  // 'few' | 'some' | 'many': how close the dots lie (LEARN_SHAPE_SPACING)
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
  three: null, threeTried: false, threeNote: '', note: '', last3: null, warned: false,
  gone: '',                      // the pictures on show of which nothing is left at the step the slider stands on: '', 'm', 'j' or 'mj'
  thin: '',                      // thin[k] === '1': the bite of step k + 1 is too fine to see in the pictures as they stand (learnShapeDraw)
  zero: { sig: '', out: false }, // kept answer of learnShapeZeroOut
  first: { sig: '', stays: false, sigJ: '', whole: true },   // kept answers of learnShapeZeroStays and learnShapeStartWhole
  above: {},                     // above[kind]: what learnShapeAbove keeps of a 3D shape seen from straight above
  place: null,                   // where One point stood when Follow went to the whole shape (learnShapeFollow)
  hot: 0, touched: 0, seen: '', quality: 'still',
  ptr: new Map(), drag: null, pinch: null,
  el: {}, dials: null, sig: '', cols: null, cut: { sig: '', holds: false },
  // what the last redraw took, in ms, for the notes: all of it; the part spent working numbers out again (0 when the
  // kept ones still fitted) and the part spent colouring and laying down the flat pictures; the 3D module's own time.
  // mapLast: the last time numbers were worked out, with how many samples and how many to a CSS pixel.
  // (round 29) dots: the part of a redraw spent on the dots of Move by move
  ms: { frame: 0, map: 0, fill: 0, three: 0, mapLast: 0, mapSamples: 0, mapDens: 0, dots: 0 },
};
const learnShapeEase = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const learnShapeIsOn = () => LEARN.on && LEARN.follow === 'shape';
const learnShapeCalm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const learnShapeKinds = () => (LEARN_SHAPE.kind === 'both' ? ['m', 'j'] : [LEARN_SHAPE.kind]);

// ---------- the numbers
// The step at which the 2D point p is thrown out, the plain way: the modifiers, the power, add c, and the
// question "further than 2 from the centre?" after every step. maxK + 1: still in after maxK steps.
// (The question is asked as x² + y² > 4, here and in learnShapeMap: for a point that lies on the big circle to the
// last digit, such as (1.2, 1.6), a square root can round to exactly 2 and give the other answer.)
// A whole power from 2 to 8 is worked by multiplying, the way the picture's own arithmetic works it (learnShapeMap),
// and only another power in the polar form of learnFlatRule. Before, every power went through the polar form, and
// a point that lies on a skin to the last digit could get another answer here than in the picture: the tip c = −2
// of the Mandelbrot shape goes 0, −2, 2, 2, 2, ... and stays exactly on the big circle, but the polar form's 2² is
// a hair more than 4, which threw it out at step 15.
function learnShapeOut2(p, kind, c, maxK) {
  const n = S.n, abs = S.abs, flip = S.flip, K = maxK === undefined ? LEARN_SHAPE_N : maxK, jul = kind === 'j';
  const px = +p[0], py = +p[1], cc = jul ? [+(c || LEARN_SHAPE.c)[0] || 0, +(c || LEARN_SHAPE.c)[1] || 0] : [px, py];
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0;
  if (!(px * px + py * py <= 4)) return 0;
  let z = jul ? [px, py, 0] : [0, 0, 0];
  for (let k = 1; k <= K; k++) {
    const x = abs[0] ? Math.abs(z[0]) : z[0], y = (abs[1] ? Math.abs(z[1]) : z[1]) * (flip[0] ? -1 : 1);
    let w;
    if (mul === 2) w = [x * x - y * y, 2 * x * y];
    else if (mul) { let a = x, b = y; for (let m = 1; m < mul; m++) { const t = a * x - b * y; b = a * y + b * x; a = t; } w = [a, b]; }
    else w = learnFlatRule([x, y, 0], n);
    z = [w[0] + cc[0], w[1] + cc[1], 0];
    if (!(z[0] * z[0] + z[1] * z[1] <= 4)) return k;
  }
  return K + 1;
}
// The same for a whole block of the page at once, as fast as it will go: sample (i, j) is the point
// (x0 + i * dx, y0 - j * dy). This is the arithmetic the picture is drawn from, and mask2 calls it too.
function learnShapeMap(kind, c, n, abs, flip, x0, y0, dx, dy, w, h, maxK, out) {
  const ax = !!abs[0], ay = !!abs[1], fy = !!flip[0], jul = kind === 'j', jx = +c[0] || 0, jy = +c[1] || 0;
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0;      // 0: the polar form
  let o = 0;
  for (let j = 0; j < h; j++) {
    const py = y0 - j * dy;
    for (let i = 0; i < w; i++, o++) {
      const px = x0 + i * dx;
      if (!(px * px + py * py <= 4)) { out[o] = 0; continue; }
      let x = 0, y = 0, cx = px, cy = py, k = 1;
      if (jul) { x = px; y = py; cx = jx; cy = jy; }
      for (; k <= maxK; k++) {
        if (ax) x = Math.abs(x);
        if (ay) y = Math.abs(y);       // (Math.abs, not "if below 0": a zero keeps the sign the lab's own rule gives it,
        if (fy) y = -y;                //  which decides the side of the cut when the power is not a whole number)
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
        if (!(x * x + y * y <= 4)) break;
      }
      out[o] = k;
    }
  }
  return out;
}
// For the outlines: the lowest number within r samples of each one (a square of side 2r + 1; past the block's
// edge the edge is repeated, so the edge of a zoomed picture is not taken for an outline).
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
// mask2(kind, size, half, maxK): the numbers of learnShapeMap on the square |x|, |y| <= half, row 0 at the top.
// size points to a side with the outer ones ON the edge of the square, as learnShape3d's slice() has them
// (opt.centres: true puts them at the centres of size cells instead, as slice() does with the same option).
function learnShapeMask2(kind, size, half, maxK, opt) {
  size = clamp(Math.round(+size) || 256, 2, 4096);
  half = isFinite(+half) && +half > 0 ? +half : 2;
  maxK = clamp(Math.round(maxK === undefined ? LEARN_SHAPE_N : +maxK) || 0, 0, 254);
  const centres = !!(opt && opt.centres), d = centres ? 2 * half / size : 2 * half / (size - 1), h0 = centres ? half - d / 2 : half;
  return learnShapeMap(kind === 'j' ? 'j' : 'm', LEARN_SHAPE.c, S.n, S.abs, S.flip, -h0, h0, d, d, size, size, maxK, new Uint8Array(size * size));
}
// Does the first step take a dot at 0 to its own c (so that the first step of a Mandelbrot shape throws nothing
// out)? On the page: the flat rule with a power above 0. In space: asked of the approach's own rule.
// In space that is not enough: an approach may also take c itself somewhere else before it is added ("Quaternions,
// 4D (slices)" with its dial w off 0 shows a slice of 4D whose points lie further out than the picture's, so the
// first step already throws out a shell). So the 3D rule itself (learnShape3d.out) is asked as well, about points
// just inside the surface of the big ball in 26 directions: each has to be still in after one step.
function learnShapeRim() {
  const out = [];
  for (const x of [-1, 0, 1]) for (const y of [-1, 0, 1]) for (const z of [-1, 0, 1]) { const l = Math.hypot(x, y, z); if (l) out.push([x, y, z].map(v => v / l * 2 * (1 - 1e-9))); }
  return out;
}
function learnShapeZeroStays() {
  if (LEARN.space !== 3) return S.n > 0;
  const F = LEARN_SHAPE.first, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip].join('|');
  if (F.sig === sig) return F.stays;
  F.sig = sig; F.stays = false;
  try {
    const q = S.param[a.id], car = typeof CARRY !== 'undefined' && CARRY[a.id] ? CARRY[a.id] : null, z = [0, 0, 0], c = [0.3, 0.2, 0.1];
    const w = car ? car.pw(car.step(car.start(q), z, c, q), z, S.n) : MATH[a.id](z, S.n, q, c);
    F.stays = learnVFinite(w) && len(w) < 1e-12
      && (typeof learnShape3d === 'undefined' || !learnShape3d || typeof learnShape3d.out !== 'function' || learnShapeRim().every(p => learnShape3d.out(p, 'm', p, 1) === 2));
  } catch (err) { F.stays = false; }
  return F.stays;
}
// Does a Julia shape begin as the whole big circle (the whole big ball)? On the page it does: every point of the
// picture is its own place to start from. In space the 3D rule is asked about the same points just inside the
// surface: each has to count as inside before the first step.
function learnShapeStartWhole() {
  if (LEARN.space !== 3 || typeof learnShape3d === 'undefined' || !learnShape3d || typeof learnShape3d.out !== 'function') return true;
  const Sh = LEARN_SHAPE, F = Sh.first, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, Sh.c].join('|');
  if (F.sigJ === sig) return F.whole;
  F.sigJ = sig; F.whole = true;
  try { F.whole = learnShapeRim().every(p => learnShape3d.out(p, 'j', Sh.c, 0) === 1); } catch (err) { F.whole = true; }
  return F.whole;
}
// In space: is every point of a Mandelbrot shape thrown out by the very first step? It is when that step takes the
// dot at 0 further than 4 from the centre (or to no number at all) before c is added: no c of the big ball brings
// that back inside. So it is with a negative power. Asked of the approach's own rule for a handful of c, and of
// learnShape3d.out, which has to agree. (A 3D picture is not read back, so this is the one case in space in which
// the words can say for certain that nothing is left.)
function learnShapeZeroOut() {
  const Sh = LEARN_SHAPE, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip].join('|');
  if (Sh.zero.sig === sig) return Sh.zero.out;
  Sh.zero.sig = sig; Sh.zero.out = false;
  if (typeof learnShape3d === 'undefined' || !learnShape3d || typeof learnShape3d.out !== 'function') return false;
  try {
    const q = S.param[a.id], car = typeof CARRY !== 'undefined' && CARRY[a.id] ? CARRY[a.id] : null, z = [0, 0, 0];
    const cs = [[0, 0, 0], [1.9, 0, 0], [-1.9, 0, 0], [0, 1.9, 0], [0, -1.9, 0], [0, 0, 1.9], [0, 0, -1.9], [0.3, 0.2, 0.1], [-0.7, 0.9, -0.5], [1, -1, 1]];
    Sh.zero.out = cs.every(c => {
      const w = car ? car.pw(car.step(car.start(q), z, c, q), z, S.n) : MATH[a.id](z, S.n, q, c);
      return (!learnVFinite(w) || len(w) > 4) && learnShape3d.out(c, 'm', c, 1) === 1;
    });
  } catch (err) { Sh.zero.out = false; }
  return Sh.zero.out;
}
// Is the 3D shape, cut at z = 0, the 2D shape of the same step? True of an approach that keeps the flat picture
// when c lies in the flat plane. It is not taken on trust: the 3D rule (learnShape3d.out) is asked about a grid of
// points of the flat plane and compared with learnShapeOut2, each time the settings change.
function learnShapeCutHolds() {
  const Sh = LEARN_SHAPE, a = ap(), sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, Sh.kind, Sh.c].join('|');
  if (Sh.cut.sig === sig) return Sh.cut.holds;
  Sh.cut.sig = sig; Sh.cut.holds = false;
  if (typeof learnShape3d === 'undefined' || !learnShape3d || typeof learnShape3d.out !== 'function') return false;
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
    Sh.cut.holds = seen > 0 && bad <= 1;      // (one point within a hair of a skin may fall either way)
  } catch (err) { Sh.cut.holds = false; }
  return Sh.cut.holds;
}

// What the words need to know of a block of numbers (a flat picture's own, or a 3D shape seen from straight above):
// left[k], how many of its points are still in after k steps, and thick[k], how thick the bite of step k + 1 is on
// the average along the outline of shape k, counted in points of the block. That is the points the step throws
// out, over the points of shape k that lie within `band` points of its outline (edge: learnShapeEdge with that
// reach), times the band. 0: the step takes nothing that the block shows.
function learnShapeTally(map, edge, n, N, band) {
  const hist = new Uint32Array(N + 2), rim = new Int32Array(N + 3), left = new Uint32Array(N + 2), thick = new Float64Array(N + 1);
  for (let o = 0; o < n; o++) { const m = map[o], e = edge[o]; hist[m]++; if (e < m) { rim[e]++; rim[m]--; } }
  for (let v = N, more = hist[N + 1]; v >= 0; v--) { left[v] = more; more += hist[v]; }
  for (let k = 0, r = 0; k < N; k++) { r += rim[k]; const bite = left[k] - left[k + 1]; thick[k] = bite > 0 ? (r > 0 ? bite / r * band : Infinity) : 0; }
  return { left, thick };
}
// A 3D picture is not read back. What the words need to know of a 3D shape is asked of the 3D module's columns():
// the shape seen from straight above, without glass (for every upright line through the big ball, the last step at
// which a point of it is still in), 192 lines each way with 192 points on each, from the same program the picture
// is drawn with. Tallied as a flat picture is: how many lines still meet shape k (none: nothing is left to see), and
// how thick the bite of step k + 1 is along the outline, here in units of the picture. Worked out once for a rule,
// a kind and a c, for the resting picture or a moment into a play, not while a dial or the picture is being dragged
// (it costs the graphics card about what one coarse picture does). null while it is not known.
const LEARN_SHAPE_ABOVE = 192;
function learnShapeAbove(kind, quality) {
  const Sh = LEARN_SHAPE, T = Sh.three, N = LEARN_SHAPE_N, a = ap(), now = performance.now();
  const sig = [a.id, JSON.stringify(S.param[a.id]), S.n, S.abs, S.flip, kind === 'j' ? Sh.c : ''].join('|');
  const A = Sh.above[kind] || (Sh.above[kind] = { sig: '', at: 0, done: false, data: null });
  if (A.sig !== sig) { A.sig = sig; A.at = now; A.done = false; A.data = null; }
  if (!A.done && T && !Sh.drag && !Sh.pinch && (quality === 'still' || (Sh.playing && now - A.at >= 150))) {
    A.done = true;
    try {
      const size = LEARN_SHAPE_ABOVE, n = size * size, map = typeof T.columns === 'function' ? T.columns(kind, Sh.c, { size, half: 2, stops: size, maxK: N }) : null;
      if (map) { A.data = learnShapeTally(map, learnShapeEdge(map, size, size, 1, new Uint8Array(n), new Uint8Array(n)), n, N, 1); A.data.unit = 4 / (size - 1); A.data.ms = performance.now() - now; }
    } catch (err) { A.data = null; }
  }
  return A.data;
}

// ---------- (round 29) Each step: Move by move. The moves inside each step, played on dots.
// The picture of a whole shape is a picture of STARTING PLACES: a point is coloured when the dot that starts there
// is still in. The moves of a step happen to where the dots are NOW, which that picture never shows. So with
// "Each step: Move by move" an even grid of dots is laid over the picture, one dot for each starting place, and
// one step (from shape k to shape k + 1) is played on them in parts. The slider's fraction inside a step runs
// through the parts in this order (learnShapePart):
//   out     the dots go from their starting places to where k steps have carried them
//   moves   the moves of the rule, one after another: the chain learnPlan gives for the space on show (the flat rule
//           on the 2D page; in 3D the approach chosen in the lab, with its dials, the power and the modifiers)
//   gone    the dots that have landed further than 2 from the centre light up in the warning colour and fade,
//           while the bite lights up in the picture of starting places as it does with "At once"
//   home    the dots that are left go back to their starting places: those places are shape k + 1
// A dot's places at whole steps are the lab's own rule to the last digit: on the 2D page the arithmetic of
// learnShapeOut2 (which is the picture's own, learnShapeMap), in 3D learnShape3d.orbit (the arithmetic of
// learnShape3d.out). The moves of step k + 1 start from that exact place after k steps, and when the last move is
// done the dot stands on the exact place after k + 1 steps (the chain of moves ends there to within rounding;
// learnShapeChain keeps the largest difference it meets, for the tests).
// one step at each speed: seconds on the parts, then seconds standing still on the whole step (about 5 s at Normal)
const LEARN_SHAPE_MOVE_SECONDS = { slow: [9.2, 0.8], normal: [4.6, 0.4], fast: [2.3, 0.2] };
// how far apart the dots lie, on the 2D page and in space
const LEARN_SHAPE_SPACING = { 2: { few: 0.25, some: 0.16, many: 0.1 }, 3: { few: 0.5, some: 0.4, many: 0.3 } };
// How strongly the picture of starting places shows while the dots are away from home (1: as at a whole step), on
// the 2D page and in space (there it is the opacity of the glass picture's canvas), and while the bite is lit.
const LEARN_SHAPE_QUIET = { 2: 0.3, 3: 0.34, bite: 0.72 };
const LEARN_SHAPE_MARKED = 6;      // how many dots are drawn larger, to be followed
const learnShapeMovesOn = () => LEARN_SHAPE.each === 'moves' && learnShapeMoves().moves.length > 0;

// The places of one 2D dot: learnShapeOut2 with the places kept (the same arithmetic, line for line).
// -> { out, pts, c, carry: null }: pts[j] is where the dot is after j steps, for j = 0 .. min(out, maxK).
function learnShapeOrbit2(p, kind, c, maxK) {
  const n = S.n, abs = S.abs, flip = S.flip, K = maxK === undefined ? LEARN_SHAPE_N : maxK, jul = kind === 'j';
  const px = +p[0], py = +p[1], cc = jul ? [+(c || LEARN_SHAPE.c)[0] || 0, +(c || LEARN_SHAPE.c)[1] || 0, 0] : [px, py, 0];
  const mul = Number.isInteger(n) && n >= 2 && n <= 8 ? n : 0, res = { out: 0, pts: [], c: cc, carry: null };
  if (!(px * px + py * py <= 4)) return res;
  let z = jul ? [px, py, 0] : [0, 0, 0];
  res.pts.push(z);
  for (let k = 1; k <= K; k++) {
    const x = abs[0] ? Math.abs(z[0]) : z[0], y = (abs[1] ? Math.abs(z[1]) : z[1]) * (flip[0] ? -1 : 1);
    let w;
    if (mul === 2) w = [x * x - y * y, 2 * x * y];
    else if (mul) { let a = x, b = y; for (let m = 1; m < mul; m++) { const t = a * x - b * y; b = a * y + b * x; a = t; } w = [a, b]; }
    else w = learnFlatRule([x, y, 0], n);
    z = [w[0] + cc[0], w[1] + cc[1], 0];
    res.pts.push(z);
    if (!(z[0] * z[0] + z[1] * z[1] <= 4)) { res.out = k; return res; }
  }
  res.out = K + 1;
  return res;
}
// The moves of one step for the space on show, as learnPlan gives them. One chain serves every dot: a move works
// from the dot it is given and nothing else, and the last move, the slide, is made with each dot's own c
// (learnShapeMoveAt). The two entries whose orbit carries something are the exception (learnShapeOwnMoves).
function learnShapeMoves() {
  const L = LEARN, Sh = LEARN_SHAPE, a = ap(), three = L.space === 3;
  const sig = [three ? 3 : 2, S.n, S.abs, S.flip, three ? a.id + JSON.stringify(S.param[a.id]) : ''].join('|');
  if (Sh.mv.sig === sig) return Sh.mv;
  let moves = [];
  try {
    const plan = typeof learnPlan === 'function' ? learnPlan({ space: three ? 3 : 2, id: a.id, params: S.param[a.id], n: S.n, c: [0, 0, 0], abs: S.abs.slice(), flip: S.flip.slice() }) : null;
    if (plan && Array.isArray(plan.moves)) moves = plan.moves;
  } catch (err) { moves = []; }
  // (The last move is "Add c" in One point; here it is the Slide, the word the sentences use. The turn that a dial of
  // the two Mandelbulbs adds is named "Add the turn" here, as the like move of the sphere inversions is.)
  const names = moves.map(m => (m.key === 'shift' ? 'Slide' : m.name === 'Add the phase' ? 'Add the turn' : m.name || 'Move'));
  return (Sh.mv = { sig, moves, names, car: three && typeof CARRY !== 'undefined' && !!CARRY[a.id],
    chips: ['Dots now'].concat(names, ['Thrown out', 'Back home']), keys: ['out'].concat(moves.map(() => 'move'), ['gone', 'home']) });
}
// Which part of a step the fraction u (0 .. 1) of the slider stands in: its number i of n, its key, for a move its
// number j, and how far through the part, t. At the joint of two parts the picture is the same; a play that was
// asked to stop there stands at the end of the part it played (Sh.endSide), anything else at the start of the next.
function learnShapePart(u) {
  const Sh = LEARN_SHAPE, M = learnShapeMoves(), n = M.keys.length, x = clamp(u, 0, 1) * n;
  let i = Math.min(n - 1, Math.floor(x + 1e-9)), t = clamp(x - i, 0, 1);
  if (t < 1e-9 && i > 0 && Sh.endSide) { i -= 1; t = 1; }
  return { i, n, t, key: M.keys[i], j: i - 1, name: M.chips[i] };
}
// The dots of one picture: an even grid of starting places over the big circle (in space the big ball), and for
// each dot the places its steps carry it to. The grid is shifted off the centre, by half a gap along x and a
// quarter along y on the page (so no two dots are mirror twins through the centre, which squaring would lay on
// top of each other), and by half, half and a quarter in space (so no dot sits on an axis or in the flat plane,
// where many of the 3D rules have a special case).
// dot = { p, out, pts, c, carry, col, big }: p the starting place; out the step at which it is thrown out
// (N + 1: still in after N); pts, c, carry as learnShapeOrbit2 / learnShape3d.orbit give them; col its colour for
// good; big: one of the handful drawn larger.
function learnShapeDots(kind) {
  const L = LEARN, Sh = LEARN_SHAPE, three = L.space === 3, a = ap(), N = LEARN_SHAPE_N, dark = learnVDark();
  const sig = [three ? 3 : 2, kind, Sh.dots, S.n, S.abs, S.flip, three ? a.id + JSON.stringify(S.param[a.id]) : '', kind === 'j' ? (three ? Sh.c : Sh.c.slice(0, 2)) : '', dark].join('|');
  let D = Sh.D[kind];
  if (D && D.sig === sig) return D;
  const gaps = LEARN_SHAPE_SPACING[three ? 3 : 2], h = gaps[Sh.dots] || gaps.some, dots = [];
  const orbit3 = three && typeof learnShape3d !== 'undefined' && learnShape3d && typeof learnShape3d.orbit === 'function' ? learnShape3d.orbit : null;
  for (const p of learnVGridPoints(three ? 3 : 2, h)) {      // (the layout is One point's "A grid of points", closer)
    let o = null;
    try { o = three ? (orbit3 ? orbit3(p, kind, Sh.c, N) : null) : learnShapeOrbit2(p, kind, Sh.c, N); } catch (err) { o = null; }
    if (o && o.pts.length) dots.push({ p, out: o.out, pts: o.pts, c: o.c, carry: o.carry, col: learnVDotColour(p, three ? 3 : 2, dark), big: false });
  }
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
  return (Sh.D[kind] = { sig, kind, three, h, dots, big: pick, chain: null });
}
// The moves of one step for one dot of an entry whose orbit carries something ("Along once, then one plane",
// "Pulled plane"): there a step depends on what the dot's own orbit carries when the step begins, and on its own c,
// so each dot gets the chain learnPlan gives for exactly that. It has the same moves as everybody's; should it ever
// have fewer or more (the rule's length depending on the direction for one dot and not for another), it is fitted
// to the same number of parts: a dot with fewer moves waits, a dot with more makes the first ones in one part.
function learnShapeOwnMoves(d, k, m) {
  const a = ap();
  let mv = [];
  try { mv = learnPlan({ space: 3, id: a.id, params: S.param[a.id], n: S.n, c: d.c.slice(), abs: S.abs.slice(), flip: S.flip.slice(), carry: d.carry ? d.carry[k] : undefined }).moves; } catch (err) { mv = []; }
  if (mv.length === m) return mv;
  const stay = { key: 'stay', at: v => [v[0], v[1], v[2]] };
  if (!mv.length) return new Array(m).fill(stay);
  if (mv.length < m) { const out = mv.slice(0, -1); while (out.length < m - 1) out.push(stay); out.push(mv[mv.length - 1]); return out; }
  const head = mv.slice(0, mv.length - m + 1), q = head.length;
  const first = { key: 'own', at: (v, t) => { let x = v; for (let i = 0; i < q; i++) { const u = clamp(t * q - i, 0, 1); if (u <= 0) break; x = head[i].at(x, u); } return x; } };
  return [first].concat(mv.slice(mv.length - m + 1));
}
// Where the dot d is after the fraction t of the move j, coming from v. own: its own chain (see above) or null.
function learnShapeMoveAt(M, own, d, j, v, t) {
  let p = null;
  try {
    if (own) p = own[j].at(v, t);
    else if (M.moves[j].key === 'shift') p = [v[0] + t * d.c[0], v[1] + t * d.c[1], v[2] + t * d.c[2]];      // the slide: by the dot's own c
    else p = M.moves[j].at(v, t);
  } catch (err) { p = null; }
  return p && isFinite(p[0]) && isFinite(p[1]) && isFinite(p[2]) ? p : v;
}
// Step k + 1 of one picture, for every dot that is still in after k steps: pos[i] = where the dot stands at the
// joints of the step (pos[i][0] after k steps, pos[i][j + 1] after the move j; the last one is the exact place
// after k + 1 steps). raw[i]: where the chain of moves itself ends, before that. gap: the largest difference
// between the two over all dots, as a share of the place's own distance from the centre (or of 1 when that is
// smaller). moved[0]: does the part "out" move any dot; moved[j + 1]: does the move j; moved[m + 1]: "home".
// centre: every dot stands at the centre when the step begins. on, thrown: how many dots take the step, and how
// many of them it throws out.
function learnShapeChain(kind, k) {
  const D = learnShapeDots(kind), M = learnShapeMoves();
  if (D.chain && D.chain.k === k && D.chain.M === M) return D.chain;
  const m = M.moves.length, n = D.dots.length;
  const ch = { k, M, m, kind, pos: new Array(n).fill(null), raw: new Array(n).fill(null), own: M.car ? new Array(n).fill(null) : null, list: [], on: 0, thrown: 0, gap: 0, moved: new Array(m + 2).fill(false), centre: true };
  if (k < LEARN_SHAPE_N) D.dots.forEach((d, i) => {
    if (!(d.out > k) || !d.pts[k + 1]) return;
    ch.on++; ch.list.push(i);
    if (d.out === k + 1) ch.thrown++;
    const own = M.car ? (ch.own[i] = learnShapeOwnMoves(d, k, m)) : null, v = [d.pts[k]], truth = d.pts[k + 1];
    for (let j = 0; j < m; j++) v.push(learnShapeMoveAt(M, own, d, j, v[j], 1));
    const g = len(sub(v[m], truth)) / Math.max(1, len(truth));
    ch.gap = g <= ch.gap ? ch.gap : g === g ? g : Infinity;
    ch.raw[i] = v[m]; v[m] = truth; ch.pos[i] = v;
    if (len(sub(v[0], d.p)) > 1e-9) ch.moved[0] = true;
    for (let j = 0; j < m; j++) if (len(sub(v[j + 1], v[j])) > 1e-9) ch.moved[j + 1] = true;
    if (d.out > k + 1 && len(sub(truth, d.p)) > 1e-9) ch.moved[m + 1] = true;
    if (len(v[0]) > 1e-12) ch.centre = false;
  });
  return (D.chain = ch);
}
// Where the dot i stands in the part ph of the step the chain ch belongs to, at the eased fraction te of the part.
function learnShapeDotAt(D, ch, i, ph, te) {
  const d = D.dots[i], v = ch.pos[i], p = d.p, mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  if (ph.key === 'out') return te >= 1 ? v[0] : te <= 0 ? p : mix(p, v[0], te);
  if (ph.key === 'move') return te >= 1 ? v[ph.j + 1] : te <= 0 ? v[ph.j] : learnShapeMoveAt(ch.M, ch.own ? ch.own[i] : null, d, ph.j, v[ph.j], te);
  if (ph.key === 'gone') return v[ch.m];
  return te >= 1 ? p : te <= 0 ? v[ch.m] : mix(v[ch.m], p, te);
}
const learnShapeGlide = t => t * t * (3 - 2 * t);      // a part starts and ends gently, by hand as well as in a play
// The dots of one picture, drawn over it. to(v) -> [x, y, depth] places a point of the picture's space on the canvas
// (in space: learnShape3d.proj, depth growing towards the eye); s: pixels to a unit. ph: the part being played, or
// null at a whole step, where the dots that are still in sit at home.
function learnShapeDotsDraw(g, P, to, s, k, ph, three) {
  const Sh = LEARN_SHAPE, C = LEARN.col, D = learnShapeDots(P.kind), dots = D.dots, t0 = performance.now(), e = learnShapeEase;
  const away = !!ph && k < LEARN_SHAPE_N, ch = away ? learnShapeChain(P.kind, k) : null, te = away ? learnShapeGlide(ph.t) : 0;
  const gap = D.h * s, r = three ? clamp(0.075 * gap, 1.6, 3) : clamp(0.22 * gap, 1.2, 3.4), rim = r >= 1.6, R = r * 1.55 + 1.3;
  const inPane = q => q[0] > P.x - 12 && q[0] < P.x + P.w + 12 && q[1] > P.y - 12 && q[1] < P.y + P.h + 12;
  const circle = (x, y, rad) => { g.beginPath(); g.arc(x, y, rad, 0, 2 * PI); };
  const show = [];
  for (let i = 0; i < dots.length; i++) {
    const d = dots[i];
    if (!(d.out > k)) continue;                                    // thrown out before: no longer on show
    const going = away && d.out === k + 1;                         // the step under way throws it out
    if (going && ph.key === 'home') continue;
    if (away && !ch.pos[i]) continue;
    const q = to(away ? learnShapeDotAt(D, ch, i, ph, te) : d.p);
    if (inPane(q)) show.push({ i, x: q[0], y: q[1], z: q[2] || 0, going });
  }
  if (three) show.sort((a, b) => a.z - b.z);                       // the far ones first
  // faint marks at the starting places while the dots are away: they come up as the dots leave and go as they return
  if (away) {
    const al = (ph.key === 'out' ? e(0, 0.5, ph.t) : ph.key === 'home' ? 1 - e(0.5, 1, ph.t) : 1) * (three ? 0.4 : 0.5), mr = Math.max(0.9, r * 0.42);
    if (al > 0.01) {
      g.beginPath();
      for (let i = 0; i < dots.length; i++) {
        const d = dots[i];
        if (!(d.out > k) || (ph.key === 'home' && d.out === k + 1)) continue;
        const q = to(d.p);
        if (inPane(q)) { g.moveTo(q[0] + mr, q[1]); g.arc(q[0], q[1], mr, 0, 2 * PI); }
      }
      g.fillStyle = C.ink2; g.globalAlpha = al; g.fill(); g.globalAlpha = 1;
      for (const i of D.big) {
        const d = dots[i];
        if (!(d.out > k) || (ph.key === 'home' && d.out === k + 1)) continue;
        const q = to(d.p);
        if (!inPane(q)) continue;
        circle(q[0], q[1], R + 1); g.strokeStyle = d.col; g.lineWidth = 1.5; g.globalAlpha = Math.min(1, al * 1.8); g.stroke(); g.globalAlpha = 1;
      }
    }
  }
  // the dots; the ones the step throws out light up in the warning colour, swell and fade
  const lit = away && ph.key === 'gone' ? e(0, 0.18, ph.t) : 0, fade = away && ph.key === 'gone' ? 1 - e(0.55, 1, ph.t) : 1;
  const dotOf = (sh, big) => {
    const d = dots[sh.i], f = three ? clamp((sh.z + 2) / 4, 0, 1) : 1;
    let rad = (big ? R : r) * (three ? 0.72 + 0.56 * f : 1), al = three ? 0.6 + 0.4 * f : 1, col = d.col;
    if (sh.going && ph.key === 'gone') { if (lit > 0.3) col = C.bad; rad *= 1 + (r < 1.7 ? 0.4 : 0.7) * lit; al *= fade; }
    if (al < 0.02) return;
    g.globalAlpha = al;
    if (big) {
      circle(sh.x, sh.y, rad + 2.6); g.fillStyle = C.stage; g.fill();
      circle(sh.x, sh.y, rad + 1.5); g.strokeStyle = C.ink; g.lineWidth = 1.4; g.stroke();
    } else if (rim) { circle(sh.x, sh.y, rad + 0.9); g.fillStyle = C.stage; g.fill(); }
    circle(sh.x, sh.y, rad); g.fillStyle = col; g.fill();
  };
  for (const sh of show) if (!dots[sh.i].big) dotOf(sh, false);
  g.globalAlpha = 1;
  // the handful to follow: the way each has come in this part as a line, then the dot itself, larger and ringed
  const bigs = show.filter(sh => dots[sh.i].big);
  if (away && ph.key !== 'gone') {
    for (const sh of bigs) {
      const d = dots[sh.i], v = ch.pos[sh.i], path = [];
      if (ph.key === 'move') { const n = 16; for (let a = 0; a <= n; a++) path.push(to(a === 0 ? v[ph.j] : learnShapeMoveAt(ch.M, ch.own ? ch.own[sh.i] : null, d, ph.j, v[ph.j], te * a / n))); }
      else path.push(to(ph.key === 'out' ? d.p : v[ch.m]), [sh.x, sh.y]);
      if (Math.hypot(path[path.length - 1][0] - path[0][0], path[path.length - 1][1] - path[0][1]) < 1 && path.length < 3) continue;
      g.beginPath(); path.forEach((q, a) => { if (a) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); });
      g.lineJoin = g.lineCap = 'round';
      g.strokeStyle = C.stage; g.lineWidth = 4; g.globalAlpha = 0.7; g.stroke();
      g.strokeStyle = d.col; g.lineWidth = 1.8; g.globalAlpha = 1; g.stroke();
    }
  }
  for (const sh of bigs) dotOf(sh, true);
  g.globalAlpha = 1;
  Sh.ms.dots += performance.now() - t0;
}
// The words of one part of step k + 1: { key, label, say }. label names the part (in the line above the sentence
// and in the picture's corner); say is the sentence.
function learnShapePartWords(k, ph) {
  const L = LEARN, Sh = LEARN_SHAPE, three = L.space === 3, ring = three ? 'ball' : 'circle', kinds = learnShapeKinds(), both = kinds.length === 2, kind = Sh.kind;
  const M = learnShapeMoves(), chs = kinds.map(kd => learnShapeChain(kd, k)), m = M.moves.length, step = `Step ${k + 1}`, steps = `${k} step${k === 1 ? '' : 's'}`;
  const [First, Second] = Sh.side ? ['Left', 'Right'] : ['Upper', 'Lower'];
  const on = chs.reduce((n, c) => n + c.on, 0), thrown = chs.reduce((n, c) => n + c.thrown, 0), left = on - thrown;
  const label = ph.key === 'out' ? 'where the dots are now' : ph.key === 'gone' ? 'thrown out' : ph.key === 'home' ? 'back home' : M.names[ph.j];
  let say;
  if (!on) say = `${step}. No dot is left to show it: every dot has already been thrown out. Dots: Many shows more of them, and Each step: At once shows every bite.`;
  else if (ph.key === 'out') {
    // what the part does in one picture: 'c' every dot goes to the centre, 's' the dots are where they start, 'o' anything else
    const does = chs.map(c => (!c.moved[0] ? 's' : c.centre ? 'c' : 'o')).join('');
    if (k > 0) say = `${step}. First, where the dots are now: each has already taken ${steps}` + (both ? '.' : kind === 'm' ? ' from the centre, with its own c.' : ' from its starting place.');
    else if (does === 'c') say = `${step}. Every dot starts at the centre. What differs from dot to dot is its number c: the place it came from.`;
    else if (does === 's') say = `${step}. The dots are at their starting places: nobody has taken a step yet.`;
    else if (does === 'cs') say = `${step}. ${First}: every dot starts at the centre, each with its own number c. ${Second}: the dots are at their starting places.`;
    else say = `${step}. First the dots go to where this approach’s dials put them before any step is taken.`;
  } else if (ph.key === 'move') {
    const mv = M.moves[ph.j], name = M.names[ph.j], moved = chs.some(c => c.moved[ph.j + 1]);
    // every dot of every picture that moves at all stands at the centre when this move begins
    const centre = chs.every(c => c.list.every(i => len(c.pos[i][ph.j]) < 1e-12));
    if (!moved) say = `${step}, ${name}: ` + (centre ? 'every dot is at the centre, so nothing moves.' : mv.key === 'shift' && kind === 'j' ? 'c is 0 here, so no dot moves.' : 'this move leaves every dot where it is.');
    else if (mv.key === 'shift') say = `${step}, ${name}: ` + (both ? `${First.toLowerCase()}, every dot is moved by its own c. ${Second}, every dot is moved by the diamond’s c.` : kind === 'm' ? 'every dot is moved by its own c.' : 'every dot is moved by c.');
    else say = `${step}, ${name}: ${mv.all || 'every dot makes this move by its own amount; Follow One point shows it for a single dot'}.`;
  } else if (ph.key === 'gone') {
    // (thin[k] other than '-': the pictures themselves show this step taking something)
    // In space a dot that is outside the big ball can still be drawn inside its outline: it is in front of the ball
    // or behind it. Where there is such a dot the sentence says so (the view decides: learnShapeProj).
    let hid = false;
    if (three && thrown) chs.forEach((c, n) => {
      const P = Sh.panes[n], D = learnShapeDots(kinds[n]);
      if (!P || hid) return;
      const pr = learnShapeProj(P), mid = pr.to([0, 0, 0]);
      hid = c.list.some(i => { if (D.dots[i].out !== k + 1) return false; const q = pr.to(c.pos[i][m]); return Math.hypot(q[0] - mid[0], q[1] - mid[1]) < 2 * pr.s; });
    });
    say = thrown ? `${step}. The dots that landed outside the big ${ring} are thrown out${both ? ', in both pictures' : ''}: ${thrown} of ${on}.` + (hid ? ' Some of them are in front of the ball or behind it.' : '')
      : `${step}. No dot landed outside the big ${ring}, so none is thrown out.` + (Sh.thin[k] === '0' || Sh.thin[k] === '1' ? ' What this step takes is finer than the gaps between the dots.' : '');
  } else {
    const home = !chs.some(c => c.moved[m + 1]);      // every dot that is left already stands on its starting place
    say = !left ? `${step}. No dot is left: every one of them has been thrown out.`
      : home ? `${step}. Every dot has landed on its own starting place, so nobody has to go back.` + (!thrown && !both ? ` Shape ${k + 1} is still the whole big ${ring}.` : '')
        : `${step}. The dots that are left go back to where they started. Those starting places are shape ${k + 1}.`;
  }
  return { key: ph.key, label, say, i: ph.i, n: ph.n, t: ph.t, j: ph.j, on, thrown };
}
// What the picture of starting places shows in a part of step k + 1: the step and the fraction of today's blend
// (learnShapeTint, learnShapeLevels), and how strongly it shows behind the dots.
function learnShapeBackdrop(k, ph, three) {
  const e = learnShapeEase, q = LEARN_SHAPE_QUIET[three ? 3 : 2], b = LEARN_SHAPE_QUIET.bite;
  if (ph.key === 'out') return { k, u: 0, back: 1 - (1 - q) * e(0, 0.6, ph.t) };
  if (ph.key === 'move') return { k, u: 0, back: q };
  if (ph.key === 'gone') return ph.t >= 1 ? { k: k + 1, u: 0, back: b } : { k, u: ph.t, back: q + (b - q) * e(0, 0.25, ph.t) };
  return { k: k + 1, u: 0, back: b + (1 - b) * e(0.35, 1, ph.t) };
}
// The names of the parts of one step, in a row under the sentence: the one being played is marked, and a click
// plays that part alone (as the names of the moves do in One point).
function learnShapeChips(W) {
  const Sh = LEARN_SHAPE, E = Sh.el, on = learnShapeMovesOn();
  if (!E.parts) return;
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

// ---------- the words
function learnShapeWords() {
  const L = LEARN, Sh = LEARN_SHAPE, N = LEARN_SHAPE_N, three = L.space === 3, ring = three ? 'ball' : 'circle';
  const k = Math.min(N, Math.floor(Sh.pos + 1e-9)), u = Sh.pos - k, whole = u < 1e-9, kind = Sh.kind, n = S.n;
  const [first, second] = Sh.side ? ['left', 'right'] : ['upper', 'lower'], First = Sh.side ? 'Left' : 'Upper', Second = Sh.side ? 'Right' : 'Lower';
  const zero = kind !== 'j' && learnShapeZeroStays();      // the first step takes nothing from the Mandelbrot shape
  const start = kind === 'm' || learnShapeStartWhole();    // the Julia shape begins as the whole big circle or ball
  // Of which pictures on show nothing is left after these k steps (learnShapeDraw finds out, and paints again when
  // that changes). "Every point of the picture": a flat picture is asked point by point, and what it cannot show
  // (a dust of single points, say) is not claimed to be gone.
  const goneM = k > 0 && kind !== 'j' && Sh.gone.includes('m'), goneJ = k > 0 && kind !== 'm' && Sh.gone.includes('j');
  const gone = kind === 'm' ? goneM : kind === 'j' ? goneJ : goneM && goneJ, steps = `${k} step${k === 1 ? '' : 's'}`;
  // the bite of the step under way is too fine to see in the pictures as they stand (learnShapeDraw finds out)
  const thin = k < N && Sh.thin[k] === '1';
  // While the steps play from end to end the sentence stays the same: one that changes every third of a second
  // cannot be read, and draws the eye off the picture. (Standing still, or going one step at a time, each step
  // has its own.) Before the first move such a play rests on the start, with the sentence of the start.
  // (round 29) with "Each step: Move by move" every part of a step has its own sentence, also while the steps play
  const mvOn = learnShapeMovesOn();
  const calm = !mvOn && Sh.playing && Sh.until === null && Sh.pos > 1e-9, pics = kind === 'both' ? 's' : '';
  const mName = 'the Mandelbrot shape', jName = 'the Julia shape for the diamond’s c';
  // (every sentence is short enough for three lines on a phone: about 150 letters)
  let say;
  if (gone) {
    say = calm ? `Nothing is left to see: every point of the picture${pics} has been thrown out.`
      : whole ? `After ${steps} nothing is left to see: every point of the picture${pics} has been thrown out.`
        : `Step ${k + 1}: there is nothing left to take it. Every point of the picture${pics} has already been thrown out.`;
  } else if (calm) {
    // ("now": a bite has been too fine by this step, and none from here on is one that can be seen; so the
    // sentence does not come and go)
    say = k < N && Sh.thin.slice(0, k + 1).includes('1') && !Sh.thin.slice(k).includes('0') ? 'The bites are now too fine to see at this size. Zoom in.'
      : `At each step${kind === 'both' ? ', in both pictures,' : ''} every point that is still here takes one more step. The ones that land outside the big ${ring} are thrown out.`;
  } else if (whole && (goneM || goneJ)) {
    say = `After ${steps}. ${First}: ${goneM ? 'nothing is left to see' : mName}. ${Second}: ${goneJ ? 'nothing is left to see' : jName}.`;
  } else if (whole && k === 0) {
    // (a 3D Julia shape that does not begin as the whole ball: an approach whose dials put the picture's points
    // further out than they look, see learnShapeStartWhole)
    const less = `With this approach’s dials as they stand, the points near the surface of the big ball already count as outside`;
    say = kind === 'm' ? `The big ${ring}: every point no further than 2 from the centre. Each point is tried as the number c; its dot starts at the centre.`
      : kind === 'j' ? (start ? `The big ${ring}. Every point is a place to start from, and all of them use the same c, the diamond.`
        : `The start. ${less}, so the shape begins smaller.`)
        : start ? `Two big ${ring}s. ${First}: each point is tried as the number c; its dot starts at the centre. ${Second}: each point is where a dot starts, all with the diamond’s c.`
          : `The start. ${First}: each point is tried as the number c. ${Second}: the points near the ball’s surface already count as outside.`;
  } else if (whole) {
    const after = `What is left after ${steps}`;
    if (k === 1 && zero) {
      say = kind === 'm' ? `After 1 step the whole big ${ring} is still there: the first step only carried each dot from the centre to its own point.`
        : `${after}. ${First}: still the whole big ${ring}. ${Second}: ${jName}.`;
    } else if (k === N) {
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
  } else if (k === 0 && zero) {
    say = kind === 'm' ? `Step 1: each dot jumps from the centre to its own point. Nobody lands outside the big ${ring}, so nothing is thrown out yet.`
      : `Step 1. ${First}: each dot jumps from the centre to its own point, and nobody lands outside. ${Second}: the points that land outside are thrown out.`;
  } else if (thin) {
    say = `Step ${k + 1}: this bite is too fine to see at this size. Zoom in.`;
  } else {
    say = `Step ${k + 1}: ${kind === 'both' ? 'in both pictures ' : ''}every point that is still here takes one more step. The ones that land outside the big ${ring} are thrown out.`;
  }
  // (round 29) Move by move: between two whole steps the words are those of the part being played (unless nothing
  // at all is left of the pictures: then the sentence above says so)
  let part = null;
  if (mvOn && !whole && k < N && !gone) { part = learnShapePartWords(k, learnShapePart(u)); say = part.say; }
  const where = whole ? `Step ${k} of ${N}: <b>${k === 0 ? 'the start' : 'what is left'}</b>` : `Step ${k + 1} of ${N}: <b>${part ? part.label : 'under way'}</b>`;
  const read = whole ? (k === 0 ? 'the start' : `after ${k} step${k === 1 ? '' : 's'}`) : part ? `step ${k + 1}: ${part.label}` : `step ${k + 1}`;
  return { say, where, read, k, u, whole, part };
}

// ---------- where the pictures stand
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

// ---------- drawing
function learnShapeCols() {
  const Sh = LEARN_SHAPE, C = LEARN.col;
  if (Sh.cols && Sh.cols.from === C) return Sh.cols;
  const rgb = s => { try { const v = hexRgb(s); return v.every(x => isFinite(x)) ? v : [0.5, 0.5, 0.5]; } catch (err) { return [0.5, 0.5, 0.5]; } };
  return (Sh.cols = { from: C, stage: rgb(C.stage), brass: rgb(C.brass), bad: rgb(C.bad), ink: rgb(C.ink), ink2: rgb(C.ink2) });
}
// Coarse or fine: coarse while the steps play, while something is held, and while changes come in a stream.
function learnShapeQuality() {
  const Sh = LEARN_SHAPE;
  return Sh.playing || Sh.drag || Sh.pinch || performance.now() - Sh.hot < 140 ? 'move' : 'still';
}
// Everything a picture depends on, as one string. A change soon after the last one means a dial or the slider is
// being dragged: the pictures stay coarse until that rests.
// In 3D every change counts as such, a single one too (a tick of the slider, another approach, a named c, the first
// notch of the wheel): the picture is drawn coarse at once and fine 180 ms later. A fine picture of a dear approach,
// zoomed in, takes the graphics card over a second, and what the coarse one cost tells the 3D module how fine the
// resting one can be without holding the page up (measured: out/r26/join/NOTES.md).
function learnShapeSeen() {
  const Sh = LEARN_SHAPE, a = ap(), V = Sh.view2, W = Sh.view3;
  const sig = [S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.kind, LEARN.space, V.m.x, V.m.y, V.m.zoom, V.j.x, V.j.y, V.j.zoom,
    W.yaw, W.pitch, W.zoom, LEARN.space === 3 ? Sh.pos : ''].join('|');
  if (sig === Sh.seen) return;
  const now = performance.now();
  if (LEARN.space === 3 || (Sh.seen && now - Sh.touched < 250)) Sh.hot = now;
  Sh.touched = now; Sh.seen = sig;
}
// The kept numbers of one flat picture, worked out again when they no longer fit.
function learnShapeChart(P, quality) {
  const Sh = LEARN_SHAPE, V = P.V, N = LEARN_SHAPE_N;
  // the part of the pane the big circle covers, in whole CSS pixels
  const x0 = Math.max(P.x, Math.floor(P.cx + (-2 - V.x) * P.s)), x1 = Math.min(P.x + P.w, Math.ceil(P.cx + (2 - V.x) * P.s));
  const y0 = Math.max(P.y, Math.floor(P.cy - (2 - V.y) * P.s)), y1 = Math.min(P.y + P.h, Math.ceil(P.cy - (-2 - V.y) * P.s));
  const key = [P.kind, S.n, S.abs[0], S.abs[1], S.flip[0], P.kind === 'j' ? Sh.c[0] + ',' + Sh.c[1] : '', x0, y0, x1, y1, P.s, P.cx, P.cy, V.x, V.y].join('|');
  // samples to a CSS pixel, each way: 2 at rest; 1 while something is dragged, or 1/2 when the power needs the polar
  // form, which costs some twenty times more a sample (measured: out/r26/core/NOTES.md)
  const polar = !(Number.isInteger(S.n) && S.n >= 2 && S.n <= 8), want = quality === 'move' ? (polar ? 0.5 : 1) : 2;
  let M = Sh.maps[P.kind];
  if (M && M.key === key && M.dens >= want) return M;
  const t0 = performance.now(), dens = want, w = Math.ceil(Math.max(0, x1 - x0) * dens), h = Math.ceil(Math.max(0, y1 - y0) * dens);
  if (!M) M = Sh.maps[P.kind] = { cv: document.createElement('canvas'), n: 0 };
  Object.assign(M, { key, dens, w, h, bx: x0, by: y0, bw: w / dens, bh: h / dens });
  if (!w || !h) return M;
  if (M.n !== w * h) { M.n = w * h; M.map = new Uint8Array(M.n); M.edge = new Uint8Array(M.n); M.tmp = new Uint8Array(M.n); }
  if (M.cv.width !== w || M.cv.height !== h) { M.cv.width = w; M.cv.height = h; M.g = M.cv.getContext('2d'); M.img = M.g.createImageData(w, h); M.px = new Uint32Array(M.img.data.buffer); }
  const d = 1 / (dens * P.s);
  learnShapeMap(P.kind, Sh.c, S.n, S.abs, S.flip, V.x + (x0 + 0.5 / dens - P.cx) / P.s, V.y - (y0 + 0.5 / dens - P.cy) / P.s, d, d, w, h, N, M.map);
  const band = dens >= 2 ? 2 : 1;
  learnShapeEdge(M.map, w, h, band, M.tmp, M.edge);
  // left[k]: how many samples are still in after k steps (so that the words can say when nothing is left);
  // thick[k]: how thick the bite of step k + 1 is, here in pixels of the picture (so that they can say when a bite
  // is too fine to see)
  const tally = learnShapeTally(M.map, M.edge, M.n, N, band);
  M.left = tally.left; M.thick = tally.thick.map(t => t / dens);
  const ms = performance.now() - t0;
  Sh.ms.map += ms; Sh.ms.mapLast = ms; Sh.ms.mapSamples = w * h; Sh.ms.mapDens = dens;
  return M;
}
// One flat picture for the slider's position k + u: the numbers become colours. What is left after step k + 1 is
// the body. The points thrown out at step k + 1 (the bite) light up and fade. The outline of the shape before
// fades out, and the outline of shape k comes up where the bite was.
function learnShapeTint(M, k, u, keep) {
  // (round 29) keep: Move by move draws the same backdrop frame after frame; when the canvas already holds the
  // colours of this very picture they are not worked out again
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
// One flat picture: faint axes, what is left, the big circle, a few numbers, the diamond.
// (Round 29.) mv: null with "Each step: At once"; with Move by move { k, ph, back }: the step the dots are at, the
// part being played (null at a whole step) and how strongly the picture shows behind the dots. k and u are then
// what the picture of starting places shows in that part (learnShapeBackdrop).
function learnShapeFlat(g, P, k, u, quality, C, label, small, mv) {
  const Sh = LEARN_SHAPE, V = P.V, X = x => P.cx + (x - V.x) * P.s, Y = y => P.cy - (y - V.y) * P.s, box = [P.x, P.y, P.w, P.h];
  const line = (x0, y0, x1, y1, col, wd, al, dash) => { g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.strokeStyle = col; g.lineWidth = wd; g.globalAlpha = al; g.setLineDash(dash || []); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; };
  g.save(); g.beginPath(); g.rect(P.x, P.y, P.w, P.h); g.clip();
  line(P.x, Y(0), P.x + P.w, Y(0), C.ink2, 1, 0.55); line(X(0), P.y, X(0), P.y + P.h, C.ink2, 1, 0.55);
  // a few numbers along the axes: a mark at each, and the figure where there is room for it. They lie under the
  // shape, like the axes: what is left covers them, and they show again where it has been eaten away.
  // (the finest of these steps that still leaves the marks 80 pixels apart; a small picture names only 2 and −2)
  const step = [0.02, 0.05, 0.1, 0.2, 0.5, 1].find(s => s * P.s >= 80) || 1, dec = step >= 1 ? 0 : step >= 0.1 ? 1 : 2, tight = P.s < 46;
  const inX = x => x > P.x + 4 && x < P.x + P.w - 4, inY = y => y > P.y + 4 && y < P.y + P.h - 4;
  for (let i = Math.ceil(-2 / step - 1e-9); i <= Math.floor(2 / step + 1e-9); i++) {
    if (!i) continue;
    const v = i * step, far = Math.abs(Math.abs(v) - 2) < 1e-9;
    line(X(v), Y(0) - 3, X(v), Y(0) + 3, C.ink2, 1, 0.8); line(X(0) - 3, Y(v), X(0) + 3, Y(v), C.ink2, 1, 0.8);
    if (tight && !far) continue;
    // a figure follows its mark; when the axis itself is out of the picture it waits at the picture's edge
    if (inX(X(v))) label(learnVNum(v, dec), X(v) + (far ? (v > 0 ? 9 : -9) : 0), Y(0) + 12, C.ink2, far ? (v > 0 ? 'left' : 'right') : 'center', small ? 10 : 11, 500, box);
    // The figures of the upright axis stand to the right of it: to its left, 1 and −1 sat on the upper and lower
    // tips of the Mandelbrot shape and looked like dirt on them. In a small picture the 2 at the top is left out:
    // the labels of the picture's corner stand there.
    if (tight && v > 0) continue;
    if (inY(Y(v))) label(learnVNum(v, dec), X(0) + 8, Y(v) + (far ? (v > 0 ? -9 : 9) : 0), C.ink2, 'left', small ? 10 : 11, 500, box);
  }
  const t0 = performance.now(), M = learnShapeChart(P, quality);
  if (M.w && M.h) {
    learnShapeTint(M, k, u, !!mv); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    if (mv) g.globalAlpha = mv.back;
    g.drawImage(M.cv, M.bx, M.by, M.bw, M.bh);
    if (mv) g.globalAlpha = 1;
  }
  Sh.ms.fill += performance.now() - t0;
  // the big circle (while the dots are away from home it is drawn firmly: it is the line the throwing out is judged by)
  g.beginPath(); g.arc(X(0), Y(0), 2 * P.s, 0, 2 * PI);
  if (mv && mv.ph) { g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.9; g.stroke(); g.globalAlpha = 1; }
  else { g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.globalAlpha = 0.8; g.setLineDash([4, 4]); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; }
  if (mv) learnShapeDotsDraw(g, P, v => [X(v[0]), Y(v[1]), 0], P.s, mv.k, mv.ph, false);
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
  if (typeof learnShape3d === 'undefined' || !learnShape3d || typeof learnShape3d.make !== 'function') { Sh.threeNote = LEARN_SHAPE_MISSING; return null; }
  let view = null;
  try { view = learnShape3d.make(); } catch (err) { console.warn('learnShape3d.make failed', err); }
  if (!view || !view.canvas || typeof view.draw !== 'function') {
    Sh.threeNote = (typeof learnShape3d.note === 'function' && learnShape3d.note()) || 'This device cannot draw the 3D picture. The 2D page still works.';
    return null;
  }
  view.canvas.classList.add('learn-shape-gl'); view.canvas.setAttribute('aria-hidden', 'true'); view.canvas.hidden = true;
  // When the browser takes the graphics away the module says so in a sentence, which stands in the picture's place;
  // when they come back the module draws again by itself, and the page has to put the picture back in sight.
  // (A task later: the module's own listener was added first and has then set itself up again.)
  // (what was asked of the lost graphics is asked again: learnShapeAbove)
  for (const ev of ['webglcontextlost', 'webglcontextrestored']) view.canvas.addEventListener(ev, () => setTimeout(() => { Sh.above = {}; learnShapeNow(); }, 0));
  stage.insertBefore(view.canvas, Sh.el.canvas);
  return (Sh.three = view);
}
// The skins of one 3D picture for the slider's position k + u. At a whole step: the shape as solid glass and the
// shape before as a ghost. In between: the skin of shape k + 1, the body that stays, comes up to solid glass in
// the first eighth of the step; the skin of shape k thins to a peel of glass and then takes the warning colour
// (first thin, then red: the whole body never flashes red), so that the body shows through it and the colour marks
// the part that goes, as the bite does on the 2D page; then the peel pales to a ghost, and the old ghost fades out.
// same: the first step takes nothing from this picture (a Mandelbrot shape whose dots go from 0 to their own c).
// Then shape 1 is shape 0: through the whole of step 1 the ball stays as it was, no warning colour and no ghost.
// solid: up to step 5 the body is glass. From there to step 11 its near side is drawn more and more solid (the 3D
// module's `solid`): what is left of the rougher rules after many steps is a body with fine folds all over, and as
// glass that was a tangle of sheets seen through one another, "a ball of gold wool". Peel and ghost stay glass.
// bite: how thick the part is that the step under way takes, in pixels of the picture (undefined: not known). A
// peel that lies less than a pixel or two off the body cannot show which part goes: it only reddens the whole
// body, at every step. So a thin bite gets a faint peel, and none at all when it is too fine to see (the sentence
// then says so); zoomed in, where the bite is thick again, the peel is back.
function learnShapeLevels(k, u, same, bite) {
  const G = LEARN_SHAPE_GLASS, e = learnShapeEase, grey = 0.55, out = [], deep = e(G.deep[0], G.deep[1], k + u);
  if (same && k === 0) return [{ k: 0, alpha: G.solid, tint: 0, solid: deep }];
  const before = k > 0 && !(same && k === 1);      // a ghost of the shape before, unless that is the very same shape
  if (u < 1e-9) { out.push({ k, alpha: G.solid, tint: 0, solid: deep }); if (before) out.push({ k: k - 1, alpha: G.ghost, tint: 0, ghost: grey, solid: 0 }); }
  else {
    const thinned = e(0, 0.18, u), pale = e(0.55, 1, u), show = bite === undefined ? 1 : e(0.5, 3, bite), peel = Math.max(G.peel * show, G.ghost);
    out.push({ k: k + 1, alpha: G.solid * e(0, 0.12, u), tint: 0, solid: deep });
    out.push({ k, alpha: G.solid + (peel - G.solid) * thinned + (G.ghost - peel) * pale, tint: show * e(0.08, 0.25, u) * (1 - pale), ghost: grey * pale, solid: deep * (1 - thinned) });
    if (before) out.push({ k: k - 1, alpha: G.ghost * (1 - e(0, 0.5, u)), tint: 0, ghost: grey, solid: 0 });
  }
  return out.filter(l => l.alpha > 0.004);
}
// Where a point of space lands in a pane of the 3D picture. The module says so itself (proj); without that, the
// same flat camera is worked out here: no perspective, the big ball taking 80% of the smaller side at zoom 1.
function learnShapeProj(P) {
  const V = LEARN_SHAPE.view3, rect = [P.x, P.y, P.w, P.h];
  const s = 0.2 * Math.min(P.w, P.h) * V.zoom;
  if (typeof learnShape3d !== 'undefined' && learnShape3d && typeof learnShape3d.proj === 'function') {
    try { const p = learnShape3d.proj(V, rect); if (p && typeof p.to === 'function') return { to: p.to, s: p.s > 0 ? p.s : s }; } catch (err) { /* worked out here instead */ }
  }
  const cy = Math.cos(V.yaw), sy = Math.sin(V.yaw), cp = Math.cos(V.pitch), sp = Math.sin(V.pitch), R = [cy, sy, 0], U = [-sy * sp, cy * sp, cp], D = [sy * cp, -cy * cp, sp];
  const mx = P.x + P.w / 2, my = P.y + P.h / 2;
  return { to: v => [mx + dot(v, R) * s, my - dot(v, U) * s, dot(v, D)], s };
}
// The 3D pictures. Returns '' when they are drawn, or the sentence to show in their place.
// (Round 29.) mv: as for learnShapeFlat.
function learnShapeSolid(g, panes, k, u, quality, C, label, small, above, mv) {
  const Sh = LEARN_SHAPE, T = learnShapeThree(), K = learnShapeCols();
  if (!T) return Sh.threeNote || LEARN_SHAPE_MISSING;
  // Each picture has skins of its own: in Both the first step takes nothing from the Mandelbrot shape and a bite
  // from the Julia shape. (o.levels is the first picture's, for a module that does not read a pane's own.)
  // above: what learnShapeAbove knows of each picture (the thickness of the bite under way comes from there).
  const zero = learnShapeZeroStays(), lv = panes.map((P, i) => {
    const A = above ? above[i] : null, bite = A && k < LEARN_SHAPE_N ? A.thick[k] * A.unit * learnShapeProj(P).s : undefined;
    return learnShapeLevels(k, u, P.kind === 'm' && zero, bite);
  });
  const V = Sh.view3, o = {
    panes: panes.map((P, i) => ({ kind: P.kind, rect: [P.x, P.y, P.w, P.h], levels: lv[i] })), c: Sh.c.slice(), levels: lv[0],
    yaw: V.yaw, pitch: V.pitch, zoom: V.zoom, quality, colours: { bg: K.stage, body: K.brass, warn: K.bad, ink: K.ink }, flat: false,
  };
  let res = null;
  if (T.canvas.hidden) T.canvas.hidden = false;      // the module fits its buffer to the box, so the box has to be there
  // (round 29) Move by move: while only the dots move, the glass picture is the same from frame to frame. It is
  // then not drawn again (its canvas keeps it), and behind the dots it shows as a faint ghost: by the opacity of
  // its canvas, which costs the graphics card nothing.
  const a3 = ap(), sig3 = mv ? JSON.stringify([o, a3.id, S.param[a3.id], S.n, S.abs, S.flip, T.canvas.clientWidth, T.canvas.clientHeight, window.devicePixelRatio]) : '';
  if (mv && sig3 === Sh.sig3 && Sh.res3 && Sh.res3.ok) res = Sh.res3;
  else {
    try { res = T.draw(o); } catch (err) { if (!Sh.warned) { Sh.warned = true; console.warn('learnShape3d.draw failed', err); } }   // (said once, not once a frame)
    Sh.sig3 = sig3; Sh.res3 = res;
  }
  const faint = mv && mv.back < 0.999 ? String(Math.round(mv.back * 1000) / 1000) : '';
  if (T.canvas.style.opacity !== faint) T.canvas.style.opacity = faint;
  Sh.last3 = { levels: o.levels, paneLevels: lv, quality, panes: o.panes.length, ok: !!(res && res.ok), ms: res ? res.ms : 0 };
  if (!res || !res.ok) return (res && res.note) || (typeof learnShape3d.note === 'function' && learnShape3d.note()) || 'The 3D picture could not be drawn for these settings.';
  Sh.ms.three = +res.ms || 0;
  // Over the glass: the rim of the big ball as a dashed ring (the big circle of the flat pictures), faintly the
  // circle in which the flat plane cuts it, and the diamond c with a thin line down to the flat plane, so that its
  // height can be read.
  for (const P of panes) {
    const pr = learnShapeProj(P), to = pr.to, mid = to([0, 0, 0]), box = [P.x, P.y, P.w, P.h];
    P.dia = null; P.at3 = null;
    g.save(); g.beginPath(); g.rect(P.x, P.y, P.w, P.h); g.clip();
    g.strokeStyle = C.ink2; g.lineWidth = 1.25; g.setLineDash([4, 4]);
    g.beginPath(); g.arc(mid[0], mid[1], 2 * pr.s, 0, 2 * PI); g.globalAlpha = 0.6; g.stroke();
    g.beginPath(); for (let i = 0; i <= 72; i++) { const a = i / 72 * 2 * PI, q = to([2 * Math.cos(a), 2 * Math.sin(a), 0]); if (i) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); }
    g.lineWidth = 1; g.setLineDash([2, 4]); g.globalAlpha = 0.4; g.stroke(); g.setLineDash([]); g.globalAlpha = 1;
    // (round 29) the dots of Move by move; while they are away from home the big ball's outline is drawn firmly
    if (mv && mv.ph) { g.beginPath(); g.arc(mid[0], mid[1], 2 * pr.s, 0, 2 * PI); g.strokeStyle = C.ink; g.lineWidth = 1.6; g.globalAlpha = 0.85; g.stroke(); g.globalAlpha = 1; }
    if (mv) learnShapeDotsDraw(g, P, to, pr.s, mv.k, mv.ph, true);
    if (Sh.kind === 'm') { g.restore(); continue; }
    const q = to(Sh.c), f = to([Sh.c[0], Sh.c[1], 0]);
    // as in a flat picture: a diamond that is out of the picture is not drawn, and neither is its letter (which
    // would be held at the picture's edge and stand there alone)
    if (!(q[0] > P.x - 8 && q[0] < P.x + P.w + 8 && q[1] > P.y - 8 && q[1] < P.y + P.h + 8)) { g.restore(); continue; }
    P.at3 = [q[0], q[1]];
    if (Math.hypot(q[0] - f[0], q[1] - f[1]) > 3) {
      g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(f[0], f[1]); g.strokeStyle = C.ink; g.lineWidth = 1; g.globalAlpha = 0.7; g.setLineDash([2, 3]); g.stroke(); g.setLineDash([]);
      g.beginPath(); g.arc(f[0], f[1], 1.75, 0, 2 * PI); g.fillStyle = C.ink; g.fill(); g.globalAlpha = 1;
    }
    learnShapeDiamond(g, C, (t, x, y, col, al, px, wt) => label(t, x, y, col, al, px, wt, box), q, small);
    g.restore();
  }
  return '';
}
// touch(), a resize and the theme come here through learnVDraw; the clock and the hands of this file call it too.
// (In a flat picture P.dia is where the diamond stands, and it can be taken hold of there. Over a 3D picture the
// diamond is only shown, at P.at3: there c is moved with its dials.)
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
  const C = L.col, g = cv.getContext('2d'), three = L.space === 3, quality = Sh.quality = learnShapeQuality(), small = w < 480;
  const N = LEARN_SHAPE_N, k = Math.min(N, Math.floor(Sh.pos + 1e-9)), u = k >= N ? 0 : clamp(Sh.pos - k, 0, 1), panes = Sh.panes = learnShapePanes(w, h);
  const label = learnShapeLabel(g, C, w, h);
  Sh.ms.map = 0; Sh.ms.fill = 0;
  g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h); g.lineJoin = g.lineCap = 'round';
  let note = '';
  // (a flat picture's numbers do not change while the steps play, so playing alone does not make it coarse)
  const flatQ = Sh.drag || Sh.pinch || t0 - Sh.hot < 140 ? 'move' : 'still';
  // what the words need to know of a 3D shape is asked before the picture is drawn: the answer waits for the
  // graphics card, and should not have to wait for a fine picture as well
  const above = three && learnShapeThree() ? panes.map(P => learnShapeAbove(P.kind, quality)) : null;
  // (round 29) Move by move: the part of the step being played (null at a whole step), what the picture of
  // starting places shows in it and how strongly (bd), and what the pictures need to draw the dots (mv). With
  // At once: no part, the picture of the slider's own position at full strength, and no dots.
  Sh.ms.dots = 0;
  const mvOn = learnShapeMovesOn(), ph = mvOn && u > 1e-9 && k < N ? learnShapePart(u) : null;
  const bd = ph ? learnShapeBackdrop(k, ph, three) : { k, u, back: 1 }, mv = mvOn ? { k, ph, back: bd.back } : null;
  if (three) note = learnShapeSolid(g, panes, bd.k, bd.u, quality, C, label, small, above, mv);
  else for (const P of panes) learnShapeFlat(g, P, bd.k, bd.u, flatQ, C, label, small, mv);
  if (Sh.three) Sh.three.canvas.hidden = !three || !!note;
  if (note) g.clearRect(0, 0, w, h);
  let said = Sh.note !== note;
  if (said) { Sh.note = note; E.note.textContent = note; }
  E.note.hidden = !note;
  // Of which pictures is nothing left after these k steps? A flat picture is asked itself (the whole one only: a
  // zoomed one shows a part). A 3D picture is not read back. There it is said in the one case that is certain, a
  // Mandelbrot shape whose every point the first step throws out (learnShapeZeroOut), and when the shape seen from
  // straight above is gone (learnShapeAbove; not zoomed in beyond one and a half times, where the picture could
  // show crumbs finer than that look).
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
      // (in Both the Julia picture is named after what chooses it, where there is room: before the first drag
      // nothing else in the pictures ties the diamond of the one to the shape of the other)
      const box = [P.x, P.y, P.w, P.h], name = (P.kind === 'm' ? 'Mandelbrot' : 'Julia') + (narrow ? '' : ' shape') + (P.kind === 'j' && panes.length === 2 && P.w >= 330 ? ' for the diamond’s c' : '');
      label(name, P.x + 10, P.y + 15, C.ink, 'left', small ? 12.5 : 14, 600, box);
      // (round 29: in a part of a step the corner names the part, where there is room; only the throwing out is in the warning colour)
      if (i === 0) label(W.part && narrow ? `step ${W.k + 1}` : W.read, P.x + 10, P.y + (small ? 32 : 35), W.whole ? C.brass : W.part && W.part.key !== 'gone' ? C.ink : C.bad, 'left', small ? 12.5 : 14, 600, box);
      // (and, where the corner has room for a third line, what a dot is)
      if (i === 0 && mv && !small && !narrow) label('each dot: one starting place', P.x + 10, P.y + 54, C.ink2, 'left', 12, 500, box);
    });
  }
  Sh.ms.frame = performance.now() - t0; Sh.ms.fill -= Sh.ms.map;
  if (said) learnShapePaint();      // the hint and the panel say whether there is a 3D picture; the sentence, whether anything is left
  // a coarse picture is followed by a fine one as soon as things rest
  if (quality === 'move' && !Sh.playing && !Sh.drag && !Sh.pinch) {
    clearTimeout(Sh.rest);
    Sh.rest = setTimeout(() => { Sh.rest = 0; if (learnShapeIsOn()) { learnShapePaint(); learnShapeDraw(); } }, 180);
  }
}

// ---------- the words and marks on the page
function learnShapePanel() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, three = L.space === 3, a = ap();
  const set = (node, text) => { if (node.textContent !== text) node.textContent = text; };
  const bare = !S.abs.some(Boolean) && !S.flip.some(Boolean), plain = S.n === 2 && bare, first = Sh.side ? 'left' : 'upper', second = Sh.side ? 'right' : 'lower';
  E.cBlock.hidden = Sh.kind === 'm';
  // a named value: its name first, where the name is true (the plain power 2), and the value as the dials name it
  E.named.forEach((b, i) => { const v = LEARN_SHAPE_NAMED[i]; b.firstChild.hidden = !plain; set(b.lastChild, plain ? `(${v.text})` : v.text); });
  // what a step is, in a line (the one-point note that says it is put away while the whole shape is on)
  set(E.intro, 'Take every point inside the big circle (in 3D, the big ball) and let each one take steps. A point that lands outside is thrown out. Press Play under the picture and watch what is left after each step.'
    + ` A step is the lab’s rule: ${S.n === 2 ? 'square' : 'take to the power ' + String(+(+S.n).toFixed(2)).replace('-', '−') + ' (the dial “Power n”)'}, then add c. (Follow: One point shows one step slowly.)`);
  set(E.helpJ, 'The number c is the same for all: the diamond. Each point of the picture is a place where a dot starts.');
  set(E.helpBoth, `${Sh.side ? 'Side by side' : 'One above the other'}. The diamond in the ${first} picture picks one c; the ${second} picture is the Julia shape for that c. `
    + (three ? 'Move c with its dials and watch the ' : 'Drag the diamond and watch the ') + second + ' picture.');
  E.rule.hidden = !three;
  // (Sh.note: the sentence the stage shows when there is no 3D picture; learnShapeDraw paints again when it changes)
  set(E.rule, !three ? '' : `In 3D the steps follow the approach chosen under Approach and equation, now “${a.name}”, with its dials and power as set there.`
    + (Sh.note ? ' ' + Sh.note : ''));
  // Both on the 2D page, a whole power of 2 or more and no modifier: once c is thrown out of the Mandelbrot shape
  // (the diamond stands outside the left shape), the Julia shape of the same step is in pieces. Not said of step 0
  // or 1, where the left shape is still the whole big circle.
  set(E.notice, three
    ? 'The ball is not bent into the shape. It is eaten away: each step removes the points that have just landed outside, and the bites get smaller and finer.'
      + (learnShapeCutHolds() ? ' Slice this 3D shape level through its middle, where the dotted ring runs, and the cut is exactly the 2D picture of the same step.'
        + (Sh.kind === 'm' ? ' (True for this approach.)' : ' (True for this approach while c’s z dial stands at 0.)') : '')
    : 'The circle is not bent into the shape. It is eaten away: each step removes the points that have just landed outside, and the bites get smaller and finer.'
      + (Sh.kind === 'both' && bare && Number.isInteger(S.n) && S.n >= 2 ? ` After a step or two, drag the diamond out of the ${first} shape and the ${second} one falls to pieces.` : ''));
  // (round 29) what the choice Each step does
  if (E.eachHelp) set(E.eachHelp, Sh.each === 'moves'
    ? 'Dots are laid over the picture, one for each starting place, and every step is played on them part by part: where the dots are now, the moves of the rule one after another, the throwing out, and the way back home. Each dot keeps its colour, and a few are drawn larger so that you can follow them. Dots chooses how many there are. (The last move, Slide, is the one that One point calls Add c.)'
    : 'Each step shows only what it leaves. Move by move shows the moves inside each step, played on dots.');
  if (Sh.dials) Sh.dials.sync();
}
function learnShapePaint() {
  const L = LEARN, Sh = LEARN_SHAPE, E = Sh.el, N = LEARN_SHAPE_N;
  if (!learnShapeIsOn() || !E.bar) return;
  if (L.space === 1) { L.space = 2; L.stale = true; }
  const put = (node, text, html) => { if (node.dataset.t !== text) { node.dataset.t = text; if (html) node.innerHTML = text; else node.textContent = text; } };
  const W = learnShapeWords(), three = L.space === 3;
  put(E.where, W.where, true); put(E.say, W.say);
  // (round 29) Move by move: the slider goes through the parts of a step, so the hand needs finer notches
  const fine = learnShapeMovesOn() ? '0.005' : '0.05';
  if (E.pos.step !== fine) E.pos.step = fine;
  if (Math.abs(+E.pos.value - Sh.pos) > 1e-6) E.pos.value = Sh.pos;
  E.pos.setAttribute('aria-valuetext', W.whole ? (W.k === 0 ? 'The start' : `What is left after ${W.k} of ${N} steps`)
    : W.part ? `Step ${W.k + 1} of ${N}, ${W.part.label}, ${Math.round(W.part.t * 100)} percent` : `Step ${W.k + 1} of ${N}, ${Math.round(W.u * 100)} percent`);
  learnShapeChips(W);
  // A low phone window: with the row of Each step and Dots (44 px) the picture's block would be taller than the pin
  // of 85-pin.js holds at the top of the window (PIN_MOST of it), and the picture would scroll away with the page,
  // which it did not before this row was there. In such a window the two choices stand in the panel only.
  // (280: the transport with that row, the gap above it and the pin's 6 px, measured; 236: without the row. Where the
  // picture would not be held even without the row, the row stays.)
  { const pin = typeof PIN !== 'undefined' ? PIN : null, most = typeof PIN_MOST !== 'undefined' ? PIN_MOST : 0.72;
    const low = !!pin && pin.can && pin.want && pin.small > 0 && matchMedia('(max-width: 620px)').matches
      && stage.offsetHeight + 280 > pin.small * most - 2 && stage.offsetHeight + 236 <= pin.small * most;
    if (E.bar.classList.contains('is-low') !== low) E.bar.classList.toggle('is-low', low); }
  // (while Move by move plays, the sentence changes with every part: a reader that speaks the page is not sent each one)
  { const live = Sh.playing && W.part ? 'off' : 'polite'; if (E.say.getAttribute('aria-live') !== live) E.say.setAttribute('aria-live', live); }
  for (const r of E.eachs) r.checked = r.value === Sh.each;
  for (const s of E.dotSels) { if (s.value !== Sh.dots) s.value = Sh.dots; s.disabled = Sh.each !== 'moves'; }
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
  const a = ap(), sig = [Sh.kind, L.space, S.n, S.abs, S.flip, a.id, JSON.stringify(S.param[a.id]), Sh.c, Sh.threeTried, !!Sh.three, Sh.note, Sh.side, Sh.each].join('|');
  if (sig !== Sh.sig) { Sh.sig = sig; learnShapePanel(); }
  L.el.eqNote.hidden = S.eq === 'z^n + c';
  L.el.hint.hidden = !!Sh.note;
  // (over a 3D picture a drag turns the picture, also when it starts on the diamond: there c is moved with its dials)
  put(L.el.hint, three ? (Sh.kind === 'm' ? 'Drag to turn the picture. Scroll or pinch to zoom.' : 'Drag to turn, scroll or pinch to zoom. Move c with its dials.')
    : Sh.kind === 'm' ? 'Scroll or pinch to zoom in, then drag to move the picture.' : 'Drag the diamond to move c. Scroll or pinch to zoom.');
  const V = Sh.view2, D = LEARN_SHAPE_VIEW3, W3 = Sh.view3;
  E.viewReset.hidden = three ? !(W3.yaw !== D.yaw || W3.pitch !== D.pitch || Math.abs(W3.zoom - D.zoom) > 1e-6) : !learnShapeKinds().some(kd => Math.abs(V[kd].zoom - 1) > 1e-6);
  L.el.viewReset.hidden = true;
}

// ---------- the clock
function learnShapeNow() { if (learnShapeIsOn()) { learnShapePaint(); learnShapeDraw(); } }
function learnShapeQueue() { const Sh = LEARN_SHAPE; if (!Sh.raf && learnShapeIsOn()) Sh.raf = requestAnimationFrame(learnShapeFrame); }
function learnShapeFrame(now) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N;
  Sh.raf = 0;
  if (!learnShapeIsOn()) return;
  if (Sh.playing) {
    // (round 29) Move by move plays the parts of a step one after another, and so takes longer for a step
    const TS = learnShapeMovesOn() ? LEARN_SHAPE_MOVE_SECONDS : LEARN_SHAPE_SECONDS;
    const dt = clamp(now - Sh.last, 0, 80), T = TS[LEARN.speed] || TS.normal, stop = Sh.until === null ? N : Math.min(N, Sh.until);
    Sh.last = now;
    if (Sh.dwell > 0) Sh.dwell -= dt;
    else {
      // The next whole step: the one above the slider, and the very one it stands a hair under. (On a 60 Hz screen
      // 66 frames make exactly one step at Normal, 33 at Fast, 132 at Slow, so the sum of the frames can end a
      // rounding error short of the whole step. Counting such a place as the step already reached made Play run
      // on through that step without its rest, one time in ten: measured, out/r26/join/NOTES.md.)
      const edge = Math.floor(Sh.pos) + 1;
      let pos = Sh.pos + dt / (T[0] * 1000);
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
  // a play from end to end that starts at step 0 first rests there, long enough for the sentence of the start
  Sh.playing = true; Sh.dwell = Sh.until === null && Sh.pos <= 1e-9 ? (LEARN_SHAPE_OPENING[LEARN.speed] || LEARN_SHAPE_OPENING.normal) * 1000 : 0;
  Sh.last = performance.now();
  learnShapePaint(); learnShapeQueue();
}
function learnShapeGoto(pos) {
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N;
  learnShapeStop(); Sh.endSide = false;
  pos = clamp(+pos || 0, 0, N);
  // close to a whole step is the whole step (round 29: with Move by move only very close, or the first part of a step could not be gone through by hand)
  Sh.pos = Math.abs(pos - Math.round(pos)) < (learnShapeMovesOn() ? 0.004 : 0.02) ? Math.round(pos) : pos;
  learnShapeNow();
}
// A change made by hand or by a dial: draw now. (learnShapeSeen decides whether it is one of a stream.)
function learnShapeChanged() { learnShapeNow(); }

// ---------- which part of Learn is on show
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
    Sh.drag = null; Sh.pinch = null; Sh.ptr.clear();
  }
  for (const r of E.follows) r.checked = r.value === L.follow;
  const head = L.follow === 'shape' ? 'Learn: a whole shape, step by step' : E.summaryWas;
  if (E.summary.textContent !== head) E.summary.textContent = head;
}
// Follow = One point or A whole shape. byHand: the reader chose it on the page (the first such switch to the
// whole shape in a visit plays the steps once by itself).
function learnShapeFollow(shape, byHand) {
  const L = LEARN, Sh = LEARN_SHAPE;
  shape = !!shape;
  if ((L.follow === 'shape') !== shape) {
    learnVStop(); learnShapeStop();
    // One point keeps its place. The space is one choice for both parts, and choosing another space starts One
    // point's step afresh: so a reader who went from 2D to 3D and back inside the whole shape came home to step 0.
    // Where One point stood is kept on the way in and put back on the way out, when the space is the same again
    // and its points have not been moved. (Coming from the 1D line the space becomes 2D, and the place is not kept.)
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
  if (shape && byHand && L.on && !Sh.played) {
    Sh.played = true;
    if (!learnShapeCalm()) { Sh.pos = 0; learnShapePlay(); }
  }
}
// Called by learnVDefaults: this part back to how it opens. Follow = One point; inside it the Mandelbrot shape,
// step 0, c as Learn opens on the 2D page, the views as they open. (The space, 2D, is put back by learnVDefaults.)
function learnShapeDefaults() {
  const L = LEARN, Sh = LEARN_SHAPE;
  learnShapeStop();
  L.follow = 'point';
  Sh.kind = 'm'; Sh.c = LEARN_V_START[2].c.slice(); Sh.pos = 0; Sh.gone = ''; Sh.thin = ''; Sh.place = null; Sh.above = {};
  Sh.each = 'moves'; Sh.dots = 'some'; Sh.endSide = false; Sh.D = {}; Sh.sig3 = '';      // (round 29)
  Sh.view2 = { m: { x: 0, y: 0, zoom: 1 }, j: { x: 0, y: 0, zoom: 1 } }; Sh.view3 = learnVCopy(LEARN_SHAPE_VIEW3);
  Sh.sig = ''; Sh.seen = '';
  if (Sh.el.speed) Sh.el.speed.value = 'normal';
  if (Sh.dials) Sh.dials.sync();
  learnShapeSync();
}

// ---------- hands on the picture
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
    try { cv.setPointerCapture(e.pointerId); } catch (err) { /* a scripted press has no real pointer */ }
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

// ---------- building it (called once by learnInit, after the one-point part is built)
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
    // (round 29) the names of the parts of one step, with Each step: Move by move
    '<div class="learn-ticks learn-shape-parts" id="learnShapeParts" role="group" aria-label="The parts of one step" hidden></div>' +
    `<div class="learn-track"><input class="learn-pos" id="learnShapePos" type="range" min="0" max="${N}" step="0.05" value="0" aria-label="Step. Drag to take the steps forwards and backwards by hand.">` +
    '<div class="learn-shape-scale"><div class="learn-shape-ticks" id="learnShapeTicks"></div></div></div>' +
    '<div class="learn-shape-row"><div class="learn-btns" role="group" aria-label="Play the steps">' +
    '<button class="btn learn-step" id="learnShapeBack" type="button" aria-label="Back one step" title="Back one step">◀</button>' +
    '<button class="btn learn-play" id="learnShapePlay" type="button" aria-pressed="false">Play</button>' +
    '<button class="btn learn-step" id="learnShapeFwd" type="button" aria-label="Forward one step" title="Forward one step">▶</button>' +
    '<button class="btn" id="learnShapeAgain" type="button" title="Back to the big circle">Start again</button></div>' +
    // (the word "Shape" before the row: without it the row reads Mandelbrot | Julia | Both, and on a phone it can
    // stand right above the lab's own tabs Mandelbrot | Julia | Kleinian | Learn, which mean something else)
    '<div class="learn-shape-pick"><span class="label learn-shape-cap" aria-hidden="true">Shape</span><fieldset class="learn-shape-seg" id="learnShapeKindBar"><legend class="learn-shape-legend">Which shape</legend>' +
    seg('learnShapeKindBar', 'm', 'Mandelbrot', 'Mandelbrot shape') + seg('learnShapeKindBar', 'j', 'Julia', 'Julia shape') + seg('learnShapeKindBar', 'both', 'Both') + '</fieldset>' +
    '<fieldset class="learn-shape-seg" id="learnShapeSpaceBar"><legend class="learn-shape-legend">Space</legend>' +
    seg('learnShapeSpaceBar', '2', '2D', '2D page') + seg('learnShapeSpaceBar', '3', '3D', '3D space') + '</fieldset></div>' +
    // (round 29) how a step is shown: only what it leaves, or the moves inside it, played on dots; and how many dots
    '<div class="learn-shape-pick learn-shape-how"><span class="label learn-shape-cap" aria-hidden="true">Each step</span><fieldset class="learn-shape-seg" id="learnShapeEachBar"><legend class="learn-shape-legend">Each step</legend>' +
    seg('learnShapeEachBar', 'once', 'At once', 'Each step shows only what it leaves') + seg('learnShapeEachBar', 'moves', 'Move by move', 'The moves inside each step, played on dots') + '</fieldset>' +
    '<label class="learn-shape-dots"><span class="label learn-shape-cap">Dots</span><select id="learnShapeDotsBar"><option value="few">Few</option><option value="some">Some</option><option value="many">Many</option></select></label></div></div>');
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
    '<label class="seg"><input type="radio" name="learnFollow" id="learnFollowPoint" value="point" checked><span>One point</span></label>' +
    '<label class="seg"><input type="radio" name="learnFollow" id="learnFollowShape" value="shape"><span>A whole shape</span></label>');
  follow.id = 'learnFollow';
  body.prepend(follow);
  E.follows = [...follow.querySelectorAll('input')];
  follow.addEventListener('change', e => { if (e.target.name === 'learnFollow') learnShapeFollow(e.target.value === 'shape', true); });
  // (the words of the note and of the helps are set by learnShapePanel: some of them follow the power and the space)
  const note = make('p', 'note learn-only-shape');
  note.id = 'learnShapeIntro';
  intro.after(note);
  E.intro = note;
  const kind = make('div', 'sec-inner learn-only-shape', '<fieldset class="learn-kind" id="learnShapeKind"><legend class="label">Which shape</legend>' +
    seg('learnShapeKind', 'm', 'Mandelbrot shape') + seg('learnShapeKind', 'j', 'Julia shape') + seg('learnShapeKind', 'both', 'Both') + '</fieldset>' +
    '<div class="learn-kind-help"><p class="note"><b>Mandelbrot shape.</b> Each point of the picture is tried as the number c, the one that is added at every step. Its dot always starts at the centre.</p>' +
    '<p class="note"><b>Julia shape.</b> <span id="learnShapeHelpJ"></span></p>' +
    '<p class="note"><b>Both.</b> <span id="learnShapeHelpBoth"></span></p></div>');
  el.eqNote.after(kind);
  E.helpJ = kind.querySelector('#learnShapeHelpJ'); E.helpBoth = kind.querySelector('#learnShapeHelpBoth');
  // (round 29) Each step: At once | Move by move, and Dots: here with a line of help, and in the transport
  const each = make('div', 'sec-inner learn-only-shape', '<fieldset class="learn-follow" id="learnShapeEach"><legend class="label">Each step</legend>' +
    seg('learnShapeEach', 'once', 'At once') + seg('learnShapeEach', 'moves', 'Move by move') + '</fieldset>' +
    '<p class="note" id="learnShapeEachHelp"></p>' +
    '<div class="field"><label class="label" for="learnShapeDots">Dots</label><select id="learnShapeDots"><option value="few">Few</option><option value="some">Some</option><option value="many">Many</option></select></div>');
  each.id = 'learnShapeEachBlock';
  kind.after(each);
  E.eachHelp = each.querySelector('#learnShapeEachHelp'); E.parts = E.bar.querySelector('#learnShapeParts');
  E.eachs = [...each.querySelectorAll('input[name=learnShapeEach]'), ...E.bar.querySelectorAll('input[name=learnShapeEachBar]')];
  E.dotSels = [each.querySelector('#learnShapeDots'), E.bar.querySelector('#learnShapeDotsBar')];
  const pickEach = e => { if (e.target.name === 'learnShapeEach' || e.target.name === 'learnShapeEachBar') LEARN.shape.set({ each: e.target.value }); };
  each.addEventListener('change', pickEach); E.bar.querySelector('#learnShapeEachBar').addEventListener('change', pickEach);
  for (const s of E.dotSels) s.addEventListener('change', () => LEARN.shape.set({ dots: s.value }));
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
  // what belongs to one point only is put away while the whole shape is on (by the style sheet: nobody's hidden state is touched)
  for (const n of [intro, el.panel.querySelector('#learnChecks'), el.hiddenNote, el.panel.querySelector('#learnDials'), el.panel.querySelector('#learnZero').parentNode,
    el.panel.querySelector('#learnMovesHead'), el.moves, el.note, el.notice]) n.classList.add('learn-only-point');
  el.panel.querySelector('#learnSpace1').closest('.seg').classList.add('learn-space-1');
  E.kinds = [...kind.querySelectorAll('input[name=learnShapeKind]'), ...E.bar.querySelectorAll('input[name=learnShapeKindBar]')];
  E.spaces = [...E.bar.querySelectorAll('input[name=learnShapeSpaceBar]')];
  const pickKind = e => { if (e.target.name === 'learnShapeKind' || e.target.name === 'learnShapeKindBar') LEARN.shape.set({ kind: e.target.value }); };
  kind.addEventListener('change', pickKind); E.bar.querySelector('#learnShapeKindBar').addEventListener('change', pickKind);
  // the c of the Julia shape: dials, the c of the Julia tab, and a few named values
  const store = {};
  ['x', 'y', 'z'].forEach((axis, i) => Object.defineProperty(store, 'c' + axis, { get: () => Sh.c[i], set: v => { Sh.c[i] = v; }, enumerable: true }));
  const pd = (key, label, when) => ({ type: 'dial', key, label, min: -2, max: 2, step: 0.01, lo: -8, hi: 8, when });
  Sh.dials = buildControls('learnShapeDials', [
    pd('cx', 'The point <span class="asis">c</span>, along x'), pd('cy', 'The point <span class="asis">c</span>, along y'),
    pd('cz', 'The point <span class="asis">c</span>, along z', () => L.space === 3),
  ], store, learnShapeChanged, { idPrefix: 'learnShape-', group: 'learn' });
  const cs = cBlock.querySelector('#learnShapeCs');
  cBlock.querySelector('#learnShapeJuliaC').addEventListener('click', () => { LEARN.shape.set({ c: S.c.slice() }); learnVShowStage(); });
  E.named = LEARN_SHAPE_NAMED.map(v => {
    // "the rabbit (c at x −0.12, y 0.74)": the name, shown where it is true, and the value (learnShapePanel)
    const b = make('button', 'btn learn-shape-value', '<span class="learn-shape-name"></span><span></span>');
    b.type = 'button'; b.firstChild.textContent = v.name + ' '; b.lastChild.textContent = v.text;
    b.addEventListener('click', () => { LEARN.shape.set({ c: v.c.slice() }); learnVShowStage(); });
    cs.appendChild(b);
    return b;
  });
  learnShapePanel();
  learnShapeSync();
}

// ---------- for tests and the console
// set({ on, kind, space, c, pos, each, dots }): any of them. on: true switches Learn on as well, with Follow = A whole shape.
// (round 29) each: 'once' | 'moves' (Each step: At once | Move by move); dots: 'few' | 'some' | 'many'.
function learnShapeSet(o) {
  const L = LEARN, Sh = LEARN_SHAPE;
  o = o || {};
  if (o.on !== undefined) {
    if (o.on && !L.on) learnVSetOn(true);
    learnShapeFollow(!!o.on, false);
  }
  if (o.kind !== undefined && ['m', 'j', 'both'].includes(o.kind)) Sh.kind = o.kind;
  if (o.each !== undefined && ['once', 'moves'].includes(o.each) && o.each !== Sh.each) { Sh.each = o.each; Sh.endSide = false; Sh.sig3 = ''; }
  if (o.dots !== undefined && ['few', 'some', 'many'].includes(o.dots)) Sh.dots = o.dots;
  if (o.c) Sh.c = [0, 1, 2].map(i => (isFinite(+o.c[i]) ? clamp(+o.c[i], -8, 8) + 0 : 0));
  if (o.pos !== undefined && isFinite(+o.pos)) { learnShapeStop(); Sh.pos = clamp(+o.pos, 0, LEARN_SHAPE_N); }
  if (o.space !== undefined && [2, 3].includes(+o.space) && +o.space !== L.space) L.set({ space: +o.space });
  else if (learnShapeIsOn()) learnShapeNow();
  return learnShapeState();
}
function learnShapeState() {
  const L = LEARN, Sh = LEARN_SHAPE, on = learnShapeIsOn();
  // what is read back is the finished picture: a fine one that was still waiting is drawn now
  if (on && (Sh.rest || (Sh.raf && !Sh.playing))) { clearTimeout(Sh.rest); Sh.rest = 0; if (!Sh.drag) Sh.hot = 0; learnShapeNow(); }
  // (while this part is not on show nothing is drawn: where the pictures would stand is worked out for the answer)
  if (!on && stage.clientWidth) Sh.panes = learnShapePanes(stage.clientWidth, stage.clientHeight);
  const W = learnShapeWords(), has3 = typeof learnShape3d !== 'undefined' && !!learnShape3d;
  return {
    on, kind: Sh.kind, space: L.space, c: Sh.c.slice(), pos: Sh.pos, step: W.k, playing: Sh.playing, steps: LEARN_SHAPE_N,
    sentence: W.say, note: on ? Sh.note : '', panes: Sh.panes.map(P => ({ kind: P.kind, x: P.x, y: P.y, w: P.w, h: P.h })),
    threeOk: has3 && !(Sh.threeTried && !Sh.three) && (typeof learnShape3d.ok !== 'function' || !!learnShape3d.ok()),
    // extras, for the notes and the checks
    follow: L.follow, quality: Sh.quality, side: Sh.side, ms: Object.assign({}, Sh.ms), three: Sh.last3,
    // (round 29) each, dots: the two new choices. part: the part of the step being played (null at a whole step and
    // with At once): its key ('out', 'move', 'gone', 'home'), its name, its number i of n, how far through it (t), and
    // for a move its number. parts: the names of the parts of one step, in order. shown: picture by picture, how many
    // dots there are and how many are on show at this step.
    each: Sh.each, dots: Sh.dots, part: W.part ? { key: W.part.key, label: W.part.label, i: W.part.i, n: W.part.n, t: W.part.t, move: W.part.key === 'move' ? W.part.j : -1 } : null,
    parts: Sh.each === 'moves' ? learnShapeMoves().chips.slice() : [],
    shown: on && Sh.each === 'moves' ? learnShapeKinds().map(kd => { const D = learnShapeDots(kd); return { kind: kd, all: D.dots.length, on: D.dots.filter(d => d.out > W.k).length }; }) : [],
    // gone, thin: what the pictures on show told the words (learnShapeDraw). thick: the bite of each step in pixels,
    // picture by picture (2D). above: what a 3D shape seen from straight above told them (thick: in units).
    gone: on ? Sh.gone : '', thin: on ? Sh.thin : '', where: W.where.replace(/<[^>]+>/g, ''),
    thick: !on || L.space === 3 ? [] : Sh.panes.map(P => { const M = Sh.maps[P.kind]; return M && M.thick ? Array.from(M.thick, t => +t.toFixed(3)) : null; }),
    above: !on || L.space !== 3 ? [] : learnShapeKinds().filter(kd => Sh.above[kd]).map(kd => { const A = Sh.above[kd]; return { kind: kd, done: A.done, ms: A.data ? +A.data.ms.toFixed(1) : null, left: A.data ? Array.from(A.data.left) : null, thick: A.data ? Array.from(A.data.thick, t => +(t * A.data.unit).toFixed(4)) : null }; }),
    view2: learnVCopy(Sh.view2), view3: learnVCopy(Sh.view3), diamonds: Sh.panes.map(P => (P.dia ? P.dia.slice(0, 2) : P.at3 ? P.at3.slice() : null)),
  };
}
// (Round 29.) The dots of "Each step: Move by move", for the checks. kind: 'm' or 'j' (in Both each picture has its own).
// dots(kind): every dot of the picture. start: its starting place; out: the step at which it is thrown out
// (steps + 1: still in at the end); places[i][j]: where dot i is after j steps, by the lab's own rule (the last
// one is the place outside, when it is thrown out); c: the number it adds at every step; big: the ones drawn larger.
function learnShapeDotsOut(kind) {
  const D = learnShapeDots(kind === 'j' ? 'j' : 'm');
  return { kind: D.kind, space: D.three ? 3 : 2, gap: D.h, n: D.dots.length, start: D.dots.map(d => d.p.slice()), out: D.dots.map(d => d.out),
    places: D.dots.map(d => d.pts.map(v => v.slice())), c: D.dots.map(d => d.c.slice()), big: D.big.slice(), colour: D.dots.map(d => d.col),
    // (carry: for an entry whose orbit carries something, what each dot carries when each of its steps begins)
    carry: D.dots.map(d => (d.carry ? JSON.parse(JSON.stringify(d.carry)) : null)) };
}
// chain(kind, k): step k + 1 as it is played. on: the dots that take it (numbers into dots()); joints[n][j]: where
// the n-th of them stands when the j-th move begins (the last: where the step ends, the exact place after k + 1
// steps); end[n]: where the chain of moves itself ends, before that place is taken; truth[n]: the lab's own rule;
// gap: the largest difference between end and truth (as a share of the place's distance from the centre, or of 1).
function learnShapeChainOut(kind, k) {
  kind = kind === 'j' ? 'j' : 'm'; k = clamp(Math.round(+k) || 0, 0, LEARN_SHAPE_N - 1);
  const D = learnShapeDots(kind), ch = learnShapeChain(kind, k);
  return { kind, k, names: ch.M.names.slice(), on: ch.list.slice(), thrown: ch.thrown, gap: ch.gap, moved: ch.moved.slice(), centre: ch.centre,
    joints: ch.list.map(i => ch.pos[i].map(v => v.slice())), end: ch.list.map(i => ch.raw[i].slice()), truth: ch.list.map(i => D.dots[i].pts[k + 1].slice()) };
}
// dotsAt(kind, pos): the dots on show at the slider's position pos (left out: where it stands), each where the
// picture draws it: { i, at: [x, y, z], going } (going: the step under way throws it out). Also the part.
function learnShapeDotsAt(kind, pos) {
  kind = kind === 'j' ? 'j' : 'm';
  const Sh = LEARN_SHAPE, N = LEARN_SHAPE_N, at = pos === undefined ? Sh.pos : clamp(+pos || 0, 0, N), k = Math.min(N, Math.floor(at + 1e-9)), u = k >= N ? 0 : clamp(at - k, 0, 1);
  if (!learnShapeMovesOn()) return { kind, pos: at, step: k, part: null, dots: [] };      // Each step: At once draws no dots
  const D = learnShapeDots(kind), ph = u > 1e-9 ? learnShapePart(u) : null, ch = ph ? learnShapeChain(kind, k) : null, te = ph ? learnShapeGlide(ph.t) : 0, list = [];
  D.dots.forEach((d, i) => {
    if (!(d.out > k)) return;
    const going = !!ph && d.out === k + 1;
    if (going && ph.key === 'home') return;
    list.push({ i, at: (ph && ch.pos[i] ? learnShapeDotAt(D, ch, i, ph, te) : d.p).slice(), going });
  });
  return { kind, pos: at, step: k, part: ph ? { key: ph.key, name: ph.name, i: ph.i, n: ph.n, t: ph.t } : null, dots: list };
}
// numbersAt(kind, points): for each point [x, y] of the 2D page, the number the fine picture's own arithmetic
// (learnShapeMap, the code the picture is drawn from) gives it: the step at which it is thrown out.
function learnShapeNumbersAt(kind, pts) {
  const one = new Uint8Array(1);
  return (pts || []).map(p => learnShapeMap(kind === 'j' ? 'j' : 'm', LEARN_SHAPE.c, S.n, S.abs, S.flip, +p[0], +p[1], 0, 0, 1, 1, LEARN_SHAPE_N, one)[0]);
}
LEARN.shape = {
  set: o => learnShapeSet(o),
  state: () => learnShapeState(),
  play: () => { if (!learnShapeIsOn()) learnShapeSet({ on: true }); learnShapePlay(); return learnShapeState(); },
  pause: () => { learnShapeStop(); learnShapeNow(); return learnShapeState(); },
  goto: pos => { learnShapeGoto(pos); return learnShapeState(); },
  out2: (p, kind, c, maxK) => learnShapeOut2(p, kind, c, maxK),
  mask2: (kind, size, half, maxK, opt) => learnShapeMask2(kind, size, half, maxK, opt),
  glass: LEARN_SHAPE_GLASS,      // the numbers of the 3D picture's glass, for trying others (then: set({}) draws again)
  // (round 29) the dots of Each step: Move by move (see learnShapeDotsOut, learnShapeChainOut, learnShapeDotsAt)
  dots: kind => learnShapeDotsOut(kind), chain: (kind, k) => learnShapeChainOut(kind, k), dotsAt: (kind, pos) => learnShapeDotsAt(kind, pos),
  playPart: i => { learnShapePlayPart(i); return learnShapeState(); },
  numbersAt: (kind, pts) => learnShapeNumbersAt(kind, pts),      // 2D: the fine picture's own numbers at any points
  // what the last redraw took (ms; see LEARN_SHAPE.ms) and where the slider stood, read without drawing anything
  timing: () => Object.assign({ pos: LEARN_SHAPE.pos, playing: LEARN_SHAPE.playing }, LEARN_SHAPE.ms),
  // 3D: the picture's own program asked about a level cut of the big ball (learnShape3d's slice(), with the c on show)
  slice3: (kind, opt) => (LEARN_SHAPE.three && typeof LEARN_SHAPE.three.slice === 'function' ? LEARN_SHAPE.three.slice(kind === 'j' ? 'j' : 'm', LEARN_SHAPE.c, opt) : null),
  quiet: LEARN_SHAPE_QUIET, moveSeconds: LEARN_SHAPE_MOVE_SECONDS,
};
