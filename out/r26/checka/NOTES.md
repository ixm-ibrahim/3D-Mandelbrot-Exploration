# Round 26, checker "arithmetic": notes

Page under test: `dist/r26-checka.html`, built by me from `src/` at 02:00 (`python build.py --name r26-checka`).
It is byte for byte `dist/r26-join.html` (compared before the first run and again after the last one; no file of
`src/` changed in between). Frozen page for comparisons: `dist/r26-checka-base.html` (`--base base18a`), byte for
byte `dist/r26-base.html`. I changed no file of `src/`. Nothing was published.

Verdict: the arithmetic is right, in the flat pictures and in space, and so are the pictures drawn from it.
Five small defects were reproduced, in words, in a test handle and in how the page is used, none in a number the
reader sees drawn.
They are listed in section 3.

## 1. How I measured

- `clab.py`: my own driver (the websocket client of `tools/shot.py`, values back in Python, screenshots as arrays).
- `cref.py`: my own reference for the flat game, written in Python from section 1 of the round's file: whole powers
  by multiplying complex numbers, other powers in polar form with the principal angle, the modifiers first
  (|x|, |y|, then flip y), "thrown out" = further than 2, the smallest such step. Checked first against eleven
  orbits worked by hand (c = 1 leaves at step 3, c = -2 never, ...).
- `c_prelude.js`, `ckOut3`: my own orbit in space, written from the lab's shader text (GL_ORBIT: where an orbit
  starts, cmap, zmap, the modifiers, the carry hook) and driven with the lab's `MATH` and `CARRY`. The fold and the
  4D slice (cmap, zmap) are ported from the GLSL, not taken from the lab's JavaScript. Nothing of
  `68-learn-shape3d.js` is used in it.
- `cpix.py`: a screenshot of the stage against the reference: every pixel is put where it stands in the plane,
  the reference says how much of it shape k covers (four points to a pixel, where the page asks), and a pixel whose
  3 x 3 neighbourhood lies wholly inside must be painted brass, one wholly outside must not be painted.
