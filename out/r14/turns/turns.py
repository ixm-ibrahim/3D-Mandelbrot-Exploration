# Round 14, "turns": both rules at every step. Stand-alone numpy voxel trial.
#
# Two rules f1(p) = P1(p) + c and f2(p) = P2(p) + c, where P2 is P1 turned 90 degrees about the x-axis.
#   union set  U = points whose orbit stays bounded for SOME order of the two rules
#   common set C = points whose orbit stays bounded for EVERY order
# Both rules square the length, so a point further than Resc = (1 + sqrt(1 + 4|c|)) / 2 from the origin
# escapes under every order. That makes a "pull back" on one grid exact up to the grid's own resolution:
#   S_0 = ball of radius Resc
#   S_d(p) = p in ball  and  ( S_{d-1}(f1 p)  OR / AND  S_{d-1}(f2 p) )
# S_d is the set for depth d (2^d orders, all of them, at the cost of 2 map evaluations per voxel in total).
import numpy as np, time, os
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

S3 = float(np.sqrt(3.0))
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- the rules (power 2), as plain numpy
def E1(x, y, z):
    """Sphere inversions, one plane (MATH.mercator with n = 2, no turn, no lift), in closed form:
    longitude doubles, Mercator latitude doubles, length squares.
    out = r^2 / (r^2 + z^2) * (x^2 - y^2, 2xy, 2 z r)"""
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2)
    den = r2 + z * z
    f = r2 / np.maximum(den, 1e-30)
    return f * (x * x - y * y), f * (2 * x * y), f * (2 * z * r)


def E1_trig(x, y, z):
    """The same, written like MATH.mercator line for line (used only to check E1)."""
    r = np.sqrt(x * x + y * y + z * z)
    Z = np.clip(np.where(r > 0, z / np.maximum(r, 1e-300), 0.0), -0.999999, 0.999999)
    m = np.clip(2 * np.arctanh(Z), -20, 20)
    h = 1 / np.cosh(m)
    R = r * r
    p = np.arctan2(y, x) * 2
    return R * h * np.cos(p), R * h * np.sin(p), R * np.tanh(m)


CAPS = [(0.5, S3 / 2), (-1.0, 0.0), (0.5, -S3 / 2)]   # cap centres a_k on the equator: 60, 180, 300 degrees


def K1(x, y, z):
    """Kleinian squaring H (ROUND14 rules, entry 4), n = 2: three caps of angular radius 60 degrees;
    inside cap k the direction is inverted in the sphere of centre 2 a_k and radius sqrt 3, then y -> -y;
    outside all caps only y -> -y. Length squares."""
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2)
    rs = np.maximum(r, 1e-30)
    dx, dy, dz = x / rs, y / rs, z / rs
    ox, oy, oz = dx.copy(), dy.copy(), dz.copy()
    for ax, ay in CAPS:
        m = (dx * ax + dy * ay) > 0.5
        sx, sy = 2 * ax, 2 * ay
        ux, uy, uz = dx - sx, dy - sy, dz
        k = 3.0 / (ux * ux + uy * uy + uz * uz)
        ox = np.where(m, sx + k * ux, ox)
        oy = np.where(m, sy + k * uy, oy)
        oz = np.where(m, k * uz, oz)
    return r2 * ox, -r2 * oy, r2 * oz


def turned(P):
    """The same rule turned 90 degrees about the x-axis (swap y and z before and after)."""
    def Q(x, y, z):
        a, b, c = P(x, z, y)
        return a, c, b
    return Q


E2 = turned(E1)
K2 = turned(K1)
RULES = {'E': (E1, E2), 'K': (K1, K2)}


def resc(c):
    n = float(np.sqrt(c[0] ** 2 + c[1] ** 2 + c[2] ** 2))
    return (1 + np.sqrt(1 + 4 * n)) / 2


