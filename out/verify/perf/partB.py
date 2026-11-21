"""Part B: wheel zoom with real wheel input. Camera distance (or 2D picture height) at every frame and at every picture shown.
Part D: a playing phase dial on the classic Mandelbulb."""
import json, os, random, sys, time
from lib import *

REC = r"""
window.__wev = [];
document.getElementById('view').addEventListener('wheel', e => window.__wev.push([performance.now(), e.deltaY, e.ctrlKey]), { capture: true });
window.__rec = ms => { const P = window.__perf, L = window.squaringLab, r = { fr: [], done: false, t0: performance.now() };
  P.blits = []; P.rafJs = []; P.on = true; window.__wev.length = 0;
  const f = () => { const now = performance.now(); r.fr.push([now - r.t0, L.cam.dist, L.S.v2.h]);
    if (now - r.t0 < ms) P.oraf(f); else { r.done = true; P.on = false; r.blits = P.blits.map(b => [b[0] - r.t0, b[1], b[2], b[3]]); r.ev = window.__wev.map(e => [e[0] - r.t0, e[1], e[2]]); r.js = Math.max(0, ...P.rafJs); } };
  P.oraf(f); window.__r = r; };
"""


def analyse(r, col):
    fr = r["fr"]
    worst = 0; wobble = 0; gap = 0; moving = 0; dirn = 0
    for a, b in zip(fr, fr[1:]):
        ch = b[col] / a[col] - 1
        if abs(ch) > 1e-7:
            moving += 1
            worst = max(worst, abs(ch))
            gap = max(gap, b[0] - a[0])
            s = 1 if ch > 0 else -1
            if dirn and s != dirn:
                wobble += 1
            dirn = s
    # the same, picture by picture (what reaches the screen)
    bl = r["blits"]; pworst = 0; pgap = 0; pics = 0
    for a, b in zip(bl, bl[1:]):
        ch = b[col + 1] / a[col + 1] - 1   # a blit record is [t, kind, dist, h]
        if abs(ch) > 1e-7:
            pics += 1
            pworst = max(pworst, abs(ch)); pgap = max(pgap, b[0] - a[0])
    return {"total": fr[-1][col] / fr[0][col], "movingFrames": moving, "worstFramePct": round(100 * worst, 2), "wobbles": wobble, "worstGapMs": round(gap, 1),
            "pictures": pics, "worstPicturePct": round(100 * pworst, 2), "worstPictureGapMs": round(pgap, 1), "events": len(r["ev"]), "jsMax": round(r["js"], 1)}


def trace(d, kind, flat):
    cx, cy = d.at("#view", 0.45, 0.5)
    d.mouse("mouseMoved", cx, cy)
    d.js("window.__rec(1900);")
    time.sleep(0.15)
    rnd = random.Random(7)
    if kind == "one notch":
        d.wheel(cx, cy, 100)
    elif kind == "five notches":
        for _ in range(5):
            d.wheel(cx, cy, 100); time.sleep(0.06)
    elif kind == "trackpad stream":
        end = time.time() + 1.0
        while time.time() < end:
            t = time.time(); d.wheel(cx, cy, rnd.uniform(3, 8)); time.sleep(max(0, 0.016 - (time.time() - t)))
    elif kind == "pinch (ctrl + wheel)":
        end = time.time() + 1.0
        while time.time() < end:
            t = time.time(); d.wheel(cx, cy, -rnd.uniform(1, 4), modifiers=2); time.sleep(max(0, 0.016 - (time.time() - t)))
    for _ in range(60):
        time.sleep(0.1)
        r = d.js("const r = window.__r; return r.done ? r : null;")
        if r:
            break
    return r, analyse(r, 2 if flat else 1)


def part_b(out, label, warm, quality):
    d, proc, prof = launch()
    try:
        d.load()
        d.js(REC)
        if not warm:
            d.js("window.squaringLab.R.warmOn = false;")
        if quality:
            d.js("document.getElementById('%s').click();" % quality)
            d.p.wait(L + ".renderIdle()", 30)
        for flat in (False, True):
            if flat:
                d.js("document.getElementById('flat').click();")
                time.sleep(1.5)
            for kind in ("one notch", "five notches", "trackpad stream", "pinch (ctrl + wheel)"):
                reps = []
                for rep in range(3):
                    r, a = trace(d, kind, flat)
                    reps.append(a)
                    if rep == 0:
                        with open(os.path.join(HERE, "B-trace-%s-%s-%s.json" % (label, "2d" if flat else "3d", kind.split(" ")[0])), "w") as f:
                            json.dump(r, f)
                    d.js("window.squaringLab.resetCam(); window.squaringLab.touch();")
                    time.sleep(0.5)
                name = "%s | %s | %s" % (label, "2D" if flat else "3D", kind)
                out[name] = reps
                g = lambda k: med([x[k] for x in reps])
                print("%-52s total x%.3f frames %3d worst/frame %5.2f%% wobbles %d worst gap %5.1f ms | pictures %3d worst/picture %5.2f%% worst picture gap %6.1f ms | events %d jsMax %.1f   all gaps %s all pic gaps %s" % (
                    name, g("total"), g("movingFrames"), g("worstFramePct"), max(x["wobbles"] for x in reps), g("worstGapMs"), g("pictures"), g("worstPicturePct"), g("worstPictureGapMs"), g("events"), g("jsMax"),
                    [x["worstGapMs"] for x in reps], [x["worstPictureGapMs"] for x in reps]), flush=True)
        if d.p.problems:
            print("PAGE PROBLEMS", d.p.problems[:10], flush=True)
    finally:
        close(d, proc, prof)


