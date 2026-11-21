"""Round 27, respace: where does way A squeeze, and how much?

Way A lifts a flat point z of a body to the ball by (b(z), |b'(z)| h). On the skin of the carried middle body (height
h_skin(z) = sqrt(1 - |b|^2) / |b'|) a tiny ball is carried to an egg whose long / short width is
    ((sqrt(s^2 + 4) + s) / 2)^2   with   s = h_skin * |b''| / |b'|      (a shear: the factor changes across the bulb).
Printed: that ratio by how far out the foot of the bulb stands (|b| = 0 middle of the body, 1 = rim), c = -1 and rabbit.
"""
import numpy as np
import carry as C

for nm, B in (('c = -1', C.BASILICA), ('rabbit', C.RABBIT)):
    rng = np.random.default_rng(4); n = 60000
    b = np.sqrt(rng.uniform(0, 0.998 ** 2, n)) * np.exp(2j * np.pi * rng.uniform(0, 1, n))
    z = B.unbott(b); bb, db = B.bott(z); ok = np.abs(bb - b) < 1e-6
    e = 1e-5; _p, dp = B.bott(z + e); _m, dm = B.bott(z - e); d2 = (dp - dm) / (2 * e)
    hs = np.sqrt(np.maximum(1 - np.abs(b) ** 2, 0)) / np.abs(db); s = hs * np.abs(d2) / np.abs(db)
    ratio = ((np.sqrt(s * s + 4) + s) / 2) ** 2
    print(nm, ': %d of %d sample points usable' % (ok.sum(), n))
    for lo, hi in ((0, 0.3), (0.3, 0.6), (0.6, 0.8), (0.8, 0.9), (0.9, 0.96), (0.96, 0.99), (0.99, 0.998)):
        m = ok & (np.abs(b) >= lo) & (np.abs(b) < hi); q = ratio[m]
        print('   foot at %.2f to %.3f of the way out: long / short, middle value %.2f, nine in ten below %.2f, worst %.1f; skin height there %.3f (middle value)'
              % (lo, hi, np.median(q), np.quantile(q, 0.9), q.max(), np.median(hs[m])))
    q = ratio[ok]; print('   share of the skin (seen from above, in the round frame) with long / short below 1.5: %.0f%%; between 1.5 and 3: %.0f%%; above 3: %.0f%%'
                         % (100 * (q < 1.5).mean(), 100 * ((q >= 1.5) & (q < 3)).mean(), 100 * (q >= 3).mean()))
    # the edge height near the two hanging points and near the bud roots: does the skin come down to the flat plane?
    for th, lab in ((0.0, 'hanging point'), (0.5, 'opposite point'), (0.25, 'root of the bud at a quarter')):
        rr = 1 - np.array([1e-1, 1e-2, 1e-3]); zz = B.unbott(rr * np.exp(-2j * np.pi * th)); b1, d1 = B.bott(zz)
        print('   skin height on the way to the %s (at 0.9, 0.99, 0.999 of the way out): %s' % (lab, np.round(np.sqrt(1 - np.abs(b1) ** 2) / np.abs(d1), 3)))
