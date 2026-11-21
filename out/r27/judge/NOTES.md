# Round 27, judge (Track B): working notes

Everything is in `out/r27/judge/`. The answers are in `ANSWERS.md`; this file says where each number comes from,
where my numbers differ from the explorers', and what I did not check.
Run as `PYTHONIOENCODING=utf-8 python -u -W ignore <script>` from this folder.

## What I read and looked at

- `docs/ROUND27.md`, `out/r25/judge/ANSWERS.md`, the three `NOTES.md` (measure, respace, pinch), `out/r25/klein/tree.py`,
  `out/r21/lib/mem.py`, respace's `carry.py` and `tests5.py`, pinch's `pinchlib.py`, `fam.py`, `objs.py`, `orange.py`.
- Explorer pictures opened: measure `fit-c-1`, `fit-c-084`, `buds`, `kiss`, `rabbit-nearest`, `family-rings`, `family-slide`;
  respace `carried-c-1`, `carried-rabbit`, `carried-ways`; pinch `pinch-flat`, `pinch-solids`, `orange`.
- Not opened: measure `fit-c-075`, `fit-sheet`, `buds-ruler`, `family-t`, `family-klein`, `rabbitfit`; respace `match`,
  `zoom-upright`, `cuts`; pinch `pinch-turn`, `b-rabbit` and the single solids. Nothing in ANSWERS.md rests on them.

## My tools

- `jlib.py`: my own recipe of the balls object, written from the text of ROUND27.md section 1 (not from `tree.py`), with the
  sideways slide and two coarser grids; the true flat picture; the wrong share; a renderer (first inside block on each
  line of sight, front to back, skin then placed by halving).
- `jcarry.py`: respace's way A set up for measuring. Way A sends (flat point, height h) to (natural coordinate b of the
  body the point stands over, magnification A times h). b and A depend on the flat point only, so I tabulate them once on a
  flat grid of step 0.001 (with respace's own `enter` and `bott`, 80 steps) and ask MY recipe plus respace's family test
  in the round frame. Checked against respace's point-by-point function: the same picture (`j10`, and the two
  renders in `w-carrylow-rabbit-front+carryx-rabbit-front.png`: 29260 against 29224 lines of sight hit, 136 against 128 specks).
- `jrender.py`, `jview.py`, `jcompose.py`: solids (kept in `cache/`), working pictures `w-*.png`, the three pictures.

## What I measured (log named)

1. `j1_recipe.log`: my recipe against `tree.py`, 200000 random points, t = 1, 1.4, 2.5, three grids: 0 verdicts differ in all
   nine runs (1 point undecided by mine at t = 1, twice). Rounds at t = 1.4, square grid: undecided after 2 / 3 / 4 / 6 / 8
   rounds: 15614 / 1691 / 307 / 13 / 0 of 200000; no decided point ever changes. Flat cut of the 3D object = line object:
   0 differ of 200000 (t = 1.4 and 2.5; at t = 1, 275 points undecided, 0 differ).
2. `j1b_ball.log`: four bodies (middle ball, right neighbour, flat bud on top, bulb toward the eye), centre and radius from
   my own arithmetic: of 200000 points on a shell at 1 - 0.0000001 of the radius, 0 are not inside. On the shell just
   outside, about 21400 of 200000 lie in buds, the same at every shell distance (0.001, 0.00001, 0.0000001).
   New, small: about 11 of every 100 parts of a ball's skin have a bud standing over them at any height.