def part_d(out):
    d, proc, prof = launch()
    try:
        d.load()
        d.js("window.squaringLab.R.warmOn = false; const L = window.squaringLab; L.S.approach = L.APPROACHES.findIndex(a => a.id === 'classic'); L.S.n = 8; L.syncControls(); L.refresh(); L.resetCam(); L.touch();")
        d.p.wait(L + ".idle()", 60)
        # instrument: canvas draws of the two step figures, scorecard mutations, formula text writes
        d.js(r"""
          const W = window.__d = { c2: 0, c3: 0, card: 0, formula: 0, busy: {}, frames: 0 };
          const wrap = (id, key) => { const cv = document.getElementById(id); if (!cv) return; const cx = cv.getContext('2d'); const o = cx.clearRect.bind(cx); cx.clearRect = (...a) => { W[key]++; return o(...a); }; };
          wrap('step2d', 'c2'); wrap('step3d', 'c3');
          new MutationObserver(m => { W.card += m.length; }).observe(document.getElementById('card'), { subtree: true, childList: true, characterData: true, attributes: true });
          new MutationObserver(m => { W.formula += m.length; }).observe(document.getElementById('rules'), { subtree: true, childList: true, characterData: true });
          W.ids = [!!document.getElementById('step2d'), !!document.getElementById('step3d'), !!document.getElementById('card')];
        """)
        res = []
        for qual in ("qBal", "qUltra"):
            d.js("document.getElementById('%s').click();" % qual)
            time.sleep(1.0)
            for rep in range(2):
                d.click("#par-classic-thetaPlay")
                time.sleep(0.5)
                r = d.js(r"""
                  const P = window.__perf, L = window.squaringLab, W = window.__d, R = L.R;
                  const w0 = { c2: W.c2, c3: W.c3, card: W.card, formula: W.formula };
                  P.blits = []; P.rafJs = []; P.on = true; const t0 = performance.now(); let n = 0, last = t0, mg = 0; const busy = {}; const th0 = L.S.param.classic.theta;
                  await new Promise(res => { const f = () => { const now = performance.now(); mg = Math.max(mg, now - last); last = now; n++; const b = document.getElementById('busy'); if (b && !b.hidden) busy[b.textContent] = (busy[b.textContent] || 0) + 1;
                    if (now - t0 < 3000) P.oraf(f); else res(); }; P.oraf(f); });
                  P.on = false;
                  const pv = P.blits.filter(b => b[1] === 'prev').length, js = P.rafJs;
                  return { frames: n, fps: n / 3, rafMax: mg, pictures: pv, picPerSec: pv / 3, step2dDraws: W.c2 - w0.c2, step3dDraws: W.c3 - w0.c3, cardMutations: W.card - w0.card, formulaMutations: W.formula - w0.formula,
                    busy, jsAvg: js.reduce((a, b) => a + b, 0) / Math.max(1, js.length), jsMax: Math.max(0, ...js), jsCalls: js.length, theta0: th0, theta1: L.S.param.classic.theta, ps: R.ps, pw: R.pw, ph: R.ph, ids: W.ids,
                    playing: document.getElementById('par-classic-thetaPlay').getAttribute('aria-pressed') };
                """)
                r["quality"] = qual
                res.append(r)
                print("D", json.dumps(r), flush=True)
                if rep == 0 and qual == "qBal":
                    d.shot("D-playing.png")
                d.click("#par-classic-thetaPlay")
                time.sleep(0.4)
        out["D"] = res
        if d.p.problems:
            print("PAGE PROBLEMS", d.p.problems[:10], flush=True)
    finally:
        close(d, proc, prof)


out = {}
what = sys.argv[1] if len(sys.argv) > 1 else "bd"
if "b" in what:
    part_b(out, "after load, Balanced", True, None)
if "d" in what:
    part_d(out)
with open(os.path.join(HERE, "partB-%s.json" % what), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
