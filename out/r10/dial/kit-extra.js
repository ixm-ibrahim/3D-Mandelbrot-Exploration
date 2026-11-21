// Engineer "dial", round 10: checks of the new rule of the arrows at a typed limit that is no round value, on the
// kit's own test page (tests/dial.html), where a dial can be made in any shape. Run through
// out/r10/dial/kit-extra.json (made by mk_kit_extra.py). Returns the lines.
const out = [], fx = document.getElementById('fixture');
let seq = 0;
const mk = (o = {}) => {
  const id = 'y' + (++seq), st = { v: o.v === undefined ? 2.37 : o.v, sets: [] };
  const c = addDial(o.host || fx, id, o.label || 'Extra ' + seq, o.min ?? 0, o.max ?? 10, o.step ?? 0.1, () => st.v, v => { st.sets.push(v); st.v = v; }, o.opts || {});
  return { c, st, id, el: c.el, n: $(id + 'Num'), mode: $(id + 'Step'), up: c.el.querySelector('.dial-up'), down: c.el.querySelector('.dial-down') };
};
const check = (name, fn) => {
  const made = seq;
  try { const r = fn(); out.push('pass  ' + name + (r ? '  :: ' + r : '')); } catch (e) { out.push('FAIL  ' + name + '  :: ' + e.message); }
  if (isExtreme()) setExtreme(false);
  controls.slice().forEach(c => { if (/^y\d+$/.test(c.id) && +c.id.slice(1) > made) c.remove(); });
};
// press the arrows as written: d down, u up, D ten down (Shift), U ten up; returns every value on the way
const go = (d, moves) => [d.st.v].concat([...moves].map(m => {
  (m.toLowerCase() === 'u' ? d.up : d.down).dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 0, shiftKey: m === 'U' || m === 'D' }));
  return d.st.v;
}));
const same = (got, want, what) => { if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${what}: expected ${JSON.stringify(want)}, got ${JSON.stringify(got)}`); return JSON.stringify(got); };

check('Trap thickness as the lab has it (0.005 to 0.5 by 0.005, typed 0.0005 to 5): down to the limit and back up on round values', () =>
  same(go(mk({ v: 0.01, min: 0.005, max: 0.5, step: 0.005, opts: { lo: 0.0005, hi: 5 } }), 'ddduuu'), [0.01, 0.005, 0.0005, 0.0005, 0.005, 0.01, 0.015], 'values'));
check('A high limit that is no round value (10.15 with steps of 0.1): up to it, and down from it to 10.1 and 10', () =>
  same(go(mk({ v: 9.9, opts: { lo: -8, hi: 10.15 } }), 'uuuudd'), [9.9, 10, 10.1, 10.15, 10.15, 10.1, 10], 'values'));
check('Ten steps at once stop on the last round value before such a limit, the next press goes to the limit, ten steps back count from the first round value', () =>
  same(go(mk({ v: 0.03, min: 0.005, max: 0.5, step: 0.005, opts: { lo: 0.0005, hi: 5 } }), 'DDdUu'), [0.03, 0.005, 0.0005, 0.0005, 0.05, 0.055], 'values'));
check('A step that changes nothing at the limit does not call the setter', () => {
  const d = mk({ v: 0.005, min: 0.005, max: 0.5, step: 0.005, opts: { lo: 0.0005, hi: 5 } });
  go(d, 'd'); const calls = d.st.sets.length; go(d, 'dd');
  if (d.st.sets.length !== calls) throw new Error('setter calls at the limit: ' + (d.st.sets.length - calls));
  return 'setter calls ' + JSON.stringify(d.st.sets);
});
check('A typed value between the round ones keeps its own offset, as before; only the limit sends the arrows back to round values', () =>
  same(go(mk({ v: 0.0125, min: 0.005, max: 0.5, step: 0.005, opts: { lo: 0.0005, hi: 5 } }), 'udddduu'), [0.0125, 0.0175, 0.0125, 0.0075, 0.0025, 0.0005, 0.005, 0.01], 'values'));
check('A limit that is a round value behaves as before (lo -8, hi 24, steps of 0.1): 23.87 goes up to 23.97 and 24, and down to 23.9', () =>
  same(go(mk({ v: 23.87, opts: { lo: -8, hi: 24 } }), 'uuud'), [23.87, 23.97, 24, 24, 23.9], 'values'));
check('The round values are the slider\'s own positions: a slider from 0.25 by 0.1 with typed limit 0.02 comes back to 0.05, 0.15, 0.25', () =>
  same(go(mk({ v: 0.25, min: 0.25, max: 5, step: 0.1, opts: { lo: 0.02, hi: 9 } }), 'ddduuu'), [0.25, 0.15, 0.05, 0.02, 0.05, 0.15, 0.25], 'values'));
check('A whole-number dial with steps of 10 and a typed limit of 25: 50, 40, 30, 25, then 30, 40', () =>
  same(go(mk({ v: 50, min: 60, max: 700, step: 10, opts: { int: true, lo: 25, hi: 3000 } }), 'ddduu'), [50, 40, 30, 25, 30, 40], 'values'));
check('A dial with a step of 1 on its finer choice 0.1, limit 0.25: 0.5, 0.4, 0.3, 0.25, then 0.3; on whole numbers 0.25 goes up to 1 as before', () => {
  const d = mk({ v: 0.5, min: 1, max: 100, step: 1, opts: { lo: 0.25, hi: 500 } });
  d.mode.click(); const a = same(go(d, 'dddu'), [0.5, 0.4, 0.3, 0.25, 0.3], 'fine');
  d.mode.click(); d.st.v = 0.25; d.c.sync(); return a + ' ' + same(go(d, 'ud'), [0.25, 1, 0.25], 'whole');
});
check('A dial without a slider (typed 0.001 to 1000, steps of 0.1): 0.2, 0.1, 0.001, then 0.1, 0.2', () =>
  same(go(mk({ v: 0.2, opts: { slider: false, lo: 0.001, hi: 1000 } }), 'dduu'), [0.2, 0.1, 0.001, 0.1, 0.2], 'values'));
check('Extreme values: the rule follows the limits in use (Mosaic cell size: 0.03 usual, 0.005 with extreme values on), and the round values stay the usual slider\'s', () => {
  const d = mk({ v: 0.05, min: 0.08, max: 1, step: 0.01, opts: { lo: 0.03, hi: 4, xmin: 0.02, xmax: 5, xlo: 0.005, xhi: 20 } });
  const a = same(go(d, 'dddu'), [0.05, 0.04, 0.03, 0.03, 0.04], 'usual');
  setExtreme(true); d.st.v = 0.02; d.c.sync();
  return a + ' ' + same(go(d, 'ddduu'), [0.02, 0.01, 0.005, 0.005, 0.01, 0.02], 'extreme');
});
check('Extreme values with a slider that starts between the round values (Surface threshold: usual 0.2 by 0.05, extreme from 0.02, typed from 0.002): the limit sends the arrows to 0.05, 0.1', () => {
  const d = mk({ v: 0.1, min: 0.2, max: 4, step: 0.05, opts: { lo: 0.02, hi: 20, xmin: 0.02, xmax: 20, xlo: 0.002, xhi: 100 } });
  setExtreme(true);
  const a = same(go(d, 'ddduu'), [0.1, 0.05, 0.002, 0.002, 0.05, 0.1], 'low end');
  d.st.v = 99.9; d.c.sync(); return a + ' ' + same(go(d, 'uuudd'), [99.9, 99.95, 100, 100, 99.95, 99.9], 'high end');
});
check('An odd dial and a whole-number dial with a step of 1 step as before at their limits', () => {
  const o = mk({ v: -5, min: -7, max: 9, step: 2, opts: { odd: true, lo: -8, hi: 10 } }), i = mk({ v: 5, min: 3, max: 60, step: 1, opts: { int: true, hi: 400 } });
  return same(go(o, 'dddu'), [-5, -7, -7, -7, -5], 'odd') + ' ' + same(go(i, 'ddduu'), [5, 4, 3, 3, 4, 5], 'int');
});
check('No floating-point noise on the way back from a limit: every value is short', () => {
  const d = mk({ v: 0.0005, min: 0.005, max: 0.5, step: 0.005, opts: { lo: 0.0005, hi: 5 } });
  const seen = go(d, 'u'.repeat(40));
  if (!seen.every(v => String(v).length <= 6)) throw new Error('long values: ' + seen.filter(v => String(v).length > 6).join(' '));
  if (seen[40] !== 0.2) throw new Error('forty steps up from 0.0005 should end on 0.2, got ' + seen[40]);
  return 'forty steps up end on ' + seen[40];
});
return out;
