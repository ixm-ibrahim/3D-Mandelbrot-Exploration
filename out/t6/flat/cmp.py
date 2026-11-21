import sys, os
from PIL import Image, ImageChops
import numpy as np
d5, d6 = 'out/t6/flat/eq5', 'out/t6/flat/eq6'
for f in sorted(os.listdir(d6)):
    if not f.endswith('.png'): continue
    a = Image.open(os.path.join(d5, f)).convert('RGB'); b = Image.open(os.path.join(d6, f)).convert('RGB')
    if a.size != b.size:
        print(f, 'SIZES DIFFER', a.size, b.size); continue
    A = np.asarray(a).astype(int); B = np.asarray(b).astype(int)
    D = np.abs(A - B).max(axis=2)
    n = (D > 0).sum()
    print('%-16s size %s max diff %3d, pixels differing %7d (%.3f%%), >8: %d, std of picture %.1f' % (f, a.size, D.max(), n, 100.0 * n / D.size, (D > 8).sum(), A.std()))
    if n:
        ys, xs = np.nonzero(D)
        print('    box of differences: x %d..%d y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))
        Image.fromarray((np.clip(D * 8, 0, 255)).astype('uint8')).save(os.path.join('out/t6/flat', 'diff-' + f))
