"""Round 16, entry: the contact sheet out/r16/entry/sheet-turning.png, with plain-word labels.
Pictures named brute-* are plain point-by-point cuts (cream = in the solid); all others are the lab's own renderer."""
import os, json
from PIL import Image, ImageDraw, ImageFont

D = 'out/r16/entry/'
try:
    FONT = ImageFont.truetype('arial.ttf', 14); BOLD = ImageFont.truetype('arialbd.ttf', 18)
except OSError:
    FONT = BOLD = ImageFont.load_default()
TW, TH, GAP, CAP = 262, 250, 8, 72
COLS = 7
A, B, F = 'Turning plane, away', 'Turning plane, along', 'Sphere inversions, two planes (the look the user liked; it tears away from the x-axis)'
RO, EX = 'estimate: Rough', 'estimate: Exact (the page as it opens)'
CAPS = json.load(open(D + 'captions.json', encoding='utf-8')) if os.path.exists(D + 'captions.json') else {}


def views(t, mode):
    return [('%s-bas-front' % t, 'from the front\n' + mode), ('%s-bas-above' % t, 'from above'), ('%s-bas-alongx' % t, 'along the x-axis'), ('%s-bas-below' % t, 'from below')]


ROWS = [
    ('STAGE 1, THE BASILICA (c = -1, power 2).   ' + A, views('ta0', RO) + [
        ('ta-bas-front', 'the same, ' + EX + ':\nthe lab draws fog. NOT the true shape'), ('brute-ta-bas-x0-14', 'cut across the middle (x = 0), point by\npoint, 14 steps: whiskers beside the diagonals'), ('brute-ta-bas-x0-40', 'the same cut, 40 steps:\nthe whiskers thin to specks')]),
    (B, views('tl', EX) + [
        ('tl0-bas-front', 'the same, ' + RO + ':\nthe same shape'), ('brute-tl-bas-x0-14', 'cut across the middle (x = 0),\npoint by point, 14 steps: 8 buds'), ('brute-tl-bas-x0-40', 'the same cut, 40 steps')]),
    (F, views('f2', EX) + [
        ('f20-bas-front', 'the same, ' + RO), ('brute-f2-bas-x0-14', 'cut across the middle (x = 0),\npoint by point, 14 steps: 4 buds'), ('brute-f2-bas-x0-40', 'the same cut, 40 steps')]),
    ('CLOSE-UP 1: the bud on top of the middle body, camera 0.9, 0.3 and 0.09 away (14, 20, 26 steps).   ' + A + ' (Rough)', [
        ('ta0-close-bud-1', 'camera 0.9 away'), ('ta0-close-bud-2', 'camera 0.3 away:\ncombed streaks and hair, some round bumps'), ('ta0-close-bud-3', 'camera 0.09 away, the next bud up'),
        ('ta-close-bud-2', 'camera 0.3 away, ' + EX + ':\nfog'), ('brute-ta-bud-x0', 'point by point: cut x = 0 through\nthe bud, 0.5 wide'), ('brute-ta-bud-x0-zoom', 'its side, 0.12 wide, 20 steps:\nsmaller buds'), ('brute-ta-bud-z06', 'level cut through the bud (z = 0.6),\n0.5 wide: a fuzzy rim')]),
    (B + ' (Exact)', [
        ('tl-close-bud-1', 'camera 0.9 away'), ('tl-close-bud-2', 'camera 0.3 away: ribs, and spiky\nbuds in rings all round'), ('tl-close-bud-3', 'camera 0.09 away, the next bud up'),
        ('tl0-close-bud-2', 'camera 0.3 away, ' + RO + ':\nthe same'), ('brute-tl-bud-x0', 'point by point: cut x = 0 through\nthe bud, 0.5 wide'), ('brute-tl-bud-x0-zoom', 'its side, 0.12 wide, 20 steps:\nsmaller buds'), ('brute-tl-bud-z06', 'level cut through the bud (z = 0.6):\nround, small spikes all round')]),
    (F + ' (Exact)', [
        ('f2-close-bud-1', 'camera 0.9 away'), ('f2-close-bud-2', 'camera 0.3 away: smooth, creased,\nbuds in rows along four lines'), ('f2-close-bud-3', 'camera 0.09 away, the next bud up'),
        (None, ''), ('brute-f2-bud-x0', 'point by point: cut x = 0 through\nthe bud, 0.5 wide'), ('brute-f2-bud-x0-zoom', 'its side, 0.12 wide, 20 steps:\nsmaller buds'), ('brute-f2-bud-z06', 'level cut through the bud (z = 0.6):\nfour small buds')]),
    ('CLOSE-UP 2: where the middle body and the left body touch, (-0.618, 0, 0), seen from above, camera 1, 0.25 and 0.06 away (14, 20, 26 steps).   ' + A + ' (Rough)', [
        ('ta0-close-meet-1', 'camera 1 away'), ('ta0-close-meet-2', 'camera 0.25 away'), ('ta0-close-meet-3', 'camera 0.06 away'), ('ta0-meet-60', 'camera 0.25 away, 60 steps:\nthe neck is gone, a single point'),
        ('brute-ta-meet-x-40', 'point by point: cut across at the\ntouching point, 0.1 wide, 40 steps:\nonly the point itself'), ('brute-ta-meet-diag-30', 'cut along the plane y = z, 0.3 wide,\n30 steps: two bodies, one point'), ('brute-ta-bas-diag-14', 'whole cut along the plane y = z:\nno buds in this plane')]),
    (B + ' (Rough)', [
        ('tl0-close-meet-1', 'camera 1 away'), ('tl0-close-meet-2', 'camera 0.25 away'), ('tl0-close-meet-3', 'camera 0.06 away'), ('tl0-meet-60', 'camera 0.25 away, 60 steps:\na single point'),
        ('brute-tl-meet-x-40', 'point by point: cut across at the\ntouching point, 0.1 wide, 40 steps:\nonly the point itself'), ('brute-tl-meet-diag-30', 'cut along the plane y = z, 0.3 wide:\nthe flat basilica, one point'), ('tl-close-meet-2', 'camera 0.25 away, ' + EX + ':\na flat sheet that is NOT there\n(the renderer, not the solid)')]),
    (F, [
        ('f2-close-meet-1', 'camera 1 away (Exact)'), ('f2-close-meet-2', 'camera 0.25 away (Exact)'), ('f2-close-meet-3', 'camera 0.06 away (Exact)'), ('f20-meet-60', 'camera 0.25 away, 60 steps (Rough)'),
        ('brute-f2-meet-x-40', 'point by point: cut across at the\ntouching point, 0.1 wide, 40 steps:\nonly the point itself'), ('brute-f2-meet-diag-30', 'cut along the plane y = z, 0.3 wide'), ('brute-f2-bas-diag-14', 'whole cut along the plane y = z')]),
    ('HONESTLY, THE OTHER SETS (stage 2 is not judged here).   ' + A + ': the rabbit c = (-0.12, 0.74, 0), and c = (-1, 0.15, 0.1), off the flat plane', [
        ('ta0-rabbit', 'the rabbit (Rough)'), ('ta0-rabbit-above', 'the rabbit from above (Rough)'), ('ta-rabbit', 'the rabbit (Exact)'), ('brute-ta-rabbit-x0-14', 'point by point: the rabbit cut\nacross (x = 0), 3 wide'),
        ('ta-cut-rabbit', 'the page\'s cut at z = 0: the flat rabbit'), ('ta0-off', 'c = (-1, 0.15, 0.1) (Rough)'), ('ta-cut-off', 'c = (-1, 0.15, 0.1), cut at z = 0')]),
    (B + ': the same', [
        ('tl0-rabbit', 'the rabbit (Rough)'), ('tl0-rabbit-above', 'the rabbit from above (Rough)'), ('tl-rabbit', 'the rabbit (Exact)'), ('brute-tl-rabbit-x0-14', 'point by point: the rabbit cut\nacross (x = 0), 3 wide'),
        ('tl-cut-rabbit', 'the page\'s cut at z = 0: the flat rabbit'), ('tl0-off', 'c = (-1, 0.15, 0.1) (Rough)'), ('tl-cut-off', 'c = (-1, 0.15, 0.1), cut at z = 0')]),
    ('THE MANDELBROT SOLID, power 2.   ' + A, [
        ('ta0-m-front', 'opening view (Rough)'), ('ta0-m-above', 'from above (Rough)'), ('ta0-m-alongx', 'along the x-axis (Rough)'), ('ta-m-front', 'opening view (Exact)'),
        ('ta-cut-m', 'the page\'s cut at z = 0:\nthe flat Mandelbrot set'), ('brute-ta-m-y0-14', 'point by point: cut at y = 0:\nthe flat Mandelbrot set again'), ('brute-ta-m-x02-14', 'point by point: cut across at\nx = -0.2, 2.4 wide')]),
    (B, [
        ('tl0-m-front', 'opening view (Rough)'), ('tl0-m-above', 'from above (Rough)'), ('tl0-m-alongx', 'along the x-axis (Rough)'), ('tl-m-front', 'opening view (Exact)'),
        ('tl-cut-m', 'the page\'s cut at z = 0:\nthe flat Mandelbrot set'), ('brute-tl-m-y0-14', 'point by point: cut at y = 0:\nthe flat Mandelbrot set again'), ('brute-tl-m-x02-14', 'point by point: cut across at\nx = -0.2, 2.4 wide')]),
    ('WHOLE POWERS (all Rough): does the count round the x-axis follow the power?   ' + A + ': the flat set lies in n planes, so 2n directions', [
        ('ta0-n3-j03-front', 'power 3, c = (0.3, 0, 0)'), ('ta0-n3-j03-alongx', 'the same along the x-axis'), ('brute-ta-n3-j03-x0', 'the same, cut across (x = 0),\npoint by point'), ('ta0-n4-bas-front', 'power 4, c = -1'),
        ('ta0-n4-bas-alongx', 'the same along the x-axis'), ('brute-ta-n4-bas-x0', 'the same, cut across (x = 0),\npoint by point'), ('ta0-n3-m', 'power 3, Mandelbrot solid')]),
    (B + ': the flat set lies in 2n planes, so 4n directions', [
        ('tl0-n3-j03-front', 'power 3, c = (0.3, 0, 0)'), ('tl0-n3-j03-alongx', 'the same along the x-axis'), ('brute-tl-n3-j03-x0', 'the same, cut across (x = 0),\npoint by point'), ('tl0-n4-bas-front', 'power 4, c = -1'),
        ('tl0-n4-bas-alongx', 'the same along the x-axis'), ('brute-tl-n4-bas-x0', 'the same, cut across (x = 0),\npoint by point'), ('tl0-n3-m', 'power 3, Mandelbrot solid')]),
    ('Power 3 with c = (0, 1, 0), the middle of its period-2 body (power 3 has none on the x-axis), and power 4, for both rules (Rough)', [
        ('ta0-n3-ji-front', 'away, power 3, c = (0, 1, 0)'), ('ta0-n3-ji-alongx', 'the same along the x-axis'), ('ta0-n4-m', 'away, power 4, Mandelbrot solid'), ('ta0-n3-m-alongx', 'away, power 3, Mandelbrot solid\nalong the x-axis'),
        ('tl0-n3-ji-front', 'along, power 3, c = (0, 1, 0)'), ('tl0-n3-ji-alongx', 'the same along the x-axis'), ('tl0-n4-m', 'along, power 4, Mandelbrot solid')]),
]
NOTE = CAPS.get('note', '')

