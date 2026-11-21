"""Random walk over the visible controls of the lab, with checks after every action.

  python out/t6/walk/walk.py --seed 1 --seconds 300 [--size 1400x950] [--theme dark] [--url dist/v6.html]
  python out/t6/walk/walk.py --replay out/t6/walk/run1/actions.jsonl [--upto 57] [--only 3,9,57] [--shot name.png]

Every action is written to run<seed>/actions.jsonl before it is carried out, so a failure can be replayed.
Failures go to run<seed>/failures.jsonl with a screenshot beside them.
"""
import argparse, json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drv import Lab, HERE  # noqa: E402

EQ_OK = ["z^n + c", "z^2 + c", "z^3 + c", "conj(z)^n + c", "abs(z)^n + c", "z^n + c*z", "c*z*(1 - z)", "z^n + 1/c",
         "z^n + c + 0.2*j", "len(z)*z + c", "z*z*z + c*i", "z^n - z + c", "1/z^n + c", "z^n + c/z"]
EQ_BAD = ["", "z^^2", "foo(z)", "z + ", "((z)", "z^n + q", "1/0", "c", "z", "n", ")(", "z^n + c;alert(1)", "z**2+c"]
Z0 = ["0", "c", "1", "i", "0.5*j", "abc", "", "c/2", "-1", "1/0"]
NONSENSE = ["", "abc", "-", ".", "1e9", "-1e9", "1,5", "−2", "  3  ", "1e-9", "NaN", "Infinity", "0x10", "2..5", "--1", "1/2", "+", "9999999999999999999999"]
WORDS = ["spiral", "my point", "x", "a" * 40, "Douady rabbit", "<b>bold</b>", "  ", "test éè", "'quote\"", "1"]
BUTTON_W = {"#resetAll": 0.2, "#collapseAll": 0.4, "#exportStart": 7, "#meshStart": 4, "#qUltra": 3, "#qFast": 3, "#qBal": 3, "#qFine": 2,
            "#reset": 2, "#camFly": 2, "#camArc": 2, "#juliaSave": 3, "#juliaFrame": 2, "#kleinFrame": 2, "#juliaFound": 3, "#juliaDelete": 3}
JOB_WORDS = ("Save the file", "Cancel", "Discard", "Start again", "Stop")
KIND_W = {"button": 30, "range": 16, "text": 12, "select": 15, "checkbox": 10, "radio": 9, "summary": 3, "canvas": 12, "slider": 2}


def fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


