# Round 27, builder "entry": Balls on balls in the lab (overlay on base18a)

Every number below was measured by a script in `out/r27/entry/mk/` on `dist/r27-entry.html`; the log it comes from is
named. "Seen" means I looked at the picture named. What I did not check is listed in section 8.

## In six plain lines

1. Balls on balls is in the lab as the second group of the Kleinian view, with its own scene program, three dials, a
   note, a Frame it button, a reset, and a row of its own in the open Approach menu. Test page `dist/r27-entry.html`.
2. The inside test of the shader, of the JavaScript twin (`window.squaringLab.ballsInside`) and of `tree.py` agree:
   twin against `tree.py` 0 of 360000 verdicts differ; shader against twin 13 of 362952 differ, all of them at t = 1
   and all at points less than 5e-8 from a ball's skin (single against double precision).
3. The distance given to the ray marcher was never longer than the true distance at 25765 random outside points
   (0 breaks), and at t = 1.4 and 2.5 a ball lies within twice that distance for 99.0% of them. In the 3D picture:
   no hole and no missing ball at 58368 probes; at t = 1.4 and 2.5 every ray stops within 1.2 pixels of a ball.
4. The first Kleinian group and the Mandelbrot and Julia views draw what the frozen page draws: 14 states, 0 pixels
   differ. The first group's controls stand where they stood (measured), under the new choice of group.
5. One thing is switched off for the new group, with one sentence on the page: trap solids (section 5). Everything
   else of decision 7 works or does what it does for the first group.
6. Not as clean as the rest: with the neighbours at 100% (t = 1) the chain never ends, each further ball costs a
   round of the search, and a few rays in a hundred stop short or pass a ball's edge (section 8).

## 1. What the user sees

- Approach menu, opened: under the list of approaches, always in view, the heading "A cousin, not a rule" and the row
  "Balls on balls / a cousin of the flat picture: no c, no power". One click: Kleinian view, Balls on balls, camera
  framed on the whole chain. Seen: `shots/lay-1400x950-dark-menu.png`, `shots/lay-390x800-*-menu.png`.
- Kleinian panel: at the top the choice "Group": "Pearls between two walls" (the group that was there, the default)
  or "Balls on balls" with the same label under it. Two radio buttons, not a drop-down: a drop-down cut the label off.
- Under the choice, for Balls on balls: the note (three sentences), "Size of the neighbours, % of the middle ball"
  (100 = as big as the middle ball = t 1; starts at 55.56 = t 1.40; down to 10; typed down to 2), "Whole numbers"
  (Square grid (four-fold) / Honeycomb grid (six-fold) / A line only (buds only round the flat picture)), "Depth of
  the search" (2 to 40 on the slider, typed to 200; starts at 16), each with a one-sentence help; "Frame it"; "Reset
  this section". One more sentence appears when it applies: "The chain of balls runs out past the Drawing radius in
  the View section, so its far ends are not drawn."
- While Balls on balls is on show the Approach menu stays on the page (its button reads "Balls on balls", the row is
  marked, no approach is ticked); the equation, the modifiers and the approach's own dials are put away as in every
  Kleinian view. Choosing an approach there (a row, or the two step buttons) leaves the Kleinian view the way the Show
  buttons do: start view, and the kind of picture the row was chosen from (Julia when it was reached another way).
- Pictures: `shots/sheet-vs-tree.png` (the page from the front and nearly end-on, square and honeycomb grid, beside
  round 25's `tree-big.png`; the start view; the 2D view). Seen: the same layout as the reference (middle ball, two
  neighbours, end balls, buds all over), four-fold against six-fold end-on.

## 2. Overlay files (`out/r27/entry/overlay/`, eleven) and what changed in each

