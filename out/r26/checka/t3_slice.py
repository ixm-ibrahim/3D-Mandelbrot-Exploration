"""Check 2: the 3D numbers.
view.slice (the graphics card, the program the picture is drawn with) against
  T = learnShape3d.out (builder three's JavaScript twin), and against
  M = my own orbit (c_prelude.js, ckOut3), written from the lab's shader text and driven with the lab's MATH / CARRY,
point for point, both kinds, at z = 0, 0.2 and 0.5, for every approach at the power 2 and for chosen approaches at
other powers, with modifiers, and with their dials moved off the starting values.
T against M must agree everywhere (both are JavaScript with the lab's MATH). Where the card differs from M the point
is looked at again: if M gives the card's number somewhere within 1e-4 of it, the point lies within a hair of a skin.
"""
import json, sys, time
from clab import Lab, Log

log = Log("t3_slice" + (("-" + sys.argv[1]) if len(sys.argv) > 1 else ""))
SIZE, K = 129, 16
CASES = [["m", [0, 0, 0]], ["j", [-1, 0, 0]], ["j", [-0.1226, 0.7449, 0]], ["j", [-0.3, 0.2, 0.35]]]
ZS = [0, 0.2, 0.5]
ALL = ["mercator", "fold", "lathe", "tilt", "bulb", "classic", "split", "softfold", "axisbulb", "pillow", "quat4", "rotor", "rotorframe",
       "kleinsq", "kleinsq2", "sqpillow", "turnaway", "turnalong", "windsq", "alongonce", "pulledplane"]
MOVED = {
    "mercator": {"turn": 25, "lift": 0.3}, "pulledplane": {"hold": 0.4, "ease": 0.3, "cpull": 30}, "fold": {"planes": 3, "lift": -0.2},
    "quat4": {"w": 0.3, "tilt": 20, "cw": 0.4}, "rotor": {"lon": 30, "lat": 40}, "lathe": {"spin": 3}, "tilt": {"tilt": -70},
    "bulb": {"lat": 20, "lon": -35}, "axisbulb": {"k": 2, "wob": 0.5, "reach": 60, "pinch": 1}, "softfold": {"planes": 3, "blend": 0.1, "curve": 1, "mix": 2},
    "pillow": {"layout": 1}, "classic": {"theta": 15, "phi": 40},
}
# (name, approaches, power, |x||y||z|, flips of y and z, dials moved?)
CONFIGS = [
    ("power 2", ALL, 2, [0, 0, 0], [0, 0], False),
    ("power 3", ["mercator", "fold", "lathe", "bulb", "alongonce", "pulledplane", "sqpillow", "turnalong", "quat4", "softfold", "windsq", "split"], 3, [0, 0, 0], [0, 0], False),
    ("power 2.5", ["mercator", "lathe", "bulb", "alongonce", "pulledplane", "split", "fold", "turnaway"], 2.5, [0, 0, 0], [0, 0], False),
    ("power 2, |x| and flip y", ["mercator", "fold", "alongonce", "pulledplane", "lathe", "windsq"], 2, [1, 0, 0], [1, 0], False),
    ("power 2, |z| and flip z", ["mercator", "fold", "alongonce", "pulledplane", "bulb", "rotorframe"], 2, [0, 0, 1], [0, 1], False),
    ("power 2, dials moved", list(MOVED), 2, [0, 0, 0], [0, 0], True),
    ("power 3, dials moved", ["mercator", "pulledplane", "quat4", "fold"], 3, [0, 0, 0], [0, 0], True),
    ("power -2", ["mercator", "lathe", "alongonce", "pulledplane", "split"], -2, [0, 0, 0], [0, 0], False),
    ("power 0.5", ["mercator", "lathe", "alongonce", "pulledplane"], 0.5, [0, 0, 0], [0, 0], False),
]
if len(sys.argv) > 1:
    CONFIGS = [c for c in CONFIGS if sys.argv[1] in c[0].replace(" ", "").replace(",", "")] or CONFIGS

