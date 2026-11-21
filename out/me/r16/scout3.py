"""Scout 3: the one-plane square about a reference plane that turns with the point, with a flat spot at both
coordinate planes:  psi(phi) = q (phi - sin(4 phi) / 4),  q = -1 (diagonals are pole lines, 4 buds) or +1 (8 buds).
python out/me/r16/scout3.py [N]"""
import os, sys, time, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import scout as S, scout2 as S2
turns = S.turns

def turning(q):
    def F(x, y, z):
        phi = np.arctan2(z, y); psi = q * (phi - 0.25 * np.sin(4 * phi)); c, s = np.cos(psi), np.sin(psi)
        yy, zz = c * y + s * z, -s * y + c * z
        X, Y, Z = S.oneplane(x, yy, zz)
        return X, c * Y - s * Z, s * Y + c * Z
    return F

def cutc(F, plane, c, at=0.0, L=1.75, n=401):
    b = np.linspace(-L, L, n); A, B = np.meshgrid(b, b, indexing='ij'); O = np.full_like(A, at)
    ins, death = S.run(F, *{'z': (A, B, O), 'y': (A, O, B), 'x': (O, A, B)}[plane], c=np.array(c, float))
    img = np.zeros((n, n, 3), np.float32); t = np.clip(death / 14.0, 0, 1)
    for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = 18 + (col - 18) * t
    img[ins] = (235, 225, 200)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]

def runm(F, x, y, z, steps=40):
    sh = x.shape; cx, cy, cz = x.ravel().copy(), y.ravel().copy(), z.ravel().copy(); x, y, z = cx.copy(), cy.copy(), cz.copy()
    alive = np.arange(x.size)
    for k in range(steps):
        Xn, Yn, Zn = F(x, y, z); Xn, Yn, Zn = Xn + cx[alive], Yn + cy[alive], Zn + cz[alive]
        keep = Xn * Xn + Yn * Yn + Zn * Zn <= 36
        alive = alive[keep]; x, y, z = Xn[keep], Yn[keep], Zn[keep]
    ins = np.zeros(cx.size, bool); ins[alive] = True; return ins.reshape(sh)

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
    Fm, Fp = turning(-1), turning(1)
    for nm, F in (('q = -1', Fm), ('q = +1', Fp)): S2.checks(F, nm)
    CS = [('c = -1', (-1, 0, 0)), ('rabbit (-0.12, 0.74, 0)', (-0.12, 0.74, 0)), ('c = (-1, 0.15, 0.1)', (-1, 0.15, 0.1)), ('c = (-0.6, 0.3, 0.3)', (-0.6, 0.3, 0.3)), ('c = i (0, 1, 0)', (0, 1, 0))]
    ROWS = [('%s, %s' % (qn, cn), F, c) for qn, F in (('q = -1', Fm), ('q = +1', Fp), ('one plane', S.oneplane)) for cn, c in CS]
    COLS = ['Front', 'From above', 'Along the x-axis', 'Cut z = 0', 'Cut y = 0', 'Cut x = 0']
    W = 250
    sheet = Image.new('RGB', (300 + W * len(COLS), 36 + W * (len(ROWS) + 3)), (12, 14, 20)); dr = ImageDraw.Draw(sheet); f1, f2 = S2.font(16), S2.font(13)
    for k, t in enumerate(COLS): dr.text((306 + k * W, 9), t, fill=(235, 235, 235), font=f1)
    a = np.linspace(-1.75, 1.75, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    for r, (name, F, c) in enumerate(ROWS):
        vol, _ = S.run(F, X, Y, Z, c=np.array(c, float))
        lab, nlab = ndimage.label(vol); big = np.bincount(lab.ravel())[1:].max() / max(vol.sum(), 1) if nlab else 0
        line = 'volume %.2f, biggest piece %.1f %%' % (vol.mean() * 3.5 ** 3, 100 * big); print('%-40s %s' % (name, line), flush=True)
        tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=-60, el=75), turns.render(vol, az=0, el=0), cutc(F, 'z', c), cutc(F, 'y', c), cutc(F, 'x', c, L=1.2)]
        y0 = 36 + r * W
        dr.text((8, y0 + W // 2 - 20), name, fill=(230, 230, 230), font=f2); dr.text((8, y0 + W // 2), line, fill=(180, 185, 195), font=f2)
        for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (300 + k * W, y0))
    b = np.linspace(-1.5, 1.5, N); Xm, Ym, Zm = np.meshgrid(b - 0.6, b, b, indexing='ij'); m2 = N // 2
    for j, (nm, F) in enumerate((('q = -1', Fm), ('q = +1', Fp), ('one plane', S.oneplane))):
        vm = runm(F, Xm, Ym, Zm); lab, nlab = ndimage.label(vm); big = np.bincount(lab.ravel())[1:].max() / max(vm.sum(), 1)
        up = vm[:, :, m2 + 1:].sum(); line = 'volume %.2f, biggest piece %.1f %%' % (vm.mean() * 27, 100 * big); print('Mandelbrot solid, %-10s %s' % (nm, line), flush=True)
        y0 = 36 + (len(ROWS) + j) * W
        dr.text((8, y0 + W // 2 - 20), 'Mandelbrot solid, ' + nm, fill=(230, 230, 230), font=f2); dr.text((8, y0 + W // 2), line, fill=(180, 185, 195), font=f2)
        tiles = [turns.render(vm, az=-60, el=22), turns.render(vm, az=-60, el=75), turns.render(vm, az=0, el=0)]
        for pl in (vm[:, :, m2], vm[:, m2, :], vm[int(round((N - 1) * (0.6 - 0.2 + 1.5) / 3.0)), :, :]):     # third: the cut x = -0.2
            img = np.zeros((N, N, 3), np.uint8); img[:] = 18; img[pl] = (235, 225, 200); tiles.append(np.transpose(img, (1, 0, 2))[::-1])
        for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (300 + k * W, y0))
    out = os.path.join(HERE, 'scout3-%d.png' % N); sheet.save(out); print('wrote', out)
