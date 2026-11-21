"""Round 19, panel2: the new hair number. Works on kept tiles (wide/<rule>-<set>.npz, made by wide.py) and on the
old panel's own PNG tiles, so it can be changed and re-run in seconds.

What is counted, in plain words (per tile, per pixel of skin line of the biggest body):

  fins  = total LENGTH of thin things: any loose piece, and anything a 3-pixel or a 9-pixel wearing-down removes,
          whose length squared is at least THIN (4) times its area (an ellipse 3 times as long as wide, or thinner;
          a needle, a blade, a sliver lying along the skin, a tuft). Round things (buds, buds cut off their stalk,
          a bud with smaller buds on it) are NOT counted, whatever their size.
  film  = per cent of the tile covered by loose dust or combs: small bits (under 12 pixels) and thin things that stand
          more than 4 pixels clear of every body, where they are dense in two directions (fattened by 4.3 pixels they
          must hold a disc of radius 6.3). A string of beads or one needle is a line and does not count.
  specks = hovering specks per pixel of skin line (printed, NOT judged: the flat airplane's strings of beads score 0.22).
  old   = the round-18 number (every inside pixel a 3-pixel wearing-down removes).

    python out/r19/panel2/hairnum.py show <rule>:<set> [...]   numbers + worst-6 montage wide/<rule>-<set>-worst6.png
    python out/r19/panel2/hairnum.py all                        every kept tile set -> wide/scores.json
"""
import os, sys, json
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CW, CH = 420, 294
E8 = np.ones((3, 3), bool)
def _disc(r):
    a = np.arange(-int(r), int(r) + 1); return (a[:, None] ** 2 + a[None, :] ** 2) <= r * r


R3, R9 = 3.3, 9.3   # true discs (a diamond leaves the rim of every round bud behind as four thin crescents)
THIN = 4.0          # length squared over area at and above which a thing is thin (ellipse 3.1 : 1)
SPECK = 6           # pixels: below this a thing has no shape to judge
REACH = 6.0         # pixels: an attached thin thing must stick out of its body at least this far to count
MINLEN = 8.0        # pixels: a thin thing shorter than this is not counted as a fin (it is a speck-sized nick)
T_FINS = 0.10       # length of thin things per pixel of skin line, over which a tile is not clean
T_FILM = 0.5        # per cent of the tile covered by a film of loose dust or a comb of fins, over which a tile is not clean
FAR = 4.0           # pixels: what stands this far clear of every body can be film
SMALL = 12          # pixels: bits under this size (and thin things) can be film; a round bud of 4 pixels across or more cannot


def _open(m, r, pad):
    """Wear down by a disc of radius r and grow back (an opening), by distances: fast. The tile is continued past its
    edge so that a body clipped by the edge is not taken for a thin thing."""
    mp = np.pad(m, pad, mode='edge')
    core = ndimage.distance_transform_edt(mp) > r
    if not core.any():
        return np.zeros_like(m)
    return (ndimage.distance_transform_edt(~core) <= r)[pad:-pad, pad:-pad] & m


def _film(cand):
    """Where the marked pixels are dense in two directions: fatten by 4.3 pixels, then keep what a disc of 6.3 fits in."""
    cp = np.pad(cand, 12)
    fat = ndimage.distance_transform_edt(~cp) <= 4.3
    core = ndimage.distance_transform_edt(fat) > 6.3
    if not core.any():
        return np.zeros_like(cand)
    return (ndimage.distance_transform_edt(~core) <= 6.3)[12:-12, 12:-12]


def _shape(ys, xs):
    """(length, length^2/area) of a pixel set from its second moments (length = full length of the matching ellipse)."""
    n = ys.size
    if n < 2:
        return 1.0, 1.0
    y = ys - ys.mean(); x = xs - xs.mean()
    a = (x * x).mean() + 1 / 12.0; b = (y * y).mean() + 1 / 12.0; c = (x * y).mean()
    l1 = 0.5 * (a + b) + np.sqrt(0.25 * (a - b) ** 2 + c * c)
    ln = 4.0 * np.sqrt(l1)
    return float(ln), float(ln * ln / n)


