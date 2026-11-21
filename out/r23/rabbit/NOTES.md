# Round 23, section "rabbit": every door on the shapes that are off the x-axis

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.
All orbits go through `M.stay` of `out/r21/lib/mem.py`. Nothing outside `out/r23/rabbit/` was touched.

## Short answer

1. **No rule in the list gives a rabbit that is both clean and has round bodies growing on it off the flat picture.**
   The rules fall into four kinds (measured, table below; seen, `sheet-doors.png`):
   - *clean but bare*: one plane, pulled plane. Separate bodies meeting at single points, nothing above or below.
   - *lump*: along, cone+. The three bodies at the meeting point are fused into one (one patch on a small ball round
     that point instead of three), volume 3.7 and 4.3 times one plane's.
   - *loose scraps*: two planes (30 % of the volume is loose), Mandelbulb (41 %), b_pcd (47 %), cone- (34 %).
   - *separate bodies with joined bodies on them*: the square pillow, both layouts, and (weakly) along once.
     The pillow is the only kind where the flat bodies stay separate at the meeting point AND there are bodies off
     the flat picture that are all joined to the rest (14 and 10 of them, none loose). But those bodies are
     stretched (long to thick 1.8 and 2.2 in the middle, up to 3), there are a few hundred crumbs, top and bottom
     differ, and c = -1 is fused along the x-axis (the cut at the touching point is 21 % and 28 % of the middle cut;
     one plane and along: 0 %).
2. **The pillow is also the only rule whose rabbit survives when c is turned 10 degrees out of the flat plane**
   (measured: volume 0.79 and 0.70 in 21 and 19 bodies). Under one plane, two planes, along once, pulled plane,
   Mandelbulb, b_pcd and cone- nothing at all survives there; along and cone+ give one lump.
3. **The dendrite (c = i) is empty under every rule** (measured: at 80 steps 0 blocks of 3.3 million stay; cone+ 5 blocks).
   No rule here makes a body where the flat picture has no inside.
4. **N sweep (along for the first N steps, then one plane): no N keeps both.** The rabbit starts to swell at N = 1
   (volume 0.44 -> 0.67, extra bodies above and below, two of them loose) and is a lump with knobs at N = 2
   (0.95) and with ribs from N = 3 (1.15; N = 5: 1.33; every step: 1.62). The eight buds of c = -1 need one more
   "along" step for every body further from the middle: N = 1 gives them to the middle body only, N = 2 also to
   the two side bodies, N = 3 to the next ones and so on (seen in `sheet-n.png`; reasoned: a point beside a side
   body is carried beside the middle body by its first step, so it meets the bud-making step one step later).
   So "eight buds on every body" needs every step, and the rabbit is already spoiled at step 2.
5. **Tries inside the doors: nothing better for the rabbit.** Pillow: making the second layout shape-true beside
   the flat plane changes almost nothing; a layout that is not mirror-symmetric un-fuses c = -1 only partly and makes
   the rabbit's bodies thin and sheared. Hinge: I found one more line that passes the two tests a hinge must pass,
   the unit circle (section 4); it gives thin bare bodies for c = -1 and giant blobs for the rabbit.

## 1. What was run

- Rules (all through `doors.get(<key>)`, file `doors.py`): `oneplane`, `twoplane`, `along` (bench);
  `alongonce` = round 21's `alongmem.c_wake1`; `pulled` = `sheet.evc005e70k16`; `pillow` = round 15's square pillow,
  reference layout `fastpil.REF` = E(1, 2, 0.5); `pillowJ` = the Joukowski layout of the study's
  `needs_from_others`, height 1.3 (the one that "kept the rabbit's bodies apart"); `mandelbulb` (bench);
  `b_pcd` (round 17); `conep`, `conem` = the scout's `cone+`, `cone-` (`out/r23/me/cone.py`).
- Shapes: rabbit, Siegel disc, dendrite c = i, and c = -0.12 + 0.75i turned 10 degrees about the x-axis,
  c = (-0.12, 0.7386, 0.1302).
- Every rule: no NaN on 200,000 random points and 19 special points (origin, poles, axes); length squared to 6e-15
  (measured, `python out/r23/rabbit/doors.py time`).
