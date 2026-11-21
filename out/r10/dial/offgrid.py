"""Which typed limits lie off the step grid of their dial, and which values did the arrows give that are neither on
the grid nor a limit? The grid is the one the kit uses: the usual slider's lowest value plus whole steps (also while
extreme ranges are on). Reads ends-<tag>.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, "ends-%s.json" % sys.argv[1]), encoding="utf-8"))
def on(v, base, f):
    k = (v - base) / f
    return abs(k - round(k)) < 1e-6
usual = {r["id"]: (r["slider"][0] if r["slider"] else r["lo"]) for r in res["usual"]}
for mode, rows in res.items():
    n = 0
    for r in rows:
        base = usual[r["id"]]
        offs = [name for name, v in (("low", r["lo"]), ("high", r["hi"])) if not on(v, base, r["step"])]
        walked = [v for k in ("low", "high", "low10", "high10", "fromLo", "fromHi") for v in r[k]]
        stray = sorted({v for v in walked if not on(float(v), base, r["step"]) and float(v) not in (r["lo"], r["hi"])}, key=float)
        if offs or stray:
            n += 1
            print("%s %s '%s' step %s, typed %s..%s: limit off the grid: %s; values the arrows gave that are neither on the grid nor a limit: %s" % (
                mode, r["id"], r["label"], r["step"], r["lo"], r["hi"], offs or "none", stray or "none"))
    print("%s: %d of %d boxes have a typed limit off their step grid or gave such values" % (mode, n, len(rows)))
