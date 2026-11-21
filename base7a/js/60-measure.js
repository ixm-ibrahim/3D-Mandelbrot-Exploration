// ---------- measuring an approach's power rule against the flat case
// The parameters are copied, so a measurement that runs over several frames keeps the values it started with.
const powerF = () => { const a = ap(), q = { ...apP() }, n = cardPower(); return v => MATH[a.id](v, n, q); };
// The power the scorecard and the two step figures describe. The equation may take another power of z than
// the dial shows: 'z^-n + c' takes -n, 'z^3 - z + c' takes 3 whatever n is. When it takes several, the first
// one written is described. A formula with no power in it (c*z*(1 - z)) leaves the dial's n.
const cardPow = { key: null, n: 2, several: false };
function cardPower() {
  const key = S.eq + '\n' + S.n;
  if (cardPow.key !== key) {
    const all = formulaPowers(S.eq, S.n).filter(x => Math.abs(x) <= 64);
    cardPow.key = key; cardPow.n = all.length ? all[0] : S.n; cardPow.several = all.some(x => Math.abs(x - all[0]) > 1e-9);
  }
  return cardPow.n;
}
function fib(i, N) {
  const z = 1 - (2 * i + 1) / N, r = Math.sqrt(Math.max(0, 1 - z * z)), a = i * PI * (3 - Math.sqrt(5));
  return [r * Math.cos(a), r * Math.sin(a), z];
}
function tangent(d) {
  const e1 = norm(cross(d, Math.abs(d[0]) < 0.8 ? [1, 0, 0] : [0, 1, 0]));
  return [e1, cross(d, e1)];
}
function symEig3(a11, a12, a13, a22, a23, a33) { // eigenvalues of a symmetric 3x3, largest first
  const p1 = a12 * a12 + a13 * a13 + a23 * a23, q = (a11 + a22 + a33) / 3;
  const p2 = (a11 - q) ** 2 + (a22 - q) ** 2 + (a33 - q) ** 2 + 2 * p1, p = Math.sqrt(p2 / 6);
  if (p < 1e-14) return [q, q, q];
  const b11 = (a11 - q) / p, b22 = (a22 - q) / p, b33 = (a33 - q) / p, b12 = a12 / p, b13 = a13 / p, b23 = a23 / p;
  const det = b11 * (b22 * b33 - b23 * b23) - b12 * (b12 * b33 - b23 * b13) + b13 * (b12 * b23 - b22 * b13);
  const phi = Math.acos(clamp(det / 2, -1, 1)) / 3;
  const e1 = q + 2 * p * Math.cos(phi), e3 = q + 2 * p * Math.cos(phi + 2 * PI / 3);
  return [e1, 3 * q - e1 - e3, e3];
}

