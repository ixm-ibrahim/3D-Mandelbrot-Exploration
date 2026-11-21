# Round 25, section "inverse": the 3D object built backwards, from roots

Every statement is marked **measured** (a number from a script here), **seen** (I looked at the picture named),
**reasoned** or **theorem**. Nothing in this folder passes the user's tests. This is a "does not work, and this is
exactly why" report.

## Six plain lines

1. Applying roots to dots over and over gives a whole surface only if the roots shrink every direction. The
   one-plane roots do not: they pull every dot down onto the flat plane, and what is left is only the flat outline.
2. The quaternion roots leave one direction alone, and what is left is the flat outline spun round the x-axis:
   rings for c = -1, taffy for the rabbit.
3. Both root sets together (four roots) give either the ring-and-taffy lump again, or the plain one-plane bodies,
   depending on how "inside" is read. Nothing new grows.
4. There is a set of four roots that shrinks every direction alike and keeps the flat picture exact with no special
   point on it (the "zip"). For c near 0 it does what was hoped: the roots alone grow a closed bumpy ball.
5. For c = -1 and the rabbit the zip fails: on the square pillow the extra bodies are as big as the flat ones and
   run into them (one lump, a ragged mass for the rabbit); on a taller pillow the bodies come apart but the extra
   ones are thin needles, and they sit in different places above and below.
6. So this corner gives no rule that is inflated, has bulbs all over by themselves and is not stretched. Fails:
   test 3 (lump, needles), test 4 (no round small bodies off the flat picture), lopsided, and it has one dial.

## 1. What "backwards" means in 3D

The flat Julia set is what is left when the two roots +-sqrt(z - c) are applied to dots over and over. In 3D that
sentence splits in two, and the briefing's wording hides it:

