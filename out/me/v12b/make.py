"""Interim Version 12: private copies of three page files of base12a, patched just enough for the split list.

The page engineer of round 12 is doing this properly in src/. These copies only keep the published page
whole in the meantime: the buttons and texts that spoke of the Planes dial of Sphere inversions.

python out/me/v12b/make.py   ->   out/me/v12b/{80-ui.js, 75-presets.js, body.html}
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = os.path.join(ROOT, 'out', 'me', 'v12b')

def patch(rel, name, pairs):
    text = io.open(os.path.join(ROOT, 'base12a', rel), encoding='utf-8').read()
    for old, new, count in pairs:
        assert text.count(old) == count, (name, old[:60], text.count(old))
        text = text.replace(old, new)
    io.open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', name)

patch('js/80-ui.js', '80-ui.js', [
    ("${S.param.mercator && S.param.mercator.planes}", "${S.param.fold && S.param.fold.planes}", 1),
    ("""  const p = S.param.mercator;
  uiApQuiet('mercator');
  S.flat = false; S.mode = 'j'; S.approach = APPROACHES.findIndex(a => a.id === 'mercator');
  p.planes = 2; p.turn = 0; p.lift = 0;""",
     """  const p = S.param.fold;
  uiApQuiet('fold');
  S.flat = false; S.mode = 'j'; S.approach = APPROACHES.findIndex(a => a.id === 'fold');
  p.planes = 2; p.lift = 0;""", 1),
    ("""  uiApQuiet('mercator');
  S.param.mercator.planes = 1;
  S.approach = APPROACHES.findIndex(a => a.id === 'mercator');""",
     """  uiApQuiet('fold');
  S.approach = APPROACHES.findIndex(a => a.id === 'mercator');""", 1),
    ("d.planes !== undefined && `Planes to ${d.planes}`",
     "d.planes !== undefined && (d.planes > 1 ? `the approach to Sphere inversions, two planes${d.planes > 2 ? ', with Planes at ' + d.planes : ''}` : 'the approach to Sphere inversions, one plane')", 1),
])

patch('js/75-presets.js', '75-presets.js', [
    ("""  const d = {}, m = S.param.mercator;
  if (p.planes > 0 && m && ap().id === 'mercator' && m.planes !== p.planes) d.planes = p.planes;""",
     """  // one plane and two planes are entries of their own now: 'mercator' and 'fold'
  const d = {}, id = ap().id, now = id === 'fold' ? S.param.fold.planes : 1;
  if (p.planes > 0 && (id === 'mercator' || id === 'fold') && now !== p.planes) d.planes = p.planes;""", 1),
    ("""  if (d.planes !== undefined) S.param.mercator.planes = d.planes;""",
     """  if (d.planes !== undefined) {
    if (d.planes > 1) S.param.fold.planes = d.planes;
    S.approach = APPROACHES.findIndex(a => a.id === (d.planes > 1 ? 'fold' : 'mercator'));
  }""", 1),
    ("""  if (d.planes !== undefined) uiApproachParam(); else touch();""",
     """  if (d.planes !== undefined) refresh(false); else touch();""", 1),
    ("return ap().id === 'mercator' ?", "return ap().id === 'mercator' || ap().id === 'fold' ?", 1),
    ("set Planes to 2 under Sphere inversions.", "choose “Sphere inversions, two planes” in the Approach list.", 7),
])

patch('body.html', 'body.html', [
    ("With Planes at 1 that formula is the whole rule, and the page opens with it. Planes at 2 or more is an earlier version, kept so that it can be compared. There the count is a free choice",
     "That formula is the whole rule of the entry “Sphere inversions, one plane”, and the page opens with it. The entry “Sphere inversions, two planes” is an earlier version, kept so that it can be compared. There the count of planes is a free choice", 1),
    ("The version you tested had Planes at 2. That setting copies", "The version you tested used two planes. That rule copies", 1),
    ("The page now opens with Planes at 1.", "The page now opens with one plane.", 1),
    ("the same picture appears with Planes at 2 and c on the x-axis", "the same picture appears under “Sphere inversions, two planes” with c on the x-axis", 1),
    ("under Sphere inversions with Planes at 2, and frames it", "under “Sphere inversions, two planes”, and frames it", 1),
    ("Back to one plane sets Planes to 1 again.", "Back to one plane goes to “Sphere inversions, one plane”.", 1),
    ("For the Lathe, and for Sphere inversions with its dials at their starting values (Planes 1, Turn 0, Lift 0),",
     "For the quaternion square (the Lathe), and for Sphere inversions with one plane and its dials at their starting values (Turn 0, Lift 0),", 1),
    ("Six entries look like their names only with Planes at 2,", "Six entries look like their names only with two planes,", 1),
])
