"""Scout: the basilica (c = -1) under a handful of cheap closed-form rules. python out/me/r16/scout.py [N]
Each rule F takes arrays x, y, z and returns the 'square' (no c). All are exact on z = 0."""
import os, sys, time, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import turns
EPS = 1e-300

def lathe(x, y, z): return x * x - y * y - z * z, 2 * x * y, 2 * x * z
def oneplane(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); f = r2 / np.maximum(r2 + z * z, EPS)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r
def twoplane(x, y, z):                       # nearest plane's rule: the Figure 4 look, with a tear on |y| = |z|
    a = np.abs(z) <= np.abs(y)
    X1, Y1, Z1 = oneplane(x, y, z); X2, Z2, Y2 = oneplane(x, z, y)
    return np.where(a, X1, X2), np.where(a, Y1, Y2), np.where(a, Z1, Z2)
def quart(k):                                # lathe with the real part pushed left between the two planes
    def F(x, y, z):
        r2 = np.maximum(x * x + y * y + z * z, EPS)
        return x * x - y * y - z * z - k * y * y * z * z / r2, 2 * x * y, 2 * x * z
    return F
def stretch(e):                              # lathe, imaginary part stretched between the two planes
    def F(x, y, z):
        p2 = y * y + z * z; m = 1 + 4 * e * y * y * z * z / np.maximum(p2 * p2, EPS)
        return x * x - p2, 2 * x * y * m, 2 * x * z * m
    return F
def switch(a):                               # one-plane rule about a reference plane that turns smoothly with the point
    def F(x, y, z):
        phi = np.arctan2(z, y); psi = phi - a * 0.25 * np.sin(4 * phi)
        c, s = np.cos(psi), np.sin(psi)
        yy, zz = c * y + s * z, -s * y + c * z                     # turn the point back by psi about x
        X, Y, Z = oneplane(x, yy, zz)
        return X, c * Y - s * Z, s * Y + c * Z
    return F
def latlon(g):                               # longitude doubles, latitude follows g (odd, pole to pole)
    def F(x, y, z):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rho = np.sqrt(x * x + y * y)
        lat = np.arctan2(z, rho); G = g(lat); cg = np.cos(G)
        c2 = np.where(rho > 0, (x * x - y * y) / np.maximum(rho * rho, EPS), 1.0); s2 = np.where(rho > 0, 2 * x * y / np.maximum(rho * rho, EPS), 0.0)
        return r2 * cg * c2, r2 * cg * s2, r2 * np.sin(G)
    return F

RULES = [('Quaternion square (rings)', lathe), ('Sphere inversions, one plane', oneplane), ('Two planes, nearest plane (tears off the axis)', twoplane),
         ('Lathe, real part pushed left between planes, k = 3', quart(3)), ('the same, k = 8', quart(8)), ('the same, k = 20', quart(20)),
         ('Lathe, stretched between planes, e = 1', stretch(1)), ('the same, e = 3', stretch(3)),
         ('One plane about a turning reference plane, a = 1', switch(1.0)),
         ('Latitude times 3, longitude times 2', latlon(lambda L: 3 * L)), ('Latitude 2L + (4/pi^2) L^3, longitude times 2', latlon(lambda L: 2 * L + 4 / np.pi ** 2 * L ** 3))]

C = np.array([-1.0, 0, 0]); STEPS, R2 = 40, 36.0
def run(F, x, y, z, c=C):
    sh = x.shape; x, y, z = x.ravel().copy(), y.ravel().copy(), z.ravel().copy()
    alive = np.arange(x.size); death = np.zeros(x.size, np.int16)
    for k in range(STEPS):
        X, Y, Z = F(x, y, z); X, Y, Z = X + c[0], Y + c[1], Z + c[2]
        keep = X * X + Y * Y + Z * Z <= R2
        death[alive[~keep]] = k + 1; alive = alive[keep]; x, y, z = X[keep], Y[keep], Z[keep]
        if alive.size == 0: break
    ins = np.zeros(death.size, bool); ins[alive] = True
    return ins.reshape(sh), death.reshape(sh)

def cut(F, plane, at=0.0, L=1.75, n=401):
    a = np.linspace(-L, L, n); A, B = np.meshgrid(a, a, indexing='ij'); O = np.full_like(A, at)
    ins, death = run(F, *{'z': (A, B, O), 'y': (A, O, B), 'x': (O, A, B)}[plane])
    img = np.zeros((n, n, 3), np.float32); t = np.clip(death / 14.0, 0, 1)
    for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = 18 + (col - 18) * t
    img[ins] = (235, 225, 200)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1], ins.mean() * (2 * L) ** 2

def font(s):
    for nme in ('segoeui.ttf', 'arial.ttf'):
        try: return ImageFont.truetype(nme, s)
        except OSError: pass
    return ImageFont.load_default()

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 129
    COLS = ['Front', 'Along the x-axis', 'Cut z = 0 (flat plane)', 'Cut y = 0 (upright)', 'Cut x = 0 (across the middle)', 'Cut x = -0.618 (touching point)']
    S = 300
    sheet = Image.new('RGB', (360 + S * len(COLS), 36 + S * len(RULES)), (12, 14, 20)); dr = ImageDraw.Draw(sheet); f1, f2 = font(16), font(14)
    for k, t in enumerate(COLS): dr.text((366 + k * S, 9), t, fill=(235, 235, 235), font=f1)
    a = np.linspace(-1.75, 1.75, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    for r, (name, F) in enumerate(RULES):
        t0 = time.time(); vol, _ = run(F, X, Y, Z)
        tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=0, el=0)]
        cz, _ = cut(F, 'z'); cy, _ = cut(F, 'y'); cx0, a0 = cut(F, 'x', 0.0, L=1.2); cxa, aa = cut(F, 'x', -0.6180339887, L=1.2)
        tiles += [cz, cy, cx0, cxa]
        up = vol[:, :, N // 2 + 1:].sum(); dn = vol[:, :, :N // 2].sum()
        line = 'volume %.2f, neck %.1f %%' % (vol.mean() * 3.5 ** 3, 100 * aa / max(a0, 1e-9))
        print('%-58s %s  above/below %.2f  %.0f s' % (name, line, up / max(dn, 1), time.time() - t0), flush=True)
        y0 = 36 + r * S
        dr.text((8, y0 + S // 2 - 22), name, fill=(230, 230, 230), font=f2); dr.text((8, y0 + S // 2), line, fill=(180, 185, 195), font=f2)
        for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((S - 6, S - 6), Image.LANCZOS), (360 + k * S, y0))
    out = os.path.join(HERE, 'scout-%d.png' % N); sheet.save(out); print('wrote', out)
