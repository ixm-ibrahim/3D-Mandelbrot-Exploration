# 3D Squaring Lab: how the code is laid out, and the rules for working on it

The lab is one web page (published as a Claude artifact) that draws 3D Mandelbrot, Julia and Kleinian sets
with a WebGL 2 ray marcher. It is assembled from small source files by `build.py`.

## Layout

```
src/head.html            <title>, meta, font link
src/css/*.css            styles, concatenated in file-name order
src/body.html            the page markup (no <html>/<body> tags; the artifact host adds them)
src/js/*.js              scripts, concatenated in file-name order INSIDE ONE FUNCTION SCOPE
base/                    a frozen copy of src/ taken before this round of work (known good)
build.py                 assembles the page
tools/shot.py            drives the page in headless Chrome and saves screenshots
docs/                    this file and SPEC.md
notes/<you>.md           your working notes and findings
data/                    preset data produced by research
out/<you>/               your screenshots
squaring-lab.html        BUILD OUTPUT, the published page. Never edit it by hand.
```

Module files and their owners this round:

| File | What it holds | Owner |
|---|---|---|
| `src/js/00-core.js`, `src/css/05-core.css` | helpers, state `S`, hooks, busy indicator, theme | orchestrator (frozen) |
| `src/js/10-approaches.js`, `src/js/20-formula.js` | the approaches (maths + shader algebra + texts), formula compiler, equation presets | approaches |
| `src/js/25-colour.js` | palettes, orbit traps, colour controls, colour shader hooks | colour |
| `src/js/30-shaders.js` | the scene shader: distance estimates, ray march, lighting, 2D view | shaders |
| `src/js/40-render.js`, `src/css/40-render.css` | WebGL plumbing, shader compile, drawing schedule, picking | render |
| `src/js/50-camera.js`, `src/css/50-camera.css` | camera, pointer/keyboard/wheel input, zoom slider, camera-mode button | camera |
| `src/js/60-measure.js` | the scorecard and the two "one step" figures | measure |
| `src/js/70-dial.js`, `src/css/70-dial.css` | controls kit: dial, checkbox, drop-down, spec-driven builder | dial |
| `src/body.html`, `src/css/00-base.css`, `src/js/75-presets.js`, `src/js/80-ui.js`, `src/js/90-boot.js` | page markup, base styles, preset lists, wiring | ui (runs after the others) |

## Rules

1. **Edit only the files you own.** If you need something from another module, use what this contract
   promises. If the contract is missing something you need, do not edit the other file: work around it
   inside your own file and say so under "open issues" in your report.
2. **One scope.** All `src/js` files are pasted into a single function, in file-name order, under
   `'use strict'`. A top-level `const`/`let`/`function` in one file is visible in every other file. So:
   - top-level names must be unique across files (the names each module provides are listed below; pick
     clearly prefixed names for anything private to you);
   - only `90-boot.js` runs code at load time. Everywhere else, top level may only declare things. A
     top-level initialiser must not use a name from a later file (it would not be initialised yet); code
     inside functions may use anything.
3. **Keep the names in this contract working.** Other modules call them. You may add to them.
4. No frameworks, no external scripts, no build tools beyond `build.py`. Plain ES2020 and WebGL 2.
5. The page runs in a locked-down frame: `alert/confirm/prompt` do nothing, downloads are blocked, and
   `localStorage` may throw (wrap every access in try/catch and work without it).
6. Do not run git. Do not publish anything. Do not start servers.
7. Run only these commands: `python build.py ...` and `python tools/shot.py ...` (and `python` on scripts you
   write under `notes/` or `tools/`). Use the Read tool to look at screenshots.
8. User-facing text: plain sentences in sentence case, named for what the user sees, no emoji, no
   exclamation marks, no "not X but Y" flourishes. Colours only through the CSS tokens in
   `src/css/00-base.css` (`--paper --panel --stage --ink --ink-2 --line --brass --cut --cut-ink --ok --warn --bad`),
   so both light and dark themes work. Controls need visible keyboard focus and must fit a 375 px wide phone.
9. Leave the code tidy: comments explain why, not what. Delete debugging leftovers.

## Building and testing

```
python build.py                                   # full build from src/ -> squaring-lab.html + dist/preview.html
python build.py --name mine --base base --use src/js/70-dial.js src/css/70-dial.css
                                                  # dist/mine.html: the frozen baseline with only YOUR files swapped in
python tools/shot.py --url dist/mine.html --js "<javascript>" --wait-done --shot out/mine/a.png --clip "#stage"
python tools/shot.py --url dist/mine.html --actions out/mine/steps.json      # several steps; see tools/shot.py and tools/smoke.json
```

