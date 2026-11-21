# Round 20, prover: are W1 to W6 right, and what do they leave out?

Everything here is about Julia sets of "wind, then square", F(v) = P(T(v)), T: (x, rho, a) -> (x, rho, g(a)).
No Mandelbrot solid was drawn or looked at. Nothing registered with the bench (no myrules.py in this folder).
Marks: [M] measured, [S] seen in a picture I looked at, [R] reasoned (pencil).

Files: `lib.py` (rules for testing only), `exact.py` -> `logs/exact.log`, `fins.py` -> `logs/fins-*.log`,
`siegel.py` -> `logs/siegel.log` + `siegel-thickness.png`, `pics.py` -> `fins-unrolled.png`, `two-planes.png`,
`neck-unrolled.png`, `ywind.py` -> `scout-ywind.png`, `logs/extra.log`.

## Short answers

| claim | verdict |
|---|---|
| W1 copy planes carry the flat picture, any c in the flat plane | HOLDS, exactly. Amendment: the copy in the plane at 60 degrees is the MIRROR image (it is the flat picture turned 240 degrees, not 60). |
| W2 k must be odd | HOLDS, but the reason given is loose: with even k the cut z = 0 is still right for c on the x-axis; it is wrong for every c off it. The clean statement is a parity rule (below). |
| W3 three-fold symmetry for every c | HOLDS, exactly. More: six-fold for c on the x-axis; also a half turn about the upright axis and mirrors. |
| W4 folds nothing, crushes six directions, buds arrive with stretch 2, only +-x go to +x | HOLDS on all four counts. LEFT OUT: the whole x-axis is a line of cone points; right beside it the stretch is 2 one way and 2 to 10 the other. |
| W5 buds in the planes round at every depth; between the planes thinner without limit | First half FALSE for the sinus profile (1.0, 1.29, 1.32, 1.48 long-to-thin at generations 1 to 4; the one-plane twins are 0.86, 0.99, 0.95). True to about 10 % with an exact band. Second half HOLDS and is PROVED for every member of the kind. |
| W6 a neutral body becomes a sheet; an exact band gives the one-plane thickness | First half HOLDS (thickness = 1 / sqrt(206 x steps), measured to 2 figures). Second half FALSE: a band gives a real body, but a wedge 13 % (band 10) or 27 % (band 20) as thick as the one-plane body, with flat faces meeting on the x-axis. |

## Pencil first (the formulas everything below is tested against)

