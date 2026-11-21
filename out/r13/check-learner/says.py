"""Print the sentence of every moment from a walk log: python says.py walk-desktop.log"""
import sys, re, json
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    m = re.match(r'step (\d+) result: "(.*)"\s*$', line)
    if not m: continue
    s = m.group(2).encode("utf-8").decode("unicode_escape").encode("latin-1", "replace").decode("utf-8", "replace") if False else json.loads('"' + m.group(2) + '"')
    k = s.find("{")
    name, d = s[:k].strip(), json.loads(s[k:])
    print("%-28s %-8s t=%-4s pt=%s | %s%s" % (name, d["mv"], d["t"], d["pt"], d["say"], "" if d["say"] == d["shown"] else "  [SHOWN DIFFERS: " + d["shown"] + "]"))
