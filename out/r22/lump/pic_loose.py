"""Picture for the user: the two loose bodies of 'Along once, then one plane' (rabbit), and where one step puts them.
    python out/r22/lump/pic_loose.py   -> lump-loose.png"""
import sys, time, os, colorsys
import numpy as np
from PIL import Image, ImageDraw
import lumplib as L
M = L.M

c = L.RABBIT; STEPS = 120
PH = np.array([(244, 232, 200), (88, 178, 255), (255, 128, 60)], float)
A = np.array([0.038, -0.295, 0.0]); B = np.array([-0.626, 0.564, 0.0])          # under the loose bodies; middle of where they land
MID = (A + B) / 2; DIR = (B - A) / np.linalg.norm(B - A); HALF = np.linalg.norm(B - A) / 2
PW = 620; LW = 1.12; pad = 16; BG = (12, 14, 20)
SW, SH = 620, 620


def cut_img(ro, dim=1.0):
    img = np.zeros(ro['n'].shape + (3,), np.uint8); t = np.clip(ro['n'] / 40.0, 0, 1) ** 0.6
    img[..., 0] = (16 + 16 * t).astype(np.uint8); img[..., 1] = (20 + 26 * t).astype(np.uint8); img[..., 2] = (34 + 50 * t).astype(np.uint8)
    for k in range(3):
        img[ro['inside'] & (ro['phase'] == k)] = (PH[k] * dim).astype(np.uint8)
    return img


