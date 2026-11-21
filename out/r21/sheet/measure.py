"""Measurements for the sheet family.

    python out/r21/sheet/measure.py vol   name ...     volume of six Julia sets and of the Mandelbrot solid at 30 / 80 / 200 steps (leaks)
    python out/r21/sheet/measure.py thick name ...     does the flat picture have BODY? flat-inside points lifted a little off the page
    python out/r21/sheet/measure.py arcs  name ...     the buds met on a circle round the x-axis (count, widths, roundness)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M


def vol(rule, n=120000, steps=(30, 80, 200), seed=11):
    """Share of a box that is inside, at several step counts, for the six Julia sets and the Mandelbrot solid."""
    rng = np.random.default_rng(seed); out = {}
    v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3))
    for nm, c in M.JSETS:
        k = M.stay(rule, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], max(steps))
        out[nm.split(',')[0]] = [100 * float((k >= s).mean()) for s in steps]
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    k = M.mandel(rule, c[:, 0], c[:, 1], c[:, 2], max(steps))
    out['Mandelbrot'] = [100 * float((k >= s).mean()) for s in steps]
    return out


def thick(rule, n=60000, steps=300, lifts=(1e-6, 1e-3, 3e-2), seed=7):
    """Take points well inside the flat picture (flat orbit never leaves in `steps` steps), lift them off the page by
    a small height, and count the share that is then lost. A picture with body loses none at small heights."""
    rng = np.random.default_rng(seed); out = {}
    sgn = rng.choice([-1.0, 1.0], n)
    cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n); ins = M.flat_stay(cr, ci, cr, ci, steps) >= steps
    out['Mandelbrot'] = [100 * float((M.mandel(rule, cr[ins], ci[ins], lf * sgn[ins], steps) < steps).mean()) for lf in lifts]
    zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for nm, c in M.JSETS[:5]:
        ins = M.flat_stay(zr, zi, c[0], c[1], steps) >= steps
        out[nm.split(',')[0]] = [100 * float((M.stay(rule, zr[ins], zi[ins], lf * sgn[ins], c[0], c[1], 0.0, steps) < steps).mean()) for lf in lifts] if ins.any() else [float('nan')] * len(lifts)
    return out


def circle(rule, x0, rho, c=None, steps=80, n=2880):
    """Inside or not, at n places on the circle of radius rho round the x-axis at x = x0. c = None: Mandelbrot solid."""
    a = np.arange(n) * 2 * np.pi / n; x = np.full(n, x0); y, z = rho * np.cos(a), rho * np.sin(a)
    k = M.mandel(rule, x, y, z, steps) if c is None else M.stay(rule, x, y, z, c[0], c[1], c[2], steps)
    return k >= steps


def arcs(ins):
    """The inside arcs on a circle: list of (centre in degrees, width in degrees)."""
    n = ins.size
    if ins.all():
        return [(0.0, 360.0)]
    if not ins.any():
        return []
    s = int(np.argmin(ins)); r = np.roll(ins, -s); out = []; i = 0      # start at an outside place
    while i < n:
        if r[i]:
            j = i
            while j < n and r[j]:
                j += 1
            out.append((((i + j - 1) / 2 + s) * 360.0 / n % 360.0, (j - i) * 360.0 / n)); i = j
        else:
            i += 1
    return out


def radial(rule, x0, ang, c=None, steps=80, lo=0.0, hi=1.4, n=1400):
    """Inside or not along the ray at turn ang (degrees) from the x-axis at x = x0: list of (from, to) in radius."""
    rho = np.linspace(lo, hi, n); a = np.radians(ang); x = np.full(n, x0); y, z = rho * np.cos(a), rho * np.sin(a)
    k = M.mandel(rule, x, y, z, steps) if c is None else M.stay(rule, x, y, z, c[0], c[1], c[2], steps)
    ins = k >= steps; out = []; i = 0
    while i < n:
        if ins[i]:
            j = i
            while j < n and ins[j]:
                j += 1
            out.append((float(rho[i]), float(rho[j - 1]))); i = j
        else:
            i += 1
    return out


# the two test circles: through the middle of the bud on top of the basilica's middle body, and of the period-3 bud
CIRCLES = [('basilica bud', 0.0, 0.62, (-1.0, 0.0, 0.0), 0.19), ('Mandelbrot period-3 bud', -0.1226, 0.7449, None, 0.19)]


def fmt_arcs(a, rho, radial_w):
    if not a:
        return 'nothing'
    big = sorted(a, key=lambda t: -t[1])[:6]
    return '%d arc(s): ' % len(a) + ', '.join('%.0f wide at %.0f (x%.1f)' % (w, c, np.radians(w) * rho / radial_w) for c, w in sorted(big))


if __name__ == '__main__':
    kind, names = sys.argv[1], sys.argv[2:]
    for nm in names:
        r = R.get(nm)
        if kind == 'vol':
            o = vol(r); print('%-10s ' % nm + ' | '.join('%s %s' % (k, '/'.join('%.2f' % t for t in v)) for k, v in o.items()))
        elif kind == 'thick':
            o = thick(r); print('%-10s lost %% at lift 1e-6 / 1e-3 / 3e-2: ' % nm + ' | '.join('%s %s' % (k, '/'.join('%.1f' % t for t in v)) for k, v in o.items()))
        elif kind == 'arcs':
            for cn, x0, rho, c, rw in CIRCLES:
                print('%-10s %-24s %s' % (nm, cn, fmt_arcs(arcs(circle(r, x0, rho, c)), rho, rw)))
        sys.stdout.flush()
