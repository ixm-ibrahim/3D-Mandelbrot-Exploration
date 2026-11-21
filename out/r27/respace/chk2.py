"""Check of the body coordinate and of first entry in carry.py."""
import time
import numpy as np
import carry as C

t0 = time.time()
for nm, B in (('c = -1', C.BASILICA), ('rabbit', C.RABBIT)):
    print(nm, 'a =', np.round(B.a, 4), 'alpha =', np.round(B.alpha, 4))
    rng = np.random.default_rng(3)
    z = rng.uniform(-1.8, 1.8, 40000) + 1j * rng.uniform(-1.3, 1.3, 40000)
    n, zn, d, alive = C.enter(B, z, 120)
    tru = C.M.flat_stay(z.real, z.imag, B.c.real, B.c.imag, 300) >= 300
    print('  true inside %d; found a first entry for %d; entry found but truly outside %d; truly inside but no entry %d'
          % (tru.sum(), (n >= 0).sum(), ((n >= 0) & ~tru).sum(), ((n < 0) & tru).sum()))
    ok = n >= 0
    b, db = B.bott(zn[ok])
    print('  |b| at entry: largest %.6f, share above 1: %.5f' % (np.abs(b).max(), (np.abs(b) > 1).mean()))
    g, _ = B.g(zn[ok]); b2, _ = B.bott(g)
    print('  b(p steps) against b^2: worst miss %.2e' % np.abs(b2 - b * b).max())
    e = 1e-6; bp, _ = B.bott(zn[ok] + e); bm, _ = B.bott(zn[ok] - e)
    rel = np.abs((bp - bm) / (2 * e) - db) / np.maximum(np.abs(db), 1e-9); deep = np.abs(b) < 0.98
    print('  derivative against a difference: worst relative miss %.2e (where |b| < 0.98)' % rel[deep].max())
    print('  b at the hanging point alpha (approached from inside):', np.round(B.bott(np.array([B.alpha * 0.999]))[0], 4))
    zz = B.unbott(b[deep][:2000]); print('  unbott(bott(z)) - z: worst %.2e' % np.abs(zz - zn[ok][deep][:2000]).max())
    print('  entry times: %s' % np.bincount(n[ok])[:12])
print('%.0f s' % (time.time() - t0))
