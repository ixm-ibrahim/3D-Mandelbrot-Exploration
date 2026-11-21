// Engineer "dial", fix pass 7: checks of the two changes on the kit's own test page (tests/dial.html), where a dial
// can be made in any shape. Run through out/r7/dial/kit-extra.json (made by mk_kit_extra.py). Returns the lines.
const out = [], fx = document.getElementById('fixture');
let seq = 0;
const mk = (o = {}) => {
  const id = 'x' + (++seq), st = { v: o.v === undefined ? 2.37 : o.v, sets: [] };
  const c = addDial(o.host || fx, id, o.label || 'Extra ' + seq, o.min ?? 0, o.max ?? 10, o.step ?? 0.1, () => st.v, v => { st.sets.push(v); st.v = v; }, o.opts || {});
  return { c, st, id, el: c.el, n: $(id + 'Num'), mode: $(id + 'Step'), up: c.el.querySelector('.dial-up'), play: $(id + 'Play') };
};
const eq = (got, want, what) => { if (!Object.is(got, want)) throw new Error(`${what}: expected ${JSON.stringify(want)}, got ${JSON.stringify(got)}`); };
const yes = (cond, what) => { if (!cond) throw new Error(what); };
const check = async (name, fn) => {
  const made = seq;
  try { const r = await fn(); out.push('pass  ' + name + (r ? '  :: ' + r : '')); } catch (e) { out.push('FAIL  ' + name + '  :: ' + e.message); }
  if (isExtreme()) setExtreme(false);
  controls.slice().forEach(c => { if (/^x\d+$/.test(c.id) && +c.id.slice(1) > made) c.remove(); });
};
const tog = d => d.mode.textContent + ' ' + d.mode.getAttribute('aria-pressed');
const w = d => Math.round(d.n.getBoundingClientRect().width * 10) / 10;
const fits = d => d.n.scrollWidth <= d.n.clientWidth;
const inside = d => { const h = d.el.getBoundingClientRect(); return [...d.el.querySelectorAll('.dial-box, .dial-box *')].every(e => { const r = e.getBoundingClientRect(); return !r.width || (r.left >= h.left - 0.5 && r.right <= h.right + 0.5); }); };
const click = b => b.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 0 }));

