# Fix pass 7, mesh: "Save a 3D model"

Files changed: `src/js/46-mesh.js` only (`src/css/46-mesh.css` untouched). Page: `dist/r7-mesh.html`
(`python build.py --name r7-mesh --base base6 --use src/js/00-core.js src/js/46-mesh.js src/css/46-mesh.css`).
Everything I ran is under `out/r7/mesh/`: `v6/` holds the testers' reproductions run on `dist/v6.html`, `new/` the
same on my page (copies of the mesh tester's `drive.py`, `check.py`, `special.py`, `declined.py`, pointed at the
page by folder name; my extra runs are in `mine.py`, called as `python out/r7/mesh/new/drive.py x special:<name>`).
Started 03:25, last measurement 04:10 (the smoke test on the final build: exit 0, no console errors).
One caution on the evidence: the two last text edits (readme wording "about 0.5 cells", brackets round the
mosaic's cell width) were made after the measurement runs; only the smoke test was run again after them.

## What was wrong, measured (mesh-4)

`out/r7/mesh/profile2-v6.txt`: the raw estimate along a line straight up through the top of the Douady rabbit.
Just outside the surface it rises by 0.49 per unit of distance, one 128-cell further out by 0.25, and from three
cells on by 0.19, for a long way. Sideways off the rim it rises by 0.5 to 0.6 (`profile-v6.txt`). Inside the solid
it falls steeply and then jumps to a large negative number. So the estimate reads short by 2 at the surface and by 5
a few cells above a flat face, and v6 compared the level `offset * cell` with that number. Reproduced on v6
(`v6/log-base.txt`, `v6/check-base.txt`; rabbit at 128): offset 0.5 moved the rim by 0.85 cells and the top by 1.37,
offset 2 by 2.9 to 3.1 and by 9.1 (lab units from `checks/*.json`, `lab_bbox_*`).

## What the mesher does now

1. `meshTrue(g, lo, mid, hi)` turns each slice's estimates into distances before marching: every estimate
   outside the solid and within the level plus one cell is divided by its own slope, measured against its six
   neighbours (the slice below and above included, so `meshBuild` now reads one slice ahead and holds three raw
   slices). Along each axis the steeper of the two sides counts. A slope above one is left alone (the estimate is
   never made shorter: on a true distance, and beside the deep inside of a solid, nothing changes) and no estimate
   is made more than four times longer (`MESH_SLOPE_MIN`).
2. Samples inside the solid keep their estimate; `meshPoint` multiplies an inside end by the factor of the outside
   end, so the two ends are on one scale and **offset 0 gives exactly the v6 surface** (same triangle count, same
   size: rabbit 37,264 triangles, 100 x 84.2 x 37.3 mm on both pages).
3. Thin parts: a true half cell does not catch a spike that runs between the samples (the nearest sample can be
   0.71 of a cell away), and the first version of this fix broke the Mandelbrot set's needle at 128 cells (model
   100 x 99.1 mm instead of 100 x 91). So a sample that is a "pit" (`meshPit`: lowest along some axis, both
   neighbours outside and clearly higher) keeps its plain estimate. That is the sample beside a part thinner than
   a cell, and the plain estimate's short reading is the margin that keeps such parts whole, as in v6.
4. The starting offset stays 0.5: measured, it is where the 128-cell model and the picture agree best.
5. A mesh point's colour is now taken between the two ends of its grid edge by its place on the edge
   (`meshPoint`, `w = s`), always, as FIX7 asks. Nothing else about colour is mine.

## Numbers on my page (default offset 0.5, real pictures, `new/check-final.txt`, `new/pics/cmp-*.png`)

Outline against the picture (overlap; share of the picture outside the model; share of the model outside the picture):

