  // (Round 29.) The same orbit, kept: for "A whole shape, Move by move" (67-learn-shape.js), whose dots are shown
  // where they are now. Line for line the arithmetic of out() above, which is left as it was.
  // -> { out, pts, c, carry }
  //   out     what out() answers
  //   pts[j]  where the dot is after j steps, for j = 0 .. min(out, maxK): when the dot is thrown out, the last
  //           place is the one that lies outside the big ball. Empty when the picture's point itself lies outside.
  //   c       the number that is added at every step (what the approach's own cmap makes of the picture's c)
  //   carry   for an entry whose orbit carries something (CARRY): carry[j] is what it carries when step j + 1
  //           begins; null for every other entry
  function orbit(p, kind, c, maxK) {
    const a = ap(), id = a.id, q = S.param[id] || {}, n = S.n, jul = kind === 'j', ab = S.abs, fl = S.flip;
    const K = maxK === undefined ? 16 : maxK, res = { out: 0, pts: [], c: [0, 0, 0], carry: null };
    if (!(Math.hypot(p[0], p[1], p[2]) <= BALL)) return res;
    let z = [0, 0, 0], cc;
    if (jul) { z = zmapJs(id, p, c, q); cc = cmapJs(id, c, q, true); } else cc = cmapJs(id, p, q, false);
    res.c = [cc[0], cc[1], cc[2]];
    const car = typeof CARRY !== 'undefined' && CARRY[id] ? CARRY[id] : null;
    let st = car ? car.start(q) : null;
    res.pts.push([z[0], z[1], z[2]]);
    if (car) res.carry = [st];
    if (jul && !(Math.hypot(z[0], z[1], z[2]) <= BALL)) return res;
    for (let k = 1; k <= K; k++) {
      const v = [ab[0] ? Math.abs(z[0]) : z[0], (ab[1] ? Math.abs(z[1]) : z[1]) * (fl[0] ? -1 : 1), (ab[2] ? Math.abs(z[2]) : z[2]) * (fl[1] ? -1 : 1)];
      let w;
      if (car) { st = car.step(st, v, cc, q); w = car.pw(st, v, n); } else w = MATH[id](v, n, q, cc);
      z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
      res.pts.push(z);
      if (car) res.carry.push(st);
      if (!(Math.hypot(z[0], z[1], z[2]) <= BALL)) { res.out = k; return res; }
    }
    res.out = K + 1;
    return res;
  }
