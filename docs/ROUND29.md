# Round 29, Track A ("free"): the two dials of Balls on balls are free of each other

Binding for everyone on this track. Read all of it before you start. (Track B, the Learn tab, has its own brief:
`docs/ROUND29-LEARN.md`. Other agents work on it at the same time, in `out/r29/learn/`. Leave their folder alone.)

## 0. The user's words

Version 21 let "Size of the neighbours" go past 100, and to keep the two spheres of the recipe from cutting into
each other it shrank the second sphere by itself. The user wrote (verbatim):

> i didn't mind the intersection or collision of the balls after 100%, please remove whatever automatic rule you
> have. publish it

So: no automatic rule at all. Each dial sets its own number and nothing else. Whatever the plain recipe then gives
is what the lab draws, also where the two spheres cut into each other.

The user is not a mathematician. They judge by pictures and by moving sliders. Earlier words that still hold:
"keep it in all cases", "the parameters should be able to go past their current limits".

House rules, how the lab is put together and the test tools: `docs/ROUND26.md` section 3, `docs/ROUND27.md` sections
2.3 and 4 (words), `docs/ROUND28.md` (all of section 1: this round continues it). They hold here with `r29` in place
of the round number, and with `base21a/` as the frozen copy (Version 21, the published page; `src/` is identical to
it today). Round 28's own files are the best starting point: `out/r28/dials/NOTES.md`, `out/r28/dials/mk/`,
`out/r28/truth/`, `out/r28/eyes/`, `out/r28/ui/`, `out/r28/fix/`, `out/r28/final/` (each has a `NOTES.md` and its
scripts in `mk/`; the real-mouse helper is `out/r28/final/ui/mk/hand.py`).

Extra rules this round:

- **No git.** The orchestrator is making a repository of this folder while you work. Run no `git` command, and do
  not create, edit or delete `.git`, `.gitignore` or `README.md`.
- Never edit `src/`, any `base*/`, `squaring-lab.html` or `dist/preview.html`. Never run plain `python build.py`.
  Never publish anything. Only the orchestrator merges and publishes.
- Write your report as `NOTES.md` in your own folder (a file named `report.md` cannot be written).
- Python files that contain backslashes: write them with the Write tool, not a shell heredoc.
- Browser scripts one at a time within your own work; other agents' browsers may run beside yours, so allow long
  timeouts.

## 1. What the plain recipe gives (the orchestrator looked first: `out/r29/me/plain.py`, `plain-all.png`)

The recipe, unchanged, in the object's own coordinates m, top = 2t, rho the second sphere's radius:

    repeat:
      if mz < 0 or mz > top:              INSIDE
      slide (mx, my) by the nearest whole number of the grid
      if |m| < 1:                         m -> m / |m|^2
      else if |m - (0,0,top)| < rho:      m -> (0,0,top) + rho^2 (m - (0,0,top)) / |m - (0,0,top)|^2
      else:                               OUTSIDE
    undecided when the rounds run out:    INSIDE

Size shown p = 100 / (top - 1). The two spheres touch at top = 1 + rho (p = 100 / rho) and cut into each other
below that (p rho > 100). Flat cuts by the recipe alone (numpy), 520 points wide:

- Both spheres equal (rho = 1): at 100 the endless chain; at 120 a dense field of balls with round holes (83 % of
  the cut is inside, and the far distance is inside too); from about 137 on the square grid the flat cut is filled
  completely (in the plane my = 0 the two spheres cover the whole cell when top < sqrt 3). Off the flat plane there
  is still room near the corners of the cell until top < sqrt 2 (p > 241), then everything is inside. The line grid
  at 150: flat cut filled, the cut across the chain shows three clean balls.
- Second sphere 75, size 80 (the two spheres apart, the copies of the second sphere cut into each other): a clean
  chain of balls with buds. This part of the dial was closed in Version 21 and looks good.
- Second sphere 75, size 150 and second sphere 50, size 300 (cutting): a band of balls with round holes.

So where the spheres cut into each other the inside is a union of whole balls that overlap, the outside is what is
left: round holes, in 3D tunnels round the circles where two spheres cross. Often the far distance is inside, and
then the 3D view is one lump as large as the Drawing radius with holes in it. That is what the user asked to see.

