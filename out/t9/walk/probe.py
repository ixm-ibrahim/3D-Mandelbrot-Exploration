import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import Lab, HERE
lab = Lab()
t = lab.wait_idle(240)
print("idle after", t)
print(json.dumps(lab.check(), ensure_ascii=False))
print(lab.picture_stats(os.path.join(HERE, "probe-pic.png")))
lab.js("document.getElementById('collapseAll').click(); await new Promise(r => setTimeout(r, 100)); if (document.getElementById('collapseAll').textContent.startsWith('Expand')) document.getElementById('collapseAll').click();")
time.sleep(0.5)
ctl = lab.js("return __w.list();")
from collections import Counter
print(len(ctl), Counter(c["kind"] for c in ctl))
for c in ctl:
    print(json.dumps(c, ensure_ascii=False)[:230])
st = lab.js("return __w.state();")
print(json.dumps(st, ensure_ascii=False)[:3000])
print("problems:", lab.problems())
lab.close()
