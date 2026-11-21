# Round 9, engineer "klein" (`src/js/25-colour.js`, `src/js/30-shaders.js`, `src/js/40-render.js`)

Started 05:30, last source change 06:23, last test and notes about 06:40. Scripts, logs and pictures: `out/r9/klein/`.
Test page: `python build.py --name r9-klein --base base8 --use src/js/25-colour.js src/js/30-shaders.js src/js/40-render.js`.
Compared with `dist/v8.html`. Every claim says whether it was **measured** or **reasoned**.

## State in one paragraph

kleinian-1 is **partly** cured, by another change than the one the assignment describes. The assignment's cure was
built and judged first: it fills the picture with huge balls, and limited to the slides alone it makes the tester's
entries worse (pictures below). On the way the cause of the largest fault showed: the "very large sheets that run
out of the picture" and the fan of spikes are the trap shape itself, coming into the solid two steps late. That is
fixed: the sheets are gone on every scene I drew. What is left of kleinian-1 is the smaller part: some balls on
leaning groups are still cut open with a flat or jagged face, and a fringe of stripes remains at the lower left of
entry 3. The note beside the choice is still true and is unchanged. solids-5, words-4 and words-5 were not started.
The two small things in `40-render.js` are done. All 67 pictures of the lists that must not change are identical to
`dist/v8.html` (largest channel difference 0).

## Item 1, kleinian-1

**Reproduced on v8** (measured): `out/r9/klein/ref/k01..k07` (entries 3 and 24, Is the solid and Is added, Balanced,
Fine, zoomed out), sheet `before-k-a.png`. Sheets across the left of the picture, sliced balls, the fan of spikes
when zoomed out; entry 0 with the trap centre at x = 0.6 has blue sheets from top to bottom (`k10`).

**The assignment's cure, built as written** (measured, `var/30-D-turn-next.js` is the code, `t1-pairs-a.png` and
`t1-pairs-b.png` the pictures, v8 above, the cure below): the trap tested at the point and at its images under the
slides by 2, by 2L and the half turn, nearest wins, the touch record in step. Every scene turns into a few huge
balls that fill the stage; entry 0 and entry 21 lose their lace behind them; entry 0 with x = 0.6 is a black stage.
Reasoned, and it fits: the map of the search carries the half-turned copy of the sphere shell (radius 1, at the
origin) exactly onto the shell itself. So with the half turn among the images, "one step after the start" is the
trap shape itself again, whatever the skip dial says, and the shell of radius 1 is as large as a copy of the pattern.

**Limited to the nearest images, the slides only** (measured, `var/30-A-slide-next.js`, `var/30-B-slide.js`,
`vA-vB-pairs.png`): entries 0 and 21 look as in v8, entries 3 and 24 get worse (larger sheets with saw-tooth
edges), entry 0 with x = 0.6 keeps its sheets.

**A model in the plane** (`out/r9/klein/model.py`, `model/sheet-e03.png`, measured in the model only): with the
trap and all its images, plus the map applied to the neighbours across each edge, every circle of the pattern is
whole. So the idea is sound for the pattern; it is the picture that it fills.

**What the sheets are** (reasoned from the search, then confirmed by the pictures). The search comes to rest in a
cycle of two points. For a point that is already at rest, step 2 is the starting point again, half turned about
μ/2 or slid by 2. The skip dial left out step 0 only, so at step 2 the trap shape itself was tested after all, in
its half-turned copy. Where both leans are 0 that copy lies wholly in the upper half of the pattern, which the
search never visits, and nothing shows. In a group that leans, the dividing line is wavy, the half-turned shell
reaches under it, and that part came into the solid as a huge piece cut off along the edges of the copy.

**Done** (`kde` in `30-shaders.js`): a step that only comes back to a step that was skipped is skipped as well.
The search keeps the point as it lay in its copy one and two steps back; step i is left out when i is below the
skip count, or when the point is where it was two steps before and that step was left out. For this the trap test
moved from the end of a turn (the point after the map) to the start of the next (the same point, `z0`), and the
search keeps the record of the touching step itself (`gTouch`, `gTouchIt`, `gTouchS`, `gTouchStr`), so the colours
never come from a step that is not in the solid. The colour module's own record is compiled out of the Kleinian
program (`#if TRAP_SOLIDS && !COL_KLEIN`).

**Measured on the final page** (`out/r9/klein/t4/`, 47 Kleinian scenes at 1400 x 950, no console errors; pairs v8
above, final below):
- `t4-pairs-a.png`: entries 3 and 24, Is the solid and Is added, Balanced and Fine: the sheets are gone; zoomed out
  (`k07`) the object is compact, no fan of spikes; entry 0 with x = 0.6 (`k10`) has no sheets and stays in the frame.
- `t4-pairs-b.png`: entry 0, entry 21 and the three Kleinian examples look as before, less a stray thin disc
  between the two front balls; entry 33 (`k14`) loses the sheet over its upper left.
