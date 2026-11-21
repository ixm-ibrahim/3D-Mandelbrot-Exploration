# Round 21, the checker: every claim of the six reports, tried again

Marks: **measured** = a number from a script of mine in this folder; **seen** = in a picture I opened;
**reasoned** = worked out by hand here. Verdicts: HOLDS, WRONG, UNPROVEN (what is missing).
All my pictures are cuts or rough blocks made with `out/r21/lib/mem.py`; nothing here is a fine render.
Nothing outside `out/r21/checker/` was written. The longest run took 425 s.

## 0. In short

- Almost every number in the six reports comes out again with my own scripts, usually to the last digit shown.
- **Claim S holds**, with the assumptions written out in section 2. I attacked it with 12 recipes of my own. The
  ones that looked like counterexamples (up to 0.34 % of verdicts changing under a turn) are rounding: with 60 and
  120 decimal digits 75 of 75 re-checked verdicts return to the flat set spun.
- **Nothing found this round beats `along`.** The one "beats along: yes" in the reports (sheet, `evc005e70k16`) is
  not supported: for the rabbit and the Siegel disc that rule IS the one-plane rule to the eye (132 of 60,000
  verdicts differ), its basilica has four bud directions against `along`'s eight, bodies are lopsided for c just off
  the x-axis, and it has three dials. One of its supporting arguments is wrong (section 5).
- **Round buds off the page that are not rings exist this round only for Julia sets with c on the x-axis**, and
  only (a) at the sheet square to the flat page (`ease`, `evc...`: four directions), or (b) in eight directions when
  `along`'s own formula does the first squaring (`c_wake1`, `c_wake2`, `b_keep`). All re-measured.
- **The library computes what it says.** Three caveats are real (section 4); none overturns a result; the numbers
  they touch are named.
- Things said too strongly in the reports: section 5.

## 1. What I did (scripts, all in this folder)

| script | output | what |
|---|---|---|
| `ck.py` | | my tools: rules re-coded from the reports' WORDS, a second iteration loop, circle walk, volume, lift test, turned test |
| `t1_defs.py` | `t1_defs.txt` | their code against my re-coding; `M.flat_check` and `M.spun_check` for every "best" rule |
| `t13_defs2.py` | `t13_defs2.txt` | the same for span's `c_lag10`, `c_lag25` and frame's `area_1_px`, `orb_inf_px` |
| `t2_film.py` | `t2_film.txt` | has the flat picture body? lift 1e-6 and 1e-3 |
| `t3_claimS.py`, `t3b_exact.py` | `.txt` | Claim S: 12 recipes of mine, then three of them with 30 / 60 / 120 decimal digits |
| `t4_lib.py` | `t4_lib.txt` | the library: dead zone of `M.half`, `M.stay`, `M.sq_about`, start at 0 against start at c |
| `t5_buds.py` | `t5_buds.txt` | buds met on circles round the x-axis; the first-step law; bud sizes |
| `t6_cuts.py` | `cuts-*.png` | cut sheets (basilica, rabbit, c just off the axis, Mandelbrot) |
| `t7_vol.py` | `t7_vol.txt` | volumes at 30 / 80 / 200 / 500 steps |
| `t8_solids.py` | `solids-A.png` | rough solids at 80 steps, two eye positions and a close-up |
| `t9_sym.py` | `t9_sym.txt` | which turns and mirrors leave each solid unchanged |
| `t10_spot.py` | `t10_*.txt` | spot checks of the remaining numbers of each report |
| `t11_pieces.py` | `t11_*.txt` | connected pieces on a 141^3 grid; `M.solid` against direct verdicts |
| `t12*.py` | `cuts-lagrabbit.png`, `cuts-otherrabbit.png`, `cuts-vote4rabbit.png` | the rabbit for the lag family and for the other best rules |

## 2. Claim S and its exact assumptions

**Statement.** A recipe = a thing the orbit carries (anything), a start for it, and a step. Suppose
1. the start of the carried thing for the turned c is the turned start (a start that is the same for every c must
   itself be unchanged by every turn round the x-axis: "nothing yet", a number, something on the x-axis);
2. the step, applied to turned things, gives the turned result, for EVERY angle and in EVERY case, the undefined
   cases included (a tie-break "keep what you carry" is fine, "use the flat page" is not);
3. "has left" is judged by the length alone;
4. the arithmetic is exact.

Then the orbit of the turned c is the turned orbit, and the Mandelbrot solid looks the same from every side of the
x-axis. If its flat cut is the flat set, it is the flat set spun. Not needed: what is carried, how long it is
remembered, whether the recipe tells left from right, whether it is smooth, whether it is exact on the flat page.
If the recipe also never says left or right, every orbit point stays in the sheet of c: no new plane is ever made.
The same holds for the Julia set of a c on the x-axis (basilica, San Marco, airplane): rings.
What S does NOT say: anything about a recipe with a fixed starting sheet, or about Julia sets of c off the x-axis.

**reasoned**: the induction is one line per step; I re-did it and the mirror step. **HOLDS.**

**measured** (`t3_claimS.txt`; 40,000 pairs, turns of 37 and 90 degrees; 60,000 points against the lathe):

