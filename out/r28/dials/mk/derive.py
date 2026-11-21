"""Round 28, Track A, builder: every line of the derivation in ROUND28.md section 1.3, checked with numbers.

  PYTHONIOENCODING=utf-8 python -W ignore out/r28/dials/mk/derive.py [quick]   -> out/r28/dials/logs/derive.txt

For each setting (rho, p, grid) a LIST OF BALLS of one cell is made (kit28.cell_balls) and the lines are tested:
  0  the list itself: the recipe's verdict against "lies in a listed ball" at random points of the cell
  1  the scale factor of the second inversion (DF) and W: against finite differences and a far point carried along
  2  the two fixed points and H_B, H_T
  3  the hull balls: every listed ball lies in the hull at a whole number or in "the rest"
  4  the rest: how high the balls outside the whole-number hulls really reach, against H_B / 2, / 3, / 4 and rho^2 H_T
  5  the spindle: no listed ball reaches into it, every point in it is OUTSIDE by the recipe, it stays in the middle cell
  6  where the chain ends
  7  the room: at points the recipe calls OUTSIDE, never longer than the distance to the nearest listed ball
  8  the whole estimate in the picture: never longer than the distance to the nearest ball of the picture's list
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit28 as K

OUT = os.path.join(os.path.dirname(HERE), 'logs'); os.makedirs(OUT, exist_ok=True)
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'
GN = ['square', 'honeycomb', 'line']
# (rho, p, grid, rmin)
SET = [
    (1.0, 55.5556, 0, 1.5e-3), (1.0, 90.0, 0, 2.5e-3), (1.0, 55.5556, 1, 1.5e-3), (1.0, 55.5556, 2, 2e-4),
    (0.5, 150.0, 0, 1.5e-3), (0.5, 150.0, 1, 1.5e-3), (0.5, 150.0, 2, 2e-4), (0.5, 190.0, 0, 3e-3), (0.5, 60.0, 0, 1.5e-3),
    (1 / 3.0, 150.0, 0, 1.5e-3), (1 / 3.0, 150.0, 1, 1.5e-3), (1 / 3.0, 150.0, 2, 2e-4),
    (0.25, 300.0, 0, 2e-3), (0.25, 300.0, 1, 2e-3), (0.25, 300.0, 2, 2e-4), (0.25, 390.0, 0, 3e-3),
    (1 / 6.0, 300.0, 0, 1.5e-3), (1 / 6.0, 300.0, 1, 1.5e-3), (0.125, 400.0, 0, 1.5e-3), (0.2, 30.0, 0, 1.5e-3),
    (0.05, 1000.0, 0, 1.5e-3), (0.025, 2000.0, 0, 1.5e-3), (0.05, 1900.0, 1, 3e-3), (0.35, 250.0, 0, 2e-3), (0.45, 215.0, 2, 3e-4),
]
if QUICK:
    SET = [SET[0], SET[4], SET[9], SET[12], SET[16]]
rng = np.random.default_rng(20261120)
lines = []


def say(s=''):
    print(s); lines.append(s); sys.stdout.flush()


def neighbours(A, grid, R=2):
    """The balls A and their slid copies by the whole numbers within R."""
    off = np.arange(-R - 1, R + 2)
    if grid == 2:
        a = off; b = np.zeros_like(off)
    else:
        a, b = np.meshgrid(off, off); a = a.ravel(); b = b.ravel()
    nx, ny = K.lat(grid, a.astype(float), b.astype(float)); keep = nx * nx + ny * ny <= R * R + 1e-9
    nx, ny = nx[keep], ny[keep]
    out = np.repeat(A[None], len(nx), 0).copy(); out[:, :, 0] += nx[:, None]; out[:, :, 1] += ny[:, None]
    return out.reshape(-1, 4)


def nearest(P, B, chunk=400):
    """For points P (N, 3) and balls B (M, 4): the smallest of |P - c| - r. The large balls one by one; the small ones
    through a tree of their centres, in classes of like radius (the eight nearest centres of each class are measured:
    a ball further off than those is never the nearest by more than the spread of the class, and any value found is the
    distance to a real ball, so "longer than this" is always a true finding)."""
    from scipy.spatial import cKDTree
    out = np.full(len(P), np.inf)
    big = B[:, 3] >= 0.05
    Bb = B[big]
    for s in range(0, len(P), chunk):
        q = P[s:s + chunk]
        if len(Bb):
            d = np.sqrt(((q[:, None, :] - Bb[None, :, :3]) ** 2).sum(2)) - Bb[None, :, 3]
            out[s:s + chunk] = d.min(1)
    Bs = B[~big]
    if len(Bs):
        cls = np.floor(np.log(Bs[:, 3]) / np.log(1.5)).astype(int)
        for c in np.unique(cls):
            G = Bs[cls == c]; k = min(8, len(G)); tr = cKDTree(G[:, :3])
            d, i = tr.query(P, k=k)
            d = d.reshape(len(P), k) - G[i.reshape(len(P), k), 3]
            out = np.minimum(out, d.min(1))
    return out


def cell_points(n, top, grid):
    """Random points of the middle cell, between the walls."""
    if grid == 1:
        x = rng.uniform(-0.7, 0.7, 3 * n); y = rng.uniform(-0.7, 0.7, 3 * n)
        nx, ny = K.near(1, x, y); k = (nx == 0) & (ny == 0); x, y = x[k][:n], y[k][:n]
    elif grid == 2:
        x = rng.uniform(-0.5, 0.5, n); y = rng.uniform(-1.5, 1.5, n)
    else:
        x = rng.uniform(-0.5, 0.5, n); y = rng.uniform(-0.5, 0.5, n)
    return x, y, rng.uniform(0, top, len(x))


t00 = time.time()
bad_total = 0
for rho, p, grid, rmin in SET:
    top = 1 + 100.0 / p; t = top / 2; h = K.hulls(top, rho); HB, HT = h['HB'], h['HT']
    say('=== second sphere %.4g %% of the first, neighbours %.6g %% (top = %.6f, t = %.6f), %s grid; list down to radius %g' % (100 * rho, p, top, t, GN[grid], rmin))
    t0 = time.time(); A1, A2 = K.cell_balls(top, rho, grid, rmin); A = np.concatenate([A1, A2])
    say('    the list: %d balls inside the first sphere, %d inside the second (%.1f s)' % (len(A1), len(A2), time.time() - t0))
    AN = neighbours(A, grid, 2)

    # 0. the list against the recipe
    x, y, z = cell_points(20000, top, grid); P = np.column_stack([x, y, z])
    v = K.recipe_m(x, y, z, top, rho, grid, 400)
    inlist = nearest(P, AN) < 0
    a = int((inlist & (v == 0)).sum()); b = int((~inlist & (v == 1)).sum()); und = int((v < 0).sum())
    # a point the recipe calls inside but no listed ball holds: it must be in a ball below the cut, so close to a listed ball
    say('  0 list against recipe, %d points of the cell: in a listed ball but OUTSIDE by the recipe %d; INSIDE by the recipe but in no listed ball %d (balls below the cut); undecided after 400 rounds %d' % (len(x), a, b, und))
    bad_total += a

    # 1. DF and W, by finite differences along the chain of moves of each point
    n1 = 4000; px = rng.uniform(-2.6, 2.6, n1); py = rng.uniform(-1.6, 1.6, n1); pz = rng.uniform(-1.6, 1.6, n1)
    worstDF = 0.0; worstW = 0.0; used2 = 0
    for i in range(0, n1, 40):
        pt = np.array([px[i], py[i], pz[i]]); u = np.array([pt[1], pt[2], pt[0] - K.K2 / 2]); d2 = u @ u
        moves = []; DF = K.K2 / d2; m = np.array([0, 0, 1.0]) + DF * u; W = np.array([0, 0, 1.0]); ok = True
        for _ in range(40):
            if m[2] < 0 or m[2] > top:
                break
            nx, ny = K.near(grid, np.array([m[0]]), np.array([m[1]])); n = np.array([nx[0], ny[0], 0.0]); m = m - n; W = W - n; moves.append(('s', n))
            mt = m - np.array([0, 0, top]); Wt = W - np.array([0, 0, top])
            if m @ m < 1:
                s = 1 / (m @ m); m = m * s; W = W / (W @ W); DF *= s; moves.append(('1',))
            elif mt @ mt < rho * rho:
                s = rho * rho / (mt @ mt); m = np.array([0, 0, top]) + mt * s; W = np.array([0, 0, top]) + rho * rho * Wt / (Wt @ Wt); DF *= s; moves.append(('2',)); used2 += 1
            else:
                break

        def carry(q):
            uu = np.array([q[1], q[2], q[0] - K.K2 / 2]); mm = np.array([0, 0, 1.0]) + K.K2 * uu / (uu @ uu)
            for mv in moves:
                if mv[0] == 's':
                    mm = mm - mv[1]
                elif mv[0] == '1':
                    mm = mm / (mm @ mm)
                else:
                    w = mm - np.array([0, 0, top]); mm = np.array([0, 0, top]) + rho * rho * w / (w @ w)
            return mm
        eps = 1e-6 * min(1.0, 1 / max(DF, 1e-9))
        num = np.mean([np.linalg.norm(carry(pt + eps * e) - carry(pt - eps * e)) / (2 * eps) for e in np.eye(3)])
        worstDF = max(worstDF, abs(num / DF - 1))
        Winf = carry(np.array([3e9, 4e9, 5e9]))          # a point far out in the picture, carried along the same chain
        worstW = max(worstW, np.linalg.norm(Winf - W) / max(1.0, np.linalg.norm(W)))
    say('  1 scale factor: %d chains (%d steps through the second sphere): DF against finite differences, worst relative error %.2e; W against a far point carried along, worst %.2e' % (n1 // 40, used2, worstDF, worstW))
    if worstDF > 1e-4 or worstW > 1e-6:
        bad_total += 1

    # 2. the fixed points
    z1, z2 = h['z1'], h['z2']
    s1 = lambda zz: 1 / zz
    s2 = lambda zz: top + rho * rho / (zz - top)
    e2 = max(abs(s2(s1(z1)) - z1), abs(s2(s1(z2)) - z2), abs(s1(z1) - z2), abs(s2(z1) - z2), abs(HB - 1 / (top - HT)), abs(HT - rho * rho / (top - HB)), abs(HT - (top - z2)))
    say('  2 fixed points z1 = %.9f, z2 = %.9f; H_B = %.9f, H_T = %.9f; worst error of the seven equations %.2e' % (z1, z2, HB, HT, e2))
    if e2 > 1e-9:
        bad_total += 1

    # 3 / 4. the hulls and the rest
    rB, rT = K.rests(top, rho, grid); tol = 1e-9
    def in_ball(Bs, c, r):
        return np.sqrt(((Bs[:, :3] - c) ** 2).sum(1)) + Bs[:, 3] <= r + tol
    in1 = in_ball(A1, np.array([0, 0, HB / 2]), HB / 2); in2 = in_ball(A2, np.array([0, 0, top - HT / 2]), HT / 2)
    if grid == 2:
        h1 = np.hypot(A1[:, 1], A1[:, 2]) + A1[:, 3]; h2 = np.hypot(A2[:, 1], top - A2[:, 2]) + A2[:, 3]
    else:
        h1 = A1[:, 2] + A1[:, 3]; h2 = top - A2[:, 2] + A2[:, 3]
    o1 = ~in1; o2 = ~in2
    v1 = int((o1 & (h1 > rB + tol)).sum()); v2 = int((o2 & (h2 > rT + tol)).sum())
    top1 = (A1[:, 2] + A1[:, 3]).max(); top2 = (top - A2[:, 2] + A2[:, 3]).max()
    say('  3 hull balls: highest point of anything on the bottom wall %.6f (H_B %.6f), deepest of anything on the top wall %.6f (H_T %.6f); balls outside the whole-number hull AND outside the rest: bottom %d, top %d'
        % (top1, HB, top2, HT, v1, v2))
    say('  4 the rest: balls outside the whole-number hulls reach %.6f on the bottom (allowed %.6f = H_B * %.4f; they use %.1f %% of it) and %.6f on the top (allowed %.6f; they use %.1f %% of it)'
        % (h1[o1].max() if o1.any() else 0, rB, rB / HB, 100 * (h1[o1].max() if o1.any() else 0) / rB, h2[o2].max() if o2.any() else 0, rT, 100 * (h2[o2].max() if o2.any() else 0) / rT))
    if top1 > HB + 1e-9 or top2 > HT + 1e-9 or v1 or v2:
        bad_total += 1; say('    *** A HULL LINE FAILS HERE')
    if rho < 1:
        # 4b (the builder's own line): the balls on the top wall outside the whole-number hull keep within top_ball of the second sphere's centre
        rTb = K.top_ball(top, rho, grid); far2 = np.sqrt(A2[:, 0] ** 2 + A2[:, 1] ** 2 + (top - A2[:, 2]) ** 2) + A2[:, 3]
        say('  4b the rest on the top wall keeps within %.6f of the centre of the second sphere (its radius is %.6f): the balls outside the whole-number hull reach %.6f from it (%d of them go further)'
            % (rTb, rho, far2[o2].max() if o2.any() else 0, int((far2[o2] > rTb + tol).sum()) if o2.any() else 0))
        if o2.any() and (far2[o2] > rTb + tol).any():
            bad_total += 1; say('    *** THE BALL ROUND THE REST FAILS HERE')

    # 5. the spindle: as the brief has it (reach 1/2 at mid-height), and as built (reach w = min(1/2, top - zm + rho))
    for brief in (True, False):
        hh = K.hulls(top, rho, brief); d2 = hh['d2']; zm = hh['zm']; a = hh['a']; Rs = hh['R']; w = hh['w']
        if brief and abs(w - K.hulls(top, rho)['w']) < 1e-15:
            continue                                          # the two are the same spindle here
        # (i) random points in it, by the recipe. In the half-plane (distance from the line, height) it is the part of
        #     the disc of radius Rs about (a, zm) with distance >= 0; for a > 0 it bulges past z1 and z2 off the line.
        ns = 60000; zz = rng.uniform(zm - Rs, zm + Rs, 6 * ns); rr = rng.uniform(0, w, 6 * ns); ang = rng.uniform(0, 2 * np.pi, 6 * ns)
        ins = np.hypot(rr - a, zz - zm) < Rs * (1 - 1e-9); zz, rr, ang = zz[ins][:ns], rr[ins][:ns], ang[ins][:ns]
        vs = K.recipe_m(rr * np.cos(ang), rr * np.sin(ang), zz, top, rho, grid, 3000)
        # (ii) points inside every listed ball that comes near it: are any of them in the spindle?
        rc = np.hypot(AN[:, 0], AN[:, 1]); dc = np.minimum(np.hypot(rc - a, AN[:, 2] - zm), np.hypot(-rc - a, AN[:, 2] - zm)) - Rs - AN[:, 3]
        cand = np.nonzero(dc < 1e-9)[0]; hit = 0; deepest = 0.0
        for k in cand[:400]:
            q = rng.normal(size=(1500, 3)); q = q / np.linalg.norm(q, axis=1)[:, None] * (AN[k, 3] * rng.uniform(0, 1, 1500)[:, None] ** (1 / 3)) + AN[k, :3]
            depth = Rs - np.hypot(np.hypot(q[:, 0], q[:, 1]) - a, q[:, 2] - zm)
            hit += int((depth > 1e-12).sum()); deepest = max(deepest, float(depth.max()))
        lo_, hi_ = (zm - Rs, zm + Rs) if a > 0 else (hh['z1'], hh['z2'])
        say('  5 spindle %s (reach %.6f at mid-height zm = %.6f, delta^2 = %.6g; it spans heights %.6f to %.6f, the walls are at 0 and %.6f): of %d random points in it the recipe calls INSIDE %d, undecided after 3000 rounds %d; listed balls that come near it %d, of 1500 points in each the number that lie in the spindle %d (deepest %.3e)'
            % ('as the brief has it' if brief else 'as built', w, zm, d2, lo_, hi_, top, len(zz), int((vs == 1).sum()), int((vs < 0).sum()), len(cand), hit, max(deepest, 0)))
        if (vs == 1).any() or hit:
            if brief:
                say('    (the spindle as the brief has it fails here: it is not used)')
            else:
                bad_total += 1; say('    *** THE SPINDLE LINE FAILS HERE')

    # 6. where the chain ends
    rpic = 2e-3
    B = K.picture_balls(A1, A2, grid, rpic, top)
    ext = float((np.abs(B[:, 0]) + B[:, 3]).max()); rc_ = K.reach(top, rho)
    ymax = float((np.hypot(B[:, 1], B[:, 2]) + B[:, 3]).max())
    say('  6 chain end: the picture\'s list (%d balls, radius >= %g) reaches |x| = %.5f; the formula says %.5f; furthest from the middle line %.5f (the neighbour alone: %.5f)' % (len(B), rpic, ext, rc_, ymax, K.K2 * p / 200))
    if ext > rc_ + 1e-9:
        bad_total += 1; say('    *** THE CHAIN REACHES PAST THE FORMULA')

    # 7. the room in the object's own space
    x, y, z = cell_points(60000, top, grid)
    outm = (x * x + y * y + z * z >= 1) & (x * x + y * y + (z - top) ** 2 >= rho * rho); x, y, z = x[outm][:20000], y[outm][:20000], z[outm][:20000]
    e = K.room_m(x, y, z, top, rho, grid); e0 = K.room_m(x, y, z, top, rho, grid, spindle=False); eb = K.room_m(x, y, z, top, rho, grid, brief=True)
    dtrue = nearest(np.column_stack([x, y, z]), AN)
    over = e - dtrue; nb = int((over > 1e-9).sum())
    ratio = np.median(e[dtrue > 0] / dtrue[dtrue > 0])
    say('  7 room at %d OUTSIDE points of the cell: longer than the distance to the nearest listed ball at %d (worst excess %.3e); median of room / true distance %.2f; the spindle is the larger room at %d points'
        % (len(x), nb, float(over.max()), ratio, int((e > e0 + 1e-12).sum())))
    if nb:
        bad_total += 1; say('    *** THE ROOM IS TOO LONG SOMEWHERE')
    nbb = int((eb - dtrue > 1e-9).sum())
    if nbb:
        say('    (with the spindle as the brief has it the room would be too long at %d of these points, by up to %.3e)' % (nbb, float((eb - dtrue).max())))

    # 8. the estimate in the picture
    rx = min(rc_ if np.isfinite(rc_) else 6, 8) + 0.6; ry = K.K2 * max(1.0, p / 100) / 2 + 0.8
    n8 = 20000 if not QUICK else 6000
    q = np.column_stack([rng.uniform(-rx, rx, n8), rng.uniform(-ry, ry, n8), rng.uniform(-ry, ry, n8)])
    best, free, st = K.estimate(q[:, 0], q[:, 1], q[:, 2], t, rho, grid, 60)
    est = np.where(st == 0, np.minimum(best, free), best)
    dpic = nearest(q, B, 200)
    o = st == 0; over = est[o] - dpic[o]; nb = int((over > 1e-7).sum())
    # verdicts: the search's inside against the list
    ins_search = st == 1; ins_list = dpic < 0
    say('  8 estimate at %d picture points (%d OUTSIDE by the search): longer than the distance to the nearest listed ball at %d (worst excess %.3e); median of estimate / true distance %.2f; "best" alone would be too long at %d points; inside by the search but in no listed ball %d, in a listed ball but outside by the search %d'
        % (n8, int(o.sum()), nb, float(over.max()) if o.any() else 0, float(np.median(est[o] / np.maximum(dpic[o], 1e-12))), int((best[o] - dpic[o] > 1e-7).sum()), int((ins_search & ~ins_list).sum()), int((ins_list & (st == 0)).sum())))
    if nb or (ins_list & (st == 0)).any():
        bad_total += 1; say('    *** THE ESTIMATE IS TOO LONG SOMEWHERE')
    say()
say('lines that failed somewhere: %d. Total time %.0f s.' % (bad_total, time.time() - t00))
with open(os.path.join(OUT, 'derive-quick.txt' if QUICK else 'derive.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
