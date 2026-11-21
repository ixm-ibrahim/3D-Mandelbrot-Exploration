"""Count the separate pieces of the solid in the 2D slice pictures.

  python out/proto/sine/pieces.py [folder]

The 2D view paints the inside of the solid in one flat colour (the cut-face colour). That colour is read from
the middle of m2d-z000.png, which lies inside the main cardioid. A pixel counts as solid when it is within
TOL of it; pieces are 8-connected; pieces under 0.05 percent of the picture are ignored. The stage's own
buttons and sliders are blanked out first.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
folder = sys.argv[1] if len(sys.argv) > 1 else HERE
TOL = 30
NAMES = ["m2d-z000", "m2d-z010", "m2d-z025", "m2d-z050", "j-bas-2d-z000", "j-bas-2d-z020"]


def load(name):
    return np.asarray(Image.open(os.path.join(folder, name + ".png")).convert("RGB")).astype(int)


ref_img = load("m2d-z000")
h, w, _ = ref_img.shape
ref = ref_img[h // 2 - 3:h // 2 + 4, w // 2 - 3:w // 2 + 4].reshape(-1, 3).mean(axis=0)
print("picture %dx%d, inside colour %s" % (w, h, np.round(ref).astype(int).tolist()))
for name in NAMES:
    img = load(name)
    mask = np.abs(img - ref).max(axis=2) <= TOL
    mask[:75, :95] = False            # axes triad
    mask[60:660, w - 80:] = False     # zoom slider and its boxes
    mask[h - 65:, :365] = False       # hint
    mask[h - 50:, w - 195:] = False   # buttons
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    sizes = np.sort(ndimage.sum(mask, lab, range(1, n + 1)))[::-1] if n else np.array([])
    floor = 0.0005 * w * h
    big = sizes[sizes >= floor]
    total = mask.sum()
    if not len(big):
        print("%s: no solid pixels above the size floor (solid pixels in all: %d)" % (name, total))
        continue
    print("%s: %d piece(s) of at least %.0f px; sizes %s; solid is %.2f%% of the picture; largest piece holds %.2f%% of the solid (%d smaller specks ignored, %d px together)"
          % (name, len(big), floor, [int(s) for s in big[:8]], 100.0 * total / (w * h), 100.0 * big[0] / total, len(sizes) - len(big), int(sizes[len(big):].sum())))
