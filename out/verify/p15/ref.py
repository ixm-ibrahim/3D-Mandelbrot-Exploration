import numpy as np
from PIL import Image
OUT = 'out/verify/p15'
def ref(n, W, H, h, iters, bail):
    ys = (np.arange(H) + 0.5) / H; xs = (np.arange(W) + 0.5) / W
    X, Y = np.meshgrid((xs - 0.5) * h * W / H, (0.5 - ys) * h)
    c = X + 1j * Y
    z = c.copy(); esc = np.abs(z) > bail
    with np.errstate(all='ignore'):
        for k in range(iters):
            z = np.where(esc, z, z ** n + c)
            esc |= ~(np.abs(z) <= bail)
    return esc
for n, tag in ((-2, 'nm2'), (-3, 'nm3')):
    im = Image.open('%s/2d-mercator-m-%s.png' % (OUT, tag)).convert('RGB')
    a = np.asarray(im).astype(int); H, W, _ = a.shape
    cen = a[H // 2, W // 2]
    solid = (np.abs(a - cen).sum(axis=2) < 24)
    best = None
    for bail in (2, 4, 8, 16, 64, 1000):
        for iters in (13, 14):
            e = ref(n, W, H, 3.072, iters, bail)
            m = np.zeros_like(e); m[60:H-110, 90:W-150] = True
            inter = (e & solid & m).sum(); union = ((e | solid) & m).sum()
            iou = inter / max(union, 1)
            if best is None or iou > best[0]: best = (iou, bail, iters, e)
    print('n', n, 'centre colour', cen, 'app solid share %.4f' % solid.mean(), 'best IoU with escaping region %.3f at bail %s iters %s; ref escaping share %.4f' % (best[0], best[1], best[2], best[3].mean()))
    Image.fromarray((best[3] * 255).astype('uint8')).save('%s/ref-%s.png' % (OUT, tag))
    Image.fromarray((solid * 255).astype('uint8')).save('%s/appsolid-%s.png' % (OUT, tag))
