"""Fixed lists of scenes for round 7 (engine), and comparisons of two sets of pictures of them.

  python out/r7/engine/scenes.py shoot <page> <label> [prefix ...]   draw the scenes whose names start with a prefix
                                                                     (all when none is given) on dist/<page>.html into
                                                                     out/r7/engine/<label>/
  python out/r7/engine/scenes.py cmp <labelA> <labelB> [prefix ...]  largest channel difference per scene (default: the
                                                                     list that must not change, prefixes f and g)
  python out/r7/engine/scenes.py pairs <labelA> <labelB> <out.png> <scale> <prefix> [...]   A above B, per scene

Every scene starts from "Reset everything". Lists:
  FIXED   f.. the 2D view and 3D pictures not coloured by a trap; g.. trap-coloured 3D pictures not named in a defect.
          These must be identical before and after.
  DEFECT  d-<defect id>-..  the testers' reproductions, set through the state (the same values the controls set).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, cam = L.cam, $ = id => document.getElementById(id);"
       "if (L.R) L.R.warmOn = false;"
       "const go = () => { L.syncControls(); L.refresh(false); L.touch(); };"
       "const mode = m => $('mode-' + m).click();"
       "const q = id => $(id).click();"
       "const kp = v => { const s = $('kleinPreset'); s.value = String(v); s.dispatchEvent(new Event('change', { bubbles: true })); $('kleinFrame').click(); };")
RESET = "L.resetAll();"
B4 = "q('qBal'); S.q.aa = 4;"
JB = "mode('j'); S.c = [-1, 0, 0];"
JR = "mode('j'); S.c = [-0.123, 0.745, 0];"
J3 = "mode('j'); S.c = [0, 1, 0];"
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
    ('g01-m-open', B4),
    ('g02-j-open', B4 + JB),
    ('g03-k-open', B4 + "mode('k');"),
    ('g04-j-fine', "q('qFine'); S.q.aa = 4; " + JB),
    ('g05-jr-open', B4 + JR),
    ('g06-m-neg2', B4 + "S.n = -2;"),
    ('g07-m-mosaic', B4 + "S.mosaic = true;"),
    ('g08-j-ultra', "q('qUltra'); " + JB),
    ('g09-k-cross-bands-fast', "q('qFast'); mode('k'); C.trap = 1; C.by = 0;"),
]
JS07 = B4 + JB + "C.trap = 5; C.solid = 1; C.radius = 0.7;"     # the tester's chain of bubbles
MX = B4 + "C.trap = 1; C.solid = 1;"                            # Mandelbrot, cross is the solid (dial 1 = the tester's skip 2)
KS = B4 + "mode('k'); C.solid = 1;"
SIDE = JR + "cam.yaw = -1.571; cam.pitch = 0.12; cam.dist = 4.6; cam.target = [0, 0, 0];"
SEA = "S.flat = true; S.iter = %d; S.v2.x = -0.7453; S.v2.y = 0.1127; S.v2.h = %s;"
DEFECT = [
    ('d-kleinian-1-e03-is', B4 + "mode('k'); kp(4); C.solid = 1;"),
    ('d-kleinian-1-e24-is', B4 + "mode('k'); kp(25); C.solid = 1;"),
    ('d-kleinian-1-e03-added', B4 + "mode('k'); kp(4); C.solid = 2;"),
    ('d-kleinian-1-e24-added', B4 + "mode('k'); kp(25); C.solid = 2;"),
    ('d-kleinian-1-e00-is', B4 + "mode('k'); kp(1); C.solid = 1;"),
    ('d-kleinian-1-e21-is', B4 + "mode('k'); kp(22); C.solid = 1;"),
    ('d-kleinian-1-e03-far', B4 + "mode('k'); kp(4); C.solid = 1; cam.dist = 20;"),
    ('d-kleinian-1-e03-colours', B4 + "mode('k'); kp(4);"),
    ('d-solids-1-m-cross-skip0', B4 + "C.trap = 1; C.solid = 1; C.skip = 0;"),
    ('d-solids-1-m-shell-skip0', B4 + "C.solid = 1; C.skip = 0;"),
    ('d-solids-2-j-thick0005', JS07 + "C.thick = 0.005;"),
    ('d-solids-2-j-thick002', JS07 + "C.thick = 0.02;"),
    ('d-solids-2-j-thick005', JS07),
    ('d-solids-2-j-thick015', JS07 + "C.thick = 0.15;"),
    ('d-solids-2-m-thick001', MX + "C.thick = 0.01;"),
    ('d-solids-2-m-thick005', MX),
    ('d-solids-2-k-thick001', KS + "C.trap = 6; C.thick = 0.01;"),
    ('d-solids-5-j-skip2', JS07 + "C.skip = 2;"),
    ('d-solids-5-j-skip3', JS07 + "C.skip = 3;"),
    ('d-solids-5-j-skip6', JS07 + "C.skip = 6;"),
    ('d-solids-5-j-tx05', JS07 + "C.tx = 0.5;"),
    ('d-solids-5-j-ty05', JS07 + "C.ty = 0.5;"),
    ('d-solids-5-j-radius02', JS07 + "C.radius = 0.2;"),
    ('d-solids-4-k-point', KS + "C.trap = 0;"),
    ('d-solids-4-k-line', KS + "C.trap = 2;"),
    ('d-solids-4-k-ray', KS + "C.trap = 3;"),
    ('d-solids-4-k-shell', KS),
    ('d-solids-4-j-point', B4 + JB + "C.trap = 0; C.solid = 1;"),
    ('d-solids-4-j-line', B4 + JB + "C.trap = 2; C.solid = 1;"),
    ('d-solids-4-j-ray', B4 + JB + "C.trap = 3; C.solid = 1;"),
    ('d-solids-3-m-point', B4 + "C.trap = 0; C.solid = 1;"),
    ('d-solids-3-m-ray', B4 + "C.trap = 3; C.solid = 1;"),
    ('d-solids-3-j3-point', B4 + J3 + "C.trap = 0; C.solid = 1;"),
    ('d-solids-3-j3-ray', B4 + J3 + "C.trap = 3; C.solid = 1;"),
    ('d-flat-2-k-in4', "S.flat = true; mode('k'); C.inMode = 4;"),
    ('d-flat-2-k-in3', "S.flat = true; mode('k'); C.inMode = 3;"),
    ('d-flat-3-cut-in3', B4 + "S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 3; cam.pitch = 1.1;"),
    ('d-flat-3-flat-in3', "S.flat = true; C.inMode = 3;"),
    ('d-flat-3-cut-in2', B4 + "S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 2; cam.pitch = 1.1;"),
    ('d-flat-3-cut-j-in3', B4 + JB + "S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 3; cam.pitch = 1.1;"),
    ('d-flat-3-flat-j-in3', "S.flat = true; " + JB + "C.inMode = 3;"),
    ('d-flat-5-m-in1', "S.flat = true; C.inMode = 1;"),
    ('d-flat-5-jr-in1', "S.flat = true; " + JR + "C.inMode = 1;"),
    ('d-flat-4-h003-i300', SEA % (300, '0.03')),
    ('d-flat-4-h0003-i300', SEA % (300, '0.003')),
    ('d-flat-4-h0003-i1500', SEA % (1500, '0.003')),
    ('d-flat-4-h00005-i300', SEA % (300, '0.0005')),
    ('d-flat-4-h00005-i3000', SEA % (3000, '0.0005')),
    ('d-words-4-rough', B4 + SIDE + "S.q.de = 0;"),
    ('d-words-4-exact', B4 + SIDE + "S.q.de = 3;"),
    ('d-words-4-rough-26', B4 + SIDE + "cam.dist = 2.6; S.q.de = 0;"),
    ('d-words-4-exact-26', B4 + SIDE + "cam.dist = 2.6; S.q.de = 3;"),
    ('d-words-5-ultra-i40', "q('qUltra'); " + JB + "S.iter = 40; cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0];"),
    ('d-words-5-ultra-i14', "q('qUltra'); " + JB + "cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0];"),
    ('d-words-5-bal-i40', B4 + JB + "S.iter = 40; cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0];"),
]
EXTRA = [
    ('x-k1-e03-three-on', B4 + "mode('k'); kp(4); S.k.three = true; C.solid = 1;"),
    ('x-k1-e00-three-off', B4 + "mode('k'); kp(1); S.k.three = false; C.solid = 1;"),
    ('x-k1-e00-tx06', B4 + "mode('k'); kp(1); C.solid = 1; C.tx = 0.6;"),
    ('x-k1-e00-ty05', B4 + "mode('k'); kp(1); C.solid = 1; C.ty = 0.5;"),
    ('x-solids-3-m-point-thick03', B4 + "C.trap = 0; C.solid = 1; C.thick = 0.3;"),
    ('x-solids-3-j3-point-thick03', B4 + J3 + "C.trap = 0; C.solid = 1; C.thick = 0.3;"),
    ('x-solids-3-m-ray-thick02', B4 + "C.trap = 3; C.solid = 1; C.thick = 0.2;"),
    ('x-solids-4-j-point-tx05', B4 + JB + "C.trap = 0; C.solid = 1; C.tx = 0.5; C.thick = 0.2;"),
    ('x-flat-4-h003-i2000', "S.extreme = true; " + SEA % (2000, '0.03')),
    ('x-flat-4-h0003-i2000', "S.extreme = true; " + SEA % (2000, '0.003')),
    ('x-words-5-steps300', "q('qUltra'); " + JB + "S.iter = 40; S.q.steps = 300; cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0];"),
]
ALL = FIXED + DEFECT + EXTRA


def shoot(page, label, only=(), extra=None, size=None):
    folder = os.path.join(HERE, label)
    os.makedirs(folder, exist_ok=True)
    todo = [(n, j) for n, j in (extra or ALL) if not only or any(n.startswith(o) or (o[:1] == '~' and o[1:] in n) for o in only)]
    rc = 0
    # the fixed list at 1000 x 700 (as round 6 drew it), the testers' reproductions at their size, 1400 x 950
    for group, sz in ((('f', 'g'), '1000x700'), (('d', 'x'), '1400x950')):
        part = [(n, j) for n, j in todo if n[0] in group]
        if not part: continue
        acts = [{'wait': 'done', 'timeout': 600}]
        for name, js in part:
            acts.append({'js': PRE + RESET + js + "go(); return '" + name + " three=' + S.k.three + ' kmx=' + S.k.mx + ' skip=' + C.skip + ' iter=' + S.iter;"})
            acts.append({'sleep': 0.15})
            acts.append({'wait': 'done', 'timeout': 900, 'shot': 'out/r7/engine/%s/%s.png' % (label, name), 'clip': '#view'})
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


def cmp(a, b, only=('f', 'g')):
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
    cols = min(len(names), 5); rows = (len(names) + cols - 1) // cols
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
    elif cmd == 'cmp': cmp(sys.argv[2], sys.argv[3], tuple(sys.argv[4:]) or ('f', 'g'))
    elif cmd == 'pairs': pairs(sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), tuple(sys.argv[6:]))
