"""Round 27, entry: the old smoke lists on a page of this round, exactly as round 22 ran them on Version 18:
tools/smoke-v14.json (62 steps) + round 20's 5 steps (with round 22's one changed line) + round 22's 20 + 3 steps.
The steps are taken from out/r22/entry/smoke.py unchanged; only the page and the folder for the pictures differ.
  python out/r27/entry/mk/smoke27.py [page] [tag] [tail]    (tail: only steps 76 to 90, on a fresh page) -> out/r27/entry/logs/<tag>.log, pictures in out/r27/entry/smoke/
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ENTRY = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(ENTRY)))
R22 = os.path.join(ROOT, 'out', 'r22', 'entry')
sys.path.insert(0, R22)
import smoke as S22          # round 22's list (it brings round 20's along)
import second                # round 22's second pass

page = sys.argv[1] if len(sys.argv) > 1 else 'dist/r27-entry.html'
tag = sys.argv[2] if len(sys.argv) > 2 else 'smoke-all'
base = json.load(open(os.path.join(ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
old = base + [dict(s) for s in S22.S20.NEW]
n_changed = 0
for s in old:
    if S22.OLD_LINE in s.get('js', ''):
        s['js'] = s['js'].replace(S22.OLD_LINE, S22.NEW_LINE); n_changed += 1
assert n_changed == 1, n_changed
steps = old + S22.steps_for('alongonce') + S22.steps_for('pulledplane') + second.STEPS + S22.LAST
if len(sys.argv) > 3 and sys.argv[3] == 'tail':   # the last 15 steps alone (steps 76 to 90), after the page is up
    steps = [S22.run.UP] + S22.steps_for('pulledplane') + second.STEPS + S22.LAST
steps = [dict(s) for s in steps]
os.makedirs(os.path.join(ENTRY, 'smoke'), exist_ok=True); os.makedirs(os.path.join(ENTRY, 'logs'), exist_ok=True)
for s in steps:
    if 'shot' in s:
        s['shot'] = 'out/r27/entry/smoke/' + os.path.basename(s['shot'])
sj = os.path.join(ENTRY, 'logs', tag + '-steps.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', '1400x950'],
                   capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'), cwd=ROOT)
text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
lines = []
for line in text.splitlines():
    m = re.match(r'(step \d+ result: )(".*")$', line)
    if m:
        try:
            v = json.loads(m.group(2)); line = m.group(1) + (v if len(v) < 1500 else v[:300] + ' ... (%d characters)' % len(v))
        except ValueError:
            pass
    lines.append(line)
results = sum(1 for l in lines if re.match(r'step \d+ result: ', l))
tail = 'steps: %d; results: %d; exit %d\n' % (len(steps), results, p.returncode)
with open(os.path.join(ENTRY, 'logs', tag + '.log'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n' + tail)
print('\n'.join(lines[-12:])); print(tail)
sys.exit(p.returncode)