## 2. Decisions that are made (do not reopen them)

1. **State.** `S.k.bt` = t as the size dial gives it: t = (100 / p + 1) / 2, p from 1 to 2000 (so t from 0.525 to
   50.5), with the one old exception that a p within 0.06 of 55.56 is t = 1.4 exactly. `S.k.brho` = rho, any number
   from 0.02 to 1. Nothing clamps one by the other. `ballsRho(r)` is `clamp(r, 0.02, 1)` (1 for a state that holds
   nothing), `ballsT(t)` is t as it stands (kept above 0.5 by a hair so that top - 1 > 0).
2. **The dials.** "Size of the neighbours, % of the middle ball": slider 2 to 400, typed 1 to 2000, as in
   Version 21; it sets t and nothing else. "Second sphere, % of the first": slider 2 to 100 in steps of 1, typed 2
   to 100 with two decimals, no jump over 50 to 100 any more; it sets rho and nothing else. "Depth of the search":
   unchanged. "Reset this section": 55.56 / 100 / 16. Remove `BALLS_DIAL.follows`, `ballsRhoFrom`'s jump, the
   give-way in `ballsSetShare` and `ballsSetRho`, the arrow-key special case and the typed-follow lines in
   `80-ui.js`, and every comment that describes them.
3. **Three programs, two of them untouched.**
   - `GL_BALLS` (key `balls`): rho = 1 and t >= 1. Not one character of its text changes.
   - `GL_BALLS_RHO` (key `balls2`): rho <= 1/2 and top >= 1 + rho (apart or touching; test with a tolerance of
     1e-9). Not one character of its text changes.
   - A new program `GL_BALLS_FREE` (key `balls3`, program name `k-balls3`, uniforms `uBT`, `uBRho`, `uBGrid`) for
     every other state: the two spheres cut into each other, or rho is between 1/2 and 1.
   Every state Version 21 could reach lies in the first two, so every picture Version 21 could make stays the same
   to the pixel. That is checked (section 4).
