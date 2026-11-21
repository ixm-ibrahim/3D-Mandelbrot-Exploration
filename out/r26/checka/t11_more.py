"""More attempts to break the arithmetic of the pictures.
M1  the diamond dragged in a flat picture (Julia shape; both pictures of Both; a zoomed picture): is c the point
    of the plane under the pointer (to a hundredth), and is the picture then the shape of that c?
M2  two pictures one above the other (a tall stage), 2D against the reference, 3D drawn
M3  a sharp screen (two device pixels to a pixel): the flat picture against the reference
M4  an equation that is not z^n + c, and a start value that is not 0: the whole shape keeps to the plain rule
    (the numbers do not change) and the page says so
M5  the 3D diamond when c is far out
"""
import json, time
import numpy as np
from clab import Lab, Log, u8
import cref, cpix

log = Log("t11_more")
defects = []
HELP = """
const glc = () => document.querySelector('canvas.learn-shape-gl');
const look3 = () => { const c = glc(); if (!c || c.hidden || !c.width) return { cover: -1, hash: 'none' };
  const t = window.__t2 || (window.__t2 = document.createElement('canvas')); t.width = 216; t.height = 128; const g = t.getContext('2d', { willReadFrequently: true }); g.drawImage(c, 0, 0, 216, 128);
  const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++;
  return { cover: +(n / (216 * 128)).toFixed(4), hash: hashOf(c), size: c.width + 'x' + c.height }; };
"""


def flat_check(lab, name, k, img=None):
    info = lab.js(cpix.INFO)
    S = cpix.Scene(info)
    if img is None: img = lab.grab("#learnShapeCanvas")
    r = cpix.check(S, img, k)
    log("      %s: flat picture against the reference at step %d: stage %d x %d, %s" % (name, k, S.W, S.H, json.dumps(r)))
    if r["miss"] or r["extra"] or r["inside"] < 0: defects.append("%s: flat picture wrong at step %d: %s" % (name, k, json.dumps(r)))
    return S


