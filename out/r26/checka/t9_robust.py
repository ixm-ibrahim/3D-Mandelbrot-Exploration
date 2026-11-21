"""Check 6: trying to break it.
R1  the window resized while the steps play (2D and 3D), and the flat picture checked against the reference after it
R2  the slider dragged fast (300 'input' events in a row), 2D and 3D; the arrow keys on the slider
R3  c far outside the big circle
R4  the powers 1, 0.5 and -2 (and the ends of the Power dial): the words at seven places of the slider, 2D and 3D
R5  the graphics taken away (WEBGL_lose_context) and given back: at rest, while playing, while on the 2D page
R6  odd calls of the test handle; kind and space switched while playing; the theme switched while on;
    reduced motion; the 1D line
"""
import json, sys, time
import numpy as np
from clab import Lab, Log, u8
import cref, cpix

log = Log("t9_robust" + (("-" + sys.argv[1]) if len(sys.argv) > 1 else ""))
only = sys.argv[1] if len(sys.argv) > 1 else ""
defects = []
HELP = """
const glc = () => document.querySelector('canvas.learn-shape-gl');
const look3 = () => { const c = glc(); if (!c || c.hidden || !c.width) return { cover: -1, hash: 'none', hidden: !c || c.hidden };
  const t = window.__t2 || (window.__t2 = document.createElement('canvas')); t.width = 216; t.height = 128; const g = t.getContext('2d', { willReadFrequently: true }); g.drawImage(c, 0, 0, 216, 128);
  const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++;
  return { cover: +(n / (216 * 128)).toFixed(4), hash: hashOf(c), size: c.width + 'x' + c.height, css: c.clientWidth + 'x' + c.clientHeight }; };
const look2 = () => hashOf($('learnShapeCanvas'));
const setRange = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
const sizes = () => { const s = $('stage'), c = $('learnShapeCanvas'), g = glc(); return { stage: [s.clientWidth, s.clientHeight], canvas: [c.width, c.height, c.clientWidth, c.clientHeight], gl: g ? [g.width, g.height, g.clientWidth, g.clientHeight, g.hidden] : null, page: [document.documentElement.scrollWidth, innerWidth] }; };
"""


def done(lab, tag):
    n = log.problems(lab)
    if n: defects.append("%s: %d console problems: %s" % (tag, n, lab.problems[:3]))


def flat_check(lab, name, k):
    info = lab.js(cpix.INFO)
    S = cpix.Scene(info)
    r = cpix.check(S, lab.grab("#learnShapeCanvas"), k)
    log("      %s: flat picture against the reference at step %d: stage %d x %d, %s" % (name, k, S.W, S.H, json.dumps(r)))
    if r["miss"] or r["extra"] or r["inside"] < 0: defects.append("%s: flat picture wrong at step %d: %s" % (name, k, json.dumps(r)))


