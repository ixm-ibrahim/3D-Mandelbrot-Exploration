"""How much of each preset does the ray march lose at the lab's default step share (0.8)?

The Kleinian distance estimate is exact only close to a pearl: at distance t from a pearl of radius rho it
returns t (1 + t / (2 rho)), so a ray that comes at a small pearl from far away can step into it or over it.
This script draws every preset twice, at the default step share and at a careful one (0.4, 600 steps), and
reports the share of the object's pixels that differ: `lost` (object in the careful picture, background in
the default one) and `changed` (object in both but a clearly different colour: a pearl drawn hollow).

    python notes/klein_stepcheck.py [stepshare] [page]     defaults: 0.8 and dist/klein-presets.html
The careful picture always comes from the baseline page; `page` is the one tested at the given step share.
"""
import json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klein_render import render, ROOT, HIDE_UI


def compare(a, b):
    A = np.asarray(Image.open(a).convert("RGB")).astype(int)
    B = np.asarray(Image.open(b).convert("RGB")).astype(int)
    bg = np.median(B[2:12, -40:-4].reshape(-1, 3), axis=0)
    objA = np.abs(A - bg).sum(2) > 40
    objB = np.abs(B - bg).sum(2) > 40
    n = max(1, int(objB.sum()))
    lost = (objB & ~objA).sum() / n
    changed = (objA & objB & (np.abs(A - B).sum(2) > 150)).sum() / n
    return float(lost), float(changed)


def stepcheck(items, tag, share=0.8, page="dist/klein-presets.html"):
    a = render(items, tag + "-a", sheet=False, extra_js=HIDE_UI + "L.S.q.stepk = %g; L.S.q.steps = 260; " % share, page=page)
    b = render(items, tag + "-b", sheet=False, extra_js=HIDE_UI + "L.S.q.stepk = 0.4; L.S.q.steps = 600; ")
    out = []
    for it, pa, pb in zip(items, a, b):
        lost, changed = compare(pa, pb)
        out.append((lost, changed))
        print("%-36s lost %5.1f%%   changed %5.1f%%" % (it["name"], 100 * lost, 100 * changed), flush=True)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    share = float(args[0]) if args else 0.8
    page = args[1] if len(args) > 1 else "dist/klein-presets.html"
    with open(os.path.join(ROOT, "data", "klein-presets.json"), encoding="utf-8") as f:
        presets = json.load(f)
    stepcheck(presets, "stepcheck" + ("-x" if len(args) > 1 else ""), share, page)
