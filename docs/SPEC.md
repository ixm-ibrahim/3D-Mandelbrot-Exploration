# This round: what the user asked for, what was decided, and who builds what

Read `docs/CONTRACT.md` first. It defines the files, the rules and the interfaces this document refers to.

## The user's feedback, verbatim

> 1. loading bar or something in some corner whenever something is thinking - like when I changed to lambda, it just froze for a bit, same with when I clicked on anything else.
> 2. the textbox part of sliders don't work properly in edge cases or if the increment is not 1 or if it is a non-integer or if it is an integer, like all this has to be checked and make sense. Also, it would be nice if I could toggle integer increments with individual textboxes, as sometimes I want to go up by the normal decimal amount (when clicking on the up and down arrows) and other times by integers.
> 3. the colors are boring. and there are no orbit trap options? like cross or ray or whatever that people commonly use
> 4. the zoom steps are jumpy, like when I scroll with the scroll wheel
> 5. an ultra fast setting, since even fast is still slow.
> 6. for julia sets, would be nice to have a list of saved 3d points to just jump to - and have some already populated from known pretty julia sets
> 7. for the camera, switch between fps and arcball (how it currently is) as some button inside the render
> 8. have a all-reset button for the different sliders, like for the klein parameters. also, as with the julia set locations above, would be nice to have a set of known pretty parameters for the klein fractals. also, there seems to be a zoom out limit? would be nice to have a slider on the left or right side that represents where we are in the zoom between the min and max zoom, and being able to limit that. but in addition to the klein stuff, it seems like it just maxes out at some radius - would be nice to increase that (unless it's there already, and if it is then I don't know what it is)
> 9. it seems odd to me that you removed the sphere inversions - like if circle inversions can create the mandelbrot, it's odd to me that sphere inversions can't create a shape that at z=0 - which is a slice that is a circle - will create the Mandelbrot shape. so try to find an approach that does this please
> 10. for the mercator approach, you say "rebuilt by eye because the paper leaves its construction out". are you manually doing something rather than procedurally doing something? I would have expected you to just figure this out. Also, there seems to be some pattern here - like for power n = 8, I would expect 8 bulbs - but this only happens if the "planes that carry the flat set" is p=4. Same for n=6 - 6 bulbs only appear when p=3. And continuing the pattern, n = 4 is matched with p=2. But inconsistently, for n=2 the normal case, a p=1 is just an inflated mandelbrot, which looks wrong. So idk what the "correct" approach should be here, if this is something to consider at all.
> 11. now this would be really cool - you know how the mandelbrot can be constructed by each pixel representing a julia set? like there is this picture on wikipedia that shows this really cool-like - it would be awesome to have some checkbox in the mandelbrot view that shows this in 3d
> 12. on that note, it would be awesome to have a 2d view of things too - like a checkbox above "show" that switches to a 2d view of everything (so just the z=0 cross section of everything, which should speed things up if I wanted to just see the z=0 slice
> 13. also, perhaps a collapse all button somewhere intuitive in case I want to collapse everything quickly to find another section
> 14. also, doesn't the normal mandelbulb have like an alpha or theta or phi offset to it that can "animate" the mandebulb making it pulse from the poles, or something like that? I forget how it works exactly. Is there an equivalent to the mercator approach, since at least with n=8 it looks so similar?
> 15. how come I can't do negative powers of n? add this please

The user is not a mathematician, wants things to be "elegant, repeatable with different equations", and judges
by how the pictures look and how the controls feel. An earlier requirement still stands: **for every approach
the plane z = 0 must behave exactly like the ordinary 2D case** (the classic Mandelbulb is the one labelled
exception, kept only as a rendering benchmark).

## A result that shapes items 9 and 10 (established and checked numerically by the orchestrator)

There is an exact identity in the plane: with ωₖ the n-th roots of unity,

    zⁿ = 1 + n / Σₖ ωₖ / (z − ωₖ)

Every `1/(…)` is a circle inversion (followed by a mirror), so the power map is built exactly from n + 1
inversions, by adding them. Replace the circles by spheres: write a point of space as q = x + yi + zj, read
`1/q` as the quaternion reciprocal `(x, −y, −z)/|q|²` (a sphere inversion and a flip), and read "times ωₖ" as a
turn about the z-axis by the angle of ωₖ. Apply the formula to the unit direction d = v/|v| and scale by |v|ⁿ:

    vⁿ = |v|ⁿ · [ 1 + n · inv( Σₖ Rₖ · inv(d − ωₖ) ) ]

On the unit sphere this equals, to rounding error, the existing "Mercator" rule (longitude × n, Mercator
latitude × n) for n = 2, 3, 4, 5, 8 (script: `notes/invcheck.py`). So the Mercator approach **is** the
sphere-inversion construction, derived, not guessed. The earlier claim on the page that inversions cannot give
the exact flat set was wrong as worded: chains of inversions cannot, sums of inversions can.

## Decisions, item by item

1. **Busy indicator, no freezes.** Shader programs compile without blocking (extension
   `KHR_parallel_shader_compile`, polled), the last picture stays up meanwhile, and `setBusy` shows a label.
   The scorecard measurement runs in small slices across frames. A thin progress bar on the stage shows
   drawing progress.
2. **Typed boxes.** A custom box (text input, not `type=number`) with its own up/down buttons, a per-dial
   toggle between the fine step and whole-number steps, and well-defined behaviour for every edge case
   (see the dial assignment).
3. **Colour.** Many more palettes, including vivid ones, and real orbit-trap choices (point, cross, axis
   line, planes, sphere shell, ring, ...), with a choice of what the trap colours by.
4. **Smooth zoom.** Wheel zoom eases toward a target instead of jumping.
5. **Ultra fast.** A new distance-estimate mode that carries no neighbouring orbits (`S.q.de = 0`), plus an
   "Ultra fast" preset (half resolution, one pass, no shadows).
6. **Julia points.** A list of classic Julia constants to jump to, plus the user's own saved points
   (kept in localStorage when available).
7. **Camera modes.** A button on the stage switches between arcball and first-person fly.
8. **Resets, Kleinian presets, zoom limits.** A reset button per section; a list of Kleinian presets; a
   vertical zoom slider on the stage edge with editable nearest/farthest limits; the drawing radius
   (`S.view.bound`) becomes adjustable.
9. **Sphere inversions.** See the result above: present the Mercator approach as the sphere-inversion
   approach, with the derivation. If a second genuinely different inversion-built variant is worth having
   (spheres fixed on the unit sphere instead of following the point), offer it as an option.
10. **"By eye" and the planes question.** Remove "rebuilt by eye": the rule is a formula, now derived. Explain in
    the panel that the number of planes is a free choice: p planes give 2p fins around the x-axis whatever the
    power is, the paper's 3D figure is p = 2 at n = 2, and the flat set's own (n − 1)-fold symmetry is a turn
    about the z-axis, a different thing. Allow up to 8 planes.
11. **Julia mosaic.** In Mandelbrot mode a checkbox fills space with a grid of small Julia sets, each cell
    showing the Julia set of the constant at its centre (the 3D version of the Wikipedia picture).
12. **2D view.** A checkbox above "Show" draws only the slice z = `S.cut` as a flat picture, with pan and zoom.
13. **Collapse all.** One button near the top of the sidebar collapses or expands every section.
14. **Phase offsets.** The two Mandelbulbs get phase dials (with a play button). The Mercator approach gets
    the equivalent: a turn (longitude offset) and a lift (Mercator-latitude offset), i.e. ζ → k·e^{iφ}·ζⁿ.
15. **Negative powers.** The power dial runs from −8 to 10 and every approach handles negative n.

## Assignments

Each assignment lists the files you own, what to build, and how it will be judged. Test with
`python build.py --name <you> --base base --use <your files>` and `python tools/shot.py --url dist/<you>.html ...`.
Save screenshots in `out/<you>/` and look at them with the Read tool: judge the pictures as the user would.
Write `notes/<you>.md` with what you built, the names you added, and anything the UI integrator must know.

### dial  (`src/js/70-dial.js`, `src/css/70-dial.css`)
Rebuild the controls kit behind the API in the contract.
- The typed box is `<input type="text" inputmode="decimal">` with id `id + 'Num'`, plus two small step
  buttons (up, down) and, unless the dial is whole-number-only, a toggle that switches the step between
  the dial's fine step and 1. The toggle shows the step it will use (for example "±0.1" / "±1").
- Stepping (buttons, ArrowUp/ArrowDown in the box; Shift or PageUp/PageDown = ten steps):
  fine mode adds or subtracts exactly one step from the current value, whatever it is (2.37 → 2.47, no
  snapping to a grid); whole-number mode goes to the next whole number above or below (2.37 → 3, 2.37 → 2,
  3 → 4). Results are cleaned of floating-point noise (no 2.4000000000000004).
- Typing: commit on Enter or when focus leaves; Escape restores the old value. Accept a leading unicode
  minus, surrounding spaces, a decimal comma, and scientific notation. Anything that is not a number
  restores the old value and flags the box briefly (`aria-invalid`). Out-of-range values clamp to `lo/hi`.
  `int` rounds; `odd` moves to the nearest odd whole number. The wheel never changes a value.
- Display: at most 6 decimals, trailing zeros trimmed, never exponent notation for ordinary sizes, and a
  proper minus sign is not required (plain "-" is fine, it must round-trip).
- The slider shows the nearest position when the value is outside its range, and must not write that
  clamped position back into the state unless the user moves it.
- `animate: true`: a play/pause button that sweeps the value across the slider range and wraps, about one
  sweep per 8 seconds, calling the setter each frame; pauses when the control is hidden or reset.
- `help`: shown as a small note under the dial.
- `buildControls` supports `dial`, `select`, `check`, `note`, and `when` (re-evaluated after every change
  and on `sync()`). `resetGroup(group)` and `syncControls()` as in the contract.
- Layout: label, box cluster and slider must fit a 320 px wide column and a 375 px phone, in both themes,
  with visible focus rings.
- Ship `tests/dial.html` + `tests/dial.json` (a `tools/shot.py --actions` script) that load your kit alone
  and assert every rule above in page JavaScript, printing a pass/fail list. All must pass.

### approaches  (`src/js/10-approaches.js`, `src/js/20-formula.js`)
- Rename the Mercator approach to "Sphere inversions" (keep `id: 'mercator'`), and rewrite its texts around
  the derivation above: `formula(p, n)` should show the inversion form; `about` explains it in plain words,
  says it reproduces the Julia figures in Kučera's paper (one plane: his "inflated" sets; two planes: his
  "truly 3D" figure) and no longer says "rebuilt by eye". Keep it short.
