"""Hunter task 4, second idea: a second 'real axis'. NOT a candidate for the lab as it stands (it is not
mirror-symmetric above / below: fails J7 by design; see report.md for why that cannot be mended).

Where a rule is the lathe about some line (DF = 2 t * identity on that line), the period-2 body is a ball touching
the main body at ONE point (all three eigenvalues reach -1 together). The quaternion square has that on the x-axis.
Rule h_string: the one-plane square P everywhere (so the cut z = 0 is the flat set, exactly), except in a cone round
the NEGATIVE z-axis, where it is the lathe about the z-axis, Lz(x, y, z) = (2 z x, 2 z y, z^2 - x^2 - y^2); between
30 and 50 degrees from that axis the two answers are blended on the sphere of directions (infinitely smooth; the two
answers are never opposite there). Then the whole z-axis follows z -> z^2 + s, and at c = (0, 0, -3/4), which is
straight below the flat plane, a period-2 ball should touch the main body at one point.
    python out/r17/hunter/hstring.py [N]
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R
P = R.get('oneplane')
B1, B2 = np.radians(30), np.radians(50)


def g(t):
    return np.where(t > 0, np.exp(-1.0 / np.maximum(t, 1e-12)), 0.0)


def h_string(x, y, z):
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); rr = np.maximum(r, 1e-300)
    beta = np.arccos(np.clip(-z / rr, -1, 1))                 # angle from the negative z-axis
    t = np.clip((beta - B1) / (B2 - B1), 0, 1)
    s = g(1 - t) / (g(t) + g(1 - t))                          # 1 inside 30 degrees, 0 beyond 50 degrees
    X1, Y1, Z1 = P(x, y, z)
    X2, Y2, Z2 = 2 * z * x, 2 * z * y, z * z - x * x - y * y
    X, Y, Z = (1 - s) * X1 + s * X2, (1 - s) * Y1 + s * Y2, (1 - s) * Z1 + s * Z2
    n = np.sqrt(X * X + Y * Y + Z * Z)
    k = np.where(n > 0, r2 / np.maximum(n, 1e-300), 0.0)
    return X * k, Y * k, Z * k


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
    OUT = os.path.join(HERE, 'hunt'); os.makedirs(OUT, exist_ok=True); t0 = time.time(); res = {}
    F = h_string
    rng = np.random.default_rng(2); Q = rng.normal(size=(200000, 3))
    FX = K.apply(F, Q)
    res['length_squared_err'] = float(np.abs(np.linalg.norm(FX, axis=1) - (Q ** 2).sum(1)).max())
    Q0 = Q.copy(); Q0[:, 2] = 0; F0 = K.apply(F, Q0)
    res['flat_plane_err'] = float(max(np.abs(F0[:, 0] - (Q0[:, 0] ** 2 - Q0[:, 1] ** 2)).max(), np.abs(F0[:, 1] - 2 * Q0[:, 0] * Q0[:, 1]).max(), np.abs(F0[:, 2]).max()))
    zz = np.linspace(-2, 2, 4001); FZ = K.apply(F, np.stack([0 * zz, 0 * zz, zz], -1))
    res['z_axis_err'] = float(np.abs(FZ[:, 2] - zz ** 2).max() + np.abs(FZ[:, :2]).max())
    # no jump: close pairs
    for st in (1e-4, 1e-5, 1e-6):
        D = rng.normal(size=Q.shape); D *= st / np.linalg.norm(D, axis=1, keepdims=True)
        U = Q / np.linalg.norm(Q, axis=1, keepdims=True)
        res['jump_%g' % st] = float(np.linalg.norm(K.apply(F, U + D) - K.apply(F, U), axis=1).max())
    J = K.jac(F, np.array([[0, 0, -0.5]])); res['DF_at_(0,0,-1/2)'] = [[round(float(a), 6) for a in row] for row in J[0]]
    S = K.skin(F, 361, 720)
    sw = np.sin(S['th'])[:, None] * np.ones(S['det'].shape); sw /= sw.sum()
    res['mirror_reversed_share'] = float(sw[S['det'] < 0].sum()); res['max_stretch'] = float(S['sv'][..., 0].max())
    print(res, flush=True)

    def cut(c0, e1, e2, hw1, hw2, n1, n2, steps=1500):
        a = np.linspace(-hw1, hw1, n1); b = np.linspace(hw2, -hw2, n2)
        A, Bq = np.meshgrid(a, b)
        return K.periods(F, np.asarray(c0) + A[..., None] * np.asarray(e1, float) + Bq[..., None] * np.asarray(e2, float), steps=steps)

    ex, ey, ez = np.eye(3)
    tiles = []
    for ttl, c0, e1, hw1, hw2 in (('cut y = 0, whole (x across, z up)', (-0.4, 0, -0.75), ex, 1.4, 1.4), ('cut x = 0, whole (y across, z up)', (0, 0, -0.75), ey, 1.4, 1.4),
                                  ('cut y = 0, close on the touching point (0, 0, -3/4), 0.5 wide', (0, 0, -0.75), ex, 0.25, 0.25), ('cut x = 0, the same', (0, 0, -0.75), ey, 0.25, 0.25),
                                  ('cut y = 0, closer: 0.06 wide', (0, 0, -0.75), ex, 0.03, 0.03), ('cut x = 0, closer: 0.06 wide', (0, 0, -0.75), ey, 0.03, 0.03),
                                  ('level cut z = -0.75 (x across, y up), 0.5 wide', (0, 0, -0.75), ex, 0.25, None), ('level cut z = -1.0 through the ball, 0.7 wide', (0, 0, -1.0), ex, 0.35, None)):
        if hw2 is None:
            per = cut(c0, e1, ey, hw1, hw1, 361, 361, steps=4000 if hw1 < 0.3 else 1500)
        else:
            per = cut(c0, e1, ez, hw1, hw2, 361, 361, steps=6000 if hw1 < 0.05 else 1500)
        tiles.append((ttl, K.colour_of(per)))
        res[ttl] = {str(k): float((per == k).mean()) for k in np.unique(per) if (per == k).mean() > 0.002}
        print(ttl, res[ttl], round(time.time() - t0), 's', flush=True)
    # how the period-2 body meets the main body: along the z-axis and on small circles round it, at heights near -3/4
    hs = np.linspace(-0.80, -0.70, 201)
    meet = {}
    for rad in (0.0, 0.002, 0.005, 0.01, 0.02):
        row = []
        for ang in np.radians(np.arange(0, 360, 30)):
            c = np.stack([rad * np.cos(ang) + 0 * hs, rad * np.sin(ang) + 0 * hs, hs], -1)
            p = K.periods(F, c, steps=20000, tol=1e-6)
            lo2 = hs[p == 2].max() if (p == 2).any() else np.nan; hi1 = hs[p == 1].min() if (p == 1).any() else np.nan
            row.append((float(lo2), float(hi1), int(((p != 1) & (p != 2)).sum())))
        meet['%g' % rad] = {'top_of_period2': [r_[0] for r_ in row], 'bottom_of_period1': [r_[1] for r_ in row], 'other_points': [r_[2] for r_ in row]}
    res['meeting'] = meet
    print('meeting', json.dumps(meet), flush=True)
    W = 361
    im = Image.new('RGB', (8 + 4 * (W + 8), 8 + 2 * (W + 28)), (12, 14, 20)); dr = ImageDraw.Draw(im)
    for k, (ttl, img) in enumerate(tiles):
        x0 = 8 + (k % 4) * (W + 8); y0 = 8 + (k // 4) * (W + 28)
        dr.text((x0, y0), ttl, fill=(225, 225, 230), font=K.font(12)); im.paste(Image.fromarray(img), (x0, y0 + 20))
    im.save(os.path.join(OUT, 'h_string-cuts.png'))

    L = 1.4; cen = np.array([-0.4, 0.0, -0.7]); hh = 2 * L / (N - 1); m = N // 2
    ax = np.linspace(-L, L, N); ay = np.linspace(0, L, m + 1)
    X, Y, Z = np.meshgrid(cen[0] + ax, ay, cen[2] + ax, indexing='ij')
    q = K.periods(F, np.stack([X, Y, Z], -1), steps=400).astype(np.int16)
    lab = np.concatenate([q[:, :0:-1, :], q], 1); lab[lab >= 9] = -2
    tot = max((lab != 0).sum(), 1)
    res['solid'] = {'volume': float(tot * hh ** 3), 'p1': float((lab == 1).sum() / tot), 'p2': float((lab == 2).sum() / tot), 'bounded_no_repeat': float((lab == -1).sum() / tot)}
    np.savez_compressed(os.path.join(OUT, 'h_string.npz'), lab=lab)
    lo = np.array([cen[0] - L, -L, cen[2] - L])
    for vn, (az, el) in (('a', (-65, 12)), ('b', (-90, 0)), ('c', (-20, -25)), ('d', (-65, 40))):
        Image.fromarray(K.render(lab, lo, hh, az, el, S=440, half=1.5, centre=cen)).save(os.path.join(OUT, 'h_string-view-%s.png' % vn))
    res['seconds'] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, 'h_string.json'), 'w'), indent=1)
    print(json.dumps(res['solid']))
