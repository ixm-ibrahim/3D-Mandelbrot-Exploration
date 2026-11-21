"""The mechanics, in numbers (rabbit):
  (a) the push straight up above the meeting point of the three bodies, height by height
  (b) the resting places off the page (points that one step puts back where they were) and their three stretches
  (c) the places that one step of along throws onto each point of the flat cycle
  (d) c_wake1's loose bodies: where one step puts their points
  (e) the three pages that do not hold c: is their picture the flat rabbit?
    python out/r22/lump/measure2.py   -> prints (kept as measure2.txt by the caller)"""
import sys, time
import numpy as np
from scipy import ndimage
import lumplib as L
M = L.M

c = L.RABBIT; cc = complex(c[0], c[1])
alpha = (1 - np.sqrt(1 - 4 * cc)) / 2                       # the fixed point where the three bodies meet
PIN = (alpha.real, alpha.imag, 0.0)
print('meeting point of the three bodies (fixed point of the flat rule): (%.4f, %.4f, 0), flat stretch there |2 alpha| = %.4f' % (PIN[0], PIN[1], abs(2 * alpha)))


def one(r, p, k=0):
    """One step (square, add c) of the points p (3, n)."""
    n = p.shape[1]; o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), k, np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
    return np.stack([o[0] + c[0], o[1] + c[1], o[2] + c[2]])


def jac(r, v, h=1e-6):
    v = np.asarray(v, float); P = np.stack([v + h * e for e in np.eye(3)] + [v - h * e for e in np.eye(3)]).T
    Q = one(r, P); return (Q[:, :3] - Q[:, 3:]) / (2 * h)       # columns = d/dx, d/dy, d/dz


def newton(r, v, target=None, it=60):
    v = np.array(v, float)
    for _ in range(it):
        F = one(r, v[:, None])[:, 0] - (v if target is None else np.asarray(target))
        A = jac(r, v) - (np.eye(3) if target is None else 0)
        try:
            dv = np.linalg.solve(A, F)
        except np.linalg.LinAlgError:
            return None
        s = min(1.0, 0.3 / max(np.linalg.norm(dv), 1e-12)); v = v - s * dv
        if np.linalg.norm(dv) < 1e-13:
            break
    F = one(r, v[:, None])[:, 0] - (v if target is None else np.asarray(target))
    return v if np.linalg.norm(F) < 1e-9 else None


