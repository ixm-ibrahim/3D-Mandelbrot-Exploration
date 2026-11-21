# Round 6, colour (`src/js/25-colour.js`, `src/js/30-shaders.js`, one line of `src/js/40-render.js`)

Started 02:33, last source change 03:45 (the smoke test and the final pictures came after it), stopped 03:58 (85 minutes). Scripts, logs and pictures: `out/r6/colour/`.
Test page: `python build.py --name r6-colour --base base6 --use src/js/25-colour.js src/js/30-shaders.js src/js/40-render.js`.
Every claim below says whether it was **measured** (with the path of the evidence) or **reasoned**.

## State in one paragraph

The colour an orbit trap gives a surface is now read from the surface itself, with a fixed number of orbit steps,
and it no longer follows the quality preset, the Detail setting, or the iterations from 24 up (measured, tables
below; before and after sheets). The rings centred on the point nearest the camera are gone at Balanced and Fine
(looked at, `pair-*-ref-final.png`). The numbers are two to four times better than Version 6 but the target of
SPEC6 ("mean difference under about 6 of 255") is met only for the Kleinian view and for part of the equation
views: what is left sits on the outline of the solid and on the edges of thin colour bands, not in regions that
change hue (difference maps: `diffmaps.png`). Zooming in keeps the colours only while the dial is not above what the
opening view can show, which is why the dial starts at 4 and not at 6. The 2D view and every 3D picture not
coloured by a trap are unchanged, except that two of the ten 2D scenes differ by 1 of 255 in one and in three
pixels. The whole smoke test passes on the final page, unchanged (42 steps, exit 0, no console errors).

## What was wrong, in the end (measured on the way)

SPEC6 named three things the count of steps followed: the hit's own escape count, the Detail setting and the camera
distance. Taking those away was not enough (`t1-sheet.png`: the first build, a fixed count read at `p - nor * d`,
still gave yellow, green or teal by Detail). The reason: beside an iterated set the distance estimate reads about
half the true height of the hit above the surface (it carries the factor 0.5 that makes it safe far away), by a
factor that changes from place to place. So `p - nor * d` is still half a pixel or more above the surface, and each
orbit step doubles that error: after five steps half a pixel is a tenth of the whole set. The colour needs the
surface point to about a twentieth of a pixel.

## What was built

1. **The colour is read from the surface (`PH_FIT`, `lift`).** The estimate falls in a straight line on the way
   down to the surface, whatever the factor. So the phase `PH_FIT` (it takes the place of `PH_COUNT`: one query per
   lit pixel, as before) reads the estimate again 60 percent of the way down to where the surface is expected, and
   the straight line through the two readings gives the height `lift`. The colour query is made at
   `p - nor * lift`. With the fastest estimate (Ultra fast: no neighbouring orbits, the size of the estimate means
   nothing) `PH_FIT` uses one neighbouring orbit along the normal and takes both readings itself (two queries), and
   starts from the last point the march knew to be outside (`t = tOut`), because that march often stops inside.
2. **The trap reads a fixed number of steps.** `gFade = colourReach(pagePix)` for that query:
   `max(min(uTrapReach, log(1 / pagePix) / log(power) - REACH_MARGIN), 1)`, with `pagePix = pix * t * uPx` (a page
   pixel: not multiplied by Detail or by the resolution setting), `power = max(|uPow|, 1.5)`, or 2 where the
   renderer's probe says the equation is not a plain power of |z| (`gPowerLaw`), and `REACH_MARGIN = 3`.
   `gFade = K` lets the steps 1 to K count in full, so the dial reads as it is labelled (this is SPEC6's
   `min(reach, K_res) - 1` with its margin of 2, counted one higher). No escape count: `PH_COUNT`, `TAIL` and
   `LEVEL_STEPS` are gone. A mosaic set is drawn small, so its pixel is divided by `uMosaic * MOSAIC_FIT`.
   Inside-out solids (negative powers) get the same rule and the same `PH_FIT`.
3. **Only trap colours take this path** (`colourFromTrap()`: `uColMode <= 1`). Escape count, depth, distance from
   the centre, direction of the last step, surface direction and plain clay are read at the hit point with
   `gFade = 1e9` exactly as before, which is why they are pixel-identical.
