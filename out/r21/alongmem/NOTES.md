# alongmem: "along" made into a rule with memory (round 21)

Every statement is marked **measured** (a number I computed), **seen** (in a picture I opened) or **reasoned**.

## The answer in short

**No. A carried frame does not cure along's lump.** Letting along's four sheets move with the orbit keeps the
rabbit a lump in every variant tried (19 rules), and the more closely the sheets follow, the more the basilica's
buds turn into fins and then rings. The reason is simple (reasoned, and checked): whatever the frame does, a
point is squared about a sheet that is never more than 14.3 degrees from its own sheet, so the whole group lives
next to the lathe, and the lathe's rabbit is the same lump.

The only thing in the family that makes the rabbit's bodies separate is to stop turning the sheet altogether and
square about the flat page, which holds c (the one-plane rule). The sheet has to hold c to within about one
degree: at 2 degrees off, the one-plane rabbit is empty (measured). So there is no gentle in-between: every rule
that moves gradually between "along" and "one-plane" tears or turns the rabbit to shards and dust (measured for
lag, delay, settle, votes).

The one clean in-between is a hard hand-over: **the first n squarings are plain along, every later one is the
one-plane rule** (`c_wake1`, `c_wake2`, ...). With n = 1 the rabbit has separate smooth bodies and the basilica's
middle body keeps its eight round buds. But it is a trade, not a cure: the buds have no buds of their own off the
flat page (one generation per along squaring), two bodies of the rabbit float free, each further along squaring
fattens the rabbit back toward the lump, and the Mandelbrot solid is simply the one-plane solid (no buds off the
flat page).

## Definitions (everything needed to re-code)

Notation. v = (x, y, z), r = |v|. phi = atan2(z, y) is the point's turn round the x-axis from the flat page.
Rot(a) turns (y, z) by the angle a round the x-axis: (y, z) -> (y cos a - z sin a, y sin a + z cos a).

- **P** (the one-plane square): P(x, y, z) = f (x^2 - y^2, 2 x y, 2 r z), f = r^2 / (r^2 + z^2).
- **P about the sheet at turn psi**: P_psi(v) = Rot(psi) P(Rot(-psi) v).
- **along**: along(v) = P_psi(v) with psi = phi - sin(4 phi) / 4.
- The orbit is v -> square(v) + c; c is added by the library. k counts the squarings an orbit has had (0 for the first).
  For the Mandelbrot solid the orbit starts at c with k = 0.
