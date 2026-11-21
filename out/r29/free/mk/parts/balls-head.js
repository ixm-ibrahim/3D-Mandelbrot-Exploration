// ---------- Balls on balls: the second group of the Kleinian view (round 27; round 28: the second sphere's size;
// round 29: the two dials are free of each other).
// Not an approach and not a rule "square, then add c": a picture made only of slides by whole numbers and sphere
// inversions. Its state is five numbers in S.k: group (0 the group that was always there, 1 this one), bt (the dial
// t = top / 2), brho (the radius of the second sphere: 0.02 to 1), bgrid (0 square grid, 1 honeycomb grid, 2 a line
// only) and bit (rounds of the recipe).
//
// The recipe, in the object's own coordinates m, with top = 2t and rho = brho (rho = 1 is out/r25/klein/tree.py):
//   repeat: if m.z < 0 or m.z > top: INSIDE. Slide (m.x, m.y) by the nearest whole number of the grid.
//           If |m| < 1: m -> m / |m|^2                              (the first sphere: radius 1 about (0, 0, 0)).
//           Else if |m - (0, 0, top)| < rho: m -> (0, 0, top) + rho^2 (m - (0, 0, top)) / |m - (0, 0, top)|^2
//                                                                   (the second sphere: radius rho about (0, 0, top)).
//           Else: OUTSIDE.
//   A point that is still undecided when the rounds run out counts as INSIDE.
// One sphere inversion at the start (centre (0, 0, 1) in m, radius k, k^2 = 1.05) brings the picture into the lab's
// frame: picture x along the chain, picture y up in the flat plane, picture z out of the flat plane. The middle ball
// is k^2 wide and its two big neighbours k^2 / (top - 1), whatever rho is: the dial "Size of the neighbours" shows
// p = 100 / (top - 1). The first sphere is the mirror x -> -x of the picture, so the picture is always its own
// mirror image left to right.
// The two spheres touch at top = 1 + rho, that is at p = 100 / rho. No two balls cut into each other when rho = 1 and
// p <= 100 (round 27), or when rho <= 1/2 and p rho <= 100 (round 28: the copies of the second sphere at
// neighbouring whole numbers do not cut into each other either). Round 29: each dial sets its own number and
// nothing else, so every other pair of numbers can be had as well. Where p rho > 100 the two spheres of the recipe
// cut into each other, and with rho between 1/2 and 1 the copies of the second sphere do; the picture is then
// whatever the plain recipe above gives, balls that run into one another and round holes between them.
const BALLS_K2 = 1.05, BALLS_T = 1.4, BALLS_ROUNDS = 16, BALLS_ROUNDS_MIN = 1, BALLS_ROUNDS_FEW = 5, BALLS_S3 = Math.sqrt(3);
// the second sphere: from BALLS_RHO_MIN of the first to as large as it; up to BALLS_RHO_HALF its copies at
// neighbouring whole numbers do not cut into each other. (t: kept above 1/2 by a hair, so that top - 1 > 0.)
const BALLS_RHO_MIN = 0.02, BALLS_RHO_HALF = 0.5, BALLS_T_MIN = 0.5001;
const BALLS_NAME = 'Balls on balls', BALLS_TAG = 'a cousin of the flat picture: no c, no power';
const BALLS_GRIDS = [[0, 'Square grid (four-fold)'], [1, 'Honeycomb grid (six-fold)'], [2, 'A line only (buds only round the flat picture)']];
const BALLS_NOTE = 'Made only of slides by whole numbers and sphere inversions, so every body is an exact ball. It is a cousin of the flat picture: its flat cut is a chain of circles. It has no c and no power.';
const ballsOn = () => S.k.group === 1;                 // this group is the one the Kleinian view holds
const ballsShown = () => S.mode === 'k' && ballsOn();  // and it is on show
const ballsGridId = g => (g === 1 || g === 'hex' || g === 'eisen' ? 1 : g === 2 || g === 'line' ? 2 : 0);
// The second sphere's radius as the programs use it: the number in the state, held to 0.02 ... 1 (1 for a state
// that holds nothing). Nothing else changes it: not the size of the neighbours either.
function ballsRho(r = S.k.brho) {
  const v = r === undefined || r === null || r === '' ? NaN : +r;
  return Number.isFinite(v) ? Math.min(1, Math.max(BALLS_RHO_MIN, v)) : 1;
}
// t as the programs use it: the number in the state as it stands (above 1/2 by a hair; 1 for a state that holds
// nothing). The second sphere does not hold it up any more.
const ballsT = (t = S.k.bt) => Math.max(BALLS_T_MIN, +t || 1);
// Which of the three program texts draws a pair of numbers (40-render.js builds each under its own key):
//   'balls'   two equal spheres that are apart or touch (rho = 1, t >= 1): GL_BALLS, round 27's text;
//   'balls2'  a second sphere of half the first's size or less, apart from the first or touching it: GL_BALLS_RHO,
//             round 28's text;
//   'balls3'  every other pair, GL_BALLS_FREE: the two spheres cut into each other, or rho lies between 1/2 and 1.
// Every pair Version 21 could reach lies in the first two, so its pictures are drawn by the programs that drew them.
const ballsApart = (t, rho) => 2 * t - 1 - rho >= -1e-9;   // (the two spheres are apart, or touch)
const ballsKind = (t = ballsT(), rho = ballsRho()) => (rho === 1 && t >= 1 ? 'balls' : rho <= BALLS_RHO_HALF && ballsApart(t, rho) ? 'balls2' : 'balls3');
// t as a program is handed it (uBT). 'balls2' was written for spheres that never cut: a t that is a rounding hair
// under the touching value is handed over as the touching value, as it always was.
const ballsTOf = (kind, t = ballsT(), rho = ballsRho()) => (kind === 'balls2' ? Math.max((1 + rho) / 2, t) : t);
// The two spheres touch: the chain never ends. (As the programs see the numbers.)
const ballsTouch = (t = S.k.bt, rho = ballsRho()) => (rho === 1 ? !(ballsT(t) > 1) : !(2 * ballsT(t) - 1 - rho > 1e-9));
// How the two spheres stand to each other as the two dials SHOW their numbers: -1 apart, 0 they touch, 1 they cut
// into each other. The dials show two decimals each, so a product of the two shown numbers that could be 100 x 100
// within their rounding counts as touching (33.33 and 300 do: the chain is then some 250 long and leaves the picture
// on both sides, as an endless one does). Two equal spheres: 100 as the dial shows it is touching, more is cutting.
function ballsMeet(t = S.k.bt, rho = ballsRho()) {
  t = ballsT(t);
  if (rho === 1) return t > 1 ? -1 : +ballsShare(t).toFixed(2) > 100 ? 1 : 0;
  if (Math.abs(2 * t - 1 - rho) <= 1e-9) return 0;
  const p = ballsShare(t), r = 100 * rho, over = p * r - 10000, tol = 0.005 * (p + r);
  return over > tol ? 1 : over >= -tol ? 0 : -1;
}
// The dial shows t the way the eye meets it: the width of the two big neighbours as a share of the middle ball.
const ballsShare = t => 100 / (2 * t - 1);
const ballsFromShare = p => (Math.abs(p - ballsShare(BALLS_T)) < 0.06 ? BALLS_T : Math.max(BALLS_T_MIN, 0.5 * (100 / Math.max(p, 1e-6) + 1)));
// The dial "Second sphere" shows 100 rho, with two decimals.
const ballsRhoShown = () => +(100 * ballsRho()).toFixed(2);
const ballsRhoFrom = v => Math.min(1, Math.max(BALLS_RHO_MIN, v / 100));
// The two dials. Each sets its own number and nothing else (round 29: Version 21 made the second sphere smaller by
// itself where the two spheres would have cut into each other; the user asked for that rule to go).
// (The size counts as it came while the two spheres are equal, as it always did, and as the dial shows it, with two
//  decimals, beside a smaller second sphere, as in Version 21.)
function ballsSetShare(p) { S.k.bt = ballsFromShare(ballsRho() < 1 ? +(+p).toFixed(2) : +p); }
// (as the dial shows it: a typed 49.999 reads 50 and is 50)
function ballsSetRho(v) { S.k.brho = ballsRhoFrom(+(+v).toFixed(2)); }
// The numbers the distance is made from while the two spheres are apart (see GL_BALLS for rho = 1, GL_BALLS_RHO for
// a smaller second sphere and GL_BALLS_FREE for one between 1/2 and 1):
// HB, HT the two hull balls; the spindle's circle (centre (a, zm), radius R, d2 = R^2 - a^2) and whether it is used;
// end = z2 - 1, where z2 is the upper of the two fixed points on the middle line (0 when the spheres touch).
function ballsHulls(t, rho, any) {
  if (rho === 1 && !any) { const H = t - Math.sqrt(Math.max(t * t - 1, 0)), s2 = t * t - 1; return { HB: H, HT: H, zm: t, d2: s2, a: 0.25 - s2, R: 0.25 + s2, on: t < BALLS_SPINDLE_T, end: t + Math.sqrt(Math.max(s2, 0)) - 1 }; }
  // (written so that nothing large is taken from something large: D = s - 2, which is 0 when the spheres touch)
  // (`any`: these lines also for two equal spheres, as GL_BALLS_FREE writes them)
  const top = 2 * t, gap = Math.max(top - 1 - rho, 0), D = gap * (top - 1 + rho) / top, sq = Math.sqrt(D * (D + 4));
  const HB = 1 / (1 + 0.5 * (D + sq)), HT = rho * rho / (top - HB), zm = 1 + 0.5 * D, d2 = 0.25 * D * (D + 4), w = Math.min(0.5, top - zm + rho);
  return { HB, HT, zm, d2, a: (w * w - d2) / (2 * w), R: (w * w + d2) / (2 * w), on: d2 < 3, end: 0.5 * (D + sq) };
}
// How far the chain reaches from the middle of the picture, along x (Infinity where the two spheres touch or cut into
// each other: there is no end to frame). The chain runs out at the two fixed points on the middle line, which the
// frame carries to x = +-reach.
function ballsReach(t = S.k.bt, rho = ballsRho()) {
  t = ballsT(t);
  if (rho === 1) return t > 1 ? BALLS_K2 / (t + Math.sqrt(t * t - 1) - 1) + BALLS_K2 / 2 : Infinity;
  return 2 * t - 1 - rho > 1e-9 ? BALLS_K2 / ballsHulls(t, rho).end + BALLS_K2 / 2 : Infinity;
}

