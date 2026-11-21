# Round 22, section "buds": how a bud is made, step by step (Q1, Q3)

Every statement is marked **measured** (a number computed here), **seen** (in a picture I opened) or **reasoned**.
All orbits are the library's (`out/r21/lib/mem.py`). Internal names are used freely here; the three pictures for the
user use only the user's words.

## 0. Files

| file | what |
|---|---|
| `budlib.py` | tools: the five rules, `trace` (positions, the page each squaring used, how far the point was from it), `flat_centres`, `arcs` |
| `e1_rings.py` -> `rings.txt` | walk round the x-axis on four rings (basilica and San Marco), five rules: inside arcs and their itineraries |
| `e2_shape.py` -> `shape.txt` | (a) the page-following dial against bud width, (b) bud sizes in three directions against what the steps do to small moves, (c) a comb of fins of `along` traced |
| `d1_across.py` -> `d1-across.png` | diagnostic: cuts across the x-axis through the four rings, five rules |
| `d2_subbuds.py` -> `d2-subbuds.png`, `subbuds.txt` | diagnostic: the big bud cut across its own stalk (buds on a bud) |
| `pictures.py`, `picture_c.py` | the three pictures for the user (below) |

Pictures for the user: `bud-two-steps.png`, `ball-rib-ring.png`, `buds-on-a-bud.png`.

