"""Where the time goes: the band schedule of the full-quality drawing, and the settle after a move, job by job."""
import json, os, sys, time
from lib import *

HOOK = r"""
const gl = document.getElementById('view').getContext('webgl2'), G = window.__g = { jobs: [], gpu: [], on: false };
const of = gl.fenceSync.bind(gl), oq = gl.getQueryParameter.bind(gl);
gl.fenceSync = (...a) => { if (G.on) G.jobs.push([performance.now(), window.squaringLab.R.rows, document.getElementById('status').textContent.slice(0, 9)]); return of(...a); };
gl.getQueryParameter = (q, p) => { const v = oq(q, p); if (G.on && p === gl.QUERY_RESULT) G.gpu.push(v / 1e6); return v; };
window.__run = (ms, pre) => new Promise(res => { const L = window.squaringLab, R = L.R, P = window.__perf; G.jobs = []; G.gpu = []; G.on = true; P.blits = []; P.on = true;
  if (pre) pre(); const t0 = performance.now(); L.cam.yaw += 0.02; L.touch(); let fin = null, bar = null;
  const f = () => { const now = performance.now(); if (bar === null && P.frac() >= 0) bar = now - t0; if (fin === null && L.renderIdle()) fin = now - t0;
    if (now - t0 < ms && fin === null) return P.oraf(f);
    G.on = false; P.on = false;
    const jobs = G.jobs.map(j => [Math.round((j[0] - t0) * 10) / 10, Math.round(j[1]), j[2]]);
    res({ final: fin, barAt: bar, frac: P.frac(), status: document.getElementById('status').textContent, jobs, gpu: G.gpu.map(x => Math.round(x * 100) / 100),
      blits: P.blits.map(b => [Math.round((b[0] - t0) * 10) / 10, b[1]]), dt: R.dt, cw: gl.canvas.width, ch: gl.canvas.height, pw: R.pw, ph: R.ph, total: R.total, exact: R.rowExact, elapsed: performance.now() - t0 }); };
  P.oraf(f); });
"""


def summarise(name, r):
    bands = [j for j in r["jobs"] if not j[2].startswith("Preview")]
    gaps = [b[0] - a[0] for a, b in zip(bands, bands[1:])]
    span = (bands[-1][0] - bands[0][0]) if len(bands) > 1 else 0
    gpu = r["gpu"]
    print("%s: final %s bar at %s frac %s status %r | %d jobs (%d bands) over %.0f ms, band start gap median %.1f ms | rows min %s median %s max %s | gpu samples %d sum %.0f ms median %.2f ms => GPU busy %.0f%% of the band phase | canvas %dx%d total passes %s" % (
        name, r["final"] and round(r["final"]), r["barAt"] and round(r["barAt"]), r["frac"], r["status"], len(r["jobs"]), len(bands), span, med(gaps) or 0,
        min([b[1] for b in bands] or [0]), med([b[1] for b in bands]), max([b[1] for b in bands] or [0]), len(gpu), sum(gpu), med(gpu) or 0, 100 * sum(gpu[1:]) / span if span else 0, r["cw"], r["ch"], r["total"]), flush=True)


d, proc, prof = launch()
out = {}
try:
    d.load()
    d.js("window.squaringLab.R.warmOn = false;" + HOOK)
    for q, ms in (("qBal", 6000), ("qUltra", 3000)):
        d.js("document.getElementById('%s').click();" % q)
        time.sleep(1.2)
        for rep in range(1 if q == "qBal" else 2):
            r = d.js("return await window.__run(%d);" % ms)
            out["%s %d" % (q, rep)] = r
            summarise("default Mandelbrot %s rep %d" % (q, rep), r)
            if q == "qUltra":
                print("   jobs", r["jobs"], "gpu", r["gpu"], "blits", r["blits"], flush=True)
                d.p.wait(L + ".renderIdle()", 10)
    # classic bulb, ultra fast: the settle timeline
    d.js("const L = window.squaringLab; L.S.approach = L.APPROACHES.findIndex(a => a.id === 'classic'); L.S.n = 8; L.syncControls(); L.refresh(); L.resetCam(); L.touch();")
    d.p.wait(L + ".renderIdle()", 30)
    for rep in range(1):
        r = d.js("return await window.__run(3000);")
        out["classic ultra %d" % rep] = r
        summarise("classic n=8 qUltra rep %d" % rep, r)
        print("   jobs", r["jobs"], "gpu", r["gpu"], "blits", r["blits"], flush=True)
        d.p.wait(L + ".renderIdle()", 10)
    print(d.p.problems)
finally:
    close(d, proc, prof)
with open(os.path.join(HERE, "diag.json"), "w") as f:
    json.dump(out, f)

# evidence pictures: the busy label during the lambda compile on a fresh page, and the progress bar
d, proc, prof = launch()
try:
    d.load()
    d.js("const s = document.getElementById('eqPreset'); s.value = '1'; s.dispatchEvent(new Event('change', { bubbles: true }));")
    time.sleep(1.0)
    d.shot("A-lambda-busy-1s.png", "#stage")
    print("busy/progress shots written", d.p.problems)
finally:
    close(d, proc, prof)
