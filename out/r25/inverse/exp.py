"""Round 25, section 'inverse': the pictures.

    python out/r25/inverse/exp.py cuts
    python out/r25/inverse/exp.py clouds
    python out/r25/inverse/exp.py solids <name> <a|top> <row,row,...> [n] [pre] [sets]
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import roots as R
M = R.M
R.Zip.ITERS = 24

Z10, Z10m, Z15, Z15m, Z20, Z20m = R.Zip(1.0), R.Zip(1.0, True), R.Zip(1.5), R.Zip(1.5, True), R.Zip(2.0), R.Zip(2.0, True)
ROWS = {
    'one': ('one plane (for comparison)', [R.P], 'any'),
    'lathe': ('quaternion square (for comparison)', [R.Q], 'any'),
    'pq_any': ('one-plane roots and quaternion roots together: inside when SOME choice of square stays', [R.P, R.Q], 'any'),
    'pq_all': ('one-plane roots and quaternion roots together: inside when EVERY choice of square stays', [R.P, R.Q], 'all'),
    'zip10': ('zip, square pillow (b = 1): the four roots that shrink every direction alike', [Z10.F], 'any'),
    'zip15': ('zip, pillow one and a half times as tall (b = 1.5)', [Z15.F], 'any'),
    'zip20': ('zip, pillow twice as tall (b = 2)', [Z20.F], 'any'),
    'zz10_any': ('zip b = 1 and its mirror image together: SOME choice stays', [Z10.F, Z10m.F], 'any'),
    'zz10_all': ('zip b = 1 and its mirror image together: EVERY choice stays', [Z10.F, Z10m.F], 'all'),
    'zz15_any': ('zip b = 1.5 and its mirror image together: SOME choice stays', [Z15.F, Z15m.F], 'any'),
    'zz15_all': ('zip b = 1.5 and its mirror image together: EVERY choice stays', [Z15.F, Z15m.F], 'all'),
}
SETS = dict(R.SETS)
SETS.update({'c = 0': (0.0, 0.0, 0.0), 'c = -0.3': (-0.3, 0.0, 0.0), 'c = 0.25i': (0.0, 0.25, 0.0), 'c = -0.5+0.5i': (-0.5, 0.5, 0.0)})


def maker(key, n, pre):
    label, Fs, mode = ROWS[key]

    def make(c):
        Kf, meta = R.grid_K(Fs, c, mode, n=n)
        return R.inside_grid(Fs, c, mode, Kf, meta, pre=pre)
    return label, make


def cuts():
    rules = [M.fixed(R.P, 'one plane', ''), Z10.rule('zip b=1'), Z10m.rule('zip b=1, other way up'), Z15.rule('zip b=1.5'), Z20.rule('zip b=2')]
    sets = [('c = -1', SETS['c = -1']), ('rabbit', SETS['rabbit']), ('c = -0.3', SETS['c = -0.3'])]
    w, h, steps, pad = 260, 195, 40, 8
    cols = [('flat', 0.0), ('turned 45', 45.0), ('upright through x', 90.0), ('across at x = 0', None)]
    W = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name, fill=(235, 220, 170), font=M.font(15))
        for j, (sn, c) in enumerate(sets):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                if ang is None:
                    p, q = np.meshgrid(np.linspace(-1.8, 1.8, w), np.linspace(1.35, -1.35, h)); n = M.stay(r, np.zeros_like(p), p, q, c[0], c[1], c[2], steps)
                else:
                    n = M.cut_axis(r, ang, w, h, steps, c=c, box=(-1.8, 1.8, -1.35, 1.35))
                im.paste(Image.fromarray(M.shade(n, steps)), (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush(); im.save(os.path.join(HERE, 'cuts.png'))
    print('wrote cuts.png', im.size)


def clouds():
    sets = [('c = -1', SETS['c = -1']), ('rabbit', SETS['rabbit']), ('c = -0.3', SETS['c = -0.3'])]
    kinds = [('the two one-plane roots', R.roots_P), ('the two quaternion roots', R.roots_Q),
             ('all four of them', lambda X, Y, Z: R.roots_P(X, Y, Z) + R.roots_Q(X, Y, Z)),
             ('the four zip roots (b = 1)', Z10.roots), ('the four zip roots (b = 1.5)', Z15.roots)]
    w, h, pad = 380, 285, 10; W = pad + len(sets) * (w + pad); H = 56 + len(kinds) * (h + 36)
    for tag, cam in R.CAMS.items():
        im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
        d.text((pad, 10), 'What is left when the roots are applied over and over to points (eye at %s)' % (cam,), fill=(240, 240, 245), font=M.font(22))
        for i, (label, fn) in enumerate(kinds):
            y = 56 + i * (h + 36); d.text((pad, y), label, fill=(235, 220, 170), font=M.font(17))
            for j, (sn, c) in enumerate(sets):
                pts = R.cloud(fn, c, walkers=40000, steps=48, burn=18); x = pad + j * (w + pad)
                im.paste(Image.fromarray(R.draw_cloud(pts, cam, w, h)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=M.font(13))
                if tag == 'a':
                    print('   %-30s %-8s points off the flat plane (|z| > 0.01): %.3f; highest |z| %.3f' % (label, sn, (np.abs(pts[2]) > 0.01).mean(), np.abs(pts[2]).max()))
        im.save(os.path.join(HERE, 'clouds-%s.png' % tag)); print('wrote clouds-%s.png' % tag); sys.stdout.flush()


def solids(name, tag, keys, n=224, pre=1, sets=('c = -1', 'rabbit'), w=380, h=285, nd=200):
    rows = [maker(k, n, pre) for k in keys]
    R.sheet(rows, os.path.join(HERE, '%s-%s.png' % (name, tag)), [(s, SETS[s]) for s in sets], R.CAMS[tag], w=w, h=h, nd=nd,
            title='Rough solids (%d^3 blocks, %d exact squaring in front), eye at %s' % (n, pre, R.CAMS[tag]))
    print('wrote %s-%s.png' % (name, tag))


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'cuts':
        cuts()
    elif a == 'clouds':
        clouds()
    else:
        name, tag, keys = sys.argv[2], sys.argv[3], sys.argv[4].split(',')
        n = int(sys.argv[5]) if len(sys.argv) > 5 else 224; pre = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        sets = sys.argv[7].split(';') if len(sys.argv) > 7 else ('c = -1', 'rabbit')
        solids(name, tag, keys, n, pre, sets)
