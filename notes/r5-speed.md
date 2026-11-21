# Round 5, speed (`src/js/25-colour.js`, `src/js/30-shaders.js`, program keys in `src/js/40-render.js`)

Started 01:20, last source change 01:55, last test 02:20 (60 minutes). Scripts, logs and pictures: `out/r5/speed/`.
Test page: `python build.py --name r5-speed --base base5 --use src/js/25-colour.js src/js/30-shaders.js src/js/40-render.js`.

## State in one paragraph

The compile targets and the picture target are met, and the Mandelbrot and Julia drawing targets (all measured,
tables below). **The Kleinian drawing target is met only while the GPU is not the limit**: at the opening settings
on a quiet GPU the Kleinian picture draws 5 to 11 percent slower than base4, but in two runs with a busy GPU it
read 31 and 33 percent slower, and at Fine, where drawing is all GPU work, 43 percent slower. 29 of those 43
points are the exact pearl distance of round 4, which SPEC5 says to keep; 13 are not traced.
A new program for the opening settings takes about 1.6 s to prepare (base4 1.4 to 1.7 s, the joined page before
this round 5.4 to 9.9 s), the Kleinian one about 0.6 s, and with every new feature on 2.5 s and 1.3 s. The opening
Mandelbrot and Julia pictures draw within 0 to 7 percent of base4. With the targets met, all 38 fixed scenes were
pixel-identical to `dist/v6a.html` (largest channel difference 0, `out/r5/speed/cmp-ref-targets-met.log`). After
that I did the optional item (a) and half of (b), which change the colours of trap solids on purpose: 32 of the
now 40 fixed scenes are still identical, the 8 that show a trap solid differ (before and after pictures below).
The files of the state "targets met, no picture changed" are kept as `out/r5/speed/*.targets-met.js` in case the
colour change is not wanted.

## What cost the compile time (measured before any change)

`python out/r5/speed/cost.py v6a m 2` and `... k 2`: the scene program's source is taken from the page, a piece is
replaced by text, and the variant is compiled fresh, least of 2 (`out/r5/speed/cost-v6a.log`).

| Variant of the v6a source | Orbit scene | Kleinian |
|---|---|---|
| as it is | 5.44 s | 4.87 s |
| no call to `cutFaceColour` | 4.26 s | 2.92 s |
| no call to `flatColour` | 3.36 s | 2.21 s |
| no call to `surfaceColour` | 4.19 s | 3.12 s |
| none of the three calls | 1.00 s | 0.35 s |
| only `surfaceColour` left | 2.40 s | |
| only `cutFaceColour` left | 2.55 s | |
| only `flatColour` left (it reaches `colTrapPick` twice) | 3.39 s | |
| `flatColour` without its inside colouring | 4.35 s | |
| `pal()` made trivial (36 copies) | 3.99 s | 2.84 s |
| the trap solid branch of `colTrapPick` dead (4 copies) | 3.24 s | |
| no `pal()` in the three-tone loop | 4.86 s | |
| `TRAP_SOLIDS = false` in the orbit loop / in `kde` | 5.26 s | 3.82 s |
| `trapAdd` empty | 4.13 s | 2.43 s |

What it says: the shader without colour compiles in 1.0 s (0.35 s Kleinian). Each path from `main()` into
`colTrapPick` costs about 1.2 to 1.5 s; there were four. Of one such copy, the trap solid branch is about 0.55 s
and its `pal()` calls about 0.35 s. The trap solid code in the orbit loop costs 0.2 s of compile time (but half
the drawing time, see below).

## What was changed

1. **One call colours every pixel.** `main()` calls `pixelColour(kind, p, nor, t, d, px, hatch)` once, for a slice
   pixel (`COL_FLAT`), a lit hit or volume sample (`COL_HIT`) and the cut face (`COL_CUT`). It replaces
   `surfaceColour`, `flatColour` and `cutFaceColour`. Inside it `colPick` (which now holds what `colTrapPick` and
   `colInside` did) is reached by one path and reads the palette in four places in place of 36: the branches work
   out palette positions, the palette is read at the end.
