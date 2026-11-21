# Round 25, section "vahlen": the squares that the quaternion arithmetic of sphere inversions offers

Every statement is marked **measured** (a number I computed), **seen** (in a picture I looked at), **reasoned**,
**theorem** (short proof given or checked by a formula) or **read** (web, with how much of it I read).
Paths are relative to the project root. Code: `out/r25/vahlen/vrules.py` (all rules), `check.py` + `check2.py`
(identities, flat check; outputs `check.txt`, `check2.txt`), `measure.py` (`measure.txt`), `saddle.py` (`saddle.txt`),
`cuts.py` (`cuts-main.png`), `sheet.py` + `combine.py` (`sheet.png`, `sheet-top.png`), `best.py`.

## 0. Result in six plain lines

1. Nothing in this corner passes. The quaternion language gives exactly three kinds of square, and I built all three.
2. Kind one, every way of multiplying the point with itself as quaternions: always the quaternion square about some
   axis in the flat plane. Rings for c = -1 or a ridged lump; never round bulbs. Already in the lab.
3. Kind two, the one square that needs no choice at all (`holo`, new, one line of formula): clean and exact, but it is
   the one-plane picture pressed flatter. Bulbs only round the flat picture.
4. Kind three, the user's own guess taken literally (`spin`: the point carries a quaternion turn along its orbit, and
   squaring means doing that turn twice): exact on the flat plane; for c = -1 it IS the quaternion square (rings);
   for the rabbit there is no body at all off the flat picture. Both numbers and the reason are below.
5. Why, in one sentence: a turn in space has one number more than a direction has, and that extra number can be
   neither chosen everywhere nor carried along without a tear at the origin; and the origin is the one place every
   body's orbit goes through.
6. Section 3 of the briefing stands from this side. One sharper form of it and one published theorem are in section 4.

## 1. The language (worked out before coding)

A point is v = x + y i + z j. a* means a with the sign of its k part flipped; the points are the quaternions with
v* = v. The chains of sphere inversions that keep 0 and infinity are the turn-and-scale maps w -> a w a*.
Such a map carries the base point 1 to a a*. So a point v "is" the turn-and-scale that carries 1 to v, written as a
quaternion a with a a* = v (its spinor). In the flat plane this is z = "multiply by z", and z^2 = "do it twice".

- **theorem** (two lines): the square of v in this language is a (a a*) a* = (a a)(a a)*: the point of the spinor
  squared. "Squaring the matrix instead of the point" is this and nothing else: the matrix of the turn-and-scale is
  diag(a, 1/a*), its square is diag(a a, ...). (The other matrices a point has are useless: the translation by v
  squares to the translation by 2v; the point as a sphere of radius 0 squares to itself, **reasoned**, by hand:
  M^2 = 2 Im(v) M.)
- **theorem**: a is fixed only up to a roll about the x-axis: a and a e^(k t) have the same point (**measured** 2e-12,
  `check.txt`), but different squares. The squares of one point fill a circle through the quaternion square v v and
  the point |v|^2 on the x-axis (**measured**, `check2.txt`: the point (0.3, 0.5, 0.4) rolled by 0, 30, ... 150 degrees
  squares to (-0.32 0.30 0.24), (-0.12 -0.02 0.49), (0.29 -0.17 0.37), (0.50 0 0), ...). This free roll is "the
  limitation of 3D rotations" in one picture. Everything below is a way of dealing with it.

## 2. The three kinds

### A. Every one-term quaternion product: the Lathe about an axis in the flat plane  (rule `lathe_b(beta)`)

- **theorem** (worked by hand; formulas checked to 1e-14 in `check.txt`, `check2.txt`). On the points, the four
  involutions of the quaternions leave only v and its conjugate. A product a v b v c, a v b v-bar c, a v-bar b v c or
  a v-bar b v-bar c that is z^2 on the flat plane and lands in space again is, for some angle beta,
      F_beta(z, t) = ( z^2 - t^2 e^(-2 i beta) ,  2 t Re(e^(i beta) z) )        (z = x + i y, t = height)
  = turn about the upright axis by beta, quaternion square, turn back by 2 beta. beta = 0 is the Lathe. It is the
  lab's "Quaternion square" and "Quaternion square, twisted". No other one-term product exists.
- **theorem**: sums of such terms give every quadratic rule that is z^2 on the flat plane and the same above and
  below: F = (z^2 + A t^2, t Re(P z)), two complex numbers A, P. None of them treats the directions round the upright
  axis alike except the flattening (z^2, 0).
