"""Tester "camera", second check: REAL input on dist/v8.html (after notes/camera_real.py).

  python out/t9/camera/real.py desk     desktop 1400 x 950: wheel, drag, keys, fly, slider, limit boxes, double-click, Tab, 2D view
  python out/t9/camera/real.py phone    emulated phone 375 x 812 with touch: zoom row, boxes, pinch, switch
"""
import json, math, sys, time
from rig import Rig, L, ok, info, tally

PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
PAGE = "dist/v8.html"


def cam(d):
    return d.js("const c = %s.cam; return { yaw: c.yaw, pitch: c.pitch, dist: c.dist, target: c.target.slice() };" % L)


def eye(d):
    return d.js("const b = %s.basis(); return { pos: b.pos, f: b.f, right: b.right };" % L)


def dot(a, b): return sum(x * y for x, y in zip(a, b))
def sub(a, b): return [x - y for x, y in zip(a, b)]
def norm(a): return dot(a, a) ** 0.5
def note(d): return d.js("const n = document.getElementById('camNote'); return n.hidden ? '' : n.textContent;")
def view(d): return d.js(PRE + "return { zmin: S.view.zmin, zmax: S.view.zmax, fly: S.view.fly, speed: S.view.speed, flat: S.flat, v2: [S.v2.x, S.v2.y, S.v2.h], hmin: S.v2.hmin, hmax: S.v2.hmax };")