W = COLS * (TW + GAP) + GAP


def wrap(d, text, font, width):
    lines, cur = [], ''
    for w in text.split(' '):
        if d.textlength((cur + ' ' + w).strip(), font=font) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    return lines


tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
note_lines = wrap(tmp, NOTE, FONT, W - 24) if NOTE else []
titles = [wrap(tmp, t, BOLD, W - 24) for t, _ in ROWS]
H = 12 + 18 * len(note_lines) + sum(8 + 22 * len(t) + TH + CAP + GAP for t in titles) + 12
sheet = Image.new('RGB', (W, H), (16, 18, 24))
d = ImageDraw.Draw(sheet)
for i, l in enumerate(note_lines):
    d.text((12, 8 + 18 * i), l, fill=(255, 214, 140), font=FONT)
y = 12 + 18 * len(note_lines)
missing = []
for (title, tiles), tl in zip(ROWS, titles):
    for i, l in enumerate(tl):
        d.text((12, y + 6 + 22 * i), l, fill=(240, 240, 240), font=BOLD)
    y += 8 + 22 * len(tl)
    for k, (name, cap) in enumerate(tiles):
        if not name:
            continue
        cap = CAPS.get(name, cap)
        p = D + name + '.png'
        x = GAP + k * (TW + GAP)
        if not os.path.exists(p):
            missing.append(name); continue
        im = Image.open(p).convert('RGB')
        if im.size[0] > 800:
            im = im.crop((0, 0, 735, im.size[1]))     # leave out the page's zoom slider at the right
        im.thumbnail((TW, TH), Image.LANCZOS)
        sheet.paste(im, (x + (TW - im.size[0]) // 2, y))
        for j, l in enumerate(wrap(d, cap.replace('\n', ' '), FONT, TW - 6)[:4]):
            d.text((x + 2, y + TH + 3 + 16 * j), l, fill=(205, 210, 220), font=FONT)
    y += TH + CAP + GAP
sheet.save(D + 'sheet-turning.png')
print('wrote', D + 'sheet-turning.png', sheet.size, 'missing:', missing)
