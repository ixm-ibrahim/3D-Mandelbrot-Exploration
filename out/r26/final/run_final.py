"""Round 26, the final look: drive a page with one of my own lists and keep the log and the pictures here.

  python out/r26/final/run_final.py LIST.js [--page r26-final] [--size 1400x950] [--theme dark|light] [--log NAME]
                                            [--def KEY=VALUE ...]

LIST.js (in out/r26/final/) is JavaScript cut into steps by lines that start with "//@". Such a line may carry keys
for that step: shot=path clip=#sel sleep=0.4 wait=done timeout=60 repeat=6 ("##" in the picture's path and "__I__"
in the JavaScript become the count). p_prelude.js is put in front of every step. In a picture's path NAME stands
for the log's name. "__KEY__" in the list's text becomes VALUE for every --def KEY=VALUE.
The log goes to out/r26/final/<log>.log. Nothing is written outside out/r26/final/.
"""
import json, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def steps_of(path, prelude, defs):
    with open(prelude, encoding="utf-8") as f:
        pre = f.read()
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    for k, v in defs.items():
        text = text.replace("__%s__" % k, v)
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


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    name = sys.argv[1]
    page, size, theme, log, defs = "r26-final", "1400x950", "dark", None, {}
    rest = sys.argv[2:]
    while rest:
        k, v = rest[0], rest[1]
        rest = rest[2:]
        if k == "--page": page = v
        elif k == "--size": size = v
        elif k == "--theme": theme = v
        elif k == "--log": log = v
        elif k == "--def":
            a, b = v.split("=", 1)
            defs[a] = b
    log = log or os.path.splitext(os.path.basename(name))[0]
    defs.setdefault("THEME", theme)
    defs.setdefault("SIZE", size)
    acts = [{"wait": "done", "timeout": 110}] + steps_of(os.path.join(HERE, name), os.path.join(HERE, "p_prelude.js"), defs)
    for a in acts:
        if "shot" in a:
            a["shot"] = a["shot"].replace("NAME", log)
            if not a["shot"].replace("\\", "/").startswith("out/r26/final/"):
                sys.exit("a picture must go to out/r26/final/: %s" % a["shot"])
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26final-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % page,
                            "--actions", tmp, "--size", size, "--theme", theme],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    text = "page dist/%s.html, size %s, theme %s, list %s, started %s, took %.0f s\n" % (
        page, size, theme, name, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t0)), time.time() - t0)
    text += r.stdout + r.stderr + "exit code %d\n" % r.returncode
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(text)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
