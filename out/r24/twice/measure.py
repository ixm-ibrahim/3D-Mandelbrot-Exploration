"""Numbers from the cached blocks (side 0.0125).   python out/r24/twice/measure.py <set> [key ...]      -> prints, and merges into measure.json

Per rule and shape:
  vol30, vol120   volume inside after 30 / 120 steps; x1 = vol120 as a multiple of one plane's
  turn            share of the inside blocks that change when the solid is turned by 180 degrees about the upright axis
  mirror_y        the same for the mirror y -> -y (only meaningful for real c)
  reach           largest |x|, |y|, |z| of an inside block (the box is 1.8 (2.0 airplane), 1.4, 1.4)
  pieces          connected pieces of 8 blocks or more; loose = share of the volume not in the biggest
  thin1, thin2    share of the volume removed by peeling 1 (2) blocks and growing them back: spikes, fins, flakes
  spikes          how many separate pieces that thin2 part falls into (pieces of 4 blocks or more)
  hair / blade    of the thin2 part: share that is thin in two directions (hair, thorn) / in one direction (blade, fin)
  bodies          lumps left after peeling 3 blocks (0.0375) everywhere, 20+ blocks; big = share of the biggest
  off             such bodies lying wholly above the flat plane (the same lie below): how many, and for each the
                  direction of its middle (latitude, longitude), its distance, and long : middle : thick
"""
import os, sys, json
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tw
M = tw.M
S6 = ndi.generate_binary_structure(3, 1); S26 = np.ones((3, 3, 3), bool); H = tw.H


def local_shape(mask, sel, rad=4):
    """For the blocks in sel: the three widths of the inside blocks within a cube of half-side rad round each (second moments).
    Returns (hair share, blade share, body share) of sel."""
    m = mask.astype(np.float32); size = 2 * rad + 1
    n = ndi.uniform_filter(m, size, mode='constant')
    ax = [np.arange(s, dtype=np.float32) for s in mask.shape]
    G = np.meshgrid(*ax, indexing='ij')
    mean = [ndi.uniform_filter(m * g, size, mode='constant') for g in G]
    idx = np.nonzero(sel); nn = n[idx]
    mu = [mm[idx] / nn for mm in mean]
    cov = np.zeros((idx[0].size, 3, 3), np.float64)
    for i in range(3):
        for j in range(i, 3):
            v = ndi.uniform_filter(m * G[i] * G[j], size, mode='constant')[idx] / nn - mu[i] * mu[j]
            cov[:, i, j] = v; cov[:, j, i] = v
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 1e-9, None), axis=1)[:, ::-1]        # largest first
    r2, r3 = np.sqrt(ev[:, 1] / ev[:, 0]), np.sqrt(ev[:, 2] / ev[:, 0])
    hair = r2 < 0.45; blade = (~hair) & (r3 < 0.45)
    return float(hair.mean()), float(blade.mean()), float((~hair & ~blade).mean())


def widths(idx):
    p = np.array(idx, float).T * H; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + H


