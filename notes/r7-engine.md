# Round 7, engine (`src/js/25-colour.js`, `src/js/30-shaders.js`, `src/js/40-render.js`)

Started 04:03, last source change 05:10, last test 05:12 (the smoke test), notes finished 05:17 (74 minutes). Scripts, logs and pictures: `out/r7/engine/`.
Test page: `python build.py --name r7-engine --base base7a --use src/js/25-colour.js src/js/30-shaders.js src/js/40-render.js`.
Compared with `dist/v7a.html` (base7a as it is). Every claim says whether it was **measured** or **reasoned**.

## State in one paragraph

Of the four majors, two are cured here (solids-2, mesh-1 as far as the samples go), one was already cured by round 6
(solids-1), and one is not cured (kleinian-1): its cause is found and proved by four pictures, it is not what the
tester suspected, and the page now says in plain words when it happens. Of the minors, flat-2, flat-3, flat-5,
solids-3, solids-6 and walk-2 are done, solids-4 has its note, flat-4 turned out not to be the iteration limit and
has a true sentence instead of the suggested one, and solids-5, words-4 and words-5 are not fixed (what was learnt
is below). 28 of the 30 pictures that must not change are identical to `dist/v7a.html` (largest channel difference
0); the other two show an inside coloured by the trap, which flat-5 changes on purpose. The smoke test
`tools/smoke-v6.json` passes on the final page (42 steps, exit 0, no console errors).

## Per defect

**kleinian-1 (major): not fixed. Cause found, hint added.**
- Reproduced on v7a (`before-kleinian.png`): entries 3 and 24 sliced, 0 and 21 clean.
- The cause is not the third map and not the march. Measured with four pictures (`x-sheet-1.png`, first row):
  entry 3 with the third map switched ON is still sliced; entry 0 with the third map switched OFF is still whole;
  entry 0 with the trap centre moved to x = 0.6 is sliced; so is any group whose μ has a real part.
- What happens (reasoned, and it fits all four): the search carries a point back into one copy of the pattern (a
  slide by 2 along x, then a half turn about μ/2 above the dividing line) and tests the trap after each map. A piece
  of the trap solid that reaches across the edge of a copy is tested, on the far side, against another part of the
  trap, so the piece ends at the edge: the flat faces are those edges (planes and their images, which are
  spheres). When the real part and the j part of μ are 0 and the trap is centred on x = 0 and z = 0, the two sides
  of every edge are mirror images of each other, the trap value agrees across the edge, and the piece carries on as
  its own reflection. That is why entries 0 and 21 look whole. Shortening the step cannot help: the solid itself
  has the cut (the tester's Fine picture shows the same).
- A real cure needs the trap to be tested in a way that does not depend on the copy: test only the point where the
  search comes to rest (it ends in a cycle of two points, which is the same for every point of an orbit), together
  with its neighbours across each edge (the slide by ±2, the half turn, and the map applied once more), in place of
  every step along the way. That changes every Kleinian trap solid, including the good ones, and "steps skipped"
  would need a new meaning there. Not started: it wants a round of its own.
- Done: a note under "In the 3D view the trap" while a Kleinian trap solid is on and μ has a real or j part or the
  trap centre is off x = 0, z = 0 (`colKleinCuts`). Measured: shown on entry 3, not on entry 0 (`repro-final.log`).
- Also seen: entry 0 with the trap centre at y = 0.5 gives a black stage (the camera is inside a piece). Not looked into.

**solids-2 (major): fixed.**
- Reproduced on v7a: Julia c = -1, shell 0.7, thickness 0.005 is an empty picture; Mandelbrot cross at 0.01 is hairlines.
- Cause: the rule that fades layers thinner than `TRAP_THIN` pixels compared the layer's own thickness, so a thin
  trap lost its first, large pieces too. The rule is about how finely the layers are folded (the stretch), so a
  trap thinner than `TRAP_REF` (0.05, where the dial starts) now fades where a trap of that thickness would, in
  proportion: `2 (w / wr) max(TRAP_THIN gPix - wr / stretch, 0)` with `wr = max(w, TRAP_REF)`. Same in the colour
  module's touch record and in its "too fine to colour" test. For thickness 0.05 and more nothing changes.
- Measured (`pairs-solids-2.png`, `repro-final.log`, through the typed boxes): share of bright pixels of the Julia
  chain 21.2 % at 0.05, 20.4 % at 0.02, 20.0 % at 0.005 (v7a: empty at 0.005); Mandelbrot cross at 0.01 7.7 %
  (the tester had 0.77 %). All trap solids at thickness 0.05 are pixel-identical to v7a (17 scenes, `cmp` in
  `cmp-defects-new1-final.log` and the console run before it).
- To look at: the Mandelbrot cross at 0.01 has fuzzy tips (`new1/d-solids-2-m-thick001.png`); the Julia chain at
  0.005 is clean.

**solids-1 (major): already cured by round 6.** With the tester's own steps (cross, Is the solid, 0 typed into the
skip box) the picture is the cross with its coral: 9.9 % bright pixels, mean colour 22, 27, 29 (v6: 0.1). Measured
on v7a (`ref/d-solids-1-*.png`) and on the final page (`final/repro-solids-1-m-cross-skip0.png`). No change made.

