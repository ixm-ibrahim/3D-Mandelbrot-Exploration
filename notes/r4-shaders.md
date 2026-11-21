# Round 4, shaders (`src/js/30-shaders.js`)

Scripts, stand-ins, logs and pictures: `out/r4/shaders/`. Only `src/js/30-shaders.js` was edited (it now has LF
line endings; `build.py` does not care). `GL_KLEIN` is untouched, as instructed.

The file needs a colour module that has `uTrapSolid`, `uTrapW`, `uTrapSkip`, `cutFaceColour` and reads `gFade`.
Base4's own colour module does not, so `--base base4 --use src/js/30-shaders.js` alone no longer compiles its
shader. Build it with the real colour file, or with my stand-in:

```
python build.py --name r4-shaders    --base base4 --use src/js/30-shaders.js src/js/25-colour.js
python build.py --name r4-shaders-si --base base4 --use src/js/30-shaders.js --swap js/25-colour.js=out/r4/shaders/25-colour.js
```

## 1. The rings (N12): what was built, and why it is not exactly the rule in CONTRACT4

`gFade` is declared in `GL_HEAD` and means what CONTRACT4 says. The hit of the 3D view is now asked twice
(`PH_COUNT`, then `PH_COLOUR`); every other query runs with `gFade = 1e9`.

**The contract's rule alone did not cure it.** With `gFade = max(count - TAIL, 1)`:
- TAIL 4: the picture is the same as base4 to the eye (`sheet-t4.png` beside `sheet-base.png`).
- TAIL 8: fainter rings, still there (`t8/rabbit-shell-b-i60.png`).
- TAIL 20: gone, but only four orbit points are left to colour with (`sheet-t20.png`).

The reason: the rings are not only the last steps of the flight. The number of steps that count changes from
pixel to pixel (it follows how high the hit hovers, which is one ring per step: `sheet-dbg.png` shows it), and
every step that joins can bring a new nearest pass. Fading the newest step makes each ring soft, not absent.

**What cures it** is a limit that is the same right across a smooth part of the solid:

```
level = min(count, -log(pix * t * max(uPx, uDetail)) / log(max(|uPow|, 1.5)) + LEVEL_STEPS)
gFade = max(level - TAIL, 1)          TAIL = 4, LEVEL_STEPS = 2
```

`pix * t` is the size of a picture pixel at the hit. A move of one pixel grows by about the power at every
step, so after that many steps the orbit can no longer follow the surface at all: later steps could only paint
detail finer than a pixel. The measured count is kept as a second limit, so the flight never counts.
The pixel meant is a page pixel (`uPx`), or the surface threshold when that is coarser. That makes the colours
the same in the moving preview, at every quality preset and in a saved picture of any size (45-export.js sets
`uPx` to picture pixels per stage pixel, which is exactly what this needs).

Not faded (always `1e9`): the 2D view, volume sampling (`uRaw`), the Kleinian view (its step count is a whole
number, and `GL_KLEIN` is being rewritten), inside-out solids (negative powers), and a hit on a trap solid.

**Checked** (base4 against the new file, same steps, `python out/r4/shaders/lab.py rings ...`):
- `sheet-base.png` and `sheet-real.png`: Douady rabbit close up, Basilica, default Mandelbrot; sphere-shell
  glow, cross glow, planes in bands; 24, 12 and 60 iterations; threshold 0.2, 1 and 3 pixels. 45 pictures each,
  Balanced with 4 passes and no shadows (to keep the run short). In base4 the shell rows are covered in rings;
  in the new build no picture of the 45 shows them. Close-ups: `real/basilica-shell-b-i60.png` against
  `base/basilica-shell-b-i60.png`, `k2/rabbit-shell-b-i24.png`.
- Full Balanced and full Fine at the page's own settings (`sheet-newdef.png`): clean. These were taken one
  edit earlier, when the limit used the picture pixel in place of the page pixel.
- The 2D view is pixel-identical to base4 with the stand-in AND with the real colour file: 8 pictures, largest
  channel difference 0 (`python out/r4/shaders/flat.py r4-shaders-base,r4-shaders-si,r4-shaders`). That run was
  before the 2D mosaic change below, which alters the mosaic picture on purpose.

**What is left, honestly:**
- Fine was not re-run through the whole matrix after the last change to the rule (only the default views
  before it). The rule gives Fine more margin than Balanced, so I expect it clean, but it is not looked at.
- The pictures look different from base4, not only cleaner: fewer steps count, so the shell glow shows more
  blue and green and less yellow and orange, and the middle of the default Mandelbrot is a calm blue. The user
  chose these colours on pictures that had the rings. If it is too flat, the glow width or the shell radius in
  the colour module is the place to retune, or raise LEVEL_STEPS by one (more detail, rings return first on the
  most stretched parts).
- A closer view shows finer colour detail than a far one, by design. Across one picture the limit changes by
  one step for every factor of the power in distance from the camera, as a smooth drift.
- Formulas whose stretch per step is not about the power dial (typed equations) fall back on the measured count,
  which is the contract's rule: softer rings, not none. Not looked at.
