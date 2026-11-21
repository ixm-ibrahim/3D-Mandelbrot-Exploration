"""Engineer "dial", fix pass 7: the Douady rabbit's c dials (c along x = -0.122561, nine characters) on a desktop and
on a touch phone, as a picture.   python out/r7/dial/rabbit.py dist/v6.html before"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402

drive.URL, TAG = sys.argv[1], sys.argv[2]
drive.HERE = HERE
for w, h, phone, theme in ((1400, 950, False, "dark"), (375, 812, True, "light")):
    page, proc, prof = drive.launch(w, h, mobile=phone, touch=phone, theme=theme)
    d = drive.Drive(page)
    d.load()
    d.js("document.getElementById('mode-j').click(); const e = document.getElementById('juliaPreset'); e.value = [...e.options].find(o => /rabbit/i.test(o.textContent)).value;"
         "e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
    r = d.js("return ['cx', 'cy', 'cz'].map(i => { const e = document.getElementById(i + 'Num'); return [e.value, e.scrollWidth, e.clientWidth]; });")
    drive.info("%s, %d wide, Douady rabbit [value, scrollWidth, clientWidth] for c along x, y, z: %s" % (drive.URL, w, r))
    d.js("document.getElementById('juliaDials').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    d.shot("%s-rabbit-%d.png" % (TAG, w), "#juliaDials")
    d.js("window.squaringLab.resetAll();"); d.idle(120)
    drive.finish(page, proc, prof, "rabbit %d" % w)
