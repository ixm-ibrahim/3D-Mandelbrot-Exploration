"""Compare the solid in the page's 2D view (negative power) with a plain complex escape grid."""
import sys, numpy as np
from PIL import Image
def ref(n, X, Y, iters=14, bail=64.0):
    c = X + 1j * Y; z = c.copy(); esc = np.zeros(c.shape, bool)
    with np.errstate(all='ignore'):
        for it in range(1, iters):          # z1 = c ... z_(iters-1)
            esc |= np.abs(z) > bail
            if it == iters - 1: break
            z = np.where(esc, z, z ** n + c)
    return esc
for n, path in ((-2, 'out/verify/maths/flat_n-2.png'), (-3, 'out/verify/maths/flat_n-3.png')):
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
    Hh, Ww = im.shape[:2]; W, H, h = 862, 701, 4.8
    off = ((Ww - W) // 2, (Hh - H) // 2)
    px = np.arange(W) + 0.5; py = np.arange(H) + 0.5
    X, Y = np.meshgrid((px - W / 2) / (H / 2) * h / 2, -(py - H / 2) / (H / 2) * h / 2)
    E = ref(n, X, Y)
    sub = im[off[1]:off[1] + H, off[0]:off[0] + W]
    # the solid colour: take it from the centre of the picture (c = 0 escapes)
    cc = sub[H // 2, W // 2]
    solid = (np.abs(sub - cc).sum(axis=2) < 40)
    win = np.zeros((H, W), bool); win[70:630, 110:760] = True     # keep clear of the overlays
    # ignore a 2-pixel rim around the reference boundary (anti-aliasing and the ink outline)
    from numpy.lib.stride_tricks import sliding_window_view
    pad = np.pad(E, 2, mode='edge'); sw = sliding_window_view(pad, (5, 5))
    core_in = sw.all(axis=(2, 3)); core_out = ~sw.any(axis=(2, 3))
    a = (core_in & win).sum(); b = (core_out & win).sum()
    miss = (core_in & win & ~solid).sum(); extra = (core_out & win & solid).sum()
    print(f"n={n}: solid colour {tuple(cc)}; reference escaping pixels well inside: {a}, drawn as solid: {a - miss} ({100*(a-miss)/max(a,1):.2f}%); reference non-escaping pixels well outside: {b}, wrongly drawn solid: {extra} ({100*extra/max(b,1):.3f}%)")
    print(f"   escaping share of the window: reference {100*(E & win).sum()/win.sum():.2f}%, page {100*(solid & win).sum()/win.sum():.2f}%")
