"""Question 2 (power 2): bodies or lumps, and detail at smaller sizes, for c = -1 and the rabbit.
 - cross-section at the touching point against the centre (c = -1), lines through the touching point
 - whole rabbit solid
 - zoomed cubes (3 sizes) round the point where two bodies meet in the flat set, and round a point of the
   skin off the plane; zoomed upright cuts through the same points
python q2_zoom.py [procs]"""
import os, sys, time, json, numpy as np
from multiprocessing import Pool
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sf

RAB = (-0.12, 0.74, 0.0)
BAS = (-1.0, 0.0, 0.0)
SIZES = (0.3, 0.075, 0.02)
ITERS = {0.3: 60, 0.075: 90, 0.02: 130}
OUT = {}


def inside_pts(P, c, iters=300):
    ins, _ = sf.orbit(P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy(), c[0], c[1], c[2], 2, iters)
    return ins


def skin_point(c, start, direction, far=3.0):
    """First point where the ray from start leaves the set (scan 4000 steps, then bisect)."""
    d = np.array(direction, float); d /= np.linalg.norm(d)
    t = np.linspace(0, far, 4001)
    P = np.array(start, float)[None, :] + t[:, None] * d[None, :]
    ins = inside_pts(P, c)
    assert ins[0], 'start not inside'
    k = int(np.argmin(ins))            # first outside
    lo, hi = t[k - 1], t[k]
    for _ in range(40):
        m = 0.5 * (lo + hi)
        if inside_pts((np.array(start, float) + m * d)[None, :], c)[0]: lo = m
        else: hi = m
    return (np.array(start, float) + lo * d).tolist()


def plane_grid(c, origin, e1, e2, half, N, iters, pool):
    """Cut on the plane origin + a e1 + b e2, |a|, |b| <= half. Returns inside [ia, ib], death."""
    a = np.linspace(-half, half, N)
    A, B = np.meshgrid(a, a, indexing='ij')
    P = np.array(origin, float)[None, :] + A.ravel()[:, None] * np.array(e1, float)[None, :] + B.ravel()[:, None] * np.array(e2, float)[None, :]
    chunks = np.array_split(np.arange(P.shape[0]), 24)
    res = pool.starmap(_pts, [(P[i], c, iters) for i in chunks])
    ins = np.concatenate([r[0] for r in res]).reshape(N, N); dth = np.concatenate([r[1] for r in res]).reshape(N, N)
    return ins, dth


def _pts(P, c, iters):
    return sf.orbit(P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy(), c[0], c[1], c[2], 2, iters)


