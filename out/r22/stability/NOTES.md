# Round 22, section "stability": the fine print of each step

Everything here is in `out/r22/stability/`. Marks: **[M]** measured (a number I computed), **[S]** seen (in a picture
I opened), **[R]** reasoned. Rules: `oneplane`, `along`, `lathe`, `away` of the bench, through `out/r21/lib/mem.py`.
No file outside this folder was written. No browser, no `src/`.

## 0. The short version

1. **A bud is the next body seen through the step. Its shape is the step's stretch at that place, and nothing else.**
   [M] Left body of the basilica under `along`: the buds on the flat and upright page are 0.91 long : thick (round),
   the two beside them at 27 and 63 degrees 1.47 (the step stretches 1.55 times more round the axis than along it
   there), the one on the diagonal page 2.84 (step: 2.92). `away`'s extra buds at 35.5 and 54.5 degrees: 4.46 (step 4.24).
2. **One formula gives the thin fins.** [R, then M to 4 digits] Beside a diagonal page `along` stretches the distance
   off the page by (2 cos t - 1) times the stretch inside the page; t = direction of the point seen from 0, counted
   from the +x axis. That is +1 near the right-hand x-axis, 0 at 60 degrees (crushed flat), -1 straight above 0
   (a mirror, shapes kept), -3 on the left-hand x-axis. Beside the flat and the upright page the factor is 1 everywhere.
   [M] The same flat bud put on the flat page and on a diagonal page, generations 1 to 4:
   flat page 0.97, 0.91, 0.92, 0.88 long : thick (one-plane: 0.90, 0.91, 0.93, 0.91);
   diagonal page **0.98, 2.84, 6.76, 19.36** (predicted from the formula 1.00, 2.92, 6.73, 19.61).
   So the thin fins are buds like any others, squeezed once more at every step their orbit takes on the left side
   away from the flat and upright pages.
3. **The brief's sentence "only the one-plane rule keeps angles everywhere" is wrong for small balls.** [M] One-plane
   keeps angles on every sphere round 0 and never turns anything inside out (0 of 400,000 points), but a tiny ball
   comes out a ball only at the flat page. Longest / shortest stretch = (1 + sin^2 L) / cos L, L = how high the point
   stands above the flat page seen from 0: 1.00 on the page, 1.24 at 22.5 degrees, 2.12 at 45, 4.84 at 67.5, without
   limit straight above 0 (measured values; the formula gives the same). In the cube -1.5..1.5 one-plane keeps shapes
   (ratio under 1.25) in 32 % of space; `along` in 21 %.
4. **`along` is the lathe with a wobble, not one-plane with more buds.** [M] Seen from 0, the image of a point under
   `along` is never more than 36.6 degrees from its image under the lathe (median 10.8); from its image under
   one-plane it is up to 179.9 degrees (median 34.6; on the left half 86). On all four pages `along` IS the lathe.
   [M] Rabbit: 68.5 % of along's solid is also inside the lathe's solid, 27.0 % inside one-plane's; one-plane's rabbit
   lies 99.6 % inside along's and 99.1 % inside the lathe's. Volumes (random points of 120,000 inside): along 7,915,
   lathe 7,250, one-plane 2,147. Same numbers at 60 and at 150 steps.
5. **`along` has no cycle off the flat page for any c tried, attracting or not.** [M] 150,000 random starts, 400 steps,
   basilica, San Marco, c = -1 + 0.03i, + 0.1i, + 0.2i, rabbit: every bounded orbit (3,347 to 9,948 of them) ends on
   the flat picture's own cycle; none on another cycle of length up to 64. The rabbit's lump is therefore not a second
   attractor: it is the catchment of the flat three-cycle, 3.6 times the size it has under one-plane.
6. **At the flat cycles themselves `along`, `away` and one-plane cannot be told apart.** [M] The pull or push straight
   off the page equals the pull or push inside the page to four digits at every cycle point and both fixed points
   of all six c. Only the lathe differs (it pulls off-page points IN toward the rabbit's pinch point, 0.553 a step,
   while pushing in-page points away, 1.107). So nothing near the page explains the lump; it is made far from the page.

