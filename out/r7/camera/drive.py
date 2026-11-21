"""Engineer "camera", fix pass 7: drive one page like tools/shot.py, but optionally as a touch phone, and with
REAL input (Tab presses, mouse clicks, finger taps and drags) beside page script.

  python out/r7/camera/drive.py --url dist/r7-camera.html --size 375x812 --phone --actions out/r7/camera/steps.json

Each action is an object with any of. They run in this order: size, js, tab, click, tap, swipe, text, key, sleep, wait, shot.
  "js":     page script (may await; the value of a final `return` is printed)
  "size":   [w, h]   change the window size (then pauses 0.6 s)
  "tab":    n      press the real Tab key n times; prints the id of the focused element after each press
  "key":    "ArrowUp" | "Enter" | ...   one real key press on whatever has the focus
  "text":   "12"   real typed text into the focused element
  "click":  [selector, fx, fy]          a real mouse click at that fraction of the element's box
  "tap":    [selector, fx, fy]          a real finger tap
  "swipe":  [selector, fx0, fy0, fx1, fy1]   a real one-finger drag inside the element's box
  "sleep":  seconds
  "wait":   expression polled until truthy ("done" = the picture is fully drawn), "timeout": seconds
  "shot":   png path, "clip": css selector (default the whole window)
Exit code 0, 2 (a wait timed out) or 3 (the page raised errors), as tools/shot.py.
"""
import argparse, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES, DONE  # noqa: E402

VK = {"Tab": 9, "Enter": 13, "Escape": 27, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40,
      "PageUp": 33, "PageDown": 34, "End": 35, "Home": 36}


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True); ap.add_argument("--size", default="1400x950"); ap.add_argument("--theme", default="dark")
    ap.add_argument("--phone", action="store_true"); ap.add_argument("--actions", required=True)
    a = ap.parse_args()
    with open(a.actions, encoding="utf-8") as f:
        actions = json.load(f)
    url = a.url if a.url.startswith(("file:", "http")) else "file:///" + os.path.abspath(a.url).replace("\\", "/")
    w, h = (int(x) for x in a.size.lower().split("x"))
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="camr7-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    code = 0
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
        page = Page(WS(target))
        page.call("Runtime.enable"); page.call("Log.enable"); page.call("Page.enable")
        page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=bool(a.phone))
        if a.phone:
            page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": a.theme}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        page.call("Page.navigate", url=url)
        page.wait("document.readyState === 'complete'", 30)
        time.sleep(0.5)

        def at(sel, fx=0.5, fy=0.5):
            b = page.js("const b = document.querySelector(%s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))
            return b[0] + b[2] * fx, b[1] + b[3] * fy

        def touch(kind, pts):
            page.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])

        for i, act in enumerate(actions):
            n = i + 1
            if "size" in act:
                page.call("Emulation.setDeviceMetricsOverride", width=int(act["size"][0]), height=int(act["size"][1]), deviceScaleFactor=1, mobile=bool(a.phone))
                time.sleep(0.6)
            if "js" in act:
                val = page.js(act["js"])
                if val is not None:
                    print("step %d result: %s" % (n, json.dumps(val, ensure_ascii=False)))
            if "tab" in act:
                seen = []
                for _ in range(int(act["tab"])):
                    page.call("Input.dispatchKeyEvent", type="rawKeyDown", key="Tab", code="Tab", windowsVirtualKeyCode=9)
                    page.call("Input.dispatchKeyEvent", type="keyUp", key="Tab", code="Tab", windowsVirtualKeyCode=9)
                    seen.append(page.js("const e = document.activeElement, r = e.getBoundingClientRect(); return (e.id || e.tagName) + '@' + Math.round(r.left) + ',' + Math.round(r.top);"))
                print("step %d tab order: %s" % (n, "  ".join(seen)))
            if "click" in act:
                sel, fx, fy = (act["click"] + [0.5, 0.5])[:3]
                x, y = at(sel, fx, fy)
                page.call("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
                page.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
                page.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
            if "tap" in act:
                sel, fx, fy = (act["tap"] + [0.5, 0.5])[:3]
                touch("touchStart", [at(sel, fx, fy)]); time.sleep(0.05); touch("touchEnd", [])
                time.sleep(0.35)
            if "swipe" in act:
                sel, fx0, fy0, fx1, fy1 = act["swipe"]
                x0, y0 = at(sel, fx0, fy0); x1, y1 = at(sel, fx1, fy1)
                touch("touchStart", [(x0, y0)])
                for s in range(1, 9):
                    touch("touchMove", [(x0 + (x1 - x0) * s / 8, y0 + (y1 - y0) * s / 8)]); time.sleep(0.03)
                time.sleep(0.25); touch("touchEnd", []); time.sleep(0.2)
            if "text" in act:
                page.call("Input.insertText", text=act["text"])
            if "key" in act:
                k = act["key"]
                page.call("Input.dispatchKeyEvent", type="rawKeyDown", key=k, code=k, windowsVirtualKeyCode=VK[k])
                page.call("Input.dispatchKeyEvent", type="keyUp", key=k, code=k, windowsVirtualKeyCode=VK[k])
            if "sleep" in act:
                time.sleep(float(act["sleep"]))
            if "wait" in act:
                expr = DONE if act["wait"] == "done" else act["wait"]
                t0 = time.time()
                if page.wait(expr, float(act.get("timeout", 120))):
                    print("step %d waited %.1f s" % (n, time.time() - t0))
                else:
                    print("step %d TIMED OUT waiting for: %s" % (n, act["wait"])); code = 2
            if "shot" in act:
                page.shot(os.path.join(ROOT, act["shot"]), act.get("clip"))
                print("step %d wrote %s" % (n, act["shot"]))
        page.js("return 0;")
        if page.problems:
            print("PAGE PROBLEMS (%d):" % len(page.problems))
            for p in page.problems[:40]:
                print("  " + p[:600])
            code = code or 3
        else:
            print("no console errors")
        try: page.call("Browser.close")
        except Exception: pass
    finally:
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
