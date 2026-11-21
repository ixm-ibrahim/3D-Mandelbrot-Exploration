# Round 21, agent "judge": the proposed rules with memory, compared with the same tools

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.
All paths are relative to the project root. All pictures are rough blocks or cuts made with `out/r21/lib/mem.py`;
nothing here is a fine render.

## 0. Verdict in plain words

**Nothing beats "along", and nothing passes the user's five tests.** Ten rules were put side by side: the two bench
rules (`along`, `oneplane`) and the best one or two of each of the four searchers.

- The two **literal readings** of the user's sentence ("square each point in the plane the orbit has just made") fail
  on rings. With the plane of the point and c the basilica is the lathe's ring set to the last grid point
  (measured); with the plane of the last two orbit points the side bodies are stacks of rings, the main body is
  terraced, the rabbit is a ribbed shell that loses a fifth of its volume between 30 and 80 steps (seen, measured).
- The rules that **follow loosely** (a tenth of the way, or counted by swept area) are the one-plane rule with
  creases, brims or debris: no buds off the flat page (2 bud directions, measured).
- Two rules keep round buds off the flat page AND take the rabbit apart into bodies. Both are trades, not wins:
  - `sheet.evc005e70k16` (eased votes): the basilica has buds in **four** directions (the flat page and the plane
    square to it), not rings; the rabbit and the Siegel disc are clean bodies where `along` has lumps. But its rabbit
    IS the one-plane rule's rabbit (one verdict in eight of its inside differs), so the smaller bodies sit round the
    flat page only; the four directions exist only for c near the x-axis (gone at c = -1 + 0.2i); for c a little off
    the axis the bodies show a seam; close up, thin loose flakes hover over the basilica's skin between the two bud
    rows; it has three hand-set numbers, and changing one of them (16 to 4) fuses the rabbit at its pinch. On the letter of the briefing's section 6, for the six test shapes, it does have both
    things asked for; on the user's tests 2 and 5 it fails at least as badly as `along`.
  - `alongmem.c_wake1` (first step "along", then one fixed plane): the basilica's middle body keeps its eight buds,
    the other bodies are bare off the page; the rabbit has smooth bodies, also off the page, but **two of them float
    free** (7.2 % of the volume each, gap 0.107 on two grids); its Mandelbrot solid is the one-plane solid exactly.
- `along` is still the only rule with round buds in many directions on every body and for every c tried. Its rabbit
  and Siegel disc are still lumps. That is a fail too; it is simply the best failure.

## 1. What was compared

| name here | whose | why this one |
|---|---|---|
| `along` | bench | the best so far |
| `oneplane` | bench | the clean reference |
| `sheet.evc005e70k16` | sheet, their first pick | "closest to section 6" |
| `sheet.ease` | sheet, second pick | the dial-free rule with four buds |
| `alongmem.c_wake1` | alongmem, first pick | "the only clean rule whose rabbit comes apart" |
| `alongmem.c_wake2` | alongmem, second pick | two generations of buds |
| `span.c_lag10` | span, first pick ("least bad") | nearly the one-plane rule |
| `span.c_page` | span, third pick; taken instead of their second (`c_lag25`) because it is the literal reading with c as partner | literal reading |
| `frame.area_1_px` | frame, first pick ("least damaged") | smooth form of following |
| `frame.orb_inf_px` | frame, second pick | the literal reading: plane of the last two orbit points |

`span.c_lag25`, `sheet.vote4` and the bench `lathe` were run through the numbers only (not the pictures).
All ten are loaded from the searchers' own files by `out/r21/judge/myrules.py` (`RULES`, `get(name)`); nothing was re-coded.

## 2. Definitions in full

Common to all. v = (x, y, z), r = |v|. The flat page is z = 0, the x-axis the real line.
- **P**, the one-plane square: P(x, y, z) = f (x^2 - y^2, 2xy, 2rz), f = r^2 / (r^2 + z^2).
- Rot(a) turns (y, z) by the angle a round the x-axis: (y, z) -> (y cos a - z sin a, y sin a + z cos a).
- **P about the sheet at turn t** = Rot(t) P(Rot(-t) v).
- Orbit: v <- square(v) + c. A point is inside if |v|^2 stays under 36 for the steps counted. Julia set of c: the
  start points that stay. Mandelbrot solid: the orbit is started at the point c (the first step of the orbit of 0)
  with the count k = 0 and a fresh carried state.

