"""Way (a): how the opening of the pointed seed changes the flat cut, for the three fits.  -> step_a_scan.log"""
import numpy as np
import pinchlib as PL, fam

for key, c in PL.CS.items():
    al, be = PL.fixed_points(c); T = PL.true_flat(c)
    for kind in ('pin', 'osc', 'affine'):
        mv, _ = PL.fitted(c, 1, kind); out = []
        for th in (40, 50, 55, 60, 65, 70, 75, 80, 90):
            B, bad = fam.orbit(mv, ('spin', al, -al, 0j, np.radians(th)), rmin=0.005, cap=40000)
            A = PL.flat_union(B); ov, nk = fam.overlap_share(B, top=300)
            out.append('%d: %.1f%% (ov %.0f%%)' % (th, 100 * PL.wrong_share(A, T), 100 * ov))
        print(PL.NAMES[key], kind, '| half opening: wrong share (overlap) |', ' ; '.join(out))
