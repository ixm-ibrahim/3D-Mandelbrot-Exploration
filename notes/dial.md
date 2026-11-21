# dial: the controls kit

Files: `src/js/70-dial.js`, `src/css/70-dial.css` (new), `tests/dial.html`, `tests/dial.json`, `notes/dial_real.py`.

## What was built

A dial is now: label, a box cluster, a slider, and an optional hint.

```
POWER N                      [play] [±0.1] [   2.37 |up/down]
━━━━━━●──────────────────────────────────────────────────────
hint text
```

- **Typed box**: `<input type="text" inputmode="decimal" id="<id>Num">` with two step buttons. No `type=number`
  anywhere, so the wheel cannot change a value (checked with real wheel events; the page still scrolls).
- **Step toggle** (`id="<id>Step"`): shows the step the arrows use, "±0.1" or "±1". It affects the box's step
  buttons and arrow keys only; the slider keeps its own step.
- **Stepping**: buttons, ArrowUp/ArrowDown; Shift, PageUp/PageDown or Shift+click = ten steps; holding a button
  repeats (after 0.42 s, every 60 ms). Fine mode adds exactly one step to whatever the value is (2.37 to 2.47).
  Whole-number mode goes to the next whole number (2.37 to 3 or 2; 3 to 4). Results are rounded in decimal, so
  there is no 2.4000000000000004. A step starts from what is typed in the box if that is a number.
- **Typing**: Enter or leaving the box commits; Escape restores. Accepted: spaces around, unicode minus and
  dashes, one decimal comma, scientific notation, `.5`, `5.`, `+4`. Refused (old value back, `aria-invalid` and a
  red border for 1.4 s): anything else, including `1,234.5`, `2/3`, `1e999`, empty. Out-of-range clamps to
  `lo/hi` (amber border for a moment). `int` rounds, `odd` goes to the nearest odd number (a tie goes up).
  Text that was not edited is never written back, so a state value with more digits than the box shows survives.
- **Display** (`dialFmt`): at most 6 decimals, trailing zeros trimmed, plain "-". Exponent form only below 1e-6
  or from 1e15 up ("4e-7"), and it reads back.
- **Slider**: restyled (hairline track filled in brass, square thumb, a small tick at the default value). A value
  outside its range shows the thumb at the near end, drawn hollow, and nothing is written until the user moves it.
  A value between two steps keeps its digits.
- **animate**: play/pause button (`id="<id>Play"`). Sweeps min to max and wraps, one range per 8 s
  (`animate: <seconds>` changes that), setter called every frame. `animate: 'bounce'` sweeps there and back
  instead (8 s each way), for a value whose two ends give different pictures. Pauses when the control is hidden
  (hidden attribute or display none, on it or anywhere above it), on reset, and when the user changes the value
  by hand. A section that is only folded shut (a closed `<details>`) does not pause it (changed in the fix round).
  Values are sent one decimal finer than the slider's step.
- **help**: a small note under the dial; also works for `check` and `select` specs.
- **buildControls**: `dial`, `select`, `check`, `note`, `when`. `when` is re-checked after every change, on
  `sync()` and on `syncControls()`. Unknown types log a console warning and are skipped.
- **resetGroup**: every control of the group is reset through its setter; for spec-built sets `onChange` runs
  once at the end instead of once per control.
- **Phone**: under `(pointer: coarse)` the cluster is 34 px tall, the two step buttons sit side by side at
  32 px each, the box text is 16 px (no zoom on focus). A tap on a step button does not put the caret in the box.
  In a narrow column the cluster drops under the label; below about 240 px the typed box narrows.

## Names (all top level in 70-dial.js)

Contract names, unchanged signatures: `addDial`, `addCheck`, `addSelect`, `buildControls`, `syncControls`,
`resetGroup`, plus the baseline's `controls` and `hostEl`.

New:
- `addReset(host, group, o)` - a `.btn.dial-reset` button, "Reset this section". `o.label`, `o.id`,
  `o.after()` (called after the reset, for state no control holds). Returns the button.
