"""Round 23, section "cone": direction maps for a homogeneous rule |v|^n * G(direction) + c, and the tools to test them.

A direction map is a function G(x, y, z) -> (X, Y, Z): unit vector in, unit vector out (any length in is accepted).

    import sys; sys.path.insert(0, 'out/r23/cone'); import conelib as L
    r = L.rule('weld0')            # a library rule (out/r21/lib/mem.py)
    L.numbers(L.DIRS['weld0'])     # covers, folded share, stretch on the cones, critical directions

Maps here:
    scout+ / scout-      the orchestrator's blended R_t (out/r23/me/cone.py)
    rt(t, phi, mu1)      R_t turned by phi about the upright axis, blended into w^2 beside the equator
    weld(theta, ...)     NOT R_t: w^2 beside the equator, the turn-over rho*e^(i theta)/w beside the 60-degree cone,
                         and the straight mix of the two unit vectors in between (see NOTES.md)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'me'))
import mem as M
import cone as C0

T15 = 2.0 - np.sqrt(3.0); RHO = 2.0 + np.sqrt(3.0); MU60 = float(np.log(RHO))      # tan 15, tan 75, Mercator latitude of 60 degrees


def smooth(q, kind=3):
    q = np.clip(q, 0.0, 1.0)
    return q * q * (3 - 2 * q) if kind == 3 else q * q * q * (10 - 15 * q + 6 * q * q)


def _mulam(x, y, z):
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    Zs = np.clip(z / rs, -1 + 1e-15, 1 - 1e-15)
    return np.arctanh(Zs), np.arctan2(y, x)


# ------------------------------------------------------------------ the welded map (step 3)
def weld_dir(x, y, z, theta=0.0, mua=0.0, mub=MU60, bend=1.0, kind=3, muc=MU60):
    """w^2 for |mu| <= mua; rho e^(i theta)/w for |mu| >= mub; between them the straight mix of the two unit vectors,
    made a unit vector again. chi = smooth(q^bend), q = (|mu| - mua)/(mub - mua). muc = Mercator latitude of the cone."""
    mu, lam = _mulam(x, y, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    q = np.clip((am - mua) / (mub - mua), 0.0, 1.0); chi = smooth(q ** bend, kind)
    a = np.minimum(2 * am, 60.0); b = np.clip(muc - am, -60.0, 60.0)
    se, te = 1 / np.cosh(a), np.tanh(a); sc, tc = 1 / np.cosh(b), np.tanh(b)
    X = (1 - chi) * se * np.cos(2 * lam) + chi * sc * np.cos(theta - lam)
    Y = (1 - chi) * se * np.sin(2 * lam) + chi * sc * np.sin(theta - lam)
    Z = (1 - chi) * te + chi * tc
    n = np.sqrt(X * X + Y * Y + Z * Z); n = np.where(n > 0, n, 1.0)
    return X / n, Y / n, sg * Z / n


# ------------------------------------------------------------------ R_t turned, with a choice of blend (step 2)
def rt_dir(x, y, z, t=T15, phi=0.0, mu1=0.4, blend='exp', top=None):
    """R_t turned by phi (radians) about the upright axis: G = Rot(2 phi) R_t Rot(-phi).
    blend 'exp': the scout's (the factor to the power chi). blend 'tvar': t itself grows from 0 at the equator.
    top = (mu2, mu3): above mu3 the exact turn-over rho/w, mixed in between mu2 and mu3 (unit vectors)."""
    co, si = np.cos(phi), np.sin(phi)
    xr, yr = co * x + si * y, co * y - si * x
    if blend == 'exp':
        X, Y, Z = C0.cone_dir(xr, yr, z, t, mu1, True)
    elif blend == 'none':
        X, Y, Z = C0.cone_dir(xr, yr, z, t, mu1, False)
    else:
        mu, lam = _mulam(xr, yr, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
        tt = t * smooth(am / mu1, 5)
        w = np.exp(np.minimum(am, 40.0) + 1j * lam)                      # northern copy, |w| >= 1
        w3 = w * w * w
        N = w * w * (1 + tt / w3); D = 1 + tt * w3
        n2, d2 = np.abs(N) ** 2, np.abs(D) ** 2; tot = n2 + d2
        xy = 2 * N * np.conj(D) / tot; X, Y, Z = xy.real, xy.imag, sg * (n2 - d2) / tot
    if top is not None:
        mu, lam = _mulam(xr, yr, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
        chi = smooth((am - top[0]) / (top[1] - top[0]), 5); b = np.clip(-np.log(abs(t)) - am, -60, 60)
        th = 0.0 if t > 0 else np.pi
        cx, cy, cz = np.cos(th - lam) / np.cosh(b), np.sin(th - lam) / np.cosh(b), sg * np.tanh(b)
        X, Y, Z = (1 - chi) * X + chi * cx, (1 - chi) * Y + chi * cy, (1 - chi) * Z + chi * cz
        n = np.sqrt(X * X + Y * Y + Z * Z); n = np.where(n > 0, n, 1.0); X, Y, Z = X / n, Y / n, Z / n
    c2, s2 = np.cos(2 * phi), np.sin(2 * phi)
    return c2 * X - s2 * Y, s2 * X + c2 * Y, Z


# ------------------------------------------------------------------ power 3 (step 4)
L31 = float(np.arccos(2.0 / 3.0)); L32 = float(np.arccos(1.0 / 3.0)); MU31 = float(np.arctanh(np.sin(L31))); MU32 = float(np.arctanh(np.sin(L32)))


def weld3_dir(x, y, z, th1=0.0, th2=0.0, kind=3):
    """Power 3: w^3 beside the equator; kappa1/w^2 beside the cone cos L = 2/3 (twice round, turned over);
    w/kappa2 beside the cone cos L = 1/3 (once round); straight mixes of unit vectors in between."""
    mu, lam = _mulam(x, y, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    a = np.minimum(3 * am, 60.0); b = np.clip(2 * (MU31 - am), -60, 60); d = np.clip(am - MU32, -60, 60)
    E = (np.cos(3 * lam) / np.cosh(a), np.sin(3 * lam) / np.cosh(a), np.tanh(a))
    C1 = (np.cos(th1 - 2 * lam) / np.cosh(b), np.sin(th1 - 2 * lam) / np.cosh(b), np.tanh(b))
    C2 = (np.cos(th2 + lam) / np.cosh(d), np.sin(th2 + lam) / np.cosh(d), np.tanh(d))
    chi1 = smooth(am / MU31, kind); chi2 = smooth((am - MU31) / (MU32 - MU31), kind)
    low = am < MU31
    out = []
    for i in range(3):
        out.append(np.where(low, (1 - chi1) * E[i] + chi1 * C1[i], (1 - chi2) * C1[i] + chi2 * C2[i]))
    n = np.sqrt(out[0] ** 2 + out[1] ** 2 + out[2] ** 2); n = np.where(n > 0, n, 1.0)
    return out[0] / n, out[1] / n, sg * out[2] / n


# ------------------------------------------------------------------ registry
DIRS = {
    'scout+': lambda x, y, z: C0.cone_dir(x, y, z, T15),
    'scout-': lambda x, y, z: C0.cone_dir(x, y, z, -T15),
}
LABELS = {'scout+': 'scout cone+ (R_t blended)', 'scout-': 'scout cone- (R_t blended)'}
POWER = {}


def add(key, fn, label, power=2):
    DIRS[key] = fn; LABELS[key] = label; POWER[key] = power


def rule(key):
    G = DIRS[key]; n = POWER.get(key, 2)

    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = G(x, y, z); s = r2 if n == 2 else r2 ** (n / 2.0)
        ok = r2 > 0
        return np.where(ok, s * X, 0.0), np.where(ok, s * Y, 0.0), np.where(ok, s * Z, 0.0)
    return M.fixed(F, key, LABELS.get(key, key))


# ------------------------------------------------------------------ numbers about a direction map
def numbers(G, n=900, cone_deg=60.0, quiet=False):
    """covers, folded share, the critical directions (where the map stops stretching) and where they are sent,
    and the stretches on the circle of latitude cone_deg."""
    lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lon = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi
    LA, LO = np.meshgrid(lat, lon, indexing='ij'); h = 1e-5

    def GG(la, lo):
        return np.stack(G(np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)), -1)
    g = GG(LA, LO); a = (GG(LA + h, LO) - GG(LA - h, LO)) / (2 * h); b = (GG(LA, LO + h) - GG(LA, LO - h)) / (2 * h) / np.cos(LA)[..., None]
    det = (np.cross(a, b) * g).sum(-1); dA = np.cos(LA) * (np.pi / n) * (np.pi / n)
    aa, bb, ab = (a * a).sum(-1), (b * b).sum(-1), (a * b).sum(-1)
    tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0)); s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 0))
    sgn = -1.0                                                           # with (lat, lon) in this order an angle-true map has det < 0
    out = {'covers': float((sgn * det * dA).sum() / (4 * np.pi)), 'covers_unsigned': float((np.abs(det) * dA).sum() / (4 * np.pi)),
           'folded_share': float((dA * (sgn * det < 0)).sum() / dA.sum()), 'finite': bool(np.isfinite(g).all())}
    # worst squeeze (ratio of the two stretches) by share of directions
    ratio = s1 / np.maximum(s2, 1e-12); wts = dA / dA.sum()
    out['share_ratio_over_2'] = float(wts[ratio > 2].sum()); out['share_ratio_over_4'] = float(wts[ratio > 4].sum())
    # critical directions: local minima of the larger stretch, northern hemisphere
    crit = []
    nh = np.nonzero(lat > np.radians(2.0))[0]; S = s1[nh]
    loc = (S <= np.roll(S, 1, 1)) & (S <= np.roll(S, -1, 1)); loc[1:-1] &= (S[1:-1] <= S[:-2]) & (S[1:-1] <= S[2:]); loc[0] = loc[-1] = False
    ii, jj = np.nonzero(loc & (S < 0.12))
    for i, j in zip(ii, jj):
        gi = g[nh[i], j]
        crit.append((float(np.degrees(lat[nh[i]])), float(np.degrees(lon[j])), float(np.degrees(np.arcsin(np.clip(gi[2], -1, 1)))), float(np.degrees(np.arctan2(gi[1], gi[0]))), float(S[i, j])))
    out['critical (lat, lon -> lat, lon, stretch)'] = crit
    # the cone
    i = int(np.argmin(np.abs(np.degrees(lat) - cone_deg)))
    out['cone'] = {'lat': float(np.degrees(lat[i])), 'image_lat_min_max': (float(np.degrees(np.arcsin(g[i, :, 2])).min()), float(np.degrees(np.arcsin(g[i, :, 2])).max())),
                   'stretch_large': (float(s1[i].min()), float(s1[i].max())), 'stretch_small': (float(s2[i].min()), float(s2[i].max()))}
    i0 = int(np.argmin(np.abs(lat)))
    out['equator'] = {'stretch_large': (float(s1[i0].min()), float(s1[i0].max())), 'stretch_small': (float(s2[i0].min()), float(s2[i0].max()))}
    if not quiet:
        for k, v in out.items():
            print('   ', k, ':', v)
    return out, (lat, lon, g, s1, s2, sgn * det)


def lift_test(r, steps=80, n=6000, eps=1e-6, seed=7):
    """Flat-inside points lifted by eps off the flat plane: how many are lost?"""
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); out = {}
    for nm, c in (('basilica', (-1.0, 0.0)), ('sanmarco', (-0.75, 0.0)), ('rabbit', M.RABBIT[:2]), ('siegel', M.SIEGEL[:2])):
        ins = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300
        # keep points well inside: also stay when moved a little in the plane
        st = M.stay(r, zr[ins], zi[ins], np.full(ins.sum(), eps), c[0], c[1], 0.0, steps) >= steps
        out[nm] = '%d lost of %d' % (int((~st).sum()), int(ins.sum()))
    return out


SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('c = -0.75', (-0.75, 0.0, 0.0)), ('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL)]


def cut_plane(r, c, e1, e2, w, h, steps, half=1.8, origin=(0.0, 0.0, 0.0)):
    """A cut along the plane through origin spanned by the unit vectors e1 (to the right) and e2 (up)."""
    u, s = np.meshgrid(np.linspace(-half, half, w), np.linspace(half * h / w, -half * h / w, h))
    P = [origin[i] + u * e1[i] + s * e2[i] for i in range(3)]
    return M.stay(r, P[0], P[1], P[2], c[0], c[1], c[2], steps)


def lonv(deg):
    a = np.radians(deg); return (float(np.cos(a)), float(np.sin(a)), 0.0)


CUTS = [('flat', (1, 0, 0), (0, 1, 0)), ('upright through x', (1, 0, 0), (0, 0, 1)), ('upright through y', (0, 1, 0), (0, 0, 1)),
        ('upright, 60 deg from x', lonv(60), (0, 0, 1)), ('tilted 30 about x', (1, 0, 0), (0, float(np.cos(np.radians(30))), 0.5))]


def cut_sheet(keys, path, sets=None, cuts=None, w=250, h=190, steps=50, rules=None, split=True):
    sets = sets or SETS; cuts = cuts or CUTS; pad = 6; f = M.font(14); t0 = time.time()
    rules = rules or [rule(k) for k in keys]
    if split and len(sets) > 1:                                           # one file per set, so that each can be looked at
        for sn, c in sets:
            tag = sn.replace(' ', '').replace('=', '').replace('.', '')
            cut_sheet(keys, path.replace('.png', '-%s.png' % tag), [(sn, c)], cuts, w, h, steps, rules, False)
        return
    W = pad + len(sets) * len(cuts) * (w + pad); H = 8 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    for i, r in enumerate(rules):
        y = 26 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(sets):
            for k, (cn, e1, e2) in enumerate(cuts):
                x = pad + (j * len(cuts) + k) * (w + pad)
                im.paste(Image.fromarray(M.shade(cut_plane(r, c, e1, e2, w, h, steps), steps)), (x, y)); d.text((x + 3, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(11))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); print('wrote', path, im.size)


def report(key, flat_n=12000):
    G = DIRS[key]; r = rule(key); print('\n==', key, '|', LABELS.get(key, ''))
    out, _ = numbers(G)
    rng = np.random.default_rng(2); p = rng.normal(size=(3, 4000)) * rng.uniform(1e-6, 2, 4000)
    X, Y, Z, _ = r.step(p[0], p[1], p[2], (), 0, 0, 0, 0); print('    finite on a random batch:', bool(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(Z).all()))
    print('    flat check:', M.flat_check(r, n=flat_n, steps=60)); print('    lift test:', lift_test(r)); sys.stdout.flush()
    return out
