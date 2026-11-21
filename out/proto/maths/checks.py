"""Claims 1-3 for the triangular pillow (radial layout). Referee's own checks."""
import numpy as np, json, os, sys
from scipy.spatial import ConvexHull
import pillow as P

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(12345)
S3 = np.sqrt(3.0)
NS = [n for n in range(-5, 9) if n != 0]
out = {}


def dist(a, b):
    return np.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


def lat2xy(a, b):
    return a - 0.5 * b, b * S3 / 2


def rot120(ux, uy, px, py, k):
    ang = k * 2 * np.pi / 3
    c, s = np.cos(ang), np.sin(ang)
    dx, dy = ux - px, uy - py
    return px + c * dx - s * dy, py + s * dx + c * dy


# ---------------- 1a: independence of the copy ----------------
N = 200000
x, y, z = P.rand_dirs(N, rng)
ux, uy = P.PhiInv(x, y, z)
gx, gy = ux.copy(), uy.copy()
for rep in range(4):            # compose 4 random symmetries
    kind = rng.integers(0, 2, N)
    a = rng.integers(-15, 16, N); b = rng.integers(-15, 16, N)
    # translation by a colour-A lattice vector: force a+b = 0 mod 3
    bt = b + ((-(a + b)) % 3)
    tx, ty = lat2xy(a, bt)
    px, py = lat2xy(a, b)       # any lattice point as a turning centre
    k = rng.choice([1, 2], N)
    rx, ry = rot120(gx, gy, px, py, k)
    gx = np.where(kind == 0, gx + tx, rx)
    gy = np.where(kind == 0, gy + ty, ry)
e0 = dist(P.Phi(gx, gy), (x, y, z)).max()
out['1a_Phi_invariant_under_symmetries_maxerr'] = float(e0)
d = {}
for n in NS:
    d[n] = float(dist(P.Phi(n * gx, n * gy), P.Phi(n * ux, n * uy)).max())
out['1a_copy_independence_maxerr_by_n'] = d
# control: a NON-symmetry (translation by a colour-B vector) must fail
tx, ty = lat2xy(1, 0)
out['1a_control_wrong_translation_n2'] = float(dist(P.Phi(2 * (ux + tx), 2 * (uy + ty)), P.Phi(2 * ux, 2 * uy)).max())
print('1a', out); sys.stdout.flush()


# ---------------- 1b: continuity ----------------
def circle(c, e1, e2, rad, M):
    t = (np.arange(M) + 0.0) * 2 * np.pi / M
    v = np.cos(rad) * c[:, None] + np.sin(rad) * (np.cos(t) * e1[:, None] + np.sin(t) * e2[:, None])
    return v[0], v[1], v[2]


