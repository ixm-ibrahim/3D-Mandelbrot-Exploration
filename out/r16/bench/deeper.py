"""One size deeper than stage 1 goes: a close-up of the biggest small body that comes off close-up 3 (so: a bud on a
bud on a bud on the middle body), for the rules named. Writes tiles/<rule>/close4.png and deeper.png.
python out/r16/bench/deeper.py twoplane along"""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bench as B, rules as R
turns = R.turns

names = sys.argv[1:] or ['twoplane', 'along']
out = {}
for n in names:
    F = R.get(n); r = B.load(n); trap = r.get('trap', 0.0)
    v3, L3, pt3 = B.take(n, 'close3')
    o3, lab3, subs3 = B.on_centre_body(v3, L3, pt3, 'sub-bud', pt3)
    if not subs3:
        print(n, 'nothing comes off close-up 3'); continue
    b = subs3[0]; N3 = v3.shape[0]; h3 = 2 * L3 / (N3 - 1); org3 = [pt3[d] - L3 for d in range(3)]
    pt4 = B.piece_point(lab3, b, h3, org3); L4 = float(np.clip(2.2 * b['r_eq'], 0.0015, L3 / 3))
    v4 = B.volume(F, 129, L=L4, centre=pt4, steps=100, trap=trap)
    B.save_tile(n, 'close4', turns.render(v4, az=-60, el=22))
    o4, _l, subs4 = B.on_centre_body(v4, L4, pt4, 'sub-sub-bud', pt4)
    out[n] = dict(box_side=2 * L4, sub_buds=o4['sub_buds'], round=sum(p['round'] >= 0.45 for p in subs4), roundness=o4['roundness'], loose_pct=o4.get('loose_pct'),
                  size_of_body=b['r_eq'], roundness_of_body=b['round'])
    print(n, out[n], flush=True)
S = 420; tags = [('close2', 'Close-up 2: one bud'), ('close3', 'Close-up 3: a small body on it'), ('close4', 'Close-up 4: a smaller body on that')]
im = Image.new('RGB', (S * 3 + 20, (S + 60) * len(names) + 10), (12, 14, 20)); dr = ImageDraw.Draw(im); f = turns.font(17)
for row, n in enumerate(names):
    y = row * (S + 60) + 8
    d = out.get(n)
    dr.text((10, y), '%s%s' % (R.RULES[n][1], '' if not d else ':  close-up 4 is %.4f wide; %d smaller bodies come off it (%d round)' % (d['box_side'], d['sub_buds'], d['round'])), fill=(235, 235, 235), font=f)
    for k, (t, ttl) in enumerate(tags):
        dr.text((12 + k * S, y + 24), ttl, fill=(190, 195, 205), font=turns.font(14)); im.paste(B.load_tile(n, t, S - 6), (10 + k * S, y + 46))
im.save(os.path.join(HERE, 'deeper.png')); print('wrote deeper.png')