t0 = time.time()
# ------------------------------------------------------------------ R1
if not only or "R1" in only.split(","):
    log("R1. the window resized while the steps play")
    for space in (2, 3):
        with Lab("r26-checka") as lab:
            lab.prelude += HELP
            lab.js("await shapeOn({ kind: 'both', space: %d, c: [-0.1226, 0.7449, 0], pos: 0 }); $('learnShapeSpeed').value = 'fast'; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true })); L.shape.play(); return 1;" % space)
            seen = []
            for w, h in ((1000, 700), (390, 800), (700, 500), (1400, 950), (320, 480), (1400, 950)):
                time.sleep(1.2)
                lab.resize(w, h)
                time.sleep(0.5)
                seen.append(lab.js("const s = L.shape.state(); return { win: [innerWidth, innerHeight], playing: s.playing, pos: +s.pos.toFixed(2), panes: s.panes.map(p => [p.x, p.y, p.w, p.h]), side: s.side, note: s.note, sz: sizes(), look: %s };" % ("look3()" if space == 3 else "0")))
                log("   %dD %s" % (space, json.dumps(seen[-1])))
                s = seen[-1]
                tot_w = max(p[0] + p[2] for p in s["panes"]); tot_h = max(p[1] + p[3] for p in s["panes"])
                if [tot_w, tot_h] != s["sz"]["stage"] or s["sz"]["canvas"][:2] != s["sz"]["stage"]:
                    defects.append("R1 %dD at %s: the panes or the canvas do not fit the stage: %s" % (space, s["win"], json.dumps(s["sz"])))
                if s["sz"]["page"][0] > s["sz"]["page"][1]: defects.append("R1 %dD at %s: the page is wider than the window: %s" % (space, s["win"], s["sz"]["page"]))
                if space == 3 and (s["note"] or s["look"]["cover"] <= 0): defects.append("R1 3D at %s: no 3D picture: %s" % (s["win"], json.dumps(s["look"])))
            ok = lab.wait("!window.squaringLab.learn.shape.state().playing", 40)
            end = lab.js("const s = L.shape.state(); return [s.playing, s.pos, s.sentence];")
            log("   %dD: the play ended: %s" % (space, json.dumps(end)))
            if not ok or end[1] != 16: defects.append("R1 %dD: play did not reach step 16 after the resizes: %s" % (space, json.dumps(end)))
            if space == 2:
                flat_check(lab, "R1 after the resizes, 1400 x 950", 16)
                lab.resize(390, 800); time.sleep(0.6)
                lab.js("L.shape.goto(5); return 1;")
                flat_check(lab, "R1 resized to 390 x 800", 5)
                lab.resize(1000, 420); time.sleep(0.6)
                flat_check(lab, "R1 resized to 1000 x 420", 5)
            else:
                # the 3D picture after the resizes against a fresh page at the same size
                # (the module picks how fine a resting picture is from what the card has just needed; a picture is compared
                #  with a fresh page's only when both came out equally fine, else the settling is waited for)
                for attempt in range(6):
                    lab.js("L.shape.goto(5); L.shape.goto(6); return L.shape.state().pos;"); time.sleep(0.5)
                    sa = lab.js("L.shape.state(); await sleep(250); return look3().size;")
                    if sa == "1724x1022": break
                a = lab.grab("#stage")
                lab.save(a, "out/r26/checka/t9-R1-3d-after-resizes.png")
                with Lab("r26-checka") as lab2:
                    lab2.prelude += HELP
                    lab2.js("await shapeOn({ kind: 'both', space: 3, c: [-0.1226, 0.7449, 0], pos: 6 }); await sleep(500); return 1;")
                    for attempt in range(6):
                        lab2.js("L.shape.goto(5); L.shape.goto(6); return L.shape.state().pos;"); time.sleep(0.5)
                        sb = lab2.js("L.shape.state(); await sleep(250); return look3().size;")
                        if sb == sa: break
                    b = lab2.grab("#stage")
                nd = -1 if a.shape != b.shape else int((np.abs(a.astype(int) - b.astype(int)).max(-1) > 8).sum())
                log("      3D picture after the resizes (buffer %s) against a fresh page (buffer %s) at step 6: %d of %d pixels differ by more than 8 levels" % (sa, sb, nd, a.shape[0] * a.shape[1]))
                if nd < 0 or (sa == sb and nd > 0.0005 * a.shape[0] * a.shape[1]): defects.append("R1 3D: after the resizes the picture (buffer %s) differs from a fresh one (buffer %s) at %d pixels" % (sa, sb, nd))
            done(lab, "R1 %dD" % space)

