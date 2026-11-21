# Closer pictures for c = -1 (the "beads round two circles" question), the sheet for the user, and the cost count.
# Run from the project root: python out/r14/turns/s05_hero.py [N]
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from turns import *

LAB = dict(az=-109, el=31.5)            # the lab's opening view (yaw -1.9, pitch 0.55)
VIEWS = [('lab', LAB), ('axis', dict(az=0, el=0)), ('top', dict(az=-90, el=89))]


def hero(args):
    pair, key, N, outdir = args
    P1, P2 = RULES[pair]
    rules, mode = {'one': ([P1], 'union'), 'union': ([P1, P2], 'union'), 'common': ([P1, P2], 'common')}[key]
    vol, death, info = julia((-1.0, 0.0, 0.0), rules, mode, N=N, verbose=False)
    ims = {name: render(vol, **v) for name, v in VIEWS}
    np.savez_compressed(os.path.join(outdir, f'hero-{pair}-{key}.npz'), **ims)
    return pair, key, info['volume'], info['depth']


def rerender(args):
    path, N, kw, out = args
    d = np.load(path)
    vol = np.unpackbits(d['vol'])[:N ** 3].reshape(N, N, N).astype(bool)
    im = render(vol, **kw)
    np.save(out, im)
    return out, int(vol.sum())


def caption(im, text, size=320):
    p = Image.fromarray(im).resize((size, size), Image.LANCZOS)
    d = ImageDraw.Draw(p)
    d.text((8, size - 26), text, fill=(235, 235, 235), font=font(15))
    return np.asarray(p)


def cost(pair, c, depth=10, n=20000, seed=3):
    """How many rule evaluations the plain way needs per point (every order, with early exits), at random points
    of the ball: [mean over all points, mean over points that end up outside but survive 4 steps, the largest]."""
    P1, P2 = RULES[pair]
    rng = np.random.default_rng(seed)
    R = resc(c)
    p = rng.normal(size=(n, 3)); p *= (R * rng.uniform(0, 1, n) ** (1 / 3) / np.linalg.norm(p, axis=1))[:, None]
    ci = np.arange(n); x, y, z = p[:, 0].copy(), p[:, 1].copy(), p[:, 2].copy()
    evals = np.zeros(n); alive_depth = np.zeros(n, int)
    for d in range(depth):
        evals += 2 * np.bincount(ci, minlength=n)
        a1, b1, c1 = P1(x, y, z); a2, b2, c2 = P2(x, y, z)
        nx = np.concatenate([a1, a2]) + c[0]; ny = np.concatenate([b1, b2]) + c[1]; nz = np.concatenate([c1, c2]) + c[2]
        nc = np.concatenate([ci, ci])
        ok = (nx * nx + ny * ny + nz * nz) <= R * R
        ci, x, y, z = nc[ok], nx[ok], ny[ok], nz[ok]
        alive_depth[np.unique(ci)] = d + 1
    inside = alive_depth == depth
    near = (~inside) & (alive_depth >= 4)
    return dict(depth=depth, mean_all=float(evals.mean()), mean_inside=float(evals[inside].mean()) if inside.any() else 0.0,
                mean_outside_near=float(evals[near].mean()) if near.any() else 0.0, largest=float(evals.max()),
                share_inside=float(inside.mean()))


