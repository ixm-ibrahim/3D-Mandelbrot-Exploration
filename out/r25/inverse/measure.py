"""Round 25, section 'inverse': the numbers behind NOTES.md.

    python out/r25/inverse/measure.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import roots as R
M = R.M
R.Zip.ITERS = 24
N = 160
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)]


def grid_stats(Fs, c, mode):
    Kf, (n, L, h, rstar) = R.grid_K(Fs, c, mode, n=N, verbose=False); K = Kf[:-1].reshape(n, n, n)
    ax = np.linspace(-L, L, n); up = K[:, :, ax > h].sum(); dn = K[:, :, ax < -h].sum()
    return K.mean(), up / max(dn, 1), Kf, (n, L, h, rstar)


def flat_diff(Fs, c, mode, Kf, meta, n=40000):
    rng = np.random.default_rng(2); x, y = rng.uniform(-1.7, 1.7, n), rng.uniform(-1.3, 1.3, n)
    a = R.inside_grid(Fs, c, mode, Kf, meta, pre=2)(x, y, np.zeros(n)); b = M.flat_stay(x, y, c[0], c[1], 60) >= 60
    return (a != b).mean(), a.mean(), b.mean()


if __name__ == '__main__':
    cases = [('one plane', [R.P], 'any'), ('P+Q some', [R.P, R.Q], 'any'), ('P+Q every', [R.P, R.Q], 'all')]
    for b in (1.0, 1.5, 2.0):
        cases.append(('zip b=%g' % b, [R.Zip(b).F], 'any'))
    cases += [('zip b=1 + mirror, every', [R.Zip(1.0).F, R.Zip(1.0, True).F], 'all'), ('zip b=2 + mirror, some', [R.Zip(2.0).F, R.Zip(2.0, True).F], 'any')]
    base = {}
    for nm, Fs, mode in cases:
        for sn, c in SETS:
            vol, ud, Kf, meta = grid_stats(Fs, c, mode)
            if nm == 'one plane':
                base[sn] = vol
            fd = flat_diff(Fs, c, mode, Kf, meta)
            print('%-26s %-7s size %.2f times the one-plane solid; above the flat plane / below it: %.2f; flat cut differs from the flat picture on %.2f%% of the test points'
                  % (nm, sn, vol / base[sn], ud, 100 * fd[0])); sys.stdout.flush()
    print('\nfirst extra ring of bodies of the zip (the circle that the square sends onto the flat circle):')
    for b in (0.75, 1.0, 1.5, 2.0, 3.0):
        m = np.pi * b / 3; print('   b = %-4g  it stands %.0f degrees above the flat plane; its bodies are %.1f times longer than wide' % (b, np.degrees(2 * np.arctan(np.tanh(m / 2))), np.cosh(m)))