def measure(key, sn, steps=120):
    nh = tw.vox(key, sn); n = tw.full(nh); ins = n >= steps; cell = H ** 3; out = {'rule': key, 'set': sn}
    out['vol30'] = float((n >= 30).sum() * cell); out['vol120'] = float(ins.sum() * cell)
    tot = max(int(ins.sum()), 1)
    out['turn'] = float((ins != ins[::-1, ::-1, :]).sum() / 2 / tot); out['mirror_y'] = float((ins != ins[:, ::-1, :]).sum() / 2 / tot)
    xs, ys, zs = tw.grid(sn); ii = np.nonzero(ins)
    out['reach'] = [float(np.abs(xs[ii[0]]).max()), float(np.abs(ys[ii[1]]).max()), float(zs[np.abs(ii[2] - zs.size + 0.5).astype(int)].max())] if tot > 1 else [0, 0, 0]
    lab, k = ndi.label(ins, structure=S26); size = np.bincount(lab.ravel())[1:]
    out['pieces'] = int((size >= 8).sum()); out['loose'] = float(1 - size.max() / tot)
    op1 = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6), structure=S6) & ins
    op2 = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6, iterations=2), structure=S6, iterations=2) & ins
    out['thin1'] = float(1 - op1.sum() / tot); out['thin2'] = float(1 - op2.sum() / tot)
    thin = ins & ~op2; tl, tk = ndi.label(thin, structure=S26); ts = np.bincount(tl.ravel())[1:]
    out['spikes'] = int((ts >= 4).sum())
    # each thin piece of 12+ blocks by its own three widths: hair = more than twice as long as its middle width;
    # blade = not a hair, and more than twice as wide as thick; the rest are stubs (short knobs)
    tobj = ndi.find_objects(tl); cnt = {'hair': 0, 'blade': 0, 'stub': 0}; ratios = []
    for b in np.nonzero(ts >= 12)[0]:
        sl = tobj[b]; idx = np.nonzero(tl[sl] == b + 1); wd = widths(idx)
        kind = 'hair' if wd[0] > 2 * wd[1] else ('blade' if wd[1] > 2 * wd[2] else 'stub')
        cnt[kind] += int(ts[b]); ratios.append(wd[0] / wd[2])
    tt = max(sum(cnt.values()), 1); out['hair'] = cnt['hair'] / tt; out['blade'] = cnt['blade'] / tt; out['stub'] = cnt['stub'] / tt
    out['spike_long_thick'] = float(np.median(ratios)) if ratios else 0.0
    core = ndi.binary_erosion(ins, structure=S6, iterations=3)
    cl, ck = ndi.label(core, structure=S6); cs = np.bincount(cl.ravel())[1:]
    keep = [i + 1 for i in range(ck) if cs[i] >= 20]; out['bodies'] = len(keep); out['big'] = float(cs.max() / max(core.sum(), 1)) if ck else 0.0
    objs = ndi.find_objects(cl); off = []; nz = zs.size
    for b in keep:
        sl = objs[b - 1]; sub = cl[sl] == b; idx = np.nonzero(sub)
        if sl[2].start + idx[2].min() >= nz:                       # wholly above the flat plane
            p = np.array([xs[sl[0].start + idx[0]].mean(), ys[sl[1].start + idx[1]].mean(), (sl[2].start + idx[2].mean() - nz + 0.5) * H])
            d = float(np.linalg.norm(p)); wd = widths(idx) + 6 * H              # put back the three blocks peeled from each side
            off.append({'lat': float(np.degrees(np.arcsin(p[2] / d))), 'lon': float(np.degrees(np.arctan2(p[1], p[0])) % 360), 'dist': d,
                        'long': float(wd[0]), 'mid': float(wd[1]), 'thick': float(wd[2]), 'blocks': int(cs[b - 1])})
    off.sort(key=lambda o: -o['blocks']); out['off'] = len(off); out['off_list'] = off[:12]
    return out


def line(m, one=None):
    s = '%-22s %-9s vol %.3f / %.3f' % (m['rule'], m['set'], m['vol30'], m['vol120'])
    if one:
        s += ' (x%.2f of one plane)' % (m['vol120'] / max(one, 1e-9))
    s += ' | turned by 180: %.4f differ, mirror y: %.4f | reach %.2f %.2f %.2f | pieces %d, loose %.3f | thin %.3f / %.3f in %d spikes (hair %.2f, blade %.2f, stub %.2f; long : thick median %.1f) | bodies %d (big %.2f), off the flat plane %d' % (
        m['turn'], m['mirror_y'], m['reach'][0], m['reach'][1], m['reach'][2], m['pieces'], m['loose'], m['thin1'], m['thin2'], m['spikes'], m.get('hair', 0), m.get('blade', 0), m.get('stub', 0),
        m.get('spike_long_thick', 0), m['bodies'], m['big'], m['off'])
    return s


if __name__ == '__main__':
    sn = sys.argv[1]
    keys = sys.argv[2:] or ['oneplane', 'along', 'm4:-0.10', 'm4:-0.20', 'm4:-0.30', 'm6:-0.05', 'm6:-0.10', 'm6:-0.20', 'm8:-0.05']
    path = os.path.join(HERE, 'measure.json'); one = None
    for key in keys:
        if not os.path.exists(tw.vkey(key, sn)):
            print('%-22s %-9s (no blocks yet)' % (key, sn)); continue
        m = measure(key, sn)
        if key == 'oneplane':
            one = m['vol120']
        print(line(m, one))
        for o in m['off_list'][:6]:
            print('      body above the flat plane: latitude %5.1f longitude %5.1f distance %.2f | long %.3f : middle %.3f : thick %.3f = %.1f : %.1f : 1 | %d blocks' % (
                o['lat'], o['lon'], o['dist'], o['long'], o['mid'], o['thick'], o['long'] / o['thick'], o['mid'] / o['thick'], o['blocks']))
        sys.stdout.flush()
        allm = json.load(open(path)) if os.path.exists(path) else {}
        allm['%s|%s' % (key, sn)] = m; json.dump(allm, open(path, 'w'), indent=1)
