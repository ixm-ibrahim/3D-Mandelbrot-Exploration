# Round 12, page: the edits to src/js/80-ui.js, as exact replacements (each must match once).
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, 'src', 'js', '80-ui.js')
src = io.open(path, encoding='utf-8').read()
EDITS = []
def rep(old, new):
    EDITS.append((old, new))

# --- constants
rep("""// What "Show Figure 4" sets besides the approach: the point c, and a camera that shows both circles of beads.""",
    """// What "Show Figure 4" sets besides the approach (Sphere inversions, two planes): the point c, and a camera that
// shows both circles of beads.""")
rep("""const UI_TWIN = { mercator: 1.15, lathe: 1.6, bulb: 1.35 };
const UI_TWIN_ROOM = 3;
""", """const UI_TWIN = { mercator: 1.15, lathe: 1.6, bulb: 1.35 };
const UI_TWIN_ROOM = 3;
// The two buttons beside the quaternion answer in the closing text, by approach id: the same for the plain
// Mandelbrot solid of that approach (no flip). The rings of the quaternion square and the body of the twisted one
// both stand further out from the x-axis than the flat set does.
const UI_QUAT = { lathe: 1.25, tilt: 1.35 };
const UI_QUAT_ROOM = 3;
""")

# --- refresh: the mark of the chosen entry goes by its id, not by its place in the list
rep("""  document.querySelectorAll('.rule').forEach((el, i) => el.classList.toggle('is-on', i === S.approach));""",
    """  document.querySelectorAll('#rules .rule').forEach(el => el.classList.toggle('is-on', el.dataset.ap === ap().id));""")

# --- As it was found: the words on the button
rep("""  // "As it was found" is on show only while it would change something
  const found = $('juliaFound'), d = juliaFoundDiff(p);
  found.hidden = !d;
  if (d) {
    const sets = [d.planes !== undefined && `Planes to ${d.planes}`, d.iter !== undefined && `Iterations to ${d.iter}`].filter(Boolean).join(' and ');
    found.title = `Sets ${sets}, as when this entry was found. Nothing else changes.`;
  }
}""", """  // "As it was found" is on show only while it would change something, and its words say what
  const found = $('juliaFound'), d = juliaFoundDiff(p), words = juliaFoundWords(d);
  found.hidden = !d;
  if (found.textContent !== words.label) found.textContent = words.label;
  found.title = words.title;
}""")

# --- the key of the Julia mark
rep("""`${S.c}|${S.eq}|${S.n}|${S.approach}|${S.iter}|${S.param.mercator && S.param.mercator.planes}`""",
    """`${S.c}|${S.eq}|${S.n}|${S.approach}|${S.iter}|${S.param.fold && S.param.fold.planes}`""")

# --- Show Figure 4 and Back to one plane
rep("""// "Show Figure 4": the Julia set for c = -1 under Sphere inversions with two planes, which is where the page
// draws the picture of Figure 4 in Kučera's paper. It sets everything that picture depends on, from any state:
// what would show another solid (the equation, the modifiers, a trap that is the solid) or hide this one (the
// 2D view, the cut) is put back too. Iterations, quality and colours stay the user's.
function uiFigure4() {
  const p = S.param.mercator;
  uiApQuiet('mercator');
  S.flat = false; S.mode = 'j'; S.approach = APPROACHES.findIndex(a => a.id === 'mercator');
  p.planes = 2; p.turn = 0; p.lift = 0;
""", """// The place of an approach in APPROACHES, by its id (-1 when this page does not have it).
const uiApIndex = id => APPROACHES.findIndex(a => a.id === id);
// "Show Figure 4": the Julia set for c = -1 under the entry Sphere inversions, two planes, which is where the page
// draws the picture of Figure 4 in Kučera's paper. It sets everything that picture depends on, from any state:
// that entry's dials (Planes 2, Lift 0), and what would show another solid (the equation, the modifiers, a trap
// that is the solid) or hide this one (the 2D view, the cut) is put back too. Iterations, quality and colours
// stay the user's, and so do the dials of the other entries.
function uiFigure4() {
  const i = uiApIndex('fold');
  if (i < 0) return;
  uiApQuiet('fold');
  S.flat = false; S.mode = 'j'; S.approach = i;
  Object.assign(S.param.fold, { planes: 2, lift: 0 });
""")
rep("""// "Back to one plane": the planes dial of Sphere inversions goes to 1, and that approach is the one on show.
// The point c, the camera and everything else stay. Planes mean nothing to a Kleinian group, so from there the
// page goes to the Julia set.
function uiOnePlane() {
  uiApQuiet('mercator');
  S.param.mercator.planes = 1;
  S.approach = APPROACHES.findIndex(a => a.id === 'mercator');
  if (S.mode === 'k') { S.mode = 'j'; resetCam(); }
""", """// "Back to one plane": the entry Sphere inversions, one plane becomes the one on show, with its dials as they
// are. The point c, the camera and everything else stay. An approach means nothing to a Kleinian group, so from
// there the page goes to the Julia set.
function uiOnePlane() {
  const i = uiApIndex('mercator');
  if (i < 0) return;
  S.approach = i;
  if (S.mode === 'k') { S.mode = 'j'; resetCam(); }
""")

