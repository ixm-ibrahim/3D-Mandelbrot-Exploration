# Round 25, section klein: the paper's own road, done properly

Every statement is marked MEASURED (a number from a script here), SEEN (I looked at the picture named),
REASONED (an argument, not checked by a run) or THEOREM (a short proof is given or it is a textbook fact).

## In six plain lines

1. The paper's road does give the thing the user describes in words, but for a cousin of the flat picture, not for
   the flat picture: a chain of exact balls, each ball carrying smaller balls all over, the same pattern on every
   ball, made only of sphere inversions and whole-number shifts, nothing stretched anywhere ("the pearl tree",
   `sheet.png` top row, `tree-big.png`). SEEN, MEASURED.
2. Its flat cut is exactly the flat pearl tree (0 of 200000 verdicts differ), and the flat pearl tree is not the
   basilica: same bodies in the same order, but every body is a perfect circle and the buds sit at different places.
   At the best setting of its two dials 38.6% of the true area gets the wrong verdict. The eye tells at once. MEASURED, SEEN.
3. It has no c and no power. Its own dials are how big the attached balls are and which whole numbers do the
   shifting (Gaussian: four-fold round the axis; Eisenstein: six-fold). That last one is a pick between two.
4. It can never be a rabbit: three balls cannot touch at one point. THEOREM. Bodies of any picture of this kind meet
   two at a time.
5. The paper's own rule ("square, add c", three caps of inversions) is far from the flat picture: 39 to 62% of the
   true area gets the wrong verdict, the c = -1 solid is lopsided (a third of it has no mirror partner) and the
   rabbit is one rock. MEASURED, SEEN. There is exactly one way to repair its flat cut (re-space the directions);
   I built it: the flat cut becomes exact, the solid stays a lopsided faceted chain with buds only round the flat
   picture, and the rabbit is still one rock. MEASURED, SEEN.
6. Why it must be so: a rule made of pieces of sphere inversions is, on the flat circle, never angle doubling
   (THEOREM), and where two pieces meet off the flat plane it must either tear or crease (THEOREM). The paper's
   "truly 3D" set works only for c on the x-axis because there the tear lies in a mirror that c does not notice
   (REASONED). This corner cannot give the user's object. It gives the pearl tree.

## Files

- `paper2d.py` (`numbers`, `picture`): the paper's flat rule measured. Log `paper2d-numbers.log`, picture `flatcut.png`.
- `tree.py` (`check`, `cuts`, `solids`): the pearl tree. Log `tree-check.log`, pictures `tree-cuts.png`, `tree-solids-a.png`, `tree-solids-top.png`.
- `repair.py` (`check`, `cuts`): the paper's rule with the directions re-spaced (`kfix`). Log `repair-check.log`, picture `repair-cuts.png`. Table `phi-table.npy`.
- `lop.py`: lopsidedness as a number. Log `lop.log`.
- `sheet.py` (`render`, `compose`, `big`): `sheet.png` (front eye), `sheet-top.png` (from above), `tree-big.png`. The kept solids are `depth-*.npz`.
- `best.py`: `rule()` = the pearl tree (Gaussian), `rule('eisen')`, `rule('line')`, `repaired()` = kfix.

## 1. The paper's flat rule: what it is and how far it is from the flat picture

The paper replaces angle doubling on the unit circle by a map h made of three pieces (arcs 0..120, 120..240,
240..360 degrees), each piece a circle inversion followed by the mirror y -> -y, and extends it "by radial scaling":
z -> |z|^2 h(z/|z|) + c. In 3D (its first construction) circles become spheres: three caps round the flat circle.
This is the bench rule `kleinian` (= `out/r14/turns/turns.py` K1); I checked it is the paper's group: caps at 60,
180, 300 degrees, radius 60 degrees, inversion spheres of centre distance 2 and radius sqrt 3. REASONED from the code and the paper's text.

What h is (MEASURED, `paper2d-numbers.log`):
- h agrees with doubling at 0, 120, 240 degrees. Elsewhere it is up to 17.6 degrees off in one step.
- Doubling moves every direction at speed 2. h moves at speeds from 1 to 3. At angle 0 the speed is exactly 1, and
  after two steps at 120 degrees it is 1 again: the three corner directions are "neutral" for h (they neither push
  away nor pull in), where for doubling they push away at speed 2 and 4. This is the heart of the difference.
- The re-spacing phi that turns h into doubling (phi(h(a)) = 2 phi(a)) moves directions by up to 14.9 degrees, and it
  is infinitely uneven: cut the circle into the 48 / 768 / 12288 / 196608 equal arcs that doubling makes after
  4 / 8 / 12 / 16 steps; for h the longest of them is 7 / 168 / 6531 / 79557 times the shortest. The ratio has no bound.
  (This is the "Minkowski question mark" kind of function the briefing mentions.)

