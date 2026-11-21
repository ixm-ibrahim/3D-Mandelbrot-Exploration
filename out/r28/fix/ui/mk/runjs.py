"""Round 28, dial checker (ui): run one JavaScript file in a page of the lab through tools/shot.py and keep the log.

  python -B out/r28/fix/ui/mk/runjs.py <file.js in out/r28/fix/ui/mk> <log name> [page] [size] [theme]
      -> out/r28/fix/ui/logs/<log name>.log (everything shot.py printed) and <log name>.json (what the script returned)
The file is the body of an async function: it may use await and must end with a return.
"""
import json, os, re, subprocess, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
name, log = sys.argv[1], sys.argv[2]
page = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('FIX_PAGE', 'dist/r28-fix.html')
size = sys.argv[4] if len(sys.argv) > 4 else '1400x950'
theme = sys.argv[5] if len(sys.argv) > 5 else 'dark'
steps = [{'wait': 'done', 'timeout': 600}, {'js': open(os.path.join(HERE, name), encoding='utf-8').read(), 'timeout': 900}, {'wait': 'done', 'timeout': 600}]
os.makedirs(os.path.join(UI, 'logs'), exist_ok=True)
sj = os.path.join(UI, 'logs', log + '-steps.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'))
t0 = time.time()
p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', size, '--theme', theme],
                   capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'), cwd=ROOT)
text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
val = None
for line in text.splitlines():
    m = re.match(r'step \d+ result: (.*)$', line)
    if m:
        try:
            val = json.loads(m.group(1))
            if isinstance(val, str):
                try: val = json.loads(val)
                except ValueError: pass
        except ValueError:
            pass
with open(os.path.join(UI, 'logs', log + '.log'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('page %s, size %s, theme %s, script %s, took %.0f s\n' % (page, size, theme, name, time.time() - t0) + text + 'exit %d\n' % p.returncode)
if val is not None:
    with open(os.path.join(UI, 'logs', log + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(val, f, ensure_ascii=False, indent=1)
for s in (sys.stdout,):
    try: s.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
print(json.dumps(val, ensure_ascii=False, indent=1) if val is not None else text[-3000:])
print('exit', p.returncode, '|', 'no console errors' if 'no console errors' in text else 'SEE THE LOG: ' + text[-1500:])
sys.exit(p.returncode)
