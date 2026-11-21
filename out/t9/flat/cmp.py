# Compare two folders of pictures pixel for pixel. python out/t9/flat/cmp.py <dirA> <dirB> [diff-prefix]
import sys, os
from PIL import Image
import numpy as np
dA, dB = sys.argv[1], sys.argv[2]
pre = sys.argv[3] if len(sys.argv) > 3 else None
print('A = %s   B = %s' % (dA, dB))
for f in sorted(os.listdir(dB)):
    if not f.endswith('.png') or not os.path.exists(os.path.join(dA, f)): continue
    a = Image.open(os.path.join(dA, f)).convert('RGB'); b = Image.open(os.path.join(dB, f)).convert('RGB')
    if a.size != b.size:
        print(f, 'SIZES DIFFER', a.size, b.size); continue
    A = np.asarray(a).astype(int); B = np.asarray(b).astype(int)
    D = np.abs(A - B).max(axis=2)
    n = int((D > 0).sum())
    print('%-16s size %s max diff %3d, pixels differing %7d (%.3f%%), >8: %6d, >32: %6d, mean abs diff over all %.4f' % (
        f, a.size, D.max(), n, 100.0 * n / D.size, (D > 8).sum(), (D > 32).sum(), np.abs(A - B).mean()))
    if n:
        ys, xs = np.nonzero(D)
        print('    box of differences: x %d..%d y %d..%d; median of the differing pixels %d, 95th percentile %d' % (
            xs.min(), xs.max(), ys.min(), ys.max(), np.median(D[D > 0]), np.percentile(D[D > 0], 95)))
        if pre:
            Image.fromarray((np.clip(D * 8, 0, 255)).astype('uint8')).save(pre + f)
