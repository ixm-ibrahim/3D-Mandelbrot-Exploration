"""Judge, round 25: small attacks on single claims.

    python out/r25/judge/attack.py tear       is the fold of twin_tri a tear off the flat plane? (and the same test on the others)
    python out/r25/judge/attack.py pearl      the pearl tree's flat cut against the true basilica
    python out/r25/judge/attack.py zip        the zip rule as a plain orbit: is there anything off the flat picture?
    python out/r25/judge/attack.py turn       does each solid keep the turn the flat picture keeps (half turn; a third for the cube)?
    python out/r25/judge/attack.py mirror     the rabbit against its mirror image (c -> conj c): is the solid the mirror image?
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl, measure as MS
M = jl.M


def one_step(r, p, c):
    n = p.shape[1]; st = tuple(r.init(n))
    o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), st, 0, np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
    return np.array([o[0], o[1], o[2]])


def tear():
    """Largest jump of one squaring between two points 1e-7 apart, over 400,000 random pairs at each height angle."""
    rng = np.random.default_rng(5)
    for name in ('oneplane', 'along', 'twoplane', 'skew', 'twin_tri', 'face_tri', 'cube', 'cone'):
        r = MS.get(name); c = jl.SETS['rabbit']; rows = []
        for lat in (5, 10, 20, 30, 45, 60, 80):
            n = 400000; lo = rng.uniform(0, 2 * np.pi, n); la = np.radians(lat) * rng.choice([-1.0, 1.0], n)
            u = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
            d = rng.normal(size=(3, n)); d -= (d * u).sum(0) * u; d /= np.linalg.norm(d, axis=0)
            a = one_step(r, u, c); b = one_step(r, u + 1e-7 * d, c)
            j = np.linalg.norm(a - b, axis=0); j = j[np.isfinite(j)]
            rows.append('%d: %.1e (share over 1e-3: %.1e)' % (lat, j.max(), (j > 1e-3).mean()))
        print('%-9s largest jump across 1e-7 at height angle  %s' % (name, ' | '.join(rows))); sys.stdout.flush()
    # the seam of twin_tri itself: the two sides of the upright plane across the line to the meeting point
    R = jl.section('fromc').R if hasattr(jl.section('fromc'), 'R') else None
    r = MS.get('twin_tri')
    for nm in ('c1', 'rabbit'):
        c = jl.SETS[nm]; a = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2; th = np.angle(a); rows = []
        for lat in (0, 10, 20, 30, 45, 60):
            la = np.radians(lat); lo = th + np.pi / 2
            p1 = np.array([[np.cos(la) * np.cos(lo - 1e-7)], [np.cos(la) * np.sin(lo - 1e-7)], [np.sin(la)]])
            p2 = np.array([[np.cos(la) * np.cos(lo + 1e-7)], [np.cos(la) * np.sin(lo + 1e-7)], [np.sin(la)]])
            A = one_step(r, p1, c)[:, 0]; B = one_step(r, p2, c)[:, 0]
            ang = np.degrees(np.arccos(np.clip(np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B)), -1, 1))); rows.append('%d: %.1f' % (lat, ang))
        print('twin_tri, %s: the two sides of its fold are sent this many degrees apart, at height angle  %s' % (nm, ' | '.join(rows)))


def pearl():
    w, h = 900, 650; xs = np.linspace(-1.9, 1.9, w); ys = np.linspace(-1.35, 1.35, h); X, Y = np.meshgrid(xs, ys)
    tru = jl.flat_true(X, Y, -1.0, 0.0, 200) >= 200
    for nm in ('pearl', 'pearl-eisen', 'pearl-line'):
        r = MS.get(nm); t = M.stay(r, X, Y, np.zeros_like(X), 0.0, 0.0, 0.0, 14) >= 14
        print('%-12s flat cut against the true flat picture of c = -1: wrong verdicts %.1f%% of the true area (extra %.1f%%, missing %.1f%%); areas %.3f against %.3f' % (
            nm, 100 * (t != tru).sum() / tru.sum(), 100 * (t & ~tru).sum() / tru.sum(), 100 * (tru & ~t).sum() / tru.sum(), t.mean(), tru.mean()))
    # the same for the skew pillow, as a control of the method: must be 0
    r = MS.get('skew'); t = M.stay(r, X, Y, np.zeros_like(X), -1.0, 0.0, 0.0, 200) >= 200
    print('control: skew pillow, flat cut against the true flat picture, same grid: wrong verdicts %.3f%%' % (100 * (t != tru).sum() / tru.sum()))


def zipcheck():
    rng = np.random.default_rng(3); n = 300000; v = rng.uniform([-1.8, -1.5, -1.5], [1.8, 1.5, 1.5], size=(n, 3))
    for nm in ('zip1', 'zip2', 'oneplane'):
        r = MS.get(nm)
        for sn in ('c1', 'rabbit'):
            c = jl.SETS[sn]; cnt = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 60)
            print('%-9s %-7s share of the box still there after 3 / 6 / 10 / 20 / 40 / 60 steps: %s' % (nm, sn, ' / '.join('%.4f' % (cnt >= s).mean() for s in (3, 6, 10, 20, 40, 60))))
    # lifted flat inside points
    zr, zi = rng.uniform(-1.7, 1.7, 60000), rng.uniform(-1.2, 1.2, 60000); ins = jl.flat_true(zr, zi, -1.0, 0.0, 200) >= 200
    for nm in ('zip1', 'zip2', 'oneplane', 'skew'):
        r = MS.get(nm)
        print('%-9s c = -1: flat inside points lifted by 1e-6 / 1e-3 / 0.02 / 0.1 that still stay after 60 steps: %s' % (
            nm, ' / '.join('%.3f' % (M.stay(r, zr[ins], zi[ins], np.full(ins.sum(), hgt), -1.0, 0.0, 0.0, 60) >= 60).mean() for hgt in (1e-6, 1e-3, 0.02, 0.1))))


def turn():
    rng = np.random.default_rng(11); n = 400000; v = rng.uniform([-1.8, -1.6, -1.5], [1.8, 1.6, 1.5], size=(n, 3))
    jobs = [('oneplane', 'c1', 2), ('oneplane', 'rabbit', 2), ('twoplane', 'c1', 2), ('twoplane', 'rabbit', 2), ('along', 'c1', 2), ('along', 'rabbit', 2), ('alongonce', 'rabbit', 2),
            ('skew', 'c1', 2), ('skew', 'rabbit', 2), ('twin_tri', 'c1', 2), ('twin_tri', 'rabbit', 2), ('cone', 'rabbit', 2),
            ('oneplane3', 'ci', 3), ('cube', 'ci', 3), ('oneplane3', 'c3b', 3), ('cube', 'c3b', 3)]
    for nm, sn, k in jobs:
        r = MS.get(nm); c = jl.SETS[sn]; a = 2 * np.pi / k; co, si = np.cos(a), np.sin(a)
        i1 = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 60) >= 60
        i2 = M.stay(r, co * v[:, 0] - si * v[:, 1], si * v[:, 0] + co * v[:, 1], v[:, 2], c[0], c[1], c[2], 60) >= 60
        print('%-10s %-7s turned by 1/%d of a turn about the upright axis (the flat picture is unchanged by it): %.1f%% of the solid has no partner (%d inside points)' % (
            nm, sn, k, 100 * (i1 & ~i2).sum() / max(1, i1.sum()), int(i1.sum()))); sys.stdout.flush()


def mirror():
    """c -> conj c mirrors the flat picture in the x-axis. Is the solid of conj c the mirror image (y -> -y) of the solid of c?"""
    rng = np.random.default_rng(13); n = 400000; v = rng.uniform([-1.8, -1.6, -1.5], [1.8, 1.6, 1.5], size=(n, 3))
    for nm in ('oneplane', 'along', 'twoplane', 'alongonce', 'skew', 'twin_tri', 'cone', 'tetra'):
        r = MS.get(nm); c = jl.SETS['rabbit']
        i1 = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], 0.0, 60) >= 60
        i2 = M.stay(r, v[:, 0], -v[:, 1], v[:, 2], c[0], -c[1], 0.0, 60) >= 60
        i3 = M.stay(r, v[:, 0], -v[:, 1], -v[:, 2], c[0], -c[1], 0.0, 60) >= 60
        print('%-10s rabbit against the mirror-image rabbit, mirrored back: %.1f%% of the solid differs (mirrored and turned upside down: %.1f%%); sizes %.4f and %.4f' % (
            nm, 100 * (i1 != i2).sum() / max(1, i1.sum()), 100 * (i1 != i3).sum() / max(1, i1.sum()), i1.mean(), i2.mean())); sys.stdout.flush()


if __name__ == '__main__':
    {'tear': tear, 'pearl': pearl, 'zip': zipcheck, 'turn': turn, 'mirror': mirror}[sys.argv[1]]()
