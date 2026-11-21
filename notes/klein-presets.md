# Kleinian presets: what was built, what the UI must wire, and one finding for the shader

Research only. Nothing in `src/` was touched.

## Read this first

1. `data/klein-presets.json` holds **19 presets**: 10 cusps of the Maskit family, 3 values just inside it, 6 found
   by exploring (5 of them with a non-zero j part, 1 with a different step for the third map). Every one was
   checked three ways (no pearls overlap; the shader draws all of it; it is bounded and centred) and looked at.
2. **The Kleinian view loses pearls at the default ray step.** The distance estimate in `GL_KLEIN` is too large
   away from a pearl, so at "Step size, share of the estimate" = 0.8 rays step into small pearls (drawn hollow) or
   over them (missing). The richer presets lose 5 to 9% of their pixels on the baseline. There is a tested fix
   that costs almost nothing: `notes/klein-kde-exact.glsl`, a drop-in `kde()`. With it eighteen of the presets
   lose 0.2 to 2.2% and one loses 5%.
   Compare `out/klein-presets/cmp3-115.png` (left: baseline, middle: the fix, right: baseline with careful steps).
   If the fix is not taken, use a step share of 0.5 in Kleinian mode. Details in "A finding for the shader".
3. The presets are framed for a camera that looks at the origin with field of view 0.32. See "What the UI must do".

## Files

| File | What it is |
|---|---|
| `data/klein-presets.json` | The deliverable. `[{ name, note, k, cam, source }]`, UTF-8 (names and notes use μ, √, ° and ·). |
| `notes/klein_cusps.py` | Cusps by the Farey recursion and Newton's method. `cusp(p, q)`; run it for the checks and a table. |
| `notes/klein_model.py` | A model of the view that does not use the shader: lists the pearls directly, ports the shader's estimate, compares the two, finds gaps to turn out through. Also `kde_exact`, the proposed estimate. |
| `notes/klein_render.py` | Renders settings on the baseline through `tools/shot.py`, makes contact sheets, measures and sizes a picture. |
| `notes/klein_build.py` | The preset list as code. Checks every preset, sizes it, writes the JSON, renders a sheet. `--check`, `--boundary`. |
| `notes/klein_stepcheck.py` | Measures how much of each preset the ray march loses at a given step share. |
| `notes/klein_apply_test.py` | Checks the JSON as data, then applies all 19 in the page with the function given below. |
| `notes/klein-kde-exact.glsl` | The proposed `kde()` for `GL_KLEIN`. Not applied. |
| `out/klein-presets/` | `final-*.png`: every preset on the baseline at default quality. `exact-*.png`: the same with the proposed estimate. `light-sheet-*`, `phone-sheet-*`: light theme, 375 px window. `r*-sheet-*`: exploration, including the rejected ones. `shaders-exact.js`: the baseline shader file with the proposed `kde()`, for `--swap`. |

To rebuild everything: `python build.py --name klein-presets --base base`, then `python notes/klein_build.py`.

## The presets

`k` is `S.k` exactly. `cam` is the arcball camera; its target is the origin.

