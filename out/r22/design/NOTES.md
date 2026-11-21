# Round 22, section "design": what the orbits point at (Q4)

Everything of mine is in `out/r22/design/`. Marks: **[M]** measured (a number I computed), **[S]** seen (in a picture
I opened), **[R]** reasoned. All orbits are the library's (`out/r21/lib/mem.py`, `M.stay`). No `src/`, no browser.
Internal names are used freely here; the one picture for the user (`q4-tries.png`) uses the user's words only.

## 0. The short version

No rule here does everything. Six new rules were tried; five fail outright, one fixes the rabbit's lump and loses
the buds. What was gained is a sharper account of what a step must do, with three parts that are proofs.

1. **A bud off the flat page needs places off the page that one step throws ONTO the page, and such places never
   come singly: they form a whole surface, and that surface carries a whole copy of the flat picture.** [R, a proof
   for rules that never turn space inside out; M on five rules] One plane throws two places onto each spot, both in
   the page: no bud off the page is possible, whatever else the rule does. `along` throws 4 (the lump section
   counted 8 onto c^2 + c), `capfold45` 6, `preturn` 8.
2. **The copy on such a surface is exact** [M]: the upright page of `preturn` is the flat picture for the basilica
   AND the rabbit (0 of 14,064 and 0 of 12,994 places differ); the cone of `capfold45` is the flat picture wrapped
   round a cone (0 of 76,328 and 0 of 69,774). Round 21's limit said no second plane can be KEPT and show the flat
   picture when c is off the x-axis. A second surface can be LAID ONTO the flat page instead, and then it does
   show the flat picture for every c. That loophole is real. It does not help: see 3.
3. **A whole extra copy is only harmless if it shares the big bodies and their meeting points with the flat page.**
   [R] For c on the x-axis every page through the x-axis does (all big bodies and all their meeting points lie on
   the x-axis): that is why `along`'s basilica is clean. For the rabbit the middle of the body round 0, c and the
   meeting point are not on one line, and a plane through three such points is the flat page itself. [S] What the
   extra copies do when they share too little: `capfold` (shares only the body round 0): a thicket of spikes and
   loose bits on both shapes; `preturn` (shares the x-axis): fine-looking basilica, ribbed shells on the rabbit.
4. **The rabbit's lump is a matter of where the spine of the pages is.** [M] `along` with its pages hinged on the
   line from 0 to the point where the big bodies meet, instead of on the x-axis (`alonghinge`; for c on the x-axis
   it IS `along`, 0 of 200,000 verdicts differ): above the meeting point the height is multiplied by -1.11 at every
   height (the flat stretch is 1.107; `along`: 1.11 falling to 0.07 at height 0.3), the space above the meeting
   point empties as under one plane (68 / 54 / 21 / 1 / 0 % inside by height band; `along` 71 to 75 % at every
   height), the rabbit's volume falls from 42,808 to 15,168 blocks (one plane 11,668), and the bodies touch at
   single points again [S]. The same for the Siegel disc and a c of the period-4 bud [M, S].
5. **But the buds do not come back.** [M, S] The hinged rabbit's skin is ridges and thin loose arcs. Reason [M]: a
   page through the spine is carried by one step exactly onto the upright plane through c and the meeting point
   (6.7e-16), but the second step scatters it (median 0.45 off the plane it would have to land on). In the basilica
   a point in a page through the spine stays in that page for good and so reaches the x-axis where the flat picture
   says; here it does not, so nothing becomes a clean bud: a ring round the spine through the middle body holds 24
   to 34 thin arcs [M], which the eye reads as ridges [S].
6. **Three conflicts, with their status** (section 3): (a) against "only two places per spot": proof. Shape-keeping
   against extra pages hinged on a line in the flat page: proof for swing-then-square, argument for the rest.
   Buds on buds against separate bodies off the axis: proof for planes, seen so far for curved surfaces.

## 1. Files

