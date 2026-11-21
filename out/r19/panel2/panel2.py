"""Round 19: panel2, the Julia panel made fit to certify a pass. Builds on the round-18 panel (panel_r18.py is that
panel's file, unchanged; results/ starts as a copy of its numbers). From the project root, PYTHONIOENCODING=utf-8:

    python out/r19/panel2/panel2.py run <rule> [<rule> ...]   EVERYTHING for a new rule (old tests, new tests, new sets)
    python out/r19/panel2/panel2.py table [<rule> ...]        old verdict and new verdict side by side (table.txt)

The steps `run` is made of (each can be run alone, each keeps its numbers):
    ... orbits [<rule> ...]        does the orbit of 0 stay bounded at each off-plane c?  (seconds)
    ... extra <rule> [...]         'the solid stays' + airplane spikes + cauliflower dimples from cuts across the axis
    ... runc <rule> [<set> ...]    the new off-plane sets (bas_yz, bas_zy, sm_yz, rab_up), only where the orbit of 0 stays
    python out/r19/panel2/wide.py <rule>:<set> ...            the 120 close-cut tiles (kept, not scored)
    ... score                      the new hair number on every kept tile set (wide/scores.json)
README.md says what each line measures and how it was calibrated.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage, signal
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import panel_r18 as P
import hairnum as H
import wide as Wd
B = P.B; R = P.R
OLD_TILES = os.path.join(ROOT, 'out', 'r18', 'panel', 'tiles')

# the off-plane sets that replace round 18's group C (rabbit turned 90 and 30 degrees)
NEWC = [
    dict(tag='bas_yz', name='Basilica nudged off both planes, c = (-1, 0.05, 0.03)', group='B', c=(-1.0, 0.05, 0.03), L=1.7, steps=40, base='basilica'),
    dict(tag='bas_zy', name='Basilica nudged off both planes, c = (-1, 0.03, 0.05)', group='B', c=(-1.0, 0.03, 0.05), L=1.7, steps=40, base='basilica'),
    dict(tag='sm_yz', name='San Marco nudged off both planes, c = (-0.75, 0.01, 0.02)', group='B', c=(-0.75, 0.01, 0.02), L=1.6, steps=40, base='sanmarco'),
    dict(tag='rab_up', name='Rabbit lifted out of the flat plane, c = (-0.1226, 0.7449, 0.015)', group='B', c=(-0.122561, 0.744862, 0.015), L=1.4, steps=40, base='rabbit'),
]
CTAGS = [s['tag'] for s in NEWC]
OLDSETS = {s['tag']: s for s in P.PANEL}
TAGS2 = ['basilica', 'sanmarco', 'airplane', 'cauliflower', 'rabbit', 'dendrite', 'siegel'] + CTAGS
ORDER2 = ['cut', 'piece', 'stays', 'bodies', 'd3', 'clean', 'mirror']
TITLE2 = dict(P.TITLE, stays='the solid stays')
T_STAY = 0.90         # volume at 80 steps over volume at 40 steps
ORBIT_STEPS = 3000
T_NUDGE_THICK = 0.8   # off-plane sets: thickest place against the same rule's own solid at the un-nudged c
T_NUDGE_VOL = (0.5, 1.5)


def log(*a):
    print(*a, flush=True)


def jload(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


# ------------------------------------------------------------------ one orbit: does 0 stay bounded?
def orbit0(F, c, n=ORBIT_STEPS):
    """The step at which the orbit of 0 under v -> F(v) + c leaves the escape radius, or None if it has not by step n."""
    x = np.zeros(1); y = np.zeros(1); z = np.zeros(1); R2 = (B.resc(c) + 1e-9) ** 2
    for k in range(n):
        x, y, z = F(x, y, z); x = x + c[0]; y = y + c[1]; z = z + c[2]
        if not np.isfinite(x[0] + y[0] + z[0]) or x[0] ** 2 + y[0] ** 2 + z[0] ** 2 > R2:
            return k + 1
    return None


def orbits(rules):
    p = os.path.join(HERE, 'results', 'orbits.json'); out = jload(p, {})
    for rule in rules:
        F = R.get(rule); out[rule] = {}
        for S in NEWC + [OLDSETS['rabbit90'], OLDSETS['rabbit30']]:
            out[rule][S['tag']] = orbit0(F, S['c'])
        log('%-10s orbit of 0 leaves at step: %s' % (rule, '  '.join('%s %s' % (t, 'never (%d)' % ORBIT_STEPS if v is None else v) for t, v in out[rule].items())))
        json.dump(out, open(p, 'w'), indent=1)
    return out


# ------------------------------------------------------------------ the solid stays
def stay_numbers(F, c, L, N=129, steps=(20, 40, 60, 80)):
    a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    ins, death = B.inside(F, X, Y, Z, c=c, steps=max(steps)); h = 2 * L / (N - 1)
    return {str(n): float((ins | (death > n)).sum() * h ** 3) for n in steps}


def flat_stay(c, L, steps=(20, 40, 60, 80), n=801):
    a = np.linspace(-L, L, n); A, Bb = np.meshgrid(a, a, indexing='ij'); z = A + 1j * Bb; cc = complex(c[0], c[1])
    R2 = (B.resc(c) + 1e-9) ** 2; ins = (z.real ** 2 + z.imag ** 2) <= R2; out = {}
    for k in range(1, max(steps) + 1):
        z = np.where(ins, z * z + cc, 0); ins &= (z.real ** 2 + z.imag ** 2) <= R2
        if k in steps:
            out[str(k)] = float(ins.sum() * (2 * L / (n - 1)) ** 2)
    return out


# ------------------------------------------------------------------ cuts across the x-axis, point by point
def across(F, c, x0, rmax, nphi=1440, nr=1200, steps=80):
    phi = np.arange(nphi) * 2 * np.pi / nphi; r = (np.arange(nr) + 0.5) * rmax / nr
    Rr, Ph = np.meshgrid(r, phi)
    ins, _ = B.inside(F, np.full_like(Rr, x0), Rr * np.cos(Ph), Rr * np.sin(Ph), c=c, steps=steps)
    return ins, r, phi


def _off_plane(deg, tol=12.0):
    d = min(abs(((deg - a + 180) % 360) - 180) for a in (0.0, 180.0)); return d > tol


def spikes(ins, r):
    """Airplane, middle body cut across at x = 0: directions in which matter stands clear of the body (spines of beads).
    Returns the directions (degrees from +y), their widths, how many are off the flat plane, and whether a ring or sheet."""
    nphi, nr = ins.shape
    first = np.where(ins.all(axis=1), nr - 1, np.argmax(~ins, axis=1)); Rb = r[first]; Rmed = float(np.median(Rb))
    beyond = ins & (r[None, :] > 1.25 * Rmed)
    m = beyond.sum(axis=1); hit = m > 0
    fat = hit | np.roll(hit, 1) | np.roll(hit, -1) | np.roll(hit, 2) | np.roll(hit, -2)
    if fat.all() or Rmed >= 0.98 * r[-1]:                 # matter in every direction: a ring, a sheet or a full disc
        return dict(body_radius=Rmed, directions=[], widths=[], n=0, off_plane=0, wide=0, covered_deg=360.0, ring=True)
    s = int(np.argmin(fat)); f = np.roll(fat, -s); mm = np.roll(m, -s); lab, k = ndimage.label(f)
    dirs = []; wid = []
    for i in range(1, k + 1):
        idx = np.flatnonzero(lab == i)
        if mm[idx].sum() < 3:
            continue
        dirs.append(float(((idx.mean() + s) % nphi) * 360.0 / nphi)); wid.append(float(idx.size * 360.0 / nphi))
    cov = float(sum(wid))
    thin = [d for d, w in zip(dirs, wid) if w <= 20.0]
    return dict(body_radius=Rmed, directions=[round(d, 1) for d in dirs], widths=[round(w, 1) for w in wid], n=len(thin),
                off_plane=int(sum(_off_plane(d) for d in thin)), wide=int(sum(w > 20.0 for w in wid)), covered_deg=cov, ring=bool(cov > 300.0))


def dimples(ins, r, depth=0.01):
    """Cauliflower cut across at x = 0: the outline's DENTS, i.e. the places where it lies inside its own rubber band
    (convex hull) by at least `depth` of the radius. An oval has none; a flower has one per cusp.
    Returns their directions (degrees from +y), depths, and how many are off the flat plane."""
    from scipy.spatial import ConvexHull
    nphi, nr = ins.shape; phi = np.arange(nphi) * 2 * np.pi / nphi
    first = np.where(ins.all(axis=1), nr - 1, np.argmax(~ins, axis=1)); Rb = ndimage.median_filter(r[first], size=3, mode='wrap'); Rmed = float(np.median(Rb))
    pts = np.c_[Rb * np.cos(phi), Rb * np.sin(phi)]; hv = np.sort(ConvexHull(pts).vertices)
    Rh = Rb.copy()
    for a_, b_ in zip(hv, np.roll(hv, -1)):
        A = pts[a_]; Bp = pts[b_]; idx = np.arange(a_, b_ if b_ > a_ else b_ + nphi) % nphi
        den = np.cos(phi[idx]) * (Bp[1] - A[1]) - np.sin(phi[idx]) * (Bp[0] - A[0])
        Rh[idx] = (A[0] * Bp[1] - Bp[0] * A[1]) / np.where(np.abs(den) < 1e-12, 1e-12, den)
    gap = (Rh - Rb) / Rmed; deep = gap >= depth
    dirs = []; deps = []
    if deep.any() and not deep.all():
        s0 = int(np.argmin(deep)); f = np.roll(deep, -s0); g = np.roll(gap, -s0); lab, k = ndimage.label(f)
        for i in range(1, k + 1):
            idx = np.flatnonzero(lab == i); j = idx[int(np.argmax(g[idx]))]
            dirs.append(float(((j + s0) % nphi) * 360.0 / nphi)); deps.append(float(g[j]))
    return dict(radius=Rmed, spread=float((Rb.max() - Rb.min()) / Rmed), directions=[round(d, 1) for d in dirs], depths=[round(d, 3) for d in deps],
                n=len(dirs), off_plane=int(sum(_off_plane(d) for d in dirs)), outline=[round(float(x), 4) for x in Rb[::4]])


def across_img(ins, r, marks_deg, n=360):
    a = np.linspace(-r[-1], r[-1], n); Y, Z = np.meshgrid(a, -a); rr = np.hypot(Y, Z); ph = np.mod(np.arctan2(Z, Y), 2 * np.pi)
    i = np.clip((ph / (2 * np.pi) * ins.shape[0]).round().astype(int) % ins.shape[0], 0, ins.shape[0] - 1); j = np.clip((rr / r[-1] * ins.shape[1]).astype(int), 0, ins.shape[1] - 1)
    img = np.zeros((n, n, 3), np.uint8); img[...] = (34, 52, 110); img[ins[i, j] & (rr <= r[-1])] = (238, 228, 200)
    im = Image.fromarray(img); dr = ImageDraw.Draw(im)
    for d in marks_deg:
        t = np.radians(d); x1 = n / 2 + 0.47 * n * np.cos(t); y1 = n / 2 - 0.47 * n * np.sin(t); x0 = n / 2 + 0.42 * n * np.cos(t); y0 = n / 2 - 0.42 * n * np.sin(t)
        dr.line((x0, y0, x1, y1), fill=(235, 60, 50) if _off_plane(d) else (120, 200, 120), width=2)
    return im


def extra(rule):
    """'The solid stays' on every old set but the dendrite; airplane spikes; cauliflower dimples."""
    F = R.get(rule); p = os.path.join(HERE, 'results', 'extra-' + rule + '.json'); out = jload(p, {})
    os.makedirs(os.path.join(HERE, 'tiles', rule), exist_ok=True)
    for S in P.PANEL:
        tag = S['tag']
        if S['group'] == 'C' or S.get('tree') or tag in out:
            continue
        t0 = time.time(); out[tag] = dict(stay=stay_numbers(F, S['c'], S['L']))
        if tag == 'airplane':
            ins, r, phi = across(F, S['c'], 0.0, 0.16); out[tag]['spikes'] = sp = spikes(ins, r)
            across_img(ins, r, sp['directions']).save(os.path.join(HERE, 'tiles', rule, 'across_airplane.png'))
        if tag == 'cauliflower':
            ins, r, phi = across(F, S['c'], 0.0, 1.15, steps=S['steps']); out[tag]['dimples'] = dm = dimples(ins, r)
            across_img(ins, r, dm['directions']).save(os.path.join(HERE, 'tiles', rule, 'across_cauliflower.png'))
        log('[%s %s] extra %s (%.0f s)' % (rule, tag, {k: (v if k != 'dimples' else {q: w for q, w in v.items() if q != 'outline'}) for k, v in out[tag].items()}, time.time() - t0))
        json.dump(out, open(p, 'w'), indent=1)
    return out


# ------------------------------------------------------------------ the new off-plane sets
def runc(rule, tags=None):
    F = R.get(rule); p = os.path.join(HERE, 'results', rule + '.json')
    out = jload(p) or dict(rule=rule, label=R.RULES[rule][1], sets={})
    for S in NEWC:
        if tags and S['tag'] not in tags:
            continue
        t0 = time.time(); esc = orbit0(F, S['c']); st = stay_numbers(F, S['c'], S['L'])
        if esc is not None:
            res = dict(rule=rule, tag=S['tag'], name=S['name'], group='C2', c=list(S['c']), steps=S['steps'], outside=True)
        else:
            res = P.run_set(rule, F, S); res['group'] = 'C2'; res['outside'] = False
        res.update(orbit0_leaves_at=esc, stay=st, base=S['base'])
        out['sets'][S['tag']] = res
        log('[%s %s] orbit of 0 leaves at %s; volume at 20/40/60/80 steps %s (%.0f s)' % (rule, S['tag'], esc, st, time.time() - t0))
        json.dump(out, open(p, 'w'), indent=1)


def fitd3(rule, tags=None):
    """'Truly 3D' for the off-plane sets. The old test measures how far each bud stands from the flat plane z = 0; when
    c is lifted out of that plane the whole solid tilts and shifts, and a flat row of buds would count as 'off the
    plane'. Here the plane is the one that best fits the buds themselves (any plane, weighted by bud size); buds count
    as off it only if they do not all lie near one plane."""
    F = R.get(rule); p = os.path.join(HERE, 'results', rule + '.json'); out = jload(p)
    for S in NEWC:
        r = out['sets'].get(S['tag'])
        if (tags and S['tag'] not in tags) or r is None or r.get('outside') or r.get('volume', 0) <= 0:
            continue
        t0 = time.time(); N = P.NMAIN; L = S['L']; h = 2 * L / (N - 1); R2 = r['flat']['thickest']
        vol = B.volume(F, N, L=L, c=S['c'], steps=S['steps'])
        rad = 0.2 * R2; rv = rad / h; org = [-L] * 3
        op, rs = B.wear(vol, rv); _lab, ps = B.pieces(rs, h, org)
        ps = [q for q in ps if q['voxels'] >= B.vmin(rv) and max(abs(x) for x in q['centre']) < L - rad]
        rings = [q for q in ps if q['extent'] >= 300 and q['rho'] > 0.3 * R2]
        buds = [q for q in ps if not (q['extent'] >= 300 and q['rho'] > 0.3 * R2)]
        d = dict(pieces=len(ps), rings=len(rings), off_plane=0, round_off_plane=0, roundness_off=None, tilt_deg=None)
        if len(buds) >= 3 and op.any():
            C = np.array([q['centre'] for q in buds]); w = np.array([q['voxels'] for q in buds], float)
            C = C - (C * w[:, None]).sum(0) / w.sum()          # the plane is free: it goes through the buds' own middle
            ev, evec = np.linalg.eigh((C * w[:, None]).T @ C / w.sum()); n = evec[:, 0]
            off = [q for q, cc in zip(buds, C) if abs(float(cc @ n)) > max(0.5 * q['r_eq'], 3 * h)]
            d.update(off_plane=len(off), round_off_plane=int(sum(q['round'] >= 0.45 for q in off)), roundness_off=B.roundness(off),
                     tilt_deg=float(np.degrees(np.arccos(min(1.0, abs(float(n[2])))))), normal=[float(x) for x in n], spread=[float(x) for x in np.sqrt(np.maximum(ev, 0))])
        r['d3fit'] = d
        log('[%s %s] buds against their own best plane: %s (%.0f s)' % (rule, S['tag'], d, time.time() - t0))
        full = jload(p); full['sets'][S['tag']]['d3fit'] = d; json.dump(full, open(p, 'w'), indent=1); out = full


# ------------------------------------------------------------------ the new hair number, from kept tiles
def score_all():
    p = os.path.join(HERE, 'wide', 'scores.json'); out = jload(p, {})
    if out.get('_measure') != H_VERSION():
        out = {'_measure': H_VERSION()}
    for f in sorted(os.listdir(os.path.join(HERE, 'wide'))):
        if f.endswith('.npz') and f[:-4] not in out:
            rule, tag = f[:-4].rsplit('-', 1) if not any(f[:-4].endswith('-' + t) for t in CTAGS) else next((f[:-4][:-len(t) - 1], t) for t in CTAGS if f[:-4].endswith('-' + t))
            rows = H.score_set(rule, tag); out[f[:-4]] = dict(rows=rows, summary=H.summary(rows))
            sm = out[f[:-4]]['summary']
            log('%-22s thin %.3f film %.2f old %.2f | over %d of %d | half-planes failing %d of %d' % (f[:-4], sm['fins_worst'], sm['film_worst'], sm['old_worst'], sm['over'], sm['tiles'], sm['half_planes_failing'], sm['half_planes']))
            json.dump(out, open(p, 'w'))
    return out


def H_VERSION():
    return 'thin %.2f reach %.1f minlen %.1f film far %.1f small %d' % (H.THIN, H.REACH, H.MINLEN, H.FAR, H.SMALL)


_SC = None


def scores():
    global _SC
    if _SC is None:
        _SC = jload(os.path.join(HERE, 'wide', 'scores.json'), {})
    return _SC


_OLD12 = {}


def old12(rule, tag):
    """The new number on the old panel's own 12 tiles (read back from its pictures: inside is one exact colour)."""
    if (rule, tag) in _OLD12:
        return _OLD12[(rule, tag)]
    rows = []
    for base in (os.path.join(HERE, 'tiles'), OLD_TILES):
        d = os.path.join(base, rule, tag)
        if not os.path.isdir(d):
            continue
        for ang in ('22_5', '11_25'):
            for pi in (0, 1):
                for q in (0, 1, 2):
                    f = os.path.join(d, 'close_%s_%d_%d.png' % (ang, pi, q))
                    if os.path.exists(f):
                        a = np.asarray(Image.open(f).convert('RGB')); m = (a[..., 0] == 238) & (a[..., 1] == 228) & (a[..., 2] == 200)
                        s = H.score(m); s.update(angle=float(ang.replace('_', '.')), off=P.OFFS[pi], q=q); rows.append(s)
        if rows:
            break
    _OLD12[(rule, tag)] = rows
    return rows


