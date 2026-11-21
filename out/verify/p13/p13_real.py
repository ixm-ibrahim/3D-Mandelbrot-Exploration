"""p13: collapse all. Real mouse, keyboard and touch against dist/preview.html. Writes into out/verify/p13/."""
import base64, json, os, shutil, socket, subprocess, sys, tempfile, time, traceback, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

L = "window.squaringLab"
VK = {"Tab": 9, "Enter": 13, " ": 32}
CODE = {"Tab": "Tab", "Enter": "Enter", " ": "Space"}
SHIFT = 8
STATES = ("return [...document.querySelectorAll('#sections > details.sec')].map(d => { const r = d.querySelector('summary').getBoundingClientRect();"
          " return {id: d.id, open: d.open, hidden: d.hidden, title: d.querySelector('summary').textContent, top: Math.round(r.top), bottom: Math.round(r.bottom)}; });")


def say(*a):
    print(*a, flush=True)


class D:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, rel):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 60)
        if not self.p.wait(L, 120):
            raise RuntimeError("the lab did not start")
        time.sleep(0.5)

    def idle(self, t=300):
        t0 = time.time()
        ok = self.p.wait(L + ".idle()", t)
        say("   (idle after %.1f s: %s)" % (time.time() - t0, ok))
        return ok

    def rect(self, sel):
        return self.js("const e = document.querySelector(%s); if (!e) return null; const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))

    def into_view(self, sel):
        """Scroll only when the element is not comfortably inside the window."""
        self.js("const e = document.querySelector(%s), b = e.getBoundingClientRect(); if (b.top < 60 || b.bottom > innerHeight - 60) { e.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 150)); }" % json.dumps(sel))

    def click(self, sel, fx=0.5, fy=0.5, scroll=True):
        if scroll:
            self.into_view(sel)
        b = self.rect(sel)
        x, y = b[0] + b[2] * fx, b[1] + b[3] * fy
        self.p.call("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
        self.p.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
        self.p.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
        time.sleep(0.25)
        return x, y

    def tap(self, sel, scroll=True):
        if scroll:
            self.into_view(sel)
        b = self.rect(sel)
        x, y = b[0] + b[2] / 2, b[1] + b[3] / 2
        self.p.call("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": x, "y": y}])
        self.p.call("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])
        time.sleep(0.35)
        return x, y

    def key(self, name, modifiers=0):
        kw = dict(key=name, code=CODE[name], windowsVirtualKeyCode=VK[name], nativeVirtualKeyCode=VK[name], modifiers=modifiers)
        text = {"Enter": "\r", " ": " "}.get(name)
        if text:
            self.p.call("Input.dispatchKeyEvent", type="keyDown", text=text, unmodifiedText=text, **kw)
        else:
            self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)
        time.sleep(0.2)

    def snap(self, name, sel=None, pad=0):
        params = {"format": "png", "captureBeyondViewport": False}
        if sel:
            b = self.rect(sel)
            sx, sy = self.js("return [scrollX, scrollY];")
            params["clip"] = {"x": b[0] + sx - pad, "y": b[1] + sy - pad, "width": b[2] + 2 * pad, "height": b[3] + 2 * pad, "scale": 1}
        data = base64.b64decode(self.p.call("Page.captureScreenshot", **params)["data"])
        with open(os.path.join(HERE, name), "wb") as f:
            f.write(data)
        say("   wrote out/verify/p13/" + name)
        return data

    def states(self):
        return self.js(STATES)

    def label(self):
        return self.js("return document.getElementById('collapseAll').textContent;")

    def active(self):
        return self.js("const a = document.activeElement; if (!a) return ''; const cs = getComputedStyle(a); let name = a.id || (a.tagName === 'SUMMARY' ? 'summary:' + a.textContent : a.tagName + '.' + a.className);"
                       " return name + ' | fv=' + a.matches(':focus-visible') + ' outline=' + cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor;")

    def mon_start(self):
        self.js("const L = window.squaringLab; const m = window.__mon = {on: true, frames: 0, notIdle: 0, renderBusy: 0, prog: 0, busy: 0, status0: document.getElementById('status').textContent, statusChanged: 0, draws0: window.__draws};"
                " const loop = () => { m.frames++; if (!L.idle()) m.notIdle++; if (!L.renderIdle()) m.renderBusy++; const p = document.getElementById('drawProgress'); if (p && !p.hidden) m.prog++;"
                " const b = document.getElementById('busy'); if (b && !b.hidden) m.busy++; if (document.getElementById('status').textContent !== m.status0) m.statusChanged++; if (m.on) requestAnimationFrame(loop); }; requestAnimationFrame(loop);")

    def mon_stop(self):
        return self.js("const m = window.__mon; m.on = false; return {frames: m.frames, notIdle: m.notIdle, renderBusy: m.renderBusy, progressBarFrames: m.prog, busyLabelFrames: m.busy, statusChangedFrames: m.statusChanged, drawCalls: window.__draws - m.draws0};")


