# camera: fix pass 7 (after the check of Version 6)

Files changed: `src/js/50-camera.js`, `src/css/50-camera.css`. Nothing else in `src/` was touched.
Page: `python build.py --name r7-camera --base base6 --use src/js/50-camera.js src/css/50-camera.css`.
Scripts, logs and pictures: `out/r7/camera/` (driver `drive.py`, step files written by `gen.py`, `*.log`, `*.png`).
This file adds to `notes/fix-camera.md`; where the two disagree this one is current.

## What changed, by defect

| Defect | Change |
|---|---|
| layout-1 (major) | On a stage narrower than 520 px (`CAM_ROW`) the zoom slider is no longer a column on the picture. `camPlace()` moves `#camZoom` out of `#stage` to just after it (so it sits between the picture and the hint) and marks it `.is-row`: nearest limit with its word above it, the slider with near at the left, farthest limit. The Arcball / Fly switch goes to the bottom left corner of the picture (`.cam-mode.is-low`), level with the three buttons, where the hint is on a wide stage. On a wider stage everything is where it was: the boxes of all the picture's controls at 1400 x 950 and 1024 x 768 are identical to Version 6. A `ResizeObserver` on the stage re-runs `camPlace()`, so turning a phone or resizing a window switches layouts both ways. |
| words-2 | Fixed by the same change: nothing of the zoom lies over the picture on a narrow stage, and the switch is out of the band the solids use. Measured with pick probes under every control that still lies over the picture (triad, switch, three buttons): no hit for the opening view, Figure 4, the three twins, the Kleinian start and a framed Julia entry, at 375 x 812 with touch and without. No camera distance was changed. |
| layout-5 | `camBuildUi()` inserts the switch and the zoom before `.stage-bar` instead of appending them after it. Tab order at 1400 x 950 is now switch, nearest limit, slider, farthest limit, then the three buttons. Because the overlays no longer follow `#glfail` in the page, hiding them while the picture cannot be made is done by a `MutationObserver` on `#glfail` that sets the class `cam-gone` (it used to be a sibling rule in the CSS). |
| solids-7 | `camHome()` (so the start view and Reset view) stands back for a trap that is the solid or is added to it: `camTrapBall()` estimates a ball that holds it from the trap's centre, radius and thickness, `camTrapDist()` turns that into a distance that fits the picture in height and width. Cameras passed in as given (`resetCam({ cam })`, so the page's Frame it and example buttons) are not touched. Reset view also looks at the picture (`camStepBack()`): while pick probes along the four edges hit the solid the camera steps back, to at most twice the distance, and if the solid still runs out a note says so. The dials do not move the camera (measured: the distance is unchanged after typing a radius). |

## The estimate for a trap solid (what is measured, what is reasoned)

- The trap shape reaches radius + thickness from its centre (a point trap: thickness only). Reasoned from the
  colour module's notes ("a line stops at the trap radius", "each plane is a disc of that radius").
- Julia mode, plain rule `z^n + c`, at least one step skipped: the solid is the trap pulled back through one
  step, a ball of radius (reach + |c|)^(1/n). Measured on c = -1, shell: radius 1.5 gives distance 5.66, radius 2
  gives 6.19, and the egg is whole in both pictures; radius 0.7 leaves the start view at 4.8 as before.
- Mandelbrot mode: with fewer skipped steps than `CAM_TRAP_SKIP_M` (2) the trap shape itself is in the solid
  (measured: shell, skip 1, a ball; distance 5.85, radius 2 gives 9.39, both whole). From 2 skipped steps on, for
  power 2, the solid lies within sqrt(reach + 1/4) of the point -1/2 (measured: shell and cross at skip 2 stay
  at 5.2 and are whole).
- Kleinian mode: no rule; only the trap's own size counts, which changes nothing at ordinary values. Reset view's
  look at the picture does the work there (thickness 0.2: 7 becomes 9.91 and the solid is whole; radius 1.6: the
  sheets have no end, the camera stops at 14 and the note shows).
- Any other equation: both sizes count (the larger wins). Not measured.
- Not done: the start view after a change of mode in Kleinian mode does not look at the picture (the program for
  the new picture is not ready at that moment, so `pick()` has nothing to read). Reset view does.

## Names added or changed (all in `50-camera.js` unless said)