// The measurement is a running total over MEASURE_N directions. measure() adds them all at once; the
// scorecard adds a few milliseconds' worth per frame. Both go through the same three functions, so
// they give the same numbers.
const MEASURE_N = 6000;
const MEASURE_AXES = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
function measureBegin(F, n) {
  return { F, g: v => norm(F(v)), n, i: 0, tear: 400 * Math.max(1, Math.abs(n)),
    lmin: Infinity, lmax: 0, smin: Infinity, smax: 0, top: new Array(8).fill(0), low: new Array(8).fill(Infinity), round: 0, rev: 0, deg: 0, sheets: 0, used: 0 };
}
// Slope of f at d along e, by central differences at two step sizes. If they disagree the sample
// straddles a jump and the answer is null. The test is written so that NaN and infinity also give null.
function measureSlope(f, d, e, h) {
  const a = scl(sub(f(add(d, scl(e, h))), f(sub(d, scl(e, h)))), 0.5 / h), h8 = h / 8;
  const b = scl(sub(f(add(d, scl(e, h8))), f(sub(d, scl(e, h8)))), 0.5 / h8);
  return len(sub(a, b)) <= 0.25 * (len(b) + 0.05) ? a : null;
}
function measureSample(st) {
  const { F, g, tear } = st, h = 1e-4, d = fib(st.i++, MEASURE_N), Fd = F(d), L = len(Fd);
  if (L === L) { st.lmin = Math.min(st.lmin, L); st.lmax = Math.max(st.lmax, L); }
  const J0 = measureSlope(F, d, MEASURE_AXES[0], h), J1 = J0 && measureSlope(F, d, MEASURE_AXES[1], h), J2 = J1 && measureSlope(F, d, MEASURE_AXES[2], h);
  if (!J2 || len(J0) > tear || len(J1) > tear || len(J2) > tear) return;
  const [e1, e2] = tangent(d), g1 = measureSlope(g, d, e1, h), g2 = g1 && measureSlope(g, d, e2, h);
  if (!g2) return;
  // Signed area scale of the map on directions: negative where a direction lands mirror-reversed on the sphere.
  // The step figure dashes the same thing. (The whole of space keeps or loses its handedness as sign(n)·w does.)
  const w = dot(norm(Fd), cross(g1, g2));
  if (w !== w) return;
  st.used++;
  if (w < 0) st.rev++;
  const ev = symEig3(dot(J0, J0), dot(J0, J1), dot(J0, J2), dot(J1, J1), dot(J1, J2), dot(J2, J2));
  const s1 = Math.sqrt(Math.max(ev[0], 0)), s3 = Math.sqrt(Math.max(ev[2], 0));
  st.smin = Math.min(st.smin, s3); st.smax = Math.max(st.smax, s1);
  // The eight largest and the eight smallest stretches. One sample can be an accident (a spike beside a bad
  // direction, a difference taken across a crease); the eighth of 6,000 says whether the extreme is typical.
  const top = st.top, low = st.low;
  if (s1 > top[7]) { let j = 7; while (j > 0 && top[j - 1] < s1) { top[j] = top[j - 1]; j--; } top[j] = s1; }
  if (s3 < low[7]) { let j = 7; while (j > 0 && low[j - 1] > s3) { low[j] = low[j - 1]; j--; } low[j] = s3; }
  st.round += s1 > 0 ? s3 / s1 : 0;
  st.deg += w; st.sheets += Math.abs(w);
}
// Add samples for about `ms` milliseconds. `most` also caps the count, for browsers whose clock is too coarse to trust.
function measureRun(st, ms, most) {
  const t0 = performance.now(), stop = Math.min(MEASURE_N, st.i + most);
  while (st.i < stop) { measureSample(st); if ((st.i & 7) === 0 && performance.now() - t0 >= ms) break; }
}
function measureEnd(st) {
  const { F, n } = st, u = Math.max(st.used, 1);
  // Does the plane z = 0 follow complex z^n? Failing that, does it land on itself as k·z^n for one fixed
  // complex k (what a turn offset gives: a turned copy of the flat case)?
  let planeErr = 0, copyErr = 0, k = null;
  for (let i = 0; i < 48; i++) {
    const a = 0.37 + i * 2.39996, r = 0.25 + 1.2 * ((i * 0.618034) % 1), x = r * Math.cos(a), y = r * Math.sin(a);
    const out = F([x, y, 0]), R = Math.pow(r, n), th = Math.atan2(y, x) * n, zx = R * Math.cos(th), zy = R * Math.sin(th);
    planeErr = Math.max(planeErr, len(sub(out, [zx, zy, 0])) / (1 + R));
    if (!k) k = [(out[0] * zx + out[1] * zy) / (R * R), (out[1] * zx - out[0] * zy) / (R * R)];
    copyErr = Math.max(copyErr, len(sub(out, [k[0] * zx - k[1] * zy, k[0] * zy + k[1] * zx, 0])) / (1 + R));
  }
  const plane = planeErr < 1e-9, scale = Math.hypot(k[0], k[1]), copy = !plane && copyErr < 1e-9 && scale > 1e-6;
  const turn = copy ? Math.atan2(k[1], k[0]) * 180 / PI : 0;   // degrees, from −180 (not included) to 180
  return { lmin: st.lmin, lmax: st.lmax, smin: st.smin, smax: st.smax, smin8: st.low[7], smax8: st.top[7], round: st.round / u, rev: st.rev / u, deg: st.deg / u, sheets: st.sheets / u,
    used: st.used, plane, copy, turn: turn < -180 + 1e-9 ? 180 : turn, scale: copy ? scale : 1 };
}
function measure(F, n) {
  const st = measureBegin(F, n);
  while (st.i < MEASURE_N) measureSample(st);
  return measureEnd(st);
}

