# Round 21, skeptic: notes

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.
All paths are relative to the project root. Run every script from the root with `PYTHONIOENCODING=utf-8`.

## 0. The short version

1. **Claim S stands.** I built 16 recipes with nothing fixed off the x-axis. None gives a Mandelbrot solid that is
   exact on the flat page and not spun. Nine of them LOOKED like counterexamples in the library's numbers
   (`M.spun_check` up to 0.43 %, thousands of verdicts different from the lathe). All of that is rounding: re-run
   with 50 to 400 decimal digits, every checked verdict goes back to the lathe's (320 of 320, eight recipes).
2. **The scout's verdict on the lag family stands, with four corrections.**
   (a) Lags 0.6 to 0.7 DO have a round bud off the flat page that is not a ring: one on each side of every basilica
   body, on the upright sheet. The rest of the skin is ribs (rings), so this is not a success.
   (b) "Exact on the flat page" is hollow for most of the family: parts of the flat picture have no thickness at all.
   (c) The rabbit of lags 0.45 to 0.65 and of `delay` is not a lump or dust: it leaks away completely.
   (d) `first` is the lathe if the orbit is started at 0 instead of at c.
   No rule in the family has a rabbit with separate bodies except lag 0 (the one-plane rule itself).
3. **The library computes what it says** (`stay`, `sq_about`, `solid`, the cuts: 0 mismatches), but three of its
   tools can mislead: `flat_check` cannot see a flat page that is infinitely thin, `spun_check` reports "not spun"
   for unstable recipes that are spun, and `M.half` reads every sheet within 5e-9 radians of the flat page (or of
   the upright sheet) as that page itself.

## 1. Definitions (enough to re-code everything)

- Point v = (x, y, z), r = |v|. Flat page: z = 0. x-axis: the real line.
- **One-plane rule** P(x, y, z) = f (x^2 - y^2, 2xy, 2rz), f = r^2 / (r^2 + z^2), P(0) = 0.
- **Sheet at turn t**: the plane through the x-axis and the direction (0, cos t, sin t). It is carried as the vector
  u = (cos 2t, sin 2t). t and t + 180 degrees are the same sheet.
- **P about the sheet t**: turn the point back, square, turn forward:
  (x, y', z') = (x, y cos t + z sin t, z cos t - y sin t); (X, Y, Z) = P(x, y', z'); result (X, Y cos t - Z sin t, Y sin t + Z cos t).
