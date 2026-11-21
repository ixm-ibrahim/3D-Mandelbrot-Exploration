"""Round 27, checker A: the old smoke lists (as out/r22/entry/NOTES.md names them) on a page of this round.
tools/smoke-v14.json (62) + round 20's 5 (round 22's one changed line) + round 22's 2 x 10 + second pass 3 ... = 90.
The list is put together from the original files here (out/r22/entry/smoke.py's own __main__ recipe), not from the
builder's script. Only the page and the folder for the pictures differ.
  python out/r27/checka/mk/smoke_run.py <page> <tag>     -> out/r27/checka/logs/<tag>.log
"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); CHK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CHK)))
R22 = os.path.join(ROOT, 'out', 'r22', 'entry')
sys.path.insert(0, R22)
import smoke as S22
import second

page = sys.argv[1]; tag = sys.argv[2]
base = json.load(open(os.path.join(ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
old = base + [dict(s) for s in S22.S20.NEW]
n_changed = 0
for s in old:
    if S22.OLD_LINE in s.get('js', ''):
        s['js'] = s['js'].replace(S22.OLD_LINE, S22.NEW_LINE); n_changed += 1
assert n_changed == 1, n_changed
new = S22.steps_for('alongonce') + S22.steps_for('pulledplane') + second.STEPS + S22.LAST
steps = [dict(s) for s in old + new]
counts = (len(base), len(S22.S20.NEW), len(S22.steps_for('alongonce')), len(S22.steps_for('pulledplane')), len(second.STEPS), len(S22.LAST))
os.makedirs(os.path.join(CHK, 'smoke'), exist_ok=True); os.makedirs(os.path.join(CHK, 'logs'), exist_ok=True)
for s in steps:
    if 'shot' in s:
        s['shot'] = 'out/r27/checka/smoke/%s-%s' % (tag, os.path.basename(s['shot']))
sj = os.path.join(CHK, 'logs', tag + '-steps.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
t0 = time.time()
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
waited = sum(1 for l in lines if re.match(r'step \d+ waited', l))
timed = sum(1 for l in lines if 'TIMED OUT' in l)
tail = 'page %s; list %s = %d steps; results: %d; waits finished: %d; waits timed out: %d; exit %d; %.0f s\n' % (
    page, '+'.join(str(c) for c in counts), len(steps), results, waited, timed, p.returncode, time.time() - t0)
with open(os.path.join(CHK, 'logs', tag + '.log'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n' + tail)
print('\n'.join(lines[-14:])); print(tail)
sys.exit(p.returncode)
