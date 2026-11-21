"""The final look: Follow = One point on the frozen page against the final page.

  python out/r26/final/compare_point.py [base-log] [final-log]      default: point-base point-final

Compares out/r26/final/<base>-N-stage.png and -N-bar.png with <final>-..., pixel for pixel, and the result lines of
the two logs word for word. Writes out/r26/final/point-compare.txt.
"""
import os, re, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))


def results(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"step (\d+) result: (.*)$", line.rstrip("\n"))
            if m:
                out[int(m.group(1))] = m.group(2)
    return out


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else "point-base"
    b = sys.argv[2] if len(sys.argv) > 2 else "point-final"
    lines, bad = [], 0
    for n in (1, 2, 3):
        for part in ("stage", "bar"):
            pa, pb = (os.path.join(HERE, "%s-%d-%s.png" % (x, n, part)) for x in (a, b))
            ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
            if ia.size != ib.size:
                lines.append("state %d %s: SIZES DIFFER %s against %s" % (n, part, ia.size, ib.size)); bad += 1
                continue
            diff = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v else 0)
            cnt = sum(1 for v in diff.getdata() if v)
            lines.append("state %d %s: %d x %d pixels, %d differ%s" % (n, part, ia.size[0], ia.size[1], cnt, "" if not cnt else "  bbox %s" % (diff.getbbox(),)))
            bad += 1 if cnt else 0
    ra, rb = results(os.path.join(HERE, a + ".log")), results(os.path.join(HERE, b + ".log"))
    for k in sorted(set(ra) | set(rb)):
        if k == max(set(ra) | set(rb)):
            lines.append("step %d (what stands first in the panel): base %s | final %s" % (k, ra.get(k), rb.get(k)))
            continue
        same = ra.get(k) == rb.get(k)
        lines.append("step %d state as the handle gives it: %s (%d letters)" % (k, "word for word the same" if same else "DIFFERS", len(ra.get(k) or "")))
        if not same:
            bad += 1
            lines.append("  base:  %s" % (ra.get(k) or "")[:900]); lines.append("  final: %s" % (rb.get(k) or "")[:900])
    lines.append("TOTAL: %d things differ" % bad)
    text = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "point-compare.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(text)


if __name__ == "__main__":
    main()
