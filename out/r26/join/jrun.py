"""Round 26, the joiner: build the joined page and drive it.

  python out/r26/join/jrun.py build
      -> dist/r26-join.html, from src/ as it stands (python build.py --name r26-join)
  python out/r26/join/jrun.py go NAME.js [--size 1400x950] [--theme dark|light] [--log NAME] [--page r26-join] [--from core]
      runs the actions that out/r26/join/NAME.js describes: JavaScript text cut into steps by lines that start with
      "//@". Such a line may carry keys for that step: shot=path clip=#sel sleep=0.4 wait=done timeout=60.
      j_prelude.js (helpers) is put in front of every step. In a picture's path NAME stands for the log's name.
      The output goes to out/r26/join/<log>.log as well.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def py(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-W", "ignore"] + list(args), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def steps_of(path, prelude=None):
    with open(prelude or os.path.join(HERE, "j_prelude.js"), encoding="utf-8") as f:
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
    page, size, theme, log = "r26-join", "1400x950", "dark", os.path.splitext(os.path.basename(name))[0]
    rest = args[1:]
    src = None
    while rest:
        k, v = rest[0], rest[1]
        rest = rest[2:]
        if k == "--page": page = v
        elif k == "--size": size = v
        elif k == "--theme": theme = v
        elif k == "--log": log = v
        elif k == "--from": src = v      # a builder's own list: out/r26/<v>/NAME.js with that folder's prelude.js
    if src:
        there = os.path.join(os.path.dirname(HERE), src)
        acts = [{"wait": "done", "timeout": 110}] + steps_of(os.path.join(there, name), os.path.join(there, "prelude.js"))
    else:
        acts = [{"wait": "done", "timeout": 110}] + steps_of(os.path.join(HERE, name))
    for a in acts:
        if "shot" in a:
            a["shot"] = a["shot"].replace("NAME", log)
            if src:      # a builder's pictures stay out of that builder's folder
                a["shot"] = a["shot"].replace("out/r26/%s/" % src, "out/r26/join/%s-" % src)
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26join-")
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "build":
        r = py("build.py", "--name", "r26-join")
        print((r.stdout + r.stderr).strip())
        sys.exit(r.returncode)
    if sys.argv[1] == "go":
        sys.exit(go(sys.argv[2:]))
    sys.exit(__doc__)
