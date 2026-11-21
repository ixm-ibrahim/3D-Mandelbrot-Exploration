"""Claims 4, 5, 7 and follow-ups. Referee's own checks."""
import numpy as np, json, os, sys
from math import gcd
import pillow as P

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(777)
S3 = np.sqrt(3.0)
out = {}


def dist(a, b):
    return np.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


# ---- follow-up to claim 2: are there genuinely folded (orientation reversed) regions? tiny triangles
N = 3000000
c = np.stack(P.rand_dirs(N, rng))
e = 1e-6
t1 = np.cross(c.T, rng.normal(size=(N, 3))).T; t1 /= np.linalg.norm(t1, axis=0)
t2 = np.cross(c.T, t1.T).T
rev = {}
for n in [2, 3, 5, 8, -2]:
    a = np.stack(P.dirmap(*(c + e * t1), n)); b = np.stack(P.dirmap(*(c + e * t2), n)); o = np.stack(P.dirmap(*c, n))
    det = np.einsum('ij,ij->j', o, np.cross((a - o).T, (b - o).T).T)
    rev[n] = {'reversed_tiny_triangles': int((det <= 0).sum()), 'of': N,
              'area_stretch_min': float(det.min() / e ** 2), 'area_stretch_max': float(det.max() / e ** 2),
              'mean_area_stretch(=degree)': float(det.mean() / e ** 2)}
out['2_followup_tiny_triangle_orientation'] = rev
print(rev); sys.stdout.flush()

# ---- the half plane y=0, x<0: is F_2(v) = -|v| v there?  and the whole circle y=0 (altitude circle)
tau = rng.uniform(0, 2 * np.pi, 200000)
f = P.dirmap(np.cos(tau), 0 * tau, np.sin(tau), 2)
out['5_altitude_circle_y0_invariant_max_abs_y'] = float(np.abs(f[1]).max())
tau2 = np.mod(np.arctan2(f[2], f[0]), 2 * np.pi)
back = np.cos(tau) < 0
out['layout_defect_back_half_xz_plane_is_antipodal_maxerr'] = float(dist(f, (-np.cos(tau), 0 * tau, -np.sin(tau)))[back].max())
dev = (tau2 - 2 * tau + np.pi) % (2 * np.pi) - np.pi
out['5_altitude_circle_max_deviation_from_doubling_deg'] = float(np.degrees(np.abs(dev).max()))
# conjugacy to doubling through the flat coordinate t (u = t*(3/2, -sqrt3/2))
def tparam(x, z):
    ux, uy = P.PhiInv(x, 0 * x, z)
    t = np.sqrt(ux ** 2 + uy ** 2) / S3
    return np.where(z >= 0, t, 1 - t)
tt = tparam(np.cos(tau), np.sin(tau)); tt2 = tparam(f[0], f[2])
dd = (tt2 - 2 * tt + 0.5) % 1.0 - 0.5
out['5_altitude_circle_is_doubling_in_flat_parameter_maxerr'] = float(np.abs(dd).max())
print({k: v for k, v in out.items() if k[0] in '5l'}); sys.stdout.flush()

# ---- claim 5: which straight closed lines through corner A are simple circles on the pillow?
def simple_closed(a, b, K=60):
    lam = (a, b); ok = True
    for lamp in [(-b, a - b), (b - a, -a)]:          # lam turned 120 and 240 degrees (lattice coords)
        den = lam[0] * lamp[1] - lam[1] * lamp[0]
        A_, B_ = np.meshgrid(np.arange(-K, K + 1), np.arange(-K, K + 1))
        m = (A_ + B_) % 3 == 0
        A_, B_ = A_[m], B_[m]
        num = A_ * lamp[1] - B_ * lamp[0]
        if den < 0:
            num, den = -num, -den
        inside = (num >= 0) & (num < den)
        nn = num[inside]
        bad = ((nn * a) % den != 0) | ((nn * b) % den != 0)
        if bad.any():
            ok = False
    return ok