RN = ['along', 'oneplane', 'lathe']; RU = {n: L.rule(n) for n in RN}
print('\n(a) a point straight above the meeting point: its height after one step / before, and is it in the shape (200 steps)?')
hs = np.array([0.005, 0.02, 0.04, 0.06, 0.075, 0.09, 0.12, 0.16, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
P = np.stack([np.full(hs.size, PIN[0]), np.full(hs.size, PIN[1]), hs])
for n in RN:
    q = one(RU[n], P); ins = M.stay(RU[n], P[0], P[1], P[2], *c, 200) >= 200
    print('  %-9s' % n, ' '.join('%.3f:%+.2f%s' % (h, a, '*' if i else ' ') for h, a, i in zip(hs, q[2] / hs, ins)), '   (* = stays)')
# how much of a small upright disc through the meeting point (across the page) is inside, by height band
for n in RN + ['alongmem.c_wake1']:
    r = L.rule(n); rng = np.random.default_rng(4); m = 40000
    p = np.stack([PIN[0] + rng.uniform(-0.1, 0.1, m), PIN[1] + rng.uniform(-0.1, 0.1, m), rng.uniform(0.0, 0.3, m)])
    ins = M.stay(r, p[0], p[1], p[2], *c, 200) >= 200
    print('  %-17s share inside in a box 0.2 wide round the meeting point, by height: ' % n + ', '.join('%.2f-%.2f: %4.1f %%' % (a, b, 100 * ins[(p[2] >= a) & (p[2] < b)].mean()) for a, b in ((0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3))))

print('\n(b) resting places off the page (one step puts the point back on itself), searched from 4000 random starts')
for n in RN:
    r = RU[n]; rng = np.random.default_rng(11); found = []
    for s in rng.uniform([-1.2, -1.2, 0.02], [1.2, 1.2, 1.0], size=(4000 if n == 'along' else 1500, 3)):
        v = newton(r, s)
        if v is not None and abs(v[2]) > 1e-6 and np.linalg.norm(v) < 3 and not any(np.linalg.norm(v - w) < 1e-6 for w in found):
            found.append(v)
    print('  %-9s %d found' % (n, len(found)))
    for v in sorted(found, key=lambda w: w[2]):
        ev = np.linalg.eigvals(jac(r, v)); ins = M.stay(r, v[0], v[1], v[2], *c, 300) >= 300
        print('     (%.4f, %.4f, %.4f)  stretches %s  det %+.3f  distance from the meeting point %.3f  %s'
              % (v[0], v[1], v[2], ' '.join('%.3f' % abs(e) for e in sorted(ev, key=abs)), np.linalg.det(jac(r, v)), np.linalg.norm(v - np.array(PIN)), 'stays' if ins else 'leaves'))

print('\n(c) places that ONE step throws exactly onto a point of the flat cycle (the flat rule has two each: v and -v)')
cyc = [0j, cc, cc * cc + cc]; names = ['0', 'c', 'c^2+c']
for n in ['along', 'oneplane']:
    r = RU[n]
    for w, nm in zip(cyc, names):
        tgt = np.array([w.real, w.imag, 0.0]); rng = np.random.default_rng(5); found = []
        for s in rng.uniform([-1.3, -1.3, -1.3], [1.3, 1.3, 1.3], size=(3000, 3)):
            v = newton(r, s, target=tgt)
            if v is not None and np.linalg.norm(v) < 3 and not any(np.linalg.norm(v - u) < 1e-5 for u in found):
                found.append(v)
        print('  %-9s onto %-6s: %d places: %s' % (n, nm, len(found), '; '.join('(%.3f, %.3f, %.3f) det %+.2f' % (v[0], v[1], v[2], np.linalg.det(jac(r, v))) for v in sorted(found, key=lambda u: abs(u[2])))))

print('\n(d) c_wake1: its pieces on a 160^3 grid, and where ONE step puts the points of the loose ones')
N = 160; g = (np.arange(N) + 0.5) / N * 3.0 - 1.5; X, Y, Z = np.meshgrid(g, g, g, indexing='ij')
rw = L.rule('alongmem.c_wake1'); ro = L.route(rw, X, Y, Z, c, 120); ins = ro['inside']
lab, k = ndimage.label(ins); sizes = ndimage.sum(ins, lab, range(1, k + 1)); order = np.argsort(-sizes)
print('  inside %d, pieces %d; biggest five: %s %%' % (ins.sum(), k, np.round(100 * sizes[order[:5]] / ins.sum(), 2).tolist()))
ra = RU['along']; r1 = RU['oneplane']
flat3 = np.array([[w.real, w.imag, 0.0] for w in cyc])
for j in order[1:3]:
    m = lab == j + 1; p = np.stack([X[m], Y[m], Z[m]]); q = one(ra, p)
    ph = ro['phase'][m]; pts = L.flat_cycle(c); pn = ['c', 'c^2+c', '0']
    d2 = np.sqrt(((q[:, None, :] - flat3.T[:, :, None]) ** 2).sum(0))             # (3 cycle points, n)
    dets = np.array([np.linalg.det(jac(ra, p[:, i])) for i in range(0, p.shape[1], max(1, p.shape[1] // 300))])
    print('  loose piece: %d blocks (%.1f %%), middle (%.3f, %.3f, %.3f), height %.2f..%.2f' % (m.sum(), 100 * m.sum() / ins.sum(), *p.mean(1), np.abs(p[2]).min(), np.abs(p[2]).max()))
    print('     after one step: middle (%.3f, %.3f, %.3f), height %.4f..%.4f (median %.4f); nearest cycle point: %s' % (*q.mean(1), np.abs(q[2]).min(), np.abs(q[2]).max(), np.median(np.abs(q[2])),
          {names[i]: int((d2.argmin(0) == i).sum()) for i in range(3)}))
    print('     body colour of its blocks (cycle point the orbit sits on at step 120): %s; along turns space inside out at %.0f %% of its blocks' % ({pn[i]: int((ph == i).sum()) for i in range(3)}, 100 * (dets < 0).mean()))
    # is the landing place inside the one-plane rabbit (it must be), and in which flat body: follow the flat rule from the landing point's shadow
main = lab == order[0] + 1
dist = ndimage.distance_transform_edt(~main) * (3.0 / N)
for j in order[1:3]:
    m = lab == j + 1; print('  gap from this loose piece to the main piece: %.3f' % dist[m].min())

print('\n(e) the three pages that do not hold c: along\'s cut against the flat rabbit drawn in that page (as if c lay in it)')
W, H = 360, 260; u, s = np.meshgrid(np.linspace(-1.8, 1.8, W), np.linspace(1.3, -1.3, H))
flat = M.flat_stay(u, s, c[0], c[1], 120) >= 120
for cname, cset in (('rabbit', c), ('basilica', L.CSETS['basilica'])):
    fl = M.flat_stay(u, s, cset[0], cset[1], 120) >= 120
    for ang in (0.0, 45.0, 90.0, 135.0):
        a = np.radians(ang); cut = M.stay(ra, u, s * np.cos(a), s * np.sin(a), *cset, 120) >= 120
        print('  %-8s page at %5.1f: flat picture %5d places, along\'s cut %5d, both %5d; differ %5d (%.1f %% of the flat picture)' % (cname, ang, fl.sum(), cut.sum(), (fl & cut).sum(), (fl != cut).sum(), 100.0 * (fl != cut).sum() / fl.sum()))
# one step from the upright page: how far from the page do the points land, and how far from the flat page
rng = np.random.default_rng(2); m = 20000
for ang in (45.0, 90.0, 135.0):
    a = np.radians(ang); xx = rng.uniform(-1, 1, m); ss = rng.uniform(-1, 1, m); p = np.stack([xx, ss * np.cos(a), ss * np.sin(a)])
    q = one(ra, p); off_own = np.abs(-np.sin(a) * q[1] + np.cos(a) * q[2]); sq = q - np.array(c)[:, None]; off_before = np.abs(-np.sin(a) * sq[1] + np.cos(a) * sq[2])
    print('  page at %5.1f: after squaring the points are still in their page (largest distance %.1e); adding c moves every one %.3f out of it' % (ang, off_before.max(), np.median(off_own)))
