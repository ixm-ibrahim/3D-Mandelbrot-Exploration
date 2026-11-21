"""Check 5: with Follow = One point the old Learn is what it was.
The same list of states is set on the frozen page (dist/r26-checka-base.html, built from base18a) and on the page
under test (dist/r26-checka.html): four approaches, the three spaces, five places in a step each, and a few extras
(power 3 with |x|, the start at 0, the hidden direction, a zoomed and a turned view). For every state:
LEARN.state() of the two pages, and the pixels of the stage and of the transport under it.
(The panel is not compared pixel for pixel: it has the new choice "Follow" at its top, which moves the rest down.
Its texts are compared instead.)
"""
import json, sys, time
import numpy as np
from clab import Lab, Log

log = Log("t8_old")
APS = ["mercator", "lathe", "pulledplane", "bulb"]
STATES = []
for ap in APS:
    for sp in (1, 2, 3):
        pre = "await pickAp('%s'); L.set({ space: %d }); L.set({ show: 'circle' }); L.again();" % (ap, sp)
        STATES += [
            ("%s %dD start" % (ap, sp), pre + "L.goto(0, 0);"),
            ("%s %dD move 0 half" % (ap, sp), pre + "L.goto(0, 0.5);"),
            ("%s %dD move 1 at 0.35" % (ap, sp), pre + "L.goto(1, 0.35);"),
            ("%s %dD second step, end" % (ap, sp), pre + "L.next(); L.goto(9, 1);"),
            ("%s %dD all directions" % (ap, sp), pre + "L.set({ show: 'all' }); L.goto(1, 0.6);"),
        ]
EXTRA = [
    ("power 3 and |x|, 2D", "await pickAp('mercator'); L.set({ space: 2, show: 'circle' }); L.again(); setRule(3, [1,0,0], [0,0]); L.goto(1, 0.5);"),
    ("power 3 and |x|, 3D", "L.set({ space: 3 }); L.goto(0, 0.7);"),
    ("power 2.5, 3D lathe", "setRule(2.5, [0,0,0], [0,0]); await pickAp('lathe'); L.goto(1, 0.3);"),
    ("back to power 2; start at 0, 2D", "setRule(2, [0,0,0], [0,0]); await pickAp('mercator'); L.set({ space: 2 }); $('learnZero').click(); L.goto(0, 0.5);"),
    ("hidden direction, 2D", "L.set({ space: 2, hidden: true, z: [0.7, 0.4, 0] }); L.goto(0, 0.5);"),
    ("hidden direction, 1D", "L.set({ space: 1, hidden: true }); L.goto(0, 0.5);"),
    ("1D without the hidden direction", "L.set({ space: 1, hidden: false }); L.goto(0, 0.5);"),
    ("3D zoomed with the wheel", "L.set({ space: 3 }); L.goto(0, 0.5); $('stage').dispatchEvent(new WheelEvent('wheel', { deltaY: -300, clientX: 500, clientY: 400, bubbles: true, cancelable: true }));"),
    ("3D turned by a drag", "const cv = $('learnCanvas'); ptr(cv, 'pointerdown', 300, 200); ptr(cv, 'pointermove', 380, 250); ptr(cv, 'pointerup', 380, 250);"),
    ("the c of the Julia tab, 3D", "$('learnJuliaC').click(); L.goto(2, 0.5);"),
    ("after the panel's reset", "document.querySelector('#learnReset button').click();"),
]
TEXTS = "return ['learnWhere', 'learnSay', 'learnNote', 'learnNotice', 'learnHiddenNote', 'learnHint', 'learnMoves'].map(id => $(id) ? $(id).textContent : null).concat([document.querySelector('#learnPanel summary').textContent, document.title]);"


def walk(page, size, theme, states):
    out = []
    with Lab(page, size=size, theme=theme) as lab:
        lab.js("$('mode-l').click(); await sleep(400); return 1;")
        for name, code in states:
            lab.js(code + "\nawait frame(); await sleep(60); return 1;")
            st = lab.js("return L.state();")
            out.append((name, st, lab.grab("#stage"), lab.grab("#learnBar"), lab.js(TEXTS)))
        out.append(("console", list(lab.problems), None, None, None))
    return out


defects = []
t0 = time.time()
for size, theme, states in (((1400, 950), "dark", STATES + EXTRA), ((1400, 950), "light", STATES[:15] + EXTRA[:3]), ((390, 800), "dark", STATES[:15] + EXTRA[3:8])):
    a = walk("r26-checka-base", size, theme, states)
    b = walk("r26-checka", size, theme, states)
    bad = 0; px = 0
    for (name, sa, ga, ba, ta), (_, sb, gb, bb, tb) in zip(a, b):
        if name == "console":
            log("   console: frozen page %d problems, this page %d problems %s" % (len(sa), len(sb), sb[:2] if sb else ""))
            if sb: defects.append("%s %s: console problems with Follow = One point: %s" % (size, theme, sb[:3]))
            continue
        same_state = json.dumps(sa, sort_keys=True) == json.dumps(sb, sort_keys=True)
        ds = -1 if ga.shape != gb.shape else int((ga != gb).any(-1).sum())
        db = -1 if ba.shape != bb.shape else int((ba != bb).any(-1).sum())
        same_text = ta == tb
        px += ga.shape[0] * ga.shape[1] + ba.shape[0] * ba.shape[1]
        if not same_state or ds or db or not same_text:
            bad += 1
            what = []
            if not same_state: what.append("LEARN.state() differs in " + ", ".join(k for k in sa if json.dumps(sa[k], sort_keys=True) != json.dumps(sb.get(k), sort_keys=True)))
            if ds: what.append("stage: %s pixels differ (sizes %s and %s)" % (ds, ga.shape[:2], gb.shape[:2]))
            if db: what.append("transport: %s pixels differ (sizes %s and %s)" % (db, ba.shape[:2], bb.shape[:2]))
            if not same_text: what.append("texts differ: " + "; ".join("%r -> %r" % (x[:70] if x else x, y[:70] if y else y) for x, y in zip(ta, tb) if x != y))
            log("   DIFFERENT %s: %s" % (name, "; ".join(what)))
            defects.append("%sx%s %s, %s: %s" % (size[0], size[1], theme, name, "; ".join(what)))
            tag = "%dx%d-%s-%s" % (size[0], size[1], theme, name.replace(" ", "_").replace(",", "").replace("|", "abs"))
            Lab.save(None, ga, "out/r26/checka/t8-DIFF-%s-frozen.png" % tag); Lab.save(None, gb, "out/r26/checka/t8-DIFF-%s-now.png" % tag)
    log("%d x %d, %s: %d states on both pages, stage %s and transport %s; %d states differ (state, stage pixels, transport pixels or texts); %d pixels compared" % (
        size[0], size[1], theme, len(states), a[0][2].shape[:2][::-1], a[0][3].shape[:2][::-1], bad, px))
    if (size, theme) == ((1400, 950), "dark"):
        from PIL import Image
        Image.fromarray(a[7][2]).save(__file__.replace("t8_old.py", "t8-frozen-mercator-2D-move1.png"))
        Image.fromarray(b[7][2]).save(__file__.replace("t8_old.py", "t8-now-mercator-2D-move1.png"))
log("")
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)
