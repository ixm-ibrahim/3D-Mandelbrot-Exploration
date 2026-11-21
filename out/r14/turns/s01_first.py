# First rough look + checks of the machinery. Run from the project root: python out/r14/turns/s01_first.py
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from turns import *

OUT = os.path.join(HERE, 'first'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1)

# ---- check 0: the closed form E1 against the line-for-line copy of MATH.mercator
p = rng.uniform(-2, 2, (200000, 3))
a = np.stack(E1(p[:, 0], p[:, 1], p[:, 2]), 1); b = np.stack(E1_trig(p[:, 0], p[:, 1], p[:, 2]), 1)
print('E1 closed form vs MATH.mercator copy: largest difference', float(np.abs(a - b).max()))
# ---- check 0b: K1 keeps the length rule and the unit sphere; equator vs angle doubling
k = np.stack(K1(p[:, 0], p[:, 1], p[:, 2]), 1)
print('K1: largest | |K1 p| - |p|^2 |', float(np.abs(np.linalg.norm(k, axis=1) - (p ** 2).sum(1)).max()))
t = np.linspace(0, 2 * np.pi, 7201)[:-1]
kx, ky, kz = K1(np.cos(t), np.sin(t), 0 * t)
dev = np.degrees(np.angle(np.exp(1j * (np.arctan2(ky, kx) - 2 * t))))
print('K1 on the equator vs angle doubling: largest difference %.2f degrees at longitude %.1f; z stays 0: %s'
      % (np.abs(dev).max(), np.degrees(t[np.abs(dev).argmax()]), bool(np.abs(kz).max() < 1e-12)))
# K1 continuity across cap rims: sample pairs of close points
q = rng.normal(size=(400000, 3)); q /= np.linalg.norm(q, axis=1)[:, None]
q2 = q + 1e-6 * rng.normal(size=q.shape); q2 /= np.linalg.norm(q2, axis=1)[:, None]
ka = np.stack(K1(q[:, 0], q[:, 1], q[:, 2]), 1); kb = np.stack(K1(q2[:, 0], q2[:, 1], q2[:, 2]), 1)
st = np.linalg.norm(ka - kb, axis=1) / np.linalg.norm(q - q2, axis=1)
print('K1 stretch on the sphere: min %.3f median %.3f max %.3f (a jump would show as a huge max)' % (st.min(), np.median(st), st.max()))
ea = np.stack(E1(q[:, 0], q[:, 1], q[:, 2]), 1); eb = np.stack(E1(q2[:, 0], q2[:, 1], q2[:, 2]), 1)
st = np.linalg.norm(ea - eb, axis=1) / np.linalg.norm(q - q2, axis=1)
print('E1 stretch on the sphere: min %.3f median %.3f max %.3f' % (st.min(), np.median(st), st.max()))

N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
c = (-1.0, 0.0, 0.0)
res = {}
# ---- check 1: one rule only (E1): must be the lab's "Sphere inversions, one plane" solid; slice z = 0 = flat set
vol, death, info = julia(c, [E1], 'union', N=N)
fj = flat_julia(c[0], c[1], N, 1.7)
sl = vol[:, :, N // 2]
print('one rule E1, slice z=0 vs flat Julia set: differing pixels', int((sl ^ fj).sum()), 'of', int(fj.sum()), 'inside')
ims = [render(vol), slice_img(vol, death, 'z', fj)]
titles = ['E, one rule only (check)', 'its cut at z = 0, flat set in red']
for pair in ('E', 'K'):
    for mode in ('union', 'common'):
        v, dth, inf = julia(c, list(RULES[pair]), mode, N=N)
        ims += [render(v), slice_img(v, dth, 'z', fj)]
        titles += [f'{pair} {mode}', f'{pair} {mode}: cut at z = 0']
rows = [ims[0:2] + [None, None], ims[2:6], ims[6:10]]
sheet(rows, ['solid', 'cut z = 0 (flat set in red)', 'solid', 'cut z = 0 (flat set in red)'],
      ['one rule E', 'E: union | common', 'K: union | common'], os.path.join(OUT, f'first-N{N}.png'),
      title=f'First look, c = -1, grid {N}')
print('wrote', os.path.join(OUT, f'first-N{N}.png'))
