"""Is the grey ('bounded, never repeats') real, or only slow settling? Take grey voxels of a known rule's solid and
run them 30,000 steps with a tighter test; also check the model: does the orbit of c find the attracting resting point?"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R
out = {}
for name in ['lathe', 'oneplane', 'along', 'twoplane']:
    F = R.get(name)
    d = np.load(os.path.join(HERE, 'skin', name + '.npz')); lab = d['lab']; N = lab.shape[0]
    L = 1.3; ax = np.linspace(-L, L, N)
    idx = np.argwhere(lab == -1); rng = np.random.default_rng(1)
    pick = idx[rng.choice(len(idx), min(3000, len(idx)), replace=False)] if len(idx) else idx
    c = np.stack([-0.55 + ax[pick[:, 0]], ax[pick[:, 1]], ax[pick[:, 2]]], -1) if len(idx) else np.zeros((0, 3))
    p = K.periods(F, c, steps=30000, pmax=60, tol=1e-7) if len(c) else np.zeros(0, int)
    r = {'grey_voxels': int(len(idx)), 'tested': int(len(c)), 'after_30000_steps': {'escaped': float((p == 0).mean()) if len(c) else None, 'period_1': float((p == 1).mean()) if len(c) else None,
         'period_2_to_60': float((p >= 2).mean()) if len(c) else None, 'still_never_repeats': float((p == -1).mean()) if len(c) else None}}
    # the model: resting point at 0.5, 0.8, 0.95 of the way to the skin; does the orbit of c end on it?
    S = K.skin(F, 181, 360)
    for frac in (0.5, 0.8, 0.95):
        v = S['u'] * (frac / S['rho'])[..., None]; cc = v - K.apply(F, v)
        w = cc.reshape(-1, 3).copy(); v0 = v.reshape(-1, 3); alive = np.ones(len(w), bool)
        for k in range(3000):
            w = K.apply(F, w) + cc.reshape(-1, 3)
            alive &= (w * w).sum(1) <= 4.0; w[~alive] = 0
        ok = alive & (np.abs(w - v0).max(1) < 1e-4)
        sw = (np.sin(S['th'])[:, None] * np.ones(S['rho'].shape)).ravel(); kd = S['kind'].ravel(); good = ~S['bad'].ravel()
        r['orbit_of_c_reaches_resting_point_at_%.2f' % frac] = {nm: (float((sw * ok)[(kd == k_) & good].sum() / max(sw[(kd == k_) & good].sum(), 1e-30)) if ((kd == k_) & good).any() else None) for nm, k_ in (('pair', 0), ('minus1', -1), ('plus1', 1))}
        r['escapes_at_%.2f' % frac] = float((sw * ~alive)[good].sum() / sw[good].sum())
    out[name] = r; print(name, json.dumps(r), flush=True)
json.dump(out, open(os.path.join(HERE, 'greycheck.json'), 'w'), indent=1)
