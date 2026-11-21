# Round 4: the user's second set of remarks, and what gets built

The user tested the early build (the page as integrated after `docs/SPEC.md`) and sent twelve remarks. They are
quoted here word for word and numbered N1 to N12. Read them as the standard everything is judged against. The
user is not a mathematician; they judge by how the pictures look and how the controls feel.

## The user's words

- **N1.** "something about the sphere inversion approach seems wrong. at z=0 it looks fine, but if i slice through
  the rest, the fractal becomes disconnected and looks weird - not what I expected at all. so the approach needs
  to be fixed (maybe have a checkbox or dropdown with different approaches, so the history tracks?). Also, it
  seems odd that the number of planes (idk what's actually happening btw, I'm just messing with sliders to see
  changes) is arbitrary - shouldn't it be forced? like idk, I see quaternions in the klein parameters, and I know
  rotations in 3d require quaternion stuff, and this approach is based off the klein stuff - I don't actually know
  the math so it might all be tangential things but I would have thought that this just comes naturally from where
  the point starts in 3d space. I wonder if the "use third map" button is relevant at all here."
- **N2.** "for default settings, like what the first time opening the page should have, is balanced performance,
  color by orbit trap, trap type is sphere shell, trap colored by how near it came as a glow, a reversed rainbow
  palette, highest search depth for klein objects,"
- **N3.** "the orbit trap approach in 3d is not right at all. like in other 3d fractals, the actual shape of the
  fractal changes based on the orbit trap selected. but in here, the shape seems to be the same, but the coloring
  on the surface is different. the 2d side is great, btw - keep that as it is - it's the 3d shapes that's the
  problem. and I know it works for 3d objects, I've seen so many renders of insane orbit traps on the same
  fractals that make them look so different"
- **N4.** "there should be a button somewhere that toggles extreme values, like enables much higher searches for
  klien objects and iterations for mandelbrots, etc."
- **N5.** "there should also be a high quality render button that exports to a file on disk, with settings like
  resolution and whatnot, ideally rendering in the background while you keep going (where if you change settings
  in the live app it doesn't affect the settings in the background render)"
- **N6.** "it would also be awesome to have a 3d export, where I could load the 3d object in blender or rhino or
  something and put it in scenes or 3d print it or whatever"
- **N7.** "shouldn't the saved julia points be a dropdown instead of whatever it is now? like the klein menu?"
- **N8.** "the preset locations/parameters should be independent of things like depth of search and iteration,
  camera location, etc. if that makes sense"
- **N9.** "you also don't have any klein presets that mess with the turning-out sphere - is that intentional?
  please add to the list, rather than take things away"
- **N10.** "is distance estimation a technique you can add to make crisper surfaces in 2d (since I see that you
  have it already for 3d, if I understand correctly)? and what about internal coloring for 2d? and different
  options for coloring inside vs outside? etc."
- **N11.** "in the rough (fastest) distance estimation, in the daudy rabbit for example in 3d, there is this weird
  glow artifact around the fractal. can this be fixed? or is that just a natural consequence?"
- **N12.** "that raymarching artifact where 3d objects appear as a set of slices appears even with the fine
  setting, which seems like a bug somewhere (looking at the daudy rabbit)"