- `t4-pairs-c.png`: all trap shapes on entry 0 at Balanced (planes and ring also at Fine) as before; planes and ring
  on entry 3 lose their sheets; skip 0 now colours the trap shape by where it was touched (it was one flat colour).
- **Still wrong** (`crop-k01-e03-is.png`, v8 left, final right, full size): the ball at the top right is cut open
  with a jagged hole, and the fringe of stripes at the lower left is smaller but there. On entry 24
  (`crop-k02-e24-is.png`, same layout) the sheet that hid the right half is gone, and behind it stand a dome with a
  torn hole and a jagged rim, and the green ball still sliced open. This is the part the last engineer described:
  a piece that reaches across the edge of a copy. Not counted; on the sheets it is one to three balls a scene.
- **Changed meaning to know about**: with 3 steps skipped, entry 3 used to show the same large balls as with 1
  (they came back through the cycle); now it shows what the help text says, the finer pieces only, and they are
  sparse fragments (`k62` in `t4-pairs-c.png`). Not judged further.

**Not done**: the remaining cut balls. What I would try next (reasoned): keep this change, and add the map applied
to the neighbours across each edge for the trap alone (no images of the trap), which the plane model says closes
pieces at the last level; then look again.

## Item 2, solids-5: not started

The reference pictures exist (`ref/p01..p12`, the tester's scenes of `pj.json` set through the state) and are
unchanged on the final page (identical). Reasoned only: making a layer go as a whole means scaling its thickness
by a factor that depends on the step alone, and the per-pixel rule has to stay beside it or walls under a pixel
come back as scratches; that changes every trap solid and needs its own round of pictures.

## Item 3, small things in `40-render.js`: done

- **No other formulas are prepared while a picture job or a model job runs** (`bgJobBusy()`, asked at the top of
  `sceneWarm`). Measured (`repro3-warm.json`, a Fine picture job at the default size started at once on a fresh
  page; `repro3-warm-v8.log`, `repro3-warm-r9-klein.log`, `repro3-warm-again.log`): programs started while the job
  ran: v8 12, 12 and 13; final page 0, 0 and 0, and two more within 4 s after the job. **The saving in time did not
  measure**: the job took 32.1, 43.2 and 41.5 s on v8 and 52.3, 41.1 and 35.2 s on the final page, on a GPU shared
  with ten others.
- **`idle()` is false while the graphics are away in the middle of a picture** (`R.lostMid`). Measured
  (`repro3-lost.json`, logs `repro3-lost-v8.log`, `repro3-lost-r9-klein.log`): context lost during pass 2 of 24:
  v8 `idle()` true, final page false; after the graphics came back and the picture was drawn again, true on both.
  Lost under a finished picture: true on both, as before. A setting changed while the graphics are away: false on
  both until the picture is drawn.

## Item 4, words-5 and words-4: not started

Reference pictures `ref/w01..w05`, identical on the final page.

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `out1`, `out2` | locals of `kde`, `30-shaders.js` | the step one turn back, two turns back, was left out of the trap test |
| `kd1`, `kd2` | locals of `kde` | the point as it lay in its copy of the pattern one and two steps back |
| `outNow`, `dq`, `sc` | locals of `kde` | this step is left out; its distance to the trap; its score |
| trap test in `kde` | `30-shaders.js` | moved to the start of a turn: it tests `z0`, the point as the last map left it, with `DF` and `it` of that step. The point after the very last turn of a search that runs out its count is no longer tested |
| `gTouch`, `gTouchIt`, `gTouchS`, `gTouchStr` | written by `kde` | the Kleinian search keeps the touch record itself, step 0 included |
| `trapAdd`, touch record | `25-colour.js` | compiled only with `TRAP_SOLIDS && !COL_KLEIN` (it was `TRAP_SOLIDS`) |
| `R.lostMid` | `40-render.js` | the graphics went away while a picture was being drawn or was due |
| `renderIdle()` | `40-render.js` | false while `lost && R.lostMid` |
| `bgJobBusy()` | `40-render.js` | a background piece is in flight or queued, or `exportBusy()` or `meshBusy()` says so |
| `sceneWarm()` | `40-render.js` | looks again in half a second while `bgJobBusy()` |

No uniform, control, state key, program key or text on the page changed. `de()` still has one call site,
`pixelColour` is still called once, `trapDist` has two call sites in `kde` as before.

## Measurements

- **Pictures that must not change** (measured; `python out/r9/klein/scenes.py shoot v8 ref` at 05:41 to 05:44,
  before any source change; `... shoot r9-klein final f g s p w` on the final build; `cmp-fixed-final.log`): 67 of
  67 identical, largest channel difference 0. They are 22 pictures of the 2D view and of 3D pictures not coloured by
  a trap (f), 11 trap-coloured 3D pictures of the three modes at Balanced, Fine, Fast and Ultra fast (g), 17 trap
  solids of Mandelbrot and Julia sets, the six examples among them (s), the 12 scenes of solids-5 (p) and the 5 of
  words-4 and words-5 (w).
- **Kleinian trap solids**: all 47 scenes differ from v8, as meant (`python out/r9/klein/scenes.py cmp ref t4 k`).
- **Smoke test** (measured, `smoke-final.log`, 06:31, on the final page): `tools/smoke.json`, 52 steps, exit 0, no
  console errors. Its Kleinian trap solid step reads 12 of 49 probes hit.
- **Compile and drawing times** (measured, the GPU shared with ten others; all in ms).
  `perf-final.log` (`python out/me/perf.py base4 r9-klein base4 r9-klein base4 r9-klein`, 06:31 to 06:35):

  | Page | M compile | M draw | J draw | K compile | K draw |
  |---|---|---|---|---|---|
  | base4 | 2024, 2138, 3471 | 766, 1082, 1466 | 1768, 2019, 1033 | 737, 742, 667 | 223, 306, 115 |
  | r9-klein | 2667, 2556, 2803 | 1663, 1463, 1252 | 2106, 470, 2049 | 958, 987, 933 | 97, 145, 333 |

  `perf-final-2.log` (`python out/me/perf.py v8 r9-klein v8 r9-klein`, 06:36 to 06:38):

  | Page | M compile | M draw | J draw | K compile | K draw |
  |---|---|---|---|---|---|
  | v8 | 3258, 2931 | 859, 376 | 1167, 607 | 812, 925 | 614, 232 |
  | r9-klein | 2638, 2671 | 389, 373 | 463, 839 | 925, 1256 | 170, 299 |

  By the rule (least of the three visits of the first run): compile M 2556 (limit 2600), K 933 (limit 1100): met,
  M only just, on a machine where base4 itself read 2024 to 3471 and v8 2931 to 3258 in the same minutes (quiet
  values 1.5 and 1.75 s). Draw against base4: J 470 against 1033 and K 97 against 115 are within a quarter; **M 1252
  against 766 is not, in that run**. In the second run M draws in 373 and 389 against v8's 376 and 859. Reasoned:
  the programs of the opening pictures are the same as v8's once the compiler has dropped what is switched off
  (every change in the shader text lies inside `#if TRAP_SOLIDS`, which is 0 there; `src-diff.txt` is the whole
  difference to base8), and their pictures are identical, so the first run's M reading is the load, not the page.
  A run on a quiet GPU would settle it.
- The page tested is the page built from the three files as they stand (`out/r9/klein/r9-klein-as-tested.html`
  is byte for byte `dist/r9-klein.html`; the files' line endings were put back to base8's after the tests and the
  build did not change by a byte).

## Sheets to look at (all in `out/r9/klein/`)

1. `t4-pairs-a.png`: the tester's scenes, v8 above, final below. Look for the sheets on the left and right, and the
   zoomed-out picture.
2. `crop-k01-e03-is.png`: what is still wrong, at full size.
3. `t4-pairs-b.png` and `t4-pairs-c.png`: entry 0, the three examples, the trap shapes, skip 0 and skip 3.
4. `t1-pairs-a.png`: the assignment's cure as written (below) against v8 (above): the stage full of balls.
5. `model/sheet-e03.png`: the plane model. Top left v8 (open arcs), bottom right the full cure (whole circles).

## Closing text (`src/body.html`, not mine)

1. "This works in Mandelbrot and Julia pictures, and in Kleinian pictures whose group does not lean: both leans of
   μ, its real part and its j part, at 0, and the trap centred on x = 0 and z = 0. In a leaning group some pieces
   come out cut open, with flat faces, and a note beside the choice says so. That fault is not cured yet."
   Still true as far as it goes. Suggested: "This works in Mandelbrot and Julia pictures and in Kleinian pictures.
   In a Kleinian group that leans (the real part or the j part of μ not 0), or with the trap centre off x = 0 and
   z = 0, a few balls still come out cut open, with a flat face, and a note beside the choice "In the 3D view the
   trap" says so. The large sheets that used to run out of such pictures are gone."
2. "Higher numbers peel the large outer pieces away." Now also true in the Kleinian view, where the large balls
   used to come back. No change needed.
3. Nothing in the closing text speaks of `idle()` or of preparing formulas during a job.

## Risks

- Every Kleinian trap solid changed a little (a stray thin disc gone on entry 0); judged on sheets at 0.3 to 0.42
  of full size and one crop at full size, by me, in one pass.
- With 2 or more steps skipped a Kleinian trap solid is now much sparser than in v8.
- A 3D model of a Kleinian trap solid uses the same search and was not made or compared.
- The time a picture job saves by the stand-back of `sceneWarm` was not shown by my runs.
- While a job runs, a program that was already being prepared stays in `R.warming` until the job ends.