1. **`along`** (no memory): phi = atan2(z, y); psi = phi - sin(4 phi)/4; square = P about the sheet at psi.
2. **`oneplane`** (no memory): square = P(v).
3. `lathe` (no memory): square = (x^2 - y^2 - z^2, 2xy, 2xz).
4. **`sheet.evc005e70k16`**. Carried: a vector w = (w1, w2), start (0.05, 0) (the flat page with strength 0.05).
   One "eased vote" of a thing with coordinates (y, z), ease e and weight k: pw = atan2(w2, w1);
   t = atan2(2yz, y^2 - z^2) - pw, brought into -180..180 degrees; a = pw + t - e sin t;
   w <- w + k (y^2 + z^2) (cos a, sin a).
   Each step: (i) c votes: coordinates (cy, cz), e = 0.7, k = 16 (a c on the x-axis has weight 0); (ii) the point
   votes: coordinates (y, z), e = 0.7, k = 1, against the w just changed; (iii) theta = atan2(w2, w1) / 2 and
   square = P about the sheet at theta; (iv) c is added.
5. **`sheet.ease`**. Carried: theta, start 0. phi = atan2(z, y) (theta where the point is on the x-axis);
   d = phi - theta brought into -90..90 degrees; theta <- theta + d - sin(2d)/2; square = P about the sheet at theta.
6. **`alongmem.c_wake1`**, **`c_wake2`**. Carried: the count k only. For k < n the square is `along`(v), for k >= n
   it is P(v); n = 1 and 2.
7. **`span.c_lag10`**. Carried: a plane through 0 as a unit normal n (n and -n the same), start (0, 0, 1).
   Before each squaring: m = unit(v x c) (m = n where v and c are in line, sine under 1e-9, or one is 0);
   s = +1 if n.m >= 0, else -1; n <- unit(0.9 n + 0.1 s m). Real axis of the plane: a = (e_x - n_x n) / sqrt(1 - n_x^2)
   (if the plane is square to the x-axis: the direction in it nearest +y); b = n x a. Square = X a + Y b + Z n with
   (X, Y, Z) = P(v.a, v.b, v.n). (`span.c_lag25`: 0.75 and 0.25 in place of 0.9 and 0.1.)
8. **`span.c_page`** (no real memory). n = unit(v x c); where v and c are in line (also at the first Mandelbrot
   squaring, v = c): the plane through v nearest the flat page, n = (-xz, -yz, x^2 + y^2) / (rho r), rho = sqrt(x^2 + y^2)
   (on the z-axis: the x-z plane). Real axis a as in 7. Square inside the plane: 2 (a.v) v - |v|^2 a.
9. **`frame.area_1_px`**. Carried: a frame E = (e1, e2, e3) of three unit vectors at right angles, start (x, y, z).
   Square F = A e1 + B e2 + W e3 with (A, B, W) = P(v.e1, v.e2, v.e3); new point v' = F + c. Then the page tips:
   w = v x v' (not unit vectors); p = w.e3; wp = w - p e3; q = |wp|; m = wp / q;
   tau = atan2(2 mu p q, 1 + mu (p^2 - q^2)) / 2 with mu = 1; e3 <- cos(tau) e3 + sin(tau) m; e1 <- the shadow of the
   x-axis on the new page, x - (x.e3) e3, made one long (the old e1's shadow if that is zero); e2 = e3 x e1.
10. **`frame.orb_inf_px`**. The same frame, square and v'. Then w = unit(v) x unit(v'); p, wp, q, m as above;
    tau = atan2(2pq, p^2 - q^2) / 2 (the smallest tip that brings e3 onto the line of w; no tip where v and v' are in
    line); e3, e1, e2 as above. So the first squaring is about the flat page and every later point is squared inside
    the plane of the last two orbit points.

## 3. What was done (scripts in `out/r21/judge/`)

- (a) `julia.py`: `M.julia_sheet` unchanged (six sets, 380 x 285 x 240 blocks) at **60 steps** (library default 28,
  which hides leaks), eye at (0.45, 0.5, 1.0) and at (0.2, 1.0, 0.35); one rule per run, rows stacked.
- (b) `cuts.py`: `M.cut_axis` at 0, 11.25, 22.5, 33.75, 45, 90 degrees (300 x 217) and `M.cut_across` at x = 0 and
  x = -1 (217 x 217), basilica and rabbit, 80 steps.
- (c) `jnum.py` -> `num/*.json`, printed by `table.py` -> `numbers.txt`: inside points on a 120 x 120 x 120 grid
  (x -1.8..1.8, y and z -1.5..1.5; no grid point on z = 0, so a film on the page is not counted), basilica and rabbit,
  at 30, 80 and 200 steps; connected pieces; pieces after peeling one layer; a ball round the rabbit's pinch point;
  flat-inside points lifted off the page; arcs on circles round the x-axis.