4. **Sentences** (`ballsTrouble`, shown in `#ballsWarn`). Plain words; the texts are fixed here:
   - Gone: "Past 100 the second sphere has to be smaller than the first ..." and "It follows the size until you set
     it yourself."
   - Kept as they are: the sentences for touching ("At 100 the chain never ends ...", "At {p} the chain never ends
     ..."), "Here the chain is too long for one picture ...", the two Drawing radius sentences, the two sentences
     for few rounds, "With the second sphere at 50 the buds on a neighbour kiss ..." (only at exactly 50, only where
     the two spheres do not cut into each other), and for any rho below 1: "The second sphere is now X % of the
     first. Reset this section puts it back to 100."
   - New, when the two spheres cut into each other (p rho > 100 as the two dials show them, beyond rounding):
     "Here the two spheres of the recipe cut into each other, so the balls run into one another. A smaller size or
     a smaller second sphere parts them again."
     and, appended when the far distance is inside (test the recipe at a few far points) and the 3D view is on:
     "Far out everything is filled, so the picture is one lump as large as the Drawing radius."
     and, appended when the flat cut is filled completely and the 2D view is on (test the recipe on a coarse
     grid of the 2D view): "The flat picture is filled completely."
   When the spheres cut, the chain sentences (never ends, too long, runs out past the Drawing radius) are not
   shown: the new sentence takes their place.
5. **Frame it and the start view.** Where the spheres cut there is no end of the chain to frame: frame the middle
   ball, its two neighbours and a stretch beyond, as for the endless chain (`ballsReach` = Infinity there). For rho
   between 1/2 and 1 with the spheres apart, frame the whole chain as for a smaller second sphere, if the numbers
   of that branch still hold there (measure; say what you found).
6. **The twins.** `ballsInside` reads t from the page as it stands (no clamp). `ballsEstimate` gets the new
   program's distance as a third branch, written the way the shader writes it, so that the checks can compare.
7. **The 3D model** (`46-mesh.js`) must take any state: find what it uses of the balls and give the new states the
   new distance or the plain inside test, whichever that code needs.
8. Nothing else changes: no preset, no link key, no other entry, no CSS unless a dial needs it, no `90-boot.js`.

## 3. The new program's distance (the hard part)

Read the long comments above `GL_BALLS` and `GL_BALLS_RHO` in `base21a/js/32-balls.js` first. The estimate is the
smaller of two numbers: `best`, the true distance to the balls the recipe's own chain meets (unchanged, exact), and
`free`, a length round the point that is certainly free of every other ball, worked out at the place where the
recipe ends OUTSIDE. Version 21's `free` rests on hull balls and spindles that are proved only where the spheres
do not cut and rho <= 1/2 (or rho = 1). The new program needs a `free` that holds for any t and rho.

What must be true of it is in section 4. How you get there is yours to choose. The orchestrator's reasoning, as a
toolbox: test each piece with numbers before you rely on it (in round 28 one line of the orchestrator's brief was
wrong and the builder caught it).

- **T1, the spheres themselves.** At the end frame (m in the middle cell, between the walls, outside both spheres)
  everything inside lies beyond a wall or within one of the spheres (first or second, at any whole number). So
  min(|m| - 1, |m - (0,0,top)| - rho), also taken for the neighbouring whole numbers, is a room. It is zero on every
  sphere surface, where usually no ball is near: alone it makes the 2D view draw lines along those surfaces and the
  3D view creep.
- **T2, looking through a sphere.** The recipe's verdict is the same on both sides of a sphere surface: a point just
  inside is carried to its mirror image just outside and goes on from there. So what lies inside sphere S is the
  mirror image of what lies outside it. Apply S's inversion to the point although it is outside ("a round that
  does not count"), with DF and W carried along as in a real round. In that frame the point is inside S and the
  content is outside S: the two walls (kpearl gives the true distance; one of them is the first bud behind the
  mirror), the other kind of sphere (distance to it, or to S's own surface from inside when the point is in both),
  and the copies of S at other whole numbers (they lie beyond the edge of the cell). Carry the room back with
  e L / ((L + e) DF). Do it for the first and the second sphere, and for the neighbouring whole numbers (shift the
  point first). What is left is zero only near the circles where two spheres cross.
- **T3, rings.** The spindle and the side spindle of Version 21 are the case of two fixed points. When the two
  spheres concerned cut into each other the two fixed points become the circle where they cross (d2 < 0, c2 < 0 in
  the same formulas), and the surfaces that both inversions carry onto themselves are rings round that circle. The
  same room formula R - |distance from the centre of the arc| holds, with the sign left in, as long as the ring
  stays inside the middle cell and clear of the walls and of every other sphere. There are three such circles:
  first sphere and second sphere (when they cut), second sphere and its copy at the next whole number (rho > 1/2),
  first sphere and its copy at the next whole number (always: the side spindle with rho = 1, on the bottom wall).
- **T4, hulls where they still hold.** While the two spheres are apart the two fixed points on the middle line are
  real, so HB and HT exist as in Version 21. "The rest" on the top wall was proved for rho <= 1/2 only.
- **T5.** In the 3D view the page never takes `free` below about two ray thresholds (the hold, last lines of `de`),
  so a small room costs steps but draws nothing wrong. In the 2D view nothing is held: the outline is drawn where
  the distance is under a pixel, so the 2D view shows every place where `free` is wrongly small as a line or a dot.

The estimate may be the largest of several rooms that each hold. Keep the program's interface exactly as the other
two have it (gEsc, gIt, gLast, gGrad, gOnTrap, trapStart, trapAdd, the landing length, the hold, the TRAP_SOLIDS
lines).

The reference to measure against, in every case: the recipe alone on a fine grid (numpy), and from it the true
distance to the nearest inside point (a distance transform of the grid, in a flat cut and in a small box in
space). No list of balls is needed.

## 4. What must be true (the checkers measure this)

Panel of new states (size, second sphere, grid; depth 16 unless said):
X1 (120, 100, square), X2 (130, 100, square), X3 (150, 100, line), X4 (150, 100, honeycomb), X5 (200, 100, line),
X6 (150, 75, square), X7 (300, 50, square), X8 (400, 100, square; everything inside), X9 (105, 100, square, depth 16
and 60), Y1 (80, 75, square), Y2 (60, 60, honeycomb), Y3 (100, 90, square), Y4 (55.56, 99, square),
Y5 (133.33, 75, square; touching), Y6 (120, 51, line), Y7 (30, 75, square).
Panel of old states (Version 21 could reach them): (55.56, 100), (100, 100), (20, 100), (150, 33.33), (300, 16.67),
(200, 50), (400, 12.5, honeycomb), (1000, 5), (60, 40, honeycomb), (80, 50, line), each also in the 2D view.

1. **Verdicts.** Shader (`sampleSlice`), twin (`ballsInside`) and a recipe you write yourself agree at every point,
   on both panels (round 28's bar: 0 points differ; a handful on a sphere surface from single precision is to be
   reported, not hidden).
2. **Old pictures unchanged.** On the old panel the page built from the overlay and the page built from `base21a`
   alone give the same picture to the pixel, 2D and 3D, and use the same program text (`same.py` of round 28 does
   this for Version 20 against 21).
3. **The distance is safe.** On the new panel, for outside points on a flat cut and in space, the estimate is not
   longer than the true distance (allow 2 % and the grid's own step) in at least 99.9 % of them, and never more
   than one and a half times it.
4. **The distance is not wrongly small.** In the 2D view of every new state, every outline pixel lies within two
   pixels of a place where the recipe changes its verdict: no lines along sphere surfaces, no dots at the circles
   where spheres cross. Report the count of stray pixels per state. (Y1 to Y7 matter most: they look like proper
   objects and the user will look closely.)
5. **The 3D view.** No holes, no noise, no banding that Version 21 does not have at a like state: compare each new
   state with a reference made from the recipe alone (rays in small fixed steps with the plain inside test, in
   numpy or in the page) at two views, and look at the pictures yourself. Report where they differ by more than a
   pixel at an edge.
6. **Speed.** Frame time of the new program at Y1 and X1 against Version 21's `balls2` at (150, 33.33): report the
   numbers. More than three times slower is a major defect.
7. **The dials** (real mouse and keys, wide window and phone, light theme first): dragging or typing the size
   never changes the second sphere's number, and the other way round; every value from 2 to 100 can be reached on
   the second sphere (slider, arrow keys, typing 62.5); typed limits hold (size 1 to 2000, depth 1 to 1000);
   Reset this section gives 55.56 / 100 / 16; the sentences are the ones in section 2 and fit the state; Frame it
   shows the middle ball and both neighbours in every state of both panels; no console error or warning; the 3D
   model can be made at Y1 and at X1.
8. Round 27's and round 28's own checks still pass on the new page (`out/r27/final/mk/verd.py`, `shape.py` with
   `R27_PAGE`, `R27_BASE`, `R27_OUT`; round 28's `same.py`).

A defect is **major** when a picture is wrong in a way the user would see without looking for it, when a dial moves
another dial, when an old picture changed, or when anything throws. Everything else is minor.

## 5. Where to work

An overlay on `base21a`, never `src/`:

    out/r29/free/overlay/js/<the files you changed>
    out/r29/free/BUILD.txt       the one build line, as out/r28/dials/BUILD.txt has it:
    PYTHONIOENCODING=utf-8 python -W ignore build.py --name r29-free --base base21a --swap js/32-balls.js=out/r29/free/overlay/js/32-balls.js ...
    out/r29/free/NOTES.md        what you built, what you measured, what is not right, what you decided and why
    out/r29/free/mk/             your scripts;  out/r29/free/shots/  your pictures

Do not touch the Learn files (`js/65-learn-steps.js`, `66-learn-view.js`, `67-learn-shape.js`,
`68-learn-shape3d.js`, `css/65-learn.css`, `css/67-learn-shape.css`) or `body.html`: Track B is changing them.
Checkers work in `out/r29/truth/`, `out/r29/eyes/`, `out/r29/ui/`, the fixer in `out/r29/fix/` (its overlay is the
builder's overlay with its changes, in `out/r29/fix/overlay/`), the last checker in `out/r29/final/`. Each builds
its own page under its own name (`--name r29-truth`, ...), so that no two agents write the same file in `dist/`.
