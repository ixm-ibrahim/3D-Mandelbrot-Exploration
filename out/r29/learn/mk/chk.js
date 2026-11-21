// Injected into the page by dotcheck.py. window.__chk(cfg) sets the lab up and measures the dots of Move by move.
// cfg = { space, kind, c, dots, n, abs: [x, y, z], flip: [y, z], ap, gpu }
// What is measured (the largest value over every dot and every step up to 16):
//   joint0    |where a step begins as played  -  the dot's kept place after k steps|            (must be 0)
//   jointEnd  |where a step ends as played    -  the dot's kept place after k + 1 steps|        (must be 0)
//   oneStep   |kept place after k + 1 steps   -  the lab's own rule (learnPlan's rule) applied once to the kept place after k|
//   iterated  |kept place after k steps       -  the rule applied k times to the start, worked out HERE, independently|
//             2D: by plain multiplication for the whole powers 2 to 8 and in polar form otherwise, the modifiers first;
//             3D: by MATH[id] / CARRY[id], the modifiers first, from the first kept place and with the c the dot adds
//   chain     |where the chain of moves itself ends  -  the kept place after k + 1 steps|   (the moves really are the rule)
// each as a share of max(1, the place's distance from the centre).
//   outTwin   dots whose step of being thrown out differs from LEARN.shape.out2 (2D) / learnShape3d.out (3D) at their starting place
//   outPic    dots for which it differs from the fine picture's own numbers at their starting place:
//             2D learnShapeMap (through numbersAt), 3D the picture's own program on the graphics card (through slice3)
//   thrownBad steps at which the dots the play throws out are not exactly the dots with that number
window.__chk = function (cfg) {
  const L = window.squaringLab, S = L.S, LE = L.learn, SH = LE.shape, N = 16;
  const len = v => Math.hypot(v[0], v[1], v[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const rel = (a, b) => { const d = len(sub(a, b)) / Math.max(1, len(b)); return d === d ? d : (a.every((x, i) => Object.is(x, b[i]) || x === b[i]) ? 0 : Infinity); };
  if (cfg.ap) { const i = L.APPROACHES.findIndex(a => a.id === cfg.ap); if (i < 0) return { error: 'no approach ' + cfg.ap }; S.approach = i; }
  S.n = cfg.n; S.abs = (cfg.abs || [0, 0, 0]).slice(); S.flip = (cfg.flip || [0, 0]).slice();
  SH.set({ on: true, each: 'moves', kind: cfg.kind, space: cfg.space, c: cfg.c, dots: cfg.dots, pos: 0 });
  const a = L.APPROACHES[S.approach], id = a.id, q = S.param[id] || {}, D = SH.dots(cfg.kind), three = cfg.space === 3;
  const car = three && L.CARRY && L.CARRY[id] ? L.CARRY[id] : null;
  const mod = z => [S.abs[0] ? Math.abs(z[0]) : z[0], (S.abs[1] ? Math.abs(z[1]) : z[1]) * (S.flip[0] ? -1 : 1), three ? (S.abs[2] ? Math.abs(z[2]) : z[2]) * (S.flip[1] ? -1 : 1) : z[2]];
  const out = { cfg, dots: D.n, names: null, joint0: 0, jointEnd: 0, oneStep: 0, iterated: 0, chain: 0, outTwin: 0, outPic: -1, thrownBad: 0, steps: 0, stay: 0, perStep: [] };
  // the lab's own rule for one step, from learnPlan (for an entry whose orbit carries something: made for each dot)
  const plan0 = car ? null : L.learnPlan({ space: three ? 3 : 2, id, params: q, n: S.n, c: [0, 0, 0], abs: S.abs.slice(), flip: S.flip.slice() });
  const ruleOf = (i, k) => {
    if (!car) return v => { const w = plan0.rule(v), c = D.c[i]; return [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; };
    return L.learnPlan({ space: 3, id, params: q, n: S.n, c: D.c[i].slice(), abs: S.abs.slice(), flip: S.flip.slice(), carry: D.carry[i][k] }).rule;
  };
  // the rule applied again and again from the start, worked out here
  const mul = Number.isInteger(S.n) && S.n >= 2 && S.n <= 8 ? S.n : 0;
  const pow2 = v => {
    const x = v[0], y = v[1];
    if (mul === 2) return [x * x - y * y, 2 * x * y, 0];
    if (mul) { let p = x, r = y; for (let m = 1; m < mul; m++) { const t = p * x - r * y; r = p * y + r * x; p = t; } return [p, r, 0]; }
    const r = Math.hypot(x, y);
    if (r < 1e-20 && S.n > 0) return [0, 0, 0];
    const R = Math.exp(Math.min(S.n * Math.log(Math.max(r, 1e-30)), 42)), an = Math.atan2(y, x) * S.n;
    return [R * Math.cos(an), R * Math.sin(an), 0];
  };
  for (let i = 0; i < D.n; i++) {
    const P = D.places[i], c = D.c[i];
    let z = P[0].slice(), st = car ? car.start(q) : null;
    for (let k = 1; k < P.length; k++) {
      const v = mod(z);
      let w;
      if (!three) w = pow2(v);
      else if (car) { st = car.step(st, v, c, q); w = car.pw(st, v, S.n); }
      else w = L.MATH[id](v, S.n, q, c);
      z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
      out.iterated = Math.max(out.iterated, rel(z, P[k]));
    }
    // the last kept place is the one outside (or the place after N steps)
    const o = D.out[i];
    if (P.length !== Math.min(o, N) + 1) out.error = 'dot ' + i + ' keeps ' + P.length + ' places, thrown out at ' + o;
    if (o > N) out.stay++;
    const twin = three ? L.learnShape3d.out(D.start[i], cfg.kind, cfg.c, N) : SH.out2(D.start[i], cfg.kind, cfg.c, N);
    if (twin !== o) out.outTwin++;
  }
  for (let k = 0; k < N; k++) {
    const ch = SH.chain(cfg.kind, k);
    out.names = ch.names;
    let thrown = 0;
    const want = []; for (let i = 0; i < D.n; i++) if (D.out[i] > k) want.push(i);
    if (want.length !== ch.on.length || want.some((i, n) => ch.on[n] !== i)) out.thrownBad++;
    ch.on.forEach((i, n) => {
      const J = ch.joints[n], P = D.places[i];
      out.joint0 = Math.max(out.joint0, rel(J[0], P[k]));
      out.jointEnd = Math.max(out.jointEnd, rel(J[J.length - 1], P[k + 1]));
      out.oneStep = Math.max(out.oneStep, rel(ruleOf(i, k)(P[k]), P[k + 1]));
      out.chain = Math.max(out.chain, rel(ch.end[n], P[k + 1]));
      out.steps++;
      if (D.out[i] === k + 1) thrown++;
    });
    if (thrown !== ch.thrown) out.thrownBad++;
    // as drawn: at the end of the throwing out, the dots still on show are exactly those with a higher number
    const drawn = SH.dotsAt(cfg.kind, k + 1 - 1e-7).dots.map(d => d.i), keep = want.filter(i => D.out[i] > k + 1);
    if (drawn.length !== keep.length || drawn.some((i, n) => keep[n] !== i)) out.thrownBad++;
    out.perStep.push([ch.on.length, ch.thrown]);
  }
  // the fine picture's own numbers at the dots' starting places
  if (!three) { const pic = SH.numbersAt(cfg.kind, D.start); out.outPic = 0; pic.forEach((v, i) => { if (v !== D.out[i]) out.outPic++; }); }
  else if (cfg.gpu) {
    const h = D.gap, m = Math.ceil(2 / h) + 1, size = 2 * m, zs = [...new Set(D.start.map(p => p[2]))];
    out.outPic = 0; out.picDots = [];
    for (const z of zs) {
      const sl = SH.slice3(cfg.kind, { z, half: m * h, size, centres: true, maxK: N });
      if (!sl) { out.outPic = -2; break; }
      D.start.forEach((p, i) => {
        if (p[2] !== z) return;
        const col = Math.round(p[0] / h - 0.5 + m), row = size - 1 - Math.round(p[1] / h - 0.5 + m);
        if (sl[row * size + col] !== D.out[i]) { out.outPic++; if (out.picDots.length < 6) out.picDots.push([i, D.out[i], sl[row * size + col]]); }
      });
    }
  }
  return out;
};
