"""Test driver for the shaders engineer, round 4. Builds step lists for tools/shot.py, runs them, makes sheets.
  python out/r4/shaders/lab.py rings <page> <label> [scenes] [variants] [traps]   -> out/r4/shaders/<label>/*.png + sheet
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = 'out/r4/shaders'
PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
L.R.warmOn = false;
const scene = name => {
  if (name === 'rabbit'){ $('mode-j').click(); const i = L.JULIA_PRESETS.findIndex(p => /rabbit/i.test(p.name)); L.applyJuliaPreset(L.JULIA_PRESETS[i]); L.resetCam(); L.cam.dist = 2.07; }
  else if (name === 'basilica'){ $('mode-j').click(); L.S.c = [-1, 0, 0]; L.resetCam(); L.cam.dist *= 0.6; }
  else if (name === 'mandel'){ $('mode-m').click(); L.resetCam(); L.cam.dist *= 0.6; }
  else if (name === 'rabbitfar'){ $('mode-j').click(); const i = L.JULIA_PRESETS.findIndex(p => /rabbit/i.test(p.name)); L.applyJuliaPreset(L.JULIA_PRESETS[i]); L.resetCam(); }
  else if (name === 'basilicafar'){ $('mode-j').click(); L.S.c = [-1, 0, 0]; L.resetCam(); }
  else if (name === 'mandelfar'){ $('mode-m').click(); L.resetCam(); }
};
const go = () => { L.syncControls(); L.refresh(false); L.touch(); L.viewChanged(); };
"""
TRAPS = {
  'shell': "Object.assign(L.S.colour, {mode: 0, trap: 5, by: 4});",
  'cross': "Object.assign(L.S.colour, {mode: 0, trap: 1, by: 4});",
  'planes': "Object.assign(L.S.colour, {mode: 0, trap: 4, by: 0});",
  'point': "Object.assign(L.S.colour, {mode: 0, trap: 0, by: 0});",
  'shellstep': "Object.assign(L.S.colour, {mode: 0, trap: 5, by: 1});",
  'shellside': "Object.assign(L.S.colour, {mode: 0, trap: 5, by: 3});",
  'tones': "Object.assign(L.S.colour, {mode: 0, trap: 7});",
  'ring': "Object.assign(L.S.colour, {mode: 0, trap: 6, by: 4});",
  'line': "Object.assign(L.S.colour, {mode: 0, trap: 2, by: 4});",
}
# name: (quality button, extra js)
VARS = {
  'b-i24': ('qBal', "L.S.iter = 24;"),
  'b-i12': ('qBal', "L.S.iter = 12;"),
  'b-i60': ('qBal', "L.S.iter = 60;"),
  'b-d02': ('qBal', "L.S.iter = 24; L.S.q.detail = 0.2;"),
  'b-d3':  ('qBal', "L.S.iter = 24; L.S.q.detail = 3;"),
  'f-i24': ('qFine', "L.S.iter = 24;"),
  'f-i60': ('qFine', "L.S.iter = 60;"),
  'f-i12': ('qFine', "L.S.iter = 12;"),
  'f-d02': ('qFine', "L.S.iter = 24; L.S.q.detail = 0.2;"),
  'f-d3':  ('qFine', "L.S.iter = 24; L.S.q.detail = 3;"),
  'b-def': ('qBal', ""),
  'f-def': ('qFine', ""),
}

