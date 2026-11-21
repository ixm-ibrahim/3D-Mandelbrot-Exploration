"""python out/r21/alongmem/views.py <tag> name [name ...] [steps=50] [sets=basilica,rabbit,siegel] [cams=front,side,top] [w=360] [zoom=1]
One row per rule; for each Julia set the rough solid from several eye positions (M.solid, M.shade_solid).
    front  the library's eye (0.45, 0.5, 1.0)
    side   from the +x end, a little up: the flat page is seen nearly edge on (bodies above and below it show left and right)
    top    from high above the flat page, a little from the side
    axis   straight down the x-axis"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M
CAMS = {'front': (0.45, 0.5, 1.0), 'side': (1.0, 0.35, 0.25), 'top': (0.25, 1.0, 0.45), 'axis': (1.0, 0.02, 0.02), 'back': (-0.45, 0.5, -1.0), 'under': (0.45, -0.6, 1.0)}
SETS = {'basilica': (-1.0, 0.0, 0.0), 'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 'sanmarco': (-0.75, 0.0, 0.0), 'airplane': (-1.754878, 0.0, 0.0), 'mandel': None}

if __name__ == '__main__':
    tag = sys.argv[1]; args = sys.argv[2:]; opt = dict(a.split('=') for a in args if '=' in a); names = [a for a in args if '=' not in a]
    steps = int(opt.get('steps', 50)); w = int(opt.get('w', 360)); h = int(w * 0.8); nd = int(opt.get('nd', 220)); zoom = float(opt.get('zoom', 1.0))
    sets = opt.get('sets', 'basilica,rabbit,siegel').split(','); cams = opt.get('cams', 'front,side,top').split(',')
    centre = tuple(float(t) for t in opt['centre'].split(',')) if 'centre' in opt else None
    rules = [M.bench(n[6:]) if n.startswith('bench:') else R.get(n) for n in names]
    pad = 8; cols = [(s, cm) for s in sets for cm in cams]; t0 = time.time()
    W = pad + len(cols) * (w + pad); H = 50 + len(rules) * (h + 34)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Rough solids, %d steps%s' % (steps, '' if zoom == 1 else ', close-up x%g' % zoom), fill=(240, 240, 245), font=M.font(20))
    for i, r in enumerate(rules):
        y = 50 + i * (h + 34); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(16))
        for j, (s, cm) in enumerate(cols):
            c = SETS[s]; hw = (1.7 if c is None else 1.75) / zoom
            dep, px = M.solid(r, c, w, h, nd, steps, centre=centre, half_w=hw, cam=CAMS[cm]); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 24)); d.text((x + 6, y + 28), '%s, eye: %s' % (s, cm), fill=(150, 160, 175), font=M.font(13))
        print('views', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        im.save(os.path.join(HERE, 'views-%s.png' % tag))
    print('done')
