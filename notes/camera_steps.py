"""Turn a readable JavaScript test file into an actions list for tools/shot.py.

  python notes/camera_steps.py out/camera/tests.js out/camera/tests.json

The .js file is cut into steps at lines that start with "//# ". The rest of such a line is a list of
key=value options copied into the action ("wait=done", "shot=out/camera/x.png", "clip=#stage", "sleep=0.5").
Everything before the first "//# " line is a prelude pasted in front of every step, so helpers can be shared.
"""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as f:
    lines = f.read().split("\n")
prelude, steps, cur = [], [], None
for ln in lines:
    if ln.startswith("//# "):
        cur = {"opts": dict(kv.split("=", 1) for kv in ln[4:].split() if "=" in kv), "js": []}
        steps.append(cur)
    elif cur is None:
        prelude.append(ln)
    else:
        cur["js"].append(ln)
out = []
for s in steps:
    act = {"js": "\n".join(prelude + s["js"])}
    for k, v in s["opts"].items():
        act[k] = float(v) if k in ("sleep", "timeout") else v
    out.append(act)
with open(dst, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("wrote %s (%d steps)" % (dst, len(out)))
