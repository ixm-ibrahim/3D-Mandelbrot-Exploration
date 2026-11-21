# render: what changed in `src/js/40-render.js` and `src/css/40-render.css`

Owner files only. Nothing else in `src/` was edited. Every name the contract lists for this module still works
(`canvas`, `stage`, `gl`, `initGL()`, `touch()`, `viewChanged()`, `kick()`, `renderIdle()`, `pick(px, py)`,
`say(text)`, `R`).

## What was built

1. **Shader programs compile without blocking the page.**
   A new program is started (`compileShader` + `linkProgram`) and the loop then asks the driver once per frame
   whether it has finished (`KHR_parallel_shader_compile`, `COMPLETION_STATUS_KHR`). Nothing else is asked of the
   program before that, because link status and uniform locations make the page wait. Meanwhile the last picture
   stays on the canvas, `setBusy('compile', 'Preparing the formula')` is up and the status line says the same.
   When the driver is done the label is cleared and drawing starts. On a driver without the extension the label
   is shown, two frames are let through so it reaches the screen, then the compile runs and blocks once.
   A failed compile shows the message in `#glfail` as before, logs one `console.error` with the driver's log,
   clears the busy label and leaves the renderer idle. A formula that cannot be read gets its own sentence.
2. **Programs are prepared ahead of time ("warming").** Half a second after a picture is finished, the renderer
   compiles, one at a time and only while idle, the programs the next click is most likely to need: every
   approach with the current equation, the other form of the power (n = 2 uses `sqr`, anything else `pw`), the
   Kleinian program, and every equation preset with the current approach. A switch to any of them then draws at
   once with no busy label. Only on drivers with parallel compile. The cache holds 40 programs, least recently
   used dropped first.
3. **Every uniform of the contract table is set**, including `uBound`, `uMosaic`, `uFlat`, `uFlatC`, `uFlatH`,
   `uSliceZ`. `uNT` comes from `S.q.de` (0, 1 or 3; numbers or numeric strings) for the preview, the full passes
   and picking. `uAnalytic` is 1 only when the "sharp" slope is chosen and `uNT` is 3 (and not in Kleinian mode).
4. **2D view.** Same schedule. The preview has its own size factor (`R.ps2`) that starts at full size and
   shrinks only when a full-size preview takes more than about two frames of GPU time. `pick()` in the 2D view is
   computed in JavaScript from `S.v2` and `S.cut` with the shader's own formula, so it works without float
   render targets and never returns null.
5. **Progress bar.** `initGL()` creates `<div id="drawProgress" class="draw-progress" hidden aria-hidden="true"><span></span></div>`
   inside `#stage`: 3 px along the bottom edge, track `--line`, fill `--brass`. It shows the share of the
   full-quality drawing done (rows of all passes), updated as each band comes back from the GPU, and is hidden
   while a preview is showing, while a program is being prepared, and when the picture is finished.
6. **Band and preview sizing no longer collapses.** The baseline timed each job by the wall clock, read once per
   frame, against a fixed 30 ms. On a 30 Hz display, or with anything else using the GPU, every band looked slow
   and bands shrank to two rows (I measured 45 s for one picture on this shared machine). Now:
   - where `EXT_disjoint_timer_query_webgl2` exists (Chrome, Edge) each job is timed by the GPU itself, bands aim
     at 70% of a frame of GPU time, and a finished band is looked for between frames (a 3 ms timer) so the next
     follows at once;
   - elsewhere the clock is used as before, but against the measured frame interval (`R.dt`) and with a least
     band size of 1/32 of the picture.
7. **No black flashes.** Before the first picture exists the canvas is cleared to the stage colour (it used to be
   black, which showed in the light theme now that the first compile no longer freezes the page). When the stage
   or the resolution changes, the last picture is put straight back, stretched, until the new size is drawn.
8. Kept as they were: preview / band / pass schedule and the 170 ms settle time, the background-tab timer
   fallback, context loss and restore, `renderIdle()`, `viewChanged()`, 3D picking, all status texts.

## Names

Top-level names in `40-render.js` (all others are unchanged from the baseline):

