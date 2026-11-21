"""Print the result of a camera test run (the log tools/shot.py wrote): one line per step, plus every failure.

  python notes/camera_report.py out/camera/tests.log [--all]
"""
import json, re, sys

show_all = "--all" in sys.argv
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    m = re.match(r"step (\d+) result: (.*)", line)
    if not m:
        print(line.rstrip())
        continue
    try:
        arr = json.loads(m.group(2))
    except ValueError:
        print(line.rstrip())
        continue
    if not isinstance(arr, list):
        print(line.rstrip())
        continue
    print("--- step %s: %s" % (m.group(1), arr[0]))
    for s in arr[1:]:
        if show_all or not s.startswith("PASS"):
            print("    " + s)
