"""The two sheets of section "rabbit" (from the cached depth maps of doors.py).
    python out/r23/rabbit/sheets.py doors      -> sheet-doors.png   one row per rule, four shapes whose c is off the x-axis
    python out/r23/rabbit/sheets.py n          -> sheet-n.png       'along' for the first N steps, then one plane
    python out/r23/rabbit/sheets.py tries      -> sheet-tries.png   the attempts inside each approach, rabbit only
Every tile: rough solid, 280 x 210 x 180 blocks, 40 steps, the same eye (0.45, 0.5, 1.0) and the same size.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
M = D.M
BG, FG, DIM, GOLD = (12, 14, 20), (240, 240, 245), (150, 160, 175), (235, 220, 170)

# what a person sees in each row (written after looking at the tiles; the numbers are in NOTES.md)
SEEN = {
    'oneplane':   'Clean, smooth, separate bodies that meet at single points. Nothing grows above or below them.',
    'twoplane':   'The flat bodies are there, with a cloud of loose shards standing above and below them.',
    'along':      'One swollen lump with ribs and fins. The separate bodies are gone.',
    'alongonce':  'Clean separate bodies as in the first row, plus a few smooth bodies above and below, some floating free.',
    'pulled':     'Nearly the same as the first row.',
    'pillow':     'The bodies are there, rough and spiky all over, with crumbs round them. Still there for the tilted c.',
    'pillowJ':    'Rounded bodies with knobs and spikes on them and crumbs between. Still there for the tilted c.',
    'mandelbulb': 'The flat bodies with streaks and loose scraps; nothing round grows on them.',
    'b_pcd':      'The flat bodies with loose scraps above and below.',
    'conep':      'One big lump; the flat picture is buried in it.',
    'conem':      'Small rough bodies with loose bits beside them.',
}


def tile(key, sname, eye='a'):
    dep, px = D.dep(key, sname, eye, quiet=True)
    return Image.fromarray(M.shade_solid(dep, px)), bool(np.isfinite(dep).any())


def doors():
    sets = ['rabbit', 'siegel', 'dendrite', 'tilt']
    heads = ['rabbit', 'Siegel disc', 'dendrite (c = i)', 'c near the rabbit\'s, tilted 10 degrees']
    import json
    num = json.load(open(os.path.join(HERE, 'numbers.json')))
    keys = D.ORDER; w, h, pad, top, rowh = D.DW, D.DH, 10, 64, D.DH + 68
    W = pad + len(sets) * (w + pad); H = top + len(keys) * rowh + 8
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Shapes whose c is off the x-axis: one row per rule, same eye, same size (a tile is empty where nothing lasts 80 steps)', fill=FG, font=M.font(19))
    for j, hd in enumerate(heads):
        d.text((pad + j * (w + pad), 40), hd, fill=DIM, font=M.font(14))
    for i, k in enumerate(keys):
        y = top + i * rowh
        d.text((pad, y), D.RULES[k][1], fill=GOLD, font=M.font(18)); d.text((pad, y + 24), SEEN.get(k, ''), fill=DIM, font=M.font(14))
        for j, s in enumerate(sets):
            t, any_ = tile(k, s); x = pad + j * (w + pad)
            if num['%s|%s' % (k, s)]['vol80'] < 1e-4:                 # under 13 blocks of 3.3 million last 80 steps
                t = Image.new('RGB', (w, h), (14, 17, 26)); any_ = False
            im.paste(t, (x, y + 46))
            if not any_:
                d.text((x + 80, y + 46 + h // 2 - 8), 'nothing survives', fill=DIM, font=M.font(15))
    p = os.path.join(HERE, 'sheet-doors.png'); im.save(p); print('wrote', p, im.size)


def nsheet():
    NS = [0, 1, 2, 3, 5, 99]
    heads = ['no "along" step (one plane)', 'first step "along"', 'first 2 steps', 'first 3 steps', 'first 5 steps', 'every step "along"']
    sets = [('basilica', 'c = -1'), ('rabbit', 'rabbit')]; w, h, pad, top = D.DW, D.DH, 10, 70
    W = pad + len(NS) * (w + pad); H = top + len(sets) * (h + 30) + 8
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The first N steps of every orbit by "along", every later step by "one plane"', fill=FG, font=M.font(21))
    for j, hd in enumerate(heads):
        d.text((pad + j * (w + pad), 42), hd, fill=GOLD, font=M.font(16))
    for i, (s, nm) in enumerate(sets):
        y = top + i * (h + 30); d.text((pad, y), nm, fill=DIM, font=M.font(15))
        for j, N in enumerate(NS):
            t, _ = tile('along%d' % N, s); im.paste(t, (pad + j * (w + pad), y + 22))
    p = os.path.join(HERE, 'sheet-n.png'); im.save(p); print('wrote', p, im.size)


def tries():
    rows = [('pillowJ', 'Square pillow, second layout (as in the big sheet)'), ('pilJA', 'the same, made shape-true beside the flat picture'),
            ('pilT45', 'the same, with a lopsided (not mirror-symmetric) layout'), ('along', 'Along (swings about the x-axis)'), ('alongC', 'Along, swinging about the unit circle instead')]
    w, h, pad, top = D.DW, D.DH, 10, 44; cols = 3
    W = pad + cols * (w + pad); H = top + 2 * (h + 30) + 8
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Rabbit: the attempts inside two approaches', fill=FG, font=M.font(21))
    for i, (k, nm) in enumerate(rows):
        r, c = divmod(i, cols); x = pad + c * (w + pad); y = top + r * (h + 30)
        d.text((x, y), nm, fill=GOLD, font=M.font(13)); t, _ = tile(k, 'rabbit'); im.paste(t, (x, y + 22))
    p = os.path.join(HERE, 'sheet-tries.png'); im.save(p); print('wrote', p, im.size)


if __name__ == '__main__':
    {'doors': doors, 'n': nsheet, 'tries': tries}[sys.argv[1]]()
