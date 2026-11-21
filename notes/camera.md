# camera: what was built, the names, and what the UI integrator must wire

Files: `src/js/50-camera.js` (rewritten), `src/css/50-camera.css` (new). Nothing else in `src/` was touched.

## What it does now

**One camera description for every mode.** `cam { yaw, pitch, dist, target }` is still the arcball. Fly mode
keeps the same four numbers and only changes what input does to them: looking around turns about the eye
(the target is carried along, `dist` ahead), and movement shifts eye and target together. So `basis()` never
looks at the mode, the renderer needs no change, and switching modes cannot move the picture (checked: the
eye and view direction are bit-identical before and after). The 2D view uses `S.v2 { x, y, h }`.

**Smooth zoom (item 4).** The wheel, the zoom buttons, the plus and minus keys and the stage slider all set a
goal; a frame loop eases the distance toward it on a log scale with a 35 ms time constant, so 97% of the
way is covered in 120 ms whatever the frame rate, it never passes the goal, and it lands on it exactly.
One mouse-wheel notch (100 px, or 3 lines in Firefox) is 12%. Trackpads send many small deltas and simply
add up; a trackpad pinch (wheel + ctrlKey) counts eight times; one event is capped at three notches. The loop
calls `touch()` every frame while moving and stops when nothing moves. Measured with a real wheel in headless
Chrome: five notches spread over 32 frames, the largest single frame being 9.9% of the whole change (the old
code did each notch as one 16% jump). Someone with "reduce motion" set gets the new view at once.

**Camera modes (item 7).** A two-part switch "Arcball | Fly" sits inside the stage, top right, under the busy
indicator's place. Fly: drag looks around (drag right looks right, drag down looks down, the eye stays put);
W A S D and the arrow keys move along the view and sideways; E and Space go up, Q and Shift go down (world
z); movement continues while keys are held, eases in and out over about 70 ms, and is `S.view.speed` scene
units per second. The wheel changes the speed by 12% per notch (up is faster). The stage slider becomes a
speed slider (fast at the top). The + and − stage buttons and keys step forward and back. Pressing F on the
focused stage also switches modes. Clicking the switch with a pointer hands the keyboard to the canvas, so
W A S D work straight away. Leaving fly mode picks the surface point in the middle of the picture as the new
pivot (falls back to a point `dist` ahead). Entering fly mode keeps `S.view.speed` unless it is absurd for
the scale (faster than the pivot distance per second, or slower than a fortieth of it), in which case it
starts at a quarter of the pivot distance per second.

**Zoom slider and limits (item 8).** A vertical slider on the stage's right edge: top is near, bottom is far,
log scale between `S.view.zmin` and `S.view.zmax`, a tick at every power of ten (a longer one at 1), the
current value written beside the thumb. Drag it, click it, or use Arrow/Page/Home/End on it. A small text
box at each end holds the limit: type a number, Enter or leaving the box commits, Escape restores, nonsense
restores and flags the box for a moment, a decimal comma, spaces, a unicode minus and exponents are read.
Hard ranges: nearest 0.00001 to 500, farthest 0.002 to 1000; the two are kept a factor 2 apart; when a limit
moves past the camera, the camera eases back inside. The default farthest distance is now 60 (was 24) and is
not tied to the drawing radius.

**2D view (item 12).** While `S.flat` is true: drag slides the picture (the grabbed point stays under the
pointer), the wheel and a pinch zoom `S.v2.h` about the cursor (the point under the cursor stays put at every
frame of the easing), double-click centres a point, arrow keys slide, plus and minus zoom, and the same
slider shows the height between `S.v2.hmin` and `S.v2.hmax` (boxes edit those). The camera switch is hidden
and arcball/fly input is off; the triad shows x right, y up, z toward the viewer. Dragging the small
"one step" figure still turns the 3D camera (it calls `viewChanged()` instead of `touch()` while flat).

**Touch.** One finger turns (or slides in 2D); two fingers pinch-zoom about the point between them and slide,
keeping each finger on the spot it touched; a double-tap is recognised by the camera itself (not every touch
browser sends `dblclick`) and is never answered twice. In fly mode a pinch moves forward or back and a
two-finger drag moves sideways. On touch screens the hint uses finger wording and the targets are bigger.

