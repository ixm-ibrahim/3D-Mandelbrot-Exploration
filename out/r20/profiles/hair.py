"""panel2's hair number on this section's kept tiles (out/r19/panel2/wide/<rule>-<set>.npz, cut by panel2's wide.py).
Nothing of panel2 is written: numbers go to hair.json here, pictures of the six worst tiles to hair-<rule>-<set>.png here.
python hair.py <rule>:<set> ..."""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'panel2'))
import hairnum as H
p = os.path.join(HERE, 'hair.json'); out = json.load(open(p)) if os.path.exists(p) else {}
for arg in sys.argv[1:]:
    rule, tag = arg.split(':'); meta, tiles = H.load_tiles(rule, tag)
    if meta is None:
        print(arg, 'no tiles yet'); continue
    rows = H.score_set(rule, tag); sm = H.summary(rows)
    med = float(np.median([r['fins'] for r in rows if r['fins'] is not None])); medf = float(np.median([r['film_pct'] for r in rows if r['fins'] is not None]))
    out[arg] = dict(summary=sm, median_thin=med, median_film=medf)
    print('%-9s %-9s tiles %3d | thin: worst %.2f, median %.2f (line 0.10) | film: worst %.1f %%, median %.1f %% (line 0.5) | tiles over a line %d | half-planes failing %d of %d' % (
        rule, tag, sm['tiles'], sm['fins_worst'], med, sm['film_worst'], medf, sm['over'], sm['half_planes_failing'], sm['half_planes']))
    print('      by angle (worst thin / worst film % / tiles over):', ' '.join('%s:%.2f/%.1f/%d' % (a, v[0], v[1], v[2]) for a, v in sm['by_angle'].items()), flush=True)
    key = lambda r: -max(r['fins'] / H.T_FINS, r['film_pct'] / H.T_FILM)
    top = sorted(rows, key=key)[:3] + sorted(rows, key=lambda r: abs(max(r['fins'] / H.T_FINS, r['film_pct'] / H.T_FILM) - np.median([max(q['fins'] / H.T_FINS, q['film_pct'] / H.T_FILM) for q in rows])))[:3]
    Wd = Image.new('RGB', (6 * (H.CW + 4), H.CH + 18), (12, 14, 20)); dr = ImageDraw.Draw(Wd)
    for j, r in enumerate(top):
        s, marks = H.score(tiles[r['k']], want_marks=True)
        Wd.paste(Image.fromarray(H.paint(tiles[r['k']], marks)), (j * (H.CW + 4), 18))
        dr.text((j * (H.CW + 4) + 3, 3), '%s thin %.2f film %.1f%% | %s deg, pt %s, w%d' % ('worst' if j < 3 else 'typical', r['fins'], r['film_pct'], r['angle'], r['off'], r['q']), fill=(235, 235, 235))
    Wd.save(os.path.join(HERE, 'hair-%s-%s.png' % (rule, tag)))
    json.dump(out, open(p, 'w'), indent=1)
