"""Tester "dials": the arrows at the low end of dials whose typed limit lies below the slider's end and off the step grid. Real clicks."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive
drive.URL = sys.argv[1] if len(sys.argv) > 1 else "dist/v8.html"
drive.HERE = HERE
E = drive.E
for s in (sys.stdout, sys.stderr):
    s.reconfigure(encoding="utf-8", errors="replace")
page, proc, prof = drive.launch()
d = drive.Drive(page); d.load(); drive.open_all(d)
d.click(E("qUltra"))
d.js("const e = document.getElementById('col-solid'); e.value = '1'; e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
for i, start in (("col-thick", "0.01"), ("qdetail", "0.1"), ("viewSpeed", "0.02"), ("col-glow", "0.03"), ("qres", "0.2")):
    up = "document.getElementById(%s).closest('.dial').querySelector('.dial-up')" % json.dumps(i + "Num")
    down = "document.getElementById(%s).closest('.dial').querySelector('.dial-down')" % json.dumps(i + "Num")
    st = drive.dial_state(d, i)
    d.retype(E(i + "Num"), start)
    seq = [d.js("return %s.value;" % E(i + "Num"))]
    for b in (down, down, down, down, up, up, up):
        d.click(b); seq.append(d.js("return %s.value;" % E(i + "Num")))
    print("info  %s '%s' slider %s, typed %s, toggle %s: from %s, down x4 then up x3: %s" % (i, st["label"], st["slider"][:3], st["title"], st["toggle"], start, seq), flush=True)
drive.finish(page, proc, prof, "grid")
