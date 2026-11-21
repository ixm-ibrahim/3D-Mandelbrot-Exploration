# Fix pass 7, export: "Save a picture" (export-1, export-2, export-3)

Files changed: `src/js/45-export.js` only (`src/css/45-export.css` is untouched).
Page: `python build.py --name r7-export --base base6 --use src/js/00-core.js src/js/45-export.js src/css/45-export.css`.
Scripts, logs and pictures: `out/r7/export/` (`drv.py` is the tester's driver with the page as an argument and
the places of long frame gaps added; `tl.py <page> <job>` is the tester's `a_sizes.py` reading of the time left;
`r_save.py <page>` is the tester's `runs.py refuse`, save part, on three fresh pages).

All timings below were taken on the shared GPU while the other engineers' tests were running (46 Chrome
processes at one point). The same 4K job took between 47 and 87 seconds from one run to the next, and single
tiles were 2 to 10 times slower in one run than in another. Read the numbers with that in mind.

## export-1 (major): the time left

Seen on `dist/v6.html` (`out/r7/export/v6-4k.log`): 4K Fine, 47 s in all; at 0.5 s "About 7 seconds left"
(true 46.5), 22 rises, said/true 0.13 to 2.55; the bar at 34% after 7% of the time.

What changed:

1. **Every tile is felt before any is drawn** (`exportFeel`). Thin strips across and down each tile (one every
   128 pixels, 2 pixels thick: 1/32 of one pass) are drawn as one background piece and timed, twice, and the
   cheaper reading counts (a third reading when the two disagree). The GPU's own count is used where it arrives,
   the clock less the cost of an empty piece otherwise. For 4K (40 tiles) this takes under half a second; the
   step line says "Working out how long it will take" meanwhile.
2. **The bar is the share of the felt cost that is drawn**, not the share of the pixels (`exportProgress`).
3. **The time left** is the felt cost still to draw times the pace of late. The pace is read only from the tiles
   the time goes into (the dearest, holding 85% of the cost, without the nearly empty stragglers of that list),
   as time over cost of the ones drawn last (half of the time those tiles have had, ten seconds at least), with a
   margin that starts at four tenths and ends at one tenth. Nearly empty tiles count by what the last eight took.
4. **No number until there is one worth showing:** not before two dear tiles are finished (or one has been
   drawn for 15 s), and not in the first 5 s of drawing. **It never goes up:** when the job is slowed the number
   waits (`job.left` is only ever lowered).
5. The words are no finer than the number: whole seconds under 20, fives to a minute, tens to 100 s, half
   minutes ("About 1½ minutes left.") to five minutes, then minutes (`exportLeftWords`).

Measured on the final design, 4K Fine JPG, opening picture (`r7e-4k.log`, strips, first calibration): 61 s in
all; first number at 9.8 s "About 40 seconds left" (true 51); said/true 0.73 to 1.44, median 0.97; no rises; bar
within 9 points of the share of time gone throughout (v6: 27 points off). Felt share against true share of the
time per tile agrees within about a half for the tiles on the solid (for instance 14.8/13.9, 15.7/15.2, 9.3/9.6,
9.7/13.8, 10.2/5.1 percent).