def short(states, all_=False):
    return " ".join("%s:%s" % (s["id"], "open" if s["open"] else "shut") for s in states if all_ or not s["hidden"]) + \
        ("" if all_ else "   [hidden: " + " ".join("%s:%s" % (s["id"], "open" if s["open"] else "shut") for s in states if s["hidden"]) + "]")


def block(name, f, *a):
    say("\n=== " + name)
    try:
        f(*a)
    except Exception:
        say("   BLOCK FAILED: " + traceback.format_exc()[-900:])


def desk_place(d):
    d.js("const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 2; L.syncControls(); L.touch();")
    d.idle()
    info = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; };"
                " return {win: [innerWidth, innerHeight], scrollY, button: q('#collapseAll'), toprow: q('.toprow'), flatLabel: q('#flatHost'), dials: q('.dials'), stage: q('#stage'), mode: q('fieldset.mode'), pageH: document.documentElement.scrollHeight, text: document.getElementById('collapseAll').textContent};")
    say("   placement at load:", json.dumps(info))
    d.snap("d-01-load.png")
    d.snap("d-01-toprow.png", ".toprow", 8)
    say("   sections at load:", short(d.states()))
    d.js("const gl = document.getElementById('view').getContext('webgl2'); window.__draws = 0; const o = gl.drawArrays.bind(gl); gl.drawArrays = function (...a) { window.__draws++; return o(...a); };")


