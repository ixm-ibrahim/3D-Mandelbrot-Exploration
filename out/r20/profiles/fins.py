"""Round 20 profiles: how big are the fins beside the buds? Basilica, point by point, no voxels.

A flat cut is sampled in polar form round a centre (2,880 rays, 1,600 steps along each). The body's own slow outline
is the running median of the first-exit radius over 12 degrees. A THING is a connected piece of the solid lying outside
that slow outline by more than 1.5 % of the mean radius. For each thing: length = how far it reaches beyond the outline,
width = its widest extent across the ray direction, aspect = length / width (a round bud is about 1; panel2 calls
anything over 3.1 thin).

  scale 1 (whole set): the middle body cut across the x-axis at x = -0.45 ... 0.45; rays are directions round the x-axis
  scale 2 (one bud):   the bud in the plane at 60 degrees (the twin of the flat set's top bud), cut across its stalk

python fins.py <rule> ...   -> prints a table and writes fins.json
"""
import os, sys, json
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R
import bench as B

NRAY, NR, STEPS = 2880, 1600, 60


def polar(F, o, u, v, rmax):
    th = np.linspace(0, 2 * np.pi, NRAY, endpoint=False); r = np.linspace(0, rmax, NR + 1)[1:]
    o, u, v = (np.array(t, float) for t in (o, u, v))
    ins = np.zeros((NRAY, NR), bool)
    for s in range(0, NRAY, 480):
        d = np.cos(th[s:s + 480])[:, None] * u[None] + np.sin(th[s:s + 480])[:, None] * v[None]
        P = o[None, None, :] + r[None, :, None] * d[:, None, :]
        ins[s:s + 480], _ = B.inside(F, P[..., 0], P[..., 1], P[..., 2], c=B.C0, steps=STEPS, trap=0.05)
    return th, r, ins


