"""Round 15, entry: checks and pictures of dist/r15-entry.html. Run from the project root, one at a time.

  python out/r15/entry/run.py checks [power]     MATH.sqpillow against out/me/r15/pillow_ref.py, the shader against MATH -> checks.txt
  python out/r15/entry/run.py pictures <set>     pictures of one set -> <name>.png (sets: see SETS)
  python out/r15/entry/run.py js <file.js> <log> run one script in the page, write what it returns
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r15-entry.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
REL = 'out/r15/entry/'


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


def checks(power=2):
    import numpy as np
    sys.path.insert(0, HERE)
    import ref_n as RN
    steps = [UP, {'js': 'window.__spPow = %d;\n' % power + open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read(), 'timeout': 900}]
    code, text, vals = shot(PAGE, steps, 'checks-steps')
    rep = [text]
    o = json.loads(vals[-1])
    if power == 2:
        write('checks-raw.json', vals[-1])
    for tag, a, b in (('20,000 points anywhere in a ball', 'P', 'F'), ('6,000 points crowded beside the plane z = 0, the plane y = 0, the corner points and the poles', 'Q', 'G')):
        P = np.array(o['math'][a], float); F = np.array(o['math'][b], float)
        W = RN.F(P, power)
        e = np.linalg.norm(F - W, axis=1); r = e / np.linalg.norm(W, axis=1)
        rep.append('MATH.sqpillow at power %d against the reference, %s: largest difference %.3e (as a share of the length %.3e), 99.9 %% %.3e, median %.3e, over 1e-9: %d' % (
            power, tag, e.max(), r.max(), np.quantile(e, .999), np.median(e), int((e > 1e-9).sum())))
        if power == 2:
            sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r15'))
            import pillow_ref as R0
            W0 = R0.F(P); e0 = np.linalg.norm(F - W0, axis=1)
            rep.append('   the same against out/me/r15/pillow_ref.py itself: largest %.3e, 99.9 %% %.3e, median %.3e, over 1e-9: %d' % (e0.max(), np.quantile(e0, .999), np.median(e0), int((e0 > 1e-9).sum())))
            k = np.argsort(-e0)[:4]
            for i in k:
                rep.append('     worst: v = %s  page %s  reference %s  off %.2e' % (P[i].tolist(), F[i].tolist(), W0[i].tolist(), e0[i]))
    rep.append('plane z = 0 in MATH: ' + json.dumps(o['flat']))
    rep.append('GPU: ' + str(o.get('gpu')))
    for k, v in (o.get('glsl') or {}).items():
        rep.append('shader, %s: %s' % (k, json.dumps(v)))
    out = '\n'.join(rep) + '\n'
    write('checks.txt' if power == 2 else 'checks-n%d.txt' % power, out)
    print(out)
    return code


HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const pick = id => { $('ap-' + id).click(); };
"""
RABBIT = '[-0.12, 0.74, 0]'
TAIL = " return '%s: approach ' + L.APPROACHES[S.approach].id + ', mode ' + S.mode + ', n ' + S.n + ', flat ' + S.flat + ', c ' + JSON.stringify(S.c) + ', cam ' + [L.cam.yaw, L.cam.pitch, L.cam.dist, ...L.cam.target].map(x => +x.toFixed(4)).join(' ') + ', failed ' + L.R.failed;"


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
        sys.exit(checks(int(a[1]) if len(a) > 1 else 2))
    if a[0] == 'js':
        sys.exit(js(a[1], a[2]))
    if a[0] == 'pictures':
        import sets
        sys.exit(run_set(a[1], sets.SETS[a[1]](), sets.SIZE.get(a[1])))