The first fifteen points and the standing requirement ("whatever approach you use, the z=0 case should be
identical to the 2d case") in `docs/SPEC.md` still hold.

## What happened between the early build and this round

- Twenty-one testers went through the early build. Their reports are in `notes/_tests.md`, their 104 defects in
  `notes/_defects.json` (fields: id, title, severity, group, repro, expected, actual, evidence, suggested_fix,
  from). The groups engine, maths, colour, dial and camera were worked on in a fix pass (`notes/fix-*.md` say
  what was done); the 42 defects of group "page" are still open and belong to this round's page engineer.
- The fix pass also took N11 and N12 (shaders), the colour part of N2 (colour), and the kit's side of N4 (dial).
- `base3/` is the frozen, working copy of the whole app after that fix pass. Test against it.

## Facts that shape the work

**Saving files.** The published page runs in a locked-down frame where a download link does nothing. The core
file now has `saveFile(filename, data)` (see `docs/CONTRACT4.md`), which hands the file to the host; the host
shows the viewer a confirmation for each file, so a save must start from a click. The host only accepts these
endings: png, jpg, jpeg, webp, gif, txt, json, md, csv, svg, pdf, html, zip. A 3D model file (stl, obj, ply)
therefore travels inside a zip.

**The picture goes through one function call.** `30-shaders.js` is built so that every distance query of a
picture goes through a single call to `de()`; this keeps the compile time down on Windows. Additions keep to it.

## Decisions, point by point

**N1. A new default approach, "pillow"; the present one stays as an earlier version.** The present rule with
planes = 2 is discontinuous on the seams between its planes, which is what tears the solid when it is sliced
off z = 0. Three versions of a continuous replacement are being prototyped and compared (see
`out/proto/` and, once written, `notes/pillow.md`); the maths engineer integrates the winner as approach id
`pillow`, first in the list and therefore the default. It has no dials, and it only has a meaning for whole
powers (`integerOnly: true`, see the page assignment). The present approach `mercator` stays in the list as
"Sphere inversions" with its planes dial starting at 1 (the plain sum of inversions, which is continuous) and
the folded settings kept as "earlier version" so the history stays visible.

**N2. Defaults.** Quality Balanced (already so). Colour: orbit trap, sphere shell, "how near it came, as a
glow", Rainbow reversed (done in the fix pass). Kleinian depth of the search starts at 150, the top of its
ordinary range (done in the core file).

**N3. The trap can be the solid.** In 3D a new choice says what the trap does: it colours the surface (as now),
it IS the solid, or it is added to the solid. "Is the solid" means: the solid is the set of all points whose
orbit comes within a chosen thickness of the trap shape, so each trap shape gives a different object. The 2D
view is not changed.

**N4. "Extreme ranges" switch.** One switch widens the ranges of the dials that have wide limits defined
(iterations, Kleinian depth, ray steps, passes, resolution, drawing radius, power and others).

**N5. "Save a picture".** A new section starts a background job that renders the picture as it is at that
moment at a chosen size and quality, while the page stays usable; later changes do not affect the job. When it
is done the user clicks "Save the file".

**N6. "Save a 3D model".** A new section turns the solid into a triangle mesh (marching cubes over a grid of the
distance estimate) and saves a zip with STL, OBJ and PLY files as chosen, for Blender, Rhino or a 3D printer.

**N7. Julia points are a drop-down** like the Kleinian list, with the user's saved points on top.

**N8. A list entry sets only what it is about.** A Julia entry sets c. A Kleinian entry sets the group (mu, L,
the third map) and its turning-out sphere. Nothing else changes: not the camera, not the depth or iterations,
not the quality, not the approach or its dials. A separate small button "Frame it" moves the camera to the
entry's recommended view for those who want that.

**N9. More Kleinian entries**, at least ten, that differ in the turning-out sphere. Nothing is removed.

**N10. 2D view.** The outline of the flat picture already comes from the distance estimate (which is why thin
threads show as clean lines); the answer to the user's question is yes, and it is there. New: a dial for the
outline's width, a glow next to it, a choice of how the INSIDE is coloured (plain as now, orbit trap, where the
orbit ends up, how deep inside, how quickly it settles) and a separate palette for the inside. The default look
of the 2D view does not change ("the 2d side is great, btw - keep that as it is"). In 3D the cut face can
optionally be coloured like the 2D inside.

**N11, N12.** Taken in the fix pass by the shaders engineer; `notes/fix-shaders.md` says what was found. This
round re-checks them on every new feature (trap solids, the new approach).

## Later findings that change the decisions above (read these; they win where they differ)

**What N12 turned out to be.** The "set of slices" is not in the shape. On the Douady rabbit at Fine the same
surface drawn with a plain colour mode (depth, no shadows) is perfectly smooth (`out/me/rabbit-fine-close-plain.png`);
with the orbit trap it is covered in fine concentric rings (`out/me/rabbit-fine.png`, `rabbit-fine-close.png`).
The rings are in the trap colour. A ray stops a fraction of a pixel short of the solid, so the colour is read
from a point hovering just outside it. That point's orbit follows the surface for a while and then flies off,
and the last few steps of the flight pass the trap at places that depend on exactly how high the point hovers.
The hover height changes smoothly across the picture, so the colour ripples: one ring per extra step. Evidence
(`out/me/rings-sheet.png`): no rings at 12 iterations (the hit then sits on the surface that the step limit
defines), rings at 24 and 60, almost none with the surface threshold at 0.2 pixels, coarser ones at 3 pixels.
Moving the colour point a little way inside does not help (`out/me/in-rabbit-fine.png`): inside points near the
surface have the same problem. The cure is to count only the part of the orbit that still follows the surface,
and to let the last few steps before the flight fade out smoothly: `gFade` in CONTRACT4. This belongs to the
shaders engineer (the two colour queries) and the colour engineer (the weights in `trapAdd`). The earlier fix
pass looked for the cause in the ray march and the shadows; the chequered shadow patches it found are a
separate, smaller thing.

