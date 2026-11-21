"""Round 27, respace: the sheets, put together from the kept solids (depth-*.npz).

    python compose27.py     -> carried-c-1.png, carried-ways.png, carried-rabbit.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw
import carry as C
M = C.M
HERE = os.path.dirname(os.path.abspath(__file__))


def tile(tag, w, h):
    f = os.path.join(HERE, 'depth-%s.npz' % tag)
    if not os.path.exists(f):
        return None
    d = np.load(f); im = Image.fromarray(M.shade_solid(d['depth'], float(d['px'])))
    return im.resize((w, h), Image.LANCZOS) if im.size != (w, h) else im


def sheet(name, title, cells, w=560, h=420, cols=3):
    pad = 10; rows = (len(cells) + cols - 1) // cols
    im = Image.new('RGB', (pad + cols * (w + pad), 46 + rows * (h + 50)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(240, 240, 245), font=M.font(21))
    for i, (tag, cap) in enumerate(cells):
        x = pad + (i % cols) * (w + pad); y = 46 + (i // cols) * (h + 50); t = tile(tag, w, h)
        if t is not None:
            im.paste(t, (x, y))
        else:
            d.text((x + 10, y + 10), 'not drawn: ' + tag, fill=(200, 120, 120), font=M.font(14))
        for j, line in enumerate(cap.split('\n')):
            d.text((x + 2, y + h + 4 + 20 * j), line, fill=(200, 205, 215), font=M.font(15))
    im.save(os.path.join(HERE, name)); print('wrote', name, im.size)


if __name__ == '__main__':
    sheet('carried-c-1.png', 'c = -1: the balls object, and the same bulbs carried onto the true flat picture', [
        ('b-T-a', 'The balls object as it is. Every body is an exact ball;\nits flat cut is a chain of circles.'),
        ('b-A-a', 'Carried over, from the front. The flat cut is now the true\nflat picture; the big bulbs stay round.'),
        ('b-A-top', 'The same from above. A fringe of thorns runs round\nthe outline of the flat picture.')])
    sheet('carried-ways.png', 'c = -1: three more ways of carrying it over (all keep the flat cut exact)', [
        ('b-B-a', 'Buds moved from the fractions to the halvings all round\neach body: the bulbs are pressed flat.'),
        ('b-C-a', 'The same move in the flat directions only:\nbulbs smeared sideways.'),
        ('b-F-a', 'A fitted sphere inversion at every point: bulbs round,\nbut fins shoot up wherever a rim bends inward.')], w=400, h=300)
    sheet('carried-rabbit.png', 'The rabbit: the same carry-over (the flat cut is the true rabbit)', [
        ('r-A-a', 'From the front.'), ('r-A-top', 'From above.'), ('r-B-a', 'With the buds moved to the halvings: pressed flat.')])
