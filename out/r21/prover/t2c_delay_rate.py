"""'delay': the growth of a small lift off the sheet at the resting point, measured against the closed form.

    python out/r21/prover/t2c_delay_rate.py  ->  out/r21/prover/t2c_delay_rate.txt

Closed form (NOTES.md, K2): lift(n+1) = 2 |zeta| lift(n) - 2 (|zeta| - Re zeta) lift(n-1); the lift grows or shrinks
per step by the larger root (in size) of  t^2 - 2 |zeta| t + 2 (|zeta| - Re zeta) = 0,  which is
sqrt(2 (|zeta| - Re zeta)) when the roots are complex.

The test is made in the sheet turned 22.5 degrees, NOT in the flat page, because of a property of the library found on
the way: a sheet is stored as (cos 2 theta, sin 2 theta) and read back by a half-angle formula, so a sheet within
about 1e-8 of a turn of the flat page (or of the upright page) is read back as exactly that page.  Lifts below 1e-8
therefore do not move the carried sheet there, and the flat page looks more stable than it is.
The orbit starts AT the resting point in the turned sheet, is lifted square to the sheet by 1e-8 and followed for
120 steps with the library's own step; the factor is read off the envelope of the heights (largest height in each
window of 10 steps, straight-line fit to the logs while the envelope is between 1e-13 and 1e-4).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M


def measure(rule, a, b, zeta, th, lift=1e-8, pre=10, n=120, lo=1e-13, hi=1e-4, win=10):
    co, si = np.cos(th), np.sin(th)
    x_, y_, z_ = np.array([zeta.real]), np.array([zeta.imag * co]), np.array([zeta.imag * si])
    cx, cy, cz = np.array([a]), np.array([b * co]), np.array([b * si]); st = (np.array([np.cos(2 * th)]), np.array([np.sin(2 * th)]))
    y_, z_ = y_ - lift * si, z_ + lift * co; hs = []
    for k in range(n):
        X, Y, Z, st = rule.step(x_, y_, z_, st, k + 1, cx, cy, cz); x_, y_, z_ = X + cx, Y + cy, Z + cz
        hs.append(abs(float(-y_[0] * si + z_[0] * co)))
    hs = np.array(hs)
    env = np.array([hs[i:i + win].max() for i in range(pre, n, win)]); nn = np.arange(len(env)) * float(win)
    ok = (env > lo) & (env < hi)
    return float(np.exp(np.polyfit(nn[ok], np.log(env[ok]), 1)[0])) if ok.sum() >= 3 else float('nan')


def main():
    np.seterr(all='ignore')
    scout = {r.name: r for r in M.SCOUT}; out = []
    def say(t):
        print(t); out.append(t)
    cs = [(-0.2, 0.3), (-0.5, 0.2), (-0.6, 0.1), (-0.3, 0.55), (0.1, 0.4), (-0.4, 0.05), (-0.1, 0.1), (0.2, 0.3), (-0.65, 0.3), (0.0, 0.6)]
    th = np.radians(22.5)
    say('growth factor per step of a small lift off the sheet of c, at the resting point of the main body')
    say('%-13s %-18s | %-22s | %-22s | %-22s' % ('c0', 'resting point', 'delay: formula, measured', 'own (lathe): 2 Re zeta', 'fixed sheet: 2 |zeta|'))
    for a, b in cs:
        c0 = complex(a, b); zeta = (1 - np.sqrt(1 - 4 * c0)) / 2
        r, x = abs(zeta), zeta.real; disc = r * r - 2 * (r - x)
        pred = np.sqrt(2 * (r - x)) if disc < 0 else max(abs(r + np.sqrt(disc)), abs(r - np.sqrt(disc)))
        fixed_in_sheet = M.Rule('fx', '', lambda x_, y_, z_, st, k, cx, cy, cz: (*M.sq_about(x_, y_, z_, *st), st))
        say('%-13s %-18s | %8.4f  %8.4f     | %8.4f  %8.4f     | %8.4f  %8.4f' % ('%.2f%+.2fi' % (a, b), '%.3f%+.3fi' % (zeta.real, zeta.imag),
            pred, measure(scout['delay'], a, b, zeta, th), abs(2 * x), measure(scout['own'], a, b, zeta, th), 2 * r, measure(fixed_in_sheet, a, b, zeta, th)))
    say('(nan: the lift shrank or grew too fast for a fit of at least three windows)')
    say('')
    say("the lagging sheet (before each squaring the sheet moves the share lam toward the point's own): formula = the larger root (in size) of")
    say('t^2 - (2|zeta| + 1 - lam (1 + 2 (|zeta| - Re zeta))) t + 2 |zeta| (1 - lam) = 0')
    say('%-13s | %-27s | %-27s | %-27s' % ('c0', 'lam 0.25: formula, measured', 'lam 0.5: formula, measured', 'lam 0.75: formula, measured'))
    for a, b in cs:
        c0 = complex(a, b); zeta = (1 - np.sqrt(1 - 4 * c0)) / 2; r, x = abs(zeta), zeta.real; row = []
        for lam in (0.25, 0.5, 0.75):
            A = np.array([[2 * r - 2 * (r - x) * lam, -2 * (r - x) * (1 - lam)], [lam, 1 - lam]])
            row += [float(np.abs(np.linalg.eigvals(A)).max()), measure(M.Rule('lg', '', M.lag(lam)), a, b, zeta, th)]
        say('%-13s | %8.4f  %8.4f          | %8.4f  %8.4f          | %8.4f  %8.4f' % ('%.2f%+.2fi' % (a, b), *row))
    say('')
    say("the same measurement for 'delay' made IN THE FLAT PAGE with a lift of 1e-11: the library reads a sheet that close to the flat page as the flat page itself,")
    say('so the carried sheet does not move and the lift shrinks by 2 |zeta| per step, whatever the closed form says')
    say('%-13s | %-12s %-12s %-12s' % ('c0', 'closed form', '2 |zeta|', 'measured'))
    for a, b in cs[:6]:
        c0 = complex(a, b); zeta = (1 - np.sqrt(1 - 4 * c0)) / 2; r, x = abs(zeta), zeta.real; disc = r * r - 2 * (r - x)
        pred = np.sqrt(2 * (r - x)) if disc < 0 else max(abs(r + np.sqrt(disc)), abs(r - np.sqrt(disc)))
        say('%-13s | %8.4f     %8.4f     %8.4f' % ('%.2f%+.2fi' % (a, b), pred, 2 * r, measure(scout['delay'], a, b, zeta, 0.0, lift=1e-11, pre=0, n=40, lo=1e-300, hi=1e-9, win=4)))
    open(os.path.join(HERE, 't2c_delay_rate.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
