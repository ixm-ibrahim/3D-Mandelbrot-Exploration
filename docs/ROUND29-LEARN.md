# Round 29, Track B ("learn"): the moves inside each step for a whole shape, and a grid of points

Binding for everyone on this track. Read all of it before you start. (Track A, the dials of Balls on balls, has its
own brief, `docs/ROUND29.md`, and other agents work on it at the same time in `out/r29/free/` and beside it. Leave
their folders alone.)

## 0. The user's words

About the Learn tab of Version 21 (verbatim):

> in the learn tab when I click on "a whole shape", I just see the outcome of one iteration blending into the next -
> which is great - but I expected the steps within each individual iteration to be shown as well. idk how you will
> do this, since you'll need to, as a step, filter which are within the inside of the fractal and which are outside,
> which occurs after each of the mathematical steps are shown - and this is overwhelming for me to think about so idk
> how to do this. Also, in "what do show", perhaps add a grid of point option? idk what "directions" means in this
> case, especially since between each iteration you reset where they start, and I don't really know what's being
> represented (either in 2d or 3d). All this will help us go through different 3d approaches at the mathematical
> level and I can help figure things out too

So three things are asked:

1. With Follow = **A whole shape**, show the moves inside each step (turn, stretch, slide, and whatever the chosen
   3D approach does), and then the throwing out, as a step of its own.
2. In **Show** (Follow = One point), a new choice: **a grid of points**.
3. Say what is being shown. "All directions at once" is not understood, and neither is the fact that the extra
   points are laid out afresh at every step.

Why it matters to them: they want to watch each 3D approach work at the level of its moves and help find the right
one. The user is not a mathematician; they judge by pictures and plain words. They have twice said "you're
literally speaking in greek to me". So this track is judged by one thing above all: does a person who is not a
mathematician see, without being told, what the dots are, where they go, and why some are thrown out.

House rules, how the lab is put together and the test tools: `docs/ROUND26.md` (the whole shape was built there:
sections 3 and 4, the contract of the 3D picture), `docs/ROUND27.md` sections 2.3 and 4 (words). They hold here
with `r29` in place of the round number and `base21a/` as the frozen copy (Version 21, the published page; `src/`
is identical to it today). The real-mouse helper is `out/r28/final/ui/mk/hand.py` (class `Hand`); the page's test
handle is `window.squaringLab` (with `learn` on it, and `LEARN.shape` for the whole shape).

Extra rules this round:

- **No git.** The orchestrator is making a repository of this folder while you work. Run no `git` command, and do
  not create, edit or delete `.git`, `.gitignore` or `README.md`.
- Never edit `src/`, any `base*/`, `squaring-lab.html` or `dist/preview.html`. Never run plain `python build.py`.
  Never publish anything. Only the orchestrator merges and publishes.
- Write your report as `NOTES.md` in your own folder (a file named `report.md` cannot be written).
- Python files that contain backslashes: write them with the Write tool, not a shell heredoc.
- Browser scripts one at a time within your own work; other agents' browsers run beside yours, so allow long
  timeouts.

## 1. What is there today

- `js/65-learn-steps.js`: `learnPlan({ space, id, params, n, c, abs, flip })` gives the chain of moves of one step
  for any approach; every move has `at(v, t)`, "so the view can push any other point through the same chain".
- `js/66-learn-view.js`: Follow = One point. The select **Show** has "The point alone", "A small circle round the
  point", "All directions at once". The last one is 72 points on the circle of radius 1 (a line: 21 dots; space: 300
  points on the ball of radius 1), pushed through the moves of the step on show and laid out afresh at every step.
- `js/67-learn-shape.js`, `js/68-learn-shape3d.js`: Follow = A whole shape. Every point of the big circle (radius 2;
  in 3D the big ball) takes steps; a point that lands outside is thrown out for good; "shape k" is what is left
  after k steps. Mandelbrot shape: every point of the picture is a c of its own and its dot starts at the centre.
  Julia shape: one c for everybody and every point of the picture is a place to start from. The picture always
  shows the **starting places**; a step only blends shape k into shape k + 1 and lights up the bite it takes.

That last line is the heart of the user's trouble: the picture is a picture of starting places, but the moves
happen to where the dots are **now**, which the picture never shows.

## 2. Decisions that are made (do not reopen them)

### 2.1 A whole shape: "Move by move"

1. A new choice in the whole shape's transport, labelled **Each step**, with two values: **At once** (today's
   behaviour, unchanged to the pixel and to the word) and **Move by move** (new). **Move by move is the default**,
   in 2D and in 3D, for every kind (Mandelbrot, Julia, Both).
