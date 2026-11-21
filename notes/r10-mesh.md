# Round 10, mesh: "Save a 3D model" (`src/js/46-mesh.js`)

Started 06:28, last source change 07:17 (back to the build of 07:01), stop 07:23. File changed: `src/js/46-mesh.js`
only (`src/css/46-mesh.css` untouched). Page: `dist/r10-mesh.html`, md5 `daaee3d588dfff1bd77547cae6963f8f`
(`python build.py --name r10-mesh --base base9m --use src/js/46-mesh.js src/css/46-mesh.css`), compared with
`dist/v9m.html`. Everything is under `out/r10/mesh/`: `v9m/` holds the runs on `dist/v9m.html` (made 06:32 to 06:38,
before any source change), `r10-mesh-c/` the runs on the final build (`dist/r10-mesh-c.html` is the same file byte
for byte). `r10-mesh-a/` and `r10-mesh-d/` are two versions I tried and dropped. `run.sh <page> <group>` draws a
group again (drive.py and check.py are the mesh tester's; groups in `mine.py`: standard, ex, warn, cut0, add, big).
`46-mesh.before.js` is the file as it was.

Every claim says whether it was **measured** or **reasoned**.

## What must not change, and did not (measured)

The tester's seven standard jobs on v9m and on the final build (`out/r10/mesh/r10-mesh-c/check-standard.txt`,
first copy of `cmp-standard.txt` printed at 07:06): mandel-128, rabbit-128, julia1-128, julia1-256, cut-128 and
klein-128 give the same STL and PLY files byte for byte. The three cut jobs (`cmp-cut0.txt`) too. Only a solid made
by a trap takes the new path, so trapsolid-128 changed: see below.

## t9-mesh-1, fins on "Sea urchins": the fins are gone, the model is not yet the picture

**Seen on v9m** (`v9m/pics/cmp-exurchins-128.png`): balls covered in fins and flakes, 1,729 pieces.

**Cause** (reasoned from `30-shaders.js`, and the fix confirms it): a trap solid has layers without end, each
thinner than the last. The picture drops every layer thinner than two to three of its pixels (`TRAP_THIN`, through
`gPix`). A volume sample is asked with `gPix = 0` and holds them all. The estimate of a trap solid is a true
distance to first order, so the half-cell offset made a tube one cell wide round every hair. The "pit" rule is not
the cause here.

**What the mesher does now, only for a solid made by a trap** (`job.trap`, from `colProgramNeeds().solid`):
1. `meshCore` finds the samples inside parts at least `g.thinT` thick (2.4 picture pixels, kept between 0.5 and 1
   cell). Thickness is read from three samples in a row: `|p - r| - 2v`.
2. `meshThin` works out for each sample near the surface a distance `u` to the thick parts alone (from balls round
   the samples of step 1). An estimate more than a quarter cell shorter than `u` comes from a thin layer and is
   replaced by `u`; with no thick part within reach the sample is put outside. A sample beside a wall that no
   sample fell into (`meshWall`) keeps its estimate.
3. The reading runs `g.thin + 1` slices ahead of the marching (two more raw slices are held).

**Measured** (overlap; picture only; model only; pieces), `v9m/check-ex.txt` against `r10-mesh-c/check-ex.txt`:

| Job | v9m | round 10 |
|---|---|---|
| Sea urchins, 128 cells | 0.780; 1.8 %; 26 %; 1,729 | 0.851; 5.8 %; 10.7 %; 9 |
| Sea urchins, 256 cells | 0.853; 2.3 %; 14.5 %; 7,962 | 0.903; 4.2 %; 6.1 %; 17 |
| Sea urchins, offset 0 | 0.902; 6.2 %; 4.0 %; 35 | 0.886; 8.1 %; 3.7 %; 15 |
| Chain of bubbles, 128 | 0.946; 1.2 %; 4.4 %; 210 | 0.954; 2.3 %; 2.4 %; 44 |
| Chain of bubbles, offset 0 | 0.460 (inside out) | 0.961; 3.9 %; 0 %; 122 |
| Arches and hoops, 128 | 0.957; 1.2 %; 3.3 %; 1,526 | 0.969; 1.5 %; 1.6 %; 28 |
| trapsolid-128 (standard) | 0.965; 0.9 %; 2.7 %; 100 | 0.971; 1.1 %; 1.8 %; 103 |
| Mandelbrot with the trap added | 0.828; 17.2 %; 0 % (inside out) | 0.967; 1.9 %; 1.4 % |