| my recipe (nothing fixed) | flat check M/bas/rab/Sie of 20,000 | Mandelbrot turned 37 (40 steps), 37 (80 steps) | differs from the lathe of 60,000 |
|---|---|---|---|
| `cov_cmid0.5`, `cov_votes`, `cov_far` (stable, unhanded) | 0/0/0/0 | 0.0000 %, 0.0000 % | 0 |
| `cov_lag0.25`, `cov_lag0.75` | 2/0/0/0 | 0.005 %, 0.07 %; 0.000 %, 0.01 % | 20; 10 |
| `cov_lag0.5` | 30/0/209/0 | 0.015 %, 0.135 % | 92 |
| `cov_delay` | 616/0/2710/2474 | 0.158 %, 0.085 % | 1,022 |
| `cov_cmid-1` (sheet = the point's sheet mirrored in c's) | 579/0/0/3770 | 0.070 %, 0.343 % | 1,999 |
| four handed ones (`cov_lag0.5_hand20`, `cov_delay_hand25`, `cov_cmid0.5_hand30`, `cov_votes_hand15`) | fail (138 to 3,770) | 0.0000 % (one: 0.0025 % at 80 steps) | 1,227 to 2,364 |

Basilica turned: 0.0000 % for all twelve. The nonzero rows are rounding (`t3b_exact.txt`): for `cov_delay`,
`cov_lag0.5`, `cov_cmid-1` I took 25 c each where the float verdict differs from the lathe and ran them in my own
scalar code with Python `decimal`: 30 digits: 13, 23, 17 of 25 agree with the flat set spun; **60 digits: 25, 25, 25;
120 digits: 25, 25, 25**; the orbit's largest distance from the sheet of c is 5e-17 / 7e-20 / 6e-26 with 60 digits
and 6e-76 / 7e-80 / 1e-85 with 120. (The failed flat checks in rows 2 to 5 are the same rounding: my recipes take
angles with atan2, which throws a flat point 1e-16 off the page, and these recipes blow that up.)
The skeptic's 16 attempts, run with my turned test: the 3 that fail the flat check are spun to the last point; the
13 exact ones show 0.0000 % to 0.4375 % (`S6 span2`); basilica 0.0000 % for all 16. The prover's nine: the same
picture (`delay_cov` 0.182 %, `lag50_cov` 0.013 %, the rest 0.000 %).

Definitions of my recipes (carried: turn theta of a sheet and a flag "a sheet exists"; phi = atan2(z, y); P about
the sheet at theta = Rot_x(theta) P(Rot_x(-theta) v)):
- `cov_lag(lam, hand)`: the first point off the x-axis sets theta = phi; later theta moves by
  0.5 atan2(lam sin 2d, 1 - lam + lam cos 2d), d = phi + hand - theta brought into -90..90; then P about theta.
- `cov_delay(hand)`: P about the sheet of the last earlier point off the axis, turned by hand (the first: own sheet).
- `cov_cmid(s, hand)`: theta = phi_c + s (phi - phi_c) + hand (c on the axis: phi). s = -1 is the mirror image.
- `cov_votes(hand)`: w starts as (0, 0); w += (y^2 - z^2, 2yz); theta = 0.5 atan2(w2, w1) + hand (-1)^k.
- `cov_far`: the sheet of the orbit point that was farthest from the x-axis so far.

## 3. The dichotomy "only at the flat page / a whole number of times / a ring"

- As logic about any solid (prover D1): the inside part of a circle is the whole circle or separate arcs. True and
  empty; it does not make two buds have the same count. **HOLDS** (reasoned). The hand-built necklace solid
  (`out/r21/prover/t6_necklace.png`, **seen**: 20 beads on the period-3 circle, other counts elsewhere, flat cut =
  the flat set) is a look-up table, labelled as such in the picture; it is NOT the output of a squaring rule.
- With symmetry (prover D3): the turns that leave a rule's fixed data unchanged are all turns, or the multiples of
  360/n. **HOLDS** (reasoned), with one correction: symmetry gives the LEAST repeat, not the count. Buds come in
  multiples of n (2n off the mirror sheets); nothing in the argument forbids more.
  **measured** (`t9_sym.txt`, percent of 40,000 verdicts that change):

  | rule | Mandelbrot: half-turn / quarter / 45 / 22.5 | basilica: half / quarter / 45 / 22.5 |
  |---|---|---|
  | lathe (`own`) | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
  | all scout rules with a flat start | 0 / 0.46 to 4.28 / ... | 0 / 0.17 to 0.62 / ... |
  | `along`, `away` | 0 / 0 / 1.59, 0.99 / 1.70, 0.83 | 0 / 0 / 0.09, 0.34 / 0.27, 0.35 |
  | `b_keep` | 0 / 0 / 0 / 1.99 | 0 / 0 / 0 / 0.27 |
  | **`ease`** | 0 / **0.000** / 1.08 / 1.02 | 0 / **0.000** / 0.17 / 0.16 |
  | `evc005e70k16` | 0 / 0.040 / 1.74 / 1.25 | 0 / 0.075 / 0.19 / 0.18 |
  | `orb_inf_px` | **0.390** / 2.98 / ... | 0 / 0.85 / ... |

  Mirrors in the flat page and in the upright page: 0.000 for every rule in the table.
  New here: `ease` names only the flat page, yet its solids are unchanged by a QUARTER turn. Reason (reasoned): its
  turn law h(d) = d - sin(2d)/2 leaves the point sin(2d)/2 off the squaring sheet, and that changes sign under a
  quarter turn, which is a mirror image; so starting from the upright sheet gives the mirrored orbit. The sin(2d)
  plays the part that sin(4 phi) plays in `along`: it is what sets the count, here four. `evc...` has it nearly.
  And `orb_inf_px` changes 0.39 % of its Mandelbrot verdicts under a half-turn that cannot change anything: that
  is this rule's rounding noise (it is unstable), see section 4.
