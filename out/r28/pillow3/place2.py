"""Round 28, pillow3: where the buds sit, second and better measure (place.py used the first exit of each line of
sight, which misses every bud that hangs on by a single point; its log is kept as place-firstexit.log).

From the centre of a body, lines of sight in every direction: mu = angle from +x (the row), th = angle round the row
(0 = up in the flat picture, 90 = off the flat picture). hull(mu, th) = the LAST place within `reach` where the line
is inside. A bud is a bump of the hull over the body's own skin (grey opening, window 40 degrees). Listed: bumps
higher than 8 % of the body's half width R, between 30 and 150 degrees from the row (nearer the row than that the
line of sight runs into the next big body). Widths at half height, in units of R.

    python out/r28/pillow3/place2.py > out/r28/pillow3/place.log
"""
import os, sys
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import place as P
MU, TH, DMU, DTH, DR = P.MU, P.TH, P.DMU, P.DTH, P.DR


def hull(fn, centre, reach):
    mu, th = np.meshgrid(MU, TH, indexing='ij'); d = np.stack([np.cos(mu), np.sin(mu) * np.cos(th), np.sin(mu) * np.sin(th)]); out = np.zeros(mu.shape)
    for r in np.arange(DR, reach, DR):
        ins = fn(centre[0] + r * d[0].ravel(), centre[1] + r * d[1].ravel(), centre[2] + r * d[2].ravel()).reshape(mu.shape); out = np.where(ins, r, out)
    return out


def report(name, fn, centre, R, reach=1.8, floor=0.08, top=8):
    hl = hull(fn, centre, reach * R); w = (int(round(40 / DMU)) | 1, int(round(40 / DTH)) | 1)
    base = ndi.grey_opening(hl, size=w, mode=('nearest', 'wrap')); hgt = (hl - base) / R
    band = (np.degrees(MU) > 30) & (np.degrees(MU) < 150); hb = np.where(band[:, None], hgt, 0.0)
    wrapd = np.concatenate([hb, hb[:, :8]], 1); lab, n = ndi.label(wrapd > floor); out = []
    for i in range(1, n + 1):
        m = lab == i; j = np.argmax(np.where(m, wrapd, -1)); a, b = np.unravel_index(j, wrapd.shape)
        if b >= hb.shape[1] or (m[:, 0].any() and b < 8 and (lab[:, hb.shape[1]:] == i).any() is False):
            continue
        half = m & (wrapd > 0.5 * wrapd[a, b]); rr = hl[a, b % hb.shape[1]] - 0.5 * wrapd[a, b] * R
        out.append((np.degrees(MU[a]), np.degrees(TH[b % hb.shape[1]]), wrapd[a, b], half[:, b].sum() * np.radians(DMU) * rr / R, half[a, :].sum() * np.radians(DTH) * rr * np.sin(MU[a]) / R))
    seen = {};
    for t in sorted(out, key=lambda t: -t[2]):
        seen.setdefault((round(t[0], 1), round(t[1], 1)), t)
    out = list(seen.values()); body = np.median(base[band]) / R
    print('%s: skin of the body at %.2f R (median); buds 30..150 degrees from the row: higher than 0.25 R: %d, 0.12..0.25 R: %d, 0.08..0.12 R: %d'
          % (name, body, sum(t[2] >= 0.25 for t in out), sum(0.12 <= t[2] < 0.25 for t in out), sum(t[2] < 0.12 for t in out)))
    for t in out[:top]:
        print('     %5.1f from +x, %5.1f round the row: height %.2f R, widths %.2f x %.2f R (long : thick %.1f)' % (*t, max(t[2], t[3], t[4]) / max(min(t[2], t[3], t[4]), 1e-9)))
    return out


if __name__ == '__main__':
    fb = P.balls_fn('gauss'); fa = P.grid_fn('m1')[0]; fB = P.grid_fn('m1-lean50')[0]; k2 = P.tree.K2; rn = k2 / (2 * P.tree.T0 - 1) / 2
    print('--- the middle body')
    report('Balls on balls, square grid', fb, (0, 0, 0), k2 / 2); report('pillow3 layout A, c = -1', fa, (0, 0, 0), 0.618); report('pillow3 layout B, c = -1', fB, (0, 0, 0), 0.618)
    print('--- the right neighbour')
    report('Balls on balls, square grid', fb, (k2 / 2 + rn, 0, 0), rn); report('pillow3 layout A', fa, (0.945, 0, 0), 0.327); report('pillow3 layout B', fB, (0.945, 0, 0), 0.327)
    print('--- the left neighbour')
    report('Balls on balls, square grid', fb, (-k2 / 2 - rn, 0, 0), rn); report('pillow3 layout A', fa, (-0.945, 0, 0), 0.327); report('pillow3 layout B', fB, (-0.945, 0, 0), 0.327)