# ------------------------------------------------------------------ R2
if not only or "R2" in only.split(","):
    log("")
    log("R2. the slider dragged fast")
    with Lab("r26-checka") as lab:
        lab.prelude += HELP
        for space, kind in ((2, "both"), (3, "both"), (3, "m")):
            r = lab.js("""
              await shapeOn({ kind: %s, space: %d, c: [-0.1226, 0.7449, 0], pos: 0 }); await sleep(300);
              let seed = 7; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
              const e = $('learnShapePos'), t0 = performance.now(); let last = 0, worst = 0;
              for (let i = 0; i < 300; i++) { last = Math.round(rnd() * 16 / 0.05) * 0.05; e.value = last; const t = performance.now(); e.dispatchEvent(new Event('input', { bubbles: true })); worst = Math.max(worst, performance.now() - t); if (i %% 10 === 9) await frame(); }
              const ms = performance.now() - t0, want = +e.value;
              const st = L.shape.state(); await sleep(250); L.shape.state();
              const a = %s;
              L.shape.goto(0); L.shape.goto(want); const st2 = L.shape.state(); await sleep(250); L.shape.state();
              const b = %s;
              return { ms: Math.round(ms), worstOneInput: Math.round(worst), slider: want, pos: st.pos, sentence: st.sentence, same: a === b, playing: st.playing, where: $('learnShapeWhere').textContent, say: $('learnShapeSay').textContent };
            """ % (json.dumps(kind), space, "look2()" if space == 2 else "look3().hash", "look2()" if space == 2 else "look3().hash"))
            r2 = r
            log("   %dD %s: %s" % (space, kind, json.dumps(r)))
            if abs(r["pos"] - r["slider"]) > 0.021 or not r["same"] or r["say"] != r["sentence"]:
                defects.append("R2 %dD %s: after 300 fast moves of the slider the page is not at the slider's place, or the picture is not the picture of that place: %s" % (space, kind, json.dumps(r)))
        r = lab.js("""
          L.shape.set({ kind: 'j', space: 2, pos: 3.4 }); const e = $('learnShapePos'); e.focus(); const out = [];
          const key = k => e.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
          key('ArrowRight'); out.push(L.shape.state().pos); key('ArrowRight'); out.push(L.shape.state().pos); key('ArrowLeft'); key('ArrowLeft'); key('ArrowLeft'); out.push(L.shape.state().pos);
          for (let i = 0; i < 40; i++) key('ArrowRight'); out.push(L.shape.state().pos); for (let i = 0; i < 40; i++) key('ArrowLeft'); out.push(L.shape.state().pos);
          $('learnShapeBack').click(); out.push(L.shape.state().pos, $('learnShapeBack').disabled, $('learnShapeFwd').disabled);
          L.shape.goto(16); out.push($('learnShapeFwd').disabled); $('learnShapePlay').click(); await sleep(300); const s = L.shape.state(); out.push(s.playing, +s.pos.toFixed(1)); L.shape.pause();
          return out;""")
        log("   arrow keys on the slider from 3.4: right, right, three left, 40 right, 40 left; Back at 0; Forward at 16; Play at 16: %s" % json.dumps(r))
        if r[:5] != [4, 5, 2, 16, 0] or r[5] != 0 or r[6] is not True or r[8] is not True or r[9] is not True or r[10] > 1.5:
            defects.append("R2: keys and buttons at the ends of the slider: %s" % json.dumps(r))
        # the picture drawn while the slider is dragged in 2D: is it the picture of the place?
        lab.js("L.shape.set({ kind: 'm', space: 2 }); const e = $('learnShapePos'); for (const v of [3, 9.5, 12, 1.25, 7]) { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); } return 1;")
        flat_check(lab, "R2 after five quick moves ending at 7", 7)
        done(lab, "R2")

