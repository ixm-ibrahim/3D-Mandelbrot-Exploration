"""The objects of this folder, by name, as lists of bodies (largest first).

    import objs; bodies = objs.get('tree-c1')

    tree-<set>            way (c): the true tree, pointed bodies with the opening that fits the flat picture best
    treetrue-<set>        way (c) with the opening the true bodies have at the meeting point
    treeball-<set>        way (c) with a ball for every body
    pin-<set>             way (a): the two fitted one-step moves ('pin' fit), pointed seed
    pinball-<set>         way (a): the same moves, ball seed
    abest-<set>           way (a) with the fit and the seed opening that come nearest the flat picture
    turn<deg>-c1          way (c) for c = -1, every body swung round the x-axis by <deg> degrees for each undo-move
                          of the kind that keeps the meeting point (a stretch about the meeting point with a turn about the chain)
<set> is c1 or rabbit.
"""
import numpy as np
import pinchlib as PL, fam

BEST = {'c1': 70.0, 'rabbit': 60.0}        # half opening that fits the flat picture best (step_c.log)


def swung_tree(c, tau_deg, theta_deg, smin=0.005):
    """The true tree for c on the x-axis; each body carries the number of '-' undo-moves in its chain and is swung
    round the x-axis by tau times that number."""
    al, be = PL.fixed_points(c)
    L = np.array([[al, -al, 0.0]], complex); N = np.array([0]); allL, allN = [L], [N]
    for _ in range(400):
        m = np.abs(L[:, 2] - c) > 1e-3; par, pn = L[m], N[m]
        if par.shape[0] == 0:
            break
        nl, nn = [], []
        for s in (1, -1):
            nl.append(PL.undo(s, par, c, like=par[:, 2:3])); nn.append(pn + (1 if s < 0 else 0))
        L = np.concatenate(nl); N = np.concatenate(nn); k = np.abs(L[:, 0] - L[:, 1]) >= smin / 8; L, N = L[k], N[k]
        if L.shape[0] == 0:
            break
        allL.append(L); allN.append(N)
    L = np.concatenate(allL); N = np.concatenate(allN); k = np.abs(L[:, 0] - L[:, 1]) >= smin; L, N = L[k], N[k]
    o = np.argsort(-np.abs(L[:, 0] - L[:, 1])); out = []
    for (P, Q, C), n in zip(L[o], N[o]):
        a = np.radians(tau_deg) * n; co, si = np.cos(a), np.sin(a)
        pts = [np.array([w.real, w.imag * co, w.imag * si]) for w in (P, Q, C)]
        b = PL.spindle(pts[0], pts[1], pts[2], np.radians(theta_deg))
        if np.isfinite(PL.bound(b)[1]):
            out.append(b)
    return out


def get(name):
    kind, key = name.rsplit('-', 1); c = PL.CS[key]; al, be = PL.fixed_points(c)
    if kind == 'tree':
        return fam.tree_bodies(fam.true_tree(c, 0.005), 'spin', BEST[key])
    if kind == 'treetrue':
        return fam.tree_bodies(fam.true_tree(c, 0.005), 'spin', fam.OPEN[key])
    if kind == 'treeball':
        return fam.tree_bodies(fam.true_tree(c, 0.005), 'ball')
    if kind in ('pin', 'pinball'):
        mv, _ = PL.fitted(c, 1, 'pin')
        seed = ('ball', 0.0 + 0j, abs(al)) if kind == 'pinball' else ('spin', al, -al, 0.0 + 0j, np.radians(fam.OPEN[key]))
        return fam.orbit(mv, seed, rmin=0.005, cap=60000)[0]
    if kind == 'abest':                                                   # way (a) with the fit and the opening that come nearest the flat picture
        fit, th = (('pin', 70.0) if key == 'c1' else ('osc', 65.0))          # (step_a_scan.log)
        mv, _ = PL.fitted(c, 1, fit)
        return fam.orbit(mv, ('spin', al, -al, 0.0 + 0j, np.radians(th)), rmin=0.005, cap=60000)[0]
    if kind.startswith('turn'):
        return swung_tree(c, float(kind[4:]), BEST[key])
    raise KeyError(name)
