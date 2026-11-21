"""Small checks behind sentences in the report. python out/r15/study/final_checks.py"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
D = os.path.join(HERE, 'data')
rng = np.random.default_rng(2)
# 1. the upright plane y = 0: one step without c keeps it, and lands on the half x >= 0
for key in (Fp.REF, ('J', 1.0, 2), ('J', 1.3, 2), ('E', 1.0, 3, 0.5)):
    x = rng.normal(size=200000); z = rng.normal(size=200000); y = np.zeros(200000)
    ox, oy, oz = vox.step(x, y, z, key)
    r2 = x * x + z * z
    ang = np.degrees(np.arctan2(oz, ox)); cov = np.unique(np.floor(ang).astype(int)).size
    print(key, 'directions in the plane y = 0 land on %d of 360 one-degree steps of the circle (from %.0f to %.0f degrees up from the +x axis)' % (cov, ang.min(), ang.max()))
    print(key, 'plane y = 0 after one step: largest |y| / length %.1e; smallest x / length %.3e; share with x < 0: %.5f' % (np.abs(oy / r2 ** (Fp.get_lay(key).n / 2)).max(), (ox / r2 ** (Fp.get_lay(key).n / 2)).min(), (ox < 0).mean()))
# 2. the rabbit's cut at z = 0 from the 321 box against the flat rabbit
d = np.load(os.path.join(D, 'rab-box-321.npy'))[:, :, 160]
a = np.linspace(-1.5, 1.5, 321); X, Y = np.meshgrid(a, a, indexing='ij')
zc = X + 1j * Y; ins = np.ones(zc.shape, bool)
with np.errstate(all='ignore'):
    for _ in range(60):
        zc = np.where(ins, zc * zc + complex(-0.12, 0.74), zc); ins &= (zc.real ** 2 + zc.imag ** 2) <= 4
print('rabbit cut z = 0 (321 x 321, 60 steps) against the flat rabbit: %d points differ, inside %d' % (((d == 0) != ins).sum(), ins.sum()))
d = np.load(os.path.join(D, 'q1-z0.npy'))[:, :, 0]
a = np.linspace(-1.75, 1.75, 1401); b = np.linspace(-1.0, 1.0, 801); X, Y = np.meshgrid(a, b, indexing='ij')
zc = X + 1j * Y; ins = np.ones(zc.shape, bool)
with np.errstate(all='ignore'):
    for _ in range(80):
        zc = np.where(ins, zc * zc - 1, zc); ins &= (zc.real ** 2 + zc.imag ** 2) <= 4
print('c = -1 cut z = 0 (1401 x 801, 80 steps) against the flat set: %d points differ, inside %d' % (((d == 0) != ins).sum(), ins.sum()))
# 3. how much of the 321 solids is loose specks, and above / below the plane
for nm, L in (('q1-box-321.npy', 1.7), ('rab-box-321.npy', 1.5)):
    v = np.load(os.path.join(D, nm)) == 0; h = 2 * L / 320
    print(nm, 'volume above the plane %.4f, below %.4f' % (v[:, :, 161:].sum() * h ** 3, v[:, :, :160].sum() * h ** 3))