- Ultra fast and a 3 pixel threshold use the coarser pixel, so they count fewer steps than Balanced.

## 2. Trap solids (N3)

In `orbitDE` (Mandelbrot, Julia, and the Julia sets of the mosaic). Not in the Kleinian view: `GL_KLEIN` was off
limits. For each orbit point with index from `uTrapSkip` up, before the orbit has left:
`(trapDist(v) - uTrapW) / stretch`, the least of them is the trap solid's distance (negative inside).
- Stretch with three neighbours: the root of the largest row sum of the neighbours' products with each other.
  That is never less than the true greatest stretch, and exact for a map that keeps shapes (the plain sum of
  squares would cost up to 1.7 times the ray steps). With one neighbour or none: what those modes have.
- `uTrapSolid` 1: this replaces the set's distance. 2: the smaller of the two. `gOnTrap` says which was returned.
- Thin layers. Late steps wrap the set in layer upon layer of the solid, each thinner than the last. Drawn as
  they are they show as ripples and hairline scratches (`sol1/basilicafar-ring.png`, before). A layer thinner
  than `TRAP_THIN` (2) picture pixels now loses thickness faster than it naturally would and is gone at about
  half that (`gPix`). With trap = solid the set itself therefore no longer shows through as dust.
- The slope is sampled whenever `uTrapSolid > 0.5`.
- With the rough estimate (Ultra fast) one neighbour is used while a trap solid is on: the rough march steps
  through thin shells.
- A hit on a trap solid is not faded (`gFade = 1e9`): the colour module reads the step that made the surface.

Pictures: `sheet-sol2.png` (plain clay, my stand-in colours: Basilica and default Mandelbrot; shell 0.7 / 0.05 /
skip 1, cross, line, ring, point), `sheet-misc.png` and `sheet-misc4.png` (the real colour module: the same in
colour, the union, Fine, Ultra fast, Fast, cut open). Each trap gives a clearly different object, silhouettes
are clean at Balanced, and no glow or slices appear at Balanced or Fine.

Not as good as asked:
- At Fast and Ultra fast the shapes are whole, but the real colour module paints most of a trap solid plain
  green (`misc4/q-fast.png`, `misc4/j-shell-ultra.png`). Its test "this hit is on the trap's part" is
  `touch.w / uTrapW < 1.5`, which fails as soon as the hit hovers higher. `gOnTrap` is the exact answer.
- A few faint hairlines remain on the big shell blobs at Balanced (`misc2/j-shell.png`): single layers about
  two pixels thick.
- Kleinian: not built. Mosaic with a trap solid: the code path is there, never looked at.

## 3. Speed and compile time: NOT within the limits

Compile time alone, pages one after another on a quieter machine, least of 3
(`python out/r4/shaders/compile.py <pages>`; final file unless marked):

| Page | Orbit scene | Kleinian |
|---|---|---|
| base4 | 1.8 s | 0.73 s |
| my file + my stand-in colour | 2.5 s | 0.85 s |
| my file + the real colour module | 9.9 s | 5.3 s |
| the same, one edit earlier (raw output with its own call to `surfaceColour`) | 13.5 s | 8.4 s |
| that earlier file without the raw call | 9.0 s | 5.5 s |
| that earlier file without the raw call and without `cutFaceColour` | 6.9 s | 3.5 s |
| that earlier file with `TRAP_SOLIDS = false` | 12.4 s | 7.9 s |

- My file with the stand-in adds about 40 percent on the orbit scene and 17 percent on the Kleinian one. The
  limit was a fifth, so the orbit scene is over it.
