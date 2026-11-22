"""Open the built page in headless Chrome and draw everything once.

  python tools/smoke.py

Draws every approach as a Julia set and as a Mandelbrot set, both Kleinian pictures, the 2D view and the Learn
tab, at low quality. Fails if a picture never finishes or the page logs an error.
"""
import os, sys, time

from shot import ROOT, open_page, report, utf8_output

PAGE = os.path.join(ROOT, "squaring-lab.html")
SETUP = ("const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
         "const draw = () => { S.q.res = 0.5; S.q.aa = 1; L.syncControls(); L.refresh(); }; ")


def draw(page, what, js, failed):
    page.js(SETUP + js)
    if not page.wait("done", 300):
        failed.append(what)
        print("never finished: " + what)


def main():
    utf8_output()
    failed, t0 = [], time.time()
    with open_page(PAGE, (1100, 900)) as page:
        page.wait("done", 180)
        ids = page.js("return window.squaringLab.APPROACHES.map(a => a.id);")
        for tab, name in (("mode-j", "Julia"), ("mode-m", "Mandelbrot")):
            for i, approach in enumerate(ids):
                draw(page, "%s, %s" % (name, approach), "$('%s').click(); S.approach = %d; draw();" % (tab, i), failed)
        draw(page, "2D view", "S.approach = 0; S.flat = true; draw();", failed)
        draw(page, "Kleinian", "S.flat = false; $('mode-k').click(); S.k.group = 0; draw();", failed)
        draw(page, "Balls on balls", "S.k.group = 1; draw();", failed)
        page.js(SETUP + "S.k.group = 0; $('mode-l').click(); await new Promise(r => setTimeout(r, 1500)); "
                        "$('learnFollowPoint').click(); await new Promise(r => setTimeout(r, 1500));")
        code = report(page)
    print("%d approaches drawn twice in %.0f s" % (len(ids), time.time() - t0))
    sys.exit(2 if failed else code)


if __name__ == "__main__":
    main()
