"""Round 26, the fixer: drive a page and keep the pictures, with my own lists or with a checker's.

  python out/r26/fix/frun.py build
      -> dist/r26-fix.html from src/ as it stands (python build.py --name r26-fix)

  python out/r26/fix/frun.py go NAME.js [--from fix|checkb|join|core] [--page r26-fix] [--size 1400x950]
                                        [--theme dark|light] [--log NAME] [--sub "OLD=>NEW"]
      runs the actions that out/r26/<from>/NAME.js describes: JavaScript text cut into steps by lines that start with
      "//@". Such a line may carry keys for that step: shot=path clip=#sel sleep=0.4 wait=done timeout=60 repeat=20
      ("##" in the picture's path and "__I__" in the JavaScript become the count). That folder's prelude is put in
      front of every step (fix: f_prelude.js, checkb: e_prelude.js, join: j_prelude.js, core: prelude.js).
      In a picture's path NAME stands for the log's name. Pictures and the log always go to out/r26/fix/, never to
      the other folder: "out/r26/<from>/" in a picture's path becomes "out/r26/fix/<from>-".

  python out/r26/fix/frun.py a SCRIPT.py [--page r26-fix] [--tag after] [--sub "OLD=>NEW"] [the script's own arguments]
      runs one of the arithmetic checker's scripts (out/r26/checka/SCRIPT.py) on another page: its log goes to
      out/r26/fix/a-<tag>-<script>.log and its pictures to out/r26/fix/a-<tag>-*.png. Nothing in out/r26/checka/
      is written. --sub runs the script with one piece of its text changed (said in the notes where it is used).

  python out/r26/fix/frun.py sheet OUT.png COLSxSCALE [--crop x,y,w,h] pic1.png pic2.png ...
      tiles pictures into one sheet, each with its file name.
"""
import json, os, runpy, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
R26 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(R26))
PRELUDES = {"fix": "f_prelude.js", "checkb": "e_prelude.js", "join": "j_prelude.js", "core": "prelude.js"}


def py(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-W", "ignore"] + list(args), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def steps_of(path, prelude, subs=()):
    with open(prelude, encoding="utf-8") as f:
        pre = f.read()
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    for old, new in subs:
        if old not in text:
            sys.exit("--sub: %r is not in %s" % (old, path))
        text = text.replace(old, new)
    out, cur, body = [], None, []

    def flush():
        if cur is None:
            return
        act = dict(cur)
        js = "\n".join(body).strip()
        n = int(act.pop("repeat", 1))
        for i in range(n):
            a = dict(act)
            if js:
                a["js"] = pre + "\n" + js.replace("__I__", str(i))
            if "shot" in a:
                a["shot"] = a["shot"].replace("##", "%02d" % i)
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
    page, size, theme, log, src, subs = "r26-fix", "1400x950", "dark", None, "fix", []
    rest = args[1:]
    while rest:
        k, v = rest[0], rest[1]
        rest = rest[2:]
        if k == "--page": page = v
        elif k == "--size": size = v
        elif k == "--theme": theme = v
        elif k == "--log": log = v
        elif k == "--from": src = v
        elif k == "--sub": subs.append(v.split("=>", 1))      # --sub "OLD=>NEW": the list is run with that text changed
    base = os.path.splitext(os.path.basename(name))[0]
    log = log or (base if src == "fix" else "%s-%s" % (src, base))
    there = os.path.join(R26, src)
    acts = [{"wait": "done", "timeout": 110}] + steps_of(os.path.join(there, name), os.path.join(there, PRELUDES[src]), subs)
    for a in acts:
        if "shot" in a:
            s = a["shot"].replace("NAME", log)
            if src != "fix":
                s = s.replace("out/r26/%s/" % src, "out/r26/fix/")
            a["shot"] = s
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26fix-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    try:
        r = py(os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % page, "--actions", tmp, "--size", size, "--theme", theme)
    finally:
        os.remove(tmp)
    text = "page dist/%s.html, size %s, theme %s, actions %s/%s, %s\n" % (page, size, theme, src, name, time.strftime("%Y-%m-%d %H:%M:%S"))
    for old, new in subs:
        text += "with this text of the list changed: %s  =>  %s\n" % (old, new)
    text += r.stdout + r.stderr
    text += "exit code %d\n" % r.returncode
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return r.returncode


def arith(args):
    script = args[0]
    page, tag, subs, extra = "r26-fix", "after", [], []
    rest = args[1:]
    while rest:
        if rest[0] in ("--page", "--tag", "--sub"):
            k, v = rest[0], rest[1]
            rest = rest[2:]
            if k == "--page": page = v
            elif k == "--tag": tag = v
            else: subs.append(v.split("=>", 1))      # --sub "OLD=>NEW": the script is run with that text changed
        else:
            extra.append(rest[0]); rest = rest[1:]
    there = os.path.join(R26, "checka")
    sys.path.insert(0, there)
    os.chdir(ROOT)
    # a --sub that fits the checker's module cpix.py (the pixel reference several scripts share) is applied there
    # too: the module is then loaded from a changed copy in a folder of its own, which is removed afterwards
    import shutil
    mods = None
    with open(os.path.join(there, "cpix.py"), encoding="utf-8") as f:
        cp = f.read()
    if any(old in cp for old, new in subs):
        for old, new in subs:
            cp = cp.replace(old, new)
        mods = os.path.join(HERE, "_mods_%d" % os.getpid())
        os.makedirs(mods, exist_ok=True)
        with open(os.path.join(mods, "cpix.py"), "w", encoding="utf-8", newline="\n") as f:
            f.write(cp)
        sys.path.insert(0, mods)
    import clab
    pre = "a-%s-" % tag
    move = lambda p: p.replace("\\", "/").replace("out/r26/checka/", "out/r26/fix/" + pre)

    class Log(clab.Log):
        def __init__(self, name):
            self.path = os.path.join(HERE, pre + name + ".log")
            self.f = open(self.path, "w", encoding="utf-8")
            for stream in (sys.stdout, sys.stderr):
                try: stream.reconfigure(encoding="utf-8", errors="replace")
                except Exception: pass
            self("log %s on dist/%s.html, %s" % (name, page, time.strftime("%Y-%m-%d %H:%M:%S")))

    class Lab(clab.Lab):
        def __init__(self, name="r26-checka", **kw):
            super().__init__(page if name == "r26-checka" else name, **kw)

        def shot(self, path, clip=None):
            return super().shot(move(path), clip)

        def save(self, arr_or_png, path):
            return super().save(arr_or_png, move(path))

    clab.Log, clab.Lab = Log, Lab
    # the script is run from a copy in this folder, so that a file it writes beside itself lands here too
    copy = os.path.join(HERE, "_run_%d_%s%s" % (os.getpid(), pre, script))
    with open(os.path.join(there, script), encoding="utf-8") as f:
        text = f.read()
    for old, new in subs:
        if old not in text and not mods:
            sys.exit("--sub: %r is not in %s" % (old, script))
        text = text.replace(old, new)
    with open(copy, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    sys.argv = [copy] + extra
    try:
        runpy.run_path(copy, run_name="__main__")
    finally:
        os.remove(copy)
        if mods:
            shutil.rmtree(mods, ignore_errors=True)
    return 0


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
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "build":
        r = py("build.py", "--name", "r26-fix")
        print((r.stdout + r.stderr).strip())
        sys.exit(r.returncode)
    if sys.argv[1] == "go":
        sys.exit(go(sys.argv[2:]))
    if sys.argv[1] == "a":
        sys.exit(arith(sys.argv[2:]))
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2:])
        sys.exit(0)
    sys.exit(__doc__)
