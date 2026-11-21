"""t8: my own rough solids at 80 steps, two eye positions, for the rules that are said to do something along does not.
Usage: python t8_solids.py <tag> <rule names...>   (names: oneplane along evc ease wake1 wake2 keep lag70 vote4)"""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
from PIL import Image, ImageDraw
import mem as M, ck

sheet, am = ck.load('sheet'), ck.load('alongmem')
BY = {'oneplane': M.bench('oneplane'), 'along': M.bench('along'), 'evc': sheet.get('evc005e70k16'), 'ease': sheet.get('ease'), 'vote4': sheet.get('vote4'),
      'wake1': am.get('c_wake1'), 'wake2': am.get('c_wake2'), 'keep': am.get('b_keep'), 'lag70': M.Rule('lag70', 'scout lag, share 0.7', M.lag(0.7))}
tag = sys.argv[1]; rules = [BY[n] for n in sys.argv[2:]]
w, h, nd, steps = 340, 255, 200, 80
views = [('basilica', (-1.0, 0.0, 0.0), (0.45, 0.5, 1.0), None, None), ('basilica, from above-behind', (-1.0, 0.0, 0.0), (-0.7, 1.0, 0.35), None, None),
         ('basilica middle body, close', (-1.0, 0.0, 0.0), (0.3, 0.75, 1.0), (0.0, 0.0, 0.0), 0.95),
         ('rabbit', ck.RABBIT, (0.45, 0.5, 1.0), None, None), ('rabbit, from above-behind', ck.RABBIT, (-0.7, 1.0, 0.35), None, None),
         ('Siegel disc', ck.SIEGEL, (0.45, 0.5, 1.0), None, None)]
pad = 8; t0 = time.time()
W = pad + len(views) * (w + pad); H = 34 + len(rules) * (h + 24)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'checker: rough solids, %d steps, %d blocks deep' % (steps, nd), fill=(240, 240, 245), font=M.font(17))
for i, r in enumerate(rules):
    y = 34 + i * (h + 24)
    for j, (vn, c, cam, ce, hw) in enumerate(views):
        dep, px = M.solid(r, c, w, h, nd, steps, centre=ce, half_w=hw, cam=cam); x = pad + j * (w + pad)
        d.text((x, y), '%s: %s' % (r.name, vn), fill=(235, 220, 170), font=M.font(13)); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 18))
    print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
im.save('out/r21/checker/solids-%s.png' % tag); print('saved', im.size)
