import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.abspath(os.path.join(here, "..", "..", ".."))
GO = "const L = window.squaringLab, S = L.S; const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); }; const idx = id => L.APPROACHES.findIndex(a => a.id === id);"
probe = open(os.path.join(here, "probe2.js"), encoding="utf-8").read()
steps = [{"wait": "done", "timeout": 120}]
for ap, extra, mode in (("pillow", "S.param.pillow.layout = 0;", "j"), ("pillow", "S.param.pillow.layout = 0;", "m"), ("softfold", "", "m"), ("pillow", "S.param.pillow.layout = 1;", "m"), ("mercator", "", "m")):
    steps += [{"js": GO + "S.approach = idx('%s'); %s S.mode = '%s'; S.c = [-1, 0, 0]; S.n = 2; go(); return 'set';" % (ap, extra, mode)}, {"wait": "done", "timeout": 150}, {"js": probe}]
act = os.path.join(here, "probe2.actions.json"); json.dump(steps, open(act, "w", encoding="utf-8"))
p = subprocess.run([sys.executable, os.path.join(root, "tools", "shot.py"), "--url", os.path.join(root, "dist", "r12-check-maths.html"), "--size", "1400x950", "--actions", act], cwd=root, env=dict(os.environ, PYTHONIOENCODING="utf-8"), capture_output=True, text=True, encoding="utf-8", errors="replace")
open(os.path.join(here, "probe2.log"), "w", encoding="utf-8").write(p.stdout + "\n--- stderr ---\n" + p.stderr + "\nexit code %d\n" % p.returncode)
for line in p.stdout.splitlines():
    if '"{' in line: print(json.loads(line[line.find('"{'):]))
print(p.stdout[-200:], "exit code", p.returncode)
