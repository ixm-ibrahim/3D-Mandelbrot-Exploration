# Round 21, agent "frame": the orbit carries a whole frame

Every statement is marked **measured** (a number I computed), **seen** (in a picture I looked at) or **reasoned**.
All paths are relative to the project root. Code: `out/r21/frame/myrules.py` (all rules), `chk.py` (the two numbers
per rule, written to `numbers.txt`), `cuts.py` (sheets of flat cuts), `sheet.py` (rough solids through the library),
`extra.py` (other eye positions, close-up), `measure.py` (numbers behind the reasoning, written to `measure.txt`).

## 0. Result in four lines

- Nothing in this family passes. No rule here has round buds off the flat page that are not ribs, and none keeps the
  rabbit in separate clean bodies while doing anything the plain one-plane rule does not already do.
- Exactness on the flat page leaves the frame only one kind of motion: tipping the page over. Turning the frame
  inside its own page is forbidden outright (section 1).
- Tipping comes in three kinds, and each fails in its own way (section 3): the page tips TOWARD the orbit (all the
  way: ribs and rings like the lathe, shards for the rabbit; part of the way: the one-plane blob with a crease),
  the page is carried WITH or AWAY from the orbit (the flat picture loses all thickness: nothing off the page),
  and the mixed "frame turns as the point turns" (bodies melt into one lump with a groove).
- `along` stays better than everything here on the basilica, and `oneplane` stays better on the rabbit.

## 1. What exactness on the flat page demands (worked out before coding)

Notation. The one-plane rule P(a, b, w) = f (a^2 - b^2, 2ab, 2rw), r = |(a, b, w)|, f = r^2 / (r^2 + w^2).
The frame E = (e1, e2, e3): real axis of the page, its "up", out of the page. Start: (x, y, z).
Squaring in the frame: S_E(v) = A e1 + B e2 + W e3 with (A, B, W) = P(v.e1, v.e2, v.e3). Orbit: v' = S_E(v) + c.

1. **A turn of the frame inside the page breaks the flat picture, always.** If the frame is turned about its own e3
   by alpha, a flat point z is squared to exp(-i alpha) z^2 (reasoned: turn back by alpha, square, turn forward by
   alpha = 2 alpha back, alpha forward). Measured: the largest difference from exp(-i alpha) z^2 over 20,000 flat
   points is 1e-15 for alpha = 10, 45, 90, 180 degrees, and the difference from z^2 is 0.8 to 8.9. Nothing inside the
   family can cancel this except turning back, which is the same as not turning.
2. **A tipped page throws flat points off the page.** For a page tipped about the x-axis by t the flat point (x, y)
   lands at height f 2y sin t cos t (x - r), f = r^2 / (r^2 + y^2 sin^2 t) (reasoned; measured to 2e-15; heights up
   to 1.8 at t = 10 degrees). At t = 90 degrees the point stays on the page but is not z^2 (difference up to 8.7).
3. So on an orbit that lives in the flat page **the frame must not move at all** (the flips e2 -> -e2 and
   e3 -> -e3 are harmless: P does not see them). (Reasoned. Strictly, for one given flat point there is a
   one-parameter set of other frames that happen to give the right square; I know no recipe that hits it for all
   flat orbits and did not look for one.)
4. Any turn that is built from flat vectors alone (the point, its image, the direction of travel) by a recipe with no
   special direction is a turn about z, that is, a turn inside the page. So: **the whole turn can never be used.
   What may be used is its TILT part: om - (om.e3) e3, the part whose axis lies in the frame's own page. On a flat
   orbit the tilt part is exactly zero.** (Reasoned; measured: the four rules that use the whole turn or turn the real
   axis in the page differ from the flat picture on 1,277 to 3,770 of 20,000 verdicts in each of four tests; all 36
   tilt-only rules differ on 0 of 20,000 in each test, and no flat point strays from the page, 0.0e+00.)
5. **"Let the first vector follow the orbit" kills the turning in the squaring.** If e1 is turned (in the page) to
   the point, the flat rule becomes z -> |z| z + c: the length is squared, the direction is not doubled (reasoned;
   measured to 3e-15). Its "Mandelbrot set" is a small round disc (seen, `cuts-mandel-fails.png`, row 4). Out of the
   page the same happens: when the page tips until it holds the point and the real axis is carried along, a point of
   the upright sheet lands on the real axis of its own page and is sent straight out along its own direction
   (reasoned; seen as a row of round discs in the upright cut of `pt_1_tr`, `cuts-basilica-all2.png`).
