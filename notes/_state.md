# Where the work stands (orchestrator's log; newest first)

## 2026-11-18 02:35: Version 6 published; round 6 running

- **Published:** Version 6 at https://claude.ai/artifact/Ko9sxAgS5VMvsdEZi4uu3e (same file path
  `squaring-lab.html`; republish with the same path, omit `capabilities` and `icon`). Frozen as `base6/` and
  `dist/v6.html`. `dist/v5.html` is the previous build (`base4/`).
- **In Version 6:** trap-shaped solids in all three modes (N3), Save a picture (N5), Save a 3D model (N6), the 2D
  view's outline, glow and inside colours and the painted cut face (N10), 15 Kleinian entries that move the
  turning-out sphere (N9), exact pearl distance, the first half of the ring cure (N12), speed back to Version 5,
  closing texts true of the page, "Show Figure 4" / "Back to one plane", the Julia list's "Found with two
  planes" and "As it was found", the mirror twins (flip z) with four buttons.
- **Measured on a quiet GPU** (`out/me/perf.py base4 v6b`): compile M 2.0 s (V5 1.8), K 0.7 to 0.9 s (0.8);
  draw M 712 to 725 ms (696 to 746), J 1485 to 1712 (1539 to 1620), K 298 to 341 (235 to 241).
- **Smoke test:** `tools/smoke.json`, 42 steps, passes on `dist/v6.html` (`out/me/smoke-v6c.log`). Generator:
  `out/r4/page/make_smoke.py` (my twin steps were added by `out/me/smoke_twin_patch.py`).
- **Running:**
  - workflow `squaring-lab-r6-colour` (task `w5ww5m2i5`, run `wf_4a3deb40-4ec`): one engineer, the proper cure
    for N12 (`docs/SPEC6.md`): a dial "Orbit steps the trap reads", colour read from a point on the surface, the
    skip count meaning the same in Mandelbrot and Julia mode, the Kleinian colour cure (p5-6), the opening look.
    Owns `25-colour.js`, `30-shaders.js`, parts of `40-render.js`; builds `dist/r6-colour.html` from `base6`.
  - workflow `squaring-lab-r6-check` (task `ww7a2m1bu`, run `wf_989ceea9-79e`): ten read-only testers on
    `dist/v6.html` (`docs/CHECK6.md`): controls, modes, solids, flat, export, mesh, kleinian, words, layout, walk.
    Their files: `out/t6/<key>/`.
- **Next:** triage the testers' defects by group; join the colour engineer's files (build, smoke, perf, look at
  its sheets, correct the closing text about the slices); fix pass with one engineer per group of files (never
  two on one file); publish Version 7; tell the user what was verified and what was not (the host's save
  confirmation cannot be exercised from here).

## N1, the state of the answer

- Two prototype rounds, six rules, none beats one plane (`notes/_pillow_lab.json`, `notes/_lab2.json`). Default
  stays Sphere inversions with one plane; two planes = Figure 4 only for c on the x-axis (the paper says the
  same, page 444, verified against the PDF).
- "Forced": lengths squared + flat slice + angle-true on the sphere of directions leaves ζ² and its mirror
  twin 1/conj(ζ)² (identity theorem; our argument).
- Found 02:00: the mirror twins = the modifier "flip z" (`docs/SPEC5.md`, last section; pictures
  `out/me/twin2-*.png`, `out/me/twin3-a.png`, `out/me/twins-for-user.png`). Seam-free, exact at z = 0, a
  different Mandelbrot solid. Not Figure 4.

## 2026-11-18 03:26: testers back; fix pass running

- Check of Version 6 (`notes/_t6_reports.json`, `notes/_t6_defects.json`): no blockers, 8 major, 28 minor. All 15
  points of the second round pass; N2, N4, N5, N7, N8, N9, N11 pass; N1, N3, N6, N10 partial; N12 in progress.
- `src/js/00-core.js`: `saveFile` no longer throws, returns `again` (checked with the smoke test,
  `dist/r7-core.html`).
- Running: workflow `squaring-lab-fix7` (task `wnwcpxrl1`, run `wf_4d254faf-d3d`): engineers export, mesh, camera,
  dial, page on `base6` (`docs/FIX7.md`); and still `squaring-lab-r6-colour` (task `w5ww5m2i5`).
- Next: when the colour engineer returns: build `base7a` = base6 + its three files, look at its sheets, smoke,
  perf; launch the engine part of `docs/FIX7.md`. When the five return: join everything, adjust the Mandelbrot
  examples' skip count, correct the closing text on the slices and on trap solids, smoke, publish Version 7.

## 2026-11-18 04:10: colour cure joined in trial; engine fix running

- Round 6 colour engineer returned (`notes/r6-colour.md`, `notes/_r6_colour_report.json`): the trap colour of a
  3D surface is read from the surface with a fixed number of orbit steps (dial "Orbit steps the trap reads",
  starts at 4; `PH_FIT` finds the surface); skip count means the same in every mode; Kleinian colour cure;
  model samples follow the same rule. My own check: `out/me/look9-a.png` (same colours at every Surface
  threshold, at 24 and 60 iterations, at Ultra fast and Fine; no rings), `out/me/look9-b.png`.
- `base7a/` = `base6/` + the three colour files + the new `00-core.js`; page `dist/v7a.html`; passes
  `tools/smoke-v6.json`.
- Running: `squaring-lab-fix7` (task `wnwcpxrl1`): page and dial done, export, mesh and camera still working;
  `squaring-lab-fix7-engine` (task `wh34lkuab`, run `wf_fe8c0b1e-bad`) on `base7a`: kleinian-1, solids-2,
  mesh-1 and the minor shader and colour findings. It is editing `src/js/25-colour.js`, `30-shaders.js`,
  `40-render.js` NOW, so Version 7 must be built with
  `python build.py --base base7a --use <the part-1 files from src> --page`, not from plain `src`.
- My edits for the join are in: closing text (trap answer, slices answer with the dial's real labels, "opens
  with"), `EXAMPLE_SKIP_M = [1, 1, 0]` in `75-presets.js`, phrases and labels in `out/r4/page/make_smoke.py`
  (52 steps now). Trial join `dist/v7b.html` (base7a + page + dial files) passes all 52 (`out/me/smoke-v7b.log`).
- Next: when export, mesh and camera return: read reports, build Version 7 as above with all part-1 files, smoke
  (52 steps), perf, look, publish. Then Version 8 with the engine fixes.

## 2026-11-18 04:19: Version 7 published

- **Published:** Version 7 (same link, same file path). Frozen as `base7/` and `dist/v7.html`. It is `base7a/`
  (Version 6 + the round 6 colour cure + the new `saveFile`) plus the five fix engineers' files
  (`notes/_fix7_reports.json`, `notes/r7-*.md`) plus my join edits (closing texts for the cure with the dials'
  real labels, `EXAMPLE_SKIP_M = [1, 1, 0]`, `CAM_TRAP_SKIP_M = 1`, phone stage height 34vh, smoke phrases).
  Built with `python build.py --base base7a --use <part-1 files> --page` because the engine engineer is
  editing the three shader files in `src/`.
- **Smoke:** `tools/smoke.json`, 52 steps, passes on `dist/v7.html` (`out/me/smoke-v7c.log`). Looked at:
  `out/me/v7/first-screens.png` (phone with the zoom as a row under the picture, Figure 4 on a phone, the
  desktop first screen), `out/me/v7b-sheet.png` (examples).
- **Fixed in Version 7 (tester ids):** N12 cure; solids-1; words-1, words-3, kleinian-2, layout-2, layout-4;
  layout-1, layout-5, solids-7 (not the Kleinian start view), words-2; controls-1, layout-3; export-1 (number
  never rises, first number rough), export-2, export-3; mesh-3, mesh-4, mesh-5, mesh-6, walk-1; nine trap
  solid examples; plainer closing text.
- **Open:** mesh-2 (negative-power model: needs the picture's own surface level in the raw samples, a shader
  change, see the mesh report's needs_from_others); kleinian-1, solids-2, mesh-1 and the minor shader and
  colour findings (engine engineer running, task `wh34lkuab`, on `base7a`); export asks `sceneWarm` to pause
  while a background job runs (40-render.js).
- **Next:** when the engine engineer returns: build Version 8 = `base7` + its three files, smoke, perf, look,
  correct texts it names, publish. Then a recheck by fresh testers of what was fixed, plus the two shader
  requests above, then the final report to the user.

## 2026-11-18 04:30: checks on Version 7

- Model against picture on `dist/v7.html` with the mesh tester's scripts (copies in `out/me/meshcheck/`, log
  `check.log`, pictures `pics/cmp-*.png`): closed, one piece each; outline overlap 0.95 (Mandelbrot), 0.967
  (rabbit), 0.956 (Julia c = -1); Mandelbrot volume 35.0 cm3 at 128 cells (Version 6: 42.7; 33.2 at 512), so the
  fattening is gone; hue difference median 8.4 degrees (Version 6: 91.5), 9.8 (66.3), 28.2 (32.5). The Julia
  model has the picture's colours but fewer, broader bands: a coarse grid reads fewer orbit steps. So mesh-1 is
  mostly cured by the colour cure plus the mesh engineer's blend.
- Speed on a GPU shared with the engine engineer (`out/me/perf.py base4 v6 v7`, three rounds): compile M 1.9 to
  2.3 s against 1.5 to 1.7 s, K 0.85 to 0.9 against 0.55 to 0.62; draw readings too noisy to judge (M: base4
  337, 362, 662; v6 695 to 736; v7 760 to 779; J: least 776, 708, 519). TO DO on a quiet GPU: check whether the
  Mandelbrot picture really draws slower than Version 5.

## 2026-11-18 05:30: Version 8 published; round 9 running

- **Published:** Version 8 (same link). Frozen as `base8/` and `dist/v8.html`; `src/` equals `base8/` at the
  start of round 9. Version 8 = `base7/` + the engine engineer's three files (`notes/r7-engine.md`,
  `notes/_fix7_engine_report.json`: solids-2, mesh-1, flat-2, flat-3, flat-5, solids-3, solids-6, walk-2) + my
  text edits (trap solids in leaning Kleinian groups, what is left with the rough estimate, the Kleinian and
  palette remarks of the 2D answer, the model's colours and the negative-power limit).
- **Checked by me on the join:** smoke 52 steps (`out/me/smoke-v8b.log`); model against picture
  (`out/me/meshcheck8/check.log`: hue median 2.8 to 7.5 degrees, outline overlap 0.945 to 0.972); pictures
  `out/me/look10-a.png` (thin trap whole, inside by trap no longer a hole, cut face matches the 2D view,
  Kleinian entry 3 still torn with its note); speed on a quiet GPU equal to Version 5 by least values, compile
  about 0.2 s more.
- **Running:** `squaring-lab-r9-fix` (task `whnnb3ocm`, run `wf_5517f941-3c3`): engineers klein (kleinian-1 by
  letting the trap share the group's symmetry, solids-5, two small things in 40-render.js) and mesh (cut face
  colour, first-model wait, mesh-2); `squaring-lab-r9-check` (task `w9hq7hipx`, run `wf_6c337abe-9cf`): nine
  testers on `dist/v8.html` (`docs/ROUND9.md`), files under `out/t9/<key>/`.
- **Next:** read both; join the engineers' files on `base8` (smoke, look at their sheets, text edits they
  name); fix what the second check finds if it is small and safe, else list it; publish Version 9; final report
  to the user: what was verified by whom, what is open (the host's save step, negative-power models if not
  cured, the seam-free Figure 4), and the pictures worth looking at.

## 2026-11-18 06:30: second check read; Version 9 published; round 10 running

- **Second check** (nine testers on Version 8; `notes/_t9_reports.json`, `_t9_defects.json`,
  `_t9_rechecks.json`): of the first check's findings 25 gone, 7 better, 8 unchanged (flat-1, flat-4 accepted;
  kleinian-1, mesh-2, solids-4, solids-5, words-4, words-5 open), none worse. 21 new: 2 major (t9-mesh-1 fins
  on the Sea urchins model; t9-mesh-2 colours of trap-solid models), 19 minor. Independent confirmation of the
  N12 cure on the user's own scene (rabbit close up): median hue difference 0.4 to 1.3 degrees across the four
  presets and thresholds, no rings on the broad surfaces at Fine.
- **Version 9 published** (`base9/`, `dist/v9.html`) = Version 8 + my page fixes: t9-words-1, -2, -3,
  t9-solids-1 (examples put the trap centre back), t9-dials-1 (Reset everything covers the save panels),
  t9-kleinian-2 (Drawing radius sentence on its own). Smoke: `tools/smoke-v9.json` (52 steps) passes.
- **After Version 9, in `src/`, not yet published:** the ray step dial stops at 1.2 (t9-walk-1; measured: the
  picture thins above 1.2 and is gone from 1.4); the model texts of the closing section; the round 9 mesh
  engineer's `46-mesh.js` (cut face rim, "Preparing to read this solid", better warning; mesh-2 measured not
  curable by any offset: `notes/r9-mesh.md`, `notes/_r9_r9_mesh_report.json`).
- **`base9m/`** = base9 + those; page `dist/v9m.html`; smoke `tools/smoke-v9m.json` passes
  (`out/me/smoke-v9m.log`). `tools/smoke.json` is kept as the Version 8 test for the round 9 shader engineer.
- **Running:** round 9 engineer klein (inside workflow task `whnnb3ocm`): kleinian-1, solids-5 on base8;
  `squaring-lab-r10-fix` (task `wshciobzj`, run `wf_432735fb-fc6`): mesh, camera, dial on `base9m`
  (`docs/ROUND10.md`).
- **Next:** when klein returns: join its three files onto base9m (+ round 10 files as they come), smoke with
  `tools/smoke-v9m.json`, look at its sheets, text edits; then one engine engineer for t9-mesh-2 and the small
  shader items of `docs/ROUND10.md`; publish Version 10 when round 10 and klein are joined; then the final
  report. No further rounds after that: what is still open is listed for the user.

## 2026-11-18 06:46: Version 10 published; last engineers running

- **Version 10 published** = `base10a/` (page `dist/v10.html` = `dist/v10a.html`): Version 9 + the ray step
  limit (1.2) + the round 9 mesh file (cut face rim gone, "Preparing to read this solid", clearer warning) +
  the round 9 shader engineer's three files (`notes/r9-klein.md`, `notes/_r9_r9_klein_report.json`: the huge
  sheets and spikes of Kleinian trap solids are gone, a few cut balls remain on leaning groups; no formulas are
  prepared while a job runs; `idle()` is false while the graphics are lost mid-picture) + text edits. Smoke:
  `tools/smoke-v9m.json`, 52 steps, passes (`out/me/smoke-v10a.log`).
