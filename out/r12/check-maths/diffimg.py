import os, sys
import numpy as np
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
for n in ("p2-rab", "p2-m"):
    A = np.asarray(Image.open(os.path.join(here, "new-%s.png" % n)).convert("RGB")).astype(np.int16)
    B = np.asarray(Image.open(os.path.join(here, "v11-%s.png" % n)).convert("RGB")).astype(np.int16)
    d = np.abs(A - B).max(axis=2)
    D = np.zeros_like(A); D[..., 0] = np.clip(d * 4, 0, 255); D[..., 1] = np.where(d > 8, 255, 0); D[..., 2] = np.where(d > 0, 80, 0)
    out = np.concatenate([A, B, D], axis=1).astype(np.uint8)
    Image.fromarray(out).resize((out.shape[1] * 2 // 3, out.shape[0] * 2 // 3)).save(os.path.join(here, "diff-%s.png" % n))
    bg = A[2, 2]; obj = np.abs(A - bg).max(axis=2) > 12; objB = np.abs(B - bg).max(axis=2) > 12
    print(n, "object pixels new %d, v11 %d, in one but not the other %d; of the pixels over 8 levels apart, %d lie where both show the object" % (obj.sum(), objB.sum(), (obj ^ objB).sum(), ((d > 8) & obj & objB).sum()), "; mean difference over object pixels %.2f levels" % d[obj | objB].mean())