# ---------------------------------------------------------------- Julia sets by pull back
def julia(c, rules, mode, N=193, L=1.7, max_depth=60, verbose=True, dtype=np.float32, sub=1):
    """rules: list of one or two maps. mode: 'union' | 'common' (with one rule both are the same).
    Returns (vol bool [N,N,N] indexed [ix,iy,iz], death uint8 [N,N,N] = the depth at which a voxel left
    (0 = never in the ball, 255 = still in at the end), info dict).
    sub > 1: each voxel is tested at sub^3 points; it counts as inside when ANY of them is (outer estimate)."""
    t0 = time.time()
    R = resc(c)
    assert R <= L * 1.0001, (R, L)
    ax = ((np.arange(N) + 0.5) / N * 2 - 1) * L
    h = 2 * L / N
    X, Y, Z = np.meshgrid(ax.astype(dtype), ax.astype(dtype), ax.astype(dtype), indexing='ij')
    ball = (X * X + Y * Y + Z * Z) <= R * R
    pts = np.flatnonzero(ball.ravel())
    px, py, pz = X.ravel()[pts], Y.ravel()[pts], Z.ravel()[pts]
    del X, Y, Z
    NN = N * N * N
    offs = [0.0] if sub == 1 else list(((np.arange(sub) + 0.5) / sub - 0.5) * h)
    idx = []      # idx[rule][subsample] -> flat voxel index of the image (NN = outside)
    for P in rules:
        per = []
        for ox in offs:
            for oy in offs:
                for oz in offs:
                    qx, qy, qz = P(px + dtype(ox), py + dtype(oy), pz + dtype(oz))
                    qx = qx + dtype(c[0]); qy = qy + dtype(c[1]); qz = qz + dtype(c[2])
                    ok = (qx * qx + qy * qy + qz * qz) <= R * R
                    ix = np.floor((qx + L) / h).astype(np.int64)
                    iy = np.floor((qy + L) / h).astype(np.int64)
                    iz = np.floor((qz + L) / h).astype(np.int64)
                    ok &= (ix >= 0) & (ix < N) & (iy >= 0) & (iy < N) & (iz >= 0) & (iz < N)
                    fl = (ix * N + iy) * N + iz
                    fl[~ok] = NN
                    per.append(fl.astype(np.int32))
        idx.append(per)
    del px, py, pz
    S = np.zeros(NN + 1, dtype=bool)
    S[pts] = True
    death = np.zeros(NN, dtype=np.uint8)
    death[pts] = 255
    alive = np.ones(len(pts), dtype=bool)
    counts = [int(alive.sum())]
    for d in range(1, max_depth + 1):
        new = None
        for per in idx:
            hit = None
            for fl in per:
                s = S[fl]
                hit = s if hit is None else (hit | s)
            if new is None:
                new = hit
            elif mode == 'union':
                new = new | hit
            else:
                new = new & hit
        new &= alive
        died = alive & ~new
        nd = int(died.sum())
        death[pts[died]] = min(d, 254)
        S[pts[died]] = False
        alive = new
        counts.append(int(alive.sum()))
        if nd == 0:
            break
    vol = S[:NN].reshape(N, N, N)
    info = dict(c=tuple(c), N=N, L=L, h=h, depth=d, converged=(nd == 0), counts=counts,
                volume=counts[-1] * h ** 3, seconds=time.time() - t0, mode=mode, sub=sub)
    if verbose:
        print(f'  julia c={tuple(round(float(v), 4) for v in c)} {mode:6s} N={N} depth={d} '
              f'converged={nd == 0} voxels={counts[-1]} volume={info["volume"]:.4f} {info["seconds"]:.1f}s', flush=True)
    return vol, death.reshape(N, N, N), info


# ---------------------------------------------------------------- pictures
def _rot(az, el):
    """Camera: looks at the origin from the direction (cos el cos az, cos el sin az, sin el); z is up."""
    a, e = np.radians(az), np.radians(el)
    w = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])       # toward the camera
    u = np.array([-np.sin(a), np.cos(a), 0.0])                                     # screen right
    v = np.cross(w, u)                                                             # screen up
    return u, v, w


def render(vol, az=-60, el=22, light=(-0.45, 0.55, 0.7), tint=(0.86, 0.78, 0.62), bg=(18, 20, 26), out=None):
    """Orthographic picture of a voxel solid: first hit along the view, normals from the smoothed solid,
    a soft shadowing term from a wider blur. Returns an RGB uint8 array [n, n, 3]."""
    N = vol.shape[0]
    n = out or N
    occ = vol.astype(np.float32)
    u, v, w = _rot(az, el)
    # view space grid (i = right, j = up, k = toward the camera): sample the solid at centre + (i u + j v + k w)
    M = np.stack([u, v, w], axis=1) * (N / n)                 # columns: where a unit step in i, j, k goes
    cen = (N - 1) / 2.0
    off = np.array([cen, cen, cen]) - M @ np.array([(n - 1) / 2.0] * 3)
    sm = ndimage.gaussian_filter(occ, 1.1)
    V = ndimage.affine_transform(sm, M, offset=off, output_shape=(n, n, n), order=1, mode='constant', cval=0.0)
    del sm
    solid = V > 0.5
    anyhit = solid.any(axis=2)
    k0 = (n - 1) - np.argmax(solid[:, :, ::-1], axis=2)      # the solid voxel nearest the camera
    k0 = np.where(anyhit, k0, 0)
    gi, gj, gk = np.gradient(V)
    ta = lambda A: np.take_along_axis(A, k0[:, :, None], axis=2)[:, :, 0]
    nx, ny, nz = -ta(gi), -ta(gj), -ta(gk)
    del gi, gj, gk
    ln = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    # shadowing: how much solid there is near the surface point, a little in front of it
    wide = ndimage.gaussian_filter(V, max(2.0, n / 60.0))
    kf = np.clip(k0 + int(max(2, n / 60.0)), 0, n - 1)
    ao = np.take_along_axis(wide, kf[:, :, None], axis=2)[:, :, 0]
    ao = np.clip(1.25 - 1.9 * ao, 0.25, 1.0)
    l = np.array(light, dtype=float); l /= np.linalg.norm(l)
    diff = np.clip(nx * l[0] + ny * l[1] + nz * l[2], 0, 1)
    rim = np.clip(nz, 0, 1)
    depth = k0 / (n - 1.0)
    shade = (0.22 + 0.68 * diff + 0.10 * rim) * ao * (0.72 + 0.28 * depth)
    img = np.zeros((n, n, 3), dtype=np.float32)
    for ch in range(3):
        img[:, :, ch] = np.where(anyhit, 255 * tint[ch] * shade, bg[ch])
    img = np.clip(img, 0, 255).astype(np.uint8)
    return np.transpose(img, (1, 0, 2))[::-1]                 # rows = up to down, columns = left to right


