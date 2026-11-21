"""Round 27, measure: how near can the balls family come to the true rabbit's flat picture? (numbers for the five tests)

    python out/r27/measure/rabbitfit.py     -> rabbitfit.log, rabbitfit.png

A. The lab's object (chain of balls, t >= 1), any size, any turn, any t: best share of the true area with the wrong verdict.
B. The ring of three (t = 0.5, every second whole number), any size, any turn, its middle put on the rabbit's meeting point.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K
import family as F

RAB = (-0.122561, 0.744862); ALPHA = (-0.27633, 0.47980)
log = open(os.path.join(HERE, 'rabbitfit.log'), 'w')


def say(s):
    print(s); log.write(s + '\n'); log.flush()


TB = (-1.8, 1.8, -1.8, 1.8); n = 450; px = 3.6 / n
xs = TB[0] + (np.arange(n) + 0.5) * px; ys = TB[3] - (np.arange(n) + 0.5) * px; X, Y = np.meshgrid(xs, ys)
T = K.julia(X, Y, RAB[0], RAB[1], 600); area = T.sum()
say('true rabbit: area %.4f' % (area * px * px))


def sample(mask, box, ox, oy):
    """mask over box (x0, x1, y0, y1) read at the points (ox, oy); False outside the box."""
    h, w = mask.shape; j = np.floor((ox - box[0]) / (box[1] - box[0]) * w).astype(int); i = np.floor((box[3] - oy) / (box[3] - box[2]) * h).astype(int)
    ok = (j >= 0) & (j < w) & (i >= 0) & (i < h); out = np.zeros(ox.shape, bool); out[ok] = mask[i[ok], j[ok]]
    return out


t0 = time.time(); bestA = (9.0,)
UB = (-4.4, 4.4, -1.6, 1.6)
for t in (1.05, 1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0, 8.0):
    g = K.Grid('line'); reps, _ = K.build(g, K.recipe_gens(2 * t), 2 * t, rho_min=3e-4); B = K.picture(reps, g, 2 * t, k2=1.0, r_min=0.002)
    O = K.discs_cov(B[:, [0, 1, 3]], 2200, 800, UB, ss=1) > 0.5
    for th in range(0, 180, 4):
        c, s = np.cos(np.radians(th)), np.sin(np.radians(th)); rx, ry = c * X + s * Y, -s * X + c * Y
        for k2 in np.arange(0.5, 1.81, 0.05):
            e = (sample(O, UB, rx / k2, ry / k2) ^ T).sum() / area
            if e < bestA[0]:
                bestA = (e, t, th, k2)
say('A. chain of balls against the true rabbit: best %.1f%% of the true area wrong (t = %.2f, turned %d degrees, middle ball %.2f wide), %.0f s' % (100 * bestA[0], bestA[1], bestA[2], bestA[3], time.time() - t0))

t = 0.5; c0, k2r, centre = F.ring_frame(t); g = K.Grid('line', 2.0)
reps, _ = K.build(g, K.recipe_gens(2 * t), 2 * t, rho_min=2e-4); B = K.picture(reps, g, 2 * t, c0=c0, k2=k2r, r_min=0.0015)
RB = (centre[0] - 1.3, centre[0] + 1.3, centre[1] - 1.3, centre[1] + 1.3); R = K.discs_cov(B[:, [0, 1, 3]], 1300, 1300, RB, ss=1) > 0.5
bestB = (9.0,)
for th in range(0, 120, 3):
    c, s = np.cos(np.radians(th)), np.sin(np.radians(th)); rx, ry = c * (X - ALPHA[0]) + s * (Y - ALPHA[1]), -s * (X - ALPHA[0]) + c * (Y - ALPHA[1])
    for sc in np.arange(0.2, 1.21, 0.04):
        e = (sample(R, RB, centre[0] + rx / sc, centre[1] + ry / sc) ^ T).sum() / area
        if e < bestB[0]:
            bestB = (e, th, sc)
say('B. ring of three against the true rabbit: best %.1f%% of the true area wrong (turned %d degrees, size %.2f), %.0f s' % (100 * bestB[0], bestB[1], bestB[2], time.time() - t0))

# the picture: both best fits over the true rabbit
w = 620; pad = 10; im = Image.new('RGB', (pad + 2 * (w + pad), w + 96), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'The true rabbit against the two nearest members of the family of balls', fill=(240, 240, 245), font=K.font(22))
xs2 = TB[0] + (np.arange(w) + 0.5) * 3.6 / w; ys2 = TB[3] - (np.arange(w) + 0.5) * 3.6 / w; X2, Y2 = np.meshgrid(xs2, ys2); T2 = K.julia(X2, Y2, RAB[0], RAB[1], 600)
e, t, th, k2 = bestA; g = K.Grid('line'); reps, _ = K.build(g, K.recipe_gens(2 * t), 2 * t, rho_min=2e-4); B = K.picture(reps, g, 2 * t, k2=1.0, r_min=0.001)
O = K.discs_cov(B[:, [0, 1, 3]], 4400, 1600, UB, ss=1) > 0.5; c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
A2 = sample(O, UB, (c * X2 + s * Y2) / k2, (-s * X2 + c * Y2) / k2)
im.paste(Image.fromarray(K.overlay(A2.astype(float), T2.astype(float))), (pad, 64)); d.text((pad, 40), 'chain of balls, best fit: %.0f of 100 parts wrong' % (100 * e), fill=(235, 220, 170), font=K.font(16))
e, th, sc = bestB; c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
R2 = sample(R, RB, centre[0] + (c * (X2 - ALPHA[0]) + s * (Y2 - ALPHA[1])) / sc, centre[1] + (-s * (X2 - ALPHA[0]) + c * (Y2 - ALPHA[1])) / sc)
im.paste(Image.fromarray(K.overlay(R2.astype(float), T2.astype(float))), (pad + w + pad, 64)); d.text((pad + w + pad, 40), 'ring of three, best fit: %.0f of 100 parts wrong' % (100 * e), fill=(235, 220, 170), font=K.font(16))
d.text((pad, w + 70), 'Pale: in both. Orange: only in the balls picture. Blue: only in the true rabbit. White line: the rim of the true rabbit.', fill=(200, 205, 215), font=K.font(15))
im.save(os.path.join(HERE, 'rabbitfit.png')); say('wrote rabbitfit.png')
