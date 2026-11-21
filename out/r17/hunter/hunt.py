"""Hunter task 4: hunt for a smooth rule whose Mandelbrot solid has a bud OFF any exact plane touching the main body
at one point. THESE RULES ARE NOT CANDIDATES FOR THE LAB: they do not keep the cut z = 0 exact (fail J1 by design).
    python out/r17/hunter/hunt.py <rule> [N]
Idea: a bud can touch at one point only where all three eigenvalue sizes reach 1 together. For the one-plane rule P
that happens on the rim of the flat plane because there DP = 2 r * (a rotation). Turning the ANSWER by a fixed
rotation A keeps that property (A * rotation is a rotation) but the plane is no longer kept: F = A P. The rim of
directions (the equator) then maps to a bent curve in c-space that lies in no exact plane.
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R
P = R.get('oneplane')


def rot(axis, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def post(A):
    def F(x, y, z):
        X, Y, Z = P(x, y, z)
        return A[0, 0] * X + A[0, 1] * Y + A[0, 2] * Z, A[1, 0] * X + A[1, 1] * Y + A[1, 2] * Z, A[2, 0] * X + A[2, 1] * Y + A[2, 2] * Z
    return F


def pre_post(A, B):
    """A P(B v): the exact plane of P is B^-1 (z = 0) going in, A (z = 0) coming out."""
    FA = post(A)
    def F(x, y, z):
        return FA(B[0, 0] * x + B[0, 1] * y + B[0, 2] * z, B[1, 0] * x + B[1, 1] * y + B[1, 2] * z, B[2, 0] * x + B[2, 1] * y + B[2, 2] * z)
    return F


HR = {
    'h_tilt10': (post(rot('x', 10)), 'One-plane square, answer turned 10 degrees about the x-axis'),
    'h_tilt25': (post(rot('x', 25)), 'One-plane square, answer turned 25 degrees about the x-axis'),
    'h_tilt45': (post(rot('x', 45)), 'One-plane square, answer turned 45 degrees about the x-axis'),
    'h_tilt90': (post(rot('x', 90)), 'One-plane square, answer turned 90 degrees about the x-axis'),
    'h_roty20': (post(rot('y', 20)), 'One-plane square, answer turned 20 degrees about the y-axis'),
    'h_tilt0':  (post(rot('x', 0)),  'One-plane square itself (control)'),
}

if __name__ == '__main__':
    name = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 129
    F, label = HR[name]
    OUT = os.path.join(HERE, 'hunt'); os.makedirs(OUT, exist_ok=True)
    t0 = time.time(); res = {'rule': name, 'label': label}
    # the rim: directions on the equator, v = u / 2
    t = np.linspace(0, 2 * np.pi, 7201)[:-1]
    u = np.stack([np.cos(t), np.sin(t), 0 * t], -1)
    J = K.jac(F, u); ev = np.linalg.eigvals(J); mod = np.abs(ev)
    res['rim_sizes_min_max'] = [float(mod.min()), float(mod.max())]             # all 2: every eigenvalue reaches 1 together at r = 1/2
    ang = np.abs(np.angle(ev)).max(-1) / (2 * np.pi)                           # the pair's angle in turns
    crim = u / 2 - K.apply(F, u) / 4
    # a plane fitted to the rim curve: how far out of any plane is it?
    cc = crim - crim.mean(0); sv = np.linalg.svd(cc, compute_uv=False)
    res['rim_out_of_plane_rms'] = float(sv[2] / np.sqrt(len(t)))
    # resonant points on the rim
    S = K.skin(F, 361, 720)
    nrm, wgt = K.normals(S['c'])
    cin = S['u'] * (0.9 / S['rho'])[..., None]; cin = cin - K.apply(F, cin)
    nrm[((S['c'] - cin) * nrm).sum(-1) < 0] *= -1
    sub = (slice(0, 361, 2), slice(0, 720, 2))
    per_out = K.periods(F, S['c'][sub] + 0.03 * nrm[sub], steps=1500)
    per_in = K.periods(F, S['c'][sub] - 0.03 * nrm[sub], steps=1500)
    Image.fromarray(K.colour_of(per_out)).resize((720, 362), Image.NEAREST).save(os.path.join(OUT, name + '-chart-out.png'))
    Image.fromarray(K.colour_of(per_in)).resize((720, 362), Image.NEAREST).save(os.path.join(OUT, name + '-chart-in.png'))
    kimg = np.zeros(S['kind'].shape + (3,), np.uint8); tt = np.clip(S['ang'] / 0.5, 0, 1)
    kimg[..., 0] = 90 + 150 * tt; kimg[..., 1] = 85 + 120 * tt; kimg[..., 2] = 70 + 60 * tt
    kimg[S['kind'] == -1] = (70, 130, 235); kimg[S['kind'] == 1] = (130, 130, 135)
    kimg[(S['low'] / S['rho'] > 0.98)] = (255, 60, 60)
    Image.fromarray(kimg).resize((720, 361), Image.NEAREST).save(os.path.join(OUT, name + '-chart-kind.png'))
    res['outside_counts'] = {str(k): int((per_out == k).sum()) for k in np.unique(per_out)}
    print(name, 'charts', round(time.time() - t0), 's', res, flush=True)

    spots = []
    for lab, lev in (('1/2', 0.5), ('1/3', 1 / 3), ('1/4', 0.25), ('1/5', 0.2), ('2/5', 0.4)):
        d = ang - lev
        if lev == 0.5:
            idx = [int(i) for i in np.flatnonzero((ang > np.roll(ang, 1)) & (ang >= np.roll(ang, -1)) & (ang > 0.498))]
        else:
            idx = [int(i) for i in np.flatnonzero(d * np.roll(d, -1) < 0)]
        for i in idx[:2]:
            spots.append((lab, i))
    tiles = []
    for lab, i in spots:
        c0 = crim[i]; T = crim[(i + 1) % len(t)] - crim[i - 1]; T /= np.linalg.norm(T)
        # outward: away from the body, taken as the direction from the image of 0.9 v to c0, made square to T
        v0 = u[i] / 2; cin0 = 0.9 * v0 - K.apply(F, 0.9 * v0[None])[0]
        n = c0 - cin0; n -= (n @ T) * T; n /= np.linalg.norm(n); B = np.cross(n, T)
        row = {'angle': lab, 't_deg': float(np.degrees(t[i])), 'c0': [float(x) for x in c0]}
        hw = 0.16; g = np.linspace(-hw, hw, 321)
        for pl, (e1, e2) in (('along the rim', (T, n)), ('across the rim', (B, n))):
            A1, A2 = np.meshgrid(g, g, indexing='xy')
            cgrid = c0 + A1[..., None] * e1 + A2[::-1, :, None] * e2            # e2 (outward) up
            per = K.periods(F, cgrid, steps=1200)
            img = K.colour_of(per)
            img[160, 160] = (255, 0, 0)
            row['share_' + pl] = {str(k): float((per == k).mean()) for k in np.unique(per)}
            tiles.append(('%s: rim point with angle %s of a turn, cut %s (0.32 wide, outward is up)' % (name, lab, pl), img))
        res.setdefault('spots', []).append(row)
        print(name, lab, row, round(time.time() - t0), 's', flush=True)
    W = 321
    im = Image.new('RGB', (8 + 4 * (W + 8), 8 + ((len(tiles) + 3) // 4) * (W + 40)), (12, 14, 20)); dr = ImageDraw.Draw(im)
    for k, (ttl, img) in enumerate(tiles):
        x0 = 8 + (k % 4) * (W + 8); y0 = 8 + (k // 4) * (W + 40)
        dr.text((x0, y0), ttl.split(': ')[1][:52], fill=(225, 225, 230), font=K.font(12)); dr.text((x0, y0 + 15), ttl.split(': ')[1][52:], fill=(225, 225, 230), font=K.font(12))
        im.paste(Image.fromarray(img), (x0, y0 + 32))
    im.save(os.path.join(OUT, name + '-spots.png'))

    # the solid
    L = 1.3; cen = np.array([-0.45, 0.0, 0.0]); h = 2 * L / (N - 1)
    ax = np.linspace(-L, L, N)
    X, Y, Z = np.meshgrid(cen[0] + ax, ax, ax, indexing='ij')
    lab3 = K.periods(F, np.stack([X, Y, Z], -1), steps=400).astype(np.int16); lab3[lab3 >= 9] = -2
    tot = max((lab3 != 0).sum(), 1)
    res['solid'] = {'volume': float(tot * h ** 3), 'p1': float((lab3 == 1).sum() / tot), 'p2': float((lab3 == 2).sum() / tot), 'p3': float((lab3 == 3).sum() / tot),
                    'p4': float((lab3 == 4).sum() / tot), 'bounded_no_repeat': float((lab3 == -1).sum() / tot)}
    np.savez_compressed(os.path.join(OUT, name + '.npz'), lab=lab3, crim=crim, ang=ang)
    lo = np.array([cen[0] - L, -L, -L])
    for vn, (az, el) in (('a', (-65, 28)), ('b', (-90, 82)), ('c', (150, 22)), ('d', (-90, 3))):
        img = K.render(lab3, lo, h, az, el, S=440, half=1.15, centre=cen, curves=[(crim, (255, 60, 60), 0)])
        Image.fromarray(img).save(os.path.join(OUT, '%s-view-%s.png' % (name, vn)))
    res['seconds'] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, name + '.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))
