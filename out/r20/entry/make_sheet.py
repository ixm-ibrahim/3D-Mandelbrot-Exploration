"""Round 20, entry: compose sheet-for-user.png and close.png from the lab's pictures (pics.py) and the point-by-point cuts (brute.py).
python out/r20/entry/make_sheet.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pics import PANEL, ENTRIES, CLOSE

def font(size, bold=False):
    for f in (('segoeuib.ttf' if bold else 'segoeui.ttf'), 'arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()

BG, FG, DIM, WARN = (12, 14, 20), (240, 240, 245), (165, 175, 190), (240, 200, 120)

def tile(path, w, crop=(95, 60, 95, 70)):
    a = Image.open(path).convert('RGB')
    a = a.crop((crop[0], crop[1], a.width - crop[2], a.height - crop[3]))
    return a.resize((w, round(a.height * w / a.width)), Image.LANCZOS)

def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def sheet():
    W, pad = 400, 10
    cols = [(id_, nm, cam) for id_, nm in ENTRIES for cam in ('side', 'above')]
    th = tile(os.path.join(HERE, 'shot-basilica-windsq-side.png'), W).height
    notes = [
        'Julia sets of z -> z^2 + c for seven values of c in the flat plane, drawn by the lab itself with 40 iterations, three rules, the same two cameras ("from the side" looks along the flat plane, a little from above; "from above" looks down on it).',
        'Wind, then square and Turning plane, along are drawn with the Rough distance estimate (the only one that draws nothing false for them); Sphere inversions, one plane with Exact.',
        'For Wind, then square the 3D picture leaves out some thin sheets (measured on the rabbit: 58 of 254 rays that meet the set show nothing). No Mandelbrot solid of the new rule has been drawn or judged.',
    ]
    head = 54 + 22 * len(notes) + 30
    H = head + len(PANEL) * (th + 30 + pad) + pad
    im = Image.new('RGB', (pad + len(cols) * (W + pad), H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Wind, then square (new) beside Turning plane, along and Sphere inversions, one plane', fill=FG, font=font(28, True))
    for k, t in enumerate(notes):
        d.text((pad, 50 + 22 * k), t, fill=WARN if k == 2 else DIM, font=font(15))
    for j, (id_, nm, cam) in enumerate(cols):
        d.text((pad + j * (W + pad), head - 26), '%s: from %s' % (nm, 'the side' if cam == 'side' else 'above'), fill=FG, font=font(15, True))
    for i, (tag, nm, c) in enumerate(PANEL):
        y = head + i * (th + 30 + pad)
        d.text((pad, y + 4), nm, fill=FG, font=font(18, True))
        for j, (id_, _, cam) in enumerate(cols):
            im.paste(tile(os.path.join(HERE, 'shot-%s-%s-%s.png' % (tag, id_, cam)), W), (pad + j * (W + pad), y + 30))
    im.save(os.path.join(HERE, 'sheet-for-user.png')); print('sheet-for-user.png', im.size)

def close():
    W, pad = 560, 10
    rows = [CLOSE[0:4], CLOSE[4:8], CLOSE[8:12]]
    titles = ['Basilica, c = -1', 'Douady rabbit, c = -0.123 + 0.745i (ray step 0.8, as the page opens)', 'The same rabbit views with the ray step at 0.4: more of the thin sheets are drawn']
    th = tile(os.path.join(HERE, CLOSE[0][0] + '.png'), W).height
    cutw = 300
    cuts = [[('brute-bas-x0.png', 'cut across the x-axis at x = 0, 2.4 wide'), ('brute-bas-xm03.png', 'cut across at x = -0.3: thin spikes, 2.4 wide'), ('brute-bas-bud-side.png', 'the bud at 60 degrees cut along the x-axis, 0.5 wide'), ('brute-bas-neck.png', 'cut across the touching point, 0.2 wide: nothing but the point'), ('brute-bas-p30.png', 'cut by the plane at 30 degrees (half way)'), ('brute-bas-p60.png', 'cut by the plane at 60 degrees: the flat set'), ('brute-bas-skin-b.png', 'skin half way between the planes, 0.12 wide')],
            [('brute-rab-flat.png', 'cut at z = 0: the flat rabbit'), ('brute-rab-p60.png', 'plane at 60 degrees: the flat rabbit, turned over'), ('brute-rab-p10.png', 'plane at 10 degrees: the ears are shreds'), ('brute-rab-p30.png', 'plane at 30 degrees (half way)'), ('brute-rab-x0.png', 'cut across the x-axis at x = 0'), ('brute-sie-x0.png', 'Siegel disc cut across: six thin sheets'), ('brute-den-p60.png', 'c = i, plane at 60 degrees: the flat tree')]]
    head = 84
    H = head + 3 * (th + 34 + pad) + 2 * (cutw + 60) + 30
    Wd = pad + 4 * (W + pad)
    im = Image.new('RGB', (Wd, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Wind, then square close up: the basilica and the rabbit (the lab itself, Rough estimate)', fill=FG, font=font(28, True))
    d.text((pad, 50), 'Below the lab pictures: cuts worked point by point with the page\'s own arithmetic (no shortcut of the 3D picture); cream = in the set. Julia sets only.', fill=DIM, font=font(15))
    y = head
    for r, row in enumerate(rows):
        d.text((pad, y + 2), titles[r], fill=FG, font=font(18, True))
        for j, (name, cap, c, it, cam, k) in enumerate(row):
            x = pad + j * (W + pad)
            im.paste(tile(os.path.join(HERE, name + '.png'), W), (x, y + 30))
            d.text((x + 6, y + 34), '%s (%d iterations)' % (cap, it), fill=FG, font=font(14))
        y += th + 34 + pad
    step = (Wd - 2 * pad) // 7
    for r, row in enumerate(cuts):
        d.text((pad, y + 2), ['Basilica, point by point', 'Rabbit, Siegel disc and c = i, point by point'][r], fill=FG, font=font(18, True))
        for j, (f, cap) in enumerate(row):
            x = pad + j * step
            a = Image.open(os.path.join(HERE, f)).convert('RGB').resize((cutw, cutw), Image.LANCZOS)
            im.paste(a, (x, y + 28))
            for k, line in enumerate(wrap(d, cap, font(13), cutw)):
                d.text((x, y + 30 + cutw + 15 * k), line, fill=DIM, font=font(13))
        y += cutw + 64
    im.save(os.path.join(HERE, 'close.png')); print('close.png', im.size)

if __name__ == '__main__':
    what = sys.argv[1:] or ['sheet', 'close']
    if 'sheet' in what:
        sheet()
    if 'close' in what:
        close()
