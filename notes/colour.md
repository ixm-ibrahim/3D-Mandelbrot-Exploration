# colour (`src/js/25-colour.js`)

Answers item 3 of the feedback: "the colors are boring. and there are no orbit trap options? like cross or ray
or whatever that people commonly use".

## What was built

**Palettes.** 19 instead of 5. The five old ones keep their numbers (0 to 4), so `S.colour.pal = 1` is still
Ember. New: Fire, Electric, Sunset, Rainbow, Ocean, Neon, Classic blue and gold (the well-known Mandelbrot
palette), Viridis, Aurora, Candy, Peacock, Ice and fire, Porcelain, Orchid. The menu lists vivid ones first.
Format: `[name, stop, stop, ...]` with two to eight stops. A palette whose last stop repeats its first runs
round in a circle (Rainbow, Neon, Candy, Classic blue and gold, Brass and verdigris); any other runs to its end
and back. Either way there is no seam. `pal(t)`: t = 0 is the first stop, t = 1 the last, period 2.

**Colour by** (`S.colour.mode`): 0 Orbit trap, 2 Escape count, 3 Distance from the centre, 4 Depth from the
camera, 5 Direction of the last step, 6 Surface direction, 7 Plain clay. The numbers 2 to 7 mean what they
meant before. 1 (the old "nearest approach to the origin") is no longer offered; the shader reads it as 0.

**Trap shape** (`S.colour.trap`, also in the constant `TRAP`): 0 point, 1 cross (the three axis lines), 2 line
(one axis, chosen by `axis`), 3 ray (half an axis, direction chosen by `ray`), 4 planes (the three coordinate
planes), 5 sphere shell (`radius`), 6 ring in the xy-plane (`radius`), 7 the old three-tone mix. Every shape
except the three-tone mix can be moved with the trap centre dials (`tx ty tz`).

**Trap colours by** (`S.colour.by`): 0 how near the orbit came, in bands (keeps cycling through the palette as
the distance grows); 4 the same as a glow (fades out away from the trap: the classic orbit-trap look in 2D);
1 the step at which it came nearest; 2 nearness blended with the escape count; 3 the side it came nearest on.

**Reverse the palette** (`rev`), bands and shift as before. The shift dial has `animate: true`, so the new
dial kit gives it a play button: that is colour cycling.

**Default:** orbit trap, planes, in bands, Sunset. It was chosen by rendering five candidates on four solids:
the planes are a trap every orbit keeps brushing past, so they draw glowing seams over the whole surface on
every kind of solid, where a point trap leaves the n = 8 bulb one flat colour.

**2D view** (`flatColour`): the solid is drawn in the cut-face colour with a one-pixel outline in the hatching
ink, anti-aliased from `d / px`; outside it every palette mode works (traps, escape count, distance from the
centre, direction of the last step). Depth has no meaning there and shows the escape count; surface direction
and plain clay leave a plain outline. Two `note` specs say so when `S.flat` is on.

## Decisions worth knowing

- Nearness is `1 − 2·√d` (bands) or `0.15 + 0.85·exp(−2.4·√d)` (glow): touching the trap lands on the palette's
  LAST stop, so palettes that run dark to light are bright along the trap.
- Escape count on a surface is counted back from the step limit (`0.8 − 0.25·(limit − count)`), in the flat
  picture forward from zero (`0.25·count`). Reason: on a surface nearly every point escapes in the last few steps
  or never, so an absolute count gave one arbitrary colour for the whole solid, and at the common setting of
  10 steps that colour was the palette's darkest stop. Now "never escaped" is always the same bright colour.
- Depth is by ratio (`log2` of the distance), so colours still vary after zooming far in; near is light.
- Planes trap in the 2D view of the slice z = 0: that plane is the picture itself, every orbit stays in it and
  it would read "touching" everywhere, so it is switched off there (`uTrapOff`). What is left is the pair of
  lines where the other two planes cross the picture. Decided in JavaScript from `S.flat`, `S.cut === 0`,
  `tz === 0` (and, for the Kleinian view, `k.cz === 0 && k.mz === 0`).

## Names added or changed

JavaScript (top level):
- `PALETTES` (kept, longer), `COLOUR_CONTROLS` (kept, more specs), `GL_COLOUR` (kept), `setColourUniforms(L)` (kept)
- `PAL_MENU` order of the palette menu (indices into `PALETTES`)
- `PAL_MAX` 16, the size of the shader's palette array
- `TRAP` `{ point, cross, line, ray, planes, shell, ring, tones }` = 0..7
- `colTrapOn(c)`, `colTrapShape(c)`, `colPalOn(c)` the `when` tests
- `palLoop(i, rev)`, `palLoopCache` the palette as the shader wants it (private)
- `paletteCss(i, rev)` a CSS `linear-gradient(...)` of a palette, for an optional preview strip

State `S.colour` (all created by `initState()` from the specs):
`mode` 0, `trap` 4, `by` 0, `axis` 0 (0 x, 1 y, 2 z), `ray` 1 (0 +x, 1 −x, 2 +y, 3 −y, 4 +z, 5 −z),
`radius` 0.7, `tx ty tz` 0, `pal` 7, `rev` false, `bands` 1, `shift` 0.

Shader (GLSL), all inside `GL_COLOUR`:
- hooks, unchanged signatures: `trapStart()`, `trapAdd(vec3, float)`, `colourCapture()`,
  `surfaceColour(vec3, vec3, float)`, `colourUnlit()`, `flatColour(vec3, float, float)`; plus `pal(float)`
