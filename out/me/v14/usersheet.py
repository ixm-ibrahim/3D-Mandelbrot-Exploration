"""A labelled sheet of the five new approaches for the user: python out/me/v14/usersheet.py -> out/me/v14/new-approaches.png"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = os.path.join(ROOT, 'out', 'r14', 'rules')
ROWS = [
 ('Quaternions, 4D (slices)',
  'With the dials at 0 it is the quaternion square, pixel for pixel. Moving or tilting the slice gives smaller rings, then a plain ball.',
  [('quat4-m', 'Mandelbrot solid, slice through the middle'), ('quat4-m-w03', 'Slice moved 0.3 along the fourth axis'), ('quat4-m-tilt45', 'Slice tilted 45 degrees'),
   ('quat4-m-tilt90', 'Slice tilted 90 degrees: a ball'), ('quat4-j-rabbit', 'Julia set, the rabbit')]),
 ('Rotor square (geometric algebra)',
  'The recipe from your image. It is the quaternion square again, turned to stand on the reference axis.',
  [('rotor-m', 'Mandelbrot solid, reference = z-axis (as in the image)'), ('rotor-cut-m', 'Its slice at z = 0: not the flat set'), ('rotor-m-x', 'Reference = x-axis: the quaternion square'),
   ('rotor-cut-m-x', 'Its slice at z = 0: the flat set'), ('rotor-j-basilica', 'Julia set, c = -1, reference = z-axis')]),
 ('Rotor square with a frame',
  'A rule the list did not have. The slice is exact. Smooth wound sheets, with one crushed half-plane (the big flat wall).',
  [('rotorframe-m', 'Mandelbrot solid'), ('rotorframe-cut-m', 'Its slice at z = 0: the flat set'), ('rotorframe-j-basilica', 'Julia set, c = -1'),
   ('rotorframe-j-rabbit', 'Julia set, the rabbit'), ('rotorframe-j-off-axis', 'Julia set, c off the flat plane')]),
 ('Kleinian squaring, one plane',
  "The paper's first construction, as I read it. The slice is a cousin of the flat set, with straighter edges.",
  [('kleinsq-m', 'Mandelbrot solid'), ('kleinsq-cut-m', 'Its slice at z = 0: a cousin, not the flat set'), ('kleinsq-j-basilica', 'Julia set, c = -1'),
   ('kleinsq-j-rabbit', 'Julia set, the rabbit'), ('kleinsq-j-off-axis', 'Julia set, c off the flat plane: shards')]),
 ('Kleinian squaring, two planes',
  "The paper's second construction. Buds round two circles when c is on the x-axis. Shards everywhere else.",
  [('kleinsq2-m', 'Mandelbrot solid: shards'), ('kleinsq2-cut-m', 'Its slice at z = 0: the same cousin'), ('kleinsq2-j-basilica', 'Julia set, c = -1: buds round two circles'),
   ('kleinsq2-j-rabbit', 'Julia set, the rabbit: shards'), ('kleinsq2-j-off-axis', 'Julia set, c off the flat plane: shards')]),
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
tiles = [[tile(n, w) for n, _ in r[2]] for r in ROWS]
h = tiles[0][0].size[1]
rowh = head + h + cap
sheet = Image.new('RGB', (pad * 2 + w * 5, pad + rowh * len(ROWS)), (12, 14, 20))
d = ImageDraw.Draw(sheet)
big, mid, small = font(22, True), font(17), font(15)
for r, (title, verdict, items) in enumerate(ROWS):
    y = pad + r * rowh
    d.text((pad, y + 2), title, fill=(245, 245, 245), font=big)
    d.text((pad, y + 32), verdict, fill=(205, 208, 215), font=mid)
    for k, (_, label) in enumerate(items):
        sheet.paste(tiles[r][k], (pad + k * w, y + head))
        d.text((pad + k * w + 6, y + head + h + 5), label, fill=(225, 225, 225), font=small)
out = os.path.join(ROOT, 'out', 'me', 'v14', 'new-approaches.png')
sheet.save(out)
print('wrote', out, sheet.size)
