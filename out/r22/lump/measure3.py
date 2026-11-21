"""(d) again, with small gaps bridged as round 21's judge did; and the Siegel disc: do the orbits come down to the page?
    python out/r22/lump/measure3.py   -> prints (kept as measure3.txt by the caller)"""
import sys, time
import numpy as np
from scipy import ndimage
import lumplib as L
M = L.M

c = L.RABBIT; cc = complex(c[0], c[1]); cyc = [cc, cc * cc + cc, 0j]; pn = ['c', 'c^2+c', '0']
flat3 = np.array([[w.real, w.imag, 0.0] for w in cyc])


def one(r, p, cset=c, k=0):
    n = p.shape[1]; o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), k, np.full(n, cset[0]), np.full(n, cset[1]), np.full(n, cset[2]))
    return np.stack([o[0] + cset[0], o[1] + cset[1], o[2] + cset[2]])


print('(d) c_wake1 rabbit, 160^3 grid, cube -1.5..1.5; pieces after bridging gaps of two cells (0.0375)')
N = 160; cell = 3.0 / N; g = (np.arange(N) + 0.5) / N * 3.0 - 1.5; X, Y, Z = np.meshgrid(g, g, g, indexing='ij')
ra = L.rule('along'); r1 = L.rule('oneplane')
for rn in ['alongmem.c_wake1', 'oneplane', 'along']:
    rw = L.rule(rn); ro = L.route(rw, X, Y, Z, c, 120); ins = ro['inside']
    fat = ndimage.binary_dilation(ins, structure=np.ones((3, 3, 3), bool), iterations=1)
    lab, k = ndimage.label(fat, structure=np.ones((3, 3, 3), bool)); lab = np.where(ins, lab, 0)
    sizes = np.array(ndimage.sum(ins, lab, range(1, k + 1))); order = np.argsort(-sizes)
    print('  %-17s inside %d; pieces %d; biggest: %s %%' % (rn, ins.sum(), k, np.round(100 * sizes[order[:6]] / ins.sum(), 2).tolist()))
    if rn != 'alongmem.c_wake1':
        continue
    main = lab == order[0] + 1; dist = ndimage.distance_transform_edt(~main) * cell
    for j in order[1:3]:
        m = lab == j + 1; p = np.stack([X[m], Y[m], Z[m]]); q = one(ra, p); ph = ro['phase'][m]
        d2 = np.sqrt(((q[:, None, :] - flat3.T[:, :, None]) ** 2).sum(0))
        ins1 = M.stay(r1, q[0], q[1], q[2], *c, 120) >= 120
        # which body of the one-plane rabbit does the landing point belong to: its own colour there
        ro1 = L.route(r1, q[0], q[1], q[2], c, 120)
        print('  loose piece: %d blocks = %.1f %% of the shape; middle (%.3f, %.3f, %.3f); x %.2f..%.2f, y %.2f..%.2f, height %.2f..%.2f; gap to the main piece %.3f'
              % (m.sum(), 100 * m.sum() / ins.sum(), *p.mean(1), p[0].min(), p[0].max(), p[1].min(), p[1].max(), np.abs(p[2]).min(), np.abs(p[2]).max(), dist[m].min()))
        print('     its blocks by body colour (the cycle point they sit on at step 120): %s' % {pn[i]: int((ph == i).sum()) for i in range(3)})
        print('     after ONE step of along: middle (%.3f, %.3f, %.3f); height: median %.4f, largest %.4f; all inside the one-plane rabbit: %s; nearest cycle point %s; body colour there %s'
              % (*q.mean(1), np.median(np.abs(q[2])), np.abs(q[2]).max(), bool(ins1.all()), {pn[i]: int((d2.argmin(0) == i).sum()) for i in range(3)}, {pn[i]: int((ro1['phase'] == i).sum()) for i in range(3)}))
        hh = 1e-6; dets = []
        for i in range(0, p.shape[1], max(1, p.shape[1] // 400)):
            v = p[:, i]; P = np.stack([v + hh * e for e in np.eye(3)] + [v - hh * e for e in np.eye(3)]).T; Q = one(ra, P); dets.append(np.linalg.det((Q[:, :3] - Q[:, 3:]) / (2 * hh)))
        dets = np.array(dets); print('     the first step turns space inside out at %.0f %% of its blocks (so the piece is folded double onto the body it jumps into)' % (100 * (dets < 0).mean()))

print('\nSiegel disc: how high above the page are the orbits that stay, as the steps go on (2000 start points that stay 300 steps, heights 0.05 to 0.6)')
cs = L.SIEGEL; rng = np.random.default_rng(8); t0 = time.time()
ccs = complex(cs[0], cs[1]); fix = (1 - np.sqrt(1 - 4 * ccs)) / 2
print('  centre of the flat disc (the flat rule\'s fixed point): (%.4f, %.4f), flat stretch there %.6f' % (fix.real, fix.imag, abs(2 * fix)))
for rn in ['along', 'oneplane', 'alongmem.c_wake1', 'lathe']:
    r = L.rule(rn); p = rng.uniform([-1.2, -1.2, 0.05], [1.2, 1.2, 0.6], size=(60000, 3)).T
    keep = M.stay(r, p[0], p[1], p[2], *cs, 300) >= 300; p = p[:, keep][:, :2000]; n = p.shape[1]
    x, y, z = p[0].copy(), p[1].copy(), p[2].copy(); st = tuple(r.init(n)); cx, cy, cz = (np.full(n, t) for t in cs); marks = {}; alive = np.ones(n, bool)
    rad = []
    for k in range(20000):
        o = r.step(x, y, z, st, k, cx, cy, cz); st = tuple(o[3]); x, y, z = o[0] + cx, o[1] + cy, o[2] + cz
        bad = ~np.isfinite(x) | (x * x + y * y + z * z > 36); alive &= ~bad; x[bad] = 0; y[bad] = 0; z[bad] = 0
        if k + 1 in (10, 30, 100, 300, 1000, 3000, 10000, 20000):
            marks[k + 1] = float(np.median(np.abs(z[alive])))
        if k >= 19900:
            rad.append(np.hypot(x - fix.real, y - fix.imag))
    rad = np.stack(rad); lo, hi = rad.min(0)[alive], rad.max(0)[alive]
    print('  %-17s %d start points (median start height %.2f), %d left after 20000 steps; median height after n steps: %s' % (rn, n, np.median(p[2]), alive.sum(), ', '.join('%d: %.1e' % (a, b) for a, b in marks.items())))
    print('      their last 100 points keep a distance from the centre of the flat disc between (median) %.3f and %.3f; share that have shrunk onto the centre (within 0.01): %.1f %%   (%.0f s)'
          % (np.median(lo), np.median(hi), 100 * (hi < 0.01).mean(), time.time() - t0)); sys.stdout.flush()
