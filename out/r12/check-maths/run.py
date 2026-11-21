"""Run one JavaScript file in a page through tools/shot.py and save what it returns.
  python out/r12/check-maths/run.py <js file> <page under dist/> <log name> [size]
Run from the project root."""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", "..", ".."))
js, page, log = sys.argv[1], sys.argv[2], sys.argv[3]
size = sys.argv[4] if len(sys.argv) > 4 else "1400x950"
with open(os.path.join(here, js), encoding="utf-8") as f:
    code = f.read()
steps = [{"wait": "done", "timeout": 120}, {"js": code}]
act = os.path.join(here, log + ".actions.json")
with open(act, "w", encoding="utf-8") as f:
    json.dump(steps, f)
env = dict(os.environ, PYTHONIOENCODING="utf-8")
p = subprocess.run([sys.executable, os.path.join(root, "tools", "shot.py"), "--url", os.path.join(root, "dist", page),
                    "--size", size, "--actions", act], cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
with open(os.path.join(here, log + ".log"), "w", encoding="utf-8") as f:
    f.write(p.stdout + "\n--- stderr ---\n" + p.stderr + "\nexit code %d\n" % p.returncode)
print(p.stdout[-6000:])
print(p.stderr[-1500:])
print("exit code", p.returncode)
