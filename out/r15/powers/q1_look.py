"""Working sheets for question 1: every solid from six sides and three cuts.  python q1_look.py N"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import viz
N = int(sys.argv[1])
names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['m2', 'm3', 'm4', 'm5', 'j2', 'j3', 'j4', 'j5']
cols = ['front', 'above (looking down)', 'below (looking up)', 'along the x-axis', 'along the y-axis', 'cut z = 0', 'cut y = 0', 'cut x = centre']
rows, rt = [], []
for nm in names:
    D = np.load(os.path.join(HERE, 'data', 'q1-%s-%d.npz' % (nm, N)))
    v, d = D['inside'], D['death']
    rows.append([viz.view(v, 'front'), viz.view(v, 'above'), viz.view(v, 'below'), viz.view(v, 'alongx'), viz.view(v, 'alongy'),
                 viz.cut(v, d, 'z'), viz.cut(v, d, 'y'), viz.cut(v, d, 'x')])
    rt.append('%s\npower %d\nbox half %.2f' % (nm, int(D['n']), float(D['L'])))
p = viz.sheet(rows, cols, rt, os.path.join(HERE, 'look-q1-%d-%s.png' % (N, '-'.join(names) if len(names) < 8 else 'all')), cell=260, left=120)
print('wrote', p)
