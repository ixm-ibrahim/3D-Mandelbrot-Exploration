"""Round 12, tried rules: a picture of each new entry as the Approach list shows it. -> panel-<id>.png, panel-phone-<id>.png"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
size, pre = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('1400x2200', 'panel-')
steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up';", 'wait': 'done', 'timeout': 300}]
for ap in ('softfold', 'axisbulb', 'pillow'):
    steps.append({'js': "document.getElementById('ap-%s').click(); await new Promise(r => setTimeout(r, 400)); return '%s';" % (ap, ap), 'wait': 'done', 'timeout': 300,
                  'shot': 'out/r12/tried/%s%s.png' % (pre, ap), 'clip': '.rule.is-on'})
sj = os.path.join(HERE, 'panel-steps.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'), indent=1)
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/r12-tried.html', '--size', size, '--actions', sj], cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8')))
