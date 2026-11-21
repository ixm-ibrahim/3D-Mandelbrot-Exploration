"""Why the sheet family behaves as it does: three measurements.

    python out/r21/sheet/explain.py lag        E1/E2: the buds met on two circles round the x-axis, as the lag goes from 0 to 1
    python out/r21/sheet/explain.py turn       E1 for the rules 'turn by h(d)': measured widths against the first-step law
    python out/r21/sheet/explain.py off name.. E2: on the Mandelbrot circle, how far the point is off its squaring sheet, for
                                               the places that stay and the places that leave
Circle 1: x = 0, radius 0.62, c = -1: through the middle of the bud on top of the basilica's middle body.
Circle 2: x = -0.1226, radius 0.7449: through the middle of the period-3 bud of the Mandelbrot set.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
import measure as ME
M = R.M
PI = np.pi


def near(arcs, at, tol=20.0):
    """Width of the arc whose centre is within tol degrees of `at` (or of at + 180); 0 if none; 360 for a full ring."""
    if arcs and arcs[0][1] >= 360.0:
        return 360.0
    w = [wd for c, wd in arcs if min(abs((c - at + 180) % 360 - 180), abs((c - at - 180 + 180) % 360 - 180)) < tol]
    return max(w) if w else 0.0


def lag_table():
    print('lag    | basilica circle: arc at 0 deg, law W0/(1-lam) | arc at 90 deg, law W0(2lam-1)/(1-lam) | all arcs || Mandelbrot circle: arc at 0 | arc at 90 | all arcs')
    w0 = None
    for lam in (0.0, 0.1, 0.25, 0.4, 0.45, 0.55, 0.6, 2 / 3., 0.75, 0.9, 1.0):
        r = R.lam_rule('lag', '', lambda d, x, y, z, k, lam=lam: lam)
        aj = ME.arcs(ME.circle(r, 0.0, 0.62, (-1.0, 0.0, 0.0))); am = ME.arcs(ME.circle(r, -0.1226, 0.7449, None))
        j0, j90, m0, m90 = near(aj, 0), near(aj, 90), near(am, 0), near(am, 90)
        if w0 is None:
            w0 = j0
        law0 = w0 / (1 - lam) if lam < 1 else float('inf'); law90 = w0 * (2 * lam - 1) / (1 - lam) if 0.5 < lam < 1 else (0.0 if lam <= 0.5 else float('inf'))
        print('%.2f   | %6.1f  law %6.1f | %6.1f  law %6.1f | %d arcs, %.0f deg inside || %6.1f | %6.1f | %d arcs, %.0f deg inside'
              % (lam, j0, min(law0, 360), j90, min(law90, 360), len(aj), sum(w for c, w in aj), m0, m90, len(am), sum(w for c, w in am)))
        sys.stdout.flush()


def slope(h, at):
    e = 1e-4; d = np.array([at - e, at + e]); z = np.zeros(2)
    hh = h(d, z, z + 1, z, 0); return float((hh[1] - hh[0]) / (2 * e))


def turn_table():
    s2 = lambda d: np.sin(2 * d)
    H = {'fixed (h = 0)': lambda d, x, y, z, k: 0 * d, 'ease': lambda d, x, y, z, k: d - 0.5 * s2(d), 'over': lambda d, x, y, z, k: d + 0.5 * s2(d),
         'easehalf': lambda d, x, y, z, k: d - 0.25 * s2(d), 'ease2': lambda d, x, y, z, k: d - s2(d), 'mirror (h = -d)': lambda d, x, y, z, k: -d,
         'thrice (h = 3d)': lambda d, x, y, z, k: 3 * d, 'twice (h = 2d)': lambda d, x, y, z, k: 2 * d, 'lag 2/3': lambda d, x, y, z, k: R.toward(d, 2 / 3.),
         'lag 0.25': lambda d, x, y, z, k: R.toward(d, 0.25), 'lag 0.9': lambda d, x, y, z, k: R.toward(d, 0.9)}
    print('rule             | 1 - h\'(0) | 1 - h\'(90) | h(90) | basilica circle: arc at 0, law | arc at 90, law | all arcs')
    w0 = None
    for nm, h in H.items():
        r = R.T(nm, '', h); a = ME.arcs(ME.circle(r, 0.0, 0.62, (-1.0, 0.0, 0.0)))
        k0, k90 = 1 - slope(h, 0.0), 1 - slope(h, PI / 2 - 1e-3); h90 = float(np.degrees(R.wrap(h(np.array([PI / 2 - 1e-6]), 0, 1, 0, 0)[0])))
        j0, j90 = near(a, 0), near(a, 90)
        if w0 is None:
            w0 = j0
        law0 = w0 / abs(k0) if abs(k0) > 1e-6 else 360.0; has90 = abs(abs(h90) - 90) < 1e-3
        law90 = (w0 / abs(k90) if abs(k90) > 1e-6 else 360.0) if has90 else 0.0
        print('%-16s | %6.2f | %6.2f | %5.1f | %6.1f  law %6.1f | %6.1f  law %6.1f | %s' % (nm, k0, k90, h90, j0, min(law0, 360), j90, min(law90, 360), ME.fmt_arcs(a, 0.62, 0.19)))
        sys.stdout.flush()


# ---- E2: a recorder wrapped round a rule's step: how far each orbit's point is off the sheet it is squared about
class Rec:
    def __init__(self, rule, n, uses_old=False, k0=3):
        self.k0 = k0; self.sum = np.zeros(n); self.cnt = np.zeros(n); self.last = np.full(n, np.nan); self.sheet = np.full(n, np.nan); self.rule = rule; self.old = uses_old
        self.r = M.Rule(rule.name, rule.label, self.step, lambda m: tuple(rule.init(m)) + (np.arange(m, dtype=float),))

    @staticmethod
    def turn_of(st):
        return st[0] if len(st) == 1 else 0.5 * np.arctan2(st[1], st[0])

    def step(self, x, y, z, st, k, cx, cy, cz):
        ids = st[-1].astype(int); X, Y, Z, new = self.rule.step(x, y, z, tuple(st[:-1]), k, cx, cy, cz)
        th = self.turn_of(st[:-1] if self.old else new)
        d = np.abs(z * np.cos(th) - y * np.sin(th))             # the height of the point above the sheet it is squared about
        if k >= self.k0:                                        # the first squarings are left out: the settling-in
            self.sum[ids] += d; self.cnt[ids] += 1
        self.last[ids] = d; self.sheet[ids] = th
        return X, Y, Z, tuple(new) + (st[-1],)


def off_table(names, steps=80, n=1440):
    a = np.arange(n) * 2 * PI / n; x = np.full(n, -0.1226); y, z = 0.7449 * np.cos(a), 0.7449 * np.sin(a)
    print('Mandelbrot circle (x = -0.1226, radius 0.7449), %d steps. "height" = distance of the orbit point from the sheet it is squared about.' % steps)
    print('rule       | inside | STAY: mean height over steps 4.., and over steps 40.. | LEAVE: mean height over steps 4.. | places off the page (more than 5 deg) that stay')
    for nm in names:
        rule = R.get(nm); old = nm in ('delay', 'after25', 'after50', 'after75', 'image50', 'image100')
        rec = Rec(rule, n, uses_old=old); k = M.mandel(rec.r, x, y, z, steps); ins = k >= steps
        rec2 = Rec(rule, n, uses_old=old, k0=40); M.mandel(rec2.r, x, y, z, steps)
        mo = rec.sum / np.maximum(rec.cnt, 1); mo2 = rec2.sum / np.maximum(rec2.cnt, 1); lv = ~ins & (rec.cnt > 0)
        offp = np.abs(R.wrap(a)) > np.radians(5)
        print('%-10s | %5.1f%% | %.4f, %.4f | %.4f | %5.1f%%' % (nm, 100 * ins.mean(), mo[ins].mean() if ins.any() else float('nan'), mo2[ins].mean() if ins.any() else float('nan'),
                                                               mo[lv].mean() if lv.any() else float('nan'), 100 * (ins & offp).sum() / offp.sum()))
        sys.stdout.flush()


if __name__ == '__main__':
    if sys.argv[1] == 'lag':
        lag_table()
    elif sys.argv[1] == 'turn':
        turn_table()
    elif sys.argv[1] == 'off':
        off_table(sys.argv[2:])
