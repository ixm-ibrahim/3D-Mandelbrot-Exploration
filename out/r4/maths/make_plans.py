"""Write the plans for out/r4/maths/sheet.py: the Lift dial, the one-plane Mandelbrot solid, slices off z = 0."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = "const L = window.squaringLab, S = L.S, P = S.param.mercator; "
SETUP = "const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 4; L.syncControls(); L.touch(); return 'approach ' + L.APPROACHES[L.S.approach].id + ', planes ' + L.S.param.mercator.planes;"


def base(n, planes, lift=0, mode='m'):
    return (PRE + "document.getElementById('mode-%s').click(); S.n = %s; P.planes = %d; P.lift = %s; P.turn = 0; S.flat = false; S.cutOn = false; "
            "L.syncControls(); L.resetCam(); " % (mode, n, planes, lift))


def cam(yaw, pitch, dist):
    return "L.cam.yaw = %s; L.cam.pitch = %s; L.cam.dist = %s; L.cam.target = [0, 0, 0]; " % (yaw, pitch, dist)


END = "L.refresh(false); return 'ok';"
tiles = []
for n in (2, 8):
    for lift in (-1, 0, 1):
        tiles.append({"label": "Mandelbrot n=%d, 1 plane, lift %s" % (n, lift), "js": base(n, 1, lift) + cam(-1, 0.55, 5.2 if n == 2 else 4.4) + END})
json.dump({"name": "lift", "cols": 3, "setup": SETUP, "tiles": tiles}, open(os.path.join(HERE, "plan-lift.json"), "w"))

tiles = []
for n, dist in ((2, 5.2), (3, 4.8)):
    for planes in (1, 2):
        tiles.append({"label": "p9: Mandelbrot n=%d, %d plane(s)" % (n, planes), "js": base(n, planes) + cam(-1, 0.55, dist) + END})
# the user's own test (N1): cut the solid away from z = 0 and look at the slice
for planes in (1, 2):
    tiles.append({"label": "Mandelbrot n=2, %d plane(s), cut open at z = 0.3" % planes,
                  "js": base(2, planes) + "S.cutOn = true; S.cut = 0.3; L.syncControls(); " + cam(-1.2, 1.0, 5.2) + END})
for planes in (1, 2):
    tiles.append({"label": "Mandelbrot n=2, %d plane(s), 2D view of the slice z = 0.3" % planes,
                  "js": base(2, planes) + "S.cut = 0.3; S.flat = true; L.syncControls(); L.resetCam(); " + END})
for planes in (1, 2):
    tiles.append({"label": "Julia c = -1, %d plane(s), 2D view of the slice z = 0.3" % planes,
                  "js": base(2, planes, 0, 'j') + "S.c = [-1, 0, 0]; S.cut = 0.3; S.flat = true; L.syncControls(); L.resetCam(); " + END})
for planes in (1, 2):
    tiles.append({"label": "Julia rabbit, %d plane(s), 2D view of the slice z = 0.2" % planes,
                  "js": base(2, planes, 0, 'j') + "S.c = [-0.122561, 0.744862, 0]; S.cut = 0.2; S.flat = true; L.syncControls(); L.resetCam(); " + END})
json.dump({"name": "oneplane", "cols": 2, "tile": 480, "setup": SETUP, "tiles": tiles}, open(os.path.join(HERE, "plan-oneplane.json"), "w"))
print("plans written")
