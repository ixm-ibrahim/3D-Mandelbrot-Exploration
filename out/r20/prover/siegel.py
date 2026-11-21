"""W6: how thick is the Siegel disc's body, rule by rule, and does it thin as the step count goes up?
    python out/r20/prover/siegel.py
EXPECT (pencil). At the disc's middle alpha = (-0.3686, -0.3378) the flat rule turns without stretching, and a height
h above the flat plane is multiplied by exactly 1 to first order. What decides is the next term:
  one-plane rule:   h -> h (1 - h^2 / (2 d^2)), d = 0.5 = distance from the origin: pulled TOWARD the plane; a body of real thickness.
  m_w3 (sinus):     g(a) = a + 12 a^3, a = h / |y|: h -> h (1 + (12 / y^2 - 2) h^2) = h (1 + 103 h^2): pushed AWAY.
                    A point stays N steps only if h < 1 / sqrt(2 * 103 * N): 0.0090 at 60 steps, 0.0045 at 240, 0.0022 at 960.
                    Thickness falls by half for every fourfold step count: in the limit a sheet.
  m_w3f ('flat'):   g(a) = a + 86.4 a^5: the pull wins below h = y^2 / (d sqrt(2 * 86.4)) = 0.017: a wafer that does NOT thin with steps.
  exact band w:     g(a) = a for |a| < w: h < |y| tan(w) = 0.060 (w = 10), 0.123 (w = 20) at the middle, and less toward the x-axis.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import lib as L
S = L.S
c = L.SETS['siegel']; cc = complex(c[0], c[1])
alpha = (1 - np.sqrt(1 - 4 * cc)) / 2
print('alpha =', alpha, ' |2 alpha| =', abs(2 * alpha), ' turn per step (deg) =', np.degrees(np.angle(2 * alpha)) % 360)
RULES = [('one-plane rule', S.oneplane), ('m_w3 (sinus)', L.wind(L.g_sin(3))), ('m_w3f (flat)', L.wind(L.g_flat(3))), ('m_w5 (sinus, k = 5)', L.wind(L.g_sin(5))),
         ('m_w3lin (even winding)', L.wind(L.g_lin(3))), ('exact band 10 deg', L.wind(L.g_band(3, 10))), ('exact band 20 deg', L.wind(L.g_band(3, 20)))]
NS = [30, 60, 120, 240, 480, 960, 1920, 3840]
hs = np.geomspace(2e-4, 0.8, 140)
spots = [('middle of the disc', alpha), ('30 % of the way to the point 0', alpha * 0.7), ('60 % of the way to the point 0', alpha * 0.4)]
for tag, p in spots:
    n = L.flat_member(np.array([p.real]), np.array([p.imag]), c, 4000)[0]
    print(f'{tag}: ({p.real:.4f}, {p.imag:.4f}); flat orbit bounded for {n} of 4000 steps; distance from the x-axis {abs(p.imag):.3f}')
table = {}
for name, F in RULES:
    for tag, p in spots:
        x = np.full_like(hs, p.real); y = np.full_like(hs, p.imag)
        n = L.member(F, x, y, hs, c, NS[-1])
        row = []
        for N in NS:
            ins = n >= N
            k = len(hs) if ins.all() else int(np.argmin(ins))
            row.append(0.0 if k == 0 else float(hs[k - 1]))
        table[(name, tag)] = row
print('\nhalf-thickness of the body above each spot (largest height below which every tested height stays for N steps; 0.0002 = thinner than the smallest height tested)')
print(f'{"rule":26s} {"spot":32s} ' + ' '.join(f'N={N:<6d}' for N in NS))
for name, F in RULES:
    for tag, p in spots:
        print(f'{name:26s} {tag:32s} ' + ' '.join(f'{v:8.4f}' for v in table[(name, tag)]))
print('\nprediction for m_w3 at the middle, 1 / sqrt(2 * 103 * N): ' + ' '.join(f'{1/np.sqrt(206*N):8.4f}' for N in NS))
y0 = alpha.imag
print(f'prediction for the bands at the middle, |y| tan(w): w = 10: {abs(y0)*np.tan(np.radians(10)):.4f}   w = 20: {abs(y0)*np.tan(np.radians(20)):.4f};   m_w3f: {y0*y0/(0.5*np.sqrt(2*86.4)):.4f}')

# picture: cut across the x-axis through the middle of the disc (plane x = alpha_x), four rules, two step counts
W, H = 560, 250
ys = np.linspace(-0.95, 0.25, W); zs = np.linspace(0.27, -0.27, H); Y, Z = np.meshgrid(ys, zs)
try:
    font = ImageFont.truetype('segoeui.ttf', 15); small = ImageFont.truetype('segoeui.ttf', 13)
except Exception:
    font = small = ImageFont.load_default()
cols = [('one-plane rule', S.oneplane), ('m_w3 (the new rule)', L.wind(L.g_sin(3))), ('m_w3f (wider round band)', L.wind(L.g_flat(3))), ('exact band 20 degrees', L.wind(L.g_band(3, 20)))]
rows = [60, 480]
pad = 8; top = 64; lab = 22
sheet = Image.new('RGB', (pad + len(cols) * (W + pad), top + len(rows) * (H + lab + pad)), (12, 14, 20)); d = ImageDraw.Draw(sheet)
d.text((pad, 8), 'The Siegel disc cut across the x-axis through its middle (x = -0.369). Cream = inside. Left to right is the flat plane; up is off the flat plane.', fill=(235, 235, 235), font=font)
d.text((pad, 32), 'Top row 60 steps, bottom row 480 steps. A body keeps its thickness when the step count goes up; a sheet thins.', fill=(190, 190, 190), font=small)
for j, N in enumerate(rows):
    for i, (name, F) in enumerate(cols):
        n = L.member(F, np.full_like(Y, alpha.real), Y, Z, c, N)
        img = Image.fromarray(L.shade(n, N))
        x0 = pad + i * (W + pad); y0p = top + j * (H + lab + pad)
        col = (n >= N)[:, int(np.argmin(np.abs(ys - alpha.imag)))]
        th = col.sum() * (zs[0] - zs[1])
        d.text((x0, y0p), f'{name}, {N} steps: thickness at the middle {th:.3f}', fill=(220, 220, 220), font=small)
        sheet.paste(img, (x0, y0p + lab))
sheet.save(f'{L.HERE}/siegel-thickness.png')
print('wrote siegel-thickness.png')
