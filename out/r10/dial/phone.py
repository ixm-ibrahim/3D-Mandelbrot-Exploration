"""Engineer "dial", round 10: t9-dials-2 on a 375 x 812 touch phone with finger taps (the tester's tap).

  python out/r10/dial/phone.py dist/r10-dial.html after
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402
drive.URL = sys.argv[1]
drive.HERE = HERE
tag = sys.argv[2]
E, ok, info = drive.E, drive.ok, drive.info
for s in (sys.stdout, sys.stderr):
    s.reconfigure(encoding="utf-8", errors="replace")

page, proc, prof = drive.launch(375, 812, mobile=True, touch=True, theme="light")
d = drive.Drive(page); d.load(); drive.open_all(d)


def tap(expr):
    x, y = d.at(expr)
    d.touch("touchStart", [(x, y)]); d.touch("touchEnd", []); time.sleep(0.12)


tap(E("qUltra"))
d.js("const e = document.getElementById('col-solid'); e.value = '1'; e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
up = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-up')" % json.dumps(i + "Num")
down = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-down')" % json.dumps(i + "Num")
box = lambda i: d.js("return %s.value;" % E(i + "Num"))
info("pointer coarse:", d.js("return matchMedia('(pointer: coarse)').matches;"), "window", d.js("return [innerWidth, innerHeight];"))
want = {"col-thick": ("0.01", ["0.01", "0.005", "0.0005", "0.0005", "0.005", "0.01", "0.015"]),
        "qdetail": ("0.1", ["0.1", "0.05", "0.02", "0.02", "0.05", "0.1", "0.15"]),
        "viewSpeed": ("0.02", ["0.02", "0.01", "0.001", "0.001", "0.01", "0.02", "0.03"])}
for i, (start, exp) in want.items():
    d.js("const n = %s; n.focus(); n.value = %s; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); n.blur();" % (E(i + "Num"), json.dumps(start)))
    seq = [box(i)]
    for m in "dddUUU".lower():
        tap(up(i) if m == "u" else down(i)); seq.append(box(i))
    ok("phone, finger taps: %s from %s, down x3 then up x3 gives %s" % (i, start, exp[1:]), seq == exp, seq)
d.js("const e = document.getElementById('col-thickNum').closest('.dial'); e.id = 'r10ThickDial';")
d.js("const n = document.getElementById('col-thickNum'); n.focus(); n.value = '0.005'; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true })); n.blur();")
tap(down("col-thick")); tap(up("col-thick"))
page.shot(os.path.join(HERE, "%s-phone-thick-up.png" % tag), "#r10ThickDial")
info("wrote out/r10/dial/%s-phone-thick-up.png; box" % tag, box("col-thick"), "sideways scroll:", d.js("return document.documentElement.scrollWidth > innerWidth;"))
drive.finish(page, proc, prof, "phone")
print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)))
