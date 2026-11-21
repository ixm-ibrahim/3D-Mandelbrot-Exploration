# Round 28, Track A: the truth checker's notes

My part: section 1.4 a, b and the first half of c of `docs/ROUND28.md`, and section 1.3 derived again by me.
Page tested: `dist/r28-truth.html`, my own build with the command in `out/r28/dials/BUILD.txt` (it is the same file,
byte for byte, as the builder's `dist/r28-dials.html`). Frozen page: `dist/r28-base-truth.html`. I changed nothing
in the overlay. Scripts: `out/r28/truth/mk/`. Logs: `out/r28/truth/logs/`. Every number below comes from a script
kept there; the script and its log are named with it.

## In plain lines

1. **It is an object.** Second sphere 100, 50, 35, 20 and 5 % of the first, neighbours from small up to the place
   where the two spheres touch, all three grids: 90 settings, 56 million balls listed. No two listed balls cut into
   each other. At 1.8 million random points the recipe and the list agree: no point the recipe calls outside lies
   in a listed ball, and every ball the recipe puts a point in is in my list whenever it is large enough to be
   listed (the 227 points that differ lie in balls smaller than the list goes, each ball worked out exactly).
2. **A second sphere of 70 % is not an object.** Balls cut into each other on all three grids at every size tried
   (12 of 12 settings), as deep as 0.035 to 0.118 where the balls themselves have radius 0.03 to 0.07. So do 60
   and 85 %. And just past the place where the spheres touch (size times second sphere 5 % and 20 % over) balls
   cut into each other in all 18 settings tried, and none do exactly at it. So the jump of the dial between 50
   and 100 and the give-way of the size are both needed.
3. **Every state the two dials lead to is an object.** 600 random moves of the two dials (typed values far outside
   the ends and inside the gap, slider positions, the reset button): 293 different states, none outside the
   allowed ones.
4. **One recipe, three voices.** 20 settings, 15 of them with a smaller second sphere and neighbours past 100.
   The twin `ballsInside` against my own writing of the recipe: 0 of 800000 verdicts differ. The shader against my
   writing: in space 0 of 409600; in the flat cut 9 of 408040, every one of them within 0.00000006 of a skin, and
   8 of the 9 in settings with two equal spheres, where the program is Version 20's own.
5. **The estimate is safe.** `ballsEstimate` is never longer than the true distance to the nearest listed ball:
   0 of 1569414 outside points in 20 settings (anywhere in the picture; beside the middle line; just under the top
   wall; beside a cell edge), and 0 of 720000 more points that fill a whole cell evenly, 12 settings. The shader's
   own number is above the true distance only by what single precision does to it (at most about one and a half
   units of its last digit, in the settings with the farthest balls).
6. **Section 1.3, line by line**: scale factor right; fixed points right; hull balls right; the rest right;
   chain end right; the lower end of the uniform right. **The spindle as written in 1.3 is wrong** for a small
   second sphere (it sticks out through the top wall and whole balls lie in it: 27 of my 60 settings). The
   builder's replacement is right, and it is the largest that is right (a listed ball touches it). The builder's
   own extra line (the bare top wall) is right too. The code does what its comment says.
7. **Defects in my part: none major.** Minor things and things seen in passing are listed under "Defects and
   remarks" below. The one the orchestrator should read: the size dial moves the second sphere more often than the
   bare formula of decision 4 says (78 of 317 moves of the size in my random walk). The builder declared this.
8. **Not checked by me**: rays and pictures (second half of c), old pictures to the pixel (d), old lists (e),
   the handling of the dials (f), speed (g).

## My tool: a list of balls with the second sphere's radius

`mk/tkit.py`, written from section 1.1 and one fact (a sphere inversion carries a ball that does not hold its
centre to a ball). I read `out/r27/measure/ballkit.py` for the idea and wrote mine differently.

- `build(grid, top, rho, r_min)`: starts from the two first buds (the top wall carried by the first sphere, the
  bottom wall carried by the second) and applies both inversions to every ball slid by every whole number that
  leaves it outside the sphere, until the images are too small. Keys are compared in full (no hashing).
  The list promises every ball of radius at least `r_min` in the object's own space, and finer near the second
  sphere's centre: `r_min` times the square of the distance from it, down to `r_min * rho^2` inside the second
  sphere (`threshold`). So the buds that hang from the top wall are listed as finely, for their size, as those on
  the bottom wall. It holds everything down to half of that, to be whole down to the promise.
- `Index`: answers "does this ball meet a listed ball" for points anywhere, knowing that the list repeats with the
  grid. `overlaps`: every ball against every ball no larger, all slid copies, and the walls; a pair counts when the
  two reach into each other by more than a millionth of the smaller one's radius.
- `recipe`: section 1.1 written out in numpy. `ball_of`: for a point the recipe calls inside, the very ball it lies
  in, found by walking the recipe's own moves backwards from the wall. This is what lets me say "the recipe's ball
  IS in the list", not only "the point is in some listed ball".
- Does the tool measure right? `mk/selftest.py` (`logs/selftest.txt`): my "meets a listed ball" test and the
  distance found from it by halving, against brute force over explicit picture balls: largest
  relative difference 1.2e-8 at 4349 points in four settings (59000 to 396000 picture balls each); honeycomb "nearest whole number" against brute
  force: 0 of 200000 differ. `mk/j_anchor.py` (`logs/j_anchor.txt`): my recipe against round 25's own program
  `out/r25/klein/tree.py` for two equal spheres, three grids, t = 1, 1.4, 2.5, in space and in the flat cut:
  0 of 360000 verdicts differ. (This also fixes which picture axis is which; section 1.1 does not say.)
- One fault of my own, found and put right: my first overlap test called two balls "the same ball listed twice"
  when their centres and radii agreed to 0.000001, which hid pairs of balls smaller than that from the test (the
  lists for small second spheres go down to 0.00000005). The test now measures against the ball's own size. The
  first run is kept as `logs/a_object-first-run.txt`; the numbers in these notes are from the run after the fix.

## a. Is it an object (`mk/a_object.py`, `logs/a_object.txt`)

Second sphere rho in {1, 0.5, 0.35, 0.2, 0.05}; size p = f * 100 / rho with f in {0.05, 0.3, 0.6, 0.9, 0.99, 1}
(f = 1: the two spheres touch, the largest size the dials allow for that second sphere); grids line, square,
honeycomb. Lists down to radius 0.0004 (square, honeycomb) and 0.00002 (line), finer near the second sphere.
20000 random points a setting: 8000 in a box of the picture, 4000 anywhere between the walls, 4000 close above the
bottom wall, 4000 close to the second sphere. The recipe with 300 rounds.

All 90 settings hold. In all:

- 56444586 listed balls (830 to 2654099 a list). Pairs that cut into each other: **0**. A ball beyond a wall: none
  (largest reach 2e-15, which is rounding). The same ball listed twice: 9049 times (a key that fell on either side
  of a rounding step; harmless, and not counted as a pair).
- 1800000 points: 386466 inside by the recipe, 1413534 outside, 0 undecided after 300 rounds.
  Outside by the recipe but in a listed ball: **0**. Inside by the recipe, its ball large enough to be listed, and
  not in the list: **0**. Inside by the recipe and in no listed ball: 227, every one in a ball smaller than the
  list promises at that place (so "the verdict differs from the list" at 227 of 1800000 points, all explained).
- From the same lists: the highest ball on the bottom wall and the deepest on the top wall stay below H_B and H_T
  of section 1.3 in every setting.

rho = 0.7 with the same tool (same log, lower part): on all three grids, at sizes 30, 55.56, 100 and 135.7, listed
balls cut into each other; the deepest reach is 0.035, 0.066, 0.100, 0.118 (the same on the three grids), into
balls of radius 0.028 to 0.069. Also rho = 0.6 (12 of 12 settings, deepest 0.004 to 0.021) and rho = 0.85 (12 of
12, deepest 0.022 to 0.060). With the same coarse lists rho = 0.5 and rho = 1 show none.
An aside, not offered by the dial: rho = 1 / sqrt(2) and 1 / sqrt(3) showed no overlap in coarse lists, and
sqrt(3) / 2 did. That agrees with "between 1/2 and 1 only single values work"; I did not test those single values
further.

Past the touching point (`mk/a_past.py`, `logs/a_past.txt`; the dials never show this), second sphere 100, 50
and 20 % on the three grids: size times second sphere 5 % and 20 % above 100 x 100: balls cut into each other in
18 of 18 settings. 2 % above: in 6 of 9 (not found for a second sphere of 20 % with lists this coarse). Exactly
at 100 x 100: none in 9 of 9.

Every state the dials lead to (`mk/i_walk.py`, `logs/i_walk.txt`): 600 moves at random (typed sizes 0.5 to 2500,
typed second spheres 0 to 120 and the values round 50, 75 and 100, slider positions of both, reset 16 times), the
state read after each: 293 different states, 0 with a second sphere between 50 and 100, 0 with size times second
sphere above 100 x 100, 0 with t below (1 + rho) / 2; second spheres met: from 2 to 50, and 100. After every move
the two boxes show the state. (Events made by script: a test of where the state can go, not of the handling.)

## b. One recipe, three voices (`mk/bc_page.py`, `logs/bc_<key>.txt`, `logs/bc_summary.txt`, `logs/h_totals.txt`)

Twenty settings, one browser at a time, state set on the page (`S.k.brho`, `S.k.bt`, `S.k.bgrid`, `S.k.bit`):

| key | second sphere % | size | grid | depth | why |
| --- | --- | --- | --- | --- | --- |
| A | 100 | 55.56 | square | 16 | as the page opens |
| B | 100 | 90 | line | 16 | |
| C | 100 | 100 | honeycomb | 30 | two equal spheres touching (a Version 20 state) |
| D | 33.33 | 150 | square | 16 | what typing 150 gives |
| E | 16.67 | 300 | honeycomb | 16 | what typing 300 gives |
| F | 50 | 190 | square | 40 | all but touching |
| G | 25 | 300 | line | 16 | |
| H | 12.5 | 400 | square | 16 | the end of the slider |
| I | 2.5 | 2000 | square | 16 | the largest size that can be typed |
| J | 50 | 150 | honeycomb | 16 | |
| K | 20 | 80 | square | 16 | smaller second sphere, size under 100 |
| L | 5 | 1900 | honeycomb | 60 | all but touching, tiny second sphere |
| M | 50 | 200 | square | 40 | touching |
| N | 20 | 250 | square | 16 | second sphere set on its own dial |
| O | 2 | 2000 | honeycomb | 16 | the smallest second sphere |
| P | 50 | 2 | square | 16 | very small neighbours |
| Q | 33.33 | 150 | square | 3 | few rounds |
| S | 50 | 199.9 | square | 300 | all but touching, deep |
| T | 16.67 | 300 | honeycomb | 1 | the smallest depth |
| U | 25 | 400 | square | 1000 | touching, the largest depth that can be typed |

In every one: the program on show is `k-balls` for a second sphere of 100 and `k-balls2` below; no console errors.

- Twin `ballsInside` against my numpy writing: 20000 points in space and 20000 in the flat cut a setting, the
  page's depth: **0 of 800000 differ**. The twin with nothing passed (read from the page) says the same as with
  the numbers passed, in all 40 runs.
- Shader (through `sampleSlice`, from the program the picture is drawn with) against my writing. Flat cut: two
  101 x 101 grids a setting (the whole object; a close-up, 0.5 wide, of the place where the middle ball and a
  neighbour kiss). In space: twenty 32 x 32 grids (ten wide at random heights, ten close-ups 0.6 wide).
  **In space 0 of 409600 differ. Flat cut 9 of 408040 differ**: 2 in B, 6 in C, 1 in F. At each of the nine, both
  the shader's number and the twin's are below 0.00000006 in size (`logs/f_shader.txt`): the point lies within
  that of a skin, among balls of that size where the depth of the search runs out. Single precision cannot decide
  those. B and C run Version 20's own program text (the same to the byte, my comparison), so 8 of the 9 are what
  Version 20 does too. Not a defect.
- The builder reports 0 of 569016 for the shader. I see no contradiction: my flat grids include a close-up of the
  kiss and three touching or nearly touching settings, which is where the nine are.

## c, first half. The estimate (`mk/bc_page.py`, `mk/c_cell.py`, `mk/e_best.py`, `mk/f_shader.py`)

The test. The ball of radius `ballsEstimate` about a picture point is carried by the frame to the object's own
space, where it is an exact ball again, and asked against my list (all slid copies) and the two walls. If it
reaches in by more than 1e-12, the estimate is too long, and the true distance to the nearest listed ball is then
found by halving. A ball smaller than the list goes cannot be seen by this test (lists: radius 0.0003 for the two
plane grids, 0.00001 for the line grid, finer near the second sphere). The list can only make the true distance
look longer than it is, never shorter, so a "too long" would be real.

- `bc_page.py`, the same 20 settings, points my recipe calls outside, up to 20000 a set:
  box (anywhere in a box of the picture, half of them close to the chain), mid (beside the middle line of a cell,
  between the two hull balls, from 0.0001 to 0.5 off the line), top (from 0.00001 to 0.3 under the top wall, half
  of them under the foot of the second sphere), edge (within 0.000001 to 0.03 of a cell edge, a third at the
  corners, half of them low). The last three are made in the object's own coordinates, slid by a whole number and
  carried to the picture. **Estimate longer than the true distance: box 0 of 370940, mid 0 of 400000, top 0 of
  400000, edge 0 of 398474.**
- `c_cell.py`, 12 settings (A C D E F G H I J L M O): points that fill a cell evenly between the walls, its lowest
  part and its highest part, 20000 each: **0 of 720000**.
- How tight it is (same logs, "twice the estimate would still be free"): away from touching, twice the estimate
  already reaches a ball at nearly every point (A: all but 33 of 20000 in the box). Where the two spheres touch
  (C, M) twice the estimate would still be free at half to nine tenths of the points: safe, but short. That is
  the speed checker's and the ray checker's business, not a fault of the distance.
- "best" is the true distance to a ball (`e_best.py`, `logs/e_best.txt`): I worked the same number out with no
  scale factor and no W, by carrying the two walls back through the search's own inversions to explicit balls of
  the picture. 36504 outside points in 7 settings: largest relative difference 2.7e-11.
- The shader's own number at its 348624 outside grid points (`logs/bc_<key>.txt`, `logs/f_shader.txt`,
  `logs/f_shader_L.txt`). Where "best" is the smaller of the two numbers the shader's number IS the true distance,
  so single precision puts it a hair above as often as below (above at 48847 points). Above by more than 0.2 % of
  the distance plus 4e-7 of the size of the coordinates: 3 points, all in L, too
  long by 0.7 to 0.93 units of the last digit there (0.000008 to 0.000024 in a picture 40 units wide), at points
  10 to 15 units from the middle. The largest excess anywhere in L, I and O, the three settings with the farthest
  balls: 1.54, 1.02 and 1.06 units of the last digit. A far
  point of the picture is carried close to (0, 0, 1), and a single-precision number near 1 has a last digit of
  1.2e-7, which is 1.2e-7 |u|^2 / k^2 in the picture. Not a defect of the overlay: it is the frame, as on
  Version 20, and far below a pixel at any view that shows those balls whole.
