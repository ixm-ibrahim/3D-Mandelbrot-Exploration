"""Round 20 check: the sheet for the user. m_w3 beside along, twoplane and oneplane on the eleven sets of panel2.
Pictures from solids.py (tiles/), verdict words from panel2's own lines (read only), by-eye words for m_w3 written by hand.
python out/r20/check/sheet.py   -> out/r20/check/sheet.png"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
P2 = os.path.join(ROOT, 'out', 'r19', 'panel2'); sys.path.insert(0, P2); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import panel2 as Q
import truth as T
sys.path.insert(0, HERE)
import solids as So

RULES = [('oneplane', 'One plane (sphere inversions)'), ('twoplane', 'Two planes, nearest plane (the look you liked)'), ('along', 'Turning plane, along (best so far)'), ('m_w3', 'NEW: wind three times, then one plane')]
WORD = dict(cut='cut at z = 0 is not the flat set', piece='not in one piece', stays='drains away with more steps', bodies='bodies wrong (lump, plates or shards)', d3='not truly 3D', clean='skin not clean close up', mirror='mirror broken')
EYE = {  # what I saw for m_w3 (pictures in out/r20/check/), in a person's words
    'basilica': 'Whole set: the liked look, buds in six rows, ribbed like a walnut. One bud: a ribbed egg, round in section, with its own small buds only in its plane (along: small round buds all over the bud). Skin close up: teeth, whiskers, dust and flat flakes everywhere except exactly in its six planes and half way between them.',
    'sanmarco': 'Whole set: as the basilica, studded with buds. Half way between the planes the three bodies run together. Skin close up: whiskers and dust (110 of 120 tiles).',
    'airplane': 'Whole set: a ball with six spines of beads. Skin: clean when looked at wide, a toothed edge at the finest width (29 of 40 fine tiles).',
    'cauliflower': 'Whole set: a pumpkin with twelve grooves. Across the axis away from the middle: a ragged, saw-toothed outline with fins in the grooves.',
    'rabbit': 'Whole set: a cloud of flakes and shards. Only the flat rabbit and its two turned copies are whole, and they are plates: the ears are half as thick as they are wide. About half the matter is not joined to the biggest piece, at every voxel size tried.',
    'dendrite': 'Three flat trees crossing on the x-axis, nothing at all between them. Paper thin: in voxels it falls to dust sooner than the one-plane tree.',
    'siegel': 'A six-armed star of thin sheets with wisps, no body. It drains away: 71 % left from 40 to 80 steps, 41 % at 320.',
    'bas_yz': 'Bodies crumpled like a walnut; outline hairy in EVERY cut, the flat plane included; pinholes inside. The inside has no resting cycle any more and leaks: 16 % gone after 3000 steps (along and one plane: none).',
    'bas_zy': 'As the other nudged basilica: crumpled, hairy outline, pinholes; leaks (7 % gone after 3000 steps).',
    'sm_yz': 'Whole set: San Marco, hardly changed. Close up the whole skin is under a film of dust (120 of 120 tiles).',
    'rab_up': 'Flakes and shards, as the rabbit; the biggest piece holds 39 % even with a one-voxel gap allowed.',
}
S = 232
LW = 270
CW = 3 * S + 14
TH = 150
W = LW + len(RULES) * CW + 10
H0 = 176
H = H0 + len(So.SETS) * (S + TH) + 20
im = Image.new('RGB', (W, H), (12, 13, 18)); dr = ImageDraw.Draw(im)
f = T.font(17); fs = T.font(16); fb = T.font(23); ft = T.font(32)


def wrap(text, font, width):
    out = []; line = ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if dr.textlength(t, font=font) <= width:
            line = t
        else:
            out.append(line); line = w
    if line:
        out.append(line)
    return out


dr.text((14, 10), 'The new rule "wind, then square" beside the three known rules, on the eleven Julia sets of the panel', fill=(240, 240, 240), font=ft)
dr.text((14, 54), 'Each cell, left to right: the solid from the front; the solid seen straight along the x-axis; a cut across the x-axis worked point by point (cream = inside). Solids are rough voxel pictures (257 a side, 40 steps; dendrite 10).', fill=(200, 200, 200), font=f)
dr.text((14, 78), 'Under each cell: the lines of panel2 it fails (red), or "passes every line" (green). For the new rule a second line says what I saw. "Outside" = the orbit of 0 leaves, dust is expected, not judged.', fill=(200, 200, 200), font=f)
npass = {}
for j, (rule, name) in enumerate(RULES):
    x0 = LW + j * CW
    full = Q.P.load(rule); ex = Q.jload(os.path.join(P2, 'results', 'extra-' + rule + '.json'), {})
    npass[rule] = 0
    for i, (tag, nm, c, L, steps, xc, half) in enumerate(So.SETS):
        y0 = H0 + i * (S + TH)
        for k, kind in enumerate(('front', 'axis', 'cross')):
            p = os.path.join(HERE, 'tiles', rule, '%s_%s.png' % (tag, kind))
            if os.path.exists(p):
                im.paste(Image.open(p).convert('RGB').resize((S, S), Image.LANCZOS), (x0 + k * S, y0))
        v = Q.verdicts2(rule, tag, full, ex); cell = Q.cell(v, Q.ORDER2) if v else '-'
        if cell == 'outside':
            txt = 'OUTSIDE: the orbit of 0 leaves, not judged'; col = (170, 170, 170)
        elif cell == 'pass':
            txt = 'passes every line'; col = (140, 225, 140); npass[rule] += 1
        else:
            ff = [k for k in Q.ORDER2 if v[k][0] is False]; txt = 'FAILS: ' + '; '.join(WORD[k] for k in ff); col = (240, 130, 115)
        yy = y0 + S + 3
        for ln in wrap(txt, f, CW - 20)[:2]:
            dr.text((x0 + 2, yy), ln, fill=col, font=f); yy += 20
        if rule == 'm_w3':
            for ln in wrap('Seen: ' + EYE[tag], fs, CW - 20)[:5]:
                dr.text((x0 + 2, yy), ln, fill=(225, 215, 170), font=fs); yy += 19
        if j == 0:
            for q, ln in enumerate(wrap(nm, fb, LW - 24)):
                dr.text((14, y0 + 60 + q * 28), ln, fill=(240, 240, 240), font=fb)
            grp = 'c on the x-axis' if i < 4 else ('c in the flat plane' if i < 7 else 'c nudged off both')
            dr.text((14, y0 + 60 + 28 * len(wrap(nm, fb, LW - 24)) + 6), grp, fill=(160, 160, 160), font=f)
            dr.text((14, y0 + 60 + 28 * len(wrap(nm, fb, LW - 24)) + 28), 'cut across at x = %.2f' % xc, fill=(160, 160, 160), font=f)
for j, (rule, name) in enumerate(RULES):
    x0 = LW + j * CW
    dr.text((x0 + 2, 112), name, fill=(245, 225, 150) if rule == 'm_w3' else (235, 235, 235), font=fb)
    dr.text((x0 + 2, 142), 'passes %d of 11 sets on panel2' % npass[rule], fill=(140, 225, 140) if npass[rule] else (240, 130, 115), font=f)
    if j:
        dr.line((x0 - 7, 108, x0 - 7, H - 12), fill=(50, 54, 66), width=2)
# the skin strip: what the voxel pictures above cannot show
sk = os.path.join(HERE, 'skin-basilica.png')
if os.path.exists(sk):
    a = Image.open(sk).convert('RGB'); a = a.resize((W - 28, int(a.size[1] * (W - 28) / a.size[0])), Image.LANCZOS)
    big = Image.new('RGB', (W, H + a.size[1] + 120), (12, 13, 18)); big.paste(im, (0, 0)); d2 = ImageDraw.Draw(big)
    d2.text((14, H + 16), 'What the rough pictures above cannot show: the skin of the basilica close up, the SAME place for the four rules', fill=(240, 240, 240), font=ft)
    d2.text((14, H + 58), 'The tiles are those of panel2, worked point by point. The new rule has a toothed, whiskered skin with dust at every width, away from its six planes; along has a few droplets here (fin combs elsewhere: 24 of its 120 tiles fail); two planes and one plane are clean lines.', fill=(200, 200, 200), font=f)
    big.paste(a, (14, H + 96)); im = big
bd = os.path.join(HERE, 'bud.png')
if os.path.exists(bd):
    a = Image.open(bd).convert('RGB'); a = a.resize((W - 28, int(a.size[1] * (W - 28) / a.size[0])), Image.LANCZOS)
    H2 = im.size[1]; big = Image.new('RGB', (W, H2 + a.size[1] + 110), (12, 13, 18)); big.paste(im, (0, 0)); d2 = ImageDraw.Draw(big)
    d2.text((14, H2 + 16), 'One bud close up, the same bud for the four rules (order here: new rule, along, two planes, one plane)', fill=(240, 240, 240), font=ft)
    d2.text((14, H2 + 58), "New rule: the bud of the basilica is round but its rim is whiskered and its own buds lie only in the plane; the ears of the rabbit are thin flakes with shards; on the nudged basilica the bud is a tuft of bristles.", fill=(200, 200, 200), font=f)
    big.paste(a, (14, H2 + 92)); im = big
im.save(os.path.join(HERE, 'sheet.png')); print('wrote sheet.png', im.size, npass)
