"""Round 15, entry: the page's 2D view of the cut at z = 0, Square pillow against Sphere inversions, one plane
(whose cut is the flat set), same page, same settings, pixel by pixel. And the flat Mandelbrot set itself, worked
in numpy at the centre of every pixel with the page's 14 steps and escape radius 64, against the page's inside colour."""
import numpy as np
from PIL import Image
D = 'out/r15/entry/'
for n in ('cut-m', 'cut-j-basilica', 'cut-j-rabbit', 'cut-j-03', 'cut-j-i'):
    a = np.asarray(Image.open(D + 'sp-' + n + '.png').convert('RGB')).astype(int)
    b = np.asarray(Image.open(D + 'ref-' + n + '.png').convert('RGB')).astype(int)
    d = np.abs(a - b).max(axis=2)
    ins = lambda im: (np.abs(im - np.array([232, 223, 201])).max(axis=2) < 14)
    ia, ib = ins(a), ins(b)
    print('%-16s %dx%d: pixels that differ by more than 8 levels: %d (%.3f %%), by more than 40: %d; inside colour: pillow %d, one plane %d, in one but not the other: %d' % (
        n, a.shape[1], a.shape[0], int((d > 8).sum()), 100.0 * (d > 8).mean(), int((d > 40).sum()), int(ia.sum()), int(ib.sum()), int((ia != ib).sum())))
# the flat Mandelbrot set at the pixel centres of sp-cut-m.png (centre -0.5, height 3.2)
a = np.asarray(Image.open(D + 'sp-cut-m.png').convert('RGB')).astype(int)
H, W = a.shape[:2]
ys, xs = np.mgrid[0:H, 0:W]
c = (-0.5 + (xs + 0.5 - W / 2) * 3.2 / H) + 1j * ((H / 2 - ys - 0.5) * 3.2 / H)
z = np.zeros_like(c); alive = np.ones(c.shape, bool)
for k in range(15):
    alive &= np.abs(z) <= 64
    z = np.where(alive, z * z + c, z)
ins = np.abs(a - np.array([232, 223, 201])).max(axis=2) < 14
ui = np.zeros((H, W), bool); ui[:, 735:] = True; ui[640:, :] = True; ui[:60, :80] = True      # the page's own controls lie over these parts
ok = ~ui
print('flat Mandelbrot set (numpy, 14 steps, radius 64) against the inside colour of sp-cut-m.png, away from the controls: set %d pixels, picture %d, in one but not the other %d (%.2f %% of the set)' % (
    int((alive & ok).sum()), int((ins & ok).sum()), int(((alive != ins) & ok).sum()), 100.0 * ((alive != ins) & ok).sum() / max(1, (alive & ok).sum())))
