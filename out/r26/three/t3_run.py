"""Run a list of actions against dist/r26-three.html with the test helper (t3_prelude.js) loaded first.

  python out/r26/three/t3_run.py out/r26/three/some-actions.json [--theme dark|light] [--size 1400x950] [--url dist/r26-three.html]

The actions file is what tools/shot.py takes. A "jsfile" key is replaced by the text of that file (relative to this folder).
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def main():
    args = sys.argv[1:]
    path = args[0]
    rest = args[1:]
    url = "dist/r26-three.html"
    if "--url" in rest:
        i = rest.index("--url"); url = rest[i + 1]; del rest[i:i + 2]
    with open(path, encoding="utf-8") as f:
        actions = json.load(f)
    for a in actions:
        if "jsfile" in a:
            with open(os.path.join(HERE, a.pop("jsfile")), encoding="utf-8") as f:
                a["js"] = f.read()
    with open(os.path.join(HERE, "t3_prelude.js"), encoding="utf-8") as f:
        pre = f.read()
    actions = [{"wait": "done", "timeout": 110}, {"js": pre + "\nreturn !!window.T3.view;"}] + actions
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="t3-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(actions, f)
    try:
        code = subprocess.call([sys.executable, "-W", "ignore", os.path.join(ROOT, "tools", "shot.py"), "--url", url, "--actions", tmp] + rest, cwd=ROOT)
    finally:
        os.remove(tmp)
    sys.exit(code)


if __name__ == "__main__":
    main()
