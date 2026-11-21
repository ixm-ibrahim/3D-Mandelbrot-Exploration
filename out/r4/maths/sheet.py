"""Render a contact sheet from a plan and stitch the tiles into one picture.

  python out/r4/maths/sheet.py out/r4/maths/plan-x.json [--url dist/r4-maths.html] [--theme dark|light]

The plan is JSON:
  { "name": "x", "size": "1000x640", "cols": 3, "tile": 380, "clip": "#stage",
    "setup": "<javascript run once>", "tiles": [ { "label": "...", "js": "<javascript>" }, ... ] }
Each tile runs its js, waits until the picture is fully drawn, and captures the clip.
The sheet is written to out/r4/maths/sheet-<name>.png, the tiles to out/r4/maths/tiles/.
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = os.path.join(ROOT, "out", "r4", "maths")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--theme", default="dark"); ap.add_argument("--url", default="dist/r4-maths.html")
    a = ap.parse_args()
    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)
    name, tiles = plan["name"], plan["tiles"]
    tdir = os.path.join(HERE, "tiles")
    os.makedirs(tdir, exist_ok=True)
    paths = [os.path.join(tdir, "%s-%02d.png" % (name, i)) for i in range(len(tiles))]
    for p in paths:   # never stitch a tile left over from an earlier run
        if os.path.exists(p):
            os.remove(p)
    actions = [{"js": plan.get("setup", "return 0;"), "wait": "done", "timeout": 300}]
    for t, p in zip(tiles, paths):
        actions.append({"js": t["js"], "wait": "done", "timeout": 300, "shot": p, "clip": t.get("clip", plan.get("clip", "#stage"))})
    apath = os.path.join(tdir, "%s-actions.json" % name)
    with open(apath, "w", encoding="utf-8") as f:
        json.dump(actions, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", a.url, "--actions", apath,
                        "--theme", a.theme, "--size", plan.get("size", "1000x640")], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", env=env)
    print("\n".join(l for l in r.stdout.splitlines() if "wrote" not in l and "waited" not in l))
    if r.stderr.strip():
        print(r.stderr[-3000:])
    print("shot.py exit", r.returncode)
    cols, tw = plan.get("cols", 3), plan.get("tile", 380)
    done = [(t, p) for t, p in zip(tiles, paths) if os.path.exists(p)]
    if not done:
        sys.exit("no tiles were written")
    im0 = Image.open(done[0][1])
    th = round(tw * im0.height / im0.width)
    rows = (len(tiles) + cols - 1) // cols
    lab = 18
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    for i, (t, p) in enumerate(zip(tiles, paths)):
        if not os.path.exists(p):
            continue
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + lab))
        d.text((x + 4, y + 2), t["label"], fill=(235, 235, 235), font=font)
    out = os.path.join(HERE, "sheet-%s.png" % name)
    sheet.save(out)
    print("sheet: out/r4/maths/sheet-%s.png  %dx%d" % (name, sheet.width, sheet.height))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
