"""Round 27, respace, step 3: how round do the bulbs off the flat picture stay?

Each bulb of the balls object that hangs on the middle ball off the flat plane is an exact ball. Its skin is sampled,
every sample is carried back to the true frame by the inverse of the carry-over (ways A, B, C; c = -1), and the
carried shape is measured: its three widths along its own main directions, longest against shortest.
Then the same bulbs on the left neighbour (one step of the flat rule back) and on the bud above (three steps back).

    python roundness.py        -> roundness.log (printed), roundness.npz
"""
import sys, time
import numpy as np
import carry as C

T0, K2, RAD = C.T0, C.K2, C.RAD
B0 = C.BASILICA


def bulbs(qmax=10, zmax=3.2):
    """First bulbs off the flat plane on the middle ball: (fraction, centre in the picture frame, radius)."""
    out = {}
    rng = range(-qmax, qmax + 1)
    for qa in rng:
        for qb in rng:
            q = complex(qa, qb); nq = qa * qa + qb * qb
            if nq == 0 or nq > qmax:
                continue
            for pa in range(-12, 13):
                for pb in range(-12, 13):
                    p = complex(pa, pb)
                    zeta = p / q
                    if abs(zeta) > zmax or zeta.imag <= 1e-9 or zeta.real < -1e-9:
                        continue
                    key = (round(zeta.real, 9), round(zeta.imag, 9))
                    if key not in out or nq < out[key]:
                        out[key] = nq                           # the smallest |q|^2 that writes this fraction
    res = []
    for (zr, zi), nq in out.items():
        d = 1.0 / (2 * T0 * nq); cm = np.array([zr, zi, d / 2]) - np.array([0.0, 0.0, 1.0]); rho = d / 2
        den = cm @ cm - rho * rho; uc = K2 * cm / den; r = K2 * rho / abs(den)
        res.append((complex(zr, zi), nq, np.array([uc[2] + K2 / 2, uc[0], uc[1]]), r))
    return res


def sphere(n=700):
    i = np.arange(n) + 0.5; ph = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(ph), np.sin(th) * np.sin(ph), np.cos(ph)]


def carry_back(way, pts, branches=()):
    """Picture-frame points of the balls object -> true-frame points (rows of NaN where the match has no point)."""
    X, Y, Z = C.unrespace(way, *(pts / RAD).T)
    b = -(X + 1j * Y); ok = np.abs(b) < 0.9995
    z = np.full(b.shape, np.nan + 0j); h = np.full(b.shape, np.nan)
    if ok.any():
        zz = B0.unbott(b[ok]); bb, db = B0.bott(zz); good = np.abs(bb - b[ok]) < 1e-6
        zz = np.where(good, zz, np.nan); z[ok] = zz; h[ok] = Z[ok] / np.abs(db)
    for sgn in branches:                                       # one step of the flat rule back: z -> a root of z + 1
        with np.errstate(all='ignore'):                        # 1 / -1: the root on the right / left; 2 / -2: above / below
            w = np.sqrt(z + 1.0); key = w.real if abs(sgn) == 1 else w.imag
            w = np.where(key * np.sign(sgn) < 0, -w, w)
            h = h / (2 * np.abs(w)); z = w
    return np.c_[z.real, z.imag, h]


def widths(P):
    P = P[np.isfinite(P).all(1)]
    if len(P) < 40:
        return None
    Q = P - P.mean(0); w, v = np.linalg.eigh(Q.T @ Q); e = Q @ v
    ext = e.max(0) - e.min(0); return np.sort(ext)[::-1], P.mean(0)


def main():
    t0 = time.time(); S = sphere(); bl = bulbs()
    bl = [b for b in bl if b[3] > 0.004]; bl.sort(key=lambda b: -b[3])
    print('%d first bulbs off the flat plane with radius above 0.004 (quarter of the ball; the rest are mirror images)' % len(bl))
    sizes = [('large', 0.05, 9), ('medium', 0.018, 0.05), ('small', 0.004, 0.018)]
    hosts = [('middle body', ()), ('left neighbour', (-1,)), ('bud above', (1, -1, 2))]
    rows = []
    for host, br in hosts:
        for way in ('A', 'B', 'C'):
            for zeta, nq, cen, r in bl:
                P = cen + r * S
                # the bulb must be checked in its own right: it is whole only if no sample is lost
                Q = carry_back(way, P, br); lost = 1.0 - np.isfinite(Q).all(1).mean()
                wd = widths(Q)
                if wd is None:
                    rows.append((host, way, zeta, r, lost, np.nan, np.nan, np.nan, np.nan)); continue
                ext, mid = wd
                rows.append((host, way, zeta, r, lost, ext[0] / ext[2], ext[0] / ext[1], ext[0], mid[2]))
        print('  %s done  %.0f s' % (host, time.time() - t0)); sys.stdout.flush()
    R = np.array([(hosts.index(next(h for h in hosts if h[0] == a[0])), 'ABC'.index(a[1]), a[2].real, a[2].imag, a[3], a[4], a[5], a[6], a[7], a[8]) for a in rows])
    np.savez('roundness.npz', rows=R)
    for hi, (host, br) in enumerate(hosts):
        for wi, way in enumerate('ABC'):
            sel = R[(R[:, 0] == hi) & (R[:, 1] == wi)]
            print('\n%s, way %s' % (host, way))
            for nm, lo, hi_ in sizes:
                s = sel[(sel[:, 4] >= lo) & (sel[:, 4] < hi_)]
                whole = s[s[:, 5] < 0.02]; cut = s[(s[:, 5] >= 0.02)]
                if len(whole):
                    q = whole[:, 6]
                    print('   %-6s bulbs (radius on the ball %.3f to %.3f): %2d whole; longest / shortest width: least %.2f, middle %.2f, worst %.2f;  %2d cut by a wall or lost'
                          % (nm, lo, min(hi_, sel[:, 4].max()), len(whole), q.min(), np.median(q), q.max(), len(cut)))
                else:
                    print('   %-6s bulbs: none whole; %d cut by a wall or lost' % (nm, len(cut)))
            w = sel[sel[:, 5] < 0.02]
            if len(w):
                k = np.argmax(w[:, 6]); print('   worst whole bulb: at the fraction %.3f%+.3fi, radius %.3f: %.2f times as long as thick' % (w[k, 2], w[k, 3], w[k, 4], w[k, 6]))
    # the twenty-odd bulbs one by one, middle body, ways A and B
    print('\nbulb by bulb on the middle body (fraction, radius on the ball, share lost, longest/shortest for way A | B | C):')
    base = R[(R[:, 0] == 0)]
    for zeta, nq, cen, r in bl[:40]:
        line = '   %6.3f%+6.3fi  r %.3f ' % (zeta.real, zeta.imag, r)
        for wi in range(3):
            s = base[(base[:, 1] == wi) & (np.abs(base[:, 2] - zeta.real) < 1e-9) & (np.abs(base[:, 3] - zeta.imag) < 1e-9)][0]
            line += ' | lost %3.0f%% ratio %5.2f' % (100 * s[5], s[6])
        print(line)
    print('%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
