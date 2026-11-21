"""The eyes, section 1.4 c: the numpy half. Reads rays/<tag>-<view>.json (mk/rays.py) and shots/<tag>-<view>.png.

3D views. Every ray pick() was asked about (every 4th pixel of every 4th row) is walked with my own recipe
(mk/recipe.py, at the page's depth, a point still undecided counts as solid, as the page says it does) in
half-pixel steps from the eye to where the ray leaves the Drawing radius. Then:
  HOLE          the page says the ray stops nowhere, but it runs through solid for 2 px or more
  SEEN THROUGH  the page stops the ray more than 2 px BEHIND the far side of such a stretch
  IN THE OPEN   the page stops the ray at a point with nothing solid within 2.5 px (the point and 78 probes round
                it; and then 3000 more random probes within 3 px for the ones that are left)
  the picture   the saved picture against pick(): a pixel well inside the stops that has the background's colour,
                a pixel well outside them that has not
2D views. Every pixel centre of the picture is put through my recipe; the picture's inside colour is read from
its own middle (the middle ball). A pixel whose 3 x 3 neighbours are all solid but is not painted inside, or all
free but painted inside, is counted.

  python out/r28/final/eyes/mk/walk.py <tag> [view ...]   -> logs/walk-<tag>.txt (one block a view), marks/<tag>-<view>.png
"""
import base64, json, os, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe
EYES = os.path.dirname(HERE)
THEME_BG = {'dark': (8, 13, 18), 'rgb(14, 20, 27)': (8, 13, 18), 'rgb(237, 240, 242)': (223, 229, 233)}   # by the page's own body colour (dark theme: rgb(14, 20, 27)); the light theme's body is rgb(237, 240, 242) and its picture background 223, 229, 233, measured on the light start views
MINRUN = 5          # 5 solid samples half a pixel apart: through solid for 2 px or more
K = 48


def load(tag, name):
    d = json.load(open(os.path.join(EYES, 'rays', '%s-%s.json' % (tag, name)), encoding='utf-8'))
    m = d['meta']
    dep = np.frombuffer(base64.b64decode(d['depth']), dtype=np.float32).astype(np.float64) if d['depth'] else None
    met = np.frombuffer(base64.b64decode(d['met']), dtype=np.float32).astype(np.float64) if d['met'] else None
    img = np.asarray(Image.open(os.path.join(EYES, 'shots', '%s-%s.png' % (tag, name))).convert('RGB')).astype(int)
    return m, dep, met, img


def rays_of(m):
    w, h, fov, STEP, nx, ny = m['w'], m['h'], m['fov'], m['STEP'], m['nx'], m['ny']
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny))
    px = ii.ravel() * STEP + 0.5; py = jj.ravel() * STEP + 0.5
    ux = (2 * px - w) / h * fov; uy = (2 * (h - py) - h) / h * fov
    R, U, F = (np.array(m[k], dtype=np.float64) for k in ('right', 'up', 'f'))
    rd = ux[:, None] * R + uy[:, None] * U + F
    rd /= np.linalg.norm(rd, axis=1)[:, None]
    return ii.ravel(), jj.ravel(), rd


