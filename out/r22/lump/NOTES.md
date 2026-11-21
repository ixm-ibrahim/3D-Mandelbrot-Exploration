# Round 22, section "lump": where do the points of the rabbit's lump go? (Q2)

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.
Paths are relative to the project root; everything of mine is in `out/r22/lump/`. Rules are the library's
(`out/r21/lib/mem.py`) and the judge's loader (`out/r21/judge/myrules.py`); nothing is re-coded. `M.stay` only
counts steps, so `lumplib.follow` is the same loop handing back the points; it agrees with `M.stay` on 20,000 random
points per rule (0 differ, measured).

## 0. The answer in plain words

1. **All of the lump goes to the flat cycle.** For `along` with the rabbit's c, every orbit that stays ends on the
   three-point cycle of the flat picture (0, c, c^2 + c), in the flat page. There is no second cycle, no closed
   curve and no cloud off the page. The same holds for `oneplane`, `alongmem.c_wake1` and `lathe`, and for
   c = -1 + 0.03i, 0.1i, 0.2i (flat two-point cycle). **Measured.** For the Siegel disc the flat picture has no
   cycle; there every orbit that stays comes down to the flat page and goes round the closed curves of the flat
   disc. **Measured.**
2. **So the lump is not a different thing from the clean bodies. It is the same bodies, fat, pressed wall to wall.**
   Colour each point by which of the three cycle points it sits on after 120 steps: each body is one colour, and
   bodies that touch have different colours. Under `oneplane` bodies touch at single points (0.1 % of all skin
   faces lie between two bodies); under `along` 14.4 % of the skin is a wall between two bodies (lathe 14.5 %,
   `c_wake1` 0.4 %). **Measured, seen** (`lump-bodies.png`).
3. **Why they press together: off the flat page `along` brings points DOWN toward the page where the flat picture
   needs them pushed AWAY.** At the point where the three main bodies meet (the flat rule pushes everything away
   from it, 1.107 times per step), `oneplane` lifts a point above it 1.02 to 1.11 times per step at every height,
   so the space over the meeting point empties. `along` lifts only close to the page (1.11 at height 0.005), is
   neutral at height 0.075 and brings down above that (0.52 at 0.2, 0.07 at 0.3). At height 0.0754 there is a
   resting place: a point that one step puts back on itself. Points above the meeting point are drawn to that
   height, hover, slide sideways into one of the bodies and stay. The space over the meeting point is filled:
   72 to 76 % of a small box round it is inside at every height up to 0.3 (`oneplane`: 66 % at the page, 4 % at
   0.1 to 0.2, 0 % above 0.2). **Measured, seen** (`lump-why.png`).