// ---------- the scorecard
const fmtN = n => (Math.abs(n - Math.round(n)) < 1e-9 ? String(Math.round(n)) : String(+n.toFixed(2)));
const tidy = x => { const r = Math.round(x); return Math.abs(x - r) < 0.07 ? String(r) : x.toFixed(1); };
const cardMinus = s => String(s).replace('-', '−');              // a proper minus sign for running text
const cardTimes = t => (t === '1' ? 'once' : t + ' times');
const cardWhole = n => Math.abs(n - Math.round(n)) < 1e-9;
const PROPS = [['len', 'Length goes to its nth power'], ['round', 'Keeps shapes'], ['wrap', 'Wraps without folding'], ['crush', 'Crushes only the origin'], ['smooth', 'One smooth formula'], ['slice', 'Contains the flat set']];
const PILL = { ok: 'holds', part: 'partly', no: 'fails' };
const CARD_MEASURED = ['len', 'round', 'wrap', 'slice'];           // rows whose "in space" cell waits for the measurement
const CARD_SLICE_MS = 4, CARD_SLICE_MOST = 500, CARD_QUIET = 150;  // work per frame; its cap in samples; pause that ends a stream of calls
// cancel: stops the measurement that is waiting or running (null when there is none). last: when updateCard was
// last called. shown: id of the approach whose measured cells are on show. result: the last measurement shown.
// cache: finished measurements, by approach, n and parameters. slices, longest: how the last measurement was
// spread over frames (count, and the longest single piece in ms), kept for the timing test.
// pow: the power the card last described (see cardPower).
const cardRun = { cancel: null, last: -1e9, shown: null, result: null, cache: new Map(), slices: 0, longest: 0, pow: null };

function buildCard() {
  $('card').innerHTML = '<p class="note" id="cardPowNote" hidden></p><div class="row head label"><div>Property</div><div>In the plane</div><div id="ruleHead">In space</div></div>' +
    PROPS.map(([id, title]) => `<div class="row"><div class="prop">${title}</div>` +
      `<div class="cell"><span class="k label">In the plane</span><span id="p-${id}"></span></div>` +
      `<div class="cell"><span class="k label k3">In space</span><span class="pill" id="b-${id}" style="display:none"></span><span id="s-${id}"></span></div></div>`).join('');
  cardRun.shown = null;
  if (!hooks.view.includes(drawStep3d)) hooks.view.push(drawStep3d);
}
function cardSet(id, text) { const el = $(id); if (el && el.textContent !== text) el.textContent = text; }
function setCell(id, st, text) {
  const b = $('b-' + id), s = $('s-' + id);
  b.className = 'pill ' + st; b.textContent = PILL[st];
  b.style.display = ''; b.style.opacity = s.style.opacity = '';
  cardSet('s-' + id, text);
}

