# Round 9: the last open faults, and a second check

## Where things stand

- **Version 8 is published**, frozen as `base8/` (source; `src/` is identical to it at the start of this round)
  and `dist/v8.html` (page). `dist/v6.html` is the build the first check ran on; `dist/v5.html` the one before.
- Since the first check (`notes/_t6_reports.json`, 36 defects in `notes/_t6_defects.json`):
  - the colour cure of round 6 (`notes/r6-colour.md`): the trap colour of a 3D surface is read from the surface
    with a fixed number of orbit steps (dial "Orbit steps the trap reads", starts at 4);
  - fix pass, first part (`docs/FIX7.md`, `notes/_fix7_reports.json`, `notes/r7-export.md`, `r7-mesh.md`,
    `r7-camera.md`, `r7-dial.md`, `r7-page.md`);
  - fix pass, second part (`notes/_fix7_engine_report.json`, `notes/r7-engine.md`).
- `tools/smoke.json` (52 steps, generator `out/r4/page/make_smoke.py`) passes on `dist/v8.html`
  (`out/me/smoke-v8b.log`).
- Measured by the orchestrator on Version 8: model against picture with the mesh tester's scripts
  (`out/me/meshcheck8/check.log`): median hue difference 3.3 degrees (Mandelbrot), 2.8 (rabbit), 7.3 (Julia
  c = -1; 4.7 at 256 cells), 7.1 (cut), 3.5 (Kleinian), 7.5 (trap solid); outline overlap 0.945 to 0.972. Speed on
  a quiet GPU (`python out/me/perf.py base4 v6 v7 v8a`, three rounds, least values): compile M 1.75 s against 1.53,
  K 0.66 against 0.56; draw M 378 ms against 606, J 578 against 858, K 97 against 99. Draw readings of one page
  vary by a factor of two between visits, so only least values of several visits mean anything.

## Status of the 36 defects of the first check

Reported fixed by their engineers (to be confirmed by the second check): solids-1, solids-2, solids-3 (note),
solids-6 (note), solids-7 (not for the Kleinian start view), flat-2, flat-3, flat-5, mesh-1, mesh-3, mesh-4,
mesh-5, mesh-6, walk-1, walk-2, export-1 (the number never rises; the first number is rough), export-2, export-3,
layout-1, layout-2, layout-3, layout-4, layout-5, controls-1, words-1, words-2, words-3, kleinian-2.

