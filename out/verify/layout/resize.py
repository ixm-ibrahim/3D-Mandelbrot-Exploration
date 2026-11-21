"""Resize the window while a picture is being drawn; check the canvas, the overlays and the page width afterwards."""
import json, os, sys, time
from lab import Lab, HERE

lab = Lab(1400, 950, "dark", False, wait_idle=150)
L = "window.squaringLab"
M = ("const c = document.getElementById('view'), s = document.getElementById('stage'), r = c.getBoundingClientRect(), q = s.getBoundingClientRect(), de = document.documentElement;"
     "const kids = [...s.querySelectorAll('.cam-mode, .cam-zoom, .stage-btns, .hint, #triad')].filter(e => e.checkVisibility()).map(e => { const b = e.getBoundingClientRect(); return [e.className.baseVal || e.className || e.id, Math.round(b.left - q.left), Math.round(b.top - q.top), Math.round(b.width), Math.round(b.height), b.right <= q.right + 1 && b.bottom <= q.bottom + 1 && b.left >= q.left - 1 && b.top >= q.top - 1]; });"
     "return { win: [innerWidth, innerHeight], hscroll: de.scrollWidth - de.clientWidth, stage: [Math.round(q.width), Math.round(q.height)], canvasCss: [Math.round(r.width), Math.round(r.height)], canvasPx: [c.width, c.height],"
     " aspectCss: +(r.width / r.height).toFixed(3), aspectPx: +(c.width / c.height).toFixed(3), idle: %s.idle(), status: document.getElementById('status').textContent, kids };" % L)
def step(name, w, h, mobile=False, trigger=True):
    if trigger:
        lab.js("%s.touch(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));" % L)
    busy = lab.js("return !%s.renderIdle();" % L)
    lab.size(w, h, mobile)
    time.sleep(0.15)
    mid = lab.js(M)
    lab.shot(os.path.join(HERE, "resize-%s-mid.png" % name))
    ok = lab.idle(120)
    time.sleep(0.3)
    end = lab.js(M)
    lab.js("document.getElementById('stage').scrollIntoView({block: 'start'}); await new Promise(r => setTimeout(r, 250));")
    lab.shot(os.path.join(HERE, "resize-%s-end.png" % name))
    lab.js("window.scrollTo(0, 0);")
    print(name, "drawing when resized:", busy); print("   mid", json.dumps(mid, ensure_ascii=False)); print("   end", json.dumps(end, ensure_ascii=False)); sys.stdout.flush()
step("a-800x600", 800, 600)
step("b-1400x950", 1400, 950)
step("c-1000x500", 1000, 500)
step("d-375x812", 375, 812)
step("e-921x700", 921, 700)
step("f-620x700", 620, 700)
step("g-1920x1080", 1920, 1080)
# several quick resizes in a row while drawing
lab.js("%s.touch();" % L)
for w, h in ((1200, 800), (900, 700), (1300, 640), (1100, 900), (1400, 950)):
    lab.size(w, h); time.sleep(0.08)
lab.idle(120); time.sleep(0.3)
print("after a burst", json.dumps(lab.js(M), ensure_ascii=False))
lab.shot(os.path.join(HERE, "resize-h-burst-end.png"))
problems = lab.close()
print("PAGE PROBLEMS:", problems[:20])