def desk_collapse(d):
    d.js("window.scrollTo(0, 0);")
    time.sleep(0.3)
    d.idle()
    before = d.snap("d-02-stage-before.png", "#stage")
    lower0 = d.js("return [document.getElementById('card').textContent.length, document.getElementById('cap3d').textContent, document.getElementById('step3d').toDataURL().length, document.getElementById('step2d').toDataURL().length];")
    b0 = d.rect("#collapseAll")
    d.mon_start()
    xy = d.click("#collapseAll", scroll=False)
    time.sleep(1.5)
    m = d.mon_stop()
    after = d.snap("d-02-stage-after-collapse.png", "#stage")
    st = d.states()
    b1 = d.rect("#collapseAll")
    say("   after a real click on Collapse all: label=%r  %s" % (d.label(), short(st)))
    say("   every visible section shut:", all(not s["open"] for s in st if not s["hidden"]))
    say("   render monitor:", json.dumps(m), " stage picture identical:", before == after)
    say("   button box before %s after %s, click at %s still on the button: %s" % ([round(v) for v in b0], [round(v) for v in b1], [round(v) for v in xy], b1[0] <= xy[0] <= b1[0] + b1[2] and b1[1] <= xy[1] <= b1[1] + b1[3]))
    fit = d.js("return {scrollY, innerHeight, titles: [...document.querySelectorAll('#sections > details.sec')].filter(x => !x.hidden).map(x => [x.querySelector('summary').textContent, Math.round(x.querySelector('summary').getBoundingClientRect().bottom)]), columnBottom: Math.round(document.querySelector('.dials').getBoundingClientRect().bottom), pageH: document.documentElement.scrollHeight};")
    say("   all titles on screen at once:", all(t[1] <= fit["innerHeight"] for t in fit["titles"]), json.dumps(fit, ensure_ascii=False))
    lower1 = d.js("return [document.getElementById('card').textContent.length, document.getElementById('cap3d').textContent, document.getElementById('step3d').toDataURL().length, document.getElementById('step2d').toDataURL().length];")
    say("   step figure and scorecard unchanged:", lower0 == lower1, "lower section top now at", d.js("return Math.round(document.querySelector('.lower').getBoundingClientRect().top);"))
    d.snap("d-03-collapsed.png")
    # open one by hand: the label and the scroll position
    for sid in ("secColour", "secQuality"):
        sel = "#%s > summary" % sid
        r0, y0 = d.rect(sel), d.js("return scrollY;")
        d.mon_start()
        d.click(sel, scroll=False)
        time.sleep(0.8)
        m = d.mon_stop()
        r1, y1 = d.rect(sel), d.js("return scrollY;")
        say("   opened %s by hand: open=%s label=%r  header top %d -> %d, scrollY %d -> %d, monitor %s" % (sid, d.js("return document.getElementById(%s).open;" % json.dumps(sid)), d.label(), r0[1], r1[1], y0, y1, json.dumps(m)))
        d.snap("d-04-opened-%s.png" % sid)
        d.click(sel, scroll=False)
        say("   shut %s by hand: open=%s label=%r header top now %d scrollY %d" % (sid, d.js("return document.getElementById(%s).open;" % json.dumps(sid)), d.label(), d.rect(sel)[1], d.js("return scrollY;")))
    # expand all
    d.js("window.scrollTo(0, 0);")
    time.sleep(0.2)
    before = d.snap("d-05-stage-before-expand.png", "#stage")
    d.mon_start()
    d.click("#collapseAll", scroll=False)
    time.sleep(1.5)
    m = d.mon_stop()
    after = d.snap("d-05-stage-after-expand.png", "#stage")
    st = d.states()
    say("   after a real click on Expand all: label=%r  %s" % (d.label(), short(st)))
    say("   every visible section open:", all(s["open"] for s in st if not s["hidden"]), " monitor:", json.dumps(m), " stage picture identical:", before == after)
    say("   page height with everything open:", d.js("return [document.documentElement.scrollHeight, Math.round(document.querySelector('.dials').getBoundingClientRect().height)];"))
    d.snap("d-06-expanded.png")


def desk_headers_mouse(d):
    """Every header, shut and open again with the real mouse; watch the label and whether the header stays under the pointer."""
    ids = [s["id"] for s in d.states() if not s["hidden"]]
    for step, want in (("shut", False), ("open", True)):
        for i, sid in enumerate(ids):
            sel = "#%s > summary" % sid
            d.into_view(sel)
            r0, y0 = d.rect(sel), d.js("return scrollY;")
            fx = (0.08, 0.5, 0.97)[i % 3]          # on the title, in the middle, on the plus sign
            d.click(sel, fx=fx, scroll=False)
            r1, y1 = d.rect(sel), d.js("return scrollY;")
            o = d.js("return document.getElementById(%s).open;" % json.dumps(sid))
            moved = round(r1[1] - r0[1])
            say("   mouse %s %-12s at %.0f%% of the row: open=%s %s label=%r header moved %d px (scrollY %d -> %d)" % (step, sid, fx * 100, o, "ok" if o == want else "WRONG", d.label(), moved, y0, y1))
    say("   end state:", short(d.states()), "label:", d.label())


