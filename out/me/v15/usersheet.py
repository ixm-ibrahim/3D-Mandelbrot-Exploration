"""A compact labelled sheet of the Square pillow entry, from the lab's own renderer: python out/me/v15/usersheet.py"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = os.path.join(ROOT, 'out', 'r15', 'entry')
ROWS = [
 ('Power 2 (the square)', 'Slice exact, no tear. But the Mandelbrot solid is a lopsided rock with fins, and the basilica (c = -1) is one spiky spindle, not a row of bodies.',
  [('sp-m', 'Mandelbrot solid'), ('sp-cut-m', 'Its slice at z = 0: the flat set'), ('sp-j-basilica', 'Julia set, c = -1: bodies stay joined'),
   ('sp-j-rabbit', 'Julia set, the rabbit'), ('sp-close-bas-body-2', 'Close up, c = -1: streaks, not small bodies')]),
 ('Power 3 (the cube)', 'The same above and below the plane. Julia sets grow buds with smaller buds on them. The Mandelbrot solid is a block with buds on its corners.',
  [('sp-m-n3', 'Mandelbrot solid'), ('sp-m-n3-side', 'The same from the side'), ('sp-j-n3', 'Julia set, c = (0.3, 0.5, 0)'),
   ('sp-close-n3-j-1', 'Close up: buds'), ('sp-close-n3-j-2', 'Closer: smaller buds on the buds')]),
 ('Powers 4 and 5', 'More buds as the power goes up, on corners and rims. Seen from the opening view only.',
  [('sp-m-n4', 'Power 4, Mandelbrot solid'), ('sp-m-n5', 'Power 5, Mandelbrot solid')]),
]
def font(size, bold=False):
    for name in (('segoeuib.ttf', 'arialbd.ttf') if bold else ('segoeui.ttf', 'arial.ttf')):
        try: return ImageFont.truetype(name, size)
        except OSError: pass
    return ImageFont.load_default()
def tile(name, w):
    im = Image.open(os.path.join(D, name + '.png')).convert('RGB')
    W, H = im.size
    im = im.crop((0, int(H * 0.03), int(W * 0.84), int(H * 0.92)))
    return im.resize((w, int(im.size[1] * w / im.size[0])), Image.LANCZOS)
w, pad, head, cap = 400, 14, 64, 30
h = tile('sp-m', w).size[1]
rowh = head + h + cap
sheet = Image.new('RGB', (pad * 2 + w * 5, pad + rowh * len(ROWS)), (12, 14, 20))
d = ImageDraw.Draw(sheet); big, mid, small = font(22, True), font(17), font(15)
for r, (title, verdict, items) in enumerate(ROWS):
    y = pad + r * rowh
    d.text((pad, y + 2), 'Square pillow: ' + title, fill=(245, 245, 245), font=big)
    d.text((pad, y + 32), verdict, fill=(205, 208, 215), font=mid)
    for k, (n, label) in enumerate(items):
        sheet.paste(tile(n, w), (pad + k * w, y + head))
        d.text((pad + k * w + 6, y + head + h + 5), label, fill=(225, 225, 225), font=small)
out = os.path.join(ROOT, 'out', 'me', 'v15', 'square-pillow.png')
sheet.save(out); print('wrote', out, sheet.size)
