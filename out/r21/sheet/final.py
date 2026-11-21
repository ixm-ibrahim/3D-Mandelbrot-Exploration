"""A harder look at one rule (default evc005e70k16) next to the one-plane rule.

    python out/r21/sheet/final.py [name]     -> final-<name>.png
Row 1, 2: Julia sets for c just off the x-axis (where c's vote is weak), rough solids and cuts across the x-axis.
Row 3:    the Mandelbrot solid cut along sheets that are NOT mirror planes (11.25, 33.75, 67.5, 78.75) and across at x = -1 and -0.5.
Row 4:    the Mandelbrot solid from four eye positions at 40 steps.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

NEAR = [('c = -1 + 0.03i', (-1.0, 0.03, 0.0)), ('c = -1 + 0.1i', (-1.0, 0.1, 0.0)), ('c = -0.75 + 0.1i', (-0.75, 0.1, 0.0)), ('c = -0.6 + 0.4i', (-0.6, 0.4, 0.0))]


def main(name):
    rules = [R.get('oneplane'), R.get(name)]; w, h, nd, s = 300, 225, 170, 225; pad = 8; t0 = time.time()
    W = pad + 6 * (w + pad); H = 44 + 2 * (2 * (h + 26)) + 2 * (h + 46) + 40
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'A harder look: %s (%s) next to the one-plane rule' % (name, rules[1].label), fill=(240, 240, 245), font=M.font(17)); y = 44
    for r in rules:
        d.text((pad, y), '%s: Julia sets for c just off the x-axis, 60 steps (solid) and the cut across the x-axis at x = 0' % r.name, fill=(235, 220, 170), font=M.font(14)); y += 22
        x = pad
        for nm, c in NEAR[:3]:
            dep, px = M.solid(r, c, w, h, nd, 60); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y)); d.text((x + 4, y + 2), nm, fill=(150, 160, 175), font=M.font(12)); x += w + pad
            n = M.cut_across(r, 0.0, h, 80, c=c, L=1.0); im.paste(Image.fromarray(M.shade(n, 80)), (x, y)); x += h + pad
        y += h + 8; print(r.name, 'julia', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    r = rules[1]
    d.text((pad, y), '%s: the Mandelbrot solid cut along sheets turned 11.25, 33.75, 67.5, 78.75 degrees, and across the x-axis at x = -1 and x = -0.5 (80 steps)' % r.name, fill=(235, 220, 170), font=M.font(14)); y += 22
    x = pad
    for a in (11.25, 33.75, 67.5, 78.75):
        n = M.cut_axis(r, a, w, h, 80); im.paste(Image.fromarray(M.shade(n, 80)), (x, y)); d.text((x + 4, y + 2), 'along %g' % a, fill=(150, 160, 175), font=M.font(12)); x += w + pad
    for x0 in (-1.0, -0.5):
        n = M.cut_across(r, x0, h, 80, L=1.0); im.paste(Image.fromarray(M.shade(n, 80)), (x, y)); d.text((x + 4, y + 2), 'across, x = %g' % x0, fill=(150, 160, 175), font=M.font(12)); x += h + pad
    y += h + 8; print('cuts', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    d.text((pad, y), '%s: the Mandelbrot solid, 40 steps, from four eye positions' % r.name, fill=(235, 220, 170), font=M.font(14)); y += 22
    x = pad
    for cam, cn in (((0.45, 0.5, 1.0), 'front, a little above'), ((0.0, 0.0, 1.0), 'straight at the flat page'), ((0.0, 1.0, 0.02), 'from above (down the y-axis)'), ((1.0, 0.3, 0.3), 'along the x-axis')):
        dep, px = M.solid(r, None, w + 60, h + 45, nd, 40, cam=cam); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y)); d.text((x + 4, y + 2), cn, fill=(150, 160, 175), font=M.font(12)); x += w + 60 + pad
        print(cn, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y + h + 45 + 8)); im.save(os.path.join(HERE, 'final-%s.png' % name))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'evc005e70k16')
