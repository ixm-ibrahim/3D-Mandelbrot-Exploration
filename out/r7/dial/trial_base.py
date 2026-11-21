"""Engineer "dial", fix pass 7: what would change on a 375 px touch phone if the usual width of the typed box were
8.5 characters there, as on a desktop, instead of 7.5?  python out/r7/dial/trial_base.py dist/r7-dial.html
Measures every dial on show in each mode, with extreme ranges off and on: its height, whether its number fits,
whether its cluster stays in its column, and the height of the page. Nothing is written to the page's files."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402

drive.URL = sys.argv[1]
drive.HERE = HERE
MEASURE = ("const o = {}; for (const n of document.querySelectorAll('.dial .num')) { const e = n.closest('.dial'); if (!e.checkVisibility()) continue; const h = e.parentElement.getBoundingClientRect(), b = e.querySelector('.dial-box').getBoundingClientRect();"
           " o[n.id] = [Math.round(e.getBoundingClientRect().height), n.scrollWidth <= n.clientWidth, b.left >= h.left - 0.5 && b.right <= h.right + 0.5, Math.round(n.getBoundingClientRect().width * 10) / 10]; }"
           " return { dials: o, pageH: document.documentElement.scrollHeight, over: document.documentElement.scrollWidth - document.documentElement.clientWidth };")
page, proc, prof = drive.launch(375, 812, mobile=True, touch=True, theme="light")
d = drive.Drive(page)
d.load()
drive.open_all(d)
d.js("const s = document.getElementById('exportSize'); s.value = [...s.options].find(o => o.text.startsWith('Typed')).value; s.dispatchEvent(new Event('change', { bubbles: true }));")
total = {"dials": 0, "taller": {}, "cut_now": {}, "cut_then": {}, "out_now": {}, "out_then": {}}
for mode in ("m", "j", "k"):
    for ext in (False, True):
        d.js("document.getElementById('mode-%s').click(); const x = document.getElementById('extreme'); if (x.checked !== %s) x.click(); await new Promise(r => setTimeout(r, 350));" % (mode, "true" if ext else "false"))
        a = d.js(MEASURE)
        d.js("const s = document.createElement('style'); s.id = 'trial'; s.textContent = '@media (pointer: coarse) { .dial .dial-num .num { --dial-w: 8.5ch; } }'; document.body.appendChild(s); await new Promise(r => setTimeout(r, 150));")
        b = d.js(MEASURE)
        d.js("document.getElementById('trial').remove(); await new Promise(r => setTimeout(r, 100));")
        tag = "%s%s" % (mode, "+extreme" if ext else "")
        taller = {k: (a["dials"][k][0], b["dials"][k][0]) for k in a["dials"] if b["dials"][k][0] != a["dials"][k][0]}
        cut_a = [k for k, v in a["dials"].items() if not v[1]]; cut_b = [k for k, v in b["dials"].items() if not v[1]]
        out_a = [k for k, v in a["dials"].items() if not v[2]]; out_b = [k for k, v in b["dials"].items() if not v[2]]
        widths = sorted(set(v[3] for v in b["dials"].values()))
        drive.info("%s: %d dials on show; page height %d -> %d; dials whose height changes: %s; number cut at 7.5: %s, at 8.5: %s; cluster out of its column at 7.5: %s, at 8.5: %s; sideways scroll %s -> %s; box widths at 8.5: %s"
                   % (tag, len(a["dials"]), a["pageH"], b["pageH"], json.dumps(taller), cut_a, cut_b, out_a, out_b, a["over"], b["over"], widths))
d.js("window.squaringLab.resetAll();"); d.idle(120)
drive.finish(page, proc, prof, "trial")