// The "in the plane" column: what complex z^n does, for any real n.
function cardPlane(n) {
  const k = Math.abs(n), A = fmtN(k), whole = cardWhole(n);
  if (A === '0') return {
    len: 'z⁰ = 1 whatever z is, so every length becomes 1.',
    round: 'Nothing to keep: every circle lands on the single point 1.',
    wrap: 'Every direction is sent to the same one.',
    crush: 'Everything is crushed onto the single point 1.',
    smooth: 'A constant.',
    slice: 'It is the flat set.',
  };
  const wrap = whole
    ? `Wraps the circle of directions ${cardTimes(A)}` + (n < 0 ? ', running the other way round all along. It never doubles back.' : ' and never reverses it.')
    : (k > 1 ? `Winds the circle of directions ${A} times round` : `Covers only ${Math.round(k * 100)}% of the circle of directions`) + (n < 0 ? ', running the other way' : '') +
      '. The two ends do not meet, which leaves a tear along the negative x-axis.';
  const crush = n > 1 ? 'Only the origin is crushed. That is why following the single point 0 is enough to decide whether c is in the set.'
    : A === '1' && n > 0 ? 'Nothing is crushed. With n = 1 the power leaves every point where it is.'
    : n > 0 ? 'Nothing is crushed. At the origin the stretch grows without limit, and far away it fades to nothing.'
    : 'No point is crushed. The origin is thrown out to infinity, and far-away points are packed in around the origin.';
  const smooth = !whole ? 'A power that is not a whole number has to measure the angle of z. The angle jumps across the negative x-axis, so the result is torn along that line.'
    : n > 0 ? (A === '1' ? 'A polynomial, the simplest one: (x, y).' : A === '2' ? 'A polynomial: (x² − y², 2xy).' : A === '3' ? 'A polynomial: (x³ − 3xy², 3x²y − y³).' : `A polynomial of degree ${A} in x and y.`)
    : (A === '1' ? 'One formula, (x, −y)/(x² + y²), smooth everywhere except the origin.' : `One divided by a polynomial of degree ${A}, smooth everywhere except the origin.`);
  return {
    len: n > 0 ? '|zⁿ| = |z|ⁿ for every z.' : '|zⁿ| = |z|ⁿ for every z except 0. A negative n turns the plane inside out: points near the origin land far away, and far points land near it.',
    round: 'Roundness 100%. A tiny circle lands as a circle' + (A === '1' ? ' of the same size at |z| = 1.' : k > 1 ? `, stretched ${A}× in every direction at |z| = 1.` : `, shrunk to ${A}× its size in every direction at |z| = 1.`),
    wrap, crush, smooth,
    slice: 'It is the flat set.',
  };
}

