"""Compares the going-back run on the new page with the frozen page: state by state, and the pictures pixel by pixel."""
import json, os, re, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ["mode", "flat", "approach", "apName", "modeChecked", "cam", "view", "v2", "colour", "q", "status", "secs", "kleinNote", "kleinWarn", "preset",
        "bodyLearn", "apShown", "kleinShown", "eqShown", "first", "pop", "list", "rowsWhollyVisible", "panelWords"]


def load(name):
    out = {}
    tail = []
    for line in open(os.path.join(HERE, "logs", name + ".txt"), encoding="utf-8"):
        m = re.match(r"step (\d+) result: (.*)", line)
        if m:
            d = json.loads(m.group(2))
            if isinstance(d, dict) and "at" in d:
                out[d["at"].split(" ")[0]] = d
        elif not re.match(r"step \d+ (wrote|waited)", line) and line.strip():
            tail.append(line.strip()[:200])
    return out, tail


def kdrop(s):
    """S.k without the four numbers of the new group."""
    d = json.loads(s)
    for key in ("group", "bt", "bgrid", "bit"):
        d.pop(key, None)
    return d


def main():
    for c in ("wd", "pl"):
        new, t1 = load("s7-back-" + c)
        base, t2 = load("s7-base-" + c)
        print("=====", c, "| new:", t1[-2:], "| base:", t2[-2:])
        for at in sorted(base):
            b, n = base[at], new.get(at)
            if n is None:
                print("  state", at, "missing on the new page"); continue
            diffs = [k for k in KEYS if k in b and b.get(k) != n.get(k)]
            if "k" in b and kdrop(b["k"]) != kdrop(n["k"]):
                diffs.append("k")
            print("  state %s (%s): %s" % (at, b["at"], "same state" if not diffs else "DIFFERENT: " + ", ".join(diffs)))
            for k in diffs:
                print("      %s  base: %s" % (k, json.dumps(b.get(k), ensure_ascii=False)[:300]))
                print("      %s  new : %s" % (k, json.dumps(n.get(k), ensure_ascii=False)[:300]))
            if "ms" in b:
                print("      ms  base %s, new %s" % (b["ms"], n.get("ms")))
        if "3" in new:
            n = new["3"]
            print("  new page, Kleinian button after an approach and Julia: group", n["group"], "| k", n["k"], "| cam", n["cam"])
        for name in ("0-open", "1-approach7", "2-julia", "4-kleinian-old", "5-kleinian-old-flat", "6-kleinian-old-laststep", "8-mandelbrot-again"):
            for part in ("stage", "window"):
                pa = os.path.join(HERE, "shots", "s7-%s-new-%s-%s.png" % (c, name, part))
                pb = os.path.join(HERE, "shots", "s7-%s-base-%s-%s.png" % (c, name, part))
                if not (os.path.exists(pa) and os.path.exists(pb)):
                    print("  picture", name, part, "missing"); continue
                A, B = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
                if A.size != B.size:
                    print("  picture %s %s: sizes differ %s %s" % (name, part, A.size, B.size)); continue
                d = ImageChops.difference(A, B).convert("L").point(lambda v: 255 if v else 0)
                n = sum(1 for v in d.getdata() if v)
                box = d.getbbox()
                print("  picture %-26s %-6s: %d of %d pixels differ%s" % (name, part, n, A.size[0] * A.size[1], "" if not n else "  box " + str(box)))
                if n and part == "window":
                    d.save(os.path.join(HERE, "shots", "s7-%s-diff-%s.png" % (c, name)))


if __name__ == "__main__":
    main()
