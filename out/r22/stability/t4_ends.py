"""t4: where do the bounded orbits END, and are there cycles off the flat page? python out/r22/stability/t4_ends.py > t4_ends.txt
For each rule and c: random start points in the box, 400 steps (the library's rule functions; positions are kept, which
M.stay does not do). Orbits still inside are sorted:
  flat cycle      : ended within 1e-6 of the flat picture's attracting cycle
  other cycle     : repeats after p <= 64 steps to 1e-8, not the flat cycle; split by on / off the flat page (|z| > 1e-6)
  no cycle        : does not repeat; split by on / off the page
For each off-page cycle found: its points, and the three stretches of one full turn (all under 1 = it pulls from every side).
Also: how close along's step is to the lathe's and to one-plane's (the turn between the two images, seen from 0)."""
import sys
import numpy as np
import stab as T
M = T.M

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000; STEPS = 400
SETS = [('basilica', T.BAS, 2), ('San Marco', T.MARCO, 1), ('c=-1+0.03i', (-1.0, 0.03, 0.0), 2), ('c=-1+0.1i', (-1.0, 0.1, 0.0), 2), ('c=-1+0.2i', (-1.0, 0.2, 0.0), 2),
        ('rabbit', T.RABBIT, 3), ('Siegel', T.SIEGEL, 0)]


def flat_cycle(c, p):
    z = 0j; cc = complex(c[0], c[1])
    for _ in range(20000):
        z = z * z + cc
    pts = [z]
    for _ in range(max(p, 1) - 1):
        pts.append(pts[-1] ** 2 + cc)
    return np.array(pts)


def run(F, v, c, steps):
    x, y, z = v
    for _ in range(steps):
        X, Y, Z = F(x, y, z); x, y, z = X + c[0], Y + c[1], Z + c[2]
        far = x * x + y * y + z * z > 36.0
        x, y, z = np.where(far, 1e3, x), np.where(far, 1e3, y), np.where(far, 1e3, z)     # parked far away: never comes back
    return x, y, z


print('== how close is along to the lathe, and to one-plane? turn between the two images of the same point (degrees), 400,000 random points in the cube -1.5..1.5')
rng = np.random.default_rng(11); P = rng.uniform(-1.5, 1.5, size=(400000, 3)); x, y, z = P.T
img = {nm: np.stack(T.rule(nm)(x, y, z), -1) for nm in T.NAMES}
for a, b in (('along', 'lathe'), ('along', 'oneplane'), ('oneplane', 'lathe'), ('away', 'lathe'), ('away', 'oneplane')):
    cs = (img[a] * img[b]).sum(-1) / (np.linalg.norm(img[a], axis=1) * np.linalg.norm(img[b], axis=1))
    ang = np.degrees(np.arccos(np.clip(cs, -1, 1)))
    print('  %-8s against %-8s: median %.1f, 90th pct %.1f, max %.1f | left half (x < 0): median %.1f, max %.1f | right half: median %.1f, max %.1f'
          % (a, b, np.median(ang), np.percentile(ang, 90), ang.max(), np.median(ang[x < 0]), ang[x < 0].max(), np.median(ang[x > 0]), ang[x > 0].max()))

rng = np.random.default_rng(5)
V = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(N, 3))
for label, c, p in SETS:
    cyc = flat_cycle(c, p) if p else None
    for nm in ('oneplane', 'along', 'lathe', 'away'):
        F = T.rule(nm)
        x, y, z = run(F, (V[:, 0].copy(), V[:, 1].copy(), V[:, 2].copy()), c, STEPS)
        ins = x * x + y * y + z * z < 36.0; x, y, z = x[ins], y[ins], z[ins]; n = ins.sum()
        # period
        px, py, pz = x.copy(), y.copy(), z.copy(); per = np.zeros(n, int)
        for k in range(1, 65):
            X, Y, Z = F(px, py, pz); px, py, pz = X + c[0], Y + c[1], Z + c[2]
            hit = (per == 0) & (np.sqrt((px - x) ** 2 + (py - y) ** 2 + (pz - z) ** 2) < 1e-8); per[hit] = k
        if cyc is not None:
            dflat = np.min(np.abs((x + 1j * y)[:, None] - cyc[None, :]), axis=1); onflat = (dflat < 1e-6) & (np.abs(z) < 1e-6)
        else:
            onflat = np.zeros(n, bool)
        off = np.abs(z) > 1e-6
        other = (per > 0) & ~onflat; noc = (per == 0) & ~onflat
        print('\n%-11s %-9s inside after %d steps: %6d of %d (%.2f %%). flat cycle %5.1f %% | other cycle: on page %5.2f %%, OFF page %5.2f %% | no cycle: on page (|z| < 1e-6) %5.2f %%, OFF page %5.2f %%'
              % (label, nm, STEPS, n, N, 100 * n / N, 100 * onflat.mean() if n else 0, 100 * (other & ~off).mean() if n else 0, 100 * (other & off).mean() if n else 0,
                 100 * (noc & ~off).mean() if n else 0, 100 * (noc & off).mean() if n else 0))
        sel = other & off
        if sel.any():
            # group the off-page cycles by period and by their largest |z|, print each kind once
            keys = {}
            for i in np.flatnonzero(sel)[:4000]:
                k = (per[i],); keys.setdefault(k, []).append(i)
            for k, ids in sorted(keys.items()):
                i = ids[0]; q = (np.array([x[i]]), np.array([y[i]]), np.array([z[i]]))
                oj = T.orbit_jac(F, *q, c, k[0]); A = oj[-1][1][0]; s = np.linalg.svd(A, compute_uv=False); ev = np.abs(np.linalg.eigvals(A))
                pts = [(x[i], y[i], z[i])] + [(float(o[0][0][0]), float(o[0][1][0]), float(o[0][2][0])) for o in oj[:-1]]
                print('    off-page cycle of %d (%d orbits end on cycles of this length): points %s | one full turn: eigenvalues %s'
                      % (k[0], len(ids), ' '.join('(%.3f, %.3f, %.3f)' % q for q in pts[:6]), ' '.join('%.3g' % e for e in sorted(ev))))
        sel = noc & off
        if sel.any():
            az = np.abs(z[sel]); rho = np.hypot(y[sel], z[sel])
            print('    no cycle, off page: |z| median %.3g, 10th..90th pct %.3g..%.3g; distance from the x-axis median %.3g' % (np.median(az), np.percentile(az, 10), np.percentile(az, 90), np.median(rho)))
        sys.stdout.flush()
