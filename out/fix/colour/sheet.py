"""colour fixes: contact sheets of colour settings.
  python out/fix/colour/sheet.py <plan> [--theme light] [--url dist/fix-colour.html] [--tag x] [--quality qBal] [--only 0,3]
Tiles land in out/fix/colour/tiles/, the sheet in out/fix/colour/sheet-<plan>[-tag]-<theme>.png."""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SETUP = """
const L = window.squaringLab, S = L.S, cam = L.cam;
document.getElementById('QUALITY').click();
window.col0 = Object.assign({}, S.colour);
window.col = o => { Object.assign(S.colour, window.col0, o); L.syncControls(); L.touch(); };
window.scene = name => {
  if (window.sceneNow === name) return; window.sceneNow = name;
  const kp = i => { document.getElementById('mode-k').click(); L.applyKleinPreset(L.KLEIN_PRESETS[i]); };
  const jp = i => { document.getElementById('mode-j').click(); L.applyJuliaPreset(L.JULIA_PRESETS[i]); };
  if (name === 'julia') jp(0);
  else if (name === 'rabbit') jp(2);
  else if (name === 'klein') document.getElementById('mode-k').click();
  else if (name === 'mandel') document.getElementById('mode-m').click();
  else if (name === 'classic8') { document.getElementById('mode-m').click(); document.getElementById('ap-classic').click(); S.n = 8; L.refresh(false); }
  else if (name === 'mosaic') { document.getElementById('mode-m').click(); document.getElementById('ap-mercator').click(); S.n = 2; S.mosaic = true; L.syncControls(); L.refresh(false); }
  else if (name === 'neg') { document.getElementById('mode-m').click(); S.mosaic = false; S.n = -2; L.syncControls(); L.refresh(false); }
  else if (name[0] === 'k') kp(+name.slice(1));
  else if (name[0] === 'j') jp(+name.slice(1));
};
window.flat = on => { const f = document.getElementById('flat'); if (f.checked !== on) f.click(); };
return JSON.stringify(S.colour);
"""
U = dict(mode=0, trap=5, by=4, pal=8, rev=True)   # what the user asked the page to open with
OLD = dict(trap=4, by=0, pal=7, rev=False)        # what the page opened with before


def tile(scene, flat=False, label=None, **col):
    bits = ['%s=%s' % (k, v) for k, v in col.items()]
    return {"label": label or (scene + (' 2D' if flat else '') + ': ' + (', '.join(bits) or 'as it opens')),
            "js": "scene(%s); flat(%s); col(%s);" % (json.dumps(scene), 'true' if flat else 'false', json.dumps(col))}


