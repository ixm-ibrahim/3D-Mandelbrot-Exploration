"""Turn the 'step N result: "<one long JSON string>"' lines that tools/shot.py prints into readable text.
  python notes/measure_steps.py ... > raw.txt ; python notes/measure_unpack.py raw.txt out.txt"""
import json, re, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
def unpack(m):
    val = json.loads(m.group(2))
    return "step %s result:\n%s\n" % (m.group(1), val if isinstance(val, str) else json.dumps(val, ensure_ascii=False, indent=1))
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(re.sub(r"step (\d+) result: (.*)\n", unpack, raw))