- Pictures: rough solids 280 x 210 x 180 blocks, 40 steps, eye (0.45, 0.5, 1.0), half-width 1.6, the same for all.
- Numbers (`measure.py`, `numbers.json`, `table.md`): blocks of side 0.02, 170 x 140 x 140, orbit of each block
  centre for 80 steps; the flat plane lies between two layers of blocks, so a film in the flat plane is not counted.
  - *pieces*: connected pieces of the inside (blocks touching by a face, edge or corner), those of 8 blocks or more;
  - *loose share*: volume not in the biggest piece;
  - *thin share*: volume removed by peeling one block off everywhere and growing it back (fins, flakes, shards);
  - *bodies after peeling*: peel two blocks (0.04) off everywhere and count the lumps of 6 blocks or more that are
    left: bodies that only touch at a point or a thin neck come apart, a lump stays one. In brackets: the share
    of the peeled volume in the biggest body;
  - *meeting point* (rabbit only): the fixed point where the three biggest flat bodies meet. A ball of radius 0.03
    round it, 28,800 points on its skin: number of separate patches that stay, and the share of the skin inside.
    3 patches = three bodies meeting at a point; 1 patch = fused. (Radius 0.06 gives the same counts.)
    For the Siegel disc the same test at the point 0 is of no use: after 80 steps the whole small ball still
    counts as inside under every rule (slow escape), so it is left out.
  - *bodies off the flat plane*: peeled bodies lying wholly above or wholly below the flat plane; *joined* if the
    piece they belong to is the biggest piece, else *loose*; *long : thick* from the body's own three widths
    (1 = a ball);
  - *over empty*: share of the volume standing over places where the flat picture is empty;
  - *lift test*: 6,000 flat-inside points lifted by a millionth, share that stays 80 steps.
  Caution (reasoned): the peeling counts as a "body" anything thicker than about 0.1, so a thick piece of a rib
  counts too. Along's 10 "bodies off the flat plane" on the rabbit are parts of its ribs (seen), not buds.

## 2. The table (measured)

Rabbit:

| rule | volume, 30 / 80 steps | loose pieces of 8+ blocks | loose share | thin share | bodies after peeling (biggest holds) | meeting point | bodies off the flat plane | their long : thick, median (range) | lift |
|---|---|---|---|---|---|---|---|---|---|
| one plane | 0.455 / 0.442 | 4 | 0.1 % | 0.8 % | 9 (0.69) | 3 patches, 48 % of the skin | 0 | - | 1.000 |
| two planes | 0.588 / 0.564 | 44 | 30.3 % | 8.6 % | 19 (0.65) | 3 patches, 43 % | 10 (2 joined, 8 loose) | 1.49 (1.31 to 1.64) | 1.000 |
| along | 1.644 / 1.618 | 0 | 0.0 % | 8.3 % | 21 (0.45) | **1 patch, 74 %** | 10 (all joined; rib parts) | 1.84 (1.67 to 2.41) | 1.000 |
| along once | 0.695 / 0.673 | 6 | 14.5 % | 1.2 % | 13 (0.49) | 3 patches, 48 % | 4 (2 joined, 2 loose) | 1.93 (1.59 to 2.27) | 1.000 |
| pulled plane | 0.522 / 0.507 | 0 | 0.0 % | 0.8 % | 9 (0.68) | 3 patches, 57 % | 0 | - | 1.000 |
| square pillow | 0.643 / 0.621 | 34 | 3.1 % | 11.2 % | 23 (0.66) | 3 patches, 39 % | 14 (all joined) | 1.77 (1.50 to 2.96) | 1.000 |
| square pillow, Joukowski layout | 0.581 / 0.565 | 24 | 1.5 % | 9.2 % | 19 (0.69) | 3 patches, 48 % | 10 (all joined) | 2.23 (1.87 to 3.14) | 1.000 |
| Mandelbulb, power 2 | 0.423 / 0.418 | 64 | 41.4 % | 7.9 % | 7 (0.70) | 3 patches, 36 % | 0 | - | 1.000 |
| b_pcd | 0.369 / 0.367 | 72 | 46.6 % | 6.1 % | 13 (0.68) | 3 patches, 14 % | 6 (all loose) | 1.95 (1.92 to 2.17) | 1.000 |
| cone+ | 1.895 / 1.893 | 0 | 0.0 % | 1.9 % | 2 (1.00) | **1 patch, 98 %** | 0 | - | 1.000 |
| cone- | 0.453 / 0.450 | 73 | 34.0 % | 7.4 % | 19 (0.61) | 3 patches, 14 % | 12 (6 joined, 6 loose) | 1.51 (1.27 to 2.23) | 1.000 |

