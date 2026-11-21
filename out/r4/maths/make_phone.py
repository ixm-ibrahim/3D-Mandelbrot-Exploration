"""out/r4/maths/phone.json: the Sphere inversions panel on a 375 px phone (run with --size 375x812 --theme light)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
steps = [
 {"js": PRE + "L.R.warmOn = false; S.q.aa = 2; L.touch(); document.querySelectorAll('details.sec').forEach(d => { d.open = d.id === 'secApproach'; }); const d = $('par-mercator-planes').closest('.dial'); d.scrollIntoView({ block: 'start' }); window.scrollBy(0, -90); return 'page width ' + document.documentElement.scrollWidth + ' of ' + window.innerWidth + '; planes dial ' + Math.round(d.getBoundingClientRect().width) + ' px wide, label ' + Math.round(d.querySelector('label').getBoundingClientRect().height) + ' px high';",
  "wait": "done", "timeout": 300, "shot": "out/r4/maths/phone-1plane.png"},
 {"js": PRE + "type('par-mercator-planesNum', '2'); const d = $('par-mercator-planes').closest('.dial'); d.scrollIntoView({ block: 'start' }); window.scrollBy(0, -90); return 'page width ' + document.documentElement.scrollWidth;",
  "wait": "done", "timeout": 300, "shot": "out/r4/maths/phone-2planes.png"},
 {"js": PRE + "if (L.setExtreme) L.setExtreme(true); const d = $('par-mercator-planes').closest('.dial'); d.scrollIntoView({ block: 'start' }); window.scrollBy(0, -90); return 'extreme on, page width ' + document.documentElement.scrollWidth;",
  "wait": "done", "timeout": 300, "shot": "out/r4/maths/phone-2planes-wide.png"},
]
json.dump(steps, open(os.path.join(HERE, "phone.json"), "w"))
print("phone.json written")
