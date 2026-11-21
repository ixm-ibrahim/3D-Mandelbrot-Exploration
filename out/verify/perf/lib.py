"""Shared launcher for the perf tester: headless Chrome on the real GPU, real input through CDP."""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402
L = "window.squaringLab"
PAGE = "file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/")

MON = r"""
window.__perf = (() => {
  const L = window.squaringLab, R = L.R;
  const vis = el => !!el && !el.hidden && getComputedStyle(el).display !== 'none';
  const P = { blits: [], rafJs: [], on: false };
  // count every picture put on the screen: a draw call while the default framebuffer is bound
  const gl = document.getElementById('view').getContext('webgl2');
  const od = gl.drawArrays.bind(gl);
  gl.drawArrays = (...a) => { od(...a); if (P.on && gl.getParameter(gl.FRAMEBUFFER_BINDING) === null) { const rec = [performance.now(), '', L.cam.dist, L.S.v2.h]; P.blits.push(rec); Promise.resolve().then(() => { rec[1] = R.shown; }); } };
  // time the page's own animation-frame callbacks
  const oraf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = cb => oraf(t => { if (!P.on) return cb(t); const a = performance.now(); try { cb(t); } finally { P.rafJs.push(performance.now() - a); } });
  P.oraf = oraf;
  P.frac = () => { const b = document.getElementById('drawProgress'); if (!vis(b)) return -1; const m = /scaleX\(([0-9.]+)\)/.exec(b.firstChild.style.transform || ''); return m ? +m[1] : 0; };
  // a simulated drag: every frame the camera turns a little (or the 2D picture slides) and touch() is called, for `ms`;
  // then the page is watched until the picture is final or `cap` ms have passed
  P.drag = (ms, cap, flat) => new Promise(res => {
    P.blits = []; P.rafJs = []; P.on = true;
    const t0 = performance.now(), gaps = []; let last = t0, tEnd = 0, n = 0;
    const o = { firstAcc: null, pass1: null, final: null, fracAtCap: null, barAt: null };
    const after = () => {
      const now = performance.now(), t = now - tEnd, st = document.getElementById('status').textContent, fr = P.frac();
      if (o.barAt === null && fr >= 0) o.barAt = t;
      if (o.firstAcc === null && R.shown === 'acc') o.firstAcc = t;
      if (o.pass1 === null && (st.startsWith('Refining') || st.startsWith('Done'))) o.pass1 = t;
      if (L.renderIdle()) { o.final = t; return fin(); }
      if (t > cap) { o.fracAtCap = fr; o.capAt = t; o.statusAtCap = st; return fin(); }
      oraf(after);
    };
    const fin = () => {
      const cv = document.getElementById('view'), flatNow = !!L.S.flat;
      const pv = P.blits.filter(b => b[0] <= tEnd + 1 && b[1] === 'prev').map(b => b[0]);
      const pg = pv.slice(1).map((x, i) => x - pv[i]);
      const js = P.rafJs.slice();
      P.on = false;
      res(Object.assign(o, { frames: n, rafAvg: gaps.reduce((a, b) => a + b, 0) / gaps.length, rafMax: Math.max(...gaps), pics: pv.length, picPerSec: pv.length / (ms / 1000),
        picGapAvg: pg.length ? pg.reduce((a, b) => a + b, 0) / pg.length : null, picGapMax: pg.length ? Math.max(...pg) : null,
        jsAvg: js.length ? js.reduce((a, b) => a + b, 0) / js.length : 0, jsMax: js.length ? Math.max(...js) : 0,
        ps: flatNow ? R.ps2 : R.ps, pw: R.pw, ph: R.ph, cw: cv.width, ch: cv.height, dt: R.dt, total: R.total,
        prevMs: R.rowMs * R.ph * R.pw / cv.width / (flatNow ? 1 : 3), exact: R.rowExact, status: document.getElementById('status').textContent }));
    };
    const f = () => {
      const now = performance.now(); gaps.push(now - last); last = now; n++;
      if (now - t0 < ms) { if (flat) L.S.v2.x += L.S.v2.h * 0.004 * Math.cos((now - t0) / 300); else L.cam.yaw += 0.01; L.touch(); tEnd = now; oraf(f); }
      else oraf(after);
    };
    oraf(f);
  });
  P.start = ms => {
    const m = { t0: performance.now(), maxRaf: 0, maxRafAt: 0, maxTick: 0, maxTickAt: 0, s: [], done: false, compiles0: R.compiles, labels: {} };
    let lr = m.t0, lt = m.t0;
    const bar = document.getElementById('drawProgress');
    const snap = () => { const b = document.getElementById('busy'), now = performance.now(), bv = vis(b);
      if (bv) { const tx = b.textContent; m.labels[tx] = (m.labels[tx] || 0) + 1; }
      m.s.push([Math.round(now - m.t0), bv ? 1 : 0, vis(bar) ? 1 : 0, L.idle() ? 1 : 0, L.renderIdle() ? 1 : 0]); };
    m.snap = snap;
    const f = () => { const now = performance.now(), g = now - lr; if (g > m.maxRaf) { m.maxRaf = g; m.maxRafAt = now - m.t0; } lr = now; snap();
      if (now - m.t0 < ms) oraf(f); else { m.done = true; clearInterval(iv); m.compiles1 = R.compiles; m.status = document.getElementById('status').textContent; } };
    oraf(f);
    const iv = setInterval(() => { const now = performance.now(), g = now - lt; if (g > m.maxTick) { m.maxTick = g; m.maxTickAt = now - m.t0; } lt = now; }, 10);
    window.__m = m; return m;
  };
  return P;
})();
"""


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, wait_idle=True):
        self.p.call("Page.navigate", url=PAGE)
        self.p.wait("document.readyState === 'complete'", 30)
        self.p.wait(L + " && " + L + ".R", 30)
        if wait_idle:
            if not self.p.wait(L + ".idle()", 90):
                raise RuntimeError("the page never finished drawing")
        self.js(MON)

    def box(self, sel):
        return self.js("const b = document.querySelector(%s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))

    def at(self, sel, fx=0.5, fy=0.5):
        b = self.box(sel)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, fx=0.5, fy=0.5):
        self.js("document.querySelector(%s).scrollIntoView({block: 'center'});" % json.dumps(sel))
        x, y = self.at(sel, fx, fy)
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n)

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def key(self, key, code, vk):
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key=key, code=code, windowsVirtualKeyCode=vk)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", key=key, code=code, windowsVirtualKeyCode=vk)

    def shot(self, name, clip=None):
        self.p.shot(os.path.join(HERE, name), clip)


def launch(w=1400, h=950):
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="perf-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    for m in ("Runtime.enable", "Log.enable", "Page.enable"):
        page.call(m)
    page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
    page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
    page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    return Drive(page), proc, prof


def close(d, proc, prof):
    try:
        d.p.js("return 0;")
        d.p.call("Browser.close")
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    shutil.rmtree(prof, ignore_errors=True)


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None
