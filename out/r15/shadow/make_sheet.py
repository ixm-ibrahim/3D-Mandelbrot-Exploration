"""Round 15B, shadow: the contact sheet out/r15/shadow/sheet-pillow4d.png, with plain-word labels.
(Layout code after out/r15/entry/make_sheet.py.) The words of the note and the row titles are in sheet_words.py."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet_words import NOTE, ROWS

D = 'out/r15/shadow/'
try:
    FONT = ImageFont.truetype('arial.ttf', 15); BOLD = ImageFont.truetype('arialbd.ttf', 19)
except OSError:
    FONT = BOLD = ImageFont.load_default()
TW, TH, GAP, CAP = 300, 286, 8, 40
COLS = 6

W = COLS * (TW + GAP) + GAP
probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))


def wrap(text, font, width):
    lines = []
    for para in text.split('\n'):
        cur = ''
        for w in para.split(' '):
            if cur and probe.textlength(cur + ' ' + w, font=font) > width:
                lines.append(cur); cur = w
            else:
                cur = (cur + ' ' + w).strip()
        lines.append(cur)
    return lines


note = wrap(NOTE, FONT, W - 24)
titles = [wrap(t, BOLD, W - 24) for t, _ in ROWS]
H = 12 + 19 * len(note) + 10 + sum(8 + 24 * len(t) + TH + CAP + GAP for t in titles) + 12
sheet = Image.new('RGB', (W, H), (16, 18, 24))
d = ImageDraw.Draw(sheet)
y = 8
for l in note:
    d.text((12, y), l, fill=(255, 214, 140), font=FONT); y += 19
y += 10
missing = []
for (title, tiles), tl in zip(ROWS, titles):
    y += 6
    for l in tl:
        d.text((12, y), l, fill=(240, 240, 240), font=BOLD); y += 24
    y += 2
    for k, (name, cap) in enumerate(tiles):
        p = D + name + '.png'
        x = GAP + k * (TW + GAP)
        if not os.path.exists(p):
            missing.append(name); continue
        im = Image.open(p).convert('RGB')
        if im.size[0] > 800:
            im = im.crop((0, 0, 735, im.size[1]))     # leave out the page's zoom slider at the right
        im.thumbnail((TW, TH), Image.LANCZOS)
        sheet.paste(im, (x + (TW - im.size[0]) // 2, y))
        for j, l in enumerate(cap.split('\n')):
            d.text((x + 2, y + TH + 3 + 17 * j), l, fill=(205, 210, 220), font=FONT)
    y += TH + CAP + GAP
sheet.save(D + 'sheet-pillow4d.png')
print('wrote', D + 'sheet-pillow4d.png', sheet.size, 'missing:', missing)