# ------------------------------------------------------------------ R3
if not only or "R3" in only.split(","):
    log("")
    log("R3. c far outside the big circle")
    with Lab("r26-checka") as lab:
        lab.prelude += HELP
        lab.js("await shapeOn({ kind: 'j', space: 2, pos: 0 }); return 1;")
        for c in ([3, 0, 0], [7, 0, 0], [2.4, 2.4, 0], [-8, 8, 0], [50, -50, 9]):
            r = lab.js("""const c = %s; const st = L.shape.set({ kind: 'j', space: 2, c, pos: 0 }); const out = { c: st.c, words: [] };
              for (const p of [0, 0.5, 1, 1.5, 2, 16]) { const s = L.shape.goto(p); out.words.push(p + ': ' + s.sentence); }
              out.mask = b64(L.shape.mask2('j', 129, 2, 16)); out.dia = L.shape.state().diamonds; return out;""" % json.dumps(c))
            cc = r["c"]
            ref = cref.mask("j", cc, 2, 129, 2.0, 16)
            got = u8(r["mask"]).reshape(129, 129)
            nd = int((got != ref).sum())
            left = [int((ref > k).sum()) for k in (0, 1, 2, 16)]
            log("   Julia shape, c asked %s, held %s: mask2 against the reference: %d differ; points left after 0, 1, 2, 16 steps: %s; diamond at %s" % (c, cc, nd, left, r["dia"]))
            for w in r["words"]: log("        " + w)
            if nd: defects.append("R3 c=%s: mask2 differs from the reference at %d points" % (cc, nd))
            lab.js("L.shape.goto(1); return 1;")
            flat_check(lab, "R3 c=%s" % cc, 1)
            # nothing left: the words must say so at the whole step, and must not say "what is left" over an empty picture
            if left[1] == 0 and "nothing is left" not in r["words"][2]:
                defects.append("R3 2D Julia c=%s: nothing is left after step 1 but the sentence is: %s" % (cc, r["words"][2]))
        lab.shot("out/r26/checka/t9-R3-2d-j-c7-step1.png") if lab.js("L.shape.set({ kind: 'j', space: 2, c: [7, 0, 0], pos: 1 }); return 1;") else None
        # Both, and 3D
        for kind, space, c in (("both", 2, [7, 0, 0]), ("j", 3, [7, 0, 0]), ("both", 3, [7, 0, 0]), ("j", 3, [0, 0, 7]), ("j", 3, [3, 1, 2])):
            r = lab.js("""const st = L.shape.set({ kind: %s, space: %d, c: %s, pos: 0 }); const words = [];
              for (const p of [0, 0.5, 1, 1.5, 2, 16]) { const s = L.shape.goto(p); await sleep(60); words.push(p + ': ' + L.shape.state().sentence); }
              L.shape.goto(1); await sleep(300); const s1 = L.shape.state(); await sleep(100);
              // in 3D: what does arithmetic say is left after step 1 (a grid of the ball), and what does the picture show
              let left1 = 0, leftK = 0, n = 0; if (%d === 3) for (let i = 0; i < 21; i++) for (let j = 0; j < 21; j++) for (let k = 0; k < 21; k++) { const p = [-2 + i * 0.2, -2 + j * 0.2, -2 + k * 0.2]; if (Math.hypot(...p) > 2) continue; n++; const o = ckOut3(p, 'j', st.c, 16); if (o > 1) left1++; if (o > 16) leftK++; }
              return { c: st.c, words, note: s1.note, look: %s, ball: [n, left1, leftK] };""" % (json.dumps(kind), space, json.dumps(c), space, "look3()" if space == 3 else "0"))
            log("   %s, %dD, c %s: %s" % (kind, space, r["c"], json.dumps({k: v for k, v in r.items() if k != "words"})))
            for w in r["words"]: log("        " + w)
            if space == 3 and kind == "j" and r["ball"][1] == 0 and "nothing is left" not in r["words"][2]:
                defects.append("R3 3D Julia c=%s: of %d grid points of the ball none is left after step 1, the picture shows only the grey ghost ball, and the sentence is: \"%s\"" % (r["c"], r["ball"][0], r["words"][2].split(": ", 1)[1]))
                lab.js("L.shape.goto(1); await sleep(400); L.shape.state(); await sleep(200); return 1;")
                lab.shot("out/r26/checka/t9-R3-3d-j-c%s-step1.png" % "_".join(str(x) for x in r["c"]))
        # the diamond dragged out of the big circle: c is held at 2.4
        r = lab.js("""L.shape.set({ kind: 'j', space: 2, c: [0.5, 0.5, 0], pos: 3 }); await sleep(100); const st = L.shape.state(), d = st.diamonds[0], cv = $('learnShapeCanvas');
          ptr(cv, 'pointerdown', d[0], d[1]); ptr(cv, 'pointermove', d[0] + 150, d[1] - 100); await frame(); ptr(cv, 'pointermove', 850, 5); await frame(); await frame(); const held = L.shape.state().c; ptr(cv, 'pointerup', 850, 5); await sleep(200);
          return { from: d, held, after: L.shape.state().c, sentence: L.shape.state().sentence };""")
        log("   the diamond dragged to the corner of the stage: %s" % json.dumps(r))
        if max(abs(r["after"][0]), abs(r["after"][1])) > 2.4 + 1e-9: defects.append("R3: the diamond can be dragged to c = %s" % r["after"])
        done(lab, "R3")

