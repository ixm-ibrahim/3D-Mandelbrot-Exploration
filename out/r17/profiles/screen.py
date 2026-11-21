"""Screen for the profile family: checks, how the rule treats directions (folds, stretch), and the close cut.

    python out/r17/profiles/screen.py <rule> [more]      (one process per call; run several calls at once)

The close cut is the orchestrator's (out/me/r16/closecut.py: same boxes, same steps, same hair number); only the
picture is written here (out/r17/profiles/cc/closecut-<rule>.png) instead of out/me/r16/.
"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import closecut as CC
import truth as T
import rules as R
os.makedirs(os.path.join(HERE, 'cc'), exist_ok=True)


def checks(F, n=20000, seed=3):
    rng = np.random.default_rng(seed); P = rng.normal(size=(n, 3)); x, y, z = P.T
    X, Y, Z = F(x, y, z); out = {}
    out['length'] = float(np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P ** 2).sum(1)).max())
    X0, Y0, Z0 = F(x, y, 0 * z); out['plane_z0'] = float(max(np.abs(X0 - (x * x - y * y)).max(), np.abs(Y0 - 2 * x * y).max(), np.abs(Z0).max()))
    X0, Y0, Z0 = F(x, 0 * y, z); out['plane_y0'] = float(max(np.abs(X0 - (x * x - z * z)).max(), np.abs(Z0 - 2 * x * z).max(), np.abs(Y0).max()))
    Xm, Ym, Zm = F(x, y, -z); out['mirror_z'] = float(max(np.abs(Xm - X).max(), np.abs(Ym - Y).max(), np.abs(Zm + Z).max()))
    Xm, Ym, Zm = F(x, -y, z); out['mirror_y'] = float(max(np.abs(Xm - X).max(), np.abs(Ym + Y).max(), np.abs(Zm - Z).max()))
    return out


def jac(F, P, h=1e-6):
    J = np.zeros((P.shape[0], 3, 3))
    for k in range(3):
        d = np.zeros(3); d[k] = h
        A = np.stack(F(*(P + d).T), 1); B = np.stack(F(*(P - d).T), 1)
        J[:, :, k] = (A - B) / (2 * h)
    return J


def directions(F, n=200000, seed=7):
    """On the unit sphere: share of directions where the rule turns space inside out (det < 0), and the stretch
    (singular values over 2 = what complex squaring gives at radius 1)."""
    rng = np.random.default_rng(seed); P = rng.normal(size=(n, 3)); P /= np.linalg.norm(P, axis=1)[:, None]
    J = jac(F, P); det = np.linalg.det(J); sv = np.linalg.svd(J, compute_uv=False) / 2.0
    neg = P[:, 0] < 0
    return dict(reversed_pct=float(100 * (det < 0).mean()), reversed_pct_xneg=float(100 * (det[neg] < 0).mean()), reversed_pct_xpos=float(100 * (det[~neg] < 0).mean()),
                stretch_max=float(sv[:, 0].max()), stretch_p99=float(np.percentile(sv[:, 0], 99)), stretch_median=float(np.median(sv[:, 0])),
                squash_p01=float(np.percentile(sv[:, 2], 1)), aniso_median=float(np.median(sv[:, 0] / np.maximum(sv[:, 2], 1e-12))),
                aniso_p90=float(np.percentile(sv[:, 0] / np.maximum(sv[:, 2], 1e-12), 90)))


def look(name, F, W=CC.W, H=CC.H):
    rows = []; nums = []
    for ang in CC.ANGLES:
        e = CC.edge(F, ang); tiles = []
        for hw in CC.WIDTHS:
            n = T.cut(F, ang, (CC.X0 - hw, CC.X0 + hw, e - 0.7 * hw, e + 0.7 * hw), W, H, CC.STEPS)
            tiles.append(T.shade(n, CC.STEPS)); nums.append(CC.hair(n >= CC.STEPS))
        rows.append((f'{name}: plane {ang} degrees from the flat plane, skin at x = {CC.X0} (height {e:.4f}), {CC.STEPS} steps. '
                     f'Widths 0.2, 0.04, 0.008. hair {nums[-3]:.2f}, {nums[-2]:.2f}, {nums[-1]:.2f}', tiles))
    im = Image.new('RGB', (10 + 3 * (W + 10), 10 + len(rows) * (H + 34)), (12, 14, 20)); d = ImageDraw.Draw(im)
    for i, (t, tiles) in enumerate(rows):
        y = 10 + i * (H + 34); d.text((10, y), t, fill=(230, 230, 235), font=T.font(17))
        for j, a in enumerate(tiles):
            im.paste(Image.fromarray(a), (10 + j * (W + 10), y + 26))
    im.save(os.path.join(HERE, 'cc', f'closecut-{name}.png'))
    return [float(v) for v in nums]


if __name__ == '__main__':
    for nm in sys.argv[1:]:
        t0 = time.time(); F = R.get(nm); res = dict(rule=nm, label=R.RULES[nm][1])
        res['checks'] = checks(F); res['directions'] = directions(F)
        res['hair'] = look(nm, F); res['hair_worst'] = float(np.nanmax(res['hair'])); res['seconds'] = time.time() - t0
        json.dump(res, open(os.path.join(HERE, 'cc', nm + '.json'), 'w'), indent=1)
        c, d = res['checks'], res['directions']
        print('%-10s hair %s worst %.2f | reversed %.0f %% (x<0: %.0f, x>0: %.0f) stretch max %.1f p99 %.1f squash p01 %.2f aniso med %.2f p90 %.1f | len %.0e z0 %.0e y0 %.0e mir %.0e %.0e | %.0f s' % (
            nm, ' '.join('%.2f' % v for v in res['hair']), res['hair_worst'], d['reversed_pct'], d['reversed_pct_xneg'], d['reversed_pct_xpos'], d['stretch_max'], d['stretch_p99'],
            d['squash_p01'], d['aniso_median'], d['aniso_p90'], c['length'], c['plane_z0'], c['plane_y0'], c['mirror_z'], c['mirror_y'], res['seconds']), flush=True)