| Picture | v6 at 128 (tester) | new at 128 | new at 512 |
|---|---|---|---|
| Opening Mandelbrot | 0.883; 2.5%; 10.4% | 0.949; 2.9%; 2.3% | 0.927; 7.3%; 0% |
| Douady rabbit | 0.889; 1.4%; 10.9% | 0.967; 1.5%; 1.8% | 0.949; 5.1%; 0% |
| Julia c = -1 | 0.855; 1.7%; 14.9% | 0.956; 1.7%; 2.8% | 0.955; 4.5%; 0% |
| Cut at z = 0 | 0.889; 2.6%; 9.6% | 0.945; 2.9%; 2.7% | not run |
| Kleinian | 0.961 | 0.961 | not run |
| Trap is the solid | 0.957 | 0.965 | not run |

Thickness and volume, 128 against 512: Mandelbrot 25.4 mm and 35.0 cm3 against 24.7 and 32.1 (v6: 27.3 and 42.7
against 24.9 and 33.2); rabbit 37.7 mm, 52.3 cm3 against 37.2, 49.2 (v6: 39.2, 61.5 against 37.4, 50.6); Julia
c = -1 33.3 mm, 26.6 cm3 against 32.8, 24.7 (v6: 35.2, 32.3 against 33.1, 25.6).

Rabbit at 128, how far each side moved for the asked offset, in cells (`new/checks/ev-rabbit-128-off*.json`,
`new/check-ev.txt`): offset 0.5 gives x 0.59, y 0.86, z 0.43; offset 2 gives x 2.38, y 2.30, z 1.59 (v6: 0.85, 0.86,
1.37 and 3.1, 2.9, 9.1). Height of the model 37.3, 37.7, 38.6 mm at offsets 0, 0.5, 2 (v6: 37.3, 39.2, 51.8);
volume 49.5, 52.3, 61.0 cm3 (v6: 49.5, 61.5, 126.2). So the offset is now the same within about a quarter on a
resolved face, not within a factor of four. It is not exact: y at 0.5 is 0.86 because the rabbit's tips there are
thinner than a cell and are kept by the "pit" rule, and 2 asked gives 1.6 on the flat top because one cell does
not resolve how the estimate bends. The hint and the readme now say "about".

Built-in fields (`fields-r7-mesh.txt`, run with `python out/r7/mesh/fields.py r7-mesh`): all closed and
oriented; sphere at offset 0, 0.5 and 2: points within 0.002 cells rms (0.016 worst) of the asked radius, volume
error -0.02 to -0.03%; torus -0.09%; pearl as in round 4. A true distance is left exactly as it was.

## mesh-2, the negative power: not cured, and why

Reproduced on v6 (`v6/pics/cmp-negpow-128-def.png`): a heart-shaped band with a spine. Then the question FIX7 asks:

- **Offset 0** (`v6/pics/cmp-negpow-512-off0-all.png`, all pieces, 512 cells): the right shapes in the right places
  (leaves on the spine, the wing arcs, the ball), but as 3,462 fragments; the largest piece is a 12.5 mm sliver.
  At 128: 276 fragments, the largest 644 triangles. So the sign of the estimate is right, and the solid is made
  of sheets thinner than a cell of any grid on offer.
- **Why the picture shows them with body:** the picture draws its surface where the estimate reads 0.8 of a
  pixel (`LEVEL` in `30-shaders.js`), not where it reads zero. On an ordinary solid that skin is about a third of a
  128-cell and nobody sees it. On this solid the skin is the whole visible thickness of every leaf. The model
  has no such skin, so no setting of the mesher alone makes the two alike.
- **True half-cell offset, every piece kept, 512 cells** (`new/pics/cmp-negpow-512-off0.5-all.png`): looks like the
  picture (overlap 0.64; leaves, arcs, spine, ball all there), plus the complete outer loops, of which the picture
  draws only the lower part. 1.67 million triangles in 17,483 pieces, 184 MB.
- At 128 cells with every piece (`new/pics/cmp-negpow-128-off0.5-all.png`): a coarse block version, overlap 0.58.
  With "Keep only the largest piece" (the default): one fragment, about a quarter of the surface.

