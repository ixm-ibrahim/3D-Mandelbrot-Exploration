# Round 26: the Learn tab gets "A whole shape"

Everything an agent of this round needs is in this file. Read all of it before touching anything.

## 0. What the user asked for (their words)

- "for the learn tab, I should be able to see how a circle turns into the mandelbrot (or a set of whatevers, if
  it's not a circle), not just a point or selection of points - and this should be extended into the 3d one too,
  where I can see how a transparent shaded ball or something turns into whatever it does after each step"
- A few minutes later: "it would be nice to have a julia option too for the learn tab, instead of the mandelbrot
  shape I mentioned earlier, so I can see the difference"
- Earlier, about a toy of mine: "the toy you made is not intuitive at all, I don't see the movements, like each
  step in the hop."

Who they are: not a mathematician. They judge by pictures and explore with sliders. They want plain words. Twice
they have answered a mathematical explanation with "you're literally speaking in greek to me".

## 1. The idea, and what is true about it

The lab iterates z -> z^n + c (n is the power, 2 unless changed). The Learn tab today follows ONE point (and a few
companion dots) through the moves of one step. The new part follows a whole shape through many steps.

The game, in the words the page must use:

- **The big circle**: every point no further than 2 from the centre. In 3D: **the big ball**.
- Every point takes steps. A point that lands outside the big circle is **thrown out**, for good.
- **What is left after k steps** is "shape k". Shape 0 is the whole big circle. Each shape lies inside the one
  before. What is left in the end is the set.
- **Mandelbrot shape**: every point of the picture is a c of its own, and its dot starts at 0 (more exactly, at the
  lab's start value, which is 0 for the plain equation). After endlessly many steps what is left is the Mandelbrot
  set.
- **Julia shape**: one c for everybody. Every point of the picture is a place to start from. What is left in the
  end is the (filled) Julia set of that c.

So the honest answer to "how does a circle turn into the Mandelbrot" is: the circle is not bent into it, it is
eaten away. Each step removes the points that have just landed outside, and the bites get smaller and finer.

Exact definitions (for the code, not for the page): for a start point p (Julia: z0 = p, c fixed; Mandelbrot:
c = p, z0 = 0) let z1, z2, ... be the orbit. out(p) = the smallest k >= 0 with |z_k| > 2 (k = 0 means the point
starts outside the big circle; for the Mandelbrot shape z0 = 0, so "k = 0" there means |c| > 2: treat c itself as
the point that must lie in the big circle, i.e. out = 0 when |p| > 2). Shape k = { p : out(p) > k }.
Shape 0 = the big circle / ball itself. Shape 1 for the Mandelbrot shape is also the whole big circle (z1 = c).

The rule in each space:

- **2D page**: the flat rule, the complex power: z^n + c with z = x + iy (polar form for a power that is not a
  whole number, exactly as `learnFlatRule` in `src/js/65-learn-steps.js`), with the modifiers (|x|, |y|, flip y)
  applied first as the lab does.
- **3D space**: the approach chosen in the lab (`ap()`), its dials (`S.param[id]`), the power `S.n`, the
  modifiers, and the PLAIN equation z^n + c whatever the equation field says (Learn already says so in a note).
  It must be the lab's own rule to the last digit: the GLSL of the approach (`a.glsl`, the same text the solid is
  drawn with) on the graphics card, and `MATH[id]` / `CARRY[id]` in JavaScript.

Truths that may be put on the page, and limits:

- For an approach that keeps the flat picture, and a c in the flat plane, cutting 3D shape k at z = 0 gives
  exactly 2D shape k. (True because such a rule sends the flat plane into itself by the flat rule.)
- Do NOT write "a point that has left never comes back" as a general fact (false for powers below 1 and negative
  powers). "Thrown out" is the rule of the game; say it that way.
- Do NOT say the 3D shape after many steps "is" the solid of the Julia / Mandelbrot tab unless you have checked
  what escape radius and step count the lab's solid uses (`uBail`, `S.iter`) and it is the same; otherwise say
  "nearly" or leave it out.

## 2. What to build in this round (cut 1)

A new choice at the top of the Learn panel:

    Follow:   ( One point )   ( A whole shape )

"One point" is today's Learn, untouched, and stays the default (old tests must pass unchanged).

With "A whole shape":

1. **Which shape**:  ( Mandelbrot shape ) ( Julia shape ) ( Both ).  "Both" shows the two pictures side by side:
   left the Mandelbrot shape with the diamond at c, right the Julia shape of that c.
2. **Space**: 2D page or 3D space (the existing radios). The 1D line is not part of this: hide or disable it
   while "A whole shape" is on, and if the space was 1D when the user switches, go to 2D.