if __name__ == '__main__':
    import multiprocessing as mp
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 321
    OUT = os.path.join(HERE, f'hero-N{N}'); os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    jobs = [(pair, key, N, OUT) for pair in ('E', 'K') for key in ('one', 'union', 'common')]
    J = os.path.join(HERE, 'julia-N257'); M = os.path.join(HERE, 'mandel-N161-d12')
    re = []
    for pair in ('E', 'K'):
        for ci in (1, 2):
            for key in ('one', 'union', 'common'):
                re.append((os.path.join(J, f'vol-{pair}-{ci}-{key}-N257.npz'), 257, LAB, os.path.join(OUT, f'j-{pair}-{ci}-{key}.npy')))
        for key in ('one', 'union', 'common'):
            re.append((os.path.join(M, f'vol-{pair}-{key}.npz'), 161, LAB, os.path.join(OUT, f'm-{pair}-{key}.npy')))
    with mp.Pool(6) as pool:
        r1 = pool.map_async(hero, jobs, chunksize=1)
        r2 = pool.map_async(rerender, re, chunksize=1)
        heroes = r1.get(); rr = dict(r2.get())
    print('heroes', heroes, 'in %.0f s' % (time.time() - t0), flush=True)

    # ---- sheet: c = -1 from three sides
    rows = []; names = []
    for pair in ('E', 'K'):
        for key, word in (('one', 'one rule alone'), ('union', 'both rules, UNION'), ('common', 'both rules, COMMON')):
            d = np.load(os.path.join(OUT, f'hero-{pair}-{key}.npz'))
            rows.append([d['lab'], d['axis'], d['top']]); names.append(f'pair {pair}\n{word}')
    sheet(rows, ['the lab\'s opening view', 'looking along the x-axis', 'from above (down the z-axis)'], names,
          os.path.join(HERE, f'sheet-beads-c-1-N{N}.png'), title=f'Julia set for c = -1 from three sides. Grid {N}.',
          note=['Beads round two circles would show as a cross of bumps in the middle column (up, down, left, right) and nothing between.'])

    # ---- the sheet for the user
    def cell(pair, row, key):
        if row == 0:
            im = np.load(os.path.join(OUT, f'hero-{pair}-{key}.npz'))['lab']; n = None
        elif row in (1, 2):
            p = os.path.join(OUT, f'j-{pair}-{row}-{key}.npy'); im = np.load(p); n = rr[p]
        else:
            p = os.path.join(OUT, f'm-{pair}-{key}.npy'); im = np.load(p); n = rr[p]
        text = ''
        if n is not None and n == 0:
            text = 'nothing: no point stays'
        elif n is not None and n < 2000 and row != 3:
            text = 'almost nothing: a few specks'
        return caption(im, text)
    rows = [[cell(pair, r, key) for pair in ('E', 'K') for key in ('one', 'union', 'common')] for r in range(4)]
    sheet(rows, ['One rule alone', 'Both rules: stays for SOME order', 'Both rules: stays for EVERY order',
                 'One rule alone', 'Both rules: stays for SOME order', 'Both rules: stays for EVERY order'],
          ['Julia set\nc = -1\n(on the x-axis)', 'Julia set\nc = (-1, 0.15, 0.1)\n(a little off\nthe axis)', 'Julia set, rabbit\nc = (-0.12, 0.74, 0)',
           'Mandelbrot solid\n(orders tried\n12 steps deep)'],
          os.path.join(HERE, 'sheet-for-user.png'), cell=320,
          title='Trial: both rules at every step.   Left three columns: the exact rule ("Sphere inversions, one plane").   Right three: the Kleinian squaring.',
          note=['Each point may use the rule for the plane z = 0 or the same rule turned a quarter turn, freely, at every step. No region is chosen by hand, so there is no seam.',
                '"Some order": the point counts when at least one way of mixing the two rules keeps it from flying off. "Every order": only when no way of mixing them throws it out.',
                'What came out: with c on the x-axis both stay close to the one-rule solid ("some order" grows extra warts). With c off the axis "some order" swells into a fat lump',
                'and "every order" leaves nothing at all. Neither gives fine detail in every direction.'])
    print('sheets written in %.0f s' % (time.time() - t0), flush=True)

    # ---- cost of the plain way (every order, early exits), per point
    out = {}
    for pair in ('E', 'K'):
        for c in ((-1.0, 0.0, 0.0), (-1.0, 0.15, 0.1)):
            for depth in (8, 10, 12):
                out[f'{pair} c={c} depth {depth}'] = cost(pair, c, depth, n=6000)
                print(pair, c, depth, out[f'{pair} c={c} depth {depth}'], flush=True)
    json.dump(out, open(os.path.join(HERE, 'cost.json'), 'w'), indent=1)
