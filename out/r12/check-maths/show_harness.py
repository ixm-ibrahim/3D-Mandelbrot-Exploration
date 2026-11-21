import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
for line in open(os.path.join(here, "gpu-new.log"), encoding="utf-8"):
    i = line.find('"{\\"mercator')
    if i < 0: continue
    d = json.loads(json.loads(line[i:]))
    json.dump(d, open(os.path.join(here, "harness.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for k, rows in d.items():
        print("==", k)
        if isinstance(rows, str): print("  ", rows); continue
        for t, r in rows.items():
            flag = "" if ("(0 of" in r and "(0 over)" in r and "(0 of 256 over)" in r and "NOT FINITE" not in r) else "   <<<"
            print("  %-78s %s%s" % (t[:78], r[:300], flag))
