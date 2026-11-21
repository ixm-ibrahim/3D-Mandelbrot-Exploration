# Round 23, outside2: verdicts on docs/ROUND23.md section 2 (a) to (f)

Marks: **theorem** (cited, or a short proof given here), **measured** (number from `check1.py` / `de.py`, logs beside
them), **reasoned** (mine, not checked by a computation), **open**.
Notation: a rule is F(v) = |v|^2 G(direction); L = latitude (0 = flat plane, 90 = upright axis), lon = longitude.

## (a) The hinge: CORRECT, and the core of it is a theorem

- "z^2 has no hinge; one plane obeys turn-by-a -> square-turns-by-2a": **measured** 7e-15 (also for the Douady-Earle
  rule). Lathe, two planes, along fail the test at every angle tried (37, 90, 120, 180 degrees): **measured**.
- The worked cause for the rabbit: **measured**, same numbers. Above the meeting point alpha = -0.2763 + 0.4797i at
  height 0.075 the height is multiplied by 0.997 under along and 1.098 under one plane (two planes: 1.098); at height
  0.15: 0.735 against 1.074. The square lands at y = -0.262, on the other side of the x-axis, as the briefing says.
- Why no hinged rule can be right off the x-axis: **theorem** (round 21's, re-derived). Two planes through 0 that both
  hold the flat picture of the same c must both contain c, so they meet in the line through 0 and c; on that line the
  two squarings agree only if the line is the fixed ray of doubling or its opposite, i.e. c is on the x-axis. So for the
  rabbit there is no second plane holding a true copy, whatever the rule.
- Addition (**reasoned**): the x-axis is not arbitrary. z^2 alone singles out exactly two things: the axis of its turn
  symmetry (the upright axis) and its fixed direction +x with its other root -x. A hinge "taken from the flat rule
  itself, the same for every c" can only be one of these two lines. The upright axis is the one the cone rule uses.

## (b) What a hinge-free rule can do: WRONG as written (one case is missing); the corrected statement is a theorem

- **Theorem** (two lines): if G(R_a u) = R_2a G(u) for every turn R_a about the upright axis and G is continuous, then
  G(L, lon) = (l(L), 2 lon + shift(L)): circles of latitude go to circles of latitude, each wound exactly TWICE, and
  each pole goes to a pole.
- The briefing says the image "must pass over a pole" between two circles laid on the flat plane, so that the only ways
  are a crushed cone or a tear. Missing third way: l(L) can turn back before the pole. That is a FOLD along a circle
  of latitude. **Counterexample, measured** (`check1.py` C, rule "fold30": latitude kept up to 30 degrees, then
  90 - 2L, then one plane): turn test 2e-14 at all four angles; continuous (a direction step of 1e-6 moves the square
  by at most 1.6e-5, 1.6e-7 beside the upright axis); flat check 0 of 20,000; and the 45-degree cone holds the RABBIT's
  flat picture exactly (0 of 40,000 verdicts differ) with real thickness (93 % of its points survive half a degree off
  the cone, 69 % five degrees off). So a hinge-free, tear-free, crush-free rule with copies off the flat plane exists.
- Corrected statement, **theorem**: hinge-free AND no tear AND no fold AND no crushed cone => l(L) rises monotonically
  from 0 to 90 => only the flat plane is sent to the flat plane => nothing touches the flat picture from outside it.
- Two additions.
  (1) **theorem** (counting): ANY fold-free rule that covers directions twice and is exact on the flat plane, hinged or
  not, sends no point off the flat plane into it, because the two flat square roots already use up both preimages. So
  each body has only the blown-up flat bodies as preimages. Buds off the flat plane need more than two coverings or a fold.
  (2) **theorem**: under full hinge-freeness every copy cone is wound twice, so its stretch along the circle is
  2 / cos L > 2 (measured 2.83 at 45 degrees): a hinge-free rule never keeps shapes on a copy cone.
- The two published "canonical" extensions of z^2 are both hinge-free and monotone: the product extension of Cabrera,
  Makienko, Sienra IS the lab's one-plane rule (**measured** 7e-15), and the Douady-Earle extension differs from it by at
  most 1.21 degrees in direction with the same length |v|^2 (**measured**, `de.py table`).

## (c) Shape-keeping needs the right cone: CORRECT (theorem-level bookkeeping), with three sharpenings

- The three stretches of |v|^2 G(u) are 2|v| along the ray and |v| times the two stretches of G: **measured** (ray
  stretch / 2|v| = 1.000000 for one plane and for R_t; one plane's other two fall from 2 at the flat plane to 1.33..1.45
  at 30 degrees, 0.53..0.62 at 60, under 0.09 near the axis). So shapes are kept exactly where G is angle-true with
  stretch 2: **theorem** (linear algebra).
- A circle of latitude laid ONCE round has stretch 1 / cos L: 2 at 60 degrees; power n: cos L = k/n. Correct, and the
  count agrees with the published 3D power maps, which cover n^2 times (ref. 6: "4-to-1" at power 2): a mirror-symmetric
  rule covering n^2 times has n(n-1)/2 = 1 + 2 + ... + (n-1) extra windings over the flat plane on each side (**reasoned**).
- Sharpening 1, **theorem**: once round is incompatible with hinge-freeness. On such a circle lon -> -lon + const, and
  2a = -a only for a = 120, 240 degrees. **Measured**: the cone rule passes the turn test at 120 degrees (2e-14) and
  fails at 37, 90, 180. So the cone rule is a rule with three special upright half-planes, not a hinge-free rule.
- Sharpening 2, **theorem** (identity theorem): a direction map that is angle-true on a connected band containing the
  equator and doubles exactly on the equator equals w^2 on that whole band. So between the flat plane and the copy
  cone there must be a zone that is NOT angle-true. The blend is not a blemish of the scout; it cannot be avoided.
- Sharpening 3, **theorem** (Riemann-Hurwitz): a fold-free direction map covering 4 times has 6 branch directions. In
  the mirror-symmetric pattern the cap inside each copy cone is laid one-to-one onto the opposite half, and the belt
  between the flat plane and the cone carries exactly 3 branch directions per side. **Measured** for R_t alone:
  latitude +-32.96, at longitudes 0, +-120, sent to latitude +-15.83 above the x-axis line and its two turned copies.
  They can be moved, never removed.
- Why "length squared" wants 4 coverings at all, **reasoned** (area count): the mean over the sphere of the product of
  G's two stretches equals the number of coverings; shape-keeping wants that product to be 4.

## (d) First scout of the cone rule: its numbers CONFIRMED where re-measured; whether the family can be clean is OPEN

- Re-measured: threefold only (above); branch directions and where they go (above, for R_t without the blend).
- **Open**: no theorem says where the three branch directions per side should be sent for the bodies to be clean once
  c is added. In flat dynamics the rule is "every branch point's orbit must fall into an attracting cycle"; in 3D the
  branch set is a bundle of rays to infinity, so part of it always escapes, and I found no published criterion.

## (e) The pillow: CORRECT, and it is the literature's own 3D power map

- The square pillow is Mayer's power map (refs. 5 to 7): **theorem** that all its iterates squeeze by a bounded amount
  and that without c its Julia set is a (quasi-)sphere. "Same spacing everywhere" is exact: maps of the sphere with a
  flat (evenly spaced) structure are power, Chebyshev or Lattès maps (ref. 10).
- **Theorem** (Euler characteristic): a sphere cannot cover itself 4 times with no special points; an evenly spaced
  doubling in two directions needs either 4 corner points (the pillow) or a doughnut (ref. 8's toroidal Julia sets).
  So "bulbs all over in the same pattern, nothing special anywhere" is impossible on a ball-like body.
- **Reasoned**: at power 2 the evenly spaced pillow is lopsided by necessity (a closed straight belt kept by doubling
  sits at one third of the height: 2t = +-t mod h has no other solution off the corners); and through the fixed direction
  +x every straight line of the pillow is kept by the map, one of them running corner to corner and folded onto half of
  itself. In a mirror-symmetric layout that line is the upright plane: the cause of the spindle at c = -1. A layout that
  is not mirror-symmetric bends that surface so that adding c no longer keeps it (worth the `rabbit` section's try).
- **Open** in the literature: nobody has drawn or studied "power map + c" in R^3 (ref. 12 gives a bounded, perfect
  Julia-like boundary if 4 > K_I; whether the lab's pillow has K_I < 4 is not measured).

## (f) What is not possible: CORRECT; theorems as cited, plus two that the briefing does not use

- "Shapes cannot be kept everywhere": **theorem** (Liouville; Gehring 1962, Reshetnyak 1967; ref. 16). A rule
  |v|^2 G is never a sphere-inversion map, so it keeps shapes on a set with no inside (cones over curves at best).
- "No tear-free rule exact on two mirror planes with the 4-and-2 count" (round 17): consistent with the degree
  **theorem**: a fold-free rule has the same number of preimages for every direction. **Reasoned** extra: with both
  mirror planes exact and no fold, the number must be at least 6, with the upright axis itself a branch line and four
  more directions sent to +x on the diagonals (round 17's six-fold caps are this case).
- Not in the briefing: (1) **theorem** (Zorich, ref. 17): a 3D rule with bounded squeeze that is not one-to-one must
  have branch lines. (2) **theorem** (Martio, Rickman, Väisälä) and **open** (Martio's conjecture, ref. 16): near a
  branch line the squeeze cannot be close to none; conjecturally at least the winding number. (3) **Measured**: neither
  the one-plane rule nor the Douady-Earle rule has bounded squeeze: largest over smallest stretch is 11 at latitude 80
  and 1,146 at 89.9 (one plane), 126 at 89 (Douady-Earle). They are not quasiregular maps.

## The user's own guess, "this has to happen with quaternion rotations somehow": NO, for a stated reason

- **Theorem** (ref. 18; also the paper the project started from): the quaternion square commutes with every rotation
  about the real axis, so its sets are the flat set spun. In 3D that is the Lathe: rings.
- **Reasoned**: a point of space gives a direction (two numbers); a rotation needs three. Choosing the third number
  continuously for every direction is impossible (the Hopf bundle has no section); the shortest-turn choice is the Lathe.
- The published Hopf-angle power map (ref. 19) lives in 4D and its 3D cuts are Mandelbulbs.
- The one multiplication of space points in the literature that restricts to the complex product (ref. 1) has the
  one-plane rule as its square.

## Straight answer for `design`: can "two planes" and "along" be ironed into one rule for every c?

1. The buds of both come from a second plane that holds a true copy of the flat picture. For c off the x-axis no such
   plane can exist (**theorem**). So their look cannot carry over to the rabbit by the same means.
2. Without folds there are exactly these roads. Two coverings: no bodies off the flat plane, ever (**theorem**); this
   is the one-plane rule and both published extensions. Four coverings, mirror-symmetric: one copy cone per side,
   three special upright half-planes, three branch directions per side to park (**theorems**; clean bodies **open**).
   Four coverings, evenly spaced: the pillow, lopsided at power 2, four corners (**theorem** / **reasoned**).
3. With folds (two planes, along, fold30) the counts can differ from direction to direction, which is what the liked
   look uses; a fold is a crease, and creases are where shards and fins come from (**reasoned**, not a theorem).
4. I found nothing published that draws a 3D z^2 + c with buds all over. The literature's 3D squares are the one-plane
   rule (exactly), its near twin, and the pillow.
