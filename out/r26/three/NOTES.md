# Round 26, builder "three": the see-through 3D picture

File owned: `src/js/68-learn-shape3d.js` (one top-level name, `learnShape3d`). Nothing else in `src/` was touched.
Test page: `dist/r26-three.html` (`python build.py --name r26-three --base base18a --use src/js/68-learn-shape3d.js src/js/90-boot.js`).
Everything below was run on the final file (19 Nov, after the last edit), in headless Chrome on this machine:
Intel Arc Pro 140T through Direct3D 11. Nothing was tried on a phone, in Safari or in Firefox.

## 1. What was built

`learnShape3d.make()` gives a view with a canvas and a WebGL2 context of its own. `view.draw(o)` draws one or two
panes; `view.slice(...)` asks the same program for the step at which each point of a flat square is thrown out;
`learnShape3d.out(...)` is the JavaScript twin from `MATH` / `CARRY`; `ok()` / `note()` say whether the last program
built.

How a picture is made:

- One program per approach serves both kinds (`uJulia` says which, pane by pane) and all dials and powers (they are
  uniforms). There are two programs per approach at most: one for the power 2 (the equation is compiled to `sqr(z) + c`,
  as the solid's is) and one for every other power (`pw(z, uPow) + c`).
- The rule is the lab's own text: the approach's `glsl` as it stands, and `f()` and `start()` cut out of `GL_ORBIT`
  by a search (so the modifiers and the carry hook come with them), with `compileFormula('z^n + c')` and
  `compileFormula('0')` put in. `cmap`, `zmap` (APR_ZMAP) and `carStart` / `carStep` (APR_CARRY) are called where
  the solid calls them. If a later edit of `30-shaders.js` moves those lines out of reach of the search, a copy of
  today's text is used instead (checked: the search finds them in `base18a` and in `src`).
- Each pixel is one straight ray through the big ball (flat camera, no perspective, the same camera as the Learn
  tab's space view). The ray is walked in even steps; at each stop the step at which the point is thrown out is
  worked out. Where two stops lie on different sides of a wanted skin the crossing is narrowed by halving (7 times
  for 'still'), and the slope is read from four points around it, each three quarters of a CSS pixel away.
- The skins a ray meets are laid over each other nearest first. A skin is most see-through where it faces the eye
  and nearly opaque at its rim; the near side of a body carries the highlight, the far side shows brightest where
  the light falls on it from inside, and the stretch of a ray inside a body adds a little of its colour.
- `main()` is one loop around ONE call of the orbit function, whose loop holds ONE call of the lab's `f()`. The walk,
  the halving, the four slope points and the flat cut are states of that one loop.

## 2. Every approach builds and draws both kinds

From `all21.log` (`a-all21.json`, `t3_all21.js`). "drawn" is the share of a 600 x 450 picture that is not background,
for the shape after 3 steps (m: Mandelbrot shape, j: Julia shape with c = -1). The ball at step 0 covers 37.7 % for
every approach, which is the disc it should be (pi * 180^2 / (600 * 450)). No console errors.

| approach | id | builds, power 2 / other | build ms, 2 / other | first picture ms, 2 / other | drawn % m, j (power 2) | drawn % m, j (power 3) | odd |
|---|---|---|---|---|---|---|---|
| Sphere inversions, one plane | mercator | yes / yes | 140 / 103 | 165 / 117 | 7.63, 9.44 | 6.54, 2.77 | its power-2 build, the first of every run, took 94 to 144 ms over six runs |
| Sphere inversions, two planes | fold | yes / yes | 153 / 140 | 175 / 164 | 10.92, 8.01 | 9.84, 7.33 | |
| Quaternion square (Lathe) | lathe | yes / yes | 91 / 101 | 110 / 119 | 12.34, 7.78 | 13.5, 10.66 | |
| Quaternion square, twisted | tilt | yes / yes | 86 / 99 | 97 / 115 | 12.77, 9.21 | 10.65, 6.96 | |
| Mandelbulb | bulb | yes / yes | 105 / 96 | 121 / 114 | 8.32, 11.88 | 10, 8.22 | |
| Mandelbulb, classic | classic | yes / yes | 96 / 96 | 115 / 114 | 12.08, 9.21 | 12.3, 10.25 | |
| Split | split | yes / yes | 85 / 92 | 96 / 107 | 18.33, 18.42 | 11.08, 12.84 | the Julia shape is a column: the flat shape times a stretch of height (as the rule says it must be) |
| Blended planes | softfold | yes / yes | 152 / 196 | 176 / 225 | 11.87, 11.76 | 9.8, 6.93 | second dearest to draw |
| Bulbs about the axis | axisbulb | yes / yes | 112 / 129 | 133 / 152 | 12.33, 7.78 | 13.32, 10.66 | |
| Pillow | pillow | yes / yes | 166 / 206 | 197 / 249 | 13.43, 9.28 | 12.72, 7.88 | dearest to draw |
| Quaternions, 4D (slices) | quat4 | yes / yes | 100 / 123 | 121 / 140 | 12.34, 7.78 | 13.5, 10.66 | the only one with `zmap`; reads `uJulia` itself |
| Rotor square (geometric algebra) | rotor | yes / yes | 95 / 107 | 107 / 125 | 12.38, 11.96 | 12, 8.11 | |
| Rotor square with a frame | rotorframe | yes / yes | 91 / 101 | 103 / 122 | 11.06, 14.65 | 10.61, 10.55 | |
| Kleinian squaring, one plane | kleinsq | yes / yes | 106 / 100 | 123 / 118 | 7.6, 9.07 | 7.48, 2.8 | |
| Kleinian squaring, two planes | kleinsq2 | yes / yes | 103 / 108 | 121 / 130 | 11.69, 7.87 | 12.13, 4.84 | |
| Square pillow | sqpillow | yes / yes | 138 / 158 | 158 / 179 | 17.02, 9.82 | 11.77, 9.82 | |
| Turning plane, away | turnaway | yes / yes | 112 / 145 | 131 / 167 | 11.7, 9.22 | 10.91, 6.97 | |
| Turning plane, along | turnalong | yes / yes | 109 / 150 | 129 / 172 | 12.15, 7.74 | 12.25, 9.62 | |
| Wind, then square | windsq | yes / yes | 124 / 191 | 139 / 220 | 18.88, 9.29 | 13.41, 7.36 | |
| Along once, then one plane | alongonce | yes / yes | 123 / 168 | 147 / 192 | 12.59, 8.66 | 12.47, 8.03 | carries a count (APR_CARRY) |
| Pulled plane | pulledplane | yes / yes | 188 / 205 | 218 / 237 | 11.17, 7.76 | 10.39, 7.96 | carries the plane (APR_CARRY) |

Build: 85 to 206 ms. First picture (build, first draw, and the wait for the card): 96 to 249 ms in this run, up to
341 ms in an earlier one. No approach fails. The path for one that does was tried with an approach broken on
purpose, added to the list for the length of the test (`a-fail.json`, log `fail-run.log`): `draw` gives ok false and
the note "The 3D picture could not be prepared for “Broken on purpose” on this device.", `ok()` is false, `note()`
says the same, `slice` gives null, the reason is written to the console once (not at every frame), and after going
back to a sound approach `ok()` is true again.

## 3. slice against out, point for point

`a-slice.json` / `t3_slice.js`, log `slice-required.log`, the full table in `tables.txt`. Grid: 257 x 257 points on
|x|, |y| <= 2 (spacing 1/64, exact in both arithmetics), 16 steps. For each differing point the script looks for the
nearest skin that explains the difference: the smallest tried distance h at which the card's value lies between the
least and the greatest value JavaScript finds at the point and at its 26 neighbours h away.

Required set: mercator, fold, lathe, turnalong, alongonce, pulledplane, bulb, split; Mandelbrot shape, Julia shape
with c = -1 and with the rabbit c; z = 0 and z = 0.3; power 2. And power 3 for mercator and lathe (Mandelbrot shape,
Julia shape with c = (-0.3, 0.2, 0.1)).

| approach | power | differ, per case (m, j c=-1, j rabbit at z = 0; the same at z = 0.3) | of |
|---|---|---|---|
| mercator | 2 | 1, 4, 0; 0, 0, 0 | 66049 each |
| fold | 2 | 1, 4, 0; 4, 0, 4 | 66049 each |
| lathe | 2 | 1, 4, 0; 0, 0, 0 | 66049 each |
| turnalong | 2 | 0, 4, 0; 8, 0, 2 | 66049 each |
| alongonce | 2 | 0, 4, 0; 0, 2, 3 | 66049 each |
| pulledplane | 2 | 0, 4, 0; 0, 0, 11 | 66049 each |
| bulb | 2 | 1, 4, 0; 0, 0, 0 | 66049 each |
| split | 2 | 1, 4, 0; 0, 0, 0 | 66049 each |
| mercator | 3 | m 12, j 1 at z = 0; m 0, j 0 at z = 0.3 | 66049 each |
| lathe | 3 | m 12, j 0 at z = 0; m 4, j 1 at z = 0.3 | 66049 each |

56 cases, 3 698 744 points, **101 differ (0.0027 %)**. Distance to the skin that explains each: 5 within 1e-9,
40 within 1e-7, 19 within 1e-6, 32 within 1e-5, 4 within 3e-5, 1 within 1e-4. None further. (A pixel of a 600 x 450
picture is 1.1e-2 wide.)

Where the differing points lie:

- (-2, 0, 0), Mandelbrot shape, z = 0 (5 cases): the tip of the set. Its dot goes 0, -2, 2, 2, 2, ... and stands
  exactly ON the big ball for ever, so rounding alone decides (JavaScript says 15, the card 17).
- (-1/64, +-1, 0) and its mirror points, Julia shape c = -1, z = 0 (4 points in each of 8 cases): the first step
  lands exactly on the ball there (|z^2 - 1| = 2 to the last digit JavaScript has).
- The rest are scattered single points next to a fine skin of step 7 to 16, most at z = 0.3 for the rules that fold
  or turn space (fold, turnalong, alongonce, pulledplane) and for the power 3.

Wider set (`a-slice-wide.json`, log `slice-wide.log`): all 21 approaches at power 2 (m and rabbit j, z = 0 and 0.3),
13 sets of dials away from their starting values, the modifiers, and the powers 2.5, -2 and 4 for six approaches.
153 cases, 10 105 497 points, **567 differ (0.0056 %)**: 11 within 1e-9, 38 within 1e-7, 152 within 1e-6,
346 within 1e-5, 19 within 3e-5, 1 within 1e-4. None further. The most in one case: 99 (Blended planes with "pinch
the seams", a rule with tears of its own), 57 (Lathe with spin 3), 34 (Mandelbulb with both phases).

Three of those points looked wrong at first and are not (`a-odd-points.json`): they lie exactly on a plane the rule
maps to itself (y = 0, or z = 0), where JavaScript's dot stays on that plane for ever and the card's dot, a rounding
error off it, leaves. Points 1e-9 to 1e-5 beside them already have the card's kind of value.

Also run, in a page built with builder core's live files (`dist/r26-three-page.html`, `a-cut.json`, log
`cut-run.log`): **the 3D slice at z = 0 against `LEARN.shape.mask2`**, 257 x 257, 16 steps, Mandelbrot shape, Julia
c = -1 and rabbit, for mercator, fold, lathe, tilt, bulb, split, turnalong, alongonce, pulledplane, sqpillow: 0 to 4
of 66049 points differ in every case (the same knife-edge points as above). For "Mandelbulb, classic", which does not
keep the flat picture, 22 281 to 23 283 differ, as they should.

## 4. The pictures (all 600 x 450, in `pics/`, sheets beside this file)

Opacities and colours are the page's own (copied from `67-learn-shape.js` as it stood at 23:42: solid 1, ghost 0.22
pushed 0.55 towards `--ink`, the bite tinted towards `--bad`). 83 pictures in each theme. I looked at every sheet
at half size and at the pictures named below at full size.

- `pics/ball-step0-dark.png`, `-light.png` (and `ball-step0-julia-*`): a round ball with a white highlight upper
  left, a warm bright patch lower right (the light falling on the far wall from inside), a dimmer middle and a firm
  rim. It reads as a tinted glass ball, not as a flat disc. It is murkier than clear glass: with nothing inside,
  what tells you it is see-through is the bright patch opposite the highlight. Edge smooth, no rings, no speckle.
- `sheet-steps-mercator-*.png` (18 pictures per theme: Mandelbrot shape, Julia c = -1, Julia rabbit; steps 1, 2, 3,
  5, 8, 16): at step 1 the Mandelbrot shape is still the whole ball (it has to be: the first step takes the dot to
  c). From step 2 a smooth glass body sits inside a faint grey shell of the shape before, and shrinks. Far side
  visible through the near one up to about step 5. At 8 and 16 the Julia shapes are strings of glass beads with
  small beads on them; the Mandelbrot shape is a thin spiky flake, small in the frame at zoom 1. Nothing torn or
  banded. A few thin bright lines run over the step-5 Julia body: they are real (a ray there meets two more skins:
  a thin channel inside the body, checked with the JavaScript twin), not marks of the drawing.
- `sheet-steps-fold-*.png`: steps 1 to 3 show the creases of the fold as flat inner faces, seen through the glass:
  this is where the glass look helps most. From step 5 the Mandelbrot shape is a shard with many inner faces. The
  rabbit Julia shape at 8 and 16 (`pics/fold-jrab-16-dark.png`) is a pitted lump whose skin is finer than a pixel:
  **grainy**, and it reads as a rough opaque rock, not as glass. No bands, no tears.
- `sheet-steps-turnalong-*.png`: glass with folds up to step 5 (`pics/turnalong-jrab-5-*.png` reads well, inner
  folds show through). At 8 and 16 the shapes turn into a ball of fine straws (`pics/turnalong-m-16-dark.png`):
  **grainy / speckled at pixel size**, not glass any more.
- Three skins at once: `pics/three-skins-clear-m-*.png`, `-clear-j-*.png`, `-clear-jrab-turnalong-*.png` (ghost
  0.22, bite 0.6 fully tinted, new shape 1) and `three-skins-page-m-2_3-*`, `-page-j-1_3-*` (the page's own numbers
  at slider 2.3 and 1.3). Grey ghost ball, red shell of what is being thrown out, brass shape inside it: all three
  can be told apart in both themes. In the page's own schedule the old ghost has all but gone by the middle of a
  step, so at 2.5 only two skins show (`pics/three-skins-m-2_5-*`).
- The bite in `--warn` instead of `--bad`: `pics/three-skins-m-2_5-warn-*`. **`--warn` is almost the brass of the
  body in both themes, the bite cannot be seen in it.** (Core already passes `--bad`.)
- Two panes: `pics/both-step0-*`, `both-step2-*`, `both-step5-fold-*`. Each pane has its own kind and its own
  centre, nothing leaks from one into the other.
- Dark and light: every picture exists in both. In the light theme the brass is dark, the ghost reads as grey glass
  and the body as amber glass; the highlight is weaker there (white on a light ground).
- 'move': `pics/move-m5-*` (where 'move' starts, 450 x 338 buffer), `move-half-jrab8-fold-*` (half size). Coarser
  and with stepped edges, the same shape and shading.
- Other approaches, for a look: `pics/bulb-m8-*`, `lathe-jrab8-*` (rings), `pulledplane-m6-*`, `split-j-1-6-*` (a
  fluted column), `power3-m4-mercator-*`, `top-m8-mercator-*` (from above the flake has the outline of the flat
  Mandelbrot shape), `zoom2-*`.
- The cut at z = 0 (`o.flat`): `pics/flat-m3-*`, `flat-jrab8-fold-*`. A lighter flat plate inside the glass. It
  works; I looked at these two only.
- In the real page with core's files: `page-3d-m0.png`, `page-3d-both-2_35.png`, `page-3d-jrab8.png`,
  `page-3d-m5.png`. The canvas sits under core's rings, labels and diamond, both panes draw, no console errors.

## 5. Timings (measured: `timing-run.log`, `t3_timing.js`)

One frame of a 600 x 450 picture, drawn and then waited for (one pixel read back), median (least) of 9, in ms.
The machine was doing other work, so single medians jump (a few are twice their least).

Building a program: 85 to 206 ms (table in section 2); mercator 100 to 140 ms, pillow 166 to 206 ms.

| approach | kind | step | still (1200 x 900 buffer, 320 stops) | move, finest (600 x 450, 160 stops) | move, where it starts (450 x 338, 128) | move, half size (300 x 225, 96) |
|---|---|---|---|---|---|---|
| Sphere inversions, one plane | m | 2 | 16.7 (15.6) | 2.9 (2.6) | 1.7 (1.5) | 1.0 (0.8) |
| | m | 8 | 15.9 (15.6) | 2.8 (2.5) | 1.6 (1.4) | 0.9 (0.7) |
| | m | 16 | 17.2 (15.9) | 2.7 (2.4) | 1.5 (1.3) | 0.9 (0.8) |
| | j | 2 | 13.3 (12.9) | 2.2 (2.1) | 1.2 (1.2) | 0.8 (0.7) |
| | j | 8 | 14.6 (14.0) | 2.3 (2.2) | 1.3 (1.1) | 0.8 (0.6) |
| | j | 16 | 16.3 (14.8) | 2.6 (2.3) | 1.4 (1.3) | 0.9 (0.9) |
| Pillow (the dearest) | m | 2 | 27.8 (27.1) | 4.2 (4.1) | 2.3 (2.2) | 1.2 (1.0) |
| | m | 8 | 46.7 (45.9) | 8.1 (7.8) | 4.6 (4.5) | 2.3 (2.1) |
| | m | 16 | 70.7 (69.8) | 12.9 (12.6) | 6.9 (6.7) | 3.8 (3.6) |
| | j | 2 | 34.0 (30.1) | 5.7 (4.8) | 2.7 (2.7) | 1.6 (1.5) |
| | j | 8 | 45.6 (45.0) | 10.3 (8.1) | 10.1 (4.5) | 4.0 (2.4) |
| | j | 16 | 80.2 (66.1) | 13.9 (11.8) | 14.2 (7.0) | 8.3 (3.9) |

Blended planes is next (still 22 to 63 ms, half-size move 1.0 to 3.4 ms), then Pulled plane (23 to 43 ms, 0.9 to
2.9 ms). Between two steps, with three skins (slider 8.5), a frame costs between what step 8 and what step 16 cost
(rows in `tables.txt`). Over all 21 approaches a still frame of the Julia shape at step 8, ghost and body, takes
9.7 to 45.4 ms (`all21.log`, the least of 3 each).

'move' at half size: 0.6 to 8.3 ms a frame, so the aim of 25 frames a second (40 ms) is met many times over, and at
full size too (2.2 to 14 ms in the table; one noisy median of 19.5 ms at slider 8.5). A view starts 'move' at three
quarters size and, from what the card reports, went to full size within five frames (`robust-run.log`: "moveLod
0 0 0 ...").

## 6. Other checks (`robust-run.log`, `t3_robust.js`)

- The twin on points worked out by hand: centre 17, outside the ball 0, c = 1 thrown out at step 3, Julia c = -1 at
  the centre 17, at (1.9, 0, 0) step 1.
- Buffer sizes: 600 x 450 box, ordinary screen: still 1200 x 900, move 450 x 338 (start) and 300 x 225 (half). On a
  sharp screen (ratio 2): still 1200 x 900, move 675 x 506. A 390 x 300 box at ratio 3: still 780 x 600. A
  1100 x 700 stage: still 2200 x 1400.
- `learnShape3d.proj` against the picture: the ball's left and right edge on the middle row at pixels 66 and 533,
  the helper says 66 and 534.
- Calls with things left out (`draw()`, no levels, no colours, four levels, `slice()` without options): none throws.
- The graphics context taken away and given back: `draw` says ok false with a plain sentence while it is gone, and
  the view draws its last picture again by itself when it is back.
- `dispose()`: the canvas leaves the page, later `draw` says ok false ("This 3D picture has been closed."), `slice`
  gives null, and another view goes on working.

## 7. Where the contract was not followed to the letter

1. `alpha` is a strength, not a literal opacity. alpha 1 is "solid glass" and still see-through: a near skin seen
   face on covers 13 % of what is behind it, at its rim 92 %; a far skin 12 % to 52 %, more where it is lit.
2. `draw()` returns before the card has finished. Its `ms` is the card's own time for the last frame of that quality
   the browser has reported (a frame or two old), and the time of the call itself until there is one.
3. A program is built the first time its approach is drawn, and the page waits for it (85 to 206 ms, first picture up
   to about 0.3 s). Nothing is shown meanwhile.
4. `slice()` gives `null`, not an array, when the program did not build or the view is closed. Its points include
   the edge of the square (row 0 IS y = +half, spacing 2 * half / (size - 1)); `{ centres: true }` gives cell centres.
   Core's `mask2` uses the same grid.
5. "0 = starts outside the big ball": for the Julia shape of "Quaternions, 4D" with its dials away from 0 the start
   point in four dimensions is tested as well as the picture point (it can be longer).
6. More than three levels: the three with the greatest alpha are drawn.
7. `dispose()` also takes the canvas out of the page.
8. `colours.ink` is used only by two extras (a level's `ghost`, and the flat cut).

Beyond the contract (all optional): `learnShape3d.proj(o, rect)` (core uses it for its rings and the diamond), a
level's `ghost` 0..1 (pushes that skin towards `colours.ink`; core uses it), `o.flat`, `o.look` / `o.lod` / `o.res`
(for trying things out and for timings), `view.slicePoint`, `view.time`, `view.stats`, `learnShape3d.source`.

## 8. What does not work, or is not known

- Deep steps of the rougher rules (fold, the turning planes, most "tried" entries; from about step 8) are grainy and
  read as a rough opaque lump, not as glass. The skin there is finer than a pixel and a ray can miss a wall thinner
  than its stride (1/80 of a unit, about one CSS pixel of a 600 x 450 picture at zoom 1). Four buffer pixels per
  pixel in 'still' soften it; they do not remove it.
- 'move' pictures have stepped edges (one buffer pixel per pixel or fewer).
- The first picture of an approach holds the page for up to about 0.3 s with no sign that it is working.
- A Mandelbrot shape with a negative power is empty from step 1 on: the dot starts at 0, the first step throws it
  to 1e18, and by the rule of the game that is "thrown out". (The lab's solid passes through that pole instead.)
  The page's sentences should not promise a shape there.
- A point that stands exactly on a skin (the tip -2 of the Mandelbrot shape, for one) gets different answers from
  JavaScript and from the card. That is 4 or 5 points of 66049 in the cut at z = 0.
- The path for a browser that does not time its graphics card (it waits for one frame in 24 instead) was not run:
  this Chrome has the timer.
- Not tried: a phone, Safari, Firefox, a screen ratio above 1 on real hardware (only the buffer arithmetic).
- Zoomed far in, the stride of a ray grows against the pixel (the stops are doubled at most).
- The flat cut is laid over the skins of its own stretch of the ray in a fixed order, so where the cut meets a skin
  one or two pixels can be laid in the wrong order.

## 9. Files here

- `t3_run.py` runs a list of actions against `dist/r26-three.html` with `t3_prelude.js` loaded;
  `t3_pics.py` makes pictures and sheets from `spec-steps.json`, `spec-special.json`, `spec-three.json`;
  `t3_tables.py` turns the logs into `tables.txt`.
- Checks: `a-slice.json` + `t3_slice.js` -> `slice-required.log`; `a-slice-wide.json` -> `slice-wide.log`;
  `a-all21.json` + `t3_all21.js` -> `all21.log`; `a-timing.json` + `t3_timing.js` -> `timing-run.log`;
  `a-robust.json` + `t3_robust.js` -> `robust-run.log`; `a-fail.json` -> `fail-run.log` (this one ends with exit
  code 3 on purpose: the console error is the thing tested); `a-odd-points.json`; in the joint page: `a-page.json` ->
  `page-run.log` and `page-3d-*.png`, `a-cut.json` -> `cut-run.log`.
