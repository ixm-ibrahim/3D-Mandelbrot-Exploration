"""Check 4: using it.
A. Every approach in the list, Mandelbrot shape, Julia shape and Both, in 3D and in 2D, at ten places of the slider:
   no console error, no note in place of the picture, something drawn.
B. With "A whole shape" on, the power, a modifier, a dial of the approach and the approach itself are changed with
   the page's own controls: does the picture change (3D), and in 2D does it change exactly when the flat rule does?
C. Follow = One point, a place in the middle of a step; over to A whole shape (by the page's own radio), things done
   there; back to One point: LEARN.state() and the whole window before and after.
D. Reset everything, and the Learn panel's own reset.
E. Leaving Learn for the Julia tab and coming back, at rest and while the steps play.
"""
import json, sys, time
import numpy as np
from clab import Lab, Log

log = Log("t6_use")
defects = []
ALL = ["mercator", "fold", "turnaway", "turnalong", "windsq", "alongonce", "pulledplane", "lathe", "tilt", "quat4", "rotor", "rotorframe", "sqpillow",
       "bulb", "classic", "split", "softfold", "axisbulb", "pillow", "kleinsq", "kleinsq2"]
HELP = """
const glc = () => document.querySelector('canvas.learn-shape-gl');
// how much of the 3D canvas shows something, and a hash of it
const look3 = () => { const c = glc(); if (!c || c.hidden || !c.width) return { cover: -1, hash: 'none' };
  const t = window.__t2 || (window.__t2 = document.createElement('canvas')); t.width = 216; t.height = 128; const g = t.getContext('2d', { willReadFrequently: true }); g.drawImage(c, 0, 0, 216, 128);
  const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++;
  return { cover: +(n / (216 * 128)).toFixed(4), hash: hashOf(c), size: c.width + 'x' + c.height }; };
const look2 = () => hashOf($('learnShapeCanvas'));
const setRange = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
"""


def same(a, b):
    return a.shape == b.shape and bool((a == b).all())


def ndiff(a, b):
    if a.shape != b.shape: return -1
    return int((np.abs(a.astype(int) - b.astype(int)).max(-1) > 0).sum())


t0 = time.time()
# ---------------------------------------------------------------- A
with Lab("r26-checka") as lab:
    lab.prelude += HELP
    lab.js("await shapeOn({ kind: 'm', space: 3, pos: 0 }); return 1;")
    hashes = {}
    for id_ in ALL:
        r = lab.js("""
          const id = %s, rows = [], bad = [];
          await pickAp(id);
          for (const [kind, c] of [['m', [0, 0, 0]], ['j', [-0.1226, 0.7449, 0]], ['both', [-1, 0, 0.2]]]) {
            L.shape.set({ kind, c, space: 3, pos: 0 });
            const covers = [];
            for (const pos of [0, 0.5, 1, 1.5, 2, 3.4, 5, 8, 12, 16]) {
              L.shape.goto(pos); await frame();
              const st = L.shape.state(), k = look3();
              covers.push(k.cover);
              if (st.note || !st.threeOk || !st.three || !st.three.ok) bad.push(kind + ' at ' + pos + ': note "' + st.note + '" threeOk ' + st.threeOk);
              if (pos === 0 && !(k.cover > 0.2)) bad.push(kind + ' at 0: the ball covers only ' + k.cover + ' of the stage');
              if (pos === 5) rows.push([kind, k.hash]);
              if (glc().hidden) bad.push(kind + ' at ' + pos + ': the 3D canvas is hidden');
            }
            rows.push([kind + ' cover', covers.join(' ')]);
          }
          // and the flat pictures with this approach chosen
          for (const kind of ['m', 'j', 'both']) { const st = L.shape.set({ kind, space: 2, pos: 6 }); if (st.note || st.space !== 2) bad.push('2D ' + kind + ': ' + JSON.stringify(st.note)); await frame(); }
          L.shape.set({ space: 3 });
          return { rows, bad, rule: $('learnShapeRule').textContent.slice(0, 160), name: AP().name };
        """ % json.dumps(id_))
        hashes[id_] = dict((k, v) for k, v in r["rows"] if "cover" not in k)
        log("%-12s %s" % (id_, "; ".join("%s: %s" % (k, v) for k, v in r["rows"] if "cover" in k)))
        if r["name"] not in r["rule"]:
            defects.append("%s: the panel's line about the rule does not name the approach: %s" % (id_, r["rule"]))
        for b in r["bad"]:
            defects.append("A, %s: %s" % (id_, b)); log("   BAD: " + b)
    # do different approaches give different pictures?
    for kind in ("m", "j", "both"):
        groups = {}
        for id_ in ALL:
            groups.setdefault(hashes[id_][kind], []).append(id_)
        same_pic = [g for g in groups.values() if len(g) > 1]
        log("3D picture at step 5, %s: %d different pictures among 21 approaches; the same picture: %s" % (kind, len(groups), same_pic))
    n = log.problems(lab)
    if n: defects.append("A: %d console problems: %s" % (n, lab.problems[:3]))

