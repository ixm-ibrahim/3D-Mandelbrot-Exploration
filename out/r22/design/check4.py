"""Does every surface that one step lays onto the flat page carry a whole copy of the flat picture? (light run)
python out/r22/design/check4.py > out/r22/design/check4.txt"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
R = L.refs()
w, h = 360, 260
u, s = np.meshgrid(np.linspace(-1.8, 1.8, w), np.linspace(1.3, -1.3, h))

print('A. preturn: the upright page (y = 0). One step lays it onto the flat page, so it should show the flat picture (its lower half, twice).')
for cn, c in (('basilica', L.BAS), ('rabbit', L.RAB), ('Siegel', M.SIEGEL)):
    cut = M.stay(D.get('preturn'), u, 0 * u, s, c[0], c[1], c[2], 120) >= 120
    flat = M.flat_stay(u, -np.abs(s), c[0], c[1], 300) >= 300
    print('   %-9s inside the cut %d, inside the flat picture laid there %d, differ %d' % (cn, cut.sum(), flat.sum(), (cut != flat).sum()))

print('B. capfold45: the cone of height angle 70.53 degrees (mirrored exactly onto the page). Should show the flat picture wrapped round the cone.')
Lg = np.degrees(np.arcsin(2 * np.sqrt(2) / 3))        # t = e^2, e = tan(22.5 deg)  ->  sin L = (1 - e^4) / (1 + e^4) = 0.9428
print('   height angle of the cone %.3f degrees' % Lg)
rr, th = np.meshgrid(np.linspace(0.02, 1.7, 300), np.linspace(-np.pi, np.pi, 720, endpoint=False)); cl, sl = np.cos(np.radians(Lg)), np.sin(np.radians(Lg))
for cn, c in (('basilica', L.BAS), ('rabbit', L.RAB)):
    for sgn in (1.0, -1.0):
        cut = M.stay(D.get('capfold45'), rr * cl * np.cos(th), rr * cl * np.sin(th), sgn * rr * sl, c[0], c[1], c[2], 120) >= 120
        flat = M.flat_stay(rr * np.cos(th), rr * np.sin(th), c[0], c[1], 300) >= 300
        print('   %-9s %s cone: inside %d, inside the flat picture wrapped %d, differ %d' % (cn, 'upper' if sgn > 0 else 'lower', cut.sum(), flat.sum(), (cut != flat).sum()))

print('C. along, basilica: the upright page (kept, not laid down): differ from the flat picture stood upright')
cut = M.stay(R['along'], u, 0 * u, s, -1.0, 0.0, 0.0, 120) >= 120; flat = M.flat_stay(u, s, -1.0, 0.0, 300) >= 300
print('   differ %d of %d' % ((cut != flat).sum(), flat.sum()))

print('D. How many places does one squaring send onto one spot? (direction grid 1440 x 1439, targets: 3 directions in the page, 2 off it; places = separate clusters of grid cells whose image is within 0.4 degrees)')
from scipy import ndimage
th = np.linspace(-np.pi, np.pi, 1440, endpoint=False); la = np.linspace(-np.pi / 2 + 0.001, np.pi / 2 - 0.001, 1439)
TH, LA = np.meshgrid(th, la); gx, gy, gz = np.cos(LA) * np.cos(TH), np.cos(LA) * np.sin(TH), np.sin(LA)
tg = [(100.0, 0.0), (20.0, 0.0), (-150.0, 0.0), (60.0, 30.0), (-110.0, 55.0)]
for nm in ['oneplane', 'lathe', 'along', 'away'] + [r.name for r in D.RULES]:
    r = R[nm] if nm in R else D.get(nm)
    X, Y, Z = L.one(r, gx.ravel(), gy.ravel(), gz.ravel(), L.RAB); n = np.sqrt(X * X + Y * Y + Z * Z); X, Y, Z = X / n, Y / n, Z / n
    out = []
    for lo, lat in tg:
        t = np.array([np.cos(np.radians(lat)) * np.cos(np.radians(lo)), np.cos(np.radians(lat)) * np.sin(np.radians(lo)), np.sin(np.radians(lat))])
        near = ((X * t[0] + Y * t[1] + Z * t[2]) > np.cos(np.radians(0.4))).reshape(gz.shape)
        near = np.concatenate([near, near[:, :40]], axis=1)                      # wrap round in longitude
        lab, nl = ndimage.label(ndimage.binary_dilation(near, iterations=3))
        ids = set(np.unique(lab[:, :1440])) - {0}; dup = set(np.unique(lab[:, 1440:])) - {0}
        out.append(len(ids | dup) - len(ids & dup) if False else len(ids))
    print('   %-12s' % nm, ' '.join('%3d' % t for t in out), '   (rabbit c for the rules that look at c)')
