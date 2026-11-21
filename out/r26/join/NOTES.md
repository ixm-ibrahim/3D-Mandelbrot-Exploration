# Round 26, the joiner: "A whole shape" with both parts in one page

Status: done. The joined page is `dist/r26-join.html`, built from `src/` as it stands
(`python build.py --name r26-join`, last built 01:14 on 20 Nov, after the last edit of a `src` file at 01:07).
Every check below was run by me on that build unless a line says otherwise. Nothing was published;
`squaring-lab.html`, `base*/`, `out/r25/`, `out/r21/` were not touched; `python build.py` was never run without `--name`.

The two parts fitted at the first build: the page built from `src` was byte for byte the page builder "core" had
tested against builder "three"'s last file (`dist/r26-core-three.html`), and 3D drew at once. What I then found
by using it, and changed, is in section 2. What is still wrong is in section 7.

## 1. Files

| File | What I did |
|---|---|
| `src/js/67-learn-shape.js` (931 lines) | four changes, section 2 (a) (b) (c) (e) |
| `src/js/68-learn-shape3d.js` (536 lines) | one change in `draw()` and `learnt()`, section 2 (d). The shader text, `out`, `slice`, `proj` are untouched |
| `src/js/66-learn-view.js`, `src/css/67-learn-shape.css`, `src/js/90-boot.js` | not changed (66 still differs from `base18a` by core's 7 added lines, 90-boot by its 3) |
| `dist/r26-join.html` | the joined page |
| `dist/r26-join-no3d.html` | the frozen copy plus 66, 67, the style sheet and 90-boot, without the 3D module (for check 3.8) |
| `out/r26/join/` | this file, the runner `jrun.py` (+ `j_prelude.js`), the action lists `*.js`, `smoke_join.py`, `j_compare.py`, `final.sh` (every check, in order), logs `*.log`, pictures |

Running a list again: `python out/r26/join/jrun.py go NAME.js [--size 390x800] [--theme light] [--log NAME]`
(`--from core` runs one of builder core's own lists against the joined page and keeps its pictures out of core's
folder; `--page r26-core-three` runs a list on the page as the builders left it). Every one of the 38 logs here
ends "no console errors".

## 2. What I changed, and why

**(a) Play ran on through some whole steps without resting on them** (core's clock, `learnShapeFrame`).
Found while timing Play: runs took 20.6 to 23.2 s instead of 22.85, and fewer sentences were seen. Measured with
`pace.js` (the slider read at every frame) on the builders' page: in 8 plays 15 of 120 rests lasted one to three
frames (50 ms at Normal, 17 at Fast, 117 at Slow) instead of 0.35 / 0.15 / 0.6 s; in one play 4 of 15
(`pace-before.log`). The sentence "What is left after k steps" of such a step was on show for a twentieth of a
second. Cause: on a 60 Hz screen 66 frames make exactly one step at Normal (33 at Fast, 132 at Slow); the sum of
the frames can end a rounding error short of the whole step, and the code took such a place for the step already
reached. Now the next whole step is `floor(pos) + 1`. After: 0 of 120 rests short, every play 23.1 s at Normal,
11.3 at Fast, 44.5 at Slow (`pace-after.log`); builder core's own play list now sees all 32 sentences in each of
its 24 plays (`c-play-*.log`).

**(b) The words when nothing is left** (builder three's open point: a Mandelbrot shape with a negative power is
empty from step 1, "the sentences should not promise a shape there").
Before, 3D said "What is left after 2 steps." over an empty picture, and in Both only the case "both empty" was
said. Now, per picture: "After k steps nothing is left to see: every point of the picture has been thrown out.";
between steps "Step k+1: there is nothing left to take it. Every point of the picture has already been thrown
out."; in Both with one picture empty "After k steps. Left: nothing is left to see. Right: what is left for the
one c of the diamond." (or the other way round).
A flat picture is asked itself, as before. A 3D picture is not read back, so in 3D this is said in one case only,
the one that is certain: a Mandelbrot shape whose dot at 0 is taken further than 4 from the centre by the first
step whatever c is (`learnShapeZeroOut`; so it is with a negative power). "Nothing is left to see ... every point
of the picture" replaces core's "nothing is left: every point has been thrown out", which was not true of a dust
of single points that a picture cannot show (a Julia shape with c far outside).
Checked: `gone.js` (power -2 in 2D and in 3D for five approaches, c = 7, a zoomed picture must claim nothing,
the plain power 2 says what it said, no forbidden word); pictures `gone-3d-power-2-m-01.png`, `gone-2d-power-2-j-16.png`.

**(c) After the browser takes the graphics away, the 3D picture did not come back by itself in the page.**
The module's sentence said "comes back by itself", and the module did draw again, but the page had hidden its
canvas and kept the sentence up until somebody touched the picture. The page now listens for the two events on the
module's canvas and redraws. Checked with the browser's own switch for this (`lost.js`, pictures `lost-1-gone.png`,
`lost-2-back.png`): sentence up and canvas hidden while gone; picture back, sentence gone, without a touch.

**(d) A resting 3D picture could hold the page up, and afterwards the fine picture never came back.**
What the builders' page did (`stall-before.log`, and by hand in `lost.js` on the first build): zoom in, and the
resting picture is first drawn at four buffer pixels a pixel, which took the card 0.2 to 0.5 s for the opening
approach and up to 1.3 s for "Pillow"; the module then stepped its 'still' fineness down, twice, and it never
stepped up again: for the rest of the visit every resting picture, at zoom 1 too, had one buffer pixel a pixel
(stepped edges). Two changes in the module:
  - what the last timed frame of the same scene cost says what a 'still' picture will cost (the card's time goes
    with buffer pixels times stops: `zoomcost.log`, 36 rows, 'still' at its three finenesses costs 6.5 / 3.1 / 1.3
    times the finest 'move' frame, for three approaches, three steps, four zooms). A 'still' that would take more
    than about 130 ms is drawn one or two steps coarser from the start;
  - a 'still' fineness that was stepped down comes back up once a frame takes under 45 ms.
And one in the page (67, `learnShapeSeen`): in 3D every change now counts as "something moves", a single one
too (a tick of the slider, another approach, a named c, the first notch of the wheel). The picture is drawn
'move' at once and 'still' 180 ms later, so the module always has a fresh frame to judge from. Before, such a
single change was drawn 'still' straight away.
After (`stall-after.log`, run back to back with the "before" run): opening approach, zoom 2.5: resting picture
306 ms -> 62 ms; zoom 6: 486 -> 206 ms; back at zoom 1 a finer picture returns (1293 x 767 after the first
rest in this run, 1724 x 1022 in an earlier one; the builders' page stays at 862 x 511). For "Sphere inversions,
two planes" at zoom 6 (363 -> 326 ms) and "Pillow" (485 -> 375 ms at zoom 2.5, 1543 -> 1305 ms at zoom 6)
nothing is gained: there even the coarsest 'still' is that dear. See section 7.
These two runs were made while the machine was busy; a pair made at a quieter time gave 267 -> 130 ms and
224 -> 168 ms for the opening approach and 261 / 350 ms for Pillow at zoom 6 (both at the coarsest). The logs
of that quieter pair were overwritten by the later runs; its figures are from my record of the run.
(`stall-after-busy-machine.log` is one more "after" run, from 01:36, with figures like those of the busy pair:
61, 139, 255, 347 and 1146 ms for the five resting pictures.)
Builder three's own checks still pass on the joined page with this change: `three-robust-on-join.log` (the same
buffer sizes as in their notes) and `three-slice-on-join.log` (56 cases, 3,698,744 points, 101 differ, the same
count and the same spread as theirs).

**(e)** (part of (d), in 67.) Nothing else.

Tried and NOT changed: how see-through the glass is. Six sets of the module's `look` numbers, the same eight
scenes each (`looks.js`, `looks-dark-*.png`). None read more like glass than what builder three built; theirs
shows most of the far wall through the near one. Left as built.

## 3. What was checked on the joined page

1. **Old smoke list of Version 18** (`out/r22/entry/smoke-all-steps.json`, the list behind
   `out/r22/entry/smoke-all.log` and `out/r22/me/smoke-v18.out`): **90 of 90 steps pass, 0 time-outs, no console
   error, exit 0** (`smoke-join.log`, 01:24 to 01:33; a run on the first build, before my changes, gave the same).
   87 of the 90 result lines are word for word those of the Version 18 run. The three that differ: step 2
   "wheel zoom eased 5.2 -> 5.391 -> 5.824" (then 5.423: the middle value is read two frames into an easing);
   step 24 "fly camera moved 0.700" (then 0.690: distance flown in 0.7 s of wall time); step 7 "76 dials, 25
   selects" (then 73 and 24: the three c dials and the Speed select of the whole shape exist now). Core's run on
   its own page had 5.246 and 0.696 for the first two, so they move with the clock, not with the page.
2. **One point is what it was**: core's 13 pictures of the one-point stage and transport, taken now on the
   frozen page and on the joined page: 0 pixels differ in all 13 (`c-pointbase.log`, `c-point.log`, `j_compare.py`).
3. **3D inside the page** (`hands.js`, `hands-*.png`): the module's canvas lies exactly under the page's own
   (862 x 511 both). Dragging turns (yaw -0.62 -> -2.4); the wheel zooms (1 -> 3.32); two scripted fingers pinch
   (1 -> 2, and one finger afterwards turns without a jump); arrow keys and minus; Reset view; one drag turns both
   pictures of Both; the diamond stands in both. While held, wheeled, pinched, slid or played the module is asked
   for 'move' and draws an 862 x 511 buffer; at rest 'still', 1724 x 1022 (1293 x 767 or 862 x 511 when zoomed
   in, by change (d)). In 2D and with One point its canvas is hidden.
4. **Play, all six, both themes, both sizes** (core's `play.js` on the joined page, `c-play-*.log`): Mandelbrot,
   Julia, Both x 2D, 3D play 0 to 16 at 1400 x 950 and 390 x 800, dark and light, 32 sentences seen each, no
   console error.
5. **3D against 2D and against the twin** (`cut.js`, `cut.log`), power 2, 16 steps:
   the module's slice at z = 0 (from the card) against `LEARN.shape.mask2`, 257 x 257 points, Mandelbrot shape,
   Julia c = -1, Julia rabbit, for all 21 approaches. The 17 for which the page shows the sentence about the cut:
   0 to 8 of 66,049 differ (most: Blended planes 8, Pillow 7; the 4 of c = -1 everywhere are the points that
   land exactly on the ball). The 4 without the sentence (classic, rotor, kleinsq, kleinsq2): 9,576 to 23,852
   differ. So "sentence shown" and "the card's cut equals the flat picture" go together for every approach.
   Slice at z = 0.3 against `learnShape3d.out`, 129 x 129, eight approaches: 11 of 399,384 differ.
6. **Other settings in 3D** (`odd.js`): powers 3, 2.5, -2, the modifiers, and every approach once (Both, rabbit
   c, steps 0, 3, 9): all 21 draw; the two balls at step 0 cover 42.4 to 42.6 % of the stage for each.
7. **Builder core's own lists on the joined page**: `ui`, `three`, `mask` (mask2 against out2: as in their
   notes, 1 of 160,801 for the Mandelbrot shape at power 2, else 0), `calm`, `words`, `drag`, `phone` at 390 x 800
   in both themes (no overlapping controls, stage plus transport 472 px = 58.9 % of the window): all pass
   (`c-*.log`).
8. **Without the 3D module** (`no3d.js` on `dist/r26-join-no3d.html`): 2D works, 3D shows "The 3D picture is
   missing from this copy of the page.", no error.
9. **Untried by the builders, tried now** (`phone2.js`, 390 x 800, both themes): the longest sentences, the one
   of 153 letters among them and my new ones, fit their three lines (57 of 57 px); nothing is wider than the
   window; a pinch with two scripted fingers zooms a flat picture (1 -> 2.5) and one finger then moves it.
   Still only scripted: no real phone, no real touch.

## 4. The pictures (task 5), and what is wrong in each

Whole window, 1400 x 950, dark: `pics-wide-dark-*.png`. Sheets of the stage and transport cut out of them:
`sheet-wide-dark-2d.png`, `sheet-wide-dark-3d.png`; light theme `sheet-wide-light.png`; phone `sheet-phone-dark.png`,
`sheet-phone-light.png`. I looked at every picture named here.

| Picture | What I see | What is wrong |
|---|---|---|
| `2d-m-00` | the full brass disc inside the dashed circle, axes with 2 and -2, "Mandelbrot shape / the start" | the sentence breaks so that "0." stands alone on its second line |
| `2d-m-02` | an egg pushed to the left, touching -2; the grey outline of the shape before runs just inside the dashed circle | the figure 1 on the axis is half under the egg's edge |
| `2d-m-05` | the shape with three bumps and its tip at -2, the grey outline of step 4 round it; reads as "eaten away" | nothing |
| `2d-m-16` | the Mandelbrot set with its needle to -2, a thin outline of step 15 hugging it | the outline reads as a faint halo; the fine hairs are barely there at this size |
| `2d-both-rabbit-08` | left the Mandelbrot shape with the diamond in the upper bud, right the rabbit; names in the corners | the letter c beside the diamond lies on the shape's edge |
| `3d-m-00` | a ball with a white highlight upper left, a brighter patch lower right, a firm rim; over it the dashed rim and the dotted circle of the flat plane | it reads as a polished, tinted ball rather than clear glass; the dotted circle is drawn over the picture, not seen through it |
| `3d-m-01` | the same ball (right: the first step throws nothing out), and the sentence says why | the sentence leaves "c." alone on its second line |
| `3d-m-03` | a rounded body inside the faint grey shell of the shape before, inside the dashed ball; "eaten away" is plain | the body looks like satin metal more than like glass |
| `3d-m-16` | a small flat spiky flake in the middle of the big ball | it fills a small part of the stage and looks solid; the reader has to zoom to see anything of it |
| `3d-j-basilica-fold-08` ("Sphere inversions, two planes") | a knobbly lump with spikes and small flat faces, the diamond on top of its left end | grainy, a rough nugget, not glass (builder three said so); the diamond and its c cover part of it |
| `3d-both-rabbit-05` | two panes, each with dashed ball, body and ghost shell, a diamond in each | the bodies are small and look metallic |
| `3d-both-rabbit-02.35` (between two steps) | red glass skins with the brass shape coming up inside, "step 3" in red | nothing; this is where the see-through look works best |

At 390 x 800 (`pics-phone-dark-*`, `pics-phone-light-*`; the four most telling: `2d-m-05`, `2d-both-rabbit-08`,
`3d-m-03`, `3d-both-rabbit-05`): the stage (358 x 242) and the whole transport are in the window under the lab's
title and opening text; names shortened to "Mandelbrot" and "Julia" in Both. Wrong: the pin's "UNPIN PICTURE"
button covers the upper right corner of the stage (in Both the corner of the right picture, the figure 2 at the
top of its circle beside it); in 3D Both the diamond and its c are large against the small bodies.
Light theme (`pics-wide-light-*`, `pics-phone-light-*`): the same pictures; the ghost reads as grey glass and
the body as amber, which is nearer to "see-through" than the dark theme. The highlight is weak on the light ground.

## 5. Play for real (task 6): `play.js`, `play-wide-dark.log`, 01:15 to 01:21

Play pressed at step 0, speed Normal, 1400 x 950, dark, stage 862 x 511; the time between every two frames
(requestAnimationFrame) until the steps stop at 16; each run 23.1 or 23.2 s, 1385 to 1391 frames (Pillow: 1101).

| | median | slowest | frames over 20 ms |
|---|---|---|---|
| 2D Mandelbrot shape | 16.7 ms | 17.1 ms | 0 |
| 2D Julia shape | 16.7 | 18.4 | 0 |
| 2D Both | 16.7 | 24.9 | 1 |
| 3D Mandelbrot shape (opening approach) | 16.7 | 21.9 | 1 |
| 3D Julia shape | 16.7 | 17.2 | 0 |
| 3D Both | 16.7 | 23.9 | 1 |
| 3D Both, Sphere inversions, two planes | 16.7 | 20.2 | 1 |
| 3D Both, Pillow (the dearest approach) | 16.7 | 50.3 | 293 of 1101 (mostly 33 ms: every other frame missed) |

One warning about these numbers: in this headless Chrome requestAnimationFrame keeps its beat while the
graphics card is busy, so for 3D the times between frames alone say little. Two more measures from the same list:
the page's own redraw took 1.2 to 1.5 ms (median) in 2D, slowest 10.3 ms, and 0.2 to 0.3 ms in 3D; and what the
card needed for each 3D picture while playing (one pixel read back in the task after each draw, in separate runs):
opening approach, one picture: median 8.4 to 8.7 ms, slowest 11.3; Both 11.7, slowest 14.2; two planes, Both
12.6, slowest 16.3; Pillow, Both: median 13.6, 95th of a hundred 33.3, slowest 48 ms. The resting picture after
the last step: 59 to 91 ms at 1724 x 1022.
In an earlier run on the first build one frame of 92.5 ms (and once 109 ms) turned up in the 3D Julia play; it
did not come again in three later plays. Cause not found.

## 6. Where the contract of ROUND26, section 4, is not followed to the letter

Mine:
1. `o.quality`: in 3D the page asks for 'move' at every change, a single one too, and for 'still' 180 ms later
   (contract: 'move' while playing or dragging). `LEARN.shape.state()` still answers after the 'still' picture.
2. `view.draw` with 'still' may start one or two steps coarser than its finest (1.5 or 1 buffer pixel a pixel)
   when the last timed frame of the same scene says the finest would take over about 130 ms; a 'still' fineness
   once stepped down comes back.
3. The page adds two listeners to `view.canvas` (graphics lost, graphics back).
4. `state().sentence`: new texts when a picture is empty (section 2 b).

The builders', still true of the joined page (their notes have the full lists): `mask2` and `slice` put their
outer points ON the edge of the square, with `{ centres: true }` for cell centres; "thrown out" is asked as
x² + y² > 4; `colours.warn` is the token `--bad`; a level may carry `ghost`; the page uses `learnShape3d.proj`;
`o.flat` is always false (the module can draw it, the page has no control for it); alpha is a strength, not an
opacity; `draw()` returns before the card has finished and its `ms` is the card's time of an earlier frame;
programs are built at first use (0.1 to 0.2 s); `slice()` gives null when there is no program; `dispose()` also
removes the canvas; the whole shape has a c of its own, not One point's.

## 7. What does not work, or is not known

- **A resting 3D picture of a dear approach, zoomed far in, still holds the page up**: "Sphere inversions, two
  planes" at zoom 6: 0.15 to 0.33 s per resting picture; "Pillow" at zoom 2.5: 0.26 to 0.37 s, at zoom 6: 0.35
  to 1.3 s (the low figures on a quiet machine, the high ones with other work running). The module's coarsest
  'still' (one buffer pixel a pixel) is that dear there. A fourth, coarser 'still' entry in `QUAL` would halve
  it at the price of a soft picture; I did not add one. On a sharp screen (two device pixels a pixel) the module
  keeps 'still' at two buffer pixels a pixel at every fineness, so there stepping down gains less. Not run on such
  a screen.
- The times of section 2 (d) and section 5 for the card vary up to five-fold with what else the machine is
  doing; pairs were run back to back, but treat single figures as rough.
- In 3D "nothing is left" is said only for the Mandelbrot shape with a first step that throws everything out. A
  3D Julia shape that has become empty (c = 7, say) still gets "What is left after 1 step." over an empty ball.
- The glass: at step 0 and for plain bodies it reads as a polished tinted ball, not as clear glass (dark theme
  most of all). Deep steps of the rougher rules are grainy. Both as builder three reported; not improved.
- From step 8 or so the 3D shapes fill a small part of the stage at zoom 1.
- On a phone the pin's button covers the upper right corner of the stage.
- Two sentences leave one short word alone on a second line at 1400 x 950 ("0." and "c.").
- The first 3D picture of an approach waits for its program (0.1 to 0.2 s, more when the lab builds its own
  for the solid at the same time: choosing another approach while zoomed in took 0.8 to 1.9 s in `stall-*.log`,
  before and after my changes).
- A power that needs the polar form is slow at rest in 2D (core: 150 to 200 ms), unchanged.
- Not tried by anyone: a real phone, real touch, Safari, Firefox, a sharp screen.
- The second picture "where those points are now" is not built (not in this round).

## 8. For the lead

- Decisions the builders left open: should the whole shape's c be One point's c (now separate); may the phone
  stage be 15 px higher for the whole shape than for One point (it is).
- If the hang of section 7 matters: add `{ n: 192, bis: 5, cross: 10, res: 0.75, cap: 1.0e6 }` as a fourth entry
  of `QUAL.still` in 68 (not tested), or lower the zoom limit of the 3D picture from 6 (in 67, `learnShapeZoom`
  and the pinch) to 3 or 4, where the opening approach rests in about 0.1 s.
- The module can show the cut at z = 0 inside the glass (`o.flat`); the page never asks for it. The 3D "What to
  notice" sentence talks about exactly that cut, so a tick box for it would let the reader see it. Not built:
  the round does not ask for it, and builder three looked at two pictures of it only.
- A gentle zoom as the steps go on would keep the late 3D shapes large; the module is quick enough at 'move'.
