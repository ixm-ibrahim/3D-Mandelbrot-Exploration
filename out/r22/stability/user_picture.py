"""The picture for the user. python out/r22/stability/user_picture.py -> out/r22/stability/keeps-shapes.png
Two rules (Turning plane, along; Sphere inversions, one plane), the c = -1 shape. Two cuts across the x-axis per rule
(through the middle body; through the buds of the body to its left), coloured by what ONE step does to a tiny ball at
each place, with the shape's outline on top, and the shape itself from the side. Only the user's words on it."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import stab as T, zones as Z
M = T.M

C = T.BAS; PW = 470; SW, SH = 520, 470; pad = 16
COL = Z.COL
ROWS = [('along', 'Turning plane, along',
         ['Round buds that carry many small buds of their own sit only in the green stripes: on the flat page and on the upright page.',
          'In the purple the step turns things inside out. The buds there come out nearly bare (middle body) or as thin leaning seeds (left body).',
          'The left body has 4 round buds and 12 seeds round it. Seeds on seeds get thinner each time (3, then 7, then 19 times as long as thick): the thin fins.']),
        ('oneplane', 'Sphere inversions, one plane',
         ['No purple: this rule never turns anything inside out. And no seeds: its skin is clean.',
          'But on each circle round the x-axis only two places land inside the next body: the two on the flat page. Two round buds, and nothing else.',
          'Above and below the flat page the step squeezes more and more (yellow, orange): it keeps shapes only near the flat page.'])]
CUTS = [('Cut through the middle body', ('across', 0.0), 0.85), ('Cut through the buds of the body to its left', ('across', -1.0463), 0.5)]


def swatch(d, x, y, col, text, f):
    d.rectangle([x, y + 3, x + 30, y + 23], fill=tuple(int(v) for v in col), outline=(255, 255, 255))
    d.text((x + 40, y), text, fill=(225, 228, 236), font=f)


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(32), M.font(23), M.font(18), M.font(16)
    W = pad + 2 * (PW + pad) + SW + pad
    rowh = 34 + 24 + PW + 10 + 3 * 26 + 30
    H = 292 + len(ROWS) * rowh + 10
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Where a step keeps shapes, the buds are round', fill=(240, 240, 245), font=f_t)
    y = 62
    for line in ['A bud is a place whose points jump, in one step or a few, into a body that is already there. So a bud is that body seen through the step.',
                 'If the step keeps shapes at that place, the bud comes out round like the body. If the step squeezes, the bud comes out squeezed.',
                 'The colours say what ONE step (square, then add c) does to a tiny ball at each place. The white line is the outline of the c = -1 shape;',
                 'bright colour is inside it. The cuts look along the x-axis: the flat page is the level line through the middle, the upright page stands on it.']:
        d.text((pad, y), line, fill=(175, 182, 196), font=f_c); y += 25
    y += 10
    swatch(d, pad, y, COL[0], 'keeps shapes: a tiny ball comes out as a ball', f_c)
    swatch(d, pad + 560, y, COL[3], 'turns inside out: a right-hand glove comes out as a left-hand glove', f_c); y += 32
    swatch(d, pad, y, COL[1], 'squeezes: a tiny ball comes out as an egg', f_c)
    swatch(d, pad + 560, y, COL[2], 'squeezes hard: a tiny ball comes out more than three times as long as thick', f_c); y += 32
    d.text((pad, y), 'The stripes are the same for every c. Only the white outline changes with c.', fill=(175, 182, 196), font=f_c)
    y = 292
    for name, head, caps in ROWS:
        r = M.bench(name)
        d.text((pad, y), head, fill=(240, 222, 160), font=f_h); y += 34
        xs = [pad, pad + PW + pad, pad + 2 * (PW + pad)]
        for (lab, kind, L), xx in zip(CUTS, xs[:2]):
            d.text((xx, y), lab, fill=(160, 168, 182), font=f_s)
        d.text((xs[2], y), 'The shape this rule makes, from the side', fill=(160, 168, 182), font=f_s); y += 24
        for (lab, kind, L), xx in zip(CUTS, xs[:2]):
            img, cat, ins = Z.tile(name, kind, C, PW, L, 150)
            im.paste(Image.fromarray(img), (xx, y))
            d.line([xx, y + PW // 2, xx + 22, y + PW // 2], fill=(255, 255, 255), width=2); d.line([xx + PW - 22, y + PW // 2, xx + PW, y + PW // 2], fill=(255, 255, 255), width=2)
            d.text((xx + 6, y + PW - 24), 'level line = the flat page, seen edge-on', fill=(235, 238, 244), font=f_s)
            print(name, lab, 'inside %d px' % ins.sum(), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        dep, px = M.solid(r, C, SW, SH, 300, 40, centre=(-0.35, 0.0, 0.0), half_w=1.3, cam=(0.75, 0.45, 1.0))
        im.paste(Image.fromarray(M.shade_solid(dep, px)), (xs[2], y)); y += PW + 10
        for cap in caps:
            d.text((pad, y), cap, fill=(218, 221, 229), font=f_c); y += 26
        y += 30
        print(name, 'drawn', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y - 10)); out = os.path.join(T.HERE, 'keeps-shapes.png'); im.save(out); print(out, im.size)


if __name__ == '__main__':
    main()
