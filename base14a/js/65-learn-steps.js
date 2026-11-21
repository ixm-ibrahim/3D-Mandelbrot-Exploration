// ---------- learn, the numbers: one step of the lab (z -> z^n + c) broken into simple moves. No DOM.
//
// learnPlan({ space, id, params, n, c, abs, flip }) -> { moves: [Move], note, ... }
//   space 1 | 2 | 3;  id an approach id;  params that approach's dials (S.param[id]);  n the power;
//   c a 3-vector;  abs [0|1, 0|1, 0|1] and flip [flip y, flip z]: the modifiers (S.abs, S.flip)
// Move = { key, name, say(a, b), at(v, t), hinge(v), sheet(v), hidden }
//   at(v, t): where the point v is after the fraction t of the move (at(v, 0) = v). Every move works from the
//   point it is given and nothing else, so the view can push any other point through the same chain.
// learnRun(plan, v) -> [v0, v1, ..., vk];  learnCheck(plan, v) -> |vk - the lab's own rule applied to v|.
// The plan also carries rule(v) (the lab's own rule for its space), run(v) and check(v), for the tests.
//
// The chain of moves ends exactly where MATH[id] (10-approaches.js) ends: every clamp and special case of that
// file is repeated here (the Mercator clamps, the fallback side of a point on an axis, the length cap aprPow).
// Where a move is not smooth (measured, out/r13/steps/): a Stretch is even on a log scale, so when a length changes
// by more than about e^20 in one move (the origin under a negative power, a tiny point under a high power) most of
// the distance is covered in the last few hundredths of the move. Two points exactly opposite on the sphere have no
// short way between them, and one way is picked (the "own" move of the Tried entries).
const learnRz = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return [c * v[0] - s * v[1], s * v[0] + c * v[1], v[2]]; };
const learnRx = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]]; };
const learnWrap = a => { const w = a - 2 * PI * Math.round(a / (2 * PI)); return w <= -PI ? w + 2 * PI : w; };   // into (-180°, 180°]
const learnIs = (n, k) => Math.abs(n - k) < 1e-9;

// ----- words. Angles in whole degrees, lengths to two decimals, a real minus sign.
function learnDeg(rad) { const d = Math.round(rad * 180 / PI); return (d < 0 ? '−' : '') + Math.abs(d) + '°'; }
function learnNum(x, coord) {
  if (!isFinite(x)) return 'more than the lab can count';
  const a = Math.abs(x);
  if (a >= 1e6 || (!coord && a > 1e-12 && a < 0.005)) {
    let e = Math.floor(Math.log10(a)), m = a / 10 ** e;
    if (+m.toFixed(1) >= 10) { m /= 10; e++; }
    return (x < 0 ? '−' : '') + m.toFixed(1) + ' × 10' + aprSup(e);
  }
  const s = a.toFixed(2);
  return (x < 0 && +s !== 0 ? '−' : '') + s;
}
const learnPt = (v, space) => (space === 1 ? learnNum(v[0], true) : '(' + (space === 2 ? [v[0], v[1]] : v).map(x => learnNum(x, true)).join(', ') + ')');
// "Squaring doubles it to ", "Cubing triples it to ", "The power 2.5 multiplies it by 2.5, to "
const learnMul = n => (learnIs(n, 2) ? 'Squaring doubles it to ' : learnIs(n, 3) ? 'Cubing triples it to ' : `The power ${aprNum(n)} multiplies it by ${aprNum(n)}, to `);
const learnPowWord = n => (learnIs(n, 2) ? 'squared' : learnIs(n, 3) ? 'cubed' : 'raised to the power ' + aprNum(n));
const learnSame = rad => (Math.abs(rad) > PI + 1e-9 ? ` (the same direction as ${learnDeg(learnWrap(rad))})` : '');
const LEARN_NO_DIR = 'The point is at the origin. It has no direction, so there is nothing to turn.';

