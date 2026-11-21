"""Round 22, entry: the texts after this round's own measurements (detest.txt, wings.txt, jump.txt). Run once."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("const CR_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says: the finer settings have not been tested for it. The pictures described here were made with Iterations at 40.';\n",
    "const crRough = (rough, fine) => `The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. Measured on the Julia sets for c = −1, the rabbit, the Siegel disc and c = −0.75, 1,728 lines of sight each, against the set worked point by point: with “Rough” no ray stopped where the set has no body, and ${rough}. ${fine} The pictures described here were made with Iterations at 40.`;\n"
    "const AO_ROUGH = crRough('of the lines that meet the set at most 4 of 323 were missed', 'With “Exact” up to 44% of the stops were at nothing, and with “One neighbour” up to 8%.');\n"
    "const PP_ROUGH = crRough('of the lines that meet the set at most 1 was missed', 'With “One neighbour” up to 82% of the stops were at nothing, and with “Exact” up to 26%.');\n")
rep("const AO_NOTE = CR_ROUGH + ", "const AO_NOTE = AO_ROUGH + ")
rep("const PP_NOTE = CR_ROUGH + ", "const PP_NOTE = PP_ROUGH + ")
rep("two bodies of the rabbit float free, and the Mandelbrot solid is the one-plane solid.';",
    "two bodies of the rabbit float free, and the Mandelbrot solid is the one-plane solid with thin wings standing off it that have no thickness.';")
rep("The Mandelbrot solid is the solid of Sphere inversions, one plane: of 200,000 points c tested with 80 steps, none got a different answer. And it is not one rule:",
    "The Mandelbrot solid has the body of the solid of Sphere inversions, one plane: of 200,000 points c tested with 80 steps in round 21, none got a different answer. But the picture also shows thin curved wings standing off its left end, where Sphere inversions, one plane has nothing: in one picture 68 of 195 rays stopped on them. The wings are there, but they are films with no thickness. Followed along a line of sight into three of them, the orbit stays longer and longer the nearer the film (21 to 27 steps at the best of 20,000 places along a stretch 0.08 long, 40 to 54 steps when the search is narrowed to a stretch of 0.000000000003), and no stretch was found whose points all stay. And it is not one rule:")
rep("the root of the first dial (read off the rule and measured).'",
    "the root of the first dial (read off the rule; measured with c = −1 at x = −0.8: two points 0.000000002 apart, one on either side of such a line, get answers 0.70 apart, which is as far apart as the answers are long).'")
io.open(P, 'w', encoding='utf-8', newline='\n').write(s); print('ok')
