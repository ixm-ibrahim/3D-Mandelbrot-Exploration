"""Tester "camera", second check: step files for tools/shot.py. python out/t9/camera/gen.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
from rig import HELP
P = "out/t9/camera/"
PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
PROBE = PRE + "return { cam: +L.cam.dist.toFixed(3), edge: T.edge(), note: T.note(), noteHidden: $('camNote').hidden, extent: T.extent() };"

def write(name, steps):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)
    print("wrote", name, len(steps))

def reshot(st, sub):
    st = dict(st); st["shot"] = st["shot"].replace("out/t6/solids/", P + sub); return st

first = {"js": HELP, "wait": "done", "timeout": 300}
RESET = PRE + "$('reset').click(); await new Promise(r => setTimeout(r, 150)); return 'reset pressed, camera ' + L.cam.dist.toFixed(3);"

# solids-7, Julia: the first check's own steps 1, 12, 13, 14 of out/t6/solids/pj.json, then Reset view
pj = json.load(open(os.path.join(ROOT, "out/t6/solids/pj.json"), encoding="utf-8"))
steps = [first]
for i in (0, 11, 12, 13):
    steps += [reshot(pj[i], "s7/"), {"js": PROBE}]
steps += [{"js": RESET, "wait": "done", "timeout": 420, "shot": P + "s7/p-j-radius2-reset.png", "clip": "#stage"}, {"js": PROBE}]
write("s7j.json", steps)

# solids-7, Kleinian: steps 1, 3, 4, 5 of pk.json, then radius 1 and step 10 (centre x 0.6), each as the dial leaves it; then each with Reset view
pk = json.load(open(os.path.join(ROOT, "out/t6/solids/pk.json"), encoding="utf-8"))
head = pk[0]["js"].split("cam.dist.toFixed(2)].join(' '); };\n")[0] + "cam.dist.toFixed(2)].join(' '); };\n"
def k(js, shot):
    return {"js": head + js + "\nawait sleep(80); return st();", "wait": "done", "timeout": 420, "shot": P + "s7/" + shot, "clip": "#stage"}
steps = [first]
for i in (0, 2, 3, 4):
    steps += [reshot(pk[i], "s7/"), {"js": PROBE}]
steps += [k("type('col-radiusNum', '1'); type('kiterNum', '150'); type('col-txNum', '0.6');", "p-k-tx0.6.png"), {"js": PROBE}]
steps += [{"js": RESET, "wait": "done", "timeout": 420, "shot": P + "s7/p-k-tx0.6-reset.png", "clip": "#stage"}, {"js": PROBE}]
steps += [k("type('col-txNum', '0'); type('col-thickNum', '0.2'); $('reset').click();", "p-k-thick0.2-reset.png"), {"js": PROBE}]
steps += [k("type('col-thickNum', '0.05'); type('col-radiusNum', '1.6'); $('reset').click();", "p-k-radius1.6-reset.png"), {"js": PROBE}]
steps += [k("type('col-radiusNum', '1'); $('reset').click();", "p-k-base-reset.png"), {"js": PROBE}]
write("s7k.json", steps)

# words-2: the first check's command at 375 x 812, with what lies under the picture's controls
write("w2.json", [first,
    {"js": PRE + "return { boxes: T.boxes(), cover: T.cover(), extent: T.extent(), under: T.under() };", "shot": P + "w2-open.png", "clip": "#stage"},
    {"js": "document.getElementById('fig4Show').click()", "wait": "done", "timeout": 300, "shot": P + "w2-fig4.png", "clip": "#stage"},
    {"js": PRE + "return { boxes: T.boxes(), cover: T.cover(), extent: T.extent(), under: T.under(), edge: T.edge(), cam: T.cam() };"},
    {"shot": P + "w2-fig4-window.png"},
    {"js": PRE + "$('twinMerc').click();", "wait": "done", "timeout": 300, "shot": P + "w2-twinM.png", "clip": "#stage"},
    {"js": PRE + "return { extent: T.extent(), under: T.under(), edge: T.edge(), cam: T.cam() };"},
    {"js": PRE + "$('twinLathe').click();", "wait": "done", "timeout": 300, "shot": P + "w2-twinL.png", "clip": "#stage"},
    {"js": PRE + "return { extent: T.extent(), under: T.under(), edge: T.edge(), cam: T.cam() };"},
    {"js": PRE + "$('twinBulb').click();", "wait": "done", "timeout": 300, "shot": P + "w2-twinB.png", "clip": "#stage"},
    {"js": PRE + "return { extent: T.extent(), under: T.under(), edge: T.edge(), cam: T.cam() };"},
])

# words-3: the first check's two states
A = "S.view.zmax = 3; S.iter = 5; L.syncControls(); L.viewChanged(); L.touch(); "
RES = PRE + "return { cam: T.cam(), probes: T.probes(), edge: T.edge(), iter: S.iter, farBox: $('camFar').value, note: T.note() };"
w3 = [first]
for bid, tag in (("fig4Show", "a-fig4"), ("twinMerc", "a-twinM"), ("twinLathe", "a-twinL"), ("twinBulb", "a-twinB")):
    w3 += [{"js": PRE + A + "$('%s').click();" % bid, "sleep": 0.5, "wait": "done", "timeout": 300, "shot": P + "w3-%s.png" % tag, "clip": "#stage"}, {"js": RES}]
w3 += [{"js": PRE + "L.resetAll(); L.setCamMode(true); S.view.bound = 1.5; S.view.fov = Math.tan(100 * Math.PI / 360); L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click();",
        "sleep": 0.5, "wait": "done", "timeout": 300, "shot": P + "w3-b-fig4.png", "clip": "#stage"}, {"js": RES}]
# a variant the first check did not try: the NEAR limit in the way (typed 6, so the camera may not come closer than 6)
w3 += [{"js": PRE + "L.resetAll(); S.view.zmin = 8; S.view.zmax = 60; L.cam.dist = 8; L.syncControls(); L.viewChanged(); L.touch(); $('fig4Show').click();",
        "sleep": 0.5, "wait": "done", "timeout": 300, "shot": P + "w3-c-near8-fig4.png", "clip": "#stage"}, {"js": RES}]
write("w3.json", w3)
