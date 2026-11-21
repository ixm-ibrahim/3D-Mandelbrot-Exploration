"""Round 16 bench, stage 2: the Mandelbrot solid, and the three warning-light Julia sets.
Both REFUSE a rule whose stage 1 (the basilica) has not passed: that is the user's order of work.
Run through bench.py:  python out/r16/bench/bench.py stage2 <rule>   |   python out/r16/bench/bench.py lights <rule>
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules as R, bench as B
turns = R.turns

MC = (-0.55, 0.0, 0.0); ML = 1.5; MSTEPS = 50          # the box of the Mandelbrot solid: x in [-2.05, 0.95], y and z in [-1.5, 1.5]
TOUCH = -0.75                                          # where the main body and the period-2 body of the flat set touch
LIGHTS = [('rabbit', (-0.12, 0.74, 0.0)), ('c_-1_0.15_0.1', (-1.0, 0.15, 0.1)), ('c_-0.6_0.3_0.3', (-0.6, 0.3, 0.3))]


def need_stage1(name):
    if not B.passed_stage1(name):
        B.log('[%s] REFUSED: stage 1 (the basilica) has not passed. Stage 2 and the warning lights are only for rules that passed.' % name)
        return False
    return True


def stage2(name, N=193):
    if not need_stage1(name):
        return None
    F = R.get(name); t0 = time.time(); res = dict(rule=name)
    kw = dict(mandel=True, steps=MSTEPS)
    # M1: the cut at z = 0 against the flat Mandelbrot set
    ins, death = B.cut(F, 'z', L=ML, n=801, centre=(MC[0], 0.0), **kw); flat = B.flat_set(L=ML, n=801, steps=MSTEPS, mandel=True, centre=(MC[0], 0.0))
    res['M1'] = dict(differ=int((ins ^ flat).sum()), flat_points=int(flat.sum()))
    B.save_tile(name, 'm_cut_z0', B.cut_img(ins, death))
    i2, d2 = B.cut(F, 'y', L=ML, n=601, centre=(MC[0], 0.0), **kw); B.save_tile(name, 'm_cut_y0', B.cut_img(i2, d2))
    flat6 = B.flat_set(L=ML, n=601, steps=MSTEPS, mandel=True, centre=(MC[0], 0.0))
    res['cut_y0_against_flat'] = dict(differ=int((i2 ^ flat6).sum()), flat_points=int(flat6.sum()))
    # M3: thin leaf or body: how full the cut x = -0.2 is inside its bounding circle
    ix, dx = B.cut(F, 'x', -0.2, L=ML, n=601, **kw); B.save_tile(name, 'm_cut_x', B.cut_img(ix, dx))
    b = np.linspace(-ML, ML, 601); rho2 = b[:, None] ** 2 + b[None, :] ** 2
    rmax = float(np.sqrt(rho2[ix].max())) if ix.any() else 0.0
    res['M3'] = dict(cut_x_fill_pct=float(100 * ix.sum() * (b[1] - b[0]) ** 2 / max(np.pi * rmax ** 2, 1e-12)), reach=rmax)
    # M4: the period-2 body: attached at a point or along a patch
    it, _ = B.cut(F, 'x', TOUCH, L=0.6, n=601, **kw); bt = np.linspace(-0.6, 0.6, 601); disc = (bt[:, None] ** 2 + bt[None, :] ** 2) <= 0.1 ** 2
    Nl, Ll = 161, 0.5
    loc = B.volume(F, Nl, L=Ll, centre=(TOUCH, 0, 0), **kw); hl = 2 * Ll / (Nl - 1)
    al = np.linspace(-Ll, Ll, Nl); dd = al[:, None, None] ** 2 + al[None, :, None] ** 2 + al[None, None, :] ** 2
    ia, ib, mm = int(round((0.40 + Ll) / hl)), int(round((-0.25 + Ll) / hl)), Nl // 2
    split = None
    for r in (0.02, 0.03, 0.04, 0.06, 0.08, 0.12, 0.16, 0.24, 0.32):
        lab, _n = ndimage.label(loc & (dd > r * r))
        if lab[ia, mm, mm] == 0 or lab[ib, mm, mm] == 0 or lab[ia, mm, mm] != lab[ib, mm, mm]:
            split = r; break
    res['M4'] = dict(cut_fill_near_touch_pct=float(100 * it[disc].mean()), smallest_ball_that_splits=split)
    B.log('[%s] M1 %s M3 %s M4 %s  (%.0f s)' % (name, res['M1'], res['M3'], res['M4'], time.time() - t0))
    # the solid
    vol = B.volume(F, N, L=ML, centre=MC, **kw); h = 2 * ML / (N - 1); m = N // 2
    res['volume'] = float(vol.sum() * h ** 3)
    for tag, az, el in (('m_front', -60, 22), ('m_above', -60, 75), ('m_alongx', 0, 0), ('m_below', -60, -40)):
        B.save_tile(name, tag, turns.render(vol, az=az, el=el))
    lab, n = ndimage.label(vol, structure=B.FULL); sz = np.bincount(lab.ravel())[1:]
    fat = ndimage.binary_dilation(vol, structure=B.FULL); lab2, n2 = ndimage.label(fat, structure=B.FULL); s2 = np.bincount(lab2[vol], minlength=n2 + 1)[1:]
    res['M2'] = dict(pieces=int(n), biggest_pct=float(100 * sz.max() / max(vol.sum(), 1)), biggest_pct_one_voxel_gap_allowed=float(100 * s2.max() / max(vol.sum(), 1)))
    v = float(max(vol.sum(), 1))
    res['M7'] = dict(changed_by_mirror_z_pct=float(100 * (vol ^ vol[:, :, ::-1]).sum() / v), changed_by_mirror_y_pct=float(100 * (vol ^ vol[:, ::-1, :]).sum() / v),
                     above_over_below=float(vol[:, :, m + 1:].sum() / max(vol[:, :, :m].sum(), 1)))
    vt = B.volume(F, N, L=ML, centre=MC, turn=45.0, **kw)
    res['M7']['changed_by_turn_45_pct'] = float(100 * (vol ^ vt).sum() / v)
    # M5, M6: wear the solid down by 0.12 and look at what comes off the main body (x > -0.75)
    org = [MC[0] - ML, -ML, -ML]; rv = 0.12 / h
    op, rs = B.wear(vol, rv); lab1, ps = B.pieces(rs, h, org)
    ps = [p for p in ps if p['voxels'] >= B.vmin(rv) and p['centre'][0] > TOUCH]
    rings = [p for p in ps if p['extent'] >= 300 and p['rho'] > 0.15]
    buds = [p for p in ps if not (p['extent'] >= 300) and p['rho'] > 0.1]
    for p in buds:
        p['off'] = bool(abs(np.sin(np.radians(p['phi']))) > B.SIN20)
    off = [p for p in buds if p['off']]
    res['M5'] = dict(wear_radius=0.12, pieces_off_main_body=len(buds), off_flat_plane=len(off), rings=len(rings),
                     directions_of_biggest=[round(p['phi']) for p in buds[:10]], sizes_of_biggest=[round(p['r_eq'], 3) for p in buds[:10]],
                     roundness_of_biggest=[round(p['round'], 2) for p in buds[:10]],
                     worn_off_share_pct=float(100 * rs.sum() / v))
    res['M6'] = dict(roundness_1=B.roundness(buds + rings))
    cand = off or buds
    if cand:
        b1 = cand[0]; pt = B.piece_point(lab1, b1, h, org); L2 = float(np.clip(2.2 * b1['r_eq'], 0.10, 0.35))
        v2 = B.volume(F, 129, L=L2, centre=pt, **kw)
        B.save_tile(name, 'm_close', turns.render(v2, az=-60, el=22))
        o2, _l, subs = B.on_centre_body(v2, L2, pt, 'bud', pt)
        res['M5']['on_one_piece'] = dict(centre=[round(x, 3) for x in pt], sub_buds=o2['sub_buds'], sub_buds_off_plane=o2['sub_buds_off_plane'])
        res['M6'].update(roundness_2=o2['roundness'], evenness_2=o2.get('skin_evenness'))
    B.log('[%s] M2 %s\n M5 %s\n M6 %s\n M7 %s  (%.0f s)' % (name, res['M2'], res['M5'], res['M6'], res['M7'], time.time() - t0))
    res['seconds'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'results', name + '-stage2.json'), 'w'), indent=1)
    return res


def load2(name):
    p = os.path.join(HERE, 'results', name + '-stage2.json')
    return json.load(open(p)) if os.path.exists(p) else None


def verdicts2(r):
    """Pass / fail lines for the Mandelbrot solid. M1, M2, M7 use the stage 1 thresholds. M3 to M6 could NOT be
    calibrated on rules with a known verdict (stage 2 may only be run on stage 1 passers): the picture decides."""
    v = {}
    v['M1'] = (r['M1']['differ'] <= 8, 'Cut at z = 0 is the flat Mandelbrot set', '%d of %d points differ' % (r['M1']['differ'], r['M1']['flat_points']))
    v['M2'] = (r['M2']['biggest_pct_one_voxel_gap_allowed'] >= B.T_J5, 'One piece', 'biggest piece holds %.3f %% (a one-voxel gap allowed; %.2f %% with none allowed, %d pieces)' % (
        r['M2']['biggest_pct_one_voxel_gap_allowed'], r['M2']['biggest_pct'], r['M2']['pieces']))
    v['M3'] = (r['M3']['cut_x_fill_pct'] >= 35, 'A body, not thin leaves', 'the cut at x = -0.2 fills %.0f %% of the circle round it' % r['M3']['cut_x_fill_pct'])
    s = r['M4']['smallest_ball_that_splits']
    v['M4'] = (s is not None and s <= 0.04, 'The period-2 body sits on the main body at one point (as in the flat set)',
               '%s; the cut through the touching point is %.0f %% full within 0.1 of the axis' % (
                   ('a ball of radius %.2f must be taken out to part them' % s) if s else 'even a ball of radius 0.32 does not part them', r['M4']['cut_fill_near_touch_pct']))
    m5 = r['M5']; dirs, rnd = m5['directions_of_biggest'], m5['roundness_of_biggest']
    nround = sum(1 for d, q in zip(dirs, rnd) if abs(np.sin(np.radians(d))) > B.SIN20 and q >= B.T_J8_ROUND)
    v['M5'] = (nround >= 2 and m5['rings'] == 0, 'Smaller round bodies on the main body, off the flat plane, no rings',
               '%d pieces come off the main body when it is worn down by 0.12, %d of them off the flat plane, %d of those round (roundness of the biggest: %s); %d go all the way round the axis' % (
                   m5['pieces_off_main_body'], m5['off_flat_plane'], nround, ', '.join('%.2f' % q for q in rnd[:8]), m5['rings']))
    r1, r2 = r['M6'].get('roundness_1'), r['M6'].get('roundness_2')
    v['M6'] = (r1 is not None and r2 is not None and min(r1, r2) >= B.T_J8_ROUND, 'Skin: bodies, not ridges or fins',
               'what comes off is round to %s, close up %s (1 = balls; under %.2f = ridges, fins, sheets)' % ('none' if r1 is None else '%.2f' % r1, 'none' if r2 is None else '%.2f' % r2, B.T_J8_ROUND))
    mz, my = r['M7']['changed_by_mirror_z_pct'], r['M7']['changed_by_mirror_y_pct']
    v['M7'] = (max(mz, my) <= 0.5, 'Not lopsided', 'mirror above/below changes %.2f %%, front/back %.2f %%' % (mz, my))
    return v


def lights(name, N=161, steps=40):
    if not need_stage1(name):
        return None
    F = R.get(name); out = {}
    for tag, c in LIGHTS:
        vol = B.volume(F, N, c=c, steps=steps); h = 3.5 / (N - 1)
        lab, n = ndimage.label(vol, structure=B.FULL); sz = np.bincount(lab.ravel())[1:]
        out[tag] = dict(c=list(c), volume=float(vol.sum() * h ** 3), pieces=int(n), biggest_pct=float(100 * sz.max() / vol.sum()) if n else 0.0)
        B.save_tile(name, 'light_' + tag, turns.render(vol, az=-60, el=22))
        i2, d2 = B.cut(F, 'z', n=401, c=c, steps=steps); B.save_tile(name, 'light_' + tag + '_z0', B.cut_img(i2, d2))
        B.log('[%s] warning light %s %s' % (name, tag, out[tag]))
    json.dump(out, open(os.path.join(HERE, 'results', name + '-lights.json'), 'w'), indent=1)
    return out
