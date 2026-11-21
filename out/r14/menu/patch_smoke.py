"""One-off: turn out/r4/page/make_smoke.py (round 12) into the round 14 version (the Approach menu).
Run once from the project root: python out/r14/menu/patch_smoke.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'out', 'r4', 'page', 'make_smoke.py')
s = io.open(P, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


def between(start, end, new):
    """Replace everything from `start` up to (not including) `end`."""
    global s
    a = s.index(start)
    b = s.index(end, a)
    s = s[:a] + new + s[b:]


# ----- header and paths
between('"""Write the page\'s smoke test for round 12', 'import io, json, os, sys', '''"""Write the page's smoke test for round 14 (the approach is a menu, in one section with the equation).

  python out/r4/page/make_smoke.py            -> tools/smoke-v14.json
  python out/r4/page/make_smoke.py --mine     -> out/r14/menu/smoke-mine.json (a trial copy)
  Screenshots of both go to out/r14/menu/smoke/.

Run it with:  python tools/shot.py --url dist/<page>.html --actions tools/smoke-v14.json
Each step throws on a wrong state, so a failure shows as "page script failed" with the reason.
Write tools/smoke-v14.json only from a version that has passed as --mine: other people run that file too.
This script no longer writes tools/smoke-v12.json, which belongs to the pages before the menu (the Approach
section as a list of radio entries, each with its text and dials under it) and must stay as it is. The same
goes for tools/smoke.json, tools/smoke-v9.json and tools/smoke-v9m.json of earlier rounds.

The steps work for any number of entries and groups in the Approach menu: they read L.APPROACHES and
L.APPROACH_GROUPS, and name an entry only where a button or a text of the page names it.
"""
''')
rep("SHOTS = 'out/r12/page/smoke/'", "SHOTS = 'out/r14/menu/smoke/'")
rep("path = os.path.join(ROOT, 'out', 'r12', 'page', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke-v12.json')",
    "path = os.path.join(ROOT, 'out', 'r14', 'menu', 'smoke-mine.json') if MINE else os.path.join(ROOT, 'tools', 'smoke-v14.json')")

# ----- helpers every step can use: the explanation of an entry as the open menu shows it
rep('''const apId = () => L.APPROACHES[L.S.approach].id;   // the id of the approach in use
''', '''const apId = () => L.APPROACHES[L.S.approach].id;   // the id of the approach in use
const plain = html => { const d = document.createElement('div'); d.innerHTML = html || ''; return d.textContent; };   // an entry's name, tag and about are HTML
// put a mouse over an entry of the Approach menu's list (the list need not be open for the text to be made)
const apHover = id => document.querySelector('#rules .rule[data-ap="' + id + '"] .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' }));
// the explanation the menu shows for an entry: hover it, read the text, leave again
const apSays = id => { apHover(id); const t = $('apInfo').textContent; $('apPop').dispatchEvent(new PointerEvent('pointerleave', { pointerType: 'mouse' })); return t; };
const key = (el, k) => el.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
''')

# ----- step 7: the two Sphere inversions entries say how they belong together, in their explanations
rep("""if (!$('pd-mercator').textContent.includes('Sphere inversions, two planes') || !document.querySelector('.rule[data-ap=fold]').textContent.includes('earlier version')) fail('the two Sphere inversions entries do not say how they belong together');""",
    """if (!apSays('mercator').includes('Sphere inversions, two planes') || !apSays('fold').includes('earlier version')) fail('the two Sphere inversions entries do not say how they belong together');""")

