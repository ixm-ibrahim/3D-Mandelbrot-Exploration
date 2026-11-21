"""Judge, re-measurement 7: how many places does one squaring send onto one spot of the flat page?  -> j7_places.txt
Newton from random starts on F(v) = w, with a finite-difference matrix; solutions clustered to 1e-5."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j7_places.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); R['hinge'] = L.design('alonghinge'); R['preturn'] = L.design('preturn'); R['capfold45'] = L.design('capfold45')
Z0 = (0.0, 0.0, 0.0); c = complex(*L.RABBIT[:2])


def F(rule, p, cc):
    n = len(p); X, Y, Z, _ = rule.step(p[:, 0].copy(), p[:, 1].copy(), p[:, 2].copy(), tuple(rule.init(n)), 0, np.full(n, cc[0]), np.full(n, cc[1]), np.full(n, cc[2]))
    return np.stack([X, Y, Z], 1)


def places(rule, w, cc, n=6000, seed=1):
    rng = np.random.default_rng(seed); r = np.sqrt(np.linalg.norm(w))
    p = rng.normal(size=(n, 3)); p *= (r * rng.uniform(0.9, 1.1, n) / np.linalg.norm(p, axis=1))[:, None]
    for _ in range(40):
        with np.errstate(all='ignore'):
            f0 = F(rule, p, cc) - w; Jm = np.zeros((n, 3, 3)); e = 1e-6
            for j in range(3):
                d = np.zeros(3); d[j] = e
                Jm[:, :, j] = (F(rule, p + d, cc) - F(rule, p - d, cc)) / (2 * e)
            ok = np.abs(np.linalg.det(Jm)) > 1e-9
            step = np.zeros_like(p); step[ok] = np.linalg.solve(Jm[ok], f0[ok][:, :, None])[:, :, 0]
            nrm = np.linalg.norm(step, axis=1); step *= np.minimum(1.0, 0.3 / np.maximum(nrm, 1e-300))[:, None]
            p = p - step
    with np.errstate(all='ignore'):
        good = np.linalg.norm(F(rule, p, cc) - w, axis=1) < 1e-9
    sol = []
    for q in p[good]:
        if not any(np.linalg.norm(q - s) < 1e-5 for s in sol):
            sol.append(q)
    return sol


TARGETS = [('the spot c^2 + c of the rabbit (in the flat page)', np.array([(c * c).real, (c * c).imag, 0.0])),
           ('a spot in the flat page, (0.3, 0.2, 0)', np.array([0.3, 0.2, 0.0])),
           ('a spot in the flat page on the left, (-0.5, 0.1, 0)', np.array([-0.5, 0.1, 0.0])),
           ('a spot off the page, (0.2, 0.3, 0.25)', np.array([0.2, 0.3, 0.25]))]
for tn, w in TARGETS:
    say('== places that one squaring sends onto ' + tn)
    for name in ('oneplane', 'lathe', 'along', 'once', 'hinge', 'preturn', 'capfold45'):
        sol = places(R[name], w, L.RABBIT)
        off = [s for s in sol if abs(s[2]) > 1e-6]
        say('   %-9s %2d places, %2d of them off the flat page%s' % (name, len(sol), len(off), ('  e.g. (%.3f, %.3f, %.3f)' % tuple(off[0])) if off else ''))
say('done %.0f s' % (time.time() - t0))
