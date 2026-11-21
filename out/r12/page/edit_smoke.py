# Round 12, page: the edits that turn out/r4/page/make_smoke.py into the smoke test of the new Approach list.
# Exact replacements, each of which must match once. Run once, from the project root.
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, 'out', 'r4', 'page', 'make_smoke.py')
src = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
EDITS = []
def rep(old, new):
    EDITS.append((old, new))

# ---------------------------------------------------------------- where the result goes
rep('''"""Write tools/smoke.json (the page's smoke test) from the steps below.

  python out/r4/page/make_smoke.py            -> tools/smoke.json, screenshots to out/smoke-*.png
  python out/r4/page/make_smoke.py --mine     -> out/r7/page/smoke-mine.json, screenshots to out/r7/page/smoke/

Each step throws on a wrong state, so a failure shows as "page script failed" with the reason.
Write tools/smoke.json only from a version that has passed as --mine: other people run that file too.
"""''', '''"""Write the page's smoke test for round 12 (every approach an entry of its own) from the steps below.

  python out/r4/page/make_smoke.py            -> tools/smoke-v12.json
  python out/r4/page/make_smoke.py --mine     -> out/r12/page/smoke-mine.json (a trial copy)
  Screenshots of both go to out/r12/page/smoke/.

Run it with:  python tools/shot.py --url dist/<page>.html --actions tools/smoke-v12.json
Each step throws on a wrong state, so a failure shows as "page script failed" with the reason.
Write tools/smoke-v12.json only from a version that has passed as --mine: other people run that file too.
This script no longer writes tools/smoke.json. That file and tools/smoke-v9.json, tools/smoke-v9m.json belong to
earlier rounds (the Planes dial under one Sphere inversions entry) and must stay as they are.

The steps work for any number of entries and groups in the Approach list: they read L.APPROACHES and
L.APPROACH_GROUPS, and name an entry only where a button or a text of the page names it.
"""''')
rep("SHOTS = 'out/r7/page/smoke/' if MINE else 'out/'", "SHOTS = 'out/r12/page/smoke/'")
rep("path = os.path.join(ROOT, 'out', 'r7', 'page', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke.json')",
    "path = os.path.join(ROOT, 'out', 'r12', 'page', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke-v12.json')")
rep('''const hits = s => s.split('1').length - 1;
''', '''const hits = s => s.split('1').length - 1;
const apId = () => L.APPROACHES[L.S.approach].id;   // the id of the approach in use
''')

# ---------------------------------------------------------------- the whole page: texts and controls
rep("""if ($('par-mercator-planes').max !== '8') fail('the planes dial should go to 8');
for (const id of ['par-mercator-liftPlay', 'par-mercator-turnPlay', 'par-bulb-latPlay',""",
    """if ($('par-fold-planes').min !== '2' || $('par-fold-planes').max !== '8') fail('the Planes dial of Sphere inversions, two planes should run from 2 to 8');
if ($('par-mercator-planes') || $('par-fold-turn')) fail('the one-plane entry should have no Planes dial, and the two-planes entry no Turn dial');
for (const id of ['par-mercator-liftPlay', 'par-mercator-turnPlay', 'par-fold-liftPlay', 'par-tilt-tiltPlay', 'par-bulb-latPlay',""")
rep("""  'The version you tested had Planes at 2', 'not a published theorem', 'as the Lathe approach', 'limited to c ∈ R',""",
    """  'The version you tested is the one the list now calls Sphere inversions, two planes', 'not a published theorem', 'in the list as Quaternion square (Lathe)', 'limited to c ∈ R',
  'kept as an entry of its own', 'Back to one plane chooses Sphere inversions, one plane, and changes nothing else', 'only under Sphere inversions, two planes',
  'Is there a quaternion rule that works everywhere in space?', 'checked against each other on 200,000 points', 'The rings break up into one body with tunnels', 'up close its skin is smooth',
  'Could the hidden rotation axis of the flat picture show the way?', 'a turn needs a plane to turn in', 'The twisted square is what makes that second turn count', 'the words on it say what it will change',""")
