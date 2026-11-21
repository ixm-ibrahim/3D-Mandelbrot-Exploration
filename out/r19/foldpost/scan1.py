"""One fold, cap centred in the upright plane y = 0: closed-form scan (no iteration, no rule code).
Angles along the upright great circle are measured from +x through straight-up (90) to -x (180).
Cap centre at psi, angular radius alpha. For -x and for +x: where the extra copy sits (answer angle E, and the
source latitude it comes from), its stretch = one-plane stretch * fold stretch, and where the crease runs.
    python out/r19/foldpost/scan1.py"""
import numpy as np
from scipy.optimize import brentq

def sP(E):                      # one-plane stretch seen from the answer, answer at angle E on the upright circle
    c = abs(np.cos(np.radians(E))); return np.sqrt(2 * c * (1 + c))
def src_lat(E):                 # source latitude of an answer at angle E (elevation min(E, 180 - E))
    L = min(E, 180 - E); return np.degrees(np.arcsin(np.tan(np.radians(L) / 2)))

def one(psi, alpha):
    a = np.tan(np.radians(alpha) / 2) ** 2
    out = {}
    for tag, t_out in (('+x', psi), ('-x', 180 - psi)):
        t_in = 2 * np.degrees(np.arctan(a / np.tan(np.radians(t_out) / 2)))
        E = psi - t_in if tag == '+x' else psi + t_in
        sR = np.sin(np.radians(t_out)) / np.sin(np.radians(t_in))
        out[tag] = dict(E=E, src_lat=src_lat(E), side='above +-x' if E < 90 else 'above +-y', sP=sP(E), sR=sR, s=sP(E) * sR)
    # the pole
    tN = abs(90 - psi)
    if tN < alpha:
        t_img = 2 * np.degrees(np.arctan(a / max(np.tan(np.radians(tN) / 2), 1e-12)))
        out['pole'] = psi + np.sign(90 - psi if psi != 90 else 1) * t_img
    else:
        out['pole'] = 90.0
    out['rim'] = (psi - alpha, psi + alpha)      # crease on the +x side and on the -x side (answer angle)
    return out

def solve_alpha_for_minus_x(psi, target=2.0):
    f = lambda al: one(psi, al)['-x']['s'] - target
    xs = np.linspace(1, min(psi, 180 - psi) - 0.01, 400); v = [f(x) for x in xs]
    sols = [brentq(f, xs[i], xs[i + 1]) for i in range(len(xs) - 1) if v[i] * v[i + 1] < 0]
    return sols

if __name__ == '__main__':
    print('A. One fold in the upright plane, radius chosen so that the extra copy of -x arrives with stretch exactly 2.')
    print('   centre = angle of the cap centre from +x (90 = straight up). All other angles: source latitude in degrees.')
    print('%7s %7s | %-28s | %-36s | %-22s | %s' % ('centre', 'radius', 'copy of -x (bud)', 'copy of +x (arm)', 'crease above +x, -x', 'pole sent to (answer angle from +x)'))
    for psi in (60, 70, 80, 85, 88, 90, 92, 94, 96, 97, 98, 99, 100, 102, 105, 110, 120):
        for al in solve_alpha_for_minus_x(psi):
            o = one(psi, al)
            print('%7.1f %7.2f | lat %5.1f %-9s str %.2f | lat %5.1f %-9s str %5.2f (%.2f x %.2f) | %5.1f, %5.1f | %6.1f' % (
                psi, al, o['-x']['src_lat'], o['-x']['side'], o['-x']['s'], o['+x']['src_lat'], o['+x']['side'], o['+x']['s'], o['+x']['sP'], o['+x']['sR'],
                src_lat(max(o['rim'][0], 0)), src_lat(min(o['rim'][1], 180)), o['pole']))
    print()
    print('B. Is there a cap for which BOTH extra copies (of -x and of +x) arrive with stretch 2? Scan of the whole family:')
    best = []
    for psi in np.arange(40, 140.01, 0.5):
        for al in np.arange(2, min(psi, 180 - psi) - 0.5, 0.25):
            o = one(psi, al)
            best.append((abs(np.log(o['-x']['s'] / 2)) + abs(np.log(o['+x']['s'] / 2)), psi, al, o))
    best.sort(key=lambda t: t[0])
    seen = []
    for e, psi, al, o in best[:4000]:
        if any(abs(psi - p) < 6 and abs(al - a) < 6 for p, a in seen): continue
        seen.append((psi, al))
        print('   centre %.1f radius %.2f: bud copy lat %.1f %s stretch %.2f; arm copy lat %.1f %s stretch %.2f; crease above +x %.1f, above -x %.1f' % (
            psi, al, o['-x']['src_lat'], o['-x']['side'], o['-x']['s'], o['+x']['src_lat'], o['+x']['side'], o['+x']['s'], src_lat(o['rim'][0]), src_lat(o['rim'][1])))
        if len(seen) >= 8: break
