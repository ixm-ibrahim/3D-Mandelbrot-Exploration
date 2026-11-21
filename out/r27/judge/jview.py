"""Judge: working pictures of the kept solids. python jview.py name-eye [name-eye ...]  -> w-<name>-<eye>.png (side by side if several)"""
import os, sys
import numpy as np
from PIL import Image
import jlib as J


def tile(tag, size=None):
    d = np.load(os.path.join(J.HERE, 'cache', 'depth-%s.npz' % tag)); im = Image.fromarray(J.shade(d['depth'], float(d['px'])))
    return im.resize(size, Image.LANCZOS) if size else im


if __name__ == '__main__':
    tags = sys.argv[1:]; ims = [tile(t) for t in tags]
    W = sum(i.size[0] for i in ims) + 8 * (len(ims) - 1); H = max(i.size[1] for i in ims)
    out = Image.new('RGB', (W, H), (12, 14, 20)); x = 0
    for i in ims:
        out.paste(i, (x, 0)); x += i.size[0] + 8
    p = os.path.join(J.HERE, 'w-%s.png' % '+'.join(tags)); out.save(p); print('wrote', p, out.size)
