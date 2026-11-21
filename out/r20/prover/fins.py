"""W5: are the buds in the copy planes round, and how thin are the buds between them, generation by generation?
    python out/r20/prover/fins.py [rule]      rule = sin3 (m_w3, default), lin3, flat3, sin5, band10, band20
Basilica, c = -1.  Method (no voxels, no picture needed): the body B2 on the x-axis left of the body round -1 has
its middle at x = -1.39.  Every bud of the solid that is a copy of B2 contains an exact pre-image of that point.
Generation 1 = the 2k buds on the middle body at x = 0 (pre-images of B2).  Generation 2 = their pre-images, and so on
(2k each).  For every bud: its width through that point along three directions, found by walking point by point
until the orbit escapes: along the ray from the origin, along the meridian (toward the x-axis), and ROUND the x-axis.
EXPECT (pencil): width along the meridian / width round the axis = 1 for every bud whose whole line of ancestors lies
in the copy planes, and = the product of g'(a) over its ancestors otherwise (about 4.6 at generation 2 for m_w3)."""
import sys
import numpy as np
import lib as L
S = L.S
rule = sys.argv[1] if len(sys.argv) > 1 else 'sin3'
K = {'sin3': 3, 'lin3': 3, 'flat3': 3, 'sin5': 5, 'band10': 3, 'band20': 3, 'one': 1}[rule]
g = {'sin3': L.g_sin(3), 'lin3': L.g_lin(3), 'flat3': L.g_flat(3), 'sin5': L.g_sin(5), 'band10': L.g_band(3, 10), 'band20': L.g_band(3, 20),
     'one': (lambda a: a)}[rule]
F = L.wind(g)
C = np.array([-1.0, 0.0, 0.0]); STEPS = 80

# inverse of g on one turn, by table and Newton
ta = np.linspace(0, 2 * np.pi, 2000001); tg = g(ta)
def dg(a, h=1e-6):
    return (g(a + h) - g(a - h)) / (2 * h)
def ginv(A):
    a = np.interp(A, tg, ta)
    for _ in range(4):
        d = dg(a); a = a - (g(a) - A) / np.maximum(d, 1e-9)
    return a

def preimages(p):
    """All 2k points v with F(v) + c = p, for points p off the x-axis. p: (m, 3) -> (m * 2k, 3), plus parent index."""
    q = p - C; r = np.linalg.norm(q, axis=1); Rr = np.sqrt(r)
    s2 = q[:, 2] / r; lon2 = np.arctan2(q[:, 1], q[:, 0])
    s = (np.sqrt(1 + s2) - np.sqrt(1 - s2)) / (np.sqrt(1 + s2) + np.sqrt(1 - s2)); h = np.sqrt(1 - s * s)
    out = []; par = []
    for half in (0.0, np.pi):
        lon = lon2 / 2 + half
        x = Rr * h * np.cos(lon); y = Rr * h * np.sin(lon); z = Rr * s
        rho = np.hypot(y, z); A = np.mod(np.arctan2(z, y), 2 * np.pi)
        for m in range(K):
            a = ginv(A + 2 * np.pi * m)
            out.append(np.stack([x, rho * np.cos(a), rho * np.sin(a)], 1)); par.append(np.arange(len(p)))
    return np.concatenate(out), np.concatenate(par)

def widths(p, tmax, n=1200):
    """Width of the solid through p along the ray, the meridian and round the x-axis (straight lines, both ways)."""
    r = np.linalg.norm(p, axis=1)[:, None]; e_r = p / r
    a = np.arctan2(p[:, 2], p[:, 1]); e_a = np.stack([0 * a, -np.sin(a), np.cos(a)], 1)
    e_m = np.cross(e_a, e_r)
    t = np.linspace(0, 1, n)[1:]
    res = []
    for e in (e_r, e_m, e_a):
        w = np.zeros(len(p))
        for sgn in (1, -1):
            pts = p[:, None, :] + sgn * (tmax[:, None, None] * t[None, :, None]) * e[:, None, :]
            ins = L.member(F, pts[..., 0], pts[..., 1], pts[..., 2], C, STEPS) >= STEPS
            first_out = np.where(ins.all(1), n - 1, np.argmin(ins, axis=1))
            w += tmax * t[np.minimum(first_out, n - 2)]
        res.append(w)
    return np.stack(res, 1)

