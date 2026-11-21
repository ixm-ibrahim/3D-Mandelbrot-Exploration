"""Pretty-print the JSON text a run.py log holds.  python out/r12/check-maths/show.py <log name> [top-level key ...]"""
import json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(here, sys.argv[1] + ".log"), encoding="utf-8").read()
best = None
for line in txt.splitlines():
    i = line.find('"{')
    if i < 0:
        continue
    try:
        best = json.loads(json.loads(line[i:]))
    except Exception as e:
        pass
if best is None:
    print("no JSON found"); sys.exit(1)
keys = sys.argv[2:] or list(best)
def show(v, ind=0):
    pad = "  " * ind
    if isinstance(v, dict):
        flat = all(not isinstance(x, (dict, list)) for x in v.values())
        if flat and len(json.dumps(v, ensure_ascii=False)) < 230:
            print(pad + json.dumps(v, ensure_ascii=False)); return
        for k, x in v.items():
            if isinstance(x, (dict, list)) and len(json.dumps(x, ensure_ascii=False)) > 150:
                print(pad + str(k) + ":"); show(x, ind + 1)
            else:
                print(pad + str(k) + ": " + json.dumps(x, ensure_ascii=False))
    elif isinstance(v, list):
        for x in v:
            show(x, ind) if isinstance(x, (dict, list)) else print(pad + str(x))
    else:
        print(pad + str(v))
for k in keys:
    print("== " + k); show(best[k], 1)
with open(os.path.join(here, sys.argv[1] + ".json"), "w", encoding="utf-8") as f:
    json.dump(best, f, indent=1, ensure_ascii=False)
