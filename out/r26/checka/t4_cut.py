"""Check 2, last part: "for an approach that keeps the flat picture and a c in the flat plane, the slice at z = 0
equals the flat mask of the same step", and what the page SAYS about it.
For every approach: view.slice at z = 0 (the card) against my Python flat reference (cref.py), and against the
page's own mask2; beside it whether the 3D "What to notice" paragraph shows the sentence
"cutting the 3D shape through the middle (at z = 0) gives exactly the 2D shape of the same step".
  shown   -> the slice must be the flat shape (but for points within a hair of a skin);
  not shown and they agree -> noted, not a defect (the round asks for the sentence only where it was checked).
Then the same with dials moved, a little and a lot, and with a c off the flat plane.
"""
import json, sys, time
import numpy as np
from clab import Lab, Log, u8
import cref

log = Log("t4_cut")
K = 16
ALL = ["mercator", "fold", "lathe", "tilt", "bulb", "classic", "split", "softfold", "axisbulb", "pillow", "quat4", "rotor", "rotorframe",
       "kleinsq", "kleinsq2", "sqpillow", "turnaway", "turnalong", "windsq", "alongonce", "pulledplane"]
JS = """
const [id, n, abs, flip, moved, kind, c, SIZE] = %s;
await pickAp(id); dialsBack(id); if (moved) Object.assign(S.param[id], moved); setRule(n, abs, flip);
const st = L.shape.set({ kind, c, space: 3, pos: 5 });
await sleep(30);
const txt = $('learnShapeNotice').textContent, shown = txt.includes('cutting the 3D shape'), v = ckView();
const k1 = kind === 'both' ? ['m', 'j'] : [kind], out = [];
for (const kd of k1) { const g = v.slice(kd, c, { z: 0, half: 2, size: SIZE, maxK: 16 }); if (!g) fail('no slice'); const f = L.shape.mask2(kd, SIZE, 2, 16); let d = 0; for (let i = 0; i < g.length; i++) if (g[i] !== f[i]) d++; out.push([kd, b64(g), d]); }
if (moved) { dialsBack(id); go(); }
return { shown, out, note: st.note, sentenceVisible: $('learnShapeNotice').getClientRects().length > 0, txt: shown ? txt.slice(txt.indexOf('With this approach')) : '' };
"""
defects, notes = [], []


def one(lab, id_, n, ab, fl, moved, kind, c, size=129):
    r = lab.js(JS % json.dumps([id_, n, ab, fl, moved, kind, c, size]))
    res = []
    for kd, g64, dpage in r["out"]:
        g = u8(g64).reshape(size, size).astype(np.int32)
        ref = cref.mask(kd, c, n, size, 2.0, K, absx=bool(ab[0]), absy=bool(ab[1]), flipy=bool(fl[0])).astype(np.int32)
        diff = g != ref; nd = int(diff.sum()); far = 0
        if nd:
            px, py = cref.grid(size, 2.0)
            X, Y = px[diff], py[diff]
            near = np.zeros(nd, dtype=bool)                       # is any skin of the flat shapes within 1e-4?
            base = ref[diff]
            for e in (1e-6, 1e-5, 1e-4):
                for dx in (-e, 0, e):
                    for dy in (-e, 0, e):
                        if dx or dy:
                            near |= cref.out_points(X + dx, Y + dy, kd, c, n, bool(ab[0]), bool(ab[1]), bool(fl[0]), K) != base
            far = int((~near).sum())
        res.append((kd, nd, far, dpage))
    return r["shown"], res, r