// The measured cells of the "in space" column, each as [state, text].
function cardSpace(a, q, n, m) {
  const k = Math.abs(n), A = fmtN(k);
  if (!m.used) {
    const t = 'Could not be measured: the rule gives no steady result around any sampled direction.';
    return { len: ['no', t], round: ['no', t], wrap: ['no', t], slice: ['no', t] };
  }
  const two = x => String(+x.toFixed(2)), dec = x => String(+x.toFixed(x < 0.95 ? 2 : 1));

  const lenOk = Math.abs(m.lmin - 1) < 1e-6 && Math.abs(m.lmax - 1) < 1e-6;
  const lenText = lenOk ? (A === '0' ? '|v⁰| = 1 for every v.' : `|vⁿ| = |v|ⁿ for every v${n < 0 ? ' except the origin' : ''}.`)
    : !(m.lmax < 1000) ? `For |v| = 1 the result can have any length from ${two(m.lmin)} upward, with no upper limit.`
    : two(m.lmin) === two(m.lmax) ? `For |v| = 1 the result always has length ${two(m.lmax)}.`
    : `For |v| = 1 the result has length anywhere from ${two(m.lmin)} to ${two(m.lmax)}.`;

  // The approach's note explains its squash. When the row holds, a note the approach also gives at an ordinary
  // power (where no rule keeps shapes) is about failing the row, so it is left out.
  const roundOk = m.round > 0.999, noteAt = x => (typeof a.roundNote === 'function' ? a.roundNote(q, x) : a.roundNote) || '';
  const note = roundOk && [2, 2.5, 3].some(x => noteAt(x) === noteAt(n)) ? '' : noteAt(n);
  let roundText = 'Nothing to keep: every direction lands on the same point.';
  if (m.smax >= 1e-6) {
    // No upper limit: the largest stretch stands far above the eighth largest (a spike that more samples would
    // push higher), or it is beyond anything a bounded rule reaches (those stay under about n², see the classic
    // Mandelbulb beside its axis). At the lower end a smallest value that stands apart from the eighth smallest
    // is a difference taken across a crease, and the eighth is shown instead.
    const lo = m.smin < 0.03 * k ? '0' : dec(m.smin8 > 1.05 * m.smin ? m.smin8 : m.smin), hi = dec(m.smax);
    const noTop = m.smax8 < 0.8 * m.smax || m.smax > 30 * Math.max(k, 1);
    roundText = `Roundness ${roundOk ? 100 : Math.min(99, Math.round(m.round * 100))}%. At |v| = 1 the stretch ` +
      (!noTop && lo === hi ? `is ${hi}× in every direction` + (hi === A ? ', as in the plane.' : `, where the plane gives ${A}×.`)
        : `runs from ${lo}× to ${noTop ? 'no upper limit' : hi + '×'}, where the plane gives ${A}× throughout.`) + (note ? ' ' + note : '');
  }

  const oneWay = m.rev < 0.005 || m.rev > 0.995, clean = oneWay && Math.abs(Math.abs(m.deg) - m.sheets) < 0.05, part = Math.round(m.sheets * 100);
  const wrap = m.sheets < 0.005 ? ['no', 'Every direction lands in the same place, so the sphere of directions is not wrapped at all.']
    : clean ? ['ok', (m.sheets < 0.95 ? `Covers only ${part}% of the sphere of directions` : `Wraps the sphere of directions ${cardTimes(tidy(m.sheets))}`) +
        (m.rev > 0.5 ? ', as a mirror image everywhere, and never folds it.' : ' and never reverses it.')]
    : ['no', (m.sheets < 0.95 ? `Covers about ${part}% of the sphere of directions` : `Covers the sphere of directions ${cardTimes(tidy(m.sheets))} over`) +
        `, but ${Math.round(m.rev * 100)}% of directions land mirror-reversed. Counted with sign, the net wrap is ${cardMinus(tidy(Math.abs(m.deg) < 0.05 ? 0 : m.deg))}.`];

  // The approach words this row, told whether the plane z = 0 follows z^n exactly. The pill is the measurement:
  // "partly" when that plane lands on itself as a turned copy of z^n (a turn offset does this).
  return { len: [lenOk ? 'ok' : 'no', lenText], round: [roundOk ? 'ok' : 'no', roundText], wrap, slice: [m.plane ? 'ok' : m.copy ? 'part' : 'no', a.slice(m.plane, q, n)] };
}