The other three shapes are in `table.md` (same columns). What they add:
- Siegel disc: one plane, along once and pulled plane give one smooth body (1 body after peeling, nothing off the
  flat plane). Bodies off the flat plane, all joined: two planes 6, along 6, pillow 8, pillow J 12, b_pcd 6,
  cone- 22, with long : thick 1.6 to 1.8 in the middle. The Mandelbulb leaks away (0.43 at 30 steps, 0.19 at 80);
  b_pcd leaks too (0.86 -> 0.72); pulled plane 1.56 -> 1.39.
- c turned 10 degrees out of the flat plane: nothing survives 80 steps under one plane, two planes, along once,
  pulled plane, Mandelbulb, b_pcd, cone-. Along: one lump, 1.80. Cone+: one lump, 1.72. Pillow: 0.79 in 21 bodies
  (biggest holds 0.62), 12 off the flat plane, all joined, long : thick 2.2. Pillow J: 0.70 in 19 bodies, 10 off
  the flat plane, all joined, 2.6.
- dendrite: empty under every rule at 80 steps (cone+ keeps 5 blocks; along 0.007 at 30 steps, 0 at 80).

Answers rule by rule for the rabbit, in words (measured unless marked):
- **one plane**: bodies separate, touch at single points, nothing off the flat picture.
- **two planes**: flat bodies separate; 10 bodies off the flat picture, 8 of them loose, fairly round (1.5), in a
  cloud of 44 loose pieces: shards.
- **along**: not separate: fused at the meeting point; one piece, 3.7 times one plane's volume, a quarter of it over
  empty flat picture; ribs and fins (thin share 8 %).
- **along once**: bodies separate at the meeting point; 4 smooth bodies off the flat picture, 2 joined and 2 loose,
  stretched 2 to 1; 14.5 % of the volume loose.
- **pulled plane**: one plane's rabbit, 15 % fatter; nothing off the flat picture.
- **square pillow, both layouts**: bodies separate at the meeting point; 14 / 10 bodies off the flat picture, all
  joined, stretched (1.8 / 2.2, up to 3); 34 / 24 loose pieces and several hundred crumbs (465 / 369 pieces in all).
- **Mandelbulb**: 41 % loose, no bodies off the flat picture: sheets and scraps.
- **b_pcd**: 47 % loose; its 6 bodies off the flat picture are all loose, stretched 2 to 1.
- **cone+**: one lump (98 % of the small ball at the meeting point is inside).
- **cone-**: small flat bodies; 12 bodies off the flat picture, half of them loose; 34 % loose.

## 3. The N sweep (`sheet-n.png`, `cuts-n.png`, `nsweep.json`; rule `doors.get('alongN')`)

`along1` is the same rule as round 21's `alongmem.c_wake1` (same picture and numbers: volume 0.673, 13 bodies).

| N | rabbit volume (80 steps) | rabbit: loose share | rabbit: bodies off the flat picture | rabbit: over empty flat picture | c = -1: buds round the middle body | c = -1: side bodies |
|---|---|---|---|---|---|---|
| 0 (one plane) | 0.442 | 0.1 % | 0 | 0 % | 2 | smooth |
| 1 (along once) | 0.673 | 14.5 % | 4 (2 loose) | 6 % | 8 | smooth |
| 2 | 0.947 | 2.0 % | 12 (6 loose) | 13 % | 8 | eight small bumps |
| 3 | 1.149 | 0.2 % | 16 (all joined) | 17 % | 8 | eight bumps; small buds on the middle body's buds begin |
| 5 | 1.329 | 0.1 % | 10 (all joined) | 20 % | 8 | eight bumps, buds on buds |
| every step (along) | 1.618 | 0.0 % | 10 (rib parts) | 25 % | 8 | eight bumps, buds on buds |

- Buds round the middle body of c = -1 (measured): on circles round the x-axis at x = 0, 1,440 points, exactly 8
  separate arcs stay for every radius from 0.51 to 0.77 at N = 1, 2, 3 (0.49 to 0.77 at N = 5, 0.48 to 0.77 for
  every step); at N = 0 two arcs for radius 0.53 to 0.77.
