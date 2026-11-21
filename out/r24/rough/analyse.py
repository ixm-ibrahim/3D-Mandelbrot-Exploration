"""Round 24, rough, step 1: does the thin scrap sit where the squeezes of several steps have multiplied?

    python out/r24/rough/analyse.py rule:set,rule:set,... [ball]    -> cache/trl-<rule>-<set>.npz, prints the tables, merges cache/analyse.json

For every inside block (side 0.02, 80 steps) the orbit of its centre is followed, with the 3 x 3 matrix of every step,
until it LANDS. Two ways of saying "lands":
   lump (default)  it enters a MAIN LUMP: the part of the inside that can be seen from a point of the attracting
                   cycle along a straight line that stays inside (the body round each cycle point, without what hangs on it)
   ball            it comes within 0.15 of the attracting cycle (the first try; it counts the steps INSIDE the main
                   bodies too, and those turn out to be harmless: see NOTES.md)
Per block:
   steps   steps before landing (0 = the block is in a main lump)
   off     of those, the steps taken from more than 12 degrees off the flat plane
   total   total squeeze: how many times as long as thick the little ellipsoid at the block is that those steps
           together turn into a ball at the landing place
   thin    the block is removed by peeling one block off the solid and growing it back (round 23's "thin scrap")
Bodies: lumps of 6+ blocks left after peeling two blocks off (round 23's "bodies"), with their long : thick.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage as ndi
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rl as L
S26 = np.ones((3, 3, 3), bool); S6 = ndi.generate_binary_structure(3, 1)
BINS = (1.0, 1.5, 2.5, 5.0, 10.0, 30.0, 1e30)


def widths(idx):
    p = np.array(idx, float).T * L.H; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + 3 * L.H


def grids(name, sname):
    n = L.blocks(name, sname); ins = n >= 80
    thin = ins & ~(ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6), structure=S6) & ins)
    return ins, thin, ndi.distance_transform_edt(ins) * L.H


def traced(name, sname, mode='lump', redo=False):
    path = os.path.join(L.CACHE, 'tr%s-%s-%s.npz' % ('l' if mode == 'lump' else '', name, sname))
    if os.path.exists(path) and not redo:
        return dict(np.load(path))
    r = L.get(name); c = L.SETS[sname]; ins, thin, edt = grids(name, sname)
    cyc, _ = L.find_cycle(r, c)
    idx = np.nonzero(ins); P = L.centres(idx); N = P.shape[0]
    rng = np.random.default_rng(4); pick = np.arange(N) if N <= 160000 else np.sort(rng.choice(N, 160000, replace=False))
    out = dict(pick=pick, N=N, cyc=cyc, thin=thin[idx][pick], edt=edt[idx][pick], ix=idx[0][pick].astype(np.int16), iy=idx[1][pick].astype(np.int16), iz=idx[2][pick].astype(np.int16))
    landed = None
    if mode == 'lump':
        star = L.star_lumps(ins, cyc); out['lump_share'] = float(star.sum() / max(ins.sum(), 1))
        landed = lambda u: L.lookup(star, u)
    parts = []
    for i0 in range(0, pick.size, 40000):
        parts.append(L.trace(r, P[pick[i0:i0 + 40000]], c, cyc, steps=40, landed=landed))
    for k in parts[0]:
        out[k] = np.concatenate([p[k] for p in parts])
    out['land_edt'] = L.lookup(edt, np.where(np.isfinite(out['land']), out['land'], 99.0))
    np.savez_compressed(path, **out)
    return out


def bodies(name, sname, t):
    """Round 23's bodies (peel two blocks, lumps of 6+): long : thick, and the steps / total squeeze of each body's middle."""
    n = L.blocks(name, sname); ins = n >= 80
    core = ndi.binary_erosion(ins, structure=S6, iterations=2); clab, ck = ndi.label(core, structure=S6)
    if ck == 0:
        return []
    size = np.bincount(clab.ravel())[1:]; objs = ndi.find_objects(clab)
    lab_at = clab[t['ix'].astype(int), t['iy'].astype(int), t['iz'].astype(int)]; rows = []
    for b in range(1, ck + 1):
        if size[b - 1] < 6:
            continue
        sl = objs[b - 1]; sub = clab[sl] == b; ii = np.nonzero(sub); wd = widths(ii)
        m = (lab_at == b) & (t['settle'] >= 0)
        if m.sum() < 3:
            continue
        s = t['settle'][m]; mid = m.copy(); mid[m] = s <= s.min()               # the middle: the blocks that land first
        rows.append(dict(size=int(size[b - 1]), ratio=float(wd[0] / wd[2]), off=float(np.median(t['off'][mid])), settle=int(s.min()), total=float(np.median(t['total'][mid]))))
    return rows


def tables(name, sname, t, mode='lump', quiet=False):
    ok = t['settle'] >= 0; thin = t['thin'].astype(bool); tot = t['total']; off = t['off']; st = t['settle']; res = dict(rule=name, set=sname, mode=mode)
    res['inside_blocks'] = int(t['N']); res['landed_share'] = float(ok.mean()); res['thin_share'] = float(thin.mean())
    main = ok & (st == 0); hang = ok & (st > 0)
    res['main_share'] = float(main.mean()); res['main_thin'] = float(thin[main].mean()) if main.any() else None
    res['hang_share'] = float(hang.mean()); res['hang_thin'] = float(thin[hang].mean()) if hang.any() else None
    res['thin_in_main'] = float((thin & main).sum() / max(thin.sum(), 1)); res['thin_never'] = float((thin & ~ok).sum() / max(thin.sum(), 1))
    res['total_median_hang'] = float(np.median(tot[hang])) if hang.any() else None

    def row(m):
        return (float(m.mean()), float(thin[m].mean()) if m.any() else None, float(np.median(tot[m])) if m.any() else None, float(np.percentile(tot[m], 90)) if m.any() else None,
                float(np.median(t['edt'][m])) if m.any() else None)
    res['by_steps'] = [(k,) + row(ok & ((st == k) if k < 6 else (st >= 6))) for k in range(0, 7)]
    res['by_off'] = [(k,) + row(hang & ((off == k) if k < 5 else (off >= 5))) for k in range(0, 6)]
    res['by_total'] = [(a, min(b, 999)) + row(hang & (tot >= a) & (tot < b))[:2] for a, b in zip(BINS[:-1], BINS[1:])]
    # size against squeeze: at the SAME number of steps before landing, thin share of the little-squeezed (< 1.5) and of the much-squeezed (>= 2.5)
    res['steps_x_squeeze'] = [(k, float((hang & (st == k) & (tot < 1.5)).mean()), float(thin[hang & (st == k) & (tot < 1.5)].mean()) if (hang & (st == k) & (tot < 1.5)).any() else None,
                               float((hang & (st == k) & (tot >= 2.5)).mean()), float(thin[hang & (st == k) & (tot >= 2.5)].mean()) if (hang & (st == k) & (tot >= 2.5)).any() else None) for k in range(1, 6)]
    res['scrap_squeezed'] = float((thin & hang & (tot >= 2.5)).mean()); res['scrap_round'] = float((thin & hang & (tot < 1.5)).mean()); res['scrap_between'] = float((thin & hang & (tot >= 1.5) & (tot < 2.5)).mean())
    a, b = hang & thin, hang & ~thin
    if a.sum() > 20 and b.sum() > 20:
        rng = np.random.default_rng(1)
        for key, arr in (('total', tot), ('off', off), ('steps', st)):
            aa = rng.choice(arr[a], 40000); bb = rng.choice(arr[b], 40000); res['auc_' + key] = float((aa > bb).mean() + 0.5 * (aa == bb).mean())
    for tag, m in (('thin', a), ('thick', b)):
        if m.sum() > 5:
            bs = t['band'][m].sum(0); res['band_' + tag] = [float(x) for x in bs / max(bs.sum(), 1e-12)]
            res['total_med_' + tag] = float(np.median(tot[m])); res['off_mean_' + tag] = float(off[m].mean()); res['steps_mean_' + tag] = float(st[m].mean())
            res['worst_med_' + tag] = float(np.median(t['worst'][m])); res['branch_' + tag] = float((t['s2min'][m] < 0.3).mean())
            wl = t['worst_lat'][m]; res['worstband_' + tag] = [float(((wl >= x) & (wl < y)).mean()) for x, y in zip(L.BANDS[:-1], L.BANDS[1:])]
            res['worst_last_' + tag] = float((t['worst_k'][m] == st[m] - 1).mean()); res['worst_first_' + tag] = float((t['worst_k'][m] == 0).mean())
            res['needle_' + tag] = float(np.median(t['top'][m])); res['blade_' + tag] = float(np.median(t['mid'][m]))
    # is the straight-line picture right? predicted half-thickness = (room round the landing place) / (largest stretch), against the measured depth below the surface
    if hang.sum() > 50:
        pred = t['land_edt'][hang] / np.maximum(t['sig1'][hang], 1e-12); meas = t['edt'][hang]
        res['pred_meas_spearman'] = float(spearmanr(pred, meas).correlation); res['pred_meas_ratio'] = float(np.median(pred / np.maximum(meas, 1e-9)))
    bd = bodies(name, sname, t); res['bodies'] = bd
    if not quiet:
        print('\n== %s, %s [%s]: %d inside blocks, thin scrap %.1f %% of them' % (name, L.SETNAME[sname], mode, res['inside_blocks'], 100 * res['thin_share']))
        print('   main lumps hold %.1f %% of the inside, thin share there %.1f %% | what hangs on them holds %.1f %%, thin share there %s %% | never lands in 40 steps: %.1f %%'
              % (100 * res['main_share'], 100 * (res['main_thin'] or 0), 100 * res['hang_share'], ('%.1f' % (100 * res['hang_thin'])) if res['hang_thin'] is not None else '-', 100 * (1 - res['landed_share'])))
        print('   of all thin scrap: %.0f %% lies in the main lumps, %.0f %% in what hangs on them, %.0f %% never lands' % (100 * res['thin_in_main'], 100 * (1 - res['thin_in_main'] - res['thin_never']), 100 * res['thin_never']))
        print('   steps before landing: share of the inside | thin share | total squeeze median (90 %) | depth below the surface, median')
        for k, sh, th, md, p9, ed in res['by_steps']:
            if sh > 0:
                print('      %s: %5.1f %% | %5.1f %% | %7.2f (%8.1f) | %.3f' % (('%d ' % k) if k < 6 else '6+', 100 * sh, 100 * th, md, p9, ed))
        print('   what hangs, by its steps off the flat plane before landing: share of the inside | thin share | total squeeze median (90 %) | depth below the surface')
        for k, sh, th, md, p9, ed in res['by_off']:
            if sh > 0:
                print('      %s: %5.1f %% | %5.1f %% | %7.2f (%8.1f) | %.3f' % (('%d ' % k) if k < 5 else '5+', 100 * sh, 100 * th, md, p9, ed))
        print('   what hangs, by its total squeeze from .. to: share of the inside | thin share')
        for a_, b_, sh, th in res['by_total']:
            if sh > 0:
                print('      %5.1f .. %5.1f: %5.1f %% | %5.1f %%' % (a_, b_, 100 * sh, 100 * th))
        print('   thin scrap as a share of the whole inside: %.1f %% much squeezed (total 2.5 or more), %.1f %% in between, %.1f %% little squeezed (below 1.5: small but not flattened), %.1f %% in the main lumps'
              % (100 * res['scrap_squeezed'], 100 * res['scrap_between'], 100 * res['scrap_round'], 100 * float((thin & main).mean())))
        print('   same number of steps before landing: thin share of the little-squeezed blocks | of the much-squeezed blocks (their shares of the inside)')
        for k, s1, t1, s2, t2 in res['steps_x_squeeze']:
            if s1 + s2 > 0:
                print('      %d: %s (%.1f %%) | %s (%.1f %%)' % (k, ('%5.1f %%' % (100 * t1)) if t1 is not None else '   -   ', 100 * s1, ('%5.1f %%' % (100 * t2)) if t2 is not None else '   -   ', 100 * s2))
        if 'auc_total' in res:
            print('   a thin hanging block has the larger number than a thick hanging block in %.0f %% of pairs for the total squeeze, %.0f %% for steps off the plane, %.0f %% for steps before landing'
                  % (100 * res['auc_total'], 100 * res['auc_off'], 100 * res['auc_steps']))
        for tag in ('thin', 'thick'):
            if 'band_' + tag in res:
                print('   %-5s hanging blocks: steps %.1f, off the plane %.1f | total squeeze median %.1f (largest : middle stretch %.1f, middle : smallest %.1f) | worst single step median %.1f; it was the last step before landing for %.0f %%, the first for %.0f %% | within reach of a branch direction %.0f %%'
                      % (tag, res['steps_mean_' + tag], res['off_mean_' + tag], res['total_med_' + tag], res['needle_' + tag], res['blade_' + tag], res['worst_med_' + tag], 100 * res['worst_last_' + tag], 100 * res['worst_first_' + tag], 100 * res['branch_' + tag]))
                print('         share of all their squeezing by latitude band 0-12 / 12-22 / 22-35 / 35-50 / 50-65 / 65-90: ' + ' / '.join('%.0f %%' % (100 * x) for x in res['band_' + tag])
                      + '   | the worst step fell in: ' + ' / '.join('%.0f %%' % (100 * x) for x in res['worstband_' + tag]))
        if 'pred_meas_spearman' in res:
            print('   straight-line picture: predicted half-thickness against measured depth below the surface, rank correlation %.2f, median predicted / measured %.2f' % (res['pred_meas_spearman'], res['pred_meas_ratio']))
        if bd:
            print('   bodies (peeled twice, 6+ blocks) by the steps off the plane of the body\'s middle: number | long : thick median (max) | total squeeze of the middle, median')
            for k in range(0, 6):
                bb = [b for b in bd if (round(b['off']) == k if k < 5 else round(b['off']) >= 5)]
                if bb:
                    rr = np.array([b['ratio'] for b in bb]); print('      %s: %3d | %.2f (%.2f) | %.2f' % (('%d ' % k) if k < 5 else '5+', len(bb), np.median(rr), rr.max(), np.median([b['total'] for b in bb])))
        sys.stdout.flush()
    return res


if __name__ == '__main__':
    mode = sys.argv[2] if len(sys.argv) > 2 else 'lump'
    path = os.path.join(L.CACHE, 'analyse%s.json' % ('' if mode == 'lump' else '-ball')); t0 = time.time(); new = {}
    for job in sys.argv[1].split(','):
        nm, sn = job.split(':'); t = traced(nm, sn, mode); new[job] = tables(nm, sn, t, mode); print('   [%.0f s]' % (time.time() - t0)); sys.stdout.flush()
    allm = json.load(open(path)) if os.path.exists(path) else {}
    allm.update(new); json.dump(allm, open(path, 'w'), indent=1)
