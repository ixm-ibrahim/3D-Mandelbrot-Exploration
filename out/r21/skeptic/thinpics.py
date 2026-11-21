"""Skeptic: pictures of the flat page and of pages lifted a hair above it.  python out/r21/skeptic/thinpics.py [m|j]
Each tile is a cut PARALLEL to the flat page at the height z given in its heading (z = 0 is the flat page itself)."""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

SC = {r.name: r for r in M.SCOUT}
what = sys.argv[1] if len(sys.argv) > 1 else 'm'
HS = (0.0, 1e-9, 1e-6, 1e-3, 0.02, 0.1)


def lifted(rule, h, w, hh, steps, c=None):
    box = (-2.1, 0.7, -1.3, 1.3) if c is None else (-1.8, 1.8, -1.3, 1.3)
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], hh)); z = np.full_like(u, h)
    return M.mandel(rule, u, s, z, steps) if c is None else M.stay(rule, u, s, z, c[0], c[1], c[2], steps)


def sheet(rows, path, title, w=300, hh=280, steps=150):
    pad = 8; W = pad + len(HS) * (w + pad); H = 50 + len(rows) * (hh + 30)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); d.text((pad, 8), title, fill=(240, 240, 245), font=M.font(20))
    for i, (r, c, lab) in enumerate(rows):
        y = 50 + i * (hh + 30); base = None
        for j, h in enumerate(HS):
            n = lifted(r, h, w, hh, steps, c); ins = n >= steps
            if base is None:
                base = ins
            x = pad + j * (w + pad); im.paste(Image.fromarray(M.shade(n, steps)), (x, y + 22))
            d.text((x, y), '%s  z = %g: %d of the %d flat pixels are gone' % (lab, h, int((base & ~ins).sum()), int(base.sum())) if j else '%s  z = 0 (the flat page)' % lab, fill=(235, 220, 170), font=M.font(13))
        print(lab); sys.stdout.flush()
    im.save(path); print('wrote', path)


if what == 'm':
    rows = [(M.bench('oneplane'), None, 'oneplane'), (M.bench('along'), None, 'along')] + [(R.BY[n], None, n) for n in ('lag05', 'lag10', 'lag25', 'lag40', 'lag60', 'lag75', 'lag90', 'delay', 'first')]
    sheet(rows, 'out/r21/skeptic/thin-mandel.png', 'Mandelbrot solid: the flat page, and pages lifted a hair above it (150 steps)')
else:
    rows = []
    for n in ('oneplane', 'lag25', 'lag50', 'lag60', 'lag75', 'delay'):
        r = M.bench('oneplane') if n == 'oneplane' else R.BY[n]
        rows += [(r, M.RABBIT, n + ' rabbit'), (r, M.SIEGEL, n + ' Siegel')]
    sheet(rows, 'out/r21/skeptic/thin-julia.png', 'Julia sets: the flat page, and pages lifted a hair above it (150 steps)')
