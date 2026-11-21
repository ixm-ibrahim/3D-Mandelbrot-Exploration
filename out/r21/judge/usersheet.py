"""The one sheet for the user: out/r21/judge/sheet-for-user.png. Plain labels, four rows, three rough solids per row.

    python out/r21/judge/usersheet.py solid <rule> <basilica|rabbit|mandel>     one solid, kept in user/<rule>-<set>.npy
    python out/r21/judge/usersheet.py compose                                   the sheet

Solids: M.solid, 520 x 390 x 330 blocks, eye at (0.45, 0.5, 1.0); Julia sets 60 steps, Mandelbrot solid 40 steps."""
import os, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
D = os.path.join(J.HERE, 'user'); os.makedirs(D, exist_ok=True)
W, H, ND = 520, 390, 330
SETS = {'basilica': ((-1.0, 0.0, 0.0), 60), 'rabbit': (M.RABBIT, 60), 'mandel': (None, 40)}
ROWS = [
    ('along', 'Best so far: "Turning plane, along" (it remembers nothing)',
     'c = -1: every body carries round buds in eight directions, with smaller buds on them. The rabbit is one swollen, layered lump with no '
     'separate bodies. The Mandelbrot solid is a lumpy rock.'),
    ('frame.orb_inf_px', 'Your idea, taken literally: each point is squared in the plane made by the last two points of its own orbit',
     'c = -1: the buds are smeared round the x-axis: the side bodies are stacks of rings and the middle body is terraced. The rabbit is a '
     'ribbed shell with a frayed edge, and a fifth of it leaks away when more steps are taken. The Mandelbrot solid is a ribbed shell: '
     'not simply spun round, but ribs instead of round buds.'),
    ('sheet.evc005e70k16', "The closest new rule: the plane starts as the flat page and is pulled toward the orbit's points as they come (far-out points pull harder, and c pulls too)",
     'c = -1: round buds in four directions (along the flat page and along the plane square to it), no rings; very close up, thin loose '
     'flakes hover over the skin between them. The rabbit has clean separate '
     'bodies, but it is almost exactly the rabbit that one fixed plane already gave: its smaller bodies sit round the flat page only. '
     'The second row of buds fades as soon as c moves a little off the x-axis, and three numbers in the recipe are set by hand. '
     'The Mandelbrot solid is the flat set with a second copy standing square to it, smooth in between.'),
    ('alongmem.c_wake1', 'A hand-over: the first step as in "Turning plane, along", every later step about the flat page',
     'c = -1: the middle body keeps its eight round buds; the other bodies have buds round the flat page only. The rabbit has smooth separate '
     'bodies, also off the flat page, but two of them float free of the rest. The Mandelbrot solid is a smooth cushion with nothing '
     'on it off the flat page (the same as one fixed plane gives).'),
]
FOOT = ['In short: nothing here beats the best rule so far. Following the orbit closely smears the buds into ribs and rings.',
        'Following it loosely, or only for one step, gives back the one-fixed-plane picture with little or nothing new off the flat page.']
HEADS = {'basilica': 'c = -1 (the "basilica")', 'rabbit': 'the "rabbit"', 'mandel': 'the Mandelbrot solid'}


def path(rule, s):
    return os.path.join(D, '%s-%s.npy' % (rule, s))


def solid(rule, s):
    c, steps = SETS[s]; dep, px = M.solid(J.get(rule), c, W, H, ND, steps); np.save(path(rule, s), dep); print(rule, s, 'done', px)


def compose():
    pad = 14; Wt = pad + 3 * (W + pad); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    wrapw = 178
    blocks = []
    for rule, head, cap in ROWS:
        blocks.append((rule, textwrap.wrap(head, 140), textwrap.wrap(cap, wrapw)))
    Ht = 120 + sum(26 * len(h) + 24 + H + 22 * len(c) + 34 for _, h, c in blocks) + 400
    im = Image.new('RGB', (Wt, Ht), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Letting the plane follow the orbit: what comes out', fill=(240, 240, 245), font=f_t)
    d.text((pad, 58), 'Each row is one way of squaring in 3D. Left and middle: two test shapes (all start points that never fly away). Right: the Mandelbrot solid.',
           fill=(170, 178, 192), font=f_c)
    d.text((pad, 82), 'Rough block pictures, not fine renders. On the flat page all four rows give exactly the flat pictures; they differ in what happens off it.',
           fill=(170, 178, 192), font=f_c)
    y = 120
    for rule, hl, cl in blocks:
        for ln in hl:
            d.text((pad, y), ln, fill=(240, 222, 160), font=f_h); y += 26
        y += 2
        for j, s in enumerate(('basilica', 'rabbit', 'mandel')):
            x = pad + j * (W + pad); d.text((x, y), HEADS[s], fill=(150, 160, 175), font=f_s)
            p = path(rule, s)
            if os.path.exists(p):
                dep = np.load(p); px = 2 * (1.7 if s == 'mandel' else 1.75) / (W - 1)
                im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 22))
        y += 22 + H + 6
        for ln in cl:
            d.text((pad, y), ln, fill=(215, 218, 226), font=f_c); y += 22
        y += 28
    for ln in FOOT:
        d.text((pad, y), ln, fill=(240, 240, 245), font=f_h); y += 28
    im = im.crop((0, 0, Wt, y + 40)); im.save(os.path.join(J.HERE, 'sheet-for-user.png')); print('wrote sheet-for-user.png', im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'solid':
        solid(sys.argv[2], sys.argv[3])
    else:
        compose()
