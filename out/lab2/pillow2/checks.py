"""lab2 / pillow2 numeric checks (numpy, double precision).
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


# ---------------- A. the closed form is the pillow ----------------
print('== A. the angle-true map is the pillow')
om = np.exp(2j * np.pi / 3)
say('A_corners', 'corners: |R(1) - 1| = %.1e, |R(w) - w^2| = %.1e, |R(w^2) - w| = %.1e   (A fixed, B and C swapped)' % (
    abs(R(1 + 0j) - 1), abs(R(om) - om ** 2), abs(R(om ** 2) - om)))
rng = np.random.default_rng(1)
cnt, worst = [], 0.0
for _ in range(2000):
    W = np.tan(rng.uniform(-1.5, 1.5)) * np.exp(1j * rng.uniform(0, 2 * np.pi))
    roots = np.roots([W, 2, 0, -2 * W, -1])           # W w^4 + 2 w^3 - 2 W w - 1 = 0
    sep = min(abs(roots[i] - roots[j]) for i in range(4) for j in range(i))
    cnt.append(len(roots) if sep > 1e-9 else -1)
    worst = max(worst, max(abs(R(roots) - W) / (1 + abs(W))))
say('A_degree', 'degree: 2000 random targets, every one has %s distinct preimages (worst |R(root) - target| %.1e)' % (sorted(set(cnt)), worst))
crit = np.roots([2, 0, 0, 4, 0, 0, 2])                   # R' has numerator 2 (w^3 + 1)^2
say('A_branch', 'branch directions: R\'(w) = 2 (w^3 + 1)^2 / (w (2 - w^3))^2; its zeros are at longitude %s degrees with |w| = %s (each a double zero: three sheets meet), images at longitude %s degrees' % (
    sorted(set(int(round(np.degrees(np.angle(c)) % 360)) for c in crit)), sorted(set(round(abs(c), 6) for c in crit)),
    [int(round(np.degrees(np.angle(R(np.exp(1j * np.radians(a))))) % 360)) for a in (60, 180, 300)]))
h = 1e-6
say('A_multiplier', 'multiplier at A: R\'(1) = %.6f (= 2^3: doubling seen through a 120 degree cone point); poles: R(0) = inf, R(inf) = 0 (the two face centres swap)' % ((R(1 + h) - R(1 - h)) / (2 * h)).real)
# local degree 3 at w = -1
say('A_local3', 'at w = -1: R(w) - 1 = (w - 1)(w + 1)^3 / (w (2 - w^3)); |R(-1 + e) - 1| / e^3 = %.4f, %.4f for e = 1e-2, 1e-3 (limit 2/3)' % (
    abs(R(-1 + 1e-2) - 1) / 1e-6, abs(R(-1 + 1e-3) - 1) / 1e-9))
# direct proof: R o Phi = Phi o (times 2), Phi = Moebius of the Weierstrass P' function of the triangular lattice
Nl = 220
ii, jj = np.meshgrid(np.arange(-Nl, Nl + 1), np.arange(-Nl, Nl + 1))
lat = (ii + jj * np.exp(1j * np.pi / 3)).ravel()
lat = lat[np.abs(lat) <= Nl * 0.86]                       # a round window keeps the sum symmetric


def wpp(u):
    return -2 * np.sum((u - lat) ** -3)


cen = (1 + np.exp(1j * np.pi / 3)) / 3                     # a triangle's centre: an order-3 point
p = wpp(cen)


def phi(u, a, b):
    beta = (a + b - 2) * p / (b - a)
    alpha = (a - 1) * p + a * beta
    t = wpp(u)
    return (t + alpha) / (t + beta)


def chordal(a, b):
    return 2 * abs(a - b) / np.sqrt((1 + abs(a) ** 2) * (1 + abs(b) ** 2))


best = None
for a, b in ((om, om ** 2), (om ** 2, om)):
    errs = []
    for _ in range(300):
        u = rng.uniform(-0.5, 0.5) + rng.uniform(-0.5, 0.5) * 1j
        errs.append(chordal(R(phi(u, a, b)), phi(2 * u, a, b)))
    circ = max(abs(abs(phi(t * np.exp(1j * np.pi / 6), a, b)) - 1) for t in rng.uniform(0.05, 0.5, 50))      # a triangle edge, A to B
    alt = max(abs(phi(t + 0j, a, b).imag) / (1 + abs(phi(t + 0j, a, b)) ** 2) for t in rng.uniform(0.05, 0.95, 50))   # the altitude through A
    if best is None or max(errs) < best[0]:
        best = (max(errs), circ, alt)
say('A_lattes', 'pillow test: with Phi = Moebius(P\'(u)) on the triangular lattice (P\' by lattice sum, %d points), max chordal |R(Phi(u)) - Phi(2u)| over 300 random u = %.1e; a triangle edge (u = t e^(i 30 deg)) lands on |w| = 1 to %.1e and the altitude through A (u real) on the real axis to %.1e. So R is exactly "double the flat sheet", seen through an angle-true wrapping.' % (len(lat), best[0], best[1], best[2]))

# ---------------- B. how far the angle-true z = 0 map is from doubling ----------------
print('== B. the angle-true map on z = 0')
t = np.linspace(0, 2 * np.pi, 720001)
ang = np.unwrap(np.angle(R(np.exp(1j * t))))
wob = np.degrees(ang - 2 * t)
speed = np.gradient(ang, t)
closed = np.degrees(2 * np.arctan2(np.sin(3 * t), 2 - np.cos(3 * t)))
say('B_wobble', 'equator: |R| - 1 max %.1e (the plane is kept); image angle = 2 t + 2 atan2(sin 3t, 2 - cos 3t) (closed form, max difference %.1e deg); wobble max %.3f deg at t = %.2f deg, rms %.2f deg; angular speed from %.4f to %.4f (exact doubling: 2 everywhere)' % (
    np.max(np.abs(np.abs(R(np.exp(1j * t))) - 1)), np.max(np.abs(wob - closed)), np.max(np.abs(wob)), np.degrees(t[np.argmax(wob)]), np.sqrt(np.mean(wob ** 2)), speed.min(), speed.max()))
# mean area stretch of the direction map (degree check on the sphere) and its spread
v = rng.normal(size=(3, 400000)); v /= np.linalg.norm(v, axis=0)
e = 1e-6
a1 = np.cross(v.T, np.array([0.3, -0.5, 0.8])); a1 /= np.linalg.norm(a1, axis=1)[:, None]
a2 = np.cross(v.T, a1)
f0 = np.array(smooth_dir(*v))
f1 = np.array(smooth_dir(*(v + e * a1.T) / np.linalg.norm(v + e * a1.T, axis=0)))
f2 = np.array(smooth_dir(*(v + e * a2.T) / np.linalg.norm(v + e * a2.T, axis=0)))
s1 = np.linalg.norm(f1 - f0, axis=0) / e; s2 = np.linalg.norm(f2 - f0, axis=0) / e
say('B_stretch', 'direction map on the sphere: mean area stretch %.3f (degree 4); conformal check, stretch ratio in two perpendicular directions: median %.4f, 99th percentile %.4f (ideal 1); linear stretch 5th / 50th / 95th percentile %.2f / %.2f / %.2f, exp(mean log) %.3f' % (
    np.mean(s1 * s2), np.median(np.maximum(s1, s2) / np.minimum(s1, s2)), np.percentile(np.maximum(s1, s2) / np.minimum(s1, s2), 99),
    *np.percentile(s1, [5, 50, 95]), np.exp(np.mean(np.log(s1)))))

# ---------------- C. slices on the pictures' own grids ----------------
print('== C. slices (bailout %.0f, %d steps, 8-connected, pieces under 0.05%% of the picture are specks)' % (BAIL, ITER))
W_, H_ = 864, 703
def grid(cx, cy, h):
    xs = cx + (np.arange(W_) + 0.5 - W_ / 2) * h / H_
    ys = cy - (np.arange(H_) + 0.5 - H_ / 2) * h / H_
    return np.meshgrid(xs, ys)
floor = 0.0005 * W_ * H_
comp = {}
flatM = flatJ = None
for rule in ('merc1', 'merc2', 'radial', 'both', 'smooth'):
    comp[rule] = {}
    X, Y = grid(-0.6, 0.0, 3.2)
    for zc in (0.0, 0.02, 0.1, 0.25, 0.5):
        m = inside(rule, X, Y, np.full(X.shape, zc))
        d = pieces(m, floor); d['area'] = round(float(m.sum()) * (3.2 / H_) ** 2, 4)
        if rule == 'merc1' and zc == 0.0: flatM = m
        if zc == 0.0: d['differs_from_flat_px'] = int((m ^ flatM).sum()); d['differs_share_of_flat'] = round(100.0 * (m ^ flatM).sum() / flatM.sum(), 2)
        else: d['flat_set_still_solid'] = round(100.0 * (m & flatM).sum() / flatM.sum(), 1)
        comp[rule]['m z=%.2f' % zc] = d
    X, Y = grid(0.0, 0.0, 3.0)
    for zc in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4):
        m = inside(rule, X, Y, np.full(X.shape, zc), c=(-1, 0, 0))
        d = pieces(m, floor); d['area'] = round(float(m.sum()) * (3.0 / H_) ** 2, 4)
        if rule == 'merc1' and zc == 0.0: flatJ = m
        if zc == 0.0: d['differs_from_flat_px'] = int((m ^ flatJ).sum()); d['differs_share_of_flat'] = round(100.0 * (m ^ flatJ).sum() / flatJ.sum(), 2)
        else: d['flat_set_still_solid'] = round(100.0 * (m & flatJ).sum() / flatJ.sum(), 1)
        comp[rule]['bas z=%.2f' % zc] = d
    for k, d in comp[rule].items():
        print('  %-7s %-11s area %6.3f  pieces %d  largest %6.2f%%  next %s  specks %d (%.2f%%)  %s' % (
            rule, k, d['area'], d['pieces'], d['largest'], d['next'], d['specks'], d['speck_share'],
            ('differs from the flat set in %d px = %.2f%% of it' % (d['differs_from_flat_px'], d['differs_share_of_flat'])) if 'differs_from_flat_px' in d
            else 'flat set still solid: %.1f%%' % d['flat_set_still_solid']))
OUT['C_slices'] = comp

# ---------------- D. the solids: thickness, bodies or lump ----------------
print('== D. solids on a 3D grid')
N3 = int(sys.argv[2]) if len(sys.argv) > 2 else 120
OUTNAME = 'checks.json' if N3 else 'checks-fast.json'
sol = {}
for name, c, box in ((('basilica', (-1, 0, 0), 1.9), ('mandelbrot', None, None)) if N3 else ()):
    for rule in ('merc1', 'merc2', 'radial', 'both', 'smooth'):
        if c is None:
            xs = np.linspace(-2.2, 1.0, N3); ys = np.linspace(-1.6, 1.6, N3); zs = np.linspace(-1.6, 1.6, N3)
        else:
            xs = np.linspace(-box, box, N3); ys = np.linspace(-box, box, N3); zs = np.linspace(-box, box, N3)
        m = np.zeros((N3, N3, N3), bool)
        for i, xv in enumerate(xs):                       # one y-z sheet at a time
            Yg, Zg = np.meshgrid(ys, zs, indexing='ij')
            m[i] = inside(rule, np.full(Yg.shape, xv), Yg, Zg, c=c)
        dv = (xs[1] - xs[0]) * (ys[1] - ys[0]) * (zs[1] - zs[0])
        da = (ys[1] - ys[0]) * (zs[1] - zs[0])
        ix, iy, iz = np.where(m)
        pc = pieces(m, 8)
        prof = m.reshape(N3, -1).sum(axis=1) * da          # cross-section area A(x)
        d = dict(volume=round(float(m.sum() * dv), 4), x=[round(float(xs[ix.min()]), 3), round(float(xs[ix.max()]), 3)],
                 y_half=round(float(np.abs(ys[iy]).max()), 3), z_half=round(float(np.abs(zs[iz]).max()), 3),
                 pieces_3d=pc['pieces'], largest_3d=pc['largest'], next_3d=pc['next'])
        if c is not None:
            def A(x0): return round(float(prof[np.argmin(np.abs(xs - x0))]), 4)
            d['area_at_x'] = {('%+.3f' % x0): A(x0) for x0 in (-1.3, -1.0, -0.8, -0.618, -0.4, 0.0, 0.4, 0.618, 0.8, 1.0, 1.3)}
            d['pinch_ratio_left'] = round(A(-0.618) / max(A(0.0), 1e-9), 3)     # 0 for bodies that touch at a point
            d['pinch_ratio_right'] = round(A(0.618) / max(A(0.0), 1e-9), 3)
            # the in-plane width against the off-plane height of the cross-section through the centre
            j0 = np.argmin(np.abs(xs - 0.0)); sl = m[j0]
            d['centre_section_y_half'] = round(float(np.abs(ys[np.where(sl)[0]]).max()), 3) if sl.any() else 0
            d['centre_section_z_half'] = round(float(np.abs(zs[np.where(sl)[1]]).max()), 3) if sl.any() else 0
        sol['%s %s' % (name, rule)] = d
        print('  %-10s %-7s %s' % (name, rule, json.dumps(d)))
OUT['D_solids'] = sol
json.dump(OUT, open(os.path.join(HERE, OUTNAME), 'w', encoding='utf-8'), indent=1)
print('wrote', OUTNAME)