- The cure I proposed for kleinian-1 (repeat the trap under the group's own moves) was built and judged bad by
  the engineer (fills the stage with huge balls; `out/r9/klein/t1-pairs-a.png`). What works: a search step that
  only comes back to a skipped step is skipped too.
- **Running:** `squaring-lab-r10-fix` (task `wshciobzj`): mesh (t9-mesh-1, -3, -4, -5), camera (t9-camera-1),
  dial (t9-dials-2) on `base9m`; `squaring-lab-r10-engine` (task `w6fw0m6uv`, run `wf_be1c9f11-b6a`) on
  `base10a`: t9-mesh-2, the fine lines at grazing angles (t9-solids-4, t9-words-4), the reach dial's help, and
  smaller ones. `src/` is being edited by all four: build releases from frozen bases with `--use`.
- **Next (last):** join round 10 (mesh, camera, dial files from `src/` onto `base10a`, then the engine files),
  smoke `tools/smoke-v9m.json`, model check (`out/me/meshcheck8/` scripts) on the three Julia examples, publish
  Version 11, write the final report on all 27 points. No further rounds.
- **Open after that, to tell the user:** the host's save confirmation (cannot be tried from here); negative-power
  models (measured: no setting gives a true model); a few cut balls in trap solids of leaning Kleinian groups;
  bubbles with ragged holes at higher skips (solids-5); the dim skirt and dark patch with the roughest settings
  (words-4, words-5); Point, Line and Ray look alike as solids (solids-4); a seam-free Figure 4 (open problem).

## 2026-11-18 08:10: session had ended mid-join; Version 11 published; the user questions the default

- The previous session ended at about 07:25 during the join. Nothing was lost: Version 10 stayed live.
- **Version 11 published** = `base11/` (page `dist/v11.html`) = `base10a/` + round 10's mesh, camera and dial
  files (`notes/r10-mesh.md`, `notes/_r10_r10_camera_report.json`, `notes/_r10_r10_dial_report.json`; the mesh
  report is in the workflow output only). Smoke `tools/smoke-v9m.json`, 52 steps, passes
  (`out/me/smoke-v11a.log`).
- **Interrupted, not finished:** workflow `squaring-lab-r10-engine` (run `wf_be1c9f11-b6a`): t9-mesh-2 (model
  colours of trap solids), fine lines at grazing angles, the reach dial's help. It left partial edits in
  `src/js/25-colour.js` and `src/js/30-shaders.js` (they differ from `base11/`); `src/js/40-render.js` is
  untouched. Before any build from plain `src/`, either restore those two files from `base11/js/` or relaunch
  the engineer (resumeFromRunId) and let it finish.
- **The user, back at 08:00:** "it's smooth - not what I imagined the algorithm to look like. and if that
  'third map' or whatever equivalent isn't here, so what's the point of this if it's just the inflated 2d
  view?" The page opens with one plane (my change for N1). Answered: the third-map equivalent is Planes = 2
  ("Show Figure 4"); whole only for c on the x-axis, as in the paper. Asked whether the page should open with
  two planes again.

## 2026-11-18 08:30: the user asks for a rule that applies everywhere; shader fixes relaunched

- The user: the two-plane rule is not the right one to them, and a rule that makes the 2D thing happen only in
  one plane feels off: "is there no analog quaternion operation that applies everywhere for 3d
  rotations/inversions?"
- Answer given: there is exactly one, the quaternion square, which is the Lathe approach. Checked by numbers
  (`notes/plane_free_check.py`, 200,000 points, worst relative difference 4e-12): the sum of sphere inversions
  with NO plane chosen, v -> e + 2 inv(inv(v - e) - inv(v + e)), IS the quaternion square
  (x^2 - y^2 - z^2, 2xy, 2xz). It gives the flat set spun about the x-axis: rings (`out/me/lathe-sheet.png`).
  The plane in "Sphere inversions" enters through the turn about the z-axis in its formula. Why nothing better:
  a rule that treats all directions alike can only turn a vector about itself; in 3D only maps built from
  inversions keep shapes true (Liouville), and one such map alone makes no fractal, several taking turns do
  (Kleinian). Offered: build the Kleinian world's own "Mandelbrot" (the map of all groups, the Maskit slice,
  with the quaternion mu) as a prototype. Waiting for the user's choice.
- `src/` was put back to `base11/` (= published Version 11). The interrupted engineer's partial edits are kept
  in `out/me/partial-r10-engine/`. Relaunched as workflow `squaring-lab-r11-engine` on `base11`
  (t9-mesh-2, t9-solids-4, t9-words-4, t9-solids-2, ...); it owns the three shader files in `src/`.

## 2026-11-18 11:20: Version 12 (first cut) published; every approach its own entry; round 12 running

- The user (10:45): "yes try it, and add all these approaches btw (like have the current approach be distinct
  from the old one, rather than have it as a manifestation of the old one)", plus the hidden-rotation-axis
  question (verbatim in `docs/ROUND12.md`).
- **Twisted quaternion square tried and drawn** (`out/me/tilt/`, sheet sent: `out/me/tilted-quaternion.png`).
  Rule: v^n = A^(-n) L^n A (v), A = turn by the tilt about z, L = quaternion power. n = 2:
  ((x+iy)^2 - z^2 e^(-2it), 2z(x cos t - y sin t)). Exact on z = 0 for whole powers at every tilt (1e-15);
  tilt 180 = the Lathe's mirror twin; tilt 90 = no end. Rings break into a body with tunnels; skin smooth.
- **`src/js/10-approaches.js` rewritten by me** (script `out/me/tilt/split_entries.py`): seven entries,
  `mercator` (one plane; dials turn, lift), `fold` (two planes; dials planes, lift), `lathe` (renamed
  "Quaternion square (Lathe)"), `tilt` (new), `bulb`, `classic`, `split`; `group` on each and
  `APPROACH_GROUPS`. `S.param.mercator.planes` no longer exists.
- Bases: `base12a/` = base11 + that file (`dist/v12a.html`). `base12b/` = base12a + three page files patched by
  me just enough (`out/me/v12b/make.py`: Show Figure 4 -> `fold`, Back to one plane -> `mercator`, "As it was
  found" switches the entry, texts). **Version 12 published = `base12b/`** (`dist/v12b.html`). Checked with
  `out/me/v12b/check.json` (15 steps, pass) and the old smoke run softly (`out/me/v12b/smoke-soft.log`: the 21
  failing steps all go back to the removed Planes dial, 31 pass). No full smoke test yet for this version.
- **Running:** workflow `squaring-lab-r12-approaches` (task `w2fxihm9x`, run `wf_5879584e-190`), spec
  `docs/ROUND12.md`, base `base12a`: page engineer (list headings, buttons, closing text with two new answers,
  `tools/smoke-v12.json`), tried-rules engineer (softfold, axisbulb, pillow as entries in group 'tried'), then
  two checkers and a fixer. Their files are in `src/`. My three patched files in `base12b/` are stand-ins and
  are replaced by theirs at the join.
- **Returned, not joined yet:** workflow `squaring-lab-r11-engine` (report `notes/_r11_engine_report.json`,
  notes `notes/r11-engine.md`): `src/js/30-shaders.js`, `src/js/25-colour.js` (model colours of trap solids:
  bubbles 21.5 -> 5.9 deg, urchins 69 -> 25; fine lines in shadowed folds gone, cause was the shadow ray; help
  texts; two notes). **Before it goes into a version: speed on a quiet GPU**
  (`python out/me/perf.py base4 r11-engine v11` three rounds; the fuller shadow query measured 1.275 x base4
  on the Mandelbrot view before its longer strides were added). Its wishes for the closing text and a smoke
  step for a Kleinian model are in the report (needs_from_others).
- **Join plan for the next version:** base12a + round 12's files from `src/` + the two shader files; smoke
  `tools/smoke-v12.json`; model check on the three Julia examples; perf; publish.

## 2026-11-18 12:30: the user asks for a pinned picture on phones, a Learn tab, and the hidden-space ladder

- The user (11:55, verbatim in `docs/ROUND13.md`): (1) on a phone the picture should stay pinned at the top while
  dials are changed; (2) a 4th "learning" tab with a 2D and 3D option that shows the steps of ONE iteration of
  any approach; (3) still does not see why turning about z matters in 2D and turning about w does not in 3D:
  their ladder is line (flip = turn through hidden space), page (hidden axis), space.
- **Round 12 state at 12:00:** both builders done (reports `notes/_r12_build_reports.json`): page engineer
  (headings, buttons, closing text, `tools/smoke-v12.json` 58 steps) and tried-rules engineer (softfold,
  axisbulb, pillow as entries; ten entries in all; idle-time preparation about 10 s longer). Its two checkers
  and the fixer are still running (task `w2fxihm9x`).
- **Round 13 launched** (task `wg05crbrl`, run `wf_f91fabcc-b98`, spec `docs/ROUND13.md`): steps engineer
  (`src/js/65-learn-steps.js`: every approach's power broken into moves, chain must equal `MATH`), view engineer
  (`src/js/66-learn-view.js`, `src/css/65-learn.css`: Learn as a 4th choice under Show, `S.learn`, own canvas,
  1D/2D/3D, hinge and sheet drawn, transport under the stage), pin engineer (`src/js/85-pin.js`,
  `src/css/85-pin.css`), then three checkers (truth, page and phone, a first-time learner) and a fixer.
  NEW FILES ONLY, because round 12 still owns the existing ones.
- **Test base `base13t/`** (`dist/v13t.html`) = base12a + round 12's files as of 12:00 + two hooks made by
  `out/me/r13/hooks.py` (90-boot.js: learnInit/pinInit calls and two names on window.squaringLab;
  40-render.js: touch() returns early while `S.learn`). **At the join run `python out/me/r13/hooks.py <dir>`
  again** on the final files (it is idempotent).
- **Join plan:** new base = base12a + round 12's final files (after its fixer) + hooks + round 13's five new
  files + the two shader files of round 11 if the speed holds (`python out/me/perf.py base4 r11-engine v11`,
  several interleaved rounds, least values). Smoke: `tools/smoke-v12.json`. Publish round 12 on its own as soon
  as it returns (publish early), then the Learn tab and the pin.
- Answer given to (3): the ladder is right and leads to the quaternion square: the rule only doubles the lean
  from the x-axis; a line has two leans, a page has all of them, space has no new ones, only a second angle
  (which way the point leans) that the rule does not look at. A point gives 2 numbers, a turn of space needs 3.

## 2026-11-18 13:20: Version 13 published (round 12 complete + Learn tab + pinned picture, first cut)

- **Round 12 returned** (reports `notes/_r12_reports.json`, notes `notes/r12-page.md`, `notes/r12-fix.md`).
  Checkers: 1 major, 16 minor; the fixer fixed all but W7. **The major one was my own wrong fact**: "at tilt 90
  and -90 the Mandelbrot solid has no end" is FALSE (the solid ends inside radius 2 at every tilt). Also: tilt
  180 = the Lathe's mirror twin only for even powers. Both were on the page for Version 12 and in my message to
  the user; corrected on the page in Version 13 and in `docs/ROUND12.md`. TELL THE USER.
  Left open: W7 (the Julia group "Found with two planes" holds 6 entries but 15 record two planes, so "As it was
  found: two planes" shows for 9 others, the Basilica included): a naming choice for me or the user. The skin
  of the tried entries stands up to 0.3 off the true set (distance estimate; shader files).
- **Bases:** `base13a/` = base12a + round 12's final files + the three hooks (`out/me/r13/hooks.py`: 90-boot,
  40-render touch guard, uiResetAll -> learnReset). `base13t/` was synced to the same files at 13:13 so that
  round 13's checkers and fixer build on the final words (`tools/smoke-v12.json` now has 60 steps and expects
  them). **`base13b/` = base13a + round 13's five new files as of 13:15 = Version 13** (`dist/v13b.html`).
  Smoke `tools/smoke-v12.json`: 60 steps pass on it (`out/me/v13/smoke-j.log`). My look:
  `out/me/v13/sheet-desk.png`, `sheet-phone.png`.
- **Round 13 builders' reports:** `notes/_r13_build_reports.json`. Steps: all ten approaches, chain equals MATH
  to 5e-15 on 60,000 points each; view: 758 lines, Learn on/off leaves the solid pixel-identical; pin: at
  920 px and narrower and at least 520 px high, `.bench-main` sticky, `svh` units, "Unpin picture" button.
  Not tested on a real phone. **Still running:** its three checkers (truth, page and phone, learner) and then
  the fixer (task `wg05crbrl`). Their fixes land in `src/` (the five new files) -> next version from base13a.
- **Shader fixes of round 11** still not joined: `dist/v13s.html` = base13b + the two shader files; timing run
  in the background (`out/me/v13/perf-shader.log`, five interleaved rounds base4 / v13s / v13b) while the
  checkers also use the GPU.

## 2026-11-18 13:45: the shader fixes of round 11 pass the speed rule and are accepted

- Timing, five interleaved rounds while three checkers also used the GPU (`out/me/v13/perf-shader.log`), least
  values: base4 M compile 2177 / draw 352, J draw 433, K compile 724 / draw 129; **v13s (with the two shader
  files)** M 2367 / 357, J 449, K 952 / 127; v13b (Version 13) M 2061 / 343, J 438, K 893 / 100. Drawing is
  within 4% of the published page and 1.01 x base4. Compile is 15% longer on the Mandelbrot program, under the
  limits used before (2600 and 1100 ms).
- `tools/smoke-v12.json`: 60 steps pass on `dist/v13s.html` (`out/me/v13/smoke-s.log`). Models at 64 cells
  come out for the Kleinian view, the example "Chain of bubbles" and the twisted square
  (`out/me/v13/models*.log`; each on a fresh page, because a second job needs the first model discarded).
- **`base13c/`** (`dist/v13c.html`) = base13a + `25-colour.js`, `30-shaders.js` of round 11 + three sentences in
  the closing text that its engineer asked for (`out/me/v13/closing_r11.py`, also applied to `src/body.html`).
  **Next version = base13c + round 13's five new files after its fixer** (`src/js/65-learn-steps.js`,
  `66-learn-view.js`, `85-pin.js`, `src/css/65-learn.css`, `85-pin.css`); then smoke, a look at phone size,
  publish.
- Not done from round 11's list: a smoke step for a Kleinian model (the smoke file belongs to round 12's
  generator `out/r4/page/make_smoke.py`; add it at the next change of that file), t9-solids-3, t9-export-1,
  the urchins' ball colour (24.9 degrees).

## 2026-11-18 13:50: THE USER PARKS THE POLISH WORK: the search for the right 3D rule comes first

- The user (13:45): "you don't have to do any of this yet, we're just working on getting the right approach for
  the 3d fractal". "This" = the shader fixes, the checkers on the Learn tab and the pin, joins and test rounds.
- Done on that: workflow `squaring-lab-r13-learn` (task `wg05crbrl`, run `wf_f91fabcc-b98`) STOPPED at 13:46
  while its three checkers were running. They had filed no report; the fixer had not started. The five new
  files in `src/` are byte for byte the published ones. Nothing is half-edited.
- **Live: Version 13 = `base13b/`.** It has the Learn tab and the pinned picture as built (engineers' own
  checks, the 60-step smoke test, my look; no independent check, no real phone).
- **Parked, ready, not published:** `base13c/` = base13a + round 11's shader fixes + three closing sentences
  (timed, smoke passes). To finish later: publish from base13c + the five new files; if wanted, run round 13's
  check and fix phases again (Workflow with its scriptPath and resumeFromRunId `wf_f91fabcc-b98`: the three
  builders replay from cache, the checkers run fresh).
- **Do not start test, check or polish rounds on my own until the user asks or the approach is settled.**
  Small experiments that serve the search for the rule (a new rule drawn, a picture, a number check) are the
  work now. Open offer, never answered by the user: the Kleinian world's own "Mandelbrot" (the map of all
  groups, c as the group's parameter), which is the paper's own road extended to the Mandelbrot side.

## 2026-11-18 14:55: round 14 launched: the paper's rule, 4D quaternion slices, rotors, approach menu