- `CAM_ROW` (520): stage width in pixels below which the zoom is a row under the picture.
- `CAM_TRAP_SKIP_M` (2): Mandelbrot mode, the number of skipped steps from which the trap shape itself is no
  longer part of a trap solid. **If the colour module changes what "Orbit steps skipped" counts in Mandelbrot
  mode (the plan says today's 2 becomes 1), set this to 1.**
- `CAM_TRAP_OUT`: the sentence shown when a trap solid still runs out of the picture after Reset view.
- `camTrapBall(target)`, `camTrapDist(target)`, `camStepBack()`: see above. They read `S.colour.solid`, `.trap`,
  `.radius`, `.thick`, `.skip`, `.tx`, `.ty`, `.tz`, the constant `TRAP` (`TRAP.tones`, `TRAP.point`), `S.c`,
  `S.n`, `S.eq`, `S.mode`. Every one is guarded: without `S.colour` or `TRAP` no trap solid is assumed.
- `camPlace()`: column or row, by the stage's width. `CV.ui.row` (true while it is a row), `CV.ui.zoom`,
  `CV.ui.bar`.
- Classes: `.cam-zoom.is-row` (the zoom as a row, outside the stage), `.cam-mode.is-low` (the switch in the
  bottom left corner), `.cam-gone` (overlay hidden while `#glfail` shows).
- `#camRail` has `aria-orientation="horizontal"` while it is a row, and takes the left and right arrow keys as
  well as up and down (left and up move in).
- As a row the thumb and the ticks are placed with `style.left`, as a column with `style.top` as before.
- The sentences for "this is the nearest / farthest the zoom may go" say "the box at the left end / right end of
  the slider" while the slider is a row.
- `resetView()` now also calls `camStepBack()`.

Ids, labels and the public functions are unchanged. `#camZoom` is a child of `.bench-main`, not of `#stage`,
while the stage is narrower than 520 px.

## What the person joining the files must know

- The row adds 54 px under the picture at phone width. At 375 x 812 the top row of the controls ("2D view",
  "Collapse all") now starts at about y = 800 instead of 750, so it is no longer on the first screen. If that
  matters, the stage height for narrow screens (`.stage` in the `max-width: 620px` block of `00-base.css`, the
  page engineer's) can give the 54 px back, for example 34vh in place of 40vh.
- `presetNarrowK()` in `75-presets.js` says it backs off so that wide sets are not "hidden behind the zoom
  slider". On a narrow stage there is no slider on the picture any more; the factor 1.2 still keeps wide
  Kleinian sets clear of the sides, so it can stay, but the comment is out of date.
- New example buttons for trap solids: pass the camera as `resetCam({ cam })` and it is used as given; or call
  the Reset view path (`resetView()` is not on `window.squaringLab`; the button `#reset` is) to get the estimate
  and the look at the picture.
- Reset view with a trap solid on show costs about 100 `pick()` calls: 60 to 270 ms here in fifteen presses, and
  once 734 ms while other jobs shared the GPU. Without a trap solid it costs nothing new.
- The look at the picture probes the edges about every 30 px, 2 px in from the frame. A piece narrower than that
  can slip through: Kleinian ring with the trap centre at x 0.6 ends at distance 9.91 with a sliver still
  touching the left edge and no note (`r7-solids.log`, step 17).

## How it was checked (all on `dist/r7-camera.html`, same scripts first run on `dist/v6.html`)

- `drive.py --size 375x812 --phone --actions phone.json`: boxes, share of the picture covered (21.8 % before,
  14.8 % after; 2D view 17.4 % before, 10.7 % after), pick probes under every control. Logs `v6-phone.log`,
  `r7-phone.log`; pictures `sheet-phone-before-after.png`, `r7-phone-open-window.png`.
- `finger.json` (real touch): drag and tap on the slider row, typing in both limit boxes, a refused limit, the
  note at the nearest limit, Fly and Arcball taps, the speed slider, Tab order, the same page made 1400 wide and
  narrow again. `r7-finger.log`.
- `more-fine.json` at 375 x 812 without touch and `more-light.json` with touch in the light theme: Figure 4, the
  three twins, a framed Julia entry, `#glfail` shown and hidden.
- `tab.json` at 1400 x 950 (real Tab presses): `v6-tab.log`, `r7-tab.log`.
- `desk.json` at 1400 x 950 and 1024 x 768: the boxes of all the picture's controls and the cover are identical
  to Version 6 (`desk-*.log`).
- `solids.json` and `solids2.json`: the tester's trap solids, before and after (`sheet-v6-solids.png`,
  `sheet-r7-solids.png`, `sheet-r7b-solids.png`).
- `tools/shot.py --actions tools/smoke-v6.json`: exit 0, no console errors (`smoke-final.log`).
- Not run: `notes/camera_real.py` and `out/camera/tests.js` (they need a page built with the camera's test
  boot); other browsers; a real phone.
