"""Shared driver for the layout tester: starts headless Chrome, loads dist/preview.html, real input helpers."""
import base64, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

URL = "file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/")
IDLE = "window.squaringLab && window.squaringLab.idle && window.squaringLab.idle()"
KEYS = {"Tab": 9, "Enter": 13, "Escape": 27, " ": 32, "PageUp": 33, "PageDown": 34, "End": 35, "Home": 36, "ArrowLeft": 37,
        "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40, "f": 70}
CODES = {" ": "Space", "f": "KeyF"}
SHIFT = 8


class Lab:
    def __init__(self, w=1400, h=950, theme="dark", mobile=False, load=True, wait_idle=120):
        for s in (sys.stdout, sys.stderr):
            try: s.reconfigure(encoding="utf-8", errors="replace")
            except Exception: pass
        chrome = next((c for c in CHROMES if os.path.exists(c)), None)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix="layout-")
        self.proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + self.prof,
                                      "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                                      "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=1", "about:blank"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            raise RuntimeError("Chrome did not start")
        self.p = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            self.p.call(m)
        self.size(w, h, mobile)
        self.theme(theme)
        self.p.call("Emulation.setFocusEmulationEnabled", enabled=True)
        if load:
            self.load(wait_idle)

    def size(self, w, h, mobile=False):
        self.w, self.h, self.mobile = w, h, mobile
        self.p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)
        if mobile:
            self.p.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)

    def theme(self, t):
        self.p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": t}])

    def load(self, wait_idle=120):
        self.p.call("Page.navigate", url=URL)
        self.p.wait("document.readyState === 'complete'", 40)
        time.sleep(0.4)
        if wait_idle:
            return self.idle(wait_idle)

    def idle(self, timeout=120):
        t0 = time.time()
        ok = self.p.wait(IDLE, timeout)
        print("   idle=%s after %.1f s" % (ok, time.time() - t0)); sys.stdout.flush()
        return ok

    def js(self, code):
        return self.p.js(code)

    def shot(self, path, clip=None):
        params = {"format": "png", "captureBeyondViewport": False}
        if clip:
            params["clip"] = {"x": clip[0], "y": clip[1], "width": clip[2], "height": clip[3], "scale": 1}
        data = self.p.call("Page.captureScreenshot", **params)["data"]
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))

    def shot_el(self, path, sel, pad=6):
        box = self.js("const e = document.querySelector(%s); if (!e) return null; e.scrollIntoView({block: 'center'});"
                      "await new Promise(r => setTimeout(r, 150)); const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))
        if not box:
            print("   no element for", sel); return
        x, y = max(0, box[0] - pad), max(0, box[1] - pad)
        self.shot(path, [x, y, box[2] + 2 * pad, box[3] + 2 * pad])

    def tiles(self, prefix, overlap=0):
        """Scroll through the whole page and save one window-sized picture per screenful. Returns the paths."""
        H = self.js("return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);")
        paths, y, i = [], 0, 0
        while True:
            self.js("window.scrollTo(0, %d); await new Promise(r => setTimeout(r, 220));" % y)
            real = self.js("return window.scrollY;")
            path = "%s-%02d.png" % (prefix, i)
            self.shot(path)
            paths.append((path, real))
            if real + self.h >= H - 1:
                break
            y += self.h - overlap; i += 1
            if i > 60: break
        self.js("window.scrollTo(0, 0);")
        return paths, H

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click_xy(self, x, y, count=1):
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", clickCount=count)
        self.mouse("mouseReleased", x, y, button="left", clickCount=count)

    def key(self, name, modifiers=0, text=None):
        kw = dict(key=name, code=CODES.get(name, name), windowsVirtualKeyCode=KEYS[name], modifiers=modifiers)
        if text is not None:
            self.p.call("Input.dispatchKeyEvent", type="keyDown", text=text, unmodifiedText=text, **kw)
        else:
            self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def close(self):
        problems = list(self.p.problems)
        try: self.p.js("return 0;")
        except Exception: pass
        problems = list(self.p.problems)
        try: self.p.call("Browser.close")
        except Exception: pass
        try: self.proc.wait(timeout=5)
        except Exception: self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)
        return problems
