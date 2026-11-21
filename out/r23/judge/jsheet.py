"""Round 23, judge: the pictures for the user, from my own depth maps (jdep.py).

    python out/r23/judge/jsheet.py look      contact sheets without captions, for me to look at first (look-*.png)
    python out/r23/judge/jsheet.py user      the pictures for the user (1-..., 2-..., 3-...), captions written after looking
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl as L, jdep as Dp
M = L.M
BG = (12, 14, 20); GOLD = (235, 220, 170); GREY = (170, 180, 195); DIM = (150, 160, 175); WHITE = (240, 240, 245)
W0, H0 = Dp.DW, Dp.DH


def wrap(d, text, font, width):
    words = text.split(); lines = []; cur = ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur); return lines


def tile(name, sname, eye):
    got = Dp.dep(name, sname, eye, compute=False)
    if got is None:
        t = Image.new('RGB', (W0, H0), (14, 17, 26)); ImageDraw.Draw(t).text((120, 115), 'not made', fill=DIM, font=M.font(13)); return t
    t = Image.fromarray(M.shade_solid(*got))
    if not np.isfinite(got[0]).any():
        ImageDraw.Draw(t).text((110, 115), 'nothing survives', fill=DIM, font=M.font(14))
    return t


def sheet(path, title, rows, cols, intro=None, foot=None):
    """rows: list of (heading, caption, [ (rule, set, eye) per column ]); cols: column heads."""
    pad = 10; Wd = pad + len(cols) * (W0 + pad); f_t, f_h, f_c, f_s = M.font(22), M.font(19), M.font(15), M.font(13)
    probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    intro_l = wrap(probe, intro, f_c, Wd - 2 * pad) if intro else []
    foot_l = [wrap(probe, s, f_c, Wd - 2 * pad - 20) for s in (foot or [])]
    caps = [wrap(probe, r[1], f_c, Wd - 2 * pad) if r[1] else [] for r in rows]
    Ht = 14 + 34 + 21 * len(intro_l) + 10 + sum(28 + 21 * len(c) + 4 + H0 + 14 for c in caps) + (sum(21 * len(l) + 6 for l in foot_l) + 16 if foot_l else 0)
    im = Image.new('RGB', (Wd, Ht), BG); d = ImageDraw.Draw(im); y = 14
    d.text((pad, y), title, fill=WHITE, font=f_t); y += 34
    for s in intro_l:
        d.text((pad, y), s, fill=GREY, font=f_c); y += 21
    y += 10
    for (head, cap, cells), cl in zip(rows, caps):
        d.text((pad, y), head, fill=GOLD, font=f_h); y += 28
        for s in cl:
            d.text((pad, y), s, fill=GREY, font=f_c); y += 21
        y += 4
        for j, cell in enumerate(cells):
            x = pad + j * (W0 + pad)
            if cell is None:
                continue
            lab = cell[3] if len(cell) > 3 else cols[j]
            im.paste(tile(*cell[:3]), (x, y)); d.rectangle([x, y, x + int(d.textlength(lab, font=f_s)) + 14, y + 24], fill=(14, 17, 26))
            d.text((x + 7, y + 4), lab, fill=(190, 198, 210), font=f_s)
        y += H0 + 14
    if foot_l:
        d.line([pad, y, Wd - pad, y], fill=(60, 66, 80), width=1); y += 10
        for l in foot_l:
            d.ellipse([pad + 2, y + 8, pad + 8, y + 14], fill=GREY)
            for s in l:
                d.text((pad + 18, y), s, fill=(225, 228, 235), font=f_c); y += 21
            y += 6
    im.save(path); print(path, im.size); return path


def four(rule):
    return [(rule, 'basilica', 'a'), (rule, 'basilica', 'top'), (rule, 'rabbit', 'a'), (rule, 'rabbit', 'top')]


COLS4 = ['c = -1, from the front', 'c = -1, from above', 'rabbit, from the front', 'rabbit, from above']

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'look'
    if mode == 'look':
        sheet(os.path.join(HERE, 'look-1.png'), 'look 1', [(nm, '', four(nm)) for nm in ('twoplane', 'along', 'alongonce', 'cones1', 'cones')], COLS4)
        if Dp.dep('o:sym2', 'basilica', 'a', compute=False) is not None:
            sheet(os.path.join(HERE, 'look-2.png'), 'look 2', [(nm, '', [(nm, 'basilica', 'a'), (nm, 'rabbit', 'a')]) for nm in ('o:sym2', 'o:eiffie', 'o:mb2', 'o:bristor')] , ['c = -1', 'rabbit'])
        if Dp.dep('cones2', 'rabbit', 'a', compute=False) is not None:
            sheet(os.path.join(HERE, 'look-3.png'), 'look 3', [('along N = 1, 2, 3, all', '', [('alongonce', 'rabbit', 'a'), ('r:along2', 'rabbit', 'a'), ('r:along3', 'rabbit', 'a'), ('along', 'rabbit', 'a')]),
                                                              ('cones N = 1, 2, 3, all', '', [('cones1', 'rabbit', 'a'), ('cones2', 'rabbit', 'a'), ('cones3', 'rabbit', 'a'), ('cones', 'rabbit', 'a')])], ['1', '2', '3', 'all'])
    else:
        import jcaptions as C
        C.make(sheet, four, COLS4, HERE)