SCENES3 = ['mandel', 'julia', 'rabbit', 'j4', 'klein', 'k2']
SCENES2 = ['mandel', 'julia', 'klein', 'k16']
PLANS = {
 # the user's chosen settings, forced, on whatever build: for the "before" picture
 'user': dict(cols=4, tiles=[tile(s, **U) for s in SCENES3] + [tile(s, True, **U) for s in SCENES2]),
 # the page as it opens, on each scene
 'open': dict(cols=4, tiles=[tile(s) for s in SCENES3] + [tile(s, True) for s in SCENES2]),
 'open3': dict(cols=3, tiles=[tile(s) for s in SCENES3]),
 'open2': dict(cols=4, tiles=[tile(s, True) for s in SCENES2]),
 # glow with every trap shape (p3-1)
 'glow-m': dict(cols=4, tiles=[tile('mandel', trap=t, by=4, pal=7, rev=False) for t in range(7)]),
 'glow-j': dict(cols=4, tiles=[tile('julia', trap=t, by=4, pal=7, rev=False) for t in range(7)]),
 'glow-k': dict(cols=4, tiles=[tile('klein', trap=t, by=4, pal=6, rev=False) for t in range(7)]),
 'glow-2d': dict(cols=4, tiles=[tile('mandel', True, trap=t, by=4, pal=7, rev=False) for t in range(7)]),
 # the old default and the other "colours by" choices: must not have moved
 'old': dict(cols=4, tiles=[tile(s, **OLD) for s in ('mandel', 'julia', 'klein')] + [tile(s, True, **OLD) for s in SCENES2]),
 'side': dict(cols=3, tiles=[tile('julia', trap=t, by=3, pal=7, rev=False) for t in (0, 2, 3, 5)] + [tile('mandel', trap=t, by=3, pal=7, rev=False) for t in (2, 3)]),
 'ray': dict(cols=4, tiles=[tile(s, trap=t, by=0, pal=7, rev=False) for s in ('mandel', 'julia') for t in (2, 3)]),
 'tones': dict(cols=3, tiles=[tile(s, trap=7, pal=7, rev=False) for s in ('mandel', 'julia', 'klein')] + [tile(s, True, trap=7, pal=7, rev=False) for s in ('mandel', 'julia')]),
 'k16': dict(cols=3, tiles=[tile('k16', True), tile('k16', True, **OLD), tile('k0', True, **OLD)]),
 'tuneA': dict(cols=4, tiles=[tile(sc, radius=r, glow=g, **U) for sc in ('mandel', 'julia', 'j4', 'klein') for (r, g) in ((0.7, 1), (0.7, 2.5), (1.0, 1), (1.0, 2.5))]),
 'tuneK': dict(cols=4, tiles=[tile('klein', ty=1, **U), tile('klein', ty=1, radius=1, **U), tile('klein', ty=1, glow=2.5, **U), tile('klein', ty=1, **OLD), tile('k2', ty=1, tx=0, **U), tile('k2', ty=1, radius=1, **U), tile('klein', True, ty=1, **U), tile('klein', radius=2, **U)]),
 'more': dict(cols=3, tiles=[tile('classic8'), tile('mosaic'), tile('neg')]),
 'last': dict(cols=2, tiles=[tile(s, mode=5, pal=7, rev=False) for s in ('mandel', 'julia')]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--theme", default="dark"); ap.add_argument("--url", default="dist/fix-colour.html")
    ap.add_argument("--tag", default=""); ap.add_argument("--size", default="1000x640"); ap.add_argument("--tile", type=int, default=440)
    ap.add_argument("--quality", default="qFast"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    plan = PLANS[a.plan]
    tiles = plan["tiles"]
    if a.only:
        tiles = [tiles[int(i)] for i in a.only.split(",")]
    name = a.plan + ("-" + a.tag if a.tag else "")
    tdir = os.path.join(HERE, "tiles")
    os.makedirs(tdir, exist_ok=True)
    paths = [os.path.join(tdir, "%s-%s-%02d.png" % (name, a.theme, i)) for i in range(len(tiles))]
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
    actions = [{"js": SETUP.replace("QUALITY", a.quality)}]
    for t, p in zip(tiles, paths):
        actions.append({"js": t["js"], "wait": "done", "timeout": 400, "shot": p, "clip": "#stage"})
    apath = os.path.join(tdir, "%s-actions.json" % name)
    with open(apath, "w", encoding="utf-8") as f:
        json.dump(actions, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", a.url, "--actions", apath,
                        "--theme", a.theme, "--size", a.size], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    print("\n".join(l for l in r.stdout.splitlines() if "wrote" not in l and "waited" not in l))
    if r.stderr.strip():
        print(r.stderr[-2000:])
    ims = [(Image.open(p).convert("RGB"), t["label"]) for p, t in zip(paths, tiles) if os.path.exists(p)]
    if not ims:
        sys.exit("no tiles were written")
    cols, tw = min(plan.get("cols", 3), len(ims)), a.tile
    th = round(tw * ims[0][0].height / ims[0][0].width)
    rows = (len(ims) + cols - 1) // cols
    lab = 18
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    for i, (im, label) in enumerate(ims):
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab))
        d.text((x + 4, y + 2), label, fill=(235, 235, 235), font=font)
    out = os.path.join(HERE, "sheet-%s-%s.png" % (name, a.theme))
    sheet.save(out)
    print("sheet:", out, "%dx%d" % (sheet.width, sheet.height))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
