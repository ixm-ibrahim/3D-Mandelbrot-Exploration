"""One picture sheet of every 3D attempt in the lab, all drawn for the same Julia set (the Basilica, c = -1),
from the same side, plus Balls on balls as the look that is wanted.

  python out/tour/make_sheet.py TILES_DIR          draws the single pictures into TILES_DIR, then joins them
  python out/tour/make_sheet.py TILES_DIR --join   only joins pictures that are already there

The sheet is written to out/tour/user-tour-basilica.png. The numbers on the tiles are the numbers of the tour.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "out", "tour", "user-tour-basilica.png")
TILES = [  # (id in the lab, name as the Approach list shows it), in the order of the tour
    ("bulb", "Mandelbulb"), ("classic", "Mandelbulb, classic"), ("split", "Split"),
    ("lathe", "Quaternion square (Lathe)"), ("tilt", "Quaternion square, twisted"),
    ("quat4", "Quaternions, 4D (slices)"), ("rotor", "Rotor square"), ("rotorframe", "Rotor square with a frame"),
    ("axisbulb", "Bulbs about the axis"),
    ("mercator", "Sphere inversions, one plane"), ("fold", "Sphere inversions, two planes"),
    ("softfold", "Blended planes"), ("turnaway", "Turning plane, away"), ("turnalong", "Turning plane, along"),
    ("windsq", "Wind, then square"), ("alongonce", "Along once, then one plane"), ("pulledplane", "Pulled plane"),
    ("kleinsq", "Kleinian squaring, one plane"), ("kleinsq2", "Kleinian squaring, two planes"),
    ("pillow", "Pillow"), ("sqpillow", "Square pillow"),
    ("BALLS", "Balls on balls (the look we want)"),
]
COLS, W = 6, 400


def draw(tiles_dir):
    acts = [{"js": "document.getElementById('mode-j').click()", "wait": "done", "timeout": 120}]
    for k, (aid, name) in enumerate(TILES, 1):
        if aid == "BALLS":
            js = "const L = window.squaringLab; document.getElementById('mode-k').click(); if (L.ballsShow) L.ballsShow();"
        else:
            js = ("const L = window.squaringLab, S = L.S; S.approach = L.APPROACHES.findIndex(a => a.id === '%s');"
                  " S.c = [-1, 0, 0]; S.n = 2; L.syncControls(); L.refresh(); L.frameJuliaPreset(L.JULIA_PRESETS[0]);" % aid)
        acts.append({"js": js, "sleep": 0.4})
        acts.append({"wait": "done", "timeout": 240, "shot": os.path.join(tiles_dir, "%02d.png" % k), "clip": "#stage"})
    steps = os.path.join(tiles_dir, "steps.json")
    with open(steps, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    return subprocess.call([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url",
                            os.path.join(ROOT, "squaring-lab.html"), "--size", "1180x800", "--actions", steps])


def join(tiles_dir):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 19)
    except OSError:
        font = ImageFont.load_default()
    ims = []
    for k, (aid, name) in enumerate(TILES, 1):
        p = os.path.join(tiles_dir, "%02d.png" % k)
        if not os.path.exists(p):
            print("missing", p)
            continue
        im = Image.open(p).convert("RGB")
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        ims.append((k, name, im))
    H, bar = max(im.height for _, _, im in ims), 30
    rows = -(-len(ims) // COLS)
    sheet = Image.new("RGB", (COLS * W, rows * (H + bar)), (16, 18, 22))
    d = ImageDraw.Draw(sheet)
    for i, (k, name, im) in enumerate(ims):
        x, y = (i % COLS) * W, (i // COLS) * (H + bar)
        sheet.paste(im, (x, y + bar))
        d.text((x + 8, y + 5), ("%d  %s" % (k, name)) if k < len(TILES) else name, fill=(235, 235, 235), font=font)
    sheet.save(OUT)
    print("wrote", OUT, sheet.size)


if __name__ == "__main__":
    tiles = sys.argv[1]
    os.makedirs(tiles, exist_ok=True)
    code = 0 if "--join" in sys.argv else draw(tiles)
    join(tiles)
    sys.exit(code)
