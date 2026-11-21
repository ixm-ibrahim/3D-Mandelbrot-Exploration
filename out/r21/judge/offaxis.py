"""c just off the x-axis, still in the flat page and still inside the flat Mandelbrot set: does the Julia set change
gently as c leaves the x-axis?  For each rule and each c: the cut along the upright sheet (90 degrees), the cut across
the x-axis at x = 0 (both 80 steps), and the rough solid from the two eye positions (60 steps).

    python out/r21/judge/offaxis.py a      c = -1 + 0.03i and -1 + 0.1i   -> offaxis-a.png
    python out/r21/judge/offaxis.py b      c = -1 + 0.2i and -0.6 + 0.2i  -> offaxis-b.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
SETS = {'a': [('c = -1 + 0.03i', (-1.0, 0.03, 0.0)), ('c = -1 + 0.1i', (-1.0, 0.1, 0.0))],
        'b': [('c = -1 + 0.2i', (-1.0, 0.2, 0.0)), ('c = -0.6 + 0.2i (inside the heart)', (-0.6, 0.2, 0.0))]}
NAMES = ['along', 'oneplane', 'sheet.evc005e70k16', 'alongmem.c_wake1']
CW, CH, A, SW, SH, ND = 240, 174, 174, 260, 195, 170
CAMS = ((0.45, 0.5, 1.0), (0.2, 1.0, 0.35))


def tiles(r, c):
    out = [M.shade(M.cut_axis(r, 90.0, CW, CH, 80, c=c), 80), M.shade(M.cut_across(r, 0.0, A, 80, c=c), 80)]
    for cam in CAMS:
        dep, px = M.solid(r, c, SW, SH, ND, 60, cam=cam); out.append(M.shade_solid(dep, px))
    return out


if __name__ == '__main__':
    tag = sys.argv[1]; sets = SETS[tag]; pad = 8
    heads = ['upright sheet (90 deg)', 'across at x = 0', 'solid, eye 1', 'solid, eye 2 (from above)']
    gw = CW + A + 2 * SW + 4 * pad; Wt = pad + len(sets) * (gw + 2 * pad); Ht = 50 + len(NAMES) * (SH + 44)
    im = Image.new('RGB', (Wt, Ht), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    d.text((pad, 8), 'c just off the x-axis (in the flat page, inside the flat Mandelbrot set). Cuts 80 steps, solids 60 steps.', fill=(240, 240, 245), font=M.font(20))
    for i, nm in enumerate(NAMES):
        r = J.get(nm); y = 50 + i * (SH + 44)
        for j, (cn, c) in enumerate(sets):
            x = pad + j * (gw + 2 * pad); d.text((x, y), '%s   |   %s' % (nm, cn), fill=(235, 220, 170), font=M.font(15))
            for hd, pic in zip(heads, tiles(r, c)):
                d.text((x, y + 21), hd, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 38)); x += pic.shape[1] + pad
        print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(J.HERE, 'offaxis-%s.png' % tag))