| # | Name | Source | μ = (mx, my, mz) | Maps | L | Centre (cx, cy, cz) | invR | Camera yaw, pitch, dist |
|---|---|---|---|---|---|---|---|---|
| 0 | 0/1 cusp, the starting view | cusp 0/1 | (0, 2, 0) | three | 1 | (1, 1, 0) | 1.2 | 0.35, 0.35, 7 |
| 1 | 0/1 cusp, one row of pearls | cusp 0/1 | (0, 2, 0) | two | 1 | (1, 1, 0) | 1.162 | -1.5708, 1.15, 6.4 |
| 2 | 1/15 cusp, spirals | cusp 1/15 | (0.011279, 1.958591, 0) | two | 1 | (-1, 0.4894, 0) | 0.8 | -1.5708, 1.15, 6.4 |
| 3 | 1/2 cusp | cusp 1/2 | (1, 1.732051, 0) | two | 1 | (-1, 0.5774, 0) | 0.879 | -1.2, 0.75, 6.4 |
| 4 | 1/3 cusp | cusp 1/3 | (0.581203, 1.693897, 0) | three | 1 | (0.2906, 0.8469, 0) | 0.662 | -1.35, 1, 6.4 |
| 5 | 2/5 cusp | cusp 2/5 | (0.766588, 1.642139, 0) | two | 1 | (1.3833, 0.8211, 0) | 0.561 | -1.35, 1, 6.4 |
| 6 | 1/5 cusp | cusp 1/5 | (0.220105, 1.766742, 0) | three | 1 | (0.1101, 0.8834, 0) | 0.465 | -1.35, 1, 6.4 |
| 7 | 1/4 cusp | cusp 1/4 | (0.352201, 1.721433, 0) | two | 1 | (-0.647, 1.2734, 0) | 0.775 | -1.35, 1, 6.4 |
| 8 | 5/13 cusp, branching | cusp 5/13 | (0.718292, 1.622179, 0) | two | 1 | (0.548, 0.855, 0) | 0.48 | -1.35, 1, 6.4 |
| 9 | 8/21 cusp, near the golden mean | cusp 8/21 | (0.700468, 1.62031, 0) | two | 1 | (-0.996, 0.293, 0) | 0.622 | -1.5708, 1.15, 6.4 |
| 10 | Above the 3/10 cusp | inside | (0.5, 1.748312, 0) | two | 1 | (-0.75, 0.8742, 0) | 0.657 | -1.35, 1, 6.4 |
| 11 | Above the 1/2 cusp | inside | (1, 1.902051, 0) | two | 1 | (-1, 0.6, 0) | 0.902 | -1.5708, 1.15, 6.4 |
| 12 | Inside, near the 0/1 cusp | inside | (0.1, 1.95, 0) | two | 1 | (1.05, 0.975, 0) | 0.982 | -1.5708, 1.15, 6.4 |
| 13 | 1/3 cusp, leaning in depth | explored | (0.581203, 1.535192, 0.715872) | two | 1 | (0.2906, 0.7676, 0.3579) | 0.656 | -1.35, 1, 6.4 |
| 14 | 2/5 cusp, leaning in depth | explored | (0.766588, 1.543106, 0.561645) | three | 1 | (1.3833, 0.7716, 0.2808) | 0.561 | -1.35, 1, 6.4 |
| 15 | 0/1 cusp, leaning 30° | explored | (0, 1.732051, 1) | two | 1 | (1, 0.866, 0) | 1.092 | -1.5708, 1.15, 6.4 |
| 16 | Leaning 30°, seen across | explored | (0, 1.732051, 1) | three | 1 | (0, 1.13, 0) | 0.862 | 0, 0.25, 6.4 |
| 17 | Leaning both ways | explored | (0.5, 1.7, 0.5) | two | 1 | (-0.988, 0.53, 0) | 0.825 | -1.35, 1, 6.4 |
| 18 | Stretched in depth | explored | (0, 2, 0) | three | 2 | (1, 1, 0) | 1.157 | 0.5, 0.5, 6.4 |

All have `iter: 60`. Preset 0 is the lab's own defaults, so it doubles as "back to the start".

What `source` means, honestly:
- `cusp p/q`: μ is the computed p/q cusp, rounded to six decimals. The framing (centre, radius, camera) is mine.
- `inside`: μ is a cusp raised by a round amount, or a round value, above the boundary. Nothing special about the
  exact numbers; any nearby value gives a similar picture.
- `explored`: found by trying values and checking them. No source beyond this work.

### How each was checked

`python notes/klein_build.py --check` prints, for every preset:
- **Clean.** The pearls are listed directly (down to radius 0.004 with two maps, 0.008 with three) and none cuts
  into another. All 19: deepest cut 0.
- **Faithful.** Of 12,000 random points, every one that the pearl list says is solid (pearls of radius 0.03 and
  up) is also solid for the shader's estimate. All 19: 0 missed.
- **Bounded.** The shader's estimate at the turning-out centre is well above zero (a centre on the limit set or
  inside a pearl gives a picture that runs off to infinity or fills the frame).

Then `notes/klein_render.py` sizes each one from a careful render so that the object reaches 0.66 of the way from
the middle of the stage to its top edge, which also fits a 375 px phone. The box around every object is centred on
the stage to within 0.07 of half the stage height (0.11 for "Above the 1/2 cusp"). In scene units every object lies
within about 1.5 of the origin.

`python notes/klein_apply_test.py`: all 19 apply at 1400 × 950 and at 375 × 812, the state equals the JSON, the
typed boxes and the third-map checkbox follow, every picture finishes, no console errors.

## The cusps

