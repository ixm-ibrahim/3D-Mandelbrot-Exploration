// The custom approach on the page. Under the picture stand the bar that plays the steps (#cuBar) and the steps
// themselves with their tools (#cuDock); the approach's panel in the controls column holds the help and the rule
// as text. The rule itself is in 12-custom.js; this file only changes S.custom and shows it.
const CUI = {
  undo: [],              // earlier rules, as text, newest last
  hot: false,            // a slider or a number box of a step is being moved (one undo entry for the whole move)
  before: 0,             // the approach that was chosen before the custom one (the button goes back to it)
  formula: new Set(),    // 'step id:key' of the settings whose menu stands on "a formula"
  playing: false, raf: 0, last: 0,
  until: null,           // a play of one step alone stops here (how far through the iteration's steps); null: at the iteration's end
  barSig: '', now: null, // what the bar last showed; the id of the step it marked
  wasOn: false,          // the custom approach was on show when customSync last looked
  saved: [],             // the rules the user has saved: [{ name, rule }], rule as cuRuleText writes it
};
// Saved rules are kept in localStorage; where that is blocked every access throws, and the list stays empty.
const CU_SAVED_KEY = 'squaringLab.customSaved';
function cuSavedLoad() {
  try {
    const list = JSON.parse(localStorage.getItem(CU_SAVED_KEY) || '[]');
    CUI.saved = (Array.isArray(list) ? list : []).filter(x => x && typeof x.name === 'string' && cuRuleOf(x.rule)).slice(0, 60).map(x => ({ name: x.name.slice(0, 40), rule: x.rule }));
  } catch (err) { CUI.saved = []; }
}
function cuSavedStore() {
  try { localStorage.setItem(CU_SAVED_KEY, JSON.stringify(CUI.saved)); return true; } catch (err) { return false; }
}
// The menu of rules to load: the user's saved ones (values s0, s1, ...) above the lab's own (0, 1, ...).
function cuStartMenu(value) {
  const sel = $('cuStart'), opt = (v, t) => `<option value="${v}">${cuEsc(t)}</option>`;
  const starts = lab => CU_STARTS.map((s, k) => (!!s.lab === lab ? opt(k, s.name) : '')).join('');
  sel.innerHTML = (CUI.saved.length ? `<optgroup label="Your saved rules">${CUI.saved.map((s, k) => opt('s' + k, s.name)).join('')}</optgroup>` : '')
    + `<optgroup label="The lab’s approaches, as steps">${starts(true)}</optgroup><optgroup label="Other rules to start from">${starts(false)}</optgroup>`;
  if (value !== undefined && [...sel.options].some(o => o.value === String(value))) sel.value = String(value);
  $('cuDelBtn').hidden = sel.value[0] !== 's';
}
const cuEsc = t => String(t).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const cuStepAt = id => S.custom.steps.findIndex(s => String(s.id) === String(id));
const cuShort = x => String(+(+x).toFixed(4));
const cuOn = () => ap().id === 'custom' && S.mode !== 'k';
const cuSpec = (st, key) => CU_BLOCKS[st.kind].params.find(x => x.key === key);
const CU_HELP = `<p class="note"><b>A point</b> is written <code>vec(x, y, z)</code>, as in <code>vec(0, 0, 1)</code> for one step straight up. Every box for a point takes that, a name such as <code>c</code> or <code>z</code>, or a formula.</p>
<p class="note"><b>A formula step</b> is one line, <code>name = formula</code>. The name <code>z</code> is the point: a line that starts <code>z =</code> moves it. Any other name is yours and can be used in every step after it.</p>
<p class="note"><b>Given:</b> <code>z</code> the point, <code>c</code>, <code>n</code> the Power dial, <code>pi</code>; the point as a length and two angles: <code>radius</code> (how far from the middle), <code>theta</code> (the angle round the upright axis) and <code>phi</code> (the angle of the height above the flat plane), so that <code>sph(radius, theta, phi)</code> is the point itself; and from the orbit <code>first</code> (its first point), <code>last</code> (the point of the iteration before), <code>point(2)</code> (its second point, and so on by number; <code>point(0)</code> is the point this iteration began with and <code>point(-1)</code> the one before), <code>mean</code> (the average of its points so far) and <code>count</code> (which iteration this is). <code>z</code> is always the point where it is now, after the steps before this one.</p>
<p class="note"><b>Before the orbit: change c</b> (a kind of step) changes c once, before anything else, as the lab’s folding rules do: <code>foldx(c, 2)</code>, <code>softmirror(c, angle, soft)</code>.</p>
<p class="note"><b><code>same(x)</code></b> is for the picture’s distance estimate, which follows a few orbits right beside each point: inside it they take the value the point itself has. Use it for a value that jumps from one point to its neighbour, such as a box’s middle.</p>
<p class="note"><b>A value the orbit keeps</b> (a kind of step) gives a name that does not start afresh: what it holds when an iteration ends is what it holds in the next. Any later step may give it a new value, as in <code>total = total + radius</code>.</p>
<p class="note"><b>Kinds:</b> a number, a point with the parts <code>.x .y .z</code>, a quaternion <code>quat(w, x, y, z)</code>, and a matrix <code>mat( )</code> of nine numbers row by row, or of three points as its columns.</p>
<p class="note"><b>Signs:</b> <code>+ − * / ^</code>, and <code>&lt; &gt; &lt;= &gt;= == !=</code>, which give 1 or 0. A number times a point stretches it, a matrix times a point moves it, and two quaternions multiply as quaternions.</p>
<p class="note"><b>Numbers:</b> <code>sin cos tan asin acos atan atan2(y, x) sinh cosh tanh atanh exp log sqrt abs floor ceil round fract sign min max mod pow clamp(x, lo, hi) mix(a, b, t) step smoothstep rad(degrees) deg(radians) if(test, a, b)</code>. Angles are in radians: write <code>rad(90)</code> for 90°.</p>
<p class="note"><b>Points:</b> <code>len dot cross unit dist abs each(a, b) flat(v) lon(v) lat(v) sph(length, lon, lat) rot(v, axis, angle) invert(v, centre, radius) mirror(v, normal) cpow(v, n) conj(v)</code>.</p>
<p class="note"><b>Quaternions and matrices:</b> <code>asquat(v)</code> reads a point as x + yi + zj and <code>aspoint(q)</code> reads it back; <code>quat(v) vec(q) re(q) conj(q) inv(q) q^n qrot(axis, angle) turn(v, q)</code>; <code>rotmat(axis, angle) transpose(m) det(m) inv(m)</code>.</p>`;