- That buds can root only along lines on a smooth body (prover D4): **UNPROVEN**. It is a count of conditions with a
  stated gap (rules with creases); the skin measurement behind it (three fixed rules) I did not re-run.
- That a rule which forgets its start can only cut pieces out of the flat set spun (prover F4): lemma **HOLDS**
  (reasoned: the lathe's slopes multiply volume by 8 x |v|^2, and a cycle off the sheet needs the product of |2x| to
  be 1, so volume does not shrink); the conclusion is **UNPROVEN in general, measured**: `first`, `first2`, `first3`,
  `first8`, `delay` hold 5.47 / 4.37 / 3.65 / 2.22 / 3.27 % of the box at 200 steps with 0.024 / 0.014 / 0.014 /
  0.005 / 0.004 % outside the spun set; cut away 24 / 39 / 49 / 69 / 54 % (prover: 24 / 40 / 50 / 69 / 54).

## 4. The library errors that were reported

| report | my test (`t4_lib.txt`, `t11_solid.txt`) | verdict | what it touches |
|---|---|---|---|
| `M.half` reads a sheet within 5e-9 radians of the flat page (or the upright sheet) as that page | turns 1e-10 .. 5e-9 read back as 0; 7e-9 as 7.45e-9; 1e-7 right to 0.04 % | **confirmed** | lift tests below about 1e-8 with rules that use `M.sq_about`: library lag25 at lift 1e-12 loses 14 of 2,368 flat Mandelbrot points, my angle-carried lag25 loses 195; from 1e-9 on they agree (1e-9: 178 / 203; 1e-8: 206 / 207; 1e-6: 210 / 209). So: the prover's column "lifted by 1e-13" (K1) and alongmem's "lifted by a billionth" for `b_delay` are UNDER-counts; the direction of both findings stands. The 1e-6 lifts of sheet, skeptic and prover are untouched |
| `M.flat_check` passes a flat page that is a film | section 6 | **confirmed** (a limit, not a bug) | every "flat page exact: yes" below needs the body test beside it |
| `M.spun_check` can say "not spun" for an unstable recipe that is spun | section 2; also `orb_inf_px`: 0.39 % under a half-turn; my re-coding of `orb_inf_px` differs from the frame agent's code on 237 of 60,000 Mandelbrot verdicts and on 0 Julia verdicts | **confirmed** | turned numbers under about 0.5 % for unstable rules are noise. No "not spun" answer of a best rule rests on such a number (they are 0.7 % to 5 %) |
| `M.stay` is right | 0 of 4,000 counts differ from my own loop (no orbit dropped), 10 rules x 3 sets | **HOLDS** | |
| `M.sq_about` is P about the sheet | largest difference from a turn by hand 1.4e-12 | **HOLDS** | |
| `M.solid` agrees with direct verdicts | 0 of 10,800 depth pixels differ, three cases | **HOLDS** | |
| the start convention matters for `first` only | started at 0, `first` differs in 848 of 40,000 and IS the lathe (0 differ); the other six scout rules: 0 | **HOLDS for the scout's seven; too narrow for the round** | also `b_keep` (797 of 40,000: started at 0 it is exactly the one-plane solid, so its "eight-pointed star" exists only with the library's start at c) and `evc005e70k16` (20). `c_wake1`: 0 |

## 5. Things said too strongly, or wrong

1. **sheet, `evc005e70k16`, "beats along: yes".** Not supported. measured: rabbit, 132 of 60,000 verdicts differ
   from the one-plane rule (inside 1,173 against 1,041); seen: its rabbit and Siegel disc cannot be told from the
   one-plane rule's in `cuts-rabbit.png` and `solids-A.png`. So for c off the x-axis it has what the one-plane rule
   already has (smaller bodies round the flat page only). Basilica: four bud directions, `along` eight.
   For c = -1+0.03i and -1+0.1i the middle body is lopsided, half-moon shaped (`cuts-off.png`, seen). Three dials.
   The sheet agent's own text says "I do not call it a success"; the yes/no should read no.
2. **sheet: "less damage at -0.75+0.1i where along shatters".** WRONG as a point against `along`: that c is outside
   the flat Mandelbrot set (measured: the flat orbit of 0 leaves at step 33), so the flat Julia set is dust and
   nothing should have body there. The shell that the one-plane rule and `evc...` show there has no flat counterpart.
3. **sheet claim 10: weighted votes are "the only followers whose rabbit keeps its body (0.0 % lost)".** The 0.0 %
   HOLDS (0 of 1,810). "Only" is WRONG as a statement about the lift test: lag 0.1, 0.25, 0.7, 0.75 also lose 0 to 4
   of 3,580. It holds only as "the only followers in that family whose rabbit keeps SEPARATE bodies" (seen).
4. **sheet: `ease`'s basilica is "clean".** Volume steady (2.61 / 2.61 / 2.61): HOLDS. Clean: not quite. Thin arcs
   round the body in the cut across x = -0.3 (`cuts-basilica.png`) and curved ridges in the sheet agent's own
   close-up (`out/r21/sheet/close-basilica60.png`), both seen.
