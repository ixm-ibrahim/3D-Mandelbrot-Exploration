"""How the rule wraps the sphere of directions (no iteration). For every direction: the signed area stretch of the
direction map (positive = right way round, negative = inside out). Summed over the sphere:
   net wraps   = right way round minus inside out  (a whole number: the degree; complex squaring spun = 0, one plane = 2)
   right / inside-out = how many spheres' worth each covers.
Also: is the diagonal plane y = z kept, with complex squaring in it (largest error on 20,000 points)?
python out/r17/profiles/cover.py [names]"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen as S
R = S.R
names = sys.argv[1:] or ['lathe', 'oneplane', 'twoplane', 'along', 'away', 'wind2'] + [n for n in R.RULES if n.startswith('p_')]
NU, NP = 300, 28800
u = (np.arange(NU) + 0.5) / NU * 2 - 1; ph = (np.arange(NP) + 0.37) / NP * 2 * np.pi
out = {}
print('%-12s %9s %9s %10s %9s | %s' % ('rule', 'net wraps', 'right way', 'inside out', 'reversed', 'diagonal plane kept (error)'))
rng = np.random.default_rng(5); a = rng.normal(size=20000); b = rng.normal(size=20000)
for nm in names:
    F = R.get(nm); tot = pos = neg = 0.0; rev = 0
    for i0 in range(0, NU, 20):
        U, P = np.meshgrid(u[i0:i0 + 20], ph, indexing='ij'); U = U.ravel(); P = P.ravel(); rho = np.sqrt(1 - U * U)
        pts = np.stack([U, rho * np.cos(P), rho * np.sin(P)], 1)
        J = S.jac(F, pts, h=2e-7); det = np.linalg.det(J) / 2.0          # radial stretch is 2 at radius 1
        tot += det.sum(); pos += det[det > 0].sum(); neg += -det[det < 0].sum(); rev += int((det < 0).sum())
    n = NU * NP
    s = np.sqrt(0.5); X, Y, Z = F(a, b * s, b * s)
    derr = float(max(np.abs(X - (a * a - b * b)).max(), np.abs(Y - 2 * a * b * s).max(), np.abs(Z - 2 * a * b * s).max()))
    out[nm] = dict(net=tot / n, right=pos / n, inside_out=neg / n, reversed_pct=100 * rev / n, diagonal_err=derr)
    print('%-12s %9.2f %9.2f %10.2f %8.1f%% | %.0e' % (nm, tot / n, pos / n, neg / n, 100 * rev / n, derr), flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cover.json'), 'w'), indent=1)
