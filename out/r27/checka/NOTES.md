# Round 27, checker "arithmetic" (Track A): what I measured

Page under test: `dist/r27-checka.html`, built by me with the command in `out/r27/entry/BUILD.txt` (same bytes as
the builder's `dist/r27-entry.html`, md5 6a531a55...). Frozen page: `dist/r27-base.html` (`--base base18a`, same bytes
as `dist/r27-entry-base.html`). Window 1400x950, stage 862x701, dark. Everything below is measured by my own scripts
in `mk/` unless a line says "reasoned" or "not checked". Nothing here is taken from the builder's notes.

## In plain lines

- Neighbours at 55.56 % (the start, t = 1.4), at 25 % (t = 2.5) and up to 90.9 % (t = 1.05): the object on the
  screen is the object of the recipe. No ball missing, no hole, nothing added but single stray points in grazing
  close-ups, in the 2D view and in 3D, far and close. (Verdicts and distances: all three grids at t = 1.4 and 2.5. 3D pictures: square, honeycomb and line at
  t = 1.4, square only at t = 2.5 and 1.05.)
- Neighbours at exactly 100 % (t = 1, the end of the dial): the 3D picture breaks. Close in, 3.5 to 4.6 % of the
  picture is black where balls are (balls hundreds of pixels across among them), and from every distance some solid
  is drawn where there is no ball (blobs 7 to 25 px wide at the starting depth).
- The distance handed to the ray marcher: never longer than the true distance where nothing is held up (the
  number 3D models are made from, read from the page; the 2D view uses the same number). In
  the 3D picture it IS longer near a skin (by design of the builder, at most 2 px, measured up to 0.74 px at
  t >= 1.4 and 1.75 px at t = 1): a literal break of the rule; at t >= 1.05 no ball is lost by it, the stray points may come from it (reasoned).
- Old pictures unchanged (18 states, 0 pixels), old smoke lists 90 of 90, no console errors, no new shader
  warnings, the new group is not slower than the old one.
- The row in the Approach list does what the decisions say; `APPROACHES` still has 21 entries.

## My tools (in `mk/`)

- `ballslib.py`: (a) the recipe written from the text of ROUND27.md; (b) `out/r25/klein/tree.py` called as it is;
  (c) BRUTE FORCE that does not use the recipe: `enum_cell` walks the group (slides by whole numbers, the two sphere
  inversions) from the two walls and lists every ball down to a radius, `picture_balls` carries the list into
  picture coordinates, `NearBalls` gives the exact distance from a point to the nearest ball of the list;
  (d) `glsl_de`: `de()` of `GL_BALLS` ported line by line (TRAP_SOLIDS 0, no landing length).
- Checks of the tools themselves: listed balls against the recipe (80 rounds): centre inside at 20000 of 20000 and
  a point at 0.98 of the radius inside at 20000 of 20000, in each of the 9 settings; in the box the recipe and
  "inside a listed ball" agree except in balls smaller than the list holds. My port against the shader's own
  number: mean relative difference 1e-7 to 2e-6 on box points (t >= 1.4).
- The shader is read through the lab's own `sampleSlice` (alpha = what `de()` returns with nothing held up). I
  checked where its samples lie (x = cx + side * ((i + 0.5) / N - 0.5)) against `ballsEstimate`: 1.6e-5.

## 1. Verdicts: shader against twin against tree.py (`verdicts.py`, `logs/verdicts-16-40.txt`)

Per setting (3 grids x t = 1, 1.4, 2.5) and depth (16 and 40 rounds): 20250 points of the flat cut (10 level pieces
of 45 x 45 points, each piece with a random centre and width) and 22500 points in space (100 pieces of 15 x 15 at
random heights). 36 runs, 769500 points.

- twin (`ballsInside`) against tree.py: **0 of 769500 differ**. Twin against my own writing of the recipe: 0.
- shader against twin, t = 1.4 and 2.5: **0 of 513000 differ**.
- shader against twin, t = 1: **31 of 256500 differ** (per run 0 to 8 in the flat cut, 0 or 1 in space). At every
  one of them the twin's own distance is under 1e-7, or one of the two is "undecided after the rounds" (which both
  count as inside). They are not near big skins only: at t = 1 the estimate is tiny in the thin gaps next to every
  kiss (see 3). Single precision against double precision; no ball's worth.
- This depth against 80 rounds: 0 differences at t = 1.4 and 2.5 (both depths). At t = 1: 169 to 182 of 20250 in
  the flat cut at 16 rounds, 15 to 22 at 40 rounds (points still undecided count as inside, as in tree.py).
