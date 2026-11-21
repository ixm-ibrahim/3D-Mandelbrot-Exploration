"""Hunter task 4, third rule: h_updown. The mirror-symmetric version of h_string.
One-plane square P everywhere (cut z = 0 exact), except in the two cones within 30 degrees of the z-axis:
    lower cone:  F = +Lz(v),   upper cone:  F = -Lz(v),    Lz(x, y, z) = (2 z x, 2 z y, z^2 - x^2 - y^2)
(the lathe about the z-axis and its negative), blended into P between 30 and 50 degrees on the sphere of directions.
It commutes with both mirrors y -> -y and z -> -z and squares lengths. On the z-axis it is t -> -t |t|: the point
(0, 0, t) goes to the OTHER side. At (0, 0, -1/2) and (0, 0, +1/2) the derivative is exactly -identity.
It is NOT exact on y = 0, the choice 'a cone of 30 degrees' is free, and it has not been through the bench.
    python out/r17/hunter/hupdown.py [N]
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


def h_updown(x, y, z):
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); rr = np.maximum(r, 1e-300)
    beta = np.arccos(np.clip(np.abs(z) / rr, -1, 1))            # angle from the z-axis (either end)
    t = np.clip((beta - B1) / (B2 - B1), 0, 1)
    s = g(1 - t) / (g(t) + g(1 - t))
    sg = np.where(z > 0, -1.0, 1.0)                              # upper cone: -Lz, lower cone: +Lz
    X1, Y1, Z1 = P(x, y, z)
    X2, Y2, Z2 = sg * 2 * z * x, sg * 2 * z * y, sg * (z * z - x * x - y * y)
    X, Y, Z = (1 - s) * X1 + s * X2, (1 - s) * Y1 + s * Y2, (1 - s) * Z1 + s * Z2
    n = np.sqrt(X * X + Y * Y + Z * Z)
    k = np.where(n > 0, r2 / np.maximum(n, 1e-300), 0.0)
    return X * k, Y * k, Z * k


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 129
    OUT = os.path.join(HERE, 'hunt'); os.makedirs(OUT, exist_ok=True); t0 = time.time(); res = {}
    F = h_updown
    rng = np.random.default_rng(2); Q = rng.normal(size=(200000, 3)); FX = K.apply(F, Q)
    res['length_squared_err'] = float(np.abs(np.linalg.norm(FX, axis=1) - (Q ** 2).sum(1)).max())
    Q0 = Q.copy(); Q0[:, 2] = 0; F0 = K.apply(F, Q0)
    res['flat_plane_err'] = float(max(np.abs(F0[:, 0] - (Q0[:, 0] ** 2 - Q0[:, 1] ** 2)).max(), np.abs(F0[:, 1] - 2 * Q0[:, 0] * Q0[:, 1]).max(), np.abs(F0[:, 2]).max()))
    res['mirror_y_err'] = float(np.abs(FX - K.apply(F, Q * [1, -1, 1]) * [1, -1, 1]).max()); res['mirror_z_err'] = float(np.abs(FX - K.apply(F, Q * [1, 1, -1]) * [1, 1, -1]).max())
    U = Q / np.linalg.norm(Q, axis=1, keepdims=True)
    for st in (1e-4, 1e-5, 1e-6):
        D = rng.normal(size=Q.shape); D *= st / np.linalg.norm(D, axis=1, keepdims=True)
        res['jump_%g' % st] = float(np.linalg.norm(K.apply(F, U + D) - K.apply(F, U), axis=1).max())
    res['DF_at_(0,0,-1/2)'] = [[round(float(a), 6) for a in row] for row in K.jac(F, np.array([[0, 0, -0.5]]))[0]]
    res['DF_at_(0,0,+1/2)'] = [[round(float(a), 6) for a in row] for row in K.jac(F, np.array([[0, 0, 0.5]]))[0]]
    S = K.skin(F, 361, 720); sw = np.sin(S['th'])[:, None] * np.ones(S['det'].shape); sw /= sw.sum()
    res['mirror_reversed_share'] = float(sw[S['det'] < 0].sum()); res['max_stretch'] = float(S['sv'][..., 0].max()); res['degree'] = float((sw * S['det']).sum() / 2)
    print(res, flush=True)
    ex, ey, ez = np.eye(3)

    def cut(c0, e1, e2, hw, n=321, steps=900):
        a = np.linspace(-hw, hw, n); b = np.linspace(hw, -hw, n); A, Bq = np.meshgrid(a, b)
        return K.periods(F, np.asarray(c0) + A[..., None] * np.asarray(e1, float) + Bq[..., None] * np.asarray(e2, float), steps=steps)
    tiles = []
    for ttl, c0, e1, e2, hw, st in (('cut y = 0, whole (x across, z up), 3 wide', (-0.4, 0, 0), ex, ez, 1.5, 700), ('cut x = 0, whole (y across, z up), 3 wide', (0, 0, 0), ey, ez, 1.5, 700),
                                    ('cut x = 0, close on (0, 0, -3/4), 0.5 wide', (0, 0, -0.75), ey, ez, 0.25, 2500), ('the same, 0.06 wide', (0, 0, -0.75), ey, ez, 0.03, 6000)):
        per = cut(c0, e1, e2, hw, steps=st); tiles.append((ttl, K.colour_of(per)))
        res[ttl] = {str(k): float((per == k).mean()) for k in np.unique(per) if (per == k).mean() > 0.002}
        print(ttl, res[ttl], round(time.time() - t0), 's', flush=True)
        W = 321; im = Image.new('RGB', (8 + 4 * (W + 8), 8 + W + 28), (12, 14, 20)); dr = ImageDraw.Draw(im)
        for k, (tt, img) in enumerate(tiles):
            dr.text((8 + k * (W + 8), 8), tt, fill=(225, 225, 230), font=K.font(12)); im.paste(Image.fromarray(img), (8 + k * (W + 8), 28))
        im.save(os.path.join(OUT, 'h_updown-cuts.png'))
    L = 1.5; cen = np.array([-0.4, 0.0, 0.0]); hh = 2 * L / (N - 1); m = N // 2
    ax = np.linspace(-L, L, N); ay = np.linspace(0, L, m + 1)
    X, Y, Z = np.meshgrid(cen[0] + ax, ay, ay, indexing='ij')
    q = K.periods(F, np.stack([X, Y, Z], -1), steps=400).astype(np.int16)
    lab = np.concatenate([q[:, :0:-1, :], q], 1); lab = np.concatenate([lab[:, :, :0:-1], lab], 2); lab[lab >= 9] = -2
    tot = max((lab != 0).sum(), 1)
    res['solid'] = {'volume': float(tot * hh ** 3), 'p1': float((lab == 1).sum() / tot), 'p2': float((lab == 2).sum() / tot), 'bounded_no_repeat': float((lab == -1).sum() / tot)}
    from scipy import ndimage as ndi
    lb, k = ndi.label(lab != 0, structure=np.ones((3, 3, 3))); res['biggest_piece_share'] = float(np.bincount(lb.ravel())[1:].max() / tot)
    np.savez_compressed(os.path.join(OUT, 'h_updown.npz'), lab=lab)
    lo = np.array([cen[0] - L, -L, -L])
    for vn, (az, el) in (('a', (-65, 12)), ('b', (-90, 0)), ('c', (0, 0)), ('d', (-65, 40))):
        Image.fromarray(K.render(lab, lo, hh, az, el, S=440, half=1.6, centre=cen)).save(os.path.join(OUT, 'h_updown-view-%s.png' % vn))
    res['seconds'] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, 'h_updown.json'), 'w'), indent=1); print(json.dumps(res['solid']))
