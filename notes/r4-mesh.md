# Round 4, mesh: "Save a 3D model" (N6)

Files: `src/js/46-mesh.js`, `src/css/46-mesh.css`. Scripts, stand-ins, logs and screenshots: `out/r4/mesh/`.

## State when I stopped

- Everything under "### mesh" in `docs/SPEC4.md` is built and passes on the built-in fields, against `base2` and
  against `base3`, with no console errors.
- **The real `src/js/45-export.js` had not arrived**, so the model export has NOT been run against the real
  `takeSnapshot` / `sampleSlice`. To see the mesher on real distance fields anyway, I wrote a private stand-in of
  that interface (`out/r4/mesh/45-export.js`, 25 lines, plus `out/r4/mesh/30-shaders.js` = base3's shaders with the
  `uRaw` branch of CONTRACT4 added). Through that stand-in the Julia set for c = -1, the default Mandelbrot and
  the default Kleinian all export, unpack and parse back closed (numbers below). The stand-in does not freeze
  anything and reads pixels in one go, so it says nothing about the real module's snapshot or its pacing.

## What the user gets

A section "Save a 3D model" (the page engineer adds the `<details id="secMesh">` and calls
`buildMeshPanel('meshPanel')`). Controls, group `mesh`: resolution (96, 128, 192, 256, 384, 512; starts at 128),
surface offset in grid cells (0 to 2, starts at 0.5), longest side in mm (100), keep only the largest piece
(on), and three ticks for STL, OBJ and PLY (all on). "Start the model" becomes a progress bar with the step in
words, a percentage, the time left and "Cancel". When done: triangles, points, size in mm, pieces, the size of each
file and of the zip, a warning above two million triangles, "Save the file" and "Discard". Messages are plain
sentences in a `role="status"` line. Keyboard focus follows the button that replaces the one just pressed.

The zip holds `<kind>-<cells>.stl / .obj / .ply` and `readme.txt` (what the picture was, size, triangle count,
volume, how to import into Blender and Rhino, a line on printing). Zip name: `squaring-lab-<kind>-<cells>.zip`.

Decisions worth knowing:
- The model is the picture: the drawing radius clips it (`max(d, |p| - bound)`) and, when the solid is cut
  open, so does the cut plane (`max(d, z - cut)`). The readme says when a cut is part of the model.
- Coordinates are millimetres, the model stands on z = 0, centred on the z-axis. STL and PLY are z-up. The OBJ
  is written y-up, (x, z, -y), because Blender and Rhino turn OBJ files on import; all three then stand alike.
- Colours in OBJ and PLY are display values (the linear surface colour to the power 1/2.2), as those formats expect.
- A point's colour comes from the outside end of its grid edge when the other end is inside the solid (on
  screen the colour is always read just outside), otherwise the two ends are blended.
- Limits: 15 million triangles or about 1.4 GB of files stop the job with a plain message.

## How it works

1. `meshLocate`: three coarse passes (24, 32, 48 slices across the box, twice as fine within a slice) inside the
   cube of the drawing radius, and up to three more of 48 while the box still halves (a very large radius). Samples whose estimate is within twice their reach mark where the
   solid may be; the box of those samples is the next pass's box. About 100 small `sampleSlice` calls.
2. `meshBuild`: a grid with N cells along the longest side of that box (plus 2 + offset cells of margin), read one
   slice at a time; `meshMarch` runs marching cubes between the two slices held. Points are shared through five
   edge maps (x and y edges of each slice, uprights between them). Samples on the outer wall count as outside, so
   the mesh is closed even when the solid runs into the wall.
3. `meshPoint` places a point on its grid edge: in proportion to the two estimates (each trusted for at most one
   cell); where the inside end holds exactly 0 (the big Kleinian pearls) from the outside end alone. Points never
   sit on a sample (2% clamp), so no triangle is without area and an STL welded by position stays closed.
4. `meshPieces` (union-find on the finished index list), `meshMeasure`, the three writers, `meshZip`.
   Every loop that can be long hands the thread back about every 12 ms (`job.turn`); a slice pair is one turn.

Marching-cubes tables: `MESH_EDGE_TABLE` is the standard 256-entry edge table. `MESH_TRI_TABLE` was not typed
from memory: `out/r4/mesh/gen_tables.py` works each case out from the cube (same corner and edge numbering and
the same face rule as the standard table: on a face with two inside corners on a diagonal, each is cut off on
its own) and checks every case. A first version filled loops with a simple fan and FAILED the closed test on
noise: a fan line can lie in a cube face, and the neighbour can draw the same line, which puts four triangles on
one edge. The fill now forbids lines between two points of one face. Checks passed: 256 cases use exactly their
crossing edges; noise fields meet all 256 cases and are closed; sphere volume positive.

## Numbers (built-in fields, base3 build; `out/r4/mesh/fields-base3.log`)