- Its params (at most four with keys, order = `uA` components): `planes` (whole, 1 to 8, default 2),
  `turn` (longitude offset in degrees, −180 to 180, default 0, `animate`), `lift` (offset added to the
  Mercator latitude after multiplying, about −2 to 2, default 0, `animate`). Add a `note` spec explaining
  the planes choice as in decision 10.
- Investigate the "fixed spheres" variant: apply the inversion formula to the point itself (spheres stay
  on the unit sphere) instead of to its direction. It is exact at z = 0 but not length-preserving off the
  plane. Characterise it numerically (does the set stay bounded, what does a slice look like). If it gives a
  usable, different object, add it as a fourth param `fixed` (a `check`); if not, leave it out and record
  why in your notes.
- Both Mandelbulbs: add phase params in degrees with `animate` (equator version: latitude phase and longitude
  phase; classic: θ phase and φ phase), added after the angle is multiplied. Default 0.
- Negative powers: make `pw`, `sqr`, `mul` and `MATH` correct and finite for every approach when n < 0
  (and for |n| < 1), including at the origin, and make each approach's texts (`formula`, `crush`, `smooth`,
  `slice`, `roundNote`) read correctly for negative n and for non-zero offsets (with a turn the plane z = 0
  carries e^{iφ}zⁿ, a turned copy of the flat set; say so plainly).