3. **The picture(s)** on the stage, in place of the one-point drawing:
   - 2D: shape k filled, the big circle as a dashed ring, faint axes with a few numbers, the outline of the shape
     before as a faint ghost, and (Julia shape, Both) the diamond c. The diamond can be dragged in a 2D
     Mandelbrot or Julia picture, and the pictures follow live.
   - 3D: shape k as a **see-through, shaded solid** (glass-like: the front skin shaded by a light, the far side
     and anything inside showing through), with the shape before as a much fainter ghost shell. Drag to turn,
     scroll or pinch to zoom, a "Reset view" button. At step 0 it is a plain see-through shaded ball.
4. **The transport**, right under the picture (reachable on a phone without scrolling past the picture):
   a slider "step" from 0 to N (N = 16 unless you find a better number; the ticks say 0, 1, 2, ...), Play / Pause,
   one step back, one step forward, "Start again", the Speed select. Also right there, not only in the panel:
   the Mandelbrot / Julia / Both switch and the 2D / 3D switch (compact).
5. **Between two whole steps** (slider position k + u, 0 < u < 1) the picture shows the bite being taken: the
   points that are thrown out at step k + 1 (they are in shape k, not in shape k + 1) light up in the warning
   colour and then fade away, while the old ghost fades out. At u = 1 the picture is exactly that of step k + 1.
   In 3D: the skin of shape k goes from "solid glass" to "ghost" (tinted on the way), the skin of shape k + 1
   comes up from nothing to "solid glass" inside it.
6. **One plain sentence** under the picture (the place of `.learn-say`), which changes with the step, for example:
   - step 0, Mandelbrot shape: "The big circle: every point no further than 2 from the centre. Each point is a c
     of its own, and its dot starts at 0."
   - step 0, Julia shape: "The big circle. Every point is a place to start from, and all of them use the same c,
     the diamond."
   - in between: "Step 3: every point that is still here takes one more step. The ones that land outside the big
     circle are thrown out."
   - at a whole step: "What is left after 3 steps." (and at the last step: "... After endlessly many steps this
     becomes the Mandelbrot set." / "... the Julia set of this c.")
   In 3D say "ball" for "circle".
7. **In the panel** (while "A whole shape" is on, the one-point controls that mean nothing are hidden: the z
   dials, "Show", "Show the hidden direction", the list of moves, "Start at 0"): a short note (below), the
   "Which shape" choice with one line of help each, the c dials (Julia shape and Both only) with "Use the c of the
   Julia tab" and three or four named c values as buttons (c = -1 "basilica", the rabbit c = -0.1226 + 0.7449i,
   c = i "dendrite", c = 0 "a plain disc": check each name against what the picture shows), in 3D one line naming
   the approach the rule comes from, and a "What to notice" paragraph.
   - Note: "Take every point inside the big circle (in 3D, the big ball) and let each one take steps. A point that
     lands outside is thrown out. Press Play under the picture and watch what is left after each step."
   - What to notice, 2D: "The circle is not bent into the shape. It is eaten away: each step removes the points
     that have just landed outside, and the bites get smaller and finer."
   - What to notice, 3D: the same for the ball, plus (only if you have checked it for the approach on show) the
     sentence about the cut at z = 0 from section 1.
8. On the first switch to "A whole shape" in a visit the picture plays by itself once from step 0 (not when the
   reader has asked for reduced motion).
9. "Reset everything" and the Learn panel's own reset put this part back to how it opens: Follow = One point;
   inside it: Mandelbrot shape, 2D, step 0, c as Learn opens.

Not in this round (do not build, but do not block): a second picture "where those points are now", in which the
same points are shown at the place they have reached and the moves of a step (turn, stretch, add c) are played on
all of them. The layout code should be able to hold two pictures side by side (it must anyway, for "Both").

### Words

Use: circle, ball, point, dot, step, c, start, thrown out, what is left, shape, the flat picture, Mandelbrot set,
Julia set, the diamond, see-through, glass.
Do not use on the page: iterate, iteration, escape, bailout, radius of escape, preimage, level set, orbit count,
potential, membership, sample, voxel, shader, mesh, render.
(The existing one-point texts keep their own words; do not rewrite them.)

### Look

The lab has a design system: use only its tokens (`--stage`, `--panel`, `--ink`, `--ink-2`, `--line`, `--brass`,
`--ok`, `--bad`, `--warn`, `--f-mono`), read them the way `learnVTheme()` in `66-learn-view.js` does, and follow
both themes (dark and light; the page reacts to `prefers-color-scheme` and to `data-theme` on `<html>`). Shape:
brass. The bite being taken: `--warn` (or `--bad` if it reads better). Ghost and big circle: `--ink-2`.
No new fonts, no gradients as decoration, no emoji.

## 3. How the lab is put together (read before coding)

