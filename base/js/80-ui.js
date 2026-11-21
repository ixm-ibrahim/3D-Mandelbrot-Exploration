let cardTimer = 0;
function refresh(slow) {
  const a = ap(), N = fmtN(S.n);
  $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = S.mode !== 'k';
  ['secApproach', 'secEq', 'secMod'].forEach(id => { $(id).hidden = S.mode === 'k'; });
  document.querySelectorAll('.rule').forEach((el, i) => el.classList.toggle('is-on', i === S.approach));
  APPROACHES.forEach(x => { $('f-' + x.id).textContent = x.formula(S.param[x.id], S.n); });
  $('cap2d').textContent = `The plane. Angles are multiplied by ${N}, so every circle lands as a circle ${N} times the size. Nothing is squashed or flipped.`;
  $('cap3d').textContent = `${a.name}. A shape-keeping rule would turn each circle into a circle ${N} times the size. Dashed outlines have landed mirror-reversed, and the brass stubs mark the axis this approach singles out. Drag to turn.`;
  buildStep3d(); drawStep2d();
  clearTimeout(cardTimer);
  if (slow) cardTimer = setTimeout(updateCard, 140); else updateCard();
  touch();
}
function applyEquation() {
  const eq = $('eq').value.trim() || 'z', z0 = $('z0').value.trim() || '0', err = $('eqErr');
  try { compileFormula(eq, true, false); compileFormula(z0, false, false); }
  catch (e) { err.textContent = e.message; err.hidden = false; return false; }
  err.hidden = true;
  S.eq = eq; S.z0 = z0;
  $('eqPreset').value = String(PRESETS.findIndex(p => p.eq === eq && p.z0 === z0));
  touch();
  return true;
}
function boot() {
  initState();
  // approaches, each with its own formula, note and controls
  APPROACHES.forEach((r, i) => {
    const el = document.createElement('div');
    el.className = 'rule';
    el.innerHTML = `<label class="rule-head"><input type="radio" name="approach" id="ap-${r.id}" value="${i}"${i === S.approach ? ' checked' : ''}><span class="mark"></span><span class="name">${r.name}</span><span class="tag">${r.tag}</span></label>` +
      `<div class="rule-body"><code id="f-${r.id}"></code><p class="note">${r.about}</p><div id="pd-${r.id}" class="sec-body"></div></div>`;
    $('rules').appendChild(el);
    const inp = el.querySelector('input');
    inp.addEventListener('change', () => { S.approach = i; refresh(false); });
    inp.addEventListener('focus', () => el.classList.toggle('is-focus', inp.matches(':focus-visible')));
    inp.addEventListener('blur', () => el.classList.remove('is-focus'));
    buildControls('pd-' + r.id, r.params || [], S.param[r.id], () => refresh(true), { idPrefix: 'par-' + r.id + '-', group: 'approach' });
  });
  // equation
  PRESETS.forEach((p, i) => $('eqPreset').add(new Option(p.name, i)));
  $('eqPreset').add(new Option('My own formula', -1));
  $('eq').value = S.eq; $('z0').value = S.z0;
  $('eqPreset').addEventListener('change', e => {
    const p = PRESETS[+e.target.value];
    if (!p) return;
    $('eq').value = p.eq; $('z0').value = p.z0;
    if (applyEquation()) { resetCam(p); touch(); }
  });
  for (const id of ['eq', 'z0']) {
    $(id).addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); applyEquation(); } });
    $(id).addEventListener('change', applyEquation);
  }
  addDial('eqDials', 'pow', 'Power n', 2, 10, 0.1, () => S.n, v => { S.n = v; refresh(true); }, { lo: -8, hi: 24 });
  addDial('eqDials', 'iter', 'Iterations', 3, 60, 1, () => S.iter, v => { S.iter = Math.round(v); touch(); }, { hi: 400 });
  // Julia constant
  addDial('juliaDials', 'cx', 'c along x', -2, 2, 0.01, () => S.c[0], v => { S.c[0] = v; touch(); }, { lo: -8, hi: 8 });
  addDial('juliaDials', 'cy', 'c along y', -2, 2, 0.01, () => S.c[1], v => { S.c[1] = v; touch(); }, { lo: -8, hi: 8 });
  addDial('juliaDials', 'cz', 'c along z', -2, 2, 0.01, () => S.c[2], v => { S.c[2] = v; touch(); }, { lo: -8, hi: 8 });
  // Kleinian group
  const K = S.k, kd = (id, label, min, max, step, key, o) => addDial('kleinDials', id, label, min, max, step, () => K[key], v => { K[key] = v; touch(); }, o);
  kd('kmy', 'μ, i part (gap between the walls)', 1.5, 2.3, 0.001, 'my', { lo: 0.5, hi: 4 });
  kd('kmx', 'μ, real part (lean)', -0.5, 0.5, 0.001, 'mx', { lo: -2, hi: 2 });
  kd('kmz', 'μ, j part (lean in depth)', -0.8, 0.8, 0.001, 'mz', { lo: -2, hi: 2 });
  kd('kL', 'L, half the step of the third map', 0.3, 2.5, 0.005, 'L', { lo: 0.05, hi: 8 });
  kd('kiter', 'Depth of the search', 5, 150, 1, 'iter', { hi: 400 });
  kd('kinvr', 'Turning-out sphere, radius', 0.4, 3, 0.01, 'invR', { lo: 0.05, hi: 10 });
  kd('kcx', 'Turning-out sphere, centre x', -1.5, 1.5, 0.005, 'cx', { lo: -6, hi: 6 });
  kd('kcy', 'Turning-out sphere, centre y', 0, 2.2, 0.005, 'cy', { lo: -6, hi: 6 });
  kd('kcz', 'Turning-out sphere, centre z', -1, 1, 0.005, 'cz', { lo: -6, hi: 6 });
  $('k3').addEventListener('change', e => { K.three = e.target.checked; touch(); });
  // modifiers
  const modBoxes = [['absx', () => S.abs[0], v => { S.abs[0] = v; }], ['absy', () => S.abs[1], v => { S.abs[1] = v; }], ['absz', () => S.abs[2], v => { S.abs[2] = v; }], ['flipy', () => S.flip[0], v => { S.flip[0] = v; }], ['flipz', () => S.flip[1], v => { S.flip[1] = v; }]];
  const showMods = () => modBoxes.forEach(([id, get]) => { $(id).checked = !!get(); });
  modBoxes.forEach(([id, , set]) => $(id).addEventListener('change', e => { set(e.target.checked ? 1 : 0); touch(); }));
  const setMods = (a, f) => { S.abs = a; S.flip = f; showMods(); touch(); };
  $('modShip').addEventListener('click', () => setMods([1, 1, 1], [0, 0]));
  $('modBar').addEventListener('click', () => setMods([0, 0, 0], [1, 1]));
  $('modNone').addEventListener('click', () => setMods([0, 0, 0], [0, 0]));
  showMods();
  // slice
  $('cutOn').checked = S.cutOn;
  $('cutOn').addEventListener('change', e => { S.cutOn = e.target.checked; touch(); });
  addDial('cutDials', 'cut', 'Height of the cut', -1.5, 1.5, 0.01, () => S.cut, v => { S.cut = v; S.cutOn = true; $('cutOn').checked = true; touch(); }, { lo: -8, hi: 8 });
  // colour and light
  buildControls('colDials', COLOUR_CONTROLS, S.colour, touch, { idPrefix: 'col-', group: 'colour' });
  addDial('colDials', 'lightAz', 'Light, compass direction', 0, 360, 1, () => S.lightAz, v => { S.lightAz = v; touch(); }, { lo: -720, hi: 720 });
  addDial('colDials', 'lightEl', 'Light, height above the horizon', 5, 90, 1, () => S.lightEl, v => { S.lightEl = v; touch(); }, { lo: -90, hi: 90 });
  // quality
  const Q = S.q, qd = (id, label, min, max, step, key, o) => addDial('qDials', id, label, min, max, step, () => Q[key], v => { Q[key] = v; touch(); }, o);
  qd('qres', 'Resolution, × screen pixels', 0.25, 2, 0.05, 'res', { lo: 0.1, hi: 3 });
  qd('qaa', 'Refining passes', 1, 64, 1, 'aa', { hi: 400 });
  qd('qsteps', 'Ray steps, at most', 60, 700, 10, 'steps', { lo: 20, hi: 3000 });
  qd('qdetail', 'Surface threshold, pixels', 0.2, 4, 0.05, 'detail', { lo: 0.02, hi: 20 });
  qd('qstepk', 'Step size, share of the estimate', 0.2, 1.2, 0.01, 'stepk', { lo: 0.05, hi: 2 });
  qd('qsmooth', 'Slope sampling width, pixels', 0.25, 4, 0.05, 'smooth', { lo: 0.05, hi: 20 });
  $('normals').value = Q.normals;
  $('normals').addEventListener('change', e => { Q.normals = e.target.value; touch(); });
  $('qShadow').addEventListener('change', e => { Q.shadow = e.target.checked; touch(); });
  $('qAO').addEventListener('change', e => { Q.ao = e.target.checked; touch(); });
  const setQ = o => { Object.assign(Q, o); syncControls(); $('qShadow').checked = Q.shadow; $('qAO').checked = Q.ao; touch(); };
  $('qFast').addEventListener('click', () => setQ({ res: 0.75, aa: 3, steps: 160, detail: 1.25, shadow: false, ao: true }));
  $('qBal').addEventListener('click', () => setQ({ res: 1, aa: 12, steps: 260, detail: 1, shadow: true, ao: true }));
  $('qFine').addEventListener('click', () => setQ({ res: 1.5, aa: 32, steps: 450, detail: 0.7, shadow: true, ao: true }));
  // mode
  $('mode-' + S.mode).checked = true;
  for (const m of ['m', 'j', 'k']) $('mode-' + m).addEventListener('change', () => { S.mode = m; resetCam(); refresh(false); });

  readTheme(); buildCard(); initGL(); bindView(); resetCam();
  hooks.view.push(drawTriad, drawStep3d);
  const retheme = () => { readTheme(); drawStep2d(); touch(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  new ResizeObserver(() => { drawStep2d(); touch(); }).observe(stage);
  new ResizeObserver(() => { drawStep2d(); viewChanged(); }).observe($('step2d'));
  refresh(false);
}
