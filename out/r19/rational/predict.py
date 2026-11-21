"""Seconds, no iteration: what the angle-keeping map R(w) = (w^n - beta) / (w^d (1 - beta w^n)), n = d + 2, does.
For each (d, beta): the directions of the upper half sent to -x (buds) and to +x (arms) with the stretch there
(2 = round bodies), the crushed directions (R' = 0) and where they are sent, the directions sent straight up,
and the stretch along the flat circle (2 everywhere = the one-plane rule).
Directions are printed as (degrees from straight up, degrees round from +x).
    python out/r19/rational/predict.py
"""
import numpy as np
P = np.polynomial.polynomial


def polys(d, beta):
    n = d + 2
    N = np.zeros(n + 1); N[0] = -beta; N[n] = 1.0                 # w^n - beta
    D = np.zeros(n + d + 1); D[d] = 1.0; D[n + d] = -beta         # w^d - beta w^(n + d)
    return N, D


def Rv(w, d, beta):
    n = d + 2
    return (w ** n - beta) / (w ** d * (1 - beta * w ** n))


def dR(w, d, beta, h=1e-6):
    return (Rv(w + h, d, beta) - Rv(w - h, d, beta)) / (2 * h)


def stretch(w, d, beta):
    R = Rv(w, d, beta)
    return abs(dR(w, d, beta)) * (1 + abs(w) ** 2) / (1 + abs(R) ** 2)


def where(w):
    return '(%.1f from up, %.0f round)' % (np.degrees(2 * np.arctan(abs(w))), np.degrees(np.angle(w)) % 360)


def report(d, beta, quiet=False):
    N, D = polys(d, beta)
    out = {}
    for tag, s in (('to -x', -1.0), ('to +x', +1.0)):
        r = P.polyroots(P.polysub(N, s * D)); r = r[np.abs(r) < 1 - 1e-6]
        out[tag] = [(w, stretch(w, d, beta)) for w in r]
    cr = P.polyroots(P.polysub(P.polymul(P.polyder(N), D), P.polymul(N, P.polyder(D))))
    cr = cr[(np.abs(cr) < 1 - 1e-9) & (np.abs(cr) > 1e-9)]
    out['crushed'] = [(w, Rv(w, d, beta)) for w in cr]
    z = P.polyroots(N); out['to up'] = list(z[np.abs(z) < 1])
    t = np.linspace(0, 2 * np.pi, 20001); e = np.exp(1j * t)
    s = np.abs(dR(e, d, beta)); out['flat'] = (float(s.min()), float(s.max()))
    if not quiet:
        print('d = %d (covers %d times), beta = %+.4f' % (d, 2 * d + 2, beta))
        for tag in ('to -x', 'to +x'):
            print('   %s: ' % tag + '; '.join('%s stretch %.2f' % (where(w), s) for w, s in out[tag]))
        print('   crushed: ' + '; '.join('%s -> %s' % (where(w), where(W) if abs(W) <= 1 else 'lower half ' + where(1 / np.conj(W))) for w, W in out['crushed'])
              + ('; and straight up (%d-fold) -> straight down' % d if d >= 2 else ''))
        print('   sent straight up: ' + '; '.join(where(w) for w in out['to up']))
        print('   stretch along the flat circle without a band: %.2f to %.2f (one plane: 2 everywhere)' % out['flat'])
    return out


def solve_bud2(d, sign, lo=0.01, hi=0.6):
    hi = 0.24 if d == 2 else hi
    """beta of the given sign for which the extra bud direction arrives with stretch 2 (None if never)."""
    f = lambda b: min([s for w, s in report(d, sign * b, True)['to -x']] or [99.0]) - 2.0
    bs = np.linspace(lo, hi, 400); v = np.array([f(b) for b in bs])
    i = np.flatnonzero((v[:-1] > 0) & (v[1:] <= 0))
    if not i.size:
        return None, float(bs[v.argmin()]), float(v.min() + 2)
    a, b = bs[i[0]], bs[i[0] + 1]
    for _ in range(60):
        m = 0.5 * (a + b)
        if f(m) > 0: a = m
        else: b = m
    return 0.5 * (a + b), None, None


if __name__ == '__main__':
    for d in (1, 2):
        for sign in (+1, -1):
            b, bmin, smin = solve_bud2(d, sign)
            if b is None:
                print('d = %d, sign %+d: the bud stretch never comes down to 2; least %.2f at |beta| = %.3f' % (d, sign, smin, bmin))
            else:
                print('d = %d, sign %+d: bud stretch exactly 2 at |beta| = %.6f' % (d, sign, b))
    print()
    for d, beta in ((1, 0.268), (1, -0.268), (1, 0.10), (1, 0.25), (2, 0.133263), (2, -0.133263), (2, 0.03), (2, -0.03), (2, -0.0666), (2, 0.2)):
        report(d, beta); print()
