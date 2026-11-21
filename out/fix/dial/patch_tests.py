"""One-off edit of tests/dial.html and tests/dial.json for the fix round: the two checks that asserted the old
behaviour (p2-1, p13-4) now assert the new one, and checks are added for the there-and-back sweep and for extreme
values. Kept for the record; it refuses to run twice."""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'tests', 'dial.html')
s = io.open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


# showcase: three dials carry a wide range, and Lift plays there and back
rep("{ type: 'dial', key: 'iter', label: 'Iterations', min: 3, max: 60, step: 1, def: 14, hi: 400, int: true },",
    "{ type: 'dial', key: 'iter', label: 'Iterations', min: 3, max: 60, step: 1, def: 14, hi: 400, xmax: 2000, xhi: 100000, int: true },")
rep("{ type: 'dial', key: 'lift', label: 'Lift', min: -2, max: 2, step: 0.01, def: 0, animate: true },",
    "{ type: 'dial', key: 'lift', label: 'Lift', min: -2, max: 2, step: 0.01, def: 0, xmin: -6, xmax: 6, animate: 'bounce' },")
rep("{ type: 'dial', key: 'cx', label: 'Turning-out sphere, centre x', min: -1.5, max: 1.5, step: 0.005, def: 1, lo: -6, hi: 6 },",
    "{ type: 'dial', key: 'cx', label: 'Turning-out sphere, centre x', min: -1.5, max: 1.5, step: 0.005, def: 1, lo: -6, hi: 6, xlo: -60, xhi: 60 },")

# a check that fails half way must not leave extreme values on for the checks after it
rep("""    try { await fn(); } catch (e) { ok = false; info = e.message; }
    results.push({ name, ok, info });
""", """    try { await fn(); } catch (e) { ok = false; info = e.message; }
    if (isExtreme()) setExtreme(false);
    results.push({ name, ok, info });
""")

# p2-1: a step of 1 means the next whole number everywhere
rep("""  await check('Whole-number dials (int with step 1, odd) and dials whose step is already 1 have no toggle', () => {
    eq(mk({ step: 1, opts: { int: true } }).mode, null, 'int');
    eq(mk({ step: 2, opts: { odd: true } }).mode, null, 'odd');
    eq(mk({ step: 1 }).mode, null, 'step 1');
    eq(mk({ step: 10, max: 700, opts: { int: true } }).mode.textContent, '±10', 'a whole-number dial with a step of 10 can switch to 1');
  });
""", """  await check('Dials that hold whole numbers only and step by 1 (int, odd) have no toggle; every other dial has one', () => {
    eq(mk({ step: 1, opts: { int: true } }).mode, null, 'int');
    eq(mk({ step: 2, opts: { odd: true } }).mode, null, 'odd');
    eq(mk({ step: 10, max: 700, opts: { int: true } }).mode.textContent, '±10', 'a whole-number dial with a step of 10 can switch to 1');
    const d = mk({ step: 1, max: 120 });
    eq(d.mode.textContent, '±1', 'a dial with a step of 1 that can hold decimals starts on whole numbers'); eq(d.mode.getAttribute('aria-pressed'), 'true', 'pressed at start');
    d.mode.click(); eq(d.mode.textContent, '±0.1', 'its finer choice'); eq(d.mode.getAttribute('aria-pressed'), 'false', 'not pressed on the finer step');
  });
  await check('A step of 1 means the next whole number on every dial: 35.49 goes up to 36 and 37 and down to 35; after a press on the toggle it moves by 0.1', () => {
    let d = mk({ v: 35.49, min: 10, max: 120, step: 1, opts: { lo: 2, hi: 150 } });
    press(d.up); eq(d.st.v, 36, 'up'); eq(d.n.value, '36', 'box'); press(d.up); eq(d.st.v, 37, 'up again');
    d = mk({ v: 35.49, min: 10, max: 120, step: 1 }); d.n.focus(); key(d, 'ArrowDown'); eq(d.st.v, 35, 'ArrowDown'); key(d, 'ArrowDown', { shiftKey: true }); eq(d.st.v, 25, 'ten down');
    d = mk({ v: 34.2, min: -180, max: 180, step: 1, opts: { animate: true } }); press(d.up); eq(d.st.v, 35, 'the value a paused sweep leaves, 34.2, goes up to 35');
    d = mk({ v: 35.49, min: 10, max: 120, step: 1 }); d.mode.click(); press(d.up); eq(d.st.v, 35.59, 'fine step up'); press(d.down); press(d.down); eq(d.st.v, 35.39, 'fine step down twice');
    slide(d, 60); eq(d.st.v, 60, 'the slider still moves by 1');
  });
""")