**The final page** (`r7-final5-4k.log`, 112 s in all, the heaviest outside load of the session, close to the
tester's 120 s): first number at 25 s "About 3 minutes left" (true 87 s, two times too long); 120 for a true 75;
80 for 63; then 40/58, 40/52, 35/41, 30/36, 30/30, 25/25, 20/19, 11/14, 6/8. Said/true 0.69 to 2.08, median 0.91,
no rises. The bar was within 7 points of the share of the time gone from start to end. Smoke test on that page:
42 steps, exit 0, no console errors (`out/r7/export/smoke.log`).

Earlier runs with the calibration variants, each under a different outside load: `r7-final-4k.log` (middle value
of the tiles' own answers): first number 70 s for a true 36, falling, no rises. `r7-final2-4k.log` (time over
cost, one tenth margin): 30 for a true 43.5, then waiting at 19 for 18 s. `r7-final3-4k.log` (fading margin, but
nearly empty tiles still in the calibration): first number 180 for a true 78, then 55. `r7-final4-4k.log`
(nearly empty tiles out of the calibration, pace of the whole job): 60 for a true 34 and 1.4 to 2.1 times too
long to the end, because the slow first tiles stayed in the pace; hence the pace of late.

What I learned, for whoever touches this next:

- **Small patches do not measure cost.** The first version felt 64 patches of 8 x 8 pixels per tile. A draw of
  64 pixels takes as long as its dearest pixel, so a tile with a thin spike read four times too dear and the
  first number came out 3.5 times too short (`r7d-4k.log`). Strips as wide as the job's own pieces fixed that.
- **The page slows its own job right after a change.** `sceneWarm` (40-render.js) prepares other formulas for
  20 s and more after a mode change or page load (`L.R.warming` was still true 20 s after switching to the
  Kleinian view). The same 2560 x 1440 Kleinian job took 4.5 s started at once and 2.4 s started 20 s later
  (`r7f-kfill.log`, `r7g-kfill-wait.log`). This is why the first five seconds give no number. If the renderer's
  engineer wants jobs to start faster: hold the warming back while `exportBusy()` or `meshBusy()`.
- With several programs on the GPU a nearly empty tile can take 1 to 3 s instead of 0.1 s (each of its seven
  pieces waits for a turn), so the pace must not be read from such tiles.
- Under a changing outside load no estimate can be right; the rule "never goes up" then shows as a number that
  waits. The margin is there to make waiting rarer; on a quiet machine expect the first number about a third
  too long, counting down a little faster than the clock.

Not measured: a quiet machine; 8K; Extra fine; a GPU without the timer extension (the clock path is reasoned
only); a job while the user drags the picture.

## export-2: after a save that throws, "Save the file" was dead

Seen on v6 (`v6-save.log`): message stays "The picture is ready.", uncaught "hook says no", the next press
hands over nothing (got 0), and every later answer of the host is ignored (0 calls).
Fix: `exportSave` clears `r.saving` in a `finally` and treats a throw like a failed save. With the new
`saveFile` nothing throws any more; the guard is for the day it does.
On my page (`r7-save.log`): "The file could not be saved. The picture is still here, so you can try again.",
no exception, next press with a working hook: "Saved as ...", got 1.

## export-3: "so you can try again" when trying again cannot help

Seen on v6: "Saving files is not available in this view. The picture is still here, so you can try again."
three times with one call of `use()`.
Fix: `exportSaveWords(out, r)` uses `out.again`:
- again true (declined, failed): message + " The picture is still here, so you can try again."
- rate_limited (its own message already says "Try again in a moment."): message + " The picture is still here."
- too_large for a PNG: message + " A JPG or WebP file of the same picture is much smaller."
- rejected_extension, extension_not_enabled: message + " Discard the picture and choose another file type."
- unavailable: the message alone.
Save and Discard stay after every one of them, and a later accepted save says "Saved as ...". A `use()` that
throws is asked again on the next press (three calls for three presses, the third saved).

## Not done

- Frame gaps at the very end of a job: looked at, not changed. In four 4K JPG runs there was one gap of 55 to
  60 ms right at the end (step "Writing the JPG file", after the job had ended: the small preview is drawn from
  the large canvas in one go). 8K and PNG were not measured. If it matters: draw the preview in bands, or tile
  by tile as tiles finish.
- The step at x = 2048 in the 4K Fine picture of the 2D view: not looked at.

## Names

New in 45-export.js: `EXPORT_FEEL` ([gap, thickness] of the strips), `exportFeel(job, piece, check)`,
`exportCost(tile)`, `exportProgress(job, force)`, `exportLeftWords(seconds)`, `exportSaveWords(out, result)`.
New fields of the job: `tiles` (one entry per tile: `x0 y0 tw th N n ms fin gpu clock felt w gMs gPx`), `t1`
(when drawing began), `told` (last time the progress was worked out). `job.left` is now -1 while no time can be
given (it was 0).
New step text: "Working out how long it will take". New test hook: `window.squaringLabExportTest = tiles => ...`
is called once per job, when the tiles are drawn, with what each tile was felt to cost and what it took.
No ids, classes or labels changed. The smoke test (`tools/smoke-v6.json`) passes unchanged.

## For whoever joins the files

- 45-export.js needs the new `saveFile` of 00-core.js (the `again` field); with the old one it falls back to
  the codes declined, rate_limited and failed.
- It uses `bgPiece`, `bgTarget`, `setScene`, `makeTarget`, `freeTarget`, `snapReady`, `sceneDe`, `halton`,
  `blitP`, `R.gen` from 40-render.js exactly as before; nothing new is asked of that file.
- The 3D model's save (46-mesh.js) has the same two faults in its own words; that is the mesh engineer's.