# ---------------------------------------------------------------- B
with Lab("r26-checka") as lab:
    lab.prelude += HELP
    r = lab.js("""
      await shapeOn({ kind: 'both', space: 3, pos: 4, c: [-0.1226, 0.7449, 0] }); await pickAp('mercator');
      const out = [], snap = async what => { await sleep(450); const st = L.shape.state(); await sleep(60); out.push([what, look3().hash, S.n, S.abs.join(''), S.flip.join(''), AP().id, JSON.stringify(S.param[AP().id]), b64(L.shape.mask2('m', 65, 2, 16)).length + ':' + hashOf($('learnShapeCanvas')), st.sentence]); };
      await snap('start');
      setRange('pow', 3); await snap('power 3 (the Power dial)');
      $('absx').click(); await snap('|x| ticked');
      $('flipz').click(); await snap('flip z ticked');
      setRange('par-mercator-lift', 0.5); await snap('dial Lift 0.5');
      setRange('par-mercator-turn', 40); await snap('dial Turn 40');
      $('ap-lathe').click(); await snap('approach Lathe');
      $('apNext').click(); await snap('approach: the Next button');
      setRange('pow', 2); await snap('power 2');
      $('absx').click(); $('flipz').click(); await snap('modifiers off');
      $('modShip').click(); await snap('the "ship" modifier button');
      $('modNone').click(); await snap('the "none" modifier button');
      return out;
    """)
    prev = None
    log("")
    log("B. 3D, Both: the hash of the 3D picture after each change made with the page's own controls")
    for row in r:
        ch = "" if prev is None else ("changed" if row[1] != prev else "DID NOT CHANGE")
        log("   %-32s n=%s abs=%s flip=%s %s %s   picture %s %s" % (row[0], row[2], row[3], row[4], row[5], row[6], row[1], ch))
        if prev is not None and row[1] == prev: defects.append("B: 3D picture did not change after: " + row[0])
        prev = row[1]
    # 2D: the power and the modifiers of x and y change it; the approach, its dials and the modifiers of z do not
    r = lab.js("""
      await pickAp('mercator'); dialsBack('mercator'); setRule(2, [0,0,0], [0,0]);
      L.shape.set({ kind: 'both', space: 2, pos: 4, c: [-0.1226, 0.7449, 0] });
      const out = [], snap = async what => { await sleep(350); L.shape.state(); out.push([what, look2()]); };
      await snap('start');
      setRange('pow', 3); await snap('power 3');
      $('absx').click(); await snap('|x| ticked');
      $('flipy').click(); await snap('flip y ticked');
      $('absz').click(); await snap('|z| ticked (nothing of the flat rule)');
      setRange('par-mercator-lift', 0.5); await snap('dial Lift 0.5 (nothing of the flat rule)');
      $('ap-lathe').click(); await snap('approach Lathe (nothing of the flat rule)');
      setRange('pow', 2.5); await snap('power 2.5');
      setRange('pow', 2); $('absx').click(); $('flipy').click(); $('absz').click(); await snap('all back');
      return out;
    """)
    log("B. 2D, Both: the hash of the flat picture after each change")
    prev = None; first = r[0][1]
    for what, h in r:
        ch = "" if prev is None else ("changed" if h != prev else "same")
        log("   %-48s %s %s" % (what, h, ch))
        if prev is not None:
            want_same = "nothing of the flat rule" in what
            if want_same and h != prev: defects.append("B: the flat picture changed after: " + what)
            if not want_same and h == prev: defects.append("B: the flat picture did not change after: " + what)
        prev = h
    if r[-1][1] != first: defects.append("B: with everything put back the flat picture is not what it was")
    log("   with everything back: %s" % ("the picture it started with" if r[-1][1] == first else "NOT the picture it started with"))
    n = log.problems(lab)
    if n: defects.append("B: %d console problems: %s" % (n, lab.problems[:3]))

