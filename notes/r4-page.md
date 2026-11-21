# r4-page: the page in round 4

Files edited: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js` (only the part after the data blocks),
`src/js/80-ui.js`, `src/js/90-boot.js`, `tools/smoke.json`. Nothing else was touched.
Scripts, logs and screenshots: `out/r4/page/`.

Test page: `sh out/r4/page/build.sh` (base3 plus the five page files and `src/js/00-core.js`; `sh out/r4/page/build.sh base2`
also takes the dial kit from `src/`). Last state: built against **base3**, `python tools/shot.py --url dist/r4-page.html
--actions tools/smoke.json` exits 0 with no console errors (`out/r4/page/smoke-final.log`).

## What was built (SPEC4, section "page")

| Item | Where | How |
|---|---|---|
| 2, N4 extreme ranges | top row, `#extreme`, hint `#extremeNote` | `addCheck` whose setter calls `setExtreme(on)` (or sets `S.extreme` when the kit has none). Wide limits on: power, iterations, Julia c (3), Kleinian dials (9), mosaic cell, cut height, fly speed, drawing radius, field of view, resolution, refining passes, ray steps, surface threshold, ray step share, slope width. 25 dials show "wide" on base3. |
| 3, N7 Julia drop-down | `#juliaPreset` in `#juliaPresetHost` | groups "Your saved points", "Classic sets", "Found by exploring"; name box and "Save this point" beside it; `#juliaDelete` ("Delete this saved point") only while a saved point is chosen. |
| 4, N8 entries set only what they are about | `applyJuliaPreset`, `applyKleinPreset` | Julia: c only. Kleinian: `KLEIN_KEYS` = mx my mz three L cx cy cz invR (the `iter` in the data is ignored). `#juliaFrame` and `#kleinFrame` ("Frame it") move the camera and the 2D frame only. Saved points hold `{ name, c }`. Both lists read "Your own values" (a disabled first option) when the values are on no entry. |
| 5, N5 and N6 sections | `#secExport > #exportPanel`, `#secMesh > #meshPanel`, after Quality and speed | `boot()` calls `buildExportPanel('exportPanel')` and `buildMeshPanel('meshPanel')` when they exist, after `initGL()`; otherwise the host gets one sentence saying the part is missing. Collapse all covers them. The page puts no text of its own in these sections (the mesh panel brings its own). |
| 6 whole powers | `uiPowerDial()` in 80-ui.js, hint `#powWhole` | The power dial lives alone in `#powHost` and is made again with `int: true`, step 1, when `ap().integerOnly` flips (the kit fixes "whole numbers" at creation). The power is rounded on the way in. Leaving gives the 0.1 step and the step toggle back. |
| 7 Kleinian list | not re-embedded | `data/klein-presets.json` was unchanged (19 entries, 19:02) when I stopped. After it changes run `python notes/ui_embed.py`; it rewrites only between the marker lines, so the new code after them is safe. |
| 8 Reset everything, quality mark, texts | `#resetAll`; `.btn.is-on` + `aria-pressed` on the four quality buttons; `footer.why` | see below |
| 9 smoke test | `tools/smoke.json` (27 steps), written by `python out/r4/page/make_smoke.py` | see below |

Texts: the closing part has a new section "Questions from testing, answered" with one short answer per question of
the user (why the earlier solid tore, whether the planes are forced, quaternions and the third map, the trap in 3D,
distance estimate and inside colours in 2D, the glow, the slices, extreme ranges, what a list entry changes, saving
pictures and models). The answers on the glow and the slices are taken from `notes/fix-shaders.md`.
**Paragraphs that describe a part are shown only when the page has that part**: elements carry `data-needs`
(`pillow`, `solid`, `inside`, `extreme`, `export`, `mesh`) and `boot()` hides those whose part is missing. On base3
that hides the trap-solid answer, the inside-colour sentence, the saving answers and the two pillow sentences.

**Gap, clearly marked:** `notes/pillow.md` did not exist when I stopped. `src/body.html` has an HTML comment
"GAP (page engineer, round 4)" above `<p data-needs="pillow" id="pillowText">`, which holds only a neutral
sentence ("The approach at the top of the list is the replacement..."). Put the plain-language text from
`notes/pillow.md` there, and check the answer under "Should the number of planes be forced by the maths?".

## The 42 page defects