2. Move by move lays **dots** over the picture: an even grid of starting places over the big circle (in 3D the big
   ball). Only the dots that are still in after k steps are on show at step k. Each dot keeps one colour for good,
   given by its starting place, so that the eye can follow it; a handful of dots are marked a little larger so that
   single ones can be followed. A choice **Dots**: Few / Some / Many (2D grid spacing about 0.25 / 0.16 / 0.1; 3D
   about 0.5 / 0.4 / 0.3), default Some.
3. One step (from shape k to shape k + 1) plays as these parts, in this order. The slider's fraction inside a step
   runs through all of them, so dragging the slider by hand goes through the moves forwards and backwards.
   - **Out**: the dots go from their starting places to where k steps have carried them. (Julia shape at k = 0:
     nothing to do, they are there. Mandelbrot shape at k = 0: every dot goes to the centre, because every dot
     starts at the centre; what differs from dot to dot is its c, the place it came from.) Faint marks stay at the
     starting places while the dots are away.
   - **The moves of the rule**, one after another, exactly the chain `learnPlan` gives for the space on show (2D:
     the flat rule; 3D: the approach chosen in the lab, with its dials, the power and the modifiers), every dot by
     its own amount, with the same names the One point view uses. In the Mandelbrot shape the last move, the slide,
     is by each dot's own c.
   - **Thrown out**: the dots that have landed further than 2 from the centre light up in the warning colour and
     fade. The bite lights up in the picture of starting places at the same moment, as it does today.
   - **Home**: the dots that are left go back to their starting places. That is shape k + 1.
   Between steps the picture stands as it does today (the fine picture of shape k + 1) with the dots at home.
4. While the dots are away from home the fine picture of the shape stays as a quiet backdrop (in 3D the glass body
   becomes a faint ghost and is not drawn again for every frame; only the dots move, on the canvas that lies over
   it, placed with `learnShape3d.proj`). The big circle (ball) is always drawn: it is the line the throwing out is
   judged by.
