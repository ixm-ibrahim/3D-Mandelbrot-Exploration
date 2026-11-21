"""t7: volumes against the number of steps (the leak test), my own sampling: 150,000 points in the box
-1.8..1.8 x -1.3..1.3 x -1.3..1.3 (volume 24.336). Printed as percent of the box (and as volume)."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
L = lambda lam: M.Rule('lag%g' % lam, '', M.lag(lam))
BOX = 3.6 * 2.6 * 2.6
part = sys.argv[1] if len(sys.argv) > 1 else 'a'
sets = [('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT), ('Siegel', ck.SIEGEL)]
if part == 'a':
    rules = [M.bench('oneplane'), M.bench('along'), M.bench('lathe'), sheet.get('evc005e70k16'), sheet.get('ease'), sheet.get('vote4'),
             am.get('c_wake1'), am.get('c_wake2'), am.get('c_wake3'), am.get('c_wake4'), am.get('b_keep'),
             span.get('c_lag10'), span.get('c_lag25'), span.get('c_page'),
             ck.byname(frame, 'area_1_px'), ck.byname(frame, 'orb_inf_px'), ck.byname(frame, 'pt_1_tr'), prover.BY['first2']]
    stepsl = (30, 80, 200)
elif part == 'b':
    rules = [L(0.1), L(0.45), L(0.5), L(0.55), L(0.6), L(0.65), L(0.7), M.SCOUT[4], M.SCOUT[5]]
    stepsl = (30, 80, 200, 500)
elif part == 'c':
    rules = [ck.fixed_sheet(d) for d in (0, 0.5, 1, 1.5, 2, 5)]
    stepsl = (80, 200)
else:
    rules = [ck.byname(frame, n) for n in ('keep_tr', 'keep_px', 'keep50_tr', 'keepfade_tr', 'turnsq', 'transport', 'pole_05')]
    stepsl = (30, 80)
print('percent of the box inside (volume) at steps %s' % (stepsl,))
for r in rules:
    t0 = time.time(); out = []
    for sn, c in sets:
        v = [ck.volume(r, c, s, n=150000) for s in stepsl]
        out.append('%s %s (%s)' % (sn, ' / '.join('%.2f' % (100 * a) for a in v), ' / '.join('%.3f' % (BOX * a) for a in v)))
    print('  %-14s %s  [%.0f s]' % (r.name, '; '.join(out), time.time() - t0)); sys.stdout.flush()
if part == 'a':
    print('\nevc005e70k16 against the one-plane rule, verdicts that differ of 60,000 at 80 steps (inside evc / inside one-plane):')
    for sn, c in sets + [('c = -1+0.1i', (-1.0, 0.1, 0.0)), ('c = -0.5+0.5i', (-0.5, 0.5, 0.0)), ('Mandelbrot', None)]:
        d = ck.differ(sheet.get('evc005e70k16'), M.bench('oneplane'), c, steps=80)
        print('   %-14s %d (%d / %d)' % (sn, d[0], d[1], d[2]))
    print('c_wake1 / c_wake2 / c_wake4 against the one-plane rule, Mandelbrot solid, verdicts that differ of 300,000 at 60 steps:')
    for n in (1, 2, 4):
        d = ck.differ(am.get('c_wake%d' % n), M.bench('oneplane'), None, steps=60, n=300000)
        print('   c_wake%d: %d (inside %d / %d)' % (n, d[0], d[1], d[2]))
