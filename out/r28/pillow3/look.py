"""Round 28, pillow3: pictures of a block solid from several eyes, side by side.

    python out/r28/pillow3/look.py <tag> <h> <out.png> [half_w] [eyes: comma list of names] [centre x,y,z]

Eyes. In every one of them the row of bodies (the x-axis) runs left to right, +x to the right.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox
M = vox.M
Y, Z = (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
EYES = {'above': ((0.3, 0.45, 1.0), Y, 'eye above the flat picture (the flat picture faces the eye)'),
        'front': ((0.0, 0.0, 1.0), Y, 'eye straight above the flat picture'),
        'side': ((0.3, -1.0, 0.4), Z, 'eye in front of the row and a little above: the flat picture lies level'),
        'edge': ((0.0, -1.0, 0.0), Z, 'eye in the flat plane: the flat picture is the level line through the middle'),
        'low': ((0.3, -1.0, -0.4), Z, 'eye in front of the row and a little below'),
        'left': ((-1.0, -0.5, 0.35), Z, 'eye near the left end of the row'),
        'right': ((1.0, -0.5, 0.35), Z, 'eye near the right end of the row'),
        'endl': ((-1.0, 0.0, 0.0), Z, 'eye on the x-axis, at the left end, looking along the row'),
        'endr': ((1.0, 0.0, 0.0), Z, 'eye on the x-axis, at the right end, looking along the row')}


def sheet(tag, h, path, half_w=1.75, eyes=('above', 'side'), w=900, hgt=680, title=None, centre=(0.0, 0.0, 0.0), flip=False):
    ins, ax, _, _ = vox.grid(tag, h); pad = 8
    if flip:
        ins = ins[:, ::-1]                                  # the mirror image in the upright plane through the x-axis
    im = Image.new('RGB', (pad + len(eyes) * (w + pad), hgt + 40), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), title or '%s, blocks of side %g' % (tag, h), fill=(240, 240, 245), font=M.font(20))
    for i, e in enumerate(eyes):
        cam, up, nm = EYES[e]; x = pad + i * (w + pad)
        dep, px = vox.depth_map(ins, ax, cam, w=w, hgt=hgt, half_w=half_w, centre=centre, up=up)
        im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, 36)); d.text((x + 6, 40), nm, fill=(150, 160, 175), font=M.font(14))
    im.save(path); print('wrote', path, im.size)


if __name__ == '__main__':
    a = sys.argv
    sheet(a[1], float(a[2]), os.path.join(HERE, a[3]), float(a[4]) if len(a) > 4 else 1.75, tuple(a[5].split(',')) if len(a) > 5 else ('above', 'side'),
          centre=tuple(float(t) for t in a[6].split(',')) if len(a) > 6 else (0.0, 0.0, 0.0))
