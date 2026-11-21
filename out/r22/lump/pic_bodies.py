"""Picture for the user: the rabbit under three rules, every point coloured by the spot its orbit ends on.
    python out/r22/lump/pic_bodies.py [cset]   -> lump-bodies.png  (cset other than rabbit: working picture bodies-<cset>.png)"""
import sys, time, os
import numpy as np
from PIL import Image, ImageDraw
import lumplib as L
M = L.M

cs = sys.argv[1] if len(sys.argv) > 1 else 'rabbit'; c = L.CSETS[cs]; fc = L.flat_cycle(c); per = len(fc)
STEPS = 120; XCUT = -0.276 if cs == 'rabbit' else 0.0
ROWS = [('along', 'Turning plane, along',
         'The same bodies as in the row below, grown so fat off the flat page that they press against each other along whole walls. A wall has no thickness, so the shape looks like one lump.'),
        ('oneplane', 'Sphere inversions, one plane',
         'Every body stays thin enough to stand free. Bodies touch only at single points, as in the flat picture.'),
        ('alongmem.c_wake1', 'Along once, then one plane',
         'Separate bodies again, fatter than one plane\'s. But two bodies touch nothing: they hang loose, one above and one below the flat page. The one above is inside the white ring; its twin is hidden behind the shape.')]
# colour of a body = the spot its points are on after 120 steps (flat_cycle order for the rabbit: c, c^2+c, 0)
PH = np.array([(244, 232, 200), (88, 178, 255), (255, 128, 60)], float) if per == 3 else np.array([(255, 128, 60), (88, 178, 255)], float)
CW, CH = 440, 330; AW = 330; SW, SH = 470, 330; pad = 14; BG = (12, 14, 20)


def cut_img(ro):
    img = np.zeros(ro['n'].shape + (3,), np.uint8); t = np.clip(ro['n'] / 40.0, 0, 1) ** 0.6
    img[..., 0] = (16 + 16 * t).astype(np.uint8); img[..., 1] = (20 + 26 * t).astype(np.uint8); img[..., 2] = (34 + 50 * t).astype(np.uint8)
    for k in range(per):
        img[ro['inside'] & (ro['phase'] == k)] = PH[k].astype(np.uint8)
    img[ro['inside'] & (ro['phase'] < 0)] = (150, 150, 150)
    return img


