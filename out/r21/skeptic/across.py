"""Skeptic, job 2: large cuts ACROSS the x-axis (y to the right, z up), with two close-ups of the bud zone.
    python out/r21/skeptic/across.py <tag> <x0> <c: basilica|mandel> <rule,rule,...> [steps]
A ring shows as a full circle band, a round bud as a round blob, a fin as a hair line."""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

tag, x0, which, names = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4].split(',')
steps = int(sys.argv[5]) if len(sys.argv) > 5 else 150
c = {'basilica': (-1.0, 0.0, 0.0), 'mandel': None, 'sanmarco': (-0.75, 0.0, 0.0), 'airplane': (-1.754878, 0.0, 0.0)}[which]
L = float(sys.argv[6]) if len(sys.argv) > 6 else 1.2
ZW = float(sys.argv[7]) if len(sys.argv) > 7 else 0.3          # half width of the close-ups
YC = float(sys.argv[8]) if len(sys.argv) > 8 else 0.9          # where the close-ups are centred (distance from the axis)


def win(rule, yc, zc, hw, n):
    p, q = np.meshgrid(np.linspace(yc - hw, yc + hw, n), np.linspace(zc + hw, zc - hw, n)); X = np.full_like(p, x0)
    return M.mandel(rule, X, p, q, steps) if c is None else M.stay(rule, X, p, q, c[0], c[1], c[2], steps)


n = 440; pad = 8; t0 = time.time()
heads = ['whole cut, half width %g' % L, 'close-up at the flat page side (y = %g, z = 0), half width %g' % (YC, ZW), 'close-up at 45 degrees', 'close-up at the upright side (y = 0, z = %g)' % YC]
W = pad + 4 * (n + pad); H = 44 + len(names) * (n + 40)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'Cuts across the x-axis at x = %g, %s, %d steps (y to the right, z up)' % (x0, which, steps), fill=(240, 240, 245), font=M.font(20))
for i, nm in enumerate(names):
    r = M.bench(nm) if nm in ('oneplane', 'along', 'lathe', 'away') else R.BY[nm]
    y = 44 + i * (n + 40); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(16))
    s = YC / np.sqrt(2)
    arrs = [win(r, 0.0, 0.0, L, n), win(r, YC, 0.0, ZW, n), win(r, s, s, ZW, n), win(r, 0.0, YC, ZW, n)]
    for j, (hd, a) in enumerate(zip(heads, arrs)):
        x = pad + j * (n + pad); d.text((x, y + 20), hd, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(M.shade(a, steps)), (x, y + 36))
    print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = 'out/r21/skeptic/across-%s.png' % tag; im.save(out); print('wrote', out)