- The user (about 14:20, verbatim in `docs/ROUND14.md`): "yes try it as a new approach" (the paper's road), and:
  the approaches section as a menu, merged with the equation section, only the chosen approach's dials under
  it, explanation on hover; add the pure quaternion approach (4D Mandelbrot, 3D slices); explore the
  geometric-algebra rotor recipe of their image (reference axis e3, rotor R onto v, R squared applied to the
  axis, times |v|^2) as another approach.
- **The paper re-read** (`notes/paper-kucera.txt`, extracted with pdfminer): its squaring on the circle is
  piecewise: g1 = inversion in the circle centre -2 radius sqrt 3 + mirror in the real line; g2 takes the inside
  of the circle centre 1 + sqrt3 i onto the outside of the one at 1 - sqrt3 i; arcs AB, BC, CA use g2, g1,
  g2^-1; "conjugate" to doubling, NOT equal to it. 3D: spheres at the same centres (one plane: inflated sets);
  plus g3 = g2 turned 90 degrees about x (Figure 4, "limited to c in R"). My reading, used in the brief:
  H(d) = mirror_y(inversion in sphere k of d) inside cap k, mirror_y(d) outside all caps: continuous, each piece
  keeps shapes; the slice at z = 0 is a cousin of the flat set, not the flat set.
- **Base `base14a/`** (`dist/v14a.html`) = base13c (shader fixes in) + the five round-13 files as published.
  `src/` was brought in line with it (hooks applied to src).
- **Running:** workflow `squaring-lab-r14-rules` (task `wc2658afe`, run `wf_a65fdb34-303`), three builders, NO
  checker phase (the user wants rules tried, not polish): rules (`10-approaches.js`, zmap hook in
  `30-shaders.js`: entries quat4, rotor, kleinsq, kleinsq2, rotorframe; new group 'kleinian'), menu
  (`body.html`, `80-ui.js`, css, `tools/smoke-v14.json`), turns (stand-alone under `out/r14/turns/`: both
  rules at every step, union and common sets, Kleinian and exact pairs).
- **Checked by me** (`out/me/r14/rotor_check.py`, real rotor arithmetic): the image's recipe with the
  reference along x IS the quaternion square (6e-15); with any other reference axis it is the same rule turned
  in space (1e-14); with e3 as written the flat plane is crushed onto the -z axis. The frame version
  (R = Rz(lon) Ry(lat)) is exact on the flat plane and on the half x > 0 of the plane y = 0, and is a
  different rule from the Lathe.
- On return: join = base14a + their files; `tools/smoke-v14.json`; look at pictures; publish; show the user
  the rules' sheets and the turns verdict.

## 2026-11-18 16:10: Version 14 published; round 15 (square pillow) launched 16:55

- **Round 14 collected** (reports: `notes/_r14_reports.json`, three in a list: turns, rules, menu). Join =
  `base14b/` = base14a + src files of rules (`10-approaches.js`, `30-shaders.js`, `65-learn-steps.js`) and
  menu (`body.html`, `80-ui.js`, `66-learn-view.js`, `00-base.css`, `65-learn.css`). `src/` == `base14b/`.
  Page `dist/v14b.html`. Smoke `tools/smoke-v14.json` 62/62 at 1400x950, no console errors
  (`out/me/v14/smoke-b.log`); I added the pair axisbulb/quat4 (Julia) to `twins` in
  `out/r4/page/make_smoke.py`. My own looks: `out/me/v14/wide-*.png`, `phone-*.png`.
- **Published as Version 14** (from `base14b`, `python build.py --base base14b --page`). It also carries the
  round-11 shader fixes that were parked. 15 entries, 6 groups, approach as a menu.
- **Sent to the user:** `out/me/v14/new-approaches.png` (my labelled sheet, script `out/me/v14/usersheet.py`)
  and `out/r14/turns/sheet-for-user.png`.
- **Verdict of round 14 (told to the user):** quat4 = the Lathe at dials 0 (pixel for pixel), other slices
  are smaller rings, tilt 90 a ball; rotor = the Lathe turned onto the reference axis (five axes measured);
  rotorframe = a new rule, slice exact, smooth wound sheets, tears at the z-axis, crushes the half-plane
  y = 0, x < 0; kleinsq = slice is a cousin (80 % of the flat M inside, an eighth outside); kleinsq2 = buds
  round two circles for c on the x-axis, shards elsewhere; turns trial = "some order" swells to a fat lump
  off the axis, "every order" is empty off the axis; only E-union at c = -1 shows beads in every direction,
  and it needs a voxel table to draw.
- **Not tested by anyone:** the menu on a real touch screen or with a real keyboard; quat4 in the mosaic.
  Known: the scorecard's slice pill says ok for quat4 with dials away from 0 (the text is right, the pill
  cannot know); the Learn tab shows quat4 as the Lathe step without the slice dials.
- **New idea, mine: the square pillow with a belt** (`docs/ROUND15.md`, reference `out/me/r15/pillow_ref.py`).
  Directions on a square pillowcase (torus / +-), direction map (s, t) -> (-2s, 2t) for t <= 1/4, (2s, 1 - 2t)
  above; the belt t = 1/3 is the equator and carries exact angle doubling; no corner or fold on the belt
  (the old triangle pillow ran its plane through the corners, which is why it failed). Checked: round trip
  3e-11, equator doubling 2e-15, no jump, sideways stretch 2.0000 next to the plane (mirror flip).
  First look (`out/me/r15/first-look-129.png`, 129^3 voxels): z = 0 cut is the flat set; rabbit = separate
  rounded bodies in space; c = -1 = bodies with horns, y = 0 cut one band with spikes; Mandelbrot solid a
  lopsided rock with fins. Lopsided in z at power 2 by nature (belt at 1/3, not 1/2); power 3 is symmetric.
  Why it might be the right family (reasoned): it is Mayer's quasiregular power map (the Zorich map's
  analog of z^2) with a mirror; every repetition distorts shapes by a bounded amount, unlike one-plane
  (crushes sideways) and the Mandelbulb (smears).
- **Running:** workflow `squaring-lab-r15-square-pillow` (task `w4zp81c43`, run `wf_3935fe58-f29`), two
  builders, no checker: entry (`sqpillow` "Square pillow", new group 'pillow', `src/js/10-approaches.js`,
  page `dist/r15-entry.html`, sheet `out/r15/entry/sheet-sqpillow.png`) and study (numpy,
  `out/r15/study/sheet-for-user.png`: bodies or lump, detail at smaller sizes, distortion under repetition,
  better layouts, Mandelbrot solid, power 3).
- On return: join = base14b + `10-approaches.js` (+ `65-learn-steps.js` if changed); smoke once; look at the
  close-ups; publish as Version 15; show the sheets with a blunt verdict.

## 2026-11-18 17:40: user rejects Kleinian squaring; round 15B launched (pillow in closed form, powers)

- **User (verbatim in `docs/ROUND15B.md`):** Kleinian squaring is wrong (z = 0 not correct; bulbs follow the
  number of planes, not the power). The paper's 3D basilica is their picture of right. "try again, and really
  believe in yourself". Tests saved in memory `right-rule-criteria`.
- **To do at the next join:** move `kleinsq` and `kleinsq2` to group 'tried' (the user called them wrong).
- **The pillow in closed form** (mine; `out/me/r15/shadow_ref.py`, checked n = 2..5): 4D pair (z1, z2) of equal
  length rho, rule (conj(z1)^n, z2^n), folded by (z1, z2) ~ (conj z1, conj z2). Survivors x1 = Re z1,
  x2 = Re z2, w = Im z1 Im z2 / rho; rule = Chebyshev: x1' = rho^n T_n(x1/rho), x2' = rho^n T_n(x2/rho),
  w' = -rho^(n-1) w U_(n-1) U_(n-1). Belt b0 = 2 pi/(n+1) laid on Z = 0: X = x1,
  Y = s0 rho w/(rho - c0 x2), Z = -(x2 - c0 rho)/s0; rho = root of a quartic. Measured: plane = z^n to 7e-15,
  no jump, sideways stretch at the plane exactly n (flipped). Same direction dynamics as `pillow_ref.py`
  (sinh layout), another layout, so solids differ off the plane.
- **Why I believe in the pillow (reasoned):** for shapes to keep proportions under repetition, sideways
  stretch must match lengthwise stretch (n) at every step; on a round sphere that is impossible, on a flat
  pillow it is automatic, and then the direction map has degree n^2 (bodies follow the power). Known limits:
  the layout depends on the power; even powers are lopsided above/below the plane (belt at 1/(n+1), a mirror
  symmetric belt needs 1/4, which only odd powers have); the plane y = 0 holds the four corners (fold
  dynamics there, expect spikes, not a second basilica). Correction to tell the user: the belt is two thirds
  of the way up the folded pillow (t = 1/3 of the unfolded height 1), not "one third".
- **Running, two workflows:**
  - `squaring-lab-r15-square-pillow` (task `w4zp81c43`): entry `sqpillow` in `src/js/10-approaches.js`
    (sinh layout) + study `out/r15/study/`.
  - `squaring-lab-r15b-pillow-closed-form` (task `wxyo1mmyl`, run `wf_c049dacb-276`): shadow engineer
    (private copy `out/r15/shadow/10-approaches.js`, entry `pillow4d` "Pillow from 4D (closed form)", marks
    R15B-BEGIN/END, page `dist/r15-shadow.html`, sheet `out/r15/shadow/sheet-pillow4d.png`, powers 2..5) and
    powers researcher (`out/r15/powers/sheet-for-user.png`: bodies against the power, layouts compared).
- **Shown to the user:** an inline widget (flat pillow sheet and the ball of directions with the same grid,
  a point and where the rule sends it).
- On return of both: join = base14b + src `10-approaches.js` (sqpillow) + the R15B block (pillow4d) + kleinsq
  entries moved to 'tried'; smoke once; look at the close-ups and the powers; publish Version 15; show sheets
  with each of the user's five tests answered yes or no.

## 2026-11-18 18:10: round 15 collected, Version 15 published; round 15B still running

- **Round 15 reports:** `notes/_r15_reports.json` (study first, entry second). Pictures:
  `out/r15/entry/sheet-sqpillow.png`, `out/r15/study/sheet-for-user.png`, `out/r15/study/sheet-layouts.png`.
- **Join:** `base15a/` = base14b + `src/js/10-approaches.js` (entry `sqpillow` "Square pillow", group 'pillow',
  whole powers 2..5) + `kleinsq`, `kleinsq2` moved to group 'tried' with "Tried: ... Failed: ..." tags
  (`out/me/v15/kleinsq_tried.py`). `src/` == `base15a/`. Page `dist/v15a.html`, smoke 62/62, no console errors
  (`out/me/v15/smoke-a.log`). **Published as Version 15.** Sent: `out/me/v15/square-pillow.png` (my sheet,
  `out/me/v15/usersheet.py`) and the study's sheet.
- **What the square pillow is (measured by the two engineers):**
  - Slice z = 0 exact (pixel for pixel, point for point); no jump; no dial.
  - Power 2: Mandelbrot solid = lopsided rock with fins (1.54 above the plane, 0.52 below), no bulbs.
    c = -1 = one spindle with spikes: cut at the touching point is 21 to 24 % of the middle cut (one plane:
    3.8 %), matter 0.54 above and below the point. Rabbit: separate bodies meeting at single points, smaller
    bodies round them; lifting c 0.12 off the plane grows them together. Close up: streaks, blades, slits
    (brute-force cuts agree), not smaller bodies.
  - Cause of the joined real axis (measured + reasoned): the rule keeps the upright plane y = 0 (the pillow's
    mirror line through all four corners) and folds directions there onto half the circle (181 of 360
    degrees). The fixed direction +x always lies on that mirror line, so every mirror-symmetric pillow
    layout has it (ten layouts tried, all joined at c = -1).
  - MY EXPECTATION WAS WRONG: shapes are kept under repetition only without c (1.9 to 1, steady). With c the
    error grows: rabbit 12 after 14 steps (Mandelbulb 10, one plane 85), c = -1 2,710 (Mandelbulb 12).
    The Mandelbulb without c is steady too (1.43). Only one plane grows without end.
  - Layout matters: a Joukowski layout (closed form, one complex square root; formula in the study's
    needs_from_others) gives the rabbit knobs on knobs down to a box 0.01 wide (stretch 3.7 instead of 12)
    but c = -1 becomes a smooth lump with horns and the belt is no longer angle-true.
  - Power 3: mirror-symmetric to rounding; Julia c = i = a ball with bodies on every side, round knobs on
    knobs at three sizes; Julia c = (0.3, 0.5, 0) = buds with rings of smaller buds (page renderer);
    Mandelbrot solid = a block or cushion with buds on four horned corners. Powers 4, 5: more buds on
    corners and rims (opening view only). Power 3 with c on the x-axis: NOT yet looked at (the 15B powers
    study has it). At power 3 the upright plane's directions cover all 360 degrees.
  - `out/me/r15/pillow_ref.py` is coarse within 1e-4 of a seam (its bisection); `out/r15/study/fastpil.py`
    is the tight reference.
- **My reasoning, to tell as reasoning:** (1) a bulb sits where one number (the turn per step) is a
  fraction; on a curve one condition picks points, on a surface it picks lines, so a 3-number rule grows
  its Mandelbrot bulbs along lines: rings (quaternion), a row on the flat rim (one plane), fins (pillow,
  Mandelbulb). (2) Flat pillows: the square's belt is 2/3 of the way up, so power 2 is lopsided by nature;
  a mirror-symmetric belt (half way) exists only for odd powers.
- **Corrections owed to the user (told 18:15):** belt is two thirds of the way up, not one third; "nothing
  smears" is false at power 2; "shapes kept under repetition" holds only without c.
- **Still running:** `squaring-lab-r15b-pillow-closed-form` (task `wxyo1mmyl`): shadow (private entry
  `pillow4d`, powers 2..5) and powers (bodies against the power; real c at each power).
- On its return: merge the R15B block into `src/js/10-approaches.js` (group 'pillow' exists already: drop its
  group line), smoke, publish Version 16, show the powers sheet; answer the user's five tests per power.

## 2026-11-18 18:55: user sets the order: basilica first; round 16 launched

- **User (verbatim in `docs/ROUND16.md`):** "n=3+ is not good enough. if julia is easier, then start with that
  basilica and don't attempt a mandelrbot until the julia passes, and if the mandelbrot fails, go back to
  another julia." Keep every earlier constraint. Higher n smears instead of looking as expected.
- **Stopped** workflow `squaring-lab-r15b-pillow-closed-form` (task `wxyo1mmyl`): the pillow cannot give the
  basilica (joined on the whole x-axis by its nature). Its private files, if any, are under `out/r15/shadow/`
  and `out/r15/powers/`; not merged, not needed.
- **My scouts** (`out/me/r16/scout.py`, `scout2.py`, `scout3.py`, `basilicas.py`; all importable):
  - Keeping the point's own plane through the x-axis (lathe with length changed by azimuth) gives tubes
    (4-pointed, square), never beads. Latitude x3 with longitude x2 falls apart.
  - **New rule, mine: the one-plane square about a plane that turns with the point.** phi = atan2(z, y),
    psi = q (phi - sin(2 m phi)/(2 m)), F = Rot_x(psi) P Rot_x(-psi), P = one-plane square. m = 2, q = -1
    "away" (4 buds, the Figure 4 look), q = +1 "along" (8 buds). Planes z = 0 and y = 0 exact (7e-15, 4e-15),
    no jump, both mirrors and the quarter turn, length squared. Basilica volumes 0.68, 0.65 (two planes
    nearest 0.64, one plane 0.72). Picture sent to the user: `out/me/r16/basilicas.png`.
  - Pure winding psi = (1 - m) phi (no flat spot): same basilica, but paper thin off the x-axis (sideways
    stretch at the plane is 2r - 2p(r - x) for slope p of psi there; p = 0 is the angle-true one).
  - Rough peeks (not verdicts): away: rabbit in pieces, c off the plane empty, Mandelbrot solid = two thin
    crossed leaves (volume 0.30). Along: rabbit a swollen lump (1.64), off-plane c gives bodies, Mandelbrot
    solid a lumpy body (1.42) with z = 0 and y = 0 cuts both the flat set.
  - For a whole power n I chose m = n planes (count round the axis 2n or 4n, so it follows the power). My
    choice, said in the brief. Open point to tell the user: the rule still has special planes (two at power
    2, because space has two sideways axes).
- **Running:** workflow `squaring-lab-r16-basilica-first` (task `wsvq7rahn`, run `wf_c88d693d-f0e`), two
  builders: bench (`out/r16/bench/`: tests J1..J9 calibrated on known rules, stage 1 on away / along /
  winding, stage 2 only for passers, `sheet-for-user.png`, `README.md`) and entry (`turnaway`, `turnalong` in
  `src/js/10-approaches.js`, group 'inversions', page `dist/r16-entry.html`, `out/r16/entry/sheet-turning.png`).
- On return: read the calibration table first (is the bench judging as the pictures do?); join base15a +
  `10-approaches.js`; smoke; publish Version 16; show the basilica from the lab renderer with J1..J9 as yes or
  no. Mandelbrot verdict only for stage-1 passers. If stage 2 fails: next round = searchers on the family
  "how the reference plane turns" (psi profile, and beyond), using the bench.

