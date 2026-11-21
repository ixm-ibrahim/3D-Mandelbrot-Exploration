# Round 21, the prover: what can and cannot come out of "follow the plane the orbit makes"

No rule was searched for here. Every rule in `myrules.py` is a TEST rule for one of the statements below.
Marks: **[proved]** a complete argument is given; **[argued]** the argument has a gap that is named;
**[measured]** a number computed here; **[seen]** in a picture I looked at; **[open]** not settled.

Words used throughout. A *sheet* is a flat plane that holds the x-axis; the *flat page* is the sheet z = 0; the
*upright page* is the sheet y = 0. For a point c: c0 = (x, distance of c from the x-axis) is "c seen in its own
sheet", a point of the flat picture. *Turning* always means turning round the x-axis. The *flat set* is the flat
Mandelbrot set; "the flat set spun" is the lathe's solid {c : c0 in the flat set}. P is the one-plane square
(`S.oneplane`); "P about a sheet" as in the briefing. The *lathe* is (x, y, z) -> (x^2 - y^2 - z^2, 2xy, 2xz).

## 0. The short answer to the user's question

"Follow whatever new plane is made during the orbit":

1. If the recipe names nothing that is fixed off the x-axis and does not tell left from right, **no new plane is
   ever made**: the orbit of 0 never leaves the sheet of c (S2). There is nothing to follow.
2. If it does tell left from right, new planes are made, and the solid is **still exactly the flat set spun** (S3).
3. So the followed plane needs a fixed place to start from (the flat page). Then:
   - if the plane later depends on the orbit alone ("forgets its start"), the solid is the flat set spun **with
     pieces cut away**; every bud it has is a piece of one of the lathe's rings; nothing new grows (F4, F5);
   - if it never forgets, it is a fixed-plane rule in disguise and the older limits apply (D4).
4. "Round buds all round, no rings, no count of planes" is **not** forbidden by logic or by symmetry (D1, D2: a
   hand-built solid of that kind is drawn in `t6_necklace.png`), but every mechanism looked at misses it for a
   stated reason (D3, D4, D5), and no squaring rule that makes it is known (D6).

## 1. Claim S

### What "uses nothing but the x-axis, c and the orbit's own points" means

A *recipe* is: something the orbit may carry (a sheet, a frame, earlier points, counters: the "carried thing" s), a
start for it, and a step (point, carried thing, c, step number) -> (next point, next carried thing).
The recipe **turns with c** if there is a way to turn carried things (a sheet turns as a sheet, a frame as a frame,
an earlier point as a point, a number stays as it is) such that

- (i) the start of the carried thing for the turned c is the turned start, and
- (ii) the step applied to turned things gives the turned result,

for every angle. This is exactly what a recipe gets for free when its wording uses only: position along the x-axis,
distance from the x-axis, lengths, angles between things, "the sheet through this point", "the plane through these
points", "half-way between these two sheets", "the point before", the step number, fixed NUMBERS, and (handed
recipes) "to the right of" / cross products. Not allowed: the flat page, the words y, z, up, front, any fixed sheet,
direction or point off the x-axis, a fixed frame to start from, a tie-break that names one of these.
A recipe is *unhanded* if the same holds for mirrors in sheets (it never says left or right).

### S1. The claim itself  [proved]

If a recipe turns with c, the orbit of the turned c is the turned orbit, step by step (induction on the step, using
(i) once and (ii) at every step). A turn does not change lengths, so c stays bounded exactly when the turned c does:
**the solid looks the same from every side of the x-axis.** If its cut along the flat page is the flat set, then it
is {c : c0 in the flat set}: as a set it IS the lathe's solid, whatever the recipe does in detail.

### S2. Memory  [proved]

S1 never asks what is carried. It holds for a carried sheet, a carried frame, earlier points, anything, as long as
(i) holds. A start that is the same for every c satisfies (i) only if no turn changes it: "no sheet yet", a number,
something on the x-axis. **The flat page as the start breaks (i); nothing else in a rule with memory does.**
A frame can be made without anything fixed only from c or an orbit point off the x-axis (the x-axis, the direction
out to the point, and, handed, their cross product); such a frame turns with c, so S1 applies to it.

Unhanded case, one step further: the mirror in the sheet of c leaves c and the start unchanged, so it leaves every
orbit point unchanged, so **every orbit point lies in the sheet of c**. All planes "made during the orbit" are the
one sheet of c. [proved]

Measured (`t1_symmetry.txt`, 40,000 points, 40 steps, share of verdicts that change when c is turned by a random
angle): the lathe `own` 0.000 %, `lag25_cov` 0.000 %, `csheet_flat` 0.000 %, `csheet_own` 0.000 %; the scout's rules
that start from the flat page: `fixed` 1.29 %, `lag25` 2.79 %, `lag50` 1.37 %, `lag75` 0.66 %, `delay` 0.47 %,
`first` 1.50 %. Two covariant rules do NOT come out at zero on the computer: `delay_cov` 0.163 %, `lag50_cov`
0.015 %. That is not a failure of S1; see K1.

### S3. Handedness  [proved]

