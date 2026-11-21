"""Prints a log of out/r27/checkb/logs/ compactly: one line per result, long lists folded, repeated state left out.

  python out/r27/checkb/read_log.py NAME-COMBO [from_step] [to_step]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"approach", "learn", "kWarnOld", "kWarnNew"}


def short(v, n=260):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + " ...(%d chars)" % len(s)


def main():
    name = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
    wide = int(sys.argv[4]) if len(sys.argv) > 4 else 260
    for line in open(os.path.join(HERE, "logs", name + ".txt"), encoding="utf-8"):
        m = re.match(r"step (\d+) result: (.*)", line)
        if not m:
            if not re.match(r"step \d+ (wrote|waited)", line) and line.strip():
                print(line.rstrip()[:400])
            continue
        k = int(m.group(1))
        if k < lo or k > hi:
            continue
        d = json.loads(m.group(2))
        if not isinstance(d, dict):
            print("step %d: %s" % (k, short(d, wide))); continue
        print("step %d: %s" % (k, d.get("f", "")))
        for key, v in d.items():
            if key == "f" or key in SKIP:
                continue
            if key in ("kWarnOld", "kWarnNew") and not v:
                continue
            print("      %s = %s" % (key, short(v, wide)))
        for w in ("kWarnOld", "kWarnNew"):
            if d.get(w):
                print("      !! %s = %s" % (w, d[w]))


if __name__ == "__main__":
    main()
