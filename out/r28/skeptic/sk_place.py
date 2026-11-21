"""Round 28, skeptic of Track B: my own count of the bodies, by a method the explorer did not use.

The explorer looked along lines of sight from the centre of a body and called a bump of the hull a bud. Here the solid
itself is taken apart into bodies:
    1. peel k blocks off the solid (every block nearer than k blocks to the outside goes). Bodies that meet in a point
       or through a thin neck fall apart.
    2. number the pieces that are left, and let every piece grow back inside the solid, all at the same speed, until
       nothing more can be reached. Each block reached belongs to one BODY.
    3. blocks that were not reached hang on to no body by a block's face: they are THIN PIECES (thinner than 2 k
       blocks everywhere, and joined to the rest by a point or not at all). They are numbered too, piece by piece.
    4. for the middle body: every body and thin piece that comes within `reach` blocks of it, with its volume, the gap
       in blocks (0 = they share a block's face), the place where it comes nearest (the touching place), its own
       centre, and how long it is against how thick (from its three main widths).
The same is done for the left and the right neighbour, and for Balls on balls as the yardstick of the method.
Why a gap is allowed: two balls that kiss exactly at a block's centre are one block apart on the grid, and two bodies
that meet in a POINT with pointed ends are a few blocks apart, because the points are thinner than a block.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_place.py <what> <h> [k,k,..] > out/r28/skeptic/place-<what>.log
"""
import os, sys, time
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sk_vox
CROSS = ndi.generate_binary_structure(3, 1); FULL = np.ones((3, 3, 3), bool)


def say(*a):
    print(*a); sys.stdout.flush()


def crop(ins, xs, ys, zs, pad=8):
    sl = []
    for d in range(3):
        m = ins.any(axis=tuple(i for i in range(3) if i != d)); i = np.flatnonzero(m); sl.append(slice(max(i[0] - pad, 0), min(i[-1] + pad + 1, m.size)))
    return ins[sl[0], sl[1], sl[2]], xs[sl[0]], ys[sl[1]], zs[sl[2]]


def grow(seg, ins, rounds=900):
    for it in range(rounds):
        d = seg.copy()
        d[1:] = np.maximum(d[1:], seg[:-1]); d[:-1] = np.maximum(d[:-1], seg[1:])
        d[:, 1:] = np.maximum(d[:, 1:], seg[:, :-1]); d[:, :-1] = np.maximum(d[:, :-1], seg[:, 1:])
        d[:, :, 1:] = np.maximum(d[:, :, 1:], seg[:, :, :-1]); d[:, :, :-1] = np.maximum(d[:, :, :-1], seg[:, :, 1:])
        fill = (seg == 0) & ins & (d > 0)
        if not fill.any():
            return seg, it
        seg[fill] = d[fill]
    return seg, rounds


def segment(ins, k):
    core = ndi.distance_transform_edt(ins) > k
    lab, n = ndi.label(core, structure=CROSS); seg, its = grow(lab.astype(np.int32), ins)
    loose = ins & (seg == 0); lab2, n2 = ndi.label(loose, structure=FULL); seg[loose] = lab2[loose] + n
    return seg, n, n2, its, int(loose.sum())


