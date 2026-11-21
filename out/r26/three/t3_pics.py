"""Make pictures of learnShape3d from a list of specs, and (optionally) one sheet that shows them side by side.

  python out/r26/three/t3_pics.py spec.json --theme dark [--sheet sheet.png --cols 3]

spec.json: { "dir": "out/r26/three/pics", "size": [600, 450], "items": [ {...}, ... ] }
An item: { "name": "ball-m", "ap": "mercator", "params": {...}, "n": 2, "kind": "m" | "j" | "both", "c": [x, y, z],
           "pos": 3.5 (a slider position; or "levels": [...]), "warn": "--bad", "extra": { anything merged into o },
           "size": [w, h], "abs": [0,0,0], "flip": [0,0] }
The file written is <dir>/<name>-<theme>.png.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def item_js(it, size):
    w, h = it.get("size", size)
    kind = it.get("kind", "m")
    panes = ("[{ kind: 'm', rect: [0, 0, %d, %d] }, { kind: 'j', rect: [%d, 0, %d, %d] }]" % (w // 2, h, w // 2, w - w // 2, h)) if kind == "both" else "null"
    return """
const T = window.T3, S = T.L.S, it = %s;
T.size(%d, %d);
T.setAp(it.ap || 'mercator');
const a = T.L.APPROACHES[S.approach];
(a.params || []).filter(s => s.key !== undefined).forEach(s => { S.param[a.id][s.key] = s.def; });
if (it.params) Object.assign(S.param[a.id], it.params);
S.n = it.n === undefined ? 2 : it.n;
S.abs = it.abs || [0, 0, 0]; S.flip = it.flip || [0, 0];
const levels = it.levels || T.levelsAt(it.pos || 0);
const o = T.one(it.kind === 'j' ? 'j' : 'm', it.c || [0, 0, 0], levels, it.extra);
const panes = %s;
if (panes) o.panes = panes;
o.colours = T.cols(it.warn);
const r = T.view.draw(o);
await new Promise(f => requestAnimationFrame(() => requestAnimationFrame(f)));
if (!r.ok) return { name: it.name, r };
""" % (json.dumps(it), w, h, panes)


def main():
    args = sys.argv[1:]
    spec_path = args[0]
    theme = "dark"
    sheet = None
    cols = 3
    if "--theme" in args: theme = args[args.index("--theme") + 1]
    if "--sheet" in args: sheet = args[args.index("--sheet") + 1]
    if "--cols" in args: cols = int(args[args.index("--cols") + 1])
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    out_dir = spec.get("dir", "out/r26/three/pics")
    size = spec.get("size", [600, 450])
    # "grid": { "aps": [...], "kinds": [{ "tag", "kind", "c" }], "steps": [...], "extra": {...} } stands for one item per combination
    spec.setdefault("items", [])
    g = spec.get("grid")
    if g:
        for ap in g["aps"]:
            for kd in g["kinds"]:
                for st in g["steps"]:
                    it = {"name": "%s-%s-%s" % (ap, kd["tag"], str(st).replace(".", "_")), "ap": ap, "kind": kd["kind"], "c": kd.get("c", [0, 0, 0]), "pos": st}
                    if g.get("extra"): it["extra"] = g["extra"]
                    if g.get("warn"): it["warn"] = g["warn"]
                    spec["items"].append(it)
    only = None
    if "--only" in args: only = args[args.index("--only") + 1]
    if only: spec["items"] = [it for it in spec["items"] if only in it["name"]]
    os.makedirs(os.path.join(ROOT, out_dir), exist_ok=True)
    actions, files = [], []
    for it in spec["items"]:
        path = "%s/%s-%s.png" % (out_dir, it["name"], theme)
        actions.append({"js": item_js(it, size)})
        actions.append({"sleep": 0.15, "shot": path, "clip": "#t3box"})
        files.append((it["name"], path))
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="t3p-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(actions, f)
    try:
        code = subprocess.call([sys.executable, "-W", "ignore", os.path.join(HERE, "t3_run.py"), tmp, "--theme", theme], cwd=ROOT)
    finally:
        os.remove(tmp)
    if sheet:
        from PIL import Image, ImageDraw
        ims = [(n, Image.open(os.path.join(ROOT, p)).convert("RGB")) for n, p in files if os.path.exists(os.path.join(ROOT, p))]
        scale = float(args[args.index("--scale") + 1]) if "--scale" in args else 1.0
        if scale != 1.0:
            ims = [(n, im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))), Image.LANCZOS)) for n, im in ims]
        if ims:
            w = max(i.size[0] for _, i in ims); h = max(i.size[1] for _, i in ims)
            rows = (len(ims) + cols - 1) // cols
            big = Image.new("RGB", (cols * w, rows * (h + 18)), (40, 40, 40))
            d = ImageDraw.Draw(big)
            for k, (n, im) in enumerate(ims):
                x, y = (k % cols) * w, (k // cols) * (h + 18)
                big.paste(im, (x, y + 18))
                d.text((x + 4, y + 3), n, fill=(255, 255, 255))
            big.save(os.path.join(ROOT, sheet))
            print("sheet", sheet, big.size)
    sys.exit(code)


if __name__ == "__main__":
    main()
