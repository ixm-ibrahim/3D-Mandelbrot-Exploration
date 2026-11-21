"""Diagnostic: buds ON a bud. The bud on the middle body of the basilica in the direction a (0 = flat page, 45 =
slanted, 90 = upright), cut ACROSS its own axis (the line from the x-axis out through the bud), at the height where
the flat picture has the bud's own two side buds (0.6641). Across = along x; up = round the x-axis.
   python out/r22/buds/d2_subbuds.py -> d2-subbuds.png, subbuds.txt"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B
M = B.M
C = B.BASILICA; W = 420; L = 0.16; STEPS = 60; H0 = 0.6641; A0 = 0.0807; pad = 8
names = ['oneplane', 'along', 'once', 'pulled']; angs = [0.0, 45.0, 90.0, 22.5]
im = Image.new('RGB', (pad + len(angs) * (W + pad), 30 + len(names) * (W + 26)), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(14)
out = open(os.path.join(HERE, 'subbuds.txt'), 'w', encoding='utf-8'); t0 = time.time()
u, v = np.meshgrid(np.linspace(-L, L, W), np.linspace(L, -L, W))
N = 1440; tau = np.arange(N) * 2 * np.pi / N
for i, name in enumerate(names):
    for j, a in enumerate(angs):
        ar = np.radians(a); er = (0, np.cos(ar), np.sin(ar)); ep = (0, -np.sin(ar), np.cos(ar))
        P = [H0 * er[k] + u * (1 if k == 0 else 0) + v * ep[k] for k in range(3)]
        n = M.stay(B.RULES[name], P[0], P[1], P[2], *C, STEPS); x = pad + j * (W + pad); y = 30 + i * (W + 26)
        im.paste(Image.fromarray(M.shade(n, STEPS)), (x, y + 18))
        d.text((x, y), '%s | bud at %g deg, cut across its own axis at height %.4f, half-width %.2f' % (name, a, H0, L), fill=(200, 200, 170), font=f)
        rr = A0 / L * (W - 1) / 2; cx_, cy_ = x + (W - 1) / 2, y + 18 + (W - 1) / 2
        d.ellipse([cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr], outline=(90, 200, 120), width=1)
        best = None
        for a0 in np.linspace(0.066, 0.100, 18):                       # the ring of side buds may sit a little in or out: take the radius with most arcs
            R = [H0 * er[k] + a0 * np.cos(tau) * (1 if k == 0 else 0) + a0 * np.sin(tau) * ep[k] for k in range(3)]
            ins = B.inside(name, R[0], R[1], R[2], C, 80); arcs = B.arcs(ins)
            if best is None or len(arcs) > len(best[1]):
                best = (a0, arcs, ins.mean())
        a0, arcs, share = best
        line = '%-8s bud at %5.1f deg: ring round the bud\'s own axis, radius %.3f: %d arcs, inside %.1f%%; centres (deg, 0 = toward +x, 90 = round the x-axis) %s widths %s' % (
            name, a, a0, len(arcs), 100 * share, np.round([c_ * 360.0 / N for c_, l in arcs], 0), np.round([l * 360.0 / N for c_, l in arcs], 1))
        print(line); out.write(line + '\n'); out.flush()
    print(name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
p = os.path.join(HERE, 'd2-subbuds.png'); im.save(p); print(p, im.size)