// ----- small geometry
// the direction d carried the short way round the sphere toward the direction e, by the fraction t
function learnSlerp(d, e, t) {
  const c = clamp(dot(d, e), -1, 1);
  let w = sub(e, scl(d, c)), lw = len(w), ang = Math.atan2(lw, c);
  if (lw < 1e-12) {
    if (c > 0) return d;
    w = cross(d, Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]); lw = len(w); ang = PI;   // exactly opposite: no short way, one is picked
  }
  const om = ang * t;
  return add(scl(d, Math.cos(om)), scl(w, Math.sin(om) / lw));
}
// the length goes from |v| to R the way r^(1 + t(n - 1)) does (evenly on a log scale); the direction is kept.
// A point at the origin has no direction: `rule(v)` is where the rule itself sends it (no rule: it stays).
function learnScale(v, R, t, rule) {
  const r = len(v);
  if (!(r > 0)) {
    const T = rule ? rule(v) : null, L = T ? len(T) : 0;
    if (!(L > 0)) return [0, 0, 0];
    return scl(T, t >= 1 ? 1 : Math.exp((1 - t) * Math.log(1e-30) + t * Math.log(L)) / L);
  }
  if (t >= 1) return scl(v, R / r);
  return R > 0 ? scl(v, Math.exp(t * (Math.log(R) - Math.log(r)))) : [0, 0, 0];
}
const learnPowLen = (r, n) => (r < 1e-20 && n > 0 ? 0 : aprPow(r, n));
// a point's level direction (x, y)/rho; on the z-axis the lab's rules read the longitude as 0, the x direction
const learnLevel = v => { const rho = Math.hypot(v[0], v[1]); return rho > 0 ? [v[0] / rho, v[1] / rho, 0] : [1, 0, 0]; };
// Mercator latitude of a point, read from z and rho (well behaved near the poles)
const learnMerc = v => { const rho = Math.hypot(v[0], v[1]); return rho > 0 ? Math.asinh(v[2] / rho) : v[2] > 0 ? Infinity : v[2] < 0 ? -Infinity : 0; };
const learnFlat = v => Math.abs(v[2]) <= 1e-12 * len(v);   // in the plane z = 0, for the wording
const learnLat = v => Math.atan2(v[2], Math.hypot(v[0], v[1]));
// the Lathe move: the angle from the axis e is multiplied, in the sheet of e and the point. f: the side a point on
// the axis itself is taken to lean to.
function learnSide(v, e, f) {
  const x = dot(v, e), p = sub(v, scl(e, x)), rho = len(p);
  return { x, rho, u: rho > 0 ? scl(p, 1 / rho) : f };
}
function learnOpen(v, e, f, n, t) {
  const r = len(v);
  if (!(r > 0)) return v;
  const s = learnSide(v, e, f), a = Math.atan2(s.rho, s.x) * (1 + t * (n - 1));
  return add(scl(e, r * Math.cos(a)), scl(s.u, r * Math.sin(a)));
}

// ----- one move. `f(v, t)` is only asked for 0 < t <= 1.
function learnMove(key, name, f, say, o = {}) {
  return {
    key, name, hidden: !!o.hidden,
    at: (v, t) => (t > 0 ? f(v, Math.min(t, 1)) : [v[0], v[1], v[2]]),
    say(a, b) { return say(a, b || f(a, 1)); },
    hinge: o.hinge || (() => null), sheet: o.sheet || (() => null),
  };
}
const LEARN_Z = () => [0, 0, 1], LEARN_X = () => [1, 0, 0];
const LEARN_PAGE = () => [[1, 0, 0], [0, 1, 0]], LEARN_YZ = () => [[0, 1, 0], [0, 0, 1]];
const learnMeridian = v => (len(v) > 0 ? [learnLevel(v), [0, 0, 1]] : null);
const learnLevelHinge = v => { if (!(len(v) > 0)) return null; const u = learnLevel(v); return [-u[1], u[0], 0]; };

