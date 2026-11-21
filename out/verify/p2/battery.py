"""p2: run every dial of dist/preview.html through the same battery with real keyboard and mouse input.
  python out/verify/p2/battery.py TAG id1,id2,...     -> out/verify/p2/res-TAG.json
"""
import json, math, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

KEYS = {"Tab": 9, "Enter": 13, "Escape": 27, "PageUp": 33, "PageDown": 34, "ArrowLeft": 37, "ArrowUp": 38,
        "ArrowRight": 39, "ArrowDown": 40, "Backspace": 8, "Delete": 46}
SHIFT = 8
L = "window.squaringLab"

# id -> (state expression, prep JS)
MODE = lambda m: "document.getElementById('mode-%s').click();" % m
AP = lambda a: MODE('m') + "document.getElementById('ap-%s').click();" % a
COL = lambda mode, trap: MODE('m') + "S.colour.mode=%d; S.colour.trap=%d; L.syncControls();" % (mode, trap)
D = {
    "m-mosaicCell": ("S.mosaicCell", MODE('m') + "S.mosaic=true; L.syncControls();"),
    "cx": ("S.c[0]", MODE('j')), "cy": ("S.c[1]", MODE('j')), "cz": ("S.c[2]", MODE('j')),
    "kmy": ("S.k.my", MODE('k')), "kmx": ("S.k.mx", MODE('k')), "kmz": ("S.k.mz", MODE('k')), "kL": ("S.k.L", MODE('k')),
    "kiter": ("S.k.iter", MODE('k')), "kinvr": ("S.k.invR", MODE('k')), "kcx": ("S.k.cx", MODE('k')),
    "kcy": ("S.k.cy", MODE('k')), "kcz": ("S.k.cz", MODE('k')),
    "par-mercator-planes": ("S.param.mercator.planes", AP('mercator')),
    "par-mercator-turn": ("S.param.mercator.turn", AP('mercator') + "S.param.mercator.planes=1; L.syncControls();"),
    "par-mercator-lift": ("S.param.mercator.lift", AP('mercator')),
    "par-lathe-spin": ("S.param.lathe.spin", AP('lathe')),
    "par-bulb-lat": ("S.param.bulb.lat", AP('bulb')), "par-bulb-lon": ("S.param.bulb.lon", AP('bulb')),
    "par-classic-theta": ("S.param.classic.theta", AP('classic')), "par-classic-phi": ("S.param.classic.phi", AP('classic')),
    "pow": ("S.n", MODE('m')), "iter": ("S.iter", MODE('m')), "cut": ("S.cut", MODE('m')),
    "col-radius": ("S.colour.radius", COL(0, 5)), "col-tx": ("S.colour.tx", COL(0, 0)), "col-ty": ("S.colour.ty", COL(0, 0)),
    "col-tz": ("S.colour.tz", COL(0, 0)), "col-bands": ("S.colour.bands", COL(0, 0)), "col-shift": ("S.colour.shift", COL(0, 0)),
    "lightAz": ("S.lightAz", MODE('m')), "lightEl": ("S.lightEl", MODE('m')),
    "viewSpeed": ("S.view.speed", MODE('m')), "viewBound": ("S.view.bound", MODE('m')),
    "viewFov": ("+(2*Math.atan(S.view.fov)*180/Math.PI).toFixed(2)", MODE('m')),
    "qres": ("S.q.res", MODE('m')), "qaa": ("S.q.aa", MODE('m')), "qsteps": ("S.q.steps", MODE('m')),
    "qdetail": ("S.q.detail", MODE('m')), "qstepk": ("S.q.stepk", MODE('m')), "qsmooth": ("S.q.smooth", MODE('m')),
}


def fmt(v):
    if v is None:
        return ""
    t = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def decs(x):
    for d in range(11):
        if abs(round(x, d) - x) <= 1e-12 * max(1, abs(x)):
            return d
    return 10


def jsround(v):
    return math.floor(v + 0.5)


