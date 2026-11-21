"""Judge: respace's "way A" (the balls object's bulbs carried onto the true flat picture), set up for my own measuring.

Way A sends a point (flat point z0, height h) to the round frame (X, Y, Z) = (-Re b, -Im b, |A| h), where b and A
depend on the flat point only (b = the natural coordinate of the body the point stands over, A = its magnification).
So b and A are tabulated once on a fine flat grid (step 0.001, from respace's own carry.enter / Body.bott, which are
the object under test), and every 3D question is answered by looking the flat point up (nearest grid point) and
asking MY recipe of the balls object (jlib.balls) plus respace's family test (carry.own_family).

    python jcarry.py build        writes cache/tab-c1.npz and cache/tab-rabbit.npz
"""
import os, sys, time
import numpy as np
import jlib as J
sys.path.insert(0, os.path.join(J.ROOT, 'out', 'r27', 'respace'))
import carry as C

RAD = C.RAD; STEP = 0.001; X0, X1, Y0, Y1 = -1.85, 1.85, -1.35, 1.35
BODIES = {'c1': C.BASILICA, 'rabbit': C.RABBIT}
CACHE = os.path.join(J.HERE, 'cache')


def build(key, nmax=80, chunk=250000):
    body = BODIES[key]; xs = np.arange(X0, X1 + STEP / 2, STEP); ys = np.arange(Y1, Y0 - STEP / 2, -STEP)
    gx, gy = np.meshgrid(xs, ys); z0 = (gx + 1j * gy).ravel(); n = z0.size
    ok = np.zeros(n, bool); X = np.zeros(n, np.float32); Y = np.zeros(n, np.float32); A = np.zeros(n, np.float32); N = np.full(n, -1, np.int16)
    t0 = time.time()
    for s in range(0, n, chunk):
        zz = z0[s:s + chunk]; cand = np.abs(zz) < 2.1
        if not cand.any():
            continue
        nn, zn, d1, _alive = C.enter(body, zz[cand], nmax)
        good = nn >= 0; idx = s + np.flatnonzero(cand)[good]
        if good.any():
            b, db = body.bott(zn[good]); a = np.abs(db) * d1[good]
            fin = np.isfinite(b) & np.isfinite(a)
            ok[idx] = fin; X[idx] = np.where(fin, -b.real, 0); Y[idx] = np.where(fin, -b.imag, 0); A[idx] = np.where(fin, a, 0); N[idx] = nn[good]
        if (s // chunk) % 8 == 0:
            print('   %s: %d of %d flat points, %.0f s' % (key, s, n, time.time() - t0)); sys.stdout.flush()
    os.makedirs(CACHE, exist_ok=True); sh = gx.shape
    np.savez_compressed(os.path.join(CACHE, 'tab-%s.npz' % key), ok=ok.reshape(sh), X=X.reshape(sh), Y=Y.reshape(sh), A=A.reshape(sh), N=N.reshape(sh))
    print('%s: table %s, %d flat points stand over a body (%.4f of the table), %.0f s' % (key, sh, int(ok.sum()), ok.mean(), time.time() - t0))


class Tab:
    def __init__(self, key):
        d = np.load(os.path.join(CACHE, 'tab-%s.npz' % key)); self.ok, self.X, self.Y, self.A, self.N = d['ok'], d['X'], d['Y'], d['A'], d['N']
        self.h, self.w = self.ok.shape; self.key = key

    def look(self, x, y):
        i = np.rint((np.asarray(x) - X0) / STEP).astype(np.int64); j = np.rint((Y1 - np.asarray(y)) / STEP).astype(np.int64)
        v = (i >= 0) & (i < self.w) & (j >= 0) & (j < self.h); i = np.where(v, i, 0); j = np.where(v, j, 0)
        return v & self.ok[j, i], self.X[j, i].astype(float), self.Y[j, i].astype(float), self.A[j, i].astype(float), self.N[j, i]

    def frame(self, x, y, z):
        """(over a body?, the point in the round frame of that body)."""
        ok, X, Y, A, _n = self.look(x, y)
        return ok, X, Y, A * np.asarray(z, float)

    def inside(self, x, y, z, rounds=14, parts=False):
        """Way A's verdict. parts=True: also say whether the point is in the base body or in a bulb standing on it."""
        sh = np.shape(x); x, y, z = (np.asarray(v, float).ravel() for v in np.broadcast_arrays(x, y, z))
        ok, X, Y, Z = self.frame(x, y, z); r2 = X * X + Y * Y + Z * Z
        base = ok & (r2 < 1.0); out = base.copy()
        cand = np.flatnonzero(ok & (r2 >= 1.0) & (r2 < 2.3))               # the biggest bulb reaches 1.44 from the middle: 1.44^2 = 2.07
        if cand.size:
            ins = J.balls(RAD * X[cand], RAD * Y[cand], RAD * Z[cand], rounds=rounds) == 1
            if ins.any():
                ins[ins] = C.own_family(RAD * X[cand][ins], RAD * Y[cand][ins], RAD * Z[cand][ins])
            out[cand] = ins
        if parts:
            return out.reshape(sh), base.reshape(sh)
        return out.reshape(sh)


if __name__ == '__main__':
    for key in (sys.argv[2:] or ['c1', 'rabbit']):
        build(key)
