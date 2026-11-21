"""Scout 2: 'wind m times about the real axis, take the one-plane square, unwind'. python out/me/r16/scout2.py [N]
F_m(v) = Rot_x(-(m-1) phi) . E1( Rot_x((m-1) phi) v ),  phi = azimuth of (y, z).  m = 1 one plane, m = 2 two planes, ..."""
import os, sys, time, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import scout as S
turns = S.turns

def wind(m):
    def F(x, y, z):
        phi = np.arctan2(z, y); a = (m - 1) * phi; c, s = np.cos(a), np.sin(a)
        yy, zz = c * y - s * z, s * y + c * z                       # turn the point on by (m - 1) phi about x
        X, Y, Z = S.oneplane(x, yy, zz)
        return X, c * Y + s * Z, -s * Y + c * Z                     # and the answer back
    return F

def checks(F, name):
    rng = np.random.default_rng(5)
    P = rng.normal(size=(200000, 3))
    X, Y, Z = F(P[:, 0], P[:, 1], 0 * P[:, 2]); e1 = np.abs(np.stack([X - (P[:, 0] ** 2 - P[:, 1] ** 2), Y - 2 * P[:, 0] * P[:, 1], Z])).max()
    X, Y, Z = F(P[:, 0], 0 * P[:, 1], P[:, 2]); e2 = np.abs(np.stack([X - (P[:, 0] ** 2 - P[:, 2] ** 2), Y, Z - 2 * P[:, 0] * P[:, 2]])).max()
    A = P / np.linalg.norm(P, axis=1)[:, None]; js = []
    for h in (1e-4, 1e-5, 1e-6):
        B = A + h * rng.normal(size=A.shape)
        js.append(np.linalg.norm(np.stack(F(*A.T)) - np.stack(F(*B.T)), axis=0).max())
    fa = np.stack(F(*A.T), 1); mz = np.stack(F(A[:, 0], A[:, 1], -A[:, 2]), 1); my = np.stack(F(A[:, 0], -A[:, 1], A[:, 2]), 1)
    q = np.stack(F(A[:, 0], -A[:, 2], A[:, 1]), 1)                 # quarter turn about x: (y, z) -> (-z, y)
    print('%-22s plane z=0 %.1e | plane y=0 %.1e | largest jump at 1e-4, 1e-5, 1e-6: %.1e %.1e %.1e | mirror z %.1e, mirror y %.1e, quarter turn %.1e | length kept %.1e'
          % (name, e1, e2, js[0], js[1], js[2], np.abs(mz - fa * [1, 1, -1]).max(), np.abs(my - fa * [1, -1, 1]).max(),
             np.abs(q - np.stack([fa[:, 0], -fa[:, 2], fa[:, 1]], 1)).max(), np.abs(np.linalg.norm(fa, axis=1) - 1).max()), flush=True)

