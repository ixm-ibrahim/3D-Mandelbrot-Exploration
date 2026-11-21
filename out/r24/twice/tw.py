"""Round 24, section "twice": the extra copy laid round an even number of times. Library of this section.

    import sys; sys.path.insert(0, 'out/r24/twice'); import tw
    r = tw.get('m4:-0.10')        rule by key (see get)
    n = tw.vox('m4:-0.10', 'basilica')      blocks (cached), how many steps each block centre stays, up to 120

Direction maps are written with the Mercator latitude mu = atanh(z / r) and the longitude lam; w = exp(mu + i lam).
My own form of the scout's map (written from the formula, not copied; compared with the scout's in check.py):
    north (mu >= 0), u = 1/w = exp(-mu - i lam), |u| <= 1:
        R = w^2 (1 + t u^m) / (1 + t w^m) = u^(m-2) (1 + t u^m) / (u^m + t)          (no overflow)
    south: the mirror image (R(1/conj w) = 1/conj R(w) for real t), so the map is computed for |mu| and z's sign put back.
    blend 'exp' (the scout's): for |mu| < mu1   W = w^2 ((1 + t u^m)/(1 + t w^m))^chi,  chi = S3(|mu| / mu1)
    blend 'tvar' (mine):       for |mu| < mu1   R with t replaced by t * S5(|mu| / mu1)     (no logarithm, no cut)
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)

Q4 = (0.282271, 0.530060, 0.0)                    # middle of the 1/4 bulb
Q25 = (-0.504340, 0.562766, 0.0)                  # middle of the 2/5 bulb (found in check.py: period 5, angle 2/5)
AIR = (-1.754878, 0.0, 0.0)
SETS = {'basilica': (-1.0, 0.0, 0.0), 'sanmarco': (-0.75, 0.0, 0.0), 'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 'q4': Q4, 'q25': Q25, 'airplane': AIR}
SETNAME = {'basilica': 'c = -1', 'sanmarco': 'c = -0.75', 'rabbit': 'rabbit', 'siegel': 'Siegel disc', 'q4': 'middle of the 1/4 bulb',
           'q25': 'middle of the 2/5 bulb', 'airplane': 'airplane, c = -1.7549'}
ORDER = ['basilica', 'sanmarco', 'rabbit', 'siegel', 'q4', 'q25', 'airplane']


def S3(q):
    q = np.clip(q, 0.0, 1.0); return q * q * (3 - 2 * q)


def S5(q):
    q = np.clip(q, 0.0, 1.0); return q * q * q * (10 - 15 * q + 6 * q * q)


def mulam(x, y, z):
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    return np.arctanh(np.clip(z / rs, -1 + 1e-15, 1 - 1e-15)), np.arctan2(y, x)


def _unit(N, D, sg):
    n2, d2 = np.abs(N) ** 2, np.abs(D) ** 2; tot = n2 + d2; tot = np.where(tot > 0, tot, 1.0)
    xy = 2 * N * np.conj(D) / tot
    return xy.real, xy.imag, sg * (n2 - d2) / tot


def mdir(x, y, z, m=4, t=-0.1, mu1=0.4, blend='exp'):
    """The extra copy laid (m - 2) times round. Unit vector out."""
    mu, lam = mulam(x, y, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    lam = np.where(z < 0, -lam, lam)                       # south = mirror image: conj in, conj out, z flipped
    u = np.exp(-np.minimum(am, 300.0) - 1j * lam)
    if blend == 'tvar':
        tt = t * S5(am / mu1); um = u ** m
        X, Y, Z = _unit(u ** (m - 2) * (1 + tt * um), um + tt, 1.0)
    else:
        um = u ** m
        N = u ** (m - 2) * (1 + t * um); D = um + t
        if blend == 'exp':
            inb = am < mu1
            if inb.any():
                ui = np.where(inb, u, 1.0); w = 1.0 / ui; chi = S3(am / mu1)
                W = w * w * np.exp(chi * (np.log(1 + t * ui ** m) - np.log(1 + t * w ** m)))
                N = np.where(inb, W, N); D = np.where(inb, 1.0 + 0j, D)
        X, Y, Z = _unit(N, D, 1.0)
    return X, np.where(z < 0, -Y, Y), sg * Z


def weld_dir(x, y, z, k=2, theta=np.pi, mua=0.15, muc=0.6, kind=5, mub=None):
    """Round 23's welded form carried to a copy laid k times round (k = 1 is round 23's own map when muc = MU60).
    E = exact doubling: Mercator latitude 2|mu|, longitude 2 lam                   (the one-plane rule)
    C = the copy's own map: Mercator latitude k (muc - |mu|), longitude theta - k lam   (lays the circle muc k times round the flat circle)
    G = (1 - chi) E + chi C made a unit vector, chi = S((|mu| - mua) / (mub - mua)).
    No fold needs chi = 2 / (2 + k) at |mu| = k muc / (2 + k), where E and C send a direction to the same latitude; mub is set from that."""
    S = S5 if kind == 5 else S3
    if mub is None:
        qs = np.linspace(0, 1, 200001); q0 = float(qs[np.argmin(np.abs(S(qs) - 2.0 / (2 + k)))])
        mub = mua + (k * muc / (2 + k) - mua) / q0
    mu, lam = mulam(x, y, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    chi = S((am - mua) / (mub - mua))
    a = np.minimum(2 * am, 60.0); b = np.clip(k * (muc - am), -60.0, 60.0)
    X = (1 - chi) * np.cos(2 * lam) / np.cosh(a) + chi * np.cos(theta - k * lam) / np.cosh(b)
    Y = (1 - chi) * np.sin(2 * lam) / np.cosh(a) + chi * np.sin(theta - k * lam) / np.cosh(b)
    Z = (1 - chi) * np.tanh(a) + chi * np.tanh(b)
    n = np.sqrt(X * X + Y * Y + Z * Z); n = np.where(n > 0, n, 1.0)
    return X / n, Y / n, sg * Z / n


def oneplane_dir(x, y, z):
    mu, lam = mulam(x, y, z); a = np.clip(2 * mu, -60, 60)
    return np.cos(2 * lam) / np.cosh(a), np.sin(2 * lam) / np.cosh(a), np.tanh(a)


def from_dir(G, name, label):
    def F(x, y, z):
        r2 = x * x + y * y + z * z; X, Y, Z = G(x, y, z); ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0)
    r = M.fixed(F, name, label); r.G = G
    return r


def dir_of(key):
    """The direction map of a key, or None for the bench rules."""
    p = key.split(':')
    if p[0] in ('oneplane', 'along', 'twoplane'):
        return None
    kw = {}
    for s in p[2:]:
        a, b = s.split('='); kw[a] = b if a == 'blend' else float(b)
    if p[0][0] == 'm':                                    # 'm4:-0.10', 'm4:-0.10:mu1=0.25', 'm6:-0.1:blend=tvar', 'm4:-0.1:blend=none'
        m = int(p[0][1:]); t = float(p[1]); mu1 = kw.get('mu1', 0.4); bl = kw.get('blend', 'exp')
        return lambda x, y, z: mdir(x, y, z, m, t, mu1, bl)
    if p[0][0] == 'w':                                    # 'w2:25' = welded, copy twice round at latitude 25; options mua=, th= (degrees), mub=
        k = int(p[0][1:]); muc = float(np.arctanh(np.sin(np.radians(float(p[1])))))
        th = np.radians(kw.get('th', 180.0)); mua = kw.get('mua', 0.15); mub = kw.get('mub', None)
        return lambda x, y, z: weld_dir(x, y, z, k, th, mua, muc, 5, mub)
    raise KeyError(key)


_made = {}


def get(key):
    if key not in _made:
        G = dir_of(key)
        _made[key] = M.bench(key) if G is None else from_dir(G, key, key)
    return _made[key]


# ---------------------------------------------------------------- blocks
H = 0.0125


def grid(sname):
    nx = 320 if sname == 'airplane' else 288
    xs = (np.arange(nx) + 0.5) * H - nx * H / 2; ys = (np.arange(224) + 0.5) * H - 224 * H / 2; zs = (np.arange(112) + 0.5) * H
    return xs, ys, zs


def vkey(key, sname):
    return os.path.join(CACHE, 'vox-%s-%s.npz' % (key.replace(':', '_').replace('=', ''), sname))


def vox(key, sname, steps=120, quiet=True, c=None, tag=None):
    """Upper half (z > 0) of the blocks; every rule here is its own mirror image in the flat plane (checked in check.py).
    Returns the number of steps each block centre stays (uint8, up to steps)."""
    path = vkey(key, tag or sname)
    if os.path.exists(path):
        return np.load(path)['n']
    r = get(key); c = c or SETS[sname]; xs, ys, zs = grid(sname); out = np.zeros((xs.size, ys.size, zs.size), np.uint8); t0 = time.time()
    for i0 in range(0, xs.size, 24):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 24], ys, zs, indexing='ij')
        out[i0:i0 + 24] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps)
    np.savez_compressed(path, n=out)
    if not quiet:
        print('vox %s %s %.0f s' % (key, sname, time.time() - t0)); sys.stdout.flush()
    return out


def full(n_half):
    return np.concatenate([n_half[:, :, ::-1], n_half], 2)


def render(ins, cam=(0.45, 0.5, 1.0), w=420, h=315, half_w=None):
    """A rough picture from the blocks (ins = full boolean block array, centred on 0): first inside block on each line of sight."""
    nx, ny, nz = ins.shape; half_w = half_w or (nx * H / 2 * 1.75 / 1.8)
    e1, e2, e3 = M.frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h)
    reach = 0.5 * H * np.sqrt(nx * nx + ny * ny + nz * nz); ds = np.arange(-reach, reach, H * 0.7)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf); off = np.array([nx, ny, nz]) * H / 2
    for k0 in range(0, ds.size, 24):
        dk = ds[k0:k0 + 24]; idx = []
        ok = np.ones((dk.size, h, w), bool)
        for i, n in enumerate((nx, ny, nz)):
            p = U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i]
            j = np.floor((p + off[i]) / H).astype(np.int32); ok &= (j >= 0) & (j < n); idx.append(np.clip(j, 0, n - 1))
        hit = ins[idx[0], idx[1], idx[2]] & ok
        depth = np.minimum(depth, np.where(hit.any(0), dk[np.argmax(hit, 0)], np.inf))
    return M.shade_solid(depth, us[1] - us[0])


EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}


def tile(key, sname, eye, steps, tag=None):
    """A cached picture tile (PNG) of the solid of key and sname, eye 'a' or 'top', after `steps` steps (30 or 120)."""
    from PIL import Image
    path = os.path.join(CACHE, 'tile-%s-%s-%s-%d.png' % (key.replace(':', '_').replace('=', ''), tag or sname, eye, steps))
    if not os.path.exists(path):
        n = full(vox(key, sname, tag=tag))
        Image.fromarray(render(n >= steps, EYES[eye])).save(path)
    return path