3. `j2_fit.log`: wrong share of the true area, 900 x 650 grid; search over the size of the picture and the dial t on 80000
   random points. c = -1: 38.5 at the lab setting, 38.5 at best. Best: -0.95: 27.9; -0.9: 20.7; -0.86: 17.1; -0.84: 16.6;
   -0.82: 16.7; -0.8: 17.3; -0.75: 20.6; -0.7: 22.4; -0.5: 19.7; -1.1: 49.0. Best t: 2.10 (c = -0.5), 1.48 (-0.7), 1.28 (-0.75).
   (My c = -1.25 number, 74.6, is not comparable with measure's 52: my search did not go below a middle ball 0.8 wide.)
4. `j3_kiss.log`: degrees of a small circle round the meeting point that lie outside, radius 0.1 / 0.03 / 0.01 / 0.003 / 0.001:
   c = -1: 144 / 140 / 140 / 130 / 138. Balls: 30 / 6.7 / 2.2 / 0.64 / 0.21. c = -0.75: 5.4 / 0.48 / 0.08 (then too slow to decide).
   `j12_opening.log`: inside degrees round the meeting point: c = -1 about 220 (two bodies, about 110 each), rabbit about
   250 (three bodies, about 83 each, buds counted in). Stretch and turn there: 1.2361 with 180.00 degrees; 1.1073 with 119.94.
5. `j9_buds.log`: balls object: a walk round the middle ball's rim meets a bud within 0.0002 of the way of every
   fraction with bottom number up to 8 (1/2 at 0.590 of the way from the meeting point to the top bud, 1/3 at 0.410, 2/3 at
   0.749, 1/4 at 0.312). True c = -1: the 14 biggest bodies attached to the middle body sit at 1/2, 1/4, the eighths and the
   sixteenths of a full turn of the body's own coordinate, each within 0.0003.
6. `j7_family.log`: the dials, tested by asking whether the recipe contradicts itself under the object's own moves
   (60000 points, 5 to 8 moves each). t = 2.5, 1.4, 1.0: 0 contradictions, three grids. Below 1, for the two coarser grids:
   0 at t = cos(180 / m) for m = 3, 4, 5, 6, 8; between them 129 to 29021 (1 and 3 at t = 0.95). Square grid with slides by
   every whole number: no outside at all at m = 3 and 4 (and at t = 0.6); at m = 6 and 5 I get 5 and 8 contradictions of 480000
   (between rungs 844 to 8952): not zero, not resolved. Slide at t = 1.15: line 0 and 1/2 clean, 0.25 and 0.1 not;
   square grid (0,0), (1/2,0), (1/2,1/2) clean, (0.25,0), (0.25,0.25), (0.3,0.1) not; coarser grids clean at every slide tried.
7. `j8_rabbitfit.log`: the chain of balls against the true rabbit, free t, size, turn and shift: 56.1 of 100 wrong at best
   (one plain disc: 68.0).
8. `j5-flat.log`: way A, 30000 random flat points, respace's own function with 300 steps against my truth (2000 steps):
   c = -1: 0 wrong (4565 truly inside); rabbit: 0 wrong (4159). Lifted by 0.000001: 0 lost, both. Lifted by 0.001: 16 and 59
   lost; by 0.01: 103 and 258.
   `j5-family.log`: respace's family test on nine explicit balls (my arithmetic): right for every one of 36000 points.
   `j5-round.log`: 79 first bulbs off the flat plane (each a known ball; its carried shape integrated over the table).
   c = -1, middle body: 59 whole, 20 cut by an upright wall; large 1.01, 1.48 (four times); 28 medium: middle value 1.55,
   worst 2.65; 26 small: 1.21, worst 1.90. Left neighbour: large 1.36 to 1.69; medium 1.61, worst 3.67. Rabbit, middle body
   (respace did not measure it): large 1.01, 1.66 to 1.68; medium 1.88, worst 3.98; small 1.32, worst 2.57.
   `j5-pieces.log`: loose pieces above the flat plane: c = -1: 38 at blocks of 0.01, 160 at 0.005 (0.03 and 0.02 of 100 parts
   of the solid); rabbit 66 and 336 (0.11 and 0.08). Skin of the middle body near the meeting point (height at the middle
   0.50 / 0.38): c = -1: 0.30, 0.26, 0.22, 0.18, 0.16, 0.15 at 0.2 ... 0.002 from it; rabbit: 0.27, 0.27, 0.29, 0.31, 0.35,
   0.36, 0.43: it rises.
   `j10_needles.log`: columns of the solid taller than 1.0: c = -1 over 16 flat grid points of 1.4 million, rabbit over 106 of
   1.3 million (taller than 0.6: 120 and 268). They stand at the points where buds are attached. Asked again point by point
   with respace's function: tops 0.42 to 1.59 (c = -1) and 0.7 to 1.55 (rabbit) at the grid point or 0.0003 beside it. So the
   needles are real, a few ten-thousandths wide, and their height at one exact point is not a stable number.
   `j11_misc.log` b: way A is its own mirror image above / below (0 of 200000 change), and for c = -1 left / right and up /
   down (0); rabbit: half turn 0. Turned by a random angle round the x-axis: 21 (c = -1) and 94 (rabbit) of 100 parts
   change; the balls object itself 12.
9. `j11_misc.log` a: respace's flat match, 30000 points: the object as it stands wrong at 1702 (38.0 of 100); asked at the
   matched point wrong at 0. c: the re-spacing sends 1/2, 1/3, 2/3, 1/4, 2/5, 3/5, 3/4, 1/5 to 1/2, 1/4, 3/4, 1/8, 3/8, 5/8,
   7/8, 1/16 exactly; the biggest bulb's 26 degrees come from 11.3; the last 10 degrees of a ball's rim next to a kiss from
   the last 0.069 degrees of the true rim.
10. `j6_pinch.log`: pinch's objects against my truth on my grid. True layout with lemons: 8.4 (c = -1), 11.6 (rabbit); with
    the true opening 29.7, 38.4; with balls 42.4, 64.5. Two fitted moves, best: 16.1, 40.8; pinned with the true opening
    35.0, 57.8. Flat area lying in two or more bodies of the lemon trees: 0.3 and 0.9 of 100 parts. No tip or axis of any
    body off the flat plane (0.0 in every object); above and below never differ. Two fitted moves, c = -1: 0 of 1764
    bodies off the x-axis. Lemons: 1.91, 1.43, 2.75, 1.73 times as long as wide at openings 110, 140, 80, 120 degrees.
    `j11_misc.log` d: turned tree: 8.4 / 11.5 / 14.6 / 11.5 of 100 wrong at 0 / 90 / 137.5 / 180 degrees.

## Where my numbers differ from the explorers'

- respace, loose pieces: 22 (c = -1) and 50 (rabbit); mine 38 and 66 at the same block size, and 160 and 336 at half the
  block size. I follow the flat orbit 80 steps, respace 48. The count grows as the blocks get finer; it is not a fixed number.
- respace, "highest block 0.74 / 0.56", "short thorns" for c = -1: at finer sampling both sets have needles taller than 1
  (item 8). respace's solids were 560 x 420 x 300 blocks, mine 1000 x 750 x 700.
- respace, medium bulbs: middle value 1.63 on 16 bulbs of a quarter; mine 1.55 on 28 of a half. The same picture.
- respace, "2 of 2788 lost when lifted by a millionth" (rabbit): mine 0 of 4159.
- pinch, rabbit lemons: 11.5; mine 11.6. measure, c = -1: 38.1 / 38.3; mine 38.5 (38.6 on the grid of picture 1). Round 25: 38.6.
- pinch's `orange.py`: the two bodies are built as round cones with their tips at the two fixed points, so "they share
  both tips" is put in by hand. What the build shows is that such a picture exists without bodies running into each
  other. The claim itself rests on the short proof in pinch's notes, section 6, which I read and find sound (a body kept
  by a stretch and by its undo-move holds points that run into the second fixed point; that point cannot lie in the
  inside of a body, or the body would be everything).

