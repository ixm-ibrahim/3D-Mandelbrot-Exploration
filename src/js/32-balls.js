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
// ----- The pairs of numbers that GL_BALLS_FREE draws ('balls3'): the length that is certainly free, in JavaScript,
// written the way that program writes it (the long comment above GL_BALLS_FREE says why each line holds).
// The whole numbers round the middle one, by grid: first the middle itself, then the ones next to it, then (square
// grid) the four on the diagonals.
const BALLS_NEAR = [
  [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]],
  [0, 1, 2, 3, 4, 5, 6].map(k => (k === 0 ? [0, 0] : [Math.cos((k - 1) * Math.PI / 3), Math.sin((k - 1) * Math.PI / 3)])),
  [[0, 0], [1, 0], [-1, 0]]];
// A length that is no longer than the distance from the point to the cell of a whole number (dx, dy: the point less
// that number).
function ballsCellFar(grid, dx, dy) {
  if (grid === 2) return Math.max(Math.abs(dx) - 0.5, 0);
  if (grid === 0) return Math.hypot(Math.max(Math.abs(dx) - 0.5, 0), Math.max(Math.abs(dy) - 0.5, 0));
  return Math.max(Math.max(Math.abs(dx), Math.abs(0.5 * dx + 0.5 * BALLS_S3 * dy), Math.abs(0.5 * dx - 0.5 * BALLS_S3 * dy)) - 0.5, 0);
}
// The numbers that depend on the dials alone.
function ballsFreeSet(t, rho, grid) {
  const top = 2 * t, rr = rho * rho, f = { top, rho, rr, grid, apart: top - 1 - rho >= -1e-6, hu: ballsHulls(t, rho, true) };
  // the side spindle (rho <= 1/2) or the side ring (rho > 1/2): its circle (c2, a, R), and how far across it may go
  const c2 = 0.25 - rr, K = top * top - 1 + rr, disc = K * K + 4 * (top * top - 1) * c2, lim = grid === 2 ? 1e9 : grid === 0 ? 0.5 : 0.5 / BALLS_S3;
  let w = (K + Math.sqrt(Math.max(disc, 0))) / (2 * (top + 1)), on = disc >= 0, clip = 1e9;
  if (rho <= 0.5) w = Math.min(w, lim, (grid === 1 ? BALLS_S3 / 2 : 1) - rho);
  else { on = on && w * w > -c2 * 1.0000001; clip = lim * -c2 / (w * w); }
  f.side = { on: on && w > 0, c2, a: (w * w - c2) / (2 * w), R: (w * w + c2) / (2 * w), clip };
  if (f.apart) return f;
  // the two spheres cut into each other: the circle where they cross lies at the height zm and is q0 across
  const zm = (top * top + 1 - rr) / (2 * top), dd = zm * zm - 1, q0 = Math.sqrt(Math.max(-dd, 0)), hmin = Math.min(zm, top - zm);
  const rw = Math.min(0.5, top - zm + rho), slab = rr - 0.25;
  f.zm = zm; f.dd = dd; f.q0 = q0;
  f.ring = { on: rw * rw + dd > 0, a: (rw * rw - dd) / (2 * rw), R: (rw * rw + dd) / (2 * rw) };
  f.ylim = slab > 1e-5 ? Math.min(grid === 0 ? -dd : grid === 1 ? 2 * (q0 - BALLS_S3 / 4) : 1e9, Math.sqrt(slab)) : -1;
  const er2 = (grid === 0 ? 0.5 : 1 / 3) + dd;
  f.edge = grid !== 2 && er2 > 0 && Math.sqrt(er2) <= Math.min(hmin, grid === 0 ? 1 : 0.5) ? Math.sqrt(er2) : -1;
  // the depth of the search (see "the depth" above GL_BALLS_FREE)
  const gv = q0 < 0.5 ? 0.5 : grid === 0 ? Math.SQRT1_2 : grid === 1 ? 1 / BALLS_S3 : q0 + 0.25, kap = Math.sqrt(Math.max(gv - q0, 1e-9) / (gv + q0));
  f.rhoT = Math.log((1 + kap) / (1 - kap));
  f.fan = Math.PI / Math.max(Math.PI - Math.acos(Math.min(1, Math.max(-1, (1 + rr - top * top) / (2 * rho)))), 1e-6) - 1e-3;
  f.fanS = rho > 0.5 ? Math.PI / Math.max(Math.PI - Math.acos(Math.min(1, Math.max(-1, (2 * rr - 1) / (2 * rr)))), 1e-6) - 1e-3 : 0;
  return f;
}
// At the place m where the recipe ends OUTSIDE (W, DF as the search carries them; left: the rounds it had left):
// [the length that is certainly free, the true distance to the two first buds behind the mirrors].
function ballsFreeRoom(m, W, DF, f, left) {
  const { top, rho, rr, grid } = f, back = (e, p, w, df) => { const L = Math.hypot(p[0] - w[0], p[1] - w[1], p[2] - w[2]), x = Math.max(e, 0); return x * L / ((L + x) * df); };
  const hb = m[2], ht = top - m[2], q = Math.hypot(m[0], m[1]), [al, ac] = ballsLean(m, grid);
  // the side spindle or the side ring, between the second sphere and its copy at the next whole number
  let side = -1;
  if (f.side.on) {
    const sd = f.side, v = al - 0.5, tq = Math.hypot(ac, ht);
    side = Math.min((sd.c2 - v * v + tq * (2 * sd.a - tq)) / (sd.R + Math.hypot(v, tq - sd.a)), sd.clip - Math.abs(ac));
  }
  if (f.apart) {
    // the two spheres apart: the hulls of GL_BALLS_RHO, which hold for a second sphere of any size
    const hu = f.hu, HB = hu.HB, HT = hu.HT, restB = grid === 0 ? HB / 2 : grid === 1 ? HB / 3 : HB / 4, restT = rr * HT;
    const rT = Math.min(rho, 2 * rr / (1 + Math.sqrt(Math.max(1 - 4 * rr, 0))) + restT), rt = Math.hypot(m[0], m[1], ht);
    const cb = Math.hypot(m[0], m[1], hb - HB / 2) - HB / 2, ct = Math.hypot(m[0], m[1], ht - HT / 2) - HT / 2;
    const lo = grid === 2 ? Math.hypot(m[1], hb) : hb, hi = grid === 2 ? Math.hypot(m[1], ht) : ht;
    let e = Math.max(Math.min(cb, ct, Math.min(lo - restB, Math.max(hi - restT, rt - rT))), 0);
    const dz = m[2] - hu.zm;
    if (hu.on) e = Math.max(e, (hu.d2 + q * (2 * hu.a - q) - dz * dz) / (hu.R + Math.hypot(q - hu.a, dz)));
    return [back(Math.max(e, side), m, W, DF), 1e9];
  }
  // the two spheres cut into each other
  const C = [0, 0, top], rb = Math.max(dot(m, m), 1e-300), mt = sub(m, C), rt = Math.max(dot(mt, mt), 1e-300);
  // looking through the first sphere, and through the second
  const mA = scl(m, 1 / rb), WA = scl(W, 1 / Math.max(dot(W, W), 1e-300)), DFA = DF / rb, LA2 = Math.max(dot(sub(mA, WA), sub(mA, WA)), 1e-300);
  const sB = rr / rt, Wt = sub(W, C), mB = add(scl(mt, sB), C), WB = add(scl(Wt, rr / Math.max(dot(Wt, Wt), 1e-300)), C), DFB = DF * sB, LB2 = Math.max(dot(sub(mB, WB), sub(mB, WB)), 1e-300);
  const pearl = (h, D, kk) => (h > 0 ? 2 * h / (1 + Math.sqrt(1 + kk * h * Math.max(D, 0))) : h);
  const bud = Math.min(pearl(top - mA[2], top - WA[2], 4 / LA2) / DFA, pearl(mB[2], WB[2], 4 / LB2) / DFB);
  let eA = 0.5, eB = 0.5;
  BALLS_NEAR[grid].forEach((c, k) => {
    const ax = mA[0] - c[0], ay = mA[1] - c[1], fa = ballsCellFar(grid, ax, ay), bx = mB[0] - c[0], by = mB[1] - c[1], fb = ballsCellFar(grid, bx, by);
    eA = Math.min(eA, Math.max(Math.hypot(ax, ay, mA[2] - top) - rho, fa));
    if (grid === 0 && k >= 5) eA = Math.min(eA, Math.max(Math.hypot(ax, ay, mA[2]) - 1, fa));
    eB = Math.min(eB, Math.max(Math.hypot(bx, by, mB[2]) - 1, fb));
    if (k >= 1) eB = Math.min(eB, Math.max(Math.hypot(bx, by, mB[2] - top) - rho, fb));
  });
  eA = Math.max(eA, 1 - Math.sqrt(dot(mA, mA))); eB = Math.max(eB, rho - Math.hypot(mB[0], mB[1], mB[2] - top));
  let free = left < 1 ? Math.min(back(Math.sqrt(rb) - 1, m, W, DF), back(Math.sqrt(rt) - rho, m, W, DF)) : Math.min(back(eA, mA, WA, DFA), back(eB, mB, WB, DFB));
  // the ring round the circle where the two spheres cross, and the balls that every move carries onto themselves
  const dz = m[2] - f.zm;
  const ring = f.ring.on ? (f.dd + q * (2 * f.ring.a - q) - dz * dz) / (f.ring.R + Math.hypot(q - f.ring.a, dz)) : -1;
  let whole = ring;
  if (f.ylim >= 0) {
    const yc = Math.min(f.ylim, Math.max(-f.ylim, ac)), r2 = 0.25 + yc * yc + f.dd;
    if (r2 > 0) whole = Math.max(whole, Math.sqrt(r2) - Math.hypot(al - 0.5, ac - yc, dz));
  }
  if (f.edge > 0) {
    let ex, ey;
    if (grid === 0) { ex = m[0] < 0 ? -0.5 : 0.5; ey = m[1] < 0 ? -0.5 : 0.5; }
    else { const a0 = (Math.floor(Math.atan2(m[1], m[0]) / (Math.PI / 3)) + 0.5) * (Math.PI / 3); ex = Math.cos(a0) / BALLS_S3; ey = Math.sin(a0) / BALLS_S3; }
    whole = Math.max(whole, f.edge - Math.hypot(m[0] - ex, m[1] - ey, dz));
  }
  // the depth of the search
  const wholeP = left >= f.fan ? back(whole, m, W, DF) * (1 - Math.exp(-f.rhoT * (left - f.fan)))
    : left >= 0.5 * f.fan + 1 && f.ring.on ? back(Math.min(ring, Math.hypot(q - f.q0, dz)), m, W, DF) : -1;
  const sideP = back(side, m, W, DF) * (rho > 0.5 ? 1 - Math.exp(-f.rhoT * Math.max(left - f.fanS, 0)) : Math.max(left - 1, 0) / (left + 8));
  free = Math.max(free, wholeP, sideP);
  return [free, left >= 1 ? bud : 1e9];
}
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

