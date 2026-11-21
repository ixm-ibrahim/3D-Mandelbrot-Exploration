"""One-off edits of src/js/80-ui.js, src/js/75-presets.js and src/js/90-boot.js for round 5 (page). Each
replacement must match exactly once, so a second run changes nothing and says so."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def edit(rel, pairs):
    path = os.path.join(ROOT, rel)
    with io.open(path, encoding='utf-8', newline='') as f:
        src = f.read()
    for old, new in pairs:
        if new in src:
            print('  already done:', new[:60].replace('\n', ' '))
            continue
        if src.count(old) != 1:
            sys.exit('%s: expected one match, found %d, for: %s' % (rel, src.count(old), old[:80]))
        src = src.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(src)
    print('edited', rel)


UI = [
# state
("""  kL: null,          // the L dial of the Kleinian group
""", """  kL: null,          // the L dial of the Kleinian group
  ap: {},            // the control set of each approach, by approach id
"""),
# Julia headings
("""function uiJuliaOptions() {
  const list = [['own', 'Your own values']];
  juliaSaved.forEach((p, i) => list.push(['s' + i, p.name, 'Your saved points']));
  JULIA_PRESETS.forEach((p, i) => { if (p.source !== 'explored') list.push(['p' + i, p.name, 'Classic sets']); });
  JULIA_PRESETS.forEach((p, i) => { if (p.source === 'explored') list.push(['p' + i, p.name, 'Found by exploring']); });
  return list;
}""", """// The heading a shipped entry stands under comes from its `source` in data/julia-presets.json. The headings
// follow one another in this order, after the user's own saved points.
const UI_JULIA_HEADS = ['Classic sets', 'Found by exploring', 'Found with two planes'];
const uiJuliaHead = p => (p.source === 'explored' ? UI_JULIA_HEADS[1] : p.source === 'two planes' ? UI_JULIA_HEADS[2] : UI_JULIA_HEADS[0]);
function uiJuliaOptions() {
  const list = [['own', 'Your own values']];
  juliaSaved.forEach((p, i) => list.push(['s' + i, p.name, 'Your saved points']));
  for (const head of UI_JULIA_HEADS) JULIA_PRESETS.forEach((p, i) => { if (uiJuliaHead(p) === head) list.push(['p' + i, p.name, head]); });
  return list;
}"""),
# the mark: also the "As it was found" button
("""  if (p && p.source !== 'saved' && (S.eq !== 'z^n + c' || S.n !== 2)) text += ' The name belongs to z² + c. With the equation and power set now, the picture is a different one.';
  if (note.textContent !== text) note.textContent = text;
}""", """  if (p && p.source !== 'saved' && (S.eq !== 'z^n + c' || S.n !== 2)) text += ' The name belongs to z² + c. With the equation and power set now, the picture is a different one.';
  if (note.textContent !== text) note.textContent = text;
  // "As it was found" is on show only while it would change something
  const found = $('juliaFound'), d = juliaFoundDiff(p);
  found.hidden = !d;
  if (d) {
    const sets = [d.planes !== undefined && `Planes to ${d.planes}`, d.iter !== undefined && `Iterations to ${d.iter}`].filter(Boolean).join(' and ');
    found.title = `Sets ${sets}, as when this entry was found. Nothing else changes.`;
  }
}"""),
("""  uiOnce('julia', `${S.c}|${S.eq}|${S.n}|${S.approach}`, uiJuliaMark);""",
 """  uiOnce('julia', `${S.c}|${S.eq}|${S.n}|${S.approach}|${S.iter}|${S.param.mercator && S.param.mercator.planes}`, uiJuliaMark);"""),
# Figure 4
("""// Everything back to how the page opens, except the user's saved Julia points and which sections are open.""",
 """// ---------- the two buttons beside the Figure 4 answer in the closing text
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
  presetFrame(UI_FIG4.cam, presetNarrow(), 3.6);
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

// Everything back to how the page opens, except the user's saved Julia points and which sections are open."""),
("""const UI_EXTREME_TEXT = {""", """// What "Show Figure 4" sets besides the approach: the point c, and a camera that shows both circles of beads.
const UI_FIG4 = { c: [-1, 0, 0], cam: { yaw: -1.9, pitch: 0.55, dist: 4.8 } };
const UI_EXTREME_TEXT = {"""),
# listeners
("""  $('juliaFrame').addEventListener('click', () => frameJuliaPreset(juliaEntry(juliaKeyAt(UI.juliaKey))));""",
 """  $('juliaFrame').addEventListener('click', () => frameJuliaPreset(juliaEntry(juliaKeyAt(UI.juliaKey))));
  $('juliaFound').addEventListener('click', () => {
    applyJuliaFound(juliaEntry(juliaKeyAt(UI.juliaKey)));
    if ($('juliaFound').hidden) $('juliaFrame').focus();   // the button has just gone: keep the focus beside it
  });"""),
