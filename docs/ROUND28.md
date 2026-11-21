# Round 28: the dials of Balls on balls go past their ends, and the last pillow

Binding for everyone in this round. Read all of it before you start.

## 0. The user's words

After playing with the lab entry "Balls on balls" (Version 20) the user wrote (verbatim):

> Whoa!! The balls on balls approach is amazing, keep it in all cases (and btw the parameters should be able to go
> past their current limits, they don't - like percentage of the balls, it should be able to go more than 100%) -
> that is (loosely, obviously the specific shapes are wrong but the placement and spacing of objects is pretty much
> perfect) exactly how I expect the 3d basilica to look. So this is what the 3d fractal should look like (with
> proper shapes obviously)

The user is not a mathematician. They judge by pictures and by moving sliders. They have twice said "you're
literally speaking in greek to me". Their five tests for "the right rule": (1) the flat cut z = 0 is exactly the
flat picture of z^2 + c; (2) the number of bulbs follows from the power; (3) no shards, no smear; (4) no rings
(the flat picture merely spun round a line), and it must work for the rabbit, not only for c = -1; (5) a
principled carry-over from 2D, nothing picked by hand.

Two tracks, independent of each other:

- Track A ("dials"): every dial of the entry can go past its present end, and the object follows.
- Track B ("pillow3"): build the one member of the even-spacing family that was never built, because the user's
  new target (the placement of Balls on balls) points at it.

House rules, how the lab is put together and the test tools: `docs/ROUND26.md` section 3 and `docs/ROUND27.md`
sections 2.3 and 4 (words). They hold here with `r28` in place of `r26` / `r27`, and with `base20a/` as the frozen
copy (Version 20, the published page; `src/` is identical to it today). The lab's handle on a page is
`window.squaringLab` (`S`, `touch`, `refresh`, `syncControls`, `idle()`, `sampleSlice`, `ballsInside`,
`ballsEstimate`, `ballsReach`, `ballsFrame`, `ballsShow`, `ballsOn`, `BALLS`, `learn`, ...).

## 1. Track A: the dials

### 1.1 What is true about "more than 100" (the orchestrator's reasoning; the truth checker tests it)

The recipe today, in the object's own coordinates m, with top = 2t (state `S.k.bt` = t):

    repeat:
      if mz < 0 or mz > top:            INSIDE
      slide (mx, my) by the nearest whole number of the grid
      if |m| < 1:                       m -> m / |m|^2                     (first sphere: radius 1 about (0, 0, 0))
      else if |m - (0,0,top)| < 1:      the same about (0, 0, top)         (second sphere: radius 1 about (0, 0, top))
      else:                             OUTSIDE

The dial "Size of the neighbours" shows p = 100 / (2t - 1) = 100 / (top - 1). At p = 100 (top = 2) the two spheres
touch. Past it they would cut into each other, and then the balls cut into each other too (round 27 measured that:
`out/r27/measure/NOTES.md` section 5.2; only single settings survive, where the chain closes into a ring, and the
lab's frame cannot show those). So with two equal spheres, 100 is a real wall: in any view that is its own mirror
image left to right, the neighbours are never larger than the middle ball.

The neighbours CAN be larger than the middle ball when the second sphere is smaller than the first. One more
number, rho (radius of the second sphere, the first stays 1):

      else if |m - (0,0,top)| < rho:    m -> (0,0,top) + rho^2 (m - (0,0,top)) / |m - (0,0,top)|^2

The frame is unchanged (one sphere inversion about (0, 0, 1), k^2 = 1.05): the middle ball is k^2 wide, the two
neighbours k^2 / (top - 1) wide, so p = 100 / (top - 1) as before, and the two spheres touch at top = 1 + rho, that
is at p = 100 / rho. It is an object (no two balls cut each other; Klein's combination) exactly when

    rho = 1      and  p <= 100         (today's object), or
    rho <= 1/2   and  p * rho <= 100   (the copies of the second sphere at neighbouring whole numbers do not cut each
                                        other, and the second sphere does not cut the first).

Between 1/2 and 1 only single values of rho work; they are NOT offered. So with rho = 0.5 the neighbours go up to
200 % of the middle ball, with rho = 0.25 up to 400 %. What the eye sees: a small middle ball between two large
balls; the large balls carry smaller and sparser buds than the middle ball does.

Not in this round, even if tempting (write the thought into your notes instead): the rings below t = 1 with equal
spheres, the sideways slide of the second sphere, coarser grids, any new choice of "Whole numbers".

### 1.2 Decisions that are made (do not reopen them)

1. New state `S.k.brho` (default 1), new uniform for it. `S.k.bt` stays t = top / 2 and may now be below 1 when
   rho < 1 (never below (1 + rho) / 2).
2. **Size of the neighbours, % of the middle ball**: slider 2 to 400, typed values 1 to 2000 (today 10 to 100 and
   2 to 100). Default 55.56 as today (the exact t = 1.4 behind it is kept, see `ballsFromShare`).
3. **Second sphere, % of the first** (new dial, shows 100 * rho): allowed values 2 to 50, and 100. Default 100.
   A value typed or dragged between 50 and 100 goes to the nearer of the two (75 and below: 50). The help says in
   one sentence what the dial does and in one why it jumps (between 50 and 100 the buds on a neighbour would cut
   into each other).
4. The two dials give way to each other (the dial the user moved wins):
   - Size set to p with p * rho > 100: rho becomes min(0.5, 50 / p) (never under 0.02; with p up to 2000 that is
     0.025). So dragging the size dial past 100 simply works: at 101 the second sphere drops to 50 %, from 100 on it
     follows as 50 / p, and the chain keeps its two ends.
   - Second sphere set to rho with p * rho > 100: p becomes 50 / rho (so back to 100 % gives p = 50).
   - Coming back below 100 does not put rho back by itself; "Reset this section" does. While rho is not 100 a
     plain status sentence under the note says so (see 6).
5. **Depth of the search**: slider 1 to 100, typed 1 to 1000 (today 5 to 40 and 5 to 200). Default 16.
   **Whole numbers**: unchanged.
6. Sentences (plain words, section 4 of ROUND27.md; at most two short sentences each; shown where `ballsTrouble`
   shows today, as status, not as an error):
   - where the two spheres touch (p * rho = 100 within rounding): today's "the chain never ends" sentence, no
     longer tied to the number 100;
   - while p > 100: that past 100 the second sphere has to be smaller than the first, or the two would cut into
     each other, and what it is now;
   - while the depth is under 5: that with so few rounds whole balls are still undecided and come out as broken
     shells.
   The note under the group choice (`BALLS_NOTE`) stays as it is. The sentence of the mesh export
   (`46-mesh.js`) names the second sphere when it is not 100.
7. **Every picture with rho = 1 is the same to the pixel as on Version 20.** Simplest safe way: the scene program
   that is compiled when rho = 1 is today's text, unchanged (cache key 'balls'); rho < 1 compiles a second variant
   with its own cache key. Any other way is fine if the pixel check passes.
8. The twin and the estimate take the new number: `ballsInside(x, y, z, { t, grid, rounds, rho })`,
   `ballsEstimate(x, y, z, { t, grid, rounds, rho, parts })`; left out, it is read from the page. `ballsReach()`
   and the start view / "Frame it" follow the larger neighbours: the whole chain in the picture while that is
   possible, and a plain sentence when it is not.
9. Nothing else in the lab changes. The first Kleinian group, the Mandelbrot and Julia views, the Learn tab, the
   Approach list and its row "Balls on balls" stay as they are, to the pixel where a picture is concerned.

### 1.3 The distance the ray marcher is given (the hard part; read the long comment above `GL_BALLS` first)

Today's estimate is the smaller of "best" (the true distance to every ball the search met; `kpearl`) and "free" (a
length that is certainly free of balls, from hulls that hold every ball the search did not meet). The hulls were
worked out for rho = 1. The orchestrator's derivation for rho < 1 follows; the builder checks each line with
numbers before relying on it, and the truth checker tests the result against lists of balls.

- The scale factor of the second inversion is rho^2 / |m - (0,0,top)|^2 (for `DF`, and for W, the image of the
  point at infinity).
- The two fixed points on the middle line: z1 = H_B and z2 = 1 / H_B, with H_B = (s - sqrt(s^2 - 4)) / 2,
  s = top + (1 - rho^2) / top. (s = 2 exactly when the spheres touch; rho = 1 gives today's H = t - sqrt(t^2 - 1).)
  H_B is the height of everything that grows on the bottom wall; H_T = top - 1 / H_B is the depth of everything
  that grows on the top wall. (They solve H_B = 1 / (top - H_T), H_T = rho^2 / (top - H_B).)
- The hull balls: diameter H_B standing on the bottom wall at the nearest whole number, diameter H_T hanging from
  the top wall at the nearest whole number.
- The rest (the buds at places that are not whole numbers): on the bottom wall as today (within H_B / 2, H_B / 3,
  H_B / 4 of the wall or of the line, by grid). On the top wall with rho <= 1/2: within rho^2 * H_T (a bud hull at
  a whole number at distance d from the sphere's centre is carried to one of diameter rho^2 H_T / d^2, d >= 1).
- The spindle (see the comment): the same formula with the middle height zm = (z1 + z2) / 2 in place of t and
  delta^2 = ((z2 - z1) / 2)^2 in place of s2 = t^2 - 1. Circles through both fixed points cross both spheres
  squarely for any rho, so the argument carries over; check that the piece between the spheres stays in the middle
  cell.
- The chain ends at picture x = +-(k^2 / 2 + k^2 H_B / (1 - H_B)) (Infinity where the spheres touch).
- In `40-render.js` the uniform is clamped with `Math.max(1, bt)`: that must become the new lower end.

### 1.4 What must be true (this is what the checkers measure)

a. **It is an object.** From an explicit LIST OF BALLS (the two walls carried by the moves; see
   `out/r27/measure/ballkit.py` for how round 27 did it; write your own with rho): no two listed balls overlap, and
   the recipe's verdict equals "lies in a listed ball" at random points, for rho in {1, 0.5, 0.35, 0.2, 0.05}, p
   from small to just under 100 / rho, all three grids. Also show, with the same tool, that rho = 0.7 (not offered)
   does overlap, so that the jump of the dial is justified.
b. **One recipe, three voices.** The twin `ballsInside`, the checker's own numpy writing of the recipe of 1.1, and
   the shader (through `sampleSlice`, flat view and in space) agree at 20000 points each for at least six settings,
   four of them with rho < 1 and p > 100.
c. **The estimate is safe and the picture whole.** `ballsEstimate` is never longer than the true distance to the
   nearest listed ball (20000 outside points per setting, to the resolution of the list). No holes, no missing
   balls, no shells: rays through at least twelve views with p > 100 (as `out/r27/final/mk/holes.py` does it), and
   the checker LOOKS at each picture.
d. **Old pictures.** Balls on balls at its default and at five more rho = 1 settings (among them p = 100 and the
   honeycomb grid), and six states that are not Balls on balls: 0 pixels differ from the frozen page
   (`python build.py --name r28-base --base base20a`).
e. **Old lists.** The old smoke list (90 steps; `out/r27/final/mk/smoke27.py` shows how it is put together),
   round 26's lists (`out/r26/final/run_final.py` with `use.js`, `spot.js`, `phone.js`) and round 27's scripts
   (`out/r27/final/mk/`: `verd.py`, `shape.py`, `same6.py`, `holes.py`, `flat.py`; they read `R27_PAGE`,
   `R27_BASE`, `R27_OUT` from the environment) pass on the new page as on Version 20. Run browser scripts one at a
   time. No console errors, no new shader warnings.
f. **The dials behave.** Slider ends, typed values past the ends, the two give-way rules of 1.2 point 4, the jump
   between 50 and 100, reset, the row in the Approach list, leaving for another approach and coming back, the 2D
   view, picture export and mesh sentence; wide (1400x950) and phone (390x800), dark and light; every word the
   user reads is in the house vocabulary.
g. **Speed.** First picture at the default no slower than 1.25 times Version 20's on the same machine in the same
   minute; at p = 150 and p = 300 the picture finishes (say how long).

### 1.5 Where to work: an overlay, never `src/`

- Nobody in round 28 may write anything under `src/`, `base*/`, `squaring-lab.html`, `dist/preview.html` or any
  `out/r2[0-7]*/` folder. Changed or new files go to `out/r28/dials/overlay/` with the path they would have under
  `src/` (start each as a copy of the file in `base20a/`).
- Test page: `python build.py --name r28-dials --base base20a --swap js/32-balls.js=out/r28/dials/overlay/js/32-balls.js ...`
  (one `slot=file` pair per overlay file). The builder keeps the full command in `out/r28/dials/BUILD.txt`;
  everyone after builds the same page under their own `--name r28-<part>`.
- Never run plain `python build.py`. Never publish. Only the orchestrator merges and publishes.
- Notes: `out/r28/<your part>/NOTES.md` (never a file called report.md), with "In plain lines" at the top; every
  number comes from a script you ran and kept; "seen" means you opened the picture.

## 2. Track B: the last pillow ("pillow3")

### 2.1 Why now (the orchestrator's reasoning; test it, do not assume it)

The user now names the placement they want: the middle ball of Balls on balls has TWO big neighbours (the chain,
both in the flat picture) and then FOUR buds round its waist (two in the flat picture, top and bottom, and two off
it, front and back), the same above and below the flat picture.

Round 25's pillow section (`out/r25/pillow/NOTES.md`; read all of it) listed every even-spacing rule
F(v) = |v|^2 G(direction of v) that holds the flat picture exactly. Reasoned by the orchestrator: this family is
the whole of the rules of that form that keep shapes within a fixed squeeze at every size (the map of directions
must double every length at the same rate as the length of v grows, and only flat pillows do that). Every
four-corner pillow gives the middle body of c = -1 FOUR equal first neighbours (two extra ones, both on one side
of the flat picture) and is lopsided above / below by force. That is not the user's placement.

One member was worked out on paper and never built (NOTES.md sections 2 A, 3 and 7): **the three-corner pillow
with ONE corner on the flat circle** (the belt runs through one corner, with one corner on each side). Counting
on it (reasoned, to be measured): the corner on the belt is the direction +x and is held fixed; the direction -x
is the one place sent to it three-fold; so the middle body of c = -1 has exactly two first neighbours, both in the
flat picture, and the four directions sent to -x are two on the belt (top and bottom) and two off it, mirror
images of each other in the flat plane. That is the count and the up / down symmetry of Balls on balls.

What the orchestrator expects to go wrong (to be seen, not assumed): the rule wraps space three times round the
negative x-axis. For c = -1 the left neighbour and the meeting point of the two big bodies lie on that line, so
the left neighbour should carry three times as many, thinner buds than the right one; the solid is then not its
own half-turn image, although every flat Julia set is. Squeeze about 3 beside the negative x-axis.

### 2.2 The job

Build it on the bench (`out/r21/lib/mem.py`; rules are `M.Rule`, verdicts `M.stay`, flat truth `M.flat_stay`,
solids `M.solid` + `M.shade_solid`, cuts `M.cut_axis`; `out/r25/pillow/pil.py` and `best.py` show the four-corner
pillows with the angle-true belt, `out/r24/me/tri.py` round 24's triangle), with the belt made angle-true so that
the flat cut is exact, and, if you can, the layout that pushes by 2 beside the flat plane at every longitude
(NOTES.md section 3 has the formula on paper). Then:

1. Checks of the build: flat check against `M.flat_stay` (0 of 20000 differ, four sets: c = -1, the rabbit,
   c = -0.75, a Siegel disc), nothing strays off the flat plane, no tear across any seam (pairs of directions on
   either side), no NaN.
2. Solids of c = -1 and of the rabbit (and its mirror image), from two eyes (one from above the flat plane, one
   from below or from the side), fine enough that buds a twentieth of the middle body show.
3. The placement, measured against Balls on balls (`window.squaringLab.ballsInside` on `dist/preview.html`, or
   `out/r25/klein/tree.py`): how many first neighbours the middle body has and where; the buds round its waist;
   the same for the left and the right neighbour; above against below; left against right (the half turn).
4. The five tests, each as yes or no with a number or a picture.

An honest "no, and here is the picture that shows why" is a full result. A claim of success needs all five tests.
Work in `out/r28/pillow3/`. Mark every statement MEASURED / SEEN / REASONED / THEOREM. Look at your own pictures
before you write about them. Deliver `NOTES.md` with "In six plain lines" at the top, at most three pictures for
the user (real shapes, captions of at most two short sentences, house words only), a "May be told" and a "May NOT
be told" list.

## 3. Done

- Track A: `dist/r28-final.html` builds from `base20a` plus the overlay with the command in
  `out/r28/dials/BUILD.txt`; section 1.4 holds, measured by people who did not build it; the final notes
  (`out/r28/final/NOTES.md`) list every overlay file with one line on what changed, give the verdict "ready" or
  "not ready" with what is left, and name two or three pictures for the user (`out/r28/final/user-*.png`: the
  neighbours at about 150 and at about 300, in the lab, light theme).
- Track B: `out/r28/pillow3/NOTES.md` and a skeptic's `out/r28/skeptic/NOTES.md` that agrees or says where not.
