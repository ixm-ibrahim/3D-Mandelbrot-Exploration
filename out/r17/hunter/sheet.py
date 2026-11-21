"""Hunter: pictures.  python out/r17/hunter/sheet.py tiles <rule>   (3D views + charts for one known rule)
                      python out/r17/hunter/sheet.py compose          (sheet.png)"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
SK = os.path.join(HERE, 'skin'); HU = os.path.join(HERE, 'hunt'); TL = os.path.join(HERE, 'tiles'); os.makedirs(TL, exist_ok=True)
KNOWN = [('lathe', 'Quaternion square (lathe)'), ('oneplane', 'Sphere inversions, one plane'), ('along', 'Turning plane, along'), ('twoplane', 'Two planes, nearest plane')]
VIEWS = [('a', -65, 28, 'from the front, a little above'), ('c', 150, 22, 'from behind the period-2 end')]
CW, CH = 540, 271


def crossing(val, level, mask):
    a = val - level; out = np.zeros(val.shape, bool)
    out[:-1] |= (a[:-1] * a[1:] <= 0) & mask[:-1] & mask[1:]
    out |= (a * np.roll(a, -1, 1) <= 0) & mask & np.roll(mask, -1, 1)
    return out


def tiles(name):
    import rules as R
    F = R.get(name)
    d = np.load(os.path.join(SK, name + '.npz'))
    lab = d['lab']; N = lab.shape[0]; L = 1.3; cen = np.array([-0.55, 0, 0]); h = 2 * L / (N - 1); lo = np.array([cen[0] - L, -L, -L])
    S = K.skin(F, 361, 720); kind, ang, c = S['kind'], S['ang'], S['c']
    pair = (kind == 0) & ~S['bad']
    c3 = crossing(ang, 1 / 3, pair); c4 = crossing(ang, 0.25, pair); c5 = crossing(ang, 0.2, pair)
    em = (kind == -1) & ((np.roll(kind, 1, 1) != -1) | (np.roll(kind, -1, 1) != -1) | (np.roll(kind, 1, 0) != -1) | (np.roll(kind, -1, 0) != -1))
    curves = [(c[c3], K.PCOL[3], 1), (c[c4], K.PCOL[4], 1)]
    for vn, az, el, _ in VIEWS:
        Image.fromarray(K.render(lab, lo, h, az, el, S=400, half=1.2, centre=cen, curves=curves)).save(os.path.join(TL, '%s-view-%s.png' % (name, vn)))
        Image.fromarray(K.render(lab, lo, h, az, el, S=400, half=1.2, centre=cen)).save(os.path.join(TL, '%s-plain-%s.png' % (name, vn)))
    # chart: what the calculation says
    img = np.zeros(kind.shape + (3,), np.uint8); img[:] = (205, 190, 150)
    img[kind == -1] = (70, 130, 235); img[kind == 1] = (120, 120, 125)
    eq = (S['low'] / S['rho'] > 0.9995) & ~S['bad']
    img[eq] = (235, 90, 90)
    for m, colr in ((c5, K.PCOL[5]), (c4, K.PCOL[4]), (c3, K.PCOL[3])):
        for sh in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            img[np.roll(m, sh, (0, 1))] = colr
    img[S['bad']] = 0
    Image.fromarray(img).resize((CW, CH), Image.LANCZOS).save(os.path.join(TL, name + '-calc.png'))
    per = d['per_out']
    half = np.concatenate([per, per[:, -2::-1]], 1); full = np.concatenate([half, half[:, -2:0:-1]], 1)
    Image.fromarray(K.colour_of(full)).resize((CW, CH), Image.NEAREST).save(os.path.join(TL, name + '-found.png'))


def compose():
    f1, f2, f3 = K.font(26), K.font(17), K.font(14)
    VW = 400; pad = 10
    W = pad + 2 * (VW + pad) + 2 * (CW + pad) + 330
    rows = len(KNOWN)
    hunt = [n for n in ('h_tilt0', 'h_tilt10', 'h_tilt25') if os.path.exists(os.path.join(HU, n + '-view-a.png'))]
    H = 150 + rows * (VW + 34) + (70 + len(hunt) * (330 + 34) if hunt else 0) + 20 + 660
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Where can smaller bodies sit on a Mandelbrot solid? The calculation, and the solids themselves (known rules, rough voxels)', fill=(240, 240, 245), font=f1)
    x = pad; y = 48
    for k, t in ((1, 'main body (rests at one point)'), (2, 'period 2'), (3, 'period 3'), (4, 'period 4'), (5, 'period 5'), (-2, 'longer periods'), (-1, 'bounded, never repeats (smear)')):
        d.rectangle([x, y + 3, x + 16, y + 19], fill=K.PCOL[k]); d.text((x + 22, y), t, fill=(215, 215, 220), font=f2); x += 40 + int(d.textlength(t, font=f2))
    d.text((pad, 76), 'Lines drawn on the solids and charts: green = where the calculation says a period-3 body can attach, orange = period 4, pink = period 5 (charts only).', fill=(200, 205, 215), font=f3)
    d.text((pad, 96), 'Charts: left to right = once round the x-axis (0 = flat plane z = 0, a quarter of the way = upright plane y = 0). Top = the cusp end (+x), bottom = the period-2 end (-x).', fill=(200, 205, 215), font=f3)
    d.text((pad, 116), 'Calculation chart: sand = skin where a turning pair of eigenvalues gives way, blue = skin where the period-2 body must grow on, grey = skin where the resting point simply vanishes (nothing can attach), red = all three sizes equal.', fill=(200, 205, 215), font=f3)
    y = 146
    for name, label in KNOWN:
        r = json.load(open(os.path.join(SK, name + '.json')))
        d.text((pad, y), label, fill=(235, 235, 240), font=f2)
        xs = pad
        for vn, az, el, cap in VIEWS:
            p = os.path.join(TL, '%s-view-%s.png' % (name, vn))
            if os.path.exists(p):
                im.paste(Image.open(p), (xs, y + 26))
            d.text((xs + 6, y + 30), cap, fill=(160, 170, 185), font=f3); xs += VW + pad
        for tg, cap in (('calc', 'the calculation: kind of skin, and the lines'), ('found', 'the solid: what sits 0.03 outside that skin')):
            p = os.path.join(TL, '%s-%s.png' % (name, tg))
            if os.path.exists(p):
                im.paste(Image.open(p), (xs, y + 26 + 50))
            d.text((xs, y + 26 + 28), cap, fill=(200, 205, 215), font=f3); xs += CW + pad
        a = r['skin_area_share']; m = r['match_out']; o = r['outside_out']
        def pc(v): return 'n/a' if v is None else '%.0f %%' % (100 * v)
        lines = ['skin: %s pair, %s period-2 patch,' % (pc(a['pair']), pc(a['minus1'])), '  %s vanishing' % pc(a['plus1']), '',
                 'period 3 found outside %s' % pc(m['p3']['share_of_curve_with_this_period_outside']), '  of the green line',
                 'period 4 outside %s of orange' % pc(m['p4']['share_of_curve_with_this_period_outside']), '',
                 'period 2 outside %s' % pc(m['p2']['share_of_minus1_patch_with_p2_outside']), '  of the blue patch', '',
                 'outside the pair skin:', '  %s flies away, %s smear' % (pc(o['pair']['escaped']), pc(o['pair']['bounded_no_repeat'])), '',
                 'mirror-reversed directions: %s' % pc(r['mirror_reversed_share'])]
        for i, t in enumerate(lines):
            d.text((xs + 4, y + 60 + i * 19), t, fill=(215, 215, 220), font=f3)
        y += VW + 34
    if hunt:
        d.text((pad, y + 6), 'The hunt (NOT candidates for the lab: these rules do not keep the flat cut). One-plane square with its answer turned about the x-axis: the red line is the bent rim on which all three sizes reach 1 together.', fill=(240, 240, 245), font=f2)
        y += 40
        for n in hunt:
            r = json.load(open(os.path.join(HU, n + '.json')))
            d.text((pad, y), r['label'] + '   (rim stands %.3f out of any flat plane; volume %.2f)' % (r['rim_out_of_plane_rms'], r['solid']['volume']), fill=(235, 235, 240), font=f2)
            xs = pad
            for vn in ('a', 'd', 'c'):
                im.paste(Image.open(os.path.join(HU, '%s-view-%s.png' % (n, vn))).resize((330, 330), Image.LANCZOS), (xs, y + 26)); xs += 330 + pad
            sp = Image.open(os.path.join(HU, n + '-spots.png'))
            sp = sp.crop((0, 0, sp.width, min(sp.height, 8 + 2 * (321 + 40))))
            sc = 330 / sp.height
            im.paste(sp.resize((int(sp.width * sc), 330), Image.LANCZOS), (xs, y + 26))
            y += 330 + 34
    if os.path.exists(os.path.join(HU, 'h_ud55-cuts.png')):
        d.text((pad, y + 6), 'Second hunt, rule h_ud55: one-plane square within 15 degrees of the flat plane (flat cut exact), lathe about the UPRIGHT z-axis within 55 degrees of that axis, blended smoothly between. Both mirrors hold.', fill=(240, 240, 245), font=f2)
        d.text((pad, y + 28), 'A period-2 body (blue) sits above and below the main body and touches it at ONE point each, on no exact plane (cuts: wide, 0.5 wide, 0.06 wide; level cut at the touching height: one pixel). But: rings round the upright axis, and its BASILICA FAILS the close-cut screen (hair 36.7, limit 0.3). Not a candidate.', fill=(235, 190, 120), font=f3)
        y += 54; xs = pad
        for vn in ('a', 'b', 'd'):
            p = os.path.join(HU, 'h_ud55-view-%s.png' % vn)
            if os.path.exists(p):
                im.paste(Image.open(p).resize((330, 330), Image.LANCZOS), (xs, y))
            xs += 330 + pad
        sp = Image.open(os.path.join(HU, 'h_ud55-cuts.png')); sc = 520 / sp.height
        im.paste(sp.resize((int(sp.width * sc), 520), Image.LANCZOS), (xs, y))
        cc = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'out', 'me', 'r16', 'closecut-h_ud55.png')
        if os.path.exists(cc):
            q = Image.open(cc); q = q.crop((0, q.height // 2, q.width, q.height)); sc2 = 1000 / q.width
            im.paste(q.resize((1000, int(q.height * sc2)), Image.LANCZOS), (pad, y + 340))
            d.text((pad + 6, y + 344 + int(q.height * sc2)), 'Above: the BASILICA of h_ud55, cut 11.25 degrees from the flat plane, 0.2 / 0.04 / 0.008 wide: brushes of streaks. It fails the first screen.', fill=(235, 190, 120), font=f3)
    im.save(os.path.join(HERE, 'sheet.png')); print('wrote sheet.png', im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'tiles':
        tiles(sys.argv[2])
    else:
        compose()