def to_px(s, z):
    return (s + LW) / (2 * LW) * (PW - 1), (LW - z) / (2 * LW) * (PW - 1)


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    r = L.rule('alongmem.c_wake1'); W = pad + PW + pad + SW + pad
    im = Image.new('RGB', (W, 1300), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), '"Along once, then one plane": the two bodies that hang loose', fill=(240, 240, 245), font=f_t)
    head = ('Each loose body is a place far above (or below) the flat page whose points the FIRST step throws straight down into one ordinary body of the rabbit, '
            'the blue one beside the meeting point. From the second step on the rule is one plane\'s, and those points simply stay with that body.')
    y = 60
    for ln in L.wrap(d, head, f_c, W - 2 * pad):
        d.text((pad, y), ln, fill=(170, 178, 192), font=f_c); y += 24
    y += 12
    d.text((pad, y), 'Cut straight down through both loose bodies', fill=(240, 222, 160), font=f_h)
    d.text((pad + PW + pad, y), 'The whole shape, seen from the side', fill=(240, 222, 160), font=f_h); y += 32
    # the cut
    s, z = np.meshgrid(np.linspace(-LW, LW, PW), np.linspace(LW, -LW, PW))
    P = [MID[i] + s * DIR[i] + (z if i == 2 else 0) for i in range(3)]
    ro = L.route(r, P[0], P[1], P[2], c, STEPS); im.paste(Image.fromarray(cut_img(ro, 0.72)), (pad, y))
    _, zy = to_px(0, 0); d.line([pad, y + zy, pad + PW, y + zy], fill=(200, 205, 215), width=1); d.text((pad + 8, y + zy + 6), 'the flat page, seen edge-on', fill=(200, 205, 215), font=f_s)
    # test points: before and after one step
    offs = [(0.0, 0.0), (0.07, 0.0), (-0.07, 0.0), (0.0, 0.13), (0.0, -0.13), (0.05, 0.22)]
    k = 0
    for sg in (1, -1):
        pts = np.array([A + o[0] * DIR + np.array([0, 0, sg * (0.649 + o[1])]) for o in offs]).T          # (3, 6)
        n = pts.shape[1]; inside = M.stay(r, pts[0], pts[1], pts[2], *c, STEPS) >= STEPS
        o = r.step(pts[0].copy(), pts[1].copy(), pts[2].copy(), tuple(r.init(n)), 0, np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
        q = np.stack([o[0] + c[0], o[1] + c[1], o[2] + c[2]])
        print('test points', 'above' if sg > 0 else 'below', 'inside:', inside.tolist()); print('   land at', np.round(q.T, 3).tolist())
        a0 = to_px(-HALF, sg * 0.649); b0 = to_px((q.mean(1) - MID) @ DIR, q[2].mean())
        d.line([pad + a0[0], y + a0[1], pad + b0[0], y + b0[1]], fill=(255, 255, 255), width=2)
        ux, uy = b0[0] - a0[0], b0[1] - a0[1]; nn = np.hypot(ux, uy); ux, uy = ux / nn, uy / nn
        d.polygon([(pad + b0[0], y + b0[1]), (pad + b0[0] - 16 * ux + 7 * uy, y + b0[1] - 16 * uy - 7 * ux), (pad + b0[0] - 16 * ux - 7 * uy, y + b0[1] - 16 * uy + 7 * ux)], fill=(255, 255, 255))
        for i in range(n):
            if not inside[i]:
                continue
            col = tuple(int(255 * t) for t in colorsys.hsv_to_rgb((k * 0.137) % 1.0, 0.9, 1.0)); k += 1
            a = to_px((pts[:, i] - MID) @ DIR, pts[2, i]); b = to_px((q[:, i] - MID) @ DIR, q[2, i])
            d.ellipse([pad + a[0] - 6, y + a[1] - 6, pad + a[0] + 6, y + a[1] + 6], fill=col, outline=(0, 0, 0))
            d.ellipse([pad + b[0] - 6, y + b[1] - 6, pad + b[0] + 6, y + b[1] + 6], fill=col, outline=(255, 255, 255))
    la = to_px(-HALF, 0.649); d.text((pad + la[0] - 45, y + la[1] - 88), 'a loose body', fill=(235, 235, 240), font=f_s)
    lc = to_px(-HALF, -0.649); d.text((pad + la[0] - 45, y + lc[1] + 70), 'its twin', fill=(235, 235, 240), font=f_s)
    lb = to_px(HALF, 0.0); d.text((pad + lb[0] - 40, y + lb[1] - 118), 'where one step', fill=(235, 235, 240), font=f_s); d.text((pad + lb[0] - 40, y + lb[1] - 100), 'puts its points', fill=(235, 235, 240), font=f_s)
    print('cut %.0f s' % (time.time() - t0)); sys.stdout.flush()
    # the solid from the side, height upright
    hw = 1.5; nd = 260; eye = (0.55, -1.0, 0.16)
    dep, px, (e1, e2, e3) = L.solid2(r, c, SW, SH, nd, 40, eye, half_w=hw); base = M.shade_solid(dep, px).astype(float); hit = np.isfinite(dep)
    us = np.linspace(-hw, hw, SW); vs = np.linspace(hw * SH / SW, -hw * SH / SW, SH); U, V = np.meshgrid(us, vs); dd = np.where(hit, dep, 0.0) + 0.5 * (2 * hw / (nd - 1))
    Q = [U * e1[i] + V * e2[i] + dd * e3[i] for i in range(3)]
    ro = L.route(r, Q[0][hit], Q[1][hit], Q[2][hit], c, STEPS); ph = np.full(dep.shape, -1); ph[hit] = np.where(ro['inside'], ro['phase'], -1)
    v = base[..., 0] / 238.0; img = np.zeros(dep.shape + (3,), np.uint8); img[...] = BG
    for kk in range(3):
        m = hit & (ph == kk); img[m] = np.clip(v[m, None] * PH[kk][None] * 1.05, 0, 255).astype(np.uint8)
    m = hit & (ph < 0); img[m] = np.clip(v[m, None] * np.array([170.0, 170, 170])[None], 0, 255).astype(np.uint8)
    ox = pad + PW + pad; im.paste(Image.fromarray(img), (ox, y))
    for sg in (1, -1):
        w = np.array([0.038, -0.295, sg * 0.649]); qx = (w @ e1 + hw) / (2 * hw) * (SW - 1); qy = (hw * SH / SW - w @ e2) / (2 * hw * SH / SW) * (SH - 1)
        d.ellipse([ox + qx - 62, y + qy - 86, ox + qx + 62, y + qy + 86], outline=(255, 255, 255), width=2)
    d.text((ox + 8, y + SH - 44), 'white rings: the two loose bodies. They stand in front of the rest,', fill=(235, 235, 240), font=f_s)
    d.text((ox + 8, y + SH - 24), 'not on it: the cut on the left shows the empty space between.', fill=(235, 235, 240), font=f_s)
    y += PW + 10
    cap = ('Coloured dots on the left: test points inside a loose body, and the same points one step later (white rim). All of them land in the blue body, close to the flat page. '
           'In the flat picture exactly two places jump onto any one spot. The first step of "along" folds space over itself, so up to eight places can jump onto one spot: '
           'two in the flat page and up to six away from it. A loose body is such an extra place. It was never one of the chain of bodies that touch each other in the flat page, so nothing joins it to them.')
    for ln in L.wrap(d, cap, f_c, W - 2 * pad):
        d.text((pad, y), ln, fill=(215, 218, 226), font=f_c); y += 24
    im = im.crop((0, 0, W, y + 14)); out = os.path.join(L.HERE, 'lump-loose.png'); im.save(out); print(out, im.size, '%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
