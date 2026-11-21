"""Does a saved picture show the same colours in the same places as the screen?
python out/t9/export/colours.py <scene> <job> [<job> ...]
scene: M (opening Mandelbrot, trap-coloured), J (Julia, Douady rabbit), S (Julia, trap is the solid), F (2D view with an
inside colouring), K (Kleinian), X (example Spiky coral).  job: two characters, size s|t|k (screen, twice, 4K) and
quality 1|2|3 (As on screen now, Fine, Extra fine), e.g. s1 t2 k3.  Each file is brought to the stage's scale and
compared with a screenshot of the stage."""
import json, os, sys, time
import numpy as np
from PIL import Image
from drv import Lab, HERE, log, open_rgb, blank, tl_report

J = lambda o: json.dumps(o, ensure_ascii=False)
SCENES = {
    'M': "",
    'J': "$('mode-j').click(); await sleep(80); pick('juliaPreset', 'Douady rabbit');",
    'S': "$('mode-j').click(); await sleep(80); pick('col-solid', 'Is the solid');",
    'F': "$('flat').click(); await sleep(80); pick('col-inMode', 'How quickly');",
    'K': "$('mode-k').click();",
    'X': "pick('trapExamples', 'Spiky coral');",
}
SIZES = {'s': 'As on screen', 't': 'Twice', 'k': '3840'}
QUALS = {'1': 'As on screen', '2': 'Fine', '3': 'Extra fine'}
STATE = """const c = L.S.colour; return { mode: L.S.mode, flat: !!L.S.flat, colourBy: chosen('col-mode'), trap: $('col-trap') ? chosen('col-trap') : null,
solid: c.solid, by: c.by, reach: c.reach, pal: chosen('col-pal'), rev: c.rev, inMode: c.inMode, canvas: [$('view').width, $('view').height] };"""


def hsv(a):
    a = a.astype(np.float32) / 255.0
    mx, mn = a.max(axis=2), a.min(axis=2)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60.0
    return h, s, mx