def font(s):
    for nme in ('segoeui.ttf', 'arial.ttf'):
        try: return ImageFont.truetype(nme, s)
        except OSError: pass
    return ImageFont.load_default()

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
    F2, F3, F4 = wind(2), wind(3), wind(4)
    for nm, F in (('m = 2', F2), ('m = 3', F3), ('m = 4', F4)): checks(F, nm)
    ROWS = [('m = 2 (two planes), c = -1', F2, (-1, 0, 0)), ('m = 3 (three planes), c = -1', F3, (-1, 0, 0)), ('m = 4 (four planes), c = -1', F4, (-1, 0, 0)),
            ('m = 2, the rabbit c = (-0.12, 0.74, 0)', F2, (-0.12, 0.74, 0)), ('m = 2, c = (-1, 0.15, 0.1)', F2, (-1, 0.15, 0.1)),
            ('m = 2, c = (-0.6, 0.3, 0.3)', F2, (-0.6, 0.3, 0.3)), ('m = 2, c = (0, 0, 0.6)', F2, (0, 0, 0.6))]
    COLS = ['Front', 'From above', 'Along the x-axis', 'Cut z = 0', 'Cut y = 0', 'Cut x = 0']
    W = 300
    sheet = Image.new('RGB', (330 + W * len(COLS), 36 + W * (len(ROWS) + 1)), (12, 14, 20)); dr = ImageDraw.Draw(sheet); f1, f2 = font(16), font(14)
    for k, t in enumerate(COLS): dr.text((336 + k * W, 9), t, fill=(235, 235, 235), font=f1)
    a = np.linspace(-1.75, 1.75, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    from scipy import ndimage
    def cutc(F, plane, c, at=0.0, L=1.75, n=401):
        b = np.linspace(-L, L, n); A, B = np.meshgrid(b, b, indexing='ij'); O = np.full_like(A, at)
        ins, death = S.run(F, *{'z': (A, B, O), 'y': (A, O, B), 'x': (O, A, B)}[plane], c=np.array(c, float))
        img = np.zeros((n, n, 3), np.float32); t = np.clip(death / 14.0, 0, 1)
        for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = 18 + (col - 18) * t
        img[ins] = (235, 225, 200)
        return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]
    for r, (name, F, c) in enumerate(ROWS):
        t0 = time.time(); vol, _ = S.run(F, X, Y, Z, c=np.array(c, float))
        lab, nlab = ndimage.label(vol); big = np.bincount(lab.ravel())[1:].max() / max(vol.sum(), 1) if nlab else 0
        line = 'volume %.2f, biggest piece %.1f %%' % (vol.mean() * 3.5 ** 3, 100 * big)
        print('%-42s %s  %.0f s' % (name, line, time.time() - t0), flush=True)
        tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=-60, el=75), turns.render(vol, az=0, el=0), cutc(F, 'z', c), cutc(F, 'y', c), cutc(F, 'x', c, L=1.2)]
        y0 = 36 + r * W
        dr.text((8, y0 + W // 2 - 22), name, fill=(230, 230, 230), font=f2); dr.text((8, y0 + W // 2), line, fill=(180, 185, 195), font=f2)
        for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (330 + k * W, y0))
    # a first peek at the Mandelbrot solid of m = 2 (start at c)
    b = np.linspace(-1.5, 1.5, N); Xm, Ym, Zm = np.meshgrid(b - 0.6, b, b, indexing='ij')
    def runm(F, x, y, z):
        sh = x.shape; cx, cy, cz = x.ravel().copy(), y.ravel().copy(), z.ravel().copy(); x, y, z = cx.copy(), cy.copy(), cz.copy()
        alive = np.arange(x.size)
        for k in range(40):
            Xn, Yn, Zn = F(x, y, z); Xn, Yn, Zn = Xn + cx[alive], Yn + cy[alive], Zn + cz[alive]
            keep = Xn * Xn + Yn * Yn + Zn * Zn <= 36
            alive = alive[keep]; x, y, z = Xn[keep], Yn[keep], Zn[keep]
        ins = np.zeros(cx.size, bool); ins[alive] = True; return ins.reshape(sh)
    vm = runm(F2, Xm, Ym, Zm); lab, nlab = ndimage.label(vm); big = np.bincount(lab.ravel())[1:].max() / max(vm.sum(), 1)
    print('Mandelbrot solid m = 2: volume %.2f, biggest piece %.1f %%' % (vm.mean() * 27, 100 * big), flush=True)
    y0 = 36 + len(ROWS) * W
    dr.text((8, y0 + W // 2 - 22), 'm = 2, Mandelbrot solid (a first peek)', fill=(230, 230, 230), font=f2)
    m2 = N // 2
    tiles = [turns.render(vm, az=-60, el=22), turns.render(vm, az=-60, el=75), turns.render(vm, az=0, el=0)]
    for pl in (vm[:, :, m2], vm[:, m2, :], vm[int(N * 0.5 * (1 + 0.5 / 1.5)), :, :]):
        img = np.zeros((N, N, 3), np.uint8); img[:] = 18; img[pl] = (235, 225, 200); tiles.append(np.transpose(img, (1, 0, 2))[::-1])
    for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (330 + k * W, y0))
    out = os.path.join(HERE, 'scout2-%d.png' % N); sheet.save(out); print('wrote', out)
