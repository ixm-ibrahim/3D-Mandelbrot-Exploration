"""Print a shot.py log compactly: one summary line per step, every FAIL line, and anything that is not a result."""
import json, sys

for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
    for ln in f:
        ln = ln.rstrip()
        if "result: " not in ln:
            print(ln)
            continue
        head, js = ln.split("result: ", 1)
        try:
            v = json.loads(js)
        except Exception:
            print(ln)
            continue
        if isinstance(v, list) and v and isinstance(v[0], str):
            print(head + v[0])
            for x in v[1:]:
                if not (isinstance(x, str) and x.startswith("PASS")):
                    print("    " + str(x))
        else:
            print(ln)
