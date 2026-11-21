"""Round 28, dial checker (ui): round 26's lists (out/r26/final/use.js, spot.js, phone.js) on a page of round 28.
The list is cut into steps by round 26's own function (run_final.steps_of, imported, with its own p_prelude.js), and
the page is taken exactly as run_final.py takes it (first a wait for the finished picture, 110 s; tools/shot.py with
--size and --theme). The only change: pictures and the log go to out/r28/fix/ui/r26/ instead of out/r26/final/.

  python -B out/r28/fix/ui/mk/old26.py <list.js> <page name in dist, without .html> <size> <theme> <log name>
"""
import json, os, subprocess, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
R26 = os.path.join(ROOT, 'out', 'r26', 'final')
sys.path.insert(0, R26)
import run_final as RF

name, page, size, theme, log = sys.argv[1:6]
OUT = os.path.join(UI, 'r26'); os.makedirs(OUT, exist_ok=True)
defs = {'THEME': theme, 'SIZE': size}
acts = [{"wait": "done", "timeout": 110}] + RF.steps_of(os.path.join(R26, name), os.path.join(R26, 'p_prelude.js'), defs)
for a in acts:
    if 'shot' in a:
        s = a['shot'].replace('NAME', log).replace('\\', '/')
        assert s.startswith('out/r26/final/'), s
        a['shot'] = 'out/r28/fix/ui/r26/' + s[len('out/r26/final/'):]
sj = os.path.join(OUT, log + '-steps.json')
json.dump(acts, open(sj, 'w', encoding='utf-8'))
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
t0 = time.time()
r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join('tools', 'shot.py'), '--url', 'dist/%s.html' % page,
                    '--actions', sj, '--size', size, '--theme', theme], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
text = 'page dist/%s.html, size %s, theme %s, list %s, started %s, took %.0f s\n' % (page, size, theme, name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t0)), time.time() - t0)
text += r.stdout + r.stderr + 'exit code %d\n' % r.returncode
with open(os.path.join(OUT, log + '.log'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print(text[-3000:])
sys.exit(r.returncode)