def choose(rng, ctrls, chk):
    """Pick one action for the controls that are visible now."""
    by = {}
    for c in ctrls:
        by.setdefault(c["kind"], []).append(c)
    by["canvas"] = [{"sel": "#view", "kind": "canvas", "name": "the picture"}]
    kinds = [k for k in by if k in KIND_W]
    visible = len(ctrls)
    w = [KIND_W[k] * (6 if k == "summary" and visible < 40 else 1) for k in kinds]
    kind = rng.choices(kinds, w)[0]
    pool = by[kind]
    if kind == "button":
        ws = []
        for c in pool:
            x = BUTTON_W.get(c["sel"], 1.0)
            if c["name"] == "Reset this section": x = 0.6
            if any(c["name"].startswith(j) for j in JOB_WORDS): x = 5
            ws.append(x)
        c = rng.choices(pool, ws)[0]
        a = {"op": "click", "sel": c["sel"], "name": c["name"]}
        if rng.random() < 0.12: a["shift"] = True
        if rng.random() < 0.1: a["hold"] = round(rng.uniform(0.5, 1.2), 2)
        if rng.random() < 0.15: a["times"] = rng.randint(2, 5)
        return a
    c = rng.choice(pool)
    a = {"sel": c["sel"], "name": c["name"]}
    if kind in ("checkbox", "radio", "summary"):
        a["op"] = "click"
    elif kind == "select":
        a["op"] = "select"; a["index"] = rng.choice(c["opts"]) if c["opts"] else 0
    elif kind == "range":
        a["op"] = "range"; a["frac"] = round(rng.choice([0, 1, rng.random(), rng.random(), rng.random()]), 3)
        a["how"] = rng.choice(["click", "drag", "keys"])
    elif kind == "text":
        a["op"] = "type"; a["commit"] = rng.choices(["Enter", "Tab", "none"], [60, 25, 15])[0]
        sel = c["sel"]
        if sel == "#eq": a["text"] = rng.choice(EQ_OK if rng.random() < 0.7 else EQ_BAD)
        elif sel == "#z0": a["text"] = rng.choice(Z0)
        elif sel == "#juliaName": a["text"] = rng.choice(WORDS)
        else:
            r = rng.random()
            lo, hi = c.get("min"), c.get("max")
            if lo is None:
                try:
                    cur = float(c.get("value") or 1)
                except ValueError:
                    cur = 1.0
                lo, hi = (cur / 4, cur * 4) if cur > 0 else (cur * 4, 4)
                if sel in ("#camNear",): lo, hi = 0.0005, 6
                if sel in ("#camFar",): lo, hi = 0.5, 1200
            if r < 0.2: a["text"] = rng.choice(NONSENSE)
            elif r < 0.42: a["text"] = fmt(rng.choice([lo - (hi - lo) * rng.uniform(0.1, 3), hi + (hi - lo) * rng.uniform(0.1, 3)]))
            elif r < 0.55: a["text"] = fmt(rng.choice([lo, hi, 0, round(rng.uniform(lo, hi))]))
            else: a["text"] = fmt(rng.uniform(lo, hi))
    elif kind == "canvas":
        op = rng.choice(["wheel", "wheel", "drag", "drag", "dbl", "key", "key"])
        a["op"] = op
        if op == "wheel": a["dy"] = rng.choice([-100, 100, -240, 240]); a["n"] = rng.randint(1, 9)
        if op == "drag": a["dx"] = rng.randint(-300, 300); a["dy"] = rng.randint(-200, 200); a["shift"] = rng.random() < 0.3; a["button"] = rng.choice(["left", "left", "left", "right", "middle"])
        if op == "dbl": a["fx"] = round(rng.uniform(0.1, 0.9), 2); a["fy"] = round(rng.uniform(0.1, 0.9), 2)
        if op == "key": a["keys"] = [rng.choice(["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-", "f", "w", "a", "s", "d", "q", "e", " ", "Escape", "0", "r"]) for _ in range(rng.randint(1, 5))]
    elif kind == "slider":
        a["op"] = "slider"; a["frac"] = round(rng.random(), 3); a["keys"] = [rng.choice(["ArrowUp", "ArrowDown", "PageUp", "PageDown", "ArrowLeft", "ArrowRight"]) for _ in range(rng.randint(0, 3))]
    return a


