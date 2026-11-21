"""Render candidates in the test page, fit each to the frame from its own hit points, and make a contact sheet.
   python out/r4/kleinian/fit.py IN.json TAG [--size 1400x950] [--quality qBal|qFine] [--aa N] [--iter N] [--nofit] [--page dist/x.html]
IN.json: [{name?, k, cam?}]. Without --nofit each item is drawn once to measure it (a grid of pick() calls gives the
points the picture hits), then the turning-out radius and the camera target are set so that the hit points sit in
a ball of radius 1.25 about the target, and it is drawn again. Writes out/r4/kleinian/shots/TAG-NN.png,
TAG-sheet-N.png and TAG-fitted.json (the items with their fitted k and cam)."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
args = sys.argv[1:]


def opt(name, default):
    return args[args.index(name) + 1] if name in args else default


items = json.load(open(args[0], encoding="utf-8"))
tag = args[1]
size = opt("--size", "1400x950")
quality = opt("--quality", "qBal")
aa = opt("--aa", None)
depth = opt("--iter", None)
nofit = "--nofit" in args
page = opt("--page", "dist/r4-kleinian.html")
os.makedirs(os.path.join(HERE, "shots"), exist_ok=True)

first = "const L = window.squaringLab; document.getElementById('mode-k').click(); document.getElementById('%s').click(); " % quality
if aa:
    first += "L.S.q.aa = %s; " % aa
if depth:
    first += "L.S.k.iter = %s; " % depth
acts = [{"js": first + "L.syncControls(); L.touch(); return 1;", "wait": "done", "timeout": 600}]

MEASURE = """
const st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight, hits = [];
let edge = 0;
for (let j = 0; j <= 30; j++) for (let i = 0; i <= 38; i++) {
  const x = 2 + (w - 4) * i / 38, y = 2 + (h - 4) * j / 30, p = L.pick(x, y);
  if (p) { hits.push(p); if (i === 0 || j === 0 || i === 38 || j === 30) edge++; }
}
if (!hits.length) return JSON.stringify({ n: 0 });
const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
for (const p of hits) for (let a = 0; a < 3; a++) { lo[a] = Math.min(lo[a], p[a]); hi[a] = Math.max(hi[a], p[a]); }
const c = lo.map((v, a) => (v + hi[a]) / 2);
let rad = 0; for (const p of hits) rad = Math.max(rad, Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2]));
const s = 1.25 / rad;
L.S.k.invR = +(L.S.k.invR * Math.sqrt(s)).toFixed(3);
const s2 = (L.S.k.invR / R0) ** 2, target = c.map(v => +(v * s2).toFixed(3));
CAM.target = target;
L.frameKleinPreset({ cam: CAM }); L.syncControls(); L.touch();
return JSON.stringify({ n: hits.length, edge, rad: +rad.toFixed(3), invR: L.S.k.invR, target });
"""

for i, it in enumerate(items):
    cam = dict(yaw=-1.35, pitch=1.0, dist=6.4)
    cam.update(it.get("cam", {}))
    k = {key: it["k"][key] for key in ("mx", "my", "mz", "three", "L", "cx", "cy", "cz", "invR")}
    head = "const L = window.squaringLab, CAM = %s, R0 = %s; " % (json.dumps(cam), json.dumps(k["invR"]))
    apply = head + "Object.assign(L.S.k, %s); L.frameKleinPreset({ cam: CAM }); L.syncControls(); L.touch(); return %d;" % (json.dumps(k), i)
    path = "out/r4/kleinian/shots/%s-%02d.png" % (tag, i)
    if nofit:
        acts.append({"js": apply, "wait": "done", "timeout": 900, "shot": path, "clip": "#stage"})
    else:
        acts.append({"js": apply, "wait": "done", "timeout": 600})
        acts.append({"js": head + MEASURE, "wait": "done", "timeout": 900, "shot": path, "clip": "#stage"})

steps = os.path.join(HERE, "shots", tag + "-steps.json")
json.dump(acts, open(steps, "w"))
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", os.path.join(ROOT, page), "--actions", steps, "--size", size],
                   capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
res = {}
for ln in r.stdout.splitlines():
    if ln.startswith("step") and 'result: "{' in ln:
        n = int(ln.split()[1])
        res[(n - 3) // 2] = json.loads(json.loads(ln.split("result: ", 1)[1]))
    elif "PROBLEM" in ln or "TIMED" in ln or "EXCEPTION" in ln or "console" in ln or ln.startswith("  "):
        print(ln)
if r.returncode:
    print("shot.py exit", r.returncode, r.stderr[-300:])

for i, it in enumerate(items):
    m = res.get(i)
    if m and m.get("n"):
        it["k"]["invR"] = m["invR"]
        c0 = dict(yaw=-1.35, pitch=1.0, dist=6.4)
        c0.update(it.get("cam", {}))
        c0["target"] = m["target"]
        it["cam"] = c0
        it["fit"] = m
    extra = ("hits %d edge %d" % (m["n"], m.get("edge", 0))) if m else ""
    it["sub"] = "%s C=(%.3g, %.3g, %.3g) R=%.3g %s" % (it.get("group", ""), it["k"]["cx"], it["k"]["cy"], it["k"]["cz"], it["k"]["invR"], extra)
json.dump(items, open(os.path.join(HERE, "shots", tag + "-fitted.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

W0, H0 = (int(v) for v in size.split("x"))
cols = 4 if W0 > 600 else 6
T = (345, 281) if W0 > 600 else (230, 300)
for s in range(0, len(items), cols * 3):
    chunk = items[s:s + cols * 3]
    rows = (len(chunk) + cols - 1) // cols
    img = Image.new("RGB", (cols * T[0], rows * (T[1] + 30)), (20, 20, 24))
    d = ImageDraw.Draw(img)
    for j, it in enumerate(chunk):
        x, y = (j % cols) * T[0], (j // cols) * (T[1] + 30)
        try:
            im = Image.open(os.path.join(ROOT, "out/r4/kleinian/shots/%s-%02d.png" % (tag, s + j))).convert("RGB")
            im.thumbnail(T, Image.LANCZOS)
            img.paste(im, (x + (T[0] - im.width) // 2, y + 30))
        except Exception:
            d.text((x + 6, y + 40), "missing", fill=(255, 120, 120))
        label = ("%d. %s" % (s + j, it.get("name", ""))).encode("ascii", "replace").decode()
        d.text((x + 4, y + 2), label[:56], fill=(240, 240, 240))
        d.text((x + 4, y + 14), it.get("sub", "").encode("ascii", "replace").decode()[:58], fill=(170, 170, 180))
    out = os.path.join(HERE, "shots", "%s-sheet-%d.png" % (tag, s // (cols * 3)))
    img.save(out)
    print("sheet", out)
