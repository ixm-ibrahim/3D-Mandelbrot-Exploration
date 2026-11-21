# Round 29, Track B ("learn"), the builder's notes

Page: `dist/r29-learn.html`. Overlay on `base21a`: `out/r29/learn/overlay/`. Build line: `out/r29/learn/BUILD.txt`.

None of the files that are off limits was touched (`00-core.js`, `32-balls.js`, `40-render.js`, `46-mesh.js`,
`80-ui.js`, `90-boot.js`, `body.html`): the overlay holds four JavaScript files and two style sheets, nothing else.
No git command was run. Nothing was published.

## In eight plain lines

1. A whole shape has a new choice in its transport and in its panel, **Each step: At once | Move by move**, and
   **Dots: Few | Some | Many**. Move by move and Some are how it opens, in 2D and 3D, for all three kinds.
2. Move by move lays coloured dots over the picture, one for each starting place, and plays every step on them in
   parts: where the dots are now, the moves of the rule one after another (the chain `learnPlan` gives), the
   throwing out (dots outside light up red and fade while the bite lights up in the picture), and the way back home.
3. The slider runs through the parts, Play takes about five seconds a step at Normal, and on a wide window a row
   of the parts' names stands under the sentence: the part being played is marked, a click plays that part alone.
4. In 3D the glass picture fades to a ghost behind the dots and is not drawn again while only the dots move.
5. One point: Show has a fourth choice, **A grid of points**, whose dots go on from where the last step left them;
   the third choice is named by what it is ("One point for every direction (a ring)" / "(a ball)" / "A row of
   points along the line"); the help is the brief's text; a line under the select says what the extra points are.
6. Numbers: 399 cases, 859 453 dot-steps. Every dot stands on the lab's own rule at every whole step (difference
   0), the chain of moves itself ends within 5.1e-15 of it, and the dots thrown out are the fine picture's own
   (2D: 0 of 93 312 dots differ; 3D against the graphics card: 1 of 119 148).
7. Nothing old changed: 130 + 53 + 71 + 53 + 6 states compared with a page built from `base21a` alone, pictures
   pixel for pixel and words word for word, all the same (one state that differed was my test taking its picture
   too early; taken again after waiting, it is the same).
8. Speed with Many dots: over three runs the slowest frame of the moving parts took 9.2 ms to draw in 2D and
   13.1 ms in 3D (limits 20 and 35); the browser's frame clock stayed at 16.7 ms.

The frozen page my scripts compare with is `dist/r29-learn-b0.html` (`build.py --name r29-learn-b0 --base base21a`).
Running the line in `BUILD.txt` gives `dist/r29-learn.html` again byte for byte (checked by its hash).

## 1. What is in the overlay

| file | what changed |
|---|---|
| `js/65-learn-steps.js` | every move carries `all`: what it does to every dot at once, as the end of a sentence ("every dot’s angle is doubled"). A few helper words. `learnStretchTo` is told whether the rule's length is the plain power. One point reads none of it; no number changes. |
| `js/66-learn-view.js` | Show: the fourth choice `grid`; the choices, the help and the new line under the select follow the space; `LEARN.points()` for the checks. New helpers: `learnVDotColour`, `learnVGridPoints` (the layout both parts of Learn use), `learnVGridMarked`, `learnVShowOptions / Help / Line / Paint`. |
| `js/67-learn-shape.js` | Each step and Dots (state, transport, panel, reset, test handle); the dots, the parts of a step, the chain of one step, the drawing of the dots, the words of each part, the row of part names, the clock. With At once every old function gets what it got before. |
| `js/68-learn-shape3d.js` | one new function beside `out()`: `learnShape3d.orbit(p, kind, c, maxK)`, the same arithmetic with the places kept. Nothing else: no word of the program text on the graphics card changed. |
| `css/65-learn.css` | 3 lines: the line under Show. |
| `css/67-learn-shape.css` | 28 lines: the new row of the transport, the Dots select, the row of part names, the phone. |

How the overlay is made: `PYTHONIOENCODING=utf-8 python -B -W ignore out/r29/learn/mk/make.py` reads the frozen
files, replaces exact pieces (`mk/patch65.py` ... `patch68.py`, with the new code in `mk/frag/`), writes the six
overlay files, writes `BUILD.txt` and builds the page. A fixer can as well edit the overlay files directly and
forget the patch scripts; the overlay is the thing.

