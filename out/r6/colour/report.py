"""All comparisons and sheets of a finished set against the reference: python out/r6/colour/report.py <label>

Writes cmp-fixed-<label>.log, accept-<label>.log, accept-ref.log, the pair sheets, pairs-extra-ref-<label>.png,
zoom-<label>.png and diffmaps-<label>.png into out/r6/colour/.
"""
import contextlib, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes as s
import numpy as np
from PIL import Image, ImageDraw

lab = sys.argv[1]
def log(name, fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): fn()
    open(os.path.join(s.HERE, name), 'w', encoding='utf-8').write(buf.getvalue())
    return buf.getvalue()

out = log('cmp-fixed-%s.log' % lab, lambda: s.cmp('ref', lab))
print(out.strip().splitlines()[-1])
for l in out.splitlines():
    if 'difference   0 ' not in l and 'largest channel' in l: print('  ', l)
for which in ('ref', lab):
    out = log('accept-%s.log' % which, lambda: s.accept(which))
    print('\n'.join(out.strip().splitlines()[-11:]))
with contextlib.redirect_stdout(io.StringIO()):
    s.sheets('ref', lab)
    s.grid([s.tile(l, n, 300, l + ' ' + n) for n, _ in s.EXTRA for l in ('ref', lab)], 4, 'pairs-extra-ref-%s.png' % lab)
    tiles = []
    for sn in ('jb', 'm', 'jr', 'k'):
        for un in ('shell1', 'planes'):
            base = s.load(lab, 'a-%s-%s-qB' % (sn, un)); w, h = base.size
            for z, vn in ((2, 'z2'), (8, 'z8')):
                cw, ch = w / z, h / z
                crop = base.resize((330, round(330 * h / w)), Image.LANCZOS, box=((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2))
                ImageDraw.Draw(crop).text((4, 2), '%s %s Balanced, middle x%d' % (sn, un, z), fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
                tiles.append(crop)
                tiles.append(s.tile(lab, 'a-%s-%s-%s' % (sn, un, vn), 330, '%s %s zoomed in x%d' % (sn, un, z)))
    s.grid(tiles, 8, 'zoom-%s.png' % lab)
    tiles = []
    for combo in ('m-shell1', 'jb-shell1', 'jr-cross'):
        base = s.load(lab, 'a-%s-qB' % combo)
        for v in ('qF', 'qN', 'qU', 'd3'):
            d = np.abs(np.asarray(base).astype(int) - np.asarray(s.load(lab, 'a-%s-%s' % (combo, v))).astype(int)).max(axis=2)
            t = Image.fromarray(np.clip(d * 3, 0, 255).astype('uint8')).convert('RGB').resize((330, round(330 * base.height / base.width)))
            ImageDraw.Draw(t).text((4, 2), '%s: %s against Balanced, difference x3' % (combo, v), fill=(255, 255, 255))
            tiles.append(t)
    s.grid(tiles, 4, 'diffmaps-%s.png' % lab)
print('sheets written')