JS = """
const [id, n, abs, flip, moved, CASES, ZS, SIZE, K] = %s;
await pickAp(id); dialsBack(id); setRule(n, abs, flip); if (moved) dials(id, moved);
const v = ckView(), T3 = LAB.learnShape3d, rows = [], odd = [];
if (!v) fail('no 3D view');
const near = (p, kind, c, want) => {
  for (const e of [1e-6, 1e-5, 1e-4]) for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let d = -1; d <= 1; d++) {
    if (!a && !b && !d) continue;
    if (ckOut3([p[0] + a * e, p[1] + b * e, p[2] + d * e], kind, c, K) === want) return e;
  }
  return 0;
};
for (const [kind, c] of CASES) for (const z of ZS) {
  const g = v.slice(kind, c, { z, half: 2, size: SIZE, maxK: K });
  if (!g) fail('no slice for ' + id + ': ' + T3.note());
  let dT = 0, dM = 0, dTM = 0, un = 0, in1 = 0, in5 = 0, inK = 0, ball = 0;
  for (let row = 0; row < SIZE; row++) for (let col = 0; col < SIZE; col++) {
    const p = ckPoint(row, col, SIZE, 2, z), i = row * SIZE + col, t = T3.out(p, kind, c, K), m = ckOut3(p, kind, c, K);
    if (m > 0) ball++; if (m > 1) in1++; if (m > 5) in5++; if (m > K) inK++;
    if (t !== m) { dTM++; if (odd.length < 6) odd.push({ what: 'T and M differ', kind, c, p, T: t, M: m, card: g[i] }); }
    if (g[i] !== t) dT++;
    if (g[i] !== m) { dM++; if (!near(p, kind, c, g[i])) { un++; if (odd.length < 12) odd.push({ what: 'card differs from M, no skin within 1e-4', kind, c, p, T: t, M: m, card: g[i] }); } }
  }
  rows.push([kind, c, z, dT, dM, dTM, un, ball, in1, in5, inK]);
}
if (moved) dialsBack(id);
return { id, ok: T3.ok(), rows, odd };
"""

t_start = time.time()
grand = dict(points=0, dT=0, dM=0, dTM=0, un=0, slices=0)
defects = []
with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'm', space: 2, pos: 2 }); return 1;")     # Learn on: the lab's own solid is left alone
    for name, ids, n, ab, fl, moved in CONFIGS:
        log("")
        log("== %s: slices of %d x %d points, 16 steps; per slice: card vs T / card vs M / T vs M / not within a hair" % (name, SIZE, SIZE))
        for id_ in ids:
            mv = MOVED.get(id_) if moved else None
            t0 = time.time()
            try:
                r = lab.js(JS % json.dumps([id_, n, ab, fl, mv, CASES, ZS, SIZE, K]))
            except Exception as e:
                log("  %-12s FAILED: %s" % (id_, str(e)[:300])); defects.append("%s, %s: %s" % (name, id_, str(e)[:200])); continue
            cells = []
            s = dict(dT=0, dM=0, dTM=0, un=0)
            for kind, c, z, dT, dM, dTM, un, ball, in1, in5, inK in r["rows"]:
                grand["points"] += SIZE * SIZE; grand["slices"] += 1
                for key, val in (("dT", dT), ("dM", dM), ("dTM", dTM), ("un", un)):
                    grand[key] += val; s[key] += val
                cells.append("%s%s z=%s: %d/%d/%d/%d (in ball %d, left after 1, 5, 16: %d %d %d)" % (kind, "" if kind == "m" else str(c), z, dT, dM, dTM, un, ball, in1, in5, inK))
            log("  %-12s%s card vs T %d, card vs M %d, T vs M %d, not within a hair %d   (%.1f s)" % (id_, (" " + json.dumps(mv)) if mv else "", s["dT"], s["dM"], s["dTM"], s["un"], time.time() - t0))
            for c in cells:
                log("      " + c)
            for o in r["odd"]:
                log("      ODD: " + json.dumps(o))
            if s["dTM"]: defects.append("%s, %s: learnShape3d.out and my MATH/CARRY orbit differ at %d points" % (name, id_, s["dTM"]))
            if s["un"]: defects.append("%s, %s: the card's slice differs from MATH/CARRY at %d points that are not within 1e-4 of a skin" % (name, id_, s["un"]))
    lab.js("await pickAp('mercator'); setRule(2, [0,0,0], [0,0]); return 1;")
    log("")
    log.problems(lab)
log("")
log("TOTAL: %d slices, %d points; card vs T %d, card vs M %d, T vs M %d, not within a hair of a skin %d   (%.0f s)" % (
    grand["slices"], grand["points"], grand["dT"], grand["dM"], grand["dTM"], grand["un"], time.time() - t_start))
log("DEFECTS: %d" % len(defects))
for d in defects:
    log("  " + d)
