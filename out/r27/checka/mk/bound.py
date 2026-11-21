"""Round 27, checker A, bullet 3: is the distance the ray marcher is given ever longer than the true distance?

The true distance is computed by BRUTE FORCE: the list of all balls from walking the group (ballslib.enum_cell,
picture_balls), then the exact distance from each point to the nearest ball surface.
The shader's distance: alpha of the lab's volume samples (sampleSlice), read at
  box:   the random pieces of verdicts.py (22500 points in space, 20250 in the flat cut, per setting and depth)
  near:  100 small pieces (15 x 15 points, side 0.001 to 0.1) placed on the skins of random balls of the list
The 3D picture's own number (min(best, max(free, 2 * uDetail * gPix))) cannot be read from the page; it is
computed from my line-by-line port of de() (ballslib.glsl_de, checked here against the shader's alpha), with gPix
of the start view (camera of the start view, 701 picture rows).
  python bound.py <grid> <t> [near]     -> ../logs/bound-g<grid>-t<t>.json / .txt
"""
import json, os, sys, time
import numpy as np
import ballslib as B
import drive as D

g = int(sys.argv[1]); t = float(sys.argv[2]); do_near = len(sys.argv) > 3 and sys.argv[3] == 'near'
if g == 2:
    rho, rmin = 2e-6, 1e-5
elif t < 1.2:
    rho, rmin = 2e-4, 5e-4
else:
    rho, rmin = 1e-4, 3.3e-4
CAM = np.array([1.0418157964350154, -3.135417226702075, 1.8049673332004073]); PIX = 2 * 0.32 / 701.0; DETAIL = 1.0
rng = np.random.default_rng(100 * g + int(10 * t))
out = dict(grid=g, t=t, rho=rho, rmin=rmin, sets=[])
lines = []


def say(s):
    lines.append(s); print(s); sys.stdout.flush()


t0 = time.time()
cell = B.enum_cell(t, g, rho)
C, R, Lv = B.picture_balls(cell, rmin, keep=B.keep_box())
nb = B.NearBalls(C, R)
say('grid %d, t = %g: brute-force list: %d balls in a cell of the grid (radius >= %g there), %d balls of the picture near the box with radius >= %g; %.0f s'
    % (g, t, cell['r'].size, rho, R.size, rmin, time.time() - t0))
# are the listed balls real? their centres must be inside by the recipe (80 rounds), and a point just outside each skin outside
ck = rng.choice(R.size, min(R.size, 20000), replace=False)
cin = B.recipe_inside(C[ck, 0], C[ck, 1], C[ck, 2], t, g, 80)
dirs = rng.normal(size=(ck.size, 3)); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
pin = C[ck] + dirs * (R[ck] * 0.98)[:, None]
pinr = B.recipe_inside(pin[:, 0], pin[:, 1], pin[:, 2], t, g, 80)
say('   listed balls checked against the recipe (80 rounds): centre inside at %d of %d; a point at 0.98 of the radius inside at %d of %d'
    % (cin.sum(), ck.size, pinr.sum(), ck.size))
out['list'] = dict(cell=int(cell['r'].size), picture=int(R.size), centres_inside=int(cin.sum()), near_skin_inside=int(pinr.sum()), checked=int(ck.size))


