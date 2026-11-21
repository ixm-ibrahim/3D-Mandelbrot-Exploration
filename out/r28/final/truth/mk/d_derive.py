"""Round 28, truth checker: section 1.3 (the distance the ray marcher is given), line by line, against my lists of balls.

  python out/r28/final/truth/mk/d_derive.py      -> out/r28/final/truth/logs/d_derive.txt

No browser. For each setting (rho, p, grid) my list of balls (tkit.build) is sorted into what grows on the bottom wall
and what hangs from the top wall (a ball inside a copy of the second sphere), and each line of 1.3 is put to it:

 fixed points  HB = z1 and HT = top - z2: no listed ball on the bottom wall reaches higher than HB, none on the top
               wall hangs lower than HT, and the highest / lowest come close to them.
 hull balls    every listed ball lies in the ball of diameter HB standing on the bottom wall at its nearest whole
               number, or in the ball of diameter HT hanging from the top wall there, or belongs to "the rest".
 the rest      bottom: within HB / 2 (square), HB / 3 (honeycomb) of the wall, within HB / 4 of the line (line grid).
               top: within rho^2 HT of the wall (of the line), for all three grids.
 bare wall     (the builder's own line) the rest on the top wall keeps within rT = min(rho, x + rho^2 HT) of the second
               sphere's centre, x = (1 - sqrt(1 - 4 rho^2)) / 2.
 spindle       AS WRITTEN in 1.3 (reach 1/2 at mid-height): does a listed ball, or the top wall, reach into it?
               AS BUILT (reach w = min(1/2, top - zm + rho)): the same question.
 chain end     the listed balls on the middle line, carried to the picture, end at x = k^2 / 2 + k^2 HB / (1 - HB).
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T

LOG = os.path.join(TRUTH, 'logs', 'd_derive.txt')
out = []


def say(s=''):
    print(s, flush=True); out.append(s)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')


def spindle_reach(balls, zm, d2, w, top):
    """How far the deepest listed ball reaches into the spindle whose arc reaches w from the middle line at mid-height
    (<= 0: none does), how many do, and how far the spindle itself stands above the top wall (<= 0: it does not)."""
    a = (w * w - d2) / (2 * w); R = (w * w + d2) / (2 * w)
    q = np.hypot(balls[:, 0], balls[:, 1]); dz = balls[:, 2] - zm; r = balls[:, 3]
    if a >= 0:
        dist = np.hypot(q - a, dz) - r                       # from the ring (q = a, z = zm) to the ball
        above = zm + R - top
    else:
        dist = np.hypot(q - a, dz) - r                       # exact for balls that do not cross the middle line
        cross = np.nonzero(q < r)[0]
        for i in cross:                                      # balls on the middle line: the nearest point of the ball, by a fine search
            zz = np.linspace(balls[i, 2] - r[i], balls[i, 2] + r[i], 2001)
            qq = np.maximum(q[i] - np.sqrt(np.maximum(r[i] ** 2 - (zz - balls[i, 2]) ** 2, 0)), 0)
            dist[i] = np.hypot(qq - a, zz - zm).min()
        above = (zm + np.sqrt(d2)) - top                     # its top is the upper fixed point
    deep = R - dist
    return float(deep.max()), int((deep > 1e-9).sum()), float(above), a, R


def one(gname, rho, p, r_min):
    grid = T.Grid(gname); top = T.top_of(p); h = T.hulls(top, rho); HB, HT = h['HB'], h['HT']; t0 = time.time()
    reps, info = T.build(grid, top, rho, r_min)
    c, r = reps[:, :3], reps[:, 3]
    nx, ny = grid.nearest(c[:, 0], c[:, 1]); dx, dy = c[:, 0] - nx, c[:, 1] - ny
    dtop = np.sqrt(dx * dx + dy * dy + (c[:, 2] - top) ** 2)
    istop = dtop + r <= rho + 1e-9                           # hangs from the top wall: inside a copy of the second sphere
    if rho == 1.0:                                           # two equal spheres: the nearer wall says which
        istop = c[:, 2] > top / 2
    bot = ~istop
    # fixed points
    hb = float((c[bot, 2] + r[bot]).max()); ht = float((top - c[istop, 2] + r[istop]).max()) if istop.any() else 0.0
    # hull balls
    inB = bot & (np.sqrt(dx * dx + dy * dy + (c[:, 2] - HB / 2) ** 2) + r <= HB / 2 + 1e-9)
    inT = istop & (np.sqrt(dx * dx + dy * dy + (top - c[:, 2] - HT / 2) ** 2) + r <= HT / 2 + 1e-9)
    restB = bot & ~inB; restT = istop & ~inT
    line = gname == 'line'
    hB = (np.hypot(c[:, 1], c[:, 2]) + r) if line else (c[:, 2] + r)
    hT = (np.hypot(c[:, 1], top - c[:, 2]) + r) if line else (top - c[:, 2] + r)
    limB = HB / 2 if gname == 'square' else HB / 3 if gname == 'hex' else HB / 4
    limT = limB if rho == 1.0 else rho * rho * HT
    mB = float(hB[restB].max()) if restB.any() else 0.0; mT = float(hT[restT].max()) if restT.any() else 0.0
    # bare wall (the builder's line), rho < 1 only
    x = (1 - np.sqrt(max(1 - 4 * rho * rho, 0.0))) / 2; rT = min(rho, x + rho * rho * HT)
    far = float((dtop[restT] + r[restT]).max()) if restT.any() else 0.0
    # where a rest ball touches the top wall is not known from the list (balls sit on balls), so the test is the one the code relies on: the ball of radius rT
    # spindle: all listed balls near the middle cell (slid copies within 1.5)
    lam = grid.upto(1.5); B = np.concatenate([np.column_stack([c[:, 0] + lx, c[:, 1] + ly, c[:, 2], r]) for lx, ly in lam])
    B = B[np.hypot(B[:, 0], B[:, 1]) - B[:, 3] < 0.55]
    d2 = h['d2']; zm = h['zm']
    s_written = spindle_reach(B, zm, d2, 0.5, top)
    w_built = min(0.5, top - zm + rho); s_built = spindle_reach(B, zm, d2, w_built, top)
    # chain end: balls centred on the middle line, above z = 1, carried to the picture
    onl = (np.hypot(c[:, 0], c[:, 1]) < 1e-9) & (c[:, 2] - r > 1.0)
    if onl.any():
        # a ball hanging at depth d on the middle line reaches, in the picture, to x = k^2 / 2 + k^2 / (its lowest point - 1): the lowest listed one is the last link
        end_list = float((T.K2 / 2 + T.K2 / (c[onl, 2] - r[onl] - 1.0)).max())
    else:
        end_list = float('nan')
    ok_fixed = hb <= HB + 1e-9 and ht <= HT + 1e-9
    ok_rest = mB <= limB + 1e-9 and mT <= limT + 1e-9
    ok_bare = rho == 1.0 or far <= rT + 1e-9
    ok_written = s_written[1] == 0 and s_written[2] <= 1e-9
    ok_built = s_built[1] == 0 and s_built[2] <= 1e-9
    say('%-6s rho %-7.4g p %-8.2f top %-7.4f %7d balls >= %.0e (%d bottom, %d top) | fixed points: highest on the bottom wall %.6f (HB %.6f), deepest on the top wall %.6f (HT %.6f): %s | '
        'rest: bottom %d balls, reach %.6f (allowed %.6f); top %d balls, reach %.6f (allowed %.6f): %s | bare wall: rest on top within %.6f of the centre (rT %.6f, rho %.4f): %s | '
        'spindle as written (w 0.5, a %.4f, R %.4f): %d listed balls reach in, deepest %.4g, it stands %.4g above the top wall: %s | spindle as built (w %.4f): %d reach in, deepest %.2g, above the wall %.2g: %s | '
        'chain: the last listed link ends at x %.4f, formula %.4f | %.0f s'
        % (gname, rho, p, top, info['n'], T.SLACK * r_min, int(bot.sum()), int(istop.sum()), hb, HB, ht, HT, 'HOLDS' if ok_fixed else 'FAILS',
           int(restB.sum()), mB, limB, int(restT.sum()), mT, limT, 'HOLDS' if ok_rest else 'FAILS', far, rT, rho, 'HOLDS' if ok_bare else 'FAILS',
           s_written[3], s_written[4], s_written[1], max(s_written[0], 0.0), max(s_written[2], 0.0), 'HOLDS' if ok_written else 'FAILS',
           w_built, s_built[1], max(s_built[0], 0.0), max(s_built[2], 0.0), 'HOLDS' if ok_built else 'FAILS', end_list, h['reach'], time.time() - t0))
    return ok_fixed, ok_rest, ok_bare, ok_written, ok_built


if __name__ == '__main__':
    say('Round 28, truth: section 1.3 line by line, on my own lists of balls.')
    SETS = [(1.0, 100 / 1.8), (1.0, 99.0), (1.0, 100.0), (0.5, 20.0), (0.5, 150.0), (0.5, 199.0), (0.5, 200.0), (1 / 3, 150.0), (0.25, 300.0), (1 / 6, 300.0), (0.125, 400.0),
            (0.2, 80.0), (0.2, 495.0), (0.05, 1000.0), (0.05, 1900.0), (0.025, 2000.0), (0.02, 400.0), (0.35, 280.0), (0.1, 900.0), (0.02, 4990.0)]
    tot = np.zeros(5, int); n = 0
    for gname in ('square', 'hex', 'line'):
        for rho, p in SETS:
            res = one(gname, rho, p, 4e-5 if gname == 'line' else 1.2e-3)
            tot += np.array(res, int); n += 1
        say('')
    say('%d settings. HOLDS: fixed points %d, rest %d, bare wall %d, spindle as written %d, spindle as built %d' % (n, *tot))
