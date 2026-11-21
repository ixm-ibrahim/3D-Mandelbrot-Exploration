"""Cuts of a list of rules (cheap looks; solids decide).

    python out/r25/pillow/cuts.py <tag> <spec> <spec> ...
    spec = one | rho,H[,kind]      e.g.  one 0,1 0.5,0.866 0.25,1,JA
Columns: c = -1: flat, upright through the x-axis, upright across the x-axis at x = 0 and at the touching point
x = -0.618; rabbit: flat, lifted to z = +0.15 and z = -0.15, upright through the x-axis, upright through the y-axis.
Prints the 'touching number' of c = -1: area inside in the cut across x = -0.618 over the area across x = 0.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
M = P.M

ALPHA = (1 - np.sqrt(5)) / 2


def plane_cut(rule, c, o, e1, e2, w, h, steps, half=1.8):
    u, v = np.meshgrid(np.linspace(-half, half, w), np.linspace(half * h / w, -half * h / w, h))
    pts = [o[i] + u * e1[i] + v * e2[i] for i in range(3)]
    return M.stay(rule, pts[0], pts[1], pts[2], c[0], c[1], c[2], steps)


VIEWS = [
    ('c = -1, flat', (-1.0, 0, 0), (0, 0, 0), (1, 0, 0), (0, 1, 0)),
    ('c = -1, upright through x-axis', (-1.0, 0, 0), (0, 0, 0), (1, 0, 0), (0, 0, 1)),
    ('c = -1, upright across, x = 0', (-1.0, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 1)),
    ('c = -1, across at touching point', (-1.0, 0, 0), (ALPHA, 0, 0), (0, 1, 0), (0, 0, 1)),
    ('rabbit, flat', M.RABBIT, (0, 0, 0), (1, 0, 0), (0, 1, 0)),
    ('rabbit, lifted to z = +0.15', M.RABBIT, (0, 0, 0.15), (1, 0, 0), (0, 1, 0)),
    ('rabbit, lowered to z = -0.15', M.RABBIT, (0, 0, -0.15), (1, 0, 0), (0, 1, 0)),
    ('rabbit, upright through x-axis', M.RABBIT, (0, 0, 0), (1, 0, 0), (0, 0, 1)),
    ('rabbit, upright through y-axis', M.RABBIT, (0, 0, 0), (0, 1, 0), (0, 0, 1)),
]


def get(spec):
    if spec == 'one':
        return M.bench('oneplane')
    if spec == 'along':
        return M.bench('along')
    if spec == 'two':
        return M.bench('twoplane')
    if spec == 'tri':
        sys.path.insert(0, os.path.join(P.ROOT, 'out', 'r24', 'me'))
        import tri as T
        return T.tri_rule(name='triangle pillow (round 24)')
    p = spec.split(','); kind = p[2] if len(p) > 2 else 'J'
    return P.rule(float(p[0]), float(p[1]), kind, name='rho %s, H %s, %s' % (p[0], p[1], kind))


def touching(rule, steps=50, n=161):
    a = plane_cut(rule, (-1.0, 0, 0), (ALPHA, 0, 0), (0, 1, 0), (0, 0, 1), n, n, steps, half=1.0) >= steps
    b = plane_cut(rule, (-1.0, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 1), n, n, steps, half=1.0) >= steps
    return a.sum() / max(b.sum(), 1), b.mean() * 4.0


def sheet(tag, specs, w=230, h=172, steps=50):
    rules = [get(s) for s in specs]; pad = 6; f = M.font(13)
    W = pad + len(VIEWS) * (w + pad); H = 8 + len(rules) * (h + 24)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 8 + i * (h + 24); tn, mid = touching(r, steps)
        d.text((pad, y), '%s   | touching number %.3f (middle cut area %.2f)' % (r.name, tn, mid), fill=(235, 220, 170), font=f)
        for j, (nm, c, o, e1, e2) in enumerate(VIEWS):
            n = plane_cut(r, c, o, e1, e2, w, h, steps); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade(n, steps)), (x, y + 18)); d.text((x + 3, y + 20), nm, fill=(150, 160, 175), font=M.font(11))
        print('%-28s touching number %.3f, middle cut area %.2f   (%.0f s)' % (r.name, tn, mid, time.time() - t0)); sys.stdout.flush()
    path = os.path.join(HERE, 'cuts-%s.png' % tag); im.save(path); print('wrote', path, im.size)


if __name__ == '__main__':
    sheet(sys.argv[1], sys.argv[2:])
