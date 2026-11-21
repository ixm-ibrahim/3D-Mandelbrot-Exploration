"""Round 28, truth checker: my writing of the recipe against round 25's own program (out/r25/klein/tree.py), for two
equal spheres. This anchors my reading of the frame (which picture axis is which) to the source the entry was built from.
  python out/r28/final/truth/mk/j_anchor.py      -> out/r28/final/truth/logs/j_anchor.txt"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(TRUTH))))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import tkit as T
import tree as TR
import mem as M
rng = np.random.default_rng(25); lines = []
for mine, theirs in (('square', 'gauss'), ('hex', 'eisen'), ('line', 'line')):
    for t in (1.0, 1.4, 2.5):
        P = np.column_stack([rng.uniform(-1.8, 1.8, 20000), rng.uniform(-1.3, 1.3, 20000), rng.uniform(-1.3, 1.3, 20000)])
        for flat in (False, True):
            z = np.zeros(20000) if flat else P[:, 2]
            ref = M.stay(TR.tree(theirs, t=t), P[:, 0], P[:, 1], z, 0.0, 0.0, 0.0, 40) >= 40
            me = T.inside_pic(P[:, 0], P[:, 1], z, T.Grid(mine), 2 * t, 1.0, 40)
            lines.append('%-6s t %.1f %-8s: 20000 points, inside by tree.py %d, by my recipe %d, verdicts that differ %d' % (mine, t, 'flat cut' if flat else 'in space', int(ref.sum()), int(me.sum()), int((ref != me).sum())))
            print(lines[-1], flush=True)
open(os.path.join(TRUTH, 'logs', 'j_anchor.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
