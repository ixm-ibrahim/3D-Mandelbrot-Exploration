"""Check model zips from "Save a 3D model" for what Blender, Rhino and a slicer need.

  python out/t6/mesh/check.py <job> [<job> ...]      reads zips/<job>.zip, runs/<job>.json, pics/<subject>.png
Writes checks/<job>.json and pics/cmp-<job>.png: the page's picture, the mesh drawn from the same camera, and
where the two outlines differ (red: in the picture only, blue: in the model only).
"""
import hashlib, json, os, re, sys, time, zipfile
import numpy as np
from PIL import Image, ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ.get('MESH_PAGE', 'v10a'))   # round 10: one folder a page


def weld(P):
    P = np.ascontiguousarray(P, np.float32) + np.float32(0.0)
    b = P.view(np.uint32).reshape(-1, 3)
    order = np.lexsort((b[:, 2], b[:, 1], b[:, 0]))
    sb = b[order]
    new = np.ones(len(sb), bool); new[1:] = np.any(sb[1:] != sb[:-1], axis=1)
    ids = np.cumsum(new) - 1
    inv = np.empty(len(sb), np.int64); inv[order] = ids
    return P[order][new], inv


def topology(F, nv, V64):
    """F: (nt, 3) point numbers, V64: (nt, 3, 3) corners. Edge and vertex checks of a triangle mesh."""
    r, cnt = {}, len(F)
    same = (F[:, 0] == F[:, 1]) | (F[:, 1] == F[:, 2]) | (F[:, 0] == F[:, 2])
    cr = np.cross(V64[:, 1] - V64[:, 0], V64[:, 2] - V64[:, 0]); nl = np.linalg.norm(cr, axis=1); area = 0.5 * nl
    r['degenerate_by_index'] = int(same.sum()); r['area_min_mm2'] = float(area.min()); r['area_below_1e-9'] = int((area < 1e-9).sum())
    r['area_total_mm2'] = float(area.sum())
    e0 = np.linalg.norm(V64[:, 1] - V64[:, 0], axis=1); e1 = np.linalg.norm(V64[:, 2] - V64[:, 1], axis=1); e2 = np.linalg.norm(V64[:, 0] - V64[:, 2], axis=1)
    longest = np.maximum(np.maximum(e0, e1), e2)
    r['edge_len_mm'] = [float(np.minimum(np.minimum(e0, e1), e2).min()), float(np.median(e0)), float(longest.max())]
    r['slivers_aspect_over_100'] = int((longest * longest / np.maximum(2 * area, 1e-300) > 100).sum())
    Fs = np.sort(F, axis=1)
    r['duplicate_triangles'] = int(cnt - len(np.unique(Fs, axis=0)))
    a = F.ravel(); b = F[:, [1, 2, 0]].ravel()
    dk = a * nv + b; rk = b * nv + a
    order = np.argsort(dk, kind='stable'); sdk = dk[order]
    r['directed_edges_repeated'] = int((sdk[1:] == sdk[:-1]).sum())
    pos = np.minimum(np.searchsorted(sdk, rk), len(sdk) - 1); has = sdk[pos] == rk
    r['edges_without_twin'] = int((~has).sum())
    und = np.minimum(a, b) * nv + np.maximum(a, b); uu, cu = np.unique(und, return_counts=True)
    r['edges'] = int(len(uu)); r['edge_use_histogram'] = {str(i): int(n) for i, n in enumerate(np.bincount(cu)) if n}
    r['closed'] = bool((cu == 2).all()); r['oriented'] = bool(r['directed_edges_repeated'] == 0 and r['edges_without_twin'] == 0)
    r['euler'] = int(nv - len(uu) + cnt)
    g = coo_matrix((np.ones(len(a), np.int8), (a, b)), shape=(nv, nv)); ncomp, lab = connected_components(g, directed=False)
    tl = lab[F[:, 0]]; sizes = np.bincount(tl, minlength=ncomp)
    six = np.einsum('ij,ij->i', V64[:, 0], np.cross(V64[:, 1], V64[:, 2]))
    vols = np.bincount(tl, weights=six, minlength=ncomp) / 6
    r['components'] = int(ncomp); r['component_triangles_top'] = sorted(sizes.tolist(), reverse=True)[:6]
    r['components_with_negative_volume'] = int((vols < 0).sum()); r['volume_cm3'] = float(six.sum() / 6000)
    # fans round each point: a point whose triangles form more than one fan is a pinch (non-manifold) point
    e = np.arange(len(dk)); twin = order[pos]; tw_next = 3 * (twin // 3) + (twin % 3 + 1) % 3
    cg = coo_matrix((np.ones(int(has.sum()), np.int8), (e[has], tw_next[has])), shape=(len(dk), len(dk)))
    nf, _ = connected_components(cg, directed=False)
    r['pinch_points'] = int(nf - nv)
    return r, cr, nl


def check_stl(data):
    r = {'bytes': len(data)}
    head = data[:80]; cnt = int(np.frombuffer(data, '<u4', 1, 80)[0])
    r['header'] = head.rstrip(b'\0').decode('latin1'); r['starts_with_solid'] = head[:5].lower() == b'solid'
    r['count'] = cnt; r['size_matches_count'] = len(data) == 84 + 50 * cnt
    dt = np.dtype([('n', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')])
    T = np.frombuffer(data, dt, cnt, 84)
    V = T['v']; r['attribute_bytes_nonzero'] = int(np.count_nonzero(T['a']))
    r['finite'] = bool(np.isfinite(V).all() and np.isfinite(T['n']).all())
    P, inv = weld(V.reshape(-1, 3)); F = inv.reshape(-1, 3); nv = len(P)
    r['points_after_weld'] = nv
    V64 = V.astype(np.float64)
    topo, cr, nl = topology(F, nv, V64); r.update(topo)
    nc = cr / np.maximum(nl, 1e-300)[:, None]; dots = (nc * T['n']).sum(1); ln = np.linalg.norm(T['n'], axis=1)
    r['normal_dot_min'] = float(dots.min()); r['normals_off_by_more_than_2.5deg'] = int((dots < 0.999).sum()); r['normals_reversed'] = int((dots < 0).sum())
    r['normal_length_range'] = [float(ln.min()), float(ln.max())]
    lo, hi = P.min(0).astype(float), P.max(0).astype(float)
    r['bbox_min'] = lo.tolist(); r['bbox_max'] = hi.tolist(); r['size_mm'] = (hi - lo).tolist()
    return r, V, P, F


def check_obj(data, V):
    r = {'bytes': len(data)}
    lines = data.split(b'\n')
    vl = [l[2:] for l in lines if l.startswith(b'v ')]; fl = [l[2:] for l in lines if l.startswith(b'f ')]
    other = [l for l in lines if l and not l.startswith((b'v ', b'f '))]
    r['other_lines'] = [l.decode('utf-8', 'replace')[:160] for l in other[:8]]; r['other_line_count'] = len(other)
    r['vn_lines'] = sum(1 for l in other if l.startswith(b'vn ')); r['vt_lines'] = sum(1 for l in other if l.startswith(b'vt '))
    r['crlf'] = data.count(b'\r\n'); r['non_ascii_bytes'] = int(sum(1 for c in data[:4096] if c > 127))
    Vt = np.array(b' '.join(vl).split()).astype(np.float64).reshape(len(vl), -1)
    Ft = np.array(b' '.join(fl).split()).astype(np.int64).reshape(len(fl), -1)
    r['v'] = len(vl); r['f'] = len(fl); r['v_fields'] = int(Vt.shape[1]); r['f_fields'] = int(Ft.shape[1])
    r['index_min'] = int(Ft.min()); r['index_max'] = int(Ft.max()); r['indices_in_range'] = bool(Ft.min() >= 1 and Ft.max() <= len(vl))
    r['points_unused'] = int(len(vl) - len(np.unique(Ft)))
    if Vt.shape[1] >= 6:
        C = Vt[:, 3:6]; r['colour_range'] = [float(C.min()), float(C.max())]; r['colour_mean'] = C.mean(0).round(3).tolist()
    # the file is y-up: (x, y, z) in it is the lab's (x, z, -y)
    lab = np.stack([Vt[:, 0], -Vt[:, 2], Vt[:, 1]], axis=1)
    tri = lab[Ft - 1]
    r['faces_match_stl'] = len(fl) == len(V)
    if len(fl) == len(V):
        r['max_distance_to_stl_mm'] = float(np.abs(tri - V).max())
    return r, Vt, Ft


def check_ply(data, V):
    r = {'bytes': len(data)}
    end = data.index(b'end_header\n') + 11
    head = data[:end].decode('ascii'); r['header'] = head
    nv = int(re.search(r'element vertex (\d+)', head).group(1)); nt = int(re.search(r'element face (\d+)', head).group(1))
    r['vertex'] = nv; r['face'] = nt; r['size_matches_counts'] = len(data) == end + 15 * nv + 13 * nt
    vd = np.dtype([('p', '<f4', (3,)), ('c', 'u1', (3,))]); fd = np.dtype([('n', 'u1'), ('i', '<i4', (3,))])
    Vp = np.frombuffer(data, vd, nv, end); Fp = np.frombuffer(data, fd, nt, end + 15 * nv)
    r['all_faces_triangles'] = bool((Fp['n'] == 3).all()); r['index_min'] = int(Fp['i'].min()); r['index_max'] = int(Fp['i'].max())
    r['indices_in_range'] = bool(Fp['i'].min() >= 0 and Fp['i'].max() < nv); r['points_unused'] = int(nv - len(np.unique(Fp['i'])))
    C = Vp['c'].astype(np.int64)
    r['colour_mean'] = C.mean(0).round(1).tolist(); r['colour_min'] = C.min(0).tolist(); r['colour_max'] = C.max(0).tolist()
    r['black_points'] = int((C.sum(1) == 0).sum()); r['distinct_colours'] = int(len(np.unique(C[:, 0] * 65536 + C[:, 1] * 256 + C[:, 2])))
    r['grey_points_share'] = float(((C.max(1) - C.min(1)) < 12).mean())
    r['faces_match_stl'] = nt == len(V)
    if nt == len(V):
        r['max_distance_to_stl_mm'] = float(np.abs(Vp['p'][Fp['i']] - V).max())
    return r, Vp, Fp


def readme_facts(text):
    f = {}
    m = re.search(r'Size:\s+([\d.]+) x ([\d.]+) x ([\d.]+) mm\. The longest side was set to ([\d.]+) mm', text); f['size'] = [float(x) for x in m.groups()] if m else None
    for key, pat in (('triangles', r'Triangles:\s+([\d,]+)'), ('points', r'Points:\s+([\d,]+)')):
        m = re.search(pat, text); f[key] = int(m.group(1).replace(',', '')) if m else None
    m = re.search(r'Volume:\s+([\d.eE+-]+) cubic centimetres', text); f['volume_cm3'] = float(m.group(1)) if m else None
    m = re.search(r"One unit of the lab's space is ([\d.eE+-]+) mm", text); f['unit'] = float(m.group(1)) if m else None
    m = re.search(r'Pieces:\s+(.*)', text); f['pieces'] = m.group(1).strip() if m else None
    m = re.search(r'Made from: (.*)', text); f['made_from'] = m.group(1).strip() if m else None
    m = re.search(r'Grid:\s+(.*)', text); f['grid'] = m.group(1).strip() if m else None
    f['cut_line'] = bool(re.search(r'cut open at height', text)); f['says_closed'] = 'The surface is closed' in text
    return f


def picture_mask(im, st):
    a = np.asarray(im.convert('RGB')).astype(np.int32)
    m = a.max(2) > 46
    H, W = m.shape
    keep = np.ones((H, W), bool)
    keep[:, W - 125:] = False                  # the zoom slider and the arcball / fly switch
    keep[:75, :95] = False                     # the axes
    keep[H - 70:, :345] = False                # the hint
    keep[H - 60:, W - 200:] = False            # minus, plus, reset view
    return m & keep, keep


def draw_mesh(Vp, Fp, V_stl_normals, rec, size):
    st, lab = rec['state'], rec['after']['lab']
    W, H = size
    org, h, lo, hi = np.array(lab['org']), lab['h'], np.array(lab['lo']), np.array(lab['hi'])
    off = org + h * np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    P = Vp['p'].astype(np.float64) / lab['unit'] + off
    pos, right, up, f = (np.array(st[k]) for k in ('pos', 'right', 'up', 'f'))
    v = P - pos; zf = v @ f
    ux = (v @ right) / zf / st['fov']; uy = (v @ up) / zf / st['fov']
    sx = st['cx'] + (ux * st['ch'] + st['cw']) / 2; sy = st['cy'] + (1 - uy) * st['ch'] / 2
    I = Fp['i']; depth = zf[I].mean(1); order = np.argsort(-depth)
    n = V_stl_normals; ndl = np.abs(n @ (-f)) if n is not None else np.ones(len(I))
    shade = 0.35 + 0.65 * ndl
    col = Vp['c'][I].astype(np.float64).mean(1) * shade[:, None]
    img = Image.new('RGB', (W, H), (8, 11, 16)); mask = Image.new('L', (W, H), 0)
    d, dm = ImageDraw.Draw(img), ImageDraw.Draw(mask)
    X = sx[I]; Y = sy[I]; front = zf[I].min(1) > 0
    for t in order:
        if not front[t]:
            continue
        pts = [(X[t, 0], Y[t, 0]), (X[t, 1], Y[t, 1]), (X[t, 2], Y[t, 2])]
        c = (int(col[t, 0]), int(col[t, 1]), int(col[t, 2]))
        d.polygon(pts, fill=c, outline=c); dm.polygon(pts, fill=255, outline=255)
    return img, np.asarray(mask) > 0, {'lab_bbox_min': (P.min(0)).round(4).tolist(), 'lab_bbox_max': (P.max(0)).round(4).tolist()}


def hue(a):
    a = a.astype(np.float64) / 255; mx, mn = a.max(-1), a.min(-1); d = mx - mn
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hh = np.zeros_like(mx); nz = d > 1e-9
    i = nz & (mx == r); hh[i] = ((g - b)[i] / d[i]) % 6
    i = nz & (mx == g) & (mx != r); hh[i] = (b - r)[i] / d[i] + 2
    i = nz & (mx == b) & (mx != r) & (mx != g); hh[i] = (r - g)[i] / d[i] + 4
    return hh * 60, np.where(mx > 0, d / np.maximum(mx, 1e-9), 0), mx


def main():
    os.makedirs(os.path.join(HERE, 'checks'), exist_ok=True)
    for job in sys.argv[1:]:
        t0 = time.time()
        zp = os.path.join(HERE, 'zips', job + '.zip')
        with open(os.path.join(HERE, 'runs', job + '.json'), encoding='utf-8') as fh:
            rec = json.load(fh)
        out = {'job': job, 'zip_bytes': os.path.getsize(zp)}
        z = zipfile.ZipFile(zp)
        out['zip_bad_entry'] = z.testzip(); out['zip_names'] = z.namelist()
        out['zip_compression'] = sorted({i.compress_type for i in z.infolist()}); out['zip_dates'] = [list(i.date_time) for i in z.infolist()][:1]
        names = {n.rsplit('.', 1)[-1]: n for n in z.namelist()}
        text = z.read('readme.txt').decode('utf-8'); out['readme'] = text; out['readme_facts'] = readme_facts(text)
        V = None
        if 'stl' in names:
            data = z.read(names['stl']); out['sha1_stl'] = hashlib.sha1(data).hexdigest()
            out['stl'], V, P, F = check_stl(data)
            dt = np.dtype([('n', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')]); normals = np.frombuffer(data, dt, out['stl']['count'], 84)['n'].astype(np.float64)
            del data
        if 'obj' in names:
            data = z.read(names['obj']); out['sha1_obj'] = hashlib.sha1(data).hexdigest()
            out['obj'], Vt, Ft = check_obj(data, V); del data
        if 'ply' in names:
            data = z.read(names['ply']); out['sha1_ply'] = hashlib.sha1(data).hexdigest()
            out['ply'], Vp, Fp = check_ply(data, V); del data
            if 'obj' in names:
                out['obj_ply_colour_max_diff_of_255'] = float(np.abs(Vt[:, 3:6] * 255 - Vp['c']).max()) if len(Vt) == len(Vp) else None
        # the facts of the panel and of the readme against the files
        rf, st = out['readme_facts'], out.get('stl')
        if st:
            out['readme_vs_file'] = {
                'triangles': rf['triangles'] == st['count'], 'points': rf['points'] == st['points_after_weld'],
                'size_diff_mm': float(np.abs(np.array(rf['size'][:3]) - np.array(st['size_mm'])).max()) if rf['size'] else None,
                'volume_ratio': rf['volume_cm3'] / st['volume_cm3'] if rf['volume_cm3'] and st['volume_cm3'] else None,
                'stands_on_z0': abs(st['bbox_min'][2]) < 1e-3, 'centred_xy_mm': [round((st['bbox_min'][k] + st['bbox_max'][k]) / 2, 4) for k in (0, 1)],
                'unit_vs_job': (rf['unit'] / rec['after']['lab']['unit']) if rf['unit'] and rec['after'].get('lab') else None}
        # the model against the picture
        pic = os.path.join(HERE, 'pics', rec['subject'] + '.png')
        if 'ply' in names and rec['after'].get('lab') and os.path.exists(pic) and '--nodraw' not in sys.argv:
            im = Image.open(pic).convert('RGB')
            img, mm, extra = draw_mesh(Vp, Fp, normals if V is not None else None, rec, im.size); out.update(extra)
            pm, keep = picture_mask(im, rec['state']); mm = mm & keep
            inter, union = (pm & mm).sum(), (pm | mm).sum()
            out['silhouette'] = {'picture_px': int(pm.sum()), 'model_px': int(mm.sum()), 'iou': float(inter / max(1, union)),
                                 'picture_only_share': float((pm & ~mm).sum() / max(1, pm.sum())), 'model_only_share': float((mm & ~pm).sum() / max(1, pm.sum()))}
            both = pm & mm
            hp, sp, vp = hue(np.asarray(im)); hm, sm, vm = hue(np.asarray(img))
            sel = both & (sp > 0.35) & (sm > 0.35)
            if sel.sum() > 50:
                dh = np.abs(hp[sel] - hm[sel]); dh = np.minimum(dh, 360 - dh)
                out['colour'] = {'compared_px': int(sel.sum()), 'hue_diff_median_deg': float(np.median(dh)), 'hue_diff_within_30deg_share': float((dh < 30).mean())}
            diff = np.zeros((im.size[1], im.size[0], 3), np.uint8) + np.array([8, 11, 16], np.uint8)
            diff[both] = (90, 96, 104); diff[pm & ~mm] = (255, 60, 50); diff[mm & ~pm] = (60, 130, 255)
            sheet = Image.new('RGB', (3 * im.size[0], im.size[1]))
            sheet.paste(im, (0, 0)); sheet.paste(img, (im.size[0], 0)); sheet.paste(Image.fromarray(diff), (2 * im.size[0], 0))
            sheet.save(os.path.join(HERE, 'pics', 'cmp-' + job + '.png'))
        out['check_seconds'] = round(time.time() - t0, 1)
        with open(os.path.join(HERE, 'checks', job + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        s = out.get('stl', {}); sil = out.get('silhouette', {}); o = out.get('obj', {}); p = out.get('ply', {})
        print('%s: tris %s, closed %s, oriented %s, edge uses %s, pinch %s, dup %s, degenerate %s (min area %.2e), normals off %s (reversed %s), pieces %s (neg vol %s), euler %s, vol %.3f cm3 (readme x%s), size %s, z0 %s | obj v %s f %s vn %s in-range %s dist %s | ply v %s f %s ok %s dist %s black %s | iou %s pic-only %s model-only %s | hue %s | %.0f s' % (
            job, s.get('count'), s.get('closed'), s.get('oriented'), s.get('edge_use_histogram'), s.get('pinch_points'), s.get('duplicate_triangles'), s.get('degenerate_by_index'), s.get('area_min_mm2', 0),
            s.get('normals_off_by_more_than_2.5deg'), s.get('normals_reversed'), s.get('components'), s.get('components_with_negative_volume'), s.get('euler'), s.get('volume_cm3', 0),
            round(out.get('readme_vs_file', {}).get('volume_ratio') or 0, 4), [round(x, 2) for x in s.get('size_mm', [])], out.get('readme_vs_file', {}).get('stands_on_z0'),
            o.get('v'), o.get('f'), o.get('vn_lines'), o.get('indices_in_range'), o.get('max_distance_to_stl_mm'), p.get('vertex'), p.get('face'), p.get('size_matches_counts'), p.get('max_distance_to_stl_mm'), p.get('black_points'),
            round(sil.get('iou', 0), 3), round(sil.get('picture_only_share', 0), 3), round(sil.get('model_only_share', 0), 3), out.get('colour'), out['check_seconds']), flush=True)


if __name__ == '__main__':
    main()
