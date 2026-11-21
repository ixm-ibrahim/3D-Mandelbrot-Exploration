"""Round 28, dial checker (ui): run a set of the old lists ONE AT A TIME and keep a line for each in logs/queue-<set>.txt.

  python -B out/r28/fix/ui/mk/queue_old.py <set> [wait-for-file]
      set: new    round 26's three lists and round 27's five scripts on dist/r28-ui.html
           old    the same on the frozen page dist/r28-base-ui.html (same6 is left out: it runs both pages itself)
           smokeold  the 90-step smoke list on the frozen page
      wait-for-file: do not start before this file holds a line that starts with "exit" (another browser script of mine)
"""
import os, subprocess, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
PY = [sys.executable, '-B', '-W', 'ignore']
which = sys.argv[1]
if len(sys.argv) > 2:
    while True:
        try:
            if any(l.startswith('exit') for l in open(sys.argv[2], encoding='utf-8', errors='replace')):
                break
        except OSError:
            pass
        time.sleep(3)
mk = lambda n: os.path.join('out', 'r28', 'ui', 'mk', n)
if which == 'new':
    jobs = [('r26 use.js', PY + [mk('old26.py'), 'use.js', 'r28-ui', '1400x950', 'dark', 'use-new']),
            ('r26 spot.js', PY + [mk('old26.py'), 'spot.js', 'r28-ui', '1400x950', 'dark', 'spot-new']),
            ('r26 phone.js', PY + [mk('old26.py'), 'phone.js', 'r28-ui', '390x800', 'dark', 'phone-new']),
            ('r27 verd.py', PY + [mk('old27.py'), 'verd', 'new']),
            ('r27 shape.py', PY + [mk('old27.py'), 'shape', 'new']),
            ('r27 same6.py', PY + [mk('old27.py'), 'same6', 'new']),
            ('r27 flat.py', PY + [mk('old27.py'), 'flat', 'new']),
            ('r27 holes.py', PY + [mk('old27.py'), 'holes', 'new'])]
elif which == 'old':
    jobs = [('r26 use.js', PY + [mk('old26.py'), 'use.js', 'r28-base-ui', '1400x950', 'dark', 'use-old']),
            ('r26 spot.js', PY + [mk('old26.py'), 'spot.js', 'r28-base-ui', '1400x950', 'dark', 'spot-old']),
            ('r26 phone.js', PY + [mk('old26.py'), 'phone.js', 'r28-base-ui', '390x800', 'dark', 'phone-old']),
            ('r27 verd.py', PY + [mk('old27.py'), 'verd', 'old']),
            ('r27 shape.py', PY + [mk('old27.py'), 'shape', 'old']),
            ('r27 flat.py', PY + [mk('old27.py'), 'flat', 'old']),
            ('r27 holes.py', PY + [mk('old27.py'), 'holes', 'old'])]
elif which == 'smokeold':
    jobs = [('smoke list, frozen page', PY + [mk('smoke28.py'), 'dist/r28-base.html', 'smoke-old'])]
else:
    sys.exit('unknown set')
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
out = os.path.join(UI, 'logs', 'queue-%s.txt' % which)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('set %s, started %s\n' % (which, time.strftime('%H:%M:%S')))
for name, cmd in jobs:
    t0 = time.time()
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = (r.stdout + r.stderr)
    with open(os.path.join(UI, 'logs', 'queue-%s-%s.out' % (which, name.replace(' ', '-').replace('.', '-').replace(',', ''))), 'w', encoding='utf-8', newline='\n') as f:
        f.write(tail)
    with open(out, 'a', encoding='utf-8', newline='\n') as f:
        f.write('%-26s exit %d, %.0f s, %s\n' % (name, r.returncode, time.time() - t0, 'no console errors' if 'no console errors' in tail else 'NO "no console errors" LINE IN ITS OUTPUT'))
with open(out, 'a', encoding='utf-8', newline='\n') as f:
    f.write('exit: the set is done at %s\n' % time.strftime('%H:%M:%S'))
