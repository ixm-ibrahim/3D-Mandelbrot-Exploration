"""Reviewer check 2: how much does the panel's close-cut number depend on WHERE the skin is looked at?
The builder's closecut (panel.py) with the same hair number, but more half-planes and more skin points.
python out/r18/review/close_sens.py <rule>:<set> [...]     (writes only into out/r18/review/close/)"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R

SETS = dict(basilica=((-1.0, 0.0, 0.0), 1.7), sanmarco=((-0.75, 0.0, 0.0), 1.6), airplane=((-1.754878, 0.0, 0.0), 0.42), cauliflower=((0.25, 0.0, 0.0), 1.15))
DISK = ndimage.iterate_structure(ndimage.generate_binary_structure(2, 1), 3)
CW, CH, CSTEPS = 420, 294, 80
ANGLES = (22.5, 11.25, 5.625, 16.875, 28.125, 33.75, 39.375, 45.0)       # the builder's two first
OFFS = (-0.5, 0.35, -0.8, -0.2, 0.7)                                      # the builder's two first


def hair(mask):          # copied from panel.py: thin stuff a 3-pixel opening removes, per pixel of skin line
    lab, k = ndimage.label(mask)
    if k == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, k + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    op_all = ndimage.binary_opening(np.pad(mask, 8, mode='edge'), DISK)[8:-8, 8:-8]
    op_main = ndimage.binary_opening(np.pad(main, 8, mode='edge'), DISK)[8:-8, 8:-8]
    skin = int((op_main & ~ndimage.binary_erosion(op_main, border_value=1)).sum())
    return float(int((mask & ~op_all).sum()) / max(skin, 1))


def shade(ins, death):
    t = np.clip(np.where(death > 0, death, 0) / float(CSTEPS), 0, 1) ** 0.6
    img = np.zeros(ins.shape + (3,), np.uint8)
    img[..., 0] = (20 + 40 * t).astype(np.uint8); img[..., 1] = (26 + 70 * t).astype(np.uint8); img[..., 2] = (40 + 150 * t).astype(np.uint8)
    img[ins] = (238, 228, 200)
    return img


def go(rule, tag):
    F = R.get(rule); c, L = SETS[tag]
    thick = json.load(open(os.path.join(ROOT, 'out', 'r18', 'panel', 'results', rule + '.json')))['sets'][tag]['flat']['thickest']
    scale = thick / 0.47; rows = []; tiles = {}
    for ang in ANGLES:
        a = np.radians(ang); ca, sa = np.cos(a), np.sin(a)
        xs = np.linspace(-L, L, 401); ss = np.linspace(0.0, L, 201)[1:]
        X, Sg = np.meshgrid(xs, ss, indexing='ij')
        ins, _ = B.inside(F, X, Sg * ca, Sg * sa, c=c, steps=CSTEPS)
        lab, k = ndimage.label(ins)
        if k == 0:
            continue
        big = lab == (1 + int(np.argmax(np.bincount(lab.ravel())[1:])))
        d = ndimage.distance_transform_edt(np.pad(big, ((1, 1), (0, 1)))[1:-1, :-1]); i, j = np.unravel_index(int(np.argmax(d)), d.shape)
        dmax = float(d[i, j] * (xs[1] - xs[0])); s0 = float(ss[j])
        for off in OFFS:
            x0 = float(xs[i] + off * dmax)
            s = np.linspace(s0, 1.3 * L, 20001)
            i1, _ = B.inside(F, np.full_like(s, x0), s * ca, s * sa, c=c, steps=CSTEPS)
            o = np.flatnonzero(~i1)
            if not o.size or o[0] == 0:
                continue
            e = float(s[o[0]])
            for q, hw0 in enumerate((0.1, 0.02, 0.004)):
                hw = hw0 * scale
                x, sg = np.meshgrid(np.linspace(x0 - hw, x0 + hw, CW), np.linspace(e + 0.7 * hw, e - 0.7 * hw, CH))
                it, dt = B.inside(F, x, sg * ca, sg * sa, c=c, steps=CSTEPS)
                hnum = hair(it)
                rows.append(dict(angle=ang, off=off, width=2 * hw, hair=hnum, builders=(ang in ANGLES[:2] and off in OFFS[:2])))
                tiles[(ang, off, q)] = shade(it, dt)
    ok = [r for r in rows if r['hair'] is not None]
    mine = sorted(ok, key=lambda r: -r['hair']); theirs = sorted([r for r in ok if r['builders']], key=lambda r: -r['hair'])
    res = dict(rule=rule, set=tag, tiles=len(ok), builders_worst=theirs[0]['hair'] if theirs else None, worst=mine[0]['hair'],
               over_line=sum(r['hair'] > 0.3 for r in ok), worst_at=dict(angle=mine[0]['angle'], off=mine[0]['off'], width=mine[0]['width']),
               worst_by_angle={str(a): max([r['hair'] for r in ok if r['angle'] == a] or [0]) for a in ANGLES},
               worst_by_off={str(o): max([r['hair'] for r in ok if r['off'] == o] or [0]) for o in OFFS}, rows=rows)
    os.makedirs(os.path.join(HERE, 'close'), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, 'close', '%s-%s.json' % (rule, tag)), 'w'), indent=1)
    # the six worst tiles side by side
    top = mine[:6]; W = Image.new('RGB', (6 * (CW + 4), CH), (12, 14, 20))
    for k, r in enumerate(top):
        q = [w for w in range(3) if abs(2 * (0.1, 0.02, 0.004)[w] * scale - r['width']) < 1e-12][0]
        W.paste(Image.fromarray(tiles[(r['angle'], r['off'], q)]), (k * (CW + 4), 0))
    W.save(os.path.join(HERE, 'close', '%s-%s-worst6.png' % (rule, tag)))
    print('%-9s %-11s tiles %3d | builder\'s 12 tiles: worst %.2f | all tiles: worst %.2f at %s deg, point %s, width %.4f | over 0.3: %d | by angle %s' % (
        rule, tag, len(ok), res['builders_worst'] or -1, res['worst'], mine[0]['angle'], mine[0]['off'], mine[0]['width'], res['over_line'],
        ' '.join('%s:%.2f' % (a, v) for a, v in res['worst_by_angle'].items())), flush=True)
    print('          top six:', ['%.2f@%s/%s/%.3f' % (r['hair'], r['angle'], r['off'], r['width']) for r in top], flush=True)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        t0 = time.time(); rule, tag = arg.split(':'); go(rule, tag); print('   (%.0f s)' % (time.time() - t0), flush=True)