- **w(v)** = (cos 4 phi, sin 4 phi), computed as (y + i z)^4 divided by its length (no angle is taken).
  **p(v)** = (cos 2 phi, sin 2 phi) = (y + i z)^2 divided by its length (the point's own sheet).
  On the x-axis neither exists: the carried thing is then left as it is.
- **blend(a -> b, lam)** = ((1 - lam) a + lam b) divided by its length; if that length is under 1e-9, a is kept.

All carried things start as the flat page: u = (1, 0) or s = (1, 0).

### Group A: the whole frame of four sheets is carried
State u = (cos 4 theta, sin 4 theta). Rot(theta) along(Rot(-theta) v) works out to the same rule with a shifted wobble:

    A_u(v) = P_psi(v),   psi = phi - (w2 u1 - w1 u2) / 4      [ = phi - |u| sin(4 (phi - theta)) / 4 ]

| name | what happens at each squaring |
|---|---|
| `a_fixed` | u never moves (= along; 0 of 60,000 verdicts differ, measured) |
| `a_lag10`, `a_lag25`, `a_lag50`, `a_lag75` | u <- blend(u -> w(v), lam), lam = 0.10, 0.25, 0.5, 0.75; then v <- A_u(v) + c |
| `a_lag25p` | as a_lag25, but u does not move at k = 0 |
| `a_delay` | v' = A_u(v) + c with the old u; then u <- w(v) |
| `a_first` = `a_wake1`, `a_wake3` | u = (1, 0) for k < 1 (k < 3); after that u = w(v) (a lathe step) |
| `a_own` | u = w(v) at once (= the lathe; 0 of 60,000 differ, measured) |
| `a_votes90`, `a_votes50`, `a_votes100` | a sum U (starts (1, 0), not normalised): U <- d U + w(v), d = 0.9, 0.5, 1; u = U / abs(U) (u = 0 if abs(U) < 1e-9) |
| `a_mean25`, `a_mean50` | u <- (1 - lam) u + lam w(v), NOT normalised (its length is the strength of the wobble), lam = 0.25, 0.5 |
| `a_settle` | u <- blend(u -> w(v), 0.5 / (k + 1)) |
| `a_lagaxis50` | u <- normalised ((1 - l) u + l w(v)), l = 0.5 (y^2 + z^2) / r^2 |
| `a_keep` | u = w(start point), kept for the whole orbit |

### Group B: only the turning sheet is carried
State s = (cos 2 t, sin 2 t), the sheet the point is squared about: v <- P_t(v) + c.
along's sheet for a point is T(v) = (cos 2 psi, sin 2 psi), psi = phi - sin(4 phi) / 4.

| name | what happens |
|---|---|
| `b_lag25`, `b_lag50`, `b_lag75` | s <- blend(s -> T(v), lam), then square about s (lam = 0: one-plane; lam = 1: along; both checked, 0 of 60,000 differ) |
| `b_delay` | square about the old s; then s <- T(v) |
| `b_mean50` | S <- (S + T(v)) / 2 not normalised; square about the sheet at turn min(abs(S), 1) * arg(S) / 2 |
| `b_settle` | s <- blend(s -> T(v), 1 / (k + 1)) |
| `b_keep`, `b_keep2`, `b_keep3` | s = T(v) while k < 1 (2, 3), then kept for the whole orbit |

### Group C: the flat spots follow, the squaring stays about the flat page
State s = (cos 2 theta, sin 2 theta), a carried sheet.

    C_s(v) = P_psi(v),   psi = d - sin(4 d) / 4,   d = phi - theta      (psi is measured from the flat page)

| name | what happens |
|---|---|
| `c_lag10` ... `c_lag75` | s <- blend(s -> p(v), lam), then v <- C_s(v) + c; lam = 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.75 (lam = 0: along; lam = 1: one-plane; both checked) |
| `c_lag25p`, `c_lag45p` | the same, but s does not move at k = 0 |
| `c_delay` | square with the old s; then s <- p(v) |
| `c_settle` | s <- blend(s -> p(v), 0.5 / (k + 1)) |
| `c_lagaxis45` | weight l = 0.45 (y^2 + z^2) / r^2 instead of lam |
| `c_keep` | s = p(start point), kept |
| **`c_wake1`, `c_wake2`**, `c_wake3`, `4`, `6`, `8`, `12` | for k < n: s = flat page (the squaring is plain along). For k >= n: s = p(v) (d = 0, the squaring is P about the flat page = the one-plane rule) |
| `c_alt`, `c_altb`, `c_alt3` | along at even k / at odd k / at every third k; the one-plane rule at the other squarings |

In one line, **`c_wake1`: v1 = along(v0) + c, and from then on v <- P(v) + c.** Its Julia set is exactly the set of v
whose image along(v) + c lies in the one-plane Julia set (0 of 60,000 verdicts differ, measured).

### Group D: the frame follows c's sheet as well
`d_lag2525`, `d_lag5025`: group A with u <- normalised ((1 - lam - mu) u + lam w(v) + mu w(c)), (lam, mu) = (0.25, 0.25), (0.5, 0.25);
for c on the x-axis w(c) is replaced by u. `d_conly50`: lam = 0, mu = 0.5 (the frame follows c's sheet only; for c in
the flat page this is along itself).

## Numbers

Every rule: flat-page check 0 / 0 / 0 / 0 of 20,000 (Mandelbrot, basilica, rabbit, Siegel), stray 0 (measured, `numbers.json`,
`nums-rerun.log`). My first coding of group A took cos and sin of 4 phi and so threw flat points off the page by 2e-14 per
step, which cost 1 to 4 verdicts in the lagging rules and 123 / 503 in `a_delay`; rewritten without any angle function
the flat page is kept to the last bit. That episode is itself a finding: see "thin flat page" below.

How to read the columns. "arcs": on the circle of radius 0.64 round the x-axis at x = 0 (where the flat basilica has its
top bud) the number of separate inside arcs and the share of the circle inside: 8 arcs = eight buds, 1 (100 %) = a ring,
2 = buds only in the flat page. "pinch ball": share of a ball of radius 0.12 round the rabbit's pinch point (-0.276, 0.480, 0)
that is inside, not counting the slab within 0.03 of the page: small = bodies come apart there, large = lump.
"turned": share of test points whose verdict changes when turned round the x-axis (0 = spun).

| rule | turned: M / basilica | basilica vol 30 -> 80 steps | arcs | rabbit vol 30 -> 80 | pinch ball | Siegel vol 30 -> 80 |
|---|---|---|---|---|---|---|
| bench along | 1.6 % / 0.3 % | 0.64 -> 0.63 | 8 (27 %) | 1.58 -> 1.56 | 77 % | 1.61 -> 1.57 |
| bench oneplane | 1.2 % / 0.3 % | 0.70 -> 0.70 | 2 (8 %) | 0.44 -> 0.43 | 38 % | 1.19 -> 1.16 |
| bench lathe | 0 / 0 | 0.77 -> 0.77 | 1 (100 %) | 1.45 -> 1.42 | 72 % | 1.67 -> 1.60 |
| a_lag10 | 1.5 % / 0.3 % | 0.64 -> 0.64 | 8 (28 %) | 1.56 -> 1.53 | 74 % | 1.62 -> 1.58 |
| a_lag25 | 1.1 % / 0.2 % | 0.65 -> 0.65 | 8 (27 %) | 1.55 -> 1.52 | 72 % | 1.66 -> 1.64 |
| a_lag50 | 0.9 % / 0.3 % | 0.67 -> 0.67 | 8 (28 %) | 1.44 -> 1.41 | 71 % | 1.62 -> 1.62 |
| a_lag75 | 0.5 % / 0.1 % | 0.73 -> 0.73 | 1 (100 %) | 1.46 -> 1.43 | 72 % | 1.59 -> 1.55 |
| a_lag25p | 1.2 % / 0.3 % | 0.65 -> 0.65 | 8 (27 %) | 1.55 -> 1.53 | 73 % | 1.65 -> 1.63 |
| a_delay | 0.9 % / 0.2 % | 0.64 -> 0.64 | 8 (27 %) | 1.39 -> 1.34 | 79 % | 1.19 -> 0.61 |
| a_first (= a_wake1) | 0.8 % / 0.2 % | 0.69 -> 0.69 | 8 (27 %) | 1.43 -> 1.40 | 72 % | 1.64 -> 1.57 |
| a_wake3 | 0.9 % / 0.3 % | 0.66 -> 0.65 | 8 (27 %) | 1.47 -> 1.45 | 72 % | 1.63 -> 1.57 |
| a_votes90 | 1.0 % / 0.3 % | 0.67 -> 0.67 | 8 (31 %) | 1.56 -> 1.52 | 73 % | 1.65 -> 1.63 |
| a_votes50 | 0.5 % / 0.2 % | 0.71 -> 0.71 | 8 (63 %) | 1.53 -> 1.50 | 71 % | 1.61 -> 1.57 |
| a_votes100 | 1.1 % / 0.3 % | 0.66 -> 0.66 | 8 (28 %) | 1.55 -> 1.50 | 74 % | 1.65 -> 1.62 |
| a_mean25 | 0.8 % / 0.3 % | 0.68 -> 0.68 | 8 (37 %) | 1.48 -> 1.45 | 72 % | 1.65 -> 1.61 |
| a_mean50 | 0.5 % / 0.2 % | 0.70 -> 0.70 | 8 (63 %) | 1.48 -> 1.45 | 71 % | 1.64 -> 1.60 |
| a_settle | 1.3 % / 0.3 % | 0.64 -> 0.64 | 8 (28 %) | 1.61 -> 1.52 | 76 % | 1.68 -> 1.66 |
| a_lagaxis50 | 1.1 % / 0.3 % | 0.66 -> 0.66 | 8 (28 %) | 1.47 -> 1.44 | 72 % | 1.65 -> 1.61 |
| a_keep | 0 / 0 | 0.77 -> 0.77 | 1 (100 %) | 1.06 -> 0.66 | 99 % | 1.59 -> 1.39 |
| d_lag2525 | 0.8 % / 0.2 % | 0.65 -> 0.65 | 8 (27 %) | 1.50 -> 1.47 | 72 % | 1.62 -> 1.58 |
| d_lag5025 | 0.5 % / 0.3 % | 0.67 -> 0.67 | 8 (28 %) | 1.43 -> 1.41 | 72 % | 1.61 -> 1.56 |
| d_conly50 | 0.9 % / 0.3 % | 0.64 -> 0.63 | 8 (27 %) | 1.58 -> 1.56 | 77 % | 1.61 -> 1.57 |
| b_lag25 | 2.6 % / 0.3 % | 0.68 -> 0.68 | 2 (8 %) | 1.11 -> 0.86 | 72 % | 1.93 -> 1.92 |
| b_lag50 | 1.4 % / 0.2 % | 0.62 -> 0.62 | 6 (7 %) | 0.96 -> 0.11 | 20 % | 1.32 -> 1.32 |
| b_lag75 | 1.4 % / 0.3 % | 0.64 -> 0.63 | 8 (28 %) | 1.57 -> 1.54 | 77 % | 1.54 -> 1.52 |
| b_delay | 0.7 % / 0.2 % | 0.65 -> 0.65 | 2 (7 %) | 0.06 -> 0.05 | 8 % | 0.14 -> 0.13 |
| b_mean50 | 2.3 % / 0.2 % | 0.63 -> 0.63 | 2 (7 %) | 2.06 -> 2.02 | 77 % | 2.18 -> 2.17 |
| b_settle | 0.8 % / 0.2 % | 0.64 -> 0.64 | 8 (28 %) | 0.28 -> 0.18 | 70 % | 0.61 -> 0.59 |
| b_keep | 1.3 % / 0.2 % | 0.65 -> 0.65 | 8 (32 %) | 0.19 -> 0.17 | 61 % | 0.31 -> 0.23 |
| b_keep2 | 1.3 % / 0.2 % | 0.64 -> 0.64 | 8 (28 %) | 0.55 -> 0.48 | 62 % | 0.74 -> 0.57 |
| b_keep3 | 1.3 % / 0.3 % | 0.64 -> 0.64 | 8 (28 %) | 0.62 -> 0.55 | 63 % | 0.61 -> 0.48 |
| c_lag10 | 2.4 % / 0.3 % | 0.63 -> 0.63 | 8 (28 %) | 1.69 -> 1.61 | 89 % | 1.70 -> 1.66 |
| c_lag25 | 1.5 % / 0.3 % | 0.64 -> 0.64 | 8 (29 %) | 1.66 -> 0.64 | 50 % | 1.77 -> 1.74 |
| c_lag35 | 1.4 % / 0.3 % | 0.64 -> 0.64 | 4 (29 %) | 1.23 -> 0.11 | 36 % | 1.79 -> 1.76 |
| c_lag40 | 1.4 % / 0.3 % | 0.64 -> 0.64 | 4 (21 %) | 0.98 -> 0.05 | 28 % | 1.83 -> 1.80 |
| c_lag45 | 1.3 % / 0.3 % | 0.64 -> 0.64 | 4 (14 %) | 0.69 -> 0.05 | 10 % | 1.81 -> 1.77 |
| c_lag50 | 1.2 % / 0.3 % | 0.65 -> 0.65 | 4 (7 %) | 0.19 -> 0.05 | 3 % | 1.73 -> 1.69 |
| c_lag60 | 1.2 % / 0.3 % | 0.69 -> 0.69 | 2 (8 %) | 0.14 -> 0.05 | 2 % | 1.26 -> 1.21 |
| c_lag75 | 1.2 % / 0.3 % | 0.70 -> 0.70 | 2 (8 %) | 0.42 -> 0.40 | 34 % | 1.20 -> 1.16 |
| c_lag25p | 1.6 % / 0.3 % | 0.64 -> 0.64 | 8 (28 %) | 1.73 -> 0.68 | 54 % | 1.81 -> 1.78 |
| c_lag45p | 1.3 % / 0.3 % | 0.64 -> 0.64 | 8 (27 %) | 0.77 -> 0.05 | 12 % | 1.91 -> 1.88 |
| c_delay | 1.3 % / 0.3 % | 0.67 -> 0.67 | 8 (29 %) | 0.06 -> 0.05 | 2 % | 0.15 -> 0.15 |
| c_settle | 2.8 % / 0.2 % | 0.64 -> 0.64 | 4 (7 %) | 1.38 -> 0.99 | 90 % | 1.74 -> 1.71 |
| c_lagaxis45 | 1.6 % / 0.2 % | 0.63 -> 0.63 | 4 (13 %) | 1.21 -> 0.05 | 38 % | 1.74 -> 1.71 |
| c_keep | 3.2 % / 0.4 % | 0.68 -> 0.68 | 2 (7 %) | 0.75 -> 0.74 | 88 % | 0.83 -> 0.81 |
| **c_wake1** | 1.2 % / 0.3 % | 0.68 -> 0.68 | 8 (30 %) | 0.67 -> 0.65 | 41 % | 1.39 -> 1.36 |
| **c_wake2** | 1.2 % / 0.3 % | 0.67 -> 0.67 | 8 (30 %) | 0.95 -> 0.92 | 44 % | 1.52 -> 1.49 |
| c_wake3 | 1.2 % / 0.3 % | 0.66 -> 0.66 | 8 (29 %) | 1.15 -> 1.11 | 47 % | 1.57 -> 1.54 |
| c_wake4 | 1.2 % / 0.3 % | 0.66 -> 0.65 | 8 (28 %) | 1.26 -> 1.21 | 50 % | 1.60 -> 1.58 |
| c_wake6 | 1.3 % / 0.3 % | 0.65 -> 0.65 | 8 (28 %) | 1.40 -> 1.35 | 56 % | 1.62 -> 1.60 |
| c_wake8 | 1.3 % / 0.3 % | 0.64 -> 0.64 | 8 (27 %) | 1.47 -> 1.42 | 60 % | 1.63 -> 1.60 |
| c_wake12 | 1.3 % / 0.3 % | 0.64 -> 0.64 | 8 (27 %) | 1.54 -> 1.49 | 69 % | 1.62 -> 1.58 |
| c_alt | 2.4 % / 0.3 % | 0.65 -> 0.65 | 8 (28 %) | 1.31 -> 1.28 | 79 % | 1.44 -> 1.41 |
| c_altb | 2.4 % / 0.2 % | 0.66 -> 0.66 | 2 (7 %) | 1.15 -> 1.13 | 79 % | 1.35 -> 1.32 |
| c_alt3 | 1.9 % / 0.3 % | 0.66 -> 0.66 | 8 (28 %) | 1.32 -> 1.31 | 83 % | 1.43 -> 1.41 |

Other measurements used below (scripts named in brackets):

- **A sheet that misses c** (`kick.py`). The one-plane rule about a FIXED sheet turned tau away from the flat page:
  rabbit volume 0.427 at 0 degrees, 0.405 at 1 degree, **0.000 at 2 degrees and beyond**; flat-page inside points kept:
  100 %, 67 %, 0 %. Siegel disc: 1.156, 0.882, 0.004 at 0, 1, 2 degrees. Basilica (c on the x-axis, in every sheet):
  0.700 to 0.705 at every turn.
- **Slow leak** (`leak.py`, volume at 30 / 80 / 200 / 500 steps). `c_lag25` rabbit: 1.660, 0.636, 0.448, 0.447, with 448
  pieces at 80 steps. `c_wake1` rabbit: 0.673, 0.652, 0.652, 0.652. `c_wake2` rabbit: 0.951, 0.920, 0.920, 0.920.
  along: 1.585, 1.563, 1.563, 1.563. one-plane: 0.438, 0.427, 0.427, 0.427.
- **Free-floating bodies** (`pieces.py`). `c_wake1` rabbit at 80 steps: 85.5 % in the biggest piece and two pieces of
  7.2 % each, middles at (0.04, -0.30, +-0.64), gap to the rest 0.124 on a 161^3 grid and 0.108 on a 257^3 grid: they
  float free. `c_wake2`: two pieces of 0.8 % at a gap of 0.06. one-plane rabbit: one piece. `c_wake1` basilica,
  San Marco and Siegel disc: one piece (100.0 %).
- **along folds space** (`jac.py`). The Jacobian of along is negative at 39 % of random points (0 % within 10 degrees
  of the flat page and of the upright sheet, 71 to 75 % round the 45-degree sheets). The one-plane rule: never negative.
- **The pinch point** (`checks.py` and a one-off). Stretch straight off the page at the rabbit's pinch point: one-plane
  1.107, along 1.107, lathe -0.553. For along about a frame turned by theta: smallest of the three stretches 1.11 at 0,
  1.00 at 5, 0.71 at 10, 0.28 at 15, 0.30 at 20, 0.79 at 25, 1.15 at 30, 1.11 at 45 degrees.
- **Thin flat page** (`verify.py`). Flat-page inside points lifted off the page by 1e-9 / 1e-4, verdicts lost:
  along rabbit 0 / 13 of 2,789, Siegel 0 / 9 of 3,831. `a_delay`: Siegel 1,205 / 1,619, rabbit 24 / 257.
  `b_lag50`: rabbit 11 / 2,762. `b_delay`: rabbit 1,249 / 2,773. `c_lag40`: rabbit 0 / 1,037. `c_lag45`: 0 / 2,475.
  `c_delay`: 37 / 2,784. `c_lag25`, `c_wake1`, `c_settle`, `c_lag75`: like along (11 to 15).
- **Mandelbrot solids** (`mdiff.py`, 60,000 random c in the box x -2.1..0.7, y and z -1.3..1.3). Share inside:
  along 7.74 %, lathe 7.95 %, one-plane 1.56 %. Group A and D sit with along and the lathe (a_lag25 7.76 %, a_lag75
  7.86 %, d_lag5025 7.92 %), the wake rules with one-plane (c_wake1 1.56 %, c_wake2 1.57 %, c_lag25 1.96 %), b_keep 3.77 %.
  `c_wake1` against the one-plane rule: **5 of 300,000 verdicts differ**; c_wake2: 11; c_wake4: 26.
  a_lag75 against the lathe: 0.47 % differ; a_mean50: 0.63 %; d_lag5025: 0.46 %.

## What each group does

### A: the four sheets follow the orbit. The lump stays; the buds smear into rings.
- Rabbit: volume 1.39 to 1.61 and pinch ball 71 to 79 % for every rule of groups A and D except `a_keep`
  (along 1.58 and 77 %, lathe 1.45 and 72 %, one-plane 0.44 and 38 %). **Measured.** In `cuts-A.png` and `julia-A.png`
  the rabbit and the Siegel disc are the same layered lump in every row. **Seen.**
- Basilica: at 25 % following the buds at 45 degrees thin into spikes and small specks appear near the skin
  (`cuts-A.png`, `angles-best.png` last row); with votes they become needles; at 75 % following, and with the
  running means, the buds join into a ring round the body (arcs 100 %, or 63 % with thin arcs between) and the solid
  is ribbed like the lathe's (`julia-A.png`). **Seen and measured.**
- `a_delay` breaks the flat page from the side: flat-page points lifted by a billionth are thrown out (1,205 of 3,831
  for the Siegel disc), and its Siegel disc leaks from 1.19 to 0.61. **Measured.**
- `a_keep` (the frame turned once to the start point): basilica exactly spun (turned-differ 0), rabbit a fan of wedges
  and dust (`cuts-keep.png`). **Measured and seen.**
- Why (reasoned). In A_u the sheet of squaring is psi = phi - |u| sin(4 (phi - theta)) / 4: at most 0.25 radian =
  14.3 degrees from the point's own sheet, for every frame. Moving the frame moves only where that small wobble sits.
  So group A cannot leave the neighbourhood of the lathe. And at the rabbit's pinch point the fixed frame is the best
  one: with the frame turned between about 5 and 28 degrees the pinch point pulls nearby points in instead of pushing
  them off (smallest stretch below 1, measured), which glues the bodies.
- Mandelbrot solid: goes from along's lumpy rock (a_lag25) to the spun set with ribs (a_lag75, a_votes90, a_mean50,
  d_lag5025: every cut along a sheet is the flat set and the cut across is a disc; `mandel-A.png`, `mandel-BD.png`).
  **Seen.** Reason: the first point of the Mandelbrot orbit is c itself, so the first thing the frame follows is c's
  sheet, which is the user's earlier "plane that c creates" and gives the spun set. In line with Claim S: the only
  thing off the x-axis is where the frame starts, and the faster it is forgotten the more spun the solid
  (turned-differ 1.6 %, 1.1 %, 0.9 %, 0.5 %, 0 for along, a_lag25, a_lag50, a_lag75, a_own). **Measured.**

