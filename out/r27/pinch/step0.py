"""Step 0: the numbers everything else rests on. Writes step0.log (through stdout).
    - the meeting point, the far end, their stretch and turn, for c = -1 and the rabbit
    - how wide the true bodies open at the meeting point (share of a small circle round it that is inside)
    - the fitted moves: where their other fixed point lies, what they do to the middle body's two ends
"""
import numpy as np
import pinchlib as PL
M = PL.M


def opening(c, p, steps=1500, n=7200):
    """Share of small circles round p that lies inside the true flat picture, over one whole period of sizes."""
    lam = abs(2 * p); out = []
    for k in range(16):
        rho = 0.004 * lam ** (k / 16.0)
        t = (np.arange(n) + 0.5) / n * 2 * np.pi; z = p + rho * np.exp(1j * t)
        ins = M.flat_stay(z.real, z.imag, c.real, c.imag, steps) >= steps
        # runs of inside along the circle = the bodies; keep the longest runs
        d = np.diff(np.concatenate([[0], ins.astype(int), [0]])); a = np.where(d == 1)[0]; b = np.where(d == -1)[0]
        runs = sorted(((b - a) / n).tolist(), reverse=True)
        if ins[0] and ins[-1] and len(runs) > 1:                           # a run through the seam
            first = (b[0] - a[0]) / n; last = (b[-1] - a[-1]) / n
            runs = sorted([first + last] + [r for r in ((b - a) / n).tolist()[1:-1]], reverse=True)
        out.append((rho, ins.mean(), runs[:4]))
    return out


for key, c in PL.CS.items():
    al, be = PL.fixed_points(c)
    print('==== %s   c = %.6f %+.6f i' % (PL.NAMES[key], c.real, c.imag))
    for nm, p in (('meeting point', al), ('far end', be)):
        print('  %-13s %+.5f %+.5f i   stretch %.4f, turn %.2f degrees (%.4f of a full turn)' % (nm, p.real, p.imag, abs(2 * p), np.degrees(np.angle(2 * p)), np.angle(2 * p) / (2 * np.pi) % 1))
    op = PL.np.array([o[1] for o in opening(c, al)]); runs = opening(c, al)
    nb = 2 if key == 'c1' else 3
    big = np.array([sum(o[2][:nb]) for o in runs])
    print('  share of a small circle round the meeting point that is inside: mean %.4f (from %.4f to %.4f over one period of sizes)' % (op.mean(), op.min(), op.max()))
    print('  of which the %d big bodies: mean %.4f  -> each opens %.1f degrees (half opening %.1f)' % (nb, big.mean(), 360 * big.mean() / nb, 180 * big.mean() / nb))
    th = np.radians(180 * big.mean() / nb)
    print('  a body pointed at both ends with that opening is %.2f times as long as wide; three balls would need 120 degrees each, two 180' % (1 / np.tan(th / 2)))
    for n in (1, 2, 3):
        for kind in ('affine', 'osc', 'pin'):
            mv, sk = PL.fitted(c, n, kind)
            print('  fitted %d-step moves, %-6s: %d moves, %d points skipped (no finite stretch)' % (n, kind, len(mv), len(sk)))
            if n == 1 or kind == 'osc':
                for m in mv:
                    q = PL.other_fixed(m['M'], m['p'])
                    qs = 'infinity' if not np.isfinite(q) else '%+.3f %+.3f i' % (q.real, q.imag)
                    print('      word %-12s fixed %+.4f %+.4f i  factor %.4f turn %+7.2f deg   other fixed point %s' % (''.join('+' if s > 0 else '-' for s in m['word']), m['p'].real, m['p'].imag, abs(m['mu']), np.degrees(np.angle(m['mu'])), qs))
            if n == 1:
                for m in mv:
                    tr = PL.undo_word(m['word'], np.array([al, -al, 0.0, be, -be]), c)
                    ft = PL.ap(m['M'], np.array([al, -al, 0.0, be, -be]))
                    print('      word %s: sends (meeting point, its twin, 0, far end, its twin) off by %s from the true undo-move' % ('+' if m['word'][0] > 0 else '-', np.round(np.abs(tr - ft), 3)))
        if n > 1:
            mv, sk = PL.fitted(c, n, 'osc')
            for p, lam, w in sk:
                print('      skipped: %+.4f %+.4f i (stretch of the forward rule there %.3g)' % (p.real, p.imag, abs(lam)))
