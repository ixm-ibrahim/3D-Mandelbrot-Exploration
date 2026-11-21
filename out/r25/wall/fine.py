"""One finer look at the cleanest case (the evenly spaced cube at c = i), to see whether the bulbs hold up.

    python out/r25/wall/fine.py [a|top]        -> cube-i-fine-<eye>.png   (560 x 420, 300 blocks deep, 40 steps)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import best
M = best.M

if __name__ == '__main__':
    eye = sys.argv[1] if len(sys.argv) > 1 else 'a'; cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[eye]
    t0 = time.time(); w, h, nd, steps = 560, 420, 300, 40
    dep, px = M.solid(best.rule(), (0.0, 1.0, 0.0), w, h, nd, steps, cam=cam, half_w=1.6)
    im = Image.fromarray(M.shade_solid(dep, px)); d = ImageDraw.Draw(im)
    d.text((8, 6), 'Evenly spaced cube, z^3 + c, c = i, %s (finer blocks, %d steps)' % ('from the front' if eye == 'a' else 'from above', steps), fill=(235, 220, 170), font=M.font(15))
    p = os.path.join(HERE, 'cube-i-fine-%s.png' % eye); im.save(p); print('wrote', p, '%.0f s' % (time.time() - t0), int(np.isfinite(dep).sum()), 'pixels hit')
