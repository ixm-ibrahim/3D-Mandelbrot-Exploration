"""Engineer "camera", round 10. Real input through the camera tester's rig (out/t9/camera/rig.py).

  python out/r10/camera/drive.py base   dist/v9m.html    boxes of the picture's controls and the start views at 1400, 1024 and 375 wide -> base-<page>.json
  python out/r10/camera/drive.py pinch  dist/v9m.html    t9-camera-1: a pinch against a zoom limit, real touch at 375 x 812, from a state with no note on show
  python out/r10/camera/drive.py kstart dist/v9m.html    solids-7, rest: the Kleinian start view with a trap solid on
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t9", "camera"))
from rig import Rig, L, ok, info, tally  # noqa: E402

PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
WHAT = sys.argv[1] if len(sys.argv) > 1 else "base"
PAGE = sys.argv[2] if len(sys.argv) > 2 else "dist/v9m.html"
TAG = os.path.splitext(os.path.basename(PAGE))[0]


def out(name):
    return os.path.join(HERE, name)


def note(d):
    return d.js("return T.note();")


def dist(d):
    return d.js("return %s.cam.dist;" % L)


def centre(d):
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});")
    time.sleep(0.3)


SNAP = PRE + """return { boxes: T.boxes(), cover: T.cover(), cam: T.cam(), v2: [S.v2.x, S.v2.y, S.v2.h, S.v2.hmin, S.v2.hmax].map(v => +v.toFixed(5)),
  hint: document.querySelector('.hint').textContent, zoom: $('camZoom').className, mode: $('camMode').className, parent: $('camZoom').parentElement.className,
  note: T.note(), over: document.documentElement.scrollWidth - document.documentElement.clientWidth, scrollY: Math.round(scrollY) };"""


def base(d):
    rec = {}
    for (w, h, phone) in ((1400, 950, False), (1024, 768, False), (375, 812, True)):
        d.metrics(w, h, phone=phone, dpr=2 if phone else 1)
        d.load(PAGE)
        d.js("window.scrollTo(0, 0);"); time.sleep(0.3); d.done()
        r = rec["%dx%d" % (w, h)] = {}
        r["open"] = d.js(SNAP)
        for m in ("j", "k", "m"):
            d.js("document.getElementById('mode-%s').click();" % m); time.sleep(0.6); d.done(); time.sleep(0.5)
            d.js("window.scrollTo(0, 0);"); time.sleep(0.2)
            r["start-" + m] = d.js(SNAP)
        d.js("document.getElementById('flat').click();"); time.sleep(0.5); d.done()
        r["2d"] = d.js(SNAP)
        d.js("document.getElementById('flat').click();"); time.sleep(0.5); d.done()
        d.js("document.getElementById('camFly').click();"); time.sleep(0.4); d.done()
        r["fly"] = d.js(SNAP)
        d.js("document.getElementById('camArc').click();"); time.sleep(0.4)
        d.js("%s.cam.dist = 3; %s.cam.yaw = 0.3; %s.touch();" % (L, L, L)); d.done()
        d.js("document.getElementById('reset').click();"); time.sleep(0.5); d.settle(); d.done()
        r["reset-view"] = d.js(SNAP)
    with open(out("base-%s.json" % TAG), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True, ensure_ascii=False)
    print("wrote out/r10/camera/base-%s.json" % TAG)


def quiet(d, why):
    """wait until no note is on show, so that a note read next was written by the step under test"""
    t0 = time.time()
    while note(d) and time.time() - t0 < 8:
        time.sleep(0.3)
    ok("no note on show before: " + why, note(d) == "", note(d))


def spread(d, cx, cy, gap0, step, n=5, lift=True):
    """two fingers, gap0 apart, each moved outward by `step` px n times (negative: together)"""
    d.touch("touchStart", [(cx - gap0 / 2, cy), (cx + gap0 / 2, cy)])
    for i in range(1, n + 1):
        d.touch("touchMove", [(cx - gap0 / 2 - step * i, cy), (cx + gap0 / 2 + step * i, cy)])
    time.sleep(0.15)
    got = [dist(d), note(d)]
    if lift:
        d.lift()
    return got


def typed(d, sel, text):
    d.tap(sel); d.js("document.activeElement.select();"); d.text(text); d.press("Enter"); time.sleep(0.2)
    d.js("document.activeElement.blur();")


def pinch(d):
    d.metrics(375, 812, phone=True, dpr=2)
    d.load(PAGE); centre(d); d.done()
    cx, cy = d.at("#view")
    # --- free pinch: no note
    quiet(d, "a free pinch")
    c0 = dist(d)
    got = spread(d, cx, cy, 80, 8)
    ok("a pinch inside the limits zooms (distance halves) and writes no note", abs(got[0] / c0 - 0.5) < 1e-6 and got[1] == "", got)
    # --- the nearest limit
    typed(d, "#camNear", "0.5")
    ok("0.5 typed as the nearest limit", d.js("return %s.S.view.zmin;" % L) == 0.5)
    d.tap("#camRail", 0.002, 0.5); time.sleep(0.6); d.settle()
    ok("the left end of the row is the nearest limit", abs(dist(d) / 0.5 - 1) < 0.02, dist(d))
    d.js("%s.cam.dist = 0.5; %s.touch();" % (L, L)); d.done()
    quiet(d, "the pinch at the nearest limit")
    got = spread(d, cx, cy, 60, 10, lift=False)
    info("pinch in at the nearest limit: distance, note", got)
    ok("a pinch stops at the nearest limit", got[0] == 0.5, got[0])
    ok("and a note says why (nearest, left end of the slider)", "nearest the zoom may go" in got[1] and "left end" in got[1], got[1])
    d.shot(out("%s-pinch-near-window.png" % TAG), clip=None)
    d.lift()
    d.tap("#zoomIn"); time.sleep(0.4)
    info("the note of the + button at the same limit", note(d))
    # --- arriving at the limit in one gesture: starts at 0.8, ends against 0.5
    d.js("%s.cam.dist = 0.8; %s.touch();" % (L, L)); d.done()
    quiet(d, "a pinch that arrives at the limit")
    got = spread(d, cx, cy, 60, 10)
    info("pinch from 0.8 against the limit 0.5 (asks for 0.3): distance, note", got)
    d.js("%s.cam.dist = 0.52; %s.touch();" % (L, L)); d.done()
    quiet(d, "a pinch that just reaches the limit")
    got = spread(d, cx, cy, 100, 1, n=3)
    info("pinch from 0.52, fingers 100 to 106 apart (asks for 0.49, 2% past the limit): distance, note", got)
    ok("a pinch that only just touches the limit writes no note", got[1] == "", got)
    # --- two fingers that slide the picture at the limit, with a little wobble in their spread
    d.js("%s.cam.dist = 0.5; %s.touch();" % (L, L)); d.done()
    quiet(d, "two fingers sliding at the limit")
    d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
    for i in range(1, 11):
        wob = (1, -1, 0, 1, -1, 1, 0, -1, 1, -1)[i - 1]
        d.touch("touchMove", [(cx - 40 - wob, cy + 6 * i), (cx + 40 + wob, cy + 6 * i)])
    time.sleep(0.15); got = [dist(d), note(d)]; d.lift()
    ok("two fingers sliding at the limit (spread wobbling by 2 px) write no note", got[1] == "", got)
    # --- the farthest limit
    typed(d, "#camFar", "20")
    d.js("%s.cam.dist = 20; %s.touch();" % (L, L)); d.done()
    quiet(d, "the pinch at the farthest limit")
    got = spread(d, cx, cy, 160, -8, lift=False)
    info("pinch together at the farthest limit: distance, note", got)
    ok("a pinch stops at the farthest limit and a note says why (farthest, right end)", got[0] == 20 and "farthest the zoom may go" in got[1] and "right end" in got[1], got)
    d.shot(out("%s-pinch-far-window.png" % TAG), clip=None)
    d.lift()
    time.sleep(6.6)
    ok("the note goes away by itself after six seconds", note(d) == "", note(d))
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch();" % (L, L, L)); d.done()
    # --- the 2D view
    d.js("document.getElementById('flat').click();"); time.sleep(0.5); d.done(); centre(d)
    cx, cy = d.at("#view")
    typed(d, "#camNear", "1")
    d.js(PRE + "S.v2.h = 1; L.touch();"); d.done()
    quiet(d, "the 2D pinch at the closest zoom")
    d.touch("touchStart", [(cx - 30, cy), (cx + 30, cy)])
    for i in range(1, 6):
        d.touch("touchMove", [(cx - 30 - 10 * i, cy), (cx + 30 + 10 * i, cy)])
    time.sleep(0.15); got = [d.js(PRE + "return S.v2.h;"), note(d)]; d.lift()
    info("2D view, pinch in at the closest zoom: span, note", got)
    ok("2D view: a pinch stops at the closest zoom and a note says why", got[0] == 1 and "closest the zoom may go" in got[1], got)
    d.js("document.getElementById('flat').click();"); time.sleep(0.5); d.done()
    d.js("%s.resetZoomLimits(); %s.resetCam(); %s.touch();" % (L, L, L)); d.done()
    # --- flying: a pinch moves, there is no limit and no note
    centre(d); cx, cy = d.at("#view")
    d.tap("#camFly"); time.sleep(0.3)
    quiet(d, "the pinch while flying")
    got = spread(d, cx, cy, 80, 8)
    ok("flying: a pinch writes no note", got[1] == "", got)
    d.tap("#camArc"); time.sleep(0.3)
    # --- turned on its side the slider is a column: the note names the box at the top
    d.metrics(812, 375, phone=True, dpr=2); time.sleep(0.8); d.done(); centre(d)
    cx, cy = d.at("#view")
    d.js(PRE + "S.view.zmin = 0.5; L.cam.dist = 0.5; L.viewChanged(); L.touch();"); d.done()
    quiet(d, "the pinch with the slider as a column")
    got = spread(d, cx, cy, 60, 10)
    info("on its side (slider a column), pinch in at the nearest limit: distance, note", got)
    ok("as a column the note names the box at the top of the slider", "at the top of the slider" in got[1], got[1])


KST = PRE + "return { mode: S.mode, solid: S.colour.solid, trap: S.colour.trap, thick: S.colour.thick, r: S.colour.radius, dist: +L.cam.dist.toFixed(3), yaw: +L.cam.yaw.toFixed(4), pitch: +L.cam.pitch.toFixed(4), target: L.cam.target.map(v => +v.toFixed(3)), edge: T.edge(), note: T.note() };"


def kstate(d, name, shot=None):
    d.done()
    s = d.js(KST); e = s["edge"]; cut = e["top"] + e["right"] + e["bottom"] + e["left"]
    info(name, s)
    if shot:
        d.shot(out("%s-%s.png" % (TAG, shot)))
    return s, cut


def trace(d, ms=2500):
    """the camera distance sampled every frame from now on: [[ms, dist], ...] where it changes"""
    d.js("window.__tr = []; const t0 = performance.now(); let last = null; const f = () => { const v = %s.cam.dist; if (v !== last) { window.__tr.push([Math.round(performance.now() - t0), +v.toFixed(3)]); last = v; } if (performance.now() - t0 < %d) requestAnimationFrame(f); }; f();" % (L, ms))


def kstart(d):
    d.load(PAGE); d.js("window.scrollTo(0, 0);")
    # the tester's state: ring, the trap is the solid, radius 1, then thickness 0.2
    d.js(PRE + "T.sel('col-trap', 6); T.sel('col-solid', 1); T.type('col-radiusNum', '1');"); d.done()
    trace(d)
    d.js(PRE + "$('mode-k').click();"); time.sleep(0.6)
    s, cut = kstate(d, "K start view, ring trap solid, radius 1, first time in Kleinian mode", "k-1-start")
    info("camera distance after the click (ms, distance)", d.js("return window.__tr;"))
    d.js(PRE + "T.type('col-thickNum', '0.2');"); d.done()
    before = dist(d)
    s, cut = kstate(d, "K: thickness 0.2 typed (a dial: the camera stays)", "k-1b-thick-typed")
    time.sleep(1.0)
    ok("typing the dial does not move the camera", dist(d) == before, (before, dist(d)))
    d.js(PRE + "$('mode-j').click();"); time.sleep(0.6); d.done()
    trace(d)
    d.js(PRE + "$('mode-k').click();"); time.sleep(0.6)
    s, cut = kstate(d, "K start view with ring trap solid thickness 0.2 (mode changed away and back)", "k-2-start-thick0.2")
    info("camera distance after the click (ms, distance)", d.js("return window.__tr;"))
    ok("Kleinian start view with a trap solid of thickness 0.2: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    start = s["dist"]
    d.click("#reset"); time.sleep(0.5); d.settle()
    s, cut = kstate(d, "the same after Reset view", "k-3-reset")
    ok("the start view and Reset view agree", s["dist"] == start, (start, s["dist"]))
    # ----- the program NOT ready at the click: a fresh page, no programs prepared ahead, the Kleinian trap solid never drawn
    def cold():
        d.load(PAGE); d.js("window.scrollTo(0, 0);")
        d.js(PRE + "L.R.warmOn = false; T.sel('col-trap', 6); T.sel('col-solid', 1); T.type('col-radiusNum', '1'); T.type('col-thickNum', '0.2');"); d.done()
        return d.at("#view")
    CLICK = PRE + "$('mode-k').click(); const mid = !!L.pick($('stage').clientWidth / 2, $('stage').clientHeight / 2); window.__tr = []; const t0 = performance.now(); let last = null; const f = () => { const v = L.cam.dist; if (v !== last) { window.__tr.push([Math.round(performance.now() - t0), +v.toFixed(3)]); last = v; } if (!window.__seen && L.pick($('stage').clientWidth * 0.3, $('stage').clientHeight * 0.75)) window.__seen = Math.round(performance.now() - t0); if (performance.now() - t0 < 8000) requestAnimationFrame(f); }; window.__seen = 0; f(); return [L.renderIdle(), mid];"
    cx, cy = cold()
    ready0 = d.js(CLICK)
    time.sleep(0.6)
    s, cut = kstate(d, "K start view, the program had to be prepared after the click, hands off", "k-4-cold")
    info("at the click: [picture finished, pick sees the middle]; pick first saw the solid after (ms); camera distance (ms, distance)", [ready0, d.js("return window.__seen;"), d.js("return window.__tr;")])
    ok("the picture was not ready at the click (so this is the waiting case)", ready0 == [False, False], ready0)
    ok("cold start view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    # the user drags before the picture is ready: the camera must stay theirs
    cx, cy = cold()
    d.mouse("mouseMoved", cx, cy)
    ready0 = d.js(CLICK)
    d.mouse("mousePressed", cx, cy, button="left", buttons=1, clickCount=1)
    for i in range(1, 6):
        d.mouse("mouseMoved", cx + 10 * i, cy, button="left", buttons=1)
    c1 = d.js("return T.cam();")
    seen1 = d.js("return window.__seen;")
    time.sleep(2.0)
    c2 = d.js("return T.cam();")
    d.mouse("mouseReleased", cx + 50, cy, button="left", clickCount=1)
    d.done(); time.sleep(1.0)
    c3 = d.js("return T.cam();")
    s, cut = kstate(d, "K: dragged by 50 px straight after the click on Kleinian", "k-5-dragged")
    info("drag case: ready at the click, pick had seen the solid when the drag was over (0 = not yet), camera distance (ms, distance)", [ready0, seen1, d.js("return window.__tr;")])
    ok("a drag begun before the picture was ready: the camera turned by the drag and was not moved afterwards",
       ready0 == [False, False] and abs(c1["yaw"] - (0.35 - 50 * 0.008)) < 1e-3 and c1["dist"] == 7 and c2 == c1 and c3 == c1, (c1, c2, c3))
    # a press with no movement, held while the picture gets ready, then released: nothing may move under the finger or after
    cx, cy = cold()
    d.mouse("mouseMoved", cx, cy)
    ready0 = d.js(CLICK)
    d.mouse("mousePressed", cx, cy, button="left", buttons=1, clickCount=1)
    time.sleep(2.5)
    c1 = d.js("return T.cam();")
    d.mouse("mouseReleased", cx, cy, button="left", clickCount=1)
    d.done(); time.sleep(1.0)
    c2 = d.js("return T.cam();")
    info("press case: ready at the click, pick first saw the solid after (ms)", [ready0, d.js("return window.__seen;")])
    ok("a press held on the picture while it got ready: the camera was not moved, then or after the release", ready0 == [False, False] and c1["dist"] == 7 and c2 == c1, (c1, c2))
    # one wheel notch straight after the click
    cx, cy = cold()
    d.mouse("mouseMoved", cx, cy)
    ready0 = d.js(CLICK)
    d.wheel(cx, cy, -100)
    time.sleep(2.5); d.settle(); d.done()
    c = d.js("return T.cam();")
    ok("a wheel notch straight after the click: the zoom is the user's (7 / 1.12), nothing stepped back", ready0 == [False, False] and abs(c["dist"] - 7 / 1.12) < 1e-3, (ready0, c["dist"]))
    # Reset view pressed while the picture is still being prepared: the look comes when it is ready
    cx, cy = cold()
    ready0 = d.js(CLICK)
    d.js("document.getElementById('reset').click();")
    time.sleep(0.6)
    s, cut = kstate(d, "K: Reset view pressed while the picture was being prepared", "k-6-reset-early")
    ok("Reset view pressed before the picture was ready still ends whole", ready0 == [False, False] and (cut == 0 or "runs out" in s["note"]), (ready0, s["dist"], s["edge"], s["note"]))
    # a camera that was given (an example from the list) is used as given
    d.js(PRE + "const e = $('trapExamples'); e.value = [...e.options].find(o => o.text.startsWith('Rings in the lace')).value; e.dispatchEvent(new Event('change', { bubbles: true }));")
    time.sleep(1.5); d.done()
    c1 = d.js("return T.cam();"); time.sleep(1.0); c2 = d.js("return T.cam();")
    s, cut = kstate(d, "K: the example Rings in the lace (its camera is given)", "k-7-example")
    info("the example's camera, at once and a second later", [c1, c2])
    ok("an example's camera is left as given", c1 == c2, (c1["dist"], c2["dist"]))
    # no trap solid: the start view is the plain one
    d.js(PRE + "T.sel('col-solid', 0); $('mode-j').click();"); time.sleep(0.6); d.done()
    d.js(PRE + "$('mode-k').click();"); time.sleep(1.0); d.done()
    ok("without a trap solid the Kleinian start view is 7", dist(d) == 7, dist(d))


with Rig(size=(1400, 950), phone=False, theme="dark") as d:
    try:
        {"base": base, "pinch": pinch, "kstart": kstart}[WHAT](d)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("STOPPED: %r" % (e,))
tally()
