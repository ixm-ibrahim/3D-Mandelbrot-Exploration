"""Check 3, flat pictures, second look. t2_pixels counted a few pixels (2 to 26 in a run of 17 steps) as "painted at
step k + 1 and not at step k". Its test for "painted" was: at least half way from the stage colour to brass and close
to that line of colours. A pixel on the edge that also holds a piece of the grey outline of the shape before lies
off that line, so it was counted as not painted. Here every pixel is taken apart into its three colours
(stage, brass, the grey --ink-2 of the outlines and axes), and the brass share is compared from step to step:
  (i)  a pixel that is wholly brass at step k + 1 must be wholly brass at step k;
  (ii) the brass share of a pixel must not grow from step k to step k + 1 (by more than 0.13: one sample of four
       is 0.25, and the browser's scaling rounds).
"""
import numpy as np
from clab import Lab, Log

log = Log("t2b_nest")
hexrgb = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)], dtype=np.float64)
INFO = """
const cv = $('learnShapeCanvas'), r = cv.getBoundingClientRect(), st = L.shape.state();
const rects = [...document.querySelectorAll('#stage *')].filter(e => e.tagName !== 'CANVAS' && !e.children.length && e.getClientRects().length)
  .map(e => e.getBoundingClientRect()).filter(b => b.width > 0 && b.height > 0).map(b => [b.left - r.left, b.top - r.top, b.width, b.height]);
const cs = getComputedStyle(document.documentElement), tok = k => cs.getPropertyValue(k).trim();
return { st, rects, brass: tok('--brass'), stage: tok('--stage'), ink2: tok('--ink-2') };
"""
defects = []


def series(lab, name, setup):
    lab.js(setup + "\nreturn 1;")
    info = lab.js("L.shape.goto(0);" + INFO)
    brass, stage, ink2 = hexrgb(info["brass"]), hexrgb(info["stage"]), hexrgb(info["ink2"])
    A = np.stack([brass - stage, ink2 - stage], axis=1)            # 3 x 2
    pinv = np.linalg.pinv(A)
    prev = None; v1 = v2 = 0; worst = 0.0
    for k in range(17):
        lab.js("L.shape.goto(%d); return 1;" % k)
        img = lab.grab("#learnShapeCanvas").astype(np.float64)
        if prev is None:
            skip = np.zeros(img.shape[:2], dtype=bool)
            for x, y, w, h in info["rects"]:
                skip[max(0, int(y) - 2):int(y + h) + 3, max(0, int(x) - 2):int(x + w) + 3] = True
            for P in info["st"]["panes"]:
                skip[int(P["y"]):int(P["y"]) + 50, int(P["x"]):int(P["x"]) + 235] = True   # the two labels (the second changes with the step)
        share = (img - stage) @ pinv.T                              # [..., 0] brass, [..., 1] grey
        a = share[..., 0]
        full = np.abs(img - brass).max(-1) <= 6
        if prev is not None:
            v1 += int((full & ~prev[1] & ~skip).sum())
            grow = (a - prev[0])[~skip]
            v2 += int((grow > 0.13).sum()); worst = max(worst, float(grow.max()))
        prev = (a, full)
    log("%-34s wholly brass at k + 1 and not at k: %d pixels;  brass share grown by more than 0.13: %d pixels;  largest growth of a pixel's brass share: %.3f" % (name, v1, v2, worst))
    if v1 or v2: defects.append("%s: %d + %d pixels" % (name, v1, v2))


on = "await shapeOn({ kind: '%s', space: 2, c: %s, pos: 0 }); setRule(%s, %s, %s);"
with Lab("r26-checka", size=(1400, 950), theme="dark") as lab:
    series(lab, "wide dark, Mandelbrot shape", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"))
    series(lab, "wide dark, Julia rabbit", on % ("j", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"))
    series(lab, "wide dark, Julia dendrite", on % ("j", "[0,1,0]", 2, "[0,0,0]", "[0,0]"))
    series(lab, "wide dark, Both, basilica", on % ("both", "[-1,0,0]", 2, "[0,0,0]", "[0,0]"))
    series(lab, "wide dark, Julia power 2.5 flip y", on % ("j", "[0.28,0.53,0]", 2.5, "[0,0,0]", "[1,0]"))
    series(lab, "wide dark, Julia power -2", on % ("j", "[0.28,0.53,0]", -2, "[0,0,0]", "[0,0]"))
    series(lab, "wide dark, Julia power 0.5 c=1.2", on % ("j", "[1.2,0.3,0]", 0.5, "[0,0,0]", "[0,0]"))
    lab.js("setRule(2, [0,0,0], [0,0]); return 1;")
    log.problems(lab)
with Lab("r26-checka", size=(1400, 950), theme="light") as lab:
    series(lab, "wide light, Mandelbrot shape", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"))
    log.problems(lab)
with Lab("r26-checka", size=(390, 800), theme="dark") as lab:
    series(lab, "phone dark, Julia basilica", on % ("j", "[-1,0,0]", 2, "[0,0,0]", "[0,0]"))
    series(lab, "phone dark, Both, rabbit", on % ("both", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"))
    log.problems(lab)
log("DEFECTS: %d" % len(defects))
for d in defects:
    log("  " + d)
