"""Round 24, section "push": WHAT HAPPENS at the meeting point, for one rule and the whole panel of c.

    python out/r24/push/necks.py <rule> [case,case,...] [n]      -> cache/necks-<rule>.json, cache/slices-<rule>.png

For every bud of the panel: the inside of a box round the meeting point as blocks; the widest ball that can pass from
the body of 0 into each other body (the NECK), beside the ball that fits in the bodies themselves; and which heights
straight above the meeting point stay inside (the COLUMN). For the other c (inside the main body, Siegel disc,
airplane): the column only. The slices picture is for checking the numbers by eye: rows = c, columns = heights.
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import plib as P
M = P.M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
SL = [0, 3, 6, 10, 16, 24, 32]


def run(name, keys=None, n=80, tag=''):
    if name.startswith('face:'):
        import extra as E
        r = E.get(name)
    else:
        try:
            r = P.rule(name)
        except KeyError:
            import extra as E
            r = E.get(name)
    keys = keys or list(P.CASES); out = {}; rows = []; t0 = time.time()
    for key in keys:
        cs = P.CASES[key]; res = dict(kind=cs['kind'], d=cs['d'], lon=cs['lon']); slow = 2 * cs['d'] < 1.07
        steps = 800 if slow else 400
        h, ins = P.column_test(r, cs, steps=steps); res['column'] = P.column_summary(h, ins); res['column_bits'] = ''.join('1' if b else '0' for b in ins)
        h, ins = P.column_test(r, cs, steps=steps, disc=0.02); res['disc'] = P.column_summary(h, ins)
        if cs['kind'] == 'airplane':
            for x, m in P._airplane_root():
                if 1.5 < m < 10:
                    h, ins = P.column_test(r, cs, steps=steps, at=complex(x)); res['column@%.4f' % x] = P.column_summary(h, ins)
        if cs['kind'] in ('bud', 'root'):
            g, xs, ys, zs = P.grid_inside(r, cs, n=n, steps=300 if slow else 150)
            nk, dx = P.neck(g, xs, ys, zs, cs); res['neck'] = nk; res['block'] = dx
            ok = [(a, b) for a, b in nk if a is not None and b]
            res['neck_max'] = max(a for a, b in ok) if ok else None
            res['ratio_max'] = max(a / b for a, b in ok) if ok else None
            res['ratio_min'] = min(a / b for a, b in ok) if ok else None
            k0 = len(zs) - 1; rows.append((key, [g[:, ::-1, k0 + i].T for i in SL], zs))
            res['share_above'] = float(g[:, :, k0 + 6:].mean())
        out[key] = res
        json.dump(out, open(os.path.join(CACHE, 'necks-%s.json' % (name.replace(':', '_') + tag)), 'w'), indent=1)
        print('%-6s %-9s 2d %.3f | column: top %.3f, inside length %.3f, lowest escape %s | disc top %.3f | %s | %.0f s'
              % (name, key, 2 * cs['d'], res['column'][0], res['column'][1], res['column'][2], res['disc'][0],
                 ('neck / body: ' + ', '.join('%.3f / %.3f' % t if t[0] is not None else 'none' for t in res['neck']) + ' (block %.4f)' % res['block']) if 'neck' in res else '', time.time() - t0))
        sys.stdout.flush()
    fn = name.replace(':', '_') + tag
    json.dump(out, open(os.path.join(CACHE, 'necks-%s.json' % fn), 'w'), indent=1)
    if rows:
        s = 2; w = rows[0][1][0].shape[1] * s; pad = 6; W = 110 + len(SL) * (w + pad); H = 26 + len(rows) * (w + pad)
        im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(13)
        d.text((6, 4), '%s: level cuts through the box round the meeting point (side 0.64), at heights %s' % (name, ', '.join('%.3f' % rows[0][2][i] for i in SL)), fill=(235, 220, 170), font=f)
        for i, (key, sl, zs) in enumerate(rows):
            y = 26 + i * (w + pad); d.text((6, y + 4), key, fill=(200, 200, 210), font=f)
            for j, a in enumerate(sl):
                img = np.zeros(a.shape + (3,), np.uint8); img[...] = (26, 32, 52); img[a] = (238, 228, 200)
                im.paste(Image.fromarray(img).resize((w, w), Image.NEAREST), (110 + j * (w + pad), y))
        im.save(os.path.join(CACHE, 'slices-%s.png' % fn))
    print('done', name, '%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    name = sys.argv[1]; keys = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] != 'all' else None
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    run(name, keys, n, tag=sys.argv[4] if len(sys.argv) > 4 else '')
