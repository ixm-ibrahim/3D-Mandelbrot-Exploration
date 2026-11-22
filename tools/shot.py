"""Drive the lab in headless Chrome: run JavaScript in the page, wait, and save screenshots.

One sequence:
  python tools/shot.py --js "document.getElementById('mode-j').click()" --wait-done --shot julia.png --clip "#stage"

Several steps, from a JSON file holding a list of actions:
  python tools/shot.py --actions steps.json
  Each action is an object with any of:
    "js":      JavaScript to run in the page (may use await; the value of a final `return` is printed)
    "wait":    a JavaScript expression polled until it is truthy ("done" stands for: the picture is fully drawn)
    "timeout": seconds to allow for that wait (default 90)
    "sleep":   seconds to pause
    "shot":    path of a PNG to write
    "clip":    CSS selector whose box is captured (default: the whole window)

Other flags: --wait EXPRESSION (in place of --wait-done), --timeout SECONDS (default 90), --url (default:
dist/preview.html), --size 1400x950, --theme dark|light.
Everything the page logs with console.error or console.warn, and any uncaught exception, is printed at the end.
Exit code: 0 on success, 2 if a wait timed out, 3 if the page raised errors.

From Python: `with open_page(url) as page:` gives a Page with js(), wait(), shot() and the list `problems`.
"""
import argparse, base64, contextlib, json, os, shutil, socket, struct, subprocess, sys, tempfile, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "dist", "preview.html")
CHROMES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]
DONE = "window.squaringLab && window.squaringLab.idle && window.squaringLab.idle()"


class WebSocket:
    """A minimal client: enough for the Chrome DevTools protocol."""

    def __init__(self, url):
        assert url.startswith("ws://")
        hostport, path = url[5:].split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)), timeout=120)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n") % (path, hostport, key)
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        if b" 101 " not in buf.split(b"\r\n", 1)[0]:
            raise RuntimeError("websocket handshake failed: %r" % buf[:200])
        self.rest = buf.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.rest) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError("connection closed")
            self.rest += chunk
        out, self.rest = self.rest[:n], self.rest[n:]
        return out

    def send(self, text):
        data = text.encode()
        head = bytearray([0x81])
        n = len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127)
            head += struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        self.s.sendall(bytes(head) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        parts = []
        while True:
            b0, b1 = self._read(2)
            op, n = b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            data = self._read(n)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if op == 0x9:  # ping
                self.s.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
                continue
            if op == 0x8:
                raise RuntimeError("websocket closed by the browser")
            parts.append(data)
            if b0 & 0x80:
                return b"".join(parts).decode("utf-8", "replace")


class Page:
    def __init__(self, ws):
        self.ws, self.n, self.problems = ws, 0, []

    def call(self, method, **params):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"]))
                return msg.get("result", {})
            self._event(msg)

    def _event(self, msg):
        m, p = msg.get("method"), msg.get("params", {})
        if m == "Runtime.exceptionThrown":
            d = p.get("exceptionDetails", {})
            self.problems.append("EXCEPTION: " + (d.get("exception", {}).get("description") or d.get("text", "")))
        elif m == "Runtime.consoleAPICalled" and p.get("type") in ("error", "warning", "assert"):
            args = " ".join(str(a.get("value", a.get("description", ""))) for a in p.get("args", []))
            self.problems.append("console.%s: %s" % (p["type"], args))
        elif m == "Log.entryAdded" and p.get("entry", {}).get("level") == "error":
            e = p["entry"]
            if "favicon" not in e.get("url", "") and "fonts.g" not in e.get("url", ""):
                self.problems.append("log error: %s %s" % (e.get("text", ""), e.get("url", "")))

    def js(self, code):
        """Run code in the page: the body of an async function, which may end in `return`."""
        expr = "(async () => { %s\n})()" % code
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True, userGesture=True)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError("page script failed: " + (d.get("exception", {}).get("description") or d.get("text", "")))
        return r.get("result", {}).get("value")

    def wait(self, expr, timeout=90):
        end = time.time() + timeout
        while time.time() < end:
            if self.js("return !!(%s);" % (DONE if expr == "done" else expr)):
                return True
            time.sleep(0.25)
        return False

    def shot(self, path, clip=None):
        params = {"format": "png"}
        if clip:
            box = self.js("const e = document.querySelector(%s); if (!e) return null; e.scrollIntoView({block: 'center'}); "
                          "await new Promise(r => setTimeout(r, 150)); const b = e.getBoundingClientRect(); "
                          "return [b.left + window.scrollX, b.top + window.scrollY, b.width, b.height];" % json.dumps(clip))
            if not box:
                raise RuntimeError("nothing matches the clip selector %s" % clip)
            # Capture inside the window as it is. Capturing beyond the viewport makes Chrome resize the page
            # for a moment, which the lab sees as a resize and answers by redrawing its quick preview.
            params["clip"] = {"x": box[0], "y": box[1], "width": box[2], "height": box[3], "scale": 1}
            params["captureBeyondViewport"] = False
        data = self.call("Page.captureScreenshot", **params)["data"]
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))


