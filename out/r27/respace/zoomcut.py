"""A closer look at upright cuts of the carried object (working picture zoom-upright-fit.png)."""
import sys
import numpy as np
from PIL import Image, ImageDraw
import carry as C

w, h = 900, 520
panels = []
for way in ('F', 'G'):
    for (x0, x1, z0, z1, yy) in ((-1.0, 0.4, -0.05, 0.76, 0.0), (-1.0, 0.4, -0.05, 0.76, 0.08)):
        u, s = np.meshgrid(np.linspace(x0, x1, w), np.linspace(z1, z0, h))
        ins = C.carried_inside(C.BASILICA, way, u, np.full_like(u, yy), s, nmax=90)
        img = np.zeros((h, w, 3), np.uint8); img[:] = (22, 28, 46); img[ins] = (238, 228, 200)
        panels.append((Image.fromarray(img), 'way %s, upright cut at y = %.2f, x from %.1f to %.1f' % (way, yy, x0, x1)))
im = Image.new('RGB', (2 * w + 30, 2 * (h + 30) + 10), (12, 14, 20)); d = ImageDraw.Draw(im)
for i, (p, t) in enumerate(panels):
    x = 10 + (i % 2) * (w + 10); y = 30 + (i // 2) * (h + 30)
    im.paste(p, (x, y)); d.text((x + 4, y - 20), t, fill=(200, 205, 215), font=C.M.font(14))
im.save('zoom-upright-fit.png'); print('wrote zoom-upright-fit.png')