def gprime_of(p):
    a = np.arctan2(p[:, 2], p[:, 1]); return dg(a), np.degrees(a) % 360

print(f'rule {rule} (k = {K}), basilica, {STEPS} steps')
gen = [None, None]
# generation 1: pre-images of the middle of B2 = (-1.39, 0, 0): at x = 0, distance sqrt(0.39) from the axis, in the 2k copy half-planes
rho1 = np.sqrt(0.39); aa = np.arange(2 * K) * np.pi / K
p1 = np.stack([0 * aa, rho1 * np.cos(aa), rho1 * np.sin(aa)], 1)
chk = np.array(F(p1[:, 0], p1[:, 1], p1[:, 2])).T + C
print('  generation 1 check: F(p) + c - (-1.39, 0, 0), largest', float(np.abs(chk - np.array([-1.39, 0, 0])).max()))
pts = p1; prod = np.ones(len(p1)); inplane = np.ones(len(p1), bool)
for G in range(1, (5 if K == 3 else 4)):
    if G > 1:
        new, par = preimages(pts)
        chk = np.array(F(new[:, 0], new[:, 1], new[:, 2])).T + C
        err = float(np.abs(chk - pts[par]).max())
        gp, adeg = gprime_of(new)
        prod = prod[par] * gp; inplane = inplane[par] & (np.abs(gp - 1) < 1e-6) & (np.abs(np.sin(np.radians(adeg) * K)) < 1e-6)
        pts = new
    else:
        err = 0.0
    scale = 0.5 ** (G - 1)
    tmax = np.full(len(pts), 0.35 * scale)
    W = widths(pts, tmax)
    ok = (W.min(1) > 0)
    ratio = W[:, 1] / np.maximum(W[:, 2], 1e-12)
    print(f'\n  generation {G}: {len(pts)} buds (pre-image error {err:.1e}); in the copy planes all the way: {int(inplane.sum())}; between the planes: {int((~inplane).sum())}')
    for tag, sel in (('in the copy planes', inplane), ('between the planes', ~inplane)):
        if sel.sum() == 0:
            continue
        w = W[sel]; rt = ratio[sel]; pr = prod[sel]
        print(f'     {tag:19s}: width along ray {np.median(w[:,0]):.4f}, along meridian {np.median(w[:,1]):.4f}, round the axis {np.median(w[:,2]):.4f} (medians)')
        print(f'     {"":19s}  meridian / round-the-axis: smallest {rt.min():.2f}, median {np.median(rt):.2f}, largest {rt.max():.2f};   product of g\' over ancestors: smallest {pr.min():.2f}, median {np.median(pr):.2f}, largest {pr.max():.2f}')
        if sel.sum() > 6:
            lr = np.log(rt); lp = np.log(pr)
            if lp.std() > 1e-9:
                print(f'     {"":19s}  measured ratio against predicted product: correlation of logs {np.corrcoef(lr, lp)[0,1]:.3f}, median of ratio / product {np.median(rt / pr):.2f}')
        thin = (rt > 2).mean() * 100
        print(f'     {"":19s}  share thinner than 2 to 1: {thin:.0f} %;  thinner than 5 to 1: {(rt > 5).mean()*100:.0f} %;  thinner than 20 to 1: {(rt > 20).mean()*100:.0f} %')
    if G == 2:
        sel = ~inplane
        a = np.degrees(np.arctan2(pts[sel, 2], pts[sel, 1])) % 60
        print(f'     between-plane buds of generation 2 sit at x = +-{np.abs(pts[sel,0]).mean():.4f}, {np.hypot(pts[sel,1], pts[sel,2]).mean():.4f} from the axis, turned (mod 60 deg) {sorted(set(np.round(a, 1).tolist()))} deg')
        np.save(f'{L.HERE}/logs/gen2-{rule}.npy', np.concatenate([pts, W, prod[:, None], inplane[:, None]], 1))
    if G == 3:
        np.save(f'{L.HERE}/logs/gen3-{rule}.npy', np.concatenate([pts, W, prod[:, None], inplane[:, None]], 1))