def walk3d(m, dep, met, img, mark_path):
    t0 = time.time()
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    ro = np.array(m['ro'], dtype=np.float64); pix = m['pix']; bound = m['bound']
    ii, jj, rd = rays_of(m)
    n = rd.shape[0]
    rows = m['rowsDone']; asked = jj < rows
    b = rd @ ro; hh = b * b - ro @ ro + bound * bound
    inb = hh > 0
    sq = np.sqrt(np.where(inb, hh, 0))
    s_in = np.maximum(-b - sq, 0.0); s_out = np.where(inb, -b + sq, -1.0)
    sol = lambda P: recipe.solid(P, top, rho, grid, rounds)
    # the eye itself, and how far the nearest solid point is: every 6th ray, steps a fiftieth longer each time
    eye_solid = bool(sol(ro[None, :])[0])
    sub = np.arange(0, n, 6); s = 1e-5; near = None
    while s < 2 * bound + np.linalg.norm(ro):
        P = ro + rd[sub] * s
        ok = (s >= s_in[sub]) & (s <= s_out[sub])
        if ok.any() and sol(P[ok]).any():
            near = s; break
        s *= 1.02
    s_free = 0.5 * near if near else None
    q = 1 + 0.5 * pix
    s_cur = np.maximum(s_in, s_free if s_free else 1e9)
    run = np.zeros(n, dtype=np.int32); run_s1 = np.zeros(n); any_s1 = np.zeros(n)
    big_s1 = np.zeros(n); big_s2 = np.zeros(n); big_n = np.zeros(n, dtype=np.int32)
    done = ~inb | ~asked | (s_cur >= s_out)
    pts = 0; pw = q ** np.arange(K)
    while True:
        act = np.nonzero(~done)[0]
        if act.size == 0:
            break
        sv = s_cur[act, None] * pw[None, :]
        P = ro[None, None, :] + rd[act][:, None, :] * sv[:, :, None]
        inside = sv <= s_out[act, None]
        so = np.zeros(sv.shape, dtype=bool)
        so[inside] = sol(P[inside])
        pts += int(inside.sum())
        r = run[act]; r1 = run_s1[act]; a1 = any_s1[act]; B1 = big_s1[act]; B2 = big_s2[act]; BN = big_n[act]; fin = np.zeros(act.size, dtype=bool)
        prev = np.where(r > 0, s_cur[act] / q, 0.0)
        for k in range(K):
            sk = so[:, k] & ~fin
            start = sk & (r == 0)
            r1 = np.where(start, sv[:, k], r1)
            a1 = np.where(start & (a1 == 0), sv[:, k], a1)
            ended = ~so[:, k] & (r > 0) & ~fin
            bigend = ended & (r >= MINRUN)
            B1 = np.where(bigend, r1, B1); B2 = np.where(bigend, prev, B2); BN = np.where(bigend, r, BN)
            fin |= bigend
            r = np.where(sk, r + 1, np.where(fin, r, 0))
            prev = np.where(sk, sv[:, k], prev)
        run[act] = r; run_s1[act] = r1; any_s1[act] = a1; big_s1[act] = B1; big_s2[act] = B2; big_n[act] = BN
        s_cur[act] = sv[:, -1] * q
        over = s_cur[act] > s_out[act]
        # a stretch still open where the ray leaves the Drawing radius counts with what it has
        openend = over & ~fin & (r >= MINRUN)
        if openend.any():
            a = act[openend]; big_s1[a] = run_s1[a]; big_s2[a] = np.minimum(s_cur[a] / q, s_out[a]); big_n[a] = run[a]
        done[act] = fin | over
    has_big = big_n >= MINRUN
    hit = (dep > 0) & asked
    miss = (dep == 0) & asked
    # ---- holes
    hole = miss & has_big
    chord = big_n * 0.5
    # ---- seen through
    thru = hit & has_big & (dep > big_s2 * (1 + 2 * pix))
    # ... and of those, the ones where the stretch holds a point that reaches a wall in 300 rounds (through a BALL);
    # the others ran through something that only the page's depth calls solid
    thru_ball = 0
    for a in np.nonzero(thru)[0]:
        sv = big_s1[a] * q ** np.arange(int(big_n[a]))
        if (recipe.verdict(ro + rd[a] * sv[:, None], top, rho, grid, 300) == 1).any():
            thru_ball += 1
    # the same for a hole: is it a ball the page misses, or only something the depth calls solid
    hole_ball = 0
    for a in np.nonzero(miss & has_big)[0]:
        sv = big_s1[a] * q ** np.arange(int(big_n[a]))
        if (recipe.verdict(ro + rd[a] * sv[:, None], top, rho, grid, 300) == 1).any():
            hole_ball += 1
    # ---- how far before (+) or behind (-) the first 2 px stretch the stops lie, in pixels
    both = hit & has_big
    short = (big_s1[both] - dep[both]) / (pix * dep[both])
    # ---- stops in the open
    hidx = np.nonzero(hit)[0]
    Pst = ro + rd[hidx] * dep[hidx, None]; one = pix * dep[hidx]
    dirs = np.array([[a, bq, c] for a in (-1, 0, 1) for bq in (-1, 0, 1) for c in (-1, 0, 1) if a or bq or c], dtype=np.float64)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    nearb = sol(Pst).copy()
    for kk in (0.8, 1.6, 2.5):
        left = np.nonzero(~nearb)[0]
        if left.size == 0:
            break
        Q = Pst[left][:, None, :] + kk * one[left][:, None, None] * dirs[None, :, :]
        nearb[left] = sol(Q.reshape(-1, 3)).reshape(left.size, -1).any(axis=1)
    left = np.nonzero(~nearb)[0]
    open78 = left.size
    nothing = np.zeros(left.size, dtype=bool)
    rng = np.random.default_rng(28)
    for a0 in range(0, left.size, 400):
        part = left[a0:a0 + 400]
        v = rng.normal(size=(3000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= (rng.random(3000) ** (1 / 3))[:, None] * 3.0
        Q = Pst[part][:, None, :] + one[part][:, None, None] * v[None, :, :]
        nothing[a0:a0 + part.size] = ~sol(Q.reshape(-1, 3)).reshape(part.size, -1).any(axis=1)
    open3000 = int(nothing.sum())
    # (a ball much smaller than a pixel slips through 3000 probes: for the few stops that are left, 400000 more
    #  within 1.5 px. Found on the way: logs/openprobe-dw.txt, where all such stops stood 0.5 to 0.9 px from a ball.)
    for a in np.nonzero(nothing)[0]:
        for _ in range(8):
            v = rng.normal(size=(50000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= (rng.random(50000) ** (1 / 3))[:, None] * 1.5
            if sol(Pst[left[a]] + one[left[a]] * v).any():
                nothing[a] = False; break
    openidx = hidx[left[nothing]]
    met_open = met[openidx] if openidx.size else np.array([])
    # the same question with a long search (300 rounds, a wall must be reached): stops that have something solid at the
    # page's depth within 2.5 px, but no point there that ever reaches a wall. Those stand on what only the depth of
    # the search calls solid (the swelling the page's sentence speaks of).
    wall = lambda P: recipe.verdict(P, top, rho, grid, 300) == 1
    neart = wall(Pst).copy()
    for kk in (0.8, 1.6, 2.5):
        leftt = np.nonzero(~neart)[0]
        if leftt.size == 0:
            break
        Q = Pst[leftt][:, None, :] + kk * one[leftt][:, None, None] * dirs[None, :, :]
        neart[leftt] = wall(Q.reshape(-1, 3)).reshape(leftt.size, -1).any(axis=1)
    depth_only = int((nearb & ~neart).sum())
    # ---- the picture against pick()
    H, W = img.shape[:2]
    nx, ny = m['nx'], m['ny']
    hitg = np.zeros((ny, nx), dtype=bool); hitg.ravel()[:] = hit
    askg = np.zeros((ny, nx), dtype=bool); askg.ravel()[:] = asked
    col = img[np.minimum(jj * m['STEP'], H - 1), np.minimum(ii * m['STEP'], W - 1)].reshape(ny, nx, 3)
    def eroded(g):
        e = g.copy()
        e[1:, :] &= g[:-1, :]; e[:-1, :] &= g[1:, :]; e[:, 1:] &= g[:, :-1]; e[:, :-1] &= g[:, 1:]
        e[1:, 1:] &= g[:-1, :-1]; e[:-1, :-1] &= g[1:, 1:]; e[1:, :-1] &= g[:-1, 1:]; e[:-1, 1:] &= g[1:, :-1]
        e[0, :] = False; e[-1, :] = False; e[:, 0] = False; e[:, -1] = False
        return e
    deep_hit = eroded(hitg & askg); deep_miss = eroded(~hitg & askg)
    # the background's colour: read from the picture where no ray stops all round; a picture with no such place takes
    # the colour measured on the start views of the same theme (dark 8, 13, 18; light: see THEME_BG)
    bgc = np.median(col[deep_miss], axis=0) if deep_miss.sum() > 20 else np.array(THEME_BG.get(m.get('theme', ''), THEME_BG['dark']), dtype=float)
    dist_bg = np.abs(col - bgc).max(axis=2)
    bg_spread = int(dist_bg[deep_miss].max()) if deep_miss.any() else -1
    pic_hole = deep_hit & (dist_bg <= 1)             # painted as the background (which is one colour to within 1) where rays stop all round
    pic_ghost = deep_miss & (dist_bg > 24)           # painted unlike the background where no ray stops all round
    # (a single dark pixel in a shadow has the background's colour too: a patch counts when more than half of the
    #  9 x 9 picture pixels round the sample are painted that way)
    full_bg = np.abs(img - bgc).max(axis=2)
    def share(y, x, test):
        blk = full_bg[max(0, y * m['STEP'] - 4):y * m['STEP'] + 5, max(0, x * m['STEP'] - 4):x * m['STEP'] + 5]
        return float(test(blk).mean())
    hole_patch = sum(1 for (y, x) in np.argwhere(pic_hole) if share(y, x, lambda b: b <= 1) > 0.5)
    ghost_patch = sum(1 for (y, x) in np.argwhere(pic_ghost) if share(y, x, lambda b: b > 24) > 0.5)
    # ---- a picture with the finds marked
    mk = img.copy().astype(np.uint8)
    def dot(k, c):
        for a in np.atleast_1d(k):
            y, x = int(jj[a] * m['STEP']), int(ii[a] * m['STEP'])
            mk[max(0, y - 3):y + 4, max(0, x - 3):x + 4] = c
    marked = 0
    for idxs, c in ((np.nonzero(hole)[0], (255, 0, 0)), (np.nonzero(thru)[0], (255, 0, 255)), (openidx, (255, 255, 255))):
        if len(idxs):
            dot(idxs, c); marked += len(idxs)
    for (y, x) in np.argwhere(pic_hole):
        mk[max(0, y * m['STEP'] - 2):y * m['STEP'] + 3, max(0, x * m['STEP'] - 2):x * m['STEP'] + 3] = (255, 128, 0); marked += 1
    for (y, x) in np.argwhere(pic_ghost):
        mk[max(0, y * m['STEP'] - 2):y * m['STEP'] + 3, max(0, x * m['STEP'] - 2):x * m['STEP'] + 3] = (0, 255, 255); marked += 1
    if marked:
        os.makedirs(os.path.dirname(mark_path), exist_ok=True); Image.fromarray(mk).save(mark_path)
    res = dict(view=m['name'], t=m['k']['bt'], p=100 / (2 * m['k']['bt'] - 1), rho=rho, grid=grid, depth=rounds, size='%dx%d' % (m['w'], m['h']), bound=bound, dist=m['cam'][2],
               rays=int(asked.sum()), stops=int(hit.sum()), nowhere=int(miss.sum()), leaveDrawingRadius=int((asked & ~inb).sum()),
               eyeSolid=eye_solid, nearestSolidFromEye=near, walkedPoints=pts,
               raysThroughSolid2px=int(has_big.sum()), HOLES=int(hole.sum()), holesOver10px=int((hole & (chord > 10)).sum()), longestHolePx=float(chord[hole].max()) if hole.any() else 0.0,
               SEEN_THROUGH=int(thru.sum()), SEEN_THROUGH_A_BALL=int(thru_ball), HOLES_IN_A_BALL=int(hole_ball),
               stopBeforeSurfacePx=[float(np.percentile(short, x)) for x in (0, 1, 50, 99, 100)] if short.size else None,
               stopsShortBy2px=int((short > 2).sum()), stopsDeepBy2px=int((short < -2).sum()),
               stopsWithNoSolidIn78Probes=int(open78), openAfter3000=open3000, IN_THE_OPEN=int(openidx.size), openWorstPagePx=float(met_open.max()) if met_open.size else 0.0,
               pageMetOver2px=int((met[hit] > 2).sum()), pageMetWorstPx=float(met[hit].max()) if hit.any() else 0.0,
               offRayPx=m['offRayPx'], bg=[int(x) for x in bgc], bgSpread=bg_spread, deepHit=int(deep_hit.sum()), deepMiss=int(deep_miss.sum()),
               PICTURE_BG_WHERE_RAYS_STOP=int(pic_hole.sum()), PICTURE_PAINT_WHERE_NO_RAY_STOPS=int(pic_ghost.sum()), PICTURE_HOLE_PATCHES=int(hole_patch), PICTURE_GHOST_PATCHES=int(ghost_patch), stopsOnDepthOnly=depth_only,
               pictureBgPixels=int((np.abs(img - bgc).max(axis=2) <= 6).sum()), picturePixels=int(H * W),
               status=m['status'], warn=m['warn'], boxes=m['boxes'], sig=m['sig'].strip(), drawMs=m['drawMs'], seconds=round(time.time() - t0, 1), marked=marked)
    return res


def walk2d(m, img, mark_path):
    t0 = time.time()
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    H, W = img.shape[:2]; w, h = m['w'], m['h']
    s = m['v2']['h'] / max(1, h)
    xs = m['v2']['x'] + (np.arange(W) + 0.5 - w / 2) * s; ys = m['v2']['y'] + (h / 2 - (np.arange(H) + 0.5)) * s
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X.ravel(), Y.ravel(), np.full(X.size, float(m['cut'] or 0.0))], axis=1)
    v = recipe.verdict(P, top, rho, grid, rounds).reshape(H, W)
    vdeep = recipe.verdict(P, top, rho, grid, 300).reshape(H, W)
    so = v != 0
    # the inside colour: the picture's own colour at the middle of the middle ball (0, 0), if that is in the picture; else the commonest colour among solid pixels
    cx = int(round((0 - m['v2']['x']) / s + w / 2 - 0.5)); cy = int(round(h / 2 - 0.5 - (0 - m['v2']['y']) / s))
    if 0 <= cx < W and 0 <= cy < H and so[cy, cx]:
        ref = img[cy, cx]
    else:
        cols, cnt = np.unique(img[so].reshape(-1, 3), axis=0, return_counts=True); ref = cols[cnt.argmax()]
    cream = np.abs(img - ref).max(axis=2) <= 10
    def eroded(g):
        e = g.copy()
        e[1:, :] &= g[:-1, :]; e[:-1, :] &= g[1:, :]; e[:, 1:] &= g[:, :-1]; e[:, :-1] &= g[:, 1:]
        e[1:, 1:] &= g[:-1, :-1]; e[:-1, :-1] &= g[1:, 1:]; e[1:, :-1] &= g[:-1, 1:]; e[:-1, 1:] &= g[1:, :-1]
        e[0, :] = False; e[-1, :] = False; e[:, 0] = False; e[:, -1] = False
        return e
    deep_in = eroded(so); deep_out = eroded(~so)
    hole = deep_in & ~cream; ghost = deep_out & cream
    marked = int(hole.sum() + ghost.sum())
    if marked:
        mk = img.copy().astype(np.uint8); mk[hole] = (255, 0, 0); mk[ghost] = (0, 255, 255)
        os.makedirs(os.path.dirname(mark_path), exist_ok=True); Image.fromarray(mk).save(mark_path)
    return dict(view=m['name'], t=m['k']['bt'], p=100 / (2 * m['k']['bt'] - 1), rho=rho, grid=grid, depth=rounds, size='%dx%d' % (m['w'], m['h']), flat=True, v2=m['v2'],
                pixels=int(H * W), solid=int(so.sum()), solidOnlyByDepth=int((so & (vdeep == 0)).sum()), undecidedAtPageDepth=int((v == 2).sum()), undecidedAt300=int((vdeep == 2).sum()),
                insideColour=[int(x) for x in ref], paintedInside=int(cream.sum()), agree=int((cream == so).sum()), differ=int((cream != so).sum()),
                wellInside=int(deep_in.sum()), wellOutside=int(deep_out.sum()), HOLES_wellInsideNotPainted=int(hole.sum()), GHOSTS_wellOutsidePainted=int(ghost.sum()),
                status=m['status'], warn=m['warn'], boxes=m['boxes'], sig=m['sig'].strip(), drawMs=m['drawMs'], seconds=round(time.time() - t0, 1), marked=marked)


def line(r):
    if r.get('flat'):
        return ('%-26s 2D %s  p %.2f rho %.4f grid %d depth %d | %d pixels: solid by my recipe %d (only because the depth leaves them undecided: %d), painted inside %d, the two differ at %d (edges) | '
                'well inside but not painted inside (HOLES) %d of %d, well outside but painted inside (GHOSTS) %d of %d | %s%s'
                % (r['view'], r['size'], r['p'], r['rho'], r['grid'], r['depth'], r['pixels'], r['solid'], r['solidOnlyByDepth'], r['paintedInside'], r['differ'],
                   r['HOLES_wellInsideNotPainted'], r['wellInside'], r['GHOSTS_wellOutsidePainted'], r['wellOutside'], r['status'], ' | ' + r['warn'] if r['warn'] else ''))
    sb = r['stopBeforeSurfacePx']
    return ('%-26s 3D %s  p %.2f rho %.4f grid %d depth %d, Drawing radius %.1f, eye %.3f from its target | rays %d: stop %d, stop nowhere %d | my walk: %d rays run through solid for 2 px or more; '
            'HOLES (the page stops nowhere on such a ray) %d (over 10 px: %d, longest %.1f px; of them through a ball, not only through what the depth calls solid: %d); SEEN THROUGH (stop more than 2 px behind such a stretch) %d (through a ball: %d) | '
            'stops against the first 2 px stretch, in px (+ before it): least %s, 1 %% %s, middle %s, 99 %% %s, most %s; more than 2 px before it %d, more than 2 px into it %d | '
            'stops with nothing solid at 78 probes within 2.5 px: %d, of those nothing at 3000 probes within 3 px: %s, of those NOTHING at 400000 more within 1.5 px (IN THE OPEN): %d (furthest by the page\'s own measure %.1f px) | '
            'stops that stand only on what the depth of the search calls solid (no point within 2.5 px reaches a wall in 300 rounds): %d | '
            'the page\'s own measure: %d stops further than 2 px from the nearest ball its search meets, worst %.1f px | picture against pick: background colour %s (spread %d); painted as the background (within 1 of its colour) where rays stop all round %d of %d (as a patch: %d); painted otherwise where no ray stops all round %d of %d (as a patch: %d) | '
            'eye solid %s, nearest solid point from the eye about %s | my ray against the stop: at most %.3f px off | %s, drawn in %d ms, program %s%s'
            % (r['view'], r['size'], r['p'], r['rho'], r['grid'], r['depth'], r['bound'], r['dist'], r['rays'], r['stops'], r['nowhere'], r['raysThroughSolid2px'],
               r['HOLES'], r['holesOver10px'], r['longestHolePx'], r.get('HOLES_IN_A_BALL', -1), r['SEEN_THROUGH'], r.get('SEEN_THROUGH_A_BALL', -1),
               *(('%.1f' % x for x in sb) if sb else ('-',) * 5), r['stopsShortBy2px'], r['stopsDeepBy2px'],
               r['stopsWithNoSolidIn78Probes'], r.get('openAfter3000', 'not counted apart'), r['IN_THE_OPEN'], r['openWorstPagePx'], r.get('stopsOnDepthOnly', -1), r['pageMetOver2px'], r['pageMetWorstPx'], r['bg'], r['bgSpread'],
               r['PICTURE_BG_WHERE_RAYS_STOP'], r['deepHit'], r.get('PICTURE_HOLE_PATCHES', -1), r['PICTURE_PAINT_WHERE_NO_RAY_STOPS'], r['deepMiss'], r.get('PICTURE_GHOST_PATCHES', -1),
               r['eyeSolid'], '%.4g' % r['nearestSolidFromEye'] if r['nearestSolidFromEye'] else 'none', r['offRayPx'], r['status'], r['drawMs'], r['sig'], ' | ' + r['warn'] if r['warn'] else ''))


if __name__ == '__main__':
    # one file a view (logs/walk/<tag>-<view>.json), so that two runs at the same time do not write over each other;
    # mk/brief.py reads them all and writes logs/walk-<tag>.txt
    tag = sys.argv[1]; names = sys.argv[2:]
    if not names:
        names = sorted(f[len(tag) + 1:-5] for f in os.listdir(os.path.join(EYES, 'rays')) if f.startswith(tag + '-') and f.endswith('.json'))
    os.makedirs(os.path.join(EYES, 'logs', 'walk'), exist_ok=True)
    for name in names:
        m, dep, met, img = load(tag, name)
        mark = os.path.join(EYES, 'marks', '%s-%s.png' % (tag, name))
        r = walk2d(m, img, mark) if m['flat'] else walk3d(m, dep, met, img, mark)
        with open(os.path.join(EYES, 'logs', 'walk', '%s-%s.json' % (tag, name)), 'w', encoding='utf-8') as f:
            f.write(json.dumps(r))
        print(line(r)); sys.stdout.flush()
