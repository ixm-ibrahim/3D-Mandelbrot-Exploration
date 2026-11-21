"""Hunter: the up / down rule with a WIDE cone (default 55 to 75 degrees from the z-axis): one-plane square within
15 degrees of the flat plane, +-lathe about the z-axis within 55 degrees of the z-axis, blended between.
    python hupdown2.py [b1 b2 [N]]      -> hunt/h_ud<b1>-*.png, hunt/h_ud<b1>.json"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import probe
b1 = int(sys.argv[1]) if len(sys.argv) > 1 else 55; b2 = int(sys.argv[2]) if len(sys.argv) > 2 else 75; N = int(sys.argv[3]) if len(sys.argv) > 3 else 129
F = probe.make(b1, b2, True); tag = 'h_ud%d' % b1
OUT = os.path.join(HERE, 'hunt'); t0 = time.time(); res = {'rule': 'one-plane square within %d degrees of the flat plane, +-lathe about z within %d degrees of the z-axis' % (90 - b2, b1)}
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
S = K.skin(F, 361, 720); sw = np.sin(S['th'])[:, None] * np.ones(S['det'].shape); sw /= sw.sum()
res['mirror_reversed_share'] = float(sw[S['det'] < 0].sum()); res['max_stretch'] = float(S['sv'][..., 0].max()); res['degree'] = float((sw * S['det']).sum() / 2)
print(res, flush=True)
ex, ey, ez = np.eye(3)
def cut(c0, e1, e2, hw, n=301, steps=900):
    a = np.linspace(-hw, hw, n); b = np.linspace(hw, -hw, n); A, Bq = np.meshgrid(a, b)
    return K.periods(F, np.asarray(c0) + A[..., None] * np.asarray(e1, float) + Bq[..., None] * np.asarray(e2, float), steps=steps)
tiles = []
def save():
    W = 301; im = Image.new('RGB', (8 + 3 * (W + 8), 8 + 2 * (W + 28)), (12, 14, 20)); dr = ImageDraw.Draw(im)
    for k, (tt, img) in enumerate(tiles):
        x0 = 8 + (k % 3) * (W + 8); y0 = 8 + (k // 3) * (W + 28)
        dr.text((x0, y0), tt, fill=(225, 225, 230), font=K.font(12)); im.paste(Image.fromarray(img), (x0, y0 + 20))
    im.save(os.path.join(OUT, tag + '-cuts.png'))
for ttl, c0, e1, e2, hw, st in (('cut x = 0, close on (0, 0, -3/4), 0.5 wide', (0, 0, -0.75), ey, ez, 0.25, 2500), ('cut x = 0, whole (y across, z up), 3 wide', (0, 0, 0), ey, ez, 1.5, 700),
                                ('cut y = 0, whole (x across, z up), 3 wide', (-0.4, 0, 0), ex, ez, 1.5, 700), ('cut x = 0 at (0, 0, -3/4), 0.06 wide', (0, 0, -0.75), ey, ez, 0.03, 5000),
                                ('cut y = 0 at (0, 0, -3/4), 0.5 wide', (0, 0, -0.75), ex, ez, 0.25, 2500), ('level cut z = -0.75, 0.2 wide', (0, 0, -0.75), ex, ey, 0.1, 3000)):
    per = cut(c0, e1, e2, hw, steps=st); tiles.append((ttl, K.colour_of(per)))
    res[ttl] = {str(k): round(float((per == k).mean()), 5) for k in np.unique(per) if (per == k).mean() > 0.002 or k in (0, 1, 2)}
    print(ttl, res[ttl], round(time.time() - t0), 's', flush=True); save()
    json.dump(res, open(os.path.join(OUT, tag + '.json'), 'w'), indent=1)
# how the two bodies approach each other: on upright lines at small distances from the axis
hs = np.linspace(-0.80, -0.70, 401); meet = {}
for rad in (0.0, 0.005, 0.01, 0.02, 0.04):
    tops = []; bots = []
    for ang in np.radians((0, 45, 90)):
        c = np.stack([rad * np.cos(ang) + 0 * hs, rad * np.sin(ang) + 0 * hs, hs], -1)
        p = K.periods(F, c, steps=12000, tol=1e-6)
        tops.append(float(hs[p == 2].max()) if (p == 2).any() else None); bots.append(float(hs[p == 1].min()) if (p == 1).any() else None)
    meet['%g' % rad] = {'top_of_period2': tops, 'bottom_of_main_body': bots}
    print('meeting', rad, meet['%g' % rad], round(time.time() - t0), 's', flush=True)
res['meeting'] = meet; json.dump(res, open(os.path.join(OUT, tag + '.json'), 'w'), indent=1)
L = 1.5; cen = np.array([-0.4, 0.0, 0.0]); hh = 2 * L / (N - 1); m = N // 2
ax = np.linspace(-L, L, N); ay = np.linspace(0, L, m + 1)
X, Y, Z = np.meshgrid(cen[0] + ax, ay, ay, indexing='ij')
q = K.periods(F, np.stack([X, Y, Z], -1), steps=400).astype(np.int16)
lab = np.concatenate([q[:, :0:-1, :], q], 1); lab = np.concatenate([lab[:, :, :0:-1], lab], 2); lab[lab >= 9] = -2
tot = max((lab != 0).sum(), 1)
from scipy import ndimage as ndi
lb, k = ndi.label(lab != 0, structure=np.ones((3, 3, 3)))
res['solid'] = {'volume': float(tot * hh ** 3), 'p1': float((lab == 1).sum() / tot), 'p2': float((lab == 2).sum() / tot), 'bounded_no_repeat': float((lab == -1).sum() / tot), 'biggest_piece_share': float(np.bincount(lb.ravel())[1:].max() / tot)}
np.savez_compressed(os.path.join(OUT, tag + '.npz'), lab=lab)
lo = np.array([cen[0] - L, -L, -L])
for vn, (az, el) in (('a', (-65, 14)), ('b', (-90, 0)), ('c', (0, 0)), ('d', (-65, 45))):
    Image.fromarray(K.render(lab, lo, hh, az, el, S=440, half=1.6, centre=cen)).save(os.path.join(OUT, '%s-view-%s.png' % (tag, vn)))
res['seconds'] = round(time.time() - t0); json.dump(res, open(os.path.join(OUT, tag + '.json'), 'w'), indent=1); print(json.dumps(res['solid']))