t0 = time.time()
with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'm', space: 3, pos: 5 }); return 1;")
    CONF = [("power 2", 2, [0, 0, 0], [0, 0], 257), ("power 3", 3, [0, 0, 0], [0, 0], 129), ("power 2.5", 2.5, [0, 0, 0], [0, 0], 129),
            ("power 2, |x| and flip y", 2, [1, 0, 0], [1, 0], 129), ("power 2, |z| and flip z", 2, [0, 0, 1], [0, 1], 129), ("power -2", -2, [0, 0, 0], [0, 0], 129)]
    KINDS = [("m", [0, 0, 0]), ("j", [-1, 0, 0]), ("j", [-0.1226, 0.7449, 0]), ("both", [-0.1226, 0.7449, 0])]
    for cname, n, ab, fl, size in CONF:
        log("")
        log("== %s, dials at their starting values, %d x %d points. Per picture: points where the card's slice at z = 0 differs from my flat reference / of those, no flat skin within 1e-4 / differs from the page's mask2" % (cname, size, size))
        for id_ in ALL:
            cells = []; shows = []; worst_far = 0; tot = 0
            for kind, c in KINDS:
                shown, res, r = one(lab, id_, n, ab, fl, None, kind, c, size)
                shows.append(shown)
                for kd, nd, far, dpage in res:
                    cells.append("%s%s%s: %d/%d/%d" % (kind if kind != "both" else "both:", kd if kind == "both" else "", "" if kd == "m" else str(c[:2]), nd, far, dpage))
                    worst_far = max(worst_far, far); tot += nd
                    if shown and far:
                        defects.append("%s, %s, %s: the sentence about the cut is shown, but the slice at z = 0 differs from the flat shape at %d of %d points, %d of them with no skin within 1e-4" % (cname, id_, kind, nd, size * size, far))
            flag = "shown" if all(shows) else "NOT shown" if not any(shows) else "shown for " + ",".join(k for (k, _), s in zip(KINDS, shows) if s)
            keeps = worst_far == 0
            if keeps and not all(shows): notes.append("%s, %s: the slice IS the flat shape here, and the sentence is %s" % (cname, id_, flag))
            log("  %-12s sentence %-10s %s   %s" % (id_, flag, "keeps the flat picture" if keeps else "does NOT keep it", "; ".join(cells)))

    log("")
    log("== dials moved, power 2 (257 x 257 points); c off the flat plane")
    MOVES = [("mercator", {"lift": 0.01}), ("mercator", {"lift": 0.05}), ("mercator", {"lift": 0.3}), ("mercator", {"turn": 1}), ("mercator", {"turn": 25}),
             ("fold", {"planes": 3}), ("fold", {"lift": 0.02}), ("lathe", {"spin": 3}), ("lathe", {"spin": 2}), ("tilt", {"tilt": -70}), ("bulb", {"lat": 2}), ("bulb", {"lon": 2}),
             ("bulb", {"lat": 20, "lon": -35}), ("quat4", {"w": 0.05}), ("quat4", {"w": 0.3, "tilt": 20}), ("quat4", {"cw": 0.4}), ("rotor", {"lon": 0, "lat": 0}),
             ("rotor", {"lon": 30, "lat": 40}), ("pulledplane", {"hold": 0.4, "ease": 0.3, "cpull": 30}), ("axisbulb", {"k": 2, "wob": 0.5}), ("softfold", {"planes": 3, "blend": 0.1}),
             ("classic", {"theta": 90}), ("pillow", {"layout": 1})]
    for id_, mv in MOVES:
        cells = []; shows = []; worst_far = 0
        for kind, c in KINDS[:3]:
            shown, res, r = one(lab, id_, 2, [0, 0, 0], [0, 0], mv, kind, c, 257)
            shows.append(shown)
            for kd, nd, far, dpage in res:
                cells.append("%s%s: %d/%d/%d" % (kd, "" if kd == "m" else str(c[:2]), nd, far, dpage)); worst_far = max(worst_far, far)
                if shown and far:
                    defects.append("%s %s, %s%s: the sentence about the cut is shown (\"exactly the 2D shape\"), but the slice at z = 0 differs from the flat shape at %d of %d points, %d of them with no skin within 1e-4" % (id_, json.dumps(mv), kind, "" if kind == "m" else " c=%s" % c[:2], nd, 257 * 257, far))
        flag = "shown" if all(shows) else "NOT shown" if not any(shows) else "shown for " + ",".join(k + str(c[:2]) for (k, c), s in zip(KINDS, shows) if s)
        if worst_far == 0 and not all(shows): notes.append("%s %s: the slice IS the flat shape, and the sentence is %s" % (id_, json.dumps(mv), flag))
        log("  %-12s %-42s sentence %-10s %s   %s" % (id_, json.dumps(mv), flag, "keeps the flat picture" if worst_far == 0 else "does NOT keep it", "; ".join(cells)))
    # a c off the flat plane: the sentence must not be said for a Julia shape or for Both
    for id_ in ("mercator", "lathe", "alongonce"):
        for kind in ("m", "j", "both"):
            for cz in (0.2, 0.01):
                r = lab.js(JS % json.dumps([id_, 2, [0, 0, 0], [0, 0], None, kind, [-0.1226, 0.7449, cz], 65]))
                log("  %-12s c = (-0.1226, 0.7449, %s), %-4s: sentence %s" % (id_, cz, kind, "shown: " + r["txt"] if r["shown"] else "not shown"))
                if r["shown"] and kind != "m": defects.append("%s, %s, c off the flat plane by %s: the sentence about the cut is shown" % (id_, kind, cz))
    lab.js("await pickAp('mercator'); setRule(2, [0,0,0], [0,0]); L.shape.set({ c: [-0.4, 0.3, 0], kind: 'm' }); return 1;")
    log("")
    log.problems(lab)

log("")
log("NOTES (not defects): %d" % len(notes))
for d in notes: log("  " + d)
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)
