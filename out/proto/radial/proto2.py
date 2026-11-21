"""More profiles for the radial layout: stereographic radius R = s^a (prof = ('st', a)), next to the two in proto.py."""
import numpy as np, proto
from proto import *
_lay, _inv = proto.layout, proto.layout_inv
def z_of(prof, ec):
    if prof == 'lin': return np.sin(PI / 2 * ec)
    if prof == 'area': return ec * (2 - ec)
    R = (1 - ec) ** prof[1]; return (1 - R * R) / (1 + R * R)
def ec_of(prof, z):
    if prof == 'lin': return np.arcsin(z) * 2 / PI
    if prof == 'area': return z / (1 + np.sqrt(1 - z))
    return 1 - np.sqrt((1 - z) / (1 + z)) ** (1 / prof[1])
def layout(l, V):
    prof, rnd, lon = V
    mn = l.min(axis=1); e = 3 * mn; s = 1 - e
    k = np.argmin(l, axis=1); sec = (k + 1) % 3
    nxt = np.take_along_axis(l, ((sec + 1) % 3)[:, None], 1)[:, 0]
    t = np.clip((nxt - mn) / np.maximum(s, 1e-300), 0, 1); w = 2 * t - 1
    lam = np.sqrt(1 + 3 * w * w)
    ec = e / (1 + s * (lam - 1)) if rnd else e
    z = z_of(prof, ec); rho = np.sqrt(np.maximum(0, 1 - z * z))
    tau = T3 * (sec + 0.5) + lon_fwd(w, (1 - ec) ** lon) if lon else T3 * (sec + t)
    return np.stack([rho * np.cos(tau), rho * np.sin(tau), z], 1)
def layout_inv(d, V):
    prof, rnd, lon = V
    z = np.clip(np.abs(d[:, 2]), 0, 1); ec = ec_of(prof, z)
    tau = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * PI) / T3
    sec = np.minimum(np.floor(tau), 2).astype(int); t = tau - sec
    if lon: t = np.clip((lon_inv((t - 0.5) * T3, (1 - ec) ** lon) + 1) / 2, 0, 1)
    w = 2 * t - 1; lam = np.sqrt(1 + 3 * w * w)
    e = lam * ec / (1 + ec * (lam - 1)) if rnd else ec
    l = np.zeros((len(z), 3)); idx = np.arange(len(z))
    l[idx, sec] = 1 - t; l[idx, (sec + 1) % 3] = t
    return e[:, None] / 3 + (1 - e)[:, None] * l
proto.layout, proto.layout_inv = layout, layout_inv
if __name__ == '__main__':
    q = lambda a, p: np.percentile(a, p)
    for V in [('lin', 0, 0), ('area', 0, 0), (('st', 1.0), 0, 0), (('st', 0.8), 0, 0), (('st', 0.6046), 0, 0), (('st', 0.45), 0, 0),
              (('st', 1.0), 1, 0), (('st', 0.8), 1, 0), (('st', 0.6046), 1, 0), (('st', 0.6046), 1, 2), (('st', 0.8), 1, 2), (('st', 1.0), 1, 2)]:
        out = []
        for n in (2, 3):
            dd, s1, s2 = proto.distortion(V, n=n); ar, pr = s1 / s2, s1 * s2
            out.append('n=%d s1/s2 med %.3f p95 %.3f p99.9 %.2f | s1*s2 med %.3f p5 %.2f p95 %.2f p99.9 %.2f' % (n, q(ar, 50), q(ar, 95), q(ar, 99.9), q(pr, 50), q(pr, 5), q(pr, 95), q(pr, 99.9)))
        print('%-22s %s' % (V, '  ||  '.join(out)))
