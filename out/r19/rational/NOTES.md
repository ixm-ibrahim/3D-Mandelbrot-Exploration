# Round 19, section "rational" (prefix q_): smooth angle-keeping surplus

Blunt summary: **no rule of this kind gets through. 12 rules written, 10 put through the close cut, 7 through
the bench's stage 1; every one fails by the close cut or by stage 1.** The kind is closed by three counts, each
checked on the rules. Nothing was published; no Mandelbrot solid was drawn. Every statement below is marked
measured / seen in the picture / reasoned.

Picture for the record: `out/r19/rational/sheet.png` (one row per rule: bench views and cuts, and the skin close
up). Logs in `out/r19/rational/logs/`.

## 1. What the kind is, and the predictions written down BEFORE anything was iterated

Coordinate on a hemisphere of directions: `w = (x + i y) / (r + |z|)`; `|w| = 1` is the flat plane, `w = 0` is
straight up. The one-plane rule is `w -> w^2`. An angle-keeping map of the whole sphere that keeps the flat circle
(going round it twice) and is the same above and below is a quotient of two "Blaschke" products; the upper half
then holds m directions sent straight up and n sent straight down with m - n = 2, and the map covers the sphere
m + n = 2 + 2n times.

Predictions (reasoned, from `predict.py`, seconds, no iteration; log `logs/predict.log`):

- P1. **It can cover 4 or 6 times, never 3.** (m - n = 2 makes m + n even.)
- P2. **Covering 4 times is lopsided front to back.** Every flat Julia set is unchanged by a half turn; a rule
  keeps that only if its direction map is a function of w^2, and then it covers 2, 6, 10 ... times, never 4.
- P3. **Covering 4 times is the only count where the stretch can be 2 on average** (the area of the sphere must
  go up 4 times when lengths go up 2 times). One plane covers twice: average too small (lenses). Six times: too
  large (needles). So "round on average" (4) and "not lopsided" (2 or 6) exclude each other for any rule of
  this kind.
- P4. **Not every crushed direction can go to a pole.** A 4-fold map crushes 3 directions per hemisphere and at
  most 2 of them can be sent straight up; a 6-fold map crushes 5 and at most 4 can go to the poles.
- P5. The gentlest member (least disturbance of the flat circle) is the symmetric one,
  `R(w) = (w^n - beta) / (w^d (1 - beta w^n))`, n = d + 2, d = 1 (4 times) or d = 2 (6 times): round 17's pole
  rule made mirror-symmetric. One number beta sets everything. What predict.py gives:

  | rule | extra bud directions (sent to -x) | extra arm directions (sent to +x) | stretch there | crushed directions are sent to | flat circle if left alone |
  |---|---|---|---|---|---|
  | 4-fold, beta = +0.268 | 28 deg from upright, leaning forward | 32 deg from upright, leaning back | 2.48 and 1.43 | 16 deg above the flat plane, towards +x and two more | 0.73 to 4.20 |
  | 4-fold, beta = +0.10 | 11 deg, forward | 11.5 deg, back | 5.25 and 4.85 | 46 deg above the flat plane | 1.45 to 2.67 |
  | 6-fold, beta = -0.1346 | 43 deg from upright in the plane x = 0 (four) | 43 deg from upright in the upright plane y = 0 (four) | **2.00 exactly** (this fixes beta) | 19 deg above the flat plane, towards +x and -x: onto the arms | 1.05 to 3.24 |
  | 6-fold, beta = +0.1346 | 38 deg, in the upright plane y = 0 | 38 deg, in the plane x = 0 | 4.00 | 19 deg above the flat plane, towards +y and -y: harmless for the basilica | 1.06 to 3.23 |
  | 6-fold, beta = +0.03 | 19 deg, in the upright plane y = 0 | 19 deg, in the plane x = 0 | 6.38 | 52 deg above the flat plane, towards +-y | 1.77 to 2.25 |

  The 4-fold bud stretch comes down to 2 only at beta = 0.5; the 6-fold one with beta > 0 never goes below 3.67.
