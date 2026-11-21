"""Check of own_family in carry.py: the middle ball's own family against the whole balls object."""
import numpy as np
from PIL import Image
import carry as C

rng = np.random.default_rng(5); n = 400000
q = rng.uniform(-1.4, 1.4, size=(3, n))
ins = C.tree_inside(q[0], q[1], q[2]); own = np.zeros(n, bool); own[ins] = C.own_family(q[0][ins], q[1][ins], q[2][ins])
mid = (q ** 2).sum(0) < C.RAD ** 2
print('points in the balls object: %d; in the middle ball: %d; in its own family beyond the ball: %d; in other families: %d'
      % (ins.sum(), (ins & mid).sum(), (own & ~mid).sum(), (ins & ~own).sum()))
print('middle-ball points not counted as own: %d' % (ins & mid & ~own).sum())
# on the flat plane nothing but the middle disc is its own
u, s = rng.uniform(-1.8, 1.8, 200000), rng.uniform(-1.3, 1.3, 200000); z0 = np.zeros_like(u)
fi = C.tree_inside(u, s, z0); fo = np.zeros(u.size, bool); fo[fi] = C.own_family(u[fi], s[fi], z0[fi])
print('flat plane: own-family points outside the middle disc: %d of %d inside points' % ((fo & (u * u + s * s > C.RAD ** 2)).sum(), fi.sum()))
# mirror tests of the family
m = q.copy(); m[2] *= -1; o2 = np.zeros(n, bool); i2 = C.tree_inside(*m); o2[i2] = C.own_family(m[0][i2], m[1][i2], m[2][i2])
m = q.copy(); m[0] *= -1; o3 = np.zeros(n, bool); i3 = C.tree_inside(*m); o3[i3] = C.own_family(m[0][i3], m[1][i3], m[2][i3])
print('own family, mirror above/below differs at %d, left/right at %d of %d' % ((own != o2).sum(), (own != o3).sum(), n))
# a picture: the upright cut through the x-axis and the cut across, own family light, other families grey
w, h = 700, 500; out = []
for kind in (0, 1):
    a, b = np.meshgrid(np.linspace(-1.75, 1.75, w), np.linspace(1.25, -1.25, h))
    P = (a, np.zeros_like(a), b) if kind == 0 else (np.zeros_like(a), a, b)
    i = C.tree_inside(*P); o = np.zeros(i.shape, bool); o[i] = C.own_family(P[0][i], P[1][i], P[2][i])
    img = np.zeros((h, w, 3), np.uint8); img[:] = (22, 28, 46); img[i] = (110, 114, 128); img[o] = (238, 228, 200); out.append(img)
Image.fromarray(np.hstack(out)).save('own-family.png'); print('wrote own-family.png')