## 2026-11-18 20:50 round 16 collected, Version 16 published, round 17 launched

- Round 16 reports: `notes/_r16_reports.json` (text: `out/me/r16/reports.txt`). Bench in `out/r16/bench/` (README there);
  entries `turnaway`, `turnalong` in `src/js/10-approaches.js` (R16-TEXTS marks).
- Bench verdicts: `along` passes J1..J8; `away` fails J8 (ribs); `wind2` fails J4, J8. Stage 2 for `along`: FAILS
  (lumpy rock, ridges, period-2 body fused). Record: "Turning plane, along: basilica passes the bench, Mandelbrot fails".
- MY CHECKS (point by point, `out/me/r16/truth.py`, `truth2.py`, `closecut.py`): the bench's voxels are too coarse.
  Between its planes the skin of `along` carries thin fins, tufts of hair and droplets (closecut worst 3.1;
  twoplane 0.04, oneplane 0.00, away 17, wind2 10.6). So `along` is NOT clean close up. Stage 1 from now on =
  bench AND closecut <= 0.3 AND the eye. The lab's ribs at 14 iterations are mostly the low iteration count.
- `out/me/r16/refsolids-161.png`: Mandelbrot solids of twoplane (crossed slabs with fins), oneplane (flat slab,
  lens buds; period-2 disc only 0.08 thick, worked out: saddle-node on the pole axis at 1/24), lathe (rings),
  away (thin crossed leaves), along (lumpy rock).
- Version 16 = base16a = base15a + `js/10-approaches.js` (two entries, texts patched by `out/me/v16/patch.py`)
  + `js/40-render.js` (an entry may cap the distance estimate: `deMax`; both turning entries use 0 = Rough,
  because Exact draws fog / false sheets for them). Smoke 62/62, no console errors (`out/me/v16/smoke.log`).
  Sent the user `out/me/v16/basilica-check.png` and `out/me/r16/refsolids-161.png`.
- Reasoning I now hold (labelled as mine in `docs/ROUND17.md`, C1..C3): (C1) a second plane with its own flat
  picture needs an invariant line of z^2 + c, so it exists only for real c (the paper says the same: "limited to
  c in R"); (C2) with two exact mirror-symmetric planes the sideways turning round the negative x-axis is 1 + 4k:
  folds (along) or over-wrap (away); kaleidoscope folds tear on y = 0 or lose the slice; (C3) on a Mandelbrot
  solid buds attach along curves (ridges, rings) or patches (fused), and at single points only on the rim of an
  exact angle-true plane. If true: round buds all over cannot come from a smooth rule.
- Round 17 (`docs/ROUND17.md`, workflow task `wwbfe3wtm`, run `wf_e650292f-9e7`): profiles (prefix p_), blends (b_)
  search on the bench (rules in `out/r17/<name>/myrules.py`, loaded by a hook I added to `out/r16/bench/rules.py`);
  prover and hunter test C1..C3. On return: read reports, look at pictures, add any stage-1 passer to the lab,
  tell the user plainly whether the claims held.

## 2026-11-18 21:10 user: "along" is the closest; a PANEL of Julia sets must pass before any Mandelbrot

- User (verbatim): "the turning along approach is the closest we've gotten so far, the basilica looks almost exactly
  as people envision, with bulbs growing between things in a natural way, very nice. The only thing is, for continued
  research, is that maybe you should look at a few julia sets first, like dendrite and basilica, and perhaps a few
  more, and then when they all pass (and then the mandelbrot passes of course) then continue". Memory updated
  (`right-rule-criteria.md`).
- Panel (my pick, 9 sets): basilica, San Marco, airplane, cauliflower (c on the x-axis); rabbit, dendrite, Siegel
  (flat plane, off the axis); rabbit turned 90 and 30 degrees about x (out of the flat plane).
- Lab pictures of `turnalong` and `mercator` on the panel: `out/me/panel/panel-axis.png`, `panel-plane.png`,
  `panel-off.png` (made by `out/me/panel/shots.py`, `sheet.py`; sent to the user). By eye: `along` good on basilica
  and San Marco, a barrel on the cauliflower, specks on the airplane, a LAYERED LUMP on every set off the x-axis
  (rabbit, dendrite, Siegel, both turned rabbits). One plane: clean on A and B (thin tree for the dendrite) but flat;
  a hollow bowl for c out of the plane. Fits C1.
- Round 18 (`docs/ROUND18-PANEL.md`): workflow builds the calibrated panel in `out/r18/panel/` then an independent
  review in `out/r18/review/`. Round 17 (task `wwbfe3wtm`) still running; its searchers gate on basilica + rabbit.
- On return of both: run the panel on every round-17 rule that passed its stage 1; report the table to the user;
  no Mandelbrot solid for a rule until the whole panel passes.

## 2026-11-18 22:25 round 17 collected (no passer; C1..C3 hold, one correction); capfold tried by me (fails)

- Reports: `notes/_r17_reports.json`, text `out/me/r16/reports17.txt` (collector `out/me/r16/collect2.py <run id> <json>`).
  Sub-agents could not write report.md files (harness refuses); everything is in the returned reports.
- profiles (25 members of the reference-plane family + 3 scouts): NO passer. Three corners: gentle crossing = hair
  (closecut 1.1..63.5); sharp crossing (< 1 degree band) = clean skin, passes bench, but it is the tear in disguise
  (two points 0.001 apart land 1.2..2.0 apart) and the rabbit breaks into 400..1300 pieces like two planes; lathe at
  the axis = rings. Sheet: `out/r17/profiles/sheet.png` (user-readable; sent). Tools: `out/r17/profiles/cliff.py`.
- blends (19 rules): NO passer. Averages/great-circle blends: turning count -3, fins on the diagonals. "Pole rules"
  (one exact plane, rational direction maps, 4 or 6 wraps, 0 % folded): clean skin (b_pcd 0.07, b_pcc 0.14) but fused
  lump (J2 fails). Counting rule: buds grow where a direction is sent to -x, arms where sent to +x; liked look
  needs 4 and 2 -> tear, fold, triple winding or extra arms. Tools: `out/r17/blends/count_dirs.py`, `turncount.py`,
  `screen.py`. Formula: with w = (y + iz)/(r + x), every known rule is w -> 2w/(1 - mu |w|^2).
- prover: C1 holds, stronger (no smooth second sheet, flat or curved, off the x-axis). C2 holds, sharper: a
  tear-free rule exact on two mirror planes wraps the direction sphere 0 or 4 times, never 2 (m planes: multiple of
  2m); no creased angle-keeping rule reaches a second exact plane. C3 holds: Mandelbrot buds attach along LINES for
  every smooth rule (two conditions, three unknowns). Stage 1 cannot see the rule inside radius 0.465 (0.347 with
  the rabbit): "two-zone" lever for the Mandelbrot main body. Options that can exist, each dropping one wish:
  ridges on a full body / rings / rows of buds on seams (thin near the rows) / tear / inexact flat cut off the axis.
- hunter: skin calculation from the resting point's derivative works (seconds, no picture): `out/r17/hunter/core.py`,
  `c2.py`. along: 38 % of skin is a period-2 patch, 18 % of volume is smear (never settles). C3's last sentence
  ("only on exact planes") is FALSE as worded: h_ud55 (one-plane near the flat plane, lathe about the upright axis)
  has a period-2 body above and below touching at one point; isolated, with rings; its basilica fails closecut.
  C2 on 32 rules: turning count +1 or -3 only.
- closecut flaws found by the searchers: counts cut-through buds as loose matter; can be fooled by NaN; J6 misses a
  smeared tear (add the cliff at gap 0.001). Not fixed yet.
- MY TRIAL of the prover's proposal C (`out/r17/me/myrules.py`, m_cap15/30/50/80: one-plane answer, steep answers
  folded back by a sphere inversion sending straight-up to straight-back): skin between planes is clean with small
  round bodies (no hair), BUT basilica fails J2, J4, J8: blade and lens bodies, a thin sheet standing on the necks
  (`out/r16/bench/sheets/m_cap15.png`). Reason (mine): the fold sends P's crushed pole direction to -x.
- My reasoning added: F = r^2 D(dir) keeps angles in 3D only where D stretches the direction sphere by exactly 2;
  that cannot hold on a patch of directions (a sphere cannot be doubled onto itself without changing curvature),
  only along curves. So perfectly round buds at every depth need an invariant curve of such directions = a plane.
- Round 18 (panel, task `wmajhtt94`) still running. Next: when it returns, round 19 = search in the class
  "one exact plane + angle-keeping pieces" gated by the panel; tell the user which Mandelbrot wish must give.

## 2026-11-18 23:05 round 18 (panel) collected; round 19 launched

- Reports: `notes/_r18_reports.json`, text `out/me/r16/reports18.txt`. Panel: `out/r18/panel/` (panel.py run/table,
  README, `sheet-for-user.png`); review: `out/r18/review/` (`review-sheet.png`).
- Panel verdicts: NO rule passes; no rule passes ANY set off the x-axis. Sets passed of 9: twoplane 4 (group A),
  along 2 (airplane, cauliflower; basilica and San Marco fail only on hair), p_tt1024 1 (its basilica pass was false:
  dust film at 45 degrees), oneplane 0 (fails only "truly 3D" on A and B; empty on C), lathe 0, away 0.
- Review: the panel is a sound FILTER for gross faults (45 of 45 calibration cells agree with the eye), NOT a
  certificate. (1) hair number fails the flat set itself (flat basilica 1.2..2.0): counts round buds as hair;
  (2) 12 tiles are too few (verdicts near 0.3 are luck); (3) group C at 40 steps is a snapshot of a draining solid
  (along at rabbit30: volume halves every 9 steps; oneplane, twoplane empty). Rabbit turned 30 degrees is outside
  every rule's own bounded region except the lathe's, so "dust" is right there: group C must be redefined.
- Lab vs iteration at rabbit30: the lab ran 40 iterations (my log), but its flat view paints every pixel within a
  pixel of the set (shader lines ~640..660), so fine dust looks filled; in 3D the ray marcher stops on slow-escape
  fog. So my `panel-off.png` sent to the user showed lumps and a bowl where there is NO lasting solid. Told the
  user (correction).
- Round 19 (`docs/ROUND19.md`, workflow task below): foldpost (f_), foldpre (g_), rational (q_) search the class
  "one exact plane + angle-keeping pieces"; panel2 repairs the panel in `out/r19/panel2/`; claimed passers go to
  independent checkers. Bench hook now also loads `out/r19/*/myrules.py`. No Mandelbrot solid in this round.
- Pending with the user: which wish the Mandelbrot solid gives up (rows of buds / full body with ridges / rings).

## 2026-11-19 round 19 collected (no passer, three kinds closed, panel repaired); MY NEW RULE "wind, then square"; round 20 launched

- Reports: `notes/_r19_reports.json`, text `out/me/r16/reports19.txt` (run `wf_e4878a78-e42`). No claim, so no checker ran.
- foldpost (f_): closed. One fold copies every flat direction (arms too); a pleat's copies have stretch
  sqrt(W)(1+W) > 2 off the plane. f_cres10 = one-plane basilica with stubby fingers (fails J4, J8).
- foldpre (g_): closed. Mirror copies are always thinner than the original (stretch > 2); fixed creases cut the
  rabbit. g_pl passes all 8 bench lines, fails closecut by eye (mild), rabbit (lump, 3.16 x volume), dendrite
  (pieces). The "sheet on the necks" is a zero-thickness film in y = 0 (`out/r19/foldpre/neckline.py`).
- rational (q_): closed by a count (4 covers for roundness, half turn allows 2 or 6; 6 = rock or spears).
- panel2 (`out/r19/panel2/`, README): hair number repaired (flat sets 0.000; along 0.81; away 1.24 + film 24 %;
  p_tt1024 film 12 %), 120 tiles a set, "the solid stays", group C = bas_yz, bas_zy, sm_yz, rab_up judged only
  where the orbit of 0 stays. NO rule passes; twoplane now fails San Marco on blades. Two holes left: saw-toothed
  skin not counted; ball -> dome on nudged sets passes "bodies". Pictures: `hair-calibration.png`, `groupc.png`.
- MY REASONING (why everything breaks off the axis): every many-plane rule gives each plane its OWN arithmetic
  (kept planes). C1 forbids a second KEPT sheet for c off the axis. It does not forbid a sheet that is sent INTO
  the flat plane after one step.
- MY NEW RULE (`out/r19/me/myrules.py`: m_w3, m_w3lin, m_w3f, m_w5; tool `out/r19/me/check.py rules|cuts`):
  F = P(T v), T winds the turn round the x-axis by odd k: g(a) = k a - (k-1) sin(2ka)/(2k) (slope 1 at copy
  planes). k = 3: half-planes at 60, 120, 240, 300 degrees are sent into the flat plane. Measured: flat plane
  exact 1e-14, copy plane exact 2e-14, no jump. `out/r19/me/cuts-m_w3.png`: the plane at 60 degrees shows the
  EXACT flat picture for basilica, rabbit, dendrite, Siegel; no lump. Bench stage 1 (basilica): J1..J7 pass
  (18 buds, 12 off the plane, all round), J8 fails (ribs 2.1 %, roundness 0.50 at one size).
  Weak spots: Siegel disc is paper-thin (sheets); thin fins/arcs between planes; walnut ribs.
  Also considered and dropped by reasoning: bicomplex (Tetrabrot) slices = square frames round the body
  (buds become rails along the edges of a diamond cross-section); co-turning c = Mandelbrot solid spun round.
- panel2 full run on m_w3 started by me (background task bhcsuqvjq, log `out/r19/me/logs/panel2-m_w3.log`).
- Round 20 launched (`docs/ROUND20.md`, workflow task `w6b9ukkeu`, run `wf_2595c976-317`): entry (lab entry
  `windsq`, build `dist/r20-entry.html`, no publish), profiles (w_: best g, bands, k = 5), prover (W1..W6),
  check (try to fail m_w3 on panel2). Bench hook now loads `out/r20/*/myrules.py`. No Mandelbrot solid.
- PANEL2 VERDICT ON m_w3 (sinus form), my run, finished: passes 0 of 11 sets (`panel2.py table m_w3`).
  Group A fails only "clean close up", but badly: basilica thin 2.37, film 38 % (along: 0.81, 2 %); the skin
  between the planes is whiskers and dust like "away" (`out/r19/panel2/worst/m_w3-basilica.png`); clean only in
  the upright plane. Rabbit: volume 0.97 x yardstick (no lump) but "no body" (thickest 0.75 x flat), 82 % in one
  piece with no gap (99.97 % with a one-voxel gap), thin layered sheets on the skin. Dendrite: in pieces at 12
  steps (83 %). Siegel: drains (71 %), sheets. Nudged basilica collapses (thickest x 0.31, 0.34); rab_up falls
  apart (39 %). Sent to the user: `out/r19/me/wind-vs-along.png`, `cuts-m_w3.png`.
- MY QUICK LOOK at two other forms (`out/r19/me/myrules.py`, `cuts-m_w3saw.png`, `cuts-m_w3b20.png`):
  m_w3saw (each 60-degree wedge turned whole onto the flat wedge, a tear half way; = Kucera's nearest plane with
  three planes that feed the flat plane): basilica clean (hexagonal middle body, round buds, no spikes); rabbit
  has ROUND ears and clean bodies, a few specks; Siegel disc shattered (triangular holes, facets).
  m_w3b20 (g = a exactly within 20 degrees of each plane, smooth ramp): round rabbit ears, a few thin fins at the
  seams, Siegel disc a feathery six-armed BODY (W6 holds by eye). So the squeeze and the whiskers of the sinus
  form come from its ramp, not from the idea. Round 20 `profiles` is measuring the bands properly.
