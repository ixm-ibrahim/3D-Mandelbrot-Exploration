"""Compare the walks of ends.py before and after: which boxes changed, and how."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "ends-before.json"), encoding="utf-8"))
B = json.load(open(os.path.join(HERE, "ends-after.json"), encoding="utf-8"))
NAMES = {"low": "down x6 then up x6 from three steps above the low limit", "high": "up x6 then down x6 from three steps below the high limit",
         "low10": "ten down, one down, ten up, one up", "high10": "ten up, one up, ten down, one down",
         "fromLo": "typed the low limit, then up, up, down, down, down", "fromHi": "typed the high limit, then down, down, up, up, up"}
for mode in A:
    same = changed = 0
    for a, b in zip(A[mode], B[mode]):
        assert a["id"] == b["id"]
        keys = [k for k in a if a[k] != b[k]]
        if not keys:
            same += 1; continue
        changed += 1
        print("%s %s '%s' step %s, typed %s..%s" % (mode, a["id"], a["label"], a["step"], a["lo"], a["hi"]))
        for k in keys:
            print("    %s\n        before %s\n        after  %s" % (NAMES.get(k, k), a[k], b[k]))
    print("%s ranges: %d boxes walked, %d the same before and after, %d changed" % (mode, len(A[mode]), same, changed))