def desk_keyboard(d):
    d.js("window.scrollTo(0, 0); document.activeElement && document.activeElement.blur();")
    # how many Tab presses from the top of the page
    path = []
    for i in range(40):
        d.key("Tab")
        a = d.active()
        path.append(a.split(" | ")[0])
        if a.startswith("collapseAll"):
            break
    say("   Tab from the top of the page reaches the button after %d presses: %s" % (len(path), " > ".join(path)))
    say("   focus on the button:", d.active())
    d.snap("d-07-button-focus.png", ".toprow", 10)
    st0 = short(d.states())
    d.key("Enter")
    time.sleep(0.3)
    say("   Enter on the button: label=%r  %s   (was %s)" % (d.label(), short(d.states()), st0))
    d.key(" ")
    time.sleep(0.3)
    say("   Space on the button: label=%r  %s" % (d.label(), short(d.states())))
    say("   focus still on the button:", d.active().split(" | ")[0])
    if any(s["open"] for s in d.states() if not s["hidden"]):
        d.key("Enter")
        time.sleep(0.3)
    say("   now collapsed for the header walk: label=%r" % d.label())
    seen = []
    for i in range(14):
        d.key("Tab")
        a = d.active()
        name = a.split(" | ")[0]
        seen.append(name)
        if name.startswith("summary:"):
            sid = d.js("return document.activeElement.parentElement.id;")
            res = []
            for k in ("Enter", "Enter", " ", " "):
                d.key(k)
                res.append(d.js("return document.getElementById(%s).open;" % json.dumps(sid)))
            good = res == [True, False, True, False]
            say("   header %-12s by keyboard: Enter, Enter, Space, Space gave open=%s %s; ring: %s; label=%r" % (sid, res, "ok" if good else "WRONG", a.split(" | ")[1], d.label()))
            if sid == "secColour":
                d.snap("d-08-header-focus.png", "#secColour", 8)
            if sid == "secQuality":
                break
    say("   Tab order after the button:", " > ".join(seen))
    d.snap("d-09-keyboard-end.png")
    # keyboard-open the last header and see whether the page follows
    d.key("Enter")
    time.sleep(0.4)
    say("   Enter on the last header: open=%s, scrollY=%s, header at y=%s, section bottom at y=%s of %s" % tuple(d.js(
        "const s = document.getElementById('secQuality'), r = s.querySelector('summary').getBoundingClientRect(); return [s.open, scrollY, Math.round(r.top), Math.round(s.getBoundingClientRect().bottom), innerHeight];")))
    d.key("Enter")


def desk_modes(d):
    d.js("window.scrollTo(0, 0);")
    if any(s["open"] for s in d.states() if not s["hidden"]):
        d.click("#collapseAll", scroll=False)
    say("   Mandelbrot, collapsed: label=%r  %s" % (d.label(), short(d.states())))
    d.click("label.seg:has(#mode-j) span", scroll=False)
    time.sleep(0.6)
    say("   -> Julia:      label=%r  %s" % (d.label(), short(d.states())))
    d.snap("d-10-collapsed-then-julia.png")
    d.click("label.seg:has(#mode-k) span", scroll=False)
    time.sleep(0.6)
    say("   -> Kleinian:   label=%r  %s" % (d.label(), short(d.states())))
    d.snap("d-10-collapsed-then-klein.png")
    # collapse here, then go back
    if any(s["open"] for s in d.states() if not s["hidden"]):
        d.click("#collapseAll", scroll=False)
    say("   Kleinian after Collapse all: label=%r  %s" % (d.label(), short(d.states())))
    d.snap("d-10-klein-collapsed.png")
    d.click("label.seg:has(#mode-m) span", scroll=False)
    time.sleep(0.6)
    say("   -> Mandelbrot: label=%r  %s" % (d.label(), short(d.states())))
    d.snap("d-10-klein-collapsed-then-mandel.png")
    # hand-made pattern, then mode and approach switches
    if not all(s["open"] for s in d.states() if not s["hidden"]):
        if not any(s["open"] for s in d.states() if not s["hidden"]):
            d.click("#collapseAll", scroll=False)
        else:
            d.click("#collapseAll", scroll=False); d.click("#collapseAll", scroll=False)
    d.js("window.scrollTo(0, 0);")
    say("   Mandelbrot after Expand all: label=%r  %s" % (d.label(), short(d.states())))
    for sid in ("secCut", "secView"):
        d.click("#%s > summary" % sid)
    pat0 = short(d.states())
    say("   pattern by hand (Slice and View shut): %s" % pat0)
    d.click("label.rule-head:has(#ap-lathe)", fy=0.3)
    time.sleep(0.8)
    say("   after choosing another approach (%s): %s  same=%s" % (d.js("return window.squaringLab.S.approach;"), short(d.states()), short(d.states()) == pat0))
    d.js("window.scrollTo(0, 0);")
    d.click("label.seg:has(#mode-j) span", scroll=False)
    time.sleep(0.6)
    say("   -> Julia:      label=%r  %s" % (d.label(), short(d.states())))
    d.click("label.seg:has(#mode-m) span", scroll=False)
    time.sleep(0.6)
    say("   -> Mandelbrot: label=%r  %s  same as the hand pattern=%s" % (d.label(), short(d.states()), short(d.states()) == pat0))
    d.click("label.rule-head:has(#ap-mercator)", fy=0.3)