### D: the frame follows c's sheet as well. Nothing new.
For c in the flat page c's sheet IS the flat page, so the extra pull only holds the frame nearer to along:
`d_conly50` equals along on every Julia verdict tested, `d_lag2525` and `d_lag5025` are lumps (pinch ball 72 %) and
`d_lag5025`'s basilica is ribbed. For the Mandelbrot solid the pull toward c's sheet makes it more spun. **Measured, seen.**

### B: only the turning sheet follows (between the one-plane rule and along).
- 25 %: basilica is the one-plane basilica (2 arcs: buds only in the flat page), rabbit a ragged lump that leaks
  (1.11 -> 0.86). 50 %: tear, rabbit gone (0.96 -> 0.11). 75 %: along again (8 arcs, lump). Delay: rabbit dust (0.06).
  Running mean of the sheets so far (`b_settle`): rabbit in shards. **Measured; seen in `cuts-BCD.png`, `cuts-keep.png`, `julia-BD.png`.**
- `b_keep` (the sheet made by the START point is kept for the whole orbit) is worth a note. For c on the x-axis it is
  the one-plane Julia set re-wrapped round the axis (the point at turn phi is inside when the point at turn
  sin(4 phi) / 4 is inside the one-plane set; 0 of 60,000 verdicts differ, measured): a clean basilica and San Marco
  with eight rows of round buds on every body, at every generation, no specks (`cuts-keep.png`, `views-basilica.png`,
  `julia-BD.png`, seen). But for c off the x-axis the kept sheet misses c, and the one-plane rule dies 2 degrees off
  c's sheet: the rabbit and the Siegel disc shrink to thin plates near the flat page, pinched to nothing along the
  x-axis (rabbit volume 0.19; no inside point at all in the ball round the middle of the main body; `julia-BD.png`
  shows flat plates). Its Mandelbrot solid is an eight-pointed star of fins (`mandel-C.png`, cut across). **Fails.**