- (d) `M.flat_check` and `M.spun_check` with the library's defaults (40,000 points), in `jnum.py`.
- Unfriendly extras: `hostile.py` -> `hostile.txt` (same-as-one-plane count, Siegel disc and San Marco to 500 steps,
  c just off the x-axis, the rabbit turned out of the page), `floating.py` -> `floating.txt`, `debris.py` ->
  `debris.txt`, and three one-off measurements kept as `dials.txt`, `leaveaxis.txt`, `valley.txt`, `mandelnum.txt`.
- Pictures beyond (a) and (b): `offaxis.py` (c just off the x-axis), `mandel.py` (`M.mandel_sheet`, solid at 40 steps),
  `closeup.py`, `budzoom.py` (zoomed cuts through single buds; with the one-off count `slivers.txt`),
  `usersheet.py` (the sheet for the user).

## 4. Numbers (all measured; full tables in `numbers.txt`, `hostile.txt`, `floating.txt`, `debris.txt`)

**(d) Flat page and turning.** `M.flat_check`: 0 of 40,000 verdicts differ for the Mandelbrot set, basilica, rabbit
and Siegel disc, for all ten rules (and `lathe`, `c_lag25`, `vote4`). `M.spun_check`, share of pairs that change
when turned (Mandelbrot solid / basilica): along 1.52 % / 0.25 %; oneplane 1.23 / 0.34; evc005e70k16 1.20 / 0.20;
ease 0.83 / 0.18; c_wake1 1.23 / 0.34; c_wake2 1.25 / 0.34; c_lag10 1.49 / 0.33; **c_page 3.46 / 0.00**;
area_1_px 1.60 / 0.98; orb_inf_px 2.19 / 1.06; lathe 0.00 / 0.00.

**(c) Does the solid stay** (inside points of 1,728,000; "kept" = 80-step count over 30-step count):

| rule | basilica 30 / 80 / 200 | kept | rabbit 30 / 80 / 200 | kept 80, 200 |
|---|---|---|---|---|
| along | 33,888 / 33,888 / 33,888 | 100.0 % | 85,602 / 84,180 / 84,178 | 98.3 %, 98.3 % |
| oneplane | 37,688 / 37,680 / 37,680 | 100.0 % | 23,680 / 22,976 / 22,976 | 97.0 %, 97.0 % |
| sheet.evc005e70k16 | 34,248 / 34,240 / 34,240 | 100.0 % | 27,176 / 26,316 / 26,316 | 96.8 %, 96.8 % |
| sheet.ease | 32,960 / 32,928 / 32,928 | 99.9 % | 31,452 / 12,372 / 901 | **39.3 %, 2.9 %** |
| alongmem.c_wake1 | 36,524 / 36,500 / 36,500 | 99.9 % | 36,174 / 35,000 / 35,000 | 96.8 %, 96.8 % |
| alongmem.c_wake2 | 35,952 / 35,936 / 35,936 | 100.0 % | 51,026 / 49,200 / 49,200 | 96.4 %, 96.4 % |
| span.c_lag10 | 36,592 / 36,592 / 36,592 | 100.0 % | 31,082 / 28,962 / 28,918 | 93.2 %, 93.0 % |
| span.c_page | 40,800 / 40,752 / 40,752 | 99.9 % | 61,312 / 51,400 / 48,784 | **83.8 %, 79.6 %** |
| frame.area_1_px | 40,984 / 38,184 / 37,932 | **93.2 %** | 40,340 / 35,144 / 35,128 | 87.1 %, 87.1 % |
| frame.orb_inf_px | 44,616 / 44,576 / 44,576 | 99.9 % | 37,636 / 30,438 / 28,482 | **80.9 %, 75.7 %** |
| lathe | 40,800 / 40,752 / 40,752 | 99.9 % | 78,504 / 76,868 / 76,868 | 97.9 % |

`span.c_page` has exactly the lathe's basilica counts: for c on the x-axis it IS the lathe.

**Buds of the basilica** (walk round the x-axis at x = 0 on circles of radius 0.56 to 0.64, 2,880 places, 80 steps:
number of separate inside arcs, share of the circle inside): along **8**, 19 to 28 %; oneplane 2, 6 to 8 %;
evc005e70k16 **4** (at 0.60 to 0.64; widths 18.6, 18.6, 14.6, 14.6 degrees at 0.62; at 0.56 and 0.58 the walk meets
8 and 16 arcs: the same four buds, each flanked 5 to 10 degrees to either side by slivers 0.2 to 1.5 degrees wide),
17 to 18 %; along's eight arcs are all 12.6 degrees wide at 0.62 and sit at 45-degree steps; ease 4 (12.4 degrees each), 9 to 14 %; c_wake1 and
c_wake2 **8**, 21 to 31 %; c_lag10 2; c_lag25 2; **c_page 1 arc, 100 % (a
ring)**; area_1_px 2 (6 wide arcs at 0.52 to 0.56: the brim); orb_inf_px 2 to 18 arcs, changing with the radius
(broken rings); lathe 1 arc, 100 %. (The same walk at x = -1 does NOT count buds, because the side body is not
round in cross-section; that table is in `numbers.txt` and is not used.)

