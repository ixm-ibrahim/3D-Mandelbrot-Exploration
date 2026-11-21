"""python out/r21/frame/numbers.py [names...]   flat_check and spun_check for the frame rules -> numbers.txt (appended)"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
import myrules as R

names = sys.argv[1:]
rs = [R.BY[n] for n in names] if names else [R.FIXED] + R.FAILS + R.RULES
if not names:
    rs += [M.bench('oneplane'), M.bench('along'), M.bench('lathe')]
out = open(os.path.join(HERE, 'numbers.txt'), 'a', encoding='utf-8')
np.seterr(all='ignore')
for r in rs:
    t0 = time.time(); f = M.flat_check(r, n=20000); s = M.spun_check(r, n=20000)
    line = ('%-15s flat page: differ M %d, basilica %d, rabbit %d, Siegel %d of %d; strays %.1e | turned round x: M differs %.2f%% (inside %.1f%%), basilica differs %.2f%% (inside %.1f%%)  [%.0f s]'
            % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], 100 * s['mandel_differ'], 100 * s['mandel_inside'],
               100 * s['basilica_differ'], 100 * s['basilica_inside'], time.time() - t0))
    print(line); sys.stdout.flush(); out.write(line + '\n'); out.flush()
