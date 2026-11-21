"""Round 22, entrycheck second pass: the smoke lists on dist/r22-entry.html at 1400x950.
Steps are read, not copied: tools/smoke-v14.json (62), out/r20/entry/smoke.py NEW (5; the one line about windsq's
place changed as the builder says), out/r22/entry/smoke.py steps_for x 2 + LAST (20), out/r22/entry/second.py STEPS (3).
Pictures go to out/r22/entrycheck2/smoke/.
  python out/r22/entrycheck2/e2_smoke.py
"""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drv

ROOT = drv.ROOT


def load(name, path):
    d = os.path.dirname(path)
    sys.path.insert(0, d)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    finally:
        sys.path.remove(d)
    return m


S22 = load('smoke22', os.path.join(ROOT, 'out', 'r22', 'entry', 'smoke.py'))
S20 = S22.S20
SEC = S22.second

base = json.load(open(os.path.join(ROOT, 'tools', 'smoke-v14.json'), encoding='utf-8'))
old = base + [dict(s) for s in S20.NEW]
changed = 0
for s in old:
    if S22.OLD_LINE in s.get('js', ''):
        s['js'] = s['js'].replace(S22.OLD_LINE, S22.NEW_LINE); changed += 1
first = S22.steps_for('alongonce') + S22.steps_for('pulledplane')
new = first + [dict(s) for s in SEC.STEPS] + S22.LAST
steps = old + new
for s in steps:
    if 'shot' in s:
        s['shot'] = 'out/r22/entrycheck2/smoke/' + os.path.basename(s['shot'])
os.makedirs(os.path.join(HERE, 'smoke'), exist_ok=True)
code, text, vals = drv.shot(drv.PAGE, steps, 'smoke-steps', '1400x950')
text += 'steps: %d of tools/smoke-v14.json + %d of round 20 (%d line changed) + %d first pass + %d second pass + %d last = %d; results %d\nexit %d\n' % (
    len(base), len(S20.NEW), changed, len(first), len(SEC.STEPS), len(S22.LAST), len(steps), len(vals), code)
drv.write('smoke.log', text)
print('\n'.join(text.splitlines()[-30:]))
sys.exit(code)