**Loose flakes over the skin** (`slivers.txt`; cut across at x = 0, 720 directions between 25 and 65 degrees from
the flat page, radius 0.44 to 0.62; a direction counts if, walking outward, one is inside again after having been
outside): oneplane 0 of 720; **evc005e70k16 336 of 720** (1,840 of 259,200 places, the same at 120 and at 600
steps, so they are inside for good); ease 382 of 720 (12,780 places). along 280 and c_wake1 249, but for those two
the count is mostly the 45-degree bud itself, which stands over the skin on a point, so the number does not
separate buds from flakes. Seen in `budzoom.png`: evc005e70k16 has no bud at 45 degrees, only a thin loose crescent.

**Rabbit: bodies or lump.**

| rule | pinch ball r = 0.12 / 0.06 | biggest piece after peeling one layer | loose after bridging 0.045 gaps (160^3 grid) |
|---|---|---|---|
| along | 74.5 % / 74.6 % | 97 % of what is left (one lump) | 0 |
| oneplane | 35.7 % / 36.9 % | 67 % | 0 |
| sheet.evc005e70k16 | 51.3 % / 51.5 % | 66 % | 0 |
| sheet.ease | 14.8 % / 15.5 % | nothing left (dust) | 2 at 80 steps; 183 pieces = 65 % at 200 steps |
| alongmem.c_wake1 | 38.5 % / 37.6 % | 47 % | **2 pieces = 14.5 % of the volume** |
| alongmem.c_wake2 | 41.7 % / 38.4 % | 41 % | 0 (two pieces of 0.8 % at a gap of 0.061, `floating.txt`) |
| span.c_lag10 | 55.0 % / 64.4 % | 64 % | 0 (2 at 200 steps) |
| span.c_page | 69.7 % / 69.7 % | 36 % (shells) | 0 (6 at 200 steps) |
| frame.area_1_px | 71.0 % / 71.6 % | 67 % | 4 (basilica: 16 loose pieces) |
| frame.orb_inf_px | 21.9 % / 23.0 % | 32 % (shards) | 0 |

"Pinch ball": share of a small ball round the rabbit's pinch point (-0.276, 0.480, 0) that is inside at 80 steps,
not counting the slab within a quarter radius of the page. Three bodies that meet in a point fill about a third.

**Floating bodies** (`floating.txt`, rabbit on 160^3 and 240^3 grids, cube -1.5..1.5): `c_wake1` has three pieces of
85.2 %, 7.2 % and 7.2 %; the two small ones have their middles at (0.04, -0.30, +-0.65) and a gap of 0.110 (5.8
cells) and 0.107 (8.5 cells) to the rest: the gap does not shrink with the cell, they float. `c_wake2`: two pieces
of 0.8 % at a gap of 0.065 and 0.061. along, oneplane, evc005e70k16: one piece.

**Body of the flat picture** (flat-inside points lifted 0.000001 off the page, lost at 300 steps; of 4,146
Mandelbrot / 3,040 basilica / 2,748 rabbit / 3,746 Siegel points): along 10 / 0 / 0 / 1; oneplane 6 / 0 / 0 / 1;
evc005e70k16 5 / 0 / 0 / 1; **ease 108 / 0 / 2,216 / 231**; c_wake1, c_wake2 6 / 0 / 0 / 1; c_lag10 1 / 0 / 0 / 0;
c_page 0 / 0 / 0 / 0; area_1_px 32 / 0 / 0 / 0; **orb_inf_px 686 / 0 / 64 / 1**. So `ease` has a flat rabbit
without body and `orb_inf_px` has a flat Mandelbrot set that is a film over a sixth of its area. `M.flat_check`
sees neither (the skeptic's and the sheet agent's warning, confirmed).

**Is the rabbit the one-plane rabbit?** (`hostile.txt`, 120^3 grid, 80 steps; verdicts that differ from the
one-plane rule's, as a share of the rule's own inside count): **evc005e70k16 3,364 = 12.8 %**; c_lag10 6,042 = 20.9 %;
area_1_px 12,260 = 34.9 %; c_wake1 12,868 = 36.8 %; c_wake2 26,976 = 54.8 %; along 61,408 = 72.9 %.

