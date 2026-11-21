"""Sheets of rough solids from the cached tiles (job.py makes the tiles).

    python out/r24/twice/sheets.py look <set> [key ...]     rows = rules, columns = eye a / eye top at 30 and 120 steps -> look-<set>-<i>.png
    python out/r24/twice/sheets.py all                      the four big grids  solids-<eye>-<steps>.png  (rows = rules, columns = the seven c)
    python out/r24/twice/sheets.py sheet                    sheet.png (what the notes claim)
"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tw
M = tw.M

KEYS = ['oneplane', 'along', 'm4:-0.10', 'm4:-0.20', 'm4:-0.30', 'm6:-0.05', 'm6:-0.10', 'm6:-0.20', 'm8:-0.05']
LAB = {'oneplane': 'one plane', 'along': 'along', 'alongonce': 'along once, then one plane'}
EYE = {'a': 'front eye (0.45, 0.5, 1)', 'top': 'second eye (0.2, 1, 0.35)'}


def label(key):
    if key in LAB:
        return LAB[key]
    p = key.split(':')
    if p[0][0] == 'm':
        s = 'copy laid %d times round, dial %s' % (int(p[0][1:]) - 2, p[1])
    else:
        s = 'welded: copy laid %s times round at latitude %s' % (p[0][1:], p[1])
    return s + (' (' + ', '.join(p[2:]) + ')' if len(p) > 2 else '')


def grid(rows, cols, cell, path, title, rowlab, collab, w=420, h=315):
    """cell(row, col) -> path of a tile."""
    pad = 8; W = pad + len(cols) * (w + pad); H = 44 + len(rows) * (h + 28)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), title, fill=(240, 240, 245), font=M.font(20))
    for i, r in enumerate(rows):
        y = 44 + i * (h + 28); d.text((pad, y), rowlab(r), fill=(235, 220, 170), font=M.font(16))
        for j, c in enumerate(cols):
            x = pad + j * (w + pad); p = cell(r, c)
            if p and os.path.exists(p):
                im.paste(Image.open(p), (x, y + 22))
            d.text((x + 5, y + 25), collab(c), fill=(150, 160, 175), font=M.font(12))
    im.save(path); print('wrote', path, im.size)


def look(sn, keys=None, tag=None):
    keys = keys or KEYS; cols = [('a', 30), ('top', 30), ('a', 120), ('top', 120)]
    for i0 in range(0, len(keys), 5):
        grid(keys[i0:i0 + 5], cols, lambda r, c: tw.tile(r, sn, c[0], c[1]), os.path.join(HERE, 'look-%s-%s%d.png' % (sn, tag or '', i0 // 5)),
             '%s: rough solids (blocks of side %.4f)' % (tw.SETNAME[sn], tw.H), label, lambda c: '%s, %d steps' % (EYE[c[0]], c[1]))


def big():
    for eye in ('a', 'top'):
        for steps in (30, 120):
            grid(KEYS, tw.ORDER, lambda r, c: tw.tile(r, c, eye, steps), os.path.join(HERE, 'solids-%s-%d.png' % (eye, steps)),
                 'Rough solids, %s, %d steps (blocks of side %.4f)' % (EYE[eye], steps, tw.H), label, lambda c: tw.SETNAME[c])


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'look':
        look(sys.argv[2], sys.argv[3:] or None, tag='x' if len(sys.argv) > 3 else None)
    elif a == 'all':
        big()