- **theorem + measured**: every quadratic rule sends v and -v to the same point, and on a ball that forces a fold:
  half of all directions come out turned inside out (**measured** 0.504 for the Lathe, 0.494 for beta = 90, 0.000 for
  one plane and `holo`; `check.txt`). In the flat plane z and -z are a half turn apart, which harms nothing; in space
  v and -v are a mirror image apart. So no formula that multiplies two quaternions built from the point can be free
  of folds. This is the plain reason behind the taffy.
- **seen** (`sheet.png`, `sheet-top.png`, row "lathe 90"): c = -1 is one ball with onion ridges; the rabbit is one
  ridged spindle. (`cuts-main.png` row 3: the Lathe itself, rings for c = -1, taffy for the rabbit.)
- Fails tests 3 and 4. Not new.

### B. The spinor square that needs no phase  (rule `holo`, new)

- **theorem**: a quadratic rule on spinors gives a rule on points without any choice only if a roll of the spinor
  rolls the result by a fixed multiple. Split the spinor into its two complex halves: the multiple can be 0 or 2 (or
  -2, the mirror image). Multiple 0 means the rule is the Hopf map of a linear picture of the point: the Lathes of A
  again. Multiple 2 means each half is squared in complex arithmetic, and then exactness on the flat plane leaves
  ONE rule (a complex-analytic map of the ball of directions that doubles the flat circle is w -> w^2 and nothing
  else): halves taken about the upright axis, each squared, times root 2. In coordinates
      square(x, y, z) = ( x^2 - y^2 , 2 x y , 2 z |v| ).
  **measured**: equal to the spinor formula to 7e-13 for any phase (`check2.txt`). Flat check 0, 0, 0, 0 of 20,000.
  It is the one-plane rule without its length correction: same directions, length |v|^2 (1 + sin^2 latitude).
- **seen** (`sheet.png`, `sheet-top.png`, row "holo"): the same bodies as one plane in the same places, pressed into
  lenses with a sharp rim; small buds only round the flat picture. **measured**: over the centre of the c = -1 body it
  reaches height 0.248, one plane 0.511 (`measure.txt`).
- Passes 1, 2, 3, 5. Fails test 4 (nothing off the flat picture), exactly as (W-a) says it must: it treats all
  directions round the upright axis alike and neither folds nor tears. It is not better than one plane.

### C. The quaternion turn carried along the orbit  (rule `spin`, new)

The user's guess, literally. The orbit carries the spinor a (a turn-and-scale), not just the point.
    step:  b = a a ;  the square is b b* ;  add c ;  new a = g b,  g = the shortest turn-and-scale from b b* to b b* + c
           (g = square root of (w + c) w^-1, w = b b*: no extra roll; this is the natural way to move a frame).
Doing a turn twice is consistent by construction, so (W-c) does not bite inside one orbit. The first spinor has to
be chosen: `spin-V` takes the shortest turn from the x-axis (undefined on the negative x-axis), `spin-up` tips up by
the latitude and turns by the longitude (undefined on the upright axis).

- **measured**: flat check 0, 0, 0, 0 of 20,000 for both starts; a flat orbit never leaves the plane (`check.txt`).
- **theorem + measured**: for c on the x-axis `spin-V` is the Lathe (the carried turn never rolls: w and w + c lie in
  one plane with the x-axis). 0 of 200,000 verdicts differ for c = -1 and c = -0.75 (`measure.txt`). Rings.
- **measured**: for c off the x-axis there is no body off the flat plane. Flat points that stay, lifted by a height
  of 1e-8: share that still stays = 0.000 (rabbit), 0.000 (c = -0.12 + 0.6i), 0.008 (Siegel disc), for both starts;
  one plane keeps 1.000 (`measure.txt`). Of 200,000 random points of the box, 0 stay for the rabbit.
- **measured**, the reason (`saddle.txt`): at the flat rule's attracting cycle the carried roll GROWS. Growth of one
  trip round the cycle, in the four directions of spinor space: c = -0.12 + 0.6i: 21.3, 0.84, 0.84, 0.005;
  c = -0.10 + 0.70i: 21.8; c = 0.2 + 0.3i: 2.35; c = -0.9 + 0.05i: 1.55; c = -0.9: 0.40 (no growth on the x-axis).
  The two 0.84 are the flat pull; the 21.3 is the roll feeding the height. The flat picture is a knife edge.
- **theorem** (the tear is not my choice of g): NO rule can carry a spinor continuously through "add c". Take a small
  ball of points round -c. Over it a spinor can be chosen smoothly (it does not hold the origin). Adding c moves the
  ball onto the origin, and round the origin no smooth choice of spinor exists (the hairy ball; the Hopf map has no
  section). **measured** (`measure.txt`): start 1e-2, 1e-4 or 1e-8 from the origin at latitude 10: the square after
  next lands at (-0.514, -0.178, -0.170) all three times, not at c^2 = (-0.540, -0.183, 0). Only the direction of
  arrival counts, however close the orbit comes. The centre of every body goes through the origin.