// The menu of a number or a point setting: where its value comes from. Returns { mode, html } for the value the
// step holds now: mode is the menu's choice ('#num' a number, '#xyz' three numbers, '#f' a formula, or the name
// or formula the choice stands for), html the menu's options.
function cuSource(st, sp) {
  const raw = String(st.p[sp.key] === undefined ? sp.def : st.p[sp.key]).trim(), scope = cuProgram().scopes[st.id] || [], flat = t => t.replace(/\s+/g, '');
  const mine = scope.filter(x => x[1] === (sp.type === 'vec' ? 'v' : 's')).map(x => x[0]);
  let opts, mode;
  if (sp.type === 'vec') {
    const pick = sp.picks.find(o => flat(o[1]) === flat(raw));
    opts = [...sp.picks.map(o => [o[1], o[0]]), ['#xyz', 'my own numbers x, y, z'], ...mine.map(name => [name, 'your point ' + name]), ['#f', 'a formula']];
    mode = CUI.formula.has(st.id + ':' + sp.key) ? '#f' : pick ? pick[1] : cuXyz(raw) ? '#xyz' : mine.includes(raw) ? raw : '#f';
  } else {
    const given = [['n', `n (Power dial: ${cuShort(S.n)})`], ['radius', 'radius: how far the point is from the middle'], ['theta', 'theta: its angle round the upright axis'], ['phi', 'phi: the angle of its height']];
    opts = [['#num', 'a number'], ...given, ...mine.map(name => [name, 'your number ' + name]), ['#f', 'a formula']];
    mode = CUI.formula.has(st.id + ':' + sp.key) ? '#f' : cuIsNum(raw) ? '#num' : given.some(o => o[0] === raw) || mine.includes(raw) ? raw : '#f';
  }
  return { mode, html: opts.map(o => `<option value="${cuEsc(o[0])}"${o[0] === mode ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('') };
}
// One setting of a step, as a row of the step's body.
function cuRow(st, sp) {
  const key = sp.key, id = `cu-${st.id}-${key}`, raw = String(st.p[key] === undefined ? sp.def : st.p[key]), lab = cuEsc(sp.label);
  const text = extra => `<input type="text" id="${id}" class="cu-in" data-key="${key}" value="${cuEsc(raw)}" spellcheck="false" autocomplete="off" autocapitalize="off"${extra || ''}>`;
  const box = (own, more) => `<input type="number" ${own ? `id="${id}" ` : ''}class="cu-in cu-nbox" data-num="${key}" step="${sp.step || 'any'}" value="${cuIsNum(raw) ? cuNum(raw) : ''}"${more || ''}>`;
  const range = `<input type="range" class="cu-range" data-num="${key}" aria-label="${lab}, slider">`;
  let cell;
  if (sp.type === 'choice') cell = `<select id="${id}" class="cu-in" data-key="${key}">${sp.options.map(o => `<option value="${o[0]}"${o[0] === st.p[key] ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('')}</select>`;
  else if (sp.type === 'text' || sp.type === 'name') cell = text();
  else if (sp.type === 'any') cell = text(` list="cu-dl-${st.id}"`) + range;
  else if (sp.type === 'num' && (sp.bare || sp.fixed)) cell = cuIsNum(raw) ? box(true) : text();
  else if (sp.type === 'num' && sp.own) cell = box(true) + range;
  else {
    const src = cuSource(st, sp), xyz = sp.type === 'vec' ? cuXyz(raw) : null;
    cell = `<select id="${id}" class="cu-src" data-src="${key}" title="Where this value comes from">${src.html}</select>`;
    if (src.mode === '#f') cell += `<input type="text" class="cu-in" data-key="${key}" value="${cuEsc(raw)}" aria-label="${lab}, formula" spellcheck="false" autocomplete="off" autocapitalize="off" list="cu-dl-${st.id}">`;
    else if (xyz) cell += '<span class="cu-xyz">' + xyz.map((x, k) => `<label>${'xyz'[k]}<input type="number" class="cu-in cu-nbox" data-xyz="${key}" step="0.05" value="${x}" aria-label="${lab}, ${'xyz'[k]}"></label>`).join('') + '</span>';
    else if (src.mode === '#num') cell += box(false, ` aria-label="${lab}, number"`) + range;
  }
  return `<div class="cu-row${sp.type === 'text' ? ' cu-row-text' : ''}" data-row="${key}"><label class="label" for="${id}">${lab}</label><div class="cu-cell">${cell}</div></div>`;
}
// A slider shows only while its setting is a plain number, and reaches as far as that number.
function cuRangeSync(li, st) {
  li.querySelectorAll('.cu-range').forEach(r => {
    const sp = cuSpec(st, r.dataset.num), raw = st.p[sp.key];
    r.hidden = !cuIsNum(raw);
    if (r.hidden) return;
    let lo = sp.min === undefined ? -4 : sp.min, hi = sp.max === undefined ? 4 : sp.max;
    if (sp.ranged) { lo = cuNum(st.p.min); hi = cuNum(st.p.max); if (!(hi > lo)) { lo = 0; hi = 1; } }
    const x = cuNum(raw);
    lo = Math.min(lo, x); hi = Math.max(hi, x);
    r.min = lo; r.max = hi; r.step = sp.step && !sp.ranged ? sp.step : (hi - lo) / 200; r.value = x;
  });
}
// The names a formula of this step can use, for the lists its boxes offer.
const cuNamesHtml = st => Object.keys(CU_GIVEN).concat((cuProgram().scopes[st.id] || []).map(x => x[0])).map(name => `<option value="${name}">`).join('');
function cuStepEl(st, i, count) {
  const B = CU_BLOCKS[st.kind], li = document.createElement('li'), k = i + 1;
  li.className = 'cu-step' + (st.on === false ? ' is-off' : ''); li.dataset.id = st.id;
  const tool = (act, label, title, text, off) => `<button type="button" class="cu-tool" data-act="${act}" aria-label="${label}" title="${title}"${off ? ' disabled' : ''}>${text}</button>`;
  li.innerHTML = `<div class="cu-head"><label class="cu-on" title="Switch this step off to see the solid without it."><input type="checkbox" data-act="on"${st.on === false ? '' : ' checked'} aria-label="Step ${k} is on"><span class="cu-no">${k}</span></label>` +
    `<button type="button" class="cu-title" data-act="show" title="Play this step, from its start to its end, in the iteration on show.">${cuEsc(B.title)}</button><span class="cu-flag">now</span><span class="cu-tools">` +
    tool('up', `Move step ${k} earlier`, 'Move earlier', '←', i === 0) + tool('down', `Move step ${k} later`, 'Move later', '→', i === count - 1) +
    (B.basic ? '' : tool('break', `Break step ${k} down`, B.plain ? 'Show this formula as its single operations, each a step of its own.' : 'Show this step as the formulas it is made of, each a step you can change. Those can be broken down again.', 'Break down')) +
    (st.kind === 'formula' ? '' : tool('reset', `Reset step ${k}`, 'Put the settings of this step back to what a new step of this kind has. A name it gives stays.', 'Reset')) +
    tool('remove', `Remove step ${k}`, 'Remove', '✕') + '</span></div>' +
    `<div class="cu-body${B.grid ? ' cu-grid' : ''}">${B.params.map(sp => cuRow(st, sp)).join('')}</div><datalist id="cu-dl-${st.id}">${cuNamesHtml(st)}</datalist><p class="err cu-err" hidden></p>`;
  cuRangeSync(li, st);
  return li;
}
function cuRender() {
  const host = $('cuSteps'), steps = S.custom.steps;
  host.textContent = '';
  steps.forEach((st, i) => host.appendChild(cuStepEl(st, i, steps.length)));
  $('cuEmpty').hidden = steps.length > 0;
  CUI.now = null; CUI.barSig = '';
}
// The menus and name lists follow the rule without the boxes being made again: a name may have come or gone, and
// the Power dial may have moved.
function cuOptionsSync() {
  document.querySelectorAll('#cuSteps .cu-step').forEach(li => {
    const st = S.custom.steps[cuStepAt(li.dataset.id)];
    if (!st) return;
    li.querySelectorAll('.cu-src').forEach(sel => { const src = cuSource(st, cuSpec(st, sel.dataset.src)); sel.innerHTML = src.html; sel.value = src.mode; });
    li.querySelector('datalist').innerHTML = cuNamesHtml(st);
  });
}
// Under each step that cannot be read, why.
function cuErrors() {
  const errs = cuProgram().errs;
  document.querySelectorAll('#cuSteps .cu-step').forEach(li => {
    const p = li.querySelector('.cu-err'), msg = errs[li.dataset.id] || '';
    p.textContent = msg ? 'This step is left out: ' + msg : ''; p.hidden = !msg;
    li.classList.toggle('is-bad', !!msg);
  });
}
function cuSnap() {
  const t = cuRuleText();
  if (CUI.undo[CUI.undo.length - 1] !== t) CUI.undo.push(t);
  if (CUI.undo.length > 40) CUI.undo.shift();
}
// After the rule changed. render: the list itself changed (a step added, moved, removed, a menu turned), not only a value.
function cuChanged(render) {
  S.custom.rev = (S.custom.rev || 0) + 1;
  if (render) cuRender();
  cuStore();
  cuErrors();
  $('cuUndo').disabled = CUI.undo.length === 0;
  if ($('cuTextBox').open) $('cuText').value = cuRuleText();
  if (ap().id === 'custom') uiApproachParam();
  cuBarSync(); cuOverDraw();
}
function cuUse(rule) {
  Object.assign(S.custom, { steps: rule.steps, next: rule.next, bail: rule.bail, rough: !!rule.rough, play: null });
  CUI.formula.clear(); cuPlayStop();
  cuChanged(true);
}
function cuSay(text) { const p = $('cuSay'); p.textContent = text || ''; p.hidden = !text; }

// The bar under the picture: which iteration is on show, how far through its steps, and the buttons that move it.
function cuPlayStop() { CUI.playing = false; CUI.until = null; const b = $('cuPlay'); if (b) b.textContent = 'Play'; }
function cuGo(pass, u) {
  const np = cuPasses(), m = cuMoving().length;
  pass = clamp(Math.round(pass), 1, np); u = clamp(u, 0, m);
  S.custom.play = pass >= np && u >= m ? null : { pass, u };
  cuBarSync(); cuOverDraw(); touch();
}
function cuPlayFrame(now) {
  CUI.raf = 0;
  if (!CUI.playing || !cuOn()) { cuPlayStop(); return; }
  const at = cuPlayAt(), m = cuMoving().length, dt = Math.min((now - CUI.last) / 1000, 0.1);
  CUI.last = now;
  let u = at.u + dt / 1.6;   // one step in 1.6 seconds
  const stop = CUI.until === null ? m : Math.min(CUI.until, m);
  if (u >= stop) { u = stop; cuPlayStop(); }
  cuGo(at.pass, u);
  if (CUI.playing) CUI.raf = requestAnimationFrame(cuPlayFrame);
}
function cuBarSync() {
  if (!cuOn() || !$('cuAt')) return;
  const at = cuPlayAt(), mov = cuMoving(), m = mov.length, np = cuPasses(), lead = cuLead(), steps = S.custom.steps;
  const sig = [at.pass, at.u, at.end, np, lead, S.iter, S.custom.bail, S.custom.rough, S.custom.rev, CUI.playing].join('|');
  if (sig === CUI.barSig) return;
  CUI.barSig = sig;
  const it = $('cuIt'), all = $('cuItAll'), slider = $('cuAt');
  it.min = 1 + lead; it.max = np + lead;
  if (document.activeElement !== it) it.value = at.pass + lead;
  if (document.activeElement !== all) all.value = S.iter;
  slider.max = Math.max(m, 1); slider.disabled = !m;
  if (Math.abs(+slider.value - at.u) > 1e-4) slider.value = at.u;
  $('cuEnd').classList.toggle('is-on', at.end); $('cuEnd').setAttribute('aria-pressed', String(at.end));
  const first = !at.end && at.pass === 1 && at.u === 0;
  $('cuFirst').classList.toggle('is-on', first); $('cuFirst').setAttribute('aria-pressed', String(first));
  for (const id of ['cuPlay', 'cuStepPrev', 'cuStepNext']) $(id).disabled = !m;
  if (document.activeElement !== $('cuBail')) $('cuBail').value = cuShort(S.custom.bail);
  $('cuRoughOn').checked = !!S.custom.rough;
  $('cuBailR').value = S.custom.bail;
  // one mark on the slider for every step that moves the point, with the step's number in the list
  const no = id => cuStepAt(id) + 1, ticks = mov.map(s => no(s.id)).join(',');
  if ($('cuTicks').dataset.sig !== ticks) {
    $('cuTicks').dataset.sig = ticks;
    $('cuTicks').innerHTML = mov.map((s, j) => `<button type="button" data-u="${j + 1}" style="left:${(100 * (j + 1) / m).toFixed(2)}%" title="To the end of step ${no(s.id)}">${no(s.id)}</button>`).join('');
  }
  // the words, and the step they are about
  const whole = Math.abs(at.u - Math.round(at.u)) < 1e-6, j = whole ? Math.round(at.u) - 1 : Math.floor(at.u), cur = m && j >= 0 && !at.end ? mov[j] : null;
  const title = s => { const t = CU_BLOCKS[steps[cuStepAt(s.id)].kind].title; return `step ${no(s.id)}, ${t[0].toLowerCase() + t.slice(1)}`; };
  const I = at.pass + lead, far = cuShort(S.custom.bail);
  $('cuNow').textContent = !m ? 'No step that is switched on moves the point, so there is nothing to play.'
    : at.end ? `The finished solid: all ${S.iter} iterations. It is every starting point that was never thrown out.`
    : at.pass === 1 && at.u === 0 ? `The start${lead ? ' (the first iteration only carries each point to its own c)' : ''}: every point no further than ${far} from the middle is in.`
    : whole && at.u === 0 ? `Iteration ${I} is about to begin. On show is what is left after ${I - 1}.`
    : whole ? `Iteration ${I}, after ${title(cur)}.` + (at.u === m ? ` That is what is left after ${I} iteration${I === 1 ? '' : 's'}.` : '')
    : `Iteration ${I}, during ${title(cur)}.`;
  const now = cur ? String(cur.id) : null;
  if (now !== CUI.now) {
    CUI.now = now;
    document.querySelectorAll('#cuSteps .cu-step').forEach(li => li.classList.toggle('is-now', li.dataset.id === now));
    const li = now && document.querySelector(`#cuSteps .cu-step[data-id="${now}"]`), dock = $('cuDock');
    // bring the marked step into view inside the list of steps, which scrolls by itself on a wide window
    if (li && dock.scrollHeight > dock.clientHeight + 4) {
      const a = li.getBoundingClientRect(), b = dock.getBoundingClientRect();
      const bar = dock.querySelector('.cu-tools-row').offsetHeight + 6;   // the tools stay at the top of the list
      if (a.top < b.top + bar || a.bottom > b.bottom) dock.scrollTop += a.top - b.top - bar;
    }
  }
}
// Show or put away what belongs to the custom approach, after the approach, the mode or the power changed.
function customSync() {
  const on = cuOn();
  // The centre of a Mandelbrot picture. The lab's own rules turn about the middle of their solid, at -0.6 along x,
  // and the custom approach about the origin (camHome). A centre that is still where the page put it goes along
  // when the approach changes between the two; one that was moved stays where it is.
  if (on !== CUI.wasOn) {
    CUI.wasOn = on;
    const h = camHome().target, t = cam.target, known = p => p[1] === 0 && p[2] === 0 && (p[0] === 0 || p[0] === -0.6);
    if (S.mode === 'm' && known(h)) {
      if (known(t) && t[0] !== h[0]) { cam.target = h.slice(); touch(); }
      if (S.v2.y === 0 && (S.v2.x === 0 || S.v2.x === -0.6)) S.v2.x = h[0];
    }
  }
  document.body.classList.toggle('is-custom', on);
  $('cuBar').hidden = $('cuDock').hidden = !on;
  if (on && cuBoth()) $('juliaPanel').hidden = false;   // the Julia half takes its c from this panel
  if (!on) { cuPlayStop(); return; }
  if (document.activeElement !== $('cuN')) $('cuN').value = cuShort(S.n);
  cuOptionsSync();
  CUI.barSig = ''; cuBarSync();
}

function customInit() {
  const C = S.custom, opt = (v, t) => `<option value="${v}">${cuEsc(t)}</option>`;
  $('pd-custom').innerHTML = `<p class="note">Your steps stand under the picture, with the bar that plays them. A step works on the point z and hands it to the next one. One run through the steps is one iteration.</p>
<details class="cu-more" open><summary>What a formula can use</summary>${CU_HELP}</details>
<details class="cu-more" id="cuTextBox"><summary>Your rule as text</summary>
  <p class="note">Copy this text to keep a rule or to send it to someone. To use a rule you were sent, paste it here and press the button.</p>
  <textarea id="cuText" rows="5" spellcheck="false" aria-label="Your rule as text"></textarea>
  <div class="row-btns"><button class="btn" id="cuTextUse" type="button">Use this text</button></div>
</details>`;
  $('cuBar').innerHTML = `<div class="cu-bar-row">
  <span class="label">Iteration</span>
  <button class="btn" id="cuItPrev" type="button" aria-label="The iteration before" title="The iteration before">◀</button>
  <input type="number" id="cuIt" class="cu-in cu-nbox" step="1" aria-label="The iteration on show">
  <span class="cu-of">of</span>
  <input type="number" id="cuItAll" class="cu-in cu-nbox" step="1" min="2" max="400" aria-label="Iterations in all" title="How many iterations the finished solid takes: the Iterations dial of the page.">
  <button class="btn" id="cuItNext" type="button" aria-label="The iteration after" title="The iteration after">▶</button>
  <span class="cu-gap"></span>
  <button class="btn" id="cuFirst" type="button" aria-pressed="false" title="Back to the start of the first iteration, before any step">First iteration</button>
  <button class="btn" id="cuStepPrev" type="button" title="Back one step">◀ Step</button>
  <button class="btn cu-play" id="cuPlay" type="button" title="Plays the steps of one iteration. Press again for the next iteration.">Play</button>
  <button class="btn" id="cuStepNext" type="button" title="On one step">Step ▶</button>
  <button class="btn" id="cuEnd" type="button" aria-pressed="true" title="All the iterations: the solid as the page usually shows it">Finished solid</button>
</div>
<div class="cu-track"><input type="range" id="cuAt" min="0" max="1" step="0.005" value="0" aria-label="How far through the steps of this iteration"><div class="cu-ticks" id="cuTicks"></div></div>
<p class="cu-now" id="cuNow" role="status"></p>
<div class="cu-bar-row cu-bar-small">
  <label class="label" for="cuBail">Thrown out beyond</label>
  <input type="number" id="cuBail" class="cu-in cu-nbox" min="1.2" max="64" step="0.1">
  <input type="range" id="cuBailR" class="cu-range" min="1.2" max="16" step="0.1" aria-label="Thrown out beyond, slider">
  <span class="note">A point is thrown out when a step lands it further than this from the middle. The solid is every starting point that is still in.</span>
</div>
<div class="cu-bar-row cu-bar-small">
  <label class="check" title="Some points of the solid, each drawn where the steps have carried it by now. They show while the play is not at the finished solid."><input type="checkbox" id="cuDotsOn" checked> <span>Dots</span></label>
  <label class="check" title="What the step on show works with: the axis of a turn, the plane of a mirror, the sphere of an inversion, the arrow of a slide."><input type="checkbox" id="cuGuidesOn" checked> <span>Guides</span></label>
  <label class="check" title="One number in place of the neighbouring orbits when the finished solid is drawn: quicker and plainer. Many of the lab’s own approaches are drawn this way, and their rules come with it ticked. A play always uses the fine estimate."><input type="checkbox" id="cuRoughOn"> <span>Plain distance estimate</span></label>
  <label class="check" title="The Mandelbrot picture on the left and the Julia picture on the right, with one camera. The Julia half uses the c of the Julia panel, which then shows in the column on the right."><input type="checkbox" id="cuBothOn"> <span>Mandelbrot and Julia side by side</span></label>
  <span class="note" id="cuDotsSay" hidden></span>
</div>`;
  $('cuDock').innerHTML = `<div class="cu-tools-row">
  <span class="cu-group"><select id="cuAddSel" aria-label="The kind of step to add">${CU_GROUPS.map(g => `<optgroup label="${g}">${Object.entries(CU_BLOCKS).filter(([, B]) => B.group === g).map(([k, B]) => opt(k, B.title)).join('')}</optgroup>`).join('')}</select><button class="btn" id="cuAddBtn" type="button">Add step</button></span>
  <span class="cu-group"><select id="cuStart" aria-label="A rule to load: one you saved, or one to start again from"></select><button class="btn" id="cuStartBtn" type="button" title="Puts these steps in the place of yours. Undo brings yours back.">Load</button><button class="btn" id="cuDelBtn" type="button" hidden title="Takes the chosen saved rule off the list. Your steps on the page stay.">Delete</button></span>
  <span class="cu-group"><input type="text" id="cuSaveName" class="cu-in" maxlength="40" placeholder="Name for this rule" aria-label="The name to save this rule under" autocomplete="off" spellcheck="false"><button class="btn" id="cuSaveBtn" type="button" title="Keeps the steps as they are now, under this name, in the list beside it. Saved rules stay in this browser.">Save</button></span>
  <button class="btn" id="cuUndo" type="button" disabled>Undo</button>
  <span class="cu-group"><label class="label" for="cuN" title="The Power dial of the page. A step whose menu says “n (Power dial)” follows it.">Power n</label><input type="number" id="cuN" class="cu-in cu-nbox" step="0.1"></span>
  <p class="note cu-say" id="cuSay" role="status" hidden></p>
</div>
<ol class="cu-steps" id="cuSteps"></ol>
<p class="note" id="cuEmpty" hidden>There are no steps, so every point stays where it is. Add a step, or load a rule to start from.</p>`;
  const list = $('cuSteps'), at = e => { const li = e.target.closest('.cu-step'); return li ? { li, i: cuStepAt(li.dataset.id), st: C.steps[cuStepAt(li.dataset.id)] } : {}; };
  // a number moved, by its box or its slider, or one of a point's three numbers: nothing else changes, so the picture follows at once
  list.addEventListener('input', e => {
    const t = e.target, { li, st } = at(e), key = t.dataset.num || t.dataset.xyz;
    if (!st || !key) return;
    let next;
    if (t.dataset.num) { if (t.value === '' || !isFinite(+t.value)) return; next = cuShort(t.value); }
    else {
      const boxes = [...li.querySelectorAll(`[data-xyz="${key}"]`)];
      if (boxes.some(b => b.value === '' || !isFinite(+b.value))) return;
      next = `vec(${boxes.map(b => cuShort(b.value)).join(', ')})`;
    }
    if (!CUI.hot) { cuSnap(); CUI.hot = true; }
    st.p[key] = next;
    if (t.dataset.num) li.querySelectorAll(`[data-num="${key}"], [data-key="${key}"]`).forEach(o => { if (o !== t) o.value = next; });
    cuChanged(false);
  });
  list.addEventListener('change', e => {
    const t = e.target, { li, st } = at(e);
    if (!st) return;
    cuSay('');
    if (t.dataset.act === 'on') { cuSnap(); st.on = t.checked; li.classList.toggle('is-off', !t.checked); cuChanged(false); return; }
    if (t.dataset.num || t.dataset.xyz) { CUI.hot = false; cuRangeSync(li, st); cuOptionsSync(); return; }   // taken already, as it moved
    if (t.dataset.src) {
      const key = t.dataset.src, sp = cuSpec(st, key), v = t.value, f = st.id + ':' + key;
      cuSnap();
      CUI.formula.delete(f);
      if (v === '#f') CUI.formula.add(f);
      else if (v === '#num') { if (!cuIsNum(st.p[key])) st.p[key] = cuIsNum(sp.def) ? sp.def : cuShort(S.n); }
      else if (v === '#xyz') { if (!cuXyz(st.p[key])) st.p[key] = 'vec(1, 0, 0)'; }
      else st.p[key] = v;
      cuChanged(true);
      const box = list.querySelector(`.cu-step[data-id="${st.id}"] [data-row="${key}"] .cu-in`) || $(`cu-${st.id}-${key}`);
      if (box) box.focus({ preventScroll: true });
      return;
    }
    if (t.dataset.key) {
      const sp = cuSpec(st, t.dataset.key);
      cuSnap();
      st.p[sp.key] = t.value.trim() || sp.def; t.value = st.p[sp.key];
      cuChanged(false);
      cuRangeSync(li, st); cuOptionsSync();
    }
  });
  list.addEventListener('click', e => {
    const b = e.target.closest('.cu-tool, .cu-title'), { i, st } = b ? at(e) : {};
    if (!st) return;
    cuSay('');
    const act = b.dataset.act;
    if (act === 'show') {
      // a step that does not move the point has nothing to play: the next one that does is played
      const mov = cuMoving(), me = cuProgram().run.find(s => s.id === st.id), j = mov.findIndex(s => s.id === st.id), k = me ? mov.findIndex(s => s.ord > me.ord) : -1;
      if (st.on === false) { cuSay('This step is switched off, so the play has no place for it.'); return; }
      if (j < 0 && k < 0) { cuSay(me ? 'This step does not move the point, and no step after it does.' : 'This step cannot be read yet, so the play has no place for it.'); return; }
      // play this step from its start to its end, in the iteration on show (the first, from the finished solid)
      const now = cuPlayAt(), from = j >= 0 ? j : k;
      cuPlayStop();
      cuGo(now.end ? 1 : now.pass, from);
      CUI.until = from + 1; CUI.playing = true; CUI.last = performance.now(); $('cuPlay').textContent = 'Pause';
      if (!CUI.raf) CUI.raf = requestAnimationFrame(cuPlayFrame);
      if (j < 0) cuSay('This step does not move the point, so the next step that does is played.');
      return;
    }
    if (act === 'break') {
      let parts;
      try { parts = st.kind === 'formula' ? cuSplit(st.p.text, cuProgram().scopes[st.id] || [], cuTaken(C.steps)) : cuBroken(st, cuTaken(C.steps)); }
      catch (err) { cuSay('This step cannot be broken down yet: ' + err.message); return; }
      if (!parts) { cuSay('This step is one operation already.'); return; }
      if (C.steps.length - 1 + parts.length > CU_MAX_STEPS) { cuSay(`A rule can hold ${CU_MAX_STEPS} steps, and breaking this one down would pass that.`); return; }
      cuSnap();
      C.steps.splice(i, 1, ...parts.map(x => Object.assign(cuStepOf(x.kind, x.p, C.next++), { on: st.on !== false })));
    } else if (act === 'reset') {
      // back to the settings of a new step of this kind; the name it gives stays, since later steps may use it
      cuSnap();
      for (const sp of CU_BLOCKS[st.kind].params) { if (sp.type !== 'name') st.p[sp.key] = sp.def; CUI.formula.delete(st.id + ':' + sp.key); }
    } else {
      cuSnap();
      if (act === 'remove') C.steps.splice(i, 1);
      else { const j = act === 'up' ? i - 1 : i + 1; if (j < 0 || j >= C.steps.length) return; C.steps.splice(j, 0, C.steps.splice(i, 1)[0]); }
    }
    cuChanged(true);
    const again = act === 'remove' || act === 'break' ? null : list.querySelector(`.cu-step[data-id="${st.id}"] [data-act="${act}"]`);
    if (again && !again.disabled) again.focus({ preventScroll: true });
  });
  $('cuAddBtn').addEventListener('click', () => {
    cuSay('');
    if (C.steps.length >= CU_MAX_STEPS) { cuSay(`A rule can hold ${CU_MAX_STEPS} steps.`); return; }
    cuSnap();
    const st = cuStepOf($('cuAddSel').value, {}, C.next++), named = st.kind === 'slider' ? 'name' : st.p.out !== undefined ? 'out' : '';
    if (named) st.p[named] = cuFresh(cuTaken(C.steps))(st.p[named]);   // a name the rule does not have yet
    C.steps.push(st);
    cuChanged(true);
    const li = list.lastElementChild, f = li && li.querySelector('.cu-in, .cu-src');
    if (li) { $('cuDock').scrollTop = $('cuDock').scrollHeight; li.scrollIntoView({ block: 'nearest' }); }
    if (f) f.focus({ preventScroll: true });
  });
  cuSavedLoad(); cuStartMenu();
  $('cuStart').addEventListener('change', () => {
    const v = $('cuStart').value;
    $('cuDelBtn').hidden = v[0] !== 's';
    if (v[0] === 's') $('cuSaveName').value = CUI.saved[+v.slice(1)].name;   // saving under this name again replaces it
  });
  $('cuStartBtn').addEventListener('click', () => {
    const v = $('cuStart').value;
    if (v[0] === 's') {
      const mine = CUI.saved[+v.slice(1)], rule = mine && cuRuleOf(mine.rule);
      if (!rule) return;
      cuSnap(); cuUse(rule);
      cuSay(`“${mine.name}” is loaded. Undo brings the steps you had back.`);
      return;
    }
    // One of the lab's approaches comes with what its own picture is drawn with: points are thrown out beyond 64,
    // and the distance estimate is the plain one where the approach asks for that.
    const k = +v, steps = cuStartSteps(k), lab = CU_STARTS[k].lab ? APPROACHES.find(x => x.id === CU_STARTS[k].lab) : null;
    cuSnap(); cuUse({ steps, next: steps.length + 1, bail: CU_STARTS[k].bail || (lab ? 64 : CU_BAIL), rough: !!lab && lab.deMax === 0 });
    cuSay('Loaded. Undo brings your own steps back.' + (lab ? ' “Thrown out beyond” stands at 64, as in the lab’s own picture of this rule; for the play, 2 shows more in the first iterations.' : '') + (CU_STARTS[k].say ? ' ' + CU_STARTS[k].say : ''));
  });
  $('cuSaveBtn').addEventListener('click', () => {
    const name = $('cuSaveName').value.trim().slice(0, 40);
    if (!name) { cuSay('Type a name for the rule in the box beside Save first.'); $('cuSaveName').focus(); return; }
    const at = CUI.saved.findIndex(s => s.name.toLowerCase() === name.toLowerCase()), entry = { name, rule: JSON.parse(cuRuleText()) }, was = CUI.saved.slice();
    if (at >= 0) CUI.saved[at] = entry; else CUI.saved.push(entry);
    if (!cuSavedStore()) { CUI.saved = was; cuSay('This browser would not keep the rule: its storage is blocked or full. The text under “Your rule as text”, in the column on the right, can be copied and kept instead.'); return; }
    cuStartMenu('s' + (at >= 0 ? at : CUI.saved.length - 1));
    cuSay((at >= 0 ? `“${name}” now holds the steps as they are.` : `Saved as “${name}”.`) + ' It is in the list beside Load, under “Your saved rules”, and is kept in this browser.');
  });
  $('cuSaveName').addEventListener('keydown', e => { if (e.key === 'Enter') $('cuSaveBtn').click(); });
  $('cuDelBtn').addEventListener('click', () => {
    const v = $('cuStart').value, k = +v.slice(1), mine = v[0] === 's' ? CUI.saved[k] : null;
    if (!mine) return;
    CUI.saved.splice(k, 1);
    cuSavedStore(); cuStartMenu();
    cuSay(`“${mine.name}” is off the list. The steps on the page are as they were.`);
  });
  $('cuUndo').addEventListener('click', () => {
    const t = CUI.undo.pop();
    if (t === undefined) return;
    cuSay('');
    cuUse(cuRuleOf(JSON.parse(t)) || { steps: [], next: 1, bail: C.bail });
  });
  $('cuN').addEventListener('change', () => { const v = +$('cuN').value; if (isFinite(v)) { S.n = v; syncControls(); refresh(); } });
  $('cuTextBox').addEventListener('toggle', () => { if ($('cuTextBox').open) $('cuText').value = cuRuleText(); });
  $('cuTextUse').addEventListener('click', () => {
    let rule = null;
    try { rule = cuRuleOf(JSON.parse($('cuText').value)); } catch (err) { /* not a rule */ }
    if (!rule) { cuSay('That text is not a rule: nothing was changed. A rule is the text this box shows for your own steps.'); return; }
    cuSnap(); cuUse(rule); cuSay('The rule from the text is in use. Undo brings the earlier one back.');
  });
  // the bar
  const move = d => { const p = cuPlayAt(); cuPlayStop(); if (d < 0 && p.pass === 1) cuGo(1, 0); else cuGo(p.pass + d, 1e9); };
  $('cuItPrev').addEventListener('click', () => move(-1));
  $('cuItNext').addEventListener('click', () => move(1));
  $('cuIt').addEventListener('change', () => { cuPlayStop(); cuGo((+$('cuIt').value || 1) - cuLead(), 1e9); CUI.barSig = ''; cuBarSync(); });
  $('cuItAll').addEventListener('change', () => { const v = Math.round(+$('cuItAll').value); if (v >= 1 + cuLead()) { S.iter = Math.min(v, 400); syncControls(); touch(); } CUI.barSig = ''; cuBarSync(); });
  $('cuStepPrev').addEventListener('click', () => {
    const p = cuPlayAt(), m = cuMoving().length;
    cuPlayStop();
    let u = Math.ceil(p.u - 1e-9) - 1, pass = p.pass;
    if (u < 0) { if (pass > 1) { pass--; u = m - 1; } else u = 0; }
    cuGo(pass, u);
  });
  $('cuStepNext').addEventListener('click', () => {
    const p = cuPlayAt(), m = cuMoving().length;
    cuPlayStop();
    let u = Math.floor(p.u + 1e-9) + 1, pass = p.pass;
    if (u > m) { if (pass < cuPasses()) { pass++; u = 1; } else u = m; }
    cuGo(pass, u);
  });
  $('cuPlay').addEventListener('click', () => {
    if (CUI.playing) { cuPlayStop(); CUI.barSig = ''; cuBarSync(); return; }
    const p = cuPlayAt(), m = cuMoving().length;
    if (!m) return;
    // from the end of an iteration the play goes on with the next one; from the finished solid it starts over
    if (p.u >= m - 1e-9) S.custom.play = p.end ? { pass: 1, u: 0 } : { pass: p.pass + 1, u: 0 };
    else if (!S.custom.play) S.custom.play = { pass: p.pass, u: p.u };
    CUI.playing = true; CUI.last = performance.now(); $('cuPlay').textContent = 'Pause';
    if (!CUI.raf) CUI.raf = requestAnimationFrame(cuPlayFrame);
  });
  $('cuEnd').addEventListener('click', () => { cuPlayStop(); cuGo(1e9, 1e9); });
  $('cuFirst').addEventListener('click', () => { cuPlayStop(); cuGo(1, 0); });
  $('cuAt').addEventListener('input', () => { cuPlayStop(); cuGo(cuPlayAt().pass, +$('cuAt').value); });
  $('cuTicks').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { cuPlayStop(); cuGo(cuPlayAt().pass, +b.dataset.u); } });
  const bail = v => { if (isFinite(+v) && +v > 0) { S.custom.bail = cuBailOf(v); cuStore(); cuBarSync(); touch(); } };
  $('cuRoughOn').addEventListener('change', () => { S.custom.rough = $('cuRoughOn').checked; cuStore(); touch(); });
  $('cuBail').addEventListener('input', () => bail($('cuBail').value));
  $('cuBailR').addEventListener('input', () => bail($('cuBailR').value));
  // the button under the Approach menu: to the custom approach, and back to the approach before it
  const mine = APPROACHES.findIndex(a => a.id === 'custom');
  $('apCustomBtn').addEventListener('click', () => {
    if (S.approach === mine) S.approach = CUI.before === mine ? 0 : CUI.before;
    else { CUI.before = S.approach; S.approach = mine; }
    uiApMenu(false);
    refresh();
  });
  cuRender(); cuErrors();
  hooks.refresh.push(customSync); hooks.view.push(cuBarSync);
  cuOverInit();
  customSync();
}

// What is drawn over the picture: the dots and the guides while a play is under way, and the names of the two
// halves while both pictures are on show. All of it is worked out here, in JavaScript, and drawn on a canvas of its
// own with the picture's camera.
//
// The dots. The solid is drawn where its points started, so a step that only turns points changes nothing in it.
// The dots are some of those points, each drawn where the steps have carried it by now (cuRun), with a short tail
// that says where it just came from. A dot keeps the colour of where it started.
//
// The guides. What the step on show works with, where that is the same for every point: the axis of a turn and the
// circle the turn goes round, the plane of a mirror, the sphere of an inversion, the arrow of a slide.
const CU_DOTS = 420, CU_DOTS_TRIES = 60000, CU_DOTS_MS = 60, CU_DOTS_TAIL = 0.18;
const CUD = { cv: null, found: {}, drawn: '' };
const cuHalton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
// the modifiers of the page, which every step of an orbit begins with
const cuMod = z => [S.abs[0] ? Math.abs(z[0]) : z[0], (S.abs[1] ? Math.abs(z[1]) : z[1]) * (S.flip[0] ? -1 : 1), (S.abs[2] ? Math.abs(z[2]) : z[2]) * (S.flip[1] ? -1 : 1)];
// Where the starting point p is when the pass `pass` begins, with what its orbit carries: { z, st, c }, or null
// when it was thrown out before that. mode: 'j' a Julia picture, 'm' a Mandelbrot one.
function cuDotAt(p, pass, bail, mode) {
  const car = CARRY.custom, jul = mode === 'j', c = jul ? S.c.slice(0, 3) : p, n = S.n;
  let z = jul ? p : [0, 0, 0], st = car.start();
  const full = () => { const v = cuMod(z); st = car.step(st, v, c); z = cuRun(v, st.cm, n, st); };
  if (!jul) full();   // the first iteration of a Mandelbrot picture carries the point to its own c
  for (let k = 1; k < pass; k++) { if (!(len(z) <= bail)) return null; full(); }
  return len(z) <= bail ? { z, st, c } : null;
}
// The dots for the pass on show: starting points spread evenly through the big ball, of which those still in are
// kept. The same points are tried in the same order every time, so a dot that is still in keeps its place and colour.
function cuDotsFind(pass, mode) {
  const bail = cuBailOf(S.custom.bail), sig = [S.custom.rev, mode === 'j' ? S.c.join(',') : '', S.n, bail, S.abs, S.flip, pass, S.z0].join('|');
  const kept = CUD.found[mode];
  if (kept && kept.sig === sig) return kept.dots;
  const dots = [], t0 = performance.now();
  CUD.found[mode] = { sig, dots };
  if (mode === 'm' && S.z0.trim() !== '0') return dots;   // a start value of its own: the page has no JavaScript for it
  for (let i = 1; i <= CU_DOTS_TRIES && dots.length < CU_DOTS; i++) {
    if (i % 400 === 0 && performance.now() - t0 > CU_DOTS_MS) break;
    const p = [bail * (2 * cuHalton(i, 2) - 1), bail * (2 * cuHalton(i, 3) - 1), bail * (2 * cuHalton(i, 5) - 1)];
    if (len(p) > bail) continue;
    const d = cuDotAt(p, pass, bail, mode);
    if (!d) continue;
    // the hue says which way round the upright axis the dot started, the lightness how high
    d.hue = Math.round((Math.atan2(p[1], p[0]) / PI + 1) * 180); d.light = Math.round(52 + 18 * clamp(p[2] / bail, -1, 1));
    dots.push(d);
  }
  return dots;
}
// The value of a setting where it is the same for every point (a typed point, a number, c in a Julia picture, a
// formula of those), or null where it follows the point or a name the rule made.
function cuFixed(text, kind, mode) {
  try {
    const node = cuParse(String(text), { vars: new Map(), zero: [], uses: new Set(), K: [], internal: false });
    let fixed = node.t === kind;
    (function walk(tr) {
      if (tr.leaf === undefined) (tr.a || [tr.of]).forEach(walk);
      else if (/^[A-Za-z]/.test(tr.leaf) && tr.leaf !== 'pi' && tr.leaf !== 'n' && !(tr.leaf === 'c' && mode === 'j')) fixed = false;
      if (tr.fn === 'point') fixed = false;
    })(node.tree);
    return fixed ? node.js({ z: [0, 0, 0], c: cuCmap(S.c.slice(0, 3)), n: S.n, K: [], v: [], tt: 1, first: [0, 0, 0], last: [0, 0, 0], mean: [0, 0, 0], count: 0 }) : null;
  } catch (err) { return null; }   // a name of the rule's own, or a formula that cannot be read
}
// The guides of one step, as shapes in space: { line: [a, b] }, { ring: [centre, normal, radius] }, { arrow: [a, b] },
// each with an optional label. R: the size to draw them at. Returns { shapes, note }.
// env: the point and the names of one dot as the step begins (cuEnvAt). What is not the same for every point is then
// worked out for that dot, and `own` says so.
function cuGuides(st, R, mode, env) {
  const p = st.p, shapes = [], O = [0, 0, 0];
  let own = false;
  const value = (key, kind) => {
    const x = cuFixed(p[key], kind, mode);
    if (x !== null || !env) return x;
    const y = cuValueFor(p[key], kind, env);
    if (y !== null) own = true;
    return y;
  };
  const vec = key => value(key, 'v'), num = key => value(key, 's');
  const axis = (a, label) => { const u = norm(a); shapes.push({ line: [scl(u, -1.25 * R), scl(u, 1.25 * R)], label }); return u; };
  let note = '';
  const moving = what => { note = `The ${what} of this step is not the same for every point. With the dots on, it is drawn for one of them.`; };
  if (st.kind === 'lon' || st.kind === 'rot' || st.kind === 'lat' || st.kind === 'merc') {
    const a = vec('axis');
    if (!a || !(len(a) > 1e-9)) moving('axis');
    else {
      const u = axis(a, 'axis');
      shapes.push({ ring: [O, u, 0.9 * R], label: st.kind === 'lat' || st.kind === 'merc' ? 'the plane the height is counted from' : 'the turn goes round' });
      const f = st.kind === 'lon' ? vec('from') : null, flat = f ? sub(f, scl(u, dot(f, u))) : null;
      if (flat && len(flat) > 1e-9) shapes.push({ arrow: [O, scl(norm(flat), 0.9 * R)], label: 'angle 0' });
    }
  } else if (st.kind === 'len') {
    for (const k of [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) shapes.push({ ring: [O, k, 1] });
    shapes[0].label = 'length 1: points here stay';
  } else if (st.kind === 'inv') {
    const c = vec('centre'), r = num('radius');
    if (!c || !(r > 0)) moving('sphere');
    else { for (const k of [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) shapes.push({ ring: [c, k, r] }); shapes[0].label = 'the sphere'; }
  } else if (st.kind === 'mirror' || st.kind === 'fold') {
    const nrm = vec('normal'), at = vec('through');
    if (!nrm || !at || !(len(nrm) > 1e-9)) moving('plane');
    else { const u = norm(nrm); shapes.push({ ring: [at, u, 1.1 * R], label: 'the plane' }, { ring: [at, u, 0.55 * R] }, { arrow: [at, add(at, scl(u, 0.6 * R))], label: st.kind === 'fold' ? 'the side that is kept' : '' }); }
  } else if (st.kind === 'addc' || st.kind === 'shift') {
    const w = st.kind === 'addc' ? vec('what') : vec('by'), k = st.kind === 'addc' ? num('times') : 1;
    if (!w || k === null) note = mode === 'm' && st.kind === 'addc' ? 'In a Mandelbrot picture every point has a c of its own, so there is no one arrow to draw: each dot slides by the place it started from.' : 'This slide is not the same for every point, so it is not drawn.';
    else shapes.push({ arrow: own ? [env.z, add(env.z, scl(w, k))] : [O, scl(w, k)], label: own ? 'the ringed dot slides by this' : st.kind === 'addc' ? 'every point slides by this' : 'the slide' });
  } else if (st.kind === 'quatpow') {
    axis([1, 0, 0], 'the x-axis: each point turns away from it, in the flat sheet that holds both');
  } else if (st.kind === 'quatturn') {
    const q = ['x', 'y', 'z'].map(num);
    if (q.some(x => x === null) || !(len(q) > 1e-9)) moving('axis');
    else { const u = axis(q, 'axis'); shapes.push({ ring: [O, u, 0.9 * R], label: 'the turn goes round' }); }
  }
  if (own) note = 'What this step works with is not the same for every point: the guide shows it as it is for the ringed dot.';
  return { shapes, note, own };
}
function cuOverDraw() {
  const cv = CUD.cv;
  if (!cv) return;
  const stage = $('stage'), w = stage.clientWidth, h = stage.clientHeight, dpr = Math.min(devicePixelRatio || 1, 2), C = S.custom;
  const on = cuOn() && !S.learn, both = on && !!C.both, dotsOn = C.dots !== false, guidesOn = C.guides !== false;
  const at = on && !S.flat && (dotsOn || guidesOn) ? cuPlayNow() : null, b = basis(), say = $('cuDotsSay');
  const sig = [both, w, h, dpr, theme.brass, theme.ink2, at ? [at.pass, at.ord, at.t, dotsOn, guidesOn, C.rev, C.bail, S.mode, S.c, S.n, S.abs, S.flip, S.z0, b.pos, b.right, b.up, S.view.fov] : ''].join('|');
  if (sig === CUD.drawn) return;
  CUD.drawn = sig;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const g = cv.getContext('2d'), font = getComputedStyle(document.body).fontFamily;
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);
  // one pane, or the two halves: the Mandelbrot picture on the left and the Julia one on the right
  const panes = both ? [{ mode: 'm', x0: 0, x1: w / 2, name: 'Mandelbrot: each point is its own c' }, { mode: 'j', x0: w / 2, x1: w, name: 'Julia: c from the dials' }] : [{ mode: S.mode, x0: 0, x1: w }];
  if (both) {
    g.strokeStyle = theme.ink2; g.lineWidth = 1; g.globalAlpha = 0.6; g.beginPath(); g.moveTo(w / 2, 0); g.lineTo(w / 2, h); g.stroke(); g.globalAlpha = 1;
    g.font = '600 13px ' + font; g.textBaseline = 'top'; g.fillStyle = theme.ink2;
    for (const P of panes) g.fillText(P.name, P.x0 + (P.mode === 'm' ? 64 : 12), 10);
  }
  if (!at) { say.hidden = true; return; }
  const n = S.n, bail = cuBailOf(C.bail), fov = S.view.fov, notes = [];
  const run = cuProgram().run.find(s => s.ord === at.ord), st = run ? C.steps[cuStepAt(run.id)] : null;
  for (const P of panes) {
    const cx = (P.x0 + P.x1) / 2, words = [];
    const scr = p => { const q = sub(p, b.pos), zc = dot(q, b.f); return zc > 0.02 ? [cx + dot(q, b.right) / (zc * fov) * h / 2, h / 2 - dot(q, b.up) / (zc * fov) * h / 2, zc] : null; };
    g.save(); g.beginPath(); g.rect(P.x0, 0, P.x1 - P.x0, h); g.clip();
    // one dot stands for the others where a guide is not the same for every point: it gets a ring
    const dots = dotsOn ? cuDotsFind(at.pass, P.mode) : [], car = CARRY.custom, mark = dots[0] || null;
    let env = null, ringed = false;
    if (mark && st) { const v0 = cuMod(mark.z), s0 = car.step(mark.st, v0, mark.c); env = cuEnvAt(v0, s0.cm, n, s0, at.ord); }
    // the guides of the step on show, under the dots; their words are written last, over everything
    if (guidesOn && st) {
      const G = cuGuides(st, bail, P.mode, env), path = pts => { g.beginPath(); let pen = false; for (const p of pts) { const q = scr(p); if (!q) { pen = false; continue; } if (pen) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); pen = true; } g.stroke(); };
      for (const s of G.shapes) {
        g.strokeStyle = theme.brass; g.fillStyle = theme.brass; g.globalAlpha = 0.95; g.lineWidth = 1.6;
        if (s.ring) {
          const [c, k, r] = s.ring, e1 = norm(cross(k, Math.abs(k[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0])), e2 = cross(k, e1), pts = [];
          for (let j = 0; j <= 96; j++) { const a = 2 * PI * j / 96; pts.push(add(c, add(scl(e1, r * Math.cos(a)), scl(e2, r * Math.sin(a))))); }
          g.setLineDash([5, 4]); path(pts); g.setLineDash([]);
          if (s.label) words.push([pts[12], s.label]);
        } else {
          const [p0, p1] = s.line || s.arrow, pts = [];
          for (let j = 0; j <= 24; j++) pts.push(add(p0, scl(sub(p1, p0), j / 24)));
          g.setLineDash([]); g.lineWidth = s.arrow ? 2.2 : 1.6; path(pts);
          const tip = scr(p1), back = scr(add(p0, scl(sub(p1, p0), 0.9)));
          if (s.arrow && tip && back) {   // an arrow head, in the picture's plane
            const d = [tip[0] - back[0], tip[1] - back[1]], l = Math.hypot(d[0], d[1]) || 1, u = [d[0] / l, d[1] / l];
            g.beginPath(); g.moveTo(tip[0], tip[1]); g.lineTo(tip[0] - 10 * u[0] + 5 * u[1], tip[1] - 10 * u[1] - 5 * u[0]); g.lineTo(tip[0] - 10 * u[0] - 5 * u[1], tip[1] - 10 * u[1] + 5 * u[0]); g.closePath(); g.fill();
          }
          if (s.label) words.push([p1, s.label]);
        }
      }
      g.globalAlpha = 1;
      if (G.note && !notes.includes(G.note)) notes.push(G.note);
      ringed = !!G.own;
    }
    if (dotsOn) {
      const out = [];
      let turned = true;   // no dot has come nearer to the middle or gone further from it in this step
      for (const d of dots) {
        const v = cuMod(d.z), stp = car.step(d.st, v, d.c);
        const now = cuRun(v, stp.cm, n, stp, { ord: at.ord, t: at.t });
        const before = cuRun(v, stp.cm, n, stp, { ord: at.ord, t: 0 }), tail = at.t > 0 ? cuRun(v, stp.cm, n, stp, { ord: at.ord, t: Math.max(0, at.t - CU_DOTS_TAIL) }) : now;
        if (Math.abs(len(now) - len(before)) > 1e-6 * Math.max(len(before), 1e-6)) turned = false;
        if (!(len(now) <= bail)) continue;   // thrown out at this moment
        const A = scr(now), B = scr(tail);
        if (A) out.push({ A, B, d });
      }
      out.sort((x, y) => y.A[2] - x.A[2]);   // the far ones first
      for (const o of out) {
        const r = clamp(0.024 * h / (o.A[2] * fov), 1.6, 7), col = `hsl(${o.d.hue} 85% ${o.d.light}%)`;
        if (o.B) { g.strokeStyle = col; g.globalAlpha = 0.55; g.lineWidth = Math.max(1, 0.6 * r); g.beginPath(); g.moveTo(o.B[0], o.B[1]); g.lineTo(o.A[0], o.A[1]); g.stroke(); }
        g.globalAlpha = 1; g.fillStyle = col; g.strokeStyle = 'rgba(0, 0, 0, 0.75)'; g.lineWidth = 1;
        g.beginPath(); g.arc(o.A[0], o.A[1], r, 0, 2 * PI); g.fill(); g.stroke();
        if (ringed && o.d === mark) { g.strokeStyle = theme.dark ? '#fff' : '#000'; g.lineWidth = 2; g.beginPath(); g.arc(o.A[0], o.A[1], r + 5, 0, 2 * PI); g.stroke(); }
      }
      const line = P.mode === 'm' && S.z0.trim() !== '0' ? 'There are no dots while the Mandelbrot set starts z at something other than 0.'
        : !dots.length ? 'No dot is left: the solid is too thin here for the dots to find it.'
        : turned && at.t > 0 ? 'This step turns the points without moving any of them nearer to the middle or further from it. So no point is thrown out, and the solid stays as it is: the dots show the turn.'
        : 'A dot is a point of the solid, drawn where the steps have carried it by now. Its colour says where it started.';
      if (!notes.includes(line)) notes.unshift(line);
    }
    for (const [p, text] of words) {
      const q = scr(p);
      if (!q) continue;
      g.font = '600 13px ' + font; g.textBaseline = 'middle'; g.setLineDash([]); g.globalAlpha = 1;
      const tw = g.measureText(text).width, x = clamp(q[0] + 10, P.x0 + 4, Math.max(P.x0 + 4, P.x1 - tw - 8)), y = clamp(q[1], 12, h - 12);
      g.fillStyle = `rgba(${theme.stage.map(c => Math.round(255 * c)).join(', ')}, 0.82)`; g.fillRect(x - 4, y - 10, tw + 8, 20);
      g.fillStyle = theme.brass; g.fillText(text, x, y);
    }
    g.restore();
  }
  say.hidden = !notes.length;
  say.textContent = notes.join(' ');
}
function cuOverInit() {
  const cv = document.createElement('canvas');
  cv.className = 'cu-dots'; cv.setAttribute('aria-hidden', 'true');
  $('view').after(cv);
  CUD.cv = cv;
  const again = () => { CUD.drawn = ''; cuOverDraw(); };
  for (const [id, key] of [['cuDotsOn', 'dots'], ['cuGuidesOn', 'guides']]) {
    $(id).checked = S.custom[key] !== false;
    $(id).addEventListener('change', () => { S.custom[key] = $(id).checked; again(); });
  }
  // both pictures at once: the shader draws the two halves (see cuUniforms), and the Julia panel shows for its c
  $('cuBothOn').checked = !!S.custom.both;
  $('cuBothOn').addEventListener('change', () => { S.custom.both = $('cuBothOn').checked; CUI.barSig = ''; refresh(); });
  hooks.view.push(cuOverDraw); hooks.refresh.push(again);
  addEventListener('resize', again);
}