# ----- the Approach menu: structure, hover text, keyboard, script, About, Learn
between('# The Approach list: a heading from APPROACH_GROUPS before the first entry of each group, nothing for a group',
        '# Every entry draws: its Mandelbrot solid, and its Julia set for c = -1.', r'''# The Approach menu. One section holds the approach and the equation. The menu is a button that names the chosen
# approach and opens the list: a heading from APPROACH_GROUPS before the first entry of each group, nothing for a
# group without entries, every entry with its ids, and one set of radios in the order the list is shown. Under
# the menu only the chosen approach's formula and dials are on show. An entry under the mouse shows its name, its
# one-line description, its formula and its explanation.
step(r"""
$('mode-m').click(); await sleep(100);   // the section is put away in the Kleinian view
const groups = L.APPROACH_GROUPS, A = L.APPROACHES;
if (!Array.isArray(groups) || !groups.length) fail('window.squaringLab.APPROACH_GROUPS is missing');
if ($('secApproach').querySelector('summary').textContent.trim() !== 'Approach and equation' || !$('secApproach').contains($('secEq')) || document.querySelector('#sections > #secEq')) fail('the approach and the equation should share the one section Approach and equation');
for (const id of ['eqPreset', 'eq', 'z0', 'pow', 'iter']) if (!$('secApproach').contains($(id)) || !shown(id)) fail('the equation control #' + id + ' should be on show in the section Approach and equation');
if (!$('apPop').hidden || $('apMenuBtn').getAttribute('aria-expanded') !== 'false' || shown('rules')) fail('the list of the Approach menu should be closed until its button is pressed');
if ($('apMenuName').textContent !== plain(A[L.S.approach].name)) fail('the button of the Approach menu should name the chosen approach, it reads ' + $('apMenuName').textContent);
$('apMenuBtn').click(); await sleep(200);
if ($('apPop').hidden || $('apMenuBtn').getAttribute('aria-expanded') !== 'true' || !shown('rules')) fail('pressing the button of the Approach menu did not open the list');
const pop = $('apPop').getBoundingClientRect(), btn = $('apMenuBtn').getBoundingClientRect();
if (pop.left < -0.5 || pop.right > innerWidth + 0.5 || pop.top < -0.5 || pop.bottom > innerHeight + 0.5) fail('the open list does not fit the window: ' + [pop.left, pop.top, pop.right, pop.bottom].map(Math.round) + ' of ' + innerWidth + ' x ' + innerHeight);
if (btn.top < -0.5 || btn.bottom > pop.top + 0.5) fail('the button of the menu should stay in view above its open list');
const known = new Set(groups.map(g => g.id));
// what the list should read, top to bottom: ['head', title] and ['entry', id]
const want = [];
for (const g of groups) { const list = A.filter(a => a.group === g.id); if (list.length) { want.push('head ' + g.title); list.forEach(a => want.push('entry ' + a.id)); } }
A.filter(a => !known.has(a.group)).forEach(a => want.push('entry ' + a.id));
const got = [...document.querySelectorAll('#rules .rule-group-head, #rules .rule')].map(e => (e.classList.contains('rule') ? 'entry ' + e.dataset.ap : 'head ' + e.textContent));
if (got.join(' | ') !== want.join(' | ')) fail('the list of the Approach menu should read ' + want.join(' | ') + ' and reads ' + got.join(' | '));
const heads = [...document.querySelectorAll('#rules .rule-group-head')];
for (const h of heads) {
  const first = h.parentNode.querySelector('.rule');
  if (!first || h.nextElementSibling !== first) fail('the heading ' + h.textContent + ' does not stand right before the first entry of its group');
  if (h.parentNode.getAttribute('aria-labelledby') !== h.id) fail('the group under ' + h.textContent + ' is not named by its heading');
  if (h.getBoundingClientRect().width <= 0) fail('the heading ' + h.textContent + ' is not on show');
}
const radios = [...document.querySelectorAll('#rules input[type=radio]')];
if (radios.length !== A.length || radios.some(r => r.name !== 'approach')) fail('every entry needs one radio of the set "approach"');
if (radios.map(r => r.id).join() !== want.filter(w => w.startsWith('entry ')).map(w => 'ap-' + w.slice(6)).join()) fail('the radios are not in the order the list is shown');
if (radios.filter(r => r.checked).length !== 1 || document.querySelectorAll('#rules .rule.is-on').length !== 1) fail('exactly one entry should be marked as chosen');
if (!$('apInfo').hidden) fail('no explanation should show before the mouse is over an entry');
const box = [];
for (const a of A) {
  for (const id of ['ap-' + a.id, 'f-' + a.id, 'pd-' + a.id]) if (!$(id)) fail('the menu lacks #' + id);
  if (+$('ap-' + a.id).value !== A.indexOf(a)) fail('the radio of ' + a.name + ' does not carry its place in the list of approaches');
  for (const s of a.params || []) if (s.key !== undefined && !$('par-' + a.id + '-' + s.key)) fail('the menu lacks #par-' + a.id + '-' + s.key);
  const rule = document.querySelector('.rule[data-ap="' + a.id + '"]');
  if (rule.querySelector('.name').textContent !== plain(a.name) || !rule.querySelector('.tag').textContent.trim()) fail('the entry ' + a.id + ' does not carry its name and its one-line description');
  // under the menu: the chosen approach's formula and dials, and nobody else's
  const on = a === A[L.S.approach];
  if (shown('f-' + a.id) !== on) fail('under the menu the formula of ' + a.name + ' should be ' + (on ? 'on show' : 'put away'));
  for (const s of a.params || []) if (s.key !== undefined && shown('par-' + a.id + '-' + s.key) && !on) fail('under the menu a dial of ' + a.name + ' is on show, and that approach is not the chosen one');
  // the explanation while the mouse is over the entry
  apHover(a.id);
  const t = $('apInfo').textContent, r = $('apInfo').getBoundingClientRect();
  if ($('apInfo').hidden || r.width <= 0 || r.height <= 0) fail('no explanation shows while the mouse is over ' + a.name);
  if (r.left < -0.5 || r.right > innerWidth + 0.5 || r.top < -0.5 || r.bottom > innerHeight + 0.5) fail('the explanation of ' + a.name + ' does not fit the window: ' + [r.left, r.top, r.right, r.bottom].map(Math.round));
  for (const [what, text] of [['name', plain(a.name)], ['one-line description', plain(a.tag)], ['formula', a.formula(L.S.param[a.id], L.S.n)], ['explanation', plain(a.about)]]) if (!text.trim() || !t.includes(text)) fail('the explanation of ' + a.name + ' lacks its ' + what);
  for (const s of a.params || []) if (s.type === 'note' && !s.when && !t.includes(s.text)) fail('the explanation of ' + a.name + ' lacks the note that stands among its dials');
  if (!rule.classList.contains('is-info')) fail('the entry under the mouse is not marked');
  box.push(Math.round(r.height));
}
// a finger does not hover
$('apPop').dispatchEvent(new PointerEvent('pointerleave', { pointerType: 'mouse' }));
if (!$('apInfo').hidden) fail('the explanation should go when the mouse leaves the list');
document.querySelector('#rules .rule .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'touch' }));
if (!$('apInfo').hidden) fail('a finger on an entry should not bring up the hover text');
if (document.documentElement.scrollWidth > innerWidth + 1) fail('the page is wider than the window: ' + document.documentElement.scrollWidth + ' of ' + innerWidth);
apHover(A[Math.min(3, A.length - 1)].id);
return heads.length + ' headings (' + heads.map(h => h.textContent).join(', ') + ') over ' + A.length + ' entries: ' + got.filter(w => w.startsWith('entry ')).map(w => w.slice(6)).join(', ') + '; open list ' + Math.round(pop.width) + ' x ' + Math.round(pop.height) + ' in a window of ' + innerWidth + ' x ' + innerHeight + '; explanation heights ' + box.join(', ');
""", '6b-approach-menu', clip=None, wait=None)

# The menu by keyboard, by mouse and from a script; "About this approach"; the two step buttons.
step(r"""
const A = L.APPROACHES, order = [...document.querySelectorAll('#rules input[type=radio]')].map(r => +r.value), btn = $('apMenuBtn');
const next = i => order[(order.indexOf(i) + 1) % order.length], prev = i => order[(order.indexOf(i) + order.length - 1) % order.length];
if ($('apPop').hidden) fail('the list should still be open from the step before');
key(btn, 'Escape');
if (!$('apPop').hidden || !$('apInfo').hidden) fail('Escape did not close the list and its explanation');
// closed, with the button in focus: the arrow keys go to the next and the previous entry, in the order of the list
const at0 = L.S.approach;
btn.focus(); key(btn, 'ArrowDown');
if (L.S.approach !== next(at0) || !$('apPop').hidden) fail('arrow down on the closed menu should choose the next entry and leave the list closed');
if ($('apMenuName').textContent !== plain(A[L.S.approach].name) || !shown('f-' + apId()) || shown('f-' + A[at0].id)) fail('after arrow down the menu should name the new approach and show its formula only');
key(btn, 'ArrowUp');
if (L.S.approach !== at0) fail('arrow up on the closed menu should choose the previous entry');
$('apNext').click(); if (L.S.approach !== next(at0)) fail('Next approach did not go to the next entry');
$('apPrev').click(); $('apPrev').click(); if (L.S.approach !== prev(at0)) fail('Previous approach did not go to the previous entry');
$('apNext').click();
// open: the focus stands on the chosen entry; the arrows move it without choosing; Enter chooses and closes
btn.click(); await sleep(100);
if (document.activeElement !== $('ap-' + A[at0].id)) fail('on opening, the focus should stand on the chosen entry');
key(document.activeElement, 'ArrowDown');
const to = A[next(at0)];
if (document.activeElement !== $('ap-' + to.id)) fail('arrow down in the open list should move the focus to the next entry');
if (L.S.approach !== at0 || $('ap-' + to.id).checked) fail('moving the focus in the open list must not choose');
const focusText = !$('apInfo').hidden && $('apInfo').textContent.includes(plain(to.about));
key(document.activeElement, 'End'); if (document.activeElement.value !== String(order[order.length - 1])) fail('End should move the focus to the last entry');
key(document.activeElement, 'Home'); if (document.activeElement.value !== String(order[0])) fail('Home should move the focus to the first entry');
$('ap-' + to.id).focus(); key(document.activeElement, 'Enter'); await sleep(100);
if (apId() !== to.id || !$('apPop').hidden || document.activeElement !== btn || $('apMenuName').textContent !== plain(to.name)) fail('Enter on an entry should choose it, close the list and put the focus back on the button');
// by mouse: a click on an entry chooses it and closes the list; a press anywhere else closes it too
btn.click(); await sleep(100);
document.querySelector('#rules .rule[data-ap="' + A[at0].id + '"] .name').click(); await sleep(100);
if (L.S.approach !== at0 || !$('apPop').hidden) fail('a click on an entry should choose it and close the list');
btn.click(); await sleep(100);
$('stage').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
if (!$('apPop').hidden) fail('a press outside the menu should close the list');
// from a script, with the list closed
const other = A[next(next(at0))];
$('ap-' + other.id).click();
if (apId() !== other.id || !$('ap-' + other.id).checked || !$('apPop').hidden || $('apMenuName').textContent !== plain(other.name)) fail('a script click on #ap-' + other.id + ' should choose that approach');
// "About this approach": the same text for the chosen approach, for a finger
const ab = $('apAboutBtn'), about = $('apAbout');
if (!shown('apAboutBtn') || !about.hidden || ab.getAttribute('aria-expanded') !== 'false') fail('About this approach should be on show, and closed until it is pressed');
ab.click();
if (about.hidden || !shown('apAbout') || ab.getAttribute('aria-expanded') !== 'true') fail('About this approach did not open the explanation');
for (const [what, text] of [['one-line description', plain(other.tag)], ['explanation', plain(other.about)]]) if (!about.textContent.includes(text)) fail('About this approach lacks the ' + what + ' of ' + other.name);
$('ap-' + A[at0].id).click();
if (!about.textContent.includes(plain(A[at0].about)) || about.textContent.includes(plain(other.about))) fail('the open explanation did not follow the approach');
for (const s of A[at0].params || []) if (s.type === 'note' && !s.when && !about.textContent.includes(s.text)) fail('About this approach lacks the note that stands among the dials of ' + A[at0].name);
const r = about.getBoundingClientRect();
if (r.left < -0.5 || r.right > innerWidth + 0.5) fail('the explanation under the menu is wider than the window');
ab.click();
if (!about.hidden || ab.getAttribute('aria-expanded') !== 'false') fail('pressing again should close the explanation');
return 'menu by keyboard (arrows on the closed button, arrows, Home, End, Enter and Escape in the list), by mouse and from a script; About this approach opens and follows; explanation on keyboard focus: ' + (focusText ? 'shown' : 'not shown in this run');
""", '6b2-menu-closed', clip='#secApproach', wait=None)

# The Learn tab keeps the approach menu with the chosen approach's dials, and the power; the rest of the equation
# part is put away. It does so coming from the Kleinian view too, where the section is hidden.
step(r"""
const A = L.APPROACHES, was = L.S.approach;
for (const from of ['m', 'k']) {
  $('mode-' + from).click(); await sleep(150);
  $('mode-l').click(); await sleep(300);
  if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on');
  for (const id of ['apMenuBtn', 'f-' + apId(), 'pow', 'apAboutBtn']) if (!shown(id)) fail('under Learn (from ' + from + ') #' + id + ' should stay on show');
  for (const id of ['eqPreset', 'eq', 'z0', 'iter', 'eqHead']) if (shown(id)) fail('under Learn #' + id + ' means nothing and should be put away');
}
const other = A[(was + 2) % A.length];
$('apMenuBtn').click(); await sleep(100);
document.querySelector('#rules .rule[data-ap="' + other.id + '"] .name').click(); await sleep(150);
if (apId() !== other.id || !$('apPop').hidden || !shown('f-' + other.id)) fail('under Learn the menu should still choose an approach');
$('ap-' + A[was].id).click();
$('mode-m').click(); await sleep(200);
if (document.body.classList.contains('is-learn') || !shown('eq') || !shown('iter')) fail('leaving Learn should bring the equation controls back');
return 'Learn keeps the approach menu, the chosen dials and the power, from the Mandelbrot and the Kleinian view; the menu chooses there too';
""", wait=None)

''')

