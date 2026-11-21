"""Round 20 check: for the user sheet. One rule, eleven sets: voxel solid (257 a side, the panel's steps), two views
(front = the panel's camera, and straight along the x-axis), and one point-by-point cut across the x-axis.
python out/r20/check/solids.py <rule> [<rule> ...]   -> out/r20/check/tiles/<rule>/<set>_{front,axis,cross}.png, vols/<rule>-<set>.npz
"""
import os, sys, json, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R
turns = R.turns

RAB = (-0.122561, 0.744862, 0.0)
# tag, plain name, c, half box, steps, x of the cut across, half width of that cut
SETS = [
    ('basilica', 'Basilica, c = -1', (-1.0, 0.0, 0.0), 1.7, 40, 0.0, 1.0),
    ('sanmarco', 'San Marco, c = -0.75', (-0.75, 0.0, 0.0), 1.6, 40, 0.0, 1.1),
    ('airplane', 'Airplane, c = -1.7549', (-1.754878, 0.0, 0.0), 0.42, 40, 0.0, 0.2),
    ('cauliflower', 'Cauliflower, c = 0.25', (0.25, 0.0, 0.0), 1.15, 40, 0.0, 1.15),
    ('rabbit', 'Rabbit, c = -0.123 + 0.745 i', RAB, 1.4, 40, -0.12, 1.2),
    ('dendrite', 'Dendrite, c = i', (0.0, 1.0, 0.0), 1.4, 10, 0.0, 1.2),
    ('siegel', 'Siegel disc, c = -0.391 - 0.587 i', (-0.390541, -0.586788, 0.0), 1.45, 40, 0.0, 1.2),
    ('bas_yz', 'Basilica nudged, c = (-1, 0.05, 0.03)', (-1.0, 0.05, 0.03), 1.7, 40, 0.0, 1.0),
    ('bas_zy', 'Basilica nudged, c = (-1, 0.03, 0.05)', (-1.0, 0.03, 0.05), 1.7, 40, 0.0, 1.0),
    ('sm_yz', 'San Marco nudged, c = (-0.75, 0.01, 0.02)', (-0.75, 0.01, 0.02), 1.6, 40, 0.0, 1.1),
    ('rab_up', 'Rabbit lifted, c = (-0.123, 0.745, 0.015)', (-0.122561, 0.744862, 0.015), 1.4, 40, -0.12, 1.2),
]
VIEW = (-78, 24)
N = 257; NC = 300


def cross(F, c, x0, half, n=NC, steps=60):
    y = np.linspace(-half, half, n); z = np.linspace(half, -half, n); Y, Z = np.meshgrid(y, z)
    ins, death = B.inside(F, np.full_like(Y, x0), Y, Z, c=c, steps=steps)
    img = np.zeros((n, n, 3), np.uint8); t = np.clip(death / 14.0, 0, 1)
    for ch, (lo, hi) in enumerate(((22, 60), (26, 90), (44, 160))):
        img[..., ch] = (lo + (hi - lo) * t).astype(np.uint8)
    img[ins] = (238, 228, 200)
    return img, ins


if __name__ == '__main__':
    for rule in sys.argv[1:]:
        F = R.get(rule); td = os.path.join(HERE, 'tiles', rule); os.makedirs(td, exist_ok=True); os.makedirs(os.path.join(HERE, 'vols'), exist_ok=True)
        for tag, name, c, L, steps, x0, half in SETS:
            if os.path.exists(os.path.join(td, tag + '_cross.png')):
                continue
            t0 = time.time()
            vol = B.volume(F, N, L=L, c=c, steps=steps)
            np.savez_compressed(os.path.join(HERE, 'vols', '%s-%s.npz' % (rule, tag)), v=np.packbits(vol))
            Image.fromarray(turns.render(vol, az=VIEW[0], el=VIEW[1])).save(os.path.join(td, tag + '_front.png'))
            Image.fromarray(turns.render(vol, az=0, el=0)).save(os.path.join(td, tag + '_axis.png'))
            img, ins = cross(F, c, x0, half, steps=max(steps, 60) if tag != 'dendrite' else 14)
            Image.fromarray(img).save(os.path.join(td, tag + '_cross.png'))
            print('%s %s: volume %.4f, %.0f s' % (rule, tag, vol.sum() * (2 * L / (N - 1)) ** 3, time.time() - t0), flush=True)
