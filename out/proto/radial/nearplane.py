"""How fast does the Mandelbrot solid change as the slice leaves the plane z = 0? (numpy copy of the rule, proto.py)
   python out/proto/radial/nearplane.py
Same test as the lab: start at 0, 14 steps of v -> F(v) + c, outside once |v| > 64."""
import numpy as np, proto
from scipy import ndimage
V = ('area', 1, 0)
W, H = 432, 352; vh = 3.2; cx = -0.6
xs = cx + (np.arange(W) + 0.5 - W / 2) * vh / H; ys = (H / 2 - np.arange(H) - 0.5) * vh / H
X, Y = np.meshgrid(xs, ys)
def inside(z, iters=14):
    c = np.stack([X.ravel(), Y.ravel(), np.full(X.size, float(z))], 1)
    v = c.copy(); alive = np.ones(len(c), bool)
    for k in range(iters - 1):
        idx = np.where(alive)[0]
        if not len(idx): break
        w = proto.F(v[idx], 2, V) + c[idx]
        v[idx] = w
        alive[idx[(w * w).sum(1) > 64.0 ** 2]] = False
    return alive.reshape(H, W)
base = inside(0.0)
print('z = 0: solid area %.3f square units' % (base.sum() * (vh / H) ** 2))
for z in [1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.25, 0.5]:
    m = inside(z); lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    sizes = np.sort(ndimage.sum(m, lab, range(1, n + 1)))[::-1] if n else np.array([0])
    print('z = %-7g area %.3f; of the flat set, %.0f%% is still solid at this height; %.0f%% of this slice lies outside the flat set; pieces over 0.05%% of the frame: %d, largest %.1f%% of the slice' % (
        z, m.sum() * (vh / H) ** 2, 100 * (m & base).sum() / base.sum(), 100 * (m & ~base).sum() / max(m.sum(), 1), (sizes >= 0.0005 * W * H).sum(), 100 * sizes[0] / max(m.sum(), 1)))