// ----- the moves
// Modifiers: each ticked coordinate goes to its mirror value, through 0.
function learnMirror(space, abs, flip) {
  const on = [!!abs[0], space > 1 && !!abs[1], space > 2 && !!abs[2]], fl = [false, space > 1 && !!flip[0], space > 2 && !!flip[1]];
  if (!on.some(Boolean) && !fl.some(Boolean)) return null;
  const goal = v => v.map((x, i) => (on[i] ? Math.abs(x) : x) * (fl[i] ? -1 : 1));
  const names = ['|x|', '|y|', '|z|'].filter((s, i) => on[i]).concat(['flip y', 'flip z'].filter((s, i) => fl[i + 1]));
  const f = (v, t) => { const g = goal(v); return t >= 1 ? g : v.map((x, i) => x + t * (g[i] - x)); };
  return learnMove('mirror', 'Mirror', f, (a, b) => {
    const ch = [0, 1, 2].filter(i => b[i] !== a[i] && !(b[i] === 0 && a[i] === 0)).map(i => `${'xyz'[i]} goes from ${learnNum(a[i], true)} to ${learnNum(b[i], true)}`);
    const which = names.length > 1 ? `The modifiers ${names.join(', ')} are ticked` : `The modifier ${names[0]} is ticked`;
    return ch.length ? `${which}, so before anything else ${ch.join(' and ')}, straight through 0.` : `${which}, but for this point that changes nothing.`;
  });
}
// The turn about the z-axis by (n - 1) times the angle around it. `what`: 'lean' (page), 'longitude' (space).
function learnTurnZ(n, space, what) {
  const f = (v, t) => learnRz(v, t * (n - 1) * Math.atan2(v[1], v[0]));
  const say = (a, b) => {
    const rho = Math.hypot(a[0], a[1]), th = Math.atan2(a[1], a[0]);
    if (space === 1) {
      const to = n * th, w = learnWrap(to);
      if (!(rho > 0)) return 'The point is 0. It has no side to lean to, so there is nothing to turn.';
      if (Math.abs(th) < 1e-12) return `A positive number leans 0° from the positive side, and 0° ${learnIs(n, 2) ? 'doubled' : learnIs(n, 3) ? 'tripled' : 'times ' + aprNum(n)} is still 0°. It stays where it is.`;
      const lands = Math.abs(Math.sin(to)) > 1e-9 ? `ends off the line, ${learnDeg(w)} round: on a line alone this power of a negative number has no answer`
        : Math.cos(to) > 0 ? 'lands on the positive side' : 'lands on the negative side again';
      if (learnIs(n, 1)) return 'A negative number leans 180° from the positive side. The power is 1, so the lean stays 180° and the point does not turn.';
      return `A negative number leans 180° from the positive side. ${learnMul(n)}${learnDeg(to)}${learnIs(w, 0) ? ', a full turn' : learnSame(to)}: the point swings through a direction the line does not have and ${lands}.`;
    }
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    if (!(rho > 0)) return what === 'flat' ? 'The point is on the z-axis: its flat part (x, y) is 0, so there is nothing to turn.' : `The point is on the z-axis, where it has no ${what}. This turn leaves it where it is.`;
    const head = space === 2 ? `The point leans ${learnDeg(th)} from the positive x-axis.` : what === 'flat' ? `The flat part (x, y) of the point leans ${learnDeg(th)} from the positive x-axis.` : `The point’s longitude, its angle around the z-axis, is ${learnDeg(th)}.`;
    if (learnIs(n, 1)) return `${head} The power is 1, so it stays ${learnDeg(th)} and the point does not turn.`;
    if (Math.abs(th) < 1e-12) return `${head} Any number times 0° is still 0°, so the point does not turn.`;
    return `${head} ${learnMul(n)}${learnDeg(n * th)}${learnSame(n * th)}: the point turns by ${learnDeg(Math.abs((n - 1) * th))} about the z-axis.`;
  };
  return learnMove('turn', 'Turn', f, say, { hinge: LEARN_Z, sheet: LEARN_PAGE, hidden: space === 1 });
}
// The stretch: the length r goes to r^n (the lab's own capped power). rule: the whole power, asked only at the origin.
function learnStretch(n, rule) {
  const f = (v, t) => learnScale(v, learnPowLen(len(v), n), t, rule);
  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(n, 'Its length', len(a), len(b)));
}
function learnSayStretch(n, what, r, R, flat) {
  if (!(r > 0)) return R > 0 ? `${flat ? 'The flat part of the point is 0' : 'The point is at the origin'}, and this power sends it outward: to a length of ${learnNum(R)}.`
    : `${flat ? 'The flat part of the point is 0' : 'The point is at the origin: its length is 0'}, and 0 ${learnPowWord(n)} is still 0. It stays.`;
  if (learnIs(n, 1)) return `${what} is ${learnNum(r)}. The power is 1, so it stays ${learnNum(r)}.`;
  const tail = R >= 1e18 ? ' That is as far as the lab counts.' : learnIs(r, 1) ? ' A length of exactly 1 stays 1.'
    : n > 1 ? (r < 1 ? ' A length under 1 gets shorter.' : ' A length over 1 gets longer.') : n < 0 ? ' A negative power turns short into long and long into short.' : '';
  return `${what}, ${learnNum(r)}, is ${learnPowWord(n)}: ${learnNum(R)}.${tail}`;
}
function learnShift(c, space) {
  const f = (v, t) => [v[0] + t * c[0], v[1] + t * c[1], v[2] + t * c[2]];
  return learnMove('shift', 'Add c', f, (a, b) => (space === 1 && Math.abs(a[1]) > 1e-9 * (1 + len(a))
    ? `Add c: the point moves by ${learnNum(c[0], true)} along the line, but it is still off the line: ${learnNum(Math.abs(a[1]))} out in the direction the line does not have.`
    : len(c) > 0
    ? `Add c: the point moves by ${learnPt(c, space)}, from ${learnPt(a, space)} to ${learnPt(b, space)}.`
    : `c is 0 here, so nothing is added: the point stays at ${learnPt(a, space)}.`));
}
// Sphere inversions: the Mercator latitude m is multiplied along the point's own meridian (clamps as in MATH.mercator)
function learnLeanMerc(n) {
  const f = (v, t) => {
    const r = len(v);
    if (!(r > 0)) return v;
    const Z = v[2] / r, m0 = Math.atanh(clamp(Z, -0.999999, 0.999999)), m1 = clamp(n * m0, -20, 20), u = learnLevel(v);
    if (t < 1 && Math.abs(Z) > 0.999999) {     // closer to a pole than the lab's Mercator scale reaches: go evenly in latitude
      const l0 = learnLat(v), l = l0 + t * (Math.atan(Math.sinh(m1)) - l0);
      return [r * Math.cos(l) * u[0], r * Math.cos(l) * u[1], r * Math.sin(l)];
    }
    const m = m0 + t * (m1 - m0), h = r / Math.cosh(m);
    return [h * u[0], h * u[1], r * Math.tanh(m)];
  };
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    if (learnFlat(a)) return 'The point lies in the flat plane: its latitude is 0°, and any number times 0° is 0°. It does not lean.';
    if (!(Math.hypot(a[0], a[1]) > 0)) return 'The point is on the z-axis, at a pole. On the scale a Mercator map uses a pole is endlessly far away, so the point stays at the pole, to within a hair.';
    const head = `Its latitude is ${learnDeg(learnLat(a))}, which is ${learnNum(learnMerc(a), true)} on the scale a Mercator map uses.`;
    if (learnIs(n, 1)) return `${head} The power is 1, so it stays there.`;
    return `${head} ${learnMul(n).replace(' it ', ' that number ')}${learnNum(learnMerc(b), true)}, which is latitude ${learnDeg(learnLat(b))}. On this scale a point can come close to a pole but never pass over it.`;
  };
  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });
}
function learnLift(lift) {
  const f = (v, t) => {
    const r = len(v);
    if (!(r > 0)) return v;
    const m0 = learnMerc(v), m = (isFinite(m0) ? m0 : m0 > 0 ? 20 : -20) + t * lift, u = learnLevel(v), h = r / Math.cosh(m);
    return [h * u[0], h * u[1], r * Math.tanh(m)];
  };
  const say = (a, b) => (len(a) > 0 ? `The Lift toward the pole dial adds ${learnNum(lift)} on the Mercator scale: the latitude goes from ${learnDeg(learnLat(a))} to ${learnDeg(learnLat(b))}.` : LEARN_NO_DIR);
  return learnMove('phase', 'Lift', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });
}
// a dial that adds an angle to the longitude: a plain turn about the z-axis
function learnTurnDial(rad, label, name) {
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    if (!(Math.hypot(a[0], a[1]) > 0)) return `The ${label} dial turns space by ${learnDeg(rad)} about the z-axis. The point is on that axis, so it stays.`;
    return `The ${label} dial adds ${learnDeg(rad)} to the longitude: it goes from ${learnDeg(Math.atan2(a[1], a[0]))} to ${learnDeg(Math.atan2(b[1], b[0]))}.`;
  };
  return learnMove('phase', name, (v, t) => learnRz(v, t * rad), say, { hinge: LEARN_Z, sheet: LEARN_PAGE });
}
// Sphere inversions, two planes: the turn about the x-axis that takes the point where foldk puts it
function learnFold(k) {
  const f = (v, t) => {
    const g = foldk(v, k);
    if (t >= 1) return g;
    return learnRx(v, t * learnWrap(Math.atan2(g[2], g[1]) - Math.atan2(v[2], v[1])));
  };
  const say = (a, b) => {
    if (!(Math.hypot(a[1], a[2]) > 0)) return len(a) > 0 ? 'The fold comes first. The point is on the x-axis, the crease of the fold, so it stays.' : 'The fold comes first. The point is at the origin, on the crease of the fold, so it stays.';
    const pa = Math.atan2(a[2], a[1]), pb = Math.atan2(b[2], b[1]);
    if (len(sub(a, b)) < 1e-12 * len(a)) return `The fold comes first, but it leaves this point alone: at ${learnDeg(pa)} around the x-axis it is already where the fold wants it.`;
    return `The fold comes first. Around the x-axis the point sits at ${learnDeg(pa)}, and the fold of ${aprNum(k)} planes carries it to ${learnDeg(pb)}.`;
  };
  return learnMove('fold', 'Fold', f, say, { hinge: LEARN_X, sheet: LEARN_YZ });
}
// Quaternion square: the angle from the axis is multiplied. tau: the tilt (0 for the Lathe), worked in the frame
// turned by the tilt, exactly as MATH.tilt does.
function learnLathe(n, tau, tilted) {
  const ex = [1, 0, 0], ey = [0, 1, 0];
  const f = (v, t) => learnRz(learnOpen(learnRz(v, tau), ex, ey, n, t), -tau);
  const side = v => learnSide(learnRz(v, tau), ex, ey);
  const axis = tilted ? 'the tilted axis' : 'the x-axis', pos = tilted ? 'the tilted axis' : 'the positive x-axis';
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    const s = side(a), al = Math.atan2(s.rho, s.x), to = n * al, sb = side(b), end = Math.atan2(sb.rho, sb.x);
    const head = tilted ? `Measured from the tilted axis (the Tilt of the axis dial is at ${learnDeg(tau)}), the point leans ${learnDeg(al)}.` : `The point leans ${learnDeg(al)} away from the positive x-axis.`;
    if (learnIs(n, 1)) return `${head} The power is 1, so the lean stays ${learnDeg(al)}.`;
    if (!(s.rho > 0) && s.x > 0) return `The point lies on ${pos}: its lean is 0°, and any number times 0° is 0°. It does not turn.`;
    const past = to > PI + 1e-9 || to < -1e-9 ? ` That is past the axis, so it ends ${learnDeg(end)} from ${pos}, on the far side.` : '';
    if (!(s.rho > 0)) return `The point lies on ${axis}, on the far side of the origin: it leans 180° and has no side to lean to, so the lab swings it through the ${tilted ? 'flat plane' : 'y direction'}. ${learnMul(n)}${learnDeg(to)}: it ${end < 0.01 ? 'lands on ' + pos : `ends ${learnDeg(end)} from ${pos}`}.`;
    return `${head} ${learnMul(n)}${learnDeg(to)}, in the flat sheet that holds ${axis} and the point.${past}`;
  };
  return learnMove('turn', 'Turn', f, say, {
    hinge: v => (len(v) > 0 ? learnRz(cross(ex, side(v).u), -tau) : null),
    sheet: v => (len(v) > 0 ? [learnRz(ex, -tau), learnRz(side(v).u, -tau)] : null),
  });
}
// Lathe: the angle round the x-axis times the spin multiplier
function learnSpin(spin) {
  const f = (v, t) => {
    const rho = Math.hypot(v[1], v[2]);
    if (!(rho > 0)) return v;
    const p = Math.atan2(v[2], v[1]) * (1 + t * (spin - 1));
    return [v[0], rho * Math.cos(p), rho * Math.sin(p)];
  };
  const say = (a, b) => {
    if (!(Math.hypot(a[1], a[2]) > 0)) return 'The point is on the x-axis, where it has no angle round the axis. The spin leaves it where it is.';
    const p = Math.atan2(a[2], a[1]);
    return `The Spin multiplier dial is at ${aprNum(spin)}: the point’s angle round the x-axis, ${learnDeg(p)}, is multiplied by it and becomes ${learnDeg(spin * p)}${learnSame(spin * p)}.`;
  };
  return learnMove('spin', 'Spin', f, say, { hinge: LEARN_X, sheet: LEARN_YZ });
}
// Twisted quaternion square: the turn back about the z-axis by (n - 1) times the tilt
function learnBack(n, tau) {
  const ang = -(n - 1) * tau;
  const say = (a, b) => {
    if (Math.abs(ang) < 1e-12) return 'There is nothing to turn back: the tilt times (n − 1) is 0°.';
    const amount = `Then all of space turns back about the z-axis by ${learnDeg(Math.abs(ang))}` + (learnIs(n, 2) ? ', the tilt.' : `: the tilt of ${learnDeg(tau)} times ${aprNum(n - 1)}.`);
    if (!(Math.hypot(a[0], a[1]) > 0)) return `${amount} The point is on that axis, so it stays.`;
    return `${amount} The point’s longitude goes from ${learnDeg(Math.atan2(a[1], a[0]))} to ${learnDeg(Math.atan2(b[1], b[0]))}.`;
  };
  return learnMove('back', 'Turn back', (v, t) => learnRz(v, t * ang), say, { hinge: LEARN_Z, sheet: LEARN_PAGE });
}
// Mandelbulb: the latitude (from the flat plane) or, classic, the angle from the z-axis is multiplied in the
// meridian sheet; the phase of that angle is added in the same move, because a point that has passed over the
// pole no longer shows which way its angle was growing.
function learnLeanBulb(n, phase, classic, label) {
  const f = (v, t) => {
    const r = len(v);
    if (!(r > 0)) return v;
    const u = learnLevel(v), rho = Math.hypot(v[0], v[1]);
    const a0 = classic ? Math.atan2(rho, v[2]) : Math.atan2(v[2], rho), a = a0 + t * ((n - 1) * a0 + phase);
    const h = r * (classic ? Math.sin(a) : Math.cos(a));
    return [h * u[0], h * u[1], r * (classic ? Math.cos(a) : Math.sin(a))];
  };
  const say = (a, b) => {
    if (!(len(a) > 0)) return LEARN_NO_DIR;
    const rho = Math.hypot(a[0], a[1]), a0 = classic ? Math.atan2(rho, a[2]) : Math.atan2(a[2], rho), mid = n * a0, to = mid + phase;
    const rb = Math.hypot(b[0], b[1]), end = classic ? Math.atan2(rb, b[2]) : Math.atan2(b[2], rb);
    const head = classic ? `Its angle from the z-axis is ${learnDeg(a0)}.` : learnFlat(a) ? 'The point lies in the flat plane: its latitude is 0°.' : `Its latitude is ${learnDeg(a0)}.`;
    const grow = learnIs(n, 1) ? ` The power is 1, so it stays ${learnDeg(a0)}.` : !classic && learnFlat(a) ? ' Any number times 0° is 0°.' : ` ${learnMul(n)}${learnDeg(mid)}.`;
    const add1 = phase ? ` The ${label} dial adds ${learnDeg(phase)}: ${learnDeg(to)}.` : '';
    const over = classic ? (to > PI + 1e-9 || to < -1e-9) : Math.abs(to) > PI / 2 + 1e-9;
    const past = over ? (classic ? ` That is past the axis, so it ends ${learnDeg(end)} from the z-axis, on the far side.` : ` That is past the pole, so it comes down the far side, at latitude ${learnDeg(end)}.`) : '';
    const leaves = classic && learnFlat(a) && Math.abs(b[2]) > 1e-9 * len(b) ? ' The point leaves the flat plane.' : '';
    return head + grow + add1 + past + leaves;
  };
  return learnMove('lean', 'Lean', f, say, { hinge: learnLevelHinge, sheet: learnMeridian });
}
// Split: the flat part (x, y) is stretched on its own, then the height on its own
function learnStretchFlat(m) {
  const f = (v, t) => {
    const rho = Math.hypot(v[0], v[1]), R = learnPowLen(rho, m), w = learnScale([v[0], v[1], 0], R, t, p => { const a = Math.atan2(p[1], p[0]) * m; return [R * Math.cos(a), R * Math.sin(a), 0]; });
    return [w[0], w[1], v[2]];
  };
  return learnMove('stretch', 'Stretch', f, (a, b) => learnSayStretch(m, 'The length of the flat part', Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1]), true) + ' The height is not touched.');
}
function learnHeight(m) {
  const f = (v, t) => {
    const az = Math.abs(v[2]);
    if (!(az > 0)) return [v[0], v[1], 0];
    const R = aprPow(az, m);
    if (t >= 1) return [v[0], v[1], R * (v[2] < 0 ? Math.cos(PI * m) : 1)];
    return [v[0], v[1], Math.exp(Math.log(az) + t * (Math.log(R) - Math.log(az))) * (v[2] < 0 ? Math.cos(PI * (1 + t * (m - 1))) : 1)];
  };
  const say = (a, b) => {
    if (!(Math.abs(a[2]) > 0)) return `The height is 0, and 0 ${learnPowWord(m)} is 0. The point stays level.`;
    if (learnIs(m, 1)) return `The height is ${learnNum(a[2], true)}. The power is 1, so it stays.`;
    return `The height, ${learnNum(a[2])}, is ${learnPowWord(m)} on its own, like a number on a line: ${learnNum(b[2])}.`
      + (a[2] < 0 ? ' On the way it passes through 0: the shadow of a swing through a direction that space does not have.' : '');
  };
  return learnMove('own', 'Height', f, say);
}
// Split, negative power: one sphere inversion with a mirror (y -> -y), as MATH.split ends
function learnInvert() {
  const most = Math.exp(APR_LOGCAP);
  const goal = u => { const L = len(u); return !(L * most > 1) ? [most, 0, 0] : [u[0] / L / L, -u[1] / L / L, u[2] / L / L]; };
  const f = (v, t) => {
    const g = goal(v), L = len(v);
    if (t >= 1) return g;
    if (!(L * most > 1)) return learnScale([0, 0, 0], most, t, () => g);
    return scl([v[0], (1 - 2 * t) * v[1], v[2]], Math.pow(L, -2 * t));   // y straight through 0, while everything is scaled by L^(-2t)
  };
  const say = (a, b) => {
    const L = len(a);
    if (!(L * most > 1)) return `A negative power ends by turning space inside out. The point is at the origin, which goes as far out as the lab counts: ${learnNum(len(b))}.`;
    return `A negative power ends by turning space inside out through the sphere of radius 1: the length goes from ${learnNum(L)} to ${learnNum(len(b))}, which is 1 divided by it, and y goes to its mirror value, from ${learnNum(a[1], true)} to ${learnNum(b[1], true)}.`;
  };
  return learnMove('own', 'Inside out', f, say);
}
// Any other rule F: the direction goes the short way round the sphere to where the rule sends it. together: the
// length goes with it in the same move (used when the rule's length depends on the direction).
function learnOwn(F, together) {
  const f = (v, t) => {
    const r = len(v), T = F(v), L = len(T);
    if (!(r > 0)) return together ? learnScale(v, L, t, () => T) : v;
    if (!(L > 0)) return together ? [0, 0, 0] : v;
    if (t >= 1) return together ? T : scl(T, r / L);
    return scl(learnSlerp(scl(v, 1 / r), scl(T, 1 / L), t), together ? Math.exp(Math.log(r) + t * (Math.log(L) - Math.log(r))) : r);
  };
  const turnOf = (a, b) => { const c = cross(a, b); return Math.atan2(len(c), dot(a, b)); };
  const say = (a, b) => {
    if (!(len(a) > 0)) return len(b) > 0 ? `The point is at the origin, and the rule sends the origin outward: to a length of ${learnNum(len(b))}.` : LEARN_NO_DIR;
    if (!(len(b) > 0)) return 'The rule sends this point to the origin.';
    const ang = turnOf(a, b), lens = together ? ` Its length goes from ${learnNum(len(a))} to ${learnNum(len(b))} on the way.` : '';
    if (ang < 1e-9) return 'The rule keeps this direction, so the point does not turn.' + lens;
    if (ang > PI - 1e-9) return 'The rule sends this direction to the exact opposite one, half way round the sphere. No way round is shorter than another, so one is picked.' + lens;
    return `The rule sends this direction ${learnDeg(ang)} round the sphere, and the point goes there the short way.` + lens;
  };
  const way = v => { const T = F(v); if (!(len(v) > 0) || !(len(T) > 0)) return null; const d = norm(v), w = sub(norm(T), scl(d, dot(d, norm(T)))); return len(w) > 1e-12 ? [d, norm(w)] : null; };
  return learnMove('own', 'Turn', f, say, { hinge: v => { const s = way(v); return s ? cross(s[0], s[1]) : null; }, sheet: way });
}
// the stretch that follows learnOwn: the length goes to the rule's length (the rule's length must not depend on the direction)
function learnStretchTo(F) {
  const f = (v, t) => learnScale(v, len(F(v)), t, F);
  const say = (a, b) => {
    if (!(len(a) > 0)) return len(b) > 0 ? `The point is at the origin, and the rule sends the origin outward: to a length of ${learnNum(len(b))}.` : 'The point is at the origin, and it stays there.';
    return `Then the length goes from ${learnNum(len(a))} to the rule’s length, ${learnNum(len(b))}.`;
  };
  return learnMove('stretch', 'Stretch', f, say);
}

