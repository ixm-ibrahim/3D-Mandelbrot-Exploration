"""walk-1 once more, alone on a fresh page and with the context lost while the mesh is being built (the first
check's run lost it at "Building the mesh, slice 7 of 68"; once.py context on Version 8 lost it at "Starting").
  python out/t9/walk/once2.py
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


def brief(c):
    return {k: c[k] for k in ("idle", "busy", "bar", "status", "bad", "exp", "mesh", "glfail", "mode", "flat", "lost")}


MPANEL = ("return { msg: (document.getElementById('meshMsg')||{}).textContent, step: (document.getElementById('meshStep')||{}).textContent, "
          "btns: [...document.querySelectorAll('#meshPanel button')].filter(b => __w.vis(b)).map(b => b.textContent).filter(t => t.length > 2), busy: squaringLab.meshBusy() };")
LOSE = "const gl = document.getElementById('view').getContext('webgl2'); window.__ext = window.__ext || gl.getExtension('WEBGL_lose_context'); window.__ext.loseContext(); await new Promise(r => setTimeout(r, 300)); return gl.isContextLost();"
REST = "window.__ext.restoreContext(); await new Promise(r => setTimeout(r, 300)); return document.getElementById('view').getContext('webgl2').isContextLost();"

lab = Lab()
out("fresh page idle after", lab.wait_idle(240), "problems", lab.problems())
lab.click("#secMesh > summary"); lab.click("#meshStart")
t0 = time.time(); p = None
while time.time() - t0 < 180:
    p = lab.js(MPANEL)
    if "slice" in (p["step"] or "") or not p["busy"]:
        break
    time.sleep(0.1)
out("A. model job after %.1f s:" % (time.time() - t0), p)
out("   lost during the job:", lab.js(LOSE)); time.sleep(2)
out("   panel:", lab.js(MPANEL), brief(lab.check()), "problems", lab.problems())
save(lab, "once2-model-lost.png")
out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats())
time.sleep(1); out("   panel after restore:", lab.js(MPANEL), "problems", lab.problems())
how = lab.click("#meshStart"); t0 = time.time(); time.sleep(0.5)
while time.time() - t0 < 400 and lab.js("return squaringLab.meshBusy();"):
    time.sleep(0.5)
out("   a new model after restore (%s):" % how, lab.js(MPANEL), "took", round(time.time() - t0, 1), "problems", lab.problems())
r = lab.js("const b = [...document.querySelectorAll('#meshPanel button')].find(b => __w.vis(b) && /^Save/.test(b.textContent)); if (!b) return 'no save button'; b.click(); await new Promise(r => setTimeout(r, 1500)); return window.__saved;")
out("   saved:", r, "problems", lab.problems())
save(lab, "once2-model-end.png")
# B. the status line through a loss at rest, read as the user would, and what idle() says in the middle of a draw
lab.click("#secQuality > summary")
out("B. at rest before:", brief(lab.check()))
out("   lost at rest:", lab.js(LOSE), brief(lab.check()))
save(lab, "once2-lost-rest.png")
out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()))
lab.click("#qFine"); time.sleep(0.25)
c = lab.check(); out("   Fine pressed, 0.25 s:", brief(c), "rIdle", c["rIdle"], "cIdle", c["cIdle"])
out("   lost mid-draw:", lab.js(LOSE))
for wait in (0.0, 1.5, 3.0):
    time.sleep(wait if wait == 0 else 1.5)
    c = lab.check(); out("   while lost:", brief(c), "rIdle", c["rIdle"], "cIdle", c["cIdle"])
out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats(), "problems", lab.problems())
save(lab, "once2-end.png")
lab.close()
