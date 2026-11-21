"""t3b: are the nonzero 'turned' numbers of nothing-fixed recipes real, or rounding?
Three unhanded recipes with nothing fixed, in my own scalar code with many decimal digits (Python decimal), on the
c where the float64 library verdict DIFFERS from the lathe's. If Claim S is right every one must return to the lathe."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
from decimal import Decimal as D, getcontext
import mem as M, ck, t3_claimS as T

STEPS = 80


def Pd(x, y, z):
    r2 = x * x + y * y + z * z; r = r2.sqrt(); f = r2 / (r2 + z * z) if r2 != 0 else D(0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def about(x, y, z, co, si):
    X, Y, Z = Pd(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Z, si * Y + co * Z


def unit(a, b):
    n = (a * a + b * b).sqrt(); return a / n, b / n


def half_dir(b1, b2):
    """(cos t, sin t) from (cos 2t, sin 2t) without losing small angles."""
    return unit(1 + b1, b2) if b1 >= 0 else unit(b2, 1 - b1)


def run(kind, cx, cy, cz, steps, off=None):
    """Returns (steps stayed, largest distance of the orbit from c's own sheet)."""
    x, y, z = cx, cy, cz; ec = unit(cy, cz); prev = None; u = None; worst = D(0)
    for k in range(steps):
        rho2 = y * y + z * z
        own = unit(y, z) if rho2 != 0 else None
        if kind == 'delay':
            use = prev if prev is not None else (own or (D(1), D(0)))
            if own is not None:
                prev = own
        elif kind == 'lag50':
            if own is None:
                use = half_dir(*u) if u is not None else (D(1), D(0))
            else:
                p = (own[0] * own[0] - own[1] * own[1], 2 * own[0] * own[1])
                if u is None:
                    u = p
                else:
                    b = (u[0] / 2 + p[0] / 2, u[1] / 2 + p[1] / 2); u = unit(*b)
                use = half_dir(*u)
        elif kind == 'cmid-1':
            if own is None:
                use = ec
            else:
                t = own[0] * ec[0] + own[1] * ec[1]; use = (2 * t * ec[0] - own[0], 2 * t * ec[1] - own[1])
        X, Y, Z = about(x, y, z, use[0], use[1])
        x, y, z = X + cx, Y + cy, Z + cz
        worst = max(worst, abs(ec[0] * z - ec[1] * y))
        if x * x + y * y + z * z >= 36:
            return k, worst
    return steps, worst


def flat(cx, cy, cz, steps):
    a, b = cx, (cy * cy + cz * cz).sqrt(); zr, zi = a, b
    for k in range(steps):
        zr, zi = zr * zr - zi * zi + a, 2 * zr * zi + b
        if zr * zr + zi * zi >= 36:
            return k
    return steps


if __name__ == '__main__':
    rng = np.random.default_rng(21); n = 60000
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    lat = M.mandel(M.bench('lathe'), c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
    for kind, rule in (('delay', T.cov_delay()), ('lag50', T.cov_lag(0.5)), ('cmid-1', T.cov_cmid(-1.0))):
        v = M.mandel(rule, c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
        bad = np.flatnonzero(v != lat)
        print('\n%s: float64 verdict differs from the lathe on %d of %d c (%d steps)' % (kind, bad.size, n, STEPS))
        pick = bad[:25]
        for digits in (30, 60, 120):
            getcontext().prec = digits; t0 = time.time(); agree = 0; w = D(0)
            for i in pick:
                cc = [D(float(t)) for t in c[i]]
                s, far = run(kind, *cc, STEPS); f = flat(*cc, STEPS)
                agree += (s >= STEPS) == (f >= STEPS); w = max(w, far)
            print('   %3d digits: %d of %d re-checked verdicts agree with the flat set spun; largest distance of an orbit from the sheet of c: %.1e  [%.0f s]'
                  % (digits, agree, pick.size, float(w), time.time() - t0)); sys.stdout.flush()