- Sources: `src/head.html`, `src/css/*.css` (sorted), `src/body.html`, `src/js/*.js` (sorted). `python build.py`
  joins them into one page. ALL JavaScript files are concatenated inside ONE function scope in file-name order, so
  a top-level name in one file is visible in the others. **Only `90-boot.js` may run code at load time.**
- `base18a/` is the frozen copy of `src/` as published (Version 18). `src/` differs from it by one new line in
  `90-boot.js` (it puts `learnShape3d` on `window.squaringLab` when that name exists).
- Test builds: `python build.py --name r26-xyz --base base18a --use src/js/67-learn-shape.js src/css/67-learn-shape.css ...`
  writes `dist/r26-xyz.html` from the frozen copy plus the listed live files. Use this while other people are
  editing `src/` at the same time. `--swap js/90-boot.js=some/file.js` substitutes any file. NEVER run plain
  `python build.py` (it overwrites the published page `squaring-lab.html`).
- Driving a page: `python tools/shot.py --url dist/r26-xyz.html --actions steps.json` (headless Chrome; actions run
  JavaScript, wait, and save screenshots; `--size 1400x950`, `--size 390x800` for a phone, `--theme dark|light`;
  read its header). `window.squaringLab` is the handle (`.learn` is `LEARN`, `.MATH`, `.APPROACHES`, `.S`, ...).
  Its socket timeout is 120 s; other work is running on this machine, so the graphics card can be slow at times.
- Learn today: `src/js/65-learn-steps.js` (the moves, no DOM), `src/js/66-learn-view.js` (state `LEARN`, the
  Canvas 2D drawing on the stage, the transport under the stage, the panel; test methods `LEARN.set`, `.state`,
  `.goto`, ...), `src/css/65-learn.css`. Read 66 and the CSS fully.
