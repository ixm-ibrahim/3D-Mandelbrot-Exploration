// ---------- controls kit: dials (a slider plus a typed box with step buttons), checkboxes, drop-downs,
// and controls built from specs. `host` is an element or the id of one. Every control registers itself
// so it can be re-read (syncControls) or put back to its default (resetGroup).
const controls = [];      // { el, group, sync(), reset(), remove() }
const dialSets = [];      // one entry per buildControls call; update() re-checks its `when` rules
const hostEl = h => (typeof h === 'string' ? $(h) : h);
let dialBatch = null;     // while resetGroup runs: change callbacks waiting to be called once at the end

// ----- numbers as text
// Decimals needed to write x (at most 10): 3 -> 0, 0.1 -> 1, 2.37 -> 2. Step arithmetic is rounded to
// this many places, so 2.3 + 0.1 gives 2.4 and never 2.4000000000000004.
function dialDecimals(x) {
  for (let d = 0; d < 10; d++) if (Math.abs(+x.toFixed(d) - x) <= 1e-12 * Math.max(1, Math.abs(x))) return d;
  return 10;
}
// The text a typed box shows: at most 6 decimals, no trailing zeros, plain digits for every ordinary size.
// Only a value too small for 6 decimals (or astronomically large) falls back to the 1e-7 form, which
// dialParse reads back.
function dialFmt(v) {
  v = Number(v);
  if (!isFinite(v)) return '';
  const a = Math.abs(v);
  if ((a !== 0 && a < 1e-6) || a >= 1e15) return String(+v.toPrecision(7)).replace('e+', 'e');
  const t = v.toFixed(6).replace(/\.?0+$/, '');
  return t === '-0' ? '0' : t;
}
// What someone typed, as a number, or NaN. Accepts spaces around it, a typographic minus or dash for the
// sign, one decimal comma, and scientific notation. Everything else is refused, never half-read.
function dialParse(text) {
  let t = String(text).trim().replace(/[\u2212\u2010-\u2015\uFE63\uFF0D]/g, '-');   // minus sign, hyphens and dashes, small and full-width minus
  if (t.indexOf(',') >= 0 && t.indexOf(',') === t.lastIndexOf(',') && t.indexOf('.') < 0) t = t.replace(',', '.');
  if (!/^[+-]?(\d+\.?\d*|\.\d+)(e[+-]?\d+)?$/i.test(t)) return NaN;
  const v = Number(t);
  return isFinite(v) ? v + 0 : NaN;   // + 0 turns -0 into 0
}
// True when the element is hidden for real: the hidden attribute or display none, on it or on anything around it
// (a `when` rule, the panel of another approach, a section of another mode). A closed section does not count:
// the user only folded it away, and what plays inside it keeps playing.
function dialGone(el) {
  if (!el.isConnected) return true;
  if (el.checkVisibility && el.checkVisibility()) return false;
  for (let n = el; n; n = n.parentElement) if (getComputedStyle(n).display === 'none') return true;
  return false;
}
// The iPhone's decimal keypad has no minus key, so there a dial that accepts negative numbers gets the full keyboard.
const DIAL_NO_MINUS_KEY = /iP(hone|ad|od)/.test(navigator.userAgent) || (/Mac/.test(navigator.userAgent) && navigator.maxTouchPoints > 1);
const DIAL_ICON = {
  up: '<svg viewBox="0 0 10 6" aria-hidden="true"><path d="M1.5 5 5 1.5 8.5 5"/></svg>',
  down: '<svg viewBox="0 0 10 6" aria-hidden="true"><path d="M1.5 1 5 4.5 8.5 1"/></svg>',
  play: '<svg class="i-play" viewBox="0 0 10 10" aria-hidden="true"><path d="M2.5 1 9 5 2.5 9z"/></svg>',
  pause: '<svg class="i-pause" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 1h2.2v8H2zM5.8 1H8v8H5.8z"/></svg>',
};

