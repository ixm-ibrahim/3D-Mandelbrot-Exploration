"""Small checks behind single sentences of NOTES.md (log: verify.log).

    python out/r25/wall/verify.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wall as W
import pil as PL
M = W.M


def main():
    rng = np.random.default_rng(1)
    # 1. the fifth thing: which points of the upright axis go to infinity and to 0
    F = W.ws(3, True); zs = np.linspace(0.05, 3.0, 200001); X, Y, Z = F(0 * zs + 1e-12, 0 * zs, zs); L = np.sqrt(X * X + Y * Y + Z * Z)
    print('wind, square on the upright axis: largest image at height %.3f (|image| = %.1e); smallest image at height %.3f (|image| = %.1e)'
          % (zs[np.nanargmax(L)], np.nanmax(L), zs[10000 + np.nanargmin(L[10000:])], np.nanmin(L[10000:])))
    # 2. zoo A: the upright disc through the two roots of z^2 + c is crushed onto the segment from 0 to c  (c = -1: roots +-1, disc in the plane y = 0)
    r = W.RULES['zooA'](); n = 20000; rad = np.sqrt(rng.uniform(0.01, 0.98, n)); ang = rng.uniform(0, 2 * np.pi, n)
    x, z = rad * np.cos(ang), rad * np.sin(ang); o = r.step(x, 0 * x, z, (), 0, np.full(n, -1.0), np.zeros(n), np.zeros(n))
    full = (o[0] - 1.0, o[1], o[2])                       # the library adds c = -1 afterwards
    print('zoo A, c = -1, points of the upright disc of radius 1 in the plane y = 0: image leaves the x-axis by at most %.1e; image x + (1 - r^2) at most %.1e'
          % (float(max(np.abs(full[1]).max(), np.abs(full[2]).max())), float(np.abs(full[0] + (1 - rad ** 2)).max())))
    # 3. the cube pattern in two layouts: push round the flat circle and the lift test at the two meeting points
    lon = np.radians(np.arange(0.5, 360, 1.0)); hs = np.geomspace(0.002, 0.4, 80)
    for muc in (0.0, np.pi / 6, np.pi / 4, np.pi / 3):
        Fp = PL.make(3, True, muc); rr = M.fixed(Fp, 'x', 'x'); row = 'cube pattern, one-plane band of height %.2f:' % muc
        for lat_deg in (5.0, 15.0, 25.0):
            la = np.radians(lat_deg); X, Y, Z = Fp(np.cos(la) * np.cos(lon), np.cos(la) * np.sin(lon), np.sin(la) + 0 * lon)
            p = np.abs(np.arcsin(np.clip(Z / np.sqrt(X * X + Y * Y + Z * Z), -1, 1)) / la) / 3; row += ' push at lift %2.0f: %.2f .. %.2f;' % (lat_deg, p.min(), p.max())
        for c in (1j, 0.5575728 + 0.5403468j):
            fp = np.roots([1, 0, -1, c]); zz = fp[np.argmin(np.abs(3 * fp * fp))]
            k = M.stay(rr, np.full(hs.size, zz.real), np.full(hs.size, zz.imag), hs, c.real, c.imag, 0.0, 80)
            row += ' held above the meeting point of c = %.2f%+.2fi (longitude %.1f, flat stretch %.2f): %.2f;' % (c.real, c.imag, np.degrees(np.angle(zz)) % 360, abs(3 * zz * zz), (k >= 80).mean())
        print(row)
    # 4. power 5 on the same pillow loads and is exact on the flat plane
    r5 = PL.rule_pillow(5); n = 20000
    for c in (0.2 + 0.6j, 0.5 + 0.3j, 0.3 + 0.0j):
        zr, zi = rng.uniform(-1.4, 1.4, n), rng.uniform(-1.4, 1.4, n)
        a = M.stay(r5, zr, zi, np.zeros(n), c.real, c.imag, 0.0, 60) >= 60; b = PL.flat_stay_n(zr, zi, c.real, c.imag, 60, n=5) >= 60
        print('power 5, c = %.2f%+.2fi: flat verdicts that differ: %d of %d (inside %d)' % (c.real, c.imag, int((a != b).sum()), n, int(b.sum())))


if __name__ == '__main__':
    main()
