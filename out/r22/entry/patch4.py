"""Round 22, entry: the 'keeps shapes' line of Along once in its own words. Run once."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(P, encoding='utf-8').read()
old = "    roundNote: () => AO_CARD + TP_ROUND + AO_LATER + ', which keeps circles on the sphere as circles.',\n"
new = "    roundNote: (p, n = S.n) => AO_CARD + `It keeps shapes inside the ${tpCount(n, true)} planes through the x-axis in which Turning plane, along is the complex power, and squashes them between those planes and across them.` + AO_LATER + ', which keeps circles on the sphere as circles.',\n"
assert s.count(old) == 1
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s); print('ok')
