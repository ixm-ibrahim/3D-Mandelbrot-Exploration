import io
p = 'docs/ROUND12.md'
t = io.open(p, encoding='utf-8').read()
old_a = t[t.index("- Tilt 0 is the Lathe. Tilt 180"):t.index("- A Julia set whose c is in the plane z = 0")]
new_a = ("- Tilt 0 is the Lathe. Tilt 180 is the Lathe with z mirrored (its mirror twin) for EVEN powers (4e-15 at\n"
         "  power 2); for odd powers a tilt of 180 is the plain Lathe. A minus sign gives the mirror image in y.\n"
         "  CORRECTED 2026-11-18 after the maths check of round 12: an earlier line here said that at tilt 90 and −90\n"
         "  the Mandelbrot solid has no end. That was wrong (my slip: the orbit of x starts at c_x, not at 0, so x must\n"
         "  also lie in the filled Julia set of x² + k). The solid ends inside radius 2 at every tilt; at 90 and −90\n"
         "  it is a fat body with spikes, farthest point about 1.8 (`out/r12/check-maths/`, `out/r12/fix/`).\n")
t = t.replace(old_a, new_a)
old_b = "fractal edge is where the solid meets the plane z = 0. Say so; do not oversell it."
new_b = "close-up pictures show smooth sheets and folds (the checker found fine layering at many places away from\n  z = 0, so do not say the plane is the only place with fine structure). Say so; do not oversell it."
assert t.count(old_b) == 1
t = t.replace(old_b, new_b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('corrected', p)
