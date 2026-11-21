"""Compare the result lines of the first check's driver on two pages, character for character.
Lines that carry times or sizes that differ from run to run are listed apart."""
import re, sys
def lines(p):
    return [l.rstrip("\n") for l in open(p, encoding="utf-8") if l.startswith(("pass", "FAIL"))]
a, b = lines(sys.argv[1]), lines(sys.argv[2])
print("%s: %d result lines (%d pass, %d FAIL)" % (sys.argv[1], len(a), sum(l.startswith("pass") for l in a), sum(l.startswith("FAIL") for l in a)))
print("%s: %d result lines (%d pass, %d FAIL)" % (sys.argv[2], len(b), sum(l.startswith("pass") for l in b), sum(l.startswith("FAIL") for l in b)))
same = sum(x == y for x, y in zip(a, b))
print("identical, character for character: %d of %d" % (same, max(len(a), len(b))))
for x, y in zip(a, b):
    if x != y:
        print("differs:\n   A %s\n   B %s" % (x[:700], y[:700]))