- Shaders: `src/js/30-shaders.js` (read its header: an approach's GLSL defines `mul`, `pw`, `sqr`, `cmap`, may
  define `APR_ZMAP` with `zmap`, and `APR_CARRY` with `carStart`, `carStep`, `carFit`, `gCarI`), `GL_HEAD` (the
  uniforms the approach GLSL reads: `uA` = `apVec()`, `uPow`, `uAbs`, `uSgn`, ...), `GL_ORBIT` (`f(z, c)` and
  `start(c)` with the compiled formula in place of `__F__` and `__Z0__`; see `40-render.js` line ~77 for how a
  program's source is put together, and `20-formula.js` `compileFormula` for the text of the plain equation).
  `src/js/10-approaches.js` holds `APPROACHES` (21 entries, each with `id`, `name`, `glsl`, `params`), `MATH[id](v,
  n, params, c)` (the JavaScript twin of one "power" of the rule, without the + c), and `CARRY[id]` for the two
  entries whose orbit carries something (`alongonce`, `pulledplane`; see how `learnPlan` uses `CARRY`).
- State: `S` in `00-core.js` (`S.n`, `S.c`, `S.abs`, `S.flip`, `S.param`, `S.approach`), `ap()`, `apVec()`.
- House rules: Python is run as `PYTHONIOENCODING=utf-8 python -W ignore ...` from the working directory. Write
  files with the Write tool. Never name a script after a standard module (`json.py`, `time.py`, ...). Notes go to
  `out/r26/<your part>/NOTES.md` (a file called `report.md` cannot be written). Do not touch `out/r25/`,
  `out/r21/`, `base*/`, `squaring-lab.html`, or any `src/` file you do not own. Do not publish anything.

## 4. Who owns what, and the contract between the two builders

### Builder "core": `src/js/67-learn-shape.js`, `src/css/67-learn-shape.css`, and the edits `66-learn-view.js` needs

Owns the choice "Follow", the panel part, the transport, the layout of one or two pictures on the stage, the
overlay (labels, numbers, the diamond, dragging), the 2D pictures, the sentences, the reset, the test handle, and
the phone layout. It calls the 3D module through the contract below and must work (2D fully, 3D with a plain
"The 3D picture is missing from this copy of the page" note) when `learnShape3d` does not exist.

Keep the edits in `66-learn-view.js` small: a field such as `LEARN.follow = 'point' | 'shape'`, and the few places
where the one-point drawing, transport and panel parts must stand aside or come back. With Follow = One point the
page must behave exactly as before.

Test handle, `LEARN.shape` (reached from tests as `window.squaringLab.learn.shape`):

    LEARN.shape.set({ on, kind: 'm' | 'j' | 'both', space: 2 | 3, c: [x, y, z], pos })   // any subset; returns state()
    LEARN.shape.state()   // { on, kind, space, c, pos, step, playing, steps (N), sentence, note, panes: [{kind, x, y, w, h}], threeOk }
    LEARN.shape.play(), .pause(), .goto(pos)
    LEARN.shape.out2(p, kind, c, maxK)      // JavaScript: the step at which the 2D point p = [x, y] is thrown out (maxK + 1 if it is still in after maxK steps)
    LEARN.shape.mask2(kind, size, half, maxK)   // from the SAME code the 2D picture is drawn with: Uint8Array(size * size) of those numbers
                                                // (capped at 255) on the square |x|, |y| <= half, row 0 at the top (y = +half)

`mask2` exists so that a checker can compare the picture's own arithmetic with `out2` point by point.

### Builder "three": `src/js/68-learn-shape3d.js` (one top-level name: `learnShape3d`)

A WebGL2 picture of its own (a canvas and context of its own, not the lab's `#view`), built for speed of
compiling and of drawing: one small program per approach that serves both kinds (a uniform says Mandelbrot or
Julia), built from the approach's own GLSL.

    learnShape3d.make() -> view      // or null when WebGL2 is not there
    view.canvas                      // the caller puts it on the stage and sizes it with CSS; draw() fits the buffer to the box
    view.draw(o) -> { ok, ms, note }
        o.panes   = [ { kind: 'm' | 'j', rect: [x, y, w, h] } , ... ]   // one or two; rect in CSS pixels inside the canvas
        o.c       = [x, y, z]            // the Julia c
        o.levels  = [ { k, alpha, tint } , ... ]   // up to three skins: the skin of shape k drawn with this opacity (0..1);
                                                   // tint 0..1 = how far its colour is pushed from the body colour to the warning colour
        o.yaw, o.pitch, o.zoom           // the eye looks at the centre; yaw about the upright z-axis, pitch above the flat plane,
                                         // in the sense of LEARN_V_VIEWS.s3 in 66-learn-view.js; zoom 1 = the big ball fills about 80 % of the smaller side
        o.quality = 'move' | 'still'     // 'move': while playing or dragging (may be coarser); 'still': the finished picture
        o.colours = { bg, body, warn, ink }   // each [r, g, b] 0..1, read from the theme tokens by the caller
        o.flat    = false | true         // optional extra: also show the cut at z = 0 inside the glass (leave out if there is no time)
        (the approach, its dials, the power and the modifiers are read from the lab's state: ap(), S.param, S.n, S.abs, S.flip)
    view.slice(kind, c, { z, half, size, maxK }) -> Uint8Array(size * size)
        // for tests, from the SAME GLSL the picture uses: the step at which each point of the square |x|, |y| <= half
        // at height z is thrown out (0 = starts outside the big ball, maxK + 1 = still in after maxK steps, capped at 255); row 0 = y = +half
    view.dispose()
    learnShape3d.out(p, kind, c, maxK) -> number     // the JavaScript twin for one point p = [x, y, z], from MATH / CARRY
    learnShape3d.ok() / learnShape3d.note()          // whether the last program built, and a plain sentence when it did not

What a skin is: the surface of shape k. A skin is shaded by a light (a slope found from the points around it, so
that it looks round), and a ray that passes through several skins shows all of them, nearest first, each with its
opacity. The big ball at step 0 must look like a see-through shaded ball, not like a flat disc.

All 21 approaches must draw (or, for one that truly cannot, `ok()` is false and `note()` says so in plain words).
Measure and write down: the time to build a program, and the time to draw one frame at 'move' and at 'still' for a
600 x 450 picture at steps 2, 8 and 16, for "Sphere inversions, one plane" and for the dearest approach you find.
'move' must feel live (aim: 25 frames a second or better at half size on this machine).

Own test page: `python build.py --name r26-three --base base18a --use src/js/68-learn-shape3d.js src/js/90-boot.js`
(the handle is `window.squaringLab.learnShape3d`). Check `slice` against `out` point for point for at least six
approaches including `mercator`, `fold`, `lathe`, `turnalong`, `alongonce`, `pulledplane`, for both kinds; points
within a hair of a skin may differ, anything else is a defect. Put pictures in `out/r26/three/`.

## 5. What "done" means for cut 1

- Follow = One point: the page is what it was (old smoke lists pass; find the lists used for Version 18 in
  `out/r22/entry/NOTES.md` and `notes/_state.md`, "PUBLISHED: Version 18").
- Follow = A whole shape: Mandelbrot shape, Julia shape and Both, in 2D and in 3D, play from step 0 to N without
  console errors, in both themes, at 1400 x 950 and at 390 x 800.
- 2D: `mask2` agrees with `out2`; the picture at a whole step shows exactly shape k.
- 3D: `slice` agrees with `out`; with a c in the flat plane and an approach that keeps the flat picture, the slice
  at z = 0 equals the 2D mask of the same step.
- A person who has never seen the page understands within ten seconds of pressing Play that a circle (a ball) is
  being eaten away into the set, without reading more than one sentence.