**Reset.** `resetCam(preset?)` restores yaw, pitch, distance and target for the mode (Mandelbrot, Julia,
Kleinian), sets the 2D view to the same framing (centre = target, height = 2 · dist · fov), cancels any
motion, and keeps the fly/arcball choice. The Mandelbrot off-centre framing now applies only for n between
1.5 and 2.5 (it used to apply to every n below 2.5, which would have been wrong for negative powers).

## Names added (all in `50-camera.js`)

Public, for other modules:
- `setCamMode(fly)`: switch arcball (false) / fly (true); keeps eye and direction; picks the pivot on the way back.
- `resetZoomLimits()`: zoom limits back to defaults (3D and 2D), view pulled inside them.
- `resetCam(preset?)`: as before, plus: `preset.cam { yaw, pitch, dist, target }` is applied in any mode
  (pitch held to ±1.5); an equation preset `{ eq, target, dist }` behaves as before (ignored in Kleinian mode,
  target ignored in Julia mode).
- `CAM_DEF { zmin: 0.005, zmax: 60, hmin: 0.0005, hmax: 40 }`: default limits.
- `CAM_LIM { zmin, zmax, hmin, hmax, speed }`: hard `[lo, hi]` ranges; `CAM_LIM.speed` is `[0.001, 100]`.
- Unchanged contract names: `cam`, `basis()`, `clampDist(d)`, `drawTriad()`, `bindView()`.

State created or changed (in `camInit`, run by the first `bindView()` or `resetCam()`):
- `S.v2.hmin` (0.0005), `S.v2.hmax` (40): zoom limits of the 2D view (smallest and largest visible height).
- `S.view.zmin`, `S.view.zmax` are set to `CAM_DEF` (0.005 and 60), replacing core's 24.
- `stage.dataset.cam` is `arc`, `fly` or `flat` (a CSS hook).

Private (prefixed, do not call): `CV` (bookkeeping: `ptr, keys, vel, goal, raf, ui, ...`), `CAM_EASE`,
`CAM_NOTCH`, `CAM_KEYS`, `CAM_TEXT`, `camInit camKind camOff camChan camT camAtT camLive camAim camFmt
camFlatUv camGoal camZoomTo camZoomBy camStep camIntoLimits camSpeedChanged camWake camNext camEase camTick
camTurn camSlide camFlatShift camFlatDrag camPinch camBindDrag camWheel camDblClick camKeyDown camParse
camSetLimit camLimitBox camBuildUi camSync`.
Removed (were never in the contract): `pointers`, `orbit`, `pan`, `bindDrag`.

Elements created inside `#stage` by `bindView()`: `#camMode` (`.cam-mode`, with buttons `#camArc`, `#camFly`),
`#camZoom` (`.cam-zoom`, with `#camEndA`, `#camNear`, `#camRail` > `#camTicks`, `#camThumb` > `#camVal`,
`#camFar`, `#camEndB`). CSS classes: `cam-mode cam-zoom cam-end cam-lim cam-rail cam-tick is-one cam-thumb cam-val`.

## What the UI integrator must do

1. Keep calling `bindView()` once from `boot()`, after `initState()` and `initGL()` and after the stage
   markup exists. It needs: `#stage`, `#view`, `.hint` inside the stage (its text is replaced by the camera),
   `#zoomIn`, `#zoomOut`, `#reset`, `#step3d`, and the triad's `#ax0..2` / `#at0..2`. Each is optional except
   stage and canvas (a missing one is skipped). `bindView()` registers `drawTriad` and its overlay sync on
   `hooks.view` itself: remove `hooks.view.push(drawTriad, ...)` from `boot()` (leaving it is harmless).
2. 2D view checkbox: set `S.flat` and call `touch()` (or `refresh`). Nothing else: the camera notices on the
   next frame, swaps hint, slider and input. `resetCam()` already keeps `S.v2` framed, so no extra reset.
3. View section, fly speed dial: value `S.view.speed`, `lo: CAM_LIM.speed[0]`, `hi: CAM_LIM.speed[1]`
   (0.001 to 100; a slider range of about 0.01 to 10 with a log feel is fine). Its setter should call
   `viewChanged()` so the stage slider follows (no redraw is needed). The camera calls `syncControls()` about
   150 ms after the wheel or the stage slider changed the speed, so the dial follows too.
4. If the sidebar gets its own camera-mode control, call `setCamMode(bool)`; do not write `S.view.fly`
   directly (it works, but skips the pivot pick and the speed check).
5. "Reset this section" for View: call `resetZoomLimits()` besides `resetGroup(...)`. The limits themselves
   live only on the stage slider, as decided.
