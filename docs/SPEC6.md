# Round 6: trap colours that belong to the surface, then the check of all points

## Where things stand (after round 5)

- **Version 6 is published** and is frozen as `base6/` (source) and `dist/v6.html` (page). It is round 4 joined,
  plus round 5: the speed is back to that of Version 5 (`notes/r5-speed.md`; reports in
  `notes/_r5_reports.json`), the closing texts are true of the page, "Show Figure 4", "Back to one plane", the
  Julia list's "Found with two planes" and "As it was found" (`notes/r5-page.md`), and the mirror twins with
  their four buttons (`docs/SPEC5.md`, last section; `uiTwin`, `uiTwinOff` in `src/js/80-ui.js`).
- `tools/smoke.json` has 42 steps (generator `out/r4/page/make_smoke.py`) and passes on `dist/v6.html`
  (`out/me/smoke-v6c.log`).
- The shader and colour code changed shape in round 5. Read `notes/r5-speed.md` before touching it: `main()`
  colours every kind of pixel through ONE call, `pixelColour(kind, p, nor, t, d, px, hatch)`; scene programs are
  built for what the colour settings need (`colProgramNeeds()`, the macros `TRAP_SOLIDS` and `COL_INSIDE`,
  `glNeeds`, the tag in the program key); `cOnTrap` carries `gOnTrap` into the colour code. Compile time is the
  thing that structure protects: a second call to the colour code from `main()`, or a fifth read of the palette,
  costs about a second each. Measure with `python out/me/perf.py base4 <your page> base4 <your page>` before
  and after; the opening settings must stay under 2.6 s (Mandelbrot) and 1.1 s (Kleinian) to compile, and the
  drawing times within a quarter of `base4`.

## Owners in round 6

| Files | Owner |
|---|---|
| `src/js/25-colour.js`, `src/js/30-shaders.js`, and in `src/js/40-render.js` only what sets uniforms and builds and keys scene programs | colour |
| everything else | nobody: leave alone, report what you need. Ten testers are reading `dist/v6.html` at the same time; they change nothing. |

Build and test against the frozen copy: `python build.py --name r6-colour --base base6 --use src/js/25-colour.js
src/js/30-shaders.js src/js/40-render.js`. Scripts, logs and pictures under `out/r6/colour/`; notes in
`notes/r6-colour.md`.

The rest of this file was written by the orchestrator while round 5 was running; where it names a function that
round 5 renamed, the meaning is what counts.

## What was found (orchestrator, on `dist/v6a.html`, the joined page of round 4)

Pictures: `out/me/look6-a.png` to `look6-d.png`, `out/me/look7-a.png`, `look7-b.png`, `out/me/look8-a.png`
(scripts `out/me/look6.py`, `look7.json`, `look8.json`).

1. **The new features work and look good**: trap solids with the cross and the ring, the inside colourings of the
   2D view, the cut face coloured like the inside, the fifteen new Kleinian entries, trap solids in the Kleinian
   view.
2. **The trap colour of a surface still depends on the settings** (`out/me/look8-a.png`: Julia set for c = -1,
   sphere shell of radius 0.7, coloured by glow). The big body is yellow at Detail 1, green at Detail 0.2, green
   with other rings at Detail 3, and teal at 60 iterations. At Detail 1 it carries fine rings centred on the point
   nearest the camera. So the "stack of slices" (N12) is fainter but not gone, and it comes back as soon as the
   trap radius is moved. The Kleinian engineer found the same kind of fault there (p5-6).
   Cause: the number of orbit steps that count towards the trap colour is still taken from things that are not
   properties of the surface: the hit's own escape count (which follows how high above the surface the ray
   stopped), the Detail setting, and the distance from the camera (which gives the rings).
3. **A trap solid in Mandelbrot mode starts as a plain ball**: the first orbit point that counts is c itself, so
   with the shell the solid is the shell (`out/me/look6-b.png`, tile 10). In Julia mode the point itself is step 0
   and "skip 1" leaves it out; in Mandelbrot mode the point itself is step 1 and "skip 1" keeps it.
4. **The opening picture is calmer than the one the user chose their colours on** (`out/me/look6-a.png`): a flat
   blue top with arcs near the rim. Glow width 2 or 3 brings a gradient back; trap radius 0.7 brings arcs back
   everywhere.

## The cure for 2: the trap reads a fixed number of steps, from a point on the surface

For a fixed number K, "the nearest the first K orbit points come to the trap" is a continuous function of the
starting point, inside and outside the solid alike. Read at a point of the surface it is a property of the
surface. Everything that made the colour wander came from letting K follow the ray. So:

