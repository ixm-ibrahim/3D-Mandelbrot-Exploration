// Round 13, truth checker: the notes and "What to notice" against numbers
(() => {
  const SL = window.squaringLab, MATH = SL.MATH, learnPlan = SL.learnPlan, CK = window.__CK, PI = Math.PI, DG = 180 / PI;
  const len = v => Math.hypot(v[0], v[1], v[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  CK.notes = () => {
    const o = {};
    // a. Lathe: the hinge is the z-axis exactly when the point lies in the flat plane
    const pl = learnPlan({ space: 3, id: 'lathe', params: { spin: 1 }, n: 2, c: [0, 0, 0] }), turn = pl.moves[0], P = CK.points3(3000, 5);
    let flatN = 0, flatOnZ = 0, offN = 0, offOnZ = 0, minOff = 9, diffLines = 0;
    for (const v of P) {
      const r = len(v); if (!(r > 1e-6)) continue;
      const h = turn.hinge(v); if (!h) continue;
      const onZ = Math.hypot(h[0], h[1]) < 1e-12;
      if (v[2] === 0) { flatN++; if (onZ) flatOnZ++; } else { offN++; if (onZ) offOnZ++; if (Math.abs(v[2]) > 1e-3 * r && Math.abs(v[1]) + Math.abs(v[2]) > 1e-6 * r) minOff = Math.min(minOff, Math.hypot(h[0], h[1])); }
    }
    const hs = P.slice(700, 760).map(v => turn.hinge(v)); for (let i = 1; i < hs.length; i++) if (len(cross(hs[i], hs[0])) > 1e-6) diffLines++;
    o.latheHinge = { flatPoints: flatN, flatWithHingeOnZ: flatOnZ, otherPoints: offN, otherWithHingeOnZ: offOnZ, smallestTiltOfHingeFromZForPointsClearlyOffThePlane: minOff, of59OtherPointsHingeDiffersFromFirst: diffLines };
    // b. tilt note: "for a point in the flat plane the two turns add up to the plain turn of a page, at every tilt"
    o.tiltFlat = [];
    for (const n of [2, 3, -2, 2.5, 0.5]) for (const tilt of [40, -75, 123, 180]) {
      let bad = 0, N = 0, ex = null; const p = learnPlan({ space: 3, id: 'tilt', params: { tilt }, n, c: [0, 0, 0] });
      for (let k = 0; k < 720; k++) { const a = (k + 0.25) * PI / 360, v = [0.9 * Math.cos(a), 0.9 * Math.sin(a), 0]; let q = v; q = p.moves[0].at(q, 1); q = p.moves[1].at(q, 1); const w = CK.cpow(v[0], v[1], Number.isInteger(n) ? n : n), R = Math.hypot(w[0], w[1]), want = [0.9 * w[0] / R, 0.9 * w[1] / R, 0]; N++; if (len(sub(q, want)) > 1e-6) { bad++; if (!ex) ex = { leanDeg: a * DG, got: q, plainPageTurn: want }; } }
      o.tiltFlat.push({ n, tilt, bad, of: N, ex });
    }
    // c. classic note: "the lean throws it out of the plane", by power
    o.classicFlat = [];
    for (const n of [2, 3, 4, 5, -1, -3, 2.5, 9]) { const p = learnPlan({ space: 3, id: 'classic', params: { theta: 0, phi: 0 }, n, c: [0, 0, 0] }); let q = [0.6, 0.5, 0]; for (const m of p.moves) q = m.at(q, 1); o.classicFlat.push({ n, endZ: q[2], endsInPlane: Math.abs(q[2]) < 1e-9, note: n === 5 ? p.note : undefined, leanSays: p.moves[1].say(p.moves[0].at([0.6, 0.5, 0], 1)) }); }
    // d. mercator: a point at a pole under a negative power
    o.mercPole = [];
    for (const n of [2, -1, -2]) { const p = learnPlan({ space: 3, id: 'mercator', params: { turn: 0, lift: 0 }, n, c: [0, 0, 0] }), a = [0, 0, 1.2], b = p.moves[1].at(a, 1); o.mercPole.push({ n, from: a, to: b, lab: MATH.mercator(a, n, {}), says: p.moves[1].say(a, b) }); }
    // e. 1D with power 2.5: the second step starts off the line
    { const p = learnPlan({ space: 1, id: 'lathe', n: 2.5, c: [-0.6, 0, 0] }); let q = [-1.2, 0, 0]; for (const m of p.moves) q = m.at(q, 1); const leanDeg = Math.atan2(q[1], q[0]) * DG; o.line25 = { startOfStep2: q, itsRealLeanDeg: leanDeg, turnSays: p.moves[0].say(q), stretchSays: p.moves[1].say(p.moves[0].at(q, 1)) }; }
    // f. axisbulb: which settings give an "own" move that reports a hinge while the length changes
    o.ownHinge = [];
    for (const q of CK.DIALS.axisbulb) { const Q = Object.assign(CK.defaults('axisbulb'), q), p = learnPlan({ space: 3, id: 'axisbulb', params: Q, n: 2, c: [0, 0, 0] }), m = p.moves[0], a = [0.5, 0.4, 0.6], b = m.at(a, 1), h = m.hinge(a); const d = v => len(sub(v, h.map(x => x * (v[0] * h[0] + v[1] * h[1] + v[2] * h[2])))); o.ownHinge.push({ q, moves: p.moves.map(x => x.key + ':' + x.name), lenA: len(a), lenB: len(b), distFromHingeStart: d(a), mid: d(m.at(a, 0.5)), end: d(b), says: m.say(a, b) }); }
    // g. on a line with n = 2: which c keep the orbit of 0 bounded (the "plain stretch of the line from -2 to 1/4")
    { const p0 = c => { const p = learnPlan({ space: 1, id: 'lathe', n: 2, c: [c, 0, 0] }); let q = [0, 0, 0]; for (let i = 0; i < 400; i++) { for (const m of p.moves) q = m.at(q, 1); if (Math.abs(q[0]) > 8) return false; } return true; }; let lo = null, hi = null; for (let k = -3000; k <= 1000; k++) { const c = k / 1000; if (p0(c)) { if (lo === null) lo = c; hi = c; } } let holes = 0; for (let k = Math.round(lo * 1000); k <= Math.round(hi * 1000); k++) if (!p0(k / 1000)) holes++; o.line = { lowestBoundedC: lo, highestBoundedC: hi, holesBetween: holes }; }
    // negative numbers under n = 2 on a line, through the plan
    { const p = learnPlan({ space: 1, id: 'lathe', n: 2, c: [0, 0, 0] }); let neg = 0, pos = 0, maxHid = 0; for (let k = 1; k <= 2000; k++) { const x = -k / 800, a = [x, 0, 0], b = p.moves[0].at(a, 1), mid = p.moves[0].at(a, 0.5); neg++; if (b[0] > 0 && Math.abs(b[1]) < 1e-12) pos++; maxHid = Math.max(maxHid, Math.abs(Math.abs(mid[1]) - Math.abs(x))); } o.lineNeg = { negatives: neg, landOnPositiveSide: pos, midSwingIsFullyInHiddenDirectionWorstGap: maxHid, hiddenFlag: p.moves[0].hidden, othersHidden: p.moves.slice(1).map(m => m.hidden) }; }
    return o;
  };
})();
