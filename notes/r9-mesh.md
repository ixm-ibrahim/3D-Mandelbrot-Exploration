# Round 9, mesh: "Save a 3D model" (`src/js/46-mesh.js`)

Started 05:30, last source change 06:10, last test 06:17 (47 minutes). File changed: `src/js/46-mesh.js` only
(`src/css/46-mesh.css` untouched). Page: `dist/r9-mesh.html`
(`python build.py --name r9-mesh --base base8 --use src/js/46-mesh.js src/css/46-mesh.css`), compared with
`dist/v8.html`. Everything I ran is under `out/r9/mesh/`: `v8/` holds the runs on `dist/v8.html` (made 05:36 to
05:46, before any source change), `r9-mesh/` the same list on the final build, `r9-mesh-first/` a copy of the
checks and pictures of the build before the last step of item 1. The list is fixed in `out/r9/mesh/mine.py` and
drawn again with `bash out/r9/mesh/run.sh <page> first cutface warn standard neg` (drive.py and check.py are the
mesh tester's, pointed at a page by its name; `cmp.py` puts two pages side by side; `pairs.py` makes the sheets).
The four edits are kept as scripts (`edit1.py` to `edit4.py`), and `46-mesh.before.js` is the file as it was.

Every claim below says whether it was **measured** or **reasoned**.

## Item 1, the cut face of a model: fixed

**Seen on v8** (`out/r9/mesh/v8/pics/cmp-cutm-128.png`, close up in `sheet-cut-close.png`, middle column): the
model's cut face is plain in the middle and has a rim of surface colours two to four cells wide; the needle and
the small buds are blue, green and orange all over, where the picture has them cream. At offset 2 the rim is about
six cells wide.

**Cause** (reasoned from the code, and the fix confirms it): a point of the cut face lies on an upright grid edge
between the last slice inside the model and the slice above. v8 blended the colours of the two ends by the
point's place. An end holds the cut face's colour only when its own estimate is at or below zero. In the band by
which the model is fatter than the solid, and over every part thinner than a cell, both ends read above zero and
hold a colour of the surface.

**What `meshPoint` does now** for colours (positions are untouched):
1. A point of a cut face takes the colour of a sample that holds the face's colour (`meshFaceFrom`): the inside
   end of its edge, else the outside end, else the nearest such sample in the two slices within `g.reach` cells
   (2 plus the offset, at most 8), else the colour the face had at the point before (`g.faceCol`). A point is of
   the cut plane's face when its edge stands upright, its outside end lies above the face, and either the cut
   plane is reached before the solid's own surface (a straight line through the two ends' own distances, kept
   by `meshTrue` as `own`) or the point sits within half a cell under the face (`MESH_FACE_NEAR`). A point whose
   outside end is a sample on the wall of the grid is of a cut face too.
2. A surface point whose inside end holds the cut face's colour takes the outside end's colour alone
   (`MESH_FACE_RULE2`). Before, the top rows of the wall under a cut face were paled by the face's cream.
Which samples hold the face's colour is the sampler's rule, repeated in three numbers (`MESH_FACE_BELOW`,
`MESH_FACE_ABOVE`, `MESH_FACE_DEEP` for `RAW_CUT`, `RAW_ABOVE`, `RAW_IN` of `30-shaders.js`).

**Measured on the final build** (`out/r9/mesh/cmp-cutface-final.txt`, `cmp-standard-final.txt`; the measure is in
`cmp.py`: of the pixels where the picture shows its plain cut face and the model is drawn, the share where the
model is plain too):

| Scene | v8 | round 9 |
|---|---|---|
| Opening Mandelbrot cut at z = 0, seen from above, 128 cells (`cutm-128`) | 0.917 | 0.977 |
| the same at 256 cells | 0.940 | 0.968 |
| the same, offset 2 | 0.784 | 0.982 |
| the same, offset 0 | 0.987 | 0.947 |
| Basilica cut (`cutj-128`) | 0.918 | 0.952 |
| Douady rabbit cut (`cutr-128`) | 0.915 | 0.973 |
| The tester's standard cut job (`cut-128`) | 0.906 | 0.965 |

