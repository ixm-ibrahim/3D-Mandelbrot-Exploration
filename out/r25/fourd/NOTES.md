# Round 25, section `fourd`: do it in 4D and come down otherwise than by a flat cut

Verdict first: **nothing from this corner passes.** Two new 4D constructions were built and drawn from two eyes, with
seven ways down between them. Each fails, and for each the reason is exact and written below. Door (iv) of the
briefing is, as far as natural 4D squares go, closed (section 4).

Every statement is marked MEASURED (a number in a log here), SEEN (I looked at the picture named), REASONED, or
THEOREM (a short proof is given or it is a textbook fact).

Files: `four.py` (everything), `best.py` (`rule()`), `twist.py`, `dbg.py`, `stitch.py`;
logs `algebra.log`, `flat.log`, `twist.log`, `best.log`;
pictures `sheet.png` (front eye), `sheet-top.png` (eye from above), `cuts-spinor.png`, `cuts-product.png`.

## 1. The spinor rule (a new 4D rule; not the plain quaternion rule)

The idea, which is the user's own ("quaternions, so that the limits of 3D rotations do not show"): turns in space
cannot be doubled in a consistent way, but quaternions can be squared. So let every point of space be the shadow of
a quaternion, square the quaternion, and add c in space.

- A point v of space is the shadow of a quaternion q:  v = q i q*  (the Hopf map; |v| = |q|^2). Space is
  x i + y j + z k, the flat plane is (i, j). Above every point there is a whole circle of quaternions, q e^(i t):
  they differ by a twist of the frame about the point.
- The rule:  **q -> sqrt(1 + c w^-1) q^2,  w = q^2 i (q^2)*.**  The shadow moves by v -> w + c. The left factor is
  the one way of moving the quaternion along the straight line from w to w + c that adds no twist (the horizontal
  lift). Nothing is chosen.
- MEASURED (`algebra.log`): the shadow of the new quaternion is w + c to 8e-14; the move has no part along the circle
  (8e-10); a flat quaternion a + d k stays flat and its square is s^4 + c, i.e. the flat rule z -> z^2 + c.

Ways down (which quaternion does a 3D point start with?) and what each gives:

| way down | flat check | c = -1 | rabbit |
|---|---|---|---|
| least-turn quaternion (3-plane 1, j, k) | 0 / 0 / 0 / 0 differ, MEASURED `flat.log` | the Lathe: 0 of 200,000 verdicts differ (MEASURED `algebra.log`); rings (SEEN `sheet.png` row 2) | nothing off the flat plane: 0 inside of 200,000 box points, the Lathe has 9,097 (MEASURED); empty (SEEN) |
| quaternion in the 3-plane (1, i, k) | exact on paper; in numbers the rabbit loses 1,340 of 20,000 because a rounding error of 1e-16 in the twist explodes (MEASURED) | one shell-shaped lump with swirl grooves, a full disc of radius 1.62 in the upright plane (SEEN `sheet.png` row 3, `cuts-spinor.png`) | nothing (SEEN) |
| ANY quaternion above the point stays | not exact: 12,716 of 20,000 flat points are extra for c = -1, 9,727 for c = -0.75, 452 Siegel, 0 rabbit (MEASURED) | a plain ball of radius 1.62 (SEEN `sheet.png` row 4) | the flat picture and nothing else, plus a thin shell round the centre (points whose orbit runs exactly through the centre) (SEEN) |
| EVERY quaternion above the point stays | not exact: 144 flat points missing for c = -1, ALL inside points missing for the rabbit (2,789) and the Siegel disc (3,831) (MEASURED) | the Lathe's rings without the small top and bottom buds (SEEN in cuts only) | empty (SEEN in cuts only) |

**Exactly why it fails (the twist law).**
- THEOREM (worked by hand, then MEASURED to 2e-9 on 94,934 points, `twist.log`): if the quaternion above a point
  v = (x, y, z) is twisted by a small angle t away from the least-turn one, then after one squaring it is twisted by
  **t (1 + |v| / x)**. Adding c keeps twist differences (the left factor depends on the shadow only; MEASURED 3e-14).
  Derivation: q = A + B j with A = cos(f/2) e^(i t/2), f the angle from the x-axis; q^2 has A' = A^2 - |B|^2.
- So the fourth direction of this rule is a twist, and the square multiplies it by 2 on the positive x-axis, by
  something huge where x is near 0, and by 0 on the negative x-axis.
- MEASURED (`twist.log`), growth of a small twist per step along flat orbits inside the picture: c = -1: wiped out
  (the body at -1 sits on the negative x-axis); c = -0.75: wiped out; rabbit: times 3.75 per step on 100 % of
  orbits; c = 0.25i: times 3.72; c = -0.12 + 0.6i: times 1.02. On the rule itself, flat inside points started with
  a twist of 1e-9: share that still stays after 60 steps: c = -1 1.000, c = -0.75 1.000, **rabbit 0.000**, Siegel
  0.447.
