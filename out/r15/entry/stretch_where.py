"""Round 15, entry: where on the sphere of directions is the rule's stretch smallest and largest (power 2)?
Stretch in three steps of 1e-5 round each of 300,000 directions (out/r15/entry/ref_n.py, the reference rule):
smallest and largest of the two sideways stretches, and where the extreme ones lie: the angle from the nearest
corner point (+-0.8, 0, +-0.6), from the plane y = 0 (the seams lie in it), from the plane z = 0."""
import sys, numpy as np
sys.path.insert(0, 'out/r15/entry')
import ref_n as R
rng = np.random.default_rng(11)
N = 300000
d = rng.normal(size=(N, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
# two tangent directions
a = np.cross(d, np.array([0.3, 0.5, 0.81])); a /= np.linalg.norm(a, axis=1)[:, None]
b = np.cross(d, a)
h = 1e-5
f0 = R.F(d, 2)
def moved(t):
    p = d + h * t; p /= np.linalg.norm(p, axis=1)[:, None]
    return (R.F(p, 2) - f0) / h
ja, jb = moved(a), moved(b)
# singular values of the 3x2 matrix [ja jb]
E = (ja * ja).sum(1); G = (jb * jb).sum(1); Fm = (ja * jb).sum(1)
tr = E + G; det = E * G - Fm * Fm
s1 = np.sqrt((tr + np.sqrt(np.maximum(tr * tr - 4 * det, 0))) / 2); s2 = np.sqrt(np.maximum((tr - np.sqrt(np.maximum(tr * tr - 4 * det, 0))) / 2, 0))
corners = np.array([[0.8, 0, 0.6], [0.8, 0, -0.6], [-0.8, 0, 0.6], [-0.8, 0, -0.6]])
angc = np.degrees(np.arccos(np.clip((d @ corners.T).max(1), -1, 1)))
angy = np.degrees(np.arcsin(np.abs(d[:, 1]))); angz = np.degrees(np.arcsin(np.abs(d[:, 2])))
print('smaller stretch: median %.2f, 1%% %.3f, 0.1%% %.4f, least %.5f;  larger stretch: median %.2f, 99%% %.2f, 99.9%% %.2f, most %.1f' % (np.median(s2), np.quantile(s2, .01), np.quantile(s2, .001), s2.min(), np.median(s1), np.quantile(s1, .99), np.quantile(s1, .999), s1.max()))
print('ratio larger / smaller: median %.2f, 90%% %.1f, 99%% %.1f; share of directions with ratio under 1.1: %.1f %%, under 1.5: %.1f %%, over 3: %.1f %%, over 10: %.1f %%' % (np.median(s1 / np.maximum(s2, 1e-12)), np.quantile(s1 / np.maximum(s2, 1e-12), .9), np.quantile(s1 / np.maximum(s2, 1e-12), .99), 100 * (s1 / np.maximum(s2, 1e-12) < 1.1).mean(), 100 * (s1 / np.maximum(s2, 1e-12) < 1.5).mean(), 100 * (s1 / np.maximum(s2, 1e-12) > 3).mean(), 100 * (s1 / np.maximum(s2, 1e-12) > 10).mean()))
lo = np.argsort(s2)[:300]; hi = np.argsort(-s1)[:300]
for name, k in (('the 300 directions with the least stretch', lo), ('the 300 directions with the most stretch', hi)):
    print('%s: angle from the nearest corner point median %.1f deg (largest %.1f); from the plane y = 0 median %.2f deg (largest %.1f); from the plane z = 0 median %.1f deg; north %d, south %d' % (name, np.median(angc[k]), angc[k].max(), np.median(angy[k]), angy[k].max(), np.median(angz[k]), int((d[k, 2] > 0).sum()), int((d[k, 2] < 0).sum())))
# by distance from the plane z = 0: the ratio in bands
for lo_, hi_ in ((0, 5), (5, 15), (15, 30), (30, 50), (50, 90)):
    m = (angz >= lo_) & (angz < hi_)
    for half, mm in (('north', m & (d[:, 2] > 0)), ('south', m & (d[:, 2] < 0))):
        print('  %s, %2d to %2d degrees from the plane z = 0: stretch ratio median %.2f, smaller stretch median %.2f, larger %.2f' % (half, lo_, hi_, np.median(s1[mm] / np.maximum(s2[mm], 1e-12)), np.median(s2[mm]), np.median(s1[mm])))
