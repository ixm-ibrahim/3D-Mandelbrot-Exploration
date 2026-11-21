"""Reads logs/s4-words-*.txt: prints the texts once and, for each window, what the measured boxes say."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORBIDDEN = ["page", "sheet", "hinge", "door", "cone copy", "critical", "covers", "winding", "jacobian", "stretch ratio", "latitude", "cusp",
             "parabolic", "loxodromic", "moebius", "möbius", "mobius", "lattice", "discrete", "limit set", "pearl tree", "skew pillow", "twin_tri",
             "kfix", "maskit", "picard", "gaussian", "eisenstein", "isometr", "subgroup", "generator", "conjugat", "orbifold", "fuchsian",
             "basilica", "c = -1", "c = −1", "rabbit", "modular", "fundamental domain", "coset", "quotient"]


def walk(o, f):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f)
    elif isinstance(o, list):
        for v in o:
            walk(v, f)
    elif isinstance(o, str):
        f(o)


def main():
    first = True
    for c in ("wd", "wl", "pd", "pl"):
        p = os.path.join(HERE, "logs", "s4-words-%s.txt" % c)
        if not os.path.exists(p):
            continue
        print("=====", c)
        for line in open(p, encoding="utf-8"):
            m = re.match(r"step (\d+) result: (.*)", line)
            if not m:
                if "PROBLEM" in line or "TIMED" in line or "exit" in line or "console" in line:
                    print("  ", line.strip()[:300])
                continue
            d = json.loads(m.group(2))
            if first:
                for k, v in d.items():
                    if k.lower().endswith(("texts", "titles")) or k in ("warn", "flatLabel", "stageHint", "status", "canvasLabel"):
                        print("  [%s]" % k)
                        for t in (v if isinstance(v, list) else [v]):
                            print("     ", t)
                hits = []
                walk(d, lambda s: [hits.append((w, s)) for w in FORBIDDEN if w in s.lower()])
                for w, s in hits:
                    print("  !! word '%s' in: %s" % (w, s[:200]))
            for key in ("menuBoxes", "boxes"):
                for name, b in (d.get(key) or {}).items():
                    if b == "MISSING":
                        print("  step %s box %s MISSING" % (m.group(1), name)); continue
                    flags = [f for f in ("outRight", "outLeft", "clipX", "clipY") if b.get(f)]
                    if flags or not b.get("shown"):
                        print("  step %s box %s: %s shown=%s x %d..%d w %d h %d" % (m.group(1), name, flags, b.get("shown"), b["x0"], b["x1"], b["w"], b["h"]))
            if "overlaps" in d:
                print("  step %s overlaps: %s" % (m.group(1), d["overlaps"]))
            if "pageWider" in d:
                print("  step %s page wider than window by %s px" % (m.group(1), d["pageWider"]))
            for k in ("popHidden", "ticked", "rowOn", "mode", "group", "win"):
                if k in d:
                    print("  step %s %s = %s" % (m.group(1), k, d[k]))
        first = False


if __name__ == "__main__":
    main()