Rules (names here): `lathe`, `oneplane`, `along` (bench); `once` = `alongmem.c_wake1`; `pulled` = `sheet.evc005e70k16`.
Page check (**measured**): "the one-plane square about the page `budlib.page_used` reports" reproduces the library's
step for all five rules to 1.4e-14 (20,000 random points, 3 steps, c = -1 and the rabbit's c).

The bodies of the flat basilica on the x-axis (**reasoned**, standard): middle body -0.618..0.618 (centre 0), left
body -1.272..-0.618 (centre -1), right body 0.618..1.272 (centre 1), small body at the far left -1.507..-1.272
(centre -1.4142). Note for the orchestrator: in `out/r22/me/one-step-ring.png` the test ring lands at x = -1.384,
which is in the SMALL body at the far left, not in the left-hand body as its captions say.

Rings used (bud centres of the flat picture, by the number of steps the centre needs to reach the x-axis):
g1 = top bud of the middle body (0, 0.6436), 1 step; g2 = side bud of the left body (-1.0462, 0.3076), 2 steps;
g3 = slanted bud of the middle body (0.3639, 0.4226), 3 steps; g4 = small bud of the right body (1.1815, 0.1789), 4 steps.
Route: g4 -> g3 -> g2 -> g1 -> small body (-1.4142) -> right body (1) -> middle body (0) -> left body (-1) -> ...

## 1. The census: how many buds on each ring, and how wide (measured, 2,880 places per ring, 80 steps)

Basilica, c = -1. Width in degrees round the x-axis.

| ring | lathe | oneplane | along | once | pulled |
|---|---|---|---|---|---|
| g1 (1 step) | whole ring | 2 x 13.4 | 8 x 12.1 | 8: flat 13.9, slanted 13.1, upright 12.1 | 4: flat 17.9, upright 14.1 |
| g2 (2 steps) | whole ring | 2 x 12.9 | **16**: 4 x 12.6 (flat, upright), 4 x 4.1 (slanted), 8 x 7.6 at 26.9 deg either side of flat and upright | **6**: 2 x 13.9 (flat), 4 x 8.4 at 26.8 deg either side of flat | 4: flat 20.4, upright 6.9 |
| g3 (3 steps) | whole ring | 2 x 8.4 | **16**: 4 x 8.1, 4 x 8.4 (slanted), 8 x 6.6 at 20.1 deg either side | 2 x 8.4 | 4: flat 14.6, upright 8.9 |
| g4 (4 steps) | whole ring | 2 x 8.4 | **16**: 4 x 8.1, 4 x 8.4, 8 x 6.6 at 20.0 deg | 2 x 8.4 | 4: flat 15.4, upright 3.4 |

San Marco, c = -0.75 (**measured**, counts only; I did not look at these in pictures): along 8 / 16 / 16 / 16;
once 8 / 6 / 2 / 4; pulled 12 / 4 / 4 / 4 (on g1: 4 buds plus 8 slivers); oneplane 2 / 2 / 4 / 4 (on g3 and g4 two of
the four "arcs" are the ring passing through a fat body: inside points up to 0.56 from the page). So the same
pattern as the basilica: 8 then 16 for `along`, 8 then 6 then 2 for `once`, 4 for `pulled`.

All of this is **seen** as well in `d1-across.png` (cuts across the x-axis through the four rings).

## 2. Is "a bud sits where the point lies in the page it is squared in" the whole story?

**For the ring one step from the axis (g1): yes, exactly (measured).** On g1 a point is inside if and only if it is
closer to its first page than a fixed distance: oneplane inside up to 0.0743 / outside from 0.0756; along 0.0653 /
0.0666; pulled 0.0719 / 0.0728. Every arc centre is 0.0000 off its page and lands at x = -1.4142, 0.0000 from the axis.

**For buds two or more steps from the axis: no (measured).** Three things are missing from the one-step law.

1. *The point must lie in its page at EVERY step until it reaches the x-axis, not only the first.* `along` has four
   kept planes (flat, upright, two slanted: eight half-pages). A point in one of them is squared in it and stays in
   it for good (all arc centres at the eight half-pages on g2, g3, g4: 0.0000 off the page at every step). In each
   of the four planes the cut is therefore the whole flat picture, all generations. `once` keeps the eight for ONE
   step and only the flat page after; `oneplane` keeps the flat page; the `lathe` keeps every page.
2. *`along` has buds that are NOT where the point lies in its page: "thrown-in" buds.* Half of along's buds on g2,
   g3, g4 (8 of 16) start between the pages. Example (g2, bud at 26.87 deg): step 1 uses the page at 13.2 deg, the
   point is 0.0726 off it (the most a point on that ring can be is 0.076), and it lands at x = 0.0008, 0.6423 from
   the axis, next to the FLAT half-page (0.0112 off it); step 2 puts it at x = -1.4123, 0.0145 from the axis: inside.
   Cause (**reasoned**, fits the numbers): on the left side (x < 0) one step of `along` sends three directions round
   the x-axis next to each flat or upright half-page: the half-page itself and the directions about 27 degrees on
   either side of it. Near the negative x-axis the turn round the axis goes phi -> 180 + phi - sin(4 phi)/2, which
   comes back to the same half-page where sin(4 phi) = 2 phi, i.e. at 27.15 deg (measured 26.87 at radius 0.31).
   The direction turns back on itself at 15 degrees either side of the flat and upright half-pages (a fold).
   Because inside overlaps: on g2 inside points are up to 0.0760 off their first page, outside ones from 0.0675.
   The thrown-in buds are passed on backwards: the g3 bud at 20.12 deg goes to the g2 thrown-in bud, then beside the
   flat page on g1, then to the axis (itinerary in `rings.txt`).
3. *A fat target forgives.* A point h off its page lands about 2 r h to the side of where the flat picture says. If
   the thing it must land in is fatter than that, it still stays. That is why bodies are full balls and only thin
   targets (a bud one step from a small body) need the point to be in its page.

## 3. What decides whether a bud is a ball, a lens, a rib or a ring

**Law (measured):** what counts is how fast a point leaves its squaring page when it moves sideways (round the axis).
With the dial family psi = phi - a sin(4 phi)/4 (a = 1 is `along`, a = 0 the lathe; the page follows the point the
closer the smaller a), bud width on g1, measured / law "edge where the point is 0.066 off its page":
a = 0.5: 27.9 / 27.6; 0.75: 16.9 / 16.6; 1: 12.1 / 12.1; 1.5: 8.1 / 7.9; 2: 5.9 / 5.9; 3: 4.1 / 3.9; a <= 0.35: the
eight buds have closed into a ring (law: wider than their 45-degree spacing). This is round 21's first-step law
(sheet agent) re-measured on a different family.

- Page stands still under the point (oneplane; along at the flat and upright pages): a point one step to the side
  is one step off its page. Bud as wide as tall: ball.
- Page overtakes the point at twice its speed (along at the slanted pages on g1): a point one step to the side is
  one step BEHIND its page. Ball again, mirrored (**measured**: 12.12 deg at all eight; one step is "mirrored" there).
- Page follows part of the way: lens, then rib; follows all the way: ring (lathe).

**Extension off the ring x = 0 (measured, new).** The same count has to be done for every step on the way to the
axis, and for `along`'s slanted pages it depends on where along the body the bud sits. For a point in a slanted page
at the angle theta from the positive x-axis, one step stretches a sideways move by (2 cos theta - 1) times what it
does to a move within the page (**reasoned**; checked: g2 has cos theta = -0.959, factor 2.92; **measured** 2-step
stretch round the axis x8.19 against x2.81 outward and along x, ratio 2.92). So:

| bud of `along` | size round the axis | outward | along x | steps stretch (outward / round the axis / along x) |
|---|---|---|---|---|
| g2 flat page | 0.068 | 0.076 | 0.062 | 2.81 / 2.81 / 2.81: ball |
| g2 slanted page | **0.022** | 0.076 | 0.062 | 2.81 / **8.19** / 2.81: a thin plate standing in the slanted page |
| g2 thrown-in (26.9 deg) | 0.041 | 0.074 | 0.060 | 2.78 / 4.31 / 2.80: lens, mirrored |
| g3 slanted page | 0.062 | 0.062 | 0.058 | 3.13 / 2.79 / 3.13: ball again (the two distortions on the way cancel to 1.12) |
| g3 thrown-in (20.1 deg) | 0.049 | 0.058 | 0.059 | 3.04 / 3.38 / 3.03: nearly a ball |

At the flat and upright pages every step keeps shapes exactly (largest / smallest stretch 1.00 on g1, g2, g3,
**measured**), so those buds are always balls. At the slanted pages a bud is a ball near x = 0 and on the right, a
thin plate on the left side (three times thinner at g2), and (**reasoned**, not measured) smeared sideways near 60
degrees from the positive x-axis, where 2 cos theta - 1 = 0.

`pulled` (**measured**): near the flat page the page follows the point about a third of the way (4.4 deg for a point
at 15 deg, 11.3 for 30 deg, at radius 0.64), so the flat-page bud is long round the axis: 0.201 against 0.134 along
x on g1 (1.5 to 1), 0.109 against 0.062 on g2, 0.108 against 0.058 on g3. Its upright bud is round on g1 and g3
(largest / smallest 1.07, 1.05) and thin on g2 (0.037 against 0.076) and g4 (3.4 deg).

## 4. Buds ON buds (seen, `d2-subbuds.png`, `buds-on-a-bud.png`; counts measured in section 1)

A bud is a small copy of the body its points are carried to. The big bud of the middle body is carried in one step
to the small body at the far left (x = -1.4142), which sits on the left part of the x-axis.
- `along`: the cut across the big bud's own stalk shows the bud with **16 small buds all round it**, the same
  pattern as the cut across the left body (4 round, 4 thin, 8 thrown-in), and the same for the big bud in the flat,
  the slanted and the upright page. Only the two along x lie in the kept plane the big bud itself lies in; the other
  14 lie in none of the four kept planes (**reasoned** from where the cut plane is: the other three planes do not
  cross the window). So along's buds are bodies of 3D in their own right, with buds round their own stalk, not
  copies of the flat picture standing in planes. (The caption of this row in `buds-on-a-bud.png` was reworded after
  rendering by painting over the text band; `picture_c.py` holds the new wording.)
- `oneplane`: one big bud (flat page), two small buds on it, both in the flat page.
- `once`: big bud in all three directions, each with **two** small buds only (in the flat-page bud left and right
  along x; in the upright bud on the two sides round the axis; in the slanted bud on a slant).
- `pulled`: big bud in the flat page (long round the axis) and upright page, two small buds each in its own page,
  thin loose flakes above and below the upright one; nothing at 45 degrees.

## 5. Why the skin between along's buds is smooth in some places and finned in others

- **Smooth and round** near the flat and upright pages: every step there keeps shapes exactly (**measured**: 1.00),
  so everything is a faithful small copy of a round thing.
- **Thin plates and fins** where a step on the way squeezes one direction. **Measured**: the slanted bud on the left
  body is a plate (section 3). A comb of fins found in the cut at 22.5 degrees (window x -0.40..-0.20, height
  0.34..0.46, 900 x 900, 80 steps): loose inside pieces are 0.12 % of the window; 57 of 92 loose runs are at most 3
  pixels (0.0004) thick. Six of them traced: each is 0.05 to 0.10 off its page in each of its first three steps;
  after the first step it sits on the left side (x = -1.0 to -1.09) at 12 to 18 degrees from the flat half-page,
  which is where the direction round the axis turns back on itself (the fold at 15 degrees, section 2); the first
  two steps together stretch one direction 4.0, 4.7, 11.4, 27.1, 42.5, 43.1 times more than another (against 1.0 to
  2.9 at every bud on the rings).
- **Reasoned, only partly measured**: a fin is a small bud or thrown-in bud whose way to the axis passes a place
  where one step nearly flattens a direction; its copy comes out stretched into a sheet. Two of the six traced had a
  ratio of only 4 to 5 after two steps, so this is support, not proof. The map of where the step flattens is the
  `stability` section's job; I did not make it.

## 6. The two near misses in the same terms

**`once` (Along once, then one plane).** Its first step is along's, so anything ONE step from the x-axis is as in
`along`: eight buds on the ring through the top bud of the middle body (**measured**). Every later step is squared
about the flat page, so anything that needs a second step off the flat page is lost:
- side bodies (g2): of along's 16, six remain: the two in the flat page and the four thrown-in ones that the first
  step puts beside the flat page (26.75 deg either side of it, 8.4 deg wide). The upright ones, the slanted ones
  and the four thrown beside the upright page are gone (**measured**; **seen** in `d1-across.png` and row 3 of
  `bud-two-steps.png`). Round 21's "side bodies bare" was read off cuts at 45 and 90 degrees, which miss these four.
- later generations on the middle body (g3, g4): two buds, the flat-page ones only (**measured**).
- buds on buds: two per bud, not sixteen (**seen**).
So it looks promising because the eye goes to the eight big buds of the middle body, which are all there and round.
What it loses is everything behind them: it is `oneplane` from the second step on.

**`pulled` (Pulled plane).** The page starts flat, weakly held (0.05), and every orbit point pulls it toward its own
page with a pull that grows with its distance from the axis squared. Page of a first step at radius 0.64
(**measured**): point at 0 / 15 / 30 / 45 / 60 / 75 / 90 degrees -> page at 0 / 4.4 / 11.3 / 22.5 / 39.2 / 62.1 / 90.
The point lies in its page only at 0 and 90 degrees: four directions. At 45 degrees it is 22.5 degrees off its page.
Near the flat page the page follows a third of the way (long buds); a point close to the axis cannot pull the page
upright at all (**measured**: the upright point of g4, 0.179 from the axis, is first squared about the FLAT page,
0.1789 off it; the pull 0.179^2 = 0.032 is less than the 0.05 the flat page starts with), which is why the upright
buds get thin and small toward the axis.

## 7. Answers to Q1 and Q3 in plain words (for the judge to check)

Q1. A point stays in the shape only if the place it jumps to stays. A bud off the flat page needs its points to
land on the x-axis after a few jumps, and a point lands where the flat picture says only when it lies in the page it
is squared in. One plane: only the flat page does that. Lathe: every page does, so every bud runs right round: rings.
Along: four pages do it at every step (seen: sixteen buds round the left body, eight round the middle), and on the
left side the jump also throws points from between the pages next to the flat and upright page, which gives eight
more. A bud is a ball when the page stands still under the point or overtakes it; it is a rib when the page
follows the point; it is a ring when the page follows it all the way. The others are smooth off the flat page
because between pages a point is thrown sideways at every step, farther each time.

Q3. Along once looks promising because the first jump is along's: the eight big buds of the middle body need only
that one jump. It loses whatever needs a second jump off the flat page: ten of the sixteen buds round each side
body, the later buds of the middle body, and the small buds all round each big bud (two instead of sixteen).

## 8. For the `design` section: what the orbits say a rule must do

- (a) A bud off the flat page exists where the point meets its squaring page at every step to the axis, or where a
  step throws it next to such a page. Memory that switches the meeting off after n steps keeps n generations only.
- (b) Round: where they meet, the page must stand still or overtake at twice the point's speed, and this must hold
  as a product over all steps to the axis. `along` manages it exactly at the flat and upright pages, only in places
  at the slanted ones.
- (c) Buds on buds all round come for free if the bodies on the left part of the x-axis carry buds all round,
  because every bud is a copy of an axis body.
- The 16-fold richness of `along` on the left side comes from the fold (three directions sent to one). That same
  fold is where shapes get flattened (fins) and where space is turned inside out. In `along`, "unique 3D buds" and
  "fins" have one cause. Whether the same fold makes the rabbit's lump I did not test (section `lump`).

## 8b. The three pictures for the user (all opened and read after the last change)

1. `bud-two-steps.png`: 96 test points round the left-hand body, before / after one jump / after two jumps, and
   the left-hand body, for one plane, along, along once. Shows 2, 16 and 6 buds and why. In the "along once" row the
   pale background of panels 2 and 3 is the one-plane cut, because that is exactly the set from which a point that
   arrives after its first step stays (labelled "from here a point stays").
2. `ball-rib-ring.png`: seven test points and the page each is squared in (first step, ring through the top bud),
   the whole ring cut across, and the middle body, for one plane, the half-way dial (a = 0.5), the lathe, along,
   pulled plane.
3. `buds-on-a-bud.png`: the middle body, and its big bud cut across its own stalk in the flat, slanted and upright
   page, for one plane, along, along once, pulled plane.

Three labels were corrected AFTER rendering by painting over the text band and writing the new text (no pixel of a
computed panel was touched): the fourth column label in picture 1 (it ran off the edge), the first caption of
picture 2 ("one bud" -> "a bud at the flat page only (one on each side of the body)"), the along caption of
picture 3. `pictures.py` and `picture_c.py` hold the corrected wording, so a re-run gives the same pictures.
Known weak spots a reader may trip on: picture 2's caption for the half-way rule calls its buds "ribs" while the
rough solid beside it looks like a mess of ridges; in picture 1 the thin slanted buds of along hold only one test
point each, so they are easy to miss in the first panel.

## 9. Not done

- San Marco: counts only (section 1); no cuts looked at, no bud shapes, no tracing of its arcs.
- "Small balls of test points round each body": not done as balls. Done instead: rings round bud centres, the
  three-direction sizes of buds and finite-difference stretches at bud centres (section 3).
- No rings round the bodies themselves away from bud centres; no fifth generation and later.
- Fins: six points of one comb traced; no map of where the step flattens; the "fin = bud through a fold" reading
  is not proven (section 5).
- The 60-degree smear on the slanted pages is reasoned from the formula, not measured.
- 30 against 80 steps not compared; everything is at 80 steps (cuts in pictures at 60, solids at 40).
- `pulled` is not in `bud-two-steps.png`: its page depends on the orbit's past, so there is no honest "from here a
  point stays" background for its second and third panel.
- No new rules were written (`myrules.py` not needed for this section).