S1 uses turns only, and a turn does not swap left and right. So a recipe that uses cross products still gives a spun
solid. And a spun solid is automatically its own mirror image in every sheet (it depends on c0 only). So
**handedness cannot un-spin anything, and for the Mandelbrot solid it cannot even un-mirror anything.**
What it can do: let the orbit leave the sheet of c; un-mirror the Julia sets of c off the x-axis (J2); and, together
with a fixed sheet, lower the forced symmetry from two mirrors to a half-turn (F1).

Measured: the handed test rules `twist` (30 degrees), `twist8`, `delay_twist`, `csheet_twist`: Mandelbrot solid
turned 0.000 %, mirrored 0.000 %, with 7.5 %, 8.7 %, 3.3 %, 1.4 % of the box inside; basilica turned 0.000 %. The
rabbit of `twist8` (7.2 % of the box inside): 4.74 % of verdicts change under the mirror z -> -z, and for the rabbit
turned 35 degrees 4.83 % change under the mirror in the sheet of c; for every unhanded covariant rule that number is
0.000 %.

### S4. Conventions at undefined points  [proved in the form stated; the size estimate is argued]

Let the recipe turn with c except in "undefined" situations, where a convention names something fixed. Let E be the
set of c whose orbit meets such a situation at some step. Before that step the orbit turns with c, so E is itself
spun, and for c outside E the verdict is the same for c and for every turned c. **The solid differs from a spun one
only inside E.** How big is E?

- *The sheet of the start point 0* (or "the sheet before anything was squared"): every orbit meets it. E is
  everything. This convention IS the fixed starting sheet; it is not a detail.
- *The sheet of c for c on the x-axis*: E is the x-axis. For the Mandelbrot solid it changes nothing (those orbits
  stay on the x-axis, and P about any sheet sends (x, 0, 0) to (x^2, 0, 0)). For the Julia sets of those c it
  changes everything (J3).
- *The own sheet of a later orbit point that lands on the x-axis*: for an unhanded recipe the orbit lies in the sheet
  of c, so "on the x-axis" is one condition and E consists of skins of revolution; for a handed one it is two
  conditions and E consists of circles. Either way E has no volume, unless the recipe sends a whole chunk of c's
  exactly onto the x-axis [argued: not proved for a general recipe]. A set without volume cannot carry a bud.

Measured (`t1b_convention.txt`): the lathe with "within the distance tau of the x-axis, use the flat page": share of
verdicts that change under a turn: tau 0.3: 1.44 %, 0.1: 0.44 %, 0.03: 0.10 %, 0.01: 0.02 %, 0.001: 0.000 %,
0: 0.000 %. (The same table for the delay recipe does not go to zero, 0.195 % at tau = 0; that is K1, not the convention.)

### K1. A warning: S1 is about exact orbits, and a computer rounds  [measured]

`delay_cov` and `lag50_cov` turn with c by construction, yet their solids on the computer are not exactly spun and
are smaller than the lathe's (7.06 % and 7.99 % of the box against 8.02 %). Cause: for these recipes the sheet of c
is a **knife edge** for part of the flat set. A lift of the orbit off the sheet by one rounding error grows until
the orbit falls off. Evidence (`t2_knife.txt`, cut of 163,800 points, exact answer = the flat set in every column):

| rule, steps | z = 0 exactly (rounding cannot leave the page) | every c lifted by 1e-13 | sheet at 22.5 degrees |
|---|---|---|---|
| delay_cov, 40 / 80 / 160 | lost 0 / 0 / 0 | lost 67 / 596 / 914 | lost 2033 / 6543 / 9165 |
| lag50_cov, 40 / 80 / 160 | 0 / 0 / 0 | 2 / 34 / 176 | 63 / 709 / 1748 |
| lathe, 40 / 80 / 160 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

`t2_knife.png` [seen]: the cut of delay_cov along the sheet at 22.5 degrees; red = points of the flat set the
computer loses: a crescent on the left of the main body, most of the period-2 disc, the period-3 buds.
So the machine's own y and z axes act as "something fixed off the x-axis". A picture of such a rule shows the spun
solid minus its knife-edge part, and that part depends on the direction of the cut.

### K2. The knife edge of `delay` in closed form  [proved (linear part), measured]

Take c0 in the main body of the flat set and its resting point zeta (zeta^2 + c0 = zeta, |zeta| < 1/2). Lift the
orbit a little off the sheet of c; call the heights h(n). To first order, for `delay` (each point squared about the
sheet of the point before):

    h(n+1) = 2 |zeta| h(n)  -  2 (|zeta| - Re zeta) h(n-1)

(derivation: turn the point into the remembered sheet, which changes its height by -theta*y with theta = h(n-1)/y;
P multiplies heights by 2|zeta|; turning back adds theta * Im(zeta^2) = theta * 2xy). When the two roots of
t^2 - 2|zeta| t + 2(|zeta| - Re zeta) = 0 are complex, the lift changes per step by the factor
**sqrt(2 (|zeta| - Re zeta))**. It dies out exactly where |zeta| - Re zeta < 1/2: the right-hand, heart-shaped part
of the main body. For comparison the same factor is 2 Re zeta for the lathe and 2|zeta| for a sheet that never moves
(both below 1 in the whole main body), and for the lagging sheet with share lam it is the larger root of
t^2 - (2|zeta| + 1 - lam (1 + 2(|zeta| - Re zeta))) t + 2|zeta|(1 - lam) = 0, also below 1 in the whole main body.