### C: the flat spots follow, squaring about the flat page (between along and the one-plane rule).
- Gradual following has no good setting. 10 %: along's lump (pinch ball 89 %). 15 to 25 %: the rabbit looks like a
  lump at 30 steps but is hollowed out from inside as steps are added (1.66 -> 0.64 -> 0.45), left as ragged shards
  (`cuts-deep300.png`, seen). 30 to 60 %: dust (0.05), with a tear at 50 %, and the flat rabbit becomes a film
  (1,037 to 2,739 of 2,789 flat-page inside points are lost when lifted by 1e-4). 75 %: the one-plane rule (basilica
  2 arcs, no off-page buds). `c_delay`, `c_settle`, `c_lagaxis45`, `c_keep`: dust, tears or loss of the buds. **Measured, seen.**
- Why there is no gentle in-between (reasoned, backed by the numbers above). Two things. (1) along's sheet goes
  round with the point (twice round as a sheet when the point goes once round the axis); the one-plane sheet does not
  move at all. No family of sheets that depends continuously on the point can pass from one to the other, so somewhere
  there is a tear; the 50 % blend is where it sits. (2) The rabbit's attracting cycle passes through 0, which lies on
  the x-axis, where a point's sheet has no meaning; a lagging sheet remembers whatever accidental direction it saw
  there, and a one-plane square about a sheet a couple of degrees off c's sheet throws the orbit out (measured: empty
  at 2 degrees).
