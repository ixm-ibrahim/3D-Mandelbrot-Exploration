"""Shared driver for the tester "walk": headless Chrome on the real GPU, real mouse and keyboard through the
DevTools protocol, plus the in-page helper that lists visible controls and checks the page after each action."""
import base64, io, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

VK = {"Tab": 9, "Enter": 13, "Escape": 27, "PageUp": 33, "PageDown": 34, "ArrowLeft": 37, "ArrowUp": 38,
      "ArrowRight": 39, "ArrowDown": 40, " ": 32}

HELPER = r"""
(() => {
  const $ = id => document.getElementById(id);
  const W = window.__w = {};
  window.__saved = [];
  window.squaringLabSaveHook = (name, blob) => { window.__saved.push({ name, size: blob.size, type: blob.type }); };
  W.sel = e => {
    if (e.id) return '#' + CSS.escape(e.id);
    const parts = [];
    let n = e;
    while (n && n.nodeType === 1 && !n.id && n !== document.body) {
      let i = 1, s = n;
      while ((s = s.previousElementSibling)) if (s.tagName === n.tagName) i++;
      parts.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + i + ')');
      n = n.parentElement;
    }
    return (n && n.id ? '#' + CSS.escape(n.id) : 'body') + ' > ' + parts.join(' > ');
  };
  W.vis = e => {
    if (e.disabled || e.hidden) return false;
    if (!e.getClientRects().length) return false;
    const cs = getComputedStyle(e);
    return !(cs.visibility === 'hidden' || cs.display === 'none');
  };
  W.name = e => {
    let t = e.getAttribute('aria-label') || '';
    if (!t && e.labels && e.labels.length) t = e.labels[0].textContent;
    if (!t) t = e.textContent || e.title || e.placeholder || '';
    return t.trim().replace(/\s+/g, ' ').slice(0, 60);
  };
  W.list = () => {
    const out = [];
    for (const e of document.querySelectorAll('button, input, select, summary, textarea')) {
      if (!W.vis(e)) continue;
      const tag = e.tagName.toLowerCase();
      const kind = tag === 'input' ? e.type : tag;
      const d = { sel: W.sel(e), kind, name: W.name(e) };
      if (tag === 'select') { d.opts = [...e.options].map((o, i) => o.disabled ? -1 : i).filter(i => i >= 0); d.cur = e.selectedIndex; }
      if (kind === 'range') { d.min = +e.min; d.max = +e.max; }
      if (kind === 'text' || kind === 'number' || tag === 'textarea') {
        d.value = e.value;
        const dial = e.closest('.dial');
        if (dial) { d.dial = true; const r = dial.querySelector('input[type=range]'); if (r) { d.min = +r.min; d.max = +r.max; } }
      }
      if (kind === 'checkbox' || kind === 'radio') d.on = e.checked;
      out.push(d);
    }
    for (const e of document.querySelectorAll('[role=slider]')) {
      if (e.tagName !== 'INPUT' && W.vis(e)) out.push({ sel: W.sel(e), kind: 'slider', name: W.name(e) });
    }
    return out;
  };
  W.box = sel => {
    const e = document.querySelector(sel);
    if (!e || !W.vis(e)) return null;
    e.scrollIntoView({ block: 'center', inline: 'nearest' });
    const b = e.getBoundingClientRect();
    return [b.left, b.top, b.width, b.height];
  };
  // is the element (or its label / a child) what a click at x, y would reach?
  W.hit = (sel, x, y) => {
    const e = document.querySelector(sel), t = document.elementFromPoint(x, y);
    if (!e || !t) return false;
    return e === t || e.contains(t) || t.contains(e) || (e.labels && [...e.labels].some(l => l.contains(t)));
  };
  W.check = () => {
    const L = window.squaringLab, S = L.S;
    const busy = $('busy'), bar = $('drawProgress');
    const bad = [];
    const rx = /NaN|undefined|Infinity|\[object|\bnull\b/;
    for (const e of document.querySelectorAll('input, select, output')) {
      if (e.type === 'checkbox' || e.type === 'radio') continue;
      const v = e.tagName === 'SELECT' ? (e.selectedOptions[0] ? e.selectedOptions[0].text : '(no option)') : e.value;
      if (rx.test(String(v)) && e.id !== 'juliaName' && e.id !== 'eq' && e.id !== 'z0') bad.push(W.sel(e) + ' = ' + v);
      if (e.tagName === 'SELECT' && e.selectedIndex < 0 && W.vis(e)) bad.push(W.sel(e) + ' = (no option chosen)');
      if (e.closest('.dial') && e.type === 'text' && String(v).trim() === '' && document.activeElement !== e && W.vis(e)) bad.push(W.sel(e) + ' = (empty)');
    }
    for (const host of document.querySelectorAll('aside.dials, #stage, #status, #hintBelow, .lower')) {
      const t = host.innerText || '';
      const m = t.match(/[^\n]{0,50}(NaN|undefined|Infinity|\[object)[^\n]{0,50}/);
      if (m) bad.push('text: ' + m[0]);
    }
    const err = $('eqErr'), kw = $('kleinWarn'), gf = $('glfail'), sn = $('stageNote');
    return {
      idle: L.idle(), rIdle: L.renderIdle(), cIdle: L.cardIdle(),
      busy: busy && !busy.hidden ? busy.textContent : null,
      bar: !!(bar && !bar.hidden),
      barW: bar && bar.firstChild ? bar.firstChild.style.cssText : '',
      status: $('status').textContent,
      bad,
      exp: L.exportBusy ? L.exportBusy() : null, mesh: L.meshBusy ? L.meshBusy() : null,
      playing: document.querySelectorAll('.dial.is-playing').length,
      glfail: !!(gf && !gf.hidden), eqErr: err && !err.hidden ? err.textContent : null, note: !!(sn && !sn.hidden),
      kwarn: kw && !kw.hidden ? kw.textContent.slice(0, 90) : null,
      mode: S.mode, flat: !!S.flat, saved: window.__saved.length,
      scrollX: window.scrollX, sw: document.documentElement.scrollWidth, iw: window.innerWidth,
    };
  };
  W.state = () => {
    const L = window.squaringLab;
    let s; try { s = JSON.parse(JSON.stringify(L.S)); } catch (e) { s = String(e); }
    let c; try { c = JSON.parse(JSON.stringify(L.cam)); } catch (e) { c = String(e); }
    return { S: s, cam: c };
  };
  const st = document.createElement('style');
  st.textContent = '#stage.__bare > :not(canvas) { visibility: hidden !important; }';
  document.head.appendChild(st);
})();
"""


