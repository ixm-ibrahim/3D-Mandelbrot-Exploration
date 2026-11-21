"""closecut at two more angles (33.75 and 45 degrees from the flat plane), same widths and measure as
out/me/r16/closecut.py, written into this folder.   python out/r19/foldpre/close45.py <rule> ..."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import closecut as C
import truth as T
import rules as R
for nm in sys.argv[1:]:
    F = R.get(nm); rows = []; nums = []
    for ang in (33.75, 45.0):
        e = C.edge(F, ang); tiles = []
        for hw in C.WIDTHS:
            n = T.cut(F, ang, (C.X0 - hw, C.X0 + hw, e - 0.7 * hw, e + 0.7 * hw), C.W, C.H, C.STEPS)
            tiles.append(T.shade(n, C.STEPS)); nums.append(C.hair(n >= C.STEPS))
        rows.append(('%s: plane %s degrees from the flat plane, skin at x = %s (height %.4f), %d steps. Widths 0.2, 0.04, 0.008. hair %.2f, %.2f, %.2f'
                     % (nm, ang, C.X0, e, C.STEPS, nums[-3], nums[-2], nums[-1]), tiles))
    im = Image.new('RGB', (10 + 3 * (C.W + 10), 10 + len(rows) * (C.H + 34)), (12, 14, 20)); d = ImageDraw.Draw(im)
    for i, (t, tiles) in enumerate(rows):
        y = 10 + i * (C.H + 34); d.text((10, y), t, fill=(230, 230, 235), font=T.font(17))
        for j, a in enumerate(tiles): im.paste(Image.fromarray(a), (10 + j * (C.W + 10), y + 26))
    im.save(os.path.join(HERE, 'close45-%s.png' % nm))
    print(nm, 'hair', ' '.join('%.2f' % v for v in nums), flush=True)
