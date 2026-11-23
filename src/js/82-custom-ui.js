// The custom approach on the page: the list of steps with its tools (in the panel of the approach, #pd-custom), the
// button that chooses the approach, and the figure that plays one pass of the steps on a ball. The rule itself is
// in 12-custom.js; this file only changes S.custom and shows it.
const CUI = {
  undo: [],          // earlier lists of steps, as text, newest last
  rangeHot: false,   // a slider of a step is being dragged (one undo entry for the whole drag)
  before: 0,         // the approach that was chosen before the custom one (the button goes back to it)
};
const cuEsc = t => String(t).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const cuStepAt = id => S.custom.steps.findIndex(s => String(s.id) === String(id));
const cuShort = x => String(+(+x).toFixed(4));
const CU_HELP = `<p class="note">A formula step is one line, <code>name = formula</code>. The name <code>z</code> is the point: a line that starts <code>z =</code> moves it. Any other name is yours and can be used in every step after it.</p>
<p class="note"><b>Given:</b> <code>z</code> the point, <code>c</code>, <code>n</code> the power, <code>pi</code>, and from the orbit <code>first</code> (its first point), <code>last</code> (the point of the step before), <code>mean</code> (the average of its points so far) and <code>count</code> (which step this is).</p>
<p class="note"><b>Kinds:</b> a number, a point <code>vec(x, y, z)</code> with the parts <code>.x .y .z</code>, a quaternion <code>quat(w, x, y, z)</code>, and a matrix <code>mat( )</code> of nine numbers row by row, or of three points as its columns.</p>
<p class="note"><b>Signs:</b> <code>+ − * / ^</code>, and <code>&lt; &gt; &lt;= &gt;= == !=</code>, which give 1 or 0. A number times a point stretches it, a matrix times a point moves it, and two quaternions multiply as quaternions.</p>
<p class="note"><b>Numbers:</b> <code>sin cos tan asin acos atan atan2(y, x) sinh cosh tanh atanh exp log sqrt abs floor ceil round fract sign min max mod pow clamp(x, lo, hi) mix(a, b, t) step smoothstep rad(degrees) deg(radians) if(test, a, b)</code>. Angles are in radians: write <code>rad(90)</code> for 90°.</p>
<p class="note"><b>Points:</b> <code>len dot cross unit dist abs each(a, b) flat(v) lon(v) lat(v) sph(length, lon, lat) rot(v, axis, angle) invert(v, centre, radius) mirror(v, normal) cpow(v, n) conj(v)</code>.</p>
<p class="note"><b>Quaternions and matrices:</b> <code>asquat(v)</code> reads a point as x + yi + zj and <code>aspoint(q)</code> reads it back; <code>quat(v) vec(q) re(q) conj(q) inv(q) q^n qrot(axis, angle) turn(v, q)</code>; <code>rotmat(axis, angle) transpose(m) det(m) inv(m)</code>.</p>`;

