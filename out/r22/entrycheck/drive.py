"""Round 22, entrycheck: drive a page of the lab with tools/shot.py (one run at a time). Everything is written into
out/r22/entrycheck/.
  python out/r22/entrycheck/drive.py js <file.js> <log-name> [page] [size]
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r22-entry.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const apId = () => L.APPROACHES[S.approach].id;
const settle = async (most = 9000) => { await sleep(250); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the picture never finished'); if (L.R.failed) fail('a program failed: ' + L.R.failed); };
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0, s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const hit = !!L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += hit ? '1' : '0'; if (hit) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } } return [n, ring, s]; };
"""
UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries: ' + L.APPROACHES.map(a => a.id).join(' ');", 'wait': 'done', 'timeout': 600}


def shot(page, steps, name, size=None):
    sj = os.path.join(HERE, name + '.json')
    json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj]
    if size:
        cmd += ['--size', size]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, env=ENV, cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines, vals = [], []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(.*)$', line)
        if m:
            try:
                v = json.loads(m.group(2)); vals.append(v)
                s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
                lines.append(m.group(1) + (s if len(s) < 3000 else s[:300] + ' ... (%d characters)' % len(s))); continue
            except ValueError:
                pass
        lines.append(line)
    lines.append('wall time %.0f s' % (time.time() - t0))
    return p.returncode, '\n'.join(lines) + '\n', vals


def write(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def js(path, log, page=PAGE, size=None):
    steps = [UP, {'js': HEAD + open(path, encoding='utf-8').read(), 'timeout': 1800}]
    code, text, vals = shot(page, steps, os.path.basename(log) + '-steps', size)
    write(log, text + 'exit %d\n' % code)
    if vals:
        v = vals[-1]
        write(log + '.json', v if isinstance(v, str) else json.dumps(v))
    print(text[-5000:]); print('exit', code)
    return code


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'js':
        sys.exit(js(a[1], a[2], a[3] if len(a) > 3 else PAGE, a[4] if len(a) > 4 else None))