| file | what |
|---|---|
| `myrules.py` | the six new rules, defined in full in its docstring: `capfold45`, `capfold30`, `capfold45x2`, `caphump45`, `preturn`, `alonghinge` |
| `dlib.py` | tools: one squaring, lift test, 3D grid, pieces, working sheet |
| `check1.py` -> `check1.txt` | length and flat page; the turn test; places thrown onto the page; flat check and lift test; 30 against 80 steps and pieces (72^3) |
| `check2.py` -> `check2.txt` | `alonghinge`: equals along on the x-axis; flat check, lift test; leak and pieces for four c; the height table above the meeting point; the box above it; where orbits end and walls between bodies |
| `check3.py` -> `check3.txt` | bud counts on the two rings of the buds section (my own census, agrees with theirs); rings round the hinge on the rabbit; is the upright page through the hinge the flat rabbit (no); one and two steps of that page |
| `check4.py` -> `check4.txt` | the copies on `preturn`'s upright page and `capfold45`'s cone against the flat picture; places per spot for ten rules |
| `check5.py` -> `check5.txt` | pieces on a 96^3 grid with gaps of 0, 1, 2 cells bridged, five c, one plane / along / alonghinge |
| `sheet1.py` -> `w-basilica.png`, `w-rabbit.png` | working sheets, all rules: cuts along pages turned 0, 22.5, 45, 90 round the x-axis, two cuts across, solids from two eye positions |
| `sheet2.py` -> `w2-rabbit.png`, `w2-siegel.png`, `w2-t02.png`, `w2-p4.png` | working sheets for the hinge: pages through the HINGE tilted 0, 11.25, 22.5, 45, 90, three cuts across it, three eye positions; one plane, along, alonghinge |
| `close1.py` -> `close-rabbit-alonghinge.png` | the hinged rabbit closer: cuts across the hinge at 30 against 80 steps (red = lost between), pages tilted 33.75 and 67.5, three solids at 60 steps |
| `pic_user.py` -> **`q4-tries.png`** | the picture for the user |

## 2. Checks of the findings I build on [M]

- Bud census (`check3.txt` A), my own ring walker: basilica, ring through the top bud of the middle body: one plane
  2 arcs of 13.4 degrees, along 8 of 12.1, lathe the whole ring; ring through the side bud of the left body: one
  plane 2 of 12.9, along 16 (12.6 x 4, 7.6 x 8, ...). Agrees with the buds section.
- Height multiplier straight above the rabbit's meeting point (`check2.txt` F): one plane 1.11 .. 1.02 .. 1.06, along
  1.11 / 1.07 / 1.00 / 0.85 / 0.52 / 0.07 / -0.33 / -0.71, lathe -0.55 throughout. Agrees with the lump section's table.
- Box above the meeting point (`check2.txt` G): one plane 66 / 59 / 35 / 4 / 0 %, along 71 / 73 / 74 / 75 / 73 %. Agrees.
- Every staying orbit of the rabbit ends on the flat three-cycle, also for `alonghinge` (4,436 of 4,436 blocks of a
  64^3 grid, height at the end under 1.2e-16) (`check2.txt` H). Walls between bodies as a share of the skin: one
  plane 0.4 %, along 13.7 %, alonghinge 5.6 %.
- Along's upright page on the basilica is the flat basilica (0 of 14,064 differ) (`check4.txt` C). Agrees with lump.
- Places one squaring sends onto one spot (`check4.txt` D, five target directions, three in the page and two off
  it): one plane 2 2 2 2 2; lathe 2 2 2 2 2; along 4 4 4 2 2; away 4 4 4 4 4; capfold45 6 everywhere; preturn
  8 8 6 2 2. (The lump section counted 8 onto c^2 + c for along; my targets are other directions.)
- New, and against what the brief's section 3 leaves open: turning a point round the UPRIGHT axis (the line through
  0 square to the flat page) by an angle a turns its one-plane square by 2a, to 6e-16 (`check1.txt` B). That is the
  flat rule's own habit (turn z by a, z^2 turns by 2a). `along`, `lathe`, `away` miss by up to the whole length:
  they single out the x-axis, which the flat rule does not. So for one plane the rabbit is as good a c as -1;
  for the others c = -1 is special because the x-axis holds the meeting points, not because c is "real".

