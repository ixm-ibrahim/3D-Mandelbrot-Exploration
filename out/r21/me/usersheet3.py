"""One sheet for the user: what comes out when the plane follows the orbit. Plain labels, no internal names.
    python out/r21/me/usersheet3.py   -> out/r21/me/plane-follows-orbit.png"""
import os, sys, time
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

S = {r.name: r for r in M.SCOUT}
ROWS = [(S['fixed'], 'The plane never moves: it stays the flat page (this is the entry "Sphere inversions, one plane")'),
        (S['lag25'], 'Before each squaring the plane turns a quarter of the way toward the orbit point'),
        (S['lag75'], 'Before each squaring the plane turns three quarters of the way toward the orbit point'),
        (S['delay'], 'Each point is squared about the plane that the point before it made'),
        (S['own'], 'The plane follows the orbit point at once (this is the entry "Quaternion square (Lathe)")'),
        (M.bench('along'), 'For comparison: "along" as it is now (no memory; four fixed planes)')]
w, h, nd, sj, sm = 380, 285, 240, 28, 22
cw, ch, sc = 300, 285, 60
pad = 10; top = 92; t0 = time.time()
heads = ['Julia set: basilica', 'Julia set: rabbit', 'Mandelbrot: cut along the flat page', 'Mandelbrot: cut along a plane turned 22.5°', 'Mandelbrot: cut across the x-axis', 'Mandelbrot: the whole solid']
tw = [w, w, cw, cw, ch, w]
W = pad + sum(t + pad for t in tw); H = top + len(ROWS) * (h + 62)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 10), 'What comes out when the plane follows the orbit', fill=(240, 240, 245), font=M.font(28))
d.text((pad, 50), 'Every orbit starts with the flat page as its plane. Each row lets the plane follow the orbit a different way. Rough blocks; cuts point by point.', fill=(160, 170, 185), font=M.font(17))
for i, (r, label) in enumerate(ROWS):
    y = top + i * (h + 62)
    d.text((pad, y), label, fill=(235, 220, 170) if i < len(ROWS) - 1 else (205, 210, 220), font=M.font(20))
    pics = []
    for c in ((-1.0, 0.0, 0.0), M.RABBIT):
        dep, px = M.solid(r, c, w, h, nd, sj); pics.append(M.shade_solid(dep, px))
    pics += [M.shade(M.cut_axis(r, a, cw, h, sc), sc) for a in (0.0, 22.5)] + [M.shade(M.cut_across(r, -0.12, ch, sc), sc)]
    dep, px = M.solid(r, None, w, h, nd, sm); pics.append(M.shade_solid(dep, px))
    x = pad
    for hd, pic in zip(heads, pics):
        d.text((x, y + 30), hd, fill=(150, 160, 175), font=M.font(14)); im.paste(Image.fromarray(pic), (x, y + 50)); x += pic.shape[1] + pad
    print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = os.path.join(HERE, 'plane-follows-orbit.png'); im.save(out); print(out, im.size)