4. **The reason for the bringing down** (reasoned, with the lathe as the measured limit): a point squared in its own
   page stays in that page, so its height becomes height times 2x (the lathe: exactly -0.55 above the meeting
   point, at every height). A point squared about the flat page has its height multiplied by about 2r, the same
   stretch as inside the page. `along` is the one-plane rule within about 10 degrees of the flat page and close to
   the lathe further up (its squaring page is never more than 14.3 degrees from the point's own page).
5. **The three pages that do not hold c.** `along` squares the points of its four pages (0, 45, 90, 135 degrees)
   inside their page, exactly as the flat rule would. Then c is added. For c = -1 (on the x-axis, in every page)
   the points stay in their page for ever and all four pages show the flat basilica exactly (0 of 14,064 places
   differ). The rabbit's c lies in the flat page only: adding it moves every point of the 45, 90 and 135 degree
   pages out of its page (by 0.527, 0.745, 0.527), and those three cuts are not the flat rabbit (60 %, 75 %, 100 %
   of the flat picture's area differs). **Measured.** So for c off the x-axis only the flat page keeps its points,
   and the gaps of the flat picture exist in that one page only. **Reasoned.**
6. **`c_wake1`'s two loose bodies** are not pieces broken off. Each is a place far from the page (middle
   (0.038, -0.295, +-0.649), heights 0.40 to 1.06) whose points the first step, which is `along`'s, throws straight
   down into the body round c^2 + c (all 7,399 blocks of each land nearest that cycle point, median height 0.089;
   test points land at heights 0.003 to 0.044). From the second step on they are ordinary points of the one-plane
   rabbit. **Measured, seen** (`lump-loose.png`). The flat rule sends two places onto any spot (v and -v); one
   step of `along` sends up to eight onto one spot (onto c^2 + c: two in the page, six off it; `oneplane`: two).
   **Measured.** The loose bodies are such extra places; half of each is turned inside out by that step, so each
   is folded double onto the body it jumps into. **Measured.** Why nothing joins them (reasoned): bodies are
   joined to each other only through the meeting points in the flat page; an extra copy made off the page has only
   scraps of the neighbours at its own copied meeting points (285 of its 7,399 blocks have another colour).
7. **What a rule must NOT do if the rabbit is to stay in separate bodies** (reasoned from 3 to 6, with the measured
   cases behind it):
   - It must not bring points down toward c's page at the places where the flat picture pushes points apart
     (the edge of the flat picture, most visibly the meeting points). There it has to push away off the page at
     least as hard as the flat rule pushes inside the page, **at every height**, not only next to the page.
   - So, off c's page, it must not square a point in its own page or in a page that tips toward the point:
     that makes the height follow 2x and collapses it. (`lathe` and `along` do; `oneplane` does not.)
   - It must not send extra places onto one spot (fold space over), or bodies get copies that hang loose
     (`c_wake1`) and, if the folding is repeated at every step, fill everything in (`along`).

## 1. What was done (scripts in `out/r22/lump/`)

| script | what it does |
|---|---|
| `lumplib.py` | `follow` (M.stay's loop, returning points), `fates` (cycle / page / off-page cycle / curve / cloud, by periodicity to 1e-7 over 128 points after a burn-in, height to 1e-7, and neighbour drift), `route` (which flat cycle point the orbit sits on, first step after which the height stays under 0.02), `solid2` (M.solid with the height upright on the screen), `wrap` |
| `explore1.py`, `explore2.py` | fates on a 3D grid; `explore2.py 56` -> `fates-table-56.json` |
| `measure1.py` | 96^3 grid: bodies by colour, body-against-body faces, height after one squaring, along against one plane by height band -> `measure1.txt`, `measure1-*.json` |
| `measure2.py` | the meeting point: push by height, box shares; resting places off the page (Newton from 4,000 starts); places thrown onto each cycle point (Newton from 3,000 starts); the three pages -> `measure2.txt` |
| `measure3.py` | `c_wake1`'s pieces with gaps of two cells bridged (as round 21's judge did), where one step puts the loose ones; Siegel disc heights over 20,000 steps -> `measure3.txt` |
| `trails1.py` | a few orbits written out step by step |
| `diag1.py` | working sheets of cuts coloured by body: `diag1-rabbit.png`, `diag1-t020.png`, `diag1-siegel.png` |
| `pic_bodies.py`, `pic_why.py`, `pic_loose.py` | the three pictures for the user |

## 2. Numbers (all measured)

**Fates** (`explore2.py 56`: 56^3 grid, x -1.8..1.8, y and z -1.5..1.5, no grid point on z = 0; inside = stays 80
steps; then 600 + 128 steps for the rabbit, 3,000 + 128 for the others).

| c | rule | inside | ends on the flat cycle | anything else |
|---|---|---|---|---|
| rabbit | along | 8,800 | 8,800 (period 3, height under 3e-28) | 0 (2 more leaked after step 80) |
| rabbit | oneplane | 2,372 | 2,372 | 0 |
| rabbit | c_wake1 | 3,622 | 3,622 | 0 |
| rabbit | lathe | 8,004 | 8,004 | 0 |
| -1 + 0.03i | along / oneplane / c_wake1 / lathe | 3,448 / 3,912 / 3,800 / 4,176 | all (period 2) | 0 |
| -1 + 0.1i | the same four | 3,314 / 3,628 / 3,578 / 3,960 | all | 0 |
| -1 + 0.2i | the same four | 2,896 / 2,544 / 2,728 / 3,144 | all | 0 |
| Siegel | along | 8,664 (92 leaked) | no flat cycle: none periodic; neighbour drift -0.006 to +0.016 per step (median -0.0003): closed curves, height median 6.9e-4 after 3,128 steps | 0.1 % (about 9 orbits) have drift over 0.01 |
| Siegel | oneplane / c_wake1 | 6,496 / 7,662 | closed curves, height 1.4e-2 after 3,128 steps and still falling | 0 |
| Siegel | lathe | 8,968 (96 leaked) | exactly on the page (height 0), closed curves | 0 |

On the 96^3 grid (`measure1.py`, 120 steps) every one of along's 44,160 inside points of the rabbit sits within
0.05 of a flat cycle point at step 120 (0 without a colour); the same for the other three rules.

**Siegel disc over 20,000 steps** (`measure3.py`, 2,000 start points at heights 0.05 to 0.6 that stay 300 steps;
median height after 10 / 100 / 1,000 / 20,000 steps): along 1.8e-2 / 1.6e-3 / 5.9e-4 / 1.2e-4, last points keep
0.23 to 0.35 from the centre of the flat disc; oneplane 0.22 / 0.079 / 0.023 / 0.0049, last points 0.07 to 0.08
from the centre (11.5 % within 0.01 of it); c_wake1 0.17 / 0.070 / 0.022 / 0.0046; lathe 2.1e-3 / 3e-24 / 0 / 0.
So `along` drops Siegel points onto the page within tens of steps and they then go round the flat disc's curves;
`oneplane` lets them sink over thousands of steps while they also creep toward the centre of the disc.

**Bodies and walls** (`measure1.py`, 96^3; faces between two inside blocks of different colour, as a share of all
skin faces):

| c | along | oneplane | c_wake1 | lathe |
|---|---|---|---|---|
| rabbit: inside blocks | 44,160 | 12,064 | 18,338 | 40,208 |
| rabbit: wall share | 14.4 % (6,532 faces) | 0.1 % (8) | 0.4 % (46) | 14.5 % (7,140) |
| -1 + 0.03i: inside / walls | 17,548 / 1.5 % | 19,652 / 0.2 % | 19,130 / 0.4 % | 21,164 / 7.5 % |
| -1 + 0.1i | 16,796 / 2.2 % | 18,312 / 0.1 % | 18,076 / 0.3 % | 19,676 / 5.2 % |
| -1 + 0.2i | 14,724 / 2.4 % | 12,700 / 0.0 % | 13,596 / 0.1 % | 15,944 / 2.8 % |

Rabbit, along against oneplane by height band (inside blocks): 0 to 0.05: 4,706 / 3,884; 0.05 to 0.1: 2,416 /
1,648; 0.1 to 0.2: 7,466 / 3,704; 0.2 to 0.4: 15,858 / 2,828; 0.4 to 0.8: 12,588 / 0; above 0.8: 1,126 / 0.
72.8 % of along's rabbit is not in one plane's. For c = -1 + i t the two solids are about the same size (along is
the smaller one at t = 0.03 and 0.1); at t = 0.2 along has 626 blocks above height 0.4 against 32. So for c just
off the x-axis there is no lump yet, only the first walls; it grows as c leaves the axis.

**Height after one squaring / before**, at the 39,454 points of along's rabbit higher than 0.05 (`measure1.py`):
along median 0.63 (shrinks at 71 % of the points), oneplane 1.01 (49 %), lathe 0.49 (74 %). Median of 2|x| there:
0.49; of 2r: 1.46.

**The meeting point** (-0.2763, 0.4797, 0), flat stretch 1.1073 (`measure2.py`). Height after one step / before,
straight above it:

| height | 0.005 | 0.04 | 0.075 | 0.12 | 0.2 | 0.3 | 0.4 | 0.6 |
|---|---|---|---|---|---|---|---|---|
| along | 1.11 | 1.07 | 1.00 | 0.85 | 0.52 | 0.07 | -0.33 | -0.71 |
| oneplane | 1.11 | 1.10 | 1.10 | 1.08 | 1.06 | 1.03 | 1.02 | 1.06 |
| lathe | -0.55 | -0.55 | -0.55 | -0.55 | -0.55 | -0.55 | -0.55 | -0.55 |

Share inside of a box 0.2 wide round the meeting point, by height 0-0.02 / 0.02-0.05 / 0.05-0.1 / 0.1-0.2 /
0.2-0.3: along 72 / 73 / 74 / 76 / 74 %; oneplane 66 / 58 / 34 / 4 / 0 %; lathe 70 / 69 / 68 / 68 / 65 %;
c_wake1 66 / 59 / 39 / 21 / 41 %.

**Resting places off the page** (one step puts the point back on itself; Newton from 4,000 random starts, 1,500 for
the other rules): for along two were found, (-0.2764, 0.4816, +-0.0754), 0.075 from the meeting point; stretches
0.798, 1.100, 1.100 (it draws points in along one direction and lets them go in the other two). They are not
attracting, so no orbit ends there and they do not show in the fates. oneplane: none. lathe: none. (Cycles of
length 2 and more off the page were not searched for; see section 4.)

**Places that one step throws onto a point of the flat cycle** (Newton from 3,000 starts): along: onto 0: four
(two in the page, (-0.657, 0.495, +-0.278) inside out); onto c^2 + c: eight ((+-(0.123, -0.745, 0)) in the page;
(-0.102, 0.576, +-0.477) and (0.058, -0.443, +-0.608) inside out; (0.002, -0.136, +-0.743) right way round);
onto c: only the origin. oneplane: two, one, two, as the flat rule.

**c_wake1's pieces** (`measure3.py`, 160^3, gaps of two cells bridged): 85.51 %, 7.24 %, 7.24 % (round 21's judge:
85.2, 7.2, 7.2). Each loose piece: 7,399 blocks, middle (0.038, -0.295, +-0.649), x -0.16..0.23, y -0.70..0.05,
height 0.40..1.06, gap to the main piece 0.114 (judge: 0.107 to 0.110). Colours of its blocks: 7,114 the colour of
"jumps into the body round c^2 + c", 285 other. After one step of along: middle (-0.626, 0.564, -+0.014), median
height 0.089, largest 0.238, all inside the one-plane rabbit, all nearest c^2 + c. That step turns space inside
out at 50 % and 53 % of the blocks. oneplane and along: one piece.

