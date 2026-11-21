"""Section 5, second point: Mandelbrot shape, Julia shape and Both, in 2D and in 3D, play from step 0 to 16 without
console errors, in both themes, at 1400 x 950 and at 390 x 800.   usage: t7_play.py dark|light 1400x950|390x800
Play is pressed with the page's own button (speed Fast). While it plays the state is read four times a second:
the slider must never go back, every whole step must be rested on, and at the end the page must stand on step 16,
not playing, with the picture of step 16 (2D: against my reference, pixel by pixel; 3D: the same picture a fresh
goto(16) gives).
"""
import json, sys, time
import numpy as np
from clab import Lab, Log
import cpix

theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
size = tuple(int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "1400x950").split("x"))
log = Log("t7_play-%s-%dx%d" % (theme, size[0], size[1]))
defects = []
HELP = """
const glc = () => document.querySelector('canvas.learn-shape-gl');
const look3 = () => { const c = glc(); if (!c || c.hidden || !c.width) return { cover: -1, hash: 'none' };
  const t = window.__t2 || (window.__t2 = document.createElement('canvas')); t.width = 216; t.height = 128; const g = t.getContext('2d', { willReadFrequently: true }); g.drawImage(c, 0, 0, 216, 128);
  const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++;
  return { cover: +(n / (216 * 128)).toFixed(4), hash: hashOf(c) }; };
"""
t0 = time.time()
with Lab("r26-checka", size=size, theme=theme) as lab:
    lab.prelude += HELP
    lab.js("$('mode-l').click(); await sleep(300); $('learnFollowShape').click(); await sleep(300); L.shape.pause(); $('learnShapeSpeed').value = 'fast'; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true })); return 1;")
    for space in (2, 3):
        for kind in ("m", "j", "both"):
            lab.js("L.shape.set({ kind: %s, space: %d, c: [-0.1226, 0.7449, 0], pos: 0 }); await sleep(200); window.__seen = { pos: [], say: new Set(), rest: new Set(), back: 0, notes: new Set(), frames: 0, worst: 0 };"
                   "const W = window.__seen; let last = performance.now(); const tick = t => { W.frames++; W.worst = Math.max(W.worst, t - last); last = t; if (!W.stop) requestAnimationFrame(tick); }; requestAnimationFrame(tick);"
                   "$('learnShapePlay').click(); return 1;" % (json.dumps(kind), space))
            t1 = time.time(); prev = -1; back = 0; rests = set(); says = set(); notes = set(); n = 0
            while time.time() - t1 < 60:
                s = lab.js("const s = L.shape.state(), e = $('learnShapeSay'); return [s.playing, s.pos, e.textContent, s.note, $('learnShapeWhere').textContent];")
                n += 1
                if s[1] < prev - 1e-9: back += 1
                prev = s[1]
                if abs(s[1] - round(s[1])) < 1e-9: rests.add(int(round(s[1])))
                says.add(s[2])
                if s[3]: notes.add(s[3])
                if not s[0]: break
                time.sleep(0.12)
            took = time.time() - t1
            end = lab.js("window.__seen.stop = true; const s = L.shape.state(); return { playing: s.playing, pos: s.pos, sentence: s.sentence, where: $('learnShapeWhere').textContent, frames: window.__seen.frames, worstGap: Math.round(window.__seen.worst), play: $('learnShapePlay').textContent, look: %s };" % ("look3()" if space == 3 else "0"))
            row = "%dD %-4s: %.1f s, read %d times, slider went back %d times, sentences seen %d, notes %s; end: %s" % (space, kind, took, n, back, len(says), sorted(notes), json.dumps(end))
            log(row)
            if end["playing"] or end["pos"] != 16 or back or notes or end["play"] != "Play":
                defects.append("%dD %s: play did not end cleanly on step 16: %s" % (space, kind, row))
            if space == 2:
                info = lab.js(cpix.INFO)
                S = cpix.Scene(info)
                r = cpix.check(S, lab.grab("#learnShapeCanvas"), 16)
                log("      the picture the play ended on, against the reference at step 16 (stage %d x %d): %s" % (S.W, S.H, json.dumps(r)))
                if r["miss"] or r["extra"] or r["inside"] < 0: defects.append("%dD %s: the picture the play ended on is not shape 16: %s" % (space, kind, json.dumps(r)))
            else:
                h = lab.js("await sleep(300); L.shape.state(); await sleep(200); const a = look3(); L.shape.goto(3); L.shape.goto(16); await sleep(300); L.shape.state(); await sleep(200); const b = look3(); return [a, b];")
                log("      3D picture the play ended on %s, a fresh goto(16) %s: %s" % (json.dumps(h[0]), json.dumps(h[1]), "the same" if h[0]["hash"] == h[1]["hash"] else "DIFFERENT"))
                if h[0]["cover"] <= 0: defects.append("3D %s: nothing drawn at the end of the play" % kind)
                if h[0]["hash"] != h[1]["hash"] and abs(h[0]["cover"] - h[1]["cover"]) > 0.003: defects.append("3D %s: the picture the play ended on is not the picture of step 16: %s" % (kind, json.dumps(h)))
            if size[0] < 500 and kind == "both":
                lab.shot("out/r26/checka/t7-%s-phone-%dd-both-16.png" % (theme, space))
    n = log.problems(lab)
    if n: defects.append("%d console problems: %s" % (n, lab.problems[:3]))
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)
