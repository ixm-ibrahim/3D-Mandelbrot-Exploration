"""Judge, round 25: the pictures. Real shapes only; captions say what a person sees (two short sentences at most).

    python out/r25/judge/compose.py            the three pictures for the user and the judge's own working sheets
"""
import os, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl, draw as D
M = jl.M
EYE = {'a': 'seen from the front', 'top': 'seen from above', 'under': 'seen from behind'}


def sheet(path, title, cols, foot=None):
    """cols = [(heading, [spec, ...], caption)]; a spec is 'rule:set:tilt:eye' or (spec, corner label)."""
    w, h, pad = D.W, D.Hh, 12; nrow = max(len(c[1]) for c in cols)
    fh, fc, fs, ft = M.font(19), M.font(16), M.font(13), M.font(24)
    wrap = int(w / 8.3); caps = [textwrap.wrap(c[2], wrap) for c in cols]; ncap = max(len(t) for t in caps)
    heads = [textwrap.wrap(c[0], int(w / 9.6)) for c in cols]; nhead = max(len(t) for t in heads)
    top = 56; y0 = top + nhead * 24 + 6
    W = pad + len(cols) * (w + pad); H = y0 + nrow * (h + pad) + ncap * 21 + 14 + (30 if foot else 0)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 12), title, fill=(240, 240, 245), font=ft)
    for j, (head, specs, cap) in enumerate(cols):
        x = pad + j * (w + pad)
        for i, line in enumerate(heads[j]):
            d.text((x, top + i * 24), line, fill=(235, 220, 170), font=fh)
        for i, sp in enumerate(specs):
            sp, lab = sp if isinstance(sp, tuple) else (sp, EYE[sp.split(':')[3]])
            y = y0 + i * (h + pad)
            if not os.path.exists(D.path(sp)):
                d.rectangle([x, y, x + w, y + h], outline=(80, 80, 90)); d.text((x + 10, y + 10), 'not drawn yet: ' + sp, fill=(200, 120, 120), font=fs); continue
            dep, px = D.panel(sp); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y)); d.text((x + 8, y + 6), lab, fill=(150, 160, 175), font=fs)
        yc = y0 + nrow * (h + pad) + 2
        for i, line in enumerate(caps[j]):
            d.text((x, yc + i * 21), line, fill=(215, 218, 225), font=fc)
    if foot:
        d.text((pad, H - 30), foot, fill=(150, 160, 175), font=fs)
    im.save(path); print('saved', path, im.size)


def user_pictures():
    sheet(os.path.join(HERE, '1-c-minus-1.png'), 'c = -1: the two favourites, and the two nearest new tries of this round', [
        ('two planes', ['twoplane:c1:0:a', 'twoplane:c1:0:top'],
         'Round bodies in a row, with buds in four directions round each body.'),
        ('along', ['along:c1:0:a', 'along:c1:0:top'],
         'Round bodies in a row, with round buds all round each body.'),
        ('new: bulbs spaced evenly all over', ['skew:c1:0:a', 'skew:c1:0:top'],
         'Bodies stay apart and carry smaller bodies with buds of their own. But those are long eggs, they sit on one side only, and the skin has thorns.'),
        ('new: the rule looks at where the bodies meet', ['twin_tri:c1:0:a', 'twin_tri:c1:0:top'],
         'The same row of round bodies as with one plane. Off the flat picture it grows only thorns and scratches.'),
    ], foot='Real shapes, rough blocks (280 deep, 40 steps). The flat picture is exact in all four.')
    sheet(os.path.join(HERE, '2-rabbit.png'), 'The rabbit: "along once", and the same two new tries', [
        ('along once', ['alongonce:rabbit:0:a', 'alongonce:rabbit:0:top'],
         'Three clean bodies round the meeting point, with a few extra bodies standing on them.'),
        ('new: bulbs spaced evenly all over', ['skew:rabbit:0:a', 'skew:rabbit:0:top'],
         'The bodies break up into rough small lumps with loose crumbs round them. No clean round body is left.'),
        ('the same rule, the mirror-image rabbit',['skew:rabbit-mirror:0:a', 'skew:rabbit-mirror:0:top'],
         'One swollen lump. The flat picture is only mirrored, but the shape is a different one.'),
        ('new: the rule looks at where the bodies meet', ['twin_tri:rabbit:0:a', 'twin_tri:rabbit:0:top'],
         'The rabbit\'s bodies stay apart and blown up, but the skin is scratched and loose flakes float round it. Nothing new grows off the flat picture.'),
    ], foot='Real shapes, rough blocks (280 deep, 40 steps). The flat picture is exact in all four.')
    sheet(os.path.join(HERE, '3-bulbs-all-over.png'), 'Where bulbs do come all over by themselves, and what each one gives up', [
        ('sphere inversions only: no c, not the flat picture', ['pearl:none:0:a', 'pearl:none:0:top'],
         'Perfect balls on balls on balls, all over, nothing stretched. But its flat cut is a chain of circles, not the flat picture of c = -1.'),
        ('the power 3 (z^3 + c, c = i), one plane', ['oneplane3:ci:0:a', 'oneplane3:ci:0:top'],
         'For comparison: the blown-up flat picture of the power 3, with buds only round the flat picture.'),
        ('the power 3, bulbs spaced evenly all over', ['cube:ci:0:a', 'cube:ci:0:top'],
         'A blown-up body with smaller bodies on it in many directions. They are long and thorny, and the three arms no longer match each other.'),
    ], foot='Real shapes, rough blocks. Left: 14 rounds of the group. Middle and right: 280 deep, 40 steps, flat picture exact.')


def working():
    sheet(os.path.join(HERE, 'w-tilt.png'), 'Judge: c lifted 3 degrees out of the flat plane (front eye)', [
        ('two planes, c = -1', ['twoplane:c1:0:a', 'twoplane:c1:3:a'], 'Top: c in the flat plane. Bottom: lifted.'),
        ('along, c = -1', ['along:c1:0:a', 'along:c1:3:a'], ''),
        ('skew pillow, c = -1', ['skew:c1:0:a', 'skew:c1:3:a'], ''),
        ('twin_tri, rabbit', ['twin_tri:rabbit:0:a', 'twin_tri:rabbit:3:a'], ''),
        ('even cube, c = i', ['cube:ci:0:a', 'cube:ci:3:a'], ''),
    ])
    sheet(os.path.join(HERE, 'w-cube.png'), 'Judge: the power 3 on the two even patterns (front, above)', [
        ('one plane, c = i', ['oneplane3:ci:0:a', 'oneplane3:ci:0:top'], ''),
        ('four special spots (wall), c = i', ['cube:ci:0:a', 'cube:ci:0:top'], ''),
        ('three special spots (judge probe), c = i', ['tri3:ci:0:a', 'tri3:ci:0:top'], ''),
        ('four spots, three-bodied c', ['cube:c3b:0:a', 'tri3:c3b:0:top'], 'bottom panel: three spots, from above'),
        ('three spots, three-bodied c', ['tri3:c3b:0:a', 'skew:c1:0:under'], 'bottom panel: skew pillow c = -1 from behind'),
    ])


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('all', 'user'):
        user_pictures()
    if which in ('all', 'work'):
        working()