- **Hard hand-over: `c_wake n`.** The first n squarings are along, the rest one-plane. Each Julia set is a clean
  solid (smooth skin, no specks: `cuts-deep300.png` at 300 steps, `views-close-basilica.png`, `views-close-rabbit.png`;
  volume steady from 80 to 500 steps). **Seen and measured.**
  - Basilica: the middle body has eight round buds (8 arcs, 30 %; each bud a lens of about equal width and height
    in `angles-best.png`; eight separate buds seen down the axis in `views-basilica.png`). With n = 1 the buds are
    smooth with one tip bud; the side bodies have buds only in the flat page. With n = 2 the buds carry a ring of
    smaller buds and the side bodies get their eight. One generation of off-page buds per along squaring. along
    itself has rosettes of buds on buds at every scale, and thin ridges (`views-close-basilica.png`). **Seen.**
  - Rabbit: n = 1 gives separate smooth bodies, also off the flat page (`views-rabbit.png`, `cuts-deep300.png`),
    thin at the pinch like the one-plane rabbit. Two sausage-shaped bodies above and below the page float free
    (7.2 % of the volume each, gap 0.11). n = 2 is crowded but still bodies; by n = 4 it is along's lump again.
    Rabbit volume 0.43, 0.65, 0.92, 1.11, 1.21, 1.35, 1.42, 1.49, 1.56 for n = 0, 1, 2, 3, 4, 6, 8, 12, infinity:
    **every squaring by along fattens the rabbit.** **Measured and seen.**
  - Why bodies can float (reasoned from a measurement): `c_wake1`'s set is the along-preimage of the (one-piece)
    one-plane set, and along folds space (Jacobian negative at 39 % of points); the preimage of one piece under a
    folding map can come apart.
  - Taking turns (`c_alt`, `c_altb`, `c_alt3`) does not help: rabbit volume 1.13 to 1.31, pinch ball 79 to 83 %. **Measured.**
  - Mandelbrot solid of `c_wake1`: the one-plane solid (5 of 300,000 verdicts differ): a smooth cushion, the flat set
    with heart-shaped smooth cuts off the page and no buds there (`mandel-C.png`). **Measured and seen.** Reason: the
    tail of the orbit decides, and the tail is the one-plane rule.