- **seen** (`sheet.png`, `sheet-top.png`, rows "spin-V", "spin-up"; `cuts-main.png` rows 5, 6): see section 3.
- Fails test 3 (rings, c = -1) and test 4 (nothing at all for the rabbit); `spin-up` also tears along the upright axis.

## 3. What the pictures show

All **seen**; rough solids at 200 blocks, 30 steps, c = -1 and the rabbit. `sheet.png` looks down on the flat picture
(eye at (0.45, 0.5, 1)); `sheet-top.png` looks along the flat plane, so it shows the thickness (eye at (0.2, 1, 0.35)).
Rows: one plane (baseline), holo, lathe 90, spin-V, spin-up.

- one plane: round blown-up bodies in a row, small buds only round the flat picture. The baseline.
- holo: the same bodies in the same places, each pressed into a lens with a sharp rim, about half as tall. Buds only
  round the flat picture. Nothing above or below.
- lathe 90: c = -1 is one ball wrapped in onion ridges with no separate bodies; the rabbit is one ridged spindle.
- spin-V: c = -1 is the quaternion square's picture, bodies turned on a lathe with stacked rings; the rabbit panel
  is EMPTY from both eyes (no block stays).
- spin-up: c = -1 is the same ringed bodies on the right and one large torn shell on the left, cut off along the
  upright axis; the rabbit panel is empty.
- `cuts-main.png` (cuts tilted 0, 30, 60, 90 degrees about the x-axis, 50 steps): one plane and holo show blobs with
  no buds once the cut is tilted; the Lathe repeats the flat cut at every tilt for c = -1; spin-V does the same for
  c = -1 and shows nothing in any tilted cut of the rabbit; spin-up shows a half disc with a straight edge on the
  upright axis.

Captions a person could be shown (two short sentences each):
- holo: "Every body is blown up, but flatter than before. Buds sit only round the flat picture."
- spin, c = -1: "The bodies are turned on a lathe: rings, not bulbs."
- spin, rabbit: "Nothing is left off the flat picture. The rabbit has no body at all."

## 4. On section 3 of the briefing (the wall)

- I found nothing wrong in (W-a), (W-c), (W-f). Each of my three kinds lands in a box of (W-a) or of (W-c).
- **A sharper (W-c), theorem** (section 2C): not only "no fixed choice of the extra roll" (known), but also "no
  carried one": any memory that holds a full turn tears at the origin. Door (i), "carry a quaternion frame along the
  orbit", is closed for frames that are tied to the point's own direction. (A carried PLANE, as in "along once",
  is not hit: a plane through the x-axis is one number, not a full turn.)
- **A sharper reason for "nothing chosen gives nothing new", theorem**: if the rule is length times a map of
  directions and that map keeps shapes on the ball of directions, exactness forces it to be w -> w^2, whose
  preimages of flat directions are all flat. So every bulb off the flat picture costs squeeze at the very first
  step, whatever the symmetry. (This does not need the "all directions alike" of (W-a).)
- **read** (search-result snippets only, not the papers): G. Martin, "Extending rational maps", Conformal Geometry
  and Dynamics 8 (2004) 158-166, asks when a flat rational rule extends to the half-space above the plane with squeeze
  that stays bounded under iteration; Meyer and Muench (arXiv 2510.18015) list among Martin's "no" cases every rule
  with a super-attracting fixed point. Every polynomial has one (infinity). If that reading is right, z^2 + c has no
  extension that keeps the upper side up and keeps bulbs round at every depth: (W-f) as a published theorem. The
  judge should read the paper before this is told to anyone.
- (W-b) as worded is about a second plane that the rule maps into ITSELF. A plane that the rule maps into the flat
  plane holds a copy for every c (**reasoned**), but such a plane needs a fold or a tear between the two halves of
  the flat plane (**reasoned**: a fan folded between two half-planes 180 degrees apart cannot be the identity on
  both). So the conclusion of (W-b) stands. **measured** (`wb.py`, `wb.txt`): in the bench rules `twoplane` and
  `along` the upright plane is the flat picture stood up for c = -1 (0 of 40,000 verdicts differ) and is not for the
  rabbit (3,764 and 4,313 differ) or the Siegel disc (5,496 and 4,953).

## 5. For the next round, from this corner

Nothing further in quaternion products or spinors: the list in section 2 is complete (theorems). If the judge wants
one more try: the 3D point set of all points for which EVERY roll at every step stays (no choice, no tear). I did not
build it: on the flat plane it is at most the flat picture and, for c = -1 already, it needs the whole circle
through z^2 - 1 and |z|^2 - 1 to stay, so its flat cut is very likely smaller than the flat picture (**reasoned**).
