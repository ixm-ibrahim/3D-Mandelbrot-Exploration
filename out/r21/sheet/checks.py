"""The two numbers of the library for every rule of myrules.py, the scout's rules and three bench rules.

    python out/r21/sheet/checks.py [names...]      -> out/r21/sheet/checks.txt (appended when names are given)
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

names = sys.argv[1:]
rules = [R.get(n) for n in names] if names else (R.RULES + M.SCOUT + [M.bench('along'), M.bench('oneplane'), M.bench('lathe')])
lines = []
for r in rules:
    t0 = time.time(); f = M.flat_check(r, n=8000); s = M.spun_check(r, n=8000)
    ln = ('%-10s flat page differs: M %d, basilica %d, rabbit %d, Siegel %d of %d; strays %.1e | turned: M differs %5.2f%% (inside %5.2f%%), basilica differs %5.2f%% (inside %5.2f%%)  [%.0f s]'
          % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], 100 * s['mandel_differ'], 100 * s['mandel_inside'],
             100 * s['basilica_differ'], 100 * s['basilica_inside'], time.time() - t0))
    print(ln); sys.stdout.flush(); lines.append(ln)
with open(os.path.join(HERE, 'checks.txt'), 'a' if names else 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines) + '\n')