rep("""const has = t => names.has(t) || [...names].some(n => n.startsWith(t + ' ') || n.startsWith(t + ','));""",
    """const has = t => names.has(t) || [...names].some(n => n.startsWith(t + ' ') || n.startsWith(t + ',') || n.startsWith(t + ':'));""")
rep("""'Show Figure 4', 'Back to one plane', 'Lathe', 'Sphere inversions', 'Colour and light',""",
    """'Show Figure 4', 'Back to one plane', 'Sphere inversions', 'Colour and light',
  'Sphere inversions, one plane', 'Sphere inversions, two planes', 'Quaternion square (Lathe)', 'Quaternion square, twisted', 'Turn', 'Lift', 'Spin multiplier (odd)', 'Tilt of the axis, degrees',
  'Show the quaternion square', 'Show the twisted quaternion square',""")
rep("""if (!$('par-mercator-note1').textContent.includes('For the look of Figure 4') || !$('par-mercator-note2').textContent.includes('whole only while c is on the x-axis')) fail('the notes under the planes dial do not point to each other');
""", """if (!$('pd-mercator').textContent.includes('Sphere inversions, two planes') || !document.querySelector('.rule[data-ap=fold]').textContent.includes('earlier version')) fail('the two Sphere inversions entries do not say how they belong together');
// the closing text names the entries kept for the record exactly when the list has some
const tried = L.APPROACHES.filter(a => a.group === 'tried'), triedTitle = ((L.APPROACH_GROUPS || []).find(g => g.id === 'tried') || {}).title;
if (!$('triedNote')) fail('the closing text has no place for the entries kept for the record');
if (!tried.length && $('triedNote').textContent) fail('the closing text names entries kept for the record, and the list has none');
if (tried.length && (!foot.includes(triedTitle) || tried.some(a => !$('triedNote').textContent.includes(a.name)))) fail('the closing text should name the heading and every entry kept for the record: ' + $('triedNote').textContent);
""")
rep("""for (const t of ['cannot be built from inversions', 'rebuilt by eye',""",
    """for (const t of ['had Planes at 2', 'Planes at 1', 'set Planes to 2', 'the Lathe approach', 'Planes 1, Turn 0', 'cannot be built from inversions', 'rebuilt by eye',""")

