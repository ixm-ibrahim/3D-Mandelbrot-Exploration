"""python out/r21/frame/measure.py   -> prints (and writes measure.txt) the numbers behind the reasoned claims in NOTES.md"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
import myrules as R
np.seterr(all='ignore')
out = open(os.path.join(HERE, 'measure.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


rng = np.random.default_rng(11); n = 20000
x, y = rng.uniform(-1.5, 1.5, n), rng.uniform(-1.5, 1.5, n); z0 = np.zeros(n); zc = x + 1j * y
c0 = np.zeros(n)

say('(a) the frame code with a frame that never moves against the bench one-plane rule (20000 random points in space):')
p = rng.uniform(-1.5, 1.5, (n, 3)); X, Y, Z, _ = R.r_fixed(p[:, 0], p[:, 1], p[:, 2], R.init_frame()(n), 0, c0, c0, c0)
X2, Y2, Z2 = M.S.oneplane(p[:, 0], p[:, 1], p[:, 2]); say('    largest difference %.1e' % max(np.abs(X - X2).max(), np.abs(Y - Y2).max(), np.abs(Z - Z2).max()))

say('(b) a frame turned INSIDE the flat page by alpha (about z): the square of a flat point against exp(-i alpha) z^2')
for al in (10.0, 45.0, 90.0, 180.0):
    a = np.radians(al); o = np.ones(n); E = ((o * np.cos(a), o * np.sin(a), 0 * o), (-o * np.sin(a), o * np.cos(a), 0 * o), (0 * o, 0 * o, o))
    F = R.sq_in((x, y, z0), E); w = np.exp(-1j * a) * zc ** 2
    say('    alpha = %5.1f: largest difference from exp(-i alpha) z^2: %.1e ; largest difference from z^2: %.2f ; off the page %.1e'
        % (al, np.abs(F[0] + 1j * F[1] - w).max(), np.abs(F[0] + 1j * F[1] - zc ** 2).max(), np.abs(F[2]).max()))

say('(c) a frame TIPPED about the x-axis by t: a flat point is thrown off the page; height against f * 2 y sin t cos t (x - r), f = r^2 / (r^2 + y^2 sin^2 t)')
for t in (10.0, 45.0, 90.0):
    a = np.radians(t); o = np.ones(n); E = ((o, 0 * o, 0 * o), (0 * o, o * np.cos(a), o * np.sin(a)), (0 * o, -o * np.sin(a), o * np.cos(a)))
    F = R.sq_in((x, y, z0), E); r = np.hypot(x, y); f = r * r / (r * r + (y * np.sin(a)) ** 2)
    say('    t = %4.1f: largest height %.2f ; largest difference from the formula %.1e ; in-page difference from z^2: %.2f'
        % (t, np.abs(F[2]).max(), np.abs(F[2] - f * 2 * y * np.sin(a) * np.cos(a) * (x - r)).max(), np.abs(F[0] + 1j * F[1] - zc ** 2).max()))

say('(d) "the real axis follows the point" (e1_to_point) on the flat page against |z| z:')
X, Y, Z, _ = R.e1_to_point(x, y, z0, R.init_frame()(n), 0, c0, c0, c0)
say('    largest difference from |z| z: %.1e ; largest difference from z^2: %.2f' % (np.abs(X + 1j * Y - np.abs(zc) * zc).max(), np.abs(X + 1j * Y - zc ** 2).max()))

say('(e) how far the carried page tips from the flat page along ONE orbit that starts close to the basilica\'s cycle, a little off the page')
say('    start v = (0.05, 0.03, 0.01), c = -1; angle between the carried out-of-page line and z, in degrees, after each step; |v| in brackets')
for nm in ('keep_tr', 'keepfade_tr', 'turnsq', 'transport', 'pole_05', 'orb_inf_px', 'area_1_px', 'pt_1_tr', 'turn50'):
    r = R.BY[nm]; v = [np.array([0.05]), np.array([0.03]), np.array([0.01])]; st = tuple(r.init(1)); row = []
    for k in range(14):
        X, Y, Z, st = r.step(v[0], v[1], v[2], st, k, np.array([-1.0]), np.array([0.0]), np.array([0.0])); st = tuple(st)
        v = [X - 1.0, Y, Z]; ang = np.degrees(np.arccos(min(1.0, abs(float(st[8][0]))))); rr = float(np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)[0])
        row.append('%.2f(%.2f)' % (ang, rr) if rr < 1e3 else 'gone')
        if rr >= 1e3:
            break
    say('    %-12s %s' % (nm, ' '.join(row)))

say('(f) full following: height of the orbit point above its carried page (|v.e3| / |v|) at the moment it is squared, steps 1..8, largest over 5000 random starts (basilica)')
for nm in ('orb_inf_px', 'orb_inf_tr', 'pt_1_tr', 'orb_2_tr', 'area_1_px'):
    r = R.BY[nm]; m = 5000; q = rng.uniform(-1.2, 1.2, (m, 3)); v = [q[:, 0].copy(), q[:, 1].copy(), q[:, 2].copy()]; st = tuple(r.init(m)); worst = []; orth = 0.0
    cc = (np.full(m, -1.0), np.zeros(m), np.zeros(m))
    for k in range(9):
        if nm.startswith('pt'):
            X, Y, Z, st2 = r.step(v[0], v[1], v[2], st, k, *cc); E = R.unpack(st2)          # this family tips BEFORE squaring
        else:
            E = R.unpack(st); X, Y, Z, st2 = r.step(v[0], v[1], v[2], st, k, *cc)
        rr = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2); ok = (rr < 6) & (rr > 1e-6)
        if k >= 1 or nm.startswith('pt'):
            worst.append(float(np.nanmax(np.where(ok, np.abs(R.dot(v, E[2])) / np.where(ok, rr, 1), 0))))
        st = tuple(st2); E2 = R.unpack(st)
        orth = max(orth, float(np.nanmax(np.where(ok, np.abs(R.dot(E2[0], E2[1])) + np.abs(R.dot(E2[0], E2[2])) + np.abs(R.dot(E2[1], E2[2])) + np.abs(R.dot(E2[0], E2[0]) - 1), 0))))
        v = [np.clip(X - 1.0, -50, 50), np.clip(Y, -50, 50), np.clip(Z, -50, 50)]
    say('    %-11s largest height share %.1e (median over steps %.1e) ; frame off orthonormal by at most %.1e' % (nm, max(worst), float(np.median(worst)), orth))

say('(g) volumes (share of a box that never leaves) at 30 and at 80 steps; a big drop = dust or a slow leak. 150000 random points.')
say('    boxes: basilica -1.8..1.8 x -1.2..1.2 x -1.2..1.2 ; rabbit -1.5..1.5 cubed')
m = 150000; pb = rng.uniform([-1.8, -1.2, -1.2], [1.8, 1.2, 1.2], (m, 3)); pr = rng.uniform(-1.5, 1.5, (m, 3))
rules = [M.bench('along'), M.bench('oneplane')] + [R.BY[t] for t in ('orb_inf_px', 'orb_inf_tr', 'orb_2_tr', 'area_1_px', 'area_4_px', 'pt_1_tr', 'pt_1_px', 'turn50', 'sticky_px', 'stickyfade_px')]
for r in rules:
    nb = M.stay(r, pb[:, 0], pb[:, 1], pb[:, 2], -1.0, 0.0, 0.0, 80); nr = M.stay(r, pr[:, 0], pr[:, 1], pr[:, 2], M.RABBIT[0], M.RABBIT[1], 0.0, 80)
    say('    %-14s basilica %.2f%% -> %.2f%% (kept %.0f%%) ; rabbit %.2f%% -> %.2f%% (kept %.0f%%)'
        % (r.name, 100 * (nb >= 30).mean(), 100 * (nb >= 80).mean(), 100 * (nb >= 80).sum() / max((nb >= 30).sum(), 1),
           100 * (nr >= 30).mean(), 100 * (nr >= 80).mean(), 100 * (nr >= 80).sum() / max((nr >= 30).sum(), 1)))