class T:
    def __init__(self, page):
        self.p = page

    def js(self, code):
        return self.p.js("const L=%s, S=L.S; %s" % (L, code))

    def rect(self, sel, scroll=False):
        return self.js("const e=document.querySelector(%s); if(!e) return null; %s const b=e.getBoundingClientRect(); return [b.left,b.top,b.width,b.height];"
                       % (json.dumps(sel), "e.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,120));" if scroll else ""))

    def xy(self, sel, fx=0.5, fy=0.5):
        b = self.rect(sel)
        if b[1] < 60 or b[1] + b[3] > 890:
            b = self.rect(sel, True)
        return b[0] + b[2] * fx, b[1] + b[3] * fy

    def mouse(self, kind, x, y, **kw):
        self.p.call("Input.dispatchMouseEvent", type=kind, x=x, y=y, **kw)

    def click(self, sel, count=1, modifiers=0, hold=0.0, fx=0.5):
        x, y = self.xy(sel, fx)
        self.mouse("mouseMoved", x, y)
        for c in range(1, count + 1):
            self.mouse("mousePressed", x, y, button="left", clickCount=c, modifiers=modifiers)
            if hold:
                time.sleep(hold)
            self.mouse("mouseReleased", x, y, button="left", clickCount=c, modifiers=modifiers)

    def key(self, name, modifiers=0, repeat=0):
        kw = dict(key=name, code=name, windowsVirtualKeyCode=KEYS[name], modifiers=modifiers)
        self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw)
        for _ in range(repeat):
            self.p.call("Input.dispatchKeyEvent", type="rawKeyDown", autoRepeat=True, **kw)
        self.p.call("Input.dispatchKeyEvent", type="keyUp", **kw)

    def chars(self, s):
        for ch in s:
            self.p.call("Input.dispatchKeyEvent", type="keyDown", text=ch, key=ch, unmodifiedText=ch)
            self.p.call("Input.dispatchKeyEvent", type="keyUp", key=ch)

    def retype(self, sel, s):
        self.click(sel, count=3)
        if s == "":
            self.key("Backspace")
        else:
            self.chars(s)