def clean_line(rule, tag, r):
    """(ok, text) for 'clean close up' by the new number."""
    key = '%s-%s' % (rule, tag); sc = scores().get(key); src = '120 tiles'
    if sc is None and rule == 'lathe' and OLDSETS.get(tag, {}).get('group') == 'A':
        sc = scores().get('flat-%s' % tag); src = 'the flat set itself (every cut through the axis of a spun solid is the flat set)'
    if sc is not None and sc['summary']:
        sm = sc['summary']; rows = [x for x in sc['rows'] if x['fins'] is not None]
        ok = sm['over'] == 0
        sub = [x for x in rows if x['angle'] in (22.5, 11.25) and x['off'] in (-0.5, 0.35)]
        subbad = sum(1 for x in sub if x['fins'] > H.T_FINS or x['film_pct'] > H.T_FILM)
        pairs = sorted(set((x['angle'], x['off']) for x in rows)); pbad = sum(1 for a, o in pairs if any(x['angle'] == a and x['off'] == o and (x['fins'] > H.T_FINS or x['film_pct'] > H.T_FILM) for x in rows))
        txt = '%s (%d half-planes x %d skin points x 3 widths): thin things (fins, needles, slivers) add up to at most %.2f of the skin line (line %.2f), loose dust or combs cover at most %.1f %% of a tile (line %.1f); %d tiles over a line; half-planes with a failing tile %d of %d, skin points %d of %d; of the %d (half-plane, skin point) pairs %d fail' % (
            src, sm['half_planes'], sm['skin_points'], sm['fins_worst'], H.T_FINS, sm['film_worst'], H.T_FILM, sm['over'], sm['half_planes_failing'], sm['half_planes'], sm['skin_points_failing'], sm['skin_points'], len(pairs), pbad)
        if sub:
            txt += '; the old panel\'s 12 tiles alone would say %s' % ('clean' if subbad == 0 else 'not clean (%d of %d)' % (subbad, len(sub)))
        txt += '; by angle (worst thin / film per cent): ' + ' '.join('%s:%.2f/%.1f' % (a, v[0], v[1]) for a, v in sm['by_angle'].items())
    else:
        rows = old12(rule, tag)
        if not rows:
            return None, 'no close-cut tiles for this set'
        bad = sum(1 for x in rows if x['fins'] is not None and (x['fins'] > H.T_FINS or x['film_pct'] > H.T_FILM))
        fw = max((x['fins'] or 0) for x in rows); lw = max(x['film_pct'] for x in rows)
        ok = False if bad else None                # a pass on 12 tiles is not a pass: it is left open
        txt = 'ONLY the old panel\'s %d tiles (2 half-planes, 2 skin points; the 120-tile cut was not made for this set): thin things at most %.2f of the skin line (line %.2f), dust or combs at most %.1f %% of a tile (line %.1f); %d tiles over a line%s' % (
            len(rows), fw, H.T_FINS, lw, H.T_FILM, bad, '' if bad else ' - nothing found, but 12 tiles are NOT a certificate: this line is left OPEN until the 120-tile cut is made')
    rb = P.load_ribs(rule).get(tag)
    if tag == 'basilica' and rb is not None and rb.get('rays_that_never_left', 0) <= 72:
        ok = ok and rb['ripple_pct'] <= P.T_RIBS; txt += '; ribs on the middle body cut across %.2f %% of its radius (over %.2f = ribbed)' % (rb['ripple_pct'], P.T_RIBS)
    return ok, txt


