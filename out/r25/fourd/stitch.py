"""Put the rows of the rough-solid sheets into one sheet per eye: python out/r25/fourd/stitch.py"""
import os
from PIL import Image, ImageDraw
import four as F
HERE = os.path.dirname(os.path.abspath(__file__)); ROWH = 285 + 36; TOP = 56


def rows_of(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        print('missing', name); return []
    im = Image.open(p).convert('RGB'); n = (im.size[1] - TOP) // ROWH
    return [im.crop((0, TOP + i * ROWH, im.size[0], TOP + (i + 1) * ROWH)) for i in range(n)]


def build(eye, parts, out, title):
    rows = []
    for name, keep in parts:
        r = rows_of(name); rows += [r[i] for i in keep if i < len(r)]
    W = max(r.size[0] for r in rows); im = Image.new('RGB', (W, TOP + len(rows) * ROWH), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((10, 10), title, fill=(240, 240, 245), font=F.M.font(20))
    for i, r in enumerate(rows):
        im.paste(r, (0, TOP + i * ROWH))
    im.save(os.path.join(HERE, out)); print('wrote', out, im.size)


if __name__ == '__main__':
    build('a', [('solids-product-a.png', [0]), ('solids-spinor-a.png', [0, 1]), ('solids-anylift-a.png', [0]), ('solids-product-a.png', [1]), ('solids-pairs-a.png', [0, 1])],
          'sheet.png', 'fourd, front eye. Left c = -1, right the rabbit. 110 to 200 blocks deep.')
    build('top', [('solids-main-top.png', [0, 2, 3]), ('solids-anylift-top.png', [0]), ('solids-main-top.png', [1]), ('solids-pairs-top.png', [0, 1])],
          'sheet-top.png', 'fourd, eye from above. Left c = -1, right the rabbit. 90 to 160 blocks deep.')