def things(th, r, ins, plane_dirs=None):
    first = np.argmax(~ins, axis=1); r0 = r[np.maximum(first - 1, 0)]
    slow = ndimage.median_filter(r0, size=int(12 / 360 * NRAY) | 1, mode='wrap'); Rm = float(slow.mean())
    out_of = ins & (r[None, :] > slow[:, None] + 0.015 * Rm)
    lab, k = ndimage.label(np.concatenate([out_of, out_of[:1]], 0))            # wrap once round
    lab = lab[:-1]
    res = []
    for sl_i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        m = lab[sl] == sl_i
        if m.sum() < 12:
            continue
        ii, jj = np.nonzero(m); ii = ii + sl[0].start; jj = jj + sl[1].start
        length = float(r[jj.max()] - (slow[ii].mean()))
        # width: for every radius the angular run (in length units), take the largest
        w = 0.0
        for j in np.unique(jj)[::max(1, len(np.unique(jj)) // 40)]:
            w = max(w, float((jj == j).sum() * (2 * np.pi / NRAY) * r[j]))
        az = float(np.degrees(np.arctan2(np.sin(th[ii]).mean(), np.cos(th[ii]).mean())) % 360)
        res.append(dict(az=az, length=length, width=w, aspect=length / max(w, 1e-9), rel=length / Rm))
    return Rm, res


def summary(Rm, res, planes, tol=5.0):
    def near(a):
        return min(abs((a - p + 180) % 360 - 180) for p in planes) <= tol
    big = [t for t in res if t['rel'] >= 0.04]
    on = [t for t in big if near(t['az'])]; off = [t for t in big if not near(t['az'])]
    f = lambda L, key: (float(np.median([t[key] for t in L])) if L else None)
    vis = [t for t in off if t['width'] >= 0.0032]; film = [t for t in off if t['width'] < 0.0032]
    return dict(raw=[(round(t['az'], 2), round(t['length'], 4), round(t['width'], 5)) for t in big], off_visible=len(vis), off_visible_aspect=f(vis, 'aspect'), off_visible_len=f(vis, 'length'), off_films=len(film), mean_radius=Rm, things=len(big), on_planes=len(on), off_planes=len(off), off_thin=sum(t['aspect'] > 3.1 for t in off),
                on_len=f(on, 'length'), on_aspect=f(on, 'aspect'), off_len=f(off, 'length'), off_width=f(off, 'width'), off_aspect=f(off, 'aspect'),
                off_len_max=max([t['length'] for t in off], default=None), on_len_max=max([t['length'] for t in on], default=None))


if __name__ == '__main__':
    p = os.path.join(HERE, 'fins.json'); allr = json.load(open(p)) if os.path.exists(p) else {}
    for nm in sys.argv[1:]:
        F = R.get(nm); k = 5 if nm in ('m_w5', 'w_5b05') else 3
        planes = [m * 180.0 / k for m in range(2 * k)]
        rows = {}
        acc = []
        for x0 in (-0.45, -0.3, -0.15, 0.15, 0.3, 0.45):
            th, r, ins = polar(F, (x0, 0, 0), (0, 1, 0), (0, 0, 1), 0.85)
            Rm, res = things(th, r, ins); acc += res
            rows['x=%g' % x0] = summary(Rm, res, planes)
        rows['middle body, six cuts together'] = summary(0.5, [dict(t, rel=t['length'] / 0.5) for t in acc], planes)
        # scale 2: the bud at 60 degrees (k = 3 only). Its centre: on the plane at 60 degrees, 0.615 from the axis
        if k == 3:
            a = np.radians(60.0); o = (0.0, 0.615 * np.cos(a), 0.615 * np.sin(a))
            th, r, ins = polar(F, o, (1, 0, 0), (0, -np.sin(a), np.cos(a)), 0.2)
            Rm, res = things(th, r, ins)
            # in this cut the bud's own planes are not known; report all things
            big = [t for t in res if t['rel'] >= 0.04]
            rows['bud at 60 degrees'] = dict(mean_radius=Rm, things=len(big), thin=sum(t['aspect'] > 3.1 for t in big),
                                             med_len=float(np.median([t['length'] for t in big])) if big else None,
                                             med_aspect=float(np.median([t['aspect'] for t in big])) if big else None,
                                             aspects=sorted(round(t['aspect'], 1) for t in big), visible=sum(t['width'] >= 0.0003 * 1.07 for t in big), raw=[(round(t['az'], 2), round(t['length'], 4), round(t['width'], 5)) for t in big])
            first = np.argmax(~ins, axis=1); r0 = r[np.maximum(first - 1, 0)]
            # how round is the bud's own outline: its radius across (direction round the x-axis) over its radius along x
            rows['bud at 60 degrees']['radius_round_axis'] = float(np.median(np.r_[r0[NRAY // 4 - 20:NRAY // 4 + 20], r0[3 * NRAY // 4 - 20:3 * NRAY // 4 + 20]]))
            rows['bud at 60 degrees']['radius_along_x'] = float(np.median(np.r_[r0[:20], r0[-20:], r0[NRAY // 2 - 20:NRAY // 2 + 20]]))
        allr[nm] = rows
        mb = rows['middle body, six cuts together']
        print(nm, '| off-plane things at least 0.0032 wide: %s (median aspect %s, length %s); thinner films: %s' % (mb['off_visible'], mb['off_visible_aspect'] and round(mb['off_visible_aspect'], 1), mb['off_visible_len'] and round(mb['off_visible_len'], 3), mb['off_films']))
        print(nm, '| middle body: things %d, on planes %d (median length %s, aspect %s), off planes %d (median length %s, width %s, aspect %s; thin %d)' % (
            mb['things'], mb['on_planes'], mb['on_len'] and round(mb['on_len'], 3), mb['on_aspect'] and round(mb['on_aspect'], 2), mb['off_planes'],
            mb['off_len'] and round(mb['off_len'], 3), mb['off_width'] and round(mb['off_width'], 4), mb['off_aspect'] and round(mb['off_aspect'], 2), mb['off_thin']), flush=True)
        if k == 3:
            b = rows['bud at 60 degrees']
            print('   bud at 60 deg: radius round the axis %.4f, along x %.4f (ratio %.2f); things on it %d, thin %d, median aspect %s, aspects %s' % (
                b['radius_round_axis'], b['radius_along_x'], b['radius_round_axis'] / b['radius_along_x'], b['things'], b['thin'], b['med_aspect'] and round(b['med_aspect'], 2), b['aspects'][:6] + ['...'] + b['aspects'][-3:]), flush=True)
        json.dump(allr, open(p, 'w'), indent=1)
