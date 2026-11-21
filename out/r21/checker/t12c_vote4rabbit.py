"""t12: the rabbit for vote4, evc005e70k16, c_wake1 (the skeptic's 'no lag has a rabbit with separate bodies'), my own cuts, 150 steps."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
from PIL import Image, ImageDraw
import mem as M, ck

L = lambda lam: M.Rule('lag%g' % lam, '', M.lag(lam))
sheet, am = ck.load('sheet'), ck.load('alongmem')
rules = [sheet.get('vote4'), sheet.get('evc005e70k16'), am.get('c_wake1')]
S = 230; steps = 150; c = ck.RABBIT; box = (-1.75, 1.75, -1.25, 1.25)
cols = [('along 5.6', lambda r: M.shade(M.cut_axis(r, 5.625, int(S * 1.4), S, steps, c=c, box=box), steps)),
        ('along 11.25', lambda r: M.shade(M.cut_axis(r, 11.25, int(S * 1.4), S, steps, c=c, box=box), steps)),
        ('along 22.5', lambda r: M.shade(M.cut_axis(r, 22.5, int(S * 1.4), S, steps, c=c, box=box), steps)),
        ('level z = 0.15', None), ('across x = 0', None)]


def level(r, z0):
    u, s = np.meshgrid(np.linspace(box[0], box[1], int(S * 1.4)), np.linspace(box[3], box[2], S))
    return M.shade(M.stay(r, u, s, np.full_like(u, z0), *c, steps), steps)


def across(r, x0, half=1.2):
    p, q = np.meshgrid(np.linspace(-half, half, S), np.linspace(half, -half, S))
    return M.shade(M.stay(r, np.full_like(p, x0), p, q, *c, steps), steps)


cols[3] = ('level z = 0.15', lambda r: level(r, 0.15)); cols[4] = ('across x = 0', lambda r: across(r, 0.0))
pad = 8; t0 = time.time(); rows = []
for r in rules:
    rows.append([f(r) for _, f in cols]); print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
W = pad + sum(p.shape[1] + pad for p in rows[0]); H = 34 + len(rules) * (S + 26)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'checker: the rabbit for vote4, evc005e70k16, c_wake1, %d steps' % steps, fill=(240, 240, 245), font=M.font(17))
for i, (r, pics) in enumerate(zip(rules, rows)):
    y = 34 + i * (S + 26); x = pad
    for (hd, _), pic in zip(cols, pics):
        d.text((x, y), ('%s: ' % r.name if x == pad else '') + hd, fill=(235, 220, 170), font=M.font(13)); im.paste(Image.fromarray(pic), (x, y + 18)); x += pic.shape[1] + pad
im.save('out/r21/checker/cuts-vote4rabbit.png'); print('saved', im.size)
