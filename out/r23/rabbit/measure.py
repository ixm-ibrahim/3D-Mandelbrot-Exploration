"""Round 23, section "rabbit": the numbers behind the sheet.   python out/r23/rabbit/measure.py <rules|all> [sets]

For each rule and shape, from the cached blocks (doors.vox: 170 x 140 x 140 blocks of side 0.02, 80 steps):
  vol30, vol80       volume inside after 30 and after 80 steps (a slow leak shows as a drop)
  pieces             connected pieces of the inside (blocks touching by a face, an edge or a corner)
  loose              share of the volume that is NOT in the biggest piece; crumbs = pieces under 8 blocks
  thin               share of the volume that a peel of one block and its regrowth removes: fins, flakes, films, shards
  bodies             what is left after peeling two blocks off everywhere (0.04), counted as separate lumps of >= 6 blocks:
                     bodies that touch at single points or thin necks come apart, a lump stays one
  big                share of all peeled volume in the biggest body (1.00 = one lump)
  off                bodies that lie wholly above or wholly below the flat plane; for those: joined (its piece is the
                     biggest piece) or loose; long to thick ratio from the body's own three widths
  over               share of the volume that stands over places where the flat picture is empty
  meet               (rabbit: the point where the three biggest bodies meet; Siegel: the point 0 where the disc meets
                     its twin) patches of inside on a small ball round that point, and the share of the ball's skin inside
  lift               share of flat-inside points that stay when lifted by a millionth
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doors as D
M = D.M
S26 = np.ones((3, 3, 3), bool); S6 = ndi.generate_binary_structure(3, 1)
H = D.VH


def flat_mask(c, steps=80):
    xs, ys, zs = D.vox_axes(); X, Y = np.meshgrid(xs, ys, indexing='ij')
    return M.flat_stay(X, Y, c[0], c[1], steps) >= steps


def widths(idx):
    """Three widths of a body from its blocks (an ellipsoid with the same spread), plus the peeled skin."""
    p = np.array(idx, float).T * H; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + 3 * H                       # full widths; 1.5 blocks of skin on each side


def sphere_patches(rule, c, centre, rad, nla=120, nlo=240, steps=80):
    la = (np.arange(nla) + 0.5) / nla * np.pi - np.pi / 2; lo = (np.arange(nlo) + 0.5) / nlo * 2 * np.pi
    LA, LO = np.meshgrid(la, lo, indexing='ij')
    x = centre[0] + rad * np.cos(LA) * np.cos(LO); y = centre[1] + rad * np.cos(LA) * np.sin(LO); z = centre[2] + rad * np.sin(LA)
    ins = M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps
    w = np.cos(LA); share = float((ins * w).sum() / w.sum())
    lab, n = ndi.label(ins, structure=np.ones((3, 3), bool))
    par = list(range(n + 1))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(nla):                                     # join across the seam of longitude
        for di in (-1, 0, 1):
            j = i + di
            if 0 <= j < nla and lab[i, 0] and lab[j, -1]:
                par[find(lab[i, 0])] = find(lab[j, -1])
    for row in (0, nla - 1):                                 # a pole is one place
        ls = np.unique(lab[row][lab[row] > 0])
        for l in ls[1:]:
            par[find(l)] = find(ls[0])
    root = np.array([find(a) for a in range(n + 1)]); lab2 = root[lab]
    area = {}
    for r in np.unique(lab2[lab2 > 0]):
        area[int(r)] = float((w * (lab2 == r)).sum() / w.sum())
    big = sorted([a for a in area.values() if a >= 0.003], reverse=True)
    return {'patches': len(big), 'share': share, 'biggest': big[:4]}


def measure(key, sname):
    n = D.vox(key, sname, quiet=True); c = D.SETS[sname]; r = D.get(key)
    cell = H ** 3; out = {'rule': key, 'set': sname}
    i30 = n >= 30; ins = n >= 80
    out['vol30'] = float(i30.sum() * cell); out['vol80'] = float(ins.sum() * cell)
    if ins.sum() == 0:
        out.update(pieces=0, loose=0.0, crumbs=0, thin=0.0, bodies=0, big=0.0, off=0, off_joined=0, off_loose=0, over=0.0, zmax=0.0, up_down=None)
    else:
        lab, k = ndi.label(ins, structure=S26); size = np.bincount(lab.ravel())[1:]
        main = int(np.argmax(size)) + 1
        out['pieces'] = int(k); out['loose'] = float(1 - size.max() / ins.sum()); out['crumbs'] = int((size < 8).sum())
        out['pieces8'] = int((size >= 8).sum())
        op = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6), structure=S6) & ins
        out['thin'] = float(1 - op.sum() / ins.sum())
        core = ndi.binary_erosion(ins, structure=S6, iterations=2)
        clab, ck = ndi.label(core, structure=S6); csize = np.bincount(clab.ravel())[1:]
        keep = [i + 1 for i in range(ck) if csize[i] >= 6]
        out['bodies'] = len(keep); out['big'] = float(csize.max() / max(core.sum(), 1)) if ck else 0.0
        zs = D.vox_axes()[2]; objs = ndi.find_objects(clab)
        off = []; onr = []
        for b in keep:
            sl = objs[b - 1]; sub = clab[sl] == b; idx = np.nonzero(sub)
            zlo, zhi = zs[sl[2].start + idx[2].min()], zs[sl[2].start + idx[2].max()]
            wd = widths(idx); ratio = float(wd[0] / wd[2])
            piece = int(lab[sl][sub][0])
            if zlo > 0 or zhi < 0:
                off.append({'vol': float(csize[b - 1] * cell), 'ratio': ratio, 'joined': piece == main, 'z': float((zlo + zhi) / 2), 'widths': [float(t) for t in wd]})
            else:
                onr.append((float(csize[b - 1] * cell), ratio))
        out['off'] = len(off); out['off_joined'] = sum(o['joined'] for o in off); out['off_loose'] = len(off) - out['off_joined']
        if off:
            rr = np.array([o['ratio'] for o in off]); out['off_ratio_median'] = float(np.median(rr)); out['off_ratio_max'] = float(rr.max()); out['off_ratio_min'] = float(rr.min())
            out['off_vol'] = float(sum(o['vol'] for o in off))
        onr.sort(reverse=True)
        out['on'] = len(onr); out['on_ratio_biggest'] = onr[0][1] if onr else None
        out['on_ratio_median'] = float(np.median([q[1] for q in onr])) if onr else None
        fm = flat_mask(c)
        out['over'] = float((ins & ~fm[:, :, None]).sum() / ins.sum())
        zi = np.nonzero(ins.any((0, 1)))[0]; out['zmax'] = float(np.abs(zs[zi]).max() + H / 2)
        up = ins[:, :, D.VN[2] // 2:].sum(); dn = ins[:, :, :D.VN[2] // 2].sum(); out['up_down'] = float(up / max(dn, 1))
    # the meeting point
    if sname == 'rabbit':
        cc = complex(c[0], c[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
        for rad in (0.06, 0.03):
            out['meet%g' % rad] = sphere_patches(r, c, (al.real, al.imag, 0.0), rad)
    elif sname == 'siegel':
        for rad in (0.06, 0.03):
            out['meet%g' % rad] = sphere_patches(r, c, (0.0, 0.0, 0.0), rad)
    # lift test
    if sname in ('rabbit', 'siegel'):
        rng = np.random.default_rng(11); zr, zi2 = rng.uniform(-1.6, 1.6, 60000), rng.uniform(-1.3, 1.3, 60000)
        ok = M.flat_stay(zr, zi2, c[0], c[1], 300) >= 300; zr, zi2 = zr[ok][:6000], zi2[ok][:6000]
        out['lift'] = float((M.stay(r, zr, zi2, np.full(zr.size, 1e-6), c[0], c[1], c[2], 80) >= 80).mean()); out['lift_n'] = int(zr.size)
    return out


if __name__ == '__main__':
    keys = D.ORDER if (len(sys.argv) < 2 or sys.argv[1] == 'all') else sys.argv[1].split(',')
    sets = sys.argv[2].split(',') if len(sys.argv) > 2 else ['rabbit', 'siegel', 'dendrite', 'tilt']
    path = os.path.join(HERE, 'numbers.json')
    allm = json.load(open(path)) if os.path.exists(path) else {}
    t0 = time.time()
    for k in keys:
        for s in sets:
            m = measure(k, s); allm['%s|%s' % (k, s)] = m
            mt = m.get('meet0.03')
            print('%-10s %-9s vol %.3f/%.3f pieces %d (>=8: %d) loose %.3f thin %.3f | bodies %d big %.2f | off %d (joined %d, loose %d) ratio med %s max %s | over %.2f zmax %.2f | meet %s | lift %s  [%.0f s]'
                  % (k, s, m['vol30'], m['vol80'], m['pieces'], m.get('pieces8', 0), m['loose'], m['thin'], m['bodies'], m['big'], m['off'], m['off_joined'], m['off_loose'],
                     ('%.2f' % m['off_ratio_median']) if m.get('off') else '-', ('%.2f' % m['off_ratio_max']) if m.get('off') else '-', m['over'], m['zmax'],
                     ('%d patches, %.2f' % (mt['patches'], mt['share'])) if mt else '-', ('%.3f' % m['lift']) if 'lift' in m else '-', time.time() - t0)); sys.stdout.flush()
    json.dump(allm, open(path, 'w'), indent=1)
