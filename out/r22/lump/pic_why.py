"""Picture for the user: what happens to test points above the place where three bodies of the rabbit meet.
    python out/r22/lump/pic_why.py   -> lump-why.png   (prints the trails it draws)

An orbit near the meeting point goes a third of the way round it at every step, so only every third step is drawn
(the point is then back on the same side) and the dots make a readable path."""
import sys, time, os
import numpy as np
from PIL import Image, ImageDraw
import lumplib as L
M = L.M

c = L.RABBIT; cc = complex(*c[:2]); al = (1 - np.sqrt(1 - 4 * cc)) / 2; PIN = np.array([al.real, al.imag, 0.0])
STEPS = 120; NT = 30
PH = np.array([(244, 232, 200), (88, 178, 255), (255, 128, 60)], float)
COLS = [('oneplane', 'Sphere inversions, one plane',
         'Both test points are lifted a little at every step, wherever they are. They climb away and leave the shape. So the space over the meeting point stays empty, and the three bodies stay three bodies that touch at one point.'),
        ('along', 'Turning plane, along',
         'Close to the flat page a point is lifted, as on the left. Higher up it is brought DOWN instead: there the page it is squared in tips toward it. Both test points end at the same small height (dashed line), hover there, then slide sideways into a body and stay. So the space over the meeting point is filled in, and the bodies are joined.')]
STARTS = [(0.0, 0.0, 0.25), (0.012, -0.008, 0.035)]             # offsets from the meeting point
TCOL = [(255, 255, 255), (120, 255, 140)]
PW = 620; pad = 16; BG = (12, 14, 20)
Y0, Y1, Z0, Z1 = 0.13, 0.83, -0.12, 0.58                        # side view window (y across, height up), square


def cut_img(ro):
    img = np.zeros(ro['n'].shape + (3,), np.uint8); t = np.clip(ro['n'] / 40.0, 0, 1) ** 0.6
    img[..., 0] = (16 + 16 * t).astype(np.uint8); img[..., 1] = (20 + 26 * t).astype(np.uint8); img[..., 2] = (34 + 50 * t).astype(np.uint8)
    for k in range(3):
        img[ro['inside'] & (ro['phase'] == k)] = (PH[k] * 0.6).astype(np.uint8)    # dimmed, so that the trails stand out
    return img


def trail(r, p, n):
    x, y, z = (np.array([q[i] for q in p], float) for i in range(3)); m = x.size; st = tuple(r.init(m)); out = [np.stack([x, y, z])]
    cx, cy, cz = (np.full(m, t) for t in c)
    for k in range(n):
        o = r.step(x, y, z, st, k, cx, cy, cz); st = tuple(o[3]); x, y, z = o[0] + cx, o[1] + cy, o[2] + cz; out.append(np.stack([x, y, z]))
    return np.stack(out)


