# r10-dial: the controls kit in round 10 (what the second check found)

File changed: `src/js/70-dial.js` (one place inside `addDial`: the function `stepFrom` and three small helpers in
front of it; 22 lines added, 1 replaced). `src/css/70-dial.css` is unchanged (the same bytes as `base9m/`).
Nothing else under `src/` was touched. Page: `dist/r10-dial.html`
(`python build.py --name r10-dial --base base9m --use src/js/70-dial.js src/css/70-dial.css`).
Scripts, logs and pictures: `out/r10/dial/`. Started 06:28, last test ended 06:51. One browser at a time.
The logs of the first check's driver say "wrote out/t6/controls/<name>" for pictures: that text is fixed in the
tester's script; the pictures are in `out/r10/dial/t6-<page>/` and nothing was written into a tester's folder.

## t9-dials-2: at the low end of Trap thickness, Surface threshold and Fly speed the arrows left the step grid

Seen on `dist/v9m.html` with the tester's own script and real clicks (`python out/t9/dials/grid.py dist/v9m.html`,
log `out/r10/dial/grid-v9m.log`), from the typed start value, down four times and up three times:

| dial | before (`dist/v9m.html`) | after (`dist/r10-dial.html`, `grid-r10.log`) |
|---|---|---|
| Trap thickness, from 0.01 | 0.005, 0.0005, 0.0005, 0.0005, 0.0055, 0.0105, 0.0155 | 0.005, 0.0005, 0.0005, 0.0005, 0.005, 0.01, 0.015 |
| Surface threshold, from 0.1 | 0.05, 0.02, 0.02, 0.02, 0.07, 0.12, 0.17 | 0.05, 0.02, 0.02, 0.02, 0.05, 0.1, 0.15 |
| Fly speed, from 0.02 | 0.01, 0.001, 0.001, 0.001, 0.011, 0.021, 0.031 | 0.01, 0.001, 0.001, 0.001, 0.01, 0.02, 0.03 |
| Glow width, from 0.03 | 0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04 | the same |
| Resolution, from 0.2 | 0.15, 0.1, 0.1, 0.1, 0.15, 0.2, 0.25 | the same |

Cause: an arrow step adds the step to the value and the result is held inside the typed limits. Where the typed
limit is no whole number of steps (0.0005 with steps of 0.005), the value is held on an odd number, and every later
step carries that odd part along.

Fix, in the kit, as the tester suggested, in two parts. Both only act at a typed limit that is no round value;
a limit that is a round value takes the old path through the code.

1. Leaving such a limit, the first step lands on the next round value, and further steps count from there
   (0.0005 up gives 0.005, 0.01; with Shift 0.05).
2. Arriving at such a limit, a step that would pass it stops on the last round value before it. Only from that
   value (or from a value beyond it) does a step go to the limit itself. With single steps from a round value this
   was so already; it now also holds for ten steps at once (Trap thickness 0.03, Shift and down: 0.005, then 0.0005;
   before: 0.0005 at once).

"Round values" are the usual slider's positions carried on past both of its ends (the slider's lowest usual value
plus whole steps). For every dial of the page that is the same as the whole multiples of its step (measured: no
usual slider starts between two multiples).

One part of the tester's wording I did not follow, on purpose: "when the value is not on the step grid (it was
held at a limit or typed), step to the next grid value". For a value held at a limit: done. For a typed value in
between (2.37 on Power n, 0.0125 on Trap thickness): not done. The kit has stepped such a value by its step and
kept the odd part since round 1 ("Fine steps never snap to a grid" is one of its own 71 checks), and the first
check recorded "ArrowUp, Shift+ArrowUp, PageDown, ArrowDown from 2.37 give 2.47, 3.47, 2.47, 2.37" as a pass, a
line that had to stay as it is. So a typed 0.0125 still goes 0.0175 up and 0.0075, 0.0025 down; from 0.0025 the next
press down is held at 0.0005, and from there the arrows are back on 0.005, 0.01. The tester's "expected" (the first
press up from the lowest value lands on the next grid value, so that 0.01 and 0.05 can be reached again) is met.

Not changed: the last press down still goes from 0.005 to 0.0005, ten times thinner in one press. The tester named
it and allowed it; the low limit stays reachable with the arrows.

### Which dials gain

Every number box of the page, both ends, usual ranges and extreme ranges, walked before and after with the same
script (`out/r10/dial/ends.py`, scripted presses on the arrow buttons; logs `ends-before.log`, `ends-after.log`;
comparison `ends-diff.log`; which limits lie off the grid: `offgrid-before.log`, `offgrid-after.log`):

- Usual ranges: 51 boxes walked, 48 the same before and after, 3 changed: Trap thickness (limit 0.0005),
  Fly speed (0.001), Surface threshold (0.02).
- Extreme ranges: 51 walked, 45 the same, 6 changed: the same three (Surface threshold with limit 0.002) and
  Mosaic cell size (0.005), Turning-out sphere radius (0.005), Ray step share (0.005).
- The boxes that changed are exactly the boxes with a typed limit off their grid. All such limits are low limits.
  After the fix no walk in the usual ranges gives a value that is neither a round value nor a limit.

