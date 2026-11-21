"""Round 20, entry: checks and pictures of dist/r20-entry.html. Run from the project root, ONE at a time (one GPU).

  python out/r20/entry/run.py checks             MATH.windsq against Python, half-planes, jump test, shader against MATH -> checks.txt
  python out/r20/entry/run.py js <file.js> <log> run one script in the page, write what it returns
  python out/r20/entry/run.py steps <steps.json> <log> [size]   run a list of steps
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r20-entry.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
REL = 'out/r20/entry/'


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
    sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'me'))
    import rule
    import myrules
    steps = [UP, {'js': open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read(), 'timeout': 1800}]
    code, text, vals = shot(PAGE, steps, 'checks-steps')
    rep = [text]
    if not vals or not vals[-1].startswith('{'):
        write('checks.txt', text); print(text); return code or 1
    o = json.loads(vals[-1])
    write('checks-raw.json', vals[-1])
    rep.append('entry: ' + json.dumps(o['entry']))
    rep.append('')
    P = np.array(o['math']['P'], float); Q = np.array(o['math']['Q'], float)
    for tag, pts, key in (('6,000 points anywhere in a ball', P, 'F'), ('7,000 points crowded beside the planes at 0, 30, 60, 90, 120 degrees and the x- and z-axes', Q, 'G')):
        for n in (2, 3, 4, 5):
            G = np.array(o['math'][key][str(n)], float)
            R = np.linalg.norm(pts, axis=1) ** n
            refs = [('out/r20/entry/rule.py wn(%d)' % n, rule.wn(n))]
            if n == 2:
                refs.append(("the bench rule m_w3 (out/r19/me/myrules.py)", myrules.RULES['m_w3'][0]))
            for nm, F in refs:
                W = np.stack(F(pts[:, 0], pts[:, 1], pts[:, 2]), axis=1)
                e = np.linalg.norm(G - W, axis=1) / R
                rep.append('MATH.windsq at power %d against %s, %s: largest difference (share of the length) %.3e, 99.9 %% %.3e, median %.3e, over 1e-12: %d' % (
                    n, nm, tag, e.max(), np.quantile(e, .999), np.median(e), int((e > 1e-12).sum())))
    rep.append('')
    rep.append('half-planes through the x-axis (500 points each): is the point sent INTO the plane z = 0, onto the complex power of x + i rho (+) or of x - i rho (-)? to 1e-9 of the length')
    for k, rows in o['half'].items():
        good = ['%g%s' % (a, '+' if wp < 1e-9 else '-') for a, wp, wm in rows if min(wp, wm) < 1e-9]
        rep.append('  %-10s %d half-planes: %s' % (k, len(good), ', '.join(good)))
        rep.append('  %-10s all (angle: smaller of the two distances): %s' % ('', '  '.join('%g: %.1e' % (a, min(wp, wm)) for a, wp, wm in rows)))
    rep.append('')
    rep.append('plane z = 0 in MATH (z out exactly 0; x and y against Sphere inversions, one plane):')
    for k, v in o['flat'].items():
        rep.append('  %-8s %s' % (k, json.dumps(v)))
    rep.append('powers whose count is 1: ' + json.dumps(o['kOne']))
    rep.append('')
    rep.append('jump test (200,000 pairs per step size, a quarter anywhere, the rest beside the planes and axes): largest gap between the answers, and gap / step')
    for k, v in o['jump'].items():
        rep.append('  %-6s %s' % (k, '   '.join('%s: %.2e (x %.1f)' % (s, d['largest'], d['ratio']) for s, d in v.items())))
        rep.append('  %-6s at %s' % ('', '   '.join(json.dumps([round(x, 4) for x in d['at']]) for d in v.values())))
    rep.append('')
    rep.append('symmetries (4,000 points, largest difference as a share of the length):')
    for k, v in o['sym'].items():
        rep.append('  %-10s %s' % (k, json.dumps(v)))
    rep.append('')
    rep.append('Learn tab plan: ' + str(o.get('learn')))
    rep.append('GPU: ' + str(o.get('gpu')))
    for k, v in (o.get('glsl') or {}).items():
        rep.append('shader, %s: %s' % (k, json.dumps(v)))
    out = '\n'.join(rep) + '\n'
    write('checks.txt', out)
    print(out)
    return code


def js(path, log):
    steps = [UP, {'js': open(path, encoding='utf-8').read(), 'timeout': 1800}]
    code, text, vals = shot(PAGE, steps, os.path.basename(log) + '-steps')
    write(os.path.basename(log), text + ('\n' + vals[-1] + '\n' if vals and len(vals[-1]) >= 4000 else ''))
    print(text)
    return code


def run_steps(path, log, size=None, page=PAGE):
    steps = json.load(open(path, encoding='utf-8'))
    code, text, vals = shot(page, steps, os.path.basename(log) + '-run', size)
    write(os.path.basename(log), text)
    print(text[-6000:])
    return code


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'checks':
        sys.exit(checks())
    if a[0] == 'js':
        sys.exit(js(a[1], a[2]))
    if a[0] == 'steps':
        sys.exit(run_steps(a[1], a[2], a[3] if len(a) > 3 else None))
