"""Run only the picture-job steps of tools/smoke.json (and report what the panel says if they fail).

  python out/r4/render-export/smoke_part.py [dist/r4-render-export.html]
"""
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
steps = json.load(io.open(os.path.join(ROOT, 'tools', 'smoke.json'), encoding='utf-8'))
i = next(k for k, a in enumerate(steps) if 'picture job started' in a.get('js', ''))
probe = {"js": "const $ = id => document.getElementById(id); return { open: $('secExport').open, msg: $('exportMsg').textContent, busy: window.squaringLab.exportBusy(), "
               "saveWidth: $('exportSave').getBoundingClientRect().width, doneHidden: $('exportSave').closest('.export-done').hidden, step: $('exportStep').textContent };"}
wait = dict(steps[i + 1]); wait_only = {"js": "return 'waiting for the job';", "wait": wait.get('wait'), "timeout": wait.get('timeout', 300)}
part = [{"js": "window.squaringLab.R.warmOn = false; return 'loaded';", "wait": "done", "timeout": 300}, steps[i], wait_only, probe, {k: v for k, v in steps[i + 1].items() if k in ('js',)}]
path = os.path.join(HERE, 'smoke_part.steps.json')
json.dump(part, io.open(path, 'w', encoding='utf-8', newline='\n'))
url = sys.argv[1] if len(sys.argv) > 1 else 'dist/r4-render-export.html'
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', url, '--actions', path], cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8')))
