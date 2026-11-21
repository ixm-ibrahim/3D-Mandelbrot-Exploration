"""Render Kleinian settings on the baseline build and lay the pictures out on contact sheets.

    from klein_render import render
    render([{"name": ..., "k": {...}, "cam": {...}}, ...], "tag")

Writes out/klein-presets/<tag>-NN.png (one per setting) and out/klein-presets/<tag>-sheet-N.png.
Run as a script to render data/klein-presets.json:
    python notes/klein_render.py [tag] [page] [--light] [--phone] [--fine]
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "klein-presets")
PAGE = "dist/klein-presets.html"
K_DEFAULT = {"mx": 0, "my": 2, "mz": 0, "three": True, "L": 1, "iter": 60, "invR": 1.2, "cx": 1, "cy": 1, "cz": 0}


def render(items, tag, cols=3, aa=4, size="1400x950", theme="dark", sheet=True, thumb=(431, 350), extra_js="", page=PAGE):
    os.makedirs(OUT, exist_ok=True)
    acts = [{"js": "document.getElementById('mode-k').click(); return 'kleinian';", "wait": "done"}]
    paths = []
    for i, it in enumerate(items):
        k = dict(K_DEFAULT); k.update(it["k"])
        cam = {"yaw": 0.35, "pitch": 0.35, "dist": 7, "target": [0, 0, 0]}
        cam.update(it.get("cam", {}))
        path = "out/klein-presets/%s-%02d.png" % (tag, i)
        js = ("const L = window.squaringLab; Object.assign(L.S.k, %s); Object.assign(L.cam, %s); L.S.q.aa = %d; %s"
              "L.syncControls(); L.touch(); return %s;") % (json.dumps(k), json.dumps(cam), aa, extra_js, json.dumps(it.get("name", str(i))))
        acts.append({"js": js, "wait": "done", "timeout": 120, "shot": path, "clip": "#stage"})
        paths.append(os.path.join(ROOT, path))
    steps = os.path.join(OUT, tag + "-steps.json")
    with open(steps, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
    for attempt in range(3):     # the machine is shared: now and then a browser start times out
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", os.path.join(ROOT, page),
                            "--actions", steps, "--size", size, "--theme", theme], capture_output=True, text=True, cwd=ROOT)
        if all(os.path.exists(p) for p in paths):
            break
        print("shot.py did not finish (exit %s), trying again" % r.returncode)
    tail = [ln for ln in r.stdout.splitlines() if "wrote" not in ln and "result" not in ln and "waited" not in ln]
    print("\n".join(tail) or "(no output)")
    if r.returncode != 0:
        print("shot.py exit code", r.returncode, r.stderr[-400:])
    if not sheet:
        return paths
    per = cols * 2
    sheets = []
    for s in range(0, len(items), per):
        chunk = items[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        W, H = thumb
        img = Image.new("RGB", (cols * W, rows * (H + 30)), (20, 20, 24))
        d = ImageDraw.Draw(img)
        for j, it in enumerate(chunk):
            x, y = (j % cols) * W, (j // cols) * (H + 30)
            try:
                im = Image.open(paths[s + j]).convert("RGB").resize((W, H), Image.LANCZOS)
                img.paste(im, (x, y + 30))
            except Exception as e:
                d.text((x + 6, y + 40), "missing: %s" % e, fill=(255, 120, 120))
            d.text((x + 6, y + 3), "%d. %s" % (s + j, it.get("name", ""))[:70], fill=(240, 240, 240))
            d.text((x + 6, y + 15), it.get("sub", "")[:75], fill=(170, 170, 180))
        p = os.path.join(OUT, "%s-sheet-%d.png" % (tag, s // per))
        img.save(p)
        sheets.append(p)
    print("sheets:", *sheets, sep="\n  ")
    return paths


HIDE_UI = "document.querySelector('.stage-bar').style.display = 'none'; document.getElementById('triad').style.display = 'none'; "


def measure(path):
    """How far the object reaches from the middle of the stage, in units of half the stage height
    (the camera looks at the origin, which is drawn in the middle). Returns dict(ext, extx, exty, fill, cx, cy)."""
    import numpy as np
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    H, W, _ = im.shape
    bg = np.median(im[2:12, W - 40:W - 4].reshape(-1, 3), axis=0)
    obj = np.abs(im - bg).sum(2) > 40
    obj[:3] = obj[-3:] = False; obj[:, :3] = obj[:, -3:] = False     # the stage border
    ys, xs = np.nonzero(obj)
    if len(xs) == 0:
        return dict(ext=0.0, extx=0.0, exty=0.0, fill=0.0, cx=0.0, cy=0.0, edge=False)
    hx = (xs - W / 2) / (H / 2); hy = (H / 2 - ys) / (H / 2)
    edge = bool(xs.min() <= 4 or xs.max() >= W - 5 or ys.min() <= 4 or ys.max() >= H - 5)
    return dict(ext=float(max(np.abs(hx).max(), np.abs(hy).max())), extx=float(np.abs(hx).max()), exty=float(np.abs(hy).max()),
                fill=float(obj.mean()), cx=float(hx.mean()), cy=float(hy.mean()), edge=edge)


def fit(items, tag, target=0.66, tries=4):
    """Choose each item's turning-out radius so the object reaches `target` of the way from the middle of
    the stage to its top edge. The picture scales exactly with invR squared, so one measurement is enough,
    unless the object runs off the stage: then the radius is halved and measured again. Items that never
    come inside the stage are marked item['unbounded'] = True."""
    todo = list(range(len(items)))
    for t in range(tries):
        if not todo:
            break
        batch = [items[i] for i in todo]
        # measured with careful ray steps, so that the size is that of the whole object (see klein_stepcheck.py)
        paths = render(batch, "%s-fit%d" % (tag, t), aa=1, sheet=False, extra_js=HIDE_UI + "L.S.q.stepk = 0.4; L.S.q.steps = 600; ")
        again = []
        for i, path in zip(todo, paths):
            m = measure(path)
            it = items[i]
            it["m"] = m
            if m["edge"] or m["ext"] > 0.985:
                it["k"]["invR"] = round(it["k"]["invR"] * 0.5, 4)
                it["unbounded"] = True
                again.append(i)
            elif m["ext"] <= 0.02:
                it["k"]["invR"] = round(it["k"]["invR"] * 2.5, 4)
                it["unbounded"] = True
                again.append(i)
            else:
                it["unbounded"] = False
                if abs(m["ext"] - target) > 0.03:
                    it["k"]["invR"] = round(it["k"]["invR"] * (target / m["ext"]) ** 0.5, 3)
        todo = again
    for it in items:
        m = it.get("m", {})
        it["sub"] = "R=%.3f ext x%.2f y%.2f fill %.2f%s" % (it["k"]["invR"], m.get("extx", 0), m.get("exty", 0), m.get("fill", 0), " UNBOUNDED" if it.get("unbounded") else "")
    return items


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tag = args[0] if args else "final"
    with open(os.path.join(ROOT, "data", "klein-presets.json"), encoding="utf-8") as f:
        presets = json.load(f)
    for p in presets:
        p["name"] = p["name"].replace("°", " deg")     # the sheet's built-in font has no degree sign
        p["sub"] = p["source"]
    phone = "--phone" in sys.argv
    render(presets, tag, theme="light" if "--light" in sys.argv else "dark", aa=8 if "--fine" in sys.argv else 4,
           size="375x720" if phone else "1400x950", cols=6 if phone else 3, thumb=(250, 300) if phone else (431, 350),
           page=args[1] if len(args) > 1 else PAGE)
