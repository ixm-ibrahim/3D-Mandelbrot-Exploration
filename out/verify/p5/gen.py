"""Writes one shot.py action list per mode into out/verify/p5/."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = "const L = window.squaringLab, $ = id => document.getElementById(id); "
RD = ("const rd = () => ({ res: $('qresNum').value, aa: $('qaaNum').value, steps: $('qstepsNum').value, detail: $('qdetailNum').value, "
      "stepk: $('qstepkNum').value, smooth: $('qsmoothNum').value, de: $('qde').value, deText: $('qde').selectedOptions[0].text, "
      "normals: $('normals').value, shadow: $('qShadow').checked, ao: $('qAO').checked, "
      "sl: [$('qres').value, $('qaa').value, $('qsteps').value, $('qdetail').value].join('/'), "
      "marks: ['qUltra','qFast','qBal','qFine'].map(id => id + ':' + $(id).className + '/' + $(id).getAttribute('aria-pressed') + '/' + getComputedStyle($(id)).backgroundColor + '/' + getComputedStyle($(id)).borderColor).join(' | '), "
      "status: $('status') ? $('status').textContent : '' }); ")

SETUP = {
    "mandel": "L.R.warmOn = false; return 'default mandelbrot';",
    "classic8": "L.R.warmOn = false; $('ap-classic').click(); L.S.n = 8; L.S.iter = 10; L.syncControls(); L.cam.target = [0,0,0]; L.cam.dist = 4.2; L.refresh(false); return 'classic n=8';",
    "lambda": "L.R.warmOn = false; const e = $('eqPreset'), o = [...e.options].find(x => /lambda/.test(x.text)); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); return 'lambda: ' + L.S.eq + ' dist ' + L.cam.dist;",
    "julia": "L.R.warmOn = false; $('mode-j').click(); const b = [...document.querySelectorAll('#juliaList .plist-item')].find(x => x.textContent === 'Douady rabbit'); b.click(); return 'julia rabbit c=' + L.S.c;",
    "klein": "L.R.warmOn = false; $('mode-k').click(); return 'kleinian default ' + JSON.stringify(L.S.k);",
    "flat": "L.R.warmOn = false; $('flat').click(); return '2D view ' + L.S.flat;",
    "mosaic": "L.R.warmOn = false; $('m-mosaic').click(); return 'mosaic ' + L.S.mosaic + ' cell ' + L.S.mosaicCell;",
}
for name, setup in SETUP.items():
    acts = [{"js": PRE + setup, "wait": "done", "timeout": 600}]
    for q in ["qUltra", "qFast", "qBal", "qFine"]:
        acts.append({"js": PRE + RD + "const t0 = performance.now(); $('%s').click(); await new Promise(r => setTimeout(r, 60)); const o = rd(); o.q = JSON.stringify(L.S.q); return o;" % q,
                     "wait": "done", "timeout": 900, "shot": "out/verify/p5/%s-%s.png" % (name, q), "clip": "#stage"})
    json.dump(acts, open(os.path.join(HERE, "run-%s.json" % name), "w", encoding="utf-8"), indent=1)

# distance-estimate choices on thin structures
acts = [{"js": PRE + "L.R.warmOn = false; $('mode-j').click(); return 'julia';", "wait": "done", "timeout": 600}]
for pj in ["Dendrite", "Airplane"]:
    acts.append({"js": PRE + "const b = [...document.querySelectorAll('#juliaList .plist-item')].find(x => x.textContent === '%s'); b.click(); $('qBal').click(); return '%s c=' + L.S.c + ' planes ' + L.S.param.mercator.planes + ' iter ' + L.S.iter;" % (pj, pj), "wait": "done", "timeout": 900})
    for de in [3, 1, 0]:
        acts.append({"js": PRE + "const e = $('qde'); e.value = '%d'; e.dispatchEvent(new Event('change', { bubbles: true })); return 'de ' + L.S.q.de + ' (' + typeof L.S.q.de + ') normals ' + L.S.q.normals + ' sel ' + e.selectedOptions[0].text;" % de,
                     "wait": "done", "timeout": 900, "shot": "out/verify/p5/de-%s-bal-de%d.png" % (pj, de), "clip": "#stage"})
    acts.append({"js": PRE + "$('qUltra').click(); return 'ultra ' + JSON.stringify(L.S.q);", "wait": "done", "timeout": 900, "shot": "out/verify/p5/de-%s-ultra.png" % pj, "clip": "#stage"})
    for de in [1, 3]:
        acts.append({"js": PRE + "const e = $('qde'); e.value = '%d'; e.dispatchEvent(new Event('change', { bubbles: true })); return 'ultra with de ' + L.S.q.de;" % de,
                     "wait": "done", "timeout": 900, "shot": "out/verify/p5/de-%s-ultra-de%d.png" % (pj, de), "clip": "#stage"})
    acts.append({"js": PRE + "$('qFine').click(); return 'fine';", "wait": "done", "timeout": 1200, "shot": "out/verify/p5/de-%s-fine.png" % pj, "clip": "#stage"})
json.dump(acts, open(os.path.join(HERE, "run-de.json"), "w", encoding="utf-8"), indent=1)
print("ok")
