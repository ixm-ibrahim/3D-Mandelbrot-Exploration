"""Round 28, truth checker: run one script in a page of the lab through tools/shot.py. ONE browser at a time.

    code, text, vals = run(page, [js, js, ...], name, size='1400x950', theme='dark')
Each js runs after the page is up, with: L = window.squaringLab, S = L.S, $ = getElementById, sleep, fail, go, settle.
The step list goes to out/r28/final/truth/logs/<name>-steps.json, what shot.py printed to <name>.log (long values cut),
and the values the scripts returned come back as text in vals.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(TRUTH))))
LOGS = os.path.join(TRUTH, 'logs')
PAGE = 'dist/r28-final.html'
BASE = 'dist/r28-base-final.html'

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const settle = async (most = 60000) => { await sleep(250); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the picture never finished'); if (L.R.failed) fail('a program failed: ' + L.R.failed); };
"""
UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 900}


def run(page, scripts, name, size='1400x950', theme='dark', keep_steps=False):
    os.makedirs(LOGS, exist_ok=True)
    steps = [UP] + [{'js': HEAD + s, 'wait': 'done', 'timeout': 1800} for s in scripts]
    sj = os.path.join(LOGS, name + '-steps.json')
    with open(sj, 'w', encoding='utf-8') as f:
        json.dump(steps, f)
    cmd = [sys.executable, '-W', 'ignore', os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', size, '--theme', theme]
    p = subprocess.run(cmd, capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'), cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines, vals = [], []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(".*")$', line)
        if m:
            try:
                v = json.loads(m.group(2)); vals.append(v)
                lines.append(m.group(1) + (v if len(v) < 2000 else v[:300] + ' ... (%d characters)' % len(v))); continue
            except ValueError:
                pass
        lines.append(line)
    short = '\n'.join(lines) + '\nexit %d\n' % p.returncode
    with open(os.path.join(LOGS, name + '.log'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(short)
    if not keep_steps:                       # the step lists hold the points (megabytes); the script that made them is kept instead
        try:
            os.remove(sj)
        except OSError:
            pass
    return p.returncode, short, vals


def clean(text):
    return 'no console errors' in text
