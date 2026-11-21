"""The eyes, section 1.4 c, the 2D view, second look: what the page's own twin says at every pixel of a 2D picture.
For each 2D view (mk/views.py; set by typing, as mk/rays.py does) the picture is saved and, for every pixel centre,
  the page's ballsInside (at the page's depth) and
  the page's ballsEstimate (the distance the picture is drawn from), in pixels
are brought back (flat/<tag>-<view>.json). Then, in numpy (my own recipe, mk/recipe.py):
  painted inside = within 10 of the colour at the middle of the middle ball (or the commonest colour of solid pixels)
  GHOST          = painted inside, and no solid point within 1.5 px (my recipe at the page's depth, 4 x 4 points a pixel)
  for the ghosts: what the page's twin says there (inside or outside), the page's estimate in pixels, and how far the
  nearest solid point really is (my recipe on a grid of quarter pixels).

  python out/r28/eyes/mk/flat2.py <tag> <size> <theme> <view> [view ...]   -> shots/<tag>-<view>.png, flat/<tag>-<view>.json, logs/flat2-<tag>.txt
  python out/r28/eyes/mk/flat2.py again <tag> <view> ...                   (the numpy half only, from what was kept)
"""
import base64, json, os, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run
import views, rays, recipe

GRAB = """
const E = window.__E, L = window.squaringLab, S = L.S, m = E.meta, w = m.w, h = m.h, s = S.v2.h / h, o = { t: m.k.bt, grid: m.k.bgrid, rounds: m.k.bit, rho: m.k.brho };
if (!E.est) { E.est = new Float32Array(w * h); E.ins = new Uint8Array(w * h); E.y = 0; }
const t1 = performance.now();
while (E.y < h && performance.now() - t1 < %d) { const y = S.v2.y + (h / 2 - (E.y + 0.5)) * s;
  for (let i = 0; i < w; i++) { const x = S.v2.x + (i + 0.5 - w / 2) * s; E.est[E.y * w + i] = L.ballsEstimate(x, y, 0, o) / s; E.ins[E.y * w + i] = L.ballsInside(x, y, 0, o) ? 1 : 0; }
  E.y++; }
return 'rows ' + E.y + ' of ' + h;
"""
DONE = """
const E = window.__E; const b64 = a => { const u = new Uint8Array(a.buffer); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
E.meta.rowsDone = E.y;
return JSON.stringify({ meta: E.meta, est: b64(E.est), ins: b64(E.ins) });
"""


def browser(tag, size, theme, names):
    steps = [run.UP]
    for name in names:
        v = views.V[name]
        assert v['flat'], name
        c = 'null' if v['cam'] is None else json.dumps(list(v['cam']))
        js = rays.SETUP % (json.dumps(name), v['grid'], json.dumps(str(v['p'])), 'null' if v['rho'] is None else json.dumps(str(v['rho'])), v['depth'], c, 'true', rays.STEP)
        steps.append({'js': js, 'wait': 'done', 'timeout': 900, 'shot': '%s/shots/%s-%s.png' % (run.OUT, tag, name), 'clip': '#view'})
        for k in range(8):
            steps.append({'js': GRAB % 30000})
        steps.append({'js': DONE})
    code, text, vals = run.shot(run.PAGE, steps, 'flat2-%s-%s' % (tag, names[0]), size, theme)
    run.write('flat2-%s-%s.log' % (tag, names[0]), text + 'exit %d\n' % code)
    os.makedirs(os.path.join(run.EYES, 'flat'), exist_ok=True)
    got = []
    for v in vals:
        if v.startswith('{"meta"'):
            d = json.loads(v)
            with open(os.path.join(run.EYES, 'flat', '%s-%s.json' % (tag, d['meta']['name'])), 'w', encoding='utf-8') as f:
                f.write(v)
            got.append(d['meta']['name'])
    print('browser: exit %d, %s, %d of %d views back' % (code, 'no console errors' if run.clean(text) else 'SEE THE LOG', len(got), len(names)))
    if code != 0:
        print(text[-2000:])
    return got


def grow(mask, n):
    g = mask.copy()
    for _ in range(n):
        e = g.copy(); e[1:, :] |= g[:-1, :]; e[:-1, :] |= g[1:, :]; e[:, 1:] |= g[:, :-1]; e[:, :-1] |= g[:, 1:]
        e[1:, 1:] |= g[:-1, :-1]; e[:-1, :-1] |= g[1:, 1:]; e[1:, :-1] |= g[:-1, 1:]; e[:-1, 1:] |= g[1:, :-1]
        g = e
    return g


