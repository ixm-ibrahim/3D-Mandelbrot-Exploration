"""Run page scripts kept in plain .js files through tools/shot.py (saves hand-escaping them into JSON).

  python notes/measure_steps.py dist/measure.html [--size 1400x1300] [--theme light] step.js[@shot.png[@clip]] ...

Each step runs its script, waits until the scorecard has settled, then takes its screenshot. (It does not wait
for the 3D picture: these tests are about the figures and the card below it.)
The page must be built with out/measure/boot-test.js in the 90-boot.js slot (it exposes window.squaringLab.T).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READY = "window.squaringLab && window.squaringLab.T.cardIdle()"

args, flags, steps = sys.argv[1:], [], []
url = args.pop(0)
while args:
    a = args.pop(0)
    if a in ("--size", "--theme"):
        flags += [a, args.pop(0)]
    else:
        steps.append(a)
actions = [{"wait": READY, "timeout": 90}]
for s in steps:
    parts = s.split("@")
    with open(os.path.join(ROOT, parts[0]), encoding="utf-8") as f:
        act = {"js": f.read(), "wait": READY, "timeout": 120}
    if len(parts) > 1:
        act["shot"] = parts[1]
    if len(parts) > 2:
        act["clip"] = parts[2]
    actions.append(act)
path = os.path.join(ROOT, "out", "measure", "_steps.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(actions, f)
# The scorecard's sentences hold characters (ⁿ, ×, −) that a Windows console code page cannot print.
env = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", url, "--actions", path] + flags, env=env))