def perform(lab, a):
    """Carry out one logged action with real input where that is possible. Returns how it went."""
    op, sel = a["op"], a.get("sel")
    q = json.dumps(sel) if sel else None
    if op == "click":
        r = "gone"
        for _ in range(a.get("times", 1)):
            r = lab.click(sel, modifiers=8 if a.get("shift") else 0, hold=a.get("hold", 0.0))
        return r
    if op == "select":
        return lab.js("const e = document.querySelector(%s); if (!e || !__w.vis(e)) return 'gone'; e.focus(); if (!e.options[%d] || e.options[%d].disabled) return 'no option'; "
                      "e.selectedIndex = %d; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); return e.options[%d].text;"
                      % (q, a["index"], a["index"], a["index"], a["index"]))
    if op == "range":
        b = lab.box(sel)
        if not b:
            return "gone"
        y = b[1] + b[3] / 2
        x1 = b[0] + 8 + (b[2] - 16) * a["frac"]
        if a["how"] == "keys":
            lab.js("document.querySelector(%s).focus();" % q)
            for k in (["ArrowRight", "ArrowLeft"][int(a["frac"] * 2) % 2],) * (1 + int(a["frac"] * 6)):
                lab.key(k)
            return "keys"
        if not lab.js("return __w.hit(%s, %f, %f);" % (q, x1, y)):
            lab.js("const e = document.querySelector(%s); e.value = String(+e.min + (%f) * (e.max - e.min)); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true }));" % (q, a["frac"]))
            return "js"
        if a["how"] == "drag":
            x0 = b[0] + b[2] / 2
            lab.mouse("mouseMoved", x0, y); lab.mouse("mousePressed", x0, y, button="left", clickCount=1)
            for i in range(1, 7):
                lab.mouse("mouseMoved", x0 + (x1 - x0) * i / 6, y, button="left", buttons=1); time.sleep(0.03)
            lab.mouse("mouseReleased", x1, y, button="left", clickCount=1)
            return "drag"
        lab.mouse("mouseMoved", x1, y); lab.mouse("mousePressed", x1, y, button="left", clickCount=1); lab.mouse("mouseReleased", x1, y, button="left", clickCount=1)
        return "click"
    if op == "type":
        r = lab.retype(sel, a["text"])
        if r == "gone":
            return r
        if a["commit"] in ("Enter", "Tab"):
            lab.key(a["commit"])
        return r
    if op in ("wheel", "drag", "dbl", "key"):
        b = lab.box("#view")
        if not b:
            return "gone"
        cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
        if op == "wheel":
            lab.mouse("mouseMoved", cx, cy)
            for _ in range(a["n"]):
                lab.mouse("mouseWheel", cx, cy, deltaX=0, deltaY=a["dy"]); time.sleep(0.03)
        elif op == "drag":
            btn = a.get("button", "left"); bits = {"left": 1, "right": 2, "middle": 4}[btn]; mod = 8 if a.get("shift") else 0
            lab.mouse("mouseMoved", cx, cy); lab.mouse("mousePressed", cx, cy, button=btn, clickCount=1, modifiers=mod)
            for i in range(1, 9):
                lab.mouse("mouseMoved", cx + a["dx"] * i / 8, cy + a["dy"] * i / 8, button=btn, buttons=bits, modifiers=mod); time.sleep(0.025)
            lab.mouse("mouseReleased", cx + a["dx"], cy + a["dy"], button=btn, clickCount=1, modifiers=mod)
        elif op == "dbl":
            x, y = b[0] + b[2] * a["fx"], b[1] + b[3] * a["fy"]
            lab.mouse("mouseMoved", x, y)
            for n in (1, 2):
                lab.mouse("mousePressed", x, y, button="left", clickCount=n); lab.mouse("mouseReleased", x, y, button="left", clickCount=n)
        else:
            lab.js("document.getElementById('view').focus({ preventScroll: true });")
            for k in a["keys"]:
                if len(k) == 1 and k.isalpha():
                    lab.key(k, text=k, code="Key" + k.upper(), hold=0.25)
                elif len(k) == 1:
                    lab.key(k, text=k, code={"+": "Equal", "-": "Minus", " ": "Space", "0": "Digit0"}.get(k, k))
                else:
                    lab.key(k, hold=0.1)
        return "real"
    if op == "slider":
        b = lab.box(sel)
        if not b:
            return "gone"
        x, y = b[0] + b[2] / 2, b[1] + 4 + (b[3] - 8) * a["frac"]
        lab.mouse("mouseMoved", x, y); lab.mouse("mousePressed", x, y, button="left", clickCount=1); lab.mouse("mouseReleased", x, y, button="left", clickCount=1)
        for k in a.get("keys", []):
            lab.key(k)
        return "real"
    if op == "js":
        return lab.js(a["code"])
    return "unknown op"


