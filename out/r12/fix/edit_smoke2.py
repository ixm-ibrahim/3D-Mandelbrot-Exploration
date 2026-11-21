"""Fixer of round 12, second edit of out/r4/page/make_smoke.py: the 165 probes are too coarse to tell two entries
apart (the Julia sets for c = -1 of Sphere inversions, one plane and of the twisted square hit the same 165 in the
test's camera, while 54 of 1320 probes differ: out/r12/fix/pair.log), so the comparison reads 408 probes. A probe
costs about 20 ms, so the Figure 4 comparison reads 660, not 1320."""
import io, os
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
p = os.path.join(root, "out", "r4", "page", "make_smoke.py")
s = io.open(p, encoding="utf-8").read()
def sw(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)
sw("// which of the 15 x 11 probes hit, as a string of 165 marks\nconst gridS = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) s += L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11) ? '1' : '0'; return s; };",
   "// which of 24 x 17 probes hit, as a string of 408 marks (the 165 of grid() are too coarse to tell two entries apart)\nconst gridS = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = ''; for (let i = 0; i < 24; i++) for (let j = 0; j < 17; j++) s += L.pick(w * (i + 0.5) / 24, h * (j + 0.5) / 17) ? '1' : '0'; return s; };")
sw("let least = 165;", "let least = 408;")
sw("(the two closest differ in ' + least + ' of 165 probes)';", "(the two closest differ in ' + least + ' of 408 probes)';")
sw("for (let i = 0; i < 44; i++) for (let j = 0; j < 30; j++) s += L.pick(w * (i + 0.5) / 44, h * (j + 0.5) / 30) ? '1' : '0'; return s; };",
   "for (let i = 0; i < 30; i++) for (let j = 0; j < 22; j++) s += L.pick(w * (i + 0.5) / 30, h * (j + 0.5) / 22) ? '1' : '0'; return s; };")
sw("if (hits(one) < 40) fail('the one-plane picture after Back to one plane is (nearly) empty: ' + hits(one) + ' of 1320 probes hit');",
   "if (hits(one) < 20) fail('the one-plane picture after Back to one plane is (nearly) empty: ' + hits(one) + ' of 660 probes hit');")
sw("if (differ < 8) fail('the picture did not change with Back to one plane: ' + differ + ' of 1320 probes differ from the Figure 4 picture');",
   "if (differ < 4) fail('the picture did not change with Back to one plane: ' + differ + ' of 660 probes differ from the Figure 4 picture');")
sw("the picture changed (' + differ + ' of 1320 probes differ,", "the picture changed (' + differ + ' of 660 probes differ,")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("edited")