def body_table(seg, xs, ys, zs, h):
    """volume, centre, the three main widths, the extent of every body (label -> row)."""
    i, j, k = np.nonzero(seg); L = seg[i, j, k]; n = int(L.max()) + 1; P = np.stack([xs[i], ys[j], zs[k]], 1)
    cnt = np.bincount(L, minlength=n).astype(float); cen = np.stack([np.bincount(L, weights=P[:, a], minlength=n) for a in range(3)], 1) / np.maximum(cnt, 1)[:, None]
    Q = P - cen[L]; cov = np.zeros((n, 3, 3))
    for a in range(3):
        for b in range(a, 3):
            cov[:, a, b] = cov[:, b, a] = np.bincount(L, weights=Q[:, a] * Q[:, b], minlength=n) / np.maximum(cnt, 1)
    cov += np.eye(3) * h * h / 12                                                                           # a single block has the spread of a block
    ev, evec = np.linalg.eigh(cov); widths = 2 * np.sqrt(5 * np.maximum(ev[:, ::-1], 0))                   # full widths of the ellipsoid with the same spread, long first
    ext = np.zeros((n, 3, 2)); ok = cnt > 0
    for a in range(3):
        o = np.lexsort((P[:, a], L)); Ls = L[o]; first = np.searchsorted(Ls, np.arange(n), 'left'); last = np.searchsorted(Ls, np.arange(n), 'right') - 1
        ext[ok, a, 0] = P[o[first[ok]], a] - h / 2; ext[ok, a, 1] = P[o[last[ok]], a] + h / 2
    # the true reach of every body along its own three main directions (long first), end to end
    reach3 = np.zeros((n, 3))
    for a in range(3):
        pr = (Q * evec[L, :, 2 - a]).sum(1); lo = np.full(n, np.inf); hi = np.full(n, -np.inf); np.minimum.at(lo, L, pr); np.maximum.at(hi, L, pr); reach3[ok, a] = (hi - lo)[ok] + h
    return dict(vol=cnt * h ** 3, cnt=cnt, cen=cen, widths=widths, long_axis=evec[:, :, 2], ext=ext, n=n, reach3=reach3)


def at_place(T, m, R, places, skip, cone=15.0):
    """Everything (bodies and thin pieces, but not the bodies in `skip`) whose own centre is seen from the centre of
    body m within `cone` degrees of each named direction and between 0.8 R and 2.4 R away: volume as share of body m."""
    v = T['cen'] - T['cen'][m]; r = np.linalg.norm(v, axis=1); out = []
    for mu, th in places:
        d = np.array([np.cos(np.radians(mu)), np.sin(np.radians(mu)) * np.cos(np.radians(th)), np.sin(np.radians(mu)) * np.sin(np.radians(th))])
        sel = (T['cnt'] > 0) & (r > 0.8 * R) & (r < 2.4 * R) & ((v @ d) > r * np.cos(np.radians(cone))); sel[list(skip)] = False; sel[0] = False
        out.append((mu, th, 100 * T['vol'][sel].sum() / T['vol'][m], int(sel.sum()), 100 * T['vol'][sel].max() / T['vol'][m] if sel.any() else 0.0))
    return out


def ang(v):
    """angle from +x (the row), and angle round the row (0 = +y: up in the flat picture, 90 = +z: off the flat picture)."""
    r = np.linalg.norm(v); return np.degrees(np.arccos(np.clip(v[0] / max(r, 1e-300), -1, 1))), np.degrees(np.arctan2(v[2], v[1])) % 360


