"""Round 28, Track A, the fixer: is the estimate still SAFE with the side spindle, at the very place it was built for?

  python out/r28/fix/mk/notch.py <tag> [key ...]     -> out/r28/fix/logs/notch-<tag>.txt
  (the page: the environment's FIX_PAGE, or dist/r28-fix.html; run it with FIX_PAGE=dist/r28-dials.html and tag
   "before" for the page as the checkers had it)

One browser at a time. For each setting 20000 points are made in the object's own coordinates round the middle point
between the second sphere's centre and its copy at a next whole number (from 0.0001 to 0.7 away, under the top wall,
half of them close to the plane half-way between the two spheres), slid by a whole number and carried to the picture.
Those my recipe calls OUTSIDE at the page's depth are given to the page's own ballsEstimate (both of its numbers).
The test is the truth checker's (out/r28/truth/mk/bc_page.py, `over`): the ball of that radius about the point,
carried to the object's own space, must meet no ball of the list (tkit.build) and no wall.
Also told: at how many points twice, and ten times, the estimate would still be free (how short the estimate is).
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIX, 'truth', 'mk'))
import tkit as T
import pagerun as R
import bc_page as B

tp = lambda p: 0.5 * (100.0 / p + 1.0)
SETS = {
    'a': (0.5, 150.0, 'square', 16), 'b': (0.5, 150.0, 'hex', 16), 'c': (0.5, 150.0, 'line', 16), 'd': (0.5, 200.0, 'square', 40),
    'e': (0.5, 60.0, 'hex', 16), 'f': (0.5, 2.0, 'square', 16), 'g': (0.499, 150.0, 'square', 16), 'h': (0.49, 150.0, 'hex', 16),
    'i': (0.45, 222.0, 'square', 16), 'j': (0.4, 250.0, 'hex', 30), 'k': (1 / 3, 150.0, 'square', 16), 'l': (0.25, 400.0, 'square', 30),
    'm': (0.125, 400.0, 'line', 16), 'n': (0.05, 1000.0, 'hex', 16), 'o': (0.5, 150.0, 'square', 100), 'p': (0.5, 199.9, 'hex', 300),
}
GID = {'square': 0, 'hex': 1, 'line': 2}
N = 20000

JS = """
const J = %s;
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.k.brho = J.rho; S.k.bt = J.t; S.k.bgrid = J.g; S.k.bit = J.depth; S.flat = false; go(); await settle();
const op = { t: J.t, grid: J.g, rounds: J.depth, rho: J.rho, parts: true }, r = [];
for (let i = 0; i < J.p.length; i += 3) { const e = L.ballsEstimate(J.p[i], J.p[i + 1], J.p[i + 2], op); r.push(e[0], e[1]); }
return JSON.stringify({ sig: String(L.R.sig || '').replace(/\\n/g, '/'), k: { brho: S.k.brho, bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit }, est: r });
"""


def points(rng, grid, top, n):
    """Points of the object's own space round the middle point between the second sphere and a neighbouring copy."""
    dirs = grid.upto(1.0 + 1e-9); dirs = dirs[np.hypot(dirs[:, 0], dirs[:, 1]) > 0.5]
    nd = dirs[rng.integers(0, len(dirs), n)]                      # the next whole number (a unit vector)
    s = 10 ** rng.uniform(-4, np.log10(0.7), n)
    v = rng.normal(size=(n, 3)); v[:, 2] = -np.abs(v[:, 2])       # under the top wall
    flat = rng.random(n) < 0.5                                    # half of them close to the plane half-way between the spheres
    along = v[:, 0] * nd[:, 0] + v[:, 1] * nd[:, 1]
    damp = np.where(flat, rng.uniform(0, 0.15, n), 1.0)
    v[:, 0] -= (1 - damp) * along * nd[:, 0]; v[:, 1] -= (1 - damp) * along * nd[:, 1]
    v /= np.sqrt((v * v).sum(1))[:, None]
    return np.column_stack([0.5 * nd[:, 0] + s * v[:, 0], 0.5 * nd[:, 1] + s * v[:, 1], top + s * v[:, 2]])


def one(key, say):
    rho, p, gname, depth = SETS[key]; t = tp(p); top = 2 * t; grid = T.Grid(gname)
    rng = np.random.default_rng(2800 + ord(key))
    M = points(rng, grid, top, 4 * N)
    P = np.round(B.slid_to_picture(rng, grid, M), 10); P = P[np.sqrt((P * P).sum(1)) < 60.0]
    outp = ~T.inside_pic(P[:, 0], P[:, 1], P[:, 2], grid, top, rho, depth); P = P[outp][:N]
    t0 = time.time()
    code, text, vals = R.run(R.PAGE, [JS % json.dumps(dict(rho=rho, t=t, g=GID[gname], depth=depth, p=P.ravel().tolist()))], 'notch_' + key)
    if not vals or not vals[-1].startswith('{'):
        say('%s: THE PAGE SCRIPT GAVE NOTHING BACK (exit %d)\n%s' % (key, code, text[-800:])); return None
    d = json.loads(vals[-1]); e = np.array(d['est'], float).reshape(-1, 2); best, free = e[:, 0], e[:, 1]; E = np.minimum(best, free)
    reps, info = T.build(grid, top, rho, 2e-5 if gname == 'line' else 6e-4); ix = T.Index(reps, grid, top)
    ok = E > 0; Pn, En = P[ok], E[ok]
    hit = B.over(Pn, En, ix, top)[0]
    twice = ~B.over(Pn, 2 * En, ix, top)[0]; ten = ~B.over(Pn, 10 * En, ix, top)[0]
    line = ('%s  second sphere %-6.4g size %-7.2f %-6s depth %-3d | program %s, %s, exit %d | %d outside points (the page calls %d of %d inside) | estimate longer than the true distance to the nearest listed ball: %d | '
            '"free" the smaller number at %d | twice the estimate still free at %d, ten times at %d | list %d balls | %.0f s'
            % (key, 100 * rho, p, gname, depth, d['sig'].split('/')[0][:12], 'no console errors' if R.clean(text) else 'CONSOLE ERRORS', code, len(Pn), int((~ok).sum()), len(P), int(hit.sum()),
               int((free[ok] < best[ok]).sum()), int(twice.sum()), int(ten.sum()), info['n'], time.time() - t0))
    if hit.any():
        td = B.true_dist(Pn[hit], En[hit], ix, top); ex = En[hit] - td; k = int(np.argmax(ex))
        line += ' | TOO LONG, worst at picture (%.8f, %.8f, %.8f): estimate %.6g, true %.6g' % (*Pn[hit][k], En[hit][k], td[k])
    say(line)
    return int(hit.sum()), len(Pn), int(twice.sum()), int(ten.sum())


if __name__ == '__main__':
    tag = sys.argv[1]; keys = sys.argv[2:] or list(SETS)
    LOG = os.path.join(FIX, 'logs', 'notch-%s.txt' % tag); out = []

    def say(s):
        print(s, flush=True); out.append(s)
        open(LOG, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    say('Round 28, the fixer: ballsEstimate round the place where the second sphere meets its copy at the next whole number. Page %s.' % R.PAGE)
    tot = np.zeros(4, int)
    for k in keys:
        r = one(k, say)
        if r:
            tot += np.array(r)
    say('%d settings: estimate longer than the true distance at %d of %d points; twice the estimate still free at %d, ten times at %d.' % (len(keys), tot[0], tot[1], tot[2], tot[3]))
