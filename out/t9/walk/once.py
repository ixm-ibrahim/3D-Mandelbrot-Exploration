"""The four one-off situations: storage blocked, a window resized mid-draw, the tab hidden and shown, a lost GL context.
  python out/t6/walk/once.py storage1|storage2|resize|hidden|context|empty
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import Lab, HERE
which = sys.argv[1]
for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass


def out(*a):
    print(*a, flush=True)


def save(lab, name):
    with open(os.path.join(HERE, name), "wb") as f:
        f.write(lab.shot_png())


def brief(c):
    return {k: c[k] for k in ("idle", "busy", "bar", "status", "bad", "exp", "mesh", "glfail", "mode", "flat")}


PANEL = ("return { msg: (document.getElementById('exportMsg')||{}).textContent, step: (document.getElementById('exportStep')||{}).textContent, "
         "btns: [...document.querySelectorAll('#exportPanel button')].filter(b => __w.vis(b)).map(b => b.textContent).filter(t => t.length > 2), busy: squaringLab.exportBusy() };")
MPANEL = ("return { msg: (document.getElementById('meshMsg')||{}).textContent, step: (document.getElementById('meshStep')||{}).textContent, "
          "btns: [...document.querySelectorAll('#meshPanel button')].filter(b => __w.vis(b)).map(b => b.textContent).filter(t => t.length > 2), busy: squaringLab.meshBusy() };")
SIZE3 = "const s = document.getElementById('exportSize'); s.selectedIndex = 3; s.dispatchEvent(new Event('change', { bubbles: true })); return s.options[3].text;"

if which in ("storage1", "storage2"):
    pre = ("Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('The operation is insecure.', 'SecurityError'); } });"
           if which == "storage1" else
           "Storage.prototype.setItem = function () { throw new DOMException('quota', 'QuotaExceededError'); };")
    lab = Lab(pre_script=pre)
    out(which, "idle after", lab.wait_idle(240), "problems", lab.problems())
    lab.click("#mode-j"); lab.wait_idle(120)
    lab.retype("#juliaName", "walk point"); lab.click("#juliaSave"); time.sleep(0.5)
    out("after save:", lab.js("const s = document.getElementById('juliaPreset'), n = document.getElementById('juliaSaveNote'); return { note: n.hidden ? null : n.textContent, groups: [...s.querySelectorAll('optgroup')].map(g => g.label + ':' + g.children.length), chosen: s.selectedOptions[0] && s.selectedOptions[0].text, del: !document.getElementById('juliaDelete').hidden, saved: squaringLab.juliaSaved().length };"))
    lab.click("#juliaDelete"); time.sleep(0.4)
    out("after delete:", lab.js("const n = document.getElementById('juliaSaveNote'); return { saved: squaringLab.juliaSaved().length, note: n.hidden ? null : n.textContent };"))
    lab.click("#resetAll"); lab.wait_idle(120)
    out("check:", brief(lab.check()), "picture", lab.picture_stats(), "problems", lab.problems())
    save(lab, "once-%s.png" % which); lab.close()

if which == "resize":
    lab = Lab()
    lab.wait_idle(240)
    lab.click("#secQuality > summary"); lab.click("#qFine")
    sizes = [(1100, 700), (700, 900), (1400, 950), (375, 812), (1600, 500), (1024, 768), (300, 300), (1400, 950)]
    for i, (w, h) in enumerate(sizes):
        time.sleep([0.15, 0.4, 0.05, 0.8, 0.02, 0.3, 0.1, 0.2][i])
        lab.p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        c = lab.check()
        out("resized to", (w, h), "idle", c["idle"], "status", c["status"], "sw/iw", c["sw"], c["iw"])
    t = lab.wait_idle(240)
    geo = lab.js("const c = document.getElementById('view'), s = document.getElementById('stage'); return { canvas: [c.width, c.height], css: [c.clientWidth, c.clientHeight], stage: [s.clientWidth, s.clientHeight], res: squaringLab.S.q.res };")
    out("idle after", t, geo, brief(lab.check()), "picture", lab.picture_stats(os.path.join(HERE, "once-resize-pic.png")), "problems", lab.problems())
    save(lab, "once-resize.png")
    lab.click("#secExport > summary"); lab.click("#exportStart"); time.sleep(0.6)
    lab.p.call("Emulation.setDeviceMetricsOverride", width=900, height=700, deviceScaleFactor=1, mobile=False); time.sleep(0.5)
    lab.p.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
    t0 = time.time()
    while time.time() - t0 < 240 and lab.js("return squaringLab.exportBusy();"):
        time.sleep(0.5)
    out("job after resize:", lab.js(PANEL), "took", round(time.time() - t0, 1), "idle", lab.wait_idle(120), "problems", lab.problems())
    lab.close()

if which == "hidden":
    lab = Lab()
    lab.wait_idle(240)
    win = lab.p.call("Browser.getWindowForTarget", targetId=lab.target_id)
    state = {"way": "minimise", "t2": None}

    def hide(on):
        if state["way"] == "minimise":
            try:
                lab.p.call("Browser.setWindowBounds", windowId=win["windowId"], bounds={"windowState": "minimized" if on else "normal"})
            except Exception as e:
                out("setWindowBounds failed:", str(e)[:200])
        elif state["way"] == "tab":
            lab.p.call("Target.activateTarget", targetId=state["t2"] if on else lab.target_id)
        else:
            lab.p.call("Page.setWebLifecycleState", state="frozen" if on else "active")
        time.sleep(0.6)
        return lab.js("return [document.hidden, document.visibilityState];") if state["way"] != "freeze" or not on else ["frozen"]

    r = hide(True)
    out("hidden by minimising:", r)
    if not r[0]:
        hide(False)
        state["t2"] = lab.p.call("Target.createTarget", url="about:blank")["targetId"]
        state["way"] = "tab"
        time.sleep(0.6)
        r = lab.js("return [document.hidden, document.visibilityState];")
        out("hidden by a new tab in front:", r)
    out("shown again:", hide(False), "way:", state["way"])
    lab.click("#secQuality > summary"); lab.click("#qFine"); time.sleep(0.3)
    c1 = lab.check(); out("drawing:", c1["status"], "| hide ->", hide(True))
    time.sleep(5)
    c2 = lab.check(); out("while hidden 5 s:", c2["status"], "idle", c2["idle"])
    out("show ->", hide(False), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats(), "problems", lab.problems())
    lab.click("#secExport > summary")
    lab.js(SIZE3)
    lab.click("#exportStart"); time.sleep(1.0)
    p1 = lab.js(PANEL); out("job started:", p1, "| hide ->", hide(True))
    time.sleep(8)
    p2 = lab.js(PANEL); out("after 8 s hidden:", p2)
    out("show ->", hide(False))
    t0 = time.time()
    while time.time() - t0 < 300 and lab.js("return squaringLab.exportBusy();"):
        time.sleep(0.5)
    out("job end:", lab.js(PANEL), "took", round(time.time() - t0, 1), "problems", lab.problems())
    lab.js("squaringLab.resetAll();"); lab.wait_idle(120)
    lab.click("#par-mercator-liftPlay"); time.sleep(0.8); hide(True); time.sleep(3); hide(False); time.sleep(1.0)
    out("sweep after hidden spell:", lab.js("return { playing: document.querySelectorAll('.dial.is-playing').length, lift: squaringLab.S.param.mercator.lift };"))
    lab.click("#par-mercator-liftPlay"); out("idle after", lab.wait_idle(120), brief(lab.check()), "problems", lab.problems())
    save(lab, "once-hidden.png"); lab.close()

if which == "context":
    lab = Lab()
    lab.wait_idle(240)
    LOSE = "const gl = document.getElementById('view').getContext('webgl2'); window.__ext = window.__ext || gl.getExtension('WEBGL_lose_context'); window.__ext.loseContext(); await new Promise(r => setTimeout(r, 300)); return gl.isContextLost();"
    REST = "window.__ext.restoreContext(); await new Promise(r => setTimeout(r, 300)); return document.getElementById('view').getContext('webgl2').isContextLost();"
    out("1. lost at rest:", lab.js(LOSE), brief(lab.check()))
    save(lab, "once-context-lost.png")
    out("   picture while lost:", lab.picture_stats())
    lab.click("#mode-j"); time.sleep(0.5)
    out("   a mode change while lost:", brief(lab.check()), "problems", lab.problems())
    out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats(), "problems", lab.problems())
    save(lab, "once-context-restored.png")
    lab.click("#secQuality > summary"); lab.click("#qFine"); time.sleep(0.25)
    out("2. lost mid-draw:", lab.js(LOSE), brief(lab.check()))
    time.sleep(1.5)
    out("   1.5 s later:", brief(lab.check()))
    out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats(), "problems", lab.problems())
    lab.click("#qBal"); lab.wait_idle(120)
    lab.click("#secExport > summary")
    lab.js(SIZE3)
    lab.click("#exportStart"); time.sleep(0.8)
    out("3. picture job running:", lab.js(PANEL))
    out("   lost during the job:", lab.js(LOSE)); time.sleep(1.5)
    out("   panel:", lab.js(PANEL), brief(lab.check()), "problems", lab.problems())
    save(lab, "once-context-job.png")
    out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats())
    time.sleep(1); out("   panel after restore:", lab.js(PANEL))
    r = lab.js("const b = [...document.querySelectorAll('#exportPanel button')].find(b => __w.vis(b) && /Start/.test(b.textContent)); if (!b) return 'no start button'; b.click(); return b.textContent;")
    t0 = time.time(); time.sleep(0.5)
    while time.time() - t0 < 240 and lab.js("return squaringLab.exportBusy();"):
        time.sleep(0.5)
    out("   a new job after restore (%s):" % r, lab.js(PANEL), "took", round(time.time() - t0, 1), "problems", lab.problems())
    lab.click("#secMesh > summary"); lab.click("#meshStart"); time.sleep(1.2)
    out("4. model job running:", lab.js(MPANEL))
    out("   lost during the job:", lab.js(LOSE)); time.sleep(2)
    out("   panel:", lab.js(MPANEL), brief(lab.check()), "problems", lab.problems())
    out("   restored: still lost?", lab.js(REST), "idle after", lab.wait_idle(240), brief(lab.check()), "picture", lab.picture_stats())
    time.sleep(1); out("   panel after restore:", lab.js(MPANEL), "problems", lab.problems())
    save(lab, "once-context-end.png"); lab.close()

if which == "empty":
    lab = Lab()
    lab.wait_idle(240)
    lab.click("#secQuality > summary")
    Q = "const e = document.querySelector(%s); return { value: e.value, invalid: e.getAttribute('aria-invalid'), active: document.activeElement === e, steps: squaringLab.S.q.steps, iter: squaringLab.S.iter, n: squaringLab.S.n, zmin: squaringLab.S.view.zmin, zmax: squaringLab.S.view.zmax };"
    for sel, txt, commit in (("#qstepsNum", "", "Enter"), ("#qstepsNum", "", "Tab"), ("#iterNum", "", "Enter"), ("#powNum", "", "Tab"), ("#camFar", "", "Enter"), ("#camNear", "", "Tab")):
        lab.retype(sel, txt); lab.key(commit); time.sleep(0.3)
        out(sel, repr(txt), commit, "->", lab.js(Q % json.dumps(sel)))
    for sel in ("#qstepsNum", "#iterNum"):
        lab.click(sel, count=3)
        lab.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key="Delete", code="Delete", windowsVirtualKeyCode=46)
        lab.p.call("Input.dispatchKeyEvent", type="keyUp", key="Delete", code="Delete", windowsVirtualKeyCode=46)
        v1 = lab.js("return document.querySelector(%s).value;" % json.dumps(sel))
        lab.key("Enter"); time.sleep(0.3)
        out(sel, "select all, Delete (box now %r), Enter ->" % v1, lab.js(Q % json.dumps(sel)))
        lab.click("#status"); time.sleep(0.3)
        out("   after clicking elsewhere:", lab.js(Q % json.dumps(sel)))
        time.sleep(2.0)
        out("   2 s later:", lab.js(Q % json.dumps(sel)))
    out("problems", lab.problems()); lab.close()