with Lab("r26-checka") as lab:
    lab.prelude += HELP
    log("M1. the diamond dragged")
    DRAG = """
      const [pane, tx, ty] = %s, cv = $('learnShapeCanvas');
      const st = L.shape.state(), d = st.diamonds[pane];
      ptr(cv, 'pointerdown', d[0], d[1]); ptr(cv, 'pointermove', (d[0] + tx) / 2, (d[1] + ty) / 2); await frame(); ptr(cv, 'pointermove', tx, ty); await frame(); await frame();
      const held = L.shape.state(); ptr(cv, 'pointerup', tx, ty); await sleep(250);
      const s = L.shape.state(), P = s.panes[pane], V = s.view2[P.kind], sc = 0.21 * Math.min(P.w, P.h) * V.zoom;
      return { from: d, c: s.c, want: [V.x + (tx - (P.x + P.w / 2)) / sc, V.y - (ty - (P.y + P.h / 2)) / sc], heldQuality: held.quality, dials: [$('learnShape-cxNum').value, $('learnShape-cyNum').value], diamondNow: s.diamonds[pane] };
    """
    for name, setup, pane, tx, ty in (
        ("Julia shape", "await shapeOn({ kind: 'j', space: 2, c: [-0.4, 0.3, 0], pos: 6 });", 0, 520.0, 170.0),
        ("Both, in the left (Mandelbrot) picture", "L.shape.set({ kind: 'both', space: 2, c: [-0.4, 0.3, 0], pos: 6 });", 0, 150.0, 300.0),
        ("Both, in the right (Julia) picture", "L.shape.set({ kind: 'both', space: 2, c: [-0.4, 0.3, 0], pos: 6 });", 1, 700.0, 180.0),
        ("Julia shape, zoomed in", "L.shape.set({ kind: 'j', space: 2, c: [0.1, 0.1, 0], pos: 6 }); await sleep(100); { const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect(); $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -600, clientX: b.left + 450, clientY: b.top + 250, bubbles: true, cancelable: true })); } await sleep(300);", 0, 300.0, 400.0),
    ):
        lab.js(setup + " await sleep(150); return 1;")
        r = lab.js(DRAG % json.dumps([pane, tx, ty]))
        err = max(abs(r["c"][0] - r["want"][0]), abs(r["c"][1] - r["want"][1]))
        log("   %s: dragged to pixel (%s, %s): c = %s, the plane's point under the pointer = (%.4f, %.4f), off by %.4f; dials show %s; the diamond now at %s" % (
            name, tx, ty, r["c"][:2], r["want"][0], r["want"][1], err, r["dials"], [round(x, 1) for x in r["diamondNow"]]))
        if err > 0.0051: defects.append("M1 %s: c is %s, the pointer is over (%.4f, %.4f)" % (name, r["c"][:2], r["want"][0], r["want"][1]))
        if [float(x.replace("−", "-")) for x in r["dials"]] != r["c"][:2]: defects.append("M1 %s: the dials show %s, c is %s" % (name, r["dials"], r["c"][:2]))
        flat_check(lab, "M1 " + name, 6)
        lab.js("$('learnShapeViewReset').click(); return 1;")
    # keys on the picture: arrows move c by 0.05
    r = lab.js("""L.shape.set({ kind: 'j', space: 2, c: [0, 0, 0], pos: 4 }); const cv = $('learnShapeCanvas'); cv.focus();
      const key = (k, o) => cv.dispatchEvent(new KeyboardEvent('keydown', Object.assign({ key: k, bubbles: true, cancelable: true }, o || {})));
      key('ArrowRight'); key('ArrowRight'); key('ArrowUp'); key('ArrowLeft', { shiftKey: true }); return L.shape.state().c;""")
    log("   arrow keys on the picture from c = 0: right, right, up, shift-left -> c = %s" % r)
    if r[:2] != [0.09, 0.05]: defects.append("M1: arrow keys moved c to %s, not (0.09, 0.05)" % r[:2])
    flat_check(lab, "M1 after the keys", 4)
    n = log.problems(lab)
    if n: defects.append("M1: console: %s" % lab.problems[:3])

    log("")
    log("M4. an equation that is not the plain one, a start value that is not 0")
    r = lab.js("""
      L.shape.set({ kind: 'both', space: 2, c: [-0.1226, 0.7449, 0], pos: 5 }); await sleep(100);
      const before = [b64(L.shape.mask2('m', 129, 2, 16)), b64(L.shape.mask2('j', 129, 2, 16)), b64(ckView().slice('m', [0, 0, 0], { z: 0.2, size: 65, half: 2, maxK: 16 })), LAB.learnShape3d.out([0.3, 0.2, 0.1], 'j', [-0.4, 0.3, 0.1], 16)];
      const eqWas = S.eq, z0Was = S.z0;
      S.eq = 'z^2 + z^3 + c'; S.z0 = '0.5'; go(); await sleep(600);
      const noteShown = $('learnEqNote').getClientRects().length > 0, note = $('learnEqNote').textContent;
      const after = [b64(L.shape.mask2('m', 129, 2, 16)), b64(L.shape.mask2('j', 129, 2, 16)), b64(ckView().slice('m', [0, 0, 0], { z: 0.2, size: 65, half: 2, maxK: 16 })), LAB.learnShape3d.out([0.3, 0.2, 0.1], 'j', [-0.4, 0.3, 0.1], 16)];
      const sentence = L.shape.goto(0).sentence;
      S.eq = eqWas; S.z0 = z0Was; go(); await sleep(400);
      return { same: before.map((x, i) => x === after[i]), noteShown, note, eq: [eqWas, z0Was], sentence, noteGone: $('learnEqNote').getClientRects().length === 0 };""")
    log("   with the equation z^2 + z^3 + c and the start value 0.5: flat masks and 3D numbers unchanged: %s; the note \"%s\" shown: %s; step 0 says: %s; gone again with the plain equation: %s" % (r["same"], r["note"], r["noteShown"], r["sentence"], r["noteGone"]))
    if not all(r["same"]) or not r["noteShown"]: defects.append("M4: another equation changes the whole shape's numbers, or the note is not shown: %s" % json.dumps(r))

    log("")
    log("M5. the 3D diamond when c is far out")
    r = lab.js("""L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0], pos: 0 }); await sleep(500); const a = L.shape.state();
      L.shape.set({ kind: 'j', space: 2, c: [7, 0, 0], pos: 0 }); await sleep(200); const b = L.shape.state();
      return { d3: a.diamonds, panes: a.panes, d2: b.diamonds };""")
    log("   c = (7, 0, 0): in 3D the diamond is drawn at %s on a stage of %s x %s; in 2D at %s" % (r["d3"], r["panes"][0]["w"], r["panes"][0]["h"], r["d2"]))
    lab.js("L.shape.set({ kind: 'j', space: 3, c: [7, 0, 0], pos: 0 }); await sleep(500); L.shape.state(); await sleep(200); return 1;")
    lab.shot("out/r26/checka/t11-M5-3d-c7-step0.png", "#stage")
    d = r["d3"][0]
    if d and (d[0] < 0 or d[0] > r["panes"][0]["w"] or d[1] < 0 or d[1] > r["panes"][0]["h"]):
        defects.append("M5: in 3D with c = (7, 0, 0) the diamond stands at pixel %s, off the stage (%s x %s), and its letter c is drawn alone at the stage's edge" % ([round(x) for x in d], r["panes"][0]["w"], r["panes"][0]["h"]))
    n = log.problems(lab)
    if n: defects.append("M4/M5: console: %s" % lab.problems[:3])

