// Round 13, steps: the tests of docs/ROUND13.md, run inside the page (window.squaringLab.learnPlan).
// Defines window.__LT.space3(id) and window.__LT.flat(space); each returns rows of results.
(() => {
  const L = window.squaringLab, learnPlan = L.learnPlan, MATH = L.MATH, AP = L.APPROACHES;
  const PI = Math.PI, hyp = Math.hypot;
  const len = a => hyp(a[0], a[1], a[2]), sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const POWERS = [2, 3, 5, -1, -2, 2.5];
  const C = [-0.4, 0.3, 0.2];
  const SETTINGS = {
    mercator: [{}, { turn: 40 }, { turn: -110, lift: 0.7 }],
    fold: [{}, { planes: 3 }, { planes: 5, lift: -0.6 }],
    lathe: [{}, { spin: 3 }, { spin: -5 }],
    tilt: [{}, { tilt: 0 }, { tilt: -125 }],
    bulb: [{}, { lat: 30 }, { lat: -140, lon: 75 }],
    classic: [{}, { theta: -90 }, { theta: 60, phi: -130 }],
    split: [{}],
    softfold: [{}, { planes: 3, blend: 0.1, curve: 1, mix: 1 }, { planes: 4, blend: 0.3, curve: 0, mix: 2 }],
    axisbulb: [{}, { k: 5, wob: 0 }, { k: -3, wob: 0.4, reach: 30, pinch: 1.5 }],
    pillow: [{}, { layout: 1 }],
  };
  // 2,000 points: 1,800 anywhere in a ball of radius 2.2, 100 in the plane z = 0, 40 in the plane y = 0, 60 special
  function points(space) {
    const r = rng(12345), out = [];
    const ball = () => { for (;;) { const p = [2 * r() - 1, 2 * r() - 1, 2 * r() - 1]; if (len(p) <= 1 && len(p) > 0) return p.map(x => 2.2 * x); } };
    for (let i = 0; i < 1800; i++) out.push(ball());
    for (let i = 0; i < 100; i++) { const p = ball(); out.push([p[0], p[1], 0]); }
    for (let i = 0; i < 40; i++) { const p = ball(); out.push([p[0], 0, p[2]]); }
    const sp = [[0, 0, 0]];
    for (const s of [0.5, 1, 1.7]) for (let k = 0; k < 3; k++) for (const g of [1, -1]) { const p = [0, 0, 0]; p[k] = g * s; sp.push(p); }
    sp.push([1e-9, 0, 1], [0, 1e-9, -1], [-1, 1e-9, 0], [-1, 0, 1e-9], [1, 1e-12, 1e-12], [0.6, 0.6, 0], [-0.6, 0.6, 0], [0.5, 0, 0.5], [0, 0.5, 0.5], [0, -0.5, 0.5],
      [1e-12, 1e-12, 1e-12], [1e-25, 0, 0], [0, 0, 1e-25], [3, 0, 0], [0, 7, 0], [0.01, 0.01, 0.01], [-0.001, 0.002, 0.0005], [0.7071, 0, 0.7071], [0.7071, 0, -0.7071], [-0.7071, 0.7071, 0]);
    while (sp.length < 60) sp.push(ball().map(x => x * 0.05));
    out.push(...sp.slice(0, 60));
    if (space === 2) return out.map(p => [p[0], p[1], 0]);
    if (space === 1) return out.map(p => [p[0], 0, 0]);
    return out;
  }
  const SPECIAL0 = 1940;   // index of the first special point
  const mods = (v, abs, flip) => [abs[0] ? Math.abs(v[0]) : v[0], (abs[1] ? Math.abs(v[1]) : v[1]) * (flip[0] ? -1 : 1), (abs[2] ? Math.abs(v[2]) : v[2]) * (flip[1] ? -1 : 1)];

  // ---- the numbers inside a sentence, checked against quantities measured here from a and b
  const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹';
  const unsup = s => [...s].map(ch => (ch === '⁻' ? '-' : SUP.indexOf(ch))).join('');
  const fix2 = x => { const s = Math.abs(x).toFixed(2); return (x < 0 && +s !== 0 ? '−' : '') + s; };
  const short = x => String(+(+x).toFixed(2)).replace('-', '−');
  function sayCheck(s, a, b, ctx) {
    if (typeof s !== 'string' || s.length < 12) return 'not a sentence';
    if (/NaN|undefined|Infinity|null|\[object/.test(s)) return 'bad word';
    const deg = x => x * 180 / PI, wrap = d => { let w = d - 360 * Math.round(d / 360); return w <= -180 ? w + 360 : w; };
    const A = [], N = [];
    const tau = (ctx.q.tilt || 0) * PI / 180, ta = [Math.cos(tau), -Math.sin(tau), 0], n = ctx.n, m = Math.abs(n);
    const angs = v => {
      const rho = hyp(v[0], v[1]), x = dot(v, ta);
      return [deg(Math.atan2(v[1], v[0])), deg(Math.atan2(v[2], rho)), deg(Math.atan2(hyp(v[1], v[2]), v[0])), deg(Math.atan2(rho, v[2])), deg(Math.atan2(v[2], v[1])),
        deg(Math.atan2(len(sub(v, ta.map(c => c * x))), x))];
    };
    const dials = Object.values(ctx.q).map(Number).filter(isFinite);
    const aa = angs(a), ab = angs(b);
    for (const k of [n, m, ctx.q.spin || 1]) for (const x of aa) { A.push(k * x, (k - 1) * x, wrap(k * x)); for (const d of dials) A.push(k * x + d, wrap(k * x + d)); }
    A.push(...aa, ...ab, ...dials, 0, 180, 360, n * 180, wrap(n * 180), (n - 1) * (ctx.q.tilt || 0));
    A.push(deg(Math.atan2(len([a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]), dot(a, b))));
    const merc = v => { const rho = hyp(v[0], v[1]); return rho > 0 ? Math.asinh(v[2] / rho) : 0; };
    N.push(len(a), len(b), ...a, ...b, ...ctx.c, hyp(a[0], a[1]), hyp(b[0], b[1]), merc(a), merc(b), n, m, n - 1, ...dials, 0, 1, Math.max(2, ctx.q.planes || 2));
    const As = A.filter(isFinite).map(Math.abs), Ns = new Set();
    for (const x of N.filter(isFinite)) { Ns.add(fix2(x)); Ns.add(short(x)); Ns.add(fix2(Math.abs(x))); Ns.add(short(Math.abs(x))); }
    const text = s.replace(/\(n − 1\)/g, '').replace(/z = 0/g, '');
    const re = /(−?\d+(?:\.\d+)?)( × 10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))?(°?)/g;
    let mm;
    while ((mm = re.exec(text))) {
      if (mm[4]) { const tv = +mm[1].replace('−', ''); if (!As.some(x => Math.abs(x - tv) <= 0.5 + 1e-6)) return 'angle ' + mm[0] + ' not measured'; continue; }
      if (mm[2]) {
        const val = +mm[1].replace('−', '-') * 10 ** +unsup(mm[3]);
        if (!N.some(x => Math.abs(x - val) <= 0.06 * Math.abs(val))) return 'number ' + mm[0] + ' not measured';
        continue;
      }
      if (!Ns.has(mm[1])) return 'number ' + mm[0] + ' not measured';
    }
    return '';
  }

  // ---- one configuration: every test on its 2,000 points
  function runConfig(o, ref, pts, label) {
    const plan = learnPlan(o), row = { label, moves: plan.moves.map(m => m.key).join(' '), n: pts.length, relMax: 0, checkFail: 0, selfMax: 0, at0Fail: 0, jumpPts: 0, jumpMoves: 0, jumpFail: 0, jumpOrigin: 0, jumpRatio: 0, jumpOther: 0, geomN: 0, geomFail: 0, keyFail: 0, jumpWorst: 0, sayN: 0, sayFail: 0, notes: [] };
    const note = (k, t) => { if (row.notes.length < 6 && !row.notes.some(x => x.startsWith(k))) row.notes.push(k + ': ' + t); };
    const ctx = { q: plan.params, n: o.n, c: plan.c };
    const KEYS = ['mirror', 'fold', 'turn', 'lean', 'spin', 'back', 'phase', 'own', 'stretch', 'shift'];
    for (const m of plan.moves) if (!KEYS.includes(m.key) || typeof m.name !== 'string' || !m.name || typeof m.say !== 'function' || typeof m.at !== 'function' || typeof m.hinge !== 'function' || typeof m.sheet !== 'function' || typeof m.hidden !== 'boolean') row.keyFail++;
    if (typeof plan.note !== 'string' || plan.note.length < 20 || plan.moves[plan.moves.length - 1].key !== 'shift') row.keyFail++;
    const farApart = (p, q2) => { const lo = Math.min(Math.abs(p), Math.abs(q2)), hi = Math.max(Math.abs(p), Math.abs(q2)); return hi > 0 && !(lo * 4.0e8 > hi); };
    pts.forEach((v, i) => {
      const run = plan.run(v), end = run[run.length - 1], want = ref(v), base = sub(want, plan.c);
      const size = Math.max(len(want), len(base)), err = len(sub(end, want)), rel = size > 0 ? err / size : err > 0 ? Infinity : 0;
      if (!(rel <= 1e-9)) { row.checkFail++; note('check', `v=${v.map(x => +x.toPrecision(4))} got ${end.map(x => +x.toPrecision(6))} want ${want.map(x => +x.toPrecision(6))}`); }
      if (isFinite(rel)) row.relMax = Math.max(row.relMax, rel);
      const self = plan.check(v); row.selfMax = Math.max(row.selfMax, size > 0 ? self / size : self);
      const special = i >= SPECIAL0, doJump = i < 140 || special, doSay = i < 340 || special;
      if (doJump) row.jumpPts++;
      plan.moves.forEach((m, k) => {
        const a = run[k], b = run[k + 1], z = m.at(a, 0);
        if (!(z[0] === a[0] && z[1] === a[1] && z[2] === a[2])) { row.at0Fail++; note('at0', m.key); }
        if (doSay) {
          row.sayN++;
          let why;
          try { why = sayCheck(m.say(a, b), a, b, ctx); } catch (e) { why = 'threw ' + e.message; }
          if (why) { row.sayFail++; note('say ' + m.key, why + ' | ' + (() => { try { return m.say(a, b); } catch (e) { return ''; } })() + ' | a=' + a.map(x => +x.toPrecision(4))); }
        }
        if (doJump) {
          row.jumpMoves++;
          const hg = m.hinge(a), sh = m.sheet(a), mid = m.at(a, 0.37), dv = sub(mid, a), tolg = 1e-9 * (1 + len(a));
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
          let p = a, path = 0, big = 0, bad = false;
          for (let s = 1; s <= 400; s++) { const qv = m.at(a, s / 400), d = len(sub(qv, p)); if (!(d >= 0)) bad = true; path += d; if (d > big) big = d; p = qv; }
          const close = len(sub(p, b));
          const allow = 0.05 * path + 1e-9 * (1 + len(a) + len(b));
          if (bad || !(big <= allow) || !(close <= 1e-9 * (1 + len(b)))) {
            row.jumpFail++;
            const kind = len(a) === 0 ? 'jumpOrigin' : farApart(len(a), len(b)) || farApart(a[2], b[2]) || farApart(hyp(a[0], a[1]), hyp(b[0], b[1])) ? 'jumpRatio' : 'jumpOther';
            row[kind]++;
            if (kind === 'jumpOther') note('JUMP-OTHER ' + m.key, `step ${big.toPrecision(3)} of path ${path.toPrecision(3)} at a=${a.map(x => +x.toPrecision(4))} b=${b.map(x => +x.toPrecision(4))}`);
            note('jump ' + m.key, `step ${big.toPrecision(3)} of path ${path.toPrecision(3)} at a=${a.map(x => +x.toPrecision(4))} b=${b.map(x => +x.toPrecision(4))}`);
          }
          if (path > 1e-6 * (1 + len(a))) row.jumpWorst = Math.max(row.jumpWorst, big / path);
        }
      });
    });
    return row;
  }

  function space3(id) {
    const rows = [], pts = points(3), sets = SETTINGS[id] || [{}];
    for (const n of POWERS) {
      sets.forEach((params, si) => {
        const q = Object.assign({}, L.S.param[id], params);
        rows.push(runConfig({ space: 3, id, params: q, n, c: C, abs: [0, 0, 0], flip: [0, 0] }, v => add(MATH[id](v, n, q), C), pts, `${id} n=${n} dials#${si} ${JSON.stringify(params)}`));
      });
      for (const [abs, flip] of [[[1, 0, 1], [1, 0]], [[0, 1, 0], [0, 1]]]) {
        const q = Object.assign({}, L.S.param[id]);
        rows.push(runConfig({ space: 3, id, params: q, n, c: C, abs, flip }, v => add(MATH[id](mods(v, abs, flip), n, q), C), pts, `${id} n=${n} modifiers abs=${abs} flip=${flip}`));
      }
    }
    return rows;
  }
  // spaces 1 and 2, against a power worked out here: repeated multiplication for whole n, exp(n log z) otherwise
  function cpow(x, y, n) {
    if (Number.isInteger(n)) {
      let a = 1, b = 0;
      for (let i = 0; i < Math.abs(n); i++) [a, b] = [a * x - b * y, a * y + b * x];
      if (n < 0) { const d = a * a + b * b; a = a / d; b = -b / d; }
      return [a, b];
    }
    const r = hyp(x, y), t = Math.atan2(y, x), R = Math.pow(r, n);
    return [R * Math.cos(n * t), R * Math.sin(n * t)];
  }
  function flat(space) {
    const rows = [], pts = points(space).filter(p => len(p) > 1e-6 || len(p) === 0);
    for (const n of POWERS) {
      for (const [abs, flip] of [[[0, 0, 0], [0, 0]], [[1, 1, 0], [1, 0]]]) {
        for (const a of AP) {
          const ref = v => {
            const w = mods(v, [abs[0], space > 1 && abs[1], 0], [space > 1 && flip[0], 0]);
            if (len(w) === 0) return n > 0 ? [C[0], space > 1 ? C[1] : 0, 0] : [NaN, NaN, NaN];
            const p = space === 1 && Number.isInteger(n) ? [Math.pow(w[0], n), 0] : cpow(w[0], w[1], n);
            return [p[0] + C[0], p[1] + (space > 1 ? C[1] : 0), 0];
          };
          const usable = n > 0 ? pts : pts.filter(p => len(p) > 0);
          const row = runConfig({ space, id: a.id, params: L.S.param[a.id], n, c: C, abs, flip }, ref, usable, `space ${space} ${a.id} n=${n} abs=${abs} flip=${flip}`);
          if (space === 1) row.offLine = usable.filter(v => { const e = learnPlan({ space, id: a.id, n, c: C, abs, flip }).run(v).pop(); return Math.abs(e[1]) > 1e-9 * (1 + len(e)); }).length;
          rows.push(row);
        }
      }
    }
    return rows;
  }
  // sentences at the awkward points, for reading by eye
  function samples() {
    const out = [];
    const show = (o, v) => { const plan = learnPlan(o), run = plan.run(v); out.push(`--- space ${o.space} ${o.id} n=${o.n} ${JSON.stringify(o.params || {})} v=${v}`); plan.moves.forEach((m, k) => out.push(`  [${m.key}] ${m.name}: ${m.say(run[k], run[k + 1])}`)); out.push('  note: ' + plan.note); };
    for (const n of [2, 3, 2.5, -1]) { show({ space: 1, id: 'lathe', n, c: [-1, 0, 0] }, [-1.2, 0, 0]); show({ space: 1, id: 'lathe', n, c: [-1, 0, 0] }, [0.8, 0, 0]); }
    show({ space: 1, id: 'lathe', n: 2, c: [0.25, 0, 0] }, [0, 0, 0]);
    show({ space: 2, id: 'lathe', n: 2, c: [-0.4, 0.3, 0] }, [0.96, 0.72, 0]);
    show({ space: 2, id: 'classic', n: 3, c: [-0.4, 0.3, 0] }, [-0.5, 0.9, 0]);
    show({ space: 2, id: 'mercator', n: 2, c: [0, 0, 0], abs: [0, 1, 0] }, [0.3, -0.9, 0]);
    show({ space: 2, id: 'bulb', n: 2, c: [0.1, 0, 0] }, [0, 0, 0]);
    for (const a of AP) for (const v of [[0.5, 0.7, 0.4], [0, 0, 0], [-1, 0, 0], [0, 0, 1], [0.6, -0.3, 0]]) show({ space: 3, id: a.id, n: 2, c: C, params: SETTINGS[a.id][SETTINGS[a.id].length - 1] }, v);
    show({ space: 3, id: 'split', n: -2, c: C }, [0.5, 0.7, -0.4]);
    show({ space: 3, id: 'split', n: -2, c: C }, [0, 0, 0]);
    show({ space: 3, id: 'lathe', n: -1, c: C }, [0, 0, 0]);
    show({ space: 3, id: 'bulb', n: 5, c: C }, [0.5, 0.7, 0.9]);
    show({ space: 3, id: 'classic', n: 2, c: C }, [0.5, 0.7, 0]);
    return out.join('\n');
  }
  // more powers and dial values, the truth check and the sentences only
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
  // which approaches, with their dials at the start, follow the complex power in the plane z = 0 and on the x-axis?
  function agree() {
    const pl = points(2).filter(p => len(p) > 1e-3), li = points(1).filter(p => len(p) > 1e-3), out = [];
    for (const a of AP) for (const n of POWERS) {
      const q = L.S.param[a.id], cnt = pts => pts.filter(p => { const w = MATH[a.id](p, n, q), z = cpow(p[0], p[1], n), want = [z[0], z[1], 0]; return len(sub(w, want)) <= 1e-9 * Math.max(1, len(want)); }).length;
      out.push(`${a.id} n=${n}: plane ${cnt(pl)}/${pl.length} line ${cnt(li)}/${li.length} | note2: ${learnPlan({ space: 2, id: a.id, n, params: q }).note.split('flat picture.')[1]} | note1: ${learnPlan({ space: 1, id: a.id, n, params: q }).note.split('flat picture.')[1]}`);
    }
    for (const [id, q, n] of [['mercator', { turn: 40 }, 2], ['mercator', { lift: 0.5 }, 2], ['tilt', { tilt: 1 }, 2.5], ['tilt', { tilt: 1 }, 2], ['bulb', { lat: 30 }, 2], ['bulb', { lon: 30 }, 3], ['classic', { theta: -90 }, 2], ['pillow', { layout: 1 }, 2], ['axisbulb', { k: 2 }, 2], ['axisbulb', { k: 5 }, 2], ['lathe', { spin: 3 }, 2]])
      out.push(`${id} ${JSON.stringify(q)} n=${n} | note2: ${learnPlan({ space: 2, id, n, params: q }).note.split('flat picture.')[1]} | note1: ${learnPlan({ space: 1, id, n, params: q }).note.split('flat picture.')[1]}`);
    return out.join(String.fromCharCode(10));
  }
  window.__LT = { space3, flat, samples, extra, agree };
})();
