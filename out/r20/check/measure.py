"""Round 20 check: numbers behind the pictures. python out/r20/check/measure.py [thick] [strict] [stay]
thick : how thick is each body of a set ROUND the x-axis, against how wide it is in its own plane (point by point)
strict: the rabbit's share in its biggest piece (no gap allowed) at 129, 257, 385, 513 points a side: voxel artefact or not
stay  : volume at 20 ... 320 steps (129 a side) for basilica, rabbit, Siegel disc
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R

RAB = (-0.122561, 0.744862, 0.0)
out = json.load(open(os.path.join(HERE, 'measure.json'))) if os.path.exists(os.path.join(HERE, 'measure.json')) else {}
what = sys.argv[1:] or ['thick', 'strict', 'stay']


def save():
    json.dump(out, open(os.path.join(HERE, 'measure.json'), 'w'), indent=1)


def body_shape(F, c, centre, steps=80):
    """centre = (x, y) of a body's middle in the flat plane. Returns its half-width along x, its half-height along y (both in
    the flat plane), and its half-thickness along the circle round the x-axis (arc length), all from the centre outward
    until the first point that is not inside."""
    x0, y0 = centre; rho = abs(y0); sgn = 1.0 if y0 >= 0 else -1.0
    t = np.linspace(0, 0.8, 16001)
    def first_out(ins):
        o = np.flatnonzero(~ins); return float(t[o[0]]) if o.size else float(t[-1])
    r = {}
    for nm, (dx, dy) in dict(xp=(1, 0), xm=(-1, 0), yp=(0, 1), ym=(0, -1)).items():
        ins, _ = B.inside(F, x0 + dx * t, y0 + dy * t, np.zeros_like(t), c=c, steps=steps); r[nm] = first_out(ins)
    a = t / max(rho, 1e-9)                                   # arc length t along the circle of radius rho
    for nm, s in (('ap', 1.0), ('am', -1.0)):
        ins, _ = B.inside(F, np.full_like(t, x0), sgn * rho * np.cos(s * a), sgn * rho * np.sin(s * a), c=c, steps=steps); r[nm] = first_out(ins)
    ins0, _ = B.inside(F, np.array([x0]), np.array([y0]), np.array([0.0]), c=c, steps=steps)
    return dict(centre_inside=bool(ins0[0]), half_x=0.5 * (r['xp'] + r['xm']), half_y=0.5 * (r['yp'] + r['ym']), half_round=0.5 * (r['ap'] + r['am']),
                round_deg=float(np.degrees(0.5 * (r['ap'] + r['am']) / max(rho, 1e-9))), rho=rho)


if 'thick' in what:
    # bodies: (set, c, name, centre in the flat plane)
    z = complex(*RAB[:2]); z2 = z * z + z
    bas_top = (0.0, 0.62)
    BODIES = [('rabbit', RAB, 'ear round c (0.75 from the axis)', (z.real, z.imag)), ('rabbit', RAB, 'ear round c^2 + c (0.56 from the axis)', (z2.real, z2.imag)),
              ('rabbit', RAB, 'small ear opposite (round -c)', (-z.real, -z.imag)),
              ('basilica', (-1.0, 0, 0), 'bud on top of the middle body (0.62 from the axis)', bas_top),
              ('basilica', (-1.0, 0, 0), 'bud on top of the left body (x = -1, 0.31 from the axis)', (-1.0, 0.31)),
              ('sanmarco', (-0.75, 0, 0), 'bud on top of the middle body', (0.0, 0.72)),
              ('siegel', (-0.390541, -0.586788, 0.0), 'the disc itself, at its resting point', None)]
    for tag, c, name, cen in BODIES:
        if cen is None:
            zz = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2; cen = (zz.real, zz.imag)
        for rule in ('oneplane', 'm_w3', 'along'):
            r = body_shape(R.get(rule), c, cen); out['thick|%s|%s|%s' % (tag, name, rule)] = r
            print('%-9s %-48s %-8s wide %.3f x %.3f in the plane, %.3f thick round the axis (%.1f deg each way) -> thickness / width = %.2f%s' % (
                tag, name, rule, r['half_x'], r['half_y'], r['half_round'], r['round_deg'], r['half_round'] / max(min(r['half_x'], r['half_y']), 1e-9), '' if r['centre_inside'] else '  (centre not inside!)'), flush=True)
    save()

if 'strict' in what:
    for rule in ('m_w3', 'oneplane'):
        for tag, c, L, steps in (('rabbit', RAB, 1.4, 40), ('basilica', (-1.0, 0, 0), 1.7, 40)):
            for N in (129, 257, 385, 513):
                if rule == 'oneplane' and N > 385:
                    continue
                t0 = time.time(); vol = B.volume(R.get(rule), N, L=L, c=c, steps=steps)
                lab, k = ndimage.label(vol); sz = np.bincount(lab.ravel())[1:]
                lab2, k2 = ndimage.label(ndimage.binary_dilation(vol, B.FULL)); big2 = np.bincount(lab2[vol])[1:].max()
                h = 2 * L / (N - 1); loose = np.sort(sz)[::-1][1:]
                r = dict(N=N, pieces=int(k), strict_pct=float(100.0 * sz.max() / vol.sum()), gap_pct=float(100.0 * big2 / vol.sum()), volume=float(vol.sum() * h ** 3),
                         loose_volume=float(loose.sum() * h ** 3), biggest_loose=[float(x * h ** 3) for x in loose[:5]])
                out['strict|%s|%s|%d' % (rule, tag, N)] = r
                print('%-8s %-8s %d a side: %d pieces, biggest holds %.2f %% (no gap) / %.3f %% (one-voxel gap); volume %.4f; loose volume %.4f; biggest loose pieces %s  (%.0f s)' % (
                    rule, tag, N, k, r['strict_pct'], r['gap_pct'], r['volume'], r['loose_volume'], ['%.5f' % x for x in r['biggest_loose'][:3]], time.time() - t0), flush=True)
                save(); del vol, lab, lab2

if 'stay' in what:
    for rule in ('m_w3', 'oneplane'):
        for tag, c, L in (('basilica', (-1.0, 0, 0), 1.7), ('rabbit', RAB, 1.4), ('siegel', (-0.390541, -0.586788, 0.0), 1.45), ('sanmarco', (-0.75, 0, 0), 1.6)):
            N = 129; a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
            ins, death = B.inside(R.get(rule), X, Y, Z, c=c, steps=320); h = 2 * L / (N - 1)
            r = {str(n): float((ins | (death > n)).sum() * h ** 3) for n in (20, 40, 80, 160, 320)}
            out['stay|%s|%s' % (rule, tag)] = r
            print('%-8s %-8s volume at 20, 40, 80, 160, 320 steps: %s ; 80/40 = %.2f, 320/40 = %.2f' % (rule, tag, ' '.join('%.4f' % r[k] for k in ('20', '40', '80', '160', '320')), r['80'] / r['40'], r['320'] / r['40']), flush=True)
            save()
