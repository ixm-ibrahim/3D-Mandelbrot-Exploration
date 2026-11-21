"""Checker "arithmetic": a flat picture of the page against my Python reference (the code t2_pixels.py uses, as a
module, for the checks that come after it).

    info = lab.js(INFO)                       # the panes the page reports, its tokens, what lies over the stage
    S = Scene(info)                           # the reference numbers for those panes
    r = check(S, lab.grab('#learnShapeCanvas'), k)   # counts for the whole step k
"""
import numpy as np
import cref

K = 16
INFO = """
const cv = $('learnShapeCanvas'), r = cv.getBoundingClientRect(), st = L.shape.state();
const rects = [...document.querySelectorAll('#stage *')].filter(e => e.tagName !== 'CANVAS' && !e.children.length && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
  .map(e => e.getBoundingClientRect()).filter(b => b.width > 0 && b.height > 0).map(b => [b.left - r.left, b.top - r.top, b.width, b.height]);
const cs = getComputedStyle(document.documentElement), tok = k => cs.getPropertyValue(k).trim();
return { st, box: [r.left, r.top, r.width, r.height], rects, brass: tok('--brass'), stage: tok('--stage'), bad: tok('--bad'), ink2: tok('--ink-2'), n: S.n, abs: S.abs, flip: S.flip };
"""
hexrgb = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)], dtype=np.float64)


def box3(a, fn):
    p = np.pad(a, 1, mode="edge"); out = a.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out = fn(out, p[dy:dy + a.shape[0], dx:dx + a.shape[1]])
    return out


class Scene:
    def __init__(self, info):
        st = info["st"]
        self.info, self.st = info, st
        self.W, self.H = int(round(info["box"][2])), int(round(info["box"][3]))
        self.ref = np.zeros((2 * self.H, 2 * self.W), dtype=np.int32) - 1
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
            yy, xx = np.mgrid[0:self.H, 0:self.W]
            rr = np.hypot(xx + 0.5 - (cx - V["x"] * s), yy + 0.5 - (cy + V["y"] * s))
            inp = (xx >= P["x"]) & (xx < P["x"] + P["w"]) & (yy >= P["y"]) & (yy < P["y"] + P["h"])
            self.skip |= inp & (np.abs(rr - 2 * s) <= 2.5)
            self.skip[int(P["y"]):int(P["y"]) + 50, int(P["x"]):int(P["x"]) + 235] = True
            d = st["diamonds"][i]
            if d:
                self.skip[max(0, int(d[1]) - 11):int(d[1]) + 22, max(0, int(d[0]) - 11):int(d[0]) + 30] = True
            if i:
                if st["side"]: self.skip[:, int(P["x"]) - 1:int(P["x"]) + 2] = True
                else: self.skip[int(P["y"]) - 1:int(P["y"]) + 2, :] = True
        for x, y, w, h in info["rects"]:
            self.skip[max(0, int(y) - 2):int(y + h) + 3, max(0, int(x) - 2):int(x + w) + 3] = True
        self.brass, self.stage, self.bad = hexrgb(info["brass"]), hexrgb(info["stage"]), hexrgb(info["bad"])

    def cover(self, k):
        ins = (self.ref > k).astype(np.float64)
        return (ins[0::2, 0::2] + ins[1::2, 0::2] + ins[0::2, 1::2] + ins[1::2, 1::2]) / 4

    def painted(self, img, colour=None):
        c = self.brass if colour is None else colour
        pix = img.astype(np.float64)
        full = np.abs(pix - c).max(-1) <= 6
        d = c - self.stage
        t = ((pix - self.stage) @ d) / (d @ d)
        resid = np.abs(pix - (self.stage + t[..., None] * d)).max(-1)
        return full, (t >= 0.5) & (resid <= 25)


def check(S, img, k):
    """inside / outside: pixels whose 3 x 3 neighbourhood lies wholly in / wholly out of shape k (ring, labels, diamond
    and what lies over the stage left out); miss: inside and not painted; extra: outside and painted at least half."""
    if img.shape[0] != S.H or img.shape[1] != S.W:
        return dict(k=k, inside=-1, outside=-1, miss=-1, extra=-1, size=img.shape[:2])
    cov = S.cover(k)
    sure_in = (box3(cov, np.minimum) >= 1) & ~S.skip
    sure_out = (box3(cov, np.maximum) <= 0) & ~S.skip
    full, half = S.painted(img)
    return dict(k=k, inside=int(sure_in.sum()), outside=int(sure_out.sum()), miss=int((sure_in & ~full).sum()), extra=int((sure_out & half).sum()))
