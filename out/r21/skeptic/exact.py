"""Skeptic: are the 'not spun' numbers of my no-start-page attempts real, or rounding?  python out/r21/skeptic/exact.py
The same recipes are run again with 30 and with 50 decimal digits (Python's decimal module, my own scalar code, no
library). In exact arithmetic the orbit of c never leaves c's own sheet for these recipes; in 16-digit arithmetic it
is pushed off by rounding, and if the recipe magnifies that push the verdict changes."""
import sys
from decimal import Decimal as D, getcontext
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

Z, ONE, TWO, HALF = D(0), D(1), D(2), D(1) / D(2)


def P(x, y, z):
    r2 = x * x + y * y + z * z; d = r2 + z * z
    if d == 0:
        return Z, Z, Z
    f = r2 / d
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r2.sqrt()


def sheet_of(y, z, u):
    q1, q2 = y * y - z * z, 2 * y * z; n = (q1 * q1 + q2 * q2).sqrt()
    return (q1 / n, q2 / n) if n > 0 else u


def half(u):
    co = max(Z, (1 + u[0]) / 2).sqrt(); si = max(Z, (1 - u[0]) / 2).sqrt()
    return co, (si if u[1] >= 0 else -si)


def sq_about(x, y, z, u):
    co, si = half(u); X, Y, Zz = P(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Zz, si * Y + co * Zz


def blend(u, p, lam):
    b1, b2 = (1 - lam) * u[0] + lam * p[0], (1 - lam) * u[1] + lam * p[1]; n = (b1 * b1 + b2 * b2).sqrt()
    return (b1 / n, b2 / n) if n > D('1e-9') else u


def step(kind, x, y, z, st):
    if kind == 'lag25':                                  # S1
        u = blend(st, sheet_of(y, z, st), D('0.25')); return sq_about(x, y, z, u), u
    if kind == 'delay':                                  # S2
        p = sheet_of(y, z, st); u = p if st == (Z, Z) else st; return sq_about(x, y, z, u), p
    if kind == 'ahead1':                                 # S4, g = 1: own sheet turned on by the handed turn from the last sheet to it
        p = sheet_of(y, z, st)
        if st == (Z, Z):
            u = p
        else:
            c2, s2 = st[0] * p[0] + st[1] * p[1], st[0] * p[1] - st[1] * p[0]
            u = (p[0] * c2 - p[1] * s2, p[0] * s2 + p[1] * c2)
        return sq_about(x, y, z, u), p
    if kind == 'lathe':
        return (x * x - y * y - z * z, 2 * x * y, 2 * x * z), st
    if kind == 'lag75':                                  # S1
        u = blend(st, sheet_of(y, z, st), D('0.75')); return sq_about(x, y, z, u), u
    if kind in ('ahead3', 'behind05'):                   # S4, g = 3 and g = -0.5
        p = sheet_of(y, z, st)
        if st == (Z, Z):
            u = p
        else:
            c2, s2 = st[0] * p[0] + st[1] * p[1], st[0] * p[1] - st[1] * p[0]        # cos and sin of twice the handed turn d
            if kind == 'ahead3':                         # turn the sheet on by 3 d: the doubled-angle vector by 6 d = three times 2 d
                a, b = c2 * c2 - s2 * s2, 2 * c2 * s2; a, b = a * c2 - b * s2, a * s2 + b * c2
            else:                                        # turn it back by d / 2: the doubled-angle vector by -d, d in (-90, 90]
                cd = max(Z, (1 + c2) / 2).sqrt(); sd = max(Z, (1 - c2) / 2).sqrt(); sd = sd if s2 >= 0 else -sd
                a, b = cd, -sd
            u = (p[0] * a - p[1] * b, p[0] * b + p[1] * a)
        return sq_about(x, y, z, u), p
    if kind == 'cahead1':                                # S5 c ahead 1: own sheet turned on by its handed turn from c's sheet
        p = sheet_of(y, z, st); cs = sheet_of(C[1], C[2], p)
        c2, s2 = cs[0] * p[0] + cs[1] * p[1], cs[0] * p[1] - cs[1] * p[0]
        return sq_about(x, y, z, (p[0] * c2 - p[1] * s2, p[0] * s2 + p[1] * c2)), st
    if kind == 'span2':                                  # S6: about the plane through 0, the point before and this point
        px, py, pz = st if len(st) == 3 else (Z, Z, Z)
        nx, ny, nz = py * z - pz * y, pz * x - px * z, px * y - py * x
        nn = (nx * nx + ny * ny + nz * nz).sqrt(); sc = ((px * px + py * py + pz * pz) * (x * x + y * y + z * z)).sqrt()
        rho = (y * y + z * z).sqrt(); ax, ay, az = (Z, -z / rho, y / rho) if rho > 0 else (Z, Z, ONE)
        if nn > D('1e-12') * max(sc, D('1e-300')):
            nx, ny, nz = nx / nn, ny / nn, nz / nn
        else:
            nx, ny, nz = ax, ay, az
        e1 = (1 - nx * nx, -nx * ny, -nx * nz); l1 = (e1[0] ** 2 + e1[1] ** 2 + e1[2] ** 2).sqrt()
        if l1 < D('1e-9'):
            nx, ny, nz = ax, ay, az; e1 = (1 - nx * nx, -nx * ny, -nx * nz); l1 = (e1[0] ** 2 + e1[1] ** 2 + e1[2] ** 2).sqrt()
        e1 = tuple(t / l1 for t in e1); e2 = (ny * e1[2] - nz * e1[1], nz * e1[0] - nx * e1[2], nx * e1[1] - ny * e1[0])
        A, B, Cc = P(x * e1[0] + y * e1[1] + z * e1[2], x * e2[0] + y * e2[1] + z * e2[2], x * nx + y * ny + z * nz)
        return (A * e1[0] + B * e2[0] + Cc * nx, A * e1[1] + B * e2[1] + Cc * ny, A * e1[2] + B * e2[2] + Cc * nz), (x, y, z)
    raise ValueError(kind)


C = (Z, Z, Z)


def orbit(kind, c, steps, digits):
    """Returns (how many steps it stays, list of the orbit's distance from c's own sheet)."""
    global C
    getcontext().prec = digits
    cx, cy, cz = (D(float(t)) for t in c); x, y, z = cx, cy, cz; st = (Z, Z); n = 0; off = []; C = (cx, cy, cz)
    rho = (cy * cy + cz * cz).sqrt()
    for k in range(steps):
        (X, Y, Zz), st = step(kind, x, y, z, st)
        x, y, z = X + cx, Y + cy, Zz + cz
        off.append(float(abs(-cz * y + cy * z) / rho) if rho > 0 else 0.0)
        if x * x + y * y + z * z >= 36:
            break
        n += 1
    return n, off


STEPS = 80
rng = np.random.default_rng(21); n = 100000
c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))          # the same 100,000 points as claimS.py
lat = M.mandel(M.bench('lathe'), c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
for kind, name in (('lag25', 'S1 lag25, no start page'), ('lag75', 'S1 lag75, no start page'), ('delay', 'S2 delay, no start page'), ('ahead1', 'S4 ahead 1'),
                   ('ahead3', 'S4 ahead 3'), ('behind05', 'S4 behind 0.5'), ('cahead1', 'S5 c ahead 1'), ('span2', 'S6 span2')):
    r = R.BY[name]; mine = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
    bad = np.flatnonzero(mine != lat); pick = bad[:40]
    print('%s: with 16 digits (the library) %d of %d verdicts differ from the lathe at %d steps (lathe says inside for %d of them). Re-run of the first %d:'
          % (name, bad.size, n, STEPS, int(lat[bad].sum()), pick.size))
    for digits in (30, 50, 100):
        agree = sum((orbit(kind, c[i], STEPS, digits)[0] >= STEPS) == bool(lat[i]) for i in pick)
        print('   with %d digits: %d of %d now agree with the lathe' % (digits, agree, pick.size))
    i = next((j for j in bad if lat[j]), bad[0])
    print('   one of them, c = (%.6f, %.6f, %.6f): distance of the orbit from the sheet of c, at steps 1, 5, 10, 20, 30, 40, 60, 80' % tuple(c[i]))
    for digits in (16, 30, 50):
        nst, off = orbit(kind, c[i], STEPS, digits)
        print('     %2d digits: stays %2d steps; ' % (digits, nst) + ' '.join('%.1e' % off[k - 1] if k <= len(off) else '  --   ' for k in (1, 5, 10, 20, 30, 40, 60, 80)))
    sys.stdout.flush()

if len(sys.argv) > 1 and sys.argv[1] == 'more':
    print('MORE DIGITS for the two recipes that 100 digits did not settle')
    for kind, name in (('behind05', 'S4 behind 0.5'), ('span2', 'S6 span2')):
        r = R.BY[name]; mine = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
        pick = np.flatnonzero(mine != lat)[:40]
        for digits in (200, 400, 800):
            agree = sum((orbit(kind, c[i], STEPS, digits)[0] >= STEPS) == bool(lat[i]) for i in pick)
            print('   %s with %d digits: %d of %d agree with the lathe' % (name, digits, agree, pick.size)); sys.stdout.flush()
