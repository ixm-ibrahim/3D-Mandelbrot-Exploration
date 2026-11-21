"""Seeded random walk over every visible control of the lab, with real input (mouse, wheel, keyboard) where it can.

  python monkey.py --seed 1 [--steps 400]            random walk, log in walk-<seed>.jsonl, findings in walk-<seed>.findings.txt
  python monkey.py --replay walk-1.jsonl --only 10-57  replay logged steps (by control, not by re-rolling the dice)

Every step is logged before it is applied, so a failing run can be replayed. A linear congruential generator makes
the walk repeatable; Math.random is not used.
"""
import argparse, io, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

VK = {"Tab": 9, "Enter": 13, "Escape": 27, "ArrowLeft": 37, "ArrowUp": 38, "ArrowRight": 39, "ArrowDown": 40,
      "PageUp": 33, "PageDown": 34, " ": 32, "w": 87, "a": 65, "s": 83, "d": 68, "q": 81, "e": 69, "f": 70,
      "+": 107, "-": 189, "=": 187, "Shift": 16, "Home": 36, "End": 35}
CODE = {" ": "Space", "w": "KeyW", "a": "KeyA", "s": "KeyS", "d": "KeyD", "q": "KeyQ", "e": "KeyE", "f": "KeyF",
        "+": "NumpadAdd", "-": "Minus", "=": "Equal", "Shift": "ShiftLeft"}

