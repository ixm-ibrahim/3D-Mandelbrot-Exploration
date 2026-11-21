"""Second picture for the user. python out/r22/stability/rabbit_pages.py -> out/r22/stability/rabbit-pages.png
The rabbit, cut along pages through the x-axis turned 0, 11, 22, 34 and 45 degrees from the flat page, for the lathe,
along and one plane. Plain: pale = inside the shape."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import stab as T
M = T.M

ANG = [0.0, 11.25, 22.5, 33.75, 45.0]; W, Hh = 330, 250; BOX = (-1.65, 1.65, -1.25, 1.25); pad = 14; STEPS = 100
ROWS = [('lathe', 'Quaternion square (Lathe)', 'The rabbit stays whole as the page is turned: its bodies stay joined, only the ears fray. Stacked up, the slices make one lump.'),
        ('along', 'Turning plane, along', 'The same here: the rabbit is still there when the page is turned, fatter and frayed, its bodies still joined. Two thirds of this lump is the lathe\'s lump.'),
        ('oneplane', 'Sphere inversions, one plane', 'Turn the page a little and the rabbit has fallen apart into separate smooth blobs. Clean bodies, but nothing of the rabbit\'s shape off the flat page.')]


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(22), M.font(17), M.font(15)
    Wd = pad + len(ANG) * (W + pad); rowh = 32 + 22 + Hh + 8 + 26 + 26
    im = Image.new('RGB', (Wd, 120 + len(ROWS) * rowh), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'The rabbit, sliced along pages turned away from the flat page', fill=(240, 240, 245), font=f_t)
    d.text((pad, 58), 'Every page goes through the x-axis, like the pages of a book whose spine is the x-axis. The first slice is the flat page itself: the flat picture.', fill=(175, 182, 196), font=f_c)
    d.text((pad, 82), 'Pale = inside the shape. The x-axis runs left to right through the middle of every slice.', fill=(175, 182, 196), font=f_c)
    y = 120
    for name, head, cap in ROWS:
        r = M.bench(name); d.text((pad, y), head, fill=(240, 222, 160), font=f_h); y += 32
        for j, a in enumerate(ANG):
            x = pad + j * (W + pad)
            d.text((x, y), 'the flat page' if a == 0 else 'page turned %s degrees' % ('%g' % round(a)), fill=(160, 168, 182), font=f_s)
            n = M.cut_axis(r, a, W, Hh, STEPS, c=T.RABBIT, box=BOX)
            im.paste(Image.fromarray(M.shade(n, STEPS)), (x, y + 22))
            print(name, a, 'inside %d px' % (n >= STEPS).sum()); sys.stdout.flush()
        y += 22 + Hh + 8
        d.text((pad, y), cap, fill=(218, 221, 229), font=f_c); y += 26 + 26
    im = im.crop((0, 0, Wd, y - 14)); out = os.path.join(T.HERE, 'rabbit-pages.png'); im.save(out); print(out, im.size, '%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
