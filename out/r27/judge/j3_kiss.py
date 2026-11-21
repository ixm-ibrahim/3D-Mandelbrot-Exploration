"""Judge, check 3: kiss or pinch? Of a small circle round the point where the middle body meets its left neighbour,
how many of its 360 degrees lie outside, at five sizes of the circle.
A pinch keeps its share at every size. A kiss loses it in step with the size (or faster)."""
import numpy as np
import jlib as J

n = 72000; a = (np.arange(n) + 0.5) * 2 * np.pi / n
radii = (0.1, 0.03, 0.01, 0.003, 0.001)


def degs(inside):
    return 360.0 * (~inside).mean()


print('radius of the circle:            ' + '   '.join('%7.3f' % r for r in radii))
al = (1 - np.sqrt(5)) / 2
row = [degs(J.truth(al + r * np.cos(a), r * np.sin(a), -1.0, 2000)) for r in radii]
print('true flat picture, c = -1:       ' + '   '.join('%7.2f' % v for v in row))
for r in radii[:3]:
    pass
row = []
for r in radii:
    steps = int(min(max(3000, 30.0 / (r * r)), 400000))
    row.append(degs(J.truth(-0.5 + r * np.cos(a[::8]), r * np.sin(a[::8]), -0.75, steps)))
print('true flat picture, c = -0.75:    ' + '   '.join('%7.3f' % v for v in row) + '   (steps grow as the circle shrinks; the last two may still call slow points inside)')
for t in (1.4, 1.0, 2.5):
    row = [degs(J.balls(-0.525 + r * np.cos(a), r * np.sin(a), 0 * a, t=t, grid='line', rounds=200) == 1) for r in radii]
    und = [int((J.balls(-0.525 + r * np.cos(a), r * np.sin(a), 0 * a, t=t, grid='line', rounds=200) == 0).sum()) for r in radii]
    print('balls object, flat cut, t = %.1f: ' % t + '   '.join('%7.2f' % v for v in row) + '   (undecided points: %s)' % und)
# the same in space for the balls object: share of a small SPHERE round the kissing point that is outside
rng = np.random.default_rng(5); d = rng.normal(size=(200000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
row = [100.0 * (J.balls(-0.525 + r * d[:, 0], r * d[:, 1], r * d[:, 2], rounds=200) != 1).mean() for r in radii]
print('balls object in space (square grid), share of a small sphere round the kissing point that is outside, of 100: ' + '   '.join('%6.2f' % v for v in row))
