# Round 29, Track A ("free"): the builder's notes

Page: `dist/r29-free.html`, built with the line in `out/r29/free/BUILD.txt` (frozen copy `base21a` plus three overlay
files). Frozen page for comparison: `dist/r29-free-base.html` (base21a alone). Every number below comes from a script
in `out/r29/free/mk/` and a log in `out/r29/free/logs/`. "Seen" means I opened the picture. Nothing was published,
nothing under `src/`, `base*/`, `out/r2[0-8]*/` or the Learn files was written, no git command was run.

## In plain lines

1. The automatic rule is gone. Each of the two dials sets its own number and nothing else: size 2 to 400 on the
   slider (typed 1 to 2000), second sphere any value from 2 to 100 (slider in whole numbers, typed with two
   decimals, no jump). Driven with a real mouse and real keys: 87 checks on the wide window, 87 on the phone, 45 more
   in the dark theme, 0 wrong, no console error or warning.
2. Every picture Version 21 could make is the same to the pixel: 24 states (the ten old states in 3D and 2D, a
   close view, three that are not Balls on balls), 0 pixels differ, and the two old program texts are the same to the
   byte. Round 28's own comparison (nine states) also gives 0.
3. Every other pair of numbers is drawn by a third program, `GL_BALLS_FREE` (key `balls3`, name `k-balls3`,
   uniforms `uBT`, `uBRho`, `uBGrid`).
4. One recipe, three voices, on both panels (1.56 million points): the twin and my own writing of the recipe never
   differ (0). The shader differs at 112 points of the new panel and 10 of the old one; every one of them lies within
   a ten-thousandth of a place where the recipe itself changes its verdict (single precision on an edge).
5. The new distance against the truth (the recipe alone on a fine grid, and a distance transform of it): never too
   long on the flat cuts and in two boxes in space, for every new state but one. The one is Y5, where the two spheres
   touch: 0.83 % of the flat cut too long at depth 16 (0 at depth 60), as Version 21's own touching states are (1.10 %
   and 0.54 % by the same measure).
6. The 3D view against rays walked with the recipe alone: 29 views, 0 holes. Of the stops the first probe called
   "in the air", all but 2 (of 4754, one view of Y1) have something inside within 4 pixels: thin parts.
7. Stray outline pixels in the 2D view, per state: 0 at nine states, 10 at Y3, 41 at X6, 85 at Y1, and 309 to 762 at
   X1, X2, X7, X9 and Y5 (the last five where the depth of 16 runs out; X9 has 0 at depth 60). Version 21's own two
   touching states have 1217 and 295 by the same measure. Y1's 85 are a real fault of the distance (see "Not right").
8. Speed: a picture of Y1 takes 1.28 x the time of Version 21's (150, 33.33). A picture of X1 takes 7.8 x, X6 3.7 x:
   over the line of three. One distance costs no more (0.5 x at X1); the picture is full (97 % of its rays stop on
   something, against 22 %). See "Not right".
9. I added one thing the brief did not ask for: in the 3D picture of the new program the solid ends at the Drawing
   radius, so the lump has a lit skin instead of a black one (see "Decisions", E).

## The overlay: every file, one line each

All under `out/r29/free/overlay/js/`. `out/r29/free/changes.diff` is the full difference against `base21a`
(`mk/frozen29.py`; 32-balls.js 101 lines out and 539 in, 40-render.js 10 and 15, 80-ui.js 58 and 10).

- `32-balls.js`: the state helpers (`ballsRho` a plain clamp to 0.02 ... 1, `ballsT` the number as it stands above
  0.5001, `ballsKind`, `ballsTOf`, `ballsMeet`), the two setters that set one number each, the twin `ballsInside`
  without a clamp, `ballsEstimate` with a third branch (`ballsFreeSet`, `ballsFreeRoom`), reach, start view and Frame
  it, the sentences (`ballsTrouble`, `ballsFarFilled`, `ballsFlatFilled`); `GL_BALLS` and `GL_BALLS_RHO` and the two
  long comments above them untouched (22231 characters, the same to the byte); the new text `GL_BALLS_FREE` after them.
  Gone: `BALLS_DIAL.follows`, the jump in `ballsRhoFrom`, the give-way in both setters, `BALLS_RHO_MAX`.