Measured (`t2c_delay_rate.txt`, in the sheet at 22.5 degrees): delay, formula against measured: 0.9988 / 0.9988,
1.2363 / 1.2308, 1.2461 / 1.2614, 0.9070 / 0.9068, 1.1092 / 1.1062, 0.7562 / 0.7467, 1.1398 / 1.1365 (three more
could not be fitted); lathe 0.7471 / 0.7471, 0.8471 / 0.8471, 0.9229 / 0.9229; fixed sheet 0.7814 / 0.7814 and six
more to four digits; lag 0.25: 0.7655 / 0.7596, 0.8003 / 0.8006, 0.8320 / 0.8354, 0.8548 / 0.8551, 0.8474 / 0.8509,
and two that are 2 to 3 % off (0.7491 / 0.7274, 0.7401 / 0.7254); lag 0.5 and 0.75 shrink too fast to fit (one value,
0.6979 / 0.7039), so for those the formula is checked at one point only. That the lag formula stays below 1 in the
whole main body: a scan of 200,000 random (zeta, lam), largest value 0.999999 (`t9_lagscan.txt`).
`t2b_delay_edge.png` [seen], `t2b_delay_edge.txt`: the flat main body, every c lifted 1e-9 off its sheet, 700 steps:
cream (back in the sheet) is the heart-shaped part the formula gives; green (32,621 points): the lift grows but the
orbit stays bounded OFF the sheet; red (40,923): it leaves. Formula against "back in the sheet": 5,300 of 143,396
differ, almost all (5,209) in a thin band just on the growing side of the formula's line, where the growth is too
slow to show in 700 steps [that reading of the band is argued, not checked with longer runs].

Consequence [argued from the measured numbers]: this is why the scout saw dust for `delay`. For the rabbit a lift of
1e-6 off the page loses 100 % of the flat rabbit's points under `delay`, 51 % under `lag50`, 0 % under `fixed`,
`lag75`, `first`, `own`, `along` (`t2_knife.txt`, last table). **Being exact on the flat page is not enough: the page
must also hold against a small lift, or the solid near it is a film with no thickness.** Going round the period-3
bud, `delay` is inside at the turns 0.0 and 180.0 only (`t4_rings.txt`): a bud of zero thickness.

### K3. A property of the library that every agent should know  [measured]

A sheet is stored as (cos 2 theta, sin 2 theta) and read back by a half-angle formula. For |theta| below about
1e-8 radians cos 2 theta rounds to exactly 1 and the sheet is read back as the flat page (the same near the upright
page). So lifts below about 1e-8 do not move a carried sheet there, and the flat page looks more stable than it is.
`t2c_delay_rate.txt`, last table: `delay` in the flat page, lift 1e-11: measured factors 0.5898, 0.7814, 0.8540,
0.9231, 0.7483, 0.6168 = 2|zeta| to four digits, where the true factors are 0.9988, 1.2363, 1.3042, 1.2461, 0.9070,
1.1092. Tests of stability must be made off the flat page (I used the sheet at 22.5 degrees) or with lifts well above 1e-8.

## 2. Julia sets

### J1. c on the x-axis, nothing fixed off the x-axis: the Julia set is spun  [proved]

Same induction as S1 with the start point in the place of c (the turn leaves c where it is). If the cut along the
flat page is the flat Julia set, the solid is that set spun: the lathe's Julia set, as a set, whatever is carried.
**The basilica, San Marco and the airplane, the user's first three sets, must fail test 4 (rings) for every recipe
that has nothing fixed off the x-axis.** A good basilica needs something fixed.
Measured: basilica, share of verdicts that change under a turn: `own`, `delay_cov`, `lag50_cov`, `lag25_cov`,
`csheet_own`, `twist`, `twist8`, `delay_twist`, `csheet_twist`: 0.000 %; the first five hold 3.14 % of the box each
(the lathe's basilica).
`along` has something fixed: its formula turns the reference sheet by 0.25 sin(4 phi), a pattern of four sheets
(0, 45, 90, 135 degrees). Measured: its basilica turned by a quarter turn: 0.000 % of verdicts change; by 45 degrees
0.060 %; by 22.5 degrees 0.228 %. "Eight round buds round each body" is the symmetry of that dial (quarter turns
and mirrors move a bud to 8 places), see D3.

### J2. c off the x-axis: c supplies a whole frame  [proved]

For c off the x-axis the recipe has, for free: the sheet of c, the direction from the x-axis out to c, and (handed)
the side of the sheet. That is a complete frame. So ANY fixed rule F, written in the frame of c, is a recipe that
turns with c; for c in the flat page it is F itself. What symmetry is left: the mirror in the sheet of c if the
recipe is unhanded (then the Julia set is its own mirror image in that sheet), nothing if it is handed. So for c off
the x-axis symmetry forbids nothing; the family only has to satisfy "Julia set of the turned c = the turned Julia set".
Measured: the rabbit of "P about the sheet of c" (`csheet_flat`, `csheet_own`) against the one-plane rule's rabbit:
0 of 40,000 verdicts differ. Start and c turned together: 0.000 % for every covariant test rule, 1.7 % to 5.7 % for
`along` and for the scout's rules that start from the flat page (`delay` aside, whose rabbit is empty in this test). Mirror in the sheet of c (rabbit turned 35 degrees): 0.000 % for the unhanded covariant
rules, 4.83 % for `twist8`.
But the Mandelbrot solid of every such recipe is spun (S1; measured 0.000 %).

### J3. The two do not fit together on the x-axis  [proved]

On the x-axis the sheet of c is undefined. Just off it, in the flat page, the Julia set is F's; just off it in the
sheet at theta, it is the same set turned by theta. AT the x-axis the recipe must either give the spun set (J1), or
take a convention, which is something fixed. Measured: basilica of `csheet_flat` (convention: the flat page) = the
one-plane rule's (0 of 40,000 differ; 341 differ from the lathe's); basilica of `csheet_own` (convention: own sheet)
= the lathe's (0 differ; 341 differ from the one-plane rule's). The convention acts on a set of c without volume and
decides three of the six standard Julia sets completely.

