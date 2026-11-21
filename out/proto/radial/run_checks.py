"""Run out/proto/radial/checks.js inside a built page and save the report.
   python out/proto/radial/run_checks.py [page.html] [report.txt]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
page = sys.argv[1] if len(sys.argv) > 1 else 'dist/proto-radial.html'
rep = sys.argv[2] if len(sys.argv) > 2 else 'out/proto/radial/checks.txt'
steps = [{"js": "const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 1; L.S.q.res = 0.25; L.touch(); return 'page up, approach ' + L.APPROACHES[L.S.approach].id;", "wait": "done", "timeout": 300},
         {"js": open(os.path.join(HERE, 'checks.js'), encoding='utf-8').read()}]
sj = os.path.join(HERE, 'checks.json')
json.dump(steps, open(sj, 'w', encoding='utf-8'))
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'notes', 'approaches_run.py'), page, rep, '--actions', sj], cwd=ROOT))
