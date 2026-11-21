"""words-4: pixels the rough picture draws outside the exact silhouette (more than 4 px away), as a share of the solid.
python out/t9/words/skirt.py  (run from the workspace root)"""
import os, sys
from PIL import Image, ImageFilter, ImageChops
D = os.path.dirname(os.path.abspath(__file__))
def mask(im):
    # background = the colour of the picture's corners; solid = anything more than 14 away from it in some channel
    im = im.convert('RGB'); w, h = im.size
    px = im.load(); corners = [px[3, 3], px[w - 4, 3], px[3, h - 4], px[w - 4, h - 4]]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    d = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L').point(lambda v: 255 if v > 9 else 0)
    return d, bg
for side, dists in (('side', [9, 4.6, 2.6, 1.6]), ('top', [4.6]), ('end', [4.6])):
    for dist in dists:
        r = Image.open(os.path.join(D, 'rc4-%s-%g-rough.png' % (side, dist))); e = Image.open(os.path.join(D, 'rc4-%s-%g-exact.png' % (side, dist)))
        mr, bg = mask(r); me, _ = mask(e)
        grown = me.filter(ImageFilter.MaxFilter(9))          # the exact silhouette, 4 px fatter
        extra = ImageChops.subtract(mr, grown)
        grown_r = mr.filter(ImageFilter.MaxFilter(9)); missing = ImageChops.subtract(me, grown_r)
        n_extra = sum(1 for v in extra.getdata() if v); n_solid = sum(1 for v in me.getdata() if v); n_miss = sum(1 for v in missing.getdata() if v)
        cols = [c for c, v in zip(r.convert('RGB').getdata(), extra.getdata()) if v]
        mean = tuple(round(sum(c[i] for c in cols) / len(cols)) for i in range(3)) if cols else None
        print('%s %g: exact solid %d px, rough extra %d px = %.2f%%, rough missing %d px = %.2f%%, mean colour of extra %s, bg %s' % (side, dist, n_solid, n_extra, 100.0 * n_extra / max(1, n_solid), n_miss, 100.0 * n_miss / max(1, n_solid), mean, bg))
        if side == 'side' and dist == 4.6:
            out = Image.new('RGB', (r.width * 3, r.height)); out.paste(r.convert('RGB'), (0, 0)); out.paste(e.convert('RGB'), (r.width, 0))
            m = e.convert('RGB').copy(); m.paste((255, 0, 255), mask=extra); out.paste(m, (2 * r.width, 0)); out.save(os.path.join(D, 'rc4-side-4.6-diff.png'))