5. **skeptic, `lag70`, "basilica round buds off the page, not rings: yes".** True only in the narrowest sense: one
   bud above and one below on the upright sheet, 17.4 degrees = 0.19 wide, about as wide as tall (measured). The bud
   itself is a stack of rings and every body is ribbed (`out/r21/skeptic/close-upbud.png`, seen), and the two buds
   at the page are arcs of 41.9 degrees. In the user's sense the answer is no; the skeptic's text says so too.
6. **prover D3: "a count of planes ... is that n and nothing else".** The n is a least repeat (section 3).
7. Small number differences, same finding: alongmem `b_delay`, `c_delay` rabbit volume 0.06, mine 0.01 at 30 steps
   and 0.00 at 80; alongmem "Jacobian of along negative at 39 % of points", mine 44.4 % in the cube -1.5..1.5 (73.7 %
   near the 45-degree sheets, theirs 71 to 75 %; the one-plane rule 0 %); span "16.6 / 13.6 / 13.7 % of the main body
   thrown out by the prev rules", mine 19.6 / 19.1 / 19.1 % at 240 steps with c at any turn (2.5 to 3.9 % at 30).

## 6. The "best" rules: every yes/no, tried again

Definitions: I re-coded each rule from the WORDS of its report and compared with the reporter's code on 60,000
points each for the basilica, the rabbit, c = (-0.6, 0.3, 0.4) and the Mandelbrot solid (`t1_defs.txt`,
`t13_defs2.txt`). **0 verdicts differ** for `evc005e70k16`, `ease`, `vote4`, `c_wake1`, `c_wake2`, `b_keep`,
`first2`, `lag70`, `lag10`, `c_lag10`, `c_lag25`, `area_1_px`, and for the bench `along`, `oneplane`, `lathe`.
`orb_inf_px`: 0 on the three Julia sets, 237 on the Mandelbrot solid (rounding noise, section 4). `c_page` I did
not re-code; I checked it against its two closed descriptions instead (fan: 0 of 20,000 differ in each of six
planes; swept solid: 0 of 40,000). `pt_1_tr` not re-coded.

P(x,y,z) = f (x^2 - y^2, 2xy, 2rz), r = |v|, f = r^2/(r^2 + z^2). "P about theta" = Rot_x(theta) P(Rot_x(-theta) v).
phi = atan2(z, y). c is added after every squaring. The Mandelbrot orbit starts at c with k = 0.

- **`evc005e70k16`** (sheet). Carried w, start (0.05, 0). One eased vote of (y, z) with weight factor k:
  psi_w = atan2(w2, w1); t = atan2(2yz, y^2 - z^2) - psi_w brought into -180..180; a = psi_w + t - 0.7 sin t;
  w += k (y^2 + z^2)(cos a, sin a). Each step: c votes with (cy, cz), k = 16; the point votes with (y, z), k = 1;
  the square is P about theta = 0.5 atan2(w2, w1).
- **`ease`** (sheet). Carried theta, start 0. d = phi - theta into -90..90 (0 on the x-axis); theta += d - sin(2d)/2;
  P about theta.
- **`vote4`** (sheet). Carried w, start (4, 0). w += (y^2 - z^2, 2yz); P about 0.5 atan2(w2, w1).
- **`c_wake1` / `c_wake2`** (alongmem). along(v) = P about psi, psi = phi - sin(4 phi)/4. Squarings number 1 (1 and 2)
  are along(v); every later one is P(v) about the flat page.
- **`b_keep`** (alongmem). At the first squaring theta = phi0 - sin(4 phi0)/4 of the start point (0 if it is on the
  x-axis); every squaring, the first included, is P about that theta.
- **`c_lag10` / `c_lag25`** (span). Carried unit normal n, start (0,0,1). m = unit(v x c) (n if v is parallel to c);
  n = unit((1 - lam) n + lam s m), s = sign(n.m), lam = 0.1 / 0.25; a = unit(e_x - n_x n), b = n x a;
  square = P(v.a, v.b, v.n) put back as X a + Y b + Z n.
- **`c_page`** (span). n = unit(v x c); where undefined the plane through v nearest the flat page; a as above;
  square = 2 (a.v) v - |v|^2 a.
- **`area_1_px`** (frame). Carried frame (e1, e2, e3), start (x, y, z). F = P(v.e1, v.e2, v.e3) put back; v' = F + c.
  w = v x v'; p = w.e3; wp = w - p e3; q = |wp|; m = wp/q; tau = 0.5 atan2(2pq, 1 + p^2 - q^2);
  e3 = cos tau e3 + sin tau m; e1 = unit(e_x - (e_x.e3) e3); e2 = e3 x e1.