5. The sentence under the picture (`#learnShapeSay`) says at every part what is happening, in one or two short
   plain sentences, with the step and the part ("Step 3, Stretch: ..."). Texts that are fixed:
   - Out, Julia: "Step {k+1}. First, where the dots are now: each has already taken {k} step(s) from its starting
     place."
   - Out, Mandelbrot, k = 0: "Step 1. Every dot starts at the centre. What differs from dot to dot is its number c:
     the place it came from."
   - Thrown out: "The dots that landed outside the big circle are thrown out." (ball in 3D)
   - Home: "The dots that are left go back to where they started. Those starting places are shape {k+1}."
   - For each move of the rule: its name as One point shows it, and one sentence about what it does to every dot
     (2D, plain power 2: "Turn: every dot's angle is doubled.", "Stretch: every dot's distance from the centre is
     squared, so dots further out than 1 move out and dots nearer than 1 move in.", "Slide: every dot is moved by
     c." and for the Mandelbrot shape "Slide: every dot is moved by its own c."). For other powers and for the moves
     of the 3D approaches write the like sentence from what the move does; where a move has no short general
     sentence, give its name and "every dot makes this move by its own amount; Follow One point shows it for a
     single dot".
   The standing sentences between steps stay as they are today.
6. Play takes longer per step than today, by the Speed choice; a whole step at Normal should take about five
   seconds. Back, Forward, the ticks, Start again, the keys and the slider keep their meaning (whole steps).
7. The dots' places are exact: a dot's place after the parts of step k + 1 is the lab's own rule applied k + 1
   times to its start, and the dots thrown out at each step are the ones the fine picture's own numbers throw out.

### 2.2 One point: a grid of points, and plain words for the choices

1. The select **Show** gets a fourth choice, **A grid of points**: dots laid out evenly over the big circle
   (radius 2; a line: a row of dots from -2 to 2; space: over the big ball), each with a colour of its own from
   where it starts, a handful marked a little larger. They take the same moves as the point, each by its own
   amount, and they are **not laid out afresh**: each dot goes on from where the last step left it, as the point
   itself does. "Start again" (and anything that starts the steps again) lays out a fresh grid. Dots that have gone
   far off are simply no longer in the picture; the picture's frame does not grow to hold them.
2. "All directions at once" is renamed, by space: a line "A row of points along the line", a page "One point for
   every direction (a ring)", space "One point for every direction (a ball)".
3. The help of the select says what each choice is, in these words (adapt only the nouns to the space):
   "The extra points take the same moves as your point, each by its own amount, so you see what a move does to
   everything around the point. A small circle: points close around your point. One point for every direction: a
   direction is which way a point lies from the centre, without how far. These points all lie 1 from the centre,
   one in each direction, so they show what a move does to every direction at once. Both of these are laid out
   afresh at the start of every step. A grid of points: dots laid out evenly over the picture. These are not laid
   out afresh: each goes on from where the last step left it."
4. Under the select, one short line that is always on show while extra points are on show, saying what they are
   right now and whether they are laid out afresh (for example: "Ring: one point for every direction, all 1 from
   the centre. Laid out afresh at each step." / "Grid: each dot goes on from where the last step left it.").

### 2.3 Not to change

- Follow = A whole shape with Each step = At once: the pictures and the words exactly as in Version 21.
- Follow = One point with the three old choices: the pictures exactly as in Version 21 (only the label of the third
  choice and the help change).
- Nothing outside the Learn tab. Files that may change: `js/65-learn-steps.js`, `js/66-learn-view.js`,
  `js/67-learn-shape.js`, `js/68-learn-shape3d.js`, `css/65-learn.css`, `css/67-learn-shape.css`, and `body.html`
  only if a control cannot be added from JavaScript. **Not** `js/00-core.js`, `32-balls.js`, `40-render.js`,
  `46-mesh.js`, `80-ui.js`, `90-boot.js`: Track A is changing those. If one of them truly has to change, keep it to
  a few lines, mark them, and say so at the top of your notes.

## 3. Words

Plain words only, the user's own where there is one: dot, point, step, move, turn, swing, stretch, slide, centre,
the big circle, the big ball, thrown out, starting place, where it is now, c, the power, shape. Do **not** use:
iteration (say step), orbit, preimage, image, map, mapping, domain, parameter, dynamical, escape, radius (say "2 from
the centre"), lattice, sample, critical, conformal, or any internal name (phase, part ids, plan, companion).
Sentences under pictures: two short ones at most.

## 4. What must be true (the checkers measure this)

1. **Numbers.** For Few, Some and Many, 2D (powers 2, 3, 2.5, -2; with and without the modifiers; Mandelbrot and
   Julia; c at the basilica, the rabbit and a c outside) and 3D (every entry of the Approach list that the whole
   shape can show, power 2 and 3): each dot's place at the end of the moves of step k + 1 equals the lab's own rule
   applied k + 1 times to its start (within 1e-9 in JavaScript), for every step up to 16; and the dots thrown out at
   each step are those the fine picture throws out at their starting places (dots within a hair of an outline may
   differ; report how many).
2. **Nothing old changed.** Each step = At once: pictures at whole steps and half-way through a step identical to
   a page built from `base21a` alone, 2D and 3D, all three kinds; the words identical. One point with the three old
   choices: pictures identical. The rest of the lab: Balls on balls and one approach of each tab look as before,
   round 27's and round 28's own checks still pass.
3. **The transport.** Play, pause, Back, Forward, every tick, Start again, the slider dragged slowly forwards and
   backwards through all parts of a step, the keys, the three speeds; changing kind, 2D/3D, Dots, Each step, c, the
   power and the approach while it plays and while it stands. Nothing throws, nothing sticks, the sentence always
   fits the picture. No console error or warning.
4. **Speed.** With Many dots, a frame of the moving parts takes no longer than 20 ms in 2D and 35 ms in 3D on this
   machine (report the numbers; say how you measured).
5. **Can it be read** (the most important one; judged by looking at window shots and reading every sentence as the
   user would): at every part of a step, in 2D and 3D, Mandelbrot, Julia and Both, wide window and phone, light and
   dark: can a dot be followed with the eye from home, through the moves, to being thrown out or going home? Is it
   clear which dots are thrown out and why? Do the dots stand out from the backdrop? Does the sentence say what is
   on the screen in plain words (none of the words of section 3's list)? Is the new choice found without being told
   where it is? Does the grid of points under One point show what the help says? Is the line under Show true at
   every choice and space?

A defect is **major** when something the user asked for is missing or cannot be read, when a number is wrong, when
anything old changed, or when anything throws or sticks. Everything else is minor.

## 5. Where to work

An overlay on `base21a`, never `src/`:

    out/r29/learn/overlay/<the files you changed, under js/ and css/>
    out/r29/learn/BUILD.txt      the one build line:
    PYTHONIOENCODING=utf-8 python -W ignore build.py --name r29-learn --base base21a --swap js/67-learn-shape.js=out/r29/learn/overlay/js/67-learn-shape.js ...
    out/r29/learn/NOTES.md       what you built, what you measured, what is not right, what you decided and why
    out/r29/learn/mk/            your scripts;  out/r29/learn/shots/  your pictures

Checkers work in `out/r29/learn-truth/`, `out/r29/learn-reader/`, `out/r29/learn-play/`, the fixer in
`out/r29/learn-fix/` (its overlay is the builder's overlay with its changes, in `out/r29/learn-fix/overlay/`), the
last checker in `out/r29/learn-final/`. Each builds its own page under its own name (`--name r29-learn-truth`,
...), so that no two agents write the same file in `dist/`.
