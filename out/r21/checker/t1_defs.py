"""t1: (a) does each 'best' rule's CODE do what its written DEFINITION says? (my re-coding against their rule,
verdict by verdict)  (b) M.flat_check and M.spun_check for every 'best' rule, run by me."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
print('alongmem names:', [r.name for r in am.RULES if 'wake' in r.name or 'keep' in r.name])
print('frame names:', [r.name for r in frame.RULES][:60])

pairs = [
    ('sheet evc005e70k16', sheet.get('evc005e70k16'), ck.evc(0.05, 0.7, 0.7, 16.0)),
    ('sheet ease', sheet.get('ease'), ck.ease()),
    ('sheet vote4', sheet.get('vote4'), ck.vote(4.0)),
    ('alongmem c_wake1', am.get('c_wake1'), ck.wake(1)),
    ('alongmem c_wake2', am.get('c_wake2'), ck.wake(2)),
    ('alongmem b_keep', am.get('b_keep'), ck.keep_along()),
    ('prover first2', prover.BY['first2'], ck.first_k(2)),
    ('skeptic lag70 = M.lag(0.7)', M.Rule('lag70', '', M.lag(0.7)), ck.lag(0.7)),
    ('skeptic lag10 = M.lag(0.1)', M.Rule('lag10', '', M.lag(0.1)), ck.lag(0.1)),
    ('bench along', M.bench('along'), ck.R('along(mine)', lambda x, y, z, st, k, cx, cy, cz: (*ck.along_sq(x, y, z), st), lambda n: ())),
    ('bench oneplane', M.bench('oneplane'), ck.fixed_sheet(0)),
    ('bench lathe', M.bench('lathe'), ck.R('lathe(mine)', lambda x, y, z, st, k, cx, cy, cz: (*ck.lathe(x, y, z), st), lambda n: ())),
]
print('\n(a) their code against my re-coding of their words: verdicts that differ of 60,000 (inside theirs / mine)')
for nm, a, b in pairs:
    t0 = time.time(); out = []
    for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT), ('c=(-0.6,0.3,0.4)', (-0.6, 0.3, 0.4)), ('Mandelbrot', None)):
        d, ia, ib, n = ck.differ(a, b, c)
        out.append('%s %d (%d/%d)' % (cn, d, ia, ib))
    print('  %-28s %s   [%.0f s]' % (nm, '; '.join(out), time.time() - t0)); sys.stdout.flush()

best = [('sheet', sheet.get('evc005e70k16')), ('sheet', sheet.get('ease')), ('sheet', sheet.get('vote4')),
        ('alongmem', am.get('c_wake1')), ('alongmem', am.get('c_wake2')), ('alongmem', am.get('b_keep')),
        ('span', span.get('c_lag10')), ('span', span.get('c_lag25')), ('span', span.get('c_page')),
        ('frame', ck.byname(frame, 'area_1_px')), ('frame', ck.byname(frame, 'orb_inf_px')), ('frame', ck.byname(frame, 'pt_1_tr')),
        ('prover', prover.BY['first2']), ('skeptic', M.Rule('lag70', '', M.lag(0.7))), ('skeptic', M.Rule('lag10', '', M.lag(0.1))),
        ('bench', M.bench('along')), ('bench', M.bench('oneplane')), ('bench', M.bench('lathe'))]
print('\n(b) flat check (40,000 points, 60 steps) and turned check (40,000 pairs, 40 steps), run by the checker')
for who, r in best:
    t0 = time.time(); f = M.flat_check(r); s = M.spun_check(r)
    print('  %-9s %-14s flat: M %d, basilica %d, rabbit %d, Siegel %d of %d, strays %.1e | turned: M %.3f%% (inside %.2f%%), basilica %.3f%% (inside %.2f%%)  [%.0f s]'
          % (who, r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'],
             100 * s['mandel_differ'], 100 * s['mandel_inside'], 100 * s['basilica_differ'], 100 * s['basilica_inside'], time.time() - t0)); sys.stdout.flush()