## 1. Files

| file | what |
|---|---|
| `stab.py` | shared tools: the 3 x 3 matrix of one step by central differences, the three stretches, handedness, kinds |
| `zones.py` | a cut coloured by kind with the solid's outline |
| `t1_onestep.py` -> `t1_onestep.txt` | tool checks; share of space by kind; the winding near the x-axis; where the inside-out border lies |
| `t2_sheet.py` -> `own-zones-{basilica,rabbit,siegel}.png`, `t2_*.txt` | my contact sheets: 4 rules x 9 cuts (across; along pages 0, 11.25, 22.5, 33.75, 45, 90) |
| `t3_cycles.py` -> `t3_cycles.txt` | pull / push at every flat cycle point and fixed point, in the page and off it; sideways drift beside each page |
| `t4_ends.py` -> `t4_ends.txt` | where bounded orbits end; search for cycles off the page; along against lathe and one-plane as maps |
| `t5_buds.py` -> `t5_buds.txt` | first buds of the middle body against the step's stretch (the "outward" width there runs into the body: ignore it, use "along x" and "round the axis") |
| `t6_fins.py` -> `t6_fins.txt`, `own-fins.png` | the formula check; zoomed cuts; orbit traces of thin pieces (the circle x = -1, 0.25 grazes the flat disc's pinch point: its traces prove nothing, see section 6) |
| `t7_lens.py` -> `t7_lens.txt` | the buds round the left body; rabbit overlap of solids; reach off the page above cycle and pinch points |
| `t8_siegel.py` -> `t8_siegel.txt` | Siegel disc and San Marco: how fast orbits sink to the page / the axis |
| `t9_deeper.py` -> `t9_deeper.txt` | the same flat bud on the flat page and on a diagonal page, generations 1 to 4 |
| `user_picture.py` -> **`keeps-shapes.png`** | picture 1 for the user |
| `rabbit_pages.py` -> **`rabbit-pages.png`** | picture 2 for the user |

Kinds used in every map: keeps shapes = longest / shortest stretch under 1.25 and handedness kept; squeezes = under 3;
squeezes hard = 3 or more; inside out = handedness reversed (whatever the squeeze).

## 2. One step of each rule under the glass [M, `t1_onestep.txt`]

Tool checks: lathe ratio = r / |x| to 2.7e-10, inside out exactly where x < 0 (its determinant is 8 x r^2);
all four rules square the length to 1e-15.

Share of the cube -1.5..1.5 (400,000 random points):

| rule | keeps shapes | squeezes | squeezes hard | inside out | median ratio |
|---|---|---|---|---|---|
| one-plane | 32.4 % | 55.5 % | 12.1 % | 0.0 % | 1.55 |
| along | 21.4 % | 22.2 % | 12.0 % | 44.4 % | 1.70 |
| lathe | 7.4 % | 29.1 % | 13.5 % | 50.0 % | 1.83 |
| away | 23.7 % | 32.2 % | 37.5 % | 6.7 % | 2.48 |

(44.4 % for along agrees with round 21's checker.)

Where the kinds lie:
- **one-plane**: by height above the flat page seen from 0 only. Keeps shapes in the double wedge within about 21
  degrees of the flat page, squeezes above, crushes on the line straight above and below 0 (the upright axis).
  A tiny ball comes out as an egg pointing away from 0 (outward stretch 2r, both sideways stretches smaller and equal).
- **along**: within 5 degrees of the flat and the upright page 100 % keeps shapes, both halves. **Left half (x < 0):
  inside out everywhere more than 15 to 21 degrees from those two pages** (border at 15.0 degrees near the axis,
  15.9 at distance 0.62 for x = -0.8, 20.4 at x = -0.1, 22.5 at x = 0). Right half: exact near the axis (ratio 1.00,
  turn passed on unchanged), inside out only far from the axis round the diagonals (x = 0.1: 25 to 65 degrees at
  distance 0.62; x = 0.4: only beyond distance 1; x >= 0.8: nowhere in the box).
- **lathe**: inside out on the whole left half; crushes on the plane x = 0 (ratio r / |x|).
- **away**: never inside out on the left half; squeezes up to 5 to 1 there; inside out only in a sliver round the
  diagonals on the right.

The turn round the x-axis close to the left-hand axis (x = -0.6, 0.001 off the axis): a point at turn phi goes to
- one-plane: 180 - phi (a mirror; with the half-turn inside the page this keeps handedness);
- lathe: phi + 180;
- along: phi + 180 - sin(4 phi)/2 [radians]: 0 -> 180, 15 -> 170.2, 22.5 -> 173.9, 45 -> 225, 90 -> 270. Slope
  1 - 2 cos(4 phi): -1 on the flat and upright page (as one-plane), 0 at 15 degrees (crushed: ratio 1.6 million),
  +1 at 22.5 (shapes kept, mirrored), **+3 on the diagonal** (ratio 3.00, inside out);
- away: 180 - 3 phi + sin(4 phi)/2: slope -1 to -5 (ratio 5.00 on the diagonal), never inside out.
So near the left axis `along` goes once round WITH the point like the lathe, with four pleats where it runs
backward like one-plane; `away` goes three times round against it.

## 3. The four pages, and what a bud's shape is

**Kept pages.** [R] The pages at 0, 45, 90, 135 degrees are mirror planes of `along`, so with c on the x-axis the
orbit keeps all four, and on each of them `along` is plain complex squaring (the point lies in the page it is squared
in). [S] `own-zones-basilica.png`: the cut of along's basilica along the page at 45 and at 90 degrees is the flat
basilica, outline for outline. So for c on the x-axis `along` shows the flat picture four times: that is its eight
buds per circle. With c off the x-axis only the flat page is kept (c's own page).

**Beside the pages.** [M, `t3_cycles.txt`, last block] Flat-inside points of the basilica put on a page and turned
0.5 degree off it; median distance from the page after 1 to 6 steps:
along, flat page 0.53, 0.69, 1.21, 1.98, 2.86, 3.84; upright page the same (3.87 after 6);
**diagonal page 1.50, 4.50, 6.50, 18.0, 40.2, 39.3**: thrown off within four steps.

**The formula.** [R] Where a point lies in the page it is squared in, and that page turns p times as fast as the
point when the point moves round the axis, the stretch off the page divided by the stretch in the page is
**1 - p (1 - cos t)**, t = direction of the point from the +x axis seen from 0.
[M] p = 0 (flat and upright page of along, away, one-plane): 1.0000 at eight directions. p = 2 (along's diagonal
page): measured ratio = 2 cos t - 1 to 4 digits at eight directions (`t6_fins.txt` block 1). p = 1 (lathe): cos t,
i.e. the lathe's r / |x| measured in section 2.
Consequences [R]:
- only p = 0 keeps a bud round wherever its orbit goes; that is a page that stands still while the point crosses it;
- p = 2 gives a factor between +1 and -3: thin on the left side, and inside out there;
- p = 1 gives a factor between -1 and 1: the bud is stretched round the axis (rib, ring).
- If a rule is "one-plane about a page that depends smoothly on the point's turn", and the page does not wind
  against the point, then between two pages that stand still (p = 0) the page must overtake the point somewhere, and
  where it does there is a page with p >= 1 on which the point lies in its own page: buds exist there and are not
  round. This is why `along`'s extra buds cost fins. NOT checked beyond along / lathe / one-plane. `away` escapes this
  argument (its page winds against the point, so its only own-page places are the flat and upright pages, p = 0)
  and pays elsewhere: its buds at 35.5 and 54.5 degrees on the left body are places that are NOT in their own page
  but land on the flat or upright page after one step, 4.46 to 1 [M].

**Buds round the left body** (the body round x = -1; circle through the bud middles, x = -1.0463, 0.3075 from
the axis; 200 steps) [M, `t7_lens.txt`]:

| rule | bud at turn | thick round the axis | long along x | long : thick | step there: round the axis / along x | where its image lies |
|---|---|---|---|---|---|---|
| along | 0 and 90 | 0.0672 | 0.0614 | 0.91 | 2.181 / 2.181, handedness kept | on the flat / upright page |
| along | 26.9 and 63.1 | 0.0409 | 0.0603 | 1.47 | 3.372 / 2.180, inside out | 1.0 degree from the flat / upright page |
| along | 45 | 0.0216 | 0.0614 | 2.84 | 6.366 / 2.181, inside out | on the diagonal page |
| along | 6.3 either side of 0 and 90 | 0.0002 | 0.0003 | hair | 1.77 / 2.18 | 6.2 degrees from a page |
| one-plane | 0 (and 180) | 0.0687 | 0.0614 | 0.89 | 2.181 / 2.181 | on the flat page |
| away | 0 and 90 | 0.0571 | 0.0614 | 1.08 | 2.181 / 2.181 | on the flat / upright page |
| away | 35.5 and 54.5 | 0.0144 | 0.0642 | 4.46 | 9.187 / 2.166 | 0.03 degree from the flat / upright page |

So round the left body `along` has 4 round buds and 12 lens-shaped ones (plus 8 hairs); one-plane 2 round buds;
away 4 round and 8 thin. [R] The buds at 26.9 / 63.1 are the other solutions of "one step puts this point on the
flat (upright) page": phi = sin(4 phi)/2 gives 27.1 degrees close to the axis.
Round the MIDDLE body (x = 0) all eight of along's buds are round at their middle, 0.1356 to 0.1378 round the axis
against 0.1332 along x [M, `t5_buds.txt`]: straight above 0 the diagonal factor is -1, a mirror that keeps shapes.
[S, `own-fins.png`] the four on the flat and upright page carry many small buds; the four diagonal ones are nearly
bare (one small bud at the tip).

**Deeper generations** [M, `t9_deeper.txt`; long = along x, thick = across the page, 300 steps]:

| flat bud (middle) | generation | along, flat page | along, diagonal page | predicted (product of 2 cos t - 1) | one-plane, flat page |
|---|---|---|---|---|---|
| (0, 0.6436) top of the middle body | 1 | 0.97 | 0.98 | 1.00 | 0.90 |
| (-1.0462, 0.3076) on the left body | 2 | 0.91 | 2.84 | 2.92 | 0.91 |
| (-0.3639, 0.4226) middle body, left side | 3 | 0.92 | 6.76 | 6.73 | 0.93 |
| (0.3639, 0.4226) middle body, right side | 3 | 0.93 | 0.92 | 0.89 | 0.93 |
| (-0.8366, 0.2526) | 4 | 0.88 | 19.36 | 19.61 | 0.91 |
| (-1.1815, 0.1789) | 4 | 0.92 | 2.75 | 2.65 | 0.94 |

**What the thin fins are, in orbits.** The brief's guess ("points that fall exactly into one of the four pages after
some steps") is right for buds AND fins alike; what separates them is which page and where:
falling into the flat or upright page and staying there: round at every generation (0.88 to 0.97);
living on a diagonal page, or landing on a page from a place that is not in its own page: thinner by the step's
factor each time the orbit is on the left side (2.8, 6.8, 19.4 to 1 by generation 4, 0.0017 thick).
[S, `own-fins.png`] the cut across x = -0.3: the skin is smooth where it crosses the green stripes and scalloped in
the purple; across x = -1.047: four round buds in the green, twelve leaning lenses in the purple.

## 4. The flat cycles seen from off the page [M, `t3_cycles.txt`]

Test: a point 1e-3 and 1e-5 from the cycle point, in the page and straight off it; one full turn of the cycle;
distance afterwards / distance before. For cycles through 0 the pull is "as the square" and K = distance / eps^2.

| c | spot | in the page | off the page: one-plane, along, away | off the page: lathe |
|---|---|---|---|---|
| basilica | cycle 0 <-> -1 | K = 2 and 4 | K = 2 and 4 (all three) | K = 2 and 4 |
| basilica | pinch point -0.618 | 1.2361 | 1.2361 | 1.2361 |
| basilica | tip 1.618 | 3.2361 | 3.2361 | 3.2361 |
| San Marco | fixed point -0.5 (and the cycle beside it) | 1.0000 (0.9900) | 1.0000 (0.9900) | the same |
| rabbit | three-cycle | K = 4.6 to 4.8, 2.3 to 2.6, 6.9 to 7.0 | K = 4.56, 2.62, 6.88 | K = 2.65, 2.62, **0.105** |
| rabbit | pinch point (-0.276, 0.480) | 1.1073 | 1.1073 | **0.5527** |
| rabbit | tip | 2.7270 | 2.7270 | 2.5527 |
| Siegel | middle of the disc | 1.0000 | 1.0000 | **0.7374** |
| Siegel | tip | 2.8195 | 2.8195 | 2.7374 |
| c = -1 + 0.1i | two-cycle | 0.4000 | 0.4000 | **0.0385** |
| c = -1 + 0.1i | pinch point | 1.2411 | 1.2411 | 1.2379 |
| c = -1 + 0.2i | two-cycle | 0.8000 | 0.8000 | **0.1403** |

Reading: one-plane, along and away pull or push a point off the page exactly as fast as a point in the page, at
every cycle (they agree to the third order at the flat page: along's page there is psi = (8/3) phi^3 [R]). The
lathe pulls off-page points in faster than in-page ones wherever the cycle point is not on the x-axis, and at the
rabbit's pinch point it pulls them IN (0.553) while the page pushes out (1.107): its bodies are welded round the axis there.

**Neutral cases** [M, `t8_siegel.txt`, 30,000 starts]. Siegel disc, median height above the page of the orbits still
inside after 100 / 400 / 1,600 / 6,400 steps: one-plane 0.076 / 0.036 / 0.018 / 0.0083; along 0.0014 / 0.00086 /
0.00041 / 0.00021; lathe 1e-24 / 1e-93 / 0 / 0. So one-plane and along do pull toward the page there, but ever more
weakly as the point comes close (four times the steps, half the height), along from about 40 times nearer; the lathe
pulls by a fixed share each step. San Marco: distance from the x-axis falls 8-fold for 4 times the steps, all three rules.

**Cycles off the page** [M, `t4_ends.txt`, 150,000 starts, 400 steps, then a test for repeats up to length 64]:

| c | bounded: one-plane | along | lathe | away | ends |
|---|---|---|---|---|---|
| basilica | 4,439 | 4,001 | 4,854 | 4,197 | 100.0 % on the flat cycle, all four rules |
| c = -1 + 0.03i | 4,441 | 3,963 | 4,795 | 4,102 | 100.0 % flat cycle |
| c = -1 + 0.1i | 4,149 | 3,778 | 4,436 | 3,610 | 100.0 % flat cycle |
| c = -1 + 0.2i | 2,886 | 3,347 | 3,607 | 2,039 | 100.0 % flat cycle; **away: 95.6 %, the other 4.4 % never settle, at height 0.04 to 0.10** |
| rabbit | 2,746 | **9,948** | 9,052 | 2,889 | 100.0 % flat cycle, all four rules |
| San Marco | 9,664 | 8,646 | 9,834 | 8,586 | no repeat (slow sink to the fixed point on the axis) |
| Siegel | 7,317 | 9,947 | 10,106 | 177 | no repeat; sinking to the page as above |

No orbit of `along` ended on a cycle off the flat page, or on any cycle but the flat one. (A repelling cycle off the
page cannot be found this way; none attracting exists in these seven sets at this sampling.)

## 5. The lump, in numbers [M, `t7_lens.txt`; S, `own-zones-rabbit.png`, `rabbit-pages.png`]

- Volume of the rabbit: along 3.6 to 3.7 times one-plane's, 1.1 times the lathe's.
- Overlap: section 0, point 4. One-plane's rabbit is the common core of all three.
- [S] Cut along pages turned 11, 22, 34 degrees: the lathe's and along's cuts still show a whole rabbit (along's
  fatter and frayed, bodies joined); one-plane's cut has fallen into separate smooth blobs at 11 degrees.
- Reach straight off the page (300 steps), above the three cycle points / above the pinch point:
  one-plane 0.236, 0.401, 0.161 / 0.000; along 0.489, 0.403, 0.514 / 0.000; lathe 0.308, 0.403, 0.501 / 0.564;
  away 0.162, 0.403, 0.103 / 0.000. So along's bodies stand two to three times as high off the page as one-plane's
  at two of the three cycle points (at c's own point as high as the lathe's), but straight above the pinch point
  along has nothing, like one-plane: the lump is not joined there. Where it IS joined I did not locate (section `lump`).
- **Negative finding.** The kind of the FIRST step does not single out the lump: of the part of along's rabbit that
  one-plane does not have (73 % of it), 19 / 25 / 11 / 44.5 % starts in keeps / squeezes / hard / inside out, against
  21 / 22 / 12 / 44 % for space as a whole. So "the lump is the inside-out zone" would be false.
- [R] Why the two rules part company off the x-axis: the eight-bud picture needs all four pages kept, which needs c on
  the x-axis (section 3). With c off it, three of the four pages are thrown about by every step while the rule still
  moves points nearly as the lathe does (36.6 degrees at most); what is left is the lathe's behaviour without the
  pages that cut it into beads.

## 6. The two pictures for the user

- `keeps-shapes.png`: the picture the brief asks for. Two rows (Turning plane, along; Sphere inversions, one plane),
  the c = -1 shape, two cuts across the x-axis each (through the middle body; through the buds of the body to its
  left), coloured by what one step does to a tiny ball there, the outline in white, and the shape from the side.
  Three plain sentences per row. Every statement on it: buds round in the green [M], 4 round + 12 seeds [M], 3 / 7 / 19
  times as long as thick [M, on the diagonal page], nearly bare diagonal buds [S], one-plane never inside out [M],
  two places per circle [M], squeezes more and more above the page [M].
- `rabbit-pages.png`: the rabbit sliced along pages turned 0, 11, 22, 34, 45 degrees, lathe / along / one plane,
  one plain sentence per row. "Two thirds of this lump is the lathe's lump" = 68.5 % [M].

Not for the user: `own-zones-*.png`, `own-fins.png` (bench names on them).

## 7. What I did not do, and what could be wrong

- **`away` got the numbers but no pictures of its own** beyond a row on my contact sheets, and its never-settling
  orbits at c = -1 + 0.2i (4.4 %) were not followed.
- **The orbit traces of thin pieces in `t6_fins.txt` (block 3) are not evidence.** I chose the circle x = -1,
  distance 0.25, which passes through the pinch point between the flat disc and its bud, so everything on it is thin
  for that reason. The fin findings rest on `t7_lens.txt` and `t9_deeper.txt` instead.
- The deeper-generation table follows buds that stay ON a diagonal page. The buds of the 27-degree family and their
  children (which hop between pages) were measured at the first generation only (1.47 to 1); that they also thin out
  generation by generation is reasoned from the stretch, not measured.
- "The count of along's buds per body: 8 on the middle body, 16 on the left body" was counted on one circle per
  body, not all over the body.
- Where the rabbit's lump is joined, and what one step does to the three pages that do not hold c, I left to the
  `lump` section; I only measured overlap, reach and ends.
- The "page must overtake" argument in section 3 is reasoned for one family of rules and checked on three members.
- Cuts were made at 60 to 150 steps, bud widths at 200 to 300; rabbit volumes agree at 60 and 150 steps. I did not
  repeat the bud widths at a second step count.
- Positions of orbits were iterated with the library's rule functions in my own loop (`M.stay` returns counts only).
- `t5_buds.txt`: the column "outward" (0.5426) is the bud plus the body behind it. Do not quote it.
- Time: about 100 minutes.