def frame(c):
    c = c / np.linalg.norm(c)
    h = np.array([0.0, 0.0, 1.0]) if abs(c[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(h, c); e1 /= np.linalg.norm(e1)
    e2 = np.cross(c, e1)
    return c, e1, e2


def maxstep(n, c, rad, M):
    c, e1, e2 = frame(np.asarray(c, float))
    fx, fy, fz = P.dirmap(*circle(c, e1, e2, rad, M), n)
    st = np.sqrt((fx - np.roll(fx, 1)) ** 2 + (fy - np.roll(fy, 1)) ** 2 + (fz - np.roll(fz, 1)) ** 2)
    return st.max()


axes = [rng.normal(size=3) for _ in range(24)]
# special great circles: almost the equator, and through the corner meridians / poles, with tiny tilts
axes += [np.array([0, 0, 1.0]), np.array([1e-9, 0, 1.0]), np.array([1e-5, 2e-5, 1.0]),
         np.array([0, 1.0, 0]), np.array([1e-9, 1.0, 1e-9]),
         np.array([np.sin(2 * np.pi / 3), -np.cos(2 * np.pi / 3), 0]), np.array([np.sin(2 * np.pi / 3) + 1e-9, -np.cos(2 * np.pi / 3), 1e-9]),
         np.array([1.0, 0, 0]), np.array([1.0, 1e-9, 0])]
cont = {}
for n in NS:
    a = max(maxstep(n, ax, np.pi / 2, 20000) for ax in axes)
    b = max(maxstep(n, ax, np.pi / 2, 200000) for ax in axes)
    cont[n] = {'max_step_20k': float(a), 'max_step_200k': float(b), 'ratio': float(a / b),
               'lipschitz_est': float(b / (2 * np.pi / 200000))}
out['1b_great_circle_scans'] = cont
print('1b scans', cont); sys.stdout.flush()

# straddling the candidate seams directly
N = 400000
lon = rng.uniform(0, 2 * np.pi, N); eps = 1e-10
jump_eq = {}; jump_mer = {}; jump_special = {}
special = {'A': (1, 0, 0), 'B': (-0.5, S3 / 2, 0), 'C': (-0.5, -S3 / 2, 0), 'Npole': (0, 0, 1), 'Spole': (0, 0, -1),
           'mid60': (0.5, S3 / 2, 0), 'mid180': (-1, 0, 0), 'mid300': (0.5, -S3 / 2, 0)}
for n in NS:
    up = P.dirmap(np.cos(lon) * np.cos(eps), np.sin(lon) * np.cos(eps), np.full(N, np.sin(eps)), n)
    dn = P.dirmap(np.cos(lon) * np.cos(eps), np.sin(lon) * np.cos(eps), np.full(N, -np.sin(eps)), n)
    jump_eq[n] = float(dist(up, dn).max())
    lat = rng.uniform(-np.pi / 2, np.pi / 2, N); mj = 0.0
    for L0 in [0.0, 2 * np.pi / 3, 4 * np.pi / 3, np.pi / 3, np.pi, 5 * np.pi / 3]:
        p = P.dirmap(np.cos(L0 + eps) * np.cos(lat), np.sin(L0 + eps) * np.cos(lat), np.sin(lat), n)
        q = P.dirmap(np.cos(L0 - eps) * np.cos(lat), np.sin(L0 - eps) * np.cos(lat), np.sin(lat), n)
        mj = max(mj, float(dist(p, q).max()))
    jump_mer[n] = mj
    sp = {}
    for name, c in special.items():
        c0, e1, e2 = frame(np.array(c, float))
        f0 = P.dirmap(np.array([c0[0]]), np.array([c0[1]]), np.array([c0[2]]), n)
        vals = []
        for rad in [1e-3, 1e-6, 1e-9]:
            f = P.dirmap(*circle(c0, e1, e2, rad, 4096), n)
            vals.append(float(dist(f, f0).max()))
        sp[name] = vals
    jump_special[n] = sp
out['1b_jump_across_equator_eps1e-10'] = jump_eq
out['1b_jump_across_meridians_eps1e-10'] = jump_mer
out['1b_spread_of_image_of_small_circles_r=1e-3,1e-6,1e-9'] = {n: jump_special[n] for n in [2, 3, -1, -2, 8]}
out['1b_spread_small_circles_worst_over_all_n_r1e-9'] = float(max(v[2] for n in NS for v in jump_special[n].values()))
print('1b jumps', jump_eq, jump_mer); sys.stdout.flush()

# ---------------- 1c: the equator ----------------
ph = np.concatenate([rng.uniform(-np.pi, np.pi, 1000000), np.arange(-360, 361) * np.pi / 180])
eq = {}
for n in NS:
    f = P.dirmap(np.cos(ph), np.sin(ph), 0 * ph, n)
    eq[n] = float(dist(f, (np.cos(n * ph), np.sin(n * ph), 0 * ph)).max())
out['1c_equator_maxerr_by_n'] = eq
# full F with radius: compare with complex power on z=0
r = rng.uniform(0.05, 3, ph.size)
eqF = {}
for n in NS:
    f = P.F(r * np.cos(ph), r * np.sin(ph), 0 * ph, n)
    w = (r * np.exp(1j * ph)) ** n
    eqF[n] = float((dist(f, (w.real, w.imag, 0 * ph)) / np.abs(w)).max())
out['1c_F_vs_complex_power_relerr_by_n'] = eqF
print('1c', eq); sys.stdout.flush()

# ---------------- 2: degree ----------------
Np = 150000
i = np.arange(Np) + 0.5
zf = 1 - 2 * i / Np; rf = np.sqrt(1 - zf * zf); pf = i * np.pi * (3 - np.sqrt(5))
pts = np.stack([rf * np.cos(pf), rf * np.sin(pf), zf], 1)
# tiny irrational rotation so no vertex sits exactly on special sets
Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
pts = pts @ Q.T
hull = ConvexHull(pts)
tri = hull.simplices
a, b, c = pts[tri[:, 0]], pts[tri[:, 1]], pts[tri[:, 2]]
sgn = np.einsum('ij,ij->i', a, np.cross(b, c)) < 0
tri[sgn] = tri[sgn][:, [0, 2, 1]]
targets = np.stack(P.rand_dirs(40, rng), 1)
deg = {}
for n in NS:
    f = np.stack(P.dirmap(pts[:, 0], pts[:, 1], pts[:, 2], n), 1)
    A, B, C = f[tri[:, 0]], f[tri[:, 1]], f[tri[:, 2]]
    ori = np.einsum('ij,ij->i', A, np.cross(B, C))
    AB, BC, CA = np.cross(A, B), np.cross(B, C), np.cross(C, A)
    Ssum = A + B + C
    pos, neg = [], []
    for yv in targets:
        s1, s2, s3 = AB @ yv, BC @ yv, CA @ yv
        front = (Ssum @ yv) > 0
        pos.append(int((front & (s1 > 0) & (s2 > 0) & (s3 > 0)).sum()))
        neg.append(int((front & (s1 < 0) & (s2 < 0) & (s3 < 0)).sum()))
    deg[n] = {'preimage_counts_min_max': [min(pos), max(pos)], 'reversed_min_max': [min(neg), max(neg)], 'n_squared': n * n,
              'share_of_grid_triangles_with_reversed_image': float((ori < 0).mean())}
out['2_degree_by_n'] = deg
print('2 degree', deg); sys.stdout.flush()


# critical points of squaring: winding number of the image of a small circle about the image of its centre
def winding(n, centres, rad, M=256):
    res = np.zeros(len(centres))
    for k, c in enumerate(centres):
        c0, e1, e2 = frame(np.array(c, float))
        f0 = np.array(P.dirmap(np.array([c0[0]]), np.array([c0[1]]), np.array([c0[2]]), n)).ravel()
        f = np.array(P.dirmap(*circle(c0, e1, e2, rad, M), n))
        g0, g1, g2 = frame(f0)
        u = g1 @ f; v = g2 @ f
        ang = np.arctan2(v, u)
        dd = np.diff(np.concatenate([ang, ang[:1]]))
        dd = (dd + np.pi) % (2 * np.pi) - np.pi
        res[k] = dd.sum() / (2 * np.pi)
    return res


Ng = 12000
i = np.arange(Ng) + 0.5
zf = 1 - 2 * i / Ng; rf = np.sqrt(1 - zf * zf); pf = i * np.pi * (3 - np.sqrt(5))
grid = np.stack([rf * np.cos(pf), rf * np.sin(pf), zf], 1)
w = winding(2, grid, 0.06)
wr = np.rint(w)
odd = grid[wr != 1]
out['2_scan_grid_points'] = Ng
out['2_scan_winding_histogram'] = {str(int(k)): int((wr == k).sum()) for k in np.unique(wr)}
lonlat = [(float(np.degrees(np.arctan2(p[1], p[0])) % 360), float(np.degrees(np.arcsin(p[2])))) for p in odd]
# cluster the anomalous points
clusters = []
for p in odd:
    for cl in clusters:
        if np.linalg.norm(cl[0] - p) < 0.3:
            cl.append(p); break
    else:
        clusters.append([p])
cs = []
for cl in clusters:
    m = np.mean(cl, 0); m /= np.linalg.norm(m)
    cs.append({'count': len(cl), 'lon_deg': float(np.degrees(np.arctan2(m[1], m[0])) % 360), 'lat_deg': float(np.degrees(np.arcsin(m[2])))})
out['2_scan_clusters_where_not_one_to_one'] = cs
loc = {}
for name, c in special.items():
    loc[name] = [float(v) for v in winding(2, [c] * 3, 1.0, 4096)[:1]] if False else [float(winding(2, [c], r_, 4096)[0]) for r_ in (1e-2, 1e-4, 1e-6)]
out['2_local_winding_at_special_points_r=1e-2,1e-4,1e-6'] = loc
img = {}
for name, c in special.items():
    f = P.dirmap(np.array([float(c[0])]), np.array([float(c[1])]), np.array([float(c[2])]), 2)
    img[name] = [round(float(f[0][0]), 12), round(float(f[1][0]), 12), round(float(f[2][0]), 12)]
out['2_images_of_special_points_under_squaring'] = img
print('2 crit', out['2_scan_winding_histogram'], cs, loc, img); sys.stdout.flush()

# ---------------- 3: local behaviour at A and B ----------------
loc3 = {}
for name, Qc, Qimg in [('A', (1, 0, 0), (1, 0, 0)), ('B', (-0.5, S3 / 2, 0), (-0.5, -S3 / 2, 0))]:
    Qc = np.array(Qc, float); Qimg = np.array(Qimg, float)
    ez = np.array([0, 0, 1.0])
    ep = np.cross(ez, Qc); ep2 = np.cross(ez, Qimg)       # east tangent at each point
    rows = {}
    beta = rng.uniform(-np.pi, np.pi, 20000)
    for e in [0.3, 0.1, 1e-2, 1e-3, 1e-4, 1e-6]:
        d = np.cos(e) * Qc[:, None] + np.sin(e) * (np.cos(beta) * ep[:, None] + np.sin(beta) * ez[:, None])
        f = np.array(P.dirmap(d[0], d[1], d[2], 2))
        ang = np.arccos(np.clip(Qimg @ f, -1, 1))
        b2 = np.arctan2(ez @ f, ep2 @ f)
        db = (b2 - beta + np.pi) % (2 * np.pi) - np.pi
        rows[str(e)] = {'angle_ratio_min': float((ang / e).min()), 'angle_ratio_max': float((ang / e).max()),
                        'max_change_of_angle_around_deg': float(np.degrees(np.abs(db).max()))}
    loc3[name] = rows
out['3_local_behaviour_squaring'] = loc3
print('3', loc3); sys.stdout.flush()

# crease across the plane z=0 (first-order kink of the longitude of the image)
kink = {}
for lon0 in [20.0, 50.0, 100.0, 170.0]:
    L0 = np.radians(lon0); row = {}
    for h in [1e-2, 1e-3, 1e-4]:
        up = P.dirmap(np.array([np.cos(L0) * np.cos(h)]), np.array([np.sin(L0) * np.cos(h)]), np.array([np.sin(h)]), 2)
        dn = P.dirmap(np.array([np.cos(L0) * np.cos(h)]), np.array([np.sin(L0) * np.cos(h)]), np.array([-np.sin(h)]), 2)
        lu = (np.arctan2(up[1][0], up[0][0]) - 2 * L0 + np.pi) % (2 * np.pi) - np.pi
        ld = (np.arctan2(dn[1][0], dn[0][0]) - 2 * L0 + np.pi) % (2 * np.pi) - np.pi
        row[str(h)] = {'dlon_over_h_above': float(lu / h), 'dlon_over_h_below': float(ld / h),
                       'lat_image_over_h_above': float(np.arcsin(up[2][0]) / h), 'lat_image_over_h_below': float(np.arcsin(dn[2][0]) / h)}
    kink[str(lon0)] = row
out['extra_crease_across_z0'] = kink
print('crease', kink)
json.dump(out, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1, default=str)
print('DONE')
