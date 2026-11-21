"""Print the pin check logs in short: python out/r13/pin/brief.py out/r13/pin/log-*.txt"""
import glob, json, re, sys

for pat in sys.argv[1:]:
    for path in sorted(glob.glob(pat)):
        print("==", path)
        for line in open(path, encoding="utf-8", errors="replace"):
            m = re.match(r"step (\d+) result: (.*)", line)
            if not m:
                if "TIMED OUT" in line or "PROBLEM" in line or "console" in line or line.startswith("  "):
                    print("  ", line.strip()[:300])
                continue
            d = json.loads(m.group(2))
            at = d.get("at")
            if at in ("top", "approach", "end of controls", "dial moved", "pinned again"):
                p = d["pin"]
                print("  %-16s on=%s stuck=%s pos=%s main=%s..%s stage=%s..%s (h %s) share=%s pinH=%s toprow=%s same=%s changed=%s hint=%s ovX=%s | %s | %s" % (
                    at, p["on"], p["stuck"], d["pos"], d["main"]["top"], d["main"]["bottom"], d["stage"]["top"], d["stage"]["bottom"], d["stage"]["h"],
                    d["share"], d["pinH"].strip(), d["toprow"], d.get("same"), d.get("pictureChanged"), d["hint"], d["overflowX"], d["status"], d["btn"]))
            elif at == "unpinned":
                a = d["atTop"]
                print("  unpinned         stored=%s atTop: pos=%s stage h %s toprow=%s btn=%s ; scrolled: stage=%s..%s" % (
                    d["stored"], a["pos"], a["stage"]["h"], a["toprow"], a["btn"], d["stage"]["top"], d["stage"]["bottom"]))
            else:
                print("  ", json.dumps(d, ensure_ascii=False)[:900])
