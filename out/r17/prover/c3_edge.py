"""Prover, claim C3: a small check of the reasoning on KNOWN rules (the full maps are the hunter's job).

Take a c inside the flat main body (the resting point's flat multiplier is rho * exp(i theta)), then lift c off the flat
plane by h. Follow the resting point of v -> F(v) + c, and print the three eigenvalues of its 3 x 3 derivative:
which one reaches size 1 first, at what height h*, and where the orbit of 0 actually stops being bounded (h_vis).

    python out/r17/prover/c3_edge.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S, scout3 as S3


def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


RULES = [('oneplane', S.oneplane), ('lathe', lathe), ('along', S3.turning(1))]


def Fv(F, v):
    X, Y, Z = F(np.array([v[0]]), np.array([v[1]]), np.array([v[2]]))
    return np.array([X[0], Y[0], Z[0]])


def jac(F, v, h=1e-6):
    J = np.zeros((3, 3))
    for k in range(3):
        e = np.zeros(3); e[k] = h
        J[:, k] = (Fv(F, v + e) - Fv(F, v - e)) / (2 * h)
    return J


def rest(F, c, v0):
    v = v0.copy()
    for _ in range(60):
        g = Fv(F, v) + c - v
        if np.linalg.norm(g) < 1e-13:
            break
        A = jac(F, v) - np.eye(3)
        try:
            v = v - np.linalg.solve(A, g)
        except np.linalg.LinAlgError:
            return None
    return v if np.linalg.norm(Fv(F, v) + c - v) < 1e-9 else None


def bounded(F, c, n=600):
    v = np.zeros(3)
    for _ in range(n):
        v = Fv(F, v) + c
        if v @ v > 36:
            return False
    return True


def kind(ev):
    k = int(np.argmax(np.abs(ev)))
    e = ev[k]
    if abs(e.imag) > 1e-7:
        return 'complex pair, angle %.4f turn' % (abs(np.angle(e)) / (2 * np.pi))
    return 'real %+.3f' % e.real


def climb(F, rho, theta, dh=2e-4, hmax=1.2):
    lam = rho * np.exp(1j * theta); a = lam / 2; c2 = a - a * a
    v = np.array([a.real, a.imag, 0.0]); hstar = None; what = ''; last = None
    h = 0.0
    while h < hmax:
        h += dh
        c = np.array([c2.real, c2.imag, h])
        w = rest(F, c, v)
        if w is None or np.linalg.norm(w - v) > 0.05:
            return h, 'resting point lost (it ran away or merged)', last
        v = w
        ev = np.linalg.eigvals(jac(F, v))
        last = ev
        if np.abs(ev).max() >= 1:
            return h, kind(ev), ev
    return None, 'still attracting at h = %.2f' % hmax, last


def visible(F, rho, theta, hmax=1.2):
    lam = rho * np.exp(1j * theta); a = lam / 2; c2 = a - a * a
    lo, hi = 0.0, None
    for h in np.linspace(0.005, hmax, 240):
        if not bounded(F, np.array([c2.real, c2.imag, h])):
            hi = h; break
        lo = h
    return lo, hi


if __name__ == '__main__':
    theta = 2.0          # a generic angle (0.318 turn), upper half of the flat main body
    for name, F in RULES:
        print('\n%s, flat multiplier rho * exp(2.0 i); n = 1 - rho is how far inside the flat rim' % name)
        hs = []
        for rho in (0.5, 0.8, 0.9, 0.95, 0.975):
            hstar, what, ev = climb(F, rho, theta)
            lo, hi = visible(F, rho, theta)
            evs = ' '.join('%.3f%+.3fi' % (e.real, e.imag) for e in ev) if ev is not None else ''
            print('  rho %.3f: resting point stops attracting at h* = %s  [%s]  eigenvalues there: %s | orbit of 0 bounded up to h = %.3f (first escape %s)'
                  % (rho, '%.4f' % hstar if hstar else 'none', what, evs, lo, '%.3f' % hi if hi else 'none'), flush=True)
            if hstar: hs.append((1 - rho, hstar))
        if len(hs) >= 3:
            n, h = np.array(hs[-3:]).T
            p = np.polyfit(np.log(n), np.log(h), 1)[0]
            print('  near the rim h* goes like n^%.2f  (1 = wedge, 1.5 = knife edge, 0.5 = round rim, 0 = full height)' % p)