## Not checked by me (so not passed on as fact)

- measure: the ring of three against the rabbit (89 of 100); the bud sizes and "size over distance" numbers; "never
  spirals" (turn 0.0000) and everything about the lab's old Kleinian group; the honeycomb grid's slides; the rungs for
  the honeycomb grid; the solids of `family-*.png` (seen, not rebuilt).
- respace: ways B, C, F, G as solids (seen in `carried-ways.png` only; of B I re-measured the squeeze of the re-spacing, not
  the bulbs); the 23 bodies of the flat match one by one; the cost in a shader; whether way A changes with the bulbs of the
  neighbours added.
- pinch: way (b) (more fitted moves fill the plane); the three ways of fitting one by one except "pinned" and the best;
  the volumes against the one-plane solid; `pinch-turn.png`.
- Nothing in the lab page, no shader, no browser. No c other than -1, the rabbit and the x-axis values of item 3.
- "The same family tree" (halvings and fractions number the same tree) is reasoned, not measured, by measure and by me.

## House rules

- Bent twice. (1) `jrender.py` was patched once by a small python script given to the shell as a here-document instead of
  the editor (the file as it stands made every solid). (2) One background job started two of its three streams in the
  workspace root by mistake; they failed at once and left two small error logs there (`render-2.log`, `render-3.log`),
  which I removed. Nothing else was written outside `out/r27/judge/`; nothing under `src/`, `base*/`, `out/r25/`, `out/r21/`,
  `out/r26/`; `squaring-lab.html` untouched; `build.py` never run; nothing published; no browser.
- Importing `tree.py`, `carry.py`, `pinchlib.py` and the bench library wrote no files in their folders (they only read).
- The `.log` files here are console output of the scripts caught by the shell (`| tee` or `>`); scripts, notes and answers
  were written with the editor.

## Files

`jlib.py`, `jcarry.py`, `jrender.py`, `jview.py`, `jcompose.py`; checks `j1_recipe.py`, `j1b_ball.py`, `j2_fit.py`, `j3_kiss.py`,
`j5_carry_tests.py` (flat | family | round | pieces), `j6_pinch.py`, `j7_family.py`, `j8_rabbitfit.py`, `j9_buds.py`,
`j10_needles.py`, `j11_misc.py`, each with its `.log` (`j12_opening.log` is a one-off printed from the shell);
`cache/` (tables and depth maps); `w-*.png` working pictures; `1-how-close.png`, `2-carried-over.png`, `3-pinched.png`.
