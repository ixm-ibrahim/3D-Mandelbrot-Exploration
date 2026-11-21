# Contract, round 4: what is added to `docs/CONTRACT.md`

Everything in `docs/CONTRACT.md` still holds, with these changes. The names below are binding: other engineers
are coding against them at the same time as you.

## Files and owners this round

| File | Owner |
|---|---|
| `src/js/00-core.js`, `src/css/05-core.css`, `src/head.html` | orchestrator (frozen) |
| `src/js/10-approaches.js`, `src/js/20-formula.js`, `src/js/60-measure.js` | maths |
| `src/js/25-colour.js` | colour |
| `src/js/30-shaders.js` | shaders |
| `src/js/40-render.js`, `src/css/40-render.css`, `src/js/45-export.js` (new), `src/css/45-export.css` (new) | render-export |
| `src/js/46-mesh.js` (new), `src/css/46-mesh.css` (new) | mesh |
| `src/js/50-camera.js`, `src/css/50-camera.css`, `src/js/70-dial.js`, `src/css/70-dial.css` | nobody this round (leave them alone; report what you need) |
| `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js` | page |
| `data/klein-presets.json`, `notes/klein-presets.md` | klein-presets |

`base3/` is the frozen working copy to test against:

```
python build.py --name r4-<you> --base base3 --use <your files>
python build.py --name r4-<you> --base base3 --use <your files> --swap js/30-shaders.js=out/r4/<you>/30-shaders.js
```

The second form puts a private stand-in into another module's slot. Keep stand-ins, scripts and screenshots under
`out/r4/<you>/`. Never run plain `python build.py`. Rule 5 of the old contract ("downloads are blocked") is
replaced by `saveFile` below.

## 00-core.js (frozen): new

- `S.extreme` (boolean, starts false): the "extreme ranges" switch.
- `S.k.iter` now starts at 150.
- `saveFile(filename, data) -> Promise<{ ok: true } | { ok: false, code, message }>`. `data` is a Blob, a string,
  an ArrayBuffer or a typed array. On the published page it hands the file to the host, which asks the viewer to
  confirm; so call it only from a click, show `message` (a plain sentence) when `ok` is false, and keep the file
  so the viewer can try again. The host accepts only these endings: png, jpg, jpeg, webp, gif, txt, json, md, csv,
  svg, pdf, html, zip. In the local preview it uses a download link. A test may set
  `window.squaringLabSaveHook = (filename, blob) => { ... }` to receive the file instead of any download.

## 70-dial.js: added in the fix pass (see `notes/fix-dial.md` for the exact form)

- A dial spec or opts may carry `xmin`, `xmax` (slider range while extreme ranges are on) and `xlo`, `xhi` (typed
  limits while they are on).
- `setExtreme(on)`, `isExtreme()`.

## 10-approaches.js

- An approach may carry `integerOnly: true`: its rule only has a meaning for whole powers. `pw` and `sqr` round
  the power themselves; the page keeps the power dial on whole numbers while such an approach is chosen.
- New approach id `pillow`, first in `APPROACHES`. `mercator` stays, with its planes dial starting at 1.

## 25-colour.js

Shader side, all in `GL_COLOUR` (which comes before the orbit code in the program, so the orbit code can use them):

- `float trapDist(vec3 v)`: the plain distance from an orbit point to the current trap shape (added in the fix
  pass; `notes/fix-colour.md` gives its meaning per shape).
- `uniform float uTrapSolid;` 0: the trap only colours the surface. 1: the trap is the solid. 2: the trap is added
  to the solid.
- `uniform float uTrapW;` thickness of the trap solid, in the units of the orbit.
- `uniform int uTrapSkip;` orbit points with index below this are ignored (index 0 is the starting point).
- `vec3 cutFaceColour(vec3 p, vec3 hatch)`: the colour of the cut face at p; returns `hatch` unless the user has
  asked for the cut face to be coloured like the inside of the 2D view. It may read the same globals the other
  colour hooks read; the shader calls `colourCapture()` before it.

JavaScript side:

- `setColourUniforms(L, raw)`: `raw` is true when the call is for volume sampling (see `uRaw`). The colour module
  sets `uTrapSolid` to 0 in the on-screen 2D view (the 2D picture is not to change) and to `S.colour.solid`
  otherwise, including when `raw` is true.
- New keys in `COLOUR_CONTROLS` / `S.colour`: `solid` (0, 1, 2), `thick`, `skip`, `inMode`, `inPal`, `inRev`,
  `edge`, `edgeGlow`, `cutFace`. A `when` rule may read the global `S` (for `S.flat`, `S.mode`, `S.cutOn`).

## 30-shaders.js

