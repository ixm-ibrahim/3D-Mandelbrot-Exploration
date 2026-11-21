# Round 25, section `torus`: the doughnut corner. Result: it does not work, and this is exactly why

Marks: **measured** (a number from `check.log` / `axis.log`), **seen** (a picture I looked at), **reasoned**,
**theorem** (short proof given here). Nothing here beats the one-plane rule. No rule of this corner is a candidate.

## Six plain lines

1. I built three things on the doughnut idea and drew them. None gives round bodies with bulbs all over.
2. Squaring done on every sphere through the flat unit circle ("book"): the flat picture is exact, but nothing
   exists off it. For c = -1 the solid is empty. A point lifted off the flat picture is twice as high after every
   round of the orbit, and far points are never thrown out, they only slide along their sphere.
3. Doubling the swing round the flat circle as well (what a doughnut needs): the flat cut is wrong at once, because
   the outside of the flat circle is folded onto the inside. Only an odd number of turns keeps it; three is the least.
4. Three turns round the flat circle, then one plane ("ring3"): flat picture exact, extra bodies come by themselves,
   but they are hundreds of thin skins all hinged on the flat circle, like an onion. For the rabbit they crumble away.
5. The honest quaternion doughnut ("hopf"): c = 0 is a perfect doughnut with the doubling pattern evenly all over it.
   For c = -1 and the rabbit every body becomes a twisted band wound round the others. Its flat cut is not the flat
   picture.
6. This cannot be repaired: a doughnut-shaped body can never have the round disc as its flat cut (proof below). So the
   one surface that carries the doubling pattern with no special point is ruled out by the user's first test.

Tests failed. `book`: test 4 (no bodies off the flat picture at all). `ring3`: tests 3 and 4 (skins and crumbs, no
round bodies, nothing for the rabbit); the c = 0 body is not a ball. `hopf`: tests 1, 3 and 4.

## The setting (internal words)

Space with the point at infinity is the sphere of unit quaternions w1 + w2 j seen through one sphere inversion:
w1 = 2(x + iy)/(1 + |v|^2), w2 = ((1 - |v|^2) + 2iz)/(1 + |v|^2). The RING is the flat unit circle (w2 = 0), the AXIS
the upright axis with infinity (w1 = 0); they are linked. In the upright half-plane of a point put
zeta = rho + iz and d = (zeta - 1)/(zeta + 1) = r e^(i sigma). Then d = 0 is the ring, |d| = 1 the axis, d = -1 the
origin, d = +1 infinity, d real the flat plane. sigma is the angle ROUND THE RING (sigma constant = a sphere through
the unit circle, a "page"), r constant a doughnut round the ring (r = tan 22.5 deg is the Clifford torus),
D = 2 artanh r the distance from the ring in the half-plane's own (hyperbolic) geometry, phi the longitude.
The flat rule in these words: phi -> 2 phi, D -> 2D (r -> 2r/(1 + r^2)), sigma stays 0 or 180. (**theorem**, two
lines of algebra; **measured**: flat check 0 for every rule built on it, with and without a rounding guard.)

## What was built (`torus.py`; pictures `sheet.png`, `sheet-top.png`, `cuts.png`)

| name | the "square" | flat check (of 20,000: M / c=-1 / rabbit / Siegel) | what the pictures show |
|---|---|---|---|
| `book` | phi -> 2phi, D -> 2D, sigma kept | 0 / 0 / 0 / 0 | c = 0: the whole box is solid (nothing leaves). c = -1: empty. rabbit: only dots where blocks sit on the flat plane. **seen** |
| `ring2` | as book, sigma -> 2 sigma | 4290 / 2960 / 2715 / 3770 | not drawn as a solid (flat cut wrong) |
| `clif` | (w1, w2) -> (w1^2, w2^2)/length | 2776 / 5082 / 7005 / 13623 | c = 0: a clean doughnut (flat cut a wide ring, upright cut two discs). c = -1, rabbit with "+ c": speckle. **seen** in `cuts.png` |
| `tor3` | as book, sigma -> 3 sigma | 0 / 0 / 0 / 0 | speckle everywhere: no escape, chaos along the upright axis. **seen** in `cuts.png` |
| `ring3` | wind 3 times round the ring (D, phi kept), then one plane | 0 / 0 / 0 / 0 | c = 0: a wafer-thin disc inside nested skins. c = -1: skins and crust. rabbit: crumbs. **seen** |
| `ring3b` | one plane, then wind 3 times | 0 / 0 / 0 / 0 | the same kind. **seen** in `cuts.png` |
| `hopf` | the unit quaternion goes to (w1^2, w2^2 + c w1^2)/length; a point is inside when w2/w1 stays under z^2 + c | 2064 / 14370 / 12335 / 14925 | c = 0: a doughnut. c = -1, rabbit: twisted bands swirling round a hole. **seen** |

