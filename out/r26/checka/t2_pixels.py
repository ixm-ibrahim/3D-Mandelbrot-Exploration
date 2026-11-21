"""Check 1b and 3 (flat part): the flat PICTURE against my Python reference, from screenshots.
For a screenshot of the stage's canvas at a whole step k every pixel is put where it stands in the plane (from the
pane the page reports and its zoom), and the reference says how much of it shape k covers (four points to a pixel,
where the page itself asks). Then:
  - a pixel whose 3 x 3 neighbourhood lies wholly in shape k must be painted in the body colour (--brass);
  - a pixel whose 3 x 3 neighbourhood lies wholly outside must not be painted (not even half);
  - nesting in the picture: a pixel painted at step k + 1 must be painted at step k.
Left out of the count: the dashed ring of the big circle (it is drawn over the shape), the diamond and its letter,
the two labels in a pane's corner, and whatever of the page lies over the stage (the hint, buttons).
Between two steps (k + u): the points being thrown out must show in the warning colour (--bad), the rest in brass.
"""
import json, sys, time
import numpy as np
from clab import Lab, Log
import cref

log = Log("t2_pixels")
K = 16
INFO = """
const cv = $('learnShapeCanvas'), r = cv.getBoundingClientRect(), st = L.shape.state();
const rects = [...document.querySelectorAll('#stage *')].filter(e => e.tagName !== 'CANVAS' && !e.children.length && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
  .map(e => e.getBoundingClientRect()).filter(b => b.width > 0 && b.height > 0).map(b => [b.left - r.left, b.top - r.top, b.width, b.height]);
const cs = getComputedStyle(document.documentElement), tok = k => cs.getPropertyValue(k).trim();
return { st, box: [r.left, r.top, r.width, r.height], rects, brass: tok('--brass'), stage: tok('--stage'), bad: tok('--bad'), ink2: tok('--ink-2'), n: S.n, abs: S.abs, flip: S.flip, sc: [scrollX, scrollY] };
"""
hexrgb = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)], dtype=np.float64)


def box3(a, fn):
    """fn (np.minimum / np.maximum) over the 3 x 3 neighbourhood, edges repeated."""
    p = np.pad(a, 1, mode="edge"); out = a.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out = fn(out, p[dy:dy + a.shape[0], dx:dx + a.shape[1]])
    return out


class Scene:
    """The reference numbers for the panes of one picture (worked out once, used for every step)."""

    def __init__(self, info):
        st = info["st"]
        self.info, self.st = info, st
        self.W, self.H = int(round(info["box"][2])), int(round(info["box"][3]))
        self.ref = np.zeros((2 * self.H, 2 * self.W), dtype=np.int32) - 1      # -1: no pane there
        self.skip = np.zeros((self.H, self.W), dtype=bool)
        n, ab, fl = info["n"], info["abs"], info["flip"]
        for i, P in enumerate(st["panes"]):
            V = st["view2"][P["kind"]]
            s = 0.21 * min(P["w"], P["h"]) * V["zoom"]
            cx, cy = P["x"] + P["w"] / 2, P["y"] + P["h"] / 2
            a0, a1, b0, b1 = int(2 * P["x"]), int(2 * (P["x"] + P["w"])), int(2 * P["y"]), int(2 * (P["y"] + P["h"]))
            ax = (np.arange(a0, a1) + 0.5) / 2; ay = (np.arange(b0, b1) + 0.5) / 2
            X, Y = np.meshgrid(V["x"] + (ax - cx) / s, V["y"] - (ay - cy) / s)
            self.ref[b0:b1, a0:a1] = cref.out_points(X, Y, P["kind"], st["c"], n, bool(ab[0]), bool(ab[1]), bool(fl[0]), K)
            # the ring of the big circle, the labels in the corner, the diamond
            yy, xx = np.mgrid[0:self.H, 0:self.W]
            rr = np.hypot(xx + 0.5 - (cx - V["x"] * s), yy + 0.5 - (cy + V["y"] * s))
            inp = (xx >= P["x"]) & (xx < P["x"] + P["w"]) & (yy >= P["y"]) & (yy < P["y"] + P["h"])
            self.skip |= inp & (np.abs(rr - 2 * s) <= 2.5)
            self.skip[int(P["y"]):int(P["y"]) + 50, int(P["x"]):int(P["x"]) + 235] = True
            d = st["diamonds"][i]
            if d:
                self.skip[max(0, int(d[1]) - 11):int(d[1]) + 22, max(0, int(d[0]) - 11):int(d[0]) + 30] = True
            if i:   # the hairline between two pictures
                if st["side"]: self.skip[:, int(P["x"]) - 1:int(P["x"]) + 2] = True
                else: self.skip[int(P["y"]) - 1:int(P["y"]) + 2, :] = True
        for x, y, w, h in info["rects"]:
            self.skip[max(0, int(y) - 2):int(y + h) + 3, max(0, int(x) - 2):int(x + w) + 3] = True
        self.brass, self.stage, self.bad = hexrgb(info["brass"]), hexrgb(info["stage"]), hexrgb(info["bad"])

    def cover(self, k):
        """how much of each pixel shape k covers (0, 1/4, ... 1)"""
        ins = (self.ref > k).astype(np.float64)
        return (ins[0::2, 0::2] + ins[1::2, 0::2] + ins[0::2, 1::2] + ins[1::2, 1::2]) / 4

    def painted(self, img, colour=None):
        """(fully painted, at least half painted) in the body colour, pixel by pixel"""
        c = self.brass if colour is None else colour
        pix = img.astype(np.float64)
        full = np.abs(pix - c).max(-1) <= 6
        d = c - self.stage
        t = ((pix - self.stage) @ d) / (d @ d)
        resid = np.abs(pix - (self.stage + t[..., None] * d)).max(-1)
        return full, (t >= 0.5) & (resid <= 25)


