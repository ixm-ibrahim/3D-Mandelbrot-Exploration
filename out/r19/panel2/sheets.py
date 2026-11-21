"""Round 19, panel2: the pictures. python out/r19/panel2/sheets.py [hair] [across] [groupc]"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel2 as Q
H = Q.H; P = Q.P
turns = P.turns
BG = (12, 14, 20)


def hair_sheet():
    """Rows of six tiles: what the new number counts (red = thin things counted, purple = film of dust or comb) and what it leaves alone."""
    rows = [
        ('flat', 'basilica', 'old', 'A. The FLAT basilica itself. The six tiles the OLD number called worst (old 1.2 to 1.9, line 0.3). New number: nothing counted. Clean, as the eye says.'),
        ('flat', 'sanmarco', 'old', 'B. The FLAT San Marco, the old number\'s six worst tiles. New number: nothing counted.'),
        ('flat', 'airplane', 'old', 'C. The FLAT airplane: strings of beads (orange = loose specks, printed but NOT judged; a string is a line, not a film). New number: clean.'),
        ('twoplane', 'basilica', 'new', 'D. Two planes (the reference look), basilica: its six worst tiles of 120 by the new number. Clean by eye and by number.'),
        ('along', 'basilica', 'new', 'E. Turning plane along, basilica: six worst of 120. Red = thin things counted: combs of fins. Not clean.'),
        ('away', 'basilica', 'new', 'F. Turning plane away, basilica: six worst of 120. Whiskers and streaks (red), loose dust (purple). Not clean.'),
        ('p_tt1024', 'basilica', 'new', 'G. p_tt1024 (round 17 "best newcomer"), basilica: six worst of 120. A film of dust half-way between its planes (purple), needles (red). Not clean.'),
        ('twoplane', 'sanmarco', 'new', 'H. Two planes, San Marco: six worst of 120. Blade-shaped bodies lying against the skin between the planes (red). The number says not clean; the eye must decide.'),
    ]
    CW, CH = H.CW, H.CH; S = 0.62; w, h = int(CW * S), int(CH * S)
    W = 20 + 6 * (w + 6); RH = h + 62; im = Image.new('RGB', (W, 60 + RH * len(rows)), BG); dr = ImageDraw.Draw(im)
    f1, f2, f3 = turns.font(22), turns.font(15), turns.font(12)
    dr.text((12, 8), 'The new hair number: what it counts and what it leaves alone', fill=(240, 240, 240), font=f1)
    dr.text((12, 36), 'Each tile: a close cut of the skin, worked point by point, cream = inside. thin = length of thin things per length of skin line (line %.2f). film = %% of the tile under loose dust or combs (line %.1f). old = round 18\'s number (line 0.3).' % (H.T_FINS, H.T_FILM), fill=(190, 190, 195), font=f3)
    for i, (rule, tag, how, cap) in enumerate(rows):
        y = 58 + i * RH; dr.text((12, y + 2), cap, fill=(230, 230, 235), font=f2)
        meta, tiles = H.load_tiles(rule, tag); sc = H.score_set(rule, tag)
        if not sc:
            continue
        key = (lambda r: -r['old']) if how == 'old' else (lambda r: -max(r['fins'] / H.T_FINS, r['film_pct'] / H.T_FILM, 0.001 * r['old']))
        for j, r in enumerate(sorted(sc, key=key)[:6]):
            s, marks = H.score(tiles[r['k']], want_marks=True)
            t = Image.fromarray(H.paint(tiles[r['k']], marks)).resize((w, h), Image.LANCZOS); x = 12 + j * (w + 6)
            im.paste(t, (x, y + 24))
            bad = r['fins'] > H.T_FINS or r['film_pct'] > H.T_FILM
            dr.text((x + 2, y + 26 + h), 'thin %.2f  film %.1f%%  (old %.2f)  %s' % (r['fins'], r['film_pct'], r['old'], 'NOT CLEAN' if bad else 'clean'), fill=(240, 130, 120) if bad else (150, 220, 150), font=f3)
            dr.text((x + 2, y + 41 + h), '%s deg from the flat plane, zoom %d' % (r['angle'], r['q'] + 1), fill=(150, 150, 155), font=f3)
    p = os.path.join(HERE, 'hair-calibration.png'); im.save(p); return p


def across_sheet(rules=('oneplane', 'twoplane', 'along', 'away', 'lathe', 'p_tt1024')):
    n = 360; W = 150 + len(rules) * (n + 6); im = Image.new('RGB', (W, 70 + 2 * (n + 44)), BG); dr = ImageDraw.Draw(im)
    f1, f2, f3 = turns.font(22), turns.font(15), turns.font(12)
    dr.text((12, 8), 'Cuts ACROSS the x-axis at x = 0, worked point by point: the airplane\'s spines and the cauliflower\'s dents, counted', fill=(240, 240, 240), font=f1)
    dr.text((12, 38), 'Ticks: green = in the flat plane, red = off it. A rule is "truly 3D" here when at least 2 spines or dents are off the flat plane and there is no ring or sheet.', fill=(190, 190, 195), font=f3)
    for i, tag in enumerate(('airplane', 'cauliflower')):
        y = 62 + i * (n + 44); dr.text((12, y + 30), {'airplane': 'Airplane,\nmiddle body\n(80 steps)', 'cauliflower': 'Cauliflower\n(40 steps)'}[tag], fill=(230, 230, 235), font=f2)
        for j, rule in enumerate(rules):
            x = 150 + j * (n + 6); ex = Q.jload(os.path.join(HERE, 'results', 'extra-' + rule + '.json'), {}).get(tag, {})
            p = os.path.join(HERE, 'tiles', rule, 'across_%s.png' % tag)
            if os.path.exists(p):
                im.paste(Image.open(p).convert('RGB').resize((n, n)), (x, y + 20))
            if i == 0:
                dr.text((x + 2, y), (P.load(rule) or {}).get('label', rule)[:44], fill=(230, 230, 235), font=f3)
            if tag == 'airplane' and 'spikes' in ex:
                s = ex['spikes']; ok = (not s['ring']) and s['off_plane'] >= 2
                txt = 'a full disc or ring: a sheet, not spines' if s['ring'] else '%d spines, %d off the flat plane' % (s['n'], s['off_plane'])
            elif tag == 'cauliflower' and 'dimples' in ex:
                s = ex['dimples']; ok = s['off_plane'] >= 2
                txt = '%d dents, %d off the flat plane' % (s['n'], s['off_plane'])
            else:
                continue
            dr.text((x + 2, y + 22 + n), txt + ('' if ok else '  (needs 2)'), fill=(150, 220, 150) if ok else (240, 130, 120), font=f3)
    p = os.path.join(HERE, 'across.png'); im.save(p); return p


def groupc_sheet(rules=('oneplane', 'twoplane', 'along', 'away', 'lathe', 'p_tt1024')):
    S = 250; sets = [('basilica', 'Basilica, c = (-1, 0, 0)\n(for comparison)')] + [(s['tag'], s['name'].replace(', c', ',\nc')) for s in Q.NEWC]
    W = 210 + len(rules) * (S + 8); RH = S + 74; im = Image.new('RGB', (W, 84 + RH * len(sets)), BG); dr = ImageDraw.Draw(im)
    f1, f2, f3 = turns.font(22), turns.font(14), turns.font(12)
    dr.text((12, 8), 'The first step off the x-axis and off the flat plane: the sets that replace "rabbit turned 90 and 30 degrees"', fill=(240, 240, 240), font=f1)
    dr.text((12, 38), 'Rough pictures (257 points a side, 40 steps). First question for each: does the orbit of 0 stay bounded? If not, c is outside that rule\'s own bounded region, dust is expected, and the set is not judged.', fill=(190, 190, 195), font=f3)
    for j, rule in enumerate(rules):
        dr.text((212 + j * (S + 8), 62), (P.load(rule) or {}).get('label', rule)[:36], fill=(230, 230, 235), font=f3)
    for i, (tag, nm) in enumerate(sets):
        y = 82 + i * RH; dr.multiline_text((12, y + 20), nm.replace('off both planes', '\noff both planes').replace('out of the flat plane', '\nout of the flat plane'), fill=(230, 230, 235), font=f2)
        for j, rule in enumerate(rules):
            x = 210 + j * (S + 8); full = P.load(rule); ex = Q.jload(os.path.join(HERE, 'results', 'extra-' + rule + '.json'), {})
            r = (full or {}).get('sets', {}).get(tag)
            if r is None:
                continue
            for base in (os.path.join(HERE, 'tiles'), Q.OLD_TILES):
                pth = os.path.join(base, rule, tag, 'front.png')
                if os.path.exists(pth):
                    t = Image.open(pth).convert('RGB'); t.thumbnail((S, S)); im.paste(t, (x, y)); break
            else:
                dr.rectangle((x, y, x + S, y + S), fill=(18, 20, 26))
            v = Q.verdicts2(rule, tag, full, ex); c = Q.cell(v, Q.ORDER2)
            if c == 'outside':
                txt = 'orbit of 0 leaves at step %d: outside, dust expected, NOT JUDGED' % r['orbit0_leaves_at']; col = (170, 170, 175)
            else:
                ff = [k for k in Q.ORDER2 if v[k][0] is False]
                txt = ('orbit of 0 stays; ' if tag in Q.CTAGS else '') + ('passes every line' if not ff else 'FAILS: ' + ', '.join(Q.TITLE2[k] for k in ff)); col = (150, 220, 150) if not ff else (240, 130, 120)
            cur = ''; yy = y + S + 2
            for wd in txt.split(' '):
                if dr.textlength(cur + ' ' + wd, font=f3) > S - 4:
                    dr.text((x + 2, yy), cur, fill=col, font=f3); yy += 15; cur = wd
                else:
                    cur = (cur + ' ' + wd) if cur else wd
            dr.text((x + 2, yy), cur, fill=col, font=f3)
    p = os.path.join(HERE, 'groupc.png'); im.save(p); return p


if __name__ == '__main__':
    what = sys.argv[1:] or ['hair', 'across', 'groupc']
    if 'hair' in what:
        print(hair_sheet(), flush=True)
    if 'across' in what:
        print(across_sheet(), flush=True)
    if 'groupc' in what:
        print(groupc_sheet(), flush=True)


def montages():
    """For every scored tile set two strips of six tiles: the worst by the new number, and the worst by the OLD number
    (the second is where a ragged or saw-toothed skin shows up, which the new number does not count)."""
    sc = Q.scores(); CW, CH = H.CW, H.CH; os.makedirs(os.path.join(HERE, 'worst'), exist_ok=True)
    for key in sorted(k for k in sc if not k.startswith('_')):
        rows = [r for r in sc[key]['rows'] if r['fins'] is not None]
        tag = next((t for t in Q.CTAGS if key.endswith('-' + t)), None) or key.rsplit('-', 1)[1]; rule = key[:-len(tag) - 1]
        meta, tiles = H.load_tiles(rule, tag)
        im = Image.new('RGB', (6 * (CW // 2 + 4), 2 * (CH // 2 + 34)), BG); dr = ImageDraw.Draw(im); f3 = turns.font(11)
        for i, (ttl, kf) in enumerate((('worst by the NEW number', lambda r: -max(r['fins'] / H.T_FINS, r['film_pct'] / H.T_FILM)), ('worst by the OLD number (look here for a ragged or saw-toothed skin)', lambda r: -r['old']))):
            y = i * (CH // 2 + 34); dr.text((4, y + 2), '%s on %s: %s' % (rule, tag, ttl), fill=(230, 230, 235), font=f3)
            for j, r in enumerate(sorted(rows, key=kf)[:6]):
                s, marks = H.score(tiles[r['k']], want_marks=True)
                im.paste(Image.fromarray(H.paint(tiles[r['k']], marks)).resize((CW // 2, CH // 2), Image.LANCZOS), (j * (CW // 2 + 4), y + 16))
                dr.text((j * (CW // 2 + 4) + 2, y + 17 + CH // 2), 'thin %.2f film %.1f%% old %.2f @%s' % (r['fins'], r['film_pct'], r['old'], r['angle']), fill=(200, 200, 205), font=f3)
        im.save(os.path.join(HERE, 'worst', key + '.png'))
    return os.path.join(HERE, 'worst')


if 'montages' in sys.argv[1:]:
    print(montages(), flush=True)