# p13-4: a closed section does not stop a sweep; p14-1: there and back
rep("""  await check('The sweep pauses when the control is hidden, when its section is closed, and when something around it is not displayed', async () => {
    const d = mk({ v: 0, opts: { animate: true } });
    d.play.click(); await frames(3); yes(d.st.v > 0, 'it should be moving first');
    d.el.hidden = true; await frames(3);
    eq(d.play.getAttribute('aria-pressed'), 'false', 'paused when hidden'); const v1 = d.st.v; await frames(3); eq(d.st.v, v1, 'value while hidden');
    d.el.hidden = false; await frames(3); eq(d.st.v, v1, 'it stays paused when shown again');
    const sec = document.createElement('details'); sec.open = true; sec.innerHTML = '<summary>Section</summary><div></div>'; fixture.appendChild(sec);
    const e = mk({ v: 0, host: sec.lastChild, opts: { animate: true } });
    e.play.click(); await frames(3); yes(e.st.v > 0, 'the dial in the section should be moving first');
    sec.open = false; await frames(3); eq(e.play.getAttribute('aria-pressed'), 'false', 'paused when the section closes');
    sec.open = true; e.play.click(); await frames(3); sec.style.display = 'none'; await frames(3); eq(e.play.getAttribute('aria-pressed'), 'false', 'paused when the section is not displayed');
    sec.remove();
  });
""", """  await check('The sweep pauses when the control is hidden and when something around it is not displayed, and stays paused when it is shown again', async () => {
    const d = mk({ v: 0, opts: { animate: true } });
    d.play.click(); await frames(3); yes(d.st.v > 0, 'it should be moving first');
    d.el.hidden = true; await frames(3);
    eq(d.play.getAttribute('aria-pressed'), 'false', 'paused when hidden'); const v1 = d.st.v; await frames(3); eq(d.st.v, v1, 'value while hidden');
    d.el.hidden = false; await frames(3); eq(d.st.v, v1, 'it stays paused when shown again');
    const wrap = document.createElement('div'); wrap.innerHTML = '<div></div>'; fixture.appendChild(wrap);
    const e = mk({ v: 0, host: wrap.lastChild, opts: { animate: true } });
    e.play.click(); await frames(3); yes(e.st.v > 0, 'the dial in the wrapper should be moving first');
    wrap.style.display = 'none'; await frames(3); eq(e.play.getAttribute('aria-pressed'), 'false', 'paused when something around it is not displayed');
    wrap.remove();
  });
  await check('Folding a section away does not stop a sweep inside it: it plays on while the section is closed and after it is opened again; hiding the section does stop it', async () => {
    const sec = document.createElement('details'); sec.open = true; sec.innerHTML = '<summary>Section</summary><div></div>'; fixture.appendChild(sec);
    const e = mk({ v: 0, host: sec.lastChild, opts: { animate: true } });
    e.play.click(); await frames(3); yes(e.st.v > 0, 'the dial in the section should be moving first');
    sec.open = false; await frames(4); eq(e.play.getAttribute('aria-pressed'), 'true', 'still playing in the closed section');
    const v1 = e.st.v; await frames(4); yes(e.st.v > v1, 'the value keeps moving while the section is closed');
    sec.open = true; await frames(3); eq(e.play.getAttribute('aria-pressed'), 'true', 'still playing after opening');
    sec.open = false; await frames(2); sec.hidden = true; await frames(3); eq(e.play.getAttribute('aria-pressed'), 'false', 'paused when the closed section is hidden');
    sec.remove();
  });
  await check('animate: "bounce" sweeps there and back: the value turns round at the top and at the bottom and never jumps from one end to the other', async () => {
    const d = mk({ v: 9.9, min: 0, max: 10, step: 0.1, opts: { animate: 'bounce' } });
    const jump = a => a.reduce((m, v, i) => (i ? Math.max(m, Math.abs(v - a[i - 1])) : 0), 0);
    d.play.click();
    const high = [d.st.v];
    for (let i = 0; i < 30; i++) { await frames(1); high.push(d.st.v); }
    yes(Math.max(...high) > 9.95, 'it should reach the top, got ' + Math.max(...high)); yes(high[high.length - 1] < Math.max(...high) - 0.1, 'after the top it should come down: ' + high.join(' '));
    d.st.v = 0.1;   // moved from outside on its way down: it carries on down from there
    const low = [d.st.v];
    for (let i = 0; i < 30; i++) { await frames(1); low.push(d.st.v); }
    d.play.click();
    yes(Math.min(...low) < 0.05, 'it should reach the bottom, got ' + Math.min(...low)); yes(low[low.length - 1] > Math.min(...low) + 0.1, 'after the bottom it should go up: ' + low.join(' '));
    yes(jump(high) < 0.5 && jump(low) < 0.5, 'largest change between two frames: ' + Math.max(jump(high), jump(low)));
    yes(d.st.sets.every(v => v >= 0 && v <= 10), 'values outside the range: ' + d.st.sets.filter(v => v < 0 || v > 10).join(' '));
    yes(/and back/.test(d.play.title), 'the play button says it goes there and back: ' + d.play.title);
  });
""")