// ----- sweeping dials share one animation-frame loop
const dialSweeps = new Set();   // one function per playing dial, called with the milliseconds since the last frame
let dialSweepFrame = 0, dialSweepLast = 0;
function dialSweepTick(now) {
  const dt = clamp(now - dialSweepLast, 0, 250);   // a stalled frame must not show up as a jump
  dialSweepLast = now;
  dialSweepFrame = 0;
  // if one dial's setter throws, the error is reported and the other sweeps keep running
  try { [...dialSweeps].forEach(f => f(dt)); }
  finally { if (dialSweeps.size && !dialSweepFrame) dialSweepFrame = requestAnimationFrame(dialSweepTick); }
}
function dialSweep(f, on) {
  if (on) dialSweeps.add(f); else dialSweeps.delete(f);
  if (dialSweeps.size && !dialSweepFrame) { dialSweepLast = performance.now(); dialSweepFrame = requestAnimationFrame(dialSweepTick); }
}

// ----- extreme values: one switch for every dial
// A dial may carry a second, wider range: o.xmin/o.xmax for the slider and o.xlo/o.xhi for typed values. While the
// switch is on, every dial that has one uses it. The flag lives in the page state (S.extreme) where there is one,
// so it is saved, restored and synced like any other value; the kit's own test page has no state and uses the
// copy kept here.
let dialExtremeOwn = false;
function isExtreme() { return typeof S !== 'undefined' && S && S.extreme !== undefined ? !!S.extreme : dialExtremeOwn; }
// Switch extreme values on or off for every dial, present and future. Switching off also brings any value that
// lies beyond its dial's normal typed limits back to the nearest limit, through the dial's setter, so the picture
// follows. (Changing S.extreme from code and calling syncControls() moves the ranges too, but writes nothing.)
function setExtreme(on) {
  dialExtremeOwn = !!on;
  if (typeof S !== 'undefined' && S) S.extreme = dialExtremeOwn;
  dialQuietly(() => controls.forEach(c => { if (c.rerange) c.rerange(!dialExtremeOwn); }));
}