## The orchestrator's two obstacles: both correct, and sharper than stated

**Obstacle 1** (doubling the angle round the unit circle). Correct. **theorem**: the flat plane is the two pages
sigma = 0 (outside the unit circle) and sigma = 180 (inside). A rule that multiplies sigma by k keeps both pages in
place only for odd k; k = 2 sends 180 to 0, so the inside is folded onto the outside. **measured**: `ring2` and the
Clifford doubling `clif` fail the flat check at 2,700 to 13,600 of 20,000 points. More: for a rule that treats all
directions round the upright axis alike, (winding round the ring) = (how often the upright axis is wound onto
itself), and the degree of the whole map is twice that. So the choices are 1 (one plane, book), 3, 5, ...

**Obstacle 2** (page by page there is no escape). Correct. **measured**: for a far point,
|book(v)| x sin(elevation) / |v| = 0.9999 .. 1.0000 at |v| = 1000 (z^2 would give 1000): the point is slid to the top
of its own sphere through the unit circle and then sits on the upright axis. At c = 0, 88 % of the test box never
leaves. A second fact kills it for every other c. **measured**: above the 2-cycle of c = -1 a height h becomes
2.000 h after one round (h = 0.0001, 0.001, 0.01). So the flat cycle that should hold a body pushes everything off
the flat plane away; the share of the box inside is 0.0067 after 30 steps and 0.0000 after 120 (rabbit: 0.47, then
0.0000: a slow leak, not a body).

