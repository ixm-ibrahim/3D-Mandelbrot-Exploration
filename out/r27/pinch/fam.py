"""Families of bodies: every copy of a seed that a set of fitted moves produces (ways a and b), and the tree of
bodies of the true flat picture with each body replaced by a ball or a spindle (way c).

    import fam
"""
import numpy as np
import pinchlib as PL

OPEN = {'c1': 55.2, 'rabbit': 39.9}        # half opening of the true bodies at the meeting point, degrees (step0.log)


def orbit(moves, seed, rmin=0.004, cap=120000, depth=200):
    """Every copy of the seed under words of the moves (each word applied once; copies smaller than rmin are dropped
    together with what they would produce). seed = ('ball', z0, r) or ('spin', P, Q, C, theta) with flat landmarks.
    Returns (list of bodies, number of copies that held a move's pole and are therefore not bounded)."""
    mats = [m['M'] for m in moves]; bad = 0
    if seed[0] == 'ball':
        Z = np.array([seed[1]], complex); R = np.array([seed[2]], float); allZ, allR = [Z], [R]; tot = 1
        for _ in range(depth):
            nz, nr = [], []
            for Mx in mats:
                c2, r2, ok = PL.disc_image(Mx, Z, R); bad += int((~ok).sum())
                keep = ok & (r2 >= rmin) & (np.abs(c2) < 20) & np.isfinite(r2); nz.append(c2[keep]); nr.append(r2[keep])
            Z = np.concatenate(nz); R = np.concatenate(nr)
            if Z.size == 0:
                break
            if tot + Z.size > cap:
                o = np.argsort(-R)[:max(cap - tot, 0)]; Z, R = Z[o], R[o]
            allZ.append(Z); allR.append(R); tot += Z.size
            if tot >= cap:
                break
        Z = np.concatenate(allZ); R = np.concatenate(allR); o = np.argsort(-R)
        return [PL.ball(Z[i], R[i]) for i in o], bad
    th = seed[4]
    L = np.array([[seed[1], seed[2], seed[3]]], complex); allL = [L]; tot = 1
    for _ in range(depth):
        nl = []
        for Mx in mats:
            L2 = PL.ap(Mx, L); sz = np.abs(L2[:, 0] - L2[:, 1])
            keep = (sz >= 2 * rmin) & np.isfinite(sz) & (np.abs(L2).max(1) < 20); nl.append(L2[keep])
        L = np.concatenate(nl)
        if L.shape[0] == 0:
            break
        if tot + L.shape[0] > cap:
            o = np.argsort(-np.abs(L[:, 0] - L[:, 1]))[:max(cap - tot, 0)]; L = L[o]
        allL.append(L); tot += L.shape[0]
        if tot >= cap:
            break
    L = np.concatenate(allL); o = np.argsort(-np.abs(L[:, 0] - L[:, 1])); out = []
    for i in o:
        b = PL.spindle(PL.to3(L[i, 0]), PL.to3(L[i, 1]), PL.to3(L[i, 2]), th)
        if np.isfinite(PL.bound(b)[1]):
            out.append(b)
        else:
            bad += 1
    return out, bad


def true_tree(c, smin=0.006, cap=60000):
    """The bodies of the true flat picture, each by three landmarks: the image of the meeting point, of its twin and
    of 0 under the chain of true undo-moves that carries the middle body onto it. Returns an array (n, 3), largest first."""
    al, be = PL.fixed_points(c)
    L = np.array([[al, -al, 0.0]], complex); allL = [L]; tot = 1
    for _ in range(400):
        par = L[np.abs(L[:, 2] - c) > 1e-3]                              # the body that holds c is not carried on:
        if par.shape[0] == 0:                                            # its two copies are the halves of the middle body
            break
        nl = []
        for s in (1, -1):
            nl.append(PL.undo(s, par, c, like=par[:, 2:3]))
        L = np.concatenate(nl); sz = np.abs(L[:, 0] - L[:, 1]); L = L[sz >= smin / 8]
        if L.shape[0] == 0:
            break
        allL.append(L); tot += L.shape[0]
        if tot > cap:
            break
    L = np.concatenate(allL); sz = np.abs(L[:, 0] - L[:, 1]); L = L[sz >= smin]
    return L[np.argsort(-np.abs(L[:, 0] - L[:, 1]))]


def tree_bodies(L, shape, theta_deg=None):
    """shape 'ball': the ball through both landmarks about their middle. 'ballc': the ball about the image of 0 whose
    skin passes at the mean distance of the two landmarks. 'spin': the spindle with tips at the two landmarks whose
    middle line passes through the image of 0, half opening theta_deg."""
    out = []
    for P, Q, C in L:
        if shape == 'ball':
            out.append(PL.ball((P + Q) / 2, abs(P - Q) / 2))
        elif shape == 'ballc':
            out.append(PL.ball(C, (abs(P - C) + abs(Q - C)) / 2))
        else:
            b = PL.spindle(PL.to3(P), PL.to3(Q), PL.to3(C), np.radians(theta_deg))
            if np.isfinite(PL.bound(b)[1]):
                out.append(b)
    return out


def samples(b):
    if b[0] == 'ball':
        c, r = b[1], b[2]
        return np.array([c + r * 0.98 * np.array(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 0))])
    _, P, Q, a, ct = b
    e = (Q - P); n = np.array([-e[1], e[0], 0.0]); L = np.linalg.norm(e); n = n / L
    th = np.arccos(ct); sag = 0.5 * L * np.tan(th / 2) * 0.6
    mid = (P + Q) / 2
    return np.array([P + 0.03 * e, Q - 0.03 * e, mid, mid + sag * n, mid - sag * n])


def overlap_share(bodies, top=600, w=720, h=520):
    """Of the largest bodies keep those that are not swallowed by a larger one; share of their joint flat area that
    lies in two or more of them (0 = bodies only touch or sit apart)."""
    B = bodies[:top]; S = [samples(b) for b in B]; keep = []
    for i, b in enumerate(B):
        sw = False
        for j in keep:
            if PL.inside(B[j], S[i]).all():
                sw = True; break
        if not sw:
            keep.append(i)
    cnt = np.zeros((h, w), np.int32)
    for i in keep:
        cnt += PL.flat_union([B[i]], w, h)
    return float((cnt >= 2).sum()) / max(float((cnt >= 1).sum()), 1.0), len(keep)