def file_url(path_or_url):
    if path_or_url.startswith(("file:", "http:", "https:")):
        return path_or_url
    return "file:///" + os.path.abspath(path_or_url).replace("\\", "/")


@contextlib.contextmanager
def open_page(url=PREVIEW, size=(1400, 950), theme="dark"):
    """Start headless Chrome on url and yield its Page. Chrome is closed and its profile folder removed on exit."""
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("No Chrome or Edge found.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    profile = tempfile.mkdtemp(prefix="labshot-")
    w, h = size
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + profile,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get("type") == "page"]
                if pages:
                    target = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            sys.exit("Chrome did not start its debugging port.")
        page = Page(WebSocket(target))
        page.call("Runtime.enable")
        page.call("Log.enable")
        page.call("Page.enable")
        page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
        page.call("Page.navigate", url=file_url(url))
        if not page.wait("document.readyState === 'complete'", 30):
            print("WARNING: the page did not finish loading in 30 s")
        time.sleep(0.4)
        yield page
        try:
            page.call("Browser.close")
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def run(page, actions):
    """Play a list of actions. Returns 0, or 2 if a wait timed out."""
    code = 0
    for i, act in enumerate(actions, 1):
        if "js" in act:
            val = page.js(act["js"])
            if val is not None:
                print("step %d result: %s" % (i, json.dumps(val, ensure_ascii=False)))
        if "sleep" in act:
            time.sleep(float(act["sleep"]))
        if "wait" in act:
            limit, t0 = float(act.get("timeout", 90)), time.time()
            if page.wait(act["wait"], limit):
                print("step %d waited %.1f s" % (i, time.time() - t0))
            else:
                print("step %d TIMED OUT after %.0f s waiting for: %s" % (i, limit, act["wait"]))
                print("  status line: %r" % page.js("const s = document.getElementById('status'); return s ? s.textContent : null;"))
                code = 2
        if "shot" in act:
            page.shot(act["shot"], act.get("clip"))
            print("step %d wrote %s" % (i, act["shot"]))
    return code


def report(page):
    """Print what the page complained about. Returns 3 if there was anything, else 0."""
    if not page.problems:
        print("no console errors")
        return 0
    print("PAGE PROBLEMS (%d):" % len(page.problems))
    for p in page.problems[:40]:
        print("  " + p[:600])
    return 3


def utf8_output():
    """A Windows console cannot print signs like the minus sign or a raised n without this."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main():
    utf8_output()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=PREVIEW)
    ap.add_argument("--size", default="1400x950")
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--js")
    ap.add_argument("--wait")
    ap.add_argument("--wait-done", action="store_true")
    ap.add_argument("--timeout", type=float, default=90)
    ap.add_argument("--shot")
    ap.add_argument("--clip")
    ap.add_argument("--actions")
    a = ap.parse_args()

    if a.actions:
        with open(a.actions, encoding="utf-8") as f:
            actions = json.load(f)
    else:
        one = {"timeout": a.timeout}
        if a.js:
            one["js"] = a.js
        if a.wait_done or a.wait:
            one["wait"] = "done" if a.wait_done else a.wait
        if a.shot:
            one["shot"] = a.shot
        if a.clip:
            one["clip"] = a.clip
        actions = [one]

    w, h = (int(x) for x in a.size.lower().split("x"))
    with open_page(a.url, (w, h), a.theme) as page:
        code = run(page, actions)
        page.js("return 0;")  # a round trip, so that what the page logged last has arrived
        code = code or report(page)
    sys.exit(code)


if __name__ == "__main__":
    main()
