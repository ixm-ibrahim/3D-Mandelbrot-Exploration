"""Lost and changed pixels at a step share against a careful render (share 0.25, 900 steps), per preset and page.
   python out/r4/kleinian/t6.py PAGE TAG SHARES PRESETS   e.g.  dist/r4-kleinian.html new 0.8,0.5 8,14,2,5,0"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
page, tag = sys.argv[1], sys.argv[2]
shares = [float(s) for s in sys.argv[3].split(',')]
presets = [int(s) for s in sys.argv[4].split(',')]
hide = "document.querySelectorAll('#stage > *:not(canvas)').forEach(e => { e.style.visibility = 'hidden'; });"
acts = [{"js": "const L = window.squaringLab; document.getElementById('mode-k').click(); document.getElementById('qBal').click(); L.S.q.aa = 3; L.R.capOff = 1; " + hide + " L.touch(); return 1;", "wait": "done", "timeout": 300}]
for i in presets:
    for s in shares + [-1]:
        js = "const L = window.squaringLab; L.applyKleinPreset(L.KLEIN_PRESETS[%d]); L.frameKleinPreset(L.KLEIN_PRESETS[%d]); L.S.q.stepk = %g; L.S.q.steps = %d; L.touch(); const t0 = performance.now(); window.__t0 = t0; return 1;" % (i, i, 0.25 if s < 0 else s, 900 if s < 0 else 260)
        acts.append({"js": js, "wait": "done", "timeout": 600, "shot": "out/r4/kleinian/sc/%s-%02d-%s.png" % (tag, i, 'ref' if s < 0 else ('s%03d' % round(100 * s))), "clip": "#stage"})
        acts.append({"js": "return Math.round(performance.now() - window.__t0);"})
os.makedirs(os.path.join(ROOT, 'out/r4/kleinian/sc'), exist_ok=True)
steps = os.path.join(ROOT, 'out/r4/kleinian/sc/%s-steps.json' % tag)
json.dump(acts, open(steps, 'w'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/shot.py'), '--url', os.path.join(ROOT, page), '--actions', steps], capture_output=True, text=True, cwd=ROOT, encoding='utf-8')
times = [int(l.split(': ')[1]) for l in r.stdout.splitlines() if 'result' in l and l.split(': ')[1].strip().isdigit()]
print([l for l in r.stdout.splitlines() if 'error' in l.lower() or 'PROBLEM' in l or 'TIMED' in l or 'console' in l])
def load(p): return np.asarray(Image.open(os.path.join(ROOT, p)).convert('RGB')).astype(int)
ti = 0
for i in presets:
    ref = load("out/r4/kleinian/sc/%s-%02d-ref.png" % (tag, i)); bg = ref[5, 5]; mr = np.abs(ref - bg).sum(2) > 40
    row = []
    for s in shares:
        a = load("out/r4/kleinian/sc/%s-%02d-s%03d.png" % (tag, i, round(100 * s))); ma = np.abs(a - bg).sum(2) > 40
        row.append("share %.2f: lost %.2f%% changed %.2f%% (%d ms)" % (s, 100 * (mr & ~ma).sum() / mr.sum(), 100 * (mr & ma & (np.abs(a - ref).sum(2) > 90)).sum() / mr.sum(), times[ti])); ti += 1
    print("preset %2d objpx %6d | %s | careful %d ms" % (i, mr.sum(), " | ".join(row), times[ti])); ti += 1
