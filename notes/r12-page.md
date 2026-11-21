# Round 12, page

Page built with
`python build.py --name r12-page --base base12a --use src/body.html src/js/80-ui.js src/js/75-presets.js src/js/90-boot.js src/css/00-base.css`
-> `dist/r12-page.html`. Scripts, logs and pictures: `out/r12/page/`.

## What was broken in `dist/v12a.html` (seen in the tool, `out/r12/page/look-v12a.json`)

- Show Figure 4 stayed on Sphere inversions, one plane and wrote a `planes` value into that entry's settings,
  which nothing reads any more: the picture was the one-plane Basilica, not Figure 4.
- As it was found did the same (title "Sets Planes to 2"), so it changed nothing in the picture and never went away.
- The list had no headings.

## 1. The list (`80-ui.js` boot, `00-base.css`)

- One `div.rule-group` per group of `APPROACH_GROUPS` that has entries, in the order of `APPROACH_GROUPS`; inside
  it a `p.label.rule-group-head` (id `apgh-<group>`, the group `div` has id `apg-<group>`, `role="group"`,
  `aria-labelledby`), then the entries of that group in the order they stand in `APPROACHES`.
- A group with no entry builds nothing. An entry whose `group` is not in `APPROACH_GROUPS` comes last, in a
  group with no heading.
- Each `.rule` carries `data-ap="<id>"`. `refresh()` marks the chosen entry by that id, no longer by its place in
  the page, so the order on show need not be the order of the array.
- Ids are as before: `ap-<id>`, `f-<id>`, `pd-<id>`, `par-<id>-<key>`. The radio's `value` is still the index in
  `APPROACHES`. All radios share the name `approach`, so the arrow keys walk the whole list top to bottom across
  the headings, as before.
- Phone width: the headings are the small capitals used for labels everywhere else, 16 px above each group.
  Pictures: `out/r12/page/list-1400.png`, `list-375.png` (first entry open), `list-1400-tilt.png`,
  `list-375-tilt.png` (the twisted square open).

## 2. What used the Planes dial

- `uiFigure4`: entry `fold`, Planes 2, Lift 0. The dials of the one-plane entry are no longer touched.
- `uiOnePlane`: entry `mercator`, nothing else. From the Kleinian view it still goes to the Julia set (kept from
  before: an approach shows nothing in a Kleinian picture, so the button would seem to do nothing).
- `juliaFoundDiff` now returns `{ entry?, planes?, iter? }`:
  found with two or more planes and one of the two Sphere inversions entries in use -> `planes` (and
  `entry: 'fold'` when the one-plane entry is in use); found with one plane while `fold` is in use ->
  `entry: 'mercator'`. Under any other approach only the iterations count.
- `juliaFoundWords(d)` (new) gives the words on the button and its tooltip: "As it was found: two planes",
  "As it was found: one plane", "As it was found: 24 iterations", "As it was found: one plane, 24 iterations".
  The words start with the old name, so the texts that call the button "As it was found" still fit.
- The seven Julia notes that said "set Planes to 2 under Sphere inversions" (the six under Found with two planes
  and Pitted gourd) now say "choose Sphere inversions, two planes in the Approach section". The notes live in
  `data/julia-presets.json`; `notes/ui_embed.py` copied them into `75-presets.js` (the header of that file asks
  for it to be done that way). Only those seven lines differ (`out/r12/page/julia-presets.before.json`).
- The key of `uiOnce('julia', ...)` reads `S.param.fold.planes`.

## 3. Buttons for the quaternion entries

- `uiShowSolid(id, flipz, back, room)` is what `uiTwin` did, with the flip as an argument. `uiTwin(id)` calls it
  with the flip on; `uiQuat(id)` with the flip off and `UI_QUAT = { lathe: 1.25, tilt: 1.2 }` (how far back the
  camera stands, as a multiple of the usual start; chosen on the pictures `try-1400-*.png`, `try-375-*.png`).
- Buttons `#quatShow`, `#tiltShow`. On `window.squaringLab`: `showQuaternionSquare()`, `showTwistedSquare()`,
  `juliaFoundWords`, `APPROACH_GROUPS`.

## 4. Closing text

Rewritten: the Planes paragraphs (two entries now), "Lathe" where the entry is meant, the twin answer (the twin of
the Lathe is the twisted square at Tilt 180), the Julia panel note, "What does a list entry change?". Two new
answers after the twin answer, with the two buttons beside the first. Only facts from `docs/ROUND12.md`.

A sentence that names the entries kept for the record is written by the page itself into `#triedNote` (end of the
Figure 4 answer), and only when the list has entries in the group `tried`. So the text is right with none, and
right with whatever the other engineer adds.

## 5. Smoke test

`out/r4/page/make_smoke.py` writes `tools/smoke-v12.json` (and with `--mine` a trial copy
`out/r12/page/smoke-mine.json`); screenshots in `out/r12/page/smoke/`. It no longer writes `tools/smoke.json`.
The copy as it was before this round: `out/r12/page/make_smoke.before-r12.py`.
New or rewritten steps: the headings and ids of the list; every entry drawing (Mandelbrot solid and the Julia set
for c = −1, for whatever entries `L.APPROACHES` holds); Show Figure 4 landing on `fold`; Back to one plane; As it
was found switching the entry both ways; the two new buttons and their names on `window.squaringLab`.

## Results (measured on `dist/r12-page.html` as built at 11:46 on 2026-11-18)

- `tools/smoke-v12.json`: 58 steps, exit code 0, no console errors (`out/r12/page/smoke.log`). Every entry drew:
  probes hit of 165, Mandelbrot solid / Julia set for c = −1: mercator 19 / 29, fold 32 / 26, lathe 50 / 31,
  tilt 35 / 29, bulb 24 / 42, classic 44 / 14, split 50 / 95.
- The same file on the stand-in page with 10 entries (`dist/r12-page-tried.html`, built before the last two wording
  edits): 58 steps, exit code 0, 5 headings over 10 entries (`out/r12/page/smoke-tried.log`).
- Real arrow keys (`out/r12/page/keys.py`, `keys.log`, `keys-tried.log`): Arrow Down walks the list in the order
  shown, across the headings, with the focus ring, and wraps from the last entry to the first; Arrow Up goes back.
- Framing of the two new buttons: twisted square 24 of 165 probes hit, none on the outer ring; quaternion square
  25, none on the outer ring (1400 x 950 and 375 x 800).

Not measured: the smoke test at phone width (it was written for 1400 x 950); other window shapes for the framing.

## Left as it was, on purpose

- Back to one plane from the Kleinian view still goes to the Julia set.
- The lede says the slice at z = 0 is the flat set "for every approach here except the classic Mandelbulb". If an
  entry kept for the record is not exact there, that sentence needs a look.

## Tried by hand

`out/r12/page/make_try.py` -> `try-1400.log`, `try-375.log` (and pictures `try-*-*.png`): each of Show Figure 4,
Back to one plane, the two new buttons and As it was found from at least two starting states, at 1400 and at
375 px wide.

`out/r12/page/make_test_approaches.py` -> `dist/r12-page-tried.html`: the frozen list plus three stand-in entries
(two in `tried`, one in a group with no heading), to see the list and the smoke test with more entries.
