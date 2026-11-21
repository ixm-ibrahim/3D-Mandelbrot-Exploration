"""Part C: speed. Per quality preset and scene: pictures per second in a 2 s simulated drag, and time to the finished picture."""
import json, os, sys, time
from lib import *

CLICK = "document.getElementById('%s').click();"
SCENES = [
    ("default Mandelbrot", "", False),
    ("classic Mandelbulb n=8", "const L = window.squaringLab; L.S.approach = L.APPROACHES.findIndex(a => a.id === 'classic'); L.S.n = 8; L.syncControls(); L.refresh(); L.resetCam(); L.touch();", False),
    ("lambda equation", "const s = document.getElementById('eqPreset'); s.value = '1'; s.dispatchEvent(new Event('change', { bubbles: true }));", False),
    ("Julia preset (Douady rabbit)", CLICK % "mode-j" + " [...document.querySelectorAll('#juliaList .plist-item')].find(b => b.textContent === 'Douady rabbit').click();", False),
    ("default Kleinian", CLICK % "mode-k", False),
    ("2D view of the default", CLICK % "flat", True),
    ("Julia mosaic", CLICK % "m-mosaic", False),
]
PRESETS = [("qUltra", "Ultra fast", 4000), ("qFast", "Fast", 9000), ("qBal", "Balanced", 6000), ("qFine", "Fine", 6000)]
only = sys.argv[1:] and [int(x) for x in sys.argv[1].split(",")]
out = {}
for si, (scene, setup, flat) in enumerate(SCENES):
    if only and si not in only:
        continue
    d, proc, prof = launch()
    try:
        d.load()
        d.js("window.squaringLab.R.warmOn = false; " + CLICK % "qUltra")
        if setup:
            d.js(setup)
        d.p.wait(L + ".renderIdle()", 30)
        time.sleep(0.3)
        d.js(CLICK % "qBal")
        time.sleep(1.0)
        d.shot("C-scene-%d.png" % si, "#stage")
        for pid, pname, cap in PRESETS:
            d.js(CLICK % pid)
            time.sleep(0.6)
            reps = []
            for rep in range(3):
                r = d.js("return await window.__perf.drag(2000, %d, %s);" % (cap if (rep == 0 or pid in ("qUltra", "qFast")) else 2500, "true" if flat else "false"))
                reps.append(r)
            # one small move from rest, for the two quick presets
            single = None
            if pid in ("qUltra", "qFast"):
                d.p.wait(L + ".renderIdle()", 15)
                single = []
                for rep in range(3):
                    single.append(d.js("const L = window.squaringLab, t0 = performance.now(); if (L.S.flat) L.S.v2.x += L.S.v2.h * 0.01; else L.cam.yaw += 0.02; L.touch();"
                                       "return await new Promise(res => { const f = () => { if (L.renderIdle()) res(performance.now() - t0); else if (performance.now() - t0 > 12000) res(null); else window.__perf.oraf(f); }; window.__perf.oraf(f); });"))
                    time.sleep(0.15)
            out[scene + " | " + pname] = {"reps": reps, "single": single}
            g = lambda k: med([x[k] for x in reps if x[k] is not None])
            print("%-30s %-10s pics/s %5.1f  picGap avg %5.1f max %5.1f | raf avg %5.1f max %5.1f | js avg %4.2f max %4.1f | prev %dx%d of %dx%d ps %.2f gpu %.1f ms%s | bar %s firstAcc %s pass1 %s final %s (all %s) cap-frac %s total %s single %s" % (
                scene, pname, g("picPerSec"), g("picGapAvg") or 0, g("picGapMax") or 0, g("rafAvg"), g("rafMax"), g("jsAvg"), g("jsMax"),
                reps[-1]["pw"], reps[-1]["ph"], reps[-1]["cw"], reps[-1]["ch"], reps[-1]["ps"], g("prevMs"), "" if reps[-1]["exact"] else "(clock)",
                g("barAt") and round(g("barAt")), g("firstAcc") and round(g("firstAcc")), g("pass1") and round(g("pass1")), g("final") and round(g("final")),
                [x["final"] and round(x["final"]) for x in reps], [(x["fracAtCap"], x.get("capAt") and round(x["capAt"])) for x in reps if x["fracAtCap"] is not None], reps[-1]["total"],
                single and [s and round(s) for s in single]), flush=True)
        if d.p.problems:
            print("PAGE PROBLEMS", d.p.problems[:10], flush=True)
    finally:
        close(d, proc, prof)
name = "partC.json" if not only else "partC-%s.json" % "-".join(str(x) for x in only)
with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
