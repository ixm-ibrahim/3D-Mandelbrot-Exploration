"""Hunter task 1: the skin of the main body of a KNOWN rule's Mandelbrot solid, from the resting point and its 3 x 3
derivative, checked against the solid itself.    python out/r17/hunter/skinmap.py <rule> [N]
Writes out/r17/hunter/skin/<rule>.json, <rule>-*.png, <rule>.npz
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R

name = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 161
F = R.get(name)
OUT = os.path.join(HERE, 'skin'); os.makedirs(OUT, exist_ok=True)
t0 = time.time()
res = {'rule': name}

# ---------------------------------------------------------------- 1. the skin from the eigenvalues
S = K.skin(F, 361, 720)
nrm, wgt = K.normals(S['c'])
cin = S['u'] * (0.9 / S['rho'])[..., None]; cin = cin - K.apply(F, cin)
flip = ((S['c'] - cin) * nrm).sum(-1) < 0
nrm[flip] *= -1
kind, ang = S['kind'], S['ang']
wsum = wgt.sum()
res['skin_area_share'] = {'pair': float(wgt[kind == 0].sum() / wsum), 'minus1': float(wgt[kind == -1].sum() / wsum), 'plus1': float(wgt[kind == 1].sum() / wsum)}
res['dir_share'] = {}
sw = np.sin(S['th'])[:, None] * np.ones_like(wgt); sw /= sw.sum()
for nm_, k_ in (('pair', 0), ('minus1', -1), ('plus1', 1)):
    res['dir_share'][nm_] = float(sw[kind == k_].sum())
res['mirror_reversed_share'] = float(sw[S['det'] < 0].sum())
res['max_stretch'] = float(np.nanmax(np.where(S['bad'], np.nan, S['sv'][..., 0])))
# where all three eigenvalues have the same size (within 2 %): the only places a bud can touch at one point
tri = (S['low'] / S['rho'] > 0.98) & ~S['bad']
res['all_three_equal_dir_share'] = float(sw[tri].sum())


def crossing(val, level, mask):
    a = val - level
    out = np.zeros(val.shape, bool)
    out[:-1] |= (a[:-1] * a[1:] <= 0) & mask[:-1] & mask[1:]
    out |= (a * np.roll(a, -1, 1) <= 0) & mask & np.roll(mask, -1, 1)
    return out


pair = (kind == 0) & ~S['bad']
CUR = {}
for lab, lev in (('1/3', 1 / 3), ('1/4', 0.25), ('1/5', 0.2), ('2/5', 0.4)):
    CUR[lab] = crossing(ang, lev, pair)
edge_m1 = (kind == -1) & ((np.roll(kind, 1, 1) != -1) | (np.roll(kind, -1, 1) != -1) | (np.roll(kind, 1, 0) != -1) | (np.roll(kind, -1, 0) != -1))
edge_p1 = (kind == 1) & ((np.roll(kind, 1, 1) != 1) | (np.roll(kind, -1, 1) != 1) | (np.roll(kind, 1, 0) != 1) | (np.roll(kind, -1, 0) != 1))
res['curve_cells'] = {k: int(v.sum()) for k, v in CUR.items()}
print(name, 'skin done', round(time.time() - t0), 's', res['skin_area_share'], flush=True)

# ---------------------------------------------------------------- 2. what the solid really does just inside / outside
sub_t = slice(0, 361, 2); sub_p = slice(0, 181, 2)          # a quarter turn round the axis (both mirrors hold)
c0 = S['c'][sub_t, sub_p]; n0 = nrm[sub_t, sub_p]; k0 = kind[sub_t, sub_p]; a0 = ang[sub_t, sub_p]; w0 = wgt[sub_t, sub_p]
PER = {}
for tag, dlt in (('in', -0.03), ('out', 0.03), ('out2', 0.07)):
    PER[tag] = K.periods(F, c0 + dlt * n0, steps=1500)
    print(name, 'periods', tag, round(time.time() - t0), 's', flush=True)


def dist(per, mask):
    w = w0[mask]; tot = max(w.sum(), 1e-30); p = per[mask]
    return {'escaped': float(w[p == 0].sum() / tot), 'p1': float(w[p == 1].sum() / tot), 'p2': float(w[p == 2].sum() / tot),
            'p3': float(w[p == 3].sum() / tot), 'p4': float(w[p == 4].sum() / tot), 'p5to24': float(w[p >= 5].sum() / tot),
            'bounded_no_repeat': float(w[p == -1].sum() / tot)}


res['inside_0.03'] = dist(PER['in'], np.ones_like(k0, bool))
for tag in ('out', 'out2'):
    res['outside_%s' % tag] = {'pair': dist(PER[tag], k0 == 0), 'minus1': dist(PER[tag], k0 == -1), 'plus1': dist(PER[tag], k0 == 1)}
    q = {}
    for per, lev in ((3, 1 / 3), (4, 0.25), (5, 0.2)):
        m = (PER[tag] == per) & (k0 == 0)
        near = (k0 == 0) & (np.abs(a0 - lev) < 0.01)
        q['p%d' % per] = {'cells': int(m.sum()),
                          'angle_10_50_90': [float(v) for v in np.percentile(a0[m], [10, 50, 90])] if m.any() else None,
                          'share_within_0.02_turn_of_curve': float((np.abs(a0[m] - lev) < 0.02).mean()) if m.any() else None,
                          'share_of_curve_with_this_period_outside': float((PER[tag][near] == per).mean()) if near.any() else None,
                          'curve_cells': int(near.sum())}
    m2 = PER[tag] == 2
    q['p2'] = {'cells': int(m2.sum()), 'share_on_minus1_patch': float((k0[m2] == -1).mean()) if m2.any() else None,
               'share_of_minus1_patch_with_p2_outside': float((PER[tag][k0 == -1] == 2).mean()) if (k0 == -1).any() else None}
    res['match_%s' % tag] = q

# ---------------------------------------------------------------- 3. charts
def chart_kind():
    img = np.zeros(kind.shape + (3,), np.uint8)
    t = np.clip(ang / 0.5, 0, 1)
    img[..., 0] = 90 + 150 * t; img[..., 1] = 85 + 120 * t; img[..., 2] = 70 + 60 * t      # pair: dark to light sand by angle
    img[kind == -1] = (70, 130, 235); img[kind == 1] = (130, 130, 135)
    for lab, colr in (('1/3', K.PCOL[3]), ('1/4', K.PCOL[4]), ('1/5', K.PCOL[5]), ('2/5', (255, 255, 255))):
        m = CUR[lab]
        for sh in ((0, 0), (1, 0), (0, 1)):
            img[np.roll(m, sh, (0, 1))] = colr
    img[tri] = (255, 60, 60)
    img[S['bad']] = 0
    return img


def tile4(per):                                   # a quarter (phi 0..90) unfolded to the full turn by the two mirrors
    half = np.concatenate([per, per[:, -2::-1]], 1)                # 0..180
    return np.concatenate([half, half[:, -2:0:-1]], 1)             # 0..360 (without the repeat)


Image.fromarray(chart_kind()).resize((720, 361), Image.NEAREST).save(os.path.join(OUT, name + '-chart-kind.png'))
for tag in ('in', 'out', 'out2'):
    Image.fromarray(K.colour_of(tile4(PER[tag]))).resize((720, 361), Image.NEAREST).save(os.path.join(OUT, name + '-chart-%s.png' % tag))

# ---------------------------------------------------------------- 4. the solid itself, coloured by period, with the predicted curves
L = 1.3; cen = np.array([-0.55, 0.0, 0.0]); h = 2 * L / (N - 1); m = N // 2
ax = cen[0] + np.linspace(-L, L, N); ay = np.linspace(0, L, m + 1)
X, Y, Z = np.meshgrid(ax, ay, ay, indexing='ij')
q = K.periods(F, np.stack([X, Y, Z], -1), steps=500)
full = np.concatenate([q[:, :0:-1, :], q], 1); full = np.concatenate([full[:, :, :0:-1], full], 2)
lab = full.astype(np.int16).copy(); lab[lab >= 9] = -2
np.savez_compressed(os.path.join(OUT, name + '.npz'), lab=lab, per_in=PER['in'], per_out=PER['out'], per_out2=PER['out2'], kind=kind, ang=ang.astype(np.float32), c=S['c'].astype(np.float32))
vol = {}
tot = (lab != 0).sum()
for k_, nm_ in ((1, 'p1'), (2, 'p2'), (3, 'p3'), (4, 'p4'), (-1, 'bounded_no_repeat')):
    vol[nm_] = float((lab == k_).sum() / max(tot, 1))
vol['other_periods'] = float(((lab >= 5) | (lab == -2)).sum() / max(tot, 1)); vol['volume'] = float(tot * h ** 3)
res['solid_shares'] = vol
print(name, 'solid done', round(time.time() - t0), 's', vol, flush=True)
lo = np.array([ax[0], -L, -L])
curves = [(S['c'][CUR['1/3']], K.PCOL[3], 1), (S['c'][CUR['1/4']], K.PCOL[4], 1), (S['c'][edge_m1], (255, 255, 255), 0)]
for vn, (az, el) in (('a', (-65, 28)), ('b', (-90, 82)), ('c', (150, 22))):
    for cv, cl in (('', curves), ('-plain', ())):
        im = K.render(lab, lo, h, az, el, S=440, half=1.25, centre=cen, curves=cl)
        Image.fromarray(im).save(os.path.join(OUT, '%s-view-%s%s.png' % (name, vn, cv)))
res['seconds'] = round(time.time() - t0)
json.dump(res, open(os.path.join(OUT, name + '.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