// ----- the plans
// the flat rule: the complex power of x + iy (on a line: of the number x, with y the hidden direction); z passes through
function learnFlatRule(v, n) {
  const r = Math.hypot(v[0], v[1]);
  if (r < 1e-20 && n > 0) return [0, 0, v[2]];
  const R = aprPow(r, n), p = Math.atan2(v[1], v[0]) * n;
  return [R * Math.cos(p), R * Math.sin(p), v[2]];
}
// does the rule F agree with G at a handful of ordinary points?
function learnAgree(F, G, pts) {
  return pts.every(p => { const a = F(p), b = G(p); return len(sub(a, b)) <= 1e-9 * Math.max(1, len(b)); });
}
// probes: a ring of 360 directions in the plane z = 0 (half a degree off the whole degrees, two lengths), and 8 numbers on the x-axis
const LEARN_PROBE_FLAT = Array.from({ length: 360 }, (x, k) => { const a = (k + 0.5) * PI / 180, r = k % 2 ? 1.2 : 0.8; return [r * Math.cos(a), r * Math.sin(a), 0]; });
const LEARN_PROBE_LINE = [-1.7, -1.1, -0.6, -0.2, 0.3, 0.8, 1.2, 1.9].map(x => [x, 0, 0]);
const LEARN_PROBE_DIRS = [[0.36, 0.48, 0.8], [-0.6, 0.64, 0.48], [0.28, -0.96, 0.0], [-0.48, -0.36, -0.8], [0.8, 0.0, -0.6], [0.0, 0.6, 0.8], [-0.936, 0.288, 0.2]];

