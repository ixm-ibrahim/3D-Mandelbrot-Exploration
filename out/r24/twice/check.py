"""Step 1 of section "twice": reproduce the scout's mfold.py with my own form of the map, and test what it is built on.

    python out/r24/twice/check.py same        my map against the scout's, finite, mirror in the flat plane, flat check
    python out/r24/twice/check.py push        the push table (and push times distance at the meeting points of 7 c)
    python out/r24/twice/check.py sphere      covers, folded share, where the copy stands and its real stretch, tears
    python out/r24/twice/check.py bulb        the middle of the 2/5 bulb
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tw
M = tw.M
sys.path.insert(0, os.path.join(tw.ROOT, 'out', 'r24', 'me'))

LIST = [(3, -0.268), (4, -0.10), (4, -0.20), (4, -0.30), (4, -0.45), (6, -0.05), (6, -0.10), (6, -0.20), (8, -0.03), (8, -0.05), (8, -0.10)]
KEYS = ['oneplane', 'along', 'm4:-0.10', 'm4:-0.20', 'm4:-0.30', 'm6:-0.05', 'm6:-0.10', 'm6:-0.20', 'm8:-0.05']


def rand_dirs(n, seed=1):
    rng = np.random.default_rng(seed); p = rng.normal(size=(3, n)); return p / np.linalg.norm(p, axis=0)


def same():
    import mfold as MF
    p = rand_dirs(20000)
    for m, t in LIST:
        a = np.array(MF.mdir(p[0], p[1], p[2], m, t)); b = np.array(tw.mdir(p[0], p[1], p[2], m, t))
        print('m %d t %+.2f: largest difference between my map and the scout\'s on 20,000 directions: %.1e' % (m, t, np.abs(a - b).max()))
    rng = np.random.default_rng(2); n = 20000
    q = rng.normal(size=(3, n)) * rng.uniform(1e-9, 2, n); q[2, :200] = 0; q[0, 200:260] = 0; q[1, 200:260] = 0; q[:, 260] = 0
    v = rng.uniform([-1.6, -1.2, 0.0], [1.6, 1.2, 1.2], size=(40000, 3))
    for key in KEYS + ['m4:-0.10:blend=tvar', 'm6:-0.10:blend=tvar', 'w2:25', 'w2:35', 'w4:25', 'w1:60']:
        r = tw.get(key); o = r.step(q[0].copy(), q[1].copy(), q[2].copy(), (), 0, 0, 0, 0)
        fin = bool(all(np.isfinite(s).all() for s in o[:3])); err = float(np.nanmax(np.abs(np.sqrt(o[0] ** 2 + o[1] ** 2 + o[2] ** 2) - (q * q).sum(0))))
        c = M.RABBIT
        a = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], 0.0, 40) >= 40; b = M.stay(r, v[:, 0], v[:, 1], -v[:, 2], c[0], c[1], 0.0, 40) >= 40
        f = M.flat_check(r, n=20000, steps=60)
        print('%-22s finite %s | length squared, largest error %.1e | mirror in the flat plane (rabbit): %d of %d inside points differ | flat check, differ of %d: M %d, c=-1 %d, rabbit %d, Siegel %d, strays %.1e'
              % (key, fin, err, int((a != b).sum()), int(a.sum()), f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'])); sys.stdout.flush()


def meeting(c):
    """The repelling fixed point of the flat rule where the bodies meet (the one with the smaller |.|), as longitude and distance."""
    cc = complex(c[0], c[1]); a = (1 - np.sqrt(1 - 4 * cc)) / 2
    return float(np.degrees(np.angle(a)) % 360), float(abs(a)), a


def push_at(G, lon_deg, lift_deg):
    la = np.radians(lift_deg); lo = np.radians(np.atleast_1d(np.asarray(lon_deg, float)))
    X, Y, Z = G(np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la) + 0 * lo)
    return np.arcsin(np.clip(Z, -1, 1)) / la


def push():
    lon = np.arange(0, 360, 15.0)
    keys = KEYS[2:] + ['m8:-0.03', 'm8:-0.10', 'm4:-0.10:blend=tvar', 'w2:25', 'w2:35', 'w4:25']
    for key in ['oneplane'] + keys:
        G = tw.dir_of(key) or tw.oneplane_dir
        p = push_at(G, np.arange(0, 360, 1.0), 15.0)
        print('\n== %s   push at a lift of 15 degrees: smallest %.2f at longitude %.0f, largest %.2f at %.0f' % (key, p.min(), np.argmin(p), p.max(), np.argmax(p)))
        print('   longitudes 0, 15, ..., 345: ' + ' '.join('%.2f' % v for v in push_at(G, lon, 15.0)))
        for sn in tw.ORDER:
            lo, d, _ = meeting(tw.SETS[sn])
            print('   %-24s meeting point at longitude %6.1f, distance %.3f: push times distance at lifts 8 / 15 / 25: %s'
                  % (tw.SETNAME[sn], lo, d, ' / '.join('%.2f' % float(push_at(G, lo, l)[0] * d) for l in (8.0, 15.0, 25.0))))
        sys.stdout.flush()


def jac(G, la, lo, h=1e-6):
    def GG(a, b):
        return np.stack(G(np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a) + 0 * b), -1)
    g = GG(la, lo); a = (GG(la + h, lo) - GG(la - h, lo)) / (2 * h); b = (GG(la, lo + h) - GG(la, lo - h)) / (2 * h) / np.cos(la)[..., None]
    return g, a, b


def sphere_numbers(G, n=900):
    lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lon = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi
    LA, LO = np.meshgrid(lat, lon, indexing='ij'); g, a, b = jac(G, LA, LO)
    det = -(np.cross(a, b) * g).sum(-1); dA = np.cos(LA) * (np.pi / n) ** 2
    aa, bb, ab = (a * a).sum(-1), (b * b).sum(-1), (a * b).sum(-1)
    tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0)); s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 0))
    ratio = s1 / np.maximum(s2, 1e-12); wts = dA / dA.sum()
    out = {'covers': float((det * dA).sum() / (4 * np.pi)), 'folded': float(wts[det < 0].sum()), 'squeeze_over_1.5': float(wts[ratio > 1.5].sum()),
           'squeeze_over_3': float(wts[ratio > 3].sum()), 'squeeze_median': float(np.median(ratio)), 'finite': bool(np.isfinite(g).all())}
    return out, (lat, lon, g, a, b, s1, s2, det)


def copy_circle(G, n=4000):
    """Where the upper half is laid onto the flat circle (image height changes sign), and the stretches there:
    along the circle (how much longer the image of a short piece of the circle is) and across it."""
    lat = np.radians(np.linspace(3.0, 89.5, n)); res = []
    for lo_deg in np.arange(0.5, 360, 3.0):
        lo = np.radians(lo_deg) + 0 * lat
        X, Y, Z = G(np.cos(lat) * np.cos(lo), np.cos(lat) * np.sin(lo), np.sin(lat))
        k = np.nonzero(np.sign(Z[1:]) != np.sign(Z[:-1]))[0]
        for i in k:
            f = Z[i] / (Z[i] - Z[i + 1]); la0 = lat[i] + f * (lat[i + 1] - lat[i])
            g, a, b = jac(G, np.array([la0]), np.array([np.radians(lo_deg)]))
            res.append((lo_deg, np.degrees(la0), float(np.linalg.norm(b[0])), float(np.linalg.norm(a[0]))))
    return np.array(res)


def tears(G, m, mu1, n=4000):
    """Largest jump of the direction map across a meridian (tested: every 360/(2m) degrees) inside and above the blend zone."""
    mu = np.linspace(1e-3, 2.5, n); la = 2 * np.arctan(np.exp(mu)) - np.pi / 2; worst = (0.0, 0.0, 0.0)
    for j in range(2 * m):
        lo = np.pi * j / m
        a = np.stack(G(np.cos(la) * np.cos(lo - 1e-9), np.cos(la) * np.sin(lo - 1e-9), np.sin(la)), -1)
        b = np.stack(G(np.cos(la) * np.cos(lo + 1e-9), np.cos(la) * np.sin(lo + 1e-9), np.sin(la)), -1)
        d = np.linalg.norm(a - b, axis=-1); i = int(np.argmax(d))
        if d[i] > worst[0]:
            bad = mu[d > 1e-4]
            worst = (float(d[i]), float(np.degrees(lo)), (float(bad.min()), float(bad.max())) if bad.size else None)
    return worst


def sphere():
    keys = ['oneplane', 'm3:-0.268'] + KEYS[2:] + ['m4:-0.45', 'm8:-0.03', 'm8:-0.10', 'm4:-0.30:mu1=0.28', 'm6:-0.20:mu1=0.25', 'm4:-0.10:blend=tvar', 'm6:-0.10:blend=tvar',
                                               'm4:-0.10:blend=none', 'w1:60:th=90:mua=0.2', 'w2:25', 'w2:35', 'w2:45', 'w4:25', 'w4:35']
    for key in keys:
        G = tw.dir_of(key) or tw.oneplane_dir
        o, _ = sphere_numbers(G); cc = copy_circle(G)
        s = '%-22s lays the directions over each other %.2f times, folded share %.4f | long : short stretch, median %.2f, share over 1.5: %.2f, over 3: %.2f' % (
            key, o['covers'], o['folded'], o['squeeze_median'], o['squeeze_over_1.5'], o['squeeze_over_3'])
        if len(cc):
            s += ' | copy at latitude %.1f..%.1f, stretch along it %.2f..%.2f, across it %.2f..%.2f' % (cc[:, 1].min(), cc[:, 1].max(), cc[:, 2].min(), cc[:, 2].max(), cc[:, 3].min(), cc[:, 3].max())
        if key[0] == 'm':
            p = key.split(':'); m = int(p[0][1:]); t = float(p[1]); mu1 = 0.4
            for q in p[2:]:
                if q.startswith('mu1='):
                    mu1 = float(q[4:])
            pole = -np.log(abs(t)) / m
            tr = tears(G, m, mu1)
            s += ' | directions sent to the upright axis: Mercator %.3f (latitude %.1f); blend ends at %.2f | largest jump across a meridian %.3f%s' % (
                pole, np.degrees(2 * np.arctan(np.exp(pole)) - np.pi / 2), mu1, tr[0], (' at longitude %.0f, Mercator %.3f..%.3f' % (tr[1], tr[2][0], tr[2][1])) if tr[2] else '')
        print(s); sys.stdout.flush()


def bulb():
    """The middle of the p/q bulb: the c near the bulb for which 0 comes back after q steps (Newton from the bulb's root pushed outward)."""
    for p, q in ((1, 4), (2, 5), (1, 3), (1, 2)):
        th = 2 * np.pi * p / q; root = np.exp(1j * th) / 2 - np.exp(2j * th) / 4
        c = root + (root - (np.exp(1j * th) / 2 * 0.9 - np.exp(2j * th) * 0.81 / 4)) * 1.0      # a step outward of the main body
        for _ in range(60):
            z, dz = 0j, 0j
            for _ in range(q):
                dz = 2 * z * dz + 1; z = z * z + c
            c -= z / dz
        z = c; orbit = [0j]
        for _ in range(q):
            orbit.append(z); z = z * z + c
        lo, d, a = None, None, (1 - np.sqrt(1 - 4 * c)) / 2
        # the turn of the bodies round the meeting point: multiplier of the fixed point
        print('%d/%d bulb: root %.6f %+.6fi, middle c = %.6f %+.6fi, 0 comes back after %d steps to %.1e; meeting point %.4f %+.4fi (longitude %.1f, distance %.4f), its multiplier turns by %.4f of a turn'
              % (p, q, root.real, root.imag, c.real, c.imag, q, abs(orbit[-1]), a.real, a.imag, np.degrees(np.angle(a)) % 360, abs(a), (np.angle(2 * a) / (2 * np.pi)) % 1))


if __name__ == '__main__':
    {'same': same, 'push': push, 'sphere': sphere, 'bulb': bulb}[sys.argv[1]]()
