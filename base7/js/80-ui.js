// ---------- the page: builds every control from the modules' specs and wires it to the state.
// Section groups for resetGroup: 'mandel', 'julia', 'klein', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'.
// The panels other modules build ("Save a picture", "Save a 3D model") use 'export' and 'mesh'; they describe
// files, not the picture, and "Reset everything" leaves them alone.
const UI = {
  col: null,         // the colour controls (a buildControls set)
  juliaSel: null,    // the Julia drop-down
  kleinSel: null,    // the Kleinian drop-down
  cutOn: null,       // the "cut the solid open" checkbox
  ex: null,          // the drop-down of trap solid examples in Colour and light
  fly: null,         // the fly-camera checkbox in the View section
  extreme: null,     // the "Extreme ranges" checkbox
  pow: null,         // the power dial (rebuilt when the approach only takes whole powers)
  powWhole: null,    // whether that dial is the whole-number one
  kL: null,          // the L dial of the Kleinian group
  ap: {},            // the control set of each approach, by approach id
  flyShown: false,   // what the fly checkbox last showed (the stage switch and the F key change the mode too)
  juliaKey: 'p0',    // the Julia entry last chosen from the list (see juliaEntry)
  kleinAt: 0,        // the Kleinian entry last chosen
  presetCut: false,  // the cut was opened by an equation preset, so the next preset or the Equation reset may close it
  mosaicWas: false,  // the mosaic checkbox as last seen, and what the cut was before the mosaic opened it
  mosaicCut: null,
  only3d: [],        // elements put away while the 2D view is on, because they do nothing there
  seen: {},          // what each mark last showed (see uiOnce)
};
const UI_GROUPS = ['mandel', 'julia', 'klein', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'];
const UI_FOV = 0.32, UI_FOV_DEG = 35.49;   // the starting field of view: as the state holds it, and as the dial shows it
// A preset sets every dial of the Quality section, so the same button always gives the same picture.
const UI_QUALITY = {
  qUltra: { res: 0.5, aa: 1, steps: 90, detail: 2, stepk: 0.8, smooth: 1, shadow: false, ao: false, de: 0, normals: 'smooth' },
  qFast: { res: 0.75, aa: 3, steps: 160, detail: 1.25, stepk: 0.8, smooth: 1, shadow: false, ao: true, de: 3, normals: 'sharp' },
  qBal: { res: 1, aa: 12, steps: 260, detail: 1, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
  qFine: { res: 1.5, aa: 32, steps: 450, detail: 0.7, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
};
// What "Show Figure 4" sets besides the approach: the point c, and a camera that shows both circles of beads.
// `room` is the radius that solid reaches to: a drawing radius below it would cut the ends off.
const UI_FIG4 = { c: [-1, 0, 0], cam: { yaw: -1.9, pitch: 0.55, dist: 4.8 }, room: 2.5 };
// The mirror twins that have a button in the closing text, by approach id: how far back the camera stands, as a
// multiple of the usual start. Their Mandelbrot solids are taller than the plain ones. UI_TWIN_ROOM is the radius
// they reach to (the Mandelbrot solid lies within 2 of the centre, and its twins stand taller).
const UI_TWIN = { mercator: 1.15, lathe: 1.6, bulb: 1.35 };
const UI_TWIN_ROOM = 3;
const UI_EXTREME_TEXT = {
  off: 'Extreme ranges lets most dials reach five to ten times further. Expect slow pictures.',
  on: 'Extreme ranges are on. Dials marked wide reach far past their usual limits, and pictures can get very slow.',
};

// After the approach, the power or the mode changed: panels, texts, figures, scorecard, then the picture.
// `slow` is kept for callers that pass it; the scorecard now spreads its own work over frames.
function refresh(slow) {
  uiPowerDial();
  const k = S.mode === 'k';
  $('mandelPanel').hidden = S.mode !== 'm'; $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = !k;
  ['secApproach', 'secEq', 'secMod'].forEach(id => { $(id).hidden = k; });
  $('mode-' + S.mode).checked = true;
  document.querySelectorAll('.rule').forEach((el, i) => el.classList.toggle('is-on', i === S.approach));
  APPROACHES.forEach((x, i) => {
    $('ap-' + x.id).checked = i === S.approach;
    $('f-' + x.id).textContent = x.formula(S.param[x.id], S.n);
  });
  uiJuliaMark(); uiKleinMark(); uiCollapsePaint(); uiEmptyNote();
  buildStep3d(); drawStep2d(); updateCard();
  touch();
  hooks.refresh.forEach(f => f());
}
// A dial of the chosen approach moved. While one sweeps this runs every frame, so it redoes only what depends
// on the dial: that approach's formula text, the 3D step figure, the scorecard and the picture.
function uiApproachParam() {
  const a = ap();
  $('f-' + a.id).textContent = a.formula(S.param[a.id], S.n);
  buildStep3d(); updateCard();
  touch();
}
function applyEquation() {
  const eq = $('eq').value.trim() || 'z', z0 = $('z0').value.trim() || '0', err = $('eqErr');
  try { compileFormula(eq, true, false); compileFormula(z0, false, false); }
  catch (e) { err.textContent = e.message; err.hidden = false; return false; }
  err.hidden = true;
  S.eq = eq; S.z0 = z0;
  uiEqMark(); uiEmptyNote();
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
// The power dial. An approach marked integerOnly has a rule that only means something for whole powers, so
// while one is chosen the dial holds whole numbers (and the power is rounded on the way in). The kit fixes
// "whole numbers only" when a dial is made, so the dial is made again when that changes.
function uiPowerDial() {
  const whole = !!ap().integerOnly;
  if (UI.pow && UI.powWhole === whole) return;
  if (UI.pow) UI.pow.remove();
  if (whole) S.n = Math.round(S.n) + 0;
  UI.powWhole = whole;
  UI.pow = addDial('powHost', 'pow', 'Power n', -8, 10, whole ? 1 : 0.1, () => S.n, v => { S.n = v; refresh(true); },
    { lo: -16, hi: 24, xmin: -40, xmax: 60, xlo: -100, xhi: 200, def: 2, group: 'eq', int: whole });
  $('powWhole').hidden = !whole;
}

// ---------- Julia points: one drop-down holding the user's saved points, then the shipped ones
// The heading a shipped entry stands under comes from its `source` in data/julia-presets.json. The headings
// follow one another in this order, after the user's own saved points.
const UI_JULIA_HEADS = ['Classic sets', 'Found by exploring', 'Found with two planes'];
const uiJuliaHead = p => (p.source === 'explored' ? UI_JULIA_HEADS[1] : p.source === 'two planes' ? UI_JULIA_HEADS[2] : UI_JULIA_HEADS[0]);
function uiJuliaOptions() {
  const list = [['own', 'Your own values']];
  juliaSaved.forEach((p, i) => list.push(['s' + i, p.name, 'Your saved points']));
  for (const head of UI_JULIA_HEADS) JULIA_PRESETS.forEach((p, i) => { if (uiJuliaHead(p) === head) list.push(['p' + i, p.name, head]); });
  return list;
}
// Fill the drop-down again (after a point was saved or deleted).
function uiJuliaList() {
  UI.juliaSel.setOptions(uiJuliaOptions());
  // "Your own values" is what the box reads when c is on no entry. It cannot be picked: there is nothing to jump to.
  $('juliaPreset').options[0].disabled = true;
  uiJuliaMark();
}
// Make the drop-down, its note and the delete button show where the point c now stands.
function uiJuliaMark() {
  if (!UI.juliaSel) return;
  const key = juliaKeyAt(UI.juliaKey), p = juliaEntry(key), note = $('juliaNote');
  UI.juliaSel.sync();
  $('juliaDelete').hidden = key[0] !== 's';
  let text = !p ? `Your own point, c = (${S.c.map(x => dialFmt(x)).join(', ')}). Save it to keep it in the list.`
    : p.source === 'saved' ? 'One of your saved points.' : juliaNoteFor(p);
  if (p && p.source !== 'saved' && (S.eq !== 'z^n + c' || S.n !== 2)) text += ' The name belongs to z² + c. With the equation and power set now, the picture is a different one.';
  if (note.textContent !== text) note.textContent = text;
  // "As it was found" is on show only while it would change something
  const found = $('juliaFound'), d = juliaFoundDiff(p);
  found.hidden = !d;
  if (d) {
    const sets = [d.planes !== undefined && `Planes to ${d.planes}`, d.iter !== undefined && `Iterations to ${d.iter}`].filter(Boolean).join(' and ');
    found.title = `Sets ${sets}, as when this entry was found. Nothing else changes.`;
  }
}
function uiKleinMark() {
  if (!UI.kleinSel) return;
  UI.kleinSel.sync();
  // an entry of the list is a checked picture, so the warning is for the user's own values only
  const i = kleinPresetAt(UI.kleinAt), note = $('kleinNote'), warn = $('kleinWarn'), trouble = i >= 0 ? '' : kleinTrouble();
  const text = i >= 0 ? kleinNoteFor(KLEIN_PRESETS[i]) : 'Your own values. Pick an entry from the list to go back to a known picture.';
  if (note.textContent !== text) note.textContent = text;
  if (warn.textContent !== trouble) warn.textContent = trouble;
  warn.hidden = !trouble;
  if (UI.kL) UI.kL.el.hidden = !S.k.three;   // L belongs to the third map
}
const uiSections = () => [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden);
function uiCollapsePaint() {
  const open = uiSections().some(d => d.open), b = $('collapseAll'), text = open ? 'Collapse all' : 'Expand all';
  if (b.textContent !== text) b.textContent = text;
}
// The 2D view: its label says which slice is drawn, and controls that only act on the 3D picture are put away.
function uiFlatPaint() {
  const z = $('flatZ');
  if (z) z.textContent = `(slice at z = ${dialFmt(+(+S.cut).toFixed(4)).replace('-', '−')})`;
  UI.only3d.forEach(el => { el.hidden = !!S.flat; });
  document.querySelectorAll('.only2d').forEach(el => { el.hidden = !S.flat; });
}
// Mark the quality preset whose values the Quality section now holds, if any.
function uiQualityMark() {
  for (const id of Object.keys(UI_QUALITY)) {
    const on = Object.entries(UI_QUALITY[id]).every(([key, v]) => S.q[key] === v), b = $(id);
    b.classList.toggle('is-on', on);
    b.setAttribute('aria-pressed', String(on));
  }
}
function uiExtremePaint() {
  if (UI.extreme) UI.extreme.sync();
  const note = $('extremeNote'), text = S.extreme ? UI_EXTREME_TEXT.on : UI_EXTREME_TEXT.off;
  if (note.textContent !== text) note.textContent = text;
}
// With the plain equation and a power between -1 and 1 the stage stays empty, which looks like a fault: say why.
function uiEmptyNote() {
  $('stageNote').hidden = !(S.mode !== 'k' && S.eq === 'z^n + c' && Math.abs(S.n) <= 1);
}
// Run a mark only when what it shows has changed.
function uiOnce(key, sig, paint) {
  if (UI.seen[key] === sig) return;
  UI.seen[key] = sig;
  paint();
}
// Called at most once a frame after anything changed (the stage, the keys, a test and other modules change the
// state too, not only the controls here): keep every mark on the page in step with the state.
function uiViewSync() {
  if (UI.fly && UI.flyShown !== !!S.view.fly) { UI.flyShown = !!S.view.fly; UI.fly.sync(); }
  uiOnce('flat', `${S.flat}|${S.cut}`, uiFlatPaint);
  uiOnce('q', JSON.stringify(S.q), uiQualityMark);
  uiOnce('julia', `${S.c}|${S.eq}|${S.n}|${S.approach}|${S.iter}|${S.param.mercator && S.param.mercator.planes}`, uiJuliaMark);
  // (the warning under the Kleinian list also depends on where the camera stands: see kleinSwallowed)
  uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? (kleinReach() > S.view.bound ? '|near, cut' : '|near') : ''), uiKleinMark);
  if (UI.ex) uiOnce('example', `${S.mode}|${S.c}|${JSON.stringify(S.k)}|${EXAMPLE_KEYS.map(key => S.colour[key])}`, UI.ex.sync);
  uiOnce('empty', `${S.mode}|${S.eq}|${S.n}`, uiEmptyNote);
  uiOnce('extreme', String(!!S.extreme), uiExtremePaint);
  // on a narrow screen the hint has no room on the picture, so a copy of it sits under the stage
  const hint = stage.querySelector('.hint'), below = $('hintBelow');
  if (hint && below.textContent !== hint.textContent) below.textContent = hint.textContent;
}
// ---------- the two buttons beside the Figure 4 answer in the closing text
// A dial that is sweeping writes its value back every frame, so the sweeps of an approach stop before its dials are set.
function uiApQuiet(id) { (UI.ap[id] ? UI.ap[id].controls : []).forEach(c => { if (c.play) c.play(false); }); }
// The picture is at the top of the page and these buttons are at its end: bring the picture into view.
function uiShowStage() {
  stage.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
}
// "Show Figure 4": the Julia set for c = -1 under Sphere inversions with two planes, which is where the page
// draws the picture of Figure 4 in Kučera's paper. It sets everything that picture depends on, from any state:
// what would show another solid (the equation, the modifiers, a trap that is the solid) or hide this one (the
// 2D view, the cut) is put back too. Iterations, quality and colours stay the user's.
function uiFigure4() {
  const p = S.param.mercator;
  uiApQuiet('mercator');
  S.flat = false; S.mode = 'j'; S.approach = APPROACHES.findIndex(a => a.id === 'mercator');
  p.planes = 2; p.turn = 0; p.lift = 0;
  S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, 0];
  S.cutOn = false; UI.presetCut = false;
  S.colour.solid = 0;
  $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
  UI.juliaKey = 'p' + Math.max(0, JULIA_PRESETS.findIndex(q => q.name === 'Basilica'));
  applyJuliaPreset({ c: UI_FIG4.c });
  // "frames it" is a promise: a zoom limit or a drawing radius of the user's that is in the way is moved
  presetFrame(UI_FIG4.cam, presetNarrow(), 3.6, UI_FIG4.room);
  uiFlatPaint(); syncControls();
  refresh(false);
  uiShowStage();
}
// "Back to one plane": the planes dial of Sphere inversions goes to 1, and that approach is the one on show.
// The point c, the camera and everything else stay. Planes mean nothing to a Kleinian group, so from there the
// page goes to the Julia set.
function uiOnePlane() {
  uiApQuiet('mercator');
  S.param.mercator.planes = 1;
  S.approach = APPROACHES.findIndex(a => a.id === 'mercator');
  if (S.mode === 'k') { S.mode = 'j'; resetCam(); }
  syncControls();
  refresh(false);
  uiShowStage();
}
// ---------- the buttons beside the mirror twin answer in the closing text
// A rule's mirror twin is the same step followed by z -> -z, which the modifier "flip z" gives. A twin button
// shows the Mandelbrot solid of one approach with that box ticked, because that solid is where the twin differs.
// Like Show Figure 4 it sets everything the picture depends on, from any state: the approach's own dials go back
// to their starting values, and what would show another solid (the equation, the other modifiers, the mosaic, a
// trap that is the solid) or hide this one (the 2D view, the cut) is put back too. Iterations, quality and
// colours stay the user's.
function uiTwin(id) {
  const i = APPROACHES.findIndex(a => a.id === id);
  if (i < 0) return;
  uiApQuiet(id);
  Object.assign(S.param[id], specDefaults(APPROACHES[i].params || []));
  S.flat = false; S.mode = 'm'; S.approach = i;
  S.mosaic = false; UI.mosaicWas = false; UI.mosaicCut = null;
  S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, 1];
  S.cutOn = false; UI.presetCut = false;
  S.colour.solid = 0;
  $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
  // the whole solid in the picture, as the text promises: a zoom limit or a drawing radius in the way is moved
  presetHome(UI_TWIN[id] || 1, UI_TWIN_ROOM);
  uiFlatPaint(); syncControls();
  refresh(false);
  uiShowStage();
}
// "Back to the plain rule": unticks flip z and changes nothing else.
function uiTwinOff() {
  S.flip = [S.flip[0], 0];
  syncControls();
  touch();
  uiShowStage();
}

