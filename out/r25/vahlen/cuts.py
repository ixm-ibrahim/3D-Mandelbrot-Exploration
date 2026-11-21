"""Cuts for the section "vahlen". python out/r25/vahlen/cuts.py [tag]   tag: main | spin"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
M = V.M


def sheet(rules, path, sets, cols, w=260, h=190, steps=50):
    pad = 8; f = M.font(15)
    W = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(sets):
            for k, (cn, kind, val) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                n = M.cut_axis(r, val, w, h, steps, c=c) if kind == 'axis' else M.cut_across(r, val, h, steps, c=c)
                pic = Image.fromarray(M.shade(n, steps)); im.paste(pic, (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); print('wrote', path, im.size)


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'main'
    cols = [('flat cut', 'axis', 0.0), ('cut tilted 30', 'axis', 30.0), ('cut tilted 60', 'axis', 60.0), ('upright cut', 'axis', 90.0)]
    if tag == 'main':
        rules = [V.R_one(), V.R_holo(), V.R_lathe(), V.R_lathe_b(90), V.spin('V'), V.spin('up')]
        sheet(rules, os.path.join(HERE, 'cuts-main.png'), V.SETS[:2], cols)
    elif tag == 'spin':
        rules = [V.spin('V'), V.spin('V', 10.0), V.spin('V', 45.0), V.spin('V', 90.0), V.spin('up'), V.spin('up', 45.0)]
        cols2 = cols + [('across x = -0.3', 'across', -0.3), ('across x = 0.4', 'across', 0.4)]
        sheet(rules, os.path.join(HERE, 'cuts-spin.png'), [V.SETS[0], V.SETS[2]], cols2, w=230, h=170)
