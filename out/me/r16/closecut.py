"""The close look the round-16 bench lacks: is the skin BETWEEN the special planes clean, or does it carry hair,
fins and loose droplets? Point by point (no voxels, no renderer), basilica c = -1, 80 steps.

    python out/me/r16/closecut.py <bench rule name> [more names]

For each rule: cuts through the x-axis at 22.5 and 11.25 degrees from the flat plane, each at three widths
(0.2, 0.04, 0.008) centred on the skin of the middle body at x = -0.3. Writes out/me/r16/closecut-<name>.png and
prints one number per tile:
    hair = (inside pixels that are loose, or that a 3-pixel opening removes from the body) / (pixels of skin line)
A clean skin gives about 0; tufts of hair, fins and droplets give more. Calibration (2026-11-18): see the bottom.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import truth as T

STEPS = 80
ANGLES = (22.5, 11.25)
WIDTHS = (0.1, 0.02, 0.004)          # half widths
X0 = -0.3
W, H = 600, 420
DISK = ndi.generate_binary_structure(2, 1)
DISK = ndi.iterate_structure(DISK, 3)


def edge(F, ang, x0=X0):
    s = np.linspace(0.05, 1.0, 20001); a = np.radians(ang)
    n = T.member(F, np.full_like(s, x0), s * np.cos(a), s * np.sin(a), (-1.0, 0.0, 0.0), STEPS)
    ins = n >= STEPS
    # the skin of the body the axis runs through: the first exit going outward from the axis
    out = np.flatnonzero(~ins)
    return float(s[out[0]]) if out.size and ins[0] else (float(s[np.flatnonzero(ins).max()]) if ins.any() else 0.3)


def hair(mask):
    lab, k = ndi.label(mask)
    if k == 0:
        return float('nan')
    sizes = ndi.sum(mask, lab, range(1, k + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    loose = int(mask.sum() - main.sum())
    pad = np.pad(main, 8, mode='edge')
    opened = ndi.binary_opening(pad, DISK)[8:-8, 8:-8]
    spikes = int((main & ~opened).sum())
    skin = int((opened & ~ndi.binary_erosion(opened, border_value=1)).sum())
    return (loose + spikes) / max(skin, 1)


def look(name, F):
    rows = []; nums = []
    for ang in ANGLES:
        e = edge(F, ang)
        tiles = []
        for hw in WIDTHS:
            n = T.cut(F, ang, (X0 - hw, X0 + hw, e - 0.7 * hw, e + 0.7 * hw), W, H, STEPS)
            tiles.append(T.shade(n, STEPS)); nums.append(hair(n >= STEPS))
        rows.append((f'{name}: plane {ang} degrees from the flat plane, skin at x = {X0} (height {e:.4f}), {STEPS} steps. '
                     f'Widths 0.2, 0.04, 0.008. hair {nums[-3]:.2f}, {nums[-2]:.2f}, {nums[-1]:.2f}', tiles))
    im = Image.new('RGB', (10 + 3 * (W + 10), 10 + len(rows) * (H + 34)), (12, 14, 20)); d = ImageDraw.Draw(im)
    for i, (t, tiles) in enumerate(rows):
        y = 10 + i * (H + 34)
        d.text((10, y), t, fill=(230, 230, 235), font=T.font(17))
        for j, a in enumerate(tiles):
            im.paste(Image.fromarray(a), (10 + j * (W + 10), y + 26))
    im.save(os.path.join(HERE, f'closecut-{name}.png'))
    return nums


if __name__ == '__main__':
    import rules as R
    for nm in sys.argv[1:]:
        nums = look(nm, R.get(nm))
        print(f'{nm:10s} hair ' + ' '.join(f'{v:.2f}' for v in nums) + f'   worst {np.nanmax(nums):.2f}', flush=True)
