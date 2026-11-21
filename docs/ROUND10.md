# Round 10: what the second check found

The second check (nine testers on Version 8, `docs/ROUND9.md`) re-ran the 36 defects of the first check: 25
gone, 7 better, 8 unchanged (all known as open or accepted), none worse. It filed 21 new defects
(`notes/_t9_defects.json`; reports in `notes/_t9_reports.json`; recheck states in `notes/_t9_rechecks.json`):
2 major, 19 minor.

Done already by the orchestrator (Version 9, `base9/`): t9-words-1, t9-words-2, t9-words-3, t9-solids-1,
t9-dials-1, t9-kleinian-2, and t9-walk-1 (the ray step dial now stops at 1.2).

## Base for this round

`base9m/` = `base9/` (Version 9) + the round 9 mesh engineer's `46-mesh.js` (`notes/r9-mesh.md`) + small page
edits. Page: `dist/v9m.html`. Smoke test for this round: `tools/smoke-v9m.json` (52 steps; it passes on
`dist/v9m.html`). Do not use `tools/smoke.json` this round: another engineer, who works on the shader files
against an older base, still needs it as it is.

Build: `python build.py --name r10-<you> --base base9m --use <your files>`. Scripts, logs, pictures under
`out/r10/<you>/`; notes in `notes/r10-<you>.md`. Own files only; never plain `python build.py`; one
`tools/shot.py` at a time; text in plain words, sentence case, no em dashes; no git, no publishing.

## mesh: `src/js/46-mesh.js`, `src/css/46-mesh.css`

Defects: **t9-mesh-1 (major)**, t9-mesh-3, t9-mesh-4, t9-mesh-5, and the thin coloured line round a cut face
at offset 0 that the round 9 engineer found and did not trace (`notes/r9-mesh.md`).

- t9-mesh-1: the model of the example "Sea urchins" (and other trap solids with hair-thin spikes) is covered in
  fins that the picture does not show; with Surface offset 0 the same solid comes out like its picture. The
  half-cell offset together with the rule that keeps parts thinner than a cell grows every hair into a fin. A
  model must not show what the picture does not. Either keep the thin-part margin only for parts the picture
  also shows, or drop fins and flakes smaller than about a cell before the offset is applied, or start such a
  solid at offset 0; judge by the tester's measure on the three Julia examples and on the seven standard jobs,
  which must not get worse (`out/t9/mesh/drive.py`, `check.py`; `out/me/meshcheck8/` shows how to point them
  at your page).
- t9-mesh-5: with offset 0 on a hollow trap solid "Keep only the largest piece" keeps an inside-out inner wall
  and the readme prints a negative volume. Choose among pieces whose volume is positive; never print a negative
  volume or "so it can be printed" for such a result.
- t9-mesh-3 and t9-mesh-4: the warnings. No warning for a model that follows its picture (inner layers nobody
  sees do not count); advice in the order that helps; the kept share shown whenever pieces were dropped.

Time: aim for 40 minutes, stop at 55.

## camera: `src/js/50-camera.js`, `src/css/50-camera.css`

Defect: t9-camera-1 (a pinch that reaches a zoom limit says nothing, while the wheel and the buttons say why).
Also from the first check, still open: when a trap solid is switched on in the Kleinian view, the start view
cannot look at the picture because the program is not ready (solids-7, remaining part; `notes/r7-camera.md`).
If there is a safe way to frame it once the picture is ready, without moving the camera after the user has
started to drag, do it; if not, leave it and say so. Time: aim for 20 minutes, stop at 30.

## dial: `src/js/70-dial.js`, `src/css/70-dial.css`

Defect: t9-dials-2 (at the low end of Trap thickness, Surface threshold and Fly speed the arrows leave the step
grid and never come back to round values). Fix it in the kit as the tester suggests, so that every dial gains.
Then run the first check's driver on all number boxes once more (`out/t6/controls/drive.py`). Time: aim for 20
minutes, stop at 30.

## engine (starts later, when the shader engineer of round 9 has returned and been joined)

**t9-mesh-2 (major)**: models of trap solids carry other colours than the picture ("Chain of bubbles" teal
instead of a rainbow swirl, "Sea urchins" confetti): a sample of a trap solid is still coloured at the grid
point, where another layer of the trap is the nearest. Also: t9-solids-2 (the help of "Orbit steps the trap
reads" should say that 4 keeps colours in place while zooming and that a higher number repaints areas as the
view zooms in), t9-solids-3 (Mandelbulb approach: colours differ between presets), t9-solids-4 and t9-words-4
(fine lines in folds and on shadowed undersides at grazing angles: find out whether they are in the shadow or
crevice shading), t9-export-1 (a thin layer of a trap solid differs between the screen and a larger file),
t9-flat-1 and t9-kleinian-1 (to be looked at again after the round 9 cure for Kleinian trap solids).

## Report

summary; files_changed; fixed (id, what, evidence); not_fixed (id, why, learned); names_added;
needs_from_others; risks. Say what you measured and what you only reasoned.
