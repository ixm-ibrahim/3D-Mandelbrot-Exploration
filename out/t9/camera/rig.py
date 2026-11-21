"""Tester "camera", second check: one headless Chrome with REAL input (mouse, wheel, keys, touch), after
notes/camera_real.py and out/r7/camera/drive.py. Import and use:

    from rig import Rig, L
    with Rig(size=(1400, 950), phone=False, theme='dark') as d:
        d.load('dist/v8.html'); ...
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES, DONE  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

L = "window.squaringLab"
VK = {"Tab": 9, "Enter": 13, "Escape": 27, "Space": 32, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40,
      "KeyW": 87, "KeyA": 65, "KeyS": 83, "KeyD": 68, "KeyQ": 81, "KeyE": 69, "KeyF": 70, "ShiftLeft": 16,
      "Equal": 187, "Minus": 189, "Home": 36, "End": 35, "PageUp": 33, "PageDown": 34}
KEYNAME = {"Space": " ", "ShiftLeft": "Shift", "Equal": "=", "Minus": "-"}

HELP = r"""
window.T = {};
const L = window.squaringLab, $ = id => document.getElementById(id);
T.sel = (id, v) => { const e = $(id); if (!e) throw new Error('no control ' + id); e.value = String(v); if (e.value !== String(v)) throw new Error('no option ' + v + ' in ' + id); e.dispatchEvent(new Event('change', { bubbles: true })); };
T.type = (id, v) => { const e = $(id); if (!e) throw new Error('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
T.boxes = () => { const s = $('stage').getBoundingClientRect(); const out = { stage: [Math.round(s.width), Math.round(s.height)], stageTop: Math.round(s.top), coarse: matchMedia('(pointer: coarse)').matches };
  for (const id of ['camArc', 'camFly', 'camNear', 'camRail', 'camThumb', 'camVal', 'camFar', 'camEndA', 'camEndB', 'zoomOut', 'zoomIn', 'reset', 'triad', 'camZoom']) { const e = $(id); if (!e) { out[id] = null; continue; } const r = e.getBoundingClientRect(); out[id] = r.width ? [Math.round(r.left - s.left), Math.round(r.right - s.left), Math.round(r.top - s.top), Math.round(r.bottom - s.top)] : 'not shown'; }
  return out; };
T.cover = () => { const st = $('stage'), sr = st.getBoundingClientRect();
  const visible = e => { if (!e.getClientRects().length) return false; const s = getComputedStyle(e); if (s.visibility === 'hidden') return false; const r = e.getBoundingClientRect(); return r.width > 0.5 && r.height > 0.5; };
  const lay = [...st.querySelectorAll('*')].filter(e => visible(e) && e.tagName !== 'CANVAS' && !e.closest('svg') || (e.tagName === 'svg' && visible(e)));
  const leaf = lay.filter(e => e.tagName === 'svg' || e.matches('button, input, p, span, output, label') || e.childElementCount === 0);
  const gw = 75, gh = 75, cell = new Uint8Array(gw * gh);
  for (const e of leaf) { const r = e.getBoundingClientRect(); const x0 = Math.max(0, Math.floor((r.left - sr.left) / sr.width * gw)), x1 = Math.min(gw, Math.ceil((r.right - sr.left) / sr.width * gw)), y0 = Math.max(0, Math.floor((r.top - sr.top) / sr.height * gh)), y1 = Math.min(gh, Math.ceil((r.bottom - sr.top) / sr.height * gh)); for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) cell[y * gw + x] = 1; }
  return Math.round(cell.reduce((a, b) => a + b, 0) / (gw * gh) * 1000) / 10; };
T.extent = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight, n = 40; let x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1, hits = 0;
  for (let i = 0; i <= n; i++) for (let j = 0; j <= n; j++) { const x = (w - 1) * i / n, y = (h - 1) * j / n; if (L.pick(x, y)) { hits++; x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); } }
  return { w, h, hits, of: (n + 1) * (n + 1), x: [Math.round(x0), Math.round(x1)], y: [Math.round(y0), Math.round(y1)], dist: +L.cam.dist.toFixed(3), target: L.cam.target.map(v => +v.toFixed(3)) }; };