6. Consequence: the third freedom of a frame (where the real axis points inside the page) is dead weight. It must
   be the x-axis on the flat page; off the page it can only be "carried along with the tip" (tr) or "set to the shadow
   of the x-axis" (px). I ran both wherever it made sense; the pictures are of the same kind (seen: `julia-b.png`
   rows 1-2 and 4-5; `cuts-basilica-all1.png` last two rows). **In effect this family is "the orbit carries a PLANE
   through the origin" (two numbers), and the scout's sheet family is the part of it where the plane always holds
   the x-axis (one number).** "Turn the frame about its own first vector toward the point" is the scout's family as
   long as e1 is on the x-axis; I did not code it.

## 2. The rules, in full

Common pieces (all in `myrules.py`):
- `rot(v, om)`: v turned by the turn vector om (axis om/|om|, angle |om| radians; Rodrigues).
- `turn_frame(E, om)`: all three vectors turned by om, then made orthonormal again (e3 normalised; e1 made square to
  e3 and normalised; e2 = e3 x e1). Measured: frames stay orthonormal to 7e-16.
- `short_turn(a, b)`: the shortest turn from direction a to direction b: axis a^ x b^, angle between them; zero where
  a^ x b^ is shorter than 1e-14 (same or opposite directions).
- `tilt_part(om, E)` = om - (om.e3) e3.
- `shadow_e1(E, n3)` (px): the frame with out-of-page vector n3, e1 = the shadow of the x-axis on the page,
  normalised (the old e1's shadow where the x-axis stands straight out of the page), e2 = n3 x e1.
- `tip_to_line(E, w, mu, mode)`: the out-of-page LINE of the page moves toward the line of w (a line has no sign,
  so two lines are averaged as lines): p = w.e3, wp = w - p e3, q = |wp|, m = wp / q,
  tau = 1/2 atan2(2 mu p q, 1 + mu (p^2 - q^2)) (mu = infinity: 1/2 atan2(2pq, p^2 - q^2), the smallest tip that brings
  e3 onto the line of w). tr: the frame is turned by tau about e3 x m. px: e3 becomes cos tau e3 + sin tau m and the
  real axis is set by `shadow_e1`.
- `tip_e3_to(E, n3, share, mode)`: the frame is turned by `share` of the shortest turn from e3 to n3 (tr), or e3 is
  moved so and the real axis set by `shadow_e1` (px).
In every rule F = S_E(v) is the square in the frame as it is at that moment, v' = F + c the new orbit point.

Rules that break the flat page (kept in `FAILS`, to show it):
- `turn_full` / `turn_full_half`: square; frame turned by all / half of short_turn(v, v').
- `transport_full`: square; frame turned by short_turn(t_before, t), t = direction of v' - v (carried: t).
- `e1_to_point`: before squaring the frame is turned about e3 until e1 points at the point's shadow on the page.

Rules that are exact on the flat page (`RULES`, 36 of them):

A. The frame turns as the point turns (tilt part only):
- `turn1`, `turn50`, `turn25`: square; frame turned by 1, 1/2, 1/4 times tilt_part(short_turn(v, v')).
- `turnsq`: the same with short_turn(v, F) (c not counted), share 1.
- `turnsin`: square; frame turned by tilt_part(v^ x v'^) (the sine of the angle in place of the angle).
- `turnarea`: square; frame turned by tilt_part(v x v') (not unit vectors).
- `transport`: square; frame turned by tilt_part(short_turn(t_before, t)), t = direction of v' - v; nothing at the
  first step. This is "carried parallel along the path, no spin about the direction of travel", tilt part.
- `keep_tr`, `keep_px`, `keep50_tr`: the frame is carried by the turning part of the squaring itself. On each ball
  round the origin P sends the compass (east, north) at a point to the compass at its square, so the turning part Q of
  P carries (v^, east, north) at v to the same three at F. Then Q e3 = sin L F^ + cos L north(F^), L = height angle of v
  above the page, north(F^) = the direction on the ball at F^ that points to the frame's pole; the frame is tipped by
  `tip_e3_to(E, Q e3, share, mode)`, share 1 (keep) or 1/2 (keep50). In words: the page tips, about the line square
  to the shadow of the square, exactly as much as the squaring pushed the point toward the pole, so the square stands
  as high above the new page as the point stood above the old. `keepfade_tr`: the share is r^2 / (1 + r^2), r = |v|.

B. The page tips toward the plane the orbit makes:
- `orb_inf_px`, `orb_inf_tr`, `orb_2_tr`, `orb_2_px`, `orb_05_tr`: square; then tip_to_line(E, v^ x v'^, mu, mode) with
  mu = infinity, 2, 0.5. v^ x v'^ stands square to the plane through the origin, the point and the new point; its
  length is the sine of the angle of the step. mu = infinity is the literal reading of the user's sentence: **every
  point after the first is squared exactly inside the plane of the last two orbit points** (measured: the height of
  the point above its page is 4e-16 of its length).
- `orbsq_inf_px`: the same with v^ x F^ (the plane of the point and its square, c not counted).
- `osc_inf_tr`, `osc_1_tr`: the same with t_before x t (the plane in which the PATH has just bent; carried: t).
- `mean_1_px`, `mean_01_px`, `mean_01_tr`: the plane the WHOLE orbit has made so far. Carried besides the frame: the
  3 x 3 table N = eps z z^T + sum over the steps so far of w w^T, w = v^ x v'^; after each squaring e3 goes to the
  main axis of N (largest eigenvalue, sign nearest the old e3) by `tip_e3_to(.., 1, mode)`. eps = 1 or 0.1 is the
  weight of the flat page.
- `area_1_px`, `area_4_px`, `area_16_px`, `area_4_tr`: as `orb`, with w = v x v' (NOT unit vectors: the plane of a
  step counts by the area of the triangle origin - point - new point), mu = 1, 4, 16.
- `marea_1_px`, `marea_01_px`: as `mean`, with w = v x v'.
- `sticky_px`, `sticky_tr`: square; if beta is the smallest tip that would bring the page onto the plane of the last
  two points (beta = 1/2 atan2(2pq, p^2 - q^2) with w = v^ x v'^), the page tips by beta - sin(4 beta) / 4: the law the
  bench rule `along` uses for its sheet (stays for small beta, all the way at 45 degrees, a quarter turn at 90).
  `stickyfade_px`: that tip times A / (1 + A), A = |v x v'|^2.

C. The page tips toward the point, BEFORE squaring, by the shortest tip:
- `pt_1_tr`, `pt_1_px`, `pt_50_tr`: with a, b, w the frame coordinates of v, rho = hypot(a, b), L = atan2(w, rho) the
  height angle and ph = (a e1 + b e2) / rho the direction of the shadow, the frame is turned by lam L about ph x e3
  (lam = 1: the page then holds the point; measured 7e-16), then v is squared in the tipped frame.
  `pt_soft_tr`: by sin(2L)/2 in place of L.
- `pole_05`: before squaring tip_to_line(E, v^, 0.5, tr): the out-of-page line moves toward the point (the opposite).

`fr_fixed` (frame never moves) agrees with the bench one-plane rule to 0.0e+00 (measured, 20,000 points).

## 3. What the pictures show

Numbers for every rule are in `numbers.txt` (flat_check and spun_check with 20,000 points). In the lines below
"inside" is the share of the spun_check box that never leaves at 40 steps (basilica: one-plane 3.3%, along 3.0%).

### Kind A: the frame is carried with the orbit. Fails.
- `turnsq`, `transport`, `keep_tr`, `keep_px`, `keep50_tr`, `keepfade_tr`, `pole_05`: the basilica has NOTHING off
  the flat page (seen: every cut off the page is empty, `cuts-basilica-all1.png`, `all3`, `all4`; measured: inside
  0.0%). The flat picture is there, with no thickness. Off the page the Mandelbrot solid shrinks to a small ball
  round c = 0 (a ragged clump for `turnsq`) (seen: `cuts-mandel-rest1.png`, `rest2`).
  Why (reasoned, then measured): the page tips AWAY from where the squaring sends the point, so a point that is a
  little above the page is a little more above the next page: the tip feeds itself. Measured on one orbit that starts
  at (0.05, 0.03, 0.01) beside the basilica's cycle, `keepfade_tr`: the page's tip from flat is 0.03, 0.06, 0.06,
  0.09, 0.09, 0.13, 0.13, 0.19, 0.19, 0.29, 0.29, 0.44, 0.44, 0.66 degrees: times 1.5 every two steps, which is the
  factor the reasoning gives for this rule. `keep_tr`, `turnsq`, `transport`, `pole_05` reach 39 to 87 degrees and
  the orbit is gone within 7 to 10 steps. Against that, `area_1_px` stays at 0.02 degrees and `pt_1_tr` at 6.06.
  (The 1.5 was worked out for `keepfade_tr` only; for the others I measured the runaway and did not derive it.)
- Two rules of kind B end the same way: `osc_inf_tr` and `orbsq_inf_px` have nothing off the page for the basilica
  except in the upright sheet (seen: `cuts-basilica-all2.png` row 4, `all3` row 5). I did not work out why.
- `turn1`, `turn50`, `turn25`, `turnsin`, `turnarea`: the row of bodies of the basilica melts into one or two lumps
  (seen: `julia-a.png` rows 3-5; cuts in `cuts-basilica-all1.png`, `all3`, `all4`), with a dark groove along the
  x-axis for `turn1` and `turn50`. The rabbit is a ragged lump or a blob (seen: `julia-a.png`, `cuts-rabbit-main.png`
  last row). The Mandelbrot solid off the page is a fat smooth lump with no buds (seen: `cuts-mandel-main.png` last
  row, `cuts-mandel-rest1.png`). Reasoned cause of the groove: the shortest turn has no direction where the point is
  thrown straight through the origin, and for c = -1 that is the x-axis between 0 and 1. `turnsin` and `turnarea`,
  which have no such jump, are lumps all the same (seen), so the jump is not the whole reason.

### Kind B, all the way: the page IS the plane the orbit has just made. Ribs and shards. Fails.
- `orb_inf_px`, `orb_inf_tr`: the basilica keeps its row of bodies (seen: all cuts, `cuts-basilica-all1.png`), but
  the side bodies are stacks of rings round the x-axis and the main body is grooved and terraced (seen:
  `julia-b.png` rows 1-2; `extra-a.png` row 2 from an eye almost on the x-axis, from above, and in the close-up).
  These are the lathe's rings, bent. Volume: basilica 4.10% of the box at 30 steps, 4.09% at 80 (measured), so no
  dust there. The rabbit is a ribbed lump in the rough solid (seen, `julia-b.png`) and thin fans of shards in the
  cuts (seen, `cuts-rabbit-main.png` rows 3-4); of its volume at 30 steps only 81% (px) and 73% (tr) is left at 80
  steps (measured). The Mandelbrot solid is a ribbed shell (seen, `mandel-a.png` rows 3-4); every cut along a sheet
  through the x-axis looks like a rough Mandelbrot set with buds, which is what ribs round the x-axis look like in
  such cuts; px has speckled holes in the main body.
- `orb_2_tr`, `orb_2_px`, `orb_05_tr`, `mean_1_px`, `mean_01_px`, `mean_01_tr`, `area_4_*`, `area_16_px`, `sticky_px`,
  `sticky_tr`: in between. Basilica: burred or lopsided bodies, some with torn-off slivers (seen:
  `cuts-basilica-all2.png` rows 1-3, `all3` rows 7-9, `all4` rows 2-4, `cuts-basilica-sticky.png`; solids of
  `orb_2_tr`, `orb_05_tr`, `area_4_px` in `julia-b.png`, `julia-c.png`: creased and ribbed lumps). Rabbit: dust for
  `orb_2_tr` (22% of the 30-step volume left at 80), `mean_1_px` (cuts nearly empty) and `sticky_px` (11% left).
- Reasoned, not tested, why the rabbit shatters: the plane of the last two points hinges about the current point at
  every step, by as much as c sticks out of it. For c on the x-axis the plane settles on the sheet through the x-axis
  (hence rings). For the rabbit's c the plane swings to hold the line of c, but its real axis is still the shadow of
  the x-axis, and in such a tilted plane c sits at another angle from the real axis than in the flat page: the orbit
  is run with a wrong c, mostly one outside the Mandelbrot set. This is limit C1 of the briefing, met again.
- Also measured: rules that read the DIRECTION of a point or of a step jump when the orbit passes close to the
  origin (the direction of a tiny point is noise): on the test orbit the page of `orb_inf_px` jumps from 19.99 to
  70.01 degrees at step 12, with the point at 1e-9 from the origin. Every centre's cycle passes through the origin.

### Kind B, part of the way and counted by area: the one-plane rule with a crease. Clean-ish, but nothing new.
- `area_1_px`, `marea_1_px`, `stickyfade_px`, `osc_1_tr`: smooth cuts, row of bodies kept, no buds off the page;
  the main body of the basilica turns from a ball into a lens with a sharp brim, and at 45 degrees its outline is a
  diamond (seen: `cuts-basilica-all4.png` rows 1 and 5, `cuts-basilica-sticky.png` row 3, `all2` row 5; solid of
  `area_1_px` in `julia-c.png` row 3 and `extra-a.png` row 3: brim, a crease, a few small buds only where the
  one-plane rule has them, and a few loose specks). Volume of `area_1_px`: basilica 3.77% at 30 steps, 3.51% at 80
  (93% kept: a slow leak; the one-plane rule keeps 100%); rabbit 88% kept. Its rabbit is a knobbly lump in the rough
  solid, less clean than the one-plane rabbit, though the cuts still show the three bodies near the page (seen:
  `julia-c.png`, `cuts-rabbit-main.png` rows 6 and 8). Its Mandelbrot solid is the one-plane blob with two extra
  wings (seen: `mandel-a.png` row 5). Solids were made for `area_1_px` only; the other three were judged from cuts.

### Kind C: the page tips to the point by the shortest tip. Fans of fins. Fails.
- `pt_1_tr`, `pt_1_px`: in every sheet through the x-axis from 0 to 45 degrees the cut is, to the eye, the flat
  basilica with all its buds, and the cut across at x = 0 is a round disc (seen: `cuts-basilica-all2.png` rows 6
  and 8): the lathe's signature. The solid is a fan of thin fins and rings (seen: `julia-b.png` rows 4-5,
  `extra-a.png` row 4, all three views). In the upright sheet: a row of round discs (tr) or one oval (px), because
  there the squaring has become a push straight outward (section 1, point 5). Mandelbrot solid: a scallop of ribs
  with loose arcs of debris, and a huge filled region in the upright sheet (seen: `mandel-a.png` row 6).
- `pt_50_tr`: nothing off the page except in the upright sheet (seen). `pt_soft_tr`: as `pt_1_tr`, with holes in
  the upright sheet (seen).

### Against the bench (same tools, same sizes)
- `along` (seen: `julia-a.png`, `julia-c.png`, `extra-a.png` row 1): basilica with round buds all over; rabbit a
  swollen lump. `oneplane`: clean separate bodies for every c, buds only round the flat page.
- No rule of mine has buds off the flat page that are round and not ribs. No rule of mine has a cleaner rabbit than
  `oneplane`. So nothing here beats `along` on the basilica or `oneplane` on the rabbit.

## 4. On Claim S (a solid that is not spun needs something fixed off the x-axis)
Not contradicted. Every rule here has such a thing, the start of the frame, and the Mandelbrot solid of every exact
rule but one is measurably not spun (spun_check, 20,000 pairs: the verdict changes for 0.1% to 5.0% of the pairs,
against 0.00% for the lathe; the one exception is `pole_05`, 0.00%, whose solid off the page has shrunk to a small
ball). But the departure from "spun" never takes the form of round buds off the flat page (seen): where the page
follows closely the solid is the spun set with ribs and bends; where it lags it is the one-plane blob.
Reasoned, not tested: every rule that tips AFTER squaring makes its first squaring about the flat page, like the
one-plane rule; only the "before squaring" rules (kind C, and the scout's sheet family) differ at the first step,
and those have to build the page from the point alone, which, done all the way, is a lathe (rings or fins).

## 5. Numbers
`numbers.txt` has one line per rule. Summary (20,000 test points, flat_check at 60 steps, spun_check at 40):
- Flat page: 0 differing verdicts in all four tests for all 36 rules of section 2 A-C and for `fr_fixed`.
  `turn_full` 2596 / 2930 / 3057 / 3131 (Mandelbrot / basilica / rabbit / Siegel), `turn_full_half`
  1277 / 2432 / 2485 / 2330, `e1_to_point` 3738 / 2960 / 2715 / 3770, `transport_full` 2534 / 1980 / 2843 / 2545.
- Mandelbrot verdicts that change when c is turned round the x-axis (and the share inside): oneplane 1.20% (1.5%),
  along 1.61% (7.4%), lathe 0.00% (7.6%); orb_inf_px 2.10% (5.5%), orb_inf_tr 1.67% (6.2%), area_1_px 1.62% (1.7%),
  pt_1_tr 4.96% (9.4%), turn50 3.62% (5.3%), sticky_tr 1.33% (5.7%); the collapsed rules 0.0 to 0.7% (0.4 to 1.5%).
- `measure.txt` has the measurements quoted in sections 1 and 3 and the volumes at 30 and 80 steps (150,000 points):
  along basilica 3.09 -> 3.09%, rabbit 6.08 -> 5.96%; oneplane 3.46 -> 3.46%, 1.71 -> 1.66%; orb_inf_px 4.10 -> 4.09%,
  2.68 -> 2.18%; orb_inf_tr 4.02 -> 3.97%, 2.80 -> 2.05%; orb_2_tr 4.71 -> 4.69%, 0.75 -> 0.17%; area_1_px 3.77 -> 3.51%,
  2.90 -> 2.54%; area_4_px 3.43 -> 2.90%, 3.12 -> 2.94%; pt_1_tr 3.68 -> 3.66%, 3.39 -> 2.93%; pt_1_px 4.93 -> 4.92%,
  4.82 -> 4.34%; turn50 4.45 -> 4.42%, 1.53 -> 1.39%; sticky_px 3.23 -> 3.23%, 0.14 -> 0.02%; stickyfade_px
  4.09 -> 3.79%, 2.43 -> 1.96%.

## 6. Pictures (all looked at)
- `out/r21/frame/julia-a.png`: rough solids of six Julia sets, 300 x 225 x 180 blocks, 28 steps: along, oneplane,
  turn1, turn50, turnsin. Shows the lumps and the groove of the turn rules.
- `out/r21/frame/julia-b.png`: the same at 240 x 180 x 140: orb_inf_px, orb_inf_tr, orb_2_tr, pt_1_tr, pt_1_px. Shows the
  ribs and rings of full following and the fans of fins of the shortest tip.
- `out/r21/frame/julia-c.png`: the same size: along, oneplane, area_1_px, area_4_px, orb_05_tr. Shows the brim and
  crease of area_1_px and the creased lumps of the in-between rules, beside the two bench rules.
- `out/r21/frame/extra-a.png`: the basilica at 60 steps from an eye almost on the x-axis, from above, and a close-up
  of the main body: along, orb_inf_px, area_1_px, pt_1_tr. Shows that the ribs of orb_inf_px are rings round the
  x-axis and that area_1_px has no buds off the page.
- `out/r21/frame/mandel-a.png`: the Mandelbrot solid, cuts at 0, 11.25, 22.5, 45, 90 degrees, across at x = -0.12, and
  the rough solid (22 steps): along, oneplane, orb_inf_px, orb_inf_tr, area_1_px, pt_1_tr.
- `out/r21/frame/cuts-basilica-all1.png`, `-all2.png`, `-all3.png`, `-all4.png`, `-sticky.png`: for every rule, cuts
  of the basilica along sheets at 0, 11.25, 22.5, 33.75, 45, 90 degrees and across the x-axis at x = 0 and x = -1
  (60 steps). These are the pictures the triage rests on.
- `out/r21/frame/cuts-rabbit-main.png`, `cuts-rabbit-sticky.png`: the same cuts of the rabbit for the main rules.
- `out/r21/frame/cuts-mandel-main.png`, `-rest1.png`, `-rest2.png`, `-rest3.png`: the same cuts of the Mandelbrot solid
  for every exact rule; `cuts-mandel-fails.png` for the rules that break the flat page (their cut at 0 degrees is not
  the Mandelbrot set).
- The scout's `out/r21/me/follow-julia-quick.png` and `follow-mandel-quick.png` (looked at, for comparison).

## 7. What I did not do, and other limits
- Rough solids exist for 11 of the 36 exact rules (those in the three Julia sheets) and Mandelbrot solids for 4; the
  rest were judged from cuts alone (eight cuts per rule for the basilica and for the Mandelbrot solid). The rabbit
  was cut for 11 of my rules. San Marco, airplane, Siegel disc and dendrite were looked at only in the three Julia
  sheets; nothing there contradicts the above (the airplane and the dendrite are specks or empty for every rule,
  including the bench rules, at this size).
- A frame rule costs 4 to 8 times a fixed rule here (a row of six rough solids took 100 to 210 s against 16 to 36 s).
  Two runs went over the 10-minute limit of the house rules: the first Julia sheet (620 s) and the extra views (698 s).
- The close-up and the second eye positions were made for the basilica only.
- Not coded: the frame turned about its own real axis toward the point (the scout's family while e1 is on the
  x-axis); the bench rule `along` applied inside a carried frame (another agent's family); a plane built from c
  (another agent's family); a quaternion in place of nine arrays.
- The explanation of the rabbit's shards (section 3) and the remark about the first squaring (section 4) are
  reasoning that I did not test.