Accepted as they are: flat-1 (the Kleinian 2D outline changed because the pearl distance is exact now), flat-4
(soft outline deep in a spiral: measured not to be the iteration limit; the dial's help says what it is).

Open: **kleinian-1** (major), **mesh-2** (major; the panel now warns), solids-4 (notes only), solids-5, words-4,
words-5.

## Engineer "klein": `src/js/25-colour.js`, `src/js/30-shaders.js`, `src/js/40-render.js`

Read `notes/r7-engine.md` (what the last engineer found, per defect), `notes/r6-colour.md` and
`notes/r5-speed.md` (how the code is built so that it compiles quickly) first. Build:
`python build.py --name r9-klein --base base8 --use src/js/25-colour.js src/js/30-shaders.js src/js/40-render.js`.

1. **kleinian-1 (major): a trap that is the solid comes out cut open in a Kleinian group that leans, or with the
   trap off centre.** The last engineer found the cause (`notes/r7-engine.md`): the search carries the point into
   one copy of the pattern at every step (a slide by 2 along x, a slide by 2L along z with the third map, a half
   turn about mu/2) and tests the trap after each map. The trap is a fixed shape in space and those three moves
   do not carry it onto itself, so a piece of the solid that reaches across the edge of a copy is tested there
   against another part of the trap and ends at the edge with a flat face.
   The cure to build and judge: **let the trap share the pattern's own symmetry.** Where the search tests the
   trap at a point z, test it at z and at the images of z under the moves the search itself uses to stay in one
   copy (z shifted by plus and minus 2 along x in the sheared frame the wrap uses; z shifted by plus and minus
   2L along z when the third map is on; the half turn mu - z), and take the nearest. Then the value no longer
   jumps where the search changes copy, because the copy next door sees the same trap. The solid becomes the
   trap repeated the way the group repeats, which is also the natural meaning of a trap inside a Kleinian
   group. Keep the record of where the trap was touched (for the colours) in step with whichever image was
   nearest. Judge by pictures: entries 3 and 24 of the Kleinian list (the tester's reproduction, in
   `notes/_t6_defects.json`), entry 0 with the trap centre at x = 0.6, the three Kleinian examples of the
   Examples list, and all the trap shapes on entry 0, at Balanced and Fine: whole pieces, no flat faces, no
   sheets running out of the picture. If the half turn still leaves a small step (its boundary is a wavy line,
   not a mirror plane), say how large and show it. If the repeated trap fills the picture with copies, limit the
   images to the nearest ones and say so. Update the note that warns about leaning groups (remove it if the
   fault is gone), and give the exact sentence of the page's closing text that has to change
   (`src/body.html`, "This works in Mandelbrot and Julia pictures, and in Kleinian pictures whose group does not
   lean ...").
2. **solids-5: bubbles with ragged holes** at higher skips, off-centre traps and a small radius. The last
   engineer's finding: the rule that fades thin layers removes a layer in patches, where its wall is under two
   pixels. A layer should go as a whole or stay as a whole (by the step that made it, or by the size of the
   piece), not by the wall thickness at each pixel. Judge on the tester's scenes (`out/t6/solids/pj.json`).
3. **Small things in `40-render.js`:** while a picture job or a model job runs, do not prepare other formulas
   in the background (the export engineer measured the same job at 4.5 s against 2.4 s; the request with a
   code sketch is in `notes/_fix7_reports.json`, export, needs_from_others); and `idle()` should not report
   true while the graphics context is lost in the middle of a picture.
4. If time is left: words-5 (dark patch in a bead at Ultra fast with 40 iterations; the last engineer reasons
   that the rough estimate's slope samples give wrong surface directions) and words-4.

Limits: compile time at the opening settings under 2.6 s (Mandelbrot) and 1.1 s (Kleinian), measured with
`python out/me/perf.py base4 r9-klein base4 r9-klein base4 r9-klein` (least of the three visits; draw times
within a quarter of `base4` by the same rule). Every picture not named in a defect stays as `dist/v8.html` draws
it: make the reference pictures first with a fixed list (the last engineer's `out/r7/engine/scenes.py` is the
model: the 2D view at the opening settings, the opening pictures of the three modes, trap-coloured sets at
Balanced and Fine, the trap solids of Mandelbrot and Julia). `tools/smoke.json` (52 steps) must pass on your
final page. Time: aim for 60 minutes, stop at 80.

## Engineer "mesh": `src/js/46-mesh.js`, `src/css/46-mesh.css`

Read `notes/r7-mesh.md` and the mesh part of `notes/r7-engine.md` first. Build:
`python build.py --name r9-mesh --base base8 --use src/js/46-mesh.js src/css/46-mesh.css`.

1. **The cut face of a model** keeps a coloured rim two to four cells wide
   (`out/r7/engine/mesh/r7-engine/pics/cmp-cut-128.png`): a point whose outside end is outside only because of
   the cut plane or the wall of the grid should take the colour of an end whose own distance is at or below
   zero, which holds the cut face's colour (the request is in `notes/_fix7_engine_report.json`,
   needs_from_others).
2. **The first model of a formula waits about 3 s** while a program of its own is prepared, with nothing on the
   panel to say why. Say it in the panel's progress line in plain words for as long as it lasts.
3. **mesh-2 (major): a negative power gives a model that does not look like the picture.** What is known
   (`notes/r7-mesh.md`): the solid is made of sheets thinner than a cell; with offset 0 the model is dust, with
   the starting offset one fragment holds a quarter of the surface. The panel warns. Find out whether a model
   that is true to the picture can be had at all with what the samples give: try the starting offset at 1 and
   1.5 cells on this solid at 128, 256 and 512 cells with every piece kept and with the largest piece only, and
   compare each with the picture by the tester's measure (outline overlap, share of the picture's outline
   missing; `out/t6/mesh/check.py`). If some offset gives a model that looks like the picture, make the panel
   offer it when it detects such a solid (a sentence and a button, or a starting value); if none does, leave
   the warning and say in it what does help. Do not change what an ordinary solid gets.
4. Re-run the tester's seven standard jobs (`out/me/meshcheck8/` shows how to point the tester's scripts at
   another page) and report shape and colour numbers before and after.

`tools/smoke.json` must pass on your final page. Time: aim for 45 minutes, stop at 60.

## Rules for both engineers

Own files only; never plain `python build.py`; scripts, logs and pictures under `out/r9/<you>/`; notes in
`notes/r9-<you>.md`; one `tools/shot.py` at a time (nine testers and the other engineer share the GPU); text in
plain words, sentence case, no em dashes; no git, no publishing. Report: summary; files_changed; fixed (id,
what, evidence); not_fixed (id, why, learned); names_added; needs_from_others (with the sentences of the
closing text that are no longer true and a suggested wording); measurements; risks.

