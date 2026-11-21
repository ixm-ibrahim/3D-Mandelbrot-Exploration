"""Round 22, entrycheck second pass: some sentences of the two entries that nobody re-measured in this round, measured
with the library (leaving = |v| >= 64). Each line names the sentence it tests.
  python out/r22/entrycheck2/e2_claims.py -> claims.txt
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

SHEET = sys.modules['rules_sheet']
PP = J.get('sheet.evc005e70k16'); AO = J.get('alongmem.c_wake1'); ONE = M.bench('oneplane')
def evc(s, e, kc):
    st, ini = SHEET.evc(s, ease_c=e, ease=e, kc=kc); return M.Rule('v', 'evc %g %g %g' % (s, e, kc), st, ini)
out = []
def say(t):
    out.append(t); print(t); sys.stdout.flush()
rng = np.random.default_rng(314); N = 300000
x = rng.uniform(-1.8, 1.8, N); y = rng.uniform(-1.4, 1.4, N); z = rng.uniform(-1.4, 1.4, N)
R2 = 4096.0

# 1. "The rabbit is nearly the rabbit of Sphere inversions, one plane (one point in eight of its inside differs)"
a = M.stay(PP, x, y, z, *M.RABBIT, 80, r2=R2) >= 80; b = M.stay(ONE, x, y, z, *M.RABBIT, 80, r2=R2) >= 80
say('1. Pulled plane rabbit against the one-plane rabbit, %d random points, 80 steps: inside %d and %d, in one but not the other %d = one in %.1f of the Pulled plane inside (%.1f %% of the union)' % (N, a.sum(), b.sum(), (a != b).sum(), a.sum() / max(1, (a != b).sum()), 100.0 * (a != b).sum() / max(1, (a | b).sum())))

# 2. "The Siegel disc loses 15% of its points between 30 and 200 steps before it settles"
n = M.stay(PP, x, y, z, *M.SIEGEL, 400, r2=R2)
say('2. Pulled plane, Siegel disc: stay 30 / 200 / 400 steps: %d / %d / %d; lost between 30 and 200: %.1f %%; between 200 and 400: %.1f %%' % ((n >= 30).sum(), (n >= 200).sum(), (n >= 400).sum(), 100.0 * (1 - (n >= 200).sum() / max(1, (n >= 30).sum())), 100.0 * (1 - (n >= 400).sum() / max(1, (n >= 200).sum()))))

# 3. "with the rabbit's c turned by 10, 30 or 45 degrees about the x-axis no point of it was left" (Pulled plane); "10 degrees or more" (Along once)
for deg in (10, 30, 45, 90):
    t = math.radians(deg); c = (M.RABBIT[0], M.RABBIT[1] * math.cos(t), M.RABBIT[1] * math.sin(t))
    p = M.stay(PP, x, y, z, *c, 300, r2=R2); q = M.stay(AO, x, y, z, *c, 300, r2=R2)
    say('3. rabbit c turned %2d degrees: Pulled plane stay 40 / 80 / 300: %d / %d / %d; Along once: %d / %d / %d' % (deg, (p >= 40).sum(), (p >= 80).sum(), (p >= 300).sum(), (q >= 40).sum(), (q >= 80).sum(), (q >= 300).sum()))

# 4. "For c = -1 + 0.2i nothing is left in the plane y = 0" (Pulled plane)
W, H = 600, 440
gx, gz = np.meshgrid(-1.8 + 3.6 * (np.arange(W) + 0.5) / W, -1.3 + 2.6 * (np.arange(H) + 0.5) / H)
for c in ((-1.0, 0.2, 0.0), (-1.0, 0.0, 0.0), (-1.0, 0.05, 0.0)):
    n = M.stay(PP, gx, np.zeros_like(gx), gz, *c, 80, r2=R2)
    off = (np.abs(gz) > 0.02)
    say('4. Pulled plane, c = %s, the plane y = 0 (%d points): stay 80 steps %d; of them off the x-axis by more than 0.02: %d' % (c, W * H, (n >= 80).sum(), ((n >= 80) & off).sum()))

# 5. "The Mandelbrot solid shows the flat set in the plane z = 0 and, but for a few points, in the plane y = 0 (104 of 84,000 places differ)"
W, H = 350, 240
cx, cz = np.meshgrid(-2.1 + 2.8 * (np.arange(W) + 0.5) / W, -1.2 + 2.4 * (np.arange(H) + 0.5) / H)
def flat(cr, ci, steps):
    zc = cr + 1j * ci; z = zc.copy(); alive = np.ones(z.shape, bool); n = np.zeros(z.shape, int)
    with np.errstate(all='ignore'):
        for _ in range(steps):
            z = z * z + zc; alive &= (z.real ** 2 + z.imag ** 2) < R2; n += alive; z = np.where(alive, z, 0)
    return n >= steps
for steps in (60, 200):
    f = flat(cx, cz, steps)
    m = M.stay(PP, cx, np.zeros_like(cx), cz, cx, np.zeros_like(cx), cz, steps, r2=R2) >= steps
    m0 = M.stay(PP, cx, cz, np.zeros_like(cx), cx, cz, np.zeros_like(cx), steps, r2=R2) >= steps
    say('5. Pulled plane, Mandelbrot, %d steps, %d places: the plane y = 0 against the flat set: %d differ (flat inside %d); the plane z = 0: %d differ' % (steps, W * H, (m != f).sum(), f.sum(), (m0 != f).sum()))

# 6. the dial help texts: "at 1 a third of the set is lost" (second dial, rabbit), measured against the dials where they start
base = M.stay(PP, x, y, z, *M.RABBIT, 80, r2=R2) >= 80
for nm, r in (('second dial at 1', evc(0.05, 1.0, 16.0)), ('second dial at 0.5', evc(0.05, 0.5, 16.0)), ('third dial at 4', evc(0.05, 0.7, 4.0))):
    v = M.stay(r, x, y, z, *M.RABBIT, 80, r2=R2) >= 80
    say('6. Pulled plane rabbit, %s: inside %d against %d with the dials where they start (%.0f %% of it)' % (nm, v.sum(), base.sum(), 100.0 * v.sum() / max(1, base.sum())))

# 7. Along once: "a point belongs to a Julia set of this entry exactly when its first step lands in the solid that Sphere inversions, one plane draws for the same c"
ALONG = M.bench('along')
for nm, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
    X, Y, Z, _ = ALONG.step(x, y, z, ALONG.init(N), 0, np.full(N, c[0]), np.full(N, c[1]), np.full(N, c[2]))
    first = M.stay(ONE, X + c[0], Y + c[1], Z + c[2], *c, 79, r2=R2) >= 79
    whole = M.stay(AO, x, y, z, *c, 80, r2=R2) >= 80
    say('7. Along once, %s: "one step of along, then in the one-plane solid" against the entry itself, %d points: %d differ (inside %d)' % (nm, N, (first != whole).sum(), whole.sum()))
open(os.path.join(HERE, 'claims.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
