"""Round 28, truth checker, sections 1.4 b and the first half of c, on my own copy of the page (dist/r28-truth.html).

  python out/r28/truth/mk/bc_page.py [keys ...]     -> out/r28/truth/logs/bc_<key>.txt, and bc_summary.txt when all ran

For each setting (rho, p, grid, depth), ONE browser at a time:
 b. three voices at the same points:
      the twin ballsInside (in the page), 20000 points in space and 20000 in the flat cut;
      my own numpy writing of the recipe of section 1.1 (tkit.recipe);
      the shader, read through sampleSlice from the program the picture is drawn with: the flat cut on two
      101 x 101 grids (the whole object; a close-up of the place where the middle ball and a neighbour kiss) and in
      space on twenty 32 x 32 grids (ten wide, ten close-ups) = 20402 + 20480 points.
 c. ballsEstimate (the page's, with parts) at points my recipe calls OUTSIDE, 20000 a set:
      box  : anywhere in a box of the picture (half of them close to the middle line of the chain);
      mid  : beside the middle line of a cell, between the two hull balls (where the spindle is the room);
      top  : just under the top wall (the bare wall, the second sphere's foot, the rest);
      edge : beside the edge of a cell (two whole numbers equally near), at every height and close to the bottom.
    (mid, top and edge are made in the object's own coordinates, slid by a whole number, and carried to the picture.)
    The test: the ball of that radius about the point, carried to the object's own space (an exact ball again), must
    meet no ball of MY list (tkit.build) and no wall. Where it does, the true distance to the nearest listed ball is
    found by halving. The same test for the shader's own number at the grid points of b.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import pagerun as R

# key: (words, rho, t, grid, depth). t = top / 2; p = 100 / (2 t - 1).
tp = lambda p: 0.5 * (100.0 / p + 1.0)
SETS = {
    'A': ('as the page opens: two equal spheres, neighbours 55.56', 1.0, 1.4, 'square', 16),
    'B': ('two equal spheres, neighbours 90, a line only', 1.0, tp(90.0), 'line', 16),
    'C': ('two equal spheres, neighbours 100 (they touch), honeycomb', 1.0, 1.0, 'hex', 30),
    'D': ('neighbours 150, second sphere 33.33 (what typing 150 gives), square', 50.0 / 150.0, tp(150.0), 'square', 16),
    'E': ('neighbours 300, second sphere 16.67 (what typing 300 gives), honeycomb', 50.0 / 300.0, tp(300.0), 'hex', 16),
    'F': ('neighbours 190, second sphere 50 (all but touching), square', 0.5, tp(190.0), 'square', 40),
    'G': ('neighbours 300, second sphere 25, a line only', 0.25, tp(300.0), 'line', 16),
    'H': ('neighbours 400, second sphere 12.5 (the end of the slider), square', 0.125, tp(400.0), 'square', 16),
    'I': ('neighbours 2000, second sphere 2.5 (the largest size that can be typed), square', 0.025, tp(2000.0), 'square', 16),
    'J': ('neighbours 150, second sphere 50, honeycomb', 0.5, tp(150.0), 'hex', 16),
    'K': ('neighbours 80, second sphere 20, square', 0.2, tp(80.0), 'square', 16),
    'L': ('neighbours 1900, second sphere 5 (all but touching), honeycomb', 0.05, tp(1900.0), 'hex', 60),
    'M': ('neighbours 200, second sphere 50 (they touch), square', 0.5, tp(200.0), 'square', 40),
    'N': ('neighbours 250, second sphere 20 (set on its own dial), square', 0.2, tp(250.0), 'square', 16),
    'O': ('neighbours 2000, second sphere 2 (the smallest), honeycomb', 0.02, tp(2000.0), 'hex', 16),
    'P': ('neighbours 2 (the smallest that can be typed is 1), second sphere 50, square', 0.5, tp(2.0), 'square', 16),
    'Q': ('neighbours 150, second sphere 33.33, square, depth 3 (few rounds)', 50.0 / 150.0, tp(150.0), 'square', 3),
    'S': ('neighbours 199.9, second sphere 50 (all but touching), square, depth 300', 0.5, tp(199.9), 'square', 300),
    'T': ('neighbours 300, second sphere 16.67, honeycomb, depth 1 (the smallest)', 50.0 / 300.0, tp(300.0), 'hex', 1),
    'U': ('neighbours 400, second sphere 25 (they touch), square, depth 1000 (the largest that can be typed)', 0.25, tp(400.0), 'square', 1000),
}
GID = {'square': 0, 'hex': 1, 'line': 2}
N = 20000

JS = """
const J = %s;
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.k.brho = J.rho; S.k.bt = J.t; S.k.bgrid = J.g; S.k.bit = J.depth; S.flat = false; S.cutOn = false; go(); await settle();
const o = { t: J.t, grid: J.g, rounds: J.depth, rho: J.rho }, op = { t: J.t, grid: J.g, rounds: J.depth, rho: J.rho, parts: true };
const w = $('ballsWarn');
const out = { sig: String(L.R.sig || '').replace(/\\n/g, '/'), k: { brho: S.k.brho, bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit, group: S.k.group }, reach: L.ballsReach(),
              warn: w && w.getClientRects().length ? w.textContent : '', status: $('status').textContent, twin: {}, same: {}, est: {}, slices: [] };
