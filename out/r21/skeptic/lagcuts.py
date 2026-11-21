"""Skeptic, job 2: cuts of the lag family at higher resolution and more steps.
    python out/r21/skeptic/lagcuts.py basilica | rabbit | mandel | vol
Cuts along sheets through the x-axis at 0, 11.25, 22.5, 33.75, 45, 90 degrees, and across the x-axis."""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

SC = {r.name: r for r in M.SCOUT}
what = sys.argv[1] if len(sys.argv) > 1 else 'basilica'
NAMES = ['oneplane', 'along', 'lag05', 'lag10', 'lag25', 'lag40', 'lag50', 'lag60', 'lag75', 'lag90', 'lag95', 'delay', 'first', 'lathe']
if len(sys.argv) > 2:
    NAMES = sys.argv[2].split(',')
RULES = [M.bench(n) if n in ('oneplane', 'along', 'lathe') else R.BY[n] for n in NAMES]
ANG = (0.0, 11.25, 22.5, 33.75, 45.0, 90.0)


def tiles_sheet(rows, heads, path, title):
    """rows: list of (label, [arrays of counts], steps)."""
    pad = 8; ws = [a.shape[1] for a in rows[0][1]]; hh = max(a.shape[0] for a in rows[0][1])
    W = pad + sum(w + pad for w in ws); H = 50 + len(rows) * (hh + 44)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); d.text((pad, 8), title, fill=(240, 240, 245), font=M.font(20))
    for i, (lab, arrs, steps) in enumerate(rows):
        y = 50 + i * (hh + 44); d.text((pad, y), lab, fill=(235, 220, 170), font=M.font(16)); x = pad
        for hd, a in zip(heads, arrs):
            d.text((x, y + 22), hd, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(M.shade(a, steps)), (x, y + 40)); x += a.shape[1] + pad
    im.save(path); print('wrote', path)


def lifted(rule, h, w, hh, steps, c, box):
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], hh)); z = np.full_like(u, h)
    return M.stay(rule, u, s, z, c[0], c[1], c[2], steps)


t0 = time.time()
if what == 'basilica':
    steps = 100; c = (-1.0, 0.0, 0.0); rows = []
    heads = ['along the sheet turned %g' % a for a in ANG] + ['across at x = 0 (y right, z up)', 'across at x = -1', 'across at x = -0.35']
    for r in RULES:
        arrs = [M.cut_axis(r, a, 380, 270, steps, c=c) for a in ANG] + [M.cut_across(r, x0, 270, steps, c=c, L=L) for x0, L in ((0.0, 1.0), (-1.0, 0.6), (-0.35, 1.0))]
        rows.append(('%s: %s' % (r.name, r.label), arrs, steps)); print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    tiles_sheet(rows, heads, 'out/r21/skeptic/lag-basilica-cuts.png', 'Basilica (c = -1): cuts, %d steps' % steps)
elif what == 'rabbit':
    steps = 100; c = M.RABBIT; rows = []; box = (-1.5, 1.5, -1.25, 1.25)
    hs = (0.0, 0.05, 0.15, 0.3)
    heads = ['flat cut lifted to z = %g' % h for h in hs] + ['along the sheet turned 45', 'along the upright sheet (90)', 'across at x = 0', 'across at x = -0.3']
    for r in RULES:
        arrs = [lifted(r, h, 330, 275, steps, c, box) for h in hs] + [M.cut_axis(r, a, 330, 275, steps, c=c, box=box) for a in (45.0, 90.0)] + [M.cut_across(r, x0, 275, steps, c=c, L=1.25) for x0 in (0.0, -0.3)]
        rows.append(('%s: %s' % (r.name, r.label), arrs, steps)); print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    tiles_sheet(rows, heads, 'out/r21/skeptic/lag-rabbit-cuts.png', 'Rabbit: cuts, %d steps' % steps)
elif what == 'mandel':
    steps = 120; rows = []
    heads = ['along the sheet turned %g' % a for a in ANG] + ['across at x = -0.12', 'across at x = -1', 'across at x = -0.6']
    for r in RULES:
        arrs = [M.cut_axis(r, a, 360, 330, steps) for a in ANG] + [M.cut_across(r, x0, 330, steps, L=L) for x0, L in ((-0.12, 1.3), (-1.0, 0.6), (-0.6, 1.0))]
        rows.append(('%s: %s' % (r.name, r.label), arrs, steps)); print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    tiles_sheet(rows, heads, 'out/r21/skeptic/lag-mandel-cuts.png', 'The Mandelbrot solid: cuts, %d steps' % steps)
elif what == 'vol':
    rng = np.random.default_rng(4); n = 300000
    v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3)); cm = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    bv, bm = 3.6 * 2.6 * 2.6, 2.8 * 2.6 * 2.6
    print('volumes (of %d random points); a slow leak or dust shows as a volume that keeps falling with the steps' % n)
    print('%-9s %-32s %-32s %-32s %-32s' % ('rule', 'basilica 30/80/200/500 steps', 'rabbit 30/80/200/500', 'Siegel 30/80/200/500', 'Mandelbrot 30/80/200/500'))
    for r in RULES:
        line = '%-9s' % r.name
        for c in ((-1.0, 0.0, 0.0), M.RABBIT, M.SIEGEL, None):
            nn = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 500) if c else M.mandel(r, cm[:, 0], cm[:, 1], cm[:, 2], 500)
            line += ' ' + '%-32s' % ' / '.join('%.3f' % ((nn >= s).mean() * (bv if c else bm)) for s in (30, 80, 200, 500))
        print(line, ' %.0f s' % (time.time() - t0)); sys.stdout.flush()
