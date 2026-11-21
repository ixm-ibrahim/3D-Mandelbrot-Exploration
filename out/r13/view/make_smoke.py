"""Copy tools/smoke-v12.json (unchanged steps) to out/r13/view/smoke.json, with only the picture paths moved to
out/r13/view/smoke/, so that a run on the view engineer's page does not overwrite round 12's pictures."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
with open(os.path.join(ROOT, "tools", "smoke-v12.json"), encoding="utf-8") as f:
    steps = json.load(f)
moved = 0
for s in steps:
    if "shot" in s:
        s["shot"] = "out/r13/view/smoke/" + os.path.basename(s["shot"]); moved += 1
with open(os.path.join(HERE, "smoke.json"), "w", encoding="utf-8") as f:
    json.dump(steps, f, ensure_ascii=False, indent=1)
print(len(steps), "steps,", moved, "picture paths moved")