// The scene program of this group. Same interface towards GL_HEAD, GL_COLOUR and GL_TAIL as GL_KLEIN: de() sets
// gEsc, gIt, gLast, gGrad and gOnTrap, feeds the colour trap (trapStart, trapAdd) and keeps the touch record of a
// trap solid (gTouch, gTouchIt, gTouchS, gTouchStr). Its two uniforms are declared here, so no other program
// changes: uBT = t, uBGrid = the grid.
//
// The distance. Every ball of the picture is the sphere that some chain of the moves carries onto one of the two
// walls (m.z = 0 and m.z = 2t). The search follows ONE chain, the recipe's. For each wall it meets, kpearl gives the
// TRUE distance to that ball (see GL_KLEIN: h is how far the mapped point stands from the wall, D the same for W,
// the image of the point at infinity, kk = 4 / |m - W|^2; DF is the scale factor of the maps so far, the frame
// inversion included).
// But the nearest ball need not be on that chain: next to every ball stand buds of every size that the recipe never
// visits from this point. So when the recipe ends OUTSIDE, the place it ends at is used for a second number, "free":
// a length inside which there is certainly no ball at all. There (m in the middle of its cell, outside both unit
// spheres) every ball other than the two walls lies inside
//   the ball of diameter H = t - sqrt(t^2 - 1) that stands on the wall at the nearest whole number (the first bud
//   and everything that grows on it; one on each wall), or
//   within H / 2 of a wall (square grid; H / 3 honeycomb; a tube of radius H / 4 round the line for the line grid):
//   the buds at the fractions that are not whole numbers.
// (The heights: a bud at the fraction p / q is 1 / |q|^2 the size of the one at a whole number, and the highest any
// growth on the bottom wall reaches is H, because H = 1 / (2t - H).) With e the distance from m to all of that, the
// ball of radius e round m is empty, and carried back to the picture it leaves a ball of radius
// e L / ((L + e) DF) round the point, L = |m - W|: an exact statement about sphere inversions, not a first-order one.
// The estimate is the smaller of the two numbers, so it is never longer than the true distance to the nearest ball.
// The spindle (added by the fixer of round 27). With large neighbours the two hull balls of diameter H nearly touch
// (at t = 1 they do, where the two unit spheres kiss), and beside that place the room above was far too small: it
// fell off like the square of the distance from the kiss while the nearest ball is as far off as the kiss itself.
// Rays there crept along, ran out of steps and left holes. So a second room is taken, and the larger of the two used.
// The two inversions of the recipe together hold two points of the middle line fixed: z = H and z = 1 / H = 2t - H
// (one point, z = 1, at t = 1). Every circle through both crosses both unit spheres squarely, so each inversion
// carries it onto itself. Take the arcs through both points that reach 1/2 from the line at mid-height z = t: in the
// (distance from the line, z) half-plane, the circle of radius 1/4 + s^2 about (1/4 - s^2, t), s^2 = t^2 - 1. Spun
// round the line they bound a spindle (a ring with no hole at t = 1). Between the two unit spheres the spindle lies
// inside the middle cell, where the recipe says OUTSIDE; the two inversions carry that piece onto the rest of the
// spindle, piece by piece, towards the two fixed points. So no ball reaches into the spindle, for any of the three
// grids, and a point m inside it has the room 1/4 + s^2 - (its distance from that circle's centre).
// One exception, in the 3D picture only (gPix > 0): "free" is not taken below two ray thresholds (one and a quarter
// when the ray takes four fifths of the estimate or more: see the last lines of de). It measures to
// hulls, not to balls, so close in it would stop every ray a few pixels short and roughen the slope; there the ray
// goes on in steps of about a pixel and is stopped by the exact distances, or by landing inside a ball (the inside
// test is exact at every size). In the 2D view and for a 3D model (gPix = 0) nothing is held up.
const GL_BALLS = `
const bool ORBIT_SCENE = false;
uniform float uBT; uniform int uBGrid;
const float BALLS_K2 = ${BALLS_K2.toFixed(4)};
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// the whole number of the grid nearest to q (what the slide takes away)
vec2 bnear(vec2 q){
  if (uBGrid == 2) return vec2(floor(q.x + 0.5), 0.0);
  if (uBGrid == 0) return floor(q + 0.5);
  float b0 = floor(q.y / 0.8660254038 + 0.5), bd = 1e30;
  vec2 best = vec2(0.0);
  for (int j = -1; j <= 1; j++){
    float b = b0 + float(j), a = floor(q.x + 0.5 * b + 0.5);
    vec2 s = vec2(a - 0.5 * b, 0.8660254038 * b), w = q - s;
    float d = dot(w, w);
    if (d < bd){ bd = d; best = s; }
  }
  return best;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, H = uBT - sqrt(max(uBT * uBT - 1.0, 0.0));
  float rest = uBGrid == 0 ? 0.5 * H : uBGrid == 1 ? H / 3.0 : 0.25 * H;
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (see gLand in GL_HEAD); none while the trap alone is the solid, because then the balls are
  // not in the picture. The distances here are lengths of the picture already, so it is used as it comes.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5, inside = false, decided = false;
  float land = walls ? gLand : 0.0;
  trapStart();
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5;
  float bestT = 1e9;
#endif
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
    // The trap as a solid: every point whose chain, from round uTrapSkip on, comes within uTrapW of the trap shape.
    // The length is carried back to the picture the way "free" is.
#if TRAP_SOLIDS
    if (trapSolid && i >= uTrapSkip){
      float dq = trapDist(tv), et = dq - uTrapW, L = sqrt(L2);
      float sc = (et > 0.0 ? et * L / (L + et) : et) / DF;
      if (sc < bestT){ bestT = sc; gTouch = vec4(tv - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
    }
#endif
    // a hit's trap colour: the search is over at the first round that lands within the landing length of a ball,
    // and that point is fed to the trap as a point of the wall itself
    bool landed = land > 0.0 && cand < land;
    if (landed){ tv.x = hb < ht ? -uBT : uBT; free = 1e9; }
    trapAdd(tv, it); gLast = tv;
    if (landed || hb < 0.0 || ht < 0.0){ inside = hb < 0.0 || ht < 0.0; decided = true; break; }
    vec3 zt = vec3(z.xy, z.z - top);
    float rb = dot(z, z), rt = dot(zt, zt);
    if (rb < 1.0){
      float s = 1.0 / max(rb, 1e-20);
      z *= s; W /= max(dot(W, W), 1e-20); DF *= s;
    } else if (rt < 1.0){
      float s = 1.0 / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt / max(dot(Wt, Wt), 1e-20); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see the top of this program).
      float cb = length(vec3(z.xy, hb - 0.5 * H)) - 0.5 * H, ct = length(vec3(z.xy, ht - 0.5 * H)) - 0.5 * H;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo, hi) - rest), 0.0), L = sqrt(L2), s2 = uBT * uBT - 1.0;
      // the spindle round the line that joins the two walls: no ball reaches into it (see the top of this program)
      // (written so that nothing large is taken from something large: beside the kiss the room is as small as the
      //  distance from the middle line, and single precision would lose it in 1/4 - 1/4)
      float rho = length(z.xy), dz = z.z - uBT;
      if (uBT < ${BALLS_SPINDLE_T.toFixed(1)}) e = max(e, (s2 + rho * (0.5 - 2.0 * s2 - rho) - dz * dz) / (0.25 + s2 + length(vec2(rho - 0.25 + s2, dz))));
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // The trap solid takes the place of the balls (1) or joins them (2: whichever surface is nearer).
  // THE PAGE DOES NOT USE THIS: for this group the colour module never asks for a trap solid (colBalls in
  // 25-colour.js), so this program is always built with TRAP_SOLIDS 0. Tried and put away in round 27: the trap is
  // met inside one cell of the grid, so any trap wider than the cell comes out cut open along the cell's flat
  // faces, and a trap near the point (0, 0, 1), which is the far distance of the picture, grows past the camera.
  // The cap keeps a ray from leaping when no round was tested (a far point is OUTSIDE at once).
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
// The same program for a second sphere that is smaller than the first (round 28): uBRho = rho < 1, its radius. It is
// a text of its own, with its own key in the cache ('balls2': sceneWant in 40-render.js), so that the program above
// stays exactly what it was and every picture with two equal spheres stays the same to the pixel.
// What differs, and why (each line was checked with numbers on lists of balls: out/r28/dials/mk/derive.py):
//   The second inversion has the scale factor rho^2 / |m - (0, 0, top)|^2 (for DF and for W).
//   The two inversions together hold two points of the middle line fixed: z1 and z2 = 1 / z1, where
//   z1 + z2 = s = top + (1 - rho^2) / top (s = 2 exactly when the two spheres touch). Nothing that grows on the
//   bottom wall reaches higher than HB = z1 and nothing on the top wall hangs lower than HT = top - z2
//   (HB = 1 / (top - HT), HT = rho^2 / (top - HB)). So the two hull balls now differ: diameter HB standing on the
//   bottom wall, diameter HT hanging from the top wall, each at the nearest whole number.
//   "The rest" on the bottom wall is as it was, with HB (HB / 2, HB / 3, a tube of HB / 4). On the top wall a bud
//   that does not stand at a whole number is the image, by the second sphere's inversion, of a hull at a whole
//   number at distance d >= 1 from the sphere's centre, which makes it rho^2 HT / d^2 across; images of images are
//   no larger while rho <= 1/2. So the rest there is rho^2 HT, for all three grids.
//   The top wall is no longer covered by the second sphere and its slid copies, so most of it is bare: nothing
//   grows there, and a rest that lay over the whole wall would leave the ray no room beside a bare wall (it crept
//   along the large neighbours in steps of a pixel, and the slope of their skin came out in faint bands). All that
//   grows on the top wall lies inside the second sphere, and the buds of the rest touch the wall no further than
//   x = (1 - sqrt(1 - 4 rho^2)) / 2 from its centre (x = rho^2 / (1 - x): a bud is the image of one that stands at
//   least 1 - x from the centre). So the rest is the part of its slab within rT = min(rho, x + rho^2 HT) of the
//   centre, and a point is at least max(distance to the slab, distance to that ball) away from it.
//   The spindle. Every circle through z1 and z2 still crosses both spheres squarely, so the argument above GL_BALLS
//   holds for the spindle of any such arc, provided the whole of it lies in the middle cell and between the two
//   walls. With two equal spheres the arc that reaches 1/2 from the line at mid-height does. With a smaller second
//   sphere that spindle can bulge through the top wall beside the second sphere (found with numbers: at 300 %
//   with rho = 1/6 it holds whole balls). So the arc taken reaches w = min(1/2, top - zm + rho) at mid-height
//   zm = s / 2: at the second value it just touches the top wall, on the circle where the second sphere meets it.
//   In the half-plane (distance from the line, z) it is the circle about (a, zm) with radius R, a = (w^2 - d2) / 2w,
//   R = (w^2 + d2) / 2w, d2 = ((z2 - z1) / 2)^2; a point inside has the room R - (its distance from that centre).
//   (All of it is written from D = s - 2 = (top - 1 - rho)(top - 1 + rho) / top, so that nothing large is taken from
//   something large beside the place where the two spheres touch.)
//   The side spindle (added by the fixer of round 28). The second sphere and its copy at the next whole number are
//   both centred on the top wall, 1 apart, and at rho = 1/2 they kiss. Beside the kiss, under the wall and outside
//   both, the room above was far too small: it fell off like the square of the distance from the kiss, while the
//   nearest ball is as far off as the kiss itself (the buds that hang there shrink like that square). The 2D view
//   draws its outline where the distance is under a pixel, so it drew a fan of lines and a bump where nothing is;
//   close to 1/2 the same, less. The cure is the argument of the spindle once more, lying on its side. The two
//   inversions, about C = (0, 0, top) and about C + n (n the next whole number, |n| = 1), hold two points of the
//   line through both centres fixed: C + x n and C + (1 - x) n, the x of the bare wall above (one point, the
//   kiss, at rho = 1/2). Every circle through both crosses both spheres squarely, so each inversion carries the
//   spindle swept by such an arc round that line onto itself, and the top wall onto itself. Take the arc that
//   reaches w = min(top - HB, D - rho) from the line at the middle point C + n / 2 (D = 1 for the square grid and for
//   a line only, sqrt(3) / 2 for the honeycomb grid): then the piece of the spindle under the wall and outside both
//   spheres holds no ball, because it stays above everything that grows on the bottom wall (nothing there is higher
//   than HB) and clear of every other copy of the second sphere. The two inversions carry that piece onto the whole
//   half spindle under the wall, piece by piece, towards the two fixed points. So no ball other than the top wall
//   itself reaches into it (the walls are measured exactly, by "best"). In the half-plane (v along the line from
//   the middle point, q the distance from the line) the arc is the circle about (0, a) with radius R,
//   a = (w^2 - c2) / 2w, R = (w^2 + c2) / 2w, c2 = 1/4 - rho^2; a point inside has the room R - |(v, q - a)|.
//   (Put to lists of balls before it was built in: out/r28/fix/mk/side.py.)
const GL_BALLS_RHO = `
const bool ORBIT_SCENE = false;
uniform float uBT, uBRho; uniform int uBGrid;
const float BALLS_K2 = ${BALLS_K2.toFixed(4)};
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// the whole number of the grid nearest to q (what the slide takes away)
vec2 bnear(vec2 q){
  if (uBGrid == 2) return vec2(floor(q.x + 0.5), 0.0);
  if (uBGrid == 0) return floor(q + 0.5);
  float b0 = floor(q.y / 0.8660254038 + 0.5), bd = 1e30;
  vec2 best = vec2(0.0);
  for (int j = -1; j <= 1; j++){
    float b = b0 + float(j), a = floor(q.x + 0.5 * b + 0.5);
    vec2 s = vec2(a - 0.5 * b, 0.8660254038 * b), w = q - s;
    float d = dot(w, w);
    if (d < bd){ bd = d; best = s; }
  }
  return best;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, rr = uBRho * uBRho;
  // the two fixed points on the middle line, the two hull balls and the spindle (see above this program)
  float sD = max(top - 1.0 - uBRho, 0.0) * (top - 1.0 + uBRho) / top, sQ = sqrt(sD * (sD + 4.0));
  float HB = 1.0 / (1.0 + 0.5 * (sD + sQ)), HT = rr / (top - HB), zm = 1.0 + 0.5 * sD, d2 = 0.25 * sD * (sD + 4.0);
  float restB = uBGrid == 0 ? 0.5 * HB : uBGrid == 1 ? HB / 3.0 : 0.25 * HB, restT = rr * HT;
  float rT = min(uBRho, 2.0 * rr / (1.0 + sqrt(max(1.0 - 4.0 * rr, 0.0))) + restT);
  float sw = min(0.5, top - zm + uBRho), sa = (sw * sw - d2) / (2.0 * sw), sR = (sw * sw + d2) / (2.0 * sw);
  // the side spindle, between the second sphere and its copy at the next whole number
  float tc2 = max(0.25 - rr, 0.0), tw = min(top - HB, (uBGrid == 1 ? 0.8660254038 : 1.0) - uBRho);
  float ta = (tw * tw - tc2) / (2.0 * tw), tR = (tw * tw + tc2) / (2.0 * tw);
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (see gLand in GL_HEAD); none while the trap alone is the solid, because then the balls are
  // not in the picture. The distances here are lengths of the picture already, so it is used as it comes.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5, inside = false, decided = false;
  float land = walls ? gLand : 0.0;
  trapStart();
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5;
  float bestT = 1e9;
#endif
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
    // The trap as a solid: every point whose chain, from round uTrapSkip on, comes within uTrapW of the trap shape.
    // The length is carried back to the picture the way "free" is.
#if TRAP_SOLIDS
    if (trapSolid && i >= uTrapSkip){
      float dq = trapDist(tv), et = dq - uTrapW, L = sqrt(L2);
      float sc = (et > 0.0 ? et * L / (L + et) : et) / DF;
      if (sc < bestT){ bestT = sc; gTouch = vec4(tv - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
    }
#endif
    // a hit's trap colour: the search is over at the first round that lands within the landing length of a ball,
    // and that point is fed to the trap as a point of the wall itself
    bool landed = land > 0.0 && cand < land;
    if (landed){ tv.x = hb < ht ? -uBT : uBT; free = 1e9; }
    trapAdd(tv, it); gLast = tv;
    if (landed || hb < 0.0 || ht < 0.0){ inside = hb < 0.0 || ht < 0.0; decided = true; break; }
    vec3 zt = vec3(z.xy, z.z - top);
    float rb = dot(z, z), rt = dot(zt, zt);
    if (rb < 1.0){
      float s = 1.0 / max(rb, 1e-20);
      z *= s; W /= max(dot(W, W), 1e-20); DF *= s;
    } else if (rt < rr){
      float s = rr / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt * (rr / max(dot(Wt, Wt), 1e-20)); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see above this program, and the top of GL_BALLS).
      float cb = length(vec3(z.xy, hb - 0.5 * HB)) - 0.5 * HB, ct = length(vec3(z.xy, ht - 0.5 * HT)) - 0.5 * HT;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo - restB, max(hi - restT, sqrt(rt) - rT))), 0.0), L = sqrt(L2);
      // the spindle round the line that joins the two walls: no ball reaches into it
      // (written so that nothing large is taken from something large: R^2 - a^2 = d2)
      float q = length(z.xy), dz = z.z - zm;
      if (d2 < 3.0) e = max(e, (d2 + q * (2.0 * sa - q) - dz * dz) / (sR + length(vec2(q - sa, dz))));
      // the side spindle: the whole number next to the middle one that the point leans towards, along it and across it
      float al = abs(z.x), ac = z.y;
      if (uBGrid == 0 && abs(z.y) > al){ al = abs(z.y); ac = z.x; }
      if (uBGrid == 1){
        float h1 = abs(0.5 * z.x + 0.8660254038 * z.y), h2 = abs(0.5 * z.x - 0.8660254038 * z.y);
        if (h1 > al){ al = h1; ac = 0.5 * z.y - 0.8660254038 * z.x; }
        if (h2 > al){ al = h2; ac = 0.5 * z.y + 0.8660254038 * z.x; }
      }
      float tl = al - 0.5, tq = length(vec2(ac, ht));
      e = max(e, (tc2 - tl * tl + tq * (2.0 * ta - tq)) / (tR + length(vec2(tl, tq - ta))));
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // (the trap solid: as in GL_BALLS, the page never asks this group for one)
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
// The same program for every pair of numbers the two programs above were not written for (round 29): the two spheres
// cut into each other (top < 1 + rho), or the second sphere lies between 1/2 and 1 of the first, so that its copies at
// neighbouring whole numbers cut into each other. A text of its own, under its own key in the cache ('balls3':
// sceneWant in 40-render.js), so that the two programs above stay exactly what they were. The recipe and "best" are
// the same lines. What is new is "free", the length that is certainly free of balls at the place m where the recipe
// ends OUTSIDE. Each piece was put to the recipe alone on a fine grid, and to the true distance taken from that grid,
// before it was built in (out/r29/free/mk/kit29.py, proto.py; the numbers are in out/r29/free/NOTES.md).
//
// A. The two spheres apart or touching, the second between 1/2 and 1 of the first. The hulls of GL_BALLS_RHO hold as
//   they stand: nothing that grows on the bottom wall reaches higher than HB, nothing on the top wall hangs lower
//   than HT, and a bud that does not hang at a whole number is the image, by the second sphere's inversion, of
//   something that hangs OUTSIDE that sphere, so it is no deeper than rho^2 HT whatever rho is. The top wall inside
//   the cell is covered by the second sphere, so "the rest" is the part of its slab inside that sphere (rT = rho).
//   The spindle holds too: inside the middle cell only the first and the second sphere act, whatever the copies do.
//   In place of the side spindle there is the side ring of C below.
//
// B. The two spheres cut into each other. Then the hulls are gone, and what is used instead is this.
//   The verdict of the recipe is the same on both sides of a sphere surface: a point just inside the first sphere is
//   carried to its mirror image just outside and goes on from there, and the same for the second sphere outside the
//   first. It is also its own mirror image in every wall of the cell. So seen from m (in the middle cell, between
//   the walls, outside both spheres) every ball other than the two walls lies inside the first sphere or inside the
//   second, in the middle cell (a ball beyond a wall of the cell has a twin on this side that is nearer).
//   Looking through a sphere. What lies inside the first sphere is the mirror image of what lies outside it. So the
//   first sphere's inversion is applied to m although m is outside ("a round that does not count"), with DF and W
//   carried along as in a real round. There the point is inside the first sphere and everything that counts is
//   outside it: the two walls (kpearl gives the true distance; the top wall is the first bud behind the mirror, a
//   ball of the picture that the recipe's own chain never meets), the second sphere and its copies, each in its
//   own cell, and (square grid) the copies of the first sphere on the diagonals. The smaller of the distances to
//   those, or the distance to the first sphere's own surface from inside where that is the longer, is a room, and
//   it is carried back with e L / ((L + e) DF). The same through the second sphere. The smaller of the two rooms
//   is free of balls, and it is zero only on the circles where two spheres cross.
//   Balls that every move carries onto themselves. A ball that crosses both spheres squarely is carried onto itself
//   by both inversions; if it lies in the middle cell, or its centre lies on a wall of the cell (or on an upright
//   edge) and it reaches no other wall, the slides carry it onto itself as well. A point in such a ball never leaves
//   it, so if the ball lies between the two walls nothing in it is ever INSIDE: the whole ball is free. These balls
//   have their centres at the height zm of the circle where the two spheres cross, and
//   radius^2 = (distance of the centre from the middle line)^2 - q0^2, q0 the radius of that circle. Used here:
//   the ring round the circle (all such balls that reach 1/2 from the middle line; the spindle's formula with
//   d2 = -q0^2), the ball centred on the wall of the cell that m leans towards (as far along the wall as the cell
//   lets it), and the ball centred on the nearest upright edge of the cell. In the flat picture the round holes
//   ARE these balls, so there the room is the true distance to the rim of the hole.
// C. The side ring. Where rho > 1/2 the second sphere and its copy at the next whole number cross in a circle that
//   stands in the wall of the cell, and beside it the room of B is zero although nothing is near. Both inversions
//   carry every ring round that circle onto itself and the top wall onto itself; the half ring under the wall holds
//   no ball as long as it stays clear of the first sphere and of its copy (w <= wA below) and inside the two cells
//   (|across| <= clip). The side spindle's formula with c2 = 1/4 - rho^2 < 0.
// D. The depth of the search. A point that is still undecided when the rounds run out counts as INSIDE, and the
//   rooms of B and C say nothing about that: they are rooms of the object at endless depth. Where the two spheres
//   cut into each other the holes of the picture are made of many mirror images of one small piece, one round of
//   the search apart, and with the dial at 16 the far side of a hole is still undecided: the hole comes out smaller
//   than it is. So those rooms are made smaller by the rounds the search had left when it ended: none at all with
//   fewer left than the fan round the crossing circle has pieces (pi / the angle between the spheres), and from
//   there on the share 1 - exp(-rhoT (left - fan)), rhoT the size of one piece as the hole measures it. With no
//   round left only the two sphere surfaces themselves are trusted. This part is fitted to the reference, not
//   proved (out/r29/free/NOTES.md says what was measured). Where the spheres are apart (A) nothing is taken off,
//   as in the two programs above.
// E. The Drawing radius. With these pairs of numbers the far distance is often INSIDE, and the 3D picture is then
//   one lump as large as the Drawing radius (ballsTrouble says so). Nothing beyond the Drawing radius is drawn, but
//   the distance knew nothing of it: the skin of the lump lay inside the solid, no light reached it and it came out
//   black. So for every query of the 3D picture (gPix > 0: the ray, its slope, its shadow) the solid ends at the
//   Drawing radius: the larger of the distance above and (distance from the middle - Drawing radius). The lump then
//   has a round skin that is lit like any other. The 2D view and a 3D model (gPix = 0) are not touched, and neither
//   is the twin in JavaScript, which does not know the picture.
const GL_BALLS_FREE = `
const bool ORBIT_SCENE = false;
uniform float uBT, uBRho; uniform int uBGrid;
const float BALLS_K2 = ${BALLS_K2.toFixed(4)};
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// the whole number of the grid nearest to q (what the slide takes away)
vec2 bnear(vec2 q){
  if (uBGrid == 2) return vec2(floor(q.x + 0.5), 0.0);
  if (uBGrid == 0) return floor(q + 0.5);
  float b0 = floor(q.y / 0.8660254038 + 0.5), bd = 1e30;
  vec2 best = vec2(0.0);
  for (int j = -1; j <= 1; j++){
    float b = b0 + float(j), a = floor(q.x + 0.5 * b + 0.5);
    vec2 s = vec2(a - 0.5 * b, 0.8660254038 * b), w = q - s;
    float d = dot(w, w);
    if (d < bd){ bd = d; best = s; }
  }
  return best;
}
// the k-th whole number round the middle one: 0 the middle itself, then the ones next to it, then (square grid) the
// four on the diagonals
vec2 bround(int k){
  if (k == 0) return vec2(0.0);
  if (uBGrid == 2) return vec2(k == 1 ? 1.0 : -1.0, 0.0);
  if (uBGrid == 0) return k == 1 ? vec2(1.0, 0.0) : k == 2 ? vec2(-1.0, 0.0) : k == 3 ? vec2(0.0, 1.0) : k == 4 ? vec2(0.0, -1.0)
    : vec2(k < 7 ? 1.0 : -1.0, k == 5 || k == 7 ? 1.0 : -1.0);
  float a = float(k - 1) * 1.0471975512;
  return vec2(cos(a), sin(a));
}
// a length that is no longer than the distance to the cell of a whole number (d: the point less that number)
float bcell(vec2 d){
  if (uBGrid == 2) return max(abs(d.x) - 0.5, 0.0);
  if (uBGrid == 0) return length(max(abs(d) - 0.5, 0.0));
  return max(max(abs(d.x), max(abs(0.5 * d.x + 0.8660254038 * d.y), abs(0.5 * d.x - 0.8660254038 * d.y))) - 0.5, 0.0);
}
// a room e at the place z, carried back to the picture
float bback(float e, vec3 z, vec3 W, float DF){ float L = length(z - W), x = max(e, 0.0); return x * L / ((L + x) * DF); }
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, rr = uBRho * uBRho;
  bool apart = top - 1.0 - uBRho >= -1e-6;
  // A: the two fixed points on the middle line, the two hull balls and the spindle (see above GL_BALLS_RHO)
  float sD = max(top - 1.0 - uBRho, 0.0) * (top - 1.0 + uBRho) / top, sQ = sqrt(sD * (sD + 4.0));
  float HB = 1.0 / (1.0 + 0.5 * (sD + sQ)), HT = rr / (top - HB), hzm = 1.0 + 0.5 * sD, d2 = 0.25 * sD * (sD + 4.0);
  float restB = uBGrid == 0 ? 0.5 * HB : uBGrid == 1 ? HB / 3.0 : 0.25 * HB, restT = rr * HT;
  float rT = min(uBRho, 2.0 * rr / (1.0 + sqrt(max(1.0 - 4.0 * rr, 0.0))) + restT);
  float sw = min(0.5, top - hzm + uBRho), sa = (sw * sw - d2) / (2.0 * sw), sR = (sw * sw + d2) / (2.0 * sw);
  // C: the side spindle (rho <= 1/2) or the side ring (rho > 1/2)
  float tc2 = 0.25 - rr, tK = top * top - 1.0 + rr, tdisc = tK * tK + 4.0 * (top * top - 1.0) * tc2;
  float tlim = uBGrid == 2 ? 1e9 : uBGrid == 0 ? 0.5 : 0.2886751346, tclip = 1e9;
  float tw = (tK + sqrt(max(tdisc, 0.0))) / (2.0 * (top + 1.0));
  bool sideOn = tdisc >= 0.0;
  // (asked of rho itself, not of its square: at exactly 1/2 the card's rounding must not choose)
  bool upto = uBRho <= 0.5;
  if (upto) tw = min(tw, min(tlim, (uBGrid == 1 ? 0.8660254038 : 1.0) - uBRho));
  else { sideOn = sideOn && tw * tw > -tc2 * 1.0000001; tclip = tlim * -tc2 / (tw * tw); }
  sideOn = sideOn && tw > 0.0;
  float ta = (tw * tw - tc2) / (2.0 * tw), tR = (tw * tw + tc2) / (2.0 * tw);
  // B: the circle where the two spheres cross (height zm, radius q0), the ring round it, the balls on the walls and
  // on the upright edges of the cell
  float zm = (top * top + 1.0 - rr) / (2.0 * top), dd = zm * zm - 1.0, q0 = sqrt(max(-dd, 0.0)), hmin = min(zm, top - zm);
  float rw = min(0.5, top - zm + uBRho), ra = (rw * rw - dd) / (2.0 * rw), rR = (rw * rw + dd) / (2.0 * rw);
  bool ringOn = rw * rw + dd > 0.0;
  // (a ball centred on a wall of the cell stays under the top wall only while its centre is no further along the
  //  wall than sqrt(rho^2 - 1/4): so there is none for a second sphere of half the first's size or less)
  float slab = rr - 0.25;
  float ylim = slab > 1e-5 ? min(uBGrid == 0 ? -dd : uBGrid == 1 ? 2.0 * (q0 - 0.4330127019) : 1e9, sqrt(slab)) : -1.0;
  float er2 = (uBGrid == 0 ? 0.5 : 1.0 / 3.0) + dd;
  float edge = uBGrid != 2 && er2 > 0.0 && sqrt(max(er2, 0.0)) <= min(hmin, uBGrid == 0 ? 1.0 : 0.5) ? sqrt(max(er2, 0.0)) : -1.0;
  // D: the depth of the search
  float gv = q0 < 0.5 ? 0.5 : uBGrid == 0 ? 0.7071067812 : uBGrid == 1 ? 0.5773502692 : q0 + 0.25;
  float kap = sqrt(max(gv - q0, 1e-9) / (gv + q0)), rhoT = log((1.0 + kap) / (1.0 - kap));
  // (a hair under, so that rounding does not decide where the fan has a whole number of pieces)
  float fan = 3.1415926536 / max(3.1415926536 - acos(clamp((1.0 + rr - top * top) / (2.0 * uBRho), -1.0, 1.0)), 1e-6) - 1e-3;
  float fanS = !upto ? 3.1415926536 / max(3.1415926536 - acos(clamp((2.0 * rr - 1.0) / (2.0 * rr), -1.0, 1.0)), 1e-6) - 1e-3 : 0.0;
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (see gLand in GL_HEAD); none while the trap alone is the solid, because then the balls are
  // not in the picture. The distances here are lengths of the picture already, so it is used as it comes.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5, inside = false, decided = false;
  float land = walls ? gLand : 0.0;
  trapStart();
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5;
  float bestT = 1e9;
#endif
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
    // The trap as a solid: every point whose chain, from round uTrapSkip on, comes within uTrapW of the trap shape.
    // The length is carried back to the picture the way "free" is.
#if TRAP_SOLIDS
    if (trapSolid && i >= uTrapSkip){
      float dq = trapDist(tv), et = dq - uTrapW, L = sqrt(L2);
      float sc = (et > 0.0 ? et * L / (L + et) : et) / DF;
      if (sc < bestT){ bestT = sc; gTouch = vec4(tv - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
    }
#endif
    // a hit's trap colour: the search is over at the first round that lands within the landing length of a ball,
    // and that point is fed to the trap as a point of the wall itself
    bool landed = land > 0.0 && cand < land;
    if (landed){ tv.x = hb < ht ? -uBT : uBT; free = 1e9; }
    trapAdd(tv, it); gLast = tv;
    if (landed || hb < 0.0 || ht < 0.0){ inside = hb < 0.0 || ht < 0.0; decided = true; break; }
    vec3 zt = vec3(z.xy, z.z - top);
    float rb = dot(z, z), rt = dot(zt, zt);
    if (rb < 1.0){
      float s = 1.0 / max(rb, 1e-20);
      z *= s; W /= max(dot(W, W), 1e-20); DF *= s;
    } else if (rt < rr){
      float s = rr / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt * (rr / max(dot(Wt, Wt), 1e-20)); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see above this program).
      float q = length(z.xy);
      // the whole number next to the middle one that the point leans towards, along it and across it
      float al = abs(z.x), ac = z.y;
      if (uBGrid == 0 && abs(z.y) > al){ al = abs(z.y); ac = z.x; }
      if (uBGrid == 1){
        float h1 = abs(0.5 * z.x + 0.8660254038 * z.y), h2 = abs(0.5 * z.x - 0.8660254038 * z.y);
        if (h1 > al){ al = h1; ac = 0.5 * z.y - 0.8660254038 * z.x; }
        if (h2 > al){ al = h2; ac = 0.5 * z.y + 0.8660254038 * z.x; }
      }
      // C: the side spindle or the side ring
      float side = -1.0;
      if (sideOn){
        float tl = al - 0.5, tq = length(vec2(ac, ht));
        side = min((tc2 - tl * tl + tq * (2.0 * ta - tq)) / (tR + length(vec2(tl, tq - ta))), tclip - abs(ac));
      }
      if (apart){
        // A: the hulls
        float cb = length(vec3(z.xy, hb - 0.5 * HB)) - 0.5 * HB, ct = length(vec3(z.xy, ht - 0.5 * HT)) - 0.5 * HT;
        float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
        float e = max(min(min(cb, ct), min(lo - restB, max(hi - restT, sqrt(rt) - rT))), 0.0), dz = z.z - hzm;
        if (d2 < 3.0) e = max(e, (d2 + q * (2.0 * sa - q) - dz * dz) / (sR + length(vec2(q - sa, dz))));
        free = bback(max(e, side), z, W, DF);
      } else {
        // B: looking through the first sphere (zA) and through the second (zB)
        float left = float(uIter - 1 - i), sA = 1.0 / max(rb, 1e-20), sB = rr / max(rt, 1e-20);
        vec3 C = vec3(0.0, 0.0, top), zA = z * sA, WA = W / max(dot(W, W), 1e-20), Wt = W - C;
        vec3 zB = C + zt * sB, WB = C + Wt * (rr / max(dot(Wt, Wt), 1e-20)), dA = zA - WA, dB = zB - WB;
        float DFA = DF * sA, DFB = DF * sB;
        float bud = min(kpearl(top - zA.z, top - WA.z, 4.0 / max(dot(dA, dA), 1e-30)) / DFA, kpearl(zB.z, WB.z, 4.0 / max(dot(dB, dB), 1e-30)) / DFB);
        float eA = 0.5, eB = 0.5;
        int nc = uBGrid == 2 ? 3 : uBGrid == 0 ? 9 : 7;
        for (int k = 0; k < 9; k++){
          if (k >= nc) break;
          vec2 c = bround(k), a2 = zA.xy - c, b2 = zB.xy - c;
          float fa = bcell(a2), fb = bcell(b2);
          eA = min(eA, max(length(vec3(a2, zA.z - top)) - uBRho, fa));
          if (uBGrid == 0 && k >= 5) eA = min(eA, max(length(vec3(a2, zA.z)) - 1.0, fa));
          eB = min(eB, max(length(vec3(b2, zB.z)) - 1.0, fb));
          if (k >= 1) eB = min(eB, max(length(vec3(b2, zB.z - top)) - uBRho, fb));
        }
        eA = max(eA, 1.0 - length(zA)); eB = max(eB, uBRho - length(zB - C));
        free = left < 1.0 ? min(bback(sqrt(rb) - 1.0, z, W, DF), bback(sqrt(rt) - uBRho, z, W, DF)) : min(bback(eA, zA, WA, DFA), bback(eB, zB, WB, DFB));
        // the ring round the crossing circle, the ball on the wall, the ball on the upright edge
        float dz = z.z - zm;
        float ring = ringOn ? (dd + q * (2.0 * ra - q) - dz * dz) / (rR + length(vec2(q - ra, dz))) : -1.0, whole = ring;
        if (ylim >= 0.0){
          float yc = clamp(ac, -ylim, ylim), r2 = 0.25 + yc * yc + dd;
          if (r2 > 0.0) whole = max(whole, sqrt(r2) - length(vec3(al - 0.5, ac - yc, dz)));
        }
        if (edge > 0.0){
          vec2 ev = vec2(z.x < 0.0 ? -0.5 : 0.5, z.y < 0.0 ? -0.5 : 0.5);
          if (uBGrid == 1){ float a0 = (floor(atan(z.y, z.x) / 1.0471975512) + 0.5) * 1.0471975512; ev = vec2(cos(a0), sin(a0)) * 0.5773502692; }
          whole = max(whole, edge - length(vec3(z.xy - ev, dz)));
        }
        // D: the depth of the search
        float wholeP = left >= fan ? bback(whole, z, W, DF) * (1.0 - exp(-rhoT * (left - fan)))
          : left >= 0.5 * fan + 1.0 && ringOn ? bback(min(ring, length(vec2(q - q0, dz))), z, W, DF) : -1.0;
        float sideP = bback(side, z, W, DF) * (!upto ? 1.0 - exp(-rhoT * max(left - fanS, 0.0)) : max(left - 1.0, 0.0) / (left + 8.0));
        free = max(free, max(wholeP, sideP));
        if (left >= 1.0) best = min(best, bud);
      }
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // E (see above this program): in the 3D picture the solid ends at the Drawing radius
  if (gPix > 0.0) d = max(d, length(p) - (uBound > 0.0 ? uBound : 8.0));
  // (the trap solid: as in GL_BALLS, the page never asks this group for one)
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