- P6. So: **stretch 2 at the extra buds needs a surplus cone 30 to 43 degrees wide, and then the crushed
  directions land within 16 to 19 degrees of the flat plane.** For the 6-fold rule the sign that gives stretch 2
  sends them onto the +-x arms (predicted: bodies fused there); the other sign sends them to +-y (harmless) but
  has stretch 4 or more (predicted: spindles, not balls). A small surplus keeps the body but gives stretch 5 to
  6 (predicted: needles).
- P7. **The change of angle that would make the flat circle exact is not a smooth function, for any member with
  a real surplus** (reasoned: it could only be smooth if every repeating direction on the flat circle were
  stretched exactly as by doubling; at +x the stretch is 1.05 for the stretch-2 rule against 2). So carrying it
  off the flat circle "smoothly" is not possible at the flat plane itself.

## 2. How the flat plane was made exact

Not by a change of angle (P7; measured below) but by a fade: the rule is R on a cap round the upright axis and
`w^2 * exp(kappa * Log(R / w^2))` outside it, kappa falling smoothly from 1 to 0 at the flat plane (or at the
edge of a band 4 degrees wide, `q_6mb`). No table, no tear, no crease. The ring where kappa changes does not
keep angles. First pacing folded 1.5 to 2.9 % of directions; pacing it in |w|^n removed the fold
(measured, `foldscan.py`, `logs/foldscan.log`: 0.00 % folded, worst 1 % of stretch ratios 2.4 for the 6-fold
rule; with a true band 5.3).

## 3. Seconds: rule checks and screens (measured; `logs/check*.log`, `screen2.log`, `count_dirs.log`)

All q_ band rules: length squared to 1e-14; flat plane exact to 0; both mirrors exact; largest jump divided by
the gap the same at gaps 1e-3, 1e-4, 1e-5, 1e-6 (4.0 to 6.9; 10 for q_4s; one plane 2.0), so no tear and no
cliff. Bench J6 passes on all seven benched. For comparison round 17's p_x_ratc25: 1700 to 2500, p_x_ratc15:
550 to 1300 (that is its fins).

| rule | covers | folded | stretch median / largest | angles kept on | directions to -x / to +x (counted) | half turn about upright keeps the rule |
|---|---|---|---|---|---|---|
| oneplane | 2.00 | 0 % | 1.39 / 2.0 | 100 % | 2 / 2 | yes |
| q_6m | 5.98 | 0 % | 2.50 / 4.0 | 77 % | 6 / 6 | yes |
| q_6mb (true band) | 5.98 | 0 % | 2.44 / 4.3 | 83 % | 6 / 6 | yes |
| q_6p | 6.00 | 0 % | 2.51 / 4.0 | 77 % | 6 / 6 | yes |
| q_6h | 5.98 | 0 % | 2.18 / 4.9 | 87 % | 6 / 6 (the six buds evenly round the x-axis) | yes |
| q_4p, q_4m | 4.00 | 0 % | **1.99** / 5.2 | 78 % | 4 / 4 | **no** (differs by 40) |

P1, P2, P3 confirmed by count: the 4-fold rules have median stretch 2.00 and are lopsided; the 6-fold ones are
symmetric with median 2.5; where the extra directions sit agrees with predict.py to the degree.

P7 measured (`tau_singular.py`, `logs/tau_singular.log`): the slope of the change of angle at +x, taken over
steps of 1/8, 1/64, 1/512, 1/4096, 1/32768 of a turn, is 1, 3.3, 17, 102, 647 for the stretch-2 rule (it
never settles; over the whole circle the slopes at the finest step run from 0.02 to 647). For a small surplus
(beta = 0.03) it is 1, 1.35, 1.95, 2.8, 4.1: still not settling. So round 17's jump failure was not table
accuracy alone and the "crumpled skin line" is built into that way of doing it.

## 4. One minute and two minutes: close cut and bench stage 1 (measured; eye on every picture named)

