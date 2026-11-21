"""Full-page pictures (one per screenful) and a layout audit, for every mode and theme at one window size.
   python pages.py desk | phone | small | narrow     [modes e.g. mjk] [themes e.g. dark,light]"""
import json, os, sys, time
from lab import Lab, HERE
from PIL import Image

kind = sys.argv[1]
modes = sys.argv[2] if len(sys.argv) > 2 else "mjk"
themes = sys.argv[3].split(",") if len(sys.argv) > 3 else ["dark", "light"]
W, H, MOB = {"desk": (1400, 950, False), "phone": (375, 812, True), "small": (800, 600, False), "narrow": (375, 812, False)}[kind]
AUDIT = open(os.path.join(HERE, "audit.js"), encoding="utf-8").read()
OPEN = "document.querySelectorAll('details.sec').forEach(s => { s.open = true; }); await new Promise(r => setTimeout(r, 300));"

lab = Lab(W, H, themes[0], MOB, wait_idle=150)
res = {}
for theme in themes:
    lab.theme(theme)
    for m in modes:
        tag = "%s-%s-%s" % (kind, theme, m)
        print(tag); sys.stdout.flush()
        lab.js("document.getElementById('mode-%s').click(); await new Promise(r => setTimeout(r, 300));" % m)
        lab.js(OPEN)
        lab.idle(100)
        lab.js("window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 200));")
        a = lab.js(AUDIT)
        res[tag] = a
        with open(os.path.join(HERE, "audit-%s.json" % tag), "w", encoding="utf-8") as f:
            json.dump(a, f, indent=1, ensure_ascii=False)
        paths, total = lab.tiles(os.path.join(HERE, "tile-" + tag))
        print("   page %d px tall, %d screens, hscroll %s" % (total, len(paths), a["hscroll"])); sys.stdout.flush()
        if W <= 500:      # put four phone screens side by side so they can be read at full size
            per = 4
            for s in range(0, len(paths), per):
                grp = paths[s:s + per]
                sheet = Image.new("RGB", (per * (W + 8), H), (255, 0, 255))
                for i, (p, _) in enumerate(grp):
                    sheet.paste(Image.open(p).convert("RGB"), (i * (W + 8), 0))
                sheet.save(os.path.join(HERE, "sheet-%s-%02d.png" % (tag, s // per)))
            for p, _ in paths:
                os.remove(p)
problems = lab.close()
print("PAGE PROBLEMS:", problems[:20])
with open(os.path.join(HERE, "audit-%s-all.json" % kind), "w", encoding="utf-8") as f:
    json.dump({"problems": problems, "res": res}, f, indent=1, ensure_ascii=False)