function learnPlan(o = {}) {
  const space = o.space === 1 || o.space === 2 ? o.space : 3;
  const A = APPROACHES.find(a => a.id === o.id) || (MATH[o.id] ? { id: o.id, name: o.id, params: [] } : APPROACHES[0]);
  const id = A.id, q = Object.assign(specDefaults(A.params || []), o.params || {});
  const n = isFinite(+o.n) && o.n !== null && o.n !== '' ? +o.n : 2;
  const c0 = o.c || [0, 0, 0], c = [+c0[0] || 0, space > 1 ? +c0[1] || 0 : 0, space > 2 ? +c0[2] || 0 : 0];
  const abs = o.abs || [0, 0, 0], flip = o.flip || [0, 0];
  const mirror = learnMirror(space, abs, flip);
  const F = v => MATH[id](v, n, q);
  const moves = mirror ? [mirror] : [];
  let note, power;

  if (space < 3) {
    power = v => learnFlatRule(v, n);
    moves.push(learnTurnZ(n, space, 'lean'), learnStretch(n, power));
    // does the chosen approach, as its dials stand, give this same answer on the x-axis (line) or in the plane z = 0 (page)?
    const same = learnAgree(F, power, space === 1 ? LEARN_PROBE_LINE : LEARN_PROBE_FLAT), where = space === 1 ? 'on the x-axis' : 'in the plane z = 0';
    note = (space === 1
      ? 'On a line a number can lean only two ways from the positive side: 0° or 180°. The turn is the same turn as on a page, so a negative number has to swing through a direction the line does not have.'
      : 'On a page the point is turned and then stretched. That is ordinary multiplication of complex numbers.')
      + ` With a whole power and the dials at their starting values, every approach in the list does this ${where}. The one exception is “Mandelbulb, classic”, which does not keep the flat picture.`
      + (id === 'classic' ? (same ? ' As the power and its dials are set now, it happens to.' : '') : same ? '' : ` As the power and its dials are set now, “${A.name}” does not follow it ${where} either.`);
    if (space === 1 && !aprWhole(n)) note += ' With a power that is not a whole number a negative number does not come back to the line.';
  } else {
    power = F;
    const zero = F;                    // asked only for a point at the origin: where the rule itself sends it
    if (id === 'mercator' || id === 'fold') {
      if (id === 'fold') moves.push(learnFold(Math.max(2, q.planes || 2)));
      moves.push(learnTurnZ(n, 3, 'longitude'), learnLeanMerc(n));
      const turn = id === 'mercator' ? aprRad(q.turn) : 0;
      if (turn) moves.push(learnTurnDial(turn, 'Turn', 'Add the turn'));
      if (+q.lift) moves.push(learnLift(+q.lift));
      moves.push(learnStretch(n, zero));
      note = (id === 'fold' ? 'The fold is not a turn of space: each point turns about the x-axis by its own amount, and points on two sides of a crease go opposite ways. After it the rule is the one-plane rule. ' : '')
        + 'The longitude is multiplied the way the lean is on a page. The latitude is multiplied on the scale a Mercator map uses, so a point comes closer to a pole but never passes over it.';
    } else if (id === 'lathe') {
      const spin = q.spin === undefined ? 1 : +q.spin || 1, odd = learnIs(Math.abs(spin) % 2, 1);
      // an odd spin gives the same answer before or after the turn; any other spin is true only before it (MATH.lathe)
      if (spin !== 1 && !odd) moves.push(learnSpin(spin));
      moves.push(learnLathe(n, 0, false));
      if (spin !== 1 && odd) moves.push(learnSpin(spin));
      moves.push(learnStretch(n, zero));
      note = 'The hinge is a different line for every point: the line square to the sheet that holds the x-axis and the point. It is the z-axis exactly when the point lies in the flat plane. A point on the negative x-axis has no side to lean to, and the lab swings it through the y direction.'
        + (spin !== 1 && !odd ? ' The Spin multiplier is not an odd number, so the spin is shown first: only in that order do the moves end where the lab’s rule ends.' : '');
    } else if (id === 'tilt') {
      const tau = aprRad(q.tilt);
      moves.push(learnLathe(n, tau, true), learnBack(n, tau), learnStretch(n, zero));
      note = 'The Lathe move, measured from an axis tilted inside the flat plane, and then a turn back about the z-axis. For a point in the flat plane the two turns add up to the plain turn of a page, at every tilt.';
    } else if (id === 'bulb' || id === 'classic') {
      const classic = id === 'classic', ph = aprRad(classic ? q.theta : q.lat), lon = aprRad(classic ? q.phi : q.lon);
      moves.push(learnTurnZ(n, 3, 'longitude'), learnLeanBulb(n, ph, classic, classic ? 'θ phase' : 'Latitude phase'));
      if (lon) moves.push(learnTurnDial(lon, classic ? 'φ phase' : 'Longitude phase', 'Add the phase'));
      moves.push(learnStretch(n, zero));
      note = (classic ? 'The angle that is multiplied is measured from the z-axis. A point in the flat plane is 90° from that axis, so the lean throws it out of the plane: this is the one approach that does not keep the flat picture.'
        : 'Two angles are multiplied: the longitude, by a turn about the z-axis, and the latitude, by a lean along the point’s own meridian. The lean may carry the point over a pole.')
        + (ph ? ` The ${classic ? 'θ phase' : 'Latitude phase'} is shown inside the Lean move: once a point has passed over a pole it no longer shows which way its angle was growing, so the phase cannot be a move of its own.` : '');
    } else if (id === 'split') {
      const m = Math.abs(n);
      moves.push(learnTurnZ(m, 3, 'flat'), learnStretchFlat(m), learnHeight(m));
      if (n < 0) moves.push(learnInvert());
      note = 'The flat part (x, y) is turned and stretched as on a page, and the height is treated as a number on a line, on its own.'
        + (n < 0 ? ` A negative power is worked as the power ${aprNum(m)}, followed by one move that turns space inside out. In that move y goes straight through 0 to its mirror value, so a point on the y-axis passes through the origin.` : '');
    } else {
      // no simpler moves are written out: the direction, then the length. That split is true only when the rule's
      // length does not depend on the direction; otherwise both go in one move.
      const lens = [0.7, 1.3].map(r => LEARN_PROBE_DIRS.map(d => len(F(scl(norm(d), r)))));
      const even = lens.every(l => Math.max(...l) - Math.min(...l) <= 1e-9 * Math.max(...l));
      if (even) moves.push(learnOwn(F, false), learnStretchTo(F));
      else moves.push(learnOwn(F, true));
      note = `No simpler moves are written out for “${A.name}”. The point goes the short way round the sphere to the direction the rule sends it to` + (even ? ', and then its length goes to the rule’s length.' : ', and its length changes on the way: with these dials the rule’s length depends on the direction, so the two cannot be shown apart.');
    }
  }
  moves.push(learnShift(c, space));
  const pre = v => (mirror ? mirror.at(v, 1) : v);
  const plan = { moves, note, space, id, n, params: q, c, rule: v => add(power(pre(v)), c) };
  plan.run = v => learnRun(plan, v);
  plan.check = v => learnCheck(plan, v);
  return plan;
}
function learnRun(plan, v) {
  const out = [[+v[0] || 0, +v[1] || 0, +v[2] || 0]];
  for (const m of plan.moves) out.push(m.at(out[out.length - 1], 1));
  return out;
}
function learnCheck(plan, v) {
  const run = learnRun(plan, v);
  return len(sub(run[run.length - 1], plan.rule(run[0])));
}
