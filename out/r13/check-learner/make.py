"""Checker (first-time learner), round 13. Writes the action files for tools/shot.py:
   walk-desktop.json (1400x950) and walk-phone.json (375x667). Pictures go to out/r13/check-learner/shots/."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const Q = window.squaringLab, L = Q.learn, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));\n"
       "const info = () => { const s = L.state(); const r = v => v.map(x => +x.toFixed(3)); return JSON.stringify({ mv: s.moves[s.move], t: +s.t.toFixed(2), done: s.done, moves: s.moves, pt: r(s.point), z: r(s.z), c: r(s.c), say: s.sentence, shown: $('learnSay').textContent, where: $('learnWhere').textContent, read: '' }); };\n")

def seq(prefix, setup, moments):
    out = []
    first = True
    for name, mv, t in moments:
        code = (setup if first else "") + "L.goto(%d, %s);" % (mv, t)
        first = False
        out.append((prefix + "-" + name, code))
    return out

TURN5 = [("t000", 0, 0), ("t025", 0, 0.25), ("t050", 0, 0.5), ("t075", 0, 0.75), ("t100", 0, 1)]
VIEWS = []
# 1D, hidden direction shown, a negative number
VIEWS += seq("a1d-hid", "L.set({ space: 1, hidden: true, show: 'circle' });", TURN5 + [("stretch050", 1, 0.5), ("stretch100", 1, 1), ("addc050", 2, 0.5), ("done", 2, 1)])
VIEWS += seq("a1d-flat", "L.set({ space: 1, hidden: false });", [("t050", 0, 0.5)])
VIEWS += seq("a1d-hid-all", "L.set({ space: 1, hidden: true, show: 'all' });", [("t050", 0, 0.5)])
# 2D flat
VIEWS += seq("b2d-flat", "L.set({ space: 2, hidden: false, show: 'circle' });", TURN5 + [("stretch050", 1, 0.5), ("addc050", 2, 0.5), ("done", 2, 1)])
# 2D tipped
VIEWS += seq("c2d-tip", "L.set({ space: 2, hidden: true, show: 'circle' });", [("t000", 0, 0), ("t050", 0, 0.5), ("t100", 0, 1), ("stretch050", 1, 0.5), ("addc050", 2, 0.5)])
VIEWS += seq("c2d-tip-neg", "L.set({ space: 2, hidden: true, show: 'circle', z: [-1.2, 0, 0], c: [-0.6, 0, 0] });", [("t050", 0, 0.5)])
# 3D lathe: a point in the flat plane, then well off it
VIEWS += seq("d3d-lathe-flat", "$('ap-lathe').click(); L.set({ space: 3, show: 'circle', z: [0.7, 0.4, 0], c: [-0.3, 0.2, 0.1] });", [("t000", 0, 0), ("t050", 0, 0.5), ("t100", 0, 1), ("stretch050", 1, 0.5), ("addc050", 2, 0.5)])
VIEWS += seq("d3d-lathe-off", "L.set({ space: 3, z: [0.5, 0.2, 0.7], c: [-0.3, 0.2, 0.1] });", [("t000", 0, 0), ("t050", 0, 0.5), ("t100", 0, 1), ("stretch050", 1, 0.5), ("addc050", 2, 0.5), ("done", 2, 1)])
VIEWS += seq("d3d-lathe-up", "L.set({ space: 3, z: [0.5, 0, 0.7] });", [("t050", 0, 0.5)])
VIEWS += seq("d3d-lathe-all", "L.set({ space: 3, show: 'all', z: [0.5, 0.2, 0.7] });", [("t050", 0, 0.5)])
# mercator, tilt, bulb at the same point off the plane
for ap in ("mercator", "tilt", "bulb"):
    VIEWS += [("e3d-%s-m%d-%s" % (ap, j, nm), ("$('ap-%s').click(); L.set({ space: 3, show: 'circle', z: [0.5, 0.2, 0.7], c: [-0.3, 0.2, 0.1] }); " % ap if (j == 0 and nm == "t000") else "") + "L.goto(%d, %s);" % (j, t))
              for j in range(4) for nm, t in (("t000", 0), ("t050", 0.5), ("t100", 1)) if not (j > 0 and nm == "t000")]

def write(fname, size, clip, sub):
    steps = [{"wait": "done", "timeout": 600}, {"js": PRE + "$('mode-l').click(); await sleep(300); return info();"}]
    for name, code in sub:
        js = PRE + code + (" window.scrollTo(0, 420); await sleep(300);" if size == "phone" else " await sleep(150);") + " return '%s ' + info();" % name
        d = {"js": js, "shot": "out/r13/check-learner/shots/%s-%s.png" % (size, name)}
        if clip: d["clip"] = clip
        steps.append(d)
    with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)
    print(fname, len(sub), "shots")

write("walk-desktop.json", "desk", ".bench-main", VIEWS)
PHONE = [v for v in VIEWS if any(k in v[0] for k in ("a1d-hid-t000", "a1d-hid-t025", "a1d-hid-t050", "a1d-hid-t075", "a1d-hid-t100", "a1d-hid-stretch050", "a1d-hid-addc050", "a1d-hid-done",
         "b2d-flat-t050", "b2d-flat-stretch050", "b2d-flat-addc050", "c2d-tip-t050", "c2d-tip-t000", "d3d-lathe-flat-t050", "d3d-lathe-off-t050", "d3d-lathe-off-stretch050", "d3d-lathe-off-addc050",
         "mercator-m0-t050", "mercator-m1-t050", "tilt-m0-t050", "tilt-m1-t050", "bulb-m0-t050", "bulb-m1-t050"))]
# on the phone each set-up has to be repeated, since moments were dropped
PH = []
SETUP = {"a1d-hid": "L.set({ space: 1, hidden: true, show: 'circle' });", "b2d-flat": "L.set({ space: 2, hidden: false, show: 'circle' });", "c2d-tip": "L.set({ space: 2, hidden: true, show: 'circle' });",
         "d3d-lathe-flat": "$('ap-lathe').click(); L.set({ space: 3, show: 'circle', z: [0.7, 0.4, 0], c: [-0.3, 0.2, 0.1] });", "d3d-lathe-off": "$('ap-lathe').click(); L.set({ space: 3, show: 'circle', z: [0.5, 0.2, 0.7], c: [-0.3, 0.2, 0.1] });"}
for name, code in PHONE:
    pre = ""
    for k, s in SETUP.items():
        if name.startswith(k + "-") and "L.set" not in code: pre = s + " "
    if name.startswith("e3d-") and "L.set" not in code:
        ap = name.split("-")[1]
        pre = "$('ap-%s').click(); L.set({ space: 3, show: 'circle', z: [0.5, 0.2, 0.7], c: [-0.3, 0.2, 0.1] }); " % ap
    PH.append((name, pre + code))
write("walk-phone.json", "phone", None, PH)