for (const name of Object.keys(J.twin)) {
  const p = J.twin[name]; let a = '', b = '';
  for (let i = 0; i < p.length; i += 3) { a += L.ballsInside(p[i], p[i + 1], p[i + 2], o) ? '1' : '0'; b += L.ballsInside(p[i], p[i + 1], p[i + 2]) ? '1' : '0'; }
  out.twin[name] = a; out.same[name] = a === b;
}
for (const name of Object.keys(J.est)) {
  const p = J.est[name], r = [];
  for (let i = 0; i < p.length; i += 3) { const e = L.ballsEstimate(p[i], p[i + 1], p[i + 2], op); r.push(e[0], e[1]); }
  out.est[name] = r;
}
for (const s of J.slices) {
  const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, s.cx, s.cy, s.side, s.z, s.n); L.releaseSnapshot(snap);
  if (!arr) fail('sampleSlice gave nothing');
  const d = [], e = [];
  for (let j = 0; j < s.n; j++) for (let i = 0; i < s.n; i++) {
    d.push(arr[4 * (j * s.n + i) + 3]);
    e.push(L.ballsEstimate(s.cx + s.side * ((i + 0.5) / s.n - 0.5), s.cy + s.side * ((j + 0.5) / s.n - 0.5), s.z, o));
  }
  out.slices.push({ d, e });
  await sleep(5);
}
out.sigAfter = String(L.R.sig || '').replace(/\\n/g, '/');
return JSON.stringify(out);
"""


def edge_radius(grid, th):
    if grid.name == 'square':
        return 0.5 / np.maximum(np.abs(np.cos(th)), np.abs(np.sin(th)))
    if grid.name == 'hex':
        return 0.5 / np.max([np.abs(np.cos(th - k * np.pi / 3)) for k in range(3)], axis=0)
    return 0.5 / np.maximum(np.abs(np.cos(th)), 0.5)


def tight(rng, grid, top, rho, n):
    """Points of the object's own space at the three kinds of place where the hulls of 1.3 are tight (before the slide)."""
    h = T.hulls(top, rho); two = 2 * np.pi
    q = 10 ** rng.uniform(-4, np.log10(0.5), n); ph = rng.uniform(0, two, n)
    mid = np.column_stack([q * np.cos(ph), q * np.sin(ph), rng.uniform(0.9 * h['HB'], top - 0.9 * h['HT'], n)])
    xy = rng.uniform(-0.62, 0.62, (n, 2)); foot = rng.random(n) < 0.5
    rr = 1.6 * rho * np.sqrt(rng.random(n)); a = rng.uniform(0, two, n)
    xy[foot, 0] = (rr * np.cos(a))[foot]; xy[foot, 1] = (rr * np.sin(a))[foot]
    topw = np.column_stack([xy, top - 10 ** rng.uniform(-5, np.log10(0.3 * min(top, 1.0)), n)])
    th = rng.uniform(0, two, n)
    if grid.name != 'line':
        corners = (np.pi / 4 + np.pi / 2 * rng.integers(0, 4, n)) if grid.name == 'square' else (np.pi / 6 + np.pi / 3 * rng.integers(0, 6, n))
        atc = rng.random(n) < 0.3; th = np.where(atc, corners + rng.normal(0, 0.03, n), th)
    d = 10 ** rng.uniform(-6, np.log10(0.03), n) * rng.choice([-1.0, 1.0], n); rb = edge_radius(grid, th) * (1 + d)
    ez = np.where(rng.random(n) < 0.5, rng.uniform(0, top, n), 10 ** rng.uniform(-4, np.log10(h['HB']), n))
    edge = np.column_stack([rb * np.cos(th), rb * np.sin(th), ez])
    if grid.name == 'line':
        edge[:, 0] = (0.5 + d) * rng.choice([-1.0, 1.0], n); edge[:, 1] = rng.uniform(-0.6, 0.6, n) * (rng.random(n) < 0.5)
        mid[::3, 1] = 0.0; topw[::3, 1] = 0.0
    return dict(mid=mid, top=topw, edge=edge)