// The slide: the whole number of the grid nearest to (x, y), as [a, b] to take away.
function ballsNearest(grid, x, y) {
  if (grid === 2) return [Math.round(x), 0];
  if (grid === 0) return [Math.round(x), Math.round(y)];
  const b0 = Math.round(y / (BALLS_S3 / 2));
  let best = null, bd = Infinity;
  for (let j = -1; j <= 1; j++) {
    const b = b0 + j, a = Math.round(x + b / 2), px = a - b / 2, py = b * BALLS_S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py);
    if (d < bd) { bd = d; best = [px, py]; }
  }
  return best;
}
// The inside test, in JavaScript: the twin of the shader (and, for rho = 1, of tree.py). Picture coordinates.
// opts = { t, grid ('square' | 'hex' | 'line', or 0 | 1 | 2), rounds, rho }; what is left out is read from the page.
// (t and rho, given here or read from the page, are used as they stand: nothing holds one by the other.)
function ballsInside(x, y, z, opts) {
  const o = opts || {}, rho = o.rho === undefined ? ballsRho() : +o.rho, r2 = rho * rho;
  const t = o.t === undefined ? ballsT() : +o.t, grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t;
  const ux = y, uy = z, uz = x - BALLS_K2 / 2;
  let d = ux * ux + uy * uy + uz * uz;
  if (!(d > 0)) d = 1e-300;
  let mx = BALLS_K2 * ux / d, my = BALLS_K2 * uy / d, mz = 1 + BALLS_K2 * uz / d;
  for (let i = 0; i < rounds; i++) {
    if (mz < 0 || mz > top) return true;
    const n = ballsNearest(grid, mx, my);
    mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / (rb > 0 ? rb : 1); mx *= s; my *= s; mz *= s; }
    else if (rt < r2) { const s = r2 / (rt > 0 ? rt : 1); mx *= s; my *= s; mz = top + (mz - top) * s; }
    else return false;
  }
  return true;
}
// Room that is certain round the line that joins the two walls (see "the spindle" above GL_BALLS, and above
// GL_BALLS_RHO for a smaller second sphere): how far the point m, which the recipe has just called OUTSIDE, stands
// inside the spindle. Below 0: not inside it. Used while the neighbours are large (rho = 1: t under BALLS_SPINDLE_T;
// rho < 1: delta^2 under 3, which is the same line); for smaller ones the other number is always the larger.
const BALLS_SPINDLE_T = 2;
// (the circle's radius - the distance from the circle's centre, written as the shaders write it)
function ballsSpindle(m, t, rho, hu) {
  if (!hu.on) return -1;
  const q = Math.hypot(m[0], m[1]);
  if (rho === 1) { const s2 = t * t - 1, dz = m[2] - t; return (s2 + q * (0.5 - 2 * s2 - q) - dz * dz) / (0.25 + s2 + Math.hypot(q - 0.25 + s2, dz)); }
  const dz = m[2] - hu.zm;
  return (hu.d2 + q * (2 * hu.a - q) - dz * dz) / (hu.R + Math.hypot(q - hu.a, dz));
}
// The side spindle (a second sphere of half the first's size or less; see above GL_BALLS_RHO): the room that is
// certain round the line that joins the second sphere's centre to its copy at the next whole number, both on the top
// wall. { c2, a, R } is its circle, for the grid: centre (0, a), radius R in the half-plane (along that line from the
// middle point between the two centres, distance from the line), c2 = R^2 - a^2 = 1/4 - rho^2.
function ballsSide(top, rho, grid, HB) {
  const c2 = Math.max(0.25 - rho * rho, 0), w = Math.min(top - HB, (grid === 1 ? BALLS_S3 / 2 : 1) - rho);
  return { c2, a: (w * w - c2) / (2 * w), R: (w * w + c2) / (2 * w) };
}
// The whole number next to the middle one that the point m leans towards: [along it, across it].
function ballsLean(m, grid) {
  let al = Math.abs(m[0]), ac = m[1];
  if (grid === 0 && Math.abs(m[1]) > al) { al = Math.abs(m[1]); ac = m[0]; }
  if (grid === 1) {
    const d1 = Math.abs(0.5 * m[0] + 0.5 * BALLS_S3 * m[1]), d2 = Math.abs(0.5 * m[0] - 0.5 * BALLS_S3 * m[1]);
    if (d1 > al) { al = d1; ac = 0.5 * m[1] - 0.5 * BALLS_S3 * m[0]; }
    if (d2 > al) { al = d2; ac = 0.5 * m[1] + 0.5 * BALLS_S3 * m[0]; }
  }
  return [al, ac];
}
// How far the point m (in the middle cell, ht under the top wall) stands inside it. Below 0: not inside it.
function ballsSideRoom(m, ht, grid, sd) {
  const [al, ac] = ballsLean(m, grid), v = al - 0.5, q = Math.hypot(ac, ht);
  return (sd.c2 - v * v + q * (2 * sd.a - q)) / (sd.R + Math.hypot(v, q - sd.a));
}
//__FREE_TWIN__
// The distance the shader hands the ray marcher, in JavaScript (the part that does not depend on the picture: see
// "free" in GL_BALLS). Negative inside a ball. For the checks. With opts.parts it returns both numbers the estimate is the
// smaller of: [the true distance to the nearest ball the search met, the length that is certainly free of balls].
// opts as for ballsInside. The length that is certainly free is worked out the way the program for that pair of
// numbers works it out (ballsKind): GL_BALLS, GL_BALLS_RHO or GL_BALLS_FREE.
function ballsEstimate(x, y, z, opts) {
  const o = opts || {}, rho = o.rho === undefined ? ballsRho() : +o.rho, r2 = rho * rho;
  const tAsk = o.t === undefined ? ballsT() : +o.t, kind = ballsKind(tAsk, rho), t = ballsTOf(kind, tAsk, rho);
  const grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t;
  const fr = kind === 'balls3' ? ballsFreeSet(t, rho, grid) : null, hu = fr ? fr.hu : ballsHulls(t, rho), HB = hu.HB, HT = hu.HT;
  // "the rest": how far from a wall the buds reach that do not stand at a whole number (on the top wall of a smaller
  // second sphere: rho^2 HT, for all three grids)
  const restB = grid === 0 ? HB / 2 : grid === 1 ? HB / 3 : HB / 4, restT = rho === 1 ? restB : r2 * HT;
  // (rho < 1: and that rest keeps within rT of the second sphere's centre: see GL_BALLS_RHO)
  const rT = Math.min(rho, 2 * r2 / (1 + Math.sqrt(Math.max(1 - 4 * r2, 0))) + restT);
  // (rho <= 1/2: and the side spindle, between the second sphere and its copy at the next whole number)
  const sd = rho <= BALLS_RHO_HALF ? ballsSide(top, rho, grid, HB) : null;
  const pearl = (h, D, kk) => (h > 0 ? 2 * h / (1 + Math.sqrt(1 + kk * h * Math.max(D, 0))) : h);
  const u = [y, z, x - BALLS_K2 / 2], d2 = Math.max(dot(u, u), 1e-300);
  let DF = BALLS_K2 / d2, m = [DF * u[0], DF * u[1], 1 + DF * u[2]], W = [0, 0, 1], best = 1e9;
  for (let i = 0; i < rounds; i++) {
    const n = ballsNearest(grid, m[0], m[1]);
    m[0] -= n[0]; m[1] -= n[1]; W[0] -= n[0]; W[1] -= n[1];
    const L2 = Math.max(dot(sub(m, W), sub(m, W)), 1e-300), kk = 4 / L2, hb = m[2], ht = top - m[2];
    const cand = Math.min(pearl(hb, W[2], kk), pearl(ht, top - W[2], kk)) / DF;
    best = Math.min(best, cand);
    if (hb < 0 || ht < 0) return o.parts ? [best, best] : best;
    const mt = [m[0], m[1], m[2] - top], rb = dot(m, m), rt = dot(mt, mt);
    if (rb < 1) { const s = 1 / Math.max(rb, 1e-300); m = scl(m, s); W = scl(W, 1 / Math.max(dot(W, W), 1e-300)); DF *= s; }
    else if (rt < r2) {
      const s = r2 / Math.max(rt, 1e-300), Wt = [W[0], W[1], W[2] - top], w = r2 / Math.max(dot(Wt, Wt), 1e-300);
      m = [mt[0] * s, mt[1] * s, top + mt[2] * s]; W = [Wt[0] * w, Wt[1] * w, top + Wt[2] * w]; DF *= s;
    } else if (fr) {
      // the pairs of numbers that GL_BALLS_FREE draws ([free, the first buds behind the two mirrors])
      const r = ballsFreeRoom(m, W, DF, fr, rounds - 1 - i);
      best = Math.min(best, r[1]);
      return o.parts ? [best, r[0]] : Math.min(best, r[0]);
    } else {
      const cb = Math.hypot(m[0], m[1], hb - HB / 2) - HB / 2, ct = Math.hypot(m[0], m[1], ht - HT / 2) - HT / 2;
      const lo = grid === 2 ? Math.hypot(m[1], hb) : hb, hi = grid === 2 ? Math.hypot(m[1], ht) : ht;
      const hiR = rho === 1 ? hi - restT : Math.max(hi - restT, Math.sqrt(rt) - rT);
      const e = Math.max(Math.min(cb, ct, Math.min(lo - restB, hiR)), ballsSpindle(m, t, rho, hu), sd ? ballsSideRoom(m, ht, grid, sd) : -1, 0), L = Math.sqrt(L2);
      const free = e * L / ((L + e) * DF);
      return o.parts ? [best, free] : Math.min(best, free);
    }
  }
  return o.parts ? [-1e-7, -1e-7] : -1e-7;
}
// The start view: the whole chain in the picture, seen from a little above the flat plane so that the buds off the
// flat picture show. { yaw, pitch, dist (at the starting field of view), h (span of the 2D view), room }.
const BALLS_FAR = 40;   // a chain that reaches further than this from the middle is not framed whole
// From how far (at the starting field of view) the ball of radius r about the picture point c is wholly in a picture
// `asp` times as wide as high, for an eye that looks at the middle from the direction (yaw, pitch), with 8 % of
// air round it. Exact for a ball: the eye's four side planes, each kept r away from the centre. (The fixer of
// round 28: the rule of thumb below measured the picture's height against a ball in the MIDDLE of the picture. A big
// neighbour stands beside the middle and nearer to the eye, so in a low, wide picture, a phone held sideways, it ran
// out of the lower edge.)
function ballsSee(c, r, asp, yaw, pitch) {
  const cp = Math.cos(pitch), off = [cp * Math.cos(yaw), cp * Math.sin(yaw), Math.sin(pitch)];
  const right = norm(cross(scl(off, -1), [0, 0, 1])), up = cross(right, scl(off, -1));
  const f = 0.32 / 1.08, g = f * asp;   // (0.32: the starting field of view, CAM_FOV0 in 50-camera.js)
  return dot(c, off) + Math.max((Math.abs(dot(c, up)) + r * Math.hypot(1, f)) / f, (Math.abs(dot(c, right)) + r * Math.hypot(1, g)) / g);
}
function ballsCam() {
  const w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight), asp = w / h, rho = ballsRho(), t = ballsT();
  if (rho === 1 && t >= 1) {
    const r = Math.min(ballsReach(), 4.5);
    return { yaw: -1.25, pitch: 0.5, dist: Math.max(3.3, 3.6 * r / asp), h: Math.max(2.1, 2.25 * r / asp), room: Math.min(r + 0.4, 8) };
  }
  // Every other pair of numbers: the neighbours may be larger than the middle ball, so the picture grows taller as
  // well as longer. `tall` is how far it reaches from the middle line: a neighbour's own radius, or the middle ball
  // with the largest bud on its waist (`waist`; measured on lists of balls for rho <= 1/2: out/r28/dials/NOTES.md).
  // A chain longer than BALLS_FAR (the two spheres touch, or all but) is not framed whole: then the middle ball, its
  // two neighbours and a stretch of what follows are, and ballsTrouble says that the chain goes on. The same stretch
  // is framed where the two spheres cut into each other: there is no end of a chain to frame (ballsReach is
  // Infinity there).
  // (Round 29, a second sphere between 1/2 and 1 of the first, the two spheres apart: the chain's reach holds as it
  //  stands, but the bud on the waist is larger than k^2 / (2 top - 1), by up to an eighth of the whole height in
  //  the pairs that were measured (out/r29/free/mk/tall29.py). There the hull of that bud is used instead: nothing
  //  that grows on the bottom wall reaches higher than HB, which the frame carries to k^2 HB / (2 - HB) beyond the
  //  middle ball.)
  const p = ballsShare(t), reach = ballsReach(t, rho);
  const whole = reach <= BALLS_FAR, r = whole ? reach : Math.max(4.5, BALLS_K2 * (0.5 + 1.5 * p / 100));
  const HBw = rho > BALLS_RHO_HALF && 2 * t - 1 - rho > 1e-9 ? ballsHulls(t, rho, true).HB : 0;
  const waist = BALLS_K2 / 2 + (HBw > 0 ? BALLS_K2 * HBw / (2 - HBw) : BALLS_K2 / (4 * t - 1));
  const tall = Math.max(BALLS_K2 * p / 200, waist);
  // The balls the picture has to hold, each seen whole (ballsSee): the middle ball with the buds on its waist, the two
  // big neighbours, and, when the chain is framed whole, the ball that holds the rest of the chain at either end.
  // Never nearer than the rule of thumb that was there before, so the views that were right stay as they were.
  const yaw = -1.25, pitch = 0.5, rN = BALLS_K2 * p / 200, xN = BALLS_K2 / 2 + rN, rE = Math.max(0, (reach - xN - rN) / 2);
  let see = ballsSee([0, 0, 0], waist, asp, yaw, pitch);
  for (const sg of [-1, 1]) {
    see = Math.max(see, ballsSee([sg * xN, 0, 0], rN, asp, yaw, pitch));
    if (whole && rE > 0) see = Math.max(see, ballsSee([sg * (reach - rE), 0, 0], rE, asp, yaw, pitch));
  }
  // (room, the Drawing radius the view wants: the whole chain with a little air; for a stretch of an endless chain
  //  so much more that the place where the Drawing radius cuts a ball open lies outside the picture)
  return { yaw, pitch, dist: Math.max(3.3, 3.6 * r / asp, 3.75 * tall, see), h: Math.max(2.1, 2.25 * r / asp, 2.4 * tall), room: whole ? r + 0.4 : 2 * r };
}
// "Frame it", and what the row in the Approach list does to the camera: the start view, with a zoom limit or a
// drawing radius that is in the way moved (a promise to show the whole thing, like the other Frame buttons).
function ballsFrame() {
  const b = ballsCam();
  presetRoom(presetDist(b.dist, 1), b.room);
  if (S.v2.hmax < b.h) S.v2.hmax = b.h;
  resetCam();
  touch();
}
// Two things the sentences below say only where the two spheres cut into each other, each found by asking the
// recipe itself (ballsInside) and kept until the numbers it was asked for change.
// Far out, is everything filled, and is the picture then one lump as large as the Drawing radius? The recipe at
// fourteen directions and two distances far beyond the Drawing radius (and beyond the two big neighbours): all of
// them inside. And on the ball of the Drawing radius itself, where the skin of the lump would be, at 120 directions
// spread evenly: at least three in ten of them inside (a lump may have holes; a band of balls with open sky round it
// is not a lump, even if far beyond it everything is filled). Where that line lies was measured: with three in ten
// or more, 97 in 100 rays of the picture or more stopped on something; with fewer, 78 in 100 or fewer
// (out/r29/free/mk/lump.js, lump2.js).
const BALLS_ASK = { far: '', farIs: false, flat: '', flatIs: false };
function ballsFarFilled() {
  const t = ballsT(), bound = +S.view.bound > 0 ? +S.view.bound : 8, base = Math.max(bound, BALLS_K2 * (0.5 + ballsShare(t) / 100));
  const key = [t, ballsRho(), S.k.bgrid | 0, S.k.bit, bound, base].join('|');
  if (BALLS_ASK.far !== key) {
    let all = true;
    for (const far of [20, 2000]) for (let i = 0; i < 14 && all; i++) {
      // (six along the axes, eight along the diagonals, a little off the straight so that no point lies in a mirror)
      const d = i < 6 ? [[1, 0.03, 0.02], [-1, 0.02, 0.03], [0.03, 1, 0.02], [0.02, -1, 0.03], [0.03, 0.02, 1], [0.02, 0.03, -1]][i]
        : [i & 1 ? 1 : -1, i & 2 ? 0.9 : -0.9, i & 4 ? 0.8 : -0.8], s = far * base / Math.hypot(d[0], d[1], d[2]);
      all = ballsInside(s * d[0], s * d[1], s * d[2]);
    }
    if (all) {
      let n = 0;
      for (let i = 0; i < 120; i++) {
        const z = 1 - (2 * i + 1) / 120, r = Math.sqrt(1 - z * z), a = 2.399963229728653 * i;
        if (ballsInside(bound * r * Math.cos(a), bound * r * Math.sin(a), bound * z)) n++;
      }
      all = n >= 36;
    }
    BALLS_ASK.far = key; BALLS_ASK.farIs = all;
  }
  return BALLS_ASK.farIs;
}
// Is the flat picture filled completely? The recipe on a grid of the 2D view as it stands, and of the 2D view that
// Frame it gives (so that a view from deep inside one ball does not count as a filled picture).
function ballsFlatFilled() {
  const w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight), asp = w / h, v = S.v2, h0 = ballsCam().h;
  const key = [ballsT(), ballsRho(), S.k.bgrid | 0, S.k.bit, v.x, v.y, v.h, S.cut, asp, h0].join('|');
  if (BALLS_ASK.flat !== key) {
    const NX = 60, NY = 40;
    let all = true;
    for (const [cx, cy, hh] of [[v.x, v.y, v.h], [0, 0, h0]]) for (let j = 0; j < NY && all; j++) for (let i = 0; i < NX && all; i++) {
      all = ballsInside(cx + ((i + 0.5) / NX - 0.5) * hh * asp, cy + ((j + 0.5) / NY - 0.5) * hh, +S.cut || 0);
    }
    BALLS_ASK.flat = key; BALLS_ASK.flatIs = all;
  }
  return BALLS_ASK.flatIs;
}
// What the user should know about the picture as the dials stand, in plain sentences (status, not an error), or ''.
// Where the two spheres touch (at 100 with two equal spheres, at 100 / rho with a smaller second one) the chain is
// endless, in the 2D view as well: nothing the user does shows all of it, so the sentence says what is on the screen
// instead of giving advice that cannot be followed. (The depth: each further ball of the chain costs the search one
// more round, and a point still undecided counts as inside, as in tree.py.)
// Round 28 added: what the second sphere is while it is not as large as the first, and what a depth under
// BALLS_ROUNDS_FEW does to the picture. Round 29: where the two spheres cut into each other (ballsMeet) one sentence
// says so, in place of the sentences about the chain, and what the picture then is (one lump, or a filled flat picture).
function ballsTrouble() {
  if (!ballsShown()) return '';
  const rho = ballsRho(), t = ballsT(), p = ballsShare(t), out = [], pc = x => dialFmt(+x.toFixed(2));
  const what = S.flat ? 'circles' : 'balls', meet = ballsMeet(t, rho), touch = meet === 0, cutting = meet > 0;
  const lump = cutting && !S.flat && ballsFarFilled();
  // (the fixer of round 28: after a large size is typed the Drawing radius is smaller than the neighbours themselves,
  //  and one of them shows as a flat wall. That is said, with its cure, in place of "its far ends are not drawn".
  //  Not where the picture is one lump anyway: no Drawing radius makes room for that.)
  const open = (rho < 1 || t < 1) && !lump && !S.flat && S.view.bound < BALLS_K2 * (0.5 + p / 100) * (1 - 1e-9);
  if (cutting) {
    out.push('Here the two spheres of the recipe cut into each other, so the balls run into one another. A smaller size or a smaller second sphere parts them again.' +
      (lump ? ' Far out everything is filled, so the picture is one lump as large as the Drawing radius.' : '') +
      (S.flat && ballsFlatFilled() ? ' The flat picture is filled completely.' : ''));
  } else if (touch && rho === 1) {
    const close = S.flat ? ', and the circles stand so close that they read as one band with holes' : ', and the balls stand so close that they read as one bar with round holes';
    out.push('At 100 the chain never ends, so the picture shows a stretch of it' + (!S.flat && S.k.bgrid === 2 ? '' : close) +
      `; where the depth of the search runs out, the far ${what} and the places where two ${what} kiss come out swollen.`);
  } else if (touch) {
    // (a smaller second sphere: the same said in two short sentences. Also where the two shown numbers multiply to
    //  100 x 100 within their rounding, ballsMeet: the chain then leaves the picture as an endless one does.)
    out.push(`At ${pc(p)} the chain never ends, so the picture shows a stretch of it. Where the depth of the search runs out, the far ${what} and the places where two ${what} kiss come out swollen.`);
  } else if (rho < 1 && ballsReach(t, rho) > BALLS_FAR) {
    // (not endless, but longer than Frame it shows whole, in the 3D and in the 2D view: ballsCam)
    out.push('Here the chain is too long for one picture, so Frame it shows a stretch of it.');
  } else if (!open && !S.flat && ballsReach() > S.view.bound) out.push('The chain of balls runs out past the Drawing radius in the View section, so its far ends are not drawn.');
  if (open) out.push('The Drawing radius in the View section cuts the two big neighbours open. Frame it makes room for them.');
  if (rho < 1) {
    out.push(`The second sphere is now ${pc(100 * rho)} % of the first. Reset this section puts it back to 100.`);
    // (at 50 the copies of the second sphere at neighbouring whole numbers kiss, and so do the buds on a neighbour:
    //  the search runs out there as it does where the two spheres touch, which the sentence above then says already.
    //  Only at exactly 50, and only where the two spheres are apart.)
    if (meet < 0 && ballsRhoShown() === 100 * BALLS_RHO_HALF) out.push('With the second sphere at 50 the buds on a neighbour kiss, and where the depth of the search runs out those places come out swollen.');
  }
  // (one round: everything inside either sphere is still undecided, which is most of the picture; seen)
  if (S.k.bit < BALLS_ROUNDS_FEW) out.push('With so few rounds of the search whole balls are still undecided, and they come out as broken shells.' +
    (S.k.bit < 2 ? ' With a single round most of the picture is one wall of colour.' : ''));
  return out.join(' ');
}

