"""Judge, re-measurement 6: loose ends (pulled plane and along once on the rabbit; the hinged pages; San Marco rings).  -> j6_extra.txt"""
import os, sys, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j6_extra.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); H = L.design('alonghinge'); C = L.RABBIT
say('== A. the rabbit under the clean rules (96^3 grid, 80 and 300 steps)')
n = 96
GX, GY, GZ = np.meshgrid(np.linspace(-1.8, 1.8, n), np.linspace(-1.5, 1.5, n), np.linspace(-1.5, 1.5, n), indexing='ij')
ins = {}
for name in ('oneplane', 'pulled', 'once', 'along'):
    st = M.stay(R[name], GX, GY, GZ, *C, 300); ins[name] = st >= 80
    fat = ndimage.binary_dilation(ins[name], structure=np.ones((3, 3, 3), bool)); lab, k = ndimage.label(fat, structure=np.ones((3, 3, 3), bool))
    cnt = np.bincount((lab * ins[name]).ravel())[1:]
    say('%-9s inside at 80 steps %6d, at 300 steps %6d | pieces with gaps of two cells bridged: %d (%s %%) | highest block %.2f'
        % (name, ins[name].sum(), (st >= 300).sum(), k, ' / '.join('%.1f' % (100 * t / ins[name].sum()) for t in sorted(cnt, reverse=True)[:3]), np.abs(GZ[ins[name]]).max()))
for name in ('pulled', 'once', 'along'):
    say('%-9s: %.1f %% of it is also in one plane\'s rabbit; %.1f %% of one plane\'s rabbit is in it' % (name, 100 * (ins[name] & ins['oneplane']).sum() / ins[name].sum(), 100 * (ins[name] & ins['oneplane']).sum() / ins['oneplane'].sum()))

say('\n== B. the hinged rule: does a page through the hinge last? 20,000 points of the upright page through the hinge')
c = complex(C[0], C[1]); alpha = (1 - np.sqrt(1 - 4 * c)) / 2; e = alpha / abs(alpha)
rng = np.random.default_rng(1); s = rng.uniform(-0.8, 0.8, 20000); h = rng.uniform(-0.8, 0.8, 20000)
p = (s * e.real, s * e.imag, h)


def off_plane(P, a0, b0):
    """Distance of points from the upright plane through the flat-page points a0 and b0."""
    dirn = (b0 - a0) / abs(b0 - a0); nx, ny = -dirn.imag, dirn.real
    return np.abs((P[0] - a0.real) * nx + (P[1] - a0.imag) * ny)


p1 = L.one(H, *p, C); say('after one step: farthest from the upright plane through c and the meeting point: %.1e' % off_plane(p1, c, alpha).max())
cx, cy, cz = (np.full(20000, t) for t in C)
X, Y, Z, _ = H.step(*p1, (), 1, cx, cy, cz); p2 = (X + C[0], Y + C[1], Z + C[2])
say('after two steps: distance from the upright plane through c^2 + c and the meeting point: median %.2f, smallest %.1e' % (np.median(off_plane(p2, c * c + c, alpha)), off_plane(p2, c * c + c, alpha).min()))
pa = (s, 0 * s, h)                                           # the same for along and c = -1: the upright page through the x-axis
q = pa
for k in range(4):
    q = L.one(R['along'], *q, L.BAS)
say('along, c = -1, the upright page through the x-axis after four steps: farthest from that page %.1e' % np.nanmax(np.abs(q[1])))

say('\n== C. San Marco (c = -0.75): the ring census on rings through four bud middles (2,880 places, 80 and 300 steps)')
cm = (-0.75, 0.0, 0.0)
# bud middles of the flat San Marco picture do not exist as preimages of 0 (the middle is a neutral point), so rings of the buds section are used
for x0, rad in ((0.0, 0.70), (-0.90, 0.33), (0.35, 0.46), (1.08, 0.2)):
    x, y, z, deg = L.ring(x0, rad, 2880)
    row = []
    for name in ('oneplane', 'along', 'once', 'pulled', 'lathe'):
        a = L.arcs(M.stay(R[name], x, y, z, *cm, 300) >= 300)
        row.append('%s %d' % (name, len(a)))
    say('ring x = %5.2f, radius %.2f: arcs: %s' % (x0, rad, ', '.join(row)))
say('done %.0f s' % (time.time() - t0))
