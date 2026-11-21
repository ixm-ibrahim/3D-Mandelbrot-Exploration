"""Judge, re-measurement 3: the fine print of one step (stability section).  -> j3_stab.txt"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j3_stab.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules()
Z0 = (0.0, 0.0, 0.0)


def sq(rule, p):
    """One squaring WITHOUT c of the rows of p (fresh orbits)."""
    X, Y, Z = L.one(rule, p[:, 0], p[:, 1], p[:, 2], Z0)
    return np.stack([X, Y, Z], 1)


def jac(rule, p, e=1e-6):
    Jm = np.zeros((len(p), 3, 3))
    for j in range(3):
        d = np.zeros(3); d[j] = e
        Jm[:, :, j] = (sq(rule, p + d) - sq(rule, p - d)) / (2 * e)
    return Jm


rng = np.random.default_rng(7)
say('== A. one step under the glass: 200,000 random points of the cube -1.5..1.5')
P = rng.uniform(-1.5, 1.5, size=(200000, 3))
for name in ('oneplane', 'along', 'lathe'):
    Jm = jac(R[name], P); det = np.linalg.det(Jm); sv = np.linalg.svd(Jm, compute_uv=False); ratio = sv[:, 0] / np.maximum(sv[:, 2], 1e-300)
    ln = np.abs(np.linalg.norm(sq(R[name], P), axis=1) - (P ** 2).sum(1)).max()
    say('%-9s turned inside out %.1f %% | keeps shapes (longest/shortest stretch under 1.25, not inside out) %.1f %% | median ratio %.2f | length squared to %.0e'
        % (name, 100 * (det < 0).mean(), 100 * ((ratio < 1.25) & (det > 0)).mean(), np.median(ratio), ln))

say('\n== B. one plane: longest / shortest stretch by height angle above the flat page; formula (1 + sin^2 L) / cos L')
for Ld in (0.0, 22.5, 45.0, 67.5):
    La = np.radians(Ld); p = np.array([[0.5 * np.cos(La), 0.3 * np.cos(La), np.hypot(0.5, 0.3) * np.sin(La)]])
    sv = np.linalg.svd(jac(R['oneplane'], p)[0], compute_uv=False)
    say('height angle %4.1f: measured %.3f, formula %.3f' % (Ld, sv[0] / sv[2], (1 + np.sin(La) ** 2) / np.cos(La)))

say('\n== C. along beside its slanted page: stretch off the page / stretch in the page; formula 2 cos t - 1')
nrm = np.array([0.0, -np.sin(np.pi / 4), np.cos(np.pi / 4)])
for td in (10, 40, 60, 90, 120, 150, 170):
    t = np.radians(td); r = 0.7
    p = np.array([[r * np.cos(t), r * np.sin(t) * np.cos(np.pi / 4), r * np.sin(t) * np.sin(np.pi / 4)]])
    Jm = jac(R['along'], p)[0]
    off = nrm @ Jm @ nrm; inpage = 2 * r
    Jf = jac(R['along'], np.array([[r * np.cos(t), r * np.sin(t), 0.0]]))[0]
    say('t = %3d: slanted page %.4f (formula %.4f) | flat page %.4f' % (td, off / inpage, 2 * np.cos(t) - 1, (Jf[2, 2]) / inpage))

say('\n== D. bud shapes round the left body of the basilica (ring through the side bud, 300 steps): thick round the axis against long along x')
g1 = np.sqrt(complex(-np.sqrt(2) + 1)); g2 = -np.sqrt(1 + g1); x0, rad = g2.real, abs(g2.imag); C = L.BAS


def extent(rule, base, direction, hi=0.2, n=4001, steps=300):
    s = np.linspace(-hi, hi, n); q = base[None] + s[:, None] * direction[None]
    ins = M.stay(rule, q[:, 0], q[:, 1], q[:, 2], *C, steps) >= steps
    mid = n // 2
    if not ins[mid]:
        return 0.0
    a = mid
    while a > 0 and ins[a - 1]:
        a -= 1
    b = mid
    while b < n - 1 and ins[b + 1]:
        b += 1
    return s[b] - s[a]


for name, angs in (('along', (0.0, 26.875, 45.0, 63.125, 90.0)), ('oneplane', (0.0,)), ('once', (0.0, 26.75)), ('pulled', (0.0, 90.0))):
    for ad in angs:
        a = np.radians(ad); base = np.array([x0, rad * np.cos(a), rad * np.sin(a)])
        tang = np.array([0.0, -np.sin(a), np.cos(a)]); outw = np.array([0.0, np.cos(a), np.sin(a)]); ex = np.array([1.0, 0.0, 0.0])
        th, ln, ou = extent(R[name], base, tang), extent(R[name], base, ex), extent(R[name], base, outw)
        say('%-9s bud at %6.2f deg: round the axis %.4f, along x %.4f, outward %.4f | long : thick %.2f' % (name, ad, th, ln, ou, ln / th if th else float('nan')))

say('\n== E. the eight buds of the middle body (ring through the top bud): round the axis against along x')
rad1 = abs(g1.imag)
for name, angs in (('along', (0.0, 45.0, 90.0)), ('oneplane', (0.0,)), ('once', (0.0, 45.0, 90.0)), ('pulled', (0.0, 90.0))):
    for ad in angs:
        a = np.radians(ad); base = np.array([0.0, rad1 * np.cos(a), rad1 * np.sin(a)])
        tang = np.array([0.0, -np.sin(a), np.cos(a)]); ex = np.array([1.0, 0.0, 0.0])
        th, ln = extent(R[name], base, tang, hi=0.3), extent(R[name], base, ex, hi=0.3)
        say('%-9s bud at %5.1f deg: round the axis %.4f, along x %.4f' % (name, ad, th, ln))

say('\n== F. along against the lathe and against one plane as moves: angle between the two images of one point, seen from 0')
Q = rng.uniform(-1.5, 1.5, size=(200000, 3)); A = sq(R['along'], Q)
for other in ('lathe', 'oneplane'):
    B = sq(R[other], Q); cs = (A * B).sum(1) / np.maximum(np.linalg.norm(A, axis=1) * np.linalg.norm(B, axis=1), 1e-300)
    ang = np.degrees(np.arccos(np.clip(cs, -1, 1)))
    say('along against %-9s: largest %.1f, median %.1f degrees' % (other, ang.max(), np.median(ang)))

say('\n== G. the rabbit: the line straight above the meeting point under along; which heights are inside (300 steps)')
c = complex(*L.RABBIT[:2]); alpha = (1 - np.sqrt(1 - 4 * c)) / 2
hh = np.linspace(0.0005, 0.8, 1600)
for name in ('along', 'oneplane', 'lathe'):
    ins = M.stay(R[name], np.full(hh.size, alpha.real), np.full(hh.size, alpha.imag), hh, *L.RABBIT, 300) >= 300
    runs = []; i = 0
    while i < hh.size:
        if ins[i]:
            j = i
            while j < hh.size and ins[j]:
                j += 1
            runs.append((hh[i], hh[j - 1])); i = j
        else:
            i += 1
    say('%-9s inside %4d of 1600 heights; runs longer than 0.01: %s' % (name, ins.sum(), ' '.join('%.3f..%.3f' % t for t in runs if t[1] - t[0] > 0.01)))

say('\n== H. rabbit volumes and overlap, 300,000 random points, 100 steps')
P3 = rng.uniform([-1.8, -1.5, -1.5], [1.8, 1.5, 1.5], size=(300000, 3))
ins = {n: M.stay(R[n], P3[:, 0], P3[:, 1], P3[:, 2], *L.RABBIT, 100) >= 100 for n in ('along', 'lathe', 'oneplane')}
say('inside: along %d, lathe %d, one plane %d | of along\'s: in the lathe\'s %.1f %%, in one plane\'s %.1f %% | of one plane\'s in along\'s %.1f %%'
    % (ins['along'].sum(), ins['lathe'].sum(), ins['oneplane'].sum(), 100 * (ins['along'] & ins['lathe']).sum() / ins['along'].sum(),
       100 * (ins['along'] & ins['oneplane']).sum() / ins['along'].sum(), 100 * (ins['along'] & ins['oneplane']).sum() / ins['oneplane'].sum()))
say('done %.0f s' % (time.time() - t0))