- **A dial for K.** New colour control `reach`, "Orbit steps the trap reads", whole numbers, shown while the
  colour is read from an orbit trap in the 3D view. Uniform `uTrapReach`. Start near 6 (tune by eye, see below).
- **In the 3D view `gFade` comes from the dial and from what a pixel can show, and from nothing else.**
  `K_res = log(1 / (page pixel at the hit)) / log(max(|power|, 1.5)) - margin`, with the page pixel `pix * t`
  (NOT multiplied by Detail or by the resolution setting, so that Ultra fast and Fine agree) and a margin of
  about 2 (tune). Then `gFade = min(uTrapReach, K_res) - 1` as a real number, so the last step fades in and out
  smoothly as the view zooms. No escape count: the extra query that learned it (`PH_COUNT`) goes away, which
  also saves one query per lit pixel.
- **The colour is read from the surface, not from where the ray stopped.** The march ends a fraction of a pixel
  above the surface with a distance estimate d and, after the slope queries, a normal. Read the colour at
  `p - nor * d` (keep d from the hit; it costs nothing). That takes most of the hover height away; what is left
  may be on either side of the surface, which does not matter for a fixed K.
- **Inside-out solids (negative powers)** get the same rule. Typed equations whose stretch per step is not the
  power: use 2 in place of the power unless you can do better cheaply; say what you did.
- **The 2D view keeps reading every step until the orbit escapes** (`gFade = 1e9`): it colours the outside, each
  orbit is finite, and the user asked for that picture to stay as it is. Pixel-identical at the opening settings.
- **Volume sampling for the 3D model (`uRaw`)** uses the same rule as the 3D view, with the sample spacing
  (`uFlatH / uRes.y`) as the pixel, so a model's colours match the picture and carry no rings.
- **Kleinian view:** the Kleinian engineer's cure for p5-6 (`notes/r4-kleinian.md`: stop feeding the trap once
  the search has landed on the hit pearl, and put that last point on the wall), using `gPix`.

Accept when, for the opening Mandelbrot view, the Julia sets for c = -1 and the Douady rabbit, and the opening
Kleinian view, each with the sphere shell at radius 1 and at 0.7 coloured by glow, with the cross coloured by
glow and with the planes coloured by bands:

- the pictures at Ultra fast, Fast, Balanced and Fine show the same colours in the same places (compare them
  scaled to one size: mean difference per channel under about 6 of 255, and no region that changes hue);
- the same holds for Detail 0.2, 1 and 3 and for 24, 60 and 120 iterations;
- there are no rings centred on the point nearest the camera, at Balanced and at Fine;
- zooming in by 2 and by 8 keeps the colours of the same places and adds detail only up to the dial's reach.

## The other items for the colour engineer of round 6

- **3 above:** make "Orbit steps skipped at the start" mean the same in both modes: 0 keeps the trap shape itself
  in the solid, 1 leaves it out. In Mandelbrot mode that is one more orbit step than in Julia mode.
- **Trap solids keep their colours at Fast and Ultra fast:** decide "this hit is on the trap's part" from
  `gOnTrap` (the shader engineer's request in `notes/r4-shaders.md`), and take the pixel size from `gPix` where
  the colour module now guesses 0.0015 of the camera distance.
- **4 above, the opening look.** After the cure, make sheets of the opening Mandelbrot view, the Julia set for
  c = -1 and the Douady rabbit for a grid of reach (4, 6, 8, 12), glow width (1, 2, 3) and trap radius (0.7, 1),
  and choose the starting values that give the most colourful picture that is still calm (no speckle, no moire).
  The user asked for: orbit trap, sphere shell, coloured by how near it came as a glow, Rainbow reversed. Keep
  those four; the numbers are yours.

- **Kleinian drawing time** is about a third above Version 5 because the pearl distance is now exact
  (`notes/r5-speed.md`). One saving that changes no picture: `gFade` is always 1e9 in the Kleinian program, so
  `trapAdd` can be built there without the fading weights. Take it if it measures.
- **A 3D model's colours** (volume sampling) must come out like the picture's: check one trap-coloured model
  against its picture once the cure is in (`python out/r4/mesh/run_tests.py` has a real-sampling mode; the PLY
  file carries the colours).

Order of work: the cure and its acceptance pictures first; then the skip count, then the Kleinian cure, then
the opening look; the two items just above last. Time: aim for 70 minutes, stop at 90 whatever the state, with
the smoke test passing on your page and every unfinished item listed.
