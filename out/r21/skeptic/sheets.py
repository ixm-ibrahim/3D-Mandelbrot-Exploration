"""Skeptic, job 2: rough solids from chosen eye positions, with the library's own sheet functions.
    python out/r21/skeptic/sheets.py julia  <tag> <rule,rule,...> <camx,camy,camz> [steps] [w] [nd] [sets]
    python out/r21/skeptic/sheets.py mandel <tag> <rule,rule,...> <camx,camy,camz> [steps] [w] [nd]
    python out/r21/skeptic/sheets.py close  <tag> <rule,rule,...> <camx,camy,camz> <set> <cx,cy,cz centre> <half width> [steps] [w] [nd]"""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

mode, tag, names = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
cam = tuple(float(t) for t in sys.argv[4].split(','))
rules = [M.bench(n) if n in ('oneplane', 'along', 'lathe', 'away', 'twoplane') else R.BY[n] for n in names]
SETS = dict(basilica=M.JSETS[0], sanmarco=M.JSETS[1], airplane=M.JSETS[2], rabbit=M.JSETS[3], siegel=M.JSETS[4], dendrite=M.JSETS[5])
if mode == 'julia':
    steps = int(sys.argv[5]) if len(sys.argv) > 5 else 40; w = int(sys.argv[6]) if len(sys.argv) > 6 else 380; nd = int(sys.argv[7]) if len(sys.argv) > 7 else 240
    sets = [SETS[s] for s in sys.argv[8].split(',')] if len(sys.argv) > 8 else None
    M.julia_sheet(rules, 'out/r21/skeptic/julia-%s.png' % tag, sets=sets, w=w, h=w * 3 // 4, nd=nd, steps=steps, cam=cam)
elif mode == 'mandel':
    steps = int(sys.argv[5]) if len(sys.argv) > 5 else 40; w = int(sys.argv[6]) if len(sys.argv) > 6 else 380; nd = int(sys.argv[7]) if len(sys.argv) > 7 else 240
    M.mandel_sheet(rules, 'out/r21/skeptic/mandel-%s.png' % tag, w=w, nd=nd, steps=steps, cut_steps=100, angles=(0.0, 11.25, 22.5, 33.75, 45.0, 90.0), cam=cam)
else:
    which = sys.argv[5]; centre = tuple(float(t) for t in sys.argv[6].split(',')); hw = float(sys.argv[7])
    steps = int(sys.argv[8]) if len(sys.argv) > 8 else 60; w = int(sys.argv[9]) if len(sys.argv) > 9 else 520; nd = int(sys.argv[10]) if len(sys.argv) > 10 else 360
    c = None if which == 'mandel' else SETS[which][1]; h = w * 3 // 4; pad = 8; t0 = time.time()
    cols = min(3, len(rules)); rows = (len(rules) + cols - 1) // cols
    im = Image.new('RGB', (pad + cols * (w + pad), 44 + rows * (h + 30)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), '%s, rough solid: centre %s, half width %g, %d steps, %d blocks deep, eye at %s' % (which, centre, hw, steps, nd, cam), fill=(240, 240, 245), font=M.font(18))
    for i, r in enumerate(rules):
        dep, px = M.solid(r, c, w, h, nd, steps, centre=centre, half_w=hw, cam=cam)
        x = pad + (i % cols) * (w + pad); y = 44 + (i // cols) * (h + 30)
        d.text((x, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 22))
        print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    out = 'out/r21/skeptic/close-%s.png' % tag; im.save(out); print('wrote', out)