## 3. What a step must do, (a) to (e)

**(a) For a bud to exist at a place off the flat page.**
Some place off the flat page must be thrown onto the flat page by a step (or onto a page that is kept for good).
Argument [R]: every staying orbit ends on the flat picture's cycle (measured for every rule and c so far, here
again for `alonghinge`). A bud that is joined to the rest is joined at a point; joining points are carried to
joining points, in the end to the point where the big bodies meet, which lies in the page. So a joined bud off
the page has a joining point off the page that lands on the page. For a rule that never turns space inside out
this is a proof, and it says more: every body is then carried ONTO a body, so holds a place that lands on 0, and
with two places per spot both are in the page; every body is then cut by the flat page. **One plane's look (buds
only round the flat page) is forced on every rule that throws only two places onto each spot.** For rules that do
fold space the argument stands but is not airtight (a fold can also make a body that is a doubled copy of the top
of another body, sitting on the fold; such a body has no joining point and hangs loose: the two loose bodies of
"along once" are of that kind, by the lump section's measurements).
The places thrown onto the page form surfaces [R: "the height after the step is zero" is one condition on a
direction, which cuts out curves of directions; M: `check1.txt` C, share of directions above the page thrown onto
or below it: one plane 0, along 0.32, lathe 0.50, away 0.17, capfold45 0.057, preturn 0.25]. Each such surface
carries the flat picture, exactly [M, section 0 point 2].

**(b) For it to be round.** The step that lays the surface onto the page must keep shapes there, and so must every
later step on the bud's way (the stability section's law: off-page stretch / in-page stretch = 1 - p (1 - cos t)).
[M] `capfold`'s mirror keeps shapes everywhere and its cone copy is exact. [R, proof] For a rule that first swings
the point round a line in the flat page (to turn m(phi) from turn phi) and then squares in the flat page: keeping
shapes means the swing does not stretch the turn (slope of m is +1 or -1 everywhere), the flat page must stay
where it is (m(0) = 0, m(180) = 180), and over that half-turn a slope of +-1 can only be m = phi. So a swing round
a line in the page that lays a second page onto the flat one MUST squeeze somewhere between the two pages. (It
need not squeeze AT the pages: `preturn`'s swing has slope 1 at the flat and at the upright page and between 2.6
and -0.6 in between.) That the squeeze shows as ribs is seen, not proved. [S] `preturn`: buds of uneven width on
the basilica (6 arcs of 22.4 / 22.4 / 14.9 / 12.6 / 12.6 / 10.4 on the middle ring [M]), ribs on the rabbit. The stability section has the same conclusion for "square about a turned page" by another
argument. Only a fold round the UPRIGHT axis can lay a surface down and keep shapes (the flat page is then a
whole circle in the middle of what stays put); that is `capfold`.

**(c) For it to carry buds itself.** Every body is a small copy of the body round 0, made by the steps that carry
it there; if those keep shapes and the body round 0 has buds all over, so has every bud [R]. The buds on the body
round 0 sit where "square, then go once round the cycle" sends a direction onto the direction of the meeting point
[R]; for buds of every generation the throwing-onto-the-page has to happen again at every step [M, buds section:
along 16 small buds per bud, along once 2]. A rule in which a page is good for one step only gets at most one
generation (along once), and where even the first step does not end on the spine it gets none: thin arcs and
ridges [M, S: `alonghinge`, section 4].

**(d) For the bodies to stay separate when c leaves the x-axis.** At the point where the big bodies meet, a point
lifted off the page must be pushed away as fast as a point in the page, at every height (the lump section). [M] It
is enough that the spine of the pages runs through the meeting point: a point straight above a point of the spine
is then squared in its own page, and its height is multiplied by twice its place on the spine, which at the
meeting point IS the flat stretch (-1.11 against 1.107). `alonghinge`: lump gone for the rabbit, the Siegel disc
and c = 0.2823 + 0.5301i (period 4): volumes 15,168 / 17,790 / 10,296 blocks of 96^3 against along's 42,808 /
43,012 / 76,216 and one plane's 11,668 / 31,584 / 9,368; biggest piece with no bridging 74 % / 99 % / 38 %
(along 99.5 / 99.8 / 99.9: one lump; one plane 62 / 100 / 50: bodies that touch at points count as separate
pieces on a grid); with gaps of two cells bridged everything is one piece (`check5.txt`).

