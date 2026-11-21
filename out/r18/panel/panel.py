"""Round 18: the Julia panel. Nine Julia sets; a rule must pass all of them before any Mandelbrot solid.
Stand-alone numpy and scipy; uses the round-16 bench's iteration helpers and rule registry. From the project root:

    python out/r18/panel/panel.py run <rule> [<rule> ...]    numbers (results/<rule>.json), tiles, sheets/<rule>.png
    python out/r18/panel/panel.py table [<rule> ...]         pass / fail lines in plain words (also table.txt)
    python out/r18/panel/panel.py sheets [<rule> ...]        redraw the sheets from saved numbers and tiles
    python out/r18/panel/panel.py user <newcomer or ->       sheet-for-user.png

What each test measures and where the thresholds come from: README.md.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R
turns = R.turns
FULL = B.FULL
NMAIN = 257
RADII = (0.02, 0.03, 0.04, 0.06, 0.08, 0.12, 0.16, 0.24, 0.32)
TREE_STEPS = (6, 8, 10, 12)


def alpha(c):
    z = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2
    return (float(z.real), float(z.imag), 0.0)


def orbit(c, k):
    z = 0j; cc = complex(c[0], c[1]); out = []
    for _ in range(k):
        out.append((float(z.real), float(z.imag), 0.0)); z = z * z + cc
    return out


RAB = (-0.122561, 0.744862, 0.0)
PANEL = [
    dict(tag='basilica', name='Basilica, c = -1', group='A', c=(-1.0, 0.0, 0.0), L=1.7, steps=40,
         meet=alpha((-1.0, 0.0)), seeds=orbit((-1.0, 0.0), 2), cross=(0.0, 1.0)),
    dict(tag='sanmarco', name='San Marco, c = -0.75', group='A', c=(-0.75, 0.0, 0.0), L=1.6, steps=40,
         meet=(-0.5, 0.0, 0.0), seeds=orbit((-0.75, 0.0), 2), cross=(0.0, 1.0), cusp=True),
    dict(tag='airplane', name='Airplane, c = -1.7549', group='A', c=(-1.754878, 0.0, 0.0), L=0.42, wide=2.0, steps=40, neck=True),
    dict(tag='cauliflower', name='Cauliflower, c = 0.25', group='A', c=(0.25, 0.0, 0.0), L=1.15, steps=40, pits=True),
    dict(tag='rabbit', name='Rabbit, c = -0.123 + 0.745i', group='B', c=RAB, L=1.4, steps=40,
         meet=alpha(RAB), seeds=orbit(RAB, 3)),
    dict(tag='dendrite', name='Dendrite, c = i', group='B', c=(0.0, 1.0, 0.0), L=1.4, steps=10, cut_steps=12, tree=True),
    dict(tag='siegel', name='Siegel disc, c = -0.391 - 0.587i', group='B', c=(-0.390541, -0.586788, 0.0), L=1.45, steps=40),
    dict(tag='rabbit90', name='Rabbit, c turned 90 degrees out of the flat plane', group='C', c=(-0.122561, 0.0, 0.744862), L=1.4, steps=40),
    dict(tag='rabbit30', name='Rabbit, c turned 30 degrees out of the flat plane', group='C', c=(-0.122561, 0.645069, 0.372431), L=1.4, steps=40),
]
TAGS = [s['tag'] for s in PANEL]


def log(*a):
    print(*a, flush=True)


def flat_inside(zx, zy, c, steps):
    """The flat rule on arbitrary points (complex numbers), same escape radius as the bench."""
    z = np.asarray(zx, float) + 1j * np.asarray(zy, float); cc = complex(c[0], c[1]); R2 = (B.resc(c) + 1e-9) ** 2
    ins = (z.real ** 2 + z.imag ** 2) <= R2
    for _ in range(steps):
        z = np.where(ins, z * z + cc, 0); ins &= (z.real ** 2 + z.imag ** 2) <= R2
    return ins


def gap_share(mask):
    """(strict share of the biggest piece, pieces, share with a one-cell gap allowed), per cent."""
    full = np.ones((3,) * mask.ndim, bool)
    lab, n = ndimage.label(mask, structure=full)
    if n == 0:
        return 0.0, 0, 0.0
    sz = np.bincount(lab.ravel())[1:]
    fat = ndimage.binary_dilation(mask, structure=full); lab2, n2 = ndimage.label(fat, structure=full)
    s2 = np.bincount(lab2[mask], minlength=n2 + 1)[1:]
    tot = float(mask.sum())
    return float(100 * sz.max() / tot), int(n), float(100 * s2.max() / tot)


def loose_share(mask):
    """Share of the matter (per cent) in pieces that are neither the biggest nor reach the wall, a one-cell gap allowed."""
    full = np.ones((3,) * mask.ndim, bool)
    fat = ndimage.binary_dilation(mask, structure=full); lab, n = ndimage.label(fat, structure=full)
    if n == 0:
        return 0.0
    sz = np.bincount(lab[mask], minlength=n + 1); sz[0] = 0
    walls = []
    for ax in range(mask.ndim):
        for e in (0, -1):
            sl = [slice(None)] * mask.ndim; sl[ax] = e; walls.append(lab[tuple(sl)].ravel())
    keep = np.ones(n + 1, bool); keep[np.unique(np.concatenate(walls))] = False; keep[np.argmax(sz)] = False; keep[0] = False
    return float(100 * sz[keep].sum() / max(mask.sum(), 1))


# ------------------------------------------------------------------ the close cut, generalised from out/me/r16/closecut.py
DISK = ndimage.iterate_structure(ndimage.generate_binary_structure(2, 1), 3)
CW, CH, CSTEPS = 420, 294, 80


def hair(mask):
    """(thin, old): thin = inside pixels that a 3-pixel opening removes (fins, whiskers, hairs, droplets under 3 pixels;
    a round bud cut through, however loose, is NOT counted) per pixel of skin line of the biggest body.
    old = the number of out/me/r16/closecut.py (every loose pixel counts, so a bud cut off its stalk counts as hair)."""
    lab, k = ndimage.label(mask)
    if k == 0:
        return None, None
    sizes = ndimage.sum(mask, lab, range(1, k + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    op_all = ndimage.binary_opening(np.pad(mask, 8, mode='edge'), DISK)[8:-8, 8:-8]
    op_main = ndimage.binary_opening(np.pad(main, 8, mode='edge'), DISK)[8:-8, 8:-8]
    skin = int((op_main & ~ndimage.binary_erosion(op_main, border_value=1)).sum())
    thin = int((mask & ~op_all).sum())
    old = int(mask.sum() - main.sum()) + int((main & ~op_main).sum())
    return float(thin / max(skin, 1)), float(old / max(skin, 1))


def shade(ins, death, steps):
    t = np.clip(np.where(death > 0, death, 0) / float(steps), 0, 1) ** 0.6
    img = np.zeros(ins.shape + (3,), np.uint8)
    img[..., 0] = (20 + 40 * t).astype(np.uint8); img[..., 1] = (26 + 70 * t).astype(np.uint8); img[..., 2] = (40 + 150 * t).astype(np.uint8)
    img[ins] = (238, 228, 200)
    return img


OFFS = (-0.5, 0.35)        # skin points: this far (in units of the body's half thickness) along x from the body's deepest point


def closecut(F, S, a0, scale, tdir):
    """Cuts through the x-axis at 22.5 and 11.25 degrees from the set's own plane (the flat plane, or the plane through
    the x-axis and c for group C), point by point, 80 steps. In each cut: the biggest body met, two skin points on it
    (never the top of the body, where a bud sits on every rule), three widths each. 12 tiles per set.
    Returns a list of dicts and writes the tiles; close_worst.png is the tile with the highest number."""
    c = S['c']; L = S['L']; out = []; worst = (-1.0, None)
    for ang in (22.5, 11.25):
        a = a0 + np.radians(ang); ca, sa = np.cos(a), np.sin(a)
        xs = np.linspace(-L, L, 401); ss = np.linspace(0.0, L, 201)[1:]
        X, Sg = np.meshgrid(xs, ss, indexing='ij')
        ins, _ = B.inside(F, X, Sg * ca, Sg * sa, c=c, steps=CSTEPS)
        lab, k = ndimage.label(ins)
        if k == 0 or np.bincount(lab.ravel())[1:].max() < 40:
            out.append(dict(angle=ang, pos=None, hair=[None] * 3, old=[None] * 3, note='nothing of the solid in this cut')); continue
        big = lab == (1 + int(np.argmax(np.bincount(lab.ravel())[1:])))
        d = ndimage.distance_transform_edt(np.pad(big, ((1, 1), (0, 1)))[1:-1, :-1]); i, j = np.unravel_index(int(np.argmax(d)), d.shape)
        dmax = float(d[i, j] * (xs[1] - xs[0])); s0 = float(ss[j])
        for pi, off in enumerate(OFFS):
            x0 = float(xs[i] + off * dmax)
            rec = dict(angle=ang, pos=pi, hair=[None] * 3, old=[None] * 3, note='')
            s = np.linspace(s0, 1.3 * L, 20001)
            i1, _ = B.inside(F, np.full_like(s, x0), s * ca, s * sa, c=c, steps=CSTEPS)
            o = np.flatnonzero(~i1)
            if not o.size or o[0] == 0:
                rec['note'] = 'no skin found'; out.append(rec); continue
            e = float(s[o[0]]); rec['skin'] = [x0, e]
            for q, hw0 in enumerate((0.1, 0.02, 0.004)):
                hw = hw0 * scale
                x, sg = np.meshgrid(np.linspace(x0 - hw, x0 + hw, CW), np.linspace(e + 0.7 * hw, e - 0.7 * hw, CH))
                it, dt = B.inside(F, x, sg * ca, sg * sa, c=c, steps=CSTEPS)
                rec['hair'][q], rec['old'][q] = hair(it)
                nm = 'close_%s_%d_%d.png' % (str(ang).replace('.', '_'), pi, q)
                Image.fromarray(shade(it, dt, CSTEPS)).save(os.path.join(tdir, nm))
                if rec['hair'][q] is not None and rec['hair'][q] > worst[0]:
                    worst = (rec['hair'][q], nm)
            rec['widths'] = [2 * w * scale for w in (0.1, 0.02, 0.004)]
            out.append(rec)
    if worst[1]:
        Image.open(os.path.join(tdir, worst[1])).save(os.path.join(tdir, 'close_worst.png'))
    return out


def extras(S, vol, res):
    """Two measures that need the solid itself. Dimples (sets flagged pits: one body with cusps, nothing comes off it):
    fill the solid's hollows with a ball of a fifth of the flat set's thickest place; what was filled are the dimples and
    grooves; count those off the flat plane and those that run round the x-axis. Doubling (the tree): take a small box
    round each point of the solid and a box twice the size; how many times more solid is in the bigger one
    (2 = a thread, 4 = a sheet, 8 = a lump; geometric mean over the solid)."""
    L = S['L']; N = vol.shape[0]; h = 2 * L / (N - 1); R2 = res['flat']['thickest']
    if S.get('pits') and vol.any():
        rv = 0.2 * R2 / h
        dil = ndimage.distance_transform_edt(~vol) <= rv
        closed = ndimage.distance_transform_edt(dil) > rv
        pit = ndimage.binary_erosion(closed & ~vol)
        _lab, ps = B.pieces(pit, h, [-L] * 3)
        ps = [q for q in ps if q['voxels'] >= B.vmin(rv)]
        rings = [q for q in ps if q['extent'] >= 300 and q['rho'] > 0.3 * R2]
        rest = [q for q in ps if not (q['extent'] >= 300 and q['rho'] > 0.3 * R2)]
        off = [q for q in rest if abs(q['centre'][2]) > max(0.5 * q['r_eq'], 3 * h)]
        res['pits'] = dict(fill_radius=0.2 * R2, dimples=len(ps), rings=len(rings), off_plane=len(off), heights=[round(abs(q['centre'][2]), 3) for q in rest[:12]])
    if S.get('tree') and vol.any():
        k = max(2, int(round(2 * R2 / h))); f = vol.astype(np.float32)
        m1 = ndimage.uniform_filter(f, size=2 * k + 1, mode='constant')[vol] * float(2 * k + 1) ** 3
        m2 = ndimage.uniform_filter(f, size=4 * k + 1, mode='constant')[vol] * float(4 * k + 1) ** 3
        res['doubling'] = dict(small_box=(2 * k + 1) * h, factor=float(np.exp(np.mean(np.log(np.maximum(m2, 1) / np.maximum(m1, 1))))))


def ribs_of(F, S, vol):
    """Ribs, without voxels (the bench's J8 outline measure): the thickest body of the solid cut across (square to the
    x-axis) through its deepest point; 1,440 rays find the outline; how far the deepest tenth of the outline lies
    inside its own slow shape, in per cent of the radius. A smooth body with buds gives about 0, a cog wheel 1 or more."""
    L = S['L']; N = vol.shape[0]; h = 2 * L / (N - 1)
    if not vol.any():
        return None
    d = ndimage.distance_transform_edt(vol); i, j, k = np.unravel_index(int(np.argmax(d)), d.shape)
    o = (-L + i * h, -L + j * h, -L + k * h); R3 = float(d[i, j, k] * h)
    out = B.outline_ripple(F, o, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), min(3.0 * R3, 1.6 * L), c=S['c'], steps=S['steps'])
    if out is not None:
        out['origin'] = [float(x) for x in o]; out['body_radius'] = R3
    return out


def ribs(rule):
    F = R.get(rule); p = os.path.join(HERE, 'results', 'ribs-' + rule + '.json'); out = {}
    for S in PANEL:
        if S.get('tree') or S.get('neck'):
            continue
        vol = B.volume(F, 193, L=S['L'], c=S['c'], steps=S['steps'])
        out[S['tag']] = ribs_of(F, S, vol)
        log('[%s %s] ribs %s' % (rule, S['tag'], out[S['tag']]))
        json.dump(out, open(p, 'w'), indent=1)


def load_ribs(rule):
    p = os.path.join(HERE, 'results', 'ribs-' + rule + '.json')
    return json.load(open(p)) if os.path.exists(p) else {}


def neck_radius(F, S):
    """At the meeting point: how far the solid reaches straight up and straight down from it (the longer of the two
    runs, looked at out to 1.0), and how far the flat set reaches from it in its emptiest direction (72 directions).
    Both are 0 for bodies that meet in a point; at a slow point (San Marco, the rabbit) both are a small blob."""
    p = S['meet']; c = S['c']; t = np.linspace(0, 1, 10001)[1:]
    def run(ins):
        o = np.flatnonzero(~ins); return float(t[o[0] - 1]) if o.size and o[0] > 0 else (0.0 if o.size else 1.0)
    up = []
    for sg in (1, -1):
        ins, _ = B.inside(F, np.full_like(t, p[0]), np.full_like(t, p[1]), sg * t, c=c, steps=S['steps']); up.append(run(ins))
    fl = []
    for k in range(72):
        a = 2 * np.pi * k / 72; fl.append(run(flat_inside(p[0] + t * np.cos(a), p[1] + t * np.sin(a), c, S['steps'])))
    return dict(up_run=max(up), flat_run=min(fl))


VIEW = (-78, 24)      # the camera: x runs across the picture


def reclose(rule):
    """Redo only the close cuts of a rule that has been run (so that the measure can be changed without new solids)."""
    F = R.get(rule); p = os.path.join(HERE, 'results', rule + '.json'); out = json.load(open(p))
    for S in PANEL:
        if S['tag'] not in out['sets']:
            continue
        r = out['sets'][S['tag']]; a0 = float(np.arctan2(S['c'][2], S['c'][1])) if S['group'] == 'C' else 0.0
        if 'meet' in r:
            r['meet'].update(neck_radius(F, S))
        t0 = time.time()
        vol = B.volume(F, NMAIN, L=S['L'], c=S['c'], steps=S['steps']); td = os.path.join(HERE, 'tiles', rule, S['tag'])
        Image.fromarray(turns.render(vol, az=VIEW[0], el=VIEW[1])).save(os.path.join(td, 'front.png'))
        Image.fromarray(turns.render(vol, az=VIEW[0], el=70)).save(os.path.join(td, 'above.png'))
        extras(S, vol, r); del vol
        if S.get('tree'):
            json.dump(out, open(p, 'w'), indent=1); continue
        r['close'] = closecut(F, S, a0, r['flat']['thickest'] / 0.47, os.path.join(HERE, 'tiles', rule, S['tag']))
        log('[%s %s] close %s  (%.0f s)' % (rule, S['tag'], [(q['angle'], q['pos'], q['hair']) for q in r['close']], time.time() - t0))
        json.dump(out, open(p, 'w'), indent=1)
    sheet(rule)


# ------------------------------------------------------------------ one rule on one set
def run_set(rule, F, S):
    t0 = time.time(); tag = S['tag']; c = S['c']; L = S['L']; steps = S['steps']; g = S['group']; N = NMAIN
    tdir = os.path.join(HERE, 'tiles', rule, tag); os.makedirs(tdir, exist_ok=True)
    save = lambda nm, img: Image.fromarray(img).save(os.path.join(tdir, nm + '.png'))
    a0 = float(np.arctan2(c[2], c[1])) if g == 'C' else 0.0
    nref = np.array([0.0, -np.sin(a0), np.cos(a0)])
    cflat = (c[0], float(np.hypot(c[1], c[2])), 0.0) if g == 'C' else c
    kw = dict(c=c, steps=steps); h = 2 * L / (N - 1)
    res = dict(rule=rule, tag=tag, name=S['name'], group=g, c=list(c), steps=steps, box=2 * L, voxel=h)

    # the flat set this solid is compared with (group C: the same c turned back into the flat plane)
    flat = B.flat_set(L=L, n=801, c=cflat, steps=steps); h2 = 2 * L / 800
    R2 = float(ndimage.distance_transform_edt(flat).max() * h2)
    fl_c = B.flat_set(L=L, n=N, c=cflat, steps=steps)
    res['flat'] = dict(thickest=R2, area=float(flat.sum() * h2 * h2), one_piece_gap_pct=gap_share(fl_c)[2], loose_pct=loose_share(fl_c))

    # exact cut
    cs = S.get('cut_steps', steps)
    ins, death = B.cut(F, 'z', L=L, n=601, c=c, steps=cs)
    if g != 'C':
        fl = B.flat_set(L=L, n=601, c=c, steps=cs)
        res['cut'] = dict(differ=int((ins ^ fl).sum()), flat_points=int(fl.sum()), steps=cs)
    save('cut_z0', B.cut_img(ins, death))
    i2, d2 = B.cut(F, 'y', L=L, n=601, c=c, steps=cs); save('cut_y0', B.cut_img(i2, d2))

    # the solid
    vol = B.volume(F, N, L=L, **kw)
    res['volume'] = float(vol.sum() * h ** 3)
    res['thickest'] = float(ndimage.distance_transform_edt(vol).max() * h)
    big = vol
    if S.get('wide'):
        big = B.volume(F, N, L=S['wide'], **kw); save('wideview', turns.render(big, az=VIEW[0], el=VIEW[1]))
    save('front', turns.render(vol, az=VIEW[0], el=VIEW[1])); save('above', turns.render(vol, az=VIEW[0], el=70))
    st, npc, gp = gap_share(vol)
    res['piece'] = dict(strict_pct=st, pieces=npc, gap_pct=gp, loose_pct=loose_share(vol))
    v = float(max(big.sum(), 1))
    res['mirror'] = dict(z_pct=float(100 * (big ^ big[:, :, ::-1]).sum() / v), y_pct=float(100 * (big ^ big[:, ::-1, :]).sum() / v))
    log('[%s %s] solid: volume %.3f thickest %.3f (flat %.3f) piece %s  (%.0f s)' % (rule, tag, res['volume'], res['thickest'], R2, res['piece'], time.time() - t0))

    # turned about the x-axis (lathe test), 129 a side
    v0 = B.volume(F, 129, L=L, **kw)
    tt = {}
    for ang in (45.0, 22.5):
        vt = B.volume(F, 129, L=L, turn=ang, **kw); tt[str(ang)] = float(100 * (v0 ^ vt).sum() / max(v0.sum(), 1))
    if g == 'C':
        vb = B.volume(F, 129, L=L, c=cflat, steps=steps, turn=float(np.degrees(a0)))
        res['turned_copy_differs_pct'] = float(100 * (v0 ^ vb).sum() / max(v0.sum(), 1))

    # what comes off when the solid is worn down by a fifth of the flat set's thickest body
    _a = np.linspace(-L, L, N); HGT = np.abs(_a[None, :, None] * nref[1] + _a[None, None, :] * nref[2])
    rad = 0.2 * R2; rv = rad / h; org = [-L] * 3
    op, rs = B.wear(vol, rv); _lab, ps = B.pieces(rs, h, org)
    ps = [p for p in ps if p['voxels'] >= B.vmin(rv) and max(abs(x) for x in p['centre']) < L - rad]
    rings = [p for p in ps if p['extent'] >= 300 and p['rho'] > 0.3 * R2]
    buds = [p for p in ps if not (p['extent'] >= 300 and p['rho'] > 0.3 * R2)]
    for p in buds:
        p['height'] = float(abs(np.dot(p['centre'], nref))); p['off'] = bool(p['height'] > max(0.5 * p['r_eq'], 3 * h))
    off = [p for p in buds if p['off']]
    res['d3'] = dict(turn_pct=min(tt.values()), turn=tt, wear_radius=rad, pieces=len(ps), rings=len(rings), off_plane=len(off),
                     round_off_plane=int(sum(p['round'] >= 0.45 for p in off)), round_all=int(sum(p['round'] >= 0.45 for p in buds)),
                     roundness=B.roundness(ps), roundness_off=B.roundness(off),
                     share_off_plane_pct=float(100 * np.broadcast_to(HGT > 3 * R2 + h, vol.shape)[vol].mean()) if S.get('tree') and vol.any() else None)
    del op, rs
    extras(S, vol, res)
    log('[%s %s] 3D %s  (%.0f s)' % (rule, tag, res['d3'], time.time() - t0))

    # the meeting point
    if S.get('meet'):
        p = np.array(S['meet']); Lm, Nm = 0.45, 201; hm = 2 * Lm / (Nm - 1)
        loc = B.volume(F, Nm, L=Lm, centre=tuple(p), **kw)
        al = np.linspace(-Lm, Lm, Nm); dd = al[:, None, None] ** 2 + al[None, :, None] ** 2 + al[None, None, :] ** 2
        seeds = [p + 0.6 * (np.array(s) - p) for s in S['seeds']]
        sidx = [tuple(int(round((s[d] - p[d] + Lm) / hm)) for d in range(3)) for s in seeds]
        s_in = [bool(loc[i]) for i in sidx]
        split = None
        if all(s_in):
            for r in RADII:
                lab, _n = ndimage.label(loc & (dd > r * r)); ls = [int(lab[i]) for i in sidx]
                if min(ls) > 0 and len(set(ls)) == len(ls):
                    split = r; break
        # the same in the flat set
        a8 = np.linspace(-Lm, Lm, 801); A8, B8 = np.meshgrid(a8 + p[0], a8 + p[1], indexing='ij'); f8 = flat_inside(A8, B8, c, steps)
        d8 = a8[:, None] ** 2 + a8[None, :] ** 2; h8 = 2 * Lm / 800
        fidx = [tuple(int(round((s[d] - p[d] + Lm) / h8)) for d in range(2)) for s in seeds]
        fsplit = None
        for r in (0.005, 0.01) + RADII:
            lab, _n = ndimage.label(f8 & (d8 > r * r)); ls = [int(lab[i]) for i in fidx]
            if min(ls) > 0 and len(set(ls)) == len(ls):
                fsplit = r; break
        t = np.linspace(-0.2, 0.2, 8001); t = t[t != 0]
        li, _ = B.inside(F, np.full_like(t, p[0]), np.full_like(t, p[1]), t, **kw)
        cr = S.get('cross')
        fline = float(flat_inside(p[0] + t * cr[0], p[1] + t * cr[1], c, steps).mean() * 0.4) if cr else 0.0
        res['meet'] = dict(point=[float(x) for x in p], seeds_inside=s_in, ball_that_parts=split, flat_disc_that_parts=fsplit,
                           upright_line=float(li.mean() * 0.4), flat_cross_line=fline,
                           ball_fill_pct=float(100 * loc[dd <= 0.01].mean()), flat_disc_fill_pct=float(100 * f8[d8 <= 0.01].mean()),
                           ball_fill_small_pct=float(100 * loc[dd <= 0.0025].mean()), flat_disc_fill_small_pct=float(100 * f8[d8 <= 0.0025].mean()))
        res['meet'].update(neck_radius(F, S))
        save('meet', turns.render(loc, az=-60, el=22))
        log('[%s %s] meet %s  (%.0f s)' % (rule, tag, res['meet'], time.time() - t0))

    # the airplane: a neck between two bodies must stay a thin spine
    if S.get('neck'):
        col = flat.sum(axis=1); xs8 = np.linspace(-L, L, 801); band = (xs8 > 0.13) & (xs8 < 0.40)
        xstar = float(xs8[band][int(np.argmin(col[band]))]); f1 = float(col[band].min() * h2 / 0.16)
        ia, _ = B.cut(F, 'x', at=xstar, L=0.08, n=201, c=c, steps=steps); b = np.linspace(-0.08, 0.08, 201)
        res['neck'] = dict(x=xstar, cut_fill_pct=float(100 * ia[(b[:, None] ** 2 + b[None, :] ** 2) <= 0.08 ** 2].mean()), flat_line_fill_pct=100 * f1)
        log('[%s %s] neck %s' % (rule, tag, res['neck']))

    # the tree
    if S.get('tree'):
        rows = []
        for n in TREE_STEPS:
            vn = B.volume(F, N, L=L, c=c, steps=n); fn = B.flat_set(L=L, n=801, c=c, steps=n); fc = B.flat_set(L=L, n=N, c=c, steps=n)
            sh = max(float(vn.any(axis=ax).sum() * h * h) for ax in range(3))
            rows.append(dict(steps=n, thickest=float(ndimage.distance_transform_edt(vn).max() * h), flat_thickest=float(ndimage.distance_transform_edt(fn).max() * h2),
                             volume=float(vn.sum() * h ** 3), gap_pct=gap_share(vn)[2], flat_gap_pct=gap_share(fc)[2],
                             biggest_shadow=sh, flat_area=float(fn.sum() * h2 * h2)))
            save('tree_%d' % n, turns.render(vn, az=-60, el=40))
        res['tree'] = rows
        log('[%s %s] tree %s  (%.0f s)' % (rule, tag, rows, time.time() - t0))

    # clean close up
    if S.get('tree'):
        res['close'] = None
    else:
        res['close'] = closecut(F, S, a0, R2 / 0.47, tdir)
        log('[%s %s] close %s  (%.0f s)' % (rule, tag, [(q['angle'], q['pos'], q['hair'], q['note']) for q in res['close']], time.time() - t0))
    res['seconds'] = time.time() - t0
    return res


def run(rule, tags=None):
    F = R.get(rule); p = os.path.join(HERE, 'results', rule + '.json'); os.makedirs(os.path.dirname(p), exist_ok=True)
    out = json.load(open(p)) if os.path.exists(p) else dict(rule=rule, label=R.RULES[rule][1], sets={})
    for S in PANEL:
        if tags and S['tag'] not in tags:
            continue
        out['sets'][S['tag']] = run_set(rule, F, S)
        json.dump(out, open(p, 'w'), indent=1)
    sheet(rule)
    return out


# ------------------------------------------------------------------ verdicts. Thresholds: README.md (set from the calibration rules' pictures)
T_CUT_SHARE = 0.001     # of the flat set's points may differ (and never fewer than 8 allowed): rounding at the skin
T_PIECE = 99.97         # per cent in the biggest piece, one-voxel gap allowed (the bench's J5)
T_LOOSE = 0.03          # per cent loose in a close-up box
T_BALL = 0.04           # the ball that parts the bodies at the meeting point
T_LINE = 0.004          # solid on the upright line through the meeting point (length within 0.2)
T_FILL = 2.0            # points of per cent by which a ball round the meeting point may be fuller than the flat disc
T_LUMP = 1.15           # thickest place of the solid over the thickest place of the flat set
T_THIN = 0.8            # thickest place of the solid over the flat set's, below which there is no body where the flat set has one
T_VOL = 2.0             # volume over the yardstick's volume (one plane: every body a ball) above which the solid is a lump
T_DOUBLE = 3.0          # the tree: doubling factor (2 = thread, 4 = sheet, 8 = lump)
T_TURN = 0.5            # per cent that must change when the solid is turned about the x-axis
T_OFF = 2               # round pieces off the set's plane
T_ROUND = 0.45
T_HAIR = 0.3            # as in docs/ROUND17.md
CLEAN_RANK = 0          # the worst tile decides, as in docs/ROUND17.md (a third-worst rule was tried and dropped: it let needles on two tiles pass)
T_MIRROR = 0.5
T_RIBS = 0.45           # the bench's J8 rib threshold
T_STRICT = 98.5         # per cent in the biggest piece with NO gap allowed (bodies touching at points lose a little here; shards lose a lot)
ORDER = ['cut', 'piece', 'bodies', 'd3', 'clean', 'mirror']
TITLE = dict(cut='exact cut', piece='one piece', bodies='bodies meet at points', d3='truly 3D', clean='clean close up', mirror='mirror')


_YARD = None


def YARD():
    """The yardstick's own numbers (one plane), per set; {} until it has been run."""
    global _YARD
    if _YARD is None:
        r = load('oneplane'); _YARD = r['sets'] if r else {}
    return _YARD


