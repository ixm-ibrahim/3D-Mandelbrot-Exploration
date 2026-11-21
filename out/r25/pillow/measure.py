"""Numbers from blocks (side 0.025, box x -1.8..1.8, y and z -1.4..1.4, 40 steps unless said).

    python out/r25/pillow/measure.py <sets: m1,rab,...> <spec> <spec> ...

  vol        volume inside
  loose      share of the volume not in the biggest piece;  crumbs = pieces under 8 blocks
  thin       share removed by peeling one block and growing it back (fins, flakes, films)
  bodies     lumps of >= 6 blocks left after peeling two blocks (0.05) everywhere; big = share of the biggest
  off        peeled bodies wholly above or wholly below the flat plane: number, how many joined to the biggest piece,
             median long : thick (1 = a ball)
  up/down    volume above the flat plane over volume below
  l/r        (sets on the x-axis) share of the volume that changes when the solid is mirrored in the upright plane y = 0
  half turn  share of the volume that changes when the solid is turned half round the upright axis (the flat picture: 0)
  touch      (c = -1) area of the cut across the touching point x = -0.618 over the area of the cut across x = 0
  meet       (rabbit) patches of inside on a ball of radius 0.03 round the meeting point, share of its skin inside
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import cuts as C
import solids as SO
M = P.M
S26 = np.ones((3, 3, 3), bool); S6 = ndi.generate_binary_structure(3, 1)
HB = 0.025
XS = np.arange(-1.8 + HB / 2, 1.8, HB); YS = np.arange(-1.4 + HB / 2, 1.4, HB); ZS = YS.copy()


def vox(rule, c, steps=40):
    out = np.zeros((XS.size, YS.size, ZS.size), bool)
    Y, Z = np.meshgrid(YS, ZS, indexing='ij')
    for i0 in range(0, XS.size, 16):
        xs = XS[i0:i0 + 16]
        X = np.broadcast_to(xs[:, None, None], (xs.size,) + Y.shape)
        out[i0:i0 + 16] = M.stay(rule, X, np.broadcast_to(Y, X.shape), np.broadcast_to(Z, X.shape), c[0], c[1], c[2], steps) >= steps
    return out


def widths(idx):
    p = np.array(idx, float).T * HB; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + 3 * HB


def sphere_patches(rule, c, centre, rad, nla=90, nlo=180, steps=60):
    la = (np.arange(nla) + 0.5) / nla * np.pi - np.pi / 2; lo = (np.arange(nlo) + 0.5) / nlo * 2 * np.pi
    LA, LO = np.meshgrid(la, lo, indexing='ij')
    x = centre[0] + rad * np.cos(LA) * np.cos(LO); y = centre[1] + rad * np.cos(LA) * np.sin(LO); z = centre[2] + rad * np.sin(LA)
    ins = M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps
    w = np.cos(LA); share = float((ins * w).sum() / w.sum())
    ext = np.concatenate([ins, ins[:, :1]], 1); lab, n = ndi.label(ext, structure=np.ones((3, 3), bool))
    par = list(range(n + 1))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(nla):
        if lab[i, 0] and lab[i, -1]:
            par[find(lab[i, 0])] = find(lab[i, -1])
    for row in (0, nla - 1):
        ls = np.unique(lab[row][lab[row] > 0])
        for l in ls[1:]:
            par[find(l)] = find(ls[0])
    root = np.array([find(a) for a in range(n + 1)]); lab2 = root[lab][:, :-1]
    big = sorted([float((w * (lab2 == r)).sum() / w.sum()) for r in np.unique(lab2[lab2 > 0])], reverse=True)
    return len([a for a in big if a >= 0.003]), share


def measure(rule, sname, steps=40):
    c = SO.SETS[sname][1]; ins = vox(rule, c, steps); cell = HB ** 3; out = {'rule': rule.name, 'set': sname, 'vol': float(ins.sum() * cell)}
    if ins.sum() == 0:
        return out
    lab, k = ndi.label(ins, structure=S26); size = np.bincount(lab.ravel())[1:]; main = int(np.argmax(size)) + 1
    out['loose'] = float(1 - size.max() / ins.sum()); out['crumbs'] = int((size < 8).sum()); out['pieces8'] = int((size >= 8).sum())
    op = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6), structure=S6) & ins
    out['thin'] = float(1 - op.sum() / ins.sum())
    core = ndi.binary_erosion(ins, structure=S6, iterations=2)
    clab, ck = ndi.label(core, structure=S6); csize = np.bincount(clab.ravel())[1:]
    keep = [i + 1 for i in range(ck) if csize[i] >= 6]
    out['bodies'] = len(keep); out['big'] = float(csize.max() / max(core.sum(), 1)) if ck else 0.0
    objs = ndi.find_objects(clab); off = []
    for b in keep:
        sl = objs[b - 1]; sub = clab[sl] == b; idx = np.nonzero(sub)
        zlo, zhi = ZS[sl[2].start + idx[2].min()], ZS[sl[2].start + idx[2].max()]
        if zlo > 0 or zhi < 0:
            wd = widths(idx); off.append((float(wd[0] / wd[2]), int(lab[sl][sub][0]) == main, float(csize[b - 1] * cell)))
    out['off'] = len(off); out['off_joined'] = sum(o[1] for o in off)
    out['off_ratio'] = float(np.median([o[0] for o in off])) if off else None
    out['off_vol'] = float(sum(o[2] for o in off))
    nz = ZS.size // 2; out['up_down'] = float(ins[:, :, nz:].sum() / max(ins[:, :, :nz].sum(), 1))
    if c[1] == 0:
        out['lr'] = float((ins != ins[:, ::-1, :]).sum() / (2 * ins.sum()))
    out['ht'] = float((ins != ins[::-1, ::-1, :]).sum() / (2 * ins.sum()))
    if sname == 'm1':
        out['touch'] = float(C.touching(rule, steps=50)[0])
    if sname in ('rab', 'arab'):
        cc = complex(c[0], c[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
        out['meet'] = sphere_patches(rule, c, (al.real, al.imag, 0.0), 0.03)
    return out


def line(m):
    if m['vol'] == 0:
        return '%-30s %-5s empty' % (m['rule'], m['set'])
    s = '%-30s %-5s vol %.3f loose %.3f crumbs %4d thin %.3f | bodies %2d big %.2f | off %2d (joined %2d) long:thick %s offvol %.3f | up/down %.2f' % (
        m['rule'], m['set'], m['vol'], m['loose'], m['crumbs'], m['thin'], m['bodies'], m['big'], m['off'], m['off_joined'],
        ('%.2f' % m['off_ratio']) if m['off_ratio'] else '  - ', m['off_vol'], m['up_down'])
    if 'lr' in m:
        s += ' | l/r %.3f' % m['lr']
    s += ' | half turn %.3f' % m['ht']
    if 'touch' in m:
        s += ' | touch %.3f' % m['touch']
    if 'meet' in m:
        s += ' | meet %d patches, %.2f' % m['meet']
    return s


if __name__ == '__main__':
    sets = sys.argv[1].split(','); t0 = time.time(); path = os.path.join(HERE, 'numbers.json')
    allm = json.load(open(path)) if os.path.exists(path) else {}
    for spec in sys.argv[2:]:
        r = SO.get(spec)
        for s in sets:
            m = measure(r, s); allm['%s|%s' % (spec, s)] = m
            print(line(m), ' [%.0f s]' % (time.time() - t0)); sys.stdout.flush()
    json.dump(allm, open(path, 'w'), indent=1)