**Siegel disc and San Marco, 30 / 80 / 200 / 500 steps** (`hostile.txt`): kept from 30 to 500: along 96.6 % / 100 %;
oneplane 97.2 % / 99.1 %; **evc005e70k16 84.9 %** (81,144 / 72,128 / 68,930 / 68,930: it settles) / 99.9 %;
c_wake1 97.9 % / 99.4 %; c_lag10 98.8 % / 99.2 %; **area_1_px 74.8 % / 76.6 %**; orb_inf_px 98.7 % / 99.8 %.

**As c leaves the x-axis** (`leaveaxis.txt`, c = -1 + i t, still inside the round disc of the flat Mandelbrot set;
largest number of arcs on the circles of radius 0.56 to 0.70 at x = 0): along 16, 12, 12, 16, 16, 22, 18 for
t = 0, 0.01, 0.03, 0.06, 0.1, 0.15, 0.2; oneplane 2 throughout; c_wake1 10 to 14 throughout;
**evc005e70k16 16, 10, 8, 6, 8, 4, 2**: at t = 0.2 nothing is left at the upright sheet (0 % inside within 20 degrees
of it; the count of the upright cut is 5,746 against the one-plane rule's 5,670).

**The dials of the eased-vote rule** (`dials.txt`; rabbit at 30 / 80 / 200 steps, pinch ball): weight of c's vote
16: 27,176 / 26,316 / 26,316, 51 %; weight 4: 41,226 / 31,756 / 31,700, **75 %** (fused); weight 1: 32,214 / 25,942 /
25,920, 61 %; ease 1 instead of 0.7: 28,612 / 19,342 / 19,118 (a third lost), bud arcs 13.6 and 10.4 degrees instead
of 18.6 and 14.6; ease 0.5: arcs 24.6 and 19.1, pinch 72 %.

**The rabbit turned out of the page** (`hostile.txt`, `dials.txt`; inside count at 80 steps with c turned 0 / 2 / 5 /
10 / 30 / 45 / 90 degrees round the x-axis): evc005e70k16 26,316 / 25,849 / 5,839 / 0 / 0 / 0 / 26,336; oneplane,
c_wake1, c_wake2: 0 from 10 degrees on; along 84,180 / - / - / 94,706 / 584 / 8,224 / 84,180.

**Mandelbrot solid** (`mandelnum.txt`, 200,000 random c, 80 steps). Share of the box inside: along 7.21 %, lathe
7.37 %, oneplane 1.45 %, evc005e70k16 4.58 %, ease 6.02 %, c_wake1 1.45 %, c_wake2 1.45 %, c_lag10 1.80 %, c_page
8.70 %, area_1_px 1.69 %, orb_inf_px 4.72 %. **c_wake1 against the one-plane rule: 0 of 200,000 verdicts differ**
(c_wake2: 4). The cut along the upright sheet against the flat set (84,000 places): along 0, ease 0, evc005e70k16
104, orb_inf_px 6,421, the one-plane kind 13,420. Walking round the x-axis through the middle of the period-3 bud
(arcs, widest in degrees): lathe 1 arc of 360; oneplane, c_wake1, c_wake2 2 arcs of 2.9 (a thin lens);
evc005e70k16 4 arcs of 8.6; along 4 patches of 27.5 and 51 specks; ease 43 specks of 0.1; c_page 2 arcs of 168;
orb_inf_px 2 arcs of 47 and 32 specks; area_1_px 2 arcs of 10.1; c_lag10 6 arcs, widest 1.4.

**A c outside the flat Mandelbrot set** (`valley.txt`). c = -0.75 + 0.1i lies in the valley between the heart and the
round disc: the flat picture has no inside (55,272 / 17,702 / 4,032 / 120 / 0 of 259,800 places at 30 / 80 / 200 /
500 / 1000 steps). On the 120^3 grid at 30 / 80 / 200 / 500 / 1000 / 3000 steps: along 67,006 / 8,374 / 1,362 / 34 /
0 / 0 (it empties, as the flat picture does); **oneplane 77,100 / 52,832 / 51,804 / 51,760 / 51,760 / 51,760**;
c_wake1 76,518 / 42,408 / 40,924 / 40,842 / 40,842 / 40,842; evc005e70k16 72,592 / 38,510 / 33,352 / 29,110 /
19,630 / 4,572. Level cuts z = h of the one-plane solid there (65,100 places, 1000 steps): 0 at h = 0, 162 at 1e-6,
1,314 at 0.001, 5,626 at 0.05, 7,968 at 0.2.

## 5. The user's five tests, rule by rule

T1 flat cut exact; T2 bodies and buds from the power, no dial that sets a number of planes; T3 no shards, dust or
loose debris; T4 not spun, no rings; T5 a principled carry-over. Then the two things section 6 asks of the Julia sets.

| rule | T1 | T2 | T3 | T4 | T5 | basilica: round buds off the page | rabbit: separate bodies |
|---|---|---|---|---|---|---|---|
| along | yes: 0 of 40,000 | **no**: sin(4 phi) sets four sheets | yes at this size: 0 loose pieces, 100 % and 98.3 % kept (fins close up are known, not re-examined) | yes: 8 arcs | **no** | **yes, 8 directions**, on every body (cuts-basilica-a row 1) | **no: lump**, pinch ball 74.5 %, 97 % in one piece after peeling |
| oneplane | yes | yes (no dial) | yes: 0 loose, 97.0 % kept | yes: 2 arcs | yes | **no**: 2 arcs, the flat page only | yes |
| sheet.evc005e70k16 | yes: 0 of 40,000; 0 of 2,748 flat rabbit points lost when lifted | **no**: the second plane is put in by the easing law, the bud's thickness by the dial 0.7 | **no, close up**: on the grids 0 loose pieces and 100.0 % / 96.8 % kept, but thin loose flakes hover over the skin of the basilica between the bud rows (budzoom.png row 2; in 336 of 720 directions, still there at 600 steps; one-plane: 0); the Siegel disc loses 15 % before it settles; c off the axis shows a seam (offaxis-a row 3) | yes: 4 arcs, round from both eyes | **no**: three hand-set numbers; 16 -> 4 fuses the rabbit | yes, **4 directions** (two planes), only for c near the x-axis | yes, but it is the one-plane rabbit (12.8 % of verdicts differ) |
| sheet.ease | on the page yes; **the flat rabbit has no body**: 2,216 of 2,748 lost when lifted a millionth | **no**: two planes built into the turning law | **no: dust**, rabbit 39 % kept at 80 steps, 3 % at 200 | yes: 4 arcs | no | yes, 4 directions | **no: dust** (cuts-rabbit-a row 4) |
| alongmem.c_wake1 | yes | **no**: sin(4 phi) again, and a counted first step | **no: two bodies float free**, 14.5 % of the rabbit, gap 0.107 | yes: 8 arcs | **no** | yes, 8, **on the middle body only** (cuts-basilica-a row 5: side bodies bare at 45 and 90 degrees) | yes (pinch ball 38.5 %), two of them loose |
| alongmem.c_wake2 | yes | no | no: two loose bodies of 0.8 %, slivers in the cut across (cuts-rabbit-b row 1) | yes: 8 arcs | no | yes, 8, two generations | crowded, on the way back to the lump (julia-cam1-b, julia-cam2-b row 1) |
| span.c_lag10 | yes | yes (as one-plane) | nearly: 0 loose, but 93 % kept and creases (julia-cam2-b row 2) | yes: 2 arcs | no: a lag dial and a jump | **no**: 2 arcs | yes, creased; fatter at the pinch (55 % and 64 %) |
| span.c_page | yes | yes | **no**: rabbit a fan with dust, 84 % then 80 % kept | **no: rings**, 1 arc, 100 %; the lathe's basilica exactly | yes (literal) | **no: rings** | **no**: fan of ribbed discs |
| frame.area_1_px | yes | yes (as one-plane) | **no**: basilica 93.2 % kept, 16 loose pieces; San Marco 77 %, Siegel 75 % kept | yes: 2 arcs | no | **no**: brim, no buds | knobbly, fused at the pinch (71 %) |
| frame.orb_inf_px | on the page yes; 686 of 4,146 flat Mandelbrot points have no body | yes | **no**: rabbit 80.9 % then 75.7 % kept, fans in every cut | **no: rings and ribs** (julia-cam1/2-b row 5) | yes (literal) | **no: rings** | **no**: ribbed shell |

## 6. Ranking against "along" (Julia sets first)

1. **along**. Still the only rule with round buds in many directions on every body, for every c tried (also at
   c = -1 + 0.2i, offaxis-b). Fails: rabbit and Siegel disc are lumps; T2 and T5.
2. **sheet.evc005e70k16**. Better than along: rabbit and Siegel disc are clean bodies, no lump. Worse: four bud directions in two fixed planes instead of eight; none at all once c is 0.2 off the
   x-axis; a seam across the bodies for c just off the axis; loose flakes over the skin close up; no buds on the
   flanks of its buds where along has them (budzoom.png); the rabbit is the one-plane rule's; three dials against one. Mandelbrot solid: two flat sets crossed at right angles, smooth between (mandel-a row 3), against along's rock.
   A trade, not a win.
3. **alongmem.c_wake1**. Better than along: the rabbit comes apart into smooth bodies, also off the page. Worse:
   only the middle body of the basilica has the eight buds; two bodies of the rabbit float; San Marco is a fused
   mass (julia-cam1-a row 5); Mandelbrot solid is the one-plane cushion. A trade inside along's own family.
4. oneplane (reference): clean everywhere, buds round the flat page only.
5. span.c_lag10: the one-plane rule with creases and a small leak. Nothing new.
6. alongmem.c_wake2: more buds than c_wake1, but the rabbit is crowding back into a lump and San Marco is a lump.
7. frame.area_1_px: one-plane with a brim, loose slivers and slow leaks on four shapes.
8. sheet.ease: a clean four-bud basilica, but the rabbit is dust and the flat rabbit has no body. Out.
9. frame.orb_inf_px (literal reading): rings and ribs, a shell for a rabbit. Out.
10. span.c_page (literal reading): the lathe for c on the x-axis, a fan with dust for the rabbit. Out.

## 7. Where my findings differ from, or sharpen, the searchers' reports

- **sheet**, "along shatters at -0.75 + 0.1i" (their `final-along.png`) is not a fault of along. That c is outside
  the flat Mandelbrot set and the flat picture has no inside there (measured, section 4). along empties as it should.
  The rules that "survive" there keep a solid off the page with the page as an empty slit through it: the one-plane
  rule holds 51,760 grid points for 3000 steps. That is a property of the one-plane rule I did not see mentioned:
  **for a c just outside the flat set it has a body where the flat picture has none.** (measured; outside my brief,
  not followed further.)
- **sheet** marks evc005e70k16 as beating along. On the letter of section 6 for the six shapes it has both features;
  I do not count it as beating along, for the reasons in section 6. Their numbers are confirmed: rabbit kept 96.8 %
  (theirs 2.17 -> 2.11), Siegel disc 15 % lost before settling, four buds, 104 of 84,000 upright places differ.
  New from me: its rabbit is the one-plane rabbit to 12.8 %; the four directions end between t = 0.15 and 0.2;
  the weight 16 is tuned (4 gives a fused pinch).
- **alongmem**: all confirmed. Floating bodies 7.2 % each, gap 0.107 to 0.110 (theirs 0.108 to 0.124); Mandelbrot
  solid equal to the one-plane solid, 0 of 200,000 (theirs 5 of 300,000).
- **span**: confirmed. c_page equals the lathe for c = -1 (identical counts, 1 arc of 100 %); c_lag10's rabbit keeps
  93.2 % (theirs 2.54 -> 2.37 %).
- **frame**: confirmed (area_1_px basilica 93.2 % kept, rabbit 87.1 %; orb_inf_px rabbit 80.9 %). New from me:
  orb_inf_px's flat Mandelbrot set has no body over a sixth of its area (686 of 4,146 points lost when lifted a
  millionth), and its flat rabbit loses 64 of 2,748.

