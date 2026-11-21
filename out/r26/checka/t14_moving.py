"""The pictures while something moves.
(1) The coarse flat picture, drawn while the diamond is held: is it still the shape (power 2, and power 2.5 where
    the page draws one sample to two pixels)? The pointer is pressed on the diamond, moved, and NOT let go.
(2) A dial of the approach played by the lab's own Play button next to it, with the 3D whole shape on show: does
    the picture follow, and does it stop when the dial stops?
"""
import json, time
import numpy as np
from clab import Lab, Log
import cpix

log = Log("t14_moving")
defects = []
with Lab("r26-checka") as lab:
    for n in (2, 2.5):
        lab.js("""await shapeOn({ kind: 'j', space: 2, c: [-0.4, 0.3, 0], pos: 4 }); setRule(%s, [0,0,0], [0,0]); await sleep(300); L.shape.state();
          const cv = $('learnShapeCanvas'), d = L.shape.state().diamonds[0];
          ptr(cv, 'pointerdown', d[0], d[1]); ptr(cv, 'pointermove', d[0] + 40, d[1] + 25); await frame(); ptr(cv, 'pointermove', d[0] + 83, d[1] + 52); await frame(); await frame(); return 1;""" % n)
        info = lab.js(cpix.INFO)
        S = cpix.Scene(info)
        img = lab.grab("#learnShapeCanvas")
        r = cpix.check(S, img, 4)
        q = info["st"]["quality"]; ms = info["st"]["ms"]
        log("power %s, diamond held at c = %s: the page says quality '%s', %s samples to a pixel each way; against the reference at step 4: %s" % (n, info["st"]["c"][:2], q, ms["mapDens"], json.dumps(r)))
        lab.save(img, "out/r26/checka/t14-held-power%s.png" % n)
        if r["miss"] or r["extra"]: defects.append("power %s: the coarse picture drawn while the diamond is held is not the shape: %s" % (n, json.dumps(r)))
        lab.js("const cv = $('learnShapeCanvas'); ptr(cv, 'pointerup', 0, 0); await sleep(300); return 1;")
        info = lab.js(cpix.INFO); S = cpix.Scene(info)
        r = cpix.check(S, lab.grab("#learnShapeCanvas"), 4)
        log("    let go: quality '%s', %s samples to a pixel; against the reference: %s" % (info["st"]["quality"], info["st"]["ms"]["mapDens"], json.dumps(r)))
        if r["miss"] or r["extra"]: defects.append("power %s: after letting go the picture is not the shape: %s" % (n, json.dumps(r)))
    lab.js("setRule(2, [0,0,0], [0,0]); return 1;")
    # (2)
    r = lab.js("""
      const glc = () => document.querySelector('canvas.learn-shape-gl');
      L.shape.set({ kind: 'm', space: 3, pos: 4 }); await pickAp('mercator'); await sleep(500); L.shape.state(); await sleep(200);
      const out = { start: [S.param.mercator.lift, hashOf(glc())], during: [] };
      const btn = $('par-mercator-liftPlay'); out.label = btn.textContent + ' / ' + (btn.title || btn.getAttribute('aria-label'));
      btn.click();
      for (let i = 0; i < 6; i++) { await sleep(350); out.during.push([+S.param.mercator.lift.toFixed(3), hashOf(glc()), L.shape.state().quality]); }
      btn.click(); await sleep(700); const a = [S.param.mercator.lift, hashOf(glc())]; await sleep(500); const b = [S.param.mercator.lift, hashOf(glc())];
      out.stopped = [a, b]; out.sentence = L.shape.state().sentence; out.notice = $('learnShapeNotice').textContent.includes('cutting the 3D shape');
      dialsBack('mercator'); await sleep(300);
      return out;""")
    log("the dial Lift of \"Sphere inversions, one plane\" played by its own button (%s):" % r["label"])
    log("   start: %s" % r["start"])
    for row in r["during"]: log("   while it plays: lift %s, picture %s, %s" % tuple(row))
    log("   stopped: %s then %s; the sentence about the cut shown with the lift off 0: %s" % (r["stopped"][0], r["stopped"][1], r["notice"]))
    hs = [row[1] for row in r["during"]]; ls = [row[0] for row in r["during"]]
    if len(set(ls)) > 2 and len(set(hs)) < len(set(ls)) - 1: defects.append("the 3D picture does not follow a dial that plays: lifts %s, pictures %s" % (ls, hs))
    if len(set(ls)) <= 1: log("   (the dial did not move: the button was not a Play button for it)")
    if r["stopped"][0][0] != r["stopped"][1][0] or r["stopped"][0][1] != r["stopped"][1][1]: defects.append("after the dial stopped the picture still changes: %s" % json.dumps(r["stopped"]))
    n = log.problems(lab)
    if n: defects.append("console: %s" % lab.problems[:3])
log("DEFECTS: %d" % len(defects))
for d in defects: log("  " + d)
