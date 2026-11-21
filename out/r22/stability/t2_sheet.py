"""t2: my own contact sheets (not for the user). python out/r22/stability/t2_sheet.py [basilica|rabbit|siegel]
One row per rule. Cuts across the x-axis and along pages turned 0, 11.25, 22.5, 33.75, 45, 90 degrees, coloured by what one
step does to a tiny ball there (teal keeps shapes, amber squeezes < 3, orange squeezes harder, purple inside out);
bright = inside the solid, white = its outline. Also prints the share of the solid's cut by kind."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import stab as T, zones as Z
M = T.M

which = sys.argv[1] if len(sys.argv) > 1 else 'basilica'
c = {'basilica': T.BAS, 'rabbit': T.RABBIT, 'siegel': T.SIEGEL, 'marco': T.MARCO}[which]
W = 260; BOX = (-1.8, 1.8, -1.3, 1.3); STEPS = 60
across = [0.0, -1.0, -0.4] if which in ('basilica', 'marco') else [0.0, -0.3, 0.3]
kinds = [('across', a) for a in across] + [('page', a) for a in (0.0, 11.25, 22.5, 33.75, 45.0, 90.0)]
pad = 8; t0 = time.time()
tw = [W if k[0] == 'across' else int(W * 3.6 / 2.6) for k in kinds]; th = W
im = Image.new('RGB', (pad + sum(t + pad for t in tw), 40 + len(T.NAMES) * (th + 30)), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), '%s, c = %s: one step under the glass (teal keeps shapes, amber squeezes, orange hard, purple inside out)' % (which, (c,)), fill=(240, 240, 245), font=M.font(18))
for i, nm in enumerate(T.NAMES):
    y = 40 + i * (th + 30); x = pad
    for k, w in zip(kinds, tw):
        ext = 1.25 if k[0] == 'across' else BOX
        img, cat, ins = Z.tile(nm, k, c, w if k[0] == 'page' else W, ext, STEPS)
        if k[0] == 'page':
            img = img[:th] if img.shape[0] >= th else img
        im.paste(Image.fromarray(img), (x, y + 22))
        d.text((x, y + 2), '%s %s %g' % (nm, k[0], k[1]), fill=(170, 178, 192), font=M.font(13))
        n = max(int(ins.sum()), 1)
        print('%-9s %-9s %-7s %6g: inside %6d px | of the inside: keeps %5.1f %%, squeezes %5.1f %%, hard %5.1f %%, inside out %5.1f %%'
              % (which, nm, k[0], k[1], ins.sum(), *(100 * ((cat == j) & ins).sum() / n for j in range(4)))); sys.stdout.flush()
        x += w + pad
    print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = os.path.join(T.HERE, 'own-zones-%s.png' % which); im.save(out); print(out, im.size)
