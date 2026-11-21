"""Round 22, entrycheck, second pass: drive a page of the lab with tools/shot.py (ONE run at a time).
Everything is written into out/r22/entrycheck2/.
  python out/r22/entrycheck2/drv.py js <file.js> <log-name> [page] [size]
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = 'dist/r22-entry.html'
BASE = 'dist/r22-entrycheck2-base.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const apId = () => L.APPROACHES[S.approach].id;
const setAp = id => { const i = L.APPROACHES.findIndex(a => a.id === id); if (i < 0) fail('no entry ' + id); S.approach = i; };
const settle = async (most = 9000) => { await sleep(250); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the picture never finished'); if (L.R.failed) fail('a program failed: ' + L.R.failed); };
const grid = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0, ring = 0, s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const hit = !!L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += hit ? '1' : '0'; if (hit) { n++; if (i === 0 || j === 0 || i === 14 || j === 10) ring++; } } return [n, ring, s]; };
const txt = id => { const e = $(id); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; };
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


def js(path, log, page=PAGE, size=None, split='//@@STEP'):
    """The file holds a common part, then steps, each begun by a line //@@STEP; each step gets HEAD and the common
    part in front. A step whose first line is ' shot: <path>' also writes a picture of the stage after it."""
    src = open(path, encoding='utf-8').read()
    parts = src.split(split); common = parts[0]
    steps = [UP]
    for part in parts[1:]:
        first = part.split('\n', 1)[0].strip()
        st = {'js': HEAD + common + part.split('\n', 1)[1], 'timeout': 110}
        if first.startswith('shot:'):
            st['shot'] = first[5:].strip(); st['clip'] = '#stage'; st['wait'] = 'done'
        steps.append(st)
    code, text, vals = shot(page, steps, os.path.basename(log) + '-steps', size)
    write(log, text + 'exit %d\n' % code)
    write(log + '.json', json.dumps(vals[1:], ensure_ascii=False, indent=1))
    print(text[-6000:]); print('exit', code)
    return code


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'js':
        sys.exit(js(a[1], a[2], a[3] if len(a) > 3 else PAGE, a[4] if len(a) > 4 else None))
