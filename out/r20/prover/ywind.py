"""A ten-second scout, NOT a gated candidate and not registered with the bench: the same kind of rule wound round the
y-axis (the bud axis of the flat square) instead of the x-axis (the axis the necks sit on). Three point-by-point cuts."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import lib as L
S = L.S
g = L.g_sin(3)
def Fy(x, y, z):
    x, y, z = (np.asarray(t, float) for t in (x, y, z))
    rho = np.hypot(x, z); a = np.arctan2(z, x); ga = g(a)
    return S.oneplane(rho * np.cos(ga), y, rho * np.sin(ga))
rng = np.random.default_rng(2); xx, yy = rng.normal(size=(2, 100000)); X, Y, Z = Fy(xx, yy, 0 * xx)
print('flat plane error', max(np.abs(X - (xx*xx - yy*yy)).max(), np.abs(Y - 2*xx*yy).max(), np.abs(Z).max()))
v = rng.normal(size=(3, 100000)); A = np.array(Fy(*v)); B = np.array(Fy(v[0], v[1], -v[2])); B[2] *= -1; print('mirror z', np.abs(A - B).max())
try:
    small = ImageFont.truetype('segoeui.ttf', 13)
except Exception:
    small = ImageFont.load_default()
n = 420; half = 1.7; steps = 60; u = np.linspace(-half, half, n); s = np.linspace(half, -half, n); U, Sg = np.meshgrid(u, s)
tiles = []
for name in ('basilica', 'rabbit'):
    c = L.SETS[name]
    tiles.append((f'{name}: cut z = 0 (differs from flat at {int(((L.member(Fy, U, Sg, 0*U, c, steps) >= steps) ^ (L.flat_member(U, Sg, c, steps) >= steps)).sum())} points)', L.member(Fy, U, Sg, 0 * U, c, steps)))
    tiles.append((f'{name}: cut y = 0, across the winding axis (across x, up z)', L.member(Fy, U, 0 * U, Sg, c, steps)))
    tiles.append((f'{name}: plane through the y-axis at 60 degrees', L.member(Fy, U * 0.5, Sg, U * np.sqrt(0.75), c, steps)))
# the skin unrolled round the x-axis close to the neck, same window as tile 2 of neck-unrolled.png
c = L.SETS['basilica']; a0, a1 = np.radians(-4.0), np.radians(94.0); W = 1276; H = 300
aa = np.linspace(a0, a1, W); rr = np.linspace(0.13, 0.0, H); Am, Rm = np.meshgrid(aa, rr)
nk = L.member(Fy, np.full_like(Am, -0.57), Rm * np.cos(Am), Rm * np.sin(Am), c, 80)
pad = 8; lab = 22
sheet = Image.new('RGB', (pad + 3 * (n + pad), pad + 2 * (n + lab + pad) + lab + H + pad), (12, 14, 20)); d = ImageDraw.Draw(sheet)
for i, (t, m) in enumerate(tiles):
    x = pad + (i % 3) * (n + pad); y = pad + (i // 3) * (n + lab + pad); d.text((x, y), t, fill=(215, 215, 215), font=small); sheet.paste(Image.fromarray(L.shade(m, steps)), (x, y + lab))
y = pad + 2 * (n + lab + pad); d.text((pad, y), 'basilica, wound round the y-axis: skin unrolled round the X-axis at x = -0.57 (0.048 from the neck), -4 to 94 degrees, 0 to 0.13 from the axis, 80 steps', fill=(215, 215, 215), font=small)
sheet.paste(Image.fromarray(L.shade(nk, 80)), (pad, y + lab)); sheet.save(f'{L.HERE}/scout-ywind.png'); print('wrote scout-ywind.png', sheet.size)