// ----- the dial
// min/max/step describe the slider. o.lo/o.hi are the hard limits for typed and stepped values (default: the
// slider's range). o.int: whole numbers only. o.odd: odd whole numbers only. o.def: the value reset() restores
// (default: the value at creation). o.animate: true (or seconds per sweep) adds a play button that sweeps the value
// to the top of the slider and starts again at the bottom, which suits an angle; 'bounce' sweeps there and back,
// for a value whose two ends give different pictures. o.help: a hint.
// o.slider: false leaves the slider out (label and typed box only; the label then points at the box).
// o.xmin/o.xmax: the slider's range while extreme values are on (setExtreme); o.xlo/o.xhi: the typed limits then.
// Any of the four may be missing: the normal value stays, except that a typed limit moves out with the slider
// when xmin or xmax reaches beyond it.
// The label is HTML. The state stays the single source of truth: the dial reads it with get() and never keeps
// a copy, so a value outside the slider's range, or finer than its step, survives until the user changes it.
function addDial(host, id, label, min, max, step, get, set, o = {}) {
  step = step > 0 ? +step : 1;
  const odd = !!o.odd, int = odd || !!o.int;
  const given = v => v !== undefined && v !== null;
  const normal = { min: +min, max: +max }, wide = {};
  normal.lo = given(o.lo) ? +o.lo : normal.min; normal.hi = given(o.hi) ? +o.hi : normal.max;
  wide.min = given(o.xmin) ? +o.xmin : normal.min; wide.max = given(o.xmax) ? +o.xmax : normal.max;
  wide.lo = given(o.xlo) ? +o.xlo : given(o.xmin) ? Math.min(normal.lo, wide.min) : normal.lo;
  wide.hi = given(o.xhi) ? +o.xhi : given(o.xmax) ? Math.max(normal.hi, wide.max) : normal.hi;
  const canWiden = ['min', 'max', 'lo', 'hi'].some(k => wide[k] !== normal[k]);
  // The range in use: min, max and span for the slider, lo and hi for typed and stepped values.
  let span, lo, hi, gridDec, isWide;
  const useRange = () => {
    isWide = canWiden && isExtreme();
    const R = isWide ? wide : normal;
    min = R.min; max = R.max; span = max - min;
    // the hard limits, moved inward onto numbers this dial can hold
    lo = odd ? 2 * Math.ceil((R.lo - 1) / 2) + 1 : int ? Math.ceil(R.lo) : R.lo;
    hi = odd ? 2 * Math.floor((R.hi - 1) / 2) + 1 : int ? Math.floor(R.hi) : R.hi;
    gridDec = Math.max(dialDecimals(min), dialDecimals(step));
  };
  useRange();
  const fix = v => {
    if (odd) v = 2 * Math.round((v - 1) / 2) + 1;   // nearest odd whole number; a tie goes up
    else if (int) v = Math.round(v);
    return clamp(v, lo, hi) + 0;
  };
  const def = o.def === undefined ? get() : o.def;
  // The arrows choose between the dial's own step and whole numbers. A dial whose own step is 1 but which can hold
  // decimals gets 0.1 as its finer choice and starts on whole numbers, so "±1" means the same on every dial: to the
  // next whole number. A dial that only holds whole numbers and steps by 1 has nothing to choose.
  const fine = step === 1 && !int ? 0.1 : step;
  const canToggle = !odd && fine !== 1;
  const canPlay = !!o.animate && (normal.max > normal.min || wide.max > wide.min);
  const bounce = o.animate === 'bounce';
  const period = (typeof o.animate === 'number' ? o.animate : 8) * 1000;
  const bare = o.slider === false;

  const el = document.createElement('div');
  el.className = bare ? 'dial dial-bare' : 'dial';
  if (o.group !== undefined) el.dataset.group = o.group;
  el.innerHTML =
    `<label class="label" for="${id}${bare ? 'Num' : ''}">${label}</label><div class="dial-box">` +
    (canWiden ? `<span class="dial-wide" id="${id}Wide" hidden>wide</span>` : '') +
    (canPlay ? `<button type="button" class="dial-play" id="${id}Play" aria-pressed="false">${DIAL_ICON.play}${DIAL_ICON.pause}</button>` : '') +
    (canToggle ? `<button type="button" class="dial-mode" id="${id}Step" aria-pressed="false"></button>` : '') +
    `<span class="dial-num"><input class="num" type="text" id="${id}Num" role="spinbutton" autocomplete="off" autocapitalize="off" spellcheck="false">` +
    `<span class="dial-steps"><button type="button" class="dial-up" tabindex="-1">${DIAL_ICON.up}</button>` +
    `<button type="button" class="dial-down" tabindex="-1">${DIAL_ICON.down}</button></span></span></div>` +
    (bare ? '' : `<input type="range" id="${id}" min="${min}" max="${max}" step="${step}">`) +
    (o.help ? `<p class="note dial-help" id="${id}Help"></p>` : '');
  hostEl(host).appendChild(el);
  const r = el.querySelector('input[type=range]'), n = el.querySelector('.num'), box = el.querySelector('.dial-num');
  const up = el.querySelector('.dial-up'), down = el.querySelector('.dial-down');
  const mode = el.querySelector('.dial-mode'), playBtn = el.querySelector('.dial-play'), wideTag = el.querySelector('.dial-wide');
  const name = el.querySelector('label').textContent;
  // everything on the page that states the range in use
  const paintRange = () => {
    const range = `${dialFmt(lo)} to ${dialFmt(hi)}`;
    if (r) {
      r.min = min; r.max = max;
      r.style.setProperty('--dial-d', isFinite(def) && def >= min && def <= max && span > 0 ? (def - min) / span : -1);
    }
    n.inputMode = lo < 0 && DIAL_NO_MINUS_KEY ? 'text' : 'decimal';
    n.setAttribute('aria-valuemin', lo); n.setAttribute('aria-valuemax', hi);
    n.title = odd ? `Odd whole numbers from ${range}` : int ? `Whole numbers from ${range}` : `From ${range}`;
    el.classList.toggle('is-wide', isWide);
    if (wideTag) {
      wideTag.hidden = !isWide;
      wideTag.title = bare ? `Extreme values are on. Typed values go from ${range}.`
        : `Extreme values are on. The slider runs from ${dialFmt(min)} to ${dialFmt(max)}, and typed values go from ${range}.`;
    }
  };
  n.setAttribute('aria-label', `${name}, typed value`);
  up.setAttribute('aria-label', `Increase ${name}`); down.setAttribute('aria-label', `Decrease ${name}`);
  if (o.help) {
    el.querySelector('.dial-help').textContent = o.help;
    n.setAttribute('aria-describedby', id + 'Help');
    if (r) r.setAttribute('aria-describedby', id + 'Help');
  }
  paintRange();

  const cur = () => { const v = Number(get()); return isFinite(v) ? v : NaN; };
  let shown = '';      // the text last written into the box; anything else in there is an unfinished edit
  let whole = canToggle && step === 1;   // step buttons and arrow keys: false = the fine step, true = whole numbers
  let flagTimer = 0;

  // Make the dial show the state. An unfinished edit is left alone unless `force`; the thumb is left alone
  // while the user is dragging it (`fromSlider`).
  const show = (force, fromSlider) => {
    if (canWiden && isWide !== isExtreme()) retune();   // the switch was changed in the state itself
    const v = cur(), ok = !isNaN(v);
    // The browser puts the thumb at the nearest position it has. Nothing is read back from it here, so a
    // value beyond the slider's range or between its steps stays as it is.
    if (r && !fromSlider) r.value = ok ? v : min;
    if (r) r.style.setProperty('--dial-p', ok && span > 0 ? clamp((v - min) / span, 0, 1) : 0);
    el.classList.toggle('is-out', ok && (v < min || v > max));
    el.dataset.at = !ok ? '' : v >= hi ? 'hi' : v <= lo ? 'lo' : '';
    const t = dialFmt(v);
    if (force || !(document.activeElement === n && n.value !== shown)) n.value = t;
    shown = t;
    if (ok) n.setAttribute('aria-valuenow', v); else n.removeAttribute('aria-valuenow');
  };
  const unflag = () => { clearTimeout(flagTimer); n.removeAttribute('aria-invalid'); delete box.dataset.flag; };
  const flag = kind => {
    unflag();
    if (kind === 'invalid') n.setAttribute('aria-invalid', 'true');
    box.dataset.flag = kind;
    flagTimer = setTimeout(unflag, 1400);
  };

  // ----- sweep (the play button)
  const sweepTitle = bounce ? 'Sweep this value across the slider and back, over and over' : 'Sweep this value across the slider, over and over';
  // `ph` is how far along the slider the sweep is. A there-and-back sweep carries on past `span` on its way down,
  // so its position folds back: the value never jumps from one end to the other.
  let playing = false, ph = 0, sent = NaN;
  const seat = (v, down) => { const u = clamp(v, min, max) - min; ph = down ? 2 * span - u : u; };   // carry on from v
  const sweepFrame = dt => {
    if (dialGone(el) || !(span > 0)) { sweep(false); return; }
    const now = cur();
    if (now !== sent && !isNaN(now)) seat(now, ph > span);   // something else moved the value: carry on from there
    ph += span * dt / period;
    if (bounce) ph %= 2 * span; else if (ph > span) ph %= span;
    // one decimal finer than the slider's step: smooth to the eye, short in the box
    const v = fix(+(min + (ph > span ? 2 * span - ph : ph)).toFixed(Math.min(10, dialDecimals(step) + 1)));
    if (v !== now) {
      try { set(v); } catch (e) { sweep(false); throw e; }   // a failing setter must not fail again on every frame
      show();
    }
    sent = cur();                                    // what the state holds now; a setter may round what it was given
  };
  const sweep = on => {
    if (!canPlay || on === playing) return;
    playing = on;
    if (on) { const v = cur(); seat(v >= min && v <= max ? v : min, ph > span); sent = v; }
    dialSweep(sweepFrame, on);
    playBtn.setAttribute('aria-pressed', on);
    playBtn.title = on ? 'Pause the sweep' : sweepTitle;
    el.classList.toggle('is-playing', on);
  };
  // The extreme switch changed: take the matching range, and let a running sweep carry on inside it.
  const retune = () => {
    const down = ph > span;
    useRange(); paintRange();
    if (playing) { const v = cur(); seat(isNaN(v) ? min : v, down); }
  };

  // ----- changes made by hand: each one stops a sweep, writes the state, and shows what the state now holds
  const put = v => {
    sweep(false);
    if (isFinite(v) && v !== cur()) set(v);
    show(true);
  };
  const commit = () => {
    if (n.value === shown) return;                   // nothing was typed
    const v = dialParse(n.value);
    if (isNaN(v)) { n.value = shown; flag('invalid'); return; }
    put(fix(v));
    if (v < lo || v > hi) flag('clamped'); else unflag();
  };
  const stepFrom = (from, dir, times) => {
    const b = +from.toFixed(10);                     // 2.9999999999999996 counts as 3
    if (odd) return fix((dir > 0 ? 2 * Math.floor((b + 1) / 2) + 1 : 2 * Math.ceil((b - 1) / 2) - 1) + 2 * dir * (times - 1));
    if (whole) return fix((dir > 0 ? Math.floor(b) + 1 : Math.ceil(b) - 1) + dir * (times - 1));
    return fix(+(from + dir * times * fine).toFixed(Math.min(10, Math.max(dialDecimals(from), dialDecimals(fine)))));
  };
  const nudge = (dir, times) => {
    let from = n.value !== shown ? dialParse(n.value) : NaN;   // step from what is typed, when that is a number
    if (isNaN(from)) from = cur();
    if (isNaN(from)) from = fix(Number(def) || 0);
    unflag();
    put(stepFrom(from, dir, times));
  };

  if (r) {
    r.addEventListener('input', () => {
      sweep(false);
      const v = fix(+(+r.value).toFixed(gridDec));
      if (v !== cur()) set(v);
      show(true, true);
    });
    r.addEventListener('change', () => show(true));  // on release the thumb settles on what the state holds
  }
  n.addEventListener('input', unflag);
  n.addEventListener('blur', commit);
  n.addEventListener('keydown', e => {
    if (e.isComposing) return;
    if (e.key === 'Enter') { e.preventDefault(); commit(); }
    else if (e.key === 'Escape') { n.value = shown; unflag(); }
    else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'PageUp' || e.key === 'PageDown') {
      e.preventDefault();
      nudge(e.key.endsWith('Up') ? 1 : -1, e.shiftKey || e.key.startsWith('Page') ? 10 : 1);
    }
  });
  for (const [btn, dir] of [[up, 1], [down, -1]]) {
    let timer = 0;
    const stop = () => { clearTimeout(timer); timer = 0; };
    btn.addEventListener('pointerdown', e => {
      if (e.button !== 0) return;
      e.preventDefault();                            // focus stays where it was, so a tap never opens the phone keyboard
      // Capturing the pointer means its release is reported here wherever it happens, so a repeat cannot run away.
      try { btn.setPointerCapture(e.pointerId); } catch (err) { /* a scripted press has no real pointer to capture */ }
      const times = e.shiftKey ? 10 : 1;
      const again = () => { if (document.hidden) return; nudge(dir, times); timer = setTimeout(again, 60); };
      stop(); nudge(dir, times);
      timer = setTimeout(again, 420);                // holding the button repeats
    });
    for (const ev of ['pointerup', 'pointercancel', 'lostpointercapture', 'pointerleave']) btn.addEventListener(ev, stop);
    // A click that follows a press has detail >= 1 and was handled above; keyboard and scripted clicks have 0.
    btn.addEventListener('click', e => { if (e.detail === 0) nudge(dir, e.shiftKey ? 10 : 1); });
  }
  const paintMode = () => {
    const s = dialFmt(whole ? 1 : fine), small = dialFmt(fine);
    if (mode) {
      mode.textContent = '±' + s;
      mode.setAttribute('aria-pressed', whole);
      mode.setAttribute('aria-label', `${name}: step by whole numbers`);
      mode.title = whole ? `The arrows move to the next whole number. Press for steps of ${small}.` : `The arrows change the value by ${small}. Press for whole-number steps.`;
    }
    const by = odd ? 'to the next odd number' : whole ? 'to the next whole number' : `by ${small}`;
    up.title = `Up ${by}. Hold Shift for ten steps.`; down.title = `Down ${by}. Hold Shift for ten steps.`;
  };
  if (mode) mode.addEventListener('click', () => { whole = !whole; paintMode(); });
  if (playBtn) {
    playBtn.setAttribute('aria-label', `Sweep ${name}`);
    playBtn.title = sweepTitle;
    playBtn.addEventListener('click', () => sweep(!playing));
  }
  paintMode(); show(true);

  const c = {
    el, group: o.group, id,
    sync: () => show(false),
    reset: () => { sweep(false); ph = 0; unflag(); set(def); show(true); },
    play: on => sweep(on === undefined ? !playing : !!on),
    // setExtreme calls this. `pull`: a value beyond the typed limits now in use goes back to the nearest one.
    rerange: pull => {
      retune();
      const v = cur();
      if (pull && !isNaN(v) && (v < lo || v > hi)) set(fix(v));
      show();
    },
    remove: () => { sweep(false); unflag(); el.remove(); const i = controls.indexOf(c); if (i >= 0) controls.splice(i, 1); },
  };
  controls.push(c);
  return c;
}