- With the real colour module a new approach or equation now takes about 10 s to prepare where base4 took 2.
  Most of that is the colour code itself: every call from my file to a colour hook is one more copy of that
  hook for the compiler. The second call to `surfaceColour` cost 4.5 s (now gone: the raw output shares the
  lit hit's call), `cutFaceColour` costs about 2 s, and the trap solid block costs nothing measurable.
- Drawing time, old against new, was measured only while a smoke test ran beside it
  (`python out/r4/shaders/timing.py`), so it is rough: default Mandelbrot at Balanced with 4 passes 141 to
  181 ms in base4, 278 to 373 ms with my file and the stand-in, 663 to 1001 ms with the real colour module;
  Ultra fast and the Kleinian view the same as base4. So the default picture may draw up to twice as slowly
  with my file even with trap solids off. NOT confirmed on a quiet GPU and not traced. Suspects: the trap block
  inside the orbit loop (the compiler may run its arithmetic on every step whether or not the switch is on),
  and the extra turn of the main loop.
- Prepared way out for the drawing time: `const bool TRAP_SOLIDS = true;` in `GL_ORBIT`. A program built from
  `GL_ORBIT.replace('TRAP_SOLIDS = true', 'TRAP_SOLIDS = false')` has no trap solid code at all. The renderer
  would key its programs on "trap solid on or off" (one more entry in `sceneWant`). Compile time is the same
  either way; the drawing time with it off was not measured.

## 4. Raw output (`uRaw`) and the cut face

- `uRaw` is declared in `GL_HEAD`. In the flat branch it writes `vec4(surfaceColour(...), d)` as CONTRACT4
  says. Three things to know: an inside-out solid is clipped at the same far limit as in the 3D picture before
  the output; the mosaic keeps the cells the 3D picture keeps (the on-screen 2D view keeps more); thin layers
  of a trap solid are NOT faded here (`gPix = 0`), so a model gets every layer. The raw output goes through
  the same `surfaceColour` call as a lit hit (see section 3). NOT run against the real `sampleSlice`: my page
  has base4's renderer, which never sets `uRaw`, so this branch has compiled but never drawn.
- Cut face: a cut hit now makes one more query (`PH_CUT`) at the point of the cut face itself, so
  `colourCapture()` reads that point's own orbit, then `cutFaceColour(vec3(p.xy, uCut), hatch)`.
  `misc/cut-plain.png` (hatched as before), `misc/cut-face.png` (the real module's inside colours),
  `misc/cut-solid.png` (a trap solid cut open: hollow shells with hatched rims).

## 5. Testers' defects

- p11-1 (2D mosaic is wallpaper): fixed. Each small set keeps a halo of its colours and the plain stage shows
  beyond (`misc/mosaic2d.png`). This changes the 2D mosaic picture and nothing else in 2D.
- Not started: p15-2, p15-5, p5-1, p5-2, p15-3, p5-3, p5-6, p5-7, p8b-1, p8b-2, p9-1, p9-2.
  p15-5, thought through only: at n = 1 the orbit of c is k times c, so the "solid" is the ball of radius
  64 / iterations (about 5), the camera sits inside it, and every ray hits at once. It is not the inside-out
  swap. A cure needs a rule for orbits that are still growing steadily when the steps run out.

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `uRaw` | uniform, `GL_HEAD` | volume sampling: the flat branch writes colour and distance only |
| `gFade` | global, `GL_HEAD` | set before a query; an orbit point with step `it` counts with weight `clamp(gFade + 1 - it, 0, 1)` |
| `gPix` | global, `GL_HEAD` | set before a query: size of a picture pixel at the point asked about; 0 in the 2D view and for `uRaw` |
| `gOnTrap` | global bool, `GL_HEAD` | after a query: the distance returned is the trap solid's, not the set's |
| `TRAP_THIN` | const, `GL_ORBIT` | 2.0: trap solid layers thinner than this many pixels fade out |
| `TRAP_SOLIDS` | const bool, `GL_ORBIT` | true; write false into the source to build a program without trap solids |
| `PH_CUT`, `PH_COUNT` | consts, `GL_TAIL` | new steps of `main()`; `PH_*` and `END_*` are renumbered |
| `TAIL`, `LEVEL_STEPS` | consts, `GL_TAIL` | 4.0 and 2.0, see section 1 |
| `fade`, `hue` | locals of `main()` | the `gFade` for the colour query; the step a hit's colour begins with |
| `trapOn`, `tbest` | locals of `orbitDE` | trap solid wanted for this query; its distance so far |

## For whoever joins the files

1. `GL_KLEIN` is pasted in from another engineer. `GL_TAIL` expects of its `de()` only what it did before.
   `main()` sets `gOnTrap = false` once per pixel and `gFade`, `gPix` before every query. If the new Kleinian
   code builds trap solids it must set `gOnTrap` on every query and should use `gPix` for thin layers.
   Kleinian hits are never faded (`ORBIT_SCENE` is false there).
2. `tools/smoke.json` step 3 gives a new program 9.6 s to compile and start drawing. With the real colour
   module the orbit program takes about 10 s here, and the step fails with "the progress bar never showed while
   drawing". See the smoke results at the end of this file.
3. Colour module: use `gOnTrap` (valid at `colourCapture()`) in place of `touch.w / uTrapW`; see section 2.
4. Renderer, optional: the `TRAP_SOLIDS` switch in section 3. The 0.5 cap on `uStepK` in Kleinian mode stays.
5. Page texts: the answer on "slices" can now say that it was the colouring, not the shape, and that it is
   fixed for the equation views; the answer on trap shapes should say the fastest settings draw them whole.

## Smoke test, final file

- `dist/r4-shaders-si.html` (base4 + my file + my stand-in colour): `tools/smoke.json` exit 0, 27 steps, no
  console errors (`out/r4/shaders/smoke-standin.log`).
- `dist/r4-shaders.html` (base4 + my file + the real `src/js/25-colour.js` as it stood at 00:57): `tools/smoke.json`
  FAILS at step 3, "the progress bar never showed while drawing": the step waits 9.6 s and the program needs
  about 10 s to compile (`smoke-real.log`). With that one wait lengthened in a private copy of the step list
  (`out/r4/shaders/smoke-long.json`, 600 turns made 4000) all 27 steps pass, exit 0, no console errors
  (`smoke-real-long.log`). Nothing else differs.
- In both pages the picture job is skipped and the model job runs on the built-in sphere, because base4 has no
  `45-export.js` and its renderer cannot sample. I did not build a page with the real renderer and export files.
- The 2D view was compared again on the final file: 7 pictures, each identical to base4 with the stand-in and
  with the real colour file (the mosaic picture left out, since it is changed on purpose).
