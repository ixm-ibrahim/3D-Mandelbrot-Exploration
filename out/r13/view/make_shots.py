"""Writes out/r13/view/shots-<size>-<theme>.json: the screenshots the brief asks for, mid-move, one file per window size and theme."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const Q = window.squaringLab, L = Q.learn, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));\n"
       "const top = async () => { if (innerWidth < 700) { window.scrollTo(0, $('stage').getBoundingClientRect().top + scrollY - 2); await sleep(250); } };\n")
VIEWS = [
 ("1d-hidden-turn", "L.set({ space: 1, hidden: true, show: 'circle' }); L.goto(0, 0.45);"),
 ("1d-flat-turn", "L.set({ space: 1, hidden: false }); L.goto(0, 0.45);"),
 ("2d-flat-turn", "L.set({ space: 2, hidden: false }); L.goto(0, 0.6);"),
 ("2d-flat-stretch-all", "L.set({ space: 2, hidden: false, show: 'all' }); L.goto(1, 0.6);"),
 ("2d-tipped-turn", "L.set({ space: 2, hidden: true, show: 'circle' }); L.goto(0, 0.6);"),
 ("2d-flat-addc-step3", "L.set({ space: 2, hidden: false }); L.again(); L.next(); L.next(); L.goto(2, 0.6);"),
 ("3d-lathe-turn", "L.again(); $('ap-lathe').click(); L.set({ space: 3 }); L.goto(0, 0.6);"),
 ("3d-lathe-all", "L.set({ show: 'all' }); L.goto(0, 0.6);"),
 ("3d-mercator-lean", "L.set({ show: 'circle' }); $('ap-mercator').click(); L.goto(1, 0.6);"),
 ("3d-tilt-turn", "$('ap-tilt').click(); L.goto(0, 0.6);"),
 ("3d-tilt-back", "L.goto(1, 0.6);"),
 ("3d-bulb-lean", "$('ap-bulb').click(); L.goto(1, 0.6);"),
 ("3d-pillow-own", "$('ap-pillow').click(); L.goto(0, 0.6);"),
 ("3d-split-height", "$('ap-split').click(); L.goto(2, 0.6);"),
 ("3d-lathe-done", "$('ap-lathe').click(); L.goto(9, 1);"),
]
for size in ("1400x950", "375x667"):
    for theme in ("light", "dark"):
        steps = [{"wait": "done", "timeout": 300}, {"js": PRE + "$('mode-l').click(); await sleep(200); return 1;"}]
        for i, (name, code) in enumerate(VIEWS):
            d = {"js": PRE + code + " await top(); await sleep(120); const s = L.state(); return s.moves[s.move] + ' | ' + s.sentence;",
                 "shot": "out/r13/view/shots/%s-%s-%02d-%s.png" % (size, theme, i + 1, name)}
            if size == "1400x950": d["clip"] = ".bench-main"
            steps.append(d)
        with open(os.path.join(HERE, "shots-%s-%s.json" % (size, theme)), "w", encoding="utf-8") as f:
            json.dump(steps, f, ensure_ascii=False, indent=1)
print("wrote 4 files of", len(VIEWS), "shots each")