# ------------------------------------------------------------------ R4
if not only or "R4" in only.split(","):
    log("")
    log("R4. the powers 1, 0.5, -2 and the ends of the Power dial")
    with Lab("r26-checka") as lab:
        lab.prelude += HELP
        rng = lab.js("await shapeOn({ kind: 'm', space: 2, pos: 0 }); const e = $('pow'); return [e.min, e.max, e.step];")
        log("   the Power dial runs from %s to %s in steps of %s" % tuple(rng))
        for n in (1, 0.5, -2, float(rng[0]), float(rng[1]), 0):
            for space in (2, 3):
                for kind, c in (("m", [0, 0, 0]), ("j", [-0.4, 0.3, 0]), ("both", [-0.4, 0.3, 0])):
                    r = lab.js("""const n = %s; setRange('pow', n); await sleep(150);
                      const st = L.shape.set({ kind: %s, space: %d, c: %s, pos: 0 }); const words = [];
                      for (const p of [0, 0.5, 1, 1.5, 2, 2.5, 16]) { L.shape.goto(p); await sleep(40); const s = L.shape.state(); words.push(p + ': ' + s.sentence + (s.note ? '  [NOTE: ' + s.note + ']' : '')); }
                      const kd = %s === 'both' ? ['m', 'j'] : [%s], left = {};
                      for (const k of kd) { const M = %d === 2 ? L.shape.mask2(k, 129, 2, 16) : ckView().slice(k, st.c, { z: 0, half: 2, size: 129, maxK: 16 }); left[k] = [0, 1, 2, 16].map(q => { let m = 0; for (let i = 0; i < M.length; i++) if (M[i] > q) m++; return m; }); }
                      return { n: S.n, words, left, look: %s, notice: $('learnShapeNotice').textContent.slice(0, 400) };""" % (
                        json.dumps(n), json.dumps(kind), space, json.dumps(c), json.dumps(kind), json.dumps(kind), space, "look3()" if space == 3 else "0"))
                    log("   power %s (held %s), %dD, %s: points left after 0, 1, 2, 16 steps (%s): %s%s" % (n, r["n"], space, kind, "flat mask" if space == 2 else "slice at z = 0", json.dumps(r["left"]), ("  3D cover %s" % r["look"]["cover"]) if space == 3 else ""))
                    for w in r["words"]: log("        " + w)
                    # the words against the numbers
                    for k in (["m", "j"] if kind == "both" else [kind]):
                        L1 = r["left"][k]
                    w1, w2, w16 = r["words"][2], r["words"][4], r["words"][6]
                    if kind != "both":
                        L1 = r["left"][kind]
                        if "still the whole big" in w1 and L1[1] != L1[0]: defects.append("R4 power %s %dD %s: the words say the whole %s is still there after step 1, the numbers say %d of %d points" % (n, space, kind, "ball" if space == 3 else "circle", L1[1], L1[0]))
                        if space == 2 and L1[1] == 0 and "nothing is left" not in w1: defects.append("R4 power %s 2D %s: nothing is left after step 1, the sentence is: %s" % (n, kind, w1))
                        if "nothing is left" in w1 and L1[1] > 0: defects.append("R4 power %s %dD %s: the sentence says nothing is left after step 1, but %d points of the %s are" % (n, space, kind, L1[1], "flat mask" if space == 2 else "slice"))
                    if "becomes the Mandelbrot set" in w16 or "becomes the Julia set" in w16 or "these become" in w16:
                        if not (float(r["n"]) == int(r["n"]) and r["n"] >= 2 and space == 2):
                            defects.append("R4 power %s %dD %s: the last sentence promises the set: %s" % (n, space, kind, w16))
                    if any("NOTE" in w for w in r["words"]): defects.append("R4 power %s %dD %s: a note stands in place of the picture: %s" % (n, space, kind, [w for w in r["words"] if "NOTE" in w][:1]))
        lab.js("setRange('pow', 2); return 1;")
        done(lab, "R4")