- On the sphere of directions the one-plane rule is w -> w^2 in the coordinate w = (x + i y) / (r - z). It keeps
  angles; its stretch at latitude L above the flat plane is 2 cos L / (1 + sin^2 L): 2 on the flat circle, 0 at
  straight up and down. [R; M: `exact.py` block 0, my P_2 equals the bench's to 1e-14]
- T keeps x and rho, so on the sphere it stretches by exactly 1 along meridians through the x-axis and by g'(a)
  round the axis. So F stretches a small body at v by 2|v| along the ray, |v| s along the meridian and |v| s g'(a)
  round the axis (s = the one-plane stretch at T(v)). The squeeze round the axis relative to the meridian is
  EXACTLY g'(a), at every point off the x-axis. [R; M: largest relative difference 5e-8 on 600,000 directions]
- g(a) = a + 12 a^3 + ... near the flat plane (sinus, k = 3): the turn off the flat plane is pushed away, weakly.
- Close to the x-axis the rule is (x, rho, a) -> (x^2, 2|x| rho, g(a) or 180 - g(a)) to first order in rho. [R; M:
  at 0.0001 from the axis, turn of the answer = 180 - g(a) to 0.01 degree, distance = 2|x| rho to 6 figures]

## W1: holds [R + M]

A point of the half-plane at j x 60 degrees is (x, rho, j pi / 3). T sends it to turn j pi: the flat plane, half
y > 0 for even j, half y < 0 for odd j. So its first answer is the flat square of x + i rho (j even) or x - i rho
(j odd), and from then on the orbit is a flat orbit. Nothing in this uses the slope of g or which c in the flat plane.
- [M] One step, 200,000 random points per half-plane: |Z| <= 3e-14; error against (x + i rho)^2 is 7e-15 at 0, 120,
  240 degrees and 51 at 60, 180, 300; against (x - i rho)^2 the other way round.
- [M] Whole sets, 60 steps, 160,801 points: the cut at 60 degrees differs from the MIRRORED flat set at 0 points
  (basilica, rabbit, Siegel) and from the plain flat rabbit at 22,976; the cut at 120 degrees differs from the plain
  flat set at 0 points. By escape step (works for the dendrite, which has no inside): 0 points differ for basilica,
  rabbit, Siegel; 1 of 160,801 for the dendrite (a rounding flip on the skin).
- [S] `two-planes.png`, bottom right: the rabbit cut at 60 degrees is the flat rabbit flipped top to bottom.
- Amendment: read as planes, the three copies are the flat picture turned 0, 120 and 240 degrees about the x-axis
  (this is W3). Whoever writes the lab text should say "turned by a third of a turn", not "turned by 60 degrees".

## W2: holds, with a better reason [R + M]

- [M] Even k (2 and 4): on the half y < 0 of the flat plane the answer is conj(z^2), exact to 0; error against z^2
  is 37. The cut z = 0 of the basilica is still the flat basilica (0 of 19,541 points differ), because a set that is
  its own mirror image cannot tell z^2 from its mirror image. The rabbit's cut z = 0 is wrong at 88.9 % of its
  points; the Siegel disc's cut is empty (100 %). [S] `two-planes.png` top middle: a rabbit folded on the x-axis.
- **Parity rule** [R]: exact on the flat plane forces T to be the identity there, so g(0) = 0 and g(180) = 180 (+
  whole turns), at EVERY power. If g only rises (no fold), the half turn above the flat plane is wound an odd
  number of half turns, 2m + 1, and the half-planes strictly above the flat plane that are sent into it number 2m:
  always EVEN. Same below. With "same above and below" the two sides are alike, so the extra half-planes number
  4m in all and k = 2m + 1 is odd. One extra half-plane a side (the upright plane, the paper's two-plane picture)
  is exactly the case that cannot be had.

## Two planes: three ways, all fail [R + M + S]

1. Even winding k = 2: flat cut wrong off the x-axis (above).
2. Lopsided k = 2 (once round above, three half turns below; `g_lop2`): flat plane exact to 5e-15, no fold, but
   the two extra half-planes both lie below (240 and 300 degrees, measured), they are not one plane, and the rule
   is not the same above and below (mirror test off by 49).
3. One fold a side (`g_fold2`): flat exact, mirror kept, the upright plane is sent into the flat plane, but both
   of its halves land on the half y < 0. Its picture is the lower half of the flat set doubled by a mirror: equal
   to the flat set for the basilica (0 points differ), not for the rabbit (11,505 points differ from the flat
   rabbit, 43 from the doubled lower half). [S] `two-planes.png` bottom middle. And matter either side of the
   crease at 135 degrees is a mirror copy (same answers at 100/170, 120/150, 134/136 degrees): this is the closed
   kind "fold before squaring".
   General [R]: with the mirror above/below, g(-a) = -g(a). For the upright plane to carry BOTH halves of the flat
   picture one needs g(-90) = g(90) + 180, i.e. g(90) = 90 or 270: then it is not sent into the flat plane at all.
   So no rule of this kind, folded or not, puts a whole flat picture in the upright plane.

## What C1 forbids, and why this rule is not forbidden [R]

C1 as proved in round 17: if a second plane (or a smooth curved sheet) is KEPT by v -> F(v) + c, i.e. mapped
into itself, then the line where it crosses the flat plane is kept by z^2 + c, and that forces c onto the x-axis.
The hypothesis is "kept". Here the planes at 60 and 120 degrees are not kept: one step sends them into the flat
plane (|Z| <= 3e-14 measured) and they never come back. They are to the flat plane what the negative real axis is
to the positive one under z^2: a second way in, not a second home. The crossing line (the x-axis) is sent into
the flat plane like every other line of the copy plane, so no condition on c arises.
The price C1 does not name: a plane that is not kept has no arithmetic of its own to keep ITS neighbourhood round
after the first step. Everything that is not in one of the three planes is carried by the winding alone, and that
is where the fins come from (W5). For c on the x-axis there is still a kept second plane, the upright one (and
the planes at 30 and 150 degrees are sent into it); it carries no flat picture, only smooth lens bodies.

## W3: holds [R + M]

g(a + 120) = g(a) + 360, so T, and with it F, does not see a turn of 120 degrees about the x-axis: measured 5.5e-14.
Also measured, all to 6e-14: F(turn 60) = half turn of F (so for c ON the x-axis the set has a SIX-fold turn);
F commutes with the mirrors z -> -z and y -> -y; F(half turn about the upright axis) = F (the flat set's own
half turn survives); F(-v) = mirror of F(v). Control: F(turn 60) - F = 50.
One sentence on the other solid: it keeps the two mirrors only, not the three-fold turn (reasoned from these; not drawn).

## W4: holds; one thing left out [R + M]

- Folds nothing: 0.0000 % of 600,000 directions land mirror-reversed; smallest area factor 1.6e-5.
- Covers the sphere 5.994 times (6 = 2 x 3); the one-plane rule 1.998.
- Crushed: area factor < 0.02 only within 0.7 degrees of the half-way turns and within 3.6 degrees of the plane
  x = 0; those six directions are sent to (0, 0, +-1) with both stretches 0.0000.
- Buds: the six directions at right angles to the x-axis in the planes are sent to (-1, 0, 0) with stretches
  2.0000 and 2.0000. Of 3,000,000 random directions 365 land within 1 degree of -x, all within 0.5 degree of
  those six, 55 to 68 each.
- Arms: 100 land within 1 degree of +x: 46 by +x, 54 by -x, 0 elsewhere.
- LEFT OUT: the x-axis. T is not smooth on it (a cone point at every point of the axis). Half a degree from the
  +x direction the stretches are 2.00 x 2.00 in a copy plane, 2 x 4 at 10 degrees, 2 x 8 at 20, 2 x 10 half way.
  Every body strung on the x-axis is wound through this, and the necks sit on it. See W5.

## W5 [R + M + S]

Method (`fins.py`): the body on the x-axis left of the body round -1 has its middle at x = -1.39. Every bud that
is a copy of it contains an exact pre-image of that point (2k = 6 per bud, found by formula, error 4e-15).
Generation 1 = the six buds on the middle body at x = 0; generation G has 6^G buds. For each, the width through
that point along the meridian and round the x-axis, walked point by point (80 steps).

| generation | buds | in the planes all the way | long : thin, in the planes (m_w3) | one-plane twins | exact band 10 | between the planes, m_w3: median long : thin (largest), thinner than 5:1, than 20:1 | median thickness |
|---|---|---|---|---|---|---|---|
| 1 | 6 | 6 | 0.98 | 0.86 | 0.86 | none | |
| 2 | 36 | 12 | 1.29 | 0.99 | 1.09 | 5.5 (5.5); 100 %; 0 % | 0.014 |
| 3 | 216 | 24 | 1.32 (1.19 to 1.45) | 0.95 (0.88 to 1.02) | 1.05 (0.97 to 1.13) | 6.9 (28); 75 %; 12 % | 0.0048 |
| 4 | 1296 | 48 | 1.48 (1.31 to 1.76) | not run | 1.12 (0.97 to 1.39) | 14.6 (126); 75 %; 40 % | 0.0013 |

(Deep buds are tilted, so widths along fixed directions understate how thin they are; a few read below 1.)

- First half, "a bud in a plane is as round as its flat twin at every depth": NOT for the sinus profile. The
  centre is stretched evenly, but g' = 1 only ON the plane; across a bud 5 degrees wide (seen from the axis) g'
  reaches 1.27, and the squeeze adds up over the ancestors: 23 % narrower than the one-plane twin at generation
  2, 28 % at 3. With g(a) = a exactly in a band (10 degrees) the buds are within about 10 % of the one-plane
  twins at all four generations. [S] `fins-unrolled.png`, top row: ovals on the green lines for m_w3, rounder for the band.
- Only 6 x 2^(G-1) of the 6^G buds lie in the planes all the way: 100 %, 33 %, 11 %, 3.7 %. The rest are fins.
- Second half, between the planes: generation 2 are 24 fins at x = +-1.041, 0.308 from the axis, turned 23.6 and
  36.4 degrees (pencil: 23.6 and 36.4), 0.076 long, 0.065 tall, 0.014 thick: 5.5 to 1 (pencil: g' = 4.57 times the
  1.2 above). [S] `fins-unrolled.png` top left: two upright slivers exactly under the red ticks, between two ovals
  on the green lines. Even winding (m_w3lin): every bud a sliver, 2.6 to 1 at generation 1, 9 to 1 at 2, 24 to 1
  at 3, 37 to 1 at 4 (measured). Band 10: fins 5.6 to 1 at generation 2, 17 to 1 at 4: no better than sinus.
- [S] `fins-unrolled.png` bottom row (x = -0.30): the skin is smooth within about 8 degrees of each copy plane
  and saw-toothed between, with thin spikes standing off it; two small ovals at about 20 and 40 degrees.
- [S] `neck-unrolled.png` (0.118, 0.048 and 0.018 from the neck at x = -0.618): between two copy planes the skin
  is a dense comb of slivers one picture point wide (0.06 degree) with loose specks above; clean only within
  about 5 degrees of each copy plane and in a notch at 30 degrees. On the green lines: clean small ovals.

**Proof that no member of the kind avoids this** [R]. Take any g that goes k >= 2 times round (rising or not,
smooth or not, any band). Near a neck on the x-axis the rule is (x, rho, a) -> (x^2, 2|x| rho, g(a)): two steps
enlarge everything by the same factor (1.53 at the basilica's neck) and wind the turn k^2 times. So a bud near
the neck has, m double-steps deeper, k^(2m) copies; they all lie at the same distance from the neck and from
the axis, i.e. on ONE circle round the axis, and all have the same length and height. To be round each would
need the same share D of the circle as the original; together they have one circle. So at most 360/D of them
can be round, and the average copy is thinner than round by k^(2m) D / 360: without limit. k = 1 (the one-plane
rule) is the only escape. A staircase g (slope 1 almost everywhere) does not help: of the k pre-images of a turn,
on average one lies on a slope-1 piece. So: fins between the planes cannot be removed in this kind, as W5 says;
what W5 did not say is that they are the large majority at depth and stand as combs at every neck.

## W6 [R + M + S]

At the middle of the Siegel disc a height h off the flat plane is multiplied by exactly 1 to first order (the
flat rule turns without stretching there, and the rule keeps angles on the flat plane). The next term decides:
one-plane h -> h (1 - 2 h^2), pulled in; m_w3 h -> h (1 + 103 h^2), pushed out (12 / y^2 - 2, y = -0.338).

Half-thickness above the middle of the disc (`logs/siegel.log`):

| steps | 30 | 60 | 120 | 240 | 480 | 960 | 1920 | 3840 |
|---|---|---|---|---|---|---|---|---|
| one-plane rule | 0.468 | 0.468 | 0.468 | 0.468 | 0.468 | 0.468 | 0.468 | 0.468 |
| m_w3 | 0.0147 | 0.0097 | 0.0064 | 0.0045 | 0.0031 | 0.0022 | 0.0015 | 0.0011 |
| pencil 1/sqrt(206 N) | 0.0127 | 0.0090 | 0.0064 | 0.0045 | 0.0032 | 0.0022 | 0.0016 | 0.0011 |
| m_w5 | 0.0060 | 0.0040 | 0.0028 | 0.0019 | 0.0013 | 0.0009 | 0.0007 | 0.0005 |
| m_w3lin | below 0.0002 at every count | | | | | | | |
| m_w3f | 0.038 | 0.030 | 0.025 | 0.021 | 0.019 | 0.016 | 0.014 | 0.013 |
| exact band 10 | 0.0615 at every count (pencil |y| tan 10 = 0.0596) | | | | | | | |
| exact band 20 | 0.1258 at every count (pencil 0.1229) | | | | | | | |

- First half holds: m_w3's Siegel disc halves in thickness for every fourfold step count: a sheet. [S]
  `siegel-thickness.png`: three thin lines at 0 and +-60 degrees meeting on the x-axis, 0.022 thick at 60 steps, 0.004 at 480.
- m_w3f (third-order term removed) is a wafer that thins slowly toward about 0.013 (pencil 0.017): 3 % of the one-plane body.
- Second half fails as worded: a band gives a body that does NOT thin with steps, but its thickness is the band's
  wedge, tan(w) times the distance from the x-axis at best (13 % and 27 % of the one-plane body at the middle),
  and less toward the x-axis (band 10: 0.038 and 0.015 at 30 % and 60 % of the way to the point 0). [S] same
  picture, right column: a six-sided wedge body with two flat faces meeting in a point on the x-axis, loose
  ragged specks round its left end.

## The right k for a whole power n [R + M]

1. Exact flat cut + same above and below + no fold: k odd, at every power (parity rule above; measured flat error
   1e-14 to 1e-11 for (n, k) = (2,3), (3,3), (4,5), (5,5), (4,3); 240 and 1200 for (3,2) and (4,4)).
2. The count: round on average needs the sphere covered n^2 times; the rule covers it n k times (measured: 5.99,
   8.99, 19.98, 24.97, 11.98 for the five pairs). So the count asks for k = n.
3. Odd powers: k = n satisfies both. Power 3 with k = 3 covers 9 = 3^2, power 5 with k = 5 covers 25 = 5^2.
4. Even powers: k = n is forbidden. n - 1 under-covers (power 2: it is the one-plane rule itself), n + 1
   over-covers by (n + 1) / n: 6 against 4 at power 2, 20 against 16 at power 4. "k = n if n is odd, n + 1 if even"
   is therefore the smallest allowed count that is never below what the power asks for, and it is the entry's formula.
5. What cannot be had: at power 2 the count the power asks for is k = 2, four buds round the axis, the two-plane
   basilica the user liked. That is exactly the forbidden case. And the count round the x-axis is 2k: 6, 6, 10, 10
   for powers 2, 3, 4, 5: it follows from the power by a formula with no dial, but it steps only every second power.
6. Left out for powers 3 and up [M]: the flat picture of z^n has an n-fold turn about the upright axis. The
   one-plane rule keeps it (2e-15). Wind-then-square keeps it only at power 2 (0.00); at powers 3, 4, 5 the answer
   changes by a median 1.0 to 1.3 on unit vectors. So at power 3 the solid's flat cut has a three-fold turn that the
   solid itself does not have: the x-axis is singled out among three equal axes. The entry's texts should say so.
7. The count does not rescue the fins at odd powers: the proof under W5 holds for every k >= 2 at every power.

## A scout that failed: the same rule wound round the y-axis [M + S]

Thought: the combs need necks ON the winding axis; wind round the bud axis instead. `ywind.py`, ten seconds, not
gated, not registered. Flat cut exact (0 points differ, error 1.6e-14) and the planes through the y-axis at 60
degrees carry the flat basilica and rabbit. But [S] `scout-ywind.png`: the basilica cut across the winding axis is
a six-armed flake with frayed, holed edges; the rabbit there is a twelve-pointed thin star; and the skin near the
x-axis neck is torn into long layered streaks, worse than m_w3's comb. FAILS. The x-axis is the better axis.

## What the claims leave out, in one list

1. The 60-degree copy is mirrored (W1).  2. The x-axis is a line of cone points (W4).  3. Buds in the planes are
ovals, not balls, for the sinus profile, and get slowly thinner with depth (W5).  4. Round buds are 33 %, 11 %,
3.7 % of all buds at generations 2, 3, 4.  5. At every neck the skin between the planes is a comb.  6. The band
cure for the Siegel disc gives a wedge, not the one-plane body.  7. For c on the x-axis the symmetry is six-fold.
8. At powers 3 and up the solid loses the flat picture's own turning symmetry.  9. Even k is not "wrong at z = 0"
for c on the x-axis.

## Not done

- No panel2 or bench run (not my section). The comb at the necks was seen in my own unrolled cuts only; it has not
  been put through panel2's hair number.
- The proof under W5 is written for a neck on the x-axis and uses the first-order form of the rule there; the
  error terms were argued, not bounded line by line. Not reviewed by a mathematician.
- Generation-4 widths for the one-plane rule were not run; deep fins were measured along fixed directions only.
- Power-n statements were tested on F itself (one step), not on Julia sets of powers 3 to 5.
