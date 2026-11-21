"""Round 28, Track A, the eyes (section 1.4 c second half, d, g): drive a page of the lab with tools/shot.py.
Run from the project root, ONE browser script at a time.

Pages: dist/r28-eyes.html (my own build of base20a + the builder's overlay, command in out/r28/dials/BUILD.txt)
       dist/r28-base-eyes.html (my own build of the frozen base20a, Version 20).
In a script: L = window.squaringLab, S = L.S, $ = getElementById, sleep(ms), fail(text), go(), settle(), type(id, text).
(The helper follows out/r27/final/mk/run.py; folder and pages are mine, waits are longer.)
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EYES = os.path.dirname(HERE)                                   # out/r28/final/eyes
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(EYES))))
OUT = 'out/r28/final/eyes'
LOGS = os.path.join(EYES, 'logs')
PAGE = 'dist/r28-final.html'
BASE = 'dist/r28-base-final.html'
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const settle = async (most = 30000) => { await sleep(250); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the picture never finished'); if (L.R.failed) fail('a program failed: ' + L.R.failed); };
const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
const warn = () => (vis($('ballsWarn')) ? $('ballsWarn').textContent : '');
// a typed value, the way a hand does it: focus the box, put the text in, press Enter
const type = async (id, text) => { const n = $(id + 'Num'); if (!n) fail('no typed box ' + id); n.focus(); n.value = String(text); n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.blur(); await sleep(60); };
"""
UP = {'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 900}


def shot(page, steps, name, size=None, theme=None):
    os.makedirs(LOGS, exist_ok=True)
    sj = os.path.join(LOGS, name + '-steps.json')
    json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
    cmd = [sys.executable, '-W', 'ignore', os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj]
    if size:
        cmd += ['--size', size]
    if theme:
        cmd += ['--theme', theme]
    p = subprocess.run(cmd, capture_output=True, env=ENV, cwd=ROOT)
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    lines, vals = [], []
    for line in text.splitlines():
        m = re.match(r'(step \d+ result: )(".*")$', line)
        if m:
            try:
                v = json.loads(m.group(2)); vals.append(v)
                lines.append(m.group(1) + (v if len(v) < 3000 else v[:300] + ' ... (%d characters)' % len(v))); continue
            except ValueError:
                pass
        lines.append(line)
    return p.returncode, '\n'.join(lines) + '\n', vals


def write(name, text):
    os.makedirs(LOGS, exist_ok=True)
    with open(os.path.join(LOGS, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def clean(text):
    return 'no console errors' in text
