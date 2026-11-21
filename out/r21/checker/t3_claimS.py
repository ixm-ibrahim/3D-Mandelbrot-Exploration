"""t3: Claim S attacked with recipes of MY OWN that name nothing fixed off the x-axis.
For each: flat check; verdicts that change under a turn of 37 and of 90 degrees; verdicts that differ from the lathe.
Then the unstable ones again with 60 decimal digits (my own scalar code, Python decimal)."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck
from ck import P, sq_th, wrap90, PI

NO = lambda n: (np.zeros(n), np.zeros(n))                 # (turn of the carried sheet, flag: 0 = no sheet made yet)


def has(y, z):
    return (y * y + z * z) > 0


def toward(d, lam):
    return 0.5 * np.arctan2(lam * np.sin(2 * d), (1 - lam) + lam * np.cos(2 * d))


def cov_lag(lam, hand=0.0):
    """The sheet starts as the first sheet the orbit makes; before each squaring it moves the share lam toward the
    point's own sheet turned `hand` degrees to the right (hand = 0: unhanded)."""
    h = np.radians(hand)
    def step(x, y, z, st, k, cx, cy, cz):
        th, fl = st; ok = has(y, z); phi = np.arctan2(z, y)
        new = np.where(fl > 0, th + np.where(ok, toward(wrap90(phi + h - th), lam), 0.0), np.where(ok, phi, 0.0))
        return (*sq_th(x, y, z, new), (new, np.maximum(fl, ok)))
    return ck.R('cov_lag%g_hand%g' % (lam, hand), step, NO)


def cov_delay(hand=0.0):
    """Each point is squared about the sheet of the last earlier point that had one (turned `hand` degrees to the
    right); the first such point about its own sheet."""
    h = np.radians(hand)
    def step(x, y, z, st, k, cx, cy, cz):
        th, fl = st; ok = has(y, z); phi = np.arctan2(z, y)
        use = np.where(fl > 0, th + h, np.where(ok, phi, 0.0))
        return (*sq_th(x, y, z, use), (np.where(ok, phi, th), np.maximum(fl, ok)))
    return ck.R('cov_delay_hand%g' % hand, step, NO)


def cov_cmid(share, hand=0.0):
    """Looks at c: the sheet is c's own sheet moved the share of the way toward the point's own sheet (plus a handed
    turn). c on the x-axis: the point's own sheet."""
    h = np.radians(hand)
    def step(x, y, z, st, k, cx, cy, cz):
        okc = has(cy, cz); ok = has(y, z); phi = np.arctan2(z, y); pc = np.where(okc, np.arctan2(cz, cy), phi)
        th = pc + share * wrap90(np.where(ok, phi, pc) - pc) + h
        return (*sq_th(x, y, z, th), st)
    return ck.R('cov_cmid%g_hand%g' % (share, hand), step, NO)


def cov_votes(hand=0.0):
    """Votes (y^2 - z^2, 2yz) of all points so far, summed from NOTHING (no flat start); sheet = direction of the sum
    (own sheet while the sum is 0), turned `hand` degrees times (-1)^k."""
    h = np.radians(hand)
    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = st[0] + y * y - z * z, st[1] + 2 * y * z
        th = np.where(np.hypot(w1, w2) > 0, 0.5 * np.arctan2(w2, w1), 0.0) + h * (-1) ** k
        return (*sq_th(x, y, z, th), (w1, w2))
    return ck.R('cov_votes_hand%g' % hand, step, NO)


def cov_far():
    """The sheet of the orbit point that was farthest from the x-axis so far (carried: that point's turn and distance)."""
    def step(x, y, z, st, k, cx, cy, cz):
        th, far = st; rho = np.hypot(y, z); phi = np.arctan2(z, y); new = rho > far
        th = np.where(new, phi, th)
        return (*sq_th(x, y, z, th), (th, np.maximum(far, rho)))
    return ck.R('cov_far', step, NO)


RECIPES = [cov_lag(0.25), cov_lag(0.5), cov_lag(0.75), cov_lag(0.5, 20.0), cov_delay(), cov_delay(25.0),
           cov_cmid(0.5), cov_cmid(0.5, 30.0), cov_cmid(-1.0), cov_votes(), cov_votes(15.0), cov_far()]

if __name__ == '__main__':
    lathe = M.bench('lathe')
    print('recipe | flat check M/basilica/rabbit/Siegel of 20000 | Mandelbrot: turned 37 deg, 90 deg at 40 steps; 37 deg at 80 steps (inside) | basilica turned 37 | differ from lathe of 60000 at 60 steps')
    for r in RECIPES + [M.SCOUT[6], lathe, M.SCOUT[1], M.bench('along')]:
        t0 = time.time(); f = M.flat_check(r, n=20000)
        a, ins = ck.turned(r, 37.0, None, 40); b, _ = ck.turned(r, 90.0, None, 40); a8, _ = ck.turned(r, 37.0, None, 80)
        j, jin = ck.turned(r, 37.0, (-1.0, 0.0, 0.0), 40)
        d = ck.differ(r, lathe, None)
        print('%-22s | %d/%d/%d/%d | %.4f%% %.4f%%; %.4f%% (%.2f%%) | %.4f%% (%.2f%%) | %d (inside %d / lathe %d)  [%.0f s]'
              % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], 100 * a, 100 * b, 100 * a8, 100 * ins, 100 * j, 100 * jin, d[0], d[1], d[2], time.time() - t0))
        sys.stdout.flush()