## Pictures (all opened and looked at)

| file | what it shows |
|---|---|
| `cuts-A.png` | cuts at 60 steps, group A with along and one-plane on top: basilica across the axis (8 buds -> spikes -> ring), rabbit level cuts and upright cuts (lump in every A row, separate ovals only for one-plane) |
| `cuts-BCD.png` | the same cuts for B, C, D: `b_lag50`, `c_lag40` dust; `c_lag75` = one-plane; `c_settle` with tear lines; `c_wake1`, `c_wake2` clean with 8 buds and separate rabbit ovals |
| `cuts-deep300.png` | 300 steps: `c_lag15/20/25/30` rabbits rot into shards and dust; `c_wake1` stays clean |
| `cuts-keep.png` | "made once and kept": `b_keep` clean 8-bud basilica but bow-tie rabbit; `b_settle` shards; `c_keep` no buds; `a_keep` spun basilica |
| `angles-best.png` | basilica cut at 11.25, 22.5, 33.75 degrees, across at three places, and close across-cuts of the top bud and the bud at 45 degrees, for along, one-plane, `c_wake1`, `c_wake2`, `b_keep`, `a_lag25` |
| `julia-A.png` | library Julia sheet (300 x 225, 28 steps): along, one-plane, `a_lag25`, `a_lag75`, `a_votes90`, `a_mean50` |
| `julia-BD.png` | library Julia sheet: along, one-plane, `b_lag25`, `b_lag75`, `b_keep`, `d_lag5025` |
| `julia-C.png` | library Julia sheet (full size): along, one-plane, `c_wake1`, `c_wake2`, `c_wake4`, `c_lag25` |
| `mandel-A.png` | library Mandelbrot sheet (cuts at 0, 11.25, 22.5, 45, 90, across, solid): along, one-plane, `a_lag25`, `a_lag75`, `a_votes90`, `a_mean50` |
| `mandel-BD.png` | `b_lag25`, `b_lag75`, `c_lag25` (tear line in the 90-degree cut), `d_lag5025`, `d_conly50` |
| `mandel-C.png` | along, one-plane, `c_wake1`, `c_wake2` (both look like one-plane), `b_keep` (eight-pointed star) |
| `views-rabbit.png` | rabbit at 50 steps from four eye positions: along (lump), one-plane, `c_wake1` (the side view shows the two floating bodies), `c_wake2` |
| `views-basilica.png` | basilica at 50 steps from the front, from above and straight down the x-axis: along, `c_wake1`, `c_wake2`, `b_keep` |
| `views-close-basilica.png` | close-up x3.2 at 70 steps: along (buds on buds, ridges), `c_wake1` (smooth, one generation), `c_wake2` (two) |
| `views-close-rabbit.png` | close-up x2.6 at 70 steps round the pinch: one-plane (bodies meet in a point), `c_wake1` (extra dumbbell body lying across the junction) |