- ROUND 20 COLLECTED (2026-11-19, `notes/_r20_reports.json`, text `out/me/r16/reports20.txt`). VERSION 17
  PUBLISHED = base17a = base16a + `js/10-approaches.js` with the entry `windsq` "Wind, then square" (sinus form,
  deMax 0, last in the list). The page build is byte-identical to `dist/r20-entry.html`, which passed the smoke
  list (62 + 5 steps, no console errors, `out/r20/entry/smoke.log`). v16 page kept in `out/me/v16/`.
  - entry: lab pictures `out/r20/entry/sheet-for-user.png` (sent to the user), `close.png`. In the lab the
    basilica is like along but bristly; rabbit and Siegel disc are feathery masses, dendrite a dust.
  - check: m_w3 fails 11 of 11 panel2 sets; along fails 9. No line where m_w3 passes and along fails. Truly
    better only in: exact flat picture in three planes for every c, no lump. New fault of the KIND: one step
    off the planes the orbit of 0 never settles (tripling the turn near the axis) and the inside leaks.
    Sheet `out/r20/check/sheet.png`. Seconds-long screens: `out/r20/check/screens.py <rule>`.
  - prover: W1, W3, W4 hold exactly. PARITY: a fold-free rule exact on the flat plane has an EVEN number of
    extra half-planes each side, so two planes (the four-bud look) cannot be had; three is the smallest.
    COUNT: for any winding k >= 2 the bodies between the planes thin with depth without limit (fins cannot be
    removed). k = n (odd power), n + 1 (even). At powers 3+ the solid loses the flat picture's own turn.
  - profiles: 11 forms; none passes; bands make flat-plane sets rounder and wreck the nudged sets; what hurts
    off the planes is ramp steepness. Recommended w_c15 (untouched within 15 degrees, straight ramp of slope
    5); still fails skin (32 to 35 of 35 tiles; along 4 of 35). Sheet `out/r20/profiles/sheet-profiles.png`.
  - WHERE THE SEARCH STANDS: three walls, each checked by a second party (not by a mathematician): C1 (no
    second KEPT plane for c off the x-axis), parity + count (fed planes come in threes and bring fins and
    unrest), uniqueness (only one plane keeps angles). So no single fixed rule passes the Julia panel as
    written. Asked the user which test gives: clean sets for every c (one plane) or buds all round for c on
    the x-axis (along). No Mandelbrot solid judged for windsq.
- (kept for reference) collect with `python out/me/r16/collect2.py wf_2595c976-317 notes/_r20_reports.json full`, look at
  the entry builder's sheet and the checker's sheet, review the src diff, build base17a + page, smoke, publish
  Version 17 with the new entry, tell the user per set.
- 2026-11-19, USER ON VERSION 17: "no it's worse now, the turning along was better. Also, I don't really understand
  the "stretch" step in that approach. but it inspired a question - why not have every tested point have a rotation
  around the plane that c creates?" So `turnalong` stays the reference; `windsq` is judged worse.
  - "Stretch" = the Learn tab's move for entries with no written-out moves (`learnStretchTo` in
    `src/js/65-learn-steps.js`); its words are "the length goes from a to the rule's length, b". Explained in chat
    (the distance from the origin is multiplied by itself). PARKED for the next version: learnStretchTo(F, n)
    should use learnSayStretch when the rule's length is the plain power. src is untouched (== base17a).
  - THE IDEA TESTED (`out/r21/me/cplane.py` -> `plane-follows-c.png`, sent): the rule turned round the x-axis until
    its flat plane holds c, F_c = Rot(a_c) F Rot(-a_c). Mandelbrot solid = the flat set spun round the x-axis
    EXACTLY (0 of 400,000 random c differ, for F = oneplane and for F = along; identical to lathe). Along as it is:
    6,568 differ. Reason: the orbit of 0 lands on c, c lies in its own plane, that plane carries the flat rule.
    Holds for every reading (any plane made from c and the x-axis). Julia sets = the flat-c sets, turned; for c on
    the x-axis the plane is undefined and the set jumps with the side c is nudged from. A partial turn (t * a_c)
    only re-winds the cuts of the fixed-rule solid round the axis.
  - NET WRAPS of the sphere of directions (`out/r21/me/wraps.py`): lathe 0 (50 % turned inside out), oneplane +2,
    away +4 (4 % inside out), along 0 (39 % inside out), m_w3 +6, m_w5 +10. So no gradual change can join along
    and oneplane (a c-aware rule that fades from one to the other needs a jump).
  - Rough blocks of along, m_w3, m_w3saw on basilica, rabbit, Siegel, San Marco (`out/r21/me/sawlook.py` ->
    `saw-look.png`, sent): the cut form m_w3saw has the tidiest basilica and San Marco of the three (smooth balls,
    six buds round), but its rabbit and Siegel disc are a crumpled mass, as bad as the sinus form. My earlier
    "round ears, clean bodies" for m_w3saw came from cuts in its own mirror planes and is WRONG for the solid.
    m_w3saw was never run on panel2.
  - New tool: `cplane.solid(G, 'j'|'m', c, centre, half, w, h, nd, steps)` + `shade_solid`: a rough 3D picture of a
    Julia or Mandelbrot solid for any numpy rule in about 15 s (orbits that have left are dropped each step).
- 2026-11-19, USER (next message, verbatim): "ok, how about following whatever new plane is made during the orbit?"
  = RULES WITH MEMORY: the orbit carries a plane, which starts as the flat page and then follows the orbit.
  - My reasoning (CLAIM S): a recipe that uses nothing but the x-axis, c and the orbit's own points is the same
    from every side of the x-axis, so its Mandelbrot solid is spun; with an exact flat cut it IS the flat set spun.
    Not spun needs something fixed off the x-axis; with memory that is where the carried plane starts.
  - SCOUT (`out/r21/me/follow.py`, quick pictures `follow-julia-quick.png`, `follow-mandel-quick.png`): carried
    sheet through the x-axis, one-plane square about it. fixed = one plane; lag25/50/75 = sheet moves that share
    toward the point's own sheet before squaring; delay = sheet of the point before; first = flat page once, then
    own sheet; own = lathe. All exact on the flat page (0 of 8,000). Seen: the family runs from one plane to the
    lathe; close following = ribs and rings; lag = budless blobs off the page, rabbit a layered lump; delay =
    rabbit and Siegel dust; lag50 tears. No round buds off the page that are not rings.
  - LIBRARY `out/r21/lib/mem.py` (M.Rule(name, label, step, init), M.stay, M.mandel, M.flat_check, M.spun_check,
    M.cut_axis, M.cut_across, M.solid, M.shade_solid, M.julia_sheet, M.mandel_sheet, M.bench(name), M.SCOUT).
    `python out/r21/lib/mem.py` prints the two numbers for the scout's rules.
  - Picture for the user: `out/r21/me/usersheet3.py` -> `out/r21/me/plane-follows-orbit.png`.
  - ROUND 21 LAUNCHED (`docs/ROUND21.md`, workflow task `wln1vwurz`, run `wf_bcebef9b-46d`): searchers sheet,
    alongmem (along with a carried frame), span (planes made by two orbit vectors, not through the x-axis), frame
    (a carried full frame); prover (Claim S, Julia analogue, the once / n times / ring dichotomy); skeptic
    (counterexample to S, break the scout, check the library); then judge (Julia sets against along,
    `out/r21/judge/sheet-for-user.png`) and checker (every claim). Folders `out/r21/<name>/`, NOTES.md each.
    When it returns: read the reports from the task result, look at the judge's sheet, tell the user; a lab entry
    only if something beats along or the user asks.

## 2026-11-19, USER (verbatim, after the plane-follows-orbit sheet): "ok none of these... how does the along approach work?"
Then, after my first answer (slider widget, "reference sheet", "lags / sweeps past", degrees): "I have no idea what
you're saying, you're not explaining it in terms I understand".
Second answer given in plain words: the book whose spine is the x-axis; every rule answers "which page does this
point use?"; Lathe = its own page, One plane = always the flat page, Along = flat or upright page, whichever is
nearer, tilting over gradually; four pages show the flat picture (flat, upright, two diagonals = ties) -> eight buds;
rabbit breaks because its c is off the spine and pushes points out of three of the four pages.
RULE FOR EXPLAINING (also in memory user-judges-by-pictures): the user's own words (plane, rotate, orbit, c, bulbs,
power), no coined terms, no charts of one quantity against another, no measured numbers unless asked.
The wrap-up box question of that turn (written-out Learn steps for along) was passed over. Do not offer it again.

## ROUND 21 RETURNED (workflow wf_bcebef9b-46d, 8 agents, all done). Rules with memory.
Read: out/r21/judge/NOTES.md (ranking, numbers, definitions in full), out/r21/checker/NOTES.md (every claim tried
again; section 10 = what may and may not be told), out/r21/<sheet|alongmem|span|frame|prover|skeptic>/NOTES.md.
Picture for the user (sent): out/r21/judge/sheet-for-user.png (4 rows: along / literal reading / evc / c_wake1).

VERDICT: nothing beats along, nothing passes the user's five tests. About 190 memory rules tried, 187 exact on the page.
ESTABLISHED (checker):
1. Claim S HOLDS. A plane made only from the x-axis, c and the orbit (nothing fixed to start from) gives exactly the
   flat set spun, whatever is remembered. Apparent counterexamples (up to 0.44 % of verdicts) were rounding: with 60
   and 120 decimal digits 75 of 75 return to the spun set. Same for basilica / San Marco / airplane: the lathe's rings.
2. So following needs a fixed start: the flat page. With it: following closely stretches every bud round the x-axis
   by 1/(1 - share) into a rib, then a ring (ring at share 0.9); lagging leaves a blob with no buds and fuses the
   rabbit; one step behind gives dust; on the Mandelbrot solid no setting gives a round ball off the page.
3. Round buds off the page that are not rings occurred only for c on the x-axis: in 4 directions (flat page and the
   page square to it: sheet.ease, sheet.evc005e70k16) or in 8 when along's own formula does the first squaring
   (alongmem.c_wake1, c_wake2, b_keep). Both come from a formula term that fixes the count (sin 2d, sin 4 phi).
4. The rabbit comes apart into bodies only where the squaring page is c's own page to within about one degree.
5. flat_check can pass while the flat picture has no body behind it (a film): lift a flat point a millionth and it is
   lost. Always run the lift test beside flat_check. Kills delay, lags near one half, ease, turn-away, orb_inf_px.
6. Library sound. Limits: M.half reads a sheet within 5e-9 rad of flat/upright as that page; spun_check numbers
   under about 0.5 % are noise for unstable rules; the start-at-c convention matters for first, b_keep, evc.
NEAR MISSES (trades, not wins):
- sheet.evc005e70k16 (eased votes; carried vector w starting (0.05, 0); c votes with weight 16, the point with 1,
  ease 0.7): basilica 4 buds (18.6 / 14.6 deg), rabbit and Siegel clean bodies BUT the rabbit is the one-plane rabbit
  (12.8 % of verdicts differ), the 4 directions die by c = -1 + 0.2i, seam for c just off the axis, loose flakes over
  the skin close up, three hand-set numbers (16 -> 4 fuses the rabbit). Mandelbrot solid = flat set at 0 and 90
  degrees, smooth hearts between.
- alongmem.c_wake1 (squaring number 1 by along, every later one by one-plane): 8 buds on the basilica's middle body
  only, rabbit in smooth separate bodies also off the page BUT two bodies float free (7.2 % each, gap 0.107);
  Mandelbrot solid = the one-plane solid exactly (0 of 200,000 differ).
- Literal readings: span.c_page (plane of the point and c) = the lathe for c on the x-axis, a fan with dust for the
  rabbit; frame.orb_inf_px (plane of the last two orbit points) = rings and ribs, rabbit a ribbed shell that leaks.
NOT TO BE TOLD: that anything beats along; that buds all round without a count of planes are proved impossible for a
rule starting from the flat page (open: prover D4 has a gap); that along is worse at c = -0.75+0.1i (that c is
outside the flat set; along empties as it should, while one-plane keeps a body there with an empty slit at the page:
a fault of ONE-PLANE not seen before, not followed up); anything about fine detail (all rough blocks or cuts).
NEW SIDE FACTS: along has buds on buds round the axis too (budzoom.png); along's Jacobian is negative at 44 % of
points in the cube (earlier figure 39 %); symmetry gives the LEAST repeat of buds, not the count.
REPORTED to the user in plain words with the sheet. Asked (wrap-up box): add the two near misses to the lab?
No lab change made, nothing published (still Version 17).

## 2026-11-19, USER on the round 21 sheet (verbatim):
"yes add them - but what's that last approach? it looks promising. and the first approach you did looks promising
too with features in 3d, but not in the way I hoped with unique bulbs and whatnot. Why is that approach doing smooth
stuff instead of the bulbs in 3d in the basilica? and why is the along approach the best so far? like can't we
examine the dynamics of those orbits, and see what's going on? also I still don't really understand the stretch
step, if we're not doubling the magnitude"
My reading: "add them" = the two near misses as lab entries; "last approach" = row 4 (c_wake1); "first approach" =
row 3 (evc005e70k16), the first of the two; the user thinks Stretch should DOUBLE the length (it squares it).
"unique bulbs" = buds of 3D in their own right, not copies of the flat picture standing in a few planes.

DONE THIS TURN:
- out/r22/me/ring.py -> out/r22/me/one-step-ring.png (sent). 48 test points on the circle x = 0, radius 0.62, c = -1,
  one step. Lathe: all land on one spot on the axis, 48 of 48 stay (ring). One plane: land on a tall line up to 0.384
  off the axis, 2 of 48 stay. Along: land in a small cluster at most 0.179 off the axis, 8 of 48 stay. Plain law:
  a bud is where the point is squared in the page it lies in (it then lands dead centre in the next body).
- Answered in plain words: row 4 = first step along, then one plane (one generation of buds per along step);
  row 3 = only two pages (flat, upright) where a point is in its own page, so four buds and smooth between;
  along best = four such pages at EVERY step; Stretch = length times itself, not doubled (0.5 -> 0.25, 2 -> 4).