## 8. Pictures (all opened and looked at)

| file | what it shows |
|---|---|
| `cuts-basilica-a.png` | along: eight buds in the cut across, flat-like cuts at 45 and 90 degrees; oneplane: two buds; evc005e70k16 and ease: four buds, the upright cut is the flat basilica; c_wake1: eight buds on the middle body, side bodies bare at 45 and 90 |
| `cuts-basilica-b.png` | c_wake2: eight buds, small ones on the side bodies; c_lag10: the one-plane cuts; c_page: the flat basilica in every sheet and a full disc across (a ring set); area_1_px: diamond bodies, fuzz and specks, a brim; orb_inf_px: squarish main body, burrs, broken arcs round it |
| `cuts-rabbit-a.png` | along: a rabbit-like cut in every sheet with ragged skin, shells in the cut across (a lump); oneplane and evc005e70k16: the same clean ovals, cut for cut; ease: dust; c_wake1: separate ovals, also off the page, with detached ones above and below |
| `cuts-rabbit-b.png` | c_wake2: more ovals, slivers at the right of the cut across; c_lag10: one-plane ovals with streaks; c_page: rabbits with a line of dust through them, nested rings across; area_1_px: fused blocks; orb_inf_px: fans of shards |
| `julia-cam1-a.png`, `julia-cam1-b.png` | the six Julia sets of all ten rules, eye 1, 60 steps (described in sections 0 and 6) |
| `julia-cam2-a.png`, `julia-cam2-b.png` | the same from above: along's and evc005e70k16's and c_wake1's buds are separate round buds, not rings; c_page and orb_inf_px are stacks of rings; area_1_px has loose slivers round every body |
| `julia/cam1-*.png`, `julia/cam2-*.png` | the single rows the sheets are stacked from |
| `offaxis-a.png` | c = -1 + 0.03i and -1 + 0.1i: along keeps eight buds; evc005e70k16 has a seam (a ledge across the front of every body) and at 0.1i a lopsided cut across with the upright buds shrunk to spikes; c_wake1 keeps eight buds, clean |
| `offaxis-b.png` | c = -1 + 0.2i and -0.6 + 0.2i: along rough and ribbed but with buds; evc005e70k16 is the one-plane shape with a ledge, no upright buds; c_wake1 has a few detached specks at -1 + 0.2i |
| `mandel-a.png`, `mandel-b.png` | Mandelbrot solids: along a rock (flat set at 0, 45, 90 degrees, ragged between); oneplane, c_wake1, c_wake2 the same smooth cushion; evc005e70k16 flat set at 0 and 90, smooth hearts between, a four-pointed star across; ease ragged blocks with dust; c_lag10 a cushion with a straight tear; c_page a ribbed shell with a half-disc flange; area_1_px a cushion with small wings; orb_inf_px a ribbed shell with a speckled bite |
| `closeup.png` | see section 9 |
| `budzoom.png` | zoomed cuts across the x-axis through single buds of the basilica (window 0.36, 120 steps). along: the buds at 0 and 90 degrees carry smaller buds on their flanks, so it has buds on buds ROUND the axis too; its bud at 45 degrees is a plain lens with a few specks beside it. evc005e70k16: fat buds at 0 and 90 degrees with ragged, spiky pieces beside them and flat flakes just over the main body's skin; at 45 degrees no bud, only a thin loose crescent over the skin. c_wake1: the bud at 0 degrees is bare (as one-plane's), the bud at 90 degrees is along's, the bud at 45 degrees a plain lens. oneplane: one bare bud at 0 degrees, nothing else |
| `sheet-for-user.png` | the one sheet for the user: four rows, plain labels |