# ---------------------------------------------------------------- M2
log("")
log("M2. two pictures one above the other")
with Lab("r26-checka", size=(390, 1300)) as lab:      # (a window tall enough to hold the whole stage: a picture is taken of what is in the window)
    lab.prelude += HELP
    r = lab.js("""await shapeOn({ kind: 'both', space: 2, c: [-0.1226, 0.7449, 0], pos: 5 });
      const s = $('stage'); s.style.height = '620px'; s.style.aspectRatio = 'auto'; await sleep(500); scrollTo(0, 0); await sleep(200);
      const b = s.getBoundingClientRect(); if (b.bottom > innerHeight) fail('the stage does not fit the window: ' + b.bottom + ' > ' + innerHeight);
      const st = L.shape.state(); return { stage: [s.clientWidth, s.clientHeight], side: st.side, panes: st.panes };""")
    log("   stage made tall: %s" % json.dumps(r))
    if r["side"]:
        log("   (the pictures still stand side by side: this layout was not reached)")
    else:
        flat_check(lab, "M2 one above the other", 5)
        lab.js("L.shape.goto(11); return 1;")
        flat_check(lab, "M2 one above the other", 11)
        lab.save(lab.grab("#learnShapeCanvas"), "out/r26/checka/t11-M2-stacked-2d.png")
        r = lab.js("L.shape.set({ space: 3, pos: 5 }); await sleep(600); const st = L.shape.state(); await sleep(300); return { note: st.note, panes: st.panes, look: look3(), words: st.sentence, dia: st.diamonds };")
        log("   3D, one above the other: %s" % json.dumps(r))
        lab.save(lab.grab("#stage"), "out/r26/checka/t11-M2-stacked-3d.png")
        if r["note"] or r["look"]["cover"] <= 0: defects.append("M2: 3D one above the other: %s" % json.dumps(r))
        w = lab.js("L.shape.set({ space: 2, pos: 0 }); const a = L.shape.state().sentence; const b = L.shape.goto(1).sentence; const c = L.shape.goto(16).sentence; return [a, b, c];")
        for x in w: log("        " + x)
        if any(any(t in x for t in ("Left:", "Right:", "(left)", "(right)", "on the left", "on the right")) for x in w):
            defects.append("M2: with the pictures one above the other the sentences still say left and right: %s" % w)
    n = log.problems(lab)
    if n: defects.append("M2: console: %s" % lab.problems[:3])

# ---------------------------------------------------------------- M3
log("")
log("M3. a sharp screen (two device pixels to a pixel)")
with Lab("r26-checka") as lab:
    lab.prelude += HELP
    lab.page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=2, mobile=False)
    time.sleep(0.8)
    for kind, c, k in (("m", [0, 0, 0], 5), ("both", [-0.1226, 0.7449, 0], 8)):
        lab.js("await shapeOn({ kind: %s, space: 2, c: %s, pos: %d }); await sleep(300); return 1;" % (json.dumps(kind), json.dumps(c), k))
        dpr = lab.js("return [devicePixelRatio, $('learnShapeCanvas').width, $('learnShapeCanvas').clientWidth];")
        big = lab.grab("#learnShapeCanvas").astype(np.float64)
        if big.shape[1] == 2 * dpr[2]:
            img = (big[0::2, 0::2] + big[1::2, 0::2] + big[0::2, 1::2] + big[1::2, 1::2]) / 4
        else:
            img = big
        log("   devicePixelRatio %s, canvas buffer %s for a box of %s; screenshot %s x %s" % (dpr[0], dpr[1], dpr[2], big.shape[1], big.shape[0]))
        flat_check(lab, "M3 %s" % kind, k, img)
    r = lab.js("L.shape.set({ kind: 'both', space: 3, pos: 5 }); await sleep(700); const st = L.shape.state(); await sleep(300); return { note: st.note, look: look3(), q: st.three };")
    log("   3D on the sharp screen: %s" % json.dumps(r))
    if r["note"] or r["look"]["cover"] <= 0: defects.append("M3: 3D on a sharp screen: %s" % json.dumps(r))
    n = log.problems(lab)
    if n: defects.append("M3: console: %s" % lab.problems[:3])

log("")
log("DEFECTS: %d" % len(defects))
for d in defects: log("  " + d)
