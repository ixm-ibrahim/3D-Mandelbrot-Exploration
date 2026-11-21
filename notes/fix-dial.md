# fix-dial: what changed in the controls kit in the fix round

Files changed: `src/js/70-dial.js`, `src/css/70-dial.css` (the two the dial group owns), plus the kit's own
regression tests `tests/dial.html`, `tests/dial.json`, `notes/dial_real.py`, and `notes/dial.md`.
Scripts, logs and screenshots of this round: `out/fix/dial/`. Test pages: `dist/fix-dial.html` (base2 + the two
kit files) and `dist/fix-dial-x.html` (the same plus throwaway copies of three files of other groups with the
"other side" filled in, see the end).

## 1. Extreme values (new from the user)

The user asked for a button that allows much higher values (deeper Kleinian searches, more iterations). The kit's
side:

- A dial spec or `addDial` opts may carry `xmin`, `xmax` (slider range while extreme values are on) and `xlo`,
  `xhi` (typed limits while they are on). Any of the four may be missing, and then the normal value stays.
  One deliberate refinement: if `xmin` or `xmax` is given without the matching `xlo` or `xhi` and reaches beyond
  the normal typed limit, the typed limit moves out with the slider. Without that, `{ xmax: 1000 }` on a dial
  whose typed limit is 400 would leave the slider's upper part dead.
- `setExtreme(on)` switches every existing and future dial that has such a range. `isExtreme()` reports the switch.
- Switching off brings any value beyond the normal typed limits back to the nearest normal limit and calls the
  dial's setter, so the picture follows. Spec-built sets get one `onChange` however many of their dials move.
  A value inside the typed limits but beyond the normal slider is left alone (hollow thumb, as before).