The STL files of all these jobs are the same byte for byte as v8's, so no shape changed. Median hue difference of
the standard cut job 7.1 to 6.3 degrees, share within 30 degrees 83 to 85 %. With the cut face painted ("Colour
the cut face like the inside of the 2D view", How deep inside; `cutp-128`) the rim now has the face's own colours
(pink, as in the picture) where v8 had trap colours: 12.6 to 11.1 degrees, 63 to 67 % within 30.

**Not as good as v8 in one case, and not traced:** at offset 0 the share fell from 0.987 to 0.947. Seen
(`sheet-cut-close.png`, lower row): v8's face ran pale to the edge, mine has a thin line of surface colours round
it and a coloured needle, which is close to the thin coloured outline the picture has, but the needle should be
cream. Reasoned, not tried: these are either wall points that now hold the full surface colour (rule 2), or rim
points more than half a cell under the face; `MESH_FACE_NEAR = 1` would settle the second.

**Sheets:** `out/r9/mesh/sheet-cut-a.png` (picture, v8, round 9 for the Mandelbrot solid at 128, 256, offset 0
and offset 2), `sheet-cut-b.png` (Basilica, rabbit, painted face), `sheet-cut-close.png` (the needle, three
times enlarged).

## Item 2, the first model of a formula: the panel says why it waits

**Seen on v8** (`out/r9/mesh/v8/log-first.txt`, GPU shared with others): the progress line reads "Starting. 0%."
for 6.2 s (opening Mandelbrot), 2.1 s (Kleinian) and 5.9 s (power -2), then the job runs for 2 to 3 s. A second
model of the same formula starts at once.

**Done:** `meshPrepare(job)` runs before the first sample. While the renderer answers that the program for
volume samples is still being prepared (`snapProg(job.snap, true) === 'wait'`), the progress line reads
"Preparing to read this solid. The first model of each formula takes a few seconds longer. The next one starts
at once." and from two seconds on adds "4 seconds so far." No percentage is shown with it (`job.plain`). Cancel
works during the wait (it goes through `job.turn`).

**Measured** (`out/r9/mesh/r9-mesh/log-first.txt`): the sentence is shown from 0.04 s to 4.6 s (Mandelbrot),
0.16 to 2.5 s (Kleinian), 0.20 to 4.5 s (power -2); the second job of each shows "Finding the solid" at once.
The wait itself is as long as before (whole jobs 6.4, 4.6, 7.0 s against 9.0, 4.0, 7.7 s on v8, within what the
shared GPU does). That run was made on the build before items 3 and the last step of item 1; the code of this
item did not change afterwards (reasoned), and the smoke test's model job ran on the final build.

## Item 3, mesh-2, the negative power: no setting gives a model true to the picture; the warning now says what helps

**Seen on v8:** power -2 at 128 cells with the opening settings gives a spine with one arc
(`out/r9/mesh/sheet-negpow-v8.png`, second tile). The picture is the first tile.

**Measured on v8** (`out/r9/mesh/v8/check-neg.txt`, PLY only, `python out/r9/mesh/drive.py v8 special:neg`; the
tester's measure: outline overlap; share of the picture's outline missing from the model; share of the model
outside the picture's outline, as a share of the picture):

| Cells | Offset | Every piece | Largest piece only |
|---|---|---|---|
| 128 | 0.5 | 0.567; 5.0 %; 68 % | 0.256; 70.5 %; 15 % |
| 128 | 1 | 0.472; 0.9 %; 110 % | 0.440; 18.7 %; 85 % |
| 128 | 1.5 | 0.444; 0.8 %; 123 % | 0.426; 16.3 %; 96 % |
| 256 | 0.5 | 0.641; 7.0 %; 45 % | 0.157; 82.1 %; 14 % |
| 256 | 1 | 0.529; 0.9 %; 87 % | 0.292; 60.6 %; 35 % |
| 256 | 1.5 | 0.480; 0.8 %; 107 % | 0.359; 43.9 %; 57 % |
| 512 | 1 | 0.628; 1.2 %; 57 % | 0.253; 70.1 %; 19 % |
| 512 | 1.5 | 0.545; 0.8 %; 82 % | 0.267; 66.7 %; 25 % |

(512 cells at offset 0.5 was not run again; round 7 had 0.64 with every piece.) Pieces: 1,492 at 128, 5,870 at
256, 16,395 to 17,141 at 512. The largest job, 512 cells at 1.5 with every piece: 4.8 million triangles, 93 MB of
PLY, 13.5 s.

**What the pictures say** (`sheet-negpow-v8.png`, looked at as a user would): no model is the picture. The best
overlap is 0.64. With every piece kept, the picture's own shapes are there from 256 cells on (the stack of discs
on the spine, the ball, the wings), most clearly at 512 with offset 1, but always inside complete outer shells
that the picture shows only as thin arcs at the bottom, so the model looks like a striped balloon with the
picture's objects inside. A larger offset does not bring the model closer: it joins pieces and covers the
picture's outline (missing share under 1 %), but the shells grow into thick bands and the overlap falls at every
resolution. The largest piece alone is a spine with one or two loops at every setting; at 128 with offset 1 or
1.5 it is a thick balloon without the inside.

**So no button and no new starting value.** The warning of `#meshWarn` for a solid that comes out as 200 pieces
or more now says what does help, in one paragraph in place of two (measured on the final build,
`out/r9/mesh/r9-mesh/log-warn.txt`):
- largest piece kept: `This solid has parts thinner than one cell of the grid. They came out as 1,492 loose
  pieces, and only the largest was kept: about 27% of the surface. So this model does not look like the picture.
  To get closer, untick "Keep only the largest piece" and choose 256 or 512 cells, then start again. A larger
  surface offset joins more of the pieces, but it makes the thin parts thick.`
- every piece kept: `... so the model is rougher than the picture and can look unlike it. 256 or 512 cells follow
  the picture more closely. A larger surface offset joins more of the pieces, but it makes the thin parts thick.`
  (at 256 cells: "512 cells follow ..."; at 512 that sentence is left out).
The warning of a solid made of a few separate parts (mosaic: `Only the largest piece was kept: about 6% of the
surface. ...`) is as it was. Nothing an ordinary solid gets has changed: offset, pieces and resolution start as
before.

Not shown by a number: that 512 cells follow the picture more closely than 256 at offset 0.5 (overlap 0.64 both;
at offset 1 it is 0.53 against 0.63). The sentence rests on the pictures.

## Item 4, the tester's seven standard jobs, before and after

`out/r9/mesh/cmp-standard-final.txt` (v8: `out/r9/mesh/v8/check-standard.txt`; final build:
`out/r9/mesh/r9-mesh/check-standard.txt`). All measured.

| Job | Shape, both pages (triangles; overlap; picture only; model only) | Hue, v8 | Hue, round 9 | Files |
|---|---|---|---|---|
| mandel-128 | 30,032; 0.950; 2.9 %; 2.3 % | 3.3 deg, 97 % | 3.3 deg, 97 % | STL and PLY identical |
| rabbit-128 | 39,252; 0.967; 1.5 %; 1.8 % | 2.8, 96 % | 2.8, 96 % | identical |
| julia1-128 | 24,840; 0.956; 1.7 %; 2.8 % | 7.3, 91 % | 7.3, 91 % | identical |
| julia1-256 | 100,664; 0.972; 2.8 %; 0.1 % | 4.7, 98 % | 4.7, 98 % | STL identical; 2 of 50,334 points changed colour, by at most 20 of 255 (rule 2) |
| cut-128 | 25,404; 0.945; 2.9 %; 2.7 % | 7.1, 83 % | 6.3, 85 % | STL identical; colours of the cut face changed (item 1) |
| klein-128 | 95,832; 0.960; 1.7 %; 2.4 % | 3.5, 91 % | 3.5, 91 % | identical |
| trapsolid-128 | 39,892; 0.965; 0.9 %; 2.7 % | 7.5, 86 % | 7.5, 86 % | identical |

Every file is closed and oriented, volumes and sizes equal on both pages. No console errors in any run.

## The final build, checked (all measured)

- `dist/r9-mesh.html`, md5 `61e2a46f05e9b3a864e4a6bd961b03ef`, built 06:10 (`out/r9/mesh/final-build.md5`). The
  cut solids, the warnings, the seven standard jobs, the smoke test and the built-in fields were all run on it.
- Smoke test: `tools/smoke.json`, 52 steps, exit 0, no console errors, the model job delivered its zip
  (`out/r9/mesh/smoke-final.log`, finished 06:16). It also passed on the build before
  (`out/r9/mesh/smoke-1.log`).
- Built-in fields through the panel (round 7's `fields.py`, copied to `out/r9/mesh/`): sphere, torus, gyroid,
  pearl and noise, ten runs, give the same triangles, points, pieces, Euler number and volume as in round 7
  (`out/r9/mesh/fields-r9-mesh.txt` against `out/r7/mesh/fields-r7-mesh.txt`), no console errors.
- The progress line of item 2 was measured on the build of 06:03 (`r9-mesh/log-first.txt`), not again on the
  final one.

## Names added or changed (all in `src/js/46-mesh.js`)

- `MESH_FACE_BELOW` (1.01), `MESH_FACE_ABOVE` (3.01), `MESH_FACE_DEEP` (1.5): where a sample holds the cut face's
  colour; they repeat `RAW_CUT`, `RAW_ABOVE`, `RAW_IN` of `30-shaders.js`.
- `MESH_FACE_NEAR` (0.5): a point this close under the cut plane's face, in cells, is coloured as part of it.
- `MESH_FACE_RULE2` (true): a surface point whose inside end holds the cut face's colour takes the outside end's.
- `MESH_WORDS.prepare`: the sentence of the progress line while the first model of a formula is prepared.
- `meshTrue` returns `own` as well: the distances before the picture's limits are applied.
- `meshSlice(g, d, c, end, f, own, zc)`: two new arguments. A slice now has `.own`, `.zc` (height above the cut
  plane, minus infinity without a cut), `.wall` (samples put outside by the wall of the grid), `.face` (every
  inside sample of this slice holds the cut face's colour).
- `meshHoldsFace(g, s, q)`, `meshFaceFrom(g, si, qi, so, qo)`: see item 1.
- `g.reach`, `g.faceCol` in `meshBuild`'s grid: how far `meshFaceFrom` looks; the last face colour found.
- `meshPrepare(job)`, `job.plain`; `meshPaint` shows the step alone while `job.plain` is set.
- `meshRun`: locals `fine`, `more`; the texts of `#meshWarn` for 200 pieces and more.
- No id, label, file name, state field, uniform or program key was added or changed. No CSS.

## For the others

- **Closing text, `src/body.html`** ("How do I get a picture or a 3D model out?"). Nothing in it is untrue now;
  three sentences can say more:
  1. "The first model of a formula takes a few seconds longer while it is prepared." Suggested: "The first model
     of a formula takes a few seconds longer while it is prepared, and the progress line says so for as long as
     it lasts."
  2. "One kind of solid does not come out like its picture yet: one made of sheets thinner than a cell of the
     grid, such as a negative power. The panel says so when it happens." Suggested: "... The panel says so when it
     happens, and what brings the model closer: untick Keep only the largest piece and choose 256 or 512 cells.
     Even then the model shows outer shells that the picture draws only in part."
  3. After "Its colours are read from the surface the same way the picture's are; ...": "A solid that is cut open
     gets the colour of the cut face there, right up to its edge."
- **Engine, `30-shaders.js`:** if `RAW_CUT`, `RAW_ABOVE` or `RAW_IN` change, `MESH_FACE_BELOW`, `MESH_FACE_ABOVE`
  and `MESH_FACE_DEEP` in `46-mesh.js` must follow, or the model's cut face gets surface colours again.
- **Engine, `40-render.js`:** `meshPrepare` asks `snapProg(snap, true)` and reads the answer `'wait'`. If the name
  or the answer changes, the job still runs but the sentence is not shown (it is guarded by `typeof`).
- **Engine, mesh-2:** round 7's request stands. A model true to the picture of a sheet solid needs the sampled
  estimate to carry the picture's own skin; no setting of the mesher gives it (table above).
- **Engine, the painted cut face:** in the middle of the face the model's "How deep inside" colours differ from
  the picture's (11 degrees median, 67 % within 30; `sheet-cut-b.png`, last row). That is the sample's colour, not
  the mesh.

## Risks, and what was not done

- Offset 0 on a cut solid: a thin coloured line round the face where v8 was pale (see item 1).
- A surface that passes within half a cell under the cut plane without being cut is coloured as the face
  (reasoned; a ring up to about one cell wide on a dome cut near its top).
- Offsets above 3 cells (Extreme ranges): the slices at the model's face are no longer ones in which every
  inside sample holds the face's colour, so the face is coloured from deep samples, the nearest one, or the last
  face colour. Not run.
- A solid that runs into the wall of the grid, and a solid cut by the drawing radius: the first follows the new
  rule but no scene of mine does that; the second is as it was.
- Not run: 192, 384 and 512 cells for the standard jobs; the Kleinian view and a trap solid cut open; a model
  made from the 2D view; files opened in Blender, Rhino or a slicer.
- The wait for the first model is as long as before; only the words are new.
