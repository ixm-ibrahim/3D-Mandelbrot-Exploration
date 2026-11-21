# Round 20, section profiles: the best form of "wind, then square"

Every statement is marked **measured**, **seen** (in a picture I looked at) or **reasoned**.
Nothing here draws, looks at or describes a Mandelbrot solid.

## The short of it

- **No form passes.** Every form of the rule (sinus, exact bands of 5 to 25 degrees, straight ramps, k = 5) fails
  the bench's J8 (ribs) and fails panel2's "clean close up" on the basilica at every tile width: 32 to 35 of 35
  tiles over the line, against 4 of 35 for `along` and 0 of 35 for `twoplane` (**measured**). The rabbit, the
  dendrite and the Siegel disc fail by eye in every form (**seen**).
- **The profile is a one-way trade, not a cure.** Wider exact bands make everything in the flat plane's family
  better (smoother skin near the planes, round buds, a Siegel disc with a body, a thicker rabbit) and make the
  first step off the planes worse (the nudged basilica thins and, from 20 degrees on, drains away). What hurts off
  the planes is the steepness of the ramp, not the band.
- **Recommended form: `w_c15`.** Slope exactly 1 within 15 degrees of each of the six half-planes, constant
  slope 5 in between. Principle (no free size): *the widest exact bands that can be had without the join being
  steeper anywhere than the smooth sinus form is at its steepest (slope 2k - 1 = 5)*. That fixes both the ramp
  (straight) and the band (half of the way to the mid plane, 90/(2k) degrees). It is no worse than the sinus on
  any line I measured and better on most; on the two nudged basilicas it is the best of the family by a factor
  of 1.1 and 1.9. Its price: a crease in the rule 15 degrees either side of every plane (a small corner in the
  outline, **seen**).
- **W6 holds, with a correction.** A band gives the Siegel disc a body, but the body is as thick as the WEDGE
  allows (0.338 x tan(band) at its centre), not as thick as the one-plane rule's (0.47), and its skin is ragged.
- **Ribs (J8) do not go.** They fall steadily with the band (2.10 % of the radius with no band, 0.40 and 0.51 %
  at 25 degrees, line 0.45) because the pleats are pushed into the ramp, where they stay.
- **Fins are not twelve rows of flattened buds; they are a comb.** Between the planes every body carries fins of
  every generation: a few lens-shaped plates (the first generation) and hundreds of films a thousandth of a unit
  thick, all about as long as a bud is big. No profile removes them.

## What I expected before computing, and what happened

| # | expectation (written first) | result |
|---|---|---|
| E1 | all forms pass the rule checks; a band changes nothing on the planes | held (**measured**) |
| E2 | a band gives the Siegel disc a body, but only as thick as the wedge: 0.338 x tan(w) at its centre, because the band is a wedge that pinches to nothing on the x-axis | held: predicted 0.030, 0.060, 0.091, 0.123, 0.158 for 5 to 25 degrees; measured 0.036, 0.070, 0.103, 0.136, 0.166 (smooth ramp), 0.091 (straight ramp, 15 degrees) |
| E3 | the ribs do not go: they are the body's six lobes copied 3, 9, 27 times round the axis; a band only moves them into the ramp; the J8 number may still fall | held (**measured**, **seen** in `zoom-shoulder-refs.png`) |
| E4 | twelve rows of fins on every body, each a bud squeezed by the ramp's slope there (4.6 for the sinus); steeper ramp, thinner fins | WRONG in size: the fins seen are of every generation, median 47 times as long as wide for the sinus; the first generation (plates 3 to 8 to 1) is the visible minority (**measured**) |
| E5 | a wide band is nearly the tear of a nearest-plane rule; harmless for c on the x-axis (the two sides of the ramp are mirror images there), harmful off it | held: nothing breaks on the basilica up to 25 degrees; the nudged basilica drains from 20 degrees (**measured**) |

## The forms (all registered in `out/r20/profiles/myrules.py`)

F(v) = P(T(v)), T: (x, rho, a) -> (x, rho, g(a)), P the one-plane rule. Planes at a = m x 60 degrees; d = angle
to the nearest plane; S = 30 degrees (half a sector); g(a) = m x 180 + sign x h(d):

    h(d) = d                                             for d <= w        (exact band: T is a plain turn)
    smooth ramp:   slope 1 + A sin^2(pi (d - w) / (2 (S - w))),  A = 120 / (30 - w)     (w = 0 is m_w3 exactly)
    straight ramp: slope 1 + A / 2

