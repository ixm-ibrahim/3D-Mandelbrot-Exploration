"""Part A: freezes. For each action, six seconds of frame gaps, timer gaps, indicator coverage, time to final."""
import json, os, sys, time
from lib import *

GET = ("const m = window.__m; return m.done ? { maxRaf: m.maxRaf, maxRafAt: m.maxRafAt, maxTick: m.maxTick, maxTickAt: m.maxTickAt, s: m.s, "
       "compiles0: m.compiles0, compiles1: m.compiles1, labels: m.labels, status: m.status, sync: m.sync || 0, n: window.squaringLab.S.n } : null;")


def analyse(m):
    s = m["s"]
    final = 0   # the last moment the page went from not-final to final
    for i, r in enumerate(s):
        if not r[3]:
            final = s[i + 1][0] if i + 1 < len(s) else None
    bare = 0; run = 0; bare_at = 0   # longest stretch not final with neither indicator on screen
    for a, b in zip(s, s[1:]):
        if not a[3] and not a[1] and not a[2]:
            run += b[0] - a[0]
            if run > bare: bare, bare_at = run, b[0]
        else:
            run = 0
    busy_ms = sum(b[0] - a[0] for a, b in zip(s, s[1:]) if a[1])
    bar_ms = sum(b[0] - a[0] for a, b in zip(s, s[1:]) if a[2])
    return {"maxRaf": round(m["maxRaf"]), "maxRafAt": round(m["maxRafAt"]), "maxTick": round(m["maxTick"]), "maxTickAt": round(m["maxTickAt"]),
            "final": final, "bare": bare, "bareAt": bare_at, "busyMs": busy_ms, "barMs": bar_ms,
            "compiles": m["compiles1"] - m["compiles0"], "labels": list(m["labels"].keys()), "status": m["status"], "sync": round(m["sync"], 1), "n": m["n"]}


def collect(d, ms):
    time.sleep(ms / 1000 + 0.25)
    for _ in range(60):
        m = d.js(GET)
        if m:
            return analyse(m)
        time.sleep(0.1)
    raise RuntimeError("monitor never finished")


def run_js(d, js, ms=6000):
    d.js("const m = window.__perf.start(%d); %s; m.snap(); m.sync = performance.now() - m.t0;" % (ms, js))
    return collect(d, ms)


def type_power(d, text, ms=6000):
    d.click("#powNum", count=3)
    d.p.call("Input.insertText", text=text)
    d.js("window.__perf.start(%d);" % ms)
    d.key("Enter", "Enter", 13)
    return collect(d, ms)


SEL = "const s = document.getElementById('%s'); s.value = '%s'; s.dispatchEvent(new Event('change', { bubbles: true }))"
CLICK = "document.getElementById('%s').click()"


def one_rep(rep, out):
    d, proc, prof = launch()
    try:
        d.load()

        def rec(name, a):
            out.setdefault(name, []).append(a)
            print(rep, name, json.dumps(a), flush=True)
        rec("eq preset: lambda", run_js(d, SEL % ("eqPreset", "1")))
        run_js(d, SEL % ("eqPreset", "0"), 1500)
        for ap in ("lathe", "bulb", "classic", "split", "mercator"):
            rec("approach: " + ap, run_js(d, CLICK % ("ap-" + ap)))
        rec("mode: Julia", run_js(d, CLICK % "mode-j"))
        rec("mode: Kleinian", run_js(d, CLICK % "mode-k"))
        rec("mode: back to Mandelbrot", run_js(d, CLICK % "mode-m"))
        for t in ("3", "2.5", "-2"):
            rec("power typed: " + t, type_power(d, t))
        type_power(d, "2", 1500)
        rec("tick 2D view", run_js(d, CLICK % "flat"))
        run_js(d, CLICK % "flat", 1500)
        rec("tick Julia mosaic", run_js(d, CLICK % "m-mosaic"))
        run_js(d, CLICK % "m-mosaic", 1500)
        rec("colour trap: another shape", run_js(d, "const s = document.getElementById('col-trap'); s.selectedIndex = (s.selectedIndex + 1) % s.options.length; s.dispatchEvent(new Event('change', { bubbles: true }))"))
        for q in ("qUltra", "qFast", "qBal", "qFine"):
            rec("quality: " + q, run_js(d, CLICK % q))
        if d.p.problems:
            print("PAGE PROBLEMS", d.p.problems[:10], flush=True)
            out.setdefault("_problems", []).extend(d.p.problems[:10])
    finally:
        close(d, proc, prof)


out = {}
for rep in range(3):
    one_rep(rep, out)
with open(os.path.join(HERE, "partA.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("\n%-30s %8s %8s %8s %8s %8s %8s  labels" % ("action (median of 3)", "maxRaf", "maxTick", "final", "bare", "busyMs", "barMs"))
for k, v in out.items():
    if k.startswith("_"):
        continue
    g = lambda key: med([x[key] if x[key] is not None else 99999 for x in v])
    print("%-30s %8s %8s %8s %8s %8s %8s  %s  all maxRaf=%s maxTick=%s final=%s bare=%s compiles=%s" % (k, g("maxRaf"), g("maxTick"), g("final"), g("bare"), g("busyMs"), g("barMs"),
          sorted(set(sum([x["labels"] for x in v], []))), [x["maxRaf"] for x in v], [x["maxTick"] for x in v], [x["final"] for x in v], [x["bare"] for x in v], [x["compiles"] for x in v]))
