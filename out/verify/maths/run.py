"""Run one or more page-JavaScript files on dist/preview.html through tools/shot.py.
usage: python out/verify/maths/run.py name [name2 ...]   (runs common.js + name.js as one step each)
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
common = open(os.path.join(HERE, "common.js"), encoding="utf-8").read()
acts = []
for name in sys.argv[1:]:
    acts.append({"js": common + "\n" + open(os.path.join(HERE, name + ".js"), encoding="utf-8").read()})
path = os.path.join(HERE, "_" + "_".join(sys.argv[1:]) + ".json")
json.dump(acts, open(path, "w", encoding="utf-8"))
env = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--actions", path], env=env))