- Second way, the 2D view as it is on the screen (`flat2d.py`, `logs/flat2d.txt`, 7 pictures, every pixel placed by
  the lab's own rule and given a verdict by the recipe): at t = 1.4 and 2.5 (z = 0 and two other heights, all three
  grids) no pixel that lies 3 px inside the recipe's outside has the inside colour and the other way round; the
  227 to 1200 pixels that differ are a band 1 px wide at the skins. At t = 1 see defect A2.
  Seen: `shots/flat2d-g0-t1.4-r16.png` (sharp chain of circles), `shots/flat2d-g0-t1-r16.png` and its `-diff.png`.

## 2. The 3D picture against a brute-force picture (`views_page.py`, `views_ref.py`, `logs/views.txt`)

Reference: the list of balls (radius >= 0.2 px on the screen; >= 1 px at t = 1 and 1.05) seen through the lab's
camera, every ball cut by every pixel-centre ray with the exact ray-and-sphere formula. No march, no estimate.
The lab: `pick()` at every pixel (2 views, 604262 picks each) or at every second pixel of every second row
(151281 picks), and the finished picture. 20 views; depth 16 and 40.

t = 1.4 (start) and 2.5, 12 views (start view and a second eye from below, close-up 0.30 from the touching point
(0.525, 0, 0), a second close-up eye 0.20 away in the plane that touches both big balls; square, honeycomb, line):

- **Holes** (reference hits a ball, the lab's ray stops nowhere): **0** in all 12 views (0 of 148553 and 0 of 604262
  in the two every-pixel views).
- **Passed through** (lab stops more than 1 px behind the reference): 0 in all 12.
- **Balls lost**: 0 of the 13064 balls seen on 3 or more pixels in the every-pixel close-up (0 of 3282 in the start
  view); of the balls with a radius of 0.2 to 0.5 px that the reference shows on at least one pixel, 0 of 60456 are
  without a lab stop. Largest missing ball: none (0 px).