| rule | what it is | close cut worst | by eye (close cut) | stage 1 | volume | by eye (bench sheet) |
|---|---|---|---|---|---|---|
| oneplane | yardstick | 0.00 | clean | fails J4 only | 0.73 | three round-ish bodies in a row |
| q_6m | 6-fold, stretch exactly 2 at extra buds and arms | 99.8 | skin smooth but standing at height 0.76 instead of 0.39: the cut is inside a lump; a blade-shaped hole | FAILS J2, J3, J4, J8 (cut at the meeting point 91 % full) | 4.59 | ONE ROCK, loaf-shaped, honeycombed skin; cut y = 0 a full barrel; the flat basilica survives only as the cut z = 0 |
| q_6mb | the same with a true one-plane band | 7.6 | (not looked at closely; same skin height by the log) | not run | | |
| q_6h | 6-fold, beta = -0.0666 (six buds evenly round) | 21.4 | slashes, combs, needles | FAILS J2, J3, J4, J8 (85 % full) | 3.27 | a rock |
| q_6m3 | 6-fold, beta = -0.03 | 9.2 | not looked at | not run | | |
| q_6p | 6-fold, same size, other sign (stretch 4) | 6.6 | scalloped skin, loose oval droplets, a few thin prongs | J1 J2 J3 J6 J7 pass; FAILS J4 (50 buds off the plane, 8 round), J5 (1201 pieces), J8 (roundness 0.38, 0.24, 0.16) | 0.52 | faceted middle body like a cut stone, side bodies flattened wedges, four spear-shaped arms on the diagonals of the plane x = 0, loose flakes |
| q_6p6 | 6-fold, beta = +0.0666 (stretch 4.3) | 3.1 | droplets, small blades | FAILS J4 (44 off the plane, 0 round), J5 (1465 pieces), J8 | 0.59 | not looked at |
| q_6p3 | 6-fold, beta = +0.03 (stretch 6.4) | 29.6 | kinked skin line with specks | FAILS J4 (28 off the plane, 4 round), J5 (1385 pieces), J8 (0.40, 0.29, 0.21) | 0.65 | the one-plane basilica, bodies parted, with four long thin "ears" standing 19 degrees from upright and thin spikes all over |
| q_4p | 4-fold, beta = +0.268 | 0.18 | smooth skin at height 0.68, one frayed comb | FAILS J2 (95 % full), J8 | 2.69 | a lopsided thorny rock, pointed forward; cut y = 0 a fish |
| q_4m | 4-fold, beta = -0.268 | 30.1 | not looked at | not run | | |
| q_4s | 4-fold, beta = +0.10 | 0.08 | clean straight skin at height 0.50, one ragged knob | FAILS J2 (89 % full), J8 (0.33, 0.34, 0.35) | 2.19 | still fused and lopsided; a tall thin spike up and down from the back body |

Read against the predictions:

- P6 holds in both directions (measured). The sign with stretch 2 (q_6m) is a rock; the other sign keeps the
  necks (J2: 0.02 % full, a ball of 0.02 parts the bodies) and gives spears. Smaller surplus: spikes (q_6p3).
- Why q_6m is a rock (reasoned, agrees with the cut y = 0, seen): for beta < 0 the map is positive on the whole
  upright circle, so no off-plane direction of the upright plane y = 0 is sent to the back half; everything
  more than 43 degrees from upright is pressed into a wedge 19 degrees thick above +x. After the step back by
  1 a point of that plane cannot get away until its distance passes about 1.6: the whole disc is kept.
- My prediction "4-fold fails J7" was WRONG about the bench: its "front/back" line is the mirror in y, which the
  rule keeps. The lopsidedness is real (measured: the rule changes by 40 under the half turn; seen: wedge
  pointing forward) but the bench has no test for it.
- All three 4-fold members fused the necks, the small one too (not predicted in detail; measured).
- No member has round bodies off the flat plane: best roundness 0.72 at one size on a rock, 0.45 at most on a
  rule that keeps its bodies; the bench wants more than 0.45 at three sizes.

