"""Pictures for the prover's notes. python out/r20/prover/pics.py fins | two
fins: the skin of the basilica unrolled round the x-axis (across = turn round the axis, up = distance from the axis),
      at the x where pencil says the first between-plane buds sit; predicted turns marked.
two:  what 'two planes' costs: the flat cut of the rabbit under an even winding, and the upright cut under a one-fold rule."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import lib as L
S = L.S
try:
    font = ImageFont.truetype('segoeui.ttf', 16); small = ImageFont.truetype('segoeui.ttf', 13)
except Exception:
    font = small = ImageFont.load_default()
BG = (12, 14, 20)

def ginv(g, Adeg):
    ta = np.linspace(0, 2 * np.pi, 2000001); return np.degrees(np.interp(np.radians(Adeg), g(ta), ta))

def fins():
    c = L.SETS['basilica']; steps = 60
    panels = []
    rules = [('m_w3 (the new rule)', L.g_sin(3)), ('m_w3lin (even winding)', L.g_lin(3)), ('exact band 10 degrees', L.g_band(3, 10))]
    A2 = 58.98                               # pencil: the turn round the x-axis of P^-1 of the 60-degree bud, before unwinding
    for x0, r0, r1, title in ((1.0413, 0.20, 0.44, 'on the body round +1, at x = 1.04 (where the first between-plane buds must sit)'),
                              (-0.30, 0.30, 0.62, 'on the middle body, at x = -0.30 (the orchestrator\'s "dozen thin spikes")')):
        for name, g in rules:
            F = L.wind(g)
            rm = 0.5 * (r0 + r1); a0, a1 = np.radians(-8.0), np.radians(68.0)
            H = 430; W = int(round(H * (a1 - a0) * rm / (r1 - r0)))
            aa = np.linspace(a0, a1, W); rr = np.linspace(r1, r0, H); Am, Rm = np.meshgrid(aa, rr)
            n = L.member(F, np.full_like(Am, x0), Rm * np.cos(Am), Rm * np.sin(Am), c, steps)
            img = Image.fromarray(L.shade(n, steps)); d = ImageDraw.Draw(img)
            def px(deg):
                return int(round((np.radians(deg) - a0) / (a1 - a0) * (W - 1)))
            for deg in (0, 60):
                d.line([(px(deg), 0), (px(deg), H)], fill=(120, 200, 120), width=1)
            d.line([(px(30), 0), (px(30), H)], fill=(110, 110, 130), width=1)
            pred = [ginv(g, A2), 60 - ginv(g, A2)] if x0 > 0 else []
            for deg in pred:
                d.line([(px(deg), 0), (px(deg), 26)], fill=(240, 120, 90), width=2)
            panels.append((img, f'{name}: {title}' + (f'.  Red ticks = predicted turns {pred[0]:.1f} and {pred[1]:.1f} deg' if pred else '')))
    Wm = max(p[0].size[0] for p in panels); pad = 8; lab = 22; top = 78
    sheet = Image.new('RGB', (pad + 3 * (Wm + pad), top + 2 * (430 + lab + pad)), BG); d = ImageDraw.Draw(sheet)
    d.text((pad, 6), 'The basilica\'s skin unrolled round the x-axis. Across: turn round the x-axis, from -8 to 68 degrees. Up: distance from the x-axis. Cream = inside. 60 steps, point by point.', fill=(235, 235, 235), font=font)
    d.text((pad, 30), 'Green lines = the copy planes at 0 and 60 degrees; grey line = half way (30). Scale is true at mid-height: a round bud looks round, a fin looks like an upright sliver.', fill=(190, 190, 190), font=small)
    d.text((pad, 50), 'What to look for: round buds standing ON the green lines, thin slivers between them.', fill=(190, 190, 190), font=small)
    for i, (img, t) in enumerate(panels):
        x = pad + (i % 3) * (Wm + pad); y = top + (i // 3) * (430 + lab + pad)
        d.text((x, y), t[:int(Wm / 6.3)], fill=(215, 215, 215), font=small); sheet.paste(img, (x, y + lab))
    sheet.save(f'{L.HERE}/fins-unrolled.png'); print('wrote fins-unrolled.png', sheet.size)

def two():
    n = 430; half = 1.6; steps = 60
    u = np.linspace(-half, half, n); s = np.linspace(half, -half, n); U, Sg = np.meshgrid(u, s)
    c = L.SETS['rabbit']; cb = L.SETS['basilica']
    F2 = L.wind(L.g_sin(2)); Ff = L.wind(L.g_fold2()); F3 = L.wind(L.g_sin(3))
    tiles = [
        ('The flat rabbit itself (what the cut z = 0 must be)', L.flat_member(U, Sg, c, steps)),
        ('Wound TWICE (k = 2): the cut z = 0 of the rabbit. Wrong.', L.member(F2, U, Sg, 0 * U, c, steps)),
        ('Wound three times (m_w3): the cut z = 0. Exact.', L.member(F3, U, Sg, 0 * U, c, steps)),
        ('Wound twice, basilica: the cut z = 0 is right (c on the x-axis)', L.member(F2, U, Sg, 0 * U, cb, steps)),
        ('Two planes by one fold: upright cut of the rabbit = lower half, doubled', L.member(Ff, U, 0 * U, Sg, c, steps)),
        ('m_w3: the rabbit cut by the plane at 60 degrees = the flat rabbit, mirrored', L.member(F3, U, Sg * 0.5, Sg * np.sqrt(0.75), c, steps)),
    ]
    pad = 8; lab = 22; top = 40
    sheet = Image.new('RGB', (pad + 3 * (n + pad), top + 2 * (n + lab + pad)), BG); d = ImageDraw.Draw(sheet)
    d.text((pad, 8), 'Two planes or three? Point by point, 60 steps, cream = inside.', fill=(235, 235, 235), font=font)
    for i, (t, m) in enumerate(tiles):
        x = pad + (i % 3) * (n + pad); y = top + (i // 3) * (n + lab + pad)
        d.text((x, y), t, fill=(215, 215, 215), font=small); sheet.paste(Image.fromarray(L.shade(m, steps)), (x, y + lab))
    sheet.save(f'{L.HERE}/two-planes.png'); print('wrote two-planes.png', sheet.size)

if __name__ == '__main__':
    {'fins': fins, 'two': two, 'neck': (lambda: None)}[sys.argv[1]]()


def neck():
    """Unrolled skin close to the neck at x = -0.618 (basilica), m_w3: the same 60 degrees, three distances from the neck."""
    c = L.SETS['basilica']; steps = 80; F = L.wind(L.g_sin(3))
    tiles = []
    for x0, r1 in ((-0.50, 0.30), (-0.57, 0.13), (-0.60, 0.05)):
        a0, a1 = np.radians(-4.0), np.radians(64.0); W = 1100; H = 330
        aa = np.linspace(a0, a1, W); rr = np.linspace(r1, 0.0, H); Am, Rm = np.meshgrid(aa, rr)
        n = L.member(F, np.full_like(Am, x0), Rm * np.cos(Am), Rm * np.sin(Am), c, steps)
        ins = n >= steps
        # count separate slivers on the row of the chart 30 % above the body's skin
        skin = np.array([rr[np.argmax(ins[:, j])] if ins[:, j].any() else 0.0 for j in range(W)])
        img = Image.fromarray(L.shade(n, steps)); d = ImageDraw.Draw(img)
        for deg in (0, 60):
            px = int(round((np.radians(deg) - a0) / (a1 - a0) * (W - 1))); d.line([(px, 0), (px, H)], fill=(120, 200, 120), width=1)
        tiles.append((img, f'x = {x0:.2f} ({abs(x0 + 0.618):.3f} from the neck); up: 0 to {r1:.2f} from the x-axis; the skin of the body lies {np.median(skin):.3f} from the axis (lowest {skin.min():.3f}, highest {skin.max():.3f})'))
    pad = 8; lab = 22; top = 58
    sheet = Image.new('RGB', (pad * 2 + 1100, top + 3 * (330 + lab + pad)), BG); d = ImageDraw.Draw(sheet)
    d.text((pad, 6), 'm_w3, basilica: the skin unrolled round the x-axis close to the neck at x = -0.618. Across: -4 to 64 degrees. 80 steps.', fill=(235, 235, 235), font=font)
    d.text((pad, 30), 'Green = copy planes. NOT true to scale across (stretched to fit): the point is how many slivers stand between two green lines.', fill=(190, 190, 190), font=small)
    for i, (img, t) in enumerate(tiles):
        y = top + i * (330 + lab + pad); d.text((pad, y), t, fill=(215, 215, 215), font=small); sheet.paste(img, (pad, y + lab))
    sheet.save(f'{L.HERE}/neck-unrolled.png'); print('wrote neck-unrolled.png', sheet.size)

if __name__ == '__main__' and sys.argv[1] == 'neck':
    neck()