- The flag lives in `S.extreme` (the orchestrator has added that field to `src/js/00-core.js`). `setExtreme`
  writes it and `isExtreme` reads it, so there is one copy. Because a dial compares its range with the flag every
  time it shows itself, `S.extreme = x; syncControls()` (a restored or undone state) also moves the ranges. A sync
  never writes a value; only `setExtreme(false)` pulls values back. Where there is no `S` (the kit's test page),
  or `S.extreme` is undefined (base2), the kit keeps the flag itself until `setExtreme` is first called.
- A dial whose range is widened shows a small tag, "wide", in front of its box cluster: brass, 10.5 px, condensed
  capitals, tooltip "Extreme values are on. The slider runs from A to B, and typed values go from C to D."
  Contrast of brass on the panel: about 5.4 in the light theme, 8.4 in the dark one. The typed box's tooltip and
  `aria-valuemin/max` follow the range in use.
- Typing, the step buttons, the whole-number toggle, the slider, `sync()`, `reset()` and play all work on the
  range in use. A sweep that is playing when the switch changes carries on inside the new range.

## 2. p14-1 (major): playing Lift snapped from one end to the other

Cause: the sweep always wrapped from the top of the slider to the bottom. That is right for an angle and wrong for
a value whose two ends give different pictures.
Fix: `animate: 'bounce'` sweeps there and back (8 seconds each way, turning round at both ends, no jump). The
sweep now keeps a phase that folds back, so a there-and-back sweep is the same code path as the wrap.
`animate: true` and `animate: <seconds>` behave as before.
Not finished without the other side: the Lift spec is in `src/js/10-approaches.js` and still says `animate: true`.
See "What the others must do".

## 3. p2-1 (minor): eight dials with a step of 1 kept their fraction (35.49, 36.49, 37.49)

Cause: a dial whose own step is 1 had no toggle, and its arrows added exactly 1.
Fix: such a dial (step 1, not `int`) now has the toggle like every other dial that can hold decimals. Its two
choices are "±1" (to the next whole number) and "±0.1", and it starts on "±1". So Field of view goes 35.49, 36, 37,
and a paused sweep value of 34.2 goes to 35. 0.1 is the resolution a sweep on such a dial produces, which is why
it is the finer choice. Dials that hold whole numbers only and step by 1 (`int`, `odd`) still have no toggle.

## 4. p13-4 (minor): collapsing a section stopped a playing sweep for good

Cause: the sweep stopped whenever the dial was not drawn, and a dial in a closed section is not drawn.
Fix: a sweep stops only when the dial is hidden for real: the `hidden` attribute or `display: none` on it or on
anything above it (a `when` rule, another approach's panel, a section of another mode). A closed `<details>` is
only folded away, so the sweep plays on, and is still playing when the section is opened again.
`dialVisible` (private) is replaced by `dialGone`.

## Names added or changed

- `setExtreme(on)`, `isExtreme()`: top-level functions, see 1.
- `dialExtremeOwn`: private top-level variable, the flag where there is no `S.extreme`.
- `dialGone(el)`: private top-level function; replaces `dialVisible` (removed, no other module used it).
- Spec and opts fields: `xmin`, `xmax`, `xlo`, `xhi`; `animate: 'bounce'`.
- Control object of a dial: `rerange(pull)`, called by `setExtreme`.
- Elements and classes: `<span class="dial-wide" id="<id>Wide">` (only on dials with a wide range, `hidden`
  while not in use); class `is-wide` on the `.dial` while its wide range is in use; the step toggle
  `<id>Step` now also exists on step-1 dials that can hold decimals (viewFov, lightAz, lightEl,
  par-mercator-turn, par-bulb-lat, par-bulb-lon, par-classic-theta, par-classic-phi).
- State: `S.extreme` is read and written by the kit (the field itself was added to 00-core.js by the orchestrator).

## What the others must do

1. approaches, `src/js/10-approaches.js`, `APPROACHES`, id `'mercator'`, params, the spec with `key: 'lift'`:
   change `animate: true` to `animate: 'bounce'`. Until then Lift still snaps once per sweep. The five degree
   dials and the colour shift keep `animate: true` (they are periodic).
2. ui, `src/js/80-ui.js`: add the switch, for example in the top row next to the 2D view box:
   `addCheck('flatHost', 'extreme', 'Extreme values', isExtreme, setExtreme, { def: false });`
   and give wide ranges to the dials that should have them, for example
   `iter`: `{ hi: 400, xmax: 1000, xhi: 100000, int: true, ... }`,
   `kiter`: `{ hi: 400, xmax: 2000, xhi: 100000, int: true }`,
   `qsteps`: `{ lo: 20, hi: 3000, xmax: 5000, xhi: 20000, int: true }`.
   The numbers are the page's choice; these are the ones tried on `dist/fix-dial-x.html`. The shader loops run
   to a uniform, so there is no fixed cap in the shader, but nobody measured how slow very high counts are.
   If a preset or reset must leave extreme mode, call `setExtreme(false)`, not `S.extreme = false` alone
   (only `setExtreme` pulls values back).
3. ui, `src/js/90-boot.js`: add `setExtreme, isExtreme` to `window.squaringLab` so tests can reach them.
4. ui, optional (the tester's side remark in p2-1): `UI_FOV_DEG` is 35.49, so Field of view starts on a fraction.
   With the new step rule the first press of an arrow lands on 35 or 36; a whole default would look tidier.

## Tests

- `python tools/shot.py --url tests/dial.html --actions tests/dial.json`: 71 checks, all pass (59 before). Two
  old checks asserted the old behaviour and were rewritten (no toggle on step 1; a closed section pauses a sweep);
  twelve are new: the step-1 rule, folding a section, the there-and-back sweep, and nine for extreme values
  (ranges, missing fields, pulling back, future dials, the tag in both themes, steps and toggle and sync and
  reset in both states, play across the switch, specs and one onChange, `S.extreme` with `syncControls`).
  The layout check now measures every column (343, 320, 295, 240 px) with the tags hidden and shown.
  New pictures: `out/dial/showcase-extreme.png`, `out/dial/showcase-extreme-other-theme.png`.
  The files as they were before this round: `out/fix/dial/dial.html.before`, `dial.json.before`.
- `python notes/dial_real.py --lab=dist/fix-dial.html` (real mouse, keyboard, touch): 42 lines, all pass,
  including the 71 checks in a focused desktop window and on an emulated 375 px touch phone. Two of its lines
  were adjusted: the tab order of the Turn dial now passes its new toggle, and the "below the slider" check reads
  the Power slider's lower end from the page (it was written for the baseline page, where that end was 2).
- `python tools/shot.py --url dist/fix-dial.html --actions out/fix/dial/repro.json`: the three reported defects
  before and after (p2-1 and p13-4 fixed on this page; p14-1 needs the Lift spec).
- `python tools/shot.py --url dist/fix-dial-x.html --actions out/fix/dial/lab-x.json`: the kit inside the lab with
  the other side filled in: Lift turns round at 2 (largest change between samples 0.017, was 3.98), the switch
  widens Iterations, Ray steps, Lift and the Julia c dials, switching off pulls Iterations 640 back to 400 and c
  55.5 back to 8, and `S.extreme` plus `syncControls()` moves the ranges without writing.
  Pictures: `out/fix/dial/lab-x-eq-dark.png`, `lab-x-approach-dark.png`, `lab-x-phone-light.png`.
- `python tools/shot.py --url dist/fix-dial.html --actions tools/smoke.json`: exit 0, 20 steps, no console errors
  (log: `out/fix/dial/smoke.log`).

## How dist/fix-dial-x.html is made

`python out/fix/dial/mk_test_copies.py` writes `t-10-approaches.js`, `t-80-ui.js`, `t-90-boot.js` next to itself
from the base2 files (Lift with `animate: 'bounce'` and a wide range; an "Extreme values" checkbox and wide ranges
on four dials; the two functions on `window.squaringLab`). Then:

    python build.py --name fix-dial-x --base base2 --use src/js/70-dial.js src/css/70-dial.css --swap js/10-approaches.js=out/fix/dial/t-10-approaches.js js/80-ui.js=out/fix/dial/t-80-ui.js js/90-boot.js=out/fix/dial/t-90-boot.js

Nothing under `src/` other than the two kit files was edited.

## Not done, and things to know

- Lift keeps snapping on the real page until the approaches spec is changed (item 1 above).
- The step toggle is still not put back by "Reset this section" and is not remembered across reloads (a tester
  noted it without filing it).
- A there-and-back sweep remembers its direction across pause and play; `reset()` starts it upward again.
- The tag reads "wide" whatever the page calls its switch. If the page's wording changes, the tooltip text
  ("Extreme values are on. ...") in `paintRange` inside `addDial` is the place.
- With extreme values on, a slider keeps its step. On a very wide range (Iterations 3 to 1000 with step 1) one
  pixel of the slider is several steps; the typed box and the arrows reach every value.
- Only Chrome was run.