def against(im, stage_path, tag):
    st = Image.open(os.path.join(HERE, stage_path)).convert('RGB')
    sw, sh = st.size
    W, H = im.size
    k = sh / H
    small = im if (W, H) == (sw, sh) else im.resize((max(1, round(W * k)), sh), Image.LANCZOS if k < 1 else Image.BICUBIC)
    w = min(small.size[0], sw)
    a = small.crop(((small.size[0] - w) // 2, 0, (small.size[0] - w) // 2 + w, sh))     # the file
    b = st.crop(((sw - w) // 2, 0, (sw - w) // 2 + w, sh))                               # the screen
    A, B = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    d = np.abs(A - B).max(axis=2)
    out = {'mean': round(float(d.mean()), 2), 'over24_pct': round(float((d > 24).mean() * 100), 2), 'over64_pct': round(float((d > 64).mean() * 100), 2), 'worst': int(d.max()),
           'lum_file_minus_screen': round(float(A.mean() - B.mean()), 2)}
    # colours in places: both brought down by 4 so that a one-pixel shift of an edge does not count
    q = (max(1, w // 4), max(1, sh // 4))
    a4, b4 = np.asarray(a.resize(q, Image.BOX)), np.asarray(b.resize(q, Image.BOX))
    ha, sa, va = hsv(a4); hb, sb, vb = hsv(b4)
    ok = (sa > 0.25) & (sb > 0.25) & (va > 0.15) & (vb > 0.15)
    dh = np.abs(((ha - hb + 180.0) % 360.0) - 180.0)
    d4 = np.abs(a4.astype(np.int16) - b4.astype(np.int16)).max(axis=2)
    out['mean_quarter_scale'] = round(float(d4.mean()), 2)
    if ok.sum() > 50:
        v = dh[ok]
        out['hue'] = {'coloured_pct': round(float(ok.mean() * 100), 1), 'median': round(float(np.median(v)), 1), 'p90': round(float(np.percentile(v, 90)), 1), 'p99': round(float(np.percentile(v, 99)), 1),
                      'over20_pct': round(float((v > 20).mean() * 100), 2), 'over45_pct': round(float((v > 45).mean() * 100), 2)}
        cells = []
        gy, gx = 5, 6
        hh, ww = ok.shape
        for r in range(gy):
            for c in range(gx):
                m = ok[r * hh // gy:(r + 1) * hh // gy, c * ww // gx:(c + 1) * ww // gx]
                if m.mean() < 0.08: continue
                x = dh[r * hh // gy:(r + 1) * hh // gy, c * ww // gx:(c + 1) * ww // gx][m]
                if x.mean() > 12 or (x > 30).mean() > 0.15:
                    cells.append(['row %d col %d' % (r + 1, c + 1), round(float(x.mean()), 1), round(float((x > 30).mean() * 100), 1)])
        out['hue']['regions_changed'] = cells
    # coloured on one and not on the other (a piece present in one picture only), at quarter scale
    ca, cb = (sa > 0.25) & (va > 0.15), (sb > 0.25) & (vb > 0.15)
    out['coloured_in_one_only_pct'] = round(float((ca ^ cb).mean() * 100), 2)
    # three panels: the screen, the file, the difference times 4
    tri = Image.new('RGB', (3 * w + 12, sh), (128, 128, 128))
    tri.paste(b, (0, 0)); tri.paste(a, (w + 6, 0))
    tri.paste(Image.fromarray(np.clip(np.abs(A - B) * 4, 0, 255).astype(np.uint8)), (2 * w + 12, 0))
    tri.save(os.path.join(HERE, tag + '-tri.png'))
    return out


def main():
    scene, jobs = sys.argv[1], sys.argv[2:]
    lab = Lab()
    try:
        lab.idle()
        if SCENES[scene]:
            lab.js(SCENES[scene] + " await sleep(150);")
        lab.idle(); time.sleep(0.4); lab.idle()
        log(scene, 'state', J(lab.js(STATE)))
        stage = 'P-%s-stage.png' % scene
        lab.stage_shot(stage)
        for jb in jobs:
            tag = 'P-%s-%s' % (scene, jb)
            size, quality = SIZES[jb[0]], QUALS[jb[1]]
            st = lab.start_job(size, quality, 'PNG', watch=False)
            if not st['busy']:
                log(tag, 'DID NOT START', J(st)); continue
            done = lab.job_wait(1500)
            en = lab.end_job()
            if not done or not en['saveShown']:
                log(tag, 'TIMED OUT or nothing to save', J({k: v for k, v in en.items() if k != 'tl'})); continue
            path, r = lab.save(tag)
            im, fmt = open_rgb(path)
            res = {'size': im.size, 'fmt': fmt, 'took_s': round(en['took'] / 1000, 1), 'blank': blank(im), 'facts': en['facts']}
            res.update(against(im, stage, tag))
            log(tag, size, '/', quality, J(res))
            rows = tl_report(en['tl'], en['took'])
            if rows:
                rises = [(a[0], a[2], b[2]) for a, b in zip(rows, rows[1:]) if b[2] > a[2]]
                ratios = [said / true for _, _, said, true in rows if true > 3]
                log(tag, 'time left: first number at %.1f s said %.0f true %.1f; rises %d; said/true %s' % (rows[0][0], rows[0][2], rows[0][3], len(rises), ('%.2f to %.2f' % (min(ratios), max(ratios))) if ratios else 'n/a'))
            if im.size[0] > 2000:      # keep the large files small on disk: a half-size copy only
                im.resize((im.size[0] // 2, im.size[1] // 2), Image.LANCZOS).save(os.path.join(HERE, tag + '-half.png')); os.remove(os.path.join(HERE, path))
        # the live picture must not have been disturbed by the jobs
        lab.idle(); lab.stage_shot('P-%s-stage-after.png' % scene)
        a = np.asarray(Image.open(os.path.join(HERE, stage)).convert('RGB'), dtype=np.int16); b = np.asarray(Image.open(os.path.join(HERE, 'P-%s-stage-after.png' % scene)).convert('RGB'), dtype=np.int16)
        log(scene, 'the screen before the jobs against the screen after them: worst', int(np.abs(a - b).max()) if a.shape == b.shape else 'sizes differ')
        log(scene, 'problems', lab.problems())
    finally:
        lab.close()


if __name__ == '__main__':
    main()
