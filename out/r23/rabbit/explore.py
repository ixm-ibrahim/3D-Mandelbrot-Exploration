"""Quick cuts of any rules of doors.py, with the flat check and the lift test.
    python out/r23/rabbit/explore.py <out name> <rule keys joined by commas> [steps]
Columns: c = -1: flat cut, upright cut through the x-axis, cut at 33.75 degrees, cut across the x-axis at x = 0;
         rabbit: flat cut, cut lifted to z = 0.15, upright cut through 0 and c, upright cut through the x-axis.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
M = D.M


def plane_cut(r, c, o, e1, e2, w, h, half, steps):
    u, s = np.meshgrid(np.linspace(-half, half, w), np.linspace(half * h / w, -half * h / w, h))
    P = [o[i] + u * e1[i] + s * e2[i] for i in range(3)]
    return M.stay(r, P[0], P[1], P[2], c[0], c[1], c[2], steps)


def lift(r, c, n=3000, seed=11):
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.6, 1.6, 40000), rng.uniform(-1.3, 1.3, 40000)
    ok = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300; zr, zi = zr[ok][:n], zi[ok][:n]
    return float((M.stay(r, zr, zi, np.full(zr.size, 1e-6), c[0], c[1], c[2], 80) >= 80).mean())


if __name__ == '__main__':
    out, keys = sys.argv[1], sys.argv[2].split(','); steps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    w, h, pad = 250, 190, 6; B, R = D.SETS['basilica'], D.SETS['rabbit']
    cd = np.array([R[0], R[1], 0.0]); cd /= np.linalg.norm(cd); a = np.radians(33.75)
    cols = [('c = -1, flat', B, (0, 0, 0), (1, 0, 0), (0, 1, 0)), ('c = -1, upright', B, (0, 0, 0), (1, 0, 0), (0, 0, 1)),
            ('c = -1, at 33.75', B, (0, 0, 0), (1, 0, 0), (0, np.cos(a), np.sin(a))), ('c = -1, across x = 0', B, (0, 0, 0), (0, 1, 0), (0, 0, 1)),
            ('rabbit, flat', R, (0, 0, 0), (1, 0, 0), (0, 1, 0)), ('rabbit, lifted 0.15', R, (0, 0, 0.15), (1, 0, 0), (0, 1, 0)),
            ('rabbit, upright through c', R, (0, 0, 0), tuple(cd), (0, 0, 1)), ('rabbit, upright through x-axis', R, (0, 0, 0), (1, 0, 0), (0, 0, 1))]
    W = pad + len(cols) * (w + pad); H = 8 + len(keys) * (h + 24)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, k in enumerate(keys):
        r = D.get(k); y = 8 + i * (h + 24)
        f = M.flat_check(r, n=6000, steps=60); lb, lr = lift(r, B), lift(r, R)
        txt = '%s: %s | flat check differ M %d, c=-1 %d, rabbit %d, Siegel %d of %d, strays %.0e | lift c=-1 %.3f rabbit %.3f' % (k, r.label, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], lb, lr)
        d.text((pad, y), txt, fill=(235, 220, 170), font=M.font(14)); print(txt)
        for j, (nm, c, o, e1, e2) in enumerate(cols):
            n = plane_cut(r, c, o, e1, e2, w, h, 1.75, steps); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade(n, steps)), (x, y + 20)); d.text((x + 4, y + 22), nm, fill=(150, 160, 175), font=M.font(12))
        print('   %.0f s' % (time.time() - t0)); sys.stdout.flush()
    p = os.path.join(HERE, out); im.save(p); print('wrote', p, im.size)
