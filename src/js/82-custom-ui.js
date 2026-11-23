// The custom approach on the page. Under the picture stand the bar that plays the steps (#cuBar) and the steps
// themselves with their tools (#cuDock); the approach's panel in the controls column holds the help and the rule
// as text. The rule itself is in 12-custom.js; this file only changes S.custom and shows it.
const CUI = {
  undo: [],              // earlier rules, as text, newest last
  hot: false,            // a slider or a number box of a step is being moved (one undo entry for the whole move)
  before: 0,             // the approach that was chosen before the custom one (the button goes back to it)
  formula: new Set(),    // 'step id:key' of the settings whose menu stands on "a formula"
  playing: false, raf: 0, last: 0,
  barSig: '', now: null, // what the bar last showed; the id of the step it marked
};
const cuEsc = t => String(t).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const cuStepAt = id => S.custom.steps.findIndex(s => String(s.id) === String(id));
const cuShort = x => String(+(+x).toFixed(4));
const cuOn = () => ap().id === 'custom' && S.mode !== 'k';
const cuSpec = (st, key) => CU_BLOCKS[st.kind].params.find(x => x.key === key);
const CU_HELP = `<p class="note"><b>A point</b> is written <code>vec(x, y, z)</code>, as in <code>vec(0, 0, 1)</code> for one step straight up. Every box for a point takes that, a name such as <code>c</code> or <code>z</code>, or a formula.</p>
<p class="note"><b>A formula step</b> is one line, <code>name = formula</code>. The name <code>z</code> is the point: a line that starts <code>z =</code> moves it. Any other name is yours and can be used in every step after it.</p>
<p class="note"><b>Given:</b> <code>z</code> the point, <code>c</code>, <code>n</code> the Power dial, <code>pi</code>, and from the orbit <code>first</code> (its first point), <code>last</code> (the point of the step before), <code>mean</code> (the average of its points so far) and <code>count</code> (which iteration this is).</p>
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
    opts = [['#num', 'a number'], ['n', `n (Power dial: ${cuShort(S.n)})`], ...mine.map(name => [name, 'your number ' + name]), ['#f', 'a formula']];
    mode = CUI.formula.has(st.id + ':' + sp.key) ? '#f' : cuIsNum(raw) ? '#num' : raw === 'n' ? 'n' : mine.includes(raw) ? raw : '#f';
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
    `<span class="cu-title">${cuEsc(B.title)}</span><span class="cu-flag">now</span><span class="cu-tools">` +
    tool('up', `Move step ${k} earlier`, 'Move earlier', '←', i === 0) + tool('down', `Move step ${k} later`, 'Move later', '→', i === count - 1) +
    (B.basic ? '' : tool('break', `Break step ${k} down`, B.plain ? 'Show this formula as its single operations, each a step of its own.' : 'Show this step as the formulas it is made of, each a step you can change. Those can be broken down again.', 'Break down')) +
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
  cuBarSync();
}
function cuUse(rule) {
  Object.assign(S.custom, { steps: rule.steps, next: rule.next, bail: rule.bail, play: null });
  CUI.formula.clear(); cuPlayStop();
  cuChanged(true);
}
function cuSay(text) { const p = $('cuSay'); p.textContent = text || ''; p.hidden = !text; }

// The bar under the picture: which iteration is on show, how far through its steps, and the buttons that move it.
function cuPlayStop() { CUI.playing = false; const b = $('cuPlay'); if (b) b.textContent = 'Play'; }
function cuGo(pass, u) {
  const np = cuPasses(), m = cuMoving().length;
  pass = clamp(Math.round(pass), 1, np); u = clamp(u, 0, m);
  S.custom.play = pass >= np && u >= m ? null : { pass, u };
  cuBarSync(); touch();
}
function cuPlayFrame(now) {
  CUI.raf = 0;
  if (!CUI.playing || !cuOn()) { cuPlayStop(); return; }
  const at = cuPlayAt(), m = cuMoving().length, dt = Math.min((now - CUI.last) / 1000, 0.1);
  CUI.last = now;
  let u = at.u + dt / 1.6;   // one step in 1.6 seconds
  if (u >= m) { u = m; cuPlayStop(); }
  cuGo(at.pass, u);
  if (CUI.playing) CUI.raf = requestAnimationFrame(cuPlayFrame);
}
function cuBarSync() {
  if (!cuOn() || !$('cuAt')) return;
  const at = cuPlayAt(), mov = cuMoving(), m = mov.length, np = cuPasses(), lead = cuLead(), steps = S.custom.steps;
  const sig = [at.pass, at.u, at.end, np, lead, S.iter, S.custom.bail, S.custom.rev, CUI.playing].join('|');
  if (sig === CUI.barSig) return;
  CUI.barSig = sig;
  const it = $('cuIt'), all = $('cuItAll'), slider = $('cuAt');
  it.min = 1 + lead; it.max = np + lead;
  if (document.activeElement !== it) it.value = at.pass + lead;
  if (document.activeElement !== all) all.value = S.iter;
  slider.max = Math.max(m, 1); slider.disabled = !m;
  if (Math.abs(+slider.value - at.u) > 1e-4) slider.value = at.u;
  $('cuEnd').classList.toggle('is-on', at.end); $('cuEnd').setAttribute('aria-pressed', String(at.end));
  for (const id of ['cuPlay', 'cuStepPrev', 'cuStepNext']) $(id).disabled = !m;
  if (document.activeElement !== $('cuBail')) $('cuBail').value = cuShort(S.custom.bail);
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
  document.body.classList.toggle('is-custom', on);
  $('cuBar').hidden = $('cuDock').hidden = !on;
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
</div>`;
  $('cuDock').innerHTML = `<div class="cu-tools-row">
  <span class="cu-group"><select id="cuAddSel" aria-label="The kind of step to add">${CU_GROUPS.map(g => `<optgroup label="${g}">${Object.entries(CU_BLOCKS).filter(([, B]) => B.group === g).map(([k, B]) => opt(k, B.title)).join('')}</optgroup>`).join('')}</select><button class="btn" id="cuAddBtn" type="button">Add step</button></span>
  <span class="cu-group"><select id="cuStart" aria-label="A rule to start again from">${CU_STARTS.map((s, k) => opt(k, s.name)).join('')}</select><button class="btn" id="cuStartBtn" type="button" title="Puts these steps in the place of yours. Undo brings yours back.">Load</button></span>
  <button class="btn" id="cuUndo" type="button" disabled>Undo</button>
  <span class="cu-group"><label class="label" for="cuN" title="The Power dial of the page. A step whose menu says “n (Power dial)” follows it.">Power n</label><input type="number" id="cuN" class="cu-in cu-nbox" step="0.1"></span>
</div>
<p class="note" id="cuSay" role="status" hidden></p>
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
    const b = e.target.closest('.cu-tool'), { i, st } = b ? at(e) : {};
    if (!st) return;
    cuSay('');
    const act = b.dataset.act;
    if (act === 'break') {
      let parts;
      try { parts = st.kind === 'formula' ? cuSplit(st.p.text, cuProgram().scopes[st.id] || [], cuTaken(C.steps)) : cuBroken(st, cuTaken(C.steps)); }
      catch (err) { cuSay('This step cannot be broken down yet: ' + err.message); return; }
      if (!parts) { cuSay('This step is one operation already.'); return; }
      if (C.steps.length - 1 + parts.length > CU_MAX_STEPS) { cuSay(`A rule can hold ${CU_MAX_STEPS} steps, and breaking this one down would pass that.`); return; }
      cuSnap();
      C.steps.splice(i, 1, ...parts.map(x => Object.assign(cuStepOf(x.kind, x.p, C.next++), { on: st.on !== false })));
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
  $('cuStartBtn').addEventListener('click', () => {
    const k = +$('cuStart').value, steps = cuStartSteps(k);
    cuSnap(); cuUse({ steps, next: steps.length + 1, bail: CU_STARTS[k].bail || CU_BAIL });
    cuSay('Loaded. Undo brings your own steps back.' + (CU_STARTS[k].say ? ' ' + CU_STARTS[k].say : ''));
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
  $('cuAt').addEventListener('input', () => { cuPlayStop(); cuGo(cuPlayAt().pass, +$('cuAt').value); });
  $('cuTicks').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { cuPlayStop(); cuGo(cuPlayAt().pass, +b.dataset.u); } });
  const bail = v => { if (isFinite(+v) && +v > 0) { S.custom.bail = cuBailOf(v); cuStore(); cuBarSync(); touch(); } };
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
  customSync();
}
