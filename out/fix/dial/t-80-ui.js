// ---------- the page: builds every control from the modules' specs and wires it to the state.
// Section groups for resetGroup: 'mandel', 'julia', 'klein', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'.
const UI = {
  col: null,        // the colour controls (a buildControls set)
  kleinSel: null,   // the Kleinian preset drop-down
  cutOn: null,      // the "cut the solid open" checkbox
  fly: null,        // the fly-camera checkbox in the View section
  flyShown: false,  // what that checkbox last showed (the stage switch and the F key change the mode too)
};
const UI_FOV = 0.32, UI_FOV_DEG = 35.49;   // the starting field of view: as the state holds it, and as the dial shows it
const UI_QUALITY = {
  qUltra: { res: 0.5, aa: 1, steps: 90, detail: 2, shadow: false, ao: false, de: 0, normals: 'smooth' },
  qFast: { res: 0.75, aa: 3, steps: 160, detail: 1.25, shadow: false, ao: true, de: 3, normals: 'sharp' },
  qBal: { res: 1, aa: 12, steps: 260, detail: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
  qFine: { res: 1.5, aa: 32, steps: 450, detail: 0.7, shadow: true, ao: true, de: 3, normals: 'sharp' },
};

// After the approach, the power or the mode changed: panels, texts, figures, scorecard, then the picture.
// `slow` is kept for callers that pass it; the scorecard now spreads its own work over frames.
function refresh(slow) {
  const k = S.mode === 'k';
  $('mandelPanel').hidden = S.mode !== 'm'; $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = !k;
  ['secApproach', 'secEq', 'secMod'].forEach(id => { $(id).hidden = k; });
  $('mode-' + S.mode).checked = true;
  document.querySelectorAll('.rule').forEach((el, i) => el.classList.toggle('is-on', i === S.approach));
  APPROACHES.forEach((x, i) => {
    $('ap-' + x.id).checked = i === S.approach;
    $('f-' + x.id).textContent = x.formula(S.param[x.id], S.n);
  });
  uiJuliaMark(); uiKleinMark(); uiCollapsePaint();
  buildStep3d(); drawStep2d(); updateCard();
  touch();
  hooks.refresh.forEach(f => f());
}
function applyEquation() {
  const eq = $('eq').value.trim() || 'z', z0 = $('z0').value.trim() || '0', err = $('eqErr');
  try { compileFormula(eq, true, false); compileFormula(z0, false, false); }
  catch (e) { err.textContent = e.message; err.hidden = false; return false; }
  err.hidden = true;
  S.eq = eq; S.z0 = z0;
  uiEqMark();
  touch();
  return true;
}
// Show which equation preset the two formulas now are (or "My own formula"), and that preset's note.
function uiEqMark() {
  const i = PRESETS.findIndex(p => p.eq === S.eq && p.z0 === S.z0), note = $('eqNote');
  $('eqPreset').value = String(i);
  note.textContent = (i >= 0 && PRESETS[i].note) || '';
  note.hidden = !note.textContent;
}

// ---------- Julia points: the shipped list, then the user's own
function uiJuliaList() {
  const host = $('juliaList');
  host.textContent = '';
  const head = text => { const h = document.createElement('p'); h.className = 'label plist-head'; h.textContent = text; host.appendChild(h); };
  const row = (p, del) => {
    const r = document.createElement('div'), b = document.createElement('button');
    r.className = 'plist-row';
    b.type = 'button'; b.className = 'plist-item'; b.textContent = p.name;
    if (p.note) b.title = p.note;
    b.addEventListener('click', () => applyJuliaPreset(p));
    r.appendChild(b);
    if (del) {
      const x = document.createElement('button');
      x.type = 'button'; x.className = 'plist-del'; x.textContent = 'Delete';
      x.setAttribute('aria-label', `Delete the saved point ${p.name}`);
      x.addEventListener('click', () => { juliaDeletePoint(juliaSaved.indexOf(p)); uiJuliaList(); });
      r.appendChild(x);
    }
    r.dataset.c = p.c.join(',');
    host.appendChild(r);
  };
  // the user's own points come first, so they are in sight without scrolling the list
  head('Your saved points');
  juliaSaved.forEach(p => row(p, true));
  if (!juliaSaved.length) {
    const e = document.createElement('p');
    e.className = 'note plist-empty'; e.textContent = 'None yet. Set c with the dials, then press Save this point.';
    host.appendChild(e);
  }
  head('Classic sets');
  JULIA_PRESETS.filter(p => p.source !== 'explored').forEach(p => row(p, false));
  head('Found by exploring');
  JULIA_PRESETS.filter(p => p.source === 'explored').forEach(p => row(p, false));
  uiJuliaMark();
}
// Mark the list entry the Julia point now stands on, and show that entry's note.
function uiJuliaMark() {
  document.querySelectorAll('#juliaList .plist-row').forEach(r => {
    const on = r.dataset.c.split(',').every((x, i) => presetSame(+x, S.c[i]));
    r.classList.toggle('is-on', on);
    r.firstChild.setAttribute('aria-pressed', String(on));
  });
  const at = juliaPresetAt(), note = $('juliaNote');
  const text = at ? (at.note || 'One of your saved points.') : `c = (${S.c.map(x => dialFmt(x)).join(', ')}) is not in the list.`;
  if (note.textContent !== text) note.textContent = text;
}
function uiKleinMark() {
  if (!UI.kleinSel) return;
  UI.kleinSel.sync();
  const i = kleinPresetAt(), note = $('kleinNote'), text = i >= 0 ? KLEIN_PRESETS[i].note : 'Your own settings. Pick an entry above to go back to a known picture.';
  if (note.textContent !== text) note.textContent = text;
}
const uiSections = () => [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden);
function uiCollapsePaint() {
  const open = uiSections().some(d => d.open), b = $('collapseAll'), text = open ? 'Collapse all' : 'Expand all';
  if (b.textContent !== text) b.textContent = text;
}
// The camera mode is also changed on the stage and with the F key: keep the View section's checkbox in step.
function uiViewSync() {
  if (UI.fly && UI.flyShown !== !!S.view.fly) { UI.flyShown = !!S.view.fly; UI.fly.sync(); }
}

function boot() {
  initState();
  juliaSavedLoad();

  // top row: 2D view and collapse all
  addCheck('flatHost', 'extreme', 'Extreme values', isExtreme, setExtreme, { def: false });
  addCheck('flatHost', 'flat', '2D view (the slice at height z only)', () => S.flat, v => { S.flat = !!v; syncControls(); touch(); }, { def: false });
  $('collapseAll').addEventListener('click', () => {
    const open = !uiSections().some(d => d.open);
    uiSections().forEach(d => { d.open = open; });
    uiCollapsePaint();
  });
  document.querySelectorAll('#sections > details.sec').forEach(d => d.addEventListener('toggle', uiCollapsePaint));

  // Mandelbrot options: the Julia mosaic
  buildControls('mandelDials', [
    { type: 'check', key: 'mosaic', label: 'Julia mosaic', def: false, help: 'Fills space with a grid of small Julia sets. Each cell shows the Julia set of the point at its centre, so together they trace the Mandelbrot solid.' },
    { type: 'dial', key: 'mosaicCell', label: 'Mosaic cell size', min: 0.08, max: 1, step: 0.01, def: 0.3, lo: 0.03, hi: 4, when: s => s.mosaic },
  ], S, touch, { idPrefix: 'm-', group: 'mandel' });
  addReset('mandelDials', 'mandel');

  // Julia point
  const cd = (id, label, i, def) => addDial('juliaDials', id, label, -2, 2, 0.01, () => S.c[i], v => { S.c[i] = v; uiJuliaMark(); touch(); }, { lo: -8, hi: 8, xlo: -100, xhi: 100, def, group: 'julia' });
  cd('cx', 'c along x', 0, -1); cd('cy', 'c along y', 1, 0); cd('cz', 'c along z', 2, 0);
  uiJuliaList();
  const save = () => {
    const r = juliaSavePoint($('juliaName').value), note = $('juliaSaveNote');
    note.textContent = !r.ok ? 'The list is full. Delete a saved point first.' : r.kept ? '' : 'Saved for this visit. This browser does not let the page keep it for next time.';
    note.hidden = !note.textContent;
    if (r.ok) { $('juliaName').value = ''; uiJuliaList(); }
  };
  $('juliaSave').addEventListener('click', save);
  $('juliaName').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); save(); } });
  addReset('juliaReset', 'julia', { after: uiJuliaMark });

  // Kleinian group
  // (the labels are upper case, which would print the Greek letter μ as a Latin M: class asis keeps it as typed)
  const K = S.k, kd = (id, label, min, max, step, key, o) => addDial('kleinDials', id, label, min, max, step, () => K[key], v => { K[key] = v; uiKleinMark(); touch(); }, { ...o, group: 'klein' });
  const kHead = { cusp: 'Cusps: pearls that just touch', inside: 'Inside the family: strings that do not close', explored: 'Found by exploring' };
  UI.kleinSel = addSelect('kleinPresetHost', 'kleinPreset', 'Start from', KLEIN_PRESETS.map((p, i) => [i, p.name, kHead[p.source.split(' ')[0]]]),
    kleinPresetAt, i => { applyKleinPreset(KLEIN_PRESETS[i]); uiKleinMark(); }, { def: 0, group: 'klein' });
  kd('kmy', '<span class="asis">μ</span>, i part (gap between the walls)', 1.4, 2.4, 0.001, 'my', { lo: 0.5, hi: 4 });
  kd('kmx', '<span class="asis">μ</span>, real part (lean)', -1, 1, 0.001, 'mx', { lo: -2, hi: 2 });
  kd('kmz', '<span class="asis">μ</span>, j part (lean in depth)', -1, 1, 0.001, 'mz', { lo: -2, hi: 2 });
  kd('kL', 'L, half the step of the third map', 0.3, 2.5, 0.005, 'L', { lo: 0.05, hi: 8 });
  kd('kiter', 'Depth of the search', 5, 150, 1, 'iter', { hi: 400, xmax: 2000, xhi: 100000, int: true });
  kd('kinvr', 'Turning-out sphere, radius', 0.4, 3, 0.01, 'invR', { lo: 0.05, hi: 10 });
  kd('kcx', 'Turning-out sphere, centre x', -1.5, 1.5, 0.005, 'cx', { lo: -6, hi: 6 });
  kd('kcy', 'Turning-out sphere, centre y', 0, 2.2, 0.005, 'cy', { lo: -6, hi: 6 });
  kd('kcz', 'Turning-out sphere, centre z', -1, 1, 0.005, 'cz', { lo: -6, hi: 6 });
  addCheck('kleinDials', 'k3', 'Use the third map, q → q + 2L·j', () => K.three, v => { K.three = !!v; uiKleinMark(); touch(); }, { group: 'klein' });
  addReset('kleinReset', 'klein', { after: uiKleinMark });

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
  addReset('approachReset', 'approach', { after: () => { S.approach = 0; refresh(false); } });

  // equation
  PRESETS.forEach((p, i) => $('eqPreset').add(new Option(p.name, i)));
  $('eqPreset').add(new Option('My own formula', -1));
  $('eq').value = S.eq; $('z0').value = S.z0;
  $('eqPreset').addEventListener('change', e => {
    const p = PRESETS[+e.target.value];
    if (!p) return;
    $('eq').value = p.eq; $('z0').value = p.z0;
    if (!applyEquation()) return;
    // a preset's cut height is meant for its Mandelbrot solid
    if (S.mode === 'm') { S.cutOn = p.cut !== undefined; if (S.cutOn) S.cut = p.cut; }
    resetCam(p); syncControls(); touch();
  });
  for (const id of ['eq', 'z0']) {
    $(id).addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); applyEquation(); } });
    $(id).addEventListener('change', applyEquation);
  }
  addDial('eqDials', 'pow', 'Power n', -8, 10, 0.1, () => S.n, v => { S.n = v; refresh(true); }, { lo: -16, hi: 24, def: 2, group: 'eq' });
  addDial('eqDials', 'iter', 'Iterations', 3, 60, 1, () => S.iter, v => { S.iter = Math.round(v); touch(); }, { hi: 400, xmax: 1000, xhi: 100000, int: true, def: 14, group: 'eq' });
  addReset('eqReset', 'eq', { after: () => { $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation(); resetCam(); refresh(false); } });
  uiEqMark();

  // modifiers
  const mod = (id, label, arr, i) => addCheck('modChecks', id, label, () => !!S[arr][i], v => { S[arr][i] = v ? 1 : 0; touch(); }, { def: false, group: 'mod' });
  mod('absx', '|x|', 'abs', 0); mod('absy', '|y|', 'abs', 1); mod('absz', '|z|', 'abs', 2); mod('flipy', 'flip y', 'flip', 0); mod('flipz', 'flip z', 'flip', 1);
  const setMods = (a, f) => { S.abs = a; S.flip = f; syncControls(); touch(); };
  $('modShip').addEventListener('click', () => setMods([1, 1, 1], [0, 0]));
  $('modBar').addEventListener('click', () => setMods([0, 0, 0], [1, 1]));
  $('modNone').addEventListener('click', () => setMods([0, 0, 0], [0, 0]));
  addReset('modReset', 'mod');

  // slice
  UI.cutOn = addCheck('cutDials', 'cutOn', 'Cut the solid open at height z', () => S.cutOn, v => { S.cutOn = !!v; touch(); }, { def: false, group: 'cut' });
  // moving the height switches the cut on, except in the 2D view, where the height is the slice itself
  addDial('cutDials', 'cut', 'Height z of the cut or slice', -1.5, 1.5, 0.01, () => S.cut, v => { S.cut = v; if (!S.flat) { S.cutOn = true; UI.cutOn.sync(); } touch(); }, { lo: -8, hi: 8, def: 0, group: 'cut' });
  addReset('cutReset', 'cut', { after: () => { S.cutOn = false; UI.cutOn.sync(); touch(); } });

  // colour and light
  UI.col = buildControls('colDials', COLOUR_CONTROLS, S.colour, touch, { idPrefix: 'col-', group: 'colour' });
  addDial('colDials', 'lightAz', 'Light, compass direction', 0, 360, 1, () => S.lightAz, v => { S.lightAz = v; touch(); }, { lo: -720, hi: 720, def: 250, group: 'colour' });
  addDial('colDials', 'lightEl', 'Light, height above the horizon', 5, 90, 1, () => S.lightEl, v => { S.lightEl = v; touch(); }, { lo: -90, hi: 90, def: 48, group: 'colour' });
  addReset('colDials', 'colour', { after: () => { UI.col.sync(); touch(); } });

  // view
  UI.fly = addCheck('viewDials', 'viewFly', 'Fly camera', () => S.view.fly, v => setCamMode(!!v), { def: false, group: 'view', help: 'Same as the Arcball and Fly buttons on the picture. Flying moves the camera itself: drag to look, W A S D to move.' });
  // the camera needs no redraw for a new speed, only its slider on the stage has to follow
  addDial('viewDials', 'viewSpeed', 'Fly speed, units per second', 0.01, 5, 0.01, () => S.view.speed, v => { S.view.speed = v; viewChanged(); }, { lo: CAM_LIM.speed[0], hi: CAM_LIM.speed[1], def: 1, group: 'view' });
  addDial('viewDials', 'viewBound', 'Drawing radius', 1, 100, 0.5, () => S.view.bound, v => { S.view.bound = v; touch(); }, { lo: 0.5, hi: 500, def: 8, group: 'view', help: 'Nothing is drawn outside a ball of this radius around the centre. Raise it when a picture is cut off far out.' });
  // The state holds the tangent of half the angle; the dial shows the whole angle in degrees. The starting
  // value is put back exactly, because preset cameras are framed for it.
  addDial('viewDials', 'viewFov', 'Field of view, degrees', 10, 120, 1, () => +(2 * Math.atan(S.view.fov) * 180 / PI).toFixed(2),
    v => { S.view.fov = Math.abs(v - UI_FOV_DEG) < 0.006 ? UI_FOV : Math.tan(v * PI / 360); touch(); }, { lo: 2, hi: 150, def: UI_FOV_DEG, group: 'view' });
  addReset('viewReset', 'view', { after: () => { resetZoomLimits(); touch(); } });

  // quality
  const Q = S.q, qd = (id, label, min, max, step, key, o) => addDial('qDials', id, label, min, max, step, () => Q[key], v => { Q[key] = v; touch(); }, { ...o, group: 'q' });
  qd('qres', 'Resolution, × screen pixels', 0.25, 2, 0.05, 'res', { lo: 0.1, hi: 3 });
  qd('qaa', 'Refining passes', 1, 64, 1, 'aa', { hi: 400, int: true });
  qd('qsteps', 'Ray steps, at most', 60, 700, 10, 'steps', { lo: 20, hi: 3000, xmax: 5000, int: true });
  qd('qdetail', 'Surface threshold, pixels', 0.2, 4, 0.05, 'detail', { lo: 0.02, hi: 20 });
  qd('qstepk', 'Step size, share of the estimate', 0.2, 1.2, 0.01, 'stepk', { lo: 0.05, hi: 2 });
  qd('qsmooth', 'Slope sampling width, pixels', 0.25, 4, 0.05, 'smooth', { lo: 0.05, hi: 20 });
  addSelect('qDials', 'qde', 'Distance estimate', [[3, 'Exact (three neighbouring orbits)'], [1, 'One neighbour (faster)'], [0, 'Rough (fastest)']],
    sceneDe, v => { Q.de = v; touch(); }, { def: 3, group: 'q', help: 'How the distance to the surface is worked out for each ray step. Rough is the quickest and the least careful.' });
  addSelect('qDials', 'normals', 'Surface detail from', [['sharp', 'Exact slope (sharp)'], ['smooth', 'Sampled slope (softer, can show rings)']],
    () => Q.normals, v => { Q.normals = v; touch(); }, { def: 'sharp', group: 'q', help: 'The exact slope needs the exact distance estimate. With the other two the slope is always sampled.' });
  const qChecks = document.createElement('div');
  qChecks.className = 'checks';
  $('qDials').appendChild(qChecks);
  addCheck(qChecks, 'qShadow', 'Shadows', () => Q.shadow, v => { Q.shadow = !!v; touch(); }, { def: true, group: 'q' });
  addCheck(qChecks, 'qAO', 'Shade crevices', () => Q.ao, v => { Q.ao = !!v; touch(); }, { def: true, group: 'q' });
  for (const id of Object.keys(UI_QUALITY)) $(id).addEventListener('click', () => { Object.assign(Q, UI_QUALITY[id]); syncControls(); touch(); });
  addReset('qReset', 'q');

  // mode
  for (const m of ['m', 'j', 'k']) $('mode-' + m).addEventListener('change', () => { S.mode = m; resetCam(); syncControls(); refresh(false); });

  // buildCard, bindView and initGL register their own overlays and hooks
  readTheme(); buildCard(); initGL(); bindView(); resetCam();
  if (!hooks.view.includes(uiViewSync)) hooks.view.push(uiViewSync);
  const retheme = () => { readTheme(); drawStep2d(); touch(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  new ResizeObserver(() => { drawStep2d(); touch(); }).observe(stage);
  new ResizeObserver(() => { drawStep2d(); viewChanged(); }).observe($('step2d'));
  refresh(false);
}
