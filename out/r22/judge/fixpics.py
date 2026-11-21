"""Judge: the five pictures for the user, in the order of the questions Q1..Q4.   python out/r22/judge/fixpics.py

Each is a section's picture, copied here; where a label had to be mended only TEXT bands are touched (painted over with
the background and rewritten, or a blank band inserted). No computed panel is changed. What was changed is listed in
NOTES.md, section 3."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
R22 = os.path.dirname(HERE)
BG = (12, 14, 20); GREY = (170, 178, 192); TXT = (215, 218, 226); GOLD = (240, 222, 160)


def wrap(d, text, font, width):
    words = text.split(); lines = []; cur = ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur); return lines


def insert_band(im, y, h):
    W, H = im.size; out = Image.new('RGB', (W, H + h), BG)
    out.paste(im.crop((0, 0, W, y)), (0, 0)); out.paste(im.crop((0, y, W, H)), (0, y + h)); return out


def band_is_text_only(im, y0, y1):
    """Guard: the band to be painted over must hold no picture tile (only background and text)."""
    px = im.crop((0, y0, im.size[0], y1)).convert('RGB'); data = px.getdata(); n = 0
    for p in data:
        if abs(p[0] - BG[0]) > 6 or abs(p[1] - BG[1]) > 6 or abs(p[2] - BG[2]) > 6:
            n += 1
    return n / (px.size[0] * px.size[1])


f17, f18, f16 = M.font(17), M.font(18), M.font(16)

# ---------------------------------------------------------------------------------------- 1 (Q1, Q3)
im = Image.open(os.path.join(R22, 'buds', 'bud-two-steps.png')).convert('RGB'); W = im.size[0]
line = ('What a "page" is: think of a book whose spine is the x-axis. Every plane through the x-axis is a page of it; the flat page is the one that holds the flat picture. '
        'A rule says which page each point is squared in.')
d0 = ImageDraw.Draw(im); lines = wrap(d0, line, f17, W - 28)
print('1: share of non-background pixels in the gap where the band goes:', band_is_text_only(im, 131, 143))
im = insert_band(im, 131, 24 * len(lines) + 4); d = ImageDraw.Draw(im)
for i, s in enumerate(lines):
    d.text((14, 131 + 24 * i), s, fill=GREY, font=f17)
im.save(os.path.join(HERE, '1-how-a-bud-is-made.png')); print('1', im.size, len(lines), 'lines added')

# ---------------------------------------------------------------------------------------- 2 (Q1, Q3)
im = Image.open(os.path.join(R22, 'buds', 'buds-on-a-bud.png')).convert('RGB')
im.save(os.path.join(HERE, '2-buds-on-a-bud.png')); print('2', im.size, 'copied unchanged')

# ---------------------------------------------------------------------------------------- 3 (Q2, Q3)
im = Image.open(os.path.join(R22, 'lump', 'lump-bodies.png')).convert('RGB'); W = im.size[0]; d = ImageDraw.Draw(im)
y0, y1 = 534, 596
cap = ('The same bodies as in the row below, grown so fat off the flat page that they press against each other along whole walls. '
       'We found no gap between them, so the shape looks like one lump.')
d.rectangle([0, y0, W, y1], fill=BG)
for i, s in enumerate(wrap(d, cap, f17, W - 28)):
    d.text((14, 536 + 24 * i), s, fill=TXT, font=f17)
im.save(os.path.join(HERE, '3-rabbit-same-bodies.png')); print('3', im.size)

# ---------------------------------------------------------------------------------------- 4 (Q2)
im = Image.open(os.path.join(R22, 'lump', 'lump-why.png')).convert('RGB')
im.save(os.path.join(HERE, '4-why-the-bodies-run-together.png')); print('4', im.size, 'copied unchanged')

# ---------------------------------------------------------------------------------------- 5 (Q4)
im = Image.open(os.path.join(R22, 'design', 'q4-tries.png')).convert('RGB'); W, H = im.size
foot = ['A bud can stand off the flat page only if a step throws some places that are off the page onto it. One plane never does that, so its buds stay round the flat page.',
        'The bodies stay apart when the spine of the book runs through the point where the bodies meet. For c = -1 the x-axis does that by itself. For the rabbit, try 1 does it.',
        'Buds on buds need pages that last for more than one step. For c = -1 they last for ever. For the rabbit, in try 1, they last for one step only: ridges instead of buds.',
        'No rule found so far gives all three for the rabbit.']
d0 = ImageDraw.Draw(im); rows = []
for s in foot:
    ls = wrap(d0, s, f16, W - 28 - 18); rows.append(ls)
extra = 16 + 30 + sum(22 * len(ls) + 6 for ls in rows) + 14
out = Image.new('RGB', (W, H + extra), BG); out.paste(im, (0, 0)); d = ImageDraw.Draw(out)
y = H + 8; d.line([14, y, W - 14, y], fill=(60, 66, 80), width=1); y += 8
d.text((14, y), 'What the orbits say, in short', fill=GOLD, font=f18); y += 30
for ls in rows:
    d.ellipse([16, y + 8, 22, y + 14], fill=(225, 228, 235))
    for s in ls:
        d.text((32, y), s, fill=(225, 228, 235), font=f16); y += 22
    y += 6
out.save(os.path.join(HERE, '5-new-tries.png')); print('5', out.size)