def slid_to_picture(rng, grid, M):
    lam = grid.upto(4.5); k = rng.integers(0, len(lam), len(M)); k[rng.random(len(M)) < 0.3] = 0
    Mf = M.copy(); Mf[:, 0] += lam[k, 0]; Mf[:, 1] += lam[k, 1]
    return np.column_stack(T.unframe(Mf[:, 0], Mf[:, 1], Mf[:, 2]))


def over(P, E, ix, top, shrink=1e-9):
    """Does the ball of radius E about the picture point P reach into a listed ball or a wall? (carried to the object's
    own space by the frame, where it is an exact ball again). Returns (hit, holds the frame's centre, reaches a wall)."""
    P = np.asarray(P, float).reshape(-1, 3); E = np.asarray(E, float) * (1 - shrink)
    u = np.column_stack([P[:, 1], P[:, 2], P[:, 0] - T.K2 / 2]); uu = (u * u).sum(1)
    centre = uu <= E * E
    den = np.where(centre, 1.0, uu - E * E)
    mc = T.C0 + T.K2 * u / den[:, None]; rm = T.K2 * E / den
    wall = (~centre) & ((rm - mc[:, 2] > 1e-12) | (rm - (top - mc[:, 2]) > 1e-12))
    hit = centre | wall; todo = np.nonzero(~hit)[0]
    if todo.size:
        hit[todo] = ix.meets(mc[todo], rm[todo], tol=1e-12, walls=False)
    return hit, centre, wall


def true_dist(P, hi, ix, top, it=40):
    """The distance from P to the nearest listed ball or wall, known to be below hi: by halving."""
    P = np.asarray(P, float).reshape(-1, 3); lo = np.zeros(len(P)); hi = np.array(hi, float)
    for _ in range(it):
        mid = 0.5 * (lo + hi); h = over(P, mid, ix, top, shrink=0.0)[0]
        hi = np.where(h, mid, hi); lo = np.where(h, lo, mid)
    return 0.5 * (lo + hi)


def rnd10(a):
    return np.round(np.asarray(a, float), 10)


