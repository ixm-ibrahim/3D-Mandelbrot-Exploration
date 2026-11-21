# Round 16 test bench: the basilica first, then the Mandelbrot solid

Stand-alone numpy and scipy. Nothing here touches `src/` or builds a page. Run everything from the project root.

## Files

| file | what it is |
|---|---|
| `rules.py` | the registry: name -> (function, plain label, what was known beforehand) |
| `bench.py` | the iteration, the measures, `stage1(rule)`, the pass / fail lines, one sheet per rule |
| `stage2.py` | `stage2(rule)` (the Mandelbrot solid) and `lights(rule)` (three warning-light Julia sets). Both refuse a rule whose stage 1 has not passed |
| `sheet_user.py` | builds `sheet-for-user.png` from the saved results and tiles |
| `deeper.py` | one close-up deeper than stage 1 goes (`deeper.png`) |
| `results/<rule>.json`, `results/<rule>-stage2.json`, `results/<rule>-lights.json` | every number |
| `tiles/<rule>/*.png`, `sheets/<rule>.png` | pictures; `cache/` holds the solids so that measures can be redone without iterating again |
| `table.txt` | the pass / fail table of all rules, as printed by `bench.py table` |
| `peek.py`, `peek_tiles.py`, `diag_outline.py` | working aids used during calibration |

## How to add a rule and run both stages

1. In `rules.py` write `def myrule(x, y, z): return X, Y, Z` (numpy arrays in, arrays out, no c added) and add a
   line to `RULES`: `'myrule': (myrule, 'Plain name', '')`. The rule must square the length of the point
   (|F(v)| = |v|^2): the escape radius relies on it. `python out/r16/bench/rules.py` prints a check of that.
2. `python out/r16/bench/bench.py stage1 myrule` (about 100 seconds for a closed-form rule, 8 minutes for the
   pillow). It prints the eight lines, writes `results/myrule.json` and `sheets/myrule.png`.