def desk_play(d):
    """A playing sweep and Collapse all."""
    d.js("window.scrollTo(0, 0);")
    if not d.js("return document.getElementById('secApproach').open;"):
        d.click("#secApproach > summary")
    d.click("#par-mercator-liftPlay")
    time.sleep(1.2)
    a = d.js("const e = document.getElementById('par-mercator-liftPlay'); return [e.getAttribute('aria-pressed'), window.squaringLab.S.param.mercator.lift];")
    d.js("window.scrollTo(0, 0);")
    time.sleep(0.2)
    d.click("#collapseAll", scroll=False)
    time.sleep(1.0)
    b = d.js("const e = document.getElementById('par-mercator-liftPlay'); return [e.getAttribute('aria-pressed'), window.squaringLab.S.param.mercator.lift];")
    time.sleep(1.0)
    c = d.js("const e = document.getElementById('par-mercator-liftPlay'); return [e.getAttribute('aria-pressed'), window.squaringLab.S.param.mercator.lift];")
    say("   Lift playing %s -> after Collapse all %s -> a second later %s (label %r)" % (a, b, c, d.label()))
    d.click("#collapseAll", scroll=False)
    time.sleep(0.8)
    e = d.js("const e = document.getElementById('par-mercator-liftPlay'); return [e.getAttribute('aria-pressed'), window.squaringLab.S.param.mercator.lift];")
    say("   after Expand all: %s" % e)
    d.js("window.squaringLab.resetGroup('approach'); window.squaringLab.refresh(false);")