class Run:
    def __init__(self, lab, folder):
        self.lab, self.folder = lab, folder
        os.makedirs(folder, exist_ok=True)
        self.fail_f = open(os.path.join(folder, "failures.jsonl"), "a", encoding="utf-8")
        self.n_fail = {}
        self.last_blank_step = -99

    def fail(self, step, kind, detail, shot=True):
        self.n_fail[kind] = self.n_fail.get(kind, 0) + 1
        rec = {"step": step, "type": kind, "detail": detail}
        if shot and self.n_fail[kind] <= 12:
            try:
                png = self.lab.shot_png()
                name = "f%04d-%s.png" % (step, kind)
                with open(os.path.join(self.folder, name), "wb") as f:
                    f.write(png)
                rec["shot"] = name
            except Exception as e:
                rec["shot_error"] = str(e)
        self.fail_f.write(json.dumps(rec, ensure_ascii=False) + "\n"); self.fail_f.flush()
        print("  !! step %d %s: %s" % (step, kind, json.dumps(detail, ensure_ascii=False)[:400]), flush=True)

    def after(self, step, a, waited_idle):
        """The checks after one action. Returns the check record."""
        lab = self.lab
        for p in lab.problems():
            self.fail(step, "console", p[:700])
        chk = lab.check()
        if chk["bad"]:
            time.sleep(0.4)
            chk2 = lab.check()
            if chk2["bad"]:
                self.fail(step, "bad-number", chk2["bad"][:6])
        if chk["sw"] > chk["iw"] + 1:
            self.fail(step, "sideways-scroll", {"scrollWidth": chk["sw"], "innerWidth": chk["iw"]})
        if chk["idle"] and (chk["busy"] or chk["bar"]):
            time.sleep(1.5)
            c2 = lab.check()
            if c2["idle"] and c2["busy"] and not (c2["exp"] or c2["mesh"]):
                self.fail(step, "busy-stuck", {"label": c2["busy"], "status": c2["status"]})
            if c2["idle"] and c2["bar"]:
                self.fail(step, "bar-stuck", {"bar": c2["barW"], "status": c2["status"]})
            chk = c2
        return chk

    def blank_check(self, step, chk, log):
        lab = self.lab
        st = lab.picture_stats()
        if st is None or st["other"] >= 0.004:
            return st
        expected = [k for k in ("eqErr", "note", "glfail", "kwarn") if chk.get(k)]
        state = lab.js("return __w.state();")
        if expected:
            self.fail(step, "blank-expected", {"why": expected, "stats": st}, shot=False)
            return st
        # is it only the camera? Reset view is itself a logged action.
        a = {"op": "click", "sel": "#reset", "name": "Reset view", "probe": True, "wait": "idle"}
        log(a)
        perform(lab, a)
        lab.wait_idle(120)
        st2 = lab.picture_stats()
        if st2 is not None and st2["other"] < 0.004:
            self.fail(step, "BLANK", {"stats": st, "after_reset_view": st2, "state": state, "check": chk})
        else:
            self.fail(step, "blank-camera", {"stats": st, "cam": state.get("cam"), "flat": chk["flat"], "mode": chk["mode"]}, shot=False)
        return st2


def walk(args):
    w, h = (int(x) for x in args.size.lower().split("x"))
    folder = os.path.join(HERE, "run%s" % args.seed)
    os.makedirs(folder, exist_ok=True)
    rng = random.Random(args.seed)
    lab = Lab(args.url, (w, h), args.theme)
    run = Run(lab, folder)
    logf = open(os.path.join(folder, "actions.jsonl"), "w", encoding="utf-8")
    step = [0]

    def log(a):
        a = dict(a); a["step"] = step[0]; a["t"] = round(time.time() - t0, 1)
        logf.write(json.dumps(a, ensure_ascii=False) + "\n"); logf.flush()

    t0 = time.time()
    first = lab.wait_idle(240)
    print("seed %s: first picture after %s s" % (args.seed, first), flush=True)
    if first is None:
        run.fail(0, "stuck", {"at": "load", "check": lab.check()})
    run.after(0, None, True)
    n_idle_waits = n_slow = 0
    force = None
    while time.time() - t0 < args.seconds:
        step[0] += 1
        s = step[0]
        try:
            ctrls = lab.js("return __w.list();")
            chk0 = lab.check()
            if force:
                a, force = force, None
            elif chk0["playing"] and rng.random() < 0.35:
                sel = lab.js("const d = document.querySelector('.dial.is-playing button[aria-pressed=true]'); return d ? __w.sel(d) : null;")
                a = {"op": "click", "sel": sel, "name": "pause a sweep"} if sel else choose(rng, ctrls, chk0)
            else:
                a = choose(rng, ctrls, chk0)
            r = rng.random()
            a["wait"] = "idle" if r < 0.55 else ("sleep:%.2f" % rng.uniform(0.05, 0.5) if r < 0.8 else "none")
            log(a)
            how = perform(lab, a)
            waited = False
            if a["wait"] == "idle":
                c = lab.check()
                if c["playing"]:
                    time.sleep(1.0)
                else:
                    n_idle_waits += 1
                    t = lab.wait_idle(args.idle)
                    waited = t is not None
                    if t is None:
                        c1 = lab.check(); time.sleep(6); c2 = lab.check()
                        if c2["idle"]:
                            waited = True
                        elif c2["playing"]:
                            pass
                        elif c1["status"] != c2["status"] or c1["barW"] != c2["barW"]:
                            n_slow += 1
                            run.fail(s, "slow", {"status": [c1["status"], c2["status"]], "bar": [c1["barW"], c2["barW"]]}, shot=False)
                        else:
                            run.fail(s, "STUCK", {"check": c2, "state": lab.js("return __w.state();")})
            elif a["wait"].startswith("sleep:"):
                time.sleep(float(a["wait"][6:]))
            chk = run.after(s, a, waited)
            if chk["idle"] and not chk["playing"] and (s % 4 == 0 or a.get("sel", "").startswith("#mode-") or a.get("sel") in ("#flat", "#resetAll", "#fig4Show", "#twinMerc", "#twinLathe", "#twinBulb")):
                run.blank_check(s, chk, log)
            if s % 10 == 0:
                print("seed %s step %d t=%.0fs mode=%s flat=%s idle=%s exp=%s mesh=%s saved=%d last=%s/%s -> %s" % (
                    args.seed, s, time.time() - t0, chk["mode"], chk["flat"], chk["idle"], chk["exp"], chk["mesh"], chk["saved"], a["op"], a.get("name", "")[:30], str(how)[:30]), flush=True)
        except Exception as e:
            run.fail(s, "driver", repr(e)[:500], shot=False)
            if "closed" in repr(e) or "connection" in repr(e).lower():
                break
    # the end: stop sweeps, let everything settle, final checks
    try:
        lab.js("document.querySelectorAll('.dial.is-playing button[aria-pressed=true]').forEach(b => b.click());")
        t = lab.wait_idle(240)
        chk = run.after(step[0] + 1, None, True)
        if t is None:
            run.fail(step[0] + 1, "STUCK", {"at": "end", "check": chk, "state": lab.js("return __w.state();")})
        saved = lab.js("return window.__saved;")
        png = lab.shot_png()
        with open(os.path.join(folder, "end.png"), "wb") as f:
            f.write(png)
        print("seed %s END: %d steps, %.0f s of page time, %d waits for idle, %d slow, files saved: %s" % (args.seed, step[0], time.time() - t0, n_idle_waits, n_slow, json.dumps(saved)[:600]))
        print("seed %s failures by type: %s" % (args.seed, json.dumps(run.n_fail)))
        print("seed %s end check: %s" % (args.seed, json.dumps(chk, ensure_ascii=False)))
    finally:
        lab.close()


