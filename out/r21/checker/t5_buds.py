"""t5: buds round the x-axis, measured by walking round circles (my own walk, ck.circle).
(a) basilica: the circle x = 0, radius 0.62, through the bud on top of the middle body (flat bud: y from 0.521 to 0.712)
(b) the 'first-step law' of the sheet agent for the lag family
(c) Mandelbrot solid: the circle through the centre of the period-3 bud (x = -0.1226, radius 0.7449)
(d) how big is a bud in its three directions (along x, along the radius, round the axis) for the rules said to have round buds"""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
L = lambda lam: M.Rule('lag%g' % lam, '', M.lag(lam))
BAS = (-1.0, 0.0, 0.0)


def show(arcs):
    if arcs and arcs[0][0] == 'ring':
        return 'RING (inside all the way round)'
    return '%d arcs: ' % len(arcs) + ', '.join('%.1f wide at %.0f' % (w, m) for m, w in arcs[:12]) + (' ...' if len(arcs) > 12 else '')


rules = [M.bench('oneplane'), M.bench('along'), M.bench('lathe'), sheet.get('ease'), sheet.get('evc005e70k16'), sheet.get('evc005e70'), sheet.get('vote4'),
         am.get('c_wake1'), am.get('c_wake2'), am.get('b_keep'), L(0.1), L(0.7), prover.BY['first2'],
         span.get('c_lag10'), span.get('c_page'), ck.byname(frame, 'area_1_px'), ck.byname(frame, 'orb_inf_px'), ck.byname(frame, 'pt_1_tr')]
print('(a) basilica, circle x = 0, radius 0.62, 80 steps, 2,880 places; widths in degrees (a round bud 0.19 tall would be about 17.6 degrees)')
for r in rules:
    arcs, share = ck.circle(r, 0.0, 0.62, BAS, 80)
    print('   %-14s inside %.1f%% of the circle; %s' % (r.name, 100 * share, show(arcs))); sys.stdout.flush()

print('\n(b) lag family, same circle: bud at the page / at the upright sheet, measured, against the law 14.1/(1-lam) and 14.1 (2 lam - 1)/(1-lam)')
base, _ = ck.circle(M.bench('oneplane'), 0.0, 0.62, BAS, 80); w0 = base[0][1]
for lam in (0.1, 0.25, 0.4, 0.45, 0.55, 0.6, 2.0 / 3, 0.7, 0.75, 0.8, 0.9):
    arcs, share = ck.circle(L(lam), 0.0, 0.62, BAS, 80)
    if arcs and arcs[0][0] == 'ring':
        print('   lam %.2f: RING' % lam); continue
    near = lambda a0: [w for m, w in arcs if min(abs(m - a0), 360 - abs(m - a0)) < 6]
    pg, up = near(0.0), near(90.0)
    print('   lam %.2f: page %s (law %.1f); upright %s (law %s); arcs in all %d, inside %.1f%%'
          % (lam, pg, w0 / (1 - lam), up, '%.1f' % (w0 * (2 * lam - 1) / (1 - lam)) if lam > 0.5 else 'none', len(arcs), 100 * share))

print('\n(c) Mandelbrot solid, circle x = -0.1226, radius 0.7449 (through the period-3 bud), 80 steps')
for r in rules + [L(0.25), L(0.4), L(0.45), L(0.55), L(0.6), L(2.0 / 3)]:
    arcs, share = ck.circle(r, -0.122561, 0.744862, None, 80)
    print('   %-14s inside %.1f%%; %s' % (r.name, 100 * share, show(arcs))); sys.stdout.flush()


def extent(rule, c, centre, direction, steps=80, span=0.5, n=2001):
    """Length of the inside run through `centre` along `direction` (None if the centre is not inside)."""
    t = np.linspace(-span, span, n); d = np.array(direction, float); d /= np.linalg.norm(d)
    p = [centre[i] + t * d[i] for i in range(3)]
    ins = ck.inside(rule, p[0], p[1], p[2], c, steps); m = n // 2
    if not ins[m]:
        return None
    a = m
    while a > 0 and ins[a - 1]:
        a -= 1
    b = m
    while b < n - 1 and ins[b + 1]:
        b += 1
    return float(t[b] - t[a])


print('\n(d) size of the basilica bud at the turn phi (centre on the circle x = 0, radius 0.62): along x / along the radius / round the axis (as a length)')
for r in [M.bench('oneplane'), M.bench('along'), sheet.get('ease'), sheet.get('evc005e70k16'), am.get('c_wake1'), am.get('b_keep'), L(0.7), L(2.0 / 3)]:
    out = []
    for phi in (0.0, 45.0, 90.0, 22.5):
        a = np.radians(phi); ce = (0.0, 0.62 * np.cos(a), 0.62 * np.sin(a))
        ex = [extent(r, BAS, ce, d) for d in ((1, 0, 0), (0, np.cos(a), np.sin(a)), (0, -np.sin(a), np.cos(a)))]
        out.append('phi %g: ' % phi + ('not inside' if ex[0] is None else '%.3f / %.3f / %.3f' % tuple(ex)))
    print('   %-14s %s' % (r.name, ' | '.join(out))); sys.stdout.flush()