def near(seg, T, m, nbody, xs, ys, zs, h, title, reach=4.0, top=16, min_blocks=20):
    mask = seg == m; d = ndi.distance_transform_edt(~mask); labs = np.arange(1, T['n'])
    gap = np.asarray(ndi.minimum(d, labels=seg, index=labs)) - 1.0; pos = ndi.minimum_position(d, labels=seg, index=labs)
    c0 = T['cen'][m]; e = T['ext'][m]; R = 0.5 * (e[0, 1] - e[0, 0])
    say('%s: centre (%.3f, %.3f, %.3f), volume %.4f; extent along the row %.3f (R = half of it = %.3f), up in the flat picture %.3f, off the flat picture %.3f; main widths %.3f / %.3f / %.3f; it fills %.0f %% of the egg that just holds it (a ball or an egg: 100)'
        % (title, *c0, T['vol'][m], e[0, 1] - e[0, 0], R, e[1, 1] - e[1, 0], e[2, 1] - e[2, 0], *T['widths'][m], 100 * T['vol'][m] / (np.pi / 6 * np.prod(e[:, 1] - e[:, 0]))))
    rows = []
    for lb, g, p in zip(labs, gap, pos):
        if lb == m or g > reach or T['cnt'][lb] < min_blocks:
            continue
        tp = np.array([xs[p[0]], ys[p[1]], zs[p[2]]]); a1, t1 = ang(tp - c0); a2, t2 = ang(T['cen'][lb] - c0)
        ax_ = T['long_axis'][lb]; out = (T['cen'][lb] - tp); lean = np.degrees(np.arccos(np.clip(abs(np.dot(ax_, (tp - c0) / np.linalg.norm(tp - c0))), 0, 1)))
        rows.append(dict(vol=T['vol'][lb], lab=int(lb), gap=float(g), a1=a1, t1=t1, a2=a2, t2=t2, w=T['widths'][lb] / R, e=T['reach3'][lb] / R, thin=lb > nbody, lean=lean))
    rows.sort(key=lambda r: -r['vol']); vm = T['vol'][m]; bod = [r for r in rows if not r['thin']]; thn = [r for r in rows if r['thin']]
    cls = lambda rs: '%d over 3 %%, %d of 0.3 .. 3 %%, %d of 0.03 .. 0.3 %%, %d smaller' % (sum(r['vol'] > 0.03 * vm for r in rs), sum(0.003 * vm < r['vol'] <= 0.03 * vm for r in rs), sum(0.0003 * vm < r['vol'] <= 0.003 * vm for r in rs), sum(r['vol'] <= 0.0003 * vm for r in rs))
    say('   within %g blocks of it (pieces of at least %d blocks): BODIES %d (by volume against this body: %s); THIN PIECES %d (%s)' % (reach, min_blocks, len(bod), cls(bod), len(thn), cls(thn)))
    say('   the largest: kind | volume as share of this body | gap in blocks | touching place: degrees from +x, degrees round the row | own centre: the same | main widths in R (the egg of the same spread), long : thick | end-to-end reach along its own three main directions in R | long axis against the line from this body\'s centre through the touching place')
    for r in rows[:top]:
        w = r['w']; e = r['e']
        say('     %-5s | %7.3f %% | %4.1f | %6.1f, %6.1f | %6.1f, %6.1f | %.2f x %.2f x %.2f R, %4.1f : 1 | %.2f x %.2f x %.2f R | %4.1f deg'
            % ('thin' if r['thin'] else 'body', 100 * r['vol'] / vm, r['gap'], r['a1'], r['t1'], r['a2'], r['t2'], w[0], w[1], w[2], w[0] / max(w[2], 1e-9), e[0], e[1], e[2], r['lean']))
    return rows, R


def whole(ins, h, name):
    v = ins.sum(); ht = ins[::-1, ::-1]; mz = ins[:, :, ::-1]; my = ins[:, ::-1]; mx = ins[::-1]
    say('%s: %d blocks inside, volume %.4f' % (name, int(v), v * h ** 3))
    say('   mirror in the flat plane (above against below): %d blocks differ (%.3f %% of the volume)' % (int((ins != mz).sum()), 100 * (ins != mz).sum() / v))
    say('   mirror in the upright plane through the x-axis: %d blocks differ (%.3f %% of the volume)' % (int((ins != my).sum()), 100 * (ins != my).sum() / v))
    d = (ins != ht).sum(); say('   half turn about the upright axis (left against right): %d blocks differ = %.1f %% of the volume counted the explorer\'s way (blocks lost plus blocks gained); share of the solid that is not in its own half-turned copy: %.1f %%' % (int(d), 100 * d / v, 100 * (ins & ~ht).sum() / v))
    d = (ins != mx).sum(); say('   mirror left to right (x -> -x): %.1f %% the same way; not in its mirrored copy: %.1f %%' % (100 * d / v, 100 * (ins & ~mx).sum() / v))
    op = ndi.binary_opening(ins, structure=CROSS, iterations=3); say('   thin share, the explorer\'s recipe (peel 3 blocks, put them back, what does not return): %.1f %%' % (100 * (1 - op.sum() / v)))
    return v


