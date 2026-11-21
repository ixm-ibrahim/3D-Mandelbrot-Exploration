"""python out/r21/alongmem/verify.py
1. End points: rules that must equal a fixed rule of the bench are compared verdict by verdict on random 3D points
   (Julia sets of c = -1, the rabbit, a c off the flat page; the Mandelbrot solid).
2. thin(rule): is the flat picture THICK? Flat-page start points are lifted off the page by 1e-9 and by 1e-4; the
   count of verdicts that differ from the flat picture is given. A rule whose flat page throws nearby points out
   (the flat picture is then a film with nothing on it) shows large counts; the one-plane rule and along show the
   few that sit on the outline."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M


def same(r1, r2, n=60000, steps=40, seed=11):
    rng = np.random.default_rng(seed); v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3)); out = []
    for c in ((-1.0, 0.0, 0.0), M.RABBIT, (-0.6, 0.3, 0.3)):
        a = M.stay(r1, v[:, 0], v[:, 1], v[:, 2], *c, steps) >= steps; b = M.stay(r2, v[:, 0], v[:, 1], v[:, 2], *c, steps) >= steps
        out.append(int((a != b).sum()))
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    a = M.mandel(r1, c[:, 0], c[:, 1], c[:, 2], steps) >= steps; b = M.mandel(r2, c[:, 0], c[:, 1], c[:, 2], steps) >= steps
    out.append(int((a != b).sum())); return out


def thin(rule, n=20000, steps=60, seed=3):
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); out = {}
    for nm, c in (('basilica', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('siegel', M.SIEGEL[:2])):
        fl = M.flat_stay(zr, zi, c[0], c[1], steps) >= steps
        out[nm] = tuple(int(((M.stay(rule, zr, zi, np.full(n, h), c[0], c[1], 0.0, steps) >= steps) != fl).sum()) for h in (1e-9, 1e-4)) + (int(fl.sum()),)
    return out


if __name__ == '__main__':
    if 'ends' in sys.argv or len(sys.argv) == 1:
        for a, b in (('a_fixed', 'along'), ('a_own', 'lathe'), ('c_lag0', 'along'), ('c_lag100', 'oneplane'), ('b_lag0', 'oneplane'), ('b_lag100', 'along'), ('d_conly50', 'along')):
            print('%-9s against %-9s verdicts that differ of 60000 (basilica, rabbit, c off the page, Mandelbrot solid): %s' % (a, b, same(R.get(a), M.bench(b))))
            sys.stdout.flush()
    names = [a for a in sys.argv[1:] if a != 'ends']
    for nm in names:
        r = M.bench(nm[6:]) if nm.startswith('bench:') else R.get(nm); t = thin(r); f = M.flat_check(r, n=20000)
        print('%-12s flat page differ M %d bas %d rab %d sie %d stray %.0e | lifted 1e-9 / 1e-4, differ (of inside): bas %d / %d (%d)  rab %d / %d (%d)  sie %d / %d (%d)' % (
            nm, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'], *t['basilica'], *t['rabbit'], *t['siegel']))
        sys.stdout.flush()
