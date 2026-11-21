"""Round 27, checker A, bullet 2, my side: a brute-force picture with the lab's camera, and the comparison.

The brute-force picture is NOT a ray march and uses no distance estimate: it is the list of all balls (walking the
group, ballslib.enum_cell) seen through the lab's camera, each ball cut by each ray with the exact formula for a ray
and a sphere. One ray through the centre of each picture pixel, the lab's own ray (uCam, uFov, uRes as in main()).
Balls with a radius of at least 0.2 pixels are in it.
Compared with the lab:
  A. the lab's finished picture (PNG of the canvas): which pixels show something (not the stage colour) against
     which pixel-centre rays hit a ball. Only "the lab shows something where the reference has nothing" is used:
     the other way round fails in deep creases, where the lab's shading is as dark as the stage.
  B. the lab's pick() on a grid of pixels (every pixel, or every second pixel of every second row): where the lab's
     ray stops, against where the reference ray first meets a ball. Holes (reference hits, lab does not stop),
     passed-through balls (lab stops more than a pixel behind), extra stops, how far the lab's stopping points are
     from the nearest ball of the list, and ball by ball whether the lab loses it.
  python views_ref.py <name> ...   -> ../views/<name>-ref.png, <name>-diff.png, ../logs/views.json (one entry per name)
"""
import json, os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import ballslib as B
import drive as D

VDIR = os.path.join(D.CHK, 'views')
CACHE = os.environ.get('CHECKA_CACHE', os.path.join(os.environ.get('TEMP', '.'), 'checka-cache'))
os.makedirs(CACHE, exist_ok=True)
RHO = {(0, 1.4): 1e-4, (1, 1.4): 1e-4, (2, 1.4): 2e-6, (0, 2.5): 1e-4, (0, 1.0): 2e-4, (0, 1.05): 2e-4}
KISS = np.array([1.05 / 2, 0.0, 0.0])
MINPX = 0.2      # balls with a radius of at least this many pixels are in the reference (t = 1: 1 pixel, see minpx)


def minpx(t):
    return MINPX if t > 1.2 else 1.0


def cell_for(g, t):
    f = os.path.join(CACHE, 'cell-g%d-t%g.npz' % (g, t))
    rho = RHO[(g, t)]
    if os.path.exists(f):
        z = np.load(f)
        return dict(c=z['c'], r=z['r'], lev=z['lev'], t=t, grid=g, rho=rho)
    cell = B.enum_cell(t, g, rho)
    np.savez(f, c=cell['c'], r=cell['r'], lev=cell['lev'])
    return cell


def camera(info):
    b = info['basis']; w, h = info['stage']
    return dict(ro=np.array(b['pos']), right=np.array(b['right']), up=np.array(b['up']), f=np.array(b['f']), fov=info['fov'], w=w, h=h,
                pix=2 * info['fov'] / h, dist=info['cam']['dist'])


def rays(cam, px, py):
    """Unit ray directions through stage positions (px, py), CSS pixels from the top left corner."""
    ux = (2 * px - cam['w']) / cam['h'] * cam['fov']; uy = (cam['h'] - 2 * py) / cam['h'] * cam['fov']
    d = ux[..., None] * cam['right'] + uy[..., None] * cam['up'] + cam['f']
    return d / np.linalg.norm(d, axis=-1, keepdims=True)


def view_balls(cell, cam):
    ro, f, right, up = cam['ro'], cam['f'], cam['right'], cam['up']
    asp = cam['w'] / cam['h']; fov = cam['fov']; pix = cam['pix']; MP = minpx(cell['t'])

    def keep(C, R):
        v = C - ro
        zc = v @ f
        m = zc > 1e-4
        m &= R >= MP * pix * np.maximum(zc, 1e-9)
        m &= np.abs(v @ right) <= fov * asp * zc * 1.03 + 1.6 * R
        m &= np.abs(v @ up) <= fov * zc * 1.03 + 1.6 * R
        return m
    # the nearest a ball can stand to the eye: a tenth of the distance to the target is a safe floor for these views
    znear = max(0.1 * cam['dist'], 0.004)
    t = cell['t']

    def per_n(n, ln):
        # where the balls slid by n land in the picture: skip the whole number if that is out of sight, and ask only
        # for the sizes that can be seen from that far
        cen, rad = B.column_ball(n, t)
        v = cen - ro
        zc = v @ f
        if zc + rad < znear:
            return None
        zfar = zc + rad
        if abs(v @ right) - rad > fov * asp * zfar * 1.03 + 0.05 or abs(v @ up) - rad > fov * zfar * 1.03 + 0.05:
            return None
        return MP * pix * max(znear, zc - rad)
    return B.picture_balls(cell, MP * pix * znear, keep=keep, per_n=per_n)