- What that means for the pictures (REASONED from the two lines above, and it is what is SEEN): where the twist is
  wiped out, every twisted start falls onto a flat orbit, so a whole ball round the picture is swallowed (lump or
  ball); where the twist grows, nothing off the flat picture survives and the flat picture itself is a knife edge.
  Bulbs would need the twist to behave like a second angle that doubles; it does not, it only dies or explodes.
- For real c the rule is unchanged by spinning space about the x-axis, so "any" and "every" are bodies of
  revolution: rings or a ball (REASONED; SEEN).
- One more defect (REASONED, SEEN as the dotted circles in `cuts-spinor.png`): when the straight move from w to
  w + c runs through the centre, the quaternion shrinks to nothing and its twist is lost. That happens for w on the
  segment from the centre to -c, which starts at the centre and so always cuts through the middle body.

In the user's words (six lines):
1. Each point carries a quaternion; the quaternion is squared and c is added in space.
2. The flat picture comes out exact when points start with the plainest quaternion.
3. For c = -1 that start gives the flat picture spun round the x-axis: rings.
4. Other starts for c = -1 give one big lump or a plain ball.
5. For the rabbit nothing at all survives off the flat picture.
6. Fails tests 3 and 4 (rings, lumps, or no body at all); with "any" or "every" start it also fails test 1.

## 2. The product of two flat pictures, with three ways down that are not flat cuts

THEOREM (standard): the commutative 4D square (m, d) -> (m^2 + d^2 + c, 2 m d) is two flat rules side by side:
u1 = m + d and u2 = m - d each follow u -> u^2 + c. A 4D point is a PAIR of flat points; it stays when both stay.
(The known `hyper` rule is the flat cut "d along one fixed direction": two flat pictures slid apart.)

THEOREM (two lines): in this 4D set the plane m = 0 holds a second exact copy of the flat picture **for every c, the
rabbit included**: (0, d) -> (d^2 + c, 0), so the pair (d, -d) lands on the flat plane after one step, and the flat
picture is its own pre-image. This does not contradict (W-b): the two planes share only the centre POINT, and two
planes of a 3D space always share a line. (It is a copy as a set; that plane is not kept by the rule, it is sent
into the flat plane.) This is the precise reason the rabbit's second copy exists in 4D and cannot be shown in 3D.

A 3D point (m, t) = (a flat point m, a height t) stands for pairs with middle m and half length t. Ways down:

| way down | flat check | what it gives |
|---|---|---|
| ANY pair with this middle and half length stays | exact, 0 extra / 0 missing of 20,000 in all four sets (MEASURED `flat.log`) | one faceted heap for c = -1 and for the rabbit (SEEN `sheet.png` row 6, `sheet-top.png`); the upright cut for c = -1 is a full diamond of half width 1.62 (SEEN `cuts-product.png`) |
| EVERY such pair stays (= the whole circle of radius t round m is inside) | exact (MEASURED) | every flat body becomes a pointed tent; bodies stay separate, the rabbit works, nothing new off the flat picture (SEEN `sheet.png` row 7) |
| the ONE pair that lies square to the line from the centre (**cone cut**) | exact (MEASURED; as a rule of the library: 0 / 0 / 0 / 0, `best.log`) | see below |

**The cone cut** (the nearest thing found; `best.py`). In ball coordinates (distance r, longitude L, latitude D):

    a 3D point is inside  iff  r e^(i(L + D))  and  r e^(i(L - D))  are both inside the flat picture.

It is the cut of the 4D product by the cone |u1| = |u2| (the cone over the Clifford torus), on which the product
square for c = 0 is perfectly even: (r, a, b) -> (r^2, 2a, 2b), no stretch, no special point (THEOREM: the cone's
own metric 2 dr^2 + r^2 (da^2 + db^2) is multiplied by 4 r^2). Nothing is chosen, c may be anything.

- SEEN (`sheet-top.png` row 5, c = -1): the centre body is round and has small knobs all over it, which nobody put
  there. Also SEEN: the side bodies are ridged, two long thin blades stick out along the upright axis, and the rabbit
  (`sheet.png`, `sheet-top.png` row 5) is a ridged slab with shards and holes. It is not a blown-up shape.
- THEOREM: for real c the upright plane through the x-axis holds a true copy of the flat picture ((x, z) is in iff
  x + iz and x - iz are in), and the upright plane through the y-axis holds the flat picture standing on end. SEEN in
  `cuts-product.png` row 3.
