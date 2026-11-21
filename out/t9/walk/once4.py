import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import Lab, HERE
lab = Lab(); lab.wait_idle(240)
lab.js("for (const d of document.querySelectorAll('details')) d.open = true;"); time.sleep(0.3)
def setk(v):
    lab.js("const e = document.getElementById('qstepkNum'); e.scrollIntoView({ block: 'center' }); e.focus(); e.select();"); lab.p.call("Input.insertText", text=str(v)); lab.key("Enter")
    t = lab.wait_idle(240)
    return lab.picture_stats(os.path.join(HERE, "once4-%s-%s.png" % (tag, v)))
print("slider:", lab.js("const r = document.getElementById('qstepk'); return [r.min, r.max, r.step, r.value];"), flush=True)
for tag, sel in (("opening", None), ("twinbulb", "#twinBulb"), ("twinlathe", "#twinLathe"), ("julia", "#mode-j")):
    lab.click("#resetAll"); lab.wait_idle(120)
    if sel: lab.click(sel); lab.wait_idle(240)
    for v in (0.8, 1.2, 1.5, 1.88, 2):
        st = setk(v)
        print(tag, "ray step", v, "->", round(st["other"], 5), st["colours"], lab.js("return [squaringLab.S.q.stepk, squaringLab.S.q.de, document.getElementById('status').textContent];"), flush=True)
print("problems", lab.problems()); lab.close()
