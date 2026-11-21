# Round 27, fixer (Track A): what was repaired in the overlay, and what was measured afterwards

Test page: `dist/r27-fix.html` (md5 417237ec7b6e93c12e7bf075f0dc670c), built with
`python out/r27/entry/mk/bld.py r27-fix`, which is the command of `out/r27/entry/BUILD.txt` with the name changed
(no overlay file was added or removed: still eleven). The page before my edits: `dist/r27-fix-before.html` (the same
bytes as the builder's `dist/r27-entry.html`; the overlay as I found it is kept in `before/overlay/`). The frozen page:
`dist/r27-fix-base.html`. Every number below was measured by a script in `mk/` (or by a copy of a checker's script in
`cka/mk/`) on the final build unless a line says otherwise; "seen" means I looked at the picture named.
What I changed, line by line: `fix.diff` (made by `mk/mkdiff.py`).

## In plain lines

- Neighbours at 100 %: the holes are gone. In the checker's close-up 1322 of 38016 rays stopped nowhere before
  (1734 at depth 40), every one of 300 walked rays going through a ball; now 0 of 38016, at depth 16 and 40, with
  the square, the honeycomb and the line grid, and at 99 % too (where there were holes as well: 85 rays).
- Why they were there, measured: the camera of that view stands 0.00004 from a ball. The certain room the builder
  computed was half the true distance or less, the ray took half of that, and 300 steps were not enough to get away
  from the ball. Three changes: a second, larger certain room beside the place where two balls kiss ("the spindle",
  reasoned and then tested, section 1), the ray takes the Quality dial's share of the estimate (0.8 as the page
  opens, at most nine tenths) instead of half, and Balls on balls may take twice the ray steps.
- The distance is still never longer than the true distance to a ball: 0 of 16200 points in double precision at nine
  sizes from 100 % down, 0 of 25765 by the builder's own list, the spindle alone 0 of 19800, and the shader's own
  number against the checker's exact lists of balls 0 beyond single-precision noise at 41853 points near skins.
- After the one click on the row the picture, the choice of group and all three dials are in the window, wide and
  phone. The phone's Approach list shows as many approaches as the frozen page again.
- The Approach section is put away while Balls on balls is on show, exactly as for the first Kleinian group. That
  settles the open question of both checkers, removes "APPROACH: Balls on balls" over another entry's table, and makes
  Learn the same from both groups.
- The table under the picture, the trap-solid choice and the Examples list are put away for Balls on balls, each
  with one plain sentence; the untrue sentence about "Three tones" no longer shows.
- The stray stops in thin air at the starting size are gone (0 of 151281 rays more than 2 px from a ball in the
  checker's view, by the checker's own reference; 108 before). The "strays" reported at 90.9 % are not strays: each
  stands within 2 px of a real ball that is smaller than the checker's list holds.
- Not repaired: at 100 % the balls still come out swollen where the search runs out of depth (that is the recipe,
  as tree.py counts it; the page now says so); at 100 %, in the close-up with the eye all but on a ball, 99 of 38016
  rays still stop in thin air (1078 before); and in the last pixel and a quarter before a skin the 3D picture's
  number is still not the certain one (section 1, B).
- One thing got slightly worse: with the longer ray step more rays stop 1 to 2 px above a ball instead of within
  1.3 px (at 90.9 %: 215 of 38016 between 1.3 and 2 px, 8 before; at the starting size 1 of 37454).
- Unchanged: twin against tree.py 0 of 360000; 14 old pictures 0 pixels; old smoke list 90 of 90; no console errors.

## 1. Arithmetic checker

### A1 (major), holes at 100 %: fixed

Reproduced first (`mk/a1.py`, `logs/a1-before-all.txt`; the checker's views, pick() at every 4th pixel of every 4th
row, then up to 300 of the rays that stop nowhere walked with the exact inside test in quarter-pixel steps):