def analyse(tag, name):
    d = json.load(open(os.path.join(run.EYES, 'flat', '%s-%s.json' % (tag, name)), encoding='utf-8'))
    m = d['meta']; w, h = m['w'], m['h']
    est = np.frombuffer(base64.b64decode(d['est']), dtype=np.float32).reshape(h, w).astype(np.float64)
    ins = np.frombuffer(base64.b64decode(d['ins']), dtype=np.uint8).reshape(h, w).astype(bool)
    img = np.asarray(Image.open(os.path.join(run.EYES, 'shots', '%s-%s.png' % (tag, name))).convert('RGB')).astype(int)
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    s = m['v2']['h'] / h
    # my recipe on a grid of quarter pixels (4 x 4 points a pixel)
    Q = 4
    xs = m['v2']['x'] + ((np.arange(w * Q) + 0.5) / Q - w / 2) * s; ys = m['v2']['y'] + (h / 2 - (np.arange(h * Q) + 0.5) / Q) * s
    fine = np.zeros((h * Q, w * Q), dtype=bool)
    for r0 in range(0, h * Q, 400):
        X, Y = np.meshgrid(xs, ys[r0:r0 + 400])
        fine[r0:r0 + 400] = recipe.solid(np.stack([X.ravel(), Y.ravel(), np.zeros(X.size)], axis=1), top, rho, grid, rounds).reshape(X.shape)
    cover = fine.reshape(h, Q, w, Q).mean(axis=(1, 3))          # the share of each pixel that is solid
    anysolid = cover > 0
    # my recipe at the pixel centres (for the three voices)
    X, Y = np.meshgrid(m['v2']['x'] + (np.arange(w) + 0.5 - w / 2) * s, m['v2']['y'] + (h / 2 - (np.arange(h) + 0.5)) * s)
    mine = recipe.solid(np.stack([X.ravel(), Y.ravel(), np.zeros(X.size)], axis=1), top, rho, grid, rounds).reshape(h, w)
    # the inside colour of the picture
    cx = int(round((0 - m['v2']['x']) / s + w / 2 - 0.5)); cy = int(round(h / 2 - 0.5 - (0 - m['v2']['y']) / s))
    if 0 <= cx < w and 0 <= cy < h and mine[cy, cx]:
        ref = img[cy, cx]
    else:
        cols, cnt = np.unique(img[grow(~mine, 3) == False].reshape(-1, 3), axis=0, return_counts=True); ref = cols[cnt.argmax()]
    painted = np.abs(img - ref).max(axis=2) <= 10
    near15 = grow(anysolid, 1)                                   # something solid in the pixel or in one of its 8 neighbours (within about 1.5 px)
    ghost = painted & ~near15
    hole = ~painted & (grow(cover < 1, 1) == False)              # the pixel and its 8 neighbours wholly solid, yet not painted inside
    # how far the nearest solid point really is from each ghost pixel, in pixels (growing the quarter-pixel mask)
    far = np.zeros((h, w)); g = fine.copy(); reached = anysolid.copy(); k = 0
    left = ghost & ~reached
    while left.any() and k < 400:
        k += 1; g = grow(g, 1)
        now = g.reshape(h, Q, w, Q).any(axis=(1, 3))
        far[left & now] = k / Q
        reached |= now; left = ghost & ~reached
    far[left] = 999
    gi = ghost
    res = dict(view=name, size='%dx%d' % (w, h), p=100 / (top - 1), rho=rho, grid=grid, depth=rounds, pixels=int(w * h), insideColour=[int(x) for x in ref],
               twinAgainstMine=int((ins != mine).sum()), paintedInside=int(painted.sum()), solidCentres=int(mine.sum()),
               GHOSTS=int(gi.sum()), ghostsTwinSaysOutside=int((gi & ~ins).sum()), ghostsEstimateUnder1px=int((gi & (est < 1) & (est > 0)).sum()),
               ghostEstMedianPx=float(np.median(est[gi])) if gi.any() else 0.0, ghostEstMaxPx=float(est[gi].max()) if gi.any() else 0.0,
               ghostRealDistMedianPx=float(np.median(far[gi])) if gi.any() else 0.0, ghostRealDistMaxPx=float(far[gi].max()) if gi.any() else 0.0,
               HOLES=int(hole.sum()), estUnder1pxWhereOutside=int(((est < 1) & ~ins).sum()), estUnder1pxOutsideAndNothingNear=int(((est < 1) & ~ins & ~near15).sum()),
               status=m['status'], warn=m['warn'], boxes=m['boxes'])
    # where the ghosts are: clusters by a coarse grid, largest first
    if gi.any():
        ys_, xs_ = np.nonzero(gi)
        lab = {}
        for y, x in zip(ys_, xs_):
            lab.setdefault((y // 24, x // 24), []).append((y, x))
        big = sorted(lab.values(), key=len, reverse=True)[:6]
        res['clusters'] = [dict(n=len(c), x=int(np.mean([q[1] for q in c])), y=int(np.mean([q[0] for q in c])),
                                px=[round(float(m['v2']['x'] + (np.mean([q[1] for q in c]) + 0.5 - w / 2) * s), 4), round(float(m['v2']['y'] + (h / 2 - np.mean([q[0] for q in c]) - 0.5) * s), 4)]) for c in big]
        mk = img.copy().astype(np.uint8); mk[gi] = (255, 0, 0); mk[hole] = (0, 255, 255)
        os.makedirs(os.path.join(run.EYES, 'marks'), exist_ok=True)
        Image.fromarray(mk).save(os.path.join(run.EYES, 'marks', 'flat2-%s-%s.png' % (tag, name)))
        c = big[0]; yy = int(np.mean([q[0] for q in c])); xx = int(np.mean([q[1] for q in c]))
        x0, y0 = max(0, min(w - 60, xx - 30)), max(0, min(h - 60, yy - 30))
        pair = np.concatenate([img[y0:y0 + 60, x0:x0 + 60].astype(np.uint8), mk[y0:y0 + 60, x0:x0 + 60]], axis=1)
        Image.fromarray(pair).resize((960, 480), Image.NEAREST).save(os.path.join(run.EYES, 'marks', 'flat2-%s-%s-zoom.png' % (tag, name)))
    return res


def line(r):
    t = ('%-26s %s p %.2f rho %.4f grid %d depth %d | twin against my recipe at the pixel centres: %d of %d differ | painted inside %d, solid centres %d | '
         'GHOSTS (painted inside, nothing solid within about 1.5 px) %d: the page\'s twin says OUTSIDE at %d of them, the page\'s estimate there is under 1 px at %d (middle %.2f px, largest %.2f px), '
         'the nearest solid point is really %.1f px away in the middle, %.1f px at most | holes (wholly solid with its neighbours, not painted inside) %d | '
         'pixels where the twin says outside and the estimate is under 1 px: %d, of those with nothing solid within about 1.5 px: %d'
         % (r['view'], r['size'], r['p'], r['rho'], r['grid'], r['depth'], r['twinAgainstMine'], r['pixels'], r['paintedInside'], r['solidCentres'], r['GHOSTS'], r['ghostsTwinSaysOutside'], r['ghostsEstimateUnder1px'],
            r['ghostEstMedianPx'], r['ghostEstMaxPx'], r['ghostRealDistMedianPx'], r['ghostRealDistMaxPx'], r['HOLES'], r['estUnder1pxWhereOutside'], r['estUnder1pxOutsideAndNothingNear']))
    if r.get('clusters'):
        t += ' | largest patches (pixels, at picture pixel, at point): ' + '; '.join('%d at (%d, %d) = (%.3f, %.3f)' % (c['n'], c['x'], c['y'], c['px'][0], c['px'][1]) for c in r['clusters'])
    return t + (' | ' + r['warn'] if r['warn'] else '')


if __name__ == '__main__':
    if sys.argv[1] == 'again':
        tag = sys.argv[2]; names = sys.argv[3:]
    else:
        tag, size, theme = sys.argv[1:4]; names = browser(tag, size, theme, sys.argv[4:])
    os.makedirs(os.path.join(run.EYES, 'logs', 'flat2'), exist_ok=True)
    for name in names:
        r = analyse(tag, name)
        json.dump(r, open(os.path.join(run.EYES, 'logs', 'flat2', '%s-%s.json' % (tag, name)), 'w', encoding='utf-8'))
        print(line(r)); sys.stdout.flush()
    D = os.path.join(run.EYES, 'logs', 'flat2')
    with open(os.path.join(run.EYES, 'logs', 'flat2-%s.txt' % tag), 'w', encoding='utf-8', newline='\n') as f:
        for fn in sorted(os.listdir(D), key=lambda fn: os.path.getmtime(os.path.join(D, fn))):
            if fn.startswith(tag + '-'):
                f.write(line(json.load(open(os.path.join(D, fn), encoding='utf-8'))) + '\n\n')