def one(key, page=R.PAGE):
    words, rho, t, gname, depth = SETS[key]; rho = float(rho); t = float(t)
    grid = T.Grid(gname); top = 2 * t; p = 100.0 / (top - 1); h = T.hulls(top, rho)
    rng = np.random.default_rng(1120 + 31 * ord(key))
    lines = []
    say = lambda s: (print(s, flush=True), lines.append(s))
    say('=== %s: %s' % (key, words))
    say('    rho %.10g, t %.10g (top %.6f, p %.4f), grid %s, depth %d; HB %.6f HT %.6f, the chain ends at x = +-%.4f' % (rho, t, top, p, gname, depth, h['HB'], h['HT'], h['reach']))
    X = float(min(T.K2 / 2 + T.K2 * p / 100 + 0.4, 12.0)); Y = float(min(max(T.K2 / 2, T.K2 * p / 200) + 0.3, 6.5))
    # ---- points
    tw_space = rnd10(np.column_stack([rng.uniform(-X, X, N), rng.uniform(-Y, Y, N), rng.uniform(-Y, Y, N)]))
    tw_flat = rnd10(np.column_stack([rng.uniform(-X, X, N), rng.uniform(-Y, Y, N), np.zeros(N)]))
    est = {}
    n3 = 5 * N
    bx = np.column_stack([rng.uniform(-X, X, n3), rng.uniform(-Y, Y, n3), rng.uniform(-Y, Y, n3)])
    close = rng.random(n3) < 0.5; rad = Y * rng.random(n3) ** 2; ang = rng.uniform(0, 2 * np.pi, n3)
    bx[close, 1] = (rad * np.cos(ang))[close]; bx[close, 2] = (rad * np.sin(ang))[close]
    cand = dict(box=bx)
    for name, M in tight(rng, grid, top, rho, n3).items():
        cand[name] = slid_to_picture(rng, grid, M)
    made = {}
    for name, C in cand.items():
        C = rnd10(C); C = C[np.sqrt((C * C).sum(1)) < 60.0]
        outp = ~T.inside_pic(C[:, 0], C[:, 1], C[:, 2], grid, top, rho, depth)
        est[name] = C[outp][:N]; made[name] = (len(C), int(outp.sum()))
    sl = [dict(cx=float(rng.uniform(-0.01, 0.01)), cy=float(rng.uniform(-0.01, 0.01)), side=2 * max(X, Y), z=0.0, n=101),
          dict(cx=T.K2 / 2 + float(rng.uniform(-0.01, 0.01)), cy=float(rng.uniform(-0.01, 0.01)), side=0.5, z=0.0, n=101)]
    for k in range(10):
        sl.append(dict(cx=float(rng.uniform(-0.01, 0.01)), cy=float(rng.uniform(-0.01, 0.01)), side=2 * max(X, Y), z=float(rng.uniform(-0.9 * Y, 0.9 * Y)), n=32))
    for k in range(10):
        sl.append(dict(cx=float(rng.uniform(-0.6 * X, 0.6 * X)), cy=float(rng.uniform(-0.5 * Y, 0.5 * Y)), side=0.6, z=float(rng.uniform(-0.4, 0.4)), n=32))
    job = dict(rho=rho, t=t, g=GID[gname], depth=depth, twin=dict(space=tw_space.ravel().tolist(), flat=tw_flat.ravel().tolist()),
               est={k: v.ravel().tolist() for k, v in est.items()}, slices=sl)
    t0 = time.time()
    code, text, vals = R.run(page, [JS % json.dumps(job)], 'bc_' + key)
    say('    page %s, exit %d, %s, %.0f s in the browser' % (page, code, 'no console errors' if R.clean(text) else 'CONSOLE: see logs/bc_%s.log' % key, time.time() - t0))
    if len(vals) < 2:
        say('    THE PAGE SCRIPT GAVE NOTHING BACK'); say(text[-1500:]); return lines, None
    d = json.loads(vals[-1])
    os.makedirs(os.path.join(R.LOGS, 'raw'), exist_ok=True)       # what the page gave back, and the points it was asked, kept for later questions
    import gzip
    with gzip.open(os.path.join(R.LOGS, 'raw', 'bc_%s.json.gz' % key), 'wt', encoding='utf-8') as f:
        json.dump(dict(job=job, page=d), f)
    say('    the page: program "%s" (after the slices "%s"), state %s, ballsReach() = %s' % (d['sig'], d['sigAfter'], json.dumps(d['k']), d['reach']))
    say('    the sentence under the dials: "%s"' % d['warn'])
    res = dict(key=key, code=code, clean=R.clean(text))
    # ---- b: the twin against my writing
    tot = 0
    for name, P in (('space', tw_space), ('flat', tw_flat)):
        mine = T.inside_pic(P[:, 0], P[:, 1], P[:, 2], grid, top, rho, depth)
        tw = np.array([c == '1' for c in d['twin'][name]])
        nd = int((tw != mine).sum()); tot += nd
        say('    b. twin against my writing, %-5s: %d points, inside by the twin %d, by me %d, verdicts that differ %d; the twin with nothing passed says the same: %s'
            % (name, len(P), int(tw.sum()), int(mine.sum()), nd, d['same'][name]))
    res['twin_diff'] = tot; res['twin_n'] = 2 * N; res['same'] = all(d['same'].values())
    # ---- the list of balls for this setting
    t0 = time.time(); r_min = 2e-5 if gname == 'line' else 6e-4
    reps, info = T.build(grid, top, rho, r_min); ix = T.Index(reps, grid, top)
    say('    my list: %d balls, every one of radius >= %.1e in the object\'s own space (finer near the second sphere), %d levels, %.0f s' % (info['n'], T.SLACK * r_min, info['levels'], time.time() - t0))
    # ---- b: the shader against my writing and against the twin; c: the shader's own number
    fl = [0, 0, 0]; sp = [0, 0, 0]; hair = []; sh_all = []; relworst = 0.0; rel1 = 0; reln = 0; signs = 0
    for s, got in zip(sl, d['slices']):
        n = s['n']; idx = (np.arange(n) + 0.5) / n - 0.5
        Xg = (s['cx'] + s['side'] * idx[None, :] + np.zeros((n, 1))).ravel(); Yg = (s['cy'] + s['side'] * idx[:, None] + np.zeros((1, n))).ravel(); Zg = np.full(n * n, s['z'])
        dd = np.array([np.nan if v is None else v for v in got['d']], float); ee = np.array(got['e'], float)
        mine = T.inside_pic(Xg, Yg, Zg, grid, top, rho, depth); sh = ~(dd > 0); tw = ~(ee > 0)
        tgt = fl if s['z'] == 0 else sp
        tgt[0] += n * n; tgt[1] += int((sh != mine).sum()); tgt[2] += int((sh != tw).sum())
        for k in np.nonzero(sh != mine)[0]:
            hair.append((Xg[k], Yg[k], Zg[k], dd[k], ee[k]))
        both = (dd > 0) & (ee > 0); signs += int(((dd > 0) != (ee > 0)).sum())
        rel = np.abs(dd[both] - ee[both]) / np.maximum(ee[both], 1e-4)
        if rel.size:
            relworst = max(relworst, float(rel.max())); rel1 += int((rel > 0.01).sum()); reln += rel.size
        sh_all.append(np.column_stack([Xg, Yg, Zg, dd])[dd > 0])
    say('    b. shader against my writing: flat cut %d points, verdicts that differ %d (from the twin: %d); in space %d points, differ %d (from the twin: %d)' % (fl[0], fl[1], fl[2], sp[0], sp[1], sp[2]))
    for hrow in hair[:12]:
        say('         differs at (%.6f, %.6f, %.6f): the shader\'s number %.3g, the twin\'s %.3g' % hrow)
    say('       shader\'s number against the twin\'s ballsEstimate where both say outside: %d points, worst relative difference %.2e, more than 1 %% apart at %d' % (reln, relworst, rel1))
    res.update(sh_flat=fl, sh_space=sp, rel_worst=relworst, rel_over=rel1)
    SH = np.concatenate(sh_all)
    # The shader works in single precision: its point is the grid point rounded to 7 digits, and so is every step of its
    # arithmetic. So its number is first tested as it stands; where it is longer than the true distance, by how much.
    hit, cen, wall = over(SH[:, :3], SH[:, 3], ix, top)
    nbeyond = 0; worst = None
    if hit.any():
        td = true_dist(SH[hit, :3], SH[hit, 3], ix, top); ex = SH[hit, 3] - td
        allow = 2e-3 * td + 4e-7 * (1 + np.sqrt((SH[hit, :3] ** 2).sum(1)))
        nbeyond = int((ex > allow).sum()); k = int(np.argmax(ex - allow))
        worst = (*SH[hit][k, :3], SH[hit][k, 3], td[k])
    say('    c. the shader\'s own number at its %d outside grid points: longer than the true distance to the nearest listed ball at %d; by more than single precision explains (0.2 %% of the distance + 4e-7 of the size of the coordinates) at %d'
        % (len(SH), int(hit.sum()), nbeyond))
    if worst:
        say('         the one furthest beyond that allowance: at (%.6f, %.6f, %.6f) the shader gives %.6g, the nearest listed ball is %.6g away' % worst)
    res['sh_over'] = nbeyond; res['sh_over_any'] = int(hit.sum()); res['sh_n'] = len(SH)
    # ---- c: ballsEstimate
    res['est'] = {}
    for name in ('box', 'mid', 'top', 'edge'):
        P = est[name]; e = np.array(d['est'][name], float).reshape(-1, 2); best, free = e[:, 0], e[:, 1]; E = np.minimum(best, free)
        outp = E > 0; Pn, En, bn, fn = P[outp], E[outp], best[outp], free[outp]
        hit, cen, wall = over(Pn, En, ix, top)
        loose = ~over(Pn, 2 * En, ix, top)[0]                        # twice the estimate would still be free
        say('    c. ballsEstimate, %-4s: %d outside points (made %d, outside by my recipe %d; the page calls %d of the %d inside), estimate longer than the true distance to the nearest listed ball at %d; '
            '"free" is the smaller of the two numbers at %d; twice the estimate would still be free at %d'
            % (name, len(Pn), made[name][0], made[name][1], int((~outp).sum()), len(P), int(hit.sum()), int((fn < bn).sum()), int(loose.sum())))
        rec = dict(n=len(Pn), over=int(hit.sum()), worst=None, free_smaller=int((fn < bn).sum()))
        if hit.any():
            td = true_dist(Pn[hit], En[hit], ix, top); ex = En[hit] - td; k = int(np.argmax(ex)); ratio = En[hit] / np.maximum(td, 1e-300); kr = int(np.argmax(ratio))
            m = np.array(T.frame(Pn[hit][k, 0], Pn[hit][k, 1], Pn[hit][k, 2])); nx, ny = grid.nearest(m[0], m[1])
            say('         too long: worst by length at picture (%.8f, %.8f, %.8f): estimate %.6g (best %.6g, free %.6g), true %.6g (too long by %.3g = %.1f %%); the framed point, slid: (%.5f, %.5f, %.5f). Worst by ratio: %.3f times the true distance (true %.3g)'
                % (*Pn[hit][k], En[hit][k], bn[hit][k], fn[hit][k], td[k], ex[k], 100 * ex[k] / max(td[k], 1e-300), m[0] - nx, m[1] - ny, m[2], ratio[kr], td[kr]))
            rec['worst'] = dict(p=Pn[hit][k].tolist(), est=float(En[hit][k]), true=float(td[k]), ratio=float(ratio[kr]), excess=float(ex[k]))
            rec['list'] = [dict(p=Pn[hit][j].tolist(), est=float(En[hit][j]), true=float(td[j])) for j in np.argsort(-ex)[:40]]
        res['est'][name] = rec
    with open(os.path.join(R.LOGS, 'bc_%s.txt' % key), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(R.LOGS, 'bc_%s.json' % key), 'w', encoding='utf-8') as f:
        json.dump(res, f)
    return lines, res


