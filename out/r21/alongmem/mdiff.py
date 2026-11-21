"""python out/r21/alongmem/mdiff.py name [name ...]
The Mandelbrot solid of each named rule against the solids of along, the one-plane rule and the lathe: the share of
60,000 random c (box x -2.1..0.7, y and z -1.3..1.3, 40 steps) whose verdict differs, the share inside, and the share
of the inside that lies more than 0.05 off the flat page AND more than 10 degrees off every one of along's 8 half-sheets."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M

if __name__ == '__main__':
    rng = np.random.default_rng(21); n = 60000; steps = 40
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    ref = {nm: M.mandel(M.bench(nm), c[:, 0], c[:, 1], c[:, 2], steps) >= steps for nm in ('along', 'oneplane', 'lathe')}
    phi = np.degrees(np.arctan2(c[:, 2], c[:, 1])) % 45; off = np.minimum(phi, 45 - phi) > 10
    for nm in sys.argv[1:]:
        r = M.bench(nm[6:]) if nm.startswith('bench:') else R.get(nm)
        m = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], steps) >= steps
        print('%-12s inside %.2f%% | differs from along %.2f%%, from one-plane %.2f%%, from the lathe %.2f%% | inside and between the sheets: %.2f%% (along %.2f%%, one-plane %.2f%%, lathe %.2f%%)' % (
            nm, 100 * m.mean(), 100 * (m != ref['along']).mean(), 100 * (m != ref['oneplane']).mean(), 100 * (m != ref['lathe']).mean(),
            100 * (m & off).mean(), 100 * (ref['along'] & off).mean(), 100 * (ref['oneplane'] & off).mean(), 100 * (ref['lathe'] & off).mean()))
        sys.stdout.flush()