| Name | Meaning |
|---|---|
| `progStart(fsSrc)` | start compiling and linking a program; returns its entry `{ p, vs, fs, state, log, l }` |
| `progSettled(e)` | has the driver finished with it (never blocks) |
| `progFinish(e)` | read the result; sets `e.state` to `'ready'` or `'failed'` (blocks if not settled) |
| `progFree(e)` | delete a program entry's GL objects |
| `sceneWant(approach, eq, z0, n2, klein)` | cache key and source of one scene program |
| `sceneNow()` | the same for the current settings, remembered between frames |
| `sceneEntry(want, start)` | look a program up in `progs`, optionally starting it |
| `sceneAcquire()` | what the loop draws with: a ready entry, `'wait'`, or the reason `'formula'` / `'shader'` |
| `sceneWarm()` | prepare the next likely program ahead of time |
| `sceneDe()` | `S.q.de` as the shader's `uNT` (3, 1 or 0) |
| `sceneFail(why)` | show or hide the "did not compile" message |
| `stageClear()` | paint the stage colour before the first picture |
| `stageProgress(f)` | set the progress bar (`null` hides it) |
| `jobBegin()`, `jobCost(job)` | GPU timing of one preview or band |
| `bandTarget(exact)`, `prevTarget(exact, flat)` | how long a band / a preview should take, in ms |
| `kicked(bg, frame)`, `bandPoll()` | the loop's wake-ups: a frame or the background timer; the between-frames check of a band |

Removed: `makeProgram`, `sceneProgram` (nothing outside this file used them).

New fields of `R` (private; listed for tests): `ps2`, `rowExact`, `tq`, `q`, `dt`, `lastLoop`, `fast`, `par`,
`shown`, `painted`, `sig`, `want`, `hold`, `holdKey`, `busy`, `failed`, `bar`, `warmOn`, `warming`, `warmT`,
`compiles`. Useful in tests:
- `R.warmOn = false` stops programs being prepared ahead of time (do this before checking that a switch shows
  the busy label, otherwise the program may already be there);
- `R.compiles` counts programs started;
- `R.par = null` takes the path of a driver without parallel compile; `R.tq = null` (set it while idle) takes
  the clock-only sizing path.

State read: `S.flat`, `S.v2 {x, y, h}`, `S.cut`, `S.cutOn`, `S.mosaic`, `S.mosaicCell`, `S.view.bound`,
`S.view.fov`, `S.q {res, aa, steps, detail, stepk, smooth, normals, ao, shadow, de}`, and everything the baseline
read. No new state fields were added to `S`.

Element ids and classes: `#drawProgress`, `.draw-progress`. Busy key: `'compile'`.

## For the UI integrator

- **No markup is needed.** The progress bar is created by `initGL()`. Keep `#glfail` (with `hidden`) and
  `#status` in `body.html`; the renderer still writes to both.
- After changing any state call `touch()` (or `refresh()`), as before. That is all the 2D view, mosaic, drawing
  radius and distance-estimate controls need: the renderer reads `S.flat`, `S.v2`, `S.cut`, `S.mosaic`,
  `S.mosaicCell`, `S.view.bound`, `S.q.de` on every draw.
- `S.q.de` may be the number or the string 0 / 1 / 3. The "exact slope" choice (`S.q.normals === 'sharp'`) only
  takes effect when `S.q.de` is 3; with 1 or 0 the slope is sampled whatever the drop-down says. It is worth
  saying so next to the drop-down, or hiding "Surface detail from" unless the estimate is "exact".
- "Ultra fast" as in the spec: `{ res: 0.5, aa: 1, steps: 90, detail: 2, shadow: false, ao: false, de: 0, normals: 'smooth' }`.
  The other presets must set `de: 3` (and `normals: 'sharp'`) or they inherit the ultra-fast estimate.
- `pick(px, py)` in the 2D view returns `[x, y, S.cut]` for every stage position (never null).
- `renderIdle()` is now also true when the current setting failed to compile (nothing more will be drawn), so a
  test that waits for "done" returns at once and shot.py reports the console error instead of timing out.
- Status line texts: "Preparing the formula", "Preview while moving", "Drawing at full size",
  "Refining: pass k of N", "Done: N passes at W × H", "Nothing drawn: this setting did not compile".
- Optional: add `pick` (and `basis`) to `window.squaringLab` in `90-boot.js`. My picking tests use a test copy of
  the boot file (`out/render/90-boot-test.js`) only for that.
- When extending `tools/smoke.json`: a step that asserts the busy label appears on a switch must first set
  `window.squaringLab.R.warmOn = false`.

## Checks (all on `python build.py --name render --base base --use src/js/40-render.js src/css/40-render.css`)

The machine was shared with the other engineers' browsers (over 60 Chrome processes on one GPU), so durations
vary a lot from run to run. Frame gaps are the reliable figure.

- **Pictures.** `tools/smoke.json` (copied to `out/render/smoke-*.json` with other file names) on the baseline
  and on the new build: all six pictures identical pixel for pixel (`python notes/render_cmp.py out/render/base-smoke- out/render/new-smoke-`).
