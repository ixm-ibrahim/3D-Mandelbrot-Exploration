"""Flat z = 0 pictures, same framing: each approach against Sphere inversions with one plane, pixel by pixel."""
import numpy as np
from PIL import Image
J = 'out/proto/judge-engineer/'
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
for kind in ('m2d-z000', 'j-bas-2d-z000'):
    ref = load(J + 'base-inflated/%s.png' % kind)
    H, W, _ = ref.shape
    inside = lambda a: (np.abs(a - np.array([233, 223, 199])).max(axis=2) <= 12)
    rin = inside(ref)
    print(kind, 'size', W, H, 'reference inside px', int(rin.sum()))
    for name, path in [('base-folded', J + 'base-folded/%s.png' % kind), ('base-bulb', J + 'base-bulb/%s.png' % kind),
                       ('radial', J + 'same-frame/radial-%s.png' % kind), ('sine', J + 'same-frame/sine-%s.png' % kind), ('twoplane', J + 'same-frame/twoplane-%s.png' % kind)]:
        a = load(path)
        d = np.abs(a - ref).max(axis=2)
        ain = inside(a)
        print('   %-12s px differing by >40: %6d (%.2f%% of picture); inside in baseline but not here: %5d; inside here but not baseline: %5d'
              % (name, int((d > 40).sum()), 100.0 * (d > 40).sum() / (W * H), int((rin & ~ain).sum()), int((ain & ~rin).sum())))
