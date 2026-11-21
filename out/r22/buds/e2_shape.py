"""E2: what decides whether a bud is a ball, a lens, a rib or a fin.   python out/r22/buds/e2_shape.py -> shape.txt

(a) Family test: the page follows the point by a dial a (psi = phi - a sin(4 phi)/4; a = 1 is along, a = 0 the lathe).
    Width of the buds on the ring through the top bud of the middle body, against the law 'width goes as 1 / a'.
(b) For every inside arc on rings g1..g3 (basilica) and the rules along, once, pulled, oneplane: the bud's measured
    size round the axis, outward, and along x; and what the steps to the x-axis do to a small move in each of
    those three directions (finite differences of the library's own orbit).
(c) A comb of fins of along (cut at 22.5 degrees, skin near x = -0.3): where its points go, step by step."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B
M = B.M
out = open(os.path.join(HERE, 'shape.txt'), 'w', encoding='utf-8')
C = B.BASILICA; N = 2880; STEPS = 80


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


def stretch(name, p, k, rule=None, h=1e-6):
    """Columns: what k steps do to a small move outward (rho), round the axis (phi), along x. Returns the 3 lengths
    of the moved images per unit move, and the largest / smallest stretch of the k-step map there."""
    x0, y0, z0 = p; rho = np.hypot(y0, z0); er = np.array([0, y0 / rho, z0 / rho]); ep = np.array([0, -z0 / rho, y0 / rho]); ex = np.array([1.0, 0, 0])
    pts = np.array([p] + [np.array(p) + s * h * e for e in (er, ep, ex) for s in (1, -1)])
    t = B.trace(name, pts[:, 0], pts[:, 1], pts[:, 2], C, k, rule=rule, page_fn=(lambda y, z, st, kk: 0 * y) if rule is not None else None)
    q = np.array(t['pos'][k]).T
    J = np.array([(q[1 + 2 * i] - q[2 + 2 * i]) / (2 * h) for i in range(3)]).T
    sv = np.linalg.svd(J, compute_uv=False)
    return np.linalg.norm(J, axis=0), sv, np.linalg.det(J)


def thickness(name, p, direction, span, rule=None, n=1201):
    """Length of the inside run through p along a direction."""
    s = np.linspace(-span, span, n); P = [p[i] + s * direction[i] for i in range(3)]
    ins = B.inside(name, P[0], P[1], P[2], C, STEPS, rule=rule); mid = n // 2
    if not ins[mid]:
        return 0.0
    a = mid
    while a > 0 and ins[a - 1]: a -= 1
    b = mid
    while b < n - 1 and ins[b + 1]: b += 1
    return (b - a + 1) * (s[1] - s[0]) * (1 if (a > 0 and b < n - 1) else -1)      # negative = ran into the edge of the scan


def main():
    t0 = time.time(); fc = B.flat_centres(C[0]); phi = np.arange(N) * 2 * np.pi / N
    # ------------------------------------------------------------------ (a)
    say('(a) the page follows the point by a dial: psi = phi - a sin(4 phi) / 4. Ring through the top bud (x = 0, radius %.4f).' % abs(fc['g1'].imag))
    rad = abs(fc['g1'].imag); x, y, z = np.zeros(N), rad * np.cos(phi), rad * np.sin(phi)
    for a in (0.0, 0.125, 0.25, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        r = M.fixed(M.S.switch(a), 'switch%g' % a)
        ins = B.inside('x', x, y, z, C, STEPS, rule=r); ar = B.arcs(ins)
        w0 = [l * 360.0 / N for ci, l in ar if abs(B.fold(phi[int(round(ci)) % N])) < 0.05 or abs(abs(B.fold(phi[int(round(ci)) % N])) - np.pi / 2) < 0.05]
        w45 = [l * 360.0 / N for ci, l in ar if abs(abs(B.fold(phi[int(round(ci)) % N])) - np.pi / 4) < 0.05]
        law = np.degrees(0.5 * np.arcsin(min(1.0, 4 * np.arcsin(0.066 / rad) / a))) if a > 0 else float('inf')
        say('   a = %-5g inside %5.1f%% of the ring, %2d arcs | width at flat/upright %s | at the slanted pages %s | law (edge where the point is 0.066 off its page): %.1f deg'
            % (a, 100 * ins.mean(), len(ar), np.round(w0[:1], 1), np.round(w45[:1], 1), law))
    # ------------------------------------------------------------------ (b)
    say(''); say('(b) bud sizes on the rings, and what the steps to the x-axis do to a small move outward / round the axis / along x')
    say('    size = length of the inside run through the bud centre (negative: the run left the scan, i.e. joined to something)')
    for gi, g in enumerate(('g1', 'g2', 'g3')):
        x0, rad = fc[g].real, abs(fc[g].imag); x, y, z = np.full(N, x0), rad * np.cos(phi), rad * np.sin(phi)
        for name in ('oneplane', 'along', 'once', 'pulled'):
            ins = B.inside(name, x, y, z, C, STEPS); seen = set()
            for ci, ln in sorted(B.arcs(ins), key=lambda a: a[0]):
                i = int(round(ci)) % N; ang = np.degrees(phi[i]); key = (round(min(ang % 90, 90 - ang % 90), 0), round(ln * 360.0 / N, 0))
                if key in seen or ang > 180.5:
                    continue
                seen.add(key)
                p = (x0, y[i], z[i]); er = (0, np.cos(phi[i]), np.sin(phi[i])); ep = (0, -np.sin(phi[i]), np.cos(phi[i]))
                tr = thickness(name, p, er, 0.6 * rad); tp = ln * 2 * np.pi * rad / N; tx = thickness(name, p, (1, 0, 0), 0.3)
                col, sv, det = stretch(name, p, gi + 1)
                say('   %s %-8s bud at %6.2f deg: size round the axis %.4f, outward %.4f, along x %.4f | %d step(s) stretch a move outward x%.2f, round the axis x%.2f, along x x%.2f; largest/smallest %.2f; %s'
                    % (g, name, ang, tp, tr, tx, gi + 1, col[0], col[1], col[2], sv[0] / max(sv[2], 1e-12), 'mirrored' if det < 0 else 'not mirrored'))
        say('   (%.0f s)' % (time.time() - t0))
    # ------------------------------------------------------------------ (c)
    say(''); say('(c) fins of along: cut at 22.5 degrees from the flat page, window x -0.40..-0.20, height 0.34..0.46, 80 steps')
    a = np.radians(22.5); W = 900
    u, s = np.meshgrid(np.linspace(-0.40, -0.20, W), np.linspace(0.46, 0.34, W))
    ins = B.inside('along', u, s * np.cos(a), s * np.sin(a), C, STEPS)
    body = np.zeros_like(ins)                                            # the body = inside and joined to the bottom edge, column by column
    for j in range(W):
        col = ins[:, j]; i = W - 1
        while i >= 0 and col[i]:
            body[i, j] = True; i -= 1
    loose = ins & ~body
    say('   inside %.1f%% of the window; of that, not joined to the body below (fins, flakes, small buds): %.2f%% of the window' % (100 * ins.mean(), 100 * loose.mean()))
    runs = []
    for j in range(0, W, 3):                                             # thin runs in each column
        col = loose[:, j]; i = 0
        while i < W:
            if col[i]:
                k = i
                while k < W and col[k]: k += 1
                runs.append((k - i, i, j)); i = k
            else:
                i += 1
    runs.sort(); thin = [r for r in runs if r[0] <= 3]; fat = [r for r in runs if r[0] >= 12]
    say('   loose runs up the columns: %d in all, %d at most 3 pixels tall (pixel = %.5f), %d at least 12 pixels' % (len(runs), len(thin), 0.12 / W, len(fat)))
    rng = np.random.default_rng(2)
    for label, group in (('thin (fin)', thin), ('fat (bud)', fat)):
        if not group:
            continue
        pick = [group[i] for i in rng.choice(len(group), size=min(4, len(group)), replace=False)]
        for ln, i, j in pick:
            uu, ss = u[i + ln // 2, j], s[i + ln // 2, j]; p = (uu, ss * np.cos(a), ss * np.sin(a))
            t = B.trace('along', [p[0]], [p[1]], [p[2]], C, 8)
            say('   %s at x %.4f, height %.4f (%d px):' % (label, uu, ss, ln))
            for k in range(8):
                px, py, pz = (t['pos'][k + 1][m][0] for m in range(3))
                col, sv, det = stretch('along', p, k + 1)
                say('       step %d: page %6.1f, point %.4f off it -> x %7.4f, %.4f from the axis, at %6.1f deg | so far: largest/smallest stretch %.1f (largest x%.1f, smallest x%.2f)'
                    % (k + 1, np.degrees(B.fold(t['page'][k][0])), t['off'][k][0], px, np.hypot(py, pz), np.degrees(np.arctan2(pz, py)), sv[0] / max(sv[2], 1e-12), sv[0], sv[2]))
    np.save(os.path.join(HERE, 'fin-window.npy'), ins.astype(np.uint8) + loose.astype(np.uint8))
    say('   (%.0f s)' % (time.time() - t0))


if __name__ == '__main__':
    main()
