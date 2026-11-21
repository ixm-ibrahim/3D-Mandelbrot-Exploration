# Round 27: the balls-on-balls object goes into the lab, and "are we close?"

Binding for everyone in this round. Read all of it before you start.

## 0. The user's words

After seeing three pictures from round 25 and being asked whether the balls-on-balls object should go into the lab
as its own entry, the user wrote (verbatim):

> yes add it - how is it generated? if it's sphere inversions and quaternion arithmetic, then it seems like we're
> pretty close to something here

Their goal, in their own words from the day before (verbatim):

> we're looking for an inflated version of the 2d (so spherical inversions have to be involved somehow) but the
> bulbs occur all over those 3d surfaces naturally, not chosen. and quaterions I imagine have to be involved
> somehow, if not fully, so the resulting object is not stretched or otherwise revealing the limitations of 3d
> rotations

The user is not a mathematician. They judge by pictures and by moving sliders. They have twice said "you're
literally speaking in greek to me". Their five tests for "the right rule": (1) the flat cut z = 0 is exactly the
flat picture of z^2 + c; (2) the number of bulbs follows from the power; (3) no shards, no smear; (4) no rings
(the flat picture merely spun round a line), and it must work for the rabbit, not only for c = -1; (5) a
principled carry-over from 2D, nothing picked by hand.

So this round has two tracks:

- Track A ("entry"): put the object into the lab so the user can turn it and move its dials.
- Track B ("bridge"): take the hunch seriously. Answer with pictures and measurements how close this object is to
  "z^2 + c blown up", from three sides (section 3).

## 1. The object (internal name "pearl tree"; the user must never see that name)

Source: `out/r25/klein/NOTES.md` (read it), code `out/r25/klein/tree.py` and `best.py`, pictures
`out/r25/klein/tree-big.png`, `sheet.png`, `tree-cuts.png`. The judge's summary of the whole of round 25:
`out/r25/judge/ANSWERS.md` (read it; its "may NOT be told" list still holds).

The recipe, in the object's own coordinates m = (mx, my, mz), with one dial t >= 1:

    repeat:
      if mz < 0 or mz > 2t:                        INSIDE (stop)
      slide: (mx, my) -> (mx, my) minus the nearest whole number of the grid
             grid = 'square'  : whole numbers a + b i          (four-fold round the chain)
             grid = 'hex'     : a + b w, w = a sixth of a turn  (six-fold)
             grid = 'line'    : a only                          (buds only round the flat picture)
      if |m| < 1:                 m -> m / |m|^2                 (sphere inversion, unit sphere about (0, 0, 0))
      else if |m - (0,0,2t)| < 1: the same about (0, 0, 2t)
      else:                                        OUTSIDE (stop, for good)

In quaternion words: m -> m - (nearest whole number), then m -> 1 / conj(m). It is the recipe of continued
fractions. One more sphere inversion at the very start (centre (0, 0, 1) in m-coordinates, radius k, k^2 = 1.05)
brings the picture into the lab's frame: picture x = along the chain, picture y = up in the flat plane, picture
z = out of the flat plane; `to_model()` in tree.py is that map. The middle ball is k^2 wide and centred at the
origin, its two big neighbours are k^2 / (2t - 1) wide, t = 1.40 is the default.

Known and checked in round 25 (do not spend time re-deriving; re-measure only what you rely on):

- Every body is an exact ball; bodies touch two at a time; on every ball the smaller balls sit at ALL fractions
  p/q of grid whole numbers, with size falling like 1/|q|^2. 8 rounds of the recipe decide every one of 200000
  random points the same as 80 rounds (at t = 1.40).
- The flat cut (picture z = 0) of the 3D object is exactly the object made with the 'line' grid.
- Against the true flat picture of c = -1: about 39 of every 100 parts of the true area get the wrong verdict at
  the best setting (k^2 = 1.05, t = 1.40). Same layout of bodies; but circles instead of pointed bodies, kissing
  (round against round) instead of pinched (meeting in a point with an opening angle), and buds at the fractions
  (1/2, 1/3, 2/3, 1/4, ...) round each body instead of at the halvings (1/2, 1/4, 3/4, 1/8, ...).
- It has no c and no power. Three balls cannot meet in one point, so it can never be a rabbit.

## 2. Track A: the lab entry

### 2.1 Decisions that are made (do not reopen them)

1. Name the user sees: **Balls on balls**. Label next to it wherever it is listed: "a cousin of the flat picture:
   no c, no power".
