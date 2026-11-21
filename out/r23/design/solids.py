"""Round 23, design: rough solids (the first block on each line of sight whose orbit never leaves) and the sheets.

    python out/r23/design/solids.py dep <eye> <rule,rule,...> [sets]     compute the depth maps that are missing (cache/)
    python out/r23/design/solids.py sheet                                -> sheet.png (front eye), sheet-top.png (second eye)

Every solid: 280 x 210 x 180 blocks, 40 steps, picture 3.2 wide, centre 0. The same as the rabbit section's, so its
depth maps for the same rule, shape and eye are read from its cache (read only).
Eyes: 'a' = (0.45, 0.5, 1.0) from the front, a little to the right and above; 'top' = (0.2, 1.0, 0.35) from above.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
RCACHE = os.path.join(R.ROOT, 'out', 'r23', 'rabbit', 'cache')
RKEY = {('oneplane', 'basilica'): 'along0', ('alongonce', 'basilica'): 'along1', ('along', 'basilica'): 'along99'}
RSAME = {'oneplane', 'twoplane', 'along', 'alongonce', 'pillowJ'}
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}
DW, DH, DN, DSTEPS, DHALF = 280, 210, 180, 40, 1.6
SETS4 = ['basilica', 'sanmarco', 'rabbit', 'siegel']


def dep(name, sname, eye, compute=True):
    path = os.path.join(CACHE, 'dep-%s-%s-%s.npz' % (name.replace(':', '-'), sname, eye))
    if os.path.exists(path):
        d = np.load(path); return d['depth'], float(d['px'])
    if eye == 'a':
        rk = RKEY.get((name, sname), name if (name in RSAME and sname in ('rabbit', 'siegel', 'dendrite')) else None)
        rp = os.path.join(RCACHE, 'dep-%s-%s-a.npz' % (rk, sname)) if rk else None
        if rp and os.path.exists(rp):
            d = np.load(rp); return d['depth'], float(d['px'])
    if not compute:
        return None
    t0 = time.time(); r = R.get(name); c = R.SETS[sname]
    depth, px = M.solid(r, c, DW, DH, DN, DSTEPS, half_w=DHALF, cam=EYES[eye])
    np.savez_compressed(path, depth=depth, px=px)
    print('dep %-9s %-9s eye %-3s %.0f s' % (name, sname, eye, time.time() - t0)); sys.stdout.flush()
    return depth, px


# what a person sees, written AFTER looking at the tiles (see NOTES.md); at most two short sentences each
CAPTION = {}


def sheet(path, rows, eye, title, sets=SETS4, captions=None):
    captions = captions or {}; pad = 8; lab = 46
    W = pad + len(sets) * (DW + pad); H = 44 + len(rows) * (DH + lab + 6)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(240, 240, 245), font=M.font(20))
    for i, nm in enumerate(rows):
        y = 44 + i * (DH + lab + 6)
        d.text((pad, y), R.PLAIN.get(nm, nm), fill=(235, 220, 170), font=M.font(17))
        if captions.get(nm):
            d.text((pad, y + 24), captions[nm], fill=(170, 180, 195), font=M.font(13))
        for j, s in enumerate(sets):
            x = pad + j * (DW + pad); got = dep(nm, s, eye, compute=False)
            if got is None:
                tile = Image.new('RGB', (DW, DH), (14, 17, 26)); ImageDraw.Draw(tile).text((90, 95), 'not made', fill=(110, 120, 135), font=M.font(13))
            else:
                tile = Image.fromarray(M.shade_solid(*got))
                if not np.isfinite(got[0]).any():
                    ImageDraw.Draw(tile).text((88, 95), 'nothing survives', fill=(150, 160, 175), font=M.font(13))
            im.paste(tile, (x, y + lab)); d.text((x + 6, y + lab + 4), R.SETNAME[s], fill=(150, 160, 175), font=M.font(12))
    im.save(path); return path


if __name__ == '__main__':
    if sys.argv[1] == 'dep':
        eye = sys.argv[2]; names = sys.argv[3].split(','); sets = sys.argv[4].split(',') if len(sys.argv) > 4 else SETS4
        t0 = time.time()
        for nm in names:
            for s in sets:
                dep(nm, s, eye)
        print('done %.0f s' % (time.time() - t0))
    elif sys.argv[1] == 'sheet':
        import captions as C
        rows = ['twoplane', 'along', 'alongonce'] + R.SIX
        print(sheet(os.path.join(HERE, 'sheet.png'), rows, 'a', 'Real shapes, seen from the front (rough blocks, 40 steps)', captions=C.FRONT))
        print(sheet(os.path.join(HERE, 'sheet-top.png'), R.SIX, 'top', 'The six rules of this round, seen from above (rough blocks, 40 steps)', captions=C.TOP))
