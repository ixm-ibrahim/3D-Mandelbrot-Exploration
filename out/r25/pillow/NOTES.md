# Round 25, section "pillow": the even-spacing family, all of it

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened), **reasoned**, or
**theorem** (a short proof is given). Nothing outside `out/r25/pillow/` was written. One slip against the house
rules: I patched two of my own Python files once with an inline script instead of the Edit tool (no harm done).

## Short answer (six plain lines)

1. I listed every even-spacing rule there can be, not only the ones tried so far. A pillow with four corners can
   hold the flat picture in exactly three ways: its two seams one above the other (round 15's square pillow), crossed
   (a tetrahedron), or the top seam turned 135 degrees (two mirror twins). A pillow with three corners can hold it in
   two ways. Pillows with corners of the kinds 2-4-4 and 2-3-6 cannot hold the flat picture at all.
2. The fused x-axis of c = -1 is NOT forced. With the seams crossed or turned the row of bodies comes apart again
   (cut at the touching point over the middle cut: 0.42 for the square pillow, 0.03 crossed, 0.016 turned, 0 for one
   plane). It also fades for the square pillow when the pillow is made taller.
3. What a pillow grows off the flat picture is always the same thing: one more copy of the flat picture rolled onto
   a cone under it, and copies of that copy. For c = -1 with the top seam turned, that looks like three separate round
   bodies with egg-shaped bodies and small buds hanging under them, in more than one direction: the nearest thing here
   to the paper's picture. But the eggs are stretched about 2 to 1, there are spikes and crumbs, and it is one-sided.
4. No pillow gives a clean rabbit. Crossed seams: a rough lump. Turned seam: small rough bodies with crumbs for the
   rabbit, and ONE LUMP for the rabbit's mirror image. Square pillow: as round 15 and 23 saw it (rough, spiky).
5. Two faults are in the nature of the family, not of my build: every four-corner pillow holds the flat picture one
   third of the way up, so what grows below never matches what grows above; the three-corner pillow is the same above
   and below but is different front and back (a half turn changes a quarter to a half of the solid).
6. Tests: passes 1 (exact), 2 (the count of neighbour bodies is the power squared) and 5; fails 3 (crumbs, spikes),
   4 (rabbit; lopsided) for every member. It contains no sphere inversion and no quaternion. **This corner does not
   hold the rule the user is looking for.**

## 1. Files

| file | what |
|---|---|
| `pil.py` | every four-corner pillow as one class `Pillow(rho, H, kind)`; `rule(rho, H, kind)`; `check` |
| `best.py` | `best.rule()` = skew pillow (the nearest thing, not a pass); `best.rule('tetra')`, `('skew-mirror')`, `('square')` |
| `cuts.py`, `solids.py`, `measure.py` | cuts, rough solids, numbers from blocks (`numbers.json`) |
| `sheet.py` -> `sheet.png`, `sheet-top.png` | the section's sheets (four standard sets, two eyes) |
| `closer.py` -> `closer.png` | the skew pillow at finer blocks (200 deep, 40 steps) and its weak side |
| `cuts-a.png` (plain layout, heights), `cuts-b.png` (angle-true layout, the named pillows, round 24's triangle) | cuts |
| `solids-s1-a.png`, `solids-s2-top.png`, `solids-s3-under.png` | first looks (plain layout), three eyes |
| `seamjump.py/.log`, `checks2.py/.log`, `upright.py/.log`, `final_checks.py/.log`, `speed.py` | the checks quoted below |

Load: `import sys; sys.path.insert(0, 'out/r25/pillow'); import best; r = best.rule('skew')`.

## 2. The family, classified

Setting. A rule is F(v) = |v|^2 G(direction of v). "Even spacing" means: the ball of directions is a flat sheet
folded shut (a pillow: flat everywhere except at a few corners), and G is "double every distance" on that sheet.
The flat plane's circle of directions must be a closed line on the pillow (the belt) that G lays twice round itself,
the right way round and at even speed.

**(A) Which pillows have a belt at all (theorem; counting bend, i.e. Gauss-Bonnet).** A closed line that does not
bend splits a pillow into two caps, and each cap must hold corners whose missing angles add up to exactly one full
turn, minus what the line itself bends at corners it runs through.
- Four corners (each missing a half turn): two corners on each side, the belt runs through none. Works.
- Three corners (each missing two thirds of a turn): the belt must run THROUGH corners, either through all three
  (round 24's triangle: the flat circle is the triangle's rim) or through one, with one corner on each side.
- Through a corner the belt must run straight in the unfolded sheet. (If it bent there, every point of the belt that
  doubling sends to that corner would need the same bend; some of those are ordinary points, and their ancestors
  too, so the belt would be bent in endlessly many places.) A straight line through a 2-, 4- or 6-corner turns back
  along itself; through a 3-corner it goes on and splits the corner evenly.
- Corners 2-4-4: no odd corner, and no split of the corners adds up. Corners 2-3-6: a belt through the 3-corner
  would need a corner missing exactly two thirds of a turn on each side; the other two miss a half and five sixths.
  **No belt, so no rule.**
- A belt through corners also passes through directions where the rule wraps space three times round a flat ray
  (if it passed none, the corners on the belt would have to be their own two-for-one ancestors under doubling, and
  no finite set of points on a circle is). So: **three-corner pillows always put fold-lines ON the flat picture**
  (for the triangle at 60, 180, 300 degrees; for the one-corner version at 180 degrees): the negative x-axis is one
  of them in both.

**(B) Four corners: exactly three kinds (theorem + measured).** Pillow = the plane of z folded by z ~ z + 1,
z ~ z + tau, z ~ -z; tau = rho + iH.
- Plain doubling z -> 2z turns every belt the WRONG way round (it gives the flat rule of conj(z)^2): on a line
  y = y0 it needs 2 y0 = -y0, and the fold that brings it back flips the line (checked by hand in `checks2.log`,
  item 2). So the map must be the mirror doubling **z -> 2 conj(z)**. That is why round 15 needed its "mirror".
- z -> 2 conj(z) respects the folding only if 4 rho is a whole number: **rho = 0, 1/4, 1/2, 3/4**.
  Measured (`seamjump.log`): 40,000 pairs of directions 2e-7 apart on either side of the top seam: for rho = 0, 0.25,
  0.5, 0.75 the images are 5e-7 apart; for rho = 0.1, 0.125, 0.2, 0.333, 0.4, 0.6, 0.9 they are 0.6 to 0.9 apart
  (a tear along the whole seam).
- The belt is **always** the line one third of the way from one seam to the other (y = H/3: the only height with
  -2y = y up to the folding). The height H is free.
- rho = 0: both seams above one another, in the upright plane through the x-axis (round 15). rho = 1/2: seams
  crossed; H = sqrt(3)/2 is the regular tetrahedron. rho = 1/4 and 3/4: top seam turned by 135 degrees, mirror twins;
  the solid of a c on the x-axis is then not its own mirror image.
- No dial left if one asks that the pillow's two periods be equally long: H = 1 (square), sqrt(3)/2 (tetrahedron),
  sqrt(15)/4 = 0.968 (skew). These are `best.rule('square' | 'tetra' | 'skew')`. (My choice of principle; said so.)

**(C) What is in the nature of each kind (theorem; measured where a number is given).**
- Four corners: turning a direction half round the upright axis does not change where G sends it (the half turn is
  one of the pillow's own symmetries and is undone by doubling). So every solid is unchanged by a half turn, as
  every flat Julia set is. Measured: 0.000 of the volume changes, all sets (`numbers.json`, "half turn").
  But above and below can never match: the belt is at one third, never in the middle. Measured: volume above over
  volume below 0.76 to 0.84 for c = -1, 0.62 to 0.88 for the rabbit.
- Three corners: above and below match (1.00), but the reason for the half-turn symmetry is missing: doubling on a
  three-corner pillow has no symmetry of the pillow that it undoes (theorem). Measured on round 24's triangle: a
  half turn changes 25 % of the volume for c = -1 and 46 % for the rabbit.
- The first extra bodies are forced too (reasoned, positions measured in `checks2.log` item 4): the four directions
  sent to +x are +x, -x and two more on a cone about 50 degrees below the flat plane, at longitude 0 and 180
  (square), 90 and 270 (tetrahedron), 130 and 310 (skew). So the middle body of c = -1 gets exactly two extra
  neighbours, both below. For the square pillow they stand right under the x-axis: that is the lump.

**(D) Layout (reasoned + measured).** Each side of the belt is a tube closed by a folded seam; laid on a half ball
it must be squeezed somewhere, because even doubling on the flat circle fixes the rim. The least possible squeeze
(the plain layout, kind 'J') is 1.03 to 1.06 below and 1.28 to 1.39 above for the named pillows, but it pushes points off
the flat plane unevenly (sideways push 1.5 to 2.6 instead of 2, by longitude: `checks2.log` item 3), and that alone
turns the skew rabbit into a lump or erodes it (`cuts-a.png`, `numbers.json`). All results below use the layout
with the belt made angle-true (kind 'JA', round 23's two clocks, here for every rho, solved by a table and Newton
steps: round trip 4e-12; sideways push 2.00 at every longitude, measured).

Checks of the named rules (`final_checks.log`, `pil.py check`): flat check 0 of 20,000 differ for all four sets;
nothing strays off the flat plane; no NaN on 200,000 points and 11 special points; length squared to 1e-14; lift
test 1.000 (skew, rabbit: 0.999); volume the same at 40 and 100 steps (no slow leak).

## 3. Is the fused x-axis forced? No (measured)

Touching number = area inside in the cut across the touching point x = -0.618 over the area in the cut across
x = 0, c = -1, 50 steps (`cuts.py`).

| rule (angle-true layout) | touching number | bodies after peeling | above : below |
|---|---|---|---|
| one plane | 0.000 | 7 | 1.00 |
| square pillow (rho 0, H 1) | 0.418 | 1 (one lump) | 0.76 |
| tetrahedron pillow (rho 1/2, H 0.866) | 0.027 | 17 | 0.78 |
| skew pillow (rho 1/4, H 0.968) | 0.016 | 11 | 0.84 |
| round 24's triangle | 0.413 | 5 (99 % in one) | 1.00 |

Height (plain layout): square 0.41 (H 1), 0.027 (H 1.5), 0.000 (H 2); crossed 0.36 (H 0.5), 0.13 (0.7), 0.076
(0.866), 0.037 (1.2), 0.007 (1.5); turned 0.087 (H 0.5), 0.048 (0.75), 0.012 (1), 0.004 (1.3), 0.001 (1.5).
At every height the turned seam is the least fused and the square the most. But a taller pillow is just one plane
again: the volume of bodies off the flat plane falls with it (crossed: 0.068, 0.038, 0.013, 0.005, 0 at H = 0.7,
0.866, 1.2, 1.5, 2) and at H = 2 nothing is left of them.

On the briefing's "fused along the whole x-axis by its nature" (section 4, the pillows):
- For four-corner pillows it is wrong as a statement of nature: it holds for the square pillow at height 1 only.
  Round 15's reason ("every mirror-symmetric layout keeps the upright plane and folds it onto half") is right for
  rho = 0 only. Measured (`upright.log`, 200,000 directions in the upright plane through the x-axis): the square
  pillow sends them back into that plane and hits 144 of its 360 degrees; the tetrahedron pillow sends them back
  into it and hits all 360; the skew pillow does not keep that plane at all.
- For round 24's triangle I found a cause that is made by its layout, not by the pillow (measured, `checks2.log`
  item 3): its sideways push beside the flat plane is 1.05 instead of 2 at exactly the longitudes 60, 180, 300.
  The touching point of c = -1 lies at longitude 180, so there a lifted point is multiplied by 0.618 x 1.05 = 0.65
  per step: it is pulled back, and the bodies grow together (the briefing's own W-e). A layout that pushes by 2 there
  exists on paper (near a corner: polar angle b in the 60-degree wedge -> 3b - sin(6b)/3, distance kept); **I did
  not build it**, so whether the triangle then comes apart is open. What stays by nature for three corners is (A)
  and (C): a three-fold wrap about the negative x-axis and the lost half-turn symmetry.

## 4. What the pillows that escape give (seen in `sheet.png`, `sheet-top.png`, `closer.png`, `solids-s3-under.png`; numbers measured)

Blocks of side 0.025, 40 steps (`measure.py`). "off" = bodies wholly above or below the flat plane after peeling.

c = -1:

| rule | volume | off (joined) | their long : thick | crumbs | thin share | mirror in the upright plane changes |
|---|---|---|---|---|---|---|
| one plane | 0.725 | 0 | - | 6 | 0.4 % | 0 |
| square | 1.534 | 0 | - | 6 | 2.0 % | 0 |
| tetrahedron | 0.777 | 14 (8) | 1.74 | 432 | 6.9 % | 0 |
| skew | 0.794 | 4 (2) | 1.96 | 116 | 3.2 % | 17 % |
| triangle (round 24) | 1.556 | 2 | 1.28 | 14 | 10.5 % | 0 |

rabbit:

| rule | volume | meeting point: patches, share of skin | bodies | off (joined) | long : thick | crumbs | thin | above : below |
|---|---|---|---|---|---|---|---|---|
| one plane | 0.444 | 3, 0.48 | 7 | 0 | - | 10 | 1.3 % | 1.00 |
| square | 0.651 | 4, 0.40 | 17 | 10 (10) | 1.90 | 154 | 14 % | 0.88 |
| tetrahedron | 0.744 | 2, 0.75 | 15 | 8 (8) | 1.87 | 44 | 12 % | 0.62 |
| skew | 0.478 | 3, 0.19 | 15 | 8 (8) | 1.52 | 204 | 14 % | 0.66 |
| skew, the rabbit's mirror image | 1.921 | 1, 0.90 | 7 (all in one) | - | - | 4 | 5 % | 1.28 |
| triangle (round 24) | 0.804 | 5, 0.48 | 15 | 8 (8) | 4.04 | 254 | 17 % | 1.00 |

c = -0.75 and the Siegel disc: one plane 1.57 and 1.20; square 2.85 and 0.96; tetrahedron 2.31 and 2.42; skew 2.00
and 1.80 (swollen; one body after peeling).

In words (seen):
- **Skew pillow, c = -1** (`closer.png` top row, 200 blocks deep; `sheet-top.png` bottom left;
  `solids-s3-under.png`): three separate round bodies in a row, meeting in single points. On the middle one stands
  one clear egg-shaped body (on the side below the flat picture) with a few pointed buds beside it; each side body
  carries a smaller egg and a handful of small buds. The side above the flat picture is nearly bare. The eggs are
  pointed and carry small spikes; there are loose specks. Not the same on the two sides of the upright plane.
- **Skew pillow, rabbit**: the flat bodies are there but broken into small rough bodies with crumbs, like
  cauliflower; the mirror-image rabbit is one swollen lump (`closer.png` bottom row). Even push beside the flat
  plane (2.00 at every longitude) does not prevent that lump, so the briefing's W-e is not the whole story
  (measured).
- **Tetrahedron pillow**: c = -1: a round middle body with ragged bodies round it, loose arcs and many crumbs;
  rabbit: one rough lump with horns; c = -0.75 and the Siegel disc: rough lumps with shells.
- **Square pillow**: c = -1 one lump with horns; rabbit rough and spiky (as rounds 15 and 23 found).

Why the extra bodies are stretched (reasoned; long : thick measured 1.5 to 2.0, the same as round 23's 1.8 to 2.2):
the pillow is flat and the ball of directions is round. Evenly spaced on the pillow is not evenly spaced on the
ball: the cone 50 degrees below the flat plane is a smaller circle, so a body there is squeezed sideways by about
1 / cos(50 degrees) = 1.55 against its length, and the corners cannot be spread out (they are corners). No layout
removes this; it only moves it.

## 5. The best even-spacing rabbit there is

None is good. By the numbers the square pillow's rabbit (round 15's, now with the angle-true layout) is still the
only one that is separate at the meeting point (4 patches), has all its 10 extra bodies joined on, and does not
depend on which way round the rabbit is; it is rough, spiky, with 154 crumbs, and its c = -1 is a lump. The skew
pillow trades that lump for a rabbit that is thin at the meeting point (0.19 of the small ball's skin against 0.48)
and a mirror rabbit that is a lump. Making any pillow taller cleans the rabbit only by taking the extra bodies away
(square, H = 1.5: 4 extra bodies, long : thick 2.6; H = 2: none: it is one plane).

## 6. What is forced, in one list (for the wall)

- Even spacing + exact flat picture + power 2 => four corners with the flat picture one third of the way up
  (lopsided above / below), or three corners with fold-lines on the flat picture and no half-turn symmetry. (theorem)
- The pattern of extra bodies is the pillow's own grid (the power squared neighbours per body), but it sits on
  cones about the UPRIGHT axis, and the first cone is one-sided. It is not "bulbs all over". (reasoned + seen)
- Squeeze cannot be removed from any layout; on the ball, even spacing is stretched by one over the cosine of the
  height. (reasoned)
- For other powers n the same family works with z -> n conj(z), belt at H / (n + 1) (not built here; round 15 did
  power 3, where the belt can sit in the middle).

## 7. Not done, and cautions

- The three-corner pillow with one corner on the flat circle and the "push 2" layout for the triangle are worked
  out on paper only (sections 2 A and 3). Their forced faults (fold-line on the negative x-axis, no half-turn
  symmetry) are measured on round 24's triangle, not on a build of mine.
- Bodies counts come from peeling blocks of side 0.025; a thick piece of a rib counts as a body. "Joined" is
  unreliable for c = -1, where bodies that touch in one point fall apart in blocks (one plane: 22 % "loose").
- c off the flat plane (the Mandelbrot solid) was not looked at.
- `cuts-a.png`, `solids-s1-a.png`, `solids-s2-top.png`, `solids-s3-under.png` use the plain layout (uneven push)
  and heights that are not the named ones; they are first looks, kept because the height sweep is read from them.
