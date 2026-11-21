"""python out/r21/frame/cuts.py <tag> <set> name1 name2 ... [steps=60] [cw=260]
Cuts of ONE Julia set (set = basilica | sanmarco | airplane | rabbit | siegel | dendrite) or of the Mandelbrot solid
(set = mandel): along sheets through the x-axis at 0, 11.25, 22.5, 33.75, 45, 90 degrees, and across the x-axis at
two places.  One row per rule.  Cheap (flat cuts only).  Names: my rules, or bench names with a leading '@'."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
import myrules as R
np.seterr(all='ignore')
SETS = {'basilica': (-1.0, 0.0, 0.0), 'sanmarco': (-0.75, 0.0, 0.0), 'airplane': (-1.754878, 0.0, 0.0), 'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 'dendrite': (0.0, 1.0, 0.0), 'mandel': None}
ACROSS = {'basilica': (0.0, -1.0), 'sanmarco': (0.0, -0.75), 'airplane': (0.0, -1.75), 'rabbit': (0.0, -0.4), 'siegel': (0.0, -0.4), 'dendrite': (0.0, 0.5), 'mandel': (-0.12, -1.0)}

tag, sname = sys.argv[1], sys.argv[2]
opts = dict(a.split('=') for a in sys.argv[3:] if '=' in a); names = [a for a in sys.argv[3:] if '=' not in a]
rs = [M.bench(n[1:]) if n.startswith('@') else R.BY[n] for n in names]
steps = int(opts.get('steps', 60)); cw = int(opts.get('cw', 260)); c = SETS[sname]
ch = int(cw * (2.6 / 2.8 if c is None else 2.6 / 3.6)); angles = (0.0, 11.25, 22.5, 33.75, 45.0, 90.0); xs = ACROSS[sname]
pad = 8; W = pad + len(angles) * (cw + pad) + len(xs) * (ch + pad); H = 50 + len(rs) * (ch + 46)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'Cuts of %s (%d steps): along sheets through the x-axis, then across it' % (sname if c is None else '%s, c = %s' % (sname, c), steps), fill=(240, 240, 245), font=M.font(20))
t0 = time.time()
for i, r in enumerate(rs):
    y = 50 + i * (ch + 46); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(15)); x = pad
    for a in angles:
        pic = M.shade(M.cut_axis(r, a, cw, ch, steps, c=c), steps)
        d.text((x, y + 20), 'sheet turned %g' % a, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 36)); x += cw + pad
    for x0 in xs:
        pic = M.shade(M.cut_across(r, x0, ch, steps, c=c), steps)
        d.text((x, y + 20), 'across at x = %g' % x0, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 36)); x += ch + pad
    print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
p = os.path.join(HERE, 'cuts-%s-%s.png' % (sname, tag)); im.save(p); print('wrote', p)
