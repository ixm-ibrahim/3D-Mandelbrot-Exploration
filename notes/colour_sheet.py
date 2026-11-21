"""Render a contact sheet of colour settings with tools/shot.py and stitch the tiles into one picture.

  python notes/colour_sheet.py out/colour/plan-x.json [--theme dark|light] [--url dist/colour.html]

The plan is JSON:
  { "name": "x", "size": "760x560", "cols": 3, "tile": 430, "clip": "#stage",
    "setup": "<javascript run once>", "tiles": [ { "label": "...", "js": "<javascript>" }, ... ] }
Each tile runs its js, waits until the picture is fully drawn, and captures the clip.
The sheet is written to out/colour/sheet-<name>-<theme>.png.
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--theme", default="dark"); ap.add_argument("--url", default="dist/colour.html")
    a = ap.parse_args()
    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)
    name, tiles = plan["name"], plan["tiles"]
    tdir = os.path.join(ROOT, "out", "colour", "tiles")
    os.makedirs(tdir, exist_ok=True)
    paths = [os.path.join(tdir, "%s-%s-%02d.png" % (name, a.theme, i)) for i in range(len(tiles))]
    for p in paths:   # never stitch a tile left over from an earlier run
        if os.path.exists(p):
            os.remove(p)
    actions = [{"js": plan.get("setup", "return 0;")}]
    for t, p in zip(tiles, paths):
        actions.append({"js": t["js"], "wait": "done", "timeout": 150, "shot": p, "clip": plan.get("clip", "#stage")})
    apath = os.path.join(tdir, "%s-actions.json" % name)
    with open(apath, "w", encoding="utf-8") as f:
        json.dump(actions, f)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", a.url, "--actions", apath,
                        "--theme", a.theme, "--size", plan.get("size", "760x560")], cwd=ROOT, capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if "wrote" not in l and "waited" not in l))
    if r.stderr.strip():
        print(r.stderr[-2000:])
    cols, tw = plan.get("cols", 3), plan.get("tile", 430)
    ims = [Image.open(p).convert("RGB") for p in paths if os.path.exists(p)]
    if not ims:
        sys.exit("no tiles were written")
    th = round(tw * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    lab = 18
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(ims):
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab))
        d.text((x + 4, y + 2), tiles[i]["label"], fill=(235, 235, 235), font=font)
    out = os.path.join(ROOT, "out", "colour", "sheet-%s-%s.png" % (name, a.theme))
    sheet.save(out)
    print("sheet: out/colour/sheet-%s-%s.png  %dx%d" % (name, a.theme, sheet.width, sheet.height))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