def solid_img(r, cam=(0.45, 0.5, 1.0), half_w=1.5, nd=280):
    dep, px = M.solid(r, c, SW, SH, nd, 40, half_w=half_w, cam=cam); base = M.shade_solid(dep, px).astype(float)
    hit = np.isfinite(dep); e1, e2, e3 = M.frame(cam)
    us = np.linspace(-half_w, half_w, SW); vs = np.linspace(half_w * SH / SW, -half_w * SH / SW, SH); U, V = np.meshgrid(us, vs)
    d = np.where(hit, dep, 0.0) + 0.5 * (2 * half_w / (nd - 1))
    P = [U * e1[i] + V * e2[i] + d * e3[i] for i in range(3)]
    ro = L.route(r, P[0][hit], P[1][hit], P[2][hit], c, STEPS); ph = np.full(dep.shape, -1); ph[hit] = np.where(ro['inside'], ro['phase'], -1)
    v = base[..., 0] / 238.0; img = np.zeros(dep.shape + (3,), np.uint8); img[...] = BG
    for k in range(per):
        m = hit & (ph == k); img[m] = np.clip(v[m, None] * PH[k][None] * 1.05, 0, 255).astype(np.uint8)
    m = hit & (ph < 0); img[m] = np.clip(v[m, None] * np.array([170.0, 170, 170])[None], 0, 255).astype(np.uint8)
    return img, (e1, e2, e3, half_w)


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    W = pad + CW + pad + AW + pad + SW + pad; rowh = 30 + 22 + CH + 8 + 48 + 30; H = 190 + len(ROWS) * rowh
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Where do the points of the rabbit\'s lump go?  All to the same three spots in the flat page.', fill=(240, 240, 245), font=f_t)
    lines = ['Every point of each shape was followed for hundreds of steps. With all three rules, every orbit that stays ends up hopping round the same three spots of the',
             'flat picture (white dots). Nothing off the flat page catches an orbit. So the lump is not hiding a second kind of thing: it is the same bodies, differently fat.',
             'Colour = which of the three spots the orbit is on after 120 steps. One body has one colour all through; bodies that touch have different colours.']
    for i, s in enumerate(lines):
        d.text((pad, 60 + 24 * i, ), s, fill=(170, 178, 192), font=f_c)
    y = 146
    xs = [pad, pad + CW + pad, pad + CW + pad + AW + pad]
    for name, head, cap in ROWS:
        r = L.rule(name)
        d.text((pad, y), head, fill=(240, 222, 160), font=f_h); y += 30
        d.text((xs[0], y), 'Cut along the flat page (the flat picture itself)', fill=(150, 160, 175), font=f_s)
        d.text((xs[1], y), 'Cut straight across, through the meeting point', fill=(150, 160, 175), font=f_s)
        d.text((xs[2], y), 'The whole shape (rough blocks)', fill=(150, 160, 175), font=f_s); y += 22
        # flat page
        u, s = np.meshgrid(np.linspace(-1.75, 1.75, CW), np.linspace(1.3125, -1.3125, CH))
        ro = L.route(r, u, s, np.zeros_like(u), c, STEPS); im.paste(Image.fromarray(cut_img(ro)), (xs[0], y))
        for w in fc:
            px, py = (w.real + 1.75) / 3.5 * (CW - 1), (1.3125 - w.imag) / 2.625 * (CH - 1)
            d.ellipse([xs[0] + px - 4, y + py - 4, xs[0] + px + 4, y + py + 4], fill=(255, 255, 255), outline=(0, 0, 0))
        if cs == 'rabbit':                                     # where the cut across goes, and the meeting point
            px = (XCUT + 1.75) / 3.5 * (CW - 1); d.line([xs[0] + px, y + 6, xs[0] + px, y + CH - 28], fill=(255, 255, 255), width=1)
            d.text((xs[0] + px + 5, y + 6), 'the cut across', fill=(220, 220, 228), font=f_s)
        # across
        LA = 1.1; p, q = np.meshgrid(np.linspace(-LA, LA, AW), np.linspace(LA, -LA, CH))
        ro = L.route(r, np.full_like(p, XCUT), p, q, c, STEPS); im.paste(Image.fromarray(cut_img(ro)), (xs[1], y))
        d.line([xs[1], y + CH // 2, xs[1] + 22, y + CH // 2], fill=(190, 198, 210), width=1); d.line([xs[1] + AW - 22, y + CH // 2, xs[1] + AW, y + CH // 2], fill=(190, 198, 210), width=1)
        d.text((xs[1] + 6, y + CH - 22), 'level line = the flat page, seen edge-on', fill=(150, 160, 175), font=f_s)
        if cs == 'rabbit':
            px = (0.4797 + LA) / (2 * LA) * (AW - 1); py = CH / 2
            d.ellipse([xs[1] + px - 9, y + py - 9, xs[1] + px + 9, y + py + 9], outline=(255, 255, 255), width=2)
            d.text((xs[1] + 8, y + 8), 'white ring: three bodies meet here', fill=(235, 235, 240), font=f_s)
        # solid
        simg, (e1, e2, e3, hw) = solid_img(r); im.paste(Image.fromarray(simg), (xs[2], y))
        if name == 'alongmem.c_wake1' and cs == 'rabbit':
            for sg in (1,):
                v = np.array([0.038, -0.295, sg * 0.649]); px = (v @ e1 + hw) / (2 * hw) * (SW - 1); py = (hw * SH / SW - v @ e2) / (2 * hw * SH / SW) * (SH - 1)
                d.ellipse([xs[2] + px - 46, y + py - 46, xs[2] + px + 46, y + py + 46], outline=(255, 255, 255), width=2)
        y += CH + 8
        for ln in L.wrap(d, cap, f_c, W - 2 * pad):
            d.text((pad, y), ln, fill=(215, 218, 226), font=f_c); y += 24
        y += 30
        print(name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y - 10)); out = os.path.join(L.HERE, 'lump-bodies.png' if cs == 'rabbit' else 'bodies-%s.png' % cs); im.save(out); print(out, im.size)


if __name__ == '__main__':
    main()