if __name__ == '__main__':
    what = sys.argv[1]; h = float(sys.argv[2]); ks = [float(t) for t in sys.argv[3].split(',')] if len(sys.argv) > 3 else [3.0]
    t0 = time.time(); ins, xs, ys, zs = sk_vox.load(what, h)
    say('=== %s, blocks of side %g' % (what, h)); whole(ins, h, what)
    insc, xc, yc, zc = crop(ins, xs, ys, zs); del ins
    dist = ndi.distance_transform_edt(insc)
    for rad_abs in (0.012, 0.018, 0.024, 0.036):             # my own thin share: what a ball of this radius, rolled about inside the solid, cannot reach
        rad = rad_abs / h; core = dist > rad; reachd = ndi.distance_transform_edt(~core) <= rad
        say('   thin share, my recipe (blocks that a ball of radius %.3f rolled about inside the solid cannot reach): %.1f %%' % (rad_abs, 100 * (insc & ~reachd).sum() / insc.sum()))
    del dist
    xn = 0.8167 if what == 'balls' else 0.945
    for k in ks:
        seg, n, n2, its, loose = segment(insc, k); T = body_table(seg, xc, yc, zc, h)
        vols = np.sort(T['vol'][1:n + 1])[::-1]; tv = np.sort(T['vol'][n + 1:])[::-1]
        say('--- peeled by %g blocks (%.3f): %d bodies (grown back in %d rounds), the eight largest by volume: %s' % (k, k * h, n, its, ', '.join('%.4f' % v for v in vols[:8])))
        say('    thin pieces: %d, together %.2f %% of the volume; the six largest: %s' % (n2, 100 * loose / insc.sum(), ', '.join('%.5f' % v for v in tv[:6])))
        idx = lambda x: tuple(int(np.argmin(np.abs(a - v))) for a, v in ((xc, x), (yc, 0.0), (zc, 0.0)))
        m = int(seg[idx(0.0)])
        rows, R0 = near(seg, T, m, n, xc, yc, zc, h, 'THE MIDDLE BODY')
        skip = [m] + [r['lab'] for r in rows if r['vol'] > 0.03 * T['vol'][m]]
        say('   everything that sits at a named place on the middle body (all bodies and thin pieces whose centre is seen within 15 degrees of the place, 0.8 R .. 2.4 R from the centre), as share of the middle body\'s volume:')
        for mu, th, tot, cnt_, mx in at_place(T, m, R0, [(90.0, 0.0), (90.0, 180.0), (90.0, 90.0), (90.0, 270.0), (132.8, 90.0), (132.8, 270.0), (47.2, 90.0), (132.8, 0.0)], skip):
            say('      %5.1f degrees from +x, %5.1f round the row: %.3f %% in %d pieces (largest piece %.3f %%)' % (mu, th, tot, cnt_, mx))
        for nm, x0 in (('THE LEFT NEIGHBOUR ON THE ROW', -xn), ('THE RIGHT NEIGHBOUR ON THE ROW', xn)):
            lb = int(seg[idx(x0)])
            if lb and lb != m:
                near(seg, T, lb, n, xc, yc, zc, h, nm, top=22)
            else:
                say('%s: not a body of its own at this peel' % nm)
        # rings or single buds: the farthest reach from the row, by the angle round the row, over the middle body's stretch of the row
        i, j, kk = np.nonzero(insc & (np.abs(xc)[:, None, None] < 0.95 * R0)); rho = np.hypot(yc[j], zc[kk]); th = np.degrees(np.arctan2(zc[kk], yc[j])) % 360
        prof = np.zeros(72); np.maximum.at(prof, ((th + 2.5) // 5).astype(int) % 72, rho)
        say('   farthest reach from the row over the middle body (|x| < %.2f), by the angle round the row, every 5 degrees from 0 (up in the flat picture; 90 = off the flat picture), in units of R:' % (0.95 * R0))
        for a in range(0, 72, 18):
            say('      %3d..%3d: %s' % (5 * a, 5 * a + 85, ' '.join('%.2f' % (v / R0) for v in prof[a:a + 18])))
        say('   [%.0f s]' % (time.time() - t0))