- **Own sheet** of a point: u = (y^2 - z^2, 2yz) / (y^2 + z^2). A point on the x-axis has none; the carried sheet is kept.
- **blend(u, p, lam)** = (1 - lam) u + lam p, scaled to length 1; if its length is under 1e-9, u is kept.
- **Orbit**: v <- F(v, carried things) + c, for as long as |v|^2 < 36. "Inside" = never left in the given number of steps.
  Julia set of c: the start is the test point. Mandelbrot solid: the start is c itself (the library's convention), carried things fresh.
- **lag lam** (library `M.lag(lam)`; `lag05` ... `lag95` in `out/r21/skeptic/myrules.py`): carried: one sheet u, at the
  start the flat page (1, 0). Each step: u <- blend(u, own sheet of the point, lam); then the point is squared by P about u.
  lam = 0 is the one-plane rule (`fixed`), lam = 1 the lathe (`own`).
- **delay**: the point is squared by P about u; then u <- own sheet of that (un-squared) point. Start: the flat page.
- **first**: squaring number 0 about the flat page; every later one about the point's own sheet.

My attempts against Claim S (`ATTEMPTS` in `myrules.py`). In all of them "no sheet yet" is carried as u = (0, 0),
nothing names the flat page, and the "handed turn" is counter-clockwise for an eye on the +x side looking at the origin
(the right hand rule about +x; in doubled-angle terms, turning u by the angle a multiplies it by the rotation through 2a).

| name | recipe |
|---|---|
| S1 lag25 / lag75, no start page | lag rule; the first point's own sheet is the first sheet (blend of "none" with p is p) |
| S2 delay, no start page | point squared about the sheet of the point before; the very first about its own |
| S3 hand 20 / 45 | every point squared about its own sheet turned on by a fixed 20 (45) degrees, handed |
| S4 ahead g (g = 1, 3, -0.5) | carried: the last point's sheet q. d = handed angle from q to the own sheet p (in (-90, 90]). Square about p turned on by g d. First point: d = 0 |
| S5 c sheet | square about the sheet that c makes (the user's earlier question); c on the axis: the point's own sheet |
| S5 c sheet + 30 | about c's sheet turned on by 30 degrees, handed |
| S5 c mid | about blend(c's sheet, own sheet, 0.5) |
| S5 c lag25 | lag 0.25 with c's sheet as the starting sheet |
| S5 c ahead 1 | about the own sheet turned on by its handed angle from c's sheet |
| S6 span2 | carried: the point before, w. Square about the PLANE through 0, w and v (any plane, not only sheets): normal n = w x v, real axis e1 = the x-axis laid down onto the plane, e2 = n x e1; (a, b, c) = (v.e1, v.e2, v.n); P(a, b, c); back. No plane yet, or w and v in line, or the plane square to the x-axis: the point's own sheet |
| S7 mean sheet | carried: the sum of the own-sheet vectors of all points so far (this one included); square about its direction |
| S8 far sheet | carried: the sheet of the orbit point that was farthest from the x-axis so far (this one included) |

## 2. Job 1: Claim S

Script `out/r21/skeptic/claimS.py` (numbers), `exact.py` (the same recipes with 30, 50, 100 digits), `fake.py` (picture).

**Noise level of `M.spun_check`** (measured): for `own` and for `bench('lathe')` 0 of 40,000 pairs differ at 40, 80 and
160 steps, and 0 of 200,000 at 40 and 80 steps, for the Mandelbrot solid and for the basilica. For scale, rules that are
truly not spun: `fixed` 1.2 %, `lag25` 2.6 %, `along` 1.5 %, `lag75` 0.65 % at 40 steps falling to 0.34 % at 160.

**Results** (measured; flat page = `M.flat_check`, 20,000 points per set; "lathe" = verdicts that differ from the
lathe's solid on the same 100,000 random c, at 40 / 80 steps; lathe inside: 7,767):

| attempt | flat page differs (M, basilica, rabbit, Siegel) | turned, Mandelbrot, 40 / 80 steps | differs from the lathe 40 / 80 | basilica turned |
|---|---|---|---|---|
| S1 lag25 no start | 0 0 0 0 | 0.0000 % / 0.0800 % | 6 / 135 | 0 |
| S1 lag75 no start | 0 0 0 0 | 0.0000 % / 0.0075 % | 0 / 49 | 0 |
| S2 delay no start | 0 0 0 0 | 0.1975 % / 0.0600 % | 970 / 1,955 | 0 |
| S3 hand 20 | 860 279 2630 1239 | 0.0000 % / 0.0000 % | 2,631 / 2,595 | 0 |
| S3 hand 45 | 1080 329 2715 3770 | 0.0000 % / 0.0000 % | 3,371 / 3,047 | 0 |
| S4 ahead 1 | 0 0 0 0 | 0.3000 % / 0.0925 % | 2,310 / 5,255 | 0 |
| S4 ahead 3 | 0 0 0 0 | 0.4250 % / 0.1775 % | 5,471 / 6,139 | 0 |
| S4 behind 0.5 | 0 0 0 0 | 0.0075 % / 0.0700 % | 26 / 252 | 0 |
| S5 c sheet | 0 0 0 0 | 0 / 0 | 0 / 0 | 0 |
| S5 c sheet + 30 | 2695 281 2715 3770 | 0 / 0 | 6,436 / 6,106 | 0 |
| S5 c mid | 0 0 0 0 | 0 / 0 | 0 / 0 | 0 |
| S5 c lag25 | 0 0 0 0 | 0.0000 % / 0.0800 % | 6 / 135 | 0 |
| S5 c ahead 1 | 0 0 0 0 | 0.0075 % / 0.1975 % | 7 / 2,836 | 0 |
| S6 span2 | 0 0 0 0 | 0.3500 % / 0.2450 % | 504 / 1,073 | 0 |
| S7 mean sheet | 0 0 0 0 | 0 / 0 | 0 / 14 | 0 |
| S8 far sheet | 0 0 0 0 | 0 / 0 | 0 / 0 | 0 |

Two kinds of outcome.

**(i) Not exact on the flat page, and spun to the last point** (S3, S5 c sheet + 30). The right hand rule turns with c:
"counter-clockwise" is the same from every side of the x-axis. Handedness can make the solid different from its
mirror image; it cannot make it different from itself turned. The step that forces the symmetry: every step
(reasoned); the number: 0 of 40,000 pairs at 40 and at 80 steps (measured).

**(ii) Exact on the flat page, and in exact arithmetic the lathe's solid.** The step that forces it is the very first
squaring (reasoned). The recipe cannot tell c's sheet from the flat page. On the flat page it must give the flat
orbit, which stays in the page; so for c in any sheet it gives the same orbit turned into that sheet. After that every
point, c and the x-axis lie in one sheet, so: S1, S5 c lag: every blend is between two copies of the same sheet;
S2: "the sheet of the point before" is the same sheet; S4, S5 c ahead: the handed turn between successive sheets is 0;
S5 c mid: half-way between a sheet and itself; S6: the plane through 0 and two points of the sheet is the sheet;
S7, S8: a mean, or a pick, of copies of one sheet.

**The nine that looked like counterexamples are rounding** (measured, `exact.py` and `exact.py more`). The library's
16 digits put the orbit about 1e-16 off c's sheet; these recipes magnify that push at every step, and after 40 to 80
steps the orbit is somewhere else. The same recipes in my own scalar code with more digits (Python `decimal`), on the
first 40 points whose verdict differs from the lathe's at 80 steps:

| | 16 digits (library) | 30 digits | 50 digits | 100 digits | more |
|---|---|---|---|---|---|
| S1 lag25 no start (= S5 c lag25) | 135 of 100,000 differ | 39 of 40 agree with the lathe | 40 of 40 | 40 of 40 | |
| S1 lag75 no start | 49 differ | 35 of 40 | 40 of 40 | 40 of 40 | |
| S2 delay no start | 1,955 differ | 19 of 40 | 40 of 40 | 40 of 40 | |
| S4 ahead 1 | 5,255 differ | 14 of 40 | 37 of 40 | 40 of 40 | |
| S4 ahead 3 | 6,139 differ | 3 of 40 | 14 of 40 | 40 of 40 | |
| S4 behind 0.5 | 252 differ | 4 of 40 | 30 of 40 | 39 of 40 | 200 digits: 40 of 40 |
| S5 c ahead 1 | 2,836 differ | 31 of 40 | 40 of 40 | 40 of 40 | |
| S6 span2 | 1,073 differ | 9 of 40 | 15 of 40 | 25 of 40 | 200: 37; 400: 40; 800: 40 of 40 |

(S7 mean sheet: 0 of 100,000 differ at 40 steps, 14 at 80; not re-run.)

One orbit of S4 ahead 1, c = (0.087129, 0.275202, 0.545483), distance of the orbit from the sheet of c:
16 digits: 1.6e-16 at step 1, 2.6e-8 at step 20, 1.7 at step 40, gone at step 40.
30 digits: 1.6e-30, 2.0e-22, 5.6e-14, gone at step 75. 50 digits: 5.6e-49 at step 5, 1.8e-42, 5.0e-34, 2.4e-16 at step 80, stays.
The same growth, started lower: the departure is made by the arithmetic, not by the recipe.
The recipes that magnify fastest need the most digits (S6 span2: 400).

**What the fake looks like** (seen, `out/r21/skeptic/fake-notspun.png`, 150 steps). For S4 ahead 1 the cuts along the
sheets at 0, 45 and 90 degrees are the full flat Mandelbrot set (0, 0 and 53 of 20,718 lathe pixels gone), the cuts at
11.25 and 22.5 degrees are an arrow shape with the buds eaten (11,743 and 11,774 gone), and the cut across the x-axis
is a small disc with four hair lines on the diagonals. S2 gives a heart (5,441 gone), S6 a cardioid with a bite of
dust in its right half (3,035 gone), S1 loses the buds of the period-2 disc (646 gone), S8 is the lathe (0 gone).
It reads as "a solid that is not spun, with the flat picture on a few special sheets". It is the grid of the computer's
numbers: on the sheets at 0, 45 and 90 degrees the rounded numbers happen to keep the orbit exactly in its sheet
(reasoned), so nothing gets magnified there (measured: 0, 0 and 53 pixels gone).

**Extension to Julia sets** (measured): with nothing fixed and c on the x-axis, the Julia set is spun too: "basilica
turned" is 0 of 40,000 for all 16 attempts at 40 and 80 steps. So a recipe with nothing fixed gives a ringed basilica.

**Other ways to smuggle a fixed thing in** (reasoned, so that nobody takes one for a counterexample): `np.arctan2(z, y)`
with a formula that is not "the same angle plus a constant" (this is how `along` names the flat page); the default
`init` of `M.Rule`, which IS the flat page; any half-angle of a sheet (`M.half` picks the side y > 0) used with a rule
that does not treat both sides of a sheet alike; a solver with a fixed starting guess.

## 3. Job 2: the lag family again

Scripts: `lagcuts.py` (cut sheets and volumes), `across.py` (large cuts across the x-axis with close-ups), `sheets.py`
(rough solids with the library's sheet functions), `lagnumbers.py`, `thin.py`, `thinpics.py`, `lift.py`, `fin.py`.
Lags run: 0.05, 0.1, 0.25, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 0.95, plus `delay`, `first`, and
`oneplane`, `along`, `lathe` drawn by the same tools. Cuts at 100 to 150 steps, solids at 40 to 60, volumes to 500.

**The two library numbers** (measured, `lagnumbers.py`): every lag, `delay` and `first` pass `M.flat_check` (0 of 20,000
on each of the four sets, strays 0). `spun_check`, Mandelbrot, at 40 / 160 steps: lag05 1.90 / 1.84 %, lag10 2.24 / 2.10,
lag25 2.61 / 2.40, lag40 2.14 / 1.81, lag50 1.34 / 0.83, lag60 0.88 / 0.44, lag70 0.70 / 0.42, lag75 0.65 / 0.34,
lag90 0.30 / 0.11, lag95 0.14 / 0.11, delay 0.47 / 0.22, first 1.38 / 1.10. So none is spun.
Of 100,000 random c (80 steps; lathe inside 7,398): lag05 has 2,170 inside, only 18 of them outside the lathe's solid;
lag25 3,834 (91 outside); lag70 6,549 (119 outside, 968 lathe points missing); lag90 7,391 (147 outside, 154 missing).
Across all the lags at most 8 % of a solid lies outside the lathe's (lag50: 523 of 6,279). In plain words (measured):
every solid of the family is, nearly, the lathe's solid with pieces taken away.

**Volumes at 30 / 80 / 200 / 500 steps** (measured, 300,000 random points, `lagcuts.py vol`):

| rule | basilica | rabbit | Siegel | Mandelbrot |
|---|---|---|---|---|
| oneplane | 0.716 / 0.716 / 0.716 / 0.716 | 0.448 / 0.436 / 0.436 / 0.436 | 1.223 / 1.187 / 1.187 / 1.187 | 0.311 / 0.278 / 0.273 / 0.272 |
| along | 0.644 / 0.643 / 0.643 / 0.643 | 1.627 / 1.598 / 1.598 / 1.598 | 1.652 / 1.608 / 1.600 / 1.595 | 1.489 / 1.365 / 1.318 / 1.295 |
| lag05 | 0.712 / 0.711 / 0.711 / 0.711 | 0.724 / 0.623 / 0.622 / 0.622 | 1.682 / 1.647 / 1.647 / 1.647 | 0.429 / 0.415 / 0.413 / 0.410 |
| lag10 | 0.706 / 0.705 / 0.705 / 0.705 | 0.823 / 0.735 / 0.735 / 0.735 | 1.839 / 1.798 / 1.797 / 1.797 | 0.515 / 0.500 / 0.494 / 0.490 |
| lag25 | 0.684 / 0.683 / 0.683 / 0.683 | 1.413 / 1.360 / 1.359 / 1.359 | 2.065 / 2.055 / 2.055 / 2.055 | 0.761 / 0.730 / 0.716 / 0.710 |
| lag40 | 0.657 (all) | 1.764 / 1.651 / 1.650 / 1.650 | 2.027 / 2.025 / 2.025 / 2.025 | 1.067 / 1.000 / 0.976 / 0.964 |
| lag45 | 0.654 (all) | **1.861 / 1.073 / 0.368 / 0.159** | 1.919 / 1.918 / 1.918 / 1.918 | 1.197 / 1.105 / 1.052 / 1.025 |
| lag50 | 0.654 (all) | **1.411 / 1.094 / 0.847 / 0.436** | 1.746 / 1.745 / 1.745 / 1.745 | 1.304 / 1.200 / 1.143 / 1.112 |
| lag55 | 0.662 (all) | **0.359 / 0.001 / 0.000 / 0.000** | 1.355 / 1.351 / 1.351 / 1.351 | 1.250 / 1.147 / 1.114 / 1.097 |
| lag60 | 0.675 / 0.674 / 0.674 / 0.674 | **0.565 / 0.018 / 0.000 / 0.000** | 1.288 / 1.281 / 1.281 / 1.281 | 1.264 / 1.142 / 1.101 / 1.087 |
| lag65 | 0.687 / 0.686 / 0.686 / 0.686 | **1.246 / 0.800 / 0.310 / 0.030** | 1.262 / 1.252 / 1.252 / 1.252 | 1.329 / 1.202 / 1.163 / 1.146 |
| lag70 | 0.696 (all) | 1.361 / 1.334 / 1.334 / 1.334 | 1.337 / 1.315 / 1.312 / 1.310 | 1.382 / 1.254 / 1.216 / 1.200 |
| lag75 | 0.704 / 0.703 / 0.703 / 0.703 | 1.392 / 1.366 / 1.366 / 1.366 | 1.449 / 1.426 / 1.424 / 1.424 | 1.445 / 1.297 / 1.253 / 1.237 |
| lag80 | 0.719 / 0.718 / 0.718 / 0.718 | 1.417 / 1.392 / 1.392 / 1.392 | 1.533 / 1.520 / 1.520 / 1.520 | 1.498 / 1.344 / 1.298 / 1.284 |
| lag90 | 0.750 (all) | 1.459 / 1.430 / 1.429 / 1.429 | 1.655 / 1.618 / 1.616 / 1.616 | 1.530 / 1.395 / 1.352 / 1.335 |
| lag95 | 0.760 / 0.759 / 0.759 / 0.759 | 1.475 / 1.443 / 1.443 / 1.443 | 1.690 / 1.629 / 1.615 / 1.611 | 1.530 / 1.398 / 1.355 / 1.337 |
| delay | 0.667 (all) | **0.000 (all)** | **0.003 / 0.000 / 0.000 / 0.000** | 0.766 / 0.669 / 0.626 / 0.603 |
| first | 0.725 (all) | 1.501 / 1.477 / 1.477 / 1.477 | 1.595 / 1.531 / 1.515 / 1.510 | 1.115 / 1.059 / 1.040 / 1.034 |
| lathe | 0.767 / 0.766 / 0.766 / 0.766 | 1.484 / 1.452 / 1.452 / 1.452 | 1.722 / 1.656 / 1.641 / 1.637 | 1.533 / 1.399 / 1.357 / 1.341 |

Correction (c) to the scout: the rabbit of lags 0.45 to 0.65 has no volume left (lag55 and lag60: nothing after 80 to
200 steps; lag45, lag50, lag65 still falling at 500 steps). What the 18-step scout picture shows as a "layered lump"
for lag50 is points that have not left yet. `delay`'s rabbit and Siegel disc are not dust either: they are empty.

### Basilica

Seen in `lag-basilica-cuts.part0..3.png` (cuts along sheets at 0, 11.25, 22.5, 33.75, 45, 90 degrees and across the
x-axis at x = 0, -1, -0.35; 100 steps), `across-bas-x0-a/b/c.png` (cuts across x = 0 at 440 px with close-ups, 150
steps), `julia-A.part0/1.png` (solids, eye (0.45, 0.5, 1)), `julia-B.png` (eye (1, 0.3, 0.25), looking along the
x-axis), `close-upbud.png` (close-up, eye (0.4, 1, 0.3)):

- lag 0.05 to 0.4: like the one-plane rule. Buds only round the flat page; the cut across x = 0 is a disc with two buds
  on the y-axis and nothing else; the cuts at 11.25 degrees and more are smooth. From 0.25 on the two buds stretch
  into arcs round the x-axis, and at 0.4 short bars appear on the skin: the beginning of the ribs.
- lag 0.5: the bud is seen in the cut at 11.25 degrees too (it has stretched into an arc); at x = -0.35 two long arcs.
- lag 0.55 to 0.7: **a second set of buds, on the upright sheet.** In the cut across x = 0 the main body has four buds
  round it: two on the flat page, stretched into lens-shaped arcs with slanted slivers beside them, and two on the
  upright sheet. The upright one is a needle at 0.55, a slim spindle at 0.6, egg-shaped at 0.65, and at 0.7 about as
  wide as it is tall (about 0.19 by 0.2) with smaller buds on its sides and tip. In the close-up solid it is a
  separate round, onion-shaped body, itself ribbed, with a smaller bud on its tip. This is a round bud off the flat
  page that is not a ring: correction (a) to the scout. But in the same pictures the skin of every body is covered
  with ribs that run round the x-axis (seen from along the axis: concentric rings), the two flat-page buds are arcs,
  and nothing sits at 45 degrees. `along` in the same close-up: round buds of many sizes in all directions, no ribs.
  Why the upright sheet (reasoned, and the cut at 90 degrees shows the complete flat basilica for every lag above
  0.5, seen): for a point on the upright sheet the blend of the flat page with the upright sheet is (1 - 2 lam, 0);
  above lam = 0.5 that IS the upright sheet, so the upright sheet is carried exactly, like the lathe. Near it the
  carried sheet over-shoots the point's own sheet by the factor lam / (2 lam - 1): large near 0.5 (thin bud), 1.75 at
  0.7 (round), 1 at lam = 1 (ring).
- lag 0.75 and 0.8: the upright bud widens into an arc, slivers appear beside the flat-page arcs, and at 0.8 the four
  arcs nearly close. lag 0.9, 0.95: rings with small cracks; the lathe.
- `delay`: like the one-plane rule (two flat-page buds), plus hair lines along the y-axis in the cut at x = -0.35.
- `first`: two flat-page buds and four slanted wing-shaped pieces at roughly 60 degrees; not round.
- Volumes of all of these are steady from 30 to 500 steps (table), so the basilica pictures are not leaks.

### Rabbit

Seen in `lag-rabbit-cuts.part0..3.png` (the flat cut lifted to z = 0, 0.05, 0.15, 0.3; cuts along the sheets at 45 and
90 degrees; cuts across x = 0 and x = -0.3; 100 steps) and in the solids of `julia-A`, `julia-B`:

- one-plane rule: separate round bodies (at z = 0.05 and 0.15 the bodies are separate blobs). Buds only round the flat page.
- lag 0.05 and 0.1: at z = 0.05 the bodies are still joined, at 0.15 one ragged piece; across x = -0.3 a stack of thin
  parallel ribs. lag 0.25, 0.4: one ragged lump with arcs round it. No separate bodies.
- lag 0.5: speckled dust everywhere off the flat page, with a straight seam (the tear). lag 0.6: nothing off the flat
  page but two hair lines (the flat page and the upright sheet). Matches the volumes.
- lag 0.75, 0.9, 0.95, `first`, lathe: the rabbit outline carried up as a column, rings and arcs across; one lump.
- `delay`: nothing off the flat page.
- `along`: one ragged lump (as known).

No rule of the family has a rabbit with separate bodies, other than lag 0. The scout's verdict stands here.

### Mandelbrot solid

Seen in `lag-mandel-cuts.part0..3.png` (cuts at 0, 11.25, 22.5, 33.75, 45, 90 degrees; across x = -0.12, -1, -0.6; 120
steps), `across-man-x012.png` (across the period-3 bud, 150 steps, close-ups), `close-mandel-above.png` (solids, eye
(0.35, 1, 0.3)):

- lag 0.05 to 0.25: off the flat page a smooth heart with a tail, no buds; the period-2 disc shrinks to a rod (across
  x = -1: a small peanut about 0.15 wide where the flat disc is 0.5 wide). From above: a smooth egg with a stick.
- lag 0.4: buds of the heart show at 11.25 degrees (arcs), ragged edges, loose fragments across x = -0.6.
- lag 0.5: a straight vertical edge near x = -0.6 in the cuts at 11 to 45 degrees (the tear), dusty edges.
- lag 0.6: the cut at 90 degrees is the complete flat set (second exact sheet, as for the basilica); the cuts between
  keep a straight cliff near x = -0.6; across x = -0.12 a disc with broken arcs; across x = -0.6 a small disc with
  hair lines along the flat page and the upright sheet.
- lag 0.55 to 0.75 across the period-3 bud: a disc with broken rings, speckled bands of dust and, at 0.6, a frayed
  crown of fragments on the upright side. No clean round bud.
- lag 0.75: the lathe's solid with a bite out of the left of the heart (across x = -0.6: a small disc, four wedge
  spokes along the two exact sheets, and debris). lag 0.9, 0.95: the lathe by eye. From above: rings.
- `delay`: a smooth arrow with fuzzy edges, no buds. `first`: the flat set deformed into pointed shapes; the top bud
  is an arc from about -30 to +30 degrees; across x = -1 a rounded box with loose arcs above and below.

No round buds off the flat page that are not rings, in any lag. The scout's verdict stands for the Mandelbrot solid.

### Correction (b): the flat page of the lag family is partly an infinitely thin slice

`M.flat_check` tests z = 0 exactly, and in floating point z = 0 stays 0 for ever. I lifted every flat test point by a
small height and compared the verdicts with the flat ones (`thin.py`, 20,000 points per set).
Verdicts that change at a lift of 1e-6 / 1e-3, at 80 steps (300 steps in brackets):

| rule | Mandelbrot (about 4,300 flat points inside) | rabbit (2,819 inside) | Siegel (about 3,750 inside) | basilica (3,037) |
|---|---|---|---|---|
| oneplane | 6 / 115 (28 / 147) | 0 / 45 | 1 / 71 | 0 / 13 |
| along | 2 / 103 (12 / 63) | 0 / 41 | 0 / 52 | 0 / 19 |
| lathe | 0 / 3 (2 / 12) | 0 / 1 | 0 / 3 | 0 / 1 |
| lag05 | 142 / 327 (331 / 353) | 0 / 39 | 20 / 113 | 0 / 11 |
| lag10 | 197 / 381 (356 / 376) | 2 / 57 | 10 / 115 | 0 / 9 |
| lag25 | 299 / 512 (489 / 507) | 1 / 54 | 76 / 203 | 0 / 2 |
| lag40 | 359 / 679 (621 / 703) | 1 / 71 | 82 / 226 | 0 / 1 |
| lag50 | 319 / 442 (354 / 460) | 861 / 1,594 (1,731 / 2,051) | 110 / 259 | 0 / 1 |
| lag60 | 189 / 344 (264 / 386) | 2,752 / 2,793 | 40 / 175 | 0 / 1 |
| lag75 | 79 / 151 (124 / 184) | 0 / 7 | 0 / 27 | 0 / 1 |
| lag90 | 5 / 19 (19 / 39) | 0 / 4 | 0 / 22 | 0 / 1 |
| lag95 | 3 / 6 (5 / 20) | 0 / 1 | 0 / 4 | 0 / 1 |
| delay | 1,338 / 1,507 (1,575 / 1,604) | 2,819 / 2,819 | 3,761 / 3,761 | 1 / 28 |
| first | 0 / 16 (1 / 15) | 0 / 1 | 0 / 4 | 0 / 2 |

Seen in `thin-mandel.png` (cuts parallel to the flat page at z = 0, 1e-9, 1e-6, 1e-3, 0.02, 0.1; 150 steps): for
lag05 to lag40 the period-2 disc, one millionth above the page, is already a flat bar with its top and bottom and all
its buds gone; for `delay` the whole set is an arrow shape; one-plane rule, `along`, `first`, lag90: unchanged by eye.
Seen in `thin-julia.png`: one millionth above the page the rabbit of lag50 is speckle, of lag60 and `delay` empty.
Measured, `lift.py` (one c lifted by 1e-6, height of its orbit): c = -0.9 + 0.2i (inside the period-2 disc), lag25:
2e-6, 2e-5 (step 20), 2e-4 (40), 3e-3 (60), 6e-2 (80), then it leaves; one-plane rule, `along`, lathe, lag60 to
lag90, `first`: stays at 1e-6 to 1e-5. Measured, `halfzone.py`: the same c under lag25 leaves after 145, 127, 110, 94,
61 steps for lifts 1e-9, 1e-8, 1e-7, 1e-6, 1e-4: about 17 steps more for every factor of ten, so any lift leaves.
In plain words: for lags up to about 0.6 the upper and lower parts of the period-2 disc (and for `delay` about a third
of the whole flat set, the whole rabbit and the whole Siegel disc) are in the solid only as a film with no thickness.
The cut at z = 0 shows them; no solid picture, print or renderer can. Test 1 is met in the letter only.
(The same holds for the one-plane rule's small flat buds in a weaker form: they are thin, not zero: 3 % of the flat
pixels are missing at 0.001 above the page, `fin.py`.)

## 4. Job 3: the library

Script `checklib.py` unless another is named. Nothing in `out/r21/lib` was edited.

1. **`M.stay` is right** (measured). 1,000 random points, 60 steps, for `fixed`, `lag25`, `lag75`, `delay`, `first`, `own`
   and the fixed rule `along`, Julia sets (six different c, two of them off the flat page) and Mandelbrot: against my
   own scalar code (plain `math`, the sheet carried as an angle, rotations written by hand, no library) and against
   `rule.step` called one orbit at a time: 0 of 1,000 counts differ in all 21 comparisons.
2. **`M.sq_about` is the one-plane rule about the sheet** (measured): against Rot_x(t) P(Rot_x(-t) v) with t over the whole
   circle, 20,000 points: largest difference 1.6e-13 (values up to 22). Length is squared to 7e-15.
3. **`M.half`**: returns t in (-90, 90] degrees, consistently (measured: error of cos and sin under 7e-12 on 200,000
   angles). On the upright sheet itself the sign of sin flips with the sign of u2 (half(-1, +0) = (0, 1),
   half(-1, -1e-17) = (0, -1)). **The result does not depend on the side** for P: with every sheet read from its other
   side, 0 of 2,000 counts change for each of the seven scout rules; and for `along`, `away`, `twoplane`, `mandelbulb`,
   `wind2` used as F in `sq_about`, the result equals the by-hand turn on both sides to 4e-13. (It would matter for an F
   that treats the two sides of a sheet differently; none in the bench does.)
   **Error found, small:** a dead zone. `halfzone.py` (measured): a sheet turned 7e-9 rad from the flat page is read as
   7.45e-9; one turned 5e-9, 3e-9, 1e-9 or 1e-12 is read as exactly 0; the same just short of the upright sheet. Cause:
   sqrt((1 - u1) / 2) with 1 - u1 = 2 t^2 below the rounding of 1. Effect: a point lifted by less than about 1e-8 of
   its distance from the x-axis is treated by every lag rule exactly as by the one-plane rule (lag25 at
   c = (-0.9, 0.2, lift): stays 400 steps for lifts 0, 1e-13, 1e-11; leaves for 1e-9 and more). It hides instability
   from very fine tests, and it is one reason why the flat and upright sheets come out "exact" in the fake pictures.
   It does not change any picture at pixel scale. A fix would be t = atan2(u2, u1) / 2.
4. **The Mandelbrot convention** (measured, 40,000 random c, 60 steps): starting at 0 (one step more) gives the same
   verdicts as starting at c for `fixed`, `lag25`, `lag50`, `lag75`, `delay`, `own` (0 differ). For **`first` 865 verdicts
   differ** (inside: 2,255 from c, 3,046 from 0), and started at 0 it is the lathe exactly (0 differ from the lathe):
   the squaring "about the flat page" is then spent on the point 0. So `first` as drawn exists only by this convention.
5. **`M.solid` shows what the cuts show, as far as blocks can** (measured, `lag25`, `lag75`, `along`; eye on the z-axis):
   the depth map equals a plain block-by-block count on the same sample points (0 of 67,721 pixels differ); the cut
   along the flat page lies inside the silhouette (0 of 11,239 pixels uncovered) when a layer of blocks lies on z = 0;
   the height over the x-axis equals the cut at 90 degrees (0 columns differ). The picture is not mirrored (reasoned
   from `frame`: screen right, up and toward the eye form a right-handed set).
   **But a solid cannot show a film** (`fin.py`, measured, 60 steps): with 160 blocks in depth (no layer on z = 0)
   the silhouette misses 1,217 of the 10,716 flat-cut pixels for lag25, 1,557 for lag40, 3,366 for `delay`, 1,271 for
   the one-plane rule, 143 for `along`, 75 for the lathe. With layers only 0.001 from the page: lag25 1,156, lag40
   1,440, `delay` 3,645, one-plane 294, `along` 172, lathe 50. So for the lag rules and `delay` 11 to 34 % of the flat
   picture is in no solid picture at any depth resolution.
6. **`M.flat_check` passes rules whose flat page is a film** (section 3, correction (b)). It should be read as "exact on
   z = 0", not as "the solid contains the flat picture". A lifted test (z = 1e-6 and 1e-3) is in `thin.py`.
7. **`M.spun_check` can say "not spun" for a recipe that is spun** (section 2): up to 0.43 % for my no-start-page
   recipes, from rounding. Its zero is clean (0 of 200,000 for the lathe). A value under about 0.5 % for a rule that
   claims to have nothing fixed must be re-checked with more digits (`exact.py`) before it is believed.

## 5. What failed, and limits of what I did

- I failed to build a counterexample to Claim S. I believe none exists: the reasoning in section 2 (ii) covers every
  recipe that is a function of the x-axis, c and the orbit's points only.
- Solids are rough blocks at 40 to 60 steps and at most 420 pixels wide: the machine was shared and slow. Two runs went
  over the 10-minute limit (12.5 and 8.3 minutes). I did not draw default-eye Mandelbrot solids at higher resolution
  for every lag; for the Mandelbrot solid I rely on the cuts (120 to 150 steps) and one eye from above.
- The "round bud on the upright sheet" of lag 0.65 and 0.7 is judged from one large cut across x = 0, the cut at 90
  degrees, and one close-up solid from one eye. I did not measure its roundness with numbers.
- The more-digits re-runs cover 40 points per recipe, not all differing points, and S7's 14 points were not re-run.
- I did not explain the straight cliff near x = -0.6 in lag60's Mandelbrot cuts; for lag 0.5 it is the tear, for 0.6
  the blend is continuous, so it may be a very steep slope and not a tear.
- A script of mine was first named `numbers.py`, which hides a standard Python module and broke numpy; it is now
  `lagnumbers.py`. Do not name a file `numbers.py` in a folder that is put on the path.

## 6. Pictures (all opened and looked at)

| file | what it shows |
|---|---|
| `out/r21/me/follow-julia-quick.png`, `follow-mandel-quick.png` | the scout's low-resolution sheets, the starting point |
| `out/r21/skeptic/fake-notspun.png` | Mandelbrot solids of six nothing-fixed recipes as the library computes them: the rounding fake |
| `out/r21/skeptic/thin-mandel.png` | Mandelbrot: the flat page and pages lifted by 1e-9 to 0.1, eleven rules |
| `out/r21/skeptic/thin-julia.png` | rabbit and Siegel disc, the same lifts, six rules |
| `out/r21/skeptic/lag-basilica-cuts.png` (looked at as `.part0` to `.part3`) | basilica cuts, 14 rules, 9 cuts each |
| `out/r21/skeptic/lag-rabbit-cuts.png` (as `.part0` to `.part3`) | rabbit: lifted flat cuts, sheets at 45 and 90, two cuts across |
| `out/r21/skeptic/lag-mandel-cuts.png` (as `.part0` to `.part3`) | Mandelbrot cuts at six angles and three cuts across |
| `out/r21/skeptic/across-bas-x0-a.png`, `-b.png` | basilica across x = 0, `along`, lag 0.25, 0.4, 0.6, 0.75, 0.9, `first`, `delay` |
| `out/r21/skeptic/across-bas-x0-c.png` | the same for lag 0.55, 0.6, 0.65, 0.7, 0.8 with close-ups on the buds: the upright bud |
| `out/r21/skeptic/across-man-x012.png` | Mandelbrot across the period-3 bud, lag 0.55 to 0.75: broken rings and dust |
| `out/r21/skeptic/julia-A.png` (as `.part0`, `.part1`) | six Julia sets, `along`, one-plane, lag 0.6 to 0.75, eye (0.45, 0.5, 1) |
| `out/r21/skeptic/julia-B.png` | basilica and rabbit seen along the x-axis, seven rules: rings show as circles |
| `out/r21/skeptic/close-upbud.png` | close-up solid of the upright bud, `along` against lag 0.65 and 0.7 |
| `out/r21/skeptic/close-mandel-above.png` | Mandelbrot solids from above the edge of the flat page, six rules |
