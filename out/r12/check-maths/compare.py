"""Checker of round 12: the split against Version 11, pixel by pixel.  python out/r12/check-maths/compare.py"""
import os
import numpy as np
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
def load(n):
    return np.asarray(Image.open(os.path.join(here, n + ".png")).convert("RGB")).astype(np.int16)
def cmp(a, b, label):
    A, B = load(a), load(b)
    if A.shape != B.shape:
        print("%-52s SIZES DIFFER %s %s" % (label, A.shape, B.shape)); return
    d = np.abs(A - B).max(axis=2)
    bg = A[2, 2]
    solid = (np.abs(A - bg).max(axis=2) > 12).mean() * 100
    print("%-52s %dx%d  pixels that differ: %.4f %% (%d)  over 8 levels: %.4f %%  largest difference: %d of 255  picture is %.1f %% not background" % (
        label, A.shape[1], A.shape[0], (d > 0).mean() * 100, (d > 0).sum(), (d > 8).mean() * 100, d.max(), solid))
for planes, word in ((2, "two planes"), (1, "one plane")):
    for v, vw in (("m", "Mandelbrot solid"), ("bas", "Basilica"), ("rab", "rabbit")):
        cmp("new-p%d-%s" % (planes, v), "v11-p%d-%s" % (planes, v), "new entry, %s / v11 Planes %d: %s" % (word, planes, vw))
print("--- how much two drawings of the same thing differ (the first picture drawn again at the end of each run)")
cmp("v11-p2-m", "v11-p2-m-again", "v11 Planes 2 Mandelbrot, drawn twice")
cmp("new-p2-m", "new-p2-m-again", "new two planes Mandelbrot, drawn twice")
print("--- that the test can tell the two rules apart")
for v in ("m", "bas", "rab"):
    cmp("new-p2-%s" % v, "v11-p1-%s" % v, "new two planes / v11 Planes 1: %s" % v)
