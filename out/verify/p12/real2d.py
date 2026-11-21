import json, os, sys, time, socket, subprocess, tempfile, shutil, urllib.request, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
spec = importlib.util.spec_from_file_location("camreal", os.path.join(ROOT, "notes", "camera_real.py")); cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
from shot import WS, Page, CHROMES
L = "window.squaringLab"
def say(*a): print(*a); sys.stdout.flush()
def main():
    chrome = next(c for c in CHROMES if os.path.exists(c))
    with socket.socket() as probe: probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p12real-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof, "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get("type") == "page"]
                if pages: target = pages[0]["webSocketDebuggerUrl"]; break
            except Exception: pass
            time.sleep(0.2)
        page = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"): page.call(m)
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        d = cr.Drive(page)
        page.call("Page.navigate", url="file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/"))
        page.wait("document.readyState === 'complete'", 30); page.wait(L + " && " + L + ".idle()", 300); time.sleep(0.3)
        def shot(n, clip="#stage"):
            page.shot(os.path.join(HERE, n), clip); say("   wrote", n)
        def idle():
            page.wait(L + ".idle()", 300); time.sleep(0.15)
        v2 = lambda: d.js("return Object.assign({}, %s.S.v2);" % L)
        cam = lambda: cr.cam(d)
        d.js("%s.R.warmOn = false; %s.S.q.aa = 4; window.scrollTo(0, 0);" % (L, L))
        # move the 3D camera somewhere particular first
        cx, cy = d.at("#view")
        d.drag(cx, cy, cx + 90, cy + 40); d.wheel(cx, cy, -200); d.settle(); time.sleep(0.3)
        c0 = cam(); say("3D cam before 2D:", c0)
        d.click("#flat"); time.sleep(0.4)
        say("after real click on #flat: flat =", d.js("return %s.S.flat;" % L), "v2 =", v2(), "cam =", cam())
        idle(); shot("c1-2d-after-3d-move.png")
        # ---- drag pans
        a = v2(); H = d.box("#view")[3]
        d.drag(cx, cy, cx + 100, cy + 50); b = v2()
        say("drag +100,+50 px: dx=%.6f (want %.6f) dy=%.6f (want %.6f)" % (b["x"] - a["x"], -100 * a["h"] / H, b["y"] - a["y"], 50 * a["h"] / H))
        bx = d.box("#view"); a = v2(); d.drag(cx, cy, bx[0] + bx[2] + 120, cy); b = v2()
        say("drag out of the stage: dx=%.6f (want %.6f)" % (b["x"] - a["x"], -(bx[0] + bx[2] + 120 - cx) * a["h"] / H))
        a = v2(); d.drag(cx, cy, cx + 60, cy, modifiers=8); b = v2(); say("shift-drag: dx=%.6f" % (b["x"] - a["x"]))
        a = v2(); d.drag(cx, cy, cx, cy + 60, button="right", buttons=2); b = v2(); say("right-drag: dy=%.6f" % (b["y"] - a["y"]))
        # ---- wheel zooms about the cursor
        px, py = d.at("#view", 0.3, 0.7)
        pick = lambda: d.js("const r = document.getElementById('view').getBoundingClientRect(); return %s.pick(%f - r.left, %f - r.top);" % (L, px, py))
        a = v2(); p0 = pick(); d.mouse("mouseMoved", px, py)
        y0 = d.js("return window.scrollY;")
        for _ in range(5):
            d.wheel(px, py, -100); time.sleep(0.05)
        d.settle(); time.sleep(0.3); b = v2(); p1 = pick()
        say("5 notches in at (0.3,0.7): h ratio %.6f (want %.6f); point under cursor before %s after %s; page scrolled %s" % (b["h"] / a["h"], 1.12 ** -5, p0, p1, d.js("return window.scrollY;") - y0))
        for _ in range(5):
            d.wheel(px, py, 100); time.sleep(0.05)
        d.settle(); time.sleep(0.3); c = v2(); say("5 notches out again: h ratio to start %.6f, centre moved by (%.2e, %.2e)" % (c["h"] / a["h"], c["x"] - a["x"], c["y"] - a["y"]))
        # ---- double-click centres
        idle(); a = v2(); p0 = pick(); d.click("#view", count=2, fx=0.3, fy=0.7); d.settle(); time.sleep(0.4); b = v2()
        say("double-click at (0.3,0.7): picked %s, new centre (%.5f, %.5f), h %.5f -> %.5f" % (p0, b["x"], b["y"], a["h"], b["h"]))
        # ---- keys
        d.js("document.getElementById('view').focus();"); a = v2(); d.press("ArrowRight", 0.3); d.settle(); b = v2(); say("ArrowRight 0.3 s: dx=%.4f dy=%.4f" % (b["x"] - a["x"], b["y"] - a["y"]))
        a = v2(); d.press("ArrowUp", 0.3); d.settle(); b = v2(); say("ArrowUp 0.3 s: dx=%.4f dy=%.4f" % (b["x"] - a["x"], b["y"] - a["y"]))
        a = v2(); page.call("Input.dispatchKeyEvent", type="keyDown", key="+", code="Equal", windowsVirtualKeyCode=187, text="+"); page.call("Input.dispatchKeyEvent", type="keyUp", key="+", code="Equal", windowsVirtualKeyCode=187); d.settle(); time.sleep(0.3); b = v2(); say("plus key: h %.4f -> %.4f" % (a["h"], b["h"]))
        d.press("KeyF"); time.sleep(0.2); say("F key in 2D: fly =", d.js("return %s.S.view.fly;" % L), "stage cam =", d.js("return document.getElementById('stage').dataset.cam;"))
        # ---- zoom buttons and the slider
        a = v2(); d.click("#zoomIn"); d.settle(); time.sleep(0.3); b = v2(); say("zoomIn button: h %.4f -> %.4f" % (a["h"], b["h"]))
        rb = d.box("#camRail"); rx = rb[0] + rb[2] / 2
        d.drag(rx, rb[1] + rb[3] * 0.8, rx, rb[1] + rb[3] * 0.5, steps=10); d.settle(); b = v2(); say("slider dropped at the middle: h = %.6f (log middle of 0.0005..40 is %.6f); zoom text %r" % (b["h"], (0.0005 * 40) ** 0.5, d.js("return document.getElementById('camZoom').innerText;")))
        idle(); shot("c2-slider-mid.png")
        # ---- Reset view
        d.click("#reset"); d.settle(); time.sleep(0.3); say("Reset view (real click) in 2D: v2 =", v2(), "cam =", cam()); idle(); shot("c3-after-reset.png")
        # ---- slice height
        d.js("document.querySelectorAll('details.sec').forEach(x => { x.open = true; }); document.getElementById('cutNum').scrollIntoView({block: 'center'});")
        time.sleep(0.2)
        d.click("#cutNum", count=3); page.call("Input.insertText", text="0.35"); d.press("Enter"); time.sleep(0.3)
        say("typed slice height 0.35: S.cut =", d.js("return %s.S.cut;" % L), "cutOn =", d.js("return %s.S.cutOn;" % L), "| stage text:", repr(d.js("return document.getElementById('stage').innerText;")), "| flat label:", repr(d.js("return document.getElementById('flatHost').textContent;")), "| status:", d.js("return document.getElementById('status').textContent;"))
        idle(); d.js("window.scrollTo(0,0);"); time.sleep(0.2); shot("c4-slice-035.png"); shot("c4-page-slice-035.png", None)
        d.js("const L = %s; L.S.cut = 0; L.syncControls(); L.touch();" % L)
        # ---- controls that mean nothing in 2D
        idle()
        d.js("window.__px = () => { const c = document.getElementById('view'); const t = document.createElement('canvas'); t.width = 96; t.height = 96; const g = t.getContext('2d'); g.drawImage(c, 0, 0, 96, 96); return Array.from(g.getImageData(0, 0, 96, 96).data).reduce((a, b, i) => a + b * (1 + i % 7), 0); };")
        def sig():
            time.sleep(0.5); idle(); return d.js("return await new Promise(r => requestAnimationFrame(() => r(window.__px())));")
        s0 = sig(); say("checksum now", s0, "and again", sig())
        for what, js in [("light azimuth 250 -> 40", "L.S.lightAz = 40;"), ("shadows off", "L.S.q.shadow = false;"), ("crevice shading off", "L.S.q.ao = false;"), ("field of view 0.32 -> 0.6", "L.S.view.fov = 0.6;"), ("drawing radius 8 -> 1", "L.S.view.bound = 1;"), ("ray steps 260 -> 60", "L.S.q.steps = 60;"), ("distance estimate 3 -> 0", "L.S.q.de = 0;"), ("surface threshold 1 -> 3", "L.S.q.detail = 3;"), ("step size 0.8 -> 0.3", "L.S.q.stepk = 0.3;"), ("slope from sampled", "L.S.q.normals = 'smooth';")]:
            d.js("const L = %s; %s L.syncControls(); L.touch();" % (L, js)); s1 = sig(); say("in 2D, %s: picture %s (checksum %s -> %s)" % (what, "UNCHANGED" if s1 == s0 else "changed", s0, s1)); s0 = s1
        shot("c9-after-nothing-controls.png")
        d.js("const L = %s; L.S.lightAz = 250; L.S.q.shadow = true; L.S.q.ao = true; L.S.view.fov = 0.32; L.S.view.bound = 8; L.S.q.steps = 260; L.S.q.de = 3; L.S.q.detail = 1; L.S.q.stepk = 0.8; L.S.q.normals = 'sharp'; L.syncControls(); L.touch();" % L)
        d.js("document.getElementById('viewFly').scrollIntoView({block: 'center'});"); time.sleep(0.2); d.click("#viewFly"); time.sleep(0.3)
        say("real click on 'Fly camera' checkbox in 2D: fly =", d.js("return %s.S.view.fly;" % L), "checked =", d.js("return document.getElementById('viewFly').checked;"), "disabled =", d.js("return document.getElementById('viewFly').disabled;"), "stage cam =", d.js("return document.getElementById('stage').dataset.cam;"), "hint =", repr(d.js("return document.querySelector('.hint').textContent;")))
        if d.js("return %s.S.view.fly;" % L):
            d.click("#viewFly"); time.sleep(0.2)
        # ---- 2D off: same 3D camera?
        d.js("window.scrollTo(0,0);"); time.sleep(0.2); d.drag(cx, cy, cx + 70, cy - 30); d.wheel(cx, cy, -300); d.settle(); time.sleep(0.3)
        say("2D view panned/zoomed to", v2()); d.click("#flat"); time.sleep(0.4); c1 = cam()
        say("2D off: cam =", c1, "| SAME as before 2D:", all(abs(c0[k] - c1[k]) < 1e-9 for k in ("yaw", "pitch", "dist")) and all(abs(x - y) < 1e-9 for x, y in zip(c0["target"], c1["target"])), "| camMode hidden:", d.js("return document.getElementById('camMode').hidden;"), "hint:", repr(d.js("return document.querySelector('.hint').textContent;")))
        idle(); shot("c10-back-in-3d.png")
        d.click("#flat"); time.sleep(0.4); say("2D on again: v2 =", v2(), "(kept from before?)")
        # ---- deep zoom
        d.js("const L = %s; L.S.iter = 300; L.S.colour.mode = 2; L.S.v2.x = -0.743643887; L.S.v2.y = 0.131825904; L.S.v2.h = 0.02; L.syncControls(); L.touch();" % L); idle(); shot("c5-deep-h0.02.png")
        say("iter now", d.js("return %s.S.iter;" % L), "iter box", d.js("return document.getElementById('iterNum').value + ' max ' + document.getElementById('iter').max;"))
        d.mouse("mouseMoved", cx, cy)
        for _ in range(60):
            d.wheel(cx, cy, -300); time.sleep(0.02)
        d.settle(); time.sleep(0.5); idle(); say("wheel in to the stop: v2 =", v2(), "| stage text:", repr(d.js("return document.getElementById('stage').innerText;")), "| status:", d.js("return document.getElementById('status').textContent;"), "| hint:", repr(d.js("return document.querySelector('.hint').textContent;")))
        shot("c6-deep-hmin-default.png")
        d.click("#camNear", count=3); page.call("Input.insertText", text="0.00001"); d.press("Enter"); time.sleep(0.2); say("near box typed 0.00001: hmin =", v2()["hmin"], "box shows", d.js("return document.getElementById('camNear').value;"))
        d.click("#camNear", count=3); page.call("Input.insertText", text="0.000001"); d.press("Enter"); time.sleep(0.2); say("near box typed 0.000001: hmin =", v2()["hmin"], "box shows", d.js("return document.getElementById('camNear').value;"), "aria-invalid", d.js("return document.getElementById('camNear').getAttribute('aria-invalid');"), "title", repr(d.js("return document.getElementById('camNear').title;")))
        d.js("const L = %s; L.S.v2.h = 5e-5; L.touch();" % L); idle(); shot("c7-deep-h5e-5.png")
        d.js("const L = %s; L.S.v2.h = 1e-5; L.touch();" % L); idle(); shot("c8-deep-h1e-5.png")
        say("at h = 1e-5: stage text:", repr(d.js("return document.getElementById('stage').innerText;")), "| status:", d.js("return document.getElementById('status').textContent;"), "| hint:", repr(d.js("return document.querySelector('.hint').textContent;")), "| busy:", repr(d.js("const b = document.getElementById('busy'); return b && !b.hidden ? b.textContent : '';")))
        page.js("return 0;"); say("PAGE PROBLEMS:", page.problems[:10])
        try: page.call("Browser.close")
        except Exception: pass
    finally:
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
main()