def score(mask, want_marks=False):
    """mask: bool [rows, cols], True = inside. Returns dict(fins, dust, old, skin, n_fins, n_dust, longest) and, if asked,
    marks: uint8 array 0 nothing, 1 thin thing (fin), 2 hovering speck (dust)."""
    H, W = mask.shape
    lab, k = ndimage.label(mask, structure=E8)
    out = dict(fins=None, dust=None, old=None, skin=0, n_fins=0, n_dust=0, longest=0.0, film_pct=0.0)
    if k == 0:
        return (out, np.zeros(mask.shape, np.uint8)) if want_marks else out
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    mainid = int(np.argmax(sizes)); main = lab == mainid
    op3 = _open(mask, R3, 8); op9 = _open(op3, R9, 24)
    opm = op3 & main
    skin = int((opm & ~ndimage.binary_erosion(opm, border_value=1)).sum())
    if skin < 50:
        skin = W                                   # no body in the tile: a straight skin line would be this long
    out['skin'] = skin
    out['old'] = float((mask & ~op3).sum() / skin)
    edge = np.zeros(mask.shape, bool); edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    marks = np.zeros(mask.shape, np.uint8)
    speck = np.zeros(mask.shape, bool); fin_len = 0.0; nf = 0; longest = 0.0
    done = np.zeros(mask.shape, bool)             # loose pieces already judged whole as thin or as specks

    def judge(L, n, whole, body=None):
        nonlocal fin_len, nf, longest
        if n == 0:
            return
        far = None
        if body is not None and body.any():
            far = ndimage.distance_transform_edt(~body)
        sz = np.bincount(L.ravel(), minlength=n + 1); tiny = sz < SPECK; tiny[0] = False
        if whole:
            tiny[mainid] = False
        tm = tiny[L]; speck[tm] = True                 # specks, all at once
        if whole:
            done[tm] = True
        objs = ndimage.find_objects(L)
        for i in np.flatnonzero(sz >= SPECK):
            if i == 0 or (whole and i == mainid):
                continue
            sl = objs[i - 1]
            sub = L[sl] == i; ys, xs = np.nonzero(sub); a = ys.size
            ln, t = _shape(ys, xs)
            onedge = int((edge[sl] & sub).sum())
            if onedge >= 0.5 * ln:                 # a bigger body clipped by the tile's edge: not judged
                continue
            if t >= THIN and ln >= MINLEN:
                if far is not None and far[sl][sub].max() < REACH:
                    continue                       # lies along the body it belongs to (a neck, the rim of a bud): not a fin
                fin_len += ln; nf += 1; longest = max(longest, ln); marks[sl][sub] = 1
                if whole:
                    done[sl] |= sub

    judge(lab, k, True)                            # loose pieces, whole
    r1 = mask & ~op3 & ~done; L1, n1 = ndimage.label(r1, structure=E8); judge(L1, n1, False, op3)
    r2 = op3 & ~op9 & ~done; L2, n2 = ndimage.label(r2, structure=E8); judge(L2, n2, False, op9)
    # dust: specks that do not sit on anything bigger (a chain of specks reaching something bigger does sit on it)
    big = mask & ~speck
    Ls, ns = ndimage.label(speck, structure=E8)
    nd = 0
    if ns:
        fat = ndimage.binary_dilation(mask, structure=E8)       # bridges gaps of up to 2 pixels
        Lf, nfat = ndimage.label(fat, structure=E8)
        has_big = np.zeros(nfat + 1, bool); has_big[np.unique(Lf[big])] = True; has_big[0] = False
        free = speck & ~has_big[Lf]
        Lq, nd = ndimage.label(free, structure=E8)
        marks[free] = 2
    # film: thin or small stuff standing clear of every body (more than FAR pixels from anything a 3-pixel wearing-down
    # leaves), where it is dense in two directions. A string of beads or a single needle is a line and does not count.
    res = mask & ~op3
    if res.any():
        Lr, nr = ndimage.label(res, structure=E8)
        small = (np.bincount(Lr.ravel()) < SMALL); small[0] = False
        cand = small[Lr] | (marks == 1)                      # small bits and thin things; a round bud is neither
        if op3.any():
            cand &= ndimage.distance_transform_edt(~op3) > FAR
        if cand.sum() >= 8:
            film = _film(cand)
            out['film_pct'] = float(100.0 * film.sum() / film.size)
            if want_marks:
                marks[film & ~mask] = 3
    out.update(fins=float(fin_len / skin), dust=float(nd / skin), n_fins=nf, n_dust=int(nd), longest=float(longest))
    return (out, marks) if want_marks else out


def load_tiles(rule, tag):
    p = os.path.join(HERE, 'wide', '%s-%s.npz' % (rule, tag))
    if not os.path.exists(p):
        return None, None
    z = np.load(p); meta = json.loads(str(z['meta'])); masks = z['masks']
    tiles = {}
    for m in meta:
        if 'k' in m:
            tiles[m['k']] = np.unpackbits(masks[m['k']], axis=1)[:, :CW].astype(bool)
    return meta, tiles


