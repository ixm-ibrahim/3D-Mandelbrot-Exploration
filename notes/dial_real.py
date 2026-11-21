"""Drive the controls kit with REAL input (mouse, keyboard, wheel, touch) through the Chrome DevTools protocol.

tools/shot.py can only run page JavaScript, and its headless window has no focus, so it cannot see focus
rings, native blur, wheel behaviour, press-and-hold or a dragged slider. This script can.

  python notes/dial_real.py            # tests/dial.html: in-page checks with a focused window, then real input, then a phone
  python notes/dial_real.py --lab      # also dist/dial.html (build it first): the kit inside the lab, desktop and phone
  python notes/dial_real.py --lab=dist/other.html     # the same against another build

The lab part was written against the baseline page (base/ plus the new kit): it expects Power n to be the first dial
in #eqDials with the ids pow / powNum / powStep, an Iterations dial "iter", and the lathe approach's spin dial
"par-lathe-spin". If the page's markup moves on, adjust lab() below.

Screenshots go to out/dial/. Exit code 0 when every line says pass.
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

OUT = os.path.join(ROOT, "out", "dial")
KEYS = {"Tab": 9, "Enter": 13, "Escape": 27, "PageUp": 33, "PageDown": 34, "ArrowLeft": 37, "ArrowUp": 38,
        "ArrowRight": 39, "ArrowDown": 40}
SHIFT = 8
results = []


def ok(name, cond, detail=""):
    results.append(bool(cond))
    print(("pass  " if cond else "FAIL  ") + name + ("" if cond else "  :: " + str(detail)))


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, rel, wait=None):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 30)
        if wait and not self.p.wait(wait, 90):
            raise RuntimeError("timed out waiting for " + wait)
        time.sleep(0.3)

    def centre(self, sel, fx=0.5, fy=0.5):
        box = self.js("const e = document.querySelector(%s); e.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 80));"
                      "const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))
        return box[0] + box[2] * fx, box[1] + box[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, modifiers=0, hold=0.0, fx=0.5):
        x, y = self.centre(sel, fx)
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", clickCount=count, modifiers=modifiers)
        if hold:
            time.sleep(hold)
        self.mouse("mouseReleased", x, y, button="left", clickCount=count, modifiers=modifiers)

    def key(self, name, modifiers=0):
        kw = dict(key=name, code=name, windowsVirtualKeyCode=KEYS[name], modifiers=modifiers)
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def text(self, s):
        self.p.call("Input.insertText", text=s)

    def retype(self, sel, s):
        """Select everything in a box with a real triple click, then type over it."""
        self.click(sel, count=3)
        self.text(s)

    def wheel(self, sel, dy):
        x, y = self.centre(sel)
        self.mouse("mouseMoved", x, y)
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy)
        time.sleep(0.25)

    def tap(self, sel):
        x, y = self.centre(sel)
        self.p.call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
        self.p.call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
        time.sleep(0.15)

    def shot(self, name, clip=None):
        self.p.shot(os.path.join(OUT, name), clip)
        print("      wrote out/dial/" + name)


def in_page_checks(d, label):
    lines = d.js("return window.dialTests.lines;")
    bad = [l for l in lines if not l.startswith("pass")]
    ring = [l for l in lines if "ring" in l or "keyboard focus" in l.lower()]
    ok("%s: all %d in-page checks pass with a focused window" % (label, len(lines)), not bad, bad)
    ok("%s: the focus-ring check ran for real" % label, any("2 px ring" in l and l.startswith("pass") for l in ring), ring)


def real_input(d):
    S = "window.dialShow['320']"
    num, rng = "#s320-nNum", "#s320-n"
    val = lambda k="n": d.js("return %s.%s;" % (S, k))
    box = lambda: d.js("return document.querySelector('%s').value;" % num)
    active = lambda: d.js("const a = document.activeElement; return a ? a.id || a.tagName : '';")

    # typing, committed by really leaving the box
    d.retype(num, "3,25")
    ok("typing changes nothing until it is committed", val() == 2.37, val())
    d.key("Tab")
    ok("typed 3,25 then Tab: the value is 3.25 and focus moved to the slider", val() == 3.25 and active() == "s320-n", (val(), active()))
    ok("the box shows 3.25", box() == "3.25", box())
    d.retype(num, "\u22121.5e0")
    d.key("Enter")
    ok("typed \u22121.5e0 then Enter: the value is -1.5 and focus stays in the box", val() == -1.5 and active() == "s320-nNum", (val(), active()))
    d.retype(num, "abc")
    d.key("Enter")
    flagged = d.js("return document.querySelector('%s').getAttribute('aria-invalid');" % num)
    ok("typed abc then Enter: the old value is back and the box is flagged", box() == "-1.5" and val() == -1.5 and flagged == "true", (box(), val(), flagged))
    d.shot("real-invalid.png", "#show320 .dial")
    time.sleep(1.6)
    ok("the flag clears by itself", d.js("return document.querySelector('%s').getAttribute('aria-invalid');" % num) is None)
    d.retype(num, "9")
    d.key("Escape")
    d.key("Tab")
    ok("typed 9 then Escape then Tab: nothing changed", val() == -1.5 and box() == "-1.5", (val(), box()))
    d.retype(num, "99")
    d.click("#show320 .label")          # leave by clicking somewhere else
    ok("typed 99 then clicked away: clamped to the hard limit 24, slider thumb at its end", val() == 24 and d.js("return document.querySelector('%s').value;" % rng) == "10", val())

    # arrow keys in the box
    d.retype(num, "2.37")
    d.key("Enter")
    d.key("ArrowUp")
    a = val()
    d.key("ArrowUp", SHIFT)
    b = val()
    d.key("PageDown")
    c = val()
    d.key("ArrowDown")
    ok("real ArrowUp, Shift+ArrowUp, PageDown, ArrowDown: 2.47, 3.47, 2.47, 2.37", (a, b, c, val()) == (2.47, 3.47, 2.47, 2.37), (a, b, c, val()))

    # the wheel
    y0 = d.js("return window.scrollY;")
    d.click(num)                         # focused box: this is where type=number used to spin
    for dy in (-120, -120, 120, -360):
        d.wheel(num, dy)
    d.key("Tab")                         # focus the slider, then wheel over it
    for dy in (-120, 120, 120):
        d.wheel(rng, dy)
    ok("real wheel over the focused box and the focused slider: the value stays 2.37", val() == 2.37, val())
    d.js("window.scrollTo(0, 0);")
    time.sleep(0.2)
    x, y = d.centre(num)
    y_before = d.js("return window.scrollY;")
    d.mouse("mouseWheel", x, y, deltaX=0, deltaY=300)
    time.sleep(0.5)
    y_after = d.js("return window.scrollY;")
    ok("the wheel over a dial still scrolls the page", y_after > y_before, (y0, y_before, y_after))

    # step buttons with the real mouse
    d.retype(num, "2.37")
    d.key("Enter")
    d.click("#show320 .dial .dial-up")
    ok("one real click on the up button is one step (2.47), and focus stays in the box", val() == 2.47 and active() == "s320-nNum", (val(), active()))
    d.click("#show320 .dial .dial-down", modifiers=SHIFT)
    ok("Shift+click on the down button is ten steps (1.47)", val() == 1.47, val())
    d.click("#show320 .dial .dial-up", hold=1.0)
    held = val()
    time.sleep(0.4)
    ok("holding the up button for a second repeats (more than 5 steps), and stops on release", held > 1.47 + 0.55 and val() == held, (held, val()))
    ok("every repeated step is clean", d.js("return document.querySelector('%s').value;" % num) == ("%g" % held), (box(), held))

    # the toggle with the real mouse
    d.retype(num, "2.37")
    d.key("Enter")
    d.click("#s320-nStep")
    label = d.js("return document.querySelector('#s320-nStep').textContent;")
    d.click("#show320 .dial .dial-up")
    a = val()
    d.click("#show320 .dial .dial-up")
    b = val()
    d.retype(num, "2.37")
    d.key("ArrowDown")
    ok("toggle pressed: it reads \u00b11, up gives 3 then 4, ArrowDown from 2.37 gives 2", (label, a, b, val()) == ("\u00b11", 3, 4, 2), (label, a, b, val()))
    d.click("#s320-nStep")
    d.key("Tab")

    # the slider with the real mouse and keyboard
    x0, y0 = d.centre(rng, 0.02)
    x1, _ = d.centre(rng, 0.5)
    d.js("%s.n = 2; syncControls();" % S)
    d.mouse("mouseMoved", x0, y0)
    d.mouse("mousePressed", x0, y0, button="left", clickCount=1)
    for i in range(1, 9):
        d.mouse("mouseMoved", x0 + (x1 - x0) * i / 8, y0, button="left", buttons=1)
    d.mouse("mouseReleased", x1, y0, button="left", clickCount=1)
    v = val()
    ok("dragging the thumb to the middle of the slider gives about 6, on the 0.1 grid", 5.7 <= v <= 6.3 and round(v, 1) == v, v)
    d.key("ArrowRight")
    ok("ArrowRight on the focused slider adds one step", abs(val() - (v + 0.1)) < 1e-9 and round(val(), 1) == val(), (v, val()))

    # tab order and focus rings
    d.click("#s320-turnNum")
    d.key("Tab")
    after = active()
    d.shot("ring-slider.png", "#show320 .dial:nth-child(4)")
    d.key("Tab", SHIFT)
    d.shot("ring-box.png", "#show320 .dial:nth-child(4)")
    d.key("Tab", SHIFT)
    before = active()
    d.key("Tab", SHIFT)
    before2 = active()
    d.shot("ring-play.png", "#show320 .dial:nth-child(4)")
    ok("Tab from the box goes to the slider, Shift+Tab to the step toggle and then to the play button; the step buttons are skipped",
       (after, before, before2) == ("s320-turn", "s320-turnStep", "s320-turnPlay"), (after, before, before2))
    ring = d.js("const e = document.activeElement, cs = getComputedStyle(e); return [e.matches(':focus-visible'), cs.outlineStyle, cs.outlineWidth].join(' ');")
    ok("a button reached with Tab shows a 2 px ring", ring == "true solid 2px", ring)
    d.click("#s320-liftNum")
    d.key("Tab", SHIFT)
    d.shot("ring-toggle.png", "#show320 .dial:nth-child(5)")
    d.js("document.querySelector('#s320-pal').focus();")
    d.key("Tab")
    ring = d.js("const e = document.activeElement, cs = getComputedStyle(e); return [e.id, e.matches(':focus-visible'), cs.outlineStyle, cs.outlineWidth].join(' ');")
    d.shot("ring-check.png", "#show320")
    ok("a checkbox reached with Tab shows a 2 px ring", ring == "s320-rev true solid 2px", ring)

    # play with the real mouse
    d.click("#s320-turnPlay")
    time.sleep(1.0)
    a = val("turn")
    time.sleep(1.0)
    b = val("turn")
    d.click("#s320-turnPlay")
    time.sleep(0.3)
    c = val("turn")
    time.sleep(0.4)
    ok("play sweeps Turn at about 45 degrees a second (one 360 degree range per 8 s), pause holds it", 36 <= b - a <= 54 and val("turn") == c, (a, b, c, val("turn")))


def phone(d, page):
    page.call("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)
    page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    d.load("tests/dial.html", "window.dialTests && window.dialTests.done")
    coarse = d.js("return matchMedia('(pointer: coarse)').matches;")
    ok("phone emulation: the pointer is coarse and the viewport is 375 px wide", coarse and d.js("return innerWidth;") == 375, coarse)
    lines = d.js("return window.dialTests.lines;")
    bad = [l for l in lines if not l.startswith("pass")]
    ok("phone: all %d in-page checks pass with finger-sized controls (this includes the 343, 295 and 240 px fits)" % len(lines), not bad, bad)
    sizes = d.js("const q = s => document.querySelector(s).getBoundingClientRect(); const u = q('#show343 .dial-up'), b = q('#show343 .dial-num'), t = q('#s343-nStep');"
                 "return [u.width, u.height, b.height, t.height, parseFloat(getComputedStyle(document.querySelector('#s343-nNum')).fontSize)];")
    ok("phone: step buttons are at least 30 x 30, the box text is 16 px (no zoom on focus)", sizes[0] >= 30 and sizes[1] >= 30 and sizes[4] >= 16, sizes)
    over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
    ok("phone: the page does not scroll sideways", over <= 0, over)
    d.js("window.dialShow['343'].n = 2.37; syncControls();")
    d.tap("#show343 .dial .dial-up")
    v = d.js("return window.dialShow['343'].n;")
    act = d.js("const a = document.activeElement; return a ? a.id || a.tagName : '';")
    ok("phone: one tap on the up button is one step (2.47) and does not put the caret in the box", v == 2.47 and act != "s343-nNum", (v, act))
    d.tap("#s343-nStep")
    d.tap("#show343 .dial .dial-down")
    v = d.js("return window.dialShow['343'].n;")
    ok("phone: tap the toggle, tap down: the next whole number below (2)", v == 2, v)
    d.js("document.querySelector('#show343').scrollIntoView({block: 'start'});")
    time.sleep(0.2)
    d.shot("phone-343.png")
    d.js("document.querySelector('#show295').parentElement.scrollIntoView({block: 'start'});")
    time.sleep(0.2)
    d.shot("phone-295.png")


def lab(d, page, phone_mode, path):
    L = "window.squaringLab"
    d.load(path, L + " && " + L + ".idle()")
    tag = "lab on a phone" if phone_mode else "lab"
    n_dials = d.js("return document.querySelectorAll('.dial').length;")
    ok("%s: the page starts and builds its dials with the new kit (%s dials)" % (tag, n_dials), n_dials >= 20, n_dials)
    if phone_mode:
        d.js("document.querySelectorAll('details.sec').forEach(s => { s.open = true; });")
        over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
        ok("lab on a phone: no sideways scrolling with every section open", over <= 0, over)
        stick = d.js("const out = []; for (const dial of document.querySelectorAll('.dial')) { if (!dial.checkVisibility()) continue; const host = dial.parentElement.getBoundingClientRect();"
                     "for (const e of dial.querySelectorAll('*')) { const r = e.getBoundingClientRect(); if (r.width && (r.left < host.left - 0.5 || r.right > host.right + 0.5)) out.push(dial.querySelector('label').textContent); } } return [...new Set(out)];")
        ok("lab on a phone: no dial sticks out of its column", not stick, stick)
        d.tap("#eqDials .dial .dial-up")
        ok("lab on a phone: a tap on Power n's up button gives 2.1", d.js("return %s.S.n;" % L) == 2.1, d.js("return %s.S.n;" % L))
        for name, sel in (("lab-phone-approach.png", "#secApproach"), ("lab-phone-equation.png", "#eqDials"), ("lab-phone-quality.png", "#qDials")):
            d.js("document.querySelector(%s).scrollIntoView({block: 'start'});" % json.dumps(sel))
            time.sleep(0.3)
            d.shot(name)
        return
    d.retype("#powNum", "3.5")
    d.key("Enter")
    ok("lab: typing 3.5 into Power n sets S.n", d.js("return %s.S.n;" % L) == 3.5)
    low = int(d.js("return +document.querySelector('#pow').min;"))   # 2 on the baseline page, -8 once the power may be negative
    d.retype("#powNum", "\u2212%d" % (4 - low))
    d.key("Tab")
    ok("lab: typing \u2212%d (below the slider's range) is kept as %d, thumb at the low end" % (4 - low, low - 4),
       d.js("return [%s.S.n, document.querySelector('#pow').value];" % L) == [low - 4, str(low)])
    d.retype("#powNum", "99")
    d.key("Enter")
    ok("lab: 99 clamps to the hard limit 24", d.js("return %s.S.n;" % L) == 24)
    d.retype("#iterNum", "20.6")
    d.key("Enter")
    ok("lab: Iterations rounds through its setter and the box shows what the state holds (21)", d.js("return [%s.S.iter, document.querySelector('#iterNum').value];" % L) == [21, "21"])
    d.retype("#powNum", "2.37")
    d.key("Enter")
    d.click("#powStep")
    d.click("#eqDials .dial .dial-up")
    ok("lab: Power n, whole-number steps: 2.37 goes to 3", d.js("return %s.S.n;" % L) == 3)
    d.click("#powStep")
    d.click("#ap-lathe + .mark")
    d.retype("#par-lathe-spinNum", "4")
    d.key("Enter")
    ok("lab: the odd-only spin dial turns a typed 4 into 5", d.js("return %s.S.param.lathe.spin;" % L) == 5)
    time.sleep(0.5)
    d.js("document.querySelectorAll('details.sec').forEach(s => { s.open = true; });")
    d.js("document.querySelector('.dials').scrollIntoView({block: 'start'});")
    time.sleep(0.4)
    d.shot("lab-sidebar-top.png")
    d.js("document.querySelector('#secColour').scrollIntoView({block: 'start'});")
    time.sleep(0.4)
    d.shot("lab-sidebar-bottom.png")
    if not d.p.wait(L + ".idle()", 90):
        ok("lab: the picture finishes drawing after the changes", False, d.js("return document.getElementById('status').textContent;"))


def main():
    lab_arg = next((a for a in sys.argv[1:] if a == "--lab" or a.startswith("--lab=")), None)
    lab_path = None if lab_arg is None else (lab_arg[6:] or "dist/dial.html") if "=" in lab_arg else "dist/dial.html"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # the check names contain a typographic minus
    os.makedirs(OUT, exist_ok=True)
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("No Chrome or Edge found.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="dialreal-")
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

        d.load("tests/dial.html", "window.dialTests && window.dialTests.done")
        in_page_checks(d, "desktop")
        real_input(d)
        if lab_path:
            lab(d, page, False, lab_path)
        phone(d, page)
        if lab_path:
            lab(d, page, True, lab_path)

        page.js("return 0;")
        problems = [p for p in page.problems if "controls kit checks failed" not in p]
        ok("no console errors or uncaught exceptions", not problems, problems[:10])
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