6. Presets: `resetCam(preset); touch();` with the whole Kleinian or Julia preset object (it reads
   `preset.cam`). Equation presets as now.
7. `S.view.fov` and `S.view.bound` dials just call `touch()`. The far limit is independent of the bound.
8. Do not put other overlays in the stage's right-hand column: busy indicator at top 10 px, camera switch at
   top 46 px, slider from top 82 px to bottom 58 px, 56 px wide, 10 px from the edge.
9. Optional, for running my checks on the final page: expose `basis, resetCam, resetZoomLimits, pick, hooks,
   CV, setCamMode, viewChanged, clampDist, camChan` on `window.squaringLab` (see `out/camera/boot-test.js`).
10. Small thing outside my files: in the 2D view the triad (white lines, `00-base.css`) can sit on the pale
    interior of a set and vanish. A rim would fix it, e.g. `.triad line, .triad text { paint-order: stroke; }`
    with a `--stage` stroke behind. My own overlays carry such a rim.

Wording used on the stage (sentence case, no flourishes): switch "Arcball" / "Fly"; slider ends "near" /
"far", "in" / "out" (2D), "fast" / "slow" (fly); hints
- arcball: "Drag to turn. Scroll to zoom. Shift-drag to slide. Double-click a spot to move in on it."
- fly: "Drag to look around. W A S D or the arrow keys move, Q and E go down and up. Scroll changes the speed."
- 2D: "Drag to slide the picture. Scroll to zoom. Double-click a spot to centre it."
(touch variants exist for each; see `CAM_TEXT`).

## How it was checked

- `sh out/camera/run-tests.sh`: builds `dist/camera-test.html` (baseline + camera + test boot) and runs
  `out/camera/tests.js` through `tools/shot.py` (converted by `notes/camera_steps.py`, summarised by
  `notes/camera_report.py`). 143 checks in 8 steps, all pass, no console errors: easing trace (no overshoot,
  97% at about 120 ms, exact landing), wheel kinds and caps, limits clamp, slider and limit boxes, arcball
  drags and keys, fly (position, speed, look, keys, wheel, switching), 2D (pan, anchored zoom, pinch, centre,
  slider, limits), reset in every mode, double-click and double-tap.
- `python notes/camera_real.py`: the same page driven with real, trusted input through the DevTools protocol
  (mouse wheel, drags that leave the stage, keyboard focus, Tab order and focus rings, typing and Tab in the
  limit boxes, native double-click, emulated touch on a tablet and a 375 px phone). 41 checks, all pass
  (log: `out/camera/real.log`).
- The same 143 checks also pass on a build that swaps in everyone's current `src/` modules (approaches,
  formula, colour, shaders, render, measure, dial) under the baseline UI: `out/camera/tests-mix.log`. With
  the others' shader and renderer the 2D view draws and pans/zooms correctly: `out/camera/31..34-mix-*.png`.
- `tools/smoke.json` (copied to `out/camera/smoke.json` with its own output paths) runs clean on the
  baseline + camera build; pictures in `out/camera/smoke-*.png`.
- Screenshots: `out/camera/10-arcball.png`, `11-fly.png`, `12-zoomed-in.png`, `13-far.png` (far limit 400,
  flagged box), `14-flat-overlay.png`, `20-phone-*.png`, `21-light-*.png`, `35-mix-klein-fly.png`,
  `42-ring-rail.png`, `44-tablet-fly.png`, `45-phone-touch.png`.

Testing notes for whoever reruns this: in headless Chrome wheel and mouse events carry whole-number client
coordinates and the window has no focus (so `blur()` fires nothing); an instant emulated swipe is read as a
fling and the next tap is swallowed. The test scripts allow for all three.

## Known limits

- Fly mode has no collision and no distance limit: you can fly through the surface or far away ("Reset
  view" brings you back). The zoom limits apply to the arcball and the 2D view only.
- No pointer lock (the artifact frame would not grant it): looking around needs a drag.
- 3D wheel zoom moves toward the pivot, not toward the cursor (double-click sets the pivot). 2D zoom is about
  the cursor.
- 2D zoom is bounded by single-precision floats in the shader: below a height of about 0.0005 the picture
  turns blocky, which is why that is the default smallest height (the box lets you go lower).
- Pinch in 3D keeps the pivot centred (zoom plus slide), so fingers track the surface only approximately; in
  2D they track exactly.
- Touch was checked with Chrome's touch emulation only, not on a real phone or in Safari.
