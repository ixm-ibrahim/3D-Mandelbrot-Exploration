"""Small things left over.
(a) Outside Learn the page is the frozen page: the opening picture and the Julia tab, stage pixels on both pages.
(b) The words the new part puts on the page: none of the words the round forbids.
(c) The named values of c and "Use the c of the Julia tab": c is what the button says, and the names are shown only
    for the plain power 2.
(d) The handle the contract promises.
"""
import json, re, time
import numpy as np
from clab import Lab, Log

log = Log("t12_rest")
defects = []
FORBID = ["iterate", "iteration", "escape", "bailout", "radius of escape", "preimage", "level set", "orbit count", "potential", "membership", "sample", "voxel", "shader", "mesh", "render"]

# (a)
pics = {}
for page in ("r26-checka-base", "r26-checka"):
    with Lab(page) as lab:
        lab.idle(120); time.sleep(0.5)
        a = lab.grab("#stage")
        lab.js("$('mode-j').click(); return 1;"); time.sleep(0.5); lab.idle(120); time.sleep(0.5)
        b = lab.grab("#stage")
        st = lab.js("return [S.mode, S.n, S.approach, document.querySelectorAll('#sections > details').length, Object.keys(LAB).length];")
        pics[page] = (a, b, st, list(lab.problems))
a0, b0, s0, p0 = pics["r26-checka-base"]; a1, b1, s1, p1 = pics["r26-checka"]
d1 = -1 if a0.shape != a1.shape else int((a0 != a1).any(-1).sum()); d2 = -1 if b0.shape != b1.shape else int((b0 != b1).any(-1).sum())
log("(a) opening picture: %d of %d stage pixels differ between the frozen page and this page; Julia tab: %d differ. Console: frozen %d, this page %d. (state: %s / %s)" % (d1, a0.shape[0] * a0.shape[1], d2, len(p0), len(p1), s0, s1))
if d1 or d2 or p1: defects.append("(a) outside Learn the stage differs from the frozen page: opening %d pixels, Julia tab %d pixels; console %s" % (d1, d2, p1[:2]))

