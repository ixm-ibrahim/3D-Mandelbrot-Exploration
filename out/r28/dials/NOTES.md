# Round 28, Track A ("dials"): the builder's notes

Page: `dist/r28-dials.html`, built with the command in `out/r28/dials/BUILD.txt` (frozen copy `base20a` plus five
overlay files). Frozen page for comparison: `dist/r28-base.html`. Every number below comes from a script in
`out/r28/dials/mk/` and its log in `out/r28/dials/logs/`. "Seen" means I opened the picture.

## In plain lines

1. The three dials go past their old ends. Size of the neighbours: slider 2 to 400, typed 1 to 2000 (was 10 to 100,
   typed 2 to 100). Depth of the search: slider 1 to 100, typed 1 to 1000 (was 5 to 40, typed 5 to 200). Whole
   numbers: unchanged. New dial "Second sphere, % of the first": 2 to 50, or 100.
2. Past 100 simply works: type 150 or drag the slider there, the second sphere drops to 50 / p of the first by
   itself, and the picture shows a small middle ball between two large ones. Seen at 101, 150, 300, 400 and 1000.
3. Every picture with two equal spheres is the same to the pixel as on Version 20: 9 states (6 of Balls on balls,
   3 others), 0 pixels differ. The old program text is untouched (`frozen.py`: the same to the byte); a smaller second sphere
   gets a program text of its own, `GL_BALLS_RHO`, with its own cache key `balls2`.
4. One recipe, three voices: the twin `ballsInside`, my own plain numpy writing of section 1.1 and the shader
   (through `sampleSlice`, flat and in space) give the same verdict at every one of about 80000 points a setting,
   for 14 settings (among them rho 0.5 with p 150 and rho 0.25 with p 300): 0 verdicts differ.
5. The derivation of section 1.3: six lines held, ONE DID NOT. The spindle as written holds whole balls when the
   second sphere is small (at 300 % with the second sphere at 16.67 % the "certainly free" length was too long by up
   to 0.006). I replaced it by a spindle that stays between the two walls (argument and test below). I also added one
   line of my own (bare wall beside the second sphere), because without it the large neighbours showed faint
   bands. With both, the distance is never longer than the true distance at 25 x 20000 test points.
6. Rays: 18 views with the neighbours past 100 or a smaller second sphere, 37625 rays each: 0 holes. Stops in the
   open: 0 in 17 views, 6 (at most 3.4 pixels out) in one of the two close-ups where the spheres touch; Version 20
   has 54 to 102 in its own touching close-ups.
7. The dials, driven with a real mouse and real keys (not made-up events): 70 checks on the wide window and 70 on
   the phone, 0 wrong, no console errors.
8. Speed: the default picture is as fast as on Version 20 (0.97 x, medians of 3). 150 and 300 finish in about
   0.2 s; the first step past 100 costs about 0.9 s once if the second program has not been prepared in the
   background yet (it is, within about 2 s of the default picture).
9. Where I went beyond the letter of the brief, each for a stated reason: the second sphere FOLLOWS the size while
   it was the size dial that set it (section "Choices"); a fourth sentence; arrows jump the gap in one step.
