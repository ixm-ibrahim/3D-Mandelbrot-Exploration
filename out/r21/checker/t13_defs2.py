"""t13: two more definitions re-coded from the reports' words and compared with the reporters' code:
span's c_lag10 and frame's area_1_px and orb_inf_px."""
import sys
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
import mem as M, ck

span, frame = ck.load('span'), ck.load('frame')


def unit(a):
    n = np.linalg.norm(a, axis=0); return a / np.where(n > 0, n, 1.0), n


def c_lag(lam):
    def step(x, y, z, st, k, cx, cy, cz):
        n = np.stack(st); v = np.stack([x, y, z]); c = np.stack([np.broadcast_to(t, x.shape) for t in (cx, cy, cz)])
        m, ln = unit(np.cross(v, c, axis=0)); par = ln <= 1e-9 * np.linalg.norm(v, axis=0) * np.linalg.norm(c, axis=0)
        m = np.where(par, n, m); s = np.where((n * m).sum(0) >= 0, 1.0, -1.0)
        n, _ = unit((1 - lam) * n + lam * s * m)
        a = np.array([1.0, 0, 0])[:, None] - n[0] * n; a, _ = unit(a); b = np.cross(n, a, axis=0)
        A, B, C = ck.P((v * a).sum(0), (v * b).sum(0), (v * n).sum(0))
        out = A * a + B * b + C * n
        return out[0], out[1], out[2], tuple(n)
    return ck.R('c_lag%g(mine)' % lam, step, lambda n: (np.zeros(n), np.zeros(n), np.ones(n)))


def follow_plane(mode, mu=1.0):
    """mode 'area': w = v x v' (not unit), tau = 1/2 atan2(2 mu p q, 1 + mu (p^2 - q^2));
       mode 'plane': w = v^ x v'^ (unit vectors), tau = 1/2 atan2(2 p q, p^2 - q^2)."""
    def step(x, y, z, st, k, cx, cy, cz):
        e1, e2, e3 = np.stack(st[0:3]), np.stack(st[3:6]), np.stack(st[6:9]); v = np.stack([x, y, z])
        A, B, W = ck.P((v * e1).sum(0), (v * e2).sum(0), (v * e3).sum(0))
        F = A * e1 + B * e2 + W * e3; vn = F + np.stack([np.broadcast_to(t, x.shape) for t in (cx, cy, cz)])
        if mode == 'area':
            w = np.cross(v, vn, axis=0)
        else:
            w = np.cross(unit(v)[0], unit(vn)[0], axis=0)
        p = (w * e3).sum(0); wp = w - p * e3; m, q = unit(wp)
        tau = 0.5 * np.arctan2(2 * mu * p * q, 1 + mu * (p * p - q * q)) if mode == 'area' else 0.5 * np.arctan2(2 * p * q, p * p - q * q)
        tau = np.where(q > 0, tau, 0.0)
        n3 = np.cos(tau) * e3 + np.sin(tau) * m; n3, _ = unit(n3)
        sh = np.array([1.0, 0, 0])[:, None] - n3[0] * n3; n1, ln = unit(sh)
        alt, _ = unit(e1 - (e1 * n3).sum(0) * n3); n1 = np.where(ln > 1e-12, n1, alt)
        n2 = np.cross(n3, n1, axis=0)
        return F[0], F[1], F[2], (*n1, *n2, *n3)
    def init(n):
        o, e = np.zeros(n), np.ones(n); return (e, o, o, o, e, o, o, o, e)
    return ck.R('%s(mine)' % mode, step, init)


pairs = [('span c_lag10', span.get('c_lag10'), c_lag(0.1)), ('span c_lag25', span.get('c_lag25'), c_lag(0.25)),
         ('frame area_1_px', ck.byname(frame, 'area_1_px'), follow_plane('area')), ('frame orb_inf_px', ck.byname(frame, 'orb_inf_px'), follow_plane('plane'))]
print('their code against my re-coding of their words: verdicts that differ of 60,000 at 60 steps (inside theirs / mine)')
for nm, a, b in pairs:
    out = []
    for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT), ('c=(-0.6,0.3,0.4)', (-0.6, 0.3, 0.4)), ('Mandelbrot', None)):
        d, ia, ib, n = ck.differ(a, b, c); out.append('%s %d (%d/%d)' % (cn, d, ia, ib))
    print('  %-18s %s' % (nm, '; '.join(out))); sys.stdout.flush()
