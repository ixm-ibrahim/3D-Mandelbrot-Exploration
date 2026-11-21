"""The fixed lists of scenes for round 6 (colour), and the comparisons of two sets of pictures of them.

  python out/r6/colour/scenes.py shoot <page> <label> [prefix ...]   draw the scenes whose names start with a prefix
                                                                     (all of them when none is given) on dist/<page>.html
                                                                     into out/r6/colour/<label>/
  python out/r6/colour/scenes.py cmp <labelA> <labelB>     the "must not change" list: largest channel difference per scene
  python out/r6/colour/scenes.py accept <label>            the acceptance scenes: each variation against Balanced
  python out/r6/colour/scenes.py sheets <labelA> [<labelB>]   contact sheets (pairs: A above B)

Every scene starts from "Reset everything". Three lists:
  FIXED   f..  pictures that must not change (the 2D view; 3D pictures not coloured by an orbit trap)
  ACCEPT  a-<subject>-<set-up>-<variation>  the acceptance scenes of docs/SPEC6.md
  SOLIDS  s..  trap solids in the three kinds of picture
The reference set (label ref) was drawn from dist/v6.html before any source was changed.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);"
       "if (L.R) L.R.warmOn = false;"
       "const go = () => { L.syncControls(); L.refresh(false); };"
       "const mode = m => $('mode-' + m).click();"
       "const q = id => $(id).click();")
RESET = "L.resetAll();"
B4 = "q('qBal'); S.q.aa = 4;"          # Balanced (shadows, crevice shading, exact slope) with 4 passes, to keep the run short
JB = "mode('j'); S.c = [-1, 0, 0];"    # the Julia set for c = -1
JR = "mode('j'); S.c = [-0.123, 0.745, 0];"   # the Douady rabbit
FIXED = [
    ('f01-flat-m-open', "S.flat = true;"),
    ('f02-flat-j-minus1', "S.flat = true; " + JB),
    ('f03-flat-j-rabbit', "S.flat = true; " + JR),
    ('f04-flat-m-slice-03', "S.flat = true; S.cut = 0.3;"),
    ('f05-flat-k', "S.flat = true; mode('k');"),
    ('f06-flat-m-neg2', "S.flat = true; S.n = -2;"),
    ('f07-flat-m-mosaic', "S.mosaic = true; S.flat = true;"),
    ('f08-flat-m-in-settle', "S.flat = true; C.inMode = 4; C.inPal = 6;"),
    ('f09-flat-j-in-trap', "S.flat = true; " + JB + "C.inMode = 1;"),
    ('f10-flat-m-cross-bands', "S.flat = true; C.trap = 1; C.by = 0;"),
    ('f11-m-escape', B4 + "C.mode = 2;"),
    ('f12-m-depth', B4 + "C.mode = 4;"),
    ('f13-m-surface-dir', B4 + "C.mode = 6;"),
    ('f14-m-clay', B4 + "C.mode = 7;"),
    ('f15-j-escape', B4 + JB + "C.mode = 2; C.pal = 6;"),
    ('f16-k-escape', B4 + "mode('k'); C.mode = 2;"),
    ('f17-k-depth', B4 + "mode('k'); C.mode = 4;"),
    ('f18-m-neg2-escape', B4 + "S.n = -2; C.mode = 2;"),
    ('f19-m-centre', B4 + "C.mode = 3;"),
    ('f20-m-laststep', B4 + "C.mode = 5;"),
    ('f21-m-ultra-escape', "q('qUltra'); C.mode = 2;"),
    ('f22-m-fast-depth', "q('qFast'); C.mode = 4;"),
    ('f23-cut-m-hatch-escape', B4 + "S.cutOn = true; S.cut = 0; C.mode = 2;"),
    ('f24-cut-j-face-trap-escape', B4 + JB + "S.cutOn = true; S.cut = 0.1; C.cutFace = true; C.inMode = 1; C.mode = 2;"),
    ('f25-m-mosaic-escape', B4 + "S.mosaic = true; C.mode = 2;"),
    ('f26-k-clay', B4 + "mode('k'); C.mode = 7;"),
]
SUBJECTS = [('jb', JB), ('m', ""), ('jr', JR), ('k', "mode('k');")]
SETUPS = [
    ('shell1', "C.mode = 0; C.trap = 5; C.by = 4; C.radius = 1; C.glow = 1;"),
    ('shell07', "C.mode = 0; C.trap = 5; C.by = 4; C.radius = 0.7; C.glow = 1;"),
    ('cross', "C.mode = 0; C.trap = 1; C.by = 4; C.radius = 1; C.glow = 1;"),
    ('planes', "C.mode = 0; C.trap = 4; C.by = 0; C.radius = 1; C.glow = 1;"),
]
# Lighting made equal (no shadows, no crevice shading, 2 passes), so that what differs between two pictures is the
# colour of the surface and not the light on it. Everything else of a preset stays as the preset sets it.
EQ = " S.q.shadow = false; S.q.ao = false; S.q.aa = 2;"
IT = " S.iter = %d; S.k.iter = %d;"
VARS = [
    ('qB', "q('qBal');" + EQ),
    ('qU', "q('qUltra');" + EQ),
    ('qF', "q('qFast');" + EQ),
    ('qN', "q('qFine');" + EQ),
    ('d02', "q('qBal');" + EQ + " S.q.detail = 0.2;"),
    ('d3', "q('qBal');" + EQ + " S.q.detail = 3;"),
    ('i24', "q('qBal');" + EQ + IT % (24, 24)),
    ('i60', "q('qBal');" + EQ + IT % (60, 60)),
    ('i120', "q('qBal');" + EQ + IT % (120, 120)),
    ('z2', "q('qBal');" + EQ),
    ('z8', "q('qBal');" + EQ),
]
# The zoom is applied after the subject is chosen (choosing a mode frames the solid for the field of view in
# force, so set before it the zoom was undone: the first reference set had that mistake for jb, jr and k, and
# those pictures were drawn again). It narrows the field of view, so the middle of the picture is magnified exactly.
POST = {'z2': " S.view.fov /= 2;", 'z8': " S.view.fov /= 8;"}
ZOOM = {'z2': 2, 'z8': 8}
ACCEPT = [('a-%s-%s-%s' % (sn, un, vn), vj + sj + uj + POST.get(vn, '')) for sn, sj in SUBJECTS for un, uj in SETUPS for vn, vj in VARS]
SOLIDS = [
    ('s01-m-shell-bal', B4 + "C.solid = 1;"),
    ('s02-m-shell-fast', "q('qFast'); C.solid = 1;"),
    ('s03-m-shell-ultra', "q('qUltra'); C.solid = 1;"),
    ('s04-j-shell07-bal', B4 + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s05-j-shell07-fast', "q('qFast'); " + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s06-j-shell07-ultra', "q('qUltra'); " + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s07-j-cross-added-bal', B4 + JB + "C.trap = 1; C.solid = 2;"),
    ('s08-j-cross-added-ultra', "q('qUltra'); " + JB + "C.trap = 1; C.solid = 2;"),
    ('s09-k-shell-bal', B4 + "mode('k'); C.solid = 1;"),
    ('s10-k-shell-fast', "q('qFast'); mode('k'); C.solid = 1;"),
    ('s11-k-cross-added-bal', B4 + "mode('k'); C.trap = 1; C.solid = 2;"),
    ('s12-k-shell-added-ultra', "q('qUltra'); mode('k'); C.solid = 2;"),
    ('s13-m-cross-added-bal', B4 + "C.trap = 1; C.solid = 2;"),
    ('s14-m-shell-step-fast', "q('qFast'); C.solid = 1; C.by = 1;"),
    ('s15-j-ring-where-fine', "q('qFine'); S.q.aa = 6; " + JB + "C.trap = 6; C.radius = 0.7; C.by = 5; C.solid = 1;"),
    ('s16-m-shell-skip0-bal', B4 + "C.solid = 1; C.skip = 0;"),
    ('s17-j-shell-skip0-bal', B4 + JB + "C.solid = 1; C.skip = 0;"),
    ('s18-m-shell-skip2-bal', B4 + "C.solid = 1; C.skip = 2;"),
    ('s19-j-shell-added-fine', "q('qFine'); S.q.aa = 6; " + JB + "C.solid = 2; C.radius = 0.7;"),
    ('s20-m-shell-added-ultra', "q('qUltra'); C.solid = 2;"),
]
# Added after the first results, to cover what the acceptance list does not: an inside-out solid, the mosaic, the
# three-tone mix, and the "colours by" choices that are not nearness, each at two quality presets.
EXTRA = [
    ('x01-m-neg2-shell-bal', B4 + "S.n = -2;"),
    ('x02-m-neg2-shell-fast', "q('qFast'); S.n = -2;"),
    ('x03-m-mosaic-shell-bal', B4 + "S.mosaic = true;"),
    ('x04-m-mosaic-shell-ultra', "q('qUltra'); S.mosaic = true;"),
    ('x05-m-tones-bal', B4 + "C.trap = 7;"),
    ('x06-m-tones-ultra', "q('qUltra'); C.trap = 7;"),
    ('x07-j-shell-step-bal', B4 + JB + "C.by = 1;"),
    ('x08-j-shell-step-ultra', "q('qUltra'); " + JB + "C.by = 1;"),
    ('x09-j-cross-blend-bal', B4 + JB + "C.trap = 1; C.by = 2;"),
    ('x10-j-cross-blend-fast', "q('qFast'); " + JB + "C.trap = 1; C.by = 2;"),
    ('x11-j-line-side-bal', B4 + JB + "C.trap = 2; C.by = 3;"),
    ('x12-j-line-side-fine', "q('qFine'); S.q.aa = 6; " + JB + "C.trap = 2; C.by = 3;"),
    ('x13-classic8-shell-bal', B4 + "q('ap-classic'); S.n = 8; S.iter = 10;"),
    ('x14-classic8-shell-ultra', "q('qUltra'); q('ap-classic'); S.n = 8; S.iter = 10;"),
]
ALL = FIXED + ACCEPT + SOLIDS + EXTRA


def shoot(page, label, only=(), extra=None, size='1000x700'):
    folder = os.path.join(HERE, label)
    os.makedirs(folder, exist_ok=True)
    acts = [{'wait': 'done', 'timeout': 600}]
    todo = [(n, j) for n, j in (extra or ALL) if not only or any(n.startswith(o) or (o[:1] == '~' and o[1:] in n) for o in only)]
    for name, js in todo:
        acts.append({'js': PRE + RESET + js + "go(); return '" + name + "';"})
        acts.append({'sleep': 0.15})
        acts.append({'wait': 'done', 'timeout': 900, 'shot': 'out/r6/colour/%s/%s.png' % (label, name), 'clip': '#view'})
    tag = '-'.join(only)[:40].replace('~', '') if only else 'all'
    path = os.path.join(folder, '_actions-%s.json' % tag)
    json.dump(acts, open(path, 'w', encoding='utf-8'))
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path,
                        '--size', size], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=7200)
    out = (r.stdout or '') + (r.stderr or '')
    open(os.path.join(folder, '_log-%s.txt' % tag), 'w', encoding='utf-8').write(out)
    lines = out.strip().splitlines()
    print('%s -> %s (%d scenes): exit %d | %s' % (page, label, len(todo), r.returncode, lines[-1] if lines else ''))
    for l in lines:
        if 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l:
            print('   ', l[:400])
    return r.returncode


def load(label, name):
    from PIL import Image
    p = os.path.join(HERE, label, name + '.png')
    return Image.open(p).convert('RGB') if os.path.exists(p) else None


def cmp(a, b, names=None):
    import numpy as np
    worst, bad, n = 0, [], 0
    for name, _ in FIXED if names is None else names:
        x, y = load(a, name), load(b, name)
        if x is None or y is None:
            print('%-30s missing' % name); continue
        x, y = np.asarray(x).astype(int), np.asarray(y).astype(int)
        if x.shape != y.shape:
            print('%-30s sizes differ %s %s' % (name, x.shape, y.shape)); bad.append(name); continue
        d = np.abs(x - y).max(axis=2)
        mx = int(d.max()); worst = max(worst, mx); n += 1
        if mx > 0: bad.append(name)
        print('%-30s largest channel difference %3d   pixels that differ at all: %8.4f %%' % (name, mx, 100 * float((d > 0).mean())))
    print('%s against %s: %d scenes, largest difference %d; scenes that differ: %s' % (a, b, n, worst, ', '.join(bad) if bad else 'none'))


def measure(base, im, zoom=1):
    """Mean difference per channel over the solid, and the share of the solid whose hue moved by more than 30 degrees.
    Both pictures are halved first. zoom: im shows the middle of base magnified that many times."""
    import numpy as np
    from PIL import Image
    w, h = base.size
    if zoom > 1:
        cw, ch = w / zoom, h / zoom
        base = base.resize((w, h), Image.LANCZOS, box=((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2))
        # the magnified picture is blurred to what the cut-out can hold, so that only colours are compared
        im = im.resize((max(1, round(cw)), max(1, round(ch))), Image.LANCZOS).resize((w, h), Image.LANCZOS)
    small = (w // 2, h // 2)
    bs, ims = base.resize(small, Image.LANCZOS), im.resize(small, Image.LANCZOS)
    x = np.asarray(bs).astype(float); y = np.asarray(ims).astype(float)
    hx = np.asarray(bs.convert('HSV')).astype(float); hy = np.asarray(ims.convert('HSV')).astype(float)
    obj = (x.max(axis=2) > 40) & (y.max(axis=2) > 40)      # both show the solid here (the stage is nearly black)
    if obj.sum() < 50: return None
    mean = float(np.abs(x - y)[obj].mean())
    # away from the outline (the solid is a little fatter at a coarser setting, which moves its edge, not its colours)
    from PIL import ImageFilter
    inner = np.asarray(Image.fromarray((obj * 255).astype('uint8')).filter(ImageFilter.MinFilter(9))) > 0
    mean_in = float(np.abs(x - y)[inner].mean()) if inner.sum() > 50 else mean
    vivid = obj & (hx[..., 1] > 70) & (hy[..., 1] > 70)
    dh = np.abs(hx[..., 0] - hy[..., 0]); dh = np.minimum(dh, 255 - dh) * 360 / 255
    hue = float((dh[vivid] > 30).mean()) if vivid.sum() else 0.0
    return mean, 100 * hue, mean_in


def accept(label, quiet=False):
    rows, worst = [], {}
    for sn, _ in SUBJECTS:
        for un, _ in SETUPS:
            base = load(label, 'a-%s-%s-qB' % (sn, un))
            if base is None: continue
            line = '%-3s %-8s' % (sn, un)
            for vn, _ in VARS[1:]:
                im = load(label, 'a-%s-%s-%s' % (sn, un, vn))
                # 60 and 120 iterations are held against 24: from 14 (Balanced as it opens) to 24 the solid itself changes
                ref = load(label, 'a-%s-%s-i24' % (sn, un)) if vn in ('i60', 'i120') else base
                m = measure(ref, im, ZOOM.get(vn, 1)) if im is not None and ref is not None else None
                if m is None: line += ' %4s  missing        ' % vn; continue
                line += ' %4s %4.1f %4.1f %3.0f%%' % (vn, m[0], m[2], m[1])
                w = worst.setdefault(vn, [0, 0, 0, 0, 0, 0]); w[0] = max(w[0], m[0]); w[1] = max(w[1], m[1]); w[2] += m[0]; w[3] += 1; w[4] = max(w[4], m[2]); w[5] += m[2]
            rows.append(line)
    if not quiet:
        print('%s: each variation against Balanced (i60 and i120 against i24). Three numbers each: mean difference per channel over the solid (of 255); the same away from the outline; share of the solid whose hue moved more than 30 degrees' % label)
        for r in rows: print(r)
        print('over the %d set-ups, worst (average) of: whole solid | away from the outline | hue share' % len(rows))
        for k, v in worst.items(): print('  %-5s %5.1f (%4.1f) | %5.1f (%4.1f) | %3.0f%%' % (k, v[0], v[2] / max(v[3], 1), v[4], v[5] / max(v[3], 1), v[1]))
    return worst


def tile(label, name, w, text=None):
    from PIL import Image, ImageDraw
    im = load(label, name)
    if im is None: im = Image.new('RGB', (w, round(w * 0.8)), (60, 0, 0))
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    ImageDraw.Draw(im).text((4, 2), text or name, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    return im


def grid(tiles, cols, out):
    from PIL import Image
    w = max(t.width for t in tiles); h = max(t.height for t in tiles); rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * h), (20, 20, 24))
    for i, t in enumerate(tiles): S.paste(t, ((i % cols) * w, (i // cols) * h))
    S.save(os.path.join(HERE, out)); print('wrote out/r6/colour/' + out, S.size)


def sheets(a, b=None, w=250):
    order = ['qU', 'qF', 'qB', 'qN', 'd02', 'd3', 'i24', 'i60', 'i120', 'z2', 'z8']
    for sn, _ in SUBJECTS:
        for un, _ in SETUPS:
            if load(a, 'a-%s-%s-qB' % (sn, un)) is None: continue
            tiles = [tile(lab, 'a-%s-%s-%s' % (sn, un, vn), w, '%s %s %s %s' % (lab, sn, un, vn)) for lab in ([a, b] if b else [a]) for vn in order]
            grid(tiles, len(order), 'pair-%s-%s-%s.png' % (sn, un, (a + '-' + b) if b else a))
    for lab in ([a, b] if b else [a]):
        for lst, nm, cols in ((FIXED, 'fixed', 7), (SOLIDS, 'solids', 5), (EXTRA, 'extra', 4)):
            if any(load(lab, n) is not None for n, _ in lst):
                grid([tile(lab, n, 300, lab + ' ' + n) for n, _ in lst], cols, 'sheet-%s-%s.png' % (nm, lab))
    if b:
        grid([tile(lab, n, 300, lab + ' ' + n) for n, _ in SOLIDS for lab in (a, b)], 6, 'pairs-solids-%s-%s.png' % (a, b))


if __name__ == '__main__':
    if sys.argv[1] == 'shoot': sys.exit(shoot(sys.argv[2], sys.argv[3], sys.argv[4:]))
    elif sys.argv[1] == 'cmp': cmp(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'accept': accept(sys.argv[2])
    elif sys.argv[1] == 'sheets': sheets(*sys.argv[2:4])
