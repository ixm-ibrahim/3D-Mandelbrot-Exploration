"""t9: which turns and mirrors leave a solid unchanged (the prover's F1, J1, J4, D3). Share of 40,000 verdicts
that change, 40 steps, my own test points (ck.turned)."""
import sys
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
rules = M.SCOUT + [M.bench('along'), M.bench('away'), sheet.get('evc005e70k16'), sheet.get('ease'), sheet.get('vote4'),
                   am.get('c_wake1'), am.get('b_keep'), span.get('c_lag10'), span.get('c_page'),
                   ck.byname(frame, 'area_1_px'), ck.byname(frame, 'orb_inf_px'), ck.byname(frame, 'pt_1_tr'), prover.BY['first2']]
for what, c in (('Mandelbrot solid', None), ('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT)):
    print('\n%s: percent of verdicts that change under  half-turn | mirror in the flat page | mirror in the upright page | quarter turn | 45 deg | 22.5 deg   (inside %%)' % what)
    for r in rules:
        v = [ck.turned(r, 180.0, c)[0], ck.turned(r, 0, c, mirror='page')[0], ck.turned(r, 0, c, mirror='upright')[0],
             ck.turned(r, 90.0, c)[0], ck.turned(r, 45.0, c)[0], ck.turned(r, 22.5, c)[0]]
        print('   %-14s %s   (%.2f)' % (r.name, ' | '.join('%.3f' % (100 * a) for a in v), 100 * ck.turned(r, 0.0, c)[1])); sys.stdout.flush()