- `40-render.js`: the third program and its key (`sceneWant`), `sceneKlein` answers `ballsKind()`, `sceneBalls` knows
  `balls3`, `uBT` is `ballsTOf(kind)` and `uBRho` goes to both programs that have it, the background warming prepares
  the other two Balls programs first.
- `80-ui.js`: the two dials without `sync` of each other; the arrow-key special case, the typed-follow lines, the
  "From 2 to 50, or 100" words and their observer are gone; two new help texts (see "Decisions", 3).

No change to `00-core.js`, `46-mesh.js`, `50-camera.js`, `90-boot.js`, `body.html`, any CSS, any Learn file.
`46-mesh.js` needed nothing: a 3D model samples the scene program through `sampleSlice`, so it gets the new program
by itself, and its sentence reads the state through `ballsRho`. Made at Y1 (5,624 triangles) and at X1 (55,528
triangles, "the largest of 33 pieces") with the page's own buttons.

The overlay files are written by `mk/make_overlay.py` from `base21a` and three parts in `mk/parts/` (it copies the two
old program texts as they are). They can also be edited directly.

## What must be true (section 4), point by point

### 1. Verdicts (`mk/voices29.py`; `logs/voices-new.txt`, `voices-old.txt`)

Each state: the flat cut on a 160 x 160 grid and fourteen 48 x 48 grids at other heights (57856 points), the shader
through `sampleSlice`, the twin read from the page, and `kit29.recipe` (numpy, written from section 1 of the brief).

- New panel, 17 states, 983552 points: twin 0 differ. Shader 112 differ: X1 26, X2 26, X4 14, X6 6, X9 16,
  X9 at depth 60 22, Y5 2, the other ten states 0. For each of them my own writing gives the other verdict within
  1e-5 of the point at 110 and within 1e-4 at all 112.
- Old panel, 10 states, 578560 points: twin 0. Shader 10 (8 at (100, 100), 2 at (200, 50): Version 21's own
  programs, where the spheres touch), all within 1e-5 of a change of verdict.
- The shader's distance against the twin's where both say outside: more than 1 % apart at 42 of about 700000 points
  (new panel) and 6 (old panel). They lie where one piece of the distance hands over to another (a point that takes
  one round more in single precision has fewer rounds left, see D below).
- The twin's distance against the numpy prototype (`kit29.estimate`), on which the truth was measured: the same to
  6e-8 at every point of the new panel.

### 2. Old pictures (`mk/same29.py`, `mk/frozen29.py`; `logs/same-1400x950-dark.txt`, `logs/frozen.txt`)

