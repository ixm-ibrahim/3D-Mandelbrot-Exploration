"""Debug copy: the 2D view shows the distance estimate itself as contour bands (one band per factor of sqrt 2).
usage: python out/fix/shaders/dbgflat.py <in.js> <out.js> [nt]"""
import sys
s = open(sys.argv[1], encoding='utf-8').read()
nt = sys.argv[3] if len(sys.argv) > 3 else '3'
a = "    col = flatColour(slicePoint, d, uFlatH / uRes.y);"
assert s.count(a) == 1
s = s.replace(a, a + "\n    if (gEsc > 0.5) col = 0.5 + 0.5 * cos(6.2832 * (log2(max(d, 1e-12)) * 2.0 + vec3(0.0, 0.33, 0.67))); else col = vec3(0.0);")
a = "    else if (flat2) qn = 3;"
assert s.count(a) == 1
s = s.replace(a, "    else if (flat2) qn = %s;" % nt)
open(sys.argv[2], 'w', encoding='utf-8').write(s)
