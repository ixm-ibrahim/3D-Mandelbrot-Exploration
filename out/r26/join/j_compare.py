"""Compare two sets of pictures in out/r26/join/ pixel for pixel.
  python out/r26/join/j_compare.py PREFIX_A PREFIX_B
For every picture out/r26/join/<PREFIX_A>-*.png the picture of the same name under PREFIX_B is compared with it.
(Used for "Follow = One point is what it was": the same list of actions on the frozen page and on the joined page.)
"""
import glob, os, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    a, b = sys.argv[1], sys.argv[2]
    bad = n = 0
    for path in sorted(glob.glob(os.path.join(HERE, a + "-*.png"))):
        tail = os.path.basename(path)[len(a):]
        other = os.path.join(HERE, b + tail)
        n += 1
        if not os.path.exists(other):
            print("%s: MISSING under %s" % (tail.lstrip("-"), b)); bad += 1; continue
        x, y = Image.open(path).convert("RGB"), Image.open(other).convert("RGB")
        if x.size != y.size:
            print("%s: SIZE %s against %s" % (tail.lstrip("-"), x.size, y.size)); bad += 1; continue
        d = sum(1 for v in ImageChops.difference(x, y).convert("L").getdata() if v)
        print("%s: %d of %d pixels differ" % (tail.lstrip("-"), d, x.width * x.height))
        bad += 1 if d else 0
    print("%d pictures compared: %s" % (n, "ALL THE SAME" if not bad and n else "%d differ" % bad))
    sys.exit(1 if bad or not n else 0)


if __name__ == "__main__":
    main()