- "Within a hair of a skin": where two answers differ, the point is asked again close by. If the other answer turns
  up within 1e-7 (two 64-bit answers) or 1e-4 (the graphics card's 32-bit answer), the point lies on a skin.

Every script `tNN_*.py` writes `tNN_*.log` beside it. Run one with
`PYTHONIOENCODING=utf-8 python -W ignore out/r26/checka/tNN_name.py`.

## 2. What was checked and found right

### Flat pictures (check 1)
- `t1_flat.log`: `mask2` against the Python reference: 144 masks of 257 x 257 points (9,511,056 points), both
  kinds, powers 2, 3, 2.5, 1, 0.5, -2, 4, 9, -1.5, modifiers none / |x| / flip y / |x| and flip y / |y| / |y| and
  flip y, c = -1, the rabbit, 0.28 + 0.53i. 78 points differ, all at the powers 1 and 0.5, all within a hair of a
  skin (the page works those powers in polar form, the reference multiplies). At the powers 2, 3 and 2.5: 0 differ.
  Three other grids (300 points, half-width 1.3; 128 cell centres; 401 points, half-width 0.4): 0 differ.
- `out2` asked one point at a time, 192,480 points: all agree but one, the tip (-2, 0) (defect 3).
- `t2_pixels.log`: the picture itself, 144 screenshots at whole steps: Mandelbrot shape and Julia shape (rabbit,
  dendrite) at every step 0 to 16, basilica, Both, power 3 with |x|, power 2.5 with flip y, power -2, power 0.5,
  zoomed with the wheel and moved by a drag, light theme, 390 x 800. Of 8,244,822 pixels surely inside a shape 0 are
  not painted; of 42,061,484 surely outside 0 are painted. Between two steps (2.3, 4.3, 1.3, 3.3): the points being thrown out are in the warning colour, the rest
  brass, nothing outside. Pictures: `t2-*.png`.
- Also right: the coarse picture drawn while the diamond is held (`t14_moving.log`; at the power 2.5, where the
  page draws one point to two pixels, 77 pixels next to the edge are soft and none is painted outside), a stage made
  tall so that Both stands one picture above the other, a sharp screen with two device pixels to a pixel
  (`t11_more.log`), the picture a play ends on (`t7_play-*.log`), the picture after the window was resized six times
  while playing (`t9_robust-R1.log`).
- The diamond: dragged in a Julia picture, in either picture of Both and in a zoomed picture, c is the point of the
  plane under the pointer to a hundredth (off by 0.003 to 0.004), the dials show it, and the picture is then the
  shape of that c (`t11_more.log`).

### Space (check 2)
- `t3_slice.log`: `view.slice` (the card) against `learnShape3d.out` (T) and against my own MATH / CARRY orbit (M):
  936 slices of 129 x 129 points (15,575,976 points): all 21 approaches at the power 2, twelve at the power 3,
  eight at 2.5, six with |x| and flip y, six with |z| and flip z, twelve with their dials moved off the starting
  values (among them both rules that carry something along the orbit, the fold with 3 planes and the 4D slice with
  all three dials moved), five at the power -2, four at 0.5; Mandelbrot shape and three Julia c (one off the flat
  plane); z = 0, 0.2, 0.5.
  T against M: 0 differ. The card against either: 1,499 differ (one in 10,000). 1,484 of them have the card's
  number within 1e-4 in my orbit. The other 15 were looked at one by one (`t3b_odd.log`): two are the tip (-2, 0, 0),
  whose orbit runs on the surface of the big ball itself; for the rest the card's number turns up among 4,000 points
  within 1e-4, or when every step of my orbit is nudged by a part in 100,000 to 1,000,000 (what 32-bit sines do).
  None is left unexplained.
- `t13_source.log`: the program text the 3D module builds holds the approach's GLSL as it stands and the lab's own
  f() and start() lines of GL_ORBIT, with the plain equation compiled by the lab's compileFormula, for all 21
  approaches and both kinds of formula.
- `t4_cut.log`: the slice at z = 0 against the flat reference, and the sentence about the cut. At the power 2 the 17
  approaches that show the sentence differ from the flat shape at 0 to 8 of 66,049 points, all on a skin; classic,
  rotor and the two Kleinian squarings do not show it and differ at 9,576 to 23,852. Same picture at the powers 3,
  2.5, -2 and with modifiers (at 2.5 "twisted", "Pillow" and "Square pillow" stop keeping the flat picture and the
  sentence goes). With dials moved (23 settings, down to a lift of 0.01 and a turn of 1 degree) the sentence is
  shown exactly where the slice is the flat shape. With c off the flat plane (by 0.2 and by 0.01) it is shown for
  the Mandelbrot shape only, as it should. One case needed a second look (`t4b_rotorframe.log`): "Rotor square with
  a frame" at the power 3, two points whose orbit passes 0.00003 from the ball's surface at step 2.
- `t5_solid.log`: the 3D picture itself (a view of my own, one skin, 600 x 450, eight scenes, k = 0 to 16): of
  262,264 lines of sight that run through shape k, none shows nothing; of the 1,988,526 lines that miss the shape
  with all their neighbours, 476 show something, and walked again with 4 x 4000 stops 420 of the 443 looked at do meet
  the shape (slivers thinner than my first walk). The 23 left are in the dust of "Along once" and of a moved
  Mandelbulb at steps 9 to 16 (`t5-slivers-*.png`); I count them as dust, not as a defect.

### Nesting (check 3)
- Arithmetic (`t15_nest_rests.log`): where a point that has left can come back (power -2: 51,300 of 51,433 points
  of the circle do), the page's shapes are "thrown out for good" (0 points differ over the 17 shapes) and not
  "inside after k steps" (363,458 would differ). Points in shape k + 1 and not in shape k: 0. The same in space on
  the card's slice for four approaches.
- Flat pictures (`t2b_nest.log`, ten runs of 17 steps): no pixel is wholly brass at step k + 1 and not at step k;
  the brass share of a pixel never grows by more than 0.023. (`t2_pixels.log` lists 2 to 26 pixels a run as
  "painted at k + 1 and not at k": that was my first test, which took an edge pixel holding a piece of the grey
  outline for unpainted.)
- 3D pictures (`t5_solid.log`): 0 pixels show something of shape k + 1 and nothing of shape k, eight scenes.

### Using it (check 4), `t6_use.log`
- All 21 approaches, Mandelbrot shape, Julia shape and Both, 3D at ten places of the slider and 2D: no console
  error, no note in place of a picture, the ball covers 29.9 % of the stage at step 0. 20 different pictures among
  the 21 (the 4D slice with its dials at 0 is the Lathe, as its own text says).
- With the page's own controls (Power dial, |x|, flip z, two dials, the approach list, its Next button, the
  modifier buttons): the 3D picture changed after each of 11 changes. The flat picture changes with the power,
  |x| and flip y, and stays the same for |z|, a dial of the approach and another approach.
