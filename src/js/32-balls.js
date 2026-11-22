// Balls on balls: the second group of the Kleinian view, a picture made only of slides by whole numbers and sphere
// inversions (no c, no power). Its numbers, its three shader programs and the JavaScript twin of their recipe.
//
// State in S.k: group (1: this group), bt (t = top / 2), brho (rho, the radius of the second sphere: 0.02 to 1),
// bgrid (0 square grid, 1 honeycomb grid, 2 a line only), bit (rounds of the recipe).
// The recipe, in the object's own coordinates m, with top = 2t:
//   repeat: if m.z < 0 or m.z > top (beyond one of the two walls): INSIDE.
//           Slide (m.x, m.y) by the nearest whole number of the grid.
//           If |m| < 1: m -> m / |m|^2                              (the first sphere: radius 1 about (0, 0, 0)).
//           Else if |m - (0, 0, top)| < rho: m -> (0, 0, top) + rho^2 (m - (0, 0, top)) / |m - (0, 0, top)|^2
//                                                                   (the second sphere: radius rho about (0, 0, top)).
//           Else: OUTSIDE.
//   A point still undecided when the rounds run out counts as INSIDE.
// One sphere inversion at the start (centre (0, 0, 1) in m, radius k, k^2 = 1.05) brings the picture into the lab's
// frame: x along the chain, y up in the flat plane, z out of the flat plane. The middle ball is k^2 wide and its two
// big neighbours k^2 / (top - 1), whatever rho is.
// The two spheres touch at top = 1 + rho and cut into each other below that. With rho between 1/2 and 1 the copies
// of the second sphere at neighbouring whole numbers cut into each other. Either way the balls run into one another.
const BALLS_K2 = 1.05, BALLS_T = 1.4, BALLS_ROUNDS = 16, BALLS_ROUNDS_MIN = 1, BALLS_ROUNDS_FEW = 5, BALLS_S3 = Math.sqrt(3);
// rho runs from BALLS_RHO_MIN to 1; up to BALLS_RHO_HALF the copies of the second sphere at neighbouring whole
// numbers do not cut into each other. BALLS_T_MIN keeps top - 1 > 0.
const BALLS_RHO_MIN = 0.02, BALLS_RHO_HALF = 0.5, BALLS_T_MIN = 0.5001;
const BALLS_NAME = 'Balls on balls', BALLS_TAG = 'a cousin of the flat picture: no c, no power';
const BALLS_GRIDS = [[0, 'Square grid (four-fold)'], [1, 'Honeycomb grid (six-fold)'], [2, 'A line only (buds only round the flat picture)']];
const BALLS_NOTE = 'Made only of slides by whole numbers and sphere inversions, so every body is an exact ball. It is a cousin of the flat picture: its flat cut is a chain of circles. It has no c and no power.';
const ballsOn = () => S.k.group === 1;                 // this group is the one the Kleinian view holds
const ballsShown = () => S.mode === 'k' && ballsOn();  // and it is on show
// rho as the programs use it: the state's number held to BALLS_RHO_MIN ... 1.
function ballsRho(r = S.k.brho) { return Math.min(1, Math.max(BALLS_RHO_MIN, r)); }
// t as the programs use it: the state's number, kept above 1/2 by a hair.
const ballsT = (t = S.k.bt) => Math.max(BALLS_T_MIN, t);
// Which of the three programs draws a pair (t, rho); 40-render.js builds each under its own key:
//   'balls'   GL_BALLS: two equal spheres that are apart or touch (rho = 1, t >= 1);
//   'ballsSmall'  GL_BALLS_RHO: a second sphere of half the first's size or less, apart from the first or touching it;
//   'ballsFree'  GL_BALLS_FREE: every other pair (the two spheres cut into each other, or rho lies between 1/2 and 1).
const ballsApart = (t, rho) => 2 * t - 1 - rho >= -1e-9;   // the two spheres are apart, or touch
const ballsKind = (t = ballsT(), rho = ballsRho()) => (rho === 1 && t >= 1 ? 'balls' : rho <= BALLS_RHO_HALF && ballsApart(t, rho) ? 'ballsSmall' : 'ballsFree');
// t as a program is handed it (uBT): GL_BALLS_RHO never gets a t under the touching value.
const ballsTOf = (kind, t = ballsT(), rho = ballsRho()) => (kind === 'ballsSmall' ? Math.max((1 + rho) / 2, t) : t);
// How the two spheres stand to each other as the two dials show their numbers: -1 apart, 0 touching, 1 cutting.
// The dials show two decimals, so a product of the shown numbers that could be 100 x 100 within their rounding
// counts as touching.
function ballsMeet(t = S.k.bt, rho = ballsRho()) {
  t = ballsT(t);
  if (rho === 1) return t > 1 ? -1 : +ballsShare(t).toFixed(2) > 100 ? 1 : 0;
  if (Math.abs(2 * t - 1 - rho) <= 1e-9) return 0;
  const p = ballsShare(t), r = 100 * rho, over = p * r - 10000, tol = 0.005 * (p + r);
  return over > tol ? 1 : over >= -tol ? 0 : -1;
}
// The dial "Size of the neighbours" shows p: the width of the two big neighbours as a percentage of the middle ball.
const ballsShare = t => 100 / (2 * t - 1);
const ballsFromShare = p => (Math.abs(p - ballsShare(BALLS_T)) < 0.06 ? BALLS_T : Math.max(BALLS_T_MIN, 0.5 * (100 / Math.max(p, 1e-6) + 1)));
// The dial "Second sphere" shows 100 rho, with two decimals.
const ballsRhoShown = () => +(100 * ballsRho()).toFixed(2);
const ballsRhoFrom = v => Math.min(1, Math.max(BALLS_RHO_MIN, v / 100));
// The two dials. Each sets its own number and nothing else.
function ballsSetShare(p) { S.k.bt = ballsFromShare(ballsRho() < 1 ? +(+p).toFixed(2) : +p); }
function ballsSetRho(v) { S.k.brho = ballsRhoFrom(+(+v).toFixed(2)); }
// Two numbers of the hulls while the two spheres are apart (see above GL_BALLS_RHO): HB, the diameter of the hull
// ball on the bottom wall, and end = z2 - 1, z2 the upper fixed point on the middle line.
function ballsHulls(t, rho) {
  // Written from D = s - 2, which is 0 when the spheres touch, so that nothing large is taken from something large.
  const top = 2 * t, gap = Math.max(top - 1 - rho, 0), D = gap * (top - 1 + rho) / top, sq = Math.sqrt(D * (D + 4));
  return { HB: 1 / (1 + 0.5 * (D + sq)), end: 0.5 * (D + sq) };
}
// How far the chain reaches from the middle of the picture, along x: it runs out at the two fixed points on the
// middle line, which the frame carries to x = +-reach. Infinity where the two spheres touch or cut into each other.
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
// The inside test, for the dials as they stand: the JavaScript twin of the shaders' recipe. Picture coordinates.
function ballsInside(x, y, z) {
  const rho = ballsRho(), r2 = rho * rho;
  const t = ballsT(), grid = S.k.bgrid;
  const rounds = S.k.bit, top = 2 * t;
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
// The spindle is used while the neighbours are large (rho = 1: t under BALLS_SPINDLE_T; rho < 1: d2 under 3, which
// is the same line); for smaller ones the room the hulls give is always the larger.
const BALLS_SPINDLE_T = 2;
const BALLS_FAR = 40;   // a chain that reaches further than this from the middle is not framed whole
// From how far (at the starting field of view) the ball of radius r about the picture point c is wholly in a picture
// `asp` times as wide as high, for an eye that looks at the middle from the direction (yaw, pitch), with 8 % of air
// round it. Exact for a ball: the eye's four side planes, each kept r away from the centre.
function ballsSee(c, r, asp, yaw, pitch) {
  const cp = Math.cos(pitch), off = [cp * Math.cos(yaw), cp * Math.sin(yaw), Math.sin(pitch)];
  const right = norm(cross(scl(off, -1), [0, 0, 1])), up = cross(right, scl(off, -1));
  const f = CAM_FOV0 / 1.08, g = f * asp;
  return dot(c, off) + Math.max((Math.abs(dot(c, up)) + r * Math.hypot(1, f)) / f, (Math.abs(dot(c, right)) + r * Math.hypot(1, g)) / g);
}
// The start view: the whole chain in the picture, seen from a little above the flat plane so that the buds off the
// flat picture show. { yaw, pitch, dist (at the starting field of view), h (span of the 2D view), room }.
function ballsCam() {
  const w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight), asp = w / h, rho = ballsRho(), t = ballsT();
  if (rho === 1 && t >= 1) {
    const r = Math.min(ballsReach(), 4.5);
    return { yaw: -1.25, pitch: 0.5, dist: Math.max(3.3, 3.6 * r / asp), h: Math.max(2.1, 2.25 * r / asp), room: Math.min(r + 0.4, 8) };
  }
  // Every other pair: the neighbours may be larger than the middle ball. `tall` is how far the picture reaches from
  // the middle line: a neighbour's own radius, or the middle ball with the largest bud on its waist (`waist`; for rho
  // between 1/2 and 1 with the spheres apart the hull of that bud, k^2 HB / (2 - HB) beyond the middle ball).
  // A chain longer than BALLS_FAR, or one with no end, is framed as a stretch: the middle ball, its two neighbours
  // and some of what follows.
  const p = ballsShare(t), reach = ballsReach(t, rho);
  const whole = reach <= BALLS_FAR, r = whole ? reach : Math.max(4.5, BALLS_K2 * (0.5 + 1.5 * p / 100));
  const HBw = rho > BALLS_RHO_HALF && 2 * t - 1 - rho > 1e-9 ? ballsHulls(t, rho).HB : 0;
  const waist = BALLS_K2 / 2 + (HBw > 0 ? BALLS_K2 * HBw / (2 - HBw) : BALLS_K2 / (4 * t - 1));
  const tall = Math.max(BALLS_K2 * p / 200, waist);
  // The balls the picture has to hold, each seen whole (ballsSee): the middle ball with the buds on its waist, the two
  // big neighbours, and, when the chain is framed whole, the ball that holds the rest of the chain at either end.
  const yaw = -1.25, pitch = 0.5, rN = BALLS_K2 * p / 200, xN = BALLS_K2 / 2 + rN, rE = Math.max(0, (reach - xN - rN) / 2);
  let see = ballsSee([0, 0, 0], waist, asp, yaw, pitch);
  for (const sg of [-1, 1]) {
    see = Math.max(see, ballsSee([sg * xN, 0, 0], rN, asp, yaw, pitch));
    if (whole && rE > 0) see = Math.max(see, ballsSee([sg * (reach - rE), 0, 0], rE, asp, yaw, pitch));
  }
  // room, the Drawing radius the view wants: the whole chain with a little air, or, for a stretch of a chain, so much
  // more that the place where the Drawing radius cuts a ball open lies outside the picture.
  return { yaw, pitch, dist: Math.max(3.3, 3.6 * r / asp, 3.75 * tall, see), h: Math.max(2.1, 2.25 * r / asp, 2.4 * tall), room: whole ? r + 0.4 : 2 * r };
}
// "Frame it", and what the row in the Approach list does to the camera: the start view, with a zoom limit or a
// Drawing radius that is in the way moved.
function ballsFrame() {
  const b = ballsCam();
  presetRoom(presetDist(b.dist, 1), b.room);
  if (S.v2.hmax < b.h) S.v2.hmax = b.h;
  resetCam();
  touch();
}
// Two answers for ballsTrouble, each found by asking ballsInside and kept until the numbers it was asked for change.
const BALLS_ASK = { far: '', farIs: false, flat: '', flatIs: false };
// Is the picture one lump as large as the Drawing radius? Yes when the recipe says INSIDE at fourteen directions and
// two distances far beyond the Drawing radius, and at three in ten or more of 120 directions spread evenly on the
// ball of the Drawing radius itself (a lump may have holes; a band of balls with open sky round it is not a lump).
function ballsFarFilled() {
  const t = ballsT(), bound = S.view.bound, base = Math.max(bound, BALLS_K2 * (0.5 + ballsShare(t) / 100));
  const key = [t, ballsRho(), S.k.bgrid | 0, S.k.bit, bound, base].join('|');
  if (BALLS_ASK.far !== key) {
    let all = true;
    for (const far of [20, 2000]) for (let i = 0; i < 14 && all; i++) {
      // six along the axes, eight along the diagonals, a little off the straight so that no point lies in a mirror
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
function ballsTrouble() {
  if (!ballsShown()) return '';
  const rho = ballsRho(), t = ballsT(), p = ballsShare(t), out = [], pc = x => dialFmt(+x.toFixed(2));
  const what = S.flat ? 'circles' : 'balls', meet = ballsMeet(t, rho), touch = meet === 0, cutting = meet > 0;
  const lump = cutting && !S.flat && ballsFarFilled();
  // open: the Drawing radius is smaller than the neighbours themselves, and one of them shows as a flat wall. Not
  // where the picture is one lump: no Drawing radius makes room for that.
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
    out.push(`At ${pc(p)} the chain never ends, so the picture shows a stretch of it. Where the depth of the search runs out, the far ${what} and the places where two ${what} kiss come out swollen.`);
  } else if (rho < 1 && ballsReach(t, rho) > BALLS_FAR) {
    out.push('Here the chain is too long for one picture, so Frame it shows a stretch of it.');
  } else if (!open && !S.flat && ballsReach() > S.view.bound) out.push('The chain of balls runs out past the Drawing radius in the View section, so its far ends are not drawn.');
  if (open) out.push('The Drawing radius in the View section cuts the two big neighbours open. Frame it makes room for them.');
  if (rho < 1) {
    out.push(`The second sphere is now ${pc(100 * rho)} % of the first. Reset this section puts it back to 100.`);
    // At 50 the copies of the second sphere at neighbouring whole numbers kiss, and so do the buds on a neighbour.
    if (meet < 0 && ballsRhoShown() === 100 * BALLS_RHO_HALF) out.push('With the second sphere at 50 the buds on a neighbour kiss, and where the depth of the search runs out those places come out swollen.');
  }
  // With one round everything inside either sphere is still undecided, which is most of the picture.
  if (S.k.bit < BALLS_ROUNDS_FEW) out.push('With so few rounds of the search whole balls are still undecided, and they come out as broken shells.' +
    (S.k.bit < 2 ? ' With a single round most of the picture is one wall of colour.' : ''));
  return out.join(' ');
}

// The opening lines of the three programs of this group: the two uniforms all of them read, the frame's constant,
// the true distance to a ball (kpearl, see GL_KLEIN) and the slide.
const GL_BALLS_HEAD = `
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
}`;
// The scene program of this group. Same interface towards GL_HEAD, GL_COLOUR and GL_TAIL as GL_KLEIN: de() sets
// gEsc, gIt, gLast, gGrad and gOnTrap and feeds the colour trap (trapStart, trapAdd). This group has no trap solid
// (25-colour.js asks ballsShown). Uniforms: uBT = t, uBGrid = the grid.
//
// The distance is the smaller of "best" and "free", so it is never longer than the true distance to the nearest ball.
// best: every ball is the sphere that some chain of the moves carries onto one of the two walls (m.z = 0 and
//   m.z = 2t). For each wall the recipe's chain meets, kpearl gives the true distance to that ball (see GL_KLEIN),
//   with W the image of the point at infinity and DF the scale factor of the maps so far, the frame included.
// free: a length certainly free of balls, taken where the recipe ends OUTSIDE, because the nearest ball need not be
//   on the recipe's chain. There every ball other than the two walls lies inside a hull ball of diameter
//   H = t - sqrt(t^2 - 1) that stands on a wall at the nearest whole number, or within "the rest" of a wall: H / 2
//   (square grid), H / 3 (honeycomb), a tube of radius H / 4 round the line (line grid). With e the distance from m
//   to all of that, the point of the picture has the room e L / ((L + e) DF), L = |m - W|: exact for inversions.
// The spindle: a second room for large neighbours, where the two hull balls nearly touch and e is far too small.
//   The two inversions hold z = H and z = 1 / H = 2t - H on the middle line fixed and carry every circle through
//   both onto itself, so no ball reaches into the spindle swept by the arcs through both that reach 1/2 from the
//   line at mid-height z = t. In the (distance from the line, z) half-plane the arc is the circle of radius
//   1/4 + s^2 about (1/4 - s^2, t), s^2 = t^2 - 1; the room is that radius less the distance from its centre.
const GL_BALLS = GL_BALLS_HEAD + `
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, H = uBT - sqrt(max(uBT * uBT - 1.0, 0.0));
  float rest = uBGrid == 0 ? 0.5 * H : uBGrid == 1 ? H / 3.0 : 0.25 * H;
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (gLand in GL_HEAD) is used as it comes: the distances here are lengths of the picture.
  bool inside = false, decided = false;
  float land = gLand;
  trapStart();
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
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
      // OUTSIDE: how much room is certain here (see above GL_BALLS)
      float cb = length(vec3(z.xy, hb - 0.5 * H)) - 0.5 * H, ct = length(vec3(z.xy, ht - 0.5 * H)) - 0.5 * H;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo, hi) - rest), 0.0), L = sqrt(L2), s2 = uBT * uBT - 1.0;
      // The spindle. Written so that nothing large is taken from something large: beside the kiss the room is as
      // small as the distance from the middle line, and single precision would lose it in 1/4 - 1/4.
      float q = length(z.xy), dz = z.z - uBT;
      if (uBT < ${BALLS_SPINDLE_T.toFixed(1)}) e = max(e, (s2 + q * (0.5 - 2.0 * s2 - q) - dz * dz) / (0.25 + s2 + length(vec2(q - 0.25 + s2, dz))));
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // Undecided when the rounds ran out counts as inside, a hair deep. In the 3D picture (gPix > 0) "free" is not taken
  // below 1.25 to 2 ray thresholds, fewer with a longer ray step: it measures to hulls, not to balls, so close in it
  // would stop every ray a few pixels short.
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
// The same program for a second sphere smaller than the first ('ballsSmall'): uBRho = rho, its radius. What differs:
//   The second inversion has the scale factor rho^2 / |m - (0, 0, top)|^2 (for DF and for W).
//   The two fixed points on the middle line are z1 and z2 = 1 / z1, z1 + z2 = s = top + (1 - rho^2) / top (s = 2
//   when the two spheres touch). The hull balls differ: diameter HB = z1 standing on the bottom wall, diameter
//   HT = top - z2 hanging from the top wall (HB = 1 / (top - HT), HT = rho^2 / (top - HB)).
//   "The rest" on the bottom wall is HB / 2, HB / 3 or a tube of HB / 4; on the top wall it is rho^2 HT for all
//   three grids. Most of the top wall is bare: the buds of the rest touch it no further than
//   x = (1 - sqrt(1 - 4 rho^2)) / 2 from the second sphere's centre (x = rho^2 / (1 - x)). So the rest there is the
//   part of its slab within rT = min(rho, x + rho^2 HT) of that centre, and a point is at least
//   max(distance to the slab, distance to that ball) away from it.
//   The spindle's arc reaches w = min(1/2, top - zm + rho) at mid-height zm = s / 2, where it just touches the top
//   wall. In the half-plane (distance from the line, z) it is the circle about (a, zm) with radius R,
//   a = (w^2 - d2) / 2w, R = (w^2 + d2) / 2w, d2 = ((z2 - z1) / 2)^2. All of it is written from
//   D = s - 2 = (top - 1 - rho)(top - 1 + rho) / top, so that nothing large is taken from something large where the
//   two spheres nearly touch.
//   The side spindle: the spindle's argument for the second sphere and its copy at the next whole number n, both
//   centred on the top wall, 1 apart, kissing at rho = 1/2. The fixed points are C + x n and C + (1 - x) n,
//   C = (0, 0, top). The arc reaches w = min(top - HB, D - rho) from the line at C + n / 2 (D = 1 for the square
//   grid and for a line only, sqrt(3) / 2 for the honeycomb grid), which keeps the half spindle under the wall above
//   all that grows on the bottom wall and clear of the other copies. In the half-plane (v along the line from the
//   middle point, q the distance from the line) it is the circle about (0, a) with radius R, a = (w^2 - c2) / 2w,
//   R = (w^2 + c2) / 2w, c2 = 1/4 - rho^2; the room is R - |(v, q - a)|.
const GL_BALLS_RHO = GL_BALLS_HEAD + `
uniform float uBRho;
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, rr = uBRho * uBRho;
  // the two fixed points on the middle line, the two hull balls and the spindle
  float sD = max(top - 1.0 - uBRho, 0.0) * (top - 1.0 + uBRho) / top, sQ = sqrt(sD * (sD + 4.0));
  float HB = 1.0 / (1.0 + 0.5 * (sD + sQ)), HT = rr / (top - HB), zm = 1.0 + 0.5 * sD, d2 = 0.25 * sD * (sD + 4.0);
  float restB = uBGrid == 0 ? 0.5 * HB : uBGrid == 1 ? HB / 3.0 : 0.25 * HB, restT = rr * HT;
  float rT = min(uBRho, 2.0 * rr / (1.0 + sqrt(max(1.0 - 4.0 * rr, 0.0))) + restT);
  float sw = min(0.5, top - zm + uBRho), sa = (sw * sw - d2) / (2.0 * sw), sR = (sw * sw + d2) / (2.0 * sw);
  // the side spindle, between the second sphere and its copy at the next whole number
  float tc2 = max(0.25 - rr, 0.0), tw = min(top - HB, (uBGrid == 1 ? 0.8660254038 : 1.0) - uBRho);
  float ta = (tw * tw - tc2) / (2.0 * tw), tR = (tw * tw + tc2) / (2.0 * tw);
  // the frame, the search and the trap: the lines of GL_BALLS
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  bool inside = false, decided = false;
  float land = gLand;
  trapStart();
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
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
      // OUTSIDE: how much room is certain here (see above GL_BALLS_RHO)
      float cb = length(vec3(z.xy, hb - 0.5 * HB)) - 0.5 * HB, ct = length(vec3(z.xy, ht - 0.5 * HT)) - 0.5 * HT;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo - restB, max(hi - restT, sqrt(rt) - rT))), 0.0), L = sqrt(L2);
      // the spindle, written so that nothing large is taken from something large: R^2 - a^2 = d2
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
  gIt = uFlat > 0.5 ? it : it + 8.0;
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
// The same program for every other pair ('ballsFree'): the two spheres cut into each other (top < 1 + rho), or rho lies
// between 1/2 and 1 and the copies of the second sphere at neighbouring whole numbers cut into each other. What
// differs is "free", at the place m where the recipe ends OUTSIDE:
// A. The spheres apart or touching, rho between 1/2 and 1: the hulls and the spindle of GL_BALLS_RHO. The top wall
//   inside the cell is covered by the second sphere, so "the rest" is the part of its slab inside that sphere
//   (rT = rho). In place of the side spindle there is the side ring of C.
// B. The spheres cut into each other. There are no hulls. Seen from m every ball other than the two walls lies
//   inside the first sphere or inside the second, in the middle cell.
//   Looking through a sphere: the first sphere's inversion is applied to m although m is outside it, with DF and W
//   carried along. From there everything that counts is outside the sphere: the two walls (kpearl; the top wall is
//   the first bud behind the mirror, a ball the recipe's own chain never meets), the second sphere and its copies,
//   each in its own cell, and (square grid) the copies of the first sphere on the diagonals. The smallest of those
//   distances, or the distance to the first sphere's own surface from inside where that is the longer, is a room,
//   carried back with e L / ((L + e) DF). The same through the second sphere; the smaller of the two rooms is used.
//   Balls that every move carries onto themselves: a ball that crosses both spheres squarely, and lies in the middle
//   cell or has its centre on a wall or an upright edge of the cell and reaches no other wall. Between the two
//   walls the whole of such a ball is free. Its centre is at the height zm of the circle where the spheres cross,
//   and radius^2 = (distance of the centre from the middle line)^2 - q0^2, q0 the radius of that circle. Used: the
//   ring round the circle (the spindle's formula with d2 = -q0^2), the ball centred on the wall of the cell that m
//   leans towards, and the ball centred on the nearest upright edge. In the flat picture the round holes are these
//   balls.
// C. The side ring, for rho > 1/2: the second sphere and its copy at the next whole number cross in a circle that
//   stands in the wall of the cell, and beside it the room of B is zero. The half ring round that circle under the
//   top wall holds no ball while it stays clear of the first sphere and of its copy and inside the two cells
//   (|across| <= clip). The side spindle's formula with c2 = 1/4 - rho^2 < 0.
// D. The depth of the search. The rooms of B and C are rooms of the object at endless depth, but a point still
//   undecided when the rounds run out counts as INSIDE. So they shrink with the rounds the search had left: to
//   nothing with fewer left than the fan round the crossing circle has pieces (pi / the angle between the spheres),
//   then by the share 1 - exp(-rhoT (left - fan)), rhoT the size of one piece as the hole measures it. With no
//   round left only the two sphere surfaces are trusted. This part is fitted, not proved. In A nothing is taken off.
// E. The Drawing radius. With these pairs the far distance is often INSIDE and the 3D picture is one lump. For every
//   query of the 3D picture (gPix > 0) the solid ends at the Drawing radius, so that the lump has a round, lit skin.
//   The 2D view and a 3D model (gPix = 0) are not touched.
const GL_BALLS_FREE = GL_BALLS_HEAD + `
uniform float uBRho;
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
  // asked of rho itself, not of its square: at exactly 1/2 the card's rounding must not choose
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
  // a ball centred on a wall of the cell stays under the top wall only while its centre is no further along the wall
  // than sqrt(rho^2 - 1/4): there is none for rho <= 1/2
  float slab = rr - 0.25;
  float ylim = slab > 1e-5 ? min(uBGrid == 0 ? -dd : uBGrid == 1 ? 2.0 * (q0 - 0.4330127019) : 1e9, sqrt(slab)) : -1.0;
  float er2 = (uBGrid == 0 ? 0.5 : 1.0 / 3.0) + dd;
  float edge = uBGrid != 2 && er2 > 0.0 && sqrt(max(er2, 0.0)) <= min(hmin, uBGrid == 0 ? 1.0 : 0.5) ? sqrt(max(er2, 0.0)) : -1.0;
  // D: the depth of the search
  float gv = q0 < 0.5 ? 0.5 : uBGrid == 0 ? 0.7071067812 : uBGrid == 1 ? 0.5773502692 : q0 + 0.25;
  float kap = sqrt(max(gv - q0, 1e-9) / (gv + q0)), rhoT = log((1.0 + kap) / (1.0 - kap));
  // a hair under, so that rounding does not decide where the fan has a whole number of pieces
  float fan = 3.1415926536 / max(3.1415926536 - acos(clamp((1.0 + rr - top * top) / (2.0 * uBRho), -1.0, 1.0)), 1e-6) - 1e-3;
  float fanS = !upto ? 3.1415926536 / max(3.1415926536 - acos(clamp((2.0 * rr - 1.0) / (2.0 * rr), -1.0, 1.0)), 1e-6) - 1e-3 : 0.0;
  // the frame, the search and the trap: the lines of GL_BALLS
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  bool inside = false, decided = false;
  float land = gLand;
  trapStart();
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
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
      // OUTSIDE: how much room is certain here (see above GL_BALLS_FREE)
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
  gIt = uFlat > 0.5 ? it : it + 8.0;
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // E: in the 3D picture the solid ends at the Drawing radius
  if (gPix > 0.0) d = max(d, length(p) - uBound);
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