While several people edit `src/` at once, **always test with `--base base --use <your files>`**: the plain
build may be broken by someone else's half-finished file. `tools/shot.py` prints any console error or
uncaught exception at the end and exits non-zero; treat every one as a bug to fix or explain.

In page scripts, `window.squaringLab` exposes `S` (state), `cam`, `touch()`, `refresh(slow)`,
`syncControls()`, `idle()`, `measure`, `setBusy`. After changing `S` from a test, call
`L.refresh(false)` (approach, power or mode changed) or `L.touch()` (anything else), and `L.syncControls()`
if you want the controls to show the new values. `--wait-done` waits for `L.idle()`.

## What each module provides

### 00-core.js (frozen)
`$`, `PI`, vector helpers `dot cross len add sub scl norm clamp` (points are `[x, y, z]` arrays),
`specDefaults(specs)`, the state `S`, `ap()` (current approach), `apP()` (its parameter object),
`apVec()` (the same as four numbers, the shader uniform `uA`), `initState()`, `hooks`, `setBusy(key, label)`,
`theme`, `hexRgb`, `lin`, `readTheme()`.

State `S` (read the comments in the file for meanings): `mode`, `flat`, `mosaic`, `mosaicCell`, `approach`,
`param`, `n`, `iter`, `eq`, `z0`, `c`, `abs`, `flip`, `cutOn`, `cut`, `colour`, `lightAz`, `lightEl`,
`q {res, aa, steps, detail, stepk, smooth, normals, ao, shadow, de}`, `view {fov, bound, zmin, zmax, fly, speed}`,
`v2 {x, y, h}`, `k {mx, my, mz, three, L, iter, invR, cx, cy, cz}`.
If you need shared state that is not there, create it in your own init function
(`S.thing = S.thing ?? default`) and list it in your report.

`hooks.view` (functions called at most once per frame after the camera or view changed) and
`hooks.refresh` (called at the end of `refresh()`). **Register your own hooks from your own init function**,
guarded so a second call does not register twice.

`setBusy('some-key', 'Short label')` shows the busy indicator in the stage corner; `setBusy('some-key', null)` clears it.

### Control specs
A control can be described as data and rendered by `buildControls` (70-dial.js):

```js
{ type: 'dial',   key, label, min, max, step, def, lo, hi, int, odd, animate, help, when }
{ type: 'select', key, label, def, options: [[value, text], ...], when }
{ type: 'check',  key, label, def, when }
{ type: 'note',   text, when }
```
`min/max/step` are the slider's range; `lo/hi` are the hard limits a typed value is clamped to (default: the
slider range); `int` whole numbers only; `odd` odd whole numbers only; `animate: true` offers a play button
that sweeps the value; `when: obj => boolean` hides the control when false; `help` is a one-line hint.

### 10-approaches.js, 20-formula.js
`APPROACHES`: array of
```js
{ id, name, tag, about,            // texts
  params: [control specs],         // at most four specs with a key; values in S.param[id][key]; uniform uA holds them in order
  glsl,                            // shader code defining: vec3 mul(vec3,vec3); vec3 pw(vec3,float); vec3 sqr(vec3); vec3 cmap(vec3)
  formula(p, n) -> string,         // shown in the approach panel; p is the parameter object, n the power
  axis(p) -> [x,y,z],              // the direction this approach singles out (drawn in the step figure)
  roundNote,                       // string, or function (p, n) -> string
  crush(p, n) -> [state, text], smooth(p, n) -> [state, text],   // state is 'ok' | 'part' | 'no'
  slice(ok, p, n) -> text }        // ok: did the measured plane z = 0 follow complex z^n
```
`MATH[id](v, n, p)`: the same power map in JavaScript (`v` a point, returns a point). It must agree with `glsl`.
The shader code may use what `GL_HEAD` declares: `PI`, `cmul(vec2,vec2)`, `at2(y,x)`, `uA` (vec4), `uPow`.
`compileFormula(text, allowZ, n2) -> GLSL expression string` (throws an Error with a user-readable message).
`PRESETS`: `[{ name, eq, z0, target?, dist? }]`.

### 25-colour.js
`PALETTES`, `COLOUR_CONTROLS` (specs; values in `S.colour`), `GL_COLOUR` (shader hooks, see the comment block in
the file for the exact contract), `setColourUniforms(L)`.
Hook names the shader calls: `trapStart()`, `trapAdd(vec3 v, float it)`, `colourCapture()`,
`surfaceColour(vec3 p, vec3 nor, float t)`, `colourUnlit()`, `flatColour(vec3 p, float d, float px)`.

