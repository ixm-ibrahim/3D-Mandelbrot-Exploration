// The page: builds every control and wires it to the state.
// The sections' groups for resetGroup are in UI_GROUPS. The panels "Save a picture" and "Save a 3D model", built
// by other modules, use 'export' and 'mesh'.
const UI = {
  col: null,         // the colour controls (a buildControls set)
  juliaSel: null,    // the Julia drop-down
  kleinSel: null,    // the Kleinian drop-down
  cutOn: null,       // the "cut the solid open" checkbox
  ex: null,          // the drop-down of trap solid examples in Colour and light
  fly: null,         // the fly-camera checkbox in the View section
  grid: null,        // the Grid checkbox in the View section
  extreme: null,     // the "Extreme ranges" checkbox
  kL: null,          // the L dial of the Kleinian group
  ap: {},            // the control set of each approach, by approach id
  apOrder: [],       // the approaches in the order the menu's list shows them (their places in APPROACHES)
  apInfo: '',        // the id of the entry whose explanation shows beside the open list ('' for none)
  apKeys: false,     // the menu is being worked with the keyboard, so the entry in focus is marked and explained
  flyShown: false,   // what the fly checkbox last showed (the stage switch and the F key change the mode too)
  juliaKey: 'p0',    // the Julia entry last chosen from the list (see juliaEntry)
  kleinAt: 0,        // the Kleinian entry last chosen
  presetCut: false,  // the cut was opened by an equation preset, so the next preset or the Equation reset may close it
  mosaicWas: false,  // the mosaic checkbox as last seen, and what the cut was before the mosaic opened it
  mosaicCut: null,
  only3d: [],        // elements put away while the 2D view is on, because they do nothing there
  seen: {},          // what each mark last showed (see uiOnce)
};
const UI_GROUPS = ['mandel', 'julia', 'klein', 'balls', 'approach', 'eq', 'mod', 'cut', 'colour', 'view', 'q'];   // 'balls': the dials of the second Kleinian group
const UI_FOV_DEG = 35.49;   // the starting field of view (CAM_FOV0) as the dial shows it
// A preset sets every dial of the Quality section, so the same button always gives the same picture.
const UI_QUALITY = {
  qUltra: { res: 0.5, aa: 1, steps: 90, detail: 2, stepk: 0.8, smooth: 1, shadow: false, ao: false, de: 0, normals: 'smooth' },
  qFast: { res: 0.75, aa: 3, steps: 160, detail: 1.25, stepk: 0.8, smooth: 1, shadow: false, ao: true, de: 3, normals: 'sharp' },
  qBal: { res: 1, aa: 12, steps: 260, detail: 1, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
  qFine: { res: 1.5, aa: 32, steps: 450, detail: 0.7, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
};
const UI_EXTREME_TEXT = {
  off: 'Extreme ranges lets most dials reach five to ten times further. Expect slow pictures.',
  on: 'Extreme ranges are on. Dials marked wide reach far past their usual limits, and pictures can get very slow.',
};

// After the approach, the power or the mode changed: panels, texts, figures, scorecard, then the picture.
function refresh() {
  const k = S.mode === 'k';
  $('mandelPanel').hidden = S.mode !== 'm'; $('juliaPanel').hidden = S.mode !== 'j'; $('kleinPanel').hidden = !k;
  ['secApproach', 'secMod'].forEach(id => { $(id).hidden = k; });
  // The table under the picture has no rows for Balls on balls: while it is on show the style sheet puts the table
  // away and one sentence stands there (86-balls.css).
  document.body.classList.toggle('balls-on', ballsShown());
  $('mode-' + S.mode).checked = true;
  if (k) uiApMenu(false);   // the section is put away in the Kleinian view, and its open list with it
  uiApPaint();
  uiJuliaMark(); uiKleinMark(); uiCollapsePaint(); uiEmptyNote();
  buildStep3d(); drawStep2d(); updateCard();
  touch();
  hooks.refresh.forEach(f => f());
}
// A dial of the chosen approach moved. While one sweeps this runs every frame, so it redoes only what depends
// on the dial: that approach's formula text, the 3D step figure, the scorecard and the picture.
function uiApproachParam() {
  const a = ap(), text = a.formula(S.param[a.id], S.n);
  $('f-' + a.id).textContent = text;
  if (UI.apInfo === a.id) { const f = $('apInfo').querySelector('code'); if (f) f.textContent = text; }
  buildStep3d(); updateCard();
  touch();
}

// The Approach menu
// A button (#apMenuBtn) shows the chosen approach and opens the list of all of them (#rules inside #apPop), one
// set of radios ap-<id>. Under the menu stands one panel per approach (its formula f-<id> and its dials pd-<id>);
// only the chosen one shows. An entry's explanation shows in #apInfo while the mouse or the keyboard focus is on
// it; "About this approach" opens the same text for the chosen approach in #apAbout.
// What an entry says about itself: its name and formula (left out where they stand beside it), its tag, its
// about, and the notes among its dials that depend on no dial (uiApStatic). Name, tag and about are HTML; a note
// is plain text.
const uiApStatic = s => s.type === 'note' && !s.when;
function uiApText(r, withName) {
  const box = document.createElement('div');
  box.innerHTML = (withName ? `<p class="ap-info-name">${r.name}</p>` : '') + `<p class="ap-info-tag">${r.tag || ''}</p>` +
    (withName ? '<code></code>' : '') + (r.about ? `<p class="note">${r.about}</p>` : '');
  const f = box.querySelector('code');
  if (f) f.textContent = r.formula(S.param[r.id], S.n);
  for (const s of r.params || []) if (uiApStatic(s)) { const p = document.createElement('p'); p.className = 'note'; p.textContent = s.text; box.appendChild(p); }
  return box;
}
// Show the explanation of one entry beside the open list (pass nothing to put it away).
function uiApInfo(r) {
  const box = $('apInfo'), id = r ? r.id : '';
  document.querySelectorAll('#rules .rule.is-info').forEach(el => { if (el.dataset.ap !== id) el.classList.remove('is-info'); });
  if (UI.apInfo === id && box.hidden === !r) return;
  UI.apInfo = id;
  box.textContent = '';
  if (r) { box.append(...uiApText(r, true).childNodes); box.scrollTop = 0; document.querySelector(`#rules .rule[data-ap="${id}"]`).classList.add('is-info'); }
  box.hidden = !r;
}
// How far down the window something is held, in pixels: the pinned picture on a narrow window (85-pin.css), or
// else the top row of the controls.
function uiHeldTop() {
  const root = document.documentElement;
  const held = matchMedia('(max-width: 920px)').matches && root.classList.contains('pin-on') && !root.classList.contains('pin-let-go');
  return held ? Math.round(document.querySelector('.bench-main').getBoundingClientRect().height) + 8 : 96;
}
// Open or close the list. `focus`: the keyboard focus goes along (into the list, or back onto the button).
function uiApMenu(open, focus) {
  const pop = $('apPop'), btn = $('apMenuBtn');
  open = !!open;
  if (open === !pop.hidden) return;
  pop.hidden = !open;
  btn.setAttribute('aria-expanded', String(open));
  $('apMenu').classList.toggle('is-open', open);
  if (!open) {
    document.querySelectorAll('#rules .rule.is-focus').forEach(el => el.classList.remove('is-focus'));
    uiApInfo(null);
    if (focus) btn.focus({ preventScroll: true });
    return;
  }
  // The list must fit in the window under whatever is held at its top (uiHeldTop). The button stays in view above
  // the list, so the room starts under it. The style sheet reads the room from --ap-room.
  const top = uiHeldTop() + btn.parentNode.offsetHeight + 8;
  pop.style.scrollMarginTop = top + 'px';
  pop.style.setProperty('--ap-room', Math.max(150, innerHeight - top - 12) + 'px');
  // the chosen entry in view inside the list, then the whole list inside the window
  const on = $('ap-' + ap().id), row = on.closest('.rule'), list = $('rules');
  list.scrollTop = Math.max(0, row.offsetTop - (list.clientHeight - row.offsetHeight) / 2);
  pop.scrollIntoView({ block: 'nearest' });
  if (focus) on.focus({ preventScroll: true });
}
// The next (1) or previous (-1) entry in the order the list shows them, round and round.
function uiApStep(dir) {
  const order = UI.apOrder, at = order.indexOf(S.approach);
  if (!order.length) return;
  S.approach = order[((at < 0 ? 0 : at + dir) % order.length + order.length) % order.length];
  refresh();
}
// Make the menu show the state: the button, the list, the chosen approach's panel and the open explanation.
function uiApPaint() {
  const a = ap();
  if ($('apMenuName').textContent !== a.name) $('apMenuName').innerHTML = a.name;
  document.querySelectorAll('#rules .rule').forEach(el => el.classList.toggle('is-on', el.dataset.ap === a.id));
  APPROACHES.forEach((x, i) => {
    $('ap-' + x.id).checked = i === S.approach;
    $('f-' + x.id).textContent = x.formula(S.param[x.id], S.n);
  });
  document.querySelectorAll('#apPanels .ap-panel').forEach(el => { el.hidden = el.dataset.ap !== a.id; });
  // "Reset the approach dials" has nothing to do for an approach without dials
  $('approachReset').hidden = !(a.params || []).some(s => s.key !== undefined);
  // An approach that writes the whole step of the orbit itself (the custom one) has no use for the equation box.
  const whole = !!a.whole;
  $('eqPreset').closest('.field').hidden = whole; $('eq').closest('.field').hidden = whole; $('eqWhole').hidden = !whole;
  $('apCustomBtn').setAttribute('aria-pressed', String(a.id === 'custom')); $('apCustomBtn').classList.toggle('is-on', a.id === 'custom');
  const about = $('apAbout');
  if (!about.hidden && about.dataset.ap !== a.id) { about.dataset.ap = a.id; about.textContent = ''; about.append(...uiApText(a, false).childNodes); }
  if (UI.apInfo) { const r = APPROACHES.find(x => x.id === UI.apInfo), f = $('apInfo').querySelector('code'); if (r && f) f.textContent = r.formula(S.param[r.id], S.n); }
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
// Show which equation preset the two formulas are (or "My own formula"), and that preset's note.
function uiEqMark() {
  const i = PRESETS.findIndex(p => p.eq === S.eq && p.z0 === S.z0), note = $('eqNote');
  $('eqPreset').value = String(i);
  note.textContent = (i >= 0 && PRESETS[i].note) || '';
  note.hidden = !note.textContent;
}

// Julia points: one drop-down holding the user's saved points, then the shipped ones under these headings, in
// this order. The heading of a shipped entry comes from its `source` in JULIA_PRESETS.
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
// Make the drop-down, its note and the delete button show where the point c stands.
function uiJuliaMark() {
  const key = juliaKeyAt(UI.juliaKey), p = juliaEntry(key), note = $('juliaNote');
  UI.juliaSel.sync();
  $('juliaDelete').hidden = key[0] !== 's';
  let text = !p ? `Your own point, c = (${S.c.map(x => dialFmt(x)).join(', ')}). Save it to keep it in the list.`
    : p.source === 'saved' ? 'One of your saved points.' : p.note;
  if (p && p.source !== 'saved' && (S.eq !== 'z^n + c' || S.n !== 2)) text += ' The name belongs to z² + c. With the equation and power set now, the picture is a different one.';
  if (note.textContent !== text) note.textContent = text;
  // "As it was found" is on show only while it would change something, and its words say what
  const found = $('juliaFound'), d = juliaFoundDiff(p), words = juliaFoundWords(d);
  found.hidden = !d;
  if (found.textContent !== words.label) found.textContent = words.label;
  found.title = words.title;
}
// The row Balls on balls of the Approach menu: goes to the Kleinian view, that group, and its start view. Chosen
// under the Learn tab, it leaves Learn the way the Kleinian button under Show does.
function uiBallsShow() {
  uiApMenu(false);
  S.k.group = 1;
  if (S.learn) $('mode-k').click();
  S.mode = 'k';
  ballsFrame();
  syncControls();
  refresh();
  // The list the click was made in has gone, and the controls column is much shorter: bring the Kleinian panel to
  // the top of the window, under whatever is held there (uiHeldTop).
  const panel = $('kleinPanel');
  panel.open = true;
  panel.style.scrollMarginTop = uiHeldTop() + 'px';
  panel.scrollIntoView({ block: 'start' });
}
// The explanation of the row Balls on balls, beside the open list (the approaches get theirs from uiApInfo).
function uiBallsInfo() {
  const box = $('apInfo');
  document.querySelectorAll('#rules .rule.is-info').forEach(el => el.classList.remove('is-info'));
  if (UI.apInfo === 'balls' && !box.hidden) return;
  UI.apInfo = 'balls';
  box.innerHTML = '<p class="ap-info-name"></p><p class="ap-info-tag"></p><p class="note"></p><p class="note">One click shows it in the Kleinian view, where its dials are.</p>';
  const p = box.querySelectorAll('p');
  p[0].textContent = BALLS_NAME; p[1].textContent = BALLS_TAG; p[2].textContent = BALLS_NOTE;
  box.scrollTop = 0; box.hidden = false;
}
function uiKleinMark() {
  // the panel holds two groups: the parts of the one that is not chosen are put away
  const balls = ballsOn(), bw = $('ballsWarn'), bt = ballsTrouble();
  $('kleinPart').hidden = balls; $('ballsPart').hidden = !balls;
  $('kleinGroup' + (balls ? 1 : 0)).checked = true;
  if (bw.textContent !== bt) bw.textContent = bt;
  bw.hidden = !bt;
  UI.kleinSel.sync();
  // the warning is for the user's own values only: every entry of the list is a known picture
  const i = kleinPresetAt(UI.kleinAt), note = $('kleinNote'), warn = $('kleinWarn'), trouble = i >= 0 ? '' : kleinTrouble();
  const text = i >= 0 ? KLEIN_PRESETS[i].note : 'Your own values. Pick an entry from the list to go back to a known picture.';
  if (note.textContent !== text) note.textContent = text;
  if (warn.textContent !== trouble) warn.textContent = trouble;
  warn.hidden = !trouble;
  UI.kL.el.hidden = !S.k.three;   // L belongs to the third map
}
const uiSections = () => [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden);
function uiCollapsePaint() {
  const open = uiSections().some(d => d.open), b = $('collapseAll'), text = open ? 'Collapse all' : 'Expand all';
  if (b.textContent !== text) b.textContent = text;
}
// The 2D view: its label says which slice is drawn, and controls that only act on the 3D picture are put away.
function uiFlatPaint() {
  $('flatZ').textContent = `(slice at z = ${dialFmt(+(+S.cut).toFixed(4)).replace('-', '−')})`;
  UI.only3d.forEach(el => { el.hidden = !!S.flat; });
  document.querySelectorAll('.only2d').forEach(el => { el.hidden = !S.flat; });
}
// Mark the quality preset whose values the Quality section holds, if any.
function uiQualityMark() {
  for (const id of Object.keys(UI_QUALITY)) {
    const on = Object.entries(UI_QUALITY[id]).every(([key, v]) => S.q[key] === v), b = $(id);
    b.classList.toggle('is-on', on);
    b.setAttribute('aria-pressed', String(on));
  }
}
function uiExtremePaint() {
  UI.extreme.sync();
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
// The Grid button on the picture and the Grid checkbox show the same setting.
function uiGridPaint() { $('gridBtn').setAttribute('aria-pressed', String(S.view.grid)); UI.grid.sync(); }
// Called at most once a frame after anything changed (the stage, the keys and other modules change the state too,
// not only the controls here): keeps every mark on the page in step with the state.
function uiViewSync() {
  if (UI.flyShown !== !!S.view.fly) { UI.flyShown = !!S.view.fly; UI.fly.sync(); }
  uiOnce('grid', String(S.view.grid), uiGridPaint);
  uiOnce('flat', `${S.flat}|${S.cut}`, uiFlatPaint);
  uiOnce('q', JSON.stringify(S.q), uiQualityMark);
  uiOnce('julia', `${S.c}|${S.eq}|${S.n}|${S.approach}|${S.iter}|${S.param.fold.planes}`, uiJuliaMark);
  // the warning under the Kleinian list also depends on where the camera stands (see kleinSwallowed)
  uiOnce('klein', JSON.stringify(S.k) + (kleinSwallowed() ? '|near' : '') + (kleinReach() > S.view.bound ? '|cut' : '') + '|' + ballsTrouble(), uiKleinMark);
  uiOnce('example', `${S.mode}|${S.c}|${JSON.stringify(S.k)}|${[...EXAMPLE_KEYS, ...EXAMPLE_CENTRE].map(key => S.colour[key])}`, UI.ex.sync);
  uiOnce('empty', `${S.mode}|${S.eq}|${S.n}`, uiEmptyNote);
  uiOnce('extreme', String(!!S.extreme), uiExtremePaint);
  // on a narrow screen the hint has no room on the picture, so a copy of it sits under the stage
  const hint = stage.querySelector('.hint'), below = $('hintBelow');
  if (below.textContent !== hint.textContent) below.textContent = hint.textContent;
}
// Everything back to how the page opens, except the user's saved Julia points and which sections are open.
function uiResetAll() {
  learnReset();
  setExtreme(false);
  S.flat = false; S.mode = 'm'; S.approach = 0;
  S.k.group = 0;   // the Kleinian view goes back to its first group
  UI.presetCut = false; UI.mosaicCut = null; UI.mosaicWas = false;
  resetGroup(UI_GROUPS);
  resetGroup(['export', 'mesh']);   // the settings of the two save panels; a job that is running keeps its own copy
  exportSizeNote();
  S.cutOn = false;   // resetting the height dial switches the cut on, as moving it by hand does
  $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
  $('juliaName').value = ''; $('juliaSaveNote').hidden = true;
  UI.juliaKey = 'p0'; UI.kleinAt = 0;
  resetZoomLimits(); resetCam();
  syncControls();
  refresh();
}

function boot() {
  initState();
  juliaSavedLoad();
  // Tell the style sheet where the picture starts on the page, so that its height stops short of the window's
  // lower edge (.stage in 00-base.css). The masthead changes height with the window's width and when the fonts
  // arrive, so this is measured again then, on the bench: the picture stays put while the page scrolls under it.
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
    // switching off also pulls every value back inside its usual limits (see setExtreme)
    setExtreme(!!v);
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
  $('gridBtn').addEventListener('click', () => { S.view.grid = !S.view.grid; touch(); });

  // Mandelbrot options: the Julia mosaic. The cells are stacked in depth too, and seen from outside they hide
  // one another, so ticking the box in the 3D view also cuts the solid open at z = 0. Unticking it puts the cut
  // back as it was, unless the user has moved it since.
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

  // Kleinian group. The list is not part of the reset group: the dials and the checkbox restore every value.
  // The labels are upper case, which would print the Greek letter μ as a Latin M: class asis keeps it as typed.
  const K = S.k, kd = (id, label, min, max, step, key, o) => addDial('kleinDials', id, label, min, max, step, () => K[key], v => { K[key] = v; uiKleinMark(); touch(); }, { ...o, group: 'klein' });
  const kHead = { cusp: 'Cusps: pearls that just touch', inside: 'Above a cusp: strings that do not close', explored: 'Found by exploring', sphere: 'Turning-out sphere' };
  const kGroup = p => kHead[p.source.split(' ')[0]];
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
  // The choice between the two groups, and the second group's own part (its dials are the group 'balls'). A
  // change of group is a change of picture, so the view goes to that group's start.
  for (const g of [0, 1]) $('kleinGroup' + g).addEventListener('change', () => { K.group = g; resetCam(); syncControls(); refresh(); });
  $('ballsNote').textContent = BALLS_NOTE;
  // Each of the two dials below sets its own number and nothing else (ballsSetShare and ballsSetRho in 32-balls.js).
  const bSet = () => { uiKleinMark(); touch(); };
  addDial('ballsDials', 'ballsSize', 'Size of the neighbours, % of the middle ball', 2, 400, 0.1, () => +ballsShare(ballsT(K.bt)).toFixed(2), v => { ballsSetShare(v); bSet(); },
    { lo: 1, hi: 2000, def: +ballsShare(BALLS_T).toFixed(2), group: 'balls', help: 'How wide the two big neighbours are, measured against the middle ball: smaller neighbours give a shorter chain. Past 100, with the second sphere at 100, the balls run into one another.' });
  addDial('ballsDials', 'ballsRho', 'Second sphere, % of the first', 2, 100, 1, ballsRhoShown, v => { ballsSetRho(v); bSet(); },
    { lo: 2, hi: 100, def: 100, group: 'balls', help: 'The sphere inversions use two spheres, and this is the size of the second against the first: with a smaller one the neighbours can be larger than the middle ball before the balls run into one another, and their buds are smaller and stand further apart.' });
  addSelect('ballsDials', 'ballsGrid', 'Whole numbers', BALLS_GRIDS, () => K.bgrid | 0, v => { K.bgrid = +v | 0; bSet(); },
    { def: 0, group: 'balls', help: 'Where the buds sit: four-fold round the chain (square grid), six-fold (honeycomb grid), or only round the flat picture (a line only); the flat cut is the same for all three.' });
  // With fewer than BALLS_ROUNDS_FEW rounds the picture comes out in broken shells, and ballsTrouble says so.
  addDial('ballsDials', 'ballsDepth', 'Depth of the search', BALLS_ROUNDS_MIN, 100, 1, () => K.bit, v => { K.bit = Math.max(BALLS_ROUNDS_MIN, Math.round(v)); bSet(); },
    { lo: BALLS_ROUNDS_MIN, hi: 1000, int: true, def: BALLS_ROUNDS, group: 'balls', help: 'How many rounds of the search a point may take before it counts as inside: the larger the neighbours, the more rounds the far balls of the chain need, and with too few they come out swollen.' });
  $('ballsFrame').addEventListener('click', ballsFrame);
  addReset('ballsReset', 'balls', { after: uiKleinMark });

  // The Approach menu (see uiApMenu). The list stands under the headings of APPROACH_GROUPS, each group in the
  // order of APPROACHES. In the open list the arrow keys move the focus without choosing, so that each explanation
  // can be read first; Enter or the space bar chooses.
  const apRule = (r, i, host) => {
    const el = document.createElement('div');
    el.className = 'rule'; el.dataset.ap = r.id;
    el.innerHTML = `<label class="rule-head"><input type="radio" name="approach" id="ap-${r.id}" value="${i}"${i === S.approach ? ' checked' : ''}><span class="mark"></span><span class="name">${r.name}</span><span class="tag">${r.tag || ''}</span></label>`;
    host.appendChild(el);
    const panel = document.createElement('div');
    panel.className = 'ap-panel'; panel.dataset.ap = r.id; panel.hidden = i !== S.approach;
    panel.innerHTML = `<code id="f-${r.id}"></code><div id="pd-${r.id}" class="sec-inner"></div>`;
    $('apPanels').appendChild(panel);
    UI.apOrder.push(i);
    const inp = el.querySelector('input');
    inp.addEventListener('change', () => { S.approach = i; refresh(); });
    inp.addEventListener('focus', () => { const seen = UI.apKeys || inp.matches(':focus-visible'); el.classList.toggle('is-focus', seen); if (seen) uiApInfo(r); });
    inp.addEventListener('blur', () => { el.classList.remove('is-focus'); if (UI.apInfo === r.id && !el.matches(':hover')) uiApInfo(null); });
    // A note that depends on no dial is part of the explanation (uiApText), so it does not stand among the dials.
    UI.ap[r.id] = buildControls('pd-' + r.id, (r.params || []).filter(s => !uiApStatic(s)), S.param[r.id], uiApproachParam, { idPrefix: 'par-' + r.id + '-', group: 'approach' });
  };
  for (const g of APPROACH_GROUPS) {
    const list = APPROACHES.map((r, i) => [r, i]).filter(([r]) => r.group === g.id);
    if (!list.length) continue;
    const box = document.createElement('div');
    box.className = 'rule-group';
    box.id = 'apg-' + g.id; box.setAttribute('role', 'group'); box.setAttribute('aria-labelledby', 'apgh-' + g.id);
    const head = document.createElement('p');
    head.className = 'label rule-group-head'; head.id = 'apgh-' + g.id; head.textContent = g.title;
    box.appendChild(head);
    $('rules').appendChild(box);
    list.forEach(([r, i]) => apRule(r, i, box));
  }
  // Balls on balls is the second group of the Kleinian view, not an approach. It has a row of its own in the open
  // menu, under the list, with its own heading. The row is a button, not one of the radios, and is not in APPROACHES.
  const cousin = document.createElement('div');
  cousin.className = 'cousin-group'; cousin.id = 'apg-cousin'; cousin.setAttribute('role', 'group'); cousin.setAttribute('aria-labelledby', 'apgh-cousin');
  cousin.innerHTML = `<p class="label cousin-group-head" id="apgh-cousin">A cousin, not a rule</p><div class="cousin-row" id="apBallsRow"><button type="button" class="rule-head cousin-head" id="ap-balls" title="Shows this object in the Kleinian view, where its dials are."><span class="mark"></span><span class="name">${BALLS_NAME}</span><span class="cousin-tag">${BALLS_TAG}</span></button></div>`;
  $('rules').after(cousin);   // right under the list, which holds the approaches and nothing else
  $('ap-balls').addEventListener('click', uiBallsShow);
  $('ap-balls').addEventListener('keydown', e => {
    if (e.key === 'Escape') { e.preventDefault(); uiApMenu(false, true); }
    else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); const all = $('rules').querySelectorAll('input[type=radio]'); if (all.length) all[all.length - 1].focus(); }
  });
  // its explanation shows while the mouse is over the row or the keyboard is on it
  cousin.addEventListener('pointerover', e => { if (e.pointerType !== 'touch') uiBallsInfo(); });
  $('ap-balls').addEventListener('focus', () => { if (UI.apKeys || $('ap-balls').matches(':focus-visible')) uiBallsInfo(); });
  $('ap-balls').addEventListener('blur', () => { if (UI.apInfo === 'balls' && !cousin.matches(':hover')) uiApInfo(null); });
  // the menu: its button, the two step buttons beside it, and the open list
  const apMenu = $('apMenu'), apBtn = $('apMenuBtn'), apPop = $('apPop'), apList = $('rules');
  const apById = id => APPROACHES.find(r => r.id === id), apRadios = () => [...apList.querySelectorAll('input[type=radio]')];
  // The entry the keyboard stands on gets its ring and its explanation here, by hand. The focus events of the
  // radios do the same for the Tab key, but a window that is not in front delivers no focus events.
  const apMark = inp => {
    apList.querySelectorAll('.rule.is-focus').forEach(el => el.classList.remove('is-focus'));
    const el = inp && inp.closest('.rule');
    if (el) { el.classList.add('is-focus'); uiApInfo(apById(el.dataset.ap)); }
  };
  // a click that comes from the keyboard (Enter or the space bar) has detail 0
  apBtn.addEventListener('click', e => { UI.apKeys = e.detail === 0; uiApMenu(apPop.hidden, true); if (UI.apKeys && !apPop.hidden) apMark($('ap-' + ap().id)); });
  apBtn.addEventListener('keydown', e => {
    if (e.ctrlKey || e.metaKey) return;
    if (e.key === 'Escape' && !apPop.hidden) { e.preventDefault(); uiApMenu(false, true); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      // closed, the arrows go straight to the next or previous approach, as on a drop-down; Alt opens the list
      if (apPop.hidden && !e.altKey) uiApStep(e.key === 'ArrowDown' ? 1 : -1);
      else if (apPop.hidden) uiApMenu(true, true);
      else { UI.apKeys = true; $('ap-' + ap().id).focus(); apMark($('ap-' + ap().id)); }
    }
  });
  $('apPrev').addEventListener('click', () => uiApStep(-1));
  $('apNext').addEventListener('click', () => uiApStep(1));
  apList.addEventListener('keydown', e => {
    const all = apRadios(), at = all.indexOf(e.target);
    if (at < 0 || e.ctrlKey || e.metaKey || e.altKey) return;
    const to = { ArrowDown: at + 1, ArrowRight: at + 1, ArrowUp: at - 1, ArrowLeft: at - 1, Home: 0, End: all.length - 1 }[e.key];
    if (to === all.length && e.key !== 'End') { e.preventDefault(); UI.apKeys = true; apMark(null); $('ap-balls').focus(); uiBallsInfo(); }   // past the last approach: the row Balls on balls
    else if (to !== undefined) { e.preventDefault(); UI.apKeys = true; const t = all[clamp(to, 0, all.length - 1)]; t.focus(); apMark(t); }
    else if (e.key === 'Enter') { e.preventDefault(); e.target.click(); }
    else if (e.key === 'Escape') { e.preventDefault(); uiApMenu(false, true); }
  });
  // A click on an entry chooses it (the radio's change does that) and closes the list.
  apList.addEventListener('click', e => { if (e.target.matches && e.target.matches('input[type=radio]')) uiApMenu(false, apPop.contains(document.activeElement)); });
  // the explanation follows the mouse over the entries; a touch chooses
  apList.addEventListener('pointerover', e => {
    const el = e.pointerType !== 'touch' && e.target.closest && e.target.closest('.rule');
    if (el) uiApInfo(apById(el.dataset.ap));
  });
  apPop.addEventListener('pointerleave', e => {
    if (e.pointerType === 'touch') return;
    const el = apList.querySelector('.rule.is-focus');
    if (!el && UI.apKeys && document.activeElement === $('ap-balls')) uiBallsInfo();   // the keyboard stands on the row Balls on balls
    else uiApInfo(el ? apById(el.dataset.ap) : null);
  });
  // the list closes when the pointer goes down, or the focus lands, anywhere outside the menu
  document.addEventListener('pointerdown', e => { UI.apKeys = false; if (!apPop.hidden && !apMenu.contains(e.target)) uiApMenu(false); });
  apMenu.addEventListener('focusout', e => { if (!apPop.hidden && e.relatedTarget && !apMenu.contains(e.relatedTarget)) uiApMenu(false); });
  // "About this approach": the explanation of the chosen approach, under the menu
  $('apAboutBtn').addEventListener('click', () => {
    const box = $('apAbout'), open = box.hidden;
    box.hidden = !open; box.dataset.ap = '';
    $('apAboutBtn').setAttribute('aria-expanded', String(open));
    $('apAboutBtn').textContent = open ? 'Hide the explanation' : 'About this approach';
    uiApPaint();
  });
  // This button puts back the dials on show: those of the chosen approach, which stays chosen.
  addReset('approachReset', [], { label: 'Reset the approach dials', after: () => { const set = UI.ap[ap().id]; if (set) set.reset(); } });

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
  addDial('powHost', 'pow', 'Power n', -8, 10, 0.1, () => S.n, v => { S.n = v; refresh(); }, { lo: -16, hi: 24, xmin: -40, xmax: 60, xlo: -100, xhi: 200, def: 2, group: 'eq' });
  addDial('eqDials', 'iter', 'Iterations', 3, 60, 1, () => S.iter, v => { S.iter = Math.round(v); touch(); }, { hi: 400, xmax: 400, xhi: 4000, int: true, def: 14, group: 'eq' });
  // this button is about the equation: the view, the approach and its dials stay
  addReset('eqReset', 'eq', { label: 'Reset the equation', after: () => {
    $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
    if (UI.presetCut) { S.cutOn = false; UI.presetCut = false; UI.cutOn.sync(); }
    refresh();
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
  // belongs to no reset group: an example is something to jump to, not a setting.
  const solidC = UI.col.controls.find(c => c.id === 'col-solid'), exHost = document.createElement('div');
  exHost.className = 'sec-inner'; exHost.id = 'exampleHost';
  solidC.el.after(exHost);
  UI.ex = addSelect(exHost, 'trapExamples', 'Examples', [[-1, 'Choose one to try'], ...EXAMPLES.map((e, i) => [i, e.name, e.head])], exampleAt, i => applyExample(EXAMPLES[i]),
    { help: 'Trap solids that work well. An example sets the kind of picture with its Julia point or Kleinian group, the trap shape, what the trap does, its thickness, skipped steps and radius, the trap centre (back to the middle), and the camera. Everything else stays as you left it, so with another approach, power or equation the same example gives a different object.' });
  $('trapExamples').options[0].disabled = true;
  const follow = () => { exHost.hidden = solidC.el.hidden; };
  new MutationObserver(follow).observe(solidC.el, { attributes: true, attributeFilter: ['hidden'] });
  follow();

  // view
  UI.fly = only3d(addCheck('viewDials', 'viewFly', 'Fly camera', () => S.view.fly, v => setCamMode(!!v), { def: false, group: 'view', help: 'Same as the Arcball and Fly buttons on the picture. Flying moves the camera itself: drag to look, W A S D to move.' }));
  UI.grid = addCheck('viewDials', 'viewGrid', 'Grid', () => S.view.grid, v => { S.view.grid = !!v; touch(); }, { def: false, group: 'view', help: 'Lines at whole numbers on the plane z = 0, with its two axes. The Grid button on the picture does the same.' });
  // the camera needs no redraw for a new speed, only its slider on the stage has to follow
  only3d(addDial('viewDials', 'viewSpeed', 'Fly speed, units per second', 0.01, 5, 0.01, () => S.view.speed, v => { S.view.speed = v; viewChanged(); }, { lo: CAM_LIM.speed[0], hi: CAM_LIM.speed[1], xmax: CAM_LIM.speed[1], def: 1, group: 'view' }));
  only3d(addDial('viewDials', 'viewBound', 'Drawing radius', 1, 100, 0.5, () => S.view.bound, v => { S.view.bound = v; touch(); }, { lo: 0.5, hi: 500, xmax: 1000, xhi: 5000, def: 8, group: 'view', help: 'Nothing is drawn outside a ball of this radius around the centre. Raise it when a picture is cut off far out.' }));
  // The state holds the tangent of half the angle; the dial shows the whole angle in degrees. The starting
  // value is put back exactly, because preset cameras are framed for it.
  only3d(addDial('viewDials', 'viewFov', 'Field of view, degrees', 10, 120, 1, () => +(2 * Math.atan(S.view.fov) * 180 / PI).toFixed(2),
    v => { S.view.fov = Math.abs(v - UI_FOV_DEG) < 0.006 ? CAM_FOV0 : Math.tan(v * PI / 360); touch(); }, { lo: 2, hi: 150, xmin: 1, xmax: 170, xlo: 0.5, xhi: 175, def: UI_FOV_DEG, group: 'view' }));
  addReset('viewReset', 'view', { after: () => { resetZoomLimits(); touch(); } });

  // quality
  const Q = S.q, qd = (id, label, min, max, step, key, o) => addDial('qDials', id, label, min, max, step, () => Q[key], v => { Q[key] = v; uiQualityMark(); touch(); }, { ...o, group: 'q' });
  qd('qres', 'Resolution, × screen pixels', 0.25, 2, 0.05, 'res', { lo: 0.1, hi: 3, xmax: 4, xhi: 6 });
  qd('qaa', 'Refining passes', 1, 64, 1, 'aa', { hi: 400, xmax: 400, xhi: 4000, int: true });
  only3d(qd('qsteps', 'Ray steps, at most', 60, 700, 10, 'steps', { lo: 20, hi: 3000, xmax: 4000, xhi: 20000, int: true,
    help: 'The most steps one ray may take. Raise it when far or thin parts go missing. (Balls on balls may take twice this number.)' }));
  only3d(qd('qdetail', 'Surface threshold, pixels', 0.2, 4, 0.05, 'detail', { lo: 0.02, hi: 20, xmin: 0.02, xmax: 20, xlo: 0.002, xhi: 100,
    help: 'A ray stops when it is this close to the surface, measured in screen pixels. Smaller shows finer detail and takes longer.' }));
  // The upper limit is 1.2 for typed values and with extreme ranges too: above it the rays step over the surface.
  only3d(qd('qstepk', 'Ray step, share of the distance estimate', 0.2, 1.2, 0.01, 'stepk', { lo: 0.05, hi: 1.2, xmin: 0.02, xmax: 1.2, xlo: 0.005, xhi: 1.2,
    help: 'Each ray step covers this share of the estimated distance to the surface. Lower is safer and slower. Higher is faster and can punch holes; the dial stops at 1.2 because beyond it the rays step over the solid and the picture goes empty. In the Kleinian view anything above 0.5 counts as 0.5 (for Balls on balls: anything above 0.9 counts as 0.9).' }));
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
  for (const m of ['m', 'j', 'k']) $('mode-' + m).addEventListener('change', () => { S.mode = m; resetCam(); syncControls(); refresh(); });

  // buildCard, bindView and initGL register their own overlays and hooks
  readTheme(); buildCard(); initGL(); bindView(); resetCam();
  // the two panels that other modules build: a background picture job and a 3D model job
  buildExportPanel('exportPanel'); buildMeshPanel('meshPanel');

  hooks.view.push(uiViewSync);
  const retheme = () => { readTheme(); drawStep2d(); touch(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  new ResizeObserver(() => { drawStep2d(); touch(); }).observe(stage);
  new ResizeObserver(() => { drawStep2d(); viewChanged(); }).observe($('step2d'));
  uiFlatPaint(); uiQualityMark(); uiExtremePaint();
  refresh();
}
