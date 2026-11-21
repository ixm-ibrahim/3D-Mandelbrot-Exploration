"""p4: zoom behaviour with REAL wheel / touch input on dist/preview.html. Adapted from notes/camera_real.py.
   python out/verify/p4/zoom_real.py [sections]   sections: any of a b c d e f (default all)
"""
import base64, io, json, math, os, shutil, socket, subprocess, sys, tempfile, time, traceback, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

OUT = HERE
PAGE = "dist/preview.html"
L = "window.squaringLab"
results = []
N12 = 1.12


def ok(name, cond, detail=""):
    results.append((bool(cond), name))
    print(("pass  " if cond else "FAIL  ") + name + ("  :: " + str(detail) if detail != "" else ""), flush=True)


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, rel):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 60)
        if not self.p.wait(L + " && " + L + ".idle()", 240):
            print("      (page did not reach idle in 240 s; carrying on)")
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

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def touch(self, kind, pts):
        self.p.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])
        if kind == "touchMove":
            time.sleep(0.03)

    def lift(self):
        time.sleep(0.25)
        self.touch("touchEnd", [])

    def settle(self, t=20):
        self.p.wait("!%s.CV.goal && !%s.CV.raf" % (L, L), t)
        time.sleep(0.08)

    def idle(self, t=180):
        return self.p.wait(L + ".idle()", t)

    def shot(self, name, clip="#stage"):
        self.p.shot(os.path.join(OUT, name), clip)
        self.js("window.scrollTo(0, 0);")   # Page.shot scrolls the clip into view; put the page back so mouse positions stay valid
        time.sleep(0.2)
        print("      wrote out/verify/p4/" + name, flush=True)

    def pump(self, secs):
        end = time.time() + secs
        while time.time() < end:
            self.p.call("Runtime.evaluate", expression="0")
            time.sleep(0.004)


class Cast:
    """Compositor frames as the user would see them (Page.startScreencast)."""
    def __init__(self, page):
        self.page, self.frames = page, []
        orig = page._event

        def ev(msg):
            if msg.get("method") == "Page.screencastFrame":
                p = msg["params"]
                self.frames.append((time.time(), p["data"]))
                page.n += 1
                page.ws.send(json.dumps({"id": page.n, "method": "Page.screencastFrameAck", "params": {"sessionId": p["sessionId"]}}))
            else:
                orig(msg)
        page._event = ev

    def start(self):
        self.frames = []
        self.page.call("Page.startScreencast", format="jpeg", quality=90, everyNthFrame=1)

    def stop(self):
        self.page.call("Page.stopScreencast")
        return self.frames