- **Added**: the lab draws everything about one pixel fat: its stopping points lie a median 0.86 px above the
  nearest ball, 99 % within 1.23 px, most 1.39 px (the marcher's level, the same for every solid in the lab). So it
  stops on 547 to 4710 rays that pass a ball within 1.4 px. Nothing further out in 10 of the 12 views.
  In the second close-up eye (`kiss-eyeB`, looking along the gap between the two big balls): 108 of 151281 grid
  points stop in the open, up to 5.6 px from the nearest ball, single points in a line down the gap (seen in
  `views/kiss-eyeB-r16-diff.png`, bright dots). Largest added thing at t >= 1.4: 5.6 px off, 2 px wide.
- Depth 16 and depth 40 give the same numbers in all four pairs.
- Seen: `views/start-r16.png` beside `views/start-r16-ref.png` (same balls in the same places),
  `views/kiss-eye1-r16.png` beside `-ref.png` (same), `views/eye2-r16.png`, `views/hex-start-r16.png`,
  `views/line-start-r16.png`, `views/kiss-eyeB-r16.png`.
- t = 1.05 (90.9 %): start view and close-up: 0 holes, 0 lost of 871 / 4955 balls, 0 and 3 points of solid by depth;
  191 and 1043 single points stop in the open (up to 4.2 and 7.0 px off). Seen: `views/t105-start-r16.png`.
- My own mistake, kept: my first second eye for the close-up stood inside the middle ball; the picture was black, as
  it should be (`views/kiss-eye2-*.png`). Not a finding.

t = 1: see defects A1 and A2.

## 3. The distance is never too long (`bound.py`, `bound_kiss.py`, `logs/bound-*.txt`)

True distance = exact distance to the nearest ball of the brute-force list (complete to radius 3.3e-4 at t >= 1.4,
1e-5 for the line grid, 5e-4 near the middle and coarser at the far ends for t = 1; next to the touching point
complete to 1e-5 and finer). Shader's number = alpha of `sampleSlice`.

- Box, per setting 22500 points in space + 20250 flat at 16 rounds + 22500 in space at 40 rounds (9 settings,
  521449 outside points): shader longer than true at **8 points, all with the line grid, all at the level of single
  precision** (the three I printed: 3e-8 to 9e-8); longer by more than 1e-6 and more than 0.1 %: **0**.
- Near skins (100 pieces of 15 x 15 points, side 0.001 to 0.1, on the skins of random balls; 9 settings, 101963
  outside points): longer than true at 7 to 18 points per setting with the square and honeycomb grids and 839 to
  1005 with the line grid, **all by less than 5e-7** (the shader holds the point's own place to about 1e-7); longer
  by more than 1e-6 and more than 0.1 %: **0**. My double-precision port of the same lines: 0 (14 points by under
  6e-12).
- Next to the touching point (27000 points within 0.045 of it, true distances with median 3e-5 to 6e-5; square and
  honeycomb at t = 1.4, square at t = 1; 16 and 40 rounds): 7 to 26 points longer, all under 2.2e-8; beyond noise 0;
  port 0.
- Probing with the recipe (48 probes on the sphere of 0.999 x the shader's number round each point): a ball found
  at 0 of the box points; at 0 to 20 of the near-skin points per setting (the line grid: 7, 12, 20), which is the
  noise class above.
- How short it is (square and honeycomb grids; the line grid is tighter): at t = 1.4 the true distance is within
  1.5 x the shader's number for 97 % of box points and 35 to 46 % of near-skin points (within 5 x: 96 to 98 %). At
  t = 2.5: 91 to 93 % and 43 to 44 % (5 x: 100 %). **At t = 1: 0 % within 1.5 x, 3 to 16 % within 2 x in the box;
  near skins 30 to 52 % within 5 x.** Short is safe, but see A1.
- **The 3D picture's own number** cannot be read from the page; from my port, with the builder's rule
  d = min(best, max(free, 2 * uDetail * gPix)) and the start view's pixel: it is **longer than the true distance at
  4 to 38 % of the near-skin outside points** (0 to 11 % of box points), by at most 0.74 px at t >= 1.4, 1.75 px at
  t = 1 (by construction never more than 2 px). Defect B.

## 4. Unchanged behaviour (`unchanged.py`, `logs/unchanged.txt`, pictures in `same/`)

18 states, each set through the page's own controls with the same script on both pages: Mandelbrot (start, 2D,
Mandelbulb, Quaternions 4D at power 3, example Spiky coral), Julia (start, rabbit with Lathe, 2D, cut plane), the old
Kleinian group (start, entries 2, 4, 13, entry 3 in 2D, example Pearls and balls, 2D at height 0.3), Learn on (two
states).

- Picture alone (canvas, everything over the stage hidden): **0 pixels differ in all 18**.
- Whole window: 0 pixels in the 11 states outside the Kleinian view. In the 7 Kleinian states about 73000 to 75000
  pixels differ, all inside the Kleinian panel (x 964 to 1323, y from 401): the new choice "Group" stands at the top
  and the old controls sit about 108 px lower (decision 2). Seen: `same/new/s12-...-full.png` beside `same/old/...`.
- The frozen page against itself: 0 pixels in the picture; 166 and 34 pixels of the zoom slider in two states.

## 5. Old smoke lists (`smoke_run.py`, `logs/smoke-checka.log`, `logs/smoke-base.log`)

The list as `out/r22/entry/NOTES.md` names it (62 + 5 + 9 + 10 + 3 + 1 = 90 steps), put together from the original
files. My page: **90 of 90, exit 0, no console errors** (301 s). Frozen page, same list: 90 of 90. The result lines
differ only in counts that the new controls change (75 dials, 25 selects, 14 reset buttons against 73, 24, 13; the
open Approach list 691 px tall against 610) and in two eased camera numbers.
Console errors in all my runs on the page (106 logs): none. Shader compile messages (`shaderlog.py`): the old
Kleinian program gives the same four warnings on both pages (two "division by zero", `f_colSide`, `f_colPick`
"potentially uninitialized"); the new program gives the same four and no other.

## 6. Time to the first picture (`speed.py`, `logs/speed.txt`)

Fresh browser each time, one click, clock from the click; 7 trials each, in turns:

- old group (Show: Kleinian): first paint median 742 ms, finished picture 922 ms (868 to 977)
- Balls on balls by its row: first paint 640 ms, finished 781 ms (733 to 1152)
- Balls on balls by Show: Kleinian with the group already chosen: first paint 675 ms, finished 838 ms (746 to 1039)

The new group is not slower (0.85 to 0.9 of the old group's time). Drawing alone, program already built
(`logs/speed-dials.txt`, 3 each): old group 211 to 223 ms; Balls on balls 116 to 311 ms in every start view; close-up
at t = 1.4 303 to 311 ms; close-up at t = 1 757 to 1167 ms.

## 7. The row, and leaving it (`row.py`, `logs/row.json`)

- Before: mode m, group 0, approach 0 (mercator). `APPROACHES`: 21 entries, none of them the new object; the row is a
  button under the heading "A cousin, not a rule", in the open menu, outside `#rules` (21 radios there).
- One click on the row: mode k, group 1, approach still 0; Show reads Kleinian, the group choice reads Balls on
  balls, the menu button reads "Balls on balls", camera at the start view (yaw -1.25, pitch 0.5, 3.765), menu closed,
  39 of 165 probes hit; `kleinTrouble()` '' and `kleinSwallowed()` false.
- Choosing Lathe afterwards: mode m (where the row was chosen from), approach lathe, camera reset; group stays 1, so
  Show: Kleinian brings Balls on balls back. From the Julia view the way back is to Julia. Reached by Show: Kleinian
  and the group choice, an approach leads to the Julia view. Under Learn the row leaves Learn. Reset everything:
  mode m, group 0, approach 0, dials 1.4 / square / 16.
- First group, as on the frozen page: the Approach section is hidden and a (scripted) choice of approach changes
  `S.approach` and stays in the Kleinian view. With Balls on balls the Approach section stays on show (note C).
- Seen: `shots/row-menu-open.png` (the row at the bottom of the open list, whole).

## Defects

**A1 (major). Neighbours at 100 % (t = 1): holes in the 3D picture.** Close-up 0.30 from (0.525, 0, 0), yaw -1.25,
pitch 0.5: the lab's ray stops nowhere at 5289 of 151281 grid points at 16 rounds and 6913 at 40 rounds (black in
the picture, `views/t1-kiss-r16.png`). I walked 300 of those rays per view with the exact inside test in
quarter-pixel steps: all 300 meet a ball; 125 of 300 a ball they stay in for more than 2 px, 50 to 62 more than
10 px, 20 to 21 more than 50 px (`logs/t1-holes-*.txt`). Where my list is complete the reference has 2098 / 3049
hits that the lab misses, blobs up to 42 / 54 px wide, and a ball 441 px across lost on all its 21 points
(`views/t1-kiss-r40-diff.png`). From 2.0 away: 8 holes of 143109 reference hits. In the lab's own start view at
t = 1: none. At t = 1.05: none (0 rays without a stop in the close-up). My reading (reasoned, not measured): where
the certain room is under 2 px the ray goes about one pixel a step, the room is tiny over large regions at t = 1 (see
3), and the ray runs out of its steps.

**A2 (minor). t = 1: solid where there is no ball.** 3D, start view of t = 1: 1733 of 30485 stopping points are
solid that only the depth of the search puts there (blobs up to 7 px) at 16 rounds, 385 (2 px) at 40 rounds; from
2.0 away 7142 points (25 px) and 1607 (9 px), plus 2434 / 6082 points that stop in the open (blobs 9 / 18 px, up to
54 px from any ball of 1 px or more). 2D view, framed, t = 1: 2113 pixels (16 rounds) and 1738 pixels (40 rounds) of
604262 are painted inside although 300 rounds call them outside and nothing inside is within 2 px; widest blob 7 and
5 px. Raising the depth does not clear it: the rest comes from the estimate being far too short there. The page says
nothing about it at 100 %.

**B (minor, the builder named it). In the 3D picture the marcher's number is longer than the true distance** at 4
to 38 % of the points near a skin, by up to 0.74 px (t >= 1.4). No ball is lost by it at t >= 1.05 (section 2).

**S (minor). Stray stops in the open.** t = 1.4, eye 0.20 from (0.525, 0, 0) at yaw 1.5708, pitch -0.6 (looking
along the gap between the two big balls): 108 of 151281 grid points stop up to 5.6 px from the nearest ball, single
points in a line (same at 40 rounds). t = 1.05: 191 (start view) and 1043 (close-up) single points, up to 4.2 and
7.0 px off. In the other ten views at t = 1.4 and 2.5: none.

**C (to decide, the builder named it).** With Balls on balls on show the Approach section stays on the page; with the
first group it is hidden, as on Version 18.

## Not checked

- The last bullet of 2.2 (sizes, overlap, words): the other checker.
- Trap colours, inside colourings, cut face, picture export, 3D model export, the examples list, the panel reset,
  Learn with Balls on balls behind it: only as far as the smoke list and section 7 touch them.
- Between t = 1 and 1.05, and above 2.5. Depths typed above 40. The line grid and t = 2.5 close up. The honeycomb
  grid at t = 1 in 3D.
- Balls smaller than my lists hold (0.2 px in the pictures; 3.3e-4 in the box test, 1e-5 next to the touching point).
- 14 of the 20 views were picked at every second pixel of every second row: a missing ball under about 3 px across
  could slip through there (the two every-pixel views would have caught it).
- The fly camera, a phone-sized window, the light theme, a lost graphics context.
- Times were taken while other jobs ran on the machine.