- Side body (measured + seen): at x = -1 a circle with exactly 8 arcs exists from N = 2 on (radius 0.24) and not at
  N = 0 or 1; in the cut across x = -1 (`cuts-n.png`, second row) the outline is round at N = 0 and 1, has eight
  faint bumps at N = 2 and clear ones from N = 3. In the solids (`sheet-n.png`, top row) the side bodies are bare at
  N = 1, carry buds at N = 2, and the small bodies beyond them carry buds from N = 3.
- Rabbit (seen in `cuts-n.png`, rows 3 and 4, and `sheet-n.png`): N = 0 clean. N = 1: four curved extra bodies above
  and below the middle body, not touching it in the upright cut. N = 2: they have grown together into two shells
  that wrap round the flat bodies. N = 3: in the cut lifted to z = 0.15 the bodies touch along seams. N = 5 and
  every step: one ragged lump.
- The meeting-point test stays at 3 patches for every finite N (measured) and drops to 1 only for "every step".
  That is no sign of health (reasoned): close to the fixed point an orbit stays close for its first N steps, so a
  small enough ball always sees the one-plane picture. The swelling is further out.
- **Verdict (measured + seen): the rabbit starts to swell at N = 1 and no N keeps both.** Eight buds on the
  middle body cost one step, on the side bodies two, on each further generation one more; the rabbit has loose
  extra bodies at one step and is a lump at two.

## 4. Tries inside each door

### Pillow door (two tries; `tries.py`, cuts in `cuts-pillow.png`)

1. **Joukowski layout with the belt made angle-true** (`pilJA`; formula in `tries.py`: the two half-widths of the
   nested ellipses run on two clocks so that beside the belt the layout is the identity to first order).
   Measured: sideways stretch beside the flat plane 2.000 everywhere (plain Joukowski, height 1.3: 1.74 to 2.28;
   height 1.0: 1.52 to 2.56); round trip 7e-8 (bisection), equator against doubling 8e-11, no jump; flat check 0
   of 6,000 differ; lift test 1.000. Seen: the cuts of c = -1 and of the rabbit are nearly the same as `pillowJ`'s.
   c = -1 still fused: cut at the touching point 18.9 % of the middle cut (pillowJ 27.6 %, reference layout 21.4 %).
   Rabbit numbers: see the end of this file. **Not better.**
2. **A layout that is not mirror-symmetric** (`pilT45`, `pilT90`: the direction is turned about the upright axis
   by 45 or 90 degrees, away from the flat plane only, before the pillow is read off; put back untwisted, so no
   upright plane is kept). Flat check 0 of 6,000, lift 1.000. Measured for c = -1: the cut at the touching point
   falls to 10.4 % (45) and 5.9 % (90) of the middle cut, so the row of bodies is less fused but still fused, and
   the middle body is lopsided (above : below 0.89 and 0.52). Seen for the rabbit: in the cut lifted to 0.15 the
   bodies are thin and sheared with loose flecks. What it costs (reasoned): a c on the x-axis no longer gives a
   picture that is the same on both sides of the upright plane. **Worse for the rabbit, half a cure for c = -1.**

### Hinge doors (two tries; cuts in `cuts-hinge.png`)

What a hinge must do (reasoned). A hinge is a curve in the flat plane; the pages are the flat plane swung about
it; a point is squared in a page. For the pages to fit together:
 (i) the flat square must send the hinge into itself, or the pages disagree on the hinge;
 (ii) swinging by a half turn lays the flat plane on itself mirrored in the hinge, and that mirror must commute
 with the flat square, or a page disagrees with itself on its two halves.
Among straight lines only the x-axis passes (i) (a line through 0 at angle a goes to the ray at 2a; any other line
goes to a parabola). Among circles only the unit circle passes (i) (radius r goes to r^2), and it passes (ii):
its mirror is z -> 1 / conj(z). So the flat rule offers exactly two hinges that are the same for every c: **the
x-axis and the unit circle.** Section 2 (a), (b) of the briefing did not have the second one.

1. **The y-axis as hinge** (`alongY`). Fails (i) and (ii) (reasoned). Measured: across its hinge the rule jumps by
   0.50 in the middle, up to 2.04; across the upright plane x = 0 by 1.20 in the middle (along across the x-axis: 0).
   Flat check still 0 of 6,000. Seen: c = -1 a fat lump in the upright cut, the rabbit ragged shards. **Fails.**
