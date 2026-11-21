"""Does the flat picture have BODY? A formula, checked against the measurement.

A rule 'the sheet turns by h(d) before the squaring' with slope kappa = h'(0) (lag: kappa = the share; one-plane: 0;
lathe: 1; mirror: -1; over: 2). Take an attracting cycle of the flat picture, lift the point by a small height eta and
tilt the carried sheet by a small angle a. One step at the cycle point x + iy (r = its length) does, to first order,

    a'   = (1 - kappa) * a + kappa * eta / y          (the sheet moves toward the point's own sheet)
    eta' = 2 r eta - 2 (r - x) y a'                   (the one-plane square about the tilted sheet)

The flat picture has body at c exactly when the product of these 2x2 matrices round the cycle shrinks (largest
eigenvalue below 1 in size).  (Reasoned; this script checks it.)

    python out/r21/sheet/stab.py      -> explain-stab.png and numbers
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M


def predicted(cr, ci, kappa, pmax=24, warm=3000):
    """Largest eigenvalue (size) of the lift-and-tilt matrix round the attracting cycle of each c; nan where none is found."""
    z = np.zeros(cr.shape, complex); c = cr + 1j * ci
    with np.errstate(all='ignore'):
        for _ in range(warm):
            z = z * z + c
        ok = np.isfinite(z) & (np.abs(z) < 4); z = np.where(ok, z, 0)
        per = np.zeros(cr.shape, int); w = z.copy()
        for p in range(1, pmax + 1):
            w = w * w + c
            per = np.where((per == 0) & ok & (np.abs(w - z) < 1e-7), p, per)
        m11, m12, m21, m22 = np.ones(cr.shape), np.zeros(cr.shape), np.zeros(cr.shape), np.ones(cr.shape); w = z.copy()
        for p in range(pmax):
            act = per > p; x, y, r = w.real, w.imag, np.abs(w); ys = np.where(np.abs(y) < 1e-12, 1e-12, y)
            a11, a12, a21, a22 = 2 * r - 2 * (r - x) * kappa, -2 * (r - x) * ys * (1 - kappa), kappa / ys, (1 - kappa) + 0 * r
            n11, n12, n21, n22 = a11 * m11 + a12 * m21, a11 * m12 + a12 * m22, a21 * m11 + a22 * m21, a21 * m12 + a22 * m22
            m11, m12, m21, m22 = (np.where(act, n, m) for n, m in ((n11, m11), (n12, m12), (n21, m21), (n22, m22)))
            w = np.where(act, w * w + c, w)
        tr, det = m11 + m22, m11 * m22 - m12 * m21; disc = (tr * tr - 4 * det).astype(complex)
        lam = np.maximum(np.abs((tr + np.sqrt(disc)) / 2), np.abs((tr - np.sqrt(disc)) / 2))
    return np.where(per > 0, lam, np.nan)


def main():
    w, h, steps, lift = 250, 232, 300, 1e-6; pad = 8
    u, v = np.meshgrid(np.linspace(-2.1, 0.7, w), np.linspace(1.3, -1.3, h)); flat = M.flat_stay(u, v, u, v, steps) >= steps
    cases = [('lag 0.25', 0.25, R.lam_rule('l', '', lambda d, x, y, z, k: 0.25)), ('lag 0.50', 0.5, R.lam_rule('l', '', lambda d, x, y, z, k: 0.5)),
             ('lag 0.67', 2 / 3., R.lam_rule('l', '', lambda d, x, y, z, k: 2 / 3.)), ('mirror (slope -1)', -1.0, R.get('mirror')), ('over (slope 2)', 2.0, R.get('over'))]
    W = pad + len(cases) * (w + pad); H = 66 + 2 * (h + 30)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Where the flat Mandelbrot set has no body: the formula (top) and the measurement (bottom: lifted a millionth, %d steps)' % steps, fill=(240, 240, 245), font=M.font(17))
    d.text((pad, 36), 'cream: has body.  red: only a film.  grey (top row only): no cycle found, no forecast', fill=(200, 200, 205), font=M.font(14))
    for i, (nm, kap, rule) in enumerate(cases):
        lam = predicted(u, v, kap); k = M.mandel(rule, u, v, np.full_like(u, lift), steps) >= steps
        pred = np.zeros((h, w, 3), np.uint8); pred[...] = (22, 28, 46); pred[flat] = (110, 110, 118); pred[flat & (lam < 1)] = (238, 228, 200); pred[flat & (lam >= 1)] = (214, 60, 50)
        meas = np.zeros((h, w, 3), np.uint8); meas[...] = (22, 28, 46); meas[flat & k] = (238, 228, 200); meas[flat & ~k] = (214, 60, 50)
        known = flat & np.isfinite(lam); agree = ((lam >= 1) == (~k))[known].mean()
        x = pad + i * (w + pad)
        d.text((x, 66), '%s: formula' % nm, fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(pred), (x, 88))
        d.text((x, 66 + h + 30), 'measured (agree on %.1f%%)' % (100 * agree), fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(meas), (x, 88 + h + 30))
        lost = known & ~k
        print('%-18s formula: lifted cycle unstable on %.1f%% of the set; measured lost %.1f%%; agree on %.1f%% of %d places; of the places measured lost, the formula flags %.1f%%'
              % (nm, 100 * (flat & (lam >= 1)).sum() / flat.sum(), 100 * (flat & ~k).sum() / flat.sum(), 100 * agree, known.sum(), 100 * (lam[lost] >= 1).mean() if lost.any() else float('nan')))
        sys.stdout.flush()
    im.save(os.path.join(HERE, 'explain-stab.png'))


if __name__ == '__main__':
    main()