| name | band w | ramp | steepest slope | move / gap across the mid plane |
|---|---|---|---|---|
| `m_w3lin` (orchestrator's) | none | slope 3 everywhere | 3 | 6.0 |
| `m_w3` (orchestrator's) = `w_s0` | 0 | sinus | 5 | 10.0 |
| `w_b05` | 5 | smooth | 5.8 | 11.6 |
| `w_b10` | 10 | smooth | 7 | 13.9 |
| `w_b15` | 15 | smooth | 9 | 17.9 |
| `w_b20` | 20 | smooth | 13 | 25.8 |
| `w_b25` | 25 | smooth | 25 | 49.1 |
| `w_c10` | 10 | straight | 4 | 8.0 |
| **`w_c15`** | 15 | straight | 5 | 10.0 |
| `m_w5`, `w_5b05` | k = 5 | sinus; band 5 | 9; 12.1 | 17.9; 24.0 |

**Measured** (`check.py rules`, `cliff.py`, logs in `logs/`): length squared to 1.4e-14, flat plane exact to
3e-14, plane at 60 degrees exact to 3e-14 for every k = 3 form (the "copy plane" column of `check.py` reads 33 to
41 for k = 5 only because its planes are at 36 degrees, not 60; at 36 degrees they are exact). No jump: move / gap
steady from gap 1e-3 to 1e-6 for every form (bench J6: largest jump 1.3e-8 to 3.1e-8 over 1e-9). The bud
direction (x = 0 on the plane at 60 degrees) is sent to (-1, 0, 0) with stretch 2.000 along x and 2.000 round
the axis in every sinus and band form (W4); `m_w3lin` gives 2 and 6. Across the mid plane, at a gap of a tenth
of the radius, two points land 0.77 (`m_w3`), 0.81 (`w_c15`), 1.15 (`w_b15`), 1.39 (`w_b20`), 1.65 (`w_b25`)
apart, where 2 is "opposite ends" and the real tear of `twoplane` gives 0.72.

**Measured** (`wedge.py`): the cut by the half-plane at 60 + d degrees equals the cut at 180 + d degrees point
for point (0 points differ, d = 4, 8, 12, 18 degrees, basilica, rabbit, Siegel disc, every form). That is W3's
turn by 120 degrees, exact, and it holds outside the bands too: it is a symmetry of g, not a gift of the band.

## 1. Exact bands

### Does the Siegel disc get a body (W6)?  Yes, a wedge-shaped ragged one.

| form | reach straight up from the disc's centre (300 steps) | volume at 20, 40, 60, 80 steps | stays (80 / 40; panel line 90 %) |
|---|---|---|---|
| one plane | 0.470 | 1.259 1.173 1.166 1.164 | 99 % |
| `m_w3` | 0.004 (0.008 at 80 steps: still thinning) | 0.342 0.213 0.172 0.151 | 71 % FAIL |
| `m_w3f` | 0.021 | 0.651 0.489 0.435 0.406 | 83 % FAIL |
| `w_b05` | 0.036 | 0.589 0.448 0.403 0.379 | 85 % FAIL |
| `w_b10` | 0.070 | 0.848 0.699 0.657 0.638 | 91 % |
| `w_b15` | 0.103 | 1.116 0.983 0.948 0.933 | 95 % |
| **`w_c15`** | 0.091 | 0.719 0.614 0.591 0.582 | 95 % |
| `w_b20` | 0.136 | 1.370 1.261 1.237 1.228 | 97 % |
| `w_b25` | 0.166 | 1.580 1.501 1.485 1.480 | 99 % |

(**measured**, `siegel.py`.) The centre of the disc is 0.338 from the x-axis; 0.338 x tan(15 degrees) = 0.091.
So W6's last sentence needs correcting: the band gives the wedge's thickness, a fifth to a third of the
one-plane rule's, and nothing where the disc crosses the x-axis.

**Seen** (`vol-siegel-above.png`, `vol-siegel-axis.png`, `vol-siegel-above2.png`, cuts in `cuts-w_*.png`): one
plane is a smooth pillow. `m_w3` is a wire skeleton with holes, six threads seen along the axis. With a band it
is a six-armed mass, fatter with every 5 degrees, with a ragged, flapping skin like torn lettuce; cut across the
x-axis it is a six-armed star of leaf-shaped arms with frayed ends and loose specks. No form gives a smooth
body. panel2's hair number on it (**measured**): `m_w3` 30 of 30 wide tiles over the line, `w_b10` 32 of 35,
`w_b20` 34 of 35.

**Reasoned**: the disc turns about a centre that is not on the x-axis, so its points cross the neighbourhood of
the x-axis again and again; there the band is thinner than any height, the point falls into a ramp and is thrown
to another wedge. That re-dealing at every crossing is what frays the skin, and no band under 30 degrees stops it.

### Do the ribs go (J8)?  No. They shrink and move into the ramp.

Bench stage 1, basilica (**measured**; J1 to J7 pass for every band form):

| form | what comes off is round to (3 sizes; line 0.45) | ribs, % of the radius (middle body, one bud, a bud's bud; line 0.45) | pieces with no gap allowed |
|---|---|---|---|
| `m_w3` | 0.68 0.50 0.67 | 0.18 2.10 1.56 | 1160 |
| `w_b05` | 0.75 0.64 0.71 | 0.18 1.87 1.77 | 933 |
| `w_b10` | 0.75 0.62 0.72 | 0.19 1.26 1.43 | 877 |
| `w_b15` | 0.72 0.61 0.75 | 0.15 0.95 0.99 | 813 |
| `w_b20` | 0.71 0.66 0.73 | 0.07 0.65 0.71 | 685 |
| `w_b25` | 0.70 0.63 0.73 | 0.02 0.40 0.51 | - |
| `w_c10` | 0.73 0.69 0.53 | 0.35 2.10 1.85 | 977 |
| **`w_c15`** | 0.76 0.64 0.72 | 0.27 1.24 1.19 | 813 |

J8 fails for all (at 25 degrees by 0.06). **Seen** (`bench-tiles-a.png`, `bench-tiles-b.png`): at the size of
the whole set all forms look alike: a row of bodies with six rows of small round buds and faint ribs running
along the bodies like a pumpkin's. Close up on one bud, `m_w3`'s bud is a lemon ribbed like a walnut; with any
band it is rounder and its ribs fainter. **Measured** (`fins.py`): the bud in the plane at 60 degrees is 0.93
as wide round the axis as along it for `m_w3`, 1.01 to 1.05 for every band form, 0.35 for `m_w3lin` (a plate,
as W5 says).

**Seen** (`zoom-shoulder-refs.png`, the picture to look at: the same 0.44-wide patch of the middle body's skin
between the planes at 0 and 60 degrees): `twoplane` is clean skin with small round buds. `along` is round bumps
of several sizes and two long fins. `m_w3` is pleated all over, like drapery or a scallop shell, with flat
lens-shaped plates stuck in the pleats. `w_b15` has the pleats in the middle third only and fewer plates;
`w_b25` is mostly smooth with round buds and one narrow bundle of pleats and blades half way. In every wind
form a straight seam runs along the body exactly half way between the planes.

**Reasoned**: at x = 0 the cut of this solid is the one-plane solid's cut with its angle replaced by g(a) (the
plane x = 0 is sent into the upright plane, which every form treats alike). So the body's outline round the axis
is one fixed oval read through g: six lobes, then 18, 54, ... on the bodies further down the chain. A band
flattens the lobes' tops; the same total rise is squeezed into the ramp.

### What happens to the fins and to the rabbit's thin arcs as the ramp steepens?

Fins: section 2. Rabbit (**measured**, `pieces.py`, 257 points a side, 40 steps; **seen** `vol-rabbit-above*.png`,
`vol-rabbit-axis*.png`):

| form | volume | thickest place (flat set 0.348) | biggest piece, no gap / one-voxel gap | pieces |
|---|---|---|---|---|
| one plane | 0.438 | 0.351 | 100 / 100 % | 7 |
| `m_w3` | 0.426 | 0.260 | 82.1 / 99.97 % | 5459 |
| `w_b10` | 0.798 | 0.331 | 94.2 / 100 % | 5391 |
| `w_b15` | 0.947 | 0.339 | 98.1 / 100 % | 5411 |
| **`w_c15`** | 0.781 | 0.323 | 95.6 / 100 % | 4531 |
| `w_b20` | 1.044 | 0.340 | 98.3 / 100 % | 5475 |
| `w_b25` | 1.073 | 0.337 | 97.6 / 99.99 % | 7383 |

Seen from above the flat plane the rabbit of every wind form is three copies of the flat rabbit crossing on the
x-axis; seen along the x-axis it is a six-armed star. With `m_w3` the arms are blades and loose lens flakes (the
"thin arcs and specks" of the orchestrator's cuts). With a band the arms fatten into faceted, kite-shaped bodies
carrying small round buds, and thin spokes stand between the arms; at 25 degrees it is a six-lobed bunch. None
of them is "balls meeting at points" as the one-plane rabbit is, and none reads as a rabbit. panel2's hair
number (**measured**): 35 of 35 tiles over the line at every tile width for `m_w3`, `w_b10` and `w_b20`
(median thin 1.1 to 1.5, line 0.10; `along`'s rabbit 0.3).

Dendrite (**measured**; **seen** `vol-dendrite.png`): biggest piece with a one-voxel gap at 8, 10, 12 steps: one
plane 100, 100, 99.3 %; `m_w3` 99.8, 97.6, 79.2; `w_b10` 100, 99.7, 97.0; `w_b15` 100, 99.85, 98.7; `w_c15` 99.99,
99.4, 95.4; `w_b20` 99.99, 99.96, 98.1. With no gap allowed every wind form is in 1,600 to 6,400 pieces (one
plane 3 to 53). By eye: one plane is one thin tree; `m_w3` is three dotted lines; with a band, three trees that
cross on the x-axis, in a cloud of specks.

## 2. The fins between the planes

**Measured** (`fins.py`, basilica, point by point, six cuts across the middle body, 2,880 directions each; a
"thing" is matter standing out of the body's own slow outline by 4 % of the radius or more):

| form | things off the planes at least 0.0032 wide (one pixel when the whole set is 1,000 pixels) | their length / width (median) | thinner films |
|---|---|---|---|
| `m_w3` | 168 | 7.7 | 648 |
| `w_b10` | 96 | 10.3 | 600 |
| `w_b15` | 48 | 9.1 | 468 |
| **`w_c15`** | 120 | 7.2 | 528 |
| `w_b20` | 84 | 8.3 | 216 |
| `w_b25` | 48 | 16.7 | 108 |
| `m_w3lin` | 84 | 7.8 | 312 |

They reach 0.04 to 0.08 out of the body (the bud at 60 degrees has radius 0.066; the body 0.5): as long as a bud
is big, at every generation. Median width of all of them 0.001: films.

- **How big beside the buds?** As long, 1/3 to 1/80 as thick. **Seen** (`cross-m03.png`): beside a ragged,
  bristly skin float a few lens-shaped plates about 3 to 1 (needles at 25 degrees).
- **At which depth do they show?** Not at the size of the whole set (**seen**, bench "front" tiles: no form
  shows them). At the size of one body's skin: pleats and plates (**seen**, `zoom-shoulder*.png`). At the size
  of one bud and below: combs (**seen**, `hair-*-basilica.png`; **measured**, panel2's number by tile width,
  half-planes at 30 and 90 degrees left out because they are the rule's mirror planes and always clean):

| basilica | tile 0.1 wide: tiles over the line, median thin, median film | tile 0.02 wide | tile 0.004 wide |
|---|---|---|---|
| `m_w3` | 35 of 35, 0.27, 1.5 % | 34 of 35, 0.83, 7.4 % | 35 of 35, 1.08, 18.1 % |
| `w_b10` | 32 of 35, 0.31, 1.4 % | 34 of 35, 0.77, 5.8 % | 34 of 35, 1.12, 13.7 % |
| `w_b15` | 32 of 35, 0.23, 1.1 % | 34 of 35, 0.71, 5.2 % | 34 of 35, 1.04, 10.9 % |
| **`w_c15`** | 32 of 35, 0.25, 1.4 % | 34 of 35, 0.67, 4.7 % | 35 of 35, 0.94, 9.8 % |
| `w_b20` | 32 of 35, 0.23, 0.9 % | 34 of 35, 0.45, 2.9 % | 33 of 35, 0.71, 6.4 % |
| `along` | 4 of 35, 0.00, 0.0 % | 6 of 35, 0.04, 0.1 % | 14 of 35, 0.00, 0.0 % |
| `twoplane` | 0 of 35 | 0 of 35 | 0 of 35 |

  (lines: thin 0.10, film 0.5 %.) So on the skin test every wind form is worse than `along` at every scale.
  Other sets, tiles over the line at the three widths (**measured**, `logs/hairw-*.log`): San Marco `m_w3` 35, 35,
  35 of 35, `w_c15` 33, 35, 35, `along` 2, 4, 6; airplane `m_w3` 0, 2, 29, `w_c15` 0, 5, 24, `along` 0, 0, 0;
  rabbit `m_w3`, `w_b10`, `w_c15`, `w_b20` 35, 35, 35 (`along` 35, 34, 34; one plane 0, 0, 0); Siegel disc
  `m_w3` 30, 30, 27 of 30, `w_b10` 32, 19, 24 of 35, `w_c15` 33, 28, 28, `w_b20` 34, 28, 32 (`along` 34, 33, 31).
- **With which profile are they least visible?** The wider the band, the fewer (a third as many films at 20
  degrees as with the sinus), because they are squeezed into a narrower ramp. No profile brings a single
  off-mirror half-plane under the line.

**Reasoned** (why a comb and not twelve rows): the solid is T pulled back over the solid's own picture one step
earlier. Each pull-back makes three copies of every row round the axis; only the copies that land on the six
planes keep their shape, the other two thirds are squeezed by the ramp's slope there. The bodies on the x-axis
feed each other (middle body, side body, middle body ...), so every body carries the rows of all generations:
6 round, then 12 squeezed once, 36 squeezed twice, and so on, all of the same length. This is W5, and it is why
a profile can thin or thicken the comb's teeth but cannot remove the comb.

## 3. k = 5 and the even winding

- `m_w3lin` (**measured**, **seen**): bench J4 and J5 fail; what comes off is round to 0.26; the bud at 60
  degrees is a plate 0.35 as wide as long; the rabbit has nothing off its planes but a speck at the axis; the
  Siegel disc is gone even in the flat plane at 60 steps, because the flat plane itself repels sideways by 3 a
  step and rounding error is enough to lose it. The known bad end, as W5 says.
- `m_w5` (**measured**, **seen** `cuts-m_w5.png`, `bench-tiles-b.png`): ten rows of buds, but J4 fails (only 8 of
  20 off-plane buds round) and J8 fails harder (round to 0.53, 0.25, 0.31): the buds are lemons, the buds on
  them stacks of plates. The rabbit is a ten-pointed spiky star with shards, the Siegel disc a ten-armed thread
  star. Worse than k = 3 on every set looked at. `w_5b05` was cut (`cuts-w_5b05.png`) but not looked at closely.

## 4. No free size

The measurements give no best band width inside the family: every flat-plane line improves up to 25 degrees and
the off-plane lines get worse. What decides the off-plane behaviour is the ramp's steepness (**measured**: the
straight ramp with a 15 degree band, steepest slope 5, keeps the nudged basilica thicker than the smooth ramp
with a 10 degree band, steepest slope 7). So the size can be fixed by a cap on steepness:

> Slope exactly 1 near every plane, and nowhere steeper than the smooth sinus form's steepest point, 2k - 1.
> The widest bands that allows are half of the way to the mid plane (90/(2k) degrees: 15 for k = 3), and the
> ramp between them is then forced to be straight.

This is a convention with a reason, not a derivation from the squaring: I found no argument that singles out
2k - 1 beyond "do not be steeper than the smoothest form already is". I say so plainly.

## 5. The off-plane sets (the gate that decided the recommendation)

The panel's first question, the orbit of 0 for 3,000 steps (**measured**, `orbit0.py`):

| form | bas_yz (-1, 0.05, 0.03) | bas_zy (-1, 0.03, 0.05) | sm_yz | rab_up |
|---|---|---|---|---|
| one plane | stays | leaves at 26 | stays | stays |
| `along` | stays | stays | stays | stays |
| `m_w3` | stays | stays | stays | stays |
| `w_b05` | leaves at 1970 | stays | stays | stays |
| `w_b10` | stays | stays | stays | stays |
| `w_b15` | stays | leaves at 32 | stays | stays |
| `w_b20` | leaves at 57 | leaves at 31 | stays | stays |
| `w_b25` | leaves at 23 | leaves at 31 | stays | stays |
| **`w_c15`** | leaves at 1736 | stays | stays | stays |

The solids themselves (**measured**, `pieces.py`, thickest place at 40 and at 80 steps; the un-nudged basilica
is 0.47 thick and the panel asks for 0.8 of that):

| form | bas_yz | bas_zy | rab_up: thickest; biggest piece no gap / one-voxel gap |
|---|---|---|---|
| one plane | 0.432, 0.432 | (outside) | 0.338; 100 / 100 % |
| `m_w3` | 0.148, 0.108 | 0.160, 0.141 | 0.217; 37 / 39 % |
| `w_b05` | 0.142, 0.113 | - | 0.266; 34 / 98.9 % |
| `w_b10` | 0.154, 0.123 | 0.098, 0.068 | 0.298; 31 / 100 % |
| `w_b15` | 0.089, 0.065 | 0.059, 0.033 (volume 0.414, 0.241: draining) | 0.307; 96 / 100 % |
| **`w_c15`** | 0.165, 0.160 | 0.299, 0.299 | 0.286; 32 / 100 % |
| `w_b20` | 0.030, 0.019 (volume 0.380, 0.164) | - | 0.310; 98 / 100 % |
| `w_b25` | volume 0.089, 0.002: gone | - | - |

San Marco nudged is the same for every form (thickest 0.48, stays). **Seen** (`vol-basyz.png`): the nudged
basilica of `m_w3` and of `w_b15` is a row of crumpled walnuts with two or three buds left; `along`'s keeps its
buds; `w_b25`'s picture is empty. Every wind form fails the panel's "bodies" line on both nudged basilicas
(`w_c15` reaches 0.35 and 0.64 of the un-nudged thickness, the others 0.07 to 0.34).

Does the nudged solid stay for long? Volume at 80, 300 and 1,000 steps (**measured**, `longstay.py`, 97 points
a side):

| form | bas_yz | bas_zy |
|---|---|---|
| **`w_c15`** | 0.563, 0.562, 0.559 | 0.542, 0.542, 0.541 |
| `m_w3` | 0.560, 0.552, 0.528 | 0.553, 0.549, 0.540 |
| `w_b10` | 0.565, 0.560, 0.545 | 0.513, 0.480, 0.387 |
| `w_b15` | 0.553, 0.511, 0.399 | 0.242, 0.129, 0.128 |

So `w_c15` holds its nudged basilicas best of the four (it loses 0.7 % and 0.2 % of the volume between step 80
and step 1,000; the sinus 5.7 % and 2.4 %; the smooth 15 degree band 28 % and 47 %), although its orbit of 0 at
bas_yz leaves at step 1736. For these rules the orbit of 0 is therefore not a safe test of "outside": the
panel will print "outside, not judged" for `w_c15` at bas_yz while its solid there is the most stable of the
family. Worth knowing before trusting that line.

## Recommendation

**`w_c15`**, for the reason in section 4 and the numbers in sections 1 and 5. Against the orchestrator's `m_w3`
it: has the same steepest slope (5) and the same cliff number (10.0); makes the bud at 60 degrees exactly as
round as its flat twin (1.05 against 0.93); cuts the ribs on the buds from 2.10 and 1.56 to 1.24 and 1.19 %;
gives the Siegel disc a body 0.091 thick that stays (95 % against 71 %); makes the rabbit's thickest place 0.323
against 0.260 (flat set 0.348) and its biggest piece 95.6 against 82.1 %; keeps the nudged basilicas 0.165 and
0.299 thick against 0.148 and 0.160. Where it is worse: ribs on the middle body 0.27 against 0.18 % (line 0.45)
and a visible corner in the outline at the band edges (**seen**, `cross-edge.png`); the orbit of 0 at bas_yz
leaves late (step 1736) where `m_w3`'s stays.

Runner-up if a crease is not wanted: `w_b10` (smooth, no worse than `m_w3` anywhere measured except bas_zy,
0.098 against 0.160), but its 10 degrees are not fixed by any principle.

It does not pass, and nothing in this family will by changing g alone: the comb (W5), the three crossing
copies of every set that does not sit on the x-axis, and the re-dealing at the x-axis are properties of
"wind k times", not of the profile.

## The corner can be rounded: `w_c15r` (tried last, **measured**)

The same band and the same ramp slope 5, with the corner rounded over 3 degrees either side of the band edge
(so the exact band is 12 degrees). Rule checks pass; bench J1 to J7 pass, J8 fails (round to 0.75, 0.63, 0.71;
ribs 0.30, 1.50, 1.36 %). Siegel disc 0.078 thick, stays 93 %. Rabbit: thickest 0.321, biggest piece 95.6 %.
Nudged basilicas: thickest 0.228 and 0.235 at 40 steps, 0.218 and 0.204 at 80; volume at 80, 300, 1,000 steps
0.564, 0.563, 0.561 and 0.542, 0.541, 0.540; the orbit of 0 stays at all four nudged sets. So rounding the
corner costs nothing off the planes and a little on the ribs, but it brings in a second size (the 3 degrees)
that no principle fixes. I keep `w_c15` as the form with no free size and name `w_c15r` as the one to switch to
if the crease shows in the lab's renderer. The only picture of `w_c15r` is the bench's own sheet
(`out/r16/bench/sheets/w_c15r.png`, **seen**: like the other band forms, a row of bodies with six rows of buds, the
bud close up roundish with faint ribs).

## Full panel2 runs (panel2's own verdicts, **measured** by `panel2.py run`; tables in `logs/panel2-*-table.txt`)

```
rule       basilica  sanmarco  airplane  cauliflower  rabbit           dendrite   siegel             bas_yz           bas_zy           sm_yz  rab_up
m_w3       F:cle     F:cle     F:cle     F:cle        F:pie,bod,d3,cle F:pie,bod  F:pie,sta,bod,d3,cle F:pie,bod,d3,cle F:pie,bod,d3,cle F:cle  F:pie,bod,d3,cle   (orchestrator's run)
w_b15      F:cle     F:cle     F:cle     F:cle        F:pie,bod,d3,cle F:pie,bod  F:bod,d3,cle       F:bod,d3,cle     outside          F:cle  F:pie,bod,d3,cle
w_c15      F:cle     F:cle     F:cle     F:cle        F:pie,d3,cle     F:pie,bod  F:pie,bod,d3,cle   outside          F:pie,bod,d3,cle F:cle  F:pie,d3,cle
```

`w_b15` against `m_w3`, line by line (**measured**): rabbit "one piece" 98.07 % with no gap (needs 98.5; `m_w3`
82.09); dendrite biggest piece at 6, 8, 10, 12 steps 100, 100, 99.86, 98.94 % (`m_w3` 100, 99.97, 98.24, 83.47;
the flat tree 100 throughout) but "a box twice the size holds 4.1 times the solid" (a sheet; allowed 3.0);
Siegel disc passes "one piece" and "the solid stays" and still fails "bodies" (thickest place 0.34 of the flat
set's), "truly 3D" (roundness 0.11) and "clean" (99 of 120 tiles); bas_yz fails "bodies" at 0.19 of the
un-nudged thickness; rab_up "one piece" 96.15 % with no gap. No set passes.

`w_c15` (the recommended form), line by line (**measured**): the four sets on the x-axis and San Marco nudged
fail "clean close up" only (basilica: 101 of 135 tiles over a line, thin up to 2.20, film up to 27.9 %). Rabbit:
passes "bodies meet at points" (`m_w3` and `w_b15` fail it), fails "one piece" (95.56 % with no gap, needs
98.5), "truly 3D" (what stands off the plane is round to 0.26, needs 0.45) and "clean" (120 of 120 tiles).
Dendrite: biggest piece at 6, 8, 10, 12 steps 100, 99.98, 99.58, 96.73 %; a box twice the size holds 3.9 times
the solid (allowed 3.0). Siegel disc: "the solid stays" passes; "one piece" 98.42 % with no gap (needs 98.5);
"bodies" fails (thickest place 0.27 of the flat set's, volume 0.52 of the yardstick's). bas_yz: printed
"outside" (the orbit of 0 leaves at step 1736) although the solid there is the family's most stable: see
section 5. bas_zy: "bodies" 0.64 of the un-nudged thickness (needs 0.8), "one piece" 77.3 % with no gap. rab_up:
passes "bodies" (0.89), fails "one piece" (31.6 % with no gap, 99.997 % with a one-voxel gap). No set passes.
Failing lines in all: `m_w3` 28 on 11 sets, `w_b15` 21 on 10, `w_c15` 21 on 10.

## Pictures (all in `out/r20/profiles/`; all looked at unless said)

- `sheet-profiles.png`: the seven pictures the summary rests on, stacked, with captions: `twoplane`, `along`,
  `m_w3`, the recommended `w_c15` and the 25 degree band side by side. START HERE.
- `zoom-shoulder-final.png`, `zoom-shoulder-refs.png`, `zoom-shoulder.png`: the middle body's skin between two
  planes, voxels. Said plainly: at this size `w_c15`'s skin is only a little better than the sinus's (pleats over
  the middle two thirds, fewer plates); the 25 degree band is the cleanest of the wind forms and still has a
  bundle of pleats; none is as clean as `twoplane` or as natural as `along`.
- `vol-rabbit-axis-final.png`, `vol-rabbit-above-final.png`, `vol-siegel-above-final.png`, `vol-basyz-final.png`:
  the same views with `w_c15` in them (in the sheet).
- `cuts-<rule>.png`: point-by-point cuts of four sets (looked at: w_b10, w_b15, w_b20, w_b25, w_c15, m_w3lin,
  m_w5; NOT looked at: w_b05, w_c10, m_w3f, w_5b05).
- `bench-tiles-a.png`, `bench-tiles-b.png`: the bench's own tiles side by side.
- `hair-<rule>-basilica.png`: panel2's three worst and three typical skin tiles (looked at: m_w3, w_b20, and
  w_b15 inside the sheet).
- `vol-rabbit*.png`, `vol-siegel*.png`, `vol-dendrite.png`, `vol-basyz.png`: voxel views, 257 a side.
- `cross-edge.png` (the crease), `cross-m03.png` (plates and bristles beside the skin).
- `hair-w_c15-basilica.png`: looked at (combs of fins and film in the three worst tiles; a slightly ragged
  coast with a few needles, small plates and round buds in the typical ones).
- NOT looked at: `vol-dendrite-axis.png`, `hair-w_b10-`, `hair-w_s0-basilica.png`.

## Tools (run from the project root, `PYTHONIOENCODING=utf-8`)

`check.py rules|cuts`, `cliff.py`, `wedge.py`, `cmp.py cross|plane|vol` (same cut or view for several rules),
`tilesheet.py`, `fins.py`, `hair.py`, `hairw.py` (panel2's hair number on kept tiles, read-only on panel2),
`siegel.py`, `pieces.py`, `orbit0.py`, `longstay.py`, `sheet.py`. Numbers: `fins.json`, `hair.json`,
`hairw.json`, `siegel.json`, `pieces.json`; logs in `logs/`.

Written outside this folder, by the bench's and panel2's own tools only: `out/r16/bench/results|tiles|sheets/`
for w_b05, w_b10, w_b15, w_b20, w_b25, w_c10, w_c15, w_c15r, m_w3lin, m_w5; `out/r19/panel2/wide/w_*-*.npz`;
`out/r19/panel2/results/` for w_b15 and w_c15 (full panel2 runs, above); panel2's `wide/scores.json` gained the
scores of these tile sets when those runs scored.

## Not done

- No `w_c20`, no band forms for k = 5 beyond one cut sheet; `w_c15r` has numbers but no pictures.
- The nudged sets were measured with my own counts (thickest place, pieces, volume), not all of panel2's lines,
  except where a full panel2 run is reported below.
- The lab's own renderer was not used (Python only); how a distance estimate copes with a slope-5 crease is
  for the entry section.
