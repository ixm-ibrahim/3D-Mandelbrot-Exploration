# camera: fixes after the testers' round

Files changed: `src/js/50-camera.js`, `src/css/50-camera.css`. Nothing else in `src/` was touched.
Test page: `python build.py --name fix-camera --base base2 --use src/js/50-camera.js src/css/50-camera.css`.
This file adds to `notes/camera.md`; where the two disagree (easing time, key step, 2D wording, how typed
limits behave, what Reset view resets) this file is the current one.

## What changed, by defect

| Defect | Change |
|---|---|
| New from the user (lists no longer move the camera), p15-1 | Framing is now one function, `camHome(preset)`, used by `resetCam()` and by the Reset view button. Negative powers start further back: distance 3.8 x (1.3 + 1/max(1, -n)), target at the centre (n = -2: 6.84, -3: 6.21, -8: 5.42, -1 and nearer 0: 8.74), and the 2D span follows (n = -2: 4.38). The sizes were measured by probing the solid with `pick()` from four sides (`out/fix/camera/probe2.log`). With no preset passed, `resetCam()` asks the page for the list entry the dials stand on (`juliaPresetAt()`, `KLEIN_PRESETS[kleinPresetAt()]`, each guarded with `typeof`) and uses that entry's own camera, so Reset view is the "frame it" for a list entry once the lists stop moving the camera. The user's saved Julia points are skipped. Nothing here moves the camera unasked. |
| p7-1 (major) | A click with a pointer on Reset view, + or - hands the keyboard to the picture, as the Arcball and Fly buttons already did. Keyboard presses of those buttons keep the focus. |
| p4-1 (major) | One wheel listener on the whole stage instead of the canvas and the rail, so the wheel zooms over +, -, Reset view, Arcball, Fly and the limit boxes, and the page stays put. In 2D the spot under the pointer is held only over the picture; over a control the zoom is about the middle. If WebGL failed (`#glfail` shown) the wheel is left to the page. |
| p7-2 | `resetCam()` in fly mode applies the same speed rule as entering fly mode (`camFitSpeed()`). |
| code-2, p8c-1 (same defect) | `resetCam()` holds the start distance to the user's zoom limits (`clampDist`), for mode defaults and for presets. `resetZoomLimits()` now also holds the view that is not on screen (`camHoldDist()` for 3D, a clamp for the 2D span). |
| p8c-2 | A typed limit on the wrong side of the other one is refused (old value back, box flagged, a note says why), instead of being bent into a number nobody typed. A value outside the hard range is still held to the range, now with the flag and a note. The box tooltips state the factor-two rule. |
| p12-2 | The Reset view button resets only the view on screen (`resetView()`): in 2D the flat picture, in 3D the camera. `resetCam()` still resets both. |
| p12-4 | A note appears when the zoom is asked to go past a limit it already rests on, when the 2D zoom passes below 0.0005, and when the 2D closest limit is typed below 0.0005. The 2D box tooltip says so too. |
| text-18 | The 2D zoom is called "span" everywhere, never "height". |
| p4-2 | One constant, `CAM_STEP = 0.8`, for the + and - buttons and keys. |
| perf-7 | `CAM_EASE` 0.035 -> 0.07 s. Measured with wheel events sent from page script: one notch 2.46% in the worst frame, five notches 60 ms apart 4.33% (was 4.35% and 5.04%). A notch is about 92% done in 180 ms and settled in about 330 ms (the spec's "roughly 120 ms" gave way to the tester's 5% bar). |

## Names added (all in `50-camera.js`)

Public:
- `resetView()`: what the Reset view button does. Fresh framing of the view on screen only, then `touch()`. A "Frame it" control should call this.
- `resetCam(preset, only)`: new optional second argument, `'3d'` or `'2d'`, to reset just that view. Without it both, as before.
- `camHome(preset)`: the start framing `{ yaw, pitch, dist, target, h }` without applying it.
- `CAM_STEP` (0.8), `CAM_SHARP` (0.0005), `CAM_FOV0` (0.32), `CAM_FIT0`.

Private: `camFit`, `camListed`, `camHoldDist`, `camFitSpeed`, `camNote`, `CV.noteTmr`, `CV.ui.note`, and in `CAM_TEXT`
the fields `names`, `stop` (arc and flat) and `soft` (flat).
Element: `#camNote` (`.cam-note`, `role="status"`) inside `#stage`, bottom left above the hint line.

## Behaviour other modules should know

- A camera passed as `resetCam({ cam: {...} })` is used exactly as given (then held to the zoom limits).
  Built-in distances, equation-preset hints and list cameras that `resetCam()` looks up itself are scaled for
  the current field of view (they were chosen at 0.32) and, for list cameras, for a tall narrow stage. At the
  default field of view nothing changes.
- `resetCam()` in Julia mode with c on a shipped list entry now gives that entry's camera (for z^n + c, n = 2).
- The camera never auto-frames. Not built: re-framing by itself when the picture is empty or wholly off the
  frame. It needs the renderer to say "nothing was hit" (or about 100 `pick()` calls, 1 to 1.5 ms each here).
- The Kleinian start distance is still 7 for settings that are not on a list entry. The size of that solid is
  the square of the turning-out radius divided by the gap between its centre and the nearest pearl, which the
  camera cannot know without the shader's distance estimate; a port of `kde()` to JavaScript would give it.
- The negative-power distances fit what the shader draws today. If the engine changes what a negative power
  shows, check `out/fix/camera/a*.png` again and adjust the one line in `camHome`.

## How it was checked

- `sh out/fix/camera/run.sh verify`: 54 checks in page script for every defect above, plus pictures
  `out/fix/camera/a1..a6-*.png` (Reset view at n = -3, -2, -8, -1, the 2D view at -2, Mandelbulb at -3: whole
  solid in the frame each time) and `b1-limit-note.png` (refused limit, flagged box, note).
- `python out/fix/camera/real_fix.py dist/fix-camera.html`: real wheel over nine places on the stage (page
  scroll 0, zoom exact) and real clicks on Reset view, +, - in fly mode followed by W (moves, focus on the picture).
- `sh out/camera/run-tests.sh`: the module's 148 checks pass. Expectations changed on purpose in
  `out/camera/tests.js`: easing times, the key step, refused limits, the negative-power start, "Span".
- `python notes/camera_real.py dist/fix-camera.html`: 41 of 41 pass.
- `python tools/shot.py --url dist/fix-camera.html --actions tools/smoke.json`: exit 0, no console errors.