- `PRESETS`: add at least two negative-power presets (for example `z^-2 + c`) with sensible start values and
  camera hints, and check every preset still compiles with `compileFormula`.
- Prove parity: a script (page JavaScript run through `tools/shot.py`) that checks, for each approach and
  n in {−3, −2, −1, 2, 3, 8}, that `MATH` agrees with complex zⁿ in the plane z = 0 when offsets are zero
  (classic excepted), and that the inversion formula agrees with `MATH.mercator` on the unit sphere.
- Write `notes/inversions.md`: the derivation in plain language, the numeric evidence, and two or three
  sentences the UI can reuse to explain it to a non-mathematician.

### colour  (`src/js/25-colour.js`)
- At least twelve palettes, including several vivid ones (think of the palettes people actually use for
  fractals: fire, electric, sunset, rainbow, ocean, neon on dark, plus two or three restrained ones). Each
  must look good on the dark stage and the light stage. Five stops is the current format; you may change the
  format (you own `pal()` and the uniforms) but keep `PALETTES[i][0]` as the name.
- Orbit traps as a proper family: point (with a movable centre), cross (the three axis lines), a single axis
  line, the coordinate planes, a sphere shell (radius dial), a ring in the xy-plane (radius dial), and the
  existing three-tone mix. Let the user choose what is mapped to colour: nearest distance, the step at which
  the orbit came nearest, or a blend with the escape count.
