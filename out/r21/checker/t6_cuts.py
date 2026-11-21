"""t6: my own cut sheets for the rules that are said to have round buds off the page that are not rings.
One row per rule. Usage: python t6_cuts.py basilica | rabbit | mandel | off"""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
from PIL import Image, ImageDraw
import mem as M, ck

sheet, am, span, frame, prover = (ck.load(f) for f in ('sheet', 'alongmem', 'span', 'frame', 'prover'))
L = lambda lam: M.Rule('lag%g' % lam, 'the scout\'s lag, share %g' % lam, M.lag(lam))
RULES = [M.bench('oneplane'), M.bench('along'), sheet.get('evc005e70k16'), sheet.get('ease'), am.get('c_wake1'), am.get('c_wake2'), am.get('b_keep'), L(0.7)]
what = sys.argv[1] if len(sys.argv) > 1 else 'basilica'
S = 250; steps = 100


def across(r, x0, c, half=1.0):
    p, q = np.meshgrid(np.linspace(-half, half, S), np.linspace(half, -half, S))
    n = M.stay(r, np.full_like(p, x0), p, q, c[0], c[1], c[2], steps) if c is not None else M.mandel(r, np.full_like(p, x0), p, q, steps)
    return M.shade(n, steps)


def along_cut(r, ang, c, box):
    return M.shade(M.cut_axis(r, ang, int(S * 1.4), S, steps, c=c, box=box), steps)


if what == 'basilica':
    c = (-1.0, 0.0, 0.0)
    cols = [('across x = 0', lambda r: across(r, 0.0, c)), ('across x = -0.3', lambda r: across(r, -0.3, c)), ('across x = -1', lambda r: across(r, -1.0, c, 0.6)),
            ('across x = -1.4', lambda r: across(r, -1.4, c, 0.4)),
            ('along 22.5', lambda r: along_cut(r, 22.5, c, (-1.75, 1.75, -1.25, 1.25))), ('along 45', lambda r: along_cut(r, 45.0, c, (-1.75, 1.75, -1.25, 1.25))),
            ('along 90', lambda r: along_cut(r, 90.0, c, (-1.75, 1.75, -1.25, 1.25)))]
elif what == 'rabbit':
    c = ck.RABBIT
    cols = [('along 0', lambda r: along_cut(r, 0.0, c, (-1.75, 1.75, -1.25, 1.25))), ('along 11.25', lambda r: along_cut(r, 11.25, c, (-1.75, 1.75, -1.25, 1.25))),
            ('along 33.75', lambda r: along_cut(r, 33.75, c, (-1.75, 1.75, -1.25, 1.25))), ('along 90', lambda r: along_cut(r, 90.0, c, (-1.75, 1.75, -1.25, 1.25))),
            ('across x = 0', lambda r: across(r, 0.0, c, 1.2)), ('across x = -0.6', lambda r: across(r, -0.6, c, 1.2)), ('across x = 0.5', lambda r: across(r, 0.5, c, 1.2))]
elif what == 'off':
    cols = []
    for cc in ((-1.0, 0.03, 0.0), (-1.0, 0.1, 0.0), (-0.75, 0.1, 0.0), (-1.0, 0.0707, 0.0707)):
        cols.append(('c=%s along 0' % (cc,), (lambda cc: lambda r: along_cut(r, 0.0, cc, (-1.75, 1.75, -1.25, 1.25)))(cc)))
        cols.append(('across x = 0', (lambda cc: lambda r: across(r, 0.0, cc))(cc)))
else:
    cols = [('along 0', lambda r: along_cut(r, 0.0, None, (-2.1, 0.7, -1.3, 1.3))), ('along 11.25', lambda r: along_cut(r, 11.25, None, (-2.1, 0.7, -1.3, 1.3))),
            ('along 45', lambda r: along_cut(r, 45.0, None, (-2.1, 0.7, -1.3, 1.3))), ('along 90', lambda r: along_cut(r, 90.0, None, (-2.1, 0.7, -1.3, 1.3))),
            ('across x = -0.12', lambda r: across(r, -0.12, None, 1.1)), ('across x = -1', lambda r: across(r, -1.0, None, 0.6)), ('across x = -0.55', lambda r: across(r, -0.55, None, 1.0))]

pad = 8; t0 = time.time(); rows = []
for r in RULES:
    rows.append([f(r) for _, f in cols]); print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
W = pad + sum(p.shape[1] + pad for p in rows[0]); H = 34 + len(RULES) * (S + 26)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'checker: %s, %d steps (cream = never leaves)' % (what, steps), fill=(240, 240, 245), font=M.font(17))
for i, (r, pics) in enumerate(zip(RULES, rows)):
    y = 34 + i * (S + 26); x = pad
    for (hd, _), pic in zip(cols, pics):
        d.text((x, y), ('%s: ' % r.name if x == pad else '') + hd, fill=(235, 220, 170), font=M.font(13)); im.paste(Image.fromarray(pic), (x, y + 18)); x += pic.shape[1] + pad
im.save('out/r21/checker/cuts-%s.png' % what); print('saved', im.size)