2. **Programs are built for what the colour settings need.** `colProgramNeeds()` (25-colour.js) answers
   `{ solid, inside }` from the state; `glNeeds(needs)` (30-shaders.js) turns that into two lines of source,
   `#define TRAP_SOLIDS 0|1` and `#define COL_INSIDE 0|1`, which go between `GL_HEAD` and `GL_COLOUR`; `#if` blocks
   in `GL_COLOUR`, `GL_ORBIT`, `GL_KLEIN` and `GL_TAIL` leave the code out. A program built with 0 declares
   `uTrapSolid`, or `uInMode` and `uCutFace`, as constants, so every test of them falls away and
   `setColourUniforms` needs no change (setting a uniform a program does not have does nothing).
   - `solid`: `S.colour.solid > 0` and the trap is not Three tones. Not tied to the 2D view on purpose: a 3D model
     made from a 2D snapshot samples the solid with the snapshot's program.
   - `inside`: in the 2D view, "Inside the set, colour by" is not Plain; in the 3D view, "Colour the cut face like
     the inside of the 2D view" is ticked (also with Plain, which takes the hatching off).
   - Only drop-downs and tick boxes are read. The cut's own tick box is NOT read, because moving the height dial
     switches the cut on, and a dial must never compile.
3. **Program key.** `sceneWant(a, eq, z0, n2, klein, needs = colProgramNeeds())` appends `|s`, `|i` or `|si` to
   the key (nothing for the plain program, so `'klein'` and the old keys are unchanged) and writes the defines into
   the source. `sceneNow()` has the needs in its signature (`R.sig`). `R.want.src()` still gives the full source.
4. **The cut face** makes its extra query (`PH_CUT`) only when it is to be painted; a hatched cut face ends at once.
5. Optional items, after the targets (see their own section): `cOnTrap`, `gOnTrap` in `GL_KLEIN`, and the touch
   record follows the renderer's thin layer rule. `TRAP_THIN` moved from `GL_ORBIT` to `GL_HEAD`.

## Measurements

All with `python out/me/perf.py base4 r5-speed base4 r5-speed` (compile least of 3, draw least of 5, 1100 x 760).
The other engineer used the GPU at the same time, so some runs are disturbed; each line is one visit.

Targets met, before the optional items (`out/r5/speed/perf-1.log`, 01:36, quiet):

| Page | M compile | M draw | J draw | K compile | K draw |
|---|---|---|---|---|---|
| base4 | 1506, 1706 ms | 337, 348 ms | 414, 422 ms | 760, 526 ms | 95, 164 ms |
| r5-speed | 1643, 1606 ms | 358, 354 ms | 442, 418 ms | 612, 764 ms | 102, 114 ms |
| v6a (one visit, same run) | 5854 ms | 508 ms | 710 ms | 4074 ms | 117 ms |

Final files, quiet run at 01:54 (its log was overwritten by the later run, the numbers are copied from the console):

| Page | M compile | M draw | J draw | K compile | K draw |
|---|---|---|---|---|---|
| base4 | 1420, 1435 ms | 340, 331 ms | 420, 420 ms | 526, 546 ms | 94, 92 ms |
| r5-speed | 1548, 1690 ms | 341, 506 ms | 439, 650 ms | 585, 579 ms | 103, 102 ms |

Final files, run at 02:03 while the GPU was busy (`out/r5/speed/perf-final.log`): base4 M compile 1614, 1813,
draw 935, 755, J 1617, 1591, K compile 658, 673, draw 233, 223; r5-speed M compile 1843, 2008, draw 673, 855,
J 1479, 1646, K compile 943, 665, draw 337, 293. Every number is two to four times the quiet one for both pages;
I do not trust the ratios of this run (K reads 31 percent slower here, 5 to 11 percent in the three quiet runs).

Final files, pages in turn over three rounds, least of 8 drawings each (`python out/r5/speed/kdraw.py 3 base4
r5-speed r5-speed-nopearl`, `out/r5/speed/kdraw-1.log`, 02:09, GPU still shared: M and J are slow for both pages):

| Page | K draw | M draw | J draw |
|---|---|---|---|
| base4 | 95 ms | 504 ms | 1634 ms |
| r5-speed | 102 ms | 501 ms | 1689 ms |
| r5-speed with the plain pearl distance (`kpearl` returns h) | 94 ms | 496 ms | 1622 ms |

With every new feature on (`PERF_JS="L.S.colour.solid = 1; L.S.colour.cutFace = true; L.S.colour.inMode = 4;
L.S.cutOn = true; L.S.cut = 0;"`, base4 only gets the cut from this):