The third map of the lab is q → μ + 1/q. With a(z) = μ + 1/z and b(z) = z + 2 the trace of the word for p/q is a
polynomial in μ built by the Farey recursion in the assignment. `notes/klein_cusps.py` evaluates it, and its
derivative, by walking down the Farey tree, and solves T = 2 by Newton's method started midway between the cusps
of the two Farey parents.

Checks, all passing:
- μ(0/1) = 2i, μ(1/1) = 2 + 2i, μ(1/2) = 1 + √3·i to 2·10⁻¹⁶.
- Re μ increases with p/q over all 23 fractions with denominator up to 8, and μ(1 − p/q) = 2 − conj μ(p/q).
- μ(1/15) = 0.0112785606 + 1.9585910301i, the value usually quoted for that cusp.
- `python notes/klein_build.py --boundary`: for each of the ten cusps used, the pearl list is finite with no
  overlap at μ (deepest cut below 10⁻¹¹), and 0.02 below μ a pearl cuts into another or the list never ends. So
  each root found is the one on the edge of the family, not another root of the same polynomial.

| p/q | μ | p/q | μ |
|---|---|---|---|
| 0/1 | 2i | 3/10 | 0.5 + 1.6583123952i |
| 1/15 | 0.0112785606 + 1.9585910301i | 1/3 | 0.5812034746 + 1.6938972023i |
| 1/10 | 0.0362880775 + 1.9134232959i | 3/8 | 0.6805515403 + 1.6331702409i |
| 1/8 | 0.0673930329 + 1.8745196270i | 8/21 | 0.7004675200 + 1.6203102624i |
| 1/7 | 0.0962758122 + 1.8462756129i | 5/13 | 0.7182917991 + 1.6221790496i |
| 1/6 | 0.1427334449 + 1.8102913200i | 2/5 | 0.7665884175 + 1.6421387687i |
| 1/5 | 0.2201052046 + 1.7667417043i | 3/7 | 0.8633931442 + 1.6399579485i |
| 1/4 | 0.3522011287 + 1.7214332372i | 1/2 | 1 + 1.7320508076i |
| 2/7 | 0.4480589981 + 1.6708006397i | 1/1 | 2 + 2i |

The family repeats when μ moves by 2, so every cusp has a copy with real part between −1 and 1.

## What exploring found

These are numerical findings from the pearl list, not proofs, except where a reason is given.

- **The flat cusps stay clean with the third map on.** Tried at L = 1: 0/1, 1/15, 1/5, 1/3, 3/10 and 1/2, none
  with an overlap. For L = 1.1, 1.25, 1.5 and 2 the lowest clean my at mx = 0 and at mx = 0.5 was the same as at
  L = 1. For L below 1 only L = 0.5 came out clean, and only for some μ; 0.6 to 0.9 gave dust at every μ tried.
  Keep L ≥ 1.
- **A j part works by turning.** Turning μ about the x-axis (keeping mx, moving part of my into mz) turns the
  first two maps as a pair, so they generate the same group, rotated; that part is exact. The walls do not turn
  with them, so the pearls are different, but they still do not overlap. The rule that came out of a scan over
  (mx, mz): the picture is clean when √(my² + mz²) is at least the boundary height of the flat family at that mx
  (2 at mx = 0, 1.73 at mx = 1, as low as 1.62 near mx = 0.7), and my is at least 1.
- **The shader's own limit is tighter.** Its rule for choosing a map is a curve fitted for my between about 1.5
  and 2. Leans of 10° and 20° draw correctly for every cusp tried (0/1, 1/15, 1/3, 2/5, 1/2), and 30° for all but
  2/5, where my falls to 1.42 and 5 to 7% of the solid goes missing. At 45° (my near 1.2) the shader misses 70 to
  87% of the solid for the 1/3, 1/2 and 2/5 cusps, and at my = 1 half of it even for 0/1. So the presets stay at
  my ≥ 1.53. A dial setting with my below about 1.45 can look sparse for this reason, not because the group is
  wrong.
- **Where to turn out from.** The picture is bounded only when the centre sits in a gap, away from every pearl.
  Two kinds of centre gave the best pictures: the middle of a round gap that touches a wall (one wall becomes the
  big sphere, the rest forms a disc of pearls around it), and the point μ/2 or μ/2 + 1, about which the whole
  set has a half-turn symmetry. The second kind is a gap only at some cusps (1/3, 1/5: μ/2; 2/5: μ/2 + 1). At
  others it lies on the limit set and the picture becomes an endless string, e.g. μ/2 + 1 at 1/15.
