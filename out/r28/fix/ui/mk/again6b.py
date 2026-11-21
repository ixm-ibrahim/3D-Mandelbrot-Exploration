"""Round 28, dial checker (ui): the one smoke picture that differed between the new and the frozen page for a reason
other than a moving camera (smoke-6b-approach-menu.png, step 8: the picture behind the open Approach list was caught
half drawn on the new page). The first nine steps of the list are run again, three times on each page; step 8 has no
wait of its own in the old list, so the picture is taken whenever the step ends. Here the status line under the
picture is read at that moment and the picture is saved again after the picture has finished, and that second one is
compared between the pages.
  python -B out/r28/fix/ui/mk/again6b.py   -> out/r28/fix/ui/logs/again6b.txt, pictures out/r28/fix/ui/again6b/
"""
import json, os, re, subprocess, sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(UI))))
steps = json.load(open(os.path.join(UI, 'logs', 'smoke-new-steps.json'), encoding='utf-8'))[:8]
out = []
pics = {}
for tag, page in (('new', os.environ.get('FIX_PAGE', 'dist/r28-fix.html')), ('frozen', 'dist/r28-base.html')):
    for k in range(3):
        st = [dict(s) for s in steps]
        for s in st:
            if 'shot' in s:
                s['shot'] = 'out/r28/fix/ui/again6b/%s-%d-%s' % (tag, k, os.path.basename(s['shot']))
        st.append({'js': "return document.getElementById('status').textContent;"})
        st.append({'wait': 'done', 'timeout': 300, 'shot': 'out/r28/fix/ui/again6b/%s-%d-finished.png' % (tag, k)})
        st.append({'js': "return document.getElementById('status').textContent;"})
        sj = os.path.join(UI, 'logs', 'again6b-steps.json'); json.dump(st, open(sj, 'w', encoding='utf-8'))
        p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'shot.py'), '--url', page, '--actions', sj, '--size', '1400x950'],
                           capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'), cwd=ROOT)
        text = p.stdout.decode('utf-8', 'replace')
        res = re.findall(r'step (9|11) result: (.*)', text)
        out.append('%s page, run %d: exit %d, %s; status when step 8 ended: %s; after waiting: %s' % (tag, k, p.returncode, 'no console errors' if 'no console errors' in text else 'SEE OUTPUT', res[0][1] if res else '?', res[1][1] if len(res) > 1 else '?'))
        pics[(tag, k)] = ('out/r28/fix/ui/again6b/%s-%d-smoke-6b-approach-menu.png' % (tag, k), 'out/r28/fix/ui/again6b/%s-%d-finished.png' % (tag, k))
img = lambda p: np.asarray(Image.open(os.path.join(ROOT, p)).convert('RGB')).astype(int)
ref_mid, ref_fin = img(pics[('frozen', 0)][0]), img(pics[('frozen', 0)][1])
for key, (mid, fin) in pics.items():
    a, b = img(mid), img(fin)
    out.append('%s %d: the picture as step 8 took it differs from frozen run 0 at %d pixels; the picture after the wait differs from frozen run 0 (after its wait) at %d pixels' % (
        key[0], key[1], int((np.abs(a - ref_mid).max(axis=2) > 0).sum()) if a.shape == ref_mid.shape else -1, int((np.abs(b - ref_fin).max(axis=2) > 0).sum()) if b.shape == ref_fin.shape else -1))
text = '\n'.join(out) + '\n'
open(os.path.join(UI, 'logs', 'again6b.txt'), 'w', encoding='utf-8', newline='\n').write(text)
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); print(text)