**reasoned** (a tidy way to see three known rules at once): in the upright half-plane the flat ray is a straight
line of the half-plane's own geometry, and the flat rule doubles the distance from the ring along it. There are
three natural ways to carry "double the distance" off the line: round the ring point (`book`: no escape), by
perpendiculars to the line (this is exactly the one-plane rule), and from the end point at infinity (pillars: the
scout's `fit`). The torus picture adds nothing to this list except the winding number.

## Obstacle 3 (new): a doughnut cannot have the flat picture as its cut

**theorem.** Let the c = 0 body be mirror-alike above and below the flat plane, with a skin that is one closed
surface meeting the flat plane in exactly the unit circle. Then the skin is not a doughnut.
Proof: the flat circle cuts the skin into the part above and the part below, which are mirror images, so two pieces
of the same kind. A doughnut skin cut along one closed curve is either still one piece (a tube), or a cap and a
doughnut with a hole: never two equal pieces. (Counting: two equal pieces need an even number of handles: 0, 2, 4.
A sphere works. Two handles would work, but a surface with two handles carries no doubling pattern at all.)
Without the mirror condition only a lopsided "ball with a handle on one side" is left.
Consequence: (W-d)'s remark "a doughnut needs none" is true and useless here. Even doubling with no special point
needs a doughnut; the exact flat cut forbids the doughnut. So the special points of (W-d) are forced.

**reasoned**, same family: any object made by sweeping the flat picture along circles (rotation round the ring, the
Hopf circles, any other family) shows each flat point twice on the flat plane (a closed curve crosses a plane an
even number of times), unless the circles are upright lines closed at infinity (pillars). So no swept object can
pass test 1 except prisms.

## The version that survives obstacle 1: `ring3`, and why it fails

Wind space three times round the flat circle (each sphere through the unit circle goes to the one at three times
its angle; distance from the ring and longitude kept), then apply the one-plane square. Exact on the flat plane, the
same in every direction round the upright axis, nothing chosen except "three = the least odd number above one".
Not of the form "length squared times a map of directions" (**measured**: |F(v)|/|v|^2 runs from 0.00015 to 2900),
so it is door (ii), and it covers space six times, so (W-a)'s "nothing new" does not apply.

- c = 0 is not a ball. **measured**: on the upright axis the inside reaches from 0 only to h = 0.105 (the axis map is
  h -> tan(3 atan h)^2, about 9 h^2 near 0, so its basin ends near 1/9), then 468 separate inside stretches follow
  between h = 0 and 6 (widest 1.38..2.24 and 4.17..5.03). **seen** (`cuts.png`, `sheet.png`): a thin disc inside
  nested bowls, every bowl hinged on the flat circle.
- **reasoned**, why this must be: the inside of the unit ball spans half a turn round the ring; three times half a
  turn is one and a half turns, so the ball cannot go into itself. Whatever is wound more than once round the flat
  circle is joined to the flat picture along the whole circle, never at points.
- c = -1: 18 % of the box stays for good (**measured** 0.297 / 0.198 / 0.185 / 0.184 after 30 / 60 / 120 / 240
  steps). **seen**: skins and a rough crust, no round bodies.
- rabbit: nothing real. **measured** 0.234 / 0.053 / 0.003 / 0.0005. **seen**: crumbs.
- `tor3` (the same without the one-plane step) has no escape at all: the upright axis is wound three times onto
  itself with nothing pulling to infinity. **seen**: speckle.

**reasoned**, the general statement behind it (uses the standard fact that a map of space that covers several times
can only branch along curves, never at single points): for a rule that is alike in all directions round the upright
axis, an extra body can be joined to a blown-up flat body only (1) along the flat circle itself (`ring3`: skins),
(2) along a whole circle of latitude where the rule branches, and on the body's skin that is exactly (W-a)'s fold
(measured as lumps in round 24), or (3) not at all (bodies floating above and below, on the upright axis). Bulbs
joined at single points off the flat picture do not occur. I built (1); (2) is round 24's cone-fold; (3) not built.

## The quaternion doughnut `hopf` (what the corner gives when left to itself)

Square the two complex halves of the unit quaternion, with c added the only way that keeps lengths out of it:
(w1, w2) -> (w1^2, w2^2 + c w1^2)/length. The number w2/w1 then moves exactly by z -> z^2 + c, and the circle of
quaternions with the same w2/w1 (a Hopf circle) turns twice. For c = 0 this is the Clifford doubling: the Clifford
torus stays, both of its angles are doubled, and the map is shape-keeping there (**reasoned**: factor 2 in all
three directions on the torus). This is the true "even doubling on a doughnut".

- **seen**: c = 0 a clean doughnut. c = -1 and the rabbit: twisted bands swirling round a hole; no round bodies,
  no bulbs. **reasoned**: every body of the flat picture is swept along a circle into a band, the bands wind once
  round each other, and where two flat bodies touch at a point two bands touch along a whole circle.
- flat cut: **measured** differs from the flat picture at 28,861 (c = -1) and 24,904 (rabbit) of 40,000 points.
  Each upright half-plane holds one whole copy of the flat picture, but stretched outward by a factor 1.0 to 2.7
  (**measured**: read through d = z/2 it still differs at 5 % and 15 % of points).
- Why bulbs do not appear on the doughnut: all of the dependence on c sits in the one number w2/w1; along the
  circles the rule only turns. So the pattern on the doughnut is stripes, not spots. (**reasoned**)
- The same rule with c added as a shift of 3D space (`clif`) has no escape either: speckle. **seen**

## On section 3 of the briefing

- (W-a) as written in ROUND25 leaves out its own assumption (round 23: F = length squared times a map of
  directions). Without it there are two more ways: winding an odd number of times round the flat circle, and
  branching along a circle of latitude off the flat plane. Neither opens the wall (see above), but the list of four
  is not complete as stated.
- (W-d) stands, and obstacle 3 closes its loophole.
- Both obstacles named for this section are correct.
- I found nothing in this corner that contradicts the "adds up to" reading.

## Files

`torus.py` (rules, `check`, `cuts`, `row`, `sheet`), `axis.py` (the small measurements), `best.py` (`rule()` =
ring3, also `book()`, `hopf()`), `check.log`, `axis.log`, `cuts.png` (flat and upright cuts of all seven),
`sheet.png` (rough solids, eye in front), `sheet-top.png` (the second eye), `row-*.png` (the strips).
Rough solids: 170 blocks deep, 60 steps, c = 0, c = -1, rabbit. For `book` and `ring3` the box is 3.5 wide and the
c = 0 pictures show the face of the box because the box is full.