Not every rule has its own Julia and Mandelbrot sheet: 12 rules have a library Julia sheet, 12 a Mandelbrot sheet,
25 are in a cuts sheet, and all 62 (58 plus four end-point checks) have the flat check, the turned check and the
numbers of the table in `numbers.json`.

## What failed, plainly

1. The family's own idea (carry along's four sheets) fails on the rabbit in all 19 variants and damages the basilica.
2. "Only the turning sheet follows" and "the flat spots follow" fail for every gradual way of following.
3. "Made once at the start and kept" (`b_keep`) gives the cleanest eight-bud basilica of the round and no rabbit at all.
4. `c_wake1` and `c_wake2` are a compromise with a dial (n), free-floating bodies, and the one-plane Mandelbrot solid.
5. Nothing in the family has a Mandelbrot solid with round buds off the flat page: the solids are along's rock, the
   spun set with ribs, the one-plane cushion, or a star of fins.

## Files

`myrules.py` (62 rules, `RULES`, `get(name)`), `tools.py` (grid, pieces, arcs, pinch measures), `nums.py` -> `numbers.json`,
`verify.py` (end points, thin flat page), `leak.py`, `pieces.py`, `kick.py`, `jac.py`, `checks.py`, `mdiff.py`,
`sheets.py` (library sheets, my cuts and angles sheets), `views.py` (solids from several eye positions).
Process note: two close-up renders ran longer than the ten-minute limit (about 19 and 10 minutes).