## 5. Rabbit and dendrite (a look only; the rules had already failed, so this is not a gate)

`python out/r18/panel/panel.py run q_6p3 rabbit dendrite` and the same for q_6p (logs `logs/panel-*.log`;
strips of the panel's tiles: `rabbit-oneplane.png`, `rabbit-q_6p3.png`, `rabbit-q_6p.png`,
`dendrite-oneplane.png`, `dendrite-q_6p3.png`, `dendrite-q_6p.png` in this folder; all looked at).

| | one plane | q_6p3 (small surplus) | q_6p (large surplus) |
|---|---|---|---|
| rabbit, volume (measured) | 0.44 | 1.74 | 2.36 |
| rabbit, a ball of 0.1 at the meeting point is ... full (measured) | (flat disc 71 %) | 92 % | 97 % |
| rabbit, how far the solid reaches straight up from the meeting point (measured) | 0.023 | 0.626 | 0.812 |
| rabbit by eye | separate bodies meeting at points | a shaggy lump, like a ball of moss; flat cut exact | a shaggy rock |
| dendrite, volume at 10 steps (measured) | 0.011 | 0.045 | 0.157 |
| dendrite, pieces with no gap allowed (measured) | (one tree) | 2157 | 1815 |
| dendrite by eye | a thin tree in the flat plane | the flat tree with a cloud of loose crumbs above and below | a bush of thin twigs in 3D with crumbs all round, 76 % of it clear of the flat plane |

Verdict (measured and seen): both swell the rabbit into a lump and break the dendrite into crumbs. The kind
needs the x-axis: design target 5 fails even for the member that kept the basilica's three bodies apart.
The dendrite stays thin (thickest place 0.039 against 0.038 for the flat tree at 10 steps): its fault is loose
pieces, not thickness.

## 6. What this closes, and what it leaves

Closed (reasoned, each step checked by a count on the rules): a tear-free, crease-free rule whose surplus keeps
angles cannot meet design targets 2, 3 and 4 together.

1. Round on average needs 4 covers; the half turn every flat set has allows only 2 or 6. (P2, P3.)
2. With 6 covers, stretch 2 at the extra buds exists only for the sign that sends the crushed directions onto
   the arms, and that rule is a rock. The other sign has stretch at least 3.67: spears.
3. A small surplus (to stay near the one-plane rule) forces a large stretch (about 1 / (2 beta) for 4 covers):
   needles. A large one swallows the flat picture.
4. Making the flat circle exact by a change of angle is not smooth for any member.

A by-product worth handing to a prover (reasoned, NOT checked): if a rule is to have stretch 2 everywhere on
average (total cover 4) AND the half turn (signed count 2 or 6), it must cover three times forward and once
mirror-reversed. That is a statement about fold rules: a quarter of what they cover has to be the reversed
sheet, and it has to keep angles.

## 7. Things to know before trusting this

- The fade between cap and flat plane is my choice (radii and pacing). One other choice was tried for the
  stretch-2 rule (a true band, q_6mb): close cut 7.6, skin at the same lump height. No fade was found or
  looked for that keeps angles; none can (an angle-keeping map that agrees with w^2 on a circle is w^2).
- "Why the 4-fold rules fuse even when small" is measured (three members), not explained.
- The rabbit and dendrite were run for two 6-fold members only, and only those two sets.
- For about three minutes (23:19 to 23:22) my rules file built a large angle table at load time, which
  slowed every bench or panel start by the other engineers. It is lazy now (the bench's rule file loads in
  1.1 s, measured). The two change-of-angle rules q_c6 and q_c4 are registered but were only screened
  (covers 5.98 times, no fold, largest stretch 18.9; jump / gap 13 to 30): never iterated.
- Outputs of the official tools went where those tools put them: `out/me/r16/closecut-q_*.png`,
  `out/r16/bench/sheets/q_*.png` and results, `out/r18/panel/{results,tiles,sheets,logs}/q_6p*`.
