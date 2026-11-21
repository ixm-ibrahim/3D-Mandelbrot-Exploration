p = 'src/js/65-learn-steps.js'
s = open(p, encoding='utf-8').read()
a = "// file is repeated here (the Mercator clamps, the fallback side of a point on an axis, the length cap aprPow).\n"
assert s.count(a) == 1
b = a + """// Where a move is not smooth (measured, out/r13/steps/): a Stretch is even on a log scale, so when a length changes
// by more than about e^20 in one move (the origin under a negative power, a tiny point under a high power) most of
// the distance is covered in the last few hundredths of the move. Two points exactly opposite on the sphere have no
// short way between them, and one way is picked (the "own" move of the Tried entries).
"""
s = s.replace(a, b).replace("    power = F;\n    const zero = F;\n", "    power = F;\n    const zero = F;                    // asked only for a point at the origin: where the rule itself sends it\n")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