def run_dial(t, did, res):
    expr, prep = D[did]
    num, rng = "#" + did.replace(".", "\\.") + "Num", "#" + did
    t.js("document.querySelectorAll('details.sec').forEach(s=>{s.open=true;});" + prep)
    time.sleep(0.25)
    info = t.js("const n=document.querySelector(%s), d=n.closest('.dial'), r=d.querySelector('input[type=range]'), m=d.querySelector('.dial-mode');"
                "return {vis:d.checkVisibility(), min:+r.min, max:+r.max, step:+r.step, title:n.title, lo:+n.getAttribute('aria-valuemin'), hi:+n.getAttribute('aria-valuemax'),"
                "toggle: m?m.textContent:null, play: !!d.querySelector('.dial-play'), label:d.querySelector('label').textContent, im:n.inputMode};" % json.dumps(num))
    mn, mx, step, lo, hi = info["min"], info["max"], info["step"], info["lo"], info["hi"]
    odd = info["title"].startswith("Odd"); integer = odd or info["title"].startswith("Whole")
    tol = 0.011 if did == "viewFov" else 1e-9
    out = {"info": info, "int": integer, "odd": odd, "tests": {}, "notes": []}
    res[did] = out
    if not info["vis"]:
        out["notes"].append("NOT VISIBLE after prep")
        return
    t.rect(num, True)

    def fix(v):
        if odd: v = 2 * jsround((v - 1) / 2) + 1
        elif integer: v = jsround(v)
        return min(max(v, lo), hi) + 0.0

    def snap():
        return t.js("const n=document.querySelector(%s), d=n.closest('.dial'), r=d.querySelector('input[type=range]'), m=d.querySelector('.dial-mode'); const a=document.activeElement;"
                    "return {s:%s, box:n.value, r:+r.value, out:d.classList.contains('is-out'), at:d.dataset.at, inv:n.getAttribute('aria-invalid'), flag:n.parentElement.dataset.flag||'',"
                    "mode:m?m.textContent:null, pressed:m?m.getAttribute('aria-pressed'):null, act:a?(a.id||a.tagName):''};" % (json.dumps(num), expr))

    def agree(z, what):
        bad = []
        s = z["s"]
        if not isinstance(s, (int, float)):
            bad.append("state not a number: %r" % (s,))
        else:
            if z["box"] != fmt(s): bad.append("box %r vs state %r" % (z["box"], s))
            if abs(z["r"] - min(max(s, mn), mx)) > step / 2 + 1e-9: bad.append("slider %r vs state %r" % (z["r"], s))
            if z["out"] != (s < mn - 1e-12 or s > mx + 1e-12): bad.append("is-out %r at state %r" % (z["out"], s))
            if s < lo - 1e-12 or s > hi + 1e-12: bad.append("state %r outside typed limits" % s)
            if integer and s != round(s): bad.append("fraction %r in a whole-number dial" % s)
            if odd and int(round(s)) % 2 == 0: bad.append("even %r in the odd dial" % s)
            if did != "viewFov" and abs(s - round(s, 10)) > 0 and len(repr(s)) > 14: bad.append("float dirt %r" % s)
        if bad:
            out["notes"].append("%s: %s" % (what, "; ".join(bad)))
        return not bad

    def rec(name, ok, detail=""):
        out["tests"][name] = "pass" if ok else "FAIL " + str(detail)

    def typed(name, text, expect, end="Enter", want_inv=None, want_flag=None):
        """type text, commit, compare with the expected value (None = unchanged, refused)."""
        before = snap()
        t.retype(num, text)
        mid = snap()
        t.key(end)
        z = snap()
        exp = before["s"] if expect is None else expect
        ok = isinstance(z["s"], (int, float)) and abs(z["s"] - exp) <= tol and agree(z, name)
        if mid["s"] != before["s"]: ok = False
        if want_inv is not None and (z["inv"] == "true") != want_inv: ok = False
        if want_flag is not None and z["flag"] != want_flag: ok = False
        rec(name, ok, "typed %r (%s): state %r -> %r, expected %r, box %r, slider %r, invalid %r, flag %r, state before commit %r"
            % (text, end, before["s"], z["s"], exp, z["box"], z["r"], z["inv"], z["flag"], mid["s"]))
        if z["inv"] or z["flag"]:
            time.sleep(0.0)
        return z

    def setv(v):
        t.retype(num, fmt(v)); t.key("Enter")
        z = snap()
        return z["s"]

    up, down = "%s ~ .dial-steps .dial-up" % num, "%s ~ .dial-steps .dial-down" % num
    span = mx - mn
    # values
    w = math.ceil(mn + span * 0.6); w = w if w <= mx else math.floor(mx)
    dv = round(mn + span * 0.37, 3)
    f = math.floor(mn + span / 2) + 0.37
    if f > mx: f -= 1
    if f < mn: f += 1
    f = round(f, 2)

    # --- typing
    setv(fix(mn + span * 0.2))
    typed("whole", fmt(w), fix(w), want_inv=False)
    typed("decimal", fmt(dv), fix(dv), want_inv=False)
    typed("negative", "-1.5", fix(-1.5), want_inv=False, want_flag=("clamped" if (-1.5 < lo) else ""))
    typed("unicode minus", "−0.25", fix(-0.25), want_inv=False)
    setv(fix(mn + span * 0.2))
    typed("comma", "1,5", fix(1.5), want_inv=False)
    typed("scientific", "12.5e-1", fix(1.25), want_inv=False)
    setv(fix(w))
    typed("empty", "", None, want_inv=True)
    typed("letters", "abc", None, want_inv=True)
    typed("lone minus", "-", None, want_inv=True)
    typed("lone dot", ".", None, want_inv=True)
    time.sleep(1.5)
    z = snap()
    rec("invalid flag clears", z["inv"] is None and z["flag"] == "", z)
    if hi > mx:
        v = (mx + hi) / 2; v = fix(v) if integer else round(v, 2)
        z = typed("beyond slider, high", fmt(v), v, want_inv=False, want_flag="")
        if not (z["out"] and abs(z["r"] - mx) < 1e-9): rec("beyond slider, high", False, "thumb/hollow: %r" % z)
    else:
        out["tests"]["beyond slider, high"] = "n/a"
    if lo < mn:
        v = (mn + lo) / 2; v = fix(v) if integer else round(v, 3)
        z = typed("beyond slider, low", fmt(v), v, want_inv=False, want_flag="")
        if not (z["out"] and abs(z["r"] - mn) < 1e-9): rec("beyond slider, low", False, "thumb/hollow: %r" % z)
    else:
        out["tests"]["beyond slider, low"] = "n/a"
    typed("beyond limits, high", fmt(hi + 100), hi, want_inv=False, want_flag="clamped")
    typed("beyond limits, low", fmt(lo - 100), lo, want_inv=False, want_flag="clamped")
    # Tab commits and moves on; Escape restores
    setv(fix(w))
    z = typed("Tab commits", fmt(dv), fix(dv), end="Tab")
    if z["act"] != did: rec("Tab commits", False, "focus went to %r, expected the slider %r" % (z["act"], did))
    setv(fix(w))
    before = snap()
    t.retype(num, fmt(dv)); t.key("Escape"); mid = snap(); t.key("Tab"); z = snap()
    rec("Escape restores", z["s"] == before["s"] and mid["box"] == before["box"] and agree(z, "Escape"), (before, mid, z))

    # --- stepping, fine
    if info["toggle"] is not None and snap()["pressed"] == "true":
        t.click("#" + did + "Step")
    sd = max(decs(step), 2)

    def stepseq(name, start, actions, expect_fn, shiftmods=None):
        s0 = setv(start)
        got, exp, ok = [], [], True
        cur = s0
        for a in actions:
            if a == "U": t.click(up)
            elif a == "D": t.click(down)
            elif a == "u": t.key("ArrowUp")
            elif a == "d": t.key("ArrowDown")
            elif a == "SU": t.key("ArrowUp", SHIFT)
            elif a == "PD": t.key("PageDown")
            elif a == "sU": t.click(up, modifiers=SHIFT)
            z = snap()
            cur = expect_fn(cur, a)
            got.append(z["s"]); exp.append(cur)
            if not (isinstance(z["s"], (int, float)) and abs(z["s"] - cur) <= tol and agree(z, name + " " + a)): ok = False
        rec(name, ok, "from %r, actions %s: got %r, expected %r" % (s0, actions, got, exp))

    def fine(cur, a):
        n = {"U": 1, "u": 1, "D": -1, "d": -1, "SU": 10, "PD": -10, "sU": 10}[a]
        if odd:
            b = round(cur, 10)
            v = (2 * math.floor((b + 1) / 2) + 1 if n > 0 else 2 * math.ceil((b - 1) / 2) - 1) + 2 * (1 if n > 0 else -1) * (abs(n) - 1)
            return fix(v)
        return fix(round(cur + n * step, max(decs(cur), decs(step))))

    def whole(cur, a):
        n = {"U": 1, "u": 1, "D": -1, "d": -1, "SU": 10, "PD": -10, "sU": 10}[a]
        b = round(cur, 10)
        return fix((math.floor(b) + 1 if n > 0 else math.ceil(b) - 1) + (1 if n > 0 else -1) * (abs(n) - 1))

    stepseq("fine: buttons+keys from fraction", f, ["U", "D", "D", "u", "d", "u"], fine)
    stepseq("fine: from whole", math.floor(f), ["U", "u", "d", "D", "D"], fine)
    stepseq("fine: ten steps (Shift/Page)", math.floor(f) if not odd else 1, ["SU", "PD", "sU"], fine)
    # floating point dirt: ten single steps
    base = fix(math.floor(f))
    setv(base)
    for _ in range(10): t.click(up)
    z = snap()
    exp = fix(round(base + 10 * (2 if odd else step), 10))
    rec("fine: ten clicks, no float dirt", abs(z["s"] - exp) <= tol and z["box"] == fmt(exp) and agree(z, "ten clicks"),
        "from %r ten up-clicks: state %r box %r, expected %r" % (base, z["s"], z["box"], exp))
    # ends of the range
    setv(hi); t.click(up); t.key("ArrowUp"); z1 = snap()
    setv(lo); t.click(down); t.key("ArrowDown"); z2 = snap()
    rec("ends hold", z1["s"] == hi and z2["s"] == lo and z1["at"] == "hi" and z2["at"] == "lo" and agree(z1, "top end") and agree(z2, "bottom end"), (z1, z2))
    # held button and held key
    s0 = setv(fix(mn + span * 0.3))
    t.click(up, hold=1.3); a = snap(); time.sleep(0.35); b = snap()
    n_steps = (a["s"] - s0) / (2 if odd else step)
    rec("held button repeats and stops", n_steps >= 3 and a["s"] == b["s"] and abs(n_steps - round(n_steps)) < 1e-6 and agree(b, "held button"),
        "from %r held 1.3 s: %r (%.2f steps), 0.35 s later %r" % (s0, a["s"], n_steps, b["s"]))
    s0 = setv(fix(mn + span * 0.3))
    t.key("ArrowDown", repeat=4); z = snap()
    exp = s0
    for _ in range(5): exp = fine(exp, "d")
    rec("held key repeats", abs(z["s"] - exp) <= tol and agree(z, "held key"), "from %r, 5 key repeats: %r expected %r" % (s0, z["s"], exp))

    # --- stepping, whole
    if info["toggle"] is not None:
        t.click("#" + did + "Step"); z = snap()
        okt = z["pressed"] == "true" and z["mode"] == "±1"
        stepseq("whole: from fraction up", f, ["U", "U", "u"], whole)
        stepseq("whole: from fraction down", f, ["D", "d", "D"], whole)
        stepseq("whole: from whole", math.floor(f), ["u", "U", "d", "D", "D"], whole)
        if lo <= -1:
            stepseq("whole: negative fraction", -0.37, ["U", "D", "D", "u"], whole)
        else:
            out["tests"]["whole: negative fraction"] = "n/a"
        stepseq("whole: ten steps", math.floor(f), ["SU", "PD"], whole)
        setv(hi); t.click(up); z1 = snap(); setv(lo); t.click(down); z2 = snap()
        rec("whole: ends hold", z1["s"] == hi and z2["s"] == lo, (z1["s"], z2["s"]))
        # just inside a fractional end
        setv(lo); t.click(up); z3 = snap()
        out["notes"].append("whole mode, up from the lower limit %r gives %r" % (lo, z3["s"]))
        t.click("#" + did + "Step"); z = snap()
        okt = okt and z["pressed"] == "false" and z["mode"] == "±" + fmt(step)
        rec("toggle label and state", okt, z)
        stepseq("fine again after toggling back", f, ["U"], fine)
    else:
        for k in ("whole: from fraction up", "whole: from fraction down", "whole: from whole", "whole: negative fraction", "whole: ten steps", "whole: ends hold", "toggle label and state", "fine again after toggling back"):
            out["tests"][k] = "no toggle"
    # --- slider: a real click in the middle, then ArrowRight
    x, y = t.xy(rng, 0.5)
    t.mouse("mouseMoved", x, y); t.mouse("mousePressed", x, y, button="left", clickCount=1); t.mouse("mouseReleased", x, y, button="left", clickCount=1)
    z = snap()
    mid = mn + span / 2
    okk = abs(z["s"] - mid) <= max(span * 0.06, step * (2 if odd else 1)) and agree(z, "slider click")
    t.key("ArrowRight"); z2 = snap()
    okk = okk and abs(z2["s"] - z["s"] - step) <= tol and agree(z2, "slider ArrowRight")
    rec("slider click and arrow key", okk, "click mid: %r (mid %r), then ArrowRight: %r" % (z["s"], mid, z2["s"]))
    # leave the dial at a tidy value
    setv(fix(w))
    out["final"] = snap()["s"]


