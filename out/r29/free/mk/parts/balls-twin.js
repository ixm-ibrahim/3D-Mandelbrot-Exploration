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
