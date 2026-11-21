"""Add the mirror twin checks to out/r4/page/make_smoke.py (run once from the project root).

- step 7 also asks for the twin answer, its four buttons and the labels it names;
- four new steps before "collapse all": each twin button from a far-away state, the picture not empty, and
  "Back to the plain rule".
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(ROOT, 'out', 'r4', 'page', 'make_smoke.py')
s = io.open(path, encoding='utf-8').read()
if 'twinMerc' in s:
    print('already patched')
    sys.exit(0)

def rep(a, b):
    global s
    assert s.count(a) == 1, 'expected exactly one place for: ' + a[:70]
    s = s.replace(a, b)

# step 7: phrases of the closing text
rep("'the first real test of saving a file from the published page is yours', 'Preparing the formula']",
    "'the first real test of saving a file from the published page is yours', 'Preparing the formula',\n"
    "  'Every rule has a mirror twin', 'the pictures match pixel for pixel', 'None of the three is Figure 4', 'It is not finished']")
# step 7: labels the closing text names (the modifiers note is outside the footer, so it is looked for on the whole page)
rep("'Show Figure 4', 'Back to one plane', 'Lathe', 'Sphere inversions', 'Colour and light', 'Kleinian group']",
    "'Show Figure 4', 'Back to one plane', 'Lathe', 'Sphere inversions', 'Colour and light', 'Kleinian group',\n"
    "  'flip z', 'Height z of the cut or slice', 'Trap radius', 'Twin of Sphere inversions', 'Twin of the Lathe', 'Twin of the Mandelbulb', 'Back to the plain rule', 'Mandelbulb']")
rep("const all = document.body.textContent;\n",
    "const all = document.body.textContent;\nif (!all.includes('turns a rule into its mirror twin')) fail('the note under Modifiers does not say what flip z is for');\n")

NEW = r'''
# the mirror twins: each button shows the Mandelbrot solid of one approach with "flip z" ticked, from any state
TWIN_CHECK = r"""
const twinState = (btn, id) => {
  const S = L.S, bad = [];
  if (S.mode !== 'm' || !$('mode-m').checked) bad.push('the mode');
  if (S.flat || $('flat').checked) bad.push('the 2D view');
  if (L.APPROACHES[S.approach].id !== id || !$('ap-' + id).checked) bad.push('the approach');
  if (S.flip.join() !== '0,1' || !$('flipz').checked || $('flipy').checked) bad.push('flip z');
  if (S.n !== 2 || $('powNum').value !== '2') bad.push('the power at ' + $('powNum').value);
  if (S.eq !== 'z^n + c' || S.cutOn || $('cutOn').checked || S.abs.join() !== '0,0,0' || $('absy').checked || S.colour.solid !== 0 || S.mosaic) bad.push('the equation, the cut, a modifier, the mosaic or the trap solid');
  const p = S.param.mercator;
  if (id === 'mercator' && (p.planes !== 1 || p.turn !== 0 || p.lift !== 0 || $('par-mercator-planesNum').value !== '1')) bad.push('the dials of Sphere inversions');
  if ($('mandelPanel').hidden || !$('juliaPanel').hidden || !$('kleinPanel').hidden) bad.push('the panels');
  if (bad.length) fail(btn + ' did not set: ' + bad.join('; '));
  const r = $('stage').getBoundingClientRect();
  if (r.bottom <= 0 || r.top >= innerHeight) fail('after ' + btn + ' the picture is out of view');
};
const twinPicture = name => { const h = hits(probes()); if (h < 5) fail('the picture of the twin of ' + name + ' is empty: ' + h + ' of 49 probes hit'); return h; };
"""
step(TWIN_CHECK + r"""
type('par-mercator-planesNum', '3'); type('par-mercator-liftNum', '0.4');
$('mode-k').click(); $('flat').click(); $('cutOn').click(); $('absy').click(); $('flipy').click(); pick('col-solid', 'Is the solid'); type('powNum', '3');
await sleep(200);
$('twinMerc').click(); await sleep(400);
twinState('Twin of Sphere inversions', 'mercator');
return 'Twin of Sphere inversions from the Kleinian 2D view: Mandelbrot, power 2, one plane, flip z ticked';
""", '21g-twin-inversions')
step(TWIN_CHECK + r"""
const h = twinPicture('Sphere inversions');
$('m-mosaic').click(); await sleep(150);
$('twinLathe').click(); await sleep(400);
twinState('Twin of the Lathe', 'lathe');
return 'twin of Sphere inversions drawn (' + h + ' of 49 probes hit); Twin of the Lathe from the mosaic';
""", '21h-twin-lathe')
step(TWIN_CHECK + r"""
const h = twinPicture('the Lathe');
$('twinBulb').click(); await sleep(400);
twinState('Twin of the Mandelbulb', 'bulb');
return 'twin of the Lathe drawn (' + h + ' of 49 probes hit); Twin of the Mandelbulb';
""", '21i-twin-bulb')
step(TWIN_CHECK + r"""
const h = twinPicture('the Mandelbulb'), view = camNow();
$('twinOff').click(); await sleep(300);
if (L.S.flip.join() !== '0,0' || $('flipz').checked) fail('Back to the plain rule left flip z on');
if (L.S.mode !== 'm' || L.APPROACHES[L.S.approach].id !== 'bulb' || camNow() !== view) fail('Back to the plain rule changed more than flip z');
$('resetAll').click(); await sleep(300);
if (L.S.mode !== 'm' || L.S.approach !== 0 || L.S.flip.join() !== '0,0') fail('Reset everything did not bring the opening state back');
L.S.q.aa = 2; L.syncControls(); L.touch();
return 'twin of the Mandelbulb drawn (' + h + ' of 49 probes hit); Back to the plain rule unticked flip z and nothing else';
""")

'''
rep("\n# 24 collapse all, also for the sections of the other modes\n", NEW + "# 24 collapse all, also for the sections of the other modes\n")
io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', path)
