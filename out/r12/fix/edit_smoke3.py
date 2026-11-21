"""Fixer of round 12, third edit of out/r4/page/make_smoke.py: my own new check asked for 20 of 660 probes on the
one-plane picture after Back to one plane. In the test's state (Turn of the one-plane entry at 30) that picture has
16 of 660, and it is a real picture. The check now asks what the test asks of the Figure 4 picture: not empty."""
import io, os
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
p = os.path.join(root, "out", "r4", "page", "make_smoke.py")
s = io.open(p, encoding="utf-8").read()
a = "if (hits(one) < 20) fail('the one-plane picture after Back to one plane is (nearly) empty: '"
assert s.count(a) == 1
s = s.replace(a, "if (hits(one) < 5) fail('the one-plane picture after Back to one plane is empty: '")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("edited")
