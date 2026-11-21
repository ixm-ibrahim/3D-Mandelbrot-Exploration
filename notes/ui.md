# ui: integration notes (first pass)

Files written: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js` (new), `src/js/80-ui.js`,
`src/js/90-boot.js`, `tools/smoke.json`, `notes/ui_embed.py` (new), this file.
Screenshots: `out/ui/` (sections and whole page at 1400 and 375 wide, light-theme footer and scorecard) and
`out/smoke-*.png` (the smoke run).

## What is wired, by the user's 15 points

| # | Where on the page | What drives it |
|---|---|---|
| 1 | Busy label in the stage's top right corner, thin bar on the stage's bottom edge | `setBusy` from the renderer ("Preparing the formula") and the scorecard ("Measuring the approach"); `stageProgress`. `boot()` only calls `initGL()` and `buildCard()`. Smoke step 3 sees both. |
| 2 | Every dial (41) | Built with the new kit: typed box, up/down buttons, step toggle (`powStep` etc.), `int: true` on Iterations, Refining passes, Ray steps, Depth of the search. |
| 3 | Colour and light | `buildControls('colDials', COLOUR_CONTROLS, S.colour, touch, { idPrefix: 'col-', group: 'colour' })`, light dials in the same group. |
| 4 | Scroll wheel on the stage | Camera module (`bindView()`), nothing to wire. Smoke step 2 checks the easing and the 12% notch. |
| 5 | Quality and speed: "Ultra fast" button, "Distance estimate" drop-down (`qde`) | `UI_QUALITY.qUltra` = res 0.5, 1 pass, 90 steps, threshold 2, no shadows, no crevices, `de: 0`, sampled slope. Fast, Balanced and Fine set `de: 3` and `normals: 'sharp'`. |
| 6 | Julia panel: list `#juliaList` (your saved points, classic sets, found by exploring), note `#juliaNote`, name box + "Save this point", "Delete" on each saved point | `applyJuliaPreset`, `juliaSavePoint`, `juliaDeletePoint`, `juliaSavedLoad` in 75-presets.js. localStorage key `squaringLab.juliaPoints.v1`, every access in try/catch; when storage is blocked the list lives for the visit and a note says so. |
| 7 | Arcball / Fly switch on the stage (camera module), plus a "Fly camera" checkbox in the View section | `setCamMode`; `uiViewSync` on `hooks.view` keeps the checkbox in step with the stage switch and the F key. |
| 8 | "Reset this section" at the end of every section (10 buttons); Kleinian "Start from" drop-down with a note; zoom slider with limit boxes on the stage; "Drawing radius" dial in View (to 500) | `addReset` + groups `mandel julia klein approach eq mod cut colour view q`; `applyKleinPreset`; `resetZoomLimits()` in the View reset. |
| 9 | Approach list (first entry "Sphere inversions"), lede, footer section "Sphere inversions and the flat set" | Texts from the approaches module; the false closing paragraph is replaced. |
| 10 | Planes dial (1 to 8) and its note in the approach panel; footer section "Nothing is drawn by eye, and the planes are a free choice" | Specs from the approaches module; page text. |
| 11 | Mandelbrot options: "Julia mosaic" checkbox and "Mosaic cell size" dial | `S.mosaic`, `S.mosaicCell`, `touch()`. |
| 12 | Top row: "2D view" checkbox (`#flat`), above Show | `S.flat`, then `syncControls()` (the colour notes depend on it) and `touch()`. Slice height is the Slice section's dial. |
| 13 | Top row: "Collapse all" / "Expand all" (`#collapseAll`) | Closes or opens every visible `#sections > details.sec`, the mode panel included. |
| 14 | Phase dials with play buttons in both Mandelbulbs, Lift and Turn in Sphere inversions; footer section "Phases that make the solid pulse" | Specs from the approaches module. |
| 15 | Equation: "Power n" slider from -8 to 10 (typed -16 to 24), a note under it, two negative-power presets | `addDial('eqDials', 'pow', ...)`. |

Other wiring from the module reports:
- `refresh()` no longer writes the two figure captions, calls `updateCard()` directly, syncs the mode
  radios, the approach radios, the three mode panels, and calls `hooks.refresh`.
- `boot()` no longer pushes `drawTriad` or `drawStep3d` on `hooks.view`.
- Equation presets: `note` is shown under the drop-down (`#eqNote`), `cut` opens the cut (Mandelbrot mode only).
- `window.squaringLab.idle()` is `renderIdle() && cardIdle()`; the handle also exposes the names the
  modules' own test scripts asked for (see 90-boot.js).
- Mode panels are now `details.sec` (`#mandelPanel`, `#juliaPanel`, `#kleinPanel`) so Collapse all covers them.
- Kleinian dial ranges widened as the presets need (mx and mz -1 to 1, my 1.4 to 2.4).
- Preset data: `python notes/ui_embed.py` copies `data/*.json` into 75-presets.js between marker lines.
- 00-base.css: a global `[hidden] { display: none !important }` (the published page has no wrapper that
  supplies it), the old `.dial` / `.num` rules removed (70-dial.css replaces them), list and top-row styles,
  a stage-coloured rim on the triad, `.label .asis` so μ is not upper-cased into M.

## Fixes in files I do not own

- `src/js/40-render.js`, `setScene()`: `uStepK` is `min(S.q.stepk, 0.5)` in Kleinian mode. Reason: the
  klein-presets research measured hollow and missing pearls at the default 0.8, and its preferred fix is in
  30-shaders.js, which must not be edited now. One line plus a comment.

Nothing else outside my files was changed. 30-shaders.js was not touched.

## Names added

75-presets.js: `JULIA_PRESETS`, `KLEIN_PRESETS`, `presetNarrow`, `presetSame`, `applyJuliaPreset`, `juliaPresetAt`,
`applyKleinPreset`, `kleinPresetAt`, `JULIA_SAVED_KEY`, `JULIA_SAVED_MOST`, `juliaSaved`, `juliaSavedLoad`,
`juliaSavedStore`, `juliaSavePoint`, `juliaDeletePoint`.
80-ui.js: `UI`, `UI_FOV`, `UI_FOV_DEG`, `UI_QUALITY`, `uiEqMark`, `uiJuliaList`, `uiJuliaMark`, `uiKleinMark`,
`uiSections`, `uiCollapsePaint`, `uiViewSync` (plus `refresh`, `applyEquation`, `boot` as before).
No new fields in `S`, no new uniforms.

## Smoke test

`python tools/shot.py --actions tools/smoke.json`: 20 steps, each new step throws on a wrong state. Covers the
six old pictures, wheel easing, busy label and progress bar, page texts and play buttons, 2D view, mosaic
(3D and 2D), a typed negative power, approach parameters (planes 1, turn 40, lift 0.3), a trap choice, Ultra
fast, a Kleinian preset, a Julia preset with save and delete (also with storage blocked), the fly camera,
the View / Quality / Julia / Equation / Approach resets with the zoom limit and drawing radius, collapse all
and expand all. Set `PYTHONIOENCODING=utf-8` on a Windows console, since some results contain ⁻ and ².

## Left for the checking stage

See "open issues" in the report. In short: nothing was tuned, light theme and phone were looked at only
briefly, real mouse and touch input were not tried on the final page, the other modules' own test scripts
were not rerun, and anything that traces into 30-shaders.js was left alone.