// The next animation frame, or a timer when the page is in the background and frames are paused. Returns a function that cancels it.
function cardFrame(fn) {
  let raf = 0, tmr = 0;
  const run = () => { cancelAnimationFrame(raf); clearTimeout(tmr); fn(); };
  raf = requestAnimationFrame(run); tmr = setTimeout(run, 200);
  return () => { cancelAnimationFrame(raf); clearTimeout(tmr); };
}
function cardStop() {
  if (!cardRun.cancel) return;
  cardRun.cancel(); cardRun.cancel = null;
  setBusy('measure', null);
}
const cardIdle = () => !cardRun.cancel;   // true when no measurement is waiting or running
function cardShow(a, q, n, m) {
  const cells = cardSpace(a, q, n, m);
  for (const id of CARD_MEASURED) setCell(id, ...cells[id]);
  $('card').removeAttribute('aria-busy');
  cardRun.shown = a.id; cardRun.result = m;
}
// Fill the card for the current approach, parameters and n. Returns at once: the cells that need no measuring
// are written straight away, the measured ones a few frames later. Calling it again cancels a measurement
// still under way, and it may be called as often as every frame (it then waits for a pause before measuring).
function updateCard() {
  const a = ap(), q = { ...apP() }, n = cardPower(), now = performance.now();
  cardStop();
  cardRun.pow = n;
  // say so when the power described is not the one on the dial
  const note = $('cardPowNote'), other = Math.abs(n - S.n) > 1e-9;
  if (note) {
    note.hidden = !other;
    cardSet('cardPowNote', other ? `The equation takes z to the power ${cardMinus(fmtN(n))}${cardPow.several ? ' first' : ''}, so that is the power described here and in the two figures above. The dial shows n = ${cardMinus(fmtN(S.n))}.` : '');
  }
  cardSet('ruleHead', a.name);
  document.querySelectorAll('.k3').forEach(el => { el.textContent = a.name; });
  const plane = cardPlane(n);
  for (const [id] of PROPS) cardSet('p-' + id, plane[id]);
  setCell('crush', ...a.crush(q, n));
  setCell('smooth', ...a.smooth(q, n));

  const key = a.id + ' ' + n + ' ' + JSON.stringify(q), known = cardRun.cache.get(key), stream = now - cardRun.last < CARD_QUIET;
  cardRun.last = now;
  if (known) { cardShow(a, q, n, known); return; }
  // Until the new numbers arrive, the old ones stay up dimmed, unless they belong to another approach.
  $('card').setAttribute('aria-busy', 'true');
  for (const id of CARD_MEASURED) {
    const b = $('b-' + id), s = $('s-' + id);
    if (cardRun.shown !== a.id) { b.style.display = 'none'; s.textContent = 'Measuring…'; }
    b.style.opacity = s.style.opacity = '0.45';
  }
  cardRun.shown = a.id;

  const st = measureBegin(v => MATH[a.id](v, n, q), n);
  cardRun.slices = 0; cardRun.longest = 0;
  const piece = () => {
    const t0 = performance.now(), bg = document.hidden;   // nobody is watching a background page, so finish in one go there
    cardRun.cancel = null;
    try { measureRun(st, bg ? 1e9 : CARD_SLICE_MS, bg ? MEASURE_N : CARD_SLICE_MOST); }
    catch (err) { setBusy('measure', null); throw err; }
    if (st.i < MEASURE_N) {
      // the label goes up once a measurement has outlived its first frame, so a stream of calls does not make it flicker
      if (cardRun.slices === 1) setBusy('measure', 'Measuring the approach');
      cardRun.cancel = cardFrame(piece);
    } else {
      const m = measureEnd(st);
      cardRun.cache.set(key, m);
      if (cardRun.cache.size > 40) cardRun.cache.delete(cardRun.cache.keys().next().value);
      setBusy('measure', null);
      cardShow(a, q, n, m);
    }
    cardRun.slices++; cardRun.longest = Math.max(cardRun.longest, performance.now() - t0);
  };
  if (stream) { const t = setTimeout(piece, CARD_QUIET); cardRun.cancel = () => clearTimeout(t); }
  else cardRun.cancel = cardFrame(piece);
}

