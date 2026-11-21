"""One-off edit of src/js/70-dial.js for the fix round (kept for the record; it refuses to run twice)."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '70-dial.js')
s = io.open(p, encoding='utf-8').read()
n0 = len(s)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)


# ---- p13-4: what counts as hidden for a sweep
rep("""// False when the element or anything around it is not drawn: hidden, display none, or inside a closed section.
const dialVisible = el => (el.checkVisibility ? el.checkVisibility() : el.getClientRects().length > 0);
""", """// True when the element is hidden for real: the hidden attribute or display none, on it or on anything around it
// (a `when` rule, the panel of another approach, a section of another mode). A closed section does not count:
// the user only folded it away, and what plays inside it keeps playing.
function dialGone(el) {
  if (!el.isConnected) return true;
  if (el.checkVisibility && el.checkVisibility()) return false;
  for (let n = el; n; n = n.parentElement) if (getComputedStyle(n).display === 'none') return true;
  return false;
}
""")

# ---- extreme values: the switch
rep("""// ----- the dial
// min/max/step describe the slider.""", """// ----- extreme values: one switch for every dial
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
// min/max/step describe the slider.""")

rep("""// (default: the value at creation). o.animate: true (or seconds per sweep) adds a play button. o.help: a hint.
// o.slider: false leaves the slider out (label and typed box only; the label then points at the box).
""", """// (default: the value at creation). o.animate: true (or seconds per sweep) adds a play button that sweeps the value
// to the top of the slider and starts again at the bottom, which suits an angle; 'bounce' sweeps there and back,
// for a value whose two ends give different pictures. o.help: a hint.
// o.slider: false leaves the slider out (label and typed box only; the label then points at the box).
// o.xmin/o.xmax: the slider's range while extreme values are on (setExtreme); o.xlo/o.xhi: the typed limits then.
// Any of the four may be missing: the normal value stays, except that a typed limit moves out with the slider
// when xmin or xmax reaches beyond it.
""")

rep("""  min = +min; max = +max; step = step > 0 ? +step : 1;
  const odd = !!o.odd, int = odd || !!o.int, span = max - min;
  const lo0 = o.lo === undefined ? min : +o.lo, hi0 = o.hi === undefined ? max : +o.hi;
  // the hard limits, moved inward onto numbers this dial can hold
  const lo = odd ? 2 * Math.ceil((lo0 - 1) / 2) + 1 : int ? Math.ceil(lo0) : lo0;
  const hi = odd ? 2 * Math.floor((hi0 - 1) / 2) + 1 : int ? Math.floor(hi0) : hi0;
  const fix = v => {""", """  step = step > 0 ? +step : 1;
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
  const fix = v => {""")

rep("""  const canToggle = !odd && step !== 1;             // a choice between ±1 and ±1 would be no choice
  const canPlay = !!o.animate && span > 0;
  const period = (typeof o.animate === 'number' ? o.animate : 8) * 1000;
  const gridDec = Math.max(dialDecimals(min), dialDecimals(step));
  const bare = o.slider === false;
""", """  // The arrows choose between the dial's own step and whole numbers. A dial whose own step is 1 but which can hold
  // decimals gets 0.1 as its finer choice and starts on whole numbers, so "±1" means the same on every dial: to the
  // next whole number. A dial that only holds whole numbers and steps by 1 has nothing to choose.
  const fine = step === 1 && !int ? 0.1 : step;
  const canToggle = !odd && fine !== 1;
  const canPlay = !!o.animate && (normal.max > normal.min || wide.max > wide.min);
  const bounce = o.animate === 'bounce';
  const period = (typeof o.animate === 'number' ? o.animate : 8) * 1000;
  const bare = o.slider === false;
""")

rep("""    `<label class="label" for="${id}${bare ? 'Num' : ''}">${label}</label><div class="dial-box">` +
""", """    `<label class="label" for="${id}${bare ? 'Num' : ''}">${label}</label><div class="dial-box">` +
    (canWiden ? `<span class="dial-wide" id="${id}Wide" hidden>wide</span>` : '') +
""")

rep("""  const mode = el.querySelector('.dial-mode'), playBtn = el.querySelector('.dial-play');
  const name = el.querySelector('label').textContent;
  const range = `${dialFmt(lo)} to ${dialFmt(hi)}`;
  n.inputMode = lo < 0 && DIAL_NO_MINUS_KEY ? 'text' : 'decimal';
  n.setAttribute('aria-label', `${name}, typed value`);
  n.setAttribute('aria-valuemin', lo); n.setAttribute('aria-valuemax', hi);
  n.title = odd ? `Odd whole numbers from ${range}` : int ? `Whole numbers from ${range}` : `From ${range}`;
  up.setAttribute('aria-label', `Increase ${name}`); down.setAttribute('aria-label', `Decrease ${name}`);
""", """  const mode = el.querySelector('.dial-mode'), playBtn = el.querySelector('.dial-play'), wideTag = el.querySelector('.dial-wide');
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
""")

