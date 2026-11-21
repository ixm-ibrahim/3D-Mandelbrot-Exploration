"""Steps for tools/shot.py: the tilted quaternion square at several tilts.

python out/me/tilt/steps.py  ->  out/me/tilt/steps.json
"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HEAD = """
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const col = o => Object.assign(L.S.colour, o);
"""
steps = []
def step(js, name):
    steps.append({"js": HEAD + js + " return '" + name + "';", "timeout": 900, "wait": "done",
                  "shot": "out/me/tilt/" + name + ".png", "clip": "#stage canvas"})

TILTS = [0, 15, 30, 45, 60, 90]
first = True
for t in TILTS:
    pick = "$('ap-tilt').click(); await sleep(400); " if first else ""
    first = False
    # the Mandelbrot solid, start view
    step(pick + "$('mode-m').click(); await sleep(200); L.S.cutOn = false; L.S.param.tilt.tilt = %d; L.resetCam(); go(); await sleep(200);" % t, "m-%02d" % t)
    # the same from above (looking down the z-axis side)
    step("L.cam.pitch = 1.25; go();", "m-%02d-top" % t)
    # cut at z = 0: must be the flat Mandelbrot set at every tilt
    step("L.S.cutOn = true; L.S.cut = 0; L.S.colour.cutFace = true; go();", "m-%02d-cut" % t)
    # Julia sets
    step("L.S.cutOn = false; $('mode-j').click(); await sleep(200); L.S.c = [-1, 0, 0]; L.resetCam(); go(); await sleep(200);", "j-bas-%02d" % t)
    step("L.S.c = [-0.122561, 0.744862, 0]; L.resetCam(); go(); await sleep(200);", "j-rab-%02d" % t)

io.open(os.path.join(ROOT, 'out', 'me', 'tilt', 'steps.json'), 'w', encoding='utf-8').write(json.dumps(steps, indent=1))
print(len(steps), 'steps')
