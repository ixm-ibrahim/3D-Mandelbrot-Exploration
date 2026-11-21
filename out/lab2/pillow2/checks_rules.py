"""(rules only, cut from checks.py) lab2 / pillow2 numeric checks (numpy, double precision).
   python out/lab2/pillow2/checks.py            -> prints, and writes out/lab2/pillow2/checks.json
Rules compared, all at power 2:
  merc1   Sphere inversions, one plane (the 'inflated' rule M)
  merc2   Sphere inversions, two planes (folded; c is folded too, as the app's cmap does)
  radial  the maths check's pillow, simplest layout (out/proto/maths/pillow.py)
  both    the same with the both-planes-exact slide (out/proto/maths/twoplane_patch.py) = approach 'pillowboth'
  smooth  the angle-true pillow w -> (2w^3 - 1)/(w(2 - w^3)) = approach 'pillowsmooth'
"""
import json, os, sys
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'proto', 'maths'))
import pillow as P                      # noqa: E402
F0, I0 = P.layout_fwd, P.layout_inv
import twoplane_patch as TP             # noqa: E402  (replaces P.layout_fwd / P.layout_inv)
F1, I1 = TP.fwd, TP.inv
OUT = {}
np.seterr(all='ignore')


def say(key, text, val=None):
    print(text)
    OUT[key] = val if val is not None else text


# ---------------- the rules (direction maps and squares) ----------------
def R(w):
    return (2 * w ** 3 - 1) / (w * (2 - w ** 3))


def smooth_dir(x, y, z):
    s = 1 + np.abs(z)
    w = (x + 1j * y) / s
    w3 = w ** 3
    N = 2 * w3 - 1
    D = w * (2 - w3)
    nn, dd = np.abs(N) ** 2, np.abs(D) ** 2
    q = nn + dd
    Pp = N * np.conj(D)
    Z = np.where(z > 0, dd - nn, nn - dd) / q
    Z = np.where(z == 0, 0.0, Z)
    return 2 * Pp.real / q, 2 * Pp.imag / q, Z


def sq_smooth(x, y, z):
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2)
    rs = np.where(r > 0, r, 1.0)
    dx, dy, dz = smooth_dir(x / rs, y / rs, z / rs)
    return r2 * dx, r2 * dy, r2 * dz


def sq_merc1(x, y, z):
    r2 = x * x + y * y + z * z
    k = r2 / np.maximum(r2 + z * z, 1e-300)
    return k * (x * x - y * y), k * 2 * x * y, k * 2 * np.sqrt(r2) * z


def fold2(x, y, z):
    rho = np.hypot(y, z)
    psi = np.arctan2(z, y)
    s = np.where(psi < 0, -1.0, 1.0)
    a = np.abs(psi)
    a2 = np.where(a < np.pi / 4, a, np.where(a < np.pi / 2, np.pi / 2 - a, np.where(a < 3 * np.pi / 4, 1.5 * np.pi - a, a))) * s
    return x, rho * np.cos(a2), rho * np.sin(a2)


def sq_merc2(x, y, z):
    return sq_merc1(*fold2(x, y, z))


def sq_radial(x, y, z):
    P.layout_fwd, P.layout_inv = F0, I0
    return P.F(x, y, z, 2)


def sq_both(x, y, z):
    P.layout_fwd, P.layout_inv = F1, I1
    return P.F(x, y, z, 2)


RULES = {'merc1': sq_merc1, 'merc2': sq_merc2, 'radial': sq_radial, 'both': sq_both, 'smooth': sq_smooth}
ITER, BAIL = 14, 64.0   # replaced below by the lab's own bailout if given on the command line
if len(sys.argv) > 1:
    BAIL = float(sys.argv[1])


def inside(rule, x, y, z, c=None, iters=ITER):
    """True where the orbit has not escaped after iters steps. c None: Mandelbrot (c = the point)."""
    sq = RULES[rule]
    if c is None:
        cx, cy, cz = x, y, z
    else:
        cx, cy, cz = [np.full(x.shape, float(t)) for t in c]
    if rule == 'merc2':
        cx, cy, cz = fold2(cx, cy, cz)
    vx, vy, vz = (x.copy(), y.copy(), z.copy()) if c is not None else (np.zeros_like(x), np.zeros_like(x), np.zeros_like(x))
    alive = np.ones(x.shape, bool)
    for _ in range(iters):
        vx, vy, vz = sq(vx, vy, vz)
        vx, vy, vz = vx + cx, vy + cy, vz + cz
        r2 = vx * vx + vy * vy + vz * vz
        esc = ~(r2 <= BAIL * BAIL)
        alive &= ~esc
        vx = np.where(alive, vx, 0.0); vy = np.where(alive, vy, 0.0); vz = np.where(alive, vz, 0.0)
    return alive


def pieces(mask, floor):
    lab, n = ndimage.label(mask, structure=np.ones((3,) * mask.ndim))
    if n == 0:
        return dict(solid=0, pieces=0, largest=0.0, next=[], specks=0, speck_share=0.0)
    sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    tot = int(mask.sum())
    big = sizes[sizes >= floor]
    return dict(solid=tot, pieces=int(len(big)), largest=round(100.0 * sizes[0] / tot, 2),
                next=[round(100.0 * s / tot, 2) for s in big[1:4]], specks=int(len(sizes) - len(big)),
                speck_share=round(100.0 * sizes[len(big):].sum() / tot, 2))


