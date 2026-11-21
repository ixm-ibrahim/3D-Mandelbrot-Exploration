// ---------- STAND-IN for 65-learn-steps.js (view engineer's test copy, never shipped).
// Same interface as docs/ROUND13.md: learnPlan, learnRun, learnCheck. Flat spaces and `lathe` only: every other
// approach id is answered with the lathe moves, and the note says so.
function learnPlan(o) {
  const n = +o.n, c = o.c || [0, 0, 0], space = o.space;
  const f = x => (Math.round(x * 100) / 100 + 0).toFixed(2).replace('-', '−');
  const dg = a => String(Math.round(a * 180 / PI)).replace('-', '−') + '°';
  const rotZ = (v, a) => [Math.cos(a) * v[0] - Math.sin(a) * v[1], Math.sin(a) * v[0] + Math.cos(a) * v[1], v[2]];
  const stretch = {
    key: 'stretch', name: 'Stretch', hidden: false,
    say: (a, b) => `Stretch: the length ${f(len(a))} becomes ${f(len(b))}, the length raised to the power ${f(n)}.`,
    at: (v, t) => { const r = len(v); return r > 0 ? scl(v, Math.pow(r, t * (n - 1))) : v.slice(); },
    hinge: () => null, sheet: () => null,
  };
  const shift = {
    key: 'shift', name: 'Add c', hidden: false,
    say: () => `Add c: the point slides by c and the step is done.`,
    at: (v, t) => add(v, scl(c, t)),
    hinge: () => null, sheet: () => null,
  };
  if (space === 1) {
    const turn = {
      key: 'turn', name: 'Turn', hidden: true,
      say: a => (a[0] < 0 ? `Turn: a negative number leans 180°, so it swings by ${dg((n - 1) * PI)} through the hidden direction.`
        : `Turn: a positive number leans 0°, so it does not move.`),
      at: (v, t) => rotZ(v, t * (n - 1) * (v[0] < 0 ? PI : 0)),
      hinge: () => [0, 0, 1], sheet: () => [[1, 0, 0], [0, 1, 0]],
    };
    return { moves: [turn, stretch, shift], note: 'Stand-in steps: a line.' };
  }
  if (space === 2) {
    const turn = {
      key: 'turn', name: 'Turn', hidden: false,
      say: (a, b) => `Turn: the lean ${dg(Math.atan2(a[1], a[0]))} becomes ${dg(n * Math.atan2(a[1], a[0]))}, a turn about the z-axis.`,
      at: (v, t) => rotZ(v, t * (n - 1) * Math.atan2(v[1], v[0])),
      hinge: () => [0, 0, 1], sheet: () => [[1, 0, 0], [0, 1, 0]],
    };
    return { moves: [turn, stretch, shift], note: 'Stand-in steps: on a page every approach takes the same three moves.' };
  }
  const frame = v => { const rho = Math.hypot(v[1], v[2]); return { rho, u: rho > 1e-12 ? [0, v[1] / rho, v[2] / rho] : [0, 1, 0], al: Math.atan2(rho, v[0]) }; };
  const turn = {
    key: 'turn', name: 'Turn', hidden: false,
    say: a => { const q = frame(a); return `Turn: the angle from the x-axis, ${dg(q.al)}, becomes ${dg(n * q.al)}. The hinge is square to the x-axis and the point.`; },
    at: (v, t) => { const q = frame(v), r = len(v), al = q.al * (1 + t * (n - 1)); return [r * Math.cos(al), r * Math.sin(al) * q.u[1], r * Math.sin(al) * q.u[2]]; },
    hinge: v => { const q = frame(v); return norm(cross([1, 0, 0], q.u)); },
    sheet: v => [[1, 0, 0], frame(v).u],
  };
  return { moves: [turn, stretch, shift], note: o.id === 'lathe' ? 'Stand-in steps for the quaternion square.' : 'Stand-in steps: only the quaternion square is written out, so that is what plays here.' };
}
function learnRun(plan, v) {
  const out = [v.slice()];
  for (const m of plan.moves) out.push(m.at(out[out.length - 1], 1));
  return out;
}
function learnCheck() { return 0; }