found = []; tested = 0
for a in range(-14, 15):
    for b in range(-14, 15):
        if (a, b) == (0, 0) or (a + b) % 3 != 0:
            continue
        g = gcd(abs(a), abs(b))
        # primitive in the colour-A lattice
        prim = True
        for d_ in range(2, g + 1):
            if g % d_ == 0 and ((a // d_) + (b // d_)) % 3 == 0:
                prim = False
        if not prim:
            continue
        tested += 1
        if simple_closed(a, b):
            x_, y_ = a - 0.5 * b, b * S3 / 2
            found.append({'lattice': [a, b], 'length': float(np.hypot(x_, y_)), 'angle_deg': float(np.degrees(np.arctan2(y_, x_)))})
out['5_directions_tested'] = tested
out['5_simple_closed_straight_circles_through_A'] = found
print('simple circles', tested, found); sys.stdout.flush()

# ---- claim 4: fractional n. turning by 120 degrees about B or C changes the answer, about A does not
N = 100000
rho = rng.uniform(0.01, 0.3, N); al = rng.uniform(0, 2 * np.pi, N)
frac = {}
for nfrac in [2.5, 1.5, 2.2]:
    row = {}
    for name, (px, py) in {'A': (0.0, 0.0), 'B': (1.0, 0.0), 'C': (0.5, -S3 / 2)}.items():
        ux, uy = px + rho * np.cos(al), py + rho * np.sin(al)
        c_, s_ = np.cos(2 * np.pi / 3), np.sin(2 * np.pi / 3)
        vx, vy = px + c_ * (ux - px) - s_ * (uy - py), py + s_ * (ux - px) + c_ * (uy - py)
        same_point = float(dist(P.Phi(ux, uy), P.Phi(vx, vy)).max())
        dif = dist(P.Phi(nfrac * ux, nfrac * uy), P.Phi(nfrac * vx, nfrac * vy))
        row[name] = {'same_direction_err': same_point, 'median_disagreement_after_power': float(np.median(dif)), 'max': float(dif.max())}
    frac[nfrac] = row
out['4_fractional_two_copies_of_same_direction'] = frac
# the rule exactly as defined (canonical copy), n = 2.5: equator exactness and jump across z=0, per arc
ph = np.radians(np.arange(0.5, 360, 1.0)); nf = 2.5; eps = 1e-9
f0 = P.dirmap(np.cos(ph), np.sin(ph), 0 * ph, nf)
phs = (ph + np.pi) % (2 * np.pi) - np.pi
err = dist(f0, (np.cos(nf * phs), np.sin(nf * phs), 0 * ph))
up = P.dirmap(np.cos(ph), np.sin(ph), 0 * ph + eps, nf); dn = P.dirmap(np.cos(ph), np.sin(ph), 0 * ph - eps, nf)
jump = dist(up, dn)
arcs = {'arc A-B (0..120)': (ph < 2 * np.pi / 3), 'arc B-C (120..240)': (ph > 2 * np.pi / 3) & (ph < 4 * np.pi / 3), 'arc C-A (240..360)': (ph > 4 * np.pi / 3)}
out['4_canonical_copy_n2.5'] = {k: {'max_equator_error_vs_principal_power': float(err[m].max()), 'max_jump_across_z0': float(jump[m].max()),
                                    'max_abs_z_of_image_of_equator': float(np.abs(f0[2][m]).max())} for k, m in arcs.items()}
print(frac, out['4_canonical_copy_n2.5']); sys.stdout.flush()


# ---- claim 5: square pillow, multiplied about the centre of a face
def sq_layout(p, q):                     # (p,q) in [-1/2,1/2]^2 -> direction with x >= 0
    ap, aq = np.abs(p), np.abs(q)
    s = np.clip(2 * np.maximum(ap, aq), 0, 1)
    ss = np.where(s > 1e-300, s, 1.0)
    bp, bq = p / ss, q / ss              # on the square boundary
    # perimeter angle: uniform along each edge, corners at 45 degrees
    beta = np.where(ap >= aq, np.where(p >= 0, (np.pi / 2) * bq, np.pi - (np.pi / 2) * bq),
                    np.where(q >= 0, np.pi / 2 - (np.pi / 2) * bp, -np.pi / 2 + (np.pi / 2) * bp))
    psi = (np.pi / 2) * s
    return np.cos(psi), np.sin(psi) * np.cos(beta), np.sin(psi) * np.sin(beta)


def sq_layout_inv(x, y, z):              # x >= 0
    psi = np.arctan2(np.hypot(y, z), x); s = psi / (np.pi / 2)
    beta = np.arctan2(z, y)
    k = np.floor((beta + np.pi / 4) / (np.pi / 2))        # -2..2 sector index
    loc = (beta - k * np.pi / 2) / (np.pi / 2)             # in [-1/2,1/2)
    k = np.mod(k, 4)
    bp = np.where(k == 0, 0.5, np.where(k == 1, -loc, np.where(k == 2, -0.5, loc)))
    bq = np.where(k == 0, loc, np.where(k == 1, 0.5, np.where(k == 2, -loc, -0.5)))
    return s * bp, s * bq


def sq_Phi(ux, uy):
    i = np.floor(ux); j = np.floor(uy)
    X = np.abs(np.mod(ux + 1, 2) - 1); Y = np.abs(np.mod(uy + 1, 2) - 1)   # fold into [0,1]
    back = np.mod(i + j, 2) == 1
    x, y, z = sq_layout(X - 0.5, Y - 0.5)
    return np.where(back, -x, x), y, z


def sq_PhiInv(x, y, z):
    p, q = sq_layout_inv(np.abs(x), y, z)
    return np.where(x >= 0, 0.5 + p, 1.5 - p), 0.5 + q


def sq_dir(x, y, z, n):
    ux, uy = sq_PhiInv(x, y, z)
    return sq_Phi(0.5 + n * (ux - 0.5), 0.5 + n * (uy - 0.5))


sq = {}
x, y, z = P.rand_dirs(200000, rng)
ux, uy = sq_PhiInv(x, y, z)
sq['roundtrip_maxerr'] = float(dist(sq_Phi(ux, uy), (x, y, z)).max())
# random symmetries of the square pillow: half turns about whole-number points, shifts by even vectors
gx, gy = ux.copy(), uy.copy()
for rep in range(3):
    kind = rng.integers(0, 2, x.size)
    a = rng.integers(-9, 10, x.size); b = rng.integers(-9, 10, x.size)
    gx = np.where(kind == 0, gx + 2 * a, 2 * a - gx)
    gy = np.where(kind == 0, gy + 2 * b, 2 * b - gy)
sq['Phi_invariant_maxerr'] = float(dist(sq_Phi(gx, gy), (x, y, z)).max())
for n in [3, 5, -3, 7, 2, 4]:
    row = {'copy_independence_maxerr': float(dist(sq_Phi(0.5 + n * (gx - 0.5), 0.5 + n * (gy - 0.5)), sq_Phi(0.5 + n * (ux - 0.5), 0.5 + n * (uy - 0.5))).max())}
    ph = rng.uniform(-np.pi, np.pi, 200000)
    f = sq_dir(np.cos(ph), np.sin(ph), 0 * ph, n)
    row['plane_z0_maxerr'] = float(dist(f, (np.cos(n * ph), np.sin(n * ph), 0 * ph)).max())
    f = sq_dir(np.cos(ph), 0 * ph, np.sin(ph), n)
    row['plane_y0_maxerr'] = float(dist(f, (np.cos(n * ph), 0 * ph, np.sin(n * ph))).max())
    # quarter-turn symmetry about the x axis
    f1 = sq_dir(x, -z, y, n); f2 = sq_dir(x, y, z, n)
    row['quarter_turn_symmetry_maxerr'] = float(dist(f1, (f2[0], -f2[2], f2[1])).max())
    # continuity: great circle scans at two resolutions
    ms = []
    for M in (20000, 200000):
        best = 0
        for ax in [rng.normal(size=3) for _ in range(12)] + [np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), np.array([1.0, 0, 0]), np.array([1.0, 1.0, 0]), np.array([0, 1.0, 1.0])]:
            ax = ax / np.linalg.norm(ax)
            h = np.array([0.3, 0.5, 0.8]); e1 = np.cross(ax, h); e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
            t = np.arange(M) * 2 * np.pi / M
            v = np.cos(t) * e1[:, None] + np.sin(t) * e2[:, None]
            fx, fy, fz = sq_dir(v[0], v[1], v[2], n)
            st = np.sqrt((fx - np.roll(fx, 1)) ** 2 + (fy - np.roll(fy, 1)) ** 2 + (fz - np.roll(fz, 1)) ** 2).max()
            best = max(best, st)
        ms.append(float(best))
    row['max_step_20k'] = ms[0]; row['max_step_200k'] = ms[1]; row['ratio'] = ms[0] / ms[1]
    # degree by mean area stretch of tiny triangles
    N2 = 1000000
    c2 = np.stack(P.rand_dirs(N2, rng)); t1 = np.cross(c2.T, rng.normal(size=(N2, 3))).T; t1 /= np.linalg.norm(t1, axis=0); t2 = np.cross(c2.T, t1.T).T
    a_ = np.stack(sq_dir(*(c2 + 1e-6 * t1), n)); b_ = np.stack(sq_dir(*(c2 + 1e-6 * t2), n)); o_ = np.stack(sq_dir(*c2, n))
    det = np.einsum('ij,ij->j', o_, np.cross((a_ - o_).T, (b_ - o_).T).T) / 1e-12
    row['mean_area_stretch(=degree if continuous)'] = float(np.median(det) if False else det[np.abs(det) < 1e4].mean())
    sq[n] = row
out['5_square_pillow_about_face_centre'] = sq
print('square', sq); sys.stdout.flush()

# ---- claim 7 side check: the smooth (angle-true) version of the pillow map is a classical rational map
w = rng.normal(size=2000) + 1j * rng.normal(size=2000)
Rt = lambda w: (2 * w ** 3 - 1) / (w * (2 - w ** 3))
RY = lambda Y: (Y ** 4 + 18 * Y ** 2 - 27) / (8 * Y ** 3)
Mob = lambda Y: (Y + 1j * S3) / (Y - 1j * S3)
MobInv = lambda w: 1j * S3 * (w + 1) / (w - 1)
om = np.exp(2j * np.pi / 3)
rat = {'conjugacy_check_maxerr': float(np.abs(Mob(RY(MobInv(w))) - Rt(w)).max() / 1.0),
       'R(1)': str(Rt(1 + 0j)), 'R(omega)-omega^2': float(abs(Rt(om) - om ** 2)), 'R(-1)': str(Rt(-1 + 0j)),
       'R(e^{i60})-omega': float(abs(Rt(np.exp(1j * np.pi / 3)) - om))}
# R - 1 has a triple root at -1 : numerator of R(w)-1 is -(w-1)(w+1)^3
num = np.poly1d([2, 0, 0, -1]) - np.poly1d([-1, 0, 0, 2, 0])
rat['roots_of_R(w)=1'] = [str(np.round(r, 6)) for r in num.roots]
th = np.linspace(0, 2 * np.pi, 20001)
img = Rt(np.exp(1j * th))
rat['unit_circle_invariant_max_abs_dev'] = float(np.abs(np.abs(img) - 1).max())
wob = np.degrees(np.angle(img * np.exp(-2j * th)))
rat['max_wobble_from_exact_doubling_deg'] = float(np.abs(wob).max())
# doubling formula check with the Weierstrass P' of the colour-A lattice (lattice sum)
lam1 = 1.5 - 1j * S3 / 2; lam2 = 1.5 + 1j * S3 / 2
K = 60
a_, b_ = np.meshgrid(np.arange(-K, K + 1), np.arange(-K, K + 1)); L = (a_ * lam1 + b_ * lam2).ravel()
pp = lambda u: -2 * np.sum(1.0 / (u - L) ** 3)
kB = pp(1.0 + 0j)          # value at corner B
us = [0.31 + 0.12j, -0.2 + 0.45j, 0.77 - 0.21j]
rat['wp_prime_doubling_relerr'] = [float(abs(pp(2 * u) / kB - RY(pp(u) / kB)) / abs(pp(2 * u) / kB)) for u in us]
rat['wp_prime_at_B_C_over_kB'] = [str(np.round(pp(1.0 + 0j) / kB, 6)), str(np.round(pp(0.5 - 1j * S3 / 2) / kB, 6))]
out['7_conformal_version_is_rational_map'] = rat
print('rational', rat)
json.dump(out, open(os.path.join(HERE, 'extra.json'), 'w'), indent=1, default=str)
print('DONE')