# ---------------------------------------------------------------- the list itself, and every entry drawing
rep('''# 8 2D view
step(r"""''', '''# The Approach list: a heading from APPROACH_GROUPS before the first entry of each group, nothing for a group
# without entries, every entry with its ids, and one set of radios in the order the list is shown.
step(r"""
const groups = L.APPROACH_GROUPS, A = L.APPROACHES;
if (!Array.isArray(groups) || !groups.length) fail('window.squaringLab.APPROACH_GROUPS is missing');
const known = new Set(groups.map(g => g.id));
// what the list should read, top to bottom: ['head', title] and ['entry', id]
const want = [];
for (const g of groups) { const list = A.filter(a => a.group === g.id); if (list.length) { want.push('head ' + g.title); list.forEach(a => want.push('entry ' + a.id)); } }
A.filter(a => !known.has(a.group)).forEach(a => want.push('entry ' + a.id));
const got = [...document.querySelectorAll('#rules .rule-group-head, #rules .rule')].map(e => (e.classList.contains('rule') ? 'entry ' + e.dataset.ap : 'head ' + e.textContent));
if (got.join(' | ') !== want.join(' | ')) fail('the Approach list should read ' + want.join(' | ') + ' and reads ' + got.join(' | '));
const heads = [...document.querySelectorAll('#rules .rule-group-head')];
for (const h of heads) {
  const first = h.parentNode.querySelector('.rule');
  if (!first || h.nextElementSibling !== first) fail('the heading ' + h.textContent + ' does not stand right before the first entry of its group');
  if (h.parentNode.getAttribute('aria-labelledby') !== h.id) fail('the group under ' + h.textContent + ' is not named by its heading');
  if (h.getBoundingClientRect().width <= 0) fail('the heading ' + h.textContent + ' is not on show');
}
const radios = [...document.querySelectorAll('#rules input[type=radio]')];
if (radios.length !== A.length || radios.some(r => r.name !== 'approach')) fail('every entry needs one radio of the set "approach", so that the arrow keys walk the whole list');
if (radios.map(r => r.id).join() !== want.filter(w => w.startsWith('entry ')).map(w => 'ap-' + w.slice(6)).join()) fail('the radios are not in the order the list is shown');
if (radios.filter(r => r.checked).length !== 1 || document.querySelectorAll('#rules .rule.is-on').length !== 1) fail('exactly one entry should be marked as chosen');
for (const a of A) {
  for (const id of ['ap-' + a.id, 'f-' + a.id, 'pd-' + a.id]) if (!$(id)) fail('the list lacks #' + id);
  if (+$('ap-' + a.id).value !== A.indexOf(a)) fail('the radio of ' + a.name + ' does not carry its place in the list of approaches');
  for (const s of a.params || []) if (s.key !== undefined && !$('par-' + a.id + '-' + s.key)) fail('the list lacks #par-' + a.id + '-' + s.key);
  const rule = document.querySelector('.rule[data-ap="' + a.id + '"]');
  if (rule.querySelector('.name').textContent !== a.name || !rule.querySelector('.tag').textContent.trim()) fail('the entry ' + a.id + ' does not show its name and its one-line description');
}
if (document.documentElement.scrollWidth > innerWidth + 1) fail('the page is wider than the window: ' + document.documentElement.scrollWidth + ' of ' + innerWidth);
return heads.length + ' headings (' + heads.map(h => h.textContent).join(', ') + ') over ' + A.length + ' entries: ' + got.filter(w => w.startsWith('entry ')).map(w => w.slice(6)).join(', ');
""", '6b-approach-list', clip='#secApproach', wait=None)

# Every entry draws: its Mandelbrot solid, and its Julia set for c = -1. The loop runs in the page and the step
# waits for it, so it works for any number of entries (a script that awaited it would hit the tool's time limit).
step(r"""
const E = window.smokeEntries = { done: false, error: '', rows: [] };
(async () => {
  try {
    const settle = async name => { await sleep(150); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 120000) throw new Error('the picture of ' + name + ' was not finished after 120 s'); await sleep(40); } };
    for (const mode of ['m', 'j']) {
      $('mode-' + mode).click();
      if (mode === 'j') L.applyJuliaPreset({ c: [-1, 0, 0] });
      for (const a of L.APPROACHES) {
        const what = (mode === 'm' ? 'the Mandelbrot solid of ' : 'the Julia set for c = −1 of ') + a.name;
        $('ap-' + a.id).click(); await settle(what);
        const on = [...document.querySelectorAll('#rules .rule.is-on')];
        if (apId() !== a.id || !$('ap-' + a.id).checked || on.length !== 1 || on[0].dataset.ap !== a.id) throw new Error('choosing ' + a.name + ' did not take');
        if (on[0].querySelector('.rule-body').getBoundingClientRect().height <= 0) throw new Error('the chosen entry ' + a.name + ' does not show its formula and dials');
        if (!$('f-' + a.id).textContent.trim()) throw new Error('no formula text for ' + a.name);
        const g = grid();
        E.rows.push(a.id + ' ' + mode + ' ' + g[0]);
        if (g[0] < 1) throw new Error(what + ' is empty: none of 165 probes hit');
      }
    }
  } catch (e) { E.error = e.message || String(e); }
  E.done = true;
})();
return 'drawing every entry, Mandelbrot solid and Julia set for c = −1: ' + L.APPROACHES.map(a => a.id).join(', ');
""", '6c-every-entry', wait='window.smokeEntries && window.smokeEntries.done', timeout=900)
step(r"""
const E = window.smokeEntries;
if (E.error) fail(E.error + ' (drawn before that: ' + E.rows.join(', ') + ')');
if (E.rows.length !== 2 * L.APPROACHES.length) fail('not every entry was drawn: ' + E.rows.join(', '));
$('ap-mercator').click(); $('mode-k').click();
return 'every entry drew (entry, m or j, probes hit of 165): ' + E.rows.join(', ');
""")

# 8 2D view
step(r"""''')