with Lab("r26-checka") as lab:
    # (b)
    r = lab.js("""
      await shapeOn({ kind: 'm', space: 2, pos: 0 });
      const texts = new Set(), add = t => { if (t && t.trim()) texts.add(t.trim()); };
      const grab = () => { for (const e of document.querySelectorAll('#learnShapeBar, #learnFollow, .learn-only-shape, #learnShapeNote, #learnHint, #learnShapeCanvas, #learnPanel summary')) { add(e.textContent); for (const a of ['aria-label', 'title', 'aria-valuetext']) { add(e.getAttribute(a)); for (const c of e.querySelectorAll('[' + a + ']')) add(c.getAttribute(a)); } } };
      for (const n of [2, 3, 2.5, -2]) { setRule(n, [0,0,0], [0,0]);
        for (const space of [2, 3]) for (const kind of ['m', 'j', 'both']) for (const c of [[-0.4, 0.3, 0], [7, 0, 0], [0.2, 0.1, 0.4]]) { L.shape.set({ kind, space, c });
          for (const pos of [0, 0.5, 1, 1.5, 2, 7, 7.5, 16]) { L.shape.goto(pos); add(L.shape.state().sentence); grab(); } } }
      setRule(2, [1,0,0], [0,0]); L.shape.set({ kind: 'both', space: 2, c: [-0.4, 0.3, 0] }); L.shape.goto(16); add(L.shape.state().sentence); grab(); setRule(2, [0,0,0], [0,0]);
      return [...texts];""")
    hits = []
    for t in r:
        low = t.lower()
        for w in FORBID:
            if re.search(r"\b" + re.escape(w), low):
                hits.append((w, t[:160]))
    log("(b) %d different texts of the new part read (sentences at 8 places, 4 powers, 3 values of c, both spaces, three kinds; panel, transport, labels, titles): forbidden words found: %d %s" % (len(r), len(hits), hits[:6]))
    if hits: defects.append("(b) forbidden words on the page: %s" % hits[:6])
    longest = max((t for t in r if len(t) < 400), key=len)
    # (c)
    r = lab.js("""
      L.shape.set({ kind: 'j', space: 2, pos: 16 }); const out = [];
      for (const b of document.querySelectorAll('#learnShapeCs .learn-shape-value')) { b.click(); await sleep(80); const s = L.shape.state(); out.push([b.textContent, s.c, b.lastChild.getClientRects().length > 0]); }
      setRule(3, [0,0,0], [0,0]); await sleep(100); const named3 = [...document.querySelectorAll('#learnShapeCs .learn-shape-value')].map(b => b.lastChild.getClientRects().length > 0);
      setRule(2, [1,0,0], [0,0]); await sleep(100); const namedAbs = [...document.querySelectorAll('#learnShapeCs .learn-shape-value')].map(b => b.lastChild.getClientRects().length > 0);
      setRule(2, [0,0,0], [0,0]);
      S.c = [0.285, 0.01, 0.2]; $('learnShapeJuliaC').click(); await sleep(80); const j2 = L.shape.state().c; L.shape.set({ space: 3 }); $('learnShapeJuliaC').click(); await sleep(200); const j3 = L.shape.state().c; S.c = [-1, 0, 0];
      // the dials of c
      L.shape.set({ space: 3, kind: 'j' }); const e = $('learnShape-cz'); e.value = 0.37; e.dispatchEvent(new Event('input', { bubbles: true })); await sleep(100); const cz = L.shape.state().c;
      L.shape.set({ space: 2 }); await sleep(100); const czShown2D = $('learnShape-cz').getClientRects().length > 0;
      return { out, named3, namedAbs, juliaC: [j2, j3], cz, czShown2D };""")
    log("(c) named values: %s" % json.dumps(r["out"], ensure_ascii=False))
    log("    names shown at power 3: %s; with |x| ticked: %s; \"Use the c of the Julia tab\" with the Julia tab's c at (0.285, 0.01, 0.2): 2D -> %s, 3D -> %s; dial c along z set to 0.37 -> c = %s; that dial shown on the 2D page: %s" % (
        r["named3"], r["namedAbs"], r["juliaC"][0], r["juliaC"][1], r["cz"], r["czShown2D"]))
    want = [[-1, 0, 0], [-0.1226, 0.7449, 0], [0, 1, 0], [0, 0, 0]]
    if [x[1] for x in r["out"]] != want or not all(x[2] for x in r["out"]) or any(r["named3"]) or any(r["namedAbs"]): defects.append("(c) named values of c: %s" % json.dumps(r))
    if r["juliaC"][0] != [0.285, 0.01, 0.2] or r["juliaC"][1] != [0.285, 0.01, 0.2] or r["cz"][2] != 0.37 or r["czShown2D"]: defects.append("(c) the c of the Julia tab or the z dial: %s" % json.dumps(r))
    # (d)
    r = lab.js("""const s = L.shape.state(), v = LAB.learnShape3d; return { shape: Object.keys(L.shape), state: Object.keys(s), three: Object.keys(v), view: Object.keys(ckView()), ok: v.ok(), note: v.note(), steps: s.steps };""")
    log("(d) LEARN.shape: %s; state(): %s; learnShape3d: %s; a view: %s; ok() %s, note() %r; steps %s" % (r["shape"], r["state"], r["three"], r["view"], r["ok"], r["note"], r["steps"]))
    need = ["on", "kind", "space", "c", "pos", "step", "playing", "steps", "sentence", "note", "panes", "threeOk"]
    miss = [k for k in need if k not in r["state"]] + [k for k in ("set", "state", "play", "pause", "goto", "out2", "mask2") if k not in r["shape"]] + [k for k in ("make", "out", "ok", "note") if k not in r["three"]] + [k for k in ("canvas", "draw", "slice", "dispose") if k not in r["view"]]
    if miss: defects.append("(d) the handle lacks: %s" % miss)
    log("    the longest text read (%d letters): %s" % (len(longest), longest))
    n = log.problems(lab)
    if n: defects.append("console: %s" % lab.problems[:3])
log("DEFECTS: %d" % len(defects))
for d in defects: log("  " + d)
