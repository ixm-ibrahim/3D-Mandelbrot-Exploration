"""Round 27, respace: solids and cuts of the carried object.

    python solids27.py solid <set> <way> <eye> [w h nd]     one solid, kept as depth-<set>-<way>-<eye>.npz
          set = b (c = -1) | r (rabbit);  way = A | B | C | T (the balls object itself, not carried);  eye = a | top | end
    python solids27.py cuts                                  cuts.png
    python solids27.py time                                  how long a known-good case takes on this machine now
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import carry as C
M = C.M
HERE = os.path.dirname(os.path.abspath(__file__))
CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'end': (1.0, 0.25, 0.3)}
BODIES = {'b': C.BASILICA, 'r': C.RABBIT}


def rule_of(st, way):
    if way == 'T':
        return C.tree_rule('gauss'), 14
    return C.carried(BODIES[st], way, nmax=48), 2


def solid(st, way, eye, w=400, h=300, nd=200):
    t0 = time.time(); r, steps = rule_of(st, way)
    dep, px = M.solid(r, C.ZERO, w, h, nd, steps, cam=CAMS[eye])
    np.savez_compressed(os.path.join(HERE, 'depth-%s-%s-%s.npz' % (st, way, eye)), depth=dep, px=px)
    Image.fromarray(M.shade_solid(dep, px)).save(os.path.join(HERE, 'solid-%s-%s-%s.png' % (st, way, eye)))
    print('solid %s %s %s  %d x %d x %d  %.0f s' % (st, way, eye, w, h, nd, time.time() - t0))


def cut_plane(st, way, kind, w, h):
    """kind 'flat': z = 0; 'up': the upright plane through the x-axis; 'side': the upright plane x = 0; 'lift': z = 0.25."""
    if kind == 'side':
        p, q = np.meshgrid(np.linspace(-1.3, 1.3, w), np.linspace(1.3 * h / w, -1.3 * h / w, h)); P = (np.zeros_like(p), p, q)
    else:
        u, s = np.meshgrid(np.linspace(-1.8, 1.8, w), np.linspace(1.8 * h / w, -1.8 * h / w, h))
        P = {'flat': (u, s, np.zeros_like(u)), 'up': (u, np.zeros_like(u), s), 'lift': (u, s, np.full_like(u, 0.25))}[kind]
    if way == 'T':
        return C.tree_inside(*P)
    if way == 'true':
        return (M.flat_stay(P[0], P[1], BODIES[st].c.real, BODIES[st].c.imag, 300) >= 300) & (P[2] == 0)
    return C.carried_inside(BODIES[st], way, *P, nmax=70)


def cuts():
    w, h, pad = 520, 376, 8; t0 = time.time()
    cols = [('b', 'T', 'the balls object as it is'), ('b', 'A', 'c = -1, way A'), ('b', 'B', 'c = -1, way B'), ('b', 'C', 'c = -1, way C'), ('r', 'A', 'rabbit, way A'), ('r', 'B', 'rabbit, way B')]
    rows = [('flat', 'flat cut'), ('up', 'upright cut through the x-axis'), ('side', 'upright cut across (x = 0)'), ('lift', 'flat cut lifted by 0.25')]
    W = pad + len(cols) * (w + pad); H = 34 + len(rows) * (h + 8)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), 'Cuts of the carried object (working picture).', fill=(240, 240, 245), font=M.font(16))
    for j, (st, way, cn) in enumerate(cols):
        for i, (kind, rn) in enumerate(rows):
            ins = cut_plane(st, way, kind, w, h); img = np.zeros((h, w, 3), np.uint8); img[:] = (22, 28, 46); img[ins] = (238, 228, 200)
            x = pad + j * (w + pad); y = 34 + i * (h + 8)
            im.paste(Image.fromarray(img), (x, y)); d.text((x + 4, y + 2), cn + ', ' + rn, fill=(150, 160, 175), font=M.font(13))
        print('cuts', cn, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'cuts.png')); print('wrote cuts.png')


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'solid':
        ext = [int(v) for v in sys.argv[5:8]]
        solid(sys.argv[2], sys.argv[3], sys.argv[4], *ext)
    elif a == 'cuts':
        cuts()
    else:
        t0 = time.time(); dep, px = M.solid(C.tree_rule('gauss'), C.ZERO, 200, 150, 80, 14); print('the balls object itself, 200 x 150 x 80: %.0f s' % (time.time() - t0))
        t0 = time.time(); dep, px = M.solid(C.carried(C.BASILICA, 'A', nmax=48), C.ZERO, 200, 150, 80, 2); print('carried, way A, 200 x 150 x 80: %.0f s' % (time.time() - t0))