- private: `trapDist`, `colDir`, `colPick`, globals `gTrap cTrap gNear cNear gNearIt cNearIt cIt cLast`
- uniforms, all set by `setColourUniforms`: `uColMode uTrap uTrapBy uPalN` (int), `uPalS uPalO uPalF uTrapR
  uColIter` (float), `uPal[16] uTrapC uTrapAx uTrapOff` (vec3)
- it uses from `GL_HEAD` only what the contract promises: `PI at2 uBg uCutCol uCutInk gEsc gIt gLast`

## For the UI integrator

1. Build the controls exactly as the baseline does:
   `const colCtl = buildControls('colDials', COLOUR_CONTROLS, S.colour, touch, { idPrefix: 'col-', group: 'colour' })`.
   Ids are then `col-mode col-trap col-by col-axis col-ray col-radius col-tx col-ty col-tz col-pal col-rev
   col-bands col-shift` (typed boxes add `Num`). Checked against the baseline kit and a snapshot of the new one.
2. Nothing to call at start: no init function, no hooks.
3. "Reset this section": `resetGroup('colour'); touch();` and then make the `when` rules run again
   (`colCtl.sync()`), since a reset changes `mode` and `trap`.
4. Two notes depend on `S.flat`. After the 2D checkbox changes, call `colCtl.sync()` so they appear or go.
5. Optional: a strip under the palette menu, `strip.style.background = paletteCss(S.colour.pal, S.colour.rev)`,
   refreshed in the colour onChange. Not required.
6. Smoke test: `S.colour.mode = 2; S.colour.pal = 1` still means escape count with Ember. A trap example:
   `Object.assign(S.colour, { mode: 0, trap: 1, by: 4, pal: 6 })` (cross, glow, Electric), then `touch()`.
7. The renderer must keep calling `setColourUniforms(L)` from `setScene` (it does). It reads `S.flat`, `S.cut`,
   `S.mode`, `S.iter` and `S.k` as well as `S.colour`.

## How it was checked

`notes/colour_plans.py` writes the plans, `notes/colour_sheet.py <plan> [--theme light] [--url ...]` renders one
with `tools/shot.py` and stitches the tiles. Test pages: `dist/colour.html` (baseline + this file) and
`dist/colour-flat.html` (the same plus snapshots of the in-progress shader and renderer, kept in
`out/colour/shaders-snap.js` and `out/colour/render-snap.js`, because the baseline has no 2D view).
Every run ended with "no console errors". Sheets, all in `out/colour/`:

| Sheet | Shows |
|---|---|
| `base-default.png` | the old default, for comparison |
| `sheet-big-default-dark.png`, `-light.png` | what the four solids open with now, full size |
| `sheet-scene-classic8-*.png`, `sheet-scene-julia-*.png`, `sheet-scene-klein-*.png` (dark and light) | classic Mandelbulb n = 8, sphere-inversion Julia c = (−1, 0, 0), Kleinian: eight palette / trap combinations each |
| `sheet-pals-a-*.png`, `sheet-pals-b-*.png` (dark and light) | all 19 palettes |
| `sheet-traps-default-dark.png`, `sheet-traps-classic8-dark.png` | all eight trap shapes |
| `sheet-by-dark.png` | the five "trap colours by" choices |
| `sheet-dials-dark.png` | trap centre, radius, line, ray, reverse, bands, shift each change the picture |
| `sheet-modes-dark.png`, `sheet-escape-dark.png` | the other modes; escape count including the 10-step case that used to be dark |
| `sheet-flat-m-dark.png`, `-light.png`, `sheet-flat-j-dark.png`, `sheet-flat-k-dark.png`, `sheet-flat-pal-dark.png` | the 2D view: Mandelbrot, Julia, Kleinian slices; palette order and reverse |
| `panel-*.png`, `paneld-2-shell.png` | the Colour section with the baseline kit and with a snapshot of the new dial kit |
| `smoke-*.png` | `tools/smoke.json` run against this build |
| `all-*.png` | a test page built from everyone's sources as they stood late in the round (`--base src --name colour-all`): default, classic n = 8, 2D view, Kleinian, power −2. No errors |

The panel run also drives every `when` rule through the real drop-downs and prints which controls are shown:
shell and ring show the radius, line shows the axis menu, ray the direction menu, three tones hides the centre
and "colours by", escape count hides everything about traps, plain clay leaves only "Colour by".

## Known limits

- Escape count and direction of the last step are poor ways to colour a surface by nature: the first is nearly
  constant over a smooth solid, the second is chaotic (it looks like sandpaper). Both are kept because they were
  there and because they are the classic 2D colourings, where they look right.
- The planes switch for the slice z = 0 assumes the orbit stays in that plane. For the classic Mandelbulb at
  even n, or a formula with a j term, it does not, and the plane z = 0 is left out all the same.
- A circular palette under "glow" starts and ends on the same colour, so the glow is a ring of the other
  colours around the trap, not a bright line.
- The palette array holds 16 entries: eight stops for an out-and-back palette, eight plus the repeated one for
  a circular one.
- Drawing cost: trap bookkeeping is one distance and one comparison per orbit step. Measured on the same
  program, a picture coloured by the planes trap took as long as one coloured by escape count (569 ms against
  576 ms in the quietest round; the machine was shared, so timings swung widely).

## Seen along the way, for other modules

- Approaches (baseline `foldk`): in the slice z = 0, a point with y < 0 comes out of the fold with
  z ≈ −8.7e−8·ρ, not 0 (the sine of a float π), and each step roughly doubles that error. It is why the planes
  switch is decided in JavaScript and not by testing whether the orbit left the plane. It is invisible in the
  3D picture but means the lower half of a 2D slice is computed slightly off the plane.
