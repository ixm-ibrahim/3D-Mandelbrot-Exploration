"""Fixed lists of scenes for round 11 (engineer "engine"), and comparisons of two sets of pictures of them.

  python out/r11/engine/scenes.py shoot <page> <label> [prefix ...]   draw the scenes whose names start with a prefix
                                                                      (all when none is given) on dist/<page>.html into
                                                                      out/r11/engine/<label>/
  python out/r11/engine/scenes.py cmp <labelA> <labelB> [prefix ...]  largest channel difference per scene
  python out/r11/engine/scenes.py pairs <labelA> <labelB> <out.png> <scale> <prefix> [...]   A above B, per scene

Every scene starts from "Reset everything" (the model is out/r9/klein/scenes.py). Lists:
  FIXED   f.. the 2D view and 3D pictures not coloured by a trap; g.. trap-coloured 3D pictures;
          s.. trap solids of the three modes. 1000 x 700, 4 passes.
  DEFECT  d.. the testers' scenes of this round's defects, 1400 x 950, the whole stage, as the testers drew them.
          x.. the same scenes with shadows or crevice shading off (to find what draws the lines).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, cam = L.cam, $ = id => document.getElementById(id);"
       "const sleep = ms => new Promise(r => setTimeout(r, ms));"
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
JS07 = JB + "C.trap = 5; C.solid = 1; C.radius = 0.7;"
FIXED = [
    ('f01-flat-m-open', "S.flat = true;"),
    ('f02-flat-j-minus1', "S.flat = true; " + JB),
    ('f05-flat-k', "S.flat = true; mode('k');"),
    ('f09-flat-j-in-trap', "S.flat = true; " + JB + "C.inMode = 1;"),
    ('f10-flat-m-cross-bands', "S.flat = true; C.trap = 1; C.by = 0;"),
    ('f11-m-escape', B4 + "C.mode = 2;"),
    ('f13-j-depth', B4 + JB + "C.mode = 4;"),
    ('f14-m-clay', B4 + "C.mode = 7;"),
    ('f15-jr-clay', B4 + JR + "C.mode = 7;"),
    ('f16-k-escape', B4 + "mode('k'); C.mode = 2;"),
    ('f17-k-clay', B4 + "mode('k'); C.mode = 7;"),
    ('f18-m-neg2-escape', B4 + "S.n = -2; C.mode = 2;"),
    ('f21-m-ultra-escape', "q('qUltra'); C.mode = 2;"),
    ('f22-m-fast-clay', "q('qFast'); C.mode = 7;"),
    ('f23-cut-m-hatch-escape', B4 + "S.cutOn = true; S.cut = 0; C.mode = 2;"),
    ('f25-m-mosaic-escape', B4 + "S.mosaic = true; C.mode = 2;"),
    ('f27-m-fine-clay', F4 + "C.mode = 7;"),
    ('g01-m-open', B4),
    ('g02-j-open', B4 + JB),
    ('g03-k-open', B4 + "mode('k');"),
    ('g04-j-fine', F4 + JB),
    ('g05-jr-open', B4 + JR),
    ('g06-m-neg2', B4 + "S.n = -2;"),
    ('g07-m-mosaic', B4 + "S.mosaic = true;"),
    ('g08-j-ultra', "q('qUltra'); " + JB),
    ('g11-k-e33-fine', F4 + "mode('k'); kp(34);"),
    ('g12-m-fine', F4),
    ('s01-ex0-m-coral', B4 + "ex(0);"),
    ('s02-ex1-m-discs', B4 + "ex(1);"),
    ('s03-ex2-m-rings', B4 + "ex(2);"),
    ('s04-ex3-j-bubbles', B4 + "ex(3);"),
    ('s05-ex4-j-urchins', B4 + "ex(4);"),
    ('s06-ex5-jr-arches', B4 + "ex(5);"),
    ('s07-m-shell-is', B4 + "C.solid = 1;"),
    ('s09-j-shell1-is', B4 + JB + "C.solid = 1;"),
    ('s10-jr-ring-added', B4 + JR + "C.trap = 6; C.solid = 2;"),
    ('s11-j-bubbles-fine', F4 + JS07),
    ('s12-j-bubbles-ultra', "q('qUltra'); " + JS07),
    ('s16-j-bubbles-cut', B4 + JS07 + "S.cutOn = true; S.cut = 0;"),
    ('s17-m-mosaic-shell', B4 + "S.mosaic = true; C.solid = 1;"),
    ('s20-k-e00-is', B4 + "mode('k'); kp(1); C.solid = 1;"),
    ('s21-k-ex6-pearls', B4 + "ex(6);"),
    ('s22-k-ex7-rings', B4 + "ex(7);"),
    ('s23-k-ex8-discs-fine', F4 + "ex(8);"),
]
RAB = "mode('j'); await sleep(200); L.applyJuliaPreset(L.JULIA_PRESETS.find(p => /rabbit/i.test(p.name))); L.syncControls(); await sleep(200); "
CLOSE = RAB + "cam.dist = cam.dist * 0.45; "
SIDE = RAB + "cam.yaw = -1.571; cam.pitch = 0.12; cam.target = [0, 0, 0]; "
BULB = "$('ap-bulb').click(); await sleep(200); C.trap = 5; C.radius = 0.7; "
KY = lambda y: "mode('k'); await sleep(200); C.solid = 1; C.ty = %s; " % y
DEFECT = [
    ('d01-solids4-rabbit-fine', CLOSE + "q('qFine');"),
    ('d02-solids4-rabbit-bal', CLOSE + "q('qBal');"),
    ('d03-words4-side26-exact', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3;"),
    ('d04-words4-side46-exact', SIDE + "cam.dist = 4.6; q('qBal'); S.q.de = 3;"),
    ('d05-words4-side26-rough', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 0;"),
    ('d06-solids3-bulb-bal', BULB + "q('qBal');"),
    ('d07-solids3-bulb-ultra', BULB + "q('qUltra');"),
    ('d08-solids3-bulb-fine', BULB + "q('qFine'); S.q.aa = 8;"),
    ('d09-flat1-k-in-trap', "$('flat').click(); await sleep(100); mode('k'); await sleep(200); C.inMode = 1;"),
    ('d10-klein1-ty05', KY(0.5) + "q('qBal'); S.q.aa = 4;"),
    ('d11-klein1-ty025', KY(0.25) + "q('qBal'); S.q.aa = 4;"),
    ('d12-klein1-ty1', KY(1) + "q('qBal'); S.q.aa = 4;"),
    ('d13-klein1-ty0', KY(0) + "q('qBal'); S.q.aa = 4;"),
    ('d14-klein1-ty05-far', KY(0.5) + "cam.dist = cam.dist * 8; q('qBal'); S.q.aa = 4;"),
    ('d15-klein1-ty1-far', KY(1) + "cam.dist = cam.dist * 8; q('qBal'); S.q.aa = 4;"),
    # the same scenes with one kind of shading off
    ('x01-rabbit-fine-noshadow', CLOSE + "q('qFine'); S.q.aa = 8; S.q.shadow = false;"),
    ('x02-rabbit-fine-noao', CLOSE + "q('qFine'); S.q.aa = 8; S.q.ao = false;"),
    ('x03-rabbit-fine-neither', CLOSE + "q('qFine'); S.q.aa = 8; S.q.ao = false; S.q.shadow = false;"),
    ('x04-rabbit-fine-both-aa8', CLOSE + "q('qFine'); S.q.aa = 8;"),
    ('x05-side26-noshadow', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3; S.q.shadow = false;"),
    ('x06-side26-noao', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3; S.q.ao = false;"),
    ('x07-side26-neither', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3; S.q.ao = false; S.q.shadow = false;"),
    ('x08-rabbit-fine-clay', CLOSE + "q('qFine'); S.q.aa = 8; C.mode = 7;"),
    ('x09-side26-clay', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3; C.mode = 7;"),
    ('x10-rabbit-fine-smooth', CLOSE + "q('qFine'); S.q.aa = 8; S.q.normals = 'smooth';"),
    ('x11-side26-smooth', SIDE + "cam.dist = 2.6; q('qBal'); S.q.de = 3; S.q.normals = 'smooth';"),
]
ALL = FIXED + DEFECT


def shoot(page, label, only=(), extra=None, size=None):
    folder = os.path.join(HERE, label)
    os.makedirs(folder, exist_ok=True)
    todo = [(n, j) for n, j in (extra or ALL) if not only or any(n.startswith(o) or (o[:1] == '~' and o[1:] in n) for o in only)]
    rc = 0
    for group, sz, clip in ((('f', 'g', 's'), '1000x700', '#view'), (('d', 'x'), '1400x950', '#stage')):
        part = [(n, j) for n, j in todo if n[0] in group]
        if not part: continue
        acts = [{'wait': 'done', 'timeout': 600}]
        for name, js in part:
            acts.append({'js': PRE + RESET + js + "go(); return '" + name + " mode=' + S.mode + ' c=' + S.c.join(',') + ' dist=' + cam.dist.toFixed(4) + ' q=' + JSON.stringify(S.q) + ' solid=' + C.solid + ' flat=' + S.flat;"})
            acts.append({'sleep': 0.15})
            acts.append({'wait': 'done', 'timeout': 900, 'shot': 'out/r11/engine/%s/%s.png' % (label, name), 'clip': clip})
        tag = (group[0] + '-' + '-'.join(only)[:40].replace('~', '')) if only else group[0] + '-all'
        path = os.path.join(folder, '_actions-%s.json' % tag)
        json.dump(acts, open(path, 'w', encoding='utf-8'))
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path,
                            '--size', size or sz], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=7200)
        out = (r.stdout or '') + (r.stderr or '')
        open(os.path.join(folder, '_log-%s.txt' % tag), 'w', encoding='utf-8').write(out)
        lines = out.strip().splitlines()
        print('%s -> %s (%d scenes, %s): exit %d | %s' % (page, label, len(part), size or sz, r.returncode, lines[-1][:200] if lines else ''))
        for l in lines:
            if 'TIMED OUT' in l or 'PROBLEMS' in l or 'console.' in l or 'EXCEPTION' in l or 'Error' in l:
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
        print('%-34s largest channel difference %3d   pixels that differ at all: %8.4f %%   over 8: %8.4f %%   mean %6.3f' % (name, mx, 100 * float((d > 0).mean()), 100 * float((d > 8).mean()), float(d.mean())))
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
