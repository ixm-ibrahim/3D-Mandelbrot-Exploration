"""A finer look at the nearest thing of this section, the skew pillow (200 blocks deep, 40 steps), and its weak side.

    python out/r25/pillow/closer.py job <n>     n = 0..3, one solid each, kept in cache/
    python out/r25/pillow/closer.py make        closer.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import best as B
M = P.M

MIRROR_RABBIT = (M.RABBIT[0], -M.RABBIT[1], 0.0)
JOBS = [
    ('skew', 'c = -1, from the front', (-1.0, 0.0, 0.0), (0.45, 0.5, 1.0), 400, 300, 200, 40),
    ('skew', 'c = -1, from the side (below the flat picture is up)', (-1.0, 0.0, 0.0), (0.2, 1.0, 0.35), 400, 300, 200, 40),
    ('skew', 'rabbit, from the front', M.RABBIT, (0.45, 0.5, 1.0), 400, 300, 200, 40),
    ('skew', 'the mirror-image rabbit, from the front', MIRROR_RABBIT, (0.45, 0.5, 1.0), 400, 300, 140, 40),
]
CACHE = os.path.join(HERE, 'cache')


def job(n):
    key, label, c, cam, w, h, nd, steps = JOBS[n]; t0 = time.time()
    dep, px = M.solid(B.rule(key), c, w, h, nd, steps, cam=cam)
    np.savez_compressed(os.path.join(CACHE, 'closer-%d.npz' % n), dep=dep, px=px); print('closer', n, '%.0f s' % (time.time() - t0))


def make():
    pad = 10; w, h = 400, 300
    im = Image.new('RGB', (pad + 2 * (w + pad), 46 + 2 * (h + 30)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Skew pillow, finer blocks (200 deep, 40 steps)', fill=(240, 240, 245), font=M.font(21))
    for n, (key, label, c, cam, w_, h_, nd, steps) in enumerate(JOBS):
        x = pad + (n % 2) * (w + pad); y = 46 + (n // 2) * (h + 30); path = os.path.join(CACHE, 'closer-%d.npz' % n)
        d.text((x, y), label, fill=(235, 220, 170), font=M.font(15))
        if os.path.exists(path):
            z = np.load(path); im.paste(Image.fromarray(M.shade_solid(z['dep'], float(z['px']))), (x, y + 22))
    im.save(os.path.join(HERE, 'closer.png')); print('wrote closer.png', im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'job':
        job(int(sys.argv[2]))
    else:
        make()
