"""t10: spot checks of the remaining numbers in the claim lists, with my own measuring code (ck.*).
Usage: python t10_spot.py sheet | alongmem | span | frame | prover | skeptic"""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

BOX = 3.6 * 2.6 * 2.6
BAS = (-1.0, 0.0, 0.0)
part = sys.argv[1]
L = lambda lam: M.Rule('lag%g' % lam, '', M.lag(lam))
one, along, lathe = M.bench('oneplane'), M.bench('along'), M.bench('lathe')


def vols(r, c, steps=(30, 80, 200), n=100000):
    return ' / '.join('%.2f' % (100 * ck.volume(r, c, s, n=n)) for s in steps)


def arcs(r, x0, rad, c, steps=80):
    a, share = ck.circle(r, x0, rad, c, steps)
    if a and a[0][0] == 'ring':
        return 'RING'
    return '%d arcs (%s%s), inside %.1f%%' % (len(a), ', '.join('%.1f at %.0f' % (w, m) for m, w in a[:6]), ' ...' if len(a) > 6 else '', 100 * share)


if part == 'sheet':
    R = ck.load('sheet')
    print('flat check of all %d rules (8,000 points): rules with any count not 0:' % len(R.RULES))
    for r in R.RULES:
        f = M.flat_check(r, n=8000)
        if f['mandelbrot'] or f['basilica'] or f['rabbit'] or f['siegel'] or f['off_the_page'] > 1e-9:
            print('   %-12s M %d, basilica %d, rabbit %d, Siegel %d, strays %.1e' % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
    print('rabbit volume %% at 30 / 80 / 200 steps (claim 8 and 13):')
    for nm in ('mirror', 'over', 'away50', 'twice', 'over150', 'thrice', 'ease2', 'after50', 'after75', 'image50', 'image100', 'peek50', 'peek100', 'after25', 'settle1', 'settle1h', 'settle3h', 'fade', 'cpull'):
        print('   %-10s %s' % (nm, vols(R.get(nm), ck.RABBIT)))
    print('votes (claim 10): rabbit lost of well-inside flat points at lift 1e-6 | basilica circle | Mandelbrot period-3 circle')
    for nm in ('vote1', 'vote025', 'vote4', 'voted1'):
        r = R.get(nm); lost, n = ck.lift_loss(r, ck.RABBIT, 1e-6, n=15000)
        print('   %-8s %d/%d | %s | %s' % (nm, lost, n, arcs(r, 0.0, 0.62, BAS), arcs(r, -0.122561, 0.744862, None)))
    print('eased votes (claim 14): Mandelbrot period-3 circle (width x 0.745 / 0.19 = thickness against height)')
    for nm in ('evc005', 'evc005e70k16', 'evc005e70', 'evc005e50', 'evsum010'):
        print('   %-13s %s' % (nm, arcs(R.get(nm), -0.122561, 0.744862, None)))
    print('turned check (claim 15), Mandelbrot solid, 37 degrees, 40 steps:')
    for nm in ('settle1', 'twice', 'ease', 'vote4', 'cpull', 'late2'):
        a, ins = ck.turned(R.get(nm), 37.0, None)
        print('   %-8s %.3f%% (inside %.2f%%)' % (nm, 100 * a, 100 * ins))
    print('upright sheet (cut at 90 degrees) against the flat picture, verdicts that differ of 20,000 (60 steps): Mandelbrot / basilica')
    rng = np.random.default_rng(4); a, b = rng.uniform(-2.1, 0.7, 20000), rng.uniform(-1.3, 1.3, 20000); p, q = rng.uniform(-1.8, 1.8, 20000), rng.uniform(-1.3, 1.3, 20000); z0 = np.zeros(20000)
    fm = M.flat_stay(a, b, a, b, 60) >= 60; fj = M.flat_stay(p, q, -1.0, 0.0, 60) >= 60
    for r in (lathe, along, R.get('ease'), R.get('lag67'), R.get('evc005e70k16'), R.get('evc005e70'), one):
        m = M.mandel(r, a, z0, b, 60) >= 60; j = M.stay(r, p, z0, q, -1.0, 0.0, 0.0, 60) >= 60
        print('   %-13s %d / %d' % (r.name, int((m != fm).sum()), int((j != fj).sum())))

elif part == 'alongmem':
    R = ck.load('alongmem')
    bad = 0
    for r in R.RULES:
        f = M.flat_check(r, n=20000)
        if f['mandelbrot'] or f['basilica'] or f['rabbit'] or f['siegel'] or f['off_the_page'] > 0:
            bad += 1; print('   NOT exact: %-10s M %d, basilica %d, rabbit %d, Siegel %d, strays %.1e' % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
    print('flat check of all %d rules (20,000 points): %d rules with a count or a stray not 0' % (len(R.RULES), bad))
    print('end points (claim 2), verdicts that differ of 60,000: basilica / rabbit / Mandelbrot')
    for nm, ref in (('a_fixed', along), ('a_own', lathe)):
        print('   %s against %s: %s' % (nm, ref.name, ' / '.join(str(ck.differ(R.get(nm), ref, c)[0]) for c in (BAS, ck.RABBIT, None))))
    names = [r.name for r in R.RULES]
    print('groups A and D (claim 4): rabbit volume at 80 steps (x box volume), basilica bud circle')
    for nm in [n for n in names if n.startswith('a_') or n.startswith('d_')]:
        r = R.get(nm); v = BOX * ck.volume(r, ck.RABBIT, 80, n=60000)
        print('   %-12s rabbit %.2f | %s' % (nm, v, arcs(r, 0.0, 0.62, BAS)))
    print('claims 9, 10, 11, 17: volumes x box at 30 / 80 / 200 / 500 steps')
    for nm in ('c_lag25', 'b_delay', 'c_delay', 'a_delay', 'a_first', 'c_wake1', 'c_keep', 'a_keep'):
        if nm in names:
            r = R.get(nm)
            print('   %-8s rabbit %s; Siegel %s' % (nm, ' / '.join('%.2f' % (BOX * ck.volume(r, ck.RABBIT, s, n=60000)) for s in (30, 80, 200, 500)),
                                                 ' / '.join('%.2f' % (BOX * ck.volume(r, ck.SIEGEL, s, n=60000)) for s in (30, 80, 200))))
    print('claim 16: Mandelbrot solid, share of verdicts changed by a random turn (M.spun_check)')
    for nm in ('a_fixed', 'a_lag25', 'a_lag50', 'a_lag75', 'a_own', 'a_keep'):
        s = M.spun_check(R.get(nm)); print('   %-8s M %.2f%%, basilica %.3f%%' % (nm, 100 * s['mandel_differ'], 100 * s['basilica_differ']))
    print('claim 17: c_keep basilica circle: %s' % arcs(R.get('c_keep'), 0.0, 0.62, BAS))
    print('claim 14: sign of along\'s Jacobian (central differences), 200,000 random points of the cube -1.5..1.5:')
    rng = np.random.default_rng(2); v = rng.uniform(-1.5, 1.5, size=(200000, 3)); h = 1e-6; F = ck.along_sq
    J = np.zeros((200000, 3, 3))
    for j in range(3):
        d = np.zeros(3); d[j] = h
        A = np.stack(F(v[:, 0] + d[0], v[:, 1] + d[1], v[:, 2] + d[2]), 1); B = np.stack(F(v[:, 0] - d[0], v[:, 1] - d[1], v[:, 2] - d[2]), 1)
        J[:, :, j] = (A - B) / (2 * h)
    det = np.linalg.det(J); phi = np.degrees(np.arctan2(v[:, 2], v[:, 1])) % 90
    print('   negative at %.1f%% of points; within 10 degrees of the 45-degree sheets: %.1f%%; one-plane rule: %.1f%%' % (100 * (det < 0).mean(), 100 * (det[np.abs(phi - 45) < 10] < 0).mean(),
          100 * (np.linalg.det(np.stack([np.stack([(a - b) / (2 * h) for a, b in zip(ck.P(*(v + e).T), ck.P(*(v - e).T))], 1) for e in (np.array([h, 0, 0]), np.array([0, h, 0]), np.array([0, 0, h]))], 2)) < 0).mean()))

elif part == 'span':
    R = ck.load('span')
    bad = 0
    for r in R.RULES:
        f = M.flat_check(r, n=20000)
        if f['mandelbrot'] or f['basilica'] or f['rabbit'] or f['siegel'] or f['off_the_page'] > 0:
            bad += 1; print('   NOT exact: %-12s %s' % (r.name, f))
    print('flat check of all %d rules (20,000 points): %d with a count or stray not 0' % (len(R.RULES), bad))
    rng = np.random.default_rng(8); v = rng.normal(size=(100000, 3)); n = rng.normal(size=(100000, 3))
    n -= (n * v).sum(1, keepdims=True) * v / (v * v).sum(1, keepdims=True); n /= np.linalg.norm(n, axis=1, keepdims=True)      # a plane through v
    a = np.array([1.0, 0, 0]) - n[:, :1] * n; a /= np.linalg.norm(a, axis=1, keepdims=True)
    sq = 2 * (a * v).sum(1, keepdims=True) * v - (v * v).sum(1, keepdims=True) * a
    Lv = np.stack(ck.lathe(v[:, 0], v[:, 1], v[:, 2]), 1); r2 = (v * v).sum(1, keepdims=True)
    alt = (Lv + r2 * n[:, :1] * n) / np.sqrt(1 - n[:, :1] ** 2)
    print('claim 2: 2(a.v)v - |v|^2 a against (L(v) + |v|^2 n_x n)/sqrt(1 - n_x^2): largest difference / |v|^2 = %.1e (planes with |n_x| < 0.999)' % float((np.abs(sq - alt).max(1) / r2[:, 0])[np.abs(n[:, 0]) < 0.999].max()))
    print('claim 3: against the bench lathe, verdicts that differ of 60,000 for c = -1 / -0.75 / -1.7549')
    for nm in ('c_lathe', 'c_page', 'prev_lathe', 'prev_page'):
        print('   %-10s %s' % (nm, ' / '.join(str(ck.differ(R.get(nm), lathe, c)[0]) for c in (BAS, (-0.75, 0, 0), (-1.754878, 0, 0)))))
    print('claim 4 (fan): rabbit of c_page in the plane through the line of c turned t from the flat page, against the flat Julia set of gamma = |c| e^(i alpha): verdicts that differ of 20,000')
    c = np.array(ck.RABBIT); ch = c / np.linalg.norm(c); perp = np.array([-ch[1], ch[0], 0.0]); ez = np.array([0, 0, 1.0])
    for t in (0, 30, 50, 60, 75, 90):
        w = np.cos(np.radians(t)) * perp + np.sin(np.radians(t)) * ez; nrm = np.cross(ch, w)
        a = np.array([1.0, 0, 0]) - nrm[0] * nrm; a /= np.linalg.norm(a); b = np.cross(nrm, a)
        gam = complex(c @ a, c @ b); s, u = rng.uniform(-1.6, 1.6, 20000), rng.uniform(-1.6, 1.6, 20000)
        pts = s[:, None] * a + u[:, None] * b
        v3 = M.stay(R.get('c_page'), pts[:, 0], pts[:, 1], pts[:, 2], *ck.RABBIT, 60) >= 60
        vf = M.flat_stay(s, u, gam.real, gam.imag, 60) >= 60
        print('   t = %2d: gamma = %.4f%+.4fi (length %.4f, angle %.1f): %d differ (inside %d)' % (t, gam.real, gam.imag, abs(gam), np.degrees(np.angle(gam)), int((v3 != vf).sum()), int(vf.sum())))
    print('claims 5 to 7: Mandelbrot solid turned by a random angle (M.spun_check), and swept formula for c_page')
    for nm in ('c_lathe', 'c_page', 'c_Pfirst', 'prev_lathe', 'prev_page', 'prev_keep'):
        s = M.spun_check(R.get(nm)); print('   %-10s M %.2f%% (inside %.2f%%)' % (nm, 100 * s['mandel_differ'], 100 * s['mandel_inside']))
    cc = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(40000, 3)); x, y, z = cc.T
    rho = np.hypot(x, y); r = np.linalg.norm(cc, axis=1)
    nn = np.stack([-x * z, -y * z, rho ** 2], 1) / (rho * r)[:, None]                 # the plane through c nearest the flat page
    a = np.array([1.0, 0, 0]) - nn[:, :1] * nn; a /= np.linalg.norm(a, axis=1, keepdims=True)
    th = np.arccos(np.clip((cc * a).sum(1) / r, -1, 1))
    v3 = M.mandel(R.get('c_page'), x, y, z, 60) >= 60; vf = M.flat_stay(r * np.cos(th), r * np.sin(th), r * np.cos(th), r * np.sin(th), 60) >= 60
    print('   c_page against "|c| e^(i theta(c)) in the flat set": %d of 40,000 differ' % int((v3 != vf).sum()))
    print('claim 8: c in the spun heart-shaped main body (flat c0 inside the cardioid, any turn): share thrown out at 240 steps')
    t = rng.uniform(0, 2 * np.pi, 60000); a0 = rng.uniform(-0.75, 0.38, 60000); b0 = rng.uniform(0, 0.66, 60000); w = a0 + 1j * b0
    card = np.abs(1 - np.sqrt(1 - 4 * w)) < 0.98; a0, b0, t = a0[card][:8000], b0[card][:8000], t[card][:8000]
    for nm in ('prev_lathe', 'prev_page', 'prev_keep', 'c_page', 'c_lathe'):
        for steps in (30, 240):
            out = ~(M.mandel(R.get(nm), a0, b0 * np.cos(t), b0 * np.sin(t), steps) >= steps)
            print('   %-10s %3d steps: %.1f%% of %d thrown out' % (nm, steps, 100 * out.mean(), a0.size))
    print('claim 11: rabbit volume %% at 30 / 80 steps')
    for nm in ('c_lag10', 'c_lag25', 'c_lag50', 'prev_lag10P', 'prev_lag25P', 'prev_lag50P'):
        print('   %-12s %s' % (nm, vols(R.get(nm), ck.RABBIT, (30, 80))))

elif part == 'frame':
    R = ck.load('frame')
    print('flat check (20,000 points) and turned check of all %d rules; listed: every rule that is NOT exact, and the range of the turned numbers of the exact ones' % len(R.RULES))
    tv = []
    for r in R.RULES:
        f = M.flat_check(r, n=20000)
        if f['mandelbrot'] or f['basilica'] or f['rabbit'] or f['siegel'] or f['off_the_page'] > 1e-9:
            print('   NOT exact: %-12s M %d, basilica %d, rabbit %d, Siegel %d, strays %.1e' % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
        else:
            s = M.spun_check(r, n=20000); tv.append((100 * s['mandel_differ'], r.name, 100 * s['mandel_inside']))
    tv.sort(); print('   exact rules: %d; turned check from %.2f%% (%s, inside %.2f%%) to %.2f%% (%s)' % (len(tv), tv[0][0], tv[0][1], tv[0][2], tv[-1][0], tv[-1][1]))
    print('   the three lowest:', ['%s %.2f%% (inside %.2f%%)' % (n, a, i) for a, n, i in tv[:3]])
    other = [n for n in dir(R) if 'RULE' in n.upper() or 'BREAK' in n.upper() or 'FAIL' in n.upper()]
    print('   lists in the module:', other)
    print('claim 1: a frame turned by alpha inside its own page: flat point z -> exp(-i alpha) z^2, largest error over 20,000 flat points')
    rng = np.random.default_rng(3); z = rng.uniform(-1.5, 1.5, 20000) + 1j * rng.uniform(-1.5, 1.5, 20000)
    for al in (10, 45, 90, 180):
        a = np.radians(al); zz = z * np.exp(-1j * a); X, Y, Z = ck.P(zz.real, zz.imag, 0 * zz.real); w = (X + 1j * Y) * np.exp(1j * a)
        print('   alpha %3d: %.1e' % (al, float(np.abs(w - np.exp(-1j * a) * z * z).max())))
    print('claim 2: page tipped by t about the x-axis: height of the square of a flat point against f 2y sin t cos t (x - r)')
    x, y = z.real, z.imag
    for t in (5, 30, 60):
        a = np.radians(t); X, Y, Z = ck.sq_th(x, y, 0 * x, a); r = np.hypot(x, y); f = r * r / (r * r + (y * np.sin(a)) ** 2)
        print('   t %2d: %.1e' % (t, float(np.abs(Z - f * 2 * y * np.sin(a) * np.cos(a) * (x - r)).max())))

elif part == 'prover':
    R = ck.load('prover')
    print('S1/S3/K1: Mandelbrot solid, share changed by a turn of 37 degrees (40 steps) | mirror in the flat page | basilica turned 37')
    for nm in ('lag25_cov', 'lag50_cov', 'delay_cov', 'csheet_flat', 'csheet_own', 'twist', 'twist8', 'delay_twist', 'csheet_twist'):
        r = R.BY[nm]
        print('   %-12s %.3f%% | %.3f%% | %.3f%%   (inside %.2f%%)' % (nm, 100 * ck.turned(r, 37.0, None)[0], 100 * ck.turned(r, 0, None, mirror='page')[0], 100 * ck.turned(r, 37.0, BAS)[0], 100 * ck.turned(r, 0.0, None)[1]))
    print('S3: rabbit of twist8, share changed by the mirror in the flat page: %.2f%%; of lag25_cov: %.3f%%' % (100 * ck.turned(R.BY['twist8'], 0, ck.RABBIT, mirror='page')[0], 100 * ck.turned(R.BY['lag25_cov'], 0, ck.RABBIT, mirror='page')[0]))
    print('J2/J3: verdicts that differ of 40,000: rabbit csheet_flat vs one-plane %d; basilica csheet_flat vs one-plane %d; basilica csheet_own vs lathe %d; basilica one-plane vs lathe %d'
          % (ck.differ(R.BY['csheet_flat'], one, ck.RABBIT, n=40000)[0], ck.differ(R.BY['csheet_flat'], one, BAS, n=40000)[0], ck.differ(R.BY['csheet_own'], lathe, BAS, n=40000)[0], ck.differ(one, lathe, BAS, n=40000)[0]))
    print('F4: Mandelbrot solid at 200 steps against the flat set spun (300,000 points): in the solid %% | in the solid but not in the spun set %% | of the spun set cut away %%')
    rng = np.random.default_rng(6); c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(300000, 3))
    spun = M.mandel(lathe, c[:, 0], c[:, 1], c[:, 2], 200) >= 200
    for r in (M.SCOUT[5], R.BY['first2'], R.BY['first3'], R.BY['first8'], M.SCOUT[4], one, M.SCOUT[3], M.SCOUT[2], M.SCOUT[1], along):
        v = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], 200) >= 200
        print('   %-8s %.3f | %.3f | %.0f' % (r.name, 100 * v.mean(), 100 * (v & ~spun).mean(), 100 * (spun & ~v).sum() / spun.sum()))
    print('F5: the closed form of `first` against the library, cut at each turn, 20,000 random c0, 60 steps: verdicts that differ')
    a = rng.uniform(-2.1, 0.7, 20000); b = rng.uniform(0.0, 1.3, 20000)
    for deg in (0, 11.25, 22.5, 45, 67.5, 90):
        t = np.radians(deg); r = np.hypot(a, b); f = r * r / (r * r + (b * np.sin(t)) ** 2)
        X = a + f * (a * a - b * b * np.cos(t) ** 2); Y = b + 2 * f * b * (a * np.cos(t) ** 2 + r * np.sin(t) ** 2); Z = f * b * (r - a) * np.sin(2 * t)
        alive = np.ones(a.size, bool); n = np.ones(a.size, int)              # the first point counts as step 1
        alive &= X * X + Y * Y + Z * Z < 36
        for k in range(59):
            X, Y, Z = np.where(alive, X * X - Y * Y - Z * Z + a, 0), np.where(alive, 2 * X * Y + b, 0), np.where(alive, 2 * X * Z, 0)
            alive &= X * X + Y * Y + Z * Z < 36
        lib = M.mandel(M.SCOUT[5], a, b * np.cos(t), b * np.sin(t), 60) >= 60
        print('   %5.2f degrees: %d' % (deg, int((lib != alive).sum())))
    print('F5 arcs: Mandelbrot period-3 circle, 80 steps')
    for r in (M.SCOUT[5], R.BY['first2'], M.SCOUT[1], M.SCOUT[4], M.bench('away')):
        print('   %-8s %s' % (r.name, arcs(r, -0.122561, 0.744862, None)))