// Everything back to how the page opens, except the user's saved Julia points and which sections are open.
function uiResetAll() {
  if (typeof setExtreme === 'function') setExtreme(false); else S.extreme = false;
  S.flat = false; S.mode = 'm'; S.approach = 0;
  UI.presetCut = false; UI.mosaicCut = null; UI.mosaicWas = false;
  resetGroup(UI_GROUPS);
  S.cutOn = false;   // resetting the height dial switches the cut on, as moving it by hand does
  $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
  $('juliaName').value = ''; $('juliaSaveNote').hidden = true;
  UI.juliaKey = 'p0'; UI.kleinAt = 0;
  resetZoomLimits(); resetCam();
  syncControls();
  refresh(false);
}

function boot() {
  initState();
  juliaSavedLoad();
  // The first screen: tell the stylesheet where the picture starts on the page, so that its height stops short
  // of the window's lower edge there (.stage in 00-base.css). The masthead above it changes height with the
  // window's width and when the fonts arrive, so it is measured again whenever that happens.
  // (measured on the bench, not on the picture: the picture stays put while the page scrolls under it)
  const bench = document.querySelector('.bench'), stageTop = () => {
    const y = Math.round(bench.getBoundingClientRect().top + scrollY) + 12;
    if (UI.seen.stageTop !== y) { UI.seen.stageTop = y; document.documentElement.style.setProperty('--stage-top', y + 'px'); }
  };
  new ResizeObserver(stageTop).observe(document.querySelector('.masthead'));
  stageTop();
  const only3d = c => { UI.only3d.push(c.el); return c; };

  // top row: 2D view, extreme ranges, collapse all, reset everything
  addCheck('flatHost', 'flat', '2D view <span class="flat-z" id="flatZ"></span>', () => S.flat, v => { S.flat = !!v; uiFlatPaint(); syncControls(); touch(); }, { def: false });
  UI.extreme = addCheck('extremeHost', 'extreme', 'Extreme ranges', () => !!S.extreme, v => {
    // switching off also pulls every value back inside its usual limits (the kit does that through each dial's setter)
    if (typeof setExtreme === 'function') setExtreme(!!v); else S.extreme = !!v;
    uiExtremePaint(); syncControls(); touch();
  }, { def: false });
  $('collapseAll').addEventListener('click', () => {
    // every section, the ones of the other modes too, so a mode switch does not bring back the opposite state
    const open = !uiSections().some(d => d.open);
    document.querySelectorAll('#sections > details.sec').forEach(d => { d.open = open; });
    uiCollapsePaint();
  });
  document.querySelectorAll('#sections > details.sec').forEach(d => d.addEventListener('toggle', uiCollapsePaint));
  $('resetAll').addEventListener('click', uiResetAll);

  // Mandelbrot options: the Julia mosaic. The cells are stacked in depth too, and seen from outside they hide
  // one another, so ticking the box in the 3D view also cuts the solid open at z = 0 (and unticking it puts the
  // cut back as it was, unless the user has moved it since).
  const mosaicChanged = () => {
    if (S.mosaic !== UI.mosaicWas) {
      UI.mosaicWas = S.mosaic;
      if (S.mosaic && !S.flat) { UI.mosaicCut = { on: S.cutOn, z: S.cut }; S.cutOn = true; S.cut = 0; }
      else if (!S.mosaic && UI.mosaicCut) {
        if (S.cutOn && S.cut === 0) { S.cutOn = UI.mosaicCut.on; S.cut = UI.mosaicCut.z; }
        UI.mosaicCut = null;
      }
      syncControls();
    }
    touch();
  };
  buildControls('mandelDials', [
    { type: 'check', key: 'mosaic', label: 'Julia mosaic', def: false, help: 'Fills space with a grid of small Julia sets. Each cell shows the Julia set of the point at its centre, so together they trace the Mandelbrot solid. The cells are stacked in depth as well, so the solid is cut open at z = 0 to show one layer. Untick the cut in the Slice section to see them all.' },
    { type: 'dial', key: 'mosaicCell', label: 'Mosaic cell size', min: 0.08, max: 1, step: 0.01, def: 0.3, lo: 0.03, hi: 4, xmin: 0.02, xmax: 5, xlo: 0.005, xhi: 20, when: s => s.mosaic },
  ], S, mosaicChanged, { idPrefix: 'm-', group: 'mandel' });
  addReset('mandelDials', 'mandel');

  // Julia point
  UI.juliaSel = addSelect('juliaPresetHost', 'juliaPreset', 'Jump to a point', uiJuliaOptions(), () => juliaKeyAt(UI.juliaKey),
    key => { const p = juliaEntry(key); if (p) { UI.juliaKey = key; applyJuliaPreset(p); } });
  const cd = (id, label, i, def) => addDial('juliaDials', id, label, -2, 2, 0.01, () => S.c[i], v => { S.c[i] = v; uiJuliaMark(); touch(); }, { lo: -8, hi: 8, xmin: -10, xmax: 10, xlo: -50, xhi: 50, def, group: 'julia' });
  cd('cx', 'c along x', 0, -1); cd('cy', 'c along y', 1, 0); cd('cz', 'c along z', 2, 0);
  uiJuliaList();
  $('juliaFrame').addEventListener('click', () => frameJuliaPreset(juliaEntry(juliaKeyAt(UI.juliaKey))));
  $('juliaFound').addEventListener('click', () => {
    applyJuliaFound(juliaEntry(juliaKeyAt(UI.juliaKey)));
    if ($('juliaFound').hidden) $('juliaFrame').focus();   // the button has just gone: keep the focus beside it
  });
  const saveNote = text => { const note = $('juliaSaveNote'); note.textContent = text; note.hidden = !text; };
  const save = () => {
    const r = juliaSavePoint($('juliaName').value);
    saveNote(!r.ok ? 'The list is full. Delete a saved point first.' : r.dup ? 'This point is already in the list under that name.'
      : r.kept ? '' : 'Saved for this visit. This browser does not let the page keep it for next time.');
    if (r.ok) { UI.juliaKey = 's' + r.at; $('juliaName').value = ''; uiJuliaList(); }
  };
  $('juliaSave').addEventListener('click', save);
  $('juliaName').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); save(); } });
  $('juliaDelete').addEventListener('click', () => {
    const key = juliaKeyAt(UI.juliaKey);
    if (key[0] !== 's') return;
    juliaDeletePoint(+key.slice(1));
    UI.juliaKey = 'own';   // the saved points behind it have moved up one
    saveNote('');
    uiJuliaList();
    $('juliaPreset').focus();   // the button has just gone, and focus must not fall back to the top of the page
  });
  addReset('juliaReset', 'julia', { after: () => { UI.juliaKey = 'p0'; $('juliaName').value = ''; saveNote(''); uiJuliaMark(); } });

  // Kleinian group. The list is not part of the reset group: the dials and the checkbox restore every value, and
  // putting the list back through its setter would do nothing more.
  // (the labels are upper case, which would print the Greek letter μ as a Latin M: class asis keeps it as typed)
  const K = S.k, kd = (id, label, min, max, step, key, o) => addDial('kleinDials', id, label, min, max, step, () => K[key], v => { K[key] = v; uiKleinMark(); touch(); }, { ...o, group: 'klein' });
  const kHead = { cusp: 'Cusps: pearls that just touch', inside: 'Above a cusp: strings that do not close', explored: 'Found by exploring', sphere: 'Turning-out sphere' };
  const kGroup = p => p.group || kHead[String(p.source || '').split(' ')[0]] || 'More';
  UI.kleinSel = addSelect('kleinPresetHost', 'kleinPreset', 'Start from', [[-1, 'Your own values'], ...KLEIN_PRESETS.map((p, i) => [i, p.name, kGroup(p)])],
    () => kleinPresetAt(UI.kleinAt), i => { if (i >= 0) { UI.kleinAt = i; applyKleinPreset(KLEIN_PRESETS[i]); } });
  $('kleinPreset').options[0].disabled = true;
  $('kleinFrame').addEventListener('click', () => frameKleinPreset(KLEIN_PRESETS[kleinPresetAt(UI.kleinAt)]));
  // The sliders keep to the region where the picture holds together; typed values and the extreme ranges go further.
  kd('kmy', '<span class="asis">μ</span>, i part (gap between the walls)', 1.5, 2.4, 0.001, 'my', { lo: 1.2, hi: 4, xmin: 0.5, xmax: 6, xlo: 0.05, xhi: 20 });
  kd('kmx', '<span class="asis">μ</span>, real part (lean)', -1, 1, 0.001, 'mx', { lo: -2, hi: 2, xmin: -5, xmax: 5, xlo: -20, xhi: 20 });
  kd('kmz', '<span class="asis">μ</span>, j part (lean in depth)', -1, 1, 0.001, 'mz', { lo: -2, hi: 2, xmin: -5, xmax: 5, xlo: -20, xhi: 20 });
  addCheck('kleinDials', 'k3', 'Use the third map, q → q + 2L·j', () => K.three, v => { K.three = !!v; uiKleinMark(); touch(); }, { group: 'klein' });
  UI.kL = kd('kL', 'L, half the step of the third map', 1, 2.5, 0.005, 'L', { lo: 0.5, hi: 8, xmin: 0.1, xmax: 12, xlo: 0.01, xhi: 50 });
  kd('kiter', 'Depth of the search', 5, 150, 1, 'iter', { hi: 400, int: true, xmax: 1000, xhi: 5000 });
  kd('kinvr', 'Turning-out sphere, radius', 0.4, 3, 0.01, 'invR', { lo: 0.05, hi: 10, xmin: 0.05, xmax: 15, xlo: 0.005, xhi: 100 });
  kd('kcx', 'Turning-out sphere, centre x', -1.5, 1.5, 0.005, 'cx', { lo: -6, hi: 6, xmin: -10, xmax: 10, xlo: -60, xhi: 60 });
  kd('kcy', 'Turning-out sphere, centre y', 0.05, 2.35, 0.005, 'cy', { lo: -6, hi: 6, xmin: -10, xmax: 10, xlo: -60, xhi: 60 });
  kd('kcz', 'Turning-out sphere, centre z', -1, 1, 0.005, 'cz', { lo: -6, hi: 6, xmin: -10, xmax: 10, xlo: -60, xhi: 60 });
  addReset('kleinReset', 'klein', { after: () => { UI.kleinAt = 0; uiKleinMark(); } });

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
    UI.ap[r.id] = buildControls('pd-' + r.id, r.params || [], S.param[r.id], uiApproachParam, { idPrefix: 'par-' + r.id + '-', group: 'approach' });
  });
  addReset('approachReset', 'approach', { after: () => { S.approach = 0; refresh(false); } });

  // equation
  PRESETS.forEach((p, i) => $('eqPreset').add(new Option(p.name, i)));
  $('eqPreset').add(new Option('My own formula', -1));
  $('eq').value = S.eq; $('z0').value = S.z0;
  $('eqPreset').addEventListener('change', e => {
    const p = PRESETS[+e.target.value];
    if (!p) { uiEqMark(); return; }   // "My own formula" is a description, not something to jump to
    $('eq').value = p.eq; $('z0').value = p.z0;
    if (!applyEquation()) return;
    // A preset's cut is meant for its Mandelbrot solid. Only a cut that a preset opened is closed again here:
    // one the user switched on is theirs.
    if (S.mode === 'm') {
      if (p.cut !== undefined) { if (!S.cutOn) UI.presetCut = true; S.cutOn = true; S.cut = p.cut; }
      else if (UI.presetCut) { S.cutOn = false; UI.presetCut = false; }
    }
    resetCam(p); syncControls(); touch();
  });
  for (const id of ['eq', 'z0']) {
    $(id).addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); applyEquation(); } });
    $(id).addEventListener('change', applyEquation);
  }
  uiPowerDial();
  addDial('eqDials', 'iter', 'Iterations', 3, 60, 1, () => S.iter, v => { S.iter = Math.round(v); touch(); }, { hi: 400, xmax: 400, xhi: 4000, int: true, def: 14, group: 'eq' });
  // the view stays where it is: this button is about the equation
  addReset('eqReset', 'eq', { after: () => {
    $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
    if (UI.presetCut) { S.cutOn = false; UI.presetCut = false; UI.cutOn.sync(); }
    refresh(false);
  } });
  uiEqMark();

  // modifiers
  const mod = (id, label, arr, i) => addCheck('modChecks', id, label, () => !!S[arr][i], v => { S[arr][i] = v ? 1 : 0; touch(); }, { def: false, group: 'mod' });
  mod('absx', '|x|', 'abs', 0); mod('absy', '|y|', 'abs', 1); mod('absz', '|z|', 'abs', 2); mod('flipy', 'flip y', 'flip', 0); mod('flipz', 'flip z', 'flip', 1);
  const setMods = (a, f) => { S.abs = a; S.flip = f; syncControls(); touch(); };
  $('modShip').addEventListener('click', () => setMods([1, 1, 1], [0, 0]));
  $('modBar').addEventListener('click', () => setMods([0, 0, 0], [1, 1]));
  $('modNone').addEventListener('click', () => setMods([0, 0, 0], [0, 0]));
  addReset('modReset', 'mod');

  // slice. A cut the user touches is theirs from then on (see the equation presets above).
  UI.cutOn = addCheck('cutDials', 'cutOn', 'Cut the solid open at height z', () => S.cutOn, v => { S.cutOn = !!v; UI.presetCut = false; touch(); }, { def: false, group: 'cut' });
  // moving the height switches the cut on, except in the 2D view, where the height is the slice itself
  addDial('cutDials', 'cut', 'Height z of the cut or slice', -1.5, 1.5, 0.01, () => S.cut, v => { S.cut = v; if (!S.flat) { S.cutOn = true; UI.presetCut = false; UI.cutOn.sync(); } uiFlatPaint(); touch(); },
    { lo: -8, hi: 8, xmin: -8, xmax: 8, xlo: -50, xhi: 50, def: 0, group: 'cut' });
  addReset('cutReset', 'cut', { after: () => { S.cutOn = false; UI.presetCut = false; UI.cutOn.sync(); touch(); } });

  // colour and light
  UI.col = buildControls('colDials', COLOUR_CONTROLS, S.colour, touch, { idPrefix: 'col-', group: 'colour' });
  only3d(addDial('colDials', 'lightAz', 'Light, compass direction', 0, 360, 1, () => S.lightAz, v => { S.lightAz = v; touch(); }, { lo: -720, hi: 720, def: 250, group: 'colour' }));
  only3d(addDial('colDials', 'lightEl', 'Light, height above the horizon', 5, 90, 1, () => S.lightEl, v => { S.lightEl = v; touch(); }, { lo: -90, hi: 90, def: 48, group: 'colour' }));
  addReset('colReset', 'colour', { after: () => { UI.col.sync(); touch(); } });
  // Trap solid examples: a drop-down right under "In the 3D view the trap", on show whenever that choice is. It
  // belongs to no reset group: an example is something to jump to, not a setting. Like the other two lists it
  // names an example only while the page stands on it (see exampleFits).
  const solidC = UI.col.controls.find(c => c.id === 'col-solid'), exHost = document.createElement('div');
  exHost.className = 'sec-inner'; exHost.id = 'exampleHost';
  if (solidC) solidC.el.after(exHost); else $('colDials').prepend(exHost);
  UI.ex = addSelect(exHost, 'trapExamples', 'Examples', [[-1, 'Choose one to try'], ...EXAMPLES.map((e, i) => [i, e.name, e.head])], exampleAt, i => applyExample(EXAMPLES[i]),
    { help: 'Trap solids that came out well in testing. An example sets the kind of picture with its Julia point or Kleinian group, the trap shape, what the trap does, its thickness, skipped steps and radius, and the camera. Everything else stays as you left it, so with another approach, power or equation the same example gives a different object.' });
  $('trapExamples').options[0].disabled = true;
  if (solidC) {
    const follow = () => { exHost.hidden = solidC.el.hidden; };
    new MutationObserver(follow).observe(solidC.el, { attributes: true, attributeFilter: ['hidden'] });
    follow();
  }

  // view
  UI.fly = only3d(addCheck('viewDials', 'viewFly', 'Fly camera', () => S.view.fly, v => setCamMode(!!v), { def: false, group: 'view', help: 'Same as the Arcball and Fly buttons on the picture. Flying moves the camera itself: drag to look, W A S D to move.' }));
  // the camera needs no redraw for a new speed, only its slider on the stage has to follow
  only3d(addDial('viewDials', 'viewSpeed', 'Fly speed, units per second', 0.01, 5, 0.01, () => S.view.speed, v => { S.view.speed = v; viewChanged(); }, { lo: CAM_LIM.speed[0], hi: CAM_LIM.speed[1], xmax: CAM_LIM.speed[1], def: 1, group: 'view' }));
  only3d(addDial('viewDials', 'viewBound', 'Drawing radius', 1, 100, 0.5, () => S.view.bound, v => { S.view.bound = v; touch(); }, { lo: 0.5, hi: 500, xmax: 1000, xhi: 5000, def: 8, group: 'view', help: 'Nothing is drawn outside a ball of this radius around the centre. Raise it when a picture is cut off far out.' }));
  // The state holds the tangent of half the angle; the dial shows the whole angle in degrees. The starting
  // value is put back exactly, because preset cameras are framed for it.
  only3d(addDial('viewDials', 'viewFov', 'Field of view, degrees', 10, 120, 1, () => +(2 * Math.atan(S.view.fov) * 180 / PI).toFixed(2),
    v => { S.view.fov = Math.abs(v - UI_FOV_DEG) < 0.006 ? UI_FOV : Math.tan(v * PI / 360); touch(); }, { lo: 2, hi: 150, xmin: 1, xmax: 170, xlo: 0.5, xhi: 175, def: UI_FOV_DEG, group: 'view' }));
  addReset('viewReset', 'view', { after: () => { resetZoomLimits(); touch(); } });

  // quality
  const Q = S.q, qd = (id, label, min, max, step, key, o) => addDial('qDials', id, label, min, max, step, () => Q[key], v => { Q[key] = v; uiQualityMark(); touch(); }, { ...o, group: 'q' });
  qd('qres', 'Resolution, × screen pixels', 0.25, 2, 0.05, 'res', { lo: 0.1, hi: 3, xmax: 4, xhi: 6 });
  qd('qaa', 'Refining passes', 1, 64, 1, 'aa', { hi: 400, xmax: 400, xhi: 4000, int: true });
  only3d(qd('qsteps', 'Ray steps, at most', 60, 700, 10, 'steps', { lo: 20, hi: 3000, xmax: 4000, xhi: 20000, int: true,
    help: 'The most steps one ray may take. Raise it when far or thin parts go missing.' }));
  only3d(qd('qdetail', 'Surface threshold, pixels', 0.2, 4, 0.05, 'detail', { lo: 0.02, hi: 20, xmin: 0.02, xmax: 20, xlo: 0.002, xhi: 100,
    help: 'A ray stops when it is this close to the surface, measured in screen pixels. Smaller shows finer detail and takes longer.' }));
  only3d(qd('qstepk', 'Ray step, share of the distance estimate', 0.2, 1.2, 0.01, 'stepk', { lo: 0.05, hi: 2, xmin: 0.02, xmax: 2, xlo: 0.005, xhi: 4,
    help: 'Each ray step covers this share of the estimated distance to the surface. Lower is safer and slower. Higher is faster and can punch holes. In the Kleinian view anything above 0.5 counts as 0.5.' }));
  only3d(qd('qsmooth', 'Slope sampling width, pixels', 0.25, 4, 0.05, 'smooth', { lo: 0.05, hi: 20, xmax: 20, xhi: 100,
    help: 'Used by the sampled slope: how far apart its samples are taken. Wider is smoother and loses fine detail.' }));
  only3d(addSelect('qDials', 'qde', 'Distance estimate', [[3, 'Exact (cleanest, slowest)'], [1, 'One neighbour (faster)'], [0, 'Rough (fastest, least accurate)']],
    sceneDe, v => { Q.de = v; uiQualityMark(); touch(); }, { def: 3, group: 'q', help: 'Before each ray step the lab works out how far away the surface is. Exact follows three extra nearby points alongside every point and gives the cleanest picture. One neighbour follows one. Rough follows none: it is the quickest and the least accurate.' }));
  only3d(addSelect('qDials', 'normals', 'Surface detail from', [['sharp', 'Exact slope (sharp)'], ['smooth', 'Sampled slope (softer, can show rings)']],
    () => Q.normals, v => { Q.normals = v; uiQualityMark(); touch(); }, { def: 'sharp', group: 'q', help: 'The exact slope needs the exact distance estimate. With the other two the slope is always sampled.' }));
  const qChecks = document.createElement('div');
  qChecks.className = 'checks';
  $('qDials').appendChild(qChecks);
  UI.only3d.push(qChecks);
  addCheck(qChecks, 'qShadow', 'Shadows', () => Q.shadow, v => { Q.shadow = !!v; uiQualityMark(); touch(); }, { def: true, group: 'q' });
  addCheck(qChecks, 'qAO', 'Shade crevices', () => Q.ao, v => { Q.ao = !!v; uiQualityMark(); touch(); }, { def: true, group: 'q' });
  for (const id of Object.keys(UI_QUALITY)) $(id).addEventListener('click', () => { Object.assign(Q, UI_QUALITY[id]); syncControls(); uiQualityMark(); touch(); });
  addReset('qReset', 'q', { after: uiQualityMark });

  // mode
  for (const m of ['m', 'j', 'k']) $('mode-' + m).addEventListener('change', () => { S.mode = m; resetCam(); syncControls(); refresh(false); });

  // buildCard, bindView and initGL register their own overlays and hooks
  readTheme(); buildCard(); initGL(); bindView(); resetCam();
  // the two panels that other modules build: a background picture job and a 3D model job
  for (const [build, host] of [[typeof buildExportPanel === 'function' && buildExportPanel, 'exportPanel'], [typeof buildMeshPanel === 'function' && buildMeshPanel, 'meshPanel']]) {
    if (build) build(host);
    else $(host).innerHTML = '<p class="note">This part of the lab is missing from this copy of the page.</p>';
  }
  $('fig4Show').addEventListener('click', uiFigure4);
  $('fig4Back').addEventListener('click', uiOnePlane);
  for (const [btn, id] of [['twinMerc', 'mercator'], ['twinLathe', 'lathe'], ['twinBulb', 'bulb']]) $(btn).addEventListener('click', () => uiTwin(id));
  $('twinOff').addEventListener('click', uiTwinOff);

  if (!hooks.view.includes(uiViewSync)) hooks.view.push(uiViewSync);
  const retheme = () => { readTheme(); drawStep2d(); touch(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  new ResizeObserver(() => { drawStep2d(); touch(); }).observe(stage);
  new ResizeObserver(() => { drawStep2d(); viewChanged(); }).observe($('step2d'));
  uiFlatPaint(); uiQualityMark(); uiExtremePaint();
  refresh(false);
}
