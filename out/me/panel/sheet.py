"""Compose out/me/panel/panel-<part>.png from the lab pictures: one row per Julia set."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, HERE)
import truth as T
from shots import PANEL
COLS = [('flat', 'Cut at z = 0 (the flat set when c is in the flat plane)'), ('along-above', 'Turning plane, along: from above'),
        ('along-side', 'Turning plane, along: from the side'), ('one-side', 'One plane, from the side (yardstick)')]
W = 520; pad = 12
def tile(tag, col):
    a = Image.open(os.path.join(HERE, f'{tag}-{col}.png')).convert('RGB')
    a = a.crop((40, 60, a.width - 150, a.height - 70))
    return a.resize((W, round(a.height * W / a.width)), Image.LANCZOS)
def sheet(rows, name, title):
    th = tile(rows[0][0], 'flat').height
    H = 70 + len(rows) * (th + 34 + pad)
    im = Image.new('RGB', (pad + len(COLS) * (W + pad), H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(240, 240, 245), font=T.font(26))
    for j, (_, ct) in enumerate(COLS):
        d.text((pad + j * (W + pad), 46), ct, fill=(165, 175, 190), font=T.font(16))
    for i, (tag, nm, c, it) in enumerate(rows):
        y = 70 + i * (th + 34 + pad)
        d.text((pad, y + 4), f'{nm}   ({it} iterations)', fill=(228, 230, 236), font=T.font(19))
        for j, (col, _) in enumerate(COLS):
            im.paste(tile(tag, col), (pad + j * (W + pad), y + 32))
    im.save(os.path.join(HERE, name)); print(name, im.size)
sheet(PANEL[:4], 'panel-axis.png', 'Julia sets with c on the x-axis')
sheet(PANEL[4:7], 'panel-plane.png', 'Julia sets with c in the flat plane, off the x-axis')
sheet(PANEL[7:], 'panel-off.png', 'Julia sets with c out of the flat plane')