- docs/ROUND22.md written. Workflow round22-entries-and-orbits LAUNCHED: task wfi33gu7v, run wf_31c3bb08-a4d.
  Branch A: entry (adds lab entries alongonce "Along once, then one plane" and pulledplane "Pulled plane" with three
  sliders s0 0.05 / ease 0.7 / c's weight 16, plus the Stretch wording fix; builds dist/r22-entry.html) ->
  entrycheck -> one repair pass if needed -> recheck. Branch B: buds, lump, stability, mandel (parallel) -> design
  -> judge (writes out/r22/judge/ANSWERS.md and up to five pictures for the user).
WHEN IT RETURNS: read the result and out/r22/*/NOTES.md; look at the entry check's verdict and at
out/r22/entry/sheet-for-user.png; if it ships: build the page from src (python build.py --page), run the smoke lists
myself once, freeze src as base18a, publish as Version 18 (Artifact publish, same path squaring-lab.html, no
capabilities, no icon), tell the user what the two entries are in plain words. Then report the orbit study with the
judge's pictures, in the user's words (plane, rotate, orbit, c, bulbs, power; the book-and-pages comparison).

## 2026-11-19, later: "you're literally speaking in greek to me"

The user's reply to my answer about the ring picture (tables of counts, "squared in the page it lies in", "lands dead
centre"), verbatim: "you're literally speaking in greek to me". Second time in one day. Plainer words were not enough.

What I did instead: a toy shown inline in the chat (not in the lab). 48 test dots in a ring round the middle blob of
the c = -1 flat picture (ring at x = 0, radius 0.62), four buttons (Lathe, One plane, Along, Along once then one
plane), Hop once / Play / Start over, and a slider that turns the view. Dots that go further than 2 from the centre
fade out; a circle stays at each starting place whose dot is still there. Counts, checked in Python
(out/r22/me/hoopnum.py, formulas agree with the library to 4e-16) and in the page itself: Lathe 48 of 48, One plane 2
(last one leaves at hop 14), Along 8 (hop 10), Along once then one plane 8 (hop 19). Test page:
scratchpad preview/hop-toy-test.html (query ?rule=..&hops=..&view=.. for still pictures); pictures out/r22/me/toy-sheet.png.

RULE FOR EXPLAINING, tightened: something to press and watch first; then a few numbered plain lines so they can name
the first one that loses them; no tables of counts; no comparison stacked on a comparison ("page" is dropped: say
"the flat picture" and "off the flat picture"); words: dot, hop, recipe, blob (big body), bulb (small one), survive.
Not yet known whether the toy lands. If it does, an orbit tool inside the lab is the natural next thing they may ask
for; do not offer it unasked.

Round 22 workflow (task wfi33gu7v) still running at this point; lab still Version 17.

## ROUND 22 RETURNED (2026-11-19, workflow wf_31c3bb08-a4d, 10 agents)

### A. The two entries (src/, six files differ from base17a: js/10-approaches, 30-shaders, 60-measure, 65-learn-steps, 66-learn-view, 90-boot)
- `alongonce` "Along once, then one plane" and `pulledplane` "Pulled plane" (three dials: 0.05, 0.7, 16). Carried state
  per orbit lives in GLSL behind `#ifdef APR_CARRY` (carStart / gCarI / carStep / carFit); JS twin `CARRY[id]`.
  `MATH[id](v, n, q, c)` now takes c for pulledplane only. Both entries `deMax: 0` (Rough).
- First check: "fix first" (7 defects, 2 major: stale card after "Jump to a point"; shards for a c out of the flat
  plane not said). Repair pass: all 7 cured (the second by text only). Second check: all 7 gone, 3 minor text defects
  in Pulled plane. I FIXED THOSE THREE MYSELF plus three sentences of Along once that the judge's measurements overtook:
  PP_ROUGH (thread example dropped), PP_ABOUT (thread = the flat picture of the same c stood upright; "no bud is
  left" instead of "nothing is left"), PP_HELP_EASE (8 % at the lab's settings, 28 % with the third dial at 1),
  AO_TAG / AO_ABOUT (side bodies keep 6 buds of along's 16, 2 small buds per bud instead of 16; Mandelbrot solid very
  nearly one plane's: 4 to 8 of 2,000,000 differ). Sheet caption "the other bodies are smooth" -> "keep only a few".
- Checked by both checkers: parity with the library 0 differences (orbits and shader slices), five untouched entries
  pixel-identical to base17a, smoke 90 of 90.
- KNOWN, SAID IN THE TEXTS, NOT CURED: for a c out of the flat plane both entries (and "Sphere inversions, one plane",
  whose texts do NOT say so) draw shards / a slab where next to nothing stays. Along once's Mandelbrot picture has
  thin curved wings with no thickness.
- Stretch wording now everywhere: "Squared means multiplied by itself, not doubled: 3 would become 9, not 6."
- Learn tab follows the entry's own orbit for the two carrying entries.

### B. What the orbits do (out/r22/judge/ANSWERS.md: Q1 to Q4, "may be told / may NOT be told"; five pictures there)
- Every orbit that stays ends on the flat picture's own spots, for every rule and c looked at. Nothing else hides
  off the flat picture.
- Along: 8 buds round the middle body, 16 round the bodies beside it, and each big bud carries 16 small buds all
  round its own stalk (one plane and along once: 2). 14 of the 16 are in none of along's four planes: buds of 3D.
- The rabbit's lump = the same bodies as one plane's, grown fat and pressed wall to wall. Cause: above the point
  where three bodies meet, one plane pushes a lifted point away at every height; along pulls it back down.
- Along once: all 8 big buds of the middle body; 6 instead of 16 on the side bodies (all near the flat picture);
  2 small buds per bud; two loose bodies on the rabbit; Mandelbrot solid one plane's to a few parts in a million.
- Six new rules tried (design section), none beats along. "New try 1" (along with the book's spine through the point
  where the big bodies meet): = along for c on the x-axis; rabbit comes apart again, but ridges and thin arcs
  instead of buds (its planes last one step only). Not a candidate.
- Next idea, NOT tried: planes that come back after as many steps as the flat picture has spots to hop round
  (3 for the rabbit). Open: getting the number of planes out of the power.
- MAY NOT BE TOLD: see ANSWERS.md. Among them: my one-step-ring.png says "inside the left-hand body"; the ring lands
  in the small body at the far left (x = -1.384; the left body ends at -1.382). The toy says only "the same spot".

### C. The judge's pictures are written in the "page" vocabulary. After "greek", send at most the lab sheet
(out/r22/entry/sheet-for-user.png, real lab pictures) and one or two of the judge's, with a one-line key.

### D. PUBLISHED: Version 18 = base18a (2026-11-19 17:31)
- base18a = copy of src/ after my five text lines; `python build.py` -> squaring-lab.html, byte-identical (wrapped) to
  dist/r22-entry.html. Against the build the second checker passed (dist/r22-entrycheck2.html) exactly 5 lines differ,
  all text constants in js/10-approaches.js.
- Smoke by me, third run: 90 of 90 steps, exit 0, no console errors (out/r22/entry/smoke-all.log, out/r22/me/smoke-v18.out).
  The first two runs died on tools/shot.py's 120 s socket timeout: for about 20 minutes (17:00 to 17:23) the machine
  drew about 15 times slower than usual (first picture 25 s instead of 1.5 s; base17a just as slow; Intel Arc GPU,
  nothing else using it, CPU not throttled; cause not found, it went away by itself). If a smoke run times out again,
  time dist/r22-base17a.html with out/r22/me/probe-steps.json before suspecting the page.
- Artifact: same URL, Version 18, version id 1795134628-a346, capabilities carried forward.
- Sent to the user: out/r22/entry/sheet-for-user.png, out/r22/judge/2-buds-on-a-bud.png, 3-rabbit-same-bodies.png.
- Box question left open: try the untried idea (planes that come back after as many hops as the flat picture has
  spots to hop round; 3 for the rabbit). DO NOT start it without a yes. The toy question ("did it make it clearer")
  is still unanswered too.

## 2026-11-19 evening: the user wants two planes and along "ironed out"; toy rebuilt; round 23 launched

- User, verbatim, in `docs/ROUND23.md` section 1. In short: the toy does not show the movements ("each step in the
  hop"); "the original sphere inversion 2-plane and along approaches have the best results, but in different things";
  wants blown-up bodies with bulbs "everywhere in the same pattern, like the 2d spacing being done in 3d", guesses
  quaternion rotations; other people's 3D rabbits are "un-rabbity"; along-once is "the closest ... but it's still
  wrong and the approach seems arbitrarily wrong too". Memories updated (right-rule-criteria, user-judges-by-pictures).
- Toy 2 shown inline: every hop is three separate moves (Turn, Stretch, Slide), "Next move" steps through them,
  trails, the dashed circle "distance 1 from the centre", rules Lathe / One plane / Two planes / Along. Counts
  checked in the page: 48, 2, 4, 8 of 48 after 24 hops (out/r23/me/hoop2.py, toy2shots.py, toy2-sheet.png; test page
  scratchpad preview/hop2-test.html?rule=..&moves=..&view=..).
- What I reread: the "same spacing everywhere" idea WAS tried: round 15 "Square pillow" (lab group "Doubling on a
  pillow grid"): spindle for c = -1, decent rabbit. Round 17's counting law and "pole rules" cover the "extra arms"
  kind. So three of the user's hopes were each tried once, under names they may not connect with their words.
- My reasoning this evening (docs/ROUND23.md section 2, a to f): the HINGE. Two planes, along, away, winding, lathe
  all hinge on the x-axis; z^2 does not (turn by a -> square turns by 2a; one plane obeys it). Hinged rules are good
  for c on the x-axis and bad off it; a hinge-free rule without a crushed cone or a tear has no buds off the flat
  plane. Shape-keeping off the flat plane is possible on the 60-degree cones (cos = 1/2: the flat plane rolled up so
  that z and -z touch), laid once round onto the flat plane.
- My scout of that ("cone rule", out/r23/me/cone.py): R_t(w) = (w^3 + t)/(w(1 + t w^3)), t = tan 15, blended into
  w^2 beside the equator. Flat check 0 of 20,000; covers 4 times; 1.8 % folded in the blend. Pictures:
  cone-cuts.png, cone-solids-basilica-rabbit-a.png (and -top when it finishes). c = -1: a dome (t > 0) or a lump
  (t < 0). Rabbit: a lump (t > 0); for t < 0 the rabbit's layout is kept and bodies stand all round it, off the flat
  plane too, but rough and spiky. Sent to the user relabelled: out/r23/me/first-test-for-user.png. NOT a win.
- Round 23 (docs/ROUND23.md): workflow task wi637hqye, run wf_e65a6727-7bf. Sections outside1 (the fractal
  community's power-2 formulas, from quoted sources), outside2 (the mathematics literature; verdicts on my a to f),
  cone, rabbit (every kind of rule on off-axis shapes; "along for the first N steps"), then design, then judge
  (out/r23/judge/ANSWERS.md). No lab work in this round. Lab still Version 18.
- WHEN IT RETURNS: read the judge's answers and wrong_claims first; look at its sheet; tell the user in a few plain
  lines with at most three pictures of real shapes; if a rule is worth a lab entry, that is the next round's job.

## 2026-11-19 late evening: ROUND 23 RETURNED; user steers to the second version; my scouts (out/r24/me/)

- Round 23 result (task wi637hqye, 6 agents, all done): `out/r23/judge/ANSWERS.md` (read it first), pictures
  `out/r23/judge/1-shapes.png`, `2-what-others-found.png`, `3-one-step-against-every-step.png`. In short: the way of
  two planes and along (second planes through the x-axis) cannot reach the rabbit, and that is a proof; 17 outside
  formulas pinned down, none does it (Msltoe = the two-planes look, Eiffie = the along look, both worse off the x-axis);
  the best new try ("welded cones", `out/r23/cone/best.py`, `out/r23/design/rules.py` names cones / cones1) gives smooth
  round extra bodies when used for the FIRST step only and a crust at every step. May / may not be told: in ANSWERS.md.
- USER (verbatim, about `out/r23/me/first-test-for-user.png`): "the second new try seems better than the first, since
  the first seems assymetrical strangely. Idk why - but anyways, keep investigating, since yes the rabbit structure is
  much better in the second one". And, mid-turn, about the lab entry Pulled plane: "seems to be intuitive but it's too
  simplistic, like there's no 3d bulbs or patterns between the ones that seem to be mirrored on either plane - but
  looking at the mandelbrot, the inflation of the insides of the fractal seem better. but then strangely, why the rabbit
  doesn't have the mirrored bulbs on the vertical plane beats me, so it's still not perfect". Memory updated.
- MEASURED BY ME (`out/r24/me/dirs.py`, `push.py`):
  - First version (dial +0.268): on directions alone it has three favourite directions (+x fixed, 120 <-> 240) that
    pull every direction in (all 20,000 random directions end there). Second version (dial -0.268): none; neighbours
    are pulled apart by 1.83 per step on average. At dial -0.5 the pull-apart is exactly 2 everywhere (1.98..2.00).
  - THE PUSH (new, the reason for the user's observation): lift a flat direction by 15 degrees; latitude of its square
    over the lift = 1.93 all round for one plane; first version 1.02 at 0/120/240 and 3.53 at 60/180/300; second
    version the other way round. Push times distance from 0 at a meeting point (above 1 = a lifted point runs away,
    below = held): c = -1 (meeting points on the x-axis, 180 degrees): first 2.18, second 0.63; rabbit (meeting point
    at 119.9 degrees): first 0.57, second 1.96. So each version is good exactly where its strong side faces the
    meeting point. A meeting point of a p/q bulb sits at about 360 p/q degrees.
- THE FAMILY (found in my own notes): R_t with t = -1/2 is w -> (2w^3 - 1)/(w(2 - w^3)), the angle-true form of the
  TRIANGLE PILLOW of the very first prototype round (`notes/_pillow_lab.json`, lab group 'tried', entry `pillow`;
  its referee wrote that formula down and proved that only the (3,3,3) pillow carries exact doubling on a mirror
  circle). So: dial 0 = one plane, dial -0.268 = the user's second version, dial -0.5 = the triangle pillow.
- SCOUTS (`out/r24/me/`): `tri.py` (the dial range blended, and the -0.5 end done exactly with a "kite" layout:
  flat check 0 of 20,000, covers 4, no fold, but squeeze median 5.7), `sweep-cuts.png`: for EVERY negative dial the
  upright cut of c = -1 is one fused lump; the rabbit keeps a clean body with small bodies above and below; the Siegel
  disc is shattered. `conefold.py` ("two planes with the second plane bent into a cone" = round 23's fold30 and
  variants, never drawn before): `conefold-cuts.png`: fused lumps for c = -1 and c = -0.75, shards over the rabbit.
  Reason (reasoned): a fold in latitude smears every body along an arc between the flat plane and its cone copy;
  two planes gets away with it only because bodies on the x-axis are already round about the x-axis. DROPPED.
  `solids2.py` -> `raw-vs-blend-a.png` (running): with and without the blend, to see whose the roughness is.
- MY REASONING ABOUT THE CRUST (to be attacked): a body k levels down the tree passes k times through the zone off
  the flat plane; if the rule squeezes there, the squeezes multiply (round 23 measured: one step smooth, two steps
  3 to 1, three steps blades, every step crust). Only a direction map with the same spacing everywhere (dial -0.5 in
  its own flat geometry) does not compound, and its flat geometry cannot be laid on the round ball without three
  corners, which is where the old pillows got their spikes.
- `raw-vs-blend-a.png` (seen): with NO blend c = -1 is a SMOOTH lump (dial -0.27: a few knobs; -0.5: a smooth egg),
  the blended second version is spiky, `tri` is ribbed all over. Unblended rules have no rabbit (their flat picture
  is another set). So the roughness comes with the squeeze, not with the copies; one picture, not a proof.
- THE LEAD (`mfold.py`, `mfold-cuts.png`): lay the extra copy round an EVEN number of times,
  R(w) = (w^m + t)/(w^(m-2)(1 + t w^m)), m = 4 or 6, t < 0, blended as before. Doubling on the flat circle for every m;
  R(-w) = R(w) for even m, so NOT lopsided (seen in cuts); flat check 0 of 20,000 for all seven settings. Push times
  distance at lifts 8/15/25: m4 t-0.10: c=-1 1.38/1.63/1.77, rabbit 1.03/0.88/0.69; m6 t-0.10: c=-1 1.49/2.06/1.66,
  rabbit 1.33/1.84/1.49 (the only setting so far that keeps BOTH apart; weak at 30, 90, 150, ... so the 1/4 bulb is
  at risk). Cuts: m4 c=-1 = a symmetric row of separate bodies with thin horns at four corners; rabbit a body with
  four arms and spikes; m6 = lens-shaped bodies with thin whiskers. In the round: NOT known yet
  (`mfold-solids-a.png` is rendering, background task bnnvyh542).
- ROUND 24 LAUNCHED (`docs/ROUND24.md`): workflow task w2abjbh1z, run wf_083f1c26-565. Sections `twice` (the copy
  laid round 2 or 4 times: solids on 7 c, what the horns are, welded form, lopsidedness as a number), `push` (test
  the push law on ten c; which c each pattern spoils; the evenest push that still has copies; pattern facing the
  meeting point), `rough` (bodies by depth, flakes followed step by step), then `design`, then `judge`
  (`out/r24/judge/ANSWERS.md`). No lab work in it.
- WHEN IT RETURNS: judge's answers and wrong_claims first; look at the sheets; tell the user in a few plain numbered
  lines with at most three pictures of real shapes. If a rule is worth a lab entry: next round (build, independent
  check, smoke, freeze base19a, publish Version 19). Open box question to the user: add the second version to the
  lab with its dial now, or wait for the round's best. Do NOT add anything to the lab without their yes.
- Still parked, not started: planes that come back after 3 hops for the rabbit (round 22's untried idea).

## 2026-11-19 night: the user rejects the cone family; round 24 STOPPED; round 25 (fresh eyes) launched

- `mfold-solids-a.png` (seen, sent to the user): copy laid round 2 or 4 times = even on both sides (not lopsided),
  c = -1 a star of spindle bodies with hair, the rabbit a rough lump. Not it.
- USER (verbatim): "none of these new tries are working. we're looking for an inflated version of the 2d (so
  spherical inversions have to be involved somehow) but the bulbs occur all over those 3d surfaces naturally, not
  chosen. and quaterions I imagine have to be involved somehow, if not fully, so the resulting object is not
  stretched or otherwise revealing the limitations of 3d rotations". Memory right-rule-criteria updated.
- I STOPPED round 24 (task w2abjbh1z, run wf_083f1c26-565) because it studied the rejected tries. Partial scripts
  and logs remain in `out/r24/twice`, `push`, `rough`; no NOTES.md, no judge. Its brief `docs/ROUND24.md` stays.
- My two "nothing chosen" scouts after the message (`out/r25/me/natural.py`, `natural-cuts.png`):
  `fit` = the chain of sphere inversions fitted to z^2 at every flat point (Ahlfors-Weill), worked out with
  quaternions: square(z0, t) = (z0^2 (4r^2 - 3t^2)/(4r^2 + t^2), height 8tr^3/(4r^2 + t^2)). Flat check 0. Endless
  pillars above and below every body. `mid s` = quaternion slerp between the one-plane square and the quaternion
  square: flat check 0; upright cut of c = -1 empty at s = 0.25 and 0.75, a fused lump at 0.5; rabbit crescents
  with shards. Both dropped. (`natural.py check` stops after `fit` on a wrong call of M.stay: needs cx, cy, cz.)
- THE WALL as I now state it (`docs/ROUND25.md` section 3): (W-a) theorem: exact flat picture + every direction
  round the upright axis treated alike => off the flat picture only nothing / fold (smear) / crushed circle (rings,
  pillars) / tear; (W-b) theorem: a second plane with a true copy only for c on the x-axis; (W-c) 3D rotations
  cannot be doubled consistently, hence the quaternion square spins; (W-d) even doubling on a ball needs 3 or 4
  corners; (W-e) the push; (W-f) squeeze multiplies. Open doors: (i) the rule looks at c or carries state,
  (ii) not "length squared times a map of directions", (iii) not an iterated 3D map (limit sets, inverse branches),
  (iv) 4D with another way down. Found while thinking, worth remembering: 3D sphere inversions ARE quaternion
  arithmetic (Vahlen: v -> (av + b)(cv + d)^-1 on v = x + yi + zj), so the user's two ingredients are one thing.
- ROUND 25 LAUNCHED: workflow task wklbwh3d0, run wf_3d14ce50-5c2. Eight independent starts (`vahlen`, `klein`,
  `torus`, `fromc`, `inverse`, `pillow`, `fourd`, `wall` = find the hole in the wall), each must build and draw;
  then `judge` (`out/r25/judge/ANSWERS.md`, fields found_it, nearest, wall_answer, next, wrong_claims).
- TOLD THE USER (plainly): these tries fail; the wall in three lines; the paper's author is stuck at the same place
  (real c only); the broad search is running. Box question: if it cannot all be had, which may bend.
- WHEN ROUND 25 RETURNS: judge first (found_it, wrong_claims), open its pictures, then a few plain numbered lines
  with at most three pictures. No lab work without the user's yes. Lab is still Version 18.

## 2026-11-19 late night: the user asks for "a whole shape" in Learn; ROUND 25 RETURNED (not found); round 26 (build) launched

### A. The user (verbatim, two messages, both after my "the wall" message; neither answers the box question)
- "and also, for the learn tab, I should be able to see how a circle turns into the mandelbrot (or a set of whatevers,
  if it's not a circle), not just a point or selection of points - and this should be extended into the 3d one too,
  where I can see how a transparent shaded ball or something turns into whatever it does after each step"
- "oh and it would be nice to have a julia option too for the learn tab, instead of the mandelbrot shape I mentioned
  earlier, so I can see the difference"

### B. Round 26 = the build of that (docs/ROUND26.md is the brief; workflow task wqjxdf815, run wf_6029e430-8d3)
- My reading: "the circle turns into the Mandelbrot" is true only as "what is left": every point of the big circle
  (radius 2) takes steps, a point that lands outside is thrown out, shape k = what is left after k steps. Mandelbrot
  shape = every point its own c, dot starts at 0; Julia shape = one c, every point a start; "Both" side by side with
  the diamond c. 2D: flat rule. 3D: the chosen approach's own GLSL, drawn as see-through shaded skins (ghost of the
  shape before, the bite lit up between steps). Follow = One point (old Learn, default) | A whole shape.
- Files: new src/js/67-learn-shape.js, src/css/67-learn-shape.css, src/js/68-learn-shape3d.js; small edits in
  66-learn-view.js; 90-boot.js has one new line of mine (learnShape3d on window.squaringLab). src was == base18a
  before that line.
- Agents: build core + build three (parallel), join, check arithmetic + check eyes, fix, final (out/r26/<part>/).
- NOT in this cut, to offer after it is published: a second picture "where those points are now" with the moves of
  a step (turn, stretch, add c) played on all of them (the user's "I don't see the movements").
- WHEN IT RETURNS: read final.verdict, defects_left, smoke; open final.user_pictures and the page myself
  (dist/r26-final.html; preview server or tools/shot.py); diff src against base18a; if good: copy src to base19a,
  `python build.py`, publish as Version 19 (Artifact, same file squaring-lab.html, same URL), send at most three
  strips, tell the user in plain lines what it shows (eaten away, not bent), then put the "where the points are
  now" question in the box.

### C. ROUND 25 RETURNED (workflow wf_3d14ce50-5c2, 9 agents): found_it = false
- Judge: out/r25/judge/ANSWERS.md (answers 1 to 4, may / may NOT be told), pictures 1-c-minus-1.png, 2-rabbit.png,
  3-bulbs-all-over.png (real shapes, plain captions; all three sent to the user).
- Some forty rules and objects from eight starts; fourteen new rules keep the flat picture exact; none gives clean
  round bodies off the flat picture for both c = -1 and the rabbit.
- The one thing with the whole look: the "pearl tree" (section klein): a chain of exact balls, each carrying smaller
  balls all over in the same pattern, sphere inversions and whole-number shifts only, not lopsided. It has no c and
  no power, its flat cut is a chain of circles (about 39 % of the true c = -1 area wrong at best fit), and it can
  never be a rabbit (three balls cannot meet in one point). The paper's own three-cap rule is far worse on the flat
  cut (49 % wrong for c = -1, 62 % rabbit).
- Nearest with the flat picture exact: for c = -1 the "skew pillow" (section pillow: smaller bodies off the flat
  picture by themselves, but eggs 2:1, thorns, about a thousand crumbs, one-sided, and it has a handedness: the
  mirror-image rabbit is one lump 4 times the size); for the rabbit "twin_tri" (section fromc: one plane with a
  scratched skin, flakes, a tear). Power 3 at c = i with even spacing (section wall): bodies in many directions but
  long, thorny, and not the same after a third of a turn. NOT a lead (judge).
- Quaternions: a quaternion carried along the orbit (three sections, independently) = the quaternion square (rings)
  for c on the x-axis and leaves nothing off the flat picture for the rabbit. The only roll-free quaternion square
  that is exact, "holo" = (x^2 - y^2, 2xy, 2 z |v|), is one plane pressed into lenses.
- Doughnuts: nothing (proof: a body alike above and below with a doughnut skin cannot have the round disc as its
  flat cut). 4D: spinor rule = rings / nothing; product of two flat pictures, cone cut = ridged bodies.
- The wall: stands for z^2 + c; nobody through, no proof that nobody can. Corrections to my briefing: (W-a) needs
  "length squared times a direction map" (or "c = 0 gives the plain ball"); a rule may also send points to infinity
  (shells). "The triangle rule fuses c = -1 by its nature" is WRONG: turned to face the meeting point it comes
  apart. (W-e) uneven push is a symptom, not the cause. Martin 2004 (read second hand only): rules that keep each
  side of the flat plane to itself must squeeze without bound; it does not cover rules that fold space onto the
  flat plane. That is the one honest open question.
- Judge's "next": no more rules of these kinds. Ask the user, with picture 3: is a clearly labelled cousin of the
  flat picture (the balls-on-balls object) acceptable as its own lab entry, or is the exact flat cut not negotiable?
  I PUT THAT QUESTION IN THE BOX this turn. No lab entry without their yes.
- MAY NOT BE TOLD: power 3 at c = i as "clean" or "a lead"; that any new rule "works for c = -1"; "impossible";
  that Martin's theorem settles it; that the pearl tree is a 3D basilica; internal names, angles, percentages as
  explanations.

## 2026-11-20: the user says "yes add it"; ROUND 27 launched (entry + bridge); two recipe pictures sent

A. The user's message, verbatim: "yes add it - how is it generated? if it's sphere inversions and quaternion arithmetic,
   then it seems like we're pretty close to something here"

B. Round 27. Brief: docs/ROUND27.md. Workflow task w8aqsm4oz, run wf_ecb1cdeb-fe3 (script
   round27-balls-entry-and-bridge-wf_ecb1cdeb-fe3.js in the session's workflows/scripts folder). Two tracks in parallel:
   - Track A "entry": builder -> two checkers (arithmetic, eyes) -> fixer if defects -> final. The object goes into the
     lab under the Kleinian kind of picture as a SECOND GROUP named "Balls on balls", with its own scene program, three
     dials (Size of the neighbours = t, Whole numbers = square / honeycomb / line, Depth of the search), one note, a row
     in the Approach list that is NOT an element of APPROACHES, and a twin window.squaringLab.ballsInside.
     IT IS BUILT AS AN OVERLAY, NOT IN src/: files in out/r27/entry/overlay/ (same relative paths as src/), build command
     in out/r27/entry/BUILD.txt (python build.py --name ... --base base18a --swap slot=file ...). Reason: round 26 builds
     its pages from src/ as it stands. Round 26 owns js/65, 66, 67, 68 and css/67; js/90-boot.js is shared (add lines only).
   - Track B "bridge": three explorers + judge -> out/r27/judge/ANSWERS.md.
     B1 measure: how far is the flat cut from the true flat pictures, is another c nearer (c = -0.75 kisses), is there a
     dial like c (the sideways slide), what is nearest to a rabbit.
     B2 respace: carry the whole object over so the flat cut is exact for c = -1; do the off-plane bulbs stay round?
     B3 pinch: swap slides (kiss) for stretches about a point (pinch); chains of sphere inversions fitted to z^2 + c.

C. Sent to the user this turn: out/r27/me/recipe-1-the-recipe.png (six panels: walls and balls, slide, flip, repeat ->
   inside, another point -> outside, every point) and out/r27/me/recipe-2-what-comes-out.png (flat cut, true c = -1 flat
   picture, close-up kiss against pinch, the solid). Script out/r27/me/recipe_strip.py.
   What I told them: the recipe (slide to the nearest whole number, flip through the ball, repeat; one last flip bends
   the walls into balls; in 3D the slide goes in two directions); in quaternion words "subtract the nearest whole
   number, take one over"; the three differences from z^2 + c (kiss / pinch; fractions / halvings; moves that can be
   undone / squaring cannot); "close in the look, not yet close to c"; the three tests now running.

D. WHEN THINGS RETURN
   - Round 26 (task wqjxdf815, Learn "A whole shape"): as written in the section before this one. Publish as soon as it
     passes (Version 19, or 20 if the entry went first).
   - Round 27 entry: read final.verdict, defects_left, merge_notes. Look at the page myself (tools/shot.py). If round 26
     is NOT merged yet, it can be published on its own from the frozen copy:
     python build.py --page --base base18a --swap <the pairs from BUILD.txt>   (writes squaring-lab.html), then copy
     base18a + overlay to a new frozen base. If round 26 IS merged: copy the overlay files over src/ (they are disjoint
     from round 26's files except js/90-boot.js: merge by hand), plain python build.py, full smoke, publish.
     After both are in: check Learn in the Kleinian view with the new group (does not crash, says what it said before).
   - Round 27 bridge: read out/r27/judge/ANSWERS.md and its pictures; tell the user in their words, pictures first;
     respect "May NOT be told". If the judge names a lead, say so and follow it; if not, say so plainly.

## 2026-11-20, later: ROUND 26 returned "ready"; VERSION 19 PUBLISHED (Learn: "A whole shape")

A. Round 26 (task wqjxdf815) finished: verdict ready, old smoke 90 of 90, no console errors, One point pixel-identical
   to Version 18. I looked at the page myself (out/r26/me/*.png, action list out/r26/me/look.json): fine.
B. Frozen: base19a = src as published (base18a + css/67-learn-shape.css, js/67-learn-shape.js, js/68-learn-shape3d.js,
   7 added lines in js/66-learn-view.js, 3 in js/90-boot.js). python build.py -> squaring-lab.html; dist/preview.html is
   byte for byte dist/r26-final.html. Published to the same URL as VERSION 19 (version id 1795181401-fc40).
C. Sent to the user: out/r26/final/user-a-circle-to-mandelbrot-2d.png, user-c-both-rabbit-2d.png, user-d-julia-ball-3d.png.
   (user-b, the 3D Mandelbrot ball, is weak at step 16: a pale straight-edged highlight across the top. Not sent.)
D. Left-overs of round 26 (out/r26/final/NOTES.md, "defects_left"): the second half of a play stands still under "The
   bites are now too fine to see at this size. Zoom in."; 3D bodies are solid, not glass, from about step 8; the pale
   highlight patch on the 3D Mandelbrot shape at late steps in the opening view; nothing zooms by itself at step 16;
   phone: "Unpin picture" over a corner in Both; the grey ghost still drawn when a 3D shape has just gone; one sentence
   ("Step 1: every point that is still here takes one more step" at a Julia shape's first step). No polish unless asked.
E. Offered, not built: cut 2 of the whole shape = "where those points are now" (the shape itself moved by each step).
F. ROUND 27 (task w8aqsm4oz) STILL RUNNING. Its entry is an overlay on base18a. Round 26 IS merged now, so when it
   returns: copy the overlay files over src/ (merge js/90-boot.js by hand: overlay copy started from src's, adds lines),
   plain python build.py, full smoke (out/r22/entry/smoke-all-steps.json) + round 27's own checks + a look at Learn's
   whole shape, freeze as base20a, publish as Version 20.

## 2026-11-20, later still: ROUND 27 returned; VERSION 20 PUBLISHED ("Balls on balls" is in the lab); the hunch tested

A. ENTRY (Track A). Final verdict "not ready" by the strict rule only: three MINOR left-overs, all at the 100 end of the
   dial "Size of the neighbours" (stray stops of single rays; far balls and kisses swollen where the depth runs out;
   the ray's step can be up to 2 px long near a skin). Everything else clean. I accepted them and published.
   Merge: overlay copied over src/ (src equalled base18a in the ten other slots; 90-boot.js = src's + 3 lines).
   dist/preview.html is byte for byte the final agent's rehearsal page dist/r27-final-merge.html (old smoke 90 of 90,
   six old states 0 pixels, Learn works with both Kleinian groups). My own re-runs on the merged page, all exit 0 and
   "no console errors" (out/r27/me/v20-checks.out): verd.py (twin and shader against tree.py: 0 of 80000 and 0 of
   40644), eyes.py wide + phone, shape.py, round 26's use.js, spot.js, phone.js. Looked myself in the light theme
   (out/r27/me/v20-*.png). Frozen: base20a = src. VERSION 20, version id 1795189459-3e70.
   Where it is: Approach list, bottom, heading "A cousin, not a rule", row "Balls on balls"; or Show: Kleinian, then
   Group: Balls on balls. Dials: Size of the neighbours (55.56 = t 1.4), Whole numbers (square / honeycomb / line),
   Depth of the search (16). Twin on the handle: window.squaringLab.ballsInside(x, y, z, { t, grid, rounds }).
   Overlay files: js/32-balls.js (new), css/86-balls.css (new), body.html, js/00-core, 25-colour, 40-render, 46-mesh,
   50-camera, 75-presets, 80-ui, 90-boot.
B. BRIDGE (Track B). Judge: out/r27/judge/ANSWERS.md. found_it = false, LEAD = NONE.
   - measure: same layout as c = -1, about 39 of 100 parts of the true area wrong; nearest true flat picture is
     c = -0.84 (one part in six wrong); buds at fractions, true buds at halvings; no dial acts like c; no rabbit.
     Correction to what I told the user before: true pictures can kiss too (c = -0.75), so "kiss against pinch" is not
     the sign by itself; exact balls and fractions are.
   - respace (bulbs carried onto the true flat picture, re-spacing fractions to halvings along each rim): flat cut exact
     for c = -1 AND the rabbit, biggest bulbs stay round, same above and below; but needles and upright walls at every
     point where a bud is attached, worse the finer one looks, and the bulbs are stamped on, not made by the squaring.
   - pinch: PROVED that in an object made the way Balls on balls is made, kisses cannot be swapped for pinches. One-way
     fitted moves: bare chain, no buds. Nearest clean thing: every body a lemon, buds only round the flat picture.
   - Judge's only suggestion: ASK the user whether the carried-over object (picture 2) deserves its own labelled entry,
     knowing its needles. Do not build it unasked.
   - I also thought through "matings" (Bullett-Penrose; Schwarz reflections: circle + cardioid = half inversions, half
     squaring, with a c, in the FLAT plane). In 3D their squaring half is the same old problem (it is the 3D square
     outside the unit ball), so no new round on it. Round 25 klein NOTES (line 178) had said the same.
   - May NOT be told: that we are close; that the carried-over object "works" or is a 3D c = -1 / rabbit; that the
     lemons are a find; that a dial is like c; that the user's object is impossible; un-re-measured numbers; internal
     names.
C. Sent to the user: out/r27/final/user-2-end-on.png, out/r27/judge/1-how-close.png, 2-carried-over.png, 3-pinched.png.
D. OPEN QUESTIONS TO THE USER: (1) wrap-up box: add the carried-over object (picture 2) as its own entry? (2) from the
   turn before, not answered: a second view in Learn, "where the points have got to after each step".
E. NOTHING IS RUNNING. No candidate rule in hand. src == base20a.

## 2026-11-20, evening: user reaction to Version 20; ROUND 28 LAUNCHED (workflow task wildzkx6n, run wf_88239966-31e)

A. User (verbatim): "Whoa!! The balls on balls approach is amazing, keep it in all cases (and btw the parameters
   should be able to go past their current limits, they don't - like percentage of the balls, it should be able to
   go more than 100%) - that is (loosely, obviously the specific shapes are wrong but the placement and spacing of
   objects is pretty much perfect) exactly how I expect the 3d basilica to look. So this is what the 3d fractal
   should look like (with proper shapes obviously)". Saved to memory (right-rule-criteria, user-judges-by-pictures).
B. Brief: docs/ROUND28.md. Track A "dials": second sphere radius rho (S.k.brho), size dial 2..400 (typed 1..2000),
   new dial "Second sphere, % of the first" (2..50 and 100), depth 1..1000, give-way rules, rho = 1 pictures
   pixel-identical. Overlay in out/r28/dials/overlay/ on base20a; BUILD.txt there; final page dist/r28-final.html;
   final notes out/r28/final/NOTES.md (or final2). Track B "pillow3": the three-corner pillow with one corner on the
   flat circle (never built in round 25), out/r28/pillow3/NOTES.md + out/r28/skeptic/NOTES.md.
C. My reasoning this evening (do not redo): with two equal spheres 100 is a real wall (past it only rings at
   t = cos(180/m); lab frame cannot show them; out/r27/measure/family-rings.png sent to the user as a look).
   Rules "length squared times a map of directions" keep shapes within a fixed squeeze at every size only if the
   map of directions is a flat pillow (Lattes type), so round 25's family is all of it; exact flat cut plus a
   shape-true map of directions is z^2 itself (buds only round the flat picture).
D. When the workflow returns: read final verdict, merge overlay into src/ (cp -r out/r28/dials/overlay/. src/),
   python build.py, check dist/preview.html == dist/r28-final(2).html, re-run checks, own look in light theme,
   freeze base21a, publish Version 21 (Artifact, url https://claude.ai/artifact/Ko9sxAgS5VMvsdEZi4uu3e), pictures.
   Still unanswered by the user: add round 27's carried-over object as an entry? a second Learn view?

## 2026-11-20, late: ROUND 28 returned; VERSION 21 PUBLISHED (Balls on balls dials past their old ends); pillow3 FAILS

A. DIALS (Track A). Final verdict READY, 0 majors left (out/r28/final/NOTES.md). 8 agents, no second fix round.
   Merge: cp -r out/r28/dials/overlay/. src/ (five files: js/00-core, 32-balls, 40-render, 46-mesh, 80-ui), python
   build.py; dist/preview.html is byte for byte dist/r28-final.html (md5 4b03c1dc...). Frozen: base21a = src.
   VERSION 21, version id 1795221232-5d4f.
   What it is: S.k.brho (second sphere's radius, default 1). Size of the neighbours: slider 2..400, typed 1..2000.
   New dial "Second sphere, % of the first": 2..50, or 100 (between: jumps). Depth: slider 1..100, typed 1..1000.
   Past 100 the second sphere becomes min(50, 5000 / size) % by itself and FOLLOWS the size until the user sets it
   on its own dial (BALLS_DIAL.follows; my ruling: kept as built, the checkers agreed). Coming back below 100
   leaves it at 50; "Reset this section" (button is '#ballsReset button') puts it back to 100.
   Two equal spheres: Version 20's program text GL_BALLS untouched to the byte, 16 old states 0 pixels differ.
   Smaller second sphere: program GL_BALLS_RHO, cache key 'balls2'. Twin: ballsInside(x,y,z,{t,grid,rounds,rho}).
   The brief's spindle line (ROUND28.md 1.3) was WRONG for a small second sphere; the page uses
   w = min(1/2, top - zm + rho), plus a "side spindle" (fixer) that cured 2D ghost fans at second sphere 50.
   My own re-runs on the merged page (out/r28/me/): own.py = my numpy writing of the recipe with rho against twin
   and shader, 7 settings (150/33.33, 300/16.67, 200/25 line, 400/12.5 honeycomb, 1000/5, 60/40 honeycomb,
   default): 0 of 317184 verdicts differ; round 27's verd.py (old object against tree.py: 0 of 80000, 0 of 40644)
   and shape.py exit 0 (v21-checks.out); look.py + reset.py with real mouse and keys, light wide, light phone,
   dark 2D: no console errors, typed 5000 holds at 2000, depth 5000 at 1000, reset restores 55.56 / 100 / 16.
   LEFT, all minor (told to the user in short): pale patches on bare skin of a large neighbour (shadow of a hull
   ball; needs a tighter hull); black crescents beside the middle ball at 1000+ (shared lighting); on the phone the
   status sentences stand above the dials; thin threads at kisses; depth 1 is one wall of colour (a sentence says so).
B. PILLOW3 (Track B): out/r28/pillow3/NOTES.md (explorer) + out/r28/skeptic/NOTES.md (skeptic, own scripts).
   found_it = FALSE, both agree. Rule: three-corner pillow, one corner on the flat circle; on the ball
   q -> 8q / (1 - 18 q^2 - 27 q^4), re-timed so the flat circle doubles evenly. Flat cut exact (0 of 20000, five
   sets, also with the flat-plane special case off). c = -1: row of separate LEMONS meeting in single points, same
   above and below, 2 big neighbours (13 % of the middle body each). Then four PLACES for buds: first build only the
   two in the flat picture are buds, off it two thin leaning strings (132.8 deg from +x); second build (both circles
   even, hand-picked cap) four buds at the waist but every body grooved like a walnut (11 % thin). Left neighbour
   SIX buds, right TWO (three-fold wrap round -x). Rabbit: three bodies meet in a point, ragged (5.8 % thin), 44 %
   changes under a half turn. No sphere inversion, no quaternion. Volumes hold from 40 to 200 steps.
   Fails tests 3, 4 (rabbit), 5; test 2 not a plain yes. THE PILLOW FAMILY IS NOW FINISHED: no member passes.
   May NOT be told: see skeptic NOTES section 7 (not "four buds" for the first build; not "nearly round"; not
   "pushed off by 2 everywhere"; no working names).
C. Sent to the user: mid-round out/r28/dials/shots/look-wide-p150-3d.png, look-wide-p300-3d.png and
   out/r28/pillow3/user-1-row.png, user-2-row-B.png, user-3-rabbit.png; at the end out/r28/final/user-1-150.png,
   user-2-300.png, user-3-along.png.
D. User clarified (verbatim, in memory): Balls on balls is "this klein attempt of a proof of concept"; the goal is
   still an iterated rule with a c "with sphere inversions and quaternions and iterations and whatnot". Do not
   polish the Kleinian entry beyond what they ask.
E. NOTHING IS RUNNING. No candidate rule in hand. src == base21a. Still unanswered by the user: carried-over
   object as an entry? second Learn view?

## 2026-11-21: ROUND 29 started (two tracks running), repository created

User, after Version 21 (verbatim): "1. i didn't mind the intersection or collision of the balls after 100%, please
remove whatever automatic rule you have. publish it (and commit it, let's have this as a new repo in my github, you
can store the project in documents/personal/3D-Mandelbrot-Exploration" and, a little later, the Learn message quoted
in full in docs/ROUND29-LEARN.md section 0 (moves inside each step for A whole shape; a grid of points under Show;
"directions" and the laying out afresh are not understood; "All this will help us go through different 3d
approaches at the mathematical level and I can help figure things out too").

A. What the plain recipe gives when nothing keeps the spheres apart (mine: out/r29/me/plain.py, plain-all.png,
   plain.txt): both spheres equal, 120: a dense field of balls with round holes, far distance inside; from about 137
   (square grid) the flat cut is filled completely; past 241 everything is inside. Second sphere 75 at size 80: a
   clean chain with buds (this part of the dial was closed in V21). The user must be told this plainly.
B. Track A "free" (docs/ROUND29.md): both dials free, no jump over 50..100, no clamp; GL_BALLS and GL_BALLS_RHO
   untouched for the states V21 could reach, a new general program GL_BALLS_FREE ('balls3') for the rest.
   Workflow task wfj17skip, run wf_755a8ddb-1a9; folders out/r29/free, truth, eyes, ui, fix, final. Result key
   `result` { build, checks, fix, fix2, final, page, overlayDir, buildLine }.
C. Track B "learn" (docs/ROUND29-LEARN.md): A whole shape gets "Each step: At once | Move by move" (default Move by
   move) with dots (Out, the moves, Thrown out, Home) and "Dots: Few | Some | Many"; One point's Show gets "A grid of
   points" (not laid out afresh), the third choice is renamed by space, new help and a line under Show.
   Workflow task wqh4fcrny, run wf_1eea81e0-f8e; folders out/r29/learn, learn-truth, learn-reader, learn-play,
   learn-fix, learn-final. Allowed files: the four Learn js files, the two Learn css files, body.html if needed.
D. Repository: `git init` here (branch main), `.gitignore` (dist/, the heavy files of out/, notes/paper-kucera.txt,
   .claude/), `.gitattributes` (* -text), README.md. First commit b990b2f "3D Squaring Lab, Version 21, with the
   research so far" (4019 files, 59 MB, out/r29 left out). Private GitHub repo created and pushed:
   https://github.com/ixm-ibrahim/3D-Mandelbrot-Exploration (remote origin, main tracks origin/main).
E. Folder: the app could not resolve Documents\Personal\3D-Mandelbrot-Exploration (it does not exist; I may not make
   it); the folder picker was then cancelled. STILL OPEN: ask the user for a folder; when they give one,
   change_directory to it (the app copies the files at the end of that turn).
F. TO DO when the tracks return: read each final NOTES.md and the result; merge the overlay into src/ (Track A's
   files and Track B's files do not overlap by design; check), `python build.py`, my own checks (recipe against the
   page at cutting states; real-mouse look), freeze base22a, publish (Artifact, url
   https://claude.ai/artifact/Ko9sxAgS5VMvsdEZi4uu3e), commit ("Version 22: ..."), push. If the tracks finish apart,
   publish the first as Version 22 and the second as Version 23. Send the final checkers' user-*.png pictures.

## 2026-11-21, later: VERSION 22 PUBLISHED (Learn: move by move, a grid of points); the way of working changed

- The user (verbatim): "btw, you use up so many tokens - just tell me what to check and I can do it faster than
  whatever you run". So: NO checking rounds any more. Build, one quick look, publish, give a short checklist.
  Both workflows are stopped as soon as their builder hands over (the Learn one was stopped; its checkers never ran).
- The user (verbatim): "why is the repo private? I have to pay for that - just keep it public". The repo is PUBLIC.
- The user found the many base*/ folders disorganized. 25 were removed (commit 7239e21); base19a/20a/21a stay only
  until the free-dials builder is done, then they go. Versions are git tags from now on (v21 = b990b2f). No more
  frozen copies and no more overlays: edit src/ directly, on a branch if need be.
- Version 22 = base21a + the Learn builder's overlay (out/r29/learn/overlay, six files), merged into src/; the built
  page is byte for byte the builder's tested dist/r29-learn.html. Version id 1795278071-21e8. The builder's own
  numbers and what it says is not right: out/r29/learn/NOTES.md (section 4: phone, 3D depth, pace).
- Still running: the free-dials builder (workflow wfj17skip). When it hands over: stop the workflow, copy its overlay
  (00-core, 32-balls, 40-render, 46-mesh, 80-ui) into src/, build, quick look, publish as Version 23, commit, tag.
  Then remove base19a/20a/21a, and move the session to C:\Users\IbrahimMahmoud\Documents\Personal\3D-Mandelbrot-Exploration
  (change_directory; access is already granted) as the LAST thing.

## 2026-11-21, later still: VERSION 23 PUBLISHED (Balls on balls: the two dials are free)

- Version 23 = Version 22 + the free-dials builder's three files (32-balls.js, 40-render.js, 80-ui.js), merged into
  src/. Version id 1795280082-d883. The checking round was stopped before it began (the user's wish); the builder's
  own numbers are in out/r29/free/NOTES.md. Mine on the merged page (out/r29/me/own29.py, own29.txt): twin against
  my recipe 0 differ at 18 states; shader 24 of 815616 differ, all at cutting states (single precision on an edge);
  no console error; the boxes show the numbers that were set (no dial moved another).
- Known, from the builder: small blobs of outline in the 2D view beside tiny lens-shaped bodies at second sphere 75
  and 90; pictures of a filled lump take several times longer to draw (nearly every ray stops on something); the
  lump is given a lit skin at the Drawing radius.
- The last frozen copies (base19a, base20a, base21a) are removed. Versions are tags: v21, v22, v23.
- NOTHING IS RUNNING. No candidate rule in hand.

## 2026-11-21, later: the research leftovers are deleted, the project moves to the user's folder

- The user: "do we need everything from the research? I'd want to remove what is not needed anymore, 15gb seems
  wild." Answer: none of it is needed. It was 25,700 test screenshots (8 GB), 330 zip bundles (4.3 GB), number
  caches (2.2 GB) and old copies of the page, all of which the scripts in `out/` can make again.
- With the user's yes, everything git ignores inside `out/` and `dist/` was deleted for good
  (`git clean -fdX -- out dist`). The folder went from 14.8 GB to 55 MB. No tracked file was touched.
- On disk but not in git: `notes/paper-kucera.txt` (the paper's text) and `.claude/`. `dist/` comes back whenever
  `build.py` runs.
- The session moves to `Documents/Personal/3D-Mandelbrot-Exploration` (the app copies the files at the end of the
  turn). A script in `out/` that needs an old cache or picture has to make it again first.
