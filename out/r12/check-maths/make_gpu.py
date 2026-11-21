"""Checker of round 12: write and run the GPU steps.
  python out/r12/check-maths/make_gpu.py new     -> pictures of the joined page (the split against Version 11), the
                                                    shader harness, probes of each picture against MATH, tilt 90 from afar
  python out/r12/check-maths/make_gpu.py v11     -> the same six pictures on dist/v11.html, the first one twice
Run from the project root. One at a time."""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", "..", ".."))
which = sys.argv[1]
GO = "const L = window.squaringLab, S = L.S; const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); }; const idx = id => L.APPROACHES.findIndex(a => a.id === id);"
RAB = "[-0.1226, 0.7449, 0]"
VIEWS = [("m", "m", "[-1, 0, 0]"), ("bas", "j", "[-1, 0, 0]"), ("rab", "j", RAB)]
steps = [{"wait": "done", "timeout": 120}]

def state(js, name, shot=True):
    steps.append({"js": GO + js + " go(); return '" + name + ": approach ' + L.APPROACHES[S.approach].id + ' ' + JSON.stringify(S.param[L.APPROACHES[S.approach].id]) + ' mode ' + S.mode + ' c ' + S.c + ' n ' + S.n + ' iter ' + S.iter + ' failed ' + L.R.failed;"})
    steps.append({"wait": "done", "timeout": 150})
    if shot:
        steps.append({"shot": "out/r12/check-maths/%s-%s.png" % (which, name), "clip": "#stage"})

if which == "v11":
    for planes in (2, 1):
        for name, mode, c in VIEWS:
            state("S.approach = idx('mercator'); S.param.mercator.planes = %d; S.param.mercator.turn = 0; S.param.mercator.lift = 0; S.mode = '%s'; S.c = %s; S.n = 2;" % (planes, mode, c), "p%d-%s" % (planes, name))
    name, mode, c = VIEWS[0]
    state("S.approach = idx('mercator'); S.param.mercator.planes = 2; S.mode = '%s'; S.c = %s; S.n = 2;" % (mode, c), "p2-m-again")
    page = "v11.html"
else:
    for planes, ap in ((2, "fold"), (1, "mercator")):
        for name, mode, c in VIEWS:
            extra = "S.param.fold.planes = 2; S.param.fold.lift = 0;" if ap == "fold" else "S.param.mercator.turn = 0; S.param.mercator.lift = 0;"
            state("S.approach = idx('%s'); %s S.mode = '%s'; S.c = %s; S.n = 2;" % (ap, extra, mode, c), "p%d-%s" % (planes, name))
    name, mode, c = VIEWS[0]
    state("S.approach = idx('fold'); S.param.fold.planes = 2; S.mode = '%s'; S.c = %s; S.n = 2;" % (mode, c), "p2-m-again")
    # the shader code of each entry against MATH
    steps.append({"js": open(os.path.join(here, "harness.js"), encoding="utf-8").read()})
    # probes of the drawn surface against MATH
    probe = open(os.path.join(here, "probe.js"), encoding="utf-8").read()
    for ap, extra in (("mercator", ""), ("lathe", ""), ("fold", ""), ("tilt", ""), ("softfold", ""), ("axisbulb", ""), ("pillow", "S.param.pillow.layout = 0;"), ("pillow", "S.param.pillow.layout = 1;")):
        for mode in ("m", "j"):
            nm = "probe-%s%s-%s" % (ap, "-smooth" if "layout = 1" in extra else "", mode)
            state("S.approach = idx('%s'); %s S.mode = '%s'; S.c = [-1, 0, 0]; S.n = 2;" % (ap, extra, mode), nm, shot=False)
            steps.append({"js": probe})
    # the twisted square at tilt 90: the page's own button, then the tilt moved, seen from the button's distance
    steps.append({"js": GO + "S.param.pillow.layout = 0; L.showTwistedSquare(); return 'button: tilt ' + S.param.tilt.tilt + ' drawing radius ' + S.view.bound + ' iter ' + S.iter;"})
    steps.append({"wait": "done", "timeout": 150})
    steps.append({"shot": "out/r12/check-maths/new-tilt40.png", "clip": "#stage"})
    for t in (90, -90, 180):
        state("S.param.tilt.tilt = %d;" % t, "tilt%d" % t)
        steps.append({"js": probe})
    page = "r12-check-maths.html"

act = os.path.join(here, "gpu-%s.actions.json" % which)
with open(act, "w", encoding="utf-8") as f:
    json.dump(steps, f)
env = dict(os.environ, PYTHONIOENCODING="utf-8")
p = subprocess.run([sys.executable, os.path.join(root, "tools", "shot.py"), "--url", os.path.join(root, "dist", page), "--size", "1400x950", "--actions", act],
                   cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
with open(os.path.join(here, "gpu-%s.log" % which), "w", encoding="utf-8") as f:
    f.write(p.stdout + "\n--- stderr ---\n" + p.stderr + "\nexit code %d\n" % p.returncode)
print(p.stdout[-3000:]); print(p.stderr[-1500:]); print("exit code", p.returncode)