**What N1 turned out to be.** Three layouts of the "pillow" rule were built and compared with the existing
rules by two judges and an independent maths check (`notes/_pillow_lab.json`, pictures under `out/proto/`). The
pillow is sound (exact on z = 0, no jumps) but none of the three layouts looks good: rocks, flames and dusty
crystals, with creases and fins. Both judges ranked the existing rule with ONE plane first: it is clean in
every view, exact, and has no seam, but it is the "inflated" set, with detail around one plane only. Decision
for now: the planes dial of `mercator` starts at 1 (done), the folded settings stay available as an earlier
version, no pillow is shown as the fix, and a second round of prototypes is under way. The page must say this
honestly. The page assignment's whole-powers item stays (a later approach may need it).

## Assignments

Everyone: read `docs/CONTRACT.md`, then `docs/CONTRACT4.md` (the names added for this round; they are binding),
then this file, then the notes of your module. Test against `base3/` plus your own files. Where you depend on
something another engineer is building in parallel, the contract tells you its name and exact meaning: code
against it, test with a private stand-in (`--swap`, kept under `out/r4/<you>/`), and near the end look whether
the real thing has arrived in `src/` and test with it if so.

### shaders (`src/js/30-shaders.js`)

1. **Trap solids (N3).** The colour module provides `float trapDist(vec3 v)` and declares the uniforms
   `uTrapSolid`, `uTrapW`, `uTrapSkip` (CONTRACT4). Definition: with `uTrapSolid` 1 the solid is the set of
   points p for which some orbit point v_k, with `uTrapSkip <= k <= step limit` and taken before the orbit has
   escaped, lies within `uTrapW` of the trap shape. Its distance estimate is the smallest, over those k, of
   `(trapDist(v_k) - uTrapW) / s_k`, where s_k is how much the map from p to v_k stretches (take it from the
   neighbouring orbits, erring on the large side; in the modes with one neighbour or none use what those modes
   have). It is negative inside. With `uTrapSolid` 2 the scene's distance is the smaller of this and the set's
   own. The slope on a trap surface is sampled, not taken from the set's gradient. It works in Mandelbrot and
   Julia modes and in the Kleinian mode (there, the same idea with the scale factor the Kleinian estimate
   already tracks); in the mosaic only if it costs nothing extra. With `uTrapSolid` 0 nothing may get slower
   beyond one test per step, and the compile time may not grow by more than a fifth: measure both.
   Done when: with the sphere-shell trap (radius 0.7, thickness 0.05, skip 1) the Julia set for c = -1 and the
   default Mandelbrot each show a new, clean solid built from the shell's pre-images; the cross, line, ring and
   point traps each give a clearly different object; silhouettes are clean at Balanced and there is no speckle;
   N11 and N12 do not reappear on these solids. Show the pictures.
2. **Raw output for the 3D model (N6).** Uniform `uRaw` (CONTRACT4): in the flat branch, when it is on, write
   `vec4(albedo, d)` instead of the flat picture.
3. **Cut face hook (N10).** After the hatch colour of the cut face is computed, pass it through the colour
   module's `cutFaceColour(p, hatch)`.
4. Anything of N11 and N12 that `notes/fix-shaders.md` lists as left over.

### render-export (`src/js/40-render.js`, new `src/js/45-export.js`, new `src/css/45-export.css`)

1. **Snapshots** `takeSnapshot()` and `releaseSnapshot(snap)`, and **`sampleSlice(...)`** (CONTRACT4). A snapshot
   freezes everything a picture depends on (all of `S`, the camera as `basis()` gives it, the theme colours, the
   compiled program) so that it can be drawn or sampled later whatever the live page has become.
