"""Judge (user lens): count the pieces of the solid in the flat-slice pictures, straight from the PNG pixels.
Solid = within TOL of the lab's inside colour; stage controls masked; 8-connected; pieces under 0.05% of the picture are specks."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

INSIDE = np.array([233, 223, 199]); TOL = 14
COLS = [("radial", "out/proto/radial/"), ("sine", "out/proto/sine/"), ("twoplane", "out/proto/twoplane/"),
        ("base-inflated", "out/proto/judge-user/base-inflated/"), ("base-folded", "out/proto/judge-user/base-folded/"),
        ("base-bulb", "out/proto/judge-user/base-bulb/")]
for kind in ["m2d-z000", "m2d-z010", "m2d-z025", "m2d-z050", "j-bas-2d-z000", "j-bas-2d-z020"]:
    print(kind)
    for name, d in COLS:
        a = np.asarray(Image.open(d + kind + ".png").convert("RGB")).astype(int)
        h, w = a.shape[:2]
        m = (np.abs(a - INSIDE).max(axis=2) <= TOL)
        m[:, 770:] = False; m[640:, :370] = False; m[645:, 660:] = False; m[:75, :95] = False
        lab, n = ndimage.label(m, structure=np.ones((3, 3)))
        sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1] if n else np.array([])
        floor = 0.0005 * w * h
        big = sizes[sizes >= floor]; tot = max(m.sum(), 1)
        print("  %-14s solid %6d px  pieces>=%d px: %d  largest %5.1f%%  next: %s  specks: %d (%.1f%%)" % (
            name, m.sum(), floor, len(big), 100 * (sizes[0] if len(sizes) else 0) / tot,
            ", ".join("%.1f%%" % (100 * s / tot) for s in big[1:5]) or "-", len(sizes) - len(big), 100 * sizes[len(big):].sum() / tot))