The concentric ripples on the front of every smooth body in the solids are the steps between blocks of the rough
picture (they are centred on the point nearest the eye in every row), not a feature of any rule. (seen, reasoned)

## 9. Close-ups, limits, and what went wrong

`closeup.png` (seen; 300 x 225 x 210 blocks, 80 steps, half width 0.85, the basilica's middle body and the rabbit
round its pinch, each from the two eye positions):
- along: the middle body carries big round buds with crowns of smaller buds and rows of small ones, in many
  directions, and fine prickles along the outline (the known fins, at this size only as points). The rabbit is
  stacked sheets: terraces and overhangs, one mass. (The close-up draws only what lies within 0.85 of its middle
  along the line of sight, so the nearest part of this lump may be cut off.)
- sheet.evc005e70k16: smooth skin, two rows of round buds (one round the flat page, one along the plane square to
  it), nothing between the rows; a faint ridge runs along the second row. The rabbit is clean separate bodies with
  small buds along the flat-page rim only; no specks at 80 steps.
- alongmem.c_wake1: the middle body has the eight larger buds and rows of small ones; the rabbit's bodies are
  smooth, and a dumbbell-shaped extra body lies across the place where they meet. (That is not one of the two
  floating bodies, whose middles are at (0.04, -0.30, +-0.65); whether the dumbbell is joined to the rest I did not
  measure separately. It is not among the loose pieces counted, so it is within 0.045 of the main piece.)

Limits and what went wrong:
- The close-ups are still rough blocks (pixel 0.0057). A first attempt at 400 x 300 x 280 took 7 minutes for along
  alone; I stopped the queue, deleted that one row unseen, and reran all three smaller.
- All solids are rough blocks; the judgement of "round" is by eye from two eye positions plus the arc widths.
- The airplane and the dendrite are specks or empty for every rule at this size and were not judged.
- along's known fault "thin fins close up" was not re-examined at fine scale.
- The reasons given in the searchers' notes (first-step law, tear argument, Claim S) were not re-derived; I checked
  outcomes only.
- Process: my first background run of the Julia sheets ended at once because the log folder did not exist yet;
  restarted, nothing lost. A script first named `numbers.py` hid a standard module and broke numpy (the trap the
  skeptic also met); it is `jnum.py` now. `debris.py` was first run with gaps of 0.09 bridged, which hid c_wake1's
  floating bodies (gap 0.107); the kept version bridges 0.045. No single run went over ten minutes (longest: one
  Julia row of a frame rule, 320 s).