def shot(url, steps, name, size='1100x760', timeout=1800):
    path = os.path.join(ROOT, HERE, 'steps-%s.json' % name)
    json.dump(steps, open(path, 'w', encoding='utf-8'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/shot.py'), '--url', url, '--size', size, '--actions', path],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    out = (r.stdout or '') + (r.stderr or '')
    open(os.path.join(ROOT, HERE, 'log-%s.txt' % name), 'w', encoding='utf-8').write(out)
    return r.returncode, out

def sheet(paths, labels, out, cols, scale=0.5):
    ims = [Image.open(os.path.join(ROOT, p)).convert('RGB') for p in paths]
    w, h = ims[0].size
    w2, h2 = int(w * scale), int(h * scale)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w2, rows * (h2 + 16)), (20, 20, 24))
    dr = ImageDraw.Draw(S)
    for i, im in enumerate(ims):
        x, y = (i % cols) * w2, (i // cols) * (h2 + 16)
        S.paste(im.resize((w2, h2), Image.LANCZOS), (x, y + 16))
        dr.text((x + 4, y + 2), labels[i], fill=(235, 235, 235))
    S.save(os.path.join(ROOT, out))
    return out

def rings(page, label, scenes, variants, traps, fast=True, size='1100x760'):
    d = '%s/%s' % (HERE, label)
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    steps, paths, labels = [], [], []
    for sc in scenes:
        for tr in traps:
            for v in variants:
                q, extra = VARS[v]
                js = PRE + "scene('%s'); $('%s').click(); %s %s %s go(); return '%s %s %s';" % (
                    sc, q, TRAPS[tr], extra, "L.S.q.aa = 4; L.S.q.shadow = false; L.S.q.ao = false;" if fast else "", sc, tr, v)
                p = '%s/%s-%s-%s.png' % (d, sc, tr, v)
                steps.append({'js': js, 'wait': 'done', 'timeout': 400, 'shot': p, 'clip': '#view'})
                paths.append(p); labels.append('%s %s %s %s' % (label, sc, tr, v))
    code, out = shot('dist/%s.html' % page, steps, label, size=size)
    print('exit', code)
    tail = out.strip().splitlines()[-6:]
    print('\n'.join(tail))
    return paths, labels

SOLID_TRAPS = {
  'shell': "trap: 5, radius: 0.7", 'cross': "trap: 1", 'line': "trap: 2, axis: 0", 'ring': "trap: 6, radius: 0.7", 'point': "trap: 0",
  'planes': "trap: 4", 'ray': "trap: 3, ray: 0",
}
def solids(page, label, scenes, traps, q='qBal', solid=1, colour="mode: 7", extra='', thick=0.05, skip=1, size='1100x760'):
    d = '%s/%s' % (HERE, label)
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    steps, paths, labels = [], [], []
    for sc in scenes:
        for tr in traps:
            js = PRE + "scene('%s'); $('%s').click(); Object.assign(L.S.colour, {%s, %s, solid: %d, thick: %g, skip: %d, tx: 0, ty: 0, tz: 0}); %s go(); return '%s %s';" % (
                sc, q, colour, SOLID_TRAPS[tr], solid, thick, skip, extra, sc, tr)
            p = '%s/%s-%s.png' % (d, sc, tr)
            steps.append({'js': js, 'wait': 'done', 'timeout': 600, 'shot': p, 'clip': '#view'})
            paths.append(p); labels.append('%s %s %s' % (label, sc, tr))
    code, out = shot('dist/%s.html' % page, steps, label, size=size)
    print('exit', code)
    print(chr(10).join(out.strip().splitlines()[-4:]))
    for l in out.splitlines():
        if 'waited' in l: print(l)
    return paths, labels

if __name__ == '__main__':
    if sys.argv[1] == 'solids':
        page, label = sys.argv[2], sys.argv[3]
        scenes = sys.argv[4].split(',')
        traps = sys.argv[5].split(',')
        kw = dict(a.split('=', 1) for a in sys.argv[6:])
        if 'solid' in kw: kw['solid'] = int(kw['solid'])
        if 'thick' in kw: kw['thick'] = float(kw['thick'])
        if 'skip' in kw: kw['skip'] = int(kw['skip'])
        paths, labels = solids(page, label, scenes, traps, **kw)
        print(sheet(paths, labels, '%s/sheet-%s.png' % (HERE, label), cols=len(traps)))
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == 'rings':
        page, label = sys.argv[2], sys.argv[3]
        scenes = sys.argv[4].split(',') if len(sys.argv) > 4 else ['rabbit']
        variants = sys.argv[5].split(',') if len(sys.argv) > 5 else ['b-i24', 'b-i12', 'b-i60', 'b-d02', 'b-d3']
        traps = sys.argv[6].split(',') if len(sys.argv) > 6 else ['shell']
        fast = not (len(sys.argv) > 7 and sys.argv[7] == 'full')
        paths, labels = rings(page, label, scenes, variants, traps, fast)
        print(sheet(paths, labels, '%s/sheet-%s.png' % (HERE, label), cols=len(variants)))
