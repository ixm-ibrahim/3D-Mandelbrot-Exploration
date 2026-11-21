"""Round 22, section 'design': shared tools. All orbits are the library's (M.stay); nothing is iterated by hand
except `follow`, which is M.stay's loop handing back the points (checked against M.stay in check1.py)."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
import myrules as D

BAS = (-1.0, 0.0, 0.0); RAB = M.RABBIT


def refs():
    return {'oneplane': M.bench('oneplane'), 'along': M.bench('along'), 'lathe': M.bench('lathe'), 'away': M.bench('away')}


def one(rule, x, y, z, c=(0.0, 0.0, 0.0)):
    """One squaring of fresh orbits (no c added)."""
    x, y, z = (np.asarray(t, float) for t in (x, y, z)); n = x.size
    out = rule.step(x.ravel(), y.ravel(), z.ravel(), tuple(rule.init(n)), 0, np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
    return out[0], out[1], out[2]


def lift_test(rule, c, n=20000, steps=80, lift=1e-6, seed=7):
    """Flat-inside points lifted off the page by `lift`: how many are still inside (a film loses them all)."""
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    ins = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300
    zr, zi = zr[ins], zi[ins]
    st = M.stay(rule, zr, zi, np.full(zr.size, lift), c[0], c[1], c[2], steps) >= steps
    return int(st.sum()), int(zr.size)


def grid(rule, c, n, steps, box=((-1.8, 1.8), (-1.5, 1.5), (-1.5, 1.5))):
    """Inside blocks on an n^3 grid (no grid point on z = 0 when n is even)."""
    xs = [np.linspace(b[0], b[1], n) for b in box]
    out = np.zeros((n, n, n), bool)
    for i in range(n):
        Y, Z = np.meshgrid(xs[1], xs[2], indexing='ij')
        out[i] = M.stay(rule, np.full_like(Y, xs[0][i]), Y, Z, c[0], c[1], c[2], steps) >= steps
    return out


def pieces(vol, bridge=0):
    """Share of the biggest piece, number of pieces, share of blocks in pieces of fewer than 8 blocks (dust)."""
    from scipy import ndimage
    v = ndimage.binary_dilation(vol, iterations=bridge) if bridge else vol
    lab, nl = ndimage.label(v)
    if nl == 0:
        return 0.0, 0, 0.0
    cnt = np.bincount(lab[vol])[1:] if bridge else np.bincount(lab.ravel())[1:]
    cnt = cnt[cnt > 0]; tot = cnt.sum()
    return float(cnt.max() / tot), int(cnt.size), float(cnt[cnt < 8].sum() / tot)


def tile(img, w, h):
    return Image.fromarray(img).resize((w, h), Image.LANCZOS)


def sheet(rules, labels, c, path, title, across=(0.0, -1.0), angles=(0.0, 22.5, 45.0, 90.0), steps=60, cams=((0.45, 0.5, 1.0), (1.0, 0.45, 0.25)),
          sw=300, sh=225, nd=200, ssteps=40, cw=260, ch=190):
    """One row per rule: cuts along pages through the x-axis, cuts across it, the rough solid from two eye positions."""
    pad = 8; t0 = time.time()
    heads = ['page turned %g' % a for a in angles] + ['across x = %g' % x0 for x0 in across] + ['solid, eye %s' % (cm,) for cm in cams]
    tw = [cw] * len(angles) + [ch] * len(across) + [sw] * len(cams)
    W = pad + sum(t + pad for t in tw); H = 50 + len(rules) * (max(ch, sh) + 46)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), title, fill=(240, 240, 245), font=M.font(20))
    for i, (r, lab) in enumerate(zip(rules, labels)):
        y = 50 + i * (max(ch, sh) + 46); d.text((pad, y), lab, fill=(235, 220, 170), font=M.font(15))
        pics = [M.shade(M.cut_axis(r, a, cw, ch, steps, c=c), steps) for a in angles]
        pics += [M.shade(M.cut_across(r, x0, ch, steps, c=c), steps) for x0 in across]
        for cm in cams:
            dep, px = M.solid(r, c, sw, sh, nd, ssteps, cam=cm); pics.append(M.shade_solid(dep, px))
        x = pad
        for hd, pic in zip(heads, pics):
            d.text((x, y + 20), hd, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 38)); x += pic.shape[1] + pad
        print('sheet', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path
