"""Round 27, checker A, bullet 3, close in: the distance against the true distance next to the touching point of the
middle ball and its right-hand neighbour (picture point (0.525, 0, 0)), where the brute-force list of balls is cheap to
make very fine: every ball within 0.06 of that point with radius >= 1e-5 (the list is complete there down to 3.4e-7
for t >= 1.4 and 7e-7 for t = 1). The shader's number is read at 120 small level pieces (15 x 15 points, side 5e-5 to
1e-2) placed on the skins of random balls within 0.035 of the point, at the default depth 16 and at depth 40.
  python bound_kiss.py <grid> <t>  -> ../logs/bound-kiss-g<grid>-t<t>.txt
"""
import json, os, sys, time
import numpy as np
import ballslib as B
import drive as D
import sampling as SP
import views_ref as VR

g = int(sys.argv[1]); t = float(sys.argv[2])
RMIN = 1e-5; KISS = np.array([1.05 / 2, 0, 0.0])
rng = np.random.default_rng(900 + 10 * g + int(10 * t))
lines = []


def say(s):
    lines.append(s); print(s); sys.stdout.flush()


t0 = time.time()
cell = VR.cell_for(g, t)
C, R, Lv = B.picture_balls(cell, RMIN, keep=B.keep_near(KISS, 0.06))
nb = B.NearBalls(C, R)
say('grid %d, t = %g: %d balls within 0.06 of the touching point with radius >= %g (cell list of %d, radius >= %g); %.0f s' % (g, t, R.size, RMIN, cell['r'].size, cell['rho'], time.time() - t0))
near = np.nonzero((np.linalg.norm(C - KISS, axis=1) - R < 0.035) & (R >= 4 * RMIN))[0]
P = []
for i in rng.choice(near, 120):
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    s = C[i] + v * R[i]
    if np.linalg.norm(s - KISS) > 0.035:
        s = KISS + (s - KISS) * 0.035 / np.linalg.norm(s - KISS) * rng.uniform(0.2, 1)
    P.append([float(s[0]), float(s[1]), float(10 ** rng.uniform(-4.3, -2)), float(s[2]), 15])
for rounds in (16, 40):
    pts, al, tw, es, bs, fr = SP.sample(g, t, rounds, P, 'bound-kiss-g%d-t%g-r%d' % (g, t, rounds))
    keep = np.linalg.norm(pts - KISS, axis=1) < 0.045           # stay where the list is complete all round the point
    pts, al, tw = pts[keep], al[keep], tw[keep]
    Dt, bi = nb.dist(pts, want_index=True)
    inl = Dt < 0
    o = (al > 0) & (Dt > 0)
    ex = al - Dt
    br = o & (al > Dt * (1 + 1e-4) + 1e-9)
    brs = br & (ex > 1e-6) & (al > 1.001 * Dt)
    # single precision: the shader holds the point's own place to about 6e-8, so that much is not the estimate's doing
    b, f, dec, ins = B.glsl_de(pts, t, g, rounds, np.float64)
    dp = B.glsl_d(b, f, dec, ins, 0.0)
    op = dec & ~ins & (Dt > 0)
    brp = op & (dp > Dt * (1 + 1e-9) + 1e-12)
    # the 3D picture's number at the close-up camera of views_page.py ('kiss-eye1': 0.30 from the point)
    gp = (2 * 0.32 / 701.0) * 0.30
    d3 = B.glsl_d(b, f, dec, ins, 2 * gp)
    br3 = op & (d3 > Dt * (1 + 1e-9) + 1e-12)
    ratio = Dt[o] / np.maximum(al[o], 1e-300)
    idx = np.nonzero(o & (al > 2e-7))[0]
    hit = np.zeros(idx.size, bool)
    for k in range(48):
        v = rng.normal(size=(idx.size, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
        q = pts[idx] + v * (al[idx] * 0.999)[:, None]
        res, used, live = B.recipe_inside(q[:, 0], q[:, 1], q[:, 2], t, g, 80, want_rounds=True)
        hit |= res & ~live
    say('   %d rounds: %d points, %d outside (true distance: median %.1e, smallest %.1e) | twin inside but in no listed ball %d (at most %.1e off one); in a listed ball but twin outside %d (at most %.1e deep) | '
        'shader longer than true: %d (beyond single-precision noise: %d; worst excess %.1e) | port (double) longer than true: %d (worst %.1e) | probes: %d of %d points | '
        'true within 1.5 x / 2 x / 5 x the shader: %.0f%% / %.0f%% / %.0f%% | 3D picture number (2 px held, close-up camera): longer than true at %d of %d (worst %.2f px)'
        % (rounds, len(pts), o.sum(), np.median(Dt[o]), Dt[o].min(), (tw & ~inl).sum(), Dt[tw & ~inl].max() if (tw & ~inl).any() else 0, (~tw & inl).sum(), -Dt[~tw & inl].min() if (~tw & inl).any() else 0,
           br.sum(), brs.sum(), ex[br].max() if br.any() else 0, brp.sum(), (dp - Dt)[brp].max() if brp.any() else 0, hit.sum(), idx.size,
           100 * (ratio <= 1.5).mean(), 100 * (ratio <= 2).mean(), 100 * (ratio <= 5).mean(), br3.sum(), op.sum(), ((d3 - Dt) / gp)[br3].max() if br3.any() else 0))
    for i in np.nonzero(brs)[0][:10]:
        say('      beyond noise: p = (%.7f, %.7f, %.7f), shader %.3e, true %.3e, ball radius %.2e' % (pts[i, 0], pts[i, 1], pts[i, 2], al[i], Dt[i], R[bi[i]]))
with open(os.path.join(D.LOGS, 'bound-kiss-g%d-t%g.txt' % (g, t)), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