Hue difference: bubbles 49 to 21 degrees, arches 12.1 to 6.5, trapsolid 7.5 to 6.9, trap added 23.8 to 6.3,
urchins 84 to 69 (colours are t9-mesh-2, the engine's).

**Seen on the final build** (`r10-mesh-c/pics/cmp-exurchins-128.png`, `cmp-exbubbles-128.png`,
`cmp-trapsolid-128.png`): the urchins are balls with their thick spikes and no fins. Not as the picture:
- the thin spikes the picture draws two to four pixels wide are missing or cut short;
- a band about half a cell wide remains all round (the offset itself: the picture's own skin is 0.8 pixel);
- **trapsolid-128 looks rougher than on v9m**: better outline and hue, but a terraced surface, Euler number -98
  against -14, 65,848 triangles against 39,892 and 79.8 cm3 against 85.8, so the kept shell now has openings into
  the hollow. Not traced. A wider reach (`r10-mesh-d/`, two cells) did not cure it and brought flakes back on the
  urchins (614 pieces), so it was taken out again. Next thing to try (reasoned, not run): let `meshThin` replace
  only "pit" samples (`meshPit`), so that a clean sample outside a thin wall is never touched;
- the smallest end bubbles of "Chain of bubbles" are lumps, and its little front bubble is a dent.

## t9-mesh-5, inside-out piece and negative volume: fixed (measured)

`meshPieces` works out each piece's volume and takes the largest among the pieces with a positive one.
Bubbles at offset 0: 100 x 43.0 x 42.1 mm, 56.86 cm3, overlap 0.961 (v9m: a ball, -447.19 cm3, 0.460). The same
fault showed on v9m at the standard offset for a trap added to the Mandelbrot set (-53.4 cm3); now 199.0 cm3. If no
piece has a positive volume, the readme gives no volume and says the surface faces inward, and the panel warns
(`info.inward`; reasoned, no scene of mine does it).

## t9-mesh-3 and t9-mesh-4, the warnings: fixed (measured, `r10-mesh-c/log-warn.txt`)

`meshPieces` also finds which pieces lie inside the largest one (a line straight up from one point of each piece,
counted through the largest piece). Only pieces that can be seen count.
- trapsolid at 128, 192, 256: no warning (v9m: warning at 192 and 256). Row: "The largest of 212, with more than
  99% of the surface that can be seen".
- power -2 at 96: "The largest of 757, with about 43% of the surface that can be seen" and the warning (v9m: no
  share, short warning). At 128: 28 %, at 256: 16 %.
- the advice now reads: untick the box and start again; with every piece kept more cells follow the picture; with
  the box ticked more cells tend to make the kept piece smaller; then the offset.
- every piece kept, power -2 at 128: the "rougher than the picture" sentence as before. Mosaic: as before, with
  "of the surface that can be seen".
- The share is shown whenever pieces that can be seen were left out; with none: "The others lie inside it."
Not run: 512 cells, and the Kleinian view at 512 with every piece at offset 0.

## The thin coloured line round a cut face at offset 0: not done

No time. Unchanged: cutm-128-off0 gives the same files as v9m, face measure 0.947 (`cmp-cut0.txt`).

## Names added or changed (all in `src/js/46-mesh.js`)

- `MESH_THIN` (0.5), `MESH_THIN_PX` (2.4), `MESH_THIN_TOL` (0.25).
- `meshCore(g, lo, mid, hi)`, `meshWall(v, a, b, c, thin, h)`, `meshThin(g, T, deep, raw, at)`.
- `g.thin`, `g.thinT` in `meshBuild`; its loop now keeps raw slices in `raw[]` and reads ahead; `job.trap`.
- `meshSlice(..., drop)`: one more argument, slices have `.drop`; `meshPoint` rule 3 (colour from the inside end).
- `meshPieces` returns `{ pieces, best, seen, seenTris, inward }`, no longer a number. `meshExtent` is gone.
- `info.seen`, `info.inward`; `kept` and `part` now count only what can be seen.
- Texts: Pieces row, `#meshWarn`, readme lines Volume, Grid (two lines for a trap solid), Pieces, the closed line.
- No id, label, file name, state field or CSS changed.

## For the person joining the files

- `job.trap` asks `colProgramNeeds()` (25-colour.js) and `job.snap.basis`, `.stage.ph`, `.S.view.fov` (40-render.js).
  If one is missing the thin limit is half a cell.
- **Engine, the better cure:** give volume samples of a trap solid the picture's pixel size (`gPix` is 0 for them;
  `pagePix` in `main()` already holds it). Then the samples lose the same layers as the picture and `meshThin` has
  nothing left to do.
- **Engine, t9-mesh-2:** bubbles at offset 0 have the picture's colours (6 degrees), at 0.5 they do not (21). So a
  sample inside the solid carries the right colour and a sample just outside does not.
- **Closing text, `src/body.html`:** if it says a model shows what the picture shows, add: "For a solid made by a
  trap, layers thinner than about half a cell are left out of the model, so the finest spikes are missing."

## Checked on the final build

- Smoke test `tools/smoke-v9m.json`: 52 steps, exit 0, no console errors, finished 07:20
  (`out/r10/mesh/smoke-final.log`; measured on the final build).
- Careful with the folder `out/r10/mesh/r10-mesh/`: its standard and ex runs (checks, pictures) are of the dropped
  wider-reach version; its warn, cut0 and add runs are of the final build. The final build's standard and ex
  results are the text files and pictures in `r10-mesh-c/`. The standard jobs, warn, cut0 and add were not run
  again after the source went back to the build of 07:01; the page is the same file (md5 above).
- Built-in fields (`fields.py`): not run this round. They do not take the new path (reasoned), but `meshPieces`
  and the loop of `meshBuild` changed for every solid; the six ordinary standard jobs are the evidence there.
