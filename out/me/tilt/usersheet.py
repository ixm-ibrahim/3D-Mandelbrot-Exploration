"""A labelled sheet for the user: python out/me/tilt/usersheet.py -> out/me/tilted-quaternion.png"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = os.path.join(ROOT, 'out', 'me', 'tilt')
TILTS = [0, 15, 30, 45, 60, 90]
ROWS = [('m-%02d', 'Mandelbrot solid'), ('m-%02d-cut', 'The same, cut at z = 0'), ('j-bas-%02d', 'Julia set, c = -1'), ('j-rab-%02d', 'Julia set, the rabbit')]

def font(size):
    for name in ('segoeui.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def tile(path, w):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    im = im.crop((0, int(H * 0.02), int(W * 0.85), int(H * 0.92)))
    return im.resize((w, int(im.size[1] * w / im.size[0])), Image.LANCZOS)

w, left, top = 330, 190, 44
tiles = [[tile(os.path.join(D, (pat % t) + '.png'), w) for t in TILTS] for pat, _ in ROWS]
h = tiles[0][0].size[1]
sheet = Image.new('RGB', (left + w * len(TILTS), top + h * len(ROWS)), (12, 14, 20))
d = ImageDraw.Draw(sheet)
big, small = font(19), font(16)
for k, t in enumerate(TILTS):
    d.text((left + k * w + 10, 11), 'Tilt %d°' % t + (' (the Lathe)' if t == 0 else ''), fill=(240, 240, 240), font=big)
for r, (pat, label) in enumerate(ROWS):
    d.text((10, top + r * h + h // 2 - 10), label, fill=(225, 225, 225), font=small)
    for k in range(len(TILTS)):
        sheet.paste(tiles[r][k], (left + k * w, top + r * h))
out = os.path.join(ROOT, 'out', 'me', 'tilted-quaternion.png')
sheet.save(out)
print('wrote', out, sheet.size)