// A hint under a checkbox or a drop-down. Returns the element to hide or show: the control itself, or a wrapper.
function dialWithHelp(host, inner, id, help, wrapClass) {
  if (!help) { hostEl(host).appendChild(inner); return inner; }
  const wrap = document.createElement('div'), p = document.createElement('p');
  wrap.className = wrapClass;
  p.className = 'note dial-help'; p.id = id + 'Help'; p.textContent = help;
  wrap.append(inner, p);
  hostEl(host).appendChild(wrap);
  inner.querySelector('input, select').setAttribute('aria-describedby', p.id);
  return wrap;
}
const dialDrop = c => { const i = controls.indexOf(c); if (i >= 0) controls.splice(i, 1); c.el.remove(); };

// o.def: the value reset() restores (default: the value at creation). o.help: a hint. The label is HTML.
function addCheck(host, id, label, get, set, o = {}) {
  const lab = document.createElement('label');
  lab.className = 'check';
  lab.innerHTML = `<input type="checkbox" id="${id}"> <span>${label}</span>`;
  const el = dialWithHelp(host, lab, id, o.help, 'check-block');
  if (o.group !== undefined) el.dataset.group = o.group;
  const box = lab.querySelector('input'), def = o.def === undefined ? get() : o.def;
  const sync = () => { box.checked = !!get(); };
  sync();
  box.addEventListener('change', () => { set(box.checked); sync(); });
  const c = { el, group: o.group, id, sync, reset: () => { set(def); sync(); }, remove: () => dialDrop(c) };
  controls.push(c);
  return c;
}