The flat cut of the paper's rule against the true flat picture (MEASURED on a 960 x 720 grid, 300 steps; SEEN `flatcut.png`):

| set | wrong verdicts, share of the true area | furthest apart (the set is about 3.2 wide) | what the eye sees |
|---|---|---|---|
| c = -1 | 49.3% | 0.18 | a chain of bodies in the right places, but diamond-shaped, and lopsided: the right side has thin plates where the left has bodies |
| rabbit | 61.5% | 0.32 | one lump. The three bodies that meet in a point are gone |
| c = -0.75 | 48.8% | 0.20 | bodies pulled apart into separate islands (true: they touch) |
| Siegel disc | 39.3% | 0.26 | one spiky lump |

The library's flat check of the same rule: 1342 / 1368 / 1730 / 1435 wrong of 20000 (Mandelbrot, c = -1, rabbit,
Siegel). MEASURED. Lopsidedness for c = -1: 26.7% of the flat cut and 33.3% of the solid has no mirror partner
left-right (one plane, two planes: 0.0%). MEASURED `lop.log`.

So "cousin" is generous. It is a cousin for c = 0 only (there the paper proves it). For the rabbit the flat cut is
not a rabbit at all. The eye can tell for every set. Reason for the lopsidedness: three caps cannot be the same left
and right; reason for the lump: at the directions where the rabbit's bodies meet the paper's map is slower than
doubling, so the meeting point does not push bodies apart hard enough. REASONED (this is the briefing's W-e seen in the flat plane).

## 2. Is there an honest repair?

THEOREM (no repair that stays on the paper's road). A chain of sphere inversions, restricted to the flat circle, is
a "one-over" kind of map of the circle (a Moebius map). Angle doubling is not of that kind on any arc, however
short. So a rule made of finitely many pieces of sphere inversions is never z^2 on the flat plane. With infinitely
many pieces (one fitted at every point) one gets the scout's `fit` rule: pillars.

The one repair there is: keep the paper's pieces and re-space the directions round the upright axis by phi before
and after (`repair.py`, `kfix`). MEASURED (`repair-check.log`): flat check 0 / 0 / 0 / 0 of 20000 (with the flat plane
written out exactly; the table alone gives 4 / 1 / 6 / 3, which is the table's accuracy); the rule is continuous
across the flat plane (at height 1e-6 the square is within 4e-5 of the flat square); length is kept.
The price, MEASURED: the re-spacing squeezes without bound (the circle cut into 256 / 4096 / 65536 / 1048576 equal
arcs: the longest re-spaced arc is 94 / 2965 / 91459 / 1230066 times the shortest).
SEEN (`sheet.png`, `sheet-top.png`, bottom row; `repair-cuts.png`): for c = -1 a chain of separate, faceted,
leaf-shaped bodies with a ridge along each and buds only round the flat picture, visibly different left and right
(12.8% of the solid has no mirror partner, MEASURED); for the rabbit one rough rock from both eyes although its flat
cut is the exact rabbit. So the repair buys test 1 and nothing else. It is worse than "one plane" on every other
count. I did not polish it. (Solids: 200 depth blocks, 28 steps; the rabbit of kfix 140 blocks, 24 steps, enlarged;
three of the four kfix solids use every 8th entry of the table, `KFIX_FAST`, good to 1e-5 in angle.)

THEOREM (where pieces meet). Take any map of directions made of pieces of sphere inversions. If two pieces agree
along a seam, then one piece followed by the other backwards leaves every point of the seam where it is. A chain
of inversions that leaves a curve pointwise fixed is either doing nothing or is the mirror in a sphere through that
curve. So across every seam the map is either one and the same piece (no seam), or the two sides are sent to the
SAME side (a crease: the surface is folded back), or the pieces do not agree (a tear). The paper's first
construction creases along the rims of its caps (SEEN: the ridges on the bodies in `sheet.png`, bottom left); its
second construction has caps that overlap (the caps at 60 degrees round the flat circle and the upright circle have
centres 75.5 degrees apart and radius 60 degrees each: REASONED from the paper's numbers), so a choice must be made
in the overlap and the choice is a tear.

REASONED (what the paper's author ran into: "limited to c in R"). A tear between two pieces that are mirror images
of each other does no harm if c lies in the mirror: the two choices give mirror-image orbits and the same verdict.
The paper's two families of caps are swapped by the mirror y <-> z, which keeps the x-axis. For c on the x-axis the
tear is invisible; for the rabbit the two choices disagree and the set is shards. This is the briefing's (W-b) again
and matches what the lab's "Kleinian squaring, two planes" shows.

## 3. The "not chosen" group, and the pearl tree

The paper's flat group (g1 a half turn, g2 a shear that fixes the point 1) is the modular group of level 2: its
tile is the triangle with corners at 0, 120, 240 degrees on the circle, quotient with one cone point and two cusps.
REASONED (area count pi = 2 pi (1/2)). The groups that contain it and act on the WHOLE sphere of directions by their
own symmetry are the Picard group (2 x 2 matrices of Gaussian integers a + bi) and its Eisenstein sister. On the
sphere such a group has no "outside": every direction is a limit direction. So it gives no rule of the paper's
kind (by the THEOREM above any one-step map built from it tears or creases), but it gives a picture as a group:

THE PEARL TREE (`tree.py`). In the group's coordinates: everything below a plane is one body; everything above a
second plane, at height 2t, is the body that touches it at the far point; the group is generated by whole-number
shifts in the plane and the inversions in the unit spheres about (0, 0, 0) and (0, 0, 2t). A point is inside if
some chain of these moves brings it below the first plane or above the second. The chain is found by the recipe of
continued fractions: shift to the nearest whole number, invert if inside a unit sphere, repeat; a point left
between the planes and outside both spheres is outside for good. One sphere inversion then brings the picture into
the usual frame (middle ball k^2 wide). In quaternion words: m -> m - (nearest a + bi), then m -> 1 / conj(m).

- THEOREM (Klein-Maskit combination, standard): for t >= 1 the group is discrete, so the bodies are exact balls
  with disjoint insides, they touch two at a time, and they form a tree. MEASURED consistent: 8 rounds of the
  recipe decide every one of 200000 random points the same way as 80 rounds.
- Bulbs all over, by themselves: on every ball the smaller balls sit at ALL the fractions p/q of Gaussian
  integers, with size falling like 1 / |q|^2. Nobody places them. Every ball carries the same pattern, and on one
  ball the pattern looks the same from every bulb (a chain of inversions moves any bulb to any other and the whole
  tree onto itself). REASONED (Picard has one class of cusps); SEEN (`tree-big.png`, `sheet.png`).
- Nothing is stretched: every move is a sphere inversion or a shift. THEOREM (Liouville's other side).
- THEOREM + MEASURED (the flat cut is exact, for the tree's own flat picture). The cut z = 0 of the 3D tree is the
  flat tree made from ordinary whole numbers (the modular group). Proof: the mirror z -> -z maps the tree to itself;
  a ball that crosses the flat plane without being centred on it would overlap its mirror image, which is another
  ball of the tree; and a ball centred on the plane hangs on a chain of balls centred on the plane (a tree has only
  one chain between two balls), touching at ordinary fractions. Measured: 0 of 200000 verdicts differ, for the
  Gaussian and for the Eisenstein tree.
- How far the flat tree is from the true basilica, MEASURED (`tree-check.log`): best fit of the two dials
  (k^2 = 1.05, t = 1.40): 38.6% of the true area gets the wrong verdict; furthest apart 0.325. SEEN
  (`tree-cuts.png`, top row): same layout (middle body, two neighbours, a bud above and below, small end bodies),
  but circles instead of pointed bodies, kissing instead of pinched, and the buds at the fractions (1/2, 1/3,
  2/3, ...) instead of at the halvings (1/2, 1/4, 3/4, ...).
- REASONED, from standard results (not re-derived here): no re-spacing with bounded squeeze turns the flat tree into
  the basilica. Between two kissing circles the outside narrows to a sliver; between two bodies of the true basilica
  the outside keeps a full wedge; a map with bounded squeeze cannot open a sliver into a wedge. So the tree cannot
  be repaired any better than the paper's rule can.
- The one pick. Round each touching point the neighbours are laid out by the lattice of shifts. A lattice of shifts
  in a plane is unstretched only if it is square (Gaussian, four-fold) or hexagonal (Eisenstein, six-fold): THEOREM
  (the crystallographic restriction). SEEN (`tree-cuts.png`: the upright cut of the Gaussian tree is its flat cut
  again, the upright cut of the Eisenstein tree is a different, finer pattern; `tree-big.png`, bottom row, nearly
  end-on: four large buds round the waist against six). So "4 or 6" is a choice of ours, the Kleinian form of "the
  limitations of 3D rotations". Both have the same flat cut (MEASURED). Cuts at other angles through the x-axis
  show other patterns (45 degrees in the Gaussian tree: buds in pairs, `tree-cuts.png` bottom row), so "the same
  pattern everywhere" is true ball by ball and bud by bud, not cut by cut.
- Solids: `sheet.png` / `sheet-top.png` top row at 280 depth blocks, `tree-big.png` at 320, 14 rounds each. SEEN
  from three eyes: balls on balls on balls, nothing between them, no plates, no rings.
- `pearl tree, one plane` (shifts along the line only) is the paper's "inflated" construction applied to the tree:
  buds only round the flat picture. SEEN (`sheet.png`, top left).
- The Hurwitz quaternions one dimension up: a tree of 4D balls with shifts by a + bi + cj. Its 3D cut through the
  plane of 1 and i is the Gaussian tree again, by the same mirror argument. REASONED. Nothing new for a 3D picture.

## 4. What plays the role of the rabbit, and of c

- There is no c. What plays its part is the group's own dial: where, and how large, the second copy is glued on.
  Height t = size of the attached balls (t large: one ball alone, the picture of c = 0; t = 1.4: nearest the
  basilica; t -> 1: neighbours as large as the middle ball, a long string, `sheet.png` top right). A sideways shift
  of the glued copy would bend and spiral the chains (the 3D form of the "Maskit slice"; this is what the paper's
  Figure 4, top, after Sakugawa, draws). I did not build the sideways shift: with the full group only four shifts
  are allowed, and the continuous dial needs a subgroup with more faces. REASONED.
- THEOREM: three balls with disjoint insides cannot share a point (at a shared point all would have the same
  tangent plane and each lies on one side of it; two on one side overlap). REASONED, standard: the same holds for
  the non-round bodies of any group picture of this kind: at a touching point exactly two bodies meet. So nothing
  on the Kleinian road is a rabbit. The nearest relatives are settings where bodies close up in rings of three
  round a small gap (the "1/3 cusp" of the Maskit slice in the flat case). Not built.
- In the flat plane there IS a known object that holds a rabbit next to a modular-group pattern: Bullett and
  Penrose's mating (for every c of the Mandelbrot set). But its rabbit half is made by a genuine two-to-one move
  (it comes from a cubic polynomial), not by inversions, its rabbit is a slightly distorted copy with one tip
  sharpened, and a 3D version would need a many-to-one shape-keeping move of space, which does not exist. REASONED
  from the literature as I remember it; not checked against the papers tonight.

## 5. Section 3 of the briefing (the wall), seen from here

- (W-f) "no chain of inversions is z^2": confirmed and sharpened (section 2: never on any arc; and the seam theorem).
- (W-d) holds for a DOUBLING pattern. The pearl tree shows what the hidden assumption is: its pattern is the same
  everywhere on a ball and has no special point at all, because it is made by infinitely many one-to-one moves
  (inversions), not by one two-to-one move. A two-to-one move of a ball's skin always has special points; a
  pattern of fractions does not need them; but a pattern of fractions is not the flat picture of z^2 + c.
  This is a real hole in the wall as worded, and it leads to the cousin, not to the user's object.
- Door (iii), "limit sets of groups": open, walked through here. What is behind it: inflated, bulbs all over by
  themselves, unstretched, exact flat cut OF THE COUSIN. Not the flat picture, no rabbit, no power.
- The briefing calls the paper's flat cut "a cousin". For c away from 0 it is less than that (table in section 1).
- (W-b) and "limited to c in R": consistent with what I find (section 2).

## 6. Which of the user's tests fail

Pearl tree (best object of this corner): fails test 1 (the flat cut is the flat tree, 38.6% away from the true
c = -1 picture at best; exact only for its own flat picture), fails test 4 for the rabbit and every c that is not
"a chain of bodies meeting two at a time" (THEOREM), fails test 5 and makes test 2 empty (no power in it; one
pick, 4-fold or 6-fold). Passes test 3 (no shards, no smear, no rings: exact balls) and is not lopsided (0.0%
without a mirror partner, MEASURED).
The paper's rule: fails 1, 3 (creases, plates), 4, and is lopsided.
The paper's rule re-spaced (kfix): passes 1; fails 4 (buds only round the flat picture; rabbit one rock), is
lopsided, squeezes without bound.

## 7. For next, from this corner

- Nothing on this road reaches the user's object; I would not spend another round on Kleinian rules "square, add c".
- If the user would like to SEE what "bulbs all over, by themselves, nothing stretched" looks like when it is done
  with no compromise, the pearl tree is that picture, and it could be a lab entry of its own ("Kleinian cousin"),
  clearly labelled as not the flat picture. Its natural further dials: the sideways shift (spiralling chains), and
  the hexagonal sister.
- The useful lesson for the other corners: the all-over pattern that needs no special points is the pattern of
  fractions, and the price of the pattern of halvings is corners (pillow) or one plane.