- A dial played by its own button: the 3D picture follows and stops with it (`t14_moving.log`).
- One point -> A whole shape (things done there) -> One point, from 2D and from 3D: `LEARN.state()` the same,
  0 pixels of the whole window differ.
- Reset everything: Learn off, Follow = One point; opened again, `LEARN.state()`, `LEARN.shape.state()` and all
  pixels of the window are those of the first opening. The panel's own reset: the same.
- To the Julia tab and back: nothing of the whole shape on show there; back, the state is the same and 0 of
  443,232 stage pixels differ. Leaving while the steps play stops them.
- Play pressed with the page's button, Fast (`t7_play-*.log`): 24 plays (three kinds x 2D / 3D x two themes x
  two sizes), each 11.3 to 11.5 s, the slider never went back, each ended on step 16 with the picture of step 16,
  no console error. Rests on the whole steps (`t15_nest_rests.log`): 150 to 167 ms at Fast, 350 to 367 ms at Normal.

### Old behaviour (check 5), `t8_old.log`, `t12_rest.log`
- Follow = One point, the same 109 states on the frozen page and on this page (four approaches x three spaces x
  five places in a step, power 3 with |x|, power 2.5, the start at 0, the hidden direction, a zoomed and a turned
  view, the c of the Julia tab, the panel's reset; dark and light at 1400 x 950, dark at 390 x 800):
  `LEARN.state()`, the texts, and every pixel of the stage and of the transport are the same (56 million pixels).
- Outside Learn: the opening picture and the Julia tab, 0 of 607,392 stage pixels differ.

### Robustness (check 6), `t9_robust-*.log`
- R1 the window resized six times while playing (down to 320 x 480): panes and canvases fit the stage every time,
  the play ends on step 16, the flat picture is right at three sizes, the 3D picture equals a fresh page's.
- R2 300 moves of the slider in a row: the page ends at the slider's place with the picture of that place
  (2D 1.3 s, 3D 1.7 to 3.2 s for the 300; one move took 212 ms once in 3D Both). Arrow keys and the buttons at the
  ends of the slider do what they should.
- R3 c far out (3, 7, (2.4, 2.4), (-8, 8), asked 50 and held at 8): `mask2` equals the reference, the flat picture
  is right, the 2D words say "nothing is left" exactly when nothing is. The diamond cannot be dragged past 2.4.
- R4 powers 1, 0.5, -2, -8, 10, 0, both spaces, three kinds: no note, no error; the words fit the numbers (the first
  step "still the whole big circle" only where it is; "becomes the Mandelbrot set" only for a whole power of 2 or
  more on the page; a Mandelbrot shape at a negative power says nothing is left after step 1, in 3D too).
- R5 the graphics taken away (WEBGL_lose_context) and given back: the sentence stands in the picture's place, the
  2D page goes on working, the picture comes back by itself with the same pixels, also while playing, also when
  lost on the 2D page. Console: nothing.
- R6 odd calls of the handle throw nothing and are clamped; kind and space switched 18 times while playing: play
  goes on; the theme switched while on: both pictures follow; the first switch plays by itself once, not with
  reduced motion, and not a second time; from the 1D line the space becomes 2D and the 1D choice is hidden.
- Other equation and start value (`t11_more.log`): the whole shape's numbers do not change and the note says so.
- Words (`t12_rest.log`): 171 texts of the new part read, none of the forbidden words. The four named c are what
  their buttons say, and the names are shown only at the plain power 2.

## 3. Defects (each reproduced)

1. **3D, a Julia shape of which nothing is left: the sentence still says "What is left after k steps."** over an
   empty ball. Steps: Power dial to 1, Learn, Follow = A whole shape, Julia (c as it opens), 3D, step 9 to 16.
   My orbit: 0 of 4,169 grid points of the ball are left from step 9 on; the picture covers 0 % of the stage; the
   2D page with the same settings says "After 9 steps nothing is left to see ...". `t16_confirm.log`,
   `t16-power1-3d-julia-step12.png`, `t16-power1-2d-julia-step12.png`. Also with c = (7, 0, 0) from step 1
   (`t10-mercator-c7-j-step2.png`). The joiner lists this as open; it is reachable with the ordinary Power dial.
2. **"Quaternions, 4D (slices)" with its dial w off 0: the words about the first step and the start are wrong.**
   Mandelbrot shape, 3D, step 1 says "still the whole big ball, because the first step only takes each dot from 0
   to its own c" and the half step before says "nothing is thrown out yet", but the first step throws out a shell:
   at w = 0.3, 3 % of the ball (978 of 33,401 grid points), at w = 1.5, 71 % (23,630). Julia shape, step 0 says
   "The big ball. Every point is a place to start from", and the shape drawn is a smaller ball (w = 1.5: 9,771 of
   33,401 grid points). The numbers and the picture agree with each other; only the words do not know that this
   slice of 4D lies further out than its picture point. `t10_words3d.log`, `t10-quat4-w1.5-m-step1.png`,
   `t10-quat4-w1.5-j-step0.png`.
3. **`LEARN.shape.out2` gives 15 for the tip c = (-2, 0) of the Mandelbrot shape at the power 2.** The orbit is
   0, -2, 2, 2, 2, ...: never thrown out. `mask2`, the arithmetic the picture is drawn from, says 17 (and 41 with
   maxK 40). So the round's own check "mask2 agrees with out2" fails at 1 of 33,282 points. `learnShape3d.out`
   says 15 there too for "one plane", the card says 17. Cause: out2 works the power 2 in polar form
   (learnFlatRule, exp(2 log 2) is not exactly 4), the picture multiplies. No picture is touched. `t1_flat.log`,
   `t4b_rotorframe.log`.
4. **One point loses its place when the space is switched inside "A whole shape".** One point, 2D, Next step,
   slider into the second move; Follow = A whole shape; press 3D, then 2D in the transport; Follow = One point:
   step 0, move 0 (before: step 1, move 1, 0.4 of the way). z and c are kept. The space choice is shared and a
   change of space has always restarted the step; here the reader ends in the space they started in. From the 1D
   line the place is lost too, which the round asks for (the space becomes 2D). `t6_use.log`.
5. **3D: the letter "c" stands alone at the edge of the stage when the diamond is off it.** Julia shape, 3D,
   c = (-1.8, 0.9, 0), five notches of the wheel (zoom 4.5): the diamond is at pixel (-480, 311), the letter is
   held inside the stage and drawn without it. `t16-3d-zoomed-lone-c.png`. The 2D page draws neither then.

Not counted as defects:
- With Both one above the other (a stage taller than wide, which I reached only by setting the stage's height by
  hand) the sentences read "on the upper for every c, on the lower for the one c of the diamond".
- "Use the c of the Julia tab" on the 2D page also takes the z of that c, which the 2D page neither shows nor uses.

## 4. Files

Scripts: `clab.py`, `cref.py`, `cpix.py`, `c_prelude.js`, `t0_probe.py`, `t0b_ids.py`, `t1_flat.py`, `t2_pixels.py`,
`t2b_nest.py`, `t3_slice.py`, `t3b_odd.py`, `t4_cut.py`, `t4b_rotorframe.py`, `t5_solid.py`, `t6_use.py`,
`t7_play.py`, `t8_old.py`, `t9_robust.py` (sections R1 to R6, one or several as an argument), `t10_words3d.py`,
`t11_more.py`, `t12_rest.py`, `t13_source.py`, `t14_moving.py`, `t15_nest_rests.py`, `t16_confirm.py`.
Logs: one `.log` per script (four for `t7_play`, four for `t9_robust`; the two `t0` looks kept none). 60 pictures,
named after the script.
A line "DEFECTS: n" at the end of a log counts what that script's own rules flagged; where a flag was looked at
again and explained, the section above says so (`t2_pixels`, `t3_slice`, `t4_cut`, `t5_solid`, `t14_moving`).
