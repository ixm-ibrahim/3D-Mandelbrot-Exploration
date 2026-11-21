"""Cuts of the basilica (c = -1) and of the rabbit, 80 steps, the same eight cuts for every rule:
along sheets through the x-axis at 0, 11.25, 22.5, 33.75, 45 and 90 degrees (M.cut_axis), and across the x-axis at
x = 0 and x = -1 (M.cut_across).  One row per rule.   python out/r21/judge/cuts.py
Writes cuts-basilica-a.png, cuts-basilica-b.png, cuts-rabbit-a.png, cuts-rabbit-b.png (five rules each)."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
ANG = (0.0, 11.25, 22.5, 33.75, 45.0, 90.0); XS = (0.0, -1.0); STEPS = 80
W, H, A = 300, 217, 217


def row(r, c):
    pics = [M.shade(M.cut_axis(r, a, W, H, STEPS, c=c), STEPS) for a in ANG]
    pics += [M.shade(M.cut_across(r, x0, A, STEPS, c=c), STEPS) for x0 in XS]
    return pics


def sheet(rules, c, cname, path):
    pad = 8; heads = ['along the sheet at %g deg' % a for a in ANG] + ['across the x-axis at x = %g' % x for x in XS]
    widths = [W] * len(ANG) + [A] * len(XS)
    Wt = pad + sum(w + pad for w in widths); Ht = 50 + len(rules) * (H + 44)
    im = Image.new('RGB', (Wt, Ht), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Cuts of the %s, %d steps. Light = inside.' % (cname, STEPS), fill=(240, 240, 245), font=M.font(22))
    t0 = time.time()
    for i, r in enumerate(rules):
        y = 50 + i * (H + 44); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(16))
        x = pad
        for hd, pic in zip(heads, row(r, c)):
            d.text((x, y + 21), hd, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 38)); x += pic.shape[1] + pad
        print(cname, r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path)


if __name__ == '__main__':
    A_, B_ = J.RULES[:5], J.RULES[5:]
    for cname, c, tag in (('basilica (c = -1)', (-1.0, 0.0, 0.0), 'basilica'), ('rabbit', M.RABBIT, 'rabbit')):
        sheet(A_, c, cname, os.path.join(J.HERE, 'cuts-%s-a.png' % tag))
        sheet(B_, c, cname, os.path.join(J.HERE, 'cuts-%s-b.png' % tag))