// hits of pick probes along the four edges of the picture, 2 px in, about every 12 px: [top, right, bottom, left, of]
T.edge = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight, m = 2, nx = Math.round(w / 12), ny = Math.round(h / 12); let t = 0, r = 0, b = 0, l = 0;
  for (let i = 0; i <= nx; i++) { const x = m + (w - 2 * m) * i / nx; if (L.pick(x, m)) t++; if (L.pick(x, h - m)) b++; }
  for (let i = 0; i <= ny; i++) { const y = m + (h - 2 * m) * i / ny; if (L.pick(m, y)) l++; if (L.pick(w - m, y)) r++; }
  return { top: t, right: r, bottom: b, left: l, perSide: [nx + 1, ny + 1] }; };
T.under = () => { const s = $('stage').getBoundingClientRect(), out = {};
  for (const id of ['camArc', 'camFly', 'camNear', 'camRail', 'camVal', 'camFar', 'zoomOut', 'zoomIn', 'reset', 'triad']) { const e = $(id); if (!e) continue; const r = e.getBoundingClientRect(); if (!r.width) continue;
    if (r.top - s.top >= s.height || r.left - s.left >= s.width) { out[id] = 'outside the picture'; continue; }
    let hit = 0, n = 0; for (let i = 0; i <= 6; i++) for (let j = 0; j <= 6; j++) { n++; if (L.pick(r.left - s.left + r.width * i / 6, r.top - s.top + r.height * j / 6)) hit++; } out[id] = hit + '/' + n; }
  return out; };
