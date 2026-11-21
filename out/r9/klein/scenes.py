"""Fixed lists of scenes for round 9 (engineer "klein"), and comparisons of two sets of pictures of them.

  python out/r9/klein/scenes.py shoot <page> <label> [prefix ...]   draw the scenes whose names start with a prefix
                                                                    (all when none is given) on dist/<page>.html into
                                                                    out/r9/klein/<label>/
  python out/r9/klein/scenes.py cmp <labelA> <labelB> [prefix ...]  largest channel difference per scene (default: the
                                                                    lists that must not change, prefixes f, g and s)
  python out/r9/klein/scenes.py pairs <labelA> <labelB> <out.png> <scale> <prefix> [...]   A above B, per scene

Every scene starts from "Reset everything". Lists (the model is out/r7/engine/scenes.py):
  FIXED   f.. the 2D view and 3D pictures not coloured by a trap; g.. trap-coloured 3D pictures;
          s.. the trap solids of Mandelbrot and Julia sets (the six examples and the usual shapes). 1000 x 700.
  DEFECT  k.. kleinian-1; p.. solids-5 (the tester's scenes of out/t6/solids/pj.json); w.. words-4 and words-5.
          1400 x 950, as the testers drew them.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, cam = L.cam, $ = id => document.getElementById(id);"
       "if (L.R) L.R.warmOn = false;"
       "const go = () => { L.syncControls(); L.refresh(false); L.touch(); };"
       "const mode = m => $('mode-' + m).click();"
       "const q = id => $(id).click();"
       "const ex = i => L.applyExample(L.EXAMPLES[i]);"
       "const kp = v => { const s = $('kleinPreset'); s.value = String(v); s.dispatchEvent(new Event('change', { bubbles: true })); $('kleinFrame').click(); };")
RESET = "L.resetAll();"
B4 = "q('qBal'); S.q.aa = 4;"
F4 = "q('qFine'); S.q.aa = 4;"
JB = "mode('j'); S.c = [-1, 0, 0];"
JR = "mode('j'); S.c = [-0.123, 0.745, 0];"
J3 = "mode('j'); S.c = [0, 1, 0];"
JS07 = JB + "C.trap = 5; C.solid = 1; C.radius = 0.7;"     # the tester's chain of bubbles
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
    ('f13-j-depth', B4 + JB + "C.mode = 4;"),
    ('f14-m-clay', B4 + "C.mode = 7;"),
    ('f15-j-escape', B4 + JB + "C.mode = 2; C.pal = 6;"),
    ('f16-k-escape', B4 + "mode('k'); C.mode = 2;"),
    ('f18-m-neg2-escape', B4 + "S.n = -2; C.mode = 2;"),
    ('f21-m-ultra-escape', "q('qUltra'); C.mode = 2;"),
    ('f23-cut-m-hatch-escape', B4 + "S.cutOn = true; S.cut = 0; C.mode = 2;"),
    ('f24-cut-j-face-trap-escape', B4 + JB + "S.cutOn = true; S.cut = 0.1; C.cutFace = true; C.inMode = 1; C.mode = 2;"),
    ('f25-m-mosaic-escape', B4 + "S.mosaic = true; C.mode = 2;"),
    ('f26-flat-k-e08', "mode('k'); kp(9); S.flat = true;"),
    ('g01-m-open', B4),
    ('g02-j-open', B4 + JB),
    ('g03-k-open', B4 + "mode('k');"),
    ('g04-j-fine', F4 + JB),
    ('g05-jr-open', B4 + JR),
    ('g06-m-neg2', B4 + "S.n = -2;"),
    ('g07-m-mosaic', B4 + "S.mosaic = true;"),
    ('g08-j-ultra', "q('qUltra'); " + JB),
    ('g09-k-cross-bands-fast', "q('qFast'); mode('k'); C.trap = 1; C.by = 0;"),
    ('g10-k-e03-colours', B4 + "mode('k'); kp(4);"),
    ('g11-k-e33-fine', F4 + "mode('k'); kp(34);"),
    # the trap solids of Mandelbrot and Julia sets
    ('s01-ex0-m-coral', B4 + "ex(0);"),
    ('s02-ex1-m-discs', B4 + "ex(1);"),
    ('s03-ex2-m-rings', B4 + "ex(2);"),
    ('s04-ex3-j-bubbles', B4 + "ex(3);"),
    ('s05-ex4-j-urchins', B4 + "ex(4);"),
    ('s06-ex5-jr-arches', B4 + "ex(5);"),
    ('s07-m-shell-is', B4 + "C.solid = 1;"),
    ('s08-m-shell-added', B4 + "C.solid = 2;"),
    ('s09-j-shell1-is', B4 + JB + "C.solid = 1;"),
    ('s10-jr-ring-added', B4 + JR + "C.trap = 6; C.solid = 2;"),
    ('s11-j-bubbles-fine', F4 + JS07),
    ('s12-j-bubbles-ultra', "q('qUltra'); " + JS07),
    ('s13-m-coral-fine', F4 + "ex(0);"),
    ('s14-j-bubbles-thick002', B4 + JS07 + "C.thick = 0.02;"),
    ('s15-m-cross-step', B4 + "C.trap = 1; C.solid = 1; C.by = 1;"),
    ('s16-j-bubbles-cut', B4 + JS07 + "S.cutOn = true; S.cut = 0;"),
    ('s17-m-mosaic-shell', B4 + "S.mosaic = true; C.solid = 1;"),
]
KE = lambda n: "mode('k'); kp(%d);" % n
SIDE = JR + "cam.yaw = -1.571; cam.pitch = 0.12; cam.dist = 4.6; cam.target = [0, 0, 0];"
W5 = "cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0];"
SHAPES = [(0, 'point'), (1, 'cross'), (2, 'line'), (3, 'ray'), (4, 'planes'), (5, 'shell'), (6, 'ring')]
DEFECT = [
    # kleinian-1: the tester's reproduction (entries 3 and 24), and what the assignment names
    ('k01-e03-is', B4 + KE(4) + "C.solid = 1;"),
    ('k02-e24-is', B4 + KE(25) + "C.solid = 1;"),
    ('k03-e03-added', B4 + KE(4) + "C.solid = 2;"),
    ('k04-e24-added', B4 + KE(25) + "C.solid = 2;"),
    ('k05-e03-is-fine', F4 + KE(4) + "C.solid = 1;"),
    ('k06-e24-is-fine', F4 + KE(25) + "C.solid = 1;"),
    ('k07-e03-is-fine-far', F4 + KE(4) + "C.solid = 1; cam.dist = 20;"),
    ('k08-e00-is', B4 + KE(1) + "C.solid = 1;"),
    ('k09-e21-is', B4 + KE(22) + "C.solid = 1;"),
    ('k10-e00-tx06', B4 + KE(1) + "C.solid = 1; C.tx = 0.6;"),
    ('k11-e00-tx06-fine', F4 + KE(1) + "C.solid = 1; C.tx = 0.6;"),
    ('k12-e00-ty05', B4 + KE(1) + "C.solid = 1; C.ty = 0.5;"),
    ('k13-e00-tz06', B4 + KE(1) + "C.solid = 1; C.tz = 0.6;"),
    ('k14-e33-is', B4 + KE(34) + "C.solid = 1;"),
    ('k15-ex6-pearls', B4 + "ex(6);"),
    ('k16-ex7-rings', B4 + "ex(7);"),
    ('k17-ex8-discs', B4 + "ex(8);"),
    ('k18-ex6-pearls-fine', F4 + "ex(6);"),
    ('k19-ex7-rings-fine', F4 + "ex(7);"),
    ('k20-ex8-discs-fine', F4 + "ex(8);"),
] + [('k3%d-e00-%s' % (t, n), B4 + KE(1) + "C.trap = %d; C.solid = 1;" % t) for t, n in SHAPES] \
  + [('k4%d-e00-%s-fine' % (t, n), F4 + KE(1) + "C.trap = %d; C.solid = 1;" % t) for t, n in SHAPES] \
  + [('k5%d-e03-%s' % (t, n), B4 + KE(4) + "C.trap = %d; C.solid = 1;" % t) for t, n in SHAPES if t != 5] + [
    ('k60-e03-is-skip0', B4 + KE(4) + "C.solid = 1; C.skip = 0;"),
    ('k61-e00-is-skip0', B4 + KE(1) + "C.solid = 1; C.skip = 0;"),
    ('k62-e03-is-skip3', B4 + KE(4) + "C.solid = 1; C.skip = 3;"),
    ('k63-e00-ring-r16', B4 + KE(1) + "C.trap = 6; C.solid = 1; C.radius = 1.6;"),
    ('k64-e00-ring-thick02', B4 + KE(1) + "C.trap = 6; C.solid = 1; C.thick = 0.2;"),
    ('k65-e03-is-ultra', "q('qUltra'); " + KE(4) + "C.solid = 1;"),
    ('k66-e03-is-cut', B4 + KE(4) + "C.solid = 1; S.cutOn = true; S.cut = 0;"),
    # solids-5: out/t6/solids/pj.json steps 7, 8, 9, 14, 15 and the clean ones beside them
    ('p01-j-base', B4 + JS07),
    ('p02-j-skip2', B4 + JS07 + "C.skip = 2;"),
    ('p03-j-skip3', B4 + JS07 + "C.skip = 3;"),
    ('p04-j-skip6', B4 + JS07 + "C.skip = 6;"),
    ('p05-j-tx05', B4 + JS07 + "C.tx = 0.5;"),
    ('p06-j-ty05', B4 + JS07 + "C.ty = 0.5;"),
    ('p07-j-radius02', B4 + JS07 + "C.radius = 0.2;"),
    ('p08-j-radius05', B4 + JS07 + "C.radius = 0.5;"),
    ('p09-j-skip3-fine', F4 + JS07 + "C.skip = 3;"),
    ('p10-j-tz05', B4 + JS07 + "C.tz = 0.5;"),
    ('p11-m-cross-skip3', B4 + "C.trap = 1; C.solid = 1; C.skip = 3;"),
    ('p12-j-skip4', B4 + JS07 + "C.skip = 4;"),
    # words-4 and words-5
    ('w01-words-4-rough', B4 + SIDE + "S.q.de = 0;"),
    ('w02-words-4-exact', B4 + SIDE + "S.q.de = 3;"),
    ('w03-words-5-ultra-i40', "q('qUltra'); " + JB + "S.iter = 40; " + W5),
    ('w04-words-5-ultra-i14', "q('qUltra'); " + JB + W5),
    ('w05-words-5-bal-i40', B4 + JB + "S.iter = 40; " + W5),
]
ALL = FIXED + DEFECT


def shoot(page, label, only=(), extra=None, size=None):
    folder = os.path.join(HERE, label)
    os.makedirs(folder, exist_ok=True)
    todo = [(n, j) for n, j in (extra or ALL) if not only or any(n.startswith(o) or (o[:1] == '~' and o[1:] in n) for o in only)]
    rc = 0
    # the lists that must not change at 1000 x 700, the testers' reproductions at their size, 1400 x 950
    for group, sz in ((('f', 'g', 's'), '1000x700'), (('k', 'p', 'w', 'x'), '1400x950')):
        part = [(n, j) for n, j in todo if n[0] in group]
        if not part: continue
        acts = [{'wait': 'done', 'timeout': 600}]
        for name, js in part:
            acts.append({'js': PRE + RESET + js + "go(); return '" + name + " three=' + S.k.three + ' kmx=' + S.k.mx + ' skip=' + C.skip + ' iter=' + S.iter + ' note=' + [...document.querySelectorAll('.note, .hint')].filter(e => !e.hidden && e.offsetParent && /cut open|leans|repeats/.test(e.textContent)).map(e => e.textContent.slice(0, 60)).join(' / ');"})
            acts.append({'sleep': 0.15})
            acts.append({'wait': 'done', 'timeout': 900, 'shot': 'out/r9/klein/%s/%s.png' % (label, name), 'clip': '#view'})
        tag = (group[0] + '-' + '-'.join(only)[:40].replace('~', '')) if only else group[0] + '-all'
        path = os.path.join(folder, '_actions-%s.json' % tag)
        json.dump(acts, open(path, 'w', encoding='utf-8'))
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path,
                            '--size', size or sz], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=7200)
        out = (r.stdout or '') + (r.stderr or '')
        open(os.path.join(folder, '_log-%s.txt' % tag), 'w', encoding='utf-8').write(out)
        lines = out.strip().splitlines()
        print('%s -> %s (%d scenes, %s): exit %d | %s' % (page, label, len(part), size or sz, r.returncode, lines[-1] if lines else ''))
        for l in lines:
            if 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l:
                print('   ', l[:400])
        rc = rc or r.returncode
    return rc


def load(label, name):
    from PIL import Image
    p = os.path.join(HERE, label, name + '.png')
    return Image.open(p).convert('RGB') if os.path.exists(p) else None


def cmp(a, b, only=('f', 'g', 's')):
    import numpy as np
    worst, bad, n = 0, [], 0
    for name, _ in ALL:
        if not any(name.startswith(o) for o in only): continue
        x, y = load(a, name), load(b, name)
        if x is None or y is None:
            print('%-34s missing' % name); continue
        x, y = np.asarray(x).astype(int), np.asarray(y).astype(int)
        if x.shape != y.shape:
            print('%-34s sizes differ %s %s' % (name, x.shape, y.shape)); bad.append(name); continue
        d = np.abs(x - y).max(axis=2)
        mx = int(d.max()); worst = max(worst, mx); n += 1
        if mx > 0: bad.append(name)
        print('%-34s largest channel difference %3d   pixels that differ at all: %8.4f %%   over 8: %8.4f %%' % (name, mx, 100 * float((d > 0).mean()), 100 * float((d > 8).mean())))
    print('%s against %s: %d scenes, largest difference %d; scenes that differ: %s' % (a, b, n, worst, ', '.join(bad) if bad else 'none'))


def pairs(a, b, out, scale, only):
    from PIL import Image, ImageDraw
    names = [n for n, _ in ALL if any(n.startswith(o) for o in only) and load(a, n) is not None and load(b, n) is not None]
    if not names: print('nothing to pair'); return
    ims = [(load(a, n), load(b, n)) for n in names]
    w = int(max(i[0].size[0] for i in ims) * scale); h = int(max(i[0].size[1] for i in ims) * scale)
    cols = min(len(names), 4); rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * (2 * h + 20)), (20, 22, 28))
    d = ImageDraw.Draw(sheet)
    for k, (n, (x, y)) in enumerate(zip(names, ims)):
        px, py = (k % cols) * w, (k // cols) * (2 * h + 20)
        sheet.paste(x.resize((w, h), Image.LANCZOS), (px, py + 18))
        sheet.paste(y.resize((w, h), Image.LANCZOS), (px, py + 18 + h))
        d.text((px + 4, py + 3), n + '  (%s above %s)' % (a, b), fill=(230, 230, 230))
    sheet.save(os.path.join(ROOT, out)); print('wrote', out, sheet.size)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'shoot': sys.exit(shoot(sys.argv[2], sys.argv[3], sys.argv[4:]))
    elif cmd == 'cmp': cmp(sys.argv[2], sys.argv[3], tuple(sys.argv[4:]) or ('f', 'g', 's'))
    elif cmd == 'pairs': pairs(sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), tuple(sys.argv[6:]))
