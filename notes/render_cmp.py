"""Compare two sets of screenshots pixel by pixel.

  python notes/render_cmp.py out/render/base-smoke- out/render/new-smoke-

Prints, for every PNG whose name starts with the first prefix and has a partner under the second prefix: the mean
absolute difference per channel (0..255), the largest difference, and the share of pixels that differ by more than 12.
The display shader adds one level of random dither, so differences of 1 to 2 levels are expected everywhere.
"""
import glob, sys
import numpy as np
from PIL import Image

a_pre, b_pre = sys.argv[1], sys.argv[2]
for a in sorted(glob.glob(a_pre + "*.png")):
    b = b_pre + a[len(a_pre):]
    try:
        A = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
        B = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
    except FileNotFoundError:
        print("%-40s no partner" % a[len(a_pre):]); continue
    if A.shape != B.shape:
        print("%-40s sizes differ: %s vs %s" % (a[len(a_pre):], A.shape, B.shape)); continue
    d = np.abs(A - B).max(axis=2)
    print("%-40s mean %.3f  max %3d  pixels off by >12: %.3f%%" % (a[len(a_pre):], np.abs(A - B).mean(), d.max(), 100.0 * (d > 12).mean()))