- Exactly why it is ridged (REASONED; each point checked against the pictures):
  1. A body away from the centre is the overlap of two copies of the flat body, each swept through space along its
     own family of curves (curves L + D = constant and L - D = constant; on a sphere these are Viviani curves). Two
     crossing tubes overlap in a body with four ridges: a small flat disc of radius p becomes
     |y| + |z| <= sqrt(p^2 - x^2), a diamond in every cross cut. Only the body at the centre comes out round.
  2. Every PAIR of flat buds at the same distance from the centre makes a piece, at the middle of their longitudes
     and at a latitude of half their difference. N buds make N x N pieces: the knobs, and the crust of ridges.
  3. Straight above the centre the pair is (u, -u), and which one depends on the side one comes from: blades.
  4. In 4D the bodies of the product are "disc times disc", which has an edge; a 4D ball has none. Any 3D view of
     the product shows that edge except at the centre.
- REASONED: the cone-fold rule of round 24 is this construction with the cone forced again after every step
  (lumps); the cone cut is the same idea with c added properly in 4D (no lumps, but ridges). Same family, both fail.

In the user's words (six lines):
1. Take two copies of the flat picture in 4D and look only at pairs of points equally far from the centre.
2. The flat picture is exact for every c, and no dial is used.
3. The centre body is round, and small knobs appear all over it by themselves.
4. Every other body has four ridges instead of being round.
5. Two blades stick out above and below the centre; the rabbit is a rough slab.
6. Fails test 3 (ridges, blades: shards) and test 4 (not round bodies). Passes tests 1 and 2.

## 3. Is there any other natural square in 4D? (short)

- REASONED, leaning on Hurwitz's theorem and on Yiu's classification of quadratic maps between spheres (1986),
  which I did not re-derive: a quadratic 4D map that squares lengths is, up to turns, either (a) the quaternion
  square followed by a 4D turn, or (b) the Hopf kind q a q*, which lands in a 3D sheet at once.
  (a) If the flat plane is to be exact the turn can only turn the hidden plane. MEASURED: 0 of 200,000 verdicts
  differ from the plain quaternion square (turns 0.7 and 2.0 per step, `algebra.log`); THEOREM why: the visible part
  depends on the hidden part only through its length.
  (b) With the flat plane exact this is exactly the lab's "Quaternion square, twisted" (round 12), a one-dial family:
  (zeta, z) -> (zeta^2 - z^2 e^(-2ia), 2 z Re(zeta e^(ia))). Known; not rebuilt. Note for `vahlen`: the list of
  quadratic maps that are z^2 on the flat plane and square lengths is this one-dial family (and its mirror), not a
  finite list.
- REASONED: the other 4D number systems that contain the flat rule are the product above (two kinds, slid along x or
  along y), the split quaternions (in the hidden direction a product of two one-line rules: diamonds) and the dual
  numbers (the hidden part is the orbit's derivative: prisms). None was drawn here beyond the product.
- REASONED (not measured): a quadratic 4D rule on pairs of complex numbers (a, b) that sends every Hopf circle to a
  Hopf circle (G(u q) = u^2 G(q) for unit u) can only be built from a^2, a b, b^2, so through the Hopf map it comes
  down to a 3D rule whose map of directions is a rational map of the sphere, w = a / b. Doubling the angle on the
  flat circle |w| = 1 then forces w -> w^2 everywhere (identity theorem). That is the one-plane rule's map of
  directions (longitude doubled, Mercator latitude doubled): in 4D, one plane is (a, b) -> (a^2, b^2) with c added
  in space (the lengths differ from the lab's by a factor between 1 and 2). So this road gives nothing new either.

## 4. What this says about section 3 of the briefing

- I found nothing wrong in (W-a) to (W-f). (W-b) should be read as a statement about 3D: in 4D a second true copy
  exists for every c (section 2), sharing one point with the first.
- Door (iv), "4D with a better way down": for the natural 4D squares it is closed, for two different reasons.
  REASONED: (1) quaternion-built rules have, for real c, the spin about the x-axis as a symmetry, so every way down
  that does not itself pick a direction gives a body of revolution, and a way down that picks one (a fixed start
  quaternion) gives a lump or nothing because of the twist law; (2) the product has no such symmetry and is exact
  for every c, but its bodies are "disc times disc" and no view of them is round away from the centre.
- Not examined: 4D maps that are not quadratic (for instance the even-spacing "pillow" family one dimension up). I
  see no reason for it to beat its 3D version, but I did not build it.
- The spinor rule is also the cleanest form of "carry a frame along the orbit, turned by the turns the point makes"
  (door (i)): the twist law (factor 1 + |v| / x per step) is the reason a carried frame with no extra choice cannot
  work, and `fromc` or the judge may want to quote it.

## 5. What should be tried next from this corner

Nothing more with 4D squares. If anything: the only thing here that made bulbs "all over by themselves" is the
PAIR structure of the product (a piece for every pair of flat buds). Its pieces are ridged because "both ends
inside" is a hard corner. A round version needs each body's own centre (its inner rings), and then pairs from two
different bodies have no place to go. I do not see a way round that.
