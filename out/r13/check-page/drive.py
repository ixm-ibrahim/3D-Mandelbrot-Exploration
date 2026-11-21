"""Checker's driver: the same headless Chrome as tools/shot.py (its WS and Page classes are reused), plus real
keyboard, mouse and touch input through the debugging protocol, a reload, and phone emulation."""
import sys, os, json, time, socket, tempfile, subprocess, shutil, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import shot as SH

for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

KEYS = {"Tab": (9, "Tab", ""), "Enter": (13, "Enter", "\r"), " ": (32, "Space", " "), "ArrowLeft": (37, "ArrowLeft", ""),
        "ArrowUp": (38, "ArrowUp", ""), "ArrowRight": (39, "ArrowRight", ""), "ArrowDown": (40, "ArrowDown", ""),
        "+": (187, "Equal", "+"), "-": (189, "Minus", "-")}

PRE = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rect = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
const vis = e => { if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && (e.checkVisibility ? e.checkVisibility({ visibilityProperty: true, contentVisibilityAuto: true }) : getComputedStyle(e).visibility !== 'hidden'); };
const mid = e => { const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const go = y => window.scrollTo({ top: y, behavior: 'instant' });
const probes = () => { let s = ''; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let i = 1; i < 8; i++) for (let j = 1; j < 8; j++) s += L.pick(w * i / 8, h * j / 8) ? '1' : '0'; return s; };
"""


class Session:
    def __init__(self, url, size, theme="light", mobile=False, dsf=1, name=""):
        self.url, self.size, self.theme, self.mobile, self.dsf, self.name = url, size, theme, mobile, dsf, name
        self.code = 0

    def __enter__(self):
        url = self.url
        if not url.startswith(("file:", "http:", "https:")):
            url = "file:///" + os.path.abspath(os.path.join(ROOT, url)).replace("\\", "/")
        w, h = (int(x) for x in self.size.lower().split("x"))
        self.w, self.h = w, h
        chrome = next((c for c in SH.CHROMES if os.path.exists(c)), None)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix="labchk-")
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
            raise RuntimeError("Chrome did not start its debugging port.")
        p = self.page = SH.Page(SH.WS(target))
        p.call("Runtime.enable"); p.call("Log.enable"); p.call("Page.enable")
        p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=self.dsf, mobile=self.mobile)
        if self.mobile:
            p.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        try: p.call("Emulation.setFocusEmulationEnabled", enabled=True)
        except Exception: pass
        p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": self.theme}])
        p.call("Page.navigate", url=url)
        if not p.wait("document.readyState === 'complete'", 30):
            print("WARNING: the page did not finish loading in 30 s")
        time.sleep(0.4)
        print("=== session %s: %s %s %s mobile=%s dsf=%s" % (self.name, self.url, self.size, self.theme, self.mobile, self.dsf))
        return self

    def __exit__(self, et, ev, tb):
        p = self.page
        try:
            p.js("return 0;")
            if p.problems:
                print("PAGE PROBLEMS (%d) in %s:" % (len(p.problems), self.name))
                for q in p.problems[:40]:
                    print("  " + q[:600])
            else:
                print("no console errors in %s" % self.name)
            try: p.call("Browser.close")
            except Exception: pass
        finally:
            try: self.proc.wait(timeout=5)
            except Exception: self.proc.kill()
            shutil.rmtree(self.prof, ignore_errors=True)
        if et:
            print("SESSION %s FAILED: %s: %s" % (self.name, et.__name__, ev))
            return True      # go on with the next session

    def js(self, code):
        return self.page.js(PRE + code)

    def wait(self, expr, timeout=240):
        t0 = time.time()
        ok = self.page.wait(expr, timeout)
        if not ok: print("  TIMED OUT after %.0f s waiting for %s" % (timeout, expr[:80]))
        return ok, time.time() - t0

    def done(self, timeout=300):
        return self.wait(SH.DONE, timeout)

    def shot(self, path):
        self.page.shot(os.path.join(HERE, path))

    def key(self, name, shift=False):
        vk, code, text = KEYS[name]
        kw = dict(key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=8 if shift else 0)
        if text: self.page.call("Input.dispatchKeyEvent", type="keyDown", text=text, **kw)
        else: self.page.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        self.page.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def mouse(self, typ, x, y, **kw):
        self.page.call("Input.dispatchMouseEvent", type=typ, x=x, y=y, **kw)

    def click(self, x, y):
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", buttons=1, clickCount=1)
        self.mouse("mouseReleased", x, y, button="left", buttons=0, clickCount=1)

    def drag(self, x0, y0, x1, y1, steps=8):
        self.mouse("mouseMoved", x0, y0)
        self.mouse("mousePressed", x0, y0, button="left", buttons=1, clickCount=1)
        for i in range(1, steps + 1):
            self.mouse("mouseMoved", x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, button="left", buttons=1)
        self.mouse("mouseReleased", x1, y1, button="left", buttons=0, clickCount=1)

    def wheel(self, x, y, dy):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy)

    def touch(self, typ, pts):
        self.page.call("Input.dispatchTouchEvent", type=typ, touchPoints=[{"x": p[0], "y": p[1], "id": i} for i, p in enumerate(pts)])

    def tap(self, x, y):
        if self.mobile:
            self.touch("touchStart", [[x, y]]); self.touch("touchEnd", [])
        else:
            self.click(x, y)

    def tdrag(self, x0, y0, x1, y1, steps=8):
        if not self.mobile:
            return self.drag(x0, y0, x1, y1, steps)
        self.touch("touchStart", [[x0, y0]])
        for i in range(1, steps + 1):
            self.touch("touchMove", [[x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps]])
        self.touch("touchEnd", [])

    def reload(self):
        self.page.call("Page.reload")
        time.sleep(0.5)
        self.page.wait("document.readyState === 'complete' && !!window.squaringLab", 30)
        time.sleep(0.4)


def show(label, val):
    print("  %s: %s" % (label, json.dumps(val, ensure_ascii=False) if not isinstance(val, str) else val))
