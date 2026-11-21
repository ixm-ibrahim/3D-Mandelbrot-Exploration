"""Render a list of Julia constants on the baseline build and tile the pictures into contact sheets.

  python notes/julia_render.py --items out/julia-presets/some.json --tag some [--passes 3] [--cols 3] [--per 6]

The items file is a JSON list of objects (data/julia-presets.json itself works: "name" stands in for "label"):
  { "label": "rabbit", "c": [x, y, z],
    "cam": {"yaw":, "pitch":, "dist":},     optional; the lab's own Julia camera when left out
    "planes": 2,                              optional; the sphere-inversion ("mercator") approach's plane count
    "iter": 14,                               optional; iteration count (14 is the lab's default)
    "cut": 0.0,                               optional; switch the cut plane on at this height
    "js": "..." }                             optional; extra page JavaScript run after the state is set (L is the lab handle)

Output: out/julia-presets/<tag>-NN.png (one per item, the stage only) and out/julia-presets/<tag>-sheet-K.png.
The page is dist/julia-presets.html, built with: python build.py --name julia-presets --base base
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "julia-presets")


# On a stage narrower than the one the cameras were chosen on (862 x 701), back off so the set still fits its width.
FIT = "{ const st = document.getElementById('stage'); L.cam.dist *= Math.max(1, 1.2 * st.clientHeight / st.clientWidth); }"


def step_js(it, fit=False):
    cam = it.get("cam") or {}
    js = ["const L = window.squaringLab, S = L.S;",
          "S.c = %s;" % json.dumps(it["c"]),
          "S.param.mercator.planes = %d; S.iter = %d;" % (int(it.get("planes", 2)), int(it.get("iter", 14))),
          # the lab's own Julia camera (resetCam in 50-camera.js), unless the item says otherwise
          "L.cam.target = [0, 0, 0]; L.cam.yaw = %r; L.cam.pitch = %r; L.cam.dist = %r;"
          % (cam.get("yaw", -1.25), cam.get("pitch", 1.0), cam.get("dist", 4.8))]
    if "cut" in it:
        js.append("S.cutOn = true; S.cut = %r;" % it["cut"])
    else:
        js.append("S.cutOn = false;")
    if fit:
        js.append(FIT)
    if it.get("js"):
        js.append(it["js"])
    js.append("L.syncControls(); L.refresh(false); return null;")
    return " ".join(js)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--items", required=True); ap.add_argument("--tag", required=True)
    ap.add_argument("--passes", type=int, default=3, help="refining passes per picture (the lab's default is 12)")
    ap.add_argument("--cols", type=int, default=3); ap.add_argument("--per", type=int, default=6, help="pictures per contact sheet")
    ap.add_argument("--size", default="1400x950"); ap.add_argument("--theme", default="dark")
    ap.add_argument("--thumb", type=int, default=430, help="width of one picture on the contact sheet")
    ap.add_argument("--fit", action="store_true", help="scale each camera distance for a narrow stage (the rule suggested to the UI)")
    a = ap.parse_args()
    with open(a.items, encoding="utf-8") as f:
        items = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    acts = [{"js": "document.getElementById('mode-j').click(); const L = window.squaringLab; L.S.q.aa = %d; "
                   "L.syncControls(); L.touch(); return null;" % a.passes, "wait": "done"}]
    shots = []
    for i, it in enumerate(items):
        path = os.path.join("out", "julia-presets", "%s-%02d.png" % (a.tag, i + 1))
        shots.append(path)
        acts.append({"js": step_js(it, a.fit), "wait": "done", "timeout": 120, "shot": path, "clip": "#stage"})
    steps = os.path.join(OUT, a.tag + "-steps.json")
    with open(steps, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", "dist/julia-presets.html",
                        "--actions", steps, "--size", a.size, "--theme", a.theme], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = [ln for ln in r.stdout.splitlines() if "wrote" not in ln and "waited" not in ln]
    print("\n".join(tail)); print(r.stderr[-2000:] if r.stderr else "", end="")
    os.remove(steps)

    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    for k in range(0, len(items), a.per):
        chunk = list(zip(items[k:k + a.per], shots[k:k + a.per]))
        ims = [Image.open(os.path.join(ROOT, p)).convert("RGB") for _, p in chunk]
        w0, h0 = ims[0].size
        tw, th = a.thumb, round(a.thumb * h0 / w0)
        rows = (len(chunk) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (tw * a.cols, (th + 22) * rows), (16, 18, 22))
        d = ImageDraw.Draw(sheet)
        for j, ((it, _), im) in enumerate(zip(chunk, ims)):
            x, y = (j % a.cols) * tw, (j // a.cols) * (th + 22)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 22))
            label = it.get("label") or "%s  (%d pl)" % (it.get("name", ""), int(it.get("planes", 2)))
            d.text((x + 6, y + 3), "%d. %s" % (k + j + 1, label), fill=(235, 225, 200), font=font)
        name = os.path.join(OUT, "%s-sheet-%d.png" % (a.tag, k // a.per + 1))
        sheet.save(name)
        print("sheet:", os.path.relpath(name, ROOT).replace("\\", "/"))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
