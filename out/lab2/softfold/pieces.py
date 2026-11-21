"""Count the separate pieces of the solid in the 2D slice pictures (PNG analysis).
   python out/lab2/softfold/pieces.py [folder] [file prefix]
The 2D view paints the solid in one flat colour. It is read from a pixel known to be inside (the z = 0 picture
of the same series), then pixels within a tolerance of it are labelled with 8-neighbour connectivity. Pieces
under 0.05 % of the picture are ignored. The zoom strip on the right of the stage, the hint box at the bottom
left and the axis triad are masked out."""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage
folder = sys.argv[1] if len(sys.argv) > 1 else 'out/lab2/softfold'
pre = sys.argv[2] if len(sys.argv) > 2 else ''
series = [('m2d-z%s.png', ['000', '010', '025', '050'], (-0.6, 0.0, 3.2), (-0.1, 0.0)), ('j-bas-2d-z%s.png', ['000', '020'], (0.0, 0.0, 3.0), (0.0, 0.0))]
for pat, hs, (cx, cy, vh), ref in series:
    col = None
    for h in hs:
        p = os.path.join(folder, pre + pat % h)
        if not os.path.exists(p): continue
        im = np.asarray(Image.open(p).convert('RGB')).astype(int); H, W = im.shape[:2]
        if col is None:
            px, py = int(W / 2 + (ref[0] - cx) * H / vh), int(H / 2 - (ref[1] - cy) * H / vh)
            col = np.median(im[py - 3:py + 4, px - 3:px + 4].reshape(-1, 3), axis=0)
        solid = (np.abs(im - col).max(axis=2) <= 8)
        solid[:, W - 80:] = False; solid[H - 70:, :370] = False; solid[:60, :90] = False
        lab, n = ndimage.label(solid, structure=np.ones((3, 3)))
        sizes = np.sort(ndimage.sum(solid, lab, range(1, n + 1)))[::-1] if n else np.array([])
        big = sizes[sizes >= 0.0005 * W * H]
        tot = solid.sum()
        print('%-26s z = %.2f: %d pieces of at least 0.05%% of the picture (%d specks below that); largest piece %.1f%% of the solid area; solid covers %.1f%% of the picture; piece sizes in %% of the picture: %s' % (
            os.path.basename(p), int(h) / 100, len(big), n - len(big), 100 * big[0] / tot if len(big) else 0, 100 * tot / (W * H), ', '.join('%.2f' % (100 * s / (W * H)) for s in big[:8])))