("""    buildControls('pd-' + r.id, r.params || [], S.param[r.id], uiApproachParam, { idPrefix: 'par-' + r.id + '-', group: 'approach' });""",
 """    UI.ap[r.id] = buildControls('pd-' + r.id, r.params || [], S.param[r.id], uiApproachParam, { idPrefix: 'par-' + r.id + '-', group: 'approach' });"""),
("""  // closing texts that describe a feature are shown only when this copy of the page has that feature
  const has = {
    pillow: APPROACHES.some(a => a.id === 'pillow'), extreme: typeof setExtreme === 'function',
    solid: COLOUR_CONTROLS.some(c => c.key === 'solid'), inside: COLOUR_CONTROLS.some(c => c.key === 'inMode'),
    export: typeof buildExportPanel === 'function', mesh: typeof buildMeshPanel === 'function',
  };
  document.querySelectorAll('[data-needs]').forEach(el => { el.hidden = !has[el.dataset.needs]; });
""", """  $('fig4Show').addEventListener('click', uiFigure4);
  $('fig4Back').addEventListener('click', uiOnePlane);
"""),
]
PRESETS = [
("""
// ----- Kleinian entries
""", """// "As it was found": the planes and the iterations a shipped entry records. They were chosen under the Sphere
// inversions approach. -> those of the two that differ from the page's own now, as { planes?, iter? }, or null
// when there is nothing to change. The planes count only while Sphere inversions is the approach in use: under
// any other approach its planes dial is out of sight and changes nothing in the picture.
function juliaFoundDiff(p) {
  if (!p || p.source === 'saved') return null;
  const d = {}, m = S.param.mercator;
  if (p.planes > 0 && m && ap().id === 'mercator' && m.planes !== p.planes) d.planes = p.planes;
  if (p.iter > 0 && S.iter !== p.iter) d.iter = p.iter;
  return d.planes === undefined && d.iter === undefined ? null : d;
}
// Set them, and nothing else: the point c, the camera and the approach stay. -> whether anything changed.
function applyJuliaFound(p) {
  const d = juliaFoundDiff(p);
  if (!d) return false;
  if (d.planes !== undefined) S.param.mercator.planes = d.planes;
  if (d.iter !== undefined) S.iter = d.iter;
  syncControls();
  if (d.planes !== undefined) uiApproachParam(); else touch();
  uiJuliaMark();
  return true;
}

// ----- Kleinian entries
"""),
]
BOOT = [
("""  resetAll: uiResetAll, saveFile,
};""", """  resetAll: uiResetAll, saveFile, showFigure4: uiFigure4, onePlane: uiOnePlane, juliaFoundDiff, applyJuliaFound,
};"""),
]
edit('src/js/80-ui.js', UI)
edit('src/js/75-presets.js', PRESETS)
edit('src/js/90-boot.js', BOOT)