**mesh-1 (major): the samples are fixed; the Julia model at 128 cells is close, not equal.**
- Reproduced on v7a with the mesh tester's scripts (copies in `out/r7/engine/mesh/`, page chosen with `MESH_PAGE`):
  round 6 had already brought the Mandelbrot model from 91.5 to 6.0 degrees of median hue difference and the rabbit
  from 66.3 to 12.8, but the Julia set for c = -1 was worse (49.5), the cut face was still blue (20.6), and the
  Kleinian model, which had matched in v6 (2.8), no longer did (16.2: its two wall spheres one plain violet where
  the picture has blue and magenta).
- Cause of what was left: a sample's colour was read where the sample is (up to a cell off the surface) and with
  the number of steps a sample spacing allows (2.4 at 128 cells), where the picture reads 4 from the surface.
- Done (all in the program for volume samples only, see `RAW_FIT`): a sample of an equation whose estimate reads
  between 1.5 spacings inside and 3.2 outside finds the surface along its own slope (two readings: the straight
  line of `PH_FIT`, then the line through the last two) and reads the trap colour there, with the picture's own
  number of steps (`uPx` carries the picture's height in page pixels for these draws, the camera is the
  snapshot's). A Kleinian sample makes one more query in which the search lands on the pearl beside it. A sample
  deeper inside, or inside the solid in one of the two slices next to the cut plane, gets the cut face's colour
  (the hatching evened out, or the inside colouring when "Colour the cut face" is ticked). The distance a sample
  hands back is untouched (measured: every outline overlap equals v7a's).
- Measured, median hue difference between picture and model, and share within 30 degrees (`mesh/check-final.txt`,
  v7a in `mesh/check-v7a.txt`): see the table under Measurements.
- Not right yet: at 128 cells the Julia model's fine orange arcs are broader and a little mottled, because the
  pattern of the fourth step is finer than a cell (`mesh/r7-engine/pics/cmp-julia1-128.png`); at 256 cells it
  reads 7.5 degrees. The model's cut face is plain in the middle and keeps a coloured rim two to four cells wide
  (`mesh/r7-engine/pics/cmp-cut-128.png`). Reasoned: the rim is the band by which the model is fatter than the
  solid (mesh-4): its samples lie outside the solid and rightly carry the surface's colour. See "For the mesh module".

**solids-5: not fixed.** The holes are layers eaten in patches by the thin layer rule: it removes a layer where its
wall is under 2 pixels, which at the opening view is a stretch of 5 to 7.5, and a bubble made by step 3 or later
straddles that. Removing a layer as a whole needs a rule by step number or by the size of the piece instead of by
wall thickness, and a new look for every trap solid. Not started. The pictures are unchanged (identical to v7a).

**solids-4:** two notes. Outside the Kleinian view (Point, Line, Ray as a solid): move the trap centre when the
object looks like the plain set (measured: Julia c = -1, Point, centre x 0.5, thickness 0.2 gives chains of beads,
`x-sheet-1.png`). In the Kleinian view: Point, Line and Ray give much the same lace, the other four shapes give
objects of their own. The Kleinian lace itself is unchanged (a thin layer rule there would also take the lace off
the good pictures).

**solids-3:** the same note says to raise the trap thickness. Measured: thickness 0.3 gives a full object for the
Mandelbrot Point and for Julia c = i, 0.2 for the Mandelbrot Ray (`x-sheet-1.png`, second row).

**solids-6:** the note under the choice now names what changes the object (thickness, steps skipped, radius,
centre) and says the iterations hardly change it.

**flat-2:** in the Kleinian view "How quickly the orbit settles" now shows the depth (as "How deep inside"), with a
note that says so. Measured: `pairs-flat.png`, first pair.

**flat-3:** fixed. The cut face's "How deep inside" now uses the renderer's own estimate at the cut point (the
query `PH_CUT` asks for three neighbouring orbits when that choice is on), which is what the 2D view draws from.
Measured: `pairs-flat.png` (Mandelbrot and Julia c = -1: the same magenta body and rings as the 2D view).

**flat-5:** fixed. While the inside is coloured by the trap in the outside's own palette, the inside starts half a
turn of the palette away (`uPalInO`), and the note says so. Measured: `pairs-flat.png`, last two pairs.

**flat-4: it is not the iteration limit.** Measured: at height 0.003 the picture at 2000 iterations (Extreme
ranges) is the same as at 300 (`flat4-300-vs-2000.png`). The first try (1500 set through the state) was no test:
the dial holds the count at 400 without Extreme ranges. Reasoned: deep in a spiral the set is a web of threads,
each drawn about a pixel wide by the estimate, and they run together. The help of "Outline width" now says that,
and that more iterations do not change it.

**words-4: not fixed.** On v7a and on the final page (identical pictures) the rough estimate draws 2993 pixels that
the exact one leaves as background (3.3 % of the solid; the tester had 5.5 % on v6) and misses 3025 that the exact
one draws. In my pictures the dark, striped band under the lower edge is in the exact picture
(`before-words4-crop.png`: rough above, exact below). Not traced.

**words-5: not fixed.** Reproduced (`ref/d-words-5-ultra-i40.png`). It is not rays running out of steps: with 300
steps in place of 90 the wedge is the same (measured, `x-sheet-1.png`, last row). Ultra fast has no shadows, so it
is not a shadow. Reasoned, not tried: the slope samples of the rough estimate, whose size is wrong by a factor that
changes from place to place at 40 iterations. A cure would take the four slope samples with the exact estimate
when the march is rough, and measure the gauge for shadows separately.

**walk-2:** done. While the context is lost the status line reads "The graphics of this page were interrupted. The
picture comes back by itself." (`LOST_WORDS`), also after a click; after the context is back it reads "Done: 12
passes ..." again. Measured: `repro-final.log`. `idle()` is unchanged (still true while the context is lost).

## Names added or changed

| Name | Where | Meaning |
|---|---|---|
| `TRAP_REF` | const, `GL_HEAD` | 0.05: a trap thinner than this fades as one of this thickness would |
| `RAW_FIT` | macro, 0 or 1 | 1 in the program volume samples are drawn with; `GL_TAIL` defines it as 1 when it is not defined |
| `glNeeds(needs, klein)` | 30-shaders.js | writes a fourth line, `#define RAW_FIT`, from `needs.raw` |
| `glNeedsKey(needs)` | 30-shaders.js | adds `'r'` for `needs.raw`: program keys of the raw programs end in `r` (`...|r`, `klein|r`, `...|sr`); all other keys are unchanged |
| `RAW_OUT`, `RAW_IN`, `RAW_CUT`, `RAW_ABOVE`, `RAW_HATCH` | consts, `GL_TAIL` | 3.2, 1.5, 1.01, 3.01, 0.12: which samples read their colour from the surface (by estimate, in sample spacings), which slices make the cut face (from 1.01 spacings below the cut plane to 3.01 above), the share of ink in the model's cut face |
| `rawCut`, `rawFace` | locals of `main()` | this volume sample is coloured as the cut face; this slice is one of those the cut face is made between |
| `crawl` in the flat branch | `main()` | counts a volume sample's queries (0 the sample itself, 1 and 2 the readings, 3 the colour) |
| `ts`, `tIn`, `dOut` in the flat branch | `main()` | reused: place and value of the reading before; the distance the sample itself read |
| `uPx` for a volume sample | uniform | the height of the snapshot's picture in page pixels (was 1) |
| `uPalInO` | uniform, `GL_COLOUR` | added to the palette shift for the inside: half a turn while the inside is coloured by the trap in the outside's palette, else 0 |
| `snap.wantRaw`, `snap.PR`, `snap.genR` | 40-render.js | a snapshot's program for volume samples, started when first asked for |
| `snapProg(snap, raw)`, `snapReady(snap, raw)` | 40-render.js | second argument: the program for volume samples. Without it they behave as before |
| `LOST_WORDS` | 40-render.js | the status line while the graphics context is lost |
| `colTrapThin(c)` | 25-colour.js | the trap is a point, a line or a ray |
| `colKleinCuts(c)` | 25-colour.js | a Kleinian trap solid would show cut pieces (μ has a real or j part, or the trap centre is off x = 0, z = 0) |
| `colViewSync` | 25-colour.js | its signature also holds whether μ leans, so the note comes and goes with the dials |
| `setColourUniforms` | 25-colour.js | `uCutFace` and `uInMode` are set for volume samples too (they were 0 there) |
| `pixelColour`, kind `COL_CUT` | `GL_COLOUR` | "how deep inside" reads `d` as handed in (the pure power estimate is gone); also used for volume samples inside the solid |
| `colPick` | `GL_COLOUR` | inside colouring 4 in the Kleinian program shows the depth |

Changed texts (25-colour.js): the note under "In the 3D view the trap"; three new notes there (thin shapes, thin
shapes in the Kleinian view, cut pieces in the Kleinian view); the note for the inside coloured by the trap; a new
note for "How quickly the orbit settles" in the Kleinian view; the help of "Outline width, pixels".

`de()` still has one call site and `pixelColour` is still called once. The picture's program (RAW_FIT 0) has no
new branch in the loop of `main()` other than `qn = uInMode == 3 ? 3 : 0` at the cut face.

## Measurements

All measured. Four builds of the test page were measured: 04:35 (first), 04:49 (the model's code moved into its
own program), 05:03 (plus the Kleinian sample's second query) and 05:10 (final: plus a wider band of slices for
the model's cut face). The last two steps are inside `#if RAW_FIT`, that is in the model's program only. Which
build each number comes from is said; "final build" in the tables below is the one of 05:03 unless it says 05:10.

**Pictures that must not change** (`python out/r7/engine/scenes.py`, 30 scenes at 1000 x 700; `ref/` drawn from
`dist/v7a.html` between 04:10 and 04:13, before any source change; `cmp-fixed-final.log`, build of 05:03): 28 of 30
identical, largest channel difference 0. They are the 2D view (opening Mandelbrot, Julia c = -1, rabbit, slice at
0.3, Kleinian, power -2, mosaic, inside "settles", cross in bands), 3D by escape count, depth and clay (Mandelbrot,
Julia, Kleinian, power -2, Ultra fast, the hatched cut, the mosaic) and the trap-coloured 3D pictures (opening
Mandelbrot, Julia and Kleinian, Julia at Fine and at Ultra fast, the rabbit, power -2, the mosaic, Kleinian cross
in bands at Fast). The two that differ, on purpose (flat-5): `f09-flat-j-in-trap` (10.7 % of the pixels) and
`f24-cut-j-face-trap-escape` (6.1 %), both an inside coloured by the trap in the palette "Same as outside".

**The testers' scenes** (55 at 1400 x 950, `ref/d-*` from v7a drawn 04:14 to 04:17, `final/d-*` from the 04:49
build; `cmp-defects-ref-final.log`): 46 identical to v7a, largest difference 0. The 9 that differ are the ones a
defect asked to change: solids-2 (Julia at 0.005 and 0.02, Mandelbrot at 0.01, and the colours of the Kleinian
ring at 0.01), flat-2 (Kleinian "settles"), flat-3 (the two cut faces), flat-5 (the two insides). Not drawn again
on the final build: it differs from the 04:49 build only inside `#if RAW_FIT`, which these pictures' programs do
not contain (reasoned). On the first build the four Julia trap solid scenes differed from v7a by 1 of 255 in
0.0036 % of the pixels; with the model's code out of the picture's program they are identical again.

**The testers' own steps, through the controls** (`python out/r7/engine/repro.py r7-engine final`,
`repro-final.log`, 04:49 build, no console errors): see solids-1, solids-2 and walk-2 above; the notes for thin
shapes, cut Kleinian pieces (shown on entry 3, not on entry 0), "settles" in the Kleinian view and the inside by
the trap are on the page where they should be.

**3D model against picture** (the mesh tester's `drive.py` and `check.py`, copied to `out/r7/engine/mesh/`; median
hue difference in degrees over the saturated pixels both show, share within 30 degrees in brackets; final build,
`mesh/check-final.txt`; v7a `mesh/check-v7a.txt` and `check-v7a-klein.txt`; v6 from the tester's report):

| Model | v6 | v7a | final | outline overlap (v7a = final) |
|---|---|---|---|---|
| Mandelbrot, 128 cells | 91.5 (18 %) | 6.0 (83 %) | 3.9 (89 %) | 0.883 |
| Rabbit, 128 | 66.3 | 12.8 (76 %) | 4.5 (86 %) | 0.889 |
| Julia c = -1, 128 | 32.5 | 49.5 (32 %) | 15.2 (75 %) | 0.855 |
| Julia c = -1, 256 | | | 7.5 (91 %) | 0.942 |
| Cut at z = 0, 128 | 28.8 | 20.6 (63 %) | 9.8 (77 %) | 0.889 |
| Kleinian, 128 | 2.8 | 16.2 (76 %) | 3.5 (91 %) | 0.960 |

The Kleinian model had matched in v6 and no longer did in v7a: round 6 made the picture's search stop at the pearl
it hit, and the model's samples did not follow. They do now. Job times: the first job of a page 3.8 s (Mandelbrot,
128 cells: it includes preparing the model's program), then 0.5 to 1.6 s. On the build of 05:10 the cut, the Julia
and the Kleinian model were made again and read the same (9.8, 15.2, 3.5; `mesh/check-final2.txt`).

**Compile time** (`python out/me/perf.py`, least of 3 fresh compiles a visit, GPU and CPU shared):

| Build | Run | M compile | K compile |
|---|---|---|---|
| base4 | `perf-1.log`, 04:40 | 1475, 1665 ms | 691, 621 ms |
| v7a | same run | 2000, 2236 ms | 731, 922 ms |
| first build (model's code in the picture's program) | same run | 2527, 2573 ms | 886, 1001 ms |
| base4 | `perf-final.log`, 04:55 | 1857, 1490 ms | 660, 679 ms |
| v7a | same run | 2301, 1921 ms | 865, 885 ms |
| 04:49 build | same run | 2006, 1962 ms | 830, 819 ms |
| base4 | `perf-final-2.log`, 05:06 | 1496, 1424 ms | 634, 689 ms |
| final build | same run | 2025, 1854 ms | 809, 910 ms |

So the picture's program prepares as fast as v7a's (limits 2600 and 1100 ms), and the first build is why the
model's code got a program of its own: it cost half a second. The model's program is prepared when the first model
of a formula is asked for.

**Drawing time** (same runs, least of 5 drawings a visit, in ms; the GPU was shared with five others and single
visits jump by a factor of three):

| Page | M | J | K |
|---|---|---|---|
| base4 (4 visits) | 494, 759, 725, 341 | 1054, 1332, 1007, 415 | 216, 209, 253, 215 |
| v7a (4 visits) | 886, 766, 694, 689 | 1620, 1641, 1121, 457 | 210, 255, 328, 306 |
| first build (2 visits) | 840, 743 | 1169, 462 | 258, 302 |
| 04:49 build (2 visits) | 418, 873 | 1247, 1388 | 241, 306 |
| base4 (2 more visits, `perf-final-2.log`) | 341, 369 | 851, 927 | 241, 223 |
| final build (2 visits, same run) | 741, 823 | 1289, 485 | 325, 338 |

Least of all visits: base4 M 341, J 415, K 209; this round M 418, J 462, K 241 (23, 11 and 15 percent above
base4); v7a M 689, J 457, K 210. **Read with care:** the least visits are within a quarter of base4, but five of
this round's six Mandelbrot visits read 740 to 870 ms, and so do all four of v7a's (690 to 890), while base4 read
341 to 370 in four of its six. So under this load the opening Mandelbrot picture of v7a, and of this round with
it, draws about twice as long as base4's most of the time. Round 6 saw the same of v6 and put it down to the
shared GPU; I cannot tell from here. It is not from this round (reasoned: the picture's program differs from
v7a's only at the cut face, `qn` for "how deep inside", and in the trap solid's fade term, neither of which the
opening pictures use), but the target "within a quarter of base4" is shown only by the least visit. A run on a
quiet GPU should settle it: `python out/me/perf.py base4 v7a r7-engine base4 v7a r7-engine`.

**Smoke test**: `tools/smoke-v6.json` on the final build of 05:10: 42 steps, exit 0, no console errors, the model
job delivered its zip (`smoke-final.log`, 05:12). It also passed on the builds of 04:49 and 05:03.

## Sheets to look at

All in `out/r7/engine/`. In a pair sheet the upper picture is v7a and the lower one this round.
1. `pairs-solids-2.png`: thickness 0.005, 0.02, 0.05, 0.15 on the Julia chain; 0.01 and 0.05 on the Mandelbrot cross.
2. `pairs-flat.png`: flat-2, flat-3 (cut face beside the 2D view), flat-5.
3. `mesh/r7-engine/pics/cmp-julia1-128.png`, `cmp-julia1-256.png`, `cmp-cut-128.png`, `cmp-klein-128.png` against
   `mesh/v7a/pics/` of the same names: picture, model, outlines.
4. `before-kleinian.png` and `x-sheet-1.png` (first row): kleinian-1 and the four pictures that show its cause.
5. `x-sheet-1.png`: second row the thin shapes with more thickness and with a moved centre; third row flat-4 at
   2000 iterations and words-5 with 300 steps.
6. `before-solids-a.png`, `before-solids-b.png`, `before-flat.png`, `before-words.png`: everything before any change.

## For the mesh module (`src/js/46-mesh.js`, not mine)

1. `meshPoint()` takes the colour of the outside end unless the inside end is outside the solid (`w = din <= 0 ? 1 : s`).
   Both ends now carry the colour of the surface nearest to them whenever they lie within 1.5 spacings inside or
   3.2 outside by the estimate, so the colour can be blended by the point's place on the edge for every edge
   (`w = s`). Exception: a point of the cut face (its outside end is outside only because of the cut plane or the
   wall of the grid). There the colour should come from an end whose own estimate is at or below zero: such an end
   holds the cut face's colour. Where both ends read above zero the point lies in the band by which the model is
   fatter than the solid, which is the coloured rim of the cut face today; it goes when offset 0 means "where the
   picture has it" (mesh-4), or the mesh could give the whole cut face the colour of the nearest end that is
   inside the solid.
2. The first model of a formula now waits for its own program (measured: 3.6 s for the first 128 cell job where it
   took about 1 s, later jobs as before). The panel could say "Preparing" for that time.
3. A snapshot made in the 2D view still gives the 3D picture's colours, as before.

## Closing text (`src/body.html`, not mine)

1. "This works in Mandelbrot, Julia and Kleinian pictures, and the solid keeps its colours at every quality
   setting." Not true for every Kleinian group. Suggested: "This works in Mandelbrot and Julia pictures and in
   Kleinian pictures whose group does not lean (the real part and the j part of μ at 0). In a leaning group some
   pieces come out cut open, and the page says so beside the choice. The solid keeps its colours at every quality
   setting."
2. "The inside can stay Plain, or be coloured by Orbit trap, Where the orbit ends up, How deep inside, or How
   quickly the orbit settles, ..." Add: "In the Kleinian view the last of these shows the depth, because that
   search has nothing that settles. Coloured by the orbit trap in the outside's own palette, the inside starts
   half-way round the palette, so that the set does not look like a hole."
3. "Such rays now get past the solid, and a ray that runs out of steps away from the surface shows the
   background." Still not quite true with the roughest estimate (words-4, words-5). Suggested addition: "With the
   Rough distance estimate the outline can still differ a little from the exact one, and at Ultra fast with many
   iterations a bead can show a dark patch. Balanced does not have either."
4. "Save a 3D model turns the solid into a mesh ..." could add: "Its colours are read from the surface the same way
   the picture's are, and a solid that is cut open gets the plain colour of the cut face there."
5. Any sentence that tells the reader to lower the iterations to thin out a trap solid is no longer what the page
   says: the note names the trap thickness, the steps skipped, and the trap radius and centre.

## Not done, and risks

- kleinian-1, solids-5, words-4, words-5: see above.
- The Julia model at 128 cells (15 degrees) and the rim of the model's cut face.
- A trap thinner than 0.05 shows the same layers as at 0.05 with thinner walls. Walls well under a pixel are drawn
  about a pixel and a half thick by the march, so the tips of thin rods look fuzzy.
- Two pictures of the fixed list changed on purpose (flat-5): the 2D inside coloured by the trap and the painted
  cut face, both with the palette "Same as outside".
- The first model of a formula takes a few seconds longer (its own program).
- Timings were taken while five others used the GPU.
- Not looked at: saved pictures (45-export.js does not use the raw program), other drivers, a model made from a
  snapshot of the 2D view, a Kleinian trap solid as a model.