def render(cam, C, R):
    """Exact picture of the balls: for every pixel the distance along its ray to the first ball, and that ball."""
    w, h = cam['w'], cam['h']; ro = cam['ro']
    PX, PY = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    Dr = rays(cam, PX, PY)                                       # h x w x 3
    depth = np.full((h, w), np.inf); ball = np.full((h, w), -1, np.int64)
    v = C - ro
    zc = v @ cam['f']
    sx = (v @ cam['right']) / (zc * cam['fov']); sy = (v @ cam['up']) / (zc * cam['fov'])
    cx = (sx * h + w) / 2; cy = (h - sy * h) / 2
    dist = np.linalg.norm(v, axis=1)
    rp = R / (zc * cam['fov']) * h / 2 / np.sqrt(np.maximum(1 - (R / dist) ** 2, 1e-6)) * np.sqrt(1 + (sx * cam['fov']) ** 2 + (sy * cam['fov']) ** 2)
    rb = rp * 1.15 + 1.2
    big = np.nonzero(rb > 3.5)[0]
    for i in big[np.argsort(-R[big])]:
        x0 = max(0, int(np.floor(cx[i] - rb[i]))); x1 = min(w, int(np.ceil(cx[i] + rb[i])) + 1)
        y0 = max(0, int(np.floor(cy[i] - rb[i]))); y1 = min(h, int(np.ceil(cy[i] + rb[i])) + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        d = Dr[y0:y1, x0:x1]
        oc = ro - C[i]
        b = d @ oc; cq = oc @ oc - R[i] * R[i]
        disc = b * b - cq
        hit = disc > 0
        s = np.where(hit, -b - np.sqrt(np.where(hit, disc, 0.0)), np.inf)
        s = np.where(s > 0, s, np.inf)
        sub = depth[y0:y1, x0:x1]; sb = ball[y0:y1, x0:x1]
        m = s < sub
        sub[m] = s[m]; sb[m] = i
    small = np.nonzero(rb <= 3.5)[0]
    if small.size:
        ix = np.round(cx[small] - 0.5).astype(int); iy = np.round(cy[small] - 0.5).astype(int)
        pix_l, s_l, b_l = [], [], []
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                jx = ix + dx; jy = iy + dy
                ok = (jx >= 0) & (jx < w) & (jy >= 0) & (jy < h) & (np.hypot(jx + 0.5 - cx[small], jy + 0.5 - cy[small]) <= rb[small] + 0.8)
                if not ok.any():
                    continue
                k = small[ok]
                d = Dr[jy[ok], jx[ok]]
                oc = ro - C[k]
                b = (d * oc).sum(1); cq = (oc * oc).sum(1) - R[k] ** 2
                disc = b * b - cq
                hit = disc > 0
                s = -b[hit] - np.sqrt(disc[hit])
                good = s > 0
                pix_l.append((jy[ok][hit] * w + jx[ok][hit])[good]); s_l.append(s[good]); b_l.append(k[hit][good])
        if pix_l:
            pp = np.concatenate(pix_l); ss = np.concatenate(s_l); bb = np.concatenate(b_l)
            o = np.lexsort((ss, pp)); pp, ss, bb = pp[o], ss[o], bb[o]
            first = np.concatenate([[True], pp[1:] != pp[:-1]])
            pp, ss, bb = pp[first], ss[first], bb[first]
            df = depth.ravel(); bf = ball.ravel()
            m = ss < df[pp]
            df[pp[m]] = ss[m]; bf[pp[m]] = bb[m]
    return depth, ball, Dr


def widest(mask):
    """Number of pixels, and the diameter of the largest disc that fits inside one blob of the mask."""
    n = int(mask.sum())
    if not n:
        return 0, 0.0, None
    e = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    j = np.unravel_index(e.argmax(), e.shape)
    return n, float(2 * e.max() - 1), [int(j[1]), int(j[0])]


def one(name):
    info = json.load(open(os.path.join(VDIR, name + '.json'), encoding='utf-8'))
    g, t, rounds = info['grid'], info['t'], info['rounds']
    cam = camera(info)
    t0 = time.time()
    cell = cell_for(g, t)
    C, R, Lv = view_balls(cell, cam)
    depth, ball, Dr = render(cam, C, R)
    w, h = cam['w'], cam['h']; ro = cam['ro']; pix = cam['pix']
    out = dict(name=name, grid=g, t=t, rounds=rounds, balls=int(R.size), cell=int(cell['r'].size), cam=info['cam'], min_radius_px=minpx(t))
    # where the list is complete down to MINPX pixels: radius >= rho * P' / k^2, P' the squared distance from the kiss
    ref = np.isfinite(depth)
    hitp = ro + Dr * np.where(ref, depth, 0.0)[..., None]
    dk = np.linalg.norm(hitp - KISS, axis=-1)
    MP = minpx(t)
    zone = cell['rho'] * dk ** 2 / B.K2 <= MP * pix * np.where(ref, depth, 1.0)
    # ---------------- A. the lab's picture, by colour
    img = np.asarray(Image.open(os.path.join(VDIR, name + '.png')).convert('RGB')).astype(int)
    if img.shape[0] != h or img.shape[1] != w:
        out['error'] = 'the picture is %s, the stage %s' % (img.shape, (h, w)); return out
    cols, counts = np.unique(img.reshape(-1, 3), axis=0, return_counts=True)
    bg = cols[counts.argmax()]
    lab = np.abs(img - bg).max(2) > 10
    out['stage_colour'] = [int(c) for c in bg]; out['lab_coloured_pixels'] = int(lab.sum()); out['ref_object_pixels'] = int(ref.sum())
    out['ref_complete_share'] = float(zone[ref].mean()) if ref.any() else 1.0
    cadd = lab & ~ref
    far = ~ndimage.binary_dilation(ref, iterations=3)
    n, d, at = widest(far & lab)
    out['colour_added_pixels'] = int(cadd.sum()); out['colour_added_over_3px_outside'] = n; out['colour_added_over_3px_outside_widest_px'] = d; out['colour_added_over_3px_outside_at'] = at
    out['colour_dark_inside_pixels'] = int((ref & ~lab).sum())
    # ---------------- B. the lab's picks, on a grid of pixels
    step = info['step']
    sd = np.load(os.path.join(VDIR, name + '-picks.npy'))
    lab_hit = sd > 0
    s_ref = depth[::step, ::step]; b_ref = ball[::step, ::step]; r_hit = np.isfinite(s_ref); dr = Dr[::step, ::step]
    assert sd.shape == s_ref.shape, (sd.shape, s_ref.shape)
    lp = ro + dr * sd[..., None]
    bi = np.maximum(b_ref, 0)
    oc = ro - C[bi]
    bq = (dr * oc).sum(-1); disc = np.maximum(bq * bq - ((oc * oc).sum(-1) - R[bi] ** 2), 0)
    sr = np.where(r_hit, s_ref, 1.0)
    chord_px = np.where(r_hit, 2 * np.sqrt(disc) / (pix * sr), 0.0)
    rad_px = np.where(r_hit, R[bi] / (pix * sr), 0.0)
    nb = B.NearBalls(C, R)
    float_px = np.zeros(sd.shape)
    if lab_hit.any():
        float_px[lab_hit] = nb.dist(lp[lab_hit]) / (pix * sd[lab_hit])
    dkl = np.linalg.norm(lp - KISS, axis=-1)
    okz = np.where(r_hit, zone[::step, ::step], True) & np.where(lab_hit, cell['rho'] * dkl ** 2 / B.K2 <= MP * pix * np.where(lab_hit, sd, 1.0), True)
    hole = r_hit & ~lab_hit & okz; extra = lab_hit & ~r_hit & okz; both = r_hit & lab_hit & okz
    dz_px = np.where(both, (s_ref - sd) / (pix * sr), 0.0)                 # > 0: the lab stops in front of the reference
    behind = both & (dz_px < -1.0)
    bad = hole | behind                                                    # the reference's first ball is not where the lab stops
    out.update(pick_step=step, picks=int(sd.size), outside_complete_zone=int((~okz).sum()), lab_stops=int((lab_hit & okz).sum()),
               ref_hits=int((r_hit & okz).sum()), both=int(both.sum()))

    def blobs(mask, weight):
        n = int(mask.sum())
        if not n:
            return dict(points=0, blobs=0, largest_blob_points=0, widest_px=0.0, at=None, weight_max=0.0)
        lab_, k = ndimage.label(mask, structure=np.ones((3, 3)))
        e = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
        j = np.unravel_index(e.argmax(), e.shape)
        sizes = np.bincount(lab_.ravel())[1:]
        return dict(points=n, blobs=int(k), largest_blob_points=int(sizes.max()), widest_px=float((2 * e.max() - 1) * step),
                    at=[int(j[1] * step), int(j[0] * step)], weight_max=float(weight[mask].max()))
    out['holes'] = blobs(hole, chord_px)             # weight: chord of the missed ball along the ray, px
    out['holes_chord_over_1px'] = int((hole & (chord_px > 1)).sum()); out['holes_chord_over_2px'] = int((hole & (chord_px > 2)).sum())
    out['behind'] = blobs(behind, chord_px)
    out['behind_chord_over_2px'] = int((behind & (chord_px > 2)).sum())
    out['extra'] = blobs(extra, float_px)            # weight: how far the lab's point is from the nearest listed ball, px
    out['extra_float_over_1.5px'] = int((extra & (float_px > 1.5)).sum()); out['extra_float_over_2px'] = int((extra & (float_px > 2)).sum())
    fl = lab_hit & okz
    out['floating_over_2px'] = blobs(fl & (float_px > 2), float_px)
    out['floating_over_4px'] = int((fl & (float_px > 4)).sum())
    out['float_median_px'] = float(np.median(float_px[fl])) if fl.any() else 0.0
    out['float_p99_px'] = float(np.percentile(float_px[fl], 99)) if fl.any() else 0.0
    out['float_max_px'] = float(float_px[fl].max()) if fl.any() else 0.0
    out['deepest_inside_a_ball_px'] = float(max(0.0, -float_px[fl].min())) if fl.any() else 0.0
    # ball by ball: of the grid points the reference gives to a ball, how many does the lab miss or pass through?
    sel = r_hit & okz
    own = np.bincount(b_ref[sel], minlength=R.size); lost = np.bincount(b_ref[bad], minlength=R.size)
    brad = np.zeros(R.size); np.maximum.at(brad, b_ref[sel], rad_px[sel])
    cand = (own >= 3) & (lost >= 0.5 * own)
    out['balls_seen_on_3_points_or_more'] = int((own >= 3).sum())
    out['balls_missing'] = int(cand.sum())
    out['largest_missing_ball_diameter_px'] = float(2 * brad[cand].max()) if cand.any() else 0.0
    idx = np.nonzero(cand)[0]
    out['missing_balls'] = [dict(radius_px=float(brad[i]), radius=float(R[i]), centre=[float(c) for c in C[i]], level=int(Lv[i]), points=int(own[i]), lost=int(lost[i]))
                            for i in idx[np.argsort(-brad[idx])][:8]]
    out['balls_partly_lost'] = int(((own >= 3) & (lost > 0) & ~cand).sum())
    bigb = (own >= 3) & (brad > 3)
    out['largest_share_lost_of_a_ball_over_6px'] = float((lost / np.maximum(own, 1))[bigb].max()) if bigb.any() else 0.0
    # the smallest balls: of those the reference shows on at least one grid point, by size class, how many does the lab stop on?
    cls = {}
    for lo, hi in ((0.2, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 4.0), (4.0, 1e9)):
        m = (own >= 1) & (brad >= lo) & (brad < hi)
        cls['%g-%g px' % (lo, hi) if hi < 1e8 else 'over %g px' % lo] = [int(m.sum()), int((m & (lost >= own)).sum())]
    out['balls_by_radius_seen_and_fully_lost'] = cls
    # The lab's stopping points that are more than 2 px from every listed ball: is something really there?
    # Probes with the recipe in the little ball of radius 2 px round each such point (120 probes each):
    #   real:      some probe is inside for good (300 rounds reach a wall): a ball the list does not have (too small)
    #   depth:     no such probe, but some probe is still undecided after this view's rounds (the page counts that
    #              as inside): solid that only the depth of the search puts there
    #   nothing:   neither: the lab stopped in the open
    far = fl & (float_px > 2)
    if far.any():
        q = lp[far]; rad = 2 * pix * sd[far]
        rngp = np.random.default_rng(3)
        real = np.zeros(q.shape[0], bool); deep = np.zeros(q.shape[0], bool)
        for k in range(120):
            w_ = rngp.normal(size=q.shape); w_ /= np.linalg.norm(w_, axis=1)[:, None]
            pr = q + w_ * (rad * rngp.uniform(0, 1, q.shape[0]) ** (1 / 3))[:, None]
            s300 = B.recipe_state(pr[:, 0], pr[:, 1], pr[:, 2], t, g, 300)
            sR = B.recipe_state(pr[:, 0], pr[:, 1], pr[:, 2], t, g, rounds)
            real |= s300 == 1
            deep |= (sR == 2) & (s300 != 1)
        kind = np.where(real, 0, np.where(deep, 1, 2))
        cls = np.full(sd.shape, -1); cls[far] = kind
        out['far_points'] = dict(points=int(far.sum()), a_real_ball_within_2px=int((kind == 0).sum()), only_the_depth_puts_solid_there=int((kind == 1).sum()), nothing_there=int((kind == 2).sum()))
        out['solid_by_depth_only'] = blobs(cls == 1, float_px)
        out['stopped_in_the_open'] = blobs(cls == 2, float_px)
    else:
        out['far_points'] = dict(points=0, a_real_ball_within_2px=0, only_the_depth_puts_solid_there=0, nothing_there=0)
        out['solid_by_depth_only'] = blobs(np.zeros(sd.shape, bool), float_px); out['stopped_in_the_open'] = blobs(np.zeros(sd.shape, bool), float_px)
    hl = np.argwhere(hole)
    out['hole_points'] = [dict(pixel=[int(x * step), int(y * step)], chord_px=float(chord_px[y, x]), ball_radius_px=float(rad_px[y, x]), ref_depth=float(s_ref[y, x]),
                               recipe_inside_at_ref_point=bool(B.recipe_inside(*(ro + dr[y, x] * (s_ref[y, x] + 2 * pix * s_ref[y, x])), t, g, rounds))) for y, x in hl[:40]]
    out['seconds'] = round(time.time() - t0)
    # ---------------- pictures: the reference shaded plainly, and the difference
    n = hitp - C[np.maximum(ball, 0)]; n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
    light = np.array([0.35, -0.5, 0.8]); light /= np.linalg.norm(light)
    sh = np.clip(0.25 + 0.75 * np.clip((n * light).sum(-1), 0, 1), 0, 1)
    lvl = Lv[np.maximum(ball, 0)] % 6
    pal = np.array([[150, 170, 255], [120, 220, 200], [240, 200, 110], [240, 140, 140], [200, 150, 240], [170, 230, 130]], float)
    refimg = np.where(ref[..., None], pal[lvl] * sh[..., None], np.array(bg, float))
    Image.fromarray(refimg.astype(np.uint8)).save(os.path.join(VDIR, name + '-ref.png'))
    dimg = np.zeros((h, w, 3), np.uint8); dimg[...] = (16, 18, 24)
    dimg[ref] = (70, 74, 84); dimg[cadd] = (40, 90, 110)
    up = lambda m: np.kron(m, np.ones((step, step), bool))[:h, :w]
    dimg[up(bad)] = (255, 60, 60); dimg[up(fl & (float_px > 2))] = (60, 220, 255)
    Image.fromarray(dimg).save(os.path.join(VDIR, name + '-diff.png'))
    return out


if __name__ == '__main__':
    names = sys.argv[1:]
    f = os.path.join(D.LOGS, 'views.json')
    for name in names:
        r = one(name)
        allr = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {}
        allr[name] = r
        print(json.dumps(r)); sys.stdout.flush()
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(allr, fh, indent=1)
