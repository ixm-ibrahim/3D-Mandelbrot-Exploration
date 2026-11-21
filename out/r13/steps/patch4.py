def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 ("      if (q.lift) moves.push(learnLift(+q.lift));", "      if (+q.lift) moves.push(learnLift(+q.lift));"),
])
sub('out/r13/steps/test.js', [
 ("jumpFail: 0, jumpWorst: 0,", "jumpFail: 0, jumpOrigin: 0, jumpRatio: 0, jumpOther: 0, geomN: 0, geomFail: 0, keyFail: 0, jumpWorst: 0,"),
 ("    const ctx = { q: plan.params, n: o.n, c: plan.c };",
  """    const ctx = { q: plan.params, n: o.n, c: plan.c };
    const KEYS = ['mirror', 'fold', 'turn', 'lean', 'spin', 'back', 'phase', 'own', 'stretch', 'shift'];
    for (const m of plan.moves) if (!KEYS.includes(m.key) || typeof m.name !== 'string' || !m.name || typeof m.say !== 'function' || typeof m.at !== 'function' || typeof m.hinge !== 'function' || typeof m.sheet !== 'function' || typeof m.hidden !== 'boolean') row.keyFail++;
    if (typeof plan.note !== 'string' || plan.note.length < 20 || plan.moves[plan.moves.length - 1].key !== 'shift') row.keyFail++;
    const big = (p, q2) => { const lo = Math.min(Math.abs(p), Math.abs(q2)), hi = Math.max(Math.abs(p), Math.abs(q2)); return hi > 0 && !(lo * 4.0e8 > hi); };"""),
 ("            row.jumpFail++;\n", """            row.jumpFail++;
            const kind = len(a) === 0 ? 'jumpOrigin' : big(len(a), len(b)) || big(a[2], b[2]) || big(hyp(a[0], a[1]), hyp(b[0], b[1])) ? 'jumpRatio' : 'jumpOther';
            row[kind]++;
            if (kind === 'jumpOther') note('JUMP-OTHER ' + m.key, `step ${big.toPrecision(3)} of path ${path.toPrecision(3)} at a=${a.map(x => +x.toPrecision(4))} b=${b.map(x => +x.toPrecision(4))}`);
"""),
 ("          let p = a, path = 0, big = 0, bad = false;", """          const hg = m.hinge(a), sh = m.sheet(a), mid = m.at(a, 0.37), dv = sub(mid, a), tolg = 1e-9 * (1 + len(a));
          if (hg || sh) {
            row.geomN++;
            let ok = true;
            if (hg && !(Math.abs(len(hg) - 1) < 1e-9 && Math.abs(dot(dv, hg)) <= tolg)) ok = false;
            if (sh) {
              const nx = [sh[0][1] * sh[1][2] - sh[0][2] * sh[1][1], sh[0][2] * sh[1][0] - sh[0][0] * sh[1][2], sh[0][0] * sh[1][1] - sh[0][1] * sh[1][0]];
              if (!(Math.abs(len(sh[0]) - 1) < 1e-9 && Math.abs(len(sh[1]) - 1) < 1e-9 && Math.abs(len(nx) - 1) < 1e-6 && Math.abs(dot(dv, nx)) <= tolg)) ok = false;
              if (hg && !(Math.abs(Math.abs(dot(hg, nx)) - 1) < 1e-6)) ok = false;
            }
            if (!ok) { row.geomFail++; note('geom ' + m.key, `a=${a.map(x => +x.toPrecision(4))} hinge=${hg && hg.map(x => +x.toPrecision(4))} sheet=${sh && JSON.stringify(sh.map(u => u.map(x => +x.toPrecision(4))))}`); }
          }
          let p = a, path = 0, big = 0, bad = false;"""),
 ("  window.__LT = { space3, flat, samples };", """  // more powers and dial values, the truth check and the sentences only
  function extra() {
    const rows = [], pts = points(3);
    for (const a of AP) for (const n of [1, 0, 0.5, 8, -0.5, -3.7, 4]) {
      const q = Object.assign({}, L.S.param[a.id]);
      rows.push(runConfig({ space: 3, id: a.id, params: q, n, c: C }, v => add(MATH[a.id](v, n, q), C), pts, `extra ${a.id} n=${n}`));
    }
    for (const spin of [2, 0.5, -4, 0]) for (const n of [2, 3, -1, 2.5]) {
      const q = { spin };
      rows.push(runConfig({ space: 3, id: 'lathe', params: q, n, c: C }, v => add(MATH.lathe(v, n, q), C), pts, `extra lathe n=${n} spin=${spin}`));
    }
    for (const [id, q] of [['mercator', { turn: 360, lift: -6 }], ['mercator', { turn: 0, lift: 20 }], ['fold', { planes: 16, lift: 6 }], ['fold', { planes: 2, lift: 0.3 }], ['tilt', { tilt: 90 }], ['tilt', { tilt: 180 }], ['bulb', { lat: 180, lon: 180 }], ['classic', { theta: 180, phi: 90 }],
      ['softfold', { planes: 2, blend: 0, curve: 0, mix: 0 }], ['softfold', { planes: 3, blend: 0.45, curve: 1, mix: 2 }], ['axisbulb', { k: 2, wob: 1, reach: 0, pinch: 0 }], ['axisbulb', { k: 9, wob: 0, reach: 45, pinch: 4 }]]) for (const n of [2, 3, -2, 2.5]) {
      const qq = Object.assign({}, L.S.param[id], q);
      rows.push(runConfig({ space: 3, id, params: qq, n, c: C }, v => add(MATH[id](v, n, qq), C), pts, `extra ${id} n=${n} ${JSON.stringify(q)}`));
    }
    return rows;
  }
  window.__LT = { space3, flat, samples, extra };"""),
])
sub('out/r13/steps/run_tests.py', [
 ("        elif w.startswith('flat'):", "        elif w == 'extra':\n            acts.append({'js': \"return '@@R' + JSON.stringify(window.__LT.extra())\"})\n        elif w.startswith('flat'):"),
 ("what = sys.argv[1:] or IDS + ['flat1', 'flat2', 'samples']", "what = sys.argv[1:] or IDS + ['flat1', 'flat2', 'extra', 'samples']"),
 ("tot = dict(cfg=0, pts=0, checkFail=0, at0Fail=0, jumpMoves=0, jumpFail=0, sayN=0, sayFail=0)", "tot = dict(cfg=0, pts=0, checkFail=0, at0Fail=0, jumpMoves=0, jumpFail=0, jumpOrigin=0, jumpRatio=0, jumpOther=0, geomN=0, geomFail=0, keyFail=0, sayN=0, sayFail=0)"),
 ("        for k in ('checkFail', 'at0Fail', 'jumpMoves', 'jumpFail', 'sayN', 'sayFail'):", "        for k in ('checkFail', 'at0Fail', 'jumpMoves', 'jumpFail', 'jumpOrigin', 'jumpRatio', 'jumpOther', 'geomN', 'geomFail', 'keyFail', 'sayN', 'sayFail'):"),
 ("r['jumpMoves'], r['jumpFail'], 100 * r['jumpWorst'], r['sayN'], r['sayFail']) + (", "r['jumpMoves'], r['jumpFail'], 100 * r['jumpWorst'], r['sayN'], r['sayFail']) + ('  jump: origin %d, ratio %d, other %d | geom %d fail %d | key %d' % (r['jumpOrigin'], r['jumpRatio'], r['jumpOther'], r['geomN'], r['geomFail'], r['keyFail'])) + ("),
])