- **`orb_inf_px`** (frame). The same with w = unit(v) x unit(v') and tau = 0.5 atan2(2pq, p^2 - q^2).
- **`pt_1_tr`** (frame): as written in the frame report; run from the frame agent's code only.
- **`first2`** (prover). Squarings 1 and 2: P about the flat page; later: the lathe (x^2 - y^2 - z^2, 2xy, 2xz).
- **`lag70` / `lag10`** (skeptic) = `M.lag(0.7)` / `M.lag(0.1)`: theta moves the share toward phi (blend of the
  doubled-angle vectors), then P about theta.

Numbers (all measured by me): flat check = `M.flat_check`, 40,000 points, four sets; body = well-inside flat points
lost when lifted 1e-6, 300 steps, Mandelbrot / rabbit / Siegel; turned = `M.spun_check` Mandelbrot; buds = arcs
met on the basilica circle x = 0, radius 0.62 (a round bud is about 14 to 18 degrees), 80 steps; volumes in percent
of the box -1.8..1.8 x -1.3..1.3 x -1.3..1.3 at 30 / 80 / 200 steps.

| rule | flat check | body lost | turned | basilica buds | rabbit volume | my reading of the yes/no |
|---|---|---|---|---|---|---|
| one-plane (yardstick) | 0 | 0 / 0 / 0 | 1.23 % | 2 x 14.1 | 1.87 / 1.81 / 1.81 | |
| `along` (yardstick) | 0 (strays 2e-14) | 0 / 0 / 1 | 1.52 % | 8 x 12.6 | 6.69 / 6.60 / 6.60 | |
| `evc005e70k16` | 0 | 0 / 0 / 1 (of 5,944 / 3,580 / 4,668, as in every row) | 1.20 % | 4: 18.6, 14.6, 18.6, 14.6 | 2.14 / 2.07 / 2.07 | flat yes HOLDS; buds yes HOLDS (two sheets only); rabbit yes HOLDS (it is the one-plane rabbit); dust-free no HOLDS (Siegel 6.58 / 5.88 / 5.63 still falling; lopsided for c just off the axis; on the three sets themselves no dust: 9 / 5 / 1 pieces against 5 / 5 / 1 for one-plane); not spun yes HOLDS; **beats along yes: not supported** |
| `ease` | 0 | 59 / **2,739 of 3,580** / 163 | 0.84 % | 4 x 12.4 | 2.50 / 0.99 / 0.08 | all six HOLD; "flat yes" is hollow for the rabbit (a film); rabbit in 1,283 pieces |
| `vote4` | 0 | 28 / 0 / 0 | 2.17 % | 2 x 15.4 | 3.75 / 2.94 / 2.94 | all HOLD; rabbit separate (seen, `cuts-vote4rabbit.png`), 111 pieces: specks |
| `c_wake1` | 0 | 0 / 0 / 0 | 1.23 % | 8: 12.6 to 14.9 | 2.82 / 2.73 / 2.73 | all HOLD. Two free bodies of 7.2 % each at (0.04, -0.29, +-0.65) (measured). Mandelbrot solid = the one-plane solid: 0 of 300,000 differ |
| `c_wake2` | 0 | 0 / 0 / 0 | 1.25 % | 8: 12.6 to 14.9 | 4.04 / 3.88 / 3.88 | all HOLD; free bodies 0.8 % each; 6 of 300,000 differ from one-plane |
| `b_keep` | 0 | 0 / 0 / 0 (25 / 37 at lift 1e-3) | 1.37 % | 8 x 14.9 | 0.86 / 0.76 / 0.75 | all HOLD; rabbit empty at 33.75 and 90 degrees (seen); Mandelbrot star depends on the start convention |
| `c_lag10` | 0 | 0 / 0 / 0 | 1.50 % | 2 x 15.4 | 2.44 / 2.28 / 2.27 | all HOLD (separate bodies seen in `cuts-otherrabbit.png`) |
| `c_lag25` | 0 | 0 / 0 / 0 | 1.75 % | not walked | 2.60 / 2.18 / 2.13 | all HOLD; at 150 steps the rabbit has holes and specks (seen) |
| `c_page` | 0 | 0 / 0 / 0 | 3.47 % | RING | 4.76 / 3.99 / 3.80 | all HOLD; for c on the x-axis it is the lathe (0 of 60,000 differ) |
| `area_1_px` | 0 | 12 / 0 / 0 | 1.60 % | 2 x 21.6 | 3.18 / 2.78 / 2.78 | all HOLD |
| `orb_inf_px` | 0 | **1,003** / 47 / 0 | 2.19 % | 23.9 at the page and specks | 2.97 / 2.42 / 2.27 | all HOLD; not said in the report: 17 % of its flat Mandelbrot set is a film |
| `pt_1_tr` | 0 | 0 / 0 / 0 | 4.81 % | RING | 3.77 / 3.26 / 3.16 | all HOLD |
| `first2` | 0 | 0 / 0 / 0 | 1.87 % | 2 x 12.4 and four slivers of 0.6 | 4.95 / 4.86 / 4.86 | all HOLD |
| `lag70` | 0 | 102 / 0 / 0 | 0.71 % | 4: 41.9 (page), 17.4 (upright) | 5.67 / 5.56 / 5.56 | see 5.5; the rest HOLD |
| `lag10` | 0 | 377 / 0 / 0 | 2.24 % | 2 x 15.6 | 3.46 / 3.08 / 3.08 | all HOLD |

Mandelbrot solid, circle through the period-3 bud (x = -0.1226, radius 0.7449), 80 steps: one-plane 2 x 2.9
degrees (a lens 0.04 thick, 0.19 tall); lathe RING; `evc005e70k16` 4 x 8.6 (page and upright sheet, nowhere else);
`ease` 164 pieces (dust); `vote4` 2 x 13.6; `c_wake1`, `c_wake2` 2 x 2.9 (the one-plane solid); `b_keep` 8 x 2.9
(eight lenses); `lag70` RING; `c_lag10` 2 x 1.6 and slivers; `c_page` 96 % inside; `area_1_px` 2 x 10.1; `first2`
12.9 at the page and slivers. No rule has a round bud off the flat page there except `evc...`'s lens-shaped one
at the upright sheet (0.11 wide, 0.19 tall).

Seen in my own pictures:
- `cuts-basilica.png`: one-plane 2 buds; `along` 8; `evc...` and `ease` 4 (smooth bodies at 22.5 and 45 degrees,
  the whole flat basilica at 90); `c_wake1` 8 on the middle body only, one bud above and below it in the 45 and 90
  cuts and none on the side bodies; `c_wake2` buds on the side bodies too; `b_keep` 8, flat basilica at 45 and 90;
  `lag70` round buds top and bottom, arcs with slivers left and right, buds in the 22.5 cut as well (ribs).
- `cuts-rabbit.png`: `evc...` = one-plane to the eye in all seven cuts; `along` a lump with shells; `ease` dust;
  `c_wake1` separate bodies with detached blobs above and below; `c_wake2` more of them; `b_keep` empty off the
  page; `lag70` a lump with shells.
- `cuts-off.png`: c = -1+0.03i, -1+0.1i: `evc...` lopsided middle body; `along` keeps its 8 buds; c = -0.75+0.1i:
  nothing in the flat cut for any rule (the c is outside the flat set).
- `cuts-mandel.png`: `evc...` flat set at 0 and 90 degrees, bud-free hearts at 11.25 and 45, a diamond with four
  small buds across; `c_wake1`, `c_wake2` = one-plane; `b_keep` an eight-pointed star; `along` a rough diamond.
- `solids-A.png` (80 steps): `evc...` basilica with buds on two circles, rabbit and Siegel disc as one-plane;
  `along` buds all round, rabbit and Siegel a ribbed lump; `c_wake1` eight buds, a crowded rabbit with free bodies,
  a creased Siegel disc.
- `cuts-lagrabbit.png` (150 steps): only lag 0 has separate round bodies off the page; lag 0.05 to 0.4 fused and
  ragged; 0.8 and 0.95 shells and rings; `first` a lump with shells; `delay` empty.
- `cuts-otherrabbit.png`: `c_lag10` separate bodies with streaks at the necks; `c_lag25` holes and specks;
  `c_page` a fan with streaks; `area_1_px` three bodies joined broadly; `orb_inf_px` shards; `pt_1_tr` rings.

## 7. Every claim, one line each

### sheet (16 claims)
1. First-step law: **HOLDS**, measured to the digit: page 15.62 / 18.88 / 23.62 / 25.62 / 27.38 / 30.88 / 37.38 /
   51.88, upright 2.88 / 6.38 / 12.88 / 27.38, ring at 0.90. (The law itself is close below share 0.5 and 10 % off above.)
2. Following gives ribs and rings: **HOLDS** (measured stretch; seen for lag70).
3. One-plane period-3 bud is a lens of 2.9 degrees: **HOLDS** (2.9).
4. No share gives a round ball on the Mandelbrot solid: **HOLDS** for the shares tried (0.10: 16.6 degrees, 2 arcs;
   0.25: 40.9, 6; 0.40: 26 arcs; 0.45: 250; 0.55, 0.60: single points; 0.67: ring).
5. Why lagging gives blobs: **UNPROVEN** (reasoned; fits the numbers).
6. A round bud off the page for c on the x-axis only at the upright sheet: **HOLDS** (2/3: 12.88 and 37.38; `ease` 4 x 12.4).
7. Flat exact is not the same as having body: **HOLDS** (mine: rabbit lost 100 % `delay`, `mirror`, `over`; 99 %
   lag60; 77 % `ease`; 60 % lag50; Mandelbrot 8.5 % lag25, 36 % `delay`, 56 % `mirror`; basilica 0 everywhere).
8. Turn-away, overshoot, move-after rules have an empty rabbit: **HOLDS** (13 rules 0.00; settle 0.08 / 0.22 / 0.58).
9. Cause and first-order formula: formula **HOLDS** (reasoned; it is the prover's lag formula, which I re-derived);
   the flag percentages not re-run; as a law **UNPROVEN**, as the agent says.
10. Votes: 0 lost **HOLDS**; "only" see 5.3; `vote025` Mandelbrot ring **HOLDS**.
11. Buds only at the flat page and the sheet square to it: **HOLDS** for the rules I walked; the reason given is
    **UNPROVEN** as a general statement (symmetry allows more).
12. Tear argument: **HOLDS** (reasoned again: the number of half-turns of the sheet on a walk round the axis is odd
    far out and 0 near the axis).
13. The sheet must come back to c's sheet: **HOLDS** (volumes as claimed).
14. Eased votes, thickness by the dial: **HOLDS** (3.4 / 8.6 / 15.4 to 17.4 / 35.4 to 39.4 degrees = x0.2 / 0.6 / 1.1 / 2.5).
15. Nothing against Claim S: **HOLDS** (`settle1` 0.000 %).
16. `bisect` fails the flat check: **HOLDS** (12 and 1,125 of 8,000; the other 68: 0).

### alongmem (18 claims)
1. 62 rules exact: **HOLDS** (0 of 20,000, stray 0, all 62). 2. End points: **HOLDS** (0 / 0 / 0 of 60,000 twice).
3. Within 14.3 degrees of the own sheet: **HOLDS** (reasoned again). 4. No carried frame cures the lump: **HOLDS**
(rabbit volume 1.34 to 1.59 for 21 rules of groups A and D, `a_keep` aside at 0.68; pinch ball not re-run). 5. Buds smear: **HOLDS**
(`a_lag25` 8.6 and 16.9, `a_lag50` 0.1 and 25.4, `a_lag75` ring, means 65 % of the circle). 6. Stretch at the pinch
point: **UNPROVEN** (not re-run). 7. The sheet must hold c to a degree: **HOLDS**, if anything too mild (rabbit 1.81 /
1.72 / 0.00 % at 0 / 1 / 2 degrees; at 1 degree the Siegel disc is gone by 200 steps, at 1.5 the rabbit too).
8. No gentle path: **HOLDS** as reasoned for rules that use one sheet per squaring; numbers partly re-run.
9. `c_lag25` rots: **HOLDS** (1.69 / 0.63 / 0.44 / 0.44). 10. Delay rules shatter: **HOLDS** (lift counts are
under-counts, section 4). 11. `c_wake1` = along once, then one-plane: **HOLDS**; tail decides: **HOLDS** (0.64 against
1.39). 12. Each along squaring fattens the rabbit: **HOLDS** to n = 4 (0.441, 0.665, 0.945, 1.151, 1.242; along 1.606).
13. One generation of buds per along squaring: **HOLDS** (seen). 14. Free bodies: **HOLDS** (7.2 % twice); cause
reasoned, **UNPROVEN**. 15. Mandelbrot solid follows the tail: **HOLDS** (0 / 6 / 14 of 300,000). 16. Faster
forgetting, more spun: **HOLDS** (1.52 / 1.31 / 0.84 / 0.39 / 0.00). 17. Made once and kept fails off the axis:
**HOLDS**. 18. No Mandelbrot solid with round buds off the page: **HOLDS** for the ones I walked.

### span (12 claims)
1. **HOLDS** (21 of 21). 2. Identity: **HOLDS** (8e-14). 3. **HOLDS** (0 / 0 / 0; `prev_page` 598 / 1,141 / 9).
4. Fan: **HOLDS** (0 of 20,000 in six planes; gamma from 99.3 to 180 degrees). 5. **HOLDS** (reasoned).
6. Swept solid: **HOLDS** (0 of 40,000). 7. **HOLDS** (0.00 / 3.46 / 1.77 %). 8. **HOLDS** in substance (see 5.7).
9. Tears: the jump of 2 |v|^2 **HOLDS** (reasoned); the other numbers not re-run. 10. Ring mechanism: **HOLDS**
(reasoned). 11. No good middle: **HOLDS** (volumes; seen). 12. `guessP`: not re-checked.

### frame (12 claims)
1. **HOLDS** (reasoned and to 3e-15). 2. **HOLDS** (formula to 2e-15; the four whole-turn rules fail with 1,277 to
3,770; all 36 others 0). 3. **HOLDS** (reasoned). 4. **UNPROVEN** (seen only, as the agent says). 5. **HOLDS**
(volumes 0.00; the growth factor not re-run). 6. **HOLDS** (seen in `out/r21/frame/julia-a.png`). 7. **HOLDS**
(basilica steady, rabbit 81 % kept, shards seen). 8. **HOLDS** (94 % and 87 % kept). 9. One orbit, not re-run.
10. **HOLDS** (0.00 % `pole_05`, then 0.12 % to 4.96 %). 11. **UNPROVEN** (not tested, as the agent says).
12. Not re-run; consistent with the flat checks.

### prover (19 statements)
S1, S2, S3: **HOLD**. S4: **HOLDS** as stated (table not re-run). K1: **HOLDS** (0.182 % and 0.013 %; the 1e-13
column is an under-count). K2: formula **HOLDS** (re-derived; fits not re-run). K3: **HOLDS**. J1: **HOLDS**.
J2 / J3: **HOLD** (0, 0, 0 of 40,000; one-plane against lathe basilica 319). F1: **HOLDS**. F2: **HOLDS** (a
look-up, as said). F3: **HOLDS** (reasoned). F4: lemma **HOLDS**, conclusion **UNPROVEN** in general, measured.
F5: **HOLDS** (re-derived; my own code of the closed form: 0 of 20,000 differ at 0, 11.25, 22.5, 45, 67.5, 90).
Arcs: **HOLD** (`first` 40.9 wide, `first2` 12.9, `delay` a point, `away` 4 x 3.1). D1 / D2: **HOLD**. D3: **HOLDS**
with the correction in 5.6. D4: **UNPROVEN**. D6: open, as said.

### skeptic (19 claims)
1 to 6: **HOLD** (section 2; I used my own recipes and my own decimal code). 7, 8, 9: **HOLD**. 10: **HOLDS**.
11: **HOLDS** for the scout's rules; see section 4. 12: **HOLDS** (depth agreement; the film counts not re-run).
13: **HOLDS**. 14: **HOLDS** (lag55 1.51 -> 0.01 -> 0.00; lag60 2.44 -> 0.08 -> 0.00; lag50 5.85 -> 1.80 at 500;
lag65 5.19 -> 0.12; `delay` 0.00). 15: **HOLDS** (2.9 / 10.9 / 17.4 / 45.9 degrees at 0.55 / 0.65 / 0.7 / 0.8, ring
from 0.9). 16: **HOLDS** (seen). 17: **HOLDS** (seen, `cuts-lagrabbit.png`). 18: **HOLDS** (circle walks, cuts).
19: **HOLDS** (lag50 502 of 6,364; lag05 23 of 2,147).

## 8. What failed, what I did not do

- My first bud-size measure along the radius ran through the pinch points on the line x = 0 and gave 0.666 for
  every rule. Dropped; the flat bud's height 0.19 is taken from the flat picture (y from 0.521 to 0.712, reasoned).
- My nothing-fixed recipes use atan2, which costs them the flat check where they are unstable; explained in section 2.
- Not re-run: alongmem's pinch-point table, pinch-ball numbers, hand-over after 6 / 8 / 12, the gap between the
  free bodies; span's tear table and `guessP`; frame's growth factor, the one-orbit jump, mu = 2 and sticky
  volumes; prover's fitted growth factors, the tau table, the skin measurement, the 1,500- and 3,000-step runs;
  the skeptic's own high-digit runs and film counts of `M.solid`.
- `pt_1_tr` and `c_page` were not re-coded from words.
- No fine render and no close-up beyond 80 to 150 steps on rough blocks.

## 9. Pictures

| file | what it shows |
|---|---|
| `cuts-basilica.png` | 8 rules: cuts across x = 0, -0.3, -1, -1.4 and along 22.5, 45, 90 degrees, 100 steps |
| `cuts-rabbit.png` | the same 8 rules, rabbit: along 0, 11.25, 33.75, 90, across x = 0, -0.6, 0.5 |
| `cuts-off.png` | c = -1+0.03i, -1+0.1i, -0.75+0.1i and c in the 45-degree sheet: flat cut and cut across |
| `cuts-mandel.png` | Mandelbrot solid: along 0, 11.25, 45, 90 and across x = -0.12, -1, -0.55 |
| `solids-A.png` | one-plane, along, `evc005e70k16`, `c_wake1`: basilica (two eyes, close-up), rabbit (two eyes), Siegel, 80 steps |
| `cuts-lagrabbit.png` | the rabbit for lag 0, 0.05, 0.1, 0.25, 0.4, 0.8, 0.95, `first`, `delay`, 150 steps |
| `cuts-otherrabbit.png` | the rabbit for `c_lag10`, `c_lag25`, `c_page`, `area_1_px`, `orb_inf_px`, `pt_1_tr`, `first2` |
| `cuts-vote4rabbit.png` | the rabbit for `vote4`, `evc005e70k16`, `c_wake1` |

Others' pictures I opened: `out/r21/sheet/final-evc005e70k16.png`, `final-along.png`, `close-basilica60.png`;
`out/r21/skeptic/close-upbud.png`; `out/r21/alongmem/views-close-basilica.png`; `out/r21/prover/t6_necklace.png`;
`out/r21/frame/julia-a.png`.

## 10. For the orchestrator

**May be told as established**
1. A plane made by the orbit alone (nothing fixed to start from) gives exactly the flat set spun, rings and all,
   whatever is remembered; and unless the rule tells left from right the orbit never even leaves the sheet of c,
   so no new plane is made. Proved, and measured three times over by three parties.
2. The same for the basilica, San Marco and airplane: with nothing fixed they come out as the lathe's ringed sets.
3. So "following" needs a fixed start, the flat page. About 190 such rules were tried by four searchers; 187 are
   exact on the flat page (I re-ran the check for all of them).
4. None of them passes the user's tests, and the way they fail is measured: following closely stretches every bud
   round the x-axis by 1/(1 - share) until it is a rib and then a ring; lagging leaves a blob without buds and
   fuses the rabbit; one step behind gives dust; on the Mandelbrot solid there is no round ball anywhere between.
5. Round buds off the page that are not rings do occur, for the basilica family only: in four directions (page and
   the sheet square to it) or in eight when `along`'s formula does the first squaring. Both come from a formula
   term that fixes the count (sin 2d, sin 4 phi).
6. The rabbit comes apart into bodies only where the squaring sheet is c's own sheet to within about one degree.
7. A rule can pass the flat check and still have nothing behind the page (a film). That sorts out `delay`, the
   lags near one half, `ease`, the turn-away and overshoot rules, and the literal reading `orb_inf_px`.
8. Closest rules, described honestly: `evc005e70k16` = the one-plane rabbit plus a four-bud basilica, joined by a
   dial, lopsided for c just off the x-axis, three dials; `c_wake1` = one squaring by `along`, then one-plane:
   eight smooth buds in one generation, a rabbit with two free-floating bodies, the one-plane Mandelbrot solid.
9. The library is sound; three limits are known and named (section 4).

**May NOT be told**
1. That a rule was found that beats `along`.
2. That round buds all round with no count of planes are proved impossible for a rule that starts from the flat
   page. That is open: one argument with a gap (prover D4), one result for rules that forget (F4), and no example.
3. That `along` is worse at c = -0.75+0.1i: that c is outside the flat set.
4. That lag 0.7 "has round buds off the page": it has one ringed bud above and below on a ribbed body.
5. That "exact on the flat page" means the flat picture is really there in the solid.
6. That `b_keep`'s star is its Mandelbrot solid without saying it depends on starting the orbit at c.
7. The necklace picture as the result of any rule.
8. That the Mandelbrot solids being "not spun" is a gain: what is off the page is keels, ribs or a blob.
9. Anything about fine detail: every picture of the round is rough blocks or a cut, at 150 steps at most.
