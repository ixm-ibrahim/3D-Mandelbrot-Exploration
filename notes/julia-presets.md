# Julia presets: what is in `data/julia-presets.json`, how it was found, and what the UI must do

Research only. Nothing in `src/` was touched. Everything was rendered on the frozen baseline
(`python build.py --name julia-presets --base base`, page `dist/julia-presets.html`).

## What was built

`data/julia-presets.json`: 26 Julia constants for z² + c, each with a name, a one-line note, a camera, and the
settings the picture was checked with.

| Group | Count | `source` |
|---|---|---|
| Well-known constants taken as they are usually quoted | 13 | `classic` |
| Well-known constants derived here (Newton's method or a closed formula) | 5 | `computed` |
| Constants with a z part, found by exploring with sphere inversions and two planes | 8 | `explored` |

Every preset was rendered on the baseline at the lab's default quality, looked at, and kept only if the picture is
sharp, fills the stage and is recognisable. The 26 final pictures are `out/julia-presets/final-01.png` to
`final-26.png` (contact sheets `final-sheet-1.png` to `final-sheet-7.png`), in the order of the file.

## The format

```json
{ "name": "Douady rabbit",
  "note": "The centre of the period-three bulb. Three lobes meet at every pinch. Best with one plane and about 24 iterations.",
  "c": [-0.122561, 0.744862, 0.0],
  "source": "computed",
  "planes": 1,
  "iter": 24,
  "cam": { "yaw": -1.571, "pitch": 1.1, "dist": 4.6 } }
```

`name`, `note`, `c`, `source` and `cam` are the fields the spec asked for. `cam` is present on every preset.
Two fields are **additions to the spec's format**, and the reason for them is the main finding below:

- `planes` (always present, 1 or 2): the value of the sphere-inversion approach's "planes" dial
  (`S.param.mercator.planes`) the picture was checked with. All eight explored presets and the seven presets on or
  next to the x-axis use 2. The eleven classics with a real y part use 1.
- `iter` (optional, only on five presets, always 24): the least iteration count (`S.iter`) at which the set shows
  the shape its note describes. It is a floor, to be applied as `S.iter = max(S.iter, iter)`.

`c` is rounded to six decimals (what the new dial displays, and far finer than a pixel). `cam` is the arcball camera
with `target = [0, 0, 0]`; distances were chosen on the baseline stage at 1400 × 950 (stage 862 × 701).

Names added this round: the two JSON fields `planes` and `iter`. Nothing was added to `src/`. `JULIA_PRESETS` and
`applyJuliaPreset` below are suggestions for files the UI owns.

## What the UI integrator must wire up

1. Copy the array into `src/js/75-presets.js` (suggested name `JULIA_PRESETS`). Keep the order: named classics,
   then the frequently shown values, then the explored ones.
2. List them in the Julia panel under the three c dials, in two groups: `source` `classic` or `computed` under a
   heading such as "Classic sets", `explored` under "Found by exploring". Show `name` as the item, and `note` as its
   hint (small text or `title`).
3. On click, run this (tested on the baseline by `notes/julia_apply_test.py` at 1400 × 950 and at 375 × 812: all
   26 apply, the c dials, the planes dial, the iteration dial and the camera follow, the picture finishes drawing,
   no console errors):

   ```js
   function applyJuliaPreset(p) {
     S.c = p.c.slice();                                     // a copy: the c dials write into S.c in place
     if (p.planes && S.param.mercator) S.param.mercator.planes = p.planes;
     if (p.iter && S.iter < p.iter) S.iter = p.iter;        // a floor, never lowers what the user chose
     if (p.cam && !S.flat) {
       const narrow = Math.max(1, 1.2 * stage.clientHeight / stage.clientWidth);   // 1 on a desktop stage
       cam.target = [0, 0, 0]; cam.yaw = p.cam.yaw; cam.pitch = p.cam.pitch; cam.dist = clampDist(p.cam.dist * narrow);
     }
     syncControls(); refresh(false);
   }
   ```
   - `S.c = p.c.slice()` matters: assigning the preset's own array would let the dials edit the preset list.
   - `refresh(false)`, not `touch()`: the planes value appears in the approach's formula text.
   - The `narrow` factor keeps wide sets inside a phone-shaped stage (checked at 375 × 812:
     `out/julia-presets/phonefit-sheet-1.png`, `-2.png`; without it the wide sets are cut off at the sides,
     `phone-sheet-1.png`). On the desktop stage it is exactly 1.
   - The camera values assume the arcball camera. If the page is in fly mode, either switch to arcball first or set
     the position through whatever the camera module offers. In the 2D view skip the camera: every preset lies
     within 2 of the origin along x and 1.1 along y, so a view centred on (0, 0) about 3.6 high holds them all on a
     desktop stage. That could not be tried here, because the baseline has no 2D view.
4. **Do apply `planes`.** If it is ignored, the eleven presets with `planes: 1` come up under the default two
   planes as torn, craggy rocks (`out/julia-presets/ignored-sheet-1.png`); several look like a rendering fault.
   If you would rather not change an approach dial from the Julia panel, then at least keep the notes visible: each
   of those eleven notes ends with "Best with one plane."
5. `iter` is a smaller matter: without it the five presets still draw, as smoother blobs (the rabbit loses its
   pinch points). Their notes end with "and about 24 iterations".
6. Saved points: the same object shape works (`{ name, note: '', c, source: 'saved', planes, cam }`). When saving,
   copy `S.c`, read `planes` from `S.param.mercator.planes`, and note that a user may have slid the camera, so a
   saved point also needs `cam.target` (the shipped presets never do: their target is the origin).
7. A sentence for the panel, if wanted: "These are constants for z² + c. A constant with a y part looks cleanest
   with one plane; on the x-axis two planes give the fully 3D figure."

The presets assume the equation z^n + c with n = 2, no modifiers, no cut, and every other parameter of the
approach at its default (turn 0, lift 0). They are not reset by the code above.

## The main finding: one plane or two

With **two planes**, the approach folds space so that the xz-plane lands on the xy-plane. The fold jumps across the
plane y = 0, and the two sides only match when c is on the x-axis (the approach's own text says so). Rendered:

- c on the x-axis: clean, warty, fully 3D solids. These are the best pictures the approach makes (Basilica, San Marco,
  golden ratio, Feigenbaum, airplane).
- c with a real y part (rabbit, Siegel disc, dendrite, and so on): the solid is torn along y = 0 into mismatched
  halves and stacked sheets. The slice z = 0 is still exactly the flat set (`out/julia-presets/rab-sheet-1.png`,
  picture 3), but the solid looks broken (`cl-sheet-2.png` to `cl-sheet-5.png`, left picture of each pair).
- With **one plane** the same constants give smooth "inflated" versions of the flat set, the ones in Kučera's
  paper (right picture of each pair).

So the classics with a y part carry `planes: 1`. The assignment asked to reject presets that look broken under the
default approach; rejecting these would have removed the rabbit and most of the named list, so they are kept with
the setting that makes them right, and flagged here.

Other facts about the constant, checked numerically with two planes (`python notes/julia_port_check.py`: 0 cells
of 373,248 differ in each test):

- A constant with only a z part is the same solid as the same number put on −y. So "c along z" alone never gives
  anything new: (−0.8, 0, 0.156) is the mirror image of the classic −0.8 + 0.156i.
- Swapping the y and z parts changes nothing. Changing the sign of the y part or the z part mirrors the solid.
- So everything new lies where both y and z are non-zero, and only the wedge 0 < z ≤ y needs exploring.

## How the explored presets were found

Sweeps on the baseline, two planes, default camera, three passes each, looked at as contact sheets:

| Sweep | Constants | Sheets | Result |
|---|---|---|---|
| A | x from −1.4 to −0.4, offsets (y, z) from (0.08, 0.08) to (0.3, 0.15) | `sa-sheet-*.png` | Offsets above about 0.2 shatter the solid into dust or zebra-striped slabs. Small offsets give cracked rocks. |
| B | one plane, z from 0.15 to 0.8 added to six classics | `sb-sheet-*.png` | Onion layers with holes and stripes. Rejected: no one-plane preset has a z part. |
| C | x in {−1, −0.75, −0.6, −0.4, −0.2, 0, 0.25}, offset length 0.05, 0.1, 0.15, tilt 15°, 30°, 45° (63 constants) | `sc-sheet-1.png` to `-7.png` | The good region: a small step off both planes cracks or plates the on-axis solid without breaking it. |
| D | 27 further constants: real axis left of −1, right of 0.25, classics with a small z, larger y | `sd-sheet-*.png` | Thorn crystal and the pitted gourd. Classics with a y part stay craggy whatever z is added. |

Then camera angles (`cam1-`, `cam2-`, `cam3-`, `v2-`, `v3-sheet-*.png`) and iteration counts (`it-`, `it2-`,
`iter30-`, `iter60-sheet-*.png`). The Cracked Basilica was moved closer to the axis, from (−1, 0.06, 0.035) to
(−1, 0.045, 0.026), because the wider cracks drew with stippled edges.

Independent of the renderer, `python notes/julia_scan.py` counts the filled volume on a 120³ grid with a numpy
port of the approach's squaring rule (the port agrees with the lab's own `MATH.mercator` to 4e−15 with two planes
and 1e−6 with one, where the lab clamps at the pole). At 14 iterations all eight explored presets are one solid
piece (largest piece ≥ 99.7 % of the volume, `out/julia-presets/scan.txt`). Five keep their volume from 14 to 60
iterations (Cracked Basilica, Flint, Plated egg, Plated ball, Cracked gourd). The Thorn crystal and the Pitted
gourd lose most of theirs by 30 and the Split conch by 60, yet all eight draw as the same solids at 30 and at 60
(`iter30-sheet-2.png`, `iter60-sheet-2.png`): the renderer draws everything within a pixel of the set, so a set
that has thinned to dense dust still reads as a surface until the camera moves in close.

## The presets

`pl` = planes, `it` = iteration floor. "Critical orbit" is the orbit of 0 under z² + c (from `python notes/julia_classics.py`).

| # | Name | c | Source | pl | it | Where the value comes from, and a check |
|---|---|---|---|---|---|---|
| 1 | Basilica | (−1, 0, 0) | classic | 2 | | Centre of the period-two disc. Critical orbit has period 2, multiplier 0. |
| 2 | San Marco | (−0.75, 0, 0) | classic | 2 | | Cardioid point with turning number 1/2. Period 2, multiplier 1 (parabolic). |
| 3 | Douady rabbit | (−0.122561, 0.744862, 0) | computed | 1 | 24 | Newton's method on f³(0) = 0 from −0.12 + 0.75i, residual 2e−16. Root of c³ + 2c² + c + 1. |
| 4 | Airplane | (−1.754878, 0, 0) | computed | 2 | | Newton's method on f³(0) = 0 from −1.75, residual 4e−16. The real root of the same cubic. |
| 5 | Cauliflower | (0.25, 0, 0) | classic | 2 | | Cusp of the cardioid. Period 1, multiplier 1 (parabolic). |
| 6 | Siegel disc | (−0.390541, −0.586788, 0) | computed | 1 | | c = λ/2 − λ²/4, λ = exp(2πi·(√5 − 1)/2). Fixed-point multiplier has size 1 and angle 0.618034 of a turn. |
| 7 | Dendrite | (0, 1, 0) | classic | 1 | | c = i. Critical orbit i → −1 + i → −i → −1 + i: it lands on a repelling 2-cycle. |
| 8 | Kokopelli | (−0.15652, 1.032247, 0) | computed | 1 | | Newton's method on f⁴(0) = 0 from −0.16 + 1.03i, residual 9e−16. Root of c⁶ + 3c⁵ + 3c⁴ + 3c³ + 2c² + 1. |
| 9 | Fat rabbit | (−0.125, 0.649519, 0) | computed | 1 | | Cardioid point with turning number 1/3: c = λ/2 − λ²/4, λ = exp(2πi/3). Period 3, multiplier 1. |
| 10 | Feigenbaum point | (−1.401155, 0, 0) | classic | 2 | | −1.401155189…, the limit of the period doublings. Orbit bounded, no cycle found. |
| 11 | Golden ratio | (−0.618034, 0, 0) | classic | 2 | | c = 1 − φ. Attracting fixed point, multiplier 0.863. |
| 12 | −0.8 + 0.156i | (−0.8, 0.156, 0) | classic | 1 | 24 | Frequently shown. Critical orbit escapes at step 252. |
| 13 | 0.285 + 0.01i | (0.285, 0.01, 0) | classic | 2 | | Frequently shown. Escapes at step 19. |
| 14 | −0.4 + 0.6i | (−0.4, 0.6, 0) | classic | 1 | | Frequently shown. Escapes at step 26. |
| 15 | −0.70176 − 0.3842i | (−0.70176, −0.3842, 0) | classic | 1 | 24 | Frequently shown. Escapes at step 16. |
| 16 | −0.835 − 0.2321i | (−0.835, −0.2321, 0) | classic | 1 | 24 | Frequently shown. Escapes at step 39. |
| 17 | −0.7269 + 0.1889i | (−0.7269, 0.1889, 0) | classic | 1 | | Frequently shown. Escapes at step 431. |
| 18 | 0.45 + 0.1428i | (0.45, 0.1428, 0) | classic | 1 | 24 | Frequently shown. Escapes at step 6. |
| 19 | Cracked Basilica | (−1, 0.045, 0.026) | explored | 2 | | Sweep C, then moved toward the axis. |
| 20 | Thorn crystal | (−1.25, 0.03, 0.02) | explored | 2 | | Sweep D. |
| 21 | Split conch | (−0.75, 0.097, 0.026) | explored | 2 | | Sweep C. |
| 22 | Flint | (−0.4, 0.13, 0.075) | explored | 2 | | Sweep C. |
| 23 | Plated egg | (−0.2, 0.13, 0.075) | explored | 2 | | Sweep C. |
| 24 | Plated ball | (0, 0.087, 0.05) | explored | 2 | | Sweep C. |
| 25 | Cracked gourd | (0.25, 0.097, 0.026) | explored | 2 | | Sweep C. |
| 26 | Pitted gourd | (0.35, 0.05, 0.03) | explored | 2 | | Sweep D. |

"Frequently shown" means a value that turns up again and again in galleries and tutorials of Julia sets. No
source is claimed for them beyond that, and they have no usual name, so the value is the name. The names of
the explored presets are descriptions of the picture, made up here.

## Rejected

| Candidate | Why |
|---|---|
| c = −2 (the segment) | The set is the line from −2 to 2: one bare line on the stage. |
| c = 0.285 | Renders as the same gourd as the cauliflower and as 0.285 + 0.01i. One of the three was enough to drop. |
| c = (φ − 2) + (φ − 1)i | Within 0.03 of −0.4 + 0.6i and the same picture. |
| Any one-plane constant with a z part | Layered shells with holes and stripes (sweep B). |
| Two-plane constants more than about 0.2 off the x-axis | Dust, or slabs with zebra stripes (sweeps A and D). |

## Known limits

- **Two planes tear every constant that is off the x-axis.** The explored presets are the mild case, where the tear
  reads as a crack. Their cracks have thin stippled edges close up: the distance estimate cannot see across the jump.
- **Iteration count.** Every preset was drawn at its own setting, at 30 and at 60 iterations
  (`iter30-sheet-*.png`, `iter60-sheet-*.png`); none goes empty. Seven classics are dust in the flat sense (their
  critical orbit escapes), and three explored presets thin out the same way, so expect gaps when zooming far in
  at high iteration counts. 0.285 + 0.01i never shows its famous swirls in 3D: it stays a gourd.
- **Thin sets.** The airplane, the Feigenbaum point, the dendrite and Kokopelli are spines and wires a few pixels
  thick. They are attractive at the chosen cameras but will not survive a much coarser quality setting, and the
  airplane and Feigenbaum pictures show faint specks around the central star.
- **Other approaches.** The same constants were rendered under the lathe and the Mandelbulb approaches
  (`other-lathe-sheet-*.png`, `other-bulb-sheet-*.png`): nothing is empty, but cameras and notes were written for
  sphere inversions.
- **Colour, quality, new parameters.** Checked with the baseline's default colour mode and palette, default quality,
  dark and light themes (`light-sheet-*.png`). Not checked against the new palettes, the new distance-estimate
  modes, or non-zero turn and lift, none of which exist in the baseline.
- `tools/shot.py` once printed "the page did not finish loading in 30 s" before a run that then passed. That is
  the font link in `head.html` waiting on the network, not a page error. No run reported a console error.

## Scripts (all under `notes/`, all run with plain `python`)

| Script | What it does |
|---|---|
| `julia_classics.py` | Derives the computed constants and classifies the critical orbit of every candidate. |
| `julia_build.py` | Writes `data/julia-presets.json` from the table of names, notes, cameras and settings. |
| `julia_render.py` | Renders a list of constants on the baseline through `tools/shot.py` and tiles contact sheets. `--items data/julia-presets.json --tag final --cols 2 --per 4 --thumb 645 --passes 12` reproduces the final pictures. |
| `julia_scan.py` | Filled volume, piece count and extent of each preset on a grid, without the renderer. |
| `julia_port_check.py` | Checks that port against the lab's own `MATH.mercator`, and the symmetry facts above. |
| `julia_apply_test.py` | Checks the JSON as data, then applies all 26 presets in the page with the code in step 3. |