# ---------------------------------------------------------------- approach dials, and the Approach reset
rep("""type('par-mercator-planesNum', '2');
if (!$('par-mercator-turn').closest('.dial').hidden) fail('the turn dial should be hidden with two planes');
type('par-mercator-planesNum', '1');
if ($('par-mercator-turn').closest('.dial').hidden) fail('the turn dial did not appear with one plane');
type('par-mercator-turnNum', '40'); type('par-mercator-liftNum', '0.3');
const p = L.S.param.mercator;
if (p.planes !== 1 || p.turn !== 40 || p.lift !== 0.3) fail('approach parameters not set: ' + JSON.stringify(p));""",
    """$('ap-fold').click(); await sleep(100);
type('par-fold-planesNum', '3');
if (L.S.param.fold.planes !== 3 || !$('f-fold').textContent.includes('3 planes')) fail('the Planes dial of the two-planes entry did not set the planes, or the formula text did not follow: ' + $('f-fold').textContent);
type('par-fold-planesNum', '1');
if (L.S.param.fold.planes < 2) fail('the Planes dial should not go below 2, it is at ' + L.S.param.fold.planes);
type('par-fold-planesNum', '2');
$('ap-mercator').click(); await sleep(100);
if ($('par-mercator-turn').closest('.dial').hidden) fail('the one-plane entry should show its Turn dial');
type('par-mercator-turnNum', '40'); type('par-mercator-liftNum', '0.3');
const p = L.S.param.mercator;
if (p.turn !== 40 || p.lift !== 0.3 || p.planes !== undefined) fail('approach parameters not set: ' + JSON.stringify(p));""")
rep("""const p = L.S.param.mercator, planes0 = L.APPROACHES.find(a => a.id === 'mercator').params.find(s => s.key === 'planes').def;
if (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');
if (p.planes !== planes0 || p.turn !== 0 || p.lift !== 0) fail('the Approach reset left ' + JSON.stringify(p));""",
    """if (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');
for (const a of L.APPROACHES) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined && L.S.param[a.id][s.key] !== s.def) fail('the Approach reset left ' + s.label + ' of ' + a.name + ' at ' + L.S.param[a.id][s.key]);""")

# ---------------------------------------------------------------- the Julia list
rep("""const view = camNow(), planes = L.S.param.mercator.planes;
pick('juliaPreset', 'Douady rabbit');""", """const view = camNow(), approach = JSON.stringify([L.S.approach, L.S.param]);
pick('juliaPreset', 'Douady rabbit');""")
rep("""if (L.S.param.mercator.planes !== planes) fail('a Julia entry changed the planes dial');""",
    """if (JSON.stringify([L.S.approach, L.S.param]) !== approach) fail('a Julia entry changed the approach or one of its dials');""")
rep("""an entry leaves camera, iterations and planes alone; Frame it""", """an entry leaves camera, iterations and the approach alone; Frame it""")

# ---------------------------------------------------------------- As it was found
old_found_start = '''# "As it was found": the planes and iterations an entry records, nothing else, and only while they differ
step(r"""'''
old_found_end = '''""", '15b-as-it-was-found')

# back to where the following steps expect the page: one plane, 17 iterations, the rabbit
step(r"""
type('par-mercator-planesNum', '1'); type('iterNum', '17'); pick('juliaPreset', 'Douady rabbit');
return 'one plane and 17 iterations again';
""")'''
i0, i1 = src.find(old_found_start), src.find(old_found_end)
if i0 < 0 or i1 < i0 or src.count(old_found_start) != 1 or src.count(old_found_end) != 1:
    sys.exit('the As it was found steps were not found')
