"""Round 27, checker A: drive a page with tools/shot.py and get back what the page scripts return.

  from drive import run
  code, vals, text = run(page, steps, tag, size='1400x950', theme='dark')
steps: a list of shot.py actions. vals: the returned values of the steps that returned one, in order (parsed JSON
when the value was a JSON string). The log goes to out/r27/checka/logs/<tag>.log, the steps to <tag>-steps.json.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); CHK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CHK)))
LOGS = os.path.join(CHK, 'logs')
PAGE = 'dist/r27-checka.html'
BASE = 'dist/r27-base.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const settle = async (most = 6000) => { await sleep(250); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the picture never finished'); if (L.R.failed) fail('a program failed: ' + L.R.failed); };
"""
UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 600}


def run(page, steps, tag, size='1400x950', theme='dark', quiet=True):
    os.makedirs(LOGS, exist_ok=True)
    sj = os.path.join(LOGS, tag + '-steps.json')
    with open(sj, 'w', encoding='utf-8') as f:
        json.dump(steps, f, indent=1)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', size, '--theme', theme]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, env=ENV, cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines, vals = [], []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(.*)$', line)
        if m:
            try:
                v = json.loads(m.group(2))
                if isinstance(v, str):
                    try:
                        v = json.loads(v)
                    except ValueError:
                        pass
                vals.append(v)
                s = m.group(2)
                lines.append(m.group(1) + (s if len(s) < 2000 else s[:300] + ' ... (%d characters)' % len(s))); continue
            except ValueError:
                pass
        lines.append(line)
    with open(os.path.join(LOGS, tag + '.log'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\nexit %d, %.0f s\n' % (p.returncode, time.time() - t0))
    if not quiet:
        print('\n'.join(lines[-30:])); print('exit', p.returncode)
    return p.returncode, vals, '\n'.join(lines)
