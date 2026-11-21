"""Round 22, entrycheck: re-run of the smoke lists on dist/r22-entry.html at 1400x950.
The steps are read, not copied: tools/smoke-v14.json (62), out/r20/entry/smoke.py NEW (5, UNCHANGED first, to see what
breaks; then with the builder's one changed line), out/r22/entry/smoke.py (the builder's 20 new steps).
Pictures go to out/r22/entrycheck/smoke/. Nothing is written outside out/r22/entrycheck/.
  python out/r22/entrycheck/ec_smoke.py
"""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive

ROOT = drive.ROOT


def load(name, path):
    d = os.path.dirname(path)
    sys.path.insert(0, d)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    finally:
        sys.path.remove(d)
    return m


S22 = load('smoke22', os.path.join(ROOT, 'out', 'r22', 'entry', 'smoke.py'))   # loads round 20's steps as S22.S20
S20 = S22.S20

base = json.load(open(os.path.join(ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
old = base + [dict(s) for s in S20.NEW]
changed = 0
for s in old:
    if S22.OLD_LINE in s.get('js', ''):
        s['js'] = s['js'].replace(S22.OLD_LINE, S22.NEW_LINE); changed += 1
new = S22.steps_for('alongonce') + S22.steps_for('pulledplane') + S22.LAST
steps = old + new
for s in steps:
    if 'shot' in s:
        s['shot'] = 'out/r22/entrycheck/smoke/' + os.path.basename(s['shot'])
os.makedirs(os.path.join(HERE, 'smoke'), exist_ok=True)
code, text, vals = drive.shot(drive.PAGE, steps, 'smoke-steps', '1400x950')
text += 'steps: %d of tools/smoke-v14.json + %d of round 20 (%d line changed) + %d new = %d; results %d\nexit %d\n' % (
    len(base), len(S20.NEW), changed, len(new), len(steps), len(vals), code)
drive.write('smoke.log', text)
print('\n'.join(text.splitlines()[-40:]))
sys.exit(code)