new_found = '''# "As it was found": the Sphere inversions entry (one plane, or two planes with their count) and the iterations
# an entry records, nothing else, and only while they differ. The words on the button say what it will do.
step(r"""
if (apId() !== 'mercator' || L.S.iter !== 17) fail('unexpected state before the test: ' + [apId(), L.S.iter]);
const f = $('juliaFound');
if (!shown('juliaFound')) fail('the rabbit records 24 iterations and the page has 17: As it was found should be on show');
if (f.textContent !== 'As it was found: 24 iterations' || !f.title.includes('Iterations to 24')) fail('the words on the button should say what it will do: ' + f.textContent + ' / ' + f.title);
const view = camNow(), c = L.S.c.join(), dials = JSON.stringify(L.S.param);
f.focus(); f.click(); await sleep(150);
if (L.S.iter !== 24 || $('iterNum').value !== '24' || apId() !== 'mercator') fail('As it was found should set 24 iterations and leave the approach: ' + [L.S.iter, apId()]);
if (camNow() !== view || L.S.c.join() !== c) fail('As it was found changed the camera or c');
if (shown('juliaFound')) fail('As it was found should go when nothing differs any more');
if (document.activeElement === document.body) fail('focus was lost when the button went');
// an entry found with two planes, while the one-plane entry is in use: the button goes to the two-planes entry
pick('juliaPreset', 'Cracked Basilica'); await sleep(150);
if ($('juliaPreset').selectedOptions[0].parentNode.label !== 'Found with two planes') fail('Cracked Basilica is not under Found with two planes');
const note = $('juliaNote').textContent;
if (!note.includes('Sphere inversions, two planes') || /set Planes|Planes to/.test(note)) fail('the note of an entry found with two planes should name the entry of the Approach list, not a dial: ' + note);
if (!shown('juliaFound') || f.textContent !== 'As it was found: two planes' || !f.title.includes('Sphere inversions, two planes')) fail('an entry found with two planes should offer the two-planes entry while the one-plane entry is in use: ' + f.textContent + ' / ' + f.title);
const c2 = L.S.c.join();
f.click(); await sleep(150);
if (apId() !== 'fold' || !$('ap-fold').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'fold') fail('As it was found should choose Sphere inversions, two planes: ' + apId());
if (L.S.param.fold.planes !== 2 || L.S.iter !== 24 || JSON.stringify(L.S.param) !== dials) fail('As it was found should leave the planes at 2 and move no other dial: ' + JSON.stringify(L.S.param));
if (camNow() !== view || L.S.c.join() !== c2 || L.S.mode !== 'j') fail('As it was found changed the camera, c or the kind of picture');
if (shown('juliaFound')) fail('the button should go once the entry is in use with the planes as recorded');
// the two-planes entry in use with another count: the button sets the count
type('par-fold-planesNum', '3'); await sleep(150);
if (!shown('juliaFound') || f.textContent !== 'As it was found: two planes' || !f.title.includes('Planes to 2')) fail('with Planes at 3 the button should offer to set them to 2: ' + f.textContent + ' / ' + f.title);
f.click(); await sleep(150);
if (L.S.param.fold.planes !== 2 || $('par-fold-planesNum').value !== '2' || apId() !== 'fold') fail('As it was found should set Planes to 2 and nothing else');
// an entry found with one plane, while the two-planes entry is in use: the button goes to the one-plane entry
pick('juliaPreset', 'Dendrite'); await sleep(150);
if (!shown('juliaFound') || f.textContent !== 'As it was found: one plane' || !f.title.includes('Sphere inversions, one plane')) fail('an entry found with one plane should offer the one-plane entry while the two-planes entry is in use: ' + f.textContent + ' / ' + f.title);
f.click(); await sleep(150);
if (apId() !== 'mercator' || !$('ap-mercator').checked || JSON.stringify(L.S.param) !== dials) fail('As it was found should choose Sphere inversions, one plane and move no dial: ' + apId());
if (shown('juliaFound')) fail('the button should go once the one-plane entry is in use');
// under any other approach the two entries do not count
$('ap-lathe').click(); pick('juliaPreset', 'Cracked Basilica'); await sleep(150);
if (shown('juliaFound')) fail('under another approach the button should stay away: ' + f.textContent);
$('ap-mercator').click(); await sleep(150);
if (!shown('juliaFound')) fail('back under Sphere inversions, one plane the button should return');
f.click(); await sleep(150);
if (apId() !== 'fold') fail('the button did not choose the two-planes entry the second time');
return 'As it was found: 24 iterations for the rabbit; Cracked Basilica goes to Sphere inversions, two planes, and sets Planes back from 3 to 2; Dendrite goes back to one plane; camera, c and the other dials untouched; hidden when nothing differs and under another approach';
""", '15b-as-it-was-found')

# back to where the following steps expect the page: one plane, 17 iterations, the rabbit
step(r"""
$('ap-mercator').click(); type('iterNum', '17'); pick('juliaPreset', 'Douady rabbit');
if (apId() !== 'mercator' || L.S.param.fold.planes !== 2) fail('could not put the page back to the one-plane entry');
return 'the one-plane entry and 17 iterations again';
""")'''
src = src[:i0] + new_found + src[i1 + len(old_found_end):]

