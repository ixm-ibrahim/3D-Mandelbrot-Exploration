"""Print the results of one of my logs step by step, readably.

  python out/r26/final/readlog.py LOG [FROM [TO]] [--width N]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    width = 6000
    if "--width" in sys.argv:
        width = int(sys.argv[sys.argv.index("--width") + 1])
        args = [a for a in args if a != str(width)]
    log = args[0]
    lo = int(args[1]) if len(args) > 1 else 1
    hi = int(args[2]) if len(args) > 2 else 10 ** 6
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with open(os.path.join(HERE, log if log.endswith(".log") else log + ".log"), encoding="utf-8") as f:
        text = f.read()
    print(text.split("\n", 1)[0])
    for line in text.split("\n"):
        m = re.match(r"step (\d+) (result: |wrote |TIMED OUT)(.*)$", line)
        if not m:
            if line.startswith(("PAGE PROBLEMS", "  EXCEPTION", "  console", "no console errors", "exit code", "RuntimeError", "Traceback")) or "page script failed" in line:
                print(line[:1500])
            continue
        n = int(m.group(1))
        if n < lo or n > hi:
            continue
        if m.group(2).startswith("result"):
            try:
                d = json.loads(m.group(3))
                s = (json.dumps(d, ensure_ascii=False) if "--compact" in sys.argv else json.dumps(d, ensure_ascii=False, indent=1)) if not isinstance(d, str) else d
            except ValueError:
                s = m.group(3)
            print("--- step %d:\n%s" % (n, s[:width]))
        else:
            print("--- step %d %s%s" % (n, m.group(2), m.group(3)))


if __name__ == "__main__":
    main()