| file | change |
|---|---|
| `js/32-balls.js` (new) | the whole object: names and texts, `ballsInside` (the twin), `ballsEstimate` (twin of the distance), the start view, `ballsFrame`, `ballsTrouble`, and the scene program `GL_BALLS` |
| `css/86-balls.css` (new) | the row in the open Approach menu, the choice of group, the two parts of the Kleinian panel, what the Approach section hides while Balls on balls is on show |
| `body.html` | Kleinian panel: the choice of group at the top; the first group's pieces wrapped in `#kleinOld` (no change to them); the new part `#ballsPart` |
| `js/00-core.js` | one line: `S.k` gains `group: 0, bt: 1.4, bgrid: 0, bit: 16` |
| `js/25-colour.js` | `colBalls()`; flat-cut rule and step limit for the new group; the first group's three notes kept to the first group; trap solids off for the new group (one sentence) |
| `js/40-render.js` | `sceneKlein()`; the program and cache key `balls`; `uIter`, `uBT`, `uBGrid` for it; snapshots take the right program |
| `js/46-mesh.js` | the sentence that describes a saved model, for the new group |
| `js/50-camera.js` | start view of the new group (`camHome`), no list camera and no trap stand-back for it |
| `js/75-presets.js` | `kleinTrouble` and `kleinSwallowed` silent for the new group; the three Kleinian examples belong to the first group (choosing one goes there) |
| `js/80-ui.js` | the choice, the dials, the note, the row, `uiBallsShow`, `uiBallsLeave`, `uiBallsMenu`, the Approach menu while Balls on balls is on show, both resets |
| `js/90-boot.js` | from `src/` (lines added only): `ballsInside`, `ballsEstimate`, `ballsReach`, `ballsFrame`, `ballsShow`, `ballsOn`, `BALLS` on `window.squaringLab` |

`changes.diff` is the full difference (481 lines: 148 added, 34 changed or removed in the nine files that existed).
`js/30-shaders.js` is NOT in the overlay: `GL_BALLS` declares its two uniforms itself, so `GL_HEAD`, `GL_KLEIN`,
`GL_TAIL` and every other program's source are untouched. At the time of writing `src/` equals `base18a/` for all
nine changed files (checked with cmp), so the overlay can be laid over `src/` as it is.
`mk/patch_ui.py`, `patch_ui2.py`, `patch_ui3.py`, `patch4.py`, `patch5.py` are the scripts that made most of the edits;
they are history, `changes.diff` is the record.

## 3. How it is generated, and the scene program

The recipe is section 1 of ROUND27.md, to the letter (slide to the nearest whole number of the grid; sphere inversion
in the unit sphere about (0, 0, 0) or (0, 0, 2t); outside both: OUTSIDE for good; beyond a wall: INSIDE; undecided
when the rounds run out: INSIDE, as `tree.py` counts it). The frame inversion is `to_model()`.

`GL_BALLS` (in `32-balls.js`; interface as `GL_KLEIN`: `de()` sets gEsc, gIt, gLast, gGrad, gOnTrap, calls trapStart
once and trapAdd once a round, honours gLand; `ORBIT_SCENE = false`; built with `glNeeds(needs, true)`):

- The scale factor DF is carried through the frame inversion and every sphere inversion, and so is W, the image of
  the picture's far distance. With them `kpearl` gives the TRUE distance to each ball the search meets (both walls,
  every round), exactly as for the first group.
- That alone is not "never longer than the true distance": the nearest ball is often a bud the recipe never visits
  from that point. So when the recipe ends OUTSIDE, a second number is made there, `free`: at that place every ball
  other than the two walls lies inside the ball of diameter H = t - sqrt(t^2 - 1) standing on each wall at the
  nearest whole number, or within H/2 of a wall (H/3 honeycomb; a tube of radius H/4 for the line grid). The distance
  e to all of that is certain room, and carried back through the maps it leaves a ball of radius
  e L / ((L + e) DF) round the picture point (L = |m - W|; exact for sphere inversions). The estimate is
  min(nearest ball met, free). Reasons for the two heights are in the comment above `GL_BALLS`.
- One exception, said plainly: in the 3D picture (not in the 2D view, not for a 3D model, not in `ballsEstimate`)
  `free` is not taken below two ray thresholds. It measures to hulls, so close in it would stop every ray a few pixels
  early and roughen the slope; there a ray goes on about a pixel a step and is stopped by the exact distances or by
  landing inside a ball (the inside test is exact). Measured effect: section 6, D.
- Loops: one `for (i < uIter)` as in `kde`; the honeycomb slide is three candidates, no inner search. One call site
  each for `trapAdd`, `trapDist`, `bnear`; two for `kpearl` (as in `GL_KLEIN`).
- What the trap sees: the point after each slide, as (m.z - t, m.x, m.y): x along the chain, z out of the flat plane,
  so the flat cut is the trap's z = 0 and the same pattern lies on every ball. A hit's colour is read as for the
  first group (the search stops at the round that lands on the ball, and that wall point is fed).
- gIt is the number of rounds (8 higher in the 3D view, as `kde` reports it).

Depth: at the start view (t = 1.4, flat view, 151281 pixel centres) 8 rounds give every pixel the verdict of 80
rounds, for all three grids; 6 rounds leave 28 pixels (`logs/holes-run1.json`, part E). The dial starts at 16, to
leave room for zooming in; the search stops by itself when a point is decided, so the spare rounds cost nothing.

