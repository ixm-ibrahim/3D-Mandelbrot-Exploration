"""Round 27, entry, step 1: the page's JavaScript twin (ballsInside) against out/r25/klein/tree.py.
  python out/r27/fix/mk/twin_check.py      -> out/r27/fix/logs/twin-check.txt
Runs mk/twin.js in the page (20000 random points of the box -1.8..1.8, -1.3..1.3, -1.3..1.3; each setting once in
the flat cut z = 0 and once in space), then asks tree.py for the same points with the same number of rounds."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ENTRY = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(ENTRY)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import run
import tree as T
import mem as M

LAT = {'square': 'gauss', 'hex': 'eisen', 'line': 'line'}


def verdict(grid, t, x, y, z, rounds):
    return M.stay(T.tree(LAT[grid], t=t), x, y, z, 0.0, 0.0, 0.0, rounds) >= rounds


if __name__ == '__main__':
    page = sys.argv[1] if len(sys.argv) > 1 else run.PAGE
    code, val = run.js(os.path.join(HERE, 'twin.js'), 'twin', page, quiet=True)
    d = json.loads(val); P = np.array(d['pts']); lines = ['page %s, exit %d, %d points' % (page, code, d['n'])]; bad = 0
    for c in d['cases']:
        mine = np.array([ch == '1' for ch in c['bits']])
        ref = verdict(c['grid'], c['t'], P[:, 0], P[:, 1], np.zeros(len(P)) if c['flat'] else P[:, 2], 40)
        n = int((mine != ref).sum()); bad += n
        lines.append('%-6s t = %-4s %-9s inside (twin) %5d, inside (tree.py) %5d, verdicts that differ: %d' % (c['grid'], c['t'], 'flat cut' if c['flat'] else 'in space', int(mine.sum()), int(ref.sum()), n))
    lines.append('TOTAL verdicts that differ: %d of %d' % (bad, len(d['cases']) * d['n']))
    text = '\n'.join(lines) + '\n'
    run.write('twin-check.txt', text); print(text)
