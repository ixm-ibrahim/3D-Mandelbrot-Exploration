"""What the balls object's own kind of recipe gives when the slide is swapped for a stretch: "oranges".

A picture kept by moves that can each be undone (a group picture, as the balls object is). Two moves:
    g   stretch about the point 0 by lam, with the turn 360/n degrees about the upright line through 0
        (n = 2, lam = 1.236: what z^2 - 1 does at its meeting point; n = 3, lam = 1.107: the rabbit)
    J   the sphere inversion in one sphere S that touches the first body from outside
Bodies: n round cones with tip 0 (half opening theta, the opening the true bodies have), and every copy of them.
All copies of S under g lie apart, so the copies of the bodies have disjoint insides (ping-pong).
One more sphere inversion at the start makes the cones finite: they become n bodies pointed at both ends that share
BOTH tips.     python orange.py  -> orange.png (flat cuts and solids), orange.log
"""
import sys, time
import numpy as np
from PIL import Image
import pinchlib as PL, fam

BIG = 1e9


def build(n, lam, theta_deg, delta_deg, K=10, levels=2, chord=1.0):
    th, de = np.radians(theta_deg), np.radians(delta_deg)
    cs = np.array([np.cos(th + de), np.sin(th + de), 0.0]); rs = np.sin(de)            # the sphere S: centre, radius (touches cone 0)
    tau = 2 * np.pi / n

    def g(X, k):
        a = tau * k; co, si = np.cos(a), np.sin(a); s = lam ** k
        return s * np.stack([co * X[..., 0] - si * X[..., 1], si * X[..., 0] + co * X[..., 1], X[..., 2]], -1)

    def J(X):
        d = X - cs; return cs + rs * rs * d / (d * d).sum(-1, keepdims=True)

    fa = tau / 2                                                                         # a clear direction: the middle between two cones
    f0 = np.array([np.cos(fa), np.sin(fa), 0.0])

    def F(X):
        d = X - f0; return f0 + d / (d * d).sum(-1, keepdims=True)

    cones = np.array([[[0.0, 0.0, 0.0], BIG * np.array([np.cos(tau * j), np.sin(tau * j), 0.0]), [np.cos(tau * j), np.sin(tau * j), 0.0]] for j in range(n)])
    ks = np.array([k for k in range(-K, K + 1)]); knz = ks[ks != 0]
    T = J(cones); allb = [cones, np.concatenate([g(T, k) for k in ks])]
    for _ in range(levels - 1):
        T = J(np.concatenate([g(T, k) for k in knz])); allb.append(np.concatenate([g(T, k) for k in ks]))
    L = F(np.concatenate(allb))
    # a turn and a scale to sit in the picture: the two shared tips on the x-axis, 2.4 apart
    ang = -np.arctan2(f0[1], f0[0]); co, si = np.cos(ang), np.sin(ang)
    L = np.stack([co * L[..., 0] - si * L[..., 1], si * L[..., 0] + co * L[..., 1], L[..., 2]], -1) * chord - np.array([chord / 2, 0.0, 0.0])
    sz = np.linalg.norm(L[:, 0] - L[:, 1], axis=1); o = np.argsort(-sz); out = []
    for i in o:
        if sz[i] < 0.006:
            break
        b = PL.spindle(L[i, 0], L[i, 1], L[i, 2], th)
        if np.isfinite(PL.bound(b)[1]) and PL.bound(b)[1] < 20:
            out.append(b)
    return out


if __name__ == '__main__':
    tiles = []
    for nm, n, lam, th, de in (('two bodies at a point (the stretch and half turn of c = -1)', 2, 1.2361, 55.2, 10.0), ('three bodies at a point (the stretch and third of a turn of the rabbit)', 3, 1.1073, 39.9, 7.0)):
        t0 = time.time(); B = build(n, lam, th, de, chord=0.75 if n == 2 else 0.45); box = PL.BOX
        A = PL.flat_union(B, 720, 520, box=box); cnt = np.zeros(A.shape, np.int32)
        for b in B[:400]:
            cnt += PL.flat_union([b], 720, 520, box=box)
        ov, nk = float((cnt >= 2).sum()) / float((cnt >= 1).sum()), min(len(B), 400)
        tiles.append((np.asarray(Image.fromarray(PL.overlay(A, A)).resize((570, 412), Image.LANCZOS)), nm + ': flat cut'))
        dep, px = PL.solid(B, 570, 412, 500, PL.EYES['a'], half_w=1.75)
        tiles.append((PL.M.shade_solid(dep, px), 'the same as a solid'))
        tips = np.array([np.concatenate([b[1], b[2]]) for b in B[:n]])
        print('%s: %d bodies; overlap share %.4f (%d largest unswallowed); the %d largest bodies have their tips at %s; %.0f s'
              % (nm, len(B), ov, nk, n, np.round(tips[:, [0, 1, 3, 4]], 3).tolist(), time.time() - t0)); sys.stdout.flush()
    PL.sheet(tiles, 2, PL.os.path.join(PL.HERE, 'orange.png'), title='A picture kept by a stretch AND its undo-move: bodies that meet in a point meet again at a second point.')
    print('wrote orange.png')
