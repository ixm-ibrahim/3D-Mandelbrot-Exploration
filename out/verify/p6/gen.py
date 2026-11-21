import json, os
D = "out/verify/p6/"
names = ["Basilica","San Marco","Douady rabbit","Airplane","Cauliflower","Siegel disc","Dendrite","Kokopelli","Fat rabbit","Feigenbaum point","Golden ratio","−0.8 + 0.156i","0.285 + 0.01i","−0.4 + 0.6i","−0.70176 − 0.3842i","−0.835 − 0.2321i","−0.7269 + 0.1889i","0.45 + 0.1428i","Cracked Basilica","Thorn crystal","Split conch","Flint","Plated egg","Plated ball","Cracked gourd","Pitted gourd"]
init = "const L = window.squaringLab, $ = id => document.getElementById(id); L.R.warmOn = false; $('mode-j').click(); $('qFast').click(); return 'julia fast';"
def click(i):
    return ("const L = window.squaringLab, $ = id => document.getElementById(id); const items = [...document.querySelectorAll('#juliaList .plist-item')]; const b = items[%d]; b.click(); await new Promise(r => setTimeout(r, 100)); "
            "const on = [...document.querySelectorAll('#juliaList .plist-row.is-on')].map(r => r.firstChild.textContent); "
            "return { name: b.textContent, c: L.S.c.slice(), dials: [$('cxNum').value, $('cyNum').value, $('czNum').value], planes: L.S.param.mercator.planes, iter: L.S.iter, on, note: $('juliaNote').textContent.slice(0, 50), cam: [L.cam.yaw, L.cam.pitch, L.cam.dist], n: items.length };" % i)
for part, rng in (("a", range(0, 9)), ("b", range(9, 18)), ("c", range(18, 26))):
    acts = [{"js": init, "wait": "done", "timeout": 300}]
    for i in rng:
        acts.append({"js": click(i), "wait": "done", "timeout": 300, "shot": D + "pre-%02d.png" % i, "clip": "#stage"})
    json.dump(acts, open(D + "pre_%s.json" % part, "w", encoding="utf-8"), ensure_ascii=False)
# 2D view of classics
acts = [{"js": init + "", "wait": "done", "timeout": 300}, {"js": "document.getElementById('flat').click(); return window.squaringLab.S.flat;", "wait": "done", "timeout": 300}]
for i in (0, 1, 2, 3, 4, 5, 6):
    acts.append({"js": click(i), "wait": "done", "timeout": 300, "shot": D + "flat-%02d.png" % i, "clip": "#stage"})
json.dump(acts, open(D + "flat.json", "w", encoding="utf-8"), ensure_ascii=False)