| Run | Page | M compile | M draw | J draw | K compile | K draw |
|---|---|---|---|---|---|---|
| 01:39, targets met, quiet (`perf-allon-1.log`) | base4 | 1452, 1416 ms | 229, 223 ms | 281, 301 ms | 523, 524 ms | 92, 98 ms |
| | r5-speed | 2473, 2438 ms | 710, 727 ms | 553, 608 ms | 1328, 1320 ms | 128, 133 ms |
| 01:56, final shader, quiet (console) | r5-speed | 2489, 2865 ms | 699, 682 ms | 546, 534 ms | 1317, 1347 ms | 131, 135 ms |
| 02:05, final, GPU busy (`perf-allon-final.log`) | base4 | 1695, 1713 ms | 565, 640 ms | 972, 1095 ms | 645, 580 ms | 177, 165 ms |
| | r5-speed | 3164, 3098 ms | 3008, 2914 ms | 2274, 2317 ms | 1532, 1776 ms | 492, 137 ms |

One more run at 02:15, GPU busy again (`out/r5/speed/perf-final-2.log`): base4 M compile 2028, 2180, draw 622, 615,
J 1353, 1346, K compile 724, 704, draw 229, 192; r5-speed M compile 2392, 2194, draw 701, 654, J 1487, 1425,
K compile 804, 720, draw 301, 255.

So: compile M 1.55 to 2.4 s (target 2.6), K 0.58 to 0.94 s (target 1.1), everything on 2.4 to 3.2 s (target 4),
in every run, quiet or busy. Draw, features off, against base4 in the same run: M +0 to +6 percent, J +0 to
+7 percent in every run; K +5 to +11 percent in the quiet runs and +31, +33 percent in the two busy ones.

**The Kleinian picture, looked at where drawing is all GPU work** (Fine; `KONLY=1 KDRAW_JS="$('qFine').click();"
python out/r5/speed/kdraw.py 2 base4 r5-speed r5-speed-nopearl r5-speed-nopearl-b4`, least of 2 visits of 8
drawings, `out/r5/speed/kdraw-fine-2.log`, and the same result in `kdraw-fine.log`):

| Page | K draw at Fine | against base4 |
|---|---|---|
| base4 | 289 ms | |
| r5-speed | 412 ms | +43 percent |
| r5-speed, `kpearl` returns the plain distance (no exact pearl distance) | 327 ms | +13 percent |
| the same with base4's own formula (`min(z.y, a - z.y) / max(DF, 1.0)`) | 328 ms | +13 percent |

So the exact pearl distance costs 85 of the 412 ms. It has to stay (SPEC5), so the Kleinian picture cannot come
within a quarter of base4 when the GPU is the limit; at the opening settings on a quiet GPU most of the time is
the page's own schedule, which is why it reads 5 to 11 percent there. The other 13 percent is not traced. One
exact saving that was not tried: in the Kleinian program `gFade` is always 1e9, so `trapAdd` could be built
without the fading weights there (a third switch).

**What is left of the gap to base4 in the equation views** (`out/r5/speed/perf-gap.log`, variants built with
`python out/r5/speed/variant.py`, least of two visits): the differences are smaller than the noise of the shared
GPU. Without the count query of the fading tail: M 345 against 353 ms, J 423 against 431 ms (about 2 percent).
Without the extra turn of the loop as well: 344 and 434 ms (nothing). The trap solid code in the loop was the
rest: v6a drew M in 508 ms and J in 710 ms in the run where r5-speed took 354 and 418. The ring cure and the
exact estimate are untouched.

## Pictures

`python out/r5/speed/scenes.py shoot <page> <label>` draws a fixed list (38 scenes fixed before any change, 2
added later, see the script) and `... cmp <a> <b>` prints, per scene, the largest channel difference and the share
of pixels over 2 of 255. Reference set: `out/r5/speed/ref/` from `dist/v6a.html` (which is byte for byte a build of
`base5`), sheet `out/r5/speed/sheet-ref.png`.

- Targets-met files: 38 of 38 scenes identical to the reference, largest channel difference 0 (set `new1`, 01:36,
  console; the files are `out/r5/speed/*.targets-met.js`).
- Final files (`out/r5/speed/cmp-ref-final.log`, set `new3`): 32 of 40 identical (difference 0). The 8 that show a
  trap solid differ on purpose: 04, 05, 06, 07, 26, 28, 37, 38 (0.3 to 3.5 percent of the pixels). Side by side:
  `out/r5/speed/pairs-fixed-solids.png`.