if __name__ == '__main__':
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    D = os.path.join(HERE, 'data')
    with Pool(procs) as pool:
        # ---------- c = -1: sections
        t0 = time.time()
        touch = (1 - np.sqrt(5)) / 2
        sec = {}
        for nm, x in (('touch', touch), ('centre', 0.0), ('side', -1.0)):
            ins, dth = plane_grid(BAS, (x, 0, -0.95), (0, 1, 0), (0, 0, 1), 2.25, 901, 80, pool)
            np.savez_compressed(os.path.join(D, 'q2-bas-x-%s.npz' % nm), inside=ins, death=dth)
            px = (4.5 / 900) ** 2
            lab, k = ndimage.label(ins)
            sec[nm] = dict(x=float(x), area=float(ins.sum() * px), pieces=int(k))
            print('c = -1, cut at x = %.4f: area %.4f, pieces %d' % (x, sec[nm]['area'], k), flush=True)
        sec['touch_over_centre_percent'] = 100 * sec['touch']['area'] / sec['centre']['area']
        print('cross-section at the touching point / at the centre: %.1f %%' % sec['touch_over_centre_percent'])
        # lines through the touching point
        t = np.linspace(-3.2, 1.6, 480001)
        for nm, d in (('z', (0, 0, 1)), ('y', (0, 1, 0))):
            P = np.array([touch, 0, 0])[None, :] + t[:, None] * np.array(d, float)[None, :]
            res = pool.starmap(_pts, [(P[i], BAS, 200) for i in np.array_split(np.arange(P.shape[0]), 24)])
            ins = np.concatenate([r[0] for r in res])
            lab, k = ndimage.label(ins)
            runs = ndimage.find_objects(lab)
            segs = [(float(t[s[0].start]), float(t[s[0].stop - 1])) for s in runs]
            big = sorted(segs, key=lambda s: s[0] - s[1])[:6]
            sec['line_' + nm] = dict(inside_length=float(ins.sum() * (t[1] - t[0])), stretches=int(k), longest=big,
                                     within_0p02=float(ins[np.abs(t) < 0.02].mean()))
            print('line through the touching point along %s: inside length %.4f in %d stretches; share inside within 0.02 of the point %.3f; longest %s'
                  % (nm, sec['line_' + nm]['inside_length'], k, sec['line_' + nm]['within_0p02'], [(round(a, 3), round(b, 3)) for a, b in big[:4]]), flush=True)
        OUT['sections_c-1'] = sec
        print('sections %.0f s' % (time.time() - t0), flush=True)

        # ---------- whole rabbit
        t0 = time.time()
        axes = sf.cube_axes((0, 0, -0.9), 2.0, 193)
        ins, dth = sf.grid('j', 2, RAB, axes, 30, pool)
        np.savez_compressed(os.path.join(D, 'q2-rabbit-193.npz'), inside=ins, death=dth, cen=np.array((0, 0, -0.9)), L=2.0, n=2)
        zz = axes[2][np.where(ins.any(axis=(0, 1)))[0]]
        print('rabbit solid N=193: volume %.4f, z from %.3f to %.3f, %.0f s' % (ins.sum() * (4.0 / 192) ** 3, zz.min(), zz.max(), time.time() - t0), flush=True)

        # ---------- zoom centres
        a = (1 - np.sqrt(1 - 4 * complex(RAB[0], RAB[1]))) / 2
        pts = {'bas-meet': (BAS, [touch, 0.0, 0.0]),
               'bas-skin': (BAS, skin_point(BAS, (0, 0, 0), (0.25, 0.35, 0.9))),
               'rab-meet': (RAB, [a.real, a.imag, 0.0]),
               'rab-skin': (RAB, skin_point(RAB, (0, 0, 0), (0.25, 0.35, 0.9)))}
        OUT['zoom_centres'] = {k: v[1] for k, v in pts.items()}
        print('zoom centres', OUT['zoom_centres'], flush=True)
        for key, (c, p) in pts.items():
            for h in SIZES:
                t0 = time.time()
                axes = sf.cube_axes(p, h, 129)
                ins, dth = sf.grid('j', 2, c, axes, ITERS[h], pool)
                np.savez_compressed(os.path.join(D, 'q2-zoom-%s-%g.npz' % (key, h)), inside=ins, death=dth, cen=np.array(p), L=h, n=2)
                lab, k = ndimage.label(ins, structure=np.ones((3, 3, 3)))
                OUT['zoom-%s-%g' % (key, h)] = dict(inside_share=float(ins.mean()), pieces=int(k))
                # upright cuts through the centre: plane y = const (x right, z up) and plane x = const (y right, z up)
                for pl, e1 in (('xz', (1, 0, 0)), ('yz', (0, 1, 0))):
                    i2, d2 = plane_grid(c, p, e1, (0, 0, 1), h, 501, ITERS[h] + 30, pool)
                    np.savez_compressed(os.path.join(D, 'q2-cut-%s-%s-%g.npz' % (key, pl, h)), inside=i2, death=d2)
                print('zoom %s half %g: inside share %.3f, pieces %d, %.0f s' % (key, h, ins.mean(), k, time.time() - t0), flush=True)
    json.dump(OUT, open(os.path.join(HERE, 'q2.json'), 'w'), indent=1)
