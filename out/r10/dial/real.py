"""Engineer "dial", round 10: t9-dials-2 with a real mouse and keyboard, in the words of the defect and beyond.

  python out/r10/dial/real.py dist/v9m.html before
  python out/r10/dial/real.py dist/r10-dial.html after

Lines starting with "pass"/"FAIL" state what the fixed page must do; on the page before the fix some of them fail,
which is the fault. Pictures go to out/r10/dial/<tag>-*.png.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402
drive.URL = sys.argv[1]
drive.HERE = HERE
tag = sys.argv[2]
E, ok, info, SHIFT = drive.E, drive.ok, drive.info, drive.SHIFT
for s in (sys.stdout, sys.stderr):
    s.reconfigure(encoding="utf-8", errors="replace")

page, proc, prof = drive.launch()
d = drive.Drive(page); d.load(); drive.open_all(d)
d.click(E("qUltra"))
d.js("const e = document.getElementById('col-solid'); e.value = '1'; e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
up = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-up')" % json.dumps(i + "Num")
down = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-down')" % json.dumps(i + "Num")
box = lambda i: d.js("return %s.value;" % E(i + "Num"))


def walk(i, start, moves, modifiers=0):
    d.retype(E(i + "Num"), start)
    seq = [box(i)]
    for m in moves:
        d.click(up(i) if m == "u" else down(i), modifiers=modifiers); seq.append(box(i))
    return seq


def shot(name, sel):
    page.shot(os.path.join(HERE, "%s-%s.png" % (tag, name)), sel)
    info("wrote out/r10/dial/%s-%s.png" % (tag, name))


# 1. the defect's own words: Trap thickness from 0.05, the down arrow ten times, then the up arrow, and on up to 0.05
seq = walk("col-thick", "0.05", "d" * 11 + "u" * 10)
ok("Trap thickness from 0.05: down x10 runs 0.045 ... 0.005 and then the limit 0.0005, an eleventh press stays there",
   seq[:12] == ["0.05", "0.045", "0.04", "0.035", "0.03", "0.025", "0.02", "0.015", "0.01", "0.005", "0.0005", "0.0005"], seq[:12])
ok("Trap thickness: up from the limit 0.0005 gives 0.005, 0.01, 0.015 and reaches 0.05 again on the tenth press",
   seq[12:] == ["0.005", "0.01", "0.015", "0.02", "0.025", "0.03", "0.035", "0.04", "0.045", "0.05"], seq[12:])
# 2. Surface threshold and Fly speed, as the defect says (type 0.1 and 0.02 first)
seq = walk("qdetail", "0.1", "dddd" + "uuu")
ok("Surface threshold from 0.1: down x4 then up x3 gives 0.05, 0.02, 0.02, 0.02, then 0.05, 0.1, 0.15", seq == ["0.1", "0.05", "0.02", "0.02", "0.02", "0.05", "0.1", "0.15"], seq)
seq = walk("viewSpeed", "0.02", "dddd" + "uuu")
ok("Fly speed from 0.02: down x4 then up x3 gives 0.01, 0.001, 0.001, 0.001, then 0.01, 0.02, 0.03", seq == ["0.02", "0.01", "0.001", "0.001", "0.001", "0.01", "0.02", "0.03"], seq)
# 3. ten steps at once (Shift with a real click)
seq = walk("col-thick", "0.03", "dd" + "uu", modifiers=SHIFT)
ok("Trap thickness from 0.03 with Shift: down stops on the last round value 0.005, down again goes to the limit 0.0005, up gives 0.05 and 0.1", seq == ["0.03", "0.005", "0.0005", "0.05", "0.1"], seq)
# 4. holding the arrow (the page repeats every 60 ms after 0.42 s)
d.retype(E("col-thickNum"), "0.05")
d.js("window.__seen = []; const n = document.getElementById('col-thickNum'); window.__t = setInterval(() => { const s = window.__seen; if (s[s.length - 1] !== n.value) s.push(n.value); }, 4);")
time.sleep(0.1)
d.click(down("col-thick"), hold=1.6); time.sleep(0.15)
seen = d.js("const s = window.__seen; window.__seen = []; return s;")
ok("Trap thickness: holding the down arrow from 0.05 runs through the round values and comes to rest on 0.0005",
   seen[-3:] == ["0.01", "0.005", "0.0005"] and seen[:2] == ["0.05", "0.045"], seen)
d.click(up("col-thick"), hold=1.3); time.sleep(0.15)
seen = d.js("const s = window.__seen; clearInterval(window.__t); return s;")
off = [v for v in seen[1:] if abs(float(v) / 0.005 - round(float(v) / 0.005)) > 1e-6]   # seen[0] is the limit the hold starts from
ok("Trap thickness: holding the up arrow from the limit 0.0005 passes only whole multiples of 0.005 (0.005, 0.01, ...)", len(seen) > 5 and not off and seen[:2] == ["0.0005", "0.005"], seen[:8] + ["..."] + seen[-2:])
# 5. the keyboard in the box
d.retype(E("col-thickNum"), "0.01")
d.click(E("col-thickNum"))
keys = []
for k, m in (("ArrowDown", 0), ("ArrowDown", 0), ("ArrowDown", 0), ("ArrowUp", 0), ("ArrowUp", 0), ("ArrowDown", 0), ("ArrowDown", 0), ("ArrowUp", SHIFT), ("PageDown", 0), ("PageDown", 0), ("PageUp", 0)):
    d.press(k, modifiers=m); keys.append(box("col-thick"))
ok("Trap thickness, keys from 0.01: Down x3, Up x2, Down x2, Shift+Up, PageDown x2, PageUp give 0.005, 0.0005, 0.0005, 0.005, 0.01, 0.005, 0.0005, 0.05, 0.005, 0.0005, 0.05",
   keys == ["0.005", "0.0005", "0.0005", "0.005", "0.01", "0.005", "0.0005", "0.05", "0.005", "0.0005", "0.05"], keys)
d.press("Tab")
# 6. what must stay: a typed value between the round ones keeps its own offset (the kit's rule since round 1)
seq = walk("col-thick", "0.0125", "u" + "ddd" + "d" + "u")
ok("Trap thickness typed 0.0125: up 0.0175, down 0.0125, 0.0075, 0.0025, then the limit 0.0005, then up 0.005",
   seq == ["0.0125", "0.0175", "0.0125", "0.0075", "0.0025", "0.0005", "0.005"], seq)
seq = walk("pow", "2.37", "uud")
ok("Power n typed 2.37: up 2.47, 2.57, down 2.47 (as before)", seq == ["2.37", "2.47", "2.57", "2.47"], seq)
seq = walk("pow", "23.95", "uu" + "d")
ok("Power n from 23.95: up 24, 24 (a limit that is a round value), down 23.9 (as before)", seq == ["23.95", "24", "24", "23.9"], seq)
d.retype(E("powNum"), "2")
# 7. the whole-number toggle at the low end (as before)
d.retype(E("col-thickNum"), "0.05"); d.click(E("col-thickStep"))
seq = [box("col-thick")]
for m in "duud":
    d.click(up("col-thick") if m == "u" else down("col-thick")); seq.append(box("col-thick"))
d.click(E("col-thickStep"))
ok("Trap thickness on the whole-number toggle from 0.05: down 0.0005, up 1, up 2, down 1 (as before)", seq == ["0.05", "0.0005", "1", "2", "1"], seq)
# 8. the tooltips and the limit mark, and what the user sees
d.retype(E("col-thickNum"), "0.005"); d.click(down("col-thick"))
st = d.js("const n = document.getElementById('col-thickNum'), e = n.closest('.dial'); return [n.value, e.dataset.at, e.querySelector('.dial-up').title, e.querySelector('.dial-down').title, n.title];")
info("Trap thickness at the limit: box, limit mark, tooltips:", json.dumps(st, ensure_ascii=False))
dial = "document.getElementById('col-thickNum').closest('.dial')"
d.js("%s.id = 'r10ThickDial'; %s.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 250));" % (dial, dial))
shot("thick-low", "#r10ThickDial")
d.click(up("col-thick"), scroll=False); time.sleep(0.2)
info("Trap thickness after one press up from the limit:", box("col-thick"), "state", d.js("return window.squaringLab.S.colour.thick;"))
shot("thick-up", "#r10ThickDial")
d.retype(E("col-thickNum"), "0.05")
drive.finish(page, proc, prof, "real")
print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)))
