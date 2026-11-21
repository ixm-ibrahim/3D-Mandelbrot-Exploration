"""Round 27, measure, parts 1 and 2: how near is the object's flat cut to the true flat pictures of z^2 + c?

    python out/r27/measure/fit.py search      best setting of the two dials (k2 = width of the middle ball, t) for each c -> fit.log, fit-table.npz
    python out/r27/measure/fit.py pictures    fit-c-1.png, fit-c-075.png, fit-sheet.png, fit-curve.png (reads fit-table.npz)

The measure is round 25's: the share of the true area that gets the wrong verdict = area(object xor true) / area(true).
The object's flat cut is the 'line' object (round 25, re-measured in check.py), drawn here from its list of circles.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K
M = K.M

CS = [0.25, 0.0, -0.25, -0.5, -0.7, -0.75, -0.8, -0.9, -1.0, -1.1, -1.2, -1.25, -1.3, -1.4]
TS = np.unique(np.round(np.concatenate([np.linspace(1.0, 2.0, 51), np.linspace(2.0, 4.0, 21), [5, 6, 8, 12, 20, 50]]), 4))
K2S = np.round(np.linspace(0.6, 2.3, 171), 4)
TB = (-2.2, 2.2, -1.5, 1.5); TPX = 0.002                     # the box and the pixel of the stored true pictures
UB = (-4.4, 4.4, -1.6, 1.6); UPX = 0.004                     # the box and the pixel of the object drawn with k2 = 1


def steps_for(c):
    return 4000 if min(abs(c - 0.25), abs(c + 0.75), abs(c + 1.25)) < 1e-9 else (3000 if c <= -1.3 else 800)


def truth(c):
    """The true flat picture of a c on the x-axis, as a boolean mask over TB (one quarter computed, then mirrored)."""
    f = os.path.join(HERE, 'cache', 'true_%+.4f.npy' % c)
    if os.path.exists(f):
        return np.load(f)
    nx = int(round((TB[1] - TB[0]) / TPX)); ny = int(round((TB[3] - TB[2]) / TPX))
    xs = TB[0] + (np.arange(nx) + 0.5) * TPX; ys = TB[3] - (np.arange(ny) + 0.5) * TPX
    u, s = np.meshgrid(xs[nx // 2:], ys[:ny // 2]); q = K.julia(u, s, c, 0.0, steps_for(c))
    top = np.concatenate([q[:, ::-1], q], 1); full = np.concatenate([top, top[::-1]], 0)
    os.makedirs(os.path.dirname(f), exist_ok=True); np.save(f, full)
    return full


def obj_discs(t, k2=1.0, r_min=0.0012, c0=(0.0, 0.0, 1.0)):
    g = K.Grid('line'); reps, _ = K.build(g, K.recipe_gens(2 * t), 2 * t, rho_min=r_min / 6)
    B = K.picture(reps, g, 2 * t, c0=c0, k2=k2, r_min=r_min)
    return B[:, [0, 1, 3]]


def obj_mask_unit(t):
    w = int(round((UB[1] - UB[0]) / UPX)); h = int(round((UB[3] - UB[2]) / UPX))
    return K.discs_cov(obj_discs(t), w, h, UB, ss=1) > 0.5


def sample_truth(T, k2):
    """The true picture read at the points k2 * (unit grid)."""
    w = int(round((UB[1] - UB[0]) / UPX)); h = int(round((UB[3] - UB[2]) / UPX))
    x = k2 * (UB[0] + (np.arange(w) + 0.5) * UPX); y = k2 * (UB[3] - (np.arange(h) + 0.5) * UPX)
    j = np.floor((x - TB[0]) / TPX).astype(int); i = np.floor((TB[3] - y) / TPX).astype(int)
    okj = (j >= 0) & (j < T.shape[1]); oki = (i >= 0) & (i < T.shape[0])
    out = np.zeros((h, w), bool); out[np.ix_(oki, okj)] = T[np.ix_(i[oki], j[okj])]
    return out


def search():
    log = open(os.path.join(HERE, 'fit.log'), 'w')

    def say(s):
        print(s); log.write(s + '\n'); log.flush()
    t0 = time.time(); Ts = {c: truth(c) for c in CS}; say('true pictures ready, %.0f s' % (time.time() - t0))
    err = np.full((len(CS), len(TS), len(K2S)), np.inf)
    for a, t in enumerate(TS):
        if t <= 1.0:
            continue                                              # at t = 1 the chain never ends (it runs out of every box)
        O = obj_mask_unit(float(t))
        for b, k2 in enumerate(K2S):
            for ci, c in enumerate(CS):
                Tk = sample_truth(Ts[c], k2); n = Tk.sum()
                if n:
                    err[ci, a, b] = (O ^ Tk).sum() / n
        if a % 10 == 0:
            print('   t = %.3f done, %.0f s' % (t, time.time() - t0)); sys.stdout.flush()
    np.savez(os.path.join(HERE, 'fit-table.npz'), err=err, cs=np.array(CS), ts=TS, k2s=K2S)
    say('share of the true area with the wrong verdict, best over the two dials (t from %.2f to %.0f, k2 from %.2f to %.2f)' % (TS[1], TS[-1], K2S[0], K2S[-1]))
    say('   c        best      at k2     t      | best with t <= 4 (k2, t)        | at the lab setting k2 = 1.05, t = 1.40')
    i14 = int(np.argmin(np.abs(TS - 1.4))); i105 = int(np.argmin(np.abs(K2S - 1.05))); t4 = TS <= 4.0
    for ci, c in enumerate(CS):
        e = err[ci]; a, b = np.unravel_index(np.argmin(e), e.shape); e4 = e[t4]; a4, b4 = np.unravel_index(np.argmin(e4), e4.shape)
        say('   %+.2f   %5.1f%%   %.2f   %5.2f   | %5.1f%%  (%.2f, %.2f)          | %5.1f%%' % (c, 100 * e[a, b], K2S[b], TS[a], 100 * e4[a4, b4], K2S[b4], TS[t4][a4], 100 * e[i14, i105]))
    say('done, %.0f s' % (time.time() - t0)); log.close()


def search2():
    """Two extra searches: (a) finer in c round the best fit; (b) c below -1 with a smaller middle ball allowed."""
    global UB
    log = open(os.path.join(HERE, 'fit2.log'), 'w'); res = {}

    def say(s):
        print(s); log.write(s + '\n'); log.flush()

    def run(cs, ts, k2s, tag):
        say(tag); Ts = {c: truth(c) for c in cs}; err = np.full((len(cs), len(ts), len(k2s)), np.inf)
        for a, t in enumerate(ts):
            O = obj_mask_unit(float(t))
            for b, k2 in enumerate(k2s):
                for ci, c in enumerate(cs):
                    Tk = sample_truth(Ts[c], k2); n = Tk.sum()
                    if n:
                        err[ci, a, b] = (O ^ Tk).sum() / n
        for ci, c in enumerate(cs):
            e = err[ci]; a, b = np.unravel_index(np.argmin(e), e.shape); res[float(c)] = (float(e[a, b]), float(k2s[b]), float(ts[a]))
            say('   c = %+.3f: best %5.1f%% at k2 = %.3f, t = %.3f   (true area in the box %.4f)' % (c, 100 * e[a, b], k2s[b], ts[a], Ts[c].mean() * (TB[1] - TB[0]) * (TB[3] - TB[2])))
    run([-0.72, -0.75, -0.78, -0.80, -0.82, -0.84, -0.86, -0.88, -0.90, -0.95], np.round(np.arange(1.20, 1.521, 0.02), 3), np.round(np.arange(0.94, 1.161, 0.01), 3), 'finer in c round the best fit')
    UB = (-7.0, 7.0, -3.0, 3.0)
    run([-1.1, -1.2, -1.25, -1.3, -1.35, -1.4], np.round(np.concatenate([np.arange(1.04, 1.5, 0.04), np.arange(1.5, 3.01, 0.25)]), 3), np.round(np.arange(0.30, 1.001, 0.02), 3), 'c below -1, middle ball from 0.3 to 1 wide')
    import json
    json.dump({'%.3f' % k: v for k, v in res.items()}, open(os.path.join(HERE, 'fit2.json'), 'w')); log.close()


def best(c, tmax=1e9):
    f2 = os.path.join(HERE, 'fit2.json')
    if os.path.exists(f2):
        import json
        r = json.load(open(f2))
        if '%.3f' % c in r:
            return tuple(r['%.3f' % c])
    z = np.load(os.path.join(HERE, 'fit-table.npz')); ci = int(np.argmin(np.abs(z['cs'] - c))); e = z['err'][ci].copy(); e[z['ts'] > tmax] = np.inf
    a, b = np.unravel_index(np.argmin(e), e.shape)
    return float(e[a, b]), float(z['k2s'][b]), float(z['ts'][a])


def panel(c, k2, t, w, h, box, r_min=None):
    px = (box[1] - box[0]) / w; d = obj_discs(t, k2, r_min or px / 3)
    co = K.discs_cov(d, w, h, box, ss=3); ct = K.julia_cov(c, 0.0, w, h, box, steps_for(c), ss=3)
    wrong = float(np.abs(co - ct).sum() / ct.sum())
    return K.overlay(co, ct), wrong


def legend(d, x, y, f):
    for col, txt in (((226, 220, 200), 'in both'), ((236, 138, 52), 'only in the balls object'), ((72, 146, 240), 'only in the true flat picture')):
        d.rectangle([x, y + 3, x + 16, y + 17], fill=col); d.text((x + 24, y), txt, fill=(225, 228, 235), font=f); x += 36 + int(d.textlength(txt, font=f))
    d.text((x, y), 'white line: the rim of the true flat picture', fill=(225, 228, 235), font=f)


def one(c, name, title, note):
    e, k2, t = best(c, 4.0); w, h = 1500, 1000; box = (-1.8, 1.8, -1.2, 1.2)
    img, wrong = panel(c, k2, t, w, h, box)
    im = Image.new('RGB', (w, h + 96), (12, 14, 20)); d = ImageDraw.Draw(im); im.paste(Image.fromarray(img), (0, 62))
    d.text((14, 8), title, fill=(240, 240, 245), font=K.font(26)); legend(d, 14, 40, K.font(15))
    d.text((14, h + 68), note % {'wrong': 100 * wrong, 'k2': k2, 't': t}, fill=(200, 205, 215), font=K.font(17))
    im.save(os.path.join(HERE, name)); print('wrote', name, 'wrong %.1f%%' % (100 * wrong), 'k2 %.3f t %.3f' % (k2, t))
    return wrong, k2, t


def pictures():
    out = open(os.path.join(HERE, 'fit-pictures.log'), 'w')
    r = one(-1.0, 'fit-c-1.png', 'True flat picture of c = -1 against the flat cut of the balls object, at its best setting',
            'Of every 100 parts of the true area, %(wrong).0f get the wrong verdict (middle ball %(k2).2f wide, t = %(t).2f).')
    out.write('c = -1: wrong %.4f at k2 = %.3f, t = %.3f (fine picture, 3 x 3 samples a pixel)\n' % r)
    r = one(-0.75, 'fit-c-075.png', 'True flat picture of c = -0.75 against the flat cut of the balls object, at its best setting',
            'Of every 100 parts of the true area, %(wrong).0f get the wrong verdict (middle ball %(k2).2f wide, t = %(t).2f).')
    out.write('c = -0.75: wrong %.4f at k2 = %.3f, t = %.3f\n' % r)
    r = one(-0.84, 'fit-c-084.png', 'The true flat picture that the balls object comes nearest to: c = -0.84',
            'Of every 100 parts of the true area, %(wrong).0f get the wrong verdict (middle ball %(k2).2f wide, t = %(t).2f).')
    out.write('c = -0.84: wrong %.4f at k2 = %.3f, t = %.3f\n' % r)
    # the sheet: eight c on the x-axis, each at the best setting with t <= 4
    cs = [0.25, 0.0, -0.5, -0.75, -0.84, -1.0, -1.25, -1.4]; w, h = 600, 400; box = (-1.95, 1.95, -1.3, 1.3); pad = 8
    W = pad + 4 * (w + pad); H = 74 + 2 * (h + 30)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'True flat pictures of eight c on the x-axis, each against the balls object at its best setting for that c', fill=(240, 240, 245), font=K.font(22))
    legend(d, pad, 40, K.font(15))
    for n, c in enumerate(cs):
        e, k2, t = best(c, 4.0); img, wrong = panel(c, k2, t, w, h, box)
        x = pad + (n % 4) * (w + pad); y = 74 + (n // 4) * (h + 30)
        im.paste(Image.fromarray(img), (x, y + 24))
        d.text((x + 2, y), 'c = %g:  %.0f of 100 parts wrong' % (c, 100 * wrong), fill=(235, 220, 170), font=K.font(18))
        out.write('sheet c = %+.2f: wrong %.4f at k2 = %.3f, t = %.3f\n' % (c, wrong, k2, t)); print('sheet', c, wrong)
    im.save(os.path.join(HERE, 'fit-sheet.png')); out.close(); print('wrote fit-sheet.png')


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'search'
    {'search': search, 'search2': search2, 'pictures': pictures}[a]()
