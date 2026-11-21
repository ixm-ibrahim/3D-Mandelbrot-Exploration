# fix-render: what changed in `src/js/40-render.js` after the testers' round

Only `src/js/40-render.js` was edited (`src/css/40-render.css` is unchanged). Every name in the contract still works.
Test page: `python build.py --name fix-render --base base2 --use src/js/40-render.js src/css/40-render.css`.
Scripts, logs and pictures: `out/fix/render/` (`run.py` runs a page script with the tracing hooks in `trace.js`;
`e1.js` drag rate, `e2.js` job-by-job trace of a full drawing, `e3.js` busy label / clock path / background path,
`e4.js` preview against finished brightness, `e5.js` preparing programs ahead).

All timings below were taken on a GPU shared with five other engineers, base2 and the new file back to back.

## What changed, by defect

**perf-3, pictures while dragging.** A finished preview was only looked for at the next animation frame, and the
preview was sized to cost 70% of a frame, so preview plus hand-over often missed that frame and every second frame
showed nothing new. Now the 3 ms between-frames look (`bandPoll`) runs for previews as well as bands, and a preview
is sized to 55% of a frame (at least 8 ms), so it is drawn, noticed and on the canvas before the next frame.
Baseline traces here showed previews noticed after 33 ms for 11.5 ms of GPU work; now 14 ms for 9.2 ms.
Drag at Fast and Balanced: 59 to 60 pictures a second (3D), Ultra fast 56, 2D view 50 to 60.

**perf-2, the fixed 170 ms wait.** The wait before the full-size drawing now depends on what the first pass will
cost (judged from the last preview): `clamp(first pass ms, max(30, 2.2 frames), 170)`. A timer ends the wait
exactly instead of at whichever frame follows. The first band is sized from the same estimate, so a cheap picture
is one band. In the 2D view a full-size preview is drawn with the final settings and is kept as the first pass
(copied into the full-size target), so nothing is drawn twice. Ultra fast, one small move from rest: finished after
61, 62 and 66 ms (baseline 200 to 300 ms in the tester's report); 2D view at Ultra fast 33 ms after a drag (baseline 182).

**perf-1, erratic full-quality speed.** Three changes to the band schedule:
- a band never has fewer than height/32 rows (`bandFloor`), also when timed by the GPU, and may shrink by at most
  0.6 per band (was 0.2, down to 2 rows);
- when bands are timed by the GPU and cost no more than 1.5 targets, two are kept in flight (`R.pend`, `R.pend2`),
  each about half a frame, so the GPU never waits for the page between bands;
- the first band is sized with a factor learnt from each first pass (`R.gain`) instead of a fixed 3.
Default view at Balanced, one small move, alternating pages: baseline 2.97, 4.70, 2.05, 3.81 s; new 1.69, 2.00, 0.77,
1.24 s. The GPU's own count of the same 12 passes fell from 1.4 to 2.8 s to 0.4 to 0.7 s, which fits a GPU that
slows its clock when it is left idle between bands. **Not reproduced:** the 20 to 30 times collapse itself (bands
stuck at 2 rows) never happened on this busy GPU, so that part is fixed by reasoning: a band that looks slow can no
longer be answered with ever smaller bands, and the GPU is kept busy. It needs one run on a quiet GPU
(`python out/fix/render/run.py dist/<page>.html out/fix/render/e2.js --argfile out/fix/render/arg-lambda-fast.json`
prints rows, GPU ms and wall ms per band).

**perf-4.** The "Preparing the formula" label now stays until the first picture drawn with the new program has
come back (`R.busyP`), not until the program is merely ready. Switch to an approach not shown before: label up
13 to 1711 ms, first preview on the canvas at 1705 ms, no time without an indicator.

**perf-5.** Programs are prepared ahead from 500 ms after the first pass of any picture and while it is refined
(it used to need a finished picture). It stands back while the picture is moving or its own program is being
prepared. During a Fine drawing still at pass 26 of 32, four programs were prepared with no frame gap above 17 ms;
afterwards an approach switch needed 0 compiles and showed no label.

**p1-1.** While the picture waits for a program the renderer puts its label back in front whenever another task's
label has replaced it (the corner shows the task raised last; `00-core.js` is frozen). During a switch only
"Preparing the formula" was seen.

**p4-3.** The ray-marched preview is now lit like the finished picture (shadows and crevice shading when the
quality setting has them), and a first pass that will be over within about 250 ms replaces the preview in one go
instead of strip by strip (`R.quick`). Preview against finished brightness: Balanced 40.4 / 36.9 before, 38.2 / 36.9
now; Fast 41.0 / 38.8 before, 40.5 / 38.8 now. Price: the moving preview is 19 to 25% smaller across at Fast and
Balanced (same cost per frame).

**text-17.** Failure texts: "This combination of approach and equation could not be prepared on this device. Try
another approach or equation." and status "Nothing drawn: these settings could not be prepared".

## Not changed

- perf-6 (small preview at Fast, Balanced, Fine): the preview still uses the chosen distance estimate, as the spec
  says. A cheaper estimate for the preview is one value in `preview()` (`nt`), but it changes the outline while
  moving and depends on the rough and one-neighbour estimates being fixed in `30-shaders.js` first.
- Everything about what the shader computes (p5-*, p8b-*, p9-*, p11-1, p15-*) belongs to `30-shaders.js`.

## Names

New fields of `R`: `pend2` (second band in flight), `pipe` (two bands may be in flight), `quick` (first pass shown
whole), `gain` (full row cost over preview row cost, learnt), `rowPrev` (preview row cost), `p0` (first pass under
way: `{ ms, rows, row }`), `busyP` (the program the busy label waits for).
New functions: `bandFloor()`, `busyOff()`, `warmSoon(ms)`, `drawDone()`, `jobDone(job, cost)`.
Changed: `prevTarget(exact)` takes one argument; `bandTarget` and `prevTarget` values; `fence(job)` files the job as
`R.pend` or `R.pend2`; jobs carry `P`, and bands also `rows`, `p0`, `last`, `show`, `behind`.
No new state in `S`, no new uniforms, no new elements or classes.

## For the next person

- `setScene()` is still the one place where uniforms are set, and it still reads `S`, `theme`, `basis()` directly.
  A background job with frozen settings needs it to take those from an argument.
- `renderIdle()` is unchanged in meaning. With two bands in flight "Done" is said when the last one comes back.
- `ensureTargets()` now runs before a preview and at the start of a drawing (every size change calls `touch()`).
- Pictures are unchanged: 18 of the 19 smoke pictures are identical pixel for pixel to base2 (`python notes/render_cmp.py
  out/fix/render/base-smoke- out/fix/render/new-smoke-`); the other is the fly-camera step, which moves by the clock.
- `tools/smoke.json` on `dist/fix-render.html`: exit 0, no console errors.
- Tests that count compiles or look for the busy label should still set `R.warmOn = false` first; warming now
  starts earlier.
