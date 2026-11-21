"""Working picture (not for the user): cuts coloured by which cycle point the orbit sits on (the body it belongs to).
    python out/r22/lump/diag1.py [cset]   -> diag1-<cset>.png"""
import sys, time, os
import numpy as np
from PIL import Image, ImageDraw
import lumplib as L
M = L.M

cs = sys.argv[1] if len(sys.argv) > 1 else 'rabbit'; c = L.CSETS[cs]
fc = L.flat_cycle(c); per = len(fc) if fc else 1
STEPS = 120 if per in (1, 2, 3) else 120
RULES = ['along', 'oneplane', 'alongmem.c_wake1', 'lathe']
ANG = [0.0, 11.25, 22.5, 45.0, 90.0]; XS = [-0.28, 0.04]
W, H = 300, 217; pad = 8
PH = np.array([(240, 226, 190), (95, 190, 255), (255, 130, 70), (150, 230, 140)], float)


def colour(ro):
    img = np.zeros(ro['n'].shape + (3,), np.uint8); t = np.clip(ro['n'] / STEPS, 0, 1) ** 0.6
    img[..., 0] = (14 + 30 * t).astype(np.uint8); img[..., 1] = (18 + 50 * t).astype(np.uint8); img[..., 2] = (30 + 100 * t).astype(np.uint8)
    ins = ro['inside']; ph = ro['phase']
    dim = 1.0 - 0.45 * np.clip(ro['land'] / 12.0, 0, 1)                          # darker = lands on the page later
    for k in range(4):
        m = ins & (ph == k); img[m] = (PH[k][None] * dim[m][:, None]).astype(np.uint8)
    img[ins & (ph < 0)] = (200, 60, 200)
    return img


t0 = time.time()
Wt = pad + len(ANG) * (W + pad) + len(XS) * (H + pad); Ht = 40 + len(RULES) * (H + 30)
im = Image.new('RGB', (Wt, Ht), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(15)
d.text((pad, 8), '%s: cuts coloured by the cycle point the orbit sits on after %d steps; darker = comes down to the page later' % (cs, STEPS), fill=(240, 240, 245), font=M.font(18))
for i, rn in enumerate(RULES):
    r = L.rule(rn); y0 = 40 + i * (H + 30); x0 = pad
    d.text((pad, y0), rn, fill=(235, 220, 170), font=f)
    for a in ANG:
        u, s = np.meshgrid(np.linspace(-1.8, 1.8, W), np.linspace(1.3, -1.3, H)); ar = np.radians(a)
        ro = L.route(r, u, s * np.cos(ar), s * np.sin(ar), c, STEPS)
        im.paste(Image.fromarray(colour(ro)), (x0, y0 + 20)); d.text((x0 + 4, y0 + 22), 'page at %g deg' % a, fill=(170, 178, 192), font=f); x0 += W + pad
    for xx in XS:
        p, q = np.meshgrid(np.linspace(-1.3, 1.3, H), np.linspace(1.3, -1.3, H))
        ro = L.route(r, np.full_like(p, xx), p, q, c, STEPS)
        im.paste(Image.fromarray(colour(ro)), (x0, y0 + 20)); d.text((x0 + 4, y0 + 22), 'across x = %g' % xx, fill=(170, 178, 192), font=f); x0 += H + pad
    print(rn, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = os.path.join(L.HERE, 'diag1-%s.png' % cs); im.save(out); print(out, im.size)
