# Round 4, render-export: snapshots, volume sampling and "Save a picture" (N5)

Files: `src/js/40-render.js` (changed), `src/js/45-export.js` (new), `src/css/45-export.css` (new).
`src/css/40-render.css` is unchanged. Scripts, logs and pictures: `out/r4/render-export/`.

Test page: `sh out/r4/render-export/go.sh <tests>` builds `dist/r4-render-export.html` (base4 + my four files + a
private shader stand-in, `out/r4/render-export/30-shaders.js` = base4's shader plus the `uRaw` branch) and runs the
named tests of `out/r4/render-export/t.py`; `go.sh --real <tests>` builds with `src/js/30-shaders.js` and
`src/js/25-colour.js` instead of the stand-in.

## What the user gets

A section "Save a picture" with: Size (as on screen, twice, four times, 1920 x 1080, 2560 x 1440, 3840 x 2160,
7680 x 4320, square 2048, square 4096, typed width and height), a line saying how many pixels that is and whether
the picture shows more or less at the sides than the screen, Quality (as on screen now, Fine, Extra fine), File
type (PNG, JPG, WebP), and "Start the picture". While it runs: a progress bar, the percentage, the time left and
"Cancel". When done: a small preview, the size, the file name, the file size, the time taken, "Save the file" and
"Discard". Messages are plain sentences in a `role="status"` line. The panel starts at twice the size on screen,
Fine, PNG. It looks and behaves like the 3D model panel next to it.

Decisions worth knowing:
- **"As on screen now" gives the same picture, only larger.** The surface threshold is counted in pixels, so at
  another size the surface would sit somewhere else and the trap colours with it. For this choice the threshold is
  scaled with the picture (`q.detail *= height / height on screen`), so the solid and its colours are where the
  screen has them. Fine and Extra fine count the threshold in the new picture's own pixels (0.7 and 0.5), which
  brings out finer detail at larger sizes and so is not pixel for pixel the screen's picture.
- A size with another shape than the stage keeps the height of the view and shows more or less at the sides (the
  shader scales by the height). The line under the size choice says so.
- The outline of the 2D view and the glow beside it are widths in pixels (`S.colour.edge`, `edgeGlow`): the job
  scales them with the picture, so they keep their weight.
- Sizes above 100 million pixels are refused in words before anything starts (`EXPORT_MAX`), and so is any size
  the browser cannot make a canvas for (one pixel in the far corner is drawn and read back).
- The file is kept until "Discard", so a refused save can be tried again. A browser that cannot write WebP hands
  back a PNG; the file is then named .png and the status line says so.

## How it works

**Snapshots (40-render.js).** `takeSnapshot()` returns `{ S, theme, basis, stage, want, P, ... }`: a deep copy of
`S`, a copy of `theme`, the camera as `basis()` gives it, the stage size (CSS pixels and picture pixels) and the
scene program for those settings (compiled if needed, and pinned: the program cache does not evict an entry with
`pins > 0`). `releaseSnapshot(snap)` unpins. After a lost GL context the program is built again from the
snapshot's own recipe (`snap.want`) on next use.

`setScene(P, o, snap)` is still the one place uniforms are set. With a snapshot it puts the snapshot's `S` and
`theme` values into the live `S` and `theme` objects key by key (`snapSwap`), sets the uniforms, and puts the live
values back in a `finally`, all inside one synchronous call; the camera is passed as an argument. That is why
`setColourUniforms`, `apVec()` and anything else that reads `S` during that call see the frozen values without
being changed. Nothing can run in between, so the page never sees the stand-in values.

**Background queue (40-render.js).** `bgPiece(draw, read, late)` queues one piece of drawing. Pieces run one at
a time through the page's own GL context. `bgPump` starts a piece, puts a fence behind it, and looks for the fence
through a message channel (not slowed in a hidden tab; no animation frame is involved) and, after 4 ms, a 2 ms
timer. Results are read back through a pixel buffer object, so reading never waits for the GPU. While the live
picture is busy (`!renderIdle()`, or touched in the last 300 ms, and the tab is visible) the next piece may only
start three times the last piece's duration after it ended (a quarter of the time), and pieces aim at 5 ms; when
the live picture is idle or the tab is hidden pieces follow one another and aim at 12 ms.
Pieces are sized by the GPU's own timing (`EXT_disjoint_timer_query_webgl2`), which arrives a little later than
the piece and is handed to `late(ms)`. The clock is only a fallback and is not allowed to shrink a piece below a
floor: on a GPU that other programs are using, a piece of any size can take several milliseconds by the clock,
and answering that with ever smaller pieces made a 2 megapixel job take 190 s instead of 7 (measured, then fixed).

**`sampleSlice(snap, cx, cy, side, z, N)`** draws the flat branch with `uRaw = 1` into an RGBA32F target, in
strips sized as above, with `setColourUniforms(L, true)` and `S.flat` false (a volume is the 3D picture whichever
view the snapshot was taken in). Layout as in CONTRACT4; `null` when the context is lost, the program cannot be
built, float targets cannot be read (`EXT_color_buffer_float` missing) or the snapshot was released.

**The picture job (45-export.js).** Tiles of 512 x 512 from the top row down. Each tile is drawn into a float
target with the same jitter sequence and additive passes as the screen (`uRes` = the whole picture, `uOff` = the
tile's corner plus the jitter), resolved with the page's own display shader (`blitP`, so the tone curve is the
screen's by construction), read back as bytes and put into a 2D canvas kept in ordinary memory. The first pass
of a tile feels its way (a few rows, then at most four times as many); later passes go several whole passes to a
piece when they fit. At the end `canvas.toBlob`, a small preview, and the large canvas is let go.

## Results (all on the shared GPU; pictures and logs in out/r4/render-export/)

| Check | Result |
|---|---|
| typed 256 x 256 PNG through `window.squaringLabSaveHook` | 256 x 256, image/png, 94 kB (`t.py basic`) |
| 8K to the end (`t.py big`, one pass, as on screen) | 7680 x 4320 exactly, JPG 1.2 MB, 7.5 s, preview 480 x 270; typed 16384 x 16384 is refused in words before anything starts |
| same size as the screen against the screen, 3D / 2D / Kleinian | largest difference 1 of 255 (the dither), stand-in and real shader |
| twice the size, "as on screen now", scaled down, against the screen | mean 0.9 of 255, 0.1 % of pixels differ by more than 24 (edges); real shader and colour |
| independence (`t.py indep`, picture `indep.png`) | job started, then approach, power, colours, light, iterations, cut, camera, quality and mode changed while it was at 0 to 8 %: its picture is identical (difference 0) to the same job run on an untouched page; the live picture during the job is identical to the live picture after it |
| frame gaps on Balanced, simulated drag, back to back (`t.py gaps`) | no job: mean 16.7 ms, worst 17 to 37 ms; 8K Extra fine job running: mean 16.5 to 16.7, worst 17 to 42 ms, none over 50; idle with the job running: worst 20 to 25 ms |
| live picture finishing after a move | 0.7 to 1.6 s without a job, 1.1 to 2.1 s with one (same runs) |
| hidden tab (animation frames stopped, `document.hidden` true) | the job finishes; picture identical to the same job shown; 10 s against 7 s shown |
| `sampleSlice` layout | 10 single points asked one by one equal the 64 x 64 grid exactly; unchanged (difference 0) after the page moved to another mode and camera; `null` after release |
| `sampleSlice` cost | about 1 to 2 ms a call at N = 49, 9 to 14 ms at N = 513 |

3D model job run for real from the page's own panel at 128 cells (`python out/r4/render-export/mesh_real.py`, stand-in
shader; zips in `out/r4/render-export/zips/`, read back with zipfile, STL parsed with the mesh engineer's functions):

| Picture | Time | Triangles | Closed | Pieces | Size mm | Zip |
|---|---|---|---|---|---|---|
| Julia set, c = -1 (STL, OBJ, PLY) | under 1 s | 26,940 | yes | 1 | 100 x 49.0 x 35.2 | 2.8 MB, CRC correct |
| Mandelbrot, default (STL) | 0.8 s | 32,284 | yes | 1 | 100 x 91.1 x 27.3 | 1.5 MB, CRC correct |
| Kleinian, default (STL) | 0.9 s | 93,224 | yes | 1 | 99.0 x 100 x 51.3 | 4.4 MB, CRC correct |

The Kleinian numbers equal the mesh engineer's stand-in run exactly. The other two differ from theirs in height
because base4 starts the sphere-inversion approach at one plane (theirs was base3).

## Names

40-render.js, new: `stagePixels()` (size of the on-screen picture in pixels; `ensureTargets` uses it),
`sceneUniforms(P, o, basis)` (the old body of `setScene`), `BG`, `SNAP_NONE`, `snapCopy`, `snapSwap`,
`takeSnapshot`, `releaseSnapshot`, `snapProg(snap)` (ready program, 'wait' or null), `snapReady(snap)` (awaits it),
`bgLiveBusy()`, `bgTarget()`, `bgPiece(draw, read, late)`, `bgLate`, `bgWake`, `bgWoken`, `bgPump`, `sampleSlice`.
Changed: `setScene(P, o, snap)` (third argument; `o.slice = { x, y, h, z }` draws that slice, `o.raw` sets `uRaw`
and is passed to `setColourUniforms(L, raw)`), `makeTarget(w, h, f32, bytes)` (fourth argument: an 8-bit target),
`sceneDe(q = S.q)`, the cache clean-up in `sceneEntry` (skips pinned programs), `setupGL` (counts contexts),
the context-lost handler (ends background pieces).
New fields of `R`: `gen` (GL context generation), `f32`, `bgN`, `bgMs`, `bgHeld` (pieces drawn, their time, times a
piece was held back for the live picture; for tests). Program entries may carry `pins`.
New uniform set: `uRaw` (0 everywhere except volume sampling).

45-export.js: `EXPORT_TILE`, `EXPORT_MAX`, `EXPORT_SIZES`, `EXPORT_QUALITY`, `EXPORT_KINDS`, `EXPORT_NAMES`,
`EXPORT_WORDS`, `EXPORT` (`opt`, `job`, `result`, `ui`), `exportBusy`, `exportStop`, `exportBytes`, `exportTime`,
`exportDims`, `exportCanvas`, `exportRun`, `exportStart`, `exportSave`, `exportSay`, `exportPaint`,
`exportSizeNote`, `exportShow`, `buildExportPanel`.
Element ids: `exportSize`, `exportW`/`exportWNum`, `exportH`/`exportHNum` (bare dials, shown for the typed size),
`exportSizeNote`, `exportQuality`, `exportKind`, `exportStart`, `exportCancel`, `exportBar`, `exportStep`,
`exportPreview`, `exportFacts`, `exportSave`, `exportDiscard`, `exportMsg`. Dial-kit group: `export`.
CSS classes (45-export.css): `export-panel`, `export-typed`, `export-size`, `export-run`, `export-bar`,
`export-step`, `export-done`, `export-preview`, `export-facts`, `export-msg`.
No new fields in `S`.

## For whoever joins the parts

1. The smoke test's two picture steps find the panel by the texts the plan fixed and pass as they are when run
   on their own (`python out/r4/render-export/smoke_part.py`). See "Smoke test" below for the whole run.
2. `window.squaringLab` needs nothing new for the page; tests of mine use `R.bgN`, `R.bgMs`, `R.bgHeld`.
3. A job's quality comes from `EXPORT_QUALITY` in 45-export.js; `fine` repeats the page's Fine preset
   (`UI_QUALITY.qFine` without `res`). If the page changes that preset, change it here too.
4. "Reset everything" leaves the group `export` alone (page engineer's choice); the panel has its own
   "Reset this section".
5. The step cap for the Kleinian view (`min(stepk, 0.5)`) is unchanged in `sceneUniforms`.
6. The model job and the picture job can run at the same time: their pieces take turns in the one queue.

## Smoke test

- `tools/smoke.json` as it stands FAILS on this page at the picture job's second step ("the picture job did not
  end with a Save the file button"), and the cause is in the test, not the panel: `tools/shot.py` runs a step's
  `js` first and its `wait` afterwards, and the generator put the wait for the job on the step that clicks Save.
  So Save is looked for 300 ms after Start, while the job is still drawing (it was at 20 %).
  **Change needed in `out/r4/page/make_smoke.py`:** give the step holding `__EXPORT_START__` the
  `wait='!window.squaringLab.exportBusy || !window.squaringLab.exportBusy()', timeout=300` and give the step
  holding `__EXPORT_SAVE__` `wait=None` (the model job's two steps already have this order), then write
  `tools/smoke.json` again.
- With exactly that change (`out/r4/render-export/smoke-fixed.json`, made from `tools/smoke.json` by moving the
  wait) the whole test passes on `dist/r4-render-export.html` (base4 + my files + the shader stand-in): 27 steps,
  exit 0, no console errors, picture job "delivered squaring-lab-mandelbrot-256x256.png, 256 x 256", model job
  "delivered squaring-lab-julia-48.zip" through the real `sampleSlice` (`out/r4/render-export/smoke-final.log`).
- With the real `src/js/30-shaders.js` and `src/js/25-colour.js` in place of the stand-in the smoke test stops at
  step 3, "the progress bar never showed while drawing". It does the same on base4 plus those two files WITHOUT
  mine (`dist/r4-re-others.html`, `out/r4/render-export/smoke-others.log`), so it is not caused by this module.
  Not looked into further: either the picture of that step is now drawn too quickly for the test to see the bar
  (it looks every 16 ms), or the bar is not raised with the new shader.

## Not done or not checked

- With the real shader and colour files only `t.py match` and `t.py twice` were run (both pass). The
  independence, frame-gap, hidden-tab and model-job runs used the shader stand-in.
- Fine and Extra fine against the screen were not looked at as pictures with the real shader (`t.py fine` is
  written for that and was not run). If their colour bands shift visibly against the screen, make "As on screen
  now" the default (`EXPORT.opt.quality` and the `def` of the Quality select).
- The panel was looked at in the dark theme at desktop width only: not at 375 px, not in the light theme.
- Not run: Firefox, Safari, a real hidden tab (it was simulated), a lost GL context during a job, the WebP
  fallback, a picture job and a model job at the same time, `saveFile` on the published host (its size limit is
  unknown).
- On a device without `EXT_color_buffer_float`, `sampleSlice` gives null and the model job says the picture
  could not be read. The picture job works there with one pass (as the screen does).
- While the live picture is busy the job takes less than its quarter: pieces are timed by the clock there, which
  also counts the wait behind the live drawing. Frames stay smooth; the job is just slower than it could be.

## Left over from the fix pass (notes/_fix1.md, render)

- perf-6 (small moving preview at Fast, Balanced, Fine): not changed. A cheaper distance estimate for the moving
  picture is still one value in `preview()` (`nt`), but it changes the outline while moving; with the time going
  into the job it was not tried against the repaired rough estimate.
