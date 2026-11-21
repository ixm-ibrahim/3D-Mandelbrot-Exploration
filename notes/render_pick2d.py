"""Check that pick() in the 2D view names the point that is drawn there.

  python notes/render_pick2d.py dist/render-sh.html

Runs notes/render_pick2d.js (which needs a build whose boot file exposes pick, see out/render/90-boot-test.js), then
looks at the screenshot: where pick() says the point is inside the Mandelbrot set the picture must show the solid
interior colour, and where it says the point is at least three pixels outside (yet close enough to take 8 steps or more to
escape) the picture must show an outside colour.
"""
import json, os, re, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = subprocess.run([sys.executable, os.path.join(ROOT, "notes", "render_run.py"), sys.argv[1], "notes/render_pick2d.js"],
                     capture_output=True, text=True, cwd=ROOT).stdout
m = re.search(r'step 2 result: (".*")', out)
if not m:
    sys.exit("no result from the page:\n" + out)
data = json.loads(json.loads(m.group(1)))
im = Image.open(os.path.join(ROOT, "out", "render", "pick2d.png")).convert("RGB")
inside = im.getpixel((data["pts"][0][0], data["pts"][0][1]))  # placeholder, replaced below
# the interior colour: take it from a point that is certainly inside (c = -0.1, the main cardioid)
v2, w, h = data["v2"], data["w"], data["h"]
sx = w / 2 + (-0.1 - v2["x"]) * h / v2["h"]; sy = h / 2 - (0.0 - v2["y"]) * h / v2["h"]
inside = im.getpixel((round(sx) + 1, round(sy) + 1))
near = lambda a, b: max(abs(a[i] - b[i]) for i in range(3)) <= 14
ok = bad = skipped = 0
for x, y, n, d in data["pts"]:
    px = im.getpixel((x, y))
    if n >= 400: good = near(px, inside)
    elif n >= 8 and 3 <= d: good = not near(px, inside)
    else: skipped += 1; continue
    ok += good; bad += not good
    if not good: print("  disagrees at stage pixel (%d, %d): escape steps %d, %.1f pixels outside, picture colour %s" % (x, y, n, d, px))
print("centre of the stage picks", data["centre"], "expected", [v2["x"], v2["y"], data["cut"]])
print("top left corner picks", data["topLeft"], "expected", [v2["x"] - w / h * v2["h"] / 2, v2["y"] + v2["h"] / 2, data["cut"]])
print("interior colour", inside, "| grid points agreeing with the picture: %d of %d (%d far outside or within the soft edge skipped)" % (ok, ok + bad, skipped))
sys.exit(0 if bad <= 0.02 * (ok + bad) else 1)