### 30-shaders.js
`VERT`, `GL_HEAD`, `GL_ORBIT` (contains the placeholders `__F__` and `__Z0__`), `GL_KLEIN`, `GL_TAIL`, `BLIT`.
A scene program is `GL_HEAD + GL_COLOUR + (approach.glsl + GL_ORBIT with placeholders filled | GL_KLEIN) + GL_TAIL`.
`GL_HEAD` declares, for the other shader pieces: `PI`, `cmul`, `at2`, `uA`, `uPow`, `uBg`, `uCutCol`, `uCutInk`,
and the orbit results `gEsc`, `gIt`, `gLast`.

Uniforms of the scene program. **30-shaders.js declares and uses them; 40-render.js sets them. Both follow this table.**

| Uniform | Type | Value |
|---|---|---|
| `uRes`, `uOff` | vec2 | size in pixels of the picture being drawn; sub-pixel offset of this pass |
| `uCamPos`, `uCam`, `uFov` | vec3, mat3, float | from `basis()`: position; columns right, up, forward; `S.view.fov` |
| `uBound` | float | `S.view.bound` (NEW: replaces the constant BOUND) |
| `uPow`, `uA` | float, vec4 | `S.n`; `apVec()` |
| `uJulia`, `uC` | float, vec3 | 1 in Julia mode; `S.c` |
| `uMosaic` | float | NEW: `S.mosaicCell` when `S.mosaic` and mode is Mandelbrot, else 0 |
| `uAbs`, `uSgn` | vec3 | modifiers: `S.abs`; `(1, flip y ? -1 : 1, flip z ? -1 : 1)` |
| `uBail`, `uIter` | float, int | escape radius; iteration count (`S.k.iter` in Kleinian mode, else `S.iter`) |
| `uCut` | float | `S.cut` when `S.cutOn`, else `1e9` |
| `uFlat`, `uFlatC`, `uFlatH`, `uSliceZ` | float, vec2, float, float | NEW: 2D view: 1 when `S.flat`; `(S.v2.x, S.v2.y)`; `S.v2.h`; `S.cut` |
| `uSteps`, `uNT`, `uDetail`, `uStepK`, `uNormEps` | int, int, float… | ray steps; neighbouring orbits used (0, 1 or 3, from `S.q.de`); surface threshold; step share; slope sampling width |
| `uAO`, `uShadow`, `uShSteps`, `uAnalytic`, `uPick` | float…, int | crevice shading on; shadows on; shadow steps; exact slope on; picking pass |
| `uPx` | float | picture pixels per CSS pixel (for the hatch pattern) |
| `uBg`, `uCutCol`, `uCutInk`, `uLight` | vec3 | linear background, cut-face and hatch colours; unit vector toward the light |
| `uKMu`, `uKInvC`, `uKL`, `uK3`, `uKInvR` | vec3, vec3, float… | Kleinian group: `(mx, my, mz)`; `(cx, cy, cz)`; `L`; `three ? 1 : 0`; `invR` |

The 2D view is a branch inside the same scene program (`uFlat > 0.5`), not a separate program. In a picking pass
(`uPick > 0.5`) the shader writes `vec4(hit position, 1)` or `vec4(0)`; in the 2D view that is the slice point.

### 40-render.js
`canvas`, `stage`, `gl`, `initGL()`, `touch()` (state changed: redraw), `viewChanged()` (overlays only),
`kick()`, `renderIdle()`, `pick(px, py) -> [x,y,z] | null`, `say(text)` (status line), `R` (private bookkeeping).

### 50-camera.js
`cam` (`yaw`, `pitch`, `dist`, `target`: the arcball camera), `basis() -> { pos, right, up, f }` (unit vectors;
this is what the renderer draws from, in every camera mode), `resetCam(preset?)`, `bindView()` (attaches all
input handling; called once from boot), `clampDist(d)`, `drawTriad()`.

### 60-measure.js
`buildCard()`, `updateCard()`, `buildStep3d()`, `drawStep2d()`, `drawStep3d()`, `measure(F, n)`, `fmtN(n)`.

### 70-dial.js
```js
addDial(host, id, label, min, max, step, get, set, opts)   // opts: lo, hi, int, odd, def, group, animate, help
addCheck(host, id, label, get, set, opts)                   // opts: def, group
addSelect(host, id, label, options, get, set, opts)         // options: [[value, text], ...]; opts: def, group
buildControls(host, specs, obj, onChange, opts)             // opts: idPrefix, group -> { sync() }
syncControls()                                              // make every control show the current state
resetGroup(group)                                           // put every control of a group back to its default (calls its setter)
```
`host` is an element or an element id. Each returns `{ el, group, sync(), reset() }`.
The range input keeps the id `id`; the typed box keeps the id `id + 'Num'`.

### 80-ui.js, 90-boot.js
`refresh(slow)` (after approach / power / mode changes: updates texts, figures, scorecard, then `touch()`),
`applyEquation()`, `boot()`. `90-boot.js` sets `window.squaringLab` and calls `boot()`.
