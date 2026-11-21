"""t6: what are along's thin fins? python out/r22/stability/t6_fins.py > t6_fins.txt   (also writes own-fins.png, not for the user)
(1) Check of a formula (reasoned, then measured): beside a DIAGONAL page the step stretches the distance off the page by
    2 (2x - r) and distances in the page by 2r, so off / in = 2 cos(t) - 1, t = the direction of the point seen from 0,
    counted from the +x axis. Beside the flat and the upright page: off / in = 1.
(2) Zoomed cuts across the x-axis with the zones behind.
(3) Thin things on circles round the x-axis (arcs under 1 degree wide): follow their middles step by step and print
    how far (degrees) each orbit point is from the nearest of the four pages, which kind (F = flat/upright, D = diagonal),
    whether it is left or right of 0, and the running squeeze (longest / shortest stretch of all the steps so far)."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import stab as T, zones as Z
M = T.M
C = T.BAS; STEPS = 200; F = T.rule('along'); R = M.bench('along')

print('== (1) stretch off a page against stretch in the page, along')
for page in (45.0, 0.0, 90.0):
    a = np.radians(page); e_in = np.array([0, np.cos(a), np.sin(a)]); e_off = np.array([0, -np.sin(a), np.cos(a)])
    for th in (10, 40, 60, 80, 90, 120, 150, 170):
        r = 0.7; p = r * np.cos(np.radians(th)) * np.array([1.0, 0, 0]) + r * np.sin(np.radians(th)) * e_in
        J = T.jac(F, *p); off = float(e_off @ J @ e_off); inn = np.linalg.norm(J @ e_in)
        print('  page %4.1f, direction from +x %3d: off-page stretch %+.4f, in-page %.4f, ratio %+.4f | formula 2cos(t)-1 = %+.4f' % (page, th, off, inn, off / inn, 2 * np.cos(np.radians(th)) - 1 if page == 45 else 1))

print('\n== (3) thin things on circles round the x-axis, basilica, along (200 steps)')
for (x1, d) in ((-1.0, 0.25), (0.0, 0.55), (-0.3, 0.52), (-1.3, 0.22), (1.0, 0.25), (0.3, 0.52)):
    ph = np.radians(np.arange(0, 90, 0.005))
    ins = M.stay(R, np.full_like(ph, x1), d * np.cos(ph), d * np.sin(ph), *C, STEPS) >= STEPS
    edges = np.flatnonzero(ins[1:] != ins[:-1]) + 1
    if ins[0]:
        edges = np.insert(edges, 0, 0)
    if len(edges) % 2:
        edges = np.append(edges, len(ins))
    arcs = [(0.005 * (s + e) / 2, 0.005 * (e - s)) for s, e in zip(edges[::2], edges[1::2])]
    print('circle x = %+.2f, distance %.2f from the axis, first quarter turn: %d pieces; widths in degrees: %s' % (x1, d, len(arcs), ' '.join('%.1f:%.3f' % a for a in arcs)))
    for mid, wdt in arcs:
        a = np.radians(mid); q = (np.array([x1]), np.array([d * np.cos(a)]), np.array([d * np.sin(a)]))
        oj = T.orbit_jac(F, *q, C, 8); line = []
        dv, kd = T.turn_from_pages(q[1], q[2]); line.append('start %s%.2f' % ('FD'[int(kd[0])], dv[0]))
        for (pt, A) in oj:
            dv, kd = T.turn_from_pages(pt[1], pt[2]); s = np.linalg.svd(A[0], compute_uv=False); rho = float(np.hypot(pt[1][0], pt[2][0]))
            line.append('%s%s%.2f(d%.2f,q%.0f%s)' % ('L' if pt[0][0] < 0 else 'R', 'FD'[int(kd[0])], dv[0], rho, s[0] / max(s[2], 1e-300), '-' if np.linalg.det(A[0]) < 0 else '+'))
        print('   piece at %6.2f, %.3f wide: %s' % (mid, wdt, '  '.join(line)))

print('\n== (2) zoomed cuts')
t0 = time.time(); W = 640; pad = 8
tiles = [('across x = 0 (middle body)', ('across', 0.0), 0.85, (0, 0)), ('across x = -1.047 (buds of the left body)', ('across', -1.047), 0.5, (0, 0)),
         ('across x = -0.3', ('across', -0.3), 0.7, (0, 0)), ('across x = -1.3', ('across', -1.3), 0.4, (0, 0))]
im = Image.new('RGB', (pad + len(tiles) * (W + pad), 2 * (W + 30) + 10), (12, 14, 20)); d = ImageDraw.Draw(im)
for row, nm in enumerate(('along', 'oneplane')):
    for j, (lab, kind, L, _) in enumerate(tiles):
        img, cat, ins = Z.tile(nm, kind, C, W, L, 120)
        im.paste(Image.fromarray(img), (pad + j * (W + pad), 26 + row * (W + 30))); d.text((pad + j * (W + pad), 6 + row * (W + 30)), '%s, %s, half-width %.2f' % (nm, lab, L), fill=(200, 205, 215), font=M.font(15))
        n = max(int(ins.sum()), 1)
        print('%-9s %-42s inside %6d px: keeps %5.1f %%, squeezes %5.1f %%, hard %5.1f %%, inside out %5.1f %%' % (nm, lab, ins.sum(), *(100 * ((cat == k) & ins).sum() / n for k in range(4))))
out = os.path.join(T.HERE, 'own-fins.png'); im.save(out); print(out, im.size, '%.0f s' % (time.time() - t0))
