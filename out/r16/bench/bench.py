"""Round 16 test bench: stage 1 (the basilica, tests J1 to J8) and stage 2 (the Mandelbrot solid).
Stand-alone numpy and scipy. Run from the project root:

    python out/r16/bench/bench.py stage1 <rule> [<rule> ...]     numbers + tiles + one sheet per rule
    python out/r16/bench/bench.py stage2 <rule> [...]            only for rules whose stage 1 passed (refuses otherwise)
    python out/r16/bench/bench.py lights <rule> [...]            the three warning-light Julia sets
    python out/r16/bench/bench.py table                          the table of all saved results with pass / fail

Results: results/<rule>.json, tiles/<rule>/*.png, sheets/<rule>.png.  How the tests are measured: README.md.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules as R
turns = R.turns

ALPHA = (1 - 5 ** 0.5) / 2            # where the middle body and the left body of the flat basilica touch (-0.618034)
C0 = (-1.0, 0.0, 0.0)
FULL = np.ones((3, 3, 3), bool)
STEPS = 60
SIN20 = float(np.sin(np.radians(20)))


def resc(c):
    n = float(np.linalg.norm(c))
    return (1 + np.sqrt(1 + 4 * n)) / 2


# ------------------------------------------------------------------ the iteration
def _inside(F, x, y, z, c=C0, steps=STEPS, trap=0.0, mandel=False):
    """x, y, z 1-D. Returns (inside bool, death int16: the step at which the point left, 0 = never left or outside at once).
    Julia: v -> F(v) + c, escape radius resc(c) (exact for rules that square the length).
    Mandelbrot: c = the point, start at v = c, escape radius 2.
    trap > 0: a point that comes within `trap` of the origin counts as inside from then on (only used for c = -1,
    and only after trap_radius() has checked it for the rule)."""
    n = x.size
    if mandel:
        cx, cy, cz = x, y, z
        R2 = 4.0
    else:
        R2 = (resc(c) + 1e-9) ** 2
    ins = np.zeros(n, bool); death = np.zeros(n, np.int16)
    alive = np.flatnonzero(x * x + y * y + z * z <= R2)
    x, y, z = x[alive], y[alive], z[alive]
    for k in range(steps):
        if alive.size == 0:
            break
        X, Y, Z = F(x, y, z)
        if mandel:
            X = X + cx[alive]; Y = Y + cy[alive]; Z = Z + cz[alive]
        else:
            X = X + c[0]; Y = Y + c[1]; Z = Z + c[2]
        r2 = X * X + Y * Y + Z * Z
        keep = r2 <= R2
        death[alive[~keep]] = k + 1
        if trap > 0:
            tr = r2 < trap * trap
            ins[alive[tr]] = True
            keep &= ~tr
        alive = alive[keep]; x, y, z = X[keep], Y[keep], Z[keep]
    ins[alive] = True
    return ins, death


def inside(F, x, y, z, chunk=1500000, **kw):
    sh = np.shape(x)
    x, y, z = (np.ravel(np.asarray(a, float)) for a in (x, y, z))
    ins = np.zeros(x.size, bool); death = np.zeros(x.size, np.int16)
    for s in range(0, x.size, chunk):
        ins[s:s + chunk], death[s:s + chunk] = _inside(F, x[s:s + chunk], y[s:s + chunk], z[s:s + chunk], **kw)
    return ins.reshape(sh), death.reshape(sh)


def trap_radius(F, r=0.05):
    """c = -1 only. Checked, not proved: 100,000 points within r of the origin all stay bounded for 150 steps and end
    within r of 0 or of -1. Then the iteration may stop as soon as a point comes within r of the origin."""
    rng = np.random.default_rng(3)
    v = rng.normal(size=(100000, 3)); v *= (r * rng.uniform(0, 1, 100000) ** (1 / 3) / np.linalg.norm(v, axis=1))[:, None]
    x, y, z = v.T
    for k in range(150):
        x, y, z = F(x, y, z); x = x - 1.0
        if not np.all(np.isfinite(x)) or (x * x + y * y + z * z).max() > 4:
            return 0.0
    d = np.minimum(np.sqrt(x * x + y * y + z * z), np.sqrt((x + 1) ** 2 + y * y + z * z))
    return r if d.max() < r else 0.0


def volume(F, N, L=1.75, centre=(0.0, 0.0, 0.0), turn=0.0, **kw):
    """bool [N, N, N] indexed [ix, iy, iz]; samples at centre + linspace(-L, L, N). N odd puts a sample on the centre.
    turn: the solid turned by this many degrees about the x-axis (the samples are turned back before the test)."""
    a = np.linspace(-L, L, N)
    Y, Z = np.meshgrid(a + centre[1], a + centre[2], indexing='ij')
    if turn:
        t = np.radians(-turn); Y, Z = Y * np.cos(t) - Z * np.sin(t), Y * np.sin(t) + Z * np.cos(t)
    vol = np.zeros((N, N, N), bool)
    per = max(1, 1500000 // (N * N))
    for i0 in range(0, N, per):
        xs = a[i0:i0 + per] + centre[0]
        m = len(xs)
        X = np.repeat(xs, N * N)
        ins, _ = _inside(F, X, np.tile(Y.ravel(), m), np.tile(Z.ravel(), m), **kw)
        vol[i0:i0 + m] = ins.reshape(m, N, N)
    return vol


def cut(F, plane, at=0.0, L=1.75, n=401, centre=(0.0, 0.0), **kw):
    """Flat cut. plane 'z': image axes (x, y); 'y': (x, z); 'x': (y, z). Returns (inside, death), indexed [a, b]."""
    a = np.linspace(-L, L, n)
    A, B = np.meshgrid(a + centre[0], a + centre[1], indexing='ij'); O = np.full_like(A, at)
    x, y, z = {'z': (A, B, O), 'y': (A, O, B), 'x': (O, A, B)}[plane]
    return inside(F, x, y, z, **kw)


def flat_set(L=1.75, n=801, c=C0, steps=STEPS, mandel=False, centre=(0.0, 0.0)):
    """The flat set itself (complex numbers), on the grid of cut(..., 'z')."""
    a = np.linspace(-L, L, n)
    A, B = np.meshgrid(a + centre[0], a + centre[1], indexing='ij')
    z0 = A + 1j * B
    cc = z0 if mandel else complex(c[0], c[1])
    R2 = 4.0 if mandel else (resc(c) + 1e-9) ** 2
    z = z0.copy(); ins = (z.real ** 2 + z.imag ** 2) <= R2
    for k in range(steps):
        z = np.where(ins, z * z + cc, 0)
        ins &= (z.real ** 2 + z.imag ** 2) <= R2
    return ins


def cut_img(ins, death):
    n = ins.shape[0]
    img = np.zeros((n, n, 3), np.float32); t = np.clip(death / 14.0, 0, 1)
    for ch, col in enumerate((70, 110, 170)):
        img[:, :, ch] = 18 + (col - 18) * t
    img[ins] = (235, 225, 200)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]


# ------------------------------------------------------------------ wearing a solid down
def wear(vol, rad_vox):
    """Wear the solid down by a ball of radius rad_vox and grow it back (an 'opening'). Returns (opened, residue):
    residue = what came off, at least 1.5 voxels clear of what stayed (so that staircase skin does not count)."""
    d_in = ndimage.distance_transform_edt(vol)
    core = d_in > rad_vox
    if not core.any():
        return np.zeros_like(vol), vol.copy()
    d_out = ndimage.distance_transform_edt(~core)
    return (d_out <= rad_vox) & vol, vol & (d_out > rad_vox + 1.5)


def pieces(mask, h, origin):
    """Label a mask (corner-connected) and measure each piece. Returns (labels, list of dicts sorted biggest first)."""
    lab, n = ndimage.label(mask, structure=FULL)
    if n == 0:
        return lab, []
    idx = np.flatnonzero(lab); l = lab.ravel()[idx]
    i, j, k = np.unravel_index(idx, lab.shape)
    P = np.stack([origin[0] + i * h, origin[1] + j * h, origin[2] + k * h], 1)
    cnt = np.bincount(l, minlength=n + 1).astype(float); cs = np.maximum(cnt, 1)
    cen = np.stack([np.bincount(l, P[:, d], n + 1) for d in range(3)], 1) / cs[:, None]
    D = P - cen[l]
    cov = np.zeros((n + 1, 3, 3))
    for a in range(3):
        for b in range(a, 3):
            cov[:, a, b] = cov[:, b, a] = np.bincount(l, D[:, a] * D[:, b], n + 1) / cs
    ev = np.linalg.eigvalsh(cov)[:, ::-1]
    bins = ((np.arctan2(P[:, 2], P[:, 1]) + np.pi) / (2 * np.pi) * 72).astype(int) % 72
    occ = np.zeros((n + 1, 72), bool); occ[l, bins] = True
    rho = np.bincount(l, np.hypot(P[:, 1], P[:, 2]), n + 1) / cs
    out = []
    for q in np.argsort(-cnt)[:400]:
        if q == 0 or cnt[q] == 0:
            continue
        e = np.maximum(ev[q], 0)
        out.append(dict(label=int(q), voxels=int(cnt[q]), centre=[float(v) for v in cen[q]],
                        r_eq=float((3 * cnt[q] / (4 * np.pi)) ** (1 / 3) * h),
                        round=float(np.sqrt(e[2] / e[0])) if e[0] > 0 else 0.0,       # 1 = ball, small = streak or sheet
                        mid=float(np.sqrt(e[1] / e[0])) if e[0] > 0 else 0.0,
                        extent=int(occ[q].sum() * 5), rho=float(rho[q]),
                        phi=float(np.degrees(np.arctan2(cen[q][2], cen[q][1])))))
    return lab, out


def vmin(rad_vox):
    return max(12.0, 4 / 3 * np.pi * (0.25 * rad_vox) ** 3)


def roundness(ps):
    """Volume-weighted mean roundness of a list of pieces (None when there is no detail)."""
    w = sum(p['voxels'] for p in ps)
    return float(sum(p['voxels'] * p['round'] for p in ps) / w) if w else None


def skin_evenness(vol):
    """How evenly the skin's normals point: 3 x the smallest eigenvalue of the mean of n n^T over skin voxels.
    1 = all ways (a ball), 0 = one or two ways (a sheet, a ridge, a tube)."""
    sm = ndimage.gaussian_filter(vol.astype(np.float32), 1.2)
    skin = vol & ~ndimage.binary_erosion(vol)
    skin[0] = skin[-1] = False; skin[:, 0] = skin[:, -1] = False; skin[:, :, 0] = skin[:, :, -1] = False
    if skin.sum() < 50:
        return None
    g = np.stack([a[skin] for a in np.gradient(sm)], 1).astype(float)
    g /= np.maximum(np.linalg.norm(g, axis=1), 1e-9)[:, None]
    ev = np.linalg.eigvalsh(g.T @ g / len(g))
    return float(3 * ev[0])


def skin_relief(vol, cell=16):
    """The brief's J8 measure: how the skin's normals point inside small boxes (cells of `cell` voxels).
    In each cell the normals give three numbers l1 >= l2 >= l3 (eigenvalues of the mean of n n^T).
    A flat patch points one way (l2 = l3 = 0); ribs, ridges, tubes and sheet edges fan out in ONE direction
    (l2 > 0, l3 = 0); balls and round bumps fan out in two (l2 = l3).
      relief_round  = mean of sqrt(l3 / l2), weighted by how much the cell's normals fan out (1 = round, 0 = streaks)
      streak_share  = share of the skin lying in cells that fan out clearly (l2 + l3 > 0.08) but one way only (sqrt(l3/l2) < 0.3)
      bumpy_share   = share in cells that fan out clearly and both ways"""
    sm = ndimage.gaussian_filter(vol.astype(np.float32), 1.2)
    skin = vol & ~ndimage.binary_erosion(vol)
    for ax in range(3):
        sl = [slice(None)] * 3
        for e in (slice(0, 2), slice(-2, None)):
            sl[ax] = e; skin[tuple(sl)] = False
    if skin.sum() < 200:
        return None
    ii = np.nonzero(skin)
    g = np.stack([a[skin] for a in np.gradient(sm)], 1).astype(float)
    g /= np.maximum(np.linalg.norm(g, axis=1), 1e-9)[:, None]
    cid = (ii[0] // cell) * 1000000 + (ii[1] // cell) * 1000 + (ii[2] // cell)
    _u, inv = np.unique(cid, return_inverse=True); nc = int(inv.max()) + 1
    n = np.bincount(inv, minlength=nc).astype(float)
    M = np.zeros((nc, 3, 3))
    for a in range(3):
        for b in range(a, 3):
            M[:, a, b] = M[:, b, a] = np.bincount(inv, g[:, a] * g[:, b], nc) / n
    ev = np.clip(np.linalg.eigvalsh(M), 0, 1)
    l3, l2 = ev[:, 0], ev[:, 1]
    ok = n >= cell * cell / 4.0
    if not ok.any():
        return None
    spread = l2 + l3; two = np.sqrt(l3 / np.maximum(l2, 1e-12))
    w = (n * spread)[ok]
    tot = n[ok].sum()
    return dict(relief_round=float((w * two[ok]).sum() / max(w.sum(), 1e-12)), mean_spread=float((n * spread)[ok].sum() / tot),
                streak_share=float(n[ok & (spread > 0.08) & (two < 0.3)].sum() / tot), bumpy_share=float(n[ok & (spread > 0.08) & (two >= 0.3)].sum() / tot),
                cells=int(ok.sum()))


def loose_pct(vol):
    """Close-up boxes: share of the matter in pieces that neither belong to the biggest piece nor reach the wall of
    the box, when a one-voxel gap is allowed (a body that touches at one point shows a gap of under one voxel)."""
    fat = ndimage.binary_dilation(vol, structure=FULL); lab, n = ndimage.label(fat, structure=FULL)
    if n == 0:
        return 0.0
    sz = np.bincount(lab[vol], minlength=n + 1); sz[0] = 0
    wall = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    keep = np.ones(n + 1, bool); keep[wall] = False; keep[np.argmax(sz)] = False; keep[0] = False
    return float(100 * sz[keep].sum() / max(vol.sum(), 1))


def cut_plane(F, origin, u, v, L, n=501, **kw):
    """Flat cut through `origin` spanned by the unit vectors u (to the right) and v (up)."""
    a = np.linspace(-L, L, n); A, Bb = np.meshgrid(a, a, indexing='ij')
    x, y, z = (origin[d] + A * u[d] + Bb * v[d] for d in range(3))
    return inside(F, x, y, z, **kw)


def outline_ripple(F, origin, u, v, rmax, nray=1440, nstep=2400, **kw):
    """Ribs on a body, measured without voxels. In the flat cut through `origin` spanned by u and v, walk outwards
    along 1,440 rays (2,400 steps each, then halving) and find where each first leaves the solid: the outline
    r(angle). Take away the outline's own slow shape (running median over 10 degrees).
      ripple_pct = how far inside its slow shape the deepest tenth of the outline lies, in per cent of the radius.
    Buds only push the outline OUT (a ray that slips through a touching point comes out on the far side of the
    bud), ribs cut grooves IN. So a smooth body with buds gives about 0 and a cog wheel gives 1 or more.
      two_sided_pct = 1.4826 x median |r - slow| / radius, for comparison (it also counts the buds)."""
    origin = np.array(origin, float); u = np.array(u, float); v = np.array(v, float)
    o_in, _ = inside(F, origin[:1], origin[1:2], origin[2:3], **kw)
    if not o_in[0]:
        return None
    th = np.linspace(0, 2 * np.pi, nray, endpoint=False)
    d = np.cos(th)[:, None] * u[None, :] + np.sin(th)[:, None] * v[None, :]
    t = np.linspace(0, rmax, nstep + 1)[1:]
    lo = np.zeros(nray); hi = np.zeros(nray); gone = np.zeros(nray, bool)
    for s in range(0, nray, 360):
        P = origin[None, None, :] + t[None, :, None] * d[s:s + 360, None, :]
        ins, _ = inside(F, P[..., 0], P[..., 1], P[..., 2], **kw)
        k = np.argmax(~ins, axis=1); gone[s:s + 360] = ~ins.all(axis=1)
        lo[s:s + 360] = np.where(k > 0, t[np.maximum(k - 1, 0)], 0.0); hi[s:s + 360] = t[k]
    for it in range(14):
        mid = 0.5 * (lo + hi); Q = origin[None, :] + mid[:, None] * d
        mi, _ = inside(F, Q[:, 0], Q[:, 1], Q[:, 2], **kw)
        lo = np.where(mi, mid, lo); hi = np.where(mi, hi, mid)
    r = np.where(gone, lo, rmax)
    slow = ndimage.median_filter(r, size=41, mode='wrap')
    Rm = float(np.mean(slow)); dev = (r - slow) / max(Rm, 1e-12)
    return dict(ripple_pct=float(max(0.0, -100 * np.percentile(dev, 10))), two_sided_pct=float(100 * 1.4826 * np.median(np.abs(dev))),
                mean_radius=Rm, rays_that_never_left=int((~gone).sum()))


def reripple(name):
    """Measure the three outlines again from the saved close-ups (no new solids) and store them in the result."""
    F = R.get(name); r = load(name); kw = dict(trap=r.get('trap', 0.0))
    r['J8']['ripple_1'] = outline_ripple(F, (0, 0, 0), (0, 1, 0), (0, 0, 1), 1.0, **kw)
    c2 = take(name, 'close2')
    if c2:
        v2, L2, pt = c2; o2, _l, _s = on_centre_body(v2, L2, pt, 'bud', pt); cA = o2.get('core_centre', list(pt))
        e = np.array([0.0, pt[1], pt[2]]); e /= max(np.linalg.norm(e), 1e-12)
        r['J8']['ripple_2'] = outline_ripple(F, cA, (1.0, 0.0, 0.0), (0.0, -e[2], e[1]), L2 * 0.9, **kw)
        c3 = take(name, 'close3')
        if c3:
            v3, L3, pt3 = c3; o3, _l, _s = on_centre_body(v3, L3, pt3, 'sub-bud', pt3)
            cc = np.array(o3.get('core_centre', list(pt3))); u3, w3 = perp_pair(cc - np.array(cA))
            r['J8']['ripple_3'] = outline_ripple(F, cc, u3, w3, L3 * 0.9, steps=80, **kw)
    json.dump(r, open(os.path.join(HERE, 'results', name + '.json'), 'w'), indent=1)
    log('[%s] ribs: %s' % (name, [r['J8'].get('ripple_%d' % k) for k in (1, 2, 3)]))
    rule_sheet(name)


def perp_pair(axis):
    a = np.array(axis, float); a /= max(np.linalg.norm(a), 1e-12)
    h = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, h); u /= np.linalg.norm(u)
    return u, np.cross(a, u)


def cache_path(name, tag):
    d = os.path.join(HERE, 'cache'); os.makedirs(d, exist_ok=True)
    return os.path.join(d, '%s-%s.npz' % (name, tag))


def put(name, tag, vol, L, centre):
    np.savez_compressed(cache_path(name, tag), bits=np.packbits(vol), shape=vol.shape, L=L, centre=np.array(centre, float))


def take(name, tag):
    p = cache_path(name, tag)
    if not os.path.exists(p):
        return None
    d = np.load(p); sh = tuple(int(v) for v in d['shape'])
    return np.unpackbits(d['bits'])[:sh[0] * sh[1] * sh[2]].astype(bool).reshape(sh), float(d['L']), tuple(float(v) for v in d['centre'])


def piece_point(lab, piece, h, origin):
    """A point of the piece itself nearest its centre of mass (the centre of a ring or a horseshoe is not on it)."""
    idx = np.flatnonzero(lab == piece['label'])
    i, j, k = np.unravel_index(idx, lab.shape)
    P = np.stack([origin[0] + i * h, origin[1] + j * h, origin[2] + k * h], 1)
    q = np.argmin(((P - np.array(piece['centre'])) ** 2).sum(1))
    return tuple(float(v) for v in P[q])


def on_centre_body(vol, L, centre, level_name, axis_ref):
    """In a close-up box centred on a bud: wear it down, find the bud's own core and what comes off the bud.
    Returns dict and (labels of residue, list of sub-buds)."""
    N = vol.shape[0]; h = 2 * L / (N - 1); org = [centre[d] - L for d in range(3)]
    rv = (L / 9.0) / h
    op, res = wear(vol, rv)
    labo, npo = ndimage.label(op, structure=FULL)
    m = N // 2
    a = labo[m, m, m]
    if a == 0 and npo:
        d = ndimage.distance_transform_edt(labo == 0, return_indices=True)[1][:, m, m, m]
        a = labo[d[0], d[1], d[2]]
    out = dict(box_side=2 * L, wear_radius=L / 9.0, step=h, sub_buds=0, sub_buds_off_plane=0, roundness=None, necks=0, phis=[])
    if a == 0:
        return out, None, []
    A = labo == a
    sizes = np.bincount(labo.ravel())
    others = np.isin(labo, [q for q in range(1, npo + 1) if q != a and sizes[q] >= 0.05 * sizes[a]])
    nearA = ndimage.distance_transform_edt(~A) <= 3.5
    nearB = ndimage.distance_transform_edt(~others) <= 3.5 if others.any() else np.zeros_like(A)
    labr, ps = pieces(res, h, org)
    cA = np.array(ndimage.center_of_mass(A)) * h + np.array(org)
    e = np.array([0.0, axis_ref[1], axis_ref[2]]); e /= max(np.linalg.norm(e), 1e-12)
    nb = np.array([0.0, -e[2], e[1]])                     # across the bud's own plane (the plane through the x-axis and the bud)
    subs = []
    for p in ps:
        if p['voxels'] < vmin(rv):
            continue
        mk = labr == p['label']
        if not nearA[mk].any():
            continue
        if nearB[mk].any():
            out['necks'] += 1; continue
        d = np.array(p['centre']) - cA
        p['off'] = bool(abs(d @ nb) > SIN20 * np.linalg.norm(d))
        subs.append(p)
    out['sub_buds'] = len(subs); out['sub_buds_off_plane'] = sum(p['off'] for p in subs)
    out['roundness'] = roundness(subs)
    out['skin_evenness'] = skin_evenness(vol)
    out['relief'] = skin_relief(vol)
    out['loose_pct'] = loose_pct(vol)
    out['core_centre'] = [float(v) for v in cA]
    return out, labr, subs


# ------------------------------------------------------------------ tiles and sheets
def save_tile(rule, name, img):
    d = os.path.join(HERE, 'tiles', rule); os.makedirs(d, exist_ok=True)
    Image.fromarray(img).save(os.path.join(d, name + '.png'))


def load_tile(rule, name, size):
    p = os.path.join(HERE, 'tiles', rule, name + '.png')
    if not os.path.exists(p):
        return Image.new('RGB', (size, size), (18, 20, 26))
    return Image.open(p).convert('RGB').resize((size, size), Image.LANCZOS)


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ stage 1: the basilica
def stage1(name, N=321):
    F = R.get(name); t0 = time.time(); res = dict(rule=name, label=R.RULES[name][1], known=R.RULES[name][2])
    trap = trap_radius(F); res['trap'] = trap
    log('[%s] trap radius %.2f' % (name, trap))
    kw = dict(trap=trap)

    # J1: the cut at z = 0 against the flat basilica, 801 x 801
    ins, death = cut(F, 'z', n=801); flat = flat_set(n=801)
    res['J1'] = dict(differ=int((ins ^ flat).sum()), flat_points=int(flat.sum()))
    save_tile(name, 'cut_z0', cut_img(ins, death))
    for pl, at, L, tag in (('y', 0.0, 1.75, 'cut_y0'), ('x', 0.0, 1.2, 'cut_x0'), ('x', ALPHA, 1.2, 'cut_xa')):
        i2, d2 = cut(F, pl, at, L=L, n=601); save_tile(name, tag, cut_img(i2, d2))
        if tag == 'cut_x0': a0 = i2
        if tag == 'cut_xa': aa = i2
    log('[%s] J1 differ %d of %d  (%.0f s)' % (name, res['J1']['differ'], res['J1']['flat_points'], time.time() - t0))

    # J2: the touching point (ALPHA, 0, 0)
    b = np.linspace(-1.2, 1.2, 601); disc = (b[:, None] ** 2 + b[None, :] ** 2) <= 0.15 ** 2
    t = np.linspace(-1, 1, 20001); t = t[t != 0]
    li, _ = inside(F, np.full_like(t, ALPHA), 0 * t, t)
    Nl, Ll = 201, 0.5
    loc = volume(F, Nl, L=Ll, centre=(ALPHA, 0, 0), **kw); hl = 2 * Ll / (Nl - 1)
    al = np.linspace(-Ll, Ll, Nl); d2 = al[:, None, None] ** 2 + al[None, :, None] ** 2 + al[None, None, :] ** 2
    ia, ib, mm = int(round((0.45 + Ll) / hl)), int(round((-0.38 + Ll) / hl)), Nl // 2
    split = None
    for r in (0.02, 0.03, 0.04, 0.06, 0.08, 0.12, 0.16, 0.24, 0.32):
        lab, _n = ndimage.label(loc & (d2 > r * r))
        if lab[ia, mm, mm] == 0 or lab[ib, mm, mm] == 0 or lab[ia, mm, mm] != lab[ib, mm, mm]:
            split = r; break
    res['J2'] = dict(neck_area_pct=float(100 * aa.sum() / max(a0.sum(), 1)), cut_fill_near_touch_pct=float(100 * aa[disc].mean()),
                     upright_line_inside=float(li.mean() * 2), upright_line_inside_near=float(li[np.abs(t) < 0.2].mean() * 0.4),
                     smallest_ball_that_splits=split)
    log('[%s] J2 %s  (%.0f s)' % (name, res['J2'], time.time() - t0))

    # the solid at N a side
    vol = volume(F, N, **kw); h = 3.5 / (N - 1); m = N // 2
    res['volume'] = float(vol.sum() * h ** 3)
    for tag, az, el in (('front', -60, 22), ('above', -60, 75), ('alongx', 0, 0)):
        save_tile(name, tag, turns.render(vol, az=az, el=el))
    log('[%s] solid %d a side, volume %.3f  (%.0f s)' % (name, N, res['volume'], time.time() - t0))

    # J5: one piece
    lab, n = ndimage.label(vol, structure=FULL); sz = np.bincount(lab.ravel())[1:]
    fat = ndimage.binary_dilation(vol, structure=FULL); lab2, n2 = ndimage.label(fat, structure=FULL)
    s2 = np.bincount(lab2[vol], minlength=n2 + 1)[1:]
    res['J5'] = dict(pieces=int(n), biggest_pct=float(100 * sz.max() / max(vol.sum(), 1)) if n else 0.0,
                     pieces_one_voxel_gap_allowed=int((s2 > 0).sum()), biggest_pct_one_voxel_gap_allowed=float(100 * s2.max() / max(vol.sum(), 1)) if n2 else 0.0)
    del lab, lab2, fat

    # J7: mirrors
    v = float(max(vol.sum(), 1))
    res['J7'] = dict(above_over_below=float(vol[:, :, m + 1:].sum() / max(vol[:, :, :m].sum(), 1)), front_over_back=float(vol[:, m + 1:, :].sum() / max(vol[:, :m, :].sum(), 1)),
                     changed_by_mirror_z_pct=float(100 * (vol ^ vol[:, :, ::-1]).sum() / v), changed_by_mirror_y_pct=float(100 * (vol ^ vol[:, ::-1, :]).sum() / v))
    log('[%s] J5 %s J7 %s  (%.0f s)' % (name, res['J5'], res['J7'], time.time() - t0))

    # J3 (first half): share of the solid that changes when it is turned about the x-axis (161 a side, exact re-sampling)
    v0 = volume(F, 161, **kw)
    res['J3'] = {}
    for ang in (45.0, 22.5):
        vt = volume(F, 161, turn=ang, **kw)
        res['J3']['changed_by_turn_%s_pct' % ang] = float(100 * (v0 ^ vt).sum() / max(v0.sum(), 1))
    del v0, vt

    # J4, J3 (second half), J8: wear the middle body down by 0.11 and look at what comes off
    hw = int(round(1.0 / h)); cube = vol[m - hw:m + hw + 1, m - hw:m + hw + 1, m - hw:m + hw + 1]; org = [-hw * h] * 3
    rad1 = 0.11; rv = rad1 / h
    op, rs = wear(cube, rv); lab1, ps = pieces(rs, h, org)
    ps = [p for p in ps if p['voxels'] >= vmin(rv) and abs(p['centre'][0]) <= 0.5]
    rings = [p for p in ps if p['extent'] >= 300 and p['rho'] > 0.15]
    buds = [p for p in ps if not (p['extent'] >= 300) and p['rho'] > 0.1]
    for p in buds:
        p['off'] = bool(abs(np.sin(np.radians(p['phi']))) > SIN20)
    off = [p for p in buds if p['off']]
    wv = float(sum(p['voxels'] for p in ps)) or 1.0
    res['J3'].update(rings_on_middle_body=len(rings), ring_share_of_what_comes_off_pct=float(100 * sum(p['voxels'] for p in rings) / wv))
    res['J4'] = dict(wear_radius=rad1, buds_on_middle_body=len(buds), buds_off_flat_plane=len(off),
                     directions_of_biggest=[round(p['phi']) for p in buds[:10]], sizes_of_biggest=[round(p['r_eq'], 3) for p in buds[:10]],
                     sectors_30deg_with_a_bud=len({int(((p['phi'] + 15) % 360) // 30) for p in buds}))
    res['J8'] = dict(roundness_1=roundness(buds + rings), relief_1=skin_relief(cube),
                     ripple_1=outline_ripple(F, (0, 0, 0), (0, 1, 0), (0, 0, 1), 1.0, **kw))       # the middle body cut across at x = 0
    res['J4']['round_buds_off_flat_plane'] = sum(p['round'] >= 0.45 for p in off)
    put(name, 'solid', vol, 1.75, (0, 0, 0))
    save_tile(name, 'close1', turns.render(np.ascontiguousarray(cube), az=-60, el=22))
    log('[%s] J3 %s\n[%s] J4 %s  (%.0f s)' % (name, res['J3'], name, res['J4'], time.time() - t0))

    # level 2: close-up of one bud (the biggest that stands off the flat plane; if none, the biggest)
    cand = (off or buds or rings)
    if cand:
        b1 = cand[0]; pt = piece_point(lab1, b1, h, org)
        L2 = float(np.clip(2.2 * b1['r_eq'], 0.10, 0.30))
        v2 = volume(F, 161, L=L2, centre=pt, **kw)
        save_tile(name, 'close2', turns.render(v2, az=-60, el=22))
        o2, labr2, subs = on_centre_body(v2, L2, pt, 'bud', pt)
        res['J4']['bud_looked_at'] = dict(centre=[round(x, 4) for x in pt], phi=round(b1['phi']), r_eq=round(b1['r_eq'], 4), off_flat_plane=bool(b1.get('off', False)))
        res['J4']['on_the_bud'] = {k: o2[k] for k in ('box_side', 'wear_radius', 'sub_buds', 'sub_buds_off_plane', 'necks')}
        res['J8'].update(roundness_2=o2['roundness'], evenness_2=o2.get('skin_evenness'), relief_2=o2.get('relief'))
        res['J5']['loose_in_close_up_2_pct'] = o2.get('loose_pct')
        put(name, 'close2', v2, L2, pt)
        e = np.array([0.0, pt[1], pt[2]]); e /= max(np.linalg.norm(e), 1e-12); cA = o2.get('core_centre', list(pt))
        ic, dc = cut_plane(F, cA, (1.0, 0.0, 0.0), (0.0, -e[2], e[1]), L2 * 0.62, n=501)      # the bud cut across, square to its own axis
        save_tile(name, 'bud_across', cut_img(ic, dc))
        res['J8']['ripple_2'] = outline_ripple(F, cA, (1.0, 0.0, 0.0), (0.0, -e[2], e[1]), L2 * 0.9, **kw)
        res['J4']['on_the_bud']['round_sub_buds'] = sum(p['round'] >= 0.45 for p in subs)
        log('[%s] bud %s -> %s  (%.0f s)' % (name, res['J4']['bud_looked_at'], o2, time.time() - t0))
        # level 3: close-up of the biggest thing on that bud
        if subs:
            b2 = subs[0]; N2 = v2.shape[0]; h2 = 2 * L2 / (N2 - 1); org2 = [pt[d] - L2 for d in range(3)]
            pt3 = piece_point(labr2, b2, h2, org2)
            L3 = float(np.clip(2.2 * b2['r_eq'], 0.012, L2 / 3))
            v3 = volume(F, 129, L=L3, centre=pt3, steps=80, **kw)
            save_tile(name, 'close3', turns.render(v3, az=-60, el=22))
            o3, _l, subs3 = on_centre_body(v3, L3, pt3, 'sub-bud', pt3)
            res['J4']['on_the_sub_bud'] = {k: o3[k] for k in ('box_side', 'wear_radius', 'sub_buds', 'sub_buds_off_plane', 'necks')}
            res['J4']['sub_bud_looked_at'] = dict(centre=[round(x, 5) for x in pt3], r_eq=round(b2['r_eq'], 5))
            res['J8'].update(roundness_3=o3['roundness'], evenness_3=o3.get('skin_evenness'), relief_3=o3.get('relief'))
            res['J5']['loose_in_close_up_3_pct'] = o3.get('loose_pct')
            put(name, 'close3', v3, L3, pt3)
            c3 = np.array(o3.get('core_centre', list(pt3))); u3, w3 = perp_pair(c3 - np.array(cA))   # the small body cut across, square to the line from its bud
            res['J8']['ripple_3'] = outline_ripple(F, c3, u3, w3, L3 * 0.9, steps=80, **kw)
            i3, d3 = cut_plane(F, c3, u3, w3, L3 * 0.62, n=401, steps=80); save_tile(name, 'sub_across', cut_img(i3, d3))
            res['J4']['on_the_sub_bud']['round_sub_buds'] = sum(p['round'] >= 0.45 for p in subs3)
            log('[%s] sub-bud -> %s  (%.0f s)' % (name, o3, time.time() - t0))

    # J6: the jump test
    res['J6'] = jump_test(F)
    log('[%s] J6 %s' % (name, res['J6']))
    res['seconds'] = time.time() - t0
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, 'results', name + '.json'), 'w'), indent=1)
    rule_sheet(name)
    return res


def jump_test(F, n=200000, seed=5):
    """Close pairs at three step sizes (as in the scouts), and a hunt: 200,000 segments of length about 0.03 are
    halved 26 times, each time keeping the half over which the rule moves more. A tear keeps its jump; a rule
    without a tear ends with a jump about as small as the last segment (5e-10)."""
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, 3)); A *= (rng.uniform(0.3, 1.5, n) / np.linalg.norm(A, axis=1))[:, None]
    out = {}
    fa = np.stack(F(*A.T), 1)
    for hstep in (1e-4, 1e-5, 1e-6):
        B = A + hstep * rng.normal(size=A.shape)
        out['largest_jump_step_%g' % hstep] = float(np.linalg.norm(fa - np.stack(F(*B.T), 1), axis=1).max())
    B = A + 0.02 * rng.normal(size=A.shape); A = A.copy(); fb = np.stack(F(*B.T), 1)
    for it in range(26):
        M = 0.5 * (A + B); fm = np.stack(F(*M.T), 1)
        left = (np.linalg.norm(fm - fa, axis=1) >= np.linalg.norm(fb - fm, axis=1))[:, None]
        B = np.where(left, M, B); fb = np.where(left, fm, fb); A = np.where(left, A, M); fa = np.where(left, fa, fm)
    j = np.linalg.norm(fa - fb, axis=1); s = np.linalg.norm(A - B, axis=1)
    q = int(np.argmax(j))
    out.update(hunt_largest_jump=float(j.max()), hunt_separation=float(s[q]), hunt_where=[float(v) for v in A[q]],
               hunt_segments_with_jump_over_1e_3=int((j > 1e-3).sum()))
    out.update(axis_test(F))
    return out


def axis_test(F, n=100000, seed=9):
    """The x-axis is a line, so random segments never cross it and the hunt cannot see it. Here: pairs of points at
    the same x and the same small distance eps from the axis but in unrelated directions round it. No tear at the
    axis means the largest jump shrinks with eps."""
    rng = np.random.default_rng(seed); x = rng.uniform(-1.5, 1.5, n); p1 = rng.uniform(0, 2 * np.pi, n); p2 = rng.uniform(0, 2 * np.pi, n)
    out = {}
    for eps in (1e-3, 1e-6, 1e-9):
        a = np.stack(F(x, eps * np.cos(p1), eps * np.sin(p1)), 1); b = np.stack(F(x, eps * np.cos(p2), eps * np.sin(p2)), 1)
        out['axis_jump_eps_%g' % eps] = float(np.linalg.norm(a - b, axis=1).max())
    return out


# ------------------------------------------------------------------ verdicts (thresholds: see README.md, from the calibration table)
def verdicts(r):
    v = {}
    J = r
    v['J1'] = (J['J1']['differ'] <= 8, '%d of %d points differ' % (J['J1']['differ'], J['J1']['flat_points']))
    s = J['J2']['smallest_ball_that_splits']
    v['J2'] = (s is not None and s <= 0.04 and J['J2']['upright_line_inside_near'] <= 0.004 and J['J2']['cut_fill_near_touch_pct'] <= 1.0,
               '%s; length of solid on the upright line within 0.2 of the touching point %.3f; the cut there is %.2f %% full within 0.15 of the axis' % (
                   ('taking out a ball of radius %.2f at the touching point parts the bodies' % s) if s else 'even a ball of radius 0.32 at the touching point does not part the bodies',
                   J['J2']['upright_line_inside_near'], J['J2']['cut_fill_near_touch_pct']))
    t = min(J['J3']['changed_by_turn_45.0_pct'], J['J3']['changed_by_turn_22.5_pct'])
    v['J3'] = (t >= 0.5 and J['J3']['rings_on_middle_body'] == 0, 'a turn about the x-axis changes %.1f %% of it; %d rings come off the middle body' % (t, J['J3']['rings_on_middle_body']))
    ob = J['J4'].get('on_the_bud', {}); osb = J['J4'].get('on_the_sub_bud', {})
    v['J4'] = (J['J4'].get('round_buds_off_flat_plane', 0) >= T_J4_OFF and ob.get('round_sub_buds', 0) >= 2 and ob.get('sub_buds_off_plane', 0) >= 1 and osb.get('round_sub_buds', 0) >= 2,
               '%d buds on the middle body, %d off the flat plane (%d of them round); on one bud %d smaller ones (%d round, %d off its own plane); on one of those %d (%d round)' % (
                   J['J4']['buds_on_middle_body'], J['J4']['buds_off_flat_plane'], J['J4'].get('round_buds_off_flat_plane', 0), ob.get('sub_buds', 0), ob.get('round_sub_buds', 0),
                   ob.get('sub_buds_off_plane', 0), osb.get('sub_buds', 0), osb.get('round_sub_buds', 0)))
    l2, l3 = J['J5'].get('loose_in_close_up_2_pct'), J['J5'].get('loose_in_close_up_3_pct')
    v['J5'] = (J['J5']['biggest_pct_one_voxel_gap_allowed'] >= T_J5 and max(l2 or 0, l3 or 0) <= T_J5_LOOSE,
               'biggest piece holds %.3f %% (a one-voxel gap allowed; %.2f %% with none allowed, %d pieces); loose matter in the two close-ups %s %% and %s %%' % (
                   J['J5']['biggest_pct_one_voxel_gap_allowed'], J['J5']['biggest_pct'], J['J5']['pieces'], 'none' if l2 is None else '%.2f' % l2, 'none' if l3 is None else '%.2f' % l3))
    v['J6'] = (J['J6']['hunt_largest_jump'] < 1e-4, 'largest jump found %.1e over a gap of %.0e' % (J['J6']['hunt_largest_jump'], J['J6']['hunt_separation']))
    mz, my = J['J7']['changed_by_mirror_z_pct'], J['J7']['changed_by_mirror_y_pct']
    v['J7'] = (max(mz, my) <= 0.5, 'mirror above/below changes %.2f %%, front/back %.2f %%' % (mz, my))
    r8 = [J['J8'].get('roundness_%d' % k) for k in (1, 2, 3)]
    rp = []
    for k in (1, 2, 3):          # an outline that more than 72 of the 1,440 rays never left is not an outline of a body: no number
        d = J['J8'].get('ripple_%d' % k) or {}
        rp.append(d.get('ripple_pct') if d.get('rays_that_never_left', 0) <= 72 else None)
    ok8 = all(x is not None and x >= T_J8_ROUND for x in r8) and all(x is not None and x <= T_J8_RIPPLE for x in rp)
    v['J8'] = (ok8, 'at 3 sizes: what comes off is round to %s (1 = balls; under %.2f = streaks, sheets, tubes); ribs on the outline %s %% of the radius (over %.2f = ribbed; none = could not be measured)' % (
        ', '.join('none' if x is None else '%.2f' % x for x in r8), T_J8_ROUND, ', '.join('none' if x is None else '%.2f' % x for x in rp), T_J8_RIPPLE))
    return v


# Thresholds. Each sits between the rules whose verdict was known beforehand (see README.md for the table).
T_J4_OFF = 2          # round buds off the flat plane on the middle body: one plane has 0, the reference 6
T_J5 = 99.97          # per cent in the biggest piece, a one-voxel gap allowed: reference 100.000, Mandelbulb (loose shards in the picture) 99.943
T_J5_LOOSE = 0.03     # per cent of loose matter in a close-up box: reference 0.00, Mandelbulb 0.06 to 0.08
T_J8_ROUND = 0.45     # roundness of what comes off: reference 0.71 to 0.74; Mandelbulb, pillow, lathe 0.02 to 0.27
T_J8_RIPPLE = 0.45    # ribs, per cent of the radius: reference 0.04 to 0.21, one plane 0.00; half way to the first ribbed rule seen (0.69)


def load(name):
    p = os.path.join(HERE, 'results', name + '.json')
    return json.load(open(p)) if os.path.exists(p) else None


def passed_stage1(name):
    r = load(name)
    return r is not None and all(ok for ok, _ in verdicts(r).values())


def table(names=None):
    names = names or [n for n in R.RULES if load(n)]
    lines = []
    for n in names:
        r = load(n); v = verdicts(r)
        lines.append('%-11s %s   %s' % (n, ' '.join('%s:%s' % (k, 'pass' if ok else 'FAIL') for k, (ok, _) in v.items()), R.RULES[n][2]))
        for k, (ok, txt) in v.items():
            lines.append('      %s %s  %s' % (k, 'pass' if ok else 'FAIL', txt))
    return '\n'.join(lines)


def rule_sheet(name, S=300):
    r = load(name); v = verdicts(r)
    tiles = [('front', 'Front'), ('above', 'From above'), ('alongx', 'Along the x-axis'), ('cut_z0', 'Cut z = 0'), ('cut_y0', 'Cut y = 0'),
             ('cut_x0', 'Cut x = 0'), ('cut_xa', 'Cut x = -0.618'), ('close1', 'Close-up 1: middle body'), ('close2', 'Close-up 2: one bud'), ('close3', 'Close-up 3: on that bud')]
    W = S * len(tiles) + 20; H = 60 + S + 22 * 9 + 20
    im = Image.new('RGB', (W, H), (12, 14, 20)); dr = ImageDraw.Draw(im); f1, f2 = turns.font(20), turns.font(15)
    dr.text((12, 8), 'Basilica (c = -1), rule: %s   [%s]' % (r['label'], name), fill=(240, 240, 240), font=f1)
    for k, (tag, ttl) in enumerate(tiles):
        dr.text((14 + k * S, 38), ttl, fill=(210, 210, 210), font=f2); im.paste(load_tile(name, tag, S - 6), (10 + k * S, 60))
    y = 60 + S + 6
    for k, (ok, txt) in v.items():
        dr.text((14, y), '%s  %s   %s' % (k, 'pass' if ok else 'FAIL', txt), fill=(150, 220, 150) if ok else (240, 130, 120), font=f2); y += 22
    os.makedirs(os.path.join(HERE, 'sheets'), exist_ok=True)
    p = os.path.join(HERE, 'sheets', name + '.png'); im.save(p); return p


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'table'
    if cmd == 'stage1':
        for nm in sys.argv[2:]:
            stage1(nm)
            log(table([nm]))
    elif cmd in ('stage2', 'lights'):
        import stage2 as S2
        for nm in sys.argv[2:]:
            (S2.stage2 if cmd == 'stage2' else S2.lights)(nm)
    elif cmd == 'reripple':
        for nm in sys.argv[2:]:
            reripple(nm)
    elif cmd == 'sheets':
        for nm in sys.argv[2:] or [n for n in R.RULES if load(n)]:
            log(rule_sheet(nm))
    else:
        log(table(sys.argv[2:] or None))
