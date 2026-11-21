import sys, numpy as np
from PIL import Image
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(np.int32)
def obj(a):
    bg = a[5, a.shape[1] // 2]
    m = (np.abs(a - bg).sum(2) > 40)
    m[:, :60] = False; m[:, 730:] = False; m[:110, :] = False; m[640:, :] = False   # overlays (triad, zoom slider, bar, hint)
    return m
for i in (2, 5, 8, 14, 0):
    ref = load("d-%02d-s025.png" % i); mr = obj(ref)
    row = []
    for s in ("s120", "s080", "s050"):
        a = load("d-%02d-%s.png" % (i, s)); ma = obj(a)
        lost = (mr & ~ma).sum(); changed = (mr & ma & (np.abs(a - ref).sum(2) > 90)).sum()
        row.append("%s lost %.2f%% changed %.2f%%" % (s, 100 * lost / mr.sum(), 100 * changed / mr.sum()))
    a, b, c = load("d-%02d-s120.png" % i), load("d-%02d-s080.png" % i), load("d-%02d-s050.png" % i)
    print(i, "objpx", mr.sum(), "|", " | ".join(row), "| identical 1.2 vs 0.8:", int(np.abs(a - b).max()), "0.8 vs 0.5:", int(np.abs(b - c).max()))