Reproduced before on base2 (`out/r4/page/repro-before.log`, `repro-phone-before.log`), re-run after on base3
(`repro-after.log`, `repro-phone-after.log`), and covered by the smoke test where a step could check them.

Fixed: p8a-1 (Kleinian list is no longer in the reset group and entries do not move the camera), p12-1 and p7-3
(14 controls that do nothing in 2D are put away there, with a note in each section: class `only2d`), p13-1 (each
tick box has its own line and both buttons share a width, so nothing moves), p13-2 (top row is sticky), p13-3,
p13-5 (button at y 748 of 812), text-4, text-5 (page text), text-8, text-9, text-10, text-13, text-14, text-16,
maths-2, p15-9, code-1, p8a-2, p8a-3, p8a-4, p8a-5, p6-1 (Frame it uses 5.2 for the Airplane: `JULIA_FRAME_DIST`),
p6-3 (same name and point: no second entry; same name on another point gets " (2)"), p6-5, p5-4, p5-5, p8b-3,
p8b-4 (sliders keep to the working region: i part 1.5 to 2.4 typed from 1.2, L from 1 typed from 0.5, centre y
0.05 to 2.35; a warning `#kleinWarn` for the user's own values; the extreme ranges reach the old limits and beyond),
p8b-5 (L is hidden while the third map is off and sits under its checkbox), p12-3 (label "2D view (slice at
z = 0.35)"), p14-2, p15-6 (a sentence on the stage, `#stageNote`, for the plain equation with a power from -1 to 1),
p7-4 (a copy of the stage hint, `#hintBelow`, under the picture on narrow screens), code-4 (page side: a dial of an
approach now runs `uiApproachParam`, not the whole `refresh`).

Fixed in part:
- p11-2: ticking the mosaic in the 3D view now cuts the solid open at z = 0 (and unticking puts the cut back),
  with a sentence in the help. The camera is NOT moved, because the user asked that choices leave the camera alone.
- text-15: Kleinian group heading renamed, "into the family" reworded where the note is shown, a sentence on what
  the fractions mean. The Julia notes ("period-two disc" and so on) live in `data/julia-presets.json`, which is
  not mine: not rewritten.
- p8b-7: Frame it backs the camera off by 1.2 on a stage that is taller than wide. Not checked picture by picture.
- p6-4: the note under the list says when the equation or power makes the name wrong; the advice "Best with one
  plane..." is shown only under the Sphere inversions approach.

Made pointless by N8 (an entry no longer sets planes or iterations): code-3, p6-2, p10-3.

## Names added or changed

75-presets.js: `presetFrame(hint, back, flatH)`, `presetNarrowK`, `juliaEntry(key)`, `juliaFits`, `juliaKeyAt(prefer)`,
`frameJuliaPreset(p)`, `JULIA_FRAME_DIST`, `juliaNoteFor(p)`, `KLEIN_KEYS`, `kleinFits(p)`, `frameKleinPreset(p)`,
`kleinNoteFor(p)`, `kleinTrouble()`. Changed: `applyJuliaPreset` (c only), `applyKleinPreset` (group and sphere only),
`kleinPresetAt(prefer)`, `juliaSavePoint` (returns `{ ok, kept, at, dup }`), saved points are `{ name, c }`.
80-ui.js: `UI_GROUPS`, `UI_EXTREME_TEXT`, `uiApproachParam`, `uiPowerDial`, `uiJuliaOptions`, `uiJuliaList` (now
refills the drop-down), `uiFlatPaint`, `uiQualityMark`, `uiExtremePaint`, `uiEmptyNote`, `uiOnce`, `uiResetAll`;
new fields in `UI`. `uiViewSync` (on `hooks.view`) now keeps every mark in step with the state, whoever changed it.
`UI_QUALITY` entries also set `stepk` and `smooth`.
Element ids: `toprow`, `extreme`, `extremeHost`, `extremeNote`, `resetAll`, `flatZ`, `juliaPresetHost`, `juliaPreset`,
`juliaFrame`, `juliaDelete`, `kleinFrame`, `kleinWarn`, `powHost`, `powWhole`, `colReset`, `qMarkNote`, `stageNote`,
`hintBelow`, `secExport`, `exportPanel`, `secMesh`, `meshPanel`, `pillowText`. Gone: `juliaList` and the `.plist*` styles.
CSS classes: `toprow-checks`, `toprow-btns`, `flat-z`, `sec-inner`, `pick-row`, `pick-list`, `warn-note`,
`stage-note`, `hint-below`, `only2d`, `.btn.is-on`, `.why h3`.
`window.squaringLab` gains `frameJuliaPreset`, `frameKleinPreset`, `juliaKeyAt`, `kleinPresetAt`, `kleinTrouble`,
`resetAll`, `saveFile`, and, each only when it exists: `takeSnapshot`, `releaseSnapshot`, `sampleSlice`,
`exportBusy`, `meshBusy`, `zipStore`, `setExtreme`, `isExtreme`. No new fields in `S`, no new uniforms.

## Smoke test

`python out/r4/page/make_smoke.py` writes `tools/smoke.json` from readable steps (edit the steps there, not the
JSON); `--mine` writes a copy that keeps its screenshots under `out/r4/page/smoke/`. It covers the old pictures
and checks plus: the opening state, the Julia drop-down, an entry leaving camera, iterations, planes and depth
alone, Frame it, "Your own values", save and delete (also with storage blocked), the extreme switch widening a
range and pulling a value back, whole powers (it marks an existing approach `integerOnly` for the test), Reset
everything, the quality mark, the 2D view putting 3D controls away, the two panels, collapse all across modes.
- **Model job:** uses `window.squaringLabMeshTest = { cells: 48 }` and the buttons `meshStart` / `meshSave`. Run for
  real against the live `src/js/46-mesh.js` (`dist/r4-page-mesh.html`): a zip arrived through
  `window.squaringLabSaveHook`. The renderer of base3 has no `sampleSlice`, so that run used the module's test
  sphere; with `sampleSlice` present the step uses the Julia set for c = -1 instead. That path is untested.
- **Picture job:** `src/js/45-export.js` had not arrived. The two steps go by the button texts the plan fixes
  ("Start the picture", "Save the file") and look for a size choice with typed width and height; they report a
  skip when `exportBusy` is missing. **Untested against the real panel.** If the panel has ids, use them here.

## For whoever joins the parts

1. `notes/pillow.md` -> the marked gap in `src/body.html` (see above).
2. Kleinian data: run `python notes/ui_embed.py` after `data/klein-presets.json` grows. The group heading of an
   entry is `p.group` if it has one, else it comes from the first word of `p.source` (`cusp`, `inside`,
   `explored`, `sphere` -> "Turning-out sphere"), else "More". An entry's `cam` may carry `target`.
3. The smoke test asserts things other modules own (play buttons of the phase dials, the option texts "Cross",
   "How near it came, as a glow", "Electric", `par-mercator-planes` going to 8, the turn dial hidden at 2 planes).
   They held on base3. If the new maths or colour modules rename them, adjust `out/r4/page/make_smoke.py`.
4. Equation presets ("Start from" in Equation) still reframe the camera, and one opens the cut. I left that: an
   equation is a different object. If the user's "presets leave my camera alone" is meant for them too, drop
   `resetCam(p)` in the `eqPreset` handler and add a third Frame it.
5. "Reset everything" does not reset the groups `export` and `mesh` (file settings), and keeps saved Julia points.
6. The step cap for the Kleinian view (`min(stepk, 0.5)` in 40-render.js) is stated in the hint of the ray step
   dial. If the renderer drops the cap, drop that sentence (80-ui.js, `qstepk`).

## Not done or not checked

- Pillow text (no `notes/pillow.md`), Kleinian re-embed (no new data), picture job run (no module): see above.
- Looked at, in pictures (`out/r4/page/look-*.png`, `phone-first-screen.png`): desktop dark (Julia, Kleinian,
  Quality and the new sections, closing texts), phone dark (first screen, controls top with the Julia panel),
  desktop light (View and Quality with extreme ranges on and Fine marked), phone light (Kleinian panel, Quality and
  the new sections). NOT looked at one by one: Approach, Equation, Modifiers, Slice and Colour sections in the light
  theme and at phone width, the lower figures, and the mesh panel inside its section. The assignment asked for
  every section in all three modes in both themes at both sizes; time ran out before that was complete.
  A script check found no sideways scroll at 375 px (scroll width 375) with every section open.
- Extreme limits are choices, not measurements: nobody timed 4000 iterations or 20000 ray steps.
- The whole-power hint says "the chosen approach is only defined for whole powers"; the real reason for pillow
  should replace it once `notes/pillow.md` says it.