What the panel does now: two plain sentences in `#meshWarn` when this happens (see mesh-3 and "names"), instead of
handing the piece over without a word. For the shader engineer or whoever joins: see needs_from_others in my
report (make the sampled estimate carry the picture's own skin, or tell the mesher its size).

## The small ones

- **mesh-3:** `meshRun` counts the triangles before `meshPieces` and measures how far all pieces reach
  (`meshExtent`). When the kept piece holds under 80% of the surface *and* is clearly shorter than all the pieces
  together along some axis, `#meshWarn` says: `Only the largest piece was kept: about 6% of the surface. Untick
  "Keep only the largest piece" and start again to get all 74 pieces.`, and the Pieces row and the readme's Pieces
  line carry the share. The second condition is there because a hollow solid (the trap solid: the largest of
  100 pieces with 36% of the triangles) loses only inner layers nobody sees; warning there would be wrong.
  From 200 pieces on a second sentence says the solid is finer than the grid. The tick box's hint no longer says
  "crumbs".
- **mesh-5:** `meshSave` clears `saving` in a `finally`, shows a sentence whatever happens, and says "so you can
  try again" unless `saveFile` answered `again: false`.
- **mesh-6:** `meshWhat` adds the trap when it is or is added to the solid (shape, radius, centre, thickness,
  skipped steps), ticked modifiers, the mosaic's cell width, and for the Kleinian view the turning-out sphere and
  the depth of search. File names are unchanged.
- **walk-1:** `meshStart` listens for `webglcontextlost` on `#view` while a job runs and asks the canvas itself
  (`meshGraphicsLost`); a job that ends that way says `The graphics of this page were interrupted, so the model
  could not be finished. Start it again.`

## Names added or changed (all in `src/js/46-mesh.js`)

- `MESH_SLOPE_MIN` (0.25), `MESH_KEPT_SHARE` (0.8), `MESH_MANY_PIECES` (200), `MESH_TRAPS` (words for the trap shapes,
  indexed like `TRAP` in `25-colour.js`), `MESH_WORDS.lost`.
- `meshTrue(g, lo, mid, hi)` -> `{ d, f }`; `meshPit(v, p, q)`; `meshExtent(g)`; `meshShare(f)`;
  `meshGraphicsLost(canvas)`.
- `meshField(job, raw, cx, cy, side, z, n, T)`: new last argument. `meshSlice(g, d, c, end, f)`: new last argument,
  and a slice now has `.f`.
- `info.cell` (mm per cell), `info.kept`, `info.part` in `meshRun`; `job.lost`.
- Text changed: hints of `#meshOffset` and `#meshLargest`; the Pieces row can read `The largest of 74, with about 6%
  of the surface`; readme lines "Made from", "Grid", "Pieces"; `#meshWarn` can hold up to three sentences.
- No id, label or file name changed.

## For the person joining the files

- `meshWhat` reads `S.colour.solid`, `.trap`, `.axis`, `.ray`, `.radius`, `.tx/.ty/.tz`, `.thick`, `.skip` and writes
  the skipped steps as the dial shows them. If the colour engineer changes what `skip` means in Mandelbrot mode,
  the readme simply repeats the dial; nothing to adjust unless the keys are renamed (a missing key is left out).
- When the samples' colours are right (mesh-1, shader side), the model's follow: the blend is by position now.
- The smoke test (`tools/smoke-v6.json`) passes on `dist/r7-mesh.html`, exit 0, no console errors
  (`out/r7/mesh/smoke.txt`).

## Not done, not checked

- mesh-2 as above.
- 192, 256 and 384 cells were not run. Only the Douady rabbit was profiled; the other pictures were judged by
  their outlines. Offsets above 2 and the extreme range were not run.
- The "pit" rule makes a few loose crumbs where a solid has specks thinner than a cell (opening Mandelbrot: the
  largest of 21 pieces at 128 and of 77 at 512, with more than 99% of the surface). They are dropped while the tick
  box is on, and saved as loose pieces when it is off.
- Self-intersections were not looked for; the files were not opened in Blender, Rhino or a slicer.