- **Rejected:** anything with the centre on the limit set (`r1-sheet-0.png` #3, `r4-sheet-0.png` #0 to #2,
  `r10-sheet-0.png` #0 and #1); the 8/21 and 5/13 cusps turned out through their symmetric points (hollow pearls
  even with careful steps, `r10-sheet-1.png` #7, #8); centres above the plane of a two-map set (small and dull,
  `r3-sheet-0.png` #1, #2); L = 0.5 (a crowded ball, `r5-sheet-1.png` #11); close-up views near the origin
  (`r7-sheet-*.png`: striking, but they fill the frame, which the brief rules out).

## A finding for the shader (affects every Kleinian picture, not only presets)

`kde()` in `GL_KLEIN` returns (distance from the mapped point to a wall) / DF. For a pearl of radius ρ at true
distance t this equals **t · (1 + t / 2ρ)**: correct beside the pearl, too large away from it, and much too large
for small pearls. A ray that reaches a small pearl from open space takes a step longer than the gap and lands
inside the pearl or beyond it. This shows as hollow shells and as missing rims.

`python notes/klein_stepcheck.py` draws each preset at the tested setting and again with careful steps (share 0.4,
600 steps), and reports the share of the object's pixels that are lost / drawn in a clearly different colour:

| # | Name | Baseline, step share 0.8 | Baseline, step share 0.5 | Proposed estimate, step share 0.8 |
|---|---|---|---|---|
| 0 | 0/1 cusp, the starting view | 0.3 / 0.8 | 0.1 / 0.1 | 0.3 / 0.6 |
| 1 | 0/1 cusp, one row of pearls | 0.6 / 0.4 | 0.1 / 0.1 | 0.9 / 0.4 |
| 2 | 1/15 cusp, spirals | 8.6 / 5.8 | 1.6 / 2.0 | 1.2 / 2.5 |
| 3 | 1/2 cusp | 1.7 / 1.9 | 0.3 / 0.3 | 0.2 / 0.8 |
| 4 | 1/3 cusp | 5.2 / 5.8 | 0.8 / 0.8 | 0.4 / 1.2 |
| 5 | 2/5 cusp | 7.7 / 6.8 | 2.1 / 1.0 | 0.8 / 1.5 |
| 6 | 1/5 cusp | 7.1 / 7.4 | 1.5 / 1.7 | 0.4 / 1.7 |
| 7 | 1/4 cusp | 5.4 / 4.1 | 1.1 / 0.7 | 0.4 / 1.4 |
| 8 | 5/13 cusp, branching | 8.7 / 6.0 | 2.4 / 1.8 | 5.3 / 2.1 |
| 9 | 8/21 cusp, near the golden mean | 7.5 / 5.3 | 1.7 / 1.1 | 1.7 / 1.4 |
| 10 | Above the 3/10 cusp | 3.2 / 2.7 | 0.4 / 0.3 | 0.3 / 1.0 |
| 11 | Above the 1/2 cusp | 0.5 / 0.4 | 0.1 / 0.0 | 0.8 / 0.3 |
| 12 | Inside, near the 0/1 cusp | 1.3 / 1.4 | 0.3 / 0.4 | 0.9 / 0.7 |
| 13 | 1/3 cusp, leaning in depth | 4.8 / 3.1 | 0.8 / 0.6 | 1.6 / 1.3 |
| 14 | 2/5 cusp, leaning in depth | 9.4 / 6.4 | 2.7 / 1.8 | 2.2 / 2.2 |
| 15 | 0/1 cusp, leaning 30° | 0.6 / 0.6 | 0.2 / 0.1 | 1.2 / 0.1 |
| 16 | Leaning 30°, seen across | 3.8 / 0.4 | 0.8 / 0.1 | 0.6 / 0.4 |
| 17 | Leaning both ways | 1.7 / 1.8 | 0.2 / 0.2 | 0.4 / 0.6 |
| 18 | Stretched in depth | 0.5 / 0.4 | 0.2 / 0.1 | 0.8 / 0.3 |

(percent lost / percent changed)

**The fix.** Carry one more point, W, through the same maps as z, starting at infinity (where the two walls
touch). At each step the pearl being met is the sphere that the maps so far carry onto a wall, and its radius
follows from W: ρ = |z − W|² / (2·D·DF), with D the distance from W to that wall. Solving for the true distance:

    t = E · 2 / (1 + √(1 + 4·h·D / |z − W|²)),   E = h / DF,   h = distance from z to the wall

That is one extra inversion and one square root per step. `notes/klein-kde-exact.glsl` is the complete function;
it replaces `kde()` and changes nothing else (same uniforms, hooks, `gIt`, `gLast`).

Evidence:
- Against the pearl list (`kde_exact` in `notes/klein_model.py`, 4,000 points each for five groups): the new
  value falls below the true distance for none of the points in four groups and 0.3% in the fifth (within the
  error of the list), its median ratio to the true distance is 1.00 in all five, and its 90th percentile is 1.04
  to 1.54 where the present estimate has 1.58 to 1.92.
- In the page, on the baseline: the table above, and `out/klein-presets/exact-*.png` against `final-*.png`.
- It also compiles and draws inside the shader file as it stood in `src/` late in this round
  (`live-exact-sheet-*.png`, no console errors), where `kde()` was still word for word the baseline's.
- What it does not fix: a pearl that the search never meets (one that belongs to a neighbouring cell) is still
  not measured. That is why 5/13 keeps 5% and why a smaller step share still helps a little.

To try it: `python build.py --name klein-presets-exact --base base --swap js/30-shaders.js=out/klein-presets/shaders-exact.js`.

## What the UI must do

1. Copy the array into `src/js/75-presets.js` (suggested name `KLEIN_PRESETS`). Keep the order: it runs from the
   lab's starting view through the cusps in order of p/q complexity, then inside, then explored. If the list is
   grouped, group by the first word of `source`: `cusp` ("Cusps: pearls that just touch"), `inside` ("Inside the
   family: strings that do not close"), `explored` ("Found by exploring").
2. Show `name` in the list and `note` as the one-line description of the chosen preset. `source` can be shown as
   a small tag; for cusps it carries the fraction.
3. On click (this exact logic passes `notes/klein_apply_test.py` on the baseline):

   ```js
   function applyKleinPreset(p) {
     Object.assign(S.k, p.k);              // all ten fields, `three` is a boolean
     $('k3').checked = S.k.three;          // or however the third-map checkbox is now built
     S.view.fly = false;                   // the framing is an arcball position
     cam.yaw = p.cam.yaw; cam.pitch = p.cam.pitch; cam.dist = clampDist(p.cam.dist); cam.target = [0, 0, 0];
     syncControls();
     touch();
   }
   ```
   If the camera module keeps a separate eased zoom target, set that to `p.cam.dist` as well, or the picture will
   drift back.
4. The framing assumes `S.view.fov = 0.32`, `S.view.bound` ≥ 3 and `S.view.zmin` ≤ 6.4 ≤ `S.view.zmax`. All
   three hold by default. If the field of view has been changed, use `dist · 0.32 / S.view.fov`.
5. Dial ranges. Every value is inside the hard limits of the baseline Kleinian dials, but some are outside the
   slider ranges: `mx` reaches 1 (slider ±0.5) and `mz` reaches 1 (slider ±0.8). Suggested sliders: `mx` −1 to 1,
   `mz` −1 to 1, `my` 1.4 to 2.4. The values have at most six decimals, so the new typed boxes show them exactly.
6. "Reset" for the Kleinian panel can simply apply preset 0: it equals the defaults of `S.k` and the Kleinian
   camera of `resetCam()`.
7. 2D view: for the two-map presets with mz = 0 and cz = 0 (1 to 3, 5 and 7 to 12) the slice z = 0 is the classic
   flat picture of that group, turned inside out. With the third map on, pearls from the rows in front and behind
   can add their own discs. A view of height about 4.5 centred on (0, 0) holds every preset. Not tested: the 2D
   view does not exist on the baseline.
8. Ray step. Either take the proposed `kde()` into `GL_KLEIN` (preferred: it is the small integration fix that
   makes these presets look as in `exact-*.png`), or lower the step share to 0.5 when the mode is Kleinian. Left
   as it is, presets 2, 4 to 9, 13 and 14 show ragged rims and a few hollow pearls.

Sentences the Kleinian panel can reuse:
- "Each preset sets the group (μ, the third map and its step), the sphere the picture is turned out through, and
  the camera."
- "At a cusp the strings of pearls just touch. Above it they hang apart. Below it they overlap and the picture
  turns to dust."
- "A rule of thumb for a clean picture: the i and j parts of μ together, √(i² + j²), should be at least the
  boundary height for its real part (2 at 0, about 1.7 at ±1, never below 1.62), and L at least 1."
- "Move the centre of the turning-out sphere and the same group gives a different picture. Keep it in a gap
  between pearls: on a pearl, the picture fills the stage."

## Names added

Nothing was added to `src/`. In the JSON: the five fields `name`, `note`, `k`, `cam`, `source` as specified, and
nothing else. Suggested for files the UI owns: `KLEIN_PRESETS`, `applyKleinPreset(p)`. Proposed for the shader:
a local `W` (and locals `x0`, `z0`, `zw`, `kk`, `h0`, `h1`, `c0`, `c1`) inside `kde()`.

In `notes/`: `cusp`, `cusp_any`, `trace`, `parents`, `farey` (klein_cusps); `pearls`, `kde`, `kde_exact`,
`de_display`, `missed`, `gaps`, `clearance`, `in_pearl`, `tiles`, `display_extent`, `form`, `tr`, `J`,
`wall_vectors`, `to_ball` (klein_model); `render`, `measure`, `fit`, `HIDE_UI` (klein_render); `presets`, `check`,
`boundary`, `mu_of`, `centre` (klein_build); `stepcheck`, `compare` (klein_stepcheck).

## Known limits

- Framed for a camera target at the origin. The schema has no target, and none is needed: every object is centred.
- Pictures were judged on the baseline renderer with the default palette. Presets 14 and 16 (a j part with the
  third map on) show a sharp colour seam across the largest pearl under the three-tone orbit trap. It is the
  colouring, not the shape.
- Sizes were set with careful ray steps. At the default step the baseline draws a slightly smaller object
  because it loses the rim.
- The pearl list fills in slowly at long cusps (at 1/15, listing down to radius 0.0007, it still misses about 9%
  of the area the shader finds solid in the plane), so the "faithful" check only covers pearls of radius 0.03 and
  up, and it cannot see dust finer than the listing radius. The boundary check is good to about 0.01 in μ.
- The turning rule for the j part is a numerical finding. It was confirmed on a 5 × 5 grid of (mx, mz) and on
  leans of the 0/1, 1/15, 1/3, 2/5 and 1/2 cusps, not proved.
- Drawing time on this shared machine at Balanced quality: up to about 30 s for the last refining pass of the
  slowest preset; the first full picture comes much sooner.

## Round 4: fifteen entries that move the turning-out sphere

Added for the user's remark N9 ("you also don't have any klein presets that mess with the turning-out sphere").
Nothing was removed and the first nineteen entries are unchanged. Full account: `notes/r4-kleinian.md`.

Every new entry reuses a group that is already in the list and changes only the sphere: its centre, and with it
the radius that makes the picture fit. Each has `"group": "Turning-out sphere"`, a `source` that starts with
`sphere`, and a camera with a `target` (the object is no longer centred on the origin when the centre leaves the
middle of a gap). `iter` is 60 as in the other entries; the page ignores it.

| # | Name | mu | Maps | Centre | invR | Room around the centre | Camera yaw, pitch, dist, target |
|---|---|---|---|---|---|---|---|
| 19 | 0/1 cusp, sphere moved to one side | (0, 2, 0) | two | (0.55, 1, 0) | 0.958 | 0.554 | -1.35, 1, 6.4, (-0.412, -0.033, 0.138) |
| 20 | 0/1 cusp, sphere close to a wall | (0, 2, 0) | two | (1, 0.45, 0) | 0.892 | 0.45 | -1.35, 1, 6.4, (0.005, -0.707, 0.342) |
| 21 | 0/1 cusp with the third map, sphere moved in depth | (0, 2, 0) | three | (1, 1, 1) | 1.14 | 1.0 | 0.5, 0.45, 6.4, (0.004, 0.166, 0.04) |
| 22 | 0/1 cusp with the third map, sphere moved across and in depth | (0, 2, 0) | three | (0, 1, 1) | 1.097 | 1.0 | 0.5, 0.45, 6.4, (0.082, 0.104, 0.03) |
| 23 | 0/1 cusp with the third map, sphere close to a wall | (0, 2, 0) | three | (1, 0.5, 0) | 0.967 | 0.5 | 0.5, 0.45, 6.4, (0.147, -0.578, 0.169) |
| 24 | 1/2 cusp, through the gap under the upper wall | (1, 1.73205, 0) | two | (0, 1.1547, 0) | 0.814 | 0.577 | -1.35, 1, 6.4, (-0.01, -0.138, 0.264) |
| 25 | 1/2 cusp, small sphere in a narrow gap | (1, 1.73205, 0) | two | (0.8707, 0.2015, 0) | 0.593 | 0.18 | -1.35, 1, 6.4, (-0.274, -0.8, 0.415) |
| 26 | 1/3 cusp, through a side gap | (0.581203, 1.6939, 0) | two | (-0.418, 1.2213, 0) | 0.758 | 0.472 | -1.35, 1, 6.4, (-0.01, -0.154, 0.287) |
| 27 | 1/3 cusp, small sphere beside the large pearls | (0.581203, 1.6939, 0) | two | (0.997, 0.7236, 0) | 0.65 | 0.223 | -1.35, 1, 6.4, (0.006, 0.648, 0.215) |
| 28 | 1/4 cusp, small sphere between the strings | (0.352201, 1.72143, 0) | two | (0.3527, 0.6928, 0) | 0.549 | 0.243 | -1.35, 1, 6.4, (0.005, 0.003, 0.191) |
| 29 | 1/4 cusp, sphere lifted off the plane | (0.352201, 1.72143, 0) | two | (-0.647, 1.2734, 0.5) | 0.88 | 0.448 | -1.2, 0.6, 6.4, (0.034, 0.116, 0.024) |
| 30 | 2/5 cusp, sphere in the middle gap | (0.766588, 1.64214, 0) | two | (0.6174, 0.8202, 0) | 0.532 | 0.232 | -1.35, 1, 6.4, (0.06, -0.041, 0.208) |
| 31 | 1/15 cusp, through the opposite gap | (0.011279, 1.95859, 0) | two | (0.9823, 0.4457, 0) | 0.766 | 0.442 | -1.35, 1, 6.4, (-0.045, -0.119, 0.282) |
| 32 | Leaning 30°, sphere lifted off the plane | (0, 1.73205, 1) | two | (1, 0.866, 0.5) | 1.052 | 0.866 | -1.2, 0.6, 6.4, (-0.008, -0.202, 0.051) |
| 33 | Leaning 30° with the third map, sphere moved across and in depth | (0, 1.73205, 1) | three | (0, 0.866, 1) | 0.732 | 0.289 | 0.5, 0.45, 6.4, (0.237, 0.66, -0.001) |

"Room around the centre" is the distance from the centre to the nearest pearl or wall, from the pearl list. The
smaller it is, the larger the nearest pearls come out and the smaller the radius has to be.

Kinds of centre, and what each does to the picture:
- **To one side of a gap, or close to a wall** (19, 20, 23): the nearest wall or pearl grows into one large ball and
  the others gather round it.
- **Another gap of the same group** (24, 26, 30, 31): a different picture of the same pearls. Away from the gap in
  the middle the half-turn symmetry is gone.
- **A small sphere in a narrow gap** (25, 27, 28): one neighbourhood shown large.
- **Off the plane the pearls lie in** (29, 32): the flat disc of a two-map group curls into a bowl or a ball.
- **Moved in depth with the third map on** (21, 22, 33): the same lattice of pearls from another gap of it.

What each needs: the default field of view and a drawing radius of 3 or more (as the first nineteen), nothing
else. They were drawn at depth 150 (Fine, 1400x950), at depth 60, and at 375x812; the pictures at 60 and 150 do
not differ visibly (`out/r4/kleinian/shots/fine-sheet-*.png`, `d60-sheet-0.png`, `phone-sheet-0.png`).

How they were checked before drawing (`out/r4/kleinian/find.py`): the centre lies in a gap, and every pearl that
will look big in the picture is whole for the shader's search (14 random points inside each of the largest pearls
must all come out solid). The second check is new this round. The first nineteen were only tested for pearls of
radius 0.03 and up, and entry 8 (5/13 cusp) fails it: the five pearls nearest its centre are invisible to the
search, and one shows as a sliver at the lower left. Its centre was left as it is.

Rejected candidates are in `out/r4/kleinian/shots/try1-sheet-*.png`: mostly two plain wall spheres with little
between them (centres far off the plane of a two-map group, as the first round also found), and one centre on the
1/15 cusp that gave an endless string.