# ----- every entry draws: the chosen entry shows its formula and dials under the menu
rep("""        if (on[0].querySelector('.rule-body').getBoundingClientRect().height <= 0) throw new Error('the chosen entry ' + a.name + ' does not show its formula and dials');""",
    """        const panels = [...document.querySelectorAll('#apPanels .ap-panel')].filter(p => !p.hidden);
        if (panels.length !== 1 || panels[0].dataset.ap !== a.id || !shown('f-' + a.id) || $('apMenuName').textContent !== plain(a.name)) throw new Error('the menu does not show ' + a.name + ' as chosen, with its formula and dials and nobody else\\'s');
        for (const s of a.params || []) if (s.key !== undefined && !s.when && !shown('par-' + a.id + '-' + s.key)) throw new Error('the dial ' + s.label + ' of the chosen entry ' + a.name + ' is not on show');""")
rep("""const same = [], twins = (a, b, mode) => mode === 'j' && [a, b].sort().join() === 'axisbulb,lathe';""",
    """// A second pair is the same by design from round 14 on, where the page has it: with its dials at their starting
// values (slice position 0, tilt 0), Quaternions, 4D (slices) is exactly the quaternion square.
const same = [], twins = (a, b, mode) => (mode === 'j' && [a, b].sort().join() === 'axisbulb,lathe') || [a, b].sort().join() === 'lathe,quat4';""")

