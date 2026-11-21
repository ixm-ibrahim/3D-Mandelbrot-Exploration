"""Engineer "mesh", fix pass 7: the built-in test fields through the panel of a built page.

  python out/r7/mesh/fields.py r7-mesh      (or v6)   -> out/r7/mesh/fields-<page>.txt
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page = sys.argv[1] if len(sys.argv) > 1 else 'r7-mesh'
steps = [{"wait": "done", "timeout": 200}, {"js": open(os.path.join(HERE, 'fields.js'), encoding='utf-8').read()}]
path = os.path.join(HERE, 'fields.steps.json')
json.dump(steps, open(path, 'w', encoding='utf-8'))
r = subprocess.run([sys.executable, 'tools/shot.py', '--url', 'dist/%s.html' % page, '--actions', path], cwd=ROOT, capture_output=True, text=True,
                   encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
out = r.stdout + r.stderr
lines = ['shot.py exit code %d' % r.returncode]
for line in out.splitlines():
    m = re.match(r'step 2 result: (.*)$', line)
    if m:
        for rec in json.loads(json.loads(m.group(1))):
            lines.append(json.dumps(rec, ensure_ascii=False))
    else:
        lines.append('| ' + line[:300])
open(os.path.join(HERE, 'fields-%s.txt' % page), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
