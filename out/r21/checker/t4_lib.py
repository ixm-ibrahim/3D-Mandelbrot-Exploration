"""t4: the library errors the skeptic and the prover report. (a) the dead zone of M.half; (b) what it does to a lag
rule (library lag against my angle-carried lag) at small lifts; (c) M.stay against my own loop that drops no orbit;
(d) M.sq_about against a turn by hand; (e) the Mandelbrot convention: start at c (k = 0) against start at 0."""
import sys
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

print('(a) M.half: the turn read back from u = (cos 2t, sin 2t)')
for t in (1e-10, 1e-9, 3e-9, 5e-9, 7e-9, 8e-9, 1e-8, 2e-8, 1e-7, 1e-6, 1e-4):
    co, si = M.half(np.cos(2 * t), np.sin(2 * t)); back = float(np.arctan2(si, co))
    co2, si2 = M.half(np.cos(2 * (np.pi / 2 - t)), np.sin(2 * (np.pi / 2 - t))); back2 = np.pi / 2 - float(np.arctan2(si2, co2))
    print('   t = %.0e: read back as %.3e (error %.1f%%); the same turn short of the upright sheet read back as %.3e' % (t, back, 100 * abs(back - t) / t, back2))
print('   M.sheet_of for a point lifted h off the page at y = 0.2: the sheet read back')
for h in (1e-10, 1e-9, 2e-9, 1e-8, 1e-7, 1e-6):
    u = M.sheet_of(np.array([0.2]), np.array([h])); co, si = M.half(*u)
    print('   h = %.0e: true turn %.3e, read back %.3e' % (h, h / 0.2, float(np.arctan2(si, co)[0])))

print('\n(b) lag25 at c = (-0.9, 0.2, lift), Mandelbrot orbit, steps stayed of 400: library | my angle-carried lag')
Llag = M.Rule('lag25', '', M.lag(0.25)); mine = ck.lag(0.25)
for lift in (0.0, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6):
    a = int(M.mandel(Llag, np.array([-0.9]), np.array([0.2]), np.array([lift]), 400)[0])
    b = int(M.mandel(mine, np.array([-0.9]), np.array([0.2]), np.array([lift]), 400)[0])
    print('   lift %.0e: %d | %d' % (lift, a, b))
print('   lost of well-inside flat Mandelbrot points, 300 steps, by lift: library lag25 | my lag25 | library delay | my delay')
for lift in (1e-12, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6):
    out = []
    for r in (Llag, mine, M.SCOUT[4], ck.delay()):
        lost, n = ck.lift_loss(r, None, lift, n=12000); out.append('%d/%d' % (lost, n))
    print('   lift %.0e: %s' % (lift, ' | '.join(out)))

print('\n(c) M.stay against my own loop (no orbit dropped): counts that differ of 4,000 (60 steps)')
rng = np.random.default_rng(1); p = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(4000, 3)); cc = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(4000, 3))
for r in M.SCOUT + [M.bench('along'), ck.evc(), ck.wake(1)]:
    out = []
    for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT)):
        a = M.stay(r, p[:, 0], p[:, 1], p[:, 2], *c, 60); b = ck.stay2(r, p[:, 0], p[:, 1], p[:, 2], *c, 60)
        out.append('%s %d' % (cn, int((a != b).sum())))
    a = M.mandel(r, cc[:, 0], cc[:, 1], cc[:, 2], 60); b = ck.stay2(r, cc[:, 0], cc[:, 1], cc[:, 2], cc[:, 0], cc[:, 1], cc[:, 2], 60)
    out.append('Mandelbrot %d' % int((a != b).sum()))
    print('   %-22s %s' % (r.name, '; '.join(out)))

print('\n(d) M.sq_about against P turned by hand (20,000 points, any turn)')
v = rng.uniform(-1.5, 1.5, size=(20000, 3)); th = rng.uniform(-np.pi, np.pi, 20000)
A = M.sq_about(v[:, 0], v[:, 1], v[:, 2], np.cos(2 * th), np.sin(2 * th)); B = ck.sq_th(v[:, 0], v[:, 1], v[:, 2], th)
print('   largest difference %.1e' % max(float(np.abs(a - b).max()) for a, b in zip(A, B)))

print('\n(e) the Mandelbrot orbit started at 0 (k = 0) against started at c (k = 0): verdicts that differ of 40,000 (60 steps); and against the lathe')
z0 = np.zeros(40000); c4 = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(40000, 3)); lat = M.mandel(M.bench('lathe'), c4[:, 0], c4[:, 1], c4[:, 2], 60) >= 60
am = ck.load('alongmem'); sh = ck.load('sheet')
for r in M.SCOUT + [am.get('c_wake1'), am.get('b_keep'), sh.get('evc005e70k16'), sh.get('ease'), sh.get('vote4')]:
    a = M.mandel(r, c4[:, 0], c4[:, 1], c4[:, 2], 60) >= 60
    b = M.stay(r, z0, z0, z0, c4[:, 0], c4[:, 1], c4[:, 2], 61) >= 61
    print('   %-14s start at 0 differs from start at c: %d;  start-at-0 solid differs from the lathe: %d' % (r.name, int((a != b).sum()), int((b != lat).sum())))
