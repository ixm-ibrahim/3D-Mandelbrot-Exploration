# r4-colour: the colour module in round 4

File edited: `src/js/25-colour.js` only. Scripts, stand-ins, logs and pictures: `out/r4/colour/`.

## State when I stopped, and the one open problem

Everything in the assignment's items 1 to 4 is built and works with the shader engineer's file as it stood at
00:17 (pictures below). **Open problem: with this colour file the scene shader takes about three times as long
to prepare**, and that makes the smoke test fail in its third step.

- "Preparing the formula" for the classic bulb at power 8, a fresh program, measured back to back on the shared
  GPU (`out/r4/colour/compile.json`): base4 1.7 to 2.9 s; base4 + this file 5.8 to 6.3 s; base4 + this file + the
  live `src/js/30-shaders.js` 15 to 21 s.
- The smoke test's third step allows 10 s for the progress bar to show after an approach change. base4 + this
  file passed the whole test once (00:17, exit 0, 27 steps, no console errors, `smoke-id.log`) and failed that
  step once (00:37, `smoke-id-final.log`); with the live shader file it failed that step every time
  (`smoke.log`). No run printed a console error or an exception; the only failure is that 10 s window.
- What I ruled out by cutting the file down and measuring again (`25-colour-A.js`, `-B.js`, `-D.js` in
  `out/r4/colour/`): taking the stretch and the touch record out of `trapAdd` changed nothing (6.8 s); taking the
  bounded shapes out of `trapDist` changed nothing; a version that carries only two more numbers through the
  orbit loop than base4 (`25-colour-v3-slower.js`, `edit3.py`) was no faster (9.8 to 10.3 s, within the noise
  or worse), so it was not kept. So the cost is not the number of values carried through the loop.
- Variant D puts base4's whole `trapAdd` back (no weights, no stretch, no touch record) and still took 8.1 s
  against 1.6 s for base4 in the same run. **So the cost is not in the orbit loop at all. It is in the colour
  code that runs after the ray has hit**, which grew most: `colTrapPick` is now copied into four call paths
  (surface, flat outside, flat inside, cut face) and `pal()` into about 34 places against 10 in base4.
- The cure to try first (not started): one call of the big function per hook. In `flatColour` decide inside or
  outside first and call the colouring once with that as an argument; let `cutFaceColour` and `surfaceColour`
  go through the same function; have every branch work out a palette position and call `pal()` once at the end
  (twice where two colours are blended, four times for the three tones). `edit3.py` holds a sketch of the same
  idea for `trapAdd`, which turned out not to be where the time goes.

`src/js/25-colour.js` is the version every check below was run on (`out/r4/colour/25-colour-v1.js` is a copy).

Test pages (all from `base4`):

```
python out/r4/colour/mk_standin.py     # writes the two private stand-ins of base4's 30-shaders.js
python build.py --name r4-colour-base --base base4                                   # base4 untouched
python build.py --name r4-colour-id --base base4 --use src/js/25-colour.js --swap js/30-shaders.js=out/r4/colour/30-shaders-id.js
                                                                                     # base4's shader plus "float gFade", always 1e9
python build.py --name r4-colour --base base4 --use src/js/25-colour.js src/js/30-shaders.js   # the real combination
python out/r4/colour/run.py id                    # 19 pictures on the first two pages, compared pixel by pixel
python out/r4/colour/run.py sheet solid r4-colour # a contact sheet of a plan in out/r4/colour/plans.json
python out/r4/colour/panel.py r4-colour           # the Colour section through its real controls
```

## What was built

### 1. The fading tail (N12), the colour half

`trapAdd(v, it)` gives every orbit point the weight `clamp(gFade + 1.0 - it, 0.0, 1.0)`.
- weight 0: the point is skipped. Weight 1: exactly the old code path (written as branches, not as `mix(a, b, 1.0)`,
  so the result is bit for bit the old one).
- in between: the nearest distance, the offset at the nearest pass (the "side"), the step of the nearest pass and
  the four numbers of the three-tone mix each move the share `weight` of the way from what they were to what the
  point would have made them. So nothing jumps while `gFade` slides.
- **Proof that 1e9 changes nothing:** `python out/r4/colour/run.py id` renders 19 scenes (12 in 3D: Mandelbrot,
  two Julia sets, Kleinian, six trap and colour choices, the cut, Balanced quality; 7 in the 2D view) on base4 and
  on base4 + this file with `gFade = 1e9`. Largest channel difference 0 in all 19, run on the first version and
  again on the final file (`out/r4/colour/id-final.log`, `sheet-id.png`).