def analyse(tag, pts, al, tw, rounds):
    d = dict(tag=tag, n=int(len(pts)), rounds=rounds)
    Dt, bi = nb.dist(pts, want_index=True)
    inl = Dt < 0
    d['twin_inside'] = int(tw.sum()); d['in_listed_ball'] = int(inl.sum())
    d['twin_inside_no_listed_ball'] = int((tw & ~inl).sum()); d['listed_ball_twin_outside'] = int((~tw & inl).sum())
    m = tw & ~inl
    d['twin_inside_no_listed_ball_max_dist'] = float(Dt[m].max()) if m.any() else 0.0
    m = ~tw & inl
    d['listed_ball_twin_outside_max_depth'] = float(-Dt[m].min()) if m.any() else 0.0
    o = (al > 0) & (Dt > 0)
    d['outside'] = int(o.sum())
    ex = al - Dt
    br = o & (al > Dt * (1 + 1e-4) + 1e-9)
    d['breaches'] = int(br.sum()); d['worst_excess'] = float(ex[br].max()) if br.any() else 0.0
    d['worst_ratio'] = float((al[br] / Dt[br]).max()) if br.any() else 0.0
    d['breach_points'] = [dict(p=[float(c) for c in pts[i]], shader=float(al[i]), true=float(Dt[i]), ball_radius=float(R[bi[i]]), ball_level=int(Lv[bi[i]])) for i in np.nonzero(br)[0][:30]]
    # breaches that are more than single-precision noise: more than 1e-6 and more than 0.1 percent too long
    brs = br & (ex > 1e-6) & (al > 1.001 * Dt)
    d['breaches_beyond_noise'] = int(brs.sum())
    ratio = Dt[o] / al[o]
    d['true_within_1.5'] = float((ratio <= 1.5).mean()) if o.any() else 0.0
    d['true_within_2'] = float((ratio <= 2).mean()) if o.any() else 0.0
    d['true_within_5'] = float((ratio <= 5).mean()) if o.any() else 0.0
    d['median_true_over_shader'] = float(np.median(ratio)) if o.any() else 0.0
    d['small_regime'] = int((o & (al < 5 * rmin)).sum())
    # my port against the shader
    b, f, dec, ins = B.glsl_de(pts, t, g, rounds, np.float64)
    dp = B.glsl_d(b, f, dec, ins, 0.0)
    cmpm = o & (al > 1e-6)
    rel = np.abs(dp[cmpm] - al[cmpm]) / al[cmpm]
    d['port_vs_shader_mean_rel'] = float(rel.mean()) if cmpm.any() else 0.0
    d['port_vs_shader_max_rel'] = float(rel.max()) if cmpm.any() else 0.0
    d['port_vs_shader_over_1pc'] = int((rel > 0.01).sum()) if cmpm.any() else 0
    # the port itself against the true distance (double precision, so no single-precision noise)
    op = dec & ~ins & (Dt > 0)
    brp = op & (dp > Dt * (1 + 1e-9) + 1e-12)
    d['port_breaches'] = int(brp.sum()); d['port_worst_excess'] = float((dp - Dt)[brp].max()) if brp.any() else 0.0
    d['port_breach_points'] = [dict(p=[float(c) for c in pts[i]], port=float(dp[i]), best=float(b[i]), free=float(f[i]), true=float(Dt[i]), ball_radius=float(R[bi[i]]), ball_level=int(Lv[bi[i]])) for i in np.nonzero(brp)[0][:30]]
    # the 3D picture's number: "free" not below two ray thresholds
    gp = PIX * np.linalg.norm(pts - CAM, axis=1); hold = 2 * DETAIL * gp
    d3 = B.glsl_d(b, f, dec, ins, hold)
    act = op & (f < hold) & (b > f)
    br3 = op & (d3 > Dt * (1 + 1e-9) + 1e-12)
    d['picture_hold_active'] = int(act.sum()); d['picture_breaches'] = int(br3.sum())
    d['picture_worst_excess_px'] = float(((d3 - Dt) / gp)[br3].max()) if br3.any() else 0.0
    # how far could a ray overstep: the step is uStepK (0.5) times (d + LEVEL e); excess as a share of the true distance
    d['picture_breach_true_px_median'] = float(np.median((Dt / gp)[br3])) if br3.any() else 0.0
    # probing with the recipe: is there a point of a ball inside the sphere of radius 0.999 x the shader's distance?
    idx = np.nonzero(o & (al > 1e-7))[0]
    K = 48
    hit = np.zeros(idx.size, bool)
    for k in range(K):
        v = rng.normal(size=(idx.size, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
        q = pts[idx] + v * (al[idx] * (0.999 if k % 3 else rng.uniform(0.3, 0.999, idx.size)))[:, None]
        res, used, live = B.recipe_inside(q[:, 0], q[:, 1], q[:, 2], t, g, 80, want_rounds=True)
        hit |= res & ~live
    d['probe_points'] = int(idx.size); d['probe_breaches'] = int(hit.sum())
    out['sets'].append(d)
    say('   %-22s points %5d, outside %5d | list against twin: twin inside but no listed ball %d (at most %.1e off a listed ball), in a listed ball but twin outside %d | '
        'shader longer than true: %d (beyond single-precision noise: %d; worst excess %.1e) | true within 1.5 x / 2 x / 5 x the shader: %.0f%% / %.0f%% / %.0f%% | '
        'port against shader: mean %.1e, worst %.1e | port (double) longer than true: %d (worst %.1e) | probes (%d per point): %d of %d points | '
        '3D picture number: hold active at %d, longer than true at %d (worst %.2f px)'
        % (tag, d['n'], d['outside'], d['twin_inside_no_listed_ball'], d['twin_inside_no_listed_ball_max_dist'], d['listed_ball_twin_outside'],
           d['breaches'], d['breaches_beyond_noise'], d['worst_excess'], 100 * d['true_within_1.5'], 100 * d['true_within_2'], 100 * d['true_within_5'],
           d['port_vs_shader_mean_rel'], d['port_vs_shader_max_rel'], d['port_breaches'], d['port_worst_excess'], K, d['probe_breaches'], d['probe_points'],
           d['picture_hold_active'], d['picture_breaches'], d['picture_worst_excess_px']))
    return d


for R_, kind in ((16, 'space'), (16, 'flat'), (40, 'space')):
    f = os.path.join(D.LOGS, 'verd-g%d-t%g-r%d-%s-pts.npy' % (g, t, R_, kind))
    if not os.path.exists(f):
        say('   missing ' + f); continue
    a = np.load(f)
    analyse('box, %s, %d rounds' % (kind, R_), a[:, :3], a[:, 3], a[:, 4] > 0.5, R_)

if do_near:
    import sampling as SP
    # pieces on the skins of random balls: half chosen by area, half evenly among the balls of radius >= 4 rmin
    big = np.nonzero(R >= 4 * rmin)[0]
    w = R[big] ** 2; w /= w.sum()
    pick = np.concatenate([rng.choice(big, 50, p=w), rng.choice(big, 50)])
    P = []
    for i in pick:
        v = rng.normal(size=3); v /= np.linalg.norm(v)
        s = C[i] + v * R[i]
        if abs(s[0]) > 2.0 or abs(s[1]) > 1.5 or abs(s[2]) > 1.5:
            continue
        P.append([float(s[0]), float(s[1]), float(10 ** rng.uniform(-3, -1)), float(s[2]), 15])
    pts, al, tw, es, bs, fr = SP.sample(g, t, 16, P, 'bound-near-g%d-t%g' % (g, t))
    np.save(os.path.join(D.LOGS, 'bound-near-g%d-t%g-pts.npy' % (g, t)), np.column_stack([pts, al, tw, es, bs, fr]))
    analyse('near skins, 16 rounds', pts, al, tw, 16)

with open(os.path.join(D.LOGS, 'bound-g%d-t%g.json' % (g, t)), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
with open(os.path.join(D.LOGS, 'bound-g%d-t%g.txt' % (g, t)), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
