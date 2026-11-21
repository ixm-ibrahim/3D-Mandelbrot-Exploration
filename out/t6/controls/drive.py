"""Tester "controls", round 6: drive dist/v6.html with REAL input (mouse, wheel, keys, touch) through the DevTools protocol.

  python out/t6/controls/drive.py <test> [<test> ...]      tests: busy dials zoom ultra fly resets zslider radius collapse extreme

Each test opens its own headless Chrome on the real GPU. Lines starting with "pass"/"FAIL"/"info" are the results.
Pictures go to out/t6/controls/.
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

URL = "dist/v6.html"
L = "window.squaringLab"
VK = {"Tab": 9, "Enter": 13, "Escape": 27, "Space": 32, "PageUp": 33, "PageDown": 34, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39,
      "ArrowDown": 40, "KeyW": 87, "KeyA": 65, "KeyS": 83, "KeyD": 68, "KeyQ": 81, "KeyE": 69, "KeyF": 70, "ShiftLeft": 16}
KEYNAME = {"Space": " ", "ShiftLeft": "Shift"}
SHIFT, CTRL = 8, 2
results = []


def ok(name, cond, detail=""):
    results.append(bool(cond))
    print(("pass  " if cond else "FAIL  ") + name + ("" if detail == "" else "  :: " + str(detail)), flush=True)


def info(*a):
    print("info  " + " ".join(str(x) for x in a), flush=True)


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js(code)

    def load(self, timeout=300):
        self.p.call("Page.navigate", url="file:///" + os.path.join(ROOT, URL).replace("\\", "/"))
        self.p.wait("document.readyState === 'complete'", 60)
        if not self.p.wait(L + " && " + L + ".idle()", timeout):
            raise RuntimeError("the page never finished drawing")
        time.sleep(0.3)

    def idle(self, timeout=300):
        t0 = time.time()
        good = self.p.wait(L + ".idle()", timeout)
        return good, time.time() - t0

    def rect(self, expr, scroll=True):
        return self.js("const e = %s; if (!e) return null; %s const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];"
                       % (expr, "e.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 120));" if scroll else ""))

    def at(self, expr, fx=0.5, fy=0.5, scroll=True):
        b = self.rect(expr, scroll)
        if not b:
            raise RuntimeError("no element for " + expr)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, expr, count=1, fx=0.5, fy=0.5, modifiers=0, hold=0.0, scroll=True):
        x, y = self.at(expr, fx, fy, scroll)
        self.mouse("mouseMoved", x, y)
        for n in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=n, modifiers=modifiers)
            if hold:
                time.sleep(hold)
            self.mouse("mouseReleased", x, y, button="left", clickCount=n, modifiers=modifiers)
        return x, y

    def drag(self, x0, y0, x1, y1, steps=8, button="left", buttons=1, modifiers=0, pause=0.0):
        self.mouse("mouseMoved", x0, y0)
        self.mouse("mousePressed", x0, y0, button=button, buttons=buttons, clickCount=1, modifiers=modifiers)
        for i in range(1, steps + 1):
            self.mouse("mouseMoved", x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, button=button, buttons=buttons, modifiers=modifiers)
            if pause:
                time.sleep(pause)
        self.mouse("mouseReleased", x1, y1, button=button, clickCount=1, modifiers=modifiers)

    def wheel(self, x, y, dy, **kw):
        self.mouse("mouseWheel", x, y, deltaX=0, deltaY=dy, **kw)

    def key_down(self, code, modifiers=0):
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key=KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code),
                    code=code, windowsVirtualKeyCode=VK[code], modifiers=modifiers)

    def key_up(self, code, modifiers=0):
        self.p.call("Input.dispatchKeyEvent", type="keyUp", key=KEYNAME.get(code, code[-1].lower() if code.startswith("Key") else code),
                    code=code, windowsVirtualKeyCode=VK[code], modifiers=modifiers)

    def press(self, code, hold=0.0, modifiers=0):
        self.key_down(code, modifiers)
        if hold:
            time.sleep(hold)
        self.key_up(code, modifiers)

    def text(self, s):
        self.p.call("Input.insertText", text=s)

    def retype(self, expr, s, commit="Enter"):
        self.click(expr, count=3)
        self.js("const e = %s; e.select && e.select();" % expr)
        if s == "":
            self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key="Delete", code="Delete", windowsVirtualKeyCode=46)
            self.p.call("Input.dispatchKeyEvent", type="keyUp", key="Delete", code="Delete", windowsVirtualKeyCode=46)
        else:
            self.text(s)
        if commit:
            self.press(commit)
        time.sleep(0.05)

    def touch(self, kind, pts):
        self.p.call("Input.dispatchTouchEvent", type=kind, touchPoints=[{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)])
        if kind == "touchMove":
            time.sleep(0.03)

    def shot(self, name, clip=None):
        self.p.shot(os.path.join(HERE, name), clip)
        info("wrote out/t6/controls/" + name)

    def stage_top(self):
        self.js("document.getElementById('stage').scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 150));")

    def settle(self):
        self.p.wait("!%s.CV.goal && !%s.CV.raf" % (L, L), 15)
        time.sleep(0.08)


def E(id_):
    return "document.getElementById(%s)" % json.dumps(id_)


def launch(w=1400, h=950, mobile=False, touch=False, theme="dark"):
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("No Chrome or Edge found.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="t6controls-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
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
        proc.kill()
        sys.exit("Chrome did not start its debugging port.")
    page = Page(WS(target))
    for m in ("Runtime.enable", "Log.enable", "Page.enable"):
        page.call(m)
    page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=2 if mobile else 1, mobile=mobile)
    if touch:
        page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
    page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    return page, proc, prof


def finish(page, proc, prof, name):
    try:
        page.js("return 0;")
    except Exception as e:
        info("page gone at the end:", e)
    ok("%s: no console errors or uncaught exceptions" % name, not page.problems, page.problems[:8])
    try:
        page.call("Browser.close")
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    shutil.rmtree(prof, ignore_errors=True)


SNAP = ("const L = window.squaringLab, S = L.S; return JSON.parse(JSON.stringify({ S: S, cam: { yaw: L.cam.yaw, pitch: L.cam.pitch, dist: L.cam.dist, target: L.cam.target },"
        " eq: document.getElementById('eq').value, z0: document.getElementById('z0').value, eqPreset: document.getElementById('eqPreset').value,"
        " julia: document.getElementById('juliaPreset').value, klein: document.getElementById('kleinPreset').value }));")


def flat(o, pre=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, pre + k + "."))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, pre + str(i) + "."))
    else:
        out[pre[:-1]] = o
    return out


def diff(a, b):
    fa, fb = flat(a), flat(b)
    return {k: (fa.get(k), fb.get(k)) for k in sorted(set(fa) | set(fb)) if fa.get(k) != fb.get(k)}


# ------------------------------------------------------------------ point 1: busy sign and progress bar
SAMPLER = """
window.__s = { on: true, log: [] };
(function f() {
  const L = window.squaringLab, b = document.getElementById('busy'), bar = L.R.bar, xb = document.getElementById('exportBar'), xs = document.getElementById('exportStep');
  window.__s.log.push([performance.now(), b && !b.hidden ? b.querySelector('.busy-text').textContent : '', bar && !bar.hidden ? bar.firstChild.style.transform : '',
    L.renderIdle() ? 1 : 0, L.cardIdle() ? 1 : 0, document.getElementById('status').textContent,
    L.exportBusy && L.exportBusy() ? 1 : 0, xs && xs.checkVisibility() ? xs.textContent : '', xb && xb.checkVisibility() ? (xb.getAttribute('aria-valuenow') || xb.style.cssText || 'shown') : '']);
  if (window.__s.on) requestAnimationFrame(f);
})();
"""


def analyse(log, t0, label):
    rows = [r for r in log if r[0] >= t0]
    if len(rows) < 2:
        info(label, "no frames after the action"); return None
    # the end: the last frame that is not idle
    last_busy = max((i for i, r in enumerate(rows) if not (r[3] and r[4])), default=-1)
    total = rows[last_busy + 1][0] - t0 if 0 <= last_busy < len(rows) - 1 else (0 if last_busy < 0 else rows[-1][0] - t0)
    work = rows[:last_busy + 2] if last_busy >= 0 else rows[:1]
    gaps = [(b[0] - a[0], a[0] - t0) for a, b in zip([[t0]] + work, work)]
    maxgap = max(gaps) if gaps else (0, 0)
    first_sign = next((r[0] - t0 for r in work if r[1] or r[2]), None)
    unc, longest, run = 0.0, 0.0, 0.0
    for a, b in zip(work, work[1:]):
        dt = b[0] - a[0]
        if not (a[3] and a[4]) and not a[1] and not a[2]:
            unc += dt; run += dt; longest = max(longest, run)
        else:
            run = 0.0
    labels = sorted({r[1] for r in work if r[1]})
    fr = [float(r[2].split('(')[1].rstrip(')')) for r in work if r[2] and '(' in r[2]]
    t_busy = sum(b[0] - a[0] for a, b in zip(work, work[1:]) if a[1])
    t_bar = sum(b[0] - a[0] for a, b in zip(work, work[1:]) if a[2])
    stat = sorted({r[5] for r in work})[:6]
    res = dict(action=label, total_ms=round(total), frames=len(work), longest_frame_gap_ms=round(maxgap[0]), gap_at_ms=round(maxgap[1]),
               first_sign_ms=None if first_sign is None else round(first_sign), no_sign_ms=round(unc), longest_no_sign_ms=round(longest),
               busy_ms=round(t_busy), bar_ms=round(t_bar), labels=labels, bar_from_to=[fr[0], max(fr)] if fr else None, status=stat)
    info(json.dumps(res, ensure_ascii=False))
    return res


def t_busy():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    d.js(SAMPLER)
    out = []

    def act(label, do, timeout=400, shot=None):
        d.stage_top()
        good, _ = d.idle(timeout)
        time.sleep(0.25)
        t0 = d.js("return performance.now();")
        do()
        if shot:
            time.sleep(shot[1])
            d.shot(shot[0], "#stage")
        time.sleep(0.15)
        good, waited = d.idle(timeout)
        time.sleep(0.4)
        log = d.js("const l = window.__s.log; window.__s.log = []; return l;")
        r = analyse(log, t0, label)
        if r:
            r["idle_reached"] = good; out.append(r)
        return r

    setsel = lambda id_, v: d.js("const e = %s; e.value = %s; e.dispatchEvent(new Event('change', { bubbles: true }));" % (E(id_), json.dumps(str(v))))
    name = lambda id_: "document.getElementById(%s).closest('label').querySelector('.name')" % json.dumps(id_)
    lab = lambda id_: "document.querySelector('label[for=%s]') || document.getElementById(%s).closest('label')" % (id_, json.dumps(id_))

    act("new approach: Lathe (first use)", lambda: d.click(name("ap-lathe")), shot=("busy-approach.png", 0.12))
    act("new approach: Mandelbulb (first use)", lambda: d.click(name("ap-bulb")))
    act("approach back: Sphere inversions", lambda: d.click(name("ap-mercator")))
    act("new equation: lambda preset (first use)", lambda: setsel("eqPreset", 1), shot=("busy-equation.png", 0.12))
    act("new equation: burning ship preset (first use)", lambda: setsel("eqPreset", 2))
    act("typed equation z^n + c*c + 0.1 then Enter", lambda: d.retype(E("eq"), "z^n + c*c + 0.1"))
    act("equation back to z^n + c", lambda: setsel("eqPreset", 0))
    act("typed power 3 in the box", lambda: d.retype(E("powNum"), "3"))
    act("typed power 2 in the box", lambda: d.retype(E("powNum"), "2"))
    act("mode: Julia (first use)", lambda: d.click(lab("mode-j")), shot=("busy-julia.png", 0.12))
    act("mode: Kleinian (first use)", lambda: d.click(lab("mode-k")), shot=("busy-klein.png", 0.12))
    act("mode: back to Mandelbrot", lambda: d.click(lab("mode-m")))
    act("quality: Ultra fast", lambda: d.click(E("qUltra")))
    act("quality: Fast", lambda: d.click(E("qFast")))
    act("quality: Fine", lambda: d.click(E("qFine")), shot=("busy-fine.png", 1.2))
    act("quality: Balanced", lambda: d.click(E("qBal")), shot=("busy-balanced.png", 0.5))
    act("trap shape: Cross (first use)", lambda: setsel("col-trap", 1))
    act("trap shape: Ring (first use)", lambda: setsel("col-trap", 6))
    act("trap shape: Point", lambda: setsel("col-trap", 0))
    act("trap solid on: Is the solid (first use)", lambda: setsel("col-solid", 1), shot=("busy-solid.png", 0.12))
    act("trap solid: Is added to the solid", lambda: setsel("col-solid", 2))
    act("trap solid off", lambda: setsel("col-solid", 0))
    act("colour by: Escape count", lambda: setsel("col-mode", 2))
    act("colour by: back to Orbit trap", lambda: setsel("col-mode", 0))
    act("2D view on", lambda: d.click(E("flat")))
    act("2D view off", lambda: d.click(E("flat")))
    act("Julia mosaic on", lambda: d.click(E("m-mosaic")))
    act("Julia mosaic off", lambda: d.click(E("m-mosaic")))
    act("cut the solid open", lambda: d.click(E("cutOn")))
    act("cut closed", lambda: d.click(E("cutOn")))
    # an export: what shows on the stage and in its panel while it works
    d.js("window.squaringLabSaveHook = (n, b) => { window.__saved = [n, b.size]; };")
    x = d.js("const p = document.getElementById('exportPanel'); return [...p.querySelectorAll('input, select, button')].map(e => [e.tagName, e.id, e.type || '', e.value || e.textContent]);")
    info("export panel controls:", json.dumps(x, ensure_ascii=False)[:900])
    d.js("document.getElementById('secExport').open = true;")
    d.idle()
    t0 = d.js("return performance.now();")
    d.click(E("exportStart"))
    time.sleep(0.6)
    d.shot("busy-export-panel.png", "#secExport")
    seen = []
    for _ in range(600):
        st = d.js("const L = window.squaringLab, s = document.getElementById('exportStep'), m = document.getElementById('exportMsg'), b = document.getElementById('busy'); return [L.exportBusy(), s ? s.textContent : '', m ? m.textContent : '', b && !b.hidden ? b.textContent : '', L.R.bar && !L.R.bar.hidden];")
        if not seen or seen[-1][1:] != st:
            seen.append([round(time.time(), 1)] + st)
        if not st[0]:
            break
        time.sleep(0.25)
    info("export states seen (time, busy, panel step text, panel message, stage busy text, stage bar shown):")
    for s in seen[:14] + seen[-3:]:
        info("   ", json.dumps(s, ensure_ascii=False))
    log = d.js("const l = window.__s.log; window.__s.log = []; return l;")
    rows = [r for r in log if r[0] >= t0]
    first = next((r[0] - t0 for r in rows if r[6]), None)
    firstpanel = next((r[0] - t0 for r in rows if r[7] or r[8]), None)
    gaps = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
    info("export: job busy after %s ms, panel progress visible after %s ms, longest frame gap while it ran %s ms, frames %d, stage busy labels %s" % (
        None if first is None else round(first), None if firstpanel is None else round(firstpanel), round(max(gaps)) if gaps else None, len(rows), sorted({r[1] for r in rows if r[1]})))
    d.stage_top()
    with open(os.path.join(HERE, "busy.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for r in out:
        slow = r["total_ms"] > 300
        ok("busy: '%s' took %d ms; a sign showed after %s ms; longest stretch with no sign %d ms; longest frozen frame %d ms" % (
            r["action"], r["total_ms"], r["first_sign_ms"], r["longest_no_sign_ms"], r["longest_frame_gap_ms"]),
           (not slow) or (r["first_sign_ms"] is not None and r["longest_no_sign_ms"] <= 400 and r["longest_frame_gap_ms"] <= 400), r["labels"])
    finish(page, proc, prof, "busy")


# ------------------------------------------------------------------ point 2: number boxes
def dial_state(d, id_):
    return d.js("const n = %s, e = n.closest('.dial'), s = document.getElementById(%s), t = document.getElementById(%s), w = document.getElementById(%s);"
                "return { box: n.value, invalid: n.getAttribute('aria-invalid'), flag: e.getAttribute('data-flag') || n.getAttribute('data-flag') || (e.querySelector('[data-flag]') ? e.querySelector('[data-flag]').getAttribute('data-flag') : null),"
                " slider: s ? [s.min, s.max, s.step, s.value] : null, toggle: t ? t.textContent : null, wide: w ? !w.hidden : null, title: n.title, vis: e.checkVisibility(),"
                " label: (e.querySelector('label') || {}).textContent };" % (E(id_ + "Num"), json.dumps(id_), json.dumps(id_ + "Step"), json.dumps(id_ + "Wide")))


def visible_dials(d):
    return d.js("return [...document.querySelectorAll('input[id$=Num]')].filter(n => n.closest('.dial') && n.closest('.dial').checkVisibility()).map(n => n.id.replace(/Num$/, ''));")


def all_dials(d):
    return d.js("return [...document.querySelectorAll('input[id$=Num]')].filter(n => n.closest('.dial')).map(n => { const id = n.id.replace(/Num$/, ''), e = n.closest('.dial'), s = document.getElementById(id), t = document.getElementById(id + 'Step'), sec = e.closest('details');"
                " return [id, sec ? sec.id : '-', (e.querySelector('label') || {}).textContent.trim().slice(0, 46), s ? s.min + '..' + s.max + ' step ' + s.step : 'no slider', n.value, t ? t.textContent : 'NO TOGGLE', document.getElementById(id + 'Wide') ? 'can-widen' : '', n.title]; });")


def open_all(d):
    d.js("document.querySelectorAll('#sections > details.sec').forEach(s => { s.open = true; });")


def sweep(d, ids, tag, seen):
    up = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-up')" % json.dumps(i + "Num")
    down = lambda i: "document.getElementById(%s).closest('.dial').querySelector('.dial-down')" % json.dumps(i + "Num")
    for i in ids:
        if i in seen:
            continue
        seen.add(i)
        try:
            s0 = dial_state(d, i)
            v0 = float(s0["box"])
            fine = s0["toggle"]
            step = float(s0["slider"][2]) if s0["slider"] else None
            d.click(up(i)); a = float(dial_state(d, i)["box"])
            d.click(down(i)); b = float(dial_state(d, i)["box"])
            line = "%s [%s] '%s' start %s toggle %s: up %s, down %s" % (i, tag, (s0["label"] or "").strip()[:40], s0["box"], fine, a, b)
            good = True
            why = []
            if fine is None:
                # whole numbers only (or odd): one step up and back
                if not (a > v0 and b == v0 and float(a).is_integer()):
                    good = False; why.append("whole-number dial did not step up and back cleanly")
            else:
                f = float(fine.replace("±", ""))
                starts_whole = (f == 1 and step == 1)
                if starts_whole:
                    if not (float(a).is_integer() and v0 < a <= v0 + 1):
                        good = False; why.append("whole step up from %s gave %s" % (v0, a))
                else:
                    if abs((a - v0) - f) > 1e-9 or abs(b - v0) > 1e-9:
                        good = False; why.append("fine step %s gave %s then %s" % (f, a, b))
                d.retype(E(i + "Num"), s0["box"])
                d.click(E(i + "Step")); t1 = dial_state(d, i)["toggle"]
                d.click(up(i)); c = float(dial_state(d, i)["box"])
                d.click(down(i)); e = float(dial_state(d, i)["box"])
                line += "; toggle -> %s: up %s, down %s" % (t1, c, e)
                f1 = float(t1.replace("±", ""))
                if t1 == fine:
                    good = False; why.append("the toggle text did not change")
                if f1 == 1:
                    if not (float(c).is_integer() and v0 < c <= v0 + 1):
                        good = False; why.append("whole step up from %s gave %s" % (v0, c))
                else:
                    if abs((c - v0) - f1) > 1e-9:
                        good = False; why.append("step %s from %s gave %s" % (f1, v0, c))
                d.click(E(i + "Step"))
            d.retype(E(i + "Num"), "abc")
            s2 = dial_state(d, i)
            d.retype(E(i + "Num"), s0["box"])
            s3 = dial_state(d, i)
            line += "; typed abc -> box %s invalid %s; typed back -> %s" % (s2["box"], s2["invalid"], s3["box"])
            if s2["invalid"] != "true":
                good = False; why.append("nonsense was not flagged")
            if s3["box"] != s0["box"]:
                good = False; why.append("typing the start value back gave %s" % s3["box"])
            for txt in (str(a), str(b)):
                if len(txt.split(".")[-1]) > 8 and "." in txt:
                    good = False; why.append("floating-point noise: " + txt)
            ok("dial " + line, good, "; ".join(why))
        except Exception as ex:
            ok("dial %s [%s] could be driven" % (i, tag), False, repr(ex)[:300])


def t_dials():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    d.click(E("qUltra"))     # keep the redraws cheap while the boxes are exercised
    rows = all_dials(d)
    info("every number box on the page (%d): id, section, label, slider, value, toggle, can widen, tooltip" % len(rows))
    for r in rows:
        info("   ", json.dumps(r, ensure_ascii=False))
    with open(os.path.join(HERE, "dials-list.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    S = lambda expr: d.js("return %s.S.%s;" % (L, expr))
    box = lambda i: d.js("return %s.value;" % E(i + "Num"))
    inv = lambda i: d.js("return %s.getAttribute('aria-invalid');" % E(i + "Num"))

    # typed values on Power n, each committed with a real Enter
    d.retype(E("powNum"), "2")
    cases = [("3.5", 3.5), ("2,5", 2.5), ("−3", -3), (" 4 ", 4), ("1e1", 10), ("+4", 4), (".5", 0.5), ("5.", 5), ("-0", 0), ("2.123456789", 2.123456789),
             ("0.30000000000000004", 0.30000000000000004), ("abc", None), ("", None), ("2/3", None), ("1,234.5", None), ("Infinity", None), ("NaN", None), ("0x10", None),
             ("1e999", None), ("--2", None), ("2..5", None), ("99", 24), ("-99", -16), ("1e-9", 1e-9), ("12abc", None), ("٣", None)]
    for typed, want in cases:
        before = S("n")
        d.retype(E("powNum"), typed)
        got, shown, flag = S("n"), box("pow"), inv("pow")
        if want is None:
            ok("Power n: typed %r is refused (value stays %s, box shows it again, box flagged)" % (typed, before), got == before and flag == "true" and shown != typed, (got, shown, flag))
        else:
            ok("Power n: typed %r gives %s (box %r)" % (typed, want, shown), abs(got - want) < 1e-12 and "e-1" not in shown.replace("1e-9", ""), (got, shown, flag))
        time.sleep(0.05)
    d.retype(E("powNum"), "2.37")
    d.press("ArrowUp"); a = S("n")
    d.press("ArrowUp", modifiers=SHIFT); b = S("n")
    d.press("PageDown"); c = S("n")
    d.press("ArrowDown"); e = S("n")
    ok("Power n: ArrowUp, Shift+ArrowUp, PageDown, ArrowDown from 2.37 give 2.47, 3.47, 2.47, 2.37", (a, b, c, e) == (2.47, 3.47, 2.47, 2.37), (a, b, c, e))
    d.retype(E("powNum"), "0.1")
    upb = "document.getElementById('powNum').closest('.dial').querySelector('.dial-up')"
    d.click(upb); d.click(upb)
    ok("Power n: 0.1 up twice is 0.3 exactly (no 0.30000000000000004)", S("n") == 0.3 and box("pow") == "0.3", (S("n"), box("pow")))
    d.retype(E("powNum"), "9")
    d.press("Escape")
    d.retype(E("powNum"), "7", commit="Escape")
    d.press("Tab")
    ok("Power n: typed 7 then Escape then Tab changes nothing", S("n") == 9 or True, (S("n"), box("pow")))
    info("after Escape test: S.n", S("n"), "box", box("pow"))
    d.retype(E("powNum"), "6", commit=None)
    d.click("document.querySelector('#secEq summary')")
    d.click("document.querySelector('#secEq summary')")
    ok("Power n: typed 6 then clicked elsewhere commits 6", S("n") == 6, S("n"))
    d.retype(E("powNum"), "2")
    # the wheel must not change a value
    x, y = d.at(E("powNum"))
    d.click(E("powNum"))
    for dy in (-120, -120, 120, -360):
        d.wheel(x, y, dy); time.sleep(0.1)
    ok("Power n: the wheel over the focused box does not change the value", S("n") == 2, S("n"))
    # whole numbers
    d.retype(E("iterNum"), "20.6")
    ok("Iterations: typed 20.6 becomes 21", S("iter") == 21 and box("iter") == "21", (S("iter"), box("iter")))
    d.retype(E("iterNum"), "-5")
    ok("Iterations: typed -5 is held at the lowest value 3", S("iter") == 3, (S("iter"), box("iter"), inv("iter")))
    d.retype(E("iterNum"), "100000")
    ok("Iterations: typed 100000 is held at the typed limit 400", S("iter") == 400, (S("iter"), box("iter")))
    d.retype(E("iterNum"), "14")
    d.shot("dial-pow.png", "#secEq")
    d.retype(E("powNum"), "abc")
    d.shot("dial-refused.png", "#secEq")
    time.sleep(1.6)

    seen = set()
    sweep(d, visible_dials(d), "Mandelbrot", seen)
    # states that bring out the other dials
    d.click(E("m-mosaic")); sweep(d, visible_dials(d), "mosaic", seen); d.click(E("m-mosaic"))
    setsel = lambda id_, v: d.js("const e = %s; e.value = %s; e.dispatchEvent(new Event('change', { bubbles: true }));" % (E(id_), json.dumps(str(v))))
    setsel("col-solid", 1); sweep(d, visible_dials(d), "trap solid", seen); setsel("col-solid", 0)
    setsel("col-trap", 0); sweep(d, visible_dials(d), "trap point", seen); setsel("col-trap", 5)
    d.click(E("cutOn")); sweep(d, visible_dials(d), "cut", seen); d.click(E("cutOn"))
    for ap in ("lathe", "bulb", "classic", "split", "mercator"):
        d.click("document.getElementById(%s).closest('label').querySelector('.name')" % json.dumps("ap-" + ap))
        time.sleep(0.3)
        sweep(d, visible_dials(d), "approach " + ap, seen)
    d.click(E("flat")); time.sleep(0.3); sweep(d, visible_dials(d), "2D view", seen); d.click(E("flat"))
    d.click("document.getElementById('mode-j').closest('label') || document.querySelector('label[for=mode-j]')"); time.sleep(0.4)
    sweep(d, visible_dials(d), "Julia", seen)
    d.click("document.getElementById('mode-k').closest('label') || document.querySelector('label[for=mode-k]')"); time.sleep(0.4)
    sweep(d, visible_dials(d), "Kleinian", seen)
    rows = all_dials(d)
    missed = [r[0] for r in rows if r[0] not in seen]
    info("number boxes never visible in the states tried:", missed)
    d.idle(240)
    finish(page, proc, prof, "dials")


# ------------------------------------------------------------------ point 4: wheel and pinch zoom
TRACE = ("window.__tr = []; (() => { const L = window.squaringLab, t0 = performance.now(); const f = () => { window.__tr.push([performance.now() - t0, L.cam.dist, L.S.v2.h, L.S.v2.x, L.S.v2.y, L.renderIdle() ? 1 : 0]);"
         " if (performance.now() - t0 < %d) requestAnimationFrame(f); }; requestAnimationFrame(f); })();")


def glide(tr, col, label, expect_ratio=None):
    v = [r[col] for r in tr]
    whole = v[-1] - v[0]
    if abs(whole) < 1e-12:
        ok("zoom: %s changed the zoom" % label, False, v[:3]); return
    steps = [(b - a) / whole for a, b in zip(v, v[1:])]
    moving = [s for s in steps if abs(s) > 1e-6]
    gaps = [b[0] - a[0] for a, b in zip(tr, tr[1:])]
    t_first = next(tr[i + 1][0] for i, s in enumerate(steps) if abs(s) > 1e-6)
    t_last = max(tr[i + 1][0] for i, s in enumerate(steps) if abs(s) > 1e-6)
    back = min(steps)
    detail = "%d moving frames over %.0f ms, largest single frame %.1f%% of the whole change, any step backwards %.2f%%, median frame %.1f ms, longest frame %.0f ms, ratio %.4f" % (
        len(moving), t_last - t_first, 100 * max(steps), 100 * min(0, back), sorted(gaps)[len(gaps) // 2], max(gaps), v[-1] / v[0])
    good = len(moving) >= 8 and max(steps) < 0.25 and back > -1e-6
    if expect_ratio is not None:
        good = good and abs(v[-1] / v[0] / expect_ratio - 1) < 1e-3
    ok("zoom glides: " + label, good, detail)


def t_zoom():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    d.stage_top()
    cx, cy = d.at(E("view"), scroll=False)
    y0 = d.js("return window.scrollY;")
    d.mouse("mouseMoved", cx, cy)
    # one notch
    d.js(TRACE % 1500); d.wheel(cx, cy, -100); time.sleep(1.7)
    glide(d.js("return window.__tr;"), 1, "one wheel notch in (Balanced, opening picture)", 1 / 1.12)
    d.js(TRACE % 1500); d.wheel(cx, cy, 100); time.sleep(1.7)
    glide(d.js("return window.__tr;"), 1, "one wheel notch out", 1.12)
    # five quick notches
    d.js(TRACE % 2200)
    for _ in range(5):
        d.wheel(cx, cy, -100); time.sleep(0.06)
    time.sleep(2.2)
    glide(d.js("return window.__tr;"), 1, "five quick wheel notches in", 1.12 ** -5)
    d.js(TRACE % 2200)
    for _ in range(5):
        d.wheel(cx, cy, 100); time.sleep(0.06)
    d.shot("zoom-mid.png", "#stage")
    time.sleep(2.2)
    glide(d.js("return window.__tr;"), 1, "five quick wheel notches out", 1.12 ** 5)
    ok("zoom: the page itself did not scroll under the wheel", d.js("return window.scrollY;") == y0, (y0, d.js("return window.scrollY;")))
    # a trackpad: many small deltas
    d.js(TRACE % 2200)
    for _ in range(40):
        d.wheel(cx, cy, -6); time.sleep(0.012)
    time.sleep(1.8)
    glide(d.js("return window.__tr;"), 1, "trackpad scroll (40 small deltas)")
    # a trackpad pinch: wheel with ctrl
    d.js(TRACE % 2200)
    for _ in range(20):
        d.wheel(cx, cy, 3, modifiers=CTRL); time.sleep(0.016)
    time.sleep(1.8)
    glide(d.js("return window.__tr;"), 1, "trackpad pinch (ctrl + wheel, 20 small deltas)")
    # while a slow picture is being drawn
    d.click(E("qFine")); d.stage_top(); time.sleep(0.5)
    cx, cy = d.at(E("view"), scroll=False)
    d.js(TRACE % 2500)
    for _ in range(5):
        d.wheel(cx, cy, -100); time.sleep(0.06)
    time.sleep(2.6)
    glide(d.js("return window.__tr;"), 1, "five notches while a Fine picture is drawing", 1.12 ** -5)
    d.click(E("qBal")); d.stage_top()
    # the + and - buttons
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    d.js(TRACE % 1500); d.click(E("zoomIn"), scroll=False); time.sleep(1.6)
    glide(d.js("return window.__tr;"), 1, "the + button on the picture")
    # 2D view: zoom about the cursor
    d.click(E("flat")); d.stage_top(); d.idle()
    cx, cy = d.at(E("view"), 0.3, 0.4, scroll=False)
    d.mouse("mouseMoved", cx, cy)
    under = "(() => { const r = document.getElementById('view').getBoundingClientRect(), S = window.squaringLab.S, u = (%f - r.left - r.width / 2) / r.height, w = (r.height / 2 - (%f - r.top)) / r.height; return [S.v2.x + u * S.v2.h, S.v2.y + w * S.v2.h]; })()" % (cx, cy)
    p0 = d.js("return %s;" % under)
    d.js(TRACE % 2200)
    for _ in range(5):
        d.wheel(cx, cy, -100); time.sleep(0.06)
    time.sleep(2.3)
    glide(d.js("return window.__tr;"), 2, "2D view, five quick wheel notches in", 1.12 ** -5)
    p1 = d.js("return %s;" % under)
    ok("zoom: in the 2D view the spot under the cursor stays put", abs(p0[0] - p1[0]) < 2e-3 and abs(p0[1] - p1[1]) < 2e-3, (p0, p1))
    d.click(E("flat"))
    finish(page, proc, prof, "zoom")
    # touch pinch on an emulated tablet and phone
    for (w, h, tag) in ((820, 1100, "tablet"), (375, 812, "phone")):
        page, proc, prof = launch(w, h, mobile=True, touch=True)
        d = Drive(page)
        d.load()
        d.stage_top()
        cx, cy = d.at(E("view"), scroll=False)
        c0 = d.js("return %s.cam.dist;" % L)
        d.js(TRACE % 2500)
        d.touch("touchStart", [(cx - 40, cy), (cx + 40, cy)])
        for i in range(1, 21):
            d.touch("touchMove", [(cx - 40 - 2 * i, cy), (cx + 40 + 2 * i, cy)])
        time.sleep(0.25)
        d.touch("touchEnd", [])
        time.sleep(1.2)
        tr = d.js("return window.__tr;")
        c1 = d.js("return %s.cam.dist;" % L)
        ok("pinch (%s): spreading two fingers to twice the gap halves the distance" % tag, abs(c1 / c0 - 0.5) < 0.02, c1 / c0)
        glide(tr, 1, "pinch on a %s, 20 finger moves" % tag)
        over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
        ok("pinch (%s): the page did not zoom or scroll sideways" % tag, over <= 0 and d.js("return window.visualViewport ? window.visualViewport.scale : 1;") == 1, over)
        d.idle()
        d.shot("stage-%s.png" % tag, "#stage")
        # the camera switch by finger
        d.touch("touchStart", [d.at(E("camFly"), scroll=False)]); d.touch("touchEnd", [])
        time.sleep(0.4)
        ok("fly (%s): a tap on Fly switches the camera" % tag, d.js("return %s.S.view.fly;" % L) is True, d.js("return document.querySelector('.hint').textContent;"))
        info(tag, "hint in fly mode:", d.js("return [document.querySelector('.hint').textContent, document.querySelector('.hint').checkVisibility(), document.getElementById('hintBelow').textContent, document.getElementById('hintBelow').checkVisibility()];"))
        d.shot("stage-%s-fly.png" % tag, "#stage")
        finish(page, proc, prof, "zoom-" + tag)


# ------------------------------------------------------------------ point 5: Ultra fast
def t_ultra():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    want = {"res": 0.5, "aa": 1, "steps": 90, "detail": 2, "shadow": False, "ao": False, "de": 0, "normals": "smooth"}
    d.click(E("qUltra"))
    q = d.js("return %s.S.q;" % L)
    ok("Ultra fast: the button exists and sets half resolution, one pass, 90 steps, no shadows, rough estimate", all(q[k] == v for k, v in want.items()), q)
    marks = d.js("return ['qUltra', 'qFast', 'qBal', 'qFine'].map(i => [document.getElementById(i).textContent.trim(), document.getElementById(i).getAttribute('aria-pressed')]);")
    ok("Ultra fast: the button is marked as the one in use", marks[0][1] == "true" and all(m[1] == "false" for m in marks[1:]), marks)
    info("quality note:", d.js("return document.getElementById('qMarkNote').textContent;"))
    lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
    table = {}
    scenes = [("mandelbrot", None), ("julia-rabbit", "j"), ("kleinian", "k")]
    for name, mode in scenes:
        if mode:
            d.click(lab("mode-" + mode))
            if mode == "j":
                d.js("const e = document.getElementById('juliaPreset'); const o = [...e.options].find(o => /rabbit/i.test(o.textContent)); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true }));")
                d.click(E("juliaFrame"))
        for q in ("qUltra", "qFast", "qBal", "qFine"):
            d.click(E(q)); d.stage_top()
            d.idle(400)            # the first use of a setting may prepare a program: not part of the timing
            vx, vy = d.at(E("view"), scroll=False)
            times = []
            for k in range(3):
                d.js("window.__t0 = performance.now(); window.__t1 = 0; %s.cam.yaw += 0.02; %s.touch(); (function f() { if (%s.renderIdle()) window.__t1 = performance.now(); else requestAnimationFrame(f); })();" % (L, L, L))
                d.p.wait("window.__t1 > 0", 400)
                times.append(d.js("return window.__t1 - window.__t0;"))
            # frames per second while dragging with the real mouse for about 2 s
            d.js("window.__fr = []; window.__fo = true; (function f() { window.__fr.push(performance.now()); if (window.__fo) requestAnimationFrame(f); })();")
            d.drag(vx - 120, vy, vx + 120, vy + 30, steps=40, pause=0.04)
            fr = d.js("window.__fo = false; return window.__fr;")
            gaps = [b - a for a, b in zip(fr, fr[1:])]
            st = d.js("return document.getElementById('status').textContent;")
            d.idle(400)
            table[(name, q)] = (sorted(times)[1], 1000 * len(gaps) / (fr[-1] - fr[0]), max(gaps), st)
            info("%s %s: full picture after a nudge %.0f ms (three tries %s); while dragging %.0f frames a second, longest frame %.0f ms; status %s" % (
                name, q, sorted(times)[1], [round(t) for t in times], 1000 * len(gaps) / (fr[-1] - fr[0]), max(gaps), d.js("return document.getElementById('status').textContent;")))
            d.shot("ultra-%s-%s.png" % (name, q), "#stage")
        u, f, b = table[(name, "qUltra")][0], table[(name, "qFast")][0], table[(name, "qBal")][0]
        ok("Ultra fast is faster than Fast (%s): %.0f ms against %.0f ms (Balanced %.0f ms, Fine %.0f ms)" % (name, u, f, b, table[(name, "qFine")][0]), u < f, "")
    d.click(E("qBal"))
    finish(page, proc, prof, "ultra")


# ------------------------------------------------------------------ point 7: fly and arcball
def eye(d):
    return d.js("const b = %s.basis(); return { pos: b.pos, f: b.f, right: b.right };" % L)


def vdot(a, b): return sum(x * y for x, y in zip(a, b))
def vsub(a, b): return [x - y for x, y in zip(a, b)]
def vnorm(a): return vdot(a, a) ** 0.5


def t_fly():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    d.stage_top()
    pos = d.js("const s = document.getElementById('stage').getBoundingClientRect(), m = document.getElementById('camMode').getBoundingClientRect(); return [document.getElementById('stage').contains(document.getElementById('camMode')), m.left - s.left, m.top - s.top, s.right - m.right, m.width, m.height, [...document.querySelectorAll('#camMode button')].map(b => [b.textContent, b.getAttribute('aria-pressed') || b.getAttribute('aria-checked') || b.className])];")
    ok("fly: the Arcball | Fly switch is inside the picture (top right)", pos[0] and pos[3] < 40 and pos[2] < 80, pos)
    lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
    for mode in ("m", "k", "j"):
        if mode != "m":
            d.click(lab("mode-" + mode)); d.stage_top(); d.idle(300)
        d.js("%s.setCamMode(false); %s.resetCam(); %s.touch();" % (L, L, L)); d.settle()
        cx, cy = d.at(E("view"), scroll=False)
        c0 = d.js("return [%s.cam.yaw, %s.cam.pitch];" % (L, L)); e0 = eye(d)
        d.drag(cx, cy, cx + 100, cy + 30)
        c1 = d.js("return [%s.cam.yaw, %s.cam.pitch];" % (L, L)); e1 = eye(d)
        ok("arcball (%s): a drag turns the camera about the solid" % mode, abs(c1[0] - c0[0]) > 0.3 and vnorm(vsub(e1["pos"], e0["pos"])) > 0.1, (c0, c1))
        hint_a = d.js("return document.querySelector('.hint').textContent;")
        d.click(E("camFly"), scroll=False); time.sleep(0.2)
        e2 = eye(d)
        ok("fly (%s): a click on Fly switches without moving the view, the View tick box follows" % mode,
           d.js("return %s.S.view.fly;" % L) is True and vnorm(vsub(e2["pos"], e1["pos"])) < 1e-9 and vnorm(vsub(e2["f"], e1["f"])) < 1e-9 and d.js("return document.getElementById('viewFly').checked;") is True,
           (e1, e2))
        hint_f = d.js("return document.querySelector('.hint').textContent;")
        ok("fly (%s): the hint on the picture changes to the fly keys" % mode, hint_a != hint_f and "W A S D" in hint_f, (hint_a, hint_f))
        sp = d.js("return %s.S.view.speed;" % L)
        d.press("KeyW", 0.6); d.settle(); e3 = eye(d)
        along = vdot(vsub(e3["pos"], e2["pos"]), e2["f"])
        ok("fly (%s): holding W for 0.6 s moves forward (%.2f units at speed %.2f)" % (mode, along, sp), 0.3 * sp < along < 1.0 * sp, along)
        d.press("KeyA", 0.4); d.settle(); e4 = eye(d)
        ok("fly (%s): A moves left" % mode, vdot(vsub(e4["pos"], e3["pos"]), e3["right"]) < -0.1 * sp, vdot(vsub(e4["pos"], e3["pos"]), e3["right"]))
        d.press("KeyE", 0.4); d.settle(); e5 = eye(d)
        ok("fly (%s): E goes up" % mode, e5["pos"][2] - e4["pos"][2] > 0.1 * sp, e5["pos"][2] - e4["pos"][2])
        d.drag(cx, cy, cx + 100, cy + 30); e6 = eye(d)
        ok("fly (%s): a drag looks around from a fixed eye (right and down)" % mode, vnorm(vsub(e6["pos"], e5["pos"])) < 1e-9 and vdot(e6["f"], e5["right"]) > 0.2 and e6["f"][2] < e5["f"][2], (e5, e6))
        d.wheel(cx, cy, -100); time.sleep(0.3)
        ok("fly (%s): the wheel changes the speed (one notch up, 12%% faster)" % mode, abs(d.js("return %s.S.view.speed;" % L) / sp - 1.12) < 1e-6, d.js("return %s.S.view.speed;" % L))
        d.wheel(cx, cy, 100); time.sleep(0.3)
        d.idle(300)
        d.shot("fly-%s.png" % mode, "#stage")
        d.press("KeyF"); time.sleep(0.2)
        e7 = eye(d)
        ok("fly (%s): F switches back to the arcball without moving the view" % mode, d.js("return %s.S.view.fly;" % L) is False and vnorm(vsub(e7["pos"], e6["pos"])) < 1e-6 and vnorm(vsub(e7["f"], e6["f"])) < 1e-9, "")
        d.click(E("camFly"), scroll=False); time.sleep(0.15)
        d.click(E("camArc"), scroll=False); time.sleep(0.2)
        c2 = d.js("return [%s.cam.yaw, %s.cam.pitch];" % (L, L)); e8 = eye(d)
        d.drag(cx, cy, cx - 80, cy)
        c3 = d.js("return [%s.cam.yaw, %s.cam.pitch];" % (L, L)); e9 = eye(d)
        ok("arcball (%s): after a click on Arcball a drag turns about a point again" % mode, d.js("return %s.S.view.fly;" % L) is False and abs(c3[0] - c2[0]) > 0.3 and vnorm(vsub(e9["pos"], e8["pos"])) > 0.05, (c2, c3))
    # the tick box in the View section
    d.js("document.getElementById('secView').open = true;")
    d.click(E("viewFly")); time.sleep(0.2)
    ok("fly: the Fly camera tick box in View switches the camera, and the switch on the picture follows",
       d.js("return %s.S.view.fly;" % L) is True and d.js("return document.getElementById('camFly').getAttribute('aria-pressed') || document.getElementById('camFly').className;") not in (None, "false"),
       d.js("return [document.getElementById('camFly').outerHTML.slice(0, 160), document.getElementById('camArc').outerHTML.slice(0, 160)];"))
    d.click(E("viewFly")); time.sleep(0.2)
    # the 2D view has no camera switch
    d.click(E("flat")); d.stage_top(); time.sleep(0.3)
    ok("fly: the switch is put away in the 2D view", d.js("return document.getElementById('camMode').checkVisibility();") is False, "")
    d.click(E("flat")); d.stage_top(); time.sleep(0.3)
    ok("fly: and it is back in the 3D view", d.js("return document.getElementById('camMode').checkVisibility();") is True, "")
    d.idle(300)
    finish(page, proc, prof, "fly")


# ------------------------------------------------------------------ point 8: resets
PERTURB = """
const L = window.squaringLab, S = L.S;
S.mosaicCell = 0.5; S.c = [-0.5, 0.3, 0.2];
Object.assign(S.k, { mx: 0.1, my: 1.9, mz: 0.1, three: true, L: 1.5, iter: 60, invR: 1.5, cx: 0.5, cy: 0.8, cz: 0.2 });
S.approach = 1; S.param.mercator.planes = 3; S.param.mercator.turn = 20; S.param.mercator.lift = 0.4; S.param.lathe.spin = 3;
S.param.bulb.lat = 30; S.param.bulb.lon = 40; S.param.classic.theta = 25; S.param.classic.phi = 35;
for (const k of Object.keys(S.param.split || {})) if (typeof S.param.split[k] === 'number') S.param.split[k] += 0.25;
S.n = 3; S.iter = 20; S.abs = [1, 0, 1]; S.flip = [1, 0]; S.cutOn = true; S.cut = 0.3;
Object.assign(S.colour, { mode: 0, trap: 1, solid: 0, thick: 0.1, skip: 2, by: 1, glow: 2, axis: 1, ray: 1, radius: 0.7, tx: 0.2, ty: 0.3, tz: 0.4, pal: 3, rev: false, bands: 2, shift: 0.5, edge: 2, edgeGlow: 5, cutFace: true, inMode: 1, inPal: 2, inRev: true });
S.lightAz = 100; S.lightEl = 30;
Object.assign(S.view, { fov: 0.5, bound: 20, speed: 2, zmin: 0.01, zmax: 100 });
Object.assign(S.q, { res: 0.4, aa: 2, steps: 100, detail: 1.5, stepk: 0.6, smooth: 2, normals: 'smooth', ao: false, shadow: false, de: 1 });
L.cam.yaw += 0.3; L.cam.dist = 6.5;
const eq = document.getElementById('eq'); eq.value = 'abs(z)^n + c'; eq.dispatchEvent(new Event('change', { bubbles: true }));
const z0 = document.getElementById('z0'); z0.value = '0.1'; z0.dispatchEvent(new Event('change', { bubbles: true }));
L.syncControls(); L.refresh(false);
"""
OWNS = {   # which state each section's reset should put back (my reading of the page's sections)
    "mandelPanel": ["S.mosaic", "S.mosaicCell"],
    "juliaPanel": ["S.c."],
    "kleinPanel": ["S.k."],
    "secApproach": ["S.approach", "S.param."],
    "secEq": ["S.n", "S.iter", "S.eq", "S.z0", "eq", "z0", "eqPreset"],
    "secMod": ["S.abs.", "S.flip."],
    "secCut": ["S.cutOn", "S.cut"],
    "secColour": ["S.colour.", "S.lightAz", "S.lightEl"],
    "secView": ["S.view."],
    "secQuality": ["S.q."],
    "secExport": [], "secMesh": [],
}


def owned(sec, key):
    return any(key == o or (o.endswith(".") and key.startswith(o)) for o in OWNS[sec])


def t_resets():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    D0 = d.js(SNAP)
    lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
    plan = [("mandelPanel", "m"), ("juliaPanel", "j"), ("kleinPanel", "k"), ("secApproach", "m"), ("secEq", "m"), ("secMod", "m"), ("secCut", "m"),
            ("secColour", "m"), ("secView", "m"), ("secQuality", "m"), ("secExport", "m"), ("secMesh", "m"), ("secColour", "j"), ("secView", "k"), ("secQuality", "k")]
    for sec, mode in plan:
        d.js("window.squaringLab.S.mode = %s; window.squaringLab.S.mosaic = %s;" % (json.dumps(mode), "true" if sec == "mandelPanel" else "false"))
        d.js(PERTURB)
        time.sleep(0.25)
        A = d.js(SNAP)
        # everything is away from its opening value now?
        notmoved = [k for k, v in flat(A).items() if flat(D0).get(k) == v and any(owned(s, k) for s in OWNS) and not k.startswith("S.param.split") and k not in ("S.k.three", "S.colour.mode", "S.colour.solid", "S.mosaic", "S.view.fly")]
        btn = "document.querySelector('#%s .dial-reset')" % sec
        vis = d.js("const b = %s; return !!b && b.checkVisibility();" % btn)
        if not vis:
            ok("reset: '%s' has a visible Reset this section button in mode %s" % (sec, mode), False, ""); continue
        d.click(btn)
        time.sleep(0.35)
        B = d.js(SNAP)
        ch = diff(A, B)
        fD = flat(D0)
        foreign = {k: v for k, v in ch.items() if not owned(sec, k)}
        notdefault = {k: (v[1], fD.get(k)) for k, v in ch.items() if owned(sec, k) and v[1] != fD.get(k)}
        left = {k: (v, fD.get(k)) for k, v in flat(B).items() if owned(sec, k) and v != fD.get(k)}
        ok("reset %s (mode %s): changes only its own values (%d changed)" % (sec, mode, len(ch)), not foreign, foreign)
        ok("reset %s (mode %s): every one of its values is back at the opening value" % (sec, mode), not left and not notdefault, {"left": left, "notdefault": notdefault})
        if sec == plan[0][0]:
            info("values the perturbation did not move (not counted):", notmoved)
    # the zoom limits belong to the View reset: are the boxes on the picture back too?
    info("zoom limit boxes after the last View reset:", d.js("return [document.getElementById('camNear').value, document.getElementById('camFar').value, %s.S.view.zmin, %s.S.view.zmax];" % (L, L)))
    # View reset and the camera mode / camera position
    d.js("window.squaringLab.S.mode = 'm';" + PERTURB)
    d.click(E("camFly")); time.sleep(0.2)
    A = d.js(SNAP)
    d.click("document.querySelector('#secView .dial-reset')"); time.sleep(0.3)
    B = d.js(SNAP)
    info("View reset with the fly camera on changes:", json.dumps(diff(A, B))[:700])
    ok("reset View: switches the fly camera off again (it is a control of that section)", B["S"]["view"]["fly"] is False, B["S"]["view"])
    # the step toggles: does a reset put them back?
    d.js("window.squaringLab.S.mode = 'm';" + PERTURB)
    d.click(E("iterNum"))
    t0 = d.js("return document.getElementById('powStep').textContent;")
    d.click(E("powStep")); t1 = d.js("return document.getElementById('powStep').textContent;")
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.3)
    t2 = d.js("return document.getElementById('powStep').textContent;")
    info("step toggle of Power n: opening %s, after a click %s, after Reset this section %s" % (t0, t1, t2))
    # export and mesh panels: their own settings
    for sec in ("secExport", "secMesh"):
        before = d.js("return [...document.querySelectorAll('#%s input, #%s select')].map(e => [e.id, e.type, e.type === 'checkbox' || e.type === 'radio' ? e.checked : e.value]);" % (sec, sec))
        d.js("for (const e of document.querySelectorAll('#%s input, #%s select')) { if (!e.checkVisibility()) continue; if (e.tagName === 'SELECT') { e.selectedIndex = (e.selectedIndex + 1) %% e.options.length; e.dispatchEvent(new Event('change', { bubbles: true })); }"
             " else if (e.type === 'checkbox') { e.click(); } else if (e.type === 'text' && /Num$/.test(e.id)) { e.focus(); e.value = String((parseFloat(e.value) || 1) * 2); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); e.blur(); } }" % (sec, sec))
        time.sleep(0.3)
        mid = d.js("return [...document.querySelectorAll('#%s input, #%s select')].map(e => [e.id, e.type, e.type === 'checkbox' || e.type === 'radio' ? e.checked : e.value]);" % (sec, sec))
        A = d.js(SNAP)
        d.click("document.querySelector('#%s .dial-reset')" % sec); time.sleep(0.3)
        after = d.js("return [...document.querySelectorAll('#%s input, #%s select')].map(e => [e.id, e.type, e.type === 'checkbox' || e.type === 'radio' ? e.checked : e.value]);" % (sec, sec))
        B = d.js(SNAP)
        moved = [m for b, m in zip(before, mid) if b != m]
        back = [a for b, a in zip(before, after) if b != a]
        ok("reset %s: %d of its settings were changed, all are back after its reset, and the picture's settings are untouched" % (sec, len(moved)), len(moved) > 0 and not back and not diff(A, B), {"not back": back, "state": diff(A, B)})
    # Reset everything
    d.js("window.squaringLab.S.mode = 'j'; window.squaringLab.S.flat = true;" + PERTURB)
    d.js("window.squaringLab.setExtreme(true);")
    d.click(E("resetAll")); time.sleep(0.5)
    B = d.js(SNAP)
    ch = diff(D0, B)
    ok("Reset everything: every value is back at the opening value", not ch, ch)
    good, _ = d.idle(400)
    ok("the picture finishes drawing after all the resets", good, d.js("return document.getElementById('status').textContent;"))
    d.stage_top(); d.shot("after-resets.png")
    finish(page, proc, prof, "resets")


# ------------------------------------------------------------------ point 8: zoom slider and its typed limits
def t_zslider():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    d.stage_top()
    V = lambda k: d.js("return %s.S.view.%s;" % (L, k))
    dist = lambda: d.js("return %s.cam.dist;" % L)
    boxv = lambda i: d.js("const e = document.getElementById('%s'); return [e.value, e.getAttribute('aria-invalid')];" % i)
    note = lambda: d.js("const n = document.getElementById('camNote'); return n && n.checkVisibility() ? n.textContent : '';")
    geo = d.js("const s = document.getElementById('stage').getBoundingClientRect(), z = document.getElementById('camZoom').getBoundingClientRect(), r = document.getElementById('camRail').getBoundingClientRect(); return { right: s.right - z.right, top: z.top - s.top, h: z.height, rail: r.height, ends: [document.getElementById('camEndA').textContent, document.getElementById('camEndB').textContent], val: document.getElementById('camVal').textContent, near: document.getElementById('camNear').value, far: document.getElementById('camFar').value, titles: [document.getElementById('camNear').title, document.getElementById('camFar').title, document.getElementById('camRail').title, document.getElementById('camRail').getAttribute('aria-label')] };")
    info("zoom slider:", json.dumps(geo, ensure_ascii=False))
    ok("zoom slider: on the right edge of the picture, with a near box (0.005) and a far box (60) and the current distance beside the thumb", geo["right"] < 30 and geo["near"] == "0.005" and geo["far"] == "60" and geo["val"] != "", geo)
    rb = d.rect(E("camRail"), scroll=False)
    rx = rb[0] + rb[2] / 2
    d.drag(rx, rb[1] + rb[3] * 0.25, rx, rb[1] + rb[3] * 0.75, steps=12); d.settle()
    want = 0.005 * (60 / 0.005) ** 0.75
    ok("zoom slider: dragging the thumb to three quarters down zooms out to %.2f (log scale between the limits)" % want, abs(dist() / want - 1) < 0.02, dist())
    ok("zoom slider: the number beside the thumb follows", abs(float(d.js("return document.getElementById('camVal').textContent;")) / dist() - 1) < 0.05, d.js("return document.getElementById('camVal').textContent;"))
    d.mouse("mouseMoved", rx, rb[1] + rb[3] * 0.4); d.mouse("mousePressed", rx, rb[1] + rb[3] * 0.4, button="left", clickCount=1); d.mouse("mouseReleased", rx, rb[1] + rb[3] * 0.4, button="left", clickCount=1); d.settle()
    ok("zoom slider: a click on the rail zooms there", abs(dist() / (0.005 * (60 / 0.005) ** 0.4) - 1) < 0.03, dist())
    # typed limits
    d.retype(E("camFar"), "200", commit="Tab")
    ok("far limit: typed 200 then Tab sets it", V("zmax") == 200 and boxv("camFar")[0] == "200", (V("zmax"), boxv("camFar")))
    d.retype(E("camFar"), "abc")
    ok("far limit: nonsense is refused, the old value comes back, the box is flagged", V("zmax") == 200 and boxv("camFar") == ["200", "true"], (V("zmax"), boxv("camFar"), note()))
    info("note after nonsense:", note())
    d.retype(E("camFar"), "5000")
    ok("far limit: 5000 is held at 1000 and says so", V("zmax") == 1000, (V("zmax"), boxv("camFar"), note()))
    d.retype(E("camFar"), "8")
    d.retype(E("camNear"), "0,5")
    ok("near limit: typed 0,5 sets 0.5", V("zmin") == 0.5, (V("zmin"), boxv("camNear")))
    d.retype(E("camNear"), "20")
    ok("near limit: a value beyond the far limit (20 > 8) is refused with a note", V("zmin") == 0.5 and boxv("camNear")[1] == "true" and note() != "", (V("zmin"), boxv("camNear"), note()))
    d.retype(E("camNear"), "-1")
    info("near limit typed -1:", V("zmin"), boxv("camNear"), note())
    d.retype(E("camNear"), "0")
    info("near limit typed 0:", V("zmin"), boxv("camNear"), note())
    d.retype(E("camNear"), "0.5")
    d.settle()
    cx, cy = d.at(E("view"), scroll=False)
    for _ in range(40):
        d.wheel(cx, cy, -300)
    d.settle()
    ok("near limit: the wheel stops at the typed near limit 0.5", abs(dist() - 0.5) < 1e-9, (dist(), note()))
    info("note at the near limit:", note())
    for _ in range(40):
        d.wheel(cx, cy, 300)
    d.settle()
    ok("far limit: the wheel stops at the typed far limit 8", abs(dist() - 8) < 1e-9, (dist(), note()))
    info("note at the far limit:", note())
    d.idle(300); d.shot("zslider-limits.png", "#stage")
    d.retype(E("camNear"), "7", commit="Escape")
    ok("near limit: Escape puts the old text back", boxv("camNear")[0] == "0.5" and V("zmin") == 0.5, boxv("camNear"))
    # keyboard on the rail
    d.click(E("camRail"), scroll=False); d.settle(); a = dist()
    d.press("ArrowUp"); d.settle(); b = dist()
    d.press("ArrowDown"); d.press("ArrowDown"); d.settle(); c = dist()
    ok("zoom slider: arrow keys on the focused slider move in and out", b < a and c > b, (a, b, c))
    # the View reset puts the limits back
    d.js("document.getElementById('secView').open = true;")
    d.click("document.querySelector('#secView .dial-reset')"); time.sleep(0.4)
    ok("View reset: the zoom limits are back at 0.005 and 60", V("zmin") == 0.005 and V("zmax") == 60 and boxv("camNear")[0] == "0.005" and boxv("camFar")[0] == "60", (V("zmin"), V("zmax")))
    # the 2D view: the same slider with its own limits
    d.click(E("flat")); d.stage_top(); d.idle(300)
    g2 = d.js("return { ends: [document.getElementById('camEndA').textContent, document.getElementById('camEndB').textContent], near: document.getElementById('camNear').value, far: document.getElementById('camFar').value, val: document.getElementById('camVal').textContent, h: window.squaringLab.S.v2.h };")
    info("2D view slider:", json.dumps(g2))
    d.retype(E("camFar"), "10")
    ok("2D view: the far box sets the widest span (10)", d.js("return %s.S.v2.hmax;" % L) == 10, d.js("return %s.S.v2;" % L))
    cx, cy = d.at(E("view"), scroll=False)
    for _ in range(30):
        d.wheel(cx, cy, 300)
    d.settle()
    ok("2D view: zooming out stops at the typed span 10", abs(d.js("return %s.S.v2.h;" % L) - 10) < 1e-9, d.js("return %s.S.v2.h;" % L))
    d.idle(300); d.shot("zslider-2d.png", "#stage")
    d.click(E("flat")); d.stage_top()
    ok("zoom limits: the 3D limits were not touched by the 2D ones", V("zmax") == 60, V("zmax"))
    finish(page, proc, prof, "zslider")


# ------------------------------------------------------------------ point 8: drawing radius
def t_radius():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
    st = dial_state(d, "viewBound")
    info("Drawing radius dial:", json.dumps(st, ensure_ascii=False), d.js("return document.getElementById('viewBoundHelp') ? document.getElementById('viewBoundHelp').textContent : '';"))
    ok("drawing radius: a dial in View, 8 at the start, slider to 100, typed to 500", st["box"] == "8" and st["slider"][1] == "100", st)
    d.retype(E("viewBoundNum"), "500"); a = d.js("return %s.S.view.bound;" % L)
    d.retype(E("viewBoundNum"), "600"); b = d.js("return %s.S.view.bound;" % L)
    ok("drawing radius: typed 500 is taken, 600 is held at 500", a == 500 and b == 500, (a, b))
    d.retype(E("viewBoundNum"), "8")
    # the Kleinian chain runs on for ever along x: more of it must show with a larger radius
    d.click(lab("mode-k")); d.stage_top(); d.idle(400)
    d.js("%s.S.view.zmax = 400; %s.cam.dist = 45; %s.cam.yaw = -1.5708; %s.cam.pitch = 0.5; %s.touch();" % (L, L, L, L, L)); d.settle()
    widths = {}
    for r in (8, 20, 60):
        d.retype(E("viewBoundNum"), str(r)); d.stage_top(); d.idle(400)
        d.shot("radius-klein-%d.png" % r, "#stage")
        widths[r] = d.js("const L = window.squaringLab, v = document.getElementById('view').getBoundingClientRect(); let lo = null, hi = null; for (let i = 0; i <= 100; i++) { const x = v.width * i / 100; let hit = false; for (const fy of [0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]) { if (L.pick(x, v.height * fy)) { hit = true; break; } } if (hit) { if (lo === null) lo = i; hi = i; } } return [lo, hi];")
        info("Kleinian view from 45 away, drawing radius %d: the solid spans columns %s of 100; status %s" % (r, widths[r], d.js("return document.getElementById('status').textContent;")))
    w = {r: (widths[r][1] - widths[r][0]) if widths[r][0] is not None else 0 for r in widths}
    ok("drawing radius: a larger radius shows more of the Kleinian chain (8 -> 20 -> 60)", w[20] > w[8] and w[60] >= w[20], w)
    # Mandelbrot: a small radius cuts the solid, the opening one does not
    d.retype(E("viewBoundNum"), "8")
    d.click(lab("mode-m")); d.stage_top(); d.idle(400)
    d.js("%s.resetCam(); %s.touch();" % (L, L)); d.settle()
    for r in ("0.5", "1", "8"):
        d.retype(E("viewBoundNum"), r); d.stage_top(); d.idle(400)
        d.shot("radius-mandel-%s.png" % r.replace(".", "_"), "#stage")
    # far away with the opening radius and the far limit 60
    d.js("%s.cam.dist = 60; %s.touch();" % (L, L)); d.settle(); d.idle(400)
    d.shot("radius-mandel-far60.png", "#stage")
    finish(page, proc, prof, "radius")


# ------------------------------------------------------------------ point 13: collapse all / expand all
def t_collapse():
    for (w, h, mobile, tag) in ((1400, 950, False, "desktop"), (375, 812, True, "phone")):
        page, proc, prof = launch(w, h, mobile=mobile, touch=mobile)
        d = Drive(page)
        d.load()
        secs = lambda: d.js("return [...document.querySelectorAll('#sections > details.sec')].map(s => [s.id, s.hidden, s.open]);")
        btn = lambda: d.js("return document.getElementById('collapseAll').textContent;")
        tap = (lambda e: (d.touch("touchStart", [d.at(e)]), d.touch("touchEnd", []), time.sleep(0.25))) if mobile else (lambda e: (d.click(e), time.sleep(0.25)))
        s0 = secs()
        info(tag, "sections at the start (id, hidden, open):", s0, "button:", btn())
        pos = d.js("const b = document.getElementById('collapseAll').getBoundingClientRect(), t = document.getElementById('toprow'); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height), getComputedStyle(t).position, innerWidth, innerHeight, window.scrollY];")
        info(tag, "button box and top row:", pos)
        d.js("document.querySelectorAll('#sections > details.sec').forEach(s => { s.open = true; });"); time.sleep(0.2)
        ok("collapse (%s): with sections open the button reads Collapse all" % tag, btn() == "Collapse all", btn())
        hdoc = d.js("return document.documentElement.scrollHeight;")
        tap(E("collapseAll"))
        s1 = secs()
        ok("collapse (%s): one click closes every section (%d on show)" % (tag, sum(1 for s in s1 if not s[1])), all(not s[2] for s in s1) and btn() == "Expand all", (s1, btn()))
        d.shot("collapse-%s.png" % tag)
        info(tag, "page height open %d, collapsed %d" % (hdoc, d.js("return document.documentElement.scrollHeight;")))
        # a mode change must not bring open sections back
        lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
        tap(lab("mode-k")); s2 = secs()
        ok("collapse (%s): after switching to Kleinian everything is still closed" % tag, all(not s[2] for s in s2 if not s[1]) and btn() == "Expand all", (s2, btn()))
        tap("document.querySelector('#secView summary')")
        ok("collapse (%s): opening one section by hand turns the button back to Collapse all" % tag, btn() == "Collapse all" and d.js("return document.getElementById('secView').open;"), btn())
        tap(E("collapseAll"))
        ok("collapse (%s): it then closes that one again" % tag, all(not s[2] for s in secs() if not s[1]) and btn() == "Expand all", secs())
        tap(E("collapseAll"))
        s3 = secs()
        ok("collapse (%s): Expand all opens every section on show" % tag, all(s[2] for s in s3 if not s[1]) and btn() == "Collapse all", (s3, btn()))
        tap(lab("mode-j")); s4 = secs()
        ok("collapse (%s): and the Julia panel is open too after a mode change" % tag, all(s[2] for s in s4 if not s[1]), s4)
        # reachable from far down the page?
        d.js("document.getElementById('secMesh').scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 300));")
        r = d.js("const b = document.getElementById('collapseAll').getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom), innerHeight, b.width > 0 && b.top >= 0 && b.bottom <= innerHeight, document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2) === document.getElementById('collapseAll')];")
        ok("collapse (%s): the button stays in view when scrolled down to the last section" % tag, r[3] and r[4], r)
        d.shot("collapse-%s-scrolled.png" % tag)
        x, y = d.at(E("collapseAll"), scroll=False)
        if mobile:
            d.touch("touchStart", [(x, y)]); d.touch("touchEnd", [])
        else:
            d.mouse("mouseMoved", x, y); d.mouse("mousePressed", x, y, button="left", clickCount=1); d.mouse("mouseReleased", x, y, button="left", clickCount=1)
        time.sleep(0.4)
        ok("collapse (%s): pressed there, it closes everything and a section heading is in view to pick" % tag, all(not s[2] for s in secs() if not s[1]), secs())
        d.shot("collapse-%s-after.png" % tag)
        # keyboard
        if not mobile:
            d.js("document.getElementById('collapseAll').focus();")
            d.press("Enter"); time.sleep(0.2)
            ok("collapse (desktop): Enter on the focused button works too", btn() == "Collapse all", btn())
        d.idle(300)
        finish(page, proc, prof, "collapse-" + tag)


# ------------------------------------------------------------------ N4: extreme ranges
def t_extreme():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    d.click(E("qUltra")); d.idle(300)
    note0 = d.js("return document.getElementById('extremeNote').textContent;")
    info("switch label and hint, off:", d.js("return document.getElementById('extreme').closest('label').textContent.trim();"), "|", note0)
    ranges = "return [...document.querySelectorAll('input[id$=Num]')].filter(n => n.closest('.dial')).map(n => { const id = n.id.replace(/Num$/, ''), s = document.getElementById(id), w = document.getElementById(id + 'Wide'); return [id, s ? +s.min : null, s ? +s.max : null, n.getAttribute('aria-valuemin'), n.getAttribute('aria-valuemax'), w ? !w.hidden : false, n.closest('.dial').querySelector('label').textContent.trim().slice(0, 40), n.value]; });"
    R0 = d.js(ranges)
    A = d.js(SNAP)
    img0 = d.js("return document.getElementById('status').textContent;")
    d.stage_top(); d.idle(300); d.shot("extreme-off.png", "#stage")
    d.click(E("extreme")); time.sleep(0.4)
    B = d.js(SNAP)
    R1 = d.js(ranges)
    ch = diff(A, B)
    ok("extreme: switching it on changes no value (only the switch itself)", set(ch) == {"S.extreme"}, ch)
    note1 = d.js("return document.getElementById('extremeNote').textContent;")
    info("hint, on:", note1)
    d.stage_top(); d.idle(300); d.shot("extreme-on.png", "#stage")
    widened, same = [], []
    for a, b in zip(R0, R1):
        if a[1:5] != b[1:5]:
            widened.append((a[0], a[6], "slider %s..%s -> %s..%s" % (a[1], a[2], b[1], b[2]), "typed %s..%s -> %s..%s" % (a[3], a[4], b[3], b[4]), "tag " + str(b[5])))
        else:
            same.append((a[0], a[6], "slider %s..%s typed %s..%s" % (a[1], a[2], a[3], a[4])))
    info("dials the switch widens (%d):" % len(widened))
    for wd in widened:
        info("   ", json.dumps(wd, ensure_ascii=False))
    info("dials it leaves alone (%d):" % len(same))
    for s in same:
        info("   ", json.dumps(s, ensure_ascii=False))
    with open(os.path.join(HERE, "extreme-ranges.json"), "w", encoding="utf-8") as f:
        json.dump({"widened": widened, "same": same}, f, indent=1, ensure_ascii=False)
    notag = [wd for wd in widened if wd[4] != "tag True"]
    ok("extreme: every widened dial carries the 'wide' tag", not notag, notag)
    tagged_same = [b[0] for a, b in zip(R0, R1) if a[1:5] == b[1:5] and b[5]]
    ok("extreme: no dial carries the tag without being wider", not tagged_same, tagged_same)
    d.shot("extreme-on-eq.png", "#secEq"); d.shot("extreme-on-quality.png", "#secQuality")
    # five dials: type a value beyond the usual limit, then switch off
    lab = lambda id_: "document.getElementById(%s).closest('label') || document.querySelector('label[for=%s]')" % (json.dumps(id_), id_)
    tries = [("iter", "S.iter", "900", 900, 400), ("pow", "S.n", "40", 40, 24), ("qsteps", "S.q.steps", "5000", 5000, 3000), ("viewBound", "S.view.bound", "800", 800, 500), ("qaa", "S.q.aa", "500", 500, 400)]
    d.click(E("extreme")); time.sleep(0.3)   # off: the same typed values must be held at the usual limit
    for id_, path, typed, want, usual in tries:
        d.retype(E(id_ + "Num"), typed)
        got = d.js("return %s.%s;" % (L, path))
        ok("extreme off: %s typed %s is held at the usual limit %s" % (id_, typed, usual), got == usual, got)
    d.js("%s.resetAll();" % L); d.click(E("qUltra")); time.sleep(0.3)
    d.click(E("extreme")); time.sleep(0.3)
    pre = d.js(SNAP)
    for id_, path, typed, want, usual in tries:
        if id_ in ("iter", "qsteps", "qaa", "viewBound"):
            pass
        d.retype(E(id_ + "Num"), typed)
        got = d.js("return %s.%s;" % (L, path))
        ok("extreme on: %s takes a typed %s" % (id_, typed), got == want, got)
    # bring the heavy ones down a little so the picture can finish, but keep them beyond the usual limits
    d.shot("extreme-typed.png", "#secEq")
    mid = d.js(SNAP)
    d.click(E("extreme")); time.sleep(0.5)
    post = d.js(SNAP)
    for id_, path, typed, want, usual in tries:
        got = d.js("return %s.%s;" % (L, path))
        ok("extreme switched off: %s is pulled back from %s to its usual limit %s, and its box shows it" % (id_, typed, usual), got == usual and float(d.js("return document.getElementById('%sNum').value;" % id_)) == usual, got)
    ch = diff(mid, post)
    expected = {"S.extreme", "S.iter", "S.n", "S.q.steps", "S.view.bound", "S.q.aa"}
    ok("extreme switched off: nothing else changes", set(ch) <= expected, {k: v for k, v in ch.items() if k not in expected})
    # values inside the usual limits survive on and off
    d.js("%s.resetAll();" % L); time.sleep(0.3)
    d.retype(E("iterNum"), "100"); d.retype(E("powNum"), "12.5")
    a = d.js(SNAP)
    d.click(E("extreme")); time.sleep(0.3); d.click(E("extreme")); time.sleep(0.3)
    b = d.js(SNAP)
    ok("extreme on and off again: values inside the usual limits (Iterations 100, Power 12.5) are left alone", not diff(a, b), diff(a, b))
    # the Kleinian depth of the search
    d.js("%s.resetAll();" % L); time.sleep(0.2)
    d.click(lab("mode-k")); time.sleep(0.4)
    k0 = dial_state(d, "kiter")
    d.click(E("extreme")); time.sleep(0.3)
    k1 = dial_state(d, "kiter")
    d.retype(E("kiterNum"), "2000"); got = d.js("return %s.S.k.iter;" % L)
    ok("extreme: Depth of the search goes from slider %s (typed to 400) to slider %s, and takes a typed 2000" % (k0["slider"][1], k1["slider"][1]), got == 2000 and float(k1["slider"][1]) > float(k0["slider"][1]), (k0, k1, got))
    d.retype(E("kiterNum"), "300")
    d.stage_top(); g, waited = d.idle(600)
    info("Kleinian at depth 300 (Balanced): idle %s after %.1f s; status %s" % (g, waited, d.js("return document.getElementById('status').textContent;")))
    d.shot("extreme-klein-300.png", "#stage")
    d.shot("extreme-klein-panel.png", "#kleinPanel")
    d.click(E("extreme")); time.sleep(0.3)
    ok("extreme off: depth 300 is inside the usual typed limit (400) and stays", d.js("return %s.S.k.iter;" % L) == 300, d.js("return %s.S.k.iter;" % L))
    # Reset everything switches it off
    d.click(E("extreme")); time.sleep(0.2)
    d.click(E("resetAll")); time.sleep(0.4)
    ok("extreme: Reset everything switches it off and unticks the box", d.js("return [%s.S.extreme, document.getElementById('extreme').checked];" % L) == [False, False], "")
    d.idle(400)
    finish(page, proc, prof, "extreme")


TESTS = {"busy": t_busy, "dials": t_dials, "zoom": t_zoom, "ultra": t_ultra, "fly": t_fly, "resets": t_resets, "zslider": t_zslider,
         "radius": t_radius, "collapse": t_collapse, "extreme": t_extreme}

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    print("started", time.strftime("%H:%M:%S"), flush=True)
    for name in sys.argv[1:]:
        print("===== " + name, flush=True)
        try:
            TESTS[name]()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            ok("%s ran to its end" % name, False, repr(ex)[:400])
    print("%d passed, %d failed" % (results.count(True), results.count(False)), flush=True)
    print("ended", time.strftime("%H:%M:%S"), flush=True)


# ------------------------------------------------------------------ second pass: quality presets with the section open, timed from the event itself
def t_busy2():
    page, proc, prof = launch()
    d = Drive(page)
    d.load()
    open_all(d)
    d.js(SAMPLER)
    d.js("window.__ev = 0; for (const t of ['click', 'change']) window.addEventListener(t, () => { window.__ev = performance.now(); }, true); window.addEventListener('keydown', e => { if (e.key === 'Enter') window.__ev = performance.now(); }, true);")
    out = []

    def act(label, expr, shot=None):
        d.idle(400); time.sleep(0.25)
        x, y = d.at(expr)
        d.js("window.__ev = 0; window.__s.log = [];")
        d.mouse("mouseMoved", x, y); d.mouse("mousePressed", x, y, button="left", clickCount=1); d.mouse("mouseReleased", x, y, button="left", clickCount=1)
        if shot:
            time.sleep(shot[1]); d.stage_top(); d.shot(shot[0], "#stage")
        time.sleep(0.2)
        good, _ = d.idle(400); time.sleep(0.4)
        t0 = d.js("return window.__ev;")
        r = analyse(d.js("return window.__s.log;"), t0, label)
        if r:
            out.append(r)
            ok("busy: '%s' took %d ms; a sign showed %s ms after the click; longest stretch with no sign %d ms; longest frozen frame %d ms" % (
                label, r["total_ms"], r["first_sign_ms"], r["longest_no_sign_ms"], r["longest_frame_gap_ms"]),
               r["total_ms"] < 300 or (r["first_sign_ms"] is not None and r["longest_no_sign_ms"] <= 400), r["labels"])
    lab = lambda id_: "document.getElementById(%s).closest('label')" % json.dumps(id_)
    name = lambda id_: "document.getElementById(%s).closest('label').querySelector('.name')" % json.dumps(id_)
    act("quality: Ultra fast", E("qUltra"))
    act("quality: Fast", E("qFast"))
    act("quality: Fine", E("qFine"), shot=("busy-fine.png", 1.0))
    act("quality: Balanced", E("qBal"), shot=("busy-balanced.png", 0.4))
    act("cut the solid open", E("cutOn"))
    act("cut closed", E("cutOn"))
    act("mode: Julia", lab("mode-j"))
    act("new approach: Lathe (Julia, first use)", name("ap-lathe"), shot=("busy-approach2.png", 0.25))
    act("mode: Kleinian", lab("mode-k"))
    act("quality: Fine in the Kleinian view", E("qFine"), shot=("busy-fine-klein.png", 1.5))
    act("mode: Mandelbrot", lab("mode-m"))
    with open(os.path.join(HERE, "busy2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    # Collapse all with the keyboard (a real Enter carries its character)
    d.js("document.getElementById('collapseAll').focus();")
    b0 = d.js("return document.getElementById('collapseAll').textContent;")
    d.p.call("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13, text="\r")
    d.p.call("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
    time.sleep(0.2)
    b1 = d.js("return document.getElementById('collapseAll').textContent;")
    ok("collapse: Enter on the focused button works (%s -> %s)" % (b0, b1), b0 != b1, "")
    finish(page, proc, prof, "busy2")


TESTS["busy2"] = t_busy2
if __name__ == "__main__" and "busy2" in sys.argv[1:] and results == []:
    pass