def phone(d, page):
    page.call("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)
    page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    d.load("dist/preview.html")
    d.js("const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 2; L.syncControls(); L.touch();")
    info = d.js("const q = s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; };"
                " return {win: [innerWidth, innerHeight], scrollY, button: q('#collapseAll'), toprow: q('.toprow'), flatLabel: q('#flatHost'), dials: q('.dials'), stage: q('#stage'), pageH: document.documentElement.scrollHeight, sideways: document.documentElement.scrollWidth - document.documentElement.clientWidth};")
    say("   phone placement at load:", json.dumps(info))
    say("   button visible without scrolling:", info["button"][3] <= info["win"][1])
    d.snap("p-01-load.png")
    d.idle(240)
    d.js("document.querySelector('.toprow').scrollIntoView({block: 'start'}); window.scrollBy(0, -12);")
    time.sleep(0.4)
    d.snap("p-02-controls-top.png")
    b0, y0 = d.rect("#collapseAll"), d.js("return scrollY;")
    before = d.js("return document.getElementById('view').toDataURL().length;")
    d.mon_start_safe = True
    d.js("window.__draws = window.__draws || 0;")
    d.mon_start()
    xy = d.tap("#collapseAll", scroll=False)
    time.sleep(1.5)
    m = d.mon_stop()
    b1, y1 = d.rect("#collapseAll"), d.js("return scrollY;")
    st = d.states()
    say("   after a real tap on Collapse all: label=%r  %s" % (d.label(), short(st)))
    say("   monitor:", json.dumps(m), " canvas data length same:", before == d.js("return document.getElementById('view').toDataURL().length;"))
    say("   button box before %s after %s; tap at %s; scrollY %d -> %d; tap point still on the button: %s" % ([round(v) for v in b0], [round(v) for v in b1], [round(v) for v in xy], y0, y1, b1[0] <= xy[0] <= b1[0] + b1[2] and b1[1] <= xy[1] <= b1[1] + b1[3]))
    fit = d.js("return {scrollY, innerHeight, titles: [...document.querySelectorAll('#sections > details.sec')].filter(x => !x.hidden).map(x => [x.querySelector('summary').textContent, Math.round(x.querySelector('summary').getBoundingClientRect().bottom)]), columnH: Math.round(document.querySelector('.dials').getBoundingClientRect().height)};")
    say("   phone, collapsed: all titles on screen at once:", all(t[1] <= fit["innerHeight"] for t in fit["titles"]), json.dumps(fit, ensure_ascii=False))
    d.snap("p-03-collapsed.png")
    sel = "#secQuality > summary"
    r0, y0 = d.rect(sel), d.js("return scrollY;")
    d.tap(sel, scroll=False)
    r1, y1 = d.rect(sel), d.js("return scrollY;")
    say("   tap on Quality and speed: open=%s label=%r header top %d -> %d scrollY %d -> %d" % (d.js("return document.getElementById('secQuality').open;"), d.label(), r0[1], r1[1], y0, y1))
    d.snap("p-04-opened-quality.png")
    d.tap(sel, scroll=False)
    say("   tap again: open=%s label=%r" % (d.js("return document.getElementById('secQuality').open;"), d.label()))
    d.tap("#collapseAll")
    st = d.states()
    say("   tap on Expand all: label=%r every visible open=%s; column height %s, page height %s, sideways scroll %s" % (
        d.label(), all(s["open"] for s in st if not s["hidden"]), d.js("return Math.round(document.querySelector('.dials').getBoundingClientRect().height);"),
        d.js("return document.documentElement.scrollHeight;"), d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")))
    # every header with a finger
    for sid in [s["id"] for s in st if not s["hidden"]]:
        sel = "#%s > summary" % sid
        d.into_view(sel)
        r0 = d.rect(sel)
        d.tap(sel, scroll=False)
        o1, r1 = d.js("return document.getElementById(%s).open;" % json.dumps(sid)), d.rect(sel)
        d.tap(sel, scroll=False)
        o2 = d.js("return document.getElementById(%s).open;" % json.dumps(sid))
        say("   finger on %-12s: shut -> open=%s, again -> open=%s %s; header %d px tall, moved %d px on shutting" % (sid, o1, o2, "ok" if (o1, o2) == (False, True) else "WRONG", r0[3], round(r1[1] - r0[1])))
    # does the top row re-wrap when the label changes? Try a range of widths.
    rows = []
    for w in (320, 340, 352, 360, 366, 370, 375, 380, 384, 390, 393, 400, 412, 414, 430):
        page.call("Emulation.setDeviceMetricsOverride", width=w, height=812, deviceScaleFactor=2, mobile=True)
        time.sleep(0.25)
        r = d.js("const b = document.getElementById('collapseAll'), t = document.querySelector('.toprow'), f = document.getElementById('flatHost'); const keep = b.textContent; const out = {};"
                 " for (const text of ['Collapse all', 'Expand all']) { b.textContent = text; const rb = b.getBoundingClientRect(), rt = t.getBoundingClientRect(), rf = f.getBoundingClientRect(); out[text] = [Math.round(rb.left - rt.left), Math.round(rb.top - rt.top), Math.round(rb.width), Math.round(rt.height), Math.round(rf.width), Math.round(rf.height)]; } b.textContent = keep; return out;")
        rows.append((w, r))
        flip = r["Collapse all"][1] != r["Expand all"][1] or r["Collapse all"][3] != r["Expand all"][3]
        say("   width %d: Collapse all at (left %d, top %d, w %d, row h %d, label w %d h %d); Expand all at (left %d, top %d, w %d, row h %d)%s" % (
            (w,) + tuple(r["Collapse all"]) + tuple(r["Expand all"][:4]) + ("   <-- the row re-wraps when the label changes" if flip else "",)))
    page.call("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p13real-")
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
        d = D(page)
        if which in ("all", "desk", "desk1", "desk2"):
            d.load("dist/preview.html")
            block("desktop: where the button is", desk_place, d)
            if which != "desk2":
                block("desktop: collapse, open by hand, expand", desk_collapse, d)
                block("desktop: every header with the mouse", desk_headers_mouse, d)
            if which != "desk1":
                block("desktop: keyboard", desk_keyboard, d)
                block("desktop: modes and approaches", desk_modes, d)
                block("desktop: a playing sweep", desk_play, d)
        if which in ("all", "phone"):
            block("phone 375x812", phone, d, page)
        page.js("return 0;")
        say("\nPAGE PROBLEMS (%d):" % len(page.problems))
        for p in page.problems[:20]:
            say("  " + p[:500])
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


if __name__ == "__main__":
    main()