- `dialFmt(v)` - number to box text. `dialParse(text)` - typed text to number or NaN. `dialDecimals(x)`.
- `dialSets`, `dialBatch`, `dialQuietly(work)`, `dialVisible(el)`, `dialSweeps`, `dialSweepFrame`,
  `dialSweepLast`, `dialSweepTick`, `dialSweep`, `dialWithHelp`, `dialDrop`, `DIAL_ICON`, `DIAL_NO_MINUS_KEY`
  - private.

New options and fields:
- `addDial` opts: `lo`, `hi`, `int`, `odd`, `def`, `group`, `animate` (true or seconds), `help`,
  `slider: false` (label and typed box only; the label then points at `<id>Num` and no element has the id `<id>`).
- `addCheck`, `addSelect` opts: `def`, `group`, `help`.
- `addSelect` options may be `[value, text, heading]`: neighbours sharing a heading go under an `<optgroup>`.
  A state value that is not an option shows an empty box (the baseline showed the first option).
- Every control: `{ el, group, id, sync(), reset(), remove() }`; dials add `play(on?)`; selects add
  `setOptions(list)`.
- `buildControls` returns `{ sync(), reset(), update(), remove(), controls }`. It also fills `obj[key]` from
  `def` when the key is missing.
- Element ids: `<id>` slider, `<id>Num` box, `<id>Step` toggle, `<id>Play` play button, `<id>Help` hint.
- CSS classes: `.dial`, `.dial-bare`, `.dial-box`, `.dial-play`, `.dial-mode`, `.dial-num`, `.dial-steps`,
  `.dial-up`, `.dial-down`, `.dial-help`, `.dial-reset`, `.check-block`, `.field-block`; states `.is-out`,
  `.is-playing`, `[data-at]`, `[data-flag]`. CSS variables on the slider: `--dial-p`, `--dial-d`, `--dial-thumb`,
  `--dial-fill`.

No state was added to `S`. No localStorage.

## What the UI integrator must do

Nothing is needed to keep existing calls working. To use the new parts:

1. **Reset buttons**: give every control of a section a group (`{ group: 'eq' }` on `addDial/addCheck/addSelect`,
   `group` in `buildControls` opts), then `addReset(hostElOrId, 'eq', { after: () => { ... } })` at the end of
   the section body, or wire your own button to `resetGroup('eq')`. `resetGroup` accepts an array of groups.
   Controls the page builds by hand (`#k3`, the modifier boxes, `#cutOn`, `#normals`, `#qShadow`, `#qAO`) are not
   in the registry: build them with `addCheck/addSelect` or reset them in `after`.
2. **After changing state from code** (presets, saved points): call `syncControls()`. It also re-checks every
   `when`. A `when` that reads state outside its own object is only re-checked by `syncControls()` or the set's
   `update()`.
3. **Whole-number dials**: pass `int: true` (Iterations, Refining passes, Depth of the search, Ray steps) so the
   kit rounds typed values. With step 1 that also means no toggle; Ray steps (step 10) gets "±10" / "±1".
4. **Power dial**: `addDial('eqDials', 'pow', 'Power n', -8, 10, 0.1, get, set, { lo: -8, hi: 24 })` or whatever
   limits are decided; nothing else to wire.