2. **The picture job (N5)** and its panel `buildExportPanel(host)`. Controls, built with the dial kit under the
   group `export`: size (as on screen, twice that, four times that, 1920 x 1080, 2560 x 1440, 3840 x 2160,
   7680 x 4320, square 2048, square 4096, or typed width and height), quality (as on screen now, Fine, or Extra
   fine with more passes and ray steps), format (PNG, JPG, WebP). Buttons and states: "Start the picture"; while
   it runs a progress bar with percent and an estimate of the time left, and "Cancel"; when done a small
   preview, the file size, "Save the file" and "Discard". One job at a time is enough.
   The job takes its snapshot at the start. It renders in tiles in the background through the same GL context,
   with the same tone curve as the screen. The live view stays usable: while the user is dragging or the live
   picture is unfinished the job takes at most about a quarter of the GPU time, in slices short enough that
   frames stay under 50 ms apart; when the live view is idle the job takes the rest. It keeps going when the
   tab is hidden. An 8K picture must not crash the page: draw finished tiles straight into a 2D canvas, and if
   the browser cannot make a canvas that large say so in plain words before starting.
   Done when: a test receives the file through `window.squaringLabSaveHook`, its size in pixels is exactly what
   was asked, it matches the on-screen picture when scaled down, a job started before changing the approach,
   the colours and the camera still shows the ORIGINAL picture, and frame gaps measured while a job runs stay
   under 50 ms on Balanced.
3. Whatever `notes/fix-render.md` lists as left over.

### mesh (new `src/js/46-mesh.js`, new `src/css/46-mesh.css`)

**The 3D model job (N6)** and its panel `buildMeshPanel(host)`, group `mesh`.
- The field is the distance estimate sampled slice by slice with `sampleSlice` (alpha is the distance, rgb the
  surface colour). Marching cubes between consecutive slices, streamed so that only two slices are in memory;
  vertices welded (shared along cell edges) so the mesh is indexed and closed; vertex positions and colours
  interpolated along the cell edge. The surface level is "Surface offset" in grid cells (0 to 2, start 0.5):
  a positive offset thickens thin parts, which a printer needs.
- Region: the cube that holds the solid, found with a coarse first pass inside the drawing radius, with a small
  margin. Resolution: 96, 128, 192, 256, 384 or 512 cells along the cube. Show the triangle count and the file
  sizes when done, and warn above two million triangles.
- Options: "Keep only the largest piece" (on at the start: floating crumbs make a print fail), "Longest side,
  mm" (100) used as the scale of the saved coordinates.
- Formats, any combination: STL (binary), OBJ (vertex colours written as "v x y z r g b"), PLY (binary, vertex
  colours). Everything chosen goes into one zip (plain "store" entries with correct CRC-32) together with a
  short readme.txt (what is inside, the size, the triangle count, how to import it into Blender and Rhino).
- A background job with its own snapshot, progress, "Cancel", then "Save the file" (`saveFile`). The page stays
  usable while it runs.
- For tests without the renderer: built-in test fields (a sphere, a torus) behind the same sampling signature.
Done when: for the sphere the mesh is closed (every edge is used by exactly two triangles), its volume is
within 2 percent of the true value and its vertex count is sensible; the Julia set for c = -1 at 128 cells
exports through `window.squaringLabSaveHook`, the zip unpacks, the STL parses back and its largest piece is
closed; the Kleinian default exports too.

### colour (`src/js/25-colour.js`)

1. **Controls and uniforms for trap solids (N3)**: `solid`, `thick`, `skip` (CONTRACT4), shown when the colour
   mode is the orbit trap with a real trap shape and the view is 3D. Set `uTrapSolid`, `uTrapW`, `uTrapSkip` in
   `setColourUniforms`.
2. **Colours on a trap solid.** On such a surface "how near it came" is the same everywhere, so those choices
   give one flat colour. Add choices that work there (which step touched the trap; where on the trap it
   touched) and make a sensible one apply automatically when the trap is the solid. The sphere shell, the cross
   and the ring must each look really good as solids with the default palette.
