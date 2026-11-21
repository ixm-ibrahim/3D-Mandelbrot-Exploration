"""Checks and direction statistics only (fast), for my rules and the known ones. python out/r17/profiles/dirs.py [names]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen as S
R = S.R
names = sys.argv[1:] or ['lathe', 'oneplane', 'twoplane', 'along', 'away'] + [n for n in R.RULES if n.startswith('p_')]
print('%-10s %9s %7s %7s | %7s %7s %7s | %6s %6s | %s' % ('rule', 'reversed', 'x<0', 'x>0', 'str max', 'str p99', 'sq p01', 'an med', 'an p90', 'length / z=0 / y=0 / mirrors'))
for nm in names:
    F = R.get(nm); c = S.checks(F); d = S.directions(F, n=100000)
    print('%-10s %8.1f%% %6.1f%% %6.1f%% | %7.2f %7.2f %7.3f | %6.2f %6.2f | %.0e %.0e %.0e %.0e %.0e' % (nm, d['reversed_pct'], d['reversed_pct_xneg'], d['reversed_pct_xpos'], d['stretch_max'], d['stretch_p99'],
          d['squash_p01'], d['aniso_median'], d['aniso_p90'], c['length'], c['plane_z0'], c['plane_y0'], c['mirror_z'], c['mirror_y']), flush=True)
