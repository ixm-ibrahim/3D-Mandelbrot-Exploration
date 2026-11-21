"""Run page scripts (JavaScript files) in the lab through tools/shot.py.

  python notes/render_run.py dist/render.html notes/render_gaps.js [more.js ...] [--theme light] [--size 1400x950]

Each file is one step, or several if it contains lines that start with "//// ": such a line begins a new step and
may carry options for it, for example
  //// wait=done shot=out/render/name.png clip=#stage sleep=0.3 timeout=120
The step's script runs first, then the sleep, the wait and the screenshot. The value a script returns is printed.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
extra = []
while len(args) >= 2 and args[-2] in ("--theme", "--size"):
    extra = args[-2:] + extra
    args = args[:-2]
url, files = args[0], args[1:]
actions = []
for f in files:
    cur = None
    for line in open(os.path.join(ROOT, f), encoding="utf-8").read().split("\n"):
        if line.startswith("//// ") or cur is None:
            cur = {"js": ""}
            actions.append(cur)
            if line.startswith("//// "):
                for opt in line[5:].split():
                    k, _, v = opt.partition("=")
                    if k in ("wait", "shot", "clip"): cur[k] = v
                    elif k in ("sleep", "timeout"): cur[k] = float(v)
                continue
        cur["js"] += line + "\n"
for a in actions:
    if not a["js"].strip(): del a["js"]
os.makedirs(os.path.join(ROOT, "out", "render"), exist_ok=True)
tmp = os.path.join(ROOT, "out", "render", "_steps_%d.json" % os.getpid())
json.dump(actions, open(tmp, "w", encoding="utf-8"))
code = subprocess.call([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", url, "--actions", tmp] + extra, cwd=ROOT)
os.remove(tmp)
sys.exit(code)