HELPER = r"""
window.__mk = (() => {
  const vis = e => {
    if (e.disabled) return false;
    let t = e;
    if (e.tagName === 'INPUT' && (e.type === 'radio' || e.type === 'checkbox')) t = e.closest('label') || e;
    if (t.checkVisibility && !t.checkVisibility()) return false;
    const r = t.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const desc = e => {
    if (e.id) return { id: e.id };
    let a = e.parentElement; while (a && !a.id) a = a.parentElement;
    const tag = e.tagName.toLowerCase();
    const list = a ? [...a.querySelectorAll(tag)] : [...document.querySelectorAll(tag)];
    return { anc: a ? a.id : '', tag, idx: list.indexOf(e), cls: String(e.getAttribute('class') || '').slice(0, 40), text: (e.textContent || '').trim().slice(0, 30) };
  };
  const find = d => {
    if (d.id) return document.getElementById(d.id);
    const a = d.anc ? document.getElementById(d.anc) : document;
    return a ? (a.querySelectorAll(d.tag)[d.idx] || null) : null;
  };
  const cat = e => {
    const t = e.tagName, ty = (e.type || '').toLowerCase();
    if (t === 'SELECT') return 'select';
    if (t === 'SUMMARY') return 'summary';
    if (t === 'INPUT') {
      if (ty === 'range') return 'range';
      if (ty === 'checkbox') return 'check';
      if (ty === 'radio') return 'radio';
      if (ty === 'text') return /Num$/.test(e.id) ? 'num' : 'text';
      return 'other';
    }
    if (t === 'BUTTON') return e.closest('.dial') ? 'dialbtn' : 'button';
    return 'other';
  };
  return {
    find,
    list() {
      const out = [];
      for (const e of document.querySelectorAll('input, select, button, summary')) {
        if (!vis(e)) continue;
        const c = cat(e); if (c === 'other') continue;
        const d = desc(e); d.cat = c;
        if (c === 'range') { d.min = +e.min; d.max = +e.max; d.step = +e.step; }
        if (c === 'num') { const r = document.getElementById(e.id.replace(/Num$/, '')); if (r) { d.min = +r.min; d.max = +r.max; d.step = +r.step; } }
        if (c === 'select') d.n = e.options.length;
        if (c === 'dialbtn') d.cls = String(e.getAttribute('class') || '');
        out.push(d);
      }
      return out;
    },
    point(d, fx, fy) {
      const e = find(d); if (!e) return null;
      let t = e, r = e.getBoundingClientRect();
      if (r.width < 4 || r.height < 4 || getComputedStyle(e).opacity === '0' || e.type === 'radio' || e.type === 'checkbox') {
        const lab = e.closest('label') || (e.id && document.querySelector('label[for="' + e.id + '"]'));
        if (lab) t = lab;
      }
      t.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
      r = t.getBoundingClientRect();
      const x = r.left + r.width * fx, y = r.top + r.height * fy;
      const hit = document.elementFromPoint(x, y);
      const lab = hit && hit.closest && hit.closest('label');
      const ok = !!hit && (hit === t || t.contains(hit) || hit.contains(e) || (lab && lab.contains(e)));
      return { x, y, ok, hit: hit ? (hit.id || hit.tagName + '.' + (hit.getAttribute('class') || '')) : null };
    },
    stage() {
      const s = document.getElementById('stage'); s.scrollIntoView({ block: 'center', behavior: 'instant' });
      const r = document.getElementById('view').getBoundingClientRect();
      return [r.left, r.top, r.width, r.height];
    },
    masks() {
      const s = document.getElementById('stage'), sr = s.getBoundingClientRect(), out = [];
      const walk = el => { for (const c of el.children) { if (c.id === 'view') continue; if (c.checkVisibility && !c.checkVisibility()) continue; const r = c.getBoundingClientRect(); if (!r.width || !r.height) continue; if (r.width * r.height > 0.3 * sr.width * sr.height) walk(c); else out.push([r.left - sr.left, r.top - sr.top, r.width, r.height]); } };
      walk(s);
      return out;
    },
    health() {
      const L = window.squaringLab, bad = [], seen = new Set();
      const walk = (o, p, d) => { if (d > 6 || !o || seen.has(o)) return; seen.add(o); for (const k of Object.keys(o)) { const v = o[k]; if (typeof v === 'number') { if (!Number.isFinite(v)) bad.push(p + k + '=' + v); } else if (v && typeof v === 'object' && !(v instanceof Node)) walk(v, p + k + '.', d + 1); } };
      walk(L.S, 'S.', 0); walk(L.cam, 'cam.', 0);
      try { walk(L.basis(), 'basis.', 0); } catch (err) { bad.push('basis() threw ' + err.message); }
      const g = document.getElementById('glfail'), b = document.getElementById('busy');
      const plays = [...document.querySelectorAll('.dial-play[aria-pressed="true"]')].map(p => ({ id: p.id, shown: !!(p.checkVisibility && p.checkVisibility()) }));
      const boxes = [];
      for (const e of document.querySelectorAll('input[type=text]')) { if (/Num$/.test(e.id) && /nan|infinity|undefined|e\+|e-/i.test(e.value)) boxes.push(e.id + '=' + e.value); }
      return { bad, failed: L.R.failed || '', glfail: g && !g.hidden ? g.textContent.slice(0, 60) : '', busy: b && !b.hidden ? b.textContent : '',
        idle: !!L.idle(), status: document.getElementById('status').textContent, plays, boxes,
        st: { mode: L.S.mode, ap: L.S.approach, flat: !!L.S.flat, mosaic: !!L.S.mosaic, n: L.S.n, iter: L.S.iter, eq: L.S.eq, fly: !!L.S.view.fly, dist: L.cam.dist, de: L.S.q.de, aa: L.S.q.aa, res: L.S.q.res, bound: L.S.view.bound } };
    },
    sig() { const L = window.squaringLab, d = document.getElementById('drawProgress'); return document.getElementById('status').textContent + '|' + (d && d.firstChild ? d.firstChild.style.transform : '') + '|' + [L.R.restart, !!L.R.prog, !!L.R.pend, L.R.wantPrev, L.renderIdle(), L.cardIdle()].join(','); },
  };
})();
"""

EQS = ["z^n + c", "z^2 + c", "z^3 + c", "z^n + c + 0.1", "z*z + c", "z^-2 + c", "z^n - c", "z^2 + c*c", "(z + c)^2", "z^n + z + c",
       "1/z + c", "z^2 + c/z", "z^", "c", "", "z^n + ", "sin(z) + c", "z^(1/2) + c", "z^n + c)", "0/0 + z", "z^0.5 + c", "z^n * z^n + c"]
Z0S = ["0", "c", "1", "0.5", "-1", "z", "", "c/2", "1/c", "c^2", "abc", "1e9"]
JUNK = ["abc", "", "-", "1e999", "NaN", "Infinity", "-Infinity", "1,5", "−3", "0x10", "1/0", "  7  ", "1e-9", ".", "--2", "1e3", "-0", "+4", "2.5.1", "9" * 30]


