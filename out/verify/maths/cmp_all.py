import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view
def ref(n, X, Y, iters=14, bail=64.0):
    c = X + 1j * Y; esc = np.zeros(c.shape, bool)
    with np.errstate(all='ignore'):
        if n < 0:
            z = c.copy()
            for it in range(1, iters):
                esc |= np.abs(z) > bail
                if it == iters - 1: break
                z = np.where(esc, z, z ** n + c)
            return esc            # the solid is the escaping region
        z = np.zeros_like(c)
        for it in range(iters):
            z = np.where(esc, z, z ** n + c); esc |= np.abs(z) > bail
        return ~esc
for ap in ['mercator', 'lathe', 'bulb', 'split', 'classic']:
    for n, (cx, h) in ((2, (-0.5, 3.2)), (-2, (0, 4.8))):
        im = np.asarray(Image.open(f'out/verify/maths/flat_{ap}_n{n}.png').convert('RGB')).astype(int)
        Hh, Ww = im.shape[:2]; W, H = 862, 701; ox, oy = (Ww - W) // 2, (Hh - H) // 2
        px = np.arange(W) + 0.5; py = np.arange(H) + 0.5
        X, Y = np.meshgrid(cx + (px - W / 2) / (H / 2) * h / 2, -(py - H / 2) / (H / 2) * h / 2)
        S = ref(n, X, Y); sub = im[oy:oy + H, ox:ox + W]
        solid = np.abs(sub - np.array([233, 223, 199])).sum(axis=2) < 40
        win = np.zeros((H, W), bool); win[70:630, 110:760] = True
        sw = sliding_window_view(np.pad(S, 2, mode='edge'), (5, 5)); ci = sw.all(axis=(2, 3)) & win; co = ~sw.any(axis=(2, 3)) & win
        print(f"{ap:9s} n={n:2d}: reference solid pixels (2 px inside the edge) {ci.sum():6d}, drawn solid {100*(ci & solid).sum()/max(ci.sum(),1):6.2f}%; reference empty pixels {co.sum():6d}, drawn solid {100*(co & solid).sum()/max(co.sum(),1):6.3f}%")