// options: [[value, text], ...]. A third entry, [value, text, heading], puts neighbouring options that share
// a heading under it. A state value that is not among the options shows as an empty box, not as the first option.
function addSelect(host, id, label, options, get, set, o = {}) {
  const field = document.createElement('div');
  field.className = 'field';
  field.innerHTML = `<label class="label" for="${id}">${label}</label><select id="${id}"></select>`;
  const el = dialWithHelp(host, field, id, o.help, 'field-block');
  if (o.group !== undefined) el.dataset.group = o.group;
  const sel = field.querySelector('select'), def = o.def === undefined ? get() : o.def;
  const index = v => { const i = options.findIndex(([x]) => x === v); return i >= 0 ? i : options.findIndex(([x]) => String(x) === String(v)); };
  const sync = () => { sel.selectedIndex = -1; const i = index(get()); if (i >= 0) sel.value = String(i); };
  const setOptions = list => {
    options = list;
    sel.textContent = '';
    let heading, parent = sel;
    options.forEach(([, text, head], i) => {
      if (head !== heading) { heading = head; parent = head === undefined ? sel : sel.appendChild(Object.assign(document.createElement('optgroup'), { label: head })); }
      parent.appendChild(new Option(text, i));
    });
    sync();
  };
  setOptions(options);
  sel.addEventListener('change', () => { const pick = options[+sel.value]; if (pick) { set(pick[0]); sync(); } });
  const c = { el, group: o.group, id, sync, setOptions, reset: () => { set(def); sync(); }, remove: () => dialDrop(c) };
  controls.push(c);
  return c;
}