// One setting of a step, as a row of the step's body.
function cuRow(st, sp, at) {
  const id = `cu-${st.id}-${sp.key}`, val = cuEsc(st.p[sp.key] === undefined ? sp.def : st.p[sp.key]), lab = cuEsc(sp.label);
  const text = `<input type="text" id="${id}" class="cu-in" data-key="${sp.key}" value="${val}" spellcheck="false" autocomplete="off" autocapitalize="off">`;
  let box;
  if (sp.type === 'choice') box = `<select id="${id}" class="cu-in" data-key="${sp.key}">${sp.options.map(o => `<option value="${o[0]}"${o[0] === st.p[sp.key] ? ' selected' : ''}>${cuEsc(o[1])}</option>`).join('')}</select>`;
  else if (sp.type === 'vec') box = `<div class="cu-pair">${text}<select class="cu-pick" data-pick="${sp.key}" aria-label="Choices for ${lab}" title="Choices for this setting. Any formula that gives a point can be typed in the box."><option value="">Pick…</option>${sp.picks.map(o => `<option value="${cuEsc(o[1])}">${cuEsc(o[0])}</option>`).join('')}</select></div>`;
  else if (sp.type === 'num' && !sp.bare) box = `<div class="cu-pair">${text}<input type="range" class="cu-range" data-range="${sp.key}" aria-label="${lab}, slider"></div>`;
  else box = text;
  return `<div class="cu-row${sp.type === 'text' ? ' cu-row-text' : ''}" data-row="${sp.key}"><label class="label" for="${id}">${lab}</label>${box}</div>`;
}
// The slider of a number setting shows only while the setting is a plain number, and reaches as far as that number.
function cuRangeSync(li, st) {
  const B = CU_BLOCKS[st.kind];
  li.querySelectorAll('.cu-range').forEach(r => {
    const sp = B.params.find(x => x.key === r.dataset.range), raw = st.p[sp.key];
    r.hidden = !cuIsNum(raw);
    if (r.hidden) return;
    let lo = sp.min, hi = sp.max;
    if (sp.ranged) { lo = cuNum(st.p.min); hi = cuNum(st.p.max); if (!(hi > lo)) { lo = 0; hi = 1; } }
    const x = cuNum(raw);
    lo = Math.min(lo, x); hi = Math.max(hi, x);
    r.min = lo; r.max = hi; r.step = sp.ranged ? (hi - lo) / 200 : sp.step; r.value = x;
  });
}
function cuStepEl(st, i, count) {
  const B = CU_BLOCKS[st.kind], li = document.createElement('li'), k = i + 1;
  li.className = 'cu-step' + (st.on === false ? ' is-off' : ''); li.dataset.id = st.id;
  const tool = (act, label, title, text, off) => `<button type="button" class="cu-tool" data-act="${act}" aria-label="${label}" title="${title}"${off ? ' disabled' : ''}>${text}</button>`;
  li.innerHTML = `<div class="cu-head"><label class="cu-on" title="Switch this step off to see the solid without it."><input type="checkbox" data-act="on"${st.on === false ? '' : ' checked'} aria-label="Step ${k} is on"><span class="cu-no">${k}</span></label>` +
    `<span class="cu-title">${cuEsc(B.title)}</span><span class="cu-tools">` +
    tool('up', `Move step ${k} up`, 'Move up', '↑', i === 0) + tool('down', `Move step ${k} down`, 'Move down', '↓', i === count - 1) +
    (B.plain ? '' : tool('break', `Break step ${k} down`, 'Show this step as the plain formulas it is made of. Each becomes a step you can change.', 'Break down')) +
    tool('remove', `Remove step ${k}`, 'Remove', '✕') + '</span></div>' +
    `<div class="cu-body${B.grid ? ' cu-grid' : ''}">${B.params.map((sp, at) => cuRow(st, sp, at)).join('')}</div><p class="err cu-err" hidden></p>`;
  cuRangeSync(li, st);
  return li;
}
function cuRender() {
  const host = $('cuSteps'), steps = S.custom.steps;
  host.textContent = '';
  steps.forEach((st, i) => host.appendChild(cuStepEl(st, i, steps.length)));
  $('cuEmpty').hidden = steps.length > 0;
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
const cuText = () => JSON.stringify(S.custom.steps.map(s => ({ kind: s.kind, on: s.on !== false, p: s.p })));
function cuSnap() {
  const t = cuText();
  if (CUI.undo[CUI.undo.length - 1] !== t) CUI.undo.push(t);
  if (CUI.undo.length > 40) CUI.undo.shift();
}
// After the steps changed. render: the list itself changed (a step added, moved, removed), not only a setting.
function cuChanged(render) {
  S.custom.rev = (S.custom.rev || 0) + 1;
  if (render) cuRender();
  cuStore();
  cuErrors();
  $('cuUndo').disabled = CUI.undo.length === 0;
  if ($('cuTextBox').open) $('cuText').value = cuText();
  if (ap().id === 'custom') uiApproachParam();
  cuFigDirty();
}
function cuUse(steps) {
  S.custom.steps = steps; S.custom.next = steps.length + 1;
  cuChanged(true);
}
function cuSay(text) { const p = $('cuSay'); p.textContent = text || ''; p.hidden = !text; }

function customInit() {
  const host = $('pd-custom');
  host.innerHTML = `<div class="cu-fig" id="cuFig">
  <p class="label">One pass of your steps, played on a ball</p>
  <canvas id="cuBall" tabindex="0" aria-label="A ball as each of your steps moves it. Drag or use the arrow keys to turn it."></canvas>
  <div class="cu-fig-bar"><button class="btn" id="cuPlay" type="button">Play</button><input type="range" id="cuAt" min="0" max="1" step="0.005" value="0" aria-label="How far through the steps the ball has come"></div>
  <p class="note" id="cuAtWords"></p>
  <div class="cu-row"><label class="label" for="cuBallR">Size of the ball</label><div class="cu-pair"><output id="cuBallRv" class="cu-out"></output><input type="range" id="cuBallR" class="cu-range" min="0.2" max="2.5" step="0.01"></div></div>
  <p class="note" id="cuFigNote"></p>
</div>
<p class="note">The picture is the solid your steps make. A step works on the point z and hands it to the next one. Switch a step off with its tick to see the solid without it, and move a slider to see the solid change.</p>
<ol class="cu-steps" id="cuSteps"></ol>
<p class="note" id="cuEmpty" hidden>There are no steps, so every point stays where it is. Add a step below, or load a rule to start from.</p>
<div class="field"><label class="label" for="cuAddSel">Add a step at the end</label><div class="cu-pair"><select id="cuAddSel">${CU_GROUPS.map(g => `<optgroup label="${g}">${Object.entries(CU_BLOCKS).filter(([, B]) => B.group === g).map(([k, B]) => `<option value="${k}">${cuEsc(B.title)}</option>`).join('')}</optgroup>`).join('')}</select><button class="btn" id="cuAddBtn" type="button">Add</button></div></div>
<div class="field"><label class="label" for="cuStart">Start again from a rule</label><div class="cu-pair"><select id="cuStart">${CU_STARTS.map((s, k) => `<option value="${k}">${cuEsc(s.name)}</option>`).join('')}</select><button class="btn" id="cuStartBtn" type="button" title="Puts these steps in the place of yours. Undo brings yours back.">Load</button></div></div>
<div class="row-btns"><button class="btn" id="cuUndo" type="button" disabled>Undo</button></div>
<p class="note" id="cuSay" role="status" hidden></p>
<details class="cu-more"><summary>What a formula can use</summary>${CU_HELP}</details>
<details class="cu-more" id="cuTextBox"><summary>Your steps as text</summary>
  <p class="note">Copy this text to keep a rule or to send it to someone. To use a rule you were sent, paste it here and press the button.</p>
  <textarea id="cuText" rows="5" spellcheck="false" aria-label="Your steps as text"></textarea>
  <div class="row-btns"><button class="btn" id="cuTextUse" type="button">Use this text</button></div>
</details>`;
  const list = $('cuSteps'), C = S.custom;
  // a setting typed or chosen
  list.addEventListener('change', e => {
    const li = e.target.closest('.cu-step'), i = li ? cuStepAt(li.dataset.id) : -1, st = C.steps[i], t = e.target;
    if (!st) return;
    cuSay('');
    if (t.dataset.act === 'on') { cuSnap(); st.on = t.checked; li.classList.toggle('is-off', !t.checked); cuChanged(false); return; }
    if (t.dataset.range) { CUI.rangeHot = false; return; }
    if (t.dataset.pick) {
      if (!t.value) return;
      cuSnap();
      st.p[t.dataset.pick] = t.value; li.querySelector(`[data-key="${t.dataset.pick}"]`).value = t.value; t.selectedIndex = 0;
      cuChanged(false); cuFigShow(st.id); return;
    }
    if (t.dataset.key) {
      const sp = CU_BLOCKS[st.kind].params.find(x => x.key === t.dataset.key);
      cuSnap();
      st.p[sp.key] = t.value.trim() || sp.def; t.value = st.p[sp.key];
      cuRangeSync(li, st);
      cuChanged(false); cuFigShow(st.id);
    }
  });
  // a slider dragged: the number changes and nothing else, so the picture follows at once
  list.addEventListener('input', e => {
    const t = e.target, li = t.closest('.cu-step'), st = li && t.dataset.range ? C.steps[cuStepAt(li.dataset.id)] : null;
    if (!st) return;
    if (!CUI.rangeHot) { cuSnap(); CUI.rangeHot = true; }
    st.p[t.dataset.range] = cuShort(t.value);
    li.querySelector(`[data-key="${t.dataset.range}"]`).value = st.p[t.dataset.range];
    cuChanged(false); cuFigShow(st.id);
  });
  list.addEventListener('click', e => {
    const b = e.target.closest('.cu-tool'), li = b && b.closest('.cu-step'), i = li ? cuStepAt(li.dataset.id) : -1, st = C.steps[i];
    if (!st) return;
    cuSay('');
    const act = b.dataset.act;
    if (act === 'break') {
      let lines;
      try { lines = cuBroken(st, cuTaken(C.steps)); } catch (err) { cuSay('This step cannot be broken down yet: ' + err.message); return; }
      if (!lines) return;
      if (C.steps.length - 1 + lines.length > CU_MAX_STEPS) { cuSay(`A rule can hold ${CU_MAX_STEPS} steps, and breaking this one down would pass that.`); return; }
      cuSnap();
      C.steps.splice(i, 1, ...lines.map(p => ({ id: C.next++, kind: 'formula', on: st.on !== false, p })));
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
    const st = cuStepOf($('cuAddSel').value, {}, C.next++);
    if (st.kind === 'slider') { const taken = cuTaken(C.steps); let name = 't', k = 1; while (taken.includes(name)) name = 't' + (++k); st.p.name = name; }
    C.steps.push(st);
    cuChanged(true); cuFigShow(st.id);
    const li = list.lastElementChild;
    if (li) { li.scrollIntoView({ block: 'nearest' }); const f = li.querySelector('.cu-in'); if (f) f.focus({ preventScroll: true }); }
  });
  $('cuStartBtn').addEventListener('click', () => {
    const k = +$('cuStart').value;
    cuSnap(); cuUse(cuStartSteps(k));
    cuSay('Loaded. Undo brings your own steps back.' + (CU_STARTS[k].say ? ' ' + CU_STARTS[k].say : ''));
  });
  $('cuUndo').addEventListener('click', () => {
    const t = CUI.undo.pop();
    if (t === undefined) return;
    cuSay('');
    cuUse(cuClean(JSON.parse(t)) || []);
  });
  $('cuTextBox').addEventListener('toggle', () => { if ($('cuTextBox').open) $('cuText').value = cuText(); });
  $('cuTextUse').addEventListener('click', () => {
    let steps = null;
    try { steps = cuClean(JSON.parse($('cuText').value)); } catch (err) { /* not a rule */ }
    if (!steps) { cuSay('That text is not a rule: nothing was changed. A rule is the text this box shows for your own steps.'); return; }
    cuSnap(); cuUse(steps); cuSay('The steps from the text are in use. Undo brings the earlier ones back.');
  });
  // the button under the Approach menu: to the custom approach, and back to the approach before it
  const mine = APPROACHES.findIndex(a => a.id === 'custom');
  $('apCustomBtn').addEventListener('click', () => {
    if (S.approach === mine) S.approach = CUI.before === mine ? 0 : CUI.before;
    else { CUI.before = S.approach; S.approach = mine; }
    uiApMenu(false);
    refresh();
  });
  cuRender(); cuErrors();
  cuFigInit();
}

// The figure. A ball of points takes one pass of the steps, and the figure shows it after each step, sliding
// from one to the next. The ball is a mesh; where each of its corners is after every step is worked out here, in
// JavaScript (cuRun), and the picture is drawn with a small program of its own. A point that a step throws
// further than CU_FIG_FAR from the middle is drawn at that distance.
const CU_FIG_FAR = 6, CU_FIG_NU = 96, CU_FIG_NV = 48;
const CUF = { gl: null, prog: null, loc: {}, mesh: null, frames: [], ids: [], far: 1, at: 0, yaw: -0.7, pitch: 0.45, sig: '', dirty: true, raf: 0,
  playing: false, last: 0, bufA: null, bufB: null, axes: null, pair: -1, drag: null, tried: false };
const cuFigOn = () => ap().id === 'custom' && S.mode !== 'k' && !$('secApproach').hidden && $('secApproach').open;
function cuFigMesh() {
  if (CUF.mesh) return CUF.mesh;
  const nu = CU_FIG_NU, nv = CU_FIG_NV, count = (nu + 1) * (nv + 1), dir = new Float32Array(count * 3), col = new Float32Array(count * 3), idx = new Uint16Array(nu * nv * 6);
  for (let j = 0, k = 0; j <= nv; j++) for (let i = 0; i <= nu; i++, k++) {
    const lo = 2 * PI * i / nu, la = PI * (j / nv - 0.5), cl = Math.cos(la);
    dir.set([cl * Math.cos(lo), cl * Math.sin(lo), Math.sin(la)], 3 * k);
    // the colour says where a patch started: its hue the way round, lighter the higher up, in a chequer of patches
    const h = 6 * (i % nu) / nu, light = 0.42 + 0.26 * j / nv + (((i >> 3) + (j >> 3)) % 2 ? 0.12 : 0), x = 1 - Math.abs(h % 2 - 1);
    const rgb = h < 1 ? [1, x, 0] : h < 2 ? [x, 1, 0] : h < 3 ? [0, 1, x] : h < 4 ? [0, x, 1] : h < 5 ? [x, 0, 1] : [1, 0, x];
    col.set(rgb.map(u => light + 0.34 * (u - 0.5)), 3 * k);
  }
  for (let j = 0, k = 0; j < nv; j++) for (let i = 0; i < nu; i++) {
    const a = j * (nu + 1) + i, b = a + nu + 1;
    idx.set([a, a + 1, b, a + 1, b + 1, b], k); k += 6;
  }
  return (CUF.mesh = { count, dir, col, idx });
}
// Where every corner of the ball is after each step that is on. frames[0] is the ball itself.
function cuFigFrames() {
  const M = cuFigMesh(), P = cuProgram(), r = S.custom.ball.r, jul = S.mode === 'j', n = S.n, car = CARRY.custom;
  const ids = P.run.filter(s => s.sw < 0 || P.K[s.sw] > 0.5).map(s => s.id);
  const frames = Array.from({ length: ids.length + 1 }, () => new Float32Array(M.count * 3));
  let far = r;
  for (let i = 0; i < M.count; i++) {
    const z0 = [M.dir[3 * i] * r, M.dir[3 * i + 1] * r, M.dir[3 * i + 2] * r], c = jul ? S.c.slice(0, 3) : z0;
    frames[0].set(z0, 3 * i);
    let k = 0;
    cuRun(z0, c, n, car.step(car.start(), z0, c), (id, z) => {
      let l = Math.hypot(z[0], z[1], z[2]), p = z;
      if (!(l <= CU_FIG_FAR)) { p = isFinite(l) && l > 0 ? scl(z, CU_FIG_FAR / l) : [CU_FIG_FAR, 0, 0]; l = CU_FIG_FAR; }
      if (l > far) far = l;
      frames[++k].set(p, 3 * i);
    });
  }
  // arcs[k]: step k + 1 changes no point's length by more than a thousandth
  const arcs = ids.map((id, k) => { const A = frames[k], B = frames[k + 1]; for (let j = 0; j < A.length; j += 3) { const a = Math.hypot(A[j], A[j + 1], A[j + 2]), b = Math.hypot(B[j], B[j + 1], B[j + 2]); if (Math.abs(a - b) > 1e-3 * Math.max(a, b, 1e-6)) return false; } return true; });
  CUF.frames = frames; CUF.ids = ids; CUF.arcs = arcs; CUF.far = far; CUF.pair = -1;
}
function cuFigStart() {
  if (CUF.tried) return !!CUF.gl;
  CUF.tried = true;
  const cv = $('cuBall'), gl = cv.getContext('webgl2', { antialias: true, alpha: false });
  if (!gl) { $('cuFigNote').textContent = 'This browser could not start WebGL 2, so the ball cannot be drawn.'; cv.hidden = true; return false; }
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; };
  const p = gl.createProgram();
  gl.attachShader(p, sh(gl.VERTEX_SHADER, `#version 300 es
in vec3 aA, aB, aCol;
uniform float uT, uScale, uAspect, uArc;
uniform mat3 uView;
out vec3 vP, vCol;
void main(){
  vec3 p = mix(aA, aB, uT);
  // a step that leaves every length alone is a turn: its points go round, not straight across
  if (uArc > 0.5){ float la = length(aA), lb = length(aB), lp = length(p); if (lp > 1e-4 * max(la, lb)) p *= mix(la, lb, uT) / lp; }
  vec3 q = uView * p * uScale;
  vP = q; vCol = aCol;
  gl_Position = vec4(q.x / uAspect, q.y, -0.12 * q.z, 1.0);
}`));
  gl.attachShader(p, sh(gl.FRAGMENT_SHADER, `#version 300 es
precision highp float;
in vec3 vP, vCol;
uniform vec3 uLight;
uniform float uLine;
out vec4 o;
void main(){
  if (uLine > 0.5){ o = vec4(vCol, 1.0); return; }
  vec3 nrm = normalize(cross(dFdx(vP), dFdy(vP)));
  if (nrm.z < 0.0) nrm = -nrm;
  float lit = 0.34 + 0.66 * max(dot(nrm, uLight), 0.0) + 0.25 * pow(max(dot(nrm, normalize(uLight + vec3(0.0, 0.0, 1.0))), 0.0), 24.0);
  o = vec4(vCol * lit, 1.0);
}`));
  gl.bindAttribLocation(p, 0, 'aA'); gl.bindAttribLocation(p, 1, 'aB'); gl.bindAttribLocation(p, 2, 'aCol');
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) { console.error('The ball figure did not build: ' + gl.getProgramInfoLog(p)); cv.hidden = true; return false; }
  const M = cuFigMesh(), buf = (data, kind = gl.ARRAY_BUFFER, use = gl.STATIC_DRAW) => { const b = gl.createBuffer(); gl.bindBuffer(kind, b); gl.bufferData(kind, data, use); return b; };
  CUF.gl = gl; CUF.prog = p;
  for (const name of ['uT', 'uScale', 'uAspect', 'uArc', 'uView', 'uLight', 'uLine']) CUF.loc[name] = gl.getUniformLocation(p, name);
  CUF.bufA = buf(new Float32Array(M.count * 3), gl.ARRAY_BUFFER, gl.DYNAMIC_DRAW); CUF.bufB = buf(new Float32Array(M.count * 3), gl.ARRAY_BUFFER, gl.DYNAMIC_DRAW);
  CUF.col = buf(M.col); CUF.idx = buf(M.idx, gl.ELEMENT_ARRAY_BUFFER);
  CUF.axes = buf(new Float32Array(18), gl.ARRAY_BUFFER, gl.DYNAMIC_DRAW); CUF.axesCol = buf(new Float32Array(18), gl.ARRAY_BUFFER, gl.DYNAMIC_DRAW);
  cv.addEventListener('webglcontextlost', e => { e.preventDefault(); CUF.gl = null; });
  return true;
}
// The words under the slider, and the step of the list that the slider stands in.
function cuFigWords() {
  const N = CUF.ids.length, at = clamp(CUF.at, 0, N), k = Math.min(Math.floor(at), N - 1), whole = Math.abs(at - Math.round(at)) < 1e-6;
  const name = j => { const i = cuStepAt(CUF.ids[j]), st = S.custom.steps[i]; const t = st ? CU_BLOCKS[st.kind].title : ''; return st ? `step ${i + 1}, ${t[0].toLowerCase() + t.slice(1)}` : 'a step'; };
  $('cuAtWords').textContent = N === 0 ? 'No step is on, so the ball stays as it is.'
    : whole && Math.round(at) === 0 ? 'The ball before the first step. Its colours stay with its points, so a patch can be followed.'
    : whole ? `After ${name(Math.round(at) - 1)}.` + (Math.round(at) === N ? ' That is one whole pass.' : '')
    : `During ${name(k)}.`;
  const now = whole ? (Math.round(at) > 0 ? CUF.ids[Math.round(at) - 1] : null) : CUF.ids[k];
  document.querySelectorAll('#cuSteps .cu-step').forEach(li => li.classList.toggle('is-now', now !== null && String(now) === li.dataset.id));
}
function cuFigDraw() {
  const cv = $('cuBall');
  if (!cuFigOn() || !cuFigStart() || !CUF.gl) return;
  const sig = [cuProgram().key, [...cuProgram().K].join(','), S.custom.ball.r, S.mode, S.mode === 'j' ? S.c.join(',') : '', S.n].join('|');
  if (CUF.dirty || sig !== CUF.sig) { CUF.sig = sig; CUF.dirty = false; cuFigFrames(); }
  const gl = CUF.gl, N = CUF.ids.length, L = CUF.loc, M = CUF.mesh;
  const slider = $('cuAt');
  if (+slider.max !== Math.max(N, 1)) slider.max = Math.max(N, 1);
  slider.disabled = N === 0;
  CUF.at = clamp(CUF.at, 0, N);
  if (Math.abs(+slider.value - CUF.at) > 1e-4) slider.value = CUF.at;
  $('cuPlay').disabled = N === 0;
  $('cuBallRv').textContent = cuShort(S.custom.ball.r);
  if (Math.abs(+$('cuBallR').value - S.custom.ball.r) > 1e-6) $('cuBallR').value = S.custom.ball.r;
  const dpr = Math.min(devicePixelRatio || 1, 2), w = Math.max(2, Math.round(cv.clientWidth * dpr)), h = Math.max(2, Math.round(cv.clientHeight * dpr));
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
  const k = Math.min(Math.floor(CUF.at), Math.max(N - 1, 0)), u = N ? CUF.at - k : 0, t = u * u * (3 - 2 * u);
  if (CUF.pair !== k) {
    CUF.pair = k;
    gl.bindBuffer(gl.ARRAY_BUFFER, CUF.bufA); gl.bufferSubData(gl.ARRAY_BUFFER, 0, CUF.frames[k]);
    gl.bindBuffer(gl.ARRAY_BUFFER, CUF.bufB); gl.bufferSubData(gl.ARRAY_BUFFER, 0, CUF.frames[Math.min(k + 1, N)]);
  }
  const bg = theme.stage, cy = Math.cos(CUF.yaw), sy = Math.sin(CUF.yaw), cp = Math.cos(CUF.pitch), sp = Math.sin(CUF.pitch);
  const scale = 0.9 / Math.max(CUF.far, 1.2);
  gl.viewport(0, 0, w, h);
  gl.clearColor(bg[0], bg[1], bg[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
  gl.useProgram(CUF.prog);
  // screen right, screen up and the direction to the eye, as the columns of the transpose (the upright axis is z)
  gl.uniformMatrix3fv(L.uView, false, [cy, -sy * sp, sy * cp, sy, cy * sp, -cy * cp, 0, cp, sp]);
  gl.uniform1f(L.uScale, scale); gl.uniform1f(L.uAspect, w / h); gl.uniform1f(L.uT, t); gl.uniform1f(L.uArc, CUF.arcs[k] ? 1 : 0);
  gl.uniform3f(L.uLight, -0.45, 0.6, 0.66);
  const attr = (at, b) => { gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(at); gl.vertexAttribPointer(at, 3, gl.FLOAT, false, 0, 0); };
  attr(0, CUF.bufA); attr(1, CUF.bufB); attr(2, CUF.col);
  gl.uniform1f(L.uLine, 0);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, CUF.idx);
  gl.drawElements(gl.TRIANGLES, M.idx.length, gl.UNSIGNED_SHORT, 0);
  // the three axes, as long as the picture is wide: x and y in the flat plane, z upright
  const far = 0.98 / scale, ink = theme.dark ? 0.62 : 0.4, lines = new Float32Array([-far, 0, 0, far, 0, 0, 0, -far, 0, 0, far, 0, 0, 0, -far, 0, 0, far]);
  gl.bindBuffer(gl.ARRAY_BUFFER, CUF.axes); gl.bufferSubData(gl.ARRAY_BUFFER, 0, lines);
  gl.bindBuffer(gl.ARRAY_BUFFER, CUF.axesCol); gl.bufferSubData(gl.ARRAY_BUFFER, 0, new Float32Array(18).fill(ink));
  attr(0, CUF.axes); attr(1, CUF.axes); attr(2, CUF.axesCol);
  gl.uniform1f(L.uLine, 1); gl.uniform1f(L.uArc, 0);
  gl.drawArrays(gl.LINES, 0, 6);
  cuFigWords();
}
function cuFigFrame(now) {
  CUF.raf = 0;
  if (CUF.playing) {
    const N = CUF.ids.length, dt = Math.min((now - CUF.last) / 1000, 0.1);
    CUF.last = now;
    CUF.at += dt / 1.8;   // one step in 1.8 seconds
    if (CUF.at >= N) { CUF.at = N; CUF.playing = false; $('cuPlay').textContent = 'Play'; }
  }
  cuFigDraw();
  if (CUF.playing) cuFigQueue();
}
function cuFigQueue() { if (!CUF.raf) CUF.raf = requestAnimationFrame(cuFigFrame); }
function cuFigDirty() { CUF.dirty = true; cuFigQueue(); }
function cuFigStop() { CUF.playing = false; $('cuPlay').textContent = 'Play'; }
// Put the slider at the end of the step that was just changed, so the ball shows what that step does.
function cuFigShow(id) {
  if (CUF.playing) return;
  const P = cuProgram(), at = P.run.filter(s => s.sw < 0 || P.K[s.sw] > 0.5).findIndex(s => s.id === id);
  if (at >= 0) { CUF.at = at + 1; cuFigQueue(); }
}
function cuFigInit() {
  const cv = $('cuBall');
  $('cuAt').addEventListener('input', () => { cuFigStop(); CUF.at = +$('cuAt').value; cuFigQueue(); });
  $('cuPlay').addEventListener('click', () => {
    if (CUF.playing) { cuFigStop(); return; }
    if (CUF.at >= CUF.ids.length - 1e-6) CUF.at = 0;
    CUF.playing = true; CUF.last = performance.now(); $('cuPlay').textContent = 'Pause';
    cuFigQueue();
  });
  $('cuBallR').addEventListener('input', () => { S.custom.ball.r = +$('cuBallR').value; cuStore(); cuFigDirty(); });
  cv.addEventListener('pointerdown', e => { CUF.drag = { x: e.clientX, y: e.clientY }; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener('pointermove', e => {
    if (!CUF.drag) return;
    CUF.yaw -= (e.clientX - CUF.drag.x) * 0.01; CUF.pitch = clamp(CUF.pitch + (e.clientY - CUF.drag.y) * 0.01, -1.5, 1.5);
    CUF.drag = { x: e.clientX, y: e.clientY };
    cuFigQueue();
  });
  const up = () => { CUF.drag = null; };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('keydown', e => {
    const d = { ArrowLeft: [0.1, 0], ArrowRight: [-0.1, 0], ArrowUp: [0, 0.1], ArrowDown: [0, -0.1] }[e.key];
    if (!d) return;
    e.preventDefault();
    CUF.yaw += d[0]; CUF.pitch = clamp(CUF.pitch + d[1], -1.5, 1.5);
    cuFigQueue();
  });
  $('cuFigNote').textContent = 'In a Julia picture the c of the page is added. In a Mandelbrot picture every point is its own c, so there the ball shows the step that follows the first. A point thrown very far is drawn at the edge of the figure.';
  // the approach, the power, the mode or c changed, the section was opened, or the window changed size
  hooks.refresh.push(cuFigDirty); hooks.view.push(cuFigQueue);
  $('secApproach').addEventListener('toggle', cuFigDirty);
  addEventListener('resize', cuFigQueue);
  cuFigQueue();
}
