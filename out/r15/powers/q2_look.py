import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import viz
keys = sys.argv[1].split(',')
rows, rt = [], []
for key in keys:
    for h in (0.3, 0.075, 0.02):
        f = os.path.join(HERE, 'data', 'q2-zoom-%s-%g.npz' % (key, h))
        if not os.path.exists(f): continue
        D = np.load(f); v = D['inside']
        r = [viz.view(v, 'front'), viz.view(v, 'above'), viz.view(v, 'alongy'), viz.view(v, 'alongx')]
        for pl in ('xz', 'yz'):
            C = np.load(os.path.join(HERE, 'data', 'q2-cut-%s-%s-%g.npz' % (key, pl, h)))
            r.append(viz.cut2d(C['inside'], C['death']))
        rows.append(r); rt.append('%s\nhalf %g' % (key, h))
p = viz.sheet(rows, ['front', 'above', 'along y', 'along x', 'upright cut (x, z)', 'upright cut (y, z)'], rt, os.path.join(HERE, 'look-q2-%s.png' % '-'.join(keys)), cell=260, left=120)
print(p)
