"""One-off: say in the slice texts what out/r12/tried/slice.txt measured: the 2D view draws a fringe around two exact slices."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
pairs = [
    ("+ (Math.abs(p.k) > 1 ? ' But a point just off the plane is pushed away from it at every step, so the exact slice is a sheet with no thickness.' : '');",
     "+ (Math.abs(p.k) > 1 ? ' But a point just off the plane is pushed away from it at every step, so the exact slice is a sheet with no thickness. The 2D view of this page draws it with a hairy fringe: measured at a multiplier of 5, 28% more solid than the flat Mandelbrot set.' : '');"),
    (": ok ? 'The planes z = 0 and y = 0 both follow complex arithmetic exactly.' : 'The plane z = 0 does not follow complex arithmetic.'),",
     ": ok ? 'The planes z = 0 and y = 0 both follow complex arithmetic exactly. The 2D view of this page still draws the slice with a fringe: measured at n = 2, about 5 to 7% more solid than the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),"),
]
for a, b in pairs:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('slice texts updated')
