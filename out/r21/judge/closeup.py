"""Close-ups at 80 steps (twice the magnification of the sheets) of the three rules that matter most.
    python out/r21/judge/closeup.py <rule>         one row, kept in closeup/<rule>.png
    python out/r21/judge/closeup.py stitch         -> closeup.png
Per rule: the basilica's middle body from the two eye positions, and the rabbit round its pinch point from the two
eye positions.  M.solid, 300 x 225 x 210 blocks, half width 0.85 (the sheets use 1.75)."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
D = os.path.join(J.HERE, 'closeup'); os.makedirs(D, exist_ok=True)
NAMES = ['along', 'sheet.evc005e70k16', 'alongmem.c_wake1']
W, H, ND, HW = 300, 225, 210, 0.85          # 400 x 300 x 280 took 7 minutes for along alone; too slow for the other two
VIEWS = [('basilica, middle body, eye 1', (-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.45, 0.5, 1.0)),
         ('basilica, middle body, eye 2 (from above)', (-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.2, 1.0, 0.35)),
         ('rabbit, eye 1', M.RABBIT, (-0.15, 0.25, 0.0), (0.45, 0.5, 1.0)),
         ('rabbit, eye 2 (from above)', M.RABBIT, (-0.15, 0.25, 0.0), (0.2, 1.0, 0.35))]

if __name__ == '__main__':
    pad = 8
    if sys.argv[1] == 'stitch':
        rows = [Image.open(os.path.join(D, nm + '.png')) for nm in NAMES if os.path.exists(os.path.join(D, nm + '.png'))]
        im = Image.new('RGB', (rows[0].width, 44 + sum(r.height for r in rows)), (12, 14, 20)); d = ImageDraw.Draw(im)
        d.text((pad, 8), 'Close-ups, 80 steps, twice the magnification of the sheets', fill=(240, 240, 245), font=M.font(20)); y = 44
        for r in rows:
            im.paste(r, (0, y)); y += r.height
        im.save(os.path.join(J.HERE, 'closeup.png'))
    else:
        nm = sys.argv[1]; r = J.get(nm)
        im = Image.new('RGB', (pad + len(VIEWS) * (W + pad), H + 50), (12, 14, 20)); d = ImageDraw.Draw(im)
        d.text((pad, 4), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(15))
        for j, (ttl, c, centre, cam) in enumerate(VIEWS):
            dep, px = M.solid(r, c, W, H, ND, 80, centre=centre, half_w=HW, cam=cam); x = pad + j * (W + pad)
            d.text((x, 26), ttl, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, 44))
        im.save(os.path.join(D, nm + '.png')); print('closeup', nm)