elif part == 'skeptic':
    print('lag solids against the lathe\'s Mandelbrot solid (100,000 c, 80 steps): inside | of those outside the lathe\'s solid')
    rng = np.random.default_rng(9); c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(100000, 3))
    lat = M.mandel(lathe, c[:, 0], c[:, 1], c[:, 2], 80) >= 80
    for lam in (0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.95):
        v = M.mandel(L(lam), c[:, 0], c[:, 1], c[:, 2], 80) >= 80
        print('   lag %.2f: %d | %d (%.1f%%)' % (lam, int(v.sum()), int((v & ~lat).sum()), 100.0 * (v & ~lat).sum() / max(v.sum(), 1)))
    print('turned check of lag70 at 40 and 160 steps (random turn, M.spun_check): %.2f%% / %.2f%%' % (100 * M.spun_check(L(0.7), steps=40)['mandel_differ'], 100 * M.spun_check(L(0.7), steps=160)['mandel_differ']))
    print('noise of the turned check for the lathe and own: %.4f%% / %.4f%% (200,000 pairs, 80 steps)' % (100 * M.spun_check(lathe, n=200000, steps=80)['mandel_differ'], 100 * M.spun_check(M.SCOUT[6], n=200000, steps=80)['mandel_differ']))
    print('basilica upright bud by share: circle x = 0, radius 0.62')
    for lam in (0.5, 0.55, 0.65, 0.7, 0.8, 0.9, 0.95):
        print('   lag %.2f: %s' % (lam, arcs(L(lam), 0.0, 0.62, BAS)))
    print('the 16 attempts of the skeptic: flat check (20,000) and turn of 37 degrees at 40 and 80 steps, Mandelbrot | basilica')
    S = ck.load('skeptic')
    for r in getattr(S, 'ATTEMPTS', []):
        f = M.flat_check(r, n=20000)
        print('   %-22s flat %d/%d/%d/%d | M %.4f%% %.4f%% | basilica %.4f%%' % (r.name[:22], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'],
              100 * ck.turned(r, 37.0, None, 40)[0], 100 * ck.turned(r, 37.0, None, 80)[0], 100 * ck.turned(r, 37.0, BAS, 40)[0]))
