# camera: round 10 (after the second check)

File changed: `src/js/50-camera.js`. `src/css/50-camera.css` is unchanged (byte for byte the copy in `base9m/`).
Page: `python build.py --name r10-camera --base base9m --use src/js/50-camera.js src/css/50-camera.css`.
Scripts, logs and pictures: `out/r10/camera/` (driver `drive.py`, the edits as applied `edit1.py`, the file before
them `50-camera.before.js`). This file adds to `notes/r7-camera.md`; where the two disagree this one is current.
Started 06:28, stopped at about 06:58.

## t9-camera-1: a pinch against a zoom limit said nothing (fixed)

Seen first on `dist/v9m.html` with real touch at 375 x 812, from a state with no note on show
(`drive.py pinch`, `pinch-v9m.log`, picture `v9m-pinch-near-window.png`): the distance stays at the limit and
`#camNote` stays empty at the nearest limit (0.5), at the farthest (20), in the 2D view at the closest zoom, and
with the phone on its side. 17 lines pass, 4 fail.

Cause: `camPinch()` held the value to the limits and never wrote a note; `camZoomTo()` (wheel, keys, buttons,
slider) does.

Change: `camPinch()` hands what the fingers asked for and what the limits allowed to the new `camPinchPast()`.
It adds up how far the pinch has asked to go past the limit (on a log scale) and shows the limit note once that
reaches a tenth (`CAM_PINCH_PAST`). The sentence is the one the wheel and the buttons give, with the same "left
end / right end" wording while the slider is a row: both now come from the new `camStopNote(end)`. Moving back
inside the limits pays the amount off again, and lifting a finger clears it.

Why a tenth and not the first clamped event: fingers are never steady, and two fingers that slide the picture
change their spread a little as they go. Without the threshold a user resting on a limit would get the note
while only sliding.

After, on `dist/r10-camera.html` (`pinch-r10.log`, 21 pass, 0 fail; pictures `r10-camera-pinch-near-window.png`,
`r10-camera-pinch-far-window.png`):

| Step | v9m | r10 |
|---|---|---|
| Spread fingers at the nearest limit 0.5 | 0.5, no note | 0.5, "This is the nearest the zoom may go. The box at the left end of the slider sets that limit." |
| Pinch together at the farthest limit 20 | 20, no note | 20, "This is the farthest the zoom may go. The box at the right end of the slider sets that limit." |
| 2D view, spread at the closest zoom 1 | 1, no note | 1, "This is the closest the zoom may go. The box at the left end ..." |
| Phone on its side (slider a column) | no note | "... The box at the top of the slider sets that limit." |
| Pinch from 0.8 that runs into 0.5 in one move | no note | the note |
| Pinch from 0.52 that asks for 2% past the limit | no note | no note |
| Two fingers sliding at the limit, spread wobbling by 2 px | no note | no note |
| Pinch inside the limits, pinch while flying | no note | no note |

The note goes away by itself after six seconds, as before. The + button at the same limit gives the same sentence.

## solids-7, the rest: the Kleinian start view with a trap solid on (fixed for the case in the assignment)

Seen first on `dist/v9m.html` (`drive.py kstart`, `kstart-v9m.log`, picture `v9m-k-2-start-thick0.2.png`): ring
trap, the trap is the solid, thickness 0.2, mode changed away and back. The camera stands at 7, 40 probes along
the frame hit the solid (24 at the bottom, 16 at the left), no note; Reset view then gives 9.913 with 0 hits.

What I found: round 7 wrote that the start view cannot look because the program is not ready. That is true only
the first time a Kleinian trap solid is drawn (and not even then when the renderer has prepared the program ahead
of time). In the tester's case the program is ready at the click: `pick()` sees the middle of the picture in the
same call as the click. The start view simply never looked. So two cases, one mechanism:

- `resetCam()` now leaves a look waiting (`camLookLater()`) when the mode is Kleinian, the 3D picture is on show,
  a trap is the solid or is added to it, and the camera was not given by the caller.
- `camLookTick()` runs first on a timer of 0 ms, so after the caller has finished changing the settings and
  before the next frame is drawn. If `pick()` can see the picture (`camCanSee()`), it runs `camStepBack()`, the
  same look Reset view uses. If not, it asks again on every frame (or every 250 ms while frames are paused),
  for at most 15 s (`CAM_LOOK_WAIT`).
- The look takes place only while the camera is still exactly as the start view left it: same yaw, pitch,
  distance, target, same camera kind, same zoom limits, still Kleinian, no pointer down on the picture, no key
  held, no zoom easing, the slider not held. Anything else drops the look for good. So nothing moves under a
  finger, and nothing moves after the user has moved the camera.
