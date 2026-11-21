"""Round 16, entry: checks and pictures of dist/r16-entry.html. Run from the project root, one at a time.

  python out/r16/entry/run.py checks             MATH.turnaway / turnalong against out/me/r16/scout3.py, planes, jump test, shader against MATH -> checks.txt
  python out/r16/entry/run.py pictures <set>     pictures of one set -> <name>.png (sets: see sets.py)
  python out/r16/entry/run.py js <file.js> <log> run one script in the page, write what it returns
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r16-entry.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
REL = 'out/r16/entry/'


def shot(page, steps, name, size=None):
    sj = os.path.join(HERE, name + '.json')
    json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj]
    if size:
        cmd += ['--size', size]
    p = subprocess.run(cmd, capture_output=True, env=ENV, cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines, vals = [], []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(".*")$', line)
        if m:
            try:
                v = json.loads(m.group(2)); vals.append(v)
                lines.append(m.group(1) + (v if len(v) < 4000 else v[:300] + ' ... (%d characters)' % len(v))); continue
            except ValueError:
                pass
        lines.append(line)
    return p.returncode, '\n'.join(lines) + '\n', vals


def write(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries: ' + L.APPROACHES.map(a => a.id).join(' ');", 'wait': 'done', 'timeout': 600}


def checks():
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
    import scout3
    steps = [UP, {'js': open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read(), 'timeout': 1800}]
    code, text, vals = shot(PAGE, steps, 'checks-steps')
    rep = [text]
    o = json.loads(vals[-1])
    write('checks-raw.json', vals[-1])
    for id_, q in (('turnaway', -1), ('turnalong', 1)):
        F = scout3.turning(q)
        for tag, a, b in (('20,000 points anywhere in a ball', 'P', 'F'), ('6,000 points crowded beside the planes z = 0, y = 0, y = z, y = -z and the x- and z-axes', 'Q', 'G')):
            P = np.array(o['math'][a], float); G = np.array(o['math'][id_][b], float)
            W = np.stack(F(P[:, 0], P[:, 1], P[:, 2]), axis=1)
            e = np.linalg.norm(G - W, axis=1)
            rep.append('MATH.%s at power 2 against scout3.turning(%d), %s: largest difference %.3e, 99.9 %% %.3e, median %.3e, over 1e-12: %d' % (
                id_, q, tag, e.max(), np.quantile(e, .999), np.median(e), int((e > 1e-12).sum())))
    rep.append('')
    rep.append('planes through the x-axis: largest distance from the complex power, as a share of the length (500 points per plane); angle of the plane in degrees')
    for k, rows in o['planes'].items():
        good = [a for a, w in rows if w < 1e-9]
        rep.append('  %-18s follows the complex power (to 1e-9) at: %s' % (k, ', '.join('%g' % a for a in good)))
        rep.append('  %-18s all: %s' % ('', '  '.join('%g: %.1e' % (a, w) for a, w in rows)))
    rep.append('')
    rep.append('plane z = 0 in MATH (z out exactly 0, x and y against Sphere inversions, one plane):')
    for k, v in o['flat'].items():
        rep.append('  %-20s %s' % (k, json.dumps(v)))
    rep.append('')
    rep.append('jump test (200,000 pairs per step size, a quarter anywhere, the rest beside the planes and axes): largest gap between the answers')
    for k, v in o['jump'].items():
        rep.append('  %-18s %s' % (k, '   '.join('%s: %.2e' % (s, d['largest']) for s, d in v.items())))
        rep.append('  %-18s at %s' % ('', '   '.join(json.dumps([round(x, 4) for x in d['at']]) for d in v.values())))
    rep.append('')
    rep.append('symmetries (4,000 points, largest difference as a share of the length):')
    for k, v in o['sym'].items():
        rep.append('  %-18s %s' % (k, json.dumps(v)))
    rep.append('')
    rep.append('GPU: ' + str(o.get('gpu')))
    for k, v in (o.get('glsl') or {}).items():
        rep.append('shader, %s: %s' % (k, json.dumps(v)))
    out = '\n'.join(rep) + '\n'
    write('checks.txt', out)
    print(out)
    return code


HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const pick = id => { $('ap-' + id).click(); };
"""
RABBIT = '[-0.12, 0.74, 0]'
TAIL = " return '%s: approach ' + L.APPROACHES[S.approach].id + ', mode ' + S.mode + ', n ' + S.n + ', iter ' + S.iter + ', flat ' + S.flat + ', c ' + JSON.stringify(S.c) + ', cam ' + [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => +x.toFixed(4)).join(' ') + ', failed ' + L.R.failed;"


def view3(mode, c=None, extra='', cam=''):
    js = "$('mode-%s').click(); await sleep(150); S.flat = false; S.cutOn = false; " % mode
    if c:
        js += "S.c = %s; " % c
    return js + extra + " L.resetCam(); " + cam + " go(); await sleep(200);"


def view2(mode, c=None, x=0.0, h=3.2, extra=''):
    js = "$('mode-%s').click(); await sleep(150); S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = %s; S.v2.y = 0; S.v2.h = %s; " % (mode, x, h)
    if c:
        js += "S.c = %s; " % c
    return js + extra + " go(); await sleep(200);"


def run_set(name, items, size=None):
    steps = [UP]
    for n, js in items:
        steps.append({'js': HEAD + js + TAIL % n, 'timeout': 900, 'wait': 'done', 'shot': REL + n + '.png', 'clip': '#stage canvas'})
    steps.append({'js': "const L = window.squaringLab; return 'end: failed ' + L.R.failed + ', status ' + document.getElementById('status').textContent;"})
    code, text, _ = shot(PAGE, steps, 'pictures-' + name + '-steps', size)
    write('pictures-' + name + '.log', text)
    print(text)
    return code


def js(path, log):
    steps = [UP, {'js': open(path, encoding='utf-8').read(), 'timeout': 1800}]
    code, text, vals = shot(PAGE, steps, os.path.basename(log) + '-steps')
    write(os.path.basename(log), text + ('\n' + vals[-1] + '\n' if vals and len(vals[-1]) >= 4000 else ''))
    print(text)
    return code


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'checks':
        sys.exit(checks())
    if a[0] == 'js':
        sys.exit(js(a[1], a[2]))
    if a[0] == 'pictures':
        sys.path.insert(0, HERE)
        import sets
        sys.exit(run_set(a[1], sets.SETS[a[1]](), sets.SIZE.get(a[1])))