# ------------------------------------------------------------------ R5
if not only or "R5" in only.split(","):
    log("")
    log("R5. the graphics taken away and given back")
    with Lab("r26-checka") as lab:
        lab.prelude += HELP
        r = lab.js("""
          await shapeOn({ kind: 'both', space: 3, c: [-0.1226, 0.7449, 0], pos: 5 }); await sleep(500); L.shape.state(); await sleep(200);
          const gl = glc().getContext('webgl2'), ext = gl.getExtension('WEBGL_lose_context'), out = {};
          if (!ext) return { no: 'this browser has no WEBGL_lose_context' };
          out.before = look3();
          ext.loseContext(); await sleep(400);
          let s = L.shape.state(); out.lost = { note: s.note, noteShown: $('learnShapeNote').getClientRects().length > 0 && $('learnShapeNote').textContent, glHidden: glc().hidden, threeOk: s.threeOk, sentence: s.sentence, hintHidden: $('learnHint').hidden };
          // used while the graphics are away: the slider, Play, the kind, the 2D page and back
          L.shape.goto(7); L.shape.play(); await sleep(500); const pl = L.shape.state(); L.shape.pause(); L.shape.set({ kind: 'j' }); L.shape.set({ space: 2 }); await sleep(100); const flat = L.shape.state(); L.shape.set({ space: 3, kind: 'both', pos: 5 }); await sleep(100);
          s = L.shape.state(); out.used = { playedTo: +pl.pos.toFixed(2), flatNote: flat.note, flatSpace: flat.space, backNote: s.note };
          ext.restoreContext(); await sleep(900);
          s = L.shape.state(); await sleep(300); out.back = Object.assign({ note: s.note, glHidden: glc().hidden, threeOk: s.threeOk }, look3());
          // while playing
          L.shape.goto(0); L.shape.play(); await sleep(700); ext.loseContext(); await sleep(600); const p1 = L.shape.state(); ext.restoreContext(); await sleep(900); const p2 = L.shape.state(); await sleep(200);
          out.playing = { lostAt: +p1.pos.toFixed(2), noteWhileLost: p1.note, stillPlaying: p1.playing, afterRestore: { playing: p2.playing, pos: +p2.pos.toFixed(2), note: p2.note }, look: look3() };
          L.shape.pause();
          // lost while the 2D page is on show, given back there, then 3D
          L.shape.set({ space: 2, pos: 4 }); await sleep(100); ext.loseContext(); await sleep(300); const f1 = L.shape.state(); ext.restoreContext(); await sleep(600); L.shape.set({ space: 3 }); await sleep(600); const f2 = L.shape.state(); await sleep(300);
          out.flat = { noteIn2D: f1.note, then3D: Object.assign({ note: f2.note }, look3()) };
          // lost in 2D, 3D asked for while it is away, then given back
          L.shape.set({ space: 2 }); await sleep(100); ext.loseContext(); await sleep(300); L.shape.set({ space: 3 }); await sleep(300); const g1 = L.shape.state(); ext.restoreContext(); await sleep(900); const g2 = L.shape.state(); await sleep(300);
          out.asked = { noteWhileLost: g1.note, afterRestore: Object.assign({ note: g2.note }, look3()) };
          return out;""")
        for k, v in r.items(): log("   %s: %s" % (k, json.dumps(v)))
        if "no" not in r:
            if not r["lost"]["note"] or not r["lost"]["glHidden"]: defects.append("R5: with the graphics gone no sentence stands in the picture's place: %s" % json.dumps(r["lost"]))
            if r["back"]["note"] or r["back"]["glHidden"] or abs(r["back"]["cover"] - r["before"]["cover"]) > 0.01: defects.append("R5: the 3D picture did not come back by itself: before %s, back %s" % (json.dumps(r["before"]), json.dumps(r["back"])))
            if r["used"]["flatNote"]: defects.append("R5: the 2D page shows a note while the graphics are gone: %s" % r["used"]["flatNote"])
            if r["playing"]["afterRestore"]["note"] or r["playing"]["look"]["cover"] <= 0: defects.append("R5: lost while playing, the picture did not come back: %s" % json.dumps(r["playing"]))
            if r["flat"]["then3D"]["note"] or r["flat"]["then3D"]["cover"] <= 0: defects.append("R5: lost and given back on the 2D page, then 3D: no picture: %s" % json.dumps(r["flat"]))
            if r["asked"]["afterRestore"]["note"] or r["asked"]["afterRestore"]["cover"] <= 0: defects.append("R5: lost on the 2D page, 3D asked for, given back: no picture: %s" % json.dumps(r["asked"]))
        lab.shot("out/r26/checka/t9-R5-after-all.png")
        n = len(lab.problems)
        log("   console while the graphics were taken away and given back: %d lines: %s" % (n, [p[:160] for p in lab.problems[:6]]))
        real = [p for p in lab.problems if "CONTEXT_LOST" not in p and "context lost" not in p.lower() and "loseContext" not in p]
        if real: defects.append("R5: console problems other than the browser's own words about the lost context: %s" % real[:3])