### J4. Memory that starts from the flat page  [proved; measured]

For c on the x-axis the flat page as start leaves three symmetries: the half-turn, the mirror in the flat page, the
mirror in the upright page (the two mirrors only for unhanded recipes). Measured for all seven scout rules, basilica:
z -> -z 0.000 %, y -> -y 0.000 %, half-turn 0.000 %. So whatever such a rule puts off both pages comes in fours.
For c in the flat page off the x-axis only the mirror in the flat page is left (measured 0.000 %).

### J5. The Julia sets of `first` in closed form  [proved]

After the first squaring the rule is the lathe, so its Julia set is {v : P(v) + c lies in the lathe's Julia set of c}:
the lathe's set pulled back once through the one-plane square. For c on the x-axis the lathe's set is all rings, and
their pull-back is what `t7_forget_julia.png` shows [seen]: ribs round every body, buds only at top and bottom.

## 3. Rules with memory whose only fixed thing is the starting sheet

### F1. The symmetry that is left  [proved; measured]

The turns and mirrors that keep the flat page (a sheet has no marked side or direction) are: the half-turn, the
mirror in the flat page, the mirror in the upright page. So the Mandelbrot solid of every such rule is unchanged by
the half-turn, and, if the rule is unhanded, by both mirrors. Measured: all seven scout rules, 0.000 % for each of
the three. Consequences: the orbit of a c in the upright page stays in the upright page, so the cut at 90 degrees is
a flat picture of its own; a bud off both pages comes in fours, a bud on the upright page in twos. A count of two
planes is built into every rule of this kind.

### F2. Beyond that, nothing is forbidden in general  [proved, by a construction that is not a principled rule]

For ANY set D with those symmetries there is a rule with memory, the flat page its only fixed thing, whose solid is
D: at the first step it looks where c sits relative to the flat page (x, distance from the x-axis, angle between the
sheet of c and the flat page), carries a flag "in D" or "not in D", parks the orbit at 0 or throws it out.
(`t6_necklace.py` draws its solid exactly this way.) So "memory + flat page" alone limits nothing. All real limits
come from what a step is allowed to be, that is from test 5.

### F3. If every step is P about some sheet  [proved]

|P(v)| = |v|^2 for every sheet (|P|^2 = f^2 ((r^2 - z^2)^2 + 4 r^2 z^2) = f^2 (r^2 + z^2)^2 = r^4). So whatever the
memory does, the solid lies inside the ball of radius 2, contains the ball of radius 1/4, and meets the x-axis in
exactly -2 .. 1/4.

### F4. A sheet that forgets its start: the solid is the flat set spun with pieces cut away

Setting: the first k squarings may use the flat page; from then on the recipe turns with c. Then

    c is in the solid  <=>  (the point and carried thing after k squarings) lies in B(c),

where B(c) = everything from which the later recipe, with the constant c, stays bounded; and the family B turns
with c. All that is not spun about the solid sits in the first k steps. [proved: it is a restatement]

For the scout's kind (later squarings about the point's own sheet = the lathe), in the frame of the sheet of c,
c0 = (a, b, 0), the later recipe is (X, Y, Z) -> (X^2 - Y^2 - Z^2 + a, 2XY + b, 2XZ). Then:

- **Lemma [proved].** This map has no attracting cycle off the sheet of c. Proof: Z(n+1) = 2 X(n) Z(n), so on a
  cycle with Z not 0 the product of the 2X is 1. The matrix of slopes at a point is a turn-and-stretch by 2|v| in the
  point's own sheet and a stretch by 2X across it, so it changes volumes by 2X * 4|v|^2. Over the cycle that is at
  least the product of |2X|^3 = 1: volumes do not shrink, so the cycle does not attract.