# ---------------------------------------------------------------- C, D, E
with Lab("r26-checka") as lab:
    lab.prelude += HELP
    lab.js("$('mode-l').click(); await sleep(400); return 1;")
    base_state = lab.js("return [L.state(), L.shape.state()];")
    base_pic = lab.grab()
    log("")
    log("C. Round trips: Follow = One point -> A whole shape -> One point")
    for space, zc in ((2, "{ z: [0.55, -0.35, 0], c: [-0.6, 0.25, 0] }"), (3, "{ z: [0.5, 0.3, 0.45], c: [-0.35, 0.2, 0.15] }"), (1, "{ z: [-1.1, 0, 0], c: [-0.7, 0, 0] }")):
        s0 = lab.js("L.set({ space: %d }); L.set(%s); L.next(); L.next(); L.goto(1, 0.4); await sleep(300); return L.state();" % (space, zc))
        p0 = lab.grab()
        mid = lab.js("""
          $('learnFollowShape').click(); await sleep(1500);
          const playing = L.shape.state().playing;
          L.shape.pause(); $('learnShapeKindBar').querySelector('input[value=both]').click(); await sleep(100);
          setRange('learnShape-cx', 0.31); setRange('learnShape-cy', -0.52); await sleep(100);
          L.shape.goto(7.3);
          const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect();
          $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -500, clientX: b.left + 200, clientY: b.top + 250, bubbles: true, cancelable: true })); await sleep(300);
          $('learnShapeFwd').click(); await sleep(700);
          const st = L.shape.state();
          $('learnFollowPoint').click(); await sleep(400);
          return { playing, st: [st.kind, st.c, st.pos, st.space, st.view2.m.zoom], body: document.body.className };
        """)
        s1 = lab.js("return L.state();")
        p1 = lab.grab()
        eq = json.dumps(s0, sort_keys=True) == json.dumps(s1, sort_keys=True)
        nd = ndiff(p0, p1)
        keys = [k for k in s0 if json.dumps(s0[k], sort_keys=True) != json.dumps(s1.get(k), sort_keys=True)]
        log("   from %dD (step %d, move %d, t %.2f): in the whole shape: %s; back: LEARN.state() %s; window pixels that differ: %d" % (
            space, s0["step"], s0["move"], s0["t"], json.dumps(mid), "the same" if eq else "DIFFERS in " + ", ".join("%s: %s -> %s" % (k, json.dumps(s0[k])[:60], json.dumps(s1.get(k))[:60]) for k in keys), nd))
        if space != 1 and (not eq or nd):
            defects.append("C: round trip from %dD does not restore One point: state %s, %d pixels differ" % (space, "same" if eq else "differs in " + ",".join(keys), nd))
            lab.save(p0, "out/r26/checka/t6-C-%dd-before.png" % space); lab.save(p1, "out/r26/checka/t6-C-%dd-after.png" % space)
        if space == 1:
            log("      (from the 1D line the round says: go to 2D. So the place on the line is not kept: space %s -> %s, step %s -> %s)" % (s0["space"], s1["space"], s0["step"], s1["step"]))
    # switching the space INSIDE the whole shape, then back
    r = lab.js("""L.set({ space: 2 }); L.set({ z: [0.55, -0.35, 0], c: [-0.6, 0.25, 0] }); L.next(); L.goto(1, 0.4); const a = L.state();
      $('learnFollowShape').click(); await sleep(200); $('learnShapeSpaceBar').querySelector('input[value="3"]').click(); await sleep(300); $('learnShapeSpaceBar').querySelector('input[value="2"]').click(); await sleep(200);
      $('learnFollowPoint').click(); await sleep(300); const b = L.state();
      return [[a.space, a.step, a.move, a.t, a.z0, a.c], [b.space, b.step, b.move, b.t, b.z0, b.c]];""")
    log("   2D -> whole shape -> 3D -> 2D -> One point: before (space, step, move, t, z0, c) %s, after %s" % (json.dumps(r[0]), json.dumps(r[1])))
    if json.dumps(r[0]) != json.dumps(r[1]):
        defects.append("C2: after switching 2D -> 3D -> 2D inside 'A whole shape', One point has lost its place: before (space, step, move, t) %s, after %s" % (json.dumps(r[0][:4]), json.dumps(r[1][:4])))

    # ---- D
    log("")
    log("D. Reset everything")
    r = lab.js("""
      $('learnFollowShape').click(); await sleep(200); L.shape.pause();
      L.shape.set({ kind: 'both', space: 3, c: [0.5, -0.7, 0.3], pos: 7.3 });
      $('learnShapeSpeed').value = 'fast'; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true }));
      const cv = $('learnShapeCanvas'); ptr(cv, 'pointerdown', 300, 200); ptr(cv, 'pointermove', 380, 260); await frame(); ptr(cv, 'pointerup', 380, 260);
      $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -400, clientX: 400, clientY: 400, bubbles: true, cancelable: true }));
      $('ap-lathe').click(); setRange('pow', 3); $('absx').click(); await sleep(400);
      const before = L.shape.state();
      $('resetAll').click(); await sleep(800);
      const off = { on: L.on, follow: L.follow, n: S.n, abs: S.abs, ap: AP().id, mode: S.mode, body: document.body.className, shapeCanvasHidden: $('learnShapeCanvas').hidden, barHidden: $('learnShapeBar').hidden, gl: glc() ? glc().hidden : 'none', speed: L.speed };
      return { before: [before.kind, before.space, before.c, before.pos, before.view3], off };
    """)
    log("   before: %s" % json.dumps(r["before"]))
    log("   after Reset everything: %s" % json.dumps(r["off"]))
    lab.idle(60)
    after = lab.js("$('mode-l').click(); await sleep(500); return [L.state(), L.shape.state()];")
    pic = lab.grab()
    drop = lambda st: {k: v for k, v in st.items() if k not in ("ms", "three", "quality")}
    eq1 = json.dumps(base_state[0], sort_keys=True) == json.dumps(after[0], sort_keys=True)
    eq2 = json.dumps(drop(base_state[1]), sort_keys=True) == json.dumps(drop(after[1]), sort_keys=True)
    nd = ndiff(base_pic, pic)
    log("   Learn opened again: LEARN.state() %s; LEARN.shape.state() %s; window pixels that differ from the first opening: %d" % (
        "as at the first opening" if eq1 else "DIFFERS", "as at the first opening" if eq2 else "DIFFERS: " + json.dumps(drop(after[1]))[:400], nd))
    if r["off"]["on"] or r["off"]["follow"] != "point" or not eq1 or not eq2 or nd:
        defects.append("D: Reset everything: on %s follow %s, state same %s, shape state same %s, %d pixels differ" % (r["off"]["on"], r["off"]["follow"], eq1, eq2, nd))
        lab.save(base_pic, "out/r26/checka/t6-D-first.png"); lab.save(pic, "out/r26/checka/t6-D-after-reset.png")
    # the Learn panel's own reset
    r = lab.js("""
      $('learnFollowShape').click(); await sleep(200); L.shape.pause();
      L.shape.set({ kind: 'j', space: 3, c: [0.5, -0.7, 0.3], pos: 9 }); await sleep(200);
      const btn = document.querySelector('#learnReset button'); if (!btn) fail('no reset button in the Learn panel');
      const label = btn.textContent; btn.click(); await sleep(500);
      const st = L.shape.state();
      return { label, on: L.on, follow: L.follow, shape: [st.on, st.kind, st.space, st.c, st.pos, st.view3, st.view2], point: $('learnFollowPoint').checked, summary: document.querySelector('#learnPanel summary').textContent };
    """)
    log("   the Learn panel's own reset (\"%s\"): %s" % (r["label"], json.dumps(r)))
    if r["follow"] != "point" or r["shape"][1] != "m" or r["shape"][2] != 2 or r["shape"][4] != 0 or r["shape"][3] != [-0.4, 0.3, 0] or not r["point"]:
        defects.append("D: the Learn panel's reset does not put the whole shape back: %s" % json.dumps(r))
    s2 = lab.js("return L.state();")
    pic2 = lab.grab()
    nd2 = ndiff(base_pic, pic2)
    log("      after it: LEARN.state() %s; window pixels that differ from the first opening: %d" % ("as at the first opening" if json.dumps(base_state[0], sort_keys=True) == json.dumps(s2, sort_keys=True) else "DIFFERS", nd2))
    if nd2:
        defects.append("D: after the Learn panel's reset the window differs from the first opening at %d pixels" % nd2)
        lab.save(pic2, "out/r26/checka/t6-D-after-panel-reset.png")

    # ---- E
    log("")
    log("E. To the Julia tab and back")
    r = lab.js("""
      $('learnFollowShape').click(); await sleep(200); L.shape.pause();
      L.shape.set({ kind: 'j', space: 3, c: [0.2, 0.5, 0.1], pos: 6 });
      const cv = $('learnShapeCanvas'); ptr(cv, 'pointerdown', 300, 200); ptr(cv, 'pointermove', 360, 240); await frame(); ptr(cv, 'pointerup', 360, 240); await sleep(500);
      const st = L.shape.state(); await sleep(100);
      return { st: [st.on, st.kind, st.space, st.c, st.pos, st.view3, st.three && st.three.quality], h: look3() };
    """)
    q0 = lab.grab("#stage")
    lab.js("$('mode-j').click(); await sleep(300); return 1;")
    lab.idle(90)
    away = lab.js("""return { on: L.on, follow: L.follow, learnS: S.learn, mode: S.mode, body: document.body.className, shapeCanvasHidden: $('learnShapeCanvas').hidden, barHidden: $('learnShapeBar').hidden, oldBarHidden: $('learnBar').hidden,
      gl: glc().hidden, panelHidden: $('learnPanel').hidden, shape: (s => [s.on, s.kind, s.space, s.c, s.pos])(L.shape.state()) };""")
    qj = lab.grab("#stage")
    lab.save(qj, "out/r26/checka/t6-E-julia-tab.png")
    back = lab.js("$('mode-l').click(); await sleep(700); const st = L.shape.state(); await sleep(100); return { st: [st.on, st.kind, st.space, st.c, st.pos, st.view3, st.three && st.three.quality], h: look3(), follow: L.follow };")
    q1 = lab.grab("#stage")
    nd = ndiff(q0, q1)
    log("   before leaving: %s" % json.dumps(r))
    log("   on the Julia tab: %s; the stage there is %s" % (json.dumps(away), "a picture (%d different colours)" % len(np.unique(qj.reshape(-1, 3), axis=0))))
    log("   back: %s; stage pixels that differ from before leaving: %d of %d" % (json.dumps(back), nd, q0.shape[0] * q0.shape[1]))
    if away["on"] or not away["shapeCanvasHidden"] or not away["barHidden"] or not away["gl"]:
        defects.append("E: on the Julia tab something of the whole shape is still on show: %s" % json.dumps(away))
    if json.dumps(r["st"][:6]) != json.dumps(back["st"][:6]) or back["follow"] != "shape":
        defects.append("E: back from the Julia tab the whole shape is not where it was: %s -> %s" % (json.dumps(r["st"]), json.dumps(back["st"])))
    if nd:
        lab.save(q0, "out/r26/checka/t6-E-before.png"); lab.save(q1, "out/r26/checka/t6-E-back.png")
        if nd > 200: defects.append("E: back from the Julia tab the stage differs at %d pixels" % nd)
    # while the steps play
    r = lab.js("""
      L.shape.set({ kind: 'both', space: 2, pos: 0 }); L.shape.play(); await sleep(1500);
      const p1 = L.shape.state();
      $('mode-j').click(); await sleep(1500);
      const a = L.shape.state(), posA = a.pos; await sleep(800); const b = L.shape.state();
      $('mode-l').click(); await sleep(600); const c = L.shape.state();
      return { playingBefore: [p1.playing, +p1.pos.toFixed(2)], away: [a.on, a.playing, +a.pos.toFixed(2), +b.pos.toFixed(2)], back: [c.on, c.playing, +c.pos.toFixed(2), c.kind, c.space], sentence: c.sentence };
    """)
    log("   leaving while the steps play: %s" % json.dumps(r))
    if r["away"][1] or r["away"][2] != r["away"][3] or r["back"][1]:
        defects.append("E: the steps go on playing after Learn was left: %s" % json.dumps(r))
    lab.idle(60)
    n = log.problems(lab)
    if n: defects.append("C/D/E: %d console problems: %s" % (n, lab.problems[:3]))

log("")
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)
