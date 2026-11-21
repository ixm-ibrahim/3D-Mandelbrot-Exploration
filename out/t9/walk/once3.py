"""Reduction of the walk's findings on a fresh page, with real keys only.
  python out/t9/walk/once3.py
A. a typed box emptied with select-all, Delete and then Enter or Tab: does the old value come back?
B. the blank picture of seed 13, step 32: Twin of the Mandelbulb, then the two quality dials the walk had moved.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import Lab, HERE
for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass


def out(*a):
    print(*a, flush=True)


def save(lab, name):
    with open(os.path.join(HERE, name), "wb") as f:
        f.write(lab.shot_png())


lab = Lab()
out("fresh page idle after", lab.wait_idle(240))
lab.js("for (const d of document.querySelectorAll('#sections details, details')) d.open = true;")
time.sleep(0.5)
Q = "const e = document.querySelector(%s); return { value: e.value, invalid: e.getAttribute('aria-invalid'), active: document.activeElement === e };"
STATE = "const c = squaringLab.S.colour; return { reach: c.reach, shift: c.shift, glow: c.glow, radius: c.radius, bands: c.bands, iter: squaringLab.S.iter, lightAz: squaringLab.S.lightAz };"
for sel, commit in (("#col-reachNum", "Enter"), ("#col-shiftNum", "Tab"), ("#col-glowNum", "Enter"), ("#col-radiusNum", "Enter"), ("#col-bandsNum", "Tab"),
                    ("#lightAzNum", "Enter"), ("#iterNum", "Enter"), ("#meshMmNum", "Enter"), ("#viewBoundNum", "Enter")):
    before = lab.js(Q % json.dumps(sel))
    how = lab.click(sel, count=3)
    lab.js("const e = document.querySelector(%s); e.focus(); e.select();" % json.dumps(sel))
    lab.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key="Delete", code="Delete", windowsVirtualKeyCode=46)
    lab.p.call("Input.dispatchKeyEvent", type="keyUp", key="Delete", code="Delete", windowsVirtualKeyCode=46)
    v1 = lab.js("return document.querySelector(%s).value;" % json.dumps(sel))
    lab.key(commit); time.sleep(0.4)
    a1 = lab.js(Q % json.dumps(sel))
    lab.click("#status"); time.sleep(0.4)
    a2 = lab.js(Q % json.dumps(sel))
    time.sleep(2.5)
    a3 = lab.js(Q % json.dumps(sel))
    out("A.", sel, "(%s)" % how, "before", before["value"], "| after select-all and Delete:", repr(v1), "|", commit, "->", a1, "| clicked elsewhere ->", a2, "| 2.5 s later ->", a3)
out("   state:", lab.js(STATE), "problems", lab.problems())
save(lab, "once3-empty.png")
lab.js("document.getElementById('col-reachNum').scrollIntoView({ block: 'center' });"); time.sleep(0.3)
save(lab, "once3-empty-colour.png")

# B. seed 13, step 32
lab.click("#resetAll"); lab.wait_idle(120)
out("B. after Reset everything:", lab.picture_stats())
for name, js in (("Twin of the Mandelbulb", None),
                 ("Ray step, share of the distance estimate = 1.88", "const e = document.getElementById('qstepkNum'); e.focus(); e.select();"),
                 ("Surface threshold, pixels = 17.92", "const e = document.getElementById('qdetailNum'); e.focus(); e.select();")):
    if js is None:
        lab.click("#twinBulb")
    else:
        if "17.92" in name and not lab.js("return squaringLab.isExtreme();"):
            lab.click("#extreme"); time.sleep(0.3)
        lab.js(js)
        lab.p.call("Input.insertText", text=name.split("= ")[1]); lab.key("Enter")
    t = lab.wait_idle(240)
    st = lab.picture_stats(os.path.join(HERE, "once3-B-%s.png" % name.split(" ")[0].lower()))
    q = lab.js("const S = squaringLab.S; return { approach: S.approach, flip: S.flip, stepk: S.q.stepk, detail: S.q.detail, de: S.q.de, extreme: squaringLab.isExtreme(), status: document.getElementById('status').textContent };")
    out("B.", name, "-> idle after", t and round(t, 1), "picture", st, q)
save(lab, "once3-B-end.png")
lab.click("#reset"); lab.wait_idle(120)
out("B. Reset view ->", lab.picture_stats())
# C. seed 12, step 48: Julia, two planes (Figure 4), power 1.9, 14 iterations, Ultra fast
lab.click("#resetAll"); lab.wait_idle(120)
def stat(tag):
    t = lab.wait_idle(240)
    out("C.", tag, "-> idle", t and round(t, 1), lab.picture_stats(os.path.join(HERE, "once3-C-%s.png" % tag.split(" ")[0].lower())), lab.js("const S = squaringLab.S; return { mode: S.mode, n: S.n, iter: S.iter, planes: S.param.mercator.planes, note: !document.getElementById('stageNote').hidden };"))
lab.click("#mode-j"); stat("julia")
lab.js("const e = document.getElementById('powNum'); e.scrollIntoView({ block: 'center' }); e.focus(); e.select();"); lab.p.call("Input.insertText", text="1.9"); lab.key("Enter"); stat("power 1.9")
lab.js("const e = document.getElementById('iterNum'); e.focus(); e.select();"); lab.p.call("Input.insertText", text="14"); lab.key("Enter"); stat("iterations 14")
lab.click("#fig4Show"); stat("figure4 pressed")
lab.js("const e = document.getElementById('powNum'); e.focus(); e.select();"); lab.p.call("Input.insertText", text="1.9"); lab.key("Enter"); stat("power19 again")
lab.click("#qUltra"); stat("ultra fast")
save(lab, "once3-C-end.png")
out("problems", lab.problems())
lab.close()