def slice_img(vol, death=None, plane='z', other=None, bg=(18, 20, 26)):
    """The cut through the middle voxel layer (plane z = 0, or y = 0). Inside: light. Outside: shaded by the
    depth at which the point left. With `other` (a bool image of the same shape, e.g. the flat Julia set):
    its outline is drawn in red on top."""
    N = vol.shape[0]
    m = N // 2
    if plane == 'z':
        a = vol[:, :, m]; dd = None if death is None else death[:, :, m]
    else:
        a = vol[:, m, :]; dd = None if death is None else death[:, m, :]
    img = np.zeros((N, N, 3), dtype=np.float32)
    img[:] = bg
    if dd is not None:
        t = np.clip(dd.astype(np.float32) / 14.0, 0, 1)
        t[dd == 0] = 0
        for ch, col in enumerate((70, 110, 170)):
            img[:, :, ch] = bg[ch] + (col - bg[ch]) * t
    img[a] = (235, 225, 200)
    if other is not None:
        er = ndimage.binary_erosion(other)
        edge = other & ~er
        img[edge] = (255, 60, 60)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return np.transpose(img, (1, 0, 2))[::-1]                 # x to the right, y (or z) up


def flat_julia(cx, cy, N, L, iters=300):
    """The flat Julia set of z^2 + c at the voxel centres of the middle layer: bool [ix, iy]."""
    ax = ((np.arange(N) + 0.5) / N * 2 - 1) * L
    X, Y = np.meshgrid(ax, ax, indexing='ij')
    z = X + 1j * Y
    c = complex(cx, cy)
    inside = np.ones(z.shape, dtype=bool)
    with np.errstate(over='ignore', invalid='ignore'):
        for _ in range(iters):
            z = np.where(inside, z * z + c, z)
            inside &= np.abs(z) <= 4
    return inside


def font(size):
    for name in ('segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def sheet(rows, col_titles, row_titles, path, title=None, cell=None, note=None, fs=17):
    """rows: list of lists of RGB arrays (None = empty). Writes a labelled contact sheet."""
    cell = cell or max(im.shape[0] for r in rows for im in r if im is not None)
    f, fb = font(fs), font(fs + 5)
    left, top, pad = 200, 40 + (44 if title else 0), 6
    foot = 30 * (len(note) if note else 0) + (12 if note else 0)
    W = left + len(col_titles) * (cell + pad) + pad
    H = top + len(rows) * (cell + pad) + pad + foot
    im = Image.new('RGB', (W, H), (10, 11, 15))
    d = ImageDraw.Draw(im)
    if title:
        d.text((12, 8), title, fill=(240, 240, 240), font=fb)
    for j, t in enumerate(col_titles):
        d.text((left + j * (cell + pad) + 4, top - 30), t, fill=(215, 215, 215), font=f)
    for i, r in enumerate(rows):
        y = top + i * (cell + pad)
        for k, line in enumerate(row_titles[i].split('\n')):
            d.text((10, y + 8 + k * (fs + 6)), line, fill=(215, 215, 215), font=f)
        for j, a in enumerate(r):
            if a is None:
                continue
            p = Image.fromarray(a)
            if p.size != (cell, cell):
                p = p.resize((cell, cell), Image.LANCZOS)
            im.paste(p, (left + j * (cell + pad), y))
    if note:
        y = H - foot + 2
        for line in note:
            d.text((12, y), line, fill=(200, 200, 200), font=f); y += 30
    im.save(path)
    return path