class Lab:
    def __init__(self, url="dist/v6.html", size=(1400, 950), theme="dark", pre_script=None, mobile=False):
        if not url.startswith(("file:", "http:", "https:")):
            url = "file:///" + os.path.join(ROOT, url).replace("\\", "/")
        self.url, self.size = url, size
        chrome = next((c for c in CHROMES if os.path.exists(c)), None)
        if not chrome:
            sys.exit("No Chrome or Edge found.")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        self.port = port
        self.prof = tempfile.mkdtemp(prefix="labwalk-")
        self.proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + self.prof,
                                      "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                                      "--window-size=%d,%d" % size, "--force-device-scale-factor=1", "about:blank"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target = None
        for _ in range(150):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get("type") == "page"]
                if pages:
                    target = pages[0]; break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            sys.exit("Chrome did not start its debugging port.")
        self.target_id = target["id"]
        self.p = Page(WS(target["webSocketDebuggerUrl"]))
        p = self.p
        p.call("Runtime.enable"); p.call("Log.enable"); p.call("Page.enable")
        p.call("Emulation.setDeviceMetricsOverride", width=size[0], height=size[1], deviceScaleFactor=1, mobile=mobile)
        p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
        p.call("Emulation.setFocusEmulationEnabled", enabled=True)
        if pre_script:
            p.call("Page.addScriptToEvaluateOnNewDocument", source=pre_script)
        self.load()

    def load(self):
        p = self.p
        p.call("Page.navigate", url=self.url)
        if not p.wait("document.readyState === 'complete' && window.squaringLab", 60):
            print("WARNING: the page did not finish loading in 60 s")
        time.sleep(0.3)
        p.js(HELPER, wrap=False)

    def js(self, code):
        return self.p.js(code)

    def problems(self):
        """New console errors, warnings and exceptions since the last call."""
        self.p.js("return 0;")
        out, self.p.problems = self.p.problems, []
        return out

    def check(self):
        return self.js("return __w.check();")

    def wait_idle(self, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.js("return !!window.squaringLab.idle();"):
                return time.time() - t0
            time.sleep(0.2)
        return None

    # ----- real input
    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def box(self, sel):
        b = self.js("const b = __w.box(%s); if (b) await new Promise(r => setTimeout(r, 60)); return b && __w.box(%s);" % (json.dumps(sel), json.dumps(sel)))
        return b

    def click(self, sel, fx=0.5, fy=0.5, count=1, modifiers=0, hold=0.0):
        """Real click. Returns 'real', 'js' (the spot was covered, so the element's own click() was used) or 'gone'."""
        b = self.box(sel)
        if not b:
            return "gone"
        x, y = b[0] + b[2] * fx, b[1] + b[3] * fy
        if not self.js("return __w.hit(%s, %f, %f);" % (json.dumps(sel), x, y)):
            self.js("document.querySelector(%s).click();" % json.dumps(sel))
            return "js"
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", clickCount=count, modifiers=modifiers)
        if hold:
            time.sleep(hold)
        self.mouse("mouseReleased", x, y, button="left", clickCount=count, modifiers=modifiers)
        return "real"

    def key(self, name, modifiers=0, text=None, code=None, hold=0.0):
        kw = dict(key=name, code=code or name, windowsVirtualKeyCode=VK.get(name, ord(name.upper()) if len(name) == 1 else 0), modifiers=modifiers)
        if text:
            self.p.call("Input.dispatchKeyEvent", type="keyDown", text=text, **kw)
        else:
            self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        if hold:
            time.sleep(hold)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def retype(self, sel, s):
        r = self.click(sel, count=3)
        if r == "gone":
            return r
        self.js("const e = document.querySelector(%s); e.focus(); if (e.select) e.select();" % json.dumps(sel))
        if s == "":
            self.key("Delete") if False else self.js("const e = document.querySelector(%s); e.value = ''; e.dispatchEvent(new Event('input', { bubbles: true }));" % json.dumps(sel))
        else:
            self.p.call("Input.insertText", text=s)
        return r

    def shot_png(self, clip_sel=None, scale=1.0, bare=False):
        params = {"format": "png"}
        if bare:
            self.js("document.getElementById('stage').classList.add('__bare'); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));")
        if clip_sel:
            b = self.js("const e = document.querySelector(%s); const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height, window.innerWidth, window.innerHeight];" % json.dumps(clip_sel))
            x0, y0 = max(0, b[0]), max(0, b[1])
            x1, y1 = min(b[4], b[0] + b[2]), min(b[5], b[1] + b[3])
            if x1 - x0 < 8 or y1 - y0 < 8:
                if bare:
                    self.js("document.getElementById('stage').classList.remove('__bare');")
                return None
            params["clip"] = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0, "scale": scale}
            params["captureBeyondViewport"] = False
        data = self.p.call("Page.captureScreenshot", **params)["data"]
        if bare:
            self.js("document.getElementById('stage').classList.remove('__bare');")
        return base64.b64decode(data)

    def picture_stats(self, save=None):
        """Share of the picture's pixels that differ from its commonest colour. None when the canvas is out of view."""
        from PIL import Image
        self.js("document.getElementById('view').scrollIntoView({ block: 'center' }); await new Promise(r => setTimeout(r, 80));")
        png = self.shot_png("#view", scale=0.25, bare=True)
        if not png:
            return None
        im = Image.open(io.BytesIO(png)).convert("RGB")
        if save:
            im.save(save)
        px = list(im.getdata())
        from collections import Counter
        q = Counter((r >> 3, g >> 3, b >> 3) for r, g, b in px)
        top = q.most_common(1)[0][1]
        return {"other": 1 - top / len(px), "colours": len(q), "n": len(px)}

    def close(self):
        try:
            self.p.call("Browser.close")
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)
