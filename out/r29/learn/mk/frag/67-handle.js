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
