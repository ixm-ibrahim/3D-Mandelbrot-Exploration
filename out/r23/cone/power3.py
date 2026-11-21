"""Step 4: power 3. Cones at cos L = 2/3 (twice round, turned over) and cos L = 1/3 (once round).
    python out/r23/cone/power3.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L
M = L.M
MU1, MU2 = L.MU31, L.MU32; D = MU2 - MU1


def weld3(x, y, z, th1=0.0, th2=0.0):
    """No-fold choice: the first mix is 3/5 turn-over where w^3 and kappa1/w^2 reach the same latitude (mu = 0.4 MU1),
    the second is 2/3 where kappa1/w^2 and w/kappa2 do (a third of the way from MU1 to MU2)."""
    mu, lam = L._mulam(x, y, z); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    a = np.minimum(3 * am, 60.0); b = np.clip(2 * (MU1 - am), -60, 60); d = np.clip(am - MU2, -60, 60)
    E = (np.cos(3 * lam) / np.cosh(a), np.sin(3 * lam) / np.cosh(a), np.tanh(a))
    C1 = (np.cos(th1 - 2 * lam) / np.cosh(b), np.sin(th1 - 2 * lam) / np.cosh(b), np.tanh(b))
    C2 = (np.cos(th2 + lam) / np.cosh(d), np.sin(th2 + lam) / np.cosh(d), np.tanh(d))
    chi1 = L.smooth(am / (0.4 * MU1 / 0.567128), 3); chi2 = L.smooth((am - MU1) / ((D / 3) / 0.613037), 3)
    low = am < MU1; out = [np.where(low, (1 - chi1) * E[i] + chi1 * C1[i], (1 - chi2) * C1[i] + chi2 * C2[i]) for i in range(3)]
    n = np.sqrt(out[0] ** 2 + out[1] ** 2 + out[2] ** 2); n = np.where(n > 0, n, 1.0)
    return out[0] / n, out[1] / n, sg * out[2] / n


def rule3(th1, th2, name):
    def F(x, y, z):
        r2 = x * x + y * y + z * z; X, Y, Z = weld3(x, y, z, th1, th2); s = r2 ** 1.5; ok = r2 > 0
        return np.where(ok, s * X, 0.0), np.where(ok, s * Y, 0.0), np.where(ok, s * Z, 0.0)
    return M.fixed(F, name, name)


def oneplane3(x, y, z):
    """The one-plane rule at power 3: w^3 on directions, length cubed."""
    mu, lam = L._mulam(x, y, z); r2 = x * x + y * y + z * z; s = r2 ** 1.5; a = np.clip(3 * mu, -60, 60)
    return s * np.cos(3 * lam) / np.cosh(a), s * np.sin(3 * lam) / np.cosh(a), s * np.tanh(a)


if __name__ == '__main__':
    print('power 3: cones at latitude %.2f (mu %.4f) and %.2f (mu %.4f)' % (np.degrees(L.L31), MU1, np.degrees(L.L32), MU2))
    for th1, th2 in ((0.0, 0.0), (np.pi / 2, 0.0), (np.pi / 2, np.pi / 2)):
        G = lambda x, y, z: weld3(x, y, z, th1, th2)
        o, (lat, lon, g, s1, s2, det) = L.numbers(G, n=900, quiet=True)
        print('th1 %.2f th2 %.2f: covers %.4f, folded share %.6f, squeezed more than 2 to 1: %.3f, more than 4 to 1: %.3f' % (th1, th2, o['covers'], o['folded_share'], o['share_ratio_over_2'], o['share_ratio_over_4']))
        for deg in (np.degrees(L.L31), np.degrees(L.L32)):
            i = int(np.argmin(np.abs(np.degrees(lat) - deg))); il = np.degrees(np.arcsin(np.clip(g[i, :, 2], -1, 1)))
            lo = np.unwrap(np.arctan2(g[i, :, 1], g[i, :, 0])); print('   circle at latitude %.2f: sent to latitude %.2f..%.2f, goes round %.2f times, stretches %.3f..%.3f and %.3f..%.3f'
                                                                      % (np.degrees(lat[i]), il.min(), il.max(), (lo[-1] - lo[0]) / (2 * np.pi), s2[i].min(), s2[i].max(), s1[i].min(), s1[i].max()))
        print('   critical directions (lat, lon -> lat, lon):', [tuple(round(v, 1) for v in c[:4]) for c in o['critical (lat, lon -> lat, lon, stretch)']])
        # directions sent into the flat plane: count the circles and how often each goes round
        zimg = g[..., 2]; j = 7; col = zimg[:, j]; k = np.nonzero(np.sign(col[1:]) != np.sign(col[:-1]))[0]
        print('   along one meridian the image crosses the flat plane at latitudes', np.round(np.degrees(lat[k]), 1))
    # the flat plane: exact?
    rng = np.random.default_rng(3); x, y = rng.uniform(-1.5, 1.5, 20000), rng.uniform(-1.5, 1.5, 20000); r = rule3(np.pi / 2, 0.0, 'cones3')
    X, Y, Z, _ = r.step(x, y, 0 * x, (), 0, 0, 0, 0); zz = (x + 1j * y) ** 3
    print('flat plane: largest difference from z^3: %.2e, largest height %.2e' % (np.abs(X + 1j * Y - zz).max(), np.abs(Z).max()))
    # pictures: c = i (0 -> i -> 0, two bodies swap) and c = 0.2 + 0.55i
    rules = [M.fixed(oneplane3, 'one plane, power 3', 'one plane, power 3'), rule3(0.0, 0.0, 'cones, power 3, both opening along +x'), rule3(np.pi / 2, 0.0, 'cones, power 3, first pair turned a quarter')]
    cuts = [('flat', (1, 0, 0), (0, 1, 0)), ('upright through x', (1, 0, 0), (0, 0, 1)), ('upright through y', (0, 1, 0), (0, 0, 1)), ('upright, 36 deg from x', L.lonv(36), (0, 0, 1)), ('tilted 30 about x', (1, 0, 0), (0, float(np.cos(np.radians(30))), 0.5))]
    w, h, steps, pad = 250, 190, 50, 6
    for sn, c in (('c = i, power 3', (0.0, 1.0, 0.0)), ('c = -0.55i... c = 0.2 + 0.5i, power 3', (0.2, 0.5, 0.0))):
        im = Image.new('RGB', (pad + len(cuts) * (w + pad), 8 + len(rules) * (h + 26)), (12, 14, 20)); d = ImageDraw.Draw(im)
        for i, r in enumerate(rules):
            yy = 26 + i * (h + 26); d.text((pad, yy - 20), r.name, fill=(235, 220, 170), font=M.font(14))
            for kk, (cn, e1, e2) in enumerate(cuts):
                n = L.cut_plane(r, c, e1, e2, w, h, steps, half=1.6); xx = pad + kk * (w + pad)
                im.paste(Image.fromarray(M.shade(n, steps)), (xx, yy)); d.text((xx + 3, yy + 2), sn.split(',')[0] + ', ' + cn, fill=(150, 160, 175), font=M.font(11))
        p = os.path.join(HERE, 'power3-%s.png' % ('ci' if c[0] == 0 else 'c2')); im.save(p); print('wrote', p)