rep("""  if (r && isFinite(def) && def >= min && def <= max && span > 0) r.style.setProperty('--dial-d', (def - min) / span);

  const cur = () => { const v = Number(get()); return isFinite(v) ? v : NaN; };
  let shown = '';      // the text last written into the box; anything else in there is an unfinished edit
  let whole = false;   // step buttons and arrow keys: false = the dial's own step, true = whole numbers
  let flagTimer = 0;
""", """  paintRange();

  const cur = () => { const v = Number(get()); return isFinite(v) ? v : NaN; };
  let shown = '';      // the text last written into the box; anything else in there is an unfinished edit
  let whole = canToggle && step === 1;   // step buttons and arrow keys: false = the fine step, true = whole numbers
  let flagTimer = 0;
""")

rep("""  const show = (force, fromSlider) => {
    const v = cur(), ok = !isNaN(v);
""", """  const show = (force, fromSlider) => {
    if (canWiden && isWide !== isExtreme()) retune();   // the switch was changed in the state itself
    const v = cur(), ok = !isNaN(v);
""")

# ---- sweep: there and back, and what stops it
rep("""  let playing = false, pos = 0, sent = NaN;
  const sweepFrame = dt => {
    if (!dialVisible(el)) { sweep(false); return; }
    const now = cur();
    if (now !== sent && !isNaN(now)) pos = clamp(now, min, max);   // something else moved the value: carry on from there
    pos += span * dt / period;
    if (pos > max) pos = min + (pos - max) % span;
    // one decimal finer than the slider's step: smooth to the eye, short in the box
    const v = fix(+pos.toFixed(Math.min(10, dialDecimals(step) + 1)));
""", """  // `ph` is how far along the slider the sweep is. A there-and-back sweep carries on past `span` on its way down,
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
""")

rep("""    if (on) { const v = cur(); pos = v >= min && v <= max ? v : min; sent = v; }
    dialSweep(sweepFrame, on);
    playBtn.setAttribute('aria-pressed', on);
    playBtn.title = on ? 'Pause the sweep' : 'Sweep this value across the slider, over and over';
    el.classList.toggle('is-playing', on);
  };
""", """    if (on) { const v = cur(); seat(v >= min && v <= max ? v : min, ph > span); sent = v; }
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
""")

rep("""    if (whole) return fix((dir > 0 ? Math.floor(b) + 1 : Math.ceil(b) - 1) + dir * (times - 1));
    return fix(+(from + dir * times * step).toFixed(Math.min(10, Math.max(dialDecimals(from), dialDecimals(step)))));
""", """    if (whole) return fix((dir > 0 ? Math.floor(b) + 1 : Math.ceil(b) - 1) + dir * (times - 1));
    return fix(+(from + dir * times * fine).toFixed(Math.min(10, Math.max(dialDecimals(from), dialDecimals(fine)))));
""")

rep("""    const s = dialFmt(whole ? 1 : step), fine = dialFmt(step);
    if (mode) {
      mode.textContent = '±' + s;
      mode.setAttribute('aria-pressed', whole);
      mode.setAttribute('aria-label', `${name}: step by whole numbers`);
      mode.title = whole ? `The arrows move to the next whole number. Press for steps of ${fine}.` : `The arrows change the value by ${fine}. Press for whole-number steps.`;
    }
    const by = odd ? 'to the next odd number' : whole ? 'to the next whole number' : `by ${fine}`;
""", """    const s = dialFmt(whole ? 1 : fine), small = dialFmt(fine);
    if (mode) {
      mode.textContent = '±' + s;
      mode.setAttribute('aria-pressed', whole);
      mode.setAttribute('aria-label', `${name}: step by whole numbers`);
      mode.title = whole ? `The arrows move to the next whole number. Press for steps of ${small}.` : `The arrows change the value by ${small}. Press for whole-number steps.`;
    }
    const by = odd ? 'to the next odd number' : whole ? 'to the next whole number' : `by ${small}`;
""")

rep("""  if (playBtn) {
    playBtn.setAttribute('aria-label', `Sweep ${name}`);
    playBtn.title = 'Sweep this value across the slider, over and over';
""", """  if (playBtn) {
    playBtn.setAttribute('aria-label', `Sweep ${name}`);
    playBtn.title = sweepTitle;
""")

rep("""  // ----- sweep (the play button)
""", """  // ----- sweep (the play button)
  const sweepTitle = bounce ? 'Sweep this value across the slider and back, over and over' : 'Sweep this value across the slider, over and over';
""")

rep("""    reset: () => { sweep(false); unflag(); set(def); show(true); },
    play: on => sweep(on === undefined ? !playing : !!on),
""", """    reset: () => { sweep(false); ph = 0; unflag(); set(def); show(true); },
    play: on => sweep(on === undefined ? !playing : !!on),
    // setExtreme calls this. `pull`: a value beyond the typed limits now in use goes back to the nearest one.
    rerange: pull => {
      retune();
      const v = cur();
      if (pull && !isNaN(v) && (v < lo || v > hi)) set(fix(v));
      show();
    },
""")

rep("""//   { type: 'dial',   key, label, min, max, step, def, lo, hi, int, odd, animate, help, when }
//   { type: 'select',""", """//   { type: 'dial',   key, label, min, max, step, def, lo, hi, xmin, xmax, xlo, xhi, int, odd, animate, help, when }
//   { type: 'select',""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', n0, '->', len(s))
