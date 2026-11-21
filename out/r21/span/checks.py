"""The two numbers for every rule of the family, plus two more:
   leak  = the volume of the basilica and of the rabbit at 30 and at 80 steps (trap b of the briefing)
   plane = how far the orbit of 0 strays from the first plane it gets (0 = the Mandelbrot orbit is flat)
python out/r21/span/checks.py [names...]   -> prints, and writes out/r21/span/checks.txt
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M


def volume(rule, c, steps, n=60000, seed=11):
    rng = np.random.default_rng(seed); v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3))
    return float((M.stay(rule, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], steps) >= steps).mean())


def mvolume(rule, steps, n=60000, seed=12):
    rng = np.random.default_rng(seed); c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    return float((M.mandel(rule, c[:, 0], c[:, 1], c[:, 2], steps) >= steps).mean())


def planar(rule, n=20000, steps=12, seed=7):
    """Largest distance of the orbit of 0 from the plane of its first two points c and v1 (orbits kept in a ball of 3)."""
    rng = np.random.default_rng(seed); c = rng.uniform([-2.0, -1.2, -1.2], [0.6, 1.2, 1.2], size=(n, 3))
    cx, cy, cz = c[:, 0], c[:, 1], c[:, 2]; x, y, z = cx.copy(), cy.copy(), cz.copy(); st = tuple(rule.init(n))
    nrm = None; worst = np.zeros(n); alive = np.ones(n, bool)
    for k in range(steps):
        X, Y, Z, st = rule.step(x, y, z, st, k, cx, cy, cz); st = tuple(st)
        x, y, z = X + cx, Y + cy, Z + cz
        alive &= (x * x + y * y + z * z) < 9.0
        x, y, z = np.where(alive, x, 0.3), np.where(alive, y, 0.2), np.where(alive, z, 0.1)
        if k == 0:
            a, b, d = cy * z - cz * y, cz * x - cx * z, cx * y - cy * x; m = np.sqrt(a * a + b * b + d * d)
            good = m > 1e-6; m = np.where(good, m, 1.0); nrm = (a / m, b / m, d / m)
        else:
            dist = np.abs(x * nrm[0] + y * nrm[1] + z * nrm[2])
            worst = np.where(alive & good, np.maximum(worst, dist), worst)
    return float(worst.max()), float(np.median(worst))


if __name__ == '__main__':
    names = sys.argv[1:] or [r.name for r in R.RULES]
    lines = []
    for nm in names:
        r = R.get(nm); t0 = time.time()
        f = M.flat_check(r); s = M.spun_check(r)
        vb = [volume(r, (-1.0, 0.0, 0.0), k) for k in (30, 80)]; vr = [volume(r, M.RABBIT, k) for k in (30, 80)]
        vm = [mvolume(r, k) for k in (30, 80)]
        pl = planar(r)
        line = ('%-13s flat: M %d, basilica %d, rabbit %d, Siegel %d of %d, strays %.1e | turned: M differs %.2f%% (inside %.1f%%), basilica differs %.2f%% (inside %.1f%%)'
                ' | volume 30/80 steps: basilica %.2f%%/%.2f%%, rabbit %.2f%%/%.2f%%, M %.2f%%/%.2f%% | orbit of 0 off its first plane: max %.1e, median %.1e | %.0f s'
                % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], 100 * s['mandel_differ'], 100 * s['mandel_inside'],
                   100 * s['basilica_differ'], 100 * s['basilica_inside'], 100 * vb[0], 100 * vb[1], 100 * vr[0], 100 * vr[1], 100 * vm[0], 100 * vm[1], pl[0], pl[1], time.time() - t0))
        print(line); sys.stdout.flush(); lines.append(line)
    with open(os.path.join(HERE, 'checks.txt'), 'a', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