def analyse(frames, box, tag, cols=6, pick=None):
    """Per-frame mean brightness and sharpness of the stage; writes a contact sheet. Returns rows."""
    from PIL import Image, ImageFilter, ImageStat, ImageChops
    rows, thumbs, prev = [], [], None
    t0 = frames[0][0] if frames else 0
    for t, data in frames:
        im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        sx = im.width / VW
        # the picture only: leave out the right-hand slider column and the bottom bar
        crop = im.crop((int((box[0] + 90) * sx), int((box[1] + 10) * sx), int((box[0] + box[2] - 80) * sx), int((box[1] + box[3] - 60) * sx)))
        g = crop.convert("L")
        mean = ImageStat.Stat(g).mean[0]
        sharp = ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).mean[0]
        diff = ImageStat.Stat(ImageChops.difference(g, prev)).mean[0] if prev is not None else 0.0
        prev = g
        rows.append((t - t0, mean, sharp, diff))
        thumbs.append(crop)
    if thumbs:
        idx = pick if pick else list(range(len(thumbs)))
        idx = [i for i in idx if 0 <= i < len(thumbs)][:cols * 4]
        tw = 330
        th = int(thumbs[0].height * tw / thumbs[0].width)
        sheet = Image.new("RGB", (cols * tw, ((len(idx) + cols - 1) // cols) * th), (40, 0, 60))
        for k, i in enumerate(idx):
            sheet.paste(thumbs[i].resize((tw, th), Image.BILINEAR), ((k % cols) * tw, (k // cols) * th))
        sheet.save(os.path.join(OUT, tag + "-sheet.png"))
        print("      wrote out/verify/p4/%s-sheet.png (frames %s)" % (tag, idx), flush=True)
    return rows, thumbs


def report_cast(rows, tag):
    print("      %s: %d frames over %.2f s" % (tag, len(rows), rows[-1][0] if rows else 0))
    print("      t(s) mean sharp diff: " + "  ".join("%.2f/%.1f/%.1f/%.1f" % r for r in rows), flush=True)
    spikes = []
    for i in range(1, len(rows) - 1):
        a, b, c = rows[i - 1][1], rows[i][1], rows[i + 1][1]
        if (b - a) * (c - b) < 0 and min(abs(b - a), abs(c - b)) > 6:
            spikes.append((i, round(a, 1), round(b, 1), round(c, 1)))
    return spikes


def cam(d):
    return d.js("const c = %s.cam; return { yaw: c.yaw, pitch: c.pitch, dist: c.dist, target: c.target.slice() };" % L)


def trace_start(d, ms):
    d.js("window.__tr = []; window.__trDone = false; const Lb = %s, t0 = performance.now(); const f = () => { window.__tr.push([performance.now() - t0, Lb.cam.dist, Lb.S.v2.h, Lb.S.v2.x, Lb.S.v2.y,"
         " parseFloat(document.getElementById('camThumb').style.top), window.scrollY, Lb.S.view.speed]); if (performance.now() - t0 < %d) requestAnimationFrame(f); else window.__trDone = true; }; requestAnimationFrame(f);" % (L, ms))


def trace_get(d):
    d.p.wait("window.__trDone", 30)
    return d.js("return window.__tr;")


def mono(vals, tol=1e-12):
    """(non-decreasing?, non-increasing?)"""
    up = all(b >= a - tol * max(1, abs(a)) for a, b in zip(vals, vals[1:]))
    dn = all(b <= a + tol * max(1, abs(a)) for a, b in zip(vals, vals[1:]))
    return up, dn


def reset(d):
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch(); window.scrollTo(0, 0);" % (L, L, L))
    d.settle()


def sec_a(d):
    """arcball: direction, notch size, adding up, trackpad, limits, page scroll, slider"""
    print("--- A: arcball wheel", flush=True)
    reset(d)
    cx, cy = d.at("#view")
    doc = d.js("return [document.documentElement.scrollHeight, innerHeight, scrollY];")
    print("      document height %s, window %s, scrollY %s; stage box %s" % (doc[0], doc[1], doc[2], d.box("#stage")))
    d.mouse("mouseMoved", cx, cy)
    d.js("window.__ev = []; document.getElementById('view').addEventListener('wheel', e => window.__ev.push([e.deltaY, e.deltaMode, e.defaultPrevented, e.ctrlKey]));")
    d0 = cam(d)["dist"]
    top0 = d.js("return [document.getElementById('camThumb').style.top, document.getElementById('camVal').textContent];")
    trace_start(d, 900)
    d.wheel(cx, cy, -100)
    tr = trace_get(d); d.settle()
    d1 = cam(d)["dist"]
    ev = d.js("return window.__ev;")
    ok("wheel up (deltaY %s) moves IN, by one 12%% notch" % ev[0][0], abs(d1 * N12 / d0 - 1) < 1e-9, "%.4f -> %.4f ratio %.5f" % (d0, d1, d1 / d0))
    ds = [r[1] for r in tr]
    moving = sum(1 for a, b in zip(ds, ds[1:]) if a != b)
    ok("one notch is eased over several frames and never passes its goal", mono(ds)[1] and min(ds) >= d1 - 1e-12 and moving >= 3, "%d moving frames, min %.5f goal %.5f" % (moving, min(ds), d1))
    t_done = next((r[0] for r in tr if r[1] == d1), None)
    t_first = next((r[0] for r in tr if r[1] != d0), None)
    print("      one notch: first change at %.0f ms, goal reached at %s ms after trace start" % (t_first or -1, t_done))
    top1 = d.js("return [document.getElementById('camThumb').style.top, document.getElementById('camVal').textContent, document.getElementById('camRail').getAttribute('aria-valuetext')];")
    wantT = math.log(d1 / 0.005) / math.log(60 / 0.005) * 100
    ok("the zoom slider follows the wheel (thumb and value label)", abs(float(top1[0].rstrip('%')) - wantT) < 0.02 and top1[0] != top0[0] and top1[1] != top0[1], (top0, top1, wantT))
    tops = [r[5] for r in tr]
    ok("the slider thumb moves along with the easing, frame by frame, one way only", mono(tops)[1] and len(set(tops)) >= 3, "%d distinct positions" % len(set(tops)))

    # wheel down = out
    d.wheel(cx, cy, 100); d.settle()
    ok("wheel down moves OUT by the same notch (back to the start exactly)", abs(cam(d)["dist"] / d0 - 1) < 1e-9, cam(d)["dist"])

    # five notches at a human pace
    reset(d); d.mouse("mouseMoved", cx, cy)
    trace_start(d, 1800)
    for _ in range(5):
        d.wheel(cx, cy, 100); time.sleep(0.07)
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    ok("five notches out add up to 1.12^5 = 1.762", abs(cam(d)["dist"] / d0 / N12 ** 5 - 1) < 1e-9, cam(d)["dist"] / d0)
    steps = [(b - a) / (d0 * (N12 ** 5 - 1)) for a, b in zip(ds, ds[1:])]
    ok("five notches: no overshoot, no step back", mono(ds)[0] and max(ds) <= d0 * N12 ** 5 * (1 + 1e-12), "largest single frame %.1f%% of the whole change, %d moving frames" % (100 * max(steps), sum(1 for s in steps if s > 1e-9)))
    gaps = [b[0] - a[0] for a, b in zip(tr, tr[1:])]
    print("      frame gaps (loaded GPU): median %.1f ms longest %.1f ms" % (sorted(gaps)[len(gaps) // 2], max(gaps)))

    # a fast flick: 20 notches with no pause
    reset(d); d.mouse("mouseMoved", cx, cy)
    trace_start(d, 1800)
    for _ in range(20):
        d.wheel(cx, cy, -100)
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    want = d0 / N12 ** 20
    ok("a fast flick of 20 notches in lands on 1/1.12^20 (%.4f) with no overshoot" % want, abs(cam(d)["dist"] / want - 1) < 1e-9 and mono(ds)[1] and min(ds) >= want * (1 - 1e-12), (cam(d)["dist"], min(ds)))

    # in then straight back out
    reset(d); d.mouse("mouseMoved", cx, cy)
    for _ in range(6):
        d.wheel(cx, cy, -100)
    for _ in range(6):
        d.wheel(cx, cy, 100)
    d.settle()
    ok("six in then six out returns exactly to the start", abs(cam(d)["dist"] / d0 - 1) < 1e-9, cam(d)["dist"])

    # trackpad: a stream of tiny pixel deltas
    reset(d); d.mouse("mouseMoved", cx, cy)
    trace_start(d, 2200)
    for _ in range(60):
        d.wheel(cx, cy, -4); time.sleep(0.012)
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    want = d0 * math.exp(-240 * math.log(N12) / 100)
    rel = [abs(math.log(b / a)) for a, b in zip(ds, ds[1:]) if a != b]
    ok("trackpad stream (60 x 4 px) adds up to the same as 2.4 notches (x%.4f) and is monotone" % (want / d0), abs(cam(d)["dist"] / want - 1) < 1e-9 and mono(ds)[1], "dist %.4f; %d moving frames; largest frame step %.2f%%, median %.2f%%" % (cam(d)["dist"], len(rel), 100 * max(rel), 100 * sorted(rel)[len(rel) // 2]))
    # fractional deltas (precision trackpads send them)
    reset(d); d.mouse("mouseMoved", cx, cy)
    for _ in range(40):
        d.wheel(cx, cy, 0.5)
    d.settle()
    ok("fractional deltas (40 x 0.5 px) are not lost", abs(cam(d)["dist"] / (d0 * math.exp(20 * math.log(N12) / 100)) - 1) < 1e-6, cam(d)["dist"] / d0)
    # a trackpad pinch = ctrl + wheel
    reset(d); d.mouse("mouseMoved", cx, cy)
    d.js("window.__ev = [];")
    dpr0 = d.js("return [devicePixelRatio, visualViewport.scale, innerWidth];")
    for _ in range(10):
        d.wheel(cx, cy, -5, modifiers=2); time.sleep(0.012)
    d.settle()
    ev = d.js("return window.__ev;")
    want = d0 * math.exp(-400 * math.log(N12) / 100)
    ok("trackpad pinch (ctrl+wheel, 10 x -5) zooms in x%.3f and the browser's own zoom stays put" % (want / d0),
       abs(cam(d)["dist"] / want - 1) < 1e-6 and d.js("return [devicePixelRatio, visualViewport.scale, innerWidth];") == dpr0 and all(e[2] for e in ev), (cam(d)["dist"] / d0, ev[:2]))
    # deltaMode = 1 lines cannot be sent through CDP; a big-delta mouse (e.g. 3 notches in one event)
    reset(d); d.mouse("mouseMoved", cx, cy)
    d.wheel(cx, cy, 240); d.settle()
    print("      one event of deltaY 240 gives x%.4f (2.4 notches would be %.4f)" % (cam(d)["dist"] / d0, N12 ** 2.4))
    d.wheel(cx, cy, 1200); d.settle()
    print("      then one event of deltaY 1200 gives x%.4f in total (clamped at 3 notches per event: %.4f)" % (cam(d)["dist"] / d0, N12 ** 5.4))

    # near limit
    reset(d); d.mouse("mouseMoved", cx, cy)
    trace_start(d, 2500)
    for _ in range(80):
        d.wheel(cx, cy, -300)
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    ok("zooming in hard stops exactly at the near limit 0.005, with no bounce", cam(d)["dist"] == 0.005 and mono(ds)[1] and min(ds) >= 0.005, (cam(d)["dist"], min(ds)))
    for _ in range(5):
        d.wheel(cx, cy, -100)
    time.sleep(0.3)
    g = d.js("return [%s.CV.goal, %s.CV.raf, %s.cam.dist];" % (L, L, L))
    ok("more wheel at the near limit does nothing and leaves nothing running", g[0] is None and g[2] == 0.005, g)
    d.wheel(cx, cy, 100); d.settle()
    ok("one notch back out from the near limit answers at once (no dead zone)", abs(cam(d)["dist"] / (0.005 * N12) - 1) < 1e-9, cam(d)["dist"])
    thumb = d.js("return document.getElementById('camThumb').style.top;")
    print("      thumb at near limit + 1 notch: %s" % thumb)
    # far limit
    trace_start(d, 2500)
    for _ in range(100):
        d.wheel(cx, cy, 300)
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    ok("zooming out hard stops exactly at the far limit 60, with no bounce", cam(d)["dist"] == 60 and mono(ds)[0] and max(ds) <= 60, (cam(d)["dist"], max(ds)))
    ok("thumb sits at the bottom end at the far limit", d.js("return document.getElementById('camThumb').style.top;") == "100.00%", d.js("return document.getElementById('camThumb').style.top;"))
    d.wheel(cx, cy, -100); d.settle()
    ok("one notch back in from the far limit answers at once", abs(cam(d)["dist"] / (60 / N12) - 1) < 1e-9, cam(d)["dist"])
    ok("the page itself never scrolled during all of this", d.js("return window.scrollY;") == 0, d.js("return window.scrollY;"))
    ev = d.js("return window.__ev;")

    # the wheel over things that sit on top of the picture
    reset(d)
    for sel in ["#zoomIn", "#zoomOut", "#reset", "#camArc", "#camFly", "#camNear", "#camFar", "#camRail", "#camEndA", ".hint", "#triad", "#camVal"]:
        try:
            d.js("window.scrollTo(0, 0);")
            x, y = d.at(sel)
            what = d.js("const e = document.elementFromPoint(%f, %f); return e ? (e.id || e.className || e.tagName) : null;" % (x, y))
            a = cam(d)["dist"]
            d.mouse("mouseMoved", x, y)
            for _ in range(3):
                d.wheel(x, y, 100); time.sleep(0.05)
            time.sleep(0.5); d.settle()
            sy = d.js("return window.scrollY;")
            b = cam(d)["dist"]
            ok("wheel with the pointer on %s (hits %s): picture zooms, page stays" % (sel, what), sy == 0 and abs(b / a / N12 ** 3 - 1) < 1e-6, "scrollY %s, dist x%.4f" % (sy, b / a))
        except Exception as e:
            print("      (skip %s: %s)" % (sel, e))
    d.js("window.scrollTo(0, 0);")


def sec_b(d):
    """buttons and keys against the wheel"""
    print("--- B: + and - buttons, keys", flush=True)
    reset(d)
    d0 = cam(d)["dist"]
    trace_start(d, 900)
    d.click("#zoomIn")
    tr = trace_get(d); d.settle()
    ds = [r[1] for r in tr]
    r1 = cam(d)["dist"] / d0
    ok("the + button moves in, eased, no overshoot", r1 < 1 and mono(ds)[1] and len(set(ds)) >= 4, "x%.4f = %.2f wheel notches" % (r1, -math.log(r1) / math.log(N12)))
    d.click("#zoomOut"); d.settle()
    ok("the - button undoes the + button exactly", abs(cam(d)["dist"] / d0 - 1) < 1e-9, cam(d)["dist"] / d0)
    for _ in range(5):
        d.click("#zoomIn")
    d.settle()
    ok("five quick + clicks add up (0.8^5)", abs(cam(d)["dist"] / d0 / 0.8 ** 5 - 1) < 1e-9, cam(d)["dist"] / d0)
    reset(d)
    cx, cy = d.at("#view")
    d.js("document.getElementById('view').focus({preventScroll: true});")
    d.p.call("Input.dispatchKeyEvent", type="keyDown", key="+", code="Equal", windowsVirtualKeyCode=187, modifiers=8, text="+")
    d.p.call("Input.dispatchKeyEvent", type="keyUp", key="+", code="Equal", windowsVirtualKeyCode=187, modifiers=8)
    d.settle()
    rk = cam(d)["dist"] / d0
    d.p.call("Input.dispatchKeyEvent", type="keyDown", key="-", code="Minus", windowsVirtualKeyCode=189, text="-")
    d.p.call("Input.dispatchKeyEvent", type="keyUp", key="-", code="Minus", windowsVirtualKeyCode=189)
    d.settle()
    ok("the + key moves in and the - key undoes it", rk < 1 and abs(cam(d)["dist"] / d0 - 1) < 1e-9, "+ key x%.4f" % rk)
    print("      step sizes: wheel notch x%.4f, + button x%.4f, + key x%.4f" % (1 / N12, r1, rk))
    ok("the + key and the + button take the same step", abs(rk - r1) < 1e-9, "button x%.3f, key x%.3f" % (r1, rk))
    # button at the limits
    d.js("%s.cam.dist = 0.0055; %s.touch();" % (L, L)); d.settle()
    trace_start(d, 800)
    d.click("#zoomIn")
    tr = trace_get(d); d.settle()
    ok("+ near the limit stops on the limit, no bounce", cam(d)["dist"] == 0.005 and mono([r[1] for r in tr])[1], cam(d)["dist"])
    # wheel then button while still easing
    reset(d)
    d.mouse("mouseMoved", cx, cy)
    d.wheel(cx, cy, -100); d.click("#zoomIn"); d.settle()
    ok("a wheel notch and a + click in quick succession multiply (no lost or doubled step)", abs(cam(d)["dist"] / d0 / (0.8 / N12) - 1) < 1e-9, cam(d)["dist"] / d0)


def sec_c(d):
    """fly mode"""
    print("--- C: fly mode", flush=True)
    reset(d)
    cx, cy = d.at("#view")
    d.click("#camFly"); time.sleep(0.3)
    st = d.js("return [%s.S.view.fly, %s.S.view.speed, document.querySelector('.hint').textContent, document.getElementById('camVal').textContent, document.getElementById('camEndA').textContent, document.getElementById('camEndB').textContent];" % (L, L))
    print("      fly: %s" % st)
    e0 = d.js("return %s.basis().pos;" % L); c0 = cam(d); s0 = st[1]
    d.mouse("mouseMoved", cx, cy)
    top0 = d.js("return document.getElementById('camThumb').style.top;")
    d.wheel(cx, cy, -100); time.sleep(0.4); d.settle()
    s1 = d.js("return %s.S.view.speed;" % L)
    e1 = d.js("return %s.basis().pos;" % L)
    top1 = d.js("return document.getElementById('camThumb').style.top;")
    ok("fly: wheel up changes the speed by 12% (faster) and does not move the camera", abs(s1 / s0 / N12 - 1) < 1e-9 and e1 == e0 and cam(d)["dist"] == c0["dist"], (s0, s1))
    ok("fly: the slider (now speed) follows, moving up for faster", float(top1.rstrip('%')) < float(top0.rstrip('%')), (top0, top1))
    ok("fly: the page does not scroll", d.js("return window.scrollY;") == 0)
    for _ in range(200):
        d.wheel(cx, cy, -300)
    time.sleep(0.3)
    sHi = d.js("return %s.S.view.speed;" % L)
    for _ in range(300):
        d.wheel(cx, cy, 300)
    time.sleep(0.3)
    sLo = d.js("return %s.S.view.speed;" % L)
    ok("fly: speed stops cleanly at both ends (100 and 0.001)", sHi == 100 and sLo == 0.001, (sHi, sLo))
    d.js("%s.S.view.speed = 1; %s.viewChanged();" % (L, L))
    e0 = d.js("return %s.basis();" % L)
    trace_start(d, 800)
    d.click("#zoomIn")
    trace_get(d); d.settle()
    e1 = d.js("return %s.basis();" % L)
    fwd = sum((a - b) * f for a, b, f in zip(e1["pos"], e0["pos"], e0["f"]))
    ok("fly: the + button moves the camera forward along its view", fwd > 0.1, "forward %.4f units at speed 1" % fwd)
    d.click("#zoomOut"); d.settle()
    e2 = d.js("return %s.basis();" % L)
    back = sum((a - b) * f for a, b, f in zip(e2["pos"], e0["pos"], e0["f"]))
    ok("fly: the - button moves back by the same amount", abs(back) < 1e-6, back)
    d.idle(120)
    d.shot("c-fly.png")
    d.click("#camArc"); time.sleep(0.3)
    reset(d)


def flat_pt(d, px, py):
    return d.js("const r = document.getElementById('view').getBoundingClientRect(), h = r.height, v = %s.S.v2; const u = [(2 * %f - r.width) / h, (h - 2 * %f) / h]; return [v.x + u[0] * v.h / 2, v.y + u[1] * v.h / 2, v.h];" % (L, px, py))


def sec_d(d, cast):
    """2D view"""
    print("--- D: 2D view", flush=True)
    reset(d)
    d.js("const f = document.getElementById('flat'); if (!f.checked) f.click();")
    time.sleep(0.5); d.settle()
    st = d.js("return [%s.S.flat, %s.S.v2, document.querySelector('.hint').textContent];" % (L, L))
    print("      2D: %s" % st)
    b = d.box("#view")
    px, py = b[2] * 0.3, b[3] * 0.35           # canvas-relative
    mx, my = b[0] + px, b[1] + py
    d.mouse("mouseMoved", mx, my)
    d.idle(120)
    p0 = flat_pt(d, px, py)
    pk0 = d.js("return %s.pick(%f, %f);" % (L, px, py))
    d.shot("d-2d-before.png")
    d.js("window.__fp = []; window.__fpOn = true; const Lb = %s; const f = () => { const r = document.getElementById('view').getBoundingClientRect(), h = r.height, v = Lb.S.v2, u = [(2 * %f - r.width) / h, (h - 2 * %f) / h];"
         " window.__fp.push([v.x + u[0] * v.h / 2, v.y + u[1] * v.h / 2, v.h]); if (window.__fpOn) requestAnimationFrame(f); }; requestAnimationFrame(f);" % (L, px, py))
    for _ in range(8):
        d.wheel(mx, my, -100); time.sleep(0.06)
    d.settle(); time.sleep(0.2)
    d.js("window.__fpOn = false;")
    fp = d.js("return window.__fp;")
    p1 = flat_pt(d, px, py)
    drift = max(math.hypot(q[0] - p0[0], q[1] - p0[1]) / q[2] * b[3] for q in fp)
    hs = [q[2] for q in fp]
    ok("2D: wheel up zooms IN by 12% a notch (8 notches)", abs(p1[2] / p0[2] * N12 ** 8 - 1) < 1e-9, p1[2] / p0[2])
    ok("2D: the point under the cursor stays put on every frame of the zoom", drift < 0.5, "largest drift %.4f px over %d frames" % (drift, len(fp)))
    ok("2D: eased, monotone, no overshoot", mono(hs)[1] and len(set(hs)) >= 6, len(set(hs)))
    d.idle(120)
    pk1 = d.js("return %s.pick(%f, %f);" % (L, px, py))
    print("      pick under the cursor before %s after %s" % (pk0, pk1))
    if pk0 and pk1:
        ok("2D: the renderer agrees (pick at the cursor returns the same slice point before and after)", math.hypot(pk0[0] - pk1[0], pk0[1] - pk1[1]) < 2 * p0[2] / b[3], (pk0, pk1))
    d.shot("d-2d-after8in.png")
    top = d.js("return [document.getElementById('camThumb').style.top, document.getElementById('camVal').textContent, document.getElementById('camNear').value, document.getElementById('camFar').value];")
    lim = d.js("return [%s.S.v2.hmin, %s.S.v2.hmax];" % (L, L))
    wantT = math.log(p1[2] / lim[0]) / math.log(lim[1] / lim[0]) * 100
    ok("2D: the zoom slider follows the wheel", abs(float(top[0].rstrip('%')) - wantT) < 0.02, (top, wantT))
    # move the cursor elsewhere and zoom out: the new point must hold
    px2, py2 = b[2] * 0.7, b[3] * 0.6
    d.mouse("mouseMoved", b[0] + px2, b[1] + py2)
    q0 = flat_pt(d, px2, py2)
    for _ in range(4):
        d.wheel(b[0] + px2, b[1] + py2, 100)
    d.settle()
    q1 = flat_pt(d, px2, py2)
    ok("2D: zooming out about another spot holds that spot", math.hypot(q1[0] - q0[0], q1[1] - q0[1]) / q1[2] * b[3] < 0.5 and abs(q1[2] / q0[2] / N12 ** 4 - 1) < 1e-9, (q0, q1))
    # buttons in 2D zoom about the centre
    c0 = d.js("return [%s.S.v2.x, %s.S.v2.y, %s.S.v2.h];" % (L, L, L))
    d.click("#zoomIn"); d.settle()
    c1 = d.js("return [%s.S.v2.x, %s.S.v2.y, %s.S.v2.h];" % (L, L, L))
    ok("2D: the + button zooms in about the centre", c1[2] < c0[2] and c1[0] == c0[0] and c1[1] == c0[1], (c0, c1))
    d.click("#zoomOut"); d.settle()
    # limits
    d.mouse("mouseMoved", mx, my)
    a0 = flat_pt(d, px, py)
    d.js("window.__fp = []; window.__fpOn = true; const Lb = %s; const f = () => { const v = Lb.S.v2; window.__fp.push([v.x, v.y, v.h]); if (window.__fpOn) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    for _ in range(120):
        d.wheel(mx, my, -300)
    d.settle(); time.sleep(0.2)
    d.js("window.__fpOn = false;")
    hs = [q[2] for q in d.js("return window.__fp;")]
    a1 = flat_pt(d, px, py)
    ok("2D: zooming in stops exactly at the smallest height, no bounce", a1[2] == lim[0] and mono(hs)[1] and min(hs) >= lim[0], (a1[2], lim[0]))
    ok("2D: the cursor point is still held at the limit", math.hypot(a1[0] - a0[0], a1[1] - a0[1]) / a1[2] * b[3] < 1.0, "drift %.3f px" % (math.hypot(a1[0] - a0[0], a1[1] - a0[1]) / a1[2] * b[3]))
    xy0 = d.js("return [%s.S.v2.x, %s.S.v2.y];" % (L, L))
    for _ in range(5):
        d.wheel(mx, my, -100)
    time.sleep(0.3); d.settle()
    xy1 = d.js("return [%s.S.v2.x, %s.S.v2.y];" % (L, L))
    ok("2D: more wheel at the limit does not slide the picture", xy0 == xy1, (xy0, xy1))
    d.idle(120); d.shot("d-2d-nearlimit.png")
    d.js("window.__fp = []; window.__fpOn = true; const Lb = %s; const f = () => { const v = Lb.S.v2; window.__fp.push([v.x, v.y, v.h]); if (window.__fpOn) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    for _ in range(140):
        d.wheel(mx, my, 300)
    d.settle(); time.sleep(0.2)
    d.js("window.__fpOn = false;")
    hs = [q[2] for q in d.js("return window.__fp;")]
    a2 = flat_pt(d, px, py)
    ok("2D: zooming out stops exactly at the largest height, no bounce", a2[2] == lim[1] and mono(hs)[0] and max(hs) <= lim[1], (a2[2], lim[1]))
    ok("2D: the page did not scroll", d.js("return window.scrollY;") == 0)
    d.idle(120); d.shot("d-2d-farlimit.png")
    # flicker in 2D
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle(); d.idle(120)
    box = d.box("#stage")
    cast.start(); d.pump(0.3)
    for _ in range(24):
        d.wheel(mx, my, -100); d.pump(0.08)
    d.pump(1.2)
    fr = cast.stop()
    rows, _ = analyse(fr, box, "d-2d-cast", pick=list(range(max(0, len(fr) // 2 - 9), len(fr) // 2 + 9)))
    sp = report_cast(rows, "2D zoom")
    ok("2D: no brightness flash between frames during a zoom (screencast)", not sp, sp)
    d.js("const f = document.getElementById('flat'); if (f.checked) f.click();")
    time.sleep(0.4); reset(d)


def sec_e(d, cast):
    """preview flicker in 3D"""
    print("--- E: preview frames during a 3D zoom", flush=True)
    reset(d); d.idle(180)
    cx, cy = d.at("#view")
    box = d.box("#stage")
    d.mouse("mouseMoved", cx, cy)
    d.js("window.__st = []; window.__stOn = true; const f = () => { const R = %s.R; window.__st.push([Math.round(performance.now()), document.getElementById('status').textContent, R.shown, R.ps]); if (window.__stOn) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    cast.start(); d.pump(0.3)
    for _ in range(24):
        d.wheel(cx, cy, -100); d.pump(0.09)
    d.pump(1.5)
    fr = cast.stop()
    rows, _ = analyse(fr, box, "e-3d-cast", pick=list(range(max(0, len(fr) // 2 - 9), len(fr) // 2 + 9)))
    sp = report_cast(rows, "3D steady zoom in (24 notches, 90 ms apart)")
    ok("3D: no brightness flash between frames during a steady zoom (screencast)", not sp, sp)
    # slow scrolling: one notch every 0.4 s, where the full-size drawing starts between notches
    reset(d); d.idle(180)
    d.mouse("mouseMoved", cx, cy)
    cast.start(); d.pump(0.3)
    for _ in range(7):
        d.wheel(cx, cy, -100); d.pump(0.45)
    d.pump(0.5)
    fr = cast.stop()
    rows, _ = analyse(fr, box, "e-3d-slow-cast", pick=list(range(max(0, len(fr) // 2 - 12), len(fr) // 2 + 12)))
    sp = report_cast(rows, "3D slow zoom (7 notches, 450 ms apart)")
    ok("3D: no brightness flash during slow notch-by-notch zooming (screencast)", not sp, sp)
    d.js("window.__stOn = false;")
    st = d.js("return window.__st;")
    seq = []
    for t, s, shown, ps in st:
        if not seq or seq[-1][1] != s or seq[-1][2] != shown:
            seq.append((t, s, shown, round(ps, 3)))
    print("      status / shown sequence (%d changes): %s" % (len(seq), seq[:60]))
    d.idle(180)
    d.shot("e-3d-after.png")


def sec_f(d, page):
    """touch: pinch"""
    print("--- F: pinch (touch)", flush=True)
    page.call("Emulation.setDeviceMetricsOverride", width=820, height=1100, deviceScaleFactor=1, mobile=True)
    page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    d.load(PAGE)
    d.js("%s.resetCam(); %s.touch(); document.getElementById('stage').scrollIntoView({block: 'center'});" % (L, L))
    time.sleep(0.4)
    cx, cy = d.at("#view")
    sy = d.js("return [window.scrollY, visualViewport.scale];")
    c0 = cam(d)
    d.js("window.__tr2 = []; window.__on = true; const Lb = %s; const f = () => { window.__tr2.push(Lb.cam.dist); if (window.__on) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    d.touch("touchStart", [(cx - 50, cy), (cx + 50, cy)])
    for i in range(1, 11):
        d.touch("touchMove", [(cx - 50 - 5 * i, cy), (cx + 50 + 5 * i, cy)])
    time.sleep(0.15)
    c1 = cam(d)
    ok("pinch: spreading two fingers to twice the gap halves the distance (moves in)", abs(c1["dist"] / c0["dist"] - 0.5) < 1e-6, c1["dist"] / c0["dist"])
    for i in range(1, 11):
        d.touch("touchMove", [(cx - 100 + 5 * i, cy), (cx + 100 - 5 * i, cy)])
    d.lift(); time.sleep(0.15)
    d.js("window.__on = false;")
    c2 = cam(d)
    tr = d.js("return window.__tr2;")
    k = tr.index(min(tr))
    ok("pinch: closing the fingers again returns to the start, smoothly in both directions", abs(c2["dist"] / c0["dist"] - 1) < 1e-6 and mono(tr[:k + 1])[1] and mono(tr[k:])[0], (c2["dist"] / c0["dist"], len(set(tr))))
    ok("pinch: the page neither scrolled nor zoomed", d.js("return [window.scrollY, visualViewport.scale];") == sy, (sy, d.js("return [window.scrollY, visualViewport.scale];")))
    # pinch hard into the near limit
    d.js("%s.cam.dist = 0.02; %s.touch();" % (L, L)); time.sleep(0.2)
    d.touch("touchStart", [(cx - 20, cy), (cx + 20, cy)])
    for i in range(1, 11):
        d.touch("touchMove", [(cx - 20 - 20 * i, cy), (cx + 20 + 20 * i, cy)])
    time.sleep(0.15)
    at_lim = cam(d)["dist"]
    for i in range(1, 4):
        d.touch("touchMove", [(cx - 220 + 20 * i, cy), (cx + 220 - 20 * i, cy)])
    time.sleep(0.15)
    back = cam(d)["dist"]
    d.lift()
    ok("pinch: stops at the near limit", at_lim == 0.005, at_lim)
    print("      after closing the fingers a little from the limit (gap 440 -> 320): dist %.5f (x%.3f)" % (back, back / at_lim))
    ok("pinch: no finger left registered", d.js("return %s.CV.ptr.size;" % L) == 0)
    # 2D pinch about the midpoint
    d.js("%s.resetCam(); const f = document.getElementById('flat'); if (!f.checked) f.click();" % L)
    time.sleep(0.6)
    b = d.box("#view")
    mxp, myp = b[2] * 0.35, b[3] * 0.4
    X, Y = b[0] + mxp, b[1] + myp
    p0 = flat_pt(d, mxp, myp)
    d.touch("touchStart", [(X - 40, Y), (X + 40, Y)])
    for i in range(1, 9):
        d.touch("touchMove", [(X - 40 - 5 * i, Y), (X + 40 + 5 * i, Y)])
    time.sleep(0.15)
    p1 = flat_pt(d, mxp, myp)
    d.lift()
    ok("2D pinch: spreading to twice the gap halves the height and holds the spot between the fingers",
       abs(p1[2] / p0[2] - 0.5) < 1e-6 and math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / p1[2] * b[3] < 1.0, (p1[2] / p0[2], math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / p1[2] * b[3]))
    d.idle(120)
    d.shot("f-touch-2d.png")
    d.js("const f = document.getElementById('flat'); if (f.checked) f.click();")
    # fly pinch
    d.js("%s.resetCam(); %s.setCamMode(true); %s.S.view.speed = 1; %s.touch();" % (L, L, L, L)); time.sleep(0.3)
    e0 = d.js("return %s.basis();" % L)
    d.touch("touchStart", [(cx - 50, cy), (cx + 50, cy)])
    for i in range(1, 11):
        d.touch("touchMove", [(cx - 50 - 5 * i, cy), (cx + 50 + 5 * i, cy)])
    d.lift()
    e1 = d.js("return %s.basis();" % L)
    fwd = sum((a - b2) * f for a, b2, f in zip(e1["pos"], e0["pos"], e0["f"]))
    ok("fly pinch: spreading the fingers moves forward", fwd > 0.5, fwd)
    d.js("%s.setCamMode(false);" % L)


def main():
    global VW
    want = set("".join(sys.argv[1:]) or "abcdef")
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("No Chrome or Edge found.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p4zoom-")
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
        VW = 1400
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        cast = Cast(page)
        d = Drive(page)
        d.load(PAGE)
        for key, fn in (("a", lambda: sec_a(d)), ("b", lambda: sec_b(d)), ("c", lambda: sec_c(d)), ("d", lambda: sec_d(d, cast)), ("e", lambda: sec_e(d, cast)), ("f", lambda: sec_f(d, page))):
            if key in want:
                try:
                    fn()
                except Exception:
                    print("ERROR in section %s:\n%s" % (key, traceback.format_exc()), flush=True)
                    results.append((False, "section %s raised" % key))
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
    bad = [n for g, n in results if not g]
    print("%d passed, %d failed" % (len(results) - len(bad), len(bad)))
    for n in bad:
        print("   failed: " + n)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    main()
