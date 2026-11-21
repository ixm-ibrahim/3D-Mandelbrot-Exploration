"""Checker of round 12: close-ups of the twisted square's Mandelbrot solid (tilt 40) at 14, 60 and 250 iterations,
at one place where the numbers say the edge is rough (height angle 50, round 250) and one where they say it is smooth
(height angle 50, round 100); then the jump test (check4.js).  python out/r12/check-maths/make_skin.py"""
import json, math, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", "..", ".."))
GO = "const L = window.squaringLab, S = L.S; const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };"
steps = [{"wait": "done", "timeout": 120}, {"js": GO + "L.showTwistedSquare(); return 'tilt ' + S.param.tilt.tilt;"}, {"wait": "done", "timeout": 150}]
places = {"rough-50-250": (50, 250, 1.018), "smooth-50-100": (50, 100, 0.683), "rough-35-300": (35, 300, 0.796)}
for name, (el, az, r) in places.items():
    a, b = math.radians(el), math.radians(az)
    d = [math.cos(a) * math.cos(b), math.cos(a) * math.sin(b), math.sin(a)]
    tgt = [-0.1 + r * d[0], r * d[1], r * d[2]]
    for it in (14, 60, 250):
        steps.append({"js": GO + "S.iter = %d; L.cam.yaw = %r; L.cam.pitch = %r; L.cam.dist = 0.45; L.cam.target = %s; go(); return '%s iter ' + S.iter + ' cam ' + JSON.stringify(L.cam);" % (it, b, a, json.dumps(tgt), name)})
        steps.append({"wait": "done", "timeout": 240})
        steps.append({"shot": "out/r12/check-maths/skin-%s-iter%d.png" % (name, it), "clip": "#stage"})
steps.append({"js": open(os.path.join(here, "check4.js"), encoding="utf-8").read()})
act = os.path.join(here, "skin.actions.json")
json.dump(steps, open(act, "w", encoding="utf-8"))
env = dict(os.environ, PYTHONIOENCODING="utf-8")
p = subprocess.run([sys.executable, os.path.join(root, "tools", "shot.py"), "--url", os.path.join(root, "dist", "r12-check-maths.html"), "--size", "1400x950", "--actions", act],
                   cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
open(os.path.join(here, "skin.log"), "w", encoding="utf-8").write(p.stdout + "\n--- stderr ---\n" + p.stderr + "\nexit code %d\n" % p.returncode)
print(p.stdout[-1500:]); print(p.stderr[-800:]); print("exit code", p.returncode)