- Shader's number against the twin's at all 817640 grid points: within 3.3 units of the last digit in 19 of the
  20 settings. In C (two equal spheres touching, Version 20's program) three points are further apart: 5.9, 82
  and 171 units, the shader the longer by 8, 16 and 12 %; yet in C the shader's number is above the true distance
  at 0 of 18334 points. Reasoned, not measured: a point within a hair of a sphere can be ended one round earlier
  by one voice than by the other, and the two endings give two different lengths that are both safe.

## Section 1.3, derived again (reasoned), and put to the lists (`mk/d_derive.py`, `logs/d_derive.txt`, 60 settings)

Words: the first sphere S1 (radius 1 about O), the second S2 (radius rho about C = (0, 0, top)), their inversions
I1 and I2. I1 keeps the bottom wall (its centre lies on it), I2 keeps the top wall. Every ball other than the two
walls lies inside a slid copy of S1 ("grows on the bottom wall") or of S2 ("hangs from the top wall").

1. **Scale factor rho^2 / |m - C|^2, for DF and for W: RIGHT.** It is what an inversion of radius rho does to
   lengths at m, and W is carried by the same map. Code: `s = r2 / rt`, `DF *= s`, `W = top + Wt * r2 / |Wt|^2`.
   Measured: see `e_best.py` above.
2. **Fixed points z1 = H_B, z2 = 1 / H_B, s = top + (1 - rho^2) / top: RIGHT.** I1 sends everything above height h
   into the ball of diameter 1 / h standing at O and moves a point outside S1 only downward; I2 likewise with
   rho^2 / d. So the highest growth on the bottom wall and the deepest on the top wall solve H_B = 1 / (top - H_T),
   H_T = rho^2 / (top - H_B), which is H_B^2 - s H_B + 1 = 0, smaller root. s - 2 = (top - 1 - rho)(top - 1 + rho)
   / top, zero exactly when the spheres touch. Measured: in all 60 lists the highest ball on the bottom wall and
   the deepest on the top wall stay below H_B and H_T and come close (for example 0.779221 of 0.779304 and
   0.050130 of 0.050138 at rho 1/6, p 300).
3. **Hull balls of diameter H_B and H_T at the nearest whole number: RIGHT.** What grows inside S1 is I1 of the
   top wall or of something hanging from the top wall in any cell, all of which lies above z2, so it lies in
   I1(above z2) = the ball of diameter 1 / z2 = H_B standing at O; or it is I1 of growth on the bottom wall of
   another cell, which is "the rest". A point of the middle cell is nearer to its own hull ball than to a slid
   copy. The same from the top. Measured: every listed ball lies in its hull ball or belongs to the rest.
4. **The rest: RIGHT.** Bottom: I1 carries the hull ball standing at the whole number n to one of diameter
   H_B / |n|^2 standing at n / |n|^2. |n| = 1 gives the hull ball back (it crosses S1 squarely); the next are
   |n|^2 = 2 (square), 3 (honeycomb), 4 (line), and images of images are smaller still (H_B / |q|^2 at the
   fraction p / q). Top, rho <= 1/2: I2 carries the hull hanging at n to diameter rho^2 H_T / |n|^2 <= rho^2 H_T;
   a rest ball slid by n stands at least 1 - rho >= 1/2 >= rho from C, so its image is no larger. Measured (60
   lists): bottom rest reaches 0.192654 of an allowed 0.210102 (square, as the page opens), top rest 0.000571 of
   0.000573 (rho 0.125, p 400); never above.
   **The builder's extra line (bare wall): RIGHT.** A rest ball touches the top wall no further from C than x with
   x = rho^2 / (1 - x), that is x = (1 - sqrt(1 - 4 rho^2)) / 2, and is at most rho^2 H_T across, so it lies within
   rT = min(rho, x + rho^2 H_T) of C; slid copies are further from the point than the middle one. Measured: the
   farthest listed rest point stays within rT in all 60 lists, closely (0.015846 of 0.016450 at rho 0.125, p 400;
   0.000627 of 0.000630 at rho 0.025, p 2000).
5. **The spindle: the idea is RIGHT, the formula AS WRITTEN IN 1.3 IS WRONG, the builder's is RIGHT.**
   Right: z1 z2 = 1 and (top - z1)(top - z2) = rho^2, so every circle through z1 and z2 crosses both spheres
   squarely; both inversions carry each such circle, and the spindle swept by the arcs up to a chosen one, onto
   itself. If the piece of the spindle between the two spheres lies in the middle cell and between the walls,
   the recipe calls it outside, and the two inversions carry it piece by piece onto the whole spindle, so no ball
   reaches in. Wrong as written: the arc that reaches 1/2 from the line at mid-height zm bulges through the top
   wall whenever top - zm + rho < 1/2. Measured: it fails in 27 of the 60 lists. At rho 1/6, p 300 the spindle
   stands 0.011 above the top wall and 6 listed balls reach in, up to 0.0062; at rho 0.025, p 2000 it stands
   0.20 above and balls reach in 0.15; in the worst of my lists 100 balls reach in, 0.17 deep.
   The largest spindle that is right is the one whose arc touches the top wall. A circle that crosses S2 squarely
   and touches a plane through C touches it on S2, so that arc is the circle about (rho, top - R) with
   R = top - zm, and its reach at mid-height is w = top - zm + rho (the identity (top - zm)^2 - delta^2 = rho^2
   is the one above). The bottom wall is never in the way (the same sum gives zm + 1). So w = min(1/2, top - zm +
   rho), which is what the builder took. Measured: with it no listed ball reaches in, in all 60 lists; and it
   cannot be made larger, a listed ball touches it to 1e-16. The room R minus the distance from the circle's
   centre: I checked that the ball of that radius about the point lies in the spindle in space, for a centre on
   either side of the line.
6. **Chain end x = +-(k^2 / 2 + k^2 H_B / (1 - H_B)): RIGHT** (z2 carried by the frame). `ballsReach()` agrees with
   it to 7.5e-15 in the 17 of my 20 settings that have an end (`logs/h_totals.txt`), and says "no end" in the three
   touching ones. The last listed link of the chain ends just inside it in every list (2.4052 of 2.4059 at rho
   1/3, p 150).
7. **The lower end of the uniform: done.** `40-render.js` sets `uBT` to `ballsT()` = max((1 + rho) / 2, t), which is
   max(1, t) for two equal spheres, and sets `uBRho` only for the second program.
8. The carry back, e L / ((L + e) DF): exact, also when e is larger than L.

**Does the code do what it says?** Yes. I read `ballsHulls`, `ballsSpindle`, `ballsEstimate` and `GL_BALLS_RHO`
against the comment above `GL_BALLS_RHO` and against my own derivation: the same expressions, in the twin and in
the shader. `GL_BALLS` is the same text as in `base20a` (5956 characters, my own comparison). The numbers bear it
out: 0 of 2.29 million estimates too long, the shader within single precision of the twin.

## Defects and remarks

None major in my part (no wrong verdict, no estimate that is too long, no console error in any of my browser runs).

Minor, or for someone else to decide:

1. **Section 1.3's spindle line is wrong as written** (the brief, not the page). Shown by
   `python out/r28/truth/mk/d_derive.py` -> `logs/d_derive.txt`, column "spindle as written": FAILS in 27 of 60.
   The page does not use it; it uses the right one.
2. **The size dial moves the second sphere more often than the bare formula of decision 4** (outside my part;
   the builder's first known gap). `logs/i_walk.txt`: in 78 of 317 moves of the size the second sphere ends
   elsewhere than "min(0.5, 50 / p) when p rho > 100, unchanged otherwise" gives. Steps (`mk/i_steps.py`,
   `logs/i_steps.txt`): open Balls on balls, type 150 into the size (second sphere 33.33), type 250: the page
   shows 20, the bare formula keeps 33.33. Then type 90: the page shows 50, the bare formula keeps 20. So "coming
   back below 100" does change the second sphere (to 50, never to 100). Also: type 101 (49.5), then 199: the page
   shows 25.13, the bare formula keeps 49.5. The moves of the second sphere's own dial, the ends, and the reset
   all match the bare formula (13 of the 18 steps in that log are the same either way). Every such state is an object. Decision 4's own sentence "from 100 on it follows
   as 50 / p, and the chain keeps its two ends" is what the page does and what the bare formula does not do
   (with the bare formula the chain grows endless at 200, then jumps). The orchestrator's call.
3. **Nine hair points in the flat cut** where the shader and the recipe differ (see b). Single precision; 8 of 9
   in Version 20's own program.
4. **One launch that stood still.** In the first try of setting Q the page stood at "Preparing the formula" for
   the whole 900 s that the first step waits for the page's opening picture, before anything of mine had run;
   then my script ran normally (`logs/bc_Q-first-try.log`). My machine was loaded then (three of my own list
   builds, one holding 4.7 GB, and other people's browsers). Not seen again: `mk/g_open.py`, 20 launches of each
   page in turn, 0 stalls, opening picture after 2.5 to 3.3 s on the new page and 2.8 to 3.6 s on the frozen one
   (`logs/g_open.txt`); nor in my other 35 or so launches. I cannot pin it on the overlay. For whoever times the
   opening.
5. **By hand only**: `ballsInside` reads t as it stands while the shader holds it to (1 + rho) / 2 or more; and
   a second sphere between 50 and 100 written into `S.k.brho` by hand is drawn as it comes (it overlaps). The
   dials reach neither (line 3 of "In plain lines").
6. **Far balls and single precision** (see c): at the largest sizes the far balls of the picture sit where the
   shader's last digit is worth up to 0.00005. Invisible at any view that shows them whole; a very deep zoom into
   a far ball would show it. The same kind of limit as Version 20's far chain.

## What I did not check

The second half of c (rays through views, looking at pictures), d (old pictures to the pixel; I only compared the
old program's text), e (old lists), f (the handling of the dials; I only walked the state), g (speed). Second
spheres between 50 and 100 beyond showing that 60, 70 and 85 overlap. An estimate that is too long only into balls
smaller than my lists go would escape the test of c; the hulls it rests on were put to the lists directly.

## Files

`mk/tkit.py` my list of balls. `mk/pagerun.py` runs a script in the page through `tools/shot.py`.
`mk/a_object.py`, `mk/a_past.py`, `mk/i_walk.py`, `mk/i_steps.py` (a). `mk/bc_page.py` (b and c), `mk/c_cell.py`, `mk/e_best.py`,
`mk/f_shader.py`, `mk/f_shader_L.py` (c). `mk/d_derive.py` (1.3). `mk/selftest.py`, `mk/j_anchor.py` (my tool).
`mk/g_open.py` (the stalled launch). `mk/h_totals.py` (totals). Logs of the same names in `logs/`;
`logs/raw/bc_<key>.json.gz` keeps the points asked and everything the page answered (80 MB in all).
