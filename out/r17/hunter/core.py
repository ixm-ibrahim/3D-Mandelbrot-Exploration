"""Round 17, hunter: shared tools. Stand-alone numpy.

Every rule here is homogeneous of degree 2 (F(t v) = t^2 F(v)), so DF(t u) = t DF(u). A resting point v of
v -> F(v) + c has c = v - F(v) and derivative DF(v). Along the ray of direction u the largest eigenvalue size is
t * rho(u), rho(u) = spectral radius of DF(u): the resting point stops attracting at t = 1 / rho(u). So the skin of
the main body is the picture of the sphere of directions under
        u  ->  c(u) = u / rho(u) - F(u) / rho(u)^2 ,
and which eigenvalue is the big one at u says what kind of skin it is there.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))

PCOL = {0: (14, 16, 22), 1: (235, 225, 200), 2: (70, 130, 235), 3: (60, 200, 95), 4: (245, 150, 40), 5: (215, 80, 215),
        6: (60, 210, 220), 7: (240, 230, 70), 8: (160, 110, 240), -1: (150, 150, 155), -2: (120, 60, 60)}
# 0 escaped, 1..24 the period found, -1 stays bounded but no repeat found within 24 steps, -2 other period 9..24


def colour_of(per):
    out = np.zeros(per.shape + (3,), np.uint8)
    for k, col in PCOL.items():
        out[per == k] = col
    out[per >= 9] = PCOL[-2]
    return out


def dirs(theta, phi):
    """theta from the +x axis, phi round the x-axis (0 = the flat plane, +y side)."""
    st = np.sin(theta)
    return np.stack([np.cos(theta), st * np.cos(phi), st * np.sin(phi)], -1)


def apply(F, v):
    X, Y, Z = F(v[..., 0], v[..., 1], v[..., 2])
    return np.stack([X, Y, Z], -1)


def jac(F, v, h=1e-6):
    v = np.asarray(v, float)
    J = np.empty(v.shape + (3,))
    for b in range(3):
        d = np.zeros(3); d[b] = h
        J[..., b] = (apply(F, v + d) - apply(F, v - d)) / (2 * h)
    return J


def skin(F, nth=361, nph=720, th=None, ph=None):
    """Returns a dict over the grid of directions (theta rows, phi columns)."""
    if th is None:
        th = (np.arange(nth) + 0.5) * np.pi / nth
    if ph is None:
        ph = np.arange(nph) * 2 * np.pi / nph
    TH, PH = np.meshgrid(th, ph, indexing='ij')
    u = dirs(TH, PH)
    J = jac(F, u)
    bad = ~np.isfinite(J).all((-1, -2)) | (np.abs(J).max((-1, -2)) > 1e3)
    J[bad] = np.eye(3)
    ev = np.linalg.eigvals(J)
    mod = np.abs(ev)
    k = np.argmax(mod, -1)
    lead = np.take_along_axis(ev, k[..., None], -1)[..., 0]
    rho = np.abs(lead)
    cplx = np.abs(lead.imag) > 1e-7 * rho
    ang = np.abs(np.angle(lead)) / (2 * np.pi)          # 0 .. 0.5 of a turn
    # the size of the other kind of eigenvalue (the real one if the pair leads, the pair or 2nd real if a real leads)
    srt = np.sort(mod, -1)
    isre = np.abs(ev.imag) <= 1e-7 * np.maximum(mod, 1e-12)
    nreal = isre.sum(-1)
    real_mod = np.where(isre, mod, -1).max(-1)           # biggest real eigenvalue size
    pair_mod = np.where(~isre, mod, -1).max(-1)          # size of the pair (or -1)
    pair_ang = np.where(~isre, np.abs(np.angle(ev)), 0).max(-1) / (2 * np.pi)
    Fu = apply(F, u)
    c = u / rho[..., None] - Fu / rho[..., None] ** 2
    det = np.linalg.det(J)
    sv = np.linalg.svd(J, compute_uv=False)
    kind = np.where(cplx, 0, np.where(lead.real < 0, -1, 1))        # 0 pair, -1 real minus one, +1 real plus one
    return dict(th=th, ph=ph, u=u, J=J, ev=ev, rho=rho, kind=kind, ang=ang, c=c, bad=bad, det=det, sv=sv,
                real_mod=real_mod, pair_mod=pair_mod, pair_ang=pair_ang, nreal=nreal, mid=srt[..., 1], low=srt[..., 0])


def normals(c, periodic=True):
    """Outward unit normals of the surface c[theta, phi] (orientation fixed by the caller)."""
    ct = np.gradient(c, axis=0)
    if periodic:
        cp = (np.roll(c, -1, 1) - np.roll(c, 1, 1)) / 2
    else:
        cp = np.gradient(c, axis=1)
    n = np.cross(ct, cp)
    ln = np.linalg.norm(n, axis=-1, keepdims=True)
    return n / np.maximum(ln, 1e-30), ln[..., 0]


def periods(F, c, steps=1500, pmax=24, tol=1e-4, R2=4.0, chunk=400000, start=None):
    """Mandelbrot run: start at v = c (as the bench does). 0 escaped, p = period found, -1 bounded without repeat."""
    sh = c.shape[:-1]
    C = c.reshape(-1, 3)
    out = np.zeros(C.shape[0], np.int16)
    for a in range(0, C.shape[0], chunk):
        cc = C[a:a + chunk]
        idx = np.arange(cc.shape[0])
        v = cc.copy() if start is None else np.broadcast_to(start, cc.shape).copy()
        ok = np.isfinite(v).all(1) & ((v * v).sum(1) <= R2)
        idx, v = idx[ok], v[ok]
        for k in range(steps):
            if idx.size == 0:
                break
            v = apply(F, v) + cc[idx]
            keep = (v * v).sum(1) <= R2
            if not keep.all():
                idx, v = idx[keep], v[keep]
        if idx.size == 0:
            continue
        ref = v.copy(); per = np.full(idx.size, -1, np.int16)
        for p in range(1, pmax + 1):
            v = apply(F, v) + cc[idx]
            hit = (per < 0) & (np.abs(v - ref).max(1) < tol)
            per[hit] = p
        keep = (v * v).sum(1) <= R2
        per[~keep] = 0
        out[a + idx] = per
    return out.reshape(sh)


# ------------------------------------------------------------------ a small renderer for labelled voxel solids
def camera(az, el):
    """View direction d (into the scene), right r, up w. az turns round z, el lifts the eye."""
    a, e = np.radians(az), np.radians(el)
    eye = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    d = -eye
    r = np.cross(d, [0, 0, 1.0]); r = r / np.linalg.norm(r) if np.linalg.norm(r) > 1e-9 else np.array([0.0, 1.0, 0.0])
    w = np.cross(r, d)
    return d, r, w


def render(lab, lo, h, az, el, S=420, half=None, centre=None, curves=(), light=(-0.4, 0.5, 0.75)):
    """lab: int array [ix, iy, iz], 0 = empty. lo: corner (3), h: voxel size. curves: list of (points (n,3), colour, size)."""
    n = np.array(lab.shape)
    hi = np.asarray(lo) + (n - 1) * h
    centre = (np.asarray(lo) + hi) / 2 if centre is None else np.asarray(centre, float)
    half = 0.5 * np.linalg.norm(hi - np.asarray(lo)) * 0.62 if half is None else half
    d, r, w = camera(az, el)
    a = (np.arange(S) + 0.5) / S * 2 - 1
    A, B = np.meshgrid(a, -a)                       # image x to the right, y up
    org = centre + half * (A[..., None] * r + B[..., None] * w) - 2.2 * half * d
    depth = np.full((S, S), np.inf); hitlab = np.zeros((S, S), lab.dtype)
    dt = h * 0.5
    nstep = int(4.4 * half / dt)
    live = np.ones((S, S), bool)
    for k in range(nstep):
        p = org + (k * dt) * d
        ijk = np.rint((p - lo) / h).astype(np.int32)
        ok = live & (ijk >= 0).all(-1) & (ijk < n).all(-1)
        if not ok.any():
            continue
        L = np.zeros((S, S), lab.dtype)
        L[ok] = lab[ijk[ok, 0], ijk[ok, 1], ijk[ok, 2]]
        new = ok & (L != 0)
        depth[new] = k * dt; hitlab[new] = L[new]; live &= ~new
    img = np.zeros((S, S, 3), np.float32); img[:] = (14, 16, 22)
    hit = np.isfinite(depth)
    from scipy import ndimage as ndi
    dz = np.where(hit, depth, np.nan)
    dzs = ndi.uniform_filter(np.where(hit, depth, 0.0), 3) / np.maximum(ndi.uniform_filter(hit.astype(float), 3), 1e-9)
    px = 2 * half / S
    gx = np.gradient(dzs, axis=1) / px; gy = -np.gradient(dzs, axis=0) / px
    nrm = gx[..., None] * r + gy[..., None] * w - d
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    lt = -d + 0.55 * w - 0.45 * r; lt /= np.linalg.norm(lt)          # light from over the viewer's left shoulder
    sh = 0.42 + 0.58 * np.clip((nrm * lt).sum(-1), 0, 1)
    col = colour_of(hitlab.astype(np.int16)).astype(np.float32)
    img[hit] = (col * sh[..., None])[hit]
    for pts, colr, size in curves:
        if len(pts) == 0:
            continue
        q = np.asarray(pts) - centre
        sx = (q @ r) / half; sy = (q @ w) / half; sd = q @ d + 2.2 * half
        ix = np.floor((sx + 1) / 2 * S).astype(int); iy = np.floor((1 - sy) / 2 * S).astype(int)
        ok = (ix >= 0) & (ix < S) & (iy >= 0) & (iy < S)
        ix, iy, sd = ix[ok], iy[ok], sd[ok]
        vis = sd <= np.where(np.isfinite(depth[iy, ix]), depth[iy, ix], 1e9) + 3.0 * h
        for dx in range(-size, size + 1):
            for dy in range(-size, size + 1):
                xx = np.clip(ix[vis] + dx, 0, S - 1); yy = np.clip(iy[vis] + dy, 0, S - 1)
                img[yy, xx] = colr
    return np.clip(img, 0, 255).astype(np.uint8)


def font(s):
    from PIL import ImageFont
    for nme in ('segoeui.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(nme, s)
        except OSError:
            pass
    return ImageFont.load_default()