def to_px(yv, zv):
    return (yv - Y0) / (Y1 - Y0) * (PW - 1), (Z1 - zv) / (Z1 - Z0) * (PW - 1)


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    W = pad + 2 * (PW + pad); im = Image.new('RGB', (W, 1200), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Why the rabbit\'s bodies run together under "along"', fill=(240, 240, 245), font=f_t)
    head = ('Three bodies of the rabbit meet at one point of the flat page (white ring). Two test points are put above it and followed. '
            'A big dot is the start; each small dot is the same test point three steps later. Same colour = same test point, left and right. '
            'Both pictures look from the side: the level line is the flat page seen edge-on, the brown and pale areas are two of the bodies, cut through.')
    y = 60
    for ln in L.wrap(d, head, f_c, W - 2 * pad):
        d.text((pad, y), ln, fill=(170, 178, 192), font=f_c); y += 24
    y += 12; ybot = y
    for j, (name, title, cap) in enumerate(COLS):
        r = L.rule(name); ox = pad + j * (PW + pad); yy = y
        d.text((ox, yy), title, fill=(240, 222, 160), font=f_h); yy += 32
        T = trail(r, [PIN + np.array(s) for s in STARTS], NT)
        p, q = np.meshgrid(np.linspace(Y0, Y1, PW), np.linspace(Z1, Z0, PW))
        ro = L.route(r, np.full_like(p, PIN[0]), p, q, c, STEPS); im.paste(Image.fromarray(cut_img(ro)), (ox, yy))
        _, zy = to_px(0, 0.0); d.line([ox, yy + zy, ox + PW, yy + zy], fill=(200, 205, 215), width=1)
        d.text((ox + 8, yy + zy + 6), 'the flat page', fill=(200, 205, 215), font=f_s)
        px, _ = to_px(PIN[1], 0); d.ellipse([ox + px - 10, yy + zy - 10, ox + px + 10, yy + zy + 10], outline=(255, 255, 255), width=2)
        if name == 'along':
            _, hy = to_px(0, 0.0754)
            for xx in range(0, PW, 14):
                d.line([ox + xx, yy + hy, ox + xx + 7, yy + hy], fill=(255, 255, 255), width=1)
        for i in range(len(STARTS)):
            ks = list(range(0, NT + 1, 3)); ok = [k for k in ks if np.isfinite(T[k, :, i]).all() and np.abs(T[k, :, i]).max() < 6]
            pts = [to_px(T[k, 1, i], T[k, 2, i]) for k in ok]
            print(name, 'test point', i, 'every third step (y, height):', ' '.join('(%.2f %.3f)' % (T[k, 1, i], T[k, 2, i]) for k in ok))
            ins = lambda pt: 0 <= pt[0] <= PW and 0 <= pt[1] <= PW
            for a, b in zip(pts[:-1], pts[1:]):
                if ins(a) and ins(b):
                    d.line([ox + a[0], yy + a[1], ox + b[0], yy + b[1]], fill=TCOL[i], width=2)
                elif ins(a):                                   # next dot is outside the window: a stub and an arrow head at the edge
                    t = 1.0
                    while t > 0.02 and not ins((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))):
                        t *= 0.9
                    e = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])); d.line([ox + a[0], yy + a[1], ox + e[0], yy + e[1]], fill=TCOL[i], width=2)
                    ux, uy = b[0] - a[0], b[1] - a[1]; nn = max(np.hypot(ux, uy), 1e-9); ux, uy = ux / nn, uy / nn      # arrow head: it goes on outside the picture
                    d.polygon([(ox + e[0], yy + e[1]), (ox + e[0] - 15 * ux + 7 * uy, yy + e[1] - 15 * uy - 7 * ux), (ox + e[0] - 15 * ux - 7 * uy, yy + e[1] - 15 * uy + 7 * ux)], fill=TCOL[i])
                    pts = pts[:pts.index(a) + 1]; break        # what it does after it has left the window is not drawn
            for k, pt in enumerate(pts):
                if ins(pt):
                    rr = 8 if k == 0 else 4
                    d.ellipse([ox + pt[0] - rr, yy + pt[1] - rr, ox + pt[0] + rr, yy + pt[1] + rr], fill=TCOL[i], outline=(0, 0, 0))
        if name == 'oneplane':
            d.text((ox + PW - 250, yy + 10), 'both climb out of the picture', fill=(235, 235, 240), font=f_s)
        else:
            _, hy = to_px(0, 0.0754); d.text((ox + 8, yy + hy - 24), 'both come to this height and hover', fill=(235, 235, 240), font=f_s)
        yy += PW + 10
        for ln in L.wrap(d, cap, f_c, PW):
            d.text((ox, yy), ln, fill=(215, 218, 226), font=f_c); yy += 24
        ybot = max(ybot, yy); print(name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, ybot + 14)); out = os.path.join(L.HERE, 'lump-why.png'); im.save(out); print(out, im.size)


if __name__ == '__main__':
    main()
