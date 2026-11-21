// Round 13, truth checker: classify the truth failures of space 3 (needs t1.js loaded first; run.py loads one file, so t1 is pasted in by run2.py)
(() => {
  const SL = window.squaringLab, MATH = SL.MATH, learnPlan = SL.learnPlan, CK = window.__CK;
  const len = v => Math.hypot(v[0], v[1], v[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const negz = v => v.some(x => Object.is(x, -0));
  const show = v => v.map(x => (Object.is(x, -0) ? '-0' : String(x)));
  const POW = [2, 3, 5, -1, -2, 2.5, 4, 8, 1, 0.5, -0.5, 7, -3];
  CK.failList = (id, N = 2000) => {
    const PTS = CK.points3(N, 9173), C3 = [0.31, -0.27, 0.19];
    const T = { id, fails: 0, inputNegZero: 0, origin: 0, afterMirrorNegZero: 0, ordinary: 0, tinyRel: 0, ex: { inputNegZero: [], origin: [], afterMirrorNegZero: [], ordinary: [] }, byPower: {} };
    for (const n of POW) for (const q of CK.DIALS[id]) for (let mi = 0; mi < CK.MODS.length; mi++) for (const c of (mi === 0 ? [C3, [0, 0, 0]] : [C3])) {
      const M = CK.MODS[mi], Q = Object.assign(CK.defaults(id), q);
      const plan = learnPlan({ space: 3, id, params: Q, n, c, abs: M.abs, flip: M.flip });
      for (const v of PTS) {
        let p = v.slice(); for (const m of plan.moves) p = m.at(p, 1);
        const u = CK.modv(v, M, 3), ref = add(MATH[id](u, n, Q), c), e = len(sub(p, ref)), size = len(ref), rel = e / (size > 0 ? size : 1);
        if (rel <= 1e-9) continue;
        T.fails++;
        const kind = !(len(v) > 0) ? 'origin' : negz(v) ? 'inputNegZero' : negz(u) ? 'afterMirrorNegZero' : 'ordinary';
        T[kind]++;
        if (rel < 1e-6) T.tinyRel++;
        T.byPower[n] = (T.byPower[n] || 0) + 1;
        if (T.ex[kind].length < 4) T.ex[kind].push({ n, q, mod: mi, c0: c[0] === 0, v: show(v), afterMirror: show(u), got: p, ref, rel });
      }
    }
    return T;
  };
  // the same question for what a user of the tab can reach: ordinary points (+0 zeros) on the axes and planes, every modifier combination
  CK.reach = () => {
    const out = [], C3 = [0.31, -0.27, 0.19];
    const pts = [];
    for (const L of [0.5, 1.2]) for (let i = 0; i < 3; i++) for (const s of [1, -1]) { const v = [0, 0, 0]; v[i] = s * L; pts.push(v); }
    for (const a of [0.4, 1.9, 3.5, 5.1]) { pts.push([Math.cos(a), Math.sin(a), 0], [Math.cos(a), 0, Math.sin(a)], [0, Math.cos(a), Math.sin(a)]); }
    pts.push([0, 0, 0]);
    const mods = [];
    for (let m = 0; m < 32; m++) mods.push({ abs: [m & 1, (m >> 1) & 1, (m >> 2) & 1], flip: [(m >> 3) & 1, (m >> 4) & 1] });
    for (const id of CK.IDS) {
      const row = { id, runs: 0, fails: 0, ex: [] };
      for (const n of [2, 3, 5, -1, -2, 2.5, 0.5, 1.5, -1.5, 4]) for (const q of CK.DIALS[id]) for (const M of mods) {
        const Q = Object.assign(CK.defaults(id), q), plan = learnPlan({ space: 3, id, params: Q, n, c: C3, abs: M.abs, flip: M.flip });
        for (const v of pts) {
          let p = v.slice(); for (const m of plan.moves) p = m.at(p, 1);
          const u = CK.modv(v, M, 3), ref = add(MATH[id](u, n, Q), C3), e = len(sub(p, ref)), size = len(ref), rel = e / (size > 0 ? size : 1);
          row.runs++;
          if (!(rel <= 1e-9)) { row.fails++; if (row.ex.length < 5 && (len(v) > 0 || row.ex.length < 1)) row.ex.push({ n, q, abs: M.abs, flip: M.flip, v: show(v), afterMirror: show(u), got: p, ref, rel }); }
        }
      }
      out.push(row);
    }
    return out;
  };
})();
