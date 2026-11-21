"""Round 20 profiles: the same cut or the same voxel view for several rules side by side.

python cmp.py cross <out.png> <set> <x0> <y0> <z0> <half> <n> <steps> <rule> ...   cut across the x-axis at x = x0, centred (y0, z0)
python cmp.py plane <out.png> <set> <ang> <xc> <sc> <half> <n> <steps> <rule> ...  cut by the half-plane at ang degrees, centred (x = xc, distance = sc)
python cmp.py vol   <out.png> <set> <cx> <cy> <cz> <L> <N> <steps> <az> <el> <rule> ...   voxel view of the box centre +- L
python cmp.py thick <set> <steps> <rule> ...     volume and thickness numbers (voxels, 161 a side)
Every tile is point by point (cross, plane) or voxels (vol). Cream = inside.
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import truth as T
import rules as R
import bench as B
import turns
TILE = int(os.environ.get('TILE', '0'))
TRAP = float(os.environ.get('TRAP', '0'))      # only for c = -1 (the bench checks the trap radius 0.05 per rule)

SETS = dict(basilica=(-1.0, 0.0, 0.0), sanmarco=(-0.75, 0.0, 0.0), airplane=(-1.754878, 0.0, 0.0), cauliflower=(0.25, 0.0, 0.0),
            rabbit=(-0.122561, 0.744862, 0.0), dendrite=(0.0, 1.0, 0.0), siegel=(-0.390541, -0.586788, 0.0),
            bas_yz=(-1.0, 0.05, 0.03), rab_up=(-0.122561, 0.744862, 0.015))
SHORT = {'m_w3': 'sinus (m_w3)', 'm_w3lin': 'even winding (m_w3lin)', 'm_w3f': 'flatter sinus (m_w3f)', 'm_w5': 'k = 5 sinus (m_w5)',
         'oneplane': 'one plane (for comparison)', 'along': 'turning along (for comparison)'}


def lab(name):
    if name in SHORT:
        return SHORT[name]
    return name + ': ' + R.RULES[name][1].replace('Wind 3 times, ', '').replace('exact band', 'band')


def row(tiles, labels, title, out, n):
    f = T.font(15); fb = T.font(18)
    W = len(tiles) * (n + 8) + 8; H = n + 70
    im = Image.new('RGB', (W, H), (12, 13, 18)); dr = ImageDraw.Draw(im)
    dr.text((8, 8), title, fill=(230, 230, 230), font=fb)
    for i, (t, l) in enumerate(zip(tiles, labels)):
        im.paste(Image.fromarray(t), (8 + i * (n + 8), 62)); dr.text((8 + i * (n + 8), 38), l, fill=(210, 210, 210), font=f)
    im.save(out); print('wrote', out)


def main():
    mode = sys.argv[1]
    if mode == 'cross':
        out, tag = sys.argv[2:4]; x0, y0, z0, half = map(float, sys.argv[4:8]); n, steps = int(sys.argv[8]), int(sys.argv[9]); names = sys.argv[10:]
        c = SETS[tag]; tiles = []
        y = np.linspace(y0 - half, y0 + half, n); z = np.linspace(z0 + half, z0 - half, n); Y, Z = np.meshgrid(y, z)
        for nm in names:
            m = T.member(R.get(nm), np.full_like(Y, x0), Y, Z, c, steps); tiles.append(T.shade(m, steps))
        row(tiles, [lab(nm) for nm in names], f'{tag}: cut across the x-axis at x = {x0:g}; the tile is {2 * half:g} wide, centred y = {y0:g}, z = {z0:g}; {steps} steps', os.path.join(HERE, out), n)
    elif mode == 'plane':
        out, tag = sys.argv[2:4]; ang, xc, sc, half = map(float, sys.argv[4:8]); n, steps = int(sys.argv[8]), int(sys.argv[9]); names = sys.argv[10:]
        c = SETS[tag]; a = np.radians(ang); tiles = []
        u = np.linspace(xc - half, xc + half, n); s = np.linspace(sc + half, sc - half, n); U, Sg = np.meshgrid(u, s)
        for nm in names:
            m = T.member(R.get(nm), U, Sg * np.cos(a), Sg * np.sin(a), c, steps); tiles.append(T.shade(m, steps))
        row(tiles, [lab(nm) for nm in names], f'{tag}: cut by the plane through the x-axis turned {ang:g} degrees from the flat plane; the tile is {2 * half:g} wide; {steps} steps', os.path.join(HERE, out), n)
    elif mode == 'vol':
        out, tag = sys.argv[2:4]; cx, cy, cz, L = map(float, sys.argv[4:8]); N, steps = int(sys.argv[8]), int(sys.argv[9]); az, el = float(sys.argv[10]), float(sys.argv[11]); names = sys.argv[12:]
        c = SETS[tag]; tiles = []
        for nm in names:
            t0 = time.time()
            p = os.path.join(HERE, 'vol', f'{nm}-{tag}-{cx:g}_{cy:g}_{cz:g}_{L:g}_{N}_{steps}{'_t' if TRAP else ''}.npy'); os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p):
                vol = np.unpackbits(np.load(p))[:N ** 3].reshape(N, N, N).astype(bool)
            else:
                vol = B.volume(R.get(nm), N, L=L, centre=(cx, cy, cz), c=c, steps=steps, trap=TRAP); np.save(p, np.packbits(vol))
            tiles.append(turns.render(vol, az=az, el=el, out=TILE or N)); print(nm, tag, 'volume', float(vol.mean() * (2 * L) ** 3), '%.0f s' % (time.time() - t0), flush=True)
        row(tiles, [lab(nm) for nm in names], f'{tag}: voxel view, box {2 * L:g} wide centred ({cx:g}, {cy:g}, {cz:g}), {N} points a side, {steps} steps', os.path.join(HERE, out), TILE or N)


if __name__ == '__main__':
    main()
