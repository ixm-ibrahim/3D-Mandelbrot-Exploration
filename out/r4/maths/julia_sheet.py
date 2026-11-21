"""Contact sheets of the Julia list (data/julia-presets.json) as the page draws it now.

  python out/r4/maths/julia_sheet.py [--url dist/r4-maths-sheet.html] [--aa 4] [--size 1000x640] [--tag a]

For every entry three tiles, each framed with the entry's own camera ("Frame it"):
  1 plane, 14 iterations  |  1 plane, 24 iterations  |  2 planes, 14 iterations (only for entries tuned for 2 planes)
The page's opening colours and Balanced quality are used (with fewer refining passes, --aa, to spare the shared GPU).
Tiles go to out/r4/maths/tiles/, sheets of five entries each to out/r4/maths/julia-sheet-<tag>-<k>.png.
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = os.path.join(ROOT, "out", "r4", "maths")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="dist/r4-maths-sheet.html"); ap.add_argument("--aa", type=int, default=4)
    ap.add_argument("--size", default="1000x640"); ap.add_argument("--tag", default="a")
    ap.add_argument("--stitch-only", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "data", "julia-presets.json"), encoding="utf-8") as f:
        entries = json.load(f)
    tdir = os.path.join(HERE, "tiles")
    os.makedirs(tdir, exist_ok=True)
    tiles = []   # (entry index, column, label, path, js)
    for i, e in enumerate(entries):
        for col, (planes, it) in enumerate(((1, 14), (1, 24), (2, 14))):
            if col == 2 and e.get("planes") != 2:
                continue
            path = os.path.join(tdir, "%s-%02d-%d.png" % (a.tag, i, col))
            js = ("const L = window.squaringLab, S = L.S; S.c = %s; S.iter = %d; S.param.mercator.planes = %d; "
                  "L.syncControls(); L.frameJuliaPreset(%s); L.refresh(false); return %s;"
                  % (json.dumps(e["c"]), it, planes, json.dumps({"name": e["name"], "cam": e["cam"]}),
                     json.dumps("%s, %d plane(s), %d iterations" % (e["name"], planes, it))))
            label = "%d %s: %d plane%s, %d it" % (i + 1, e["name"], planes, "" if planes == 1 else "s", it)
            tiles.append((i, col, label, path, js))
    if not a.stitch_only:
        for t in tiles:
            if os.path.exists(t[3]):
                os.remove(t[3])
        actions = [{"js": "const L = window.squaringLab; L.R.warmOn = false; document.getElementById('mode-j').click(); "
                          "L.S.q.aa = %d; L.syncControls(); L.touch(); "
                          "return 'approach ' + L.APPROACHES[L.S.approach].id + ', colour ' + JSON.stringify(L.S.colour).slice(0, 200);" % a.aa,
                    "wait": "done", "timeout": 300}]
        for t in tiles:
            actions.append({"js": t[4], "wait": "done", "timeout": 300, "shot": t[3], "clip": "#stage"})
        apath = os.path.join(tdir, "%s-actions.json" % a.tag)
        with open(apath, "w", encoding="utf-8") as f:
            json.dump(actions, f)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", a.url, "--actions", apath,
                            "--size", a.size], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env)
        print("\n".join(l for l in r.stdout.splitlines() if "wrote" not in l and "waited" not in l))
        if r.stderr.strip():
            print(r.stderr[-3000:])
        print("shot.py exit", r.returncode)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    tw, lab, per = 380, 18, 5
    first = next((t for t in tiles if os.path.exists(t[3])), None)
    if not first:
        sys.exit("no tiles were written")
    im0 = Image.open(first[3])
    th = round(tw * im0.height / im0.width)
    for k in range(0, len(entries), per):
        rows = min(per, len(entries) - k)
        sheet = Image.new("RGB", (3 * tw, rows * (th + lab)), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for (i, col, label, path, js) in tiles:
            if not (k <= i < k + per) or not os.path.exists(path):
                continue
            x, y = col * tw, (i - k) * (th + lab)
            sheet.paste(Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + lab))
            d.text((x + 4, y + 2), label, fill=(235, 235, 235), font=font)
        out = os.path.join(HERE, "julia-sheet-%s-%d.png" % (a.tag, k // per + 1))
        sheet.save(out)
        print("sheet:", os.path.relpath(out, ROOT).replace("\\", "/"), "%dx%d" % sheet.size)


if __name__ == "__main__":
    main()