The numbers are written into the state on both pages (Version 21's dials cannot be set to a pair one by one).
24 states, picture alone, 862 x 701: 0 pixels differ. Every program text handed to the graphics card was caught
(`shaderSource`) and is the same on both pages (k-balls 59719 characters, k-balls2 60433). The camera is the same in
all 24. The sentence differs in 11, as decided: "Past 100 the second sphere has to be smaller ..." is gone and
"The second sphere is now X % of the first. Reset this section puts it back to 100." stands there.

### 3. The distance is safe (`mk/proto.py` with `mk/kit29.py`; `logs/proto-flat.txt`, `proto-flat-depth60.txt`, `proto-box.txt`)

The reference: the recipe alone on a grid 900 wide of the flat cut (about the start view), and in two boxes of 160^3
points (one round the place where the middle ball and a neighbour meet, one above the middle ball); the true distance
is a distance transform of the grid. "Too long": longer than the truth by more than 2 % and one grid step.

| state | flat cut, depth 16: too long, worst ratio | flat cut, depth 60 | boxes: too long, worst ratio |
| --- | --- | --- | --- |
| X1 (120, 100) | 0 of 233917, 1.006 | 0, 1.000 | 0, 0.998 |
| X2 (130, 100) | 0 of 80301, 1.018 | 0, 1.000 | 0, 0.995 |
| X3, X4, X5, X8 | flat cut all inside | | X3 0, 1.000; X4 0, 1.132; X5 0, 1.023; X8 all inside |
| X6 (150, 75) | 0 of 428902, 1.000 | 0, 0.999 | 0, 0.999 |
| X7 (300, 50) | 0 of 314633, 1.491 | 0, 1.127 | 0, 1.001 |
| X9 (105, 100), 16 and 60 | 0 of 479571, 1.026 | 0, 0.999 | 0, 0.995 |
| Y1, Y2, Y3, Y4, Y6, Y7 | 0 each, 0.981 to 0.998 | | 0 each, 0.912 to 1.000 |
| Y5 (133.33, 75; touching) | 4413 of 531808 (0.83 %), 3.218 | 0, 1.198 | 12 of 1272766 and 531 of 1434284 (0.037 %), 2.05 |

For comparison, Version 21's own touching states by the same measure (flat cut, depth 16, prototype of
`GL_BALLS_RHO`'s lines): (100, 100) 1.10 % too long, worst ratio 3.67; (200, 50) 0.54 %, 3.08; both 0 at depth 60.
So the line "99.9 %, never more than one and a half times" holds for sixteen states and not for Y5, where the chain
never ends and the depth of 16 leaves its far balls undecided (the sentence on the page says so).
Median of estimate / truth: 0.54 to 0.97 in the Y states' boxes except Y5 (0.33 and 0.36), 0.50 to 0.95 in the X
states' except X4 (0.08 and 0.14: honeycomb at 150, where little of the cell is in the open and the rooms are small).

### 4. The distance is not wrongly small (`mk/looks29.py`; `logs/looks-new-1400x950-light.txt`, `looks-old-...txt`)

2D view as Frame it gives it, light theme, 862 x 701; the middle 701 x 701 pixels measured. Outline pixel: the
distance the program hands out is above 0 and under 1.5 pixels. Stray: more than two pixels from every place where
the recipe changes its verdict (the recipe on a grid four times as fine, and at the pixels' centres).

| state | outline pixels | stray | | state | outline pixels | stray |
| --- | --- | --- | --- | --- | --- | --- |
| X1 | 34222 | 309 | | Y1 | 10894 | 85 |
| X2 | 17632 | 762 | | Y2 | 7814 | 0 |
| X3, X4, X5, X8 | 0 (filled) | 0 | | Y3 | 15154 | 10 |
| X6 | 27394 | 41 | | Y4 | 10300 | 0 |
| X7 | 20598 | 511 | | Y5 | 24174 | 611 |
| X9 | 28988 | 348 | | Y6 | 8818 | 0 |
| X9 at depth 60 | 26822 | 0 | | Y7 | 5358 | 0 |

Version 21's own programs by the same measure: (100, 100) 1217 of 28176, (200, 50) 295, (150, 33.33) 10, the other
seven 0. The shader's verdict against the recipe away from every edge: 0 pixels differ in all 27 states.
No lines along sphere surfaces and no dots where spheres cross (seen in the 2D pictures of X1, X2, X6, X7, X9 and
Y1 to Y7 beside pictures made from the recipe alone: `shots/look-<state>-sheet.png`). What is left:
X1, X2, X7, X9, Y5: along the side of a hole or of the chain where the depth of 16 runs out (seen at X2: the upper
rim of each large hole is ragged and its outline there is a few pixels thick; `shots/look-X2-2d-stray.png`).
Y1, Y3: small blobs of outline beside the tiny lens-shaped bodies on the two neighbours ("Not right", 2).

### 5. The 3D view (`mk/rays29.py`, `mk/air29.py`; `logs/rays.txt`, `rays-X2-X3-X4-X5-X7-X8.txt`, `air.txt`)

Every new state at two views (the start view; a second one from another side, six tenths as far away), every 8th
pixel of every 8th row (9504 rays): `pick()` in the page against a walk of the same ray with the recipe alone in
steps of half a pixel. 29 views counted; in 5 (the second view of X2, X4, X5, X7, X8) the eye stands inside the
solid and nothing was counted.

- Holes (the page's ray stops nowhere or more than 3 pixels behind the reference, where the solid is more than 2
  pixels thick): 0 in all 29 views.
- Stops where nothing inside lies within 2.5 pixels (first probe, 79 points): 0 in 14 views; X1 6 and 3, X6 70 and 83,
  X9 100 and 141, X9 at depth 60 138 and 195, Y1 40 and 108, Y3 16 and 30, Y5 53 and 108, Y6 1. Looked at again with
  3000 points within 4 pixels of each: every one has something inside within 4 pixels (parts thinner than the first
  probe sees), except 2 of the 108 at Y1's second view.
- The page stops a median of 1.2 to 3.6 pixels in front of the reference along the ray (it stops on a level above
  the skin, and these skins are mostly seen at a slant); 0.00 where the whole picture is the skin of the lump.
- Seen, light theme: Y1, Y2, Y4, Y5 (start and second view), X1, X3, X6, X7, X8, X9. Y states: whole balls with
  buds, no holes, no speckle. X6, X9: a clean band of sponge with round holes. X1: a sponge that fills the picture.
  X7, X8 (and X2, X4, X5): the lump fills the whole picture, so the start view shows only its lit skin, a plain field
  of colour ("Not right", 4).

### 6. Speed (`mk/speed29.py`, `mk/speed29b.py`, `mk/steps29.py`; `logs/speed.txt`, `speed-b.txt`, `steps.txt`)

One page, warming off, 1400 x 950, medians of five, the whole picture (12 passes) drawn again from nothing:

| state | program | whole picture | against V21's (150, 33.33) | rays that stop on something | one distance in the open |
| --- | --- | --- | --- | --- | --- |
| V21 (150, 33.33) | k-balls2 | 110 ms | 1.00 | 22 % | 1.00 |
| V21 (55.56, 100) | k-balls | 133 ms | 1.21 | 25 % | 1.03 |
| V21 (100, 100) | k-balls | 185 ms | 1.67 | 20 % | 0.86 |
| Y1 (80, 75) | k-balls3 | 142 ms | 1.28 | 22 % | 0.91 |
| Y2 (60, 60, honeycomb) | k-balls3 | 140 ms | 1.27 | | |
| X4 (150, 100, honeycomb) | k-balls3 | 258 ms | 2.34 | | |
| X6 (150, 75) | k-balls3 | 409 ms | 3.71 | 44 % | 0.51 |
| X9 (105, 100) | k-balls3 | 417 ms | 3.76 | 32 % | 0.51 |
| X1 (120, 100) | k-balls3 | 859 ms | 7.79 | 97 % | 0.50 |

("One distance in the open": 512 x 512 queries that run the recipe to OUTSIDE and work out the room, against the
same at V21's (150, 33.33).) A ray of X1's start view takes 17 strides on average by my own marching of the prototype
(median 15, nine in ten under 32, none runs out), 14.6 without the guard for the depth.

### 7. The dials (`mk/dials29.py` with round 28's `hand.py`; `logs/dials-wide-light.txt`, `dials-phone-light.txt`, `dials-wide-dark-words-frame.txt`)

Real mouse presses, moves, releases and real keys. Wide 1400 x 950 and phone 390 x 800, light theme: 87 checks each,
0 wrong. Wide, dark theme, the sentences and Frame it: 45 checks, 0 wrong. No console error or warning in any run.

- Typed sizes 150, 300, 101, 99.99, 2000, 80: the second sphere stays 100. Typed second spheres 62.5, 33.33, 50, 75,
  99, 2: t does not change. Size slider dragged from 60 to 390 with the second sphere at 40: 54 readings on the way,
  the second sphere showed 40 in every one. Second sphere slider dragged from 40 to 97 at size 150: the size showed
  150 throughout.
- Second sphere: the slider reaches 100, 99, 76, 75, 74, 63, 51, 50, 49, 2, 60, 88; ArrowUp from 50 gives 51, 52, 53;
  ArrowDown from 100 gives 99, 98, 97; on the slider Left and Right step by 1; typed 62.5 is 62.5; the two small step
  buttons go to the next whole number.
- Typed limits: size 5000 gives 2000, 0.2 gives 1; second sphere 1 and 0 give 2, 250 gives 100; depth 0 gives 1,
  5000 gives 1000. Sliders dragged past their ends stop at 2 and 400, 2 and 100, 1 and 100.
- Reset this section after 300 / 62.5 / 40 / honeycomb: 55.56 / 100 / 16, t exactly 1.4, rho exactly 1, no sentence.
- Sentences, 17 states (3D and 2D), word for word as section 2 fixes them: all as expected.
- Frame it, all 26 states of both panels, 3D and 2D: the middle ball and both neighbours lie in the picture. The
  least margin: 0.40 of a ball's own radius in 3D (the old state (60, 40, honeycomb)), 0.081 of the view's height
  in 2D (the same state); for the new states 0.53 (Y2) and 0.098 (Y2).
- A 3D model at Y1 and at X1: made and saved (see above).

### 8. Old checks on the new page (`mk/old29.py`; `out/r29/free/old/`)

(All four were run again on the final page; the numbers are of that run.)

- Round 27 `verd.py`: twin against tree.py 0 of 80000, shader 0 of 40644.
- Round 27 `shape.py`: its report is the same as round 28's final run of it, line for line, apart from the page's name.
- Round 28, the builder's `same.py` (nine states, new page against base21a alone): 0 pixels differ.
- Round 28, the eyes' `same.py` (sixteen states and the whole window): 0 pixels differ in fifteen. The sixteenth,
  "second sphere there and back", walks the automatic rule itself (size 150, second sphere 50, back to 100, "which
  must give 50"): on the new page the size stays 150, so the two pages show different states. That is the change
  the user asked for (604262 pixels). The whole-window comparison then differs by 14 to 24 pixels in one row (the
  handle of the zoom slider) in three later states (five in an earlier run): Frame it in that one state moved a
  zoom limit differently, and round 27 already noted that this handle differs between two runs of one page.
- NOT run by me: the old smoke list (90 steps), round 26's lists, round 27's `same6.py`, `holes.py`, `flat.py`,
  round 28's `holes28.py`, the phone in the dark theme.

## The new distance: what was built, and what of the brief's toolbox held

The long comment above `GL_BALLS_FREE` says it in the code's own words. In short (m: the place where the recipe ends
OUTSIDE, in the middle cell, between the walls, outside both spheres):

- **A, the two spheres apart or touching, second sphere between 1/2 and 1.** T4 holds for any size of the second
  sphere, the rest on the top wall included: `GL_BALLS_RHO`'s lines as they stand (with rT = rho). Measured: 0 too
  long at Y1, Y2, Y3, Y4, Y6, Y7, flat and in space. In place of the side spindle there is the side ring (C).
- **B, the two spheres cut into each other.**
  - T1 holds and is simpler than the brief has it: the picture is its own mirror image in every wall of the cell, so
    a ball beyond a wall has a twin on this side that is nearer. Only the two spheres of the middle cell count.
    Alone it inks 12 % of the outside of X7 and X9 as outline.
  - T2 holds, with one change: behind a mirror the other spheres count each in its own cell only (the larger of the
    distance to the sphere and the distance to its cell). The first bud behind each mirror is a ball of the picture;
    its true distance goes into "best". Alone, T2 leaves 0.35 % (X7) and 0.77 % (X9) wrongly under a pixel.
  - T3 holds and goes further than three rings. Any ball that crosses both spheres squarely is carried onto itself
    by both inversions; if it lies in the cell, or is centred on a wall or an upright edge of the cell and reaches
    no other wall, the slides do the same. If it also lies between the walls, nothing in it is ever INSIDE. Those
    balls have their centres at the height of the crossing circle and radius^2 = (distance from the middle line)^2
    - q0^2. The brief's first ring is the family of them at one distance (the spindle's formula with d2 < 0). The
    one centred on the wall is the large one: in the flat picture the round holes ARE these balls, so with the
    rounds not running out the distance there equals the truth (worst ratio 1.000 at depth 60, X1, X2, X9).
    The brief's third ring (first sphere and its copy) is not needed: with the cells in T2 the room there is not zero.
  - C, the side ring (second sphere and its copy, rho > 1/2): the side spindle's formula with c2 < 0, kept clear of
    the first sphere (a closed form for the largest w) and inside the two cells.
- **D, the depth of the search.** Not in the brief. The rooms of B and C are rooms of the object at endless depth,
  and at depth 16 the far side of every hole is still undecided and counts as inside: without a guard 14.5 % of X2's
  outside points were too long (worst ratio 5.4). So those rooms are made smaller by the rounds the search had left:
  none while fewer are left than the fan round the crossing circle has pieces, then the share
  1 - exp(-rhoT (left - fan)); the side spindle at rho <= 1/2 gets (left - 1) / (left + 8); with no round left only
  the two sphere surfaces are trusted. FITTED to the reference, not proved (three numbers: the fan, rhoT, the 8).
  Its price: the outline beside an undecided rim is a few pixels thick (the strays of X1, X2, X7, X9).
- **E, the Drawing radius** (my addition, see "Decisions").
- Two places where rounding chose between shader and twin were found and closed: a ball on a wall exists only for
  rho > 1/2 (its limit is rho^2 - 1/4, which is 0 at exactly 1/2: the shader said yes, the twin no, and at X7 the
  two were up to twice apart), and the fan is taken a thousandth under its value.

## Not right

1. **Speed at the X states, by the letter of point 6.** X1 7.8 x, X9 3.8 x, X6 3.7 x the frame time of Version 21's
   (150, 33.33); the line is three. One distance is not dearer (half the cost at X1), and a ray takes 17 strides.
   What differs is the picture: at X1 97 of 100 rays stop on something and then ask for slope, shadow and crevice,
   against 22 of 100. Per ray that stops, X1 costs about 1.7 x V21's (150, 33.33) and about as much as V21's own
   (100, 100). I did not find a way to make a full picture cheap.
2. **Y1 and Y3: small blobs of outline where nothing is (85 and 10 pixels).** With the second sphere between 1/2 and
   1 its copies cut into each other, and the walls of the cell inside them are creases: the picture is mirrored
   there, not carried on. The distance follows the recipe's own chain across the crease and meets balls that exist
   only on the other side of it. So next to the tiny lens-shaped bodies on the neighbours it is under a pixel and a
   half in blobs of up to about 7 by 14 pixels where nothing is (seen: `shots/crease-Y1-strays.png`, the page's 2D
   picture with the strays marked, and `shots/crease-Y1-zoom.png`, the recipe alone round the picture point
   (-1.326, 0.3705) with the distance under a pixel and a half in red). It is never too long there
   (a ball beyond a flat mirror has a nearer twin; measured 0 too long). The cure I see and did NOT build: carry the
   nearest crease along the chain as a sphere, and leave out every ball and hull that lies wholly beyond it.
   In 3D the same thing can stop a ray: 2 stops of 4754 in one view of Y1 had nothing inside within 4 pixels.
3. **Y5 (touching): the distance is too long beside the undecided far balls at depth 16** (0.83 % of the flat cut,
   worst ratio 3.2; 0 at depth 60). The same as Version 21 where its spheres touch. The guard D is not applied where
   the spheres are apart or touch.
4. **A lump that fills the picture shows only its skin.** After Frame it at X2, X4, X5, X7, X8 the 3D picture is one
   plain field of colour: the eye stands 13 to 20 away and the lump is 9 to 13.65 in radius. The brief's decision 5
   (frame as for the endless chain) is built as written. Standing back to about three and a half Drawing radii would
   show the lump whole; I did not change the decision.
5. **Where the depth of 16 runs out in the X states** the holes come out smaller on one side with a ragged rim, in 2D
   and 3D (the recipe's own picture at that depth; X9 at depth 60 is clean). No sentence says so there: the fixed
   texts for cutting spheres do not mention the depth.
6. The shader's verdict differs from the recipe's at 112 of 983552 points, all on an edge. Version 21 has 10 of
   578560 by the same check.
7. The guard D is fitted on eight states (X1, X2, X6, X7, X9 at two depths, flat and in space). Other pairs of
   numbers were not measured against the truth; a pair with a much smaller angle between the spheres than X9's, or a
   depth under about 8, may be too long beside undecided parts.
8. The safety numbers of point 3 were measured on the numpy prototype, which the twin equals to 6e-8 and the shader
   to 1 % at all but 42 points; the shader itself was not put against the truth point by point.

## Decisions I had to make (please check them)

A. **Touching and cutting "as the dials show them"** (`ballsMeet`). Two equal spheres: 100 as shown is touching,
   100.01 and more is cutting. Otherwise the product of the two shown numbers within their rounding of 100 x 100 is
   touching (Y5: 133.33 x 75), beyond it cutting. The program is chosen from the state itself, not from this.
B. **The size as typed.** With the second sphere at 100 the number counts as it came, beside a smaller second sphere
   with two decimals: both as in Version 21, so that the same typing gives the same state as before.
C. **The sentences.** The cutting sentence stands in place of the three chain sentences. "The Drawing radius ...
   cuts the two big neighbours open" is shown for cutting states too, but not when the lump sentence is.
   "With the second sphere at 50 ..." only at exactly 50 and only where the spheres are apart (not when touching:
   as in Version 21).
   - "Far out everything is filled ...": the brief says to test a few far points. I test fourteen directions at 20
     and at 2000 times the Drawing radius (all inside), AND ask that at least three in ten of 120 directions on the
     ball of the Drawing radius itself are inside. Without the second part the sentence stood under pictures that
     are a band with open sky (X6: 44 % of the rays stop). With it: shown wherever 97 % or more of the rays stop,
     not shown where 78 % or fewer do (`mk/lump.js`, 36 pictures), with one exception ((250, 45, line) at Drawing
     radius 30: shown at 55 %).
   - "The flat picture is filled completely.": the recipe on a 60 x 40 grid of the 2D view as it stands AND of the
     2D view Frame it gives, so that a view from deep inside one ball does not count.
D. **Help texts** (the old ones described the automatic rule and the jump). Size: "How wide the two big neighbours
   are, measured against the middle ball: smaller neighbours give a shorter chain. Past 100, with the second sphere
   at 100, the balls run into one another." Second sphere: "The sphere inversions use two spheres, and this is the
   size of the second against the first: with a smaller one the neighbours can be larger than the middle ball before
   the balls run into one another, and their buds are smaller and stand further apart."
E. **The Drawing radius ends the solid in the 3D picture of `GL_BALLS_FREE`** (one line: for every query of the 3D
   picture the distance is at least (distance from the middle - Drawing radius)). Before it the lump's skin lay
   inside the solid, no light reached it and it was black; all of X8 was a black picture (seen). Now the skin is lit.
   The 2D view, a 3D model and the twin are not touched; the two old programs are not touched, so a ball that the
   Drawing radius cuts open in a Version 21 state is still dark there. If this is not wanted, take out the line
   marked "E" at the end of `de`.
F. **Frame it for a second sphere between 1/2 and 1, the spheres apart** (decision 5: "measure; say what you
   found"; `mk/tall29.py`, 13 pairs, 200 rounds). The chain's reach holds in 13 of 13 (the largest |x| inside is
   0.0001 to 0.004 under the formula). The height does NOT: the object reaches up to 0.98 from the middle line where
   Version 21's number says 0.875 (7 of 13 pairs fail, by up to 14 %). I use the hull of the bud on the waist
   instead, k^2 / 2 + k^2 HB / (2 - HB): holds in 13 of 13, 0.4 % to 17 % above the measured height. For rho <= 1/2
   the number is Version 21's, so its views are unchanged.
G. **Warming**: with Balls on balls on show the other two of its programs are prepared in the background,
   `balls3` first.
H. The handle `window.squaringLab` has the names it had; `ballsKind`, `ballsMeet` are not on it (`90-boot.js` is
   not mine to change). `ballsEstimate(..., { parts: true })` returns for the new pairs [best with the two first
   buds behind the mirrors taken in, free].

## Files

- `overlay/js/` the three files; `BUILD.txt`; `changes.diff`.
- `mk/`: `kit29.py` (the recipe, the prototype, the reference), `proto.py`, `make_overlay.py` and `parts/`,
  `run29.py`, `open1.js`, `same29.py`, `frozen29.py`, `voices29.py`, `looks29.py`, `rays29.py`, `air29.py`,
  `steps29.py`, `speed29.py`, `speed29b.py`, `dials29.py`, `tall29.py`, `lump.js`, `lump2.js`, `old29.py`,
  `dbg7.js`, `dbg7b.js` (how the rounding at exactly 1/2 was found), `queue1.sh`, `queue2.sh`.
- `shots/`: `look-<state>-{2d,3d,recipe,sheet}.png` (page 2D, recipe alone, page 3D), `look-*-2d-stray.png`,
  `rays-<state>-<view>.png` and `-marked.png`, `proto-<state>.png`, `crease-Y1-*.png`, `depth-guard-X2-X9.png` (the
  prototype's outline with the guard D at depth 16), `depth-X2-2d-rim.png`. `same/`: the 48 pictures of point 2.
  `old/`: what the old checks wrote.