# ------------------------------------------------------------------ verdicts
def verdicts2(rule, tag, full, ex):
    """full = results/<rule>.json, ex = results/extra-<rule>.json. Returns {line: (ok or None, text)} over ORDER2."""
    r = full['sets'].get(tag)
    if r is None:
        return None
    c2 = tag in CTAGS
    if c2 and r.get('outside'):
        st = r['stay']
        txt = 'the orbit of 0 leaves at step %d: this c lies OUTSIDE the rule\'s own bounded region, so its Julia set should be dust and is not judged (volume at 20, 40, 80 steps: %.3f, %.3f, %.3f)' % (r['orbit0_leaves_at'], st['20'], st['40'], st['80'])
        v = {k: (None, 'not judged') for k in ORDER2}; v['cut'] = (None, txt); return v
    if r['volume'] <= 0 or r['piece']['pieces'] == 0:
        v = {k: (None, 'nothing to measure') for k in ORDER2}
        v['piece'] = (False, 'the solid is EMPTY at 40 steps although the orbit of 0 stays bounded' if c2 else 'the solid is EMPTY'); return v
    v = dict(P.verdicts(r))
    # the solid stays
    st = r.get('stay') if c2 else (ex.get(tag) or {}).get('stay')
    if 'tree' in r:
        v['stays'] = (None, 'not asked of a tree: the flat tree has no inside and thins with every step (the tree test stands in)')
    elif st is None:
        v['stays'] = (None, 'not measured yet')
    else:
        q = st['80'] / max(st['40'], 1e-12)
        v['stays'] = (q >= T_STAY, 'volume at 80 steps is %.0f %% of the volume at 40 (needs %.0f); at 20, 40, 60, 80 steps: %.3f, %.3f, %.3f, %.3f (129 points a side)' % (100 * q, 100 * T_STAY, st['20'], st['40'], st['60'], st['80']))
    # bodies: lines that could not fail are no longer called a pass
    if tag == 'sanmarco' or tag == 'siegel':
        ok, txt = v['bodies']
        why = ('at 40 steps even the yardstick is fused at the meeting point, so "meeting at a point" cannot be seen here' if tag == 'sanmarco'
               else 'one fat body with no meeting point: this line cannot tell a smooth body from a layered or terraced lump (that is left to "truly 3D" and "clean close up")')
        ratio = r['thickest'] / max(r['flat']['thickest'], 1e-9); yv = (P.YARD().get(tag) or {}).get('volume'); vr = r['volume'] / yv if yv else None
        gross = ratio < P.T_THIN or ratio > P.T_LUMP or (vr is not None and vr > P.T_VOL)
        v['bodies'] = (False if gross else None, ('FAILS the gross check: ' if gross else 'NOT JUDGED (%s); only the gross check is made and it finds nothing: ' % why) +
                       'thickest place %.2f x the flat set\'s (0.8 to 1.15), volume %s x the yardstick\'s (up to 2)' % (ratio, '?' if vr is None else '%.2f' % vr))
    if c2:
        v['cut'] = (None, 'c is out of the flat plane: there is no flat set to compare the cut with. The orbit of 0 stays bounded for %d steps, so a solid is expected here' % ORBIT_STEPS)
        v['mirror'] = (None, 'no mirror to demand for a c off both planes')
        b = full['sets'].get(r['base'])
        if b:
            rt = r['thickest'] / max(b['thickest'], 1e-9); rv = r['volume'] / max(b['volume'], 1e-9)
            vb = verdicts2(rule, r['base'], full, ex)['bodies']
            ok = rt >= T_NUDGE_THICK and T_NUDGE_VOL[0] <= rv <= T_NUDGE_VOL[1]
            txt = "against this rule's own solid at the un-nudged c (%s): thickest place x %.2f (needs %.1f or more), volume x %.2f (needs %.1f to %.1f): a small step off the axis should leave the bodies nearly as they were" % (
                r['base'], rt, T_NUDGE_THICK, rv, T_NUDGE_VOL[0], T_NUDGE_VOL[1])
            if vb[0] is False:
                ok = False; txt += '; and the un-nudged set itself FAILS this line, so the nudged one does too'
            elif vb[0] is None and ok:
                ok = None; txt = 'NOT JUDGED beyond the gross check (as for the un-nudged set): ' + txt
            v['bodies'] = (ok, txt)
    if c2:
        d = r['d3']; f = r.get('d3fit')
        if f is None:
            v['d3'] = (None, 'not judged yet: for a c off the flat plane the buds must be measured against their own best plane (run "fitd3"); against the flat plane the old count would be %d round pieces' % d['round_off_plane'])
        else:
            ro = f['roundness_off']
            ok = d['turn_pct'] >= P.T_TURN and f['rings'] == 0 and f['round_off_plane'] >= P.T_OFF and ro is not None and ro >= P.T_ROUND
            v['d3'] = (ok, 'a turn about the x-axis changes %.1f %% of it; %d pieces come off: %d rings; measured against the plane that best fits the buds themselves (tilted %s degrees from the flat plane), %d stand off it, %d of those round (2 needed); roundness of those %s (needs %.2f). Against the flat plane z = 0 the old count was %d: for a lifted c that count is wrong, a flat row of buds tilts out of z = 0' % (
                d['turn_pct'], f['pieces'], f['rings'], '?' if f['tilt_deg'] is None else '%.0f' % f['tilt_deg'], f['off_plane'], f['round_off_plane'], 'none' if ro is None else '%.2f' % ro, P.T_ROUND, d['round_off_plane']))
    # truly 3D on airplane and cauliflower: counted from point-by-point cuts across the axis
    d = r['d3']; e = ex.get(tag) or {}
    if tag == 'airplane' and 'spikes' in e:
        s = e['spikes']
        v['d3'] = ((not s['ring']) and s['off_plane'] >= 2 and d['rings'] == 0, 'middle body cut across at x = 0, point by point, 1,440 directions: spines of beads stand out in %d directions, %d of them off the flat plane (2 needed)%s; %.0f degrees of the round are covered (over 300 = a ring or sheet); voxel rings %d' % (
            s['n'], s['off_plane'], '' if not s.get('wide') else '; %d wide fans (over 20 degrees) not counted as spines' % s['wide'], s['covered_deg'], d['rings']))
    if tag == 'cauliflower' and 'dimples' in e:
        s = e['dimples']; q = r.get('pits') or {}
        v['d3'] = (s['off_plane'] >= 2 and q.get('rings', 0) == 0 and d['turn_pct'] >= P.T_TURN, 'cut across at x = 0, point by point, 1,440 directions: the outline has %d dents (places at least 1 %% of the radius inside its own rubber band), %d of them off the flat plane (2 needed); grooves running round the axis (voxels): %d; a turn about the x-axis changes %.1f %%' % (
            s['n'], s['off_plane'], q.get('rings', 0), d['turn_pct']))
    if 'tree' in r:
        v['clean'] = (None, 'not measured: a tree has no skin (the tree test stands in)')
    else:
        v['clean'] = clean_line(rule, tag, r)
    return {k: v.get(k, (None, '')) for k in ORDER2}