# --- the twin buttons and the two quaternion buttons share one function
rep("""function uiTwin(id) {
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
}""", """function uiTwin(id) { uiShowSolid(id, 1, UI_TWIN[id] || 1, UI_TWIN_ROOM); }
// The Mandelbrot solid of one approach at power 2, with that approach's dials at their starting values and
// "flip z" as given (1 for the mirror twin, 0 for the plain rule), `back` times as far away as the usual start
// and with room for a solid that reaches `room` from the centre.
function uiShowSolid(id, flipz, back, room) {
  const i = uiApIndex(id);
  if (i < 0) return;
  uiApQuiet(id);
  Object.assign(S.param[id], specDefaults(APPROACHES[i].params || []));
  S.flat = false; S.mode = 'm'; S.approach = i;
  S.mosaic = false; UI.mosaicWas = false; UI.mosaicCut = null;
  S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, flipz ? 1 : 0];
  S.cutOn = false; UI.presetCut = false;
  S.colour.solid = 0;
  $('eq').value = 'z^n + c'; $('z0').value = '0'; applyEquation();
  // the whole solid in the picture, as the text promises: a zoom limit or a drawing radius in the way is moved
  presetHome(back, room);
  uiFlatPaint(); syncControls();
  refresh(false);
  uiShowStage();
}
// ---------- the two buttons beside the quaternion answer in the closing text
// "Show the quaternion square" and "Show the twisted quaternion square": the plain Mandelbrot solid of that entry
// (Spin 1, or the Tilt at its starting value), set from any state the way a twin button does it, without the flip.
function uiQuat(id) { uiShowSolid(id, 0, UI_QUAT[id] || 1, UI_QUAT_ROOM); }""")

# --- the list
rep("""  // approaches, each with its own formula, note and controls
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
""", """  // Approaches, each with its own formula, note and controls. The list stands under the headings of
  // APPROACH_GROUPS: a heading comes before the first entry of its group, the entries of a group keep the order
  // they have in APPROACHES, and a group with no entry shows nothing. An entry whose group has no heading comes
  // last, under no heading. All the radios share one name, so the arrow keys walk the whole list as it is shown.
  const apGroups = typeof APPROACH_GROUPS === 'undefined' ? [] : APPROACH_GROUPS, apKnown = new Set(apGroups.map(g => g.id));
  const apRule = (r, i, host) => {
    const el = document.createElement('div');
    el.className = 'rule'; el.dataset.ap = r.id;
    el.innerHTML = `<label class="rule-head"><input type="radio" name="approach" id="ap-${r.id}" value="${i}"${i === S.approach ? ' checked' : ''}><span class="mark"></span><span class="name">${r.name}</span><span class="tag">${r.tag || ''}</span></label>` +
      `<div class="rule-body"><code id="f-${r.id}"></code><p class="note">${r.about || ''}</p><div id="pd-${r.id}" class="sec-body"></div></div>`;
    host.appendChild(el);
    const inp = el.querySelector('input');
    inp.addEventListener('change', () => { S.approach = i; refresh(false); });
    inp.addEventListener('focus', () => el.classList.toggle('is-focus', inp.matches(':focus-visible')));
    inp.addEventListener('blur', () => el.classList.remove('is-focus'));
    UI.ap[r.id] = buildControls('pd-' + r.id, r.params || [], S.param[r.id], uiApproachParam, { idPrefix: 'par-' + r.id + '-', group: 'approach' });
  };
  for (const g of [...apGroups, null]) {
    const list = APPROACHES.map((r, i) => [r, i]).filter(([r]) => (g ? r.group === g.id : !apKnown.has(r.group)));
    if (!list.length) continue;
    const box = document.createElement('div');
    box.className = 'rule-group';
    if (g) {
      box.id = 'apg-' + g.id; box.setAttribute('role', 'group'); box.setAttribute('aria-labelledby', 'apgh-' + g.id);
      const head = document.createElement('p');
      head.className = 'label rule-group-head'; head.id = 'apgh-' + g.id; head.textContent = g.title;
      box.appendChild(head);
    }
    $('rules').appendChild(box);
    list.forEach(([r, i]) => apRule(r, i, box));
  }
  // the closing text names the entries kept for the record, whichever of them this page has
  const tried = APPROACHES.filter(r => r.group === 'tried').map(r => r.name), triedHead = apGroups.find(g => g.id === 'tried');
  if (tried.length && triedHead && $('triedNote')) {
    $('triedNote').textContent = ` ${tried.length === 1 ? 'One of the rules that were tried is' : 'Some of the rules that were tried are'} in the Approach list, under “${triedHead.title}”: ${tried.length > 1 ? tried.slice(0, -1).join(', ') + ' and ' : ''}${tried[tried.length - 1]}.`;
  }
  addReset('approachReset', 'approach', { after: () => { S.approach = 0; refresh(false); } });
""")

# --- the buttons
rep("""  $('twinOff').addEventListener('click', uiTwinOff);
""", """  $('twinOff').addEventListener('click', uiTwinOff);
  for (const [btn, id] of [['quatShow', 'lathe'], ['tiltShow', 'tilt']]) $(btn).addEventListener('click', () => uiQuat(id));
""")

for old, new in EDITS:
    n = src.count(old)
    if n != 1:
        sys.exit('edit matches %d times, expected 1:\n%s' % (n, old[:200]))
    src = src.replace(old, new)
io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
print('%d edits applied to src/js/80-ui.js' % len(EDITS))