// Build controls from specs:
//   { type: 'dial',   key, label, min, max, step, def, lo, hi, xmin, xmax, xlo, xhi, int, odd, animate, help, when }
//   { type: 'select', key, label, def, options: [[value, text], ...], help, when }
//   { type: 'check',  key, label, def, help, when }
//   { type: 'note',   text, when }
// Values are read from and written to obj[key]. onChange() runs after every change. `when(obj)` decides whether a
// control is shown; it is re-checked after every change, on sync(), and on syncControls().
// o.idPrefix goes in front of each key to make the element ids; o.group names the set for resetGroup.
function buildControls(host, specs, obj, onChange, o = {}) {
  const made = [];
  const update = () => made.forEach(([s, c]) => { if (s.when) c.el.hidden = !s.when(obj); });
  const flush = () => { update(); if (onChange) onChange(); };
  const changed = () => { if (dialBatch) dialBatch.add(flush); else flush(); };
  specs.forEach((s, i) => {
    const id = (o.idPrefix || '') + (s.key === undefined ? 'note' + i : s.key);
    if (s.key !== undefined && obj[s.key] === undefined && s.def !== undefined) obj[s.key] = s.def;
    const get = () => obj[s.key], set = v => { obj[s.key] = v; changed(); };
    const opt = { ...s, group: o.group };
    let c;
    if (s.type === 'dial') c = addDial(host, id, s.label, s.min, s.max, s.step, get, set, opt);
    else if (s.type === 'select') c = addSelect(host, id, s.label, s.options, get, set, opt);
    else if (s.type === 'check') c = addCheck(host, id, s.label, get, set, opt);
    else if (s.type === 'note') {
      const p = document.createElement('p');
      p.className = 'note'; p.id = id; p.textContent = s.text;
      hostEl(host).appendChild(p);
      c = { el: p, group: o.group, id, sync() {}, reset() {}, remove() { p.remove(); } };
    } else { console.warn(`buildControls: unknown control type "${s.type}"`); return; }
    made.push([s, c]);
  });
  update();
  const built = {
    controls: made.map(([, c]) => c),
    update,
    sync: () => { made.forEach(([, c]) => c.sync()); update(); },
    reset: () => dialQuietly(() => made.forEach(([, c]) => c.reset())),
    remove: () => { made.forEach(([, c]) => c.remove()); const i = dialSets.indexOf(built); if (i >= 0) dialSets.splice(i, 1); },
  };
  dialSets.push(built);
  return built;
}
// Run something that changes many spec-built controls, then call each affected onChange once, not once per control.
function dialQuietly(work) {
  if (dialBatch) { work(); return; }
  const batch = dialBatch = new Set();
  try { work(); } finally { dialBatch = null; batch.forEach(f => f()); }
}
// A small button that puts a group (or several: pass an array) back to its defaults. o.label: its text.
// o.after: called after the reset, for state of that section that is not held by a control. o.id: element id.
function addReset(host, group, o = {}) {
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'btn dial-reset'; b.textContent = o.label || 'Reset this section';
  if (o.id) b.id = o.id;
  b.addEventListener('click', () => { resetGroup(group); if (o.after) o.after(); });
  hostEl(host).appendChild(b);
  return b;
}
// Make every control show the current state (call after changing the state from code).
function syncControls() { controls.forEach(c => c.sync()); dialSets.forEach(s => s.update()); }
// Put every control of a group (or of several: pass an array) back to its default. Each control's setter is called.
function resetGroup(group) {
  const groups = [].concat(group);
  dialQuietly(() => controls.filter(c => groups.includes(c.group)).forEach(c => c.reset()));
}
