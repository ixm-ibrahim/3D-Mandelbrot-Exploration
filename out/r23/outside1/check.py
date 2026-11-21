"""Round 23 outside1: the numbers for every outside formula.   python out/r23/outside1/check.py [name ...]
For each: flat check (M.flat_check), lift test, the screen of round 17 (covers, folded share, jumps = tear),
and which directions are sent to -x and to +x (round 17's count_dirs, copied so that it takes a plain function).
Writes checks.json beside this file."""
import os, sys, json, io, contextlib, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r17', 'blends'))
import mem as M, outrules as O, screen as SC

rngD = np.random.default_rng(11); V = rngD.normal(size=(1500000, 3)); V /= np.linalg.norm(V, axis=1)[:, None]


def groups(P):
    out = []; P = list(P)
    while P:
        c = P[0]; A = np.array(P); d = A @ c
        near = d > np.cos(np.radians(12.0)); out.append((A[near].mean(0), int(near.sum()))); P = [p for p, n in zip(P, near) if not n]
    return out


def where(c):
    c = c / np.linalg.norm(c)
    return '(%.0f from +x, %.0f round)' % (np.degrees(np.arccos(np.clip(c[0], -1, 1))), np.degrees(np.arctan2(c[2], c[1])))


def count_dirs(F):
    with np.errstate(all='ignore'):
        X, Y, Z = F(V[:, 0], V[:, 1], V[:, 2]); n = np.sqrt(X * X + Y * Y + Z * Z); X = X / n
    res = {}
    for tag, sel in (('to -x', X < -np.cos(np.radians(1.5))), ('to +x', X > np.cos(np.radians(1.5)))):
        g = [q for q in groups(V[sel][:3000]) if q[1] >= 3]
        res[tag] = dict(groups=len(g), share=float(sel.mean()), where=[where(q[0]) for q in g[:12]])
    return res


def lift(rule, c, n=40000, steps=60, h=1e-6, seed=7):
    """Of the flat-inside points of the Julia set of c (complex orbit), the share that stays when lifted by h."""
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    ins = M.flat_stay(zr, zi, c[0], c[1], steps) >= steps
    st = M.stay(rule, zr[ins], zi[ins], np.full(ins.sum(), h), c[0], c[1], 0.0, steps) >= steps
    return float(st.mean()), int(ins.sum())


def inside_share(rule, c, n=200000, steps=40, seed=9):
    rng = np.random.default_rng(seed); v = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(n, 3))
    return float((M.stay(rule, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], steps) >= steps).mean())


if __name__ == '__main__':
    names = sys.argv[1:] or (['oneplane', 'twoplane', 'along'] + O.NAMES)
    path = os.path.join(HERE, 'checks.json'); res = json.load(open(path)) if os.path.exists(path) else {}
    for nm in names:
        t0 = time.time()
        if nm in ('oneplane', 'twoplane', 'along'):
            rule = M.bench(nm); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); import rules as R; F = R.get(nm)
        else:
            rule = O.get(nm); F = None if nm == 'hyper' else O.plain(nm)
        d = {}
        with np.errstate(all='ignore'):
            d['flat'] = M.flat_check(rule, n=20000)
            d['lift_basilica'], d['n_basilica'] = lift(rule, (-1.0, 0.0)); d['lift_rabbit'], d['n_rabbit'] = lift(rule, M.RABBIT[:2])
            d['inside_basilica'] = inside_share(rule, (-1.0, 0.0, 0.0)); d['inside_rabbit'] = inside_share(rule, M.RABBIT)
            if F is not None:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    s = SC.screen(nm, F, n=200000)
                d['screen'] = {k: (v if not isinstance(v, list) else [float(t) for t in v]) for k, v in s.items()}
                d['dirs'] = count_dirs(F)
        res[nm] = d
        f = d['flat']
        line = '%-12s flat differ: M %d, basilica %d, rabbit %d, Siegel %d of %d, strays %.1e | lift stays: basilica %.3f, rabbit %.3f | inside share: basilica %.4f, rabbit %.4f' % (
            nm, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], d['lift_basilica'], d['lift_rabbit'], d['inside_basilica'], d['inside_rabbit'])
        if 'screen' in d:
            s = d['screen']; q = d['dirs']
            line += '\n             covers %.2f | folded %.1f %% | jumps %.0e %.0e %.0e | stretch med %.2f, 99%% %.2f | to -x: %d groups (%.4f) %s | to +x: %d groups (%.4f) %s' % (
                s['degree'], s['folded_pct'], *s['jumps'], s['stretch_median'], s['stretch_99'], q['to -x']['groups'], q['to -x']['share'], ' '.join(q['to -x']['where'][:8]),
                q['to +x']['groups'], q['to +x']['share'], ' '.join(q['to +x']['where'][:8]))
        print(line + '   [%.0f s]' % (time.time() - t0), flush=True)
        json.dump(res, open(path, 'w'), indent=1)