# ------------------------------------------------------------------ R6
if not only or "R6" in only.split(","):
    log("")
    log("R6. odd things")
    with Lab("r26-checka") as lab:
        lab.prelude += HELP
        r = lab.js("""
          await shapeOn({ kind: 'm', space: 2, pos: 2 });
          const out = {}, tryIt = (name, f) => { try { out[name] = f(); } catch (e) { out[name] = 'THROWS: ' + e.message; } };
          tryIt('set garbage', () => { const s = L.shape.set({ kind: 'x', c: ['a', null, undefined], pos: 99, space: 1 }); return [s.kind, s.c, s.pos, s.space]; });
          tryIt('set nothing', () => L.shape.set().pos);
          tryIt('set pos NaN, -5', () => [L.shape.set({ pos: NaN }).pos, L.shape.set({ pos: -5 }).pos]);
          tryIt('goto(garbage)', () => [L.shape.goto('abc').pos, L.shape.goto(1e9).pos, L.shape.goto(-3).pos, L.shape.goto(4.99).pos, L.shape.goto(5.03).pos]);
          tryIt('mask2 odd sizes', () => [L.shape.mask2('m', 1, 2, 16).length, L.shape.mask2('m', 3, -1, 16).length, L.shape.mask2('q', 5, 2, 999).join(''), L.shape.mask2('m', 5, 2, 0).join('')]);
          tryIt('out2 odd', () => [L.shape.out2([0, 0], 'm'), L.shape.out2([NaN, 0], 'm', null, 5), L.shape.out2([9, 9], 'j', [0, 0], 5), L.shape.out2([0.3, 0.2], 'j', undefined, 3), L.shape.out2([0, 0], 'j', [0, 0], 0)]);
          tryIt('3d out odd', () => [LAB.learnShape3d.out([0, 0, 0], 'm', [0, 0, 0], 0), LAB.learnShape3d.out([NaN, 0, 0], 'j', [0, 0, 0], 4), LAB.learnShape3d.out([0, 0, 0], 'j', [0, 0, 0])]);
          L.shape.set({ kind: 'm', c: [-0.4, 0.3, 0], pos: 0 });
          return out;""")
        for k, v in r.items():
            log("   %s -> %s" % (k, json.dumps(v)))
            if isinstance(v, str) and v.startswith("THROWS"): defects.append("R6: %s %s" % (k, v))
        # kind and space switched while the steps play, by the transport's own switches
        r = lab.js("""
          L.shape.set({ kind: 'm', space: 2, pos: 0 }); $('learnShapeSpeed').value = 'fast'; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true })); $('learnShapePlay').click();
          const seen = []; const kinds = ['j', 'both', 'm'], spaces = ['3', '2'];
          for (let i = 0; i < 18; i++) { await sleep(280); if (i % 2) $('learnShapeKindBar').querySelector('input[value=' + kinds[(i >> 1) % 3] + ']').click(); else $('learnShapeSpaceBar').querySelector('input[value="' + spaces[(i >> 1) % 2] + '"]').click();
            const s = L.shape.state(); seen.push([s.kind, s.space, s.playing, +s.pos.toFixed(1), s.note]); }
          const s = L.shape.state();
          return { seen: seen.map(x => x.join('/')).join('  '), end: [s.kind, s.space, s.playing, +s.pos.toFixed(2)] };""")
        log("   kind and space switched 18 times while playing (kind/space/playing/pos/note): %s" % r["seen"])
        stops = [x for x in r["seen"].split("  ") if "/false/" in x]
        log("      -> %s" % ("Play went on through every switch" if not stops else "Play STOPPED at: %s" % stops[:4]))
        lab.js("L.shape.pause(); return 1;")
        # the theme switched while on (the page's own attribute), 2D and 3D
        r = lab.js("""
          L.shape.set({ kind: 'j', space: 2, c: [-1, 0, 0], pos: 4 }); await sleep(200);
          const tok = () => getComputedStyle(document.documentElement).getPropertyValue('--stage').trim(), out = [];
          const px = () => { const c = $('learnShapeCanvas'), g = c.getContext('2d'), P = L.shape.state().panes[0], d = g.getImageData(Math.round(P.x + P.w / 2), Math.round(P.y + P.h / 2), 1, 1).data, e = g.getImageData(3, c.height - 3, 1, 1).data; return [[d[0], d[1], d[2], d[3]], [e[0], e[1], e[2], e[3]]]; };
          out.push([document.documentElement.dataset.theme || '(none)', tok(), px()]);
          document.documentElement.dataset.theme = 'light'; await sleep(400); L.shape.state(); out.push(['light', tok(), getComputedStyle(document.documentElement).getPropertyValue('--brass').trim(), px()]);
          L.shape.set({ space: 3 }); await sleep(500); L.shape.state(); await sleep(200); out.push(['light 3D', look3()]);
          document.documentElement.dataset.theme = 'dark'; await sleep(500); L.shape.state(); await sleep(200); out.push(['dark 3D', look3()]);
          delete document.documentElement.dataset.theme; await sleep(300);
          return out;""")
        for row in r: log("   theme: %s" % json.dumps(row))
        if r[2][1]["hash"] == r[3][1]["hash"]: defects.append("R6: the 3D picture did not change when the theme went from light to dark")
        lab.shot("out/r26/checka/t9-R6-end.png")
        done(lab, "R6")
    # the first switch plays by itself once; not with reduced motion; the 1D line
    for reduced in (False, True):
        with Lab("r26-checka", reduced=reduced) as lab:
            r = lab.js("""
              $('mode-l').click(); await sleep(300); $('learnSpace1').click(); await sleep(200);
              const before = [L.space, L.follow];
              $('learnFollowShape').click(); await sleep(600);
              const s1 = L.shape.state(), line = $('learnSpace1').closest('.seg'), lineShown = line.getClientRects().length > 0;
              await sleep(900); const s2 = L.shape.state();
              L.shape.pause(); $('learnFollowPoint').click(); await sleep(200); $('learnFollowShape').click(); await sleep(500); const s3 = L.shape.state();
              return { before, first: [s1.space, s1.playing, +s1.pos.toFixed(2)], later: [s2.playing, +s2.pos.toFixed(2)], secondSwitch: [s3.playing, +s3.pos.toFixed(2)], line1DShown: lineShown, calm: matchMedia('(prefers-reduced-motion: reduce)').matches };""")
            log("   first switch to A whole shape from the 1D line, reduced motion %s: %s" % (reduced, json.dumps(r)))
            if r["first"][0] != 2 or r["line1DShown"]: defects.append("R6: from the 1D line: space %s, 1D choice shown %s" % (r["first"][0], r["line1DShown"]))
            if reduced and (r["first"][1] or r["later"][1] > 0): defects.append("R6: with reduced motion the picture plays by itself: %s" % json.dumps(r))
            if not reduced and not (r["first"][1] and r["later"][1] > r["first"][2]): defects.append("R6: the first switch does not play by itself: %s" % json.dumps(r))
            if r["secondSwitch"][0]: defects.append("R6: the second switch plays by itself again: %s" % json.dumps(r))
            done(lab, "R6 first switch, reduced %s" % reduced)

log("")
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)