- Keep the other modes (escape count, distance from centre, depth, direction of the last step, surface
  direction, plain clay). Add a "reverse palette" check. Make the default look lively, not beige.
- `flatColour(p, d, px)` for the 2D view: solid interior (`uCutCol`), exterior coloured by the current mode
  where that makes sense (escape count and traps do), a crisp anti-aliased edge using `d / px`.
- All of it through `COLOUR_CONTROLS` with `when` so only relevant dials show.
- Check by screenshot on the baseline: classic Mandelbulb at n = 8, the sphere-inversion Julia set at
  c = (−1, 0, 0), and the Kleinian view, each with at least four palette/trap combinations, in dark and light
  (`--theme light`). The 2D view does not exist in the baseline, so keep `flatColour` simple and robust.

### shaders  (`src/js/30-shaders.js`)
- `uBound` replaces the constant `BOUND`.
- Distance-estimate modes by `uNT`: 3 (as now), 1 (as now), and **0: no neighbouring orbits**. In mode 0
  carry a single scalar stretch estimate through the orbit (for example `dr = pn * (|w| + ε) / (|v| + ε) * dr + (julia ? 0 : 1)`)
  and use it in the same distance formula; slope then comes from sampling. It must be visibly faster and still
  recognisable.
- **Mosaic** (`uMosaic > 0`, Mandelbrot mode): space is cut into cubes of side `uMosaic`; inside each cube the
  distance estimate is that of the Julia set whose constant is the cube's centre (after `cmap`), scaled to fit
  the cube with a small margin. Rays must be able to pass from cube to cube (limit each step by the distance
  to the cube wall plus a little). It must also work in the 2D view.
- **2D view** (`uFlat > 0.5`): each pixel is the slice point `(uFlatC + uv * uFlatH / 2, uSliceZ)`; run the
  same orbit (any approach, equation, modifiers, Julia or Mandelbrot or mosaic, and the Kleinian set) and
  output `flatColour(p, d, px)`. No ray march. Picking returns the slice point.
- Negative powers and poles: the orbit must stay finite (no NaN reaching the screen) when `uPow < 0` or the
  formula divides by z, including starting at z = 0. Decide and document what "escaped" means there.
- Keep the hook contract with 25-colour.js exactly, and the uniform table in the contract exactly.
- Check by screenshot on the baseline (set uniforms through `window.squaringLab.S`; the baseline renderer
  does not set the new uniforms, so default them sensibly in the shader when they are zero, e.g. treat
  `uBound == 0.0` as 8): default view, classic n = 8, Kleinian. Anything that needs the new renderer or camera
  is checked after integration; make it robust.

### render  (`src/js/40-render.js`, `src/css/40-render.css`)
- Compile scene programs without blocking: use `KHR_parallel_shader_compile` when present; keep drawing the
  previous program's last picture (do not clear the stage) while the new one compiles; show
  `setBusy('compile', 'Preparing the formula')`; when it finishes, draw. Without the extension, show the busy
  label, yield one frame, then compile. A failed compile reports in the stage as now and clears the busy label.
- Set every uniform in the contract's table, including the new ones (`uBound`, `uMosaic`, `uFlat`, `uFlatC`,
  `uFlatH`, `uSliceZ`), and `uNT` from `S.q.de` (0, 1 or 3) for the final passes. The moving preview uses
  `min(S.q.de, 3)` too, so "ultra fast" stays cheap. Exact slope (`uAnalytic`) only when `uNT == 3`.