2. Home: the kind of picture **Kleinian** (radio `#mode-k`, `S.mode === 'k'`). The lab already has one Kleinian
   group there (Jos Leys's method, `GL_KLEIN` in `30-shaders.js`, state `S.k`, panel `#kleinPanel`). The new object
   is a second group in the same panel: a choice at the top of the panel between the group that is there today
   (first, the default, unchanged in every pixel) and **Balls on balls**. Reason: about eighty places in the code
   already treat `S.mode === 'k'` as "a group picture with no c and no approach". An entry of `APPROACHES` would
   break the contract of that list (scorecard, Learn, twenty-one smoke lists).
3. It must also be reachable **from the Approach list in one click**, as its own clearly labelled row under its own
   small heading (for example "A cousin, not a rule"), because that list is where the user looks for entries. The
   row is NOT an element of `APPROACHES`. Choosing it switches to Kleinian, picks Balls on balls and frames the
   camera. Choosing any real approach afterwards behaves as it does today when one leaves the Kleinian view.
4. It gets its own scene program (its own GLSL constant beside `GL_KLEIN`, with the same interface towards
   `GL_HEAD` / `GL_COLOUR` / `GL_TAIL`), compiled only when it is chosen, with its own cache key.
5. Its dials (plain words, each with a one-sentence help):
   - **Size of the neighbours**: the dial t, shown the way the eye meets it (from "as big as the middle ball",
     t = 1, to small). Default t = 1.40.
   - **Whole numbers**: Square grid (four-fold) | Honeycomb grid (six-fold) | A line only (buds only round the
     flat picture). Default: Square grid.
   - **Depth of the search**: rounds of the recipe. Pick the default so that the default view is exact to the
     pixel; give the dial enough range for zooming in.
   - No dial for k^2 (fixed at 1.05).
6. One note under the choice, at most three short sentences, in the words of section 4. It must say: made only of
   slides by whole numbers and sphere inversions, so every body is an exact ball; it is a cousin of the flat
   picture, its flat cut is a chain of circles; it has no c and no power.
7. Everything that works in the Kleinian view today must either work for Balls on balls or be switched off for it
   with one plain sentence: the 2D view and its cut slider, colours (outside and inside), orbit traps and trap
   solids, picture export, mesh export, the scorecard, camera framing and the "Frame it" button, the examples list,
   the "Start from" list (it belongs to the old group), every reset button, the Learn tab (whatever it does in the
   Kleinian view today, the same). The old group's own warnings (`kleinTrouble`, `kleinReach`, `kleinSwallowed`)
   must not fire for the new group.
8. A JavaScript twin of the inside test, reachable as `window.squaringLab.ballsInside(x, y, z, opts)` (picture
   coordinates; `opts` = { t, grid, rounds }; returns true / false), for the checks.

### 2.2 What must be true (this is what the checkers measure)

- The shader's verdict equals the twin's and equals `out/r25/klein/tree.py` at 20000 random points of the box
  (flat view, three grids, t = 1, 1.4, 2.5), and the 3D picture has no holes, no missing balls down to the size
  the depth allows, and no shell artefacts. The distance the ray marcher is given must never be longer than the
  true distance to the nearest ball (read how `kpearl` does it for the old group and why).
- With the old Kleinian group, and in the Mandelbrot and Julia views, screenshots are pixel-identical with the
  frozen page (`python build.py --name r27-base --base base18a`) for a list of at least twelve states.
- The old smoke lists pass on the new page exactly as on Version 18 (90 of 90; `out/r22/entry/NOTES.md` names the
  lists).
- No console errors, no shader compile warnings that were not there before, first picture of the new group no
  slower than twice the old group's.
- Wide (1400x950) and phone (390x800), dark and light: the new controls fit, nothing overlaps, every word is in
  the house vocabulary.

### 2.3 Where to work: an overlay, never `src/`

Another team (round 26) is building and testing in `src/` right now and builds pages from `src/` as it stands.
**Nobody in round 27 may write anything under `src/`, `base*/`, `squaring-lab.html`, `out/r25/`, `out/r21/` or
`out/r26/`.** The entry is built as an overlay on the frozen copy:

- Changed or new files go to `out/r27/entry/overlay/`, with the same relative path they would have under `src/`
  (for example `out/r27/entry/overlay/js/30-shaders.js`, `out/r27/entry/overlay/body.html`). Start each changed
  file as a copy of the file in `base18a/`. The one exception is `js/90-boot.js`: start from the copy in `src/`
  (it has one more line than `base18a/`), and only ADD lines to it.
- Do not put `js/66-learn-view.js`, `js/65-learn-steps.js`, `js/67-*.js`, `js/68-*.js` or `css/67-*.css` into the
  overlay: round 26 owns them. If the Learn tab needs a change for the new group, write the exact change into
  your notes instead of making it.
- Test page: `python build.py --name r27-entry --base base18a --swap js/30-shaders.js=out/r27/entry/overlay/js/30-shaders.js ...`
  (one `slot=file` pair per overlay file; a new slot name adds a file). Keep the full command in
  `out/r27/entry/BUILD.txt` so that everyone after you builds the same page under their own `--name r27-...`.
- Never run plain `python build.py`. Never publish. Only the orchestrator merges the overlay into `src/` and
  publishes.

How the lab is put together, the test tools (`tools/shot.py`, `window.squaringLab`) and the house rules are in
`docs/ROUND26.md`, section 3. They hold here too, with `r27` in place of `r26`.

## 3. Track B: the bridge. Three questions, each with a picture answer

The hunch: "if it's sphere inversions and quaternion arithmetic, then it seems like we're pretty close to
something here". What the orchestrator believes before the round (to be tested, not assumed):

- The object is made by moves that can each be undone (a slide, a sphere inversion). z^2 + c is a move that sends
  two points to one. Only chains of sphere inversions keep small shapes round in space (Liouville), and z^2 is not
  one, on any piece of the plane.
- What the eye sees of that difference in the flat cut: fractions instead of halvings, and kisses instead of
  pinches. A round ball cannot come to a point, so exact balls and pinched bodies exclude each other from the
  first pair of bodies on.
- So "close" can mean three different things, and each is one explorer's question.

**B1, "measure": how close is it, exactly where is it off, and does it have a dial like c?**
Overlay the true flat pictures on the object's flat cut and measure. Not only c = -1: the bodies of c = -0.75 kiss
(they do not pinch), so the object may sit nearer to that one; try other c on the x-axis too. Show where the buds
sit (fractions against halvings) in a picture a non-mathematician can read. Then the object's own dials: t, the
grid, and the one round 25 did not build, the sideways slide of the glued copy (the 3D form of the "Maskit
slice"; the lab's old Kleinian group has such a dial, `S.k.mx / my / mz`, read `GL_KLEIN`). Is there a family of
these objects with a dial that plays the part of c, and what is the nearest thing in it to a rabbit ("rings of
three round a small gap")? Deliver the truthful "how close" pictures.

**B2, "respace": can the object be carried over so that its flat cut becomes exact, and do the bulbs off the flat
picture survive?**
Build the point-to-point match between the object's flat cut and the true flat picture of c = -1 (body to body,
rim to rim, fractions to halvings), extend it off the flat plane in the two or three most natural ways, carry the
whole 3D object over, render it, and measure how round the bulbs off the flat picture stay. Round 25's klein
section says no match with bounded squeeze exists and built a re-spacing of the paper's rule only (`repair.py`,
"kfix"); nobody has carried the balls object itself over and looked. The question is what the eye sees, and
whether any of it passes the five tests.

**B3, "pinch": can kisses be swapped for pinches while every move stays a sphere inversion?**
A slide is a sphere-inversion move that fixes one point (bodies kiss there). A stretch about a point, with or
without a turn, is a sphere-inversion move too (bodies come to a point there, like in the true flat picture).
Build pictures from chains of such moves fitted to z^2 + c (for example: the moves that have the same fixed
points and the same stretch there as the two undo-moves of z^2 + c; trees of bodies whose meeting points stretch
instead of slide), in 3D, with whatever gives bulbs all over by itself. Such a thing would have a c and could have
a rabbit (three bodies can meet in a point when the move there is a stretch with a third of a turn), at the price
that bodies are no longer exact balls and the flat cut is near, not exact. How near, how round, and does it look
like the user's object? Also say plainly if this is only round 25's "one fitted at every point" pillars again.

Each explorer: work in `out/r27/<name>/`, use the bench library `out/r21/lib/mem.py` (read its docstring; rules
are `M.Rule`, verdicts `M.stay`, flat truth `M.flat_stay`, solids `M.solid` + `M.shade_solid`, cuts
`M.cut_axis`), mark every statement MEASURED / SEEN / REASONED / THEOREM, look at your own pictures before you
write about them, and write `NOTES.md` (never a file called report.md) with "In six plain lines" at the top.
Read `out/r25/klein/NOTES.md`, `out/r25/judge/ANSWERS.md`, `out/r25/wall/NOTES.md` and, where it helps,
`out/r25/vahlen/NOTES.md` and `out/r25/inverse/NOTES.md` first, so that you do not rebuild what is closed.
An honest "no, and here is the picture that shows why" is a full result. A claim of success needs the five tests,
each as yes or no with a number or a picture.

## 4. Words

Use: plane, flat picture, flat cut, rotate / swing, slide, orbit, c, bulbs / buds, body, ball, the power, blown up
/ inflated, dot / point, hop / step, off the flat picture, kiss, pinch, fractions, halvings, whole numbers.
Never in anything the user reads: page, sheet, hinge, door, cone copy, critical, covers, winding, Jacobian,
stretch ratio, latitude, cusp, parabolic, loxodromic, Moebius, lattice, discrete, limit set, group theory terms,
or any internal name (pearl tree, skew pillow, twin_tri, kfix, Maskit, Picard, Gaussian, Eisenstein). "Kleinian"
is allowed: it is already a name in the lab. Captions on pictures: at most two short sentences. No tables of
numbers and no charts in anything meant for the user.

## 5. Done

- Track A: `dist/r27-final.html` builds from `base18a` plus the overlay with the command in
  `out/r27/entry/BUILD.txt`; section 2.2 holds, measured by someone who did not build it; the final notes list
  every overlay file and say in one line each what changed.
- Track B: `out/r27/judge/ANSWERS.md` answers the three questions, with at most three pictures for the user
  (real shapes, from two eyes where it is a solid), a "May be told" and a "May NOT be told" list.