- With the real shader (`gFade` set from the step count): `sheet-fade0.png` (base4) against `sheet-fade.png`.
  The fine rings on the rabbit at Fine and on the Mandelbrot's top are gone. The opening picture is calmer for
  it: a blue top with rings near the rim (`out/r4/colour/fade/m-glow.png`).

### 2. Trap solids (N3): controls, uniforms, colours

Uniforms declared in `GL_COLOUR` and set in `setColourUniforms`: `uTrapSolid` (0, 1, 2), `uTrapW`, `uTrapSkip`.
`uTrapSolid` is 0 in the 2D view on screen and for the three-tone "shape"; otherwise `S.colour.solid`, also when
`raw` is true, and **also when "Colour by" is not the orbit trap** (so a trap solid can be shown in plain clay or by
depth; the trap's own controls stay on show while a solid is on).

Controls (all in `COLOUR_CONTROLS`, ids `col-<key>`):

| key | label | choices or range | shown when |
|---|---|---|---|
| `solid` | In the 3D view the trap | Colours the surface (0), Is the solid (1), Is added to the solid (2) | 3D view, a trap with a shape is in use, or a solid is on |
| `thick` | Trap thickness | 0.005 to 0.5, typed 0.0005 to 5, starts 0.05 | a solid is on |
| `skip` | Orbit steps skipped at the start | whole numbers 0 to 12, typed to 100, starts 1 | a solid is on |
| `radius` | Trap radius (existing) | | now also for cross, line, ray and planes while a solid is on |
| `by` | Trap colours by (existing) | new choice 5: Where on the trap it came nearest | |

Three new notes explain: what the solid is (and that fewer iterations keep only the large pieces); that three
tones cannot be a solid; that nearness is flat on a trap solid and what is shown instead; that lines stop at the
trap radius.

**A change to `trapDist` that the shader engineer should know about.** While `uTrapSolid > 0.5`, the endless
shapes are cut down to the trap radius: cross, line and ray become rods that reach `uTrapR` from the centre, the
planes become three discs of radius `uTrapR`. With `uTrapSolid` 0 `trapDist` is unchanged. Reason: endless lines
gave sheets right out to the drawing radius with the camera inside them (first version of `sheet-solid.png`).
It is still a true distance (never over-estimates), so the solid's distance estimate needs nothing new.

**Colours on a trap solid** (`colTrapPick`, the branch for `uTrapSolid > 0.5`):
- `trapAdd` keeps a second record beside the nearest pass: the step that TOUCHED the trap, which is the step with
  the least `(trapDist - uTrapW) / stretch`, the renderer's own measure. The stretch is a stand-in the colour
  module can work out from the orbit points alone: `n |v|^(n-1)` per step (a pure power), `|v - mu|^2` per map in
  the Kleinian mode. This record ignores `gFade` (most trap solids are touched during the flight) and respects
  `uTrapSkip`. A Julia orbit's starting point (step 0, which `trapAdd` never sees) is tested at colour time from
  the hit position.
- "Where on the trap" (`colWhere`): direction from the centre for shell and point, angle round the ring, distance
  along a line, and for cross and planes which of the three plus the place on it (a third of the palette apart).
- With a nearness choice (bands, glow, blend) the trap's part of the solid shows "where it touched" and nearness
  is left to the parts where it does vary: the fine layers close to the set, and the set's own surface when the
  trap is added. With step, side or place chosen, layers finer than about a pixel fade to the palette's mean
  colour (what such a pixel would average to), which stops the sparkle there.
- Pictures with the real shader, default palette: `sheet-solid.png` (shell, cross, ring on Julia c = -1 and on the
  Mandelbrot; by step; added), `sheet-solid2.png` (4 iterations, skip 0, planes, line, plain clay, by side, Sunset,
  Kleinian), `panel-solid-1400-dark.png` (the cross at Balanced with the controls beside it).

### 3. The 2D view (N10)

| key | label | choices or range | shown when |
|---|---|---|---|
| `edge` | Outline width, pixels | 0 to 8, typed to 40, starts 1 | 2D view |
| `edgeGlow` | Glow beside the outline, pixels | 0 to 60, typed to 400, starts 0 | 2D view |
| `inMode` | Inside the set, colour by | Plain (0), Orbit trap (1), Where the orbit ends up (2), How deep inside (3), How quickly the orbit settles (4) | 2D view, or 3D with the cut face coloured |
| `inPal` | Palette for the inside | Same as outside (-1), then every palette | an inside colouring is on |
| `inRev` | Reverse the inside palette | | the inside has its own palette |

- At the defaults `flatColour` computes exactly what it did (7 of the 19 identical pictures are 2D).
- The outline lies outside the set, `edge` pixels wide by the distance estimate; under 1 it fades instead of
  thinning; the glow fades the ink into the colours over `edgeGlow` pixels.
- With an inside colouring there is no blend across the edge (an inside colour read from an escaping orbit is
  noise); the refining passes soften it.
- "How quickly the orbit settles" is the average stretch per step (0 at a centre, 1 at the edge): the classic
  rings inside each bulb. "How deep" uses the renderer's distance estimate. "Where the orbit ends up" is the
  direction and size of the last orbit point.
- Pictures: `sheet-inside.png`, `panel-2d-1400-dark.png`.

### 4. The cut face

`cutFace` ("Colour the cut face like the inside of the 2D view", shown in 3D while the solid is cut open) and
`vec3 cutFaceColour(vec3 p, vec3 hatch)`. Off: returns `hatch`. On: the inside colouring of `inMode` (Plain gives
the plain cut colour without hatching, as the 2D inside is). The hook gets no distance estimate, so "How deep" on
the cut face uses the estimate a pure power would give; it looks like the 2D one but is not identical to it.
Pictures: last row of `sheet-inside.png`.

### 5. Wide ranges

`xmin/xmax/xlo/xhi` on: glow (40, typed 1000), radius (10, 500), trap centre x y z (±10, ±500), bands (30, 500),
thickness (2.5, 50), skipped steps (60, 1000), outline width (40, 400), glow beside the outline (400, 4000).
Checked through the real controls: six tags show, typed values are taken, switching off pulls them back.

## Names added

JavaScript, top level: `palMenuOptions`, `colSolidAsked`, `colSolidOn`, `colInsideShown`, `colInsideOn`,
`colTrapColours`, `colTrapBy`, `colNearBy`, `palLoopCacheIn`, `palBoth`, `colSeen`, `colViewSync`.
Changed: `colTrapOn`, `colTrapShape`, `colPalOn`, `colGlowOn` (meanings widened), `palLoop(i, rev, cache)`,
`setColourUniforms(L, raw)`, `palLoopCache.mean`.
State: `S.colour.solid, thick, skip, inMode, inPal, inRev, edge, edgeGlow, cutFace` (made by `specDefaults`; a
missing value reads as its default in `setColourUniforms`).
Shader uniforms: `uTrapSolid, uTrapW, uTrapSkip` (for the renderer's shader too), and private `uPalInN, uPalInF,
uPalMean, uInMode, uColNeed, uEdge, uEdgeGlow, uCutFace, uColKlein, uColJulia, uColMu`; `uPal` now holds two
palettes (32 slots).
Shader globals and functions: `gTouch, gTouchIt, gTouchS, gTouchStr, gStr, gLogS, gSteps` and their `c*` copies,
`gColIn`; `colWhere`, `colTrapPick`, `colInside`, `cutFaceColour`. `trapDist` changed as described above.
`GL_COLOUR` reads from `GL_HEAD`: `PI, at2, uPow, uBg, uCutCol, uCutInk, gEsc, gIt, gLast, gFade`. Nothing else.

## For whoever joins the parts

1. `colViewSync` is put on `hooks.view` by the first call of `setColourUniforms`. When the 2D view, the cut or
   the mode changes it calls `syncControls()` once, so the `when` rules that read `S` are re-checked. Nothing in
   the page has to do that.
2. `setColourUniforms` reads `S.colour, S.flat, S.cut, S.cutOn, S.mode, S.k, S.iter` and nothing else, so the
   renderer's snapshot swap covers it.
3. `src/js/45-export.js` scales `snap.S.colour.edge` with the picture; `edgeGlow` is in pixels too and needs the
   same line.
4. The closing texts marked `data-needs="solid"` and `data-needs="inside"` in `src/body.html` switch themselves on
   (the keys `solid` and `inMode` exist). The exact labels are in the tables above.
5. The smoke test's colour assertions (the choices "Cross", "How near it came, as a glow", "Electric") still hold.

## Not done

- The colour leftovers of the fix pass (point glow on a Julia set, three tones in 3D and on the Kleinian set, the
  Kleinian wall spheres, speckle of "direction of the last step") were not started.
- The opening picture was not re-tuned for the fade: it is cleaner and plainer. Glow width 2 to 3 brings colour
  back; a 3D-only default would be the way if the user misses the old look (the 2D view must not move).
- Not looked at: light theme and phone width of the new controls, the trap solids at Fine, the Kleinian trap
  solid (the shader did not have it when the pictures were made), trap solids in the mosaic.
