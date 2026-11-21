"""Tester "camera", second check: Reset view and the start view with and without a trap solid (resets), and the
first screens at three sizes in both themes (sheets).  python out/t9/camera/views.py resets|sheets"""
import json, sys, time
from rig import Rig, L, ok, info, tally

PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
PAGE = "dist/v8.html"
ST = PRE + "return { mode: S.mode, solid: S.colour.solid, trap: S.colour.trap, r: S.colour.radius, thick: S.colour.thick, skip: S.colour.skip, t: [S.colour.tx, S.colour.ty, S.colour.tz], dist: +L.cam.dist.toFixed(3), yaw: +L.cam.yaw.toFixed(3), target: L.cam.target.map(v => +v.toFixed(3)), edge: T.edge(), note: T.note(), ext: (e => [e.x, e.y, e.hits])(T.extent()) };"


def state(d, name, shot=None):
    d.done()
    s = d.js(ST)
    e = s["edge"]
    cut = e["top"] + e["right"] + e["bottom"] + e["left"]
    info(name, s)
    if shot:
        d.shot("rs/" + shot)
    return s, cut


def reset(d, tap=False):
    if tap:
        d.tap("#reset")
    else:
        d.click("#reset")
    time.sleep(0.5); d.settle()


def resets(d):
    d.load(PAGE)
    d.js("window.scrollTo(0, 0);")
    s, cut = state(d, "M fresh, no trap solid", "m-0-fresh.png")
    ok("Mandelbrot start view: distance 5.2, whole", s["dist"] == 5.2 and cut == 0, (s["dist"], cut))
    d.js(PRE + "T.sel('col-solid', 1);")
    s, cut = state(d, "M: trap is the solid, switched on with the drop-down (camera not asked)", "m-1-solid-on.png")
    reset(d)
    s, cut = state(d, "M: trap is the solid, after Reset view", "m-2-solid-reset.png")
    ok("M trap solid after Reset view: nothing at the frame", cut == 0, (s["dist"], s["edge"], s["note"]))
    d.js(PRE + "T.type('col-radiusNum', '2');")
    s, cut = state(d, "M: trap solid, radius 2 typed (dial only)", "m-3-r2-dial.png")
    reset(d)
    s, cut = state(d, "M: trap solid radius 2, after Reset view", "m-4-r2-reset.png")
    ok("M trap solid radius 2 after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    d.js(PRE + "T.type('col-skipNum', '0');")
    d.done()
    reset(d)
    s, cut = state(d, "M: trap solid radius 2, skip 0, after Reset view", "m-5-r2-skip0-reset.png")
    ok("M trap solid radius 2 skip 0 after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    d.js(PRE + "T.type('col-skipNum', '1'); T.type('col-radiusNum', '1'); T.sel('col-solid', 2);")
    d.done()
    reset(d)
    s, cut = state(d, "M: trap is added to the solid, after Reset view", "m-6-added-reset.png")
    ok("M trap added to the solid after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    # start view: change of mode with the trap solid on
    d.js(PRE + "T.sel('col-solid', 1); T.type('col-radiusNum', '1.5');")
    d.done()
    d.js(PRE + "$('mode-j').click();"); time.sleep(0.5)
    s, cut = state(d, "J start view (mode changed with a trap solid of radius 1.5 on)", "j-1-start-r1.5.png")
    ok("Julia start view with a trap solid of radius 1.5: nothing at the frame", cut == 0, (s["dist"], s["edge"]))
    d.js(PRE + "T.type('cxNum', '-1'); T.type('cyNum', '0'); T.type('czNum', '0'); T.type('col-radiusNum', '2');")
    d.done()
    d.js(PRE + "$('mode-m').click();"); time.sleep(0.5)
    s, cut = state(d, "M start view (mode changed back, trap solid radius 2)", "m-7-start-r2.png")
    ok("Mandelbrot start view with a trap solid of radius 2: nothing at the frame", cut == 0, (s["dist"], s["edge"]))
    d.js(PRE + "$('mode-j').click();"); time.sleep(0.5)
    s, cut = state(d, "J start view, c = -1, trap solid radius 2", "j-2-start-r2.png")
    ok("Julia c = -1 start view with a trap solid of radius 2: nothing at the frame", cut == 0, (s["dist"], s["edge"]))
    d.js(PRE + "T.type('col-radiusNum', '0.7'); T.type('col-txNum', '1');")
    d.done()
    reset(d)
    s, cut = state(d, "J: trap solid radius 0.7 centred at x = 1, after Reset view", "j-3-tx1-reset.png")
    ok("Julia trap solid off centre after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    d.js(PRE + "T.type('col-txNum', '0'); T.sel('col-trap', 6); T.type('col-radiusNum', '1');")
    d.done()
    d.js(PRE + "$('mode-k').click();"); time.sleep(0.6)
    s, cut = state(d, "K start view (mode changed, ring trap solid, radius 1)", "k-1-start.png")
    d.js(PRE + "T.type('col-thickNum', '0.2'); $('mode-j').click();"); time.sleep(0.6); d.done()
    d.js(PRE + "$('mode-k').click();"); time.sleep(0.6)
    s, cut = state(d, "K start view with ring trap solid thickness 0.2 (mode changed away and back)", "k-2-start-thick0.2.png")
    info("K start view with thickness 0.2: probes at the frame, note, distance", [cut, s["note"], s["dist"]])
    reset(d)
    s, cut = state(d, "K thickness 0.2 after Reset view", "k-3-thick0.2-reset.png")
    ok("Kleinian trap solid thickness 0.2 after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    d.js(PRE + "T.type('col-thickNum', '0.05'); T.type('col-radiusNum', '1.6');"); d.done()
    reset(d)
    s, cut = state(d, "K radius 1.6 after Reset view", "k-4-r1.6-reset.png")
    ok("Kleinian trap solid radius 1.6 after Reset view: a note says it runs out", "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    nb = d.js("const n = document.getElementById('camNote').getBoundingClientRect(), s = document.getElementById('stage').getBoundingClientRect(); return [Math.round(n.left - s.left), Math.round(n.top - s.top), Math.round(n.right - s.left), Math.round(n.bottom - s.top)];")
    info("where the note sits on the picture", nb)
    time.sleep(6.5)
    info("the note 6.5 s later", d.js("return T.note();"))
    # now the user turns the trap solid off: the camera stays far away until Reset view
    d.js(PRE + "T.sel('col-solid', 0);")
    s, cut = state(d, "K: trap solid switched off (camera left where it was)", "k-5-solid-off.png")
    reset(d)
    s, cut = state(d, "K: no trap solid, after Reset view", "k-6-off-reset.png")
    ok("Kleinian start view without a trap solid is back at 7 and the note is gone", s["dist"] == 7 and s["note"] == "", (s["dist"], s["note"]))
    d.js(PRE + "$('mode-m').click();"); time.sleep(0.5)
    s, cut = state(d, "M start view again, no trap solid", "m-8-off-start.png")
    ok("Mandelbrot start view without a trap solid is back at 5.2", s["dist"] == 5.2 and cut == 0, s["dist"])
    # Reset view in the 2D view with a trap solid on: nothing odd, the 3D camera is left alone
    d.js(PRE + "T.sel('col-solid', 1); T.type('col-radiusNum', '2'); $('flat').click();"); time.sleep(0.4); d.done()
    c0 = d.js("return T.cam();")
    reset(d); d.done()
    c1 = d.js("return T.cam();")
    ok("2D view with a trap solid on: Reset view leaves the 3D camera alone and shows no note", c0["dist"] == c1["dist"] and d.js("return T.note();") == "", (c0["dist"], c1["dist"], d.js("return T.note();")))
    d.js(PRE + "$('flat').click();"); time.sleep(0.3); d.done()
    # the far limit in the way of the step back
    d.js(PRE + "$('mode-j').click();"); time.sleep(0.5); d.done()
    d.js(PRE + "T.type('cxNum', '-1'); T.type('cyNum', '0'); T.type('czNum', '0'); T.sel('col-trap', 5); T.type('col-radiusNum', '2'); S.view.zmax = 5; L.syncControls(); L.viewChanged(); L.touch();")
    d.done()
    reset(d)
    s, cut = state(d, "J radius 2 with the farthest zoom limit typed as 5, after Reset view", "j-4-r2-far5-reset.png")
    info("far limit 5 in the way: distance, probes at the frame, note", [s["dist"], cut, s["note"]])
    d.js(PRE + "L.resetZoomLimits(); L.resetAll();"); time.sleep(0.5); d.done()
    s, cut = state(d, "after Reset everything", "m-9-reset-all.png")
    ok("Reset everything: start view 5.2, no trap solid", s["dist"] == 5.2 and s["solid"] == 0, s)

    # phone: the same trap solids on a narrow stage
    d.metrics(375, 812, phone=True, dpr=2)
    d.load(PAGE)
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    d.js(PRE + "$('mode-j').click();"); time.sleep(0.5); d.done()
    d.js(PRE + "T.type('cxNum', '-1'); T.type('cyNum', '0'); T.type('czNum', '0'); T.sel('col-trap', 5); T.sel('col-solid', 1); T.type('col-radiusNum', '2');"); d.done()
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    reset(d, tap=True)
    s, cut = state(d, "phone: J c = -1 trap solid radius 2 after Reset view", "p-j-r2-reset.png")
    under = d.js("return T.under();")
    ok("phone: Julia trap solid radius 2 after Reset view: nothing at the frame", cut == 0, (s["dist"], s["edge"], s["note"]))
    info("phone: what lies under the picture's controls", under)
    d.js(PRE + "$('mode-k').click();"); time.sleep(0.6); d.done()
    d.js(PRE + "T.sel('col-trap', 6); T.type('col-radiusNum', '1'); T.type('col-thickNum', '0.2');"); d.done()
    d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
    reset(d, tap=True)
    s, cut = state(d, "phone: K ring trap solid thickness 0.2 after Reset view", "p-k-thick0.2-reset.png")
    ok("phone: Kleinian trap solid thickness 0.2 after Reset view: nothing at the frame, or a note", cut == 0 or "runs out" in s["note"], (s["dist"], s["edge"], s["note"]))
    d.shot("rs/p-k-thick0.2-reset-window.png", clip=None)


def sheets(d):
    for theme in ("dark", "light"):
        d.set_theme(theme)
        for (w, h, ph) in ((375, 812, True), (1024, 768, False), (1400, 950, False)):
            tag = "%d%s%s" % (w, theme[0], "t" if ph else "")
            d.metrics(w, h, phone=ph, dpr=1)
            d.load(PAGE)
            d.js("window.scrollTo(0, 0);"); time.sleep(0.3); d.done()
            m = d.js("const $ = id => document.getElementById(id), s = $('stage').getBoundingClientRect(), r = $('reset').getBoundingClientRect(), z = $('camZoom').getBoundingClientRect(), hn = document.querySelector('.hint').getBoundingClientRect();"
                     "return { win: [innerWidth, innerHeight], stage: [Math.round(s.left), Math.round(s.top), Math.round(s.right), Math.round(s.bottom)], reset: [Math.round(r.top), Math.round(r.bottom)], zoom: [Math.round(z.left), Math.round(z.top), Math.round(z.right), Math.round(z.bottom)], hint: [Math.round(hn.top), Math.round(hn.bottom)], over: document.documentElement.scrollWidth - document.documentElement.clientWidth, boxes: T.boxes(), cover: T.cover(), under: T.under() };")
            info("first screen %s" % tag, m)
            d.shot("sh/%s-0-open.png" % tag, clip=None)
            if w == 1400 and theme == "dark":
                # layout-5 by hand: click the page just above the picture, then Tab nine times
                st = d.box("#stage")
                what = d.js("const e = document.elementFromPoint(%f, %f); return e ? e.tagName + '.' + e.className : null;" % (st[0] + 200, st[1] - 12))
                d.click_xy(st[0] + 200, st[1] - 12)
                seen = []
                for _ in range(9):
                    d.press("Tab")
                    seen.append(d.js("const e = document.activeElement, r = e.getBoundingClientRect(); return (e.id || e.tagName) + '@' + Math.round(r.top);"))
                info("layout-5 by hand: clicked on %s above the picture, then nine Tab presses" % what, seen)
                d.js("document.activeElement.blur(); window.scrollTo(0, 0);")
            d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
            d.shot("sh/%s-1-stage.png" % tag, clip=None)
            d.js("document.getElementById('mode-k').click();"); time.sleep(0.6); d.done()
            d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
            mk = d.js("return { under: T.under(), ext: T.extent(), cover: T.cover() };")
            info("kleinian %s" % tag, mk)
            d.shot("sh/%s-2-klein.png" % tag, clip=None)
            d.js("document.getElementById('camFly').click();"); time.sleep(0.4); d.done()
            d.shot("sh/%s-3-klein-fly.png" % tag, clip=None)
            d.js("document.getElementById('camArc').click(); document.getElementById('mode-j').click();"); time.sleep(0.6); d.done()
            d.js("document.getElementById('flat').click();"); time.sleep(0.4); d.done()
            d.js("document.getElementById('stage').scrollIntoView({block: 'center'});"); time.sleep(0.3)
            d.shot("sh/%s-4-julia-2d.png" % tag, clip=None)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "resets"
    with Rig(size=(1400, 950), phone=False, theme="dark") as d:
        try:
            (resets if which == "resets" else sheets)(d)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("STOPPED: %r" % (e,))
    tally()


if __name__ == "__main__":
    main()
