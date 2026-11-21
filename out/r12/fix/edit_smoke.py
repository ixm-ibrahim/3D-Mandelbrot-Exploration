"""Fixer of round 12: bring out/r4/page/make_smoke.py in step with the corrected words of the page, and make the
test look at pictures and controls where the checker found it blind (defect T1). Run once, from the project root:
  python out/r12/fix/edit_smoke.py
A copy of the file as it was is kept beside this script (make_smoke.before-fix.py)."""
import io, os, shutil

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", "..", ".."))
path = os.path.join(root, "out", "r4", "page", "make_smoke.py")
keep = os.path.join(here, "make_smoke.before-fix.py")
if not os.path.exists(keep):
    shutil.copyfile(path, keep)
with io.open(path, encoding="utf-8") as f:
    s = f.read()


def swap(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit("expected %d of %r, found %d" % (count, old[:70], n))
    s = s.replace(old, new)


# ---- words that changed on the page
swap("'Back to one plane chooses Sphere inversions, one plane, and changes nothing else',",
     "'Back to one plane chooses Sphere inversions, one plane. From a Mandelbrot or Julia picture it changes nothing else', 'From the Kleinian view it also goes to the Julia set',")
swap("'up close its skin is smooth',", "'in the close-up pictures its skin is smooth sheets and folds', 'nothing further than 2 from the centre belongs to it', 'at power 2 it is what Quaternion square, twisted gives',")
swap("'Twin of Sphere inversions', 'Twin of the Lathe', 'Twin of the Mandelbulb',", "'Twin of Sphere inversions, one plane', 'Twin of the quaternion square', 'Twin of the Mandelbulb',")
swap("for (const t of ['had Planes at 2', 'Planes at 1',",
     "for (const t of ['has no end', 'runs off along a band', 'Twin of the Lathe', 'the Lathe’s mirror twin', 'as with every quaternion rule', 'no plane chosen and no seam', 'For every approach here except', 'had Planes at 2', 'Planes at 1',")
swap("twinState('Twin of Sphere inversions', 'mercator');",
     "if ($('twinMerc').textContent !== 'Twin of Sphere inversions, one plane' || $('twinLathe').textContent !== 'Twin of the quaternion square') fail('the twin buttons should name their entries: ' + $('twinMerc').textContent + ' / ' + $('twinLathe').textContent);\ntwinState('Twin of Sphere inversions, one plane', 'mercator');")
swap("return 'Twin of Sphere inversions from the Kleinian 2D view:", "return 'Twin of Sphere inversions, one plane from the Kleinian 2D view:")
swap("twinState('Twin of the Lathe', 'lathe');", "twinState('Twin of the quaternion square', 'lathe');")
swap("Twin of the Lathe from the mosaic';", "Twin of the quaternion square from the mosaic';")
swap("const h = twinPicture('the Lathe');", "const h = twinPicture('the quaternion square');")
swap("return 'twin of the Lathe drawn (", "return 'twin of the quaternion square drawn (")
# As it was found, with the two-planes entry already in use: the words name the dial that moves (defect W2)
swap("f.textContent !== 'As it was found: two planes' || !f.title.includes('Planes to 2')) fail('with Planes at 3 the button should offer to set them to 2: '",
     "f.textContent !== 'As it was found: Planes at 2' || !f.title.includes('Planes to 2')) fail('with Planes at 3 the button should say that it sets Planes to 2: '")

# ---- T1: every entry drawing. Keep which probes hit, and fail when two entries that should differ draw the same.
swap("        const g = grid();\n        E.rows.push(a.id + ' ' + mode + ' ' + g[0]);",
     "        const g = grid();\n        E.rows.push(a.id + ' ' + mode + ' ' + g[0]);\n        E.pics.push([a.id, mode, gridS()]);")
swap("const E = window.smokeEntries = { done: false, error: '', rows: [] };",
     "const E = window.smokeEntries = { done: false, error: '', rows: [], pics: [] };\n"
     "// which of the 15 x 11 probes hit, as a string of 165 marks\n"
     "const gridS = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) s += L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11) ? '1' : '0'; return s; };")
swap("if (E.rows.length !== 2 * L.APPROACHES.length) fail('not every entry was drawn: ' + E.rows.join(', '));",
     "if (E.rows.length !== 2 * L.APPROACHES.length) fail('not every entry was drawn: ' + E.rows.join(', '));\n"
     "// Two entries must not draw the same picture. One pair is the same set by design and is left out: for a c on the\n"
     "// x-axis, Bulbs about the axis keeps the Julia set of the quaternion square (that is the entry's own verdict).\n"
     "const same = [], twins = (a, b, mode) => mode === 'j' && [a, b].sort().join() === 'axisbulb,lathe';\n"
     "let least = 165;\n"
     "for (let i = 0; i < E.pics.length; i++) for (let j = i + 1; j < E.pics.length; j++) {\n"
     "  const [a, ma, sa] = E.pics[i], [b, mb, sb] = E.pics[j];\n"
     "  if (ma !== mb || twins(a, b, ma)) continue;\n"
     "  let d = 0; for (let q = 0; q < sa.length; q++) if (sa[q] !== sb[q]) d++;\n"
     "  least = Math.min(least, d);\n"
     "  if (d === 0) same.push(a + ' and ' + b + ' (' + ma + ')');\n"
     "}\n"
     "if (same.length) fail('two entries draw the same picture, probe for probe: ' + same.join('; '));")
swap("return 'every entry drew (entry, m or j, probes hit of 165): ' + E.rows.join(', ');",
     "return 'every entry drew (entry, m or j, probes hit of 165): ' + E.rows.join(', ') + '; no two entries draw the same picture (the two closest differ in ' + least + ' of 165 probes)';")

# ---- T1: the Approach reset. Move drop-downs too, and look at what the controls show, not only at the state.
swap("document.querySelector('#approachReset .dial-reset').click();\nif (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');",
     "let moved = 0;\n"
     "for (const a of L.APPROACHES) for (const s of a.params || []) if (s.type === 'select') { const e = $('par-' + a.id + '-' + s.key), o = s.options.find(x => x[0] !== s.def); e.value = String(s.options.indexOf(o)); e.dispatchEvent(new Event('change', { bubbles: true })); if (L.S.param[a.id][s.key] !== o[0]) fail('the drop-down ' + s.label + ' of ' + a.name + ' did not take the choice ' + o[1]); moved++; }\n"
     "document.querySelector('#approachReset .dial-reset').click();\nif (L.S.approach !== 0) fail('the Approach reset should go back to the first approach');\n"
     "for (const a of L.APPROACHES) for (const s of a.params || []) if (s.key !== undefined && s.def !== undefined) { const e = s.type === 'select' ? $('par-' + a.id + '-' + s.key) : $('par-' + a.id + '-' + s.key + 'Num'); if (!e) fail('no control for ' + s.label + ' of ' + a.name); const shows = s.type === 'select' ? (s.options[e.selectedIndex] || [])[0] : Number(e.value.replace('−', '-')); if (shows !== s.def) fail('after the Approach reset the control ' + s.label + ' of ' + a.name + ' shows ' + shows + ', not ' + s.def); }")
swap("return 'trap ' + c.trap + ', by ' + c.by + ', palette ' + c.pal;",
     "return 'Approach reset: every dial and drop-down shows its starting value (' + moved + ' drop-downs moved first); trap ' + c.trap + ', by ' + c.by + ', palette ' + c.pal;")

# ---- T1: Figure 4 against the one-plane picture. The 49 probes cannot tell the two apart, so a finer grid is read
# before and after Back to one plane, with both pictures fully drawn.
swap("const two = probes(), whole = grid();\nif (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');",
     "const fine = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 44; i++) for (let j = 0; j < 30; j++) s += L.pick(w * (i + 0.5) / 44, h * (j + 0.5) / 30) ? '1' : '0'; return s; };\n"
     "const drawn = async () => { for (let i = 0; i < 1200 && !L.idle(); i++) await sleep(100); if (!L.idle()) fail('the picture was not finished after 120 s'); };\n"
     "await drawn();\n"
     "const two = probes(), whole = grid(), fig4 = fine();\nif (hits(two) < 5) fail('the picture of Figure 4 is empty: ' + hits(two) + ' of 49 probes hit');")
swap("if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the approach');\nreturn 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane chose Sphere inversions, one plane and nothing else';",
     "if (L.S.mode !== 'j' || L.S.c.join() !== '-1,0,0' || camNow() !== view) fail('Back to one plane changed more than the approach');\n"
     "await drawn();\n"
     "const one = fine(); let differ = 0; for (let q = 0; q < one.length; q++) if (one[q] !== fig4[q]) differ++;\n"
     "if (hits(one) < 40) fail('the one-plane picture after Back to one plane is (nearly) empty: ' + hits(one) + ' of 1320 probes hit');\n"
     "if (differ < 8) fail('the picture did not change with Back to one plane: ' + differ + ' of 1320 probes differ from the Figure 4 picture');\n"
     "return 'Figure 4 picture: ' + hits(two) + ' of 49 probes hit; Back to one plane chose Sphere inversions, one plane and nothing else; the picture changed (' + differ + ' of 1320 probes differ, ' + hits(fig4) + ' hit before and ' + hits(one) + ' after)';")
# ... from the Kleinian view the page text now says what else happens: check it
swap("if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');",
     "if (L.S.mode !== 'j' || !$('mode-j').checked) fail('from the Kleinian view, Back to one plane should go to the Julia set');\n"
     "if (Math.abs(L.cam.dist - 4.8) > 1e-6 || $('juliaPanel').hidden || !$('kleinPanel').hidden || $('secApproach').hidden) fail('from the Kleinian view, Back to one plane should put the camera back to its starting view and show the Julia panels: camera at ' + L.cam.dist);")

# ---- T1: a new step. Every choice of the drop-downs in the Approach list sets its value, shows it and draws.
marker = "# the mirror twins: each button shows the Mandelbrot solid of one approach"
new_step = r'''# every drop-down of the Approach list (the entries kept for the record have three): each choice sets its value,
# shows it, changes the formula text where the entry writes one for it, and draws a picture that is not empty
step(r"""
const E = window.smokeChoices = { done: false, error: '', rows: [] };
const gridS = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) s += L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11) ? '1' : '0'; return s; };
(async () => {
  try {
    const settle = async name => { await sleep(150); const t0 = performance.now(); while (!L.idle()) { if (performance.now() - t0 > 120000) throw new Error('the picture of ' + name + ' was not finished after 120 s'); await sleep(40); } };
    $('resetAll').click(); await sleep(200);
    for (const a of L.APPROACHES) for (const s of a.params || []) {
      if (s.type !== 'select') continue;
      $('ap-' + a.id).click(); await settle(a.name);
      const e = $('par-' + a.id + '-' + s.key);
      if (!e || !shown('par-' + a.id + '-' + s.key)) throw new Error('the drop-down ' + s.label + ' of ' + a.name + ' is not on show');
      if (e.options.length !== s.options.length) throw new Error('the drop-down ' + s.label + ' of ' + a.name + ' has ' + e.options.length + ' choices, not ' + s.options.length);
      const pics = [];
      for (const o of s.options) {
        e.value = String(s.options.indexOf(o)); e.dispatchEvent(new Event('change', { bubbles: true })); await settle(a.name + ' with ' + o[1]);
        if (L.S.param[a.id][s.key] !== o[0] || e.options[e.selectedIndex].text !== o[1]) throw new Error('choosing ' + o[1] + ' in ' + s.label + ' of ' + a.name + ' did not take');
        if (apId() !== a.id) throw new Error('choosing ' + o[1] + ' changed the approach');
        if (!$('f-' + a.id).textContent.trim()) throw new Error('no formula text for ' + a.name + ' with ' + o[1]);
        const p = gridS();
        if (hits(p) < 1) throw new Error('the picture of ' + a.name + ' with ' + o[1] + ' is empty');
        pics.push(p);
      }
      const d = pics.slice(1).map(p => { let n = 0; for (let q = 0; q < p.length; q++) if (p[q] !== pics[0][q]) n++; return n; });
      // the two layouts of the Pillow and the pinch of Blended planes are different rules: their pictures must differ
      if (a.id === 'pillow' && s.key === 'layout' && d[0] === 0) throw new Error('the two layouts of the Pillow draw the same picture');
      if (a.id === 'softfold' && s.key === 'mix' && d[d.length - 1] === 0) throw new Error('the pinch of Blended planes draws the same picture as the blend');
      E.rows.push(a.id + ' ' + s.key + ': ' + s.options.length + ' choices, probes that differ from the first: ' + d.join(' and '));
      e.value = String(s.options.findIndex(x => x[0] === s.def)); e.dispatchEvent(new Event('change', { bubbles: true }));
    }
    $('resetAll').click(); await sleep(300);
    L.S.q.aa = 2; L.syncControls(); L.touch();
  } catch (e) { E.error = e.message || String(e); }
  E.done = true;
})();
return 'trying every choice of the drop-downs in the Approach list';
""", wait='window.smokeChoices && window.smokeChoices.done', timeout=900)
step(r"""
const E = window.smokeChoices;
if (E.error) fail(E.error + ' (done before that: ' + E.rows.join('; ') + ')');
if (L.S.mode !== 'm' || L.S.approach !== 0) fail('Reset everything did not bring the opening state back after the drop-downs');
return E.rows.length ? 'every choice of every drop-down in the Approach list set its value and drew: ' + E.rows.join('; ') : 'the Approach list has no drop-downs on this page';
""")

'''
swap(marker, new_step + marker)

with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(s)
print("edited", os.path.relpath(path, root))
