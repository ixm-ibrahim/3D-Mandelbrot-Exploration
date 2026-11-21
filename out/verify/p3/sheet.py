"""p3 tester: contact sheets of colour settings on dist/preview.html.  python out/verify/p3/sheet.py <name> [--theme light]"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SETUP = """
const L = window.squaringLab, S = L.S, cam = L.cam;
document.getElementById('qFast').click();
window.col0 = Object.assign({}, S.colour);
window.col = o => { Object.assign(S.colour, window.col0, o); L.syncControls(); L.touch(); };
window.scene = name => {
  if (window.sceneNow === name) return; window.sceneNow = name;
  if (name === 'julia') { document.getElementById('mode-j').click(); L.applyJuliaPreset(L.JULIA_PRESETS[0]); }
  if (name === 'rabbit') { document.getElementById('mode-j').click(); L.applyJuliaPreset(L.JULIA_PRESETS[2]); }
  if (name === 'klein') { document.getElementById('mode-k').click(); }
  if (name === 'klein2') { document.getElementById('mode-k').click(); L.applyKleinPreset(L.KLEIN_PRESETS[2]); }
  if (name === 'mandel') { document.getElementById('mode-m').click(); }
};
window.flat = on => { const f = document.getElementById('flat'); if (f.checked !== on) f.click(); };
return JSON.stringify(S.colour);
"""
PALS = ['Brass and verdigris', 'Ember', 'Glacier', 'Moss and rust', 'Stone', 'Fire', 'Electric', 'Sunset', 'Rainbow', 'Ocean',
        'Neon', 'Classic blue and gold', 'Viridis', 'Aurora', 'Candy', 'Peacock', 'Ice and fire', 'Porcelain', 'Orchid']
TRAPS = ['point', 'cross', 'line', 'ray', 'planes', 'shell', 'ring', 'three tones']
BY = {0: 'bands', 4: 'glow', 1: 'step', 2: 'blend esc', 3: 'side'}
MODES = {0: 'trap', 2: 'escape count', 3: 'dist from centre', 4: 'depth', 5: 'last step dir', 6: 'surface dir', 7: 'clay'}


def tile(scene, flat=False, **col):
    bits = []
    if col.get('mode', 0) != 0: bits.append(MODES[col['mode']])
    if 'trap' in col: bits.append(TRAPS[col['trap']])
    if 'by' in col: bits.append(BY[col['by']])
    if 'pal' in col: bits.append(PALS[col['pal']])
    bits += ['%s=%s' % (k, v) for k, v in col.items() if k not in ('mode', 'trap', 'by', 'pal')]
    return {"label": scene + (' 2D' if flat else '') + ': ' + (', '.join(bits) or 'as it opens'),
            "js": "scene(%s); flat(%s); col(%s);" % (json.dumps(scene), 'true' if flat else 'false', json.dumps(col))}


def trapby(scene, flat=False, **extra):
    t = []
    for tr in range(7):
        for by in (0, 4, 1, 2, 3):
            t.append(tile(scene, flat, trap=tr, by=by, **extra))
    t.append(tile(scene, flat, trap=7, **extra))
    return t


PLANS = {
 'pals-m': dict(cols=5, tiles=[tile('mandel', pal=i) for i in [7, 5, 1, 6, 9, 2, 13, 12, 15, 8, 14, 10, 11, 16, 18, 0, 3, 17, 4]]),
 'trapby-m': dict(cols=5, tiles=trapby('mandel')),
 'trapby-j': dict(cols=5, tiles=trapby('julia')),
 'dials-m': dict(cols=4, tiles=[tile('mandel', trap=0), tile('mandel', trap=0, tx=-1), tile('mandel', trap=0, tx=0.5, ty=0.5, tz=0.5),
     tile('mandel', trap=5, radius=0.2), tile('mandel', trap=5, radius=0.7), tile('mandel', trap=5, radius=1.5),
     tile('mandel', trap=6, radius=0.3), tile('mandel', trap=6, radius=1.2), tile('mandel', trap=4, tx=0.4, ty=0.3),
     tile('mandel', trap=2, axis=0), tile('mandel', trap=2, axis=1), tile('mandel', trap=2, axis=2),
     tile('mandel', trap=3, ray=0), tile('mandel', trap=3, ray=1), tile('mandel', trap=3, ray=2), tile('mandel', trap=3, ray=4),
     tile('mandel'), tile('mandel', rev=True), tile('mandel', bands=3), tile('mandel', bands=0.3), tile('mandel', shift=0.5), tile('mandel', shift=1.0),
     tile('mandel', pal=8, rev=True), tile('mandel', pal=11, bands=6)]),
 'modes': dict(cols=6, tiles=[tile(s, mode=m) for s in ('mandel', 'julia') for m in (2, 3, 4, 5, 6, 7)] + [tile(s, mode=m, pal=6) for s in ('mandel', 'julia') for m in (2, 3, 4, 5, 6, 7)]),
 'flat-trapby-m': dict(cols=5, tiles=trapby('mandel', True)),
 'flat-trapby-j': dict(cols=5, tiles=trapby('julia', True)),
 'flat-misc': dict(cols=6, tiles=[tile('mandel', True, pal=i) for i in [7, 5, 6, 8, 11, 10]] + [tile('mandel', True, mode=m) for m in (2, 3, 4, 5, 6, 7)]
     + [tile('julia', True, mode=m) for m in (2, 3, 4, 5, 6, 7)] + [tile('mandel', True, rev=True), tile('mandel', True, bands=3), tile('mandel', True, shift=0.5),
        tile('mandel', True, trap=0, tx=-1), tile('mandel', True, trap=5, radius=1.5), tile('mandel', True, trap=6, radius=0.3)]),
 'klein': dict(cols=4, tiles=[tile('klein', pal=p) for p in (7, 6, 11)] + [tile('klein', trap=1, by=4, pal=6)]
     + [tile('klein', trap=t, by=b, pal=p) for (t, b, p) in ((0, 0, 7), (5, 0, 5), (6, 4, 9), (7, 0, 7))]
     + [tile('klein', mode=m) for m in (2, 3, 4, 5)] + [tile('klein2', pal=p) for p in (7, 6, 11)] + [tile('klein2', trap=1, by=1, pal=8)]
     + [tile('klein', True, pal=p) for p in (7, 6, 11)] + [tile('klein', True, trap=1, by=4, pal=6)]),
 'light': dict(cols=4, tiles=[tile('mandel'), tile('mandel', pal=6), tile('mandel', pal=11), tile('mandel', pal=4), tile('mandel', pal=17), tile('mandel', trap=1, by=4, pal=5),
     tile('mandel', mode=2), tile('mandel', mode=7), tile('julia'), tile('julia', trap=0, by=4, pal=9), tile('klein'), tile('klein', pal=6),
     tile('mandel', True), tile('mandel', True, trap=1, by=4, pal=6), tile('mandel', True, mode=2, pal=11), tile('julia', True)]),
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("--theme", default="dark"); a = ap.parse_args()
    plan = PLANS[a.name]; tiles = plan["tiles"]; name = a.name
    tdir = os.path.join(HERE, "tiles")
    os.makedirs(tdir, exist_ok=True)
    paths = [os.path.join(tdir, "%s-%s-%02d.png" % (name, a.theme, i)) for i in range(len(tiles))]
    for p in paths:
        if os.path.exists(p): os.remove(p)
    actions = [{"js": SETUP, "wait": "done", "timeout": 300}]
    for t, p in zip(tiles, paths):
        actions.append({"js": t["js"], "wait": "done", "timeout": 300, "shot": p, "clip": "#stage"})
    apath = os.path.join(tdir, "%s-%s-actions.json" % (name, a.theme))
    with open(apath, "w", encoding="utf-8") as f: json.dump(actions, f)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--actions", apath, "--theme", a.theme, "--size", "1000x640"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("\n".join(l for l in r.stdout.splitlines() if "wrote" not in l))
    if r.stderr.strip(): print(r.stderr[-2000:])
    cols, tw = plan.get("cols", 4), plan.get("tile", 330)
    ims = [(i, Image.open(p).convert("RGB")) for i, p in enumerate(paths) if os.path.exists(p)]
    if not ims: sys.exit("no tiles")
    th = round(tw * ims[0][1].height / ims[0][1].width); rows = (len(tiles) + cols - 1) // cols; lab = 18
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab)), (40, 40, 40)); d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("arial.ttf", 13)
    except Exception: font = ImageFont.load_default()
    for i, im in ims:
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab)); d.text((x + 4, y + 2), tiles[i]["label"], fill=(235, 235, 235), font=font)
    out = os.path.join(HERE, "sheet-%s-%s.png" % (name, a.theme)); sheet.save(out)
    print("sheet:", out, sheet.size); sys.exit(r.returncode)


main()
