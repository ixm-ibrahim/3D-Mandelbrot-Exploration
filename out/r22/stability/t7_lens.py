"""t7: three follow-up measurements. python out/r22/stability/t7_lens.py > t7_lens.txt
(a) The buds of the basilica's LEFT body (round x = -1) under along: on the circle through their middles
    (x = -1.0463, 0.3075 from the axis) where is there matter, how wide round the axis, how long along x; against the stretch of the step.
(b) The rabbit: how much of along's solid lies inside the lathe's solid and inside one-plane's (random points, 60 and 150 steps).
(c) The rabbit and the Siegel disc: how far the solid reaches straight off the flat page above each cycle point and above the pinch point."""
import numpy as np
import stab as T
M = T.M

print('== (a) buds of the left body, basilica, 200 steps')
X1, D = -1.0463, 0.3075
for nm in ('along', 'oneplane', 'away'):
    r = M.bench(nm); F = T.rule(nm)
    ph = np.radians(np.arange(-10, 100, 0.01))
    ins = M.stay(r, np.full_like(ph, X1), D * np.cos(ph), D * np.sin(ph), *T.BAS, 200) >= 200
    edges = np.flatnonzero(ins[1:] != ins[:-1]) + 1
    if ins[0]:
        edges = edges[1:]
    for s, e in zip(edges[::2], edges[1::2]):
        mid = -10 + 0.01 * (s + e) / 2; wd = 0.01 * (e - s); a = np.radians(mid)
        p0 = np.array([X1, D * np.cos(a), D * np.sin(a)])
        t = np.linspace(0, 0.2, 4001); lx = 0.0
        for sg in (1, -1):
            i2 = M.stay(r, p0[0] + sg * t, np.full_like(t, p0[1]), np.full_like(t, p0[2]), *T.BAS, 200) >= 200
            lx += 0.2 if i2.all() else t[np.argmin(i2)]
        thick = np.radians(wd) * D
        J = T.jac(F, *p0); e_rnd = np.array([0, -np.sin(a), np.cos(a)]); s3, det = T.stretch(J)
        Xo, Yo, Zo = F(*(np.array([v]) for v in p0)); dv, kd = T.turn_from_pages(Yo, Zo)
        print('%-9s bud at turn %6.2f: %.2f degrees = %.4f thick round the axis, %.4f long along x -> long : thick = %.2f | step there: round the axis x%.3f, along x x%.3f, det %+d | its image is %.2f degrees from a %s page, %.3f from the axis, x = %.3f'
              % (nm, mid, wd, thick, lx, lx / max(thick, 1e-9), np.linalg.norm(J @ e_rnd), np.linalg.norm(J[:, 0]), det, dv[0], 'diagonal' if kd[0] else 'flat/upright', float(np.hypot(Yo[0], Zo[0])), Xo[0] - 1))

print('\n== (b) rabbit: overlap of the solids (120,000 random points in the box)')
rng = np.random.default_rng(9); V = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(120000, 3))
for steps in (60, 150):
    ins = {nm: M.stay(M.bench(nm), V[:, 0], V[:, 1], V[:, 2], *T.RABBIT, steps) >= steps for nm in ('along', 'lathe', 'oneplane')}
    A, L, O = ins['along'], ins['lathe'], ins['oneplane']
    print('  %d steps: inside along %d, lathe %d, one-plane %d | of along: %.1f %% also in the lathe, %.1f %% also in one-plane | of the lathe: %.1f %% in along | of one-plane: %.1f %% in along, %.1f %% in the lathe'
          % (steps, A.sum(), L.sum(), O.sum(), 100 * (A & L).sum() / A.sum(), 100 * (A & O).sum() / A.sum(), 100 * (A & L).sum() / L.sum(), 100 * (A & O).sum() / O.sum(), 100 * (O & L).sum() / O.sum()))
    s, det = T.stretch(T.jac(T.rule('along'), V[:, 0], V[:, 1], V[:, 2])); cat = T.category(s, det)
    extra = A & ~O
    print('     along\'s solid by kind of first step: keeps %.1f %%, squeezes %.1f %%, hard %.1f %%, inside out %.1f %% | the part that one-plane does not have (%.1f %% of along): keeps %.1f, squeezes %.1f, hard %.1f, inside out %.1f %%'
          % (*(100 * (cat[A] == k).mean() for k in range(4)), 100 * extra.sum() / A.sum(), *(100 * (cat[extra] == k).mean() for k in range(4))))

print('\n== (c) reach straight off the flat page (up the z direction), 300 steps')
for label, c, p in (('rabbit', T.RABBIT, 3), ('Siegel', T.SIEGEL, 1), ('c=-1+0.1i', (-1.0, 0.1, 0.0), 2), ('basilica', T.BAS, 2)):
    cc = complex(c[0], c[1]); z = 0j
    for _ in range(20000):
        z = z * z + cc
    pts = [('cycle point', z)]
    for _ in range(p - 1):
        pts.append(('cycle point', pts[-1][1] ** 2 + cc))
    alpha = (1 - np.sqrt(1 - 4 * cc + 0j)) / 2
    pts.append(('pinch point', alpha) if label != 'Siegel' else ('middle of the disc', alpha))
    for nm in ('oneplane', 'along', 'lathe', 'away'):
        r = M.bench(nm); out = []
        for lab, q in pts:
            t = np.linspace(1e-4, 1.2, 6000)
            ins = M.stay(r, np.full_like(t, q.real), np.full_like(t, q.imag), t, *c, 300) >= 300
            reach = 0.0 if not ins[0] else (1.2 if ins.all() else t[np.argmin(ins)])
            out.append('%s (%.3f, %.3f): %.3f%s' % (lab, q.real, q.imag, reach, '' if ins[:np.argmin(ins) if not ins.all() else None].all() else '?'))
        print('  %-10s %-9s %s' % (label, nm, ' | '.join(out)))