- The flat attracting cycle of c0, when there is one, also attracts across the sheet (the cross factors 2X are no
  larger than the flat factors 2|z|). So the fat part of B(c) is the 3D basin of the flat cycle; if c0 is outside the
  flat set there is no fat part. [argued: bounded orbits that are not drawn to a cycle are not excluded by the lemma]
  Measured (`t3b_outside.txt`, 400,000 start points, 1500 steps): c0 = 0.5+0.5i, -0.8+0.4i, -0.2+0.9i, 0.32+0.02i
  (all outside the flat set): 0 stay, longest stay 38 to 100 steps; rabbit, Siegel disc, -0.4+0.3i, 0.3+0.5i,
  0.33+0.07i (inside): 6.6 % to 18.5 % stay, and every one of them has sunk into the sheet (largest height left 0 to 1e-168).
- **Hence: the solid lies inside the flat set spun, up to its skin.** Proved for the cuts at 0 and 90 degrees (there
  the first point lies in the sheet of c, the question is flat, and a flat Julia set of a c outside the flat set has
  no area); argued in between; measured (`t3b_outside.txt`, `first`, 400,000 random c): points in the solid whose c0
  has left the flat orbit: 351, 92, 24, 10 at 60, 200, 1000, 3000 squarings; the 10 that remain have a c0 that itself
  leaves only after 135 to 1956 squarings (the skin); of the 369,667 points whose c0 leaves within 60 squarings none
  stays 3000 (longest stay 901).

So **a rule that forgets its start cannot grow anything off the flat page that the lathe does not have. Every bud
it has is a piece of one of the lathe's rings.** How much is cut away (`t3_first.txt`, 300,000 points, 200 steps;
the flat set spun holds 7.224 % of the box):

| rule | in the solid | in the solid, not in the spun set | of the spun set, cut away |
|---|---|---|---|
| own (lathe) | 7.224 % | 0 | 0 |
| first (k = 1) | 5.532 % | 0.023 % | 24 % |
| first2 | 4.359 % | 0.013 % | 40 % |
| first3 | 3.649 % | 0.008 % | 50 % |
| first5 | 2.810 % | 0.007 % | 61 % |
| first8 | 2.238 % | 0.004 % | 69 % |
| delay | 3.295 % | 0.005 % | 54 % |
| fixed (one-plane rule, never forgets) | 1.445 % | 0.002 % | 80 % |
| lag75 / lag50 / lag25 | 6.679 / 6.074 / 3.791 % | 0.082 / 0.379 / 0.068 % | 9 / 21 / 48 % |
| along (bench) | 7.026 % | 0.623 % | 11 % |

So the answer to "how much can still differ after forgetting at step k": by volume a quarter of the solid already
for k = 1, more for later k; but only by removal. (Not expected, measured only: the one-plane rule's own solid also
lies inside the flat set spun, 6 of 300,000 points outside. `along` and `lag50` do stick out.)
`t7_forget_mandel.png` [seen]: rows k = 0 (lathe), 1, 2, 3, 8, never: every cut is the flat set with more and more
missing; the buds off the page go first (at 11.25 degrees the period-3 bud is already gone for k = 1), then the left
side of the main body and the period-2 disc; the rough solid goes from the lathe's ribbed top to the one-plane
rule's smooth rock. No round bud off the flat page in any row.

### F5. `first` in closed form  [proved; checked against the library with 0 differences]

c at the turn theta, c0 = a + i b in its own sheet, r = |c0|, f = r^2 / (r^2 + b^2 sin^2 theta). In the frame of the
sheet of c the first point is

    X1 = a + f (a^2 - b^2 cos^2 theta)
    Y1 = b + 2 f b (a cos^2 theta + r sin^2 theta)
    Z1 = f b (r - a) sin(2 theta)            (the height above the sheet of c)

and every later step is (X, Y, Z) -> (X^2 - Y^2 - Z^2 + a, 2XY + b, 2XZ). At 90 degrees it is flat:
z1 = c + s(c) with s(c) = f (a^2 + 2 i r b), f = r^2 / (r^2 + b^2), then z -> z^2 + c.
Checked (`t3_first.txt`, 163,800 points per cut, 60 steps) against `M.cut_axis` at 0, 11.25, 22.5, 33.75, 45, 67.5,
90 degrees: 0 verdicts differ at every angle; the flat formula at 90 degrees: 0 of 163,800 differ.
`t3_first_cuts.png` [seen]: the seven cuts; cream = solid, dark red = part of the flat set cut away, green = in the
solid but outside the flat set (a one-pixel line on the skin: slow leavers at 60 steps).

In words: go once round the x-axis over a fixed c0. The first point runs round a closed loop on the ball of radius
|c0|^2 about c0; at the flat page it is the true c0^2 + c0; its height off the sheet of c is f b (|c0| - a) sin 2 theta.
The lathe's ring over c0 survives at exactly the turns where the loop point lies in the 3D basin. The basin is open
and holds the flat one, so each flat bud survives over an ARC of turns round the flat page (and round 180 degrees).

