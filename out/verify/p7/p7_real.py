"""p7: the camera switch, driven with real input on dist/preview.html.  python p7_real.py desktop|phone"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

L = "window.squaringLab"
PAGE = "dist/preview.html"
VK = {"Tab": 9, "Enter": 13, "Escape": 27, "Space": 32, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40,
      "KeyW": 87, "KeyA": 65, "KeyS": 83, "KeyD": 68, "KeyQ": 81, "KeyE": 69, "KeyF": 70, "ShiftLeft": 16}
KEYNAME = {"Space": " ", "ShiftLeft": "Shift"}
results = []
TAG = "d"


def ok(name, cond, detail=""):
    results.append(bool(cond))
    print(("pass  " if cond else "FAIL  ") + name + ("" if detail == "" else "  :: " + str(detail)), flush=True)


def info(name, detail):
    print("info  " + name + "  :: " + str(detail), flush=True)


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, rel):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 60)
        if not self.p.wait(L + " && " + L + ".idle()", 240):
            raise RuntimeError("the page never finished drawing")
        time.sleep(0.3)

    def idle(self, t=120):
        return self.p.wait(L + ".idle()", t)

    def stage(self):
        self.js("document.getElementById('stage').scrollIntoView({block: 'center'});")
        time.sleep(0.15)

    def box(self, sel):
        return self.js("const b = document.querySelector(%s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))

    def at(self, sel, fx=0.5, fy=0.5):
        b = self.box(sel)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, fx=0.5, fy=0.5, scroll=False):
        if scroll:
            self.js("const e = document.querySelector(%s); let p = e; while (p) { if (p.tagName === 'DETAILS') p.open = true; p = p.parentElement; } e.scrollIntoView({block: 'center'});" % json.dumps(sel))
            time.sleep(0.2)
        x, y = self.at(sel, fx, fy)
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n)
        time.sleep(0.15)

    def drag(self, x0, y0, x1, y1, steps=8, button="left", buttons=1, modifiers=0):
        self.mouse("mouseMoved", x0, y0)
        self.mouse("mousePressed", x0, y0, button=button, buttons=buttons, clickCount=1, modifiers=modifiers)
        for i in range(1, steps + 1):
            self.mouse("mouseMoved", x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, button=button, buttons=buttons, modifiers=modifiers)
        self.mouse("mouseReleased", x1, y1, button=button, clickCount=1, modifiers=modifiers)

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def _k(self, code):
        return KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code)

    def key_down(self, code, text=None):
        kw = dict(type="keyDown" if text else "rawKeyDown", key=self._k(code), code=code, windowsVirtualKeyCode=VK[code])
        if text:
            kw["text"] = text
        self.p.call("Input.dispatchKeyEvent", **kw)

    def key_up(self, code):
        self.p.call("Input.dispatchKeyEvent", type="keyUp", key=self._k(code), code=code, windowsVirtualKeyCode=VK[code])

    def press(self, code, hold=0.0, text=None):
        self.key_down(code, text)
        if hold:
            time.sleep(hold)
        self.key_up(code)

    def touch(self, kind, pts):
        self.p.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])
        if kind == "touchMove":
            time.sleep(0.03)

    def lift(self):
        time.sleep(0.25)
        self.touch("touchEnd", [])

    def tap(self, sel):
        self.touch("touchStart", [self.at(sel)])
        self.touch("touchEnd", [])
        time.sleep(0.4)

    def settle(self):
        self.p.wait("!%s.CV.goal && !%s.CV.raf" % (L, L), 15)
        time.sleep(0.1)

    def shot(self, name, clip="#stage", wait=True):
        if wait:
            self.idle(150)
        self.p.shot(os.path.join(HERE, name), clip)
        print("      wrote out/verify/p7/" + name, flush=True)


ST = ("const L = window.squaringLab, q = s => document.querySelector(s), cb = document.getElementById('viewFly'), sp = document.getElementById('viewSpeedNum');"
      "return { fly: L.S.view.fly, flat: !!L.S.flat, arc: q('#camArc').getAttribute('aria-pressed'), flyb: q('#camFly').getAttribute('aria-pressed'),"
      "hint: q('.hint').textContent, cb: cb ? cb.checked : 'missing', cbDisabled: cb ? cb.disabled : null, cbVisible: cb ? cb.getClientRects().length > 0 : null, kind: q('#stage').dataset.cam, modeHidden: q('#camMode').hidden,"
      "speed: L.S.view.speed, speedBox: sp ? sp.value : 'missing', endA: q('#camEndA').textContent, endB: q('#camEndB').textContent, val: q('#camVal').textContent, mode: L.S.mode,"
      "focus: document.activeElement.id || document.activeElement.tagName, keys: [...L.CV.keys] };")


def st(d):
    return d.js(ST)


def cam(d):
    return d.js("const c = %s.cam; return { yaw: c.yaw, pitch: c.pitch, dist: c.dist, target: c.target.slice() };" % L)


def eye(d):
    return d.js("const b = %s.basis(); return { pos: b.pos, f: b.f, right: b.right, up: b.up };" % L)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def norm(a):
    return dot(a, a) ** 0.5


def same_eye(a, b, tol=1e-9):
    return norm(sub(a["pos"], b["pos"])) < tol and norm(sub(a["f"], b["f"])) < tol


def consistent(s, fly):
    return s["fly"] is fly and s["arc"] == str(not fly).lower() and s["flyb"] == str(fly).lower() and s["cb"] is fly and s["kind"] == ("fly" if fly else "arc")


def imgdiff(a, b):
    try:
        from PIL import Image, ImageChops
        A, B = Image.open(os.path.join(HERE, a)).convert("RGB"), Image.open(os.path.join(HERE, b)).convert("RGB")
        if A.size != B.size:
            return "sizes differ %s %s" % (A.size, B.size)
        h = ImageChops.difference(A, B).convert("L").histogram()
        n = A.size[0] * A.size[1]
        return {"pixels_over_24": sum(h[25:]) / n, "mean": sum(i * c for i, c in enumerate(h)) / n}
    except Exception as e:
        return "no diff: %s" % e


def hold_move(d, code, hold):
    """Hold a key; return movement vector and the held time as the page saw it, plus frame statistics."""
    d.js("window.__k = {}; window.__fr = []; if (!window.__kl) { window.__kl = 1; window.addEventListener('keydown', e => { window.__k.d = performance.now(); }, true);"
         "window.addEventListener('keyup', e => { window.__k.u = performance.now(); }, true); }"
         "const t0 = performance.now(); const f = () => { window.__fr.push(performance.now()); if (performance.now() - t0 < %d) requestAnimationFrame(f); }; requestAnimationFrame(f);" % int(hold * 1000 + 1500))
    e0 = eye(d)
    d.key_down(code)
    time.sleep(hold)
    d.key_up(code)
    d.settle()
    time.sleep(0.2)
    e1 = eye(d)
    k = d.js("const fr = window.__fr, g = fr.slice(1).map((t, i) => t - fr[i]); g.sort((a, b) => a - b); return { held: (window.__k.u - window.__k.d) / 1000, frames: fr.length, med: g[g.length >> 1], max: g[g.length - 1] };")
    return sub(e1["pos"], e0["pos"]), e0, k


def desktop(d, page):
    d.js("window.scrollTo(0, 0);")
    cx, cy = d.at("#view")
    s = st(d)
    info("start state", s)
    ok("at load: Arcball is shown active, Fly not, checkbox clear, arcball hint", consistent(s, False) and s["hint"].startswith("Drag to turn."), s)
    b = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };"
             "const cs = s => { const c = getComputedStyle(document.querySelector(s)); return [c.backgroundColor, c.color, c.fontWeight]; };"
             "return { stage: q('#stage'), mode: q('#camMode'), arc: q('#camArc'), fly: q('#camFly'), arcStyle: cs('#camArc'), flyStyle: cs('#camFly') };")
    info("switch geometry and styles (arcball active)", b)
    ok("the two buttons look different when one is active", b["arcStyle"] != b["flyStyle"], b)
    d.shot("%s-01-arcball.png" % TAG)

    # ---- switch to fly with a real click
    e0 = eye(d)
    d.click("#camFly")
    s = st(d); e1 = eye(d)
    ok("real click on Fly: mode, both buttons, checkbox and stage agree; view did not move", consistent(s, True) and same_eye(e0, e1), s)
    ok("fly hint text", s["hint"].startswith("Drag to look around. W A S D"), s["hint"])
    ok("keyboard goes to the picture after the click", s["focus"] == "view", s["focus"])
    d.shot("%s-02-fly.png" % TAG)
    info("picture change arcball -> fly (should be only overlays)", imgdiff("%s-01-arcball.png" % TAG, "%s-02-fly.png" % TAG))

    # ---- mouse look
    d.drag(cx, cy, cx + 100, cy + 30)
    e2 = eye(d)
    ok("drag looks around from a fixed eye (right and down)", norm(sub(e2["pos"], e1["pos"])) < 1e-9 and dot(e2["f"], e1["right"]) > 0.2 and e2["f"][2] < e1["f"][2], (e2["f"], e1["f"]))
    d.drag(cx, cy, cx - 100, cy - 30)

    # ---- keys
    y0 = d.js("return window.scrollY;")
    want = {"KeyW": ("f", 1), "KeyS": ("f", -1), "KeyA": ("right", -1), "KeyD": ("right", 1), "ArrowUp": ("f", 1), "ArrowDown": ("f", -1),
            "ArrowLeft": ("right", -1), "ArrowRight": ("right", 1), "KeyE": ("z", 1), "KeyQ": ("z", -1), "Space": ("z", 1), "ShiftLeft": ("z", -1)}
    rates = {}
    for code, (ax, sign) in want.items():
        mv, e, k = hold_move(d, code, 0.5)
        comp = mv[2] if ax == "z" else dot(mv, e[ax])
        rates[code] = round(comp / max(k["held"], 1e-6), 3)
        ok("%s moves %s%s" % (code, "+" if sign > 0 else "-", ax), sign * comp > 0.2 and abs(norm(mv) - abs(comp)) < 0.05, "moved %.3f along, |mv| %.3f, held %.3f s, frames med %.0f max %.0f ms" % (comp, norm(mv), k["held"], k["med"], k["max"]))
    info("units per second of key held, by key (speed is %s)" % st(d)["speed"], rates)
    ok("no key scrolled the page", d.js("return window.scrollY;") == y0)

    # ---- frame-rate independence: the same hold with the CPU throttled
    mv, e, k = hold_move(d, "KeyW", 1.0)
    r1 = dot(mv, e["f"]) / k["held"]
    page.call("Emulation.setCPUThrottlingRate", rate=6)
    mv, e, k2 = hold_move(d, "KeyS", 1.0)
    r2 = -dot(mv, e["f"]) / k2["held"]
    page.call("Emulation.setCPUThrottlingRate", rate=1)
    ok("frame-rate independent: units per second the same at normal and throttled frame rates", abs(r1 - r2) < 0.15 * max(r1, r2) and abs(r1 - st(d)["speed"]) < 0.2,
       "normal %.3f u/s (frames med %.0f max %.0f ms), throttled x6 %.3f u/s (frames med %.0f max %.0f ms)" % (r1, k["med"], k["max"], r2, k2["med"], k2["max"]))

    # ---- speed: wheel, the stage slider, the View dial
    sp0 = st(d)["speed"]
    d.mouse("mouseMoved", cx, cy)
    d.wheel(cx, cy, -100); time.sleep(0.5)
    s = st(d)
    ok("wheel up makes flying 12% faster, View dial follows, eye does not zoom", abs(s["speed"] / sp0 - 1.12) < 1e-6 and abs(float(s["speedBox"]) - s["speed"]) < 0.006, s)
    ok("stage slider reads fast/slow and shows the speed", s["endA"] == "fast" and s["endB"] == "slow" and abs(float(s["val"]) - s["speed"]) < 0.01, (s["endA"], s["endB"], s["val"]))
    d.wheel(cx, cy, 100); time.sleep(0.4)
    d.click("#viewSpeedNum", count=3, scroll=True)
    page.call("Input.insertText", text="2.5")
    d.press("Enter"); time.sleep(0.3)
    s = st(d)
    ok("typing 2.5 in the Fly speed box sets the speed and the stage slider", s["speed"] == 2.5 and s["val"] in ("2.5", "2.50"), (s["speed"], s["val"]))
    d.stage()
    d.shot("%s-03-fly-speed.png" % TAG, wait=False)
    d.click("#viewSpeedNum", count=3, scroll=True)
    page.call("Input.insertText", text="1")
    d.press("Enter"); time.sleep(0.2)

    # ---- typing in boxes never moves the camera
    d.stage()
    e0 = eye(d)
    for sel in ("#eq", "#powNum", "#viewSpeedNum"):
        d.click(sel, scroll=True)
        f = st(d)["focus"]
        for code, text in (("KeyW", "w"), ("KeyA", "a"), ("KeyS", "s"), ("KeyD", "d"), ("KeyQ", "q"), ("KeyE", "e"), ("Space", " "), ("KeyF", "f")):
            d.key_down(code, text); time.sleep(0.12); d.key_up(code)
        if sel == "#eq":
            for code in ("ArrowLeft", "ArrowRight"):
                d.press(code, 0.1)
        time.sleep(0.3)
        s = st(d)
        val = d.js("return document.querySelector(%s).value;" % json.dumps(sel))
        ok("typing w a s d q e space f in %s (focus %s) leaves the camera and the mode alone" % (sel, f), same_eye(e0, eye(d)) and s["fly"] is True and not s["keys"], (val, s["keys"], s["fly"]))
        d.press("Escape"); time.sleep(0.15)
    eqv = d.js("return [document.getElementById('eq').value, document.getElementById('powNum').value, document.getElementById('viewSpeedNum').value];")
    info("box contents after Escape", eqv)
    if eqv[0] != "z^n + c":
        d.js("const e = document.getElementById('eq'); e.value = 'z^n + c'; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true}));")
    d.js("document.activeElement.blur();")
    d.idle(120)
    ok("after the typing test the view is still where it was", same_eye(e0, eye(d)), (e0["pos"], eye(d)["pos"]))

    # ---- a held key, then focus moves to a box: no sticking
    d.stage()
    d.click("#view", fx=0.3, fy=0.3)
    d.key_down("KeyW"); time.sleep(0.3)
    d.click("#eq", scroll=True)
    time.sleep(0.6)
    a = eye(d); time.sleep(0.5); bb = eye(d)
    ok("W held, then a click into the equation box: movement stops", norm(sub(a["pos"], bb["pos"])) == 0 and not st(d)["keys"], (norm(sub(a["pos"], bb["pos"])), st(d)["keys"]))
    d.key_up("KeyW")
    d.js("document.activeElement.blur();")

    # ---- a held key, then the window loses focus: no sticking
    d.stage()
    d.click("#view", fx=0.3, fy=0.3)
    d.key_down("KeyW"); time.sleep(0.3)
    real = "real"
    try:
        page.call("Emulation.setFocusEmulationEnabled", enabled=False)
        t = page.call("Target.createTarget", url="about:blank")
        time.sleep(0.6)
        if d.js("return %s.CV.keys.size;" % L):
            real = "synthetic (a new tab did not blur the headless window)"
            d.js("window.dispatchEvent(new Event('blur'));")
        try:
            page.call("Target.closeTarget", targetId=t["targetId"])
        except Exception:
            pass
        page.call("Page.bringToFront")
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    except Exception as ex:
        real = "synthetic (%s)" % ex
        d.js("window.dispatchEvent(new Event('blur'));")
    time.sleep(0.7)
    a = eye(d); time.sleep(0.6); bb = eye(d)
    ok("W held, window loses focus (%s), key never released: movement stops" % real, norm(sub(a["pos"], bb["pos"])) == 0 and not st(d)["keys"], (norm(sub(a["pos"], bb["pos"])), st(d)["keys"]))
    d.key_up("KeyW")

    # ---- triad in fly mode
    d.stage()
    cx, cy = d.at("#view")
    d.drag(cx, cy, cx + 160, cy - 60)
    tri = d.js("const b = %s.basis(), d3 = (a, c) => a[0]*c[0] + a[1]*c[1] + a[2]*c[2]; return [[1,0,0],[0,1,0],[0,0,1]].map((v, i) => { const l = document.getElementById('ax' + i);"
               "return [Math.abs(+l.getAttribute('x2') - (36 + 23 * d3(v, b.right))) < 0.06, Math.abs(+l.getAttribute('y2') - (36 - 23 * d3(v, b.up))) < 0.06]; });" % L)
    ok("axes icon matches the fly camera after looking around", all(all(t) for t in tri), tri)
    d.shot("%s-04-fly-looked.png" % TAG)

    # ---- back to the arcball: no jump (looking at the set, then looking at empty space)
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    d.click("#view", fx=0.5, fy=0.5)
    d.press("KeyW", 0.8); d.settle()
    d.drag(cx, cy, cx + 60, cy + 40)
    e0 = eye(d); c0 = cam(d)
    d.shot("%s-05-before-arc.png" % TAG)
    d.click("#camArc")
    s = st(d); e1 = eye(d); c1 = cam(d)
    ok("click Arcball while looking at the set: eye and direction unchanged, everything agrees", consistent(s, False) and same_eye(e0, e1) and s["hint"].startswith("Drag to turn."), (s, c0, c1))
    d.shot("%s-06-after-arc.png" % TAG)
    info("picture change fly -> arcball, looking at the set", imgdiff("%s-05-before-arc.png" % TAG, "%s-06-after-arc.png" % TAG))
    info("arcball pivot after the switch", c1)
    y0 = c1["yaw"]
    d.drag(cx, cy, cx + 50, cy)
    c2 = cam(d)
    ok("the arcball then turns about a point in front (target unchanged by a drag)", abs(c2["yaw"] - (y0 - 0.4)) < 1e-9 and norm(sub(c2["target"], c1["target"])) < 1e-12, c2)
    d.press("KeyF"); time.sleep(0.2)
    s = st(d)
    ok("F key switches to fly and the buttons and checkbox follow", consistent(s, True), s)
    d.drag(cx, cy, cx + 500, cy - 250, steps=12)   # look away into empty space
    e0 = eye(d)
    d.press("KeyF"); time.sleep(0.2)
    e1 = eye(d); s = st(d)
    ok("F back to arcball while looking at empty space: no jump", consistent(s, False) and same_eye(e0, e1), (cam(d), s))

    # ---- Reset view in both modes
    d.click("#reset"); d.settle()
    c = cam(d)
    ok("Reset view in arcball mode restores the start view", abs(c["yaw"] + 1) < 1e-9 and abs(c["dist"] - 5.2) < 1e-9 and norm(sub(c["target"], [-0.6, 0, 0])) < 1e-9, c)
    d.click("#camFly")
    d.press("KeyW", 0.6); d.settle()
    d.drag(cx, cy, cx + 200, cy + 60)
    d.click("#reset"); d.settle()
    c = cam(d); s = st(d)
    ok("Reset view in fly mode restores the start view and stays in fly mode", abs(c["yaw"] + 1) < 1e-9 and abs(c["dist"] - 5.2) < 1e-9 and norm(sub(c["target"], [-0.6, 0, 0])) < 1e-9 and consistent(s, True), (c, s))
    mv, e, k = hold_move(d, "KeyW", 0.5)
    ok("after clicking Reset view in fly mode, W still moves without clicking the picture again", dot(mv, e["f"]) > 0.2, "moved %.3f; focus is on %s" % (dot(mv, e["f"]), st(d)["focus"]))
    d.shot("%s-07-fly-reset.png" % TAG)

    # ---- zoomed in close, switch to fly, then Reset view: is the speed still usable?
    d.click("#camArc")
    d.js("%s.resetCam(); %s.cam.dist = 0.05; %s.cam.target = [-0.75, 0.1, 0]; %s.touch();" % (L, L, L, L)); d.settle()
    d.click("#camFly")
    s = st(d)
    info("entering fly at distance 0.05: speed becomes", (s["speed"], s["speedBox"], s["val"]))
    d.click("#reset"); d.settle()
    d.click("#view", fx=0.3, fy=0.3)
    mv, e, k = hold_move(d, "KeyW", 1.0)
    s = st(d)
    ok("after Reset view from a close-up, one second of W moves a visible amount (at least 2% of the 5.2 distance)", norm(mv) > 0.1, "moved %.4f units in %.2f s at speed %s (view distance %.2f)" % (norm(mv), k["held"], s["speed"], cam(d)["dist"]))
    d.js("%s.S.view.speed = 1; %s.syncControls(); %s.viewChanged();" % (L, L, L))

    # ---- checkbox in the View section drives the buttons, and Reset this section
    d.js("%s.setCamMode(false); %s.resetCam(); %s.touch();" % (L, L, L)); d.settle()
    d.click("#viewFly", scroll=True)
    s = st(d)
    ok("ticking Fly camera in View switches the stage buttons", consistent(s, True), s)
    d.click("#viewFly", scroll=True)
    ok("clearing it switches back", consistent(st(d), False), st(d))
    d.click("#viewFly", scroll=True)
    d.click("#viewReset button", scroll=True)
    s = st(d)
    ok("Reset this section (View) returns to arcball, buttons and checkbox agree", consistent(s, False) and s["speed"] == 1, s)
    d.stage()
    d.shot("%s-08-view-section.png" % TAG, clip="#secView", wait=False)

    # ---- Julia and Kleinian
    for mode, name in (("j", "julia"), ("k", "klein")):
        d.stage()
        d.click("#camFly")
        d.click("#mode-" + mode, scroll=True)
        d.idle(150)
        d.stage()
        s = st(d); c = cam(d)
        ok("%s: still in fly mode after choosing the mode, everything agrees, fly hint" % name, s["mode"] == mode and consistent(s, True) and s["hint"].startswith("Drag to look around."), (s, c))
        d.click("#view", fx=0.3, fy=0.3)
        cx, cy = d.at("#view")
        mv, e, k = hold_move(d, "KeyW", 0.6)
        ok("%s: W flies forward" % name, dot(mv, e["f"]) > 0.2 * s["speed"], "moved %.3f at speed %s, dist %s" % (dot(mv, e["f"]), s["speed"], c["dist"]))
        e0 = eye(d)
        d.drag(cx, cy, cx + 80, cy + 20)
        ok("%s: drag looks around from a fixed eye" % name, norm(sub(eye(d)["pos"], e0["pos"])) < 1e-9 and norm(sub(eye(d)["f"], e0["f"])) > 0.1)
        d.shot("%s-09-fly-%s.png" % (TAG, name))
        e0 = eye(d)
        d.click("#camArc")
        ok("%s: back to arcball without a jump" % name, same_eye(e0, eye(d)) and consistent(st(d), False), cam(d))
        d.click("#reset"); d.settle()
    d.click("#mode-m", scroll=True)
    d.idle(150)

    # ---- the 2D view while flying
    d.stage()
    d.click("#camFly")
    d.click("#view", fx=0.3, fy=0.3)
    d.press("KeyW", 0.5); d.settle()
    c0 = cam(d)
    d.click("#flat", scroll=True)
    d.idle(150); d.stage()
    s = st(d)
    info("2D view turned on while flying", s)
    ok("2D view: the Arcball/Fly switch is hidden and the hint is the 2D one", s["modeHidden"] is True and s["kind"] == "flat" and s["hint"].startswith("Drag to slide the picture."), s)
    ok("2D view: the Fly camera checkbox is not left looking usable (hidden or disabled), since it does nothing here", (s["cbDisabled"] or not s["cbVisible"]), "checked %s, disabled %s, visible %s" % (s["cb"], s["cbDisabled"], s["cbVisible"]))
    d.click("#view", fx=0.3, fy=0.3)
    v0 = d.js("return [%s.S.v2.x, %s.S.v2.y, %s.S.v2.h];" % (L, L, L))
    d.press("KeyW", 0.4); d.press("KeyF"); d.settle()
    s2 = st(d)
    ok("2D view: W and F do nothing", d.js("return [%s.S.v2.x, %s.S.v2.y, %s.S.v2.h];" % (L, L, L)) == v0 and s2["fly"] is True, s2)
    d.shot("%s-10-flat-while-fly.png" % TAG)
    d.click("#viewFly", scroll=True)
    s3 = st(d)
    info("2D view: clicking the Fly camera checkbox gives", {k: s3[k] for k in ("fly", "cb", "kind", "hint", "modeHidden")})
    d.shot("%s-11-flat-view-section.png" % TAG, clip="#secView", wait=False)
    d.click("#viewFly", scroll=True)
    d.click("#flat", scroll=True)
    d.idle(150); d.stage()
    s = st(d); c1 = cam(d)
    ok("leaving the 2D view: fly mode is back with buttons, checkbox and hint agreeing, camera where it was",
       consistent(s, True) and s["modeHidden"] is False and s["hint"].startswith("Drag to look around.") and abs(c1["dist"] - c0["dist"]) < 1e-9 and norm(sub(c1["target"], c0["target"])) < 1e-9, (s, c0, c1))
    d.shot("%s-12-fly-after-flat.png" % TAG)


def phone(d, page):
    page.call("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)
    page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    d.load(PAGE)
    d.stage()
    s = st(d)
    ok("phone: arcball at load, touch hint", consistent(s, False) and s["hint"].startswith("Drag to turn. Pinch to zoom."), s)
    fit = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };"
               "const h = document.querySelector('.hint'); return { stage: q('#stage'), mode: q('#camMode'), arc: q('#camArc'), fly: q('#camFly'), hint: q('.hint'), btns: q('.stage-btns'), zoom: q('#camZoom'), triad: q('#triad'),"
               "over: document.documentElement.scrollWidth - document.documentElement.clientWidth, hintClipped: h.scrollWidth > h.clientWidth + 1 || h.scrollHeight > h.clientHeight + 1 };")
    info("phone geometry (arcball)", fit)
    ok("phone: buttons at least 30 px tall, inside the stage, no sideways scroll", fit["fly"][3] >= 30 and fit["over"] <= 0 and fit["mode"][0] >= fit["stage"][0] and fit["mode"][0] + fit["mode"][2] <= fit["stage"][0] + fit["stage"][2], fit)
    d.shot("%s-01-arcball.png" % TAG)
    cx, cy = d.at("#view")
    c0 = cam(d)
    d.touch("touchStart", [(cx, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx + 12 * i, cy + 4 * i)])
    d.lift()
    c1 = cam(d)
    ok("phone arcball: one finger turns", abs(c1["yaw"] - (c0["yaw"] - 60 * 0.008)) < 1e-6 and norm(sub(c1["target"], c0["target"])) < 1e-9, (c0, c1))
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 - 8 * i, cy), (cx + 40 + 8 * i, cy)])
    d.lift()
    c2 = cam(d)
    ok("phone arcball: pinch out to twice the gap halves the distance", abs(c2["dist"] / c1["dist"] - 0.5) < 0.02, c2["dist"] / c1["dist"])
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()

    e0 = eye(d)
    d.tap("#camFly")
    s = st(d); e1 = eye(d)
    ok("phone: a tap on Fly switches, buttons and checkbox agree, no jump, touch fly hint", consistent(s, True) and same_eye(e0, e1) and s["hint"].startswith("Drag to look around. Pinch to move"), s)
    fit = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };"
               "const h = document.querySelector('.hint'); return { stage: q('#stage'), mode: q('#camMode'), hint: q('.hint'), btns: q('.stage-btns'), zoom: q('#camZoom'), triad: q('#triad'), hintClipped: h.scrollWidth > h.clientWidth + 1 || h.scrollHeight > h.clientHeight + 1 };")
    info("phone geometry (fly)", fit)
    d.shot("%s-02-fly.png" % TAG)
    d.touch("touchStart", [(cx, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx + 12 * i, cy + 4 * i)])
    d.lift()
    e2 = eye(d)
    ok("phone fly: one finger looks around from a fixed eye", norm(sub(e2["pos"], e1["pos"])) < 1e-9 and dot(e2["f"], e1["right"]) > 0.1, (e1["f"], e2["f"]))
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 - 8 * i, cy), (cx + 40 + 8 * i, cy)])
    d.lift()
    e3 = eye(d)
    fwd = dot(sub(e3["pos"], e2["pos"]), e2["f"])
    ok("phone fly: pinch out moves forward (about 1.04 units at speed 1)", abs(fwd - 1.04) < 0.08 * max(1, s["speed"]), (fwd, s["speed"]))
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 + 10 * i, cy), (cx + 40 + 10 * i, cy)])
    d.lift()
    e4 = eye(d)
    side = dot(sub(e4["pos"], e3["pos"]), e3["right"])
    ok("phone fly: two fingers dragged sideways move the camera sideways, direction unchanged", abs(side) > 0.02 and norm(sub(e4["f"], e3["f"])) < 1e-9, side)
    rb = d.box("#camRail")
    rx = rb[0] + rb[2] / 2
    sp0 = st(d)["speed"]
    d.touch("touchStart", [(rx, rb[1] + rb[3] * 0.5)])
    for i in range(1, 6):
        d.touch("touchMove", [(rx, rb[1] + rb[3] * (0.5 - 0.04 * i))])
    d.lift()
    s = st(d)
    ok("phone fly: a finger on the slider changes the speed (up = faster)", s["speed"] > sp0 * 1.2, (sp0, s["speed"], s["val"]))
    ok("phone: no finger left registered", d.js("return %s.CV.ptr.size;" % L) == 0)
    d.shot("%s-03-fly-moved.png" % TAG)
    e0 = eye(d)
    d.tap("#camArc")
    s = st(d)
    ok("phone: a tap on Arcball switches back without a jump, touch arcball hint", consistent(s, False) and same_eye(e0, eye(d)) and s["hint"].startswith("Drag to turn. Pinch to zoom."), (s, cam(d)))
    d.tap("#camFly")
    d.tap("#reset"); d.settle()
    c = cam(d); s = st(d)
    ok("phone: Reset view in fly mode restores the start view, still fly", abs(c["dist"] - 5.2) < 1e-9 and abs(c["yaw"] + 1) < 1e-9 and consistent(s, True), (c, s))
    d.js("const e = document.getElementById('viewFly'); let p = e; while (p) { if (p.tagName === 'DETAILS') p.open = true; p = p.parentElement; } e.scrollIntoView({block: 'center'});")
    time.sleep(0.3)
    d.tap("#viewFly")
    s = st(d)
    ok("phone: a tap on the Fly camera checkbox turns fly off, buttons agree", consistent(s, False), s)
    d.shot("%s-04-view-section.png" % TAG, clip="#secView", wait=False)
    # 2D on the phone while flying
    d.tap("#viewFly")
    d.js("document.getElementById('flat').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    d.tap("#flat")
    d.idle(150); d.stage()
    s = st(d)
    ok("phone 2D while flying: switch hidden, 2D touch hint", s["modeHidden"] is True and s["hint"].startswith("Drag to slide the picture. Pinch"), s)
    d.shot("%s-05-flat.png" % TAG)


def main():
    global TAG
    which = sys.argv[1] if len(sys.argv) > 1 else "desktop"
    TAG = "d" if which == "desktop" else "p"
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p7real-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(150):
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
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        d = Drive(page)
        try:
            if which == "desktop":
                d.load(PAGE)
                desktop(d, page)
            else:
                phone(d, page)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            ok("the run finished without the script failing", False, ex)
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
    print("%d passed, %d failed" % (results.count(True), results.count(False)))


if __name__ == "__main__":
    main()