def replay(args):
    w, h = (int(x) for x in args.size.lower().split("x"))
    acts = [json.loads(l) for l in open(args.replay, encoding="utf-8") if l.strip()]
    only = set(int(x) for x in args.only.split(",")) if args.only else None
    lab = Lab(args.url, (w, h), args.theme)
    run = Run(lab, os.path.join(HERE, "replay"))
    lab.wait_idle(240)
    try:
        for a in acts:
            s = a["step"]
            if args.upto and s > args.upto: break
            if only is not None and s not in only: continue
            how = perform(lab, a)
            if a.get("wait") == "idle" or args.settle:
                if not lab.check()["playing"]:
                    t = lab.wait_idle(args.idle)
                    if t is None: print("  step %d: not idle after %s s" % (s, args.idle))
                else: time.sleep(1.0)
            elif str(a.get("wait", "")).startswith("sleep:"):
                time.sleep(float(a["wait"][6:]))
            chk = run.after(s, a, True)
            print("step %d %s %s %s -> %s | idle=%s busy=%s bar=%s status=%r bad=%s" % (s, a["op"], a.get("sel", ""), {k: v for k, v in a.items() if k in ("text", "index", "frac", "keys", "dy", "dx", "n", "commit", "times", "shift", "hold")}, str(how)[:40], chk["idle"], chk["busy"], chk["bar"], chk["status"], chk["bad"]), flush=True)
        if args.final_js:
            print("final js:", json.dumps(lab.js(args.final_js), ensure_ascii=False)[:3000])
        time.sleep(args.linger)
        chk = lab.check()
        print("final check:", json.dumps(chk, ensure_ascii=False))
        print("picture:", lab.picture_stats())
        if args.shot:
            with open(os.path.join(HERE, args.shot), "wb") as f:
                f.write(lab.shot_png())
        print("problems:", lab.problems())
    finally:
        lab.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="1"); ap.add_argument("--seconds", type=float, default=300)
    ap.add_argument("--size", default="1400x950"); ap.add_argument("--theme", default="dark"); ap.add_argument("--url", default="dist/v6.html")
    ap.add_argument("--idle", type=float, default=120)
    ap.add_argument("--replay"); ap.add_argument("--upto", type=int); ap.add_argument("--only"); ap.add_argument("--shot")
    ap.add_argument("--settle", action="store_true"); ap.add_argument("--final-js", dest="final_js"); ap.add_argument("--linger", type=float, default=0.5)
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    (replay if args.replay else walk)(args)