5. **Sweeps** call the setter about 60 times a second. A spec set's `onChange` therefore runs every frame while
   a dial plays; keep it light (the approaches' live code was fine: 121 frames in 2 s on the test machine).
6. **CSS**: 70-dial.css restates everything a dial needs. The old `.dial`, `.dial input[type=range]` and `.num`
   rules in `00-base.css` are overridden and can be deleted; keep `.label`, `.note`, `.field`, `.check`,
   `.checks`, `.btn`, which the kit uses. The kit hides `[hidden]` dials, fields, checks and notes itself.
7. **Optional**: the camera's zoom-limit boxes can become kit boxes with
   `addDial(host, id, label, min, max, step, get, set, { slider: false, lo, hi })`, or keep their own inputs and
   use `dialParse` / `dialFmt` for the same typing rules.
8. Labels are HTML (as in the baseline); `help` and `note` text are plain text.

## Tests

- `python tools/shot.py --url tests/dial.html --actions tests/dial.json` - the kit alone, 59 checks in page
  JavaScript, a pass/fail list on the page and in `window.dialTests.lines`; exits non-zero on any failure.
  Run from the workspace root. Screenshots: `out/dial/tests.png`, `out/dial/showcase.png`.
- `python notes/dial_real.py --lab` - real mouse, keyboard, wheel and touch through the DevTools protocol:
  42 lines in all. The same 59 checks in a focused window (so the focus rings are really observed), 22
  real-input checks on the test page, 7 in `dist/dial.html` on desktop, 10 on an emulated 375 px touch phone
  (test page and lab), and a console-error check. `--lab=<path>` points it at another build; its lab part
  assumes the baseline's ids (see the docstring). Once, with several Chromes running at the same time, it
  stopped with "Chrome did not start its debugging port"; running it again passed.

## Known limits and choices

- **Toggle rule (changed in the fix round).** No toggle only when the dial holds whole numbers and steps by 1
  (`int` with step 1) or is `odd`. A whole-number dial with a larger step (Ray steps, 10) gets "±10" / "±1". A dial
  whose own step is 1 but which can hold decimals (Field of view, the light dials, the phase and turn dials) gets
  "±1" / "±0.1" and starts on "±1", so its arrows go to the next whole number (35.49 to 36).
- **Focus rings cannot be asserted under tools/shot.py**: its headless window has no focus, so no `:focus` rule
  matches. There the line reads "Every control can take keyboard focus ..."; under `notes/dial_real.py` (focus
  emulation on) the real check runs and passes, and `out/dial/rings.png` shows the rings.
- On iPhone and iPad a dial that accepts negative numbers gets `inputmode="text"`, because the decimal keypad
  there has no minus key. Everywhere else it is `decimal`. Not tested on a real device.
- Changing a value by hand pauses its sweep; it does not resume by itself.
- The toggle state is per dial and is not remembered across reloads.
- `reset()` always calls the setter, even when the value is already the default (the contract says so).
- Firefox and Safari were not run; the slider has `-moz-` rules written but only Chrome was tested.

## Extreme values (added in the fix round)

One switch widens the range of every dial that carries a wider range. Details and the reasons are in
`notes/fix-dial.md`; the interface is:

- Spec or opts fields, all optional: `xmin`, `xmax` (the slider's range while the switch is on) and `xlo`, `xhi`
  (the typed limits while it is on). A missing field keeps the normal value. One exception: when `xmin` or `xmax`
  is given without `xlo` or `xhi` and reaches beyond the normal typed limit, that typed limit moves out with the
  slider, so no part of the wide slider is dead. `int` and `odd` apply to the wide limits too.
- `setExtreme(on)`: switches every dial, present and future. Switching off brings a value beyond the normal typed
  limits back to the nearest limit through the dial's setter (one `onChange` per spec-built set). A value inside
  the typed limits is left alone even when it lies beyond the normal slider (hollow thumb, as before).
- `isExtreme()`: the state of the switch.
- The flag is stored in `S.extreme` when the page state exists (it does in the lab; `setExtreme` writes it and
  `isExtreme` reads it). So `S.extreme = true; syncControls()` also moves the ranges, but a sync never writes a
  value. On the kit's own test page there is no `S` and the kit keeps the flag itself.
- A dial using its wide range shows a small tag, "wide", in front of its box cluster (`<span class="dial-wide"
  id="<id>Wide">`, brass, 10.5 px), with the ranges in its tooltip, and has the class `is-wide`.
- Every control object of a dial has `rerange(pull)`; `setExtreme` calls it. Not for page code.
- Typing, steps, the step toggle, the slider, `sync()`, `reset()` and play all use the range in use. A playing
  sweep carries on inside the new range when the switch changes.

Tests after the fix round: `tests/dial.html` has 71 checks (59 before); `notes/dial_real.py --lab=dist/fix-dial.html`
prints 42 lines, all pass.