def cell(v, order):
    if v is None:
        return '-'
    if all(v[k][0] is None for k in order) and 'OUTSIDE' in v['cut'][1]:
        return 'outside'
    ff = [k for k in order if v[k][0] is False]
    if not ff and 'clean' in v and v['clean'][0] is None and 'ONLY the old panel' in v['clean'][1]:
        return 'open(12tiles)'
    return 'pass' if not ff else 'F:' + ','.join(k[:3] for k in ff)


def table(names=None):
    names = names or [n for n in P.saved_rules()]
    L = []
    L.append('OLD (round 18 panel, as it judged)'); L.append('%-10s ' % 'rule' + ' '.join('%-12s' % t for t in P.TAGS))
    for n in names:
        full = P.load(n)
        L.append('%-10s ' % n + ' '.join('%-12s' % (cell(P.verdicts(full['sets'][t]), P.ORDER) if t in full['sets'] else '-')[:12] for t in P.TAGS))
    L.append(''); L.append('NEW (panel2). sta = the solid stays; "outside" = the orbit of 0 leaves, c is outside the rule\'s bounded region, not judged; "open(12tiles)" = no line fails, but the skin was looked at in 12 tiles only, so it is not a pass; "-" = not run')
    L.append('%-10s ' % 'rule' + ' '.join('%-13s' % t for t in TAGS2))
    for n in names:
        full = P.load(n); ex = jload(os.path.join(HERE, 'results', 'extra-' + n + '.json'), {})
        L.append('%-10s ' % n + ' '.join('%-13s' % cell(verdicts2(n, t, full, ex), ORDER2)[:13] for t in TAGS2))
    L.append('')
    for n in names:
        full = P.load(n); ex = jload(os.path.join(HERE, 'results', 'extra-' + n + '.json'), {})
        L.append('=== %s  (%s)' % (n, full['label']))
        for t in TAGS2:
            v = verdicts2(n, t, full, ex)
            if v is None:
                continue
            ff = [k for k in ORDER2 if v[k][0] is False]
            old = cell(P.verdicts(full['sets'][t]), P.ORDER) if t in P.TAGS else 'new set'
            L.append('  %-11s NEW: %s   (old panel: %s)' % (t, cell(v, ORDER2) if not ff else 'FAILS first on: ' + TITLE2[ff[0]], old))
            for k in ORDER2:
                ok, txt = v[k]
                L.append('      %-22s %-4s %s' % (TITLE2[k], 'n/a' if ok is None else ('pass' if ok else 'FAIL'), txt))
    return '\n'.join(L)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'table'; args = sys.argv[2:]
    if cmd == 'orbits':
        orbits(args or P.saved_rules())
    elif cmd == 'extra':
        for nm in args:
            extra(nm)
    elif cmd == 'runc':
        tags = [a for a in args if a in CTAGS]
        for nm in [a for a in args if a not in CTAGS]:
            runc(nm, tags or None)
    elif cmd == 'fitd3':
        tags = [a for a in args if a in CTAGS]
        for nm in [a for a in args if a not in CTAGS]:
            fitd3(nm, tags or None)
    elif cmd == 'score':
        score_all()
    elif cmd == 'moves':
        # how the 'clean close up' verdict moves with where the skin is looked at
        sc = scores(); L = ['%-22s %5s %7s %7s %6s %11s %11s %9s %10s  %s' % ('rule-set', 'tiles', 'thin', 'film %', 'over', 'half-planes', 'skin points', 'pairs', 'old 12', 'pass chance if ONE (half-plane, skin point) pair were looked at')]
        for key in sorted(k for k in sc if not k.startswith('_')):
            sm = sc[key]['summary']
            if not sm:
                continue
            rows = [x for x in sc[key]['rows'] if x['fins'] is not None]; bad = lambda x: x['fins'] > H.T_FINS or x['film_pct'] > H.T_FILM
            pairs = sorted(set((x['angle'], x['off']) for x in rows)); pb = sum(1 for a, o in pairs if any(x['angle'] == a and x['off'] == o and bad(x) for x in rows))
            sub = [x for x in rows if x['angle'] in (22.5, 11.25) and x['off'] in (-0.5, 0.35)]; sb = sum(1 for x in sub if bad(x))
            L.append('%-22s %5d %7.3f %7.2f %6d %11s %11s %9s %10s  %3.0f %%' % (key, sm['tiles'], sm['fins_worst'], sm['film_worst'], sm['over'], '%d of %d' % (sm['half_planes_failing'], sm['half_planes']),
                     '%d of %d' % (sm['skin_points_failing'], sm['skin_points']), '%d of %d' % (pb, len(pairs)), ('clean' if sb == 0 else 'not clean') if sub else '-', 100.0 * (len(pairs) - pb) / max(len(pairs), 1)))
        t = '\n'.join(L); log(t); open(os.path.join(HERE, 'moves.txt'), 'w', encoding='utf-8').write(t + '\n')
    elif cmd == 'staycal':
        # fail-side and pass-side examples for 'the solid stays' (known rules at round 18's rabbit30 and at the new sets)
        out = {}
        for rule, tag, c, L in (('along', 'rabbit30', OLDSETS['rabbit30']['c'], 1.4), ('p_cot', 'rabbit30', OLDSETS['rabbit30']['c'], 1.4), ('lathe', 'rabbit30', OLDSETS['rabbit30']['c'], 1.4),
                                ('p_ss', 'rabbit30', OLDSETS['rabbit30']['c'], 1.4), ('oneplane', 'bas_zy', (-1.0, 0.03, 0.05), 1.7)):
            st = stay_numbers(R.get(rule), c, L); out['%s@%s' % (rule, tag)] = dict(stay=st, orbit0=orbit0(R.get(rule), c))
            log(rule, tag, 'orbit of 0 leaves at', out['%s@%s' % (rule, tag)]['orbit0'], 'volume 20/40/60/80:', ['%.3f' % st[k] for k in ('20', '40', '60', '80')], '80/40 = %.2f' % (st['80'] / max(st['40'], 1e-12)))
        for tag in ('basilica', 'sanmarco', 'airplane', 'cauliflower', 'rabbit', 'siegel'):
            S = OLDSETS[tag]; st = flat_stay(S['c'], S['L']); out['flat@' + tag] = dict(stay=st)
            log('flat', tag, 'area 20/40/60/80:', ['%.4f' % st[k] for k in ('20', '40', '60', '80')], '80/40 = %.3f' % (st['80'] / st['40']))
        json.dump(out, open(os.path.join(HERE, 'results', 'stay-calib.json'), 'w'), indent=1)
    elif cmd == 'run':
        for nm in args:
            P.run(nm, [t for t in P.TAGS if t not in ('rabbit90', 'rabbit30')]); P.ribs(nm); extra(nm); runc(nm); fitd3(nm)
            full = P.load(nm)
            for t in TAGS2:
                if t != 'dendrite' and t in full['sets'] and not full['sets'][t].get('outside'):
                    Wd.go(nm, t) if not os.path.exists(os.path.join(HERE, 'wide', '%s-%s.npz' % (nm, t))) else None
            score_all(); _SC = None
            log(table([nm]))
    else:
        t = table(args or None); log(t)
        if not args:
            open(os.path.join(HERE, 'table.txt'), 'w', encoding='utf-8').write(t + '\n')