Measured arcs (`t4_rings.txt`, circle through the centre of a flat bud, 80 steps, quarter-degree steps; "round"
= the half-arc a ball of the bud's flat radius would cover):

| bud (round would be) | own | lag75 | lag25 | first | first2 | delay | fixed | away |
|---|---|---|---|---|---|---|---|---|
| period 3 (+-7.2) | ring | ring | +-20.2 | +-20.2, slivers to 22.5 | +-6.2, slivers to 16.5 | 0.0 only | +-1.2 | +-1.5 at 0, 90, 180, 270 |
| period 4 (+-4.8) | ring | ring | +-23.5 | +-32.0 | +-13.2 | 0.0 only | +-1.0 | +-1.2, four places |
| period 5 (+-4.1) | ring | 4 single points | +-14.8 | +-11.5 | +-12.2 | 0.0 only | +-0.8 | +-3.5, four places |

(`lag50` and `along`: dozens of scattered arcs, 34 to 88 per circle.) The arc has no reason to match the bud's own size and does
not: 0.9 to 6.7 times the round value for the forgetting rules, 0.17 to 0.2 times for the one-plane rule.
`t4_rings.png` [seen]: the band round the x-axis at x = -0.1226 unrolled. The lathe: a level stripe (ring). `lag25`,
`first`, `first2`: the skin rises smoothly to a peak at the flat page; the bud is the tip of a ridge, not a ball
sitting on the body. `fixed`: a thin spike at the flat page. `away`: four thin spikes. `along`: four cusps with spray.

## 4. The dichotomy: "only at the flat page, or a whole number of times, or a ring"

### D1. For an arbitrary solid it is true and says nothing  [proved]

Take any closed solid whose flat cut is the flat set and the circle round the x-axis through a point of a flat bud.
The part of the circle inside the solid is a closed set on a circle: the whole circle, or separate arcs and points.
That is all logic gives. It does not say the number of pieces is the same for two buds, or that the pieces are evenly
spaced, or that they line up on planes. **"So round buds all round with no count of planes are impossible for any
rule whatever" does not follow, and as a statement about solids it is false** (D2).

### D2. A solid that has it  [constructed, seen, measured] -- `t6_necklace.png`, `t6_necklace.py`

HAND-BUILT, not from a squaring rule. Recipe: (1) every body of the flat set that sits on the x-axis is spun (no ring
arises: these are bodies ON the axis). (2) Every limb off the x-axis (a bud touching one of those bodies, with all
that grows on it) is puffed in its own sheet (a disc of radius r becomes a ball: thickness sqrt(d (2r - d)) at the
distance d from the disc's edge, measured along the ring) and repeated N times round the x-axis, N = the even number
nearest to pi * (height of the bud above the x-axis) / (1.3 * radius of the bud), at least 2, one copy on the flat
page. (3) On the flat page the true flat orbit is run. The table behind it: the upper half of the flat picture at
0.002 per pixel, 2500 + 96 steps, bodies = connected patches of one cycle period, rim pixels given to the nearest body.
Measured: flat page 0 of 20,000 verdicts differ; 0.46 % change under a turn (not spun); N = 20 (period 3), 32
(period 4), 38, 24, 38, 56, 106, 50, 118, 44: no common count; the only sheet all necklaces share is the flat page.
Seen: a smooth main body, a necklace of 20 round balls where the lathe has its period-3 ring, smaller necklaces at
every other latitude, each ball with its own smaller buds; cut along the flat page = the flat set; cut across at
x = -0.12 = a disc with 20 round beads; cut at 11.25 degrees = the bare bodies with a few small sections.
Its faults, plainly: one level only (the buds ON a ball sit in that ball's own sheet, two directions, not all
round); buds smaller than 0.008 are not in the table and show as faint grooves (rings) on the main body; the flat
page is a visible seam where every necklace has a bead; and it is a look-up table, not a rule (fails test 5).

### D3. With symmetry it is a theorem, and it explains every "count"  [proved]

Let G be the set of turns that leave the rule's fixed data unchanged. G is closed under doing one turn after another,
so it is either all turns, or the turns by multiples of 360/n degrees for one whole number n. Therefore:

- nothing fixed off the x-axis: G = all turns: every feature off the axis is a ring;
- otherwise: every feature off the axis appears n times, evenly spaced (2n times off the mirror sheets if unhanded);
  n = 1 forces nothing.

A "count of planes" that repeats evenly at every scale is the n of the rule's fixed data and nothing else:
`along` and `away`: the pattern sin(4 phi), quarter turns (measured: `along`'s Mandelbrot solid turned 90 degrees:
0.000 % change, 45 degrees: 1.7 %; `away`'s buds at 0, 90, 180, 270); memory rules that start from the flat page:
n = 2. **So a rule whose only fixed thing is the flat page is the only kind for which symmetry forces neither rings
nor a count.** What it then does off the page is decided by its dynamics, D4 and D5.

### D4. Where a bud can root at all: along lines  [argued by counting conditions; measured for three rules]

A body of the solid is a region of c where the orbit settles on a cycle. On its skin the cycle lets go, in one of
two ways: a single real multiplier reaches +1 (bare skin) or -1 (one period-2 lump over a whole patch); or a complex
pair reaches size 1: near the skin the orbit goes ROUND the cycle by an angle alpha per turn of the cycle, and a bud
of q times the period can root where alpha is the fraction p/q of a full turn. In the flat picture the skin is a
curve and "alpha = p/q" picks POINTS on it: round buds, one at every fraction. In three dimensions the skin is a
surface and "alpha = p/q" is still ONE condition: it picks LINES. A bud rooted along a line is a ridge. A ridge is a
ring if the line closes round the x-axis; it looks round only if the line is short, that is only if the part of the
skin where a complex pair leads is a narrow BAND. This count does not change with memory (memory enlarges what the
orbit is, not the three numbers of c). To root buds at POINTS of a surface two independent angles would have to be
fractions at once, which three numbers of c cannot arrange except by coincidence.
Two consequences [argued]: small buds get thinner (like 1/q^2 in the flat picture) while their lines do not get
shorter, so small buds become ribs (what the scout saw where the sheet follows closely); and the "count of planes"
of a smooth rule is the number of bands that cross a latitude.
Gap: this is the standard count for smooth rules and typical cases; the lab's rules have creases, and a ridge can in
principle be pinched into beads. A pinch is a two-condition coincidence on a line, so it needs a reason, and the only
reason known here is a symmetry of the fixed data (the dial).

Measured (`t5_skin.py`: for each c of a cut the resting point of F + c is found, the 3 x 3 matrix of slopes there by
central differences, its eigenvalues; "skin layer" = largest eigenvalue size between 0.9 and 1):

| rule | cut across x = -0.12 | cut across x = -0.45 | cut along the sheet at 45 |
|---|---|---|---|
| lathe | complex pair 100 % | 100 % | 100 % |
| one-plane | complex pair 35 %, real + 65 % | 43 %, 57 % | 12 %, real + 45 %, real - 43 % |
| along | complex pair 70 %, real - 30 % | 58 %, 42 % | 60 %, 40 % |

`t5_skin.png` [seen]: lathe: the whole body "goes round", the level lines of alpha are circles round the x-axis:
rings. One-plane rule: the body in a cut across is a lens; "going round" only in a thin strip along the flat page, the
rest of the skin bare: buds only where the strip meets the skin, in the flat page. `along`: a cross of four arms
(0, 90, 180, 270 degrees) where it goes round, separated by diagonals where a real multiplier leads: four bands.

### D5. Forgetting rules  [from F4]

Their buds are pieces of the lathe's rings, kept over an arc round the flat page (and round 180 degrees, mirrored).

### D6. What arrangement would satisfy someone who rejects both, and can a rule make it?

- Every round body with an exact flat cut has its own axis in the flat page (from its root to its tip). The flat
  picture puts 2 smaller buds at each height along that axis (p/q and its mirror image). In space the same height is
  a circle round the body's axis. Per circle the choice is: 2 (flat page only: the one-plane look), N (a necklace),
  or all of it (a ring). In the flat picture the 2 is everything the mirror gives; the honest carry-over of
  "everything the symmetry gives" to space IS the ring. To get N instead, something must pick N places. [proved as a
  description; it is D1 and D3 applied to each body]
- A necklace whose N differs from bud to bud ("as many as fit"): possible as a set (D2).
- A spiral: the flat cut needs a bud at the turns 0 and 180 at every height p/q, so a spiral alone cannot be right;
  the other beads of each necklace may be offset along a spiral (needs a handed rule).
- Place depending on x: the same, a necklace with offsets; each necklace must still have a bead on the flat page.
- Corners of a regular solid: not round the main body (the flat picture has one mirror only, cusp on the right,
  period-2 disc on the left, so the x-axis is special in the cut and hence in the solid); not on a single bud either
  (its root is special and the flat cut has the period-doubling bud opposite the root, so only turns round its own
  root-to-tip axis can be symmetries: ring, N or 2 again). [proved]
- Can a rule make the necklace? The look-up rule of F2: yes, not principled. Nothing fixed: no (S1). Forgetting
  rules: no (F4). Smooth rules: each ridge of D4 would have to be pinched into N(q) beads for every q, with no
  symmetry to do it [argued]. **[open]** whether a principled rule that is not smooth can do it. I know of none.

In plain words: round buds all round need places round each body to be picked out. If nothing in the rule is fixed
off the axis, nothing can pick: rings. If the rule has a dial, the dial picks: a count of planes. If the only fixed
thing is the flat page, the flat page picks itself: buds there, ridges or bare skin elsewhere. `t6_necklace.png` is
what a fourth possibility would have to look like.

## 5. Definitions of the test rules (all in `myrules.py`, built from the library's blocks)

"own sheet" = `M.sheet_of(y, z)`; a point on the x-axis has none. "turned right by d" = the sheet's doubled-angle
vector multiplied by (cos 2d, sin 2d) (from +y toward +z). "no sheet yet" = a third carried number d = 0.

- `delay_cov`: carried: a sheet, at first "no sheet yet". Each point is squared (P) about the carried sheet if there
  is one, otherwise about its own sheet; then the carried sheet becomes the point's own sheet if it has one.
- `lag50_cov`, `lag25_cov`: carried sheet, at first none. Before each squaring: if none yet, it becomes the point's
  own sheet; otherwise it moves the share 0.5 (0.25) toward the point's own sheet (`M.blend`). Then P about it.
- `twist`, `twist8`: no memory. P about the point's own sheet turned right by 30 (8) degrees. Not exact on the flat page.
- `delay_twist`: `delay_cov` with the sheet turned right by 30 degrees before it is used. Not exact on the flat page.
- `csheet_flat` / `csheet_own`: P about the sheet of c; for c on the x-axis: about the flat page / the point's own sheet.
- `csheet_twist`: P about the sheet of c turned right by 30 degrees (c on the x-axis: own sheet). Not exact.
- `first1`, `first2`, `first3`, `first5`, `first8`: squarings number 1..k about the flat page, later ones about the
  point's own sheet. `first1` is the scout's `first`.
- `lathe_x`: (x^2 - y^2 - z^2, 2xy, 2xz).
- `own_tol(tau)`, `delay_tol(tau)` (in `t1b_convention.py`): as `own` / `delay_cov`, but a point closer than tau to
  the x-axis counts as having no sheet of its own and gets the flat page.
- `necklace` (in `t6_necklace.py`): the look-up rule of D2.

Flat page (`t8_flatcheck.txt`, 20,000 points each, Mandelbrot / basilica / rabbit / Siegel): 0 / 0 / 0 / 0 for
`first1..8`, `delay_cov`, `lag50_cov`, `lag25_cov`, `csheet_flat`, `csheet_own`, `lathe_x`; the handed rules are
NOT exact (`twist` 702 / 281 / 2715 / 1466, `twist8` 495 / 247 / 1120 / 858) and were used for symmetry tests only.
Leak check for `first1..3` (share of the box inside at 30 / 80 / 200 steps): Mandelbrot 5.84 / 5.55 / 5.45,
4.59 / 4.40 / 4.35, 3.79 / 3.68 / 3.65; basilica and rabbit unchanged from 80 to 200.

## 6. The pictures (all looked at)

- `t2_knife.png`: delay_cov and lag50_cov, cut at 22.5 degrees, 40 and 160 steps; red = flat-set points lost to rounding.
- `t2b_delay_edge.png`: `delay`, flat main body lifted by 1e-9: cream holds (the formula's heart), green bounded off the sheet, red lost, blue a thin band of disagreement.
- `t3_first_cuts.png`: seven cuts of `first`: the flat set with pieces cut away.
- `t4_rings.png`: the band round the x-axis through the period-3 bud, unrolled, ten rules.
- `t5_skin.png`: how the main body's resting point lets go at the skin: lathe (all "going round", circles), one-plane rule (a thin strip), along (four arms).
- `t6_necklace.png`: the hand-built necklace solid: two eye positions, a close-up, three cuts.
- `t7_forget_mandel.png`: Mandelbrot cuts and rough solids for forgetting after 0, 1, 2, 3, 8 squarings and never.
- `t7_forget_julia.png`: Julia sets of `first1..3` and `along`, rough blocks, 28 steps, one eye position. Seen: `first1..3`: basilica and San Marco with ribs and with buds at top and bottom only; rabbit and Siegel disc one lump with swirls and holes; nothing like `along`'s buds all round. None of them is a candidate.
- Also looked at: the scout's `out/r21/me/follow-mandel-quick.png` and `follow-julia-quick.png`.

## 7. What went wrong on the way, and what is not done

- I expected `delay_cov` to be exactly spun on the computer. It is not (K1). The reason, rounding on a knife edge, is itself a finding.
- First test of the `delay` formula compared it with "the orbit stays bounded". Wrong test: the lift can grow and the orbit still stay bounded off the sheet (the green region). The right test is "returns to the sheet"; 5,300 of 143,396 points still disagree, in a band next to the formula's line.
- First measurement of the growth factor was made in the flat page with a lift of 1e-11 and gave 2|zeta| every time: the library's dead zone (K3). Redone in the sheet at 22.5 degrees. Several fast-shrinking cases could not be fitted (printed as nan).
- First version of `t3b_outside.py` kept dead orbits and ran past 10 minutes; stopped and rewritten.
- Two of my "outside the flat set" test constants (0.3+0.5i, 0.33+0.07i) were in fact inside; relabelled, others added.
- The handed test rule `twist` (30 degrees) has an almost empty rabbit (0.03 % of the box), a weak test of mirror symmetry; `twist8` was added.
- First necklace table found 3 limbs instead of 12 (rim pixels have no period); fixed by giving rim pixels the nearest body.
- Not proved: that the lathe has no fat set of bounded orbits beyond the basin of the flat cycle (F4, only "no attracting cycle off the sheet" is proved); the general size of E in S4; D4 for rules with creases.
- Not done: close-ups and second eye positions of the Julia sets of `first1..3` (they are not candidates); the necklace beyond one level; the skin test (D4) for rules with memory.
