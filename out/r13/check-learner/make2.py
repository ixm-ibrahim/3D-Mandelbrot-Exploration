"""Second pass: measurements (camera yaw against the height of z, hinge direction, play timing, label boxes) and
   whole-window pictures of the panel. Writes probe.json (desktop) and light.json (light theme)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const Q = window.squaringLab, L = Q.learn, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));\n")
steps = [{"wait": "done", "timeout": 600}, {"js": PRE + "$('mode-l').click(); await sleep(300); return 1;"}]
# 1. the camera's yaw and the hinge while the height of z is raised under Lathe (the view has not been dragged)
steps.append({"js": PRE + """
$('ap-lathe').click(); L.set({ space: 3, show: 'circle', z: [0.7, 0.4, 0], c: [-0.3, 0.2, 0.1] }); L.goto(0, 0);
const out = [];
for (let h = 0; h <= 0.8001; h += 0.05) {
  L.set({ z: [0.7, 0.4, +h.toFixed(2)] }); L.goto(0, 0);
  const plan = Q.learnPlan({ space: 3, id: 'lathe', params: {}, n: 2, c: [0, 0, 0], abs: [0, 0, 0], flip: [0, 0] });
  const hg = plan.moves[0].hinge([0.7, 0.4, +h.toFixed(2)]);
  out.push(h.toFixed(2) + ' yaw ' + L.view.s3.yaw.toFixed(3) + ' hinge ' + hg.map(x => x.toFixed(2)).join(',') + ' hingeFromZ ' + (Math.acos(Math.min(1, Math.abs(hg[2]))) * 180 / Math.PI).toFixed(0) + 'deg');
}
return out.join(' | ');"""})
# 2. the same for the other approaches at one point: which line is the hinge of the first turning move
steps.append({"js": PRE + """
const out = [];
for (const id of ['lathe', 'mercator', 'tilt', 'bulb', 'classic', 'fold', 'split', 'softfold', 'axisbulb', 'pillow']) {
  $('ap-' + id).click(); L.set({ space: 3, z: [0.5, 0.2, 0.7] }); L.goto(0, 0);
  const s = L.state(), K = L.cache;
  out.push(id + ': ' + s.moves.join('>') + ' hinges ' + K.sheets.map(q => q.hinge ? q.hinge.map(x => x.toFixed(2)).join(',') : '-').join(' ; ') + ' yaw ' + L.view.s3.yaw.toFixed(2) + ' | note: ' + s.note + ' | say0: ' + K.say[0]);
}
return out.join('\\n');"""})
# 3. how long a played step takes at each speed (wall clock)
steps.append({"js": PRE + """
$('ap-lathe').click(); L.set({ space: 2, hidden: false, show: 'circle' }); L.goto(0, 0);
const out = [];
for (const sp of ['normal', 'slow', 'fast']) {
  $('learnSpeed').value = sp; $('learnSpeed').dispatchEvent(new Event('change', { bubbles: true }));
  L.goto(0, 0); const t0 = performance.now(); $('learnPlay').click();
  let t1 = 0; while (performance.now() - t0 < 20000) { await sleep(30); const s = L.state(); if (!t1 && (s.move >= 1 || s.done)) t1 = performance.now(); if (s.done && !s.playing) break; }
  out.push(sp + ': first move ' + ((t1 - t0) / 1000).toFixed(2) + ' s, whole step of 3 moves ' + ((performance.now() - t0) / 1000).toFixed(2) + ' s');
}
$('learnSpeed').value = 'normal'; $('learnSpeed').dispatchEvent(new Event('change', { bubbles: true }));
return out.join(' | ');"""})
# 4. the panel as a reader meets it: whole window, 1D, 2D, 3D
for sp, extra in ((1, "hidden: true"), (2, "hidden: false"), (3, "show: 'circle'")):
    steps.append({"js": PRE + "L.set({ space: %d, %s }); L.reset && 0; L.goto(0, 0.5); window.scrollTo(0, 0); await sleep(200); return $('learnHiddenNote').textContent + ' || ' + $('learnNote').textContent + ' || ' + $('learnNotice').textContent;" % (sp, extra),
                  "shot": "out/r13/check-learner/shots/desk-window-%dd.png" % sp})
# 5. the hidden-direction box in 2D is off at first: what a first visit shows (fresh defaults), and the first sentence
steps.append({"js": PRE + "L.reset(); await sleep(200); $('mode-l').click(); await sleep(300); const s = L.state(); return JSON.stringify({ space: s.space, hidden: s.hidden, z: s.z, c: s.c, say: s.sentence, playing: s.playing, t: s.t });",
              "shot": "out/r13/check-learner/shots/desk-first-visit.png"})
# 6. Next step pressed four times in 2D: the trail
steps.append({"js": PRE + "L.set({ space: 2, hidden: false, show: 'point' }); L.next(); L.next(); L.next(); L.next(); L.goto(0, 0.5); await sleep(150); const s = L.state(); return JSON.stringify({ step: s.step, orbit: s.orbit.map(v => v.map(x => +x.toFixed(2))) });",
              "shot": "out/r13/check-learner/shots/desk-2d-step5.png", "clip": ".bench-main"})
# 7. power 3 on the line and on the page; a negative power
steps.append({"js": PRE + "L.again(); Q.S.n = 3; Q.touch(); await sleep(200); L.set({ space: 1, hidden: true, show: 'circle' }); L.goto(0, 0.5); await sleep(150); const s = L.state(); return s.moves.join('>') + ' | ' + s.sentence + ' | ' + s.note;",
              "shot": "out/r13/check-learner/shots/desk-1d-n3.png", "clip": ".bench-main"})
steps.append({"js": PRE + "Q.S.n = 2; Q.touch(); await sleep(200); return L.state().sentence;"})
with open(os.path.join(HERE, "probe.json"), "w", encoding="utf-8") as f:
    json.dump(steps, f, ensure_ascii=False, indent=1)

light = [{"wait": "done", "timeout": 600}, {"js": PRE + "$('mode-l').click(); await sleep(300); return 1;"}]
for name, code in (("1d-hid-t050", "L.set({ space: 1, hidden: true, show: 'circle' }); L.goto(0, 0.5);"),
                   ("2d-tip-t050", "L.set({ space: 2, hidden: true, show: 'circle' }); L.goto(0, 0.5);"),
                   ("3d-lathe-off-t050", "$('ap-lathe').click(); L.set({ space: 3, show: 'circle', z: [0.5, 0.2, 0.7], c: [-0.3, 0.2, 0.1] }); L.goto(0, 0.5);"),
                   ("3d-mercator-lean", "$('ap-mercator').click(); L.goto(1, 0.5);")):
    light.append({"js": PRE + code + " await sleep(150); return L.state().sentence;", "shot": "out/r13/check-learner/shots/light-%s.png" % name, "clip": "#stage"})
with open(os.path.join(HERE, "light.json"), "w", encoding="utf-8") as f:
    json.dump(light, f, ensure_ascii=False, indent=1)
print("wrote probe.json", len(steps), "and light.json", len(light))