# ---------------------------------------------------------------- Show Figure 4 and Back to one plane
rep("""$('ap-mercator').click(); type('par-mercator-liftNum', '0.4'); $('par-mercator-liftPlay').click();
$('mode-k').click();""", """$('ap-mercator').click(); type('par-mercator-turnNum', '30');
$('ap-fold').click(); type('par-fold-planesNum', '5'); type('par-fold-liftNum', '0.4'); $('par-fold-liftPlay').click();
$('ap-classic').click(); $('mode-k').click();""")
rep("""const S = L.S, p = S.param.mercator, bad = [];
if (S.mode !== 'j' || !$('mode-j').checked) bad.push('the mode');""", """const S = L.S, p = S.param.fold, bad = [];
if (S.mode !== 'j' || !$('mode-j').checked) bad.push('the mode');""")
rep("""if (L.APPROACHES[S.approach].id !== 'mercator' || !$('ap-mercator').checked) bad.push('the approach');
if (p.planes !== 2 || $('par-mercator-planesNum').value !== '2') bad.push('the planes at ' + $('par-mercator-planesNum').value);
if (p.turn !== 0 || p.lift !== 0 || $('par-mercator-liftNum').value !== '0') bad.push('turn or lift at ' + [p.turn, p.lift]);
if (!$('par-mercator-turn').closest('.dial').hidden || $('par-mercator-note2').hidden) bad.push('the planes panel (Turn should be away, the note on the earlier version on show)');""",
    """if (apId() !== 'fold' || !$('ap-fold').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'fold') bad.push('the approach, which is ' + apId() + ' and should be Sphere inversions, two planes');
if (p.planes !== 2 || $('par-fold-planesNum').value !== '2') bad.push('the planes at ' + $('par-fold-planesNum').value);
if (p.lift !== 0 || $('par-fold-liftNum').value !== '0') bad.push('the lift at ' + p.lift);
if (S.param.mercator.turn !== 30) bad.push('the Turn dial of the one-plane entry, which is not this button\\'s to move');""")
rep("""if (L.S.param.mercator.lift !== 0) bad.push('the Lift sweep, still running');""", """if (L.S.param.fold.lift !== 0) bad.push('the Lift sweep, still running');""")
rep("""return 'Show Figure 4 from the Kleinian 2D view: Julia, c = (-1, 0, 0), power 2, Sphere inversions with 2 planes, turn 0, lift 0, framed';""",
    """return 'Show Figure 4 from the Kleinian 2D view with the classic Mandelbulb chosen and Planes at 5: Julia, c = (-1, 0, 0), power 2, the entry Sphere inversions, two planes with Planes 2 and Lift 0, framed';""")