| Field | Cells | Triangles | Points | Closed | Euler | Volume error | Point fit (cells, rms / worst) | Time |
|---|---|---|---|---|---|---|---|---|
| sphere, offset 0 | 96 | 68,648 | 34,326 | yes | 2 | -0.033 % | 0.0016 / 0.013 | 0.2 s |
| sphere, defaults (offset 0.5) | 128 | 123,340 | 61,672 | yes | 2 | -0.019 % | 0.002 / 0.018 | 0.25 s |
| torus | 128 | 73,552 | 36,776 | yes | 0 | -0.089 % | 0.0027 / 0.014 | 0.16 s |
| gyroid wall, every piece | 96 | 161,152 | 80,634 | yes | 58 (61 pieces) | | | 0.4 s |
| gyroid wall, largest of 121 | 192 | 689,200 | 344,526 | yes | -74 | | | 1.6 s |
| pearl (0 inside, reads 1.6x long), offset 0 | 96 | 74,168 | 37,086 | yes | 2 | -0.43 % | 0.11 / 0.35 | 0.2 s |
| pearl, offset 0.5 | 96 | 70,656 | 35,330 | yes | 2 | -0.35 % | 0.08 / 0.35 | 0.1 s |
| noise, every piece | 40 | 52,184 | 24,102 | yes | | | | 0.1 s |
| noise, largest of 384 | 56 | 166,132 | 76,352 | yes | | | | 0.2 s |
| sphere cut at z = 0.3 | 96 | 57,208 | 28,606 | yes | 2 | -0.045 % (against the cut ball) | | 0.1 s |
| torus clipped by drawing radius 0.8 | 96 | 47,008 | 23,504 | yes | 0 | | | 0.1 s |
| sphere, offset 0, drawing radius 300 | 96 | 69,128 | 34,566 | yes | 2 | -0.034 % | | 0.3 s |

"Closed" means: every edge is used by exactly two triangles, once each way; no point unused; smallest triangle
area 0.000346 cells squared (the clamp), never zero. Sensible point count: points = triangles / 2 + Euler.
Longest pause of the page's own timers while a job ran: 28 to 40 ms. Cancel took 11 ms. A 384-cell gyroid
(2.9 million triangles, 318 MB zip) built, warned and was saved through the hook.

Zips read back with python's `zipfile` (CRC of every entry correct, all stored): sphere 128 (STL, OBJ, PLY),
gyroid 192 (75 MB), noise 56. STL re-welded by position: closed, one piece, normals agree with the corners,
longest side 100.000 mm, lowest z 0, centre 0. OBJ and PLY: same triangles, positions within 0.00005 mm of each
other, colours within 0.13 of 255. `zipStore` on its own (a string with accents, bytes, an empty file): correct.

## Numbers through the private stand-in of the sampling interface (`out/r4/mesh/real-standin.log`)

| Picture (base3 defaults) | Cells | Triangles | Pieces | Closed (mesh and STL read back) | Size mm | Time |
|---|---|---|---|---|---|---|
| Julia set, c = -1 | 128 | 27,232 | 1 | yes | 100 x 48.9 x 49.3 | 0.5 s |
| Mandelbrot, default | 128 | 86,360 | largest of 156 | yes | 100 x 91.1 x 90.9 | 0.6 s |
| Kleinian, default | 128 | 93,224 | 1 | yes | 99.0 x 100 x 51.3 | 0.5 s |

Pictures: `real-julia-picture.png` (the page) beside `real-julia-mesh.png` (the mesh itself, drawn by the test's
own little rasteriser in `draw.js`), the same for `klein` and `mandel`. The meshes show the same objects with
their colours; the big Kleinian pearls come out smooth.

## A bug the tests caught

"Keep only the largest piece" first renumbered points in the order triangles used them while moving them in
place, which overwrote points still to be moved. The index-level checks passed; the STL read back (welded by
position) was not closed. Points now keep their order when the gaps are closed.

## For the other engineers

- render-export: the job calls `sampleSlice` one call at a time, with `N` anything from 8 to 513 (N is cells + 1
  for the model, so 97, 129, 193, 257, 385, 513, and smaller odd sizes during the search), a different `side`
  and centre per phase, and about 100 small calls before the big ones. `takeSnapshot()` is called inside the
  click, `releaseSnapshot` in a `finally`. A `null` from `sampleSlice` ends the job with "The picture could not
  be read just now...".
- page: the panel gives its host the class `mesh-panel` and lays itself out; it brings its own "Reset this
  section" button. Ids: `meshStart`, `meshCancel`, `meshSave`, `meshDiscard`, `meshCells`, `meshOffset`,
  `meshMm`, `meshLargest`, `meshStl`, `meshObj`, `meshPly`, `meshBar`, `meshStep`, `meshFacts`, `meshWarn`,
  `meshMsg`. For the 48-cell smoke job: `window.squaringLabMeshTest = { cells: 48 }` before clicking
  `#meshStart`, wait for `!squaringLab.meshBusy()`, click `#meshSave`.
- Test hook: `window.squaringLabMeshTest = { field?: 'sphere' | 'torus' | 'gyroid' | 'pearl' | 'noise', cells? }`;
  the finished mesh is left in its `.mesh`.

## Open issues

- Not run against the real `45-export.js` (see the top).
- The box found by the search is 5 to 8 percent loose on each side, so the solid spans about 85 to 90 percent of
  the chosen cell count. The saved size is exact all the same (the longest side is measured on the mesh).
- Vertex placement on a field that is 0 inside and reads long outside is good to about a third of a cell (the
  pearl rows above). Real pearls looked smooth in the picture.
- Only the largest piece is judged by triangle count. A solid made of two equal halves loses one; the user can
  untick the box.
- The host's size limit for `saveFile` is unknown. A refused save shows the core's sentence and keeps the model.
- The import notes in readme.txt (Blender's Scale 0.001, the Attribute colour setting, Rhino's "Map OBJ Y to
  Rhino Z") are written from knowledge of those programs, not checked in them here.

## Running the tests again

```
python out/r4/mesh/gen_tables.py                               # the tables and their checks
python out/r4/mesh/run_tests.py fields --base base3            # built-in fields, zips read back
python out/r4/mesh/run_tests.py real --base base3 --use src/js/45-export.js src/css/45-export.css src/js/40-render.js src/css/40-render.css
python out/r4/mesh/run_tests.py real --base base3 js/30-shaders.js=out/r4/mesh/30-shaders.js js/45-export.js=out/r4/mesh/45-export.js   # the stand-ins
```
