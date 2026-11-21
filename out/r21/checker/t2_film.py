"""t2: has the flat picture BODY? Points well inside the flat picture are lifted off the page; how many are lost.
My own sampling (ck.lift_loss), their rules and my re-codings. Also the half-angle dead zone of M.half."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
L = lambda lam: M.Rule('M.lag%g' % lam, '', M.lag(lam))
rules = [M.bench('oneplane'), M.bench('along'), M.bench('lathe'),
         L(0.1), ck.lag(0.1), L(0.25), ck.lag(0.25), L(0.5), ck.lag(0.5), L(0.6), L(0.7), ck.lag(0.7), L(0.75),
         M.SCOUT[4], ck.delay(), M.SCOUT[5],
         sheet.get('ease'), sheet.get('vote4'), sheet.get('evc005e70k16'), sheet.get('mirror'), sheet.get('over'),
         am.get('c_wake1'), am.get('c_wake2'), am.get('b_keep'),
         span.get('c_lag10'), span.get('c_lag25'), span.get('c_page'),
         ck.byname(frame, 'area_1_px'), ck.byname(frame, 'orb_inf_px'), ck.byname(frame, 'pt_1_tr'), prover.BY['first2']]
sets = [('Mandelbrot', None), ('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT), ('Siegel', ck.SIEGEL)]
lifts = [float(a) for a in sys.argv[1:]] or [1e-6]
for lift in lifts:
    print('\nlift %g, 300 steps: lost / well-inside flat points' % lift)
    for r in rules:
        t0 = time.time(); out = []
        for sn, c in sets:
            lost, n = ck.lift_loss(r, c, lift)
            out.append('%s %d/%d (%.1f%%)' % (sn, lost, n, 100.0 * lost / max(n, 1)))
        print('  %-18s %s  [%.0f s]' % (r.name, '; '.join(out), time.time() - t0)); sys.stdout.flush()
