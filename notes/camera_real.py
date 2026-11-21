"""Drive the camera with REAL input (mouse, wheel, keyboard, touch) through the Chrome DevTools protocol.

tools/shot.py can only run page JavaScript, so its events are synthetic: no pointer capture, no focus, no
native double-click or blur. This script sends trusted input instead and checks what the camera does.

  python notes/camera_real.py [dist/camera-test.html]

The page must be built with the test boot (out/camera/boot-test.js), which exposes basis(), CV and friends.
Screenshots go to out/camera/. Exit code 0 when every line says pass.
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

OUT = os.path.join(ROOT, "out", "camera")
L = "window.squaringLab"
VK = {"Tab": 9, "Enter": 13, "Escape": 27, "Space": 32, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40,
      "KeyW": 87, "KeyA": 65, "KeyS": 83, "KeyD": 68, "KeyQ": 81, "KeyE": 69, "KeyF": 70, "ShiftLeft": 16}
KEYNAME = {"Space": " ", "ShiftLeft": "Shift"}
results = []


def ok(name, cond, detail=""):
    results.append(bool(cond))
    print(("pass  " if cond else "FAIL  ") + name + ("" if cond and detail == "" else "  :: " + str(detail)))


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, rel):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 30)
        if not self.p.wait(L + " && " + L + ".idle()", 90):
            raise RuntimeError("the page never finished drawing")
        time.sleep(0.3)

    def box(self, sel):
        return self.js("const b = document.querySelector(%s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))

    def at(self, sel, fx=0.5, fy=0.5):
        b = self.box(sel)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, fx=0.5, fy=0.5):
        x, y = self.at(sel, fx, fy)
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n)

    def drag(self, x0, y0, x1, y1, steps=8, button="left", buttons=1, modifiers=0):
        self.mouse("mouseMoved", x0, y0)
        self.mouse("mousePressed", x0, y0, button=button, buttons=buttons, clickCount=1, modifiers=modifiers)
        for i in range(1, steps + 1):
            self.mouse("mouseMoved", x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, button=button, buttons=buttons, modifiers=modifiers)
        self.mouse("mouseReleased", x1, y1, button=button, clickCount=1, modifiers=modifiers)

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def key_down(self, code):
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key=KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code),
                    code=code, windowsVirtualKeyCode=VK[code])

    def key_up(self, code):
        self.p.call("Input.dispatchKeyEvent", type="keyUp", key=KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code),
                    code=code, windowsVirtualKeyCode=VK[code])

    def press(self, code, hold=0.0):
        self.key_down(code)
        if hold:
            time.sleep(hold)
        self.key_up(code)

    def touch(self, kind, pts):
        self.p.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])
        if kind == "touchMove":
            time.sleep(0.03)   # a human pace: Chrome reads an instant swipe as a fling and swallows the tap that follows one

    def lift(self):
        time.sleep(0.25)       # rest before lifting, so the gesture ends without speed
        self.touch("touchEnd", [])

    def settle(self):
        self.p.wait("!%s.CV.goal && !%s.CV.raf" % (L, L), 10)
        time.sleep(0.08)

    def shot(self, name, clip="#stage"):
        self.p.shot(os.path.join(OUT, name), clip)
        print("      wrote out/camera/" + name)


def cam(d):
    return d.js("const c = %s.cam; return { yaw: c.yaw, pitch: c.pitch, dist: c.dist, target: c.target.slice() };" % L)


def eye(d):
    return d.js("const b = %s.basis(); return { pos: b.pos, f: b.f, right: b.right };" % L)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def norm(a):
    return dot(a, a) ** 0.5


def desktop(d):
    d.js("%s.S.q.aa = 2; %s.resetCam(); %s.touch(); window.scrollTo(0, 0);" % (L, L, L))
    d.settle()
    cx, cy = d.at("#view")

    # ----- the wheel, as a real mouse sends it
    d.mouse("mouseMoved", cx, cy)
    d.js("window.__tr = []; window.__ev = []; document.getElementById('view').addEventListener('wheel', e => window.__ev.push([e.deltaY, e.deltaMode, e.defaultPrevented]));"
         "const t0 = performance.now(); const f = () => { window.__tr.push([performance.now() - t0, %s.cam.dist]); if (performance.now() - t0 < 1500) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    y_before = d.js("return window.scrollY;")
    for _ in range(5):
        d.wheel(cx, cy, 100)
        time.sleep(0.06)
    time.sleep(1.6)
    tr, ev = d.js("return window.__tr;"), d.js("return window.__ev;")
    dist = cam(d)["dist"]
    ok("five real wheel notches (deltaY %s, mode %s) zoom out by 1.12^5" % (ev[0][0], ev[0][1]), abs(dist / 5.2 - 1.12 ** 5) < 1e-9, dist / 5.2)
    ok("the page itself did not scroll", d.js("return window.scrollY;") == y_before)
    steps = [(b[1] - a[1]) / (5.2 * (1.12 ** 5 - 1)) for a, b in zip(tr, tr[1:])]
    moving = [s for s in steps if s > 1e-6]
    ok("the zoom is spread over many frames, the largest single step being a small share of the whole",
       len(moving) >= 15 and max(steps) < 0.12 and min(steps) >= 0, "%d moving frames, largest step %.1f%% of the whole change" % (len(moving), 100 * max(steps)))
    gaps = [b[0] - a[0] for a, b in zip(tr, tr[1:])]
    print("      frame gaps while zooming: median %.1f ms, longest %.1f ms" % (sorted(gaps)[len(gaps) // 2], max(gaps)))
    d.js("%s.resetCam(); %s.touch();" % (L, L))

    # ----- a real drag, which leaves the stage on the way (pointer capture keeps it)
    c0 = cam(d)
    b = d.box("#view")
    d.drag(cx, cy, b[0] + b[2] + 150, cy + 40, steps=10)
    c1 = cam(d)
    want = c0["yaw"] - (b[0] + b[2] + 150 - cx) * 0.008
    ok("a real drag turns the camera and keeps turning outside the stage", abs(c1["yaw"] - want) < 1e-9 and abs(c1["pitch"] - (c0["pitch"] + 40 * 0.008)) < 1e-9, (c1["yaw"], want))
    ok("the canvas took the keyboard focus on the press", d.js("return document.activeElement.id;") == "view")
    d.mouse("mouseMoved", cx + 80, cy)
    ok("moving the mouse with no button down does nothing", cam(d)["yaw"] == c1["yaw"])
    t0 = cam(d)["target"]
    d.drag(cx, cy, cx + 60, cy, modifiers=8)
    ok("shift-drag slides", norm(sub(cam(d)["target"], t0)) > 0.05 and cam(d)["yaw"] == c1["yaw"])
    t0 = cam(d)["target"]
    d.drag(cx, cy, cx, cy + 60, button="right", buttons=2)
    ok("right-button drag slides, and no context menu handler complains", norm(sub(cam(d)["target"], t0)) > 0.05)

    # ----- real keys on the focused canvas
    d.js("%s.resetCam(); %s.touch();" % (L, L))
    y0 = cam(d)["yaw"]
    d.press("ArrowLeft", 0.4)
    d.settle()
    ok("holding the left arrow turns the arcball smoothly", -0.75 < cam(d)["yaw"] - y0 < -0.3, cam(d)["yaw"] - y0)

    # ----- the camera switch with a real click, then flying with real keys
    e0 = eye(d)
    d.click("#camFly")
    time.sleep(0.15)
    e1 = eye(d)
    ok("a real click on Fly switches the mode without moving the view", d.js("return %s.S.view.fly;" % L) is True and norm(sub(e0["pos"], e1["pos"])) < 1e-12 and norm(sub(e0["f"], e1["f"])) < 1e-12)
    ok("and hands the keyboard to the canvas", d.js("return document.activeElement.id;") == "view")
    d.shot("40-real-fly.png")
    y_before = d.js("return window.scrollY;")
    d.press("KeyW", 0.6)
    d.settle()
    e2 = eye(d)
    along = dot(sub(e2["pos"], e1["pos"]), e1["f"])
    ok("holding W for 0.6 s flies forward about 0.6 units at speed 1", 0.4 < along < 0.85, along)
    d.press("Space", 0.3)
    d.settle()
    e3 = eye(d)
    ok("Space rises and does not scroll the page", e3["pos"][2] - e2["pos"][2] > 0.12 and d.js("return window.scrollY;") == y_before, e3["pos"][2] - e2["pos"][2])
    d.press("ShiftLeft", 0.3)
    d.settle()
    ok("Shift sinks", eye(d)["pos"][2] - e3["pos"][2] < -0.12, eye(d)["pos"][2] - e3["pos"][2])
    before = eye(d)
    d.key_down("KeyD"); d.key_down("KeyW")
    time.sleep(0.4)
    d.key_up("KeyD"); d.key_up("KeyW")
    d.settle()
    e4 = eye(d)
    mv = sub(e4["pos"], before["pos"])
    time.sleep(0.2)
    ok("two keys at once move diagonally and everything stops on release",
       dot(mv, before["f"]) > 0.15 and dot(mv, before["right"]) > 0.15 and d.js("return %s.CV.keys.size;" % L) == 0 and norm(sub(eye(d)["pos"], e4["pos"])) == 0, mv)
    d.wheel(cx, cy, -100)
    time.sleep(0.2)
    ok("a real wheel notch upward makes flying 12% faster", abs(d.js("return %s.S.view.speed;" % L) - 1.12) < 1e-9, d.js("return %s.S.view.speed;" % L))
    d.wheel(cx, cy, 100)
    e5 = eye(d)
    d.drag(cx, cy, cx + 100, cy + 30)
    e6 = eye(d)
    ok("a real drag looks around from a fixed eye, to the right and down", norm(sub(e6["pos"], e5["pos"])) < 1e-9 and dot(e6["f"], e5["right"]) > 0.2 and e6["f"][2] < e5["f"][2])
    d.press("KeyF")
    time.sleep(0.15)
    e7 = eye(d)
    ok("F switches back to the arcball without moving the view", d.js("return %s.S.view.fly;" % L) is False and norm(sub(e7["pos"], e6["pos"])) < 1e-9 and norm(sub(e7["f"], e6["f"])) < 1e-12)

    # ----- the zoom slider and its limit boxes with a real mouse and keyboard
    d.js("%s.resetCam(); %s.touch();" % (L, L))
    rb = d.box("#camRail")
    rx = rb[0] + rb[2] / 2
    d.drag(rx, rb[1] + rb[3] * 0.25, rx, rb[1] + rb[3] * 0.75, steps=12)
    d.settle()
    want = 0.005 * (60 / 0.005) ** 0.75
    ok("dragging the slider thumb zooms to where it is dropped", abs(cam(d)["dist"] / want - 1) < 1e-6, (cam(d)["dist"], want))
    ok("the rail took the focus, so its arrow keys work next", d.js("return document.activeElement.id;") == "camRail")
    d.press("ArrowUp")
    d.settle()
    ok("arrow up on the focused rail moves in by 2% of the rail", abs(cam(d)["dist"] / (0.005 * (60 / 0.005) ** 0.73) - 1) < 1e-6, cam(d)["dist"])
    d.click("#camFar", count=3)
    d.p.call("Input.insertText", text="200")
    ok("typing in the far box changes nothing yet", d.js("return %s.S.view.zmax;" % L) == 60)
    d.press("Tab")
    ok("leaving the box with Tab commits the far limit", d.js("return %s.S.view.zmax;" % L) == 200 and d.js("return document.getElementById('camFar').value;") == "200")
    d.click("#camNear", count=3)
    d.p.call("Input.insertText", text="abc")
    d.press("Enter")
    ok("nonsense then Enter: the old near limit is back and the box is flagged",
       d.js("const e = document.getElementById('camNear'); return [e.value, e.getAttribute('aria-invalid'), %s.S.view.zmin];" % L) == ["0.005", "true", 0.005])
    d.shot("41-real-invalid-box.png")
    d.click("#camNear", count=3)
    d.p.call("Input.insertText", text="0,5")
    d.press("Enter")
    ok("0,5 then Enter sets the near limit to 0.5", d.js("return %s.S.view.zmin;" % L) == 0.5)
    for _ in range(40):
        d.wheel(cx, cy, -300)
    d.settle()
    ok("the wheel then stops at the new near limit", cam(d)["dist"] == 0.5, cam(d)["dist"])
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch();" % (L, L, L))

    # ----- a real double-click
    d.p.wait(L + ".idle()", 60)
    px, py = d.at("#view", 0.55, 0.5)
    hit = d.js("const r = document.getElementById('view').getBoundingClientRect(); return %s.pick(%f - r.left, %f - r.top);" % (L, px, py))
    d.click("#view", count=2, fx=0.55, fy=0.5)
    d.settle()
    c = cam(d)
    ok("a real double-click moves in on the clicked spot (once, not twice)", hit is not None and norm(sub(c["target"], hit)) < 0.02 and 2.2 < c["dist"] < 3.0, (hit, c))

    # ----- focus rings, reached with Tab
    d.js("%s.resetCam(); %s.touch(); document.getElementById('view').focus();" % (L, L))
    seen = []
    for _ in range(9):
        d.press("Tab")
        seen.append(d.js("const e = document.activeElement, cs = getComputedStyle(e); return [e.id, e.matches(':focus-visible'), cs.outlineStyle, cs.outlineWidth].join(' ');"))
        if seen[-1].startswith("camRail"):
            d.shot("42-ring-rail.png")
        if seen[-1].startswith("camFly"):
            d.shot("43-ring-fly.png")
    mine = [s for s in seen if s.startswith("cam")]
    ok("Tab reaches Arcball, Fly, near box, slider, far box, each with a 2 px ring",
       [s.split(" ")[0] for s in mine] == ["camArc", "camFly", "camNear", "camRail", "camFar"] and all(s.endswith("true solid 2px") for s in mine), seen)


def touch_screen(d, page):
    page.call("Emulation.setDeviceMetricsOverride", width=820, height=1100, deviceScaleFactor=1, mobile=True)
    page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    d.load(PAGE)
    d.js("%s.S.q.aa = 2; %s.resetCam(); %s.touch(); document.getElementById('stage').scrollIntoView({block: 'center'});" % (L, L, L))
    time.sleep(0.3)
    ok("tablet emulation: coarse pointer, and the hint speaks of fingers", d.js("return matchMedia('(pointer: coarse)').matches;") and d.js("return document.querySelector('.hint').textContent;").startswith("Drag to turn. Pinch to zoom."),
       d.js("return document.querySelector('.hint').textContent;"))
    sizes = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; }; return [q('#camFly'), q('#camRail'), q('#camNear'), q('#camThumb')];")
    ok("finger-sized targets: mode buttons at least 30 px tall, rail 44 px wide", sizes[0][1] >= 30 and sizes[1][0] >= 44, sizes)
    cx, cy = d.at("#view")
    c0 = cam(d)
    d.touch("touchStart", [(cx, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx + 12 * i, cy + 4 * i)])
    d.lift()
    c1 = cam(d)
    ok("one finger turns", abs(c1["yaw"] - (c0["yaw"] - 60 * 0.008)) < 1e-9 and abs(c1["pitch"] - (c0["pitch"] + 20 * 0.008)) < 1e-9, (c0, c1))
    d.touch("touchStart", [(cx - 50, cy), (cx + 50, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 50 - 10 * i, cy), (cx + 50 + 10 * i, cy)])
    time.sleep(0.1)   # touch moves are delivered with the next frame
    c2 = cam(d)
    ok("two fingers spread to twice the gap: the distance halves, at once", abs(c2["dist"] / c1["dist"] - 0.5) < 1e-6, c2["dist"] / c1["dist"])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 100, cy + 10 * i), (cx + 100, cy + 10 * i)])
    d.lift()
    c3 = cam(d)
    ok("two fingers moved together slide the scene and leave the zoom alone", norm(sub(c3["target"], c2["target"])) > 0.03 and abs(c3["dist"] / c2["dist"] - 1) < 0.02, (c3["dist"] / c2["dist"], norm(sub(c3["target"], c2["target"]))))
    ok("no finger is left registered", d.js("return %s.CV.ptr.size;" % L) == 0)
    d.js("%s.resetCam(); %s.touch();" % (L, L))
    d.p.wait(L + ".idle()", 60)
    px, py = d.at("#view", 0.55, 0.5)
    for _ in range(2):
        d.touch("touchStart", [(px, py)])
        d.touch("touchEnd", [])
        time.sleep(0.09)
    d.settle()
    c4 = cam(d)
    ok("a double-tap moves in once (55% of the distance)", 2.2 < c4["dist"] < 3.0, c4["dist"])
    rb = d.box("#camRail")
    rx = rb[0] + rb[2] / 2
    d.touch("touchStart", [(rx, rb[1] + rb[3] * 0.3)])
    for i in range(1, 6):
        d.touch("touchMove", [(rx, rb[1] + rb[3] * (0.3 + 0.08 * i))])
    d.lift()
    d.settle()
    want = 0.005 * (60 / 0.005) ** 0.7
    ok("a finger drags the zoom slider", abs(cam(d)["dist"] / want - 1) < 1e-6, (cam(d)["dist"], want))
    d.touch("touchStart", [d.at("#camFly")])
    d.touch("touchEnd", [])
    time.sleep(0.3)
    ok("a tap on Fly switches the mode; the hint explains flying with fingers", d.js("return %s.S.view.fly;" % L) is True and d.js("return document.querySelector('.hint').textContent;").startswith("Drag to look around. Pinch to move"))
    e0 = eye(d)
    d.touch("touchStart", [(cx - 50, cy), (cx + 50, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 50 - 10 * i, cy), (cx + 50 + 10 * i, cy)])
    d.lift()
    e1 = eye(d)
    fwd = dot(sub(e1["pos"], e0["pos"]), e0["f"])
    ok("when flying, spreading two fingers to twice the gap moves forward 1.5 ln 2 = 1.04 units at speed 1", abs(fwd - 1.0397) < 0.01, fwd)
    d.p.wait(L + ".idle()", 60)
    d.shot("44-tablet-fly.png")

    page.call("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)
    d.load(PAGE)
    d.js("%s.S.q.aa = 2; %s.touch(); document.getElementById('stage').scrollIntoView({block: 'center'});" % (L, L))
    d.p.wait(L + ".idle()", 60)
    time.sleep(0.3)
    fit = d.js("const st = document.getElementById('stage').getBoundingClientRect(), z = document.getElementById('camZoom').getBoundingClientRect(), m = document.getElementById('camMode').getBoundingClientRect(),"
               "b = document.querySelector('.stage-btns').getBoundingClientRect(); return { over: document.documentElement.scrollWidth - document.documentElement.clientWidth,"
               "inside: z.right <= st.right && m.right <= st.right && m.left >= st.left, clearOfButtons: z.bottom <= b.top, rail: document.getElementById('camRail').getBoundingClientRect().height };")
    ok("phone, 375 px: overlays inside the stage, clear of the stage buttons, no sideways scrolling, rail at least 80 px long",
       fit["over"] <= 0 and fit["inside"] and fit["clearOfButtons"] and fit["rail"] >= 80, fit)
    d.shot("45-phone-touch.png")
    fs = d.js("const e = document.getElementById('camNear'); e.value = '0.00001'; return [parseFloat(getComputedStyle(e).fontSize), e.scrollWidth <= e.clientWidth];")
    ok("phone: the limit boxes use 16 px text (no page zoom on focus) and still fit their longest value", fs == [16, True], fs)


def main():
    global PAGE
    PAGE = sys.argv[1] if len(sys.argv) > 1 else "dist/camera-test.html"
    os.makedirs(OUT, exist_ok=True)
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("No Chrome or Edge found.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="camreal-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get("type") == "page"]
                if pages:
                    target = pages[0]["webSocketDebuggerUrl"]; break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            sys.exit("Chrome did not start its debugging port.")
        page = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            page.call(m)
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)   # the window counts as focused, as a real one would
        d = Drive(page)
        d.load(PAGE)
        desktop(d)
        touch_screen(d, page)
        page.js("return 0;")
        ok("no console errors or uncaught exceptions", not page.problems, page.problems[:10])
        try:
            page.call("Browser.close")
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    bad = results.count(False)
    print("%d passed, %d failed" % (results.count(True), bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