- The 2D view at the opening settings is identical to base4: scene 17, largest channel difference 0
  (`out/r5/speed/cmp-base4-flat.log`; the same script reports the Kleinian 2D view and a Julia solid as different
  from base4, as round 4 made them, so the comparison does see differences).

## Flipping the settings a program is built for

`python out/r5/speed/flip.py r5-speed new3` (`out/r5/speed/flip-final.log`): through the page's own controls,
the trap as solid on, off, added, trap shape to Three tones and back, inside colouring in the 2D view on and off,
the 2D view off and on with an inside colouring kept, the cut face painted and not, the Kleinian trap solid on and
off. Each first use of a new program showed "Preparing the formula" (2.4 s orbit scene with trap solid, 1.9 s with
inside colouring, 1.2 s Kleinian with trap solid, 0.7 s plain Kleinian), going back was immediate (the program is
kept), and all 14 pictures equal the picture of the same state drawn from a fresh start (difference 0).

## Snapshots

`python out/r5/speed/snap.py v6a r5-speed` (`out/r5/speed/snap-2.log` on the targets-met files, `snap-final.log`
on the final shader): a picture job is started and the live page switched at once, both ways round; then a
snapshot is taken, the live page switched and drawn, and one slice of the snapshot sampled (what the 3D model uses).
- The job started with the trap solid on draws the trap solid (`snap/r5-speed-on-then-off-export.png`) while the
  live page shows the plain set (`...-live.png`); the snapshot's key ends in `|s`, the live one does not.
- The other way round the export is the plain set and the live page the trap solid.
- Targets-met files: both exports, both live pictures and both slices are identical to v6a's (difference 0, the
  same sums and hash). Final shader: the plain pictures and the plain slice are identical; the ones with the trap
  solid have the same shape (1228 of 9216 points inside, the same sum of distances) and the new colours.
- These ran before the last edit (the cut face with Plain); that edit only changes which program a painted cut
  face gets. The smoke test's picture job and model job passed after it.

## The optional items

(a) **Trap solid colours.** Two changes, the second beyond what SPEC5 names:
- `cOnTrap`: the colour module takes "this hit is on the trap's part" from `gOnTrap` (copied in
  `colourCapture()`), as asked. Measured alone (`sol-before` against `sol-after`): it repairs the far blob of the
  Mandelbrot shell at Ultra fast and small pieces elsewhere, but changes under 0.5 percent of the pixels of the
  Julia shell at Fast and Ultra fast, which stayed plain green (`out/r5/speed/sheet-sol-after.png`). So the
  shader engineer's diagnosis was only part of it.
- The real cause: at a point that hovers above the surface, the colour module's record of "the step that touched
  the trap" (least of (distance - thickness) / stretch) went to a late step, whose huge stretch makes any distance
  look small. The renderer does not make that mistake, because it thins out layers under `TRAP_THIN` pixels.
  `trapAdd` now charges the same (`+ 2 max(TRAP_THIN gPix - thickness / stretch, 0)`, equation views only).
  Result: the Julia shell solid shows its "where on the trap" colours all over at Balanced, Fast and Ultra fast
  (`sheet-sol-before.png` against `sheet-sol-final.png`, scenes s04, s05, s15, s16), and the stray patches on the
  Mandelbrot shell and on "by step" are gone (s01 to s03, s14, fixed scenes 04, 28, 37).
- To take it back: use the three `*.targets-met.js` files, or delete the added term in `trapAdd` and put
  `smoothstep(1.5, 2.5, at.w / max(uTrapW, 1e-6))` back in place of `cOnTrap ? 0.0 : 1.0` in `colPick`.

(b) **Kleinian trap solid.** `kde` now sets `gOnTrap` (and `de` clears it for a point inside a wall sphere), so
(a) works there (s09 to s12: small balls in the lace keep their colours). `gPix` is NOT used: the Kleinian solid
has no thin layer rule, and the touch record's new term is switched off for it to match.

