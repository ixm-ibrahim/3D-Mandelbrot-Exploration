"""Compare sets of pictures pixel for pixel.
  python out/r26/core/compare.py point-base point-core [point-core-back ...]
For every picture out/r26/core/<first>-*.png the same name under each other prefix is compared with it.
"""
import glob, os, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ref, others = sys.argv[1], sys.argv[2:]
    bad = 0
    for path in sorted(glob.glob(os.path.join(HERE, ref + "-*.png"))):
        tail = os.path.basename(path)[len(ref):]
        a = Image.open(path).convert("RGB")
        row = [tail.lstrip("-")]
        for o in others:
            p2 = os.path.join(HERE, o + tail)
            if not os.path.exists(p2):
                row.append("%s: MISSING" % o); bad += 1; continue
            b = Image.open(p2).convert("RGB")
            if a.size != b.size:
                row.append("%s: SIZE %s against %s" % (o, b.size, a.size)); bad += 1; continue
            diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v else 0)
            n = sum(1 for v in diff.getdata() if v)
            row.append("%s: %d of %d pixels differ" % (o, n, a.width * a.height))
            bad += 1 if n else 0
        print("  ".join(row))
    print("ALL THE SAME" if not bad else "%d comparisons differ" % bad)


if __name__ == "__main__":
    main()