## 2. How a step is played (for whoever reads the code next)

- **Dots** (`learnShapeDots`): the grid of `learnVGridPoints`, gap 0.25 / 0.16 / 0.1 on the 2D page (202 / 484 /
  1258 dots) and 0.5 / 0.4 / 0.3 in space (268 / 516 / 1232). For each dot the places after 0, 1, 2, ... steps are
  kept, worked out by the picture's own arithmetic: 2D `learnShapeOrbit2` (line for line `learnShapeOut2`, which is
  `learnShapeMap`), 3D `learnShape3d.orbit` (line for line `learnShape3d.out`, with the approach's own `cmap`, `zmap`
  and what an orbit carries).
- **Parts** (`learnShapePart`): `out`, one part for each move of `learnPlan`, `gone`, `home`. They share the slider's
  fraction inside a step evenly (2D: 6 parts; 3D: 6 to 8). Inside a part the motion starts and ends gently.
- **The chain of one step** (`learnShapeChain`): from each dot's exact place after k steps the moves are applied one
  after another. Every move works from the dot it is given; the last one, the slide, is made with each dot's own c.
  When the last move is done the dot is put on its exact place after k + 1 steps (the chain ends within rounding of
  it; the largest difference met is kept as `gap`). For the two entries whose orbit carries something ("Along once,
  then one plane", "Pulled plane") every dot gets the chain `learnPlan` gives for what its own orbit carries and for
  its own c.
- **The picture behind the dots** (`learnShapeBackdrop`): in `out` and the moves, shape k, quiet (30 % on the page;
  in space the glass canvas at 34 % opacity, not drawn again). In `gone`, today's whole blend from shape k to shape
  k + 1 (the bite lights up and fades) at 72 %. In `home`, shape k + 1, coming up to full strength.
- **Test handle** (all on `LEARN.shape`): `set({ each: 'once' | 'moves', dots: 'few' | 'some' | 'many' })`;
  `state()` gives `each`, `dots`, `part` (`key` out / move / gone / home, `label`, `i` of `n`, `t`, `move`), `parts`,
  `shown`; `dots(kind)` gives every dot's `start`, `out`, `places` (after 0, 1, ... steps), `c`, `carry`, `big`,
  `colour`; `chain(kind, k)` gives step k + 1 as played (`on`, `joints`, `end` = where the chain of moves itself
  ends, `truth`, `gap`, `moved`); `dotsAt(kind, pos)` gives the dots as drawn at a slider position; `numbersAt(kind,
  points)` the fine 2D picture's own numbers at any points; `slice3(kind, opt)` the 3D picture's own program on a
  level cut; `playPart(i)`; `timing()`. For One point: `LEARN.points()` and `LEARN.set({ show: 'grid' })`.

## 3. What I measured (section 4 of the brief)

All on this machine, headless Chrome, with `tools/shot.py` and the real-mouse helper `hand.py`. Logs are in
`out/r29/learn/*.txt`, scripts in `out/r29/learn/mk/`, pictures in `out/r29/learn/shots/`.

### 4.1 Numbers (`mk/dotcheck.py 2d`, `3d`; what is measured: header of `mk/chk.js`)

- 2D: 144 cases (Few, Some, Many; powers 2, 3, 2.5, −2; no modifier, |x| + flip y, |y|; Mandelbrot, Julia at the
  basilica, the rabbit and c = 0.9 + 0.8i outside), 356 749 dot-steps.
  - where a step begins and ends as played, against the dot's kept places: 0 and 0.
  - kept place after k + 1 steps against `learnPlan`'s own rule applied once to the kept place after k: at most 2.4e-15.
  - kept places against the rule applied again and again from the start, written out a second time in the test
    (multiplication for whole powers 2 to 8, polar form otherwise, modifiers first): 0.
  - where the chain of moves itself ends, against the kept place: at most 2.5e-15.
  - thrown out at another step than `LEARN.shape.out2` says: 0 dots. Than the fine picture's own arithmetic
    (`learnShapeMap`) at the starting place says: 0 of 93 312 dots. Steps with the wrong dots thrown out: 0.
- 3D: 255 cases (Few, Some, Many; all 21 entries of the Approach list; powers 2 and 3; Mandelbrot and Julia; plus
  |x| |z| flip y for three entries), 502 704 dot-steps.
  - begin and end as played: 0 and 0. One step of `learnPlan`'s rule: 0. Iterated with `MATH` / `CARRY` in the
    test: 0. The chain of moves itself: at most 5.1e-15.
  - thrown out at another step than `learnShape3d.out` says: 0. Than the picture's own program on the graphics card
    says (`slice` at the dots' own places, level by level): **1 of 119 148 dots** ("Pillow", Julia shape, Many,
    power 2: the dot says step 10, the card step 9; the card counts in single precision).
- All 21 entries can be shown; none was left out. The names of the parts per entry are in `numbers-3d.txt`.

### 4.2 Nothing old changed (`mk/old.py`, `mk/smoke29.py`, `mk/old27b.py`)

- `old.py`: the same states on `dist/r29-learn-b0.html` (base21a alone) and on the new page; the stage cut out of a
  window shot, compared pixel by pixel; the words under and beside the picture word for word.
  - A whole shape with At once (53 states: 2D and 3D, the three kinds, four c, whole steps and half-way positions,
    another approach and power): 1400x950 dark 53 of 53, 1400x950 light 53 of 53, 390x800 light 53 of 53, 390x800
    dark 53 of 53. Words 53 of 53 each time. (The pictures themselves were deleted after the comparison, being
    the same; the result lines are in `old-*.txt`.)
  - One point with the three old choices (71 states: three spaces, hidden direction on and off, four places in a
    step, a second step): 1400x950 dark 71 of 71, 390x800 light 71 of 71. Words 71 of 71.
  - The rest of the lab (6 states: Mandelbrot, Julia, Julia with the Lathe, Kleinian, Balls on balls, back): 6 of 6.
  - In the first run of all 130 states one differed ("point-reset": Learn switched off, the lab's own solid still
    being drawn when my script took the picture after half a second). The script now waits for the finished
    picture there; run again, 71 of 71.
- The old smoke list of 90 steps (put together as round 28 did it): 90 of 90 steps with a result, no console
  error. Against round 28's own run of the list: 87 result lines the same word for word. The three that differ:
  two carry a number that depends on timing (the eased wheel zoom, the fly camera), and step 7 counts the selects
  of the page, 28 where there were 26 (my two Dots selects). Pictures: 52 of 54 the same; the two are the fly
  camera's and "collapsed", which differs by the same 3353 pixels between round 28's own two pages (the status
  line under the picture).
- Round 27's `same6` (six old states, new page against frozen page): 0 pixels differ.
- **Not run:** round 27's other four scripts (verd, shape, holes, flat) and round 28's own (the dial checks f1,
  fuzz). They are about Balls on balls, which this overlay does not touch; the one Balls picture in my own list is
  the same to the pixel.

### 4.3 The transport (`mk/transport.py`, real mouse and keys; `mk/misc.py`)

- 1400x950 dark and light, 390x800 dark and light: all checks pass. Play, Pause, Back, Forward, every tick,
  Start again, the six part names, the slider dragged a pixel at a time forwards and backwards through two steps
  (every part met, in order, both ways), arrow keys on the slider, the space bar on the picture, the three speeds
  chosen with the keys; kind, 2D/3D, Dots, Each step, c, the power and three approaches changed while it plays
  and while it stands. After every change the script checks that the part the words name is the part the dots are
  drawn in. No console error or warning.
- Forward plays one whole step in 4.51 s at Normal, 2.22 s at Fast, 9.11 s at Slow; a play from end to end rests
  0.4 / 0.2 / 0.8 s on each whole step on top of that.
- `misc.py`: no motion wanted (no play by itself, Forward and the part names jump); the theme and the window
  changed in the middle of a part; the diamond dragged and the 3D picture turned while the dots are away; Learn
  left and entered again, Follow switched, Reset everything, all while it plays; an empty picture; a negative
  power; the grid of One point through three presses of Next step (every dot where three steps of the rule take
  it, 3.2e-15) and Start again. All pass.

### 4.4 Speed (`mk/speed.py`)

How: one step is played at Normal by the page's own clock. A second `requestAnimationFrame` loop reads, once a
frame, what the page measured for its last redraw (`LEARN.shape.timing()`: from the start to the end of
`learnShapeDraw`), where the slider stood, and the time since the frame before. Dots: Many, 1400x950, steps 1 and 3.

- 2D (Julia, Mandelbrot, Both with 2516 dots, power 2.5): a frame of the moving parts takes 0.9 to 3.5 ms in the
  middle; the slowest frame in three runs of the script took 6.8, **9.2** and 5.1 ms.
- 3D (seven approaches, among them the two whose orbit carries something; Both with 2464 dots): 1.0 to 5.7 ms in
  the middle; the slowest frame in three runs took 10.6, **13.1** and 11.2 ms. The glass is not drawn in these
  frames. (The slowest frame is the first of a step, in which the chain of the step is worked out for every dot.)
- The frame clock: median 16.7 ms, 95 % under 17.2 ms in every case. Single late frames happen: one or two of
  33 ms in some of the 276-frame plays, and once one of 80 ms (other agents' browsers were running beside mine).
- In the throwing out, where the 3D glass is drawn again every frame as with At once: draw time at most 9.2 ms,
  frame clock 95 % at 16.8 ms.

### 4.5 Can it be read (my own look; the checkers must judge this)

I looked at window shots of every part of a step for: 2D Julia light and dark, 2D Mandelbrot dark (step 1) and
light (step 4, Many), Both 2D dark and on a phone light, 3D Julia dark (sphere inversions) and light (Lathe,
Many), 3D Mandelbrot light (Mandelbulb), Both 3D on a phone, a low phone window; the panel wide and on a phone;
the grid of One point in 2D, 3D and on a line. What I see:

- A dot can be followed: six dots a picture are larger and ringed, with a line for the way they came in the part
  being played and a ring where they started.
- Which dots are thrown out, and why, is clear on the 2D page: the big circle is drawn firmly while the dots are
  away, the dots outside it turn red and fade, and the bite turns red in the picture at the same moment.
- The dots stand out from the quiet picture in both themes.
- Weaker, and said in section 4 below: Both on a phone, 3D in general, and the pace at Normal.

## 4. What is not right, or not done

1. **A phone, Both:** two pictures 179 px wide. The dots are 1.2 to 1.8 px in radius; the cloud is seen moving
   and the six larger dots can be followed, a single small one cannot.
2. **3D:** a dot that is outside the big ball can be drawn inside its outline (it is in front of the ball or
   behind it). The picture cannot show the difference; the sentence of the throwing out says "Some of them are
   in front of the ball or behind it" when that is so. Turning the picture helps. A cloud of 500 dots in space
   is harder to follow than the flat one.
3. **Pace:** at Normal a part lasts about 0.8 s. That is the five seconds a step the brief asks for, but a
   sentence cannot be read in that time. Slow gives 1.5 s; the part names (wide window) and the slider go as
   slowly as one likes. The first switch to A whole shape still plays by itself, now for 80 s unless paused.
4. **A phone has no row of part names** (no room): the line above the sentence names the part. On a phone the
   slider has about 3.5 px for a part, so going through the parts by hand is coarse there.
5. **A phone, low window:** the new row makes the transport 44 px taller (266 px for 222). Where that would stop
   the picture from being held at the top of the window while the controls scroll (the pin lets go above 72 % of
   the window: windows about 600 to 645 px high), the row is put away and Each step and Dots stand in the panel
   only. Measured (`pin.txt`): with that, the picture is held at exactly the window heights at which it was held
   before (600, 640, 667, 700, 740, 800), and the row shows from 667 px up. On a real phone the bars of the
   browser change these heights; I could only test in headless Chrome.
6. **Steps in which nothing moves are played all the same:** "where the dots are now" in step 1 of a Julia shape
   (the sentence says the dots are at their starting places), Turn and Stretch in step 1 of a Mandelbrot shape
   (every dot is at the centre; the sentence says so).
7. **Later steps have few dots.** With Some, a Julia shape has about 80 dots left after six steps, and steps
   that take a bite finer than the gaps throw out no dot (the sentence says so). Many helps.
8. **Dots that are thrown out are mostly out of the picture** when the step stretches them far (the frame does
   not grow). One sees them leave during the Stretch; in the throwing out only those near the big circle are in
   view.
9. For the entries without written-out moves the sentence of the Turn is general ("every dot swings round the
   centre, the short way, to the direction this approach sends it to. Each by its own amount: Follow One point
   shows it for a single dot").
10. I did not try a touch screen, another browser, or a real phone.

## 5. Decisions I had to make

1. **The grid is shifted off the centre** (half a gap along x, a quarter along y; in space half, half and a
   quarter). With a grid that is its own mirror image through the centre, squaring lays the dots on top of each
   other two by two and half of them seem to vanish at the Turn. In space the shift also keeps every dot off the
   axes and the flat plane, where many rules have a special case. The 3D shift is chosen so that `slice()` can ask
   the graphics card about exactly the dots' places.
2. **Exact places first, moves between them.** A dot's place at every whole step is the picture's own arithmetic;
   the moves of a step start from that place and the end of the last move is that arithmetic's next place. So no
   error can pile up over 16 steps, and the dots thrown out are the picture's by construction.
3. **Names.** The last move is "Slide" (the brief's sentences), where One point says "Add c"; One point is not
   changed (its pictures must not change), and the panel says "(The last move, Slide, is the one that One point
   calls Add c.)". The turn that a dial of the two Mandelbulbs adds is "Add the turn" here, not One point's "Add
   the phase", and the sentences name that dial "one of this approach’s dials". The first and the last part are
   called "where the dots are now" and "back home" above the sentence, "Dots now" and "Back home" in the row of
   part names.
4. **Sentences that the brief did not fix** (all in `learnShapePartWords`): step 1 of a Julia shape, first part:
   "The dots are at their starting places: nobody has taken a step yet."; a Mandelbrot shape after step 1: "...
   each has already taken k steps from the centre, with its own c."; Both: "Left: every dot starts at the centre,
   each with its own number c. Right: the dots are at their starting places." and "Slide: left, every dot is moved
   by its own c. Right, every dot is moved by the diamond’s c."; a part in which no dot moves: "every dot is at
   the centre, so nothing moves." / "c is 0 here, so no dot moves." / "this move leaves every dot where it is.";
   the throwing out carries the count ("...are thrown out: 41 of 204."), and when nobody is thrown out: "No dot
   landed outside the big circle, so none is thrown out." (plus "What this step takes is finer than the gaps
   between the dots." when the picture shows a bite); the way home when every dot is already there: "Every dot has
   landed on its own starting place, so nobody has to go back."; no dot left: "No dot is left to show it: ...".
   The sentences for the moves of every approach and power are listed by `mk/words.json`.
5. **A row of the parts' names** under the sentence (wide windows). The brief did not ask for it. It shows the
   order of the parts, marks the one being played, and a click plays that part alone and stops at its end. Back,
   Forward, the ticks and the keys keep their meaning (whole steps).
6. **The whole blend of today's bite is played inside the throwing out**; the way home is played over shape
   k + 1 at rising strength. So the dots that are left go home into the very shape they make.
7. **Six larger dots a picture:** two that stay to the end and four that are thrown out at early and late steps,
   far apart from one another (where there are such).
8. **Colours:** the hue from which way a dot starts from the centre (in space round the z-axis), light or deep from
   how far out (in space how high); light on the dark stage, deep on the light one. A turn and a stretch of the
   whole grid then show in the colours.
9. **The slider** gets finer notches with Move by move (0.005 of a step for 0.05) and snaps to a whole step only
   within 0.004 (0.02 with At once, as before).
10. **Dots is greyed with At once** (there are no dots then), and At once shows no dots at whole steps either.
11. On a wide stage the corner of the first picture carries a third line, "each dot: one starting place".
12. While Move by move plays, the sentence is not sent to a screen reader at every part (`aria-live` off while
    playing, as the one calm sentence did before for At once).
13. **One point, the grid:** gap 0.25 on the page (202 dots), 0.5 in space (268), 0.1 on a line (41 dots from −2 to
    2). The picture's frame holds the big circle the grid is laid over and does not grow after that. Five dots are
    larger, with a ring where the step on show found them. For an entry whose orbit carries something the grid's
    dots go through the moves of the point's own steps, as every extra point always did.
14. The line under Show for the grid says, after k steps: "Grid: each dot goes on from where the last step left
    it. This is where they are after k steps."