- **Longest gap between animation frames around a switch** (`notes/render_gaps.js`, warming off, 60 Hz):

  | Switch | Baseline | New renderer |
  |---|---|---|
  | approach to classic | 1330 ms | 17 ms |
  | equation to lambda | 3855 ms | 17 ms |
  | power 2 to 3 | 1239 ms | 17 ms |
  | mode to Kleinian | 481 ms | 17 ms |
  | click on an approach (page handler included) | 1670 ms | 37 ms, all of it the baseline's own click handler (scorecard) |
  | click on an equation preset | 1488 ms | 20 ms |

  The busy label was up for the whole compile (21 to 241 frames) and the progress bar ran to between 0.92 and 1.00
  before hiding. The longest single run of the drawing loop, in any test, was 5.4 ms. With everyone's live
  modules in one throwaway build (`--name render-all --base src`) the gaps were 17 to 29 ms in five of six
  runs; one run showed gaps of 300 to 500 ms that did not come back, including on a switch that compiles
  nothing, so I put it down to another process holding the GPU.
- **Warming** (`notes/render_warm.js`): 11 programs prepared in 32 s in the background with no frame gap above
  21 ms; afterwards approach, equation, power and mode switches needed 0 compiles and showed no busy label.
- **While moving** (two seconds, one camera change per frame, live shader snapshot): 101 to 119 previews in 120
  frames, preview GPU time about 10 to 12 ms, longest frame gap 20 ms, and the full drawing begins 182 ms after
  the last move.
- **New uniforms**, against a snapshot of the live `30-shaders.js` (`notes/render_newshader.js`,
  `out/render/sh-sheet.png`): drawing radius clips the solid, the three distance estimates, mosaic, 2D view of
  the Mandelbrot set, of the mosaic, of a Julia set and of the Kleinian view all draw.
- **2D picking** (`python notes/render_pick2d.py dist/render-sh.html`): centre and corner exact; 625 of 625
  grid points agree with the picture (inside where drawn solid, outside where drawn coloured).
- **Other paths** (`notes/render_paths.js`): 3D pick round trip 0.000 px; unreadable formula and broken shader
  show the message, clear the label and recover; without parallel compile the label is on screen for 2 frames
  before the one blocking compile; with animation frames paused the picture still finishes from the timer;
  after a lost and restored context the picture is identical; stage resize and resolution change redraw.
- **Sizing paths**: GPU timer, clock only, and clock only at 30 frames a second all finish with sensible bands
  (the last one draws 19 to 25 bands for 12 passes; the baseline rule would shrink to 2 rows there).
- Phone width, dark and light: `out/render/phone-sheet.png`. Light theme at load: `out/render/first-sheet.png`.

How to rerun: `python notes/render_run.py <page> <script.js> [--theme light] [--size WxH]`. Builds used:
`render` (as above), `render-t` (adds `--swap js/90-boot.js=out/render/90-boot-test.js`), `render-sh` (also
`js/30-shaders.js=out/render/30-shaders-snap.js`).

## Known limits

- While a new program is being prepared the picture does not follow the camera: the last picture stays until
  the program is ready. Warming makes this rare after the first few seconds on a page.
- Compile time itself is the driver's. On this machine one program took 1 to 10 s with the baseline shaders
  (the lambda preset is the slow one); the page stays live but the new picture waits that long the first time.
- On a driver without `KHR_parallel_shader_compile` the first use of each program still blocks once, and nothing
  is prepared ahead of time.
- Warming compiles up to about a dozen programs after each new equation or approach. It runs on the driver's
  own threads and only while the picture is finished, but it is real CPU work on battery.
- GPU work is not preemptible: a single preview that is far too large for a sudden change (say iterations typed
  from 14 to 400) can hold the GPU for a few hundred milliseconds once; the next preview is already resized.
- The 2D view's first full pass repeats what the full-size preview drew. Harmless, and it keeps one schedule.
- `EXT_disjoint_timer_query_webgl2` is absent in Firefox and Safari; they use the clock path (tested by
  clearing `R.tq`).

## Seen while testing, outside this module

- `src/head.html` loads the fonts with a plain `<link rel="stylesheet">`. The page's script waits for it, so when
  that request stalls the lab does not start: `tools/shot.py` printed "the page did not finish loading in 30 s"
  several times in about 60 runs, and in three of them `window.squaringLab` was still undefined when the first
  step ran. Loading the font sheet without blocking
  (for example `media="print"` switched to `all` on load) would remove this for users and for the tests.