def check_whole(S, img, k):
    cov = S.cover(k)
    sure_in = (box3(cov, np.minimum) >= 1) & ~S.skip
    sure_out = (box3(cov, np.maximum) <= 0) & ~S.skip
    full, half = S.painted(img)
    miss = sure_in & ~full          # should be painted and is not
    extra = sure_out & half         # painted where nothing is left
    edge = ~(box3(cov, np.minimum) >= 1) & ~(box3(cov, np.maximum) <= 0)
    # along the edge: how far the painted share of the picture is from the reference's share, in pixels of area
    return dict(k=k, inside=int(sure_in.sum()), outside=int(sure_out.sum()), miss=int(miss.sum()), extra=int(extra.sum()), edge=int(edge.sum()),
                area_ref=float(cov[~S.skip].sum()), area_pic=float(half[~S.skip].sum())), miss | extra


defects, pics = [], []


def run(lab, name, setup, steps, series=False, shot_at=()):
    """setup: JavaScript that puts the page in the scene; steps: whole steps to look at"""
    lab.js(setup + "\nreturn 1;")
    info = lab.js("L.shape.goto(0);" + INFO)
    S = Scene(info)
    prev = None; nest_bad = 0; rows = []
    for k in steps:
        st = lab.js("return L.shape.goto(%d);" % k)
        if st["pos"] != k: defects.append("%s: goto(%d) left the slider at %s" % (name, k, st["pos"]))
        img = lab.grab("#learnShapeCanvas")
        if img.shape[0] != S.H or img.shape[1] != S.W:
            defects.append("%s: canvas box %s is not the stage the page reports %s" % (name, img.shape, (S.H, S.W))); return
        r, wrong = check_whole(S, img, k)
        rows.append(r)
        if series and prev is not None:
            _, half = S.painted(img)
            v = half & ~prev & ~S.skip
            nest_bad += int(v.sum())
        if series:
            prev = S.painted(img)[1]
        if r["miss"] or r["extra"]:
            defects.append("%s, step %d: %d pixels inside shape %d are not painted, %d pixels outside it are" % (name, k, r["miss"], k, r["extra"]))
            out = img.copy(); out[wrong] = [255, 0, 255]
            pics.append(lab.save(out, "out/r26/checka/t2-WRONG-%s-%02d.png" % (name, k)))
        if k in shot_at:
            pics.append(lab.save(img, "out/r26/checka/t2-%s-%02d.png" % (name, k)))
    log("%s  (stage %d x %d, %d pane%s, power %s, |x||y| %s, flip y %s, c %s, zoom %s)" % (name, S.W, S.H, len(S.st["panes"]), "" if len(S.st["panes"]) == 1 else "s",
        info["n"], info["abs"][:2], info["flip"][0], S.st["c"][:2], [S.st["view2"][P["kind"]]["zoom"] for P in S.st["panes"]]))
    for r in rows:
        log("   step %2d: surely inside %7d px, not painted %d;  surely outside %7d px, painted %d;  edge band %6d px;  area: reference %.0f px, picture %.0f px" % (
            r["k"], r["inside"], r["miss"], r["outside"], r["extra"], r["edge"], r["area_ref"], r["area_pic"]))
    if series:
        log("   nesting in the picture, steps %d to %d: %d pixels painted at a step and not at the step before" % (steps[0], steps[-1], nest_bad))
        if nest_bad: defects.append("%s: %d pixels are painted at step k + 1 and not at step k" % (name, nest_bad))
    return S


def between(lab, name, setup, pos):
    lab.js(setup + "\nreturn 1;")
    info = lab.js("L.shape.goto(%s);" % pos + INFO)
    S = Scene(info); k = int(pos)
    img = lab.grab("#learnShapeCanvas")
    c0, c1 = S.cover(k), S.cover(k + 1)
    stay = (box3(c1, np.minimum) >= 1) & ~S.skip                       # still in after step k + 1
    bite = (box3(c0 - c1, np.minimum) >= 1) & ~S.skip                  # in shape k, thrown out by step k + 1
    out = (box3(c0, np.maximum) <= 0) & ~S.skip
    fb, hb = S.painted(img); fw, hw = S.painted(img, S.bad)
    r = dict(stay=int(stay.sum()), stay_not_brass=int((stay & ~fb).sum()), bite=int(bite.sum()), bite_not_warn=int((bite & ~fw).sum()), out=int(out.sum()), out_painted=int((out & (hb | hw)).sum()))
    log("%s at %s: %s   (sentence: %s)" % (name, pos, json.dumps(r), info["st"]["sentence"]))
    pics.append(lab.save(img, "out/r26/checka/t2-%s-%s.png" % (name, pos)))
    if r["stay_not_brass"] or r["bite_not_warn"] or r["out_painted"]:
        defects.append("%s at %s: %s" % (name, pos, json.dumps(r)))


