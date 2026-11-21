"""t9: do seeds on seeds get thinner? python out/r22/stability/t9_deeper.py > t9_deeper.txt
Basilica, along. Buds that stay in ONE page all the way, compared between the flat page and a diagonal page:
the same flat bud (its middle w is a point of the flat picture), put on the page, and measured: length along x
and thickness across the page (through the middle, 300 steps). Generation = steps needed to reach the body round -1.414.
Predicted long : thick = the product of |2 cos(t) - 1| over the steps (t = direction of the orbit point seen from 0)."""
import numpy as np
import stab as T
M = T.M
R = M.bench('along'); O = M.bench('oneplane')


def reach(r, p0, d, hmax=0.15, n=6001):
    t = np.linspace(0, hmax, n); tot = 0.0
    for sg in (1, -1):
        ins = M.stay(r, p0[0] + sg * t * d[0], p0[1] + sg * t * d[1], p0[2] + sg * t * d[2], *T.BAS, 300) >= 300
        tot += hmax if ins.all() else t[np.argmin(ins)]
    return tot


# flat bud middles: pull the point -1.41421 back along chosen branches of the square root
def back(w, sign):
    z = np.sqrt(complex(w) + 1.0); return z if (z.real >= 0) == (sign > 0) else -z


chains = {'gen 1: top of the middle body': [(-1)], 'gen 2: on the left body': [(-1), (-1)], 'gen 3: on the middle body, left side': [(-1), (-1), (-1)],
          'gen 3: on the right body': [(-1), (-1), (+1)], 'gen 4: left of the left body': [(-1), (-1), (-1), (-1)], 'gen 4': [(-1), (-1), (+1), (-1)]}
for label, signs in chains.items():
    w = complex(-np.sqrt(2.0), 0.0); path = []
    for k, s in enumerate(signs):
        w = back(w, s) if k else complex(0.0, np.sqrt(np.sqrt(2.0) - 1.0))
        path.append(w)
    w = complex(w.real, abs(w.imag))
    # the orbit of w, and the predicted squeeze beside a diagonal page
    z = w; pred = 1.0; orb = []
    for _ in signs:
        orb.append(z); pred *= abs(2 * z.real / abs(z) - 1); z = z * z - 1
    out = []
    for page in (0.0, 45.0):
        a = np.radians(page); p0 = np.array([w.real, w.imag * np.cos(a), w.imag * np.sin(a)]); e_off = np.array([0.0, -np.sin(a), np.cos(a)])
        if M.stay(R, *p0, *T.BAS, 300) < 300:
            out.append('page %g: middle not inside' % page); continue
        lx = reach(R, p0, np.array([1.0, 0, 0])); th = reach(R, p0, e_off)
        out.append('page %2g: long %.4f, thick %.5f, long : thick %.2f' % (page, lx, th, lx / max(th, 1e-9)))
    p0 = np.array([w.real, w.imag, 0.0]); lo = reach(O, p0, np.array([1.0, 0, 0])); to = reach(O, p0, np.array([0.0, 0, 1.0]))
    print('%-38s middle (%.4f, %.4f), orbit left/right: %s | along: %s | predicted beside the diagonal page %.2f | one-plane, flat page: long %.4f thick %.5f (%.2f)'
          % (label, w.real, w.imag, ''.join('L' if q.real < 0 else 'R' for q in orb), ' ; '.join(out), pred, lo, to, lo / max(to, 1e-9)))