3. Look at `sheets/myrule.png`. The eye is the judge: the numbers were set from pictures, not the other way round.
4. Only if all eight pass: `python out/r16/bench/bench.py stage2 myrule` and `... lights myrule`. They refuse
   otherwise (that is the user's order of work, not a technical limit).
5. `python out/r16/bench/bench.py table` prints every saved rule. Add the name to `ROWS` and `NAMES` in
   `sheet_user.py` and run it for the user's sheet.

Several rules can be run at once as separate processes (one core each; set `OMP_NUM_THREADS=1`).

## What stage 1 measures (basilica, c = (-1, 0, 0), power 2, 60 steps)

The solid is sampled at 321 points a side on [-1.75, 1.75]^3. Close-ups are iterated afresh in smaller boxes
(161 and 129 a side), never enlarged from the big solid. "Worn down" means: take away everything within a given
distance of the skin, grow what is left back by the same distance; what does not come back is "what comes off".

| test | measure | pass when |
|---|---|---|
| J1 flat cut | cut at z = 0 against complex z^2 - 1 on 801 x 801 points, same steps and escape radius | at most 8 points differ |
| J2 touch at a point | at the touching point (-0.618034, 0, 0): the smallest ball whose removal parts the middle body from the left body (box 1.0 wide, 201 a side, face-connected); length of solid on the upright line within 0.2 of the point; how full the cut x = -0.618 is within 0.15 of the axis | ball <= 0.04, length <= 0.004, cut <= 1 % full |
| J3 not spun | share of the solid that changes when it is turned 45 and 22.5 degrees about the x-axis (re-sampled exactly, 161 a side; the smaller of the two); pieces that come off the middle body (worn down by 0.11) and reach at least 300 degrees round the axis | change >= 0.5 % and no such piece |
| J4 buds in more directions, buds on buds | pieces that come off the middle body (worn down by 0.11): how many, how many stand more than 20 degrees off the flat plane, how many of those are round (roundness >= 0.45). Then a close-up of the biggest off-plane one, worn down by 1/18 of the box: what comes off it, how many round, how many off the bud's own plane. Then the same on the biggest of those | >= 2 round off-plane buds; on the bud >= 2 round, >= 1 off its own plane; on the smaller one >= 2 round |
| J5 one piece | share of the solid in the biggest piece when a one-voxel gap is allowed (a body touching at one point shows a sub-voxel gap), and the loose matter in the two close-ups. The strict share (no gap allowed) and the piece count are reported too | >= 99.97 % and loose <= 0.03 % |
| J6 no tear | 200,000 close pairs at steps 1e-4, 1e-5, 1e-6 (as in the scouts), and a hunt: 200,000 segments halved 26 times towards the half where the rule moves more; the jump left over a gap of about 1e-9 | jump < 1e-4 |
| J7 mirrors | share of the solid that changes under z -> -z and under y -> -y | both <= 0.5 % |
| J8 bodies, not streaks | at three sizes (middle body, one bud, a small body on that bud): (a) roundness of what comes off = sqrt(smallest / largest spread of each piece), volume-weighted, 1 = ball; (b) ribs: the outline of the body in a cut across it, found without voxels along 1,440 rays; how far the deepest tenth of the outline lies inside its own slow shape, in per cent of the radius | every roundness >= 0.45 and every rib number <= 0.45 |

Roundness in plain words: a ball is 1, a body twice as long as wide is about 0.5, a blade or a tube is under 0.3.

## Calibration: the rules whose verdict was known

| rule | known beforehand | J1 points | J2 ball / line / cut | J3 turn / rings | J4 round off-plane / on bud / on small body | J5 gap allowed (strict) | J6 jump | J7 mirror | J8 roundness | J8 ribs | bench says |
|---|---|---|---|---|---|---|---|---|---|---|---|
| two planes, nearest | the liked look; tears | 0 | 0.02 / 0.000 / 0.02 % | 6.0 % / 0 | 6 / 8 / 9 | 100.000 (99.99) | 4.3 | 0.00 % | 0.74, 0.71, 0.74 | 0.21, 0.04, 0.05 | fails J6 only |
| one plane | buds only in the flat plane | 0 | 0.02 / 0.000 / 0.02 % | 6.7 % / 0 | 0 / 4 / 5 | 100.000 (99.99) | 4e-9 | 0.00 % | 0.76, 0.72, 0.73 | 0.00, 0.00, 0.00 | fails J4 only |
| quaternion (lathe) | spun | 0 | 0.02 / 0.000 / 0.02 % | 0.0 % / 7 | 0 / 0 / 0 | 100.000 (100.00) | 4e-9 | 0.00 % | 0.07, 0.03, 0.02 | (no bud to cut: tubes) | fails J3, J4, J8 |
| square pillow | joined, lopsided, streaks | 0 | none up to 0.32 / 0.400 / 57 % | 30 % / 1 | 0 / 0 / 0 | 99.999 (99.90) | 1e-8 | 32.5 % | 0.15, 0.23, 0.14 | 0.04, (blades), (blades) | fails J2, J3, J4, J7, J8 |
| Kleinian squaring | flat cut wrong | 33,432 | 0.02 / 0.000 / 0.02 % | 11.0 % / 0 | 0 / 1 / 1 | 99.507 (99.34) | 5e-9 | 0.00 % | 0.73, 0.54, 0.57 | 0.00, 0.00, 0.00 | fails J1, J4, J5 |
| Mandelbulb, power 2 | smear | 0 | 0.02 / 0.000 / 0.02 % | 17.3 % / 0 | 0 / 0 / 3 | 99.943 (98.57) | 3e-7 | 0.00 % | 0.23, 0.27, 0.20 | 0.29, 0.18, 0.07 | fails J4, J5, J8 |
| latitude x 3, longitude x 2 | falls apart (scout) | 0 | 0.02 / 0.000 / 0.02 % | 62 % / 1 | 4 / 0 / 0 | 82.577 (80.98) | 9e-9 | 0.00 % | 0.34, 0.09, 0.06 | 2.43, 2.14, 0.94 | fails J3, J4, J5, J8 |

The brief's four conditions hold: two planes passes J1 to J5, J7, J8 and fails J6; one plane fails J4; the lathe
fails J3; the pillow fails J2 and J7. Kleinian, Mandelbulb and "latitude x 3" were added by the bench so that J1,
J8 and J5 each had a rule known to fail them. The pillow also fails J3 here: a collar round the axis comes off
(the front view shows collars).

Where each threshold sits:
- J1: 0 against 33,432. J2: 0.02 against "none up to 0.32". J6: under 1e-6 against 4.3. J7: 0.00 against 32.5.
  Wide gaps, nothing to argue about.
- J3: 0.0 (lathe) against 6.0 (reference), threshold 0.5, plus "no piece goes round the axis".
- J4: 0 round off-plane buds (one plane) against 6 (reference), threshold 2.
- J5: 82.6 (falls apart) and 99.943 (Mandelbulb: loose shards are visible in its picture) against 100.000;
  threshold 99.97. This one is fine-drawn.
- J8 roundness: at most 0.34 for every rule known to be bad, at least 0.71 for the two good ones; threshold 0.45.
  Anything between 0.34 and 0.71 is NOT decided by calibration: look at the close-ups.
- J8 ribs: 0.21 at most for the two good rules. No rule with a known verdict is ribbed the way "away" is, so the
  threshold (0.45) is half way between the reference (0.21) and the first ribbed rule seen (0.69). It rests on
  the pictures: the bud of "away" cut across is a cog wheel, the reference's is smooth.

## Where a measure had to be changed

1. J8, normals in small boxes (the brief's proposal): built (`skin_relief`, stored as `relief_*`) and dropped
   from the verdict. It gave "away" 0.77, 0.72, 0.68 and the reference 0.80, 0.76, 0.71: no separation, while the
   close-ups plainly show a ribbed melon skin on "away". Shallow ribs on a ball tilt the normals too little.
   Replaced by roundness of what comes off (catches blades, tubes, sheets) and the rib number (catches ribs).
2. J8, ribs, first try: a coarse walk along the rays (300 steps) and a two-sided statistic gave the REFERENCE
   0.71 % at the largest size, more than "away" (0.53 %). Cause: the walk stepped over the thin gap under small
   buds and counted buds as ripple. Now 2,400 steps and a one-sided statistic (grooves in, not buds out):
   reference 0.21, "away" 0.69.
3. J3, "cut x = 0 minus its core disc is a ring": not measurable as written, the lathe's disc and ring touch
   with no gap. Replaced by "does a piece that comes off go all the way round the axis".
4. J5: the strict biggest-piece share punishes bodies that touch at one point (voxels miss the point: the
   reference has 41 pieces at 99.99 %). The verdict uses the share with a one-voxel gap allowed.
5. J4 counts only round pieces. Without that the Mandelbulb's blades (18 "buds" off the plane) and the pure
   winding's ribbed lemons passed J4.
6. J7 uses the share that changes under the mirror, not the volume ratio (the pillow is 0.956 to 1 by volume
   but a third of it changes).
7. J6: the close pairs alone find the tear of two planes only by luck at small steps (1.2, 0.57, 0.17); the
   hunt by halving finds a jump of 4.3 over a gap of 4e-10.
8. J2: the area ratio of the two cuts (the brief's first proposal) is stored (`neck_area_pct`) but the verdict
   uses the ball, the upright line and the cut near the axis.

## Results of this round (stage 1, then stage 2 for the passer)

| rule | J1 | J2 | J3 turn / rings | J4 round off-plane / on bud / on small body | J5 | J6 | J7 | J8 roundness | J8 ribs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Turning plane, along | 0 | 0.02 / 0.000 / 0.02 % | 2.5 % / 0 | 26 / 24 / 19 | 100.000 (99.89, 161 pieces) | 8e-9 | 0.00 % | 0.74, 0.56, 0.52 | 0.04, 0.06, 0.04 | PASSES all eight |
| Turning plane, away | 0 | 0.02 / 0.000 / 0.02 % | 11.5 % / 0 | 6 / 8 / 9 | 99.998 (99.64, 701 pieces) | 1e-8 | 0.00 % | 0.58, 0.64, 0.67 | 0.69, 1.38, 1.31 | FAILS J8 (ribbed) |
| Pure winding, m = 2 | 0 | 0.02 / 0.000 / 0.02 % | 9.1 % / 0 | 0 / 0 / 1 | 100.000 (99.70, 573 pieces) | 8e-9 | 0.00 % | 0.32, 0.32, 0.38 | 0.70, 1.24, 1.28 | FAILS J4, J8 |

Things to say about "along" that the pass / fail line hides:
- J3: its turn number (2.5 %) is below the reference's (6.0 %). The reason is its eight nearly equal buds: a
  45 degree turn puts buds on buds. A 22.5 degree turn changes 8.5 %. Nothing that comes off goes round the axis.
- J8: its small bodies are less round than the reference's (0.56 and 0.52 against 0.71 and 0.74), inside the
  band the calibration does not decide. One close-up deeper (`deeper.png`, box 0.006 wide) the number is 0.47
  against 0.73: lemon-shaped bodies with clusters of small pegs. Still bodies on bodies, not streaks, by eye; but
  the roundness falls with depth (0.74, 0.56, 0.52, 0.47) and the reference's does not.

Stage 2 was run for "Turning plane, along" only (193 a side, 50 steps, box x in [-2.05, 0.95]):

| | measure | value | |
|---|---|---|---|
| M1 | cut at z = 0 against the flat Mandelbrot set, 801 x 801 | 0 of 112,963 points differ (cut at y = 0: 0 of 63,599 too) | pass |
| M2 | biggest piece, one-voxel gap allowed (strict) | 99.991 % (99.85 %, 411 pieces) | pass |
| M3 | how full the cut x = -0.2 is inside the circle round it | 60 % | body, not leaves |
| M4 | period-2 body: ball needed to part it from the main body; cut at x = -0.75 within 0.1 of the axis | 0.12; 78 % full | FAIL: grown on along a patch |
| M5 | pieces that come off the main body (worn down by 0.12) | 8, 6 off the flat plane, none round (0.15 and 0.27); 2 go round the axis | FAIL |
| M6 | roundness of what comes off, and close up | 0.29, 0.20 | FAIL: ridges and fins |
| M7 | mirrors | 0.00 % and 0.01 % | pass |

Verdict to record: **Turning plane, along: basilica passes, Mandelbrot fails, because the solid is a lumpy rock
with ridges and a few horns; nothing round comes off it and the period-2 body is grown onto the main body.**
M3 to M6 could not be calibrated on rules with a known verdict (stage 2 may only be run on stage 1 passers), so
for those the picture is the evidence: `sheet-for-user.png`, second half.

Warning lights for "along" (161 a side, 40 steps; not part of any verdict): rabbit (-0.12, 0.74, 0): volume 1.67,
biggest piece 99.997 %, 5 pieces (one swollen lump with ridges); c = (-1, 0.15, 0.1): volume 0.45, biggest piece
98.7 %, 82 pieces; c = (-0.6, 0.3, 0.3): volume 0.63, biggest piece 97.3 %, 350 pieces.

## Extra checks made this round

- The x-axis (`axis_test`, `logs/axis-test.log`): the hunt of J6 follows random segments and cannot see a line.
  Pairs of points at the same x, the same small distance from the axis, in unrelated directions round it: the
  largest jump is 6e-3, 6e-6, 6e-9 at distances 1e-3, 1e-6, 1e-9 for "along", "away" and the pure winding (and
  for two planes: its tear dies out at the axis). So none of them tears at the axis.
- The wearing radius (`wear_check.py`, `logs/wear-check.log`): round buds off the flat plane on the middle body at
  radius 0.07 / 0.11 / 0.15: reference 6 / 6 / 2, one plane 0 / 0 / 0, "along" 26 / 26 / 6, "away" 6 / 6 / 2,
  pure winding 0 / 0 / 0. The J4 verdicts do not depend on the radius in that range.
- Where the ribs of "away" sit (`logs/diag-outline.png`, the outline of the cut x = 0 against the angle): the
  ripple is in a band about 20 degrees either side of each diagonal (45, 135, 225, 315 degrees), smooth near
  the two planes. Seen in the plot, not put into a number.

## Limits (read before trusting a number)

- Voxel pictures at 321 a side are rough. The cuts and the rib outlines do not use voxels.
- For c = -1 the iteration stops a point once it comes within 0.05 of the origin (it is then counted inside).
  This was checked per rule on 100,000 points for 150 steps (`trap_radius`), not proved.
- The close-ups follow ONE bud (the biggest off the flat plane) and one small body on it. Other buds may differ.
- J4 and J8 depend on the wearing radius (0.11 on the middle body, 1/18 of the box in close-ups). Not varied.
- The escape radius assumes the rule squares the length. A rule that does not needs `resc` changed.
- Stage 2 thresholds M3 to M6 are uncalibrated (see above).
