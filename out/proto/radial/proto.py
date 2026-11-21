"""Numpy prototype of the pillow rule with the radial layout, to compare profile variants quickly.
   python out/proto/radial/proto.py
Variants: prof = 'lin' (polar angle linear in s) | 'area' (equal area: z = 1 - s^2)
          rnd  = 0 (triangular level sets) | 1 (Moebius rounding of the level sets near the centre)
          lon  = 0 (longitude = edge position) | p > 0 (longitude blends to the true angle near the centre, B = sigma^p)
"""
import numpy as np, sys
PI = np.pi; T3 = 2 * PI / 3; R3 = np.sqrt(3.0)

def lon_fwd(w, B):          # w in [-1,1] along the edge -> longitude offset from the sector middle, in [-pi/3, pi/3]
    k = R3 * (1 - B)
    small = k < 1e-4
    ks = np.where(small, 1.0, k)
    return np.where(small, w, np.arctan(ks * w) / np.arctan(ks)) * (PI / 3)
def lon_inv(h, B):
    k = R3 * (1 - B)
    small = k < 1e-4
    ks = np.where(small, 1.0, k)
    return np.where(small, h / (PI / 3), np.tan(h / (PI / 3) * np.arctan(ks)) / ks)

def layout(l, V):
    prof, rnd, lon = V
    mn = l.min(axis=1); e = 3 * mn; s = 1 - e
    k = np.argmin(l, axis=1)                       # which weight is smallest: 2 -> edge AB, 0 -> BC, 1 -> CA
    sec = (k + 1) % 3
    nxt = np.take_along_axis(l, ((sec + 1) % 3)[:, None], 1)[:, 0]   # weight of the corner the edge runs toward
    ss = np.maximum(s, 1e-300)
    t = np.clip((nxt - mn) / ss, 0, 1)
    w = 2 * t - 1
    lam = np.sqrt(1 + 3 * w * w)
    ec = e / (1 + s * (lam - 1)) if rnd else e      # 1 - sigma
    if prof == 'lin': z = np.sin(PI / 2 * ec)
    else: z = ec * (2 - ec)
    rho = np.sqrt(np.maximum(0, 1 - z * z))
    if lon: tau = T3 * (sec + 0.5) + lon_fwd(w, (1 - ec) ** lon)
    else: tau = T3 * (sec + t)
    return np.stack([rho * np.cos(tau), rho * np.sin(tau), z], 1)

def layout_inv(d, V):
    prof, rnd, lon = V
    z = np.clip(np.abs(d[:, 2]), 0, 1)
    if prof == 'lin': ec = np.arcsin(z) * 2 / PI
    else: ec = z / (1 + np.sqrt(1 - z))
    tau = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * PI) / T3
    sec = np.minimum(np.floor(tau), 2).astype(int); t = tau - sec
    if lon:
        w = lon_inv((t - 0.5) * T3, (1 - ec) ** lon); t = np.clip((w + 1) / 2, 0, 1)
    w = 2 * t - 1
    lam = np.sqrt(1 + 3 * w * w)
    e = lam * ec / (1 + ec * (lam - 1)) if rnd else ec
    l = np.zeros((len(z), 3))
    idx = np.arange(len(z))
    l[idx, sec] = 1 - t; l[idx, (sec + 1) % 3] = t
    return e[:, None] / 3 + (1 - e)[:, None] * l

def F(v, n, V):
    r = np.linalg.norm(v, axis=1); d = v / r[:, None]
    l = layout_inv(d, V)
    up = d[:, 2] >= 0
    x = np.where(up[:, None], l, np.stack([l[:, 0] + l[:, 2], l[:, 1] + l[:, 2], -l[:, 2]], 1))
    x = np.stack([n * x[:, 0] - (n - 1), n * x[:, 1], n * x[:, 2]], 1)
    i = np.floor(x); f = x - i
    inv = f.sum(axis=1) > 1.5
    k = np.mod(i[:, 1] - i[:, 2], 3).astype(int)
    g = np.where(inv[:, None], 1 - f[:, [0, 2, 1]], f)        # weights for colours k, k+1, k+2
    g = g / g.sum(axis=1)[:, None]
    l2 = np.zeros_like(g); idx = np.arange(len(k))
    for j in range(3): l2[idx, (k + j) % 3] = g[:, j]
    o = layout(l2, V)
    o[:, 2] *= np.where(inv, -1, 1)
    return o * (r ** n)[:, None]

def rand_dirs(N, rng):
    v = rng.normal(size=(N, 3)); return v / np.linalg.norm(v, axis=1)[:, None]

def distortion(V, n=2, N=20000, h=2e-6, seed=1):
    rng = np.random.default_rng(seed)
    d = rand_dirs(N, rng)
    a = np.cross(d, rng.normal(size=(N, 3))); a /= np.linalg.norm(a, axis=1)[:, None]
    b = np.cross(d, a)
    def D(p): p = p / np.linalg.norm(p, axis=1)[:, None]; return F(p, n, V)
    Ja = (D(d + h * a) - D(d - h * a)) / (2 * h); Jb = (D(d + h * b) - D(d - h * b)) / (2 * h)
    E = Ja[:, 0] * Ja[:, 0] + Ja[:, 1] * Ja[:, 1] + Ja[:, 2] * Ja[:, 2]
    G = (Jb * Jb).sum(1); Fm = (Ja * Jb).sum(1)
    tr = E + G; det = np.maximum(E * G - Fm * Fm, 0)
    s1 = np.sqrt((tr + np.sqrt(np.maximum(tr * tr - 4 * det, 0))) / 2) / abs(n); s2 = np.sqrt(det) / (s1 * n * n)
    return d, s1, s2

if __name__ == '__main__':
    rng = np.random.default_rng(0)
    for V in [('lin', 0, 0), ('area', 0, 0), ('lin', 1, 0), ('area', 1, 0), ('area', 1, 1), ('area', 1, 2), ('lin', 1, 1), ('lin', 1, 2), ('area', 0, 1), ('area', 0, 2)]:
        # quick sanity: plane exactness and round trip
        th = rng.uniform(0, 2 * PI, 2000); rr = rng.uniform(0.1, 2, 2000)
        v = np.stack([rr * np.cos(th), rr * np.sin(th), 0 * th], 1)
        errs = []
        for n in (2, 3, -2):
            w = F(v, n, V); zc = (rr * np.exp(1j * th)) ** n
            errs.append(np.max(np.abs(w[:, 0] + 1j * w[:, 1] - zc) / np.abs(zc)) + np.max(np.abs(w[:, 2])))
        d = rand_dirs(5000, rng); rt = np.abs(layout(layout_inv(d, V), V) - np.abs(d) * np.sign(d) * [1, 1, 0] - np.abs(d) * [0, 0, 1]).max()
        dd, s1, s2 = distortion(V)
        ar, pr = s1 / s2, s1 * s2
        q = lambda a, p: np.percentile(a, p)
        print('%-16s plane err %.1e  roundtrip %.1e | s1/s2 med %.3f p95 %.3f p99.9 %.2f max %.1f | s1*s2 med %.3f p5 %.3f p95 %.3f p99.9 %.2f | mean log(s1/s2) %.3f' % (
            V, max(errs), rt, q(ar, 50), q(ar, 95), q(ar, 99.9), ar.max(), q(pr, 50), q(pr, 5), q(pr, 95), q(pr, 99.9), np.mean(np.log(ar))))
