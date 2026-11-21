# measure: the scorecard and the two "one step" figures (`src/js/60-measure.js`)

## What changed

1. **The scorecard no longer blocks.** `updateCard()` returns in 0.1 to 0.6 ms. It writes at once everything that
   needs no measuring (header, the whole "in the plane" column, the approach's own "crush" and "smooth" rows) and
   then measures the 6,000 directions about 4 ms at a time, one piece per animation frame. While it runs it shows
   `setBusy('measure', 'Measuring the approach')`, sets `aria-busy="true"` on `#card` and dims the four measured
   cells (the old numbers stay up dimmed; after an approach switch they are replaced by "Measuring…"). A newer
   call cancels an older one. The call may be made every frame: a stream of calls (closer than 150 ms apart) only
   starts measuring once it pauses, and the busy label only goes up once a measurement has outlived its first
   frame, so dragging or animating a dial does not make it flicker. Finished measurements are remembered (up to
   40, by approach, n and parameters), so going back to a state seen before is instant. In a background tab,
   where frames are paused, the measurement finishes in one go on a timer.
2. **`measure(F, n)` is still a plain synchronous function.** It and the sliced path run the same three functions
   (`measureBegin`, `measureSample`, `measureEnd`), so they give bit-identical numbers (checked, see below).
3. **Every sentence is right for any real n.** The "in the plane" column and both figure captions now have wording
   for whole n ≥ 2, n = 1, n = 0, 0 < |n| < 1, other fractions, and negative n (inside-out, the ring running the
   other way, nothing finite crushed, one over a polynomial, the tear along the negative x-axis for fractions).
   The measured cells use |n| where the old code used n (the old thresholds turned every negative power into
   "no upper limit"), say "except the origin" for negative n, and have wording for n = 0, for partial coverage
   (|n| < 1), for a mirror image without folds, and for a rule that keeps shapes (n = ±1).
4. **Offsets.** The approach texts are called as `crush(p, n)`, `smooth(p, n)`, `slice(ok, p, n)` and
   `roundNote(p, n)` (a string still works). The slice row has three states: "holds" when the plane z = 0 follows
   zⁿ exactly, "partly" when the measurement finds it lands on itself as k·zⁿ for one fixed complex k (what a turn
   offset gives, and also the classic Mandelbulb at n = 3, 7, −1 …), "fails" otherwise.
5. **Figures survive every n.** The 2D figure now draws zⁿ exactly as the shader computes it (angle between
   −180° and 180°), so for a fractional n the circle sitting on the negative x-axis is shown torn in two. Circles
   grow for |n| < 1 so what is left of them stays visible; a circle that shrinks to a point (n = 0) is drawn as a
   dot. The 3D figure skips points the rule sends to nothing usable (zero or infinite length) instead of drawing
   NaN. Both captions are written by this module (see "UI wiring").
6. **`drawStep3d` registers itself** on `hooks.view` from `buildCard()` (guarded), and skips the redraw when nothing
   it shows has changed (camera basis, curves, canvas size, theme, axis). A second registration is therefore
   harmless, just pointless.

## Names

Kept (contract): `buildCard()`, `updateCard()`, `buildStep3d()`, `drawStep2d()`, `drawStep3d()`, `measure(F, n)`,
`fmtN(n)`. Also kept from before: `powerF`, `fib`, `tangent`, `symEig3`, `tidy`, `PROPS`, `PILL`, `setCell`, `prep`,
`hueCol`, `arrow`, `ringAround`, `stepCurves`.

Added (all top level, all private to this file except where noted):

| Name | Meaning |
|---|---|
| `MEASURE_N` | 6000, the number of directions sampled |
| `MEASURE_AXES` | the three coordinate axes |
| `measureBegin(F, n)` | start a measurement: returns its running state |
| `measureSlope(f, d, e, h)` | slope of f at d along e, or null across a jump (also for NaN and infinity) |
| `measureSample(st)` | add one direction to the state |
| `measureRun(st, ms, most)` | add samples for about `ms` milliseconds, at most `most` of them |
| `measureEnd(st)` | finish: the plane check and the result object |
| `cardIdle()` | **for the UI and tests**: true when no measurement is waiting or running |
| `cardRun` | **for tests**: `{ cancel, last, shown, result, cache, slices, longest }`. `result` is the last measurement shown; `slices` and `longest` say how the last measurement was spread over frames (count; longest piece in ms); `cache` is a Map of finished measurements |
| `cardPlane(n)` | the six "in the plane" sentences for a power n |
| `cardSpace(a, q, n, m)` | the four measured cells as `[state, text]` for approach a, parameters q, power n, measurement m |
| `cardShow`, `cardStop`, `cardFrame`, `cardSet` | show a finished measurement; cancel one; next-frame-or-timer; set text if changed |
| `cardMinus`, `cardTimes`, `cardWhole` | "−" for "-"; "once" / "3 times"; is n a whole number |
| `CARD_MEASURED`, `CARD_SLICE_MS`, `CARD_SLICE_MOST`, `CARD_QUIET` | measured row ids; 4 ms per frame; at most 500 samples per frame; 150 ms pause that ends a stream of calls |
| `stepCaption2d(n)`, `stepCaption3d(a, n, anyFlipped)` | the caption sentences |
| `stepRadius`, `stepSize`, `stepDot` | sample-circle radius for a power; "3 times the size"; dot for a collapsed circle |
| `stepBuilt`, `stepDrawn` | counter bumped by `buildStep3d`; signature of what `drawStep3d` last drew |

`measure(F, n)` returns `{ lmin, lmax, smin, smax, smin8, smax8, round, rev, deg, sheets, used, plane, copy, turn, scale }`.
New fields: `smin8` / `smax8` the eighth smallest / largest stretch; `used` samples that counted; `copy` true when
the plane z = 0 lands on itself as k·zⁿ without being exact; `turn` the angle of k in degrees (−180 to 180];
`scale` |k|. Changed meaning: `rev` is the share of directions that land mirror-reversed **on the sphere of
directions** (the same thing the 3D figure dashes). For n > 0 that is what it always was; for n < 0 the old
whole-space test would have flipped every sample, because a negative power also turns space inside out.

No new fields in `S`.

## UI wiring (what 80-ui.js / 90-boot.js should do)

1. `refresh()`: delete the two lines that set `$('cap2d').textContent` and `$('cap3d').textContent`. `drawStep2d()`
   writes `#cap2d` and `buildStep3d()` writes `#cap3d`. (While those lines sit before `buildStep3d(); drawStep2d();`
   they are simply overwritten; moved after, they would put wrong text back.) Keep the element ids `cap2d`, `cap3d`,
   `step2d`, `step3d`, `card`.
2. `refresh()`: call `updateCard()` directly every time; `cardTimer` and `setTimeout(updateCard, 140)` can go.
   `updateCard()` copes with a call per frame by itself, and called directly it updates the plane column and dims
   the stale numbers at once instead of leaving them looking current for 140 ms. Keep the order
   `buildStep3d(); drawStep2d(); updateCard(); touch();`.
3. `boot()`: drop `drawStep3d` from `hooks.view.push(drawTriad, drawStep3d)`; `buildCard()` registers it (and
   the camera registers `drawTriad`). `buildCard()` must still be called once, after `readTheme()`.
4. `90-boot.js`: use `idle: () => renderIdle() && cardIdle()` in `window.squaringLab`, so `--wait-done` screenshots
   show the finished card, and expose `cardIdle` (and, if you want the timing test to run on the real build,
   `cardRun`, `updateCard`, `MATH`, `APPROACHES`).
5. Keep calling `drawStep2d()` on theme change and on resize, followed by `touch()` or `viewChanged()` as now
   (that is what makes `drawStep3d` run; it redraws only if something it shows changed).
6. Nothing to do for the busy label or the dimming: the label goes through `setBusy`, the dimming is an inline
   opacity on the four measured cells, and `#card[aria-busy="true"]` is there if you want to style it.
7. The sentence under the heading ("measured … by sampling its derivative over 6,000 directions") is still true.

## Known limits

- "No upper limit" is a judgement on samples: it is said when the largest stretch stands well above the eighth
  largest (a spike that more samples would push higher) or exceeds 30·max(|n|, 1). Bounded maxima in this lab stay
  under about n². A very slow blow-up (for example n = 0.9, where the stretch grows like distance^−0.1) is
  reported with the largest sampled value.
- The lower end of the stretch range shows the eighth smallest sample when the smallest stands apart from it:
  a difference taken across a mirror crease (several planes) can undershoot by up to about a quarter.
- A `roundNote` is left out when the row holds and the approach gives the same note at n = 2, 2.5 or 3 (there it
  describes the failure). This is what keeps "The squash is in the spin direction." off the n = 1 card.
- |n| < 0.005 is treated as n = 0 in the wording (it also prints as 0).
- `rev`, `deg` and `sheets` skip samples that straddle a tear, as before.

## Checks (all scripts in `out/measure/`, run through `notes/measure_steps.py`)

Builds: `dist/measure.html` = baseline + this file; `dist/measure-apr.html` = the same plus a snapshot of the new
approaches (`out/measure/approaches-snap.js`, `formula-snap.js`); both with `out/measure/boot-test.js` in the boot
slot, which adds `window.squaringLab.T`.

```
python build.py --name measure --base base --use src/js/60-measure.js --swap js/90-boot.js=out/measure/boot-test.js
python notes/measure_steps.py dist/measure.html out/measure/quick.js out/measure/timing.js out/measure/behaviour.js
python notes/measure_steps.py dist/measure-apr.html out/measure/quick.js out/measure/direct.js out/measure/sweep.js
python notes/measure_steps.py dist/measure-apr.html out/measure/variants.js out/measure/texts.js   (pipe through notes/measure_unpack.py)
```

- `timing.js` (results in `final-base.txt`, `final-apr.txt`): `updateCard()` returns in 0.1 to 0.6 ms; 12 to 16
  pieces; longest piece 3.1 to 4.5 ms; longest gap between animation frames 16.7 to 17.2 ms; finished after 200 to
  270 ms (one blocking `measure()` takes 25 to 50 ms here); the result equals `measure()` field for field
  (`Object.is`) for all five approaches at n = 2, 3, −2, 8, 2.5, −3, 0.5.
- `behaviour.js` (20 checks, all pass): cancel, stream of calls, cache, waiting look, single hook registration,
  redraw guard.
- `sweep.js`: 224 cases (5 approaches, 16 powers from −8 to 10, offsets) through the real page: 415 different
  sentences, none with NaN / undefined / Infinity / a plain "-" / an empty cell, every pill filled. Longest gap
  between frames 18.8 ms when only this module's functions are called. Through `refresh()` on the baseline
  renderer there are gaps of 1 to 4 s whenever a new shader is compiled: that is the renderer's blocking compile.
- `texts.js` → `texts-apr.txt`, `texts-base.txt`: every sentence for every approach and power, read through.
- `waiting.json`: the waiting state photographed (`waiting-stage.png`, `waiting-card.png`); a simulated
  background tab finishes in one piece.
- Pictures: `fig-n-2.png`, `fig-n-1.png`, `fig-n0.png`, `fig-n0.5.png`, `fig-n-0.5.png`, `fig-n2.5.png`, `fig-n-8.png`,
  `light-turn.png` (light theme, one plane, turn 30°, n = −2), `phone-turn.png` (375 px), `all-lower.png` (built with
  every module as it stood in `src/` at the time).
- `out/measure/smoke.json` (the smoke sequence with its pictures under `out/measure/`): no console errors.
