"""Round 15, entry: the contact sheet out/r15/entry/sheet-sqpillow.png, with plain-word labels."""
import os
from PIL import Image, ImageDraw, ImageFont

D = 'out/r15/entry/'
try:
    FONT = ImageFont.truetype('arial.ttf', 15); BOLD = ImageFont.truetype('arialbd.ttf', 19)
except OSError:
    FONT = BOLD = ImageFont.load_default()
TW, TH, GAP, CAP = 300, 286, 8, 40
COLS = 6

ROWS = [
    ('Square pillow, power 2: the Mandelbrot solid (one lopsided rock with fins; it is not the same above and below)', [
        ('sp-m', 'opening view'), ('sp-m-above', 'from above'), ('sp-m-below', 'from below'), ('sp-m-side', 'from the side (along y)'),
        ('sp-cut-m', 'cut at z = 0: the flat Mandelbrot set'), ('ref-cut-m', 'the same cut, Sphere inversions, one plane:\nno pixel differs')]),
    ('Julia sets, opening view', [
        ('sp-j-basilica', 'c = -1'), ('sp-j-rabbit', 'the rabbit, c = (-0.12, 0.74, 0)'), ('sp-j-off-axis', 'c = (-1, 0.15, 0.1)'),
        ('sp-j-03', 'c = (0.3, 0, 0)'), ('sp-j-i', 'c = i = (0, 1, 0)'), ('sp-j-i-below', 'c = i from below')]),
    ('Julia sets: from below, and the cuts at z = 0 (each is the flat Julia set)', [
        ('sp-j-basilica-below', 'c = -1 from below'), ('sp-j-rabbit-below', 'the rabbit from below'), ('sp-cut-j-basilica', 'cut at z = 0, c = -1'),
        ('sp-cut-j-rabbit', 'cut at z = 0, the rabbit'), ('sp-cut-j-03', 'cut at z = 0, c = 0.3'), ('sp-cut-j-i', 'cut at z = 0, c = i')]),
    ('Close-up 1, c = -1, the skin of the middle body: camera 1, 0.25 and 0.06 away (14, 20, 26 steps). Right: plain point-by-point cuts at the same place, 0.8, 0.2 and 0.05 wide (cream = in the solid)', [
        ('sp-close-bas-body-1', 'camera 1 away'), ('sp-close-bas-body-2', 'camera 0.25 away'), ('sp-close-bas-body-3', 'camera 0.06 away'),
        ('brute-bas-body-1', 'cut 0.8 wide'), ('brute-bas-body-2', 'cut 0.2 wide'), ('brute-bas-body-3', 'cut 0.05 wide')]),
    ('Close-up 2, c = -1, the skin above the point where two flat bodies touch (-0.618, 0, 0). The point itself lies inside the solid: the bodies do not come apart', [
        ('sp-close-bas-meet-1', 'camera 1 away'), ('sp-close-bas-meet-2', 'camera 0.25 away'), ('sp-close-bas-meet-3', 'camera 0.06 away'),
        ('brute-bas-meet-1', 'cut 0.8 wide'), ('brute-bas-meet-2', 'cut 0.2 wide'), ('brute-bas-meet-3', 'cut 0.05 wide')]),
    ('Close-up 3, the rabbit, the skin of a body, and point-by-point cuts at the same place', [
        ('sp-close-rab-body-1', 'camera 1 away'), ('sp-close-rab-body-2', 'camera 0.25 away'), ('sp-close-rab-body-3', 'camera 0.06 away'),
        ('brute-rab-body-1', 'cut 0.8 wide'), ('brute-rab-body-2', 'cut 0.2 wide'), ('brute-rab-body-3', 'cut 0.05 wide')]),
    ('Close-up 4, the rabbit, the skin above the point where its three flat bodies meet.   Then the powers 3, 4 and 5 (opening view only)', [
        ('sp-close-rab-meet-1', 'camera 1 away'), ('sp-close-rab-meet-2', 'camera 0.25 away'), ('sp-close-rab-meet-3', 'camera 0.06 away'),
        ('sp-m-n3', 'power 3, Mandelbrot solid'), ('sp-m-n4', 'power 4, Mandelbrot solid'), ('sp-m-n5', 'power 5, Mandelbrot solid')]),
    ('Power 3 (mirror-symmetric above and below)', [
        ('sp-m-n3-side', 'power 3, Mandelbrot solid from the side'), ('sp-cut-m-n3', 'power 3, cut at z = 0: the flat set of z^3 + c'), ('sp-j-n3', 'power 3, Julia set, c = (0.3, 0.5, 0)')]),
    ('Close-up 5, POWER 3, the Julia set c = (0.3, 0.5, 0): buds with smaller buds on them, no streaks (one set, one place). Right: point-by-point cuts at the same place', [
        ('sp-close-n3-j-1', 'camera 1 away'), ('sp-close-n3-j-2', 'camera 0.25 away'), ('sp-close-n3-j-3', 'camera 0.06 away'),
        ('brute-n3-j-1', 'cut 0.8 wide'), ('brute-n3-j-2', 'cut 0.2 wide'), ('brute-n3-j-3', 'cut 0.05 wide')]),
]
NOTE = ('What came out: the slice at z = 0 is exactly the flat set and no tear was found. But at power 2 the skin is streaked sheets, blades and slits at every depth looked at, not smaller bodies; '
        'the bodies of c = -1 stay joined (cut through the touching point: 24 % of the cut through the middle; Sphere inversions, one plane: 4 %). Powers 3 to 5 show knobbly buds on corners and rims. Power 3 close up (one Julia set, one place, last row): buds with smaller buds on them, no streaks.')

H = 60 + sum(34 + TH + CAP + GAP for _ in ROWS) + 20
W = COLS * (TW + GAP) + GAP
sheet = Image.new('RGB', (W, H), (16, 18, 24))
d = ImageDraw.Draw(sheet)
# the note, wrapped
words, lines, cur = NOTE.split(' '), [], ''
for w in words:
    if d.textlength(cur + ' ' + w, font=FONT) > W - 24:
        lines.append(cur); cur = w
    else:
        cur = (cur + ' ' + w).strip()
lines.append(cur)
for i, l in enumerate(lines[:3]):
    d.text((12, 6 + 18 * i), l, fill=(255, 214, 140), font=FONT)
y = 62
missing = []
for title, tiles in ROWS:
    d.text((12, y + 6), title, fill=(240, 240, 240), font=BOLD if d.textlength(title, font=BOLD) < W - 24 else FONT)
    y += 34
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
sheet.save(D + 'sheet-sqpillow.png')
print('wrote', D + 'sheet-sqpillow.png', sheet.size, 'missing:', missing)
