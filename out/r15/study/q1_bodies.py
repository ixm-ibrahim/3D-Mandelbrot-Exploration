"""Question 1: c = -1, bodies or one lump? python out/r15/study/q1_bodies.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
from PIL import Image
D = os.path.join(HERE, 'data'); os.makedirs(D, exist_ok=True)
KEY = Fp.REF
AL = (1 - 5 ** 0.5) / 2          # -0.618034, where the flat bodies touch
C = (-1.0, 0.0, 0.0)

if __name__ == '__main__':
    pool = vox.make_pool()
    res = {}
    # ---- fine flat cuts (1201 x 1201, 80 steps)
    n = 1201
    for name, x0 in (('centre', 0.0), ('touch', AL), ('touchR', -AL), ('mid_side', -1.0)):
        d = vox.plane(pool, KEY, (x0, 0, 0), (0, 1, 0), (0, 0, 1), 1.2, 1.2, n, n, C, 80, cache=os.path.join(D, 'q1-x-%s.npy' % name))
        area = float((d == 0).mean() * 2.4 * 2.4)
        lab, k = ndimage.label(d == 0)
        res['area_x_' + name] = area
        res['pieces_x_' + name] = int(k)
        ys, zs = np.nonzero(d == 0)
        if ys.size:
            a = np.linspace(-1.2, 1.2, n)
            res['extent_x_' + name] = dict(y=[float(a[ys.min()]), float(a[ys.max()])], z=[float(a[zs.min()]), float(a[zs.max()])])
        Image.fromarray(vox.cut_img(d)).save(os.path.join(HERE, 'q1-cut-x-%s.png' % name))
        print(name, 'x = %.4f: area %.5f, pieces %d' % (x0, area, k), res.get('extent_x_' + name), flush=True)
    res['ratio_touch_over_centre'] = res['area_x_touch'] / res['area_x_centre']
    res['ratio_touchR_over_centre'] = res['area_x_touchR'] / res['area_x_centre']
    print('cross-section at x = -0.618 / centre: %.2f %%;  at +0.618: %.2f %%' % (100 * res['ratio_touch_over_centre'], 100 * res['ratio_touchR_over_centre']), flush=True)
    # ---- upright cut y = 0 and the flat cut z = 0, whole set, then zooms on the touching point
    d = vox.plane(pool, KEY, (0, 0, 0), (1, 0, 0), (0, 0, 1), 1.75, 1.0, 1401, 801, C, 80, cache=os.path.join(D, 'q1-y0.npy'))
    Image.fromarray(vox.cut_img(d)).save(os.path.join(HERE, 'q1-cut-y0.png'))
    d = vox.plane(pool, KEY, (0, 0, 0), (1, 0, 0), (0, 1, 0), 1.75, 1.0, 1401, 801, C, 80, cache=os.path.join(D, 'q1-z0.npy'))
    Image.fromarray(vox.cut_img(d)).save(os.path.join(HERE, 'q1-cut-z0.png'))
    for L in (0.2, 0.05, 0.0125):
        for pl, u, v in (('y0', (1, 0, 0), (0, 0, 1)), ('z0', (1, 0, 0), (0, 1, 0)), ('x', (0, 1, 0), (0, 0, 1))):
            d = vox.plane(pool, KEY, (AL, 0, 0), u, v, L, L, 701, 701, C, 120, cache=os.path.join(D, 'q1-zoom-%s-%g.npy' % (pl, L)))
            Image.fromarray(vox.cut_img(d, 30.0)).save(os.path.join(HERE, 'q1-zoom-%s-%g.png' % (pl, L)))
            res['zoom_%s_%g_inside_share' % (pl, L)] = float((d == 0).mean())
            print('zoom', pl, L, 'inside share %.4f' % (d == 0).mean(), flush=True)
    # ---- lines through the touching point: how far is there matter
    t = np.linspace(-1, 1, 200001)
    for nm, dirv in (('z', (0, 0, 1)), ('y', (0, 1, 0)), ('diag_yz', (0, 0.7071067811865476, 0.7071067811865476))):
        dd = vox.esc(AL + t * dirv[0], t * dirv[1], t * dirv[2], C, KEY, 200)
        ins = dd == 0
        segs = []
        if ins.any():
            idx = np.flatnonzero(ins); br = np.flatnonzero(np.diff(idx) > 1)
            st = np.r_[idx[0], idx[br + 1]]; en = np.r_[idx[br], idx[-1]]
            segs = [(float(t[a]), float(t[b])) for a, b in zip(st, en)]
        res['line_' + nm] = dict(total_inside_length=float(ins.mean() * 2), segments=segs[:12], n_segments=len(segs))
        print('line through the touching point along', nm, ': inside length %.5f in %d stretches' % (ins.mean() * 2, len(segs)), segs[:6], flush=True)
    # ---- the solid at 321^3
    N = 321; L = 1.7
    dth = vox.box(pool, KEY, (0, 0, 0), L, N, C, 40, cache=os.path.join(D, 'q1-box-%d.npy' % N))
    vol = dth == 0
    h = 2 * L / (N - 1)
    res['volume'] = float(vol.sum() * h ** 3)
    lab, k = ndimage.label(vol)
    sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    res['pieces_3d'] = int(k); res['largest_piece_share'] = float(sizes[0] / vol.sum())
    res['piece_sizes_top'] = [int(s) for s in sizes[:10]]
    ax = np.linspace(-L, L, N)
    prof = vol.sum(axis=(1, 2)) * h * h
    res['profile_x'] = [[float(a), float(p)] for a, p in zip(ax, prof)]
    i0 = int(np.argmin(np.abs(ax - AL)))
    res['box_section_touch'] = float(prof[i0]); res['box_section_centre'] = float(prof[N // 2])
    res['box_section_min_near_touch'] = float(prof[i0 - 6:i0 + 7].min())
    # with the layers near x = -0.618 and +0.618 taken out: how many big pieces
    v2 = vol.copy()
    for xa in (AL, -AL):
        i1 = int(np.argmin(np.abs(ax - xa))); v2[i1 - 1:i1 + 2] = False
    lab2, k2 = ndimage.label(v2); s2 = np.sort(np.bincount(lab2.ravel())[1:])[::-1]
    res['pieces_after_removing_touch_layers'] = int(k2); res['sizes_after'] = [int(s) for s in s2[:8]]
    zz = np.nonzero(vol.any(axis=(0, 1)))[0]; yy = np.nonzero(vol.any(axis=(0, 2)))[0]
    res['half_height_z'] = [float(ax[zz[0]]), float(ax[zz[-1]])]; res['half_width_y'] = [float(ax[yy[0]]), float(ax[yy[-1]])]
    print('volume %.4f, 3D pieces %d, largest %.2f %%, section at touch %.4f, centre %.4f' % (res['volume'], k, 100 * res['largest_piece_share'], res['box_section_touch'], res['box_section_centre']), flush=True)
    print('z extent', res['half_height_z'], 'y extent', res['half_width_y'], flush=True)
    json.dump(res, open(os.path.join(HERE, 'q1.json'), 'w'), indent=1)
    pool.close()