ALLK = list(range(0, 17))
t0 = time.time()
with Lab("r26-checka", size=(1400, 950), theme="dark") as lab:
    on = "await shapeOn({ kind: '%s', space: 2, c: %s, pos: 0 }); setRule(%s, %s, %s);"
    run(lab, "wide-dark-m", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"), ALLK, series=True, shot_at=(0, 2, 5, 16))
    run(lab, "wide-dark-j-rabbit", on % ("j", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"), ALLK, series=True, shot_at=(1, 8))
    run(lab, "wide-dark-j-basilica", on % ("j", "[-1,0,0]", 2, "[0,0,0]", "[0,0]"), [0, 1, 2, 5, 16], shot_at=(5,))
    run(lab, "wide-dark-j-dendrite", on % ("j", "[0,1,0]", 2, "[0,0,0]", "[0,0]"), ALLK, series=True, shot_at=(16,))
    run(lab, "wide-dark-both-rabbit", on % ("both", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"), [0, 1, 4, 9, 16], shot_at=(4,))
    run(lab, "wide-dark-m-power3-absx", on % ("m", "[0,0,0]", 3, "[1,0,0]", "[0,0]"), [1, 2, 4, 7, 16], shot_at=(4,))
    run(lab, "wide-dark-j-power2.5-flipy", on % ("j", "[0.28,0.53,0]", 2.5, "[0,0,0]", "[1,0]"), ALLK, series=True, shot_at=(3,))
    run(lab, "wide-dark-both-power-2", on % ("both", "[0.28,0.53,0]", -2, "[0,0,0]", "[0,0]"), [0, 1, 2, 3, 8, 16], shot_at=(2,))
    run(lab, "wide-dark-j-power0.5", on % ("j", "[-0.6,0.2,0]", 0.5, "[0,0,0]", "[0,0]"), ALLK, series=True, shot_at=(3,))
    # zoomed in with the wheel, and moved by a drag
    zoom = on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]") + """
      const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect();
      $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -700, clientX: b.left + 300, clientY: b.top + 215, bubbles: true, cancelable: true }));
      await sleep(250);
      ptr(cv, 'pointerdown', 500, 300); ptr(cv, 'pointermove', 470, 280); ptr(cv, 'pointermove', 441, 263); await frame(); ptr(cv, 'pointerup', 441, 263); await sleep(250);"""
    run(lab, "wide-dark-m-zoomed", zoom, [2, 3, 6, 9, 16], shot_at=(6,))
    zoomj = zoom.replace("kind: 'm'", "kind: 'both'").replace("c: [0,0,0]", "c: [-0.1226,0.7449,0]")
    run(lab, "wide-dark-both-zoomed-left", zoomj, [3, 7], shot_at=(7,))
    lab.js("$('learnShapeViewReset').click(); return 1;")
    between(lab, "wide-dark-m-between", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"), 2.3)
    between(lab, "wide-dark-j-rabbit-between", on % ("j", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"), 4.3)
    between(lab, "wide-dark-both-between", on % ("both", "[-1,0,0]", 2, "[0,0,0]", "[0,0]"), 1.3)
    lab.js("setRule(2, [0,0,0], [0,0]); return 1;")
    log.problems(lab)
    if lab.problems: defects.append("console problems in the wide dark run: %s" % lab.problems[:3])

with Lab("r26-checka", size=(1400, 950), theme="light") as lab:
    run(lab, "wide-light-m", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"), [0, 1, 5, 16], shot_at=(5,))
    run(lab, "wide-light-both-rabbit", on % ("both", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"), [0, 6, 16], shot_at=(6,))
    between(lab, "wide-light-m-between", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"), 3.3)
    log.problems(lab)
    if lab.problems: defects.append("console problems in the wide light run: %s" % lab.problems[:3])

with Lab("r26-checka", size=(390, 800), theme="dark") as lab:
    run(lab, "phone-dark-m", on % ("m", "[0,0,0]", 2, "[0,0,0]", "[0,0]"), [0, 2, 5, 16], shot_at=(5,))
    run(lab, "phone-dark-both-rabbit", on % ("both", "[-0.1226,0.7449,0]", 2, "[0,0,0]", "[0,0]"), [0, 5, 16], shot_at=(5,))
    run(lab, "phone-dark-j-basilica", on % ("j", "[-1,0,0]", 2, "[0,0,0]", "[0,0]"), ALLK, series=True, shot_at=(8,))
    log.problems(lab)
    if lab.problems: defects.append("console problems in the phone run: %s" % lab.problems[:3])

log("")
log("pictures: " + ", ".join(p.replace("\\", "/").split("/checka/")[-1] for p in pics))
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects:
    log("  " + d)