## The second check: nine testers on `dist/v8.html`

Rules as in `docs/CHECK6.md`, section "Rules for every tester", with these changes: the page under test is
`dist/v8.html`; your folder is `out/t9/<key>/`; defect ids start with `t9-<key>-`. For every defect of the first
check in your list, run its own reproduction (in `notes/_t6_defects.json`) on `dist/v8.html` and say whether it
is gone, changed or still there, with the evidence. Then look for what the fixes may have broken in your area.
A finding of the first check that is listed above as accepted or open is not news: confirm its state in one
line. Time: aim for 30 minutes, stop at 40.

- **solids**: solids-1 to solids-7. Then the cure for the "stack of slices" (N12), which no tester has seen
  yet: the user's own scene (the Douady rabbit close up at Fine) and three others, coloured by the sphere shell
  at radius 1 and 0.7, by the cross and by the planes: do the colours stay in the same places at Ultra fast,
  Fast, Balanced and Fine, at "Surface threshold, pixels" 0.2, 1 and 3, at 24, 60 and 120 iterations, and
  while zooming in by 2 and by 8; are there rings anywhere; does the dial "Orbit steps the trap reads" do what
  its help says. Then the nine entries of the Examples list: each sets what the hint says, shows a whole
  object, and looks like its name.
- **kleinian**: kleinian-1 (open: confirm, and that the note beside the choice is true and shown exactly when
  the fault shows), kleinian-2, layout-2. Then: do the colours of the Kleinian view stay the same across the
  four quality presets (the first check's p5-6); all 34 entries through the list and "Frame it" once more (the
  pearl search changed); the 2D view of five entries; the inside colourings in the Kleinian view (flat-2).
- **export**: export-1, export-2, export-3. Then the question nobody has measured since the colour cure: does a
  saved picture show the same colours in the same places as the screen, at "As on screen now", Fine and Extra
  fine, at the screen's size, twice and 4K, for a trap-coloured Mandelbrot, a Julia set, a trap solid, the 2D
  view with an inside colouring and the Kleinian view (compare scaled copies; report the mean difference and
  whether any region changes hue). Independence from later changes once more, with the new controls.
- **mesh**: mesh-1 to mesh-6 and walk-1 (mesh-2 is open: confirm the warning and judge its words). Then the
  standard jobs at 96, 128, 192, 256 and 512 cells: validity of the files, outline against the picture, colours
  against the picture, sizes and volumes across resolutions; a cut solid's face; a model of each Examples
  entry of the Julia group; the readme.
- **camera**: layout-1, layout-4, layout-5, solids-7, words-2, words-3. Then real input (copy
  `notes/camera_real.py`): on a desktop, drag, wheel, keys, double-click, the two limit boxes, the fly camera;
  on an emulated phone with touch, the new zoom row (slider, both boxes), pinch, the switch. Reset view and
  the start view with and without a trap solid. Sheets at 375 x 812, 1024 x 768 and 1400 x 950, dark and light.
- **dials**: controls-1, layout-3. Then all number boxes once more with real typing (the first check's driver
  `out/t6/controls/drive.py`), including the new ones (Orbit steps the trap reads; Trap thickness below 0.05),
  the step toggles, Extreme ranges, every "Reset this section" and "Reset everything" (do they cover the new
  keys and the two save panels; is anything left changed).
- **words**: words-1, words-3, words-4, words-5. Then read "Questions from testing, answered" from top to
  bottom once more and check every sentence against the page: the control exists under that name, the thing
  promised happens. Mark what is untrue, what claims more than was shown, and what is not plain words. Open
  the page fresh and list what it starts with against the user's list (N2), including the new dial.
- **flat**: flat-1 to flat-5. Then the user's remark "the 2d side is great, btw - keep that as it is": at the
  opening settings, compare the 2D view of `dist/v8.html` with `dist/v5.html` pixel for pixel for the thirteen
  pictures of the first check (`out/t6/flat/`), and say exactly which differ, by how much, and whether a
  person could see it.
- **walk**: walk-1, walk-2. Then wander again (the first check's driver `out/t6/walk/walk.py`, with a better
  test for a blank picture than the one that gave false alarms): five seeds, three window sizes, both themes,
  including the Examples list, the twin and Figure 4 buttons, the new dial, and jobs running; report every
  console error, stuck state, NaN or blank picture with the shortest sequence that shows it.