- `resetView()` (the button) is as before when the picture can be seen. Pressed while the picture is still being
  prepared it used to see nothing and do nothing; now the waiting look does the job once the picture is ready.

After, on `dist/r10-camera.html` (`kstart-r10.log`, 11 pass, 0 fail; pictures `r10-camera-k-*.png`):

| Case | v9m | r10 |
|---|---|---|
| Tester's case: thickness 0.2, mode away and back | 7, 40 probes at the frame, no note | 9.913, 0 probes; first frame after the click already shows 9.913 |
| Then Reset view | 9.913 | 9.913 (start view and Reset view agree) |
| Program not prepared at the click (fresh page, warm-up off), hands off | not run on this case (it never looks) | 7 at the click, `pick()` could see after 40 ms, 9.913 from 160 ms, 0 probes |
| Same, a drag of 50 px begun straight after the click | n/a | yaw turned by the drag, distance 7, not moved in the 3 s after |
| Same, a press held on the picture for 2.5 s, then released | n/a | distance 7 throughout and after |
| Same, one wheel notch straight after the click | 6.25 | 6.25 (the user's zoom, nothing stepped back) |
| Same, Reset view pressed straight after the click | n/a | 9.913, 0 probes |
| Example "Rings in the lace" (camera given) | 7 | 7, unchanged a second later |
| No trap solid | 7 | 7 |

Measured: all of the above. Only reasoned: that a slow machine behaves the same (here the program was ready 40 ms
after the click, so the wait was short); a real phone.

Not done, on purpose:
- Typing a trap dial still does not move the camera or show a word (round 7's choice; the tester lists it as
  still not good; it is not in this round's assignment).
- Mandelbrot and Julia start views are untouched: they have the estimate, and the look is not left waiting there.
- If the 2D view is up when the mode changes, no look is left waiting; the 3D camera stands at 7 until Reset view.
- The look probes the frame about every 30 px, as in round 7, so a sliver can still slip through.

## What did not change (recorded before the edit, compared after)

`drive.py base` on both pages at 1400 x 950, 1024 x 768 and 375 x 812 (touch): the boxes of all the picture's
controls (switch, both limit boxes, rail, thumb, value, the three buttons, the axes, the zoom container), the
share of the picture they cover, the hint, the classes, and the camera and the 2D view for the opening view, the
start views of Julia, Kleinian and Mandelbrot, the 2D view, the fly camera and Reset view. 735 values compared
between `base-v9m.json` and `base-r10-camera.json`: 0 differ. Start distances, both pages: 5.2 / 4.8 / 7 at 1400,
5.2 / 5.3798 / 7.8455 at 1024, 5.2 / 4.8648 / 7.0944 at 375 (Mandelbrot / Julia / Kleinian).

Smoke test: `tools/shot.py --url dist/r10-camera.html --actions tools/smoke-v9m.json`, log
`out/r10/camera/smoke-final.log`: all 52 steps ran, exit 0, no console errors (run once, on the final page).

## Names added or changed (all in `50-camera.js`)

- `CAM_PINCH_PAST` (0.1), `CAM_LOOK_WAIT` (15000).
- `CV.past` (how far the pinch under way has asked past a limit), `CV.look` (the waiting look, or null).
- `camStopNote(end)`: the limit note, taken out of `camZoomTo()` unchanged so the pinch can use it.
- `camPinchPast(asked, v, f)`.
- `camCanSee()`, `camLookLater()`, `camLookDrop()`, `camLookTick()`.
- `camHome()` now also returns `given` (true when the camera was used exactly as given).
- `resetCam()` drops any waiting look and may leave a new one; `resetView()` drops it when the picture can be seen.
- The pointer-up handler of the picture sets `CV.past = 0`.

No id, label, class or public function changed. Nothing new on `window.squaringLab`.

## What the person joining the files must know

- Take `src/js/50-camera.js` as a whole. The stylesheet needs no change.
- `camCanSee()` reads two names of `40-render.js` that are not in the contract: `sceneNow()` and the map `progs`
  (an entry's `state === 'ready'`), the same test `pick()` makes. Both are asked for with `typeof` first. If the
  engine engineer renames them, nothing breaks: the camera then falls back on `renderIdle()`, and the look takes
  place when the picture is finished instead of when it can first be seen.
- The look costs what Reset view costs with a trap solid on show (about 100 `pick()` calls, 60 to 270 ms in
  round 7), once per Kleinian start view with a trap solid, and nothing otherwise.
- When the program has to be prepared, the picture can show the camera at 7 for a frame or two (as a preview)
  before it stands back: the renderer draws its first preview in the same call that finds the program ready.
- New example buttons: a camera passed as `resetCam({ cam })` is still used as given and gets no look.