10. Not done by me: the old smoke lists and round 26 / 27 scripts (they write their logs into folders I may not
    write to), and the proof that no two balls cut into each other (section 1.4 a, the truth checker's).

## The overlay: every file, one line each

All under `out/r28/dials/overlay/js/`. `out/r28/dials/changes.diff` is the full difference against `base20a`.

- `00-core.js`: one new number in the state, `S.k.brho: 1` (the second sphere's radius).
- `32-balls.js`: the recipe, the twin and the estimate take rho; `ballsRho`, `ballsT`, `ballsTouch`, `ballsHulls`,
  the two give-way setters `ballsSetShare` / `ballsSetRho`; reach, start view and Frame it for larger neighbours;
  the status sentences; `GL_BALLS` unchanged to the byte, and the new program text `GL_BALLS_RHO` after it.
- `40-render.js`: the second program and its key (`sceneWant`, `sceneKlein` now answers `'balls'` or `'balls2'`,
  new helper `sceneBalls`); the uniform `uBT` is held to (1 + rho) / 2 or more and `uBRho` is set; the background
  warming prepares the other Balls program first while Balls on balls is on show.
- `46-mesh.js`: the sentence of a saved 3D model names the second sphere when it is not 100.
- `80-ui.js`: the wider dials, the new dial with its help, the arrows across the gap between 50 and 100, and
  "its three dials" became "its dials" in the explanation beside the row of the Approach list.

No change to `body.html`, any CSS file, `25-colour.js`, `50-camera.js`, `75-presets.js`, `70-dial.js`, `90-boot.js`.
The handle `window.squaringLab` has the same names as before; `ballsInside` and `ballsEstimate` take `rho` in their
options (left out: read from the page), `ballsReach(t, rho)` takes it as a second argument.

## What I tested, and what came out

| what | script | log | result |
| --- | --- | --- | --- |
| page opens, both programs build, no console errors | `open1.js` (through `run28.py`) | `open1.log` | no console errors; `k-balls` at the default, `k-balls2` at 150 |
| old pictures, pixel by pixel against the frozen page | `same.py` | `same.txt`, pictures in `same/` | 9 states, 0 pixels differ |
| twin = plain recipe = shader | `voices.py`, `voices.py extreme` | `voices.txt`, `voices-extreme.txt` | 14 settings: twin 0 of 560000, shader flat 0 of 282296, in space 0 of 286720 |
| the derivation of 1.3, line by line | `derive.py` (uses `kit28.py`) | `derive.txt` | 25 settings, see next section |
| pictures to look at | `looks.py` | `shots/look-*.png` | seen, see below |
| holes and stops in the open | `holes28.py` | `holes.txt`, `shots/holes-*.png` | 18 views, 0 holes |
| the dials, real mouse and keys | `dials28.py wide`, `dials28.py phone` (uses `drive28.py`) | `dials-wide.txt`, `dials-phone.txt` | 70 + 70 checks, 0 wrong |
| the panel fits | `panel.py` | `panel.txt`, `shots/panel-*.png` | wide and phone, dark and light: nothing sticks out or overlaps |
| a saved picture at 150 | `export1.js` | `export1.log` | 862 x 701 file, 22.4 % not background (the screen: 22.6 %) |
| speed | `speed28.py`, `extras.py` | `speed.txt`, `extras.txt` | see "Speed" |
| how far the picture reaches from the middle line | `tall.py` | `tall.txt` | see choice 5 |

`logs/final-run.txt` is one run of all the browser tests in a row on the final page.

### Old pictures (test 2)

Same script on both pages, picture alone (the canvas), 862 x 701, 4 passes (the first state 12): the page as it opens; Balls on balls as
the row gives it; size 80 typed; 100 with the honeycomb grid; a close-up of the kiss at 100 (where the old spindle
works); 90 with a line only in the 2D view; 30 at depth 8; the first Kleinian group; a Julia rabbit with the bulb
approach and a cut. 0 pixels differ in each. Why it holds by construction: for rho = 1 the program text, the uniform
`uBT` (max(1, t)), the reach and the start view are computed by the very expressions of Version 20 (kept as their
own branch), so nothing can differ by rounding.

### The three voices (test 3)

Settings: rho 0.5 p 150 square; rho 0.25 p 300 square; rho 1/3 p 150 honeycomb; rho 1/6 p 300 line; rho 0.5 p 200
(the spheres touch); rho 0.05 p 1000 honeycomb; rho 0.4 p 60; rho 1 p 55.56; and the ends of the dials: rho 0.025
p 2000; rho 0.5 p 1; rho 0.02 p 55.56 honeycomb; rho 0.02 p 400 line; rho 0.5 p 199.9; rho 1 p 2.
Each: the twin at 20000 random points of a box round the object with 16 and with 60 rounds; the shader on a
142 x 142 grid of the flat view and on twenty 32 x 32 grids at random heights. Against my numpy writing of the
recipe: 0 verdicts differ anywhere. The twin with nothing passed (read from the page) equals the twin with the
numbers passed, in all 14.
The shader's distance against `ballsEstimate` at the same grid points (where both say outside): within 1 % at all
but 4 of about 450000 points (worst 1.8 %, beside touching spheres and at rho 0.05: single precision).

### Pictures (test 5): what I saw

`shots/look-wide-p150-3d.png`, `-2d.png`, `look-wide-p300-3d.png`, `-2d.png`, the same four with `phone`, and with
`wide-light` and `phone-light`: a small middle ball between two large ones, the whole chain in the picture in the 3D
and in the 2D view, whole balls, no holes, no shells, no speckle. Also seen: 101, 400, 1000, 150 honeycomb, 300 line
only, second sphere 25 at 300, second sphere 50 at 55.56, 190 and 200 (touching), second sphere 25 at 400
(touching), 40 at 250 (touching), depth 3 and depth 2 (broken shells, as the sentence says).

Two things the eye should know:

- With the second sphere at exactly 50 the buds on a neighbour touch each other (that is the edge of what is
  allowed). At 55.56 this shows as a pattern of touching circles in the colouring of the neighbours, smooth to the
  touch (`shots/zz-crop-rho50-p55.png`). Near touching (190, 200) the 2D view is a lens or a band with round holes
  and no bare outline of a circle is left (`shots/zz-sheet-2.png`). The three voices agree there too, so this is
  the recipe's picture, not a fault of the drawing; whether one likes it is another matter.
- My first p = 300 picture had faint bands on the large balls (seen only with the contrast raised:
  kept in the notes, the picture was overwritten). Cause and cure: "the bare wall" below.

### Holes (rays)

Method of round 27's `holes.py` with rho added to the recipe written out in the script: every 4th pixel of every
4th row is picked; a ray that stops nowhere is walked with the exact inside test in quarter-pixel steps; a ray that
stops is measured against the nearest ball the search meets (300 rounds). My own addition: for every stop, 38 points
back along the ray are tested, to catch a ray that went through a ball and stopped behind it (0 in all views).

Views: start views at 150 (square, honeycomb), 300 (square, line), 400, 1000, second sphere 50 at 150 and at 190,
25 at 300, 40 at 60; close-ups: the kiss of middle ball and neighbour at 150 and 300, the far end of a neighbour at
150 and 300, along the bare skin of a neighbour at 300, the buds on the middle ball at 150, the kiss where the
spheres touch (50 at 200, 25 at 400). In all 18 the eye is outside every ball.
Result: holes 0 of 18 views. Stops further than 2 pixels from every ball the search meets: none in 15 views; in 2
views (second sphere 50 at 150; 25 at 400, touching) all of them, 8 and 57, lie beside a region that only the depth
of 16 calls solid; in the close-up "second sphere 50, size 200" (touching) there are 427, of which 421 lie beside
such a region and 6 are in the open by that measure, 2 of them with no ball within 2.5 pixels, the furthest 3.4
pixels out.

### The dials (test 6)

`drive28.py` sends real mouse presses, moves and releases and real keys through Chrome's debugging port, so the
slider is dragged and the boxes are typed into as a hand does. What `dials28.py` goes through, on both window sizes:

- Typing: 150 gives second sphere 33.33; 300 gives 16.67; 101 gives 49.5; 80 keeps the second sphere at 50 and the
  sentence says so and names "Reset this section"; the reset gives 55.56 / 100 / 16 with t exactly 1.4.
- Dragging the size slider from 55.56 to about 250 and back to about 60: at every step the second sphere is 100
  up to size 100 and 50 / p past it; on the way back it ends at 50.
- A second sphere typed by hand (30) stays through size 200 (200 x 0.30 = 60) and gives way at 400 (to 12.5).
  2000 gives 2.5; 5000 is held at 2000; 0.2 is held at 1.
- The other way: size 300, then second sphere 40: the size becomes 125; second sphere 100: the size becomes 50.
- The jump: typed 60 and 75 give 50; 76 and 99 give 100; 51 gives 50; 1 and 0 give 2; 250 gives 100. Dragging the
  second-sphere slider down from 100: the box shows 100 while the thumb is above 75, 50 between 50 and 75, then
  the thumb's own value; let go at 66 the thumb goes to 50, at 90 to 100.
- Arrows: in the typed box, on the two small step buttons and on the slider itself, one step up from 50 gives 100
  and one step down from 100 gives 50; a step down from 50 gives 49.
- Touching: second sphere 50 then size 200 gives "At 200 the chain never ends ..."; 200.1 gives way (24.99); 100
  with two equal spheres gives Version 20's sentence word for word.
- Depth: 4 and 1 show the "so few rounds" sentence, 5 does not; 0 is held at 1, 5000 at 1000; all three sliders
  dragged past both ends stop at their ends (size 2 and 400, second sphere 2 and 100, depth 1 and 100).
- Leaving for the Mandelbrot view and coming back by the row, leaving for the first group and coming back: the
  dials are as they were left. The 2D view. "Reset everything" puts all of it back.
- A saved 3D model: at 150 the sentence reads "... neighbours 150 % of the middle ball, second sphere 33.33 % of
  the first, square grid, depth of search 16."; at the default it reads as on Version 20 (no second sphere named).

### Speed

`speed28.py`, 3 trials, the two pages in turn, fresh browser each, warming off: default picture finished after
892 ms on the new page against 919 ms on the frozen one (medians; 0.97 x). On the new page, then: 150 for the first
time 903 ms (one program is built), 150 again 158 ms, 300 170 ms, back to the default 188 ms.
`extras.py`: with the warming on (the page as a user gets it) the second program is started in the background
within about 2 s of the default picture, and the first step to 150 then builds nothing and finishes in about
250 ms (250 ms is also the floor of that script's clock). The deepest search (typed 1000) at the worst places
(100 with equal spheres, 200 with the second at 50, 3D and 2D) finishes within 0.25 to 0.7 s.

## The derivation of section 1.3, line by line

`derive.py` makes, for 25 settings (rho 1, 0.5, 0.45, 0.35, 1/3, 0.25, 0.2, 1/6, 0.125, 0.05, 0.025; p from 30 to
2000; all three grids), a LIST OF BALLS of one cell (`kit28.cell_balls`: from the two walls downward in size, 1000
to 27000 balls a setting) and tests each line. First the list itself against the recipe: of 500000 random points
none lies in a listed ball and is OUTSIDE by the recipe; 211 are INSIDE by the recipe and in no listed ball (balls
below the cut of the list).

| line of 1.3 | verdict | numbers |
| --- | --- | --- |
| scale factor of the second inversion rho^2 / d^2, for DF and W | HELD | DF against finite differences along 2500 chains: worst relative error 5e-9; W against a far point carried along: 1.5e-10 |
| the two fixed points z1 = H_B, z2 = 1 / H_B, s = top + (1 - rho^2) / top; H_T = top - 1 / H_B | HELD | seven equations, worst error 2e-13 |
| hull balls: diameter H_B on the bottom wall, H_T on the top wall, at the nearest whole number | HELD | in all 25 lists no ball outside both the hull and the rest; nothing reaches above H_B or below top - H_T |
| the rest: H_B / 2, / 3, / 4 on the bottom; rho^2 H_T on the top (rho <= 1/2) | HELD | the balls outside the whole-number hulls use up to 99.8 % of the bottom allowance and up to 98.3 % of the top one: both are tight, neither is broken |
| the spindle with zm and delta^2, reaching 1/2 at mid-height | **DID NOT HOLD, CHANGED** | see below |
| the chain ends at x = +-(k^2 / 2 + k^2 H_B / (1 - H_B)) | HELD | the lists reach up to, never past, the formula (25 of 25) |
| the uniform's lower end | DONE | `ballsT()`: max((1 + rho) / 2, t); for rho = 1 that is Version 20's max(1, t) |

The whole estimate, in the picture: at 20000 random points a setting never longer than the distance to the nearest
ball of the picture's list (0 of 25 x 20000; "best" alone would be too long at up to 99 % of the points, so the
second number is doing its work). Median of estimate / true distance between 0.64 and 1.00.

### The spindle: what failed and what I built instead

The argument (every circle through the two fixed points crosses both spheres squarely, so the spindle is carried
onto itself) holds for any rho. What it also needs is that the WHOLE spindle lies in the middle cell AND between
the two walls. The brief asks to check the first; it is the second that fails. The arc that reaches 1/2 at
mid-height has its circle's centre on the far side of the middle line when delta^2 < 1/4, so it bulges beyond the
two fixed points off the line (an apple, not a lemon). With two equal spheres the bulge stays between the walls
(t <= 1.5). With a small second sphere the upper bulge goes through the top wall beside the sphere.
Numbers: at 300 % with rho = 1/6, of 60000 random points of that spindle the recipe calls 363 INSIDE, and the room
is too long at 156 of 20000 test points, by up to 0.0062. At rho 0.125 p 400: 4458 points inside, too long by up to
0.034. At rho 0.025 p 2000: 34983 of 60000 inside, too long by up to 0.15. It fails in 6 of my 25 settings, exactly
those with top - zm + rho < 1/2.

Built instead: the arc that reaches w = min(1/2, top - zm + rho) at mid-height. (top - zm)^2 - delta^2 = rho^2, so
at the second value the circle has its centre at distance rho from the line and radius top - zm: it just touches
the top wall, on the circle where the second sphere meets the wall. In the half-plane (distance from the line,
height): centre (a, zm), radius R, a = (w^2 - d2) / 2w, R = (w^2 + d2) / 2w. For rho = 1 this is w = 1/2 and the
old formula. Tested in all 25 settings: 0 of 60000 random points inside by the recipe, and no listed ball has a
point in it. Used while delta^2 < 3 (for rho = 1 that is the old "t under 2").

### The bare wall: one line of my own

A second sphere smaller than the cell leaves most of the top wall bare. The rest "within rho^2 H_T of the top wall"
is a slab over the whole wall, so beside a bare wall the certain length went to zero: rays crept along the large
neighbours a pixel a step, and the slope of their skin came out in faint bands (seen). Everything that grows on
the top wall lies inside the second sphere, and the buds of the rest touch the wall no further than
x = (1 - sqrt(1 - 4 rho^2)) / 2 from its centre (x solves x = rho^2 / (1 - x): a bud is the image of one that stands
at least 1 - x from the centre). So the rest is only the part of the slab within rT = min(rho, x + rho^2 H_T) of
the centre, and a point is at least max(distance to the slab, distance to that ball) from it. Tested (line "4b" of
`derive.txt`): in the 21 lists with rho < 1 no ball of the rest goes further out than rT (where the list is fine
enough to hold such balls they reach 78 to 95 % of it). After it the bands are gone (seen, same view, same
contrast) and the median of room / true distance at 300 % rose from 0.56 to 0.90 and more.

## Choices I made inside the brief (please check them)

1. **The second sphere follows the size.** Point 4 gives a formula ("size set to p with p rho > 100: rho becomes
   min(0.5, 50 / p)") and a description ("from 100 on it follows as 50 / p, and the chain keeps its two ends").
   The bare formula does not give the description: dragged from 100 to 400 the second sphere would stay at 49.5
   until about 202, the chain would grow endless there, and then it would jump. I built the description: once the
   size dial has set the second sphere, moving the size keeps it at min(1/2, 50 / p); a second sphere set on its
   own dial stays as it is until p rho > 100. One flag, `BALLS_DIAL.follows` in `32-balls.js`, holds "who moved
   last"; it is not part of the state `S`. To get the bare formula back, drop `|| (BALLS_DIAL.follows && rho < 1)`
   in `ballsSetShare`. Consequence to know: coming back below 100 the second sphere stays at 50, not at 49.5.
2. **A fourth sentence.** Point 4 asks for a sentence "while rho is not 100", point 6 lists one for p > 100 only. For
   a smaller second sphere at p <= 100 the page says: "The second sphere is now 50 % of the first. Reset this
   section puts it back to 100."
3. **Arrows across the gap.** A step up from 50 would land at 51 and come back, so the arrow keys and the step
   buttons would be stuck at 50. One step takes them across (up to 100, down to 50). Typed and dragged values
   follow the brief's "nearer of the two".
4. **The sentence where the spheres touch**, for a smaller second sphere: "At 200 the chain never ends, so the
   picture shows a stretch of it, and the small balls between the large ones stand so close that they read as a
   bar with round holes; ..." (2D: "small circles ... a band with holes"). Written after looking at the pictures
   (`shots/zz-sheet-2.png`, `zz-sheet-5.png`). For two equal spheres the sentence is Version 20's.
5. **Start view and Frame it** for a smaller second sphere: the whole chain while it reaches no further than 40 from
   the middle (`BALLS_FAR`); the picture is also made tall enough for the neighbours (how far the object reaches
   from the middle line is max(neighbour's radius, k^2 / 2 + k^2 / (2 top - 1)): `tall.py`, `logs/tall.txt`, 38 lists
   with rho <= 1/2, exact in each). Beyond 40, or where the spheres touch, a stretch is shown (middle ball, both neighbours and a
   bit) and the Drawing radius is set to twice that stretch, so that the place where it cuts a ball open lies
   outside the picture. The camera does not move when a dial moves (as on Version 20): after a long drag the user
   presses Frame it or zooms out.
6. **Help texts.** Size: "How wide the two big neighbours are, measured against the middle ball: smaller neighbours
   give a shorter chain. Past 100 the neighbours are larger than the middle ball, and the second sphere is made
   smaller to let them." (The old text ended "... and at 100 the chain never ends", which is no longer the whole
   truth.) Second sphere: "The sphere inversions use two spheres, and this is the size of the second against the
   first: with a smaller one the neighbours can be larger than the middle ball, and their buds are smaller and
   stand further apart. Between 50 and 100 the buds on a neighbour would cut into each other, so the dial jumps
   from 50 to 100."
7. **Warming.** While Balls on balls is on show the other of its two programs is prepared in the background
   first, so that the first drag past 100 does not stop. It changes no picture; it is one more program built per
   visit to this group.

## What I am not sure of

- The reading of point 4 in choice 1. A checker who tests the bare formula will find that after "size 150" the
  step "size 250" gives 20, not 33.33.
- That it is an object for rho <= 1/2 and p rho <= 100 (no two balls cut into each other): I did not test overlaps.
  My lists only show that every listed ball is inside by the recipe.
- Everything about the distance is tested with numbers on lists of balls down to radius 0.0015 to 0.003 (0.0002 for
  the line grid), not proved. The two arguments I added (the changed spindle, the ball round the rest) are short
  and written above `GL_BALLS_RHO`; a second pair of eyes on them is worth it.
- `ballsEstimate` for a rho between 1/2 and 1 passed by hand (the dial cannot give one): the verdict `ballsInside`
  is the plain recipe and is right; the "certainly free" part is not derived there and I did not test it.
- The 6 stops in the open (up to 3.4 pixels) in the touching close-up with the second sphere at 50. Version 20 has
  more at its own touching view and was accepted with them, but I did not hunt these down.
- The look of the second sphere at exactly 50 near touching (a lens with round holes, see "Pictures"). It is what
  the recipe gives. If the user dislikes it, the cure is a dial that stops a little short of 50, which is a
  decision, not a repair.
- Start views were looked at on 1400 x 950 and 390 x 800 only.
- The old smoke list (90 steps) and the round 26 / 27 scripts were not run by me: they write into `out/r26`,
  `out/r27`. One old script that will read differently on purpose: `out/r27/final/mk/eyes.py` counts the dials'
  help sentences (the size help now has two) and lists three dials.
- Second sphere slider while it is dragged through the gap: the thumb stays under the finger and the box shows 50
  or 100; the thumb goes to its place when let go. That is how every dial of the lab treats a value its setter
  changes; I left it so.

## Thoughts that were tempting and are NOT built

- Moving the camera while the size dial is dragged past 100 (the neighbours grow out of the picture). A change of
  behaviour for Version 20's range too, so not mine to make.
- A second sphere just under 50 as the largest value (48, say), to keep the buds on a neighbour from touching.
- For rho between 1/2 and 1 only single values work; nothing was tried there.
- The rings below t = 1 with equal spheres, the sideways slide of the second sphere, coarser grids: not touched.
