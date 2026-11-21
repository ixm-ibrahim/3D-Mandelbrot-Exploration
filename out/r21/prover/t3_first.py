"""The scout's rule 'first' in closed form, and what a rule that forgets its start can and cannot do (NOTES.md, part 3).

    python out/r21/prover/t3_first.py  ->  out/r21/prover/t3_first.txt, t3_first_cuts.png

A. The cut of the Mandelbrot solid of 'first' along the sheet turned theta, written out with no sheet look-up at all,
   against the library's own orbit.  c0 = a + i b is the point of the cut in the sheet's own coordinates.
B. The cut at 90 degrees as a purely flat (complex number) computation.
C. Is the solid a part of the flat set spun?  (points inside the solid whose own flat point c0 is outside the flat set)
D. Bounded orbits of the lathe with a start point OFF the sheet of c: do they all sink into the sheet?
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def first_cut_closed(a, b, theta_deg, steps, r2=36.0):
    """Verdicts of the closed form. Step 1: the one-plane square of c about the flat page, written in the frame of
    c's own sheet. Steps 2..: the lathe (quaternion square) with the constant c0 = (a, b, 0)."""
    th = np.radians(theta_deg); r = np.hypot(a, b); f = r * r / np.maximum(r * r + (b * np.sin(th)) ** 2, 1e-300)
    X = a + f * (a * a - (b * np.cos(th)) ** 2)
    Y = b + 2 * f * b * (a * np.cos(th) ** 2 + r * np.sin(th) ** 2)
    Z = f * b * (r - a) * np.sin(2 * th)
    alive = X * X + Y * Y + Z * Z < r2
    for _ in range(steps - 1):
        X, Y, Z = np.where(alive, X * X - Y * Y - Z * Z + a, X), np.where(alive, 2 * X * Y + b, Y), np.where(alive, 2 * X * Z, Z)
        alive &= X * X + Y * Y + Z * Z < r2
    return alive


def upright_cut_flat(a, b, steps, r2=36.0):
    """The 90 degree cut with complex numbers only: z1 = c + s(c), s(c) = f (a^2 + 2 i r b), f = r^2 / (r^2 + b^2); then z -> z^2 + c."""
    c = a + 1j * b; r = np.abs(c); f = r * r / np.maximum(r * r + b * b, 1e-300)
    z = c + f * (a * a + 2j * r * b); alive = np.abs(z) ** 2 < r2
    for _ in range(steps - 1):
        z = np.where(alive, z * z + c, z); alive &= (z.real ** 2 + z.imag ** 2) < r2
    return alive


def main():
    scout = {r.name: r for r in M.SCOUT}; first = scout['first']; t0 = time.time()
    W, H, steps = 420, 390, 60
    a, b = np.meshgrid(np.linspace(-2.1, 0.7, W), np.linspace(1.3, -1.3, H))
    flat = M.flat_stay(a, b, a, b, steps) >= steps
    say('A. The cut of "first" along the sheet turned theta: closed form against the library (%d x %d points, %d steps)' % (W, H, steps))
    tiles = []
    for th in (0.0, 11.25, 22.5, 33.75, 45.0, 67.5, 90.0):
        lib = M.cut_axis(first, th, W, H, steps) >= steps
        cf = first_cut_closed(a, b, th, steps)
        say('   theta = %5.2f: inside %6d (library) %6d (closed form), verdicts that differ %d | points of the cut outside the flat set: %d, points of the flat set missing: %d (flat set: %d)'
            % (th, lib.sum(), cf.sum(), (lib != cf).sum(), (lib & ~flat).sum(), (flat & ~lib).sum(), flat.sum()))
        img = M.shade(np.where(lib, steps, 0), steps); img[flat & ~lib] = (120, 60, 60); img[lib & ~flat] = (60, 220, 90)
        tiles.append(('theta = %g' % th, img))
    say('B. The cut at 90 degrees with complex numbers only:')
    lib = M.cut_axis(first, 90.0, W, H, steps) >= steps; fl = upright_cut_flat(a, b, steps)
    say('   verdicts that differ from the library: %d of %d' % ((lib != fl).sum(), lib.size))
    pad = 8; im = Image.new('RGB', (pad + len(tiles) * (W // 2 + pad), H // 2 + 66), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), "The scout's rule 'first': cuts along sheets through the x-axis. Cream = in the solid, dark red = in the flat set but cut away, green = in the solid but not in the flat set", fill=(240, 240, 245), font=M.font(14))
    for i, (t, img) in enumerate(tiles):
        x = pad + i * (W // 2 + pad); d.text((x, 34), t, fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(img).resize((W // 2, H // 2), Image.LANCZOS), (x, 58))
    im.save(os.path.join(HERE, 't3_first_cuts.png'))
    say('(%.0f s)' % (time.time() - t0)); say()

    say('C. Is the solid a part of the flat set spun round the x-axis?  300,000 random points c of the box, c0 = (x, distance from the x-axis)')
    rng = np.random.default_rng(21); n = 300000
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3)); rho = np.hypot(c[:, 1], c[:, 2])
    for steps in (60, 200):
        spun = M.flat_stay(c[:, 0], rho, c[:, 0], rho, steps) >= steps
        say('   %d steps; the flat set spun holds %.3f%% of the box' % (steps, 100 * spun.mean()))
        say('   %-10s %9s %22s %22s' % ('rule', 'inside', 'inside, NOT in the spun', 'in the spun, cut away'))
        rules = [scout[k] for k in ('own', 'first')] + [R.BY[k] for k in ('first2', 'first3', 'first5', 'first8')] + [scout[k] for k in ('delay', 'lag75', 'lag50', 'lag25', 'fixed')] + [M.bench('along')]
        for r in rules:
            m = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], steps) >= steps
            say('   %-10s %8.3f%% %15.3f%% (%6d) %15.3f%% (%6d)' % (r.name, 100 * m.mean(), 100 * (m & ~spun).mean(), (m & ~spun).sum(), 100 * (spun & ~m).mean(), (spun & ~m).sum()))
        say('   (%.0f s)' % (time.time() - t0))
    say()

    say('D. The lathe with a start point off the sheet of c: 200,000 random start points with |z| up to 1.2, 400 steps')
    v = rng.uniform([-1.8, -1.3, -1.2], [1.8, 1.3, 1.2], size=(200000, 3))
    for nm, cc in (('rabbit', M.RABBIT), ('basilica', (-1.0, 0.0, 0.0)), ('Siegel disc', M.SIEGEL), ('c = -0.4 + 0.3i (in the main body)', (-0.4, 0.3, 0.0)), ('c = 0.3 + 0.5i (outside the flat set)', (0.3, 0.5, 0.0)), ('dendrite c = i', (0.0, 1.0, 0.0))):
        X, Y, Z = v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy(); alive = np.ones(len(X), bool)
        for k in range(400):
            X, Y, Z = np.where(alive, X * X - Y * Y - Z * Z + cc[0], X), np.where(alive, 2 * X * Y + cc[1], Y), np.where(alive, 2 * X * Z, Z)
            alive &= X * X + Y * Y + Z * Z < 36.0
        if alive.any():
            # for c on the x-axis the 'sheet of c' is undefined: measure nothing there
            az = np.abs(Z[alive]); say('   %-38s stay: %6d (%.2f%%); their height above the page after 400 steps: largest %.2e, median %.2e' % (nm, alive.sum(), 100 * alive.mean(), az.max(), np.median(az)))
        else:
            say('   %-38s stay: 0' % nm)
    open(os.path.join(HERE, 't3_first.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
