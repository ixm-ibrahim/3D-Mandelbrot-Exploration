"""One sheet for the record: for each rule its bench views and cuts (from out/r16/bench/sheets/<rule>.png) and the
first row of its close cut (out/me/r16/closecut-<rule>.png), with a plain label.
    python out/r19/rational/sheet.py rule=label ..."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
try:
    FONT = ImageFont.truetype('segoeui.ttf', 22); SMALL = ImageFont.truetype('segoeui.ttf', 16)
except Exception:
    FONT = SMALL = ImageFont.load_default()
rows = []
for a in sys.argv[1:]:
    nm, _, label = a.partition('=')
    b = os.path.join(ROOT, 'out', 'r16', 'bench', 'sheets', nm + '.png'); c = os.path.join(ROOT, 'out', 'me', 'r16', 'closecut-' + nm + '.png')
    tiles = []
    if os.path.exists(b):
        im = Image.open(b).convert('RGB'); tiles.append(im.crop((0, 42, 2415, 360)))      # views, four cuts, close-up 1
    if os.path.exists(c):
        im = Image.open(c).convert('RGB'); w, h = im.size
        t = im.crop((0, 0, w, h // 2)); k = 318 / t.size[1]; tiles.append(t.resize((int(t.size[0] * k), 318)))
    rows.append((nm, label, tiles))
W = max(sum(t.size[0] for t in tl) + 20 * len(tl) for _, _, tl in rows) + 20
H = sum(40 + 338 + 16 for _ in rows) + 60
out = Image.new('RGB', (W, H), (11, 13, 18)); d = ImageDraw.Draw(out)
d.text((14, 10), 'Round 19, "rational": the basilica (c = -1) under rules whose surplus keeps angles. Left: bench views and cuts. Right: the skin close up, 22.5 degrees off the flat plane, three widths.', font=FONT, fill=(235, 235, 235))
y = 52
for nm, label, tl in rows:
    d.text((14, y), '%s: %s' % (nm, label), font=FONT, fill=(240, 220, 170)); y += 36
    x = 14
    for t in tl:
        out.paste(t, (x, y)); x += t.size[0] + 20
    y += 338 + 20
out.save(os.path.join(HERE, 'sheet.png')); print('wrote', os.path.join(HERE, 'sheet.png'), out.size)
