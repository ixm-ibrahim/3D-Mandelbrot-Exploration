"""Two folds (a pleat, a Z-fold): closed-form and meridian scans, no iteration.
Rims are circles centred in the upright plane y = 0. Along the upright great circle, e = elevation above -x,
running over straight-up (90) to +x (180). Cap 1 spans e in (g1, E1); cap 2 (contains cap 1) spans (-g2, E2).
    python out/r19/foldpost/scan2.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import folds as FO


def at_e(e):
    e = np.radians(e); return np.array([-np.cos(e), 0.0, np.sin(e)])


def pleat_from(g1, E1, g2, E2):
    n1 = at_e((g1 + E1) / 2); a1 = np.radians((E1 - g1) / 2)
    n2 = at_e((E2 - g2) / 2); a2 = np.radians((E2 + g2) / 2)
    return FO.fold_pleat(n1, a1, n2, a2)


def meridian_copies(fold, lon=90.0, n=40001):
    """Directions on the meridian above +y that are sent to -x: (source latitude, stretch, handedness)."""
    D = FO.D_of(fold)
    lat = np.linspace(0.02, 89.98, n)
    W = D(FO.sph(lat, np.full_like(lat, lon)))
    e = np.degrees(np.arctan2(W[2], -W[0]))             # elevation above -x of the answer, signed
    out = []
    idx = np.flatnonzero((e[:-1] * e[1:] < 0) & (np.abs(e[:-1] - e[1:]) < 20))
    for i in idx:
        l = lat[i] + (lat[i + 1] - lat[i]) * e[i] / (e[i] - e[i + 1])
        s1, s2, sg = FO.stretch_at(D, FO.sph(l, lon))
        out.append((float(l), s1, sg))
    return out


if __name__ == '__main__':
    print('A. Crescent pleat: both rims pass through straight-up and touch there (straight-up stays straight-up).')
    print('   Closed form: a copy of -x that lands from answer elevation e arrives with stretch sqrt(W)(1+W), W = tan(45 + e/2).')
    for g1, g2 in ((5, 5), (10, 10), (10, 20), (15, 15), (20, 20)):
        f = pleat_from(g1, 90.0, g2, 90.0)
        cp = meridian_copies(f)
        print('   rims %2d above and %2d below -x: copies at source latitude ' % (g1, g2) + '; '.join('%.1f (stretch %.2f%s)' % (l, s, ', mirrored' if sg < 0 else '') for l, s, sg in cp))
    for e in (10, 20, 30, 40, 60):
        W = np.tan(np.radians(45 + e / 2)); print('      closed form, answer elevation %2d (source latitude %.1f): stretch %.2f' % (e, np.degrees(np.arcsin(np.tan(np.radians(e) / 2))), np.sqrt(W) * (1 + W)))
    print()
    print('B. General pleat, cap 1 from g1 above -x over the top to E1 (E1 = 130 leaves 50 degrees of answer, 27 of source, above +x).')
    print('   For each (g1, E1): the mirrored copy is fixed; then scan cap 2 (g2 below -x, E2) for the forward copy nearest stretch 2.')
    for g1, E1 in ((10, 130), (10, 140), (15, 130), (10, 110), (20, 140)):
        best = None
        for g2 in (5, 10, 15, 20, 30):
            for E2 in np.arange(E1 + 1, 179, 2.0):
                f = pleat_from(g1, E1, g2, E2); cp = meridian_copies(f, n=8001)
                if len(cp) != 2: continue
                sc = abs(np.log(cp[1][1] / 2))
                if best is None or sc < best[0]: best = (sc, g2, E2, cp)
        if best:
            sc, g2, E2, cp = best
            f = pleat_from(g1, E1, g2, E2); pole = FO.D_of(f)(np.array([[0.0], [0.0], [1.0]]))[:, 0]
            print('   cap 1 (%d, %d), best cap 2 (-%d, %d): mirrored copy at lat %.1f stretch %.2f; forward copy at lat %.1f stretch %.2f; pole sent to elevation %.1f above %s' % (
                g1, E1, g2, E2, cp[0][0], cp[0][1], cp[1][0], cp[1][1], np.degrees(np.arcsin(pole[2])), '-x' if pole[0] < 0 else '+x'))
            for g2b in (5, 10, 20):
                row = []
                for E2 in (E1 + 2, E1 + 10, E1 + 20, E1 + 35):
                    if E2 >= 179: continue
                    cp = meridian_copies(pleat_from(g1, E1, g2b, E2), n=8001)
                    row.append('E2 %d: ' % E2 + ', '.join('%.1f/%.2f' % (l, s) for l, s, sg in cp))
                print('        g2 %2d -> (source latitude / stretch of each copy)  ' % g2b + ' | '.join(row))
