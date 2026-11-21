"""Round 20 check: the worst close-cut tiles of m_w3 on every set, from panel2's 120 tiles (read only) and from my
tiles at the rule's own angles (wide30/). One row per set: the 4 worst tiles by panel2's new number (thin + film), then
the 3 worst by the OLD number (which also sees ragged, saw-toothed skin: README limit 1), each with its numbers.
python out/r20/check/worst.py [rule]   -> worst-<rule>.png, worst-<rule>.json (per set, per angle)"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
P2 = os.path.join(ROOT, 'out', 'r19', 'panel2'); sys.path.insert(0, P2); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import hairnum as H
import truth as T
rule = sys.argv[1] if len(sys.argv) > 1 else 'm_w3'
TAGS = ['basilica', 'sanmarco', 'airplane', 'cauliflower', 'rabbit', 'siegel', 'bas_yz', 'bas_zy', 'sm_yz', 'rab_up']
CW = H.CW if hasattr(H, 'CW') else 420


def load(path):
    if not os.path.exists(path):
        return []
    z = np.load(path); meta = json.loads(str(z['meta'])); masks = z['masks']; out = []
    for m in meta:
        if 'k' in m:
            out.append((m, np.unpackbits(masks[m['k']], axis=1)[:, :420].astype(bool)))
    return out


W, Hh = 300, 210
im = Image.new('RGB', (7 * (W + 6) + 150, len(TAGS) * (Hh + 40) + 50), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(13); fb = T.font(17)
dr.text((8, 6), '%s: worst skin tiles per set. Left 4: worst by panel2\'s number (red = thin things counted, purple = film). Right 3: worst by the old number (ragged skin shows here).' % rule, fill=(230, 230, 230), font=fb)
summ = {}
for i, tag in enumerate(TAGS):
    tiles = load(os.path.join(P2, 'wide', '%s-%s.npz' % (rule, tag))) + [(dict(m, mine=True), k) for m, k in load(os.path.join(HERE, 'wide30', '%s-%s.npz' % (rule, tag)))]
    rows = []
    for m, mask in tiles:
        s, marks = H.score(mask, want_marks=True)
        if s['fins'] is None:
            continue
        rows.append(dict(angle=m['angle'], off=m['off'], q=m['q'], width=m['width'], fins=s['fins'], film=s['film_pct'], old=s['old'], mask=mask, marks=marks, mine=m.get('mine', False)))
    y0 = 36 + i * (Hh + 40)
    dr.text((8, y0 + 60), tag, fill=(240, 220, 150), font=fb)
    if not rows:
        dr.text((8, y0 + 90), 'no tiles', fill=(200, 200, 200), font=f); continue
    bad = lambda r: r['fins'] > H.T_FINS or r['film'] > H.T_FILM
    by = {}
    for r in rows:
        a = by.setdefault(str(r['angle']), dict(tiles=0, over=0, thin=0.0, film=0.0, old=0.0)); a['tiles'] += 1; a['over'] += int(bad(r)); a['thin'] = max(a['thin'], r['fins']); a['film'] = max(a['film'], r['film']); a['old'] = max(a['old'], r['old'])
    p2rows = [r for r in rows if not r['mine']]
    summ[tag] = dict(by_angle=by, tiles=len(p2rows), over=sum(bad(r) for r in p2rows), thin=max([r['fins'] for r in p2rows] or [0]), film=max([r['film'] for r in p2rows] or [0]),
                     tiles_mine=len(rows) - len(p2rows), over_mine=sum(bad(r) for r in rows if r['mine']))
    dr.text((8, y0 + 86), '%d of %d tiles over' % (summ[tag]['over'], summ[tag]['tiles']), fill=(235, 130, 120) if summ[tag]['over'] else (150, 220, 150), font=f)
    dr.text((8, y0 + 104), '(+ %d of %d at 30/60/150)' % (summ[tag]['over_mine'], summ[tag]['tiles_mine']), fill=(200, 200, 200), font=f)
    new = sorted(rows, key=lambda r: -(r['fins'] / H.T_FINS + r['film'] / H.T_FILM))[:4]
    old = [r for r in sorted(rows, key=lambda r: -r['old']) if not any(r is q for q in new)][:3]
    for j, r in enumerate(new + old):
        img = Image.fromarray(H.paint(r['mask'], r['marks'])).resize((W, Hh), Image.NEAREST)
        x0 = 150 + j * (W + 6) + (10 if j >= 4 else 0); im.paste(img, (x0, y0))
        dr.text((x0, y0 + Hh + 2), 'thin %.2f film %.1f%% old %.2f  %s' % (r['fins'], r['film'], r['old'], 'NOT CLEAN' if bad(r) else 'clean by number'), fill=(235, 130, 120) if bad(r) else (150, 220, 150), font=f)
        dr.text((x0, y0 + Hh + 17), '%.2f deg from the flat plane, %.3f wide' % (r['angle'], r['width']), fill=(170, 170, 170), font=f)
im.save(os.path.join(HERE, 'worst-%s.png' % rule)); json.dump(summ, open(os.path.join(HERE, 'worst-%s.json' % rule), 'w'), indent=1)
for tag, s in summ.items():
    print('%-12s %3d of %3d over; worst thin %.2f film %.1f | by angle (over/tiles thin film old): ' % (tag, s['over'], s['tiles'], s['thin'], s['film']) + ' '.join('%s:%d/%d %.2f %.1f %.1f' % (a, v['over'], v['tiles'], v['thin'], v['film'], v['old']) for a, v in sorted(s['by_angle'].items(), key=lambda kv: float(kv[0]))))
