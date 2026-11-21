"""Round 28, Track A, the final checker: the fixer's new room, the side spindle, put to the plain recipe. No browser.

  python -B out/r28/final/mk/side7.py     -> out/r28/final/logs/side7.txt

The claim (comment above GL_BALLS_RHO): round the line that joins the second sphere's centre C to its copy at the next
whole number, both on the top wall, the spindle swept by the arc through the two fixed points that reaches
w = min(top - HB, D - rho) from the line at its middle (D = 1 square grid and a line only, sqrt(3) / 2 honeycomb)
holds no ball below the wall. A ball would show as a point of it that the recipe of section 1.1 calls INSIDE. So:
random points of the half spindle under the wall (a third of them within a thousandth of its skin, a third close to
the line and the two fixed points), the recipe with 300 rounds (the truth checker's numpy writing, tkit.recipe, which
does not know of any hull or room). This test does not depend on how fine a list of balls is.
As a control the same with a spindle 1.5 times as wide: there the recipe must find points INSIDE, or the test is blind.
MINE: the test and the settings (108: nine second spheres from 50 down to 2 %, four sizes each, three grids).
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'truth', 'mk'))
import tkit as T

LOG = os.path.join(FINAL, 'logs', 'side7.txt'); out = []


def say(s=''):
    print(s, flush=True); out.append(s)
    open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')


def spindle_points(rng, n, top, rho, w, nvec):
    c2 = max(0.25 - rho * rho, 0.0); a = (w * w - c2) / (2 * w); R = (w * w + c2) / (2 * w)
    k = n // 3
    # 1: anywhere in it   2: within a thousandth (of R) of its skin   3: close to the line (and so to the fixed points)
    ang = rng.uniform(0, 2 * np.pi, n); rad = R * np.sqrt(rng.random(n))
    rad[k:2 * k] = R * (1 - 10 ** rng.uniform(-7, -3, k))
    v = rad * np.cos(ang); q = a + rad * np.sin(ang)
    v[2 * k:] = rng.uniform(-1, 1, n - 2 * k) * np.sqrt(c2) * (1 + 1e-3) if c2 > 0 else rng.normal(0, 1e-3, n - 2 * k)
    q[2 * k:] = 10 ** rng.uniform(-9, np.log10(max(w, 1e-8)), n - 2 * k)
    ok = (q > 0) & (v * v + (q - a) ** 2 < R * R)
    v, q = v[ok], q[ok]
    th = rng.uniform(0, np.pi, v.size)
    across = q * np.cos(th); depth = q * np.sin(th)
    nx, ny = nvec; px, py = -ny, nx
    x = 0.5 * nx + v * nx + across * px; y = 0.5 * ny + v * ny + across * py; z = top - depth
    keep = z > 0
    return x[keep], y[keep], z[keep]


if __name__ == '__main__':
    rng = np.random.default_rng(71120)
    say('The side spindle against the plain recipe (300 rounds). INSIDE = a ball reaches into it. Points per setting: about 60000.')
    say('')
    bad = 0; n_set = 0; n_pts = 0; blind = 0; ctl = 0; t0 = time.time()
    for gname, D, nvecs in (('square', 1.0, [(1.0, 0.0), (0.0, 1.0)]), ('hex', np.sqrt(3) / 2, [(1.0, 0.0), (0.5, np.sqrt(3) / 2), (-0.5, np.sqrt(3) / 2)]), ('line', 1.0, [(1.0, 0.0)])):
        grid = T.Grid(gname)
        for rho in (0.5, 0.499, 0.49, 0.45, 0.4, 0.3, 0.2, 0.1, 0.02):
            for f in (0.1, 0.5, 0.9, 1.0):
                p = f * 100.0 / rho; top = T.top_of(p); HB = T.hulls(top, rho)['HB']
                w = min(top - HB, D - rho)
                res = []
                for wide in (1.0, 1.5):
                    ins = und = tot = 0
                    for nv in nvecs:
                        x, y, z = spindle_points(rng, 60000 // len(nvecs), top, rho, w * wide, nv)
                        st = T.recipe(x, y, z, grid, top, rho, 300)
                        ins += int((st == 1).sum()); und += int((st == -1).sum()); tot += st.size
                    res.append((ins, und, tot))
                n_set += 1; n_pts += res[0][2]; bad += res[0][0] > 0; ctl += 1; blind += res[1][0] == 0
                say('%-6s second sphere %-5g %% size %-9.4g (top %.5f, HB %.5f): w = %.5f | the spindle: %d of %d points INSIDE (%d still undecided after 300 rounds) | 1.5 times as wide: %d of %d INSIDE%s'
                    % (gname, 100 * rho, p, top, HB, w, res[0][0], res[0][2], res[0][1], res[1][0], res[1][2], '' if res[0][0] == 0 else '   <-- A BALL REACHES IN'))
        say('')
    say('%d settings, %d points of the spindle in all: a ball reaches in, in %d settings. The control (1.5 times as wide) finds points INSIDE in %d of %d settings. %.0f s'
        % (n_set, n_pts, bad, ctl - blind, ctl, time.time() - t0))
