"""Cuts (working pictures, not for the user): flat cut and upright cut through the x-axis, one row per rule.

    python out/r25/wall/cuts.py <tag> key1 key2 ...      -> cuts-<tag>.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wall as W
M = W.M

SETS = [('c = 0', (0.0, 0.0, 0.0))] + W.SETS


def main():
    tag = sys.argv[1]; keys = sys.argv[2:]
    import pil as PL
    extra = {'p2': lambda: PL.rule_lop(2), 'pillow': lambda: M.bench('pillow'), 'twoplane': lambda: M.bench('twoplane'), 'along': lambda: M.bench('along')}
    rules = [(W.RULES.get(k) or extra[k])() for k in keys]
    w, h, steps, pad = 260, 200, 50, 8; f = M.font(15)
    cols = [('flat', 0.0), ('upright', 90.0), ('upright across (x = 0 plane)', None)]
    W_ = pad + len(SETS) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W_, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(SETS):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                if ang is None:
                    n = M.cut_across(r, 0.0, w, steps, c=c, L=1.8)[int((w - h) / 2):int((w - h) / 2) + h]
                else:
                    n = M.cut_axis(r, ang, w, h, steps, c=c, box=(-1.9, 1.9, -1.46, 1.46))
                im.paste(Image.fromarray(M.shade(n, steps)), (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    p = os.path.join(HERE, 'cuts-%s.png' % tag); im.save(p); print('wrote', p, im.size)


if __name__ == '__main__':
    main()