2. **The unit circle as hinge** (`alongC`: pages are the balls through the unit circle, the flat plane and the
   unit ball among them at right angles; `twoC`: the nearer of those two, as in "two planes"). Measured: flat
   check 0 of 6,000, lift 1.000, no jump in 200,000 close pairs. Seen: for c = -1 `alongC` gives thin lens bodies
   with NO buds off the flat plane (middle cut 0.31 against one plane's 0.83); for the rabbit both give huge
   blobs that run out of the picture above and below. Why (reasoned): adding c keeps the x-axis where it is when
   c lies on it, but it never keeps the unit circle, so no c has its bodies sitting on this hinge; and every
   ball-shaped page has its own far point at a finite place on the upright axis, so what the flat rule throws out
   is thrown to a finite place and can stay. **Fails, and it was the only other candidate.** So section 2 (a) and
   (b) hold after this attack: the x-axis is the only usable hinge that comes from the flat rule alone.

### Along once (the N sweep): section 3.

## 5. What this says about the user's question (reasoned from the measurements)

- "Bodies everywhere in the flat picture's own pattern" for the rabbit: the only door that shows a hint of it is
  the pillow (joined bodies on separate bodies, also for a c turned out of the flat plane). Its faults are the ones
  round 15 found: stretched knobs, crumbs, lopsided at power 2, and c = -1 fused along the x-axis.
- The hinge doors cannot do it: their one usable hinge is the x-axis, and the rabbit's bodies do not sit on it.
- Along once is not a middle way that can be tuned: its one dial (N) trades the rabbit for the buds step by step.

## 6. Files

- `doors.py` loader and cache; `measure.py`, `numbers.json`, `table.py`, `table.md` the numbers;
  `nsweep.py`, `nsweep.json`, `cutsn.py` the N sweep; `tries.py` the tries; `explore.py` quick cuts;
  `necks.py` the c = -1 neck numbers; `sheets.py` the sheets; `logs/` run logs; `cache/` blocks and depth maps.
- Pictures: `sheet-doors.png` (one row per rule, four shapes; solids at 40 steps; a tile is left empty with the
  words "nothing survives" where under 13 of 3.3 million blocks last 80 steps, because at 40 steps such tiles
  show a haze of single dots that is on its way out), `sheet-n.png` (N sweep, c = -1 and rabbit, solids),
  `cuts-n.png` (N sweep, cuts), `cuts-pillow.png`, `cuts-hinge.png` (the tries, cuts).
- NOT made: solids of the tries (`sheets.py tries` exists but its depth maps were not computed; I stopped that
  run for time). The tries are judged from cuts and block numbers only. No second eye position was drawn; the
  block numbers stand in for it.

## 7. Numbers of the tries on the rabbit (measured, same columns as the table)

| rule | volume, 30 / 80 | loose pieces of 8+ | loose share | thin share | bodies after peeling (biggest holds) | meeting point | bodies off the flat plane | long : thick | lift |
|---|---|---|---|---|---|---|---|---|---|
| pillow J (for comparison) | 0.581 / 0.565 | 24 | 1.5 % | 9.2 % | 19 (0.69) | 3 patches, 48 % | 10 (all joined) | 2.23 | 1.000 |
| pilJA (belt angle-true) | 0.576 / 0.554 | 42 | 28.7 % | 9.4 % | 21 (0.68) | 4 patches, 44 % | 12 (6 joined, 6 loose) | 2.38 (up to 3.28) | 1.000 |
| pilT45 (not mirror-symmetric) | 0.365 / 0.362 | 22 | 2.6 % | 11.6 % | 11 (0.73) | 3 patches, 46 % | 4 (all joined) | 2.85 (up to 3.09) | 1.000 |
| alongC (unit circle as hinge) | 9.73 / 9.64 | 0 | 0.0 % | 0.0 % | 1 (1.00) | 1 patch, 97 % | 0 | - | 1.000 |

- pilJA: same volume and look as pillow J; the jump of the loose share to 29 % is most likely one large body
  counted as loose because its contact with the rest is thinner than a block (reasoned, not checked); the bodies
  off the flat picture are no rounder (2.4 against 2.2).
- pilT45: fewer and more stretched bodies (2.9), a smaller rabbit than one plane's (0.36 against 0.44).
- alongC: one blob filling a third of the whole test box (9.6 of 26.7).
