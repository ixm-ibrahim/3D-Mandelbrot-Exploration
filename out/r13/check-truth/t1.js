// Round 13, truth checker. Independent of out/r13/steps/test.js: own points, own reference, own parser.
(() => {
  const SL = window.squaringLab, MATH = SL.MATH, APS = SL.APPROACHES, learnPlan = SL.learnPlan;
  const PI = Math.PI, DG = 180 / PI;
  const len = v => Math.hypot(v[0], v[1], v[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const scl = (a, s) => [a[0] * s, a[1] * s, a[2] * s], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const ang = (a, b) => Math.atan2(len(cross(a, b)), dot(a, b));
  const wrap = d => { let w = d - 360 * Math.round(d / 360); return w; };
  function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  const defaults = id => { const A = APS.find(a => a.id === id), o = {}; (A.params || []).forEach(s => { if (s.key !== undefined) o[s.key] = s.def; }); return o; };
  const DIALS = {
    mercator: [{}, { turn: 73, lift: 0.4 }, { turn: -120, lift: -0.7 }, { turn: 180 }, { lift: 1.3 }],
    fold: [{}, { planes: 3 }, { planes: 5, lift: 0.3 }, { planes: 8, lift: -0.5 }],
    lathe: [{}, { spin: 3 }, { spin: -3 }, { spin: 5 }, { spin: -1 }],
    tilt: [{}, { tilt: 0 }, { tilt: -75 }, { tilt: 180 }, { tilt: 123 }],
    bulb: [{}, { lat: 30, lon: -45 }, { lat: -100, lon: 170 }, { lat: 90 }],
    classic: [{}, { theta: 25, phi: 60 }, { theta: -140, phi: -10 }],
    split: [{}],
    softfold: [{}, { planes: 3, blend: 0.1, curve: 1, mix: 1 }, { planes: 4, blend: 0.4, mix: 2 }, { planes: 2, blend: 0 }],
    axisbulb: [{}, { k: 3 }, { k: -2, wob: 0.5, reach: 20, pinch: 1.5 }, { k: 2, wob: 0 }, { k: 1, wob: 0, reach: 0, pinch: 0.5 }],
    pillow: [{}, { layout: 1 }],
  };
  const MODS = [{ abs: [0, 0, 0], flip: [0, 0] }, { abs: [1, 0, 1], flip: [1, 0] }, { abs: [0, 1, 0], flip: [0, 1] }, { abs: [1, 1, 1], flip: [1, 1] }];
  const modv = (v, M, space) => v.map((x, i) => { if (i >= space) return x; let y = M.abs[i] ? Math.abs(x) : x; if (i === 1 && M.flip[0]) y = -y; if (i === 2 && M.flip[1]) y = -y; return y; });
  const POW_REQ = [2, 3, 5, -1, -2, 2.5], POW_ALL = [2, 3, 5, -1, -2, 2.5, 4, 8, 1, 0.5, -0.5, 7, -3];
  const C3 = [0.31, -0.27, 0.19];

  function points3(N, seed) {
    const r = rng(seed), S = [[0, 0, 0]];
    for (const L of [1e-25, 1e-21, 1e-19, 1e-12, 0.003, 0.5, 1, 1.7, 30, 1e5]) for (let i = 0; i < 3; i++) for (const s of [1, -1]) { const v = [0, 0, 0]; v[i] = s * L; S.push(v); }
    for (const e of [1e-9, 1e-13, 1e-17]) for (let i = 0; i < 3; i++) for (const s of [1, -1]) for (let j = 0; j < 3; j++) if (j !== i) { const v = [0, 0, 0]; v[i] = s * 0.9; v[j] = e; S.push(v); const w = [0, 0, 0]; w[i] = s * 0.9; w[j] = -e; S.push(w); }
    S.push([-1, -0, 0], [-1, 0, -0], [-1, -0, -0], [1, -0, -0], [0, -0, 1], [-0, 0, -1], [-0, -1, 0], [0, 1, -0]);
    for (const d of [1e-3, 1e-4, 1e-6, 1e-7, 1e-8]) for (const s of [1, -1]) { S.push([d * 0.6, d * 0.8, s]); S.push([-d, 0, s * 1.3]); }
    for (const k of [2, 3, 4, 5, 8]) for (let j = 0; j < 2 * k; j++) { const a = j * PI / k, b = (j + 0.5) * PI / k; S.push([0.3, 0.8 * Math.cos(a), 0.8 * Math.sin(a)]); S.push([0.3, 0.8 * Math.cos(b), 0.8 * Math.sin(b)]); S.push([-0.4, 0.8 * Math.cos(b + 1e-9), 0.8 * Math.sin(b + 1e-9)]); }
    for (let i = 0; i < 120; i++) { const a = r() * 2 * PI, L = 0.1 + 2 * r(); S.push([L * Math.cos(a), L * Math.sin(a), 0]); S.push([L * Math.cos(a), 0, L * Math.sin(a)]); S.push([0, L * Math.cos(a), L * Math.sin(a)]); }
    while (S.length < N) { const v = [2 * r() - 1, 2 * r() - 1, 2 * r() - 1], l = len(v); if (l > 1 || l < 1e-6) continue; S.push(scl(v, 2.4 * Math.cbrt(r()) / l)); }
    return S;
  }
  function points2(N, seed) {
    const r = rng(seed), S = [[0, 0, 0]];
    for (const L of [1e-25, 1e-12, 0.003, 0.5, 1, 1.7, 30]) for (let i = 0; i < 2; i++) for (const s of [1, -1]) { const v = [0, 0, 0]; v[i] = s * L; S.push(v); }
    for (const e of [1e-9, 1e-13, 1e-17]) for (const s of [1, -1]) { S.push([s * 0.9, e, 0], [s * 0.9, -e, 0], [e, s * 0.9, 0], [-e, s * 0.9, 0]); }
    S.push([-1, -0, 0], [1, -0, 0]);
    while (S.length < N) { const a = r() * 2 * PI, L = 2.4 * Math.sqrt(r()); S.push([L * Math.cos(a), L * Math.sin(a), 0]); }
    return S;
  }
  function points1(N, seed) {
    const r = rng(seed), S = [[0, 0, 0]];
    for (const L of [1e-25, 1e-12, 0.003, 0.5, 1, 1.7, 30]) for (const s of [1, -1]) S.push([s * L, 0, 0]);
    S.push([-1, -0, 0], [-0.7, -0, -0]);
    while (S.length < N) S.push([(2 * r() - 1) * 2.5, 0, 0]);
    return S;
  }
  // independent complex power (repeated multiplication for whole n; polar otherwise). cap as the lab: e^42
  function cpow(x, y, n) {
    if (Number.isInteger(n)) {
      let ar = 1, ai = 0; const m = Math.abs(n);
      for (let i = 0; i < m; i++) [ar, ai] = [ar * x - ai * y, ar * y + ai * x];
      if (n < 0) { const d = ar * ar + ai * ai; return [ar / d, -ai / d]; }
      return [ar, ai];
    }
    const r = Math.hypot(x, y), th = Math.atan2(y, x), R = Math.pow(r, n);
    return [R * Math.cos(n * th), R * Math.sin(n * th)];
  }
  const runTo = (plan, v) => { let p = v.slice(); for (const m of plan.moves) p = m.at(p, 1); return p; };

  // ---- 1. truth in space
  function truth3(id, N = 2000) {
    const PTS = points3(N, 9173), rows = [];
    let cfg = 0, runs = 0, fails = 0, worst = 0, firstFail = null, nonfinite = 0;
    for (const n of POW_ALL) for (const q of DIALS[id]) for (let mi = 0; mi < MODS.length; mi++) for (const c of (mi === 0 ? [C3, [0, 0, 0]] : [C3])) {
      const M = MODS[mi], Q = Object.assign(defaults(id), q);
      const plan = learnPlan({ space: 3, id, params: Q, n, c, abs: M.abs, flip: M.flip });
      cfg++;
      for (const v of PTS) {
        const p = runTo(plan, v), ref = add(MATH[id](modv(v, M, 3), n, Q), c), e = len(sub(p, ref)), size = len(ref);
        const rel = e / (size > 0 ? size : 1);
        runs++;
        if (!isFinite(e)) nonfinite++;
        if (!(rel <= 1e-9)) { fails++; if (!firstFail) firstFail = { n, q, mod: mi, c, v, got: p, ref, rel }; }
        if (rel > worst) worst = rel;
      }
    }
    return { id, cfg, runs, fails, worst, nonfinite, firstFail };
  }
  // an independent spot check that does not use MATH: Lathe n = 2 is the quaternion square; bulb n = 2 by its angles
  function spot() {
    const PTS = points3(1500, 44), out = {};
    let w = 0;
    const pl = learnPlan({ space: 3, id: 'lathe', params: { spin: 1 }, n: 2, c: [0, 0, 0] });
    for (const v of PTS) { const [x, y, z] = v, ref = [x * x - y * y - z * z, 2 * x * y, 2 * x * z], p = runTo(pl, v), s = len(ref); if (s > 1e-30 && s < 1e30) w = Math.max(w, len(sub(p, ref)) / s); }
    out.latheVsQuaternionSquare = w;
    w = 0;
    const pm = learnPlan({ space: 3, id: 'mercator', params: { turn: 0, lift: 0 }, n: 2, c: [0, 0, 0] });
    for (const v of PTS) { const r = len(v); if (!(r > 1e-6 && r < 100)) continue; const d = scl(v, 1 / r); if (Math.abs(d[2]) > 0.9999) continue; const q = 1 + d[2] * d[2], ref = scl([(d[0] * d[0] - d[1] * d[1]) / q, 2 * d[0] * d[1] / q, 2 * d[2] / q], r * r), p = runTo(pm, v); w = Math.max(w, len(sub(p, ref)) / len(ref)); }
    out.mercatorVsClosedFormSquare = w;
    return out;
  }
  // ---- spaces 1 and 2 against x^n and the complex power; and what the note says about the chosen approach
  function flat(space, N = 2000) {
    const PTS = space === 1 ? points1(N, 77) : points2(N, 78), out = [];
    const c = space === 1 ? [-0.37, 0, 0] : [-0.37, 0.21, 0];
    let cfg = 0, runs = 0, fails = 0, worst = 0, firstFail = null, skipped = 0, noteWrong = [];
    for (const A of APS) for (const n of POW_ALL) for (let mi = 0; mi < 3; mi++) {
      const id = A.id, M = MODS[mi], Q = defaults(id);
      const plan = learnPlan({ space, id, params: Q, n, c, abs: M.abs, flip: M.flip });
      cfg++;
      for (const v of PTS) {
        const u = modv(v, M, space), r = Math.hypot(u[0], u[1]);
        if (r < 1e-6 && (n < 0 || r > 0)) { skipped++; continue; }   // the plain power has no value / the lab caps
        if (r > 20 && Math.abs(n) > 5) { skipped++; continue; }
        const w = cpow(u[0], u[1], n), ref = [w[0] + c[0], w[1] + c[1], 0], p = runTo(plan, v), e = len(sub(p, ref)), size = Math.max(len(ref), Math.hypot(w[0], w[1]));
        const rel = e / (size > 0 ? size : 1);
        runs++;
        if (!(rel <= 1e-9)) { fails++; if (!firstFail) firstFail = { id, n, mod: mi, v, got: p, ref, rel }; }
        if (rel > worst) worst = rel;
      }
    }
    // the note: "does not follow it either" / "happens to" against my own count on many points
    const probe = PTS.filter(v => { const r = len(v); return r > 0.05 && r < 3; });
    const noteRows = [];
    for (const A of APS) for (const q of DIALS[A.id]) for (const n of POW_ALL) {
      const id = A.id, Q = Object.assign(defaults(id), q), plan = learnPlan({ space, id, params: Q, n, c: [0, 0, 0] });
      let bad = 0;
      for (const v of probe) { const w = cpow(v[0], v[1], n), a = MATH[id](v, n, Q); if (len(sub(a, [w[0], w[1], 0])) > 1e-7 * Math.max(1, Math.hypot(w[0], w[1]))) bad++; }
      const says = /does not follow it/.test(plan.note) ? 'not' : id === 'classic' ? (/happens to/.test(plan.note) ? 'same' : 'not') : 'same';
      const truthIs = bad === 0 ? 'same' : 'not';
      if (says !== truthIs) noteWrong.push({ id, q, n, bad, of: probe.length, note: plan.note });
      const whole = Number.isInteger(n), def = Object.keys(q).length === 0;
      if (whole && def && id !== 'classic' && bad) noteRows.push({ claim: 'every approach agrees at whole powers and starting dials', id, n, bad, of: probe.length });
    }
    return { space, cfg, runs, fails, worst, skipped, firstFail, noteWrong: noteWrong.slice(0, 12), noteWrongCount: noteWrong.length, claimBroken: noteRows };
  }

  // ---- 2 and 4. along each move: at(v,0) = v, no jump, the end is reached smoothly, hinge and sheet
  function moves3(id, space = 3, NP = 110, powers = POW_REQ) {
    const base = space === 3 ? points3(700, 31) : space === 2 ? points2(200, 32) : points1(120, 33);
    const rr = rng(5), extra = [];
    if (space === 3) for (let i = 0; i < 40; i++) { const v = [2 * rr() - 1, 2 * rr() - 1, 2 * rr() - 1]; extra.push(scl(v, 1.6 * rr() / (len(v) || 1) + 0)); }
    const PTS = (space === 3 ? base.slice(0, 200).filter((v, i) => i % 3 === 0).concat(base.slice(200, 520).filter((v, i) => i % 9 === 0), base.slice(653, 653 + 30), extra) : base).slice(0, NP + 60);
    const T = { id, space, cfg: 0, paths: 0, at0Fail: 0, jumpFail: 0, jumpOrigin: 0, jumpRatio: 0, jumpOther: [], endFail: [], startFail: [], hingeN: 0, hingeAxisFail: 0, hingeDistFail: 0, hingeDistBy: {}, sheetN: 0, sheetFail: 0, squareFail: 0, unitFail: 0, hingeEx: [], sheetEx: [], worstStep: 0, nonfinite: 0 };
    const dials = space === 3 ? DIALS[id] : [{}];
    for (const n of powers) for (const q of dials) for (const mi of [0, 3]) {
      const M = MODS[mi], Q = Object.assign(defaults(id), q), c = space === 1 ? [0.31, 0, 0] : space === 2 ? [0.31, -0.27, 0] : C3;
      const plan = learnPlan({ space, id, params: Q, n, c, abs: M.abs, flip: M.flip });
      T.cfg++;
      for (const v of PTS) {
        let a = v.slice();
        for (const m of plan.moves) {
          T.paths++;
          const p0 = m.at(a, 0);
          if (!(Object.is(p0[0] + 0, a[0] + 0) && p0[1] + 0 === a[1] + 0 && p0[2] + 0 === a[2] + 0)) T.at0Fail++;
          let prev = a, total = 0, mx = 0, at = 0, bad = false;
          for (let i = 1; i <= 400; i++) { const p = m.at(a, i / 400), d = len(sub(p, prev)); if (!isFinite(d)) bad = true; total += d; if (d > mx) { mx = d; at = i; } prev = p; }
          const b = prev, la = len(a), lb = len(b);
          if (bad) T.nonfinite++;
          if (total > 0 && mx > 0.05 * total + 1e-9 * Math.max(la, lb)) {
            T.jumpFail++;
            const ratio = la > 0 && lb > 0 ? Math.abs(Math.log(lb / la)) : Infinity;
            // Split: the flat part or the height can change by a huge factor on its own
            const r2 = Math.max(...[[Math.hypot(a[0], a[1]), Math.hypot(b[0], b[1])], [Math.abs(a[2]), Math.abs(b[2])]].map(([x, y]) => (x > 0 && y > 0 ? Math.abs(Math.log(y / x)) : 0)));
            if (!(la > 0)) T.jumpOrigin++;
            else if (ratio > 15 || r2 > 15) T.jumpRatio++;
            else if (T.jumpOther.length < 8) T.jumpOther.push({ n, q, mod: mi, move: m.name, a, b, share: mx / total, atStep: at });
            else T.jumpOther.push(1);
          }
          if (total > 0) T.worstStep = Math.max(T.worstStep, mx / total);
          // the two ends are reached, not jumped to
          const pe = m.at(a, 1 - 1e-7), ps = m.at(a, 1e-7);
          const lr = la > 0 && lb > 0 ? Math.abs(Math.log(lb / la)) : 100;
          if (len(sub(pe, b)) > 1e-5 * (1 + lr) * total + 1e-12 * Math.max(la, lb) && T.endFail.length < 6 && la > 0) T.endFail.push({ n, q, mod: mi, move: m.name, a, b, gap: len(sub(pe, b)), total });
          if (len(sub(ps, a)) > 1e-5 * (1 + lr) * total + 1e-12 * Math.max(la, lb) && T.startFail.length < 6 && la > 0) T.startFail.push({ n, q, mod: mi, move: m.name, a, b, gap: len(sub(ps, a)), total });
          // hinge and sheet
          const h = m.hinge(a), sh = m.sheet(a), tol = 1e-9 * Math.max(la, lb, 1e-300);
          if (h) {
            T.hingeN++;
            if (Math.abs(len(h) - 1) > 1e-9) T.unitFail++;
            const ax0 = dot(a, h), d0 = len(sub(a, scl(h, ax0)));
            let axBad = false, dBad = false;
            for (const t of [0.13, 0.37, 0.5, 0.81, 1]) { const p = m.at(a, t), ax = dot(p, h), d = len(sub(p, scl(h, ax))); if (Math.abs(ax - ax0) > tol) axBad = true; if (Math.abs(d - d0) > tol) dBad = true; }
            if (axBad) T.hingeAxisFail++;
            if (dBad) { T.hingeDistFail++; const k = m.key + ':' + m.name; T.hingeDistBy[k] = (T.hingeDistBy[k] || 0) + 1; if (T.hingeEx.length < 4) T.hingeEx.push({ n, q, move: m.name, key: m.key, a, b, d0, dEnd: len(sub(b, scl(h, dot(b, h)))) }); }
          }
          if (sh) {
            T.sheetN++;
            const [u, w] = sh;
            if (Math.abs(len(u) - 1) > 1e-9 || Math.abs(len(w) - 1) > 1e-9) T.unitFail++;
            const nm = cross(u, w), ln = len(nm);
            if (h && (Math.abs(dot(h, u)) > 1e-9 || Math.abs(dot(h, w)) > 1e-9)) T.squareFail++;
            let sBad = false;
            if (ln > 1e-9) for (const t of [0.13, 0.37, 0.5, 0.81, 1]) { const p = m.at(a, t); if (Math.abs(dot(sub(p, a), nm)) / ln > tol) sBad = true; }
            if (sBad) { T.sheetFail++; if (T.sheetEx.length < 4) T.sheetEx.push({ n, q, move: m.name, a, b }); }
          }
          a = b;
        }
      }
    }
    T.jumpOtherCount = T.jumpOther.length; T.jumpOther = T.jumpOther.filter(x => x !== 1);
    return T;
  }

  // ---- 3. the words
  const NUM = '(−?\\d+\\.\\d+(?: × 10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)?)', DEG = '(−?\\d+)°';
  const R = (src) => new RegExp(src.replace(/NUM/g, NUM).replace(/DEG/g, DEG));
  function pnum(s) { const m = s.match(/^(−?)(\d+\.\d+)(?: × 10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))?$/); let x = +m[2], sci = false; if (m[3]) { sci = true; x *= 10 ** +[...m[3]].map(ch => (ch === '⁻' ? '-' : '⁰¹²³⁴⁵⁶⁷⁸⁹'.indexOf(ch))).join(''); } return { x: m[1] ? -x : x, sci }; }
  const numOK = (s, actual) => { const p = pnum(s); return p.sci ? Math.abs(p.x - actual) <= 0.051 * Math.abs(actual) : Math.abs(p.x - actual) <= 0.00501 || (Math.abs(actual) >= 1e6); };
  const pdeg = s => +s.replace('−', '-');
  const degOK = (s, actual) => Math.abs(pdeg(s) - actual) <= 0.5001;
  const degModOK = (s, actual) => Math.abs(wrap(pdeg(s) - actual)) <= 0.5001;
  const lonD = v => Math.atan2(v[1], v[0]) * DG, latD = v => Math.atan2(v[2], Math.hypot(v[0], v[1])) * DG, colD = v => Math.atan2(Math.hypot(v[0], v[1]), v[2]) * DG;
  const xangD = v => Math.atan2(v[2], v[1]) * DG, merc = v => Math.asinh(v[2] / Math.hypot(v[0], v[1]));
  const is = (a, b) => Math.abs(a - b) < 1e-9;
  function coords(s) { return s.replace(/[()]/g, '').split(', '); }

  function checkSay(I, m, a, b, s) {
    const P = [], bad = t => P.push(t), { space, id, n, Q } = I, pw = id === 'split' && space === 3 ? Math.abs(n) : n;
    if (typeof s !== 'string' || s.trim().length < 12) { bad('empty'); return P; }
    if (/NaN|undefined|null|Infinity|\[object|function|=>/.test(s)) bad('bad token');
    if (!/[.!]$/.test(s.trim())) bad('no full stop');
    if (/—/.test(s)) bad('em dash');
    const two = /Squaring|squared|doubles|doubled/.test(s), three = /Cubing|cubed|triples|tripled/.test(s);
    const isDialMove = m.key === 'spin' || m.key === 'phase' || m.key === 'back' || m.key === 'mirror' || m.key === 'fold';
    if (two && (!is(pw, 2) || isDialMove)) bad('says squared/doubles but the power is ' + pw);
    if (three && (!is(pw, 3) || isDialMove)) bad('says cubed/triples but the power is ' + pw);
    const la = len(a), lb = len(b), rhoA = Math.hypot(a[0], a[1]), rhoB = Math.hypot(b[0], b[1]);
    let parsed = false, mm;
    const turnZ = m.key === 'turn' && (space < 3 || ['mercator', 'fold', 'bulb', 'classic', 'split'].includes(id));
    if (turnZ && space === 1) {
      parsed = true;
      const neg = /A negative number leans 180°/.test(s), pos = /A positive number leans 0°/.test(s), zero = /The point is 0\./.test(s);
      if (neg && !(a[0] < 0)) bad('says negative, x is ' + a[0]);
      if (pos && !(a[0] > 0)) bad('says positive, x is ' + a[0]);
      if (zero && a[0] !== 0) bad('says 0');
      if (!neg && !pos && !zero) parsed = false;
      if (pos && len(sub(a, b)) > 1e-9 * la) bad('positive number moved in the turn');
      if (neg) {
        if ((mm = s.match(R('(?:to|stays) DEG')))) { if (!is(Math.abs(pdeg(mm[1])), Math.abs(n * 180))) bad('lean after: ' + mm[1] + ' expected ±' + n * 180); if (pdeg(mm[1]) * n < 0) bad('sign of the lean after: says ' + mm[1] + '° with power ' + n); }
        const off = Math.abs(b[1]) > 1e-9 * lb;
        if (/lands on the positive side/.test(s) && !(b[0] > 0 && !off)) bad('does not land on the positive side');
        if (/lands on the negative side again/.test(s) && !(b[0] < 0 && !off)) bad('does not land on the negative side');
        if (/ends off the line/.test(s) && !off) bad('says off the line, is on it');
        if (!/ends off the line/.test(s) && off) bad('is off the line, sentence does not say');
        if (/a full turn/.test(s) && !(Math.abs(wrap(n * 180)) < 1e-6)) bad('full turn claimed');
        if (Math.abs(len(b) - la) > 1e-9 * la) bad('turn changed the length');
      }
    } else if (turnZ) {
      const th = lonD(a);
      if ((mm = s.match(R('leans DEG from the positive x-axis|around the z-axis, is DEG\\.')))) { parsed = true; const A = mm[1] || mm[2]; if (!degOK(A, th)) bad('lean before ' + A + ' vs ' + th.toFixed(2)); }
      if ((mm = s.match(R('(?:, to| it to) DEG')))) { if (!degOK(mm[1], pw * th)) bad('lean after ' + mm[1] + ' vs ' + (pw * th).toFixed(2)); if (rhoB > 1e-9 * lb && !degModOK(mm[1], lonD(b))) bad('point does not end at the stated lean ' + mm[1] + ' vs ' + lonD(b).toFixed(2)); }
      if ((mm = s.match(R('turns by DEG about the z-axis')))) { if (!degOK(mm[1], Math.abs((pw - 1) * th))) bad('turn amount ' + mm[1]); }
      if ((mm = s.match(R('same direction as DEG')))) { if (!degModOK(mm[1], pw * th) || Math.abs(pdeg(mm[1])) > 180) bad('same direction as ' + mm[1]); }
      if (/there is nothing to turn|leaves it where it is|does not turn/.test(s)) { parsed = true; if (len(sub(a, b)) > 1e-9 * la) bad('says no turn but the point moved'); }
      if (Math.abs(lb - la) > 1e-9 * la) bad('turn changed the length');
    } else if (m.key === 'turn' && (id === 'lathe' || id === 'tilt')) {
      const tau = id === 'tilt' ? (Q.tilt || 0) / DG : 0, e = [Math.cos(tau), -Math.sin(tau), 0], al = la > 0 ? ang(a, e) * DG : 0, end = lb > 0 ? ang(b, e) * DG : 0;
      if ((mm = s.match(R('leans DEG')))) { parsed = true; if (!degOK(mm[1], al)) bad('lean ' + mm[1] + ' vs ' + al.toFixed(2)); }
      if ((mm = s.match(R('dial is at DEG\\)')))) { if (!degOK(mm[1], Q.tilt)) bad('tilt ' + mm[1]); }
      const to = s.match(R('(?:, to| it to) DEG')), ends = s.match(R('ends DEG from'));
      if (to && !degOK(to[1], n * al)) bad('lean after ' + to[1] + ' vs ' + (n * al).toFixed(2));
      if (ends && !degOK(ends[1], end)) bad('ends ' + ends[1] + ' vs ' + end.toFixed(2));
      if (to && !ends && !/lands on/.test(s) && !degOK(to[1], end)) bad('point does not end at the stated lean ' + to[1] + ' vs ' + end.toFixed(2));
      if (/lands on/.test(s) && end > 0.6) bad('does not land on the axis');
      if (/does not turn|lean stays|It has no direction/.test(s)) { parsed = true; if (len(sub(a, b)) > 1e-9 * la) bad('says no turn but moved'); }
      if (/on the far side of the origin/.test(s)) parsed = true;
      if (Math.abs(lb - la) > 1e-9 * la) bad('turn changed the length');
    } else if (m.key === 'stretch' && m.name === 'Stretch' && !(id === 'split' && space === 3)) {
      if ((mm = s.match(R('(?:Its length|Then the length goes from|length), NUM, is .*?: NUM\\.')))) { parsed = true; if (!numOK(mm[1], la)) bad('length before ' + mm[1] + ' vs ' + la); if (!numOK(mm[2], lb)) bad('length after ' + mm[2] + ' vs ' + lb); }
      if ((mm = s.match(R('length goes from NUM to the rule’s length, NUM\\.')))) { parsed = true; if (!numOK(mm[1], la)) bad('length before'); if (!numOK(mm[2], lb)) bad('length after'); }
      if ((mm = s.match(R('Its length is NUM\\. The power is 1, so it stays NUM\\.')))) { parsed = true; if (!numOK(mm[1], la) || !numOK(mm[2], lb)) bad('length'); }
      if (/gets shorter/.test(s) && !(lb < la)) bad('says shorter');
      if (/gets longer/.test(s) && !(lb > la)) bad('says longer');
      if (/stays 1\./.test(s) && Math.abs(lb - 1) > 1e-6) bad('says stays 1');
      if (/short into long/.test(s) && !((la < 1 && lb > 1) || (la > 1 && lb < 1) || is(la, 1))) bad('short into long');
      if (/origin|It stays|sends the origin outward/.test(s)) parsed = true;
      if (la > 0 && lb > 0 && len(sub(scl(a, 1 / la), scl(b, 1 / lb))) > 1e-7) bad('stretch changed the direction');
      // is the length really the power? (untried entries only; my own power, capped like the lab)
      if (!['softfold', 'axisbulb', 'pillow'].includes(id) && la > 1e-20) { const want = Math.exp(Math.min(pw * Math.log(la), 42)); if (Math.abs(lb - want) > 1e-9 * want) bad('length is not r^n: ' + lb + ' vs ' + want); }
    } else if (m.key === 'stretch' && id === 'split') {
      if ((mm = s.match(R('flat part, NUM, is .*?: NUM\\.')))) { parsed = true; if (!numOK(mm[1], rhoA)) bad('flat before'); if (!numOK(mm[2], rhoB)) bad('flat after'); }
      if (/flat part is NUM|flat part of the point is 0|The power is 1/.test(s.replace(/NUM/, ''))) parsed = true;
      if (!/The height is not touched\.$/.test(s) || b[2] !== a[2]) bad('height touched');
    } else if (m.key === 'shift') {
      if ((mm = s.match(/from (\(.*?\)|[−\d.]+(?: × 10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)?) to (\(.*?\)|[−\d.]+(?: × 10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)?)\.$/))) {
        parsed = true; const ca = coords(mm[1]), cb = coords(mm[2]);
        if (ca.length !== space || cb.length !== space) bad('number of coordinates');
        ca.forEach((t, i) => { if (!numOK(t, a[i])) bad('from coordinate ' + t + ' vs ' + a[i]); }); cb.forEach((t, i) => { if (!numOK(t, b[i])) bad('to coordinate ' + t + ' vs ' + b[i]); });
      }
      if (/still off the line|nothing is added/.test(s)) parsed = true;
      if (len(sub(sub(b, a), I.c)) > 1e-9 * Math.max(1, lb)) bad('shift is not c');
    } else if (m.key === 'lean' && (id === 'mercator' || id === 'fold')) {
      if ((mm = s.match(R('latitude is DEG, which is NUM on the scale')))) { parsed = true; if (!degOK(mm[1], latD(a))) bad('latitude before'); if (!numOK(mm[2], merc(a))) bad('mercator before ' + mm[2] + ' vs ' + merc(a)); }
      if ((mm = s.match(R(' to NUM, which is latitude DEG\\.')))) { if (!numOK(mm[1], merc(b))) bad('mercator after ' + mm[1] + ' vs ' + merc(b)); if (!degOK(mm[2], latD(b))) bad('latitude after'); const Z = a[2] / la; if (Math.abs(Z) < 0.99999 && Math.abs(n * merc(a)) < 19 && Math.abs(merc(b) - n * merc(a)) > 1e-6 * (1 + Math.abs(merc(b)))) bad('mercator number is not multiplied by n'); }
      if (/It does not lean|stays at the pole|It has no direction|so it stays there/.test(s)) { parsed = true; if (len(sub(a, b)) > 2e-3 * la) bad('says stays but moved'); }
      if (Math.abs(lb - la) > 1e-9 * la) bad('lean changed the length');
      if (rhoA > 1e-9 * la && rhoB > 1e-9 * lb && Math.abs(wrap(lonD(a) - lonD(b))) > 1e-6) bad('lean changed the longitude');
    } else if (m.key === 'lean') {
      const cl = id === 'classic', a0 = cl ? colD(a) : latD(a), end = cl ? colD(b) : latD(b), ph = cl ? Q.theta : Q.lat;
      if ((mm = s.match(R(cl ? 'angle from the z-axis is DEG\\.' : 'latitude is DEG\\.')))) { parsed = true; if (!degOK(mm[1], a0)) bad('angle before ' + mm[1] + ' vs ' + a0.toFixed(2)); }
      const to = s.match(R('(?:, to| it to) DEG\\.')), adds = s.match(R('adds DEG: DEG\\.')), past = s.match(R(cl ? 'ends DEG from the z-axis' : 'at latitude DEG\\.'));
      if (to && !degOK(to[1], n * a0)) bad('angle after ' + to[1] + ' vs ' + (n * a0).toFixed(2));
      if (adds) { if (!degOK(adds[1], ph)) bad('phase ' + adds[1]); if (!degOK(adds[2], n * a0 + ph)) bad('angle with phase ' + adds[2] + ' vs ' + (n * a0 + ph).toFixed(2)); }
      if (!!ph !== !!adds && la > 0) bad('phase sentence missing or extra');
      if (past && !degOK(past[1], end)) bad('end angle ' + past[1] + ' vs ' + end.toFixed(2));
      const last = adds ? adds[2] : to ? to[1] : null;
      if (last && !past && lb > 0 && !degOK(last, end)) bad('point does not end at the stated angle ' + last + ' vs ' + end.toFixed(2));
      if (/It has no direction|flat plane|stays/.test(s)) parsed = true;
      if (/leaves the flat plane/.test(s) && !(Math.abs(b[2]) > 1e-9 * lb)) bad('says leaves the plane');
      if (Math.abs(lb - la) > 1e-9 * la) bad('lean changed the length');
    } else if (m.key === 'back') {
      const want = -(n - 1) * Q.tilt;
      if ((mm = s.match(R('turns back about the z-axis by DEG')))) { parsed = true; if (!degOK(mm[1], Math.abs(want))) bad('turn back amount'); }
      if ((mm = s.match(R('longitude goes from DEG to DEG\\.')))) { if (!degOK(mm[1], lonD(a)) || !degOK(mm[2], lonD(b))) bad('longitudes'); }
      if (/nothing to turn back/.test(s)) parsed = true;
      if (rhoA > 1e-9 * la && Math.abs(wrap(lonD(b) - lonD(a) - want)) > 1e-6) bad('turn back is not -(n-1) tilt');
      if (Math.abs(b[2] - a[2]) > 1e-12 * la) bad('turn back moved z');
    } else if (m.key === 'spin') {
      if ((mm = s.match(R('round the x-axis, DEG, is multiplied by it and becomes DEG')))) { parsed = true; if (!degOK(mm[1], xangD(a))) bad('spin before'); if (!degOK(mm[2], Q.spin * xangD(a))) bad('spin after'); if (!degModOK(mm[2], xangD(b))) bad('point does not end at the stated spin angle ' + mm[2] + ' vs ' + xangD(b).toFixed(2)); }
      if (/has no angle round the axis/.test(s)) parsed = true;
      if (Math.abs(b[0] - a[0]) > 1e-12 * la) bad('spin moved x');
    } else if (m.key === 'fold') {
      if ((mm = s.match(R('sits at DEG, and the fold of (\\d+) planes carries it to DEG\\.')))) { parsed = true; if (!degOK(mm[1], xangD(a))) bad('fold before'); if (!degModOK(mm[3], xangD(b))) bad('fold after ' + mm[3] + ' vs ' + xangD(b)); if (+mm[2] !== Math.max(2, Q.planes || 2)) bad('planes'); }
      if ((mm = s.match(R('at DEG around the x-axis it is already')))) { parsed = true; if (!degModOK(mm[1], xangD(a))) bad('fold angle'); if (len(sub(a, b)) > 1e-9 * la) bad('says left alone'); }
      if (/on the crease|so it stays/.test(s)) parsed = true;
    } else if (m.key === 'phase' && m.name === 'Lift') {
      if ((mm = s.match(R('adds NUM on the Mercator scale: the latitude goes from DEG to DEG\\.')))) { parsed = true; if (!numOK(mm[1], Q.lift)) bad('lift'); if (!degOK(mm[2], latD(a)) || !degOK(mm[3], latD(b))) bad('lift latitudes'); if (rhoA > 1e-6 * la && Math.abs(merc(a)) < 15 && Math.abs(merc(b) - merc(a) - Q.lift) > 1e-6) bad('lift is not added on the Mercator scale'); }
      if (/It has no direction/.test(s)) parsed = true;
    } else if (m.key === 'phase') {
      const dial = id === 'mercator' ? Q.turn : id === 'bulb' ? Q.lon : Q.phi;
      if ((mm = s.match(R('adds DEG to the longitude: it goes from DEG to DEG\\.')))) { parsed = true; if (!degOK(mm[1], dial)) bad('dial'); if (!degOK(mm[2], lonD(a)) || !degOK(mm[3], lonD(b))) bad('longitudes'); if (Math.abs(wrap(lonD(b) - lonD(a) - dial)) > 1e-6) bad('longitude not added'); }
      if (/It has no direction|so it stays/.test(s)) parsed = true;
    } else if (m.key === 'own' && m.name === 'Height') {
      if ((mm = s.match(R('The height, NUM, is .*?: NUM\\.')))) { parsed = true; if (!numOK(mm[1], a[2])) bad('height before ' + mm[1] + ' vs ' + a[2]); if (!numOK(mm[2], b[2])) bad('height after ' + mm[2] + ' vs ' + b[2]); }
      if (/passes through 0/.test(s) && !(a[2] < 0)) bad('passes through 0');
      if (/The height is 0|The power is 1/.test(s)) parsed = true;
      if (b[0] !== a[0] || b[1] !== a[1]) bad('height moved the flat part');
    } else if (m.key === 'own' && m.name === 'Inside out') {
      if ((mm = s.match(R('length goes from NUM to NUM, which is 1 divided by it, and y goes to its mirror value, from NUM to NUM\\.')))) { parsed = true; if (!numOK(mm[1], la) || !numOK(mm[2], lb)) bad('lengths'); if (!numOK(mm[3], a[1]) || !numOK(mm[4], b[1])) bad('y values'); if (Math.abs(lb * la - 1) > 1e-9) bad('not 1 divided by'); }
      if (/as far out as the lab counts/.test(s)) parsed = true;
    } else if (m.key === 'own') {
      if ((mm = s.match(R('sends this direction DEG round the sphere')))) { parsed = true; if (!degOK(mm[1], ang(a, b) * DG)) bad('own angle ' + mm[1] + ' vs ' + (ang(a, b) * DG).toFixed(2)); }
      if ((mm = s.match(R('Its length goes from NUM to NUM on the way')))) { if (!numOK(mm[1], la) || !numOK(mm[2], lb)) bad('own lengths'); } else if (la > 0 && lb > 0 && Math.abs(lb - la) > 1e-9 * la) bad('own turn changed the length without saying');
      if (/keeps this direction|exact opposite|origin/.test(s)) parsed = true;
    } else if (m.key === 'mirror') {
      parsed = true;
      const re = new RegExp('([xyz]) goes from ' + NUM + ' to ' + NUM, 'g'); let g;
      while ((g = re.exec(s))) { const i = 'xyz'.indexOf(g[1]); if (!numOK(g[2], a[i]) || !numOK(g[3], b[i])) bad('mirror numbers'); }
      const want = modv(a, I.M, space); if (len(sub(want, b)) > 0) bad('mirror end');
    }
    if (!parsed) P.push('UNPARSED');
    return P;
  }
  function words(id, space = 3, NP = 320, powers = POW_REQ.concat([1, 4, -3])) {
    const base = space === 3 ? points3(900, 61) : space === 2 ? points2(NP, 62) : points1(NP, 63);
    const PTS = space === 3 ? base.filter((v, i) => i < 653 ? i % 4 === 0 : true).slice(0, NP) : base;
    const T = { id, space, sentences: 0, problems: 0, byKind: {}, examples: [], unparsed: {}, sayNoB: 0, round2: { n: 0, off: 0 }, roundLen: { n: 0, off: 0 } };
    const dials = space === 3 ? DIALS[id] : [{}];
    for (const n of powers) for (const q of dials) for (const mi of [0, 3]) {
      const M = MODS[mi], Q = Object.assign(defaults(id), q), c = space === 1 ? [0.31, 0, 0] : space === 2 ? [0.31, -0.27, 0] : C3;
      const plan = learnPlan({ space, id, params: Q, n, c, abs: M.abs, flip: M.flip }), I = { space, id, n, Q, c: plan.c, M };
      for (const v of PTS) {
        let a = v.slice();
        for (const m of plan.moves) {
          const b = m.at(a, 1), s = m.say(a, b), s2 = m.say(a);
          T.sentences++;
          if (s2 !== s) T.sayNoB++;
          const P = checkSay(I, m, a, b, s);
          for (const p of P) {
            if (p === 'UNPARSED') { const k = m.key + ':' + s.replace(/−?\d+(\.\d+)?/g, '#').slice(0, 150); T.unparsed[k] = (T.unparsed[k] || 0) + 1; continue; }
            T.problems++;
            const kind = m.key + ':' + m.name + ': ' + p.replace(/−?\d+(\.\d+)?(e-?\d+)?/g, '#');
            T.byKind[kind] = (T.byKind[kind] || 0) + 1;
            if (T.examples.length < 14 && T.byKind[kind] <= 2) T.examples.push({ n, q, mod: mi, move: m.name, a, b, s, p });
          }
          // rounding: do the printed numbers agree with the printed word?
          let mm;
          if (is(n, 2) && (mm = s.match(/leans (−?\d+)° .*doubles it to (−?\d+)°/))) { T.round2.n++; if (2 * pdeg(mm[1]) !== pdeg(mm[2])) T.round2.off++; }
          if (is(n, 2) && (mm = s.match(/Its length, (\d+\.\d+), is squared: (\d+\.\d+)\./))) { T.roundLen.n++; if ((+mm[1] * +mm[1]).toFixed(2) !== mm[2]) T.roundLen.off++; }
          a = b;
        }
      }
    }
    const un = Object.entries(T.unparsed).sort((x, y) => y[1] - x[1]);
    T.unparsedKinds = un.length; T.unparsed = un.slice(0, 25);
    return T;
  }
  window.__CK = { truth3, spot, flat, moves3, words, points3, DIALS, defaults, MODS, modv, cpow, IDS: APS.map(a => a.id) };
})();