def paint(mask, marks=None):
    img = np.zeros(mask.shape + (3,), np.uint8); img[...] = (34, 52, 110); img[mask] = (238, 228, 200)
    if marks is not None:
        img[marks == 3] = (90, 60, 150); img[marks == 1] = (235, 60, 50); img[marks == 2] = (255, 160, 0)
    return img


def score_set(rule, tag):
    meta, tiles = load_tiles(rule, tag)
    if meta is None:
        return None
    rows = []
    for m in meta:
        if 'k' not in m:
            continue
        s = score(tiles[m['k']]); s.update(angle=m['angle'], off=m['off'], q=m['q'], k=m['k']); rows.append(s)
    return rows


def summary(rows, t_fins=None, t_film=None):
    t_fins = T_FINS if t_fins is None else t_fins; t_film = T_FILM if t_film is None else t_film
    ok = [r for r in rows if r['fins'] is not None]
    if not ok:
        return None
    angs = sorted(set(r['angle'] for r in ok)); offs = sorted(set(r['off'] for r in ok))
    bad = [r for r in ok if r['fins'] > t_fins or r['film_pct'] > t_film]
    return dict(tiles=len(ok), fins_worst=max(r['fins'] for r in ok), dust_worst=max(r['dust'] for r in ok), film_worst=max(r['film_pct'] for r in ok), old_worst=max(r['old'] for r in ok),
                over=len(bad),
                by_angle={str(a): [max(r['fins'] for r in ok if r['angle'] == a), max(r['film_pct'] for r in ok if r['angle'] == a),
                                   sum(1 for r in bad if r['angle'] == a)] for a in angs},
                by_off={str(o): [max(r['fins'] for r in ok if r['off'] == o), max(r['film_pct'] for r in ok if r['off'] == o),
                                 sum(1 for r in bad if r['off'] == o)] for o in offs},
                half_planes_failing=sum(1 for a in angs if any(r['angle'] == a for r in bad)), half_planes=len(angs),
                skin_points_failing=sum(1 for o in offs if any(r['off'] == o for r in bad)), skin_points=len(offs))


def show(rule, tag, n=6, key=None):
    meta, tiles = load_tiles(rule, tag); rows = score_set(rule, tag)
    if not rows:
        print(rule, tag, 'no tiles'); return
    key = key or (lambda r: -max(r['fins'] / T_FINS, r['film_pct'] / T_FILM))
    top = sorted(rows, key=key)[:n]
    Wd = Image.new('RGB', (n * (CW + 4), CH + 18), (12, 14, 20)); dr = ImageDraw.Draw(Wd)
    for j, r in enumerate(top):
        s, marks = score(tiles[r['k']], want_marks=True)
        Wd.paste(Image.fromarray(paint(tiles[r['k']], marks)), (j * (CW + 4), 18))
        dr.text((j * (CW + 4) + 3, 3), 'thin %.2f film %.1f%% old %.2f | %s deg, pt %s, w%d' % (r['fins'], r['film_pct'], r['old'], r['angle'], r['off'], r['q']), fill=(235, 235, 235))
    p = os.path.join(HERE, 'wide', '%s-%s-worst6.png' % (rule, tag)); Wd.save(p)
    sm = summary(rows)
    print('%-9s %-11s tiles %3d | thin worst %.3f | film worst %.2f %% | (specks %.2f) | old worst %.2f | tiles over the line %d | half-planes failing %d of %d' % (
        rule, tag, sm['tiles'], sm['fins_worst'], sm['film_worst'], sm['dust_worst'], sm['old_worst'], sm['over'], sm['half_planes_failing'], sm['half_planes']))
    print('     by angle (thin, film %, tiles over):', ' '.join('%s:%.2f/%.2f/%d' % (a, v[0], v[1], v[2]) for a, v in sm['by_angle'].items()))
    return sm


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'show':
        for arg in sys.argv[2:]:
            rule, tag = arg.split(':'); show(rule, tag)
    elif cmd == 'all':
        out = {}
        for f in sorted(os.listdir(os.path.join(HERE, 'wide'))):
            if f.endswith('.npz'):
                rule, tag = f[:-4].rsplit('-', 1); rows = score_set(rule, tag); out[f[:-4]] = dict(rows=rows, summary=summary(rows))
                sm = out[f[:-4]]['summary']
                print('%-22s thin %.3f film %.2f old %.2f over %d/%d  half-planes failing %d/%d' % (f[:-4], sm['fins_worst'], sm['film_worst'], sm['old_worst'], sm['over'], sm['tiles'], sm['half_planes_failing'], sm['half_planes']))
        json.dump(out, open(os.path.join(HERE, 'wide', 'scores.json'), 'w'))
