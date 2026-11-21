"""Going round the x-axis through a bud of the flat picture: ring, arcs, or only at the flat page? (NOTES.md, part 4)

    python out/r21/prover/t4_rings.py  ->  out/r21/prover/t4_rings.txt, t4_rings.png

For each rule: (a) the circle round the x-axis through the centre of three buds of the flat set (period 3 on top of
the main body, period 4, period 5): at which turns theta is the point in the solid?  (b) a picture of the band round
the x-axis at x = -0.1226 (the plane across the x-axis through the centre of the period-3 bud), unrolled:
theta to the right (-180..180), distance from the x-axis upward (0.50..0.95).  A ring of the lathe is a level stripe.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

BUDS = [('period 3 (top of the main body)', -0.122561, 0.744862, 0.094), ('period 4', 0.282271, 0.530061, 0.044), ('period 5', -0.504340, 0.562766, 0.040)]
out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def arcs(inside, th):
    """The runs of 'inside' along the circle, as (from, to) in degrees; the circle is closed."""
    n = len(th)
    if inside.all():
        return 'ALL ROUND (a ring)'
    if not inside.any():
        return 'nowhere'
    k0 = int(np.argmin(inside)); ins = np.roll(inside, -k0); t = np.roll(th, -k0); res = []; i = 0
    while i < n:
        if ins[i]:
            j = i
            while j + 1 < n and ins[j + 1]:
                j += 1
            res.append((t[i], t[j])); i = j + 1
        else:
            i += 1
    res.sort()
    return '%d arc(s): ' % len(res) + ', '.join('%.1f..%.1f' % (p, q) for p, q in res[:12]) + (' ...' if len(res) > 12 else '')


def main():
    scout = {r.name: r for r in M.SCOUT}; t0 = time.time(); steps = 80
    rules = [scout['own'], scout['lag75'], scout['lag50'], scout['lag25'], scout['first'], R.BY['first2'], scout['delay'], scout['fixed'], M.bench('along'), M.bench('away')]
    th = np.arange(-180.0, 180.0, 0.25); a = np.radians(th)
    say('Circles round the x-axis through the centre of a bud of the flat set, %d steps, one test point every quarter degree.' % steps)
    say('theta = 0 is the flat page (the bud itself), +-180 is its mirror twin below; a ring would be "ALL ROUND".')
    for nm, bx, by, br in BUDS:
        say(); say('%s: centre (%.4f, %.4f), flat radius about %.3f; a ROUND bud would cover about +-%.1f degrees' % (nm, bx, by, br, np.degrees(br / by)))
        for r in rules:
            ins = M.mandel(r, np.full_like(a, bx), by * np.cos(a), by * np.sin(a), steps) >= steps
            say('   %-7s %s' % (r.name, arcs(ins, th)))
    # the unrolled band
    W, Hh = 1080, 135; T, RHO = np.meshgrid(np.radians(np.linspace(-180, 180, W)), np.linspace(0.95, 0.50, Hh)); x0 = BUDS[0][1]
    pad = 8; im = Image.new('RGB', (W + 2 * pad, 40 + len(rules) * (Hh + 26)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The band round the x-axis at x = %.4f, unrolled: turn theta from -180 (left) to 180 (right); distance from the x-axis 0.50 (bottom) to 0.95 (top). Flat page at the middle and at both ends.' % x0, fill=(240, 240, 245), font=M.font(14))
    for i, r in enumerate(rules):
        n = M.mandel(r, np.full_like(T, x0), RHO * np.cos(T), RHO * np.sin(T), 60)
        y = 40 + i * (Hh + 26); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(14))
        im.paste(Image.fromarray(M.shade(n, 60)), (pad, y + 20))
        for deg in (-90, 0, 90):
            xx = pad + int((deg + 180) / 360 * (W - 1)); d.line([(xx, y + 20), (xx, y + 26)], fill=(255, 120, 90), width=1)
    im.save(os.path.join(HERE, 't4_rings.png'))
    say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 't4_rings.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
