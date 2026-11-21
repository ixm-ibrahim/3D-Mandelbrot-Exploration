"""Real (trusted) input for the two major camera defects, reusing the driver in notes/camera_real.py.

  python out/fix/camera/real_fix.py dist/fix-camera.html

p4-1: the wheel over a control that sits on the picture must zoom and must not scroll the page.
p7-1: after a real click on Reset view (or + / -) in fly mode, W must fly without clicking the picture again.
"""
import os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "notes"))
import camera_real as R  # noqa: E402

L = "window.squaringLab"


def desktop(d):
    for sel in ["#zoomIn", "#zoomOut", "#reset", "#camFar", "#camNear", "#camArc", "#camFly", "#camRail", "#view"]:
        d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch(); window.scrollTo(0, 0); return 0;" % (L, L, L))
        d.settle()
        x, y = d.at(sel)
        d.mouse("mouseMoved", x, y)
        d0 = d.js("return %s.cam.dist;" % L)
        for _ in range(3):
            d.wheel(x, y, 100)
            time.sleep(0.06)
        d.settle()
        time.sleep(0.3)
        sy, d1 = d.js("return [window.scrollY, %s.cam.dist];" % L)
        R.ok("real wheel over %s: three notches zoom and the page stays put" % sel, sy == 0 and abs(d1 / d0 - 1.12 ** 3) < 1e-6, "scrollY %s, dist x%.4f" % (sy, d1 / d0))
    d.js("%s.resetCam(); %s.touch(); window.scrollTo(0, 0); return 0;" % (L, L))
    d.click("#camFly")
    for sel in ["#reset", "#zoomIn", "#zoomOut"]:
        d.click(sel)
        d.settle()
        p0 = d.js("return %s.basis().pos;" % L)
        d.press("KeyW", 0.5)
        d.settle()
        p1, focus = d.js("return [%s.basis().pos, document.activeElement && document.activeElement.id];" % L)
        moved = sum((a - b) ** 2 for a, b in zip(p0, p1)) ** 0.5
        R.ok("fly mode: after a real click on %s, W moves without clicking the picture" % sel, moved > 0.2 and focus == "view", "moved %.3f, focus on %s" % (moved, focus))
    d.click("#camArc")


R.desktop = desktop
R.touch_screen = lambda d, page: None
R.main()