### With real input, on `dist/r10-dial.html`

`python out/r10/dial/real.py dist/r10-dial.html after` (log `real-after.log`): 13 pass, 0 fail. The same script on
`dist/v9m.html` (`real-before.log`): 6 pass, 7 fail, which is the fault.

- The defect's own words: Trap thickness from 0.05, down ten times: 0.045 ... 0.005, 0.0005; then up: 0.005, 0.01,
  0.015 ... and 0.05 again on the tenth press (before: 0.0055 ... 0.0505).
- Shift with a real click, a held arrow (down to 0.0005, then up through 0.005, 0.01 ... only), and the keys in the
  box (ArrowDown, ArrowUp, Shift+ArrowUp, PageDown, PageUp).
- What stays: typed 0.0125 keeps its odd part until it meets the limit; Power n 2.37 gives 2.47, 2.57; Power n at
  its limit 24 steps down to 23.9; Trap thickness on the whole-number toggle: 0.0005, 1, 2, 1.
- Finger taps on a 375 x 812 touch phone (`phone.py`, `phone-after.log`): the three dials, 4 pass, 0 fail, no
  sideways scroll.
- Pictures looked at: `after-thick-low.png` (box 0.0005, hollow thumb at the left end, down arrow dimmed),
  `after-thick-up.png` (one press up: box 0.005 and the thumb on the slider's lowest position, so box and slider
  agree), `before-thick-up.png` (0.0055), `after-phone-thick-up.png` (phone, light theme, 0.005, clean row).

## What must not change, and did not

Recorded on `dist/v9m.html` before any source was touched, repeated on `dist/r10-dial.html` after:

- The first check's driver, unchanged (`python out/r10/dial/run_t6.py <page> dials resets extreme`; logs
  `t6-on-v9m.log`, `t6-on-r10.log`; comparison `t6-compare.log`): 144 result lines on both pages, identical
  character for character. dials 84 pass, 0 fail; resets 34 pass, 2 fail (the two lines the first tester explained
  as their table being too strict); extreme 24 pass, 0 fail. The list of the 51 number boxes (ranges, start values,
  toggles, tooltips) is the same in both logs.
- The kit's own page (`python tools/shot.py --url tests/dial.html --actions tests/dial.json`): all 71 checks pass
  before (`kit-tests-before.log`) and after (`kit-tests-after.log`). The 13 extra checks of round 7
  (`out/r7/dial/kit-extra.json`): 13 pass (`kit-extra-r7.log`).
- 14 new checks of the new rule on the kit's page (`out/r10/dial/kit-extra.js`, made into `kit-extra.json` by
  `mk_kit_extra.py`; log `kit-extra.log`): all pass. They cover shapes the page does not have: a high limit off the
  grid (10.15 by 0.1: down gives 10.1, 10), a slider that starts between multiples of its step, a whole-number
  dial with steps of 10, a dial with a step of 1 on its finer choice, a dial without a slider, extreme ranges on,
  an odd dial, no setter call at the limit, no floating-point noise over forty steps.
- Smoke test: `python tools/shot.py --url dist/r10-dial.html --actions tools/smoke-v9m.json`: exit 0, 52 steps,
  no console errors (`smoke.log`). The page was built again after the last test: the same bytes.

## Names added or changed

- `roundDec`, `isRound(v)`, `roundNext(v, dir)`: private to `addDial`, in front of `stepFrom`. The round values of
  the dial and the next one beyond a value.
- `stepFrom`: same name and arguments; its last line (the fine step) became the two rules above.
- No id, class, label, tooltip, CSS property or function that another file or a test relies on was changed.
  No new control, no new option in a dial spec.

## What the person joining the files must know

- Take `src/js/70-dial.js` as it is; the style sheet did not change. The change is inside `addDial` only.
- The tooltips of the arrows still say "Up by 0.005" and "Down by 0.005". At a limit that is no round value the
  one step that leaves it is shorter than that (0.0005 to 0.005). I left the words alone.
- For a page owner, not a kit matter and not a filed defect: with Extreme ranges on, the slider of Surface
  threshold starts at 0.02 and moves by 0.05, so the slider itself gives 0.07, 0.12 (`src/js/80-ui.js`, `qdetail`,
  `xmin: 0.02`). An `xmin` of 0.05 would keep it on round values. The arrows now come back to 0.05, 0.1 from the
  limit there too.
- `tests/dial.html` could take the 14 checks of `out/r10/dial/kit-extra.js` (and the 13 of round 7).

## Measured, and only reasoned

- Measured: everything above, in headless Chrome on this machine, real mouse, keys and touch through the DevTools
  protocol for `grid.py`, `real.py`, `phone.py` and the first check's driver; scripted presses for `ends.py` and
  the kit checks.
- Only reasoned: the tester's other scripts of the second check (`new9.py`, `recheck.py`) were not run again.
  Their one line that touches this is "the down button twelve times from 0.05, then the up button three times",
  whose values after the fix are 0.005, 0.01, 0.015 by the runs above. The play button (sweep), typing, the slider
  and the whole-number toggle do not go through the changed lines.
- Not done: other browsers; the light theme on a desktop (no colour or layout changed).
