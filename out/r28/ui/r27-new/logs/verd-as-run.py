# copy of out/r27/final/mk/verd.py as run by out/r28/ui/mk/old27.py: 0 fixed picture path(s) changed, nothing else
"""Round 27, final, number 1: verdicts of dist/r27-final.html against out/r25/klein/tree.py (square grid, t = 1.4).
  python out/r27/final/mk/verd.py [page]    -> out/r27/final/logs/verd.txt
mk/verd.js runs in the page (the twin at 20000 + 20000 random points; the shader through sampleSlice at 20164 flat
and 20480 points in space); this script asks tree.py for the same points with the same number of rounds and counts.
Also: my own writing of the recipe from docs/ROUND27.md section 1 (numpy), as a third voice."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ENTRY = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(ENTRY)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import run
import tree as T
import mem as M

T14 = 1.4


def tree_inside(x, y, z, rounds):
    return M.stay(T.tree('gauss', t=T14), np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), 0.0, 0.0, 0.0, rounds) >= rounds


def recipe_inside(x, y, z, rounds, t=T14, k2=1.05):
    """ROUND27.md section 1, written out by me: True = inside or still undecided after the rounds."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    ux, uy, uz = y, z, x - k2 / 2
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    mx, my, mz = k2 * ux / d, k2 * uy / d, 1 + k2 * uz / d
    top = 2 * t
    state = np.zeros(x.shape, int)                                    # 0 undecided, 1 inside, 2 outside
    for _ in range(rounds):
        live = state == 0
        state = np.where(live & ((mz < 0) | (mz > top)), 1, state); live = state == 0
        mx = mx - np.round(mx); my = my - np.round(my)
        rb = mx * mx + my * my + mz * mz; rt = mx * mx + my * my + (mz - top) ** 2
        inb = live & (rb < 1); itp = live & ~inb & (rt < 1)
        state = np.where(live & ~inb & ~itp, 2, state)
        sb = 1 / np.where(rb > 0, rb, 1.0); st = 1 / np.where(rt > 0, rt, 1.0)
        mx, my, mz = (np.where(inb, mx * sb, np.where(itp, mx * st, mx)), np.where(inb, my * sb, np.where(itp, my * st, my)),
                      np.where(inb, mz * sb, np.where(itp, top + (mz - top) * st, mz)))
    return state != 2


if __name__ == '__main__':
    page = sys.argv[1] if len(sys.argv) > 1 else run.PAGE
    code, val = run.js(os.path.join(HERE, 'verd.js'), 'verd', page, '1400x950', 'dark', quiet=True)
    log = open(os.path.join(run.LOGS, 'verd.log'), encoding='utf-8').read()
    d = json.loads(val)
    o = d['asOpened']; depth = int(o['bit'])
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if run.clean(log) else 'SEE logs/verd.log'),
             'after one click on the row: mode %s, group %s, t = %s, grid %s, depth %s, status "%s"' % (o['mode'], o['group'], o['bt'], o['bgrid'], o['bit'], o['status'])]
    P = np.array(d['twin']['pts']); zero = np.zeros(len(P)); total = 0; npts = 0
    for key, flat, R in (('spaceOwnDepth', False, depth), ('flatOwnDepth', True, depth), ('space40', False, 40), ('flat40', True, 40)):
        mine = np.array([c == '1' for c in d['twin'][key]])
        z = zero if flat else P[:, 2]
        ref = tree_inside(P[:, 0], P[:, 1], z, R); me = recipe_inside(P[:, 0], P[:, 1], z, R)
        n = int((mine != ref).sum()); total += n; npts += len(P)
        lines.append('twin (ballsInside), %-8s %2d rounds: %d points, inside by the twin %d, by tree.py %d; verdicts that differ from tree.py: %d; from my own writing of the recipe: %d; tree.py against my writing: %d'
                     % ('flat cut' if flat else 'in space', R, len(P), int(mine.sum()), int(ref.sum()), n, int((mine != me).sum()), int((ref != me).sum())))
    lines.append('TWIN against tree.py: %d of %d verdicts differ' % (total, npts))
    stot = 0; sn = 0; flat_n = flat_bad = sp_n = sp_bad = 0; hair = []
    for s in d['shader']:
        n = s['n']; idx = (np.arange(n) + 0.5) / n - 0.5
        X = s['cx'] + s['side'] * idx[None, :] + np.zeros((n, 1)); Y = s['cy'] + s['side'] * idx[:, None] + np.zeros((1, n))
        x = X.ravel(); y = Y.ravel(); z = np.full(n * n, s['z'])
        box = (np.abs(x) <= 1.8) & (np.abs(y) <= 1.3)                      # the box of section 2.2; the grid square is 3.6 wide and high
        mine = np.array([c == '1' for c in s['bits']]); ref = tree_inside(x, y, z, int(s['depth']))
        bad = mine != ref; nb = int(bad.sum()); stot += nb; sn += n * n
        if s['z'] == 0:
            flat_n += n * n; flat_bad += nb
        else:
            sp_n += n * n; sp_bad += nb
        for k in np.nonzero(bad)[0]:
            hair.append((x[k], y[k], z[k], s['d'][k], bool(box[k])))
        s['inbox'] = int(box.sum()); s['bad_inbox'] = int((bad & box).sum())
    lines.append('shader (sampleSlice, depth %d), flat view: %d grid points (%d of them inside the box of 3.6 x 2.6), verdicts that differ from tree.py: %d' % (depth, flat_n, d['shader'][0]['inbox'], flat_bad))
    lines.append('shader (sampleSlice, depth %d), in space, %d heights between -1.3 and 1.3: %d grid points (%d inside the box), verdicts that differ from tree.py: %d' % (
        depth, len(d['shader']) - 1, sp_n, sum(s['inbox'] for s in d['shader'][1:]), sp_bad))
    for h in hair[:20]:
        lines.append('   differs at (%.6f, %.6f, %.6f), the shader\'s distance there %g, inside the box: %s' % h)
    lines.append('SHADER against tree.py: %d of %d verdicts differ' % (stot, sn))
    text = '\n'.join(lines) + '\n'
    run.write('verd.txt', text); print(text)
