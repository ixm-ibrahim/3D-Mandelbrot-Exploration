# r7-dial: the controls kit in the fix pass after the check of Version 6

Files changed: `src/js/70-dial.js` (three places inside `addDial`), `src/css/70-dial.css` (the typed box).
Nothing else under `src/` was touched. Page: `dist/r7-dial.html`
(`python build.py --name r7-dial --base base6 --use src/js/70-dial.js src/css/70-dial.css`).
Scripts, logs and pictures: `out/r7/dial/`. Started 03:25; the final page was built at 03:52 and every check below
was run on it again, ending 04:01. The logs of the tester's driver say "wrote out/t6/controls/<name>" for every
picture: that text is fixed in the tester's script, the pictures are in `out/r7/dial/` (and `out/r7/dial/t6/`), and
nothing was written into the tester's folder.

To repeat: `python out/r7/dial/repro.py dist/v6.html before` and `python out/r7/dial/repro.py dist/r7-dial.html after`
(parts `c1`, `l3`, `ex`; a third argument runs one part).

## controls-1: "Reset this section" left a dial's step toggle where the user had put it

Seen on `dist/v6.html` with real clicks (`out/r7/dial/before.log`): toggle of Power n opens on ±0.1, reads ±1 after
a click, still ±1 and pressed after "Reset this section", and the up arrow then gives 3. The same for a dial that
opens on whole steps (Field of view stayed on ±0.1), for every section's button, and for "Reset everything"
(40 toggles left flipped).

Cause: the control's `reset()` put back the value and the sweep, not the step mode.

Fix: `addDial` remembers the step mode a dial opens on (`whole0`) and `reset()` puts it back and repaints the
toggle (text, `aria-pressed`, tooltips of the toggle and of both arrows). Everything that resets goes through
`reset()`, so one line covers `resetGroup`, the "Reset this section" buttons (`addReset`), `buildControls(...).reset()`
and the page's "Reset everything". `sync()` and `syncControls()` leave the toggle alone: a list entry, a quality
button or an undone state does not change the step the user chose.

On `dist/r7-dial.html` (`out/r7/dial/after-c1.log`, real clicks): after "Reset this section" Power n reads ±0.1, not
pressed, the up arrow gives 2.1. Field of view is back on ±1. Every section's button puts back its own toggles and
no others, all 42 toggles of the page between them (Mandelbrot options 1, Approach 6, Equation 1, Slice 1, Colour
and light 12, View 3, Quality and speed 5, Save a 3D model 2, and in their own modes the Julia panel 3 and the
Kleinian panel 8). "Reset everything" puts back all 40 toggles of the sections it resets. The two toggles of
"Save a 3D model" stay as they are after "Reset everything", exactly like that panel's values (measured: Longest
side typed 150 still reads 150 after "Reset everything"; the panel's own button gives 100 and both toggles back):
the page does not reset the two file panels there (`UI_GROUPS` in `src/js/80-ui.js` has no `'export'` or `'mesh'`).
The tester's own line (`out/t6/controls/drive.py resets`, run on my page) now reads
"step toggle of Power n: opening ±0.1, after a click ±1, after Reset this section ±0.1".
Pictures: `out/r7/dial/after-c1-power-toggled.png`, `after-c1-power-after-reset.png`.

## layout-3: on a phone a typed box cut the last digit of a six-decimal value

Seen on `dist/v6.html` at 375 x 812 as a touch phone: `kmyNum` = `['1.732051', 77, 72]`
(`out/r7/dial/before-l3-375t-klein-dials.png`). Looking further than the one entry showed it is wider than reported:
on the phone 52 dial values across the 62 list entries were cut (μ i part in 24 Kleinian entries, μ real part in 15,
μ j part in 2, c along x in 7 Julia entries, c along y in 4), and six of them are cut on a desktop at 1400 as well
(c along x in 5 Julia entries, c along y in 1): a value with a minus sign and six decimals has nine characters and
the desktop box holds eight and a half. The Douady rabbit is one of them: c along x = -0.122561 showed with its
minus sign clipped (`before-rabbit-1400.png`, `before-rabbit-375.png`).

Cause: the box had one fixed width (8.5 characters; 7.5 with a coarse pointer, where the type is 16 px), and a
number can have up to 6 decimals, a sign and digits before the point.

Fix: the box keeps its usual width for every ordinary number and grows for a longer one. The script writes the
number of characters of the number on show into `--dial-len` on the typed input (only when that count changes), and
the style sheet makes the box `max(usual width, that many characters plus half a character)`. The usual widths are
unchanged (`--dial-w`: 8.5ch, 7.5ch with a coarse pointer), so no dial that looked right before looks different
now. The box does not resize while the user types; it follows the number the state holds.

I tried the tester's first suggestion too (a wider usual box on phones, 8.5 characters): measured on the page at
375 wide it changes the height of 2 to 5 dials in the ordinary state and of 15 to 18 with extreme ranges on, because
labels that shared a row with the box no longer fit (`out/r7/dial/trial_base.log`). That is a wide change to a layout
the layout tester found clean, so I did not do it.

