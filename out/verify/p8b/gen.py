import json, os
D = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
H = "const L = window.squaringLab, $ = id => document.getElementById(id); "
def sel(i):
    return H + "const e = $('kleinPreset'); e.value = e.options[%d].value; e.dispatchEvent(new Event('change', {bubbles: true})); return [%d, e.options[e.selectedIndex].text, L.kleinPresetAt ? 1 : 0, JSON.stringify(L.S.k), L.cam.dist];" % (i, i)
def modek(extra=""):
    return {"js": H + "$('mode-k').click(); " + extra + " return 'k';", "wait": "done", "timeout": 400}
def shot(name, js, timeout=400):
    return {"js": js, "wait": "done", "timeout": timeout, "shot": "%s/%s.png" % (D, name), "clip": "#stage"}
def write(name, acts):
    json.dump(acts, open("%s/%s.json" % (D, name), "w", encoding="utf-8"), indent=0)

# A: all 19 at Balanced (the default)
for tag, rng in (("A1", range(0, 7)), ("A2", range(7, 13)), ("A3", range(13, 19))):
    write(tag, [modek()] + [shot("a-%02d" % i, sel(i)) for i in rng])
# B: Fine for the presets the notes list as lossy
for tag, rng in (("B1", (2, 4, 5)), ("B2", (6, 7, 8)), ("B3", (9, 13, 14))):
    write(tag, [modek("$('qFine').click();")] + [shot("fine-%02d" % i, sel(i), 900) for i in rng])
# D: step share honesty and whether 0.5 is enough (res 1, 4 passes)
acts = [modek("L.S.q.aa = 4; L.syncControls(); L.touch();")]
acts.append({"js": H + "const q = $('qstepk'), n = $('qstepkNum'); const host = q.closest('.dial') || q.parentElement.parentElement; return {slider: q.value, box: n.value, text: host.innerText, sec: $('qstepk').closest('details').innerText.slice(0, 1500)};"})
for i in (2, 5, 8, 14, 0):
    acts.append(shot("d-%02d-s120" % i, sel(i) + ""))
    acts[-1]["js"] = H + "L.S.q.stepk = 1.2; L.S.q.steps = 260; L.syncControls(); " + sel(i).replace(H, "")
    acts.append(shot("d-%02d-s080" % i, H + "L.S.q.stepk = 0.8; L.syncControls(); L.touch(); return 0.8;"))
    acts.append(shot("d-%02d-s050" % i, H + "L.S.q.stepk = 0.5; L.syncControls(); L.touch(); return 0.5;"))
    acts.append(shot("d-%02d-s025" % i, H + "L.S.q.stepk = 0.25; L.S.q.steps = 900; L.syncControls(); L.touch(); return 0.25;"))
write("D", acts)
# C: dial sweeps from three presets at Fast
SW = [("my", [1.0, 1.3, 1.4, 1.45, 1.5, 1.6, 2.2, 2.4]), ("mx", [-1, -0.5, 0.3, 1]), ("mz", [-1, -0.4, 0.2, 0.5, 1]),
      ("L", [0.3, 0.6, 0.8, 1.25, 2.5]), ("iter", [5, 15, 150]), ("invR", [0.4, 2, 3]), ("cx", [-1.5, 1.5]), ("cy", [0, 2.2]), ("cz", [-1, 1])]
for p in (0, 4, 15):
    acts = [modek("$('qFast').click();")]
    for key, vals in SW:
        for v in vals:
            js = sel(p).split(" return ")[0] + " L.S.k.%s = %r; L.syncControls(); L.touch(); return ['%s', %r, $('kleinPreset').value, $('kleinNote').textContent.slice(0, 60)];" % (key, v, key, v)
            acts.append(shot("c-%02d-%s-%s" % (p, key, str(v).replace('-', 'm').replace('.', '_')), js))
    write("C%d" % p, acts)
# E: 2D view and Ultra fast
acts = [modek()]
for i in (0, 1, 3, 4, 8, 13, 16, 18):
    acts.append(shot("e2d-%02d" % i, sel(i).split(" return ")[0] + " if (!$('flat').checked) $('flat').click(); return [L.S.flat, JSON.stringify(L.S.v2)];"))
acts.append({"js": H + "$('flat').click(); $('qUltra').click(); return [L.S.flat, JSON.stringify(L.S.q)];", "wait": "done", "timeout": 400})
for i in (0, 2, 4, 5, 8, 13, 14, 16, 18):
    acts.append(shot("ultra-%02d" % i, sel(i)))
write("E", acts)
# P: phone width, all 19 at Balanced with 4 passes
acts = [modek("L.S.q.aa = 4; L.syncControls(); L.touch();")]
for i in range(19):
    acts.append(shot("p-%02d" % i, sel(i)))
acts.append({"js": "window.scrollTo(0, 0); return [innerWidth, document.documentElement.scrollWidth];", "shot": "%s/p-page.png" % D})
write("P", acts)
print("ok")
