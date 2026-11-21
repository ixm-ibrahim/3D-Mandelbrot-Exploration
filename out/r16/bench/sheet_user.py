"""The sheet for the user: the basilica of each new rule beside the two-plane reference, with the pass / fail
lines; then, only for rules that passed stage 1, the Mandelbrot solid and the warning lights.
python out/r16/bench/sheet_user.py     (reads results/ and tiles/, writes sheet-for-user.png)"""
import os, sys, json, textwrap
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bench as B, rules as R, stage2 as S2
font = R.turns.font

ROWS = ['twoplane', 'along', 'away', 'wind2']
NAMES = {'twoplane': 'Two planes, as before (the look you liked)', 'along': 'Turning plane, along (new)', 'away': 'Turning plane, away (new)', 'wind2': 'Pure winding, no flat spot (new)'}
TESTS = {'J1': 'Cut at z = 0 is the flat basilica', 'J2': 'Bodies touch at single points', 'J3': 'Not the flat set spun round the axis',
         'J4': 'Buds in more than one direction, and buds on buds', 'J5': 'One piece, no dust', 'J6': 'No tear in the rule',
         'J7': 'Mirror-symmetric', 'J8': 'Close up: smaller bodies, not streaks'}
TILES = [('front', 'Front'), ('alongx', 'Along the x-axis'), ('cut_x0', 'Cut across the middle (x = 0)'), ('cut_y0', 'Cut at y = 0 (upright)'),
         ('close2', 'Close-up of one bud'), ('close3', 'Closer: a small body on that bud'), ('bud_across', 'That bud cut across')]
S, TW, M = 250, 930, 20
GOOD, BAD, FG, DIM = (150, 220, 150), (245, 135, 120), (236, 236, 236), (185, 190, 200)
f_t, f_h, f_b, f_s = font(26), font(19), font(15), font(14)


def lines_for(name):
    v = B.verdicts(B.load(name)); out = []
    for k, (ok, txt) in v.items():
        w = textwrap.wrap('%s. %s' % (TESTS[k], txt[0].upper() + txt[1:]), 118)
        out.append((k, ok, w))
    return v, out


passers = [n for n in ROWS if n != 'twoplane' and B.passed_stage1(n)]
blocks = []
for n in ROWS:
    v, ls = lines_for(n)
    blocks.append((n, v, ls, max(S + 62, 62 + sum(18 * len(w) + 3 for _k, _o, w in ls))))
W = M + S * len(TILES) + 20 + TW + M
H = 110 + sum(b[3] + 26 for b in blocks)
H2 = 0
for n in passers:
    H2 += 60 + 300 + 18 * 16 + 40 + 60 + S + 70
