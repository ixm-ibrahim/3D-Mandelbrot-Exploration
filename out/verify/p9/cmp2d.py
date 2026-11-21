import numpy as np, sys, json
from PIL import Image
APS = ['mercator', 'lathe', 'bulb', 'split', 'classic']
NS = [2, 3, 5, 8]
SC = [('m', None), ('j', (-1, 0)), ('j', (-0.122561, 0.744862))]
def win(mode, n):
    if mode == 'm': return (-0.5, 0, 3.2) if n == 2 else (0, 0, 3.0)
    return (0, 0, 3.6)
def ref(X, Y, n, mode, c, its=14):
    P = X + 1j * Y
    if mode == 'm': z = np.zeros_like(P); C = P
    else: z = P.copy(); C = complex(*c)
    alive = np.ones(P.shape, bool)
    for k in range(its + 1):
        esc = np.abs(z) > 64
        alive &= ~esc
        if k == its: break
        z = np.where(alive, z, 0)
        z = z ** n + C
    return alive
def dil(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out
rows = []
for a in APS:
    for n in NS:
        for si, (mode, c) in enumerate(SC):
            im = np.asarray(Image.open('out/verify/p9/f_%s_n%d_s%d.png' % (a, n, si)).convert('RGB')).astype(int)
            H, W, _ = im.shape
            cx, cy, h = win(mode, n)
            xs = cx + h * ((np.arange(W) + 0.5) - W / 2) / H
            ys = cy + h * (H / 2 - (np.arange(H) + 0.5)) / H
            X, Y = np.meshgrid(xs, ys)
            R = ref(X, Y, n, mode, c)
            bg = im[2, 2]
            dbg = np.abs(im - bg).sum(2)
            # solid colour: the most common colour among the pixels far from bg
            far = im[dbg > 40]
            if len(far) == 0:
                rows.append((a, n, si, W, H, 'EMPTY', R.mean())); continue
            vals, cnt = np.unique(far.reshape(-1, 3), axis=0, return_counts=True)
            solid = vals[cnt.argmax()]
            dso = np.abs(im - solid).sum(2)
            isS = dso < 20; isB = dbg < 20; edge = ~(isS | isB)
            raw = ((isS & ~R) | (isB & R))
            # an edge band of 2 px around the reference outline
            band = dil(R, 2) & dil(~R, 2)
            off = raw & ~band
            # also treat edge-class pixels far from the band as wrong
            stray = edge & ~band
            rows.append((a, n, si, W, H, 'bg=%s solid=%s' % (tuple(bg), tuple(solid)), round(100 * R.mean(), 2), round(100 * isS.mean(), 2), round(100 * edge.mean(), 3), round(100 * raw.mean(), 4), round(100 * off.mean(), 4), round(100 * stray.mean(), 4), round(100 * band.mean(), 3)))
print('approach n scene W H colours ref_in% drawn_solid% edgeclass% raw_disagree% beyond2px% strayedge% band%')
for r in rows: print(*r)