**The three pages** (`measure2.py` (e), 360 x 260 places, 120 steps; along's cut against the flat picture drawn in
that page): rabbit: 0 degrees 0 differ of 12,994; 45 degrees 7,748; 90 degrees 9,714; 135 degrees 13,064.
Basilica: 0 differ of 14,064 in all four pages. After the squaring the points of each page are still in it (to
1e-15); adding the rabbit's c moves them 0.527 / 0.745 / 0.527 out of the 45 / 90 / 135 degree page.

## 3. Pictures (all opened and read)

For the user (plain labels, checked as a reader who knows no mathematics):

| file | what it shows |
|---|---|
| `lump-bodies.png` | Rabbit under along, one plane, along once: flat cut (identical in all three, three colours of bodies, the three cycle points as white dots), cut straight across through the meeting point, whole shape coloured by body. along: orange and pale areas meet along a straight wall through the meeting point, the solid is a patchwork of the three colours in bands; one plane: two bodies touching at one point, clean coloured bodies; along once: clean fatter bodies, one loose body ringed |
| `lump-why.png` | Side view at the meeting point, two test points followed every third step. One plane: both climb out of the picture. along: one comes down from 0.25, one comes up from 0.035, both to the dashed height 0.075, then slide sideways into the brown and the pale body |
| `lump-loose.png` | along once: cut straight down through both loose bodies with five test points each and where one step puts them (all in the blue body on the page), and the whole shape from the side with the loose bodies ringed |

