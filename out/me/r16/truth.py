"""Ground truth for 'Turning plane, along': point-by-point cuts of the basilica through the x-axis at
in-between angles, at several step counts. Question: are the ribs round the x-axis that the lab's
renderer draws really there, or do they come from the renderer / a low step count?
No voxels, no renderer: every pixel is one point followed for N steps."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import scout as S
import scout3 as T

OUT = os.path.dirname(__file__)


def member(F, x, y, z, c, steps, r2=36.0):
    """How many steps each point stays inside (steps = never left)."""
    n = np.zeros(x.shape, np.int32)
    alive = np.ones(x.shape, bool)
    x, y, z = x.copy(), y.copy(), z.copy()
    for k in range(steps):
        X, Y, Z = F(x, y, z)
        x = np.where(alive, X + c[0], x); y = np.where(alive, Y + c[1], y); z = np.where(alive, Z + c[2], z)
        alive &= (x * x + y * y + z * z) < r2
        n += alive
    return n


def cut(F, ang, box, w, h, steps, c=(-1.0, 0.0, 0.0)):
    x0, x1, s0, s1 = box
    xs = np.linspace(x0, x1, w); ss = np.linspace(s1, s0, h)
    x, s = np.meshgrid(xs, ss)
    a = np.radians(ang)
    return member(F, x, s * np.cos(a), s * np.sin(a), c, steps)


def shade(n, steps):
    inside = n >= steps
    t = np.clip(n / steps, 0, 1) ** 0.6
    img = np.zeros(n.shape + (3,), np.uint8)
    img[..., 0] = (20 + 40 * t).astype(np.uint8); img[..., 1] = (26 + 70 * t).astype(np.uint8); img[..., 2] = (40 + 150 * t).astype(np.uint8)
    img[inside] = (238, 228, 200)
    return img


def font(sz):
    for f in ('segoeui.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def sheet(name, rule, rows, cols, title, box, w, h):
    pad, top = 10, 70
    W = pad + len(cols) * (w + pad); H = top + len(rows) * (h + 34 + pad)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(235, 235, 240), font=font(24))
    stats = {}
    for i, ang in enumerate(rows):
        for j, steps in enumerate(cols):
            n = cut(rule, ang, box, w, h, steps)
            x = pad + j * (w + pad); y = top + i * (h + 34 + pad)
            d.text((x, y), f'plane turned {ang:g} degrees from the flat plane, {steps} steps', fill=(200, 205, 215), font=font(17))
            im.paste(Image.fromarray(shade(n, steps)), (x, y + 26))
            stats[(ang, steps)] = float((n >= steps).mean())
    im.save(os.path.join(OUT, name))
    return stats


if __name__ == '__main__':
    along = T.turning(+1)
    away = T.turning(-1)
    which = sys.argv[1] if len(sys.argv) > 1 else 'along'
    F = {'along': along, 'away': away, 'two': S.twoplane, 'one': S.oneplane}[which]
    st = sheet(f'truth-{which}-whole.png', F, [0, 11.25, 22.5, 33.75, 45], [14, 26, 60],
               f'{which}: basilica cut through the x-axis, point by point', (-1.75, 1.75, -1.0, 1.0), 700, 400)
    for k, v in st.items():
        print(which, 'whole', k, round(100 * v, 2), '% inside')
    st = sheet(f'truth-{which}-top.png', F, [0, 11.25, 22.5, 33.75, 45], [14, 26, 60],
               f'{which}: the top of the middle body, point by point', (-0.55, 0.55, 0.45, 1.05), 700, 382)
    for k, v in st.items():
        print(which, 'top', k, round(100 * v, 2), '% inside')
