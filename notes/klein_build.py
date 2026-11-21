"""Build data/klein-presets.json: the list of Kleinian presets, each checked three ways.

    python notes/klein_build.py            check every preset, size it, write the JSON, render a contact sheet
    python notes/klein_build.py --check    checks only (no rendering, nothing written)
    python notes/klein_build.py --boundary confirm that every cusp used sits on the edge of the family

For each preset:
  1. clean:  the pearls are listed directly (klein_model.pearls) and none may cut into another;
  2. faithful: the shader's distance estimate (ported in klein_model.kde) must call solid every sample
     point that the pearl list says is solid;
  3. framed: the turning-out radius is set from a quick render so the object reaches about two thirds of
     the way from the middle of the stage to its top edge (klein_render.fit). An object that will not
     come inside the stage is refused.
The camera always looks at the origin, where the two walls touch.
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klein_cusps import cusp
from klein_model import pearls, missed, kde
from klein_render import render, fit, ROOT

TOP = dict(yaw=-1.5708, pitch=1.15)      # from above, wall spheres one over the other on screen
TILT = dict(yaw=-1.35, pitch=1.0)        # from above and a little to one side
HOME = dict(yaw=0.35, pitch=0.35)        # the lab's own Kleinian camera
DIST = 6.4


def mu_of(p, q, lean=0.0, lift=0.0):
    """mu of the p/q cusp, raised by `lift` (into the family), then turned `lean` degrees about the x-axis
    (which moves part of its i component into j)."""
    m = cusp(p, q)
    t = math.radians(lean)
    y = m.imag + lift
    return [m.real, y * math.cos(t), y * math.sin(t)]


def centre(mu, dx=0.0, dz=0.0):
    """mu/2 moved by whole cells: a point about which the whole set has a half-turn symmetry"""
    return [mu[0] / 2 + dx, mu[1] / 2, mu[2] / 2 + dz]


def P(name, note, source, mu, C, three, cam, L=1.0, depth=60, R=None, dist=DIST):
    return dict(name=name, note=note, source=source,
                k=dict(mx=round(mu[0], 6), my=round(mu[1], 6), mz=round(mu[2], 6), three=three, L=L, iter=depth,
                       invR=R if R else 0.8, cx=round(C[0], 4), cy=round(C[1], 4), cz=round(C[2], 4)),
                cam=dict(yaw=cam["yaw"], pitch=cam["pitch"], dist=dist), fixedR=R is not None)


def presets():
    out = []
    # ----- cusps of the Maskit family (mz = 0): pearls that just touch
    m = mu_of(0, 1)
    out.append(P("0/1 cusp, the starting view", "The lab's own starting group, μ = 2i. Two wall spheres and pearls that just touch, spread in every direction by the third map.",
                 "cusp 0/1", m, [1, 1, 0], True, HOME, R=1.2, dist=7))
    out.append(P("0/1 cusp, one row of pearls", "The same group without the third map, seen from above. The pearls and the round gaps between them together make the Apollonian gasket.",
                 "cusp 0/1", m, [1, 1, 0], False, TOP))
    m = mu_of(1, 15)
    out.append(P("1/15 cusp, spirals", "A classic cusp. The strings of pearls wind into spirals before they close up. Two maps, seen from above.",
                 "cusp 1/15", m, [-1, 0.4894, 0], False, TOP))
    m = mu_of(1, 2)
    out.append(P("1/2 cusp", "μ = 1 + √3·i. Two maps. The picture is mirror-symmetric, with round windows between the strings of pearls.",
                 "cusp 1/2", m, [-1, 0.5774, 0], False, dict(yaw=-1.2, pitch=0.75)))
    m = mu_of(1, 3)
    out.append(P("1/3 cusp", "Turned out through the middle of a round gap, which gives the picture a half-turn symmetry. Third map on.",
                 "cusp 1/3", m, centre(m), True, TILT))
    m = mu_of(2, 5)
    out.append(P("2/5 cusp", "Two maps. A short chain of pearls runs between two large ones, and the picture has a half-turn symmetry.",
                 "cusp 2/5", m, centre(m, 1), False, TILT))
    m = mu_of(1, 5)
    out.append(P("1/5 cusp", "Third map on. Two large pearls joined by a short chain, with round windows on either side.",
                 "cusp 1/5", m, centre(m), True, TILT))
    m = mu_of(1, 4)
    out.append(P("1/4 cusp", "Two maps, seen from above. One wall sphere, with strings of pearls closing around round windows.",
                 "cusp 1/4", m, [-0.647, 1.2734, 0], False, TILT))
    m = mu_of(5, 13)
    out.append(P("5/13 cusp, branching", "5/13 is a ratio of Fibonacci numbers, like 1/2, 1/3, 2/5 and 3/8 before it. The pearls thin out into branches.",
                 "cusp 5/13", m, [0.548, 0.855, 0], False, TILT))
    m = mu_of(8, 21)
    out.append(P("8/21 cusp, near the golden mean", "The next fraction in the same sequence: 8/21 is close to 0.382, one minus the golden mean. Fine branches of pearls stand around one wall sphere.",
                 "cusp 8/21", m, [-0.996, 0.293, 0], False, TOP))
    # ----- just inside the family: the strings of pearls no longer close up
    m = mu_of(3, 10, lift=0.09)
    out.append(P("Above the 3/10 cusp", "μ raised by 0.09 from the 3/10 cusp into the family. The strings of pearls have come apart into one loose chain.",
                 "inside", m, centre(m, -1), False, TILT))
    m = mu_of(1, 2, lift=0.17)
    out.append(P("Above the 1/2 cusp", "μ raised by 0.17 from the 1/2 cusp. The strings of pearls no longer close up.",
                 "inside", m, [-1, 0.6, 0], False, TOP))
    m = [0.1, 1.95, 0.0]
    out.append(P("Inside, near the 0/1 cusp", "μ = 0.1 + 1.95i, a little above the boundary. Two wall spheres with horns that curl but do not close.",
                 "inside", m, centre(m, 1), False, TOP))
    # ----- found by exploring: a non-zero j part, or a different step for the third map
    m = mu_of(1, 3, lean=25)
    out.append(P("1/3 cusp, leaning in depth", "The two maps of the 1/3 cusp turned 25° about the x-axis, which gives μ a j part. The walls now cut the group at a slant, so the pearls come out in unequal sizes.",
                 "explored", m, centre(m), False, TILT))
    m = mu_of(2, 5, lean=20)
    out.append(P("2/5 cusp, leaning in depth", "The 2/5 cusp turned 20° about the x-axis, with the third map on.",
                 "explored", m, centre(m, 1), True, TILT))
    m = mu_of(0, 1, lean=30)
    out.append(P("0/1 cusp, leaning 30°", "μ = √3·i + j: the starting group turned 30° about the x-axis. Two maps, seen from above.",
                 "explored", m, [1, m[1] / 2, 0], False, TOP))
    out.append(P("Leaning 30°, seen across", "The same leaning group with the third map on, seen from the side: a disc of pearls with round windows.",
                 "explored", m, [0, 1.13, 0], True, dict(yaw=0.0, pitch=0.25)))
    m = [0.5, 1.7, 0.5]
    out.append(P("Leaning both ways", "μ = 0.5 + 1.7i + 0.5j: a real part and a j part at once, a little inside the boundary.",
                 "explored", m, [-0.988, 0.53, 0], False, TILT))
    m = mu_of(0, 1)
    out.append(P("Stretched in depth", "μ = 2i with the third map's step doubled (L = 2), so the rows of pearls stand twice as far apart in depth.",
                 "explored", m, [1, 1, 0], True, dict(yaw=0.5, pitch=0.5), L=2.0))
    return out


def check(p):
    k = p["k"]
    mu = [k["mx"], k["my"], k["mz"]]
    Pl = pearls(mu, k["L"], k["three"], eps=0.004 if not k["three"] else 0.008, stop_at=0.02)
    M = missed(mu, k["L"], k["three"], iters=k["iter"], n=12000)
    C = np.array([[k["cx"], k["cy"], k["cz"]]])
    d = float(kde(C, mu, k["L"], k["three"], 300)[0][0])
    p["checks"] = dict(pearls=int(len(Pl["r"])), overlap=round(Pl["overlap"], 4), shader_misses=round(M["share"], 4), de_at_centre=round(d, 3))
    return p["checks"]


def boundary():
    """Each cusp must sit on the edge of the family: at mu the list of pearls is finite and none cuts into
    another; 0.02 below mu either a pearl cuts into another or the list never ends (pearls pile up without
    limit, which a clean group cannot do above a given size)."""
    for p, q in [(0, 1), (1, 15), (1, 5), (1, 4), (3, 10), (1, 3), (5, 13), (8, 21), (2, 5), (1, 2)]:
        m = cusp(p, q)
        at = pearls([m.real, m.imag, 0.0], 1.0, False, eps=0.001, stop_at=0.01, max_pearls=60000)
        below = pearls([m.real, m.imag - 0.02, 0.0], 1.0, False, eps=0.001, stop_at=0.01, max_pearls=60000)
        broken = "a pearl cuts %.2f of its radius into another" % below["overlap"] if below["overlap"] > 0.01 else                  ("more than 60000 pearls and still growing" if not below["complete"] else "nothing found")
        ok = at["overlap"] < 1e-6 and at["complete"] and broken != "nothing found"
        print("%2d/%-2d mu = %.6f + %.6fi   at mu: %d pearls, deepest cut %.0e   0.02 below: %s   %s"
              % (p, q, m.real, m.imag, len(at["r"]), at["overlap"], broken, "ok" if ok else "FAILS"), flush=True)


def main():
    if "--boundary" in sys.argv:
        return boundary()
    ps = presets()
    bad = False
    for p in ps:
        c = check(p)
        ok = c["overlap"] <= 0.001 and c["shader_misses"] <= 0.002 and c["de_at_centre"] > 0.02
        bad |= not ok
        print("%-34s %-11s mu=(%.4f, %.4f, %.4f) three=%d L=%g  pearls %5d  overlap %.4f  shader misses %.4f  estimate at centre %.3f  %s"
              % (p["name"], p["source"], p["k"]["mx"], p["k"]["my"], p["k"]["mz"], p["k"]["three"], p["k"]["L"], c["pearls"], c["overlap"], c["shader_misses"], c["de_at_centre"], "ok" if ok else "FAILS"), flush=True)
    if "--check" in sys.argv:
        return
    free = [p for p in ps if not p["fixedR"]]
    fit(free, "build", target=0.66)
    for p in ps:
        if p.get("unbounded"):
            bad = True
            print("NOT BOUNDED:", p["name"])
    out = [dict(name=p["name"], note=p["note"], k=p["k"], cam=p["cam"], source=p["source"]) for p in ps]
    if bad:
        print("some presets fail: JSON not written")
        return
    with open(os.path.join(ROOT, "data", "klein-presets.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join("  " + json.dumps(o, ensure_ascii=False) for o in out) + "\n]\n")
    print("wrote data/klein-presets.json (%d presets)" % len(out))
    for p in ps:
        p["sub"] = "%s  R=%.3f" % (p["source"], p["k"]["invR"])
    render(ps, "final")


if __name__ == "__main__":
    main()