# extreme values
rep("""  // ----- hint
""", """  // ----- extreme values
  const xi = { int: true, hi: 400, xmax: 1000, xhi: 100000 };   // Iterations, as the lab might widen it
  const lim = d => [d.r.min, d.r.max, d.n.getAttribute('aria-valuemin'), d.n.getAttribute('aria-valuemax')].join(' ');
  await check('Extreme values: setExtreme(true) gives a dial its wide slider range (xmin, xmax) and typed limits (xlo, xhi), a dial without them is left alone, and isExtreme() reports the switch', () => {
    const d = mk({ v: 14, min: 3, max: 60, step: 1, opts: xi }), plain = mk({ v: 5 });
    eq(isExtreme(), false, 'off at first'); eq(lim(d), '3 60 3 400', 'normal range');
    setExtreme(true);
    eq(isExtreme(), true, 'on'); eq(lim(d), '3 1000 3 100000', 'wide range'); eq(lim(plain), '0 10 0 10', 'a dial without the fields');
    enter(d, '900'); eq(d.st.v, 900, 'typed 900'); eq(d.r.value, '900', 'thumb'); yes(!d.el.classList.contains('is-out'), '900 lies on the wide slider');
    enter(d, '250000'); eq(d.st.v, 100000, 'clamped to xhi'); enter(d, '1'); eq(d.st.v, 3, 'there is no xlo, so the normal low limit holds');
    slide(d, 640); eq(d.st.v, 640, 'the slider reaches 640'); enter(plain, '15'); eq(plain.st.v, 10, 'the plain dial keeps its limits');
    setExtreme(false); eq(isExtreme(), false, 'off again'); eq(lim(d), '3 60 3 400', 'normal range again');
  });
  await check('Extreme values: any of the four fields may be missing; the normal value stays, and a typed limit goes out with the slider when only the slider end is given', () => {
    const a = mk({ v: 0, min: -2, max: 2, step: 0.01, opts: { lo: -6, hi: 6, xmin: -6, xmax: 6, xlo: -20, xhi: 20 } });
    const b = mk({ v: 0, min: -2, max: 2, step: 0.01, opts: { lo: -6, hi: 6, xhi: 50 } });
    const c = mk({ v: 5, min: 0, max: 10, step: 0.5, opts: { xmax: 100 } });
    const e = mk({ v: 5, min: 0, max: 10, step: 0.5, opts: { lo: 1, hi: 9, xmin: -5 } });
    const f = mk({ v: 1, min: -7, max: 9, step: 2, opts: { odd: true, xmin: -20, xmax: 20 } });
    setExtreme(true);
    eq(lim(a), '-6 6 -20 20', 'all four'); eq(lim(b), '-2 2 -6 50', 'xhi alone'); eq(lim(c), '0 100 0 100', 'xmax alone');
    eq(lim(e), '-5 10 -5 9', 'xmin alone: only the low side moves'); eq(lim(f), '-20 20 -19 19', 'an odd dial keeps odd limits');
    enter(f, '18'); eq(f.st.v, 19, 'and odd values');
    setExtreme(false); eq(lim(a), '-2 2 -6 6', 'back'); eq(lim(c), '0 10 0 10', 'back'); eq(f.st.v, 9, 'the odd dial is pulled back to its highest normal value');
  });
  await check('Switching extreme values off brings a value beyond the normal typed limits back to the nearest limit, through the setter, once; a value inside them is left alone even beyond the slider', () => {
    const d = mk({ v: 14, min: 3, max: 60, step: 1, opts: xi }), f = mk({ v: 14, min: 3, max: 60, step: 1, opts: xi });
    const e = mk({ v: 0, min: -2, max: 2, step: 0.01, opts: { lo: -6, hi: 6, xmin: -6, xmax: 6, xlo: -20, xhi: 20 } });
    setExtreme(true); enter(d, '640'); enter(e, '-12.5'); enter(f, '250');
    const calls = [d, e, f].map(x => x.st.sets.length);
    setExtreme(false);
    eq(d.st.v, 400, 'above the limit'); eq(d.n.value, '400', 'box'); eq(d.st.sets.length, calls[0] + 1, 'setter calls'); eq(d.st.sets[calls[0]], 400, 'what the setter was given');
    eq(e.st.v, -6, 'below the limit'); eq(e.n.value, '-6', 'box'); eq(e.st.sets.length, calls[1] + 1, 'setter calls below');
    eq(f.st.v, 250, 'inside the typed limits'); eq(f.st.sets.length, calls[2], 'no setter call'); yes(f.el.classList.contains('is-out'), 'beyond the slider, so the thumb waits at its end'); eq(f.r.value, '60', 'thumb');
    setExtreme(false); eq(d.st.sets.length, calls[0] + 1, 'switching off twice writes nothing more');
  });
  await check('A dial made while extreme values are on starts with its wide range', () => {
    setExtreme(true);
    const d = mk({ v: 700, min: 3, max: 60, step: 1, opts: xi });
    eq(lim(d), '3 1000 3 100000', 'range'); eq(d.r.value, '700', 'thumb'); eq(visible($(d.id + 'Wide')), true, 'tag');
    setExtreme(false); eq(lim(d), '3 60 3 400', 'range after switching off'); eq(d.st.v, 400, 'value pulled back');
  });
  await check('A widened dial shows a small tag, "wide", in front of its box, with the range in its tooltip and a colour from the theme; with the switch off, or without a wide range, there is none', () => {
    const d = mk({ v: 14, min: 3, max: 60, step: 1, opts: xi }), plain = mk(), tag = $(d.id + 'Wide');
    eq(plain.el.querySelector('.dial-wide'), null, 'plain dial'); yes(tag && d.el.querySelector('.dial-box').contains(tag), 'the tag belongs to the box cluster');
    eq(visible(tag), false, 'hidden while off'); yes(!d.el.classList.contains('is-wide'), 'class while off');
    setExtreme(true);
    eq(visible(tag), true, 'shown while on'); eq(tag.textContent, 'wide', 'text'); yes(d.el.classList.contains('is-wide'), 'class while on');
    yes(/3 to 1000,/.test(tag.title) && /3 to 100000\\./.test(tag.title), 'tooltip: ' + tag.title); yes(/100000/.test(d.n.title), 'the box tooltip states the limits in use: ' + d.n.title);
    yes(tag.getBoundingClientRect().right <= d.box.getBoundingClientRect().left, 'the tag sits before the box'); yes(parseFloat(getComputedStyle(tag).fontSize) <= 12, 'small type');
    const root = document.documentElement, was = root.getAttribute('data-theme');
    root.setAttribute('data-theme', 'dark'); const dark = getComputedStyle(tag).color; root.setAttribute('data-theme', 'light'); const light = getComputedStyle(tag).color;
    if (was === null) root.removeAttribute('data-theme'); else root.setAttribute('data-theme', was);
    yes(dark !== light, 'dark ' + dark + ', light ' + light);
    setExtreme(false); eq(visible(tag), false, 'hidden again');
  });
  await check('In both states the step buttons, the whole-number toggle, sync() and reset() work, and steps stop at the limits in use', () => {
    const d = mk({ v: 5.5, min: 0, max: 10, step: 0.5, opts: { def: 2, lo: 0, hi: 12, xmax: 100, xhi: 1000 } });
    for (const on of [true, false]) {
      setExtreme(on);
      const top = on ? 1000 : 12, s = on ? 'on' : 'off';
      enter(d, '5.5'); press(d.up); eq(d.st.v, 6, s + ': fine step'); d.mode.click(); press(d.up); eq(d.st.v, 7, s + ': whole step'); d.mode.click();
      enter(d, String(top - 0.2)); press(d.up); eq(d.st.v, top, s + ': a step stops at the limit'); eq(d.el.dataset.at, 'hi', s + ': marked as at the limit');
      d.st.v = 9.5; d.c.sync(); eq(d.n.value, '9.5', s + ': sync shows the state'); eq(d.r.value, '9.5', s + ': thumb after sync');
      d.c.reset(); eq(d.st.v, 2, s + ': reset'); eq(d.n.value, '2', s + ': box after reset'); eq(d.r.max, on ? '100' : '10', s + ': slider top');
    }
  });
  await check('Play sweeps the range in use: across the wide slider while extreme values are on, and on inside the normal one once they are switched off', async () => {
    const d = mk({ v: 0, min: 0, max: 10, step: 0.1, opts: { animate: 1, xmax: 40 } });
    setExtreme(true); d.play.click();
    let top = 0;
    for (let i = 0; i < 40 && top <= 10; i++) { await frames(1); top = Math.max(top, d.st.v); }
    yes(top > 10, 'it should pass the normal top of 10, got ' + top); eq(d.play.getAttribute('aria-pressed'), 'true', 'playing');
    setExtreme(false);
    const n0 = d.st.sets.length; await frames(12);
    eq(d.play.getAttribute('aria-pressed'), 'true', 'still playing after switching off'); const after = d.st.sets.slice(n0);
    yes(after.length >= 6, 'it should keep moving, got ' + after.length + ' values'); yes(d.st.sets.slice(n0 - 1).every(v => v >= 0 && v <= 10), 'values after switching off: ' + after.join(' '));
    d.play.click();
  });
  await check('Specs carry the fields through buildControls, and switching off calls the onChange of a set once, however many of its dials move', () => {
    const host = document.createElement('div'); host.className = 'sec-body'; fixture.appendChild(host);
    const obj = { a: 10, b: 20 }, log = [];
    const built = buildControls(host, [
      { type: 'dial', key: 'a', label: 'A', min: 0, max: 50, step: 1, def: 10, int: true, xmax: 500 },
      { type: 'dial', key: 'b', label: 'B', min: 0, max: 50, step: 1, def: 20, int: true, xmax: 500, xhi: 5000 },
    ], obj, () => log.push({ ...obj }), { idPrefix: 'xs-' });
    setExtreme(true); eq($('xs-a').max, '500', 'spec xmax'); eq(log.length, 0, 'switching on writes nothing');
    obj.a = 300; obj.b = 4000; built.sync(); eq($('xs-bNum').value, '4000', 'sync in the wide state');
    setExtreme(false); eq(JSON.stringify(obj), '{"a":50,"b":50}', 'both pulled back'); eq(log.length, 1, 'onChange calls');
    built.remove(); host.remove();
  });
  await check('Where the page keeps a state, S.extreme is the switch: setExtreme writes it, and changing it from code then calling syncControls() moves the ranges without writing a value', () => {
    window.S = {};   // stands in for the lab's state object; this page has none of its own
    try {
      const d = mk({ v: 14, min: 3, max: 60, step: 1, opts: xi });
      setExtreme(true); eq(window.S.extreme, true, 'setExtreme writes S.extreme'); eq(lim(d), '3 1000 3 100000', 'wide');
      d.st.v = 640; window.S.extreme = false; eq(isExtreme(), false, 'isExtreme reads S.extreme'); syncControls();
      eq(lim(d), '3 60 3 400', 'normal range after syncControls'); eq(d.st.v, 640, 'a sync does not touch the value'); eq(d.st.sets.length, 0, 'setter calls');
      window.S.extreme = true; d.c.sync(); eq(lim(d), '3 1000 3 100000', 'wide again after sync()');
      setExtreme(false); eq(d.st.v, 400, 'setExtreme(false) pulls the value back');
    } finally { delete window.S; setExtreme(false); }
  });

  // ----- hint
""")