**(e) For the count of buds to come from the power.** Open. In every rule so far a number is written in: 4 pages
(sin 4 phi), 3 (wind, then square), one fold at a hand-set height (`capfold`). [R] The plainest way to get it from
the power, "double the turn round the spine as the angle in the page is doubled", cannot be done: the half of the flat
page on the far side of the spine stands at turn 180, and doubling sends it to turn 360 = 0, onto the near half,
so the flat page would no longer be the flat picture. More generally, for a swing that leaves both halves of the
flat page where they are and treats above and below the page alike, the pages go round an odd number of times
(1: lathe and along; 3: wind, then square; -3: away), never 2. So in this family the count cannot be the power 2. [M] In `capfold` the buds ON the cone do come from the power (the cone holds the
flat picture itself), but where the cone stands is a hand-set number, and the result is not usable anyway.

**Which pull against each other.**

| pair | what happens | proof or seen |
|---|---|---|
| (a) against "two places per spot, no folding" (one plane's cleanness) | no bud off the page at all | proof for rules that never turn space inside out; argument for the others |
| (a) + (b) against pages hinged on a line in the flat page | a second page laid onto the flat one forces a squeeze somewhere between the pages; it shows as fins and ribs | the squeeze: proof for swing-then-square, the stability section's argument for square-about-a-turned-page; that it shows as fins and ribs: seen on along, away, preturn |
| (a) + (c) against (d) | buds of every generation need pages that are kept or laid down again and again; off the x-axis a kept plane cannot show the flat picture (round 21, proof), and a laid-down copy must share the big bodies and their meeting points, which for three points not on a line only the flat page does | proof for planes; seen so far for curved surfaces (capfold's cone, preturn's page) |
| (d) against the x-axis as the spine | the spine has to go through the meeting point, which moves with c | measured on three c |
| (e) against the power 2 | the turn round the spine cannot be doubled without spoiling the flat page; the pages go round an odd number of times | reasoned (two lines) for swings round a line in the flat page, agrees with all rules built so far; open for other kinds of rule |

## 4. The six rules, plainly

Definitions in full: docstring of `myrules.py`. All six: length squared to 1e-14, flat check 0 of 20,000 differing
verdicts for the Mandelbrot set, basilica, rabbit and Siegel disc, lift test passed (2,920 of 2,920 and 2,716 of
2,716 flat-inside points lifted by a millionth still inside) (`check1.txt` A, D; `check2.txt` D). None is a film.

| rule | idea | basilica | rabbit | verdict |
|---|---|---|---|---|
| `capfold45` | keep the flat rule's turn habit; mirror the caps above 45 degrees in their rim (keeps shapes), then one-plane square: lays two cones onto the page | [S] upright cut is a ragged tree to the edge of the frame, solid a spiky shell. [M] ring through the top bud: 120 arcs; dust 3.4 % | [S] ragged lump with clouds of dust in the cuts at 22.5 and 45 degrees. [M] 22.6 % of the 30-step solid gone at 80 steps, dust 16.8 % | fails: spikes, dust, leaks |
| `capfold30` | the same, fold at 30 degrees | [S] upright cut nearly filled, ribbed shell with spikes. [M] 12 arcs, two of 155 degrees | [S] ragged lump. [M] 9.4 % lost 30 -> 80, dust 3.7 % | fails |
| `capfold45x2` | the same mirror twice (the upright axis is then sent to itself, not to the opposite side) | as capfold45 [S]; 28 arcs [M] | as capfold45; 22.7 % lost, dust 17.4 % [M] | fails |
| `caphump45` | the fold made smooth (no crease; keeps shapes near the page only) | [S] one plane's basilica with long needles; [M] 16 arcs, 14 of them about 2 degrees wide | [S] one plane's rabbit with needles; [M] 20.1 % lost 30 -> 80 | fails: needles (shards), leaks |
| `preturn` | swing the upright half-page onto the flat page round the x-axis, then one-plane square | [S] looks like along at first sight: buds in the cuts at 45 and 90, buds all over the solid; [M] 6 buds of uneven width on the middle ring, 10 on the left ring; 0.1 % lost | [S] upright cut IS a flat rabbit [M: 0 of 12,994 differ]; between the pages ribbed shells, arcs in the cut across; [M] biggest piece 43 % of a 72^3 grid, dust 7.4 % | fails on the rabbit: ribs and loose shells |
| `alonghinge` | along with the spine through the meeting point | IS along [M: 0 of 200,000 differ for c = -1, -0.75, -1.7549, 0.2] | [M, S] no lump; bodies touch at single points; skin in ridges with thin loose arcs within one or two grid cells of the body (1.5 % of blocks; 0.8 % lost 30 -> 80); in the cut across the middle body four pairs of lens-shaped buds on thin necks [S] | half: (d) yes, (b) and (c) no |

More on `alonghinge` [M unless marked]:
- The hinge: rabbit -60.1 degrees (meeting point at -0.554 on it), Siegel 42.5, c = -1 + 0.2i -8.2, c = 0.2823 + 0.5301i 89.9.
- Siegel disc: no lump, bowtie in the cut across at the meeting point [S], but the solid is ragged and THINNER than
  one plane's (17,790 against 31,584 blocks) and leaks: 9.2 % of the 30-step solid is gone at 80 steps.
- c = -1 + 0.2i: hardly different from along (the hinge turns 8 degrees; neither has a lump there) [S].
- Rings round the hinge through the middle body of the rabbit: radius 0.46: 24 arcs, 138 degrees inside
  (along 24 arcs, 262 degrees; one plane nothing); radius 0.50: 34 arcs. Many thin arcs, not a few buds.
- The page through the hinge standing upright is NOT the flat rabbit (9,030 places differ; flat picture 12,986).
- **A seam in the definition.** The hinge is a line, and `along` is not the same rule when turned half-way round
  the upright axis (largest difference 36 in `check2.txt` A), so "which end of the hinge points at the meeting
  point" matters. I folded the hinge's turn into -90..90 degrees: the meeting point is on the negative side of the
  hinge when its real part is negative (basilica, rabbit, Siegel), on the positive side otherwise (the period-4 c,
  whose turn is 89.9: it sits right at the seam). Across "meeting point straight above or below 0" the rule jumps.
  Both sides gave separate bodies, but the seam is a fault of the rule as defined.
- Not defined for a c off the flat page (it reads c's flat-page part only): no Mandelbrot solid was made.

## 5. What this says about Q4

A rule would have to, at every step: throw places off the page onto the page (or onto pages that last), in whole
surfaces; keep shapes while doing so; hang those surfaces on a line through the point where the big bodies meet,
which moves with c; and get the number of surfaces out of the doubling. The first two can be had together only
by folding round the upright axis, which gives copies that share nothing but the middle body (thicket). The first
and third can be had together (`alonghinge`), but then the surfaces last one step, and buds need them to last.
For c on the x-axis all of it falls into place by luck of position: the x-axis holds every meeting point of the
row of big bodies, so pages through it last for ever. That is the whole reason `along` is the best so far there,
and the reason it cannot simply be carried to other c.

What the orbits point at, and how far:
- [M] where the spine must be (through the meeting point): the lump is a misplaced spine, not a deep fault;
- [M] that a second page showing the flat picture for every c exists if it is laid onto the flat page, not kept;
- [R] that the next thing to try is a way for the laid-down or hinged pages to come back after the cycle's
  length (three steps for the rabbit) instead of after one step. Near the meeting point the flat rule turns
  everything by a third of a turn and stretches it by 1.107 [M: 119.94 degrees], so three upright planes through
  the meeting point are handed round in a circle there; away from it the flat rule bends planes (a line not through
  0 is squared into a curve), and no rule made of planes through one line can follow that. I did not find a rule
  that does, and the "proof for planes" row above says it cannot be done with planes.
- [R] It may be that "buds of 3D all over, for every c, with an exact flat page, separate bodies and no hand-set
  number" has no solution among rules that square the length and act through pages. That is not proved.

## 6. The two pictures for the user (both opened and read after the last change)

`q4-tries.png`: four rows (one plane; along; new try 1 = the hinged rule; new try 2 = the fold), three tiles each:
the c = -1 shape, the rabbit (rough solids, 60 steps, eye (0.45, 0.5, 1)), and the rabbit cut straight across
through the point where its three big bodies meet (80 steps). One or two plain sentences per row. Words used:
page, book, spine, body, buds, lump, skin, the flat page, the flat picture, cone. [S] one plane: two bodies
touching at one point in the cut; along: one filled mass; hinged: two wedges touching at one point with thin arcs
beside them, the solid in three separate ridged bodies; fold: a bowtie in clouds of specks, spiky solids.

`q4-second-page.png`: `preturn` on the rabbit ("New try 3"): cut along the flat page, cut along the upright page
(the lower half of the flat rabbit, once above and once below: 0 of 12,994 places differ [M]), and the whole shape
from two eye positions (shells and ribs [S]). Three plain sentences. Its last clause ("it brings bodies of its own
instead of adding buds to the first one") is reasoned.

Weak spots a reader may trip on: "spine of the book" leans on the orchestrator's comparison (a book whose spine is
the x-axis) and is not explained again in the picture; the solids are the library's rough blocks; "fold the top and
the bottom of space down onto the flat page" is a loose way of saying what `capfold` does (it mirrors two caps; what
lands exactly on the page is one cone above and one below).

## 7. Not done, and what could be wrong

- Six rules, the limit. Nothing was tried for "pages that come back after the cycle's length".
- `alonghinge`: no Mandelbrot solid (not defined off the flat page); the seam at "meeting point straight above 0"
  was found, not mended; only four c off the x-axis looked at (rabbit, Siegel, -1 + 0.2i, one period-4 c);
  San Marco, the airplane and the dendrite were not drawn (for c on the x-axis left of 1/4 it is along by
  construction; 0 of 200,000 verdicts differ at four such c).
- Cuts at 11.25 and 33.75 degrees round the x-axis were not made for the five failing rules (22.5 was; their
  faults show at 22.5, 45, 90 and across). For `alonghinge` the pages tilted 11.25, 22.5, 33.75, 45, 67.5, 90
  round the HINGE were cut.
- 30 against 80 steps: as block counts for all rules (72^3), as a picture only for the hinged rabbit.
- Two eye positions for all rules on the working sheets, three for the hinged rule; the user picture has one.
- The proofs are sketched in section 3, not written out formally. The (a) argument rests on "every staying orbit
  ends on the flat cycle", which is measured, not proved. The (a)+(c)-against-(d) row is a proof for planes only.
- "Places per spot" in `check4.txt` D counts clusters on a grid of directions (0.25 degree cells, targets 0.4
  degrees wide); it can miss places that lie closer together than about a degree.
- The fold height of `capfold` was tried at 45 and 30 degrees only. Lower or higher might look different; both
  tried are thickets, and the cone copy that causes it is there at any height.
- Bud roundness of `preturn` and `alonghinge` was judged from arc widths and pictures, not measured in three directions.
- `preturn`'s basilica looks close to along's at first sight (buds all over); I did not judge it further (buds on
  buds, fins, close-ups), because its rabbit fails. It is a check of an argument, not a candidate.
- The Siegel disc under `preturn`: the upright page differs from the flat picture at 102 of about 17,300 places
  (120 against 300 steps near a neutral point; not followed up).
- Time: about 45 minutes of wall clock, no run over four minutes.