4. **The 2D view** keeps `gFade = 1e9`. **Volume sampling** (`uRaw`) uses `colourReach(uFlatH / uRes.y)`: the rule
   of the 3D view with the sample spacing as the pixel. Its distance (`gPix = 0`, the shape of trap solids) is
   untouched.
5. **Kleinian view** (the Kleinian engineer's cure for p5-6, with the pixel): the colour query is made at
   `p - nor * lift` (the estimate there is the true distance to a pearl, so no `PH_FIT`) with
   `gLand = max(page pixel, 0.5 * e)`. In `kde` the first step that lands within `gLand` (in cell units) of a
   pearl ends the search: that point is fed to the trap with its y put on the wall (0 or a) and nothing after it. A
   hit on a wall sphere has landed before the first step and feeds the wall point alone. Off while the trap alone is
   the solid. The dial does not act here: the search reads every step until it lands.
6. **The dial.** `reach`, "Orbit steps the trap reads", whole numbers 1 to 16 (1 to 100 typed, 60 and 1000 with
   Extreme ranges), starts at 4, shown in the 3D view of an equation while "Colour by" is "Orbit trap"
   (`colReachOn`). Uniform `uTrapReach`; no program is built for it (measured: the smoke test and all runs show no
   "Preparing the formula" from a dial; reasoned: it is only a uniform).
7. **"Orbit steps skipped at the start" means the same in every mode**: 0 keeps the trap shape itself in the solid,
   1 leaves it out. `uTrapSkip` is the dial plus `colSkipFrom()`, which is 1 in Mandelbrot mode when the start
   value is not written with c (the orbit then starts from a fixed value and its first point that moves with the
   place is step 1) and 0 otherwise (Julia, Kleinian, the mosaic, a start value such as c). The shader is unchanged
   for this. Measured: `pairs-solids-ref-final.png`, s01 against s16 and s18.
8. **Trap solids:** the colour module's "layers thinner than a pixel" test uses the renderer's pixel (`cPix`, the
   captured `gPix`) in place of 0.0015 of the camera distance. (`gOnTrap` was taken over in round 5.) The colour of
   a trap solid is read from the fitted surface point too, where the step that touched the trap scores exactly 0.
9. **Kleinian program without the fading weights:** `glNeeds(needs, klein)` writes `#define COL_KLEIN 0|1`; with 1
   `trapAdd` has `const float w = 1.0`. No picture changes (measured: f05, f16, f17, f26 identical).

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `reach` | `COLOUR_CONTROLS`, `S.colour.reach` | the dial "Orbit steps the trap reads"; a state without it reads as `COL_REACH` |
| `COL_REACH` | 25-colour.js | where the dial starts: 4 |
| `colReachOn(c)` | 25-colour.js | the dial is shown: 3D view, not Kleinian, coloured by the trap |
| `colSkipFrom()` | 25-colour.js | 1 where the orbit starts from a fixed value (added to the skip dial for `uTrapSkip`) |
| `uTrapReach` | uniform, `GL_COLOUR` | the dial; read only through `colourReach` |
| `uTrapSkip` | uniform | changed meaning: the dial plus `colSkipFrom()` |
| `colourReach(px)` | `GL_COLOUR` | the value of `gFade` for the query a surface colour (or a volume sample) is read from |
| `colourFromTrap()` | `GL_COLOUR` | true when the surface colour comes from the trap |
| `REACH_MARGIN` | const, `GL_COLOUR` | 3: steps held back from what a pixel could just show |
| `cPix` | global, `GL_COLOUR` (trap solids only) | `gPix` as it stood at `colourCapture()` |
| `COL_KLEIN` | macro, 0 or 1 | 1 in the Kleinian program: `trapAdd` without weights. `GL_COLOUR` defines it as 0 when it is not defined |
| `glNeeds(needs, klein)` | 30-shaders.js | second argument; writes the third `#define`. `glNeedsKey` and all program keys are unchanged |
| `gLand` | global, `GL_HEAD` | set before a query; above 0 the Kleinian search lands (see 5) |
| `MOSAIC_FIT` | const | moved from `GL_ORBIT` to `GL_HEAD`, same value |
| `kde(z, land)` | `GL_KLEIN` | second argument: the landing length in cell units, 0 for none |
| `PH_FIT` | const, `GL_TAIL` | the phase that finds the surface under a hit; has the number `PH_COUNT` had. `PH_COUNT`, `TAIL`, `LEVEL_STEPS` are removed |
| `FIT_STEP` | const, `GL_TAIL` | 0.6: how far down `PH_FIT` reads |
| `lift`, `fit1`, `fitFirst`, `pagePix`, `hue` | locals of `main()` | `lift` replaces `fade`; `hue` is now `PH_FIT` for trap colours of an equation, else `PH_COLOUR`. `crawl` (dead after the march) counts the readings of `PH_FIT` |
| `sceneWant` | 40-render.js | passes `klein` on to `glNeeds`; nothing else changed in that file |

Help text of the skip dial gained one sentence ("At 0 the trap shape itself is part of the solid, at 1 it is left
out."). `de()` still has one call site; `pixelColour` is still called once; the palette is read no more often.

## Measurements

All measured. Scene lists and comparisons: `out/r6/colour/scenes.py` (26 scenes that must not change, 176
acceptance scenes, 20 trap solids, 14 extra), drawn at 1000 x 700. Sets: `ref/` from `dist/v6.html`, `final/` from
the final page. Of `ref/`, the 26 fixed scenes, the 20 trap solids and the acceptance scenes of Julia c = -1 were
drawn before any source change (02:55 to 03:04); the acceptance scenes of the other three subjects, the 14 extra
scenes and the corrected zoom scenes were drawn later from the same frozen page. `python out/r6/colour/report.py final` writes every log and sheet named here.

**Pictures that must not change** (`cmp-fixed-final.log`): 24 of 26 identical, largest channel difference 0: the
2D view (opening Mandelbrot, Julia c = -1, rabbit, slice at 0.3, Kleinian, power -2, mosaic, inside "settles") and
all 16 of the 3D pictures by escape count, depth, distance from the centre, last step, surface direction and clay
(Mandelbrot, Julia, Kleinian, power -2, mosaic, cut face, Ultra fast, Fast). Two 2D pictures coloured by the trap
differ by 1 of 255: `f09-flat-j-in-trap` in 0.0003 percent of its pixels (one pixel) and `f10-flat-m-cross-bands`
in 0.0007 percent (three pixels). v6 drawn twice gives 0 for both (`ref2/`), so the change is mine. Reasoned, not
traced: no line of the 2D path changed, so this is the driver's compiler rounding differently in a program whose
`main()` changed. The opening 2D picture (f01) is identical.

**Acceptance scenes** (`accept-final.log`, `accept-ref.log`): opening Mandelbrot, Julia c = -1, Douady rabbit,
opening Kleinian, each with shell 1 glow, shell 0.7 glow, cross glow, planes bands. Every variation is held against
Balanced of the same set-up, with shadows and crevice shading off in all of them so that the light does not count
(the presets are otherwise as they are); 60 and 120 iterations are held against 24. Pictures are halved first.
Worst of the 16 set-ups (average in brackets):

| Variation | v6: mean difference of 255 | v6: hue moved over 30 degrees | final: mean difference | final: away from the outline | final: hue moved |
|---|---|---|---|---|---|
| Ultra fast | 50.0 (25.8) | 77 % | 19.1 (13.7) | 18.4 (12.6) | 16 % |
| Fast | 48.3 (17.7) | 73 % | 17.7 (9.5) | 19.3 (8.1) | 18 % |
| Fine | 23.8 (12.9) | 34 % | 14.1 (7.9) | 13.6 (6.1) | 12 % |
| Detail 0.2 | 30.5 (16.6) | 40 % | 18.1 (10.2) | 18.0 (8.2) | 17 % |
| Detail 3 | 52.2 (29.7) | 62 % | 37.8 (19.5) | 43.0 (19.3) | 45 % |
| 24 iterations against 14 | 27.1 (11.9) | 37 % | 30.5 (12.1) | 34.5 (14.2) | 38 % |
| 60 and 120 against 24 | 1.5 (0.3) | 2 % | 1.7 (0.3) | 1.7 (0.3) | 2 % |
| zoomed in 2 times | 70.2 (21.8) | 83 % | 19.4 (9.6) | 15.9 (7.4) | 12 % |
| zoomed in 8 times | 89.2 (33.5) | 81 % | 31.2 (14.7) | 25.8 (9.6) | 22 % |

Read with the sheets: the Kleinian rows are 3 to 6 at Fast, Fine and Detail 0.2 and 9 to 13 at Ultra fast; the
shell and cross rows of the equation views are 7 to 12; the planes with bands are the worst rows (13 to 19),
because thin high-contrast bands turn a shift of one pixel into a large difference. The pictures show the same
colours in the same places (`pair-*-ref-final.png`); the difference maps (`diffmaps-final.png`) put what is left
on the outline and on band edges. So: **"under about 6" is met for the Kleinian view at Fast, Fine and Detail 0.2,
and on average for Fine away from the outline; it is not met for the other rows.** No region changes hue in the
sheets I looked at, except:
- **Detail 3** (the worst row): at Detail 3 the solid is drawn about two pixels fatter, so its outline and its
  bands sit elsewhere. The colours of the broad parts agree.
- **14 against 24 iterations**: unchanged from v6. From 14 to 24 iterations the solid itself changes shape, and
  the colour is read from the surface, so the colours move with it (the big body of Julia c = -1 goes from
  yellow-green to yellow). From 24 up nothing moves (0.3 on average).
- **The zoom scenes are exact magnifications** (the field of view is narrowed). With the dial at 4 the middle of
  the picture keeps its colours at 2 and 8 times (`zoom-final.png`). What is left in the numbers at 8 times is
  mostly the blur of a cut-out magnified 8 times.

**Where the dial starts** (`reachzoom.log`, 12 equation set-ups, how far the colours of the same places move when
zooming in): dial at 4: 2 times 10.6 on average (worst 19.4, hue 12 %), 8 times 14.3 (31.2, 22 %); at 5: 15.5
(26.9, 30 %) and 20.7 (48.0, 63 %); at 6: 19.1 (36.9, 39 %) and 39.4 (91.5, 99 %: the whole body of Julia c = -1
with shell 0.7 goes from cyan to green). At the opening views a pixel allows 4.5 to 5.5 steps, so a dial at 4 is
never above it, on any screen. At the opening view the pictures with the dial at 4, 6 and 12 look the same
(`look-look1-m.png`, `-jb.png`, `-jr.png`).

**Margin** (`m2-sheet.png`, console): with `REACH_MARGIN` 2 in place of 3 the Julia shell 0.7 rows read Fast 11.4
(3: 7.9), Fine 10.5 (7.0), Detail 3 21.6 (16.6). Kept 3.

**Smoke test**: `tools/smoke.json`, unchanged, on the final page: 42 steps, exit 0, no console errors
(`smoke-final.log`, 03:46). The inside colouring step reports 5 clearly different colours at 7 places; the two
trap solid steps report 12 of 49 probes (Mandelbrot) and 13 of 49 (Kleinian). No step is out of date.

**The dial on the page** (`dial.log`, `python out/r6/colour/dial.py`, final page): shown at the opening settings
with the value 4; typing 9 sets 9 and starts no program (`R.compiles` unchanged); 2.6 becomes 3; with Extreme
ranges the slider goes to 60; hidden in the 2D view, in the Kleinian view and with "Colour by" at Escape count;
back when "Orbit trap" is chosen again. No console errors.

**Compile time** (`perf-final.log`, `python out/me/perf.py base4 r6-colour v6 base4 r6-colour v6`, dial at 6, the
shader is the same): opening Mandelbrot program 2235 and 2142 ms (base4 2053, 2327; v6 1760, 1813; limit 2600).
Kleinian 685 ms in the first round (base4 606, v6 962) and 1296 ms in the second, where base4 itself read 1017
(limit 1100): the second round was disturbed. So the Mandelbrot program takes about 0.4 s longer to prepare than
v6's and stays under the limit.

**Drawing time** (`chain2.log`, `python out/r5/speed/kdraw.py 2 v6 r6-colour base4`, pages in turn, least of 8
drawings a visit, final page): no difference can be read out of the noise of the shared GPU. Visits: v6 K 129, 120,
M 692, 621, J 427, 661; r6-colour K 126, 157, M 587, 445, J 541, 507; base4 K 100, 94, M 488, 344, J 511, 434.
Least: base4 K 94, M 344, J 434; v6 K 120, M 621, J 427; r6-colour K 126, M 445, J 507. v6 itself reads 80
percent above base4 for M here, where round 5 measured 0 to 6 percent on a quiet GPU. Reasoned: per lit pixel the
count query (one neighbouring orbit) is replaced by the fit query (the neighbours of the quality setting), two at
Ultra fast, against some hundreds of queries for the march, shadows and crevices, so a real change should be under
two percent. **The Kleinian saving (no fading weights) did not measure**: 126 against 120 ms, inside the noise.

**A 3D model's colours** (`model-ref-new.png`, `python out/r6/colour/model.py`, Julia c = -1 from above, dial at
6): the colours `sampleSlice()` gives the top of the solid, beside the picture. v6: specks and fine rings along
every edge. Now: smooth, with the same arcs in the same places as the picture. The model shows fewer and broader
arcs than the picture because its samples (160 across) are coarser than the page's pixels, and the rule reads
fewer steps where a sample is larger. Not run through the mesh module (`out/r4/mesh/run_tests.py`).

**The first reference set had one mistake**: the zoom was set before the subject, and choosing a mode frames the
solid again, which undid it for Julia and Kleinian. `scenes.py` now applies it last; the zoom scenes of both sets
were drawn again (v6 is frozen, so its pictures are the same whenever they are drawn).

## Sheets to look at

All in `out/r6/colour/`. In a pair sheet the upper row is v6, the lower row the final page, and the columns are
Ultra fast, Fast, Balanced, Fine, Detail 0.2, Detail 3, 24, 60, 120 iterations, zoomed in 2 and 8 times.

1. `pair-jb-shell07-ref-final.png`: the fault of `out/me/look8-a.png` and its cure in one sheet. Upper row teal,
   yellow with rings, green, orange rings when zoomed; lower row the same cyan body with yellow necks in all eleven.
2. `pair-m-shell07-ref-final.png` and `pair-jr-planes-ref-final.png`: the same for the opening Mandelbrot view and
   for the hardest case (thin bands on the rabbit).
3. `pairs-solids-ref-final.png` (v6 left, final right of each pair): trap solids keep their colours at Fast and
   Ultra fast (s04 to s08), and what the skip dial now means in Mandelbrot mode (s01, s16, s18).
4. `pairs-extra-ref-final.png`: what the acceptance list does not cover, each at two presets: power -2, the
   mosaic, three tones, "the step at which it came nearest" (x07, x08: v6 differs between Balanced and Ultra
   fast, the final page does not), "blended with the escape count", "the side", classic power 8.

Also: `zoom-final.png` (Balanced magnified beside the real zoom), `diffmaps-final.png`, `look-look1-m.png`,
`look-look1-jb.png`, `look-look1-jr.png` (the opening look for the dial at 4, 6, 12, glow width 1, 2, 3, trap
radius 1 and 0.7; drawn while the dial started at 6), `sheet-fixed-final.png`, `sheet-solids-final.png`,
`t1-sheet.png` and `t2-sheet.png` (the first build without `PH_FIT` and the first with it), `model-ref-new.png`.

## For whoever joins these files into the page

1. Take the three files together. `40-render.js` differs from base6 in one line (`sceneWant` hands `klein` to
   `glNeeds`). No other file needs a change. Program keys are as they were.
2. New state key `S.colour.reach` (starts at 4), control id `col-reach` by the usual pattern. A saved state
   without it reads as 4.
3. `tools/smoke.json` passes as it is. Its picture `out/smoke-21b-trap-solid-m.png` now shows another solid (see 5).
4. Every 3D picture coloured by a trap changes: calmer, and the same at every setting. Nothing else changes.
5. **Closing text, "Why did the orbit trap only recolour the surface in 3D?"** No longer true: "With the Sphere
   shell, a Mandelbrot picture starts as plain balls: try the cross or the ring as Trap shape, or raise the skipped
   steps to 2 or 3." Suggested: "“Orbit steps skipped at the start” means the same in every kind of picture: at 0
   the trap shape itself is part of the solid, and at 1, where it starts, the shape is left out and its first echo
   shows. Higher numbers peel the large outer pieces away." (The sentence "the solid keeps its colours at every
   quality setting" is true.)
6. **Closing text, "Why did solids look like a stack of slices, even at Fine?"** No longer true, from "The last
   few steps now fade out of the colouring" to the end of the paragraph: "This is cured for the opening pictures
   of Mandelbrot and Julia sets, and the Kleinian view never had it. It is not finished. With another Trap radius
   faint rings can come back, and the colours a trap gives a surface still shift with the quality setting and with
   the Iterations. The next version reads a fixed number of orbit steps, from a point on the surface itself, to end
   that. The price so far is a calmer picture than before. A Glow width of 2 or 3 brings more colour back."
   (The Kleinian view did have the fault in another form: its trap colours changed with the quality setting.)
   Suggested paragraph: "The slices were in the colouring, not in the shape: drawn in one plain colour, the same
   surface was smooth. A ray stops a hair above the solid, and the colour used to be read from there, from every
   step of the orbit. The height of that hair changes from pixel to pixel and from one quality setting to the
   next, and every further step of the orbit turned it into another ring. Now the colour is read from the surface
   itself, and the trap reads a fixed number of steps: the number on the dial “Orbit steps the trap reads” in
   Colour and light. So a place keeps its colour at Ultra fast, Fast, Balanced and Fine, at any Detail, and
   while you zoom in. Raise the dial for finer patterns. Steps too fine for the picture to show are left out and
   come in as you zoom in. In the Kleinian view the search now stops at the pearl the ray hit, which keeps its
   colours steady too. Two things still move a colour a little: Iterations below about 24, where the solid itself
   is still changing shape, and a Detail of 3, which draws the solid fatter. The picture is calmer than Version 5
   was. A Glow width of 2 or 3 brings more colour, and so does a Trap radius of 0.7 in the Mandelbrot picture."
7. "What does the page open with?" could add: "“Orbit steps the trap reads” starts at 4."
8. The note under "In the 3D view the trap" and the dial's help text are in `25-colour.js` and are already right.

## Not done, and risks

- **The target number of SPEC6 is not met everywhere** (table above). To the eye the presets agree. Detail 3 and
  thin bands are the weak rows.
- **Two 2D pictures differ by 1 of 255 in one and three pixels.** Cause reasoned, not traced.
- **The opening look (item 4 of SPEC6): glow width and trap radius were left at 1.** Both act on the 2D view too,
  and its opening picture was not to change. The sheets say: radius 1 with glow 1 is the most colourful for both
  Julia sets (radius 0.7 turns Julia c = -1 one flat colour); the Mandelbrot picture would gain from glow 2 (a
  gradient in place of the flat blue top) or radius 0.7 (arcs everywhere). If the 2D opening picture may change,
  glow 2 is the one to try. Only the dial's start was chosen (4), from the zoom measurements, not from the sheets:
  at the opening view 4, 6 and 12 look the same.
- **The dial does nothing above about 5 at the opening view** (a pixel cannot show more), which may feel dead until
  the view is zoomed in. The help text says so in plain words.
- **Kleinian, planes centred on the origin**: every pearl that is an image of the wall y = 0 now has the one
  colour of "touching the trap", because that wall is one of the trap planes. It is true of the surface, and
  plain to look at (`pair-k-planes-ref-final.png`). Moving the trap centre changes it.
- **Ultra fast** agrees in colour but is the weakest preset (12 to 19): its hits are found to about a pixel only.
- **3D model colours** were checked by sampling, not through the mesh module, and with the dial at 6.
- **Kleinian models**: volume samples do not use the landing rule (their distance has to stay exact), so a
  Kleinian model's trap colours are as they were in v6.
- **The mosaic with a trap solid and 0 steps skipped**: the colour module still does not see step 0 of the small
  sets (as before).
- **Timings**: the GPU was shared. Compile time of the opening program is up by about 0.4 s against v6.
- Not looked at: saved pictures (reasoned to agree, because `45-export.js` hands over the same page pixel through
  `px`), other drivers, the look on a large screen.
