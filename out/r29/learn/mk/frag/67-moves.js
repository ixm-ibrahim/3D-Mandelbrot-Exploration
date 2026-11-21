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