- Uses `trapDist`, `uTrapSolid`, `uTrapW`, `uTrapSkip` as defined above, in `GL_ORBIT` and `GL_KLEIN`.
- `uniform float uRaw;` (declared in `GL_HEAD`; the renderer sets it; 0 everywhere except volume sampling). When
  `uFlat > 0.5` and `uRaw > 0.5` the program writes `vec4(albedo, d)` and nothing else: `d` is the signed distance
  estimate of the scene at the slice point exactly as `de()` gives it (positive outside, zero or negative inside;
  trap solids included; the cut plane ignored; the mosaic as on screen), and `albedo` is
  `surfaceColour(slicePoint, n, 0.0)` after `colourCapture()`, with `n` the unit gradient when the query has one
  and `(0, 0, 1)` otherwise: linear colour, no lighting, no tone curve, no outline.
- Calls `cutFaceColour(p, hatch)` for the cut face.

## The fading tail (the cure for N12, see "What N12 turned out to be" in SPEC4)

- `float gFade;` is declared in `GL_HEAD` (shaders) next to `gEsc`, `gIt`, `gLast`. Meaning: an orbit point with
  index `it` counts towards the trap with the weight `clamp(gFade + 1.0 - it, 0.0, 1.0)`. `1e9` means every point
  counts in full.
- The shader sets `gFade = 1e9` for every query except the one the surface colour is read from in the 3D view.
  For that query it first learns the smooth escape count of the hit point (a query with `gFade = 1e9`, reading
  `gIt`; for a point whose orbit does not escape, the step limit), then sets
  `gFade = max(count - TAIL, 1.0)` with a constant `TAIL` of about 4 (tuned by experiment), and queries again.
  The 2D view and volume sampling (`uRaw`) always use `1e9`: the 2D picture must not change.
- The colour module's `trapAdd(vec3 v, float it)` applies that weight to every measure it keeps (nearest
  distance, the step of nearest approach, the side, the three-tone mix): a point of weight 0 has no effect, a
  point of weight 1 its full effect, and in between the result moves smoothly, with no jump as `gFade` changes
  by a small amount.

## Base for this round

`base4/` is `base3/` plus the new page (drop-downs, extreme switch, the two new sections) and the 3D-model module.
Where this file or SPEC4 says `base3`, use `base4`.

## 40-render.js and 45-export.js (render-export)

- `takeSnapshot() -> snap`: an opaque object that freezes the picture as it is now: a deep copy of `S`, the camera
  as `basis()` returns it, the theme colours, the light, and the compiled scene program (kept alive while the
  snapshot lives). Nothing the page does afterwards changes it.
- `releaseSnapshot(snap)`: lets go of it.
- `sampleSlice(snap, cx, cy, side, z, N) -> Promise<Float32Array | null>`: `4 * N * N` numbers for the square of
  side `side` centred on `(cx, cy)` at height `z`: for each grid point, in rows from the lowest y upward and from
  the lowest x upward within a row, `r, g, b` (surface colour, linear, 0 to 1) and `a` (the signed distance
  estimate, scene units). Grid point `(i, j)` is at `x = cx - side/2 + (i + 0.5) * side / N`, the same for y.
  It uses the flat branch of the scene program with `uRaw` on, in pieces small enough not to stall the page, and
  resolves `null` if the picture cannot be sampled (GL context lost, program not available).
- `buildExportPanel(host)`: builds the "Save a picture" controls into the element `host` (an element or an id)
  with the dial kit, group `export`, and runs picture jobs. Returns nothing the page needs.
- `exportBusy() -> boolean`: a picture job is running (so tests can wait).

## 46-mesh.js (mesh)

- `buildMeshPanel(host)`: builds the "Save a 3D model" controls into `host`, group `mesh`, and runs model jobs.
  Uses `takeSnapshot`, `sampleSlice`, `releaseSnapshot` and `saveFile`.
- `meshBusy() -> boolean`.
- `zipStore(files) -> Blob`, where `files` is `[{ name, data }]` (data a Uint8Array or a string): a plain zip with
  stored entries and correct CRC-32. Others may use it.

## 80-ui.js, 90-boot.js, body.html (page)

- New sections after "Quality and speed": `<details class="sec" id="secExport">` holding `<div id="exportPanel">`,
  and `<details class="sec" id="secMesh">` holding `<div id="meshPanel">`.
- `boot()` calls `buildExportPanel('exportPanel')` and `buildMeshPanel('meshPanel')` when those functions exist.
- The extreme switch has the id `extreme`; the Julia drop-down `juliaPreset`; the "Frame it" buttons `juliaFrame`
  and `kleinFrame`.
- `window.squaringLab` also carries `takeSnapshot`, `sampleSlice`, `exportBusy`, `meshBusy`, `setExtreme`,
  `isExtreme`, `saveFile` (each only when it exists), and `idle()` stays "the live picture and the scorecard are
  finished" (it does not wait for background jobs).