- 2D view (`S.flat`): the same schedule works, but there is no ray march, so the preview can be full size.
- A thin progress bar along the bottom edge of the stage: fraction of the full-quality drawing done
  (bands and passes). Hidden when idle. Keep the status line text.
- Keep: the preview/band/pass schedule, timing-based band sizing, the background-tab timer fallback,
  context-loss handling, `renderIdle()`, `viewChanged()`, `pick()`. Picking must work in the 2D view.
- Nothing may block the page for longer than about 50 ms on a mid-range laptop GPU except the first use of
  a program on a driver without parallel compile.
- Check on the baseline build: switching approach and equation shows the busy label and never freezes
  input (measure the longest gap between animation frames around a switch and report it), the progress bar
  moves, all smoke-test pictures still match `tools/smoke.json`.

### camera  (`src/js/50-camera.js`, `src/css/50-camera.css`)
- **Smooth zoom:** wheel input changes a target distance; the camera eases to it over roughly 120 ms
  (frame-rate independent), calling `touch()` while moving. One mouse-wheel notch changes distance by about
  12%; pixel-precise trackpads scale smoothly. Zoom buttons use the same easing.
- **Camera modes:** a small button inside the stage (top right area, below the busy indicator's place)
  toggles arcball / fly. Fly: drag looks around; W A S D (and arrow keys) move, Q/E or Space/Shift move down/up;
  speed is `S.view.speed` scene units per second, the wheel changes speed, and movement continues while keys
  are held. Switching modes keeps the current position and view direction. `basis()` stays the single source
  the renderer uses. Show a one-line hint for the active mode (replace the text of the existing `.hint`).
- **Zoom slider:** a vertical slider on the stage's right edge showing where the distance sits between
  `S.view.zmin` and `S.view.zmax` on a log scale; dragging it zooms. Small editable boxes at its two ends set
  the nearest and farthest limits (you may build these with `addDial`'s typed box or simple inputs; they must
  accept typed numbers). Keep it clear of the bottom-right buttons and usable on a phone.
- The farthest distance may exceed the drawing radius; do not tie them, but make the default farthest limit
  generous (about 60) and let it go to 1000.
- **2D view** (`S.flat`): drag pans `S.v2.x/y`, wheel and pinch zoom `S.v2.h` about the cursor, the zoom
  slider maps `S.v2.h`, double-click centres. Arcball/fly input is inactive while flat.
- `resetCam(preset?)` covers all modes including Kleinian and 2D. Touch: one finger turns or pans, two
  fingers pinch-zoom and slide.
- You create your own overlay elements inside `#stage` from `bindView()` and style them in your CSS file.
  Register `drawTriad` on `hooks.view` yourself (guard against double registration).
- Check on the baseline by driving synthetic events from page JavaScript (wheel, pointer, key) and by
  screenshot: zoom easing reaches its target without overshoot, fly movement changes `basis().pos`, the
  slider tracks the distance, limits clamp.

### measure  (`src/js/60-measure.js`)
- `updateCard()` must not block: do the 6,000-sample measurement in slices of a few milliseconds across
  frames (show `setBusy('measure', 'Measuring the approach')` while it runs; a newer call cancels an older one).
  Keep `measure(F, n)` as a plain synchronous function for tests.
- Make every sentence in the scorecard and the figure captions correct for negative n, n between −1 and 1,
  and for approaches with offsets (use the approach's own `crush/smooth/slice/roundNote`, which now receive
  `(p, n)`; `roundNote` may be a string or a function).
- The "one step" figures must not break for negative n (circles shrink or grow sensibly; guard against
  infinities at the origin).
- Register `drawStep3d` on `hooks.view` yourself from `buildCard()` (guarded).
- Check: time `updateCard()` (the call must return in under 5 ms and the longest slice stay under 12 ms), and
  compare the final numbers with the synchronous `measure` for three approaches.

### klein-presets  (`data/klein-presets.json`, `notes/klein-presets.md`)
Research only: do not edit `src/`.
- Compute boundary ("cusp") parameters of the Maskit family the Kleinian view uses. In the lab's notation the
  third map is q → μ + 1/q with μ = `mx + my·i + mz·j`, and `mx = Re μ`, `my = Im μ`. The classic p/q cusps are
  the solutions of trace polynomials built by the Farey recursion T(0/1) = −iμ, T(1/0) = 2, T(1/1) = −iμ + 2i,
  T((p+r)/(q+s)) = T(p/q)·T(r/s) − T((p−r)/(q−s)), solved for T = 2 by Newton's method starting between the
  Farey parents. Known values to verify against: μ(0/1) = 2i, μ(1/1) = 2 + 2i, μ(1/2) = 1 + √3·i.
- Produce at least twelve presets: several cusps (touching pearls), a few values just inside the family
  (separated pearls), and several with a non-zero j part found by exploring. For each, find a framing
  (turning-out sphere centre and radius, third map on/off, L, recursion depth, camera yaw/pitch/dist) that
  gives a good-looking, bounded picture, by rendering it with `tools/shot.py` on the baseline build (set
  `S.k` and `cam`, mode `k`) and looking at the result. Reject any that render as dust or fill the frame.
- Output JSON: `[{ "name", "note", "k": {mx,my,mz,three,L,iter,invR,cx,cy,cz}, "cam": {yaw,pitch,dist}, "source": "cusp p/q" | "inside" | "explored" }]`
  with honest names ("1/3 cusp", "Leaning in depth") and no invented provenance.

### julia-presets  (`data/julia-presets.json`, `notes/julia-presets.md`)
Research only: do not edit `src/`.
- Collect at least fourteen well-known Julia constants for z² + c with their usual names (Basilica −1,
  Douady rabbit, San Marco −0.75, Siegel disc, dendrite i, airplane, cauliflower 0.25, and the frequently
  shown values such as −0.8 + 0.156i, 0.285 + 0.01i, −0.4 + 0.6i, −0.70176 − 0.3842i, −0.835 − 0.2321i).
  Use only values you are sure of; compute any you derive (for example the rabbit and airplane centres) and
  record how.
- Add at least six constants with a non-zero z part that look good under the sphere-inversion approach
  (id `mercator`, 2 planes), found by exploring and rendering on the baseline. Mark them "explored".
- Render each preset once (Julia mode, default approach) and reject any that look empty or broken.
- Output JSON: `[{ "name", "note", "c": [x, y, z], "source": "classic" | "computed" | "explored", "cam": {yaw,pitch,dist}? }]`.

### ui  (runs after everything above: `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js`)
Integrate all of it into one coherent page, read every other module's `notes/*.md` first, then:
- Sidebar order: a top row with the "2D view" checkbox and a "Collapse all / Expand all" button; Show
  (Mandelbrot / Julia / Kleinian) with its mode panel; Approach; Equation; Modifiers; Slice; Colour and
  light; View; Quality and speed. Every section body ends with a small "Reset this section" button wired to
  `resetGroup` (plus any non-dial state of that section).
- Mandelbrot panel: the mosaic checkbox and its cell-size dial. Julia panel: the c dials, then the list of
  points (classic presets, explored presets, and the user's saved points with "Save this point" and a
  delete button each; saved in localStorage inside try/catch). Kleinian panel: the preset list, the dials
  built with groups so reset works, and a reset button.
- Equation: power dial from −8 to 10, more presets from 20-formula.js.
- View section: fly speed, drawing radius (`S.view.bound`, up to 500), field of view; the zoom limits live
  on the stage slider.
- Quality: add "Ultra fast" (res 0.5, 1 pass, 90 steps, threshold 2, no shadows, no crevice shading,
  `de = 0`, sampled slope), a "Distance estimate" drop-down (exact / one neighbour / rough), keep the rest.
- Build every group of controls from specs with `buildControls` where practical; use `75-presets.js` for the
  preset data copied from `data/*.json`.
- Texts: update the lede and the closing section so they are true (sums of inversions can give the exact
  flat set; the approach list now includes sphere inversions). Remove stale statements.
- Fix whatever does not fit together. You may make small fixes in other modules' files when integration
  needs it; list each such fix in `notes/ui.md`.
- Finish with a full build (`python build.py`), `tools/smoke.json` extended to cover the new features, zero
  console errors, and screenshots of the whole page at 1400 px and 375 px wide in dark and light.
