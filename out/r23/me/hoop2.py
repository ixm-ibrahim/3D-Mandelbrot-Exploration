"""Numbers for the second toy: the ring of 48 dots round the middle body of c = -1 (x = 0, radius 0.62), five rules,
the two-plane rule among them. Formulas as the toy will use them; the two-plane one is checked against the bench.
    python out/r23/me/hoop2.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r22', 'me'))
import mem as M
import hoopnum as H


def twoplane(x, y, z):
    """Sphere inversions, two planes: the one-plane square about the flat plane or the upright plane, whichever is nearer."""
    up = np.abs(z) > np.abs(y)
    X, Y, Z = H.oneplane(x, np.where(up, z, y), np.where(up, -y, z))          # turn the upright plane down onto the flat one
    return X, np.where(up, -Z, Y), np.where(up, Y, Z)                          # and back up


def main():
    names = []
    try:
        sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); import rules as R
        names = sorted(R.RULES); print('bench rules:', ', '.join(names))
    except Exception as e:
        print('bench not loaded', e)
    rng = np.random.default_rng(3); p = rng.uniform(-1.2, 1.2, (3, 4000))
    for cand in ('twoplane', 'fold', 'two', 'planes2'):
        if cand in names:
            a = R.get(cand)(p[0], p[1], p[2]); b = twoplane(p[0], p[1], p[2])
            print('two planes against bench rule %s: largest difference %.2e' % (cand, max(np.abs(a[i] - b[i]).max() for i in range(3))))
    H.RULES['twoplane'] = lambda k: twoplane
    C = (-1.0, 0.0, 0.0)
    for name in ('lathe', 'oneplane', 'twoplane', 'along', 'alongonce'):
        counts, left = H.run(name, *H.hoop(0.0, 0.62), C, 200)
        print('%-10s' % name, 'still here after 1, 5, 10, 20, 24, 40, 200 hops:', [counts[k - 1] for k in (1, 5, 10, 20, 24, 40, 200)],
              ' last one leaves at hop', int(left.max()), ' survivors', np.nonzero(left == 0)[0].tolist())


if __name__ == '__main__':
    main()
