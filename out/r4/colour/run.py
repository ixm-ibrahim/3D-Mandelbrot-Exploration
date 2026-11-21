"""Test driver for the colour module, round 4.

  python out/r4/colour/run.py id                 the same scenes on base4 and on base4 + the colour file: must be pixel-identical
  python out/r4/colour/run.py sheet NAME PAGE    render the plan NAME (see PLANS) on dist/PAGE.html into one contact sheet

Pictures go to out/r4/colour/<plan>/, sheets to out/r4/colour/sheet-<plan>.png.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRE = ("const L = window.squaringLab, S = L.S, C = S.colour, $ = id => document.getElementById(id);"
       "const go = () => { L.syncControls(); L.refresh(false); };"
       "const mode = m => { S.mode = m; $('mode-' + m).checked = true; };"
       "const q = id => $(id).click();")
RESET = "L.resetAll();"

# name -> [(label, javascript)]; every scene starts from "Reset everything"
PLANS = {
    'id': [
        ('m-default', "q('qFast');"),
        ('j-basilica', "q('qFast'); mode('j'); S.c = [-1, 0, 0];"),
        ('j-rabbit-cross-bands', "q('qFast'); mode('j'); S.c = [-0.123, 0.745, 0]; C.trap = 1; C.by = 0; C.pal = 6;"),
        ('m-planes-step', "q('qFast'); C.trap = 4; C.by = 1;"),
        ('m-line-side', "q('qFast'); C.trap = 2; C.by = 3;"),
        ('m-ring-blend', "q('qFast'); C.trap = 6; C.by = 2;"),
        ('m-tones', "q('qFast'); C.trap = 7;"),
        ('m-escape', "q('qFast'); C.mode = 2;"),
        ('m-laststep', "q('qFast'); C.mode = 5;"),
        ('m-cut', "q('qFast'); S.cutOn = true; S.cut = 0;"),
        ('k-default', "q('qFast'); mode('k');"),
        ('m-balanced', ""),
        ('2d-m', "q('qFast'); S.flat = true;"),
        ('2d-m-old', "q('qFast'); S.flat = true; C.trap = 4; C.by = 0; C.pal = 7; C.rev = false;"),
        ('2d-j-ring-blend', "q('qFast'); S.flat = true; mode('j'); S.c = [-1, 0, 0]; C.trap = 6; C.by = 2;"),
        ('2d-j-tones-z', "q('qFast'); S.flat = true; mode('j'); S.c = [-0.123, 0.745, 0]; C.trap = 7; S.cut = 0.2;"),
        ('2d-m-clay', "q('qFast'); S.flat = true; C.mode = 7;"),
        ('2d-m-point-step', "q('qFast'); S.flat = true; C.trap = 0; C.by = 1; C.pal = 5;"),
        ('2d-k', "q('qFast'); S.flat = true; mode('k');"),
    ],
}


def actions(plan, folder, clip='#stage'):
    acts = [{'wait': 'done', 'timeout': 240}]
    for name, js in plan:
        acts.append({'js': PRE + RESET + js + 'go();'})
        acts.append({'sleep': 0.15})
        acts.append({'wait': 'done', 'timeout': 400, 'shot': os.path.join(folder, name + '.png').replace('\\', '/'), 'clip': clip})
    return acts


def shoot(page, plan, folder, size='1000x700', theme='dark'):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, '_actions.json')
    json.dump(actions(plan, folder), open(path, 'w'))
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--actions', path,
                        '--size', size, '--theme', theme], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout + r.stderr).strip().splitlines()
    print('  %s: exit %d' % (page, r.returncode), '|', ' / '.join(l for l in tail if 'rror' in l or 'xception' in l or 'timed out' in l)[:600])
    return r.returncode


def sheet(plan, folder, out, cols=4, w=420):
    tiles = []
    for name, _ in plan:
        p = os.path.join(folder, name + '.png')
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        ImageDraw.Draw(im).text((6, 4), name, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        tiles.append(im)
    if not tiles:
        return
    h = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    big = Image.new('RGB', (cols * w, rows * h), (20, 20, 20))
    for i, t in enumerate(tiles):
        big.paste(t, ((i % cols) * w, (i // cols) * h))
    big.save(out)
    print('  sheet', out)


def main():
    what = sys.argv[1]
    if what == 'id':
        plan = PLANS['id']
        a, b = os.path.join(HERE, 'id', 'base'), os.path.join(HERE, 'id', 'mine')
        mine = sys.argv[2] if len(sys.argv) > 2 else 'r4-colour-id'
        shoot('r4-colour-base', plan, a)
        shoot(mine, plan, b)
        worst = 0
        for name, _ in plan:
            x = np.asarray(Image.open(os.path.join(a, name + '.png')).convert('RGB')).astype(int)
            y = np.asarray(Image.open(os.path.join(b, name + '.png')).convert('RGB')).astype(int)
            if x.shape != y.shape:
                print('  %-24s sizes differ' % name); worst = 999; continue
            d = np.abs(x - y)
            worst = max(worst, int(d.max()))
            print('  %-24s largest channel difference %3d, pixels that differ %d of %d' % (name, d.max(), int((d.max(axis=2) > 0).sum()), d.shape[0] * d.shape[1]))
        print('IDENTICAL' if worst == 0 else 'DIFFERENT (worst %d)' % worst)
        sheet(plan, b, os.path.join(HERE, 'sheet-id.png'))
    elif what == 'sheet':
        name, page = sys.argv[2], sys.argv[3]
        plans = json.load(open(os.path.join(HERE, 'plans.json'), encoding='utf-8'))
        plan = [tuple(x) for x in plans[name]]
        folder = os.path.join(HERE, name)
        theme = sys.argv[4] if len(sys.argv) > 4 else 'dark'
        shoot(page, plan, folder, theme=theme)
        sheet(plan, folder, os.path.join(HERE, 'sheet-%s.png' % name), cols=int(plans.get('_cols', {}).get(name, 4)))


if __name__ == '__main__':
    main()
