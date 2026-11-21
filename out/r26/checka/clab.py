"""Round 26, checker "arithmetic": a small driver for the lab in headless Chrome.

It reuses the websocket client of tools/shot.py (WS, Page) and adds what a measuring script needs: values back in
Python, pictures as numpy arrays, a window that can be resized, and a prelude of JavaScript helpers of my own.

    from clab import Lab
    with Lab('r26-checka', size=(1400, 950), theme='dark') as lab:
        v = lab.js("return LAB.learn.shape.state();")
        img = lab.grab('#stage')            # numpy uint8 (h, w, 3)
        lab.shot('out/r26/checka/x.png', '#stage')
    lab.problems  -> what the page logged with console.error / console.warn, and uncaught exceptions
"""
import base64, io, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import shot as _shot  # noqa: E402  (tools/shot.py)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

with open(os.path.join(HERE, "c_prelude.js"), encoding="utf-8") as _f:
    PRELUDE = _f.read()


class Lab:
    def __init__(self, page="r26-checka", size=(1400, 950), theme="dark", prelude=True, reduced=False):
        self.name, self.size, self.theme = page, size, theme
        url = "file:///" + os.path.join(ROOT, "dist", page + ".html").replace("\\", "/")
        chrome = next((c for c in _shot.CHROMES if os.path.exists(c)), None)
        if not chrome:
            raise RuntimeError("no Chrome or Edge")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix="labchk-")
        w, h = size
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
            raise RuntimeError("Chrome did not start its debugging port")
        self.page = _shot.Page(_shot.WS(target))
        p = self.page
        p.call("Runtime.enable"); p.call("Log.enable"); p.call("Page.enable")
        p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        feats = [{"name": "prefers-color-scheme", "value": theme}]
        if reduced:
            feats.append({"name": "prefers-reduced-motion", "value": "reduce"})
        p.call("Emulation.setEmulatedMedia", features=feats)
        p.call("Page.navigate", url=url)
        if not p.wait("document.readyState === 'complete'", 40):
            print("WARNING: the page did not finish loading in 40 s")
        time.sleep(0.5)
        self.prelude = PRELUDE if prelude else ""

    @property
    def problems(self):
        return self.page.problems

    def js(self, code):
        return self.page.js(self.prelude + "\n" + code)

    def wait(self, expr, timeout=60):
        return self.page.wait(expr, timeout)

    def idle(self, timeout=90):
        return self.page.wait(_shot.DONE, timeout)

    def resize(self, w, h):
        self.size = (w, h)
        self.page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)

    def shot(self, path, clip=None):
        if not os.path.isabs(path):
            path = os.path.join(ROOT, path)
        self.page.shot(path, clip)
        return path

    def png(self, clip=None):
        """PNG bytes of the window, or of the box of a selector, without scrolling anything."""
        params = {"format": "png"}
        if clip:
            box = self.page.js("const e = document.querySelector(%s); if (!e) return null; const b = e.getBoundingClientRect(); "
                               "return [b.left, b.top, b.width, b.height];" % json.dumps(clip))
            if not box:
                raise RuntimeError("nothing matches " + clip)
            params["clip"] = {"x": box[0], "y": box[1], "width": box[2], "height": box[3], "scale": 1}
            params["captureBeyondViewport"] = False
        return base64.b64decode(self.page.call("Page.captureScreenshot", **params)["data"])

    def grab(self, clip=None):
        return np.asarray(Image.open(io.BytesIO(self.png(clip))).convert("RGB"))

    def save(self, arr_or_png, path):
        if not os.path.isabs(path):
            path = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if isinstance(arr_or_png, (bytes, bytearray)):
            with open(path, "wb") as f:
                f.write(arr_or_png)
        else:
            Image.fromarray(arr_or_png).save(path)
        return path

    def close(self):
        try:
            self.page.js("return 0;")
        except Exception:
            pass
        try:
            self.page.call("Browser.close")
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def u8(b64):
    return np.frombuffer(base64.b64decode(b64), dtype=np.uint8)


class Log:
    """print and keep: everything goes to out/r26/checka/<name>.log as well."""

    def __init__(self, name):
        self.path = os.path.join(HERE, name + ".log")
        self.f = open(self.path, "w", encoding="utf-8")
        for stream in (sys.stdout, sys.stderr):
            try: stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception: pass
        self("log %s, %s" % (name, time.strftime("%Y-%m-%d %H:%M:%S")))

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        self.f.write(s + "\n"); self.f.flush()

    def problems(self, lab):
        if lab.problems:
            self("PAGE PROBLEMS (%d):" % len(lab.problems))
            for p in lab.problems[:40]:
                self("  " + p[:600])
        else:
            self("no console errors")
        return len(lab.problems)