3. **2D view (N10)**, shown only in the 2D view, and WITHOUT changing how the 2D view looks at its defaults:
   `inMode` (inside: plain as now, orbit trap, where the orbit ends up, how deep inside, how quickly it
   settles), `inPal` and `inRev` (a palette of its own for the inside, or the same as outside), `edge` (outline
   width in pixels, 1 as now, 0 for none, drawn from the distance estimate so thin threads stay visible),
   `edgeGlow` (0 as now).
4. **Cut face** `cutFaceColour(vec3 p, vec3 hatch)` and the check `cutFace` (off at the start).
5. Whatever `notes/fix-colour.md` lists as left over.

### maths (`src/js/10-approaches.js`, `src/js/20-formula.js`, `src/js/60-measure.js`)

Briefed separately when the prototype comparison has finished: integrate the chosen pillow rule as approach
`pillow` (first in the list, `integerOnly: true`, plain-language texts, the JavaScript mirror, the scorecard
entries), set the planes dial of `mercator` to start at 1 and word its panel as described under N1.

### klein-presets (research: `data/klein-presets.json`, `notes/klein-presets.md`)

At least ten new entries (group "Turning-out sphere") that differ from the existing ones in the centre and
radius of the turning-out sphere and give visibly different objects: for instance the sphere centred close to
a point where pearls touch, so the object opens out into a long chain; a centre inside a big pearl; a small
sphere that shows one neighbourhood large; centres off the plane with a j part in mu. Each entry: whole at
Fine quality (no hollow or sliced pearls), bounded, attractive at the default camera and at phone width, with
a recommended camera for "Frame it" and a one-line note in plain words. Entries no longer set the depth of the
search, so each must look right at any depth from 60 up; say in the notes what each needs. Keep all nineteen
existing entries.

### page (`src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js`)

1. The 42 open defects of group "page" in `notes/_defects.json` (skip those made pointless by 3 and 4 below).
2. **N4**: an "Extreme ranges" switch in the top row beside "2D view" and "Collapse all", with a one-line hint.
   It sets `S.extreme` and calls `setExtreme(on)`. Give wide limits (`xmin`, `xmax`, `xlo`, `xhi`) to:
   iterations, Kleinian depth, ray steps, refining passes, resolution, drawing radius, power, the Julia c dials,
   the Kleinian dials, the mosaic cell size, and whatever else it makes sense for; roughly five to ten times the
   ordinary range. Approach and colour dials get theirs from their own modules.
3. **N7**: the Julia list becomes a drop-down like the Kleinian one (groups: your saved points, classic sets,
   found by exploring), with the name box and "Save this point" beside it and "Delete this saved point" when a
   saved one is chosen.
4. **N8**: a Julia entry sets only c; a Kleinian entry sets only mx, my, mz, L, three, cx, cy, cz, invR. Add
   "Frame it" beside each list (camera only). Saved points hold only c and a name. When the values are moved
   away from the chosen entry, the list shows "Your own values" instead of a stale name.
5. **N6, N5**: two new sections after "Quality and speed": "Save a picture" (`<details id="secExport">` holding
   `<div id="exportPanel">`) and "Save a 3D model" (`secMesh`, `meshPanel`). In `boot()`, after the renderer is
   up: `if (typeof buildExportPanel === 'function') buildExportPanel('exportPanel')`, and the same for
   `buildMeshPanel`. They take part in Collapse all.
6. **Whole powers only**: when `ap().integerOnly` is true the power dial takes whole numbers only (round the
   power when switching to such an approach, keep the whole-step behaviour on, and say why in a hint); give the
   freedom back when leaving.
7. Re-embed the Kleinian list after the research engineer has extended it (`notes/ui_embed.py`); if the new
   entries have not arrived when you finish, say so.
8. A "Reset everything" button, a visible mark on the active quality preset, and the page texts: the closing
   sections must answer the user's questions in plain words with what is true now. The text about the new
   approach comes from `notes/pillow.md` when it exists; if it does not exist yet, leave a clearly marked gap
   and say so.
9. Extend `tools/smoke.json`: the Julia drop-down; an entry leaves the camera and the iterations alone; "Frame
   it"; the extreme switch widens a range and pulls a value back; the two new panels exist; a 256 x 256 picture
   job and a 48-cell model job each deliver a file through `window.squaringLabSaveHook` (skip a job with a
   clear message when its module has not arrived).
