"""Run out/lab2/softfold/checks.js inside the built test page and save the report.
   python out/lab2/softfold/run_checks.py [page.html] [report.txt] [indices of the settings to run, e.g. 0,1]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page = sys.argv[1] if len(sys.argv) > 1 else 'dist/lab2-softfold.html'
rep = sys.argv[2] if len(sys.argv) > 2 else 'out/lab2/softfold/checks.txt'
only = '[%s]' % sys.argv[3] if len(sys.argv) > 3 else 'null'
steps = [{"js": "const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 1; L.S.q.res = 0.25; L.touch(); window.__only = %s; return 'page up, approach ' + L.APPROACHES[L.S.approach].id;" % only, "wait": "done", "timeout": 300},
         {"js": open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read()}]
sj = os.path.join(HERE, 'checks.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'))
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'notes', 'approaches_run.py'), page, rep, '--actions', sj], cwd=ROOT))
