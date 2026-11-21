"""Compare the pictures of two runs: python cmp.py dirA dirB  -> how many pictures differ, and by how many pixels."""
import os, sys
from PIL import Image, ImageChops
a, b = sys.argv[1], sys.argv[2]
same = diff = 0; worst = []
for n in sorted(os.listdir(a)):
    pa, pb = os.path.join(a, n), os.path.join(b, n)
    if not n.endswith(".png") or not os.path.exists(pb): continue
    ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
    if ia.size != ib.size: diff += 1; worst.append((n, "size %s vs %s" % (ia.size, ib.size))); continue
    bbox = ImageChops.difference(ia, ib).getbbox()
    if bbox is None: same += 1
    else:
        d = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 8 else 0)
        cnt = sum(1 for v in d.getdata() if v)
        diff += 1; worst.append((n, "%d px differ, box %s" % (cnt, bbox)))
print("identical:", same, "different:", diff)
for w in worst[:40]: print(" ", w[0], w[1])