class LCG:
    def __init__(self, seed): self.s = seed & 0xFFFFFFFF
    def nxt(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s
    def rnd(self): return (self.nxt() >> 8) / float(1 << 24)
    def below(self, n): return int(self.rnd() * n) if n > 0 else 0
    def pick(self, seq): return seq[self.below(len(seq))]


class Drive:
    def __init__(self, page):
        self.p = page

    def js(self, code): return self.p.js(code)
    def mouse(self, kind, x, y, **kw): self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click_at(self, x, y, count=1, modifiers=0):
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", clickCount=count, modifiers=modifiers)
        self.mouse("mouseReleased", x, y, button="left", clickCount=count, modifiers=modifiers)

    def key(self, name, modifiers=0, hold=0.0):
        kw = dict(key=name, code=CODE.get(name, name), windowsVirtualKeyCode=VK[name], modifiers=modifiers)
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        if hold: time.sleep(hold)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def text(self, s): self.p.call("Input.insertText", text=s)


def fmt_num(v):
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return s or "0"


def choose(rng, d):
    """Turn the dice into one logged step. Uses only the page's list of visible controls and the generator."""
    ctrls = d.js("return window.__mk.list();")
    by = {}
    for c in ctrls:
        by.setdefault(c["cat"], []).append(c)
    weights = [("num", 18), ("range", 10), ("dialbtn", 10), ("check", 8), ("select", 10), ("radio", 10), ("button", 18),
               ("summary", 3), ("stage", 12), ("text", 5)]
    weights = [(k, w) for k, w in weights if k == "stage" or by.get(k)]
    r = rng.rnd() * sum(w for _, w in weights)
    cat = weights[-1][0]
    for k, w in weights:
        if r < w: cat = k; break
        r -= w
    if cat == "stage":
        g = rng.pick(["wheel", "wheel", "wheel", "drag", "drag", "drag", "shiftdrag", "dbl", "key", "key", "click", "wheelburst"])
        st = {"cat": "stage", "g": g, "x": round(0.05 + 0.9 * rng.rnd(), 3), "y": round(0.05 + 0.9 * rng.rnd(), 3)}
        if g in ("wheel", "wheelburst"): st["dy"] = rng.pick([-100, 100, -100, 100, -300, 300, -1200, 1200, -33, 33, -4000, 4000]); st["k"] = 1 + rng.below(8)
        if g in ("drag", "shiftdrag"): st["x2"] = round(0.05 + 0.9 * rng.rnd(), 3); st["y2"] = round(0.05 + 0.9 * rng.rnd(), 3)
        if g == "key": st["key"] = rng.pick(["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-", "=", "w", "a", "s", "d", "q", "e", " ", "f", "Home", "PageUp", "PageDown"]); st["hold"] = rng.pick([0, 0.05, 0.3])
        return st
    c = dict(rng.pick(by[cat]))
    st = {"cat": cat, "el": {k: c[k] for k in ("id", "anc", "tag", "idx") if k in c}, "what": c.get("id") or ("%s#%s[%d] %s" % (c.get("tag"), c.get("anc"), c.get("idx", -1), c.get("text", "")))}
    if cat == "num":
        lo, hi, step = c.get("min", 0), c.get("max", 1), c.get("step", 0.1) or 0.1
        kind = rng.pick(["in", "in", "in", "in", "edge", "out", "out", "junk", "fine", "whole"])
        span = hi - lo
        if kind == "in": v = fmt_num(lo + span * rng.rnd())
        elif kind == "fine": v = "%.9f" % (lo + span * rng.rnd())
        elif kind == "whole": v = str(int(round(lo + span * rng.rnd())))
        elif kind == "edge": v = fmt_num(rng.pick([lo, hi, lo - step, hi + step, 0]))
        elif kind == "out": v = fmt_num(rng.pick([lo - span * (1 + 9 * rng.rnd()), hi + span * (1 + 9 * rng.rnd()), -1e6, 1e6, 1e12, -1e12]))
        else: v = rng.pick(JUNK)
        st["v"] = v; st["commit"] = rng.pick(["Enter", "Enter", "Enter", "Tab", "Tab", "Escape", "blur"]); st["kind"] = kind
    elif cat == "text":
        i = c.get("id")
        if i == "eq": st["v"] = rng.pick(EQS)
        elif i == "z0": st["v"] = rng.pick(Z0S)
        elif i in ("camNear", "camFar"): st["v"] = rng.pick([fmt_num(10 ** (-3 + 6 * rng.rnd())), fmt_num(10 ** (-3 + 6 * rng.rnd())), rng.pick(JUNK), "0", "-5", "1000", "0.001", "100000"])
        else: st["v"] = rng.pick(["monkey %d" % rng.below(1000), "", "<b>x</b>", "a" * 60, "  ", "éè — '\""])
        st["commit"] = rng.pick(["Enter", "Enter", "Tab", "blur"])
    elif cat == "range":
        st["how"] = rng.pick(["click", "click", "click", "drag", "keys"])
        st["fx"] = round(0.02 + 0.96 * rng.rnd(), 3); st["fx2"] = round(0.02 + 0.96 * rng.rnd(), 3)
        st["key"] = rng.pick(["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"]); st["k"] = 1 + rng.below(6)
    elif cat == "select":
        st["i"] = rng.below(c.get("n", 1))
    elif cat == "dialbtn":
        st["k"] = rng.pick([1, 1, 1, 2, 3]); st["shift"] = rng.rnd() < 0.15; st["cls"] = c.get("cls", "")
    return st


def click_el(d, st, fx=0.5, fy=0.5, count=1, modifiers=0):
    pt = d.js("return window.__mk.point(%s, %s, %s);" % (json.dumps(st["el"]), fx, fy))
    if pt is None:
        return "missing"
    if pt["ok"]:
        d.click_at(pt["x"], pt["y"], count, modifiers)
        return "mouse"
    d.js("const e = window.__mk.find(%s); if (e) e.click();" % json.dumps(st["el"]))
    return "js-click (covered by %s)" % pt["hit"]


def apply(d, st):
    cat = st["cat"]
    if cat == "stage":
        x0, y0, w, h = d.js("return window.__mk.stage();")
        x, y = x0 + w * st["x"], y0 + h * st["y"]
        g = st["g"]
        if g in ("wheel", "wheelburst"):
            d.mouse("mouseMoved", x, y)
            for _ in range(st["k"] if g == "wheelburst" else 1):
                d.mouse("mouseWheel", x, y, deltaX=0, deltaY=st["dy"])
        elif g in ("drag", "shiftdrag"):
            mod = 8 if g == "shiftdrag" else 0
            x2, y2 = x0 + w * st["x2"], y0 + h * st["y2"]
            d.mouse("mouseMoved", x, y)
            d.mouse("mousePressed", x, y, button="left", clickCount=1, modifiers=mod)
            for i in range(1, 7):
                d.mouse("mouseMoved", x + (x2 - x) * i / 6, y + (y2 - y) * i / 6, button="left", buttons=1, modifiers=mod)
            d.mouse("mouseReleased", x2, y2, button="left", clickCount=1, modifiers=mod)
        elif g == "dbl":
            d.click_at(x, y, 1); d.click_at(x, y, 2)
        elif g == "click":
            d.click_at(x, y, 1)
        elif g == "key":
            d.js("document.getElementById('view').focus({ preventScroll: true });")
            d.key(st["key"], hold=st.get("hold", 0))
        return "real"
    if cat in ("num", "text"):
        how = click_el(d, st, count=3)
        if how == "missing": return how
        if how != "mouse":
            d.js("const e = window.__mk.find(%s); e.focus(); e.select();" % json.dumps(st["el"]))
        else:
            d.js("const e = window.__mk.find(%s); if (document.activeElement === e) e.select();" % json.dumps(st["el"]))
        if st["v"] == "":
            d.p.call("Input.dispatchKeyEvent", type="rawKeyDown", key="Delete", code="Delete", windowsVirtualKeyCode=46)
            d.p.call("Input.dispatchKeyEvent", type="keyUp", key="Delete", code="Delete", windowsVirtualKeyCode=46)
            d.js("const e = window.__mk.find(%s); if (e && document.activeElement === e && e.value !== '') { e.value = ''; e.dispatchEvent(new Event('input', { bubbles: true })); }" % json.dumps(st["el"]))
        else:
            d.text(st["v"])
        c = st["commit"]
        if c == "blur":
            x0, y0, w, h = d.js("const r = document.querySelector('h1').getBoundingClientRect(); return [r.left, r.top, r.width, r.height];")
            d.js("document.activeElement && document.activeElement.blur();")
        else:
            d.key(c)
        return how + "+keys"
    if cat == "range":
        if st["how"] == "click":
            return click_el(d, st, fx=st["fx"])
        if st["how"] == "drag":
            a = d.js("return window.__mk.point(%s, %s, 0.5);" % (json.dumps(st["el"]), st["fx"]))
            if a is None: return "missing"
            b = d.js("return window.__mk.point(%s, %s, 0.5);" % (json.dumps(st["el"]), st["fx2"]))
            d.mouse("mouseMoved", a["x"], a["y"])
            d.mouse("mousePressed", a["x"], a["y"], button="left", clickCount=1)
            for i in range(1, 6):
                d.mouse("mouseMoved", a["x"] + (b["x"] - a["x"]) * i / 5, a["y"], button="left", buttons=1)
            d.mouse("mouseReleased", b["x"], a["y"], button="left", clickCount=1)
            return "mouse-drag"
        how = d.js("const e = window.__mk.find(%s); if (!e) return 'missing'; e.focus({ preventScroll: false }); return 'keys';" % json.dumps(st["el"]))
        if how == "missing": return how
        for _ in range(st["k"]):
            d.key(st["key"])
        return how
    if cat == "select":
        return d.js("const e = window.__mk.find(%s); if (!e) return 'missing'; e.focus(); if (%d >= e.options.length) return 'no such option'; e.selectedIndex = %d; "
                    "e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); return 'change-event: ' + e.options[e.selectedIndex].text.slice(0, 40);"
                    % (json.dumps(st["el"]), st["i"], st["i"]))
    if cat == "dialbtn":
        how = ""
        for _ in range(st.get("k", 1)):
            how = click_el(d, st, modifiers=8 if st.get("shift") else 0)
        return how
    return click_el(d, st)


def stage_stats(d, path):
    """Screenshot the stage and report how uniform the picture is outside the overlay controls."""
    import numpy as np
    from PIL import Image
    d.p.shot(path, "#stage")
    masks = d.js("return window.__mk.masks();")
    im = np.asarray(Image.open(path).convert("RGB")).astype("int16")
    keep = np.ones(im.shape[:2], bool)
    for x, y, w, h in masks:
        keep[max(0, int(y) - 2):int(y + h) + 3, max(0, int(x) - 2):int(x + w) + 3] = False
    keep[:3, :] = keep[-6:, :] = False; keep[:, :3] = keep[:, -3:] = False
    px = im[keep]
    if not len(px):
        return {"n": 0}
    rng = (px.max(0) - px.min(0)).tolist()
    q = (px // 8).astype("int32"); codes = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]
    vals, counts = np.unique(codes, return_counts=True)
    return {"n": int(len(px)), "range": rng, "modal_share": round(float(counts.max()) / len(px), 5), "colours": int(len(vals)), "mean": [round(float(v), 1) for v in px.mean(0)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--replay"); ap.add_argument("--only"); ap.add_argument("--tag"); ap.add_argument("--idle-timeout", type=float, default=150)
    ap.add_argument("--every", type=int, default=25); ap.add_argument("--pause", type=float, default=0.08)
    ap.add_argument("--shots", action="store_true", help="in replay: a stage shot after every step")
    ap.add_argument("--url")
    a = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    tag = a.tag or ("replay" if a.replay else "walk-%d" % a.seed)
    shots = os.path.join(HERE, tag); os.makedirs(shots, exist_ok=True)
    plan = None
    if a.replay:
        with open(a.replay, encoding="utf-8") as f:
            plan = [json.loads(l) for l in f if l.strip()]
        plan = [p for p in plan if "step" in p]
        if a.only:
            want = set()
            for part in a.only.split(","):
                if "-" in part: lo, hi = part.split("-"); want |= set(range(int(lo), int(hi) + 1))
                else: want.add(int(part))
            plan = [p for p in plan if p["i"] in want]
    log = open(os.path.join(HERE, tag + ".jsonl"), "w", encoding="utf-8")
    findings = []

    def note(i, kind, detail):
        findings.append((i, kind, detail))
        print("  !! step %s %s: %s" % (i, kind, str(detail)[:400]), flush=True)

    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="monkey-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof, "--no-first-run",
                             "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "--window-size=1400,950",
                             "--force-device-scale-factor=1", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_start = time.time()
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get("type") == "page"]
                if pages: target = pages[0]["webSocketDebuggerUrl"]; break
            except Exception:
                pass
            time.sleep(0.2)
        page = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"): page.call(m)
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        url = a.url or ("file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/"))
        if not url.startswith(("file:", "http")): url = "file:///" + os.path.abspath(url).replace("\\", "/")
        page.call("Page.navigate", url=url)
        page.wait("document.readyState === 'complete'", 30)
        d = Drive(page)
        if not page.wait("window.squaringLab && window.squaringLab.idle()", 240):
            note(0, "never-idle", "the page did not become idle after loading: " + str(d.js("return document.getElementById('status').textContent;")))
        d.js(HELPER)
        rng = LCG(a.seed)
        seen_problems = 0
        n = len(plan) if plan is not None else a.steps

        def checkpoint(i):
            h = d.js("return window.__mk.health();")
            if h["plays"]:
                hidden = [p["id"] for p in h["plays"] if not p["shown"]]
                if hidden: note(i, "play-while-hidden", hidden)
                d.js("document.querySelectorAll('.dial-play[aria-pressed=\"true\"]').forEach(b => b.click());")
            t0 = time.time(); ok = page.wait("window.squaringLab.idle()", a.idle_timeout); tries = 0
            while not ok and tries < 3:
                s1 = d.js("return window.__mk.sig();"); time.sleep(4); s2 = d.js("return window.__mk.sig();")
                if s1 == s2:
                    break
                tries += 1; ok = page.wait("window.squaringLab.idle()", a.idle_timeout)
            waited = time.time() - t0
            if not ok:
                note(i, "never-idle", {"waited": round(waited), "sig": d.js("return window.__mk.sig();"), "state": h["st"], "plays": h["plays"]})
            path = os.path.join(shots, "cp-%03d.png" % i)
            try:
                st = stage_stats(d, path)
            except Exception as err:
                st = {"error": str(err)}
            h2 = d.js("return window.__mk.health();")
            rec = {"checkpoint": i, "idle": ok, "waited": round(waited, 1), "stats": st, "state": h2["st"], "failed": h2["failed"], "status": h2["status"], "plays_stopped": [p["id"] for p in h["plays"]]}
            log.write(json.dumps(rec, ensure_ascii=False) + "\n"); log.flush()
            if st.get("n") and max(st["range"]) <= 6 and not h2["failed"]:
                note(i, "one-colour", {"stats": st, "state": h2["st"], "shot": path})
            print("checkpoint %d: idle=%s after %.1fs, colours=%s modal=%s failed=%r %s" % (i, ok, waited, st.get("colours"), st.get("modal_share"), h2["failed"], json.dumps(h2["st"], ensure_ascii=False)), flush=True)

        for i in range(1, n + 1):
            if plan is not None:
                st = plan[i - 1]["step"]; label = plan[i - 1]["i"]
            else:
                st = choose(rng, d); label = i
            log.write(json.dumps({"i": label, "step": st}, ensure_ascii=False) + "\n"); log.flush()
            try:
                how = apply(d, st)
            except Exception as err:
                how = "DRIVER ERROR " + str(err)[:300]
                note(label, "driver-error", how)
            time.sleep(a.pause)
            try:
                h = d.js("return window.__mk.health();")
            except Exception as err:
                h = None; note(label, "health-failed", str(err)[:300])
                try: d.js(HELPER)
                except Exception: pass
            new = page.problems[seen_problems:]; seen_problems = len(page.problems)
            for p in new: note(label, "console", p[:500])
            if h:
                if h["bad"]: note(label, "non-finite", h["bad"])
                if h["failed"] == "shader": note(label, "shader-failed", h["glfail"])
                if h["boxes"]: note(label, "odd-box-text", h["boxes"])
                log.write(json.dumps({"i": label, "how": how, "failed": h["failed"], "state": h["st"], "status": h["status"], "t": round(time.time() - t_start, 1)}, ensure_ascii=False) + "\n")
            if a.shots:
                try: d.p.shot(os.path.join(shots, "s-%03d.png" % label), "#stage")
                except Exception as err: print("shot failed", err)
            if (plan is None and i % a.every == 0) or (plan is not None and i == n):
                checkpoint(label)
        new = page.problems[seen_problems:]
        for p in new: note("end", "console", p[:500])
        try: page.call("Browser.close")
        except Exception: pass
    finally:
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
        log.close()
    with open(os.path.join(HERE, tag + ".findings.txt"), "w", encoding="utf-8") as f:
        for i, kind, detail in findings:
            f.write("%s\t%s\t%s\n" % (i, kind, json.dumps(detail, ensure_ascii=False) if not isinstance(detail, str) else detail))
    print("DONE %s: %d steps, %d findings, %.0f s" % (tag, n, len(findings), time.time() - t_start))
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
