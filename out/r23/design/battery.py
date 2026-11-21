"""Round 23, design: the numbers for every rule on the five shapes.

    python out/r23/design/battery.py <rule,rule,...|all> [sets]      -> battery.json (merged), prints one line per rule and shape

Per rule: M.flat_check (20,000 points, 60 steps).
Per rule and shape, from blocks of side 0.02 (170 x 140 x 140, orbit of each block centre, 80 steps; the flat plane lies
between two layers of blocks). The measures are the rabbit section's (out/r23/rabbit/measure.py), copied here so that
nothing is written into that folder:
  vol30, vol80   volume inside after 30 and after 80 steps
  pieces8        connected pieces of 8 blocks or more; loose = share of the volume not in the biggest piece
  thin           share of the volume removed by peeling one block and growing it back (fins, flakes, shards)
  bodies         lumps of 6+ blocks left after peeling two blocks (0.04) off everywhere; big = share in the biggest
  off            such bodies lying wholly above or wholly below the flat plane; joined / loose; long : thick (median, max)
  over           share of the volume standing over places where the flat picture is empty
  up_down        volume above the flat plane / volume below it
  meet           (rabbit) patches of inside on a ball of radius 0.03 round the point where the three big bodies meet
  lift           share of flat-inside points that stay 80 steps when lifted by a millionth (n = how many were tried)
Blocks computed by the rabbit section for the same rule and shape are read from its cache (read only).
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
RCACHE = os.path.join(R.ROOT, 'out', 'r23', 'rabbit', 'cache')
RKEY = {('oneplane', 'basilica'): 'along0', ('alongonce', 'basilica'): 'along1', ('along', 'basilica'): 'along99'}
RSAME = {'oneplane', 'twoplane', 'along', 'alongonce', 'pillowJ'}
H = 0.02; VN = (170, 140, 140)
S26 = np.ones((3, 3, 3), bool); S6 = ndi.generate_binary_structure(3, 1)


def axes():
    return tuple((np.arange(n) + 0.5) * H - n * H / 2 for n in VN)


def blocks(name, sname, steps=80):
    fn = 'vox-%s-%s-%d.npz' % (name.replace(':', '-'), sname, steps); path = os.path.join(CACHE, fn)
    if os.path.exists(path):
        return np.load(path)['n']
    rk = RKEY.get((name, sname), name if (name in RSAME and sname in ('rabbit', 'siegel', 'dendrite')) else None)
    if rk:
        rp = os.path.join(RCACHE, 'vox-%s-%s-%d.npz' % (rk, sname, steps))
        if os.path.exists(rp):
            return np.load(rp)['n']
    r = R.get(name); c = R.SETS[sname]; xs, ys, zs = axes(); out = np.zeros(VN, np.uint8)
    for i0 in range(0, VN[0], 34):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 34], ys, zs, indexing='ij')
        out[i0:i0 + 34] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps)
    np.savez_compressed(path, n=out)
    return out


def widths(idx):
    p = np.array(idx, float).T * H; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + 3 * H


def sphere_patches(rule, c, centre, rad, nla=120, nlo=240, steps=80):
    la = (np.arange(nla) + 0.5) / nla * np.pi - np.pi / 2; lo = (np.arange(nlo) + 0.5) / nlo * 2 * np.pi
    LA, LO = np.meshgrid(la, lo, indexing='ij')
    x = centre[0] + rad * np.cos(LA) * np.cos(LO); y = centre[1] + rad * np.cos(LA) * np.sin(LO); z = centre[2] + rad * np.sin(LA)
    ins = M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps
    w = np.cos(LA); share = float((ins * w).sum() / w.sum())
    lab, n = ndi.label(np.concatenate([ins, ins[:, :1]], 1), structure=np.ones((3, 3), bool))
    par = list(range(n + 1))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(nla):                                     # the added column is column 0 again: join the seam
        if lab[i, 0] and lab[i, -1]:
            par[find(lab[i, 0])] = find(lab[i, -1])
    for row in (0, nla - 1):
        ls = np.unique(lab[row][lab[row] > 0])
        for l in ls[1:]:
            par[find(l)] = find(ls[0])
    root = np.array([find(a) for a in range(n + 1)]); lab2 = root[lab[:, :-1]]
    big = sorted([float((w * (lab2 == q)).sum() / w.sum()) for q in np.unique(lab2[lab2 > 0])], reverse=True)
    return {'patches': len([a for a in big if a >= 0.003]), 'share': share}


def measure(name, sname):
    n = blocks(name, sname); c = R.SETS[sname]; r = R.get(name); cell = H ** 3; out = {'rule': name, 'set': sname}
    ins = n >= 80; out['vol30'] = float((n >= 30).sum() * cell); out['vol80'] = float(ins.sum() * cell)
    if ins.sum() == 0:
        out.update(pieces8=0, loose=0.0, crumbs=0, thin=0.0, bodies=0, big=0.0, off=0, off_joined=0, off_loose=0, over=0.0, up_down=None)
    else:
        lab, k = ndi.label(ins, structure=S26); size = np.bincount(lab.ravel())[1:]; main = int(np.argmax(size)) + 1
        out['pieces8'] = int((size >= 8).sum()); out['crumbs'] = int((size < 8).sum()); out['loose'] = float(1 - size.max() / ins.sum())
        op = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6), structure=S6) & ins
        out['thin'] = float(1 - op.sum() / ins.sum())
        core = ndi.binary_erosion(ins, structure=S6, iterations=2)
        clab, ck = ndi.label(core, structure=S6); csize = np.bincount(clab.ravel())[1:]
        keep = [i + 1 for i in range(ck) if csize[i] >= 6]
        out['bodies'] = len(keep); out['big'] = float(csize.max() / max(core.sum(), 1)) if ck else 0.0
        zs = axes()[2]; objs = ndi.find_objects(clab); off = []
        for b in keep:
            sl = objs[b - 1]; sub = clab[sl] == b; idx = np.nonzero(sub)
            zlo, zhi = zs[sl[2].start + idx[2].min()], zs[sl[2].start + idx[2].max()]
            if zlo > 0 or zhi < 0:
                wd = widths(idx); off.append((float(wd[0] / wd[2]), int(lab[sl][sub][0]) == main, float(csize[b - 1] * cell)))
        out['off'] = len(off); out['off_joined'] = sum(o[1] for o in off); out['off_loose'] = len(off) - out['off_joined']
        if off:
            rr = np.array([o[0] for o in off]); out['off_ratio_median'] = float(np.median(rr)); out['off_ratio_max'] = float(rr.max()); out['off_vol'] = float(sum(o[2] for o in off))
        xs, ys, _ = axes(); X, Y = np.meshgrid(xs, ys, indexing='ij'); fm = M.flat_stay(X, Y, c[0], c[1], 80) >= 80
        out['over'] = float((ins & ~fm[:, :, None]).sum() / ins.sum())
        up = ins[:, :, VN[2] // 2:].sum(); dn = ins[:, :, :VN[2] // 2].sum(); out['up_down'] = float(up / max(dn, 1))
    if sname == 'rabbit':
        cc = complex(c[0], c[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
        out['meet'] = sphere_patches(r, c, (al.real, al.imag, 0.0), 0.03)
    rng = np.random.default_rng(11); zr, zi = rng.uniform(-1.6, 1.6, 60000), rng.uniform(-1.3, 1.3, 60000)
    ok = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300; zr, zi = zr[ok][:6000], zi[ok][:6000]; out['lift_n'] = int(zr.size)
    out['lift'] = float((M.stay(r, zr, zi, np.full(zr.size, 1e-6), c[0], c[1], c[2], 80) >= 80).mean()) if zr.size else None
    return out


if __name__ == '__main__':
    names = (R.REF + R.SIX) if sys.argv[1] == 'all' else sys.argv[1].split(',')
    sets = sys.argv[2].split(',') if len(sys.argv) > 2 else ['basilica', 'sanmarco', 'rabbit', 'siegel', 'dendrite']
    path = os.path.join(HERE, 'battery.json'); allm = json.load(open(path)) if os.path.exists(path) else {}
    t0 = time.time()
    for nm in names:
        f = M.flat_check(R.get(nm), n=20000, steps=60); allm['%s|flat' % nm] = f
        print('%-9s flat check, differ of %d: M %d, c=-1 %d, rabbit %d, Siegel %d; strays %.1e' % (nm, f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
        for s in sets:
            m = measure(nm, s); allm['%s|%s' % (nm, s)] = m; mt = m.get('meet')
            print('  %-9s vol %.3f/%.3f pieces8 %d loose %.3f thin %.3f | bodies %d big %.2f | off %d (joined %d, loose %d) ratio med %s max %s | over %.2f up/down %s | meet %s | lift %s of %d  [%.0f s]'
                  % (s, m['vol30'], m['vol80'], m['pieces8'], m['loose'], m['thin'], m['bodies'], m['big'], m['off'], m['off_joined'], m['off_loose'],
                     ('%.2f' % m['off_ratio_median']) if m.get('off') else '-', ('%.2f' % m['off_ratio_max']) if m.get('off') else '-', m['over'],
                     ('%.2f' % m['up_down']) if m.get('up_down') else '-', ('%d patches, %.2f' % (mt['patches'], mt['share'])) if mt else '-',
                     ('%.3f' % m['lift']) if m['lift'] is not None else '-', m['lift_n'], time.time() - t0)); sys.stdout.flush()
        json.dump(allm, open(path, 'w'), indent=1)
