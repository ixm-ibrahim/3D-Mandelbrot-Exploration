"""Solids. python render.py <object name> <eye a|top|end> [w h nd]   -> depth-<name>-<eye>.npz and solid-<name>-<eye>.png
The solid is the library's kind (first block on each line of sight that is inside), shaded by the library."""
import sys, time
import numpy as np
from PIL import Image
import pinchlib as PL, objs

EYES = dict(PL.EYES); EYES['end'] = (1.0, 0.25, 0.3)
name, eye = sys.argv[1], sys.argv[2]
w, h, nd = (int(v) for v in sys.argv[3:6]) if len(sys.argv) > 5 else (440, 330, 200)
t0 = time.time(); B = objs.get(name)
depth, px = PL.solid(B, w, h, nd, EYES[eye])
np.savez_compressed(PL.os.path.join(PL.HERE, 'depth-%s-%s.npz' % (name, eye)), depth=depth, px=px)
Image.fromarray(PL.M.shade_solid(depth, px)).save(PL.os.path.join(PL.HERE, 'solid-%s-%s.png' % (name, eye)))
print('%s eye %s: %d bodies, %d x %d x %d blocks, %.0f s' % (name, eye, len(B), w, h, nd, time.time() - t0))
