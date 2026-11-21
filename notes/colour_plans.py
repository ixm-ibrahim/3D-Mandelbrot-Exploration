"""Write the contact-sheet plans used to check the colour module (render them with notes/colour_sheet.py).

  python notes/colour_plans.py        -> out/colour/plan-*.json

3D plans run on dist/colour.html (the frozen baseline with src/js/25-colour.js swapped in). The flat-* plans
need the 2D view, which the baseline does not have: they run on dist/colour-flat.html, built with snapshots of
the in-progress shader and renderer (out/colour/shaders-snap.js, out/colour/render-snap.js).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETUP = """
const L = window.squaringLab, S = L.S, cam = L.cam;
S.q.aa = 3;
window.scene = name => {
  if (name === 'default') { S.mode = 'm'; S.approach = 0; S.n = 2; S.iter = 14; cam.yaw = -1; cam.pitch = 0.55; cam.dist = 5.2; cam.target = [-0.6, 0, 0]; }
  if (name === 'classic8') { S.mode = 'm'; S.approach = 3; S.n = 8; S.iter = 10; cam.yaw = -1; cam.pitch = 0.55; cam.dist = 4.2; cam.target = [0, 0, 0]; }
  if (name === 'julia') { S.mode = 'j'; S.approach = 0; S.n = 2; S.iter = 14; S.c = [-1, 0, 0]; cam.yaw = -1.25; cam.pitch = 1.0; cam.dist = 4.8; cam.target = [0, 0, 0]; }
  if (name === 'klein') { S.mode = 'k'; cam.yaw = 0.35; cam.pitch = 0.35; cam.dist = 7; cam.target = [0, 0, 0]; }
};
window.col = o => { Object.assign(S.colour, window.col0, o); L.syncControls(); L.refresh(false); };
window.col0 = Object.assign({}, S.colour);
return JSON.stringify(S.colour);
"""
FLAT = SETUP.replace("S.q.aa = 3;", "S.q.aa = 4; S.flat = true;")
PALS = ['Brass and verdigris', 'Ember', 'Glacier', 'Moss and rust', 'Stone', 'Fire', 'Electric', 'Sunset', 'Rainbow', 'Ocean',
        'Neon', 'Classic blue and gold', 'Viridis', 'Aurora', 'Candy', 'Peacock', 'Ice and fire', 'Porcelain', 'Orchid']
TRAPS = ['point', 'cross', 'line', 'ray', 'planes', 'shell', 'ring', 'three tones']
BY = ['bands', 'step', 'blend with escape', 'side', 'glow']
MODES = {0: 'trap', 2: 'escape count', 3: 'distance from centre', 4: 'depth', 5: 'last step', 6: 'surface direction', 7: 'clay'}


def tile(scene, **col):
    bits = []
    if col.get('mode', 0) != 0: bits.append(MODES[col['mode']])
    if 'trap' in col: bits.append(TRAPS[col['trap']])
    if 'by' in col: bits.append(BY[col['by']])
    if 'pal' in col: bits.append(PALS[col['pal']])
    bits += ['%s=%s' % (k, v) for k, v in col.items() if k not in ('mode', 'trap', 'by', 'pal')]
    return {"label": scene + ': ' + (', '.join(bits) or 'as it opens'), "js": "scene(%s); col(%s);" % (json.dumps(scene), json.dumps(col))}


def plan(name, tiles, cols=4, size="1000x640", tile_w=330, setup=SETUP, clip="#stage"):
    p = {"name": name, "size": size, "cols": cols, "tile": tile_w, "clip": clip, "setup": setup, "tiles": tiles}
    with open(os.path.join(ROOT, "out", "colour", "plan-%s.json" % name), "w", encoding="utf-8") as f:
        json.dump(p, f, indent=1)


os.makedirs(os.path.join(ROOT, "out", "colour"), exist_ok=True)
SCENES = ('default', 'classic8', 'julia', 'klein')
# the picture each scene opens with, at full size
plan("big-default", [tile(s) for s in SCENES], cols=2, size="1400x950", tile_w=660)
# every palette, with the default trap
plan("pals-a", [tile('default', pal=i) for i in range(0, 10)])
plan("pals-b", [tile('default', pal=i) for i in range(10, 19)])
# every trap shape, and every "trap colours by"
plan("traps-default", [tile('default', trap=i) for i in range(8)])
plan("traps-classic8", [tile('classic8', trap=i) for i in range(8)])
plan("by", [tile(s, trap=t, by=b) for s, t in (('default', 4), ('classic8', 1)) for b in (0, 4, 1, 2, 3)], cols=5, tile_w=264)
# the three scenes the assignment names, eight palette / trap combinations each
COMBOS = [dict(), dict(trap=1, by=4, pal=6), dict(trap=0, by=1, pal=10), dict(trap=5, by=2, pal=11),
          dict(trap=6, pal=13), dict(trap=3, by=3, pal=8), dict(mode=2, pal=5), dict(trap=7, pal=0)]
for s in ('classic8', 'julia', 'klein'):
    plan("scene-" + s, [tile(s, **c) for c in COMBOS])
# the other modes
plan("modes", [tile(s, mode=m) for s in ('classic8', 'julia') for m in (2, 3, 4, 5, 6, 7)])
# trap dials: centre, radius, axis, ray, and the palette dials
plan("dials", [tile('classic8', trap=0, tx=0.6), tile('classic8', trap=5, radius=1.0), tile('classic8', trap=6, radius=0.4),
               tile('classic8', trap=2, axis=2), tile('classic8', trap=3, ray=4), tile('classic8', rev=True),
               tile('classic8', bands=3), tile('classic8', shift=0.5)])
# the 2D view
FCOMBOS = [dict(), dict(by=4), dict(trap=0, pal=6), dict(trap=1, by=1, pal=10), dict(trap=5, by=2, pal=11), dict(trap=6, by=3, pal=8),
           dict(trap=7, pal=0), dict(mode=2, pal=5), dict(mode=2, pal=11, bands=0.5), dict(mode=3, pal=13), dict(mode=5, pal=14), dict(mode=7)]
plan("flat-m", [tile('default', **c) for c in FCOMBOS], setup=FLAT)
plan("flat-j", [tile('julia', **c) for c in FCOMBOS[:8]], setup=FLAT.replace("S.flat = true;", "S.flat = true; S.v2.x = 0; S.v2.h = 3.4;"))
plan("flat-k", [tile('klein', **c) for c in FCOMBOS[:8]], setup=FLAT.replace("S.flat = true;", "S.flat = true; S.v2.x = 0; S.v2.h = 5;"))
plan("flat-big", [tile('default'), tile('default', by=4), tile('default', mode=2, pal=11, bands=0.5), tile('julia', trap=5, by=2, pal=6)],
     cols=2, size="1400x950", tile_w=660, setup=FLAT)
plan("flat-pal", [tile('default', mode=2, pal=p, rev=r) for p in (7, 8, 0, 10) for r in (False, True)], setup=FLAT)



# Escape count on a surface. "low" is the case that used to come out as one dark colour: a step limit of 10
# that no surface point escapes within, seen from straight above.
def low(**c):
    t = tile('julia', **c)
    t["js"] = "scene('julia'); S.iter = 10; cam.pitch = 1.5; cam.yaw = -Math.PI / 2; cam.dist = 4.4; col(%s);" % json.dumps(c)
    t["label"] = t["label"].replace('julia', 'julia from above, 10 steps')
    return t


plan("escape", [f(mode=2, pal=p) for p in (1, 7, 5, 6) for f in (lambda **c: tile('classic8', **c), low, lambda **c: tile('klein', **c))],
     cols=6, tile_w=220, setup=SETUP.replace("window.scene", "window.S = S; window.cam = cam; window.scene"))
print("plans written")