def main():
    tag, ids = sys.argv[1], sys.argv[2].split(",")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p2-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = {}
    try:
        target = None
        for _ in range(150):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [x for x in json.load(r) if x.get("type") == "page"]
                if pages:
                    target = pages[0]["webSocketDebuggerUrl"]; break
            except Exception:
                pass
            time.sleep(0.2)
        page = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            page.call(m)
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        page.call("Page.navigate", url="file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/"))
        page.wait("document.readyState === 'complete'", 60)
        page.wait(L + " && " + L + ".S", 120)
        time.sleep(1.0)
        t = T(page)
        # keep the picture cheap while the dials are exercised (set from code, then shown)
        t.js("S.q.res=0.25; S.q.aa=1; S.q.steps=60; S.q.shadow=false; S.q.ao=false; L.syncControls(); L.touch();")
        for did in ids:
            t0 = time.time()
            try:
                run_dial(t, did, res)
            except Exception as e:
                res.setdefault(did, {"tests": {}, "notes": []})["notes"].append("SCRIPT ERROR: %r" % (e,))
            fails = [k for k, v in res[did].get("tests", {}).items() if v.startswith("FAIL")]
            print("%-22s %4.0fs  %d tests, %d fail %s" % (did, time.time() - t0, len(res[did].get("tests", {})), len(fails), fails), flush=True)
        page.js("return 0;")
        res["_problems"] = page.problems[:40]
        print("problems:", page.problems[:10])
        try:
            page.call("Browser.close")
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
        with open(os.path.join(HERE, "res-%s.json" % tag), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