H += H2 + 150
im = Image.new('RGB', (W, H), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((M, 14), 'Round 16 test bench. Stage 1: the basilica (c = -1) under each new rule, beside the two-plane look', fill=FG, font=f_t)
dr.text((M, 52), 'Each rule is put through the eight tests J1 to J8. A rule goes on to the Mandelbrot solid only if all eight pass. Rough voxel pictures (321 a side); the close-ups and the cuts are worked out afresh at each size.', fill=DIM, font=f_b)
dr.text((M, 74), 'The thresholds sit between rules whose verdict was known beforehand: two planes (only its tear fails), one plane (fails J4), quaternion (fails J3), square pillow (fails J2, J7), Kleinian (fails J1), Mandelbulb (fails J8).', fill=DIM, font=f_b)
y = 110
for n, v, ls, hh in blocks:
    fails = [k for k, (ok, _t) in v.items() if not ok]
    if n == 'twoplane':
        tag, col = 'Reference. Fails only J6: the rule tears, which is why it cannot be used', DIM
    elif not fails:
        tag, col = 'PASSES all eight basilica tests', GOOD
    else:
        tag, col = 'FAILS the basilica: ' + ', '.join(fails), BAD
    dr.text((M, y), NAMES[n], fill=FG, font=f_h); dr.text((M + 470, y + 2), tag, fill=col, font=f_h)
    for k, (tag_, ttl) in enumerate(TILES):
        dr.text((M + k * S + 2, y + 30), ttl, fill=DIM, font=f_s); im.paste(B.load_tile(n, tag_, S - 6), (M + k * S, y + 52))
    ty = y + 52; tx = M + S * len(TILES) + 20
    for k, ok, w in ls:
        dr.text((tx, ty), '%s %s' % (k, 'pass' if ok else 'FAIL'), fill=GOOD if ok else BAD, font=f_b)
        for j, line in enumerate(w):
            dr.text((tx + 72, ty + 18 * j), line, fill=GOOD if ok else BAD, font=f_s)
        ty += 18 * len(w) + 3
    y += hh + 26

for n in passers:
    r2 = S2.load2(n)
    dr.line([(M, y), (W - M, y)], fill=(70, 75, 90), width=2); y += 14
    dr.text((M, y), 'Stage 2: the Mandelbrot solid of %s (the only new rule whose basilica passed; the others were not tried, as agreed)' % NAMES[n].replace(' (new)', ''), fill=FG, font=f_t); y += 44
    mt = [('m_front', 'Front'), ('m_above', 'From above'), ('m_below', 'From below'), ('m_alongx', 'Along the x-axis'), ('m_cut_z0', 'Cut at z = 0'), ('m_cut_y0', 'Cut at y = 0'),
          ('m_cut_x', 'Cut at x = -0.2'), ('m_close', 'Close-up of what stands off the flat plane')]
    S3 = (W - 2 * M) // len(mt)
    for k, (tag_, ttl) in enumerate(mt):
        dr.text((M + k * S3 + 2, y), ttl, fill=DIM, font=f_s); im.paste(B.load_tile(n, tag_, S3 - 6), (M + k * S3, y + 20))
    y += 20 + S3 + 8
    if r2:
        v2 = S2.verdicts2(r2); fails = [k for k, (ok, _a, _b) in v2.items() if not ok]
        dr.text((M, y), ('Mandelbrot solid PASSES' if not fails else 'Mandelbrot solid FAILS: ' + ', '.join(fails) + '. By eye: a lumpy rock with ridges and a few horns, not a body carrying smaller round bodies.'),
                fill=GOOD if not fails else BAD, font=f_h); y += 30
        for k, (ok, ttl, txt) in v2.items():
            dr.text((M, y), '%s %s' % (k, 'pass' if ok else 'FAIL'), fill=GOOD if ok else BAD, font=f_b)
            dr.text((M + 72, y), '%s. %s' % (ttl, txt[0].upper() + txt[1:]), fill=GOOD if ok else BAD, font=f_s); y += 21
        dr.text((M, y + 2), 'M1, M2, M7 use the stage 1 thresholds. M3 to M6 could not be checked against rules with a known verdict (stage 2 is only run on basilica passers): for those the picture decides.', fill=DIM, font=f_s); y += 32
    lp = os.path.join(HERE, 'results', n + '-lights.json')
    if os.path.exists(lp):
        L = json.load(open(lp))
        dr.text((M, y), 'Warning lights only (not part of the verdict): three other Julia sets of the same rule', fill=FG, font=f_h); y += 30
        x = M
        for tag_, c in S2.LIGHTS:
            d = L[tag_]
            dr.text((x + 2, y), 'c = (%g, %g, %g): volume %.2f, biggest piece %.1f %%, %d pieces' % (c[0], c[1], c[2], d['volume'], d['biggest_pct'], d['pieces']), fill=DIM, font=f_s)
            im.paste(B.load_tile(n, 'light_' + tag_, S - 6), (x, y + 20)); im.paste(B.load_tile(n, 'light_' + tag_ + '_z0', S - 6), (x + S, y + 20))
            x += 2 * S + 40
        y += 20 + S + 10
if not passers:
    dr.text((M, y), 'No new rule passed the basilica, so no Mandelbrot solid was tried.', fill=BAD, font=f_h); y += 40
im = im.crop((0, 0, W, y + 16))
out = os.path.join(HERE, 'sheet-for-user.png'); im.save(out); print('wrote', out, im.size)