rep("""const view = camNow();
$('fig4Back').click(); await sleep(300);
const p = L.S.param.mercator;
if (p.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('Back to one plane left the planes at ' + p.planes);
if ($('par-mercator-turn').closest('.dial').hidden || $('par-mercator-note1').hidden) fail('with one plane the Turn dial and the one-plane note should be on show');
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the planes');
return 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane set the planes dial to 1 and nothing else';""",
    """const view = camNow(), dials = JSON.stringify(L.S.param);
$('fig4Back').click(); await sleep(300);
if (apId() !== 'mercator' || !$('ap-mercator').checked || document.querySelector('#rules .rule.is-on').dataset.ap !== 'mercator') fail('Back to one plane should choose Sphere inversions, one plane, the approach is ' + apId());
if (JSON.stringify(L.S.param) !== dials) fail('Back to one plane moved a dial: ' + JSON.stringify(L.S.param));
if ($('par-mercator-turn').closest('.dial').hidden) fail('the one-plane entry should show its Turn dial');
if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the approach');
return 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane chose Sphere inversions, one plane and nothing else';""")
rep("""type('par-mercator-planesNum', '3'); $('ap-lathe').click(); $('mode-k').click(); await sleep(150);
$('fig4Back').click(); await sleep(300);
if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');
if (L.APPROACHES[L.S.approach].id !== 'mercator' || !$('ap-mercator').checked || L.S.param.mercator.planes !== 1 || $('par-mercator-planesNum').value !== '1') fail('Back to one plane should show Sphere inversions with Planes at 1');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.param.mercator.planes !== 1 || L.S.colour.solid !== 0) fail('Reset everything did not bring the opening state back');""",
    """type('par-fold-planesNum', '3'); $('ap-tilt').click(); $('mode-k').click(); await sleep(150);
$('fig4Back').click(); await sleep(300);
if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');
if (apId() !== 'mercator' || !$('ap-mercator').checked || L.S.param.fold.planes !== 3) fail('Back to one plane should show Sphere inversions, one plane and leave the Planes dial of the other entry alone');
// ... and Show Figure 4 a second time, from the Mandelbrot solid of the twisted quaternion square
$('ap-tilt').click(); $('mode-m').click(); await sleep(150);
$('fig4Show').click(); await sleep(300);
if (apId() !== 'fold' || L.S.mode !== 'j' || L.S.param.fold.planes !== 2 || L.S.c.join() !== '-1,0,0' || !$('ap-fold').checked) fail('Show Figure 4 from the twisted quaternion square did not land on Sphere inversions, two planes with Planes at 2');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.param.fold.planes !== 2 || L.S.param.mercator.turn !== 0 || L.S.colour.solid !== 0) fail('Reset everything did not bring the opening state back');""")
rep("""return 'Back to one plane also works from the Kleinian view and another approach';""",
    """return 'Back to one plane also works from the Kleinian view and another approach; Show Figure 4 also from the twisted quaternion square';""")

# ---------------------------------------------------------------- the twin buttons
rep("""  const p = S.param.mercator;
  if (id === 'mercator' && (p.planes !== 1 || p.turn !== 0 || p.lift !== 0 || $('par-mercator-planesNum').value !== '1')) bad.push('the dials of Sphere inversions');""",
    """  const p = S.param.mercator;
  if (id === 'mercator' && (p.turn !== 0 || p.lift !== 0 || $('par-mercator-turnNum').value !== '0' || $('par-mercator-liftNum').value !== '0')) bad.push('the dials of Sphere inversions, one plane');""")
rep("""type('par-mercator-planesNum', '3'); type('par-mercator-liftNum', '0.4');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');""",
    """type('par-mercator-turnNum', '25'); type('par-mercator-liftNum', '0.4');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');""")
rep("""return 'Twin of Sphere inversions from the Kleinian 2D view: Mandelbrot, power 2, one plane, flip z ticked';""",
    """return 'Twin of Sphere inversions from the Kleinian 2D view: Mandelbrot, power 2, the one-plane entry with Turn 0 and Lift 0, flip z ticked';""")

