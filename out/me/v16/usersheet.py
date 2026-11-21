"""The picture for the user: the basilica of the two new entries from the lab's own renderer, beside the two-plane
look, and the same three skins close up, worked point by point."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T
cols = [('Two planes, as before (the look you liked; tears for c off the x-axis)', 'fold-bas-40.png', 'closecut-twoplane.png', 'clean'),
        ('Turning plane, along (new, no tear)', 'along-bas-40.png', 'closecut-along.png', 'thin fins, tufts of hair, droplets'),
        ('Turning plane, away (new, no tear)', 'away-bas-40.png', 'closecut-away.png', 'whiskers and loose specks')]
W = 700; pad = 14
tiles = []
for title, lab, cc, word in cols:
    a = Image.open(os.path.join(HERE, lab)).convert('RGB'); a = a.crop((0, 0, a.width - 130, a.height))
    a = a.resize((W, round(a.height * W / a.width)), Image.LANCZOS)
    c = Image.open(os.path.join(ROOT, 'out', 'me', 'r16', cc)).convert('RGB').crop((620, 36, 1220, 456)).resize((W, 490), Image.LANCZOS)
    tiles.append((title, a, c, word))
h1 = max(t[1].height for t in tiles)
H = 96 + h1 + 60 + 490 + 20
im = Image.new('RGB', (pad + 3 * (W + pad), H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 10), 'The basilica (c = -1) under the two new rules, beside the two-plane look', fill=(240, 240, 245), font=T.font(28))
d.text((pad, 50), 'Top: the lab itself, 40 iterations.   Bottom: the skin between the special planes, 0.04 wide, worked point by point (cream = inside).', fill=(170, 178, 192), font=T.font(18))
for j, (title, a, c, word) in enumerate(tiles):
    x = pad + j * (W + pad)
    d.text((x, 80), title, fill=(225, 228, 235), font=T.font(19))
    im.paste(a, (x, 108))
    d.text((x, 108 + h1 + 14), 'Skin close up: ' + word, fill=(225, 228, 235), font=T.font(19))
    im.paste(c, (x, 108 + h1 + 44))
im.save(os.path.join(HERE, 'basilica-check.png'))
print(im.size)