def desktop(d):
    d.load(PAGE)
    d.js("window.scrollTo(0, 0);")
    d.settle()
    c00 = cam(d)
    info("start view", c00)
    cx, cy = d.at("#view")
    info("stage box", d.box("#stage"))

    # ----- the wheel
    d.mouse("mouseMoved", cx, cy)
    d.js("window.__tr = []; window.__ev = []; document.getElementById('view').addEventListener('wheel', e => window.__ev.push([e.deltaY, e.deltaMode, e.defaultPrevented]));"
         "const t0 = performance.now(); const f = () => { window.__tr.push([performance.now() - t0, %s.cam.dist]); if (performance.now() - t0 < 2500) requestAnimationFrame(f); }; requestAnimationFrame(f);" % L)
    y_before = d.js("return window.scrollY;")
    for _ in range(5):
        d.wheel(cx, cy, 100)
        time.sleep(0.06)
    time.sleep(2.7)
    d.settle()
    tr, ev = d.js("return window.__tr;"), d.js("return window.__ev;")
    dist = cam(d)["dist"]
    ok("five real wheel notches zoom out by 1.12^5", abs(dist / c00["dist"] - 1.12 ** 5) < 1e-6, dist / c00["dist"])
    ok("the page itself did not scroll under the wheel", d.js("return window.scrollY;") == y_before)
    steps = [(b[1] - a[1]) / (c00["dist"] * (1.12 ** 5 - 1)) for a, b in zip(tr, tr[1:])]
    moving = [s for s in steps if s > 1e-6]
    gaps = [b[0] - a[0] for a, b in zip(tr, tr[1:])]
    info("wheel glide", "%d moving frames, largest single step %.1f%% of the whole change, never backwards %s; frame gaps median %.0f ms, longest %.0f ms" % (
        len(moving), 100 * max(steps), min(steps) >= 0, sorted(gaps)[len(gaps) // 2], max(gaps)))
    ok("the wheel zoom glides (several frames, never backwards)", len(moving) >= 6 and min(steps) >= -1e-9, len(moving))
    # wheel over the controls on the picture must not scroll the page either
    zx, zy = d.at("#camRail")
    d.wheel(zx, zy, 100); time.sleep(0.5); d.settle()
    ok("the wheel over the zoom slider zooms and does not scroll the page", cam(d)["dist"] > dist * 1.1 and d.js("return window.scrollY;") == y_before, (cam(d)["dist"] / dist, d.js("return window.scrollY;")))
    d.click("#reset"); d.settle(); d.done()
    c0 = cam(d)
    ok("a real click on Reset view puts the start view back", abs(c0["dist"] - c00["dist"]) < 1e-9 and abs(c0["yaw"] - c00["yaw"]) < 1e-9 and norm(sub(c0["target"], c00["target"])) < 1e-9, c0)

    # ----- a real drag that leaves the stage
    b = d.box("#view")
    d.drag(cx, cy, b[0] + b[2] + 150, cy + 40, steps=10)
    c1 = cam(d)
    want = c0["yaw"] - (b[0] + b[2] + 150 - cx) * 0.008
    ok("a real drag turns the camera and keeps turning outside the picture", abs(c1["yaw"] - want) < 1e-9 and abs(c1["pitch"] - (c0["pitch"] + 40 * 0.008)) < 1e-9, (c1["yaw"], want, c1["pitch"]))
    ok("the canvas took the keyboard focus on the press", d.js("return document.activeElement.id;") == "view")
    d.mouse("mouseMoved", cx + 80, cy)
    ok("moving the mouse with no button down does nothing", cam(d)["yaw"] == c1["yaw"])
    t0 = cam(d)["target"]
    d.drag(cx, cy, cx + 60, cy, modifiers=8)
    ok("shift-drag slides", norm(sub(cam(d)["target"], t0)) > 0.05 and cam(d)["yaw"] == c1["yaw"], norm(sub(cam(d)["target"], t0)))
    t0 = cam(d)["target"]
    d.drag(cx, cy, cx, cy + 60, button="right", buttons=2)
    ok("right-button drag slides", norm(sub(cam(d)["target"], t0)) > 0.05, norm(sub(cam(d)["target"], t0)))
    # a drag straight up past the pole: the pitch stops, the picture does not flip
    d.drag(cx, cy, cx, cy + 600, steps=12)
    ok("dragging far down stops at the pole (pitch held under 90 degrees)", abs(cam(d)["pitch"]) <= 1.5 + 1e-9, cam(d)["pitch"])

    # ----- real keys on the focused canvas
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    y0 = cam(d)["yaw"]
    d.press("ArrowLeft", 0.4)
    d.settle()
    ok("holding the left arrow turns the arcball", -1.2 < cam(d)["yaw"] - y0 < -0.15, cam(d)["yaw"] - y0)
    p0 = cam(d)["pitch"]
    d.press("ArrowUp", 0.3); d.settle()
    info("arrow up for 0.3 s changes the pitch by", cam(d)["pitch"] - p0)
    d0 = cam(d)["dist"]
    d.press("Equal"); time.sleep(0.6); d.settle()
    ok("the = (plus) key zooms in one step of 0.8", abs(cam(d)["dist"] / d0 - 0.8) < 1e-6, cam(d)["dist"] / d0)
    d.press("Minus"); time.sleep(0.6); d.settle()
    ok("the minus key zooms back out", abs(cam(d)["dist"] / d0 - 1) < 1e-6, cam(d)["dist"] / d0)
    d.click("#zoomIn"); time.sleep(0.6); d.settle()
    ok("a real click on Zoom in moves in by 0.8", abs(cam(d)["dist"] / d0 - 0.8) < 1e-6, cam(d)["dist"] / d0)
    ok("and the keyboard is back on the picture", d.js("return document.activeElement.id;") == "view")
    d.click("#zoomOut"); time.sleep(0.6); d.settle()
    ok("Zoom out undoes it", abs(cam(d)["dist"] / d0 - 1) < 1e-6, cam(d)["dist"] / d0)

    # ----- the camera switch, then flying
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    e0 = eye(d)
    d.click("#camFly")
    time.sleep(0.3)
    e1 = eye(d)
    ok("a real click on Fly switches the mode without moving the view", d.js("return %s.S.view.fly;" % L) is True and norm(sub(e0["pos"], e1["pos"])) < 1e-12 and norm(sub(e0["f"], e1["f"])) < 1e-12)
    ok("and hands the keyboard to the canvas", d.js("return document.activeElement.id;") == "view")
    info("fly: hint", d.js("return document.querySelector('.hint').textContent;"))
    info("fly: slider ends and boxes", d.js(PRE + "return [$('camEndA').textContent, $('camEndB').textContent, $('camNear').hidden, $('camFar').hidden, $('camVal').textContent, $('camRail').getAttribute('aria-label')];"))
    d.done()
    d.shot("real-desk-fly.png")
    y_before = d.js("return window.scrollY;")
    sp = d.js("return %s.S.view.speed;" % L)
    d.press("KeyW", 0.6)
    d.settle()
    e2 = eye(d)
    along = dot(sub(e2["pos"], e1["pos"]), e1["f"])
    ok("holding W for 0.6 s flies forward (speed %s)" % sp, 0.3 * sp < along < 1.2 * sp, along)
    d.press("Space", 0.3)
    d.settle()
    e3 = eye(d)
    ok("Space rises and does not scroll the page", e3["pos"][2] - e2["pos"][2] > 0.08 and d.js("return window.scrollY;") == y_before, e3["pos"][2] - e2["pos"][2])
    d.press("ShiftLeft", 0.3)
    d.settle()
    ok("Shift sinks", eye(d)["pos"][2] - e3["pos"][2] < -0.08, eye(d)["pos"][2] - e3["pos"][2])
    e3b = eye(d)
    d.press("KeyE", 0.3); d.settle()
    eE = eye(d)
    d.press("KeyQ", 0.3); d.settle()
    ok("E goes up and Q goes down", eE["pos"][2] - e3b["pos"][2] > 0.08 and eye(d)["pos"][2] - eE["pos"][2] < -0.08, (eE["pos"][2] - e3b["pos"][2], eye(d)["pos"][2] - eE["pos"][2]))
    before = eye(d)
    d.key_down("KeyD"); d.key_down("KeyW")
    time.sleep(0.4)
    d.key_up("KeyD"); d.key_up("KeyW")
    d.settle()
    e4 = eye(d)
    mv = sub(e4["pos"], before["pos"])
    time.sleep(0.2)
    ok("two keys at once move diagonally and everything stops on release",
       dot(mv, before["f"]) > 0.1 and dot(mv, before["right"]) > 0.1 and d.js("return %s.CV.keys.size;" % L) == 0 and norm(sub(eye(d)["pos"], e4["pos"])) == 0, mv)
    before = eye(d)
    d.press("ArrowUp", 0.3); d.settle()
    ok("the up arrow also flies forward", dot(sub(eye(d)["pos"], before["pos"]), before["f"]) > 0.08, dot(sub(eye(d)["pos"], before["pos"]), before["f"]))
    d.mouse("mouseMoved", cx, cy)
    d.wheel(cx, cy, -100)
    time.sleep(0.3)
    ok("a real wheel notch upward makes flying 12% faster", abs(d.js("return %s.S.view.speed;" % L) / sp - 1.12) < 1e-9, d.js("return %s.S.view.speed;" % L))
    d.wheel(cx, cy, 100); time.sleep(0.2)
    e5 = eye(d)
    d.drag(cx, cy, cx + 100, cy + 30)
    e6 = eye(d)
    ok("a real drag looks around from a fixed eye, to the right and down", norm(sub(e6["pos"], e5["pos"])) < 1e-9 and dot(e6["f"], e5["right"]) > 0.2 and e6["f"][2] < e5["f"][2])
    # the speed slider with a real mouse
    rb = d.box("#camRail")
    d.drag(rb[0] + rb[2] / 2, rb[1] + rb[3] * 0.5, rb[0] + rb[2] / 2, rb[1] + rb[3] * 0.25, steps=6); time.sleep(0.2)
    want = 0.001 * (100 / 0.001) ** 0.75
    ok("flying: dragging the slider up to a quarter from the top sets the speed there (fast at the top)", abs(d.js("return %s.S.view.speed;" % L) / want - 1) < 1e-6, (d.js("return %s.S.view.speed;" % L), want))
    info("fly speed dial in the panel after the slider moved", d.js(PRE + "await new Promise(r => setTimeout(r, 400)); const e = $('speedNum') || $('flySpeedNum') || document.querySelector('[id*=peed][type=number], [id*=peed][type=text]'); return e ? [e.id, e.value] : 'no speed box found';"))
    e6 = eye(d)
    d.click("#view")
    d.press("KeyF")
    time.sleep(0.3)
    e7 = eye(d)
    ok("F switches back to the arcball without moving the view", d.js("return %s.S.view.fly;" % L) is False and norm(sub(e7["pos"], e6["pos"])) < 1e-9 and norm(sub(e7["f"], e6["f"])) < 1e-9, (norm(sub(e7["pos"], e6["pos"])), norm(sub(e7["f"], e6["f"]))))
    d.click("#camFly"); time.sleep(0.2)
    d.click("#reset"); time.sleep(0.3); d.settle()
    cr = cam(d)
    ok("Reset view while flying puts the start view back and keeps the fly camera", abs(cr["dist"] - c00["dist"]) < 1e-9 and d.js("return %s.S.view.fly;" % L) is True, cr)
    d.click("#camArc"); time.sleep(0.3)

    # ----- the zoom slider and its limit boxes with a real mouse and keyboard
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    rb = d.box("#camRail")
    rx = rb[0] + rb[2] / 2
    d.drag(rx, rb[1] + rb[3] * 0.25, rx, rb[1] + rb[3] * 0.75, steps=12)
    time.sleep(0.6); d.settle()
    want = 0.005 * (60 / 0.005) ** 0.75
    ok("dragging the slider thumb zooms to where it is dropped", abs(cam(d)["dist"] / want - 1) < 1e-6, (cam(d)["dist"], want))
    ok("the rail took the focus, so its arrow keys work next", d.js("return document.activeElement.id;") == "camRail")
    d.press("ArrowUp")
    time.sleep(0.6); d.settle()
    ok("arrow up on the focused rail moves in by 2% of the rail", abs(cam(d)["dist"] / (0.005 * (60 / 0.005) ** 0.73) - 1) < 1e-6, cam(d)["dist"])
    d.press("PageDown"); time.sleep(0.6); d.settle()
    ok("Page Down on the rail moves out by 10% of the rail", abs(cam(d)["dist"] / (0.005 * (60 / 0.005) ** 0.83) - 1) < 1e-6, cam(d)["dist"])
    d.click("#camFar", count=3)
    d.text("200")
    ok("typing in the far box changes nothing yet", d.js("return %s.S.view.zmax;" % L) == 60)
    d.press("Tab")
    ok("leaving the box with Tab commits the far limit", d.js("return %s.S.view.zmax;" % L) == 200 and d.js("return document.getElementById('camFar').value;") == "200")
    d.click("#camNear", count=3)
    d.text("abc")
    d.press("Enter")
    ok("nonsense then Enter: the old near limit is back and the box is flagged",
       d.js("const e = document.getElementById('camNear'); return [e.value, e.getAttribute('aria-invalid'), %s.S.view.zmin];" % L) == ["0.005", "true", 0.005], note(d))
    info("note after nonsense", note(d))
    d.shot("real-desk-invalid-box.png")
    d.click("#camNear", count=3); d.text("150"); d.press("Enter")
    ok("near limit above half the far one is refused with a reason", d.js("return %s.S.view.zmin;" % L) == 0.005 and "at most half" in note(d), note(d))
    d.click("#camFar", count=3); d.text("0.006"); d.press("Enter")
    ok("far limit under twice the near one is refused with a reason", d.js("return %s.S.view.zmax;" % L) == 200 and "at least twice" in note(d), note(d))
    d.click("#camFar", count=3); d.text("5000"); d.press("Enter")
    info("far limit 5000 (hard range ends at 1000)", [d.js("return %s.S.view.zmax;" % L), note(d)])
    d.click("#camFar", count=3); d.text("-3"); d.press("Enter")
    info("far limit -3", [d.js("return %s.S.view.zmax;" % L), note(d)])
    d.click("#camFar", count=3); d.text("77"); d.press("Escape")
    ok("Escape in a box gives the old number back", d.js("return [document.getElementById('camFar').value, %s.S.view.zmax];" % L) == ["1000", 1000], d.js("return [document.getElementById('camFar').value, %s.S.view.zmax];" % L))
    d.click("#camNear", count=3)
    d.text("0,5")
    d.press("Enter")
    ok("0,5 then Enter sets the near limit to 0.5", d.js("return %s.S.view.zmin;" % L) == 0.5)
    d.mouse("mouseMoved", cx, cy)
    for _ in range(40):
        d.wheel(cx, cy, -300)
    time.sleep(0.8); d.settle()
    ok("the wheel then stops at the new near limit", cam(d)["dist"] == 0.5, cam(d)["dist"])
    d.wheel(cx, cy, -300); time.sleep(0.3)
    info("note at the nearest limit", note(d))
    ok("a note says why the zoom stopped", "nearest the zoom may go" in note(d), note(d))
    d.done()
    d.shot("real-desk-near-limit-note.png")
    # Reset view keeps the typed limits (by design): what does the user see?
    d.click("#reset"); time.sleep(0.4); d.settle()
    info("after Reset view with near 0.5 and far 1000", {"cam": cam(d)["dist"], "view": view(d)})
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch();" % (L, L, L))

    # ----- a real double-click
    d.done()
    px, py = d.at("#view", 0.55, 0.5)
    hit = d.js("const r = document.getElementById('view').getBoundingClientRect(); return %s.pick(%f - r.left, %f - r.top);" % (L, px, py))
    d.click("#view", count=2, fx=0.55, fy=0.5)
    time.sleep(0.8); d.settle()
    c = cam(d)
    ok("a real double-click moves in on the clicked spot (once, not twice)", hit is not None and norm(sub(c["target"], hit)) < 0.02 and 2.0 < c["dist"] < 3.2, (hit, c))
    d.click("#view", count=2, fx=0.03, fy=0.05); time.sleep(0.5); d.settle()
    ok("a double-click on empty background changes nothing", abs(cam(d)["dist"] - c["dist"]) < 1e-9, cam(d)["dist"])

    # ----- focus rings, reached with Tab
    d.js("%s.resetCam(); %s.touch(); document.getElementById('view').focus();" % (L, L))
    seen = []
    for _ in range(9):
        d.press("Tab")
        seen.append(d.js("const e = document.activeElement, cs = getComputedStyle(e), r = e.getBoundingClientRect(); return [e.id, e.matches(':focus-visible'), cs.outlineStyle, cs.outlineWidth, Math.round(r.top)].join(' ');"))
    info("Tab from the picture", seen)
    ids = [s.split(" ")[0] for s in seen]
    ok("Tab walks the picture's controls in screen order: switch, near box, slider, far box, then the three buttons",
       ids[:8] == ["camArc", "camFly", "camNear", "camRail", "camFar", "zoomOut", "zoomIn", "reset"], ids)
    ok("each of them shows a focus ring", all(" true solid " in s for s in seen[:8]), seen[:8])

    # ----- the 2D view with a real mouse
    d.js(PRE + "$('flat').click();"); time.sleep(0.4); d.done()
    v0 = view(d)
    info("2D view opened", v0)
    info("2D: hint, ends, switch hidden", d.js(PRE + "return [document.querySelector('.hint').textContent, $('camEndA').textContent, $('camEndB').textContent, $('camMode').hidden, $('camNear').value, $('camFar').value];"))
    b = d.box("#view")
    wx, wy = b[0] + b[2] * 0.7, b[1] + b[3] * 0.3
    spot0 = d.js(PRE + "const r = $('view').getBoundingClientRect(), h = r.height, u = [(2 * (%f - r.left) - r.width) / h, (h - 2 * (%f - r.top)) / h]; return [S.v2.x + u[0] * S.v2.h / 2, S.v2.y + u[1] * S.v2.h / 2];" % (wx, wy))
    d.mouse("mouseMoved", wx, wy)
    for _ in range(6):
        d.wheel(wx, wy, -100); time.sleep(0.05)
    time.sleep(1.0); d.settle()
    v1 = view(d)
    spot1 = d.js(PRE + "const r = $('view').getBoundingClientRect(), h = r.height, u = [(2 * (%f - r.left) - r.width) / h, (h - 2 * (%f - r.top)) / h]; return [S.v2.x + u[0] * S.v2.h / 2, S.v2.y + u[1] * S.v2.h / 2];" % (wx, wy))
    ok("2D: six wheel notches zoom in by 1.12^6 and hold the spot under the pointer", abs(v0["v2"][2] / v1["v2"][2] - 1.12 ** 6) < 1e-6 and norm(sub(spot0, spot1)) < 1e-6 * max(1, v0["v2"][2]), (v0["v2"][2] / v1["v2"][2], spot0, spot1))
    d.drag(cx, cy, cx + 100, cy + 50)
    v2 = view(d)
    s = v1["v2"][2] / b[3]
    ok("2D: a drag slides the picture with the pointer", abs((v2["v2"][0] - v1["v2"][0]) + 100 * s) < 1e-9 and abs((v2["v2"][1] - v1["v2"][1]) - 50 * s) < 1e-9, (v2["v2"], v1["v2"]))
    d.click("#view", count=2, fx=0.25, fy=0.25); time.sleep(0.8); d.settle()
    v3 = view(d)
    ok("2D: a double-click centres the clicked spot", abs(v3["v2"][0] - (v2["v2"][0] + (0.25 * b[2] * 2 - b[2]) / b[3] * v2["v2"][2] / 2)) < 1e-6 and abs(v3["v2"][2] - v2["v2"][2]) < 1e-9, (v2["v2"], v3["v2"]))
    d.click("#reset"); time.sleep(0.4); d.settle(); d.done()
    v4 = view(d)
    ok("2D: Reset view puts the flat picture back", all(abs(a - b_) < 1e-9 for a, b_ in zip(v4["v2"], v0["v2"])), (v4["v2"], v0["v2"]))
    ok("2D: Reset view left the 3D camera alone", abs(cam(d)["dist"] - c00["dist"]) < 1e-9, cam(d)["dist"])
    d.shot("real-desk-2d.png")
    d.js(PRE + "$('flat').click();"); time.sleep(0.3); d.done()


def phone(d):
    d.metrics(375, 812, phone=True, dpr=2)
    d.load(PAGE)
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});")
    time.sleep(0.4); d.done()
    ok("phone emulation: coarse pointer, and the hint speaks of fingers", d.js("return matchMedia('(pointer: coarse)').matches;") and d.js("return document.querySelector('.hint').textContent;").startswith("Drag to turn. Pinch to zoom."),
       d.js("return document.querySelector('.hint').textContent;"))
    boxes = d.js("return { boxes: T.boxes(), cover: T.cover(), under: T.under(), extent: T.extent(), over: document.documentElement.scrollWidth - document.documentElement.clientWidth, row: document.getElementById('camZoom').className, parent: document.getElementById('camZoom').parentElement.className, mode: document.getElementById('camMode').className };")
    info("phone layout", boxes)
    sizes = d.js("const q = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; }; return { camArc: q('#camArc'), camFly: q('#camFly'), camRail: q('#camRail'), camNear: q('#camNear'), camFar: q('#camFar'), camThumb: q('#camThumb'), zoomOut: q('#zoomOut'), zoomIn: q('#zoomIn'), reset: q('#reset'), nearFont: getComputedStyle(document.getElementById('camNear')).fontSize };")
    info("phone: sizes of the touch targets (w, h)", sizes)
    ok("phone: the zoom is a row outside the picture, no sideways scrolling", "is-row" in boxes["row"] and boxes["over"] <= 0 and boxes["boxes"]["camRail"][2] >= boxes["boxes"]["stage"][1], boxes["boxes"]["camRail"])
    d.shot("real-phone-open-window.png", clip=None)
    cx, cy = d.at("#view")
    c0 = cam(d)
    y_before = d.js("return window.scrollY;")

    # one finger turns, and the page does not scroll under it
    d.touch("touchStart", [(cx, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx + 12 * i, cy + 12 * i)])
    d.lift()
    c1 = cam(d)
    ok("one finger turns the solid", abs(c1["yaw"] - (c0["yaw"] - 60 * 0.008)) < 1e-9 and abs(c1["pitch"] - (c0["pitch"] + 60 * 0.008)) < 1e-9, (c0["yaw"], c1["yaw"], c0["pitch"], c1["pitch"]))
    ok("and the page did not scroll under the finger", d.js("return window.scrollY;") == y_before, (y_before, d.js("return window.scrollY;")))

    # pinch
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 - 8 * i, cy), (cx + 40 + 8 * i, cy)])
    time.sleep(0.15)
    c2 = cam(d)
    ok("two fingers spread to twice the gap: the distance halves", abs(c2["dist"] / c1["dist"] - 0.5) < 1e-6, c2["dist"] / c1["dist"])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 80, cy + 8 * i), (cx + 80, cy + 8 * i)])
    d.lift()
    c3 = cam(d)
    ok("two fingers moved together slide the scene and leave the zoom alone", norm(sub(c3["target"], c2["target"])) > 0.02 and abs(c3["dist"] / c2["dist"] - 1) < 0.02, (c3["dist"] / c2["dist"], norm(sub(c3["target"], c2["target"]))))
    ok("no finger is left registered, the page is not zoomed or scrolled", d.js("return %s.CV.ptr.size;" % L) == 0 and d.js("return [window.visualViewport ? visualViewport.scale : 1, window.scrollY];") == [1, y_before], d.js("return [window.visualViewport ? visualViewport.scale : 1, window.scrollY];"))
    info("zoom row after the pinch: value tag and thumb", d.js("const t = document.getElementById('camThumb').getBoundingClientRect(), r = document.getElementById('camRail').getBoundingClientRect(); return [document.getElementById('camVal').textContent, ((t.left + t.width / 2 - r.left) / r.width).toFixed(3)];"))
    # pinch together again
    d.touch("touchStart", [(cx - 80, cy), (cx + 80, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 80 + 8 * i, cy), (cx + 80 - 8 * i, cy)])
    d.lift()
    ok("pinching together to half the gap doubles the distance", abs(cam(d)["dist"] / c3["dist"] - 2) < 1e-6, cam(d)["dist"] / c3["dist"])

    # double-tap
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.done()
    px, py = d.at("#view", 0.5, 0.5)
    for _ in range(2):
        d.touch("touchStart", [(px, py)])
        d.touch("touchEnd", [])
        time.sleep(0.09)
    time.sleep(0.8); d.settle()
    c4 = cam(d)
    ok("a double-tap moves in once (55% of the distance to the spot)", 0.4 * c0["dist"] < c4["dist"] < 0.62 * c0["dist"], c4["dist"])
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.done()

    # the zoom row: a finger drags the slider
    rb = d.box("#camRail")
    ry = rb[1] + rb[3] / 2
    y_before = d.js("return window.scrollY;")
    d.touch("touchStart", [(rb[0] + rb[2] * 0.3, ry)])
    for i in range(1, 6):
        d.touch("touchMove", [(rb[0] + rb[2] * (0.3 + 0.08 * i), ry)])
    d.lift()
    time.sleep(0.6); d.settle()
    want = 0.005 * (60 / 0.005) ** 0.7
    ok("a finger drags the zoom slider along the row (near at the left)", abs(cam(d)["dist"] / want - 1) < 1e-6, (cam(d)["dist"], want))
    ok("and the page did not scroll while the slider was dragged", d.js("return window.scrollY;") == y_before, d.js("return window.scrollY;"))
    # a slightly slanted drag, as a thumb does it: 30 px down while moving along
    d.touch("touchStart", [(rb[0] + rb[2] * 0.7, ry)])
    for i in range(1, 6):
        d.touch("touchMove", [(rb[0] + rb[2] * (0.7 - 0.06 * i), ry + 6 * i)])
    d.lift()
    time.sleep(0.6); d.settle()
    want = 0.005 * (60 / 0.005) ** 0.4
    ok("a slanted drag (30 px down while moving along) still follows the finger and does not scroll the page", abs(cam(d)["dist"] / want - 1) < 1e-6 and d.js("return window.scrollY;") == y_before, (cam(d)["dist"], want, d.js("return window.scrollY;")))
    d.tap("#camRail", 0.6, 0.5)
    time.sleep(0.5); d.settle()
    want = 0.005 * (60 / 0.005) ** 0.6
    ok("a tap on the row jumps the zoom there", abs(cam(d)["dist"] / want - 1) < 1e-6, (cam(d)["dist"], want))
    d.done()
    d.shot("real-phone-row-dragged-window.png", clip=None)

    # the two boxes, typed after a tap
    d.tap("#camNear")
    ok("a tap on the nearest box puts the cursor in it", d.js("return document.activeElement.id;") == "camNear", d.js("return document.activeElement.id;"))
    info("page scroll and scale after the box took the focus", d.js("return [window.scrollY, window.visualViewport ? visualViewport.scale : 1];"))
    d.js("document.activeElement.select();"); d.text("0.5"); d.press("Enter")
    ok("phone: 0.5 then Enter sets the nearest limit", d.js("return %s.S.view.zmin;" % L) == 0.5, d.js("return %s.S.view.zmin;" % L))
    d.tap("#camFar")
    d.js("document.activeElement.select();"); d.text("20"); d.press("Enter")
    ok("phone: 20 then Enter sets the farthest limit", d.js("return %s.S.view.zmax;" % L) == 20 and d.js("return document.activeElement.id;") == "camFar", d.js("return [%s.S.view.zmax, document.activeElement.id];" % L))
    d.js("document.activeElement.select();"); d.text("0.6"); d.press("Enter")
    nt = note(d)
    ok("phone: a far limit under twice the near one is refused with a reason", d.js("return %s.S.view.zmax;" % L) == 20 and "at least twice" in nt, nt)
    nb = d.js("const n = document.getElementById('camNote').getBoundingClientRect(), s = document.getElementById('stage').getBoundingClientRect(); return { note: [Math.round(n.left), Math.round(n.top), Math.round(n.right), Math.round(n.bottom)], stage: [Math.round(s.left), Math.round(s.top), Math.round(s.right), Math.round(s.bottom)], win: [innerWidth, innerHeight] };")
    info("where the note shows", nb)
    d.shot("real-phone-refused-window.png", clip=None)
    d.js("document.activeElement.blur();")
    # the slider now runs between the typed limits
    rb = d.box("#camRail")
    d.tap("#camRail", 1.0 - 1e-3, 0.5); time.sleep(0.6); d.settle()
    ok("the right end of the row is the typed farthest limit", abs(cam(d)["dist"] / 20 - 1) < 0.02, cam(d)["dist"])
    d.tap("#camRail", 0.002, 0.5); time.sleep(0.6); d.settle()
    ok("the left end of the row is the typed nearest limit", abs(cam(d)["dist"] / 0.5 - 1) < 0.02, cam(d)["dist"])
    # pinch against the limit: stops, and says why?
    cx, cy = d.at("#view")
    d.touch("touchStart", [(cx - 30, cy), (cx + 30, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 30 - 10 * i, cy), (cx + 30 + 10 * i, cy)])
    d.lift()
    info("pinch in at the nearest limit: distance, note", [cam(d)["dist"], note(d)])
    ok("a pinch stops at the nearest limit", cam(d)["dist"] == 0.5, cam(d)["dist"])
    d.tap("#zoomIn"); time.sleep(0.4)
    nt = note(d)
    ok("the note at the limit names the box at the left end of the slider", "left end" in nt, nt)
    d.shot("real-phone-limit-note.png", clip=None)
    d.tap("#reset"); time.sleep(0.5); d.settle()
    info("phone: after Reset view with limits 0.5 and 20", {"dist": cam(d)["dist"], "view": view(d)})
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch();" % (L, L, L)); d.done()

    # the switch
    e0 = eye(d)
    d.tap("#camFly")
    ok("a tap on Fly switches the camera without moving the view", d.js("return %s.S.view.fly;" % L) is True and norm(sub(eye(d)["pos"], e0["pos"])) < 1e-12, d.js("return %s.S.view.fly;" % L))
    ok("the hint explains flying with fingers", d.js("return document.querySelector('.hint').textContent;").startswith("Drag to look around. Pinch to move"), d.js("return document.querySelector('.hint').textContent;"))
    info("fly on the phone: row ends, boxes hidden, value", d.js("const $ = id => document.getElementById(id); return [$('camEndA').textContent, $('camEndB').textContent, $('camNear').hidden, $('camFar').hidden, $('camVal').textContent, T.boxes()];"))
    e0 = eye(d)
    sp = d.js("return %s.S.view.speed;" % L)
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 - 8 * i, cy), (cx + 40 + 8 * i, cy)])
    d.lift()
    e1 = eye(d)
    fwd = dot(sub(e1["pos"], e0["pos"]), e0["f"])
    ok("flying: spreading two fingers to twice the gap moves forward 1.5 ln 2 times the speed", abs(fwd / sp - 1.0397) < 0.01, (fwd, sp))
    rb = d.box("#camRail")
    d.tap("#camRail", 0.25, 0.5); time.sleep(0.3)
    sp2 = d.js("return %s.S.view.speed;" % L)
    info("flying: a tap on the row a quarter from the left gives speed", [sp2, "left end word", d.js("return document.getElementById('camEndA').textContent;")])
    d.touch("touchStart", [(cx, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx + 10 * i, cy)])
    d.lift()
    e2 = eye(d)
    ok("flying: one finger looks around from a fixed eye", norm(sub(e2["pos"], e1["pos"])) < 1e-9 and norm(sub(e2["f"], e1["f"])) > 0.1, norm(sub(e2["f"], e1["f"])))
    d.done()
    d.shot("real-phone-fly-window.png", clip=None)
    d.tap("#camArc")
    e3 = eye(d)
    ok("a tap on Arcball switches back without moving the view, and the limit boxes return", d.js("return %s.S.view.fly;" % L) is False and norm(sub(e3["pos"], e2["pos"])) < 1e-9 and d.js("return document.getElementById('camNear').hidden;") is False, norm(sub(e3["pos"], e2["pos"])))
    d.tap("#reset"); time.sleep(0.5); d.settle(); d.done()
    cR = cam(d)
    ok("phone: a tap on Reset view puts the start view back", abs(cR["dist"] - c0["dist"]) < 1e-9 and abs(cR["yaw"] - c0["yaw"]) < 1e-9, cR)

    # the 2D view on the phone
    d.js("document.getElementById('flat').click();"); time.sleep(0.4); d.done()
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    info("phone 2D layout", d.js("return { boxes: T.boxes(), cover: T.cover(), hint: document.querySelector('.hint').textContent, modeHidden: document.getElementById('camMode').hidden };"))
    cx, cy = d.at("#view")
    v0 = view(d)
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 40 - 8 * i, cy), (cx + 40 + 8 * i, cy)])
    d.lift()
    v1 = view(d)
    ok("phone 2D: a pinch to twice the gap halves the span and keeps the middle", abs(v1["v2"][2] / v0["v2"][2] - 0.5) < 1e-6 and abs(v1["v2"][0] - v0["v2"][0]) < 1e-6, (v0["v2"], v1["v2"]))
    d.done()
    d.shot("real-phone-2d-window.png", clip=None)
    d.js("document.getElementById('flat').click();"); time.sleep(0.3)
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.done()

    # turning the phone: the stage becomes wide, the zoom goes back on the picture as a column, and back again
    d.metrics(812, 375, phone=True, dpr=2); time.sleep(0.8); d.done()
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    wide = d.js("return { boxes: T.boxes(), row: document.getElementById('camZoom').className, over: document.documentElement.scrollWidth - document.documentElement.clientWidth, win: [innerWidth, innerHeight] };")
    info("phone turned on its side (812 x 375)", wide)
    d.shot("real-phone-landscape-window.png", clip=None)
    d.metrics(375, 812, phone=True, dpr=2); time.sleep(0.8); d.done()
    back = d.js("return { row: document.getElementById('camZoom').className, parent: document.getElementById('camZoom').parentElement.className, stage: T.boxes().stage };")
    ok("turned upright again the zoom is a row again", "is-row" in back["row"], back)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "desk"
    with Rig(size=(1400, 950), phone=False, theme="dark") as d:
        try:
            if which == "desk":
                desktop(d)
            else:
                phone(d)
        except Exception as e:
            print("STOPPED: %r" % (e,))
    tally()


if __name__ == "__main__":
    main()