| view | before: stop nowhere, of them through a ball | after |
|---|---|---|
| 100 %, square, close-up, depth 16 | 1322 of 38016; 300 of 300 walked meet a ball, 135 for more than 2 px, 23 for more than 50 px | 0 |
| 100 %, square, close-up, depth 40 | 1734; 300 of 300, 126 for more than 2 px | 0 |
| 100 %, line grid, close-up | 198; 198 of 198, 185 for more than 50 px | 0 |
| 100 %, honeycomb, close-up | 0 | 0 |
| 99 % (t = 1.01), close-up | 85; 85 of 85, 47 for more than 2 px | 0 |
| 90.9 % (t = 1.05), close-up; 55.56 % three close-ups | 0 | 0 |

(After: `logs/a1-final.txt`. In the views where rays do leave the picture, the start views and the side view, 300
walked rays met no ball, before and after.) Seen: `shots/a1-before-all-t1-kiss-r16.png` has black patches,
`shots/a1-final-t1-kiss-r16.png` has none. At every second pixel, with the checker's own script: 0 of 151281 rays
stop nowhere at depth 16 and at depth 40 (5289 and 6913 on the builder's page); see the end of this section.

The cause (`mk/why.js`, `mk/why2.js`, `logs/why1.json`, `logs/why2.json`): the marcher written out in JavaScript on
the twin's numbers gives the same result as the page (118 of 119 missing rays "out of steps, far from anything"),
and the six I printed end 0.0066 to 0.0081 from the eye: they never get away from where they start. At the eye of that view the
true distance to the nearest ball is 4.2e-5, the certain room read 2.1e-5, the ray took half of it. The checker's
reading "the ray runs out of its steps" is right; it is at the start of the ray, not along it.

What I changed:

1. **The spindle** (`32-balls.js`, GL_BALLS and `ballsSpindle` for the twin). The builder's certain room measures to
   two hull balls of diameter H; at 100 % those two touch exactly where the two unit spheres kiss, and beside that
   place the room fell off like the square of the distance from the kiss while the nearest ball is as far away as the
   kiss itself. The new room: the two inversions of the recipe together hold two points of the middle line fixed
   (z = H and z = 2t - H; one point at t = 1). Every circle through both crosses both unit spheres squarely, so each
   inversion carries it onto itself. The arcs through both that reach 1/2 from the line at mid-height bound a
   spindle; between the two unit spheres it lies inside the middle cell, where the recipe says OUTSIDE, and the two
   inversions carry that piece onto the rest of it. So no ball reaches into the spindle (REASONED, then MEASURED:
   `mk/spindle.py`, `logs/spindle.txt`, part 1: 19800 points inside the spindle at eleven values of t from 1 to 1.99
   and all three grids, 400 directions each at 0.999 of the room, recipe with 400 rounds: a ball inside the room at
   0). The larger of the two rooms is used; the spindle is the larger one at 3411 of those points, nearly all at
   t <= 1.1. It is used for t under 2 (above that the other room is always the larger; none of 1800 points at 1.7 and
   1.99 had the spindle larger).
2. **Ray step** (`40-render.js`): for Balls on balls the share of the estimate a ray takes is the Quality dial's
   value up to 0.9, not capped at 0.5. The cap is the first group's, whose estimate can run long; this one is never
   longer than the true distance, so a ray that takes all of it cannot pass a ball. 0.9, not 1, so that no ray lands
   on a skin by rounding. The Quality help says so in a bracket.
3. **Ray steps** (`40-render.js`): Balls on balls gets twice the number on the Quality dial (and twice pick()'s 300).
   With 1 and 2 alone 12 and 31 of 38016 rays still stopped nowhere (`logs/a1-fix2.txt`); the written-out marcher
   said 520 steps clear all of them (`logs/why3.json`). The Quality help says so in a bracket.
4. The hold of the 3D picture (defect B) follows the ray step: see B below.

Cost: the first picture is not slower (`logs/speed.txt`, three fresh pages each: first group 976, 1075, 1063 ms;
Balls on balls 902, 895, 907 ms; by its row 876, 938, 861 ms).

### A2 (minor), solid where there is no ball at 100 %: half fixed, the rest said on the page

Two causes, and only one is a fault.
- The estimate read under half a pixel far from any ball, so the 2D view painted outline there. `mk/flat2.py`
  (the number of the 2D view through sampleSlice, 600 x 600 points of the framed view; `logs/flat2-before.txt`,
  `logs/flat2-after.txt`): points painted although the verdict is outside and nothing is inside within 2 px:
  **3568 before, 196 after** at depth 16; 3884 and 286 at depth 40; 3908 and 300 at depth 200. That is the spindle.
  I did not look at where the remaining 196 to 300 of 360000 lie.
- Points still undecided when the rounds run out count as inside, as in tree.py: 340 of 360000 at depth 16, 24 at 40,
  0 at 200, the same before and after. In 3D (`logs/a1-final.txt`): of 1200 stops in the close-up at depth 16, 84
  stand on such a region (7 at depth 40). This is the recipe, not a fault; a greater depth shrinks it and, the chain
  being endless at 100 %, never ends it. NOT changed. The page now says it: at 100 % the panel reads "At 100 the chain never ends, so the picture shows a
  stretch of it, and the balls stand so close that they read as one bar with round holes; where the depth of the
  search runs out, the far balls and the places where two balls kiss come out swollen."

### B (minor), the 3D picture's number is longer than the true distance near a skin: NOT fixed, made smaller

It is the builder's hold: within the last pixels the hull-based room would stop every ray short of the skin, so there
the ray goes on a threshold a step and is stopped by the exact distances or by landing inside a ball. I kept it. With
the ray step now 0.8 at the starting quality the hold is one and a quarter thresholds instead of two
(`clamp(1 / uStepK, 1.25, 2)`), so the number can be longer than the true distance by at most 1.25 pixels, where it
was 2; a ray still advances one threshold a step there. Removing the hold altogether is one line; I did not try it,
because the builder had looked at that picture and it stops every ray a few pixels early. Not measured: how often the
number is longer now (the checker's port of de() does not know the spindle).

### S (minor), stray stops in the open: gone at 55.56 %; not a defect at 90.9 %; fewer, not gone, at 100 %

`mk/stops.py` (`logs/stops-final.txt`, `logs/stops-before.txt`): for every stop of pick() at every 4th pixel of every
4th row, the exact distance from the stopping point to the nearest ball the search meets from there (the first
number of `ballsEstimate` with parts, 300 rounds; such a ball is a real ball whatever its size), in pixels.

| view | before | after |
|---|---|---|
| 55.56 %, the eye along the gap (the checker's view) | of 37484 stops: 17 further than 2.5 px from every such ball (furthest 6.7 px), 7 between 2 and 2.5 px | of 37454: 0 further than 2 px; 1 between 1.3 and 2 px; furthest 1.3 px |
| 55.56 %, close-up and start view | all within 1.3 px | all within 1.3 px but 2 of 9570 in the start view (1.3 to 2 px) |
| 90.9 % (t = 1.05), close-up | all 38016 within 2 px (8 between 1.3 and 2 px; furthest 1.5 px) | all 38016 within 2 px (215 between 1.3 and 2 px; furthest 1.9 px) |
| 90.9 %, start view | all 4840 within 1.3 px | all 4836 within 2 px (22 between 1.3 and 2 px) |
| 100 %, close-up, depth 16 | of 36694: 4033 further than 2.5 px: 2955 beside a region only the depth calls solid, 1078 in the open | of 38016: 3162: 3063 by the depth, 99 in the open |
| 100 %, close-up, depth 40 | of 36282: 1614: 252 by the depth, 1362 in the open | of 38016: 615: 267 by the depth, 348 in the open |
| 100 %, from 2.0 away | of 36769: 743: 676 by the depth, 67 in the open | of 36707: 690: 672 by the depth, 18 in the open |

- At 55.56 % the stray points are gone (0 where the checker found 108 of 151281 and I found 17 of 37484 with my
  measure); the checker's reference agrees (below).
- At 90.9 % the "1043 single points up to 7.0 px off" are **not strays**: every stop there stands within 2 px of a
  real ball the search meets, before and after. The checker's list of balls for t <= 1.2 holds only balls of 1 px
  radius and more, and the 120 probes miss smaller ones; those rays stop on balls smaller than that. The reference
  run again gives 1104 such points on the fixed page, as it must.
- One thing got a little worse and I say it: after the fixes more rays stop 1 to 2 px above a ball instead of
  within 1.3 px (at 90.9 %: 3479 between 1 and 1.3 px and 215 between 1.3 and 2 px of 38016, where it was 851 and
  8). At 55.56 % it is 1 stop of 37454. I did not find the cause and did not look further; none is further than 2 px.
- At 100 % stops in the open are left: 99 of 38016 in the close-up at depth 16 (1078 before), 348 at depth 40 (1362
  before). `mk/why4.js` (`logs/why4.json`) took 40 of the 99: all twelve I printed stop 0.00006 to 0.00007 from the
  eye, where a pixel is 6e-8 wide; single precision holds a place to about 1e-7. The camera of that view stands
  0.00004 from a ball. The same marcher written out in double precision does not stop there on 28 of the 40. NOT
  repaired: it is the checker's view with the eye all but on a ball, and the threshold of a ray is the marcher's,
  which the overlay does not touch.

### C (to decide): decided, see section 2, defect O

### The checker's reference, run again on the fixed page

`cka/mk/` holds copies of `out/r27/checka/mk/` with the page and the folders changed (and the path to the project,
which is one folder deeper). `cka/chain-cka.out`, `cka/logs/views.json`, pictures `cka/views/`. pick() at every second
pixel of every second row (151281 rays a view) against the checker's brute-force list of balls.

| view | the checker's numbers on the builder's page | the same scripts on the fixed page |
|---|---|---|
| 100 %, close-up, depth 16 | 5289 rays stop nowhere; where the list is complete 2098 holes, blobs to 42 px, 138 of 138 balls lost, one 441 px across | 0 rays stop nowhere; holes 0; passed through 0; balls lost 0 of 109 (0 of 297 by radius); 98 stops on solid that only the depth puts there (widest 6.9 px); 32 single stops in the open (up to 5.0 px off) |
| 100 %, close-up, depth 40 | 6913 rays stop nowhere; 3049 holes, blobs to 54 px | 0; holes 0; balls lost 0 of 169 (0 of 454 by radius); 36 by the depth; 131 single stops in the open (up to 9.4 px off) |
| 55.56 %, the eye along the gap | 0 holes; 108 stops more than 2 px from every ball, up to 5.6 px | 0 holes; balls lost 0 of 3775 (0 of 41988 by radius, down to 0.2 px); **0 stops more than 2 px from a ball**; median 0.85 px, 99 % within 1.14 px, furthest 1.37 px |
| 90.9 %, close-up | 0 holes; 1043 single points "in the open" | 0 holes; balls lost 0 of 4960; 1104 such points (see S above: they stand on balls smaller than the list holds) |

Seen: `cka/views/t1-kiss-r40.png` (no black patch), `cka/views/kiss-eyeB-r16.png` (the gap between the two big
balls, clean).
The checker's `bound.py`, part "near skins" (`cka/chain-bound.out`, `cka/logs/bound-g*-t*.txt`): the shader's own
single-precision number, read through sampleSlice, against the exact distance to the nearest ball of the brute-force
list, at 100 pieces of 15 x 15 points on the skins of random balls:

| setting | outside points | shader longer than the true distance | beyond single-precision noise | worst excess |
|---|---|---|---|---|
| square, t = 1 | 10057 | 10 | 0 | 1.1e-8 |
| honeycomb, t = 1 | 9320 | 13 | 0 | 3.9e-8 |
| line, t = 1 | 10533 | 795 | 0 | 4.9e-7 |
| square, t = 1.4 | 11943 | 20 | 0 | 1.1e-7 |

That is the class the checker found on the builder's page (7 to 18 points with the square and honeycomb grids, 839
to 1005 with the line grid, all under 5e-7). Only this part was run: the "box" part needs the points of
`verdicts.py`, which I did not run, and the columns "port" and "3D picture number" of that script come from the
checker's line-by-line port of the builder's de(), which knows neither the spindle nor the new hold, so they say
nothing about this page. Not run: the other five settings, `verdicts.py`, `bound_kiss.py`, `flat2d.py`.

## 2. Eyes checker

| defect | what was done | measured after |
|---|---|---|
| A (major) the dials are above the window after the click | `uiBallsShow` opens the Kleinian panel and brings its top under whatever is held at the top of the window (the pinned picture on a phone, the top row of the controls otherwise) | `mk/land.py`, `logs/land-before.txt` / `land-final.txt`. Wide: choice of group at -568 before, 140 after; picture top -175 before, 12 after; Frame it ends at 769 of 950. Phone: choice at 164 under a picture that ends at 390 before; 442 after, first dial at 682 of 800. Seen: `shots/land-after-wd-1-right-after-the-row.png`, `shots/land-after-pd-1-right-after-the-row.png` |
| B (major) the phone's list shows one and a half approaches | on a narrow window the heading stands in the row's own first line and the explanation under the list gives up the height the row takes (`86-balls.css`) | list 89 px with 1 whole approach before; 169 px with 4 after (the checker measured 170 and four on the frozen page; I did not measure that page again), opened the way the checker opened it. Opened with a finger-like click (no explanation box): 7 whole approaches. Seen: `shots/land-after-pd-0-menu-open.png`, `shots/lay-390x800-light-menu.png` |
| C (major) the untrue sentence about Three tones | its rule now excludes Balls on balls | `logs/look-final.txt`: with a trap solid set from elsewhere and the Sphere shell: one sentence, not two; with Three tones: the same one sentence |
| D (major) the Examples list | the choice "In the 3D view the trap" is put away for Balls on balls, and the Examples list, which stands under it and follows it, goes with it; one sentence stands there: "Balls on balls has no trap solid, and so none of the examples, which are all trap solids: in this view the trap only colours the balls." A choice made in another view is kept for that view | `logs/look-final.txt`, `logs/ui.json`. Seen: `shots/look-final-cd-colour-section.png` |
| E (major) another entry's table under the picture | while Balls on balls is on show the table is put away and one sentence stands under its heading: "Balls on balls is not a rule that takes a point to a power and adds c, so it has no rows in this table." (body gets the class `balls-on`; not under Learn, where the table is the approach's) | `logs/look-final.txt`. Seen: `shots/look-final-e-table-under-the-picture.png`. The section "One step, seen on directions" beside it still shows the approach's figures: not changed, not in decision 7 |
| F (minor) 100 % shows no balls, the warning never goes | the sentence at 100 % says what is on the screen (above, A2), with its own form for the line grid and for the 2D view; from 99 % down the old sentence about the Drawing radius, which Frame it or the dial can answer | seen: `shots/look-final-f-100-square-3d.png` (a bar with round holes), `-f-100-line-3d.png`, `-f-100-2d.png` (a band with holes), `-f-100-panel.png` |
| G (minor) depth 1 to 4 looks broken | the dial starts at 5, typed values too (`BALLS_ROUNDS_MIN`); the twin still takes any number of rounds | slider min 5; a typed 1 gives 5 |
| H (minor) the depth help | "How many rounds of the search a point may take before it counts as inside: the larger the neighbours, the more rounds the far balls of the chain need, and with too few they come out swollen." | |
| I (minor) "Direction of the last step" is one pale pink | one sentence in the 3D view: "On Balls on balls the last step lands somewhere different for every point of a ball, so in the 3D view this choice blends into one pale colour: it is at its best in the 2D view." | seen: `shots/look-final-i-last-step-3d.png` (pale), `-i-last-step-2d.png` (a full pattern) |
| J (minor) mirror discs in different colours | the first group's sentence about it now shows for both groups | `logs/look-final.txt` |
| K (minor) the explanation box keeps another entry's text | the row has its own explanation (name, label, the note, "One click shows it in the Kleinian view, where its three dials are."), with the mouse over it and with the keyboard on it | seen: `shots/look-final-k-hover-on-the-row.png`. Pointer events made by script |
| L (minor) helps of three or four sentences | one sentence each; the one about the grid no longer speaks of slides | `logs/look-final.txt` |
| M (minor) "t = 1.4" in the saved model | taken out of `meshWhat` | `mk/model.js`, `logs/model.json`: a 48-cell model saved through the page's hook reads "Made from: Balls on balls (slides by whole numbers and sphere inversions), neighbours 55.56 % of the middle ball, square grid, depth of search 16." |
| N (minor) "Nothing else changes." | the tooltip of Frame it: "Move the camera to a view that shows the whole chain. A zoom limit or a Drawing radius that is in the way is moved as well." | |
| O (minor) Learn differs between the groups; and C of the other checker | the Approach section is put away while Balls on balls is on show, as for the first group; an approach chosen from a script stays in the Kleinian view, as on the frozen page; the way back is the Show buttons. `uiBallsMenu`, `uiBallsLeave`, the watcher on body's class and `UI.ballsBack` are gone | `logs/look-final.txt`: under Learn the section is on show and the table is the approach's from both groups; back from Learn it is put away from both |

Which pictures I looked at, and on which build. On the final build: `look-final-cd-colour-section.png`,
`look-final-e-table-under-the-picture.png`, `look-final-f-100-line-3d.png` (a row of equal balls with holes between
them along the flat picture), `look-final-f-100-panel.png` (the bar with round holes and the panel beside it),
`land-final-pd-1-right-after-the-row.png`, `lay-390x800-light-menu.png`. On the build before the last two edits (one
comment reworded, one line of the shader written another way; nothing of the controls): the same pictures under the
names `look-a-*` for defects F (square 3D and 2D), I and K, and `land-after-*` for A (wide) and B. The pictures
`look-final-*` and `land-final-*` of those were made and not looked at.

Decision 3 as it now reads on the page: the row is in the Approach list (one click); after the click the page is in
the Kleinian view like any other; "choosing any real approach afterwards" is done after leaving by Show: Mandelbrot or
Julia, where the approaches behave as they always did. If the orchestrator wants the menu kept on the page while
Balls on balls is on show, the builder's version of `80-ui.js` is in `before/overlay/`.

Wording of the new sentences: read against section 4 of ROUND27.md by me; no forbidden word found by reading. Not
checked by a script.

## 3. What the fixes could have broken: the re-runs (all on the final build, one after the other)

`logs/chain-final.out` holds the ends of all of them; the page's md5 was the same before and after the chain.

- **Twin against tree.py** (`mk/twin_check.py`, `logs/twin-check.txt`): 0 of 360000 verdicts differ. (The twin's
  inside test was not touched.)
- **Shader against twin** (`mk/verdict.js`, `logs/verdict.json`): 0 of 241968 differ at t = 1.4 and 2.5; 13 of
  120984 at t = 1, the twin's distance under 5e-8 at each (the same 13 as before the fixes). Shader's distance
  against the twin's: largest relative difference 0.04 % at t > 1. At t = 1, one point of 120984 where the shader's
  number is 2.2 % longer than the twin's; my reading, not measured: the two land on different sides of the edge of a
  piece, and both numbers are certain rooms.
- **Never longer than the true distance** (`verdict.js` part C, changed in one place: a probe that 60 rounds call
  inside is asked again with 4000 rounds): 0 of 25765 outside points; 6 probes were only undecided at 60 rounds.
  Before that change of the script it reported 5 "breaks" at t = 1; `mk/breaks.js` (`logs/breaks.json`) took the
  same points: none of those probes reaches a wall, each is OUTSIDE after 63 to 253 rounds. So: the estimate is never
  longer than the distance to a ball, but beside a kiss at 100 % it can be longer than the distance to a point that
  only a shallow depth calls inside. A checker who counts "undecided" as "inside a ball" will see those.
  `mk/spindle.py` part 2 (decided inside only, 400 rounds, 400 directions): 0 of 16200 outside points at t = 1, 1.003,
  1.02, 1.05, 1.1, 1.2, 1.4, 1.99, 2.5, three grids, in the box and close to the kiss.
  How tight now at t = 1 (`verdict.js` part C, 8188 outside points of the three grids): a ball within 3 d for 74 % and
  within 5 d for 99 % (the builder measured 59 % and 89 % with the same script before the spindle); at t = 1.02
  within 2 d for 92 % of 300 points; unchanged at 1.4 and 2.5.
- **3D picture, the builder's check** (`mk/holes.js`, `logs/holes.json`): 0 of 58368 probes hit by the slow march and
  missed by the page. At t = 1.4 and 2.5 (16 views): every page hit within 1.3 px of a ball its search met, none
  behind the slow march. At t = 1 (3 views): 7, 11 and 26 hits further than 2 px from a ball (worst 17.7 px) and 2 and
  18 behind: those are the depth, as before the fixes (the slow march uses 80 rounds, the page 16).
- **Old pictures** (`mk/same.py`, `logs/same.txt`): 14 states (7 first Kleinian group, 3 Mandelbrot, 4 Julia), the
  picture alone, against the frozen page: 0 pixels differ in all 14.
- **The first group's panel** (`mk/oldpanel.py`, `logs/oldpanel.txt`): its 14 controls stand at the same places
  relative to its first note as on the frozen page.
- **Old smoke list** (`mk/smoke27.py`, `logs/smoke-all.log`): 90 steps, 90 results, exit 0, no console errors, in one
  run. One earlier run on the build before stopped at step 7 (`logs/smoke-all.run1-stopped-at-step-7.log`): that step
  reads the whole text of the body, scripts included, for old wordings, and a comment of mine said "the chain has no
  end". The comment was reworded.
- **Controls** (`mk/ui.js`, the builder's list with its expectations changed where the page changed, by
  `mk/patch_uitest.py`; `logs/ui.json`): exit 0, no console errors; picture export 1.0 MB, a 48-cell model, Learn,
  both resets, 7 colourings, 8 trap shapes, 6 colours-by, 5 inside colourings.
- **Layout** (`mk/layout.py`, changed by `mk/patch_layout.py`; `logs/layout.txt`): 1400x950 and 390x800, dark and
  light: the open menu fits with the row whole, 7 new pieces inside the window, none overlapping, no text cut off,
  page not wider than the window; no console errors. Seen: the phone menu in light, the wide panel at 100 % in dark.
- **Speed**: above.

## 4. Overlay files I changed (`fix.diff`)

- `js/32-balls.js` (+42 -7): the spindle in GL_BALLS and in `ballsEstimate`; the hold follows the ray step;
  `BALLS_ROUNDS_MIN`; `ballsTrouble` says what is on the screen at 100 %.
- `js/40-render.js` (+7 -2): for Balls on balls the ray step up to 0.9 and twice the ray steps.
- `js/80-ui.js` (+56 -46): the Approach section put away as for the first group; `uiBallsShow` brings the panel into
  view; `uiBallsInfo`; the three helps; the depth dial from 5; the two brackets in the Quality helps; the class
  `balls-on` on body. Gone: `uiBallsMenu`, `uiBallsLeave`, `UI.ballsBack`, the watcher on body's class. So the two
  things the builder said the merge with Learn must keep true are no longer needed.
- `js/25-colour.js` (+8 -4): the trap-solid choice put away for Balls on balls with one sentence; the Three tones
  rule; the mirror sentence for both groups; the sentence for "Direction of the last step".
- `js/46-mesh.js` (+1 -1): no "t =" in a saved model's description.
- `css/86-balls.css` (+16 -4): the row on a narrow window; the table's sentence; rules of the kept menu removed.
- `body.html` (+2 -1): the table's sentence; the tooltip of Frame it.
- Not changed: `js/00-core.js`, `js/50-camera.js`, `js/75-presets.js`, `js/90-boot.js` (still `src/` plus added
  lines only). `src/` still equals `base18a/` for every file the overlay replaces (checked with cmp).
- `out/r27/entry/changes.diff` and `out/r27/entry/NOTES.md` are the builder's and describe the overlay before these
  changes.

## 5. Not checked

- A real mouse, a finger, a real keyboard on the row (events were made by script).
- The Fine, Fast and Ultra fast presets, the fly camera, extreme ranges, a lost graphics context, the published host.
- Sizes between 99 % and 100 % in 3D pictures other than the one close-up at 99 %; the honeycomb and the line grid
  in 3D at 99 % and 90.9 %.
- A saved model opened in another program; the saved picture was only counted in bytes.
- How often the 3D picture's held number is longer than the true distance now (B).
- Whether twice the ray steps slows a slow graphics card in the moving preview (120 steps became 240 there).
- Anything against `src/` or with round 26's Learn files in the page.
- The light theme and the phone for the new sentences in Colour and light (seen wide and dark only).
