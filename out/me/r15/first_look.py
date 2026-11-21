"""First rough look at the square-pillow rule: voxel solids and cuts. python out/me/r15/first_look.py [N]"""
import os, sys, time, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns')); sys.path.insert(0, HERE)
import turns, pillow_ref as P

N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
ITERS = 30

def grid(cen, L):
    a = np.linspace(-L, L, N)
    X, Y, Z = np.meshgrid(a + cen[0], a + cen[1], a + cen[2], indexing='ij')
    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)

def run(start, c, R=4.0):
    """start (M, 3); c either (3,) or (M, 3). Returns bool inside, int death step."""
    M = start.shape[0]
    v = start.copy(); alive = np.arange(M); death = np.zeros(M, np.int16)
    cc = None if c.ndim == 1 else c
    for k in range(ITERS):
        w = P.F(v) + (c if cc is None else cc[alive])
        r = np.linalg.norm(w, axis=1)
        keep = r <= R
        death[alive[~keep]] = k + 1
        alive, v = alive[keep], w[keep]
        if alive.size == 0: break
    inside = np.zeros(M, bool); inside[alive] = True
    return inside.reshape(N, N, N), death.reshape(N, N, N)

def font(size):
    for n in ('segoeui.ttf', 'arial.ttf'):
        try: return ImageFont.truetype(n, size)
        except OSError: pass
    return ImageFont.load_default()

def cut(vol, death, axis):
    m = N // 2
    a = {'z': vol[:, :, m], 'y': vol[:, m, :], 'x': vol[m, :, :]}[axis]
    d = {'z': death[:, :, m], 'y': death[:, m, :], 'x': death[m, :, :]}[axis]
    img = np.zeros((N, N, 3), np.float32); t = np.clip(d / 14.0, 0, 1)
    for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = 18 + (col - 18) * t
    img[a] = (235, 225, 200)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]

CASES = [('Julia set, c = -1', 'j', (-1.0, 0, 0), (0, 0, 0), 1.75),
         ('Julia set, the rabbit', 'j', (-0.12, 0.74, 0), (0, 0, 0), 1.6),
         ('Julia set, c = (-1, 0.15, 0.1)', 'j', (-1.0, 0.15, 0.1), (0, 0, 0), 1.75),
         ('Mandelbrot solid', 'm', None, (-0.6, 0, 0), 1.6)]
COLS = ['Seen from the front', 'Seen from above', 'Seen from below', 'Cut at z = 0 (the flat plane)', 'Cut at y = 0 (upright plane)', 'Cut at x = centre']
S = 330
sheet = Image.new('RGB', (190 + S * len(COLS), 40 + S * len(CASES)), (12, 14, 20))
dr = ImageDraw.Draw(sheet); f1, f2 = font(17), font(15)
for k, t in enumerate(COLS): dr.text((196 + k * S, 10), t, fill=(235, 235, 235), font=f1)
for r, (name, mode, c, cen, L) in enumerate(CASES):
    t0 = time.time(); g = grid(cen, L)
    vol, death = run(g, np.array(c, float)) if mode == 'j' else run(g.copy(), g)
    print(name, 'volume %.3f' % (vol.mean() * (2 * L) ** 3), 'voxels', int(vol.sum()), '%.0f s' % (time.time() - t0), flush=True)
    np.save(os.path.join(HERE, 'vol-%d-%d.npy' % (r, N)), vol)
    tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=-60, el=75), turns.render(vol, az=-60, el=-70), cut(vol, death, 'z'), cut(vol, death, 'y'), cut(vol, death, 'x')]
    dr.text((10, 40 + r * S + S // 2 - 10), name, fill=(225, 225, 225), font=f2)
    for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((S - 6, S - 6), Image.LANCZOS), (190 + k * S, 40 + r * S))
out = os.path.join(HERE, 'first-look-%d.png' % N)
sheet.save(out); print('wrote', out)
