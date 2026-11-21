"""Plan for sheet.py: pick entries through the real drop-down and "Frame it" on the page that carries the new data,
at the usual window size, and print the note the page shows for each."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
       "const pick = (id, text) => { const e = $(id), o = [...e.options].find(x => x.text.startsWith(text)); if (!o) throw new Error('no option ' + text); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); }; ")
SETUP = "const L = window.squaringLab; L.R.warmOn = false; document.getElementById('mode-j').click(); L.S.q.aa = 4; L.syncControls(); L.touch(); return 'julia mode';"
names = ["Airplane", "Feigenbaum point", "Thorn crystal", "Basilica", "Cracked Basilica", "Douady rabbit"]
tiles = [{"label": n + " (list entry, then Frame it)", "js": PRE + "pick('juliaPreset', %s); $('juliaFrame').click(); return $('juliaNote').textContent + ' | dist ' + L.cam.dist.toFixed(2);" % json.dumps(n)} for n in names]
json.dump({"name": "list", "size": "1400x950", "cols": 3, "tile": 380, "setup": SETUP, "tiles": tiles}, open(os.path.join(HERE, "plan-list.json"), "w"))
print("plan written")
