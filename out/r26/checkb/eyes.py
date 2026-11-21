"""Round 26, checker "eyes": drive the joined page the way a reader would and keep the pictures.

  python out/r26/checkb/eyes.py go NAME.js [--size 1400x950] [--theme dark|light] [--log NAME] [--page r26-checkb]
      runs the actions that out/r26/checkb/NAME.js describes: JavaScript text cut into steps by lines that start
      with "//@". Such a line may carry keys for that step: shot=path clip=#sel sleep=0.4 wait=done timeout=60
      repeat=20 (the step is run that many times; "##" in the picture's path and "__I__" in the JavaScript become
      the count, 00, 01, ...). e_prelude.js (helpers) is put in front of every step. In a picture's path NAME
      stands for the log's name. The output goes to out/r26/checkb/<log>.log as well.

  python out/r26/checkb/eyes.py sheet OUT.png COLSxSCALE [--crop x,y,w,h] pic1.png pic2.png ...
      tiles pictures into one sheet (for looking at a run of frames side by side), each with its file name.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def py(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-W", "ignore"] + list(args), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def steps_of(path):
    with open(os.path.join(HERE, "e_prelude.js"), encoding="utf-8") as f:
        pre = f.read()
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    out, cur, body = [], None, []

    def flush():
        if cur is None:
            return
        act = dict(cur)
        js = "\n".join(body).strip()
        n = int(act.pop("repeat", 1))
        for i in range(n):
            a = dict(act)
            tag = "%02d" % i
            if js:
                a["js"] = pre + "\n" + js.replace("__I__", str(i))
            if "shot" in a:
                a["shot"] = a["shot"].replace("##", tag)
            out.append(a)

    for line in text.split("\n"):
        if line.startswith("//@"):
            flush()
            cur, body = {}, []
            for part in line[3:].split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    cur[k] = float(v) if k in ("sleep", "timeout") else v
        elif cur is not None:
            body.append(line)
    flush()
    return out


def go(args):
    name = args[0]
    page, size, theme, log = "r26-checkb", "1400x950", "dark", os.path.splitext(os.path.basename(name))[0]
    rest = args[1:]
    while rest:
        k, v = rest[0], rest[1]
        rest = rest[2:]
        if k == "--page": page = v
        elif k == "--size": size = v
        elif k == "--theme": theme = v
        elif k == "--log": log = v
    acts = [{"wait": "done", "timeout": 110}] + steps_of(os.path.join(HERE, name))
    for a in acts:
        if "shot" in a:
            a["shot"] = a["shot"].replace("NAME", log)
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26eyes-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    try:
        r = py(os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % page, "--actions", tmp, "--size", size, "--theme", theme)
    finally:
        os.remove(tmp)
    text = "page dist/%s.html, size %s, theme %s, actions %s\n" % (page, size, theme, name) + r.stdout + r.stderr
    text += "exit code %d\n" % r.returncode
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return r.returncode


def sheet(args):
    from PIL import Image, ImageDraw
    out, spec = args[0], args[1]
    cols, scale = spec.lower().split("x")
    cols, scale = int(cols), float(scale)
    rest, crop = args[2:], None
    if rest and rest[0] == "--crop":
        crop = [int(v) for v in rest[1].split(",")]
        rest = rest[2:]
    tiles = []
    for p in rest:
        im = Image.open(os.path.join(ROOT, p) if not os.path.isabs(p) else p).convert("RGB")
        if crop:
            im = im.crop((crop[0], crop[1], crop[0] + crop[2], crop[1] + crop[3]))
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        tiles.append((os.path.basename(p), im))
    if not tiles:
        sys.exit("no pictures")
    tw, th, bar = max(t[1].width for t in tiles), max(t[1].height for t in tiles), 16
    rows = (len(tiles) + cols - 1) // cols
    big = Image.new("RGB", (cols * (tw + 4) + 4, rows * (th + bar + 4) + 4), (128, 128, 128))
    d = ImageDraw.Draw(big)
    for i, (name, im) in enumerate(tiles):
        x, y = 4 + (i % cols) * (tw + 4), 4 + (i // cols) * (th + bar + 4)
        d.rectangle([x, y, x + tw, y + bar], fill=(255, 255, 255))
        d.text((x + 3, y + 2), name, fill=(0, 0, 0))
        big.paste(im, (x, y + bar))
    path = os.path.join(ROOT, out) if not os.path.isabs(out) else out
    big.save(path)
    print("wrote %s (%d x %d, %d pictures)" % (out, big.width, big.height, len(tiles)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    if sys.argv[1] == "go":
        sys.exit(go(sys.argv[2:]))
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2:])
        sys.exit(0)
    sys.exit(__doc__)
