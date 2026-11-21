# Round 23, outside2: three constructions from the literature that the project has not tried

Checked against the bench list (`out/r16/bench/rules.py`), the lab's entries and `notes/_state.md`: none of the three is
there. K1 is built and tested. K2 and K3 are written out and NOT built (time); every statement about them is reasoned.

## K1. The "balanced view" square (Douady-Earle extension of z^2; Petersen 2011). BUILT: `de.py`

Idea: a point p above the flat plane sees the flat plane as a sphere of view. Push that view through z -> z^2. The
answer is the one point from which the pushed view is balanced. No choice is made anywhere; it commutes with every
sphere-inversion map of the plane, so "square, then add c" holds with a fixed square.

Formula. For v with |v| = r, latitude L >= 0, longitude lon:
    E(v) = r^2 ( R(L) cos 2lon, R(L) sin 2lon, T(L) ),      mirrored for z < 0,
where (R, T) solves, for p = (cos L, 0, sin L):
    mean over directions xi uniform on the unit sphere of  U( ((cos L + sin L * s(xi))^2 - R) / T )  =  0,
    s(xi) = (xi1 + i xi2) / (1 - xi3),     U(eta) = (2 Re eta, 2 Im eta, |eta|^2 - 1) / (|eta|^2 + 1).
Solve by repeating  R += 1.5 T m1,  T *= exp(1.5 m3)  (m = the mean) from the one-plane value. Table of 181 latitudes
in `de_table.npz` (200,000 directions, residual under 1e-13). Load: `sys.path.insert(0, 'out/r23/outside2'); import de; r = de.rule()`.

Result (measured): length exactly |v|^2 (to 5 decimals); direction within 1.21 degrees of the one-plane rule; latitude
rises all the way (no fold, no crushed cone); hinge-free (turn test 7e-15); flat check 0 of 20,000; lift test passes
(3441 of 3443 basilica, 3195 of 3195 rabbit, same as one plane). Bodies: verdicts differ from one plane on 0.07 %
(basilica), 0.08 % (rabbit), 0.5 % (c = -0.75) of the test box. Seen (`de-cuts.png`, `de-solids-a.png`,
`de-solids-top.png`): the same clean separate blown-up bodies as one plane for c = -1 and the rabbit, buds round the
flat picture only, nothing off it; at c = -0.75 the waists between bodies are a little deeper.
Verdict: the canonical extension IS the one-plane look. It confirms the theorem (two coverings, no fold: nothing off
the flat picture) and it shows the lab's one-plane rule is not an accident of a formula. Not a new look.

## K2. One plane with an arc blown up (Pilgrim and Tan Lei's surgery). NOT BUILT

Idea: leave the one-plane rule untouched everywhere except inside one thin lens of directions on each side of the flat
plane. Inside the lens, a small disc of directions is opened up and laid once over ALL directions. That adds one covering
per side (4 in all) with no fold, no blend near the flat plane, and exactly two new branch directions per side, whose
images are the two ends of the arc, which we choose.

Formula. Choose the arc's middle m = (cos b, 0, sin b) (latitude b above +x: the arc must lie above +x for the rule to
stay mirror-symmetric in y, because directions above +x are the squares of directions above +x and above -x), its
half-length lam, and an ellipse size rho > 1. Let e1 = (-sin b, 0, cos b), e2 = (0, 1, 0), eps = tan(lam / 2),
a = (rho + 1/rho)/2, b' = (rho - 1/rho)/2. One more choice: the side sx = +1 or -1 (which of the two roots gets the disc).
    1. d = one-plane direction of v (unit).
    2. If z of v > 0 and x of v has the sign sx:
         p = ((d.e1) + i (d.e2)) / (1 + d.m) / eps
         if (Re p / a)^2 + (Im p / b')^2 < 1:   zeta = rho (Re p / a + i Im p / b');   p = (zeta + 1/zeta) / 2
         p = eps p;   d = ( m (1 - |p|^2) + 2 Re p e1 + 2 Im p e2 ) / (1 + |p|^2)
    3. F(v) = |v|^2 d.    The lower side is the mirror image (z -> -z).
(zeta = 0 gives the direction -m. Outside the ellipse nothing changes; on the ellipse the two formulas agree, so there is
no tear. The opened disc is |zeta| < 1. Squeeze inside the ellipse: a / b' = (rho^2 + 1)/(rho^2 - 1), 1.25 at rho = 3.)
What to expect (reasoned): each lens holds one rolled-up copy of the flat picture (once round, so it can be made
shape-keeping where the copy's circle has half the equator's length, i.e. a disc about 30 degrees in radius: a wide arc).
The rule has one special upright half-plane (the arc's), not three. For c = -1 the middle body gets two more big
neighbours, at the directions sent to +x. Risk: the same as the cone rule's, where the two new branch directions go.
Why it is worth a try: it is the only fold-free way I found in the literature to add coverings while the rule stays
exactly one plane elsewhere, so the flat check and the lift test are free and the fault, if any, is local.

## K3. Doubling on a doughnut (both turning angles of the 3-sphere doubled, seen in space). NOT BUILT

Idea: the user's sentence "the 2D spacing being done in 3D, not stretched" is literally possible only on a doughnut
(verdicts.md (e)). The cleanest such map doubles both turning angles of a 4D rotation and is seen in 3D through the
angle-true projection of the 3-sphere.

Formula. For v = (x, y, z), s = |v|^2:
    z1 = (2x + 2iy) / (s + 1),   z2 = (2z + i(s - 1)) / (s + 1)          (|z1|^2 + |z2|^2 = 1)
    Z1 = z1^2,  Z2 = z2^2,  N = sqrt(|Z1|^2 + |Z2|^2),  Z1 /= N,  Z2 /= N
    F(v) = ( Re Z1, Im Z1, Re Z2 ) / (1 - Im Z2);    orbit v -> F(v) + c.
Known without building (reasoned): without c the set is a round doughnut (radii sqrt 2 and 1) on which the map doubles
both angles and keeps shapes exactly, stretch 2 in all three directions; the unit circle of the flat plane and the
upright axis are both pulled in. It FAILS the user's test 1 by construction: the flat plane is sent to a dome, not to
itself, so the cut z = 0 is not the flat picture. Worth building only as a picture of what "the same spacing everywhere"
looks like when taken literally, not as a candidate.

## Considered and dropped

- The square by the best-fitting sphere-inversion map at the foot point (osculating Möbius map):
  F = ( (x^2 - y^2) q, 2xy q, 8 rho^3 z / (4 rho^2 + z^2) ), q = (4 rho^2 - 3 z^2)/(4 rho^2 + z^2), rho^2 = x^2 + y^2.
  Agrees with one plane to second order in the height, but sends the whole upright axis to 0, so the set would be an
  endless column (reasoned). Not length-squared.
- Other evenly spaced direction maps (the triangle pillows; square or hexagonal lattices with a turning multiplier of
  size 2): no closed belt that avoids the corners is kept by them (reasoned), so no flat plane.
