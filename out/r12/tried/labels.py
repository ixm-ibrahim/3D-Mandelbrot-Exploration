"""One-off: shorter words in the two lists of choices, so they fit the list's width."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
pairs = [
    ("options: [[0, 'Blend along the great circle between the two answers'], [1, 'Blend along the straight line between them'], [2, 'No blend: pinch each seam onto the x-axis']] },",
     "options: [[0, 'Blend along a great circle'], [1, 'Blend along a straight line'], [2, 'No blend: pinch the seams']], help: 'How the two plane answers are joined. A great circle is the shortest way round the sphere of directions from one answer to the other. The pinch does not blend: the nearer plane answers alone, and each seam half way between two planes is pulled onto the x-axis.' },"),
    ("options: [[0, 'Creased: the planes z = 0 and y = 0 exact'], [1, 'Smooth: every angle kept, the slice not exact']],",
     "options: [[0, 'Creased, both planes exact'], [1, 'Smooth, slice not exact']],"),
]
for a, b in pairs:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('labels shortened')
