"""The fixed list of scenes for round 5 (speed), and the comparison of two sets of pictures of it.

  python out/r5/speed/scenes.py shoot <page> <label> [name-prefix ...]   draw the list on dist/<page>.html into out/r5/speed/<label>/
  python out/r5/speed/scenes.py cmp <labelA> <labelB>                    per scene: largest channel difference, share of pixels over 2 of 255
  python out/r5/speed/scenes.py sheet <label>                            one contact sheet of a set

Every scene starts from "Reset everything". The list is fixed: the reference set (label ref, from dist/v6a.html)
was drawn before any source was changed.
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
JB = "mode('j'); S.c = [-1, 0, 0];"    # the Basilica
JR = "mode('j'); S.c = [-0.123, 0.745, 0];"   # the Douady rabbit
SCENES = [
    ('01-m-open', ""),                                   # the opening view, opening settings
    ('02-j-basilica', B4 + JB),
    ('03-k-open', "mode('k');"),
    ('04-m-solid1-shell', B4 + "C.solid = 1;"),
    ('05-j-solid2-cross', B4 + JB + "C.trap = 1; C.solid = 2;"),
    ('06-j-solid1-ring-where', B4 + JB + "C.trap = 6; C.radius = 0.7; C.by = 5; C.solid = 1;"),
    ('07-k-solid1-shell', B4 + "mode('k'); C.solid = 1;"),
    ('08-k-solid2-cross-step', B4 + "mode('k'); C.trap = 1; C.by = 1; C.solid = 2;"),
    ('09-m-cross-bands', B4 + "C.trap = 1; C.by = 0;"),
    ('10-j-planes-step', B4 + JR + "C.trap = 4; C.by = 1; C.pal = 6;"),
    ('11-m-tones', B4 + "C.trap = 7;"),
    ('12-m-line-side', B4 + "C.trap = 2; C.by = 3;"),
    ('13-m-escape', B4 + "C.mode = 2; C.pal = 6;"),
    ('14-m-laststep', B4 + "C.mode = 5;"),
    ('15-m-surface-dir', B4 + "C.mode = 6;"),
    ('16-m-depth', B4 + "C.mode = 4;"),
    ('17-flat-m-open', "S.flat = true;"),                # also compared with base4: must be identical
    ('18-flat-m-in-trap', "S.flat = true; C.inMode = 1;"),
    ('19-flat-j-in-settle', "S.flat = true; " + JB + "C.inMode = 4; C.inPal = 6; C.edge = 2; C.edgeGlow = 10;"),
    ('20-flat-m-in-deep', "S.flat = true; C.inMode = 3; C.inPal = 5; C.inRev = true;"),
    ('21-flat-j-in-ends', "S.flat = true; " + JR + "C.inMode = 2;"),
    ('22-flat-k', "S.flat = true; mode('k');"),
    ('23-cut-m-hatch', B4 + "S.cutOn = true; S.cut = 0;"),
    ('24-cut-m-face-settle', B4 + "S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 4;"),
    ('25-cut-j-face-trap', B4 + JB + "S.cutOn = true; S.cut = 0.1; C.cutFace = true; C.inMode = 1; C.inPal = 6;"),
    ('26-cut-j-solid1-shell', B4 + JB + "S.cutOn = true; S.cut = 0; C.solid = 1;"),
    ('27-m-ultra', "q('qUltra');"),
    ('28-m-ultra-solid1', "q('qUltra'); C.solid = 1;"),
    ('29-j-fine', "q('qFine'); " + JB),
    ('30-m-mosaic', B4 + "q('m-mosaic');"),
    ('31-m-mosaic-flat', "q('m-mosaic'); S.flat = true;"),
    ('32-m-neg2', B4 + "S.n = -2;"),
    ('33-classic8', B4 + "q('ap-classic'); S.n = 8; S.iter = 10;"),
    ('34-k-cross-bands', B4 + "mode('k'); C.trap = 1; C.by = 0;"),
    ('35-flat-m-solid-asked', "S.flat = true; C.solid = 1;"),
    ('36-k-cut-face-ends', B4 + "mode('k'); S.cutOn = true; S.cut = 0.2; C.cutFace = true; C.inMode = 2;"),
    ('37-j-fast-solid2-shell-step', "q('qFast'); " + JB + "C.solid = 2; C.by = 1;"),
    ('38-m-cut-face-deep-solid1', B4 + "S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 3; C.solid = 1;"),
    # added after the first comparison, when reading the code showed a case the list did not cover (the cut face
    # painted with the inside left Plain: no hatching); its reference picture is from dist/v6a.html like the rest
    ('39-cut-m-face-plain', B4 + "S.cutOn = true; S.cut = 0; C.cutFace = true;"),
    ('40-cut-j-face-plain-flat-inside', "S.flat = true; " + JB + "C.cutFace = true; C.inMode = 2;"),
]

# A second list, for the trap solids' colours at the quality presets (the optional item (a) of SPEC5): drawn only
# when asked for by prefix ("s"), before and after that change. It is not part of the fixed list above.
SOLIDS = [
    ('s01-m-shell-glow-bal', B4 + "C.solid = 1;"),
    ('s02-m-shell-glow-fast', "q('qFast'); C.solid = 1;"),
    ('s03-m-shell-glow-ultra', "q('qUltra'); C.solid = 1;"),
    ('s04-j-shell-glow-fast', "q('qFast'); " + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s05-j-shell-glow-ultra', "q('qUltra'); " + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s06-j-cross-added-bal', B4 + JB + "C.trap = 1; C.solid = 2;"),
    ('s07-j-cross-added-fast', "q('qFast'); " + JB + "C.trap = 1; C.solid = 2;"),
    ('s08-j-cross-bands-ultra', "q('qUltra'); " + JB + "C.trap = 1; C.solid = 1; C.by = 0;"),
    ('s09-k-shell-glow-bal', B4 + "mode('k'); C.solid = 1;"),
    ('s10-k-shell-glow-fast', "q('qFast'); mode('k'); C.solid = 1;"),
    ('s11-k-cross-added-bal', B4 + "mode('k'); C.trap = 1; C.solid = 2;"),
    ('s12-k-shell-added-ultra', "q('qUltra'); mode('k'); C.solid = 2;"),
    ('s13-j-ring-blend-fine', "q('qFine'); S.q.aa = 8; " + JB + "C.trap = 6; C.radius = 0.7; C.by = 2; C.solid = 1;"),
    ('s14-m-shell-step-fast', "q('qFast'); C.solid = 1; C.by = 1;"),
    ('s15-j-shell-glow-bal', B4 + JB + "C.solid = 1; C.radius = 0.7;"),
    ('s16-j-shell-added-ultra', "q('qUltra'); " + JB + "C.solid = 2; C.radius = 0.7;"),
]


def shoot(page, label, only=()):
    folder = os.path.join(HERE, label)
    os.makedirs(folder, exist_ok=True)
    acts = [{'wait': 'done', 'timeout': 400}]
    for name, js in (SCENES + SOLIDS if only else SCENES):
        if only and not any(name.startswith(o) for o in only):
            continue
        acts.append({'js': PRE + RESET + js + "go(); return '" + name + "';"})
        acts.append({'sleep': 0.15})
        acts.append({'wait': 'done', 'timeout': 600, 'shot': 'out/r5/speed/%s/%s.png' % (label, name), 'clip': '#view'})
    path = os.path.join(folder, '_actions.json')
    json.dump(acts, open(path, 'w', encoding='utf-8'))
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path,
                        '--size', '1000x700'], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
    out = (r.stdout or '') + (r.stderr or '')
    open(os.path.join(folder, '_log.txt'), 'w', encoding='utf-8').write(out)
    lines = out.strip().splitlines()
    print('%s -> %s: exit %d | %s' % (page, label, r.returncode, lines[-1] if lines else ''))
    for l in lines:
        if 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l:
            print('   ', l[:400])
    return r.returncode


def cmp(a, b):
    import numpy as np
    from PIL import Image
    worst, bad = 0, []
    for name, _ in SCENES + SOLIDS:
        pa, pb = os.path.join(HERE, a, name + '.png'), os.path.join(HERE, b, name + '.png')
        if not (os.path.exists(pa) or os.path.exists(pb)):
            continue
        if not (os.path.exists(pa) and os.path.exists(pb)):
            print('%-30s missing' % name); continue
        x = np.asarray(Image.open(pa).convert('RGB')).astype(int); y = np.asarray(Image.open(pb).convert('RGB')).astype(int)
        if x.shape != y.shape:
            print('%-30s sizes differ %s %s' % (name, x.shape, y.shape)); bad.append(name); continue
        d = np.abs(x - y).max(axis=2)
        mx, over = int(d.max()), float((d > 2).mean())
        worst = max(worst, mx)
        if mx > 2: bad.append(name)
        print('%-30s largest channel difference %3d   pixels over 2 of 255: %8.4f %%   pixels that differ at all: %8.4f %%' % (name, mx, 100 * over, 100 * float((d > 0).mean())))
    print('%s against %s: largest difference %d; scenes over 2 of 255: %s' % (a, b, worst, ', '.join(bad) if bad else 'none'))


def sheet(label, cols=6, w=300):
    from PIL import Image, ImageDraw
    tiles = []
    for name, _ in SCENES + SOLIDS:
        p = os.path.join(HERE, label, name + '.png')
        if not os.path.exists(p): continue
        im = Image.open(p).convert('RGB'); im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        ImageDraw.Draw(im).text((5, 3), name, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        tiles.append(im)
    h = max(t.height for t in tiles); rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * h), (20, 20, 24))
    for i, t in enumerate(tiles): S.paste(t, ((i % cols) * w, (i // cols) * h))
    out = os.path.join(HERE, 'sheet-%s.png' % label); S.save(out); print('wrote', out)


if __name__ == '__main__':
    if sys.argv[1] == 'shoot': sys.exit(shoot(sys.argv[2], sys.argv[3], sys.argv[4:]))
    elif sys.argv[1] == 'cmp': cmp(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'sheet': sheet(sys.argv[2])