// ----- controls-1: reset() puts the step back
await check('reset() puts the toggle of a fine dial back to its own step, and the arrows with it', () => {
  const d = mk({ v: 2 });
  eq(tog(d), '±0.1 false', 'opening'); d.mode.click(); eq(tog(d), '±1 true', 'after a press');
  d.st.v = 5; d.c.reset();
  eq(tog(d), '±0.1 false', 'after reset'); eq(d.st.v, 2, 'value after reset');
  yes(/by 0\.1/.test(d.mode.title) && /by 0\.1/.test(d.up.title), 'tooltips say 0.1 again: ' + d.mode.title + ' / ' + d.up.title);
  click(d.up); eq(d.st.v, 2.1, 'one step up after reset');
  d.n.focus(); d.n.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true, cancelable: true })); eq(d.st.v, 2.2, 'ArrowUp after reset');
});
await check('reset() puts a dial that opens on whole steps (step 1, decimals allowed) back to ±1', () => {
  const d = mk({ v: 35.49, min: 10, max: 120, step: 1, opts: { def: 35.49 } });
  eq(tog(d), '±1 true', 'opening'); d.mode.click(); eq(tog(d), '±0.1 false', 'after a press');
  d.c.reset(); eq(tog(d), '±1 true', 'after reset'); click(d.up); eq(d.st.v, 36, 'one step up after reset');
});
await check('reset() of a dial whose toggle was not touched changes nothing about it; dials without a toggle (int, odd) reset as before', () => {
  const a = mk({ v: 2 }), b = mk({ v: 7, min: 3, max: 60, step: 1, opts: { int: true, def: 14 } }), c = mk({ v: 5, min: -7, max: 9, step: 2, opts: { odd: true, def: 1 } });
  const t = a.mode.title; a.c.reset(); eq(tog(a), '±0.1 false', 'untouched toggle'); eq(a.mode.title, t, 'tooltip');
  yes(!b.mode && !c.mode, 'int and odd dials have no toggle'); b.c.reset(); c.c.reset(); eq(b.st.v, 14, 'int default'); eq(c.st.v, 1, 'odd default');
  click(b.up); eq(b.st.v, 15, 'int step'); click(c.up); eq(c.st.v, 3, 'odd step');
});
await check('resetGroup puts back the toggles of its group and of no other; addReset buttons do the same', () => {
  const a = mk({ v: 2, opts: { group: 'xg1' } }), b = mk({ v: 2, opts: { group: 'xg1' } }), c = mk({ v: 2, opts: { group: 'xg2' } });
  for (const d of [a, b, c]) d.mode.click();
  resetGroup('xg1'); eq(tog(a) + ', ' + tog(b), '±0.1 false, ±0.1 false', 'group xg1'); eq(tog(c), '±1 true', 'group xg2 left alone');
  const btn = addReset(fx, 'xg2', { id: 'xreset' }); btn.click(); btn.remove(); eq(tog(c), '±0.1 false', 'after the button of xg2');
  a.mode.click(); c.mode.click(); resetGroup(['xg1', 'xg2']); eq(tog(a) + ', ' + tog(c), '±0.1 false, ±0.1 false', 'two groups at once');
});
await check('sync() and syncControls() leave the toggle as the user set it (only a reset puts it back)', () => {
  const d = mk({ v: 2 }); d.mode.click(); d.st.v = 4.5; d.c.sync(); syncControls(); eq(tog(d), '±1 true', 'after sync'); eq(d.n.value, '4.5', 'box follows the state');
});
await check('A set built from specs: its reset() puts the toggles back and calls onChange once', () => {
  const host = document.createElement('div'); fx.appendChild(host);
  const obj = { a: 1.5, b: 20 }; let calls = 0;
  const set = buildControls(host, [{ type: 'dial', key: 'a', label: 'A', min: 0, max: 4, step: 0.01, def: 1 }, { type: 'dial', key: 'b', label: 'B, degrees', min: -180, max: 180, step: 1, def: 0, animate: true }], obj, () => { calls++; }, { idPrefix: 'xs-', group: 'xset' });
  $('xs-aStep').click(); $('xs-bStep').click(); eq($('xs-aStep').textContent + ' ' + $('xs-bStep').textContent, '±1 ±0.1', 'flipped');
  set.reset(); eq($('xs-aStep').textContent + ' ' + $('xs-bStep').textContent, '±0.01 ±1', 'after reset'); eq(JSON.stringify(obj), '{"a":1,"b":0}', 'values'); eq(calls, 1, 'onChange calls');
  set.remove(); host.remove();
});
await check('With extreme values on, reset() puts the toggle back and the wide range stays in use', () => {
  const d = mk({ v: 2, opts: { xmax: 100, def: 2 } }); setExtreme(true); d.mode.click(); d.st.v = 55; d.c.sync();
  d.c.reset(); eq(tog(d), '±0.1 false', 'toggle'); eq(d.st.v, 2, 'value'); eq($(d.id).max, '100', 'slider top'); yes(!$(d.id + 'Wide').hidden, 'the wide tag still shows');
});
await check('A sweep that is playing is stopped by reset() as before, and the toggle goes back too', async () => {
  const d = mk({ v: 3, opts: { animate: true, def: 1.5 } }); d.mode.click(); d.play.click(); await new Promise(r => setTimeout(r, 120));
  d.c.reset(); eq(d.play.getAttribute('aria-pressed'), 'false', 'paused'); eq(d.st.v, 1.5, 'default'); eq(tog(d), '±0.1 false', 'toggle');
});