# ----- "Reset the approach dials": the dials on show, those of the chosen approach, which stays chosen
between('# 13 Approach reset, then a trap choice', '# 14 quality presets and their mark', r'''# 13 Reset the approach dials (the chosen approach's own, which stays chosen), then a trap choice
step(r"""
let moved = 0;
for (const a of L.APPROACHES) for (const s of a.params || []) if (s.type === 'select') { const e = $('par-' + a.id + '-' + s.key), o = s.options.find(x => x[0] !== s.def); e.value = String(s.options.indexOf(o)); e.dispatchEvent(new Event('change', { bubbles: true })); if (L.S.param[a.id][s.key] !== o[0]) fail('the drop-down ' + s.label + ' of ' + a.name + ' did not take the choice ' + o[1]); moved++; }
const A = L.APPROACHES, me = A[L.S.approach], rb = document.querySelector('#approachReset .dial-reset');
const atStart = a => (a.params || []).every(s => s.key === undefined || s.def === undefined || L.S.param[a.id][s.key] === s.def);
if (me.id !== 'mercator' || atStart(me)) fail('the step before should have left Sphere inversions, one plane chosen with its dials moved');
if (!rb || rb.getBoundingClientRect().width <= 0 || rb.textContent !== 'Reset the approach dials') fail('the button Reset the approach dials should be on show under the dials');
const others = () => JSON.stringify(A.filter(a => a !== me).map(a => L.S.param[a.id])), before = others();
rb.click();
if (L.S.approach !== A.indexOf(me)) fail('Reset the approach dials should keep the approach');
if (!atStart(me)) fail('Reset the approach dials left a dial of ' + me.name + ' moved: ' + JSON.stringify(L.S.param[me.id]));
if (others() !== before) fail('Reset the approach dials should leave the dials of the other approaches alone');
// every approach in turn: the button puts its dials back, and an approach without dials has no such button
let none = 0;
for (const a of A) {
  $('ap-' + a.id).click();
  const has = (a.params || []).some(s => s.key !== undefined);
  if ((rb.getBoundingClientRect().width > 0) !== has) fail('Reset the approach dials should be on show exactly when the approach has dials: ' + a.name);
  if (has) rb.click(); else none++;
  if (apId() !== a.id) fail('Reset the approach dials changed the approach from ' + a.name);
}
for (const a of L.APPROACHES) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined) { const e = s.type === 'select' ? $('par-' + a.id + '-' + s.key) : $('par-' + a.id + '-' + s.key + 'Num'); if (!e) fail('no control for ' + s.label + ' of ' + a.name); const shows = s.type === 'select' ? (s.options[e.selectedIndex] || [])[0] : Number(e.value.replace('−', '-')); if (shows !== s.def) fail('after its reset the control ' + s.label + ' of ' + a.name + ' shows ' + shows + ', not ' + s.def); }
for (const a of L.APPROACHES) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined && L.S.param[a.id][s.key] !== s.def) fail('the reset left ' + s.label + ' of ' + a.name + ' at ' + L.S.param[a.id][s.key]);
$('ap-mercator').click();
pick('col-trap', 'Cross'); pick('col-by', 'How near it came, as a glow'); pick('col-pal', 'Electric');
const c = L.S.colour;
if (c.trap !== 1 || c.by !== 4) fail('trap choice not set: ' + JSON.stringify(c));
return 'Reset the approach dials: the chosen approach keeps its place and gets its starting values, the others are left alone; done for every approach (' + moved + ' drop-downs moved first, ' + none + ' approaches without dials have no button); trap ' + c.trap + ', by ' + c.by + ', palette ' + c.pal;
""", '12-trap-cross')

''')

io.open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('patched', os.path.relpath(P, ROOT))