- **Roots applied to dots** give what the roots cannot shrink away. For the one-plane rule that is the flat outline
  and nothing else. **Measured** (`clouds.log`): share of cloud dots further than 0.01 from the flat plane is 0.000
  for c = -1, the rabbit and c = -0.3. **Seen** (`clouds-a.png`, row 1): three thin flat curves.
  **Reasoned**: a one-plane root halves the height of a direction above the flat plane (in the map-maker's measure),
  so every chain of roots ends on the flat plane.
- **The skin of a blown-up body** is what is left when the roots are applied to a big ball (or to its outside)
  over and over. That is the same thing as "the orbit stays", so for one rule nothing is gained by going backwards.
  **Reasoned**.

So going backwards can only give something new in two ways: (a) more roots per point than one rule has (a rule
with several squares per point), or (b) roots that shrink every direction, so that dots alone already fill a
surface. Both were built.

## 2. Root sets tried

| root set | what is left from dots | solid | verdict |
|---|---|---|---|
| the 2 one-plane roots | the flat outline only | the one-plane bodies | baseline; nothing off the flat picture |
| the 2 quaternion roots | the flat outline spun round the x-axis | rings / taffy | known (the Lathe) |
| all 4 of these | the spun surface plus dust falling to the flat plane | "some choice stays": rings and a taffy lump; "every choice stays": the one-plane look | nothing new |
| the 4 zip roots, square pillow (b = 1) | dots all over the solid (98 % of them off the flat plane) | c = -1 one lump of fused bodies; rabbit a ragged mass with holes | fails 3, 4; lopsided |
| the 4 zip roots, taller pillow (b = 1.5, 2) | the same | b = 2: bodies apart, thin needles, placed differently above and below | fails 3, 4; lopsided; a dial |
| zip and its mirror image, 8 roots | - | b = 1.5, seen from one eye only: "some" a hairy lump, "every" the one-plane look. b = 1 "every", measured only: half the one-plane size | nothing new |

Pictures: `sheet.png` (front eye), `sheet-top.png` (second eye), `clouds-a.png`, `clouds-top.png`, `cuts.png`
(readable halves: `cuts-c1.png`, `cuts-rabbit.png`), `look2-a.png` (the 8-root rows, front eye only).

## 3. A rule with several squares per point ("some" and "every")

Two readings of "inside" for a rule with squares F1, F2 at every point: **some** = a point is inside when at every
step some choice of square keeps it (all the roots of both rules applied to a big ball); **every** = inside when
every chain of choices keeps it (all the roots applied to the outside of a big ball; the rest is the solid).
Worked out on a grid of blocks (`roots.grid_K`), because the number of chains doubles at every step.

- **Theorem** (two lines): if every square in the family is z^2 on the flat plane and keeps the flat plane, then
  every chain of choices from a flat point is the flat orbit, so both solids cut the flat plane exactly in the flat
  picture. **Measured** to the grid's own error (`measure.log`): the flat cut of every grid solid differs from the
  flat picture on 0.6 to 0.9 % of test points for c = -1 and 1.5 to 2.2 % for the rabbit, the same as the one-plane
  rule measured the same way (0.71 %, 1.54 %), whose exactness is known.
- One-plane and quaternion squares together. **Seen** (`sheet.png`, `sheet-top.png`, rows 2 and 3): "some" is the
  ring solid for c = -1 and one taffy lump for the rabbit; "every" looks like the one-plane solid. **Measured**:
  size against the one-plane solid 1.41 and 5.99 ("some"), 0.84 and 0.88 ("every"), for c = -1 and the rabbit.
- **Reasoned**: "some" always contains the solid of each rule alone, so it inherits every lump and every ring;
  "every" is contained in each, so it keeps only what all rules agree on, and all exact rules agree only next to
  the flat picture. A family of exact rules can therefore never add a bulb off the flat picture under "every", and
  never remove a lump under "some". This closes "more roots per point" as a way round the wall.

## 4. The zip: the four roots that shrink every direction alike

**Where it comes from (reasoned).** Roots that shrink every direction alike and by the same amount are the roots
of an even doubling on a flat pillow (that is the wall's W-d). The flat circle must be a closed straight line of
the pillow that the doubling sends to itself, twice round, forwards, without a fold. Three facts:

- A closed straight line that avoids the corners must have corners worth half the total on each side. Only the
  four-corner pillow can do that (two corners each side). On the three-corner pillows there is no such line at
  all. **Theorem** (Gauss-Bonnet).
- On the four-corner pillow the doubling u -> 2u sends the line at offset a to the line at 2a. It comes back to
  itself only for a = 0 (the seam through the corners: folded, this is the pillow already in the lab) and for
  a = one third of the way across. **Theorem** (one line of arithmetic).
- On the one-third line u -> 2u runs the circle backwards (it would give the flat picture of conj(z)^2). The
  mirrored doubling u -> 2 conj(u) runs it forwards: t -> 2t exactly. **Theorem**. Its price: the line splits the
  pillow 2 : 1, so the upper and lower halves of the directions cannot be alike. For power 2 the lopsidedness is
  forced. (For power 3 the line at one quarter works with u -> 3 conj(u) and splits the pillow evenly. Not built.)

**The rule** (`roots.Zip`, `best.rule(b)`). Pillow = a tube, t = longitude / 360, s = 0 .. b/2 across, both ends
pressed flat and zipped shut. Square: (t, s) -> (-2t, 2s) for s < b/4, (2t, b - 2s) otherwise; length -> length
squared. Flat circle = the line s = b/3; wide band = upper half of the directions. Layout: band -> ring -> disc by
zeta = V + chi r0^2 / V (chi = 0 at the flat circle, 1 at the zip) -> half sphere. b is the pillow's height over
its girth: **a dial I had to pick**; b -> infinity is the one-plane rule (mirrored), b = 1 the square pillow.

**Checks, measured** (`python out/r25/inverse/roots.py check`):
- flat check 0 differing verdicts of 20000 for the Mandelbrot set, c = -1, the rabbit and the Siegel disc; b = 1
  and 1.5 both ways up, b = 2 one way up (`best.py`). (Points exactly on the flat plane are computed as plain z^2; the rule is continuous there:
  the push off the flat plane is 0.9997 to 1.0003 of the one-plane push at every longitude, on both sides.)
- the square of each of the four roots gives the point back: worst error 6e-9. All values finite.
- at c = 0 the roots applied to dots fill all 648 equal patches of the unit sphere (one-plane roots: 72, the belt).
- squeeze of the layout: b = 1 median 1.07, one tenth above 1.68, one hundredth above 3.0; b = 1.5 median 1.03,
  one hundredth above 1.28. The squeeze is the same at every step (it does not multiply down the tree).

**What it gives.**
- c = -0.3: **seen** (`clouds-a.png`, rows 4 and 5): a closed, gently bumpy ball, filled all over by dots alone.
  This is the only place in the folder where "bulbs all over by themselves from roots" is visibly true.
- c = -1, b = 1: **seen** (`sheet.png` and `sheet-top.png`, row 4; `cuts.png`): one lump of about six fused round
  masses, taller on the upper side. **Measured**: 3.0 times the size of the one-plane solid, 1.38 times more above
  the flat plane than below.
- rabbit, b = 1: **seen**: a ragged mass with holes from both eyes; the upright cut shows a core with thin arcs
  round it (shards). **Measured**: 1.6 times the one-plane size.
- b = 2: **seen** (rows 5, both eyes; `cuts-c1.png`): the bodies are round and apart as in one plane, and thin
  spindles several times longer than wide stick out of them. Above the flat plane the biggest two stand on the
  middle body; below it they hang under the side bodies. So the two sides do not match.
  **Measured**: 1.12 and 1.02 times the one-plane size.
- b = 1.5: in between: bodies half fused, with horns (`look1-a.png`, `cuts.png`).

**Exactly why (reasoned, and it matches the numbers).** The square sends one more circle of directions onto the
flat circle: the ring at s = b/6, above the flat plane. Whatever sits on the flat circle (for c = -1: the two big
neighbours of the middle body) appears a second time on that ring, **full length**, because lengths are squared
the same way everywhere. The ring stands about gd(pi b / 3) above the flat plane and its bodies are about
cosh(pi b / 3) times longer than wide (worked out for c = 0 and the plain layout; adding c moves points off the
ring, so for c = -1 this is a guide, not a number measured on the solid; the upright cuts in `cuts-c1.png` show
the two extra bodies where it says, as shoulders for b = 1, horns for b = 1.5 and ears for b = 2):

| b | ring stands at | its bodies are |
|---|---|---|
| 0.75 | 41 degrees | 1.3 times longer than wide |
| 1 | 51 degrees | 1.6 |
| 1.5 | 67 degrees | 2.5 |
| 2 | 76 degrees | 4.1 |

Low ring: round enough, but full-size bodies 51 degrees up touch the flat ones and the middle one: a lump. High
ring: they clear, and they are needles. There is no b in between that is both (b = 1.5 is half fused and already
2.5 times too long). The lopsidedness comes on top and cannot be removed for power 2 (see the three facts).

## 5. About section 3 of the briefing (the wall), from this corner

- The reading stands. I found nothing that contradicts W-a to W-f.
- One addition to W-a. The zip is the "fold" option with the crease ironed out: in pillow coordinates the latitude
  is folded back once (a tent), and the pole is replaced by a zipped slit so that the fold leaves no crease. It
  treats all longitudes alike except at the two zips. It is still a lump for c = -1. So the fold fails for a
  reason that has nothing to do with its crease: the folded part carries a full-size second copy.
- One correction to section 4. "Square pillow: c = -1 fused along the whole x-axis by its nature (branch directions
  lie ON the flat circle)" is not the whole cause. With the flat circle on the one-third line there is no special
  point on the flat circle, the push off the flat plane is even to 3 parts in 10000, and c = -1 is still fused
  (b = 1). **Seen and measured.**
- Door (iii), "limit sets of inverse branches", is closed as far as root sets go. **Reasoned**, three cases with a
  picture each: roots that pull to the flat plane (nothing new), roots that leave a direction alone (rings), roots
  that shrink every direction (a pillow; lump or needles); and mixing root sets gives a union lump or the one-plane
  look (section 3 above). What I did not do: objects built from the flat picture without any 3D root at all, and
  group limit sets (the `klein` corner).

## 6. Method notes

- Solids of rules with several squares, and of the zip (which is slow), are made on a grid of blocks: a block is
  inside when its square lands on an inside block, repeated until nothing changes, with one exact squaring in
  front of the grid for the picture. **Measured** against the plain orbit test (one plane, c = -1, 160^3 blocks):
  0.07 % of the box differs, all of it at the skin. Roughness finer than a block (0.015) is not to be trusted;
  the lump, the holes and the needles are far bigger and also show in `cuts.png`, which uses plain orbits.
- The two eyes are the library's: (0.45, 0.5, 1) looks down on the flat plane, (0.2, 1, 0.35) looks along it.
- Clouds: 40000 dots, 48 roots each, the first 18 thrown away, a root picked at random each time.

## 7. Files

- `roots.py`: the roots of the one-plane and quaternion squares, `class Zip` (rule, roots, layout), `grid_K`
  ("some" / "every" solids), `render`, `sheet`, `cloud`, and `check`.
- `exp.py`: `cuts`, `clouds`, `solids`. `measure.py` -> `measure.log`. `compose.py` -> `sheet.png`, `sheet-top.png`.
- `best.py`: `rule(b=1.0, mirror=False)` (the zip as a mem.Rule), `both(c, mode)` (zip and its mirror image).
- Pictures: `sheet.png`, `sheet-top.png` (rows: one plane; four roots "some"; four roots "every"; zip b = 1;
  zip b = 2), `clouds-a.png`, `clouds-top.png`, `cuts.png`, `look1-a.png` (first look, coarser), `look2-a.png`.

## 8. For next, from this corner

- Nothing more from root sets for power 2. The even-shrinking family is one family with one dial, and the table in
  section 4 says why no setting works.
- Cheap and worth one look: the power-3 zip (flat circle on the line at one quarter, u -> 3 conj(u)). It is the
  only member that is not lopsided, so it would tell whether the user's eye objects to the lopsidedness or to the
  lump and the needles. I expect the latter: the ring argument does not depend on the power.
- What two planes and "along" have and the zip has not: their extra copies share the big bodies on the x-axis with
  the flat picture, so nothing collides. The zip's extra copy shares nothing. For the rabbit there is no such
  shared line in space (W-b), so a rule would have to take it from the flat picture itself (the `fromc` corner).