Working pictures (internal words, not for the user): `diag1-rabbit.png` (cuts at 0, 11.25, 22.5, 45, 90 degrees and
across at x = -0.28 and 0.04, four rules, coloured by body: only the 0 degree cut is the flat rabbit; lathe's cut
across x = 0.04 is nested rings of the three colours, along's is the same broken into arcs), `diag1-t020.png`
(c = -1 + 0.2i: two colours, bodies still separate along the x-axis under all four rules, along's skin ragged off
the page), `diag1-siegel.png` (no colours, since there is no flat cycle; along and lathe ragged and wide,
one plane smooth).

## 4. Not done, limits, what went wrong

- **No picture for the user of the Siegel disc or of c = -1 + i t.** Numbers and working sheets only. For the
  Siegel disc the bodies were not coloured (there is no flat cycle to name a body by), so "pressed wall to wall"
  is measured for the rabbit and c = -1 + i t only; for the Siegel disc it is inferred from the same height
  numbers and the ragged cuts.
- **Trails are drawn over cuts, not over the solid**, and in `lump-why.png` they are side views: the test points
  leave the cut plane (they go a third of the way round the meeting point per step), which is why only every
  third step is drawn. The first version with every step joined was unreadable and was replaced.
- **Off-page cycles of length 2 or more were not searched for.** Only resting places (length 1) were. None can be
  attracting with a catchment bigger than a grid block, since no orbit of the grids ends on one; unstable ones
  like the two resting places probably sit over every meeting point of the rabbit (reasoned, not measured).
- **The walls are not proved to have no thickness.** Blocks of different colour are face neighbours at 0.03, and in
  the 620-pixel cut of `lump-why.png` (0.0011 per pixel) the wall through the meeting point is sharp up to about
  height 0.2, with dark slivers (points that leave) above that. So "wall" is seen at those sizes; thinner gaps
  cannot be excluded.
- **Why the loose bodies are not joined** is reasoned, not measured: I measured what they are and where they go,
  and that the pieces beside them are small (285 blocks), not the path along which a join would have to run.
- The rule in item 7 of section 0 is what follows from these measurements; it is not a proof that nothing else can
  fuse the bodies.
- "Steps until the height stays under 0.02" (`route`'s `land`) did not separate the rules (medians 11, 13, 12; the
  lathe 4) because for this rabbit the last of the height is lost only at the pass through 0. It is in
  `measure1.txt` and is not used in any statement.
- Process: one shell patch of `pic_bodies.py` failed silently (a backslash was mangled, the house trap) and cost a
  two-minute render of the unchanged picture; redone with the Edit tool. My first piece count of `c_wake1` without
  bridging split the rabbit at every meeting point (135 pieces); `measure2.txt` (d) still holds those wrong
  numbers, `measure3.txt` holds the right ones. No run went over about two and a half minutes.
