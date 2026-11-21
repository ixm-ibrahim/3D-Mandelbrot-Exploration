"""The words of the 3D picture against its numbers, where I expected them to part:
(1) "Quaternions, 4D (slices)" with its dial w (where the slice sits on the fourth axis) off 0. The picture point p
    stands for a point of 4D that is further from the centre than p is, so the first step of a Mandelbrot shape
    (0 to its own c) already throws out a shell, and a Julia shape does not start as the whole ball.
    What do the sentences say?
(2) A 3D Julia shape of which nothing is left (c far out): the words at steps 1, 2 and 5, and the picture.
For each: points of the ball on a grid of 0.1 (my own orbit) that are left after 0, 1, 2 steps; the card's slice
at z = 0; the sentences; a picture.
"""
import json
from clab import Lab, Log

log = Log("t10_words3d")
defects = []
JS = """
const [id, moved, kind, c] = %s;
await shapeOn({ kind, space: 3, c, pos: 0 }); await pickAp(id); dialsBack(id); if (moved) { Object.assign(S.param[id], moved); go(); }
L.shape.set({ kind, space: 3, c, pos: 0 }); await sleep(200);
let n = 0; const left = [0, 0, 0, 0];
for (let i = 0; i <= 40; i++) for (let j = 0; j <= 40; j++) for (let k = 0; k <= 40; k++) { const p = [-2 + i * 0.1, -2 + j * 0.1, -2 + k * 0.1]; if (Math.hypot(...p) > 2) continue; n++; const o = ckOut3(p, kind, c, 16), t = LAB.learnShape3d.out(p, kind, c, 16); if (o !== t) fail('twins differ'); if (o > 0) left[0]++; if (o > 1) left[1]++; if (o > 2) left[2]++; if (o > 16) left[3]++; }
const g = ckView().slice(kind, c, { z: 0, half: 2, size: 129, maxK: 16 }); let sb = 0; const sl = [0, 0, 0];
for (let r = 0; r < 129; r++) for (let q = 0; q < 129; q++) { const p = ckPoint(r, q, 129, 2, 0); if (Math.hypot(...p) > 2) continue; sb++; const o = g[r * 129 + q]; if (o > 0) sl[0]++; if (o > 1) sl[1]++; if (o > 2) sl[2]++; }
const words = [];
for (const pos of [0, 0.5, 1, 2, 5]) { L.shape.goto(pos); await sleep(60); const s = L.shape.state(); words.push(pos + ': ' + s.sentence); }
return { ballPoints: n, left, sliceBall: sb, sliceLeft: sl, words, notice: $('learnShapeNotice').textContent };
"""
CASES = [
    ("quat4", None, "m", [0, 0, 0], 1),
    ("quat4", {"w": 0.3}, "m", [0, 0, 0], 1),
    ("quat4", {"w": 1.5}, "m", [0, 0, 0], 1),
    ("quat4", {"w": 1.5}, "j", [-0.4, 0.3, 0], 0),
    ("quat4", {"w": 0.3}, "j", [-0.4, 0.3, 0], 0),
    ("quat4", {"w": 1.5}, "both", [-0.4, 0.3, 0], 1),
    ("mercator", None, "j", [7, 0, 0], 2),
    ("lathe", None, "j", [2.5, 2.5, 0], 5),
]
with Lab("r26-checka") as lab:
    for id_, mv, kind, c, shot_at in CASES:
        kd = "m" if kind == "both" else kind
        r = lab.js(JS % json.dumps([id_, mv, kd, c]))
        if kind == "both":
            r["words"] = lab.js("const out = []; L.shape.set({ kind: 'both' }); for (const pos of [0, 0.5, 1, 2, 5]) { L.shape.goto(pos); await sleep(60); out.push(pos + ': ' + L.shape.state().sentence); } return out;")
        log("%s %s, %s, c %s" % (id_, json.dumps(mv) if mv else "(dials at their starting values)", kind, c))
        log("    of %d grid points of the big ball: in shape 0: %d, left after 1 step: %d, after 2: %d, after 16: %d;  the card's slice at z = 0: %d points in the big circle, in shape 0: %d, after 1: %d, after 2: %d" % (
            r["ballPoints"], r["left"][0], r["left"][1], r["left"][2], r["left"][3], r["sliceBall"], r["sliceLeft"][0], r["sliceLeft"][1], r["sliceLeft"][2]))
        for w in r["words"]: log("        " + w)
        lab.js("L.shape.goto(%d); await sleep(500); L.shape.state(); await sleep(250); return 1;" % shot_at)
        name = "out/r26/checka/t10-%s-%s-%s-step%d.png" % (id_, "w%s" % mv["w"] if mv and "w" in mv else "c%s" % c[0], kind, shot_at)
        lab.shot(name, "#stage")
        log("    picture: " + name.split("/")[-1])
        n, L0, L1 = r["ballPoints"], r["left"][0], r["left"][1]
        if kd == "m":
            if "still the whole big ball" in r["words"][2] and L1 < n:
                defects.append("%s %s, %s: at step 1 the sentence says \"still the whole big ball\", but of %d grid points of the ball only %d are left after step 1 (%.0f %%)" % (id_, json.dumps(mv), kind, n, L1, 100.0 * L1 / n))
            if "nothing is thrown out" in r["words"][1] and L1 < n:
                defects.append("%s %s, %s: during step 1 the sentence says nothing is thrown out, but %d of %d grid points of the ball are" % (id_, json.dumps(mv), kind, n - L1, n))
        else:
            if r["words"][0].startswith("The big ball") and L0 < n:
                defects.append("%s %s, Julia shape: at step 0 the sentence says \"The big ball. Every point is a place to start from\", but the shape drawn is smaller: %d of %d grid points of the ball (%.0f %%)" % (id_, json.dumps(mv), L0, n, 100.0 * L0 / n))
            if L1 == 0 and "nothing is left" not in r["words"][2]:
                defects.append("%s, Julia shape, c %s: nothing is left after step 1 (0 of %d grid points), the sentence at steps 1, 2, 5: %s" % (id_, c, n, " | ".join(w.split(": ", 1)[1] for w in r["words"][2:])))
        lab.js("dialsBack(AP().id); go(); return 1;")
    lab.js("await pickAp('mercator'); L.shape.set({ kind: 'm', c: [-0.4, 0.3, 0], pos: 0 }); return 1;")
    log.problems(lab)
log("DEFECTS: %d" % len(defects))
for d in defects: log("  " + d)
