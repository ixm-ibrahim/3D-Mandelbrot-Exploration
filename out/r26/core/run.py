"""Round 26, builder "core": build a test page and drive it.

  python out/r26/core/run.py build                 -> dist/r26-core.html       (the task's test page: no 3D module, so 3D shows the plain note)
  python out/r26/core/run.py build fake            -> dist/r26-core-fake.html  (the same with out/r26/core/fake3d.js in the 3D module's slot)
  python out/r26/core/run.py build three           -> dist/r26-core-three.html (the same with builder "three"'s live src/js/68-learn-shape3d.js)
  python out/r26/core/run.py build base            -> dist/r26-base.html       (the frozen copy, base18a)
  python out/r26/core/run.py go NAME.js [--page core|fake|three|base] [--size 1400x950] [--theme dark|light] [--log NAME]
      runs the actions that out/r26/core/NAME.js describes: the file is JavaScript text cut into steps by lines that
      start with "//@". Such a line may carry keys for that step: shot=path clip=#sel sleep=0.4 wait=done timeout=60.
      prelude.js (helpers) is put in front of every step. The output goes to out/r26/core/<log>.log as well.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MINE = ["src/js/67-learn-shape.js", "src/css/67-learn-shape.css", "src/js/66-learn-view.js", "src/js/90-boot.js"]
PAGES = {
    "core": (["--use"] + MINE, "r26-core"),
    "fake": (["--use"] + MINE + ["--swap", "js/68-learn-shape3d.js=out/r26/core/fake3d.js"], "r26-core-fake"),
    "three": (["--use"] + MINE + ["src/js/68-learn-shape3d.js"], "r26-core-three"),
    "base": ([], "r26-base"),
}


def py(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-W", "ignore"] + list(args), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def build(which):
    extra, name = PAGES[which]
    r = py("build.py", "--name", name, "--base", "base18a", *extra)
    print((r.stdout + r.stderr).strip())
    return r.returncode


def steps_of(path):
    with open(os.path.join(HERE, "prelude.js"), encoding="utf-8") as f:
        pre = f.read()
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    out, cur, body = [], None, []

    def flush():
        if cur is None:
            return
        act = dict(cur)
        js = "\n".join(body).strip()
        if js:
            act["js"] = pre + "\n" + js
        out.append(act)

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
    page, size, theme, log = "core", "1400x950", "dark", os.path.splitext(os.path.basename(name))[0]
    rest = args[1:]
    pre = None
    while rest:
        k, v = rest[0], rest[1]
        rest = rest[2:]
        if k == "--page": page = v
        elif k == "--size": size = v
        elif k == "--theme": theme = v
        elif k == "--log": log = v
        elif k == "--pre": pre = v      # the steps of another file first
    acts = [{"wait": "done", "timeout": 110}] + (steps_of(os.path.join(HERE, pre)) if pre else []) + steps_of(os.path.join(HERE, name))
    for a in acts:      # NAME in a picture's path stands for the log's name, so one list can serve several pages
        if "shot" in a:
            a["shot"] = a["shot"].replace("NAME", log)
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26core-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    try:
        r = py(os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % PAGES[page][1], "--actions", tmp, "--size", size, "--theme", theme)
    finally:
        os.remove(tmp)
    text = "page %s (dist/%s.html), size %s, theme %s, actions %s\n" % (page, PAGES[page][1], size, theme, name) + r.stdout + r.stderr
    text += "exit code %d\n" % r.returncode
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return r.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "build":
        sys.exit(build(sys.argv[2] if len(sys.argv) > 2 else "core"))
    if sys.argv[1] == "go":
        sys.exit(go(sys.argv[2:]))
    sys.exit(__doc__)
