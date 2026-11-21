"""N12: do the trap colours stay in the same places? python out/t9/solids/cmp.py r m b x
Each variation against Balanced of the same set-up (60 and 120 iterations against 24; a zoom against the middle of
the unzoomed picture magnified). Pictures halved first. Over the pixels that are on the solid in both pictures:
median hue difference in degrees, share whose hue moved by more than 30 degrees, mean difference of 255.
Also writes one contact sheet a scene (sheet-n-<scene>.png) and a zoom sheet (sheet-z-<scene>.png)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)) + os.sep
SETUPS = ['shell1', 'shell07', 'cross', 'planes']
VARS = ['U', 'F', 'B', 'N', 'd02', 'd3', 'i24', 'i60', 'i120', 'zb', 'z2', 'z8']


def load(p):
    return Image.open(p).convert('RGB')


def hsv(im):
    a = np.asarray(im).astype(np.float32) / 255
    mx, mn = a.max(axis=2), a.min(axis=2)
    d = mx - mn
    h = np.zeros(mx.shape, np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = d > 1e-6
    i = m & (mx == r); h[i] = ((g - b)[i] / d[i]) % 6
    i = m & (mx == g) & (mx != r); h[i] = (b - r)[i] / d[i] + 2
    i = m & (mx == b) & (mx != r) & (mx != g); h[i] = (r - g)[i] / d[i] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx, a


def measure(ia, ib):
    w, h = ia.size
    ia, ib = ia.resize((w // 2, h // 2), Image.LANCZOS), ib.resize((w // 2, h // 2), Image.LANCZOS)
    ha, sa, va, ra = hsv(ia); hb, sb, vb, rb = hsv(ib)
    # the stage's own controls sit at the right edge and in the corners: leave them out
    keep = np.zeros(ha.shape, bool); keep[20:-45, 10:int(ha.shape[1] * 0.88)] = True
    on = keep & (va > 0.2) & (vb > 0.2) & (sa > 0.25) & (sb > 0.25)
    if on.sum() < 500:
        return None
    dh = np.abs(ha - hb); dh = np.minimum(dh, 360 - dh)[on]
    return float(np.median(dh)), 100 * float((dh > 30).mean()), 255 * float(np.abs(ra - rb)[on].mean()), 100 * on.mean()


def crop(im, f):
    w, h = im.size
    cw, ch = w / f, h / f
    return im.crop((int(w / 2 - cw / 2), int(h / 2 - ch / 2), int(w / 2 + cw / 2), int(h / 2 + ch / 2))).resize((w, h), Image.BICUBIC)


for sn in sys.argv[1:]:
    tiles = []
    for un in SETUPS:
        P = lambda v: HERE + 'n-%s-%s-%s.png' % (sn, un, v)
        if not os.path.exists(P('z8')):
            print(sn, un, 'not drawn'); continue
        ims = {v: load(P(v)) for v in VARS}
        row = []
        for v, ref in (('U', 'B'), ('F', 'B'), ('N', 'B'), ('d02', 'B'), ('d3', 'B'), ('i24', 'B'), ('i60', 'i24'), ('i120', 'i24')):
            m = measure(ims[v], ims[ref]); row.append('%s~%s %s' % (v, ref, 'none' if not m else 'hue %4.1f deg, moved %4.1f %%, mean %4.1f' % m[:3]))
        for v, f in (('z2', 2), ('z8', 8)):
            c = crop(ims['zb'], f); c.save(HERE + 'n-%s-%s-zb-x%d.png' % (sn, un, f))
            m = measure(ims[v], c); row.append('%s~zb magnified %s' % (v, 'none' if not m else 'hue %4.1f deg, moved %4.1f %%, mean %4.1f' % m[:3]))
        print('%s %-8s ' % (sn, un) + ' | '.join(row))
        tiles.append([P(v) for v in VARS])
    if not tiles:
        continue
    sc = 0.2
    w, h = ims['B'].size; tw, th = int(w * sc), int(h * sc)
    sheet = Image.new('RGB', (12 * tw, len(tiles) * (th + 16)), (20, 22, 28)); d = ImageDraw.Draw(sheet)
    for r, paths in enumerate(tiles):
        for c, p in enumerate(paths):
            sheet.paste(load(p).resize((tw, th), Image.LANCZOS), (c * tw, r * (th + 16) + 16))
            d.text((c * tw + 3, r * (th + 16) + 2), os.path.basename(p)[2:-4], fill=(230, 230, 230))
    sheet.save(HERE + 'sheet-n-%s.png' % sn)
    # zoom sheet: zb, zb magnified 2, z2, zb magnified 8, z8, at a third of full size
    sc = 0.36; tw, th = int(w * sc), int(h * sc)
    sheet = Image.new('RGB', (5 * tw, len(tiles) * (th + 16)), (20, 22, 28)); d = ImageDraw.Draw(sheet)
    for r, un in enumerate([u for u in SETUPS if os.path.exists(HERE + 'n-%s-%s-z8.png' % (sn, u))]):
        for c, name in enumerate(['zb', 'zb-x2', 'z2', 'zb-x8', 'z8']):
            p = HERE + 'n-%s-%s-%s.png' % (sn, un, name)
            sheet.paste(load(p).resize((tw, th), Image.LANCZOS), (c * tw, r * (th + 16) + 16))
            d.text((c * tw + 3, r * (th + 16) + 2), os.path.basename(p)[2:-4], fill=(230, 230, 230))
    sheet.save(HERE + 'sheet-z-%s.png' % sn)
    print('wrote sheet-n-%s.png, sheet-z-%s.png' % (sn, sn))
