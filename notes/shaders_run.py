"""Run a shader test written as plain .js files through tools/shot.py.

  python notes/shaders_run.py lib.js tests.js --url dist/shaders-t.html [--size 1400x950] [--theme dark]

Each .js file is a list of steps (several files are run one after the other in the same page). A step starts
with a line "//# key=value key=value ..." (wait, timeout, shot, clip, sleep: the keys tools/shot.py understands)
and the lines after it are the JavaScript of that step. Writing the steps as JavaScript instead of JSON keeps
quotes and backslashes readable.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    files = [a for a in sys.argv[1:] if a.endswith(".js")]
    rest = [a for a in sys.argv[1:] if not a.endswith(".js")]
    steps, cur = [], None
    for src in files:
        cur = None
        with open(src, encoding="utf-8") as f:
            for line in f:
                if line.startswith("//#"):
                    cur = {"_js": []}
                    for kv in line[3:].split():
                        k, v = kv.split("=", 1)
                        cur[k] = float(v) if k in ("timeout", "sleep") else v
                    steps.append(cur)
                elif cur is not None:
                    cur["_js"].append(line)
    for s in steps:
        js = "".join(s.pop("_js")).strip()
        if js:
            s["js"] = js
    out = os.path.splitext(files[-1])[0] + ".json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(steps, f, indent=1)
    sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--actions", out] + rest))


if __name__ == "__main__":
    main()