def verdicts(r):
    v = {}; g = r['group']; tree = 'tree' in r
    if r['volume'] <= 0 or r['piece']['pieces'] == 0:
        v = {k: (None, 'nothing to measure') for k in ORDER}
        v['piece'] = (False, 'the solid is EMPTY at %d a side and %d steps: nothing there, or a shell thinner than a voxel (%.3f)' % (NMAIN, r['steps'], r['voxel']))
        return v
    if g == 'C':
        v['cut'] = (None, 'c is out of the flat plane: there is no flat set to compare the cut with')
    else:
        d = r['cut']; lim = max(8, T_CUT_SHARE * d['flat_points'])
        v['cut'] = (d['differ'] <= lim, '%d of %d points of the cut at z = 0 differ from the flat set (%d steps)' % (d['differ'], d['flat_points'], d['steps']))
    pc = r['piece']; fl = r['flat']
    if tree:
        ok = all(q['gap_pct'] >= min(T_PIECE, q['flat_gap_pct']) for q in r['tree'])
        v['piece'] = (ok, 'biggest piece at %s steps: %s %% (the flat tree on the same grid: %s %%)' % (
            ', '.join(str(q['steps']) for q in r['tree']), ', '.join('%.2f' % q['gap_pct'] for q in r['tree']), ', '.join('%.2f' % q['flat_gap_pct'] for q in r['tree'])))
    elif r['tag'] == 'airplane':
        v['piece'] = (None, 'not judged: the spine is thinner than a voxel. Close-up box round the middle body: %.3f %% of the matter is loose (flat set on the same grid: %.3f %%); loose specks are left to the clean close up test' % (pc['loose_pct'], fl['loose_pct']))
    else:
        v['piece'] = (pc['gap_pct'] >= min(T_PIECE, fl['one_piece_gap_pct']) and pc['strict_pct'] >= T_STRICT, 'biggest piece holds %.3f %% with a one-voxel gap allowed (needs %.2f) and %.2f %% with none (needs %.1f); %d pieces' % (pc['gap_pct'], T_PIECE, pc['strict_pct'], T_STRICT, pc['pieces']))
    ratio = r['thickest'] / max(fl['thickest'], 1e-9)
    lump = 'thickest place of the solid %.3f, of the flat set %.3f (x %.2f)' % (r['thickest'], fl['thickest'], ratio)
    yv = (YARD().get('rabbit' if g == 'C' else r['tag']) or {}).get('volume')
    vr = (r['volume'] / yv) if yv else None
    lump += '; volume %.3f%s' % (r['volume'], '' if vr is None else ' = %.2f x the yardstick\'s (one plane%s; over %.1f = a lump)' % (vr, ', flat rabbit' if g == 'C' else '', T_VOL))
    not_lump = T_THIN <= ratio <= T_LUMP and (vr is None or vr <= T_VOL)
    if ratio < T_THIN:
        lump += '; NO BODY: the thickest place is under %.1f of the flat set\'s (plates, shards or wisps)' % T_THIN
    if tree:
        rows = r['tree']
        thin = all(q['thickest'] <= 1.5 * q['flat_thickest'] + r['voxel'] for q in rows)
        thins = rows[-1]['thickest'] / max(rows[0]['thickest'], 1e-9) <= 2 * rows[-1]['flat_thickest'] / max(rows[0]['flat_thickest'], 1e-9) + 0.05
        db = (r.get('doubling') or {}).get('factor')
        v['bodies'] = (thin and thins and db is not None and db <= T_DOUBLE, 'a tree stays a tree: thickest place at %s steps %s (flat tree %s); a box twice the size holds %s times the solid (2 = thread, 4 = sheet, 8 = lump; allowed %.1f)' % (
            ', '.join(str(q['steps']) for q in rows), ', '.join('%.3f' % q['thickest'] for q in rows), ', '.join('%.3f' % q['flat_thickest'] for q in rows), '?' if db is None else '%.1f' % db, T_DOUBLE))
    elif 'meet' in r:
        m = r['meet']; s = m['ball_that_parts']; y = (YARD().get(r['tag']) or {}).get('meet') or {}
        ys = y.get('ball_that_parts'); parts = []
        if 'ball_that_parts' in y and ys is None:
            ok_ball = True; parts.append('even the yardstick (one plane) is not parted by a ball up to 0.32 at %d steps, so the ball is not demanded here' % r['steps'])
        else:
            lim_ball = max(T_BALL, RADII[min(RADII.index(ys) + 1, len(RADII) - 1)]) if ys in RADII else T_BALL
            ok_ball = s is not None and s <= lim_ball
            parts.append((('a ball of radius %.2f at the meeting point parts the bodies' % s) if s else ('no ball up to 0.32 parts the bodies' if all(m['seeds_inside']) else 'a body centre is not in the solid')) + ' (allowed: %.2f)' % lim_ball)
        lim_run = 1.5 * max(m.get('flat_run', 0.0), y.get('up_run', 0.0)) + T_LINE
        ok_run = m.get('up_run', 9.0) <= lim_run
        parts.append('the solid reaches %.3f straight up from the meeting point (flat set in its emptiest direction: %.3f; one plane: %s; allowed %.3f)' % (
            m.get('up_run', float('nan')), m.get('flat_run', float('nan')), ('%.3f' % y['up_run']) if 'up_run' in y else '?', lim_run))
        ok_fill = m['ball_fill_pct'] <= m['flat_disc_fill_pct'] + T_FILL
        parts.append('a ball of radius 0.1 there is %.0f %% full (the flat disc: %.0f %%)' % (m['ball_fill_pct'], m['flat_disc_fill_pct']))
        v['bodies'] = (ok_ball and ok_run and ok_fill and not_lump, '; '.join(parts) + '; ' + lump)
    elif 'neck' in r:
        k = r['neck']; lim = max(1.0, 2 * (k['flat_line_fill_pct'] / 100) ** 2 * 100)
        v['bodies'] = (k['cut_fill_pct'] <= lim and not_lump, 'the neck at x = %.3f is %.2f %% full within 0.08 of the axis (a thin spine: under %.1f %%); %s' % (k['x'], k['cut_fill_pct'], lim, lump))
    else:
        v['bodies'] = (not_lump, 'no meeting point to test in this set, only "not a lump": ' + lump + ('; compared with the flat rabbit (reasoned)' if g == 'C' else ''))
    d = r['d3']
    if tree:
        ok = d['turn_pct'] >= T_TURN and (d['share_off_plane_pct'] or 0) >= 10.0
        v['d3'] = (ok, 'a turn about the x-axis changes %.1f %% of it; %.0f %% of the tree stands clear of the flat plane (branch or sheet: by eye only)' % (d['turn_pct'], d['share_off_plane_pct'] or 0))
    elif r['tag'] == 'airplane':
        v['d3'] = (d['rings'] == 0 and d['off_plane'] >= T_OFF, 'what comes off the middle body here is thin spikes, not buds: %d pieces, %d rings, %d of them off the flat plane (2 needed). Voxels; the turn test cannot be used (the body is a near ball: a turn changes %.1f %%)' % (
            d['pieces'], d['rings'], d['off_plane'], d['turn_pct']))
    elif 'pits' in r:
        q = r['pits']
        v['d3'] = (d['turn_pct'] >= T_TURN and q['rings'] == 0 and q['off_plane'] >= T_OFF, 'one body, nothing comes off it, so its dimples are counted: %d dimples or grooves (hollows a ball of radius %.2f cannot enter), %d run round the x-axis, %d lie off the flat plane (2 needed); a turn about the x-axis changes %.1f %%' % (
            q['dimples'], q['fill_radius'], q['rings'], q['off_plane'], d['turn_pct']))
    else:
        ro = d.get('roundness_off')
        ok = d['turn_pct'] >= T_TURN and d['rings'] == 0 and d['round_off_plane'] >= T_OFF and ro is not None and ro >= T_ROUND
        v['d3'] = (ok, 'a turn about the x-axis changes %.1f %% of it; %d pieces come off (worn down by %.3f): %d rings, %d off the set\'s plane, %d of those round (2 needed); roundness of what stands off the plane %s (1 = balls; under %.2f = ridges, sheets, shards)' % (
            d['turn_pct'], d['pieces'], d['wear_radius'], d['rings'], d['off_plane'], d['round_off_plane'], 'none' if ro is None else '%.2f' % ro, T_ROUND))
    cl = r.get('close')
    if cl is None:
        v['clean'] = (None, 'not measured: a tree has no skin (the tree test stands in)')
    elif cl and 'pos' not in cl[0]:
        v['clean'] = (None, 'close cuts not redone yet')
    else:
        hs = sorted([x for q in cl for x in q['hair'] if x is not None], reverse=True)
        if len(hs) < 3:
            v['clean'] = (None, 'nothing of the solid in the cuts between the planes')
        else:
            rb = load_ribs(r['rule']).get(r['tag']); rtxt = ''; rok = True
            if rb is not None:
                if rb.get('rays_that_never_left', 0) > 72:
                    rtxt = '; ribs: no outline to measure (the cut across the thickest body is not a body)'
                else:
                    if r['tag'] == 'basilica':
                        rok = rb['ripple_pct'] <= T_RIBS; rtxt = '; ribs on the middle body cut across: %.2f %% of its radius (over %.2f = ribbed)' % (rb['ripple_pct'], T_RIBS)
                    else:
                        rtxt = '; rib number %.2f (NOT judged here: off the basilica it reads fat-necked buds and lobes as ribs)' % rb['ripple_pct']
            v['clean'] = (hs[CLEAN_RANK] <= T_HAIR and rok, 'thin stuff (fins, hair, specks) per pixel of skin in %d point-by-point tiles between the planes: worst %.2f, third worst %.2f, middle %.2f (worst over %.1f = not clean)' % (
                len(hs), hs[0], hs[2], hs[len(hs) // 2], T_HAIR) + rtxt)
    mr = r['mirror']
    if g == 'A':
        v['mirror'] = (max(mr['z_pct'], mr['y_pct']) <= T_MIRROR, 'mirror above/below changes %.2f %%, front/back %.2f %%' % (mr['z_pct'], mr['y_pct']))
    elif g == 'B':
        v['mirror'] = (mr['z_pct'] <= T_MIRROR, 'mirror above/below changes %.2f %%' % mr['z_pct'])
    else:
        v['mirror'] = (None, 'no mirror to demand; the flat rabbit\'s solid turned by the same angle differs from this one by %.1f %% of it' % r.get('turned_copy_differs_pct', float('nan')))
    return v


def first_fail(v):
    for k in ORDER:
        if v[k][0] is False:
            return k
    return None


def load(rule):
    p = os.path.join(HERE, 'results', rule + '.json')
    return json.load(open(p)) if os.path.exists(p) else None


def saved_rules():
    d = os.path.join(HERE, 'results')
    have = [f[:-5] for f in os.listdir(d) if f.endswith('.json')] if os.path.isdir(d) else []
    return [n for n in R.RULES if n in have]


def table(names=None):
    names = names or saved_rules(); lines = []
    lines.append('%-10s ' % 'rule' + ' '.join('%-11s' % t for t in TAGS))
    for n in names:
        r = load(n)
        if not r:
            continue
        cells = []
        for t in TAGS:
            if t not in r['sets']:
                cells.append('-'); continue
            v = verdicts(r['sets'][t]); ff = [k for k in ORDER if v[k][0] is False]
            cells.append('pass' if not ff else 'F:' + ','.join(k[:3] for k in ff))
        lines.append('%-10s ' % n + ' '.join('%-11s' % x[:11] for x in cells))
    lines.append('')
    for n in names:
        r = load(n)
        if not r:
            continue
        lines.append('=== %s  (%s)' % (n, r['label']))
        for t in TAGS:
            if t not in r['sets']:
                continue
            s = r['sets'][t]; v = verdicts(s); ff = first_fail(v)
            lines.append('  %-11s %s' % (t, 'PASSES' if ff is None else 'FAILS first on: ' + TITLE[ff]))
            for k in ORDER:
                ok, txt = v[k]
                lines.append('      %-22s %-4s %s' % (TITLE[k], 'n/a' if ok is None else ('pass' if ok else 'FAIL'), txt))
    return '\n'.join(lines)


# ------------------------------------------------------------------ pictures
def tile(rule, tag, name, size):
    p = os.path.join(HERE, 'tiles', rule, tag, name + '.png')
    if not os.path.exists(p):
        return Image.new('RGB', (size, size), (18, 20, 26))
    im = Image.open(p).convert('RGB'); w, h = im.size; s = size / max(w, h)
    im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    bg = Image.new('RGB', (size, size), (18, 20, 26)); bg.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2)); return bg


def meet_cut(rule, S):
    """Point by point: the cut straight up through the meeting point (across: towards the body that holds 0; up: z), 0.6 wide."""
    path = os.path.join(HERE, 'tiles', rule, S['tag'], 'meetcut.png')
    if os.path.exists(path) or not S.get('meet'):
        return
    pt = np.array(S['meet']); u = -pt / max(np.linalg.norm(pt), 1e-12)
    ins, death = B.cut_plane(R.get(rule), pt, u, (0.0, 0.0, 1.0), 0.3, n=401, c=S['c'], steps=S['steps'])
    Image.fromarray(B.cut_img(ins, death)).save(path)


def sheet(rule, S=230):
    r = load(rule)
    for P_ in PANEL:
        if P_['tag'] in r['sets']:
            meet_cut(rule, P_)
    cols = [('front', 'Solid'), ('above', 'From above'), ('cut_z0', 'Cut z = 0'), ('cut_y0', 'Cut y = 0'), ('meetcut', 'Cut up through the meeting point'),
            ('close_22_5_0_0', 'Skin between planes'), ('close_worst', 'Skin: the worst tile')]
    TW = 1150; W = 20 + S * len(cols) + TW; RH = S + 34; H = 50 + RH * len(PANEL)
    im = Image.new('RGB', (W, H), (12, 14, 20)); dr = ImageDraw.Draw(im); f1, f2, f3 = turns.font(20), turns.font(14), turns.font(13)
    dr.text((12, 8), 'Julia panel, rule: %s   [%s]' % (r['label'], rule), fill=(240, 240, 240), font=f1)
    for i, P in enumerate(PANEL):
        y = 44 + i * RH; t = P['tag']
        if t not in r['sets']:
            continue
        s = r['sets'][t]; v = verdicts(s); ff = first_fail(v)
        dr.text((14, y), '%s (group %s, %d steps)  -  %s' % (P['name'], P['group'], P['steps'], 'PASSES' if ff is None else 'FAILS: ' + ', '.join(TITLE[k] for k in ORDER if v[k][0] is False)),
                fill=(150, 220, 150) if ff is None else (240, 130, 120), font=f2)
        cc = list(cols)
        if t == 'airplane':
            cc[4] = ('wideview', 'The whole set (specks)')
        if t == 'dendrite':
            cc[4] = ('tree_6', '6 steps'); cc[5] = ('tree_8', '8 steps'); cc[6] = ('tree_12', '12 steps')
        for k, (nm, ttl) in enumerate(cc):
            im.paste(tile(rule, t, nm, S - 6), (10 + k * S, y + 22)); dr.text((14 + k * S, y + 24), ttl, fill=(200, 200, 205), font=f3)
        yy = y + 26
        for k in ORDER:
            ok, txt = v[k]; col = (150, 150, 155) if ok is None else ((150, 220, 150) if ok else (240, 130, 120))
            line = '%s: %s. %s' % (TITLE[k], 'n/a' if ok is None else ('pass' if ok else 'FAIL'), txt)
            words = line.split(' '); cur = ''
            for w in words:
                if dr.textlength(cur + ' ' + w, font=f3) > TW - 20:
                    dr.text((20 + S * len(cols), yy), cur, fill=col, font=f3); yy += 16; cur = '    ' + w
                else:
                    cur = (cur + ' ' + w) if cur else w
            dr.text((20 + S * len(cols), yy), cur, fill=col, font=f3); yy += 18
    os.makedirs(os.path.join(HERE, 'sheets'), exist_ok=True)
    p = os.path.join(HERE, 'sheets', rule + '.png'); im.save(p); return p


SHORT = dict(cut='cut at z = 0 is wrong', piece='falls apart', bodies='bodies fused or a lump', d3='not truly 3D', clean='skin not clean', mirror='lopsided')


def short_words(r, v):
    """The failing tests of one (rule, set) in a few plain words for the user's sheet."""
    if r['volume'] <= 0 or r['piece']['pieces'] == 0:
        return ['nothing there: the solid is empty']
    out = []; d = r['d3']; ratio = r['thickest'] / max(r['flat']['thickest'], 1e-9)
    if v['cut'][0] is False:
        out.append('cut at z = 0 is wrong')
    if v['piece'][0] is False:
        out.append('falls apart (loose pieces)')
    if v['bodies'][0] is False:
        out.append('not a thin tree (sheets, a bush or a lump)' if 'tree' in r else ('no solid body (plates, shards or wisps)' if ratio < T_THIN else 'bodies fused into a lump'))
    if v['d3'][0] is False:
        if 'tree' in r:
            out.append('spun round the axis' if d['turn_pct'] < T_TURN else 'nothing stands off the flat plane')
        elif d['turn_pct'] < T_TURN or (d['rings'] > 0 and r['group'] == 'A'):
            out.append('rings round the axis')
        elif d['off_plane'] == 0 and (r.get('pits') or {}).get('off_plane', 0) == 0:
            out.append('buds only in the flat plane')
        else:
            out.append('what stands off the plane is not round bodies')
    if v['clean'][0] is False:
        out.append('skin not clean (hair, fins, specks or ribs)')
    if v['mirror'][0] is False:
        out.append('lopsided')
    return out


def user_sheet(newcomer=None, S=300):
    names = ['oneplane', 'twoplane', 'along'] + ([newcomer] if newcomer and load(newcomer) else [])
    heads = {'oneplane': 'One plane (the yardstick)', 'twoplane': 'Two planes, nearest plane', 'along': 'Turning plane, along',
             'p_tt1024': 'Newcomer: nearest plane, smoothed', 'p_tt256': 'Newcomer: nearest plane, smoothed'}
    W = 250 + (S + 10) * len(names) + 10; RH = S + 92; H = 96 + RH * len(PANEL)
    im = Image.new('RGB', (W, H), (12, 14, 20)); dr = ImageDraw.Draw(im); f1, f2, f3 = turns.font(24), turns.font(17), turns.font(14)
    dr.text((12, 8), 'The Julia panel: nine Julia sets, each rule judged on every one', fill=(240, 240, 240), font=f1)
    dr.text((12, 42), 'Green = passes every test on that set. Red = what it fails. Rough pictures (%d points a side). Airplane: only its middle body is drawn. An empty tile = nothing is left of the solid.' % NMAIN, fill=(190, 190, 195), font=f3)
    for j, n in enumerate(names):
        dr.text((254 + j * (S + 10), 66), heads.get(n, (load(n) or {}).get('label', n))[:38], fill=(230, 230, 235), font=f2)
    for i, P in enumerate(PANEL):
        y = 94 + i * RH
        words = P['name'].split(' '); cur = ''; yy = y + 20
        for w in words:
            if dr.textlength(cur + ' ' + w, font=f2) > 230:
                dr.text((12, yy), cur, fill=(230, 230, 235), font=f2); yy += 22; cur = w
            else:
                cur = (cur + ' ' + w) if cur else w
        dr.text((12, yy), cur, fill=(230, 230, 235), font=f2)
        dr.text((12, yy + 26), {'A': 'c on the x-axis', 'B': 'c in the flat plane', 'C': 'c out of the flat plane'}[P['group']], fill=(160, 160, 165), font=f3)
        for j, n in enumerate(names):
            r = load(n); x = 250 + j * (S + 10)
            if not r or P['tag'] not in r['sets']:
                continue
            im.paste(tile(n, P['tag'], 'front', S), (x, y))
            v = verdicts(r['sets'][P['tag']]); bad = short_words(r['sets'][P['tag']], v)
            txt = 'passes every test' if not bad else 'FAILS: ' + '; '.join(bad)
            col = (150, 220, 150) if not bad else (240, 130, 120); cur = ''; yy = y + S + 2
            for w in txt.split(' '):
                if dr.textlength(cur + ' ' + w, font=f3) > S - 4:
                    dr.text((x + 2, yy), cur, fill=col, font=f3); yy += 17; cur = w
                else:
                    cur = (cur + ' ' + w) if cur else w
            dr.text((x + 2, yy), cur, fill=col, font=f3)
    p = os.path.join(HERE, 'sheet-for-user.png'); im.save(p); return p


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'table'
    if cmd == 'run':
        args = sys.argv[2:]; tags = [a for a in args if a in TAGS]; names = [a for a in args if a not in TAGS]
        for nm in names:
            run(nm, tags or None)
            log(table([nm]))
    elif cmd == 'close':
        for nm in sys.argv[2:]:
            reclose(nm)
    elif cmd == 'ribs':
        for nm in sys.argv[2:]:
            ribs(nm)
    elif cmd == 'sheets':
        for nm in sys.argv[2:] or saved_rules():
            log(sheet(nm))
    elif cmd == 'user':
        log(user_sheet(sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None))
    else:
        t = table(sys.argv[2:] or None); log(t)
        if len(sys.argv) <= 2:
            open(os.path.join(HERE, 'table.txt'), 'w', encoding='utf-8').write(t + '\n')