## 4. Decisions, and where I read them one way

- 1, 2, 4, 5, 6, 8: as written. Dial t is shown as the neighbours' width in % of the middle ball; the typed box
  shows 55.56 and the slider's own step shows it as 55.6; both give t = 1.40 exactly (the setter snaps within 0.06).
- 3: the row stands in the open menu directly under the list of approaches, not inside `#rules`. Reason: smoke step 8
  reads every heading and row of `#rules` and expects the approaches only (first run: it failed there). The row is a
  button; `APPROACHES` still has 21 entries.
- 3, "choosing any real approach afterwards behaves as it does today when one leaves the Kleinian view": I kept the
  Approach menu on the page while Balls on balls is on show (otherwise there is nothing to choose from), and choosing
  an approach does what the Show buttons do (mode, `resetCam()`, `syncControls()`, `refresh()`), going to the kind of
  picture the row was chosen from. With the FIRST group on show nothing changed: the section is hidden, and an
  approach chosen from a script stays in the Kleinian view (checked).
- 7, trap solids: switched off for the new group (section 5).

## 5. Every place that asks for the Kleinian view, and what it does for Balls on balls

Works for the new group:
- `40-render.js` sceneWant / sceneNow / takeSnapshot: own program, key `balls` (`balls|i`, `balls|r`, ...), built only
  when the group is chosen (`sceneWarm` still prepares the first group's program only). sceneUniforms: `uIter` = the
  new depth; `uStepK` at most 0.5 and no exact slope, as for the first group (the Quality help text that says so stays
  true); the first group's five uniforms are set and not read.
- `25-colour.js`: colours outside and inside, all trap shapes and "colours by" (drawn, section 6 F); `colOrbitsFlat`
  true at slice height 0; `uColIter` = the new depth; "Orbit steps the trap reads" hidden as for the first group; the
  note "The Kleinian search has no orbit that settles..." shows for both groups (true for both).
- `50-camera.js`: start view, Reset view, Frame it (section 6 F). No list camera, no look-at-the-picture step (that
  is for trap solids).
- `45-export.js`: a saved picture is named `squaring-lab-kleinian-W x H.png` for both groups; `46-mesh.js`: a model
  is made and its description names Balls on balls, t, the grid and the depth.
- `80-ui.js`: refresh, uiKleinMark, uiViewSync, Reset everything (back to the first group, the three dials back),
  the panel's own reset, the Show buttons (the Kleinian button brings back whichever group was chosen last).
- 2D view and its height dial; the cut plane and a painted cut face; the scorecard (it has no Kleinian place: it
  shows the chosen approach's card, as today); the Learn tab (it does what it does with the first group behind it:
  the Approach menu is the approach's there; `66-learn-view.js` untouched and no change needed).

Belongs to the first group, and says nothing for the new one:
- `75-presets.js`: the "Start from" list, its Frame it, `kleinFits`, `applyKleinPreset`, `kleinPresetAt`
  (put away with the first group's part of the panel); `kleinTrouble`, `kleinSwallowed` (return '' / false);
  `kleinReach` (a number of the first group, unchanged, not used for the new one); the three Kleinian EXAMPLES
  (none is marked while Balls on balls is on show; choosing one goes to the first group).
- `25-colour.js`: `colKleinHigh`, `colKleinCuts`, the thin-trap note and the mirror note are the first group's.

Switched off for the new group, with one sentence:
- Trap solids ("In the 3D view the trap: Is the solid / Is added to the solid"). The page then says "Balls on balls
  has no trap solid: in this view the trap only colours the balls." and draws the plain balls; the thickness and
  skipped-steps dials are put away. Why: I built it and looked (`shots/trap-*.png`, `logs/traps.log`, on an earlier
  build). The trap is met inside one cell of the grid, one unit across, so the lab's usual trap (radius 1) comes out as
  blocks cut along the cell's flat faces (seen: `trap-shell-r1-skip1-added.png`); a trap near the point that stands
  for the far distance grows past the camera (seen: `trap-shell-r05-skip1-added.png`); and "is the solid" drew
  nothing at all until a cap was added. The shader code is still in `GL_BALLS` under `#if TRAP_SOLIDS`, with a
  comment; the page never builds it.

## 6. My own checks (section 2.2), on the final build unless a line says otherwise

A. Twin against `tree.py` (`mk/twin_check.py`, `logs/twin-check.txt`): 20000 random points of the box, each of 9
   settings (three grids; t = 1, 1.4, 2.5) once in the flat cut and once in space, 40 rounds: 0 of 360000 differ.
B. Shader against twin (`mk/verdict.js`, `logs/verdict.json`): the program the picture is drawn with, read through
   `sampleSlice`, 142 x 142 points of the square -1.8..1.8, the same 9 settings, flat cut and one random height each:
   t = 1.4 and t = 2.5: 0 of 241968 differ. t = 1: 13 of 120984 differ (1, 1, 4, 0, 7, 0), the twin's distance at
   every one of them under 5e-8. Shader's distance against the twin's where both are outside: mean relative
   difference 1e-7 to 1e-5, largest 0.3%, never more than 0.1% longer.
C. Never longer than the true distance (`verdict.js` part C, in double precision): 25765 random outside points, 240
   directions each: no point of the sphere of radius 0.999 d is inside a ball (0 breaks). Tightness: a ball within
   1.5 d for 82.3% and within 2 d for 99.0% of the 17577 points at t = 1.4 and 2.5 (for 138 of them, 0.8%, none of the
   240 directions found a ball within 10 d; I did not look further into those); at t = 1 it is looser (of 8188 points:
   within 3 d for 59%, within 5 d for 89%).
D. The 3D picture (`mk/holes.js`, `logs/holes.json`): 19 views (5 settings; start view, front, end-on, two close
   views), 3072 probes each: the page's ray against a slow march that uses the twin's distance with 80 rounds.
   Hit by the slow march and missed by the page: 0 of 58368. At t = 1.4 and 2.5 (16 views) every page hit stands
   within 1.2 pixels of a ball its search met (no shell in thin air), and none lies behind the slow march's hit.
   Between 6% and 19% of the hits (by view) stop more than 4 pixels in FRONT of the slow march's hit: those rays pass
   within a pixel of a bud's edge, which the picture draws and a ray of no width misses (the ball is there: see the
   1.2 pixels; my reading of the rest, not measured further). Page hit where the slow march misses: 5 to 20 probes a
   view, the same edges. At t = 1: section 8.
E. Unchanged pictures (`mk/same.py`, `logs/same.txt`): 14 states (7 of the first Kleinian group incl. 2D view,
   inside colours, a list entry, own values, two trap-solid examples, the cut; 3 Mandelbrot; 4 Julia), the picture
   alone, new page against `python build.py --name r27-entry-base --base base18a`: 0 pixels differ in all 14.
   (With the zoom slider left on the picture 14 pixels of its handle differ in two states, and they differ the same
   way between two runs of the frozen page itself: `logs/same-frozen-against-itself.txt`.)
   First group's panel (`logs/oldpanel.txt`): its 14 controls stand at the same places relative to its first note.
F. Controls (`mk/ui.js`, `logs/ui.json`, 47 lines of results, no console errors): the list and the row; one click;
   defaults; the three dials (each changes the picture, the start values bring the first picture back); Frame it and
   Reset view; the panel's reset; the 2D view and the height dial; 7 colourings, 8 trap shapes, 6 "colours by", the
   cut with a painted face, 5 inside colourings; the trap-solid sentence; the Examples; picture export (a 1.0 MB PNG
   reached the save hook); a 3D model of 48 cells ("The model is ready."); Learn; choosing an approach afterwards
   (rows and step buttons, from Mandelbrot and from Julia); the first group unaffected; Reset everything.
G. Wide and phone, dark and light (`mk/layout.py`, `logs/layout.txt`, pictures `shots/lay-*.png`): at 1400 x 950 and
   390 x 800, both themes: the 7 new pieces lie inside the window, none overlaps another, no text is cut off, the
   page is not wider than the window, the open menu fits the window with the row whole and marked. Seen: the phone
   panel in light, the wide menu in dark.
H. Speed (`layout.py speed`; `logs/speed-a.txt`, `logs/speed-b.txt`; a fresh page for every number): from the click
   to the finished picture (12 passes at 862 x 701, the program built on the way), in ms.
   First group: 860, 863, 950, 929, 1045, 899. Balls on balls by the Kleinian button: 917, 810, 923, 885, 973, 1072.
   Balls on balls by its row: 841, 1796, 777, 977, 968, 805. So the same as the first group's, with one sample of
   twelve at twice the time (1796; I do not know why: other work runs on this machine, and I did not measure it).
   An earlier set, on a busier machine and the build before the last: 1459, 2193, 2053 / 1446, 1812, 1516 / 1749,
   1626, 1380. The line "first full-size pass on screen after ... ms" in those logs is NOT a measurement of the
   first pass (it sees the Mandelbrot picture that was up before); only the finished times count, and I have no
   separate number for the first pass.
I. Console: no console errors or warnings in any run above (`tools/shot.py` prints them; a shader that fails to
   build is reported there as an error, and none was).
J. The old smoke lists: see the last section of this file (SMOKE).

## 7. Tools in `mk/`

`bld.py` (the build command of BUILD.txt), `run.py` (runner; logs go to `logs/`), `twin.js` + `twin_check.py`,
`verdict.js`, `holes.js`, `ui.js`, `same.py`, `layout.py`, `oldpanel.py`, `sheet.py`, `traps.py`, `first.py`,
`smoke27.py` (round 22's 90 steps on a page of this round; pictures to `smoke/`). Run one at a time.

## 8. Known gaps, and what I did not check

- t = 1 (neighbours at 100%): the chain is endless and every further ball needs one more round, so with 16 rounds
  the far balls, and thin slivers at each kiss, count as inside (flat start view: 642 of 151281 pixels differ from 80
  rounds; 348 at 20 rounds). In the 3D picture there, 7 to 25 of about 570 hits per view stop 2 to 18 pixels from the
  nearest ball, and in the end-on view 19 hits lie behind the slow march's (a ray passing a ball's thin edge). The
  distance is also looser there (C). Not repaired.
- The exception in the 3D picture (section 3): within two ray thresholds the estimate is not the certain one. A ray
  that runs out of steps there is drawn as a hit a few pixels early. Not seen at t = 1.4 and 2.5 in D; not measured
  with fewer ray steps than the Balanced quality, nor in the Fine, Fast and Ultra fast presets.
- Trap solids: off (section 5).
- The mirror symmetry of trap colours inside the discs of the 2D view was not checked for the new group (the first
  group's note about it is not shown for the new one).
- Colour pictures were checked by "it draws and no program fails" plus the start-view pictures I looked at; I did
  not look at each of the 26 colour settings.
- Hovering the row shows no explanation box (the approaches have one); the row carries its label and a tooltip.
- Fly camera, pinch and touch input, extreme ranges, a lost graphics context, and saving on the published host were
  not tried with the new group.
- The speed check has no first-pass number, and one of its twelve samples for the new group took twice the first
  group's time (H).
- Programs: by reading the code, the new program is built only when the group is on show (`sceneWarm` prepares the
  first group's only); by measurement only this much: a fresh page that goes to either group has built 3 programs
  (the display one, the Mandelbrot one, and that group's), never 4.
- I did not run anything against `src/` or with round 26's Learn files in the page.

## 9. Learn

No change to `66-learn-view.js`, `65-learn-steps.js` or round 26's files is needed. Under Learn with Balls on balls
as the picture left behind, the Approach menu shows the approach (name, tick, dials), choosing one stays in Learn,
the Kleinian button brings Balls on balls back, and the row chosen under Learn leaves Learn (all in `logs/ui.json`).
`80-ui.js` watches the class of `<body>` (Learn sets `is-learn`) to repaint the menu; nothing else touches Learn.

## SMOKE

SMOKE-FINAL (`logs/smoke-all.log`, `mk/smoke27.py`, on the final build of `dist/r27-entry.html`, 1400 x 950): round
22's list, unchanged except for the page and the folder its pictures go to (62 steps of `tools/smoke-v14.json`, round
20's 5 with round 22's one changed line, round 22's 20 + 3): **90 steps ran, 90 results, exit 0, "no console errors"**,
in one run. Pictures in `smoke/`.

Two earlier runs, for the record:
- first run, an earlier build: stopped at step 8 ("the list of the Approach menu should read ..."), because the row of
  Balls on balls then stood inside `#rules`. That is why the row now stands under the list (section 4).
- second run (`logs/smoke-all.run2-timeout-at-82.log`): 81 steps passed, then `tools/shot.py` gave up on step 82 after
  its 120 seconds (thirteen pictures of "Pulled plane" in one step; the machine was busy). The last fourteen steps
  alone on a fresh page passed (`logs/smoke-tail.log`), and the third run, above, passed whole.

## Order of the runs on the final build

build (02:41) -> ui.js (pass) -> smoke (90 of 90) -> twin_check, verdict.js, holes.js -> same.py, layout.py,
oldpanel.py -> speed twice. `first.py`, `traps.py`, `sheet.py` and part E of the depth count ran on earlier builds of
the same shader path (the pictures in `shots/first-*`, `trap-*`, `sheet-*` are from those).