// ---------- the step figures
function prep(cv) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  return { ctx, w, h };
}
const hueCol = hue => `hsl(${hue.toFixed(0)} 62% ${theme.dark ? 64 : 40}%)`;
function arrow(ctx, w, h) {
  ctx.strokeStyle = theme.ink2; ctx.globalAlpha = 1; ctx.lineWidth = 1.25; ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(w / 2 - 9, h / 2); ctx.lineTo(w / 2 + 9, h / 2);
  ctx.moveTo(w / 2 + 4, h / 2 - 4); ctx.lineTo(w / 2 + 9, h / 2); ctx.lineTo(w / 2 + 4, h / 2 + 4); ctx.stroke();
}
// Radius of the sample circles. For |n| > 1 it shrinks so the pushed-through circles stay apart; for |n| < 1
// it grows (up to `most`) so that what is left of them after the step can still be seen.
function stepRadius(n, usual, room, most) {
  const k = Math.abs(n);
  return k >= 1 ? Math.min(usual, room / k) : Math.min(most, usual / Math.sqrt(Math.max(k, 1e-6)));
}
const stepSize = n => (fmtN(Math.abs(n)) === '1' ? 'of the same size' : fmtN(Math.abs(n)) + ' times the size');
function stepCaption2d(n) {
  const N = cardMinus(fmtN(n));
  if (N === '0') return 'The plane. With n = 0 every point is sent to 1, so all the circles shrink onto that one point.';
  return `The plane. Angles are multiplied by ${N}, so every circle lands as a circle ${stepSize(n)}` + (n < 0 ? ', and the ring of circles runs the other way round' : '') +
    '. Nothing is squashed or flipped.' + (cardWhole(n) ? '' : ` Because ${N} is not a whole number, the angle jumps across the negative x-axis, and the circle sitting on that line is torn in two.`);
}
function stepCaption3d(a, n, anyFlipped) {
  return `${a.name}. ` + (fmtN(n) === '0' ? 'With n = 0 every direction is sent to the same place, so the circles shrink onto one point.' : `A shape-keeping rule would turn each circle into a circle ${stepSize(n)}.`) +
    (anyFlipped ? ' Dashed outlines have landed mirror-reversed, and the brass stubs mark the axis this approach singles out.' : ' The brass stubs mark the axis this approach singles out.') + ' Drag to turn.';
}
// A circle that the step has shrunk to a point (all its screen points within a pixel) is drawn as a dot,
// so that it does not simply vanish from the "after" picture.
function stepDot(ctx, pts, color) {
  if (!pts.length) return false;
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  if (Math.max(...xs) - Math.min(...xs) >= 1 || Math.max(...ys) - Math.min(...ys) >= 1) return false;
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.arc(pts[0][0], pts[0][1], 2.5, 0, 2 * PI); ctx.fill();
  return true;
}
function drawStep2d() {
  const { ctx, w, h } = prep($('step2d')), n = cardPower(), whole = cardWhole(n), K = 7, rho = stepRadius(n, 0.16, 0.34, 0.3), M = 48;
  const R = Math.min(w / 4, h / 2) / 1.5, cy = h / 2;
  [w * 0.25, w * 0.75].forEach((cx, side) => {
    ctx.setLineDash([]); ctx.globalAlpha = 1; ctx.lineWidth = 1; ctx.strokeStyle = theme.line;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.moveTo(cx, cy); ctx.lineTo(cx + R, cy); ctx.stroke();
    ctx.lineWidth = 1.6;
    for (let k = 0; k < K; k++) {
      const th = 0.45 + 2 * PI * k / K, pts = [], color = hueCol(th * 180 / PI);
      let re0 = 0, im0 = 0;
      for (let j = 0; j <= M; j++) {
        const t = 2 * PI * j / M, re = Math.cos(th) + rho * Math.cos(t), im = Math.sin(th) + rho * Math.sin(t);
        let X = re, Y = im, lift = j === 0;
        if (side === 1) { // z^n as the shader computes it: the angle is taken between −180° and 180°
          const r = Math.pow(Math.hypot(re, im), n), a = Math.atan2(im, re) * n;
          X = r * Math.cos(a); Y = r * Math.sin(a);
          // unless n is a whole number the result jumps where the angle does: do not draw across that tear
          if (!whole && re < 0 && re0 < 0 && (im < 0) !== (im0 < 0)) lift = true;
        }
        pts.push([cx + R * X, cy - R * Y, lift]);
        re0 = re; im0 = im;
      }
      if (stepDot(ctx, pts, color)) continue;
      ctx.strokeStyle = color;
      ctx.beginPath();
      for (const [x, y, lift] of pts) { if (lift) ctx.moveTo(x, y); else ctx.lineTo(x, y); }
      ctx.stroke();
    }
  });
  arrow(ctx, w, h);
  cardSet('cap2d', stepCaption2d(n));
}
let stepCurves = [], stepBuilt = 0, stepDrawn = '';
function ringAround(c, ang, M) {
  const [e1, e2] = tangent(c), pts = [];
  for (let j = 0; j <= M; j++) {
    const t = 2 * PI * j / M;
    pts.push(norm(add(scl(c, Math.cos(ang)), scl(add(scl(e1, Math.cos(t)), scl(e2, Math.sin(t))), Math.sin(ang)))));
  }
  return pts;
}
function buildStep3d() {
  // the direction a direction is sent to, or null where the rule gives nothing usable (a point crushed to the origin or thrown to infinity)
  const P = powerF(), F = v => { const p = P(v), l = len(p); return l > 0 && l < Infinity ? scl(p, 1 / l) : null; };
  const N = 34, n = cardPower(), rho = stepRadius(n, 0.11, 0.24, 0.2), h = 1e-4;
  stepCurves = []; stepBuilt++;
  for (let i = 0; i < N; i++) {
    const c = fib(i, N), [e1, e2] = tangent(c), before = ringAround(c, rho, 44);
    const Fc = F(c), a1 = F(add(c, scl(e1, h))), b1 = F(sub(c, scl(e1, h))), a2 = F(add(c, scl(e2, h))), b2 = F(sub(c, scl(e2, h)));
    const flipped = !!(Fc && a1 && b1 && a2 && b2) && dot(Fc, cross(sub(a1, b1), sub(a2, b2))) < 0;
    stepCurves.push({ hue: (Math.atan2(c[1], c[0]) * 180 / PI + 360) % 360, before, after: before.map(F), flipped });
  }
  cardSet('cap3d', stepCaption3d(ap(), n, stepCurves.some(cv => cv.flipped)));
}
function drawStep3d() {
  // A new equation reaches this module only through this hook: the page redraws the picture without calling
  // refresh(). When the equation now takes another power, the figures and the card follow it.
  if (cardRun.pow !== null && cardRun.pow !== cardPower()) { buildStep3d(); drawStep2d(); updateCard(); }
  const el = $('step3d'), b = basis(), axis = ap().axis(apP());
  // Called whenever anything on the stage changes. Skip the work unless something this figure shows has changed.
  const sig = [stepBuilt, el.clientWidth, el.clientHeight, window.devicePixelRatio, theme.line, theme.ink2, theme.brass, theme.dark, axis, b.right, b.up].join();
  if (sig === stepDrawn) return;
  stepDrawn = sig;
  const { ctx, w, h } = prep(el);
  const R = Math.min(w / 4, h / 2) / 1.2, cy = h / 2;
  const P = (cx, p) => [cx + R * dot(p, b.right), cy - R * dot(p, b.up), -dot(p, b.f)];
  const poly = (cx, pts, color, width, dash) => {
    const scr = pts.map(p => p && P(cx, p)), real = scr.filter(Boolean);
    ctx.globalAlpha = real.length && real[0][2] < 0 ? 0.2 : 1;
    if (stepDot(ctx, real, color)) return;
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.setLineDash(dash || []);
    for (const front of [false, true]) {
      ctx.globalAlpha = front ? 1 : 0.2;
      ctx.beginPath();
      for (let j = 0; j + 1 < pts.length; j++) {
        if (!pts[j] || !pts[j + 1] || len(sub(pts[j], pts[j + 1])) > 0.8) continue; // do not draw across a tear or a missing point
        const a = scr[j], c = scr[j + 1];
        if ((a[2] + c[2] >= 0) !== front) continue;
        ctx.moveTo(a[0], a[1]); ctx.lineTo(c[0], c[1]);
      }
      ctx.stroke();
    }
  };
  const great = k => { const pts = []; for (let j = 0; j <= 64; j++) { const t = 2 * PI * j / 64, p = [0, 0, 0]; p[k] = Math.cos(t); p[(k + 1) % 3] = Math.sin(t); pts.push(p); } return pts; };
  [w * 0.25, w * 0.75].forEach((cx, side) => {
    ctx.globalAlpha = 1; ctx.setLineDash([]); ctx.lineWidth = 1; ctx.strokeStyle = theme.line;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.stroke();
    for (let k = 0; k < 3; k++) poly(cx, great(k), theme.line, 1);
    for (const s of [1, -1]) { // the axis this approach singles out
      const a = P(cx, scl(axis, s)), c = P(cx, scl(axis, s * 1.16));
      ctx.globalAlpha = a[2] >= 0 ? 1 : 0.35; ctx.strokeStyle = theme.brass; ctx.lineWidth = 2; ctx.setLineDash([]);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(c[0], c[1]); ctx.stroke();
    }
    for (const cv of stepCurves) poly(cx, side ? cv.after : cv.before, hueCol(cv.hue), 1.6, side && cv.flipped ? [4, 3] : null);
  });
  arrow(ctx, w, h);
}