// ----- layout-3: the box holds its number
await check('The box keeps its usual width for ordinary numbers and grows for long ones, then shrinks back', () => {
  const d = mk({ v: 2, min: -2, max: 2, step: 0.001, opts: { lo: -50, hi: 50 } });
  const base = w(d), seen = [];
  for (const v of [0, 1.5, -1.25, 12.34567, 1.732051]) { d.st.v = v; d.c.sync(); eq(w(d), base, 'width with ' + v); yes(fits(d), v + ' does not fit'); }
  let last = base;
  for (const v of [-1.732051, -12.345678, -1.2345678e-7]) { d.st.v = v; d.c.sync(); yes(w(d) > last, 'the box did not grow for ' + d.n.value); yes(fits(d), d.n.value + ' does not fit'); last = w(d); seen.push(d.n.value + ' ' + last + ' px'); }
  d.st.v = 0.5; d.c.sync(); eq(w(d), base, 'back to the usual width'); eq(d.n.style.getPropertyValue('--dial-len'), '3', 'the length the script wrote');
  return 'usual width ' + base + ' px; ' + seen.join(', ');
});
await check('Typing a long number does not resize the box until it is committed; a refused or cancelled entry leaves it as it was', () => {
  const d = mk({ v: 2, min: -2, max: 2, step: 0.001, opts: { lo: -50, hi: 50 } }), base = w(d);
  d.n.focus(); d.n.value = '-1.2345678901'; d.n.dispatchEvent(new Event('input', { bubbles: true })); eq(w(d), base, 'while typing');
  d.c.sync(); eq(w(d), base, 'a sync during the edit'); eq(d.n.value, '-1.2345678901', 'the edit is left alone');
  d.n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); eq(d.n.value, '-1.234568', 'committed'); yes(w(d) > base && fits(d), 'the box holds the committed number');
  d.n.value = 'abcdefghijklmnop'; d.n.dispatchEvent(new Event('input', { bubbles: true })); d.n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }));
  eq(d.n.value, '-1.234568', 'refused'); yes(fits(d), 'still fits after a refusal');
  d.n.value = '9'; d.n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true })); eq(d.n.value, '-1.234568', 'cancelled'); d.n.blur();
});
await check('A state value that is not a number shows an empty box of the usual width, and the next number is shown whole', () => {
  const d = mk({ v: 2, min: -2, max: 2, step: 0.001, opts: { lo: -50, hi: 50 } }), base = w(d);
  d.st.v = NaN; d.c.sync(); eq(d.n.value, '', 'empty box'); eq(w(d), base, 'width'); d.st.v = -0.122561; d.c.sync(); yes(fits(d) && w(d) > base, 'the next long number fits');
});
await check('In a column too narrow for the whole cluster the box gives up width and nothing sticks out, with a short and with a long number', () => {
  const res = [];
  for (const px of [343, 295, 240, 200]) {
    const host = document.createElement('div'); host.style.cssText = 'width:' + px + 'px; display:flex; flex-direction:column; gap:14px'; fx.appendChild(host);
    const d = mk({ host, v: 0.5, min: -2, max: 2, step: 0.01, label: 'Lift toward the pole', opts: { xmin: -6, xmax: 6, animate: 'bounce' } });
    setExtreme(true);
    yes(inside(d), px + ' px, short number: something sticks out');
    d.st.v = -1.234567; d.c.sync(); yes(inside(d), px + ' px, long number: something sticks out');
    res.push(px + ' px: box ' + w(d) + ' px, ' + (fits(d) ? 'number whole' : 'number cut (no room)'));
    setExtreme(false); d.c.remove(); host.remove();
  }
  return res.join('; ');
});
await check('While a sweep plays, the box keeps one width (the play button does not move under the pointer)', async () => {
  const d = mk({ v: 0, min: 0, max: 2, step: 0.005, opts: { animate: 0.4 } }), base = w(d), x0 = d.play.getBoundingClientRect().left;
  d.play.click(); let moved = 0, n = 0;
  for (let i = 0; i < 30; i++) { await new Promise(r => requestAnimationFrame(r)); n++; if (w(d) !== base || d.play.getBoundingClientRect().left !== x0) moved++; }
  d.play.click(); eq(moved, 0, 'frames in which the box or the button moved, of ' + n);
});
return out;
