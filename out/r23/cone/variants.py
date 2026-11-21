"""The variants this section tested, registered in conelib.  import variants  (after sys.path has out/r23/cone)

    python out/r23/cone/variants.py report key [key ...]      numbers, flat check, lift test
    python out/r23/cone/variants.py cuts name key [key ...]   a sheet of cuts -> cuts-<name>.png
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L

PI = np.pi
# tuned by tune.py: no fold. (kind, mua, mub, bend)
WA = dict(kind=5, mua=0.0, mub=0.9, bend=0.732855)
WB = dict(kind=5, mua=0.0, mub=L.MU60, bend=0.478916)


def _w(theta, p):
    return lambda x, y, z: L.weld_dir(x, y, z, theta, p['mua'], p['mub'], p['bend'], p['kind'])


L.add('weld0', _w(0.0, WA), 'welded map: the rolled-up copy opens toward +x')
L.add('weldpi', _w(PI, WA), 'welded map: the rolled-up copy opens toward -x')
L.add('weld90', _w(PI / 2, WA), 'welded map turned a quarter (no y-mirror)')
L.add('weld0w', _w(0.0, WB), 'welded map, wide mix, opens toward +x')
L.add('weldpiw', _w(PI, WB), 'welded map, wide mix, opens toward -x')
L.add('rt30', lambda x, y, z: L.rt_dir(x, y, z, L.T15, PI / 6, 0.4, 'exp'), 'scout R_t turned 30 degrees (no y-mirror)')
L.add('rt-30', lambda x, y, z: L.rt_dir(x, y, z, L.T15, -PI / 6, 0.4, 'exp'), 'scout R_t turned -30 degrees (no y-mirror)')
L.add('rtn02', lambda x, y, z: L.rt_dir(x, y, z, L.T15, 0.0, 0.2, 'exp'), 'scout R_t, narrow blend (0.2)')
L.add('rt_t10', lambda x, y, z: L.rt_dir(x, y, z, 0.10, 0.0, 0.4, 'exp'), 'R_t with t = 0.10 (cone at 78.6 degrees, stretch 5)')
L.add('rt_t-10', lambda x, y, z: L.rt_dir(x, y, z, -0.10, 0.0, 0.4, 'exp'), 'R_t with t = -0.10')

# The no-fold condition, found in tune.py and then by hand: the mix must be exactly 2/3 turn-over at the Mercator
# latitude MU60/3 (latitude 24.4 degrees), where w^2 and the turn-over send a direction to the same latitude.
QSTAR = {3: 0.613037, 5: 0.59087}


def band(mua, kind=5):
    """Exactly w^2 (the one-plane rule) for |mu| <= mua; the mix ends at mub, set by the no-fold condition."""
    return dict(kind=kind, mua=mua, mub=mua + (L.MU60 / 3 - mua) / QSTAR[kind], bend=1.0)


for nm, mua in (('b0', 0.0), ('b1', 0.1), ('b2', 0.2), ('b3', 0.3)):
    p = band(mua)
    L.add('weld90' + nm, _w(PI / 2, p), 'welded, turned a quarter, exactly one-plane up to mu = %.1f (mix ends %.2f)' % (mua, p['mub']))
    L.add('weld0' + nm, _w(0.0, p), 'welded, opens +x, exactly one-plane up to mu = %.1f' % mua)
    L.add('weldpi' + nm, _w(PI, p), 'welded, opens -x, exactly one-plane up to mu = %.1f' % mua)
    L.add('weld270' + nm, _w(-PI / 2, p), 'welded, turned a quarter the other way, one-plane up to mu = %.1f' % mua)


def weld_c_rule(p=None, name='weldc', label='welded map, turned with c (the three stopping directions point away along c)'):
    """theta = 1.5 * arg(c): the critical values sit at longitude arg(c) (+120, +240), latitude 44.9. Looks at c."""
    p = p or band(0.2)

    def step(x, y, z, st, k, cx, cy, cz):
        th = 1.5 * np.arctan2(cy, cx) + 0 * x
        r2 = x * x + y * y + z * z
        X, Y, Z = L.weld_dir(x, y, z, th, p['mua'], p['mub'], p['bend'], p['kind'])
        ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0), st
    return L.M.Rule(name, label, step, init=lambda n: ())


def thickness(r, c, n=1500, steps=150, seed=11):
    """For flat-inside points: the first height above the flat plane at which the point is lost. Returns the heights."""
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, 6 * n), rng.uniform(-1.3, 1.3, 6 * n)
    ins = L.M.flat_stay(zr, zi, c[0], c[1], 400) >= 400; zr, zi = zr[ins][:n], zi[ins][:n]
    hs = 0.002 * 1.35 ** np.arange(22); th = np.zeros(zr.size); alive = np.ones(zr.size, bool)
    for h in hs:
        st = L.M.stay(r, zr, zi, np.full(zr.size, h), c[0], c[1], 0.0, steps) >= steps
        alive &= st; th[alive] = h
    return th


def get(k):
    if k == 'weldc':
        return weld_c_rule()
    if k in L.DIRS:
        return L.rule(k)
    return L.M.bench(k)


if __name__ == '__main__' and sys.argv[1] == 'thick':
    for k in sys.argv[2:]:
        r = get(k); row = []
        for sn, c in L.SETS:
            th = thickness(r, c); row.append('%s: median %.3f, share under 0.01: %.2f' % (sn, np.median(th), np.mean(th < 0.01)))
        print('%-10s %s' % (k, ' | '.join(row))); sys.stdout.flush()
    sys.exit()
if __name__ == '__main__' and sys.argv[1] == 'cuts2':
    cuts = L.CUTS[:3] + [('upright through c', None, (0, 0, 1)), ('across x at -1', None, None), ('tilted 20 about y', (float(np.cos(np.radians(20))), 0, float(np.sin(np.radians(20)))), (0, 1, 0))]
    for sn, c in L.SETS:
        cc = []
        for cn, e1, e2 in cuts:
            if cn == 'upright through c':
                a = np.arctan2(c[1], c[0]); e1 = (float(np.cos(a)), float(np.sin(a)), 0.0)
            cc.append((cn, e1, e2))
        cc[4] = ('upright through y, moved to x = c', (0, 1, 0), (0, 0, 1))
        tag = sn.replace(' ', '').replace('=', '').replace('.', '')
        rules = [get(k) for k in sys.argv[3:]]
        # the moved cut needs an origin: draw it by hand through cut_plane's origin argument
        from PIL import Image, ImageDraw
        w, h, steps, pad = 250, 190, 60, 6
        im = Image.new('RGB', (pad + len(cc) * (w + pad), 8 + len(rules) * (h + 26)), (12, 14, 20)); d = ImageDraw.Draw(im)
        for i, r in enumerate(rules):
            y = 26 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=L.M.font(14))
            for kk, (cn, e1, e2) in enumerate(cc):
                org = (c[0], 0.0, 0.0) if kk == 4 else (0.0, 0.0, 0.0)
                x = pad + kk * (w + pad)
                im.paste(Image.fromarray(L.M.shade(L.cut_plane(r, c, e1, e2, w, h, steps, origin=org), steps)), (x, y)); d.text((x + 3, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=L.M.font(11))
        im.save(os.path.join(HERE, 'cuts2-%s-%s.png' % (sys.argv[2], tag))); print('wrote cuts2', sys.argv[2], tag); sys.stdout.flush()
    sys.exit()
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'report':
        for k in sys.argv[2:]:
            L.report(k)
    elif cmd == 'cuts':
        L.cut_sheet(sys.argv[3:], os.path.join(HERE, 'cuts-%s.png' % sys.argv[2]))