# ---------------------------------------------------------------- the two quaternion buttons (new)
rep('''# The trap solid examples (the list "Examples" under "In the 3D view the trap").''',
    '''# The two buttons beside the quaternion answer: each shows the plain Mandelbrot solid of one entry (the quaternion
# square with Spin 1, the twisted one with its Tilt at the starting value) and frames the whole solid, from any state.
QUAT_CHECK = r"""
const quatState = (btn, id) => {
  const S = L.S, bad = [], a = L.APPROACHES.find(x => x.id === id);
  if (!a) fail('the list has no entry ' + id);
  if (S.mode !== 'm' || !$('mode-m').checked) bad.push('the mode');
  if (S.flat || $('flat').checked) bad.push('the 2D view');
  if (apId() !== id || !$('ap-' + id).checked || document.querySelector('#rules .rule.is-on').dataset.ap !== id) bad.push('the approach, which is ' + apId());
  if (S.flip.join() !== '0,0' || $('flipz').checked || $('flipy').checked) bad.push('flip y or flip z');
  if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
  if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absy').checked || S.colour.solid !== 0 || S.mosaic) bad.push('the equation, the cut, a modifier, the mosaic or the trap solid');
  for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined && (S.param[id][s.key] !== s.def || $('par-' + id + '-' + s.key + 'Num').value !== String(s.def))) bad.push('the dial ' + s.label + ', at ' + S.param[id][s.key]);
  if ($('mandelPanel').hidden || !$('juliaPanel').hidden || !$('kleinPanel').hidden) bad.push('the panels');
  if (S.view.zmax < L.cam.dist || S.view.bound < 3) bad.push('the room for the whole solid: camera at ' + L.cam.dist.toFixed(2) + ', far limit ' + S.view.zmax + ', drawing radius ' + S.view.bound);
  if (bad.length) fail(btn + ' did not set: ' + bad.join('; '));
  const r = $('stage').getBoundingClientRect();
  if (r.bottom <= 0 || r.top >= innerHeight) fail('after ' + btn + ' the picture is out of view');
};
const quatPicture = name => { const g = grid(); if (g[0] < 8) fail('the picture of ' + name + ' is (nearly) empty: ' + g[0] + ' of 165 probes hit'); if (g[1] > 4) fail(name + ' is not whole in the frame: ' + g[1] + ' probes hit on the outer ring'); return g[0] + ' of 165 probes hit, ' + g[1] + ' on the outer ring'; };
"""
step(QUAT_CHECK + r"""
if (typeof L.showQuaternionSquare !== 'function' || typeof L.showTwistedSquare !== 'function') fail('window.squaringLab lacks showQuaternionSquare or showTwistedSquare');
if ($('quatShow').textContent !== 'Show the quaternion square' || $('tiltShow').textContent !== 'Show the twisted quaternion square') fail('the two buttons do not carry their names');
const answer = $('quatShow').closest('.row-btns').previousElementSibling;
let h = answer; while (h && h.tagName !== 'H3') h = h.previousElementSibling;
if (!h || h.textContent !== 'Is there a quaternion rule that works everywhere in space?' || $('tiltShow').parentNode !== $('quatShow').parentNode) fail('the two buttons should stand together beside the answer on the quaternion rule');
type('par-tilt-tiltNum', '-120'); type('par-lathe-spinNum', '3');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); $('flipz').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
L.S.view.zmax = 3; L.S.view.bound = 1.5; L.syncControls(); L.viewChanged();   // a far zoom limit and a drawing radius that would not let the solid fit
await sleep(200);
$('tiltShow').click(); await sleep(400);
quatState('Show the twisted quaternion square', 'tilt');
if (L.S.param.lathe.spin !== 3) fail('Show the twisted quaternion square moved a dial of another entry');
return 'Show the twisted quaternion square from the Kleinian 2D view with Tilt at −120: Mandelbrot, power 2, Tilt 40, no flip, room made for the solid';
""", '21k-twisted-square')
step(QUAT_CHECK + r"""
const was = quatPicture('the twisted quaternion square');
$('m-mosaic').click(); await sleep(150);
$('mode-j').click(); $('ap-bulb').click(); $('flipz').click(); await sleep(150);
$('quatShow').click(); await sleep(400);
quatState('Show the quaternion square', 'lathe');
if (L.S.param.tilt.tilt !== 40) fail('Show the quaternion square moved a dial of another entry');
return 'twisted quaternion square drawn (' + was + '); Show the quaternion square from the Julia set of the Mandelbulb with Spin at 3 and flip z ticked: Mandelbrot, power 2, Spin 1, no flip';
""", '21l-quaternion-square')
step(QUAT_CHECK + r"""
const was = quatPicture('the quaternion square');
// the same two by their names on window.squaringLab, from Figure 4
$('fig4Show').click(); await sleep(300);
L.showTwistedSquare(); await sleep(300);
quatState('showTwistedSquare()', 'tilt');
$('fig4Show').click(); await sleep(300);
L.showQuaternionSquare(); await sleep(300);
quatState('showQuaternionSquare()', 'lathe');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.param.tilt.tilt !== 40 || L.S.param.lathe.spin !== 1 || L.S.flip.join() !== '0,0') fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'quaternion square drawn (' + was + '); showTwistedSquare() and showQuaternionSquare() do the same from Figure 4';
""")

# The trap solid examples (the list "Examples" under "In the 3D view the trap").''')

for old, new in EDITS:
    n = src.count(old)
    if n != 1:
        sys.exit('edit matches %d times, expected 1:\n%s' % (n, old[:300]))
    src = src.replace(old, new)
io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
print('%d edits applied to out/r4/page/make_smoke.py' % (len(EDITS) + 1))
