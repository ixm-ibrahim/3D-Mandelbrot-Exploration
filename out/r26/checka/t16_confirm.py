"""Two findings reproduced the way a reader would reach them, with the page's own controls only.
(1) The Power dial at 1, Follow = A whole shape, Julia shape (c as it opens), 3D: from which step on is nothing left,
    what does the sentence say there, and what does the 2D page say for the same settings?
(2) 3D, Julia shape, c inside the big ball, zoomed in with the wheel: the diamond off the stage and its letter.
"""
import json, time
from clab import Lab, Log

log = Log("t16_confirm")
with Lab("r26-checka") as lab:
    r = lab.js("""
      const setRange = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
      const glc = () => document.querySelector('canvas.learn-shape-gl');
      const cover = () => { const c = glc(); const t = document.createElement('canvas'); t.width = 216; t.height = 128; const g = t.getContext('2d'); g.drawImage(c, 0, 0, 216, 128); const d = g.getImageData(0, 0, 216, 128).data, b = [d[0], d[1], d[2]]; let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]) > 12) n++; return +(n / (216 * 128)).toFixed(4); };
      $('mode-l').click(); await sleep(300); $('learnFollowShape').click(); await sleep(300); $('learnShapePlay').click(); await sleep(100);
      if ($('learnShapePlay').textContent === 'Pause') $('learnShapePlay').click();
      $('learnShapeAgain').click();
      $('learnShapeKindBar').querySelector('input[value=j]').click(); await sleep(100);
      setRange('pow', 1); await sleep(200);
      const rows = [];
      for (const space of ['3', '2']) {
        $('learnShapeSpaceBar').querySelector('input[value="' + space + '"]').click(); await sleep(400);
        for (const k of [0, 4, 8, 9, 10, 12, 16]) { $('learnShapeTicks').children[k].click(); await sleep(space === '3' ? 450 : 80); const s = L.shape.state(); await sleep(space === '3' ? 200 : 0);
          let left = 0; if (space === '3') { for (let i = 0; i <= 20; i++) for (let j = 0; j <= 20; j++) for (let m = 0; m <= 20; m++) { const p = [-2 + i * 0.2, -2 + j * 0.2, -2 + m * 0.2]; if (Math.hypot(...p) <= 2 && ckOut3(p, 'j', s.c, 16) > k) left++; } }
          rows.push([space + 'D', k, $('learnShapeSay').textContent, space === '3' ? 'grid points of the ball left: ' + left + ', picture covers ' + cover() : '']); }
      }
      return { c: L.shape.state().c, n: S.n, rows };""")
    log("(1) power %s, Julia shape, c = %s (as it opens):" % (r["n"], r["c"]))
    for row in r["rows"]: log("    %s step %2d: \"%s\"  %s" % tuple(row))
    lab.js("L.shape.set({ space: 3 }); $('learnShapeTicks').children[12].click(); await sleep(500); L.shape.state(); await sleep(250); return 1;")
    lab.shot("out/r26/checka/t16-power1-3d-julia-step12.png")
    lab.js("L.shape.set({ space: 2 }); await sleep(250); return 1;")
    lab.shot("out/r26/checka/t16-power1-2d-julia-step12.png")
    r = lab.js("""
      const setRange = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
      setRange('pow', 2); await sleep(100);
      L.shape.set({ kind: 'j', space: 3, pos: 3 }); setRange('learnShape-cx', -1.8); setRange('learnShape-cy', 0.9); await sleep(300);
      const a = L.shape.state();
      const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect();
      for (let i = 0; i < 5; i++) { $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -200, clientX: b.left + 430, clientY: b.top + 255, bubbles: true, cancelable: true })); await sleep(120); }
      await sleep(600); const s = L.shape.state(); await sleep(300);
      return { c: s.c, zoom: s.view3.zoom, diamondBefore: a.diamonds, diamond: s.diamonds, stage: [s.panes[0].w, s.panes[0].h] };""")
    log("(2) 3D Julia shape, c = %s, zoom %.2f by the wheel: the diamond was at %s, now at %s on a stage of %s" % (r["c"], r["zoom"], r["diamondBefore"], r["diamond"], r["stage"]))
    lab.shot("out/r26/checka/t16-3d-zoomed-lone-c.png", "#stage")
    log.problems(lab)