if __name__ == '__main__':
    keys = sys.argv[1:] or list(SETS)
    for k in keys:
        try:
            one(k)
        except Exception as err:
            import traceback
            print('SETTING %s STOPPED: %s' % (k, err)); traceback.print_exc()
    # the summary, from whatever has been run so far
    rows = []
    for k in SETS:
        fn = os.path.join(R.LOGS, 'bc_%s.json' % k)
        if os.path.exists(fn):
            rows.append(json.load(open(fn, encoding='utf-8')))
    s = ['Round 28, truth, 1.4 b and c (first half): %d settings run. Details: logs/bc_<key>.txt' % len(rows), '']
    for r in rows:
        w = SETS[r['key']]
        s.append('%s  %-78s | console %s | twin against my recipe: %d of %d differ | shader against my recipe: flat %d of %d, in space %d of %d | shader number > true: %d of %d | ballsEstimate > true: %s'
                 % (r['key'], w[0], 'clean' if r['clean'] else 'ERRORS', r['twin_diff'], r['twin_n'], r['sh_flat'][1], r['sh_flat'][0], r['sh_space'][1], r['sh_space'][0], r['sh_over'], r['sh_n'],
                    ', '.join('%s %d of %d' % (n, v['over'], v['n']) for n, v in r['est'].items())))
    open(os.path.join(R.LOGS, 'bc_summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(s) + '\n')
    print('\n'.join(s))