On `dist/r7-dial.html` (`out/r7/dial/after.log`, `after-l3-1024.log`): `kmyNum` = `['1.732051', 82, 82]` on the phone.
In all 62 list entries (34 Kleinian and 26 Julia, plus "Your own values" in each list) no number is cut and no box
cluster leaves its column, at 375 touch light, 1400 dark and 1024 light. -1.732051, -0.123456, -12.345678 and 1.5e-7 show whole.
The fullest cluster on the page (Lift toward the pole on the phone: wide tag, play, toggle, box, in the 295 px card)
holds -1.234567 whole. No sideways scroll.
Pictures: `after-l3-375t-klein-dials.png`, `after-l3-375t-julia-long.png`, `after-l3-375t-lift-long.png`,
`after-l3-1400-julia-long.png`, `after-l3-1024-julia-long.png`, `after-rabbit-375.png`, `after-rabbit-1400.png`.

What it costs, to be honest about it: a box with a long number is one or two characters wider than its neighbours,
so in a column of dials the toggles of those rows sit a little further left (`after-rabbit-375.png` shows the three
c dials with three widths). And when a number gets very long (-12.345678 on the phone) the label moves to a row of
its own above the box.

## The 50 number boxes

- The controls tester's own tests, unchanged, on my page (`python out/r7/dial/run_t6.py dist/r7-dial.html dials resets extreme`,
  log `out/r7/dial/t6-on-r7.log`): `dials` 83 pass, 0 fail, and its 83 result lines are the same, character for
  character, as the tester's on Version 6 (`out/t6/controls/dials.log`): the 26 typed cases on Power n, the arrow
  keys, 0.1 up twice = 0.3, the wheel, Iterations, and the sweep of 48 boxes (a step up and down, the toggle and a
  whole step, "abc" refused, the start value typed back). `extreme` 24 pass, the same 24 lines as the tester's.
  `resets` 34 pass, 2 fail: the same two lines as on Version 6, which the tester's report explains as their table
  being too strict (the Julia and Kleinian lists move to the entry the restored values stand on).
- The two boxes the tester did not reach, typed width and height of a picture (`out/r7/dial/after.log`, part `ex`):
  swept with the tester's own sweep, both pass; 99999 is held at 8192, 2.6 becomes 16.
- The kit's own page: `python tools/shot.py --url tests/dial.html --actions tests/dial.json`: all 71 checks pass
  (`out/r7/dial/kit-tests.log`). 13 new checks of the two changes, run on the same page
  (`out/r7/dial/kit-extra.js`, made into `kit-extra.json` by `mk_kit_extra.py`; log `kit-extra.log`): all pass.
  They cover: reset on a fine dial, on a dial that opens on whole steps, on dials without a toggle; groups and
  `addReset`; `sync()` leaving the toggle alone; a spec-built set; extreme values on; a playing sweep; the box at its
  usual width, grown and back; typing, refusing and cancelling; a value that is not a number; columns of 343, 295,
  240 and 200 px; no movement of the play button while a sweep runs.
- Real mouse, keyboard and finger (`notes/dial_real.py`): 40 of 42 lines pass on my page and the same 40 on
  Version 6. The two that fail on both are the script's, not the page's: it clicks `#eqDials .dial .dial-up` and
  means Power n, which has had its own host `#powHost` for some rounds. With that selector corrected
  (`out/r7/dial/dial_real_r7.py`, which patches a copy in memory and leaves the file alone) all 42 pass on my page,
  among them the 71 in-page checks with a focused window and again as a 375 px touch phone, and real taps.
- Smoke test: `python tools/shot.py --url dist/r7-dial.html --actions tools/smoke-v6.json`: exit 0, 42 steps, no
  console errors (`out/r7/dial/smoke.log`).

## Names added or changed

- `--dial-len` (CSS custom property, set by the script on each typed input `.dial .num`): the number of characters
  of the number the box shows. Not set while the box is empty.
- `--dial-w` (CSS custom property on `.dial .dial-num .num`): the usual width of the typed box, 8.5ch, and 7.5ch
  inside `@media (pointer: coarse)`. Change the usual width there, not in `width`.
- `whole0` (private constant inside `addDial`): the step mode a dial opens on.
- Behaviour of `reset()` on a dial's control object: it now also puts the step toggle back. No id, class, label or
  function name changed. No new function.

## What the person joining the files must know

- Take both files together: the script writes `--dial-len`, the style sheet reads it. With the old style sheet the
  new script is harmless (the property is unused); with the old script the new style sheet keeps the usual width.
- A browser without CSS `max()` keeps the usual width (the growing rule sits in an `@supports` block).
- Where a column is too narrow for the whole cluster the box still gives up width, as before (in the kit test a
  200 px column cuts a nine-character number). No state of the page at 375 wide does that today.
- Not a kit matter, for whoever owns it: `notes/dial_real.py`, function `lab()`, the two strings
  `"#eqDials .dial .dial-up"` should read `"#powHost .dial .dial-up"`. And `tests/dial.html` could take the 13 checks
  of `out/r7/dial/kit-extra.js`.
- If "Reset everything" should also put back the two file panels (their values and their two toggles), that is
  `UI_GROUPS` in `src/js/80-ui.js`; the kit needs nothing more for it.

## Not done, not tried

- Only headless Chrome, with IBM Plex Mono loaded. The growth counts characters in `ch`, which is exact for a
  fixed-pitch font; every font in `--f-mono` is one.
- The light theme was looked at on the phone and at 1024, the dark theme at 1400. No colour was changed.
- I did not make the boxes of one panel grow together (so that the toggles keep lining up when one number is long).
  It would need the dials of a host to know about each other.