// 15 x 11 probes over the picture (the words tester's measure): [hits, hits on the outer ring, picture]
T.probes = () => { let s = '', hit = 0, ring = 0; const w = $('stage').clientWidth, h = $('stage').clientHeight; for (let j = 1; j < 12; j++) { for (let i = 1; i < 16; i++) { const p = !!L.pick(w * i / 16, h * j / 12); if (p) { hit++; if (i === 1 || i === 15 || j === 1 || j === 11) ring++; } s += p ? '#' : '.'; } s += '|'; } return { hit, ring, of: 165, map: s }; };
T.note = () => { const n = $('camNote'); return n && !n.hidden ? n.textContent : ''; };
T.cam = () => ({ yaw: +L.cam.yaw.toFixed(4), pitch: +L.cam.pitch.toFixed(4), dist: +L.cam.dist.toFixed(4), target: L.cam.target.map(v => +v.toFixed(4)), zmin: L.S.view.zmin, zmax: L.S.view.zmax, fly: L.S.view.fly, fov: +L.S.view.fov.toFixed(4), bound: L.S.view.bound });
return 'helpers ready';
"""


class Rig:
    def __init__(self, size=(1400, 950), phone=False, theme="dark", dpr=1):
        self.size, self.phone, self.theme, self.dpr = size, phone, theme, dpr

    def __enter__(self):
        chrome = next((c for c in CHROMES if os.path.exists(c)), None)
        if not chrome:
            sys.exit("No Chrome or Edge found.")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix="t9cam-")
        self.proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + self.prof,
                                      "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                                      "--window-size=%d,%d" % self.size, "--force-device-scale-factor=1", "about:blank"],
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
            sys.exit("Chrome did not start its debugging port.")
        self.p = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            self.p.call(m)
        self.metrics(self.size[0], self.size[1], self.phone, self.dpr)
        self.set_theme(self.theme)
        self.p.call("Emulation.setFocusEmulationEnabled", enabled=True)
        return self

    def __exit__(self, *a):
        try:
            self.p.js("return 0;")
            if self.p.problems:
                print("PAGE PROBLEMS (%d):" % len(self.p.problems))
                for q in self.p.problems[:40]:
                    print("  " + q[:600])
            else:
                print("no console errors")
        except Exception as e:
            print("could not read the page at the end:", e)
        try: self.p.call("Browser.close")
        except Exception: pass
        try: self.proc.wait(timeout=5)
        except Exception: self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)
        return False

    def metrics(self, w, h, phone=False, dpr=1):
        self.p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=dpr, mobile=bool(phone))
        self.p.call("Emulation.setTouchEmulationEnabled", enabled=bool(phone), maxTouchPoints=5 if phone else 1)
        self.phone = phone

    def set_theme(self, theme):
        self.p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])

    def js(self, code):
        return self.p.js(code)

    def load(self, rel="dist/v8.html", timeout=240):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, rel).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 30)
        if not self.p.wait(DONE, timeout):
            raise RuntimeError("the page never finished drawing")
        time.sleep(0.3)
        self.js(HELP)

    def done(self, timeout=240, pause=0.25):
        time.sleep(pause)
        t0 = time.time()
        if not self.p.wait(DONE, timeout):
            print("   TIMED OUT after %d s waiting for the picture" % timeout)
            return False
        return time.time() - t0

    def box(self, sel):
        return self.js("const b = document.querySelector(%s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))

    def at(self, sel, fx=0.5, fy=0.5):
        b = self.box(sel)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, fx=0.5, fy=0.5):
        x, y = self.at(sel, fx, fy)
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n)

    def click_xy(self, x, y, count=1):
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n)

    def drag(self, x0, y0, x1, y1, steps=8, button="left", buttons=1, modifiers=0):
        self.mouse("mouseMoved", x0, y0)
        self.mouse("mousePressed", x0, y0, button=button, buttons=buttons, clickCount=1, modifiers=modifiers)
        for i in range(1, steps + 1):
            self.mouse("mouseMoved", x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, button=button, buttons=buttons, modifiers=modifiers)
        self.mouse("mouseReleased", x1, y1, button=button, clickCount=1, modifiers=modifiers)

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def _key(self, kind, code, modifiers=0):
        key = KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code)
        kw = dict(type=kind, key=key, code=code, windowsVirtualKeyCode=VK[code], modifiers=modifiers)
        self.p.call("Input.dispatchKeyEvent", **kw)

    def key_down(self, code, modifiers=0):
        self._key("rawKeyDown", code, modifiers)

    def key_up(self, code, modifiers=0):
        self._key("keyUp", code, modifiers)

    def press(self, code, hold=0.0, modifiers=0):
        self.key_down(code, modifiers)
        if hold:
            time.sleep(hold)
        self.key_up(code, modifiers)

    def text(self, s):
        self.p.call("Input.insertText", text=s)

    def touch(self, kind, pts):
        self.p.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])
        if kind == "touchMove":
            time.sleep(0.03)

    def lift(self):
        time.sleep(0.25)
        self.touch("touchEnd", [])

    def tap(self, sel, fx=0.5, fy=0.5):
        self.touch("touchStart", [self.at(sel, fx, fy)]); time.sleep(0.05); self.touch("touchEnd", []); time.sleep(0.35)

    def settle(self, timeout=15):
        self.p.wait("!%s.CV.goal && !%s.CV.raf" % (L, L), timeout)
        time.sleep(0.08)

    def shot(self, name, clip="#stage"):
        path = name if os.path.isabs(name) else os.path.join(HERE, name)
        self.p.shot(path, clip)
        print("      wrote out/t9/camera/" + name)


results = []


def ok(name, cond, detail=""):
    results.append((bool(cond), name, detail))
    print(("pass  " if cond else "FAIL  ") + name + ("" if detail == "" else "  :: " + str(detail)))
    sys.stdout.flush()


def info(name, detail=""):
    print("info  " + name + ("" if detail == "" else "  :: " + (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))))
    sys.stdout.flush()


def tally():
    bad = [r for r in results if not r[0]]
    print("%d passed, %d failed" % (len(results) - len(bad), len(bad)))