(c) Not started.

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `pixelColour(kind, p, nor, t, d, px, hatch)` | `GL_COLOUR` | the one colour hook `main()` calls; replaces `surfaceColour`, `flatColour`, `cutFaceColour` (all three removed) |
| `COL_HIT`, `COL_FLAT`, `COL_CUT` | consts, `GL_COLOUR` | the kinds of pixel `pixelColour` is asked about |
| `colPick(p, depth, inside, deep)` | `GL_COLOUR` | changed: now also does what `colTrapPick` and `colInside` did (both removed) |
| `pal(t, inside)` | `GL_COLOUR` | changed: the palette to read is an argument; the global `gColIn` is removed |
| `cOnTrap` | global bool, `GL_COLOUR` | `gOnTrap` as it stood at `colourCapture()` |
| `TRAP_SOLIDS` | macro, 0 or 1 | was a `const bool` in `GL_ORBIT`; the program can draw the trap as a solid |
| `COL_INSIDE` | macro, 0 or 1 | the program can colour the inside (2D view, cut face) |
| `TRAP_THIN` | const | moved from `GL_ORBIT` to `GL_HEAD`, same value 2.0 |
| `colProgramNeeds()` | 25-colour.js | `{ solid, inside }` for the state in `S` |
| `glNeeds(needs)`, `glNeedsKey(needs)` | 30-shaders.js | the two `#define` lines; the tag `''`, `'s'`, `'i'` or `'si'` |
| `sceneWant(a, eq, z0, n2, klein, needs)` | 40-render.js | sixth argument, defaults to `colProgramNeeds()`; key gets `'|' + tag` when the tag is not empty |
| `hit`, `flatPix` | locals of `main()` | what the pixel is at the end |

`GL_COLOUR` defines both macros as 1 when they are not defined, so `GL_HEAD + GL_COLOUR + ...` without `glNeeds`
still compiles (a full program). Uniform and control names are unchanged. `gFade`, `gPix`, `gOnTrap` keep their
meanings; `de()` still has one call site; the 0.5 cap on the Kleinian step share is untouched.

## Smoke test

- `tools/smoke.json` as it was for base5 passed on the targets-met page at 01:44 (27 steps, exit 0, no console
  errors, real picture job and model job: `out/r5/speed/smoke-1.log`).
- At 01:47 the page engineer replaced `tools/smoke.json` with one that checks their new texts and buttons, which a
  page built from base5 and my files cannot have (it stops at step 7, "the closing text lacks: the count is a free
  choice"). On my final page I therefore ran their saved copy of the base5 test (`out/r5/page/smoke-base5.json`,
  copied to `out/r5/speed/smoke-base5.copy.json`): 27 steps, exit 0, no console errors, picture job and model job
  delivered (`out/r5/speed/smoke-final.log`, 02:00).
- For the join: a page from ALL live files as they stood at 02:01 (`python build.py --name r5-speed-joined --base
  src`) passed the live `tools/smoke.json` of that moment: 38 steps, exit 0, no console errors, including their new
  steps for the trap solid in the Mandelbrot and Kleinian pictures and an inside colouring
  (`out/r5/speed/smoke-joined-try.log`).

## For whoever joins the two halves

1. Take all three files together. `30-shaders.js` needs `pixelColour` and `TRAP_THIN` in its place; `25-colour.js`
   needs the macros; `40-render.js` writes them.
2. Changing "In the 3D view the trap", the trap shape to or from Three tones, "Inside the set, colour by" between
   Plain and anything else in the 2D view, the 2D view itself while an inside colouring is chosen, or "Colour the
   cut face" now prepares a new program the first time (1.2 to 2.5 s, "Preparing the formula"). A test that looks
   at the picture right after such a change must wait for `idle()`.
3. `out/me/30-shaders-ts0.js` and anything else that writes `TRAP_SOLIDS = false` into the source no longer applies.
   `out/r4/shaders/variant.py` and the stand-in colour files of round 4 do not fit the new hook.
4. The page text on trap shapes can say that they keep their colours at the fastest settings too.

## Not done, and risks

- (b) the thin layer rule (`gPix`) in the Kleinian trap solid, and (c) the Kleinian colours that change with the
  quality setting: not started.
- The trap solid's colours in a 3D model (volume sampling, `gPix` = 0) get no thin layer term, so there the touch
  record can still go to a late step. Not looked at.
- The colour change of (a) was judged on 16 + 8 scenes at 1000 x 700, by me, in one pass. Fine was looked at in
  one scene only (s13).
- **The Kleinian drawing target** (within a quarter of base4): met on a quiet GPU at the opening settings, not
  met when the GPU is the limit (+31 to +43 percent). 29 points are the exact pearl distance, which was to stay;
  the rest is not traced. See the table above.
- Timings: the GPU was shared the whole time. The compile targets and the Mandelbrot and Julia drawing targets
  hold in every run, busy or quiet.
- Only this machine (Windows, ANGLE on D3D) was measured. `#if` is plain GLSL ES 3.00, so other drivers should
  take it; not tried.
