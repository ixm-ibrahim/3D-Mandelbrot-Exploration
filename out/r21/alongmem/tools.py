"""Measuring tools of agent 'alongmem' (round 21). Everything is point by point through M.stay.

    numbers(rule)   one dict of numbers for a rule (see the keys below)
"""
import os, sys, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M

BAS = (-1.0, 0.0, 0.0); RAB = M.RABBIT; SIE = M.SIEGEL
_s = np.sqrt(complex(1 - 4 * RAB[0], -4 * RAB[1])); ALPHA = ((1 - _s) / 2)          # the rabbit's pinch point (three bodies meet)
ALPHA = (ALPHA.real, ALPHA.imag)


def grid(rule, c, N=97, steps=30, L=1.75):
    a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    return M.stay(rule, X, Y, Z, c[0], c[1], c[2], steps) >= steps


def volume(rule, c, N=97, steps=30, L=1.75):
    return float(grid(rule, c, N, steps, L).mean() * (2 * L) ** 3)


def pieces(vol, erode=0):
    """Connected pieces (blocks touching by a face). With erode > 0 the solid is first shaved by that many blocks, so
    that bodies joined by thin necks come apart while a lump stays one piece. Returns (number of pieces that hold more
    than 3 % of what is left, share of the biggest piece, share of the solid that is NOT in the biggest piece
    before shaving = dust and debris)."""
    lab, n = ndimage.label(vol)
    if n == 0:
        return 0, 0.0, 0.0
    cnt = np.bincount(lab.ravel())[1:]; debris = 1 - cnt.max() / cnt.sum()
    v = ndimage.binary_erosion(vol, iterations=erode) if erode else vol
    lab, n = ndimage.label(v)
    if n == 0:
        return 0, 0.0, float(debris)
    cnt = np.bincount(lab.ravel())[1:]
    return int((cnt > 0.03 * cnt.sum()).sum()), float(cnt.max() / cnt.sum()), float(debris)


def arcs(rule, c=BAS, x0=0.0, radii=(0.56, 0.60, 0.64, 0.68, 0.72), n=1440, steps=40):
    """On circles round the x-axis at x = x0: the share of the circle that is inside, and the number of separate
    inside arcs. The flat basilica has a bud at (0, +-0.64): a ring gives share 1 and one arc, along gives 8 arcs."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False); out = []
    for r in radii:
        ins = M.stay(rule, np.full(n, x0), r * np.cos(a), r * np.sin(a), c[0], c[1], c[2], steps) >= steps
        na = int((ins & ~np.roll(ins, 1)).sum()); out.append((r, float(ins.mean()), na if not ins.all() else 1))
    return out


def thick(rule, c, p, n=801, H=0.8, steps=40):
    """Thickness of the solid on the line through the flat-page point p straight up and down (z from -H to H):
    the total length inside, and the length of the inside stretch that holds z = 0 (0 if p itself is outside)."""
    z = np.linspace(-H, H, n); ins = M.stay(rule, np.full(n, p[0]), np.full(n, p[1]), z, c[0], c[1], c[2], steps) >= steps
    dz = z[1] - z[0]; m = n // 2; run = 0
    if ins[m]:
        i = m
        while i < n and ins[i]:
            i += 1
        j = m
        while j >= 0 and ins[j]:
            j -= 1
        run = i - j - 1
    return float(ins.sum() * dz), float(run * dz)


def near(rule, c, p, rad=0.12, n=20000, steps=40, seed=7, zmin=0.03):
    """Share of the ball of radius rad round the flat-page point p that is inside, NOT counting the slab |z| < zmin
    next to the flat page. Round a pinch point of separate bodies this is small; inside a lump it is near 1."""
    rng = np.random.default_rng(seed); v = rng.normal(size=(n, 3)); v *= (rad * rng.uniform(0, 1, n) ** (1 / 3) / np.linalg.norm(v, axis=1))[:, None]
    v = v[np.abs(v[:, 2]) > zmin]
    ins = M.stay(rule, p[0] + v[:, 0], p[1] + v[:, 1], v[:, 2], c[0], c[1], c[2], steps) >= steps
    return float(ins.mean())


def numbers(rule, full=True):
    t0 = time.time(); out = {'name': rule.name}
    f = M.flat_check(rule, n=20000); out['flat'] = (f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'])
    s = M.spun_check(rule, n=20000); out['spun'] = (s['mandel_differ'], s['basilica_differ'], s['mandel_inside'], s['basilica_inside'])
    gb = grid(rule, BAS); gr = grid(rule, RAB)
    out['bas_vol30'] = float(gb.mean() * 3.5 ** 3); out['rab_vol30'] = float(gr.mean() * 3.5 ** 3)
    out['bas_pieces'] = pieces(gb, 0); out['rab_pieces'] = pieces(gr, 0); out['rab_shaved'] = pieces(gr, 2)
    out['bas_shaved'] = pieces(gb, 2)
    out['arcs'] = arcs(rule)
    out['rab_alpha'] = near(rule, RAB, ALPHA); out['rab_centre'] = near(rule, RAB, (0.0, 0.0))
    out['rab_thick_alpha'] = thick(rule, RAB, ALPHA); out['rab_thick_0'] = thick(rule, RAB, (0.0, 0.0))
    if full:
        out['bas_vol80'] = volume(rule, BAS, steps=80); out['rab_vol80'] = volume(rule, RAB, steps=80)
        out['sie_vol30'] = volume(rule, SIE, steps=30); out['sie_vol80'] = volume(rule, SIE, steps=80)
    out['secs'] = time.time() - t0
    return out


def line(o):
    a = o['arcs']; s = '%-11s flat %d/%d/%d/%d stray %.0e | turned: M %.1f%% bas %.1f%% | ' % (o['name'], *o['flat'][:4], o['flat'][4], 100 * o['spun'][0], 100 * o['spun'][1])
    s += 'bas vol %.2f' % o['bas_vol30'] + (' ->80: %.2f' % o['bas_vol80'] if 'bas_vol80' in o else '') + ' debris %.1f%% shaved pieces %d (biggest %.0f%%) | ' % (100 * o['bas_pieces'][2], o['bas_shaved'][0], 100 * o['bas_shaved'][1])
    s += 'arcs r=.60/.64/.68: %d (%.0f%%) %d (%.0f%%) %d (%.0f%%) | ' % (a[1][2], 100 * a[1][1], a[2][2], 100 * a[2][1], a[3][2], 100 * a[3][1])
    s += 'rab vol %.2f' % o['rab_vol30'] + (' ->80: %.2f' % o['rab_vol80'] if 'rab_vol80' in o else '') + ' debris %.1f%% shaved pieces %d (biggest %.0f%%) pinch-ball %.0f%% centre-ball %.0f%% thick@pinch %.2f thick@0 %.2f' % (
        100 * o['rab_pieces'][2], o['rab_shaved'][0], 100 * o['rab_shaved'][1], 100 * o['rab_alpha'], 100 * o['rab_centre'], o['rab_thick_alpha'][0], o['rab_thick_0'][0])
    if 'sie_vol30' in o:
        s += ' | siegel vol %.2f ->80: %.2f' % (o['sie_vol30'], o['sie_vol80'])
    return s
