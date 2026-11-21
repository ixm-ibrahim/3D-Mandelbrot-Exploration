"""Compare pictures pair by pair: python out/t9/kleinian/cmp.py <a.png> <b.png> [<a2> <b2> ...]
Prints size, share of pixels that differ by more than 8 and by more than 40 in any channel, mean absolute difference,
and over pixels that are saturated in both the median and 90th percentile hue difference in degrees."""
import sys, colorsys
import numpy as np
from PIL import Image
def hue(a):
    a = a.astype(float) / 255; mx = a.max(-1); mn = a.min(-1); d = mx - mn
    h = np.zeros(mx.shape); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = d > 0
    hr = ((g - b) / np.where(m, d, 1)) % 6; hg = (b - r) / np.where(m, d, 1) + 2; hb = (r - g) / np.where(m, d, 1) + 4
    h = np.where(mx == r, hr, np.where(mx == g, hg, hb)) * 60
    s = np.where(mx > 0, d / np.where(mx > 0, mx, 1), 0)
    return h, s, mx
def cmp(pa, pb):
    A = Image.open(pa).convert('RGB'); B = Image.open(pb).convert('RGB')
    note = ''
    if A.size != B.size:
        note = ' (sizes %s and %s, second scaled)' % (A.size, B.size); B = B.resize(A.size, Image.LANCZOS)
    a = np.asarray(A).astype(int); b = np.asarray(B).astype(int)
    d = np.abs(a - b).max(-1)
    ha, sa, va = hue(a); hb, sb, vb = hue(b)
    m = (sa > 0.35) & (sb > 0.35) & (va > 0.25) & (vb > 0.25)
    dh = np.abs(ha - hb); dh = np.minimum(dh, 360 - dh)
    med = float(np.median(dh[m])) if m.any() else -1; p90 = float(np.percentile(dh[m], 90)) if m.any() else -1
    big = float((dh[m] > 60).mean() * 100) if m.any() else -1
    print('%-34s %-34s >8: %5.1f%%  >40: %5.1f%%  mean %5.2f  hue median %5.1f p90 %5.1f  hue>60deg %4.1f%% of %d%s' % (pa.split('/')[-1], pb.split('/')[-1], (d > 8).mean() * 100, (d > 40).mean() * 100, np.abs(a - b).mean(), med, p90, big, int(m.sum()), note))
args = sys.argv[1:]
for i in range(0, len(args) - 1, 2): cmp(args[i], args[i + 1])
