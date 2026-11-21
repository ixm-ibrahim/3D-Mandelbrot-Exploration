"""python out/r21/frame/sheet.py julia|mandel <tag> name1 name2 ...  [w=300] [nd=180] [steps=28] [cam=0.45,0.5,1]
Names: my rules (myrules.BY) or bench names with a leading '@' (e.g. @along)."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
import myrules as R
np.seterr(all='ignore')

kind, tag = sys.argv[1], sys.argv[2]
opts = dict(a.split('=') for a in sys.argv[3:] if '=' in a); names = [a for a in sys.argv[3:] if '=' not in a]
rs = [M.bench(n[1:]) if n.startswith('@') else R.BY[n] for n in names]
w = int(opts.get('w', 300)); nd = int(opts.get('nd', 180)); cam = tuple(float(t) for t in opts.get('cam', '0.45,0.5,1').split(','))
t0 = time.time()
if kind == 'julia':
    steps = int(opts.get('steps', 28))
    p = M.julia_sheet(rs, os.path.join(HERE, 'julia-%s.png' % tag), w=w, h=int(w * 0.75), nd=nd, steps=steps, cam=cam)
else:
    steps = int(opts.get('steps', 22))
    p = M.mandel_sheet(rs, os.path.join(HERE, 'mandel-%s.png' % tag), w=w, cw=int(opts.get('cw', 240)), ch=int(opts.get('ch', 224)), nd=nd, steps=steps, cam=cam,
                       angles=(0.0, 11.25, 22.5, 45.0, 90.0))
print('wrote', p, '%.0f s' % (time.time() - t0))
