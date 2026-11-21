"""Zoomed cuts ACROSS the x-axis at x = 0 through single buds of the basilica (c = -1), 120 steps, 360 x 360 places
each, window 0.36 wide: is a bud round in this cut, and what are the thin arcs that the walk round the axis met
beside it?   python out/r21/judge/budzoom.py  ->  budzoom.png
Tiles: for each rule the bud at the flat page (y up to the right in the cut), the bud at the upright sheet, and for
along and the hand-over rule also the bud at 45 degrees."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
N, HW, STEPS, RAD = 360, 0.18, 120, 0.62
ROWS = [('along', (0.0, 90.0, 45.0)), ('sheet.evc005e70k16', (0.0, 90.0, 45.0)), ('alongmem.c_wake1', (0.0, 90.0, 45.0)), ('oneplane', (0.0, 90.0, 45.0))]
pad = 8
im = Image.new('RGB', (pad + 3 * (N + pad), 44 + len(ROWS) * (N + 40)), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'Cuts across the x-axis at x = 0 through one bud of the basilica, 120 steps. Window 0.36 wide; the x-axis is toward the bottom of each tile.', fill=(240, 240, 245), font=M.font(16))
for i, (nm, angs) in enumerate(ROWS):
    r = J.get(nm); y0 = 44 + i * (N + 40); d.text((pad, y0), nm, fill=(235, 220, 170), font=M.font(15))
    for j, a in enumerate(angs):
        t = np.radians(a); u, v = np.meshgrid(np.linspace(-HW, HW, N), np.linspace(HW, -HW, N))       # u: round the axis, v: away from the axis
        rad = RAD + v; y = rad * np.cos(t) - u * np.sin(t); z = rad * np.sin(t) + u * np.cos(t)
        n = M.stay(r, np.zeros_like(y), y, z, -1.0, 0.0, 0.0, STEPS)
        x = pad + j * (N + pad); d.text((x, y0 + 18), 'bud at %g degrees from the flat page' % a, fill=(150, 160, 175), font=M.font(12))
        im.paste(Image.fromarray(M.shade(n, STEPS)), (x, y0 + 34))
    print(nm); sys.stdout.flush()
im.save(os.path.join(J.HERE, 'budzoom.png'))