# layout: every column is measured with the wide tags hidden and shown
rep("""    for (const host of [$('show320'), $('show295'), $('show343'), squeeze]) {
      const box = host.getBoundingClientRect();
      yes(host.scrollWidth <= host.clientWidth, `content is wider than the ${Math.round(box.width)} px column`);
""", """    for (const on of [false, true]) for (const host of [$('show320'), $('show295'), $('show343'), squeeze]) {
      setExtreme(on);   // the second round shows the "wide" tags
      const box = host.getBoundingClientRect();
      yes(host.scrollWidth <= host.clientWidth, `content is wider than the ${Math.round(box.width)} px column`);
""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)

# tests/dial.json: two more pictures of the showcase, with extreme values on, in the theme of the run and in the other one
pj = os.path.join(ROOT, 'tests', 'dial.json')
acts = json.load(io.open(pj, encoding='utf-8'))
assert len(acts) == 5 and 'showcase-extreme' not in json.dumps(acts)
extra = [
    {"js": "setExtreme(true); return 'showcase with extreme values on: Iterations, Lift and Turning-out sphere carry a wide range and show the tag';",
     "sleep": 0.3, "shot": "out/dial/showcase-extreme.png", "clip": "#showcase"},
    {"js": "const root = document.documentElement, dark = matchMedia('(prefers-color-scheme: dark)').matches; root.setAttribute('data-theme', dark ? 'light' : 'dark'); return 'the same in the ' + (dark ? 'light' : 'dark') + ' theme';",
     "sleep": 0.3, "shot": "out/dial/showcase-extreme-other-theme.png", "clip": "#showcase"},
    {"js": "document.documentElement.removeAttribute('data-theme'); setExtreme(false); return 'extreme values off again: ' + !isExtreme();"},
]
acts = acts[:4] + extra + acts[4:]
with io.open(pj, 'w', encoding='utf-8', newline='\n') as f:
    f.write('[\n' + ',\n'.join('  ' + json.dumps(a, ensure_ascii=False) for a in acts) + '\n]\n')
print('tests patched')
