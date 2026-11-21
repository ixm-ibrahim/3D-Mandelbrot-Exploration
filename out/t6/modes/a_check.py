"""Part A check: page's 2D view at z = 0 (two-tone silhouette) against a flat set computed here with plain
complex arithmetic and the page's own stopping rule (escape radius 64, the iteration count on the page, the pole
rule for a negative power started at 0). Prints one line per case and writes a_result.json."""
import json, os, sys, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
cases = json.load(open(os.path.join(HERE, "a_cases.json")))
ITER = int(sys.argv[1]) if len(sys.argv) > 1 else 14
ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
BAIL = 64.0


def escaped(case, W, H, iters=ITER):
    s = case["h"] / H
    x = case["x"] + (np.arange(W) + 0.5 - W / 2) * s
    y = case["y"] + (H / 2 - (np.arange(H) + 0.5)) * s
    X, Y = np.meshgrid(x, y)
    P = X + 1j * Y
    n = case["n"]
    if case["mode"] == "m":
        c = P.copy(); v = np.zeros_like(P)
    else:
        c = np.full(P.shape, complex(case["c"][0], case["c"][1])); v = P.copy()
    r = np.abs(v)
    esc = np.zeros(P.shape, bool); alive = np.ones(P.shape, bool)
    for k in range(iters + 1):
        newly = alive & (r > BAIL)
        esc |= newly; alive &= ~newly
        if k == iters:
            break
        with np.errstate(all="ignore"):
            w = v ** n + c
            w2 = np.abs(w) ** 2
        wild = ~(w2 < 1e36)
        pole = np.zeros(P.shape, bool)
        if k == 0:
            big = 1e3 * (BAIL + np.abs(c))
            pole = alive & (r < 1e-3) & (wild | (w2 > big * big))
        w = np.where(wild, 1e18 + 0j, w)
        lw = np.where(wild, 1e18, np.sqrt(np.where(wild, 0, w2)))
        upd = alive & ~pole
        v = np.where(upd, w, v); r = np.where(upd, lw, r)
        v = np.where(pole, 1e9 + 0j, v); r = np.where(pole, 0.0, r)
    return esc


def near(mask_edge, d):
    out = mask_edge.copy()
    for _ in range(d):
        o = out.copy()
        o[1:, :] |= out[:-1, :]; o[:-1, :] |= out[1:, :]; o[:, 1:] |= out[:, :-1]; o[:, :-1] |= out[:, 1:]
        o[1:, 1:] |= out[:-1, :-1]; o[:-1, :-1] |= out[1:, 1:]; o[1:, :-1] |= out[:-1, 1:]; o[:-1, 1:] |= out[1:, :-1]
        out = o
    return out


def edge_of(m):
    e = np.zeros(m.shape, bool)
    e[1:, :] |= m[1:, :] != m[:-1, :]; e[:-1, :] |= m[1:, :] != m[:-1, :]
    e[:, 1:] |= m[:, 1:] != m[:, :-1]; e[:, :-1] |= m[:, 1:] != m[:, :-1]
    return e


ref = np.asarray(Image.open(os.path.join(HERE, "a", "mercator-m-n2-f0.png")).convert("RGB")).astype(float)
Hh, Ww = ref.shape[:2]
cut = ref[Hh // 2, Ww // 2]          # c = -0.5: inside the Mandelbrot set
bg = ref[2, 2]                       # a corner: outside
print("picture %dx%d, inside colour %s, outside colour %s, iterations %d" % (Ww, Hh, cut, bg, ITER))
rows = []
for case in cases:
    if ONLY and not re.search(ONLY, case["name"]): continue
    p = os.path.join(HERE, "a", case["name"] + ".png")
    if not os.path.exists(p):
        print("%-24s MISSING" % case["name"]); continue
    im = np.asarray(Image.open(p).convert("RGB")).astype(float)
    H, W = im.shape[:2]
    d_in = np.linalg.norm(im - cut, axis=2); d_out = np.linalg.norm(im - bg, axis=2)
    page_in = d_in < d_out
    other = (np.minimum(d_in, d_out) > 0.25 * np.linalg.norm(cut - bg)).mean()   # pixels that are neither colour (blends)
    esc = escaped(case, W, H)
    res = {}
    for label, refin in (("bounded", ~esc), ("escaping", esc)):
        dis = page_in != refin
        e = edge_of(refin)
        far2 = dis & ~near(e, 2)
        far4 = dis & ~near(e, 4)
        res[label] = dict(dis=float(dis.mean()), far2=int(far2.sum()), far4=int(far4.sum()), edge=float(e.mean()), ref_in=float(refin.mean()))
    expect = "escaping" if case["n"] < 0 else "bounded"
    best = min(res, key=lambda k: res[k]["dis"])
    r = res[best]
    row = dict(name=case["name"], expect=expect, best=best, page_in=float(page_in.mean()), blend=float(other), **{k: r[k] for k in r},
               other_dis=res["escaping" if expect == "bounded" else "bounded"]["dis"])
    rows.append(row)
    print("%-24s solid=%-8s page_in %6.2f%% ref_in %6.2f%% disagree %6.3f%% (outline %5.2f%%) beyond2px %5d beyond4px %5d %s"
          % (case["name"], best, 100 * row["page_in"], 100 * r["ref_in"], 100 * r["dis"], 100 * r["edge"], r["far2"], r["far4"],
             "" if best == expect else "  << not the labelling I expected"))
json.dump(rows, open(os.path.join(HERE, "a_result_i%d%s.json" % (ITER, "-part" if ONLY else "")), "w"), indent=1)
